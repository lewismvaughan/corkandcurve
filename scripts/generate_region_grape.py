#!/usr/bin/env python3
"""Generate region x grape cross-cut pages.

For every region, emit one page per grape varietal grown there, listing the
estates that grow it:

    /<country>/<region>/grape/<grape-slug>/

This is the wine analog of TableJourney's generate_city_cuisine.py. The
region-scoped grape page captures long-tail "where to taste <grape> in
<region>" intent and is linked DOWN to from /<country>/<region>/grapes/.

Re-runnable; rewrites and prunes every run.

Usage:
    python scripts/generate_region_grape.py
    python scripts/generate_region_grape.py <country> <region>   # one region
"""

from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.data_loader import SITE_DATA, load_country_data, get_all_regions
from utils.seo import meta_desc as _meta_desc
from utils.slug import slugify
from utils.template_renderer import TemplateRenderer

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

# Topics whose entities carry varietal lists worth aggregating into a
# region x grape page.
VARIETAL_TOPICS = ("vineyards", "tasting_rooms", "hidden_gems", "budget_wines")
# Minimum estates before a region x grape page is worth emitting.
MIN_ESTATES = 1


def _collect_region_grapes(research: dict) -> dict:
    """Return {grape_slug: {"display": name, "vineyards": [entity, ...]}}."""
    grape_display = {}
    for g in research.get("signature_grapes", []) or []:
        if isinstance(g, dict) and g.get("name"):
            grape_display[slugify(g["name"])] = g["name"]

    by_grape: dict[str, dict] = defaultdict(lambda: {"display": "", "vineyards": []})
    for tk in VARIETAL_TOPICS:
        for v in research.get(tk, []) or []:
            if not isinstance(v, dict):
                continue
            varietals = v.get("varietals") or v.get("varietals_focus") or []
            if isinstance(varietals, str):
                varietals = [varietals]
            for varietal in varietals:
                # varietals may be plain strings ("Sangiovese") or
                # {grape, pct} dicts (the wines.json shape). Normalise to
                # the grape name before slugifying so a dict never gets
                # stringified into a slug like "grape-sangiovese-pct-60".
                if isinstance(varietal, dict):
                    varietal = varietal.get("grape") or varietal.get("name") or ""
                if not isinstance(varietal, str):
                    continue
                gslug = slugify(varietal)
                if not gslug:
                    continue
                gb = by_grape[gslug]
                gb["display"] = grape_display.get(gslug) or gb["display"] or varietal
                ident = v.get("slug") or v.get("name")
                if ident and not any((e.get("slug") or e.get("name")) == ident for e in gb["vineyards"]):
                    gb["vineyards"].append(v)
    return by_grape


def _all_regions() -> list[tuple[str, str]]:
    pairs = []
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        for region in get_all_regions(country_dir.name):
            pairs.append((country_dir.name, region))
    return pairs


def generate_for_region(renderer: TemplateRenderer, country_slug: str, region_slug: str) -> tuple[int, int]:
    """Emit region x grape pages for one region. Returns (written, pruned)."""
    try:
        data = load_country_data(country_slug, region_slug=region_slug)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"  [WARN] skipping {country_slug}/{region_slug}: {exc}")
        return 0, 0
    research = data.get("research", {})
    region_name = data.get("destination", {}).get("name", region_slug.replace("-", " ").title())
    by_grape = _collect_region_grapes(research)

    template = renderer.env.get_template("cross-cuts/region-grape.html")
    grape_root = CONTENT_DIR / country_slug / region_slug / "grape"
    written = 0
    keep: set[str] = set()

    for gslug, blob in by_grape.items():
        vineyards = blob["vineyards"]
        if len(vineyards) < MIN_ESTATES:
            continue
        display = blob["display"]
        canonical = f"{BASE}/{country_slug}/{region_slug}/grape/{gslug}/"
        title = f"{display} in {region_name} | Cork & Curve"
        n = len(vineyards)
        estate_phrase = "1 estate" if n == 1 else f"{n} estates"
        desc = _meta_desc(
            f"Where to taste {display} in {region_name}: {estate_phrase} editor-picked on Cork & Curve, with how the region expresses the grape and how to book a visit.",
            f"Where to taste {display} in {region_name}: {estate_phrase} editor-picked on Cork & Curve.",
        )
        ctx = {
            "grape": display,
            "grape_slug": gslug,
            "region_name": region_name,
            "region_slug": region_slug,
            "country_slug": country_slug,
            "vineyards": vineyards,
            "total_entities": n,
            "breadcrumb": [
                {"name": "Home", "url": "/"},
                {"name": region_name, "url": f"/{country_slug}/{region_slug}/"},
                {"name": "Grapes", "url": f"/{country_slug}/{region_slug}/grapes/"},
                {"name": display, "url": None},
            ],
            "seo": {
                "meta": {"title": title, "description": desc, "canonical_url": canonical,
                         "robots": "index, follow, max-image-preview:large, max-snippet:-1"},
                "open_graph": {"og_title": title, "og_description": desc, "og_url": canonical,
                               "og_type": "article", "og_image": f"{BASE}/og/default.jpg",
                               "og_image_alt": f"{display} in {region_name}", "og_locale": "en_US"},
                "twitter": {}, "alternates": [],
            },
            "destination": {"name": region_name, "country": ""},
            "analytics": {"page_type": "region-grape", "destination": f"{region_slug}-{gslug}",
                          "country": country_slug, "region": region_slug},
            "base_path": "../../../..",
        }
        out = grape_root / gslug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.render(**ctx), encoding="utf-8")
        keep.add(gslug)
        written += 1

    # Prune stale grape dirs in this region.
    pruned = 0
    if grape_root.exists():
        for sub in list(grape_root.iterdir()):
            if sub.is_dir() and sub.name not in keep:
                shutil.rmtree(sub)
                pruned += 1
    return written, pruned


def main() -> int:
    renderer = TemplateRenderer()
    if len(sys.argv) == 3:
        pairs = [(sys.argv[1], sys.argv[2])]
    else:
        pairs = _all_regions()

    total_w = total_p = 0
    for country_slug, region_slug in pairs:
        w, p = generate_for_region(renderer, country_slug, region_slug)
        total_w += w
        total_p += p
        if w or p:
            print(f"  {country_slug}/{region_slug}: {w} region-grape pages ({p} pruned)")
    print(f"DONE: {total_w} region-grape pages written, {total_p} pruned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
