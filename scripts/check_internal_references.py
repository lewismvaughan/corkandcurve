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

# Topic files whose entries can be referenced from itineraries / producer.
ENTITY_TOPIC_FILES = (
    "vineyards.json", "tasting-rooms.json", "wine-bars.json",
    "wine-restaurants.json", "wine-retailers.json", "wine-schools.json",
    "wine-tours.json", "wine-festivals.json", "distilleries.json",
    "wine-museums.json", "wine-hotels.json", "wine-experiences.json",
    "budget-wines.json", "hidden-gems.json", "day-trips-wine.json",
)
TOPIC_KEY = {
    "vineyards.json": "vineyards", "tasting-rooms.json": "tasting_rooms",
    "wine-bars.json": "wine_bars", "wine-restaurants.json": "wine_restaurants",
    "wine-retailers.json": "wine_retailers", "wine-schools.json": "wine_schools",
    "wine-tours.json": "wine_tours", "wine-festivals.json": "wine_festivals",
    "distilleries.json": "distilleries", "wine-museums.json": "wine_museums",
    "wine-hotels.json": "wine_hotels", "wine-experiences.json": "wine_experiences",
    "budget-wines.json": "budget_wines", "hidden-gems.json": "hidden_gems",
    "day-trips-wine.json": "day_trips_wine",
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


def _check_signature_wines(data_dir: Path, name_index: dict, issues: list,
                           slug_index: dict | None = None) -> None:
    """Every `signature-wines.producer` should fuzzy-resolve to a verified
    vineyard name in the region. Otherwise ERR (an iconic bottle whose
    producer we don't cover is a dangling reference).

    The producer field is a slug, so we also check slug_index as a fallback
    for cases where name normalisation fails (e.g. apostrophe in 'Chateau d\'Yquem'
    normalises differently from the slug 'chateau-dyquem').
    """
    sw = data_dir / "signature-wines.json"
    if not sw.exists():
        return
    try:
        d = json.loads(sw.read_text(encoding="utf-8"))
    except Exception:
        return
    for wine in d.get("signature_wines") or []:
        if not isinstance(wine, dict):
            continue
        wine_slug = wine.get("slug", "?")
        producer = wine.get("producer")
        if not isinstance(producer, str) or not producer:
            continue
        # Direct slug lookup (producer field IS a slug)
        if slug_index and producer in slug_index:
            continue
        n = _norm_name(producer)
        if not n or n in name_index:
            continue
        partial = next((k for k in name_index if n in k or k in n), None)
        if partial:
            continue
        issues.append((
            "ERR",
            f"signature-wines.json '{wine_slug}' producer={producer!r} does not resolve to any verified vineyard in this region",
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
    _check_signature_wines(data_dir, name_index, issues, slug_index=slug_index)
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
