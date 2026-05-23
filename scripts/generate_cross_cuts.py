#!/usr/bin/env python3
"""Generate cross-cut landing pages by aggregating entities across all regions.

Emits:
    /grape/<grape-slug>/                   grape (varietal) landing (global)
    /style/<style-slug>/                   wine-style landing (global)
    /world/<world-slug>/                   Old World / New World landing (global)
    /neighborhood/<region-slug>/<sub>/     sub-appellation landing (region-scoped)

Re-runnable; rewrites pages every run and prunes orphans.

Usage:
    python scripts/generate_cross_cuts.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import (
    SITE_DATA,
    load_country_data,
)
from utils.seo import meta_desc as _meta_desc
from utils.slug import slugify
from utils.template_renderer import TemplateRenderer

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

TOPIC_DISPLAY = {
    "vineyards": "Vineyards",
    "tasting-rooms": "Tasting Rooms",
    "wine-bars": "Wine Bars",
    "wine-restaurants": "Wine Restaurants",
    "wine-retailers": "Wine Retailers",
    "wine-schools": "Wine Schools",
    "wine-tours": "Wine Tours",
    "wine-festivals": "Wine Festivals",
    "distilleries": "Distilleries",
    "wine-museums": "Wine Museums",
    "wine-hotels": "Wine Hotels",
    "wine-experiences": "Wine Experiences",
    "budget-wines": "Budget Wines",
    "hidden-gems": "Hidden Gems",
    "day-trips-wine": "Wine Day Trips",
}

# research-key -> topic-slug (entity-bearing list topics that carry a
# `neighborhood` / sub-appellation worth aggregating).
RESEARCH_KEY_TO_TOPIC = {
    "vineyards": "vineyards",
    "tasting_rooms": "tasting-rooms",
    "wine_bars": "wine-bars",
    "wine_restaurants": "wine-restaurants",
    "wine_retailers": "wine-retailers",
    "wine_schools": "wine-schools",
    "wine_tours": "wine-tours",
    "wine_festivals": "wine-festivals",
    "distilleries": "distilleries",
    "wine_museums": "wine-museums",
    "wine_hotels": "wine-hotels",
    "wine_experiences": "wine-experiences",
    "budget_wines": "budget-wines",
    "hidden_gems": "hidden-gems",
    "day_trips_wine": "day-trips-wine",
}

# Country -> world category. A region.json may override via
# destination.world ("old-world" / "new-world").
COUNTRY_WORLD = {
    "france": "old-world", "italy": "old-world", "spain": "old-world",
    "portugal": "old-world", "germany": "old-world", "austria": "old-world",
    "hungary": "old-world", "greece": "old-world", "georgia": "old-world",
    "croatia": "old-world", "slovenia": "old-world", "romania": "old-world",
    "switzerland": "old-world", "bulgaria": "old-world", "moldova": "old-world",
    "lebanon": "old-world", "israel": "old-world", "turkey": "old-world",
    "czech-republic": "old-world", "slovakia": "old-world", "england": "old-world",
    "united-kingdom": "old-world",
    "united-states": "new-world", "usa": "new-world", "argentina": "new-world",
    "chile": "new-world", "australia": "new-world", "new-zealand": "new-world",
    "south-africa": "new-world", "canada": "new-world", "brazil": "new-world",
    "uruguay": "new-world", "mexico": "new-world", "china": "new-world",
    "india": "new-world", "japan": "new-world",
}
WORLD_DISPLAY = {"old-world": "Old World", "new-world": "New World"}

# Wine-style controlled vocabulary. A free-form style string ("still red
# Bordeaux blend", "vintage Champagne") is classified to one canonical
# style by keyword. Order matters: the first match wins, "still" is the
# catch-all and must stay last.
STYLE_KEYWORDS = [
    ("sparkling", ["sparkling", "champagne", "cremant", "crémant", "cava",
                   "prosecco", "spumante", "franciacorta", "sekt", "pet-nat",
                   "pét-nat", "petnat", "metodo classico", "traditional method"]),
    ("sweet", ["sweet", "dessert", "late harvest", "late-harvest", "noble rot",
               "botrytis", "sauternes", "ice wine", "icewine", "eiswein",
               "tokaji", "passito", "vin doux", "moelleux", "auslese",
               "beerenauslese", "trockenbeerenauslese"]),
    ("fortified", ["fortified", "port", "sherry", "madeira", "marsala",
                   "vermouth", "vin doux naturel", "vdn"]),
    ("orange", ["orange", "skin-contact", "skin contact", "amber"]),
    ("natural", ["natural", "low-intervention", "low intervention",
                 "zero-zero", "zero zero", "minimal intervention"]),
    ("still", ["still", "red", "white", "rose", "rosé", "blend", "dry"]),
]
STYLE_DISPLAY = {
    "sparkling": "Sparkling", "still": "Still", "sweet": "Sweet",
    "fortified": "Fortified", "orange": "Orange", "natural": "Natural",
}


def _classify_style(style_str: str) -> str | None:
    if not style_str:
        return None
    s = style_str.lower()
    for slug, keywords in STYLE_KEYWORDS:
        if any(kw in s for kw in keywords):
            return slug
    return None


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
            "og_image_alt": "Cork & Curve wine guide",
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
    region with a region.json. Includes country-level hubs (region_slug=None).
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
    """Walk every region, return aggregated cross-cut structures.

    Resilient to per-region failures: a single bad region (malformed JSON,
    missing file) is logged and skipped; the rest still aggregate.
    """
    regions_data = []
    for country, region in _all_country_region_pairs():
        try:
            data = load_country_data(country, region_slug=region)
        except (FileNotFoundError, ValueError, OSError) as exc:
            print(f"  [WARN] skipping {country}/{region or '-'}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - log + skip, don't poison the run
            print(f"  [WARN] skipping {country}/{region or '-'}: unexpected error: {exc}")
            continue
        dest = data.get("destination", {})
        regions_data.append({
            "country_slug": country,
            "region_slug": region or country,
            "is_country": region is None,
            "region_name": dest.get("name", (region or country).title()),
            "world": dest.get("world"),
            "blurb": dest.get("blurb", ""),
            "data": data,
        })

    by_grape: dict[str, dict] = defaultdict(lambda: {"display": "", "regions": defaultdict(list)})
    by_style: dict[str, dict] = defaultdict(lambda: {"display": "", "regions": defaultdict(list)})
    by_world: dict[str, dict] = defaultdict(lambda: {"display": "", "regions": []})
    by_neighborhood: dict[tuple, dict] = defaultdict(lambda: {
        "display": "", "vibe": "", "region_name": "", "region_slug": "", "country_slug": "",
        "entities_by_topic": defaultdict(list),
    })

    for region in regions_data:
        research = region["data"].get("research", {})
        rkey = (region["country_slug"], region["region_slug"], region["region_name"])

        # Prefer canonical display names for grapes from signature-grapes.json.
        grape_display = {}
        for g in research.get("signature_grapes", []) or []:
            if isinstance(g, dict) and g.get("name"):
                grape_display[slugify(g["name"])] = g["name"]

        # grape: from vineyard.varietals (every venue that lists varietals).
        for vk in ("vineyards", "tasting_rooms", "hidden_gems", "budget_wines"):
            for v in research.get(vk, []) or []:
                if not isinstance(v, dict):
                    continue
                varietals = v.get("varietals") or v.get("varietals_focus") or []
                if isinstance(varietals, str):
                    varietals = [varietals]
                for varietal in varietals:
                    gslug = slugify(varietal)
                    if not gslug:
                        continue
                    gb = by_grape[gslug]
                    gb["display"] = grape_display.get(gslug) or gb["display"] or varietal
                    # de-dupe vineyards per region by slug/name
                    bucket = gb["regions"][rkey]
                    ident = v.get("slug") or v.get("name")
                    if ident and not any((e.get("slug") or e.get("name")) == ident for e in bucket):
                        bucket.append(v)

        # style: classify signature_wines, attach the producer vineyard when
        # we can resolve it; plus natural-wine vineyards into the natural style.
        vineyard_by_name = {}
        for v in research.get("vineyards", []) or []:
            if isinstance(v, dict) and v.get("name"):
                vineyard_by_name[v["name"]] = v
                if v.get("natural_wine"):
                    sb = by_style["natural"]
                    sb["display"] = STYLE_DISPLAY["natural"]
                    bucket = sb["regions"][rkey]
                    ident = v.get("slug") or v.get("name")
                    if not any((e.get("slug") or e.get("name")) == ident for e in bucket):
                        bucket.append(v)
        for w in research.get("signature_wines", []) or []:
            if not isinstance(w, dict):
                continue
            sslug = _classify_style(w.get("style", ""))
            if not sslug:
                continue
            producer = w.get("producer")
            vyd = vineyard_by_name.get(producer) if producer else None
            if vyd is None:
                continue
            sb = by_style[sslug]
            sb["display"] = STYLE_DISPLAY[sslug]
            bucket = sb["regions"][rkey]
            ident = vyd.get("slug") or vyd.get("name")
            if not any((e.get("slug") or e.get("name")) == ident for e in bucket):
                bucket.append(vyd)

        # world: regions (not country hubs) classified Old / New World.
        if not region["is_country"]:
            wslug = region["world"] or COUNTRY_WORLD.get(region["country_slug"])
            if wslug in WORLD_DISPLAY:
                wb = by_world[wslug]
                wb["display"] = WORLD_DISPLAY[wslug]
                wb["regions"].append({
                    "region_name": region["region_name"],
                    "region_slug": region["region_slug"],
                    "country_slug": region["country_slug"],
                    "blurb": region["blurb"],
                })

        # neighborhoods (sub-appellations): walk every entity-bearing topic.
        for rk, topic_slug in RESEARCH_KEY_TO_TOPIC.items():
            for e in research.get(rk, []) or []:
                if not isinstance(e, dict) or not e.get("neighborhood"):
                    continue
                nslug = slugify(e["neighborhood"])
                if not nslug:
                    continue
                key = (region["region_slug"], nslug)
                slot = by_neighborhood[key]
                slot["display"] = e["neighborhood"].split("(")[0].strip()
                slot["region_name"] = region["region_name"]
                slot["region_slug"] = region["region_slug"]
                slot["country_slug"] = region["country_slug"]
                slot["entities_by_topic"][topic_slug].append(e)

        # Attach vibe + editorial display from neighborhoods.json.
        for n in research.get("neighborhoods", []) or []:
            if not isinstance(n, dict) or not n.get("name"):
                continue
            aliases = n.get("aliases") or []
            for alias in aliases:
                key = (region["region_slug"], alias)
                if key not in by_neighborhood:
                    continue
                if n.get("vibe"):
                    by_neighborhood[key]["vibe"] = n["vibe"]
                by_neighborhood[key]["display"] = f"{n['name']} ({alias})"
            if not aliases:
                ns = slugify(n["name"])
                key = (region["region_slug"], ns)
                if key in by_neighborhood and n.get("vibe"):
                    by_neighborhood[key]["vibe"] = n["vibe"]

    return {
        "grape": by_grape,
        "style": by_style,
        "world": by_world,
        "neighborhood": by_neighborhood,
    }


def _regions_list(regions_dict: dict) -> tuple[list, int]:
    """Turn a {(country,region_slug,region_name): [vineyards]} dict into the
    sorted `regions` list the templates expect, and the total entity count."""
    out = []
    total = 0
    for (country, region_slug, region_name), vineyards in regions_dict.items():
        out.append({
            "country_slug": country,
            "region_slug": region_slug,
            "region_name": region_name,
            "vineyards": vineyards,
        })
        total += len(vineyards)
    out.sort(key=lambda r: r["region_name"].lower())
    return out, total


def write_grape_pages(renderer: TemplateRenderer, by_grape: dict) -> int:
    template = renderer.env.get_template("cross-cuts/grape.html")
    count = 0
    for slug, blob in by_grape.items():
        regions, total = _regions_list(blob["regions"])
        if not regions:
            continue
        display = blob["display"]
        canonical = f"{BASE}/grape/{slug}/"
        title = f"{display} Around the World | Cork & Curve"
        n = len(regions)
        region_phrase = "1 region" if n == 1 else f"{n} regions"
        dl = display.lower()
        desc = _meta_desc(
            f"Editor-picked {dl} producers across {region_phrase} on Cork & Curve. How each region expresses the grape, the estates to visit and the bottles that show it best.",
            f"Editor-picked {dl} producers across {region_phrase} on Cork & Curve. How each region expresses the grape and the estates worth a visit.",
            f"Editor-picked {dl} producers across {region_phrase} on Cork & Curve.",
        )
        ctx = {
            "grape": display,
            "grape_slug": slug,
            "regions": regions,
            "total_entities": total,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "Grapes", "url": "/grapes/"},
                {"name": display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": display, "country": ""},
            "analytics": _analytics("grape", slug),
            "base_path": "../..",
        }
        out = CONTENT_DIR / "grape" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.render(**ctx), encoding="utf-8")
        count += 1
    return count


def write_style_pages(renderer: TemplateRenderer, by_style: dict) -> int:
    template = renderer.env.get_template("cross-cuts/style.html")
    count = 0
    for slug, blob in by_style.items():
        regions, total = _regions_list(blob["regions"])
        if not regions:
            continue
        display = blob["display"]
        canonical = f"{BASE}/style/{slug}/"
        title = f"{display} Wine Around the World | Cork & Curve"
        n = len(regions)
        region_phrase = "1 region" if n == 1 else f"{n} regions"
        dl = display.lower()
        desc = _meta_desc(
            f"Editor-picked {dl} wine across {region_phrase} on Cork & Curve. The producers, the regions and what to look for in the glass.",
            f"Editor-picked {dl} wine across {region_phrase} on Cork & Curve.",
        )
        ctx = {
            "style": display,
            "style_slug": slug,
            "regions": regions,
            "total_entities": total,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "Styles", "url": "/styles/"},
                {"name": display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": display, "country": ""},
            "analytics": _analytics("style", slug),
            "base_path": "../..",
        }
        out = CONTENT_DIR / "style" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.render(**ctx), encoding="utf-8")
        count += 1
    return count


def write_world_pages(renderer: TemplateRenderer, by_world: dict) -> int:
    template = renderer.env.get_template("cross-cuts/world.html")
    count = 0
    for slug, blob in by_world.items():
        regions = sorted(blob["regions"], key=lambda r: r["region_name"].lower())
        if not regions:
            continue
        display = blob["display"]
        canonical = f"{BASE}/world/{slug}/"
        title = f"{display} Wine Regions | Cork & Curve"
        desc = _meta_desc(
            f"The {display} wine regions we cover on Cork & Curve, and what defines each. Vineyards, signature wines and how to plan a visit.",
            f"The {display} wine regions we cover on Cork & Curve, and what defines each.",
        )
        ctx = {
            "world": display,
            "world_slug": slug,
            "regions": regions,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "World", "url": "/world/"},
                {"name": display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": display, "country": ""},
            "analytics": _analytics("world", slug),
            "base_path": "../..",
        }
        out = CONTENT_DIR / "world" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.render(**ctx), encoding="utf-8")
        count += 1
    return count


def write_neighborhood_pages(renderer: TemplateRenderer, by_neighborhood: dict) -> int:
    template = renderer.env.get_template("cross-cuts/neighborhood.html")
    count = 0
    for (region_slug, hood_slug), blob in by_neighborhood.items():
        total = sum(len(v) for v in blob["entities_by_topic"].values())
        canonical = f"{BASE}/neighborhood/{region_slug}/{hood_slug}/"
        display = blob["display"]
        region_name = blob["region_name"]
        title = f"Wine in {display}, {region_name} | Cork & Curve"
        vibe = (blob["vibe"] or "").strip().rstrip(".")
        if vibe:
            desc = _meta_desc(
                f"{vibe}. The vineyards, tasting rooms and wine bars in {display}, {region_name}, editor-picked by Cork & Curve.",
                f"{vibe}. Editor-picked wine in {display}, {region_name}, on Cork & Curve.",
                f"{vibe}.",
            )
        else:
            desc = _meta_desc(
                f"Where to drink in {display}, {region_name}: the vineyards, tasting rooms and wine bars editor-picked by Cork & Curve, with what to taste and how to book.",
                f"Where to drink in {display}, {region_name}: vineyards, tasting rooms and wine bars editor-picked by Cork & Curve.",
            )
        ctx = {
            "neighborhood": display,
            "neighborhood_slug": hood_slug,
            "region_name": region_name,
            "region_slug": region_slug,
            "country_slug": blob["country_slug"],
            "vibe": blob["vibe"],
            "entities_by_topic": dict(blob["entities_by_topic"]),
            "topic_display": TOPIC_DISPLAY,
            "total_entities": total,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": "Sub-Appellations", "url": "/neighborhoods/"},
                {"name": region_name, "url": f"/{blob['country_slug']}/{region_slug}/"},
                {"name": display, "url": None},
            ],
            "seo": _seo_block(canonical, title, desc),
            "destination": {"name": region_name, "country": ""},
            "analytics": _analytics("neighborhood", f"{region_slug}-{hood_slug}"),
            "base_path": "../../..",
        }
        out = CONTENT_DIR / "neighborhood" / region_slug / hood_slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.render(**ctx), encoding="utf-8")
        count += 1
    return count


def _write_manifest(parent_dir: Path, entries: list[dict]) -> None:
    """Drop a flat JSON manifest of every cross-cut page under `parent_dir`,
    read by the chrome + scoped cross-cut generators to build index pages
    without re-opening every HTML file."""
    import json as _json
    parent_dir.mkdir(parents=True, exist_ok=True)
    (parent_dir / "_manifest.json").write_text(
        _json.dumps({"entries": entries}, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _prune_stale(parent: Path, keep_slugs: set[str], *, two_level: bool = False) -> int:
    """Delete cross-cut directories under `parent` whose slug is not in
    `keep_slugs`. `two_level=True` for neighborhood
    (content/neighborhood/<region>/<sub>/, key "<region>/<sub>")."""
    import shutil as _shutil
    if not parent.exists():
        return 0
    pruned = 0
    if two_level:
        for region_dir in list(parent.iterdir()):
            if not region_dir.is_dir():
                continue
            for hood_dir in list(region_dir.iterdir()):
                if not hood_dir.is_dir():
                    continue
                if f"{region_dir.name}/{hood_dir.name}" not in keep_slugs:
                    _shutil.rmtree(hood_dir)
                    pruned += 1
            if region_dir.is_dir() and not any(region_dir.iterdir()):
                region_dir.rmdir()
        return pruned
    for sub in list(parent.iterdir()):
        if sub.is_dir() and sub.name not in keep_slugs and sub.name != "_manifest.json":
            _shutil.rmtree(sub)
            pruned += 1
    return pruned


def main() -> int:
    print("Collecting cross-cut data from all regions...")
    agg = collect_all()
    renderer = TemplateRenderer()

    n_g = write_grape_pages(renderer, agg["grape"])
    n_s = write_style_pages(renderer, agg["style"])
    n_w = write_world_pages(renderer, agg["world"])
    n_n = write_neighborhood_pages(renderer, agg["neighborhood"])

    # Prune orphans (entries that stopped appearing). Only keep slugs that
    # actually produced a page (non-empty regions).
    keep_grape = {s for s, b in agg["grape"].items() if any(b["regions"].values())}
    keep_style = {s for s, b in agg["style"].items() if any(b["regions"].values())}
    keep_world = {s for s, b in agg["world"].items() if b["regions"]}
    pruned_g = _prune_stale(CONTENT_DIR / "grape", keep_grape)
    pruned_s = _prune_stale(CONTENT_DIR / "style", keep_style)
    pruned_w = _prune_stale(CONTENT_DIR / "world", keep_world)
    pruned_n = _prune_stale(
        CONTENT_DIR / "neighborhood",
        {f"{r}/{h}" for (r, h) in agg["neighborhood"].keys()},
        two_level=True,
    )

    # Manifests for the chrome + scoped index generators.
    grape_entries = []
    for s, b in sorted(agg["grape"].items()):
        regions, _ = _regions_list(b["regions"])
        if not regions:
            continue
        grape_entries.append({
            "slug": s, "display": b["display"],
            "regions": [{"country_slug": r["country_slug"], "region_slug": r["region_slug"],
                         "region_name": r["region_name"], "n": len(r["vineyards"])} for r in regions],
        })
    _write_manifest(CONTENT_DIR / "grape", grape_entries)

    style_entries = []
    for s, b in sorted(agg["style"].items()):
        regions, _ = _regions_list(b["regions"])
        if not regions:
            continue
        style_entries.append({
            "slug": s, "display": b["display"],
            "regions": [{"country_slug": r["country_slug"], "region_slug": r["region_slug"],
                         "region_name": r["region_name"], "n": len(r["vineyards"])} for r in regions],
        })
    _write_manifest(CONTENT_DIR / "style", style_entries)

    world_entries = []
    for s, b in sorted(agg["world"].items()):
        if not b["regions"]:
            continue
        world_entries.append({"slug": s, "display": b["display"],
                              "regions": sorted(b["regions"], key=lambda r: r["region_name"].lower())})
    _write_manifest(CONTENT_DIR / "world", world_entries)

    nb_entries = []
    for (region_slug, hood_slug), b in sorted(agg["neighborhood"].items()):
        nb_entries.append({
            "slug": hood_slug, "display": b["display"],
            "region_slug": region_slug, "region_name": b["region_name"],
            "country_slug": b["country_slug"],
        })
    _write_manifest(CONTENT_DIR / "neighborhood", nb_entries)

    print(f"  grape pages:         {n_g}  (pruned {pruned_g} stale)")
    print(f"  style pages:         {n_s}  (pruned {pruned_s} stale)")
    print(f"  world pages:         {n_w}  (pruned {pruned_w} stale)")
    print(f"  neighborhood pages:  {n_n}  (pruned {pruned_n} stale)")
    print(f"DONE: {n_g + n_s + n_w + n_n} cross-cut pages written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
