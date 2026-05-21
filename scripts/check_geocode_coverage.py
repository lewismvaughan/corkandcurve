#!/usr/bin/env python3
"""Soft-fail geocode coverage check for ship_city.sh.

Walks every entity in a city (or all cities) and counts how many have a
geocode cache hit. Prints a per-city summary and a list of entities
without coords so an editor can refine the address.

Exit codes:
  0 — coverage above threshold OR --soft mode (always 0; just report)
  1 — coverage below threshold (only in --hard mode)

Usage:
  python scripts/check_geocode_coverage.py france paris
  python scripts/check_geocode_coverage.py --all
  python scripts/check_geocode_coverage.py france paris --hard --threshold 0.9
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
GEOCODE_CACHE = REPO / "data" / "geocode-cache.json"

ENTITY_TOPICS = {
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
}


def _cache_key(address: str, city_name: str) -> str:
    blob = f"{address.lower().strip()}|{city_name.lower().strip()}"
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def _walk(country_slug: str, city_slug: str) -> list[tuple[str, str, str]]:
    """Yield (topic, slug, address) for every entity with an address."""
    data_dir = SITE_DATA / country_slug / city_slug / "data"
    out: list[tuple[str, str, str]] = []
    for filename, key in ENTITY_TOPICS.items():
        p = data_dir / filename
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in (d.get(key) or []):
            if not isinstance(e, dict):
                continue
            addr = e.get("address") or e.get("location") or e.get("meeting_point")
            slug = e.get("slug")
            if slug and addr:
                out.append((key, slug, addr))
    # Dietary nested dict
    p = data_dir / "dietary.json"
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            for diet, entries in (d.get("dietary") or {}).items():
                if not isinstance(entries, list):
                    continue
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    if e.get("slug") and e.get("address"):
                        out.append((f"dietary.{diet}", e["slug"], e["address"]))
        except (OSError, json.JSONDecodeError):
            pass
    return out


def _city_name(country_slug: str, city_slug: str) -> str:
    rj = SITE_DATA / country_slug / city_slug / "data" / "region.json"
    if not rj.exists():
        return city_slug.replace("-", " ").title()
    try:
        return (json.loads(rj.read_text(encoding="utf-8")).get("destination") or {}).get("name") or city_slug.replace("-", " ").title()
    except (OSError, json.JSONDecodeError):
        return city_slug.replace("-", " ").title()


def check(country_slug: str, city_slug: str, cache: dict) -> dict:
    city_name = _city_name(country_slug, city_slug)
    entities = _walk(country_slug, city_slug)
    if not entities:
        return {"city": city_name, "total": 0, "geocoded": 0, "coverage": 1.0, "missing": []}

    geocoded = 0
    missing: list[tuple[str, str, str]] = []
    for topic, slug, addr in entities:
        ck = _cache_key(addr, city_name)
        entry = cache.get(ck)
        if entry and entry.get("ok"):
            geocoded += 1
        else:
            missing.append((topic, slug, addr))
    return {
        "city": city_name,
        "total": len(entities),
        "geocoded": geocoded,
        "coverage": geocoded / len(entities) if entities else 1.0,
        "missing": missing,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("country", nargs="?")
    p.add_argument("city", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--hard", action="store_true",
                   help="Exit non-zero if coverage < threshold (default soft: always exit 0)")
    p.add_argument("--threshold", type=float, default=0.85,
                   help="Min acceptable geocode coverage in hard mode (default 0.85)")
    args = p.parse_args()

    if not GEOCODE_CACHE.exists():
        print("[WARN] no geocode cache found; nothing to check.")
        return 0
    try:
        cache = json.loads(GEOCODE_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERR] could not read geocode cache: {exc}")
        return 1

    targets: list[tuple[str, str]] = []
    if args.all:
        for country_dir in sorted(SITE_DATA.iterdir()):
            if not country_dir.is_dir():
                continue
            for city_dir in sorted(country_dir.iterdir()):
                if not city_dir.is_dir() or city_dir.name == "data":
                    continue
                if (city_dir / "data" / "region.json").exists():
                    targets.append((country_dir.name, city_dir.name))
    elif args.country and args.city:
        targets.append((args.country, args.city))
    else:
        print("Usage: check_geocode_coverage.py <country> <city>  |  --all")
        return 2

    worst_coverage = 1.0
    for country, city in targets:
        rep = check(country, city, cache)
        bar = "[" + ("#" * round(rep["coverage"] * 20)).ljust(20) + "]"
        print(f"{bar} {rep['coverage']:.0%}  {rep['city']:20}  ({rep['geocoded']}/{rep['total']})")
        if rep["missing"] and len(targets) == 1:
            print(f"\n  {len(rep['missing'])} entities still need a refined address:")
            for topic, slug, addr in rep["missing"][:30]:
                print(f"    {topic:25} {slug:35} {addr}")
            if len(rep["missing"]) > 30:
                print(f"    ... and {len(rep['missing']) - 30} more")
        worst_coverage = min(worst_coverage, rep["coverage"])

    if args.hard and worst_coverage < args.threshold:
        print(f"\nBLOCKED: coverage {worst_coverage:.0%} below threshold {args.threshold:.0%}")
        print("Refine the missing addresses (or mark them inherently un-geocodable) before shipping.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
