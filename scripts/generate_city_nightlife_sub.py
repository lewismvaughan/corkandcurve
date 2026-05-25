#!/usr/bin/env python3
"""Generate per-city nightlife-subcategory sub-pages.

For every city, walk nightlife.json and emit one index page per
subcategory that has >= MIN_ENTITIES entries:

  /<country>/<city>/nightlife/dance-clubs/
  /<country>/<city>/nightlife/live-music/
  /<country>/<city>/nightlife/rooftop-bars/
  /<country>/<city>/nightlife/speakeasies/
  /<country>/<city>/nightlife/lgbtq/
  /<country>/<city>/nightlife/listening-bars/
  /<country>/<city>/nightlife/late-night-dives/

Mirrors generate_city_dietary.py for shape, pipeline wiring, and
no-orphan discipline. The parent nightlife topic template already
links to these sub-pages when threshold is met
(templates/topics/nightlife-topic.html).

Re-runnable; rewrites every page each run; prunes any (city, subcat)
page whose data dropped below threshold.

Usage:
    python scripts/generate_city_nightlife_sub.py
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402
from utils.filter_search import filter_search_widget  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

MIN_ENTITIES = 1

SUBCAT_META: dict[str, dict] = {
    "dance_clubs": {
        "slug": "dance-clubs",
        "display": "Dance Clubs",
        "blurb": "techno, house, electronic and disco rooms with serious dancefloors",
        "h1_suffix": "Dance Clubs in {city}",
    },
    "live_music": {
        "slug": "live-music",
        "display": "Live Music",
        "blurb": "jazz cellars, indie venues, rock pubs and intimate gig rooms",
        "h1_suffix": "Live Music in {city}",
    },
    "rooftop_bars": {
        "slug": "rooftop-bars",
        "display": "Rooftop Bars",
        "blurb": "skyline-view cocktail terraces and top-floor drinking rooms",
        "h1_suffix": "Rooftop Bars in {city}",
    },
    "speakeasies": {
        "slug": "speakeasies",
        "display": "Speakeasies",
        "blurb": "hidden-door cocktail bars with bartender pedigree",
        "h1_suffix": "Speakeasies in {city}",
    },
    "lgbtq": {
        "slug": "lgbtq",
        "display": "LGBTQ+",
        "blurb": "queer-coded bars, clubs, and party nights",
        "h1_suffix": "LGBTQ+ Nightlife in {city}",
    },
    "listening_bars": {
        "slug": "listening-bars",
        "display": "Listening Bars",
        "blurb": "audiophile vinyl bars with curated sound systems",
        "h1_suffix": "Listening Bars in {city}",
    },
    "late_night_dives": {
        "slug": "late-night-dives",
        "display": "Late-Night Dives",
        "blurb": "cheap, character-heavy bars open past 02:00",
        "h1_suffix": "Late-Night Dives in {city}",
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
    href = f"/{country_slug}/{city_slug}/nightlife/{slug}/" if slug else ""
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


_SUBCAT_LOOKUP_CACHE: dict[tuple[str, str], dict] = {}


def _other_subcats_for_city(country_slug: str, city_slug: str, exclude_key: str) -> list[tuple[str, str]]:
    """Return list of (subcat_slug, display_label) for OTHER nightlife
    subcats in this city that have a rendered page. Cross-links each
    sub-page to its siblings so the cluster is fully connected.
    """
    cache_key = (country_slug, city_slug)
    if cache_key not in _SUBCAT_LOOKUP_CACHE:
        path = SITE_DATA / country_slug / city_slug / "data" / "nightlife.json"
        if not path.exists():
            _SUBCAT_LOOKUP_CACHE[cache_key] = {}
            return []
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _SUBCAT_LOOKUP_CACHE[cache_key] = {}
            return []
        _SUBCAT_LOOKUP_CACHE[cache_key] = d.get("nightlife") or {}

    subs = _SUBCAT_LOOKUP_CACHE[cache_key]
    out = []
    for k, entries in subs.items():
        if k == exclude_key:
            continue
        if k not in SUBCAT_META:
            continue
        if isinstance(entries, list) and len(entries) >= MIN_ENTITIES:
            out.append((SUBCAT_META[k]["slug"], SUBCAT_META[k]["display"]))
    return out


def _render_page(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
                 city_slug: str, city_name: str, subcat_key: str, entities: list[dict]) -> Path:
    meta = SUBCAT_META[subcat_key]
    subcat_slug = meta["slug"]
    subcat_display = meta["display"]
    n = len(entities)

    canonical = f"{BASE}/{country_slug}/{city_slug}/nightlife/{subcat_slug}/"
    title = f"{subcat_display} in {city_name}: {n} rooms worth the night | Cork & Curve"
    description = (
        f"{n} {subcat_display.lower()} in {city_name}, editor-picked rooms with "
        f"door policy, hours and what to order. "
        f"{meta['blurb'].capitalize()}, by Cork & Curve editors."
    )
    if len(description) > 165:
        description = description[:162].rsplit(" ", 1)[0] + "..."

    cards_html = "".join(_entity_card(e, country_slug, city_slug) for e in entities)

    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{subcat_display} in {city_name}",
        "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": f"https://corkandcurve.com/{country_slug}/{city_slug}/nightlife/{e.get('slug', '')}/",
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

    cross_links = _other_subcats_for_city(country_slug, city_slug, subcat_key)
    cross_html = ""
    if cross_links:
        items_html = "".join(
            f'<li><a href="/{country_slug}/{city_slug}/nightlife/{slug}/">{label} in {city_name}</a></li>'
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

    map_section = ''
    if n >= 5:
        map_section = (
            f'<section aria-label="Map of {subcat_display} in {city_name}">'
            f'<div class="tj-citymap-wrap">'
            f'<div class="tj-citymap" data-pins-url="/{country_slug}/{city_slug}/_pins.json" '
            f'data-filter-nightlife="{subcat_key}"></div>'
            f'</div>'
            f'</section>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {subcat_display.lower()} in {city_name}, '
        f'editor-picked by Cork & Curve. '
        f'<a href="/{country_slug}/{city_slug}/nightlife/">All {city_name} nightlife</a>.'
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
        {"position": 4, "name": "Nightlife", "url": f"{BASE}/{country_slug}/{city_slug}/nightlife/"},
        {"position": 5, "name": subcat_display, "url": None},
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
    out = CONTENT / country_slug / city_slug / "nightlife" / subcat_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        template.render(
            page=page_ctx,
            seo=seo,
            analytics={
                "page_type": "city-nightlife-sub",
                "destination": f"{city_slug}-{subcat_slug}",
            },
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
            nj = city_dir / "data" / "nightlife.json"
            if not rj.exists() or not nj.exists():
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
                nightlife = json.loads(nj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()

            entries_by_sub = nightlife.get("nightlife") or {}
            had_any = False
            for subcat_key, entries in entries_by_sub.items():
                if subcat_key not in SUBCAT_META:
                    continue
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
                    subcat_key=subcat_key,
                    entities=entries,
                )
                written.add(p)
            if had_any:
                n_cities_with_data += 1

    # Prune stale (city, subcat) pages whose data dropped below threshold.
    pruned = 0
    known_slugs = {m["slug"] for m in SUBCAT_META.values()}
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            nightlife_dir = city_dir / "nightlife"
            if not nightlife_dir.is_dir():
                continue
            for sub_dir in nightlife_dir.iterdir():
                if not sub_dir.is_dir():
                    continue
                if sub_dir.name not in known_slugs:
                    continue
                idx = sub_dir / "index.html"
                if idx.exists() and idx not in written:
                    shutil.rmtree(sub_dir)
                    pruned += 1

    print(
        f"wrote {len(written)} city×nightlife-sub pages "
        f"across {n_cities_with_data} cities "
        f"(skipped {skipped_thin} city/subcat combos with <{MIN_ENTITIES} entities)"
    )
    if pruned:
        print(f"pruned {pruned} stale city×nightlife-sub pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
