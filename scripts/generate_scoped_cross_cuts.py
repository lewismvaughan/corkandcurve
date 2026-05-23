#!/usr/bin/env python3
"""Generate global, country-scoped and region-scoped cross-cut index pages.

Emits the index landings that make the per-grape / per-style / per-world
cross-cut pages reachable, plus the sub-appellation indexes:

  /grapes/                          global grape (varietal) index
  /styles/                          global wine-style index
  /world/                           Old World / New World index
  /regions/                         all wine regions, grouped by country
  /<country>/grapes/                grapes present in that country
  /<country>/styles/                styles present in that country
  /<country>/neighborhoods/         sub-appellations grouped by region
  /<country>/<region>/grapes/       grapes present in that region
  /<country>/<region>/styles/       styles present in that region
  /<country>/<region>/neighborhoods/ sub-appellations in that region

Reads the manifests written by generate_cross_cuts.py (grape, style, world,
neighborhood). Must be run AFTER generate_cross_cuts.py.

Usage:
    python scripts/generate_scoped_cross_cuts.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.template_renderer import TemplateRenderer, WINE_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
SITE_DATA = REPO_ROOT / "site-data"
BASE = "https://corkandcurve.com"

_ALPHA_GROUP_THRESHOLD = 25


def _country_display(slug: str) -> str:
    overrides = {
        "usa": "USA",
        "united-states": "United States",
        "united-kingdom": "United Kingdom",
        "new-zealand": "New Zealand",
        "south-africa": "South Africa",
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


def _walk_countries_and_regions() -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    """Return (countries, regions).

    countries: (country_slug, country_display) for countries with a
               country-level region.json.
    regions:   (country_slug, region_slug, region_display) for every shipped
               region under each country.
    """
    countries: list[tuple[str, str]] = []
    regions: list[tuple[str, str, str]] = []

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

        for region_dir in sorted(country_dir.iterdir()):
            if not region_dir.is_dir() or region_dir.name == "data":
                continue
            rj = region_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                payload = json.loads(rj.read_text(encoding="utf-8"))
                r_name = payload.get("destination", {}).get("name") or region_dir.name.replace("-", " ").title()
            except (OSError, json.JSONDecodeError):
                r_name = region_dir.name.replace("-", " ").title()
            regions.append((c_slug, region_dir.name, r_name))

    return countries, regions


def _itemlist_jsonld(entries: list[dict], name: str, *, href_fn) -> str:
    """ItemList schema for a scoped index list. Cap at 50 entries."""
    items = []
    for i, e in enumerate(entries[:50], start=1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "url": BASE + href_fn(e),
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
    return (
        _FILTER_SEARCH_HTML
        + f'<nav class="tj-alpha-jumps" aria-label="Jump to letter">{jumps}</nav>'
        + f'<div id="tj-scoped-list">{"".join(sections)}</div>'
    )


def _present_regions(entry: dict, *, country: str | None, region: str | None) -> list[dict]:
    return [
        r for r in entry.get("regions", [])
        if (country is None or r["country_slug"] == country)
        and (region is None or r["region_slug"] == region)
    ]


def _grape_or_style_filtered(manifest: list[dict], *, country: str | None,
                             region: str | None, unit: str) -> list[dict]:
    """Filter a grape/style manifest to a scope. `unit` is the noun for the
    region-scope count (e.g. 'producer'). Each result: {slug, display, sub}."""
    out = []
    for e in manifest:
        present = _present_regions(e, country=country, region=region)
        if not present:
            continue
        if region is not None:
            n = sum(r.get("n", 0) for r in present)
            sub = f"{n} {unit}{'s' if n != 1 else ''}"
        else:
            nr = len(present)
            sub = f"{nr} region{'s' if nr != 1 else ''}"
        out.append({"slug": e["slug"], "display": e["display"], "sub": sub})
    out.sort(key=lambda e: e["display"].lower())
    return out


def _neighborhoods_filtered_country(manifest: list[dict], country: str) -> str:
    """Country-scoped sub-appellations: group by region, list under each."""
    by_region: dict[tuple[str, str], list[dict]] = {}
    for e in manifest:
        if e.get("country_slug") != country:
            continue
        by_region.setdefault((e["region_slug"], e["region_name"]), []).append(e)
    if not by_region:
        return ""
    sections = []
    for (region_slug, region_name) in sorted(by_region.keys(), key=lambda x: x[1].lower()):
        hoods = sorted(by_region[(region_slug, region_name)], key=lambda e: e["display"].lower())
        items = "".join(
            f'<li><a href="/neighborhood/{region_slug}/{h["slug"]}/">'
            f'<strong>{h["display"]}</strong></a></li>'
            for h in hoods
        )
        sections.append(
            f'<h2><a href="/{country}/{region_slug}/">{region_name}</a></h2>'
            f'<ul class="tj-grid-list">{items}</ul>'
        )
    return "".join(sections)


def _neighborhoods_filtered_region(manifest: list[dict], region_slug: str) -> str:
    """Region-scoped sub-appellations: flat alpha-ordered list."""
    hoods = [e for e in manifest if e.get("region_slug") == region_slug]
    if not hoods:
        return ""
    hoods.sort(key=lambda e: e["display"].lower())
    items = "".join(
        f'<li><a href="/neighborhood/{e["region_slug"]}/{e["slug"]}/">'
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
            "og_image": f"{BASE}/og/default.jpg",
            "og_image_alt": "Cork & Curve wine guide",
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
        topic_nav=WINE_TOPIC_NAV,
        breadcrumb=spec["breadcrumb"],
        current_year=2026,
    )
    out = CONTENT / spec["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def main() -> int:
    grape_manifest = _load_manifest(CONTENT / "grape")
    style_manifest = _load_manifest(CONTENT / "style")
    world_manifest = _load_manifest(CONTENT / "world")
    nb_manifest = _load_manifest(CONTENT / "neighborhood")

    countries, regions = _walk_countries_and_regions()
    renderer = TemplateRenderer()
    written = 0
    skipped_empty = 0
    written_paths: set[Path] = set()

    # ---- GLOBAL index landings -------------------------------------------
    # /grapes/
    if grape_manifest:
        items = [{"slug": e["slug"], "display": e["display"],
                  "sub": f"{len(e.get('regions', []))} region{'s' if len(e.get('regions', [])) != 1 else ''}"}
                 for e in grape_manifest]
        items.sort(key=lambda e: e["display"].lower())
        href = lambda e: f"/grape/{e['slug']}/"
        body = (
            "<p>Every grape we cover, across every wine region on Cork & Curve. "
            "Click through to see how each region expresses the varietal.</p>"
            + _render_alpha_grouped(items, href_fn=href)
            + _itemlist_jsonld(items, "Grapes on Cork & Curve", href_fn=href)
        )
        written_paths.add(_render_scoped_page(renderer, {
            "slug": "grapes",
            "title": "Wine Grapes A to Z | Cork & Curve",
            "meta_description": ("Every grape varietal we cover on Cork & Curve, "
                                 "from Cabernet to Zinfandel, and the regions that grow each best.")[:165],
            "h1": "Wine grapes, A to Z",
            "subtitle": "Every varietal we cover, and where it shines.",
            "body": body,
            "breadcrumb": crumb(("Home", f"{BASE}/"), ("Grapes", None)),
        }))
        written += 1

    # /styles/
    if style_manifest:
        items = [{"slug": e["slug"], "display": e["display"],
                  "sub": f"{len(e.get('regions', []))} region{'s' if len(e.get('regions', [])) != 1 else ''}"}
                 for e in style_manifest]
        items.sort(key=lambda e: e["display"].lower())
        href = lambda e: f"/style/{e['slug']}/"
        body = (
            "<p>Wine by style, from sparkling to fortified, across every region we cover.</p>"
            + _render_alpha_grouped(items, href_fn=href)
            + _itemlist_jsonld(items, "Wine styles on Cork & Curve", href_fn=href)
        )
        written_paths.add(_render_scoped_page(renderer, {
            "slug": "styles",
            "title": "Wine Styles | Cork & Curve",
            "meta_description": ("Browse wine by style on Cork & Curve: sparkling, still, sweet, "
                                 "fortified, orange and natural, and the regions known for each.")[:165],
            "h1": "Wine styles",
            "subtitle": "Sparkling, still, sweet, fortified, orange, natural.",
            "body": body,
            "breadcrumb": crumb(("Home", f"{BASE}/"), ("Styles", None)),
        }))
        written += 1

    # /world/
    if world_manifest:
        items = [{"slug": e["slug"], "display": e["display"],
                  "sub": f"{len(e.get('regions', []))} region{'s' if len(e.get('regions', [])) != 1 else ''}"}
                 for e in world_manifest]
        items.sort(key=lambda e: e["display"].lower())
        href = lambda e: f"/world/{e['slug']}/"
        body = (
            "<p>The classic split: Old World tradition versus New World expression. "
            "Browse the regions in each.</p>"
            + _render_alpha_grouped(items, href_fn=href)
            + _itemlist_jsonld(items, "Old World and New World", href_fn=href)
        )
        written_paths.add(_render_scoped_page(renderer, {
            "slug": "world",
            "title": "Old World vs New World Wine | Cork & Curve",
            "meta_description": ("Old World versus New World wine on Cork & Curve: what divides them "
                                 "and the regions in each camp.")[:165],
            "h1": "Old World and New World",
            "subtitle": "Two ways of thinking about wine.",
            "body": body,
            "breadcrumb": crumb(("Home", f"{BASE}/"), ("World", None)),
        }))
        written += 1

    # /regions/  (all region hubs, grouped by country)
    if regions:
        by_country: dict[str, list[tuple[str, str]]] = {}
        for c_slug, r_slug, r_name in regions:
            by_country.setdefault(c_slug, []).append((r_slug, r_name))
        sections = []
        for c_slug in sorted(by_country.keys(), key=_country_display):
            rows = "".join(
                f'<li><a href="/{c_slug}/{r_slug}/"><strong>{r_name}</strong></a></li>'
                for r_slug, r_name in sorted(by_country[c_slug], key=lambda x: x[1].lower())
            )
            sections.append(
                f'<h2><a href="/{c_slug}/">{_country_display(c_slug)}</a></h2>'
                f'<ul class="tj-grid-list">{rows}</ul>'
            )
        body = (
            "<p>Every wine region we cover, grouped by country.</p>" + "".join(sections)
        )
        written_paths.add(_render_scoped_page(renderer, {
            "slug": "regions",
            "title": "Wine Regions A to Z | Cork & Curve",
            "meta_description": ("Every wine region we cover on Cork & Curve, grouped by country. "
                                 "Vineyards, tasting rooms and signature wines for each.")[:165],
            "h1": "Wine regions",
            "subtitle": "Every region we cover, grouped by country.",
            "body": body,
            "breadcrumb": crumb(("Home", f"{BASE}/"), ("Regions", None)),
        }))
        written += 1

    def _intro_country(scope_word: str, kind: str, country: str) -> str:
        return (
            f"<p>{scope_word} found across every {country} region we cover on "
            f"Cork & Curve. Click through to see the producers in each. "
            f"Want the global picture? <a href=\"/{kind}/\">Browse all {kind}</a>.</p>"
        )

    def _intro_region(scope_word: str, kind: str, region: str, country_slug: str) -> str:
        return (
            f"<p>{scope_word} represented in our {region} guide. Click through "
            f"to see the estates and what to taste. Want a wider lens? "
            f"<a href=\"/{country_slug}/{kind}/\">All {kind} in this country</a> "
            f"or the <a href=\"/{kind}/\">global {kind} index</a>.</p>"
        )

    # ---- COUNTRY scope ----------------------------------------------------
    for country_slug, country_name in countries:
        # grapes
        items = _grape_or_style_filtered(grape_manifest, country=country_slug, region=None, unit="producer")
        if items:
            href = lambda e: f"/grape/{e['slug']}/"
            body = (_intro_country(f"{len(items)} grapes", "grapes", country_name)
                    + _render_alpha_grouped(items, href_fn=href)
                    + _itemlist_jsonld(items, f"Grapes in {country_name}", href_fn=href))
            written_paths.add(_render_scoped_page(renderer, {
                "slug": f"{country_slug}/grapes",
                "title": f"Wine Grapes of {country_name} | Cork & Curve",
                "meta_description": (f"Every grape grown across {country_name} on Cork & Curve, "
                                     f"with the regions where each is at its best.")[:165],
                "h1": f"Wine grapes of {country_name}",
                "subtitle": f"What {country_name} grows, varietal by varietal.",
                "body": body,
                "breadcrumb": crumb(("Home", f"{BASE}/"), (country_name, f"{BASE}/{country_slug}/"), ("Grapes", None)),
            }))
            written += 1
        else:
            skipped_empty += 1

        # styles
        items = _grape_or_style_filtered(style_manifest, country=country_slug, region=None, unit="producer")
        if items:
            href = lambda e: f"/style/{e['slug']}/"
            body = (_intro_country(f"{len(items)} styles", "styles", country_name)
                    + _render_alpha_grouped(items, href_fn=href)
                    + _itemlist_jsonld(items, f"Wine styles in {country_name}", href_fn=href))
            written_paths.add(_render_scoped_page(renderer, {
                "slug": f"{country_slug}/styles",
                "title": f"Wine Styles of {country_name} | Cork & Curve",
                "meta_description": (f"The wine styles made across {country_name} on Cork & Curve, "
                                     f"from sparkling to fortified, region by region.")[:165],
                "h1": f"Wine styles of {country_name}",
                "subtitle": f"How {country_name} makes wine, style by style.",
                "body": body,
                "breadcrumb": crumb(("Home", f"{BASE}/"), (country_name, f"{BASE}/{country_slug}/"), ("Styles", None)),
            }))
            written += 1
        else:
            skipped_empty += 1

        # sub-appellations
        body_hoods = _neighborhoods_filtered_country(nb_manifest, country_slug)
        if body_hoods:
            n_hoods = sum(1 for e in nb_manifest if e.get("country_slug") == country_slug)
            intro = (
                f"<p>{n_hoods} sub-appellations across {country_name}, grouped by region. "
                f"Want the global view? <a href=\"/regions/\">Browse every region</a>.</p>"
            )
            written_paths.add(_render_scoped_page(renderer, {
                "slug": f"{country_slug}/neighborhoods",
                "title": f"Sub-Appellations of {country_name} | Cork & Curve",
                "meta_description": (f"Every {country_name} sub-appellation we cover on Cork & Curve, "
                                     f"grouped by region. Plan a visit cru by cru.")[:165],
                "h1": f"Sub-appellations of {country_name}",
                "subtitle": "Inside each region, cru by cru.",
                "body": intro + body_hoods,
                "breadcrumb": crumb(("Home", f"{BASE}/"), (country_name, f"{BASE}/{country_slug}/"), ("Sub-appellations", None)),
            }))
            written += 1
        else:
            skipped_empty += 1

    # ---- REGION scope -----------------------------------------------------
    for country_slug, region_slug, region_name in regions:
        # grapes — link DOWN to /<country>/<region>/grape/<slug>/ when present.
        items = _grape_or_style_filtered(grape_manifest, country=country_slug, region=region_slug, unit="producer")
        if items:
            def _region_or_global_grape_href(e, _cs=country_slug, _rs=region_slug):
                rg = CONTENT / _cs / _rs / "grape" / e["slug"] / "index.html"
                return f"/{_cs}/{_rs}/grape/{e['slug']}/" if rg.exists() else f"/grape/{e['slug']}/"
            href = _region_or_global_grape_href
            body = (_intro_region(f"{len(items)} grapes", "grapes", region_name, country_slug)
                    + _render_alpha_grouped(items, href_fn=href)
                    + _itemlist_jsonld(items, f"Grapes in {region_name}", href_fn=href))
            written_paths.add(_render_scoped_page(renderer, {
                "slug": f"{country_slug}/{region_slug}/grapes",
                "title": f"Wine Grapes of {region_name} | Cork & Curve",
                "meta_description": (f"Every grape grown in {region_name} on Cork & Curve, "
                                     f"with the estates that grow each.")[:165],
                "h1": f"Wine grapes of {region_name}",
                "subtitle": f"What {region_name} grows, varietal by varietal.",
                "body": body,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (_country_display(country_slug), f"{BASE}/{country_slug}/"),
                    (region_name, f"{BASE}/{country_slug}/{region_slug}/"),
                    ("Grapes", None),
                ),
            }))
            written += 1
        else:
            skipped_empty += 1

        # styles
        items = _grape_or_style_filtered(style_manifest, country=country_slug, region=region_slug, unit="producer")
        if items:
            href = lambda e: f"/style/{e['slug']}/"
            body = (_intro_region(f"{len(items)} styles", "styles", region_name, country_slug)
                    + _render_alpha_grouped(items, href_fn=href)
                    + _itemlist_jsonld(items, f"Wine styles in {region_name}", href_fn=href))
            written_paths.add(_render_scoped_page(renderer, {
                "slug": f"{country_slug}/{region_slug}/styles",
                "title": f"Wine Styles of {region_name} | Cork & Curve",
                "meta_description": (f"The wine styles made in {region_name} on Cork & Curve, "
                                     f"from sparkling to fortified.")[:165],
                "h1": f"Wine styles of {region_name}",
                "subtitle": f"How {region_name} makes wine, style by style.",
                "body": body,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (_country_display(country_slug), f"{BASE}/{country_slug}/"),
                    (region_name, f"{BASE}/{country_slug}/{region_slug}/"),
                    ("Styles", None),
                ),
            }))
            written += 1
        else:
            skipped_empty += 1

        # sub-appellations
        body_hoods = _neighborhoods_filtered_region(nb_manifest, region_slug)
        if body_hoods:
            n_hoods = sum(1 for e in nb_manifest if e.get("region_slug") == region_slug)
            intro = (
                f"<p>{n_hoods} sub-appellations in our {region_name} guide. "
                f"Click a cru to see every estate, tasting room and wine bar we cover there. "
                f"<a href=\"/{country_slug}/neighborhoods/\">All sub-appellations in this country</a>.</p>"
            )
            written_paths.add(_render_scoped_page(renderer, {
                "slug": f"{country_slug}/{region_slug}/neighborhoods",
                "title": f"Sub-Appellations of {region_name} | Cork & Curve",
                "meta_description": (f"Every {region_name} sub-appellation we cover, with the estates, "
                                     f"tasting rooms and wine bars inside each.")[:165],
                "h1": f"Sub-appellations of {region_name}",
                "subtitle": "Inside the region, cru by cru.",
                "body": intro + body_hoods,
                "breadcrumb": crumb(
                    ("Home", f"{BASE}/"),
                    (_country_display(country_slug), f"{BASE}/{country_slug}/"),
                    (region_name, f"{BASE}/{country_slug}/{region_slug}/"),
                    ("Sub-appellations", None),
                ),
            }))
            written += 1
        else:
            skipped_empty += 1

    # ---- Prune stale scoped pages ----------------------------------------
    pruned = 0
    GLOBAL_SLUGS = ("grapes", "styles", "world", "regions")
    for g in GLOBAL_SLUGS:
        p = CONTENT / g / "index.html"
        if p.exists() and p not in written_paths:
            shutil.rmtree(p.parent)
            pruned += 1
    scoped_subdirs = ("grapes", "styles", "neighborhoods")
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for sub in scoped_subdirs:
            p = country_dir / sub / "index.html"
            if p.exists() and p not in written_paths:
                shutil.rmtree(p.parent)
                pruned += 1
        for region_dir in country_dir.iterdir():
            if not region_dir.is_dir():
                continue
            for sub in scoped_subdirs:
                p = region_dir / sub / "index.html"
                if p.exists() and p not in written_paths:
                    shutil.rmtree(p.parent)
                    pruned += 1

    print(f"wrote {written} scoped cross-cut pages ({skipped_empty} scopes had no data)")
    if pruned:
        print(f"pruned {pruned} stale scoped pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
