#!/usr/bin/env python3
"""Build content/search/search-index.json from every published page.

The index is the data layer for /search/. It feeds a client-side fuzzy
ranker; the goal is high recall (every page on the site is findable) with
sensible ranking (cities > signature dishes > entities > topic pages,
prefix matches > anywhere matches).

Each entry shape:

    {
      "id":     "france:paris:restaurants:bistrot-paul-bert",
      "type":   "entity" | "city" | "country" | "topic" | "dish" | "cuisine"
                | "neighborhood" | "chrome",
      "name":   "Bistrot Paul Bert",
      "subtitle": "French bistro in Paris, 11e",
      "url":    "/france/paris/restaurants/bistrot-paul-bert/",
      "country":"france",     // for filtering / sorting
      "city":   "paris",       // for filtering / sorting
      "tokens": "bistrot paul bert french bistro paris 11e bistrot-paul-bert",
      "weight": 6              // type-derived ranking floor; client tops with match score
    }

`tokens` is the pre-normalised search blob (lowercase, diacritic-stripped,
hyphens kept as separators, slug appended). The client takes the user's
input, normalises it the same way, and does prefix/substring/word-start
matching against it. Pre-computing `tokens` server-side means the client
never normalises 100k entries per keystroke.

Designed to scale to ~30 cities (~10k-20k entries) as a single JSON file.
Beyond that, shard by first letter of `name_initial` (task #15).
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.data_loader import (  # noqa: E402
    SITE_DATA, get_all_regions, load_file, load_country_data,
)
from utils.template_renderer import FOOD_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"

COUNTRY_NAMES = {
    "france": "France",
    "italy": "Italy",
    "japan": "Japan",
    "spain": "Spain",
    "united-kingdom": "United Kingdom",
    "united-states": "United States",
    "germany": "Germany",
}


def _country_display(slug: str) -> str:
    return COUNTRY_NAMES.get(slug, slug.replace("-", " ").title())
OUT = CONTENT / "search" / "search-index.json"


# Weight floor by entry type. Client scoring multiplies the per-match bonus
# by this so a city match beats an entity match at equal text distance.
# Cities sit highest because their pages link to every other entry below
# them; a search query that could be either a city or an entity usually
# wants the city first.
TYPE_WEIGHT = {
    "city": 10,
    "country": 9,
    "dish": 8,
    "cuisine": 7,
    "neighborhood": 6,
    "topic": 5,
    "entity": 4,
    "chrome": 2,
}


_COMBINING_RE = re.compile(r"[̀-ͯ]")


def _norm(s: str) -> str:
    """Lowercase + strip diacritics + collapse whitespace.

    Cafe -> cafe, Bistrot Paul Bert -> bistrot paul bert. The client
    applies the same transform to the user input so 'cafe' matches 'Cafe'
    even when the page name has accents.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).lower()
    s = _COMBINING_RE.sub("", s)
    return " ".join(s.split())


def _entry(type_, name, url, *, subtitle="", country="", city="", extra_tokens=()):
    tokens = " ".join(filter(None, [
        _norm(name),
        _norm(subtitle),
        _norm(country),
        _norm(city),
        *(_norm(t) for t in extra_tokens),
        # url path tokens, slug-style, so 'bistrot paul bert' also
        # matches 'bistrot-paul-bert' or the URL itself.
        " ".join(_norm(p) for p in url.strip("/").split("/")),
    ]))
    return {
        "id": (country + ":" + city + ":" + url).strip(":/"),
        "type": type_,
        "name": name,
        "subtitle": subtitle,
        "url": url,
        "country": country,
        "city": city,
        "tokens": tokens,
        "weight": TYPE_WEIGHT.get(type_, 1),
    }


# Topics whose entries are city-scoped venues / entities.
# Note: itineraries are content (not venues) and render inline on the
# topic page; they're not indexed per-entry here.
ENTITY_TOPICS = {
    "restaurants": "restaurants",
    "fine-dining": "fine_dining",
    "casual-dining": "casual_dining",
    "cafes": "cafes",
    "bakeries": "bakeries",
    "coffee-roasters": "coffee_roasters",
    "wine-bars": "wine_bars",
    "bars": "bars",
    "street-food": "street_food",
    "breweries": "breweries",
    "markets": "markets",
    "food-tours": "food_tours",
    "festivals": "food_festivals",
    "cooking-classes": "cooking_classes",
    "budget-eating": "budget_eating",
    "hidden-gems": "hidden_gems",
    "brunch": "brunch",
    "late-night": "late_night",
    "day-trips-food": "day_trips_food",
}


def _index_city(entries: list, country: str, region: str | None) -> None:
    """Append every searchable entry under one city to the entries list."""
    data = load_country_data(country, region_slug=region)
    dest = data.get("destination", {})
    research = data.get("research", {})
    city_slug = region or country
    city_name = dest.get("name", city_slug.replace("-", " ").title())
    country_name = dest.get("country", country.replace("-", " ").title())
    base = f"/{country}/{region}/" if region else f"/{country}/"

    # 1) The city hub.
    entries.append(_entry(
        "city", city_name, base,
        subtitle=f"{country_name} food guide",
        country=country, city=city_slug,
        extra_tokens=["food guide"],
    ))

    # 2) The 20 topic pages under this city.
    for topic in FOOD_TOPIC_NAV:
        entries.append(_entry(
            "topic", f"{topic['name']} in {city_name}",
            f"{base}{topic['slug']}/",
            subtitle=f"{city_name}, {country_name} food guide",
            country=country, city=city_slug,
            extra_tokens=[topic["slug"], topic["name"]],
        ))

    # 3) Entities (restaurants, cafes, bars, etc) - the bulk of the index.
    for topic_slug, research_key in ENTITY_TOPICS.items():
        for e in (research.get(research_key) or []):
            if not isinstance(e, dict) or not e.get("slug"):
                continue
            name = e.get("name") or e.get("operator") or e["slug"]
            sub_parts = [topic_slug.replace("-", " ")]
            if e.get("cuisine"):
                sub_parts.insert(0, e["cuisine"])
            if e.get("neighborhood"):
                sub_parts.append(e["neighborhood"])
            subtitle = ", ".join(sub_parts) + f" in {city_name}, {country_name}"
            entries.append(_entry(
                "entity", name, f"{base}{topic_slug}/{e['slug']}/",
                subtitle=subtitle,
                country=country, city=city_slug,
                extra_tokens=[
                    e.get("cuisine", ""), e.get("neighborhood", ""),
                    e.get("dish", ""), topic_slug, e["slug"],
                ],
            ))

    # 4) Dietary entries (different shape: dict of lists).
    dietary = research.get("dietary") or {}
    if isinstance(dietary, dict):
        for diet_key, places in dietary.items():
            if not isinstance(places, list):
                continue
            for e in places:
                if not isinstance(e, dict) or not e.get("slug"):
                    continue
                name = e.get("name") or e["slug"]
                entries.append(_entry(
                    "entity", name, f"{base}dietary/{e['slug']}/",
                    subtitle=f"{diet_key.replace('_', ' ').title()} in {city_name}, {country_name}",
                    country=country, city=city_slug,
                    extra_tokens=["dietary", diet_key, e["slug"]],
                ))

    # 4b) Nightlife entries (same dict-of-lists shape as dietary).
    nightlife = research.get("nightlife") or {}
    if isinstance(nightlife, dict):
        for night_key, places in nightlife.items():
            if not isinstance(places, list):
                continue
            for e in places:
                if not isinstance(e, dict) or not e.get("slug"):
                    continue
                name = e.get("name") or e["slug"]
                entries.append(_entry(
                    "entity", name, f"{base}nightlife/{e['slug']}/",
                    subtitle=f"{night_key.replace('_', ' ').title()} in {city_name}, {country_name}",
                    country=country, city=city_slug,
                    extra_tokens=["nightlife", night_key, e["slug"]],
                ))

    # 5) Signature dishes (per city; the /dish/<slug>/ cross-cut is
    # indexed separately from the manifest).
    for d in (research.get("signature_dishes") or []):
        if not isinstance(d, dict) or not d.get("slug"):
            continue
        entries.append(_entry(
            "dish", d.get("name", d["slug"]),
            f"{base}signature-dishes/",
            subtitle=f"Signature dish of {city_name}, {country_name}",
            country=country, city=city_slug,
            extra_tokens=[d["slug"], "dish", "signature"],
        ))


def _safe_load_manifest(path: Path) -> list[dict]:
    """Read a cross-cut manifest defensively. Missing file -> []; malformed
    JSON -> log + []. Critical at scale: one corrupt manifest mustn't crash
    the search-index build for every other entry on the site."""
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("entries", [])
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  [WARN] could not read manifest {path}: {exc}")
        return []


def _index_cross_cuts(entries: list) -> None:
    """Append /cuisine/<slug>/, /dish/<slug>/, /neighborhood/<city>/<hood>/
    pages by reading the manifest files written by generate_cross_cuts.py."""
    for parent, type_ in (
        (CONTENT / "cuisine", "cuisine"),
        (CONTENT / "dish", "dish"),
    ):
        m = parent / "_manifest.json"
        for e in _safe_load_manifest(m):
            slug = e["slug"]; display = e["display"]
            subtitle = (
                "Cross-city cuisine guide" if type_ == "cuisine"
                else "Where to eat the canonical version"
            )
            entries.append(_entry(
                type_, display, f"/{type_}/{slug}/",
                subtitle=subtitle,
                extra_tokens=[slug, type_],
            ))

    for e in _safe_load_manifest(CONTENT / "neighborhood" / "_manifest.json"):
        entries.append(_entry(
            "neighborhood", e["display"],
            f"/neighborhood/{e['city_slug']}/{e['slug']}/",
            subtitle=f"Eat in {e['display']}, {e['city_name']}, {_country_display(e.get('country_slug',''))}",
            country=e.get("country_slug", ""), city=e["city_slug"],
            extra_tokens=[e["slug"], "neighbourhood", "neighborhood"],
        ))


def _index_scoped_cross_cuts(entries: list) -> None:
    """Append country-scoped + city-scoped cross-cut index pages.

    Reads the country/city walk to know which scope hosts which surface,
    and checks each rendered HTML on disk so the index never claims a
    page that wasn't actually written by generate_scoped_cross_cuts.py.
    """
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        country_name = _country_display(country)
        # Country-scoped
        for sub, label in (
            ("cuisines", "Cuisines"),
            ("signature-dishes", "Signature dishes"),
            ("neighborhoods", "Neighbourhoods"),
        ):
            if (CONTENT / country / sub / "index.html").exists():
                entries.append(_entry(
                    "scoped-index", f"{label} in {country_name}",
                    f"/{country}/{sub}/",
                    subtitle=f"All {label.lower()} across {country_name}",
                    country=country,
                    extra_tokens=[sub, label.lower(), country, country_name],
                ))
        # City-scoped
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city = city_dir.name
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            city_name = rdata.get("destination", {}).get("name") or city.replace("-", " ").title()
            # signature-dishes is the existing topic chapter; cuisines +
            # neighborhoods are the new city-scoped indexes.
            for sub, label in (
                ("cuisines", "Cuisines"),
                ("neighborhoods", "Neighbourhoods"),
            ):
                if (CONTENT / country / city / sub / "index.html").exists():
                    entries.append(_entry(
                        "scoped-index", f"{label} in {city_name}",
                        f"/{country}/{city}/{sub}/",
                        subtitle=f"All {label.lower()} in {city_name}, {country_name}",
                        country=country, city=city,
                        extra_tokens=[sub, label.lower(), city, city_name],
                    ))


def _index_city_cuisine(entries: list) -> None:
    """Append city × cuisine pages: /<country>/<city>/cuisine/<slug>/.

    Walks content/ for any cuisine subdirectory under each city so we
    don't need to duplicate the threshold logic from
    generate_city_cuisine.py.
    """
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        country_name = _country_display(country)
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city = city_dir.name
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            city_name = (rdata.get("destination") or {}).get("name") or city.replace("-", " ").title()
            cuisine_dir = CONTENT / country / city / "cuisine"
            if not cuisine_dir.is_dir():
                continue
            for slug_dir in sorted(cuisine_dir.iterdir()):
                if not slug_dir.is_dir() or not (slug_dir / "index.html").exists():
                    continue
                cuisine_slug = slug_dir.name
                cuisine_display = cuisine_slug.replace("-", " ").title()
                entries.append(_entry(
                    "cuisine-index", f"{cuisine_display} in {city_name}",
                    f"/{country}/{city}/cuisine/{cuisine_slug}/",
                    subtitle=f"{cuisine_display} rooms in {city_name}, {country_name}",
                    country=country, city=city,
                    extra_tokens=[
                        "cuisine", cuisine_slug, cuisine_display.lower(),
                        city, city_name, country, country_name,
                    ],
                ))


def _index_city_dish(entries: list) -> None:
    """Append /<country>/<city>/dish/<slug>/ pages.

    Walks content/ to know which (city, dish) pairs got rendered, then
    pulls the dish display name from the city's signature-dishes.json
    so the search hit reads "Croissant in Paris" not "croissant in Paris".
    """
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        country_name = _country_display(country)
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city = city_dir.name
            rj = city_dir / "data" / "region.json"
            sd = city_dir / "data" / "signature-dishes.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            city_name = (rdata.get("destination") or {}).get("name") or city.replace("-", " ").title()
            # Map dish slug -> display name from signature-dishes.json
            slug_to_name: dict[str, str] = {}
            if sd.exists():
                try:
                    sdata = json.loads(sd.read_text(encoding="utf-8"))
                    for d in (sdata.get("signature_dishes") or []):
                        if isinstance(d, dict) and d.get("slug"):
                            slug_to_name[d["slug"]] = d.get("name") or d["slug"]
                except (OSError, json.JSONDecodeError):
                    pass
            dish_dir = CONTENT / country / city / "dish"
            if not dish_dir.is_dir():
                continue
            for slug_dir in sorted(dish_dir.iterdir()):
                if not slug_dir.is_dir() or not (slug_dir / "index.html").exists():
                    continue
                dish_slug = slug_dir.name
                dish_display = slug_to_name.get(dish_slug, dish_slug.replace("-", " ").title())
                entries.append(_entry(
                    "dish-index", f"{dish_display} in {city_name}",
                    f"/{country}/{city}/dish/{dish_slug}/",
                    subtitle=f"Where to eat {dish_display} in {city_name}, {country_name}",
                    country=country, city=city,
                    extra_tokens=[
                        "dish", dish_slug, dish_display.lower(),
                        city, city_name, country, country_name,
                    ],
                ))


def _index_city_dietary(entries: list) -> None:
    """Append city × diet landing pages.

    /<country>/<city>/dietary/vegan/, /vegetarian/, /gluten-free/,
    /halal/, /kosher/ — emitted by generate_city_dietary.py when a city
    has >= 2 entries for that diet. Walks content/ so we don't need to
    duplicate the threshold logic here.
    """
    diet_display = {
        "vegan": "Vegan",
        "vegetarian": "Vegetarian",
        "gluten-free": "Gluten-free",
        "halal": "Halal",
        "kosher": "Kosher",
    }
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        country_name = _country_display(country)
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city = city_dir.name
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            city_name = rdata.get("destination", {}).get("name") or city.replace("-", " ").title()
            dietary_dir = CONTENT / country / city / "dietary"
            if not dietary_dir.is_dir():
                continue
            for diet_slug, diet_label in diet_display.items():
                if (dietary_dir / diet_slug / "index.html").exists():
                    entries.append(_entry(
                        "dietary-index", f"{diet_label} in {city_name}",
                        f"/{country}/{city}/dietary/{diet_slug}/",
                        subtitle=f"{diet_label} rooms in {city_name}, {country_name}",
                        country=country, city=city,
                        extra_tokens=[
                            "dietary", diet_slug, diet_label.lower(),
                            city, city_name, country, country_name,
                        ],
                    ))


def _index_chrome(entries: list) -> None:
    """Append the chrome / index pages that aren't auto-discovered."""
    chrome_pages = [
        ("Cities", "/cities/", "Every city we cover"),
        ("Cuisines", "/cuisines/", "Cuisines we cover across all cities"),
        ("Dishes", "/dishes/", "Signature dishes across the archive"),
        ("Neighbourhoods", "/neighborhoods/", "Neighbourhood eating guides"),
        ("Topics", "/topics/", "The 20 food chapters in every city guide"),
        ("About", "/about/", "About TableJourney"),
        ("Editorial standards", "/editorial-standards/", "How we cover food"),
        ("Contact", "/contact/", "Get in touch with the editorial desk"),
    ]
    for name, url, subtitle in chrome_pages:
        entries.append(_entry("chrome", name, url, subtitle=subtitle))


def all_countries_with_any_data() -> list[str]:
    out = []
    if not SITE_DATA.exists():
        return out
    for d in sorted(SITE_DATA.iterdir()):
        if not d.is_dir():
            continue
        if (d / "data" / "region.json").exists():
            out.append(d.name); continue
        if any((sub / "data" / "region.json").exists()
               for sub in d.iterdir() if sub.is_dir()):
            out.append(d.name)
    return out


def main() -> int:
    entries: list[dict] = []

    for country in all_countries_with_any_data():
        # Country-level region.json (if present).
        try:
            country_region = load_file(country, "region.json")
        except FileNotFoundError:
            country_region = None
        if country_region:
            dest = country_region.get("destination", {})
            entries.append(_entry(
                "country", dest.get("name", country.title()), f"/{country}/",
                subtitle=dest.get("country", "") or "Country guide",
                country=country,
                extra_tokens=[country],
            ))
        for region in get_all_regions(country):
            try:
                _index_city(entries, country, region)
            except (FileNotFoundError, ValueError, OSError) as exc:
                print(f"  [WARN] search index skipping {country}/{region}: {exc}")
            except Exception as exc:  # noqa: BLE001
                print(f"  [WARN] search index skipping {country}/{region}: unexpected error: {exc}")

    _index_cross_cuts(entries)
    _index_scoped_cross_cuts(entries)
    _index_city_dietary(entries)
    _index_city_cuisine(entries)
    _index_city_dish(entries)
    _index_chrome(entries)

    # Deduplicate on (type, url). With the way entries are produced, the
    # only realistic duplicates are stub edge cases; keep first occurrence.
    seen = set()
    unique = []
    for e in entries:
        key = (e["type"], e["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # Compact JSON (no indent) to minimise download size; the index is
    # consumed by JS, not read by humans.
    OUT.write_text(
        json.dumps({"entries": unique}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT} with {len(unique)} entries ({size_kb:.1f} KB)")

    # Qwen tag enrichment (always tries, skips silently if no key is
    # findable). Adds synonym/occasion/vibe/dietary tags to each entry's
    # tokens blob so "noodles" matches ramen, "date night" matches
    # romantic-bistro entries, etc. Caches by content hash, so
    # incremental builds only call the model for new or changed entries.
    # Key lookup order: AI_KEY env > data/.qwen-key file > skip.
    key_file = REPO_ROOT / "data" / ".qwen-key"
    have_key = bool(os.environ.get("AI_KEY")) or key_file.exists()
    if have_key:
        try:
            import subprocess
            print("Running Qwen search tagger (key found; incremental — only new entries call the model)")
            subprocess.run(
                [sys.executable, str(Path(__file__).parent / "qwen_search_tagger.py")],
                check=True, cwd=REPO_ROOT,
            )
        except Exception as e:
            print(f"  [WARN] Qwen tagger failed (non-fatal, index already written): {e}")
    else:
        print("  Qwen tagger skipped (no AI_KEY env var, no data/.qwen-key file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
