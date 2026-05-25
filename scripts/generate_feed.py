#!/usr/bin/env python3
"""
Write content/feed.xml (RSS 2.0) and content/site.webmanifest (PWA).

base.html links both site-wide:
  <link rel="manifest" href="/site.webmanifest">
  <link rel="alternate" type="application/rss+xml" href="/feed.xml">

The RSS feed carries one <item> per live wine-region hub. A region is
"live" when site-data/<country>/<region>/data/region.json exists AND
content/<country>/<region>/index.html has shipped. Country-level
region.json stubs are skipped.

Usage:
    python3 scripts/generate_feed.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
SITE_DATA = REPO_ROOT / "site-data"
BASE = "https://corkandcurve.com"


def _live_regions() -> list[dict]:
    regions: list[dict] = []
    if not SITE_DATA.exists():
        return regions
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country_slug = country_dir.name
        for region_dir in sorted(country_dir.iterdir()):
            if not region_dir.is_dir() or region_dir.name == "data":
                continue
            region_slug = region_dir.name
            region_json = region_dir / "data" / "region.json"
            if not region_json.exists():
                continue
            if not (CONTENT / country_slug / region_slug / "index.html").exists():
                continue
            try:
                payload = json.loads(region_json.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            dest = payload.get("destination", {}) or {}
            blurb = (dest.get("tagline") or dest.get("description")
                     or dest.get("overview") or "").strip()
            regions.append({
                "country_slug": country_slug,
                "region_slug": region_slug,
                "name": dest.get("name", region_slug.replace("-", " ").title()),
                "country": dest.get("country", country_slug.replace("-", " ").title()),
                "blurb": blurb,
            })
    regions.sort(key=lambda r: r["name"].lower())
    return regions


def _rfc822(dt: datetime) -> str:
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def write_feed() -> Path:
    now = datetime.now(timezone.utc)
    pub = _rfc822(now)
    items = []
    for r in _live_regions():
        link = f"{BASE}/{r['country_slug']}/{r['region_slug']}/"
        desc = r["blurb"] or f"The Cork & Curve wine guide to {r['name']}, {r['country']}."
        title = f"{r['name']}, {r['country']}"
        items.append(
            "    <item>\n"
            f"      <title>{escape(title)}</title>\n"
            f"      <link>{escape(link)}</link>\n"
            f"      <guid isPermaLink=\"true\">{escape(link)}</guid>\n"
            f"      <description>{escape(desc)}</description>\n"
            f"      <pubDate>{pub}</pubDate>\n"
            "    </item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Cork &amp; Curve</title>\n"
        f"    <link>{BASE}</link>\n"
        "    <description>Wine and spirits travel guides, written by editors on the ground. Where the world drinks.</description>\n"
        "    <language>en</language>\n"
        f"    <lastBuildDate>{pub}</lastBuildDate>\n"
        f'    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml" />\n'
        + "\n".join(items)
        + ("\n" if items else "")
        + "  </channel>\n"
        "</rss>\n"
    )
    out = CONTENT / "feed.xml"
    out.write_text(xml, encoding="utf-8")
    return out


def write_manifest() -> Path:
    manifest = {
        "name": "Cork & Curve",
        "short_name": "Cork & Curve",
        "description": "Wine and spirits travel guides. Where the world drinks.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#6b1f3a",
        "theme_color": "#6b1f3a",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        ],
    }
    out = CONTENT / "site.webmanifest"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    return out


def main() -> int:
    feed = write_feed()
    print(f"wrote {feed}")
    manifest = write_manifest()
    print(f"wrote {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
