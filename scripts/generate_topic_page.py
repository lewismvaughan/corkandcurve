#!/usr/bin/env python3
"""
Generate topic pages from site-data JSON using Jinja2 templates.

Usage:
    python generate_topic_page.py <country_slug> <topic_slug>                       # One topic, one country
    python generate_topic_page.py <country_slug> --all                              # All topics, one country
    python generate_topic_page.py <country_slug> <topic_slug> --region <region>     # One topic, one region
    python generate_topic_page.py <country_slug> --all --region <region>            # All topics, one region
    python generate_topic_page.py <country_slug> <topic_slug> --all-regions         # One topic, all regions
    python generate_topic_page.py <country_slug> --all --all-regions                # All topics, all regions
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.template_renderer import TemplateRenderer, render_page


# TableJourney v1 has no digital products. Reserved for later.
TOPIC_PRODUCT_MAPPING: dict = {}

# 24 wine topics. Keys are URL slugs and match TOPIC_FILES filenames 1:1.
# Each entry drives the page H1, subtitle, badge, and which TOC sidebar to show.
STANDARD_TOPICS = {
    'vineyards': {
        'name': 'Vineyards', 'badge': 'Estates & Châteaux', 'icon': '🍇',
        'h1_template': 'Vineyards in {name}',
        'subtitle_template': 'The estates, domaines and châteaux worth the drive in {name}, from first growths to grower gems.',
        'meta_description_template': 'The estates, domaines and châteaux worth visiting in {name}. Classifications, varietals, tasting programs and how to book a cellar visit.',
    },
    'wines': {
        'name': 'Wines', 'badge': 'Every Cuvée', 'icon': '🍷',
        'h1_template': 'Wines of {name}',
        'subtitle_template': 'Every cuvée worth knowing in {name}: taste, food pairings, history and tags to find your match.',
        'meta_description_template': 'Every cuvée worth knowing in {name}. Taste profiles, food pairings, history and filter chips so you can find the wine that fits the meal, mood or occasion.',
    },
    'tasting-rooms': {
        'name': 'Tasting Rooms', 'badge': 'Where to Taste', 'icon': '🍷',
        'h1_template': 'Tasting Rooms in {name}',
        'subtitle_template': 'Urban tasting rooms and at-winery flights in {name}, with what they pour and whether you need an appointment.',
        'meta_description_template': 'Where to taste in {name}: urban tasting rooms and at-winery flights, what they pour, flight prices and whether you can walk in or need to book.',
    },
    'wine-bars': {
        'name': 'Wine Bars', 'badge': 'By the Glass', 'icon': '🥂',
        'h1_template': 'Best Wine Bars in {name}',
        'subtitle_template': 'Where to drink by the glass in {name}: natural, classical and grower-focused lists worth the detour.',
        'meta_description_template': 'Where to drink wine by the glass in {name}. The natural-wine rooms, classical caves and grower-focused lists worth the detour, with what is poured.',
    },
    'wine-restaurants': {
        'name': 'Wine Restaurants', 'badge': 'Cellar & Plate', 'icon': '🍽️',
        'h1_template': 'Wine Restaurants in {name}',
        'subtitle_template': 'Restaurants in {name} with cellars and sommeliers worth the markup.',
        'meta_description_template': 'Restaurants in {name} known for their wine: deep cellars, award lists and sommeliers worth the markup, with what to order alongside.',
    },
    'wine-retailers': {
        'name': 'Wine Retailers', 'badge': 'Bottles to Buy', 'icon': '🛒',
        'h1_template': 'Wine Retailers in {name}',
        'subtitle_template': 'Where to buy bottles to take home in {name}: cavistes, enotecas and specialist merchants.',
        'meta_description_template': 'Where to buy wine to take home in {name}. Cavistes, enotecas and specialist merchants, what they stock and who ships internationally.',
    },
    'wine-schools': {
        'name': 'Wine Schools', 'badge': 'Learn the Region', 'icon': '🎓',
        'h1_template': 'Wine Schools and Classes in {name}',
        'subtitle_template': 'Tastings, courses and structured sessions in {name} that teach you the region in a glass.',
        'meta_description_template': 'Wine schools and classes in {name}. Guided tastings, certification courses and blending sessions that teach the region in a glass, with prices.',
    },
    'wine-tours': {
        'name': 'Wine Tours', 'badge': 'Guided Routes', 'icon': '🚐',
        'h1_template': 'Wine Tours in {name}',
        'subtitle_template': 'Guided wine tours in {name} worth booking, by route and theme, with run times and what is poured.',
        'meta_description_template': 'Guided wine tours in {name} worth your time. Operators we would book, by route and theme, with run times, group size and what is poured.',
    },
    'wine-festivals': {
        'name': 'Wine Festivals', 'badge': 'Annual Events', 'icon': '🎉',
        'h1_template': 'Wine Festivals in {name}',
        'subtitle_template': 'Wine fairs and en primeur weeks in {name} worth planning a trip around, by month.',
        'meta_description_template': 'Wine festivals in {name} worth planning a trip around. By month, with featured producers, where they happen, tickets and the satellite events worth catching.',
    },
    'distilleries': {
        'name': 'Distilleries', 'badge': 'Spirits Too', 'icon': '🥃',
        'h1_template': 'Distilleries in {name}',
        'subtitle_template': 'Where the region overlaps spirits: distilleries and tasting bars in {name}.',
        'meta_description_template': 'Distilleries in {name} where the region overlaps spirits. What they make, tour and tasting options and where to taste the local pour.',
    },
    'wine-museums': {
        'name': 'Wine Museums', 'badge': 'History & Craft', 'icon': '🏛️',
        'h1_template': 'Wine Museums in {name}',
        'subtitle_template': "Museums and interpretive centres in {name} that tell the region's wine story.",
        'meta_description_template': "Museums and interpretive centres in {name} that tell the region's wine story, with what to see, ticket prices and how long to allow.",
    },
    'wine-hotels': {
        'name': 'Wine Hotels', 'badge': 'Estate Stays', 'icon': '🛏️',
        'h1_template': 'Wine Hotels in {name}',
        'subtitle_template': 'Vineyard B&Bs and estate stays in {name} where you sleep among the vines.',
        'meta_description_template': 'Where to stay among the vines in {name}. Vineyard B&Bs and estate hotels, what they offer guests and how to book a room with a cellar view.',
    },
    'wine-experiences': {
        'name': 'Wine Experiences', 'badge': 'Beyond the Tasting', 'icon': '✨',
        'h1_template': 'Wine Experiences in {name}',
        'subtitle_template': 'Harvest days, blending sessions and vineyard flights in {name}, beyond the standard tasting.',
        'meta_description_template': 'Wine experiences in {name} beyond the standard tasting. Harvest days, blending sessions, vineyard helicopter flights and how to book them.',
    },
    'wine-history': {
        'name': 'Wine History', 'badge': 'How {name} Drinks', 'icon': '📜',
        'h1_template': 'Wine History of {name}',
        'subtitle_template': 'How {name} came to make wine the way it does: the eras, families and rules that shaped the glass.',
        'meta_description_template': 'How {name} came to make wine the way it does. The viticultural eras, families, classifications and rules that shaped the glass.',
    },
    'seasonal-wine': {
        'name': 'Seasonal', 'badge': 'When to Visit', 'icon': '🍂',
        'h1_template': 'Seasonal Wine in {name}',
        'subtitle_template': 'When to visit {name}: harvest, en primeur and the calendar that shapes a cellar visit.',
        'meta_description_template': 'When to visit {name} for wine. Harvest, en primeur weeks and the season-by-season calendar that shapes a cellar visit.',
    },
    'signature-wines': {
        'name': 'Signature Wines', 'badge': 'Iconic Bottles', 'icon': '🍾',
        'h1_template': 'Signature Wines of {name}',
        'subtitle_template': 'The iconic bottles that define {name}: what they are, who makes them and what they cost.',
        'meta_description_template': 'The iconic bottles that define {name}. What they are, who makes them, the style, typical vintages and what a bottle costs at retail.',
    },
    'signature-grapes': {
        'name': 'Signature Grapes', 'badge': 'Canonical Varietals', 'icon': '🌿',
        'h1_template': 'Signature Grapes of {name}',
        'subtitle_template': 'The grapes that define {name}: the canonical varietals and how the region expresses them.',
        'meta_description_template': 'The grapes that define {name}. The canonical varietals, how the region expresses them and the bottles that show them at their best.',
    },
    'budget-wines': {
        'name': 'Budget Wines', 'badge': 'Under €25', 'icon': '💶',
        'h1_template': 'Budget Wines in {name}',
        'subtitle_template': 'Excellent bottles under €25 in {name}: the value finds locals actually drink.',
        'meta_description_template': 'Excellent wines under €25 in {name}. The value bottles locals actually drink, where to buy them and the producers punching above their price.',
    },
    'hidden-gems': {
        'name': 'Hidden Gems', 'badge': 'Locals-Only', 'icon': '💎',
        'h1_template': 'Hidden Wine Gems in {name}',
        'subtitle_template': 'The lesser-known estates and cellars in {name} that the guidebooks miss.',
        'meta_description_template': 'The lesser-known estates and cellars in {name} that the guidebooks miss. Grower gems, family domaines and the cellars locals keep quiet.',
    },
    'day-trips-wine': {
        'name': 'Day Trips', 'badge': 'Within Reach', 'icon': '🚆',
        'h1_template': 'Wine Day Trips from {name}',
        'subtitle_template': 'Neighbouring appellations within easy reach of {name}, worth the early start.',
        'meta_description_template': 'Wine day trips from {name}. Neighbouring appellations worth the early start, with travel times, what they are known for and where to taste.',
    },
    'itineraries': {
        'name': 'Itineraries', 'badge': 'Day-by-day Plans', 'icon': '🗺️',
        'h1_template': 'Wine Itineraries for {name}',
        'subtitle_template': 'Day-by-day estate-visit plans for {name}: weekend, first-timer and deep-cellar editions.',
        'meta_description_template': 'Day-by-day estate-visit plans for {name}, by audience. Weekend routes, first-timer plans and deep-cellar editions on Cork & Curve.',
    },
    # NOTE: 'neighborhoods' (sub-appellations) is intentionally NOT a topic
    # page. The region-scoped sub-appellation index at
    # /<country>/<region>/neighborhoods/ is owned by
    # generate_scoped_cross_cuts.py (a better grouped index than a generic
    # card grid). The nav chip for it lives in WINE_TOPIC_NAV and points at
    # that scoped index.
    'nightlife': {
        'name': 'Nightlife', 'badge': 'After Dark', 'icon': '🌃',
        'h1_template': 'Wine Nightlife in {name}',
        'subtitle_template': 'Late wine bars, listening rooms and evening tastings in {name}.',
        'meta_description_template': 'Where to drink wine after dark in {name}. Late-opening wine bars, listening rooms, fortified specialists and evening tastings worth the trip.',
    },
    'dietary': {
        'name': 'Biodynamic & Natural', 'badge': "How It's Made", 'icon': '🌱',
        'h1_template': 'Biodynamic, Organic and Natural Wine in {name}',
        'subtitle_template': 'Biodynamic, organic and natural wine in {name}: the certified estates and low-intervention cellars.',
        'meta_description_template': 'Biodynamic, organic and natural wine in {name}. The Demeter-certified estates, organic growers and low-intervention cellars, and where to taste them.',
    },
    'food-pairing': {
        'name': 'Food Pairing', 'badge': 'Wine & Table', 'icon': '🧀',
        'h1_template': 'Food and Wine Pairing in {name}',
        'subtitle_template': "What to eat with the wines of {name}, and where the region's food and wine meet.",
        'meta_description_template': "What to eat with the wines of {name}. Classic regional pairings, the local dishes that match the bottles and where food and wine meet.",
    },
}


def load_site_data(country_slug: str, topic_slug: str = None, region_slug: str = None) -> dict:
    """Load site-data for a country or subregion from split files (26-file format).
    If topic_slug provided, loads only region.json + that topic file (2 files).
    Otherwise loads all 26 files (for full dataset)."""
    if topic_slug:
        from utils.data_loader import load_for_topic
        return load_for_topic(country_slug, topic_slug, region_slug=region_slug)
    from utils.data_loader import load_country_data
    return load_country_data(country_slug, region_slug=region_slug)


def get_related_product(products: list, topic_slug: str) -> dict:
    """
    Get the most relevant product for a topic page.

    Args:
        products: List of products from site-data
        topic_slug: The current topic slug

    Returns:
        The most relevant product dict, or None if no products available
    """
    if not products:
        return None

    # Get the preferred product type for this topic
    preferred_type = TOPIC_PRODUCT_MAPPING.get(topic_slug, '7day-itinerary')

    # Try to find the preferred product
    for product in products:
        if product.get('product_type_key') == preferred_type:
            return product

    # Fallback to first available product (usually 7day-itinerary)
    return products[0] if products else None


def prepare_topic_data(site_data: dict, topic_slug: str) -> dict:
    """
    Prepare data context for a specific topic page.

    Adds topic-specific fields to the site data.
    """
    data = dict(site_data)  # Copy to avoid modifying original
    dest_name = data.get('destination', {}).get('name', 'Unknown')

    # Get topic config
    topic_config = STANDARD_TOPICS.get(topic_slug, {
        'name': topic_slug.title(),
        'badge': 'Guide',
        'h1_template': '{name} ' + topic_slug.title() + ' Guide 2025',
        'subtitle_template': 'Your guide to ' + topic_slug + ' in {name}.',
    })

    # Build topic metadata
    data['topic'] = {
        'name': topic_config['name'],
        'slug': topic_slug,
        'badge': topic_config['badge'],
        'title': topic_config['h1_template'].format(name=dest_name),
        'h1': topic_config['h1_template'].format(name=dest_name),
        'subtitle': topic_config['subtitle_template'].format(name=dest_name),
        'meta_description': topic_config.get(
            'meta_description_template',
            topic_config['subtitle_template'],
        ).format(name=dest_name),
        'read_time': 12,
        'word_count': 2500,
        'icon': topic_config.get('icon', '🍽️'),
        'updated': 'May 2026',
        'url': f"/{data.get('country_slug', 'unknown')}/{data.get('region_slug')}/{topic_slug}/" if data.get('region_slug') else f"/{data.get('country_slug', 'unknown')}/{topic_slug}/",
    }

    data['toc_items'] = _get_toc_items(topic_slug)
    data['related_topic_links'] = _get_related_topics(
        topic_slug,
        data.get('country_slug', 'unknown'),
        region_slug=data.get('region_slug'),
    )

    return data


def _get_toc_items(topic_slug: str) -> list:
    """TOC items for the topic-page sidebar. Section IDs match what each topic template renders."""
    toc_map = {
        'vineyards':        [('intro','Overview'), ('picks','Estates to visit'), ('faq','FAQ')],
        'wines':            [('intro','Overview'), ('filter','Filter by tag'), ('cuvees','Every cuvée'), ('faq','FAQ')],
        'tasting-rooms':    [('intro','Overview'), ('picks','Where to taste'), ('faq','FAQ')],
        'wine-bars':        [('intro','Overview'), ('picks','Best wine bars'), ('faq','FAQ')],
        'wine-restaurants': [('intro','Overview'), ('picks','Cellar & plate'), ('faq','FAQ')],
        'wine-retailers':   [('intro','Overview'), ('picks','Where to buy'), ('faq','FAQ')],
        'wine-schools':     [('intro','Overview'), ('picks','Classes'), ('faq','FAQ')],
        'wine-tours':       [('intro','Overview'), ('picks','Tours'), ('faq','FAQ')],
        'wine-festivals':   [('intro','Overview'), ('picks','Festivals by month'), ('faq','FAQ')],
        'distilleries':     [('intro','Overview'), ('picks','Distilleries'), ('faq','FAQ')],
        'wine-museums':     [('intro','Overview'), ('picks','Museums'), ('faq','FAQ')],
        'wine-hotels':      [('intro','Overview'), ('picks','Estate stays'), ('faq','FAQ')],
        'wine-experiences': [('intro','Overview'), ('picks','Experiences'), ('faq','FAQ')],
        'wine-history':     [('intro','Overview'), ('key-eras','Key eras'), ('influences','Influences'), ('innovations','Innovations'), ('faq','FAQ')],
        'seasonal-wine':    [('intro','Overview'), ('spring','Spring'), ('summer','Summer'), ('autumn','Autumn'), ('winter','Winter'), ('faq','FAQ')],
        'signature-wines':  [('intro','Overview'), ('wines','Iconic bottles'), ('faq','FAQ')],
        'signature-grapes': [('intro','Overview'), ('grapes','Canonical grapes'), ('faq','FAQ')],
        'budget-wines':     [('intro','Overview'), ('picks','Value finds'), ('faq','FAQ')],
        'hidden-gems':      [('intro','Overview'), ('picks','Off the beaten cellar'), ('faq','FAQ')],
        'day-trips-wine':   [('intro','Overview'), ('picks','Worth the trip'), ('faq','FAQ')],
        'itineraries':      [('intro','Overview'), ('plans','Day-by-day plans'), ('faq','FAQ')],
        'neighborhoods':    [('intro','Overview'), ('picks','Sub-appellations'), ('faq','FAQ')],
        'dietary':          [('intro','Overview'), ('biodynamic','Biodynamic'), ('organic','Organic'), ('natural','Natural'), ('faq','FAQ')],
        'nightlife':        [('intro','Overview'), ('wine_bars_late','Late Wine Bars'), ('listening_bars','Listening Rooms'), ('late_tastings','Late Tastings'), ('faq','FAQ')],
        'food-pairing':     [('intro','Overview'), ('pairings','Pairings'), ('faq','FAQ')],
    }
    pairs = toc_map.get(topic_slug, [('intro','Overview'), ('picks','Our picks'), ('faq','FAQ')])
    return [{'id': i, 'title': t} for i, t in pairs]


def _get_related_topics(current_topic: str, country_slug: str, region_slug: str = None) -> list:
    """Curated related-topic clusters within the wine universe."""
    relations = {
        'vineyards':        ['wines', 'tasting-rooms', 'signature-wines', 'signature-grapes'],
        'wines':            ['vineyards', 'signature-wines', 'signature-grapes', 'food-pairing'],
        'tasting-rooms':    ['vineyards', 'wine-bars', 'distilleries', 'signature-wines'],
        'wine-bars':        ['wine-restaurants', 'tasting-rooms', 'nightlife', 'hidden-gems'],
        'wine-restaurants': ['wine-bars', 'food-pairing', 'signature-wines', 'wine-hotels'],
        'wine-retailers':   ['signature-wines', 'budget-wines', 'tasting-rooms', 'vineyards'],
        'wine-schools':     ['wine-tours', 'tasting-rooms', 'wine-history', 'signature-grapes'],
        'wine-tours':       ['vineyards', 'tasting-rooms', 'distilleries', 'wine-experiences'],
        'wine-festivals':   ['seasonal-wine', 'signature-wines', 'wine-experiences', 'wine-history'],
        'distilleries':     ['wine-bars', 'wine-tours', 'tasting-rooms', 'hidden-gems'],
        'wine-museums':     ['wine-history', 'vineyards', 'wine-tours', 'signature-grapes'],
        'wine-hotels':      ['vineyards', 'wine-experiences', 'itineraries', 'wine-restaurants'],
        'wine-experiences': ['wine-tours', 'vineyards', 'wine-festivals', 'wine-hotels'],
        'wine-history':     ['signature-grapes', 'wine-museums', 'signature-wines', 'wine-festivals'],
        'seasonal-wine':    ['wine-festivals', 'wine-experiences', 'vineyards', 'itineraries'],
        'signature-wines':  ['signature-grapes', 'vineyards', 'wine-retailers', 'food-pairing'],
        'signature-grapes': ['signature-wines', 'vineyards', 'wine-history', 'neighborhoods'],
        'budget-wines':     ['wine-retailers', 'hidden-gems', 'tasting-rooms', 'signature-wines'],
        'hidden-gems':      ['vineyards', 'tasting-rooms', 'budget-wines', 'wine-bars'],
        'day-trips-wine':   ['wine-tours', 'itineraries', 'neighborhoods', 'vineyards'],
        'itineraries':      ['vineyards', 'wine-tours', 'wine-hotels', 'day-trips-wine'],
        'neighborhoods':    ['vineyards', 'signature-grapes', 'day-trips-wine', 'tasting-rooms'],
        'nightlife':        ['wine-bars', 'tasting-rooms', 'wine-restaurants', 'hidden-gems'],
        'dietary':          ['vineyards', 'signature-grapes', 'wine-bars', 'hidden-gems'],
        'food-pairing':     ['wine-restaurants', 'signature-wines', 'signature-grapes', 'wine-bars'],
    }
    related_slugs = relations.get(current_topic, ['vineyards', 'tasting-rooms', 'signature-wines', 'hidden-gems'])
    out = []
    for t in related_slugs:
        if t == current_topic:
            continue
        out.append({
            'slug': t,
            'name': STANDARD_TOPICS.get(t, {}).get('name', t.replace('-', ' ').title()),
            'url': f"/{country_slug}/{region_slug}/{t}/" if region_slug else f"/{country_slug}/{t}/",
        })
    return out[:4]


def _get_quick_facts(data: dict) -> list:
    """Extract quick facts from site data."""
    dest = data.get('destination', {})
    facts = []

    if dest.get('capital'):
        facts.append(f"Capital: {dest['capital']}")
    if dest.get('languages'):
        langs = dest['languages']
        if isinstance(langs, list):
            facts.append(f"Languages: {', '.join(langs)}")
        else:
            facts.append(f"Languages: {langs}")
    if dest.get('currency'):
        facts.append(f"Currency: {dest['currency']}")
    if dest.get('time_zone'):
        facts.append(f"Time Zone: {dest['time_zone']}")

    research = data.get('research', {})
    best_time = research.get('best_time_to_visit', {})
    if best_time.get('best'):
        facts.append(f"Best Season: {best_time['best']}")

    return facts


def generate_topic_page(country_slug: str, topic_slug: str, region_slug: str = None, output_dir: str = None) -> str:
    """
    Generate a topic page for a country or subregion.

    Args:
        country_slug: The country slug (e.g., 'afghanistan')
        topic_slug: The topic slug (e.g., 'attractions')
        region_slug: Optional subregion slug (e.g., 'kabul')
        output_dir: Optional custom output directory

    Returns:
        Path to the generated HTML file
    """
    repo_root = Path(__file__).parent.parent

    # Load site data (optimized: only loads region.json + topic file)
    data = load_site_data(country_slug, topic_slug=topic_slug, region_slug=region_slug)
    data['country_slug'] = country_slug
    if region_slug:
        data['region_slug'] = region_slug

    # Extract continent from seo.geo.region
    if 'continent' not in data:
        data['continent'] = data.get('seo', {}).get('geo', {}).get('region', 'World')

    # Prepare topic-specific data
    data = prepare_topic_data(data, topic_slug)

    # Clean navigation: only link to sibling topics that actually have data,
    # and expose the populated set so the template's sidebar quick-links can
    # gate themselves (no links to thin/missing chapters).
    try:
        from utils.data_loader import load_country_data, populated_topic_slugs
        _full = load_country_data(country_slug, region_slug=region_slug)
        _populated = populated_topic_slugs(_full.get("research", {}))
    except Exception:
        _populated = set()
    if _populated:
        data['populated_topics'] = sorted(_populated)
        data['related_topic_links'] = [
            r for r in data.get('related_topic_links', [])
            if r.get('slug') in _populated
        ]

    # Render the page using topic-specific template
    html = render_page(data, page_type='TOPIC', topic_slug=topic_slug)

    # Determine output path - use folder/index.html structure for clean URLs
    if output_dir:
        output_path = Path(output_dir) / topic_slug
    elif region_slug:
        output_path = repo_root / 'content' / country_slug / region_slug / topic_slug
    else:
        output_path = repo_root / 'content' / country_slug / topic_slug

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / 'index.html'

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(output_file)


def get_all_countries() -> list:
    """Get list of all countries with site-data."""
    repo_root = Path(__file__).parent.parent
    site_data_dir = repo_root / 'site-data'

    countries = []
    for item in site_data_dir.iterdir():
        if item.is_dir() and (item / 'data' / 'region.json').exists():
            countries.append(item.name)

    return sorted(countries)


def get_all_regions(country_slug: str) -> list:
    """Get list of all regions with site-data for a country."""
    from utils.data_loader import get_all_regions as _get_all
    return _get_all(country_slug)


def _generate_topics_for_target(country_slug: str, topic_slug: str = None, region_slug: str = None):
    """Generate topic page(s) for a single country or region target.

    If topic_slug is None, generates all 20 topics.
    """
    label = f"{country_slug}/{region_slug}" if region_slug else country_slug

    if topic_slug:
        # Single topic
        try:
            output_file = generate_topic_page(country_slug, topic_slug, region_slug=region_slug)
            print(f"Topic page generated successfully!")
            print(f"Output: {output_file}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            if region_slug:
                print(f"(Expected data at: site-data/{country_slug}/{region_slug}/data/{topic_slug}.json)")
            sys.exit(1)
        except Exception as e:
            print(f"Error generating page: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # All topics — but ONLY those with real data, so we never ship a
        # thin/empty chapter. Editorial topics (wine-history, seasonal-wine,
        # itineraries, food-pairing) count as data once the agent fills them.
        from utils.data_loader import load_country_data, populated_topic_slugs
        try:
            full = load_country_data(country_slug, region_slug=region_slug)
            populated = populated_topic_slugs(full.get("research", {}))
        except Exception as e:
            print(f"  [WARN] could not compute populated topics for {label}: {e}; generating all")
            populated = set(STANDARD_TOPICS.keys())
        targets = [ts for ts in STANDARD_TOPICS.keys() if ts in populated]
        skipped = [ts for ts in STANDARD_TOPICS.keys() if ts not in populated]
        print(f"Generating {len(targets)} populated topic pages for {label} (skipping {len(skipped)} empty)...")
        for ts in targets:
            try:
                output_file = generate_topic_page(country_slug, ts, region_slug=region_slug)
                print(f"  [OK] {ts} -> {output_file}")
            except Exception as e:
                print(f"  [FAIL] {ts}: {e}")
        # Prune any previously-generated topic page that is now empty (data
        # dropped) so stale thin pages don't linger.
        repo_root = Path(__file__).parent.parent
        import shutil as _shutil
        for ts in skipped:
            base = (repo_root / "content" / country_slug / region_slug / ts) if region_slug else (repo_root / "content" / country_slug / ts)
            if (base / "index.html").exists():
                _shutil.rmtree(base)
                print(f"  [PRUNE] removed now-empty {ts}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_topic_page.py <country_slug> <topic_slug>")
        print("       python generate_topic_page.py <country_slug> --all")
        print("       python generate_topic_page.py <country_slug> <topic_slug> --region <region>")
        print("       python generate_topic_page.py <country_slug> --all --region <region>")
        print("       python generate_topic_page.py <country_slug> <topic_slug> --all-regions")
        print("       python generate_topic_page.py <country_slug> --all --all-regions")
        print("\nAvailable topics:")
        for topic, config in STANDARD_TOPICS.items():
            print(f"  - {topic}: {config['name']}")
        print("\nAvailable countries:")
        for country in get_all_countries():
            print(f"  - {country}")
        sys.exit(1)

    country_slug = sys.argv[1]

    if len(sys.argv) < 3:
        print(f"Error: Please specify a topic or --all")
        print(f"Usage: python generate_topic_page.py {country_slug} <topic_slug>")
        sys.exit(1)

    # Parse all args after country_slug
    topic_slug = None
    region_slug = None
    all_topics = False
    all_regions = False

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--all':
            all_topics = True
            i += 1
        elif arg == '--region' and i + 1 < len(sys.argv):
            region_slug = sys.argv[i + 1]
            i += 2
        elif arg == '--all-regions':
            all_regions = True
            i += 1
        elif not arg.startswith('--') and topic_slug is None:
            topic_slug = arg
            i += 1
        else:
            print(f"Error: Unknown argument '{arg}'")
            sys.exit(1)

    # Validate: need either a topic or --all
    if not all_topics and not topic_slug:
        print(f"Error: Please specify a topic slug or --all")
        sys.exit(1)

    # Determine the effective topic (None means all topics)
    effective_topic = None if all_topics else topic_slug

    # Mode: all regions of a country
    if all_regions:
        regions = get_all_regions(country_slug)
        if not regions:
            print(f"No regions with full site-data found for {country_slug}.")
            print(f"(Regions need site-data/{country_slug}/{{region}}/data/region.json)")
            sys.exit(1)

        topic_label = "all topics" if all_topics else effective_topic
        print(f"Generating {topic_label} for {len(regions)} regions of {country_slug}...")

        for region in regions:
            _generate_topics_for_target(country_slug, effective_topic, region_slug=region)
        return

    # Mode: one specific region
    if region_slug:
        _generate_topics_for_target(country_slug, effective_topic, region_slug=region_slug)
        return

    # Mode: country level (default)
    _generate_topics_for_target(country_slug, effective_topic)


if __name__ == '__main__':
    main()
