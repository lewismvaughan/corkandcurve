#!/usr/bin/env python3
"""Site-wide SEO hygiene scanner.

Walks every HTML page under content/ and reports:

  * duplicate <title> tags (Google penalises duplicate titles).
  * duplicate <meta name="description"> values.
  * pages whose title is outside the 30-65 char SERP sweet spot.
  * pages whose description is outside the 140-165 char band.
  * pages with multiple <h1>.
  * pages with no canonical, or canonical pointing somewhere
    that doesn't match the page's URL.
  * pages with multiple canonicals (Google picks one but warns).
  * pages with low-value anchor text: "click here", "read more",
    "here", "this", "learn more", etc.
  * pages with <img> tags missing alt or with empty alt.

Output:
  /tmp/tj_seo_hygiene.json     full report
  stdout summary

Usage:
  python3 scripts/check_seo_hygiene.py
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
BASE = "https://tablejourney.com"

# Anchor text that signals lazy writing. Lowercased + stripped before compare.
LOW_VALUE_ANCHORS = {
    "click here", "read more", "here", "this", "learn more",
    "more", "see more", "details", "go", "info", "view",
    "click", "read", "link",
}

# Length bands. Title 70 matches the cap used by build_entity_context
# (the generator already drops " | TableJourney" suffix above 70). Title 30
# lower bound stays the same; anything terser is usually intentional (404).
# Description band is the SERP sweet spot — short descs (130-140) are
# acceptable but flagged to surface tightening opportunities.
TITLE_MIN, TITLE_MAX = 30, 70
DESC_MIN, DESC_MAX = 140, 165


class PageParser(HTMLParser):
    """Pull out the SEO-relevant signals from a single HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str = ""
        self.in_title = False
        self.description: str = ""
        self.canonical: list[str] = []
        self.h1_count = 0
        self.in_h1 = False
        self.h1_text: str = ""
        self.imgs: list[dict] = []
        self.anchors: list[dict] = []
        self._anchor_buf: list[str] | None = None
        self._anchor_href: str = ""
        self.viewport: str = ""
        self.robots: str = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            if name == "description":
                self.description = a.get("content", "") or ""
            elif name == "viewport":
                self.viewport = a.get("content", "") or ""
            elif name == "robots":
                self.robots = a.get("content", "") or ""
        elif tag == "link":
            if (a.get("rel") or "").lower() == "canonical":
                self.canonical.append(a.get("href", "") or "")
        elif tag == "h1":
            self.h1_count += 1
            if self.h1_count == 1:
                self.in_h1 = True
        elif tag == "img":
            self.imgs.append({
                "src": a.get("src", ""),
                "alt": a.get("alt"),
                "width": a.get("width"),
                "height": a.get("height"),
                "loading": a.get("loading"),
                "fetchpriority": a.get("fetchpriority"),
            })
        elif tag == "a":
            self._anchor_buf = []
            self._anchor_href = a.get("href", "") or ""

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "a" and self._anchor_buf is not None:
            text = " ".join("".join(self._anchor_buf).split()).strip()
            self.anchors.append({"href": self._anchor_href, "text": text})
            self._anchor_buf = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1 and self.h1_count == 1:
            self.h1_text += data
        if self._anchor_buf is not None:
            self._anchor_buf.append(data)


def url_for_file(path: Path) -> str:
    rel = path.relative_to(CONTENT)
    parts = rel.parts
    if parts[-1] == "index.html":
        if len(parts) == 1:
            return "/"
        return "/" + "/".join(parts[:-1]) + "/"
    return "/" + "/".join(parts)


def scan() -> dict:
    pages: list[dict] = []
    titles: dict[str, list[str]] = defaultdict(list)
    descs: dict[str, list[str]] = defaultdict(list)

    for f in sorted(CONTENT.rglob("*.html")):
        if not f.is_file():
            continue
        url = url_for_file(f)
        html = f.read_text(encoding="utf-8", errors="replace")
        p = PageParser()
        try:
            p.feed(html)
        except Exception as e:  # noqa: BLE001
            pages.append({"url": url, "parse_error": str(e)})
            continue

        title = " ".join(p.title.split()).strip()
        desc = " ".join(p.description.split()).strip()
        titles[title].append(url)
        descs[desc].append(url)

        # Anchor scan. SEO cares about anchor text on links that pass
        # PageRank — that means cross-page anchors. Skip in-page (#foo)
        # anchors, which are TOC + skip-link UX patterns Google understands.
        # Also skip mailto:/tel:/external links since those don't pass
        # internal-link equity.
        low_value_anchors = []
        for anc in p.anchors:
            href = anc["href"]
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            # External links: not our internal SEO concern here.
            if href.startswith(("http://", "https://")) and "tablejourney.com" not in href:
                continue
            t = anc["text"].lower().strip().rstrip("→").strip()
            t = re.sub(r"\s+", " ", t)
            if not t:
                continue
            if t in LOW_VALUE_ANCHORS:
                low_value_anchors.append({"href": href, "text": anc["text"]})

        # Image alt scan.
        missing_alt = [i for i in p.imgs if i["alt"] is None or i["alt"] == ""]

        # Canonical check.
        canonicals = p.canonical
        expected_canon = f"{BASE}{url}"
        canon_mismatches: list[str] = []
        for c in canonicals:
            # Normalise trailing slash for the compare.
            c_norm = c
            if c_norm != expected_canon:
                canon_mismatches.append(c)

        pages.append({
            "url": url,
            "title": title,
            "title_len": len(title),
            "title_in_band": TITLE_MIN <= len(title) <= TITLE_MAX,
            "description": desc,
            "desc_len": len(desc),
            "desc_in_band": DESC_MIN <= len(desc) <= DESC_MAX,
            "canonicals": canonicals,
            "canonical_expected": expected_canon,
            "canonical_mismatch": bool(canon_mismatches),
            "canonical_count": len(canonicals),
            "h1_count": p.h1_count,
            "h1_text": " ".join(p.h1_text.split()).strip(),
            "img_count": len(p.imgs),
            "img_missing_alt": len(missing_alt),
            "img_missing_alt_samples": [i.get("src") for i in missing_alt[:3]],
            "anchor_count": len(p.anchors),
            "low_value_anchors": low_value_anchors,
            "viewport": p.viewport,
            "robots": p.robots,
        })

    dup_titles = {t: urls for t, urls in titles.items() if len(urls) > 1 and t}
    dup_descs = {d: urls for d, urls in descs.items() if len(urls) > 1 and d}

    return {
        "pages": pages,
        "duplicate_titles": dup_titles,
        "duplicate_descriptions": dup_descs,
    }


def main() -> int:
    report = scan()
    pages = report["pages"]
    print(f"Pages scanned: {len(pages)}")
    print()

    # Title duplicates.
    dups = report["duplicate_titles"]
    print(f"Duplicate titles: {len(dups)} (across {sum(len(v) for v in dups.values())} pages)")
    for t, urls in sorted(dups.items()):
        print(f"  [{len(urls)}x] {t!r}")
        for u in urls[:5]:
            print(f"      - {u}")
        if len(urls) > 5:
            print(f"      ... and {len(urls) - 5} more")
    print()

    # Description duplicates.
    dups_d = report["duplicate_descriptions"]
    print(f"Duplicate descriptions: {len(dups_d)} (across {sum(len(v) for v in dups_d.values())} pages)")
    for d, urls in sorted(dups_d.items()):
        snippet = d[:80] + ("…" if len(d) > 80 else "")
        print(f"  [{len(urls)}x] {snippet!r}")
        for u in urls[:5]:
            print(f"      - {u}")
        if len(urls) > 5:
            print(f"      ... and {len(urls) - 5} more")
    print()

    # Title length outliers.
    bad_titles = [p for p in pages if not p.get("title_in_band", False)]
    print(f"Titles outside {TITLE_MIN}-{TITLE_MAX} chars: {len(bad_titles)}")
    for p in bad_titles[:15]:
        print(f"  {p['title_len']:3d}  {p['url']}  -> {p['title']!r}")
    if len(bad_titles) > 15:
        print(f"  ... and {len(bad_titles) - 15} more")
    print()

    # Description length outliers.
    bad_descs = [p for p in pages if not p.get("desc_in_band", False)]
    print(f"Descriptions outside {DESC_MIN}-{DESC_MAX} chars: {len(bad_descs)}")
    for p in bad_descs[:15]:
        snippet = (p["description"] or "")[:60]
        print(f"  {p['desc_len']:3d}  {p['url']}  -> {snippet!r}…")
    if len(bad_descs) > 15:
        print(f"  ... and {len(bad_descs) - 15} more")
    print()

    # H1 anomalies.
    bad_h1 = [p for p in pages if p.get("h1_count", 0) != 1]
    print(f"Pages without exactly one H1: {len(bad_h1)}")
    for p in bad_h1[:15]:
        print(f"  h1_count={p['h1_count']}  {p['url']}")
    print()

    # Canonical issues.
    bad_canon = [p for p in pages if p.get("canonical_count", 0) != 1 or p.get("canonical_mismatch")]
    print(f"Pages with canonical anomalies: {len(bad_canon)}")
    for p in bad_canon[:15]:
        print(f"  count={p.get('canonical_count')}  mismatch={p.get('canonical_mismatch')}  {p['url']}")
        for c in p.get("canonicals", []):
            print(f"      <link rel=canonical href={c!r}> (expected {p['canonical_expected']!r})")
    print()

    # Low-value anchors.
    bad_anchor_pages = [p for p in pages if p.get("low_value_anchors")]
    total_low = sum(len(p["low_value_anchors"]) for p in bad_anchor_pages)
    print(f"Pages with low-value anchor text: {len(bad_anchor_pages)}  (total {total_low} anchors)")
    for p in bad_anchor_pages[:10]:
        print(f"  {p['url']}")
        for a in p["low_value_anchors"][:3]:
            print(f"      <a href={a['href']!r}>{a['text']!r}</a>")
    print()

    # Missing alt.
    bad_alt = [p for p in pages if p.get("img_missing_alt", 0) > 0]
    total_imgs_missing = sum(p["img_missing_alt"] for p in bad_alt)
    print(f"Pages with images missing alt: {len(bad_alt)}  (total {total_imgs_missing} imgs)")
    for p in bad_alt[:10]:
        print(f"  {p['url']}  {p['img_missing_alt']}/{p['img_count']} imgs missing alt")
        for src in p.get("img_missing_alt_samples", []):
            print(f"      src={src!r}")
    print()

    out = Path("/tmp/tj_seo_hygiene.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Full report: {out}")

    failed = bool(dups) or bool(dups_d) or bool(bad_canon) or bool(bad_alt)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
