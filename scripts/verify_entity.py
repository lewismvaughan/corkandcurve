#!/usr/bin/env python3
"""Per-entity verifier — the same checks `verify_entities.py` does over a
whole city, scoped down to one entity so the research agent can run it
inline after writing each entity. Catches mechanical defects at write
time rather than at end-of-batch QA.

Checks performed:

  1. `verified.source_url` HEAD-resolves.
  2. `verified.open_evidence_url` HEAD-resolves.
  3. `verified.cuisine_evidence_url` HEAD-resolves (if present).
  4. `verified.address_quoted` fuzzy-matches `entity.address` (diacritic-
     stripped, token-set fallback per verify_entities.py).
  5. `verified.checked_on` is within 90 days.
  6. `verified.open_status == "open"`.
  7. For dietary entries: GET cuisine_evidence_url and confirm the page text
     contains the dietary keyword (vegan/vegetarian/halal/kosher/gluten-free).

Usage (in research agent's loop):

    python3 scripts/verify_entity.py <country> <city> <topic> <slug>

Exit 0 if the entity is clean and shippable. Exit 1 with one or more
HARD/WARN lines to stdout if not — agent fixes the JSON, re-runs, repeats
until 0. Tools the QA judgment pass uses (route/curriculum match, festival
month sanity) live in QA, not here, because they require fetching pages
and reading them with LLM judgment.

Designed for fast feedback: typical run is one HTTP HEAD per URL = ~200ms
total per entity. Cheap enough to invoke after every entity write.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# Reuse verify_entities.py's primitives (address matcher, URL HEAD,
# entity-list keys, anti-bot codes) so the per-entity verifier and the
# full-city verifier stay byte-identical in their judgment.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from verify_entities import (  # noqa: E402
    _address_matches, _check_url, ENTITY_LIST_KEYS, ANTI_BOT_CODES, STALE_DAYS,
)
import datetime  # noqa: E402
import urllib.request  # noqa: E402

UA = "TableJourney-Verifier/1.0 (+https://tablejourney.com)"

DIETARY_KEYWORDS = {
    "vegan": ["vegan", "plant-based", "plant based"],
    "vegetarian": ["vegetarian", "veggie"],
    "halal": ["halal"],
    "kosher": ["kosher"],
    "gluten_free": ["gluten-free", "gluten free", "gluten_free"],
    "dairy_free": ["dairy-free", "dairy free"],
    "nut_free": ["nut-free", "nut free"],
}


def _fetch_text(url: str, max_bytes: int = 200_000) -> str | None:
    """Fetch the page body as text, capped. Returns None on any error or
    anti-bot response. Best-effort; we don't try to be a browser."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status >= 400:
                return None
            raw = r.read(max_bytes)
            charset = "utf-8"
            ct = r.headers.get("Content-Type", "")
            if "charset=" in ct:
                charset = ct.split("charset=", 1)[1].split(";")[0].strip() or "utf-8"
            try:
                return raw.decode(charset, errors="ignore")
            except Exception:
                return raw.decode("utf-8", errors="ignore")
    except Exception:
        return None


def _find_entity(country: str, city: str, topic: str, slug: str) -> tuple[Path, dict, dict | None] | None:
    """Locate the entity dict inside its topic JSON. Returns
    (file_path, parent_topic_dict, entity_dict). Entity may live under a
    nested key for the dietary file (vegan/vegetarian/etc) — we walk the
    common list keys to find one with a matching slug."""
    f = SITE_DATA / country / city / "data" / f"{topic}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text(encoding="utf-8"))

    def walk_lists(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, list):
                    for it in v:
                        if isinstance(it, dict) and it.get("slug") == slug:
                            return it
                else:
                    r = walk_lists(v)
                    if r is not None:
                        return r
        return None

    ent = walk_lists(d)
    if ent is None:
        return None
    return f, d, ent


def check(country: str, city: str, topic: str, slug: str) -> list[tuple[str, str]]:
    """Returns a list of (level, message) tuples. level in HARD / WARN.
    Empty list = clean."""
    res: list[tuple[str, str]] = []
    found = _find_entity(country, city, topic, slug)
    if found is None:
        return [("HARD", f"entity not found: {country}/{city}/{topic}.json slug={slug}")]
    _, parent, ent = found

    v = ent.get("verified")
    if not v or not isinstance(v, dict):
        return [("HARD", "missing or invalid 'verified' block")]

    # 1-3: URL HEAD checks.
    for field in ("source_url", "open_evidence_url", "cuisine_evidence_url"):
        url = v.get(field)
        if not url:
            if field in ("source_url", "open_evidence_url"):
                res.append(("HARD", f"verified.{field} missing"))
            continue
        status = _check_url(url)
        if isinstance(status, int) and status < 400:
            continue
        if isinstance(status, int) and status in ANTI_BOT_CODES:
            res.append(("WARN", f"verified.{field}={url} anti-bot ({status}); may be fine"))
            continue
        res.append(("HARD", f"verified.{field}={url} returned {status}"))

    # 4: address fuzzy match.
    addr = ent.get("address") or ent.get("meeting_point") or ""
    quoted = v.get("address_quoted") or ""
    if addr and quoted and not _address_matches(quoted, addr):
        res.append(("HARD", f"verified.address_quoted={quoted!r} does not fuzzy-match entity.address={addr!r}"))

    # 5: stale checked_on.
    co = v.get("checked_on")
    if not co:
        res.append(("HARD", "verified.checked_on missing"))
    else:
        try:
            d = datetime.date.fromisoformat(co)
            age = (datetime.date.today() - d).days
            if age > STALE_DAYS:
                res.append(("WARN", f"verified.checked_on={co} is {age}d old (stale at >{STALE_DAYS}d)"))
        except Exception:
            res.append(("HARD", f"verified.checked_on={co!r} not ISO date"))

    # 6: open_status.
    os_ = v.get("open_status", "")
    if os_ != "open":
        res.append(("HARD", f"verified.open_status={os_!r} (must be 'open' for the entity to render)"))

    # 7: dietary content match. Only applies if this entity lives inside a
    # named dietary sub-category (vegan / vegetarian / halal / kosher /
    # gluten_free / dairy_free / nut_free). Heuristic: find the key in
    # parent that contains this entity, see if it matches a dietary key.
    dietary_key = None
    if topic == "dietary":
        # parent['dietary'] is dict of sub-cat → list
        diet = parent.get("dietary") or {}
        if isinstance(diet, dict):
            for k, lst in diet.items():
                if isinstance(lst, list) and any(isinstance(it, dict) and it.get("slug") == slug for it in lst):
                    dietary_key = k
                    break
    if dietary_key and dietary_key in DIETARY_KEYWORDS:
        cev = v.get("cuisine_evidence_url")
        if cev:
            text = _fetch_text(cev)
            if text is None:
                res.append(("WARN", f"dietary cuisine_evidence_url={cev} could not be fetched for content check"))
            else:
                low = text.lower()
                if not any(kw.lower() in low for kw in DIETARY_KEYWORDS[dietary_key]):
                    res.append(("HARD", f"dietary cuisine_evidence_url={cev} does not contain '{dietary_key}' keyword"))

    return res


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("country")
    p.add_argument("city")
    p.add_argument("topic")
    p.add_argument("slug")
    p.add_argument("--quiet", action="store_true",
                   help="Print only HARD failures; ignore WARNs.")
    args = p.parse_args()

    issues = check(args.country, args.city, args.topic, args.slug)
    hards = [m for lvl, m in issues if lvl == "HARD"]
    warns = [m for lvl, m in issues if lvl == "WARN"]

    label = f"{args.country}/{args.city}/{args.topic}/{args.slug}"
    if hards:
        print(f"[verify_entity] {label}: {len(hards)} HARD, {len(warns)} WARN")
        for m in hards:
            print(f"  HARD: {m}")
        if not args.quiet:
            for m in warns:
                print(f"  WARN: {m}")
        return 1
    if warns and not args.quiet:
        print(f"[verify_entity] {label}: clean (with {len(warns)} WARN)")
        for m in warns:
            print(f"  WARN: {m}")
    else:
        print(f"[verify_entity] {label}: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
