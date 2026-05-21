#!/usr/bin/env python3
"""Festival date sanity check (deterministic, no AI).

For each festival in `festivals.json` with `annual: true` + `start_month`,
fetch `verified.source_url` and look for the month name in the page text.
If the page text mentions a DIFFERENT month for this festival's edition,
flag it. Catches the wrong-month defect class that shipped 8+ defects
across 4 prior QA rounds (Taste of Times Square claimed June, actually
September; Taste of Chicago wrong month; Salon du Chocolat October-November
cross-month; etc.).

Method:
  1. Fetch the festival's source_url (or open_evidence_url as fallback).
  2. Lowercase the page text.
  3. Search for the claimed `start_month` (lowercase).
  4. Also count appearances of other full month names.
  5. If start_month is present, PASS. If it's absent AND some other month
     appears with a date-like pattern near it, MISS (likely wrong month).
  6. If neither the claimed month nor any other clear month indicator,
     UNKNOWN (don't flag; the source isn't date-specific).

Usage:
    python3 scripts/check_festival_dates.py --country france --city paris
    python3 scripts/check_festival_dates.py --all
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
WORKERS = 6
UA = "TableJourney-FestivalChecker/1.0 (+https://tablejourney.com)"

MONTHS = (
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
)
MONTHS_FR = (
    "janvier", "février", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "août", "aout", "septembre", "octobre", "novembre", "décembre", "decembre",
)
FR_TO_EN = {
    "janvier": "january", "février": "february", "fevrier": "february",
    "mars": "march", "avril": "april", "mai": "may", "juin": "june",
    "juillet": "july", "août": "august", "aout": "august",
    "septembre": "september", "octobre": "october", "novembre": "november",
    "décembre": "december", "decembre": "december",
}

_HTML_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
_WS_RE = re.compile(r"\s+")


def _fetch(url: str) -> tuple[str, str]:
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
                return f"{r.status}:short_body", ""
            return str(r.status), text
    except urllib.error.HTTPError as e:
        return str(e.code), ""
    except urllib.error.URLError as e:
        return f"ERR:{type(e.reason).__name__ if hasattr(e.reason, '__name__') else 'URLError'}", ""
    except Exception as e:
        return f"ERR:{type(e).__name__}", ""


def _mentioned_months(text: str) -> dict[str, int]:
    """Returns {english_month: count} for any month name (EN or FR) found
    on the page. Counts substring occurrences as a rough signal of
    relevance — a festival landing page typically repeats its month."""
    counts: dict[str, int] = {m: 0 for m in MONTHS}
    for m in MONTHS:
        counts[m] = len(re.findall(rf"\b{m}\b", text))
    for fr in MONTHS_FR:
        if fr in text:
            en = FR_TO_EN[fr]
            counts[en] += len(re.findall(rf"\b{re.escape(fr)}\b", text))
    return counts


def check_city(country: str, city: str) -> int:
    data_dir = SITE_DATA / country / city / "data"
    fp = data_dir / "festivals.json"
    if not fp.exists():
        print(f"[{country}/{city}] no festivals.json")
        return 0
    try:
        d = json.loads(fp.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[{country}/{city}] festivals.json read error: {e}")
        return 1
    festivals = d.get("food_festivals") or []
    rows = []
    urls_to_fetch: dict[str, list] = {}

    for f in festivals:
        if not isinstance(f, dict):
            continue
        if not f.get("annual"):
            continue
        sm = (f.get("start_month") or "").strip().lower()
        if sm not in MONTHS:
            continue
        em = (f.get("end_month") or sm).strip().lower()
        v = f.get("verified") or {}
        url = v.get("source_url") or v.get("open_evidence_url")
        if not url:
            continue
        row = {
            "slug": f.get("slug", "?"), "name": f.get("name", "?"),
            "start_month": sm, "end_month": em, "url": url,
            "status": None, "verdict": None, "detail": "",
        }
        rows.append(row)
        urls_to_fetch.setdefault(url, []).append(row)

    if not rows:
        print(f"[{country}/{city}] no annual festivals with source_url + start_month to check.")
        return 0

    print(f"[{country}/{city}] checking {len(urls_to_fetch)} festival sources for {len(rows)} festivals...")
    fetched: dict[str, tuple[str, str]] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(_fetch, u): u for u in urls_to_fetch}
        for fut in as_completed(futures):
            url = futures[fut]
            fetched[url] = fut.result()

    err = 0
    warn = 0
    for url, (status, text) in fetched.items():
        for row in urls_to_fetch[url]:
            row["status"] = status
            if not text:
                row["verdict"] = "FETCH_FAIL"
                warn += 1
                continue
            counts = _mentioned_months(text)
            claimed_count = counts[row["start_month"]] + (counts[row["end_month"]] if row["end_month"] != row["start_month"] else 0)
            other = sorted(((m, n) for m, n in counts.items() if m not in {row["start_month"], row["end_month"]} and n > 0), key=lambda x: -x[1])
            top_other = other[:3]
            row["counts"] = counts
            if claimed_count >= 1:
                row["verdict"] = "OK"
                row["detail"] = f"start_month={row['start_month']} found ({claimed_count}x)"
            else:
                # Did some OTHER month dominate?
                if top_other and top_other[0][1] >= 3:
                    row["verdict"] = "MISS"
                    row["detail"] = f"claimed {row['start_month']} not found; page dominantly mentions {top_other[0][0]} ({top_other[0][1]}x) — possible wrong month"
                    err += 1
                else:
                    row["verdict"] = "UNKNOWN"
                    row["detail"] = "page doesn't mention claimed month or any other clearly — source isn't date-specific"
                    warn += 1

    print()
    print(f"{'slug':40s} {'claimed':10s} {'status':10s} verdict")
    print("-" * 110)
    for row in sorted(rows, key=lambda r: (r["verdict"] == "OK", r["slug"])):
        if row["verdict"] == "OK":
            continue
        print(f"  {row['slug']:38s} {row['start_month']:10s} {row['status']:10s} {row['verdict']}: {row['detail']}")
    ok = sum(1 for r in rows if r["verdict"] == "OK")
    print()
    print(f"[{country}/{city}] OK: {ok}/{len(rows)}  MISS: {err}  fetch-fail/UNKNOWN: {warn}")
    return 1 if err else 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()
    if args.all:
        targets = []
        for cd in sorted(SITE_DATA.iterdir()):
            if not cd.is_dir():
                continue
            for cy in sorted(cd.iterdir()):
                if (cy / "data").exists():
                    targets.append((cd.name, cy.name))
    elif args.country and args.city:
        targets = [(args.country, args.city)]
    else:
        p.error("Pass --all or --country + --city")
        return 2
    total = sum(check_city(c, s) for c, s in targets)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
