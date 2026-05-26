#!/usr/bin/env python3
"""Generate per-country cuisine rollup pages.

For every (country, cuisine) with enough content, emit a country-level
top-list:

  /<country>/cuisine/italian/
  /<country>/cuisine/japanese-sushi/
  /<country>/cuisine/mexican/
  ...

Sibling of generate_city_cuisine.py at country scope. Reads restaurants
/ casual-dining / fine-dining across every city in the country, buckets
by canonical cuisine, ships the top entities per (country, cuisine).

Usage:
    python scripts/generate_country_cuisine.py
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

MIN_ENTITIES = 1
TOP_N = 30

SOURCES = (
    ("restaurants.json",   "restaurants",   "restaurants"),
    ("casual-dining.json", "casual_dining", "casual-dining"),
    ("fine-dining.json",   "fine_dining",   "fine-dining"),
)


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


def _cuisine_display(slug: str) -> str:
    return slug.replace("-", " ").title()


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


def _collect(country_dir: Path) -> dict[str, list[tuple[dict, str, str, str]]]:
    """Returns {cuisine_slug: [(entity, city_slug, city_name, topic_slug)]}."""
    buckets: dict[str, list[tuple[dict, str, str, str]]] = defaultdict(list)
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
            hub = CONTENT / country_dir.name / city_slug / "index.html"
            if not hub.exists():
                continue
        city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()
        for fname, key, topic in SOURCES:
            p = city_dir / "data" / fname
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
                score = e.get("editorial_score")
                if not isinstance(score, (int, float)) or score < 3.5:
                    continue
                buckets[cc.slug].append((e, city_slug, city_name, topic))
    for k in list(buckets.keys()):
        buckets[k].sort(key=lambda t: t[0].get("editorial_score", 0), reverse=True)
        buckets[k] = buckets[k][:TOP_N]
    return buckets


def _render(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
            cuisine_slug: str, entries: list[tuple[dict, str, str, str]],
            available_cuisines: set[str]) -> Path:
    cuisine_display = _cuisine_display(cuisine_slug)
    n = len(entries)
    canonical = f"{BASE}/{country_slug}/cuisine/{cuisine_slug}/"
    title = f"Top {cuisine_display} restaurants in {country_name}: {n} rooms | Cork & Curve"
    description = (
        f"The best {n} {cuisine_display.lower()} rooms across {country_name}, "
        f"editor-picked with neighborhoods, what to order and where to book."
    )
    if len(description) > 165:
        from utils.seo import _smart_truncate as _mt
        description = _mt(description, max_len=158)

    cards_html = "".join(_entity_card(e, country_slug, cs, t, cn) for e, cs, cn, t in entries)
    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": f"{cuisine_display} restaurants in {country_name}", "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "url": f"https://tablejourney.com/{country_slug}/{cs}/{t}/{e.get('slug','')}/",
             "name": e.get("name", "")}
            for i, (e, cs, _, t) in enumerate(entries, start=1) if e.get("slug")
        ],
    }
    itemlist_html = '<script type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":")) + '</script>'

    cross_items = [s for s in sorted(available_cuisines) if s != cuisine_slug][:12]
    cross_html = ""
    if cross_items:
        items_html = "".join(
            f'<li><a href="/{country_slug}/cuisine/{s}/">{_cuisine_display(s)} in {country_name}</a></li>'
            for s in cross_items
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">More cuisines across {country_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )
    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {cuisine_display.lower()} rooms worth the trip across {country_name}, '
        f'editor-ranked. <a href="/{country_slug}/cuisines/">All cuisines in {country_name}</a>.'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card", placeholder="Filter by name, neighborhood…", aria_label="Filter list") + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html + itemlist_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": "Cuisines", "url": f"{BASE}/{country_slug}/cuisines/"},
        {"position": 4, "name": cuisine_display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"Top {cuisine_display} restaurants in {country_name}",
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
    out = CONTENT / country_slug / "cuisine" / cuisine_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "country-cuisine", "destination": f"{country_slug}-{cuisine_slug}"},
        base_path="", topic_nav=FOOD_TOPIC_NAV, breadcrumb=breadcrumb, current_year=2026,
    ), encoding="utf-8")
    return out


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    by_country: dict[str, set[str]] = defaultdict(set)

    candidates: dict[tuple[str, str], list] = {}
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        buckets = _collect(country_dir)
        for cuisine_slug, entries in buckets.items():
            if len(entries) >= MIN_ENTITIES:
                candidates[(country_dir.name, cuisine_slug)] = entries
                by_country[country_dir.name].add(cuisine_slug)

    for (country_slug, cuisine_slug), entries in candidates.items():
        p = _render(renderer, country_slug=country_slug,
                    country_name=_country_display(country_slug),
                    cuisine_slug=cuisine_slug, entries=entries,
                    available_cuisines=by_country[country_slug])
        written.add(p)

    pruned = 0
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        cuisine_dir = country_dir / "cuisine"
        if not cuisine_dir.is_dir():
            continue
        for sub in cuisine_dir.iterdir():
            if not sub.is_dir():
                continue
            idx = sub / "index.html"
            if idx.exists() and idx not in written:
                shutil.rmtree(sub)
                pruned += 1

    print(f"wrote {len(written)} country×cuisine pages across {len(by_country)} countries")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
