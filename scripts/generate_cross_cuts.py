#!/usr/bin/env python3
"""Generate cross-cut landing pages by aggregating entities across all cities.

Emits:
    /cuisine/<cuisine-slug>/               cuisine landing (global)
    /dish/<dish-slug>/                     signature-dish landing (global)
    /neighborhood/<city-slug>/<hood>/      neighborhood landing (city-scoped)

Re-runnable; rewrites pages every run.

Usage:
    python scripts/generate_cross_cuts.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.cuisine import canonicalise as _canon_cuisine
from utils.data_loader import (
    SITE_DATA,
    load_country_data,
    get_all_countries,
    get_all_regions,
)
from utils.seo import meta_desc as _meta_desc
from utils.slug import slugify
from utils.template_renderer import TemplateRenderer

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BASE = "https://tablejourney.com"

TOPIC_DISPLAY = {
    "restaurants": "Restaurants",
    "fine-dining": "Fine Dining",
    "casual-dining": "Casual Dining",
    "cafes": "Cafés",
    "bakeries": "Bakeries",
    "coffee-roasters": "Coffee Roasters",
    "wine-bars": "Wine Bars",
    "bars": "Bars",
    "street-food": "Street Food",
    "breweries": "Breweries",
    "markets": "Markets",
    "food-tours": "Food Tours",
    "festivals": "Food Festivals",
    "cooking-classes": "Cooking Classes",
    "budget-eating": "Budget Eats",
    "hidden-gems": "Hidden Gems",
    "brunch": "Brunch",
    "late-night": "Late-Night Eats",
    "day-trips-food": "Food Day Trips",
}

# research-key -> topic-slug (only entity-bearing list topics)
RESEARCH_KEY_TO_TOPIC = {
    "restaurants": "restaurants",
    "fine_dining": "fine-dining",
    "casual_dining": "casual-dining",
    "cafes": "cafes",
    "bakeries": "bakeries",
    "coffee_roasters": "coffee-roasters",
    "wine_bars": "wine-bars",
    "bars": "bars",
    "street_food": "street-food",
    "breweries": "breweries",
    "markets": "markets",
    "food_tours": "food-tours",
    "food_festivals": "festivals",
    "cooking_classes": "cooking-classes",
    "budget_eating": "budget-eating",
    "hidden_gems": "hidden-gems",
    "brunch": "brunch",
    "late_night": "late-night",
    "day_trips_food": "day-trips-food",
}


def _seo_block(canonical: str, title: str, description: str) -> dict:
    if len(description) > 165:
        description = description[:162].rstrip() + "..."
    return {
        "meta": {
            "title": title,
            "description": description,
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large, max-snippet:-1",
        },
        "open_graph": {
            "og_title": title,
            "og_description": description,
            "og_image": f"{BASE}/og/default.jpg",
            "og_image_alt": "TableJourney food guide",
            "og_url": canonical,
            "og_type": "article",
            "og_locale": "en_US",
        },
        "twitter": {},
        "alternates": [],
    }


def _analytics(page_type: str, slug: str) -> dict:
    return {
        "page_type": page_type,
        "destination": slug,
        "country": "", "region": "",
        "context": f"{page_type}:{slug}",
    }


def _all_country_region_pairs() -> list:
    """Walk site-data/ and return (country_slug, region_slug) for every
    city with a region.json. Includes country-level cities (region_slug=None).
    Doesn't require a country-level region.json to recurse into regions.
    """
    pairs = []
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        if (country_dir / "data" / "region.json").exists():
            pairs.append((country, None))
        for region_dir in sorted(country_dir.iterdir()):
            if region_dir.is_dir() and region_dir.name != "data" and (region_dir / "data" / "region.json").exists():
                pairs.append((country, region_dir.name))
    return pairs


def collect_all() -> dict:
    """Walk every city, return aggregated structures.

    Resilient to per-city failures: a single bad city (malformed JSON,
    missing file, broken encoding) is logged and skipped, the rest of the
    aggregation still produces a complete cross-cut set. Without this, one
    subagent's bad output would break /cuisine/, /dish/, and
    /neighborhood/ for every city.
    """
    cities_data = []
    for country, region in _all_country_region_pairs():
        try:
            data = load_country_data(country, region_slug=region)
        except (FileNotFoundError, ValueError, OSError) as exc:
            print(f"  [WARN] skipping {country}/{region or '-'}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - log + skip, don't poison the whole run
            print(f"  [WARN] skipping {country}/{region or '-'}: unexpected error: {exc}")
            continue
        cities_data.append({
            "country_slug": country,
            "city_slug": region or country,
            "city_name": data.get("destination", {}).get("name", (region or country).title()),
            "data": data,
        })

    by_cuisine: dict[str, dict] = defaultdict(lambda: {"display": "", "cities": defaultdict(list)})
    by_dish: dict[str, dict] = defaultdict(lambda: {
        "display": "", "description": "", "history": "",
        "allergens": [], "where_to_eat": defaultdict(list),
        "make_it_yourself": None,
    })
    by_neighborhood: dict[tuple, dict] = defaultdict(lambda: {
        "display": "", "vibe": "", "city_name": "", "city_slug": "", "country_slug": "",
        "entities_by_topic": defaultdict(list),
    })

    unmapped_cuisines: dict[str, list[str]] = {}
    for city in cities_data:
        research = city["data"].get("research", {})
        # cuisine: from restaurants[].cuisine + casual_dining[].cuisine
        # All raw cuisine strings go through the controlled vocab; unknown
        # values are logged (not silently slug-fragmented into their own page).
        for rk in ("restaurants", "casual_dining", "fine_dining"):
            for r in research.get(rk, []) or []:
                if not isinstance(r, dict) or not r.get("cuisine"):
                    continue
                cc = _canon_cuisine(r["cuisine"])
                if cc is None:
                    unmapped_cuisines.setdefault(r["cuisine"], []).append(
                        f"{city['country_slug']}/{city['city_slug']}:{r.get('slug') or r.get('name', '?')}"
                    )
                    continue
                cb = by_cuisine[cc.slug]
                cb["display"] = cc.display
                cb["cities"][(city["country_slug"], city["city_slug"], city["city_name"])].append(r)

        # dishes: from signature_dishes[]
        for d in research.get("signature_dishes", []) or []:
            if not isinstance(d, dict) or not d.get("slug"):
                continue
            ds = d["slug"]
            slot = by_dish[ds]
            slot["display"] = d.get("name", ds)
            slot["description"] = slot["description"] or d.get("description", "")
            slot["history"] = slot["history"] or d.get("history", "")
            if d.get("allergens") and not slot["allergens"]:
                slot["allergens"] = d["allergens"]
            if d.get("make_it_yourself") and not slot["make_it_yourself"]:
                slot["make_it_yourself"] = d["make_it_yourself"]
            # where_to_eat references restaurant/venue names. The dish
            # might be made famous by a bistro (restaurants), a street stall
            # (street_food), a bakery (cafes), a budget bouillon
            # (budget_eating), etc. Resolve names across every venue-style
            # topic in the city so a falafel-sandwich reference to
            # "L'As du Fallafel" (in street_food.json) lands on the dish
            # card. Index is keyed by (city_slug, name) so name collisions
            # across cities don't shadow each other at multi-city scale.
            venue_index = {}
            for venue_key in (
                "restaurants", "casual_dining", "fine_dining",
                "cafes", "bakeries", "coffee_roasters", "wine_bars",
                "bars", "street_food", "breweries",
                "markets", "budget_eating", "hidden_gems",
                "brunch", "late_night",
            ):
                for r in research.get(venue_key) or []:
                    if isinstance(r, dict) and r.get("name"):
                        venue_index[r["name"]] = r
            resolved = [venue_index[name] for name in (d.get("where_to_eat") or []) if name in venue_index]
            slot["where_to_eat"][(city["country_slug"], city["city_slug"], city["city_name"])].extend(resolved)

        # neighborhoods: walk every entity-bearing topic, group by entity.neighborhood
        for rk, topic_slug in RESEARCH_KEY_TO_TOPIC.items():
            for e in research.get(rk, []) or []:
                if not isinstance(e, dict) or not e.get("neighborhood"):
                    continue
                nslug = slugify(e["neighborhood"])
                if not nslug:
                    continue
                key = (city["city_slug"], nslug)
                slot = by_neighborhood[key]
                slot["display"] = e["neighborhood"].split("(")[0].strip()
                slot["city_name"] = city["city_name"]
                slot["city_slug"] = city["city_slug"]
                slot["country_slug"] = city["country_slug"]
                slot["entities_by_topic"][topic_slug].append(e)

        # Attach vibe + editorial display name from neighborhoods.json. Each
        # editorial entry may list `aliases` (entity.neighborhood values that
        # belong to it). When an alias matches an arr-code cross-cut, the
        # cross-cut adopts the editorial name (e.g. "3e" -> "Le Marais (3e)").
        for n in research.get("neighborhoods", []) or []:
            if not isinstance(n, dict) or not n.get("name"):
                continue
            aliases = n.get("aliases") or []
            for alias in aliases:
                key = (city["city_slug"], alias)
                if key not in by_neighborhood:
                    continue
                if n.get("vibe"):
                    by_neighborhood[key]["vibe"] = n["vibe"]
                by_neighborhood[key]["display"] = f"{n['name']} ({alias})"
            # Fallback for cities that haven't adopted aliases yet: match by slug.
            if not aliases:
                ns = slugify(n["name"])
                key = (city["city_slug"], ns)
                if key in by_neighborhood and n.get("vibe"):
                    by_neighborhood[key]["vibe"] = n["vibe"]

    return {
        "cuisine": by_cuisine,
        "dish": by_dish,
        "neighborhood": by_neighborhood,
        "unmapped_cuisines": unmapped_cuisines,
    }


def write_cuisine_pages(renderer: TemplateRenderer, by_cuisine: dict) -> int:
    template = renderer.env.get_template("cross-cuts/cuisine.html")
    count = 0
    for slug, blob in by_cuisine.items():
        cities_list = []
        total = 0
        for (country, city_slug, city_name), restaurants in blob["cities"].items():
            cities_list.append({
                "country_slug": country,
                "city_slug": city_slug,
                "city_name": city_name,
                "restaurants": restaurants,
            })
            total += len(restaurants)
        cities_list.sort(key=lambda c: c["city_name"])
        cuisine_display = blob["display"]

        canonical = f"{BASE}/cuisine/{slug}/"
        title = f"{cuisine_display} Restaurants Around the World | TableJourney"
        n_cities = len(cities_list)
        city_phrase = "1 city" if n_cities == 1 else f"{n_cities} cities"
        cl = cuisine_display.lower()
        desc = _meta_desc(
            f"Editor-picked {cl} rooms across {city_phrase} on TableJourney. Where to sit, what to order, what each kitchen does best and how to book without losing the meal.",
            f"Editor-picked {cl} rooms across {city_phrase} on TableJourney. Where to sit, what to order, what each kitchen does best and how to book.",
            f"Editor-picked {cl} rooms across {city_phrase} on TableJourney. Where to sit, what to order and how to book without losing the meal.",
            f"Editor-picked {cl} rooms across {city_phrase} on TableJourney. Where to sit, what to order and how to book.",
        )

        ctx = {
            "cuisine": cuisine_display,
            "cuisine_slug": slug,
            "cities": cities_list,
            "total_entities": total,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "Cuisines", "url": "/cuisines/"},
                {"name": cuisine_display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": cuisine_display, "country": ""},
            "analytics": _analytics("cuisine", slug),
            "base_path": "../..",
        }
        html = template.render(**ctx)
        out = CONTENT_DIR / "cuisine" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        count += 1
    return count


def write_dish_pages(renderer: TemplateRenderer, by_dish: dict) -> int:
    template = renderer.env.get_template("cross-cuts/dish.html")
    count = 0
    for slug, blob in by_dish.items():
        where_list = []
        total_r = 0
        for (country, city_slug, city_name), restaurants in blob["where_to_eat"].items():
            where_list.append({
                "country_slug": country,
                "city_slug": city_slug,
                "city_name": city_name,
                "restaurants": restaurants,
            })
            total_r += len(restaurants)
        where_list.sort(key=lambda c: c["city_name"])
        display = blob["display"]

        canonical = f"{BASE}/dish/{slug}/"
        title = f"{display}: where to eat it | TableJourney"
        n_cities = len(where_list)
        city_phrase = "1 city" if n_cities == 1 else f"{n_cities} cities"
        dl = display.lower()
        base = (blob["description"] or "").strip().rstrip(".")
        if base:
            stem = f"{base}."
            desc = _meta_desc(
                f"{stem} Where to eat the canonical {dl} in {city_phrase} we cover on TableJourney, with editor-picked rooms, how to order and what to skip.",
                f"{stem} Where to eat the canonical {dl} in {city_phrase} we cover, with editor-picked rooms and how to order on TableJourney.",
                f"{stem} Where to eat the canonical {dl} in {city_phrase} we cover on TableJourney, room by room.",
                f"{stem} Where to eat the canonical {dl} in {city_phrase} we cover on TableJourney.",
                f"{stem} Where to eat the canonical version in {city_phrase} we cover on TableJourney.",
                f"{stem} Where to eat the canonical version on TableJourney, room by room.",
                f"{stem} Where to eat the canonical version on TableJourney.",
                f"{stem} Where to eat it on TableJourney, room by room.",
                f"{stem} Where to eat it on TableJourney.",
                # Short tails for the case where the base description alone is
                # already ~130 chars: any longer suffix blows past 165, but
                # the bare stem under-shoots the 140 floor. These two land
                # in band for stems in the 110-145 char range.
                f"{stem} Editor pick on TableJourney with where to eat it.",
                f"{stem} On TableJourney, room by room.",
                f"{stem} On TableJourney.",
                f"{stem}",
            )
        else:
            desc = _meta_desc(
                f"{display}: what the dish is, where it comes from, and where to eat the canonical version in {city_phrase} we cover on TableJourney, room by room.",
                f"{display}: what the dish is, where it comes from, and where to eat the canonical version in {city_phrase} we cover on TableJourney.",
                f"{display}: what the dish is, where it comes from and where to eat the canonical version on TableJourney.",
                f"{display}: what the dish is and where to eat the canonical version in {city_phrase} we cover on TableJourney.",
            )

        ctx = {
            "dish": display,
            "dish_slug": slug,
            "description": blob["description"],
            "history": blob["history"],
            "allergens": blob["allergens"],
            "make_it_yourself": blob["make_it_yourself"],
            "where_to_eat": where_list,
            "total_restaurants": total_r,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "Dishes", "url": "/dishes/"},
                {"name": display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": display, "country": ""},
            "analytics": _analytics("dish", slug),
            "base_path": "../..",
        }
        html = template.render(**ctx)
        out = CONTENT_DIR / "dish" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        count += 1
    return count


def write_neighborhood_pages(renderer: TemplateRenderer, by_neighborhood: dict) -> int:
    template = renderer.env.get_template("cross-cuts/neighborhood.html")
    count = 0
    for (city_slug, hood_slug), blob in by_neighborhood.items():
        total = sum(len(v) for v in blob["entities_by_topic"].values())
        canonical = f"{BASE}/neighborhood/{city_slug}/{hood_slug}/"
        display = blob["display"]
        city_name = blob["city_name"]
        title = f"Eat in {display}, {city_name} | TableJourney"
        vibe = (blob["vibe"] or "").strip().rstrip(".")
        if vibe:
            desc = _meta_desc(
                f"{vibe}. The restaurants, cafes, bars and markets in {display}, {city_name}, editor-picked by TableJourney with what to order and how to book.",
                f"{vibe}. The restaurants, cafes, bars and markets in {display}, {city_name}, editor-picked by TableJourney.",
                f"{vibe}. The restaurants, cafes, bars and markets in {display}, {city_name}, on TableJourney.",
                f"{vibe}. Editor-picked rooms in {display}, {city_name}, on TableJourney.",
                f"{vibe}.",
            )
        else:
            desc = _meta_desc(
                f"Where to eat in {display}, {city_name}: the restaurants, cafes, bars, markets and bakeries editor-picked by TableJourney with what to order and how to book.",
                f"Where to eat in {display}, {city_name}: the restaurants, cafes, bars and markets editor-picked by TableJourney, with what to order and how to book.",
                f"Where to eat in {display}, {city_name}: restaurants, cafes, bars and markets editor-picked by TableJourney with what to order.",
                f"Where to eat in {display}, {city_name}: restaurants, cafes, bars and markets editor-picked by TableJourney.",
            )

        ctx = {
            "neighborhood": display,
            "neighborhood_slug": hood_slug,
            "city_name": city_name,
            "city_slug": city_slug,
            "country_slug": blob["country_slug"],
            "vibe": blob["vibe"],
            "entities_by_topic": dict(blob["entities_by_topic"]),
            "topic_display": TOPIC_DISPLAY,
            "total_entities": total,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "Neighbourhoods", "url": "/neighborhoods/"},
                {"name": city_name, "url": f"/{blob['country_slug']}/{city_slug}/"},
                {"name": display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": city_name, "country": ""},
            "analytics": _analytics("neighborhood", f"{city_slug}-{hood_slug}"),
            "base_path": "../../..",
        }
        html = template.render(**ctx)
        out = CONTENT_DIR / "neighborhood" / city_slug / hood_slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        count += 1
    return count


def _write_manifest(parent_dir: Path, entries: list[dict]) -> None:
    """Drop a flat JSON manifest of every cross-cut page under `parent_dir`.

    Read by generate_chrome_pages.py to build the /cuisines/, /dishes/,
    /neighborhoods/ index pages without having to open and regex every
    individual cross-cut HTML. At 100k cross-cuts that file-open loop is
    the difference between a multi-minute chrome regen and a one-second one.

    Schema: { "entries": [{"slug": ..., "display": ..., ... per-type extras}] }
    """
    import json as _json
    parent_dir.mkdir(parents=True, exist_ok=True)
    payload = {"entries": entries}
    (parent_dir / "_manifest.json").write_text(
        _json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _prune_stale(parent: Path, keep_slugs: set[str], *, two_level: bool = False) -> int:
    """Delete cross-cut directories under `parent` whose slug is not in
    `keep_slugs`. Used to drop orphans when a cuisine/dish/neighborhood
    stops appearing (e.g. canonicalisation collapsed two slugs into one,
    or a city removed an entry).

    `two_level=True` for neighborhood, where the dir layout is
    content/neighborhood/<city>/<hood>/ and the slug key is "<city>/<hood>".

    Returns number of pruned dirs.
    """
    import shutil as _shutil
    if not parent.exists():
        return 0
    pruned = 0
    if two_level:
        for city_dir in parent.iterdir():
            if not city_dir.is_dir():
                continue
            for hood_dir in list(city_dir.iterdir()):
                if not hood_dir.is_dir():
                    continue
                key = f"{city_dir.name}/{hood_dir.name}"
                if key not in keep_slugs:
                    _shutil.rmtree(hood_dir)
                    pruned += 1
            # If the city dir is empty after pruning, drop it too.
            if not any(city_dir.iterdir()):
                city_dir.rmdir()
        return pruned
    for sub in list(parent.iterdir()):
        if sub.is_dir() and sub.name not in keep_slugs:
            _shutil.rmtree(sub)
            pruned += 1
    return pruned


def main() -> int:
    print("Collecting cross-cut data from all cities...")
    agg = collect_all()
    renderer = TemplateRenderer()

    n_c = write_cuisine_pages(renderer, agg["cuisine"])
    n_d = write_dish_pages(renderer, agg["dish"])
    n_n = write_neighborhood_pages(renderer, agg["neighborhood"])

    # Prune stale cross-cut directories (orphans from removed entries or
    # canonicalisation collapses). Critical for SEO: leaving orphaned
    # URLs serving 200 creates duplicate-content liability.
    pruned_c = _prune_stale(CONTENT_DIR / "cuisine", set(agg["cuisine"].keys()))
    pruned_d = _prune_stale(CONTENT_DIR / "dish", set(agg["dish"].keys()))
    pruned_n = _prune_stale(
        CONTENT_DIR / "neighborhood",
        {f"{c}/{h}" for (c, h) in agg["neighborhood"].keys()},
        two_level=True,
    )

    # Write manifests so chrome-page indexes can be assembled cheaply.
    # Each entry carries a `cities` list so country-scoped + city-scoped
    # indexes can be built by filtering the same manifest. `n` is the
    # entity count in that city (for sort-by-coverage display).
    cuisine_entries = []
    for s, b in sorted(agg["cuisine"].items()):
        cities = [
            {
                "country_slug": country,
                "city_slug": city_slug,
                "city_name": city_name,
                "n": len(restaurants),
            }
            for (country, city_slug, city_name), restaurants in b["cities"].items()
        ]
        cities.sort(key=lambda c: c["city_name"].lower())
        cuisine_entries.append({"slug": s, "display": b["display"], "cities": cities})
    _write_manifest(CONTENT_DIR / "cuisine", cuisine_entries)

    dish_entries = []
    for s, b in sorted(agg["dish"].items()):
        cities = [
            {
                "country_slug": country,
                "city_slug": city_slug,
                "city_name": city_name,
                "n": len(restaurants),
            }
            for (country, city_slug, city_name), restaurants in b["where_to_eat"].items()
            if restaurants
        ]
        cities.sort(key=lambda c: c["city_name"].lower())
        dish_entries.append({"slug": s, "display": b["display"], "cities": cities})
    _write_manifest(CONTENT_DIR / "dish", dish_entries)
    # Neighborhood manifest groups by city for the chrome index.
    nb_entries = []
    for (city_slug, hood_slug), b in sorted(agg["neighborhood"].items()):
        nb_entries.append({
            "slug": hood_slug,
            "display": b["display"],
            "city_slug": city_slug,
            "city_name": b["city_name"],
            "country_slug": b["country_slug"],
        })
    _write_manifest(CONTENT_DIR / "neighborhood", nb_entries)

    print(f"  cuisine pages:       {n_c}  (pruned {pruned_c} stale)")
    print(f"  dish pages:          {n_d}  (pruned {pruned_d} stale)")
    print(f"  neighborhood pages:  {n_n}  (pruned {pruned_n} stale)")

    # Surface unmapped cuisines so an editor can either add to data/cuisines.json
    # or correct the offending entry. Unmapped cuisines do NOT get a cross-cut.
    unmapped = agg.get("unmapped_cuisines") or {}
    if unmapped:
        print(f"\n[WARN] {len(unmapped)} cuisine value(s) not in data/cuisines.json:")
        for raw, refs in sorted(unmapped.items()):
            sample = refs[0] if refs else ""
            extra = f" (+{len(refs) - 1} more)" if len(refs) > 1 else ""
            print(f"  - {raw!r}: {sample}{extra}")
        print("  Fix: add an alias under the matching canonical in data/cuisines.json, then re-run.")

    print(f"DONE: {n_c + n_d + n_n} cross-cut pages written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
