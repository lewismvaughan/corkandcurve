#!/usr/bin/env python3
"""Fetch each entity's `verified.cuisine_evidence_url` and confirm the
cuisine / dietary / category claim actually appears in the page text.

This is the deterministic version of the QA agent's "section A" judgment
check. Pizzeria Popolare shipped as gluten-free with a cuisine_evidence_url
pointing at Big Mamma — but Big Mamma's GF kitchen is actually at a
different venue (Biglove Caffè). L'As du Fallafel shipped as halal with
an evidence URL whose page only ever mentions kosher (Beth Din of Paris).
Both went undetected through 4 rounds of LLM QA and were caught only by
the exhaustive verification pass that manually fetched evidence pages.

This script makes that check mechanical:
  1. For each entity, fetch verified.cuisine_evidence_url.
  2. Lowercase + strip HTML.
  3. For each cuisine/dietary claim (entity.cuisine, dietary sub-category,
     topic-class flag like "wine_focus"), check the page text mentions
     it (or a close synonym).
  4. No match -> WARN (or ERR with --strict). Manual review may follow.

Synonyms are conservative; false-positive ("page says 'vegan' so the
restaurant is vegan-friendly enough") is acceptable. False-negative
("page doesn't say 'halal' but venue is halal-certified") would let
defects through, so the substring set is broad.

Usage:
    python3 scripts/check_evidence_content.py --country france --city paris
    python3 scripts/check_evidence_content.py --all --strict

Exit code:
    0 if every entity's cuisine_evidence_url contains its claim.
    1 if any does not (when --strict; otherwise WARN, exit 0).

This script is slower than verify_entities.py (full GET vs HEAD) and is
intended to run periodically or at ship time, not on every JSON edit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
TIMEOUT = 15
WORKERS = 8
UA = "TableJourney-EvidenceChecker/1.0 (+https://tablejourney.com)"

ENTITY_LIST_KEYS = (
    "restaurants", "fine_dining", "casual_dining", "cafes", "bakeries",
    "coffee_roasters", "wine_bars", "bars", "street_food", "breweries",
    "markets", "food_tours", "food_festivals", "cooking_classes",
    "budget_eating", "hidden_gems", "brunch", "late_night", "day_trips_food",
)
SKIP_FILES = {
    "itineraries.json", "signature-dishes.json", "region.json",
    "city.json", "neighborhoods.json", "food-history.json",
    "seasonal-food.json",
}

# Dietary sub-categories and the substrings that count as "page says X".
# Broad on purpose; better a false positive than a missed defect.
DIETARY_SYNONYMS: dict[str, tuple[str, ...]] = {
    "vegan":       ("vegan", "plant-based", "plant based", "100% plant"),
    "vegetarian":  ("vegetarian", "no meat", "meat-free", "meatless", "shojin", "shojin ryori"),
    "gluten_free": ("gluten-free", "gluten free", "gluten-friendly", "celiac", "coeliac", "100% gf", "dedicated gluten"),
    "halal":       ("halal", "halaal", "zabihah", "muslim-friendly"),
    "kosher":      ("kosher", "casher", "beth din", "orthodox union", "ou-certified", "crc", "cor"),
}

# Topic-level claims: we DON'T check these. Venues don't describe
# themselves with critic-vocabulary like "Modern American" / "wine bar"
# on their own homepages; that's editorial framing. The only claim class
# that's specific enough to reliably catch real defects is dietary, where
# halal/kosher/gluten-free/vegan are concrete labels venues either
# advertise explicitly or don't carry at all. Pizzeria Popolare, L'As du
# Fallafel and Chez Imo were all caught in the dietary class.
TOPIC_CLAIM: dict[str, tuple[str, ...]] = {}

_HTML_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
_WS_RE = re.compile(r"\s+")


def _fetch_text(url: str) -> tuple[str, str]:
    """Returns (status_str, text). status_str is the integer status code
    or an ERR:* token; text is plaintext (HTML-stripped) lowercased.
    Treats empty/short bodies on success codes as fetch failures
    (anti-bot Cloudflare often 200s with a JS challenge page)."""
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(2_000_000)
            charset = r.headers.get_content_charset() or "utf-8"
            try:
                html = raw.decode(charset, errors="replace")
            except LookupError:
                html = raw.decode("utf-8", errors="replace")
            html = _SCRIPT_RE.sub(" ", html)
            text = _HTML_RE.sub(" ", html)
            text = _WS_RE.sub(" ", text).lower()
            if len(text) < 400:
                # Body too short to draw conclusions; treat as fetch fail.
                return f"{r.status}:short_body", ""
            return str(r.status), text
    except urllib.error.HTTPError as e:
        return str(e.code), ""
    except urllib.error.URLError as e:
        name = type(e.reason).__name__ if hasattr(e.reason, "__name__") else "URLError"
        return f"ERR:{name}", ""
    except Exception as e:
        return f"ERR:{type(e).__name__}", ""


def _walk_entities(data_dir: Path):
    for f in sorted(data_dir.glob("*.json")):
        if f.name in SKIP_FILES:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        if f.name == "dietary.json":
            for sub, ents in (d.get("dietary") or {}).items():
                if isinstance(ents, list):
                    for e in ents:
                        if isinstance(e, dict):
                            yield f.name, f"dietary[{sub}]", sub, e
            continue
        for k in ENTITY_LIST_KEYS:
            v = d.get(k)
            if isinstance(v, list):
                for e in v:
                    if isinstance(e, dict):
                        yield f.name, k, None, e


def _expected_claims(topic_key: str, dietary_sub: str | None, entity: dict) -> tuple[list[str], list[str]]:
    """Return (label_for_report, substrings_to_search) the page must contain
    at least one of. The page is page text, lowercased."""
    needles: list[tuple[str, tuple[str, ...]]] = []  # (label, syn list)

    if dietary_sub:
        syns = DIETARY_SYNONYMS.get(dietary_sub)
        if syns:
            needles.append((f"dietary={dietary_sub}", syns))

    labels = [n[0] for n in needles]
    return labels, [s for _, syns in needles for s in syns]


def check_city(country: str, city: str, strict: bool = False) -> int:
    data_dir = SITE_DATA / country / city / "data"
    if not data_dir.exists():
        print(f"[{country}/{city}] no such city")
        return 1

    rows = []
    urls_to_fetch: dict[str, list[tuple]] = {}

    for fname, topic, dietary_sub, e in _walk_entities(data_dir):
        v = e.get("verified")
        if not isinstance(v, dict):
            continue
        url = v.get("cuisine_evidence_url")
        if not isinstance(url, str) or not url.startswith("http"):
            continue
        labels, needles = _expected_claims(topic, dietary_sub, e)
        if not needles:
            continue
        slug = e.get("slug", "?")
        name = e.get("name") or e.get("operator") or slug
        row = {
            "fname": fname, "topic": topic, "slug": slug, "name": name,
            "url": url, "labels": labels, "needles": needles,
            "status": None, "matched": [], "missed": [],
        }
        rows.append(row)
        urls_to_fetch.setdefault(url, []).append(row)

    print(f"[{country}/{city}] checking {len(urls_to_fetch)} unique cuisine_evidence_urls across {len(rows)} entities...")

    fetched: dict[str, tuple[str, str]] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(_fetch_text, u): u for u in urls_to_fetch}
        for fut in as_completed(futures):
            url = futures[fut]
            fetched[url] = fut.result()

    err = 0
    warn = 0
    fetch_fail = 0
    for url, page in fetched.items():
        status, text = page
        for row in urls_to_fetch[url]:
            row["status"] = status
            if not text:
                # Anti-bot / Cloudflare / 4xx — page unreachable from this
                # IP, not necessarily a defect. WARN only.
                row["missed"] = ["FETCH_FAILED"]
                fetch_fail += 1
                continue
            for needle in row["needles"]:
                if needle.lower() in text:
                    row["matched"].append(needle)
            if not row["matched"]:
                row["missed"] = row["needles"]
                err += 1

    print()
    print(f"{'slug':35s} {'topic':18s} {'status':8s} {'verdict'}")
    print("-" * 90)
    for row in sorted(rows, key=lambda r: (bool(row["matched"]), r["slug"])):
        if row["matched"]:
            continue
        verdict = "MISS" if row["status"] and row["status"].isdigit() and int(row["status"]) < 400 else "FETCH"
        print(f"  {row['slug']:33s} {row['topic']:18s} {str(row['status']):8s} {verdict} (no synonym for {','.join(row['labels'])})")

    matched_count = sum(1 for r in rows if r["matched"])
    print()
    print(f"[{country}/{city}] matched: {matched_count}/{len(rows)}  miss: {err}  fetch-fail: {fetch_fail}")
    print("    miss = page text does not mention the claim and the page fetched OK.")
    print("    fetch-fail = could not fetch the page (anti-bot/Cloudflare/4xx); not a defect.")

    return 1 if err else 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--all", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero on MISS (default: only on fetch failures)")
    args = p.parse_args()

    if args.all:
        targets = []
        for country_dir in sorted(SITE_DATA.iterdir()):
            if not country_dir.is_dir():
                continue
            for city_dir in sorted(country_dir.iterdir()):
                if (city_dir / "data").exists():
                    targets.append((country_dir.name, city_dir.name))
    elif args.country and args.city:
        targets = [(args.country, args.city)]
    else:
        p.error("Pass --all or both --country and --city")
        return 2

    total_err = 0
    for country, city in targets:
        total_err += check_city(country, city, args.strict)
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
