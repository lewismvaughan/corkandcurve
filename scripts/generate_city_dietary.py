#!/usr/bin/env python3
"""Generate per-city dietary sub-pages.

For every city, walk dietary.json and emit one index page per diet that
has >= MIN_ENTITIES entries:

  /<country>/<city>/dietary/vegan/
  /<country>/<city>/dietary/vegetarian/
  /<country>/<city>/dietary/gluten-free/
  /<country>/<city>/dietary/halal/
  /<country>/<city>/dietary/kosher/

This is the highest commercial-intent SEO surface we haven't built yet
("vegan paris", "gluten free london", "halal new york"). Each page is a
focused card grid for one diet in one city, with editor-picked rooms and
direct booking links where available.

Re-runnable; rewrites every page each run; prunes any (city, diet) page
whose data dropped below threshold.

Usage:
    python scripts/generate_city_dietary.py
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, WINE_TOPIC_NAV  # noqa: E402
from utils.filter_search import filter_search_widget  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

# Below MIN_ENTITIES we skip the page entirely (and prune any existing
# stale page) — a "1 biodynamic estate in <region>" listing is thin SEO and
# worse UX than just not having the page.
MIN_ENTITIES = 1

DIET_META: dict[str, dict] = {
    "biodynamic": {
        "slug": "biodynamic",
        "display": "Biodynamic",
        "blurb": "Demeter-certified and biodynamic-practicing estates",
        "h1_suffix": "Biodynamic wine in {city}",
    },
    "organic": {
        "slug": "organic",
        "display": "Organic",
        "blurb": "certified-organic growers",
        "h1_suffix": "Organic wine in {city}",
    },
    "natural": {
        "slug": "natural",
        "display": "Natural",
        "blurb": "low-intervention, natural-wine cellars",
        "h1_suffix": "Natural wine in {city}",
    },
    "vegan_winemaking": {
        "slug": "vegan-winemaking",
        "display": "Vegan winemaking",
        "blurb": "estates that fine without animal products",
        "h1_suffix": "Vegan wine in {city}",
    },
    "lowsulfite": {
        "slug": "lowsulfite",
        "display": "Low sulfite",
        "blurb": "cellars working with little or no added sulfur",
        "h1_suffix": "Low-sulfite wine in {city}",
    },
}


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



def _entity_card(e: dict, country_slug: str, city_slug: str) -> str:
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
    href = f"/{country_slug}/{city_slug}/dietary/{slug}/" if slug else ""
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
    locale = html.escape(", ".join(locale_bits)) if False else " · ".join(locale_bits)

    parts = [title_html]
    parts.append(f'<h3 class="tj-entity-name">{name}{score_html}</h3>')
    if locale:
        parts.append(f'<p class="tj-entity-locale">{locale}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    if e.get("tip"):
        parts.append(f'<p class="tj-entity-desc"><strong>Tip:</strong> {html.escape(e["tip"])}</p>')
    parts.append(closer)
    return "".join(parts)


_DIET_LOOKUP_CACHE: dict[tuple[str, str], dict] = {}


def _other_diets_for_city(country_slug: str, city_slug: str, exclude_diet_key: str) -> list[tuple[str, str]]:
    """Return list of (diet_slug, display_label) for OTHER diets in this
    city that have a rendered page. Used to cross-link diet pages so each
    page has internal links to its siblings (free internal linking that
    helps Google understand the cluster).
    """
    cache_key = (country_slug, city_slug)
    if cache_key not in _DIET_LOOKUP_CACHE:
        path = SITE_DATA / country_slug / city_slug / "data" / "dietary.json"
        if not path.exists():
            _DIET_LOOKUP_CACHE[cache_key] = {}
            return []
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _DIET_LOOKUP_CACHE[cache_key] = {}
            return []
        _DIET_LOOKUP_CACHE[cache_key] = d.get("dietary") or {}

    diets = _DIET_LOOKUP_CACHE[cache_key]
    out = []
    for k, entries in diets.items():
        if k == exclude_diet_key:
            continue
        if k not in DIET_META:
            continue
        # Count only renderable entries (matching page generation): a sibling
        # subcat with only unknown/permanently_closed entries gets no page, so
        # don't cross-link it (Champagne 2026-05-25).
        renderable = [e for e in entries if isinstance(e, dict)
                      and ((e.get("verified") or {}).get("open_status")) not in ("unknown", "permanently_closed")] if isinstance(entries, list) else []
        if len(renderable) >= MIN_ENTITIES:
            out.append((DIET_META[k]["slug"], DIET_META[k]["display"]))
    return out


def _render_page(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
                 city_slug: str, city_name: str, diet_key: str, entities: list[dict]) -> Path:
    meta = DIET_META[diet_key]
    diet_slug = meta["slug"]
    diet_display = meta["display"]
    n = len(entities)

    canonical = f"{BASE}/{country_slug}/{city_slug}/dietary/{diet_slug}/"
    title = f"{diet_display} in {city_name}: {n} rooms worth booking | Cork & Curve"
    description = (
        f"{n} {diet_display.lower()} spots in {city_name} worth the trip, with "
        f"editor-picked rooms, what to order and how to find them. "
        f"{meta['blurb'].capitalize()}, by Cork & Curve editors."
    )
    # Trim to OG-safe length (~160 chars)
    if len(description) > 165:
        from utils.seo import _smart_truncate as _mt
        description = _mt(description, max_len=158)

    cards_html = "".join(_entity_card(e, country_slug, city_slug) for e in entities)

    # ItemList JSON-LD so Google can render this as a list rich result.
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{diet_display} in {city_name}",
        "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": f"https://corkandcurve.com/{country_slug}/{city_slug}/dietary/{e.get('slug', '')}/",
                "name": e.get("name", ""),
            }
            for i, e in enumerate(entities, start=1)
            if e.get("slug")
        ],
    }
    itemlist_html = (
        '<script type="application/ld+json">'
        + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":"))
        + '</script>'
    )

    # Internal cross-link block: other diets available in this same city.
    cross_links = _other_diets_for_city(country_slug, city_slug, diet_key)
    cross_html = ""
    if cross_links:
        items_html = "".join(
            f'<li><a href="/{country_slug}/{city_slug}/dietary/{slug}/">{label} in {city_name}</a></li>'
            for slug, label in cross_links
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); '
            'border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">Also in {city_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul>'
            '</div>'
        )

    # Only ship the map when the result set is large enough — see STANDARDS §2d.
    map_section = ''
    if n >= 5:
        map_section = (
            f'<section aria-label="Map of {diet_display} rooms in {city_name}">'
            f'<div class="tj-citymap-wrap">'
            f'<div class="tj-citymap" data-pins-url="/{country_slug}/{city_slug}/_pins.json" '
            f'data-filter-diet="{diet_key}"></div>'
            f'</div>'
            f'</section>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {diet_display.lower()} spots in {city_name}, '
        f'editor-picked by Cork & Curve. '
        f'<a href="/{country_slug}/{city_slug}/dietary/">All dietary guides in {city_name}</a>.'
        f'</p>'
        + map_section
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card", placeholder="Filter by name, neighborhood…", aria_label="Filter list") + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html
        + itemlist_html
    )

    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": city_name, "url": f"{BASE}/{country_slug}/{city_slug}/"},
        {"position": 4, "name": "Dietary", "url": f"{BASE}/{country_slug}/{city_slug}/dietary/"},
        {"position": 5, "name": diet_display, "url": None},
    ]

    page_ctx = {
        "title": title,
        "meta_description": description,
        "h1": meta["h1_suffix"].format(city=city_name),
        "subtitle": f"{n} editor-picked rooms in {city_name}.",
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
            "og_image": "https://corkandcurve.com/og/default.jpg",
            "og_image_alt": "Cork & Curve wine guide",
            "og_locale": "en_US",
        },
        "twitter": {"twitter_title": title, "twitter_description": description},
        "structured_data": {"breadcrumb_items": breadcrumb},
        "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    out = CONTENT / country_slug / city_slug / "dietary" / diet_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        template.render(
            page=page_ctx,
            seo=seo,
            analytics={
                "page_type": "city-dietary",
                "destination": f"{city_slug}-{diet_slug}",
            },
            base_path="",
            topic_nav=WINE_TOPIC_NAV,
            breadcrumb=breadcrumb,
            current_year=2026,
        ),
        encoding="utf-8",
    )
    return out


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    skipped_thin = 0
    n_cities_with_data = 0

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
            dj = city_dir / "data" / "dietary.json"
            if not rj.exists() or not dj.exists():
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
                dietary = json.loads(dj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                # Match the chrome-page convention: only treat as stub if the
                # city hub hasn't shipped yet. Once /<country>/<city>/index.html
                # exists, the city is live whatever the metadata flag says.
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()

            entries_by_diet = dietary.get("dietary") or {}
            had_any = False
            for diet_key, entries in entries_by_diet.items():
                if diet_key not in DIET_META:
                    continue
                # Only list entities that get a rendered page (entity-page gen
                # skips open_status unknown/permanently_closed) — else the card
                # links 404 (Champagne allocation-only growers, 2026-05-25).
                if isinstance(entries, list):
                    entries = [e for e in entries if isinstance(e, dict)
                               and ((e.get("verified") or {}).get("open_status")) not in ("unknown", "permanently_closed")]
                if not isinstance(entries, list) or len(entries) < MIN_ENTITIES:
                    skipped_thin += 1
                    continue
                had_any = True
                p = _render_page(
                    renderer,
                    country_slug=country_slug,
                    country_name=country_name,
                    city_slug=city_slug,
                    city_name=city_name,
                    diet_key=diet_key,
                    entities=entries,
                )
                written.add(p)
            if had_any:
                n_cities_with_data += 1

    # Prune stale (city, diet) pages whose data fell below threshold.
    pruned = 0
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            dietary_dir = city_dir / "dietary"
            if not dietary_dir.is_dir():
                continue
            for diet_dir in dietary_dir.iterdir():
                if not diet_dir.is_dir():
                    continue
                idx = diet_dir / "index.html"
                # Only prune pages we know we own (the diet-slug list).
                known_slugs = {m["slug"] for m in DIET_META.values()}
                if diet_dir.name in known_slugs and idx.exists() and idx not in written:
                    shutil.rmtree(diet_dir)
                    pruned += 1

    print(
        f"wrote {len(written)} city×dietary pages "
        f"across {n_cities_with_data} cities "
        f"(skipped {skipped_thin} city/diet combos with <{MIN_ENTITIES} entities)"
    )
    if pruned:
        print(f"pruned {pruned} stale city×dietary pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
