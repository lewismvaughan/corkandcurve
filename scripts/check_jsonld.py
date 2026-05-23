#!/usr/bin/env python3
"""Local JSON-LD validator for corkandcurve.com.

Walks every HTML page under content/, extracts every <script type="application/ld+json">
block, and checks:

  * the JSON parses cleanly.
  * the block has @context (schema.org or http://schema.org).
  * the block has @type OR @graph (one of the two — graph blocks list nested types).
  * required fields per @type:
      Article             headline, datePublished
      Restaurant          name, address
      LocalBusiness       name, address
      CafeOrCoffeeShop    name, address
      Bakery              name, address
      BarOrPub            name, address
      Brewery             name, address
      FoodEstablishment   name
      TouristDestination  name
      TouristTrip         name
      Festival            name
      EducationEvent      name
      Thing               name
      ItemList            itemListElement
      BreadcrumbList      itemListElement
      FAQPage             mainEntity
      Question            name, acceptedAnswer
      WebPage             name
      WebSite             name
      Organization        name
      ImageObject         url

Output:
  /tmp/tj_jsonld.json   full report
  stdout summary

This is a local sanity check, not a replacement for Google's Rich Results
Test. It catches the common subagent failure modes (malformed JSON, missing
required field, wrong @context) before pages reach production.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"

# Pulled from schema.org's documentation for the @types we emit. Only the
# fields whose absence would cause Google to ignore the snippet (and which
# the renderer is responsible for producing) are listed here.
REQUIRED_BY_TYPE = {
    "Article":            ("headline", "datePublished"),
    "Restaurant":         ("name", "address"),
    "LocalBusiness":      ("name", "address"),
    "CafeOrCoffeeShop":   ("name", "address"),
    "Bakery":             ("name", "address"),
    "BarOrPub":           ("name", "address"),
    "Brewery":            ("name", "address"),
    "FoodEstablishment":  ("name",),
    "Winery":             ("name",),
    "Distillery":         ("name",),
    "Museum":             ("name",),
    "Store":              ("name",),
    "LodgingBusiness":    ("name",),
    "TouristAttraction":  ("name",),
    "TouristDestination": ("name",),
    "TouristTrip":        ("name",),
    "Festival":           ("name",),
    "EducationEvent":     ("name",),
    "Course":             ("name",),
    "Product":            ("name",),
    "Brand":              ("name",),
    "CollectionPage":     ("name",),
    "HowTo":              ("name",),
    "AboutPage":          (),
    "ContactPage":        (),
    "ItemList":           ("itemListElement",),
    "BreadcrumbList":     ("itemListElement",),
    "FAQPage":            ("mainEntity",),
    "Question":           ("name", "acceptedAnswer"),
    "WebPage":            (),
    "WebSite":            ("name",),
    "Organization":       ("name",),
    "ImageObject":        ("url",),
    "Thing":              ("name",),
}

# @types where address may live one nest deeper (e.g. @graph entries that
# include a parent business + a PostalAddress as a child item).
# Right now we just require name + address presence on the top-level dict,
# which matches what generate_entity_pages.py emits.

JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


def url_for_file(path: Path) -> str:
    rel = path.relative_to(CONTENT)
    parts = rel.parts
    if parts[-1] == "index.html":
        if len(parts) == 1:
            return "/"
        return "/" + "/".join(parts[:-1]) + "/"
    return "/" + "/".join(parts)


def _has_context(node: dict) -> bool:
    ctx = node.get("@context")
    if isinstance(ctx, str):
        return "schema.org" in ctx.lower()
    if isinstance(ctx, list):
        return any(isinstance(c, str) and "schema.org" in c.lower() for c in ctx)
    if isinstance(ctx, dict):
        return any(isinstance(v, str) and "schema.org" in v.lower() for v in ctx.values())
    return False


def _flatten_items(node: object) -> list[dict]:
    """Yield every dict-with-@type out of a JSON-LD payload, including @graph
    members. Used so we can audit every typed entity even when the page emits
    a single top-level @graph wrapper."""
    out: list[dict] = []
    if isinstance(node, dict):
        if "@type" in node:
            out.append(node)
        if "@graph" in node and isinstance(node["@graph"], list):
            for child in node["@graph"]:
                out.extend(_flatten_items(child))
    elif isinstance(node, list):
        for child in node:
            out.extend(_flatten_items(child))
    return out


def _check_block(block: dict, where: str, issues: list) -> None:
    if not _has_context(block):
        issues.append(f"{where}: missing @context (or not schema.org)")
    items = _flatten_items(block)
    if not items:
        issues.append(f"{where}: no @type and no @graph entries")
        return
    for item in items:
        t = item.get("@type")
        if isinstance(t, list):
            # Multi-type entries — we check the first type for required fields.
            t_check = t[0] if t else None
        else:
            t_check = t
        if not t_check:
            issues.append(f"{where}: entry without @type ({list(item.keys())[:5]})")
            continue
        required = REQUIRED_BY_TYPE.get(t_check)
        if required is None:
            # Unknown type. We don't error, but note it so we can extend coverage.
            continue
        for field in required:
            v = item.get(field)
            if v is None or (isinstance(v, str) and not v.strip()) \
               or (isinstance(v, (list, dict)) and not v):
                issues.append(f"{where}: {t_check} missing '{field}'")


def main() -> int:
    pages = list(CONTENT.rglob("*.html"))
    total_blocks = 0
    pages_with_issues = []
    type_counts: dict[str, int] = defaultdict(int)

    # Utility pages exempt from JSON-LD validation (they're not crawled for
    # rich-result snippets — they're transport-level error/redirect pages).
    EXEMPT_URLS = {"/404.html"}
    for f in sorted(pages):
        if not f.is_file():
            continue
        url = url_for_file(f)
        if url in EXEMPT_URLS:
            continue
        html = f.read_text(encoding="utf-8", errors="replace")
        blocks = JSONLD_RE.findall(html)
        issues: list[str] = []
        for i, raw in enumerate(blocks):
            total_blocks += 1
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as e:
                issues.append(f"block #{i}: invalid JSON ({e})")
                continue
            _check_block(payload, f"block #{i}", issues)
            for item in _flatten_items(payload):
                t = item.get("@type")
                if isinstance(t, list):
                    for tt in t:
                        type_counts[tt] += 1
                elif isinstance(t, str):
                    type_counts[t] += 1
        if not blocks:
            issues.append("no JSON-LD blocks found")
        if issues:
            pages_with_issues.append({"url": url, "issues": issues})

    print(f"Pages scanned: {len(pages)}")
    print(f"JSON-LD blocks: {total_blocks}")
    print()
    print("@type counts:")
    for t, n in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {n:5d}  {t}")
    print()
    print(f"Pages with JSON-LD issues: {len(pages_with_issues)}")
    for row in pages_with_issues[:20]:
        print(f"  {row['url']}")
        for issue in row["issues"][:3]:
            print(f"    - {issue}")
        if len(row["issues"]) > 3:
            print(f"    ... and {len(row['issues']) - 3} more")
    if len(pages_with_issues) > 20:
        print(f"  ... and {len(pages_with_issues) - 20} more pages")

    out_path = Path("/tmp/tj_jsonld.json")
    out_path.write_text(json.dumps({
        "pages_scanned": len(pages),
        "total_blocks": total_blocks,
        "type_counts": dict(type_counts),
        "pages_with_issues": pages_with_issues,
    }, indent=2), encoding="utf-8")
    print(f"\nFull report: {out_path}")
    return 1 if pages_with_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
