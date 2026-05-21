#!/usr/bin/env python3
"""
Generate the remaining site infrastructure pages:

  /topics/<topic>/        cross-city index for each of 20 food topics
  /search/                client-side search powered by /search/search-index.json
  /404.html               friendly 404 page
  /feed.xml               minimal RSS feed pointing at city/topic pages
  /og/default.jpg         1200x630 social-card image (PIL)

All page chrome (header, footer, breadcrumbs, JSON-LD) is rendered through
templates/chrome/page.html so it stays consistent with about/contact/etc.
"""

from __future__ import annotations

import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.template_renderer import TemplateRenderer, FOOD_TOPIC_NAV  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://tablejourney.com"


COUNTRY_NAMES = {
    "france": "France",
    "italy": "Italy",
    "japan": "Japan",
    "spain": "Spain",
    "united-kingdom": "United Kingdom",
    "united-states": "United States",
    "germany": "Germany",
}


def _country_display(slug: str) -> str:
    return COUNTRY_NAMES.get(slug, slug.replace("-", " ").title())


TOPIC_META = {
    "restaurants":      ("Best restaurants in every TableJourney city",
                         "Restaurants worth a reservation, indexed across every TableJourney city. Neighbourhood bistros, new classics and the chefs running them, with editor picks."),
    "fine-dining":      ("Fine dining around the world",
                         "Tasting menus, starred rooms and the kitchens redefining cooking across every TableJourney city, with editorial picks, what to order and how to book."),
    "casual-dining":    ("Casual dining: where locals actually eat",
                         "Bistros, trattorias, izakayas and neighbourhood tables across every TableJourney city: the everyday rooms that show you how a place eats when nobody is performing."),
    "cafes":            ("Best cafes around the world",
                         "Coffee, pastries and slow-morning rooms across every TableJourney city: where to sit, where to sip and where to come back, picked by our city editors."),
    "bakeries":         ("Best bakeries around the world",
                         "Bread, pastry and morning counters across every TableJourney city. Levain loaves, laminated pastry, regional bakes and the doors worth crossing town for."),
    "coffee-roasters":  ("Best coffee roasters around the world",
                         "The roasters writing each city's coffee scene on TableJourney: where they source from, where to drink their coffee and which ones keep a public cafe."),
    "wine-bars":        ("Best wine bars around the world",
                         "Where to drink wine by the glass and the bottle across every TableJourney city: natural-wine rooms, classical caves and grower-focused lists worth the trip."),
    "bars":             ("Best bars around the world",
                         "Cocktails, wine bars and the dives worth the cab fare across every TableJourney city, with editor picks, neighbourhoods and how to grab a stool on the night."),
    "street-food":      ("Street food, by city",
                         "The fastest, cheapest and often best food on the planet's streets, by city: vendor names, addresses, opening hours and what to actually order on TableJourney."),
    "breweries":        ("Breweries and taprooms, by city",
                         "Where each city drinks local: brewpubs, taprooms and new-wave producers worth a tram ride, indexed across every TableJourney city with editor picks and notes."),
    "markets":          ("Food markets around the world",
                         "Where each city shops, snacks and lunches: the food markets worth your morning, with stall-by-stall direction from TableJourney editors across every city we cover."),
    "food-tours":       ("Food tours worth booking",
                         "Guided food tours we'd actually book across every TableJourney city: operators, neighbourhoods, prices, what the tour delivers and what it quietly misses."),
    "festivals":        ("Food festivals around the world",
                         "Food festival calendar by city: month-by-month events worth planning a trip around, from harvest weekends to street feasts, with editor picks across TableJourney."),
    "cooking-classes":  ("Cooking classes you'd take twice",
                         "Hands-on cooking classes across every TableJourney city: the schools that teach a dish you will actually cook again at home, with editor notes on price and pace."),
    "dietary":          ("Vegan, vegetarian, gluten-free, halal and kosher guides",
                         "How to eat well in each TableJourney city with dietary needs: vegan, vegetarian, gluten-free, halal and kosher rooms worth the trip, by city, with editor picks."),
    "budget-eating":    ("Eating well, cheap, in every city",
                         "Locals'-budget editions for every TableJourney city: cheap eats that taste expensive, the prix-fixe rooms worth knowing, prices and the queue rules."),
    "signature-dishes": ("Signature dishes of the eating cities of the world",
                         "The plates that define a place, what they actually are and where to eat the canonical version, indexed across every TableJourney city with editor picks."),
    "hidden-gems":      ("Hidden food gems, by city",
                         "The places the guidebooks miss, recommended by editors who eat in the city week in, week out, indexed across every TableJourney city with addresses and tips."),
    "brunch":           ("Best brunch around the world",
                         "Morning rooms worth the queue, mid-morning institutions, lazy Sunday rituals: the brunch picks for every TableJourney city, with addresses and what to order."),
    "late-night":       ("Late-night food around the world",
                         "Where to eat after midnight across every TableJourney city: the classic 2 a.m. moves, the all-night counters and the night-bus rituals, with editor picks."),
    "food-history":     ("Food history, city by city",
                         "How each city came to eat the way it does: the migrations, money and accidents that wrote the plate, told as story not lecture, on TableJourney by editors."),
    "seasonal-food":    ("What's in season, by city",
                         "What is in season in each TableJourney city and what to order when the market changes: a rolling calendar by destination, with the dishes that follow the produce."),
    "day-trips-food":   ("Food day trips from every TableJourney city",
                         "Food destinations within an hour or two of each TableJourney city: trips worth the early start, with the train, the car key or the tram fare in hand."),
    "itineraries":      ("Eating itineraries, by city",
                         "Day-by-day eating plans for each TableJourney city, by audience: weekend classics, family two-day plans, vegan three-day routes, morning to dinner."),
}


def discover_cities() -> list[dict]:
    """Walk site-data/ and return [{country_slug, city_slug, name}] for cities that have data."""
    out = []
    if not SITE_DATA.exists():
        return out
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir():
                continue
            data_dir = city_dir / "data"
            if not (data_dir / "region.json").exists():
                continue
            region = {}
            try:
                region = json.loads((data_dir / "region.json").read_text("utf-8"))
            except Exception:
                pass
            name = (
                region.get("destination", {}).get("name")
                or region.get("name")
                or city_dir.name.title()
            )
            tagline = (region.get("destination", {}) or {}).get("tagline", "")
            out.append({
                "country_slug": country_dir.name,
                "city_slug": city_dir.name,
                "name": name,
                "tagline": tagline,
            })
    return out


def crumb(*items):
    return [{"position": i, "name": name, "url": url} for i, (name, url) in enumerate(items, start=1)]


# Reusable client-side filter widget for "list-everything" index pages.
# Returns an <input> + tiny inline <script> that filters child items of the
# given selector by text match. Defensive: no-op when the selector matches
# zero items. Used by generate_extras (topic landings), generate_scoped_cross_cuts
# (country/city cuisine + dish + neighborhoods indexes), and any other generator
# that ships a long list of links the reader needs to scan.
def filter_search_widget(*, target_selector: str, item_selector: str,
                          placeholder: str = "Filter…",
                          aria_label: str = "Filter list") -> str:
    """Render a search input + script. `target_selector` is the container,
    `item_selector` is the children to filter (relative to target). The script
    is idempotent: re-running it on an already-wired input is a no-op."""
    import json as _json
    return (
        '<div class="tj-filter-search" style="margin:12px 0 16px;">'
        f'<input type="search" autocomplete="off" spellcheck="false" '
        f'class="tj-filter-search-input" '
        f'placeholder="{html.escape(placeholder)}" '
        f'aria-label="{html.escape(aria_label)}" '
        f'data-filter-target="{html.escape(target_selector)}" '
        f'data-filter-item="{html.escape(item_selector)}" '
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


def render_chrome(renderer, *, slug, title, meta_description, h1, subtitle, body_html, breadcrumb, page_type="collection", canonical_override=None, robots_override=None):
    canonical = canonical_override or f"{BASE}/{slug}/"
    page_ctx = {
        "title": title,
        "meta_description": meta_description,
        "h1": h1,
        "subtitle": subtitle,
        "canonical_url": canonical,
        "body_html": body_html,
        "breadcrumb_items": breadcrumb,
        "page_type": page_type,
        "updated": "May 2026",
        "modified": "2026-05-17",
    }
    seo = {
        "meta": {
            "title": title,
            "description": meta_description,
            "canonical_url": canonical,
            "robots": robots_override or "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        },
        "open_graph": {
            "og_title": title,
            "og_description": meta_description,
            "og_url": canonical,
            "og_type": "website",
            "og_image": f"{BASE}/og/default.jpg",
            "og_image_alt": "TableJourney food guide",
            "og_locale": "en_US",
        },
        "twitter": {
            "twitter_title": title,
            "twitter_description": meta_description,
            "twitter_image": f"{BASE}/og/default.jpg",
            "twitter_image_alt": "TableJourney food guide",
        },
        "structured_data": {"breadcrumb_items": breadcrumb},
        "alternates": [],
    }
    tpl = renderer.env.get_template("chrome/page.html")
    return tpl.render(
        page=page_ctx,
        seo=seo,
        analytics={"page_type": "chrome", "destination": "global"},
        base_path="",
        topic_nav=FOOD_TOPIC_NAV,
        breadcrumb=breadcrumb,
        current_year=2026,
    )


def write(out: Path, html_str: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_str, encoding="utf-8")
    print(f"wrote {out}")


# ──────────────────────────────────────────────────────────────────────
# /topics/<topic>/ cross-city pages
# ──────────────────────────────────────────────────────────────────────

# Topics that get the filterable card grid. Each topic's JSON shape differs,
# so _TOPIC_FIELD_ADAPTERS maps topic slug -> {category_field, price_field,
# category_label_prefix}. The aggregator pulls per-topic fields and the card
# renderer falls back gracefully when a field is empty.
_ENTITY_LIST_TOPICS = {
    "restaurants", "fine-dining", "casual-dining", "cafes", "bakeries",
    "coffee-roasters", "wine-bars", "bars", "street-food", "breweries",
    "markets", "food-tours", "festivals", "cooking-classes",
    "budget-eating", "hidden-gems", "brunch", "late-night",
}

# Per-topic schema adapter. Each entry specifies which JSON field becomes the
# card's "category" line (cuisine/type/style) and the "price" line, if any.
# Topics without natural cuisine/price fields just omit them (the card still
# renders, with name + description as the editorial substance).
_TOPIC_FIELD_ADAPTERS = {
    "restaurants":     {"category": "cuisine",        "price": "price_tier",        "category_label": "Cuisine", "price_label": "Price"},
    "fine-dining":     {"category": "chef",           "price": "tasting_menu_price","category_label": "Chef",    "price_label": "Tasting", "category_prefix": "Chef "},
    "casual-dining":   {"category": "cuisine",        "price": "price_tier",        "category_label": "Cuisine", "price_label": "Price"},
    "cafes":           {"category": "signature_drink","price": None,                "category_label": "Drink"},
    "bakeries":        {"category": "specialty",      "price": None,                "category_label": "Specialty"},
    "coffee-roasters": {"category": "beans_from",     "price": None,                "category_label": "Beans",   "category_prefix": "Beans: "},
    "wine-bars":       {"category": "wine_focus",     "price": None,                "category_label": "Focus"},
    "bars":            {"category": "type",           "price": None,                "category_label": "Type"},
    "street-food":     {"category": "dish",           "price": "price",             "category_label": "Dish",    "price_label": "Price"},
    "breweries":       {"category": "style",          "price": None,                "category_label": "Style"},
    "markets":         {"category": "best_for",       "price": None,                "category_label": "Best for"},
    "food-tours":      {"category": "route",          "price": "price",             "category_label": "Route",   "price_label": "Price", "name_field": "operator"},
    "festivals":       {"category": "focus_cuisine",  "price": "month",             "category_label": "Cuisine", "price_label": "Month"},
    "cooking-classes": {"category": "cuisine_taught", "price": "price",             "category_label": "Cuisine", "price_label": "Price"},
    "budget-eating":   {"category": "dish",           "price": "price",             "category_label": "Dish",    "price_label": "Price"},
    "hidden-gems":     {"category": None,             "price": None},
    "brunch":          {"category": "style",          "price": "price_range",       "category_label": "Style",   "price_label": "Price"},
    "late-night":      {"category": "dish",           "price": None,                "category_label": "Dish"},
}


def _topic_list_key(slug: str) -> str:
    # Default: hyphen-slug to underscored JSON key (e.g. wine-bars -> wine_bars).
    return slug.replace("-", "_")


def _aggregate_topic_entities(slug: str, cities: list[dict]) -> list[dict]:
    """Walk every city's <slug>.json and return a flat list of entities,
    each decorated with city_slug, city_name, country_slug. Skip cities
    that don't publish this topic, malformed JSON, or empty lists."""
    list_key = _topic_list_key(slug)
    adapter = _TOPIC_FIELD_ADAPTERS.get(slug, {})
    name_field = adapter.get("name_field", "name")
    category_field = adapter.get("category")
    price_field = adapter.get("price")
    aggregated: list[dict] = []
    for c in cities:
        # Only include cities whose topic page has actually shipped (file in content/),
        # so the topic grid never links to a 404.
        if not (CONTENT / c["country_slug"] / c["city_slug"] / slug / "index.html").exists():
            continue
        src = SITE_DATA / c["country_slug"] / c["city_slug"] / "data" / f"{slug}.json"
        if not src.exists():
            continue
        try:
            payload = json.loads(src.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entries = payload.get(list_key) if isinstance(payload, dict) else payload
        if not isinstance(entries, list):
            continue
        for e in entries:
            if not isinstance(e, dict):
                continue
            entry_slug = e.get("slug")
            cat_val = e.get(category_field, "") if category_field else ""
            price_val = e.get(price_field, "") if price_field else ""
            # Apply prefixes/labels
            if cat_val and adapter.get("category_prefix"):
                cat_val = adapter["category_prefix"] + str(cat_val)
            decorated = {
                "name": e.get(name_field, "") or e.get("name", ""),
                "cuisine": str(cat_val),  # generic category slot, named "cuisine" for back-compat
                "price_tier": str(price_val) if price_val else "",
                "neighborhood": e.get("neighborhood", ""),
                "editorial_score": e.get("editorial_score"),
                "description": e.get("description", "") or e.get("why_hidden", ""),
                "booking_url": e.get("booking_url", "") or e.get("affiliate_url", ""),
                "city_name": c["name"],
                "city_slug": c["city_slug"],
                "country_slug": c["country_slug"],
                "country_name": _country_display(c["country_slug"]),
                "entity_url": (
                    f"/{c['country_slug']}/{c['city_slug']}/{slug}/{entry_slug}/"
                    if entry_slug else
                    f"/{c['country_slug']}/{c['city_slug']}/{slug}/"
                ),
            }
            aggregated.append(decorated)
    return aggregated


def _cuisine_class(cuisine: str) -> str:
    """Bucket the entity's free-form `cuisine` string into ~25 canonical
    classes for the filter chip UI. The full string still renders on the
    entity card subtitle; this is for filter-chip readability only.

    Lewis 2026-05-19: "these filters need a way better user design, there
    are way too many" — 616 unique cuisine strings across all cities,
    most micro-variants of a primary class. Order of rules matters
    (most specific first); first match wins.
    """
    if not cuisine:
        return "Other"
    c = cuisine.lower()

    def has(*keys: str) -> bool:
        return any(k in c for k in keys)

    # Most-specific markers first.
    if has("izakaya"):                                     return "Japanese"
    if has("ramen"):                                       return "Japanese"
    if has("sushi", "omakase", "edomae", "kaiseki"):       return "Japanese"
    if has("japanese", "yakitori", "robata"):              return "Japanese"
    if has("dim sum"):                                     return "Chinese"
    if has("cantonese", "szechuan", "sichuan", "shanghai"): return "Chinese"
    if has("chinese", "taiwanese"):                        return "Chinese"
    if has("korean"):                                      return "Korean"
    if has("vietnamese", "pho", "banh mi"):                return "Vietnamese"
    if has("thai"):                                        return "Thai"
    if has("indian", "tandoori", "bombay", "punjabi"):     return "Indian"
    if has("malaysian", "indonesian", "burmese", "cambodian", "filipino", "hmong"):
        return "SE Asian"
    if has("italian-american"):                            return "Italian-American"
    if has("pizza", "pizzeria", "neapolitan pizza"):       return "Pizza"
    if has("italian", "trattoria", "osteria", "salumeria", "florentine", "bolognese",
           "roman", "tuscan", "sicilian", "neapolitan", "milanese", "lombard",
           "venetian", "piedmont", "ligurian", "emilian"):
        return "Italian"
    if has("french bistro", "neo-bistro", "bouillon", "brasserie"):
        return "French"
    if has("french"):                                      return "French"
    if has("spanish tapas", "tapas"):                      return "Tapas"
    if has("basque", "catalan", "andalucian", "asturian", "castilian", "galician",
           "valencian", "madrileno", "spanish"):
        return "Spanish"
    if has("paella"):                                      return "Spanish"
    if has("mexican", "taqueria", "taco", "tex-mex", "tex mex"):
        return "Mexican"
    if has("peruvian", "cuban", "argentine", "venezuelan", "salvadoran", "caribbean",
           "colombian", "brazilian", "puerto rican"):
        return "Latin American"
    if has("turkish", "lebanese", "syrian", "israeli", "persian", "iranian",
           "egyptian", "moroccan", "levantine", "middle eastern", "kebab",
           "falafel", "hummus"):
        return "Middle Eastern"
    if has("greek"):                                       return "Greek"
    if has("ethiopian", "eritrean", "senegalese", "nigerian", "kenyan", "south african"):
        return "African"
    if has("steakhouse", "asador", "parrilla"):            return "Steakhouse"
    if has("barbecue", "bbq", "smokehouse"):               return "BBQ"
    if has("seafood", "oysters", "fish and chips", "shellfish", "crab", "lobster"):
        return "Seafood"
    if has("burger"):                                      return "Burgers"
    if has("diner"):                                       return "Diner"
    if has("soul food", "lowcountry", "creole", "cajun", "southern"):
        return "Southern"
    if has("food hall"):                                   return "Food Hall"
    if has("gastropub", "tavern", "pub"):                  return "Pub & Gastropub"
    if has("german", "austrian", "bavarian"):              return "German"
    if has("scottish", "british", "english", "irish", "welsh", "modern british"):
        return "British"
    if has("scandinavian", "swedish", "danish", "norwegian", "nordic", "finnish"):
        return "Nordic"
    if has("mediterranean"):                               return "Mediterranean"
    if has("modern european", "european"):                 return "Modern European"
    if has("vegan"):                                       return "Vegan"
    if has("vegetarian", "plant-based", "plant based"):    return "Vegetarian"
    if has("cafe", "coffee", "roaster"):                   return "Cafe & Coffee"
    if has("bakery", "patisserie", "boulangerie", "pasticceria"):
        return "Bakery"
    if has("wine bar", "wine-led", "natural wine"):        return "Wine Bar"
    if has("cocktail"):                                    return "Cocktail Bar"
    if has("modern american", "new american", "american contemporary"):
        return "Modern American"
    if has("american"):                                    return "American"
    if has("fine dining", "tasting menu", "michelin"):     return "Fine Dining"
    return "Other"


def _entity_card_html(e: dict, *, is_pick: bool = False) -> str:
    pick = '<span class="tj-pick-badge">Editor\'s pick</span>' if is_pick else ''
    price = html.escape(e["price_tier"]) if e["price_tier"] else ""
    cuisine = html.escape(e["cuisine"]) if e["cuisine"] else ""
    nbhd = html.escape(e["neighborhood"]) if e["neighborhood"] else ""
    city = html.escape(e["city_name"])
    country = html.escape(e.get("country_name", ""))
    score_val = e.get("editorial_score")
    score_html = ""
    if isinstance(score_val, (int, float)) and 1.0 <= score_val <= 5.0:
        score_html = (
            f' <span class="tj-entity-score" '
            f'aria-label="TableJourney editorial score {score_val:.1f} out of 5">'
            f'★ {score_val:.1f}</span>'
        )
    meta_bits = [b for b in [cuisine, price] if b]
    meta_line = " · ".join(meta_bits)
    locale_bits = [b for b in [nbhd, city, country] if b]
    locale = ", ".join(locale_bits)
    raw_desc = e.get("description", "")
    if len(raw_desc) > 140:
        # First try: end at the nearest preceding sentence boundary within 90..140
        cut = raw_desc[:140]
        idx = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
        if idx >= 90:
            raw_desc = cut[:idx + 1]
        else:
            # Fall back to word boundary + ellipsis
            sp = cut.rfind(" ")
            raw_desc = (cut[:sp].rstrip(",.;: ") + "...") if sp >= 80 else (cut + "...")
    desc = html.escape(raw_desc)
    return (
        f'<a class="tj-entity-card" href="{html.escape(e["entity_url"])}">'
        f'{pick}'
        f'<h3 class="tj-entity-name">{html.escape(e["name"])}{score_html}</h3>'
        f'<p class="tj-entity-meta">{meta_line}</p>'
        f'<p class="tj-entity-locale">{locale}</p>'
        f'<p class="tj-entity-desc">{desc}</p>'
        f'</a>'
    )


def _render_entity_topic_body(slug: str, name: str, entities: list[dict]) -> str:
    """Render Option B layout: editorial picks + filter chips + card grid + JS."""
    if not entities:
        return (
            f'<p>We have not yet published a <strong>{html.escape(name.lower())}</strong> '
            f'chapter for any city. New city guides are added regularly. '
            f'<a href="/cities/">Browse the cities we cover</a> '
            f'or <a href="/contact/">tell us where you want us to eat next</a>.</p>'
        )

    n_total = len(entities)
    city_set = sorted({e["city_name"] for e in entities})
    n_cities = len(city_set)

    # Header line
    header = (
        f'<p class="tj-topic-headline"><strong>{n_total}</strong> '
        f'{html.escape(name.lower())} across <strong>{n_cities}</strong> '
        f'{"city" if n_cities == 1 else "cities"}.</p>'
    )

    # Editorial section: first 6 entries by JSON order (curation lives in the JSON)
    # Only render when there's enough to make it feel distinct from the full list.
    editorial = ""
    if n_total >= 12:
        picks = entities[:6]
        editorial = (
            '<section class="tj-topic-section">'
            f'<h2>Editor\'s picks</h2>'
            '<div class="tj-entity-grid">'
            + "".join(_entity_card_html(e, is_pick=True) for e in picks) +
            '</div></section>'
        )

    # Filters as multi-select popups with type-ahead search. Trigger
    # button shows the active count; opening the popup reveals a search
    # input + checkbox list. Lewis 2026-05-19 wanted "search to selects
    # also, and multi select for the filtering". Multiple values combine
    # as OR within a filter category, AND across categories.
    def _select(label: str, key: str, values: list[str]) -> str:
        if len(values) < 2:
            return ""
        options = "".join(
            f'<label class="tj-filter-opt">'
            f'<input type="checkbox" data-filter="{key}" value="{html.escape(v)}"> '
            f'<span>{html.escape(v)}</span></label>'
            for v in values
        )
        gid = f"tj-filter-{key}"
        return (
            f'<div class="tj-filter-group" data-key="{key}">'
            f'<button type="button" class="tj-filter-trigger" data-filter-trigger="{key}" '
            f'aria-haspopup="true" aria-expanded="false" aria-controls="{gid}-popup">'
            f'<span class="tj-filter-label">{label}</span>'
            f'<span class="tj-filter-value" data-filter-value="{key}">All</span>'
            f'<svg class="tj-filter-caret" width="12" height="12" viewBox="0 0 16 16" aria-hidden="true">'
            f'<path fill="currentColor" d="M8 11.5 3.5 7h9z"/></svg>'
            f'</button>'
            f'<div class="tj-filter-popup" id="{gid}-popup" data-filter-popup="{key}" hidden>'
            f'<input type="search" class="tj-filter-search" placeholder="Search {html.escape(label.lower())}..." aria-label="Filter {html.escape(label.lower())}">'
            f'<div class="tj-filter-opts">{options}</div>'
            f'<div class="tj-filter-actions">'
            f'<button type="button" class="tj-filter-clear" data-filter-clear="{key}">Clear</button>'
            f'<button type="button" class="tj-filter-done">Done</button>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
    _chips = _select

    adapter = _TOPIC_FIELD_ADAPTERS.get(slug, {})
    cat_label = adapter.get("category_label", "Cuisine")
    price_label = adapter.get("price_label", "Price")

    cities_in_data = sorted({e["city_name"] for e in entities})
    prices_in_data = sorted({e["price_tier"] for e in entities if e["price_tier"]})
    # Bucket the raw cuisine strings into ~25 canonical classes for the
    # filter chip UI. The card subtitle still shows the entity's specific
    # cuisine string ("Bolognese trattoria, sfoglia pasta") — only the
    # chip labels collapse to "Italian".
    cuisines_in_data = sorted({_cuisine_class(e["cuisine"]) for e in entities if e["cuisine"]})

    filter_html = (
        '<div class="tj-topic-filters" role="region" aria-label="Filter">'
        + _chips("City", "city", cities_in_data)
        + _chips(price_label, "price", prices_in_data)
        + _chips(cat_label, "cuisine", cuisines_in_data)
        + '</div>'
    )

    # Grid: render ALL cards server-side (SEO-crawlable). The first
    # INITIAL_VISIBLE cards are visible by default; cards past that get
    # `.tj-hidden` directly on the entity card so the grid layout isn't
    # broken by a wrapper element.
    INITIAL_VISIBLE = 24
    def _wrap(i: int, e: dict) -> str:
        raw = _entity_card_html(e)
        if i >= INITIAL_VISIBLE:
            raw = raw.replace('"tj-entity-card"', '"tj-entity-card tj-hidden"', 1)
        return raw
    cards_html = "".join(_wrap(i, e) for i, e in enumerate(entities))
    grid_html = (
        f'<div class="tj-entity-grid" id="tj-topic-grid" data-initial-visible="{INITIAL_VISIBLE}">'
        + cards_html +
        '</div>'
    )

    show_more_html = (
        f'<div class="tj-topic-paginate">'
        f'<button type="button" class="tj-show-more" id="tj-show-more">Show all {n_total}</button>'
        f'</div>'
    ) if n_total > INITIAL_VISIBLE else ""

    browse_section = (
        '<section class="tj-topic-section">'
        f'<h2>Browse all {n_total}</h2>'
        + filter_html +
        '<div class="tj-topic-meta-row">'
        f'<span class="tj-topic-count" id="tj-topic-count">Showing {min(INITIAL_VISIBLE, n_total)} of {n_total}</span>'
        '</div>'
        + grid_html +
        show_more_html +
        '</section>'
    )

    # Inline data JSON for the client filter. Lean: only fields used for filtering.
    filter_data = [
        {"i": idx,
         "city": e["city_name"],
         "price": e["price_tier"],
         "cuisine": _cuisine_class(e["cuisine"])}
        for idx, e in enumerate(entities)
    ]
    data_json = json.dumps(filter_data, ensure_ascii=False)

    # Multi-select + search filter popups. Each filter category is a
    # button trigger + hidden popup with search input + checkboxes.
    # active.* is a Set per category; empty set = no filter on that key.
    # apply() shows a card iff every filter set is empty OR contains the
    # card's value for that key. Pagination kicks in only when no filters
    # are active.
    script = """
<script>
(function(){
  var data = window.__TJ_TOPIC_DATA__;
  var grid = document.getElementById('tj-topic-grid');
  var countEl = document.getElementById('tj-topic-count');
  if (!grid || !data) return;
  var cards = grid.children;
  var initialVisible = parseInt(grid.getAttribute('data-initial-visible') || '24', 10);
  var showAllBtn = document.getElementById('tj-show-more');
  var showAllOn = false;
  var active = { city: new Set(), price: new Set(), cuisine: new Set() };

  function anyFilter(){
    return active.city.size + active.price.size + active.cuisine.size > 0;
  }
  function matchKey(key, val){
    var s = active[key];
    return s.size === 0 || s.has(val);
  }

  function apply(){
    var shown = 0, total = data.length;
    var filtering = anyFilter();
    var paginateOff = filtering || showAllOn;
    for (var i=0;i<data.length;i++){
      var d = data[i];
      var matches = matchKey('city', d.city) && matchKey('price', d.price) && matchKey('cuisine', d.cuisine);
      var visible = matches && (paginateOff || i < initialVisible);
      cards[i].classList.toggle('tj-hidden', !visible);
      if (matches) shown++;
    }
    countEl.textContent = paginateOff
        ? ('Showing ' + shown + ' of ' + total)
        : ('Showing ' + Math.min(initialVisible, shown) + ' of ' + total);
    if (showAllBtn) showAllBtn.style.display = paginateOff ? 'none' : '';

    ['city','price','cuisine'].forEach(function(k){
      var lbl = document.querySelector('[data-filter-value="' + k + '"]');
      if (!lbl) return;
      var s = active[k];
      lbl.textContent = s.size === 0 ? 'All' :
                        s.size === 1 ? Array.from(s)[0] :
                        s.size + ' selected';
      var trig = document.querySelector('[data-filter-trigger="' + k + '"]');
      if (trig) trig.classList.toggle('tj-has-selection', s.size > 0);
    });
  }

  function closeAll(){
    document.querySelectorAll('.tj-filter-popup').forEach(function(p){
      p.hidden = true;
      var t = document.querySelector('[data-filter-trigger="' + p.getAttribute('data-filter-popup') + '"]');
      if (t) t.setAttribute('aria-expanded','false');
    });
  }

  function clampPopup(popup){
    // Reset inline positioning so each open re-measures fresh.
    popup.style.left = '0';
    popup.style.right = '';
    var margin = 8;
    var vw = document.documentElement.clientWidth;
    var r = popup.getBoundingClientRect();
    if (r.right > vw - margin) {
      // Shift left so the popup's right edge sits inside the viewport.
      var shift = (vw - margin) - r.right;
      popup.style.left = shift + 'px';
      r = popup.getBoundingClientRect();
    }
    if (r.left < margin) {
      // Popup is wider than the room available to the right; pin its left
      // edge to the viewport margin instead of staying under the trigger.
      var op = popup.offsetParent;
      var opLeft = op ? op.getBoundingClientRect().left : 0;
      popup.style.left = (margin - opLeft) + 'px';
    }
  }
  document.querySelectorAll('[data-filter-trigger]').forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      var key = btn.getAttribute('data-filter-trigger');
      var popup = document.querySelector('[data-filter-popup="' + key + '"]');
      var isOpen = !popup.hidden;
      closeAll();
      if (!isOpen){
        popup.hidden = false;
        btn.setAttribute('aria-expanded','true');
        clampPopup(popup);
        var s = popup.querySelector('.tj-filter-search');
        if (s) setTimeout(function(){ s.focus(); s.value=''; filterOptions(popup, ''); }, 10);
      }
    });
  });

  function filterOptions(popup, q){
    q = q.toLowerCase().trim();
    popup.querySelectorAll('.tj-filter-opt').forEach(function(opt){
      var txt = (opt.querySelector('span').textContent || '').toLowerCase();
      opt.style.display = (!q || txt.indexOf(q) >= 0) ? '' : 'none';
    });
  }
  document.querySelectorAll('.tj-filter-search').forEach(function(inp){
    inp.addEventListener('input', function(){ filterOptions(inp.parentElement, inp.value); });
  });

  document.querySelectorAll('.tj-filter-opt input[type=checkbox]').forEach(function(cb){
    cb.addEventListener('change', function(){
      var key = cb.getAttribute('data-filter');
      if (cb.checked) active[key].add(cb.value); else active[key].delete(cb.value);
      apply();
    });
  });

  document.querySelectorAll('[data-filter-clear]').forEach(function(b){
    b.addEventListener('click', function(){
      var key = b.getAttribute('data-filter-clear');
      active[key].clear();
      document.querySelectorAll('input[data-filter="' + key + '"]').forEach(function(c){ c.checked = false; });
      apply();
    });
  });
  document.querySelectorAll('.tj-filter-done').forEach(function(b){
    b.addEventListener('click', closeAll);
  });

  document.addEventListener('click', function(e){
    if (!e.target.closest('.tj-filter-group')) closeAll();
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') closeAll();
  });

  if (showAllBtn) showAllBtn.addEventListener('click', function(){ showAllOn = true; apply(); });
  apply();
})();
</script>
"""
    data_blob = f'<script>window.__TJ_TOPIC_DATA__={data_json};</script>'

    # ItemList schema. Google's rich-list rich results consider the first
    # 100 elements; we cap at 50 to keep payload reasonable. Editor's picks
    # come first so the highest-signal entities are always in the cap.
    itemlist_jsonld = _topic_itemlist_jsonld(slug, name, entities)

    return header + editorial + browse_section + data_blob + itemlist_jsonld + script


def _topic_itemlist_jsonld(slug: str, name: str, entities: list[dict], limit: int = 50) -> str:
    """Build an ItemList JSON-LD block for a global topic page.

    Schema.org ItemList tells Google the page is a curated list and
    enumerates its members so the list-rich-result becomes eligible.
    """
    items = []
    for i, e in enumerate(entities[:limit], start=1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "url": "https://tablejourney.com" + e["entity_url"],
            "name": e["name"],
        })
    blob = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{name} on TableJourney",
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "numberOfItems": len(entities),
        "itemListElement": items,
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(blob, ensure_ascii=False, separators=(",", ":"))
        + '</script>'
    )


def render_topic_cross_city(renderer, topic, cities):
    slug = topic["slug"]
    name = topic["name"]
    icon = topic["icon"]
    title, lede = TOPIC_META.get(slug, (f"{name} guides", f"{name} guides on TableJourney."))

    # Entity-list topics get the filterable card grid (Option B design).
    # Narrative topics keep the original city-list pattern.
    if slug in _ENTITY_LIST_TOPICS:
        entities = _aggregate_topic_entities(slug, cities)
        body = _render_entity_topic_body(slug, name, entities)
    else:
        items = []
        for c in cities:
            topic_dir = CONTENT / c["country_slug"] / c["city_slug"] / slug
            if not (topic_dir / "index.html").exists():
                continue
            url = f"/{c['country_slug']}/{c['city_slug']}/{slug}/"
            items.append(
                f'<li><a href="{html.escape(url)}"><strong>{html.escape(name)} in {html.escape(c["name"])}</strong>'
                f'<span class="tj-list-sub">Editor picks, neighbourhoods, what to order, what to skip.</span></a></li>'
            )
        if items:
            list_id = f"tj-cities-{slug}"
            body = (
                f'<p>Every TableJourney city is broken into the same twenty-four food chapters, so you can read just the '
                f'<strong>{html.escape(name.lower())}</strong> chapter for whichever city you are travelling to. Pick a city below.</p>'
                + filter_search_widget(
                    target_selector=f"#{list_id}",
                    item_selector="li",
                    placeholder=f"Filter {name.lower()} by city…",
                    aria_label=f"Filter {name.lower()} city list",
                )
                + f'<ul id="{list_id}" class="tj-grid-list">{"".join(items)}</ul>'
                f'<p class="tj-note">More cities are in research. Want one covered next? '
                f'<a href="/contact/">Tell us where you want to eat.</a></p>'
            )
        else:
            body = (
                f'<p>We have not yet published a <strong>{html.escape(name.lower())}</strong> chapter for any city. '
                f'New city guides are added regularly. '
                f'<a href="/cities/">Browse the cities we cover</a> '
                f'or <a href="/contact/">tell us where you want us to eat next</a>.</p>'
            )

    page_h1 = f"{icon}  {name}"

    return render_chrome(
        renderer,
        slug=f"topics/{slug}",
        title=f"{title} | TableJourney",
        meta_description=lede,
        h1=page_h1,
        subtitle=lede,
        body_html=body,
        breadcrumb=crumb(
            ("Home", f"{BASE}/"),
            ("Topics", f"{BASE}/topics/"),
            (name, None),
        ),
    )


# ──────────────────────────────────────────────────────────────────────
# /search/ page (client-side, reads /search/search-index.json)
# ──────────────────────────────────────────────────────────────────────

SEARCH_BODY = """
<form class="tj-search-form" role="search" action="/search/" method="get" id="tj-search-form">
    <label class="tj-sr-only" for="tj-search-q">Search a city, dish, cuisine, restaurant or topic</label>
    <input id="tj-search-q" name="q" type="search" placeholder="Try Paris, steak frites, bistrot paul bert..." autocomplete="off" autofocus>
    <button type="submit">Search</button>
</form>
<div class="tj-search-type-filters" id="tj-search-type-filters" role="group" aria-label="Filter by result type"
     style="display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 4px;">
    <button type="button" class="tj-search-type-pill is-active" data-type="all"
            style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:var(--tj-surface);color:inherit;font-size:0.9rem;cursor:pointer;">All</button>
    <button type="button" class="tj-search-type-pill" data-type="city" style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:transparent;color:inherit;font-size:0.9rem;cursor:pointer;">Cities</button>
    <button type="button" class="tj-search-type-pill" data-type="entity" style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:transparent;color:inherit;font-size:0.9rem;cursor:pointer;">Places</button>
    <button type="button" class="tj-search-type-pill" data-type="dish" style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:transparent;color:inherit;font-size:0.9rem;cursor:pointer;">Dishes</button>
    <button type="button" class="tj-search-type-pill" data-type="cuisine" style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:transparent;color:inherit;font-size:0.9rem;cursor:pointer;">Cuisines</button>
    <button type="button" class="tj-search-type-pill" data-type="topic" style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:transparent;color:inherit;font-size:0.9rem;cursor:pointer;">Topics</button>
    <button type="button" class="tj-search-type-pill" data-type="country" style="padding:6px 12px;border:1px solid var(--tj-border);border-radius:999px;background:transparent;color:inherit;font-size:0.9rem;cursor:pointer;">Countries</button>
</div>
<p class="tj-search-status" id="tj-search-status">Type a city, dish, restaurant, cuisine, neighbourhood, or topic.</p>
<ul class="tj-grid-list" id="tj-search-results" aria-live="polite"></ul>

<script>
(function () {
  var input  = document.getElementById('tj-search-q');
  var list   = document.getElementById('tj-search-results');
  var status = document.getElementById('tj-search-status');
  var form   = document.getElementById('tj-search-form');
  var pills  = document.querySelectorAll('.tj-search-type-pill');
  var idx = null;
  var renderTimer = null;
  var activeType = 'all';

  function urlQ() {
    var p = new URLSearchParams(window.location.search);
    return p.get('q') || '';
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];
    });
  }
  // Diacritic-strip + lowercase. Mirrors server-side _norm() in
  // generate_search_index.py so 'cafe' matches 'Café' and vice versa.
  function norm(s) {
    return String(s || '')
      .normalize('NFKD')
      .replace(/[\\u0300-\\u036f]/g, '')
      .toLowerCase()
      .trim();
  }

  // Per-token scoring. Each query token contributes a bonus based on
  // *where* it lands in the entry's tokens blob: exact start of name,
  // start of any word, or substring anywhere. Tokens that don't appear
  // at all kill the result (every token must match somewhere).
  function tokenScore(tokensBlob, name, t) {
    if (!t) return 0;
    if (tokensBlob.indexOf(t) < 0) return -1;          // miss -> reject
    if (name.indexOf(t) === 0) return 40;              // name starts with token
    if ((' ' + name).indexOf(' ' + t) >= 0) return 30; // word-start in name
    if (tokensBlob.indexOf(t) === 0) return 20;        // token blob starts with t
    if ((' ' + tokensBlob).indexOf(' ' + t) >= 0) return 15; // word-start elsewhere
    return 5;                                          // substring fallback
  }

  function score(item, qTokens) {
    if (!qTokens.length) return 0;
    var nameN = norm(item.name);
    var blob = item.tokens || (nameN + ' ' + norm(item.subtitle || ''));
    var total = 0;
    for (var i = 0; i < qTokens.length; i++) {
      var s = tokenScore(blob, nameN, qTokens[i]);
      if (s < 0) return 0; // any unmet token -> drop this entry entirely
      total += s;
    }
    // Bonus when query exactly equals the name (autocomplete-feel).
    if (nameN === qTokens.join(' ')) total += 100;
    // Type weight tilts ties toward higher-value page types.
    return total + (item.weight || 1);
  }

  function render(q) {
    if (!idx) { status.textContent = 'Loading search index...'; return; }
    var qN = norm(q);
    if (!qN) {
      status.textContent = 'Type a city, dish, restaurant, cuisine, neighbourhood, or topic.';
      list.innerHTML = '';
      return;
    }
    var qTokens = qN.split(/\\s+/).filter(Boolean);
    var results = [];
    for (var i = 0; i < idx.length; i++) {
      // Type filter: 'all' accepts everything; specific filters match the
      // entry's `type` field exactly.
      if (activeType !== 'all' && idx[i].type !== activeType) continue;
      var s = score(idx[i], qTokens);
      if (s > 0) results.push({ item: idx[i], s: s });
    }
    results.sort(function (a, b) {
      if (b.s !== a.s) return b.s - a.s;
      return a.item.name.localeCompare(b.item.name);
    });
    results = results.slice(0, 50);
    if (!results.length) {
      status.textContent = 'No matches for "' + q + '". Try a different spelling, or browse the ' +
        '<a href="/cities/">cities</a>, <a href="/dishes/">dishes</a> or <a href="/cuisines/">cuisines</a> indexes.';
      list.innerHTML = '';
      return;
    }
    status.textContent = results.length + ' result' + (results.length === 1 ? '' : 's') + ' for "' + q + '".';
    var out = new Array(results.length);
    for (var j = 0; j < results.length; j++) {
      var it = results[j].item;
      out[j] = '<li><a href="' + escapeHtml(it.url) + '"><strong>' + escapeHtml(it.name) + '</strong>'
             + (it.subtitle ? '<span class="tj-list-sub">' + escapeHtml(it.subtitle) + '</span>' : '')
             + '</a></li>';
    }
    list.innerHTML = out.join('');
  }

  // Debounce keystrokes so we don't re-render on every char at scale.
  function scheduleRender() {
    if (renderTimer) clearTimeout(renderTimer);
    renderTimer = setTimeout(function () { render(input.value); }, 60);
  }

  fetch('/search/search-index.json', { credentials: 'omit' })
    .then(function (r) { return r.ok ? r.json() : { entries: [] }; })
    .then(function (data) {
      idx = Array.isArray(data) ? data : (data.entries || data.items || []);
      render(input.value || urlQ());
    })
    .catch(function () { status.textContent = 'Could not load the search index.'; });

  input.addEventListener('input', scheduleRender);
  form.addEventListener('submit', function (e) { e.preventDefault(); render(input.value); });
  // Type-filter pills — clicking toggles the result-type narrowing and
  // re-renders the current query.
  pills.forEach(function (p) {
    p.addEventListener('click', function () {
      activeType = p.getAttribute('data-type') || 'all';
      pills.forEach(function (q) {
        q.classList.toggle('is-active', q === p);
        q.style.background = (q === p) ? 'var(--tj-surface)' : 'transparent';
      });
      render(input.value);
    });
  });
  var q0 = urlQ();
  if (q0) { input.value = q0; }
})();
</script>
"""

def render_search_page(renderer):
    return render_chrome(
        renderer,
        slug="search",
        title="Search TableJourney. cities, dishes, cuisines, topics",
        meta_description="Search every page on TableJourney by city, dish, cuisine, neighbourhood or topic: restaurants, markets, food tours, festivals and the full editorial archive.",
        h1="Search",
        subtitle="Cities, dishes, cuisines and topics across the full archive.",
        body_html=SEARCH_BODY,
        breadcrumb=crumb(("Home", f"{BASE}/"), ("Search", None)),
        page_type="webpage",
    )


def render_404_page(renderer):
    body = (
        '<p>The page you are looking for has moved, never existed, or has been '
        'retired by the editorial desk. Here are some better doors in:</p>'
        '<ul class="tj-grid-list">'
        '<li><a href="/"><strong>Home</strong>'
        '<span class="tj-list-sub">Featured cities, trending dishes, every food topic</span></a></li>'
        '<li><a href="/cities/"><strong>All cities</strong>'
        '<span class="tj-list-sub">Every city TableJourney covers</span></a></li>'
        '<li><a href="/topics/"><strong>All topics</strong>'
        '<span class="tj-list-sub">Restaurants, street food, markets, festivals and the rest</span></a></li>'
        '<li><a href="/search/"><strong>Search</strong>'
        '<span class="tj-list-sub">Find a city, dish, cuisine or topic by name</span></a></li>'
        '</ul>'
    )
    return render_chrome(
        renderer,
        slug="404",
        title="Page not found | TableJourney",
        meta_description="The page you are looking for has moved, never existed, or has been retired. Here are some better doors in: home, all cities, all topics, search.",
        h1="Page not found",
        subtitle="404. Let's get you back to the table.",
        body_html=body,
        breadcrumb=crumb(("Home", f"{BASE}/"), ("Not found", None)),
        page_type="webpage",
        # 404 page must NOT be indexed (Google would treat it as a soft-404
        # for the real URL the visitor was trying to reach). It also lives at
        # /404.html, not /404/, so the canonical needs the .html form.
        canonical_override=f"{BASE}/404.html",
        robots_override="noindex, nofollow",
    )


# ──────────────────────────────────────────────────────────────────────
# /feed.xml. minimal RSS pointing at city + topic pages
# ──────────────────────────────────────────────────────────────────────

def build_feed(cities):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for c in cities:
        city_url = f"{BASE}/{c['country_slug']}/{c['city_slug']}/"
        items.append(f"""
    <item>
      <title>{xml_escape(c['name'])} food guide</title>
      <link>{city_url}</link>
      <guid isPermaLink="true">{city_url}</guid>
      <pubDate>{now}</pubDate>
      <description>{xml_escape(f"The TableJourney food guide to {c['name']}: restaurants, dishes, markets, hidden gems and food culture, edited in person.")}</description>
    </item>""")
        # Also add a couple of the most read topics
        for topic_slug in ("restaurants", "signature-dishes", "hidden-gems"):
            t_dir = CONTENT / c["country_slug"] / c["city_slug"] / topic_slug
            if not (t_dir / "index.html").exists():
                continue
            t_url = f"{city_url}{topic_slug}/"
            t_name = next((t["name"] for t in FOOD_TOPIC_NAV if t["slug"] == topic_slug), topic_slug)
            items.append(f"""
    <item>
      <title>{xml_escape(f'{t_name} in {c["name"]}')}</title>
      <link>{t_url}</link>
      <guid isPermaLink="true">{t_url}</guid>
      <pubDate>{now}</pubDate>
      <description>{xml_escape(f'{t_name} in {c["name"]}. TableJourney editorial picks.')}</description>
    </item>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>TableJourney. where the world eats</title>
    <link>{BASE}/</link>
    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml" />
    <description>Food travel guides for the world's great eating cities, written by editors who eat in person.</description>
    <language>en</language>
    <lastBuildDate>{now}</lastBuildDate>
    <generator>tablejourney/scripts/generate_extras.py</generator>{''.join(items)}
  </channel>
</rss>
"""


# ──────────────────────────────────────────────────────────────────────
# /og/default.jpg. simple 1200x630 brand card
# ──────────────────────────────────────────────────────────────────────

def write_og_image(path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    bg = (250, 246, 240)
    accent = (200, 74, 46)
    text = (26, 26, 26)
    muted = (92, 87, 80)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    def load_font(size, bold=False):
        candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    title_font = load_font(120, bold=True)
    tag_font = load_font(40, bold=False)
    brand_font = load_font(34, bold=True)

    # Accent rule top + bottom
    d.rectangle([(0, 0), (W, 14)], fill=accent)
    d.rectangle([(0, H - 14), (W, H)], fill=accent)

    # Brand mark
    d.text((80, 60), "TableJourney", fill=text, font=brand_font)

    # Title two lines
    d.text((80, 210), "Where the world", fill=text, font=title_font)
    d.text((80, 340), "eats.", fill=accent, font=title_font)

    # Tagline
    d.text((80, 510), "Food travel guides for the world's great eating cities.", fill=muted, font=tag_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=88, optimize=True)
    print(f"wrote {path}")


# ──────────────────────────────────────────────────────────────────────
# /logo.png. 1024x1024 brand mark for JSON-LD Organization.logo
# ──────────────────────────────────────────────────────────────────────

def write_logo(path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    W = H = 1024
    bg = (250, 246, 240)
    accent = (200, 74, 46)
    text = (26, 26, 26)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    def load_font(size, bold=True):
        candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    # accent rim
    rim = 28
    d.rectangle([(0, 0), (W, rim)], fill=accent)
    d.rectangle([(0, H - rim), (W, H)], fill=accent)
    d.rectangle([(0, 0), (rim, H)], fill=accent)
    d.rectangle([(W - rim, 0), (W, H)], fill=accent)

    # stacked "Table / Journey", Journey in accent
    title_font = load_font(190, bold=True)
    t1 = "Table"
    t2 = "Journey"
    bb1 = d.textbbox((0, 0), t1, font=title_font)
    bb2 = d.textbbox((0, 0), t2, font=title_font)
    w1, h1 = bb1[2] - bb1[0], bb1[3] - bb1[1]
    w2, h2 = bb2[2] - bb2[0], bb2[3] - bb2[1]
    gap = 30
    block_h = h1 + gap + h2
    y0 = (H - block_h) // 2 - 20
    d.text(((W - w1) // 2, y0), t1, fill=text, font=title_font)
    d.text(((W - w2) // 2, y0 + h1 + gap), t2, fill=accent, font=title_font)

    # mark
    mark_font = load_font(48, bold=False)
    mark = "where the world eats"
    mb = d.textbbox((0, 0), mark, font=mark_font)
    mw = mb[2] - mb[0]
    d.text(((W - mw) // 2, H - rim - 110), mark, fill=text, font=mark_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {path}")


# ──────────────────────────────────────────────────────────────────────
# /og/<city>.jpg. per-city 1200x630 social card
# ──────────────────────────────────────────────────────────────────────

def write_city_og(path: Path, city_name: str, tagline: str = "") -> None:
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    bg = (250, 246, 240)
    accent = (200, 74, 46)
    text = (26, 26, 26)
    muted = (92, 87, 80)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    def load_font(size, bold=True):
        candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    brand_font = load_font(34, bold=True)
    eyebrow_font = load_font(34, bold=False)
    title_font = load_font(150, bold=True)
    tag_font = load_font(34, bold=False)

    d.rectangle([(0, 0), (W, 14)], fill=accent)
    d.rectangle([(0, H - 14), (W, H)], fill=accent)
    d.text((80, 60), "TableJourney", fill=text, font=brand_font)
    d.text((80, 170), "Food guide", fill=muted, font=eyebrow_font)
    d.text((80, 220), city_name, fill=text, font=title_font)

    if tagline:
        # truncate to fit one line
        max_chars = 70
        line = tagline if len(tagline) <= max_chars else tagline[: max_chars - 1].rsplit(" ", 1)[0] + "."
        d.text((80, 470), line, fill=muted, font=tag_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=88, optimize=True)
    print(f"wrote {path}")


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main() -> int:
    renderer = TemplateRenderer()
    cities = discover_cities()

    # cross-city topic pages
    for topic in FOOD_TOPIC_NAV:
        out = CONTENT / "topics" / topic["slug"] / "index.html"
        write(out, render_topic_cross_city(renderer, topic, cities))

    # search
    write(CONTENT / "search" / "index.html", render_search_page(renderer))

    # 404
    write(CONTENT / "404.html", render_404_page(renderer))

    # feed
    feed_path = CONTENT / "feed.xml"
    feed_path.write_text(build_feed(cities), encoding="utf-8")
    print(f"wrote {feed_path}")

    # og image (default + per city)
    write_og_image(CONTENT / "og" / "default.jpg")
    for c in cities:
        write_city_og(CONTENT / "og" / f"{c['city_slug']}.jpg", c["name"], c.get("tagline", ""))

    # logo for JSON-LD Organization.logo
    write_logo(CONTENT / "logo.png")

    print(f"\nDone. cities discovered: {len(cities)} ({', '.join(c['city_slug'] for c in cities) or 'none'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
