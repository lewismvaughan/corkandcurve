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
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent
SITE_DATA = REPO_ROOT / 'site-data'

# 24 wine topic file names, matched 1:1 to topic slugs.
TOPIC_FILES = [
    'vineyards.json', 'wines.json', 'tasting-rooms.json', 'wine-bars.json',
    'wine-restaurants.json', 'wine-retailers.json', 'wine-schools.json',
    'wine-tours.json', 'wine-festivals.json', 'distilleries.json',
    'wine-museums.json', 'wine-hotels.json', 'wine-experiences.json',
    'wine-history.json', 'seasonal-wine.json', 'signature-wines.json',
    'signature-grapes.json', 'budget-wines.json', 'hidden-gems.json',
    'day-trips-wine.json', 'itineraries.json', 'food-pairing.json',
    'dietary.json', 'nightlife.json',
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
    "vineyards": "vineyards",
    "tasting_rooms": "tasting-rooms",
    "wine_bars": "wine-bars",
    "wine_restaurants": "wine-restaurants",
    "wine_retailers": "wine-retailers",
    "wine_schools": "wine-schools",
    "wine_tours": "wine-tours",
    "wine_festivals": "wine-festivals",
    "distilleries": "distilleries",
    "wine_museums": "wine-museums",
    "wine_hotels": "wine-hotels",
    "wine_experiences": "wine-experiences",
    "budget_wines": "budget-wines",
    "hidden_gems": "hidden-gems",
    "day_trips_wine": "day-trips-wine",
    # itineraries, signature_wines, signature_grapes, wine_history,
    # seasonal_wine and food_pairing are NOT entered here: they are
    # editorial / abstract content (not venues), render inline on their
    # topic page, and have no region-scoped per-entity page in v1.
}


# Every navigable topic slug -> the research key it reads. Used to decide
# which topic pages/nav chips to render (only those with real data) so the
# site never ships thin/empty chapters or links to a 404.
TOPIC_SLUG_TO_KEY = {
    "vineyards": "vineyards",
    "wines": "wines",
    "tasting-rooms": "tasting_rooms",
    "wine-bars": "wine_bars",
    "wine-restaurants": "wine_restaurants",
    "wine-retailers": "wine_retailers",
    "wine-schools": "wine_schools",
    "wine-tours": "wine_tours",
    "wine-festivals": "wine_festivals",
    "distilleries": "distilleries",
    "wine-museums": "wine_museums",
    "wine-hotels": "wine_hotels",
    "wine-experiences": "wine_experiences",
    "wine-history": "wine_history",
    "seasonal-wine": "seasonal_wine",
    "signature-wines": "signature_wines",
    "signature-grapes": "signature_grapes",
    "budget-wines": "budget_wines",
    "hidden-gems": "hidden_gems",
    "day-trips-wine": "day_trips_wine",
    "itineraries": "itineraries",
    "neighborhoods": "neighborhoods",
    "nightlife": "nightlife",
    "dietary": "dietary",
    "food-pairing": "food_pairing",
}


_PRICE_NUM_RE = re.compile(r"\d+(?:[\.,]\d+)?")
_PRICE_CURRENCY_DEFAULT = "€"
_PRICE_TIERS = (
    (15,    1, "Everyday",  "Under {sym}15"),
    (30,    2, "Trade-up",  "{sym}15 to 30"),
    (75,    3, "Premium",   "{sym}30 to 75"),
    (200,   4, "Fine",      "{sym}75 to 200"),
    (500,   5, "Luxury",    "{sym}200 to 500"),
    (float("inf"), 5, "Collector", "{sym}500+"),
)


def compute_price_tier(price_band: Any) -> dict | None:
    """Map a free-form price_band string to a tier indicator.

    Mirrors the price-axis derivation in docs/WINE_TAGS.md so the visual
    tier and the /tag/price-*/ pages stay in sync. Returns a dict with:
      - tier:   integer 1..5
      - symbol: that many currency symbols (€ to €€€€€)
      - label:  "Everyday" / "Trade-up" / "Premium" / "Fine" / "Luxury"
      - range:  display range like "€30 to 75"
    Currency is auto-detected from price_band ($, €, £, ¥), defaults to €.

    Returns None when no numeric value can be parsed from price_band.
    Used in templates as `{{ wine._price_tier.symbol }}` etc.
    """
    if not isinstance(price_band, str) or not price_band.strip():
        return None
    nums = _PRICE_NUM_RE.findall(price_band.replace(",", ""))
    if not nums:
        return None
    try:
        lower = float(nums[0])
    except ValueError:
        return None
    sym = _PRICE_CURRENCY_DEFAULT
    for candidate in ("$", "€", "£", "¥"):
        if candidate in price_band:
            sym = candidate
            break
    for ceiling, tier_n, label, range_tmpl in _PRICE_TIERS:
        if lower < ceiling:
            # Cap at 5 symbols so very-expensive cuvées don't overflow card layout.
            return {
                "tier":     tier_n,
                "symbol":   sym * tier_n,
                "currency": sym,    # for filter dropdowns / per-region currency split
                "label":    label,
                "range":    range_tmpl.format(sym=sym),
            }
    return None


def _nonempty(value: Any) -> bool:
    """True if a research value carries real content. Handles list topics,
    dict-of-lists topics (dietary/nightlife) and object topics
    (wine_history/seasonal_wine) uniformly."""
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return any(
            _nonempty(v) if isinstance(v, (list, dict)) else bool(v)
            for v in value.values()
        )
    return bool(value)


def topic_has_data(research: Dict[str, Any], topic_slug: str) -> bool:
    """Does this region have real content for the given topic slug?"""
    key = TOPIC_SLUG_TO_KEY.get(topic_slug)
    if not key:
        return False
    return _nonempty(research.get(key))


def populated_topic_slugs(research: Dict[str, Any]) -> set:
    """Set of topic slugs that have real data in this region's research."""
    return {s for s in TOPIC_SLUG_TO_KEY if topic_has_data(research, s)}


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

    # Signature wines and grapes are abstract (a bottle / a varietal, not a
    # venue). They render inline on their topic page with #<slug> anchors and
    # also surface as global cross-cuts at /grape/<slug>/. Point each at the
    # grape cross-cut when a slug is present; the signature-wines page links
    # in-page via anchors.
    grapes = research.get("signature_grapes")
    if isinstance(grapes, list):
        _content = REPO_ROOT / "content"
        for g in grapes:
            if isinstance(g, dict) and g.get("slug"):
                # Only link to the global grape cross-cut if it was actually
                # generated. A signature grape with no producers in any region
                # (e.g. Piedmont Brachetto/Timorasso) has no /grape/<slug>/
                # page, so linking it would 404 — render it as plain text.
                if (_content / "grape" / g["slug"] / "index.html").exists():
                    g["_url"] = f"/grape/{g['slug']}/"

    # Cuvée pages use a GLOBAL URL scheme keyed on the producer slug
    # rather than the region's path, so they're shareable across the
    # whole catalog. wines.json lives under each region's data dir
    # (1:1 with the producer's region) but the rendered page lives at
    # /wine/<producer-slug>/<cuvee-slug>/ and is the same URL no
    # matter which region's hub a visitor reaches it from.
    # signature_wines[*] reference these cuvée pages; in
    # _enrich_signature_wine_urls below we set _url for signature wines
    # to the matching cuvée page when a producer slug is present.
    wines = research.get("wines")
    if isinstance(wines, list):
        for w in wines:
            if isinstance(w, dict) and w.get("slug") and w.get("producer"):
                w["_url"] = f"/wine/{w['producer']}/{w['slug']}/"
                # Visual price tier (€ to €€€€€). Computed once here so
                # every template that iterates wines (cuvée page,
                # wines-topic, tag-page card, homepage featured) reads
                # the same value without re-parsing price_band.
                tier = compute_price_tier(w.get("price_band"))
                if tier:
                    w["_price_tier"] = tier

    sigwines = research.get("signature_wines")
    if isinstance(sigwines, list) and isinstance(wines, list):
        # Build a producer lookup so signature_wines (curated subset with
        # only `slug`+`producer`) can resolve to the same /wine/.../...
        # URL as the full cuvée entry.
        wines_by_slug = {
            w["slug"]: w for w in wines
            if isinstance(w, dict) and w.get("slug")
        }
        for s in sigwines:
            if not isinstance(s, dict) or not s.get("slug"):
                continue
            prod = s.get("producer") or (wines_by_slug.get(s["slug"]) or {}).get("producer")
            if prod:
                s["_url"] = f"/wine/{prod}/{s['slug']}/"


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

    from utils.slug import slugify  # local import: avoids a module-level cycle
    base = f"/neighborhood/{region_slug}/"
    for n in hoods:
        if not isinstance(n, dict):
            continue
        aliases = n.get("aliases") or []
        # The cross-cut page lives at the SLUGIFIED path (generate_cross_cuts
        # writes /neighborhood/<region>/<slugify(neighborhood)>/), so the link
        # must slugify too. Raw aliases ("Rioja Alavesa", "Cote de Nuits") in
        # the URL 404'd on every region hub before this.
        linked = [{"code": a, "url": f"{base}{slugify(a)}/"} for a in aliases if a in used]
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
