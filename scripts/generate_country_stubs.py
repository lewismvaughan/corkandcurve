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

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
BASE = "https://tablejourney.com"


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
        "czech-republic": "Czech Republic",
    }.get(slug, slug.replace("-", " ").title())


def _stub_html(country_slug: str, country_name: str,
               cities: list[tuple[str, str]],
               rollups: list[tuple[str, str]]) -> str:
    canonical = f"{BASE}/{country_slug}/"
    title = f"{country_name} | TableJourney"
    desc = f"Where to eat in {country_name}: editor-picked guides for every city we cover, with cuisines, neighborhoods and signature dishes."
    cities_html = "".join(
        f'<li><a href="/{country_slug}/{cs}/"><strong>{html.escape(cn)}</strong></a></li>'
        for cs, cn in cities
    )
    rollups_html = "".join(
        f'<li><a href="{href}">{html.escape(label)}</a></li>'
        for href, label in rollups
    )
    return (
        '<!doctype html><html lang="en"><head>'
        '<meta charset="utf-8">'
        f'<title>{html.escape(title)}</title>'
        f'<meta name="description" content="{html.escape(desc)}">'
        f'<link rel="canonical" href="{html.escape(canonical)}">'
        '<meta name="robots" content="index, follow, max-image-preview:large">'
        '<link rel="stylesheet" href="/css/base.css">'
        '<link rel="stylesheet" href="/css/theme.css">'
        '</head><body>'
        '<header><nav><a href="/">TableJourney</a> &middot; <a href="/cities/">Cities</a> &middot; <a href="/topics/">Topics</a></nav></header>'
        '<main><div class="tj-container tj-prose">'
        f'<nav class="tj-breadcrumb"><a href="/">Home</a> &rsaquo; {html.escape(country_name)}</nav>'
        f'<h1>{html.escape(country_name)}</h1>'
        f'<p>Where to eat across {html.escape(country_name)}, editor-picked by TableJourney.</p>'
        + (
            '<section class="tj-section"><h2>Cities</h2>'
            f'<ul class="tj-grid-list">{cities_html}</ul></section>'
            if cities_html else ""
        )
        + (
            f'<section class="tj-section"><h2>Top across {html.escape(country_name)}</h2>'
            f'<ul class="tj-grid-list">{rollups_html}</ul></section>'
            if rollups_html else ""
        )
        + '</div></main>'
        '<footer><p><a href="/">Home</a> &middot; <a href="/cities/">All cities</a> &middot; <a href="/topics/">All topics</a> &middot; <a href="/about/">About</a></p></footer>'
        '</body></html>'
    )


def _collect_cities(country_dir: Path) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for child in sorted(country_dir.iterdir()):
        if not child.is_dir():
            continue
        # Skip rollup dirs that aren't cities
        if child.name in {"cuisine", "dish", "dietary", "nightlife", "cuisines",
                          "signature-dishes", "neighborhoods"}:
            continue
        # Skip topic-slug dirs at country scope
        topic_slugs = {
            "restaurants", "fine-dining", "casual-dining", "bakeries", "cafes",
            "coffee-roasters", "bars", "wine-bars", "breweries", "street-food",
            "markets", "late-night", "hidden-gems", "budget-eating", "brunch",
            "food-tours", "cooking-classes", "day-trips-food",
        }
        if child.name in topic_slugs:
            continue
        idx = child / "index.html"
        if not idx.exists():
            continue
        out.append((child.name, child.name.replace("-", " ").title()))
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
        cities = _collect_cities(country_dir)
        rollups = _collect_rollups(country_dir, country_slug)
        if not cities and not rollups:
            continue
        html_str = _stub_html(country_slug, country_name, cities, rollups)
        (country_dir / "index.html").write_text(html_str, encoding="utf-8")
        written += 1
        print(f"  emitted /{country_slug}/  ({len(cities)} cities, {len(rollups)} rollups)")
    print(f"wrote {written} country stub indexes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
