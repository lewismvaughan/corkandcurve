#!/usr/bin/env python3
"""Generate per-cuvée pages for every wine in every region.

Output: content/wine/<producer-slug>/<cuvee-slug>/index.html

Wines are vintage-agnostic — one page per producer cuvée. The URL is
global (not region-scoped) so the cuvée page is shareable across the
whole catalog and indexable as a single canonical entity per cuvée.

The data lives in each region's wines.json (in
site-data/<country>/<region>/data/wines.json). The producer slug must
resolve to a vineyards.json entry in the same region — that's how we
attach the cellar-visit / address sidebar to the cuvée page.

See docs/WINE_TAGS.md for the tag vocabulary, agents/wine-research/SCHEMA.md
for the wines field shape, and templates/wine.html for the rendered page.

Usage:
    python scripts/generate_wine_pages.py                    # all regions
    python scripts/generate_wine_pages.py france bordeaux    # one region
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.data_loader import (  # noqa: E402
    SITE_DATA, compute_price_tier, get_all_countries, get_all_regions,
    load_country_data, load_file,
)
from utils.template_renderer import TemplateRenderer  # noqa: E402
# Reuse the tag-derivation logic from the tag-page generator so the cuvée
# page links to the same tag set the /tag/<slug>/ pages are built from.
# Without this, derived tags (old-world, biodynamic, grape-*, etc.) would
# be orphans (no inbound link from any cuvée page).
from generate_tag_pages import _derive_tags as _derive_wine_tags  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BASE_URL = "https://corkandcurve.com"


def _build_tj_pairings(pairings: list) -> list[dict]:
    """Pre-build absolute TableJourney URLs for pairings.

    Templates render the URL through `tj_url`. We keep the original
    `dish`/`why` keys and add `tj_url` only when the data carried a
    non-null `tablejourney_ref`. Refs are paths (e.g.
    `italy/florence/restaurants/trattoria-mario`) per the schema; we
    normalise to a trailing-slash URL on tablejourney.com so the page
    template stays dumb.
    """
    out = []
    for p in pairings or []:
        if not isinstance(p, dict):
            continue
        entry = {"dish": p.get("dish") or "", "why": p.get("why") or "", "tj_url": None}
        ref = p.get("tablejourney_ref")
        if isinstance(ref, str) and ref.strip():
            ref = ref.strip().strip("/")
            if ref.startswith("http"):
                entry["tj_url"] = ref
            else:
                entry["tj_url"] = f"https://tablejourney.com/{ref}/"
        out.append(entry)
    return out


def _verified_display(wine: dict) -> tuple[str, str]:
    """Pull (display-date, source_url) from the cuvée's verified block.
    Returns ("", "") when the block is absent or incomplete."""
    v = wine.get("verified") or {}
    if not isinstance(v, dict):
        return "", ""
    return v.get("checked_on") or "", v.get("source_url") or ""


def _build_breadcrumb(country_slug: str, region_slug: str, region_name: str, country_name: str, wine_name: str) -> list[dict]:
    return [
        {"name": "Home", "url": "/"},
        {"name": country_name, "url": f"/{country_slug}/"},
        {"name": region_name, "url": f"/{country_slug}/{region_slug}/"},
        {"name": "Wines", "url": f"/{country_slug}/{region_slug}/wines/"},
        {"name": wine_name, "url": None},
    ]


def _render_for_region(renderer: TemplateRenderer, country_slug: str, region_slug: str) -> tuple[int, int]:
    """Render every cuvée page for one region. Returns (written, skipped)."""
    try:
        wines_data = load_file(country_slug, "wines.json", region_slug=region_slug)
    except FileNotFoundError:
        return 0, 0
    wines = wines_data.get("wines") or []
    if not wines:
        return 0, 0

    # Pull producer slugs once so we can attach producer context.
    try:
        vineyards_data = load_file(country_slug, "vineyards.json", region_slug=region_slug)
    except FileNotFoundError:
        vineyards_data = {"vineyards": []}
    vineyards_by_slug = {
        v["slug"]: v for v in (vineyards_data.get("vineyards") or [])
        if isinstance(v, dict) and v.get("slug")
    }

    region_data = load_file(country_slug, "region.json", region_slug=region_slug)
    destination = region_data.get("destination", {})
    region_name = destination.get("name") or region_slug.replace("-", " ").title()
    country_name = destination.get("country") or country_slug.replace("-", " ").title()
    region_url = f"/{country_slug}/{region_slug}/"
    wines_topic_url = f"{region_url}wines/"

    # Sibling cuvées: every other cuvée by the same producer in this region.
    by_producer: dict[str, list[dict]] = {}
    for w in wines:
        if isinstance(w, dict) and w.get("producer") and w.get("slug"):
            by_producer.setdefault(w["producer"], []).append(w)

    written = 0
    skipped = 0

    for w in wines:
        if not isinstance(w, dict):
            skipped += 1
            continue
        prod_slug = w.get("producer")
        cuvee_slug = w.get("slug")
        if not prod_slug or not cuvee_slug:
            skipped += 1
            continue
        producer = vineyards_by_slug.get(prod_slug)
        if producer:
            producer = dict(producer)
            producer["_url"] = f"/{country_slug}/{region_slug}/vineyards/{prod_slug}/"

        siblings = [
            {
                "name": s.get("name") or s["slug"],
                "_url": f"/wine/{prod_slug}/{s['slug']}/",
            }
            for s in by_producer.get(prod_slug, [])
            if s.get("slug") != cuvee_slug
        ]

        verified_display, verified_source_url = _verified_display(w)

        wine_url = f"/wine/{prod_slug}/{cuvee_slug}/"
        canonical = f"{BASE_URL}{wine_url}"

        # Hand-build the minimal SEO block the wine template needs. We
        # don't go through TemplateRenderer._prepare_seo because cuvée
        # pages live outside the country/region path scheme and would
        # confuse the canonical-URL builder otherwise.
        wine_seo = {
            "meta": {
                "title": f"{w.get('name')} by {w.get('producer_name')} | Cork & Curve",
                "description": (w.get("description")
                                or (w.get("taste") or {}).get("summary")
                                or f"{w.get('name')} by {w.get('producer_name')}: taste, pairings and history."),
                "canonical_url": canonical,
                "robots": "index, follow, max-image-preview:large",
                "author": "Cork & Curve Editorial",
            },
            "open_graph": {
                "og_title": f"{w.get('name')} by {w.get('producer_name')}",
                "og_description": (w.get("description")
                                   or (w.get("taste") or {}).get("summary")
                                   or ""),
                "og_image": f"{BASE_URL}/og/default.jpg",
                "og_image_width": "1200", "og_image_height": "630",
                "og_image_alt": f"{w.get('name')} by {w.get('producer_name')}",
                "og_url": canonical, "og_type": "article",
                "og_site_name": "Cork & Curve", "og_locale": "en_US",
            },
            "twitter": {
                "twitter_card": "summary_large_image",
                "twitter_title": f"{w.get('name')} by {w.get('producer_name')}",
                "twitter_description": (w.get("description")
                                        or (w.get("taste") or {}).get("summary")
                                        or ""),
                "twitter_image": f"{BASE_URL}/og/default.jpg",
                "twitter_image_alt": f"{w.get('name')} by {w.get('producer_name')}",
            },
            "article": {
                "published_time": "2026-01-01T00:00:00Z",
                "modified_time": "2026-05-22T00:00:00Z",
                "author": "Cork & Curve Editorial", "section": "Wine",
            },
            "geo": {
                "place_name": region_name,
                "latitude": "0.0", "longitude": "0.0",
                "country_code": (region_data.get("seo", {}).get("geo", {}) or {}).get("country_code", "XX"),
            },
            "structured_data": {"breadcrumb_items": []},
        }

        # Union researcher-emitted tags with derived tags (price-*,
        # drink-young / cellar-worthy, grape-*, biodynamic, old-world,
        # etc.). The cuvée page renders chips for the full set so the
        # /tag/<slug>/ pages aren't orphans.
        all_tags = sorted(set(w.get("tags") or []) | _derive_wine_tags(w, country_slug))

        # Inject visual price tier (€ to €€€€€). generate_wine_pages
        # loads via load_file, NOT load_country_data, so the price tier
        # that _inject_entity_urls would otherwise compute is absent.
        # Mutate the wine dict in place so wine.html reads `wine._price_tier`
        # the same way the wines-topic page does.
        price_tier = compute_price_tier(w.get("price_band"))
        if price_tier and "_price_tier" not in w:
            w["_price_tier"] = price_tier

        context = {
            "wine": w,
            "all_tags": all_tags,
            "producer": producer,
            "destination": destination,
            "country_slug": country_slug,
            "region_slug": region_slug,
            "region_url": region_url,
            "wines_topic_url": wines_topic_url,
            "tj_pairings": _build_tj_pairings(w.get("pairings")),
            "sibling_cuvees": siblings,
            "breadcrumb": _build_breadcrumb(country_slug, region_slug, region_name, country_name, w.get("name") or cuvee_slug),
            "verified_display": verified_display,
            "verified_source_url": verified_source_url,
            # /wine/<producer>/<cuvee>/index.html is 3 directories deep,
            # so CSS/JS asset references need three ../ steps to reach the
            # /css/ and /js/ roots. The wrong value here was the source
            # of the "no padding" report — stylesheet 404'd entirely.
            "seo": wine_seo,
            "base_path": "../../..",
            "products": [],
            "faqs": [],
            "topic": {},
            "research": {},
            "hub_page": {},
            "analytics": {
                "measurement_id": "",
                "page_type": "cuvee",
                "destination": region_slug,
                "country": country_slug,
                "region": region_slug,
                "context": f"{country_slug}:{region_slug}:wine:{prod_slug}:{cuvee_slug}",
            },
        }

        template = renderer.env.get_template("wine.html")
        html = template.render(**context)

        out_dir = CONTENT_DIR / "wine" / prod_slug / cuvee_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.html"
        out_path.write_text(html, encoding="utf-8")
        written += 1

    return written, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("country", nargs="?", help="Limit to one country slug")
    ap.add_argument("region", nargs="?", help="Limit to one region slug")
    args = ap.parse_args()

    renderer = TemplateRenderer()

    targets: list[tuple[str, str]] = []
    if args.country and args.region:
        targets.append((args.country, args.region))
    elif args.country:
        for r in get_all_regions(args.country):
            targets.append((args.country, r))
    else:
        for c in get_all_countries():
            for r in get_all_regions(c):
                targets.append((c, r))

    total_written = total_skipped = 0
    for country, region in targets:
        written, skipped = _render_for_region(renderer, country, region)
        if written or skipped:
            print(f"  [OK] {country}/{region}: wrote {written} cuvée page(s); skipped {skipped}")
        total_written += written
        total_skipped += skipped

    print(f"\nTotal cuvée pages: {total_written} written, {total_skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
