#!/usr/bin/env python3
"""Generate per-city cuisine sub-pages.

For every city, bucket restaurants/casual_dining/fine_dining by canonical
cuisine class and emit one index page per (city, cuisine) combination
with >= MIN_ENTITIES entries:

  /<country>/<city>/cuisine/italian/
  /<country>/<city>/cuisine/japanese/
  /<country>/<city>/cuisine/mexican/
  ...

These are the highest commercial-intent SEO queries we don't yet carve
("italian paris", "japanese new york"). Each page is a focused card grid
for one cuisine in one city, with editor scores + neighborhoods.

Mirrors scripts/generate_city_dietary.py in shape and pipeline wiring.

Usage:
    python scripts/generate_city_cuisine.py
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
from utils.cuisine import canonicalise as _canon_cuisine  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

# Threshold gates thin pages. >=2 is the same bar we use for city × dietary;
# below this the page is too sparse to compete vs the city's restaurants/
# fine-dining topic chapter.
MIN_ENTITIES = 1


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



def _entity_card(e: dict, country_slug: str, city_slug: str, topic_slug: str) -> str:
    name = html.escape(e.get("name", ""))
    addr = html.escape(e.get("address", ""))
    desc = html.escape(e.get("description", ""))
    nbhd = html.escape(e.get("neighborhood", "")) if e.get("neighborhood") else ""
    cuisine = html.escape(e.get("cuisine", "")) if e.get("cuisine") else ""
    price = html.escape(e.get("price_tier", "")) if e.get("price_tier") else ""
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

    meta_bits = " · ".join(b for b in [cuisine, price] if b)
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


def _collect_entities(city_data_dir: Path) -> dict[str, list[tuple[dict, str]]]:
    """Walk restaurants/casual_dining/fine_dining for one city, bucket by
    canonical cuisine slug. Returns {cuisine_slug: [(entity, topic_slug)]}.
    """
    buckets: dict[str, list[tuple[dict, str]]] = defaultdict(list)
    sources = (
        ("restaurants.json", "restaurants", "restaurants"),
        ("casual-dining.json", "casual_dining", "casual-dining"),
        ("fine-dining.json", "fine_dining", "fine-dining"),
    )
    for filename, key, topic_slug in sources:
        p = city_data_dir / filename
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in (d.get(key) or []):
            if not isinstance(e, dict) or not e.get("cuisine"):
                continue
            cc = _canon_cuisine(e["cuisine"])
            if cc is None:
                continue
            buckets[cc.slug].append((e, topic_slug))
    return buckets


def _canonical_display(slug: str) -> str:
    """Resolve canonical slug back to its display name via the cuisine
    canonicaliser. Picks up "Italian", "French Bistro", etc."""
    # The canonicaliser doesn't expose a reverse map, so we round-trip via
    # the data: slugify(display) should match the slug, modulo our hand
    # mapping. Cheapest reliable path: title-case the slug.
    return slug.replace("-", " ").title()


def _render_page(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
                 city_slug: str, city_name: str, cuisine_slug: str,
                 entries: list[tuple[dict, str]]) -> Path:
    cuisine_display = _canonical_display(cuisine_slug)
    n = len(entries)

    canonical = f"{BASE}/{country_slug}/{city_slug}/cuisine/{cuisine_slug}/"
    title = f"{cuisine_display} restaurants in {city_name}: {n} rooms | Cork & Curve"
    description = (
        f"{n} {cuisine_display.lower()} rooms in {city_name} worth booking, with "
        f"editor scores, neighborhoods and what each kitchen does best. "
        f"Editor-picked by TableJourney."
    )
    if len(description) > 165:
        description = description[:162].rsplit(" ", 1)[0] + "..."

    cards_html = "".join(
        _entity_card(e, country_slug, city_slug, topic_slug)
        for (e, topic_slug) in entries
    )

    # ItemList JSON-LD
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{cuisine_display} restaurants in {city_name}",
        "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": f"https://tablejourney.com/{country_slug}/{city_slug}/{topic_slug}/{e.get('slug', '')}/",
                "name": e.get("name", ""),
            }
            for i, (e, topic_slug) in enumerate(entries, start=1)
            if e.get("slug")
        ],
    }
    itemlist_html = (
        '<script type="application/ld+json">'
        + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":"))
        + '</script>'
    )

    # Build the map section only when the result set is large enough to
    # justify a 420px Leaflet container. Avoids the LCP/CLS hit on 2-3
    # pin pages where the map dominates the viewport. See STANDARDS §2d.
    map_section = ''
    if n >= 5:
        map_section = (
            f'<section aria-label="Map of {cuisine_display} rooms in {city_name}">'
            f'<div class="tj-citymap-wrap">'
            f'<div class="tj-citymap" data-pins-url="/{country_slug}/{city_slug}/_pins.json" '
            f'data-filter-cuisine="{cuisine_slug}"></div>'
            f'</div>'
            f'</section>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {cuisine_display.lower()} rooms in {city_name}, '
        f'editor-picked by TableJourney. '
        f'<a href="/{country_slug}/{city_slug}/cuisines/">All cuisines in {city_name}</a> '
        f'| <a href="/cuisine/{cuisine_slug}/">{cuisine_display} across every city</a>.'
        f'</p>'
        + map_section
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card", placeholder="Filter by name, neighborhood…", aria_label="Filter list") + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + itemlist_html
    )

    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": city_name, "url": f"{BASE}/{country_slug}/{city_slug}/"},
        {"position": 4, "name": "Cuisines", "url": f"{BASE}/{country_slug}/{city_slug}/cuisines/"},
        {"position": 5, "name": cuisine_display, "url": None},
    ]

    page_ctx = {
        "title": title,
        "meta_description": description,
        "h1": f"{cuisine_display} in {city_name}",
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
    out = CONTENT / country_slug / city_slug / "cuisine" / cuisine_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        template.render(
            page=page_ctx,
            seo=seo,
            analytics={"page_type": "city-cuisine", "destination": f"{city_slug}-{cuisine_slug}"},
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
            if not rj.exists():
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                # Mirror chrome-page convention: only treat as stub if the
                # city hub hasn't shipped yet.
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = (region.get("destination") or {}).get("name") or city_slug.replace("-", " ").title()

            buckets = _collect_entities(city_dir / "data")
            had_any = False
            for cuisine_slug, entries in buckets.items():
                if len(entries) < MIN_ENTITIES:
                    skipped_thin += 1
                    continue
                had_any = True
                p = _render_page(
                    renderer,
                    country_slug=country_slug,
                    country_name=country_name,
                    city_slug=city_slug,
                    city_name=city_name,
                    cuisine_slug=cuisine_slug,
                    entries=entries,
                )
                written.add(p)
            if had_any:
                n_cities += 1

    # Prune stale (city, cuisine) pages.
    pruned = 0
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            cuisine_dir = city_dir / "cuisine"
            if not cuisine_dir.is_dir():
                continue
            for slug_dir in list(cuisine_dir.iterdir()):
                if not slug_dir.is_dir():
                    continue
                idx = slug_dir / "index.html"
                if idx.exists() and idx not in written:
                    shutil.rmtree(slug_dir)
                    pruned += 1
            # Drop the parent cuisine/ dir entirely if it's empty after pruning.
            if cuisine_dir.is_dir() and not any(cuisine_dir.iterdir()):
                cuisine_dir.rmdir()

    print(
        f"wrote {len(written)} city×cuisine pages across {n_cities} cities "
        f"(skipped {skipped_thin} thin combos with <{MIN_ENTITIES} entities)"
    )
    if pruned:
        print(f"pruned {pruned} stale city×cuisine pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
