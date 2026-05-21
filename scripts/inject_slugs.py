#!/usr/bin/env python3
"""Idempotent: inject stable `slug` field into every entity entry in a city's
site-data, and normalise `location` -> `address` where applicable.

Usage:
    python scripts/inject_slugs.py france paris        # one city
    python scripts/inject_slugs.py --all               # every city in site-data/

Idempotent: re-runs do not overwrite existing slugs. New entries (added by
the food-research agent later) get their slug assigned here.

Topics processed (those with place-style entities):
    restaurants, fine-dining, casual-dining, cafes, bakeries,
    coffee-roasters, wine-bars, bars, street-food, breweries, markets,
    food-tours, festivals, cooking-classes, dietary, budget-eating,
    hidden-gems, brunch, late-night, day-trips-food, itineraries,
    signature-dishes (global dish slugs).

`location` -> `address` rename applies to: street-food, budget-eating,
hidden-gems entries.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.slug import slugify, unique_slug

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# topic_file -> top-level key inside the JSON
LIST_TOPICS = {
    "restaurants.json": "restaurants",
    "fine-dining.json": "fine_dining",
    "casual-dining.json": "casual_dining",
    "cafes.json": "cafes",
    "bakeries.json": "bakeries",
    "coffee-roasters.json": "coffee_roasters",
    "wine-bars.json": "wine_bars",
    "bars.json": "bars",
    "street-food.json": "street_food",
    "breweries.json": "breweries",
    "markets.json": "markets",
    "food-tours.json": "food_tours",
    "festivals.json": "food_festivals",
    "cooking-classes.json": "cooking_classes",
    "budget-eating.json": "budget_eating",
    "hidden-gems.json": "hidden_gems",
    "brunch.json": "brunch",
    "late-night.json": "late_night",
    "day-trips-food.json": "day_trips_food",
    "itineraries.json": "itineraries",
    "signature-dishes.json": "signature_dishes",
}

# Dietary is a dict-of-lists; treated separately.
DIETARY_FILE = "dietary.json"

# Files where the per-entry address field was historically named `location`.
LOCATION_RENAME_FILES = {"street-food.json", "budget-eating.json", "hidden-gems.json"}

# Entries with these top-level keys use `operator` as their canonical name.
NAME_FIELD_OVERRIDES = {
    "food_tours": "operator",  # tour entries have `operator` not `name`
}


def _entry_name(entry: dict, list_key: str) -> str:
    """Return the human name to slugify, by topic convention."""
    name_field = NAME_FIELD_OVERRIDES.get(list_key, "name")
    return entry.get(name_field) or entry.get("name") or ""


def process_list(entries: list, list_key: str, rename_location: bool) -> dict:
    """Mutate `entries` in place. Return counts: {slugs_added, renamed_location}."""
    if not isinstance(entries, list):
        return {"slugs_added": 0, "renamed_location": 0}

    existing_slugs = {e["slug"] for e in entries if isinstance(e, dict) and e.get("slug")}
    added = 0
    renamed = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if rename_location and "location" in entry and "address" not in entry:
            entry["address"] = entry.pop("location")
            renamed += 1
        if not entry.get("slug"):
            base = slugify(_entry_name(entry, list_key))
            if not base:
                # Cannot slugify: missing name. Leave for the validator to flag.
                continue
            entry["slug"] = unique_slug(base, existing_slugs)
            added += 1
    return {"slugs_added": added, "renamed_location": renamed}


def process_dietary(payload: dict) -> dict:
    """Dietary has shape {dietary: {vegan: [...], vegetarian: [...], ...}}."""
    totals = {"slugs_added": 0, "renamed_location": 0}
    dietary = payload.get("dietary")
    if not isinstance(dietary, dict):
        return totals
    for category, places in dietary.items():
        result = process_list(places, "dietary", rename_location=False)
        for k, v in result.items():
            totals[k] += v
    return totals


def process_city(country_slug: str, city_slug: str) -> dict:
    data_dir = SITE_DATA / country_slug / city_slug / "data"
    if not data_dir.exists():
        print(f"  SKIP: no data dir at {data_dir}")
        return {"slugs_added": 0, "renamed_location": 0, "files_touched": 0}

    totals = {"slugs_added": 0, "renamed_location": 0, "files_touched": 0}

    for filename, list_key in LIST_TOPICS.items():
        path = data_dir / filename
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get(list_key)
        before = json.dumps(payload, sort_keys=True)
        result = process_list(entries, list_key, rename_location=(filename in LOCATION_RENAME_FILES))
        after = json.dumps(payload, sort_keys=True)
        if before != after:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            totals["files_touched"] += 1
        totals["slugs_added"] += result["slugs_added"]
        totals["renamed_location"] += result["renamed_location"]

    # Dietary (dict-of-lists)
    dpath = data_dir / DIETARY_FILE
    if dpath.exists():
        payload = json.loads(dpath.read_text(encoding="utf-8"))
        before = json.dumps(payload, sort_keys=True)
        result = process_dietary(payload)
        after = json.dumps(payload, sort_keys=True)
        if before != after:
            dpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            totals["files_touched"] += 1
        totals["slugs_added"] += result["slugs_added"]

    return totals


def all_cities() -> list:
    """Walk SITE_DATA and return (country_slug, city_slug) pairs."""
    out = []
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir():
                continue
            if (city_dir / "data" / "region.json").exists():
                out.append((country_dir.name, city_dir.name))
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("country_slug", nargs="?")
    p.add_argument("city_slug", nargs="?")
    p.add_argument("--all", action="store_true", help="Process every city")
    args = p.parse_args()

    if args.all:
        cities = all_cities()
    elif args.country_slug and args.city_slug:
        cities = [(args.country_slug, args.city_slug)]
    else:
        p.error("Pass <country> <city> or --all")
        return 2

    grand_totals = {"slugs_added": 0, "renamed_location": 0, "files_touched": 0, "cities": 0}
    for country, city in cities:
        print(f"{country}/{city}")
        totals = process_city(country, city)
        for k in ("slugs_added", "renamed_location", "files_touched"):
            grand_totals[k] += totals[k]
        grand_totals["cities"] += 1
        print(
            f"  slugs_added={totals['slugs_added']}  "
            f"renamed_location={totals['renamed_location']}  "
            f"files_touched={totals['files_touched']}"
        )

    print("")
    print(f"DONE: {grand_totals['cities']} cities, "
          f"{grand_totals['slugs_added']} slugs added, "
          f"{grand_totals['renamed_location']} location->address, "
          f"{grand_totals['files_touched']} files written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
