#!/usr/bin/env python3
"""
Scaffold the JSON data tree for a new city, ready for the food-research agent to fill.

Usage:
    python scripts/new_city.py france paris
    python scripts/new_city.py italy rome --name "Rome" --country "Italy"

Creates site-data/<country>/<city>/data/ with 27 stub files:
    region.json + city.json + neighborhoods.json
    + 24 topic files (one per food topic slug)

Each stub holds a top-level dict keyed to the field the templates read, so the
research agent only has to fill values. Re-runs are idempotent: existing files
are never overwritten unless --force is given.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# 24 food topic slugs <-> template-facing research keys (templates read snake_case).
# Keep this in lockstep with TOPIC_TEMPLATE_MAP in scripts/utils/template_renderer.py
# and TOPIC_FILES in scripts/utils/data_loader.py.
TOPIC_KEYS = {
    "restaurants":      "restaurants",
    "fine-dining":      "fine_dining",
    "casual-dining":    "casual_dining",
    "cafes":            "cafes",
    "bakeries":         "bakeries",
    "coffee-roasters":  "coffee_roasters",
    "wine-bars":        "wine_bars",
    "bars":             "bars",
    "street-food":      "street_food",
    "breweries":        "breweries",
    "markets":          "markets",
    "food-tours":       "food_tours",
    "festivals":        "food_festivals",
    "cooking-classes":  "cooking_classes",
    "dietary":          "dietary",
    "budget-eating":    "budget_eating",
    "signature-dishes": "signature_dishes",
    "hidden-gems":      "hidden_gems",
    "brunch":           "brunch",
    "late-night":       "late_night",
    "food-history":     "food_history",
    "seasonal-food":    "seasonal_food",
    "day-trips-food":   "day_trips_food",
    "itineraries":      "itineraries",
    "nightlife":        "nightlife",
}

# Some topics use a dict instead of a list (templates iterate keys).
DICT_TOPICS = {"dietary", "food-history", "seasonal-food", "nightlife"}


def stub_region(country_slug: str, city_slug: str, name: str, country: str) -> dict:
    base = f"https://tablejourney.com/{country_slug}/{city_slug}"
    today = _today_iso()
    return {
        "destination": {
            "name": name,
            "country": country,
            "tagline": "",
            "overview": "",
            "population": "",
            "hero_image": "",
            "hero_image_alt": f"{name} food scene",
            "hero_image_source": "",
            "hero_image_source_url": "",
            "hero_image_photographer": "",
            "hero_image_license": "",
        },
        "seo": {
            "base_url": "https://tablejourney.com",
            "shared": {
                "og_image": f"https://tablejourney.com/og/{city_slug}.jpg",
                "og_image_alt": f"{name} food guide on TableJourney",
            },
            "geo": {
                "place_name": name,
                "country_code": "",
                "region": "",
                "latitude": "",
                "longitude": "",
            },
            "pages": {
                "index": {
                    "title": f"{name} Food Guide | TableJourney",
                    "description": f"Where to eat in {name}: restaurants, signature dishes, markets, hidden gems and food culture. By TableJourney editors.",
                },
            },
            "article": {
                "author": "TableJourney Editorial",
                "published_time": f"{today}T00:00:00Z",
                "modified_time": f"{today}T00:00:00Z",
                "modified_display": _today_display(),
            },
            "alternates": [],
        },
        "research": {},
        "products": [],
        "_metadata": {
            "schema_version": "tj.v1",
            "status": "stub",
            "ready_to_publish": False,
        },
    }


def _today_iso() -> str:
    from datetime import date
    return date.today().isoformat()


def _today_display() -> str:
    from datetime import date
    d = date.today()
    return d.strftime("%B %Y")


def stub_city() -> dict:
    return {
        "food_culture_summary": "",
        "peak_food_season": "",
        "local_dining_hours": "",
        "tipping_norm": "",
        "food_tagline": "",
    }


def stub_neighborhoods() -> dict:
    return {"neighborhoods": []}


def stub_topic(slug: str) -> dict:
    key = TOPIC_KEYS[slug]
    if slug in DICT_TOPICS:
        if slug == "dietary":
            return {"dietary": {"vegan": [], "vegetarian": [], "gluten_free": [], "halal": [], "kosher": []}}
        if slug == "food-history":
            return {"food_history": {"key_eras": [], "immigrant_influences": [], "signature_innovations": []}}
        if slug == "seasonal-food":
            return {"seasonal_food": {"spring": [], "summer": [], "autumn": [], "winter": []}}
        if slug == "nightlife":
            return {"nightlife": {
                "dance_clubs": [],
                "live_music": [],
                "rooftop_bars": [],
                "speakeasies": [],
                "lgbtq": [],
                "listening_bars": [],
                "late_night_dives": [],
            }}
    return {key: []}


def write_if_missing(path: Path, payload: dict, force: bool) -> str:
    if path.exists() and not force:
        return "skip"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return "write"


def scaffold(country_slug: str, city_slug: str, name: str, country: str, force: bool) -> None:
    data_dir = SITE_DATA / country_slug / city_slug / "data"
    print(f"Scaffolding {country_slug}/{city_slug} at {data_dir}")
    actions = {"write": 0, "skip": 0}
    actions[write_if_missing(data_dir / "region.json", stub_region(country_slug, city_slug, name, country), force)] += 1
    actions[write_if_missing(data_dir / "city.json", stub_city(), force)] += 1
    actions[write_if_missing(data_dir / "neighborhoods.json", stub_neighborhoods(), force)] += 1
    for slug in TOPIC_KEYS:
        actions[write_if_missing(data_dir / f"{slug}.json", stub_topic(slug), force)] += 1
    total = sum(actions.values())
    print(f"Done: {actions['write']} written, {actions['skip']} skipped ({total} files).")
    if not force and actions["skip"]:
        print("Use --force to overwrite existing files.")


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold a new TableJourney city.")
    p.add_argument("country_slug", help="kebab-case slug, e.g. france")
    p.add_argument("city_slug", help="kebab-case slug, e.g. paris")
    p.add_argument("--name", help="Display name (default: titled city slug)")
    p.add_argument("--country", help="Display country (default: titled country slug)")
    p.add_argument("--force", action="store_true", help="Overwrite existing stubs")
    args = p.parse_args()

    name = args.name or args.city_slug.replace("-", " ").title()
    country = args.country or args.country_slug.replace("-", " ").title()
    scaffold(args.country_slug, args.city_slug, name, country, args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
