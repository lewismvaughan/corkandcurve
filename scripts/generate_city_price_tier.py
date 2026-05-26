#!/usr/bin/env python3
"""Generate per-city price-tier rollup pages.

For every city, bucket every entity (across restaurants / fine-dining /
casual-dining / bars / wine-bars / bakeries / cafes / etc.) by its
price_tier field, then emit one index page per tier with >= MIN_ENTITIES:

  /<country>/<city>/cheap-eats/    (1-tier — €, $, £ etc.)
  /<country>/<city>/mid-range/     (2-tier)
  /<country>/<city>/upscale/       (3-tier)
  /<country>/<city>/splurge/       (4-tier)

Targets the "<city> <budget>" head term ("cheap eats paris", "fine dining
new york"). Each card links to the entity's home topic page; same
filter/Itemlist/breadcrumb pattern as other city sub-rollups.

Cross-links sibling tiers in the same city + same tier in other cities
(via a country-level lookup) to keep the cluster fully connected.

Usage:
    python scripts/generate_city_price_tier.py
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

MIN_ENTITIES = 5  # higher floor — these are head-term pages, thin = bad
TOP_N = 40

# Entity-bearing topic files to walk per city. Same shape as
# generate_country_topic.py's TOPIC_META, simplified.
SOURCES = [
    ("restaurants",      "restaurants",      "restaurants"),
    ("fine-dining",      "fine_dining",      "fine-dining"),
    ("casual-dining",    "casual_dining",    "casual-dining"),
    ("bakeries",         "bakeries",         "bakeries"),
    ("cafes",            "cafes",            "cafes"),
    ("coffee-roasters",  "coffee_roasters",  "coffee-roasters"),
    ("bars",             "bars",             "bars"),
    ("wine-bars",        "wine_bars",        "wine-bars"),
    ("breweries",        "breweries",        "breweries"),
    ("street-food",      "street_food",      "street-food"),
    ("late-night",       "late_night",       "late-night"),
    ("hidden-gems",      "hidden_gems",      "hidden-gems"),
    ("budget-eating",    "budget_eating",    "budget-eating"),
    ("brunch",           "brunch",           "brunch"),
]

TIER_META = {
    1: {"slug": "cheap-eats", "display": "Cheap Eats", "blurb": "the best low-budget rooms in {city} — the places editors actually return to."},
    2: {"slug": "mid-range",  "display": "Mid-Range",  "blurb": "the comfortable everyday-good rooms in {city} — no surprise on the bill, real cooking."},
    3: {"slug": "upscale",    "display": "Upscale",    "blurb": "occasion rooms in {city} — destination kitchens for celebrations and visits."},
    4: {"slug": "splurge",    "display": "Splurge",    "blurb": "tasting menus and the full big-night-out treatment in {city}."},
}


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


def _tier_from_price(p) -> int | None:
    """Normalize price_tier to integer 1-4. Accepts €, $, £, ¥ repeated 1-4
    times (with or without spaces). Returns None for unrecognized values."""
    if not isinstance(p, str):
        return None
    raw = p.strip().replace(" ", "")
    if not raw:
        return None
    chars = set(raw)
    # Must be a single repeated currency mark
    if len(chars) != 1:
        return None
    ch = next(iter(chars))
    if ch not in {"$", "€", "£", "¥", "₩", "₹", "฿", "₺", "₽"}:
        return None
    n = len(raw)
    if 1 <= n <= 4:
        return n
    return None


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



def _entity_card(e: dict, country_slug: str, city_slug: str, topic_slug: str) -> str:
    name = html.escape(e.get("name", ""))
    addr = html.escape(e.get("address", ""))
    desc = html.escape(e.get("description", ""))
    nbhd = html.escape(e.get("neighborhood", "")) if e.get("neighborhood") else ""
    score = e.get("editorial_score")
    score_html = ""
    if isinstance(score, (int, float)) and 1.0 <= score <= 5.0:
        score_html = f' <span class="tj-entity-score">★ {score:.1f}</span>'
    slug = e.get("slug") or ""
    href = f"/{country_slug}/{city_slug}/{topic_slug}/{slug}/" if slug else ""
    _dscore = f' data-score="{score:.2f}"' if isinstance(score, (int, float)) else ''
    _dname = f' data-name="{html.escape(e.get("name", ""))}"'
    _pn = _extract_price_int(e)
    _dprice = f' data-price="{_pn}"' if _pn is not None else ''
    title_html = f'<a class="tj-entity-card" href="{html.escape(href)}"{_dscore}{_dprice}{_dname}>' if href else f'<div class="tj-entity-card"{_dscore}{_dprice}{_dname}>'
    closer = "</a>" if href else "</div>"
    locale = " · ".join(b for b in [nbhd, addr] if b)
    parts = [title_html, f'<h3 class="tj-entity-name">{name}{score_html}</h3>']
    if locale:
        parts.append(f'<p class="tj-entity-locale">{locale}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    if e.get("tip"):
        parts.append(f'<p class="tj-entity-desc"><strong>Tip:</strong> {html.escape(e["tip"])}</p>')
    parts.append(closer)
    return "".join(parts)


def _collect_city(country_slug: str, city_slug: str) -> dict[int, list[tuple[dict, str]]]:
    """Returns {tier: [(entity, topic_slug)]}."""
    buckets: dict[int, list[tuple[dict, str]]] = defaultdict(list)
    for fname, key, topic in SOURCES:
        p = SITE_DATA / country_slug / city_slug / "data" / (fname + ".json")
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in (d.get(key) or []):
            if not isinstance(e, dict):
                continue
            tier = _tier_from_price(e.get("price_tier"))
            if tier is None:
                continue
            buckets[tier].append((e, topic))
    for k in buckets:
        buckets[k].sort(key=lambda t: t[0].get("editorial_score", 0) or 0, reverse=True)
        buckets[k] = buckets[k][:TOP_N]
    return buckets


def _render(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
            city_slug: str, city_name: str, tier: int, entries: list[tuple[dict, str]],
            available_tiers: list[int]) -> Path:
    meta = TIER_META[tier]
    tier_slug = meta["slug"]
    tier_display = meta["display"]
    blurb = meta["blurb"].format(city=city_name)
    n = len(entries)
    canonical = f"{BASE}/{country_slug}/{city_slug}/{tier_slug}/"
    title = f"{tier_display} in {city_name}: {n} editor picks | Cork & Curve"
    description = (
        f"{n} {tier_display.lower()} rooms in {city_name} editor-picked by TableJourney. "
        f"{blurb.capitalize()}"
    )
    if len(description) > 165:
        description = description[:162].rsplit(" ", 1)[0] + "..."

    cards_html = "".join(_entity_card(e, country_slug, city_slug, t) for e, t in entries)

    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": f"{tier_display} in {city_name}", "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "url": f"https://tablejourney.com/{country_slug}/{city_slug}/{t}/{e.get('slug','')}/",
             "name": e.get("name", "")}
            for i, (e, t) in enumerate(entries, start=1) if e.get("slug")
        ],
    }
    itemlist_html = '<script type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":")) + '</script>'

    # Sibling tier cross-links — other tiers available in this city
    others = [TIER_META[t] for t in available_tiers if t != tier]
    cross_html = ""
    if others:
        items_html = "".join(
            f'<li><a href="/{country_slug}/{city_slug}/{m["slug"]}/">{m["display"]} in {city_name}</a></li>'
            for m in others
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">Other price guides in {city_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {tier_display.lower()} rooms in {city_name}, editor-picked. '
        f'{blurb} <a href="/{country_slug}/{city_slug}/">All {city_name} food</a>.'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card",
                                placeholder="Filter by name, neighborhood…",
                                aria_label=f"Filter {tier_display.lower()} list")
        + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html + itemlist_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": city_name, "url": f"{BASE}/{country_slug}/{city_slug}/"},
        {"position": 4, "name": tier_display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"{tier_display} in {city_name}",
        "subtitle": f"{n} editor-picked rooms in {city_name}.",
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
    out = CONTENT / country_slug / city_slug / tier_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "city-price-tier", "destination": f"{city_slug}-{tier_slug}"},
        base_path="", topic_nav=FOOD_TOPIC_NAV, breadcrumb=breadcrumb, current_year=2026,
    ), encoding="utf-8")
    return out


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    skipped_thin = 0

    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country_slug = country_dir.name
        country_name = _country_display(country_slug)
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city_slug = city_dir.name
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()

            buckets = _collect_city(country_slug, city_slug)
            available_tiers = [t for t, ents in buckets.items() if len(ents) >= MIN_ENTITIES]
            for tier in available_tiers:
                p = _render(renderer,
                            country_slug=country_slug, country_name=country_name,
                            city_slug=city_slug, city_name=city_name,
                            tier=tier, entries=buckets[tier],
                            available_tiers=available_tiers)
                written.add(p)
            skipped_thin += len([t for t, ents in buckets.items() if len(ents) < MIN_ENTITIES and len(ents) > 0])

    # Prune stale (city, tier) pages
    pruned = 0
    known_slugs = {m["slug"] for m in TIER_META.values()}
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            for tier_dir in city_dir.iterdir():
                if not tier_dir.is_dir() or tier_dir.name not in known_slugs:
                    continue
                idx = tier_dir / "index.html"
                if idx.exists() and idx not in written:
                    shutil.rmtree(tier_dir)
                    pruned += 1

    print(f"wrote {len(written)} city×price-tier pages (skipped {skipped_thin} thin combos with <{MIN_ENTITIES} entries)")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
