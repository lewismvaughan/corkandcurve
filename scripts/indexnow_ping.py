#!/usr/bin/env python3
"""
Ping IndexNow with a list of URLs so Bing / Yandex / Seznam re-crawl
them within hours instead of waiting days for their next scheduled pass.

Usage:
    python3 scripts/indexnow_ping.py <url> [<url> ...]
    python3 scripts/indexnow_ping.py --city united-states new-york-city

Requires `indexnow_key` in data/site_config.json and a key file at
content/<key>.txt (referenced via `keyLocation` in the POST).

Designed to be called from ship_city.sh after a successful city ship.
Non-fatal on errors (network issues should not block a deploy).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"

ENDPOINT = "https://api.indexnow.org/IndexNow"
TIMEOUT_SECONDS = 10

# Derive BASE/HOST from site_config so this never drifts back to the
# TableJourney fork's domain (the bug that produced 403 on Burgundy:
# submitting tablejourney.com URLs with a corkandcurve.com key file).
_CFG = json.loads((REPO_ROOT / "data" / "site_config.json").read_text("utf-8"))
BASE = (_CFG.get("base_url") or "https://corkandcurve.com").rstrip("/")
HOST = BASE.split("://", 1)[-1]


def _load_key() -> str:
    cfg = json.loads((REPO_ROOT / "data" / "site_config.json").read_text("utf-8"))
    key = (cfg.get("indexnow_key") or "").strip()
    if not key:
        raise SystemExit("indexnow_key missing from data/site_config.json")
    # Sanity check the key file exists at the public root.
    if not (CONTENT / f"{key}.txt").exists():
        raise SystemExit(
            f"Key file content/{key}.txt missing. IndexNow needs this fetchable "
            f"at https://{HOST}/{key}.txt for the ping to be accepted."
        )
    return key


def _urls_for_city(country_slug: str, city_slug: str) -> list[str]:
    """All URLs we want crawled when a city ships: hub, 24 topic pages,
    every per-entity page generate_entity_pages emits. Cheap to enumerate
    by walking content/ once."""
    city_root = CONTENT / country_slug / city_slug
    if not city_root.exists():
        return []
    urls: list[str] = []
    for idx in city_root.rglob("index.html"):
        rel = idx.parent.relative_to(CONTENT).as_posix()
        urls.append(f"{BASE}/{rel}/")
    # Always include the homepage + sitemap so trending content re-surfaces.
    urls.append(f"{BASE}/")
    urls.append(f"{BASE}/sitemap.xml")
    # Deduplicate, stable order.
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def ping(urls: list[str]) -> int:
    """POST a batch to IndexNow. Returns the HTTP status code (or 0 on
    network failure). 200 + 202 are success; 422 means the host or key
    is wrong; 429 means rate-limited."""
    if not urls:
        print("indexnow: no urls to submit", file=sys.stderr)
        return 0
    key = _load_key()
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"{BASE}/{key}.txt",
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as r:
            status = r.status
            print(f"indexnow: {status} ({len(urls)} URLs submitted)")
            return status
    except urllib.error.HTTPError as e:
        # IndexNow returns the body in error responses with the reason.
        print(f"indexnow: HTTP {e.code} - {e.read().decode('utf-8', errors='replace')[:300]}", file=sys.stderr)
        return e.code
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"indexnow: network error - {e}", file=sys.stderr)
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("urls", nargs="*", default=[], help="absolute URLs to submit")
    g.add_argument("--city", nargs=2, metavar=("COUNTRY", "CITY"),
                   help="enumerate all URLs under content/<country>/<city>/ and submit them")
    args = ap.parse_args()

    if args.city:
        country, city = args.city
        urls = _urls_for_city(country, city)
        if not urls:
            print(f"indexnow: no pages found under content/{country}/{city}/", file=sys.stderr)
            return 0
    else:
        urls = [u for u in args.urls if u.startswith(BASE)]
        if not urls:
            print(f"indexnow: no URLs given (or none matched {BASE})", file=sys.stderr)
            return 0

    status = ping(urls)
    # Non-fatal: deploy should not fail because IndexNow had a hiccup.
    return 0 if status in (200, 202, 0) else 0


if __name__ == "__main__":
    sys.exit(main())
