#!/usr/bin/env python3
"""Generate global cross-city "top <topic>" rollup pages.

For every supported topic, walk every city, aggregate entities sorted by
editorial_score descending, and emit a single global landing page:

  /rooftops/                 (every rooftop_bars entity across the site)
  /speakeasies/              (every speakeasies entity)
  /dance-clubs/              (every dance_clubs entity)
  /live-music/               (every live_music entity)
  /lgbtq/                    (every lgbtq nightlife entity)
  /listening-bars/           (every listening_bars entity)
  /late-night-dives/         (every late_night_dives entity)
  /wine-bars-global/         (every wine_bars entity across cities)
  /coffee-roasters-global/   (every coffee_roasters entity)
  /best-brunch/              (every brunch entity)
  /best-cocktails/           (every bars entity with cocktail flag — proxy: editorial_score >= 4)

These are the highest-volume head-term queries ("best rooftops worldwide",
"best speakeasies") which the city-scoped pages don't compete for.

URL slug deliberately uses singular topic word at root level so we don't
collide with existing chrome pages. Top-N cap keeps the page curated.

Each entity card on the page links to the entity's home city page. The
page is reachable from /topics/ (already lists all cross-cuts), so no
orphan.

Usage:
    python scripts/generate_global_top_topics.py
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

MIN_ENTITIES = 3
TOP_N = 50  # global pages get a longer top-list since the catchment is huge

# Each entry: (URL slug, JSON file, list key | dict key, display label, blurb)
# For nightlife subcategories, file is nightlife.json and we walk
# payload["nightlife"][subkey].
TOPIC_SPECS = [
    # Nightlife subcategories — global head-terms.
    {"url_slug": "rooftops",         "file": "nightlife", "subkey": "rooftop_bars",     "display": "Rooftop Bars",       "blurb": "the best skyline-view rooftop bars in the cities we cover."},
    {"url_slug": "speakeasies",      "file": "nightlife", "subkey": "speakeasies",      "display": "Speakeasies",        "blurb": "hidden-door cocktail bars with serious bartenders, worldwide."},
    {"url_slug": "dance-clubs",      "file": "nightlife", "subkey": "dance_clubs",      "display": "Dance Clubs",        "blurb": "techno, house and electronic clubs with serious dancefloors."},
    {"url_slug": "live-music",       "file": "nightlife", "subkey": "live_music",       "display": "Live Music Venues",  "blurb": "jazz cellars, indie rooms, rock pubs and intimate gig venues."},
    {"url_slug": "lgbtq-nightlife",  "file": "nightlife", "subkey": "lgbtq",            "display": "LGBTQ+ Nightlife",   "blurb": "queer-coded bars, clubs and party nights worth the trip."},
    {"url_slug": "listening-bars",   "file": "nightlife", "subkey": "listening_bars",   "display": "Listening Bars",     "blurb": "audiophile vinyl bars with curated sound, worldwide."},
    {"url_slug": "late-night-dives", "file": "nightlife", "subkey": "late_night_dives", "display": "Late-Night Dives",   "blurb": "cheap character bars open past 02:00."},
    # Food topics — global head-terms.
    {"url_slug": "best-brunch",      "file": "brunch",           "list_key": "brunch",          "display": "Best Brunch",          "blurb": "the best weekend brunch destinations worldwide."},
    {"url_slug": "best-coffee",      "file": "coffee-roasters",  "list_key": "coffee_roasters", "display": "Best Coffee Roasters", "blurb": "third-wave roasters and specialty coffee bars worldwide."},
    {"url_slug": "best-wine-bars",   "file": "wine-bars",        "list_key": "wine_bars",       "display": "Best Wine Bars",       "blurb": "natural and classic wine bars worldwide."},
    {"url_slug": "best-bakeries",    "file": "bakeries",         "list_key": "bakeries",        "display": "Best Bakeries",        "blurb": "the bread, pastry and morning baking destinations editors send friends to."},
    {"url_slug": "best-markets",     "file": "markets",          "list_key": "markets",         "display": "Best Food Markets",    "blurb": "produce, fish and food halls worth a flight."},
    {"url_slug": "best-breweries",   "file": "breweries",        "list_key": "breweries",       "display": "Best Craft Breweries", "blurb": "the craft breweries with destination taprooms."},
    {"url_slug": "best-cocktail-bars","file": "bars",            "list_key": "bars",            "display": "Best Cocktail Bars",   "blurb": "cocktail icons and serious drinking destinations worldwide."},
]


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



def _entity_card(e: dict, country_slug: str, city_slug: str, topic_path: str, city_name: str) -> str:
    name = html.escape(e.get("name", ""))
    addr = html.escape(e.get("address", ""))
    desc = html.escape(e.get("description", ""))
    nbhd = html.escape(e.get("neighborhood", "")) if e.get("neighborhood") else ""
    score = e.get("editorial_score")
    score_html = ""
    if isinstance(score, (int, float)) and 1.0 <= score <= 5.0:
        score_html = f' <span class="tj-entity-score">★ {score:.1f}</span>'
    slug = e.get("slug") or ""
    href = f"/{country_slug}/{city_slug}/{topic_path}/{slug}/" if slug else ""
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


def _collect(spec: dict) -> list[tuple[dict, str, str, str]]:
    """Returns [(entity, country_slug, city_slug, city_name)]."""
    fname = spec["file"] + ".json"
    is_nightlife = "subkey" in spec
    out: list[tuple[dict, str, str, str]] = []
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country_slug = country_dir.name
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city_slug = city_dir.name
            rj = city_dir / "data" / "region.json"
            tj = city_dir / "data" / fname
            if not rj.exists() or not tj.exists():
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
                payload = json.loads(tj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()
            if is_nightlife:
                entries = (payload.get("nightlife") or {}).get(spec["subkey"]) or []
            else:
                entries = payload.get(spec["list_key"]) or []
            if not isinstance(entries, list):
                continue
            for e in entries:
                if not isinstance(e, dict):
                    continue
                score = e.get("editorial_score")
                if not isinstance(score, (int, float)) or score < 3.5:
                    continue
                out.append((e, country_slug, city_slug, city_name))
    out.sort(key=lambda t: t[0].get("editorial_score", 0), reverse=True)
    return out[:TOP_N]


def _render(renderer: TemplateRenderer, *, spec: dict, entries: list[tuple[dict, str, str, str]],
            all_top_topic_links: list[dict]) -> Path:
    url_slug = spec["url_slug"]
    display = spec["display"]
    blurb = spec["blurb"]
    n = len(entries)
    canonical = f"{BASE}/{url_slug}/"
    title = f"{display} Worldwide: {n} editor picks | Cork & Curve"
    description = f"The best {n} {display.lower()} across every city we cover. {blurb}"
    if len(description) > 165:
        from utils.seo import _smart_truncate as _mt
        description = _mt(description, max_len=158)

    # Topic path mapping: nightlife entities live under /<country>/<city>/nightlife/<slug>/.
    # Food topics live under /<country>/<city>/<topic-slug>/<slug>/.
    topic_path = "nightlife" if "subkey" in spec else spec["file"]
    cards_html = "".join(_entity_card(e, cs, cy, topic_path, cn) for e, cs, cy, cn in entries)

    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": f"{display} worldwide", "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "url": f"https://corkandcurve.com/{cs}/{cy}/{topic_path}/{e.get('slug','')}/",
             "name": e.get("name", "")}
            for i, (e, cs, cy, _) in enumerate(entries, start=1) if e.get("slug")
        ],
    }
    itemlist_html = '<script type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":")) + '</script>'

    # Cross-link to other global top-X pages — keeps the global cluster connected.
    cross_html = ""
    others = [t for t in all_top_topic_links if t["url_slug"] != url_slug]
    if others:
        items_html = "".join(
            f'<li><a href="/{t["url_slug"]}/">{t["display"]} worldwide</a></li>'
            for t in others
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            '<h3 style="margin:0 0 8px; font-size:1rem;">More cross-city editor lists</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {display.lower()} worth the trip across every Cork & Curve region. '
        f'Editor-ranked. {blurb}'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card",
                                placeholder=f"Filter {display.lower()} by name, city…",
                                aria_label=f"Filter {display.lower()}")
        + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html + itemlist_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": "Topics", "url": f"{BASE}/topics/"},
        {"position": 3, "name": display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"{display} Worldwide",
        "subtitle": f"{n} editor-picked rooms across every Cork & Curve region.",
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
    out = CONTENT / url_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "global-top-topic", "destination": url_slug},
        base_path="", topic_nav=FOOD_TOPIC_NAV, breadcrumb=breadcrumb, current_year=2026,
    ), encoding="utf-8")
    return out


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    candidates = []
    for spec in TOPIC_SPECS:
        entries = _collect(spec)
        if len(entries) >= MIN_ENTITIES:
            candidates.append((spec, entries))

    all_top_topic_links = [s for s, _ in candidates]

    for spec, entries in candidates:
        p = _render(renderer, spec=spec, entries=entries, all_top_topic_links=all_top_topic_links)
        written.add(p)

    # Prune stale top-X pages: any /<slug>/ dir matching a topic spec whose
    # data fell below threshold this run.
    pruned = 0
    known = {spec["url_slug"] for spec in TOPIC_SPECS}
    for child in CONTENT.iterdir():
        if not child.is_dir() or child.name not in known:
            continue
        idx = child / "index.html"
        if idx.exists() and idx not in written:
            shutil.rmtree(child)
            pruned += 1

    print(f"wrote {len(written)} global top-topic pages")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
