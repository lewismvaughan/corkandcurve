#!/usr/bin/env python3
"""Cross-reference checker: every venue named in itineraries or
signature-dishes.where_to_eat must resolve to a real verified entity
elsewhere in the same city.

This closes the last gap in the provenance architecture: the `verified`
block proves each entity exists, but until now nothing checked that
venue names *referenced* in editorial content (itinerary prose,
signature-dish "where to eat" lists) point to those same verified
entities. A research agent could write a perfectly clean entity for
"Joe's Bistro" and then invent "Mary's Cafe" in an itinerary, and only
the live audit (or a reader) would notice.

Checks per city:
  1. For each entry in `signature-dishes.where_to_eat[*]` (a list of
     venue names), fuzzy-match the name against the city's verified
     entity-name index. Unresolved names = ERR.
  2. For each `itineraries[*].days[*].venues[*]` (a list of slugs,
     required field), confirm the slug exists in the city's verified
     entity-slug index. Unresolved slugs = ERR. Missing `venues` field
     entirely = WARN until backfill is complete.

Usage:
    python3 scripts/check_internal_references.py --country france --city paris
    python3 scripts/check_internal_references.py --all

Exit 0 if no unresolved references, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# Topic files whose entries can be referenced from itineraries / where_to_eat.
ENTITY_TOPIC_FILES = (
    "restaurants.json", "fine-dining.json", "casual-dining.json",
    "cafes.json", "bakeries.json", "coffee-roasters.json", "wine-bars.json",
    "bars.json", "street-food.json", "breweries.json", "markets.json",
    "food-tours.json", "festivals.json", "cooking-classes.json",
    "budget-eating.json", "hidden-gems.json", "brunch.json", "late-night.json",
    "day-trips-food.json",
)
TOPIC_KEY = {
    "restaurants.json": "restaurants", "fine-dining.json": "fine_dining",
    "casual-dining.json": "casual_dining", "cafes.json": "cafes",
    "bakeries.json": "bakeries", "coffee-roasters.json": "coffee_roasters",
    "wine-bars.json": "wine_bars", "bars.json": "bars",
    "street-food.json": "street_food", "breweries.json": "breweries",
    "markets.json": "markets", "food-tours.json": "food_tours",
    "festivals.json": "food_festivals", "cooking-classes.json": "cooking_classes",
    "budget-eating.json": "budget_eating", "hidden-gems.json": "hidden_gems",
    "brunch.json": "brunch", "late-night.json": "late_night",
    "day-trips-food.json": "day_trips_food",
}

_NAME_NORM_RE = re.compile(r"[^a-z0-9]+")


def _norm_name(s: str) -> str:
    """Aggressive normalization for name fuzzy-matching. Lowercase, strip
    punctuation, collapse whitespace, drop common parenthetical suffixes
    like '(Lincoln Park)' that distinguish locations of a chain."""
    if not s:
        return ""
    s = s.lower()
    # Drop parenthetical suffixes
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    s = _NAME_NORM_RE.sub(" ", s).strip()
    return s


def _build_index(data_dir: Path) -> tuple[dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    """Returns (name_index, slug_index). Both map their key to (topic_file, slug).
    Only entities with a `verified` block are indexed — references to
    unverified entities are themselves unverified.
    """
    name_index: dict[str, tuple[str, str]] = {}
    slug_index: dict[str, tuple[str, str]] = {}

    for fn in ENTITY_TOPIC_FILES:
        path = data_dir / fn
        if not path.exists():
            continue
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        key = TOPIC_KEY[fn]
        entries = d.get(key) or []
        if not isinstance(entries, list):
            continue
        for e in entries:
            if not isinstance(e, dict) or "verified" not in e:
                continue
            slug = e.get("slug")
            name = e.get("name") or e.get("operator")
            if slug:
                slug_index[slug] = (fn, slug)
            if name:
                name_index[_norm_name(name)] = (fn, slug or "")

    # Also walk dietary.json (DICT shape)
    dietary = data_dir / "dietary.json"
    if dietary.exists():
        try:
            d = json.loads(dietary.read_text(encoding="utf-8"))
        except Exception:
            d = None
        if isinstance(d, dict):
            for sub, entries in (d.get("dietary") or {}).items():
                if isinstance(entries, list):
                    for e in entries:
                        if not isinstance(e, dict) or "verified" not in e:
                            continue
                        slug = e.get("slug")
                        name = e.get("name")
                        if slug:
                            slug_index[slug] = ("dietary.json", slug)
                        if name:
                            name_index[_norm_name(name)] = ("dietary.json", slug or "")
    return name_index, slug_index


def _check_signature_dishes(data_dir: Path, name_index: dict, issues: list) -> None:
    """Every entry in `signature-dishes.where_to_eat[*]` must fuzzy-resolve
    to a verified entity name in the city. Otherwise ERR."""
    sd = data_dir / "signature-dishes.json"
    if not sd.exists():
        return
    try:
        d = json.loads(sd.read_text(encoding="utf-8"))
    except Exception:
        return
    for dish in d.get("signature_dishes") or []:
        if not isinstance(dish, dict):
            continue
        dish_slug = dish.get("slug", "?")
        for venue in dish.get("where_to_eat") or []:
            if not isinstance(venue, str):
                continue
            n = _norm_name(venue)
            if not n:
                continue
            if n in name_index:
                continue
            # Try partial match — venue name might include extra qualifier
            partial = next((k for k in name_index if n in k or k in n), None)
            if partial:
                continue
            issues.append((
                "ERR",
                f"signature-dishes.json '{dish_slug}' where_to_eat={venue!r} does not resolve to any verified entity in this city",
            ))


def _check_itineraries(data_dir: Path, slug_index: dict, issues: list) -> None:
    """Each itinerary day SHOULD list `venues: [slug, ...]`. Each slug must
    resolve to a verified entity in the city. Missing `venues` is WARN
    until backfill."""
    it = data_dir / "itineraries.json"
    if not it.exists():
        return
    try:
        d = json.loads(it.read_text(encoding="utf-8"))
    except Exception:
        return
    for itin in d.get("itineraries") or []:
        if not isinstance(itin, dict):
            continue
        itin_slug = itin.get("slug", "?")
        for day in itin.get("days") or []:
            if not isinstance(day, dict):
                continue
            day_n = day.get("day_number", "?")
            venues = day.get("venues")
            if venues is None:
                issues.append((
                    "WARN",
                    f"itineraries.json '{itin_slug}' day {day_n} missing 'venues' list (research agent should list slugs of venues mentioned in prose)",
                ))
                continue
            if not isinstance(venues, list):
                issues.append((
                    "ERR",
                    f"itineraries.json '{itin_slug}' day {day_n} venues={venues!r} must be a list of slugs",
                ))
                continue
            for slug in venues:
                if not isinstance(slug, str) or not slug:
                    issues.append((
                        "ERR",
                        f"itineraries.json '{itin_slug}' day {day_n} venues entry {slug!r} is not a valid slug string",
                    ))
                    continue
                if slug not in slug_index:
                    issues.append((
                        "ERR",
                        f"itineraries.json '{itin_slug}' day {day_n} venues references slug={slug!r} but no verified entity with that slug exists in this city",
                    ))


def check_city(country: str, city: str) -> int:
    data_dir = SITE_DATA / country / city / "data"
    if not data_dir.exists():
        print(f"[{country}/{city}] no such city")
        return 1
    name_index, slug_index = _build_index(data_dir)
    issues: list[tuple[str, str]] = []
    _check_signature_dishes(data_dir, name_index, issues)
    _check_itineraries(data_dir, slug_index, issues)
    print(f"[{country}/{city}] verified-entity index: {len(name_index)} names, {len(slug_index)} slugs")
    errs = sum(1 for lvl, _ in issues if lvl == "ERR")
    warns = sum(1 for lvl, _ in issues if lvl == "WARN")
    for lvl, msg in issues:
        print(f"  {lvl}: {msg}")
    print(f"[{country}/{city}] ERR={errs} WARN={warns}")
    return 1 if errs else 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    if args.all:
        targets = []
        for country_dir in sorted(SITE_DATA.iterdir()):
            if not country_dir.is_dir():
                continue
            for city_dir in sorted(country_dir.iterdir()):
                if (city_dir / "data").exists():
                    targets.append((country_dir.name, city_dir.name))
    elif args.country and args.city:
        targets = [(args.country, args.city)]
    else:
        p.error("Pass --all or both --country and --city")
        return 2

    total_err = 0
    for country, city in targets:
        rc = check_city(country, city)
        total_err += rc
    print(f"\nCities with ERRs: {total_err}/{len(targets)}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
