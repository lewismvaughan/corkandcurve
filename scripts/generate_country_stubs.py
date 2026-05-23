#!/usr/bin/env python3
"""Emit a minimal /<country>/index.html for any country that has city
content + rollup pages but no data/region.json at country scope.

Without this stub, every /<country>/<topic|cuisine|dish|dietary|nightlife>/
page beneath becomes an orphan (no inbound editorial link from a parent).

Germany is the canonical case: berlin + munich shipped, country rollups
exist, but no data/germany/region.json → generate_region_page.py errors.

The stub is minimal — chrome, an H1, a sentence, and links to:
  - every city in the country
  - every country × topic/cuisine/dish/dietary/nightlife-sub rollup
    that the generators have emitted

Runs AFTER all rollup generators and AFTER generate_region_page.py so
it only fills the gap left behind.

Usage:
    python scripts/generate_country_stubs.py
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import json  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
        "czech-republic": "Czech Republic",
    }.get(slug, slug.replace("-", " ").title())


def _region_card_html(country_slug: str, region_slug: str, region_name: str,
                      hero_image: str | None, tagline: str | None) -> str:
    """Render one region as a tj-city-card (same component the homepage
    uses) so the country page visually matches the rest of the site."""
    img_html = (
        f'<img class="tj-city-card-img" src="{html.escape(hero_image)}" '
        f'alt="{html.escape(region_name)} wine country" loading="lazy" '
        f'decoding="async" width="600" height="450">'
        if hero_image
        else f'<div class="tj-city-card-img tj-city-card-ph" aria-hidden="true">'
             f'<span>{html.escape(region_name[:1])}</span></div>'
    )
    tag_html = (
        f'<p class="tj-city-card-tagline">{html.escape(tagline)}</p>'
        if tagline else ""
    )
    return (
        f'<a href="/{country_slug}/{region_slug}/" class="tj-city-card" '
        f'title="{html.escape(region_name)} wine guide">'
        f'{img_html}'
        f'<div class="tj-city-card-body">'
        f'<h3 class="tj-city-card-name">{html.escape(region_name)}</h3>'
        f'{tag_html}'
        f'</div></a>'
    )


def _country_destination(country_slug: str) -> dict:
    """Return country-level destination dict from site-data/<country>/data/region.json
    if present, otherwise {}. The hero_image + tagline + overview are
    consumed by _stub_html so /<country>/ renders the same hero treatment
    region pages get. Without country-level data the page falls back to
    title-only hero (visually flat — encourage creating the file)."""
    p = REPO_ROOT / "site-data" / country_slug / "data" / "region.json"
    if not p.exists():
        return {}
    try:
        return (json.loads(p.read_text(encoding="utf-8")).get("destination") or {})
    except (OSError, json.JSONDecodeError):
        return {}


def _stub_html(country_slug: str, country_name: str,
               regions: list[dict],
               rollups: list[tuple[str, str]]) -> str:
    """Render a country stub page via the chrome/page.html template chain
    so the result inherits the proper site nav, footer, theme and SEO
    plumbing. The body_html is a card grid of regions plus an optional
    rollups list — same visual language as the homepage's region marquee.
    """
    from utils.template_renderer import TemplateRenderer  # local import
    canonical = f"{BASE}/{country_slug}/"
    title = f"{country_name} wine regions | Cork & Curve"
    desc = (
        f"Wine regions across {country_name} on Cork & Curve. "
        f"Vineyards, tasting rooms, signature wines and food-pairing guides, "
        f"written by editors who taste in person."
    )
    # Pull country-level metadata (hero_image, tagline, overview) from
    # site-data/<country>/data/region.json if it exists. Without it, the
    # hero falls back to title-only.
    country_dest = _country_destination(country_slug)
    hero_image = country_dest.get("hero_image") or None
    hero_image_alt = country_dest.get("hero_image_alt") or f"{country_name} wine country"
    hero_image_credit = country_dest.get("hero_image_credit") or None
    overview = country_dest.get("overview") or None
    tagline = country_dest.get("tagline") or "Wine regions on Cork & Curve"

    body_parts: list[str] = []
    if hero_image:
        # Render as a wide hero image immediately under the H1. Matches the
        # /<country>/<region>/ region-hub treatment.
        credit_html = (
            f'<p class="tj-country-hero-credit" style="font-size:0.75rem;color:var(--tj-muted, #6b6b6b);text-align:right;margin:6px 0 0;">'
            f'{html.escape(hero_image_credit)}</p>'
            if hero_image_credit else ""
        )
        body_parts.append(
            f'<figure class="tj-country-hero" style="margin:0 0 28px;">'
            f'<img src="{html.escape(hero_image)}" alt="{html.escape(hero_image_alt)}" '
            f'loading="eager" fetchpriority="high" decoding="async" '
            f'style="width:100%;height:auto;max-height:480px;object-fit:cover;border-radius:var(--tj-radius, 8px);display:block;">'
            f'{credit_html}'
            f'</figure>'
        )
    if overview:
        body_parts.append(
            f'<p class="tj-intro">{html.escape(overview)}</p>'
        )
    else:
        body_parts.append(
            f'<p class="tj-intro">Wine regions across {html.escape(country_name)} '
            f'on Cork & Curve. Pick a region to dive into vineyards, tasting '
            f'rooms, cuvées and food pairings.</p>'
        )
    if regions:
        cards = "".join(
            _region_card_html(country_slug, r["slug"], r["name"], r.get("image"), r.get("tagline"))
            for r in regions
        )
        body_parts.append(
            f'<section class="tj-section" id="regions">'
            f'<h2>Regions</h2>'
            f'<div class="tj-card-grid">{cards}</div>'
            f'</section>'
        )
    if rollups:
        rollups_html = "".join(
            f'<li><a href="{href}">{html.escape(label)}</a></li>'
            for href, label in rollups
        )
        body_parts.append(
            f'<section class="tj-section" id="rollups">'
            f'<h2>Top across {html.escape(country_name)}</h2>'
            f'<ul class="tj-grid-list">{rollups_html}</ul>'
            f'</section>'
        )

    page = {
        "title": title,
        "meta_description": desc,
        "canonical_url": canonical,
        "h1": country_name,
        "subtitle": tagline,
        "page_type": "collection",
        "updated": "May 2026",
        "body_html": "".join(body_parts),
        "breadcrumb_items": [
            {"position": 1, "name": "Home", "url": BASE + "/"},
            {"position": 2, "name": country_name, "url": None},
        ],
    }

    renderer = TemplateRenderer()
    template = renderer.env.get_template("chrome/page.html")
    # chrome/page.html extends base.html which expects a context shape with
    # seo / destination / topic / analytics / base_path defaults; pass the
    # bare minimum needed so the nav/footer/JSON-LD render correctly.
    return template.render(
        page=page,
        seo={
            "meta": {
                "title": title, "description": desc, "canonical_url": canonical,
                "robots": "index, follow, max-image-preview:large",
                "author": "Cork & Curve Editorial",
            },
            "open_graph": {
                "og_title": title, "og_description": desc, "og_url": canonical,
                "og_type": "website",
                "og_image": f"{BASE}/og/default.jpg",
                "og_image_alt": f"{country_name} wine regions",
            },
            "twitter": {
                "twitter_card": "summary_large_image",
                "twitter_title": title, "twitter_description": desc,
                "twitter_image": f"{BASE}/og/default.jpg",
                "twitter_image_alt": f"{country_name} wine regions",
            },
            "article": {},
            "geo": {"place_name": country_name, "latitude": "0.0", "longitude": "0.0", "country_code": "XX"},
            "structured_data": {"breadcrumb_items": page["breadcrumb_items"]},
        },
        destination={"name": country_name},
        topic={},
        country_slug=country_slug,
        region_slug=None,
        analytics={"page_type": "country_stub", "destination": country_slug, "country": country_slug, "region": "", "context": f"country_stub:{country_slug}"},
        breadcrumb=[
            {"name": "Home", "url": "/"},
            {"name": country_name, "url": None},
        ],
        base_path="..",
        products=[],
        faqs=[],
        research={},
        hub_page={},
    )


def _collect_regions(country_dir: Path, country_slug: str) -> list[dict]:
    """Return [{slug, name, image, tagline}] for every region with a
    rendered index.html under content/<country>/<region>/. The display
    name + hero_image + tagline come from the matching
    site-data/<country>/<region>/data/region.json so the country stub
    visually matches the region hub it links to."""
    out: list[dict] = []
    site_data_dir = REPO_ROOT / "site-data" / country_slug
    # Skip rollup / topic dirs that aren't regions.
    topic_slugs = {
        "cuisine", "dish", "dietary", "nightlife", "cuisines",
        "signature-dishes", "neighborhoods",
        "restaurants", "fine-dining", "casual-dining", "bakeries", "cafes",
        "coffee-roasters", "bars", "wine-bars", "breweries", "street-food",
        "markets", "late-night", "hidden-gems", "budget-eating", "brunch",
        "food-tours", "cooking-classes", "day-trips-food",
        "vineyards", "tasting-rooms", "wine-restaurants", "wine-retailers",
        "wine-schools", "wine-tours", "wine-festivals", "distilleries",
        "wine-museums", "wine-hotels", "wine-experiences", "wine-history",
        "seasonal-wine", "signature-wines", "signature-grapes", "budget-wines",
        "day-trips-wine", "itineraries", "food-pairing", "wines",
    }
    for child in sorted(country_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in topic_slugs:
            continue
        idx = child / "index.html"
        if not idx.exists():
            continue
        region_slug = child.name
        # Pull rich metadata from region.json if available.
        rj = site_data_dir / region_slug / "data" / "region.json"
        name = region_slug.replace("-", " ").title()
        image = None
        tagline = None
        if rj.exists():
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
                dest = rdata.get("destination") or {}
                name = dest.get("name") or name
                image = dest.get("hero_image") or None
                tagline = dest.get("tagline") or None
            except (OSError, json.JSONDecodeError):
                pass
        out.append({
            "slug": region_slug, "name": name,
            "image": image, "tagline": tagline,
        })
    return out


def _collect_rollups(country_dir: Path, country_slug: str) -> list[tuple[str, str]]:
    """Return [(href, label)] for every country-level rollup page that exists."""
    out: list[tuple[str, str]] = []

    topic_labels = {
        "restaurants": "Restaurants",
        "fine-dining": "Fine Dining",
        "casual-dining": "Casual Dining",
        "bakeries": "Bakeries",
        "cafes": "Cafes",
        "coffee-roasters": "Coffee Roasters",
        "bars": "Bars",
        "wine-bars": "Wine Bars",
        "breweries": "Breweries",
        "street-food": "Street Food",
        "markets": "Markets",
        "late-night": "Late Night",
        "hidden-gems": "Hidden Gems",
        "budget-eating": "Budget Eating",
        "brunch": "Brunch",
        "food-tours": "Food Tours",
        "cooking-classes": "Cooking Classes",
        "day-trips-food": "Day Trips",
        "nightlife": "Nightlife",
    }
    for slug, label in topic_labels.items():
        if (country_dir / slug / "index.html").exists():
            out.append((f"/{country_slug}/{slug}/", label))

    for parent_slug, parent_label in (("cuisine", "cuisines"), ("dish", "dishes"),
                                       ("dietary", "dietary"), ("nightlife", "nightlife")):
        d = country_dir / parent_slug
        if not d.is_dir():
            continue
        for sub in sorted(d.iterdir()):
            if not sub.is_dir():
                continue
            if (sub / "index.html").exists():
                label = f'{parent_label.title()}: {sub.name.replace("-", " ").title()}'
                out.append((f"/{country_slug}/{parent_slug}/{sub.name}/", label))
    return out


_NON_COUNTRY_DIRS = {
    "css", "og", "search", "topics", "cities", "cuisine", "cuisines", "dish",
    "dishes", "neighborhood", "neighborhoods", "signature-dishes", "dietary",
    "nightlife", "about", "contact", "privacy", "terms", "cookies",
    "disclaimer", "editorial-standards", "_manifest.json",
    "rooftops", "speakeasies", "dance-clubs", "live-music", "lgbtq-nightlife",
    "listening-bars", "late-night-dives", "best-brunch", "best-coffee",
    "best-wine-bars", "best-bakeries", "best-markets", "best-breweries",
    "best-cocktail-bars", "best-cocktails",
    # Cork & Curve cross-cut + asset roots that live directly under
    # content/ but aren't countries. Without this exclude list the stub
    # generator emits e.g. /grape/index.html with a "France"-shaped layout
    # that lists individual grape slugs as if they were regions.
    "grape", "grapes", "style", "styles", "world", "tag", "tags",
    "regions", "wine", "img", "js", "fonts", "assets",
}


def main() -> int:
    written = 0
    for country_dir in sorted(CONTENT.iterdir()):
        if not country_dir.is_dir():
            continue
        if (country_dir / "index.html").exists():
            continue
        country_slug = country_dir.name
        if country_slug in _NON_COUNTRY_DIRS:
            continue
        country_name = _country_display(country_slug)
        regions = _collect_regions(country_dir, country_slug)
        rollups = _collect_rollups(country_dir, country_slug)
        if not regions and not rollups:
            continue
        html_str = _stub_html(country_slug, country_name, regions, rollups)
        (country_dir / "index.html").write_text(html_str, encoding="utf-8")
        written += 1
        print(f"  emitted /{country_slug}/  ({len(regions)} regions, {len(rollups)} rollups)")
    print(f"wrote {written} country stub indexes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
