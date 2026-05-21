#!/usr/bin/env python3
"""Render a static map thumbnail per geocoded entity.

For each entity with cached coordinates, emit a 600x400 JPEG showing
the entity's location pinned on an OpenStreetMap tile background.
Output: content/maps/<country>/<city>/<topic>/<entity-slug>.jpg

The thumbnail wraps inline on the entity page's Location section as a
decorative + trust-building visual. Zero JS, just an <img> — keeps LCP
clean while still telling the reader "this is where it is" before they
click the directions link.

Reads data/geocode-cache.json (built by scripts/geocode_entities.py).
Skips entities whose address isn't yet in the cache so we never render
a map without a known pin location.

Re-runnable; uses the cached coords + OSM tiles. OSM tile policy
permits this scale of usage; for sustained > 10k req/day we'd switch
to a paid tile provider or self-host. Caches PNG tile downloads in
~/.cache/staticmap via the library's internal cache.

Usage:
    python scripts/build_entity_maps.py                  # process all
    python scripts/build_entity_maps.py --city paris     # one city
    python scripts/build_entity_maps.py --limit 50       # cap for testing
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image
from staticmap import StaticMap, CircleMarker

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
CONTENT = REPO / "content"
GEOCODE_CACHE = REPO / "data" / "geocode-cache.json"

MAP_W, MAP_H = 600, 400
ZOOM = 15  # close enough to see streets, far enough to give context
TILE_URL = "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
# TJ terracotta pin with a cream centre dot
PIN_OUTER = "#C84A2E"
PIN_INNER = "#FAF7F0"


def _cache_key(address: str, city_name: str) -> str:
    blob = f"{address.lower().strip()}|{city_name.lower().strip()}"
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def _load_geocode() -> dict:
    if not GEOCODE_CACHE.exists():
        return {}
    try:
        return json.loads(GEOCODE_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _render_one(lat: float, lon: float, out_path: Path) -> None:
    """Render a single 600x400 JPEG with the TJ-styled pin at (lat, lon)."""
    sm = StaticMap(MAP_W, MAP_H, url_template=TILE_URL)
    sm.add_marker(CircleMarker((lon, lat), PIN_OUTER, 18))
    sm.add_marker(CircleMarker((lon, lat), PIN_INNER, 7))
    img = sm.render(zoom=ZOOM)
    # Convert to RGB (drop alpha if any) and save as JPEG for ~5x smaller
    # files than PNG. 600x400 PNGs from staticmap come in at ~400KB; the
    # JPEG at quality 82 is ~30-50KB which is the right LCP budget.
    if img.mode != "RGB":
        img = img.convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=82, optimize=True, progressive=True)


def _walk_entities(only_city: str | None) -> list[tuple[str, str, str, str, str, str]]:
    """Yield (country, city, city_name, topic_slug, entity_slug, address)."""
    sources = [
        ("restaurants", "restaurants.json"),
        ("fine-dining", "fine-dining.json"),
        ("casual-dining", "casual-dining.json"),
        ("cafes", "cafes.json"),
        ("bakeries", "bakeries.json"),
        ("coffee-roasters", "coffee-roasters.json"),
        ("wine-bars", "wine-bars.json"),
        ("bars", "bars.json"),
        ("street-food", "street-food.json"),
        ("breweries", "breweries.json"),
        ("markets", "markets.json"),
        ("food-tours", "food-tours.json"),
        ("festivals", "festivals.json"),
        ("cooking-classes", "cooking-classes.json"),
        ("budget-eating", "budget-eating.json"),
        ("hidden-gems", "hidden-gems.json"),
        ("brunch", "brunch.json"),
        ("late-night", "late-night.json"),
        ("day-trips-food", "day-trips-food.json"),
    ]
    research_keys = {
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
    out = []
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            if only_city and city_dir.name != only_city:
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

            for topic_slug, filename in sources:
                p = city_dir / "data" / filename
                if not p.exists():
                    continue
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                key = research_keys[topic_slug]
                for e in (d.get(key) or []):
                    if not isinstance(e, dict):
                        continue
                    slug = e.get("slug")
                    addr = e.get("address") or e.get("location") or e.get("meeting_point")
                    if not slug or not addr:
                        continue
                    out.append((country, city, city_name, topic_slug, slug, addr))

            # Dietary sub-buckets
            d_path = city_dir / "data" / "dietary.json"
            if d_path.exists():
                try:
                    dd = json.loads(d_path.read_text(encoding="utf-8"))
                    for diet_key, entries in (dd.get("dietary") or {}).items():
                        if not isinstance(entries, list):
                            continue
                        for e in entries:
                            if not isinstance(e, dict):
                                continue
                            slug = e.get("slug")
                            addr = e.get("address")
                            if not slug or not addr:
                                continue
                            out.append((country, city, city_name, "dietary", slug, addr))
                except (OSError, json.JSONDecodeError):
                    pass
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--city", default=None, help="Restrict to one city slug")
    p.add_argument("--limit", type=int, default=None, help="Cap for testing")
    p.add_argument("--force", action="store_true", help="Re-render even if output exists")
    args = p.parse_args()

    cache = _load_geocode()
    targets = _walk_entities(args.city)

    rendered = 0
    skipped_no_coord = 0
    skipped_existing = 0
    seen_paths: set[Path] = set()
    for country, city, city_name, topic_slug, slug, address in targets:
        if args.limit is not None and rendered >= args.limit:
            print(f"  --limit {args.limit} reached")
            break
        ck = _cache_key(address, city_name)
        entry = cache.get(ck)
        if not entry or not entry.get("ok"):
            skipped_no_coord += 1
            continue
        out_path = CONTENT / "maps" / country / city / topic_slug / f"{slug}.jpg"
        seen_paths.add(out_path)
        if out_path.exists() and not args.force:
            skipped_existing += 1
            continue
        try:
            _render_one(entry["lat"], entry["lon"], out_path)
        except Exception as exc:  # noqa: BLE001
            print(f"  [WARN] render failed for {country}/{city}/{topic_slug}/{slug}: {exc}")
            continue
        rendered += 1
        if rendered % 100 == 0:
            print(f"  ... rendered {rendered}")

    print(f"DONE. rendered={rendered}  skipped_existing={skipped_existing}  skipped_no_coord={skipped_no_coord}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
