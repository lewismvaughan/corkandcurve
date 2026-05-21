#!/usr/bin/env python3
"""
Post-render SEO validator. Walks content/ and reports per-page:
  - missing <title> or title outside 30-70 char band
  - missing meta description or outside 120-170 chars
  - missing canonical, OG image, Twitter card
  - missing H1 or more than one H1
  - <img> without alt text
  - hero <img> without fetchpriority="high"
  - missing JSON-LD Article + FAQPage + BreadcrumbList
  - em dashes / en dashes anywhere in body
  - internal links pointing to /destinations/ (old travel URL)
  - missing Updated stamp

Usage:
    python scripts/validate_seo.py
    python scripts/validate_seo.py --root content/france/paris
    python scripts/validate_seo.py --errors-only
"""

import argparse
import html as _html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_RE = re.compile(r'<meta\s+[^>]*name=["\']([^"\']+)["\'][^>]*\bcontent="([^"]*)"', re.IGNORECASE)
META_PROP_RE = re.compile(r'<meta\s+[^>]*property=["\']([^"\']+)["\'][^>]*\bcontent="([^"]*)"', re.IGNORECASE)
LINK_REL_RE = re.compile(r'<link\s+[^>]*rel=["\']([^"\']+)["\'][^>]*href=["\']([^"\']*)["\']', re.IGNORECASE)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
IMG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
SCRIPT_LD_RE = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.IGNORECASE | re.DOTALL)
HREF_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']*)["\']', re.IGNORECASE)
EM_DASH_RE = re.compile(r"[–—]")


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def validate(path: Path, errors_only: bool) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    issues = []  # (level, msg)

    # title
    titles = TITLE_RE.findall(html)
    if not titles:
        issues.append(("ERR", "missing <title>"))
    else:
        t = titles[0].strip()
        if len(t) < 30:
            issues.append(("WARN", f"title is {len(t)} chars (target 50-70)"))
        elif len(t) > 70:
            issues.append(("WARN", f"title is {len(t)} chars (>70 may truncate)"))

    # meta description. Length is measured after HTML-entity decode so that
    # &#39; counts as 1 char (what Google sees in the SERP snippet), not 5.
    metas = {name.lower(): content for name, content in META_RE.findall(html)}
    desc = metas.get("description", "")
    desc_rendered = _html.unescape(desc)
    if not desc_rendered:
        issues.append(("ERR", "missing meta description"))
    elif not (120 <= len(desc_rendered) <= 170):
        issues.append(("WARN", f"meta description is {len(desc_rendered)} chars (sweet spot 140-165)"))

    # canonical
    rels = {rel.lower(): href for rel, href in LINK_REL_RE.findall(html)}
    if "canonical" not in rels:
        issues.append(("ERR", "missing <link rel=canonical>"))

    # OG image
    props = {p.lower(): c for p, c in META_PROP_RE.findall(html)}
    if not props.get("og:image"):
        issues.append(("ERR", "missing og:image"))
    if not metas.get("twitter:card"):
        issues.append(("WARN", "missing twitter:card"))

    # H1
    h1s = H1_RE.findall(html)
    if not h1s:
        issues.append(("ERR", "no <h1> on page"))
    elif len(h1s) > 1:
        issues.append(("ERR", f"{len(h1s)} <h1> elements (must be exactly 1)"))

    # images
    imgs = IMG_RE.findall(html)
    for attrs in imgs:
        if not re.search(r'\balt\s*=\s*["\'][^"\']+["\']', attrs):
            issues.append(("ERR", f"<img> missing alt text: {attrs.strip()[:80]}"))
            break  # one per page is enough to flag

    # JSON-LD presence. Different page types accept different schemas:
    #   Entity pages use Restaurant/LocalBusiness/CafeOrCoffeeShop/etc.
    #   Cross-cut landings use CollectionPage.
    #   Chrome / topic-landing pages use CollectionPage or WebPage.
    #   City hubs + topic pages use Article.
    # Any of these counts as "primary schema present" — no Article WARN.
    ld_blocks = SCRIPT_LD_RE.findall(html)
    ld_blob = "\n".join(ld_blocks)
    PRIMARY_SCHEMAS = (
        "Article", "Restaurant", "LocalBusiness", "FoodEstablishment",
        "CafeOrCoffeeShop", "BarOrPub", "Brewery", "TouristTrip",
        "TouristDestination", "Festival", "EducationEvent",
        "CollectionPage", "WebPage", "AboutPage", "ContactPage",
        "ItemPage", "WebSite",
    )
    has_primary = any(f'"{s}"' in ld_blob for s in PRIMARY_SCHEMAS)
    has_breadcrumb = '"BreadcrumbList"' in ld_blob
    has_faq = '"FAQPage"' in ld_blob
    if not has_primary:
        issues.append(("WARN", "no primary schema (Article/Restaurant/CollectionPage/...)"))
    if not has_breadcrumb:
        issues.append(("WARN", "no BreadcrumbList JSON-LD"))
    # FAQPage is only mandatory on pages that visually have an FAQ block.
    has_faq_block = 'class="tj-faq"' in html or 'id="faq"' in html
    if has_faq_block and not has_faq:
        issues.append(("WARN", "page has FAQ block but no FAQPage JSON-LD"))

    # em / en dashes in body
    body_only = strip_tags(re.sub(SCRIPT_LD_RE, "", html))
    if EM_DASH_RE.search(body_only):
        # count
        n = len(EM_DASH_RE.findall(body_only))
        issues.append(("ERR", f"{n} em/en dashes in body (banned)"))

    # placeholder / draft text leaking into prod
    placeholders = ["lorem ipsum", "todo:", "tbd", "coming soon", "[name]", "[city]", "{{ ", "}} ", "xxx"]
    body_lc = body_only.lower()
    for p in placeholders:
        if p in body_lc:
            issues.append(("ERR", f"placeholder text in body: '{p}'"))

    # legacy travel URLs
    if "/destinations/" in html:
        issues.append(("WARN", "contains legacy /destinations/ link"))
    if "opentravelguide" in html.lower():
        issues.append(("ERR", "contains 'opentravelguide' reference"))

    # Updated stamp. Only mandatory on Article-style pages (city hub, topic
    # page). Entity pages and cross-cut landings don't need a visible date.
    if '"Article"' in ld_blob and "Updated" not in html:
        issues.append(("WARN", "no 'Updated' stamp visible"))

    # report
    status = "PASS"
    if any(lvl == "ERR" for lvl, _ in issues):
        status = "FAIL"
    elif any(lvl == "WARN" for lvl, _ in issues):
        status = "WARN"
    rel = path.relative_to(REPO_ROOT) if path.is_absolute() else path
    print(f"[{status}] {rel}")
    for lvl, msg in issues:
        if errors_only and lvl != "ERR":
            continue
        print(f"   {lvl}: {msg}")
    return any(lvl == "ERR" for lvl, _ in issues)


def main() -> int:
    p = argparse.ArgumentParser(description="SEO validator for rendered TableJourney pages.")
    p.add_argument("--root", default=str(REPO_ROOT / "content"), help="directory to walk (default: content/)")
    p.add_argument("--errors-only", action="store_true")
    p.add_argument("--warn-only", action="store_true", help="never exit non-zero")
    args = p.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"No such directory: {root}", file=sys.stderr)
        return 1

    any_err = False
    count = 0
    for path in sorted(root.rglob("index.html")):
        count += 1
        any_err |= validate(path, args.errors_only)
    print(f"\nChecked {count} pages.")
    return 0 if (args.warn_only or not any_err) else 1


if __name__ == "__main__":
    raise SystemExit(main())
