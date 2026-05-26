#!/usr/bin/env python3
"""Generate per-neighborhood × cuisine rollup pages.

For every (city, neighborhood, cuisine) combo with >= MIN_ENTITIES entities,
emit a hyper-targeted long-tail page:

  /neighborhood/rome/trastevere/italian/
  /neighborhood/paris/marais/french-bistro/
  /neighborhood/tokyo/shibuya/japanese-sushi/
  ...

These target the "<cuisine> <neighborhood>" head term Google sees a lot of
("italian trastevere", "natural wine east village"). Restaurant cards link
to the entity's home page; cross-links surface sibling cuisines in the
same neighborhood + same cuisine in other neighborhoods.

Sibling URL pattern with the existing /neighborhood/<city>/<nbhd>/ pages.

Re-runnable; rewrites every page each run; prunes stale leaves.

Usage:
    python scripts/generate_neighborhood_cuisine.py
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402
from utils.cuisine import canonicalise as _canon_cuisine  # noqa: E402
from utils.filter_search import filter_search_widget  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

MIN_ENTITIES = 1
TOP_N = 20

SOURCES = (
    ("restaurants.json",   "restaurants",   "restaurants"),
    ("casual-dining.json", "casual_dining", "casual-dining"),
    ("fine-dining.json",   "fine_dining",   "fine-dining"),
)


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


def _slugify(s: str) -> str:
    """Minimal slugify for matching against neighborhoods.json aliases.
    Lowercase, strip diacritics-ish, collapse non-alnum to single dash."""
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


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



def _entity_card(e: dict, country_slug: str, city_slug: str, topic_slug: str) -> str:
    name = html.escape(e.get("name", ""))
    addr = html.escape(e.get("address", ""))
    desc = html.escape(e.get("description", ""))
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
    parts = [title_html, f'<h3 class="tj-entity-name">{name}{score_html}</h3>']
    if addr:
        parts.append(f'<p class="tj-entity-locale">{addr}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    if e.get("tip"):
        parts.append(f'<p class="tj-entity-desc"><strong>Tip:</strong> {html.escape(e["tip"])}</p>')
    parts.append(closer)
    return "".join(parts)


def _city_neighborhood_lookup(neighborhoods: list) -> dict[str, dict]:
    """Build a normalized lookup: matching-string → {slug, name}.
    Indexes by the canonical name, every alias, and the slug itself."""
    out: dict[str, dict] = {}
    for nb in neighborhoods or []:
        if not isinstance(nb, dict):
            continue
        slug = nb.get("slug")
        name = nb.get("name")
        if not slug or not name:
            continue
        meta = {"slug": slug, "name": name}
        keys = {_slugify(name), _slugify(slug)}
        for alias in (nb.get("aliases") or []):
            if isinstance(alias, str):
                keys.add(_slugify(alias))
        for k in keys:
            if k and k not in out:
                out[k] = meta
    return out


def _collect_city(country_slug: str, city_slug: str, city_name: str,
                   nbhd_lookup: dict) -> dict[tuple[str, str], list]:
    """Returns {(nbhd_slug, cuisine_slug): [(entity, topic_slug, nbhd_name)]}."""
    buckets: dict[tuple[str, str], list] = defaultdict(list)
    for fname, key, topic in SOURCES:
        p = SITE_DATA / country_slug / city_slug / "data" / fname
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for e in (d.get(key) or []):
            if not isinstance(e, dict):
                continue
            raw_nb = e.get("neighborhood")
            raw_cu = e.get("cuisine")
            if not raw_nb or not raw_cu:
                continue
            nb_match = nbhd_lookup.get(_slugify(raw_nb))
            if not nb_match:
                continue
            cc = _canon_cuisine(raw_cu)
            if cc is None:
                continue
            buckets[(nb_match["slug"], cc.slug)].append((e, topic, nb_match["name"]))
    return buckets


def _render(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
            city_slug: str, city_name: str, nbhd_slug: str, nbhd_name: str,
            cuisine_slug: str, entries: list,
            sibling_cuisines_in_nbhd: list[str],
            sibling_nbhds_with_cuisine: list[tuple[str, str]]) -> Path:
    cuisine_display = _cuisine_display(cuisine_slug)
    n = len(entries)
    canonical = f"{BASE}/neighborhood/{city_slug}/{nbhd_slug}/{cuisine_slug}/"
    title = f"{cuisine_display} in {nbhd_name}, {city_name}: {n} rooms | Cork & Curve"
    description = (
        f"The best {n} {cuisine_display.lower()} rooms in {nbhd_name}, {city_name}, "
        f"editor-picked with what to order, who to ask for, and what to skip."
    )
    if len(description) > 165:
        from utils.seo import _smart_truncate as _mt
        description = _mt(description, max_len=158)

    cards_html = "".join(_entity_card(e, country_slug, city_slug, t) for e, t, _ in entries[:TOP_N])

    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": f"{cuisine_display} in {nbhd_name}, {city_name}", "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "url": f"https://tablejourney.com/{country_slug}/{city_slug}/{t}/{e.get('slug','')}/",
             "name": e.get("name", "")}
            for i, (e, t, _) in enumerate(entries[:TOP_N], start=1) if e.get("slug")
        ],
    }
    itemlist_html = '<script type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":")) + '</script>'

    # Sibling cuisine cross-links — other cuisines available in THIS neighborhood
    cross_cuisines_html = ""
    other_cuisines = [c for c in sibling_cuisines_in_nbhd if c != cuisine_slug][:8]
    if other_cuisines:
        items_html = "".join(
            f'<li><a href="/neighborhood/{city_slug}/{nbhd_slug}/{c}/">{_cuisine_display(c)} in {nbhd_name}</a></li>'
            for c in other_cuisines
        )
        cross_cuisines_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">More cuisines in {nbhd_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )

    # Sibling neighborhood cross-links — same cuisine in OTHER neighborhoods
    cross_nbhds_html = ""
    if sibling_nbhds_with_cuisine:
        items_html = "".join(
            f'<li><a href="/neighborhood/{city_slug}/{ns}/{cuisine_slug}/">{_cuisine_display(cuisine_slug)} in {nn}</a></li>'
            for ns, nn in sibling_nbhds_with_cuisine[:8]
        )
        cross_nbhds_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">{cuisine_display} in other {city_name} neighborhoods</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {cuisine_display.lower()} rooms in {nbhd_name}, editor-picked by '
        f'TableJourney. <a href="/neighborhood/{city_slug}/{nbhd_slug}/">All of {nbhd_name}\'s food</a> · '
        f'<a href="/{country_slug}/{city_slug}/cuisine/{cuisine_slug}/">All {cuisine_display.lower()} in {city_name}</a>.'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card",
                                placeholder="Filter by name, address…",
                                aria_label="Filter list")
        + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_cuisines_html + cross_nbhds_html + itemlist_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": city_name, "url": f"{BASE}/{country_slug}/{city_slug}/"},
        {"position": 3, "name": nbhd_name, "url": f"{BASE}/neighborhood/{city_slug}/{nbhd_slug}/"},
        {"position": 4, "name": cuisine_display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"{cuisine_display} in {nbhd_name}",
        "subtitle": f"{n} editor-picked rooms in {nbhd_name}, {city_name}.",
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
    out = CONTENT / "neighborhood" / city_slug / nbhd_slug / cuisine_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "neighborhood-cuisine", "destination": f"{city_slug}-{nbhd_slug}-{cuisine_slug}"},
        base_path="", topic_nav=FOOD_TOPIC_NAV, breadcrumb=breadcrumb, current_year=2026,
    ), encoding="utf-8")
    return out


def _inject_cuisine_block_into_neighborhood_index(
    *, city_slug: str, nbhd_slug: str, nbhd_name: str, cuisines: list[str]
) -> None:
    """Patch the rendered /neighborhood/<city>/<nbhd>/index.html to surface
    the cuisine subpages we just emitted under it. Without this the new
    pages have no inbound link from their parent (orphan rule violation).

    Idempotent: if the block already exists, replace it. Detection sentinel
    is the `<!-- nbhd-cuisine-block -->` marker comment.
    """
    idx_path = CONTENT / "neighborhood" / city_slug / nbhd_slug / "index.html"
    if not cuisines:
        return
    if not idx_path.exists():
        # Parent neighborhood index missing — happens when the entity's
        # neighborhood value (e.g. "2e") maps via an alias in
        # neighborhoods.json to a canonical slug ("le-panier") that
        # generate_cross_cuts.py didn't emit. Emit a minimal parent so
        # the cuisine sub-pages have a real inbound link target.
        idx_path.parent.mkdir(parents=True, exist_ok=True)
        stub_links = "".join(
            f'<li><a href="/neighborhood/{city_slug}/{nbhd_slug}/{c}/">'
            f'{_cuisine_display(c)} in {html.escape(nbhd_name)}</a></li>'
            for c in cuisines
        )
        idx_path.write_text(
            '<!doctype html><html lang="en"><head>'
            f'<meta charset="utf-8"><title>{html.escape(nbhd_name)} | Cork & Curve</title>'
            f'<link rel="canonical" href="{BASE}/neighborhood/{city_slug}/{nbhd_slug}/">'
            '<meta name="robots" content="index, follow">'
            '<link rel="stylesheet" href="/css/base.css">'
            '</head><body><main><div class="tj-container tj-prose">'
            f'<h1>{html.escape(nbhd_name)}</h1>'
            f'<p>{html.escape(nbhd_name)} neighborhood food guide, '
            f'<a href="/{city_slug.split("-")[0] if False else ""}">{html.escape(nbhd_name)} on TableJourney</a>.</p>'
            '<!-- nbhd-cuisine-block -->'
            f'<section class="tj-section" id="nbhd-cuisines">'
            f'<h2>Cuisines in {html.escape(nbhd_name)}</h2>'
            f'<ul class="tj-grid-list">{stub_links}</ul>'
            '</section>'
            '<!-- /nbhd-cuisine-block -->'
            '</div></main></body></html>',
            encoding="utf-8",
        )
        return
    items = "".join(
        f'<li><a href="/neighborhood/{city_slug}/{nbhd_slug}/{c}/">'
        f'{_cuisine_display(c)} in {html.escape(nbhd_name)}</a></li>'
        for c in cuisines
    )
    block = (
        '<!-- nbhd-cuisine-block -->'
        '<section class="tj-section" id="nbhd-cuisines">'
        f'<h2>Cuisines in {html.escape(nbhd_name)}</h2>'
        f'<ul class="tj-grid-list">{items}</ul>'
        '</section>'
        '<!-- /nbhd-cuisine-block -->'
    )
    src = idx_path.read_text(encoding="utf-8")
    # Replace existing block if present
    start = src.find("<!-- nbhd-cuisine-block -->")
    end = src.find("<!-- /nbhd-cuisine-block -->")
    if start != -1 and end != -1:
        new = src[:start] + block + src[end + len("<!-- /nbhd-cuisine-block -->"):]
        idx_path.write_text(new, encoding="utf-8")
        return
    # Otherwise inject just before the closing </main> or </article> tag.
    marker = "</main>"
    pos = src.rfind(marker)
    if pos == -1:
        marker = "</article>"
        pos = src.rfind(marker)
    if pos == -1:
        # Last resort: prepend before </body>
        marker = "</body>"
        pos = src.rfind(marker)
    if pos == -1:
        return
    new = src[:pos] + block + src[pos:]
    idx_path.write_text(new, encoding="utf-8")


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    skipped_no_lookup = 0
    cuisines_by_nbhd_global: dict[tuple[str, str], list[str]] = defaultdict(list)
    nbhd_names_global: dict[tuple[str, str], str] = {}

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
            nbj = city_dir / "data" / "neighborhoods.json"
            if not rj.exists() or not nbj.exists():
                skipped_no_lookup += 1
                continue
            try:
                region = json.loads(rj.read_text(encoding="utf-8"))
                nbs = json.loads(nbj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = region.get("_metadata") or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()
            nbhd_lookup = _city_neighborhood_lookup(nbs.get("neighborhoods") or [])
            if not nbhd_lookup:
                skipped_no_lookup += 1
                continue
            buckets = _collect_city(country_slug, city_slug, city_name, nbhd_lookup)
            # Sort each bucket by editorial_score desc
            for k in buckets:
                buckets[k].sort(key=lambda t: t[0].get("editorial_score", 0) or 0, reverse=True)

            # Build sibling indexes for cross-linking
            cuisines_by_nbhd: dict[str, set[str]] = defaultdict(set)
            nbhds_by_cuisine: dict[str, list[tuple[str, str]]] = defaultdict(list)
            nbhd_name_by_slug = {nb["slug"]: nb["name"] for nb in (nbs.get("neighborhoods") or []) if isinstance(nb, dict) and nb.get("slug")}
            for (nbhd_slug, cuisine_slug), entries in buckets.items():
                if len(entries) < MIN_ENTITIES:
                    continue
                cuisines_by_nbhd[nbhd_slug].add(cuisine_slug)
                nm = nbhd_name_by_slug.get(nbhd_slug, nbhd_slug.replace("-", " ").title())
                nbhds_by_cuisine[cuisine_slug].append((nbhd_slug, nm))

            for (nbhd_slug, cuisine_slug), entries in buckets.items():
                if len(entries) < MIN_ENTITIES:
                    continue
                nbhd_name = nbhd_name_by_slug.get(nbhd_slug, nbhd_slug.replace("-", " ").title())
                sibling_cuisines = sorted(cuisines_by_nbhd.get(nbhd_slug, set()))
                sibling_nbhds = sorted(
                    [pair for pair in nbhds_by_cuisine.get(cuisine_slug, []) if pair[0] != nbhd_slug],
                    key=lambda p: p[1]
                )
                p = _render(renderer,
                            country_slug=country_slug, country_name=country_name,
                            city_slug=city_slug, city_name=city_name,
                            nbhd_slug=nbhd_slug, nbhd_name=nbhd_name,
                            cuisine_slug=cuisine_slug, entries=entries,
                            sibling_cuisines_in_nbhd=sibling_cuisines,
                            sibling_nbhds_with_cuisine=sibling_nbhds)
                written.add(p)
                cuisines_by_nbhd_global[(city_slug, nbhd_slug)].append(cuisine_slug)
                nbhd_names_global[(city_slug, nbhd_slug)] = nbhd_name

    # Patch every parent /neighborhood/<city>/<nbhd>/ index page to surface
    # the cuisine sub-pages we just emitted under it. Required by the
    # no-orphan rule: without this, the 378 new pages have no editorial
    # inbound link from the parent.
    injected = 0
    for (cs, ns), cuisines in cuisines_by_nbhd_global.items():
        _inject_cuisine_block_into_neighborhood_index(
            city_slug=cs,
            nbhd_slug=ns,
            nbhd_name=nbhd_names_global.get((cs, ns), ns.replace("-", " ").title()),
            cuisines=sorted(set(cuisines)),
        )
        injected += 1
    if injected:
        print(f"injected nbhd-cuisine link block into {injected} parent neighborhood indexes")

    # Prune stale (nbhd, cuisine) leaves
    pruned = 0
    for city_dir in (CONTENT / "neighborhood").iterdir() if (CONTENT / "neighborhood").is_dir() else []:
        if not city_dir.is_dir():
            continue
        for nbhd_dir in city_dir.iterdir():
            if not nbhd_dir.is_dir():
                continue
            for cuisine_dir in nbhd_dir.iterdir():
                if not cuisine_dir.is_dir():
                    continue
                idx = cuisine_dir / "index.html"
                if idx.exists() and idx not in written:
                    shutil.rmtree(cuisine_dir)
                    pruned += 1

    print(f"wrote {len(written)} neighborhood×cuisine pages (skipped {skipped_no_lookup} cities without neighborhood data)")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
