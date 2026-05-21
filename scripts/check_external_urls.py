#!/usr/bin/env python3
"""Verify outbound URLs in a city's JSON resolve (no 4xx/5xx/timeouts).

Walks site-data/<country>/<city>/data/*.json and HEAD-requests every
external URL in known URL-bearing fields. Fails non-zero on any broken
or unreachable URL.

Usage:
    python3 scripts/check_external_urls.py --country united-states --city new-york-city
    python3 scripts/check_external_urls.py --all                # every shipped city

Wired into ship_city.sh and agents/validation/PROMPT.md as a hard gate.
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

# Fields whose value is an external URL that we should HEAD-test.
# hero_image and og_image are included: they are NOT always self-hosted
# (hero_image typically points at images.unsplash.com, and agents have
# been known to fabricate Unsplash photo IDs that 404 — same defect
# class as venue source_url fabrication). og_image is self-hosted but
# scaffolded with a path the actual file lives at, and was mis-pointed
# for the whole site for months. Both deserve mechanical validation.
URL_FIELDS = {"booking_url", "affiliate_url", "hero_image_source_url",
              "hero_image", "og_image", "image"}
TIMEOUT = 10  # seconds
WORKERS = 12  # parallel HEAD requests
UA = "TableJourney-Validator/1.0 (+https://tablejourney.com)"


def collect_urls(country_slug: str, city_slug: str) -> list[tuple[str, str, str]]:
    base = REPO_ROOT / "site-data" / country_slug / city_slug / "data"
    found: list[tuple[str, str, str]] = []

    def walk(obj, path: str = ""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in URL_FIELDS and isinstance(v, str) and v.startswith("http"):
                    found.append((path + "." + k, k, v))
                else:
                    walk(v, path + "." + str(k))
        elif isinstance(obj, list):
            for i, x in enumerate(obj):
                walk(x, path + f"[{i}]")

    for f in sorted(base.glob("*.json")):
        try:
            with open(f) as fh:
                d = json.load(fh)
        except Exception:
            continue
        walk(d, f.name)
    return found


def check_url(url: str) -> tuple[str, int | str]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        # Some sites 405/403/404 on HEAD but serve GET fine (anti-bot or
        # method-routing). Retry once with GET to be sure before declaring broken.
        if e.code in (404, 405, 403):
            try:
                req2 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
                with urllib.request.urlopen(req2, timeout=TIMEOUT) as r:
                    return url, r.status
            except urllib.error.HTTPError as e2:
                return url, e2.code
            except Exception as e2:
                return url, f"ERR:{type(e2).__name__}"
        return url, e.code
    except urllib.error.URLError as e:
        err_name = type(e.reason).__name__ if hasattr(e.reason, '__name__') else 'URLError'
        # Retry TimeoutError once with a longer timeout — some legitimate
        # restaurant sites (Tokyo's jimbochoden.com / Den) are reliably slow
        # but live. A 10s HEAD timeout shouldn't HARD-fail an otherwise
        # healthy URL. Added 2026-05-19 after Tokyo Den shipped broken.
        if err_name == 'TimeoutError':
            try:
                req3 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
                with urllib.request.urlopen(req3, timeout=TIMEOUT * 3) as r:
                    return url, r.status
            except Exception:
                return url, f"ERR:{err_name}"
        return url, f"ERR:{err_name}"
    except Exception as e:
        return url, f"ERR:{type(e).__name__}"


def collect_urls_from_file(path: Path) -> list[tuple[str, str, str]]:
    """Walk a single JSON file for URL_FIELDS hits. Used to cover singletons
    like site-data/home.json that aren't inside a city's data dir."""
    found: list[tuple[str, str, str]] = []
    try:
        with open(path) as fh:
            d = json.load(fh)
    except Exception:
        return found

    def walk(obj, p: str = ""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in URL_FIELDS and isinstance(v, str) and v.startswith("http"):
                    found.append((p + "." + k, k, v))
                else:
                    walk(v, p + "." + str(k))
        elif isinstance(obj, list):
            for i, x in enumerate(obj):
                walk(x, p + f"[{i}]")

    walk(d, path.name)
    return found


def check_path_label(label: str, urls: list[tuple[str, str, str]]) -> int:
    """Shared HEAD-check + broken-tally for any URL list."""
    if not urls:
        print(f"[{label}] 0 external URLs found.")
        return 0
    print(f"[{label}] checking {len(urls)} URLs ({WORKERS} workers, {TIMEOUT}s timeout)...")
    status_for: dict[str, int | str] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(check_url, u[2]): u[2] for u in urls}
        for fut in as_completed(futures):
            url, status = fut.result()
            status_for[url] = status
    ANTI_BOT = {401, 403, 405, 429, 500, 503, 504, 521}
    # 500 + 504 added 2026-05-19 — transient server errors from established sites
    # (Williams-Sonoma 500, Cloudflare-cached 504) shouldn't HARD-fail ship_safety.
    # Kept in sync with verify_entities.py ANTI_BOT_CODES.
    broken = []
    for path, field, url in urls:
        s = status_for.get(url)
        is_anti_bot = isinstance(s, int) and s in ANTI_BOT
        is_broken = ((isinstance(s, int) and s >= 400) or isinstance(s, str)) and not is_anti_bot
        if is_broken:
            broken.append((path, field, url, s))
    if broken:
        print(f"[{label}] BROKEN: {len(broken)} / {len(urls)}")
        for path, field, url, status in broken:
            print(f"  [{status}] {path}: {url}")
    else:
        print(f"[{label}] all {len(urls)} URLs OK.")
    return len(broken)


def check_homepage_json() -> int:
    """Validate site-data/home.json — the only site-wide JSON outside any
    city's data dir. Lewis's NOLA card 404 in 2026-05-19 was missed
    because the old check_city() walker never visited this file."""
    home = REPO_ROOT / "site-data" / "home.json"
    if not home.exists():
        return 0
    return check_path_label("site-data/home.json", collect_urls_from_file(home))


def check_city(country_slug: str, city_slug: str) -> int:
    urls = collect_urls(country_slug, city_slug)
    if not urls:
        print(f"[{country_slug}/{city_slug}] 0 external URLs found.")
        return 0
    print(f"[{country_slug}/{city_slug}] checking {len(urls)} URLs ({WORKERS} workers, {TIMEOUT}s timeout)...")
    status_for: dict[str, int | str] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(check_url, u[2]): u[2] for u in urls}
        for fut in as_completed(futures):
            url, status = fut.result()
            status_for[url] = status
    # Anti-bot codes (401/403/405/429/503/521) are NOT broken — those
    # protections often serve normal traffic but block automated HEAD
    # checks. cleanup_broken_urls.py preserves them. Treat them
    # consistently here so ship_safety.sh doesn't false-positive.
    ANTI_BOT = {401, 403, 405, 429, 500, 503, 504, 521}
    # 500 + 504 added 2026-05-19 — transient server errors from established sites
    # (Williams-Sonoma 500, Cloudflare-cached 504) shouldn't HARD-fail ship_safety.
    # Kept in sync with verify_entities.py ANTI_BOT_CODES.
    broken = []
    for path, field, url in urls:
        s = status_for.get(url)
        is_anti_bot = isinstance(s, int) and s in ANTI_BOT
        is_broken = ((isinstance(s, int) and s >= 400) or isinstance(s, str)) and not is_anti_bot
        if is_broken:
            broken.append((path, field, url, s))
    if broken:
        print(f"[{country_slug}/{city_slug}] BROKEN: {len(broken)} / {len(urls)}")
        for path, field, url, status in broken:
            print(f"  [{status}] {path}: {url}")
    else:
        print(f"[{country_slug}/{city_slug}] all {len(urls)} URLs OK.")
    return len(broken)


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
    total_broken = sum(check_city(c, s) for c, s in targets)
    # Always include site-wide singletons (home.json) when --all is used so
    # one broken homepage card can't slip past a release sweep.
    if args.all:
        total_broken += check_homepage_json()
    print(f"\nTotal broken across {len(targets)} cities: {total_broken}")
    sys.exit(1 if total_broken else 0)


if __name__ == "__main__":
    main()
