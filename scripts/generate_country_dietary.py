#!/usr/bin/env python3
"""Generate per-country dietary rollup pages.

For every (country, diet) with enough content, emit a country-level
top list:

  /<country>/dietary/vegan/
  /<country>/dietary/vegetarian/
  /<country>/dietary/gluten-free/
  /<country>/dietary/halal/
  /<country>/dietary/kosher/

Sibling of generate_city_dietary.py at country scope.

Usage:
    python scripts/generate_country_dietary.py
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
from utils.filter_search import filter_search_widget  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

MIN_ENTITIES = 1
TOP_N = 30

DIET_META: dict[str, dict] = {
    "vegan":       {"slug": "vegan",        "display": "Vegan",        "blurb": "fully plant-based rooms"},
    "vegetarian":  {"slug": "vegetarian",   "display": "Vegetarian",   "blurb": "kitchens with strong meatless menus"},
    "gluten_free": {"slug": "gluten-free",  "display": "Gluten-free",  "blurb": "rooms where coeliacs can eat without the interrogation"},
    "halal":       {"slug": "halal",        "display": "Halal",        "blurb": "halal-certified kitchens and halal-friendly rooms"},
    "kosher":      {"slug": "kosher",       "display": "Kosher",       "blurb": "kosher-certified rooms and kosher-style kitchens"},
}


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


def _extract_price_int(e: dict) -> int | None:
    """Best-effort numeric price for sort widget. Mirrors
    TemplateRenderer._price_to_int in scripts/utils/template_renderer.py
    so HTML pages emitted from generators sort consistently with template-
    rendered pages."""
    import re as _re
    for field in ("price_range", "price", "tasting_menu_price"):
        raw = e.get(field)
        if isinstance(raw, str) and raw.strip():
            m = _re.search(r"\d+", raw.replace(",", ""))
            if m:
                return int(m.group(0))
    tier = e.get("price_tier")
    if isinstance(tier, str) and tier.strip():
        sigils = sum(1 for c in tier if c in "$€£¥₩₹฿")
        if sigils:
            return sigils * 30
    return None



def _entity_card(e: dict, country_slug: str, city_slug: str, city_name: str) -> str:
    name = html.escape(e.get("name", ""))
    addr = html.escape(e.get("address", ""))
    desc = html.escape(e.get("description", ""))
    nbhd = html.escape(e.get("neighborhood", "")) if e.get("neighborhood") else ""
    score = e.get("editorial_score")
    score_html = ""
    if isinstance(score, (int, float)) and 1.0 <= score <= 5.0:
        score_html = f' <span class="tj-entity-score">★ {score:.1f}</span>'
    slug = e.get("slug") or ""
    href = f"/{country_slug}/{city_slug}/dietary/{slug}/" if slug else ""
    _dscore = f' data-score="{score:.2f}"' if isinstance(score, (int, float)) else ''
    _dname = f' data-name="{html.escape(e.get("name", ""))}"'
    _pn = _extract_price_int(e)
    _dprice = f' data-price="{_pn}"' if _pn is not None else ''
    title_html = f'<a class="tj-entity-card" href="{html.escape(href)}"{_dscore}{_dprice}{_dname}>' if href else f'<div class="tj-entity-card"{_dscore}{_dprice}{_dname}>'
    closer = "</a>" if href else "</div>"
    locale = " · ".join(b for b in [nbhd, addr] if b)
    city_tag = f' <span class="tj-entity-city" style="font-size:.85em; opacity:.75;">· {html.escape(city_name)}</span>'
    parts = [title_html, f'<h3 class="tj-entity-name">{name}{score_html}{city_tag}</h3>']
    if locale:
        parts.append(f'<p class="tj-entity-locale">{locale}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    if e.get("tip"):
        parts.append(f'<p class="tj-entity-desc"><strong>Tip:</strong> {html.escape(e["tip"])}</p>')
    parts.append(closer)
    return "".join(parts)


def _collect(country_dir: Path, diet_key: str) -> list[tuple[dict, str, str]]:
    out: list[tuple[dict, str, str]] = []
    for city_dir in sorted(country_dir.iterdir()):
        if not city_dir.is_dir() or city_dir.name == "data":
            continue
        city_slug = city_dir.name
        rj = city_dir / "data" / "region.json"
        dj = city_dir / "data" / "dietary.json"
        if not rj.exists() or not dj.exists():
            continue
        try:
            region = json.loads(rj.read_text(encoding="utf-8"))
            payload = json.loads(dj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        meta = region.get("_metadata") or {}
        if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
            hub = CONTENT / country_dir.name / city_slug / "index.html"
            if not hub.exists():
                continue
        city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()
        entries = (payload.get("dietary") or {}).get(diet_key)
        if not isinstance(entries, list):
            continue
        for e in entries:
            if not isinstance(e, dict):
                continue
            score = e.get("editorial_score")
            if not isinstance(score, (int, float)) or score < 3.5:
                continue
            out.append((e, city_slug, city_name))
    out.sort(key=lambda t: t[0].get("editorial_score", 0), reverse=True)
    return out[:TOP_N]


def _render(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
            diet_key: str, entities: list[tuple[dict, str, str]],
            available_diets: set[str]) -> Path:
    meta = DIET_META[diet_key]
    diet_slug = meta["slug"]
    diet_display = meta["display"]
    n = len(entities)
    canonical = f"{BASE}/{country_slug}/dietary/{diet_slug}/"
    title = f"Top {diet_display} restaurants in {country_name}: {n} rooms | Cork & Curve"
    description = (
        f"The best {n} {diet_display.lower()} spots across {country_name}, "
        f"editor-picked with neighborhoods, what to order and where to book. "
        f"{meta['blurb'].capitalize()}."
    )
    if len(description) > 165:
        description = description[:162].rsplit(" ", 1)[0] + "..."

    cards_html = "".join(_entity_card(e, country_slug, cs, cn) for e, cs, cn in entities)

    cross_items = [
        (DIET_META[k]["slug"], DIET_META[k]["display"])
        for k in DIET_META if k != diet_key and DIET_META[k]["slug"] in available_diets
    ]
    cross_html = ""
    if cross_items:
        items_html = "".join(
            f'<li><a href="/{country_slug}/dietary/{s}/">{l} in {country_name}</a></li>'
            for s, l in cross_items
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">More dietary guides across {country_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )
    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {diet_display.lower()} spots across {country_name}, '
        f'editor-picked. <a href="/{country_slug}/">All {country_name} guides</a>.'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card", placeholder="Filter by name, neighborhood…", aria_label="Filter list") + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": "Dietary", "url": None},
        {"position": 4, "name": diet_display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"Top {diet_display} restaurants in {country_name}",
        "subtitle": f"{n} editor-picked rooms across {country_name}.",
        "canonical_url": canonical, "body_html": body_html,
        "breadcrumb_items": breadcrumb, "page_type": "collection",
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
    out = CONTENT / country_slug / "dietary" / diet_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "country-dietary", "destination": f"{country_slug}-{diet_slug}"},
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
        for diet_key, meta in DIET_META.items():
            ents = _collect(country_dir, diet_key)
            if len(ents) >= MIN_ENTITIES:
                candidates[(country_dir.name, diet_key)] = ents
                by_country[country_dir.name].add(meta["slug"])

    for (country_slug, diet_key), ents in candidates.items():
        p = _render(renderer, country_slug=country_slug,
                    country_name=_country_display(country_slug),
                    diet_key=diet_key, entities=ents,
                    available_diets=by_country[country_slug])
        written.add(p)

    pruned = 0
    known = {m["slug"] for m in DIET_META.values()}
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        # Only prune inside real country dirs (not chrome/cross-cut dirs).
        if not (SITE_DATA / country_dir.name / "data" / "region.json").exists():
            continue
        dietary_dir = country_dir / "dietary"
        if not dietary_dir.is_dir():
            continue
        for sub in dietary_dir.iterdir():
            if not sub.is_dir() or sub.name not in known:
                continue
            idx = sub / "index.html"
            if idx.exists() and idx not in written:
                shutil.rmtree(sub)
                pruned += 1

    print(f"wrote {len(written)} country×dietary pages across {len(by_country)} countries")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
