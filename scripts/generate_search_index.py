#!/usr/bin/env python3
"""Build content/search/search-index.json from every published page.

The index is the data layer for /search/. It feeds a client-side fuzzy
ranker; the goal is high recall (every page on the site is findable) with
sensible ranking (cities > signature dishes > entities > topic pages,
prefix matches > anywhere matches).

Each entry shape:

    {
      "id":     "france:paris:restaurants:bistrot-paul-bert",
      "type":   "entity" | "city" | "country" | "topic" | "wine" | "grape" | "style" | "world"
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
from utils.template_renderer import WINE_TOPIC_NAV  # noqa: E402

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
    "grape": 8,
    "style": 7,
    "world": 7,
    "wine": 6,
    "neighborhood": 6,
    "topic": 5,
    "entity": 4,
    "scoped-index": 3,
    "grape-index": 3,
    "dietary-index": 3,
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
    "vineyards": "vineyards",
    "tasting-rooms": "tasting_rooms",
    "wine-bars": "wine_bars",
    "wine-restaurants": "wine_restaurants",
    "wine-retailers": "wine_retailers",
    "wine-schools": "wine_schools",
    "wine-tours": "wine_tours",
    "wine-festivals": "wine_festivals",
    "distilleries": "distilleries",
    "wine-museums": "wine_museums",
    "wine-hotels": "wine_hotels",
    "wine-experiences": "wine_experiences",
    "budget-wines": "budget_wines",
    "hidden-gems": "hidden_gems",
    "day-trips-wine": "day_trips_wine",
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
        subtitle=f"{country_name} wine guide",
        country=country, city=city_slug,
        extra_tokens=["wine guide", "wine region"],
    ))

    # 2) The 24 topic pages under this region.
    for topic in WINE_TOPIC_NAV:
        entries.append(_entry(
            "topic", f"{topic['name']} in {city_name}",
            f"{base}{topic['slug']}/",
            subtitle=f"{city_name}, {country_name} wine guide",
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
            if e.get("classification"):
                sub_parts.insert(0, e["classification"])
            if e.get("neighborhood"):
                sub_parts.append(e["neighborhood"])
            subtitle = ", ".join(sub_parts) + f" in {city_name}, {country_name}"
            varietals = e.get("varietals") or e.get("varietals_focus") or []
            if isinstance(varietals, str):
                varietals = [varietals]
            # normalize: cuvée entries store [{grape, pct}]; vineyards store ["Sangiovese", ...]
            _norm_varietals: list[str] = []
            for _item in varietals:
                if isinstance(_item, str):
                    _norm_varietals.append(_item)
                elif isinstance(_item, dict):
                    _g = _item.get("grape") or _item.get("name") or _item.get("varietal")
                    if _g and isinstance(_g, str):
                        _norm_varietals.append(_g)
            entries.append(_entry(
                "entity", name, f"{base}{topic_slug}/{e['slug']}/",
                subtitle=subtitle,
                country=country, city=city_slug,
                extra_tokens=[
                    e.get("classification", ""), e.get("neighborhood", ""),
                    *_norm_varietals, topic_slug, e["slug"],
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

    # 5) Wines (per-cuvée pages — the full catalog).
    # Each cuvée gets one entry pointing at the global /wine/<producer>/<slug>/
    # URL. Taste descriptors + tags + grapes flow into extra_tokens so a
    # search for "bold tannic sangiovese" finds Tignanello. This is the
    # primary wine-search surface; the signature-wines block below is the
    # fallback for regions that haven't been migrated to wines.json yet.
    for w in (research.get("wines") or []):
        if not isinstance(w, dict) or not w.get("slug") or not w.get("producer"):
            continue
        taste = w.get("taste") or {}
        aroma = taste.get("aroma") or []
        if not isinstance(aroma, list):
            aroma = []
        palate = taste.get("palate") or []
        if not isinstance(palate, list):
            palate = []
        tags = w.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        varietals = w.get("varietals") or []
        grape_tokens = []
        if isinstance(varietals, list):
            for v in varietals:
                if isinstance(v, dict) and v.get("grape"):
                    grape_tokens.append(v["grape"])
                elif isinstance(v, str):
                    grape_tokens.append(v)
        subtitle_parts = [w.get("producer_name") or w["producer"]]
        if w.get("style"):
            subtitle_parts.append(w["style"].replace("-", " "))
        subtitle_parts.append(f"{city_name}, {country_name}")
        entries.append(_entry(
            "wine", w.get("name", w["slug"]),
            f"/wine/{w['producer']}/{w['slug']}/",
            subtitle=", ".join(subtitle_parts),
            country=country, city=city_slug,
            extra_tokens=[
                w["slug"], "wine", "cuvee",
                w.get("producer", ""), w.get("producer_name", ""),
                w.get("style", "").replace("-", " "),
                w.get("classification", ""),
                w.get("price_band", ""),
                *grape_tokens, *aroma, *palate, *tags,
            ],
        ))

    # 5a) Signature wines (curated subset of wines.json). When wines.json
    # exists the signature-wines slugs already appear above via the cuvée
    # pages, so emit signature-wines entries only as a fallback for regions
    # that haven't migrated to wines.json yet (no wines list at all).
    if not (research.get("wines") or []):
        for w in (research.get("signature_wines") or []):
            if not isinstance(w, dict) or not w.get("slug"):
                continue
            entries.append(_entry(
                "wine", w.get("name", w["slug"]),
                f"{base}signature-wines/#{w['slug']}",
                subtitle=f"Signature wine of {city_name}, {country_name}",
                country=country, city=city_slug,
                extra_tokens=[w["slug"], "wine", "signature", w.get("producer", "")],
            ))

    # 5b) Signature grapes (per region; also surface as /grape/<slug>/).
    for g in (research.get("signature_grapes") or []):
        if not isinstance(g, dict) or not g.get("slug"):
            continue
        entries.append(_entry(
            "grape", g.get("name", g["slug"]),
            f"/grape/{g['slug']}/",
            subtitle=f"Signature grape of {city_name}, {country_name}",
            country=country, city=city_slug,
            extra_tokens=[g["slug"], "grape", "varietal"],
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
    """Append /grape/<slug>/, /style/<slug>/, /world/<slug>/,
    /neighborhood/<region>/<sub>/ pages by reading the manifest files
    written by generate_cross_cuts.py."""
    for parent, type_, subtitle in (
        (CONTENT / "grape", "grape", "Where to taste this grape worldwide"),
        (CONTENT / "style", "style", "This wine style across regions"),
        (CONTENT / "world", "world", "Wine regions in this world category"),
    ):
        for e in _safe_load_manifest(parent / "_manifest.json"):
            slug = e["slug"]; display = e["display"]
            entries.append(_entry(
                type_, display, f"/{type_}/{slug}/",
                subtitle=subtitle,
                extra_tokens=[slug, type_],
            ))

    for e in _safe_load_manifest(CONTENT / "neighborhood" / "_manifest.json"):
        entries.append(_entry(
            "neighborhood", e["display"],
            f"/neighborhood/{e['region_slug']}/{e['slug']}/",
            subtitle=f"Wine in {e['display']}, {e['region_name']}, {_country_display(e.get('country_slug',''))}",
            country=e.get("country_slug", ""), city=e["region_slug"],
            extra_tokens=[e["slug"], "sub-appellation", "neighbourhood"],
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
            ("grapes", "Grapes"),
            ("styles", "Wine styles"),
            ("neighborhoods", "Sub-appellations"),
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
            # region-scoped grape / style / sub-appellation indexes.
            for sub, label in (
                ("grapes", "Grapes"),
                ("styles", "Wine styles"),
                ("neighborhoods", "Sub-appellations"),
            ):
                if (CONTENT / country / city / sub / "index.html").exists():
                    entries.append(_entry(
                        "scoped-index", f"{label} in {city_name}",
                        f"/{country}/{city}/{sub}/",
                        subtitle=f"All {label.lower()} in {city_name}, {country_name}",
                        country=country, city=city,
                        extra_tokens=[sub, label.lower(), city, city_name],
                    ))


def _index_region_grape(entries: list) -> None:
    """Append region × grape pages: /<country>/<region>/grape/<slug>/.

    Walks content/ for any grape subdirectory under each region so we
    don't duplicate the threshold logic from generate_region_grape.py.
    Pulls the grape display name from the region's signature-grapes.json
    when available so the hit reads "Cabernet Sauvignon in Bordeaux".
    """
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        country_name = _country_display(country)
        for region_dir in sorted(country_dir.iterdir()):
            if not region_dir.is_dir() or region_dir.name == "data":
                continue
            region = region_dir.name
            rj = region_dir / "data" / "region.json"
            sg = region_dir / "data" / "signature-grapes.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            region_name = (rdata.get("destination") or {}).get("name") or region.replace("-", " ").title()
            slug_to_name: dict[str, str] = {}
            if sg.exists():
                try:
                    sgdata = json.loads(sg.read_text(encoding="utf-8"))
                    for g in (sgdata.get("signature_grapes") or []):
                        if isinstance(g, dict) and g.get("slug"):
                            slug_to_name[g["slug"]] = g.get("name") or g["slug"]
                except (OSError, json.JSONDecodeError):
                    pass
            grape_dir = CONTENT / country / region / "grape"
            if not grape_dir.is_dir():
                continue
            for slug_dir in sorted(grape_dir.iterdir()):
                if not slug_dir.is_dir() or not (slug_dir / "index.html").exists():
                    continue
                grape_slug = slug_dir.name
                grape_display = slug_to_name.get(grape_slug, grape_slug.replace("-", " ").title())
                entries.append(_entry(
                    "grape-index", f"{grape_display} in {region_name}",
                    f"/{country}/{region}/grape/{grape_slug}/",
                    subtitle=f"Where to taste {grape_display} in {region_name}, {country_name}",
                    country=country, city=region,
                    extra_tokens=[
                        "grape", grape_slug, grape_display.lower(),
                        region, region_name, country, country_name,
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
        "biodynamic": "Biodynamic",
        "organic": "Organic",
        "natural": "Natural",
        "vegan-winemaking": "Vegan winemaking",
        "lowsulfite": "Low sulfite",
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


def _index_tag_pages(entries: list) -> None:
    """Append /tag/<slug>/ and /tag/<slug>/<region>/ entries from the
    manifest written by generate_tag_pages.py. Tag pages let users browse
    the catalog by pairing / mood / occasion / style etc, and benefit from
    being findable in the global search box."""
    manifest = _safe_load_manifest(CONTENT / "tag" / "_manifest.json")
    for e in manifest:
        slug = e["slug"]
        display = e.get("display") or slug.replace("-", " ").title()
        axis = e.get("axis") or "tag"
        count = e.get("count", 0)
        entries.append(_entry(
            "tag", display, f"/tag/{slug}/",
            subtitle=f"{axis.title()} tag: {count} cuvée{'' if count == 1 else 's'}",
            extra_tokens=[slug, "tag", axis, "wine", "filter"],
        ))
        for r in e.get("regions", []):
            if r.get("count", 0) < 2:
                continue
            r_slug = r.get("region_slug")
            c_slug = r.get("country_slug")
            if not r_slug or not c_slug:
                continue
            r_name = r_slug.replace("-", " ").title()
            entries.append(_entry(
                "tag", f"{display} in {r_name}",
                f"/tag/{slug}/{r_slug}/",
                subtitle=f"{display} cuvées in {r_name}",
                country=c_slug, city=r_slug,
                extra_tokens=[slug, "tag", axis, r_slug, "wine"],
            ))


def _index_chrome(entries: list) -> None:
    """Append the chrome / index pages that aren't auto-discovered."""
    chrome_pages = [
        ("Regions", "/regions/", "Every wine region we cover"),
        ("Grapes", "/grapes/", "Grape varietals we cover across all regions"),
        ("Styles", "/styles/", "Wine styles across the archive"),
        ("Old World & New World", "/world/", "Wine regions by world category"),
        ("Topics", "/topics/", "The 24 wine chapters in every region guide"),
        ("About", "/about/", "About Cork & Curve"),
        ("Editorial standards", "/about/editorial/", "How we cover wine"),
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
    _index_region_grape(entries)
    _index_tag_pages(entries)
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
