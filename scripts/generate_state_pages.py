#!/usr/bin/env python3
"""
Generate state-index hub pages from city data.

Walks site-data/<country>/<city>/data/region.json files, groups cities by
their destination.state / destination.state_slug fields, and renders one
state hub page per unique state at /content/<country>/<state_slug>/index.html.

Usage:
    python3 generate_state_pages.py                 # all countries
    python3 generate_state_pages.py united-states   # one country
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from utils.template_renderer import render_page
from utils.data_loader import get_all_countries, get_all_regions


def collect_states(country_slug: str, repo_root: Path) -> dict:
    """Return {(state_slug, state_name): [city_dict, ...]} for one country."""
    states = defaultdict(list)
    site_data = repo_root / 'site-data' / country_slug
    for city_slug in get_all_regions(country_slug):
        region_path = site_data / city_slug / 'data' / 'region.json'
        if not region_path.exists():
            continue
        with open(region_path, encoding='utf-8') as f:
            rdata = json.load(f)
        dest = rdata.get('destination', {})
        state_slug = dest.get('state_slug')
        state_name = dest.get('state')
        if not (state_slug and state_name):
            continue
        states[(state_slug, state_name)].append({
            'slug': city_slug,
            'name': dest.get('name', city_slug.replace('-', ' ').title()),
            'description': dest.get('tagline') or dest.get('overview', '')[:160],
        })
    return states


def generate_state_page(country_slug: str, state_slug: str, state_name: str,
                        cities: list, repo_root: Path) -> str:
    country_name_map = {'united-states': 'United States', 'france': 'France', 'japan': 'Japan'}
    country_name = country_name_map.get(country_slug, country_slug.replace('-', ' ').title())

    data = {
        'country_slug': country_slug,
        'region_slug': state_slug,
        'destination': {
            'name': state_name,
            'country': country_name,
            'tagline': f'Where to eat across {state_name}, city by city.',
            'overview': (
                f'{state_name} is a state of distinct food cities, each with its own '
                f'kitchens, markets and traditions. This is the {state_name} index for '
                f'TableJourney: pick a city to start eating.'
            ),
            'population': '',
            'hero_image': '',
            'hero_image_alt': f'{state_name} food scene',
        },
        'seo': {
            'base_url': 'https://tablejourney.com',
            'shared': {
                'og_image': f'https://tablejourney.com/og/{country_slug}.jpg',
                'og_image_alt': f'{state_name} food guide on TableJourney',
            },
            'geo': {
                'place_name': state_name,
                'country_code': 'US' if country_slug == 'united-states' else 'XX',
                'region': state_name,
                'latitude': '0.0',
                'longitude': '0.0',
            },
            'pages': {
                'index': {
                    'title': f'{state_name} Food Guide: Where to Eat City by City | TableJourney',
                    'description': (
                        f'Where to eat in {state_name}, city by city: restaurants, signature dishes, '
                        f'markets, hidden gems and the food culture of each {state_name} town.'
                    ),
                },
            },
            'alternates': [],
        },
        'research': {
            'food_culture_summary': (
                f'Pick a {state_name} city to begin. Each has its own food scene, '
                f'from neighbourhood institutions to the rooms defining the next decade.'
            ),
        },
        'products': [],
        'subregions': sorted(cities, key=lambda c: c['name']),
        'is_state_hub': True,
        '_metadata': {'schema_version': 'tj.v1', 'status': 'hub', 'ready_to_publish': True},
    }

    html = render_page(data, page_type='REGION')

    output_path = repo_root / 'content' / country_slug / state_slug
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    return str(output_file)


def main():
    repo_root = Path(__file__).parent.parent
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    countries = [arg] if arg else get_all_countries()

    written = []
    for country_slug in countries:
        states = collect_states(country_slug, repo_root)
        for (state_slug, state_name), cities in states.items():
            out = generate_state_page(country_slug, state_slug, state_name, cities, repo_root)
            written.append(out)
            print(f"  [OK] {state_name} ({country_slug}/{state_slug}) -> {out}")

    print(f"\nDone. {len(written)} state pages written.")


if __name__ == '__main__':
    main()
