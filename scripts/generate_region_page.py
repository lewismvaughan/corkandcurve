#!/usr/bin/env python3
"""
Generate region/country hub pages from site-data JSON using Jinja2 templates.

Usage:
    python generate_region_page.py <country_slug>                      # One country
    python generate_region_page.py --all                               # All countries
    python generate_region_page.py <country_slug> --region <region>    # One region
    python generate_region_page.py <country_slug> --all-regions        # All regions of a country
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.template_renderer import TemplateRenderer, render_page


def load_site_data(country_slug: str, region_slug: str = None) -> dict:
    """Load site-data for a country or subregion from split files (26-file format)."""
    from utils.data_loader import load_country_data
    return load_country_data(country_slug, region_slug=region_slug)


def generate_region_page(country_slug: str, region_slug: str = None, output_dir: str = None) -> str:
    """
    Generate a region hub page for a country or subregion.

    Args:
        country_slug: The country slug (e.g., 'afghanistan')
        region_slug: Optional subregion slug (e.g., 'kabul')
        output_dir: Optional custom output directory

    Returns:
        Path to the generated HTML file
    """
    repo_root = Path(__file__).parent.parent

    # Load site data
    data = load_site_data(country_slug, region_slug=region_slug)

    # Add slugs to data
    data['country_slug'] = country_slug
    if region_slug:
        data['region_slug'] = region_slug

    # Extract continent from seo.geo.region
    if 'continent' not in data:
        data['continent'] = data.get('seo', {}).get('geo', {}).get('region', 'World')

    # For country hub pages (not subregion pages), load subregions list
    if not region_slug:
        from utils.data_loader import get_all_regions as _get_all_regions

        SITE_DATA = repo_root / 'site-data'
        subregion_slugs = _get_all_regions(country_slug)
        subregions = []
        for sub_slug in subregion_slugs:
            # First try data/region.json (has full destination object with "name")
            region_json = SITE_DATA / country_slug / sub_slug / 'data' / 'region.json'
            index_json = SITE_DATA / country_slug / sub_slug / 'index.json'

            name = sub_slug.replace('-', ' ').title()  # fallback
            description = ''

            if region_json.exists():
                with open(region_json, encoding='utf-8') as f:
                    rdata = json.load(f)
                name = rdata.get('destination', {}).get('name', name)
                description = rdata.get('destination', {}).get('description', '')
            elif index_json.exists():
                # index.json uses "region_name" (not "name")
                with open(index_json, encoding='utf-8') as f:
                    idata = json.load(f)
                name = idata.get('region_name', name)
                description = idata.get('meta_description', '')

            subregions.append({
                'slug': sub_slug,
                'name': name,
                'description': description,
            })
        data['subregions'] = subregions

    # Render the page
    html = render_page(data, page_type='REGION')

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
    elif region_slug:
        output_path = repo_root / 'content' / country_slug / region_slug
    else:
        output_path = repo_root / 'content' / country_slug

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / 'index.html'

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(output_file)


def get_all_countries() -> list:
    """Get list of all countries with site-data."""
    from utils.data_loader import get_all_countries as _get_all
    return _get_all()


def get_all_regions(country_slug: str) -> list:
    """Get list of all regions with site-data for a country."""
    from utils.data_loader import get_all_regions as _get_all
    return _get_all(country_slug)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_region_page.py <country_slug>")
        print("       python generate_region_page.py --all")
        print("       python generate_region_page.py <country_slug> --region <region_slug>")
        print("       python generate_region_page.py <country_slug> --all-regions")
        print("\nAvailable countries:")
        for country in get_all_countries():
            print(f"  - {country}")
        sys.exit(1)

    # Parse --all (all countries)
    if sys.argv[1] == '--all':
        countries = get_all_countries()
        print(f"Generating region pages for {len(countries)} countries...")

        for country in countries:
            try:
                output_file = generate_region_page(country)
                print(f"  [OK] {country} -> {output_file}")
            except Exception as e:
                print(f"  [FAIL] {country}: {e}")
        return

    country_slug = sys.argv[1]

    # Parse remaining args
    region_slug = None
    all_regions = False

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--region' and i + 1 < len(sys.argv):
            region_slug = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--all-regions':
            all_regions = True
            i += 1
        else:
            print(f"Error: Unknown argument '{sys.argv[i]}'")
            sys.exit(1)

    # Mode: all regions of a country
    if all_regions:
        regions = get_all_regions(country_slug)
        if not regions:
            print(f"No regions with full site-data found for {country_slug}.")
            print(f"(Regions need site-data/{country_slug}/{{region}}/data/region.json)")
            sys.exit(1)

        print(f"Generating region pages for {len(regions)} regions of {country_slug}...")

        for region in regions:
            try:
                output_file = generate_region_page(country_slug, region_slug=region)
                print(f"  [OK] {country_slug}/{region} -> {output_file}")
            except Exception as e:
                print(f"  [FAIL] {country_slug}/{region}: {e}")
        return

    # Mode: one specific region
    if region_slug:
        try:
            output_file = generate_region_page(country_slug, region_slug=region_slug)
            print(f"Region page generated successfully!")
            print(f"Output: {output_file}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print(f"(Expected data at: site-data/{country_slug}/{region_slug}/data/region.json)")
            sys.exit(1)
        except Exception as e:
            print(f"Error generating page: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return

    # Mode: one country (default)
    try:
        output_file = generate_region_page(country_slug)
        print(f"Region page generated successfully!")
        print(f"Output: {output_file}")

        # Print stats
        data = load_site_data(country_slug)
        research = data.get('research', {})
        print(f"\nStats:")
        print(f"  - Attractions: {len(research.get('top_attractions', []))}")
        print(f"  - Hotels: {len(research.get('hotels', []))}")
        print(f"  - Restaurants: {len(research.get('restaurants', []))}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating page: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
