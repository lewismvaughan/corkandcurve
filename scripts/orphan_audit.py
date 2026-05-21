#!/usr/bin/env python3
"""Orphan audit: find every URL we ship that has zero inbound links
from page content (not counting global nav / footer / header).

Orphans = pages Google discovers via sitemap only; they pass no
PageRank-equivalent and rarely rank. We aim for zero orphans of any
generator-emitted page type. See docs/STANDARDS.md section 1.

Reports grouped by page type with a sample of orphan URLs and a count.
Exits 0 always (this is a SOFT audit; fold into CI as a hard gate by
checking the printed counts).

Usage:
    python scripts/orphan_audit.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
BASE_DOMAIN = "tablejourney.com"

LINK_RE = re.compile(r'<a\s[^>]*href="([^"]+)"', re.IGNORECASE)
# Strip nav + header + footer + breadcrumbs (they're global / boilerplate
# links and don't count as "real" inbound editorial links).
STRIP_RE = re.compile(
    r"<(?:nav|footer|header)[^>]*>.*?</(?:nav|footer|header)>",
    re.DOTALL | re.IGNORECASE,
)
BREADCRUMB_RE = re.compile(
    r'<(?:ol|ul|nav)\s+[^>]*class="[^"]*breadcrumb[^"]*"[^>]*>.*?</(?:ol|ul|nav)>',
    re.DOTALL | re.IGNORECASE,
)


def page_type(u: str) -> str:
    parts = u.strip("/").split("/")
    if u == "/":
        return "homepage"
    if u.startswith("/topics/"):
        return "topic (cross-city)"
    if u.startswith("/cuisine/"):
        return "cuisine (cross-cut)"
    if u.startswith("/dish/"):
        return "dish (cross-cut)"
    if u.startswith("/neighborhood/"):
        return "neighborhood (cross-cut)"
    if u.startswith(("/cuisines/", "/dishes/", "/neighborhoods/")):
        return "global-index"
    if u.startswith(("/about", "/cities/", "/contact", "/privacy", "/terms",
                     "/cookies", "/disclaimer", "/editorial-standards",
                     "/search")):
        return "chrome"
    if len(parts) == 1:
        return "country"
    if len(parts) == 2:
        return "city-or-state"
    if len(parts) == 3:
        last = parts[-1]
        if last in {"cuisines", "signature-dishes", "neighborhoods", "dietary"}:
            return "scoped-index"
        return "city-topic"
    if len(parts) == 4:
        if parts[2] in {"dietary", "cuisine", "dish"}:
            return f"city × {parts[2]}"
        return "entity"
    return f"other ({len(parts)} parts)"


def main() -> int:
    all_urls: set[str] = set()
    for idx in CONTENT.rglob("index.html"):
        rel = "/" + str(idx.relative_to(CONTENT)).replace("\\", "/").replace("index.html", "")
        if rel == "/index.html/":
            rel = "/"
        all_urls.add(rel)

    print(f"Total shipped URLs: {len(all_urls)}")

    inbound: dict[str, int] = defaultdict(int)
    for idx in CONTENT.rglob("index.html"):
        html = idx.read_text(encoding="utf-8", errors="replace")
        # Strip global / boilerplate regions so we count only editorial links.
        body = STRIP_RE.sub("", html)
        body = BREADCRUMB_RE.sub("", body)
        for href in LINK_RE.findall(body):
            u = href.split("#")[0].split("?")[0]
            if u.startswith("http"):
                p = urlparse(u)
                if BASE_DOMAIN not in p.netloc:
                    continue
                u = p.path
            if not u.startswith("/"):
                continue
            if not u.endswith("/") and "." not in u.rsplit("/", 1)[-1]:
                u = u + "/"
            if u in all_urls:
                inbound[u] += 1

    orphans = sorted(u for u in all_urls if inbound[u] == 0)
    by_type: dict[str, list[str]] = defaultdict(list)
    for o in orphans:
        by_type[page_type(o)].append(o)

    print(f"\nOrphans (zero editorial inbound links): {len(orphans)}")
    if not orphans:
        print("  ✓ no orphans")
        return 0

    for t in sorted(by_type.keys()):
        pages = by_type[t]
        print(f"\n  {t}: {len(pages)} orphans")
        for p in pages[:5]:
            print(f"    {p}")
        if len(pages) > 5:
            print(f"    ...and {len(pages) - 5} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
