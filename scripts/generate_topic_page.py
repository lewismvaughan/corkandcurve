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

# 20 food topics. Keys are URL slugs and match TOPIC_FILES filenames 1:1.
# Each entry drives the page H1, subtitle, badge, and which TOC sidebar to show.
STANDARD_TOPICS = {
    'restaurants': {
        'name': 'Restaurants', 'badge': 'Where to Eat', 'icon': '🍽️',
        'h1_template': 'Best Restaurants in {name}',
        'subtitle_template': 'The rooms worth a reservation in {name}, from neighbourhood bistros to the new classics.',
        'meta_description_template': 'The rooms worth a reservation in {name}, from neighbourhood bistros to the new-classics. Editor-picked menus, price ranges and what to order on a first visit.',
    },
    'fine-dining': {
        'name': 'Fine Dining', 'badge': 'Tasting Menus', 'icon': '⭐',
        'h1_template': 'Fine Dining in {name}',
        'subtitle_template': 'Tasting menus, Michelin stars and the chefs redefining {name}.',
        'meta_description_template': 'Tasting menus, Michelin stars and the chefs redefining {name}. Where to splurge, what each room serves and how to book without losing a month’s rent.',
    },
    'casual-dining': {
        'name': 'Casual Dining', 'badge': 'Neighbourhood Tables', 'icon': '🥘',
        'h1_template': 'Casual Dining in {name}',
        'subtitle_template': 'Bistros, trattorias and the everyday rooms where {name} actually eats.',
        'meta_description_template': 'Bistros, trattorias and the everyday rooms where {name} actually eats. Daily menus under €40, fair house wine and the regulars’ tables worth angling for.',
    },
    'cafes': {
        'name': 'Cafés', 'badge': 'Coffee & Bakeries', 'icon': '☕',
        'h1_template': 'Best Cafés in {name}',
        'subtitle_template': 'Where to sit, sip and slow down in {name}.',
        'meta_description_template': 'Where to sit, sip and slow down in {name}. Third-wave roasters, classic morning rooms, the bakeries worth the queue and the cafés that open before sunrise.',
    },
    'bakeries': {
        'name': 'Bakeries', 'badge': 'Bread & Pastry', 'icon': '🥐',
        'h1_template': 'Best Bakeries in {name}',
        'subtitle_template': 'The counters in {name} worth queuing for: bread, pastry, and the morning ritual.',
        'meta_description_template': 'The bakery counters in {name} worth queuing for, picked by TableJourney editors. Levain loaves, laminated pastry and the regional bakes worth crossing town for.',
    },
    'coffee-roasters': {
        'name': 'Coffee Roasters', 'badge': 'Beans & Brew', 'icon': '🫘',
        'h1_template': 'Best Coffee Roasters in {name}',
        'subtitle_template': 'The roasters writing the coffee scene in {name}: who they are, where they source from and where to drink it.',
        'meta_description_template': 'The roasters defining the coffee scene in {name}, picked by TableJourney editors. Where they source from, where to drink it, and which roasters keep a public cafe.',
    },
    'wine-bars': {
        'name': 'Wine Bars', 'badge': 'By the Glass', 'icon': '🍷',
        'h1_template': 'Best Wine Bars in {name}',
        'subtitle_template': 'Where to drink well in {name} by the glass and the bottle: natural, classical, and worth the cab fare.',
        'meta_description_template': 'Where to drink wine in {name} by the glass and the bottle. The natural-wine rooms, classical caves and grower-focused lists worth booking on TableJourney.',
    },
    'bars': {
        'name': 'Bars', 'badge': 'Drinking Guide', 'icon': '🍸',
        'h1_template': 'Best Bars in {name}',
        'subtitle_template': 'Cocktails, wine bars and dives: drinking in {name} for grown-ups.',
        'meta_description_template': 'Cocktails, wine bars and dives in {name}, plus the natural-wine rooms and listening bars now defining the scene, with reservations, hours and price ranges.',
    },
    'street-food': {
        'name': 'Street Food', 'badge': 'Vendors & Stalls', 'icon': '🌮',
        'h1_template': 'Street Food in {name}',
        'subtitle_template': "The fastest, cheapest, frequently best food on {name}'s streets.",
        'meta_description_template': 'The fastest, cheapest and frequently best food on {name}’s streets. Vendors worth the queue, the classic snacks every visitor should try and where to find them.',
    },
    'breweries': {
        'name': 'Breweries', 'badge': 'Local Beer', 'icon': '🍺',
        'h1_template': 'Breweries & Taprooms in {name}',
        'subtitle_template': 'Where {name} drinks local: brewpubs, taprooms and the new wave.',
        'meta_description_template': 'Where {name} drinks local. Brewpubs, taprooms, new-wave craft and the classic beer halls, with what to drink, what to eat alongside it and which ones to skip.',
    },
    'markets': {
        'name': 'Markets', 'badge': 'Food Markets', 'icon': '🥬',
        'h1_template': 'Food Markets in {name}',
        'subtitle_template': 'Where {name} shops, snacks and lunches: the markets worth your morning.',
        'meta_description_template': 'Where {name} shops, snacks and lunches. The covered halls, weekly street markets and producer stalls worth your morning, with what to buy and where to eat.',
    },
    'food-tours': {
        'name': 'Food Tours', 'badge': 'Guided Eating', 'icon': '🚶',
        'h1_template': 'Best Food Tours in {name}',
        'subtitle_template': 'Guided food tours in {name} worth your time, with operators we’d actually book.',
        'meta_description_template': 'Guided food tours in {name} worth your time and your euros. Operators we’d actually book, by neighbourhood and theme, with run times, group size and what’s served.',
    },
    'festivals': {
        'name': 'Food Festivals', 'badge': 'Annual Events', 'icon': '🎉',
        'h1_template': 'Food Festivals in {name}',
        'subtitle_template': 'Food festivals in {name} worth planning a trip around, by month.',
        'meta_description_template': 'Food festivals in {name} worth planning a trip around. By month, with what’s served, where they happen, ticket prices and the satellite events worth catching.',
    },
    'cooking-classes': {
        'name': 'Cooking Classes', 'badge': 'Hands-On', 'icon': '👨‍🍳',
        'h1_template': 'Cooking Classes in {name}',
        'subtitle_template': 'Hands-on cooking classes in {name} that teach something you’ll cook again at home.',
        'meta_description_template': 'Hands-on cooking classes in {name} that teach a recipe you’ll cook again at home. Market-to-table sessions, pastry workshops and the chefs worth booking, with prices.',
    },
    'dietary': {
        'name': 'Dietary', 'badge': 'Eat-Your-Way Guide', 'icon': '🌱',
        'h1_template': 'Vegan, Vegetarian & Dietary Guide to {name}',
        'subtitle_template': 'Vegan, vegetarian, gluten-free, halal and kosher options across {name}.',
        'meta_description_template': 'Vegan, vegetarian, gluten-free, halal and kosher eating across {name}. The menus that actually deliver, the dedicated rooms worth a trip and where to shop.',
    },
    'budget-eating': {
        'name': 'Budget Eats', 'badge': 'Cheap & Good', 'icon': '💶',
        'h1_template': 'Cheap Eats in {name}',
        'subtitle_template': "Eat well in {name} for under €15 a plate: the locals'-budget edition.",
        'meta_description_template': 'Eat well in {name} for under €15 a plate. The locals’-budget edition: bakery lunches, prix-fixe rooms, market-stall snacks and the chains worth the visit.',
    },
    'signature-dishes': {
        'name': 'Signature Dishes', 'badge': 'Must-Try', 'icon': '🥖',
        'h1_template': 'Signature Dishes of {name}',
        'subtitle_template': 'The plates that define {name}: what they are, and where to eat the canonical version.',
        'meta_description_template': 'The plates that define {name}. What they are, where to eat the canonical version, what a fair price looks like and which rooms have become the new reference.',
    },
    'hidden-gems': {
        'name': 'Hidden Gems', 'badge': 'Locals-Only', 'icon': '💎',
        'h1_template': 'Hidden Food Gems in {name}',
        'subtitle_template': 'The places in {name} the guidebooks miss.',
        'meta_description_template': 'The {name} rooms the guidebooks miss. Locals’-only addresses, family kitchens, the bars that don’t bother with signage and the producers who skip tourists.',
    },
    'brunch': {
        'name': 'Brunch', 'badge': 'Morning & Midday', 'icon': '🥞',
        'h1_template': 'Best Brunch in {name}',
        'subtitle_template': 'Where to brunch in {name}: morning rooms worth the queue.',
        'meta_description_template': 'Where to brunch in {name}. The morning rooms worth the queue, the boozy weekend menus and the bakery counters that have become the better, faster move.',
    },
    'late-night': {
        'name': 'Late-Night Eats', 'badge': 'After Hours', 'icon': '🌙',
        'h1_template': 'Late-Night Food in {name}',
        'subtitle_template': 'Where to eat in {name} after midnight, and the classic 2am move.',
        'meta_description_template': 'Where to eat in {name} after midnight. Bistros holding kitchens open, kebab counters, ramen, late-bar plates and the classic post-2am move every local knows.',
    },
    'food-history': {
        'name': 'Food History', 'badge': 'How {name} Eats', 'icon': '📜',
        'h1_template': 'Food History of {name}',
        'subtitle_template': 'How {name} came to eat the way it does: the people, migrations and accidents that shaped the plate.',
        'meta_description_template': 'How {name} came to eat the way it does. The migrations, markets, regulations and accidents that shaped the plate, plus where you can still taste each chapter today.',
    },
    'seasonal-food': {
        'name': 'Seasonal', 'badge': 'In Season', 'icon': '🍂',
        'h1_template': 'What’s in Season in {name}',
        'subtitle_template': 'What’s in season in {name}, and what to order when the market changes.',
        'meta_description_template': 'What’s in season in {name}, month by month. The vegetables, fruit, game and seafood at their peak, what to order when the market changes and the dishes that follow.',
    },
    'day-trips-food': {
        'name': 'Food Day Trips', 'badge': 'Within Reach', 'icon': '🚆',
        'h1_template': 'Food Day Trips from {name}',
        'subtitle_template': 'Food destinations within easy reach of {name}, worth the early start.',
        'meta_description_template': 'Food destinations within easy reach of {name}. Wine villages, producer towns, coastal stops and market days worth an early start, with travel times and routes.',
    },
    'itineraries': {
        'name': 'Itineraries', 'badge': 'Day-by-day Plans', 'icon': '🗺️',
        'h1_template': 'Eating Itineraries for {name}',
        'subtitle_template': 'Day-by-day eating plans for {name}: weekend, family, vegan, on-a-budget.',
        'meta_description_template': 'Day-by-day eating plans for {name}, by audience. Weekend classics, family two-day plans, vegan three-day routes and budget editions on TableJourney.',
    },
    'nightlife': {
        'name': 'Nightlife', 'badge': 'After Hours', 'icon': '🌃',
        'h1_template': 'Nightlife in {name}',
        'subtitle_template': 'Dance clubs, live music, rooftop bars, speakeasies, LGBTQ+ venues, listening bars and late-night dives in {name}.',
        'meta_description_template': 'Where to go out in {name} after dark. Dance clubs, live music venues, rooftop bars, speakeasies, LGBTQ+ nightlife, listening bars and the late-night dives worth the trip, told by TableJourney editors.',
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
        'restaurants':      [('intro','Overview'), ('picks','Our picks'), ('faq','FAQ')],
        'fine-dining':      [('intro','Overview'), ('top-tables','Top tables'), ('faq','FAQ')],
        'casual-dining':    [('intro','Overview'), ('picks','Where to eat'), ('faq','FAQ')],
        'cafes':            [('intro','Overview'), ('picks','Best cafés'), ('faq','FAQ')],
        'bakeries':         [('intro','Overview'), ('picks','Best bakeries'), ('faq','FAQ')],
        'coffee-roasters':  [('intro','Overview'), ('picks','Roasters worth knowing'), ('faq','FAQ')],
        'wine-bars':        [('intro','Overview'), ('picks','Best wine bars'), ('faq','FAQ')],
        'bars':             [('intro','Overview'), ('picks','Where to drink'), ('faq','FAQ')],
        'street-food':      [('intro','Overview'), ('vendors','Don’t-miss vendors'), ('faq','FAQ')],
        'breweries':        [('intro','Overview'), ('picks','Drink local'), ('faq','FAQ')],
        'markets':          [('intro','Overview'), ('picks','Markets'), ('faq','FAQ')],
        'food-tours':       [('intro','Overview'), ('picks','Tours'), ('faq','FAQ')],
        'festivals':        [('intro','Overview'), ('picks','Festivals by month'), ('faq','FAQ')],
        'cooking-classes':  [('intro','Overview'), ('picks','Classes'), ('faq','FAQ')],
        'dietary':          [('intro','Overview'), ('vegan','Vegan'), ('vegetarian','Vegetarian'), ('gluten_free','Gluten-free'), ('faq','FAQ')],
        'budget-eating':    [('intro','Overview'), ('cheap-eats','Cheap eats'), ('faq','FAQ')],
        'signature-dishes': [('intro','Overview'), ('dishes','Must-try'), ('faq','FAQ')],
        'hidden-gems':      [('intro','Overview'), ('gems','Off the beaten plate'), ('faq','FAQ')],
        'brunch':           [('intro','Overview'), ('picks','Brunch picks'), ('faq','FAQ')],
        'late-night':       [('intro','Overview'), ('picks','After-hours'), ('faq','FAQ')],
        'food-history':     [('intro','Overview'), ('key-eras','Key eras'), ('influences','Influences'), ('innovations','Innovations'), ('faq','FAQ')],
        'seasonal-food':    [('intro','Overview'), ('spring','Spring'), ('summer','Summer'), ('autumn','Autumn'), ('winter','Winter'), ('faq','FAQ')],
        'day-trips-food':   [('intro','Overview'), ('trips','Worth the trip'), ('faq','FAQ')],
        'itineraries':      [('intro','Overview'), ('plans','Day-by-day plans'), ('faq','FAQ')],
        'nightlife':        [('intro','Overview'), ('dance_clubs','Dance Clubs'), ('live_music','Live Music'), ('rooftop_bars','Rooftop Bars'), ('speakeasies','Speakeasies'), ('lgbtq','LGBTQ+'), ('listening_bars','Listening Bars'), ('late_night_dives','Late-Night Dives'), ('faq','FAQ')],
    }
    pairs = toc_map.get(topic_slug, [('intro','Overview'), ('faq','FAQ')])
    return [{'id': i, 'title': t} for i, t in pairs]


def _get_related_topics(current_topic: str, country_slug: str, region_slug: str = None) -> list:
    """Curated related-topic clusters within the food universe."""
    relations = {
        'restaurants':      ['fine-dining', 'casual-dining', 'signature-dishes', 'hidden-gems'],
        'fine-dining':      ['restaurants', 'signature-dishes', 'cooking-classes', 'food-history'],
        'casual-dining':    ['restaurants', 'budget-eating', 'brunch', 'hidden-gems'],
        'cafes':            ['brunch', 'bakeries', 'coffee-roasters', 'hidden-gems'],
        'bakeries':         ['cafes', 'brunch', 'budget-eating', 'hidden-gems'],
        'coffee-roasters':  ['cafes', 'bakeries', 'brunch', 'hidden-gems'],
        'wine-bars':        ['bars', 'casual-dining', 'hidden-gems', 'late-night'],
        'bars':             ['wine-bars', 'breweries', 'late-night', 'hidden-gems'],
        'street-food':      ['markets', 'budget-eating', 'hidden-gems', 'signature-dishes'],
        'breweries':        ['bars', 'food-tours', 'casual-dining', 'late-night'],
        'markets':          ['street-food', 'signature-dishes', 'food-tours', 'seasonal-food'],
        'food-tours':       ['markets', 'street-food', 'signature-dishes', 'cooking-classes'],
        'festivals':        ['seasonal-food', 'signature-dishes', 'markets', 'food-history'],
        'cooking-classes':  ['signature-dishes', 'markets', 'food-history', 'food-tours'],
        'dietary':          ['restaurants', 'cafes', 'budget-eating', 'brunch'],
        'budget-eating':    ['street-food', 'casual-dining', 'markets', 'hidden-gems'],
        'signature-dishes': ['restaurants', 'food-history', 'street-food', 'cooking-classes'],
        'hidden-gems':      ['street-food', 'late-night', 'restaurants', 'cafes'],
        'brunch':           ['cafes', 'casual-dining', 'hidden-gems', 'dietary'],
        'late-night':       ['bars', 'street-food', 'hidden-gems', 'breweries'],
        'food-history':     ['signature-dishes', 'food-tours', 'cooking-classes', 'festivals'],
        'seasonal-food':    ['markets', 'festivals', 'signature-dishes', 'casual-dining'],
        'day-trips-food':   ['food-tours', 'festivals', 'markets', 'signature-dishes'],
        'itineraries':      ['restaurants', 'signature-dishes', 'hidden-gems', 'day-trips-food'],
        'nightlife':        ['bars', 'wine-bars', 'late-night', 'hidden-gems'],
    }
    related_slugs = relations.get(current_topic, ['restaurants', 'signature-dishes', 'street-food', 'hidden-gems'])
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
        # All topics
        print(f"Generating all topic pages for {label}...")
        for ts in STANDARD_TOPICS.keys():
            try:
                output_file = generate_topic_page(country_slug, ts, region_slug=region_slug)
                print(f"  [OK] {ts} -> {output_file}")
            except Exception as e:
                print(f"  [FAIL] {ts}: {e}")


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
