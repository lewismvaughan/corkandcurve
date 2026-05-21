#!/usr/bin/env python3
"""Generate country-scoped and city-scoped cross-cut index pages.

For every live country and city, emit index pages that show only the
cuisines / signature dishes / neighbourhoods present in that scope:

  /<country>/cuisines/
  /<country>/signature-dishes/
  /<country>/neighborhoods/
  /<country>/<city>/cuisines/
  /<country>/<city>/neighborhoods/

(City-level signature-dishes already exists as a topic chapter on the
city hub, so we don't emit it here.)

Reads the enriched manifests written by generate_cross_cuts.py (cuisine,
dish, neighborhood). Must be run AFTER generate_cross_cuts.py.

Usage:
    python scripts/generate_scoped_cross_cuts.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
SITE_DATA = REPO_ROOT / "site-data"
BASE = "https://tablejourney.com"

_ALPHA_GROUP_THRESHOLD = 25


def _country_display(slug: str) -> str:
    overrides = {
        "usa": "USA",
        "united-states": "United States",
        "united-kingdom": "United Kingdom",
    }
    return overrides.get(slug, slug.replace("-", " ").title())


def _load_manifest(parent: Path) -> list[dict]:
    path = parent / "_manifest.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("entries", [])
    except (OSError, json.JSONDecodeError):
        return []


def _walk_countries_and_cities() -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    """Return (countries, cities).

    countries: list of (country_slug, country_display) for countries that
               have a country-level region.json.
    cities:    list of (country_slug, city_slug, city_display) for every
               shipped city under each country.
    """
    countries: list[tuple[str, str]] = []
    cities: list[tuple[str, str, str]] = []

    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        c_slug = country_dir.name
        country_data = country_dir / "data" / "region.json"
        if country_data.exists():
            try:
                payload = json.loads(country_data.read_text(encoding="utf-8"))
                c_name = payload.get("destination", {}).get("country") or _country_display(c_slug)
            except (OSError, json.JSONDecodeError):
                c_name = _country_display(c_slug)
            countries.append((c_slug, c_name))

        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                payload = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            meta = payload.get("_metadata", {}) or {}
            if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                hub = CONTENT / c_slug / city_dir.name / "index.html"
                if not hub.exists():
                    continue
            city_name = payload.get("destination", {}).get("name") or city_dir.name.replace("-", " ").title()
            cities.append((c_slug, city_dir.name, city_name))

    return countries, cities


def _itemlist_jsonld(entries: list[dict], name: str, *, href_fn) -> str:
    """ItemList schema for a scoped index list. Cap at 50 entries per
    Google's rich-list rendering limits.
    """
    items = []
    for i, e in enumerate(entries[:50], start=1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "url": "https://tablejourney.com" + href_fn(e),
            "name": e["display"],
        })
    blob = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(entries),
        "itemListElement": items,
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(blob, ensure_ascii=False, separators=(",", ":"))
        + '</script>'
    )


_FILTER_SEARCH_HTML = (
    '<div class="tj-filter-search" style="margin:12px 0 16px;">'
    '<input type="search" autocomplete="off" spellcheck="false" '
    'class="tj-filter-search-input" '
    'placeholder="Filter…" '
    'aria-label="Filter list" '
    'data-filter-target="#tj-scoped-list" '
    'data-filter-item="li" '
    'style="width:100%;max-width:420px;padding:10px 14px;'
    'border:1px solid var(--tj-border);border-radius:var(--tj-radius);'
    'background:var(--tj-surface);color:inherit;font-size:1rem;">'
    '</div>'
    '<script>(function(){'
    'function wire(){'
    'var inputs=document.querySelectorAll("input.tj-filter-search-input:not([data-wired])");'
    'inputs.forEach(function(inp){'
    'inp.setAttribute("data-wired","1");'
    'var t=document.querySelector(inp.getAttribute("data-filter-target"));'
    'if(!t)return;'
    'var sel=inp.getAttribute("data-filter-item");'
    'inp.addEventListener("input",function(){'
    'var q=inp.value.trim().toLowerCase();'
    'var items=t.querySelectorAll(sel);'
    'items.forEach(function(it){'
    'var txt=(it.textContent||"").toLowerCase();'
    'it.style.display=(!q||txt.indexOf(q)!==-1)?"":"none";'
    '});'
    '});'
    '});'
    '}'
    'if(document.readyState==="loading"){'
    'document.addEventListener("DOMContentLoaded",wire);'
    '}else{'
    'wire();'
    '}'
    '})();</script>'
)


def _render_alpha_grouped(entries: list[dict], *, href_fn) -> str:
    if not entries:
        return ""
    if len(entries) < _ALPHA_GROUP_THRESHOLD:
        items = "".join(
            f'<li><a href="{href_fn(e)}"><strong>{e["display"]}</strong>'
            + (f' <span class="tj-list-sub">{e["sub"]}</span>' if e.get("sub") else "")
            + "</a></li>"
            for e in entries
        )
        # Filter widget shown when list has >=8 items (small lists don't need it).
        prelude = _FILTER_SEARCH_HTML if len(entries) >= 8 else ""
        return prelude + f'<ul id="tj-scoped-list" class="tj-grid-list">{items}</ul>'

    groups: dict[str, list[dict]] = {}
    for e in entries:
        first = (e["display"][:1] or "#").upper()
        if not ("A" <= first <= "Z"):
            first = "#"
        groups.setdefault(first, []).append(e)
    jumps = "".join(f'<a href="#alpha-{k}">{k}</a>' for k in sorted(groups.keys()))
    sections = []
    for letter in sorted(groups.keys()):
        rows = "".join(
            f'<li><a href="{href_fn(e)}"><strong>{e["display"]}</strong>'
            + (f' <span class="tj-list-sub">{e["sub"]}</span>' if e.get("sub") else "")
            + "</a></li>"
            for e in groups[letter]
        )
        sections.append(
            f'<h2 id="alpha-{letter}">{letter}</h2>'
            f'<ul class="tj-grid-list">{rows}</ul>'
        )
    # Wrap alpha-grouped output in a single container so the filter input
    # can target every <li> across all letter sections at once.
    return (
        _FILTER_SEARCH_HTML
        + f'<nav class="tj-alpha-jumps" aria-label="Jump to letter">{jumps}</nav>'
        + f'<div id="tj-scoped-list">{"".join(sections)}</div>'
    )


def _cuisines_filtered(manifest: list[dict], *, country: str | None, city: str | None) -> list[dict]:
    """Filter the cuisine manifest. Each entry in the result has:
    {slug, display, sub: '<n cities>' or '<n restaurants>'}.
    """
    out = []
    for e in manifest:
        present = [
            c for c in e.get("cities", [])
            if (country is None or c["country_slug"] == country)
            and (city is None or c["city_slug"] == city)
        ]
        if not present:
            continue
        if city is not None:
            n = sum(c.get("n", 0) for c in present)
            sub = f"{n} restaurant{'s' if n != 1 else ''}"
        else:
            nc = len(present)
            sub = f"{nc} cit{'ies' if nc != 1 else 'y'}"
        out.append({"slug": e["slug"], "display": e["display"], "sub": sub})
    out.sort(key=lambda e: e["display"].lower())
    return out


def _dishes_filtered(manifest: list[dict], *, country: str | None, city: str | None) -> list[dict]:
    out = []
    for e in manifest:
        present = [
            c for c in e.get("cities", [])
            if (country is None or c["country_slug"] == country)
            and (city is None or c["city_slug"] == city)
        ]
        if not present:
            continue
        if city is not None:
            n = sum(c.get("n", 0) for c in present)
            sub = f"{n} room{'s' if n != 1 else ''}"
        else:
            nc = len(present)
            sub = f"{nc} cit{'ies' if nc != 1 else 'y'}"
        out.append({"slug": e["slug"], "display": e["display"], "sub": sub})
    out.sort(key=lambda e: e["display"].lower())
    return out


def _neighborhoods_filtered_country(manifest: list[dict], country: str) -> str:
    """Country-scoped neighborhoods: group by city, list hoods under each."""
    by_city: dict[tuple[str, str], list[dict]] = {}
    for e in manifest:
        if e.get("country_slug") != country:
            continue
        by_city.setdefault((e["city_slug"], e["city_name"]), []).append(e)

    if not by_city:
        return ""

    def _nat_key(e: dict):
        m = re.match(r"^(\d+)", e["slug"])
        return (0, int(m.group(1))) if m else (1, e["display"].lower())

    sections = []
    for (city_slug, city_name) in sorted(by_city.keys(), key=lambda x: x[1].lower()):
        hoods = sorted(by_city[(city_slug, city_name)], key=_nat_key)
        items = "".join(
            f'<li><a href="/neighborhood/{city_slug}/{h["slug"]}/">'
            f'<strong>{h["display"]}</strong></a></li>'
            for h in hoods
        )
        sections.append(
            f'<h2><a href="/{country}/{city_slug}/">{city_name}</a></h2>'
            f'<ul class="tj-grid-list">{items}</ul>'
        )
    return "".join(sections)


def _neighborhoods_filtered_city(manifest: list[dict], city: str) -> str:
    """City-scoped neighborhoods: flat alpha-ordered list."""
    hoods = [e for e in manifest if e.get("city_slug") == city]
    if not hoods:
        return ""

    def _nat_key(e: dict):
        m = re.match(r"^(\d+)", e["slug"])
        return (0, int(m.group(1))) if m else (1, e["display"].lower())

    hoods.sort(key=_nat_key)
    items = "".join(
        f'<li><a href="/neighborhood/{e["city_slug"]}/{e["slug"]}/">'
        f'<strong>{e["display"]}</strong></a></li>'
        for e in hoods
    )
    return f'<ul class="tj-grid-list">{items}</ul>'


def crumb(*items):
    return [{"position": i, "name": n, "url": u} for i, (n, u) in enumerate(items, start=1)]


def _render_scoped_page(renderer: TemplateRenderer, spec: dict) -> Path:
    canonical = f"{BASE}/{spec['slug']}/"
    page_ctx = {
        "title": spec["title"],
        "meta_description": spec["meta_description"],
        "h1": spec["h1"],
        "subtitle": spec.get("subtitle", ""),
        "canonical_url": canonical,
        "body_html": spec["body"],
        "breadcrumb_items": spec["breadcrumb"],
        "page_type": "collection",
        "updated": "May 2026",
        "modified": "2026-05-19",
    }
    seo = {
        "meta": {
            "title": spec["title"],
            "description": spec["meta_description"],
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        },
        "open_graph": {
            "og_title": spec["title"],
            "og_description": spec["meta_description"],
            "og_url": canonical,
            "og_type": "website",
            "og_image": "https://tablejourney.com/og/default.jpg",
            "og_image_alt": "TableJourney food guide",
            "og_locale": "en_US",
        },
        "twitter": {
            "twitter_title": spec["title"],
            "twitter_description": spec["meta_description"],
        },
        "structured_data": {"breadcrumb_items": spec["breadcrumb"]},
        "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    html = template.render(
        page=page_ctx,
        seo=seo,
        analytics={
            "page_type": "scoped-cross-cut",
            "destination": spec["slug"],
        },
        base_path="",
        topic_nav=FOOD_TOPIC_NAV,
        breadcrumb=spec["breadcrumb"],
        current_year=2026,
    )
    out = CONTENT / spec["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def main() -> int:
    cuisine_manifest = _load_manifest(CONTENT / "cuisine")
    dish_manifest = _load_manifest(CONTENT / "dish")
    nb_manifest = _load_manifest(CONTENT / "neighborhood")

    countries, cities = _walk_countries_and_cities()
    renderer = TemplateRenderer()
    written = 0
    skipped_empty = 0
    written_paths: set[Path] = set()

    def _intro_country(scope_word: str, kind: str, country: str) -> str:
        return (
            f"<p>{scope_word} found across every {country} city we cover on "
            f"TableJourney. Click through to see the rooms and what to order "
            f"in each city. Want the global picture? "
            f"<a href=\"/{kind}/\">Browse all {kind}</a>.</p>"
        )

    def _intro_city(scope_word: str, kind: str, city: str, country_slug: str) -> str:
        return (
            f"<p>{scope_word} represented in our {city} guide. Click through "
            f"to the entry to see editor-picked rooms, what to order and how "
            f"to book. Want a wider lens? "
            f"<a href=\"/{country_slug}/{kind}/\">All {kind} in this country</a> "
            f"or <a href=\"/{kind}/\">global {kind} index</a>.</p>"
        )

    # COUNTRY scope
    for country_slug, country_name in countries:
        # cuisines — link DOWN to /<country>/cuisine/<slug>/ when that page
        # exists (emitted by generate_country_cuisine.py). Falls back to
        # global only if the country rollup page doesn't exist for this
        # cuisine. Same no-orphan + scope-down discipline as the city scope.
        items = _cuisines_filtered(cuisine_manifest, country=country_slug, city=None)
        if items:
            def _country_or_global_cuisine_href(e, _cs=country_slug):
                country_page = CONTENT / _cs / "cuisine" / e["slug"] / "index.html"
                if country_page.exists():
                    return f"/{_cs}/cuisine/{e['slug']}/"
                return f"/cuisine/{e['slug']}/"
            href = _country_or_global_cuisine_href
            body = (
                _intro_country(f"{len(items)} cuisines", "cuisines", country_name)
                + _render_alpha_grouped(items, href_fn=href)
                + _itemlist_jsonld(items, f"Cuisines in {country_name}", href_fn=href)
            )
            spec = {
                "slug": f"{country_slug}/cuisines",
                "title": f"Cuisines in {country_name} | TableJourney",
                "meta_description": (
                    f"Every cuisine represented across {country_name} on TableJourney, "
                    f"with the cities where each is at its best and editor-picked rooms to book."
                )[:165],
                "h1": f"Cuisines in {country_name}",
                "subtitle": f"What {country_name} eats, plate by plate, across every city we cover.",
                "body": body,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (country_name, f"{BASE}/{country_slug}/"),
                    ("Cuisines", None),
                ),
            }
            written_paths.add(_render_scoped_page(renderer, spec))
            written += 1
        else:
            skipped_empty += 1

        # signature dishes — link DOWN to /<country>/dish/<slug>/ when that
        # page exists (emitted by generate_country_dish.py). Falls back to
        # global only if no country rollup for this dish.
        items = _dishes_filtered(dish_manifest, country=country_slug, city=None)
        if items:
            def _country_or_global_dish_href(e, _cs=country_slug):
                country_page = CONTENT / _cs / "dish" / e["slug"] / "index.html"
                if country_page.exists():
                    return f"/{_cs}/dish/{e['slug']}/"
                return f"/dish/{e['slug']}/"
            href = _country_or_global_dish_href
            body = (
                _intro_country(f"{len(items)} signature dishes", "dishes", country_name)
                + _render_alpha_grouped(items, href_fn=href)
                + _itemlist_jsonld(items, f"Signature dishes of {country_name}", href_fn=href)
            )
            spec = {
                "slug": f"{country_slug}/signature-dishes",
                "title": f"Signature dishes of {country_name} | TableJourney",
                "meta_description": (
                    f"The plates that define {country_name}: what each dish is, where to eat the canonical "
                    f"version and which city does it best, indexed across every TableJourney city."
                )[:165],
                "h1": f"Signature dishes of {country_name}",
                "subtitle": f"Order what the place is known for. {country_name}, plate by plate.",
                "body": body,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (country_name, f"{BASE}/{country_slug}/"),
                    ("Signature dishes", None),
                ),
            }
            written_paths.add(_render_scoped_page(renderer, spec))
            written += 1
        else:
            skipped_empty += 1

        # neighborhoods
        body_hoods = _neighborhoods_filtered_country(nb_manifest, country_slug)
        if body_hoods:
            n_hoods = sum(1 for e in nb_manifest if e.get("country_slug") == country_slug)
            intro = (
                f"<p>{n_hoods} neighbourhoods across {country_name}, grouped by city. "
                f"Plan dinner by the door you walk out of. Want the global view? "
                f"<a href=\"/neighborhoods/\">Browse every neighbourhood</a>.</p>"
            )
            spec = {
                "slug": f"{country_slug}/neighborhoods",
                "title": f"Neighbourhoods of {country_name} | TableJourney",
                "meta_description": (
                    f"Every {country_name} neighbourhood we cover on TableJourney, grouped by city. "
                    f"Plan your eating by the district you're staying in, not by a mega-list."
                )[:165],
                "h1": f"Neighbourhoods of {country_name}",
                "subtitle": "Plan dinner by the door you walk out of.",
                "body": intro + body_hoods,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (country_name, f"{BASE}/{country_slug}/"),
                    ("Neighbourhoods", None),
                ),
            }
            written_paths.add(_render_scoped_page(renderer, spec))
            written += 1
        else:
            skipped_empty += 1

    # CITY scope
    for country_slug, city_slug, city_name in cities:
        # cuisines — link DOWN to the city × cuisine page when it exists
        # (otherwise the city × cuisine pages become orphans). SEO standard:
        # when both a city-scoped and global cross-cut exist, scoped pages
        # link DOWN to the city-specific child, not UP to the global parent.
        # See docs/STANDARDS.md.
        items = _cuisines_filtered(cuisine_manifest, country=country_slug, city=city_slug)
        if items:
            def _city_or_global_cuisine_href(e, _cs=country_slug, _cy=city_slug):
                city_page = CONTENT / _cs / _cy / "cuisine" / e["slug"] / "index.html"
                if city_page.exists():
                    return f"/{_cs}/{_cy}/cuisine/{e['slug']}/"
                return f"/cuisine/{e['slug']}/"
            href = _city_or_global_cuisine_href
            body = (
                _intro_city(f"{len(items)} cuisines", "cuisines", city_name, country_slug)
                + _render_alpha_grouped(items, href_fn=href)
                + _itemlist_jsonld(items, f"Cuisines in {city_name}", href_fn=href)
            )
            spec = {
                "slug": f"{country_slug}/{city_slug}/cuisines",
                "title": f"Cuisines in {city_name} | TableJourney",
                "meta_description": (
                    f"Every cuisine represented in our {city_name} guide on TableJourney, "
                    f"with editor-picked rooms and what each kitchen does best."
                )[:165],
                "h1": f"Cuisines in {city_name}",
                "subtitle": f"What {city_name} cooks, plate by plate.",
                "body": body,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (_country_display(country_slug), f"{BASE}/{country_slug}/"),
                    (city_name, f"{BASE}/{country_slug}/{city_slug}/"),
                    ("Cuisines", None),
                ),
            }
            written_paths.add(_render_scoped_page(renderer, spec))
            written += 1
        else:
            skipped_empty += 1

        # neighborhoods
        body_hoods = _neighborhoods_filtered_city(nb_manifest, city_slug)
        if body_hoods:
            n_hoods = sum(1 for e in nb_manifest if e.get("city_slug") == city_slug)
            intro = (
                f"<p>{n_hoods} neighbourhoods in our {city_name} guide. "
                f"Click a district to see every restaurant, bar, market and bakery we cover there. "
                f"<a href=\"/{country_slug}/neighborhoods/\">All neighbourhoods in this country</a>.</p>"
            )
            spec = {
                "slug": f"{country_slug}/{city_slug}/neighborhoods",
                "title": f"Neighbourhoods of {city_name} | TableJourney",
                "meta_description": (
                    f"Every {city_name} neighbourhood we cover, with the restaurants, bars, markets and "
                    f"bakeries inside each. Plan dinner by the district you're staying in."
                )[:165],
                "h1": f"Neighbourhoods of {city_name}",
                "subtitle": "Plan dinner by the door you walk out of.",
                "body": intro + body_hoods,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (_country_display(country_slug), f"{BASE}/{country_slug}/"),
                    (city_name, f"{BASE}/{country_slug}/{city_slug}/"),
                    ("Neighbourhoods", None),
                ),
            }
            written_paths.add(_render_scoped_page(renderer, spec))
            written += 1
        else:
            skipped_empty += 1

    # Prune stale scoped pages we no longer emit (city/country dropped, or
    # data emptied). Walk content/<country>/cuisines, /signature-dishes,
    # /neighborhoods, plus city versions, and remove any index.html that
    # wasn't written this run.
    pruned = 0
    scoped_subdirs = ("cuisines", "signature-dishes", "neighborhoods")
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for sub in scoped_subdirs:
            p = country_dir / sub / "index.html"
            if p.exists() and p not in written_paths:
                shutil.rmtree(p.parent)
                pruned += 1
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            for sub in ("cuisines", "neighborhoods"):
                p = city_dir / sub / "index.html"
                if p.exists() and p not in written_paths:
                    shutil.rmtree(p.parent)
                    pruned += 1

    print(f"wrote {written} scoped cross-cut pages ({skipped_empty} scopes had no data)")
    if pruned:
        print(f"pruned {pruned} stale scoped pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
