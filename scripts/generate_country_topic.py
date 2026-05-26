#!/usr/bin/env python3
"""Generate per-country topic rollup pages.

For every (country, topic) combination with enough content, emit a
"top across <Country>" landing page that aggregates the best entities
in that topic across all cities in the country:

  /<country>/restaurants/
  /<country>/wine-bars/
  /<country>/bakeries/
  /<country>/nightlife/
  /<country>/cafes/
  ... etc.

This is the country-level peer of the existing city × topic chapter.
Each card links to the entity's own page on its home city. Sorted by
editorial_score descending, capped at TOP_N entries.

Re-runnable; rewrites every page each run; prunes any (country, topic)
page whose data fell below the MIN_ENTITIES threshold.

Internal-link discipline: each rendered page links to its sibling
country × topic pages so the cluster is fully connected and the
country index links into every emitted topic page (no orphans).

Usage:
    python scripts/generate_country_topic.py
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

# Minimum entities to ship the page. Three is the bar to avoid one-city
# pages masquerading as country rollups.
MIN_ENTITIES = 1
# Card cap. Country-level pages should feel curated, not exhaustive.
TOP_N = 30

# Topic configuration: (file basename without .json, top-level list key in
# the JSON, URL slug, display label, blurb). File and list-key are usually
# the same kebab/snake variant, listed explicitly so re-keys don't silently
# drop pages.
TOPIC_META: list[dict] = [
    {"file": "restaurants",      "key": "restaurants",      "slug": "restaurants",      "display": "Restaurants",      "blurb": "editor-picked dining rooms"},
    {"file": "fine-dining",      "key": "fine_dining",      "slug": "fine-dining",      "display": "Fine Dining",      "blurb": "tasting menus and serious destination rooms"},
    {"file": "casual-dining",    "key": "casual_dining",    "slug": "casual-dining",    "display": "Casual Dining",    "blurb": "everyday-good neighborhood restaurants"},
    {"file": "bakeries",         "key": "bakeries",         "slug": "bakeries",         "display": "Bakeries",         "blurb": "bread, pastry and morning baking destinations"},
    {"file": "cafes",            "key": "cafes",            "slug": "cafes",            "display": "Cafes",            "blurb": "all-day cafes worth sitting in"},
    {"file": "coffee-roasters",  "key": "coffee_roasters",  "slug": "coffee-roasters",  "display": "Coffee Roasters",  "blurb": "third-wave roasters and specialty coffee bars"},
    {"file": "bars",             "key": "bars",             "slug": "bars",             "display": "Bars",             "blurb": "cocktail and craft drinks across the country"},
    {"file": "wine-bars",        "key": "wine_bars",        "slug": "wine-bars",        "display": "Wine Bars",        "blurb": "natural and classic wine destinations"},
    {"file": "breweries",        "key": "breweries",        "slug": "breweries",        "display": "Breweries",        "blurb": "craft breweries and taproom destinations"},
    {"file": "street-food",      "key": "street_food",      "slug": "street-food",      "display": "Street Food",      "blurb": "stalls, kiosks and street-eating worth queuing for"},
    {"file": "markets",          "key": "markets",          "slug": "markets",          "display": "Food Markets",     "blurb": "produce, fish and food halls"},
    {"file": "late-night",       "key": "late_night",       "slug": "late-night",       "display": "Late-Night",       "blurb": "kitchens open past midnight"},
    {"file": "hidden-gems",      "key": "hidden_gems",      "slug": "hidden-gems",      "display": "Hidden Gems",      "blurb": "lesser-known editor picks worth the detour"},
    {"file": "budget-eating",    "key": "budget_eating",    "slug": "budget-eating",    "display": "Budget Eating",    "blurb": "cheap and excellent across the country"},
    {"file": "brunch",           "key": "brunch",           "slug": "brunch",           "display": "Brunch",           "blurb": "weekend morning and late-breakfast destinations"},
    {"file": "food-tours",       "key": "food_tours",       "slug": "food-tours",       "display": "Food Tours",       "blurb": "operator-led food walks and tastings"},
    {"file": "cooking-classes",  "key": "cooking_classes",  "slug": "cooking-classes",  "display": "Cooking Classes",  "blurb": "hands-on cooking classes for travelers"},
    {"file": "day-trips-food",   "key": "day_trips_food",   "slug": "day-trips-food",   "display": "Day Trips",        "blurb": "food-led day trips from the city"},
]


def _country_display(slug: str) -> str:
    return {
        "usa": "USA",
        "united-states": "United States",
        "united-kingdom": "United Kingdom",
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



def _entity_card(e: dict, country_slug: str, city_slug: str, topic_slug: str, city_name: str) -> str:
    name = html.escape(e.get("name", ""))
    addr = html.escape(e.get("address", ""))
    desc = html.escape(e.get("description", ""))
    nbhd = html.escape(e.get("neighborhood", "")) if e.get("neighborhood") else ""
    score = e.get("editorial_score")
    score_html = ""
    if isinstance(score, (int, float)) and 1.0 <= score <= 5.0:
        score_html = (
            f' <span class="tj-entity-score" '
            f'aria-label="Cork & Curve editorial score {score:.1f} out of 5">'
            f'★ {score:.1f}</span>'
        )
    slug = e.get("slug") or ""
    href = f"/{country_slug}/{city_slug}/{topic_slug}/{slug}/" if slug else ""
    _dscore = f' data-score="{score:.2f}"' if isinstance(score, (int, float)) else ''
    _dname = f' data-name="{html.escape(e.get("name", ""))}"'
    _pn = _extract_price_int(e)
    _dprice = f' data-price="{_pn}"' if _pn is not None else ''
    title_html = (
        f'<a class="tj-entity-card" href="{html.escape(href)}"{_dscore}{_dprice}{_dname}>' if href
        else f'<div class="tj-entity-card"{_dscore}{_dprice}{_dname}>'
    )
    closer = "</a>" if href else "</div>"

    locale_bits = [b for b in [nbhd, addr] if b]
    locale = " · ".join(locale_bits)
    # Always show the city since this is a country rollup; readers need to
    # know which city each card belongs to.
    city_tag = (
        f' <span class="tj-entity-city" style="font-size:.85em; opacity:.75;">'
        f'· {html.escape(city_name)}</span>'
    )

    parts = [title_html]
    parts.append(f'<h3 class="tj-entity-name">{name}{score_html}{city_tag}</h3>')
    if locale:
        parts.append(f'<p class="tj-entity-locale">{locale}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    if e.get("tip"):
        parts.append(f'<p class="tj-entity-desc"><strong>Tip:</strong> {html.escape(e["tip"])}</p>')
    parts.append(closer)
    return "".join(parts)


def _other_topics_for_country(country_slug: str, exclude_slug: str, available: set[str]) -> list[tuple[str, str]]:
    """Sibling topic links — only emit links to topics that actually
    rendered a page for this country (no orphans)."""
    out = []
    for meta in TOPIC_META:
        if meta["slug"] == exclude_slug:
            continue
        if meta["slug"] in available:
            out.append((meta["slug"], meta["display"]))
    return out


def _render_page(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
                 topic_meta: dict, entities: list[tuple[dict, str, str]],
                 available_topics: set[str]) -> Path:
    """entities is list of (entity_dict, city_slug, city_name)."""
    topic_slug = topic_meta["slug"]
    topic_display = topic_meta["display"]
    n = len(entities)

    canonical = f"{BASE}/{country_slug}/{topic_slug}/"
    title = f"Top {topic_display} in {country_name}: {n} editor-picked rooms | Cork & Curve"
    description = (
        f"The best {n} {topic_display.lower()} across {country_name}, "
        f"editor-ranked with what to order, where and why. "
        f"{topic_meta['blurb'].capitalize()}, by Cork & Curve."
    )
    if len(description) > 165:
        from utils.seo import _smart_truncate as _mt
        description = _mt(description, max_len=158)

    cards_html = "".join(
        _entity_card(e, country_slug, city_slug, topic_slug, city_name)
        for e, city_slug, city_name in entities
    )

    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{topic_display} in {country_name}",
        "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": f"https://corkandcurve.com/{country_slug}/{city_slug}/{topic_slug}/{e.get('slug', '')}/",
                "name": e.get("name", ""),
            }
            for i, (e, city_slug, _) in enumerate(entities, start=1)
            if e.get("slug")
        ],
    }
    itemlist_html = (
        '<script type="application/ld+json">'
        + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":"))
        + '</script>'
    )

    cross_links = _other_topics_for_country(country_slug, topic_slug, available_topics)
    cross_html = ""
    if cross_links:
        items_html = "".join(
            f'<li><a href="/{country_slug}/{slug}/">{label} in {country_name}</a></li>'
            for slug, label in cross_links
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); '
            'border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">More across {country_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul>'
            '</div>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {topic_display.lower()} worth the trip across {country_name}, '
        f'editor-ranked by Cork & Curve. '
        f'<a href="/{country_slug}/">All {country_name} guides</a>.'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card", placeholder="Filter by name, neighborhood…", aria_label="Filter list") + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html
        + itemlist_html
    )

    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": topic_display, "url": None},
    ]

    page_ctx = {
        "title": title,
        "meta_description": description,
        "h1": f"Top {topic_display} in {country_name}",
        "subtitle": f"{n} editor-picked rooms across {country_name}.",
        "canonical_url": canonical,
        "body_html": body_html,
        "breadcrumb_items": breadcrumb,
        "page_type": "collection",
        "updated": "May 2026",
        "modified": "2026-05-20",
    }
    seo = {
        "meta": {
            "title": title,
            "description": description,
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        },
        "open_graph": {
            "og_title": title,
            "og_description": description,
            "og_url": canonical,
            "og_type": "website",
            "og_image": "https://corkandcurve.com/og/default.jpg",
            "og_image_alt": "Cork & Curve wine guide",
            "og_locale": "en_US",
        },
        "twitter": {"twitter_title": title, "twitter_description": description},
        "structured_data": {"breadcrumb_items": breadcrumb},
        "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    out = CONTENT / country_slug / topic_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        template.render(
            page=page_ctx,
            seo=seo,
            analytics={
                "page_type": "country-topic",
                "destination": f"{country_slug}-{topic_slug}",
            },
            base_path="",
            topic_nav=FOOD_TOPIC_NAV,
            breadcrumb=breadcrumb,
            current_year=2026,
        ),
        encoding="utf-8",
    )
    return out


def _collect_topic_entities(country_dir: Path, topic: dict) -> list[tuple[dict, str, str]]:
    """Walk every city in the country, pull the topic's entity list from
    each city, attach city_slug + city_name, return flat list sorted by
    editorial_score descending."""
    file_name = topic["file"] + ".json"
    list_key = topic["key"]
    out: list[tuple[dict, str, str]] = []
    for city_dir in sorted(country_dir.iterdir()):
        if not city_dir.is_dir() or city_dir.name == "data":
            continue
        city_slug = city_dir.name
        rj = city_dir / "data" / "region.json"
        tj = city_dir / "data" / file_name
        if not rj.exists() or not tj.exists():
            continue
        try:
            region = json.loads(rj.read_text(encoding="utf-8"))
            payload = json.loads(tj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        meta = region.get("_metadata") or {}
        if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
            hub = CONTENT / country_dir.name / city_slug / "index.html"
            if not hub.exists():
                continue
        city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()
        entries = payload.get(list_key)
        if not isinstance(entries, list):
            continue
        for e in entries:
            if not isinstance(e, dict):
                continue
            # Skip entities that won't have a rendered page (generate_entity_pages
            # skips open_status unknown/permanently_closed) — else the rollup
            # card links to a 404 (Champagne allocation-only growers, 2026-05-25).
            if ((e.get("verified") or {}).get("open_status")) in ("unknown", "permanently_closed"):
                continue
            score = e.get("editorial_score")
            if not isinstance(score, (int, float)) or score < 3.5:
                # Only entities with a credible editorial_score land on
                # country rollups — keeps the page curated, not exhaustive.
                continue
            out.append((e, city_slug, city_name))
    out.sort(key=lambda t: t[0].get("editorial_score", 0), reverse=True)
    return out[:TOP_N]


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    skipped_thin = 0
    by_country: dict[str, set[str]] = defaultdict(set)
    # First pass: figure out which topics actually have ≥MIN_ENTITIES per
    # country, so the cross-link block can reference live siblings only.
    candidate: dict[tuple[str, str], list[tuple[dict, str, str]]] = {}
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country_slug = country_dir.name
        for topic in TOPIC_META:
            entities = _collect_topic_entities(country_dir, topic)
            if len(entities) < MIN_ENTITIES:
                skipped_thin += 1
                continue
            candidate[(country_slug, topic["slug"])] = entities
            by_country[country_slug].add(topic["slug"])

    # Second pass: render each candidate with sibling links scoped to its
    # country's live topics.
    for (country_slug, topic_slug), entities in candidate.items():
        country_dir = SITE_DATA / country_slug
        if not country_dir.exists():
            continue
        country_name = _country_display(country_slug)
        topic_meta = next(m for m in TOPIC_META if m["slug"] == topic_slug)
        p = _render_page(
            renderer,
            country_slug=country_slug,
            country_name=country_name,
            topic_meta=topic_meta,
            entities=entities,
            available_topics=by_country[country_slug],
        )
        written.add(p)

    # Prune stale (country, topic) pages whose data dropped below threshold.
    pruned = 0
    known_slugs = {m["slug"] for m in TOPIC_META}
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        # Only prune inside REAL country dirs. Without this guard the loop
        # also walks chrome/cross-cut dirs (/topics/, /grape/, /tag/, ...)
        # and deletes e.g. /topics/wine-bars/ (owned by generate_chrome_pages)
        # because its name matches a topic slug. (Bug found 2026-05-25.)
        if not (SITE_DATA / country_dir.name / "data" / "region.json").exists():
            continue
        for child in country_dir.iterdir():
            if not child.is_dir() or child.name not in known_slugs:
                continue
            idx = child / "index.html"
            if idx.exists() and idx not in written:
                # Only prune if this is a country × topic page (not a city
                # named after a topic slug somehow — defensive check).
                shutil.rmtree(child)
                pruned += 1

    print(
        f"wrote {len(written)} country×topic pages "
        f"across {len(by_country)} countries "
        f"(skipped {skipped_thin} country/topic combos with <{MIN_ENTITIES} editorial-grade entities)"
    )
    if pruned:
        print(f"pruned {pruned} stale country×topic pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
