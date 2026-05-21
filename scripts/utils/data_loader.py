#!/usr/bin/env python3
"""
Data loader for split site-data files.
Provides functions to load individual files or assemble the full dataset.

26-file split layout (1:1 mapping):
  region.json          → region/country hub page
  {topic}.json (×20)   → 20 topic pages
  product-{type}.json (×5) → 5 digital products

Usage:
  from utils.data_loader import load_country_data, load_for_topic, load_for_product

  data = load_country_data('france')           # Full dataset (all 26 files merged)
  data = load_for_topic('france', 'hotels')    # region.json + hotels.json
  data = load_for_product('france', '7day-itinerary')  # region.json + product-itinerary-7day.json
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent
SITE_DATA = REPO_ROOT / 'site-data'

# 24 food topic file names, matched 1:1 to topic slugs.
TOPIC_FILES = [
    'restaurants.json', 'fine-dining.json', 'casual-dining.json',
    'cafes.json', 'bakeries.json', 'coffee-roasters.json',
    'wine-bars.json', 'bars.json', 'street-food.json',
    'breweries.json', 'markets.json', 'food-tours.json',
    'festivals.json', 'cooking-classes.json', 'dietary.json',
    'budget-eating.json', 'signature-dishes.json', 'hidden-gems.json',
    'brunch.json', 'late-night.json', 'food-history.json',
    'seasonal-food.json', 'day-trips-food.json', 'itineraries.json',
    'nightlife.json',
]

# City-level metadata files merged into research dict on city-hub renders.
# Each must be a dict; its keys become research fields (e.g. city.json -> food_culture_summary).
CITY_META_FILES = [
    'city.json', 'neighborhoods.json',
]

# Digital products not in scope for v1 TableJourney; keep empty so loader is happy.
PRODUCT_FILES: list = []

# Files merged into research for full city-hub load.
OTHER_FILES = TOPIC_FILES + CITY_META_FILES + PRODUCT_FILES


def _data_dir(country_slug: str, region_slug: Optional[str] = None) -> Path:
    """Resolve the data/ directory for a country or subregion.

    Country:   site-data/{country}/data/
    Subregion: site-data/{country}/{region}/data/
    """
    if region_slug:
        return SITE_DATA / country_slug / region_slug / 'data'
    return SITE_DATA / country_slug / 'data'


def load_file(country_slug: str, filename: str, region_slug: Optional[str] = None) -> Dict[str, Any]:
    """Load a single data file for a country or subregion."""
    path = _data_dir(country_slug, region_slug) / filename
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Map of research-dict key -> topic URL slug. Used to compute per-entity URLs.
# Keys here are the keys templates iterate over in `research`.
# Topics absent from this map (e.g. signature_dishes, food_history, seasonal_food)
# do NOT get city-scoped per-entity pages.
RESEARCH_KEY_TO_TOPIC_SLUG = {
    "restaurants": "restaurants",
    "fine_dining": "fine-dining",
    "casual_dining": "casual-dining",
    "cafes": "cafes",
    "bakeries": "bakeries",
    "coffee_roasters": "coffee-roasters",
    "wine_bars": "wine-bars",
    "bars": "bars",
    "street_food": "street-food",
    "breweries": "breweries",
    "markets": "markets",
    "food_tours": "food-tours",
    "food_festivals": "festivals",
    "cooking_classes": "cooking-classes",
    "budget_eating": "budget-eating",
    "hidden_gems": "hidden-gems",
    "brunch": "brunch",
    "late_night": "late-night",
    "day_trips_food": "day-trips-food",
    # itineraries are NOT entered here: they are editorial content (not
    # venues), render inline on /<country>/<city>/itineraries/ with anchor
    # links (#<slug>), and have no city-scoped per-entity page in v1.
}


def _inject_entity_urls(research: Dict[str, Any], country_slug: str, region_slug: Optional[str]) -> None:
    """Add `_url` (and `_dish_url` for signature_dishes) to every entry with a slug.

    Mutates the research dict in place. URL convention:
      city-scoped entity: /<country>/<city>/<topic>/<slug>/
      global dish:        /dish/<slug>/

    Entries without a `slug` field are skipped. Templates render plain text
    via title_link() when `_url` is missing.
    """
    base = f"/{country_slug}/{region_slug}/" if region_slug else f"/{country_slug}/"
    for research_key, topic_slug in RESEARCH_KEY_TO_TOPIC_SLUG.items():
        entries = research.get(research_key)
        if isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict) and e.get("slug"):
                    e["_url"] = f"{base}{topic_slug}/{e['slug']}/"

    # Dietary: dict-of-lists keyed by vegan/vegetarian/...
    dietary = research.get("dietary")
    if isinstance(dietary, dict):
        for places in dietary.values():
            if isinstance(places, list):
                for e in places:
                    if isinstance(e, dict) and e.get("slug"):
                        e["_url"] = f"{base}dietary/{e['slug']}/"

    # Signature dishes: prefer the city × dish page if it exists, else
    # fall back to the global cross-cut. SEO standard: when both exist,
    # link the user DOWN to the city-scoped page (more specific intent,
    # captures long-tail "where to eat <dish> in <city>" queries).
    # See docs/STANDARDS.md.
    from pathlib import Path as _Path
    _content_dir = _Path(__file__).resolve().parent.parent.parent / "content"
    dishes = research.get("signature_dishes")
    if isinstance(dishes, list):
        for d in dishes:
            if isinstance(d, dict) and d.get("slug"):
                city_dish_url = None
                if region_slug:
                    p = _content_dir / country_slug / region_slug / "dish" / d["slug"] / "index.html"
                    if p.exists():
                        city_dish_url = f"/{country_slug}/{region_slug}/dish/{d['slug']}/"
                d["_url"] = city_dish_url or f"/dish/{d['slug']}/"


def _enrich_neighborhoods(research: Dict[str, Any], country_slug: str, region_slug: Optional[str]) -> None:
    """Bridge editorial neighborhoods.json entries to /neighborhood/<city>/<alias>/ cross-cuts.

    Each editorial neighborhood may carry `aliases` (entity.neighborhood values
    that map to it). For each alias actually used by at least one entity in this
    city, we render the alias as a linked code on the hub card. Sets:

      n._link_url           URL of the first alias's cross-cut (the primary link)
      n._linked_aliases     [{code, url}] for every alias with entities
      n._display_label      "Le Marais (3e/4e)" — name + parens with linked codes only
    """
    if not region_slug:
        return  # only city hubs render neighborhood cards
    hoods = research.get("neighborhoods")
    if not isinstance(hoods, list):
        return

    # Collect every entity.neighborhood value used in this city.
    used: set = set()
    for key in RESEARCH_KEY_TO_TOPIC_SLUG:
        entries = research.get(key)
        if isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict) and e.get("neighborhood"):
                    used.add(e["neighborhood"])
    dietary = research.get("dietary")
    if isinstance(dietary, dict):
        for places in dietary.values():
            if isinstance(places, list):
                for e in places:
                    if isinstance(e, dict) and e.get("neighborhood"):
                        used.add(e["neighborhood"])

    base = f"/neighborhood/{region_slug}/"
    for n in hoods:
        if not isinstance(n, dict):
            continue
        aliases = n.get("aliases") or []
        linked = [{"code": a, "url": f"{base}{a}/"} for a in aliases if a in used]
        if linked:
            n["_link_url"] = linked[0]["url"]
            n["_linked_aliases"] = linked
        name = n.get("name") or ""
        if aliases:
            n["_display_label"] = f"{name} ({'/'.join(aliases)})"
        else:
            n["_display_label"] = name


def load_country_data(country_slug: str, region_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    Assemble full dataset from all 26 split files.
    Works for both countries and subregions.

    Returns the same structure templates expect:

    {
        "destination": { ... },
        "seo": { ... },
        "research": { ... },
        "products": [ ... ],
        "_metadata": { ... }
    }

    Country path:   site-data/{country}/data/
    Subregion path: site-data/{country}/{region}/data/
    """
    region = load_file(country_slug, 'region.json', region_slug)

    # Start with region's research data
    research = dict(region.get('research', {}))

    # Merge optional supporting files into research dict.
    # Files may be absent during the layout / dry-run phase, skip gracefully.
    for filename in OTHER_FILES:
        try:
            file_data = load_file(country_slug, filename, region_slug)
        except FileNotFoundError:
            continue
        if isinstance(file_data, dict):
            research.update(file_data)

    _inject_entity_urls(research, country_slug, region_slug)
    _enrich_neighborhoods(research, country_slug, region_slug)

    return {
        "destination": region.get("destination", {}),
        "seo": region.get("seo", {}),
        "research": research,
        "products": region.get("products", []),
        "_metadata": region.get("_metadata", {}),
    }


def load_for_topic(country_slug: str, topic_slug: str, region_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    Load only 2 files for a topic page: region.json + {topic}.json.

    Returns the same structure as load_country_data() but with
    only the relevant research section populated.

    Works for both countries and subregions.
    """
    region = load_file(country_slug, 'region.json', region_slug)
    topic_file = f'{topic_slug}.json'
    topic_data = load_file(country_slug, topic_file, region_slug)

    research = dict(topic_data)
    _inject_entity_urls(research, country_slug, region_slug)

    return {
        "destination": region.get("destination", {}),
        "seo": region.get("seo", {}),
        "research": research,
        "products": region.get("products", []),
    }


def load_for_product(country_slug: str, product_type: str, region_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    Load only 2 files for a digital product: region.json + product file.

    Args:
        product_type: One of 'itinerary-7day', 'itinerary-3day',
                      'family-guide', 'food-guide', 'budget-guide'

                      Also accepts short forms: '7day-itinerary' → 'itinerary-7day'

    Works for both countries and subregions.
    """
    # Map common aliases to actual file names
    PRODUCT_ALIASES = {
        '7day-itinerary': 'itinerary-7day',
        '3day-itinerary': 'itinerary-3day',
    }
    product_key = PRODUCT_ALIASES.get(product_type, product_type)

    region = load_file(country_slug, 'region.json', region_slug)
    product_file = f'product-{product_key}.json'
    product_data = load_file(country_slug, product_file, region_slug)

    return {
        "destination": region.get("destination", {}),
        "research": dict(product_data),
    }


def get_all_countries() -> list:
    """Get sorted list of all country slugs that have split data."""
    return sorted([
        d.name for d in SITE_DATA.iterdir()
        if d.is_dir() and (d / 'data' / 'region.json').exists()
    ])


def get_all_regions(country_slug: str) -> list:
    """Get sorted list of all region slugs for a country that have split data.

    Only returns regions that have the full 26-file data/ directory
    (i.e., site-data/{country}/{region}/data/region.json exists).
    """
    country_dir = SITE_DATA / country_slug
    if not country_dir.is_dir():
        return []
    return sorted([
        d.name for d in country_dir.iterdir()
        if d.is_dir() and d.name != 'data' and (d / 'data' / 'region.json').exists()
    ])
