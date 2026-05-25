#!/usr/bin/env python3
"""Generate /tag/<slug>/ (global) and /tag/<slug>/<region>/ (scoped) pages.

For every cuvée in every region's wines.json, this builds:

  1. /tag/<slug>/                  one global page per tag (across regions)
  2. /tag/<slug>/<region>/         one per (tag, region) with >=2 cuvées
  3. /tag/_manifest.json           {slug,display,axis,count} per tag — read
                                   by generate_search_index.py so the global
                                   wine search surfaces tag pages

The tag vocabulary is parsed from docs/WINE_TAGS.md (single source of
truth). Researcher-emitted tags are picked up verbatim from
wines[*].tags. Derived axes (price / ageing / production / grape / world
/ sweetness) are computed here from the cuvée's other fields so the
researcher prompt doesn't have to remember them and the result stays
consistent across the catalog.

See docs/WINE_TAGS.md for the full axis-by-axis vocabulary and the
derivation formulas this file implements.

Usage:
    python scripts/generate_tag_pages.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.data_loader import (  # noqa: E402
    SITE_DATA, compute_price_tier, get_all_countries, get_all_regions, load_file,
)
from utils.slug import slugify  # noqa: E402
from utils.template_renderer import TemplateRenderer  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BASE_URL = "https://corkandcurve.com"
WINE_TAGS_DOC = REPO_ROOT / "docs" / "WINE_TAGS.md"

# Old World countries (from docs/WINE_TAGS.md world axis). Country slugs
# are matched against this set; everything else is New World.
OLD_WORLD_COUNTRIES = {
    "france", "italy", "spain", "portugal", "germany", "austria",
    "greece", "hungary", "switzerland",
}

# Per-axis section headers used on the tag page. Keys are tag prefixes
# or exact slugs; the lookup tries longest-prefix-first.
AXIS_LABELS = {
    "style": "Style",
    "body": "Body",
    "tannin": "Tannin",
    "acidity": "Acidity",
    "sweetness": "Sweetness",
    "pairing": "Pairing",
    "occasion": "Occasion",
    "mood": "Mood",
    "price": "Price band",
    "ageing": "Ageing",
    "production": "Production",
    "grape": "Grape",
    "world": "World",
    "editorial": "Editorial",
}

# Hardcoded axis lookups for tags whose axis isn't obvious from the slug.
# Researcher-emitted tags from docs/WINE_TAGS.md mostly use prefixed slugs
# (pairs-with-*, occasion-*, mood-*, price-*) so the prefix lookup wins.
# This table covers the bare-slug cases.
TAG_TO_AXIS_OVERRIDES = {
    "still-red": "style", "still-white": "style", "still-rose": "style",
    "sparkling-traditional": "style", "sparkling-tank": "style", "sparkling-ancestral": "style",
    "orange": "style",
    "dessert-late-harvest": "style", "dessert-noble-rot": "style",
    "dessert-ice-wine": "style", "dessert-passito": "style",
    "fortified-port": "style", "fortified-sherry": "style", "fortified-madeira": "style",
    "fortified-marsala": "style", "fortified-vdn": "style",
    "vermouth": "style",
    "light-body": "body", "medium-body": "body", "full-body": "body",
    "low-tannin": "tannin", "medium-tannin": "tannin", "firm-tannin": "tannin", "high-tannin": "tannin",
    "low-acid": "acidity", "medium-acid": "acidity", "high-acid": "acidity", "racy-acid": "acidity",
    "dry": "sweetness", "off-dry": "sweetness", "medium-sweet": "sweetness",
    "sweet": "sweetness", "dessert": "sweetness",
    "drink-young": "ageing", "medium-term": "ageing", "cellar-worthy": "ageing",
    "biodynamic": "production", "biodynamic-certified": "production",
    "organic": "production", "natural": "production", "vegan": "production",
    "low-sulfite": "production",
    "old-world": "world", "new-world": "world",
    "iconic": "editorial", "hidden-gem": "editorial", "value-pick": "editorial",
    "super-tuscan": "editorial", "first-growth": "editorial", "grand-cru": "editorial",
    "cult-wine": "editorial", "garagiste": "editorial", "single-vineyard": "editorial",
    "old-vines": "editorial", "field-blend": "editorial", "library-release": "editorial",
}

PRICE_BREAKS = (
    (15, "price-everyday"),
    (30, "price-trade-up"),
    (75, "price-premium"),
    (200, "price-fine"),
    (500, "price-luxury"),
    (float("inf"), "price-collector"),
)

_PRICE_NUM_RE = re.compile(r"\d+(?:[\.,]\d+)?")


def _lower_price(price_band: str) -> float | None:
    """Pull the lower numeric bound out of a free-form price_band string.

    "€90-130 at retail" -> 90.0
    "$45"              -> 45.0
    "Around €1200"     -> 1200.0
    "Not for sale"     -> None
    """
    if not isinstance(price_band, str):
        return None
    nums = _PRICE_NUM_RE.findall(price_band.replace(",", ""))
    if not nums:
        return None
    try:
        return float(nums[0])
    except (ValueError, TypeError):
        return None


def _ageing_tag(drinking_window: str) -> str | None:
    """Derive ageing tag from a drinking_window_years string.

    "3-10 from vintage" -> "medium-term"  (upper=10)
    "10-25 from vintage" -> "cellar-worthy" (upper=25)
    "2-4 from vintage" -> "drink-young"   (upper=4)
    """
    if not isinstance(drinking_window, str):
        return None
    nums = _PRICE_NUM_RE.findall(drinking_window)
    if not nums:
        return None
    try:
        upper = float(nums[-1])
    except (ValueError, TypeError):
        return None
    if upper <= 5:
        return "drink-young"
    if upper <= 15:
        return "medium-term"
    return "cellar-worthy"


_GRAPE_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _grape_slug(name: str) -> str:
    """Convert "Cabernet Sauvignon" -> "cabernet-sauvignon"."""
    s = name.strip().lower()
    s = _GRAPE_SLUG_RE.sub("-", s).strip("-")
    return s


def _derive_tags(wine: dict, country_slug: str) -> set[str]:
    """Compute the DERIVED tags for a cuvée. Researcher does not emit these.

    Mirrors docs/WINE_TAGS.md derived axes:
      - sweetness (from wine.sweetness)
      - price-* (from wine.price_band lower bound)
      - drink-young / medium-term / cellar-worthy (from drinking_window_years)
      - biodynamic[-certified] / organic / natural / vegan / low-sulfite
        (from cuvée + producer flags)
      - grape-<slug> for each entry in varietals
      - old-world / new-world (from country)
    """
    out: set[str] = set()

    sw = wine.get("sweetness")
    if sw:
        out.add(sw)

    price = _lower_price(wine.get("price_band"))
    if price is not None:
        for ceiling, slug in PRICE_BREAKS:
            if price < ceiling:
                out.add(slug)
                break

    age_tag = _ageing_tag(wine.get("drinking_window_years"))
    if age_tag:
        out.add(age_tag)

    bs = wine.get("biodynamic_status")
    if bs and bs != "none":
        out.add("biodynamic")
        if bs == "demeter_certified":
            out.add("biodynamic-certified")
    os_ = wine.get("organic_status")
    if os_ and os_ != "none":
        out.add("organic")
    if wine.get("vegan") is True:
        out.add("vegan")
    if wine.get("low_sulfite") is True or wine.get("natural") is True:
        # Producer may flag natural at cuvée level; the vineyards-level
        # natural_wine field is handled at the producer cross-walk.
        out.add("natural" if wine.get("natural") else "low-sulfite")

    for v in wine.get("varietals") or []:
        if isinstance(v, dict) and v.get("grape"):
            out.add(_grape_slug(v["grape"]))

    out.add("old-world" if country_slug in OLD_WORLD_COUNTRIES else "new-world")

    return out


def _axis_for(tag: str) -> str:
    """Resolve a tag slug to its axis. Tries override table first, then
    prefix match. Unknown tags fall back to 'editorial' so a typo doesn't
    crash the build — the validator catches typos separately."""
    if tag in TAG_TO_AXIS_OVERRIDES:
        return TAG_TO_AXIS_OVERRIDES[tag]
    for prefix in ("pairs-with-", "occasion-", "mood-", "price-",
                   "fortified-", "sparkling-", "dessert-"):
        if tag.startswith(prefix):
            if prefix == "pairs-with-":
                return "pairing"
            if prefix == "occasion-":
                return "occasion"
            if prefix == "mood-":
                return "mood"
            if prefix == "price-":
                return "price"
            return "style"
    # Bare grape slugs fall here.
    return "grape"


def _load_tag_display_map() -> dict[str, str]:
    """Parse docs/WINE_TAGS.md for slug -> display label."""
    out: dict[str, str] = {}
    if not WINE_TAGS_DOC.exists():
        return out
    text = WINE_TAGS_DOC.read_text(encoding="utf-8")
    row_re = re.compile(
        r"^\|\s*`([a-z0-9-]+)`\s*\|\s*([^|]+?)\s*\|", re.MULTILINE
    )
    for slug, display in row_re.findall(text):
        out[slug] = display.strip()
    return out


def _collect_wines() -> list[dict]:
    """Walk every region's wines.json into a flat list.

    Each entry carries the fields the tag template needs PLUS the full
    tag set (researcher-emitted ∪ derived).
    """
    flat: list[dict] = []
    # Walk SITE_DATA directly rather than use get_all_countries(): the
    # latter requires a country-level region.json, but most C&C regions
    # are region-only (no country hub). Mirror the discovery logic used
    # in generate_search_index.py's all_countries_with_any_data().
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        for region in get_all_regions(country):
            try:
                wines_data = load_file(country, "wines.json", region_slug=region)
            except FileNotFoundError:
                continue
            try:
                region_data = load_file(country, "region.json", region_slug=region)
            except FileNotFoundError:
                continue
            dest = region_data.get("destination") or {}
            region_name = dest.get("name") or region.replace("-", " ").title()
            country_name = dest.get("country") or country.replace("-", " ").title()

            for w in wines_data.get("wines") or []:
                if not isinstance(w, dict) or not w.get("slug") or not w.get("producer"):
                    continue
                researcher_tags = set(w.get("tags") or [])
                derived = _derive_tags(w, country)
                all_tags = researcher_tags | derived
                taste = w.get("taste") or {}
                # Pull the top 2 mood-* tags from the researcher-emitted set
                # so the tag-page card can render a compact descriptor line
                # (matches wine.html hero + wines-topic.html card format).
                mood_descriptors = [
                    t[5:].replace("-", " ").title()
                    for t in (w.get("tags") or [])
                    if isinstance(t, str) and t.startswith("mood-")
                ][:2]
                price_tier = compute_price_tier(w.get("price_band"))
                flat.append({
                    "slug": w["slug"],
                    "name": w.get("name") or w["slug"],
                    "producer": w["producer"],
                    "producer_name": w.get("producer_name") or w["producer"],
                    "country_slug": country,
                    "country_name": country_name,
                    "region_slug": region,
                    "region_name": region_name,
                    "style": w.get("style") or "",
                    "price_band": w.get("price_band") or "",
                    "price_tier": price_tier,
                    "taste_summary": taste.get("summary") or "",
                    "editorial_score": w.get("editorial_score"),
                    "sweetness": w.get("sweetness") or "",
                    "taste_body": taste.get("body") or "",
                    "taste_tannin": taste.get("tannin") or "",
                    "taste_acidity": taste.get("acidity") or "",
                    "mood_descriptors": mood_descriptors,
                    "url": f"/wine/{w['producer']}/{w['slug']}/",
                    "tags": all_tags,
                })
    return flat


def _render_tag_page(
    renderer: TemplateRenderer,
    tag_slug: str,
    tag_display: str,
    tag_axis: str,
    wines: list[dict],
    scope: str,
    scope_region: dict | None,
    related_tags: list[dict],
    scope_regions_with_tag: list[dict] | None,
    out_path: Path,
) -> None:
    """Render one /tag/<slug>/[<region>/]index.html."""
    if scope == "region" and scope_region:
        url_path = f"/tag/{tag_slug}/{scope_region['region']}/"
        title = f"{tag_display} wines in {scope_region['region_name']} | Cork & Curve"
        description = (
            f"Cuvées tagged {tag_display.lower()} in "
            f"{scope_region['region_name']}, {scope_region['country_name']}, "
            f"on Cork & Curve."
        )
        breadcrumb = [
            {"name": "Home", "url": "/"},
            {"name": tag_display, "url": f"/tag/{tag_slug}/"},
            {"name": scope_region["region_name"], "url": None},
        ]
    else:
        url_path = f"/tag/{tag_slug}/"
        title = f"{tag_display} wines | Cork & Curve"
        description = (
            f"Every cuvée we cover tagged {tag_display.lower()}, "
            f"across {len(set((w['region_slug'], w['country_slug']) for w in wines))} "
            f"regions on Cork & Curve."
        )
        breadcrumb = [
            {"name": "Home", "url": "/"},
            {"name": "Tags", "url": "/tags/"},
            {"name": tag_display, "url": None},
        ]
    canonical = f"{BASE_URL}{url_path}"

    tag_seo = {
        "meta": {
            "title": title,
            "description": description,
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large",
            "author": "Cork & Curve Editorial",
        },
        "open_graph": {
            "og_title": title, "og_description": description,
            "og_image": f"{BASE_URL}/og/default.jpg",
            "og_image_width": "1200", "og_image_height": "630",
            "og_image_alt": title,
            "og_url": canonical, "og_type": "website",
            "og_site_name": "Cork & Curve", "og_locale": "en_US",
        },
        "twitter": {
            "twitter_card": "summary_large_image",
            "twitter_title": title, "twitter_description": description,
            "twitter_image": f"{BASE_URL}/og/default.jpg",
            "twitter_image_alt": title,
        },
        "article": {
            "published_time": "2026-01-01T00:00:00Z",
            "modified_time": "2026-05-22T00:00:00Z",
            "author": "Cork & Curve Editorial", "section": "Wine",
        },
        "geo": {"place_name": "Global", "latitude": "0.0", "longitude": "0.0", "country_code": "XX"},
        "structured_data": {"breadcrumb_items": []},
    }

    context = {
        "tag_slug": tag_slug,
        "tag_display": tag_display,
        "tag_axis": tag_axis,
        "tag_axis_label": AXIS_LABELS.get(tag_axis, tag_axis.title()),
        "scope": scope,
        "scope_region": scope_region,
        "scope_regions_with_tag": scope_regions_with_tag or [],
        "wines": wines,
        "related_tags": related_tags,
        "breadcrumb": breadcrumb,
        "canonical_url": canonical,
        "destination": {"name": "Cork & Curve"},
        "seo": tag_seo,
        # /tag/<slug>/index.html sits 2 levels below content/ so needs
        # ../../ to reach /css/ and /js/. /tag/<slug>/<region>/index.html
        # is 3 levels deep so needs ../../../. Off-by-one here was the
        # source of the "no padding" report on cuvée + tag pages.
        "base_path": "../../.." if scope == "region" else "../..",
        "products": [],
        "faqs": [],
        "topic": {},
        "research": {},
        "hub_page": {},
        "country_slug": "",
        "region_slug": "",
        "analytics": {
            "measurement_id": "",
            "page_type": "tag",
            "destination": scope_region["region"] if scope == "region" and scope_region else "global",
            "country": "",
            "region": scope_region["region"] if scope == "region" and scope_region else "",
            "context": f"tag:{tag_slug}" + (f":{scope_region['region']}" if scope == "region" and scope_region else ""),
        },
    }
    template = renderer.env.get_template("tag.html")
    html = template.render(**context)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--region-threshold", type=int, default=2,
                    help="Minimum cuvées for a /tag/<slug>/<region>/ page to render (default 2)")
    args = ap.parse_args()

    renderer = TemplateRenderer()
    flat = _collect_wines()
    if not flat:
        print("No wines found in any region. /tag/ pages skipped.")
        return 0

    display_map = _load_tag_display_map()

    # Bucket cuvées by tag and by (tag, region).
    by_tag: dict[str, list[dict]] = defaultdict(list)
    by_tag_region: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for w in flat:
        for t in w["tags"]:
            by_tag[t].append(w)
            by_tag_region[(t, w["country_slug"], w["region_slug"])].append(w)

    # Build axis index for "related tags" sidebar.
    by_axis: dict[str, list[str]] = defaultdict(list)
    for t in by_tag:
        by_axis[_axis_for(t)].append(t)

    manifest: list[dict] = []
    global_pages = 0
    region_pages = 0

    for tag_slug, wines in sorted(by_tag.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        # Stable ordering inside the page: by region then name.
        wines = sorted(wines, key=lambda w: (w["region_name"], w["name"]))
        axis = _axis_for(tag_slug)
        display = display_map.get(tag_slug) or tag_slug.replace("-", " ").title()

        # Related tags: top 8 other tags in the same axis by cuvée count.
        related = []
        for sibling in sorted(by_axis.get(axis, []), key=lambda s: -len(by_tag[s])):
            if sibling == tag_slug:
                continue
            related.append({
                "slug": sibling,
                "display": display_map.get(sibling) or sibling.replace("-", " ").title(),
                "count": len(by_tag[sibling]),
            })
            if len(related) >= 8:
                break

        # Per-region breakdown for the global page sidebar.
        regions_with_tag = sorted(
            ({
                "country_slug": c, "region_slug": r,
                "region_name": next(w["region_name"] for w in wines if w["country_slug"] == c and w["region_slug"] == r),
                "count": len([w for w in wines if w["country_slug"] == c and w["region_slug"] == r]),
            } for c, r in {(w["country_slug"], w["region_slug"]) for w in wines}),
            key=lambda r: -r["count"],
        )

        # 1) Global page.
        out_global = CONTENT_DIR / "tag" / tag_slug / "index.html"
        _render_tag_page(
            renderer,
            tag_slug=tag_slug, tag_display=display, tag_axis=axis,
            wines=wines, scope="global", scope_region=None,
            related_tags=related,
            # Only link regions that will actually get a scoped page below
            # (count >= threshold); else the global page 404s on single-cuvée
            # regions whose scoped page is never written.
            scope_regions_with_tag=[r for r in regions_with_tag if r["count"] >= args.region_threshold],
            out_path=out_global,
        )
        global_pages += 1

        # 2) Region-scoped pages (>= threshold).
        for r in regions_with_tag:
            if r["count"] < args.region_threshold:
                continue
            scope_wines = [w for w in wines if w["region_slug"] == r["region_slug"] and w["country_slug"] == r["country_slug"]]
            out_region = CONTENT_DIR / "tag" / tag_slug / r["region_slug"] / "index.html"
            _render_tag_page(
                renderer,
                tag_slug=tag_slug, tag_display=display, tag_axis=axis,
                wines=scope_wines, scope="region",
                scope_region={
                    "country": r["country_slug"], "region": r["region_slug"],
                    "country_name": next(w["country_name"] for w in scope_wines),
                    "region_name": r["region_name"],
                    "url": f"/{r['country_slug']}/{r['region_slug']}/",
                },
                related_tags=related,
                scope_regions_with_tag=None,
                out_path=out_region,
            )
            region_pages += 1

        manifest.append({
            "slug": tag_slug,
            "display": display,
            "axis": axis,
            "count": len(wines),
            "regions": [{"country_slug": r["country_slug"], "region_slug": r["region_slug"], "count": r["count"]} for r in regions_with_tag],
        })

    # Manifest: read by generate_search_index.py + generate_sitemap.py so
    # the tag pages get inbound links from search + sitemap.
    manifest_path = CONTENT_DIR / "tag" / "_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"entries": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {global_pages} global tag page(s) and {region_pages} region-scoped tag page(s)")
    print(f"  Manifest: {manifest_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
