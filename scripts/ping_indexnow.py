#!/usr/bin/env python3
"""Notify IndexNow (Bing, Yandex, Seznam) about changed tablejourney URLs.

IndexNow is the open protocol the non-Google search engines use to be told
when a page changes. One POST submits up to 10,000 URLs per host. Google
does not consume IndexNow but ignores it cleanly, so there is no downside
to pinging on every publish.

Usage:
  python3 scripts/ping_indexnow.py --all              # every URL in sitemap.xml
  python3 scripts/ping_indexnow.py /france/paris/     # one or more explicit URLs

Auth: a public key file is served at
  https://tablejourney.com/<INDEXNOW_KEY>.txt
containing only the key. IndexNow fetches that on first submission to prove
we own the host. The same key is sent in the POST body. The protocol is
spec'd at https://www.indexnow.org/documentation.

This script is NOT wired into ship_city.sh by default. Run it manually after
a publish you actually want crawled fast, or wire it up once we are sure of
the cadence (Bing rate-limits if you ping the same URL multiple times in a
short window).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import request
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
HOST = "tablejourney.com"
INDEXNOW_KEY = "5dbedeb25ac84e5fa160521e5b309b1d"
KEY_LOCATION = f"https://{HOST}/{INDEXNOW_KEY}.txt"
ENDPOINT = "https://api.indexnow.org/IndexNow"


def urls_from_sitemap() -> list[str]:
    """Pull every URL out of content/sitemap.xml, handling the single-file
    and sitemap-index shapes both produced by generate_sitemap.py."""
    sitemap_path = CONTENT / "sitemap.xml"
    if not sitemap_path.exists():
        raise FileNotFoundError(f"{sitemap_path} does not exist. Run scripts/generate_sitemap.py first.")
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    out: list[str] = []

    # Case 1: <urlset> directly under root.
    for loc in root.findall("sm:url/sm:loc", ns):
        if loc.text:
            out.append(loc.text.strip())

    # Case 2: <sitemapindex> referencing shard files.
    for shard_loc in root.findall("sm:sitemap/sm:loc", ns):
        if not shard_loc.text:
            continue
        shard_url = shard_loc.text.strip()
        # We only ship a single host, so the shard URL maps 1:1 to content/.
        shard_name = shard_url.rsplit("/", 1)[-1]
        shard_path = CONTENT / shard_name
        if not shard_path.exists():
            continue
        shard_tree = ET.parse(shard_path)
        for loc in shard_tree.getroot().findall("sm:url/sm:loc", ns):
            if loc.text:
                out.append(loc.text.strip())
    return out


def normalise_urls(urls: list[str]) -> list[str]:
    """Coerce relative paths and bare hostnames into absolute https URLs."""
    out: list[str] = []
    for u in urls:
        u = u.strip()
        if not u:
            continue
        if u.startswith("/"):
            u = f"https://{HOST}{u}"
        elif not u.startswith(("http://", "https://")):
            u = f"https://{HOST}/{u.lstrip('/')}"
        out.append(u)
    # De-duplicate while preserving order.
    seen = set()
    deduped = []
    for u in out:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return deduped


def submit(urls: list[str]) -> int:
    """POST a single IndexNow submission. Returns HTTP status code."""
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            return resp.status
    except Exception as e:  # noqa: BLE001
        print(f"ERROR posting to IndexNow: {e}", file=sys.stderr)
        return 0


# IndexNow accepts up to 10k URLs per request, but we batch smaller so a
# transient failure doesn't lose the whole publish.
BATCH = 1000


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="Submit every URL in sitemap.xml")
    p.add_argument("urls", nargs="*", help="Explicit URLs (or paths) to submit")
    p.add_argument("--dry-run", action="store_true", help="Print the payload without sending")
    args = p.parse_args()

    if args.all:
        urls = urls_from_sitemap()
    elif args.urls:
        urls = args.urls
    else:
        p.error("Pass --all or a list of URLs")
        return 2

    urls = normalise_urls(urls)
    if not urls:
        print("No URLs to submit.")
        return 0

    print(f"Submitting {len(urls)} URLs to IndexNow (key={INDEXNOW_KEY[:8]}…)")
    if args.dry_run:
        for u in urls[:10]:
            print(f"  {u}")
        if len(urls) > 10:
            print(f"  ... and {len(urls) - 10} more")
        print("(dry-run; not POSTed)")
        return 0

    fail = 0
    for i in range(0, len(urls), BATCH):
        batch = urls[i:i + BATCH]
        status = submit(batch)
        if 200 <= status < 300:
            print(f"  batch {i // BATCH + 1}: HTTP {status}  ({len(batch)} URLs)")
        else:
            print(f"  batch {i // BATCH + 1}: HTTP {status}  FAIL  ({len(batch)} URLs)")
            fail += 1
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
