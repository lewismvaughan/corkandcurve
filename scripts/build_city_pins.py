#!/usr/bin/env python3
"""Build a lean per-city pins JSON for the interactive city-hub map.

For each city, walks every entity-bearing topic + dietary sub-buckets,
joins each entity to its cached geocode, and writes a compact JSON to
content/<country>/<city>/_pins.json:

  {
    "city": {"name": "Paris", "center": [48.857, 2.347], "country": "France"},
    "pins": [
      {"slug": "frenchie", "name": "Frenchie", "topic": "restaurants",
       "url": "/france/paris/restaurants/frenchie/", "lat": 48.872,
       "lng": 2.349, "score": 4.6, "cuisine": "French bistro"},
      ...
    ]
  }

Loaded client-side by the city-hub Leaflet map on intersection (lazy).
Typical size: 5-25 KB per city — well below the 50 KB Leaflet JS itself.

City center is the centroid of all pins (median lat/lng) so the map
opens framed on the entities, not a hardcoded coordinate.

Usage:
    python scripts/build_city_pins.py                # all cities
    python scripts/build_city_pins.py --city paris   # one
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.slug import slugify  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
CONTENT = REPO / "content"
GEOCODE_CACHE = REPO / "data" / "geocode-cache.json"

# topic-slug -> research-key in region JSON
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


def _cache_key(address: str, city_name: str) -> str:
    blob = f"{address.lower().strip()}|{city_name.lower().strip()}"
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def _load_geo() -> dict:
    if not GEOCODE_CACHE.exists():
        return {}
    try:
        return json.loads(GEOCODE_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _walk_city(country: str, city: str, city_name: str, geocache: dict) -> list[dict]:
    pins: list[dict] = []
    data_dir = SITE_DATA / country / city / "data"

    for topic_slug, research_key in ENTITY_TOPICS.items():
        p = data_dir / f"{topic_slug}.json"
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in (d.get(research_key) or []):
            if not isinstance(e, dict):
                continue
            slug = e.get("slug")
            addr = e.get("address") or e.get("location") or e.get("meeting_point")
            name = e.get("name") or e.get("operator")
            if not slug or not addr or not name:
                continue
            ck = _cache_key(addr, city_name)
            entry = geocache.get(ck)
            if not entry or not entry.get("ok"):
                continue
            pin = {
                "slug": slug,
                "name": name,
                "topic": topic_slug,
                "url": f"/{country}/{city}/{topic_slug}/{slug}/",
                "lat": round(entry["lat"], 5),
                "lng": round(entry["lon"], 5),
            }
            if isinstance(e.get("editorial_score"), (int, float)):
                pin["score"] = round(float(e["editorial_score"]), 1)
            if e.get("classification"):
                pin["classification"] = e["classification"]
            varietals = e.get("varietals") or e.get("varietals_focus")
            if varietals:
                first = varietals[0] if isinstance(varietals, list) and varietals else varietals
                if isinstance(first, str):
                    pin["grape"] = first
                    pin["grape_slug"] = slugify(first)  # filterable by region × grape pages
            if e.get("neighborhood"):
                pin["hood"] = e["neighborhood"]
            pins.append(pin)

    # Dietary sub-buckets — each entity lives under /<city>/dietary/<slug>/
    d_path = data_dir / "dietary.json"
    if d_path.exists():
        try:
            dd = json.loads(d_path.read_text(encoding="utf-8"))
            for diet, entries in (dd.get("dietary") or {}).items():
                if not isinstance(entries, list):
                    continue
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    slug = e.get("slug")
                    addr = e.get("address")
                    name = e.get("name")
                    if not slug or not addr or not name:
                        continue
                    ck = _cache_key(addr, city_name)
                    entry = geocache.get(ck)
                    if not entry or not entry.get("ok"):
                        continue
                    pin = {
                        "slug": slug,
                        "name": name,
                        "topic": "dietary",
                        "diet": diet,
                        "url": f"/{country}/{city}/dietary/{slug}/",
                        "lat": round(entry["lat"], 5),
                        "lng": round(entry["lon"], 5),
                    }
                    if isinstance(e.get("editorial_score"), (int, float)):
                        pin["score"] = round(float(e["editorial_score"]), 1)
                    pins.append(pin)
        except (OSError, json.JSONDecodeError):
            pass

    # Dedupe by (slug, topic) — entity might appear in multiple sources
    # (e.g. budget_eating + restaurants). First write wins.
    seen: set[tuple[str, str]] = set()
    unique = []
    for p in pins:
        key = (p["slug"], p["topic"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _city_center(pins: list[dict], fallback_lat: float = 48.857, fallback_lng: float = 2.347) -> list[float]:
    """Median lat/lng across pins so the initial framing isn't skewed by
    an outlier (a day-trip in the Loire when the city is Paris)."""
    if not pins:
        return [fallback_lat, fallback_lng]
    lats = sorted(p["lat"] for p in pins)
    lngs = sorted(p["lng"] for p in pins)
    return [round(statistics.median(lats), 5), round(statistics.median(lngs), 5)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    geocache = _load_geo()
    written = 0
    skipped_no_pins = 0
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            if args.city and city_dir.name != args.city:
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
            country_name = (rdata.get("destination") or {}).get("country") or country.replace("-", " ").title()

            pins = _walk_city(country, city, city_name, geocache)
            if not pins:
                skipped_no_pins += 1
                continue
            blob = {
                "city": {
                    "slug": city,
                    "name": city_name,
                    "country": country_name,
                    "center": _city_center(pins),
                    "n": len(pins),
                },
                "pins": pins,
            }
            out = CONTENT / country / city / "_pins.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(blob, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            written += 1

    print(f"wrote {written} _pins.json files (skipped {skipped_no_pins} cities with no geocoded entities yet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
