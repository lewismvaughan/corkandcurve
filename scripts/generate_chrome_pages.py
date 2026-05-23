#!/usr/bin/env python3
"""
Render the site's chrome / footer / index pages from a single config.

Pages produced (all under content/):
  /about/                  about Cork & Curve
  /about/editorial/        editorial team / author bios
  /editorial-standards/    full editorial policy
  /contact/                contact info
  /cities/                 cities directory
  /cuisines/               cuisines directory
  /dishes/                 dishes directory
  /neighborhoods/          neighborhoods directory
  /topics/                 topics directory (the 20 food topics)
  /privacy/                privacy policy
  /terms/                  terms of use
  /cookies/                cookie policy
  /disclaimer/             disclaimer

Each page is rendered through templates/chrome/page.html, which extends
base.html so all SEO meta, OG/Twitter cards, JSON-LD, footer, and bottom
nav stay consistent across the site.

Usage:
    python3 scripts/generate_chrome_pages.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.template_renderer import TemplateRenderer, WINE_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

# Pagination thresholds for chrome index pages. Below GROUP, render as a
# single flat list. At/above GROUP, alpha-group with anchor jumplinks.
# (No page sharding yet; A-Z anchoring scales comfortably to a few thousand
# entries per category. If any single category passes a few thousand entries,
# revisit with paginated sub-pages /cuisines/page-2/, etc.)
_ALPHA_GROUP_THRESHOLD = 25


def _load_manifest(parent: Path) -> list[dict]:
    """Read the manifest written by generate_cross_cuts.py. Returns [] if
    the manifest is missing (e.g. cross-cuts not generated yet, or empty).

    The manifest is the source of truth for /cuisines/, /dishes/,
    /neighborhoods/. It's tiny (one JSON file per category) and avoids the
    O(N file opens) cost of scraping h1s out of every cross-cut page.
    """
    path = parent / "_manifest.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("entries", [])
    except (OSError, json.JSONDecodeError):
        return []


def _render_alpha_grouped(
    entries: list[dict],
    *,
    href_fn,
) -> str:
    """Render entries as either a flat list (below threshold) or A-Z
    alphabetical groups (at/above threshold). Each group has an id anchor.

    `entries` is a list of dicts with at minimum {"slug", "display"}.
    `href_fn(entry)` returns the URL for one entry.
    """
    if not entries:
        return ""
    if len(entries) < _ALPHA_GROUP_THRESHOLD:
        items = "".join(
            f'<li><a href="{href_fn(e)}"><strong>{e["display"]}</strong></a></li>'
            for e in entries
        )
        return f'<ul class="tj-grid-list">{items}</ul>'

    # Alpha-group. Entries already arrive display-sorted from the manifest.
    groups: dict[str, list[dict]] = {}
    for e in entries:
        # Bucket by first ASCII letter; everything else lands in "#".
        first = (e["display"][:1] or "#").upper()
        if not ("A" <= first <= "Z"):
            first = "#"
        groups.setdefault(first, []).append(e)

    # Jumplinks (only the letters that have content).
    jumps = "".join(
        f'<a href="#alpha-{k}">{k}</a>'
        for k in sorted(groups.keys())
    )

    sections = []
    for letter in sorted(groups.keys()):
        rows = "".join(
            f'<li><a href="{href_fn(e)}"><strong>{e["display"]}</strong></a></li>'
            for e in groups[letter]
        )
        sections.append(
            f'<h2 id="alpha-{letter}">{letter}</h2>'
            f'<ul class="tj-grid-list">{rows}</ul>'
        )
    return (
        f'<nav class="tj-alpha-jumps" aria-label="Jump to letter">{jumps}</nav>'
        + "".join(sections)
    )


def crumb(*items):
    """items: (name, url-or-None). Last has url=None."""
    out = []
    for i, (name, url) in enumerate(items, start=1):
        out.append({"position": i, "name": name, "url": url})
    return out


def _topic_list_html():
    rows = []
    for t in WINE_TOPIC_NAV:
        rows.append(
            f'<li><a href="/topics/{t["slug"]}/"><span class="tj-topic-icon" aria-hidden="true">{t["icon"]}</span> {t["name"]}</a></li>'
        )
    return '<ul class="tj-grid-list">' + "\n".join(rows) + "</ul>"


def _cities_html():
    """List every live city by walking site-data/<country>/<city>/data/.

    Reads each city's region.json (destination.name, destination.country,
    destination.tagline) so the listing is always in sync with what is
    actually shipped. Falls back to the directory slug if region.json is
    missing or malformed. Alpha-groups at >=25 cities."""
    import json as _json

    site_data = REPO_ROOT / "site-data"
    cities: list[dict] = []
    if site_data.exists():
        for country_dir in sorted(site_data.iterdir()):
            if not country_dir.is_dir():
                continue
            country_slug = country_dir.name
            for city_dir in sorted(country_dir.iterdir()):
                if not city_dir.is_dir() or city_dir.name == "data":
                    continue
                region_json = city_dir / "data" / "region.json"
                if not region_json.exists():
                    continue
                try:
                    payload = _json.loads(region_json.read_text(encoding="utf-8"))
                except (OSError, _json.JSONDecodeError):
                    continue
                dest = payload.get("destination", {}) or {}
                # Skip stub cities (e.g. Tokyo placeholder) so the public
                # /cities/ index never lists somewhere that has no real guide.
                meta = payload.get("_metadata", {}) or {}
                if meta.get("status") == "stub" or meta.get("ready_to_publish") is False:
                    # Reveal stubs only if the city hub has already shipped
                    # (i.e. /<country>/<city>/index.html exists in content/).
                    hub = CONTENT / country_slug / city_dir.name / "index.html"
                    if not hub.exists():
                        continue
                cities.append({
                    "slug": city_dir.name,
                    "country_slug": country_slug,
                    "display": dest.get("name", city_dir.name.replace("-", " ").title()),
                    "country": dest.get("country", country_slug.replace("-", " ").title()),
                    "tagline": dest.get("tagline", "").strip(),
                })

    intro = (
        "<p>Every city we cover gets a 20-chapter food guide. Pick one to "
        "start eating. New cities appear here automatically as they ship.</p>"
    )
    if not cities:
        return intro + (
            '<p class="tj-note">No city guides live yet.</p>'
        )

    cities.sort(key=lambda c: c["display"].lower())

    def _row(c):
        sub = f'{c["country"]}. {c["tagline"]}' if c["tagline"] else c["country"]
        return (
            f'<li><a href="/{c["country_slug"]}/{c["slug"]}/">'
            f'<strong>{c["display"]}</strong>'
            f'<span class="tj-list-sub">{sub}</span></a></li>'
        )

    _filter_widget = (
        '<div class="tj-filter-search" style="margin:12px 0 16px;">'
        '<input type="search" autocomplete="off" spellcheck="false" '
        'class="tj-filter-search-input" '
        'placeholder="Filter cities…" '
        'aria-label="Filter cities" '
        'data-filter-target="#tj-cities-list" '
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

    if len(cities) < _ALPHA_GROUP_THRESHOLD:
        body = _filter_widget + '<ul id="tj-cities-list" class="tj-grid-list">' + "".join(_row(c) for c in cities) + "</ul>"
    else:
        groups: dict[str, list[dict]] = {}
        for c in cities:
            first = (c["display"][:1] or "#").upper()
            if not ("A" <= first <= "Z"):
                first = "#"
            groups.setdefault(first, []).append(c)
        jumps = "".join(f'<a href="#alpha-{k}">{k}</a>' for k in sorted(groups.keys()))
        sections = []
        for letter in sorted(groups.keys()):
            rows = "".join(_row(c) for c in groups[letter])
            sections.append(
                f'<h2 id="alpha-{letter}">{letter}</h2>'
                f'<ul class="tj-grid-list">{rows}</ul>'
            )
        body = (
            _filter_widget
            + f'<nav class="tj-alpha-jumps" aria-label="Jump to letter">{jumps}</nav>'
            + f'<div id="tj-cities-list">{"".join(sections)}</div>'
        )

    return intro + body + (
        '<p class="tj-note">More cities are in research. Want a city covered next? '
        '<a href="/contact/">Tell us where you want to eat.</a></p>'
    )


def _cuisines_html():
    """List every /cuisine/<slug>/ cross-cut. Reads the manifest written
    by generate_cross_cuts.py. Alpha-groups at >=25 entries."""
    entries = _load_manifest(CONTENT / "cuisine")
    intro = (
        "<p>Cuisine pages collect every restaurant we cover in a given "
        "cuisine, across every city. Pick one to see the rooms worth the "
        "visit and where each is.</p>"
    )
    if not entries:
        return intro + (
            '<p class="tj-note">No cuisine pages live yet. They get built '
            'automatically from the restaurants in each city guide. '
            '<a href="/cities/">See cities live now</a>.</p>'
        )
    entries.sort(key=lambda e: e["display"].lower())
    return intro + _render_alpha_grouped(
        entries, href_fn=lambda e: f"/cuisine/{e['slug']}/"
    )


def _dishes_html():
    """List every /dish/<slug>/ cross-cut. Reads the manifest, alpha-groups."""
    entries = _load_manifest(CONTENT / "dish")
    intro = (
        "<p>Each signature dish gets a page collecting where to eat the "
        "canonical version, the history, and (where we have it) a recipe "
        "from the Cork & Curve kitchen.</p>"
    )
    if not entries:
        return intro + (
            '<p class="tj-note">No dish pages live yet. They get built '
            'automatically from the signature-dishes chapter of each city '
            'guide. <a href="/cities/">See cities live now</a>.</p>'
        )
    entries.sort(key=lambda e: e["display"].lower())
    return intro + _render_alpha_grouped(
        entries, href_fn=lambda e: f"/dish/{e['slug']}/"
    )


def _neighborhoods_html():
    """List every /neighborhood/<city>/<slug>/ cross-cut. Reads the
    manifest and groups by city. Within each city the neighbourhoods
    sort by display name (with numeric prefixes ordered naturally,
    so "2e" comes before "11e")."""
    entries = _load_manifest(CONTENT / "neighborhood")
    intro = (
        "<p>Neighbourhood pages collect every restaurant, bar, market and "
        "bakery in a single district, across the cities we cover. Plan by "
        "where you are sleeping.</p>"
    )
    if not entries:
        return intro + (
            '<p class="tj-note">No neighbourhood pages live yet. '
            '<a href="/cities/">See cities live now</a>.</p>'
        )

    def _nat_key(e: dict):
        m = re.match(r'^(\d+)', e["slug"])
        return (0, int(m.group(1))) if m else (1, e["display"].lower())

    cities: dict[tuple[str, str], list[dict]] = {}
    for e in entries:
        cities.setdefault((e["city_slug"], e["city_name"]), []).append(e)

    # At scale (hundreds of cities), alpha-group by city name. Below
    # threshold, render city-by-city sections.
    if len(cities) >= _ALPHA_GROUP_THRESHOLD:
        # Treat each city as an entry; the per-city list collapses into
        # one anchor row that points at the first hood under that city.
        # Cleaner alternative: link to a future /neighborhood/<city>/ index.
        # For now we just A-Z group the city sections themselves.
        city_entries = [
            {"slug": s, "display": n, "_hoods": sorted(hoods, key=_nat_key)}
            for (s, n), hoods in cities.items()
        ]
        city_entries.sort(key=lambda x: x["display"].lower())
        # Build alpha-grouped, with each "card" being the city heading plus
        # its hood list.
        groups: dict[str, list[dict]] = {}
        for c in city_entries:
            first = (c["display"][:1] or "#").upper()
            if not ("A" <= first <= "Z"):
                first = "#"
            groups.setdefault(first, []).append(c)
        jumps = "".join(
            f'<a href="#alpha-{k}">{k}</a>' for k in sorted(groups.keys())
        )
        sections = []
        for letter in sorted(groups.keys()):
            for c in groups[letter]:
                items = "".join(
                    f'<li><a href="/neighborhood/{h["city_slug"]}/{h["slug"]}/">'
                    f'<strong>{h["display"]}</strong></a></li>'
                    for h in c["_hoods"]
                )
                sections.append(
                    f'<h2 id="alpha-{letter}">{c["display"]}</h2>'
                    f'<ul class="tj-grid-list">{items}</ul>'
                )
        return intro + (
            f'<nav class="tj-alpha-jumps" aria-label="Jump to letter">{jumps}</nav>'
            + "".join(sections)
        )

    sections = []
    for (city_slug, city_name) in sorted(cities.keys(), key=lambda x: x[1].lower()):
        hoods = sorted(cities[(city_slug, city_name)], key=_nat_key)
        items = "".join(
            f'<li><a href="/neighborhood/{city_slug}/{h["slug"]}/">'
            f'<strong>{h["display"]}</strong></a></li>'
            for h in hoods
        )
        sections.append(
            f'<h2>{city_name}</h2>'
            f'<ul class="tj-grid-list">{items}</ul>'
        )
    return intro + "".join(sections)


def _topics_index_html():
    return (
        "<p>Every region we cover is broken into the same twenty-four wine chapters. "
        "Each topic page below is a cross-region index. Pick a topic to see "
        "every region we have written about it.</p>"
        + _topic_list_html()
    )


def _about_html():
    return """
<p>Cork & Curve is a wine travel publication. We write the wine chapter of
a guidebook the way a guidebook used to be written: with a point of view,
on the ground, by editors who care which cellar you walk into.</p>

<p>We do not aggregate. We do not score estates on a borrowed five-star wheel.
We do not promise the &quot;top 10 of everything&quot;. Each region we cover is
researched, tasted, and written by one editorial voice with help from
the growers, winemakers and sommeliers living in it.</p>

<h2>What you will find here</h2>
<ul>
  <li>Region guides organised into twenty-four consistent wine chapters,
    from vineyards to tasting rooms to wine festivals.</li>
  <li>Signature-wine writing that tells you what the bottle is, who makes it,
    and what it actually means in that region.</li>
  <li>Sub-appellation breakdowns so you can plan by the cru you are
    visiting, not by a single mega-list.</li>
  <li>No sponsored placements in the editorial. See <a
    href="/about/editorial/">our standards</a>.</li>
</ul>

<h2>Who is behind it</h2>
<p>Cork & Curve is published by a small editorial desk based in the United
Kingdom. The wine research that powers each region guide is done by editorial
staff and on-the-ground correspondents, working from a shared 24-chapter
brief so every region reads with the same depth.</p>

<h2>How to use the site</h2>
<p>Start with the <a href="/regions/">regions index</a>, or jump straight to a
region you are travelling to. Inside each region, the chapters work as
stand-alone pieces. you can read just the Vineyards chapter, or just
the Tasting Rooms chapter, without needing the rest.</p>

<h2>Get in touch</h2>
<p>Press, partnerships, corrections, or just want to tell us where you tasted?
The <a href="/contact/">contact page</a> is the way.</p>
"""


def _about_editorial_html():
    return """
<p>Cork & Curve is written and edited by a small team working from a
shared 23-chapter brief. Every city guide is overseen by the editorial
desk before publication.</p>

<h2>The desk</h2>
<p><strong>Cork & Curve Editorial</strong> is the byline you will see on
city guides, signature-dish writeups and topic pages. It is a working
desk, not a pseudonym: every piece has an editor of record on file.
Corrections, story tips and inquiries go to that desk.</p>

<h2>Correspondents</h2>
<p>Each city we cover has at least one on-the-ground correspondent. They
eat. They drink. They walk the streets. They write the first draft. The
desk fact-checks, edits and signs off.</p>

<h2>Standards</h2>
<p>The full editorial standards. how we decide what to cover, how we
handle gifts and comped meals, how we handle errors. live on the <a
href="/editorial-standards/">editorial standards page</a>.</p>

<h2>Contact</h2>
<p>Corrections, story tips and partnership inquiries should go through
the <a href="/contact/">contact page</a>. We read everything.</p>
"""


def _editorial_standards_html():
    return """
<p>Cork & Curve exists to help readers eat well. We treat that as a
responsibility, not a tagline. These are the rules we apply to every
piece we publish.</p>

<h2>1. No paid placements in editorial</h2>
<p>No restaurant, bar, market, hotel, or tour operator can pay to be
included, ranked, or featured in our editorial. There is no PR-pitched
inclusion. There is no &quot;affiliate priority&quot; ranking.</p>

<h2>2. Comped meals and press visits</h2>
<p>Editors and correspondents may, at their own discretion, accept comped
meals or press visits in the course of research. If they do, the piece
discloses it in the byline area or in a note at the bottom. A comp does
not buy a positive verdict. A comped meal that disappointed gets written
up that way.</p>

<h2>3. Affiliate links</h2>
<p>We may include affiliate links to booking partners (for example, hotel
or tour operator partners). Affiliate revenue plays no part in editorial
selection. If a partner property is bad, it gets that verdict and the
affiliate link goes away.</p>

<h2>4. Sourcing</h2>
<p>Every restaurant, bar, market and dish we recommend has been visited
by either the named editor of record or a named correspondent. We do not
aggregate from other publications.</p>

<h2>5. Updates and corrections</h2>
<p>Every chapter shows an &quot;Updated&quot; stamp at the top. If a place
closes, changes hands, drops in quality, or otherwise warrants a new
verdict, we update the page and stamp it. Material corrections are
called out at the bottom of the affected page.</p>

<h2>6. AI assistance</h2>
<p>We use AI tools to help with research synthesis, copy edits, and
structural drafting. We do not publish AI-generated content as
editorial. Every claim of fact on this site has a named human editor
who has verified it.</p>

<h2>7. Conflicts of interest</h2>
<p>Editors disclose to the desk any personal relationship with a
restaurateur, chef, or operator they are writing about. Where the
relationship is material, the piece is reassigned.</p>

<h2>8. Scoring methodology</h2>
<p>Every restaurant, bar, market, dish, itinerary and other entry on
Cork & Curve carries an editorial score between 1.0 and 5.0, shown as
&quot;★ 4.3&quot; next to the entry name. The score is the Cork & Curve
editorial verdict, derived from many inputs:</p>
<ul>
  <li><strong>External reputation</strong>. published reviews,
    independent press, food-critic writeups, the Michelin Guide and Le
    Fooding where relevant, and the patterns visible across diner
    reviews (volume and recency, not just star averages).</li>
  <li><strong>Recency</strong>. a place strong in 2022 but slipping
    today scores lower than its legacy reputation would suggest. We
    weight sources from the last eighteen months.</li>
  <li><strong>On-the-ground reporting</strong>. first-hand visits and
    local correspondent notes outrank aggregated star averages.</li>
  <li><strong>Editorial judgment</strong>. distinctiveness, canonical
    execution of a category, and how essential the place is to its
    city's food scene.</li>
</ul>
<p>We do not cache or display source ratings (Google, Yelp,
TripAdvisor, etc.). The number you see is ours. A place scoring 5.0 is
defining, essential, and would change the city's food story if it
vanished. 4.5 to 4.9 is excellent. 4.0 to 4.4 is a strong recommend.
3.5 to 3.9 is a solid pick for the category. Below 3.0 places are rare,
included only when category coverage requires breadth.</p>

<h2>Reporting an issue</h2>
<p>If you spot a factual error, a closed business, or anything that
needs a correction, the <a href="/contact/">contact page</a> is the
fastest way to reach the editorial desk.</p>
"""


def _contact_html():
    return """
<p>Editorial corrections, story tips, partnership inquiries, press,
syndication, and just wanting to tell us where you ate. all welcome.</p>

<h2>Email</h2>
<p><a href="mailto:hello@corkandcurve.com">hello@corkandcurve.com</a>
for general inquiries.</p>

<h2>Editorial corrections</h2>
<p>Spotted a factual error, a closed business, or something that needs an
update? Email <a href="mailto:editorial@corkandcurve.com">editorial@corkandcurve.com</a>
with the URL and what needs fixing. We read every correction and respond
to those that need a reply.</p>

<h2>Press and partnerships</h2>
<p>Tour operators, hotels, tourism boards and other partners can reach
the partnerships desk at <a href="mailto:partnerships@corkandcurve.com">partnerships@corkandcurve.com</a>.
Read the <a href="/editorial-standards/">editorial standards</a> first.
The short version: editorial decisions are not for sale.</p>

<h2>Where we are</h2>
<p>Cork & Curve is published from the United Kingdom. The editorial team
works remotely with correspondents in each of the cities we cover.</p>
"""


def _privacy_html():
    return """
<p>This privacy notice describes what data Cork & Curve collects when you
visit this site, why we collect it, and what we do with it. We try to
collect as little as possible and to be honest about what we do collect.</p>

<h2>What we collect</h2>
<ul>
  <li><strong>Server logs</strong>. our web server records standard request
    metadata. IP address, user-agent string, the URL requested, and the
    timestamp. This is used for security, debugging, and aggregate traffic
    counts.</li>
  <li><strong>Analytics</strong>. we may use a privacy-respecting analytics
    tool to count page views in aggregate. If we use one that sets cookies,
    those are disclosed in the <a href="/cookies/">cookies policy</a>.</li>
  <li><strong>Email you send us</strong>. if you email us, we keep the email
    so we can reply and follow up.</li>
</ul>

<h2>What we do not do</h2>
<ul>
  <li>We do not sell your data to anyone.</li>
  <li>We do not build a profile of you across other sites.</li>
  <li>We do not require sign-up to read anything.</li>
</ul>

<h2>Third-party content</h2>
<p>Some pages include embedded content from third parties (for example,
map providers or images served by other hosts). Those providers may set
their own cookies and follow their own privacy policies. We do not control
them.</p>

<h2>Advertising</h2>
<p>If we run advertising on the site, the advertising provider may set
cookies or use device identifiers. The kinds of cookies set are listed
on the <a href="/cookies/">cookies policy</a>.</p>

<h2>Your rights</h2>
<p>You have the right to know what we hold about you, to ask for a copy,
and to ask us to delete it. Email <a href="mailto:privacy@corkandcurve.com">privacy@corkandcurve.com</a>
and we will respond within a reasonable time.</p>

<h2>Updates</h2>
<p>If this notice changes materially, we will update it and stamp the new
&quot;Updated&quot; date at the top.</p>
"""


def _terms_html():
    return """
<p>By using corkandcurve.com you agree to these terms. If you do not
agree with any of them, do not use the site.</p>

<h2>What you can do</h2>
<p>You can read the site, link to it from anywhere, and quote short
passages with attribution and a link back. Personal, non-commercial use
of the content is welcome.</p>

<h2>What you cannot do</h2>
<ul>
  <li>Republish, rehost, or redistribute substantial portions of our
    editorial without prior written permission.</li>
  <li>Use the content to train models that compete with us. AI training
    on this site requires a separate licence.</li>
  <li>Scrape the site at a rate that imposes load. We block crawlers that
    misbehave.</li>
</ul>

<h2>Accuracy</h2>
<p>We work hard to keep the site accurate. Restaurants close, prices
change, chefs leave. We update pages when we know, but we make no
guarantee that any specific detail is current at the time you read it.
Confirm anything important before you travel. See the <a
href="/disclaimer/">full disclaimer</a>.</p>

<h2>Third-party links</h2>
<p>We link to third-party sites for booking, reading, and reference.
We do not control those sites and are not responsible for their content
or their privacy practices.</p>

<h2>Affiliate disclosure</h2>
<p>Some outbound links are affiliate links, meaning we may earn a
commission if you book through them. This never affects editorial
selection. See <a href="/editorial-standards/">editorial standards</a>.</p>

<h2>Changes</h2>
<p>We may update these terms. The &quot;Updated&quot; stamp at the top
shows when they last changed.</p>

<h2>Governing law</h2>
<p>These terms are governed by the laws of England and Wales.</p>
"""


def _cookies_html():
    return """
<p>This page lists the cookies and similar technologies corkandcurve.com
may set when you visit. We aim to keep it short.</p>

<h2>Strictly necessary</h2>
<p>None at present. The static site itself does not require any cookies
to function.</p>

<h2>Preferences</h2>
<ul>
  <li><strong>tj-theme</strong>. remembers your light or dark theme
    choice. Stored in your browser only. Not sent to us.</li>
</ul>

<h2>Analytics</h2>
<p>If we enable analytics, we will list any cookies it sets here, with
purpose and lifetime. We aim to choose a privacy-respecting tool that
does not set tracking cookies. The current setup does not load
analytics.</p>

<h2>Advertising</h2>
<p>If we serve advertising on the site, ad partners may set cookies for
frequency capping, fraud prevention, and interest-based ads. Those
cookies are governed by the partner's own policy. We will list the
partners here once advertising is enabled.</p>

<h2>How to control cookies</h2>
<p>You can clear cookies, block them, or set your browser to ask before
accepting them. Doing so will not break the editorial part of the site.</p>
"""


def _disclaimer_html():
    return """
<p>Cork & Curve publishes editorial recommendations for food, drink, and
travel. We do our best to be accurate, but we are not infallible and the
world keeps moving. Before you act on anything here, please confirm.</p>

<h2>Restaurants, bars, markets</h2>
<p>Opening hours, menus, prices, chefs, and even addresses change. A room
we praised six months ago may have changed hands, moved, or closed. Call
ahead. Book where booking is sensible.</p>

<h2>Allergens, dietary requirements, and health</h2>
<p>Our coverage of vegan, vegetarian, gluten-free, halal, kosher, nut-free
and other dietary categories is editorial guidance, not a clinical
substitute. If you have a serious allergy or medical condition,
double-check directly with the kitchen.</p>

<h2>Travel advice</h2>
<p>We are a food publication, not a safety or visa advisor. For travel
advisories, vaccinations, visas, and the like, consult your government's
travel advice and a qualified professional.</p>

<h2>Affiliate disclosure</h2>
<p>Some links on this site are affiliate links. If you book through them,
we may earn a commission at no extra cost to you. This does not influence
our editorial choices. See <a href="/editorial-standards/">editorial
standards</a> for the full policy.</p>

<h2>Liability</h2>
<p>To the maximum extent permitted by law, Cork & Curve is not liable for
losses arising from your reliance on the editorial content.</p>
"""


PAGES = [
    {
        "slug": "about",
        "title": "About Cork & Curve. Where the world drinks",
        "meta_description": "Wine travel guides written by editors on the ground. Twenty-four consistent wine chapters per region, signature-wine writing and sub-appellation maps. No paid placements.",
        "h1": "About Cork & Curve",
        "subtitle": "A wine travel publication, edited by humans, tasted in person.",
        "page_type": "about",
        "body": _about_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("About", None)),
    },
    {
        "slug": "about/editorial",
        "title": "The Cork & Curve editorial team",
        "meta_description": "Meet the editors and correspondents behind Cork & Curve. Who writes each city guide, who edits, who signs off, and how every published piece gets attributed.",
        "h1": "Editorial team",
        "subtitle": "Real bylines. Real editors. Real meals.",
        "page_type": "about",
        "body": _about_editorial_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("About", f"{BASE}/about/"), ("Editorial team", None)),
    },
    {
        "slug": "editorial-standards",
        "title": "Editorial standards. how Cork & Curve works",
        "meta_description": "Our editorial standards in full. No paid placements, comped meals disclosed, affiliate links never influence selection, every claim has a named editor of record.",
        "h1": "Editorial standards",
        "subtitle": "How we decide what to cover, and how we keep it honest.",
        "page_type": "webpage",
        "body": _editorial_standards_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Editorial standards", None)),
    },
    {
        "slug": "contact",
        "title": "Contact Cork & Curve. corrections, tips, partnerships",
        "meta_description": "How to reach the Cork & Curve editorial team. Send a correction, a story tip, a press inquiry, a partnership request, or a recommendation. We read everything.",
        "h1": "Contact us",
        "subtitle": "Email is the fastest way to reach the desk.",
        "page_type": "contact",
        "body": _contact_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Contact", None)),
    },
    {
        "slug": "topics",
        "title": "Wine topics. vineyards to tasting rooms, indexed",
        "meta_description": "Browse Cork & Curve by wine topic. Vineyards, tasting rooms, wine bars, wine tours, festivals, signature wines and the rest, indexed across every region.",
        "h1": "Topics",
        "subtitle": "The twenty-four wine chapters, indexed across every region.",
        "page_type": "collection",
        "body": _topics_index_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Topics", None)),
    },
    {
        "slug": "privacy",
        "title": "Privacy. what we collect and what we do not",
        "meta_description": "Cork & Curve's privacy notice. What data we collect, why, what we never do (sell your data, profile you across sites), and how to ask for a copy or a deletion.",
        "h1": "Privacy",
        "subtitle": "We try to collect as little as possible. This is what and why.",
        "page_type": "privacy",
        "body": _privacy_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Privacy", None)),
    },
    {
        "slug": "terms",
        "title": "Terms of use. the rules for reading Cork & Curve",
        "meta_description": "The rules for using corkandcurve.com. What you may do with our content, what you may not, how affiliate links work, editorial scope, and which law governs.",
        "h1": "Terms of use",
        "subtitle": "The short, plain-English version of the rules.",
        "page_type": "terms",
        "body": _terms_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Terms", None)),
    },
    {
        "slug": "cookies",
        "title": "Cookies. what Cork & Curve stores in your browser",
        "meta_description": "What cookies and storage Cork & Curve uses. The static site does not need cookies to work. Theme, analytics, and advertising are listed in plain language.",
        "h1": "Cookies",
        "subtitle": "Short list. We try to keep it that way.",
        "page_type": "privacy",
        "body": _cookies_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Cookies", None)),
    },
    {
        "slug": "disclaimer",
        "title": "Disclaimer. confirm before you act on it",
        "meta_description": "Cork & Curve is editorial guidance, not a guarantee. Restaurants change, dietary categories need verification, travel advice is not our remit. Full disclaimer here.",
        "h1": "Disclaimer",
        "subtitle": "We do our best. Then call ahead.",
        "page_type": "webpage",
        "body": _disclaimer_html(),
        "breadcrumb": crumb(("Home", f"{BASE}/"), ("Disclaimer", None)),
    },
]


def render_one(renderer, spec):
    canonical = f"{BASE}/{spec['slug']}/"
    page_ctx = {
        "title": spec["title"],
        "meta_description": spec["meta_description"],
        "h1": spec["h1"],
        "subtitle": spec.get("subtitle", ""),
        "canonical_url": canonical,
        "body_html": spec["body"],
        "breadcrumb_items": spec["breadcrumb"],
        "page_type": spec["page_type"],
        "updated": "May 2026",
        "modified": "2026-05-17",
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
            "og_image": "https://corkandcurve.com/og/default.jpg",
            "og_image_alt": "Cork & Curve food guide",
            "og_locale": "en_US",
        },
        "twitter": {
            "twitter_title": spec["title"],
            "twitter_description": spec["meta_description"],
        },
        "structured_data": {
            "breadcrumb_items": spec["breadcrumb"],
        },
        "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    html = template.render(
        page=page_ctx,
        seo=seo,
        analytics={"page_type": "chrome", "destination": "global"},
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
    renderer = TemplateRenderer()
    for spec in PAGES:
        out = render_one(renderer, spec)
        print(f"wrote {out}")
    print(f"Rendered {len(PAGES)} chrome pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
