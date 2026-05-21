#!/usr/bin/env python3
"""Generate per-city per-dish pages.

For every city with `signature_dishes` data, emit one page per dish:

  /<country>/<city>/dish/<dish-slug>/

These pages answer high-commercial-intent queries like "where to eat
croissant in paris" or "best pizza in nyc" with editor-picked venues
in that specific city for that specific dish.

The `where_to_eat` array on each dish names venues (by display name);
we resolve those names against every entity-bearing topic in the same
city, so a falafel reference to "L'As du Fallafel" (in street_food.json)
lands on the dish card alongside a bistro reference.

Threshold: emit only when at least 1 venue resolves. (Single-venue dish
pages still rank well because the canonical-version query is narrow.)

Mirrors scripts/generate_city_cuisine.py + generate_city_dietary.py in
shape and pipeline wiring.

Usage:
    python scripts/generate_city_dish.py
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://tablejourney.com"

# Min venue mentions to ship a page. 1 is fine for canonical-version queries.
MIN_VENUES = 1

# Which topic JSONs to scan when resolving where_to_eat venue names. Mirrors
# the venue_index in generate_cross_cuts.collect_all().
VENUE_TOPIC_KEYS = (
    ("restaurants", "restaurants"),
    ("casual_dining", "casual-dining"),
    ("fine_dining", "fine-dining"),
    ("cafes", "cafes"),
    ("bakeries", "bakeries"),
    ("coffee_roasters", "coffee-roasters"),
    ("wine_bars", "wine-bars"),
    ("bars", "bars"),
    ("street_food", "street-food"),
    ("breweries", "breweries"),
    ("markets", "markets"),
    ("budget_eating", "budget-eating"),
    ("hidden_gems", "hidden-gems"),
    ("brunch", "brunch"),
    ("late_night", "late-night"),
)


def _country_display(slug: str) -> str:
    return {
        "usa": "USA",
        "united-states": "United States",
        "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


def _build_venue_index(city_data_dir: Path) -> dict[str, tuple[dict, str]]:
    """Map venue display name -> (entity_dict, topic_slug) across every
    entity-bearing JSON in this city. Used to resolve dish.where_to_eat
    references."""
    idx: dict[str, tuple[dict, str]] = {}
    file_map = {key: f"{slug}.json" for key, slug in VENUE_TOPIC_KEYS}
    for json_key, filename in file_map.items():
        p = city_data_dir / filename
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in (d.get(json_key) or []):
            if isinstance(e, dict) and e.get("name") and e.get("slug"):
                # First occurrence wins; topic order above puts more-likely
                # canonical references first.
                idx.setdefault(e["name"], (e, dict(VENUE_TOPIC_KEYS)[json_key]))
    return idx


def _extract_price_int(e: dict) -> int | None:
    """Best-effort numeric price for sort. Mirrors TemplateRenderer._price_to_int
    so HTML pages emitted from generators sort consistently with template-rendered
    pages."""
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
    cuisine = html.escape(e.get("cuisine", "")) if e.get("cuisine") else ""
    score = e.get("editorial_score")
    score_html = ""
    if isinstance(score, (int, float)) and 1.0 <= score <= 5.0:
        score_html = (
            f' <span class="tj-entity-score" '
            f'aria-label="TableJourney editorial score {score:.1f} out of 5">'
            f'★ {score:.1f}</span>'
        )
    slug = e.get("slug") or ""
    href = f"/{country_slug}/{city_slug}/{topic_slug}/{slug}/" if slug else ""

    meta_bits = " · ".join(b for b in [cuisine] if b)
    locale_bits = " · ".join(b for b in [nbhd, addr] if b)

    _dscore = f' data-score="{score:.2f}"' if isinstance(score, (int, float)) else ''
    _dname = f' data-name="{html.escape(e.get("name", ""))}"'
    _pn = _extract_price_int(e)
    _dprice = f' data-price="{_pn}"' if _pn is not None else ''
    parts = [
        f'<a class="tj-entity-card" href="{html.escape(href)}"{_dscore}{_dprice}{_dname}>' if href
        else f'<div class="tj-entity-card"{_dscore}{_dprice}{_dname}>'
    ]
    parts.append(f'<h3 class="tj-entity-name">{name}{score_html}</h3>')
    if meta_bits:
        parts.append(f'<p class="tj-entity-meta">{meta_bits}</p>')
    if locale_bits:
        parts.append(f'<p class="tj-entity-locale">{locale_bits}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    parts.append("</a>" if href else "</div>")
    return "".join(parts)


def _render_page(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
                 city_slug: str, city_name: str, dish: dict,
                 resolved: list[tuple[dict, str]]) -> Path:
    dish_slug = dish["slug"]
    dish_name = dish.get("name", dish_slug)
    n = len(resolved)

    canonical = f"{BASE}/{country_slug}/{city_slug}/dish/{dish_slug}/"
    title = f"Where to eat {dish_name} in {city_name}: {n} editor pick{'s' if n != 1 else ''} | TableJourney"
    description = (
        f"Where to eat the canonical {dish_name} in {city_name}: {n} editor-picked "
        f"room{'s' if n != 1 else ''} that does the dish right, with what to order and how to find it."
    )
    if len(description) > 165:
        description = description[:162].rsplit(" ", 1)[0] + "..."

    cards_html = "".join(
        _entity_card(e, country_slug, city_slug, topic_slug)
        for e, topic_slug in resolved
    )

    # Lead with the dish description if present, then the venue grid.
    lead = ""
    if dish.get("description"):
        lead = f'<p class="tj-topic-headline">{html.escape(dish["description"])}</p>'
    if dish.get("history"):
        lead += f'<p>{html.escape(dish["history"])}</p>'

    # ItemList JSON-LD
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Where to eat {dish_name} in {city_name}",
        "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": f"https://tablejourney.com/{country_slug}/{city_slug}/{topic_slug}/{e.get('slug', '')}/",
                "name": e.get("name", ""),
            }
            for i, (e, topic_slug) in enumerate(resolved, start=1)
        ],
    }
    itemlist_html = (
        '<script type="application/ld+json">'
        + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":"))
        + '</script>'
    )

    # City-pins map filtered to ONLY the venues named in this dish's
    # where_to_eat. Comma-separated allow-list of entity slugs lets the
    # shared JS reuse the city's pins.json without us emitting a
    # per-dish JSON file.
    venue_slugs = ",".join(e.get("slug", "") for e, _ in resolved if e.get("slug"))
    # Only ship the map when there are enough venues to fill it — see STANDARDS §2d.
    map_section = ''
    if n >= 5:
        map_section = (
            f'<section aria-label="Map of where to eat {dish_name} in {city_name}">'
            f'<div class="tj-citymap-wrap">'
            f'<div class="tj-citymap" data-pins-url="/{country_slug}/{city_slug}/_pins.json" '
            f'data-filter-slugs="{venue_slugs}"></div>'
            f'</div>'
            f'</section>'
        )

    # Add filter+sort widget when the venue list is long enough to warrant it.
    filter_widget = ""
    if n >= 6:
        from utils.filter_search import filter_search_widget
        filter_widget = filter_search_widget(
            target_id="tj-dish-venues",
            item_selector=".tj-entity-card",
            placeholder="Filter venues by name, neighborhood…",
            aria_label=f"Filter {dish_name} venues",
        )

    body_html = (
        lead
        + f'<p><strong>{n}</strong> editor pick{"s" if n != 1 else ""} for {dish_name} in {city_name}, '
        f'ranked by editorial score. '
        f'<a href="/{country_slug}/{city_slug}/signature-dishes/">All {city_name} signature dishes</a> · '
        f'<a href="/dish/{dish_slug}/">{dish_name} across every city</a>.</p>'
        + map_section
        + filter_widget
        + f'<div id="tj-dish-venues" class="tj-entity-grid">{cards_html}</div>'
        + itemlist_html
    )

    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": city_name, "url": f"{BASE}/{country_slug}/{city_slug}/"},
        {"position": 4, "name": "Signature dishes", "url": f"{BASE}/{country_slug}/{city_slug}/signature-dishes/"},
        {"position": 5, "name": dish_name, "url": None},
    ]

    page_ctx = {
        "title": title,
        "meta_description": description,
        "h1": f"Where to eat {dish_name} in {city_name}",
        "subtitle": f"{n} editor pick{'s' if n != 1 else ''} for the canonical version.",
        "canonical_url": canonical,
        "body_html": body_html,
        "breadcrumb_items": breadcrumb,
        "page_type": "collection",
        "updated": "May 2026",
        "modified": "2026-05-19",
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
            "og_image": f"https://tablejourney.com/og/{city_slug}.jpg",
            "og_image_alt": f"TableJourney {city_name} food guide",
            "og_locale": "en_US",
        },
        "twitter": {"twitter_title": title, "twitter_description": description},
        "structured_data": {"breadcrumb_items": breadcrumb},
        "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    out = CONTENT / country_slug / city_slug / "dish" / dish_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        template.render(
            page=page_ctx,
            seo=seo,
            analytics={"page_type": "city-dish", "destination": f"{city_slug}-{dish_slug}"},
            base_path="",
            topic_nav=FOOD_TOPIC_NAV,
            breadcrumb=breadcrumb,
            current_year=2026,
        ),
        encoding="utf-8",
    )
    return out


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    unresolved = 0
    n_cities = 0

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
            sd = city_dir / "data" / "signature-dishes.json"
            if not rj.exists() or not sd.exists():
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
                dishes_data = json.loads(sd.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = (region.get("destination") or {}).get("name") or city_slug.replace("-", " ").title()

            venue_index = _build_venue_index(city_dir / "data")

            dishes = dishes_data.get("signature_dishes") or []
            had_any = False
            for dish in dishes:
                if not isinstance(dish, dict) or not dish.get("slug"):
                    continue
                names = dish.get("where_to_eat") or []
                if not isinstance(names, list):
                    continue
                resolved = [venue_index[n] for n in names if n in venue_index]
                # Sort venues by editorial_score descending so the top-N
                # ranking on the dish detail page is meaningful, not just
                # the order the editor happened to type them.
                resolved.sort(
                    key=lambda t: (t[0].get("editorial_score") if isinstance(t[0].get("editorial_score"), (int, float)) else -1),
                    reverse=True,
                )
                if len(resolved) < MIN_VENUES:
                    unresolved += 1
                    continue
                had_any = True
                p = _render_page(
                    renderer,
                    country_slug=country_slug,
                    country_name=country_name,
                    city_slug=city_slug,
                    city_name=city_name,
                    dish=dish,
                    resolved=resolved,
                )
                written.add(p)
            if had_any:
                n_cities += 1

    # Prune stale (city, dish) pages — anything not written this run.
    pruned = 0
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            dish_dir = city_dir / "dish"
            if not dish_dir.is_dir():
                continue
            for slug_dir in list(dish_dir.iterdir()):
                if not slug_dir.is_dir():
                    continue
                idx = slug_dir / "index.html"
                if idx.exists() and idx not in written:
                    shutil.rmtree(slug_dir)
                    pruned += 1
            if dish_dir.is_dir() and not any(dish_dir.iterdir()):
                dish_dir.rmdir()

    print(
        f"wrote {len(written)} city×dish pages across {n_cities} cities "
        f"(skipped {unresolved} dishes with <{MIN_VENUES} resolved venues)"
    )
    if pruned:
        print(f"pruned {pruned} stale city×dish pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
