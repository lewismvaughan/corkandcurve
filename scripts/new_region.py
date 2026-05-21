#!/usr/bin/env python3
"""
Scaffold the JSON data tree for a new wine region, ready for the wine-research agent to fill.

Usage:
    python scripts/new_region.py france bordeaux
    python scripts/new_region.py italy tuscany --name "Tuscany" --country "Italy"

Creates site-data/<country>/<region>/data/ with 28 stub files:
    region.json + neighborhoods.json + 24 wine topic files + nightlife.json + dietary.json

Each stub holds a top-level dict keyed to the field the templates read.
Re-runs are idempotent unless --force is given.
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# 24 wine topic slugs <-> template-facing research keys
TOPIC_KEYS = {
    "vineyards":          "vineyards",
    "tasting-rooms":      "tasting_rooms",
    "wine-bars":          "wine_bars",
    "wine-restaurants":   "wine_restaurants",
    "wine-retailers":     "wine_retailers",
    "wine-schools":       "wine_schools",
    "wine-tours":         "wine_tours",
    "wine-festivals":     "wine_festivals",
    "distilleries":       "distilleries",
    "wine-museums":       "wine_museums",
    "wine-hotels":        "wine_hotels",
    "wine-experiences":   "wine_experiences",
    "wine-history":       "wine_history",
    "seasonal-wine":      "seasonal_wine",
    "signature-wines":    "signature_wines",
    "signature-grapes":   "signature_grapes",
    "budget-wines":       "budget_wines",
    "hidden-gems":        "hidden_gems",
    "day-trips-wine":     "day_trips_wine",
    "itineraries":        "itineraries",
    "food-pairing":       "food_pairing",
}

NIGHTLIFE_SUBKEYS = (
    "wine_bars_late", "listening_bars", "candle_lit", "lounges",
    "fortified_specialists", "late_tastings", "sparkling_rooms",
)

DIETARY_SUBKEYS = (
    "biodynamic", "organic", "natural", "vegan_winemaking", "lowsulfite",
)


def write_stub(path: Path, payload: dict, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("country_slug")
    p.add_argument("region_slug")
    p.add_argument("--name", default=None)
    p.add_argument("--country", default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    name = args.name or args.region_slug.replace("-", " ").title()
    country = args.country or args.country_slug.replace("-", " ").title()
    region_dir = SITE_DATA / args.country_slug / args.region_slug / "data"
    print(f"Scaffolding {args.country_slug}/{args.region_slug} at {region_dir}")

    written = skipped = 0

    # region.json
    region = {
        "destination": {
            "slug": args.region_slug,
            "name": name,
            "country": country,
            "country_slug": args.country_slug,
            "hero_image": "",
            "hero_image_source_url": "",
            "blurb": "",
            "type": "wine-region",
        },
        "seo": {"pages": {}},
        "faqs": [],
    }
    if write_stub(region_dir / "region.json", region, args.force):
        written += 1
    else:
        skipped += 1

    # neighborhoods (sub-appellations) stub
    if write_stub(region_dir / "neighborhoods.json", {"neighborhoods": []}, args.force):
        written += 1
    else:
        skipped += 1

    # 24 topic files (mostly flat list-shaped)
    for slug, key in TOPIC_KEYS.items():
        path = region_dir / f"{slug}.json"
        if write_stub(path, {key: []}, args.force):
            written += 1
        else:
            skipped += 1

    # nightlife.json (nested subkeys)
    nightlife = {"nightlife": {sk: [] for sk in NIGHTLIFE_SUBKEYS}}
    if write_stub(region_dir / "nightlife.json", nightlife, args.force):
        written += 1
    else:
        skipped += 1

    # dietary.json (nested subkeys)
    dietary = {"dietary": {sk: [] for sk in DIETARY_SUBKEYS}}
    if write_stub(region_dir / "dietary.json", dietary, args.force):
        written += 1
    else:
        skipped += 1

    total = written + skipped
    print(f"Done: {written} written, {skipped} skipped ({total} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
