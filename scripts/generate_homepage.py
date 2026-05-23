#!/usr/bin/env python3
"""
Render templates/home.html into content/index.html.

Homepage data is derived from the filesystem, NOT hand-edited:

- `featured_regions` — discovered by walking every
  `site-data/<country>/<region>/data/region.json` that has real content
  (>= 1 vineyard). Bordeaux is the only live region today; as new
  regions ship the homepage picks them up automatically without a
  home.json edit.

- `trending_wines` — the "featured wines" rotation. Walks every
  `wines.json` across regions, ranks by editorial_score, dedups by
  producer, then rotates a window of 8 cuvées on a 3-day deterministic
  cadence (the rotation seed is `(today - epoch) // 3`, so the same
  window stays stable until the next 3-day boundary). Each cuvée links
  to its global `/wine/<producer>/<slug>/` page.

`site-data/home.json` is still loaded for any HAND-CURATED extras
(topics list, hero copy overrides) but featured_regions and
trending_wines are auto-discovered and overwrite whatever's in JSON.
"""

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.data_loader import compute_price_tier  # noqa: E402
from utils.template_renderer import TemplateRenderer, WINE_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
HOME_JSON = REPO_ROOT / "site-data" / "home.json"
OUT = REPO_ROOT / "content" / "index.html"


# 3-day rotation epoch. Fixed so the same window stays stable across
# any rebuild on the same 3-day calendar slice. Moving this date
# shifts the rotation cycle but not the content pool.
_ROTATION_EPOCH = datetime.date(2026, 1, 1)


def _rotation_window_index(window_days: int = 3,
                           today: datetime.date | None = None) -> int:
    """Days since _ROTATION_EPOCH divided by window length. Deterministic
    per-3-day-slice; flips to next index on the boundary."""
    today = today or datetime.date.today()
    return max(0, (today - _ROTATION_EPOCH).days) // window_days


def collect_featured_regions() -> list[dict]:
    """Discover every region with real (non-stub) content.

    Walks site-data/<country>/<region>/data/region.json. A region must
    have >= 1 vineyard to count as "live" — empty scaffolds (regions
    created with new_region.py but never researched) don't ship to the
    homepage marquee. Sorted by vineyard count desc so the most-mature
    region surfaces first; ties broken by display name.
    """
    out = []
    for region_path in sorted(REPO_ROOT.glob("site-data/*/*/data/region.json")):
        parts = region_path.parts
        region_slug = parts[-3]
        country_slug = parts[-4]
        try:
            data = json.loads(region_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (data.get("_metadata") or {}).get("status") == "stub":
            continue
        dest = data.get("destination") or {}
        name = dest.get("name") or region_slug.replace("-", " ").title()
        # Filesystem-side check: at least 1 vineyard. region.json may
        # not embed vineyards inline, so read vineyards.json directly.
        v_path = region_path.parent / "vineyards.json"
        try:
            v_data = json.loads(v_path.read_text(encoding="utf-8"))
            n_vineyards = len(v_data.get("vineyards") or [])
        except (OSError, json.JSONDecodeError):
            n_vineyards = 0
        if n_vineyards == 0:
            continue
        out.append({
            "name": name,
            "url": f"/{country_slug}/{region_slug}/",
            "tagline": dest.get("tagline") or (dest.get("overview") or "")[:120],
            "image": dest.get("hero_image") or None,
            "image_alt": dest.get("hero_image_alt") or f"{name} wine country",
            "country": dest.get("country") or country_slug.replace("-", " ").title(),
            "status": "live",
            "_n_vineyards": n_vineyards,
        })
    out.sort(key=lambda r: (-r["_n_vineyards"], r["name"]))
    for r in out:
        r.pop("_n_vineyards", None)
    return out


def collect_trending_wines(limit: int = 8, window_days: int = 3,
                           min_score: float = 4.0,
                           pool_size: int = 30,
                           today: datetime.date | None = None) -> list[dict]:
    """Featured-wine carousel with deterministic 3-day rotation.

    Pool: every cuvée from every region's wines.json with
    `editorial_score >= min_score`, dedup'd to one cuvée per producer
    (geographic + producer variety), top `pool_size` by score.

    Rotation: at window index `i = days_since_epoch // window_days`,
    return `limit` cuvées starting at offset `(i * limit) % pool_size`
    and wrapping to the head when needed. So:
      - Same window → same 8 wines. SEO-stable HTML.
      - Window advances → next 8 wines rotate in.
      - Full pool cycles every `ceil(pool_size / limit)` windows
        (with pool_size=30, limit=8: every 4 windows = 12 days the
        full top-30 has been featured).

    Linking strategy: every cuvée gets its own /wine/<producer>/<slug>/
    page now, so the homepage card links there directly (no more
    signature-wines anchor fallback).
    """
    pool = []
    for wines_path in sorted(REPO_ROOT.glob("site-data/*/*/data/wines.json")):
        parts = wines_path.parts
        region_slug = parts[-3]
        country_slug = parts[-4]
        try:
            data = json.loads(wines_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        # Region display name comes from sibling region.json
        try:
            rdata = json.loads((wines_path.parent / "region.json").read_text(encoding="utf-8"))
            region_name = (rdata.get("destination") or {}).get("name") or region_slug.replace("-", " ").title()
        except (OSError, json.JSONDecodeError):
            region_name = region_slug.replace("-", " ").title()
        for w in data.get("wines") or []:
            if not isinstance(w, dict):
                continue
            slug = w.get("slug")
            producer = w.get("producer")
            if not slug or not producer:
                continue
            try:
                score = float(w.get("editorial_score") or 0)
            except (TypeError, ValueError):
                score = 0.0
            if score < min_score:
                continue
            taste = w.get("taste") or {}
            desc = taste.get("summary") or w.get("description") or ""
            if len(desc) > 200:
                desc = desc[:197].rstrip() + "..."
            pool.append({
                "_score": score,
                "_producer": producer,
                "_region": region_slug,
                "name": w.get("name") or slug,
                "producer": w.get("producer_name") or producer,
                "region": region_name,
                "description": desc,
                "editorial_score": score,
                "price_tier": compute_price_tier(w.get("price_band")),
                "url": f"/wine/{producer}/{slug}/",
            })

    # Sort top-scoring first; deterministic name tiebreaker
    pool.sort(key=lambda x: (-x["_score"], x["name"]))

    # Dedup by producer for variety; also cap at pool_size
    seen_producers: set[str] = set()
    deduped: list[dict] = []
    for w in pool:
        if w["_producer"] in seen_producers:
            continue
        seen_producers.add(w["_producer"])
        deduped.append(w)
        if len(deduped) >= pool_size:
            break

    if not deduped:
        return []

    # Deterministic 3-day rotation window
    window_index = _rotation_window_index(window_days, today=today)
    start = (window_index * limit) % len(deduped)
    chosen = deduped[start:start + limit]
    if len(chosen) < limit:
        chosen += deduped[:limit - len(chosen)]

    # Strip internal sort keys before returning to template
    return [{k: v for k, v in w.items() if not k.startswith("_")} for w in chosen]


def main() -> int:
    home = {}
    if HOME_JSON.exists():
        home = json.loads(HOME_JSON.read_text(encoding="utf-8"))

    # Auto-discover live regions. Any home.json `featured_regions` value
    # is overwritten — the filesystem is the source of truth.
    home["featured_regions"] = collect_featured_regions()

    # 3-day-rotating featured wines.
    home["trending_wines"] = collect_trending_wines(limit=8, window_days=3)
    # Date marker so the template can show "Updated every 3 days · Last refresh DATE".
    home["trending_wines_window_started"] = (
        _ROTATION_EPOCH + datetime.timedelta(days=_rotation_window_index() * 3)
    ).isoformat()
    home["trending_wines_window_days"] = 3

    print(f"  Featured regions: {len(home['featured_regions'])} live")
    print(f"  Featured wines:   {len(home['trending_wines'])} cuvée(s) "
          f"(window started {home['trending_wines_window_started']})")

    renderer = TemplateRenderer()
    template = renderer.env.get_template("home.html")

    title = "Cork & Curve. Where the world drinks"
    description = (
        "Wine and spirits travel guides to the world's great wine regions. "
        "Vineyards, tasting rooms, signature wines, hidden cellars and wine "
        "culture, written by editors who taste in person."
    )
    canonical = "https://corkandcurve.com/"
    # Homepage OG: our own branded image with the CORK & CURVE wordmark.
    # Rebuild via scripts/build_og_home.py.
    og_image = "https://corkandcurve.com/img/og-home.jpg"

    seo = {
        "meta": {
            "title": title,
            "description": description,
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
            "author": "Cork & Curve Editorial",
        },
        "open_graph": {
            "og_title": title,
            "og_description": description,
            "og_url": canonical,
            "og_type": "website",
            "og_image": og_image,
            "og_image_alt": "Cork & Curve. wine travel guides",
            "og_locale": "en_US",
        },
        "twitter": {
            "twitter_card": "summary_large_image",
            "twitter_title": title,
            "twitter_description": description,
            "twitter_image": og_image,
            "twitter_image_alt": "Cork & Curve. wine travel guides",
        },
        "article": {},
        "structured_data": {
            "breadcrumb_items": [
                {"position": 1, "name": "Home", "url": canonical},
            ],
        },
    }

    # First city-card image becomes the LCP element on mobile (Lighthouse
    # confirmed). Preload it so the fetch starts during HTML parse instead
    # of waiting for the marquee img tag to be parsed. See STANDARDS §2.
    first_region = next(
        (c for c in (home.get("featured_regions") or [])
         if c.get("status") != "coming-soon" and c.get("image")),
        None,
    )
    hero_image_url = first_region["image"] if first_region else None

    html = template.render(
        home=home,
        seo=seo,
        analytics={"page_type": "home", "destination": "global"},
        base_path="",
        topic_nav=WINE_TOPIC_NAV,
        breadcrumb=None,
        current_year=2026,
        hero_image_url=hero_image_url,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
