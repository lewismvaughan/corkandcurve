#!/usr/bin/env python3
"""Internal-link-density analyzer for tablejourney.com.

Walks every HTML page in content/, builds a {page -> [outgoing_links]} map
plus the reverse index {page -> [incoming_links]}, and reports:

  * pages with fewer than MIN_IN incoming links (orphan SEO risk).
  * pages with fewer than MIN_OUT outgoing links (thin internal anchor).
  * the top-N pages by outgoing and incoming counts (so you can spot
    pages that are over- or under-leveraged).
  * pages that exist on disk but are not referenced from anywhere
    (true orphans, no incoming links at all).

Outputs:
  /tmp/tj_link_density.json   full report (every page, in/out counts)
  stdout summary suitable for skimming

Usage:
  python3 scripts/link_density.py [--min-in N] [--min-out N] [--top N]

Only internal links are considered. External links, mailto:, tel:, anchor-
only (#foo) and asset paths (.css, .png, .xml, etc.) are ignored. Trailing
slashes are normalised so /foo/ and /foo are treated as the same URL.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"

# Heuristics for what counts as a "page" vs an asset.
ASSET_SUFFIXES = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico",
    ".xml", ".json", ".txt", ".pdf", ".gif",
)
EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:")


class AnchorCollector(HTMLParser):
    """Collect href values from <a> tags only."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for k, v in attrs:
            if k == "href" and v:
                self.hrefs.append(v)
                break


def url_for_file(path: Path) -> str:
    """Return the canonical URL path served by Caddy for a content/ HTML file."""
    rel = path.relative_to(CONTENT)
    parts = rel.parts
    # index.html in any directory → that directory with trailing slash.
    if parts[-1] == "index.html":
        if len(parts) == 1:
            return "/"
        return "/" + "/".join(parts[:-1]) + "/"
    # 404.html and other one-off pages map to their literal URL.
    return "/" + "/".join(parts)


def is_internal_page_link(href: str) -> bool:
    """Filter out external, asset, anchor-only, and protocol-relative URLs."""
    if not href:
        return False
    h = href.strip()
    if h.startswith("#"):
        return False
    if h.startswith(EXTERNAL_PREFIXES):
        # Allow tablejourney.com absolute URLs - we strip and treat as internal.
        if h.startswith(("https://tablejourney.com", "http://tablejourney.com")):
            return True
        return False
    if not h.startswith("/"):
        return False
    # Strip query/fragment for asset-suffix check.
    h_path = h.split("?", 1)[0].split("#", 1)[0]
    if h_path.lower().endswith(ASSET_SUFFIXES):
        return False
    return True


def normalise_internal(href: str) -> str:
    """Strip query/fragment, strip absolute host, return path with trailing slash
    (when the URL looks like a directory). Lowercased to dedupe case noise."""
    h = href.strip()
    for pfx in ("https://tablejourney.com", "http://tablejourney.com"):
        if h.startswith(pfx):
            h = h[len(pfx):] or "/"
    h = h.split("?", 1)[0].split("#", 1)[0]
    if not h.startswith("/"):
        h = "/" + h
    # Don't add a slash to file URLs (e.g. /404.html, /sitemap.xml).
    # The asset check upstream usually removes these, but 404.html is the
    # exception we explicitly want to count as a page.
    if "." not in h.rsplit("/", 1)[-1] and not h.endswith("/"):
        h = h + "/"
    return h.lower()


def collect_pages() -> dict[str, Path]:
    """Map canonical URL -> source file for every HTML page under content/."""
    pages: dict[str, Path] = {}
    for f in CONTENT.rglob("*.html"):
        if not f.is_file():
            continue
        url = url_for_file(f).lower()
        pages[url] = f
    return pages


def extract_links(html: str) -> list[str]:
    """Return every href on internal-looking anchors."""
    parser = AnchorCollector()
    try:
        parser.feed(html)
    except Exception:  # noqa: BLE001
        # html.parser can occasionally choke on malformed pages; fall back to
        # a regex sweep so we still emit data for the page.
        return re.findall(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', html, flags=re.I)
    return parser.hrefs


def build_graph(pages: dict[str, Path]) -> tuple[dict, dict]:
    """Return (out_map, in_map) where each maps url -> sorted unique list."""
    out_map: dict[str, set[str]] = defaultdict(set)
    in_map: dict[str, set[str]] = defaultdict(set)
    for url, path in pages.items():
        html = path.read_text(encoding="utf-8", errors="replace")
        for href in extract_links(html):
            if not is_internal_page_link(href):
                continue
            target = normalise_internal(href)
            # Self-links are noise.
            if target == url:
                continue
            out_map[url].add(target)
            in_map[target].add(url)
    # Convert to sorted lists.
    return (
        {k: sorted(v) for k, v in out_map.items()},
        {k: sorted(v) for k, v in in_map.items()},
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--min-in", type=int, default=3,
                   help="Pages with fewer incoming links than this get flagged.")
    p.add_argument("--min-out", type=int, default=5,
                   help="Pages with fewer outgoing links than this get flagged.")
    p.add_argument("--top", type=int, default=10,
                   help="How many top-N rows to show in each ranking.")
    args = p.parse_args()

    pages = collect_pages()
    print(f"Pages on disk: {len(pages)}")
    out_map, in_map = build_graph(pages)

    # Build report rows for every page on disk (whether or not it has
    # links in/out). Pages that exist but are unlinked are the worst kind
    # of orphan, so we want to surface them.
    rows: list[dict] = []
    for url in sorted(pages):
        rows.append({
            "url": url,
            "in":  len(in_map.get(url, [])),
            "out": len(out_map.get(url, [])),
        })

    # Pages referenced by anchors that don't exist on disk (broken
    # internal links, caught earlier by audit_live but useful to surface
    # here too for cross-checking).
    referenced = set(in_map.keys())
    missing = sorted(t for t in referenced if t not in pages)

    # Surface findings.
    print()
    print(f"Total internal anchor edges: {sum(len(v) for v in out_map.values())}")
    print(f"Pages with at least 1 incoming link: {sum(1 for r in rows if r['in'] > 0)}")
    print(f"Pages with 0 incoming links (orphan): {sum(1 for r in rows if r['in'] == 0)}")
    print(f"Pages with at least 1 outgoing link: {sum(1 for r in rows if r['out'] > 0)}")
    print()

    low_in = [r for r in rows if r["in"] < args.min_in]
    low_out = [r for r in rows if r["out"] < args.min_out]
    print(f"Pages with fewer than {args.min_in} incoming links: {len(low_in)}")
    for r in sorted(low_in, key=lambda x: (x["in"], x["url"]))[:30]:
        print(f"  in={r['in']:3d}  out={r['out']:3d}  {r['url']}")
    print()
    print(f"Pages with fewer than {args.min_out} outgoing links: {len(low_out)}")
    for r in sorted(low_out, key=lambda x: (x["out"], x["url"]))[:30]:
        print(f"  in={r['in']:3d}  out={r['out']:3d}  {r['url']}")
    print()

    print(f"Top {args.top} most-linked-to pages (incoming):")
    for r in sorted(rows, key=lambda x: (-x["in"], x["url"]))[:args.top]:
        print(f"  in={r['in']:3d}  out={r['out']:3d}  {r['url']}")
    print()
    print(f"Top {args.top} hub pages (outgoing):")
    for r in sorted(rows, key=lambda x: (-x["out"], x["url"]))[:args.top]:
        print(f"  in={r['in']:3d}  out={r['out']:3d}  {r['url']}")
    print()

    if missing:
        print(f"WARN: {len(missing)} anchored URL(s) have no matching file on disk:")
        for m in missing[:30]:
            print(f"  -> {m}  (linked from {len(in_map[m])} page(s))")
        if len(missing) > 30:
            print(f"  ... and {len(missing) - 30} more")

    report = {
        "pages_on_disk": len(pages),
        "edges": sum(len(v) for v in out_map.values()),
        "rows": rows,
        "low_in": [r["url"] for r in low_in],
        "low_out": [r["url"] for r in low_out],
        "missing_targets": missing,
        "in_map": in_map,
        "out_map": out_map,
        "thresholds": {"min_in": args.min_in, "min_out": args.min_out},
    }
    out_path = Path("/tmp/tj_link_density.json")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nFull report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
