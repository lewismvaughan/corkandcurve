#!/usr/bin/env python3
"""Generate per-country signature-dish rollup pages.

For every (country, dish) with the dish appearing in >=2 cities in the
country, emit a country-level page that shows where to eat each city's
local variant:

  /<country>/dish/carbonara/        (Rome, Naples, ...)
  /<country>/dish/pierogi/          (Warsaw, Krakow, Gdansk, ...)
  /<country>/dish/pho/              (per VN-cluster — if VN cities exist)

Each city's signature_dishes entry becomes a section: local description,
history, and the where_to_eat venue list (as text — the venue names are
strings, not entity refs, so no automatic linking).

Usage:
    python scripts/generate_country_dish.py
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

MIN_CITIES = 1  # any dish in any city in the country gets a rollup page


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


def _dish_display(slug: str) -> str:
    return slug.replace("-", " ").title()


def _city_section(d: dict, country_slug: str, city_slug: str, city_name: str) -> str:
    name = html.escape(d.get("name", _dish_display(d.get("slug", ""))))
    desc = html.escape(d.get("description", ""))
    hist = html.escape(d.get("history", ""))
    wte = d.get("where_to_eat") or []
    wte_html = ""
    if isinstance(wte, list) and wte:
        items = "".join(f"<li>{html.escape(str(v))}</li>" for v in wte[:8])
        wte_html = f'<p><strong>Where to eat in {html.escape(city_name)}:</strong></p><ul>{items}</ul>'
    body = []
    body.append(f'<h2 style="margin-top:32px;">{name} · <a href="/{country_slug}/{city_slug}/">{html.escape(city_name)}</a></h2>')
    if desc:
        body.append(f'<p>{desc}</p>')
    if hist:
        body.append(f'<p><em>{hist}</em></p>')
    if wte_html:
        body.append(wte_html)
    return "".join(body)


def _collect(country_dir: Path) -> dict[str, list[tuple[dict, str, str]]]:
    """Returns {dish_slug: [(dish_entry, city_slug, city_name)]}."""
    buckets: dict[str, list[tuple[dict, str, str]]] = defaultdict(list)
    for city_dir in sorted(country_dir.iterdir()):
        if not city_dir.is_dir() or city_dir.name == "data":
            continue
        city_slug = city_dir.name
        rj = city_dir / "data" / "region.json"
        sj = city_dir / "data" / "signature-dishes.json"
        if not rj.exists() or not sj.exists():
            continue
        try:
            region = json.loads(rj.read_text(encoding="utf-8"))
            payload = json.loads(sj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        meta = region.get("_metadata") or {}
        if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
            hub = CONTENT / country_dir.name / city_slug / "index.html"
            if not hub.exists():
                continue
        city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()
        entries = payload.get("signature_dishes") or []
        for d in entries:
            if not isinstance(d, dict):
                continue
            slug = d.get("slug")
            if not slug:
                continue
            buckets[slug].append((d, city_slug, city_name))
    return buckets


def _render(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
            dish_slug: str, cities: list[tuple[dict, str, str]],
            available_dishes: set[str]) -> Path:
    dish_display = _dish_display(dish_slug)
    n = len(cities)
    canonical = f"{BASE}/{country_slug}/dish/{dish_slug}/"
    title = f"{dish_display} across {country_name}: where to eat | Cork & Curve"
    description = (
        f"Where to eat {dish_display} in {country_name}, with each city's "
        f"local variant and {n} city guides linked. Editor-picked by TableJourney."
    )
    if len(description) > 165:
        from utils.seo import _smart_truncate as _mt
        description = _mt(description, max_len=158)

    sections_html = "".join(_city_section(d, country_slug, cs, cn) for d, cs, cn in cities)

    cross_items = [s for s in sorted(available_dishes) if s != dish_slug][:12]
    cross_html = ""
    if cross_items:
        items_html = "".join(
            f'<li><a href="/{country_slug}/dish/{s}/">{_dish_display(s)} across {country_name}</a></li>'
            for s in cross_items
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">More dishes across {country_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )
    body_html = (
        f'<p class="tj-topic-headline">{dish_display} appears as a signature dish in {n} '
        f'{country_name} cities. See each city\'s local variant and where to eat it.'
        f'</p>'
        + sections_html + cross_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": "Signature Dishes", "url": f"{BASE}/{country_slug}/signature-dishes/"},
        {"position": 4, "name": dish_display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"{dish_display} across {country_name}",
        "subtitle": f"{n} {country_name} city variants.",
        "canonical_url": canonical, "body_html": body_html,
        "breadcrumb_items": breadcrumb, "page_type": "article",
        "updated": "May 2026", "modified": "2026-05-20",
    }
    seo = {
        "meta": {"title": title, "description": description, "canonical_url": canonical,
                 "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"},
        "open_graph": {"og_title": title, "og_description": description, "og_url": canonical,
                       "og_type": "website", "og_image": "https://corkandcurve.com/og/default.jpg",
                       "og_image_alt": "Cork & Curve wine guide", "og_locale": "en_US"},
        "twitter": {"twitter_title": title, "twitter_description": description},
        "structured_data": {"breadcrumb_items": breadcrumb}, "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    out = CONTENT / country_slug / "dish" / dish_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "country-dish", "destination": f"{country_slug}-{dish_slug}"},
        base_path="", topic_nav=FOOD_TOPIC_NAV, breadcrumb=breadcrumb, current_year=2026,
    ), encoding="utf-8")
    return out


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    by_country: dict[str, set[str]] = defaultdict(set)

    candidates: dict[tuple[str, str], list[tuple[dict, str, str]]] = {}
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        buckets = _collect(country_dir)
        for dish_slug, cities in buckets.items():
            if len(cities) >= MIN_CITIES:
                candidates[(country_dir.name, dish_slug)] = cities
                by_country[country_dir.name].add(dish_slug)

    for (country_slug, dish_slug), cities in candidates.items():
        p = _render(renderer, country_slug=country_slug,
                    country_name=_country_display(country_slug),
                    dish_slug=dish_slug, cities=cities,
                    available_dishes=by_country[country_slug])
        written.add(p)

    pruned = 0
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        dish_dir = country_dir / "dish"
        if not dish_dir.is_dir():
            continue
        for sub in dish_dir.iterdir():
            if not sub.is_dir():
                continue
            idx = sub / "index.html"
            if idx.exists() and idx not in written:
                shutil.rmtree(sub)
                pruned += 1

    print(f"wrote {len(written)} country×dish pages across {len(by_country)} countries")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
