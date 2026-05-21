#!/usr/bin/env python3
"""
Render templates/home.html into content/index.html using a hand-edited
site-data/home.json.

site-data/home.json shape:
{
  "featured_cities": [ {"name": "Paris", "url": "/france/paris/", "tagline": "...", "image": "..."} ],
  "trending_dishes": [ {"name": "...", "description": "...", "city": "Paris", "where": "..."} ]
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
HOME_JSON = REPO_ROOT / "site-data" / "home.json"
OUT = REPO_ROOT / "content" / "index.html"


def collect_trending_dishes(limit: int = 12) -> list[dict]:
    """Walk every city's signature-dishes.json, return the top `limit`
    sorted by editorial_score, with at most one dish per city for
    geographic diversity. Falsifies "all Paris" homepage bias.
    """
    pool = []
    for sig_path in REPO_ROOT.glob("site-data/*/*/data/signature-dishes.json"):
        parts = sig_path.parts
        city_slug = parts[-3]
        country_slug = parts[-4]
        try:
            data = json.loads(sig_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        city_display = city_slug.replace("-", " ").title()
        items = data.get("signature_dishes") or data.get("entities") or []
        for it in items:
            name = it.get("name") or it.get("dish")
            if not name:
                continue
            try:
                score = float(it.get("editorial_score", 0) or 0)
            except (TypeError, ValueError):
                score = 0.0
            wte = it.get("where_to_eat") or []
            where = wte[0] if isinstance(wte, list) and wte and isinstance(wte[0], str) else (
                wte[0].get("name", "") if isinstance(wte, list) and wte and isinstance(wte[0], dict) else ""
            )
            dish_slug = it.get("slug")
            # Prefer the city-scoped dish page (always emitted by
            # generate_city_dish.py) so the link lands on the dish's
            # local-variant page, not the global cross-cut.
            url = f"/{country_slug}/{city_slug}/dish/{dish_slug}/" if dish_slug else f"/{country_slug}/{city_slug}/"
            pool.append({
                "_score": score,
                "_city_slug": city_slug,
                "name": name,
                "description": (it.get("description") or "")[:200],
                "city": city_display,
                "where": where,
                "editorial_score": score,
                "url": url,
            })
    pool.sort(key=lambda x: (-x["_score"], x["name"]))
    chosen = []
    seen_cities = set()
    for d in pool:
        if d["_city_slug"] in seen_cities:
            continue
        seen_cities.add(d["_city_slug"])
        chosen.append({k: v for k, v in d.items() if not k.startswith("_")})
        if len(chosen) >= limit:
            break
    return chosen


def main() -> int:
    home = {}
    if HOME_JSON.exists():
        home = json.loads(HOME_JSON.read_text(encoding="utf-8"))

    home["trending_dishes"] = collect_trending_dishes()

    renderer = TemplateRenderer()
    template = renderer.env.get_template("home.html")

    title = "TableJourney. Where the world eats"
    description = (
        "Food travel guides to the world's great eating cities. Restaurants, "
        "street food, signature dishes, hidden gems and food culture, "
        "written by editors who eat in person."
    )
    canonical = "https://tablejourney.com/"
    # Homepage OG: our own branded global-table image with the
    # TABLEJOURNEY wordmark. Rebuild via scripts/build_og_home.py.
    og_image = "https://tablejourney.com/img/og-home.jpg"

    seo = {
        "meta": {
            "title": title,
            "description": description,
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
            "author": "TableJourney Editorial",
        },
        "open_graph": {
            "og_title": title,
            "og_description": description,
            "og_url": canonical,
            "og_type": "website",
            "og_image": og_image,
            "og_image_alt": "TableJourney. food travel guides",
            "og_locale": "en_US",
        },
        "twitter": {
            "twitter_card": "summary_large_image",
            "twitter_title": title,
            "twitter_description": description,
            "twitter_image": og_image,
            "twitter_image_alt": "TableJourney. food travel guides",
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
    first_city = next(
        (c for c in (home.get("featured_cities") or [])
         if c.get("status") != "coming-soon" and c.get("image")),
        None,
    )
    hero_image_url = first_city["image"] if first_city else None

    html = template.render(
        home=home,
        seo=seo,
        analytics={"page_type": "home", "destination": "global"},
        base_path="",
        topic_nav=FOOD_TOPIC_NAV,
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
