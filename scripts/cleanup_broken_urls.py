#!/usr/bin/env python3
"""Strip confirmed-broken external URL fields from a city's JSON.

Pairs with scripts/check_external_urls.py. Statuses treated as broken
(field is removed):
    - 404 / 410 / 451                 (page gone, doesn't exist)
    - "ERR:*" e.g. URLError / DNS     (domain dead or wrong)

Statuses preserved (may be anti-bot blocks against a HEAD request, the
URL is probably fine in a browser):
    - 401 / 403 / 405

Statuses preserved with warning:
    - 5xx                              (transient server issue)

Usage:
    python3 scripts/cleanup_broken_urls.py --country united-states --city new-york-city
    python3 scripts/cleanup_broken_urls.py --all

Idempotent: rerun yields no change if the JSON has no broken URLs.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

URL_FIELDS = {"booking_url", "affiliate_url", "hero_image_source_url"}
TIMEOUT = 10
WORKERS = 12
UA = "TableJourney-Validator/1.0 (+https://tablejourney.com)"

REMOVE_STATUSES = (404, 410, 451)


def check_url(url: str):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status
    except urllib.error.HTTPError as e:
        if e.code in (404, 405, 403):
            try:
                req2 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
                with urllib.request.urlopen(req2, timeout=TIMEOUT) as r:
                    return r.status
            except urllib.error.HTTPError as e2:
                return e2.code
            except Exception as e2:
                return f"ERR:{type(e2).__name__}"
        return e.code
    except urllib.error.URLError as e:
        return f"ERR:{type(e.reason).__name__ if hasattr(e.reason, '__name__') else 'URLError'}"
    except Exception as e:
        return f"ERR:{type(e).__name__}"


def collect_urls(base: Path):
    found = []
    for f in sorted(base.glob("*.json")):
        try:
            with open(f) as fh:
                d = json.load(fh)
        except Exception:
            continue
        def walk(obj):
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    if k in URL_FIELDS and isinstance(v, str) and v.startswith("http"):
                        found.append((f, obj, k, v))
                    else:
                        walk(v)
            elif isinstance(obj, list):
                for x in obj:
                    walk(x)
        walk(d)
    # Cache the parsed JSON for atomic rewrite later
    return found


def clean_city(country: str, city: str):
    base = REPO_ROOT / "site-data" / country / city / "data"
    if not base.exists():
        print(f"[{country}/{city}] no data dir, skipping.")
        return 0

    found = collect_urls(base)
    if not found:
        print(f"[{country}/{city}] no URLs to check.")
        return 0
    urls = {u[3] for u in found}
    print(f"[{country}/{city}] checking {len(urls)} unique URLs ({len(found)} sites) ...")

    status = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(check_url, u): u for u in urls}
        for fut in as_completed(futures):
            status[futures[fut]] = fut.result()

    removed = 0
    kept_anti_bot = 0
    kept_5xx = 0
    files_touched = {}
    for f, container, key, url in found:
        s = status[url]
        is_remove = isinstance(s, int) and s in REMOVE_STATUSES
        is_err = isinstance(s, str) and s.startswith("ERR:")
        if is_remove or is_err:
            print(f"  REMOVE [{s}] {f.name} {key}={url}")
            del container[key]
            files_touched.setdefault(f, True)
            removed += 1
        elif isinstance(s, int) and s in (401, 403, 405):
            kept_anti_bot += 1
        elif isinstance(s, int) and s >= 500:
            print(f"  KEEP [{s} 5xx] {f.name} {key}={url}  (transient?)")
            kept_5xx += 1

    # Re-read + atomic write per touched file (preserves field order best-effort
    # because we mutated the in-memory dict; on write we just dump it).
    for f in files_touched:
        try:
            with open(f) as fh:
                # we already mutated; need to re-fetch original to re-walk and rebuild
                pass
            # Re-walk the JSON in this file to capture the cleaned state
            with open(f) as fh:
                d = json.load(fh)
            def walk_clean(obj):
                if isinstance(obj, dict):
                    for k in list(obj.keys()):
                        v = obj[k]
                        if k in URL_FIELDS and isinstance(v, str) and v.startswith("http"):
                            s = status.get(v)
                            if (isinstance(s, int) and s in REMOVE_STATUSES) or (isinstance(s, str) and s.startswith("ERR:")):
                                del obj[k]
                        else:
                            walk_clean(v)
                elif isinstance(obj, list):
                    for x in obj:
                        walk_clean(x)
            walk_clean(d)
            tmp = f.with_suffix(f.suffix + ".tmp")
            with open(tmp, "w") as fh:
                json.dump(d, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            tmp.replace(f)
        except Exception as e:
            print(f"  ERR rewriting {f}: {e}")

    print(
        f"[{country}/{city}] removed={removed}, kept_anti_bot={kept_anti_bot}, "
        f"kept_5xx={kept_5xx}, files_touched={len(files_touched)}"
    )
    return removed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    if args.all:
        targets = []
        for f in (REPO_ROOT / "site-data").rglob("*/data"):
            country = f.parent.parent.name
            city = f.parent.name
            if country == "data":
                continue
            targets.append((country, city))
    elif args.country and args.city:
        targets = [(args.country, args.city)]
    else:
        p.error("Either --all or both --country and --city are required")

    total = sum(clean_city(c, s) for c, s in targets)
    print(f"\nTotal URL fields removed across {len(targets)} cities: {total}")


if __name__ == "__main__":
    main()
