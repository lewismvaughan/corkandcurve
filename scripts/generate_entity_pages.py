#!/usr/bin/env python3
"""Generate per-entity detail pages for a city.

For each entity-bearing topic, emits:
    content/<country>/<city>/<topic>/<slug>/index.html

One entity = one page. Page provides full schema.org Restaurant/LocalBusiness,
breadcrumbs, address + Google Maps directions link, "more in <topic>"
siblings list, and links to cuisine/neighborhood/dish cross-cuts.

Usage:
    python scripts/generate_entity_pages.py france paris       # one city
    python scripts/generate_entity_pages.py --all              # every city
"""

from __future__ import annotations

import argparse
import functools
import json
import sys
from datetime import date as _date
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))

from utils.cuisine import canonicalise as _canon_cuisine
from utils.data_loader import load_for_topic, get_all_countries, get_all_regions
from utils.seo import meta_desc as _meta_desc
from utils.slug import slugify
from utils.template_renderer import TemplateRenderer

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}

EVENT_STATUS_MAP = {
    "scheduled":   "https://schema.org/EventScheduled",
    "cancelled":   "https://schema.org/EventCancelled",
    "postponed":   "https://schema.org/EventPostponed",
    "rescheduled": "https://schema.org/EventRescheduled",
}


_CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
_COUNTRY_CURRENCY = {"united-states": "USD", "france": "EUR", "japan": "JPY"}


def _parse_price_to_offer(price_str, country_slug=None):
    """Parse free-form price like '$95-225' / '€175' / '$75' into an Offer
    JSON-LD dict. Returns None when no usable signal can be extracted.

    Output shapes:
      - single price:   {"price": 175, "priceCurrency": "EUR"}
      - range:          {"priceSpecification": {"minPrice": 75, "maxPrice": 150,
                          "priceCurrency": "USD"}}
    Caller wraps with @type=Offer and availability/url.
    """
    if not price_str or not isinstance(price_str, str):
        return None
    s = price_str.strip()
    currency = None
    for sym, code in _CURRENCY_SYMBOLS.items():
        if sym in s:
            currency = code
            break
    if not currency and country_slug:
        currency = _COUNTRY_CURRENCY.get(country_slug)
    if not currency:
        return None
    import re as _re
    numbers = [int(n) for n in _re.findall(r"\d+", s)]
    if not numbers:
        return None
    if len(numbers) == 1:
        return {"price": numbers[0], "priceCurrency": currency}
    lo, hi = min(numbers), max(numbers)
    if lo == hi:
        return {"price": lo, "priceCurrency": currency}
    return {
        "priceSpecification": {
            "minPrice": lo,
            "maxPrice": hi,
            "priceCurrency": currency,
        }
    }


def _next_festival_occurrence(start_month, start_day, end_month=None, end_day=None, today=None):
    """Compute next future occurrence ISO date range for an annual festival.

    Returns (start_iso, end_iso) or (None, None) when the recurrence
    pattern is incomplete or invalid. Rolls forward by one year when
    the most-recent occurrence has already ended, so static pages stay
    eligible for Google rich event cards without per-year JSON edits.
    """
    today = today or _date.today()
    sm = MONTH_MAP.get(start_month) if start_month else None
    if not sm or not start_day:
        return None, None
    em = MONTH_MAP.get(end_month or start_month)
    if not em:
        return None, None
    eday = end_day or start_day
    try:
        start = _date(today.year, sm, int(start_day))
        end_year = today.year + (1 if em < sm else 0)
        end = _date(end_year, em, int(eday))
    except (ValueError, TypeError):
        return None, None
    if end < today:
        try:
            start = _date(start.year + 1, sm, int(start_day))
            end = _date(end.year + 1, em, int(eday))
        except (ValueError, TypeError):
            return None, None
    return start.isoformat(), end.isoformat()

# topic-slug -> (research-key, single-entity label, schema.org @type)
ENTITY_TOPICS = {
    "vineyards":        ("vineyards",        "Vineyard",        "Winery"),
    "tasting-rooms":    ("tasting_rooms",    "Tasting room",    "Winery"),
    "wine-bars":        ("wine_bars",        "Wine bar",        "BarOrPub"),
    "wine-restaurants": ("wine_restaurants", "Wine restaurant", "Restaurant"),
    "wine-retailers":   ("wine_retailers",   "Wine retailer",   "Store"),
    "wine-schools":     ("wine_schools",     "Wine school",     "EducationEvent"),
    "wine-tours":       ("wine_tours",       "Wine tour",       "LocalBusiness"),
    "wine-festivals":   ("wine_festivals",   "Wine festival",   "Festival"),
    "distilleries":     ("distilleries",     "Distillery",      "Distillery"),
    "wine-museums":     ("wine_museums",     "Wine museum",     "Museum"),
    "wine-hotels":      ("wine_hotels",      "Wine hotel",      "LodgingBusiness"),
    "wine-experiences": ("wine_experiences", "Wine experience", "TouristAttraction"),
    "budget-wines":     ("budget_wines",     "Budget wine pick", "Winery"),
    "hidden-gems":      ("hidden_gems",      "Hidden gem",      "Winery"),
    "day-trips-wine":   ("day_trips_wine",   "Wine day trip",   "TouristDestination"),
}

# Topic display names. Keep in sync with STANDARD_TOPICS in generate_topic_page.
TOPIC_DISPLAY_NAMES = {
    "vineyards": "Vineyards",
    "tasting-rooms": "Tasting Rooms",
    "wine-bars": "Wine Bars",
    "wine-restaurants": "Wine Restaurants",
    "wine-retailers": "Wine Retailers",
    "wine-schools": "Wine Schools",
    "wine-tours": "Wine Tours",
    "wine-festivals": "Wine Festivals",
    "distilleries": "Distilleries",
    "wine-museums": "Wine Museums",
    "wine-hotels": "Wine Hotels",
    "wine-experiences": "Wine Experiences",
    "budget-wines": "Budget Wines",
    "hidden-gems": "Hidden Gems",
    "day-trips-wine": "Wine Day Trips",
}


def directions_url(address: str, city_name: str) -> str:
    """Legacy Google Maps directions URL, used as the `directions_url`
    context value when a more precise google_maps_url isn't available.
    Same shape as google_maps_url (below) without the lat/lng anchor."""
    if not address:
        return ""
    if city_name and city_name.lower() not in address.lower():
        q = f"{address}, {city_name}"
    else:
        q = address
    return f"https://www.google.com/maps/dir/?api=1&destination={quote(q)}"


def google_maps_url(address: str, city_name: str, geo: dict | None) -> str:
    """Google Maps directions URL. Prefers lat/lng anchor when available
    (avoids the directions-to-wrong-place class of bug when the address
    is ambiguous or shared by multiple cities)."""
    if geo and "lat" in geo and ("lon" in geo or "lng" in geo):
        lon = geo.get("lon") or geo.get("lng")
        # `destination=lat,lng` + `destination_place_id` would be best but
        # we don't have a place_id. Coordinates alone are fine and
        # universally understood by Google Maps web + app.
        coord = f"{geo['lat']},{lon}"
        return f"https://www.google.com/maps/dir/?api=1&destination={coord}"
    return directions_url(address, city_name)


def apple_maps_url(address: str, city_name: str, geo: dict | None) -> str:
    """Apple Maps deep link. On iOS this opens the native Apple Maps
    app; everywhere else it falls back to the web preview at maps.apple.com.

    Coordinate anchor preferred when present, address fallback otherwise.
    `q=` is the search/destination query Apple Maps accepts."""
    if geo and "lat" in geo and ("lon" in geo or "lng" in geo):
        lon = geo.get("lon") or geo.get("lng")
        return f"https://maps.apple.com/?ll={geo['lat']},{lon}&q={geo['lat']},{lon}"
    if not address:
        return "https://maps.apple.com/"
    if city_name and city_name.lower() not in address.lower():
        q = f"{address}, {city_name}"
    else:
        q = address
    return f"https://maps.apple.com/?q={quote(q)}"


@functools.lru_cache(maxsize=1)
def _geocode_cache() -> dict:
    """Load the persistent geocode cache once per process. Missing file or
    parse error -> empty dict (geo fields just don't render)."""
    import hashlib as _hashlib  # local import keeps top-of-file clean
    p = Path(__file__).resolve().parent.parent / "data" / "geocode-cache.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _lookup_geo(address: str, city_name: str) -> dict | None:
    """Return {'lat': ..., 'lon': ...} or None. Same hashing as
    scripts/geocode_entities.py — must stay in sync."""
    if not address:
        return None
    import hashlib as _hashlib
    blob = f"{address.lower().strip()}|{city_name.lower().strip()}"
    key = _hashlib.sha1(blob.encode("utf-8")).hexdigest()
    entry = _geocode_cache().get(key)
    if entry and entry.get("ok"):
        return {"lat": entry["lat"], "lon": entry["lon"]}
    return None


def build_entity_context(
    *,
    entity: dict,
    topic_slug: str,
    topic_name: str,
    research_key: str,
    entity_type_label: str,
    entity_schema_type: str,
    country_slug: str,
    region_slug: str | None,
    destination: dict,
    region_seo: dict,
    siblings: list,
    valid_dish_slugs: set[str] | None = None,
) -> dict:
    """Assemble the Jinja context for a single entity page."""
    base_path_url = f"/{country_slug}/{region_slug}/" if region_slug else f"/{country_slug}/"
    topic_url = f"{base_path_url}{topic_slug}/"
    city_url = base_path_url
    entity_url = f"{topic_url}{entity['slug']}/"
    canonical = f"{BASE}{entity_url}"

    # Tour entries use `operator` instead of `name`. Normalise here so the
    # template can rely on entity.name being present.
    display_name = entity.get("name") or entity.get("operator") or entity["slug"].replace("-", " ").title()
    entity = dict(entity)
    entity["name"] = display_name

    # Attach geo coordinates from the persistent cache (populated by
    # scripts/geocode_entities.py). Missing -> field stays absent and
    # template skips the geo block. Caching is by (address, city) hash so
    # multiple entities at the same address share the lookup.
    geo = _lookup_geo(entity.get("address", ""), destination.get("name", ""))
    if geo:
        entity["geo"] = geo

    # Static map thumbnail (built by scripts/build_entity_maps.py).
    # Template uses entity.map_thumb_url; skip cleanly if the JPEG isn't
    # on disk yet (entity might not be geocoded, or maps not rebuilt).
    map_rel = f"maps/{country_slug}/{region_slug or country_slug}/{topic_slug}/{entity['slug']}.jpg"
    if (CONTENT_DIR / map_rel).exists():
        entity["map_thumb_url"] = f"/{map_rel}"

    # Precompute per-dish link records so the template only emits anchors
    # for dishes that actually have a /dish/<slug>/ cross-cut page. Anything
    # else renders as plain text. valid_dish_slugs is the set built from the
    # city's signature-dishes.json (passed in by generate_for_city).
    valid = valid_dish_slugs or set()
    sig_dishes_raw = entity.get("signature_dishes") or []
    if isinstance(sig_dishes_raw, list):
        entity["signature_dishes_links"] = [
            {
                "name": str(d),
                "url": (f"/dish/{slugify(str(d))}/" if slugify(str(d)) in valid else None),
            }
            for d in sig_dishes_raw
            if d
        ]
    else:
        entity["signature_dishes_links"] = []

    # Cooking-classes (EducationEvent) get Event-shaped JSON-LD too, but
    # with no fabricated startDate -- we don't have weekday/start_time
    # data for these schools yet. What we DO emit: location-wrapped
    # address (Event-canonical), Offer parsed from `price`, eventStatus,
    # eventAttendanceMode. When schedule data lands later, the template's
    # date branch lights up the same way festivals do.
    if topic_slug == "wine-schools":
        offer = _parse_price_to_offer(entity.get("price"), country_slug=country_slug)
        if offer:
            offer = {"@type": "Offer", **offer, "availability": "https://schema.org/InStock"}
            if entity.get("booking_url"):
                offer["url"] = entity["booking_url"]
            # validFrom is required by Google for nested Offer (GSC 2026-05-23).
            verified = entity.get("verified") or {}
            checked_on = verified.get("checked_on") if isinstance(verified, dict) else None
            if not offer.get("validFrom"):
                import datetime as _dt_local
                offer["validFrom"] = checked_on or _dt_local.date.today().isoformat()
            entity["offer_dict"] = offer
        entity["event_status_url"] = EVENT_STATUS_MAP["scheduled"]
        entity["event_attendance_mode_url"] = "https://schema.org/OfflineEventAttendanceMode"

    # Festival recurrence -> next-occurrence ISO dates. Only annual
    # festivals with an explicit start_day get Event-shaped schema; the
    # template gates emission on entity.start_date_iso so non-recurring
    # one-offs render the bare Festival type with no fabricated dates.
    if topic_slug == "wine-festivals" and entity.get("annual"):
        start_iso, end_iso = _next_festival_occurrence(
            entity.get("start_month") or entity.get("month"),
            entity.get("start_day"),
            entity.get("end_month"),
            entity.get("end_day"),
        )
        if start_iso and end_iso:
            entity["start_date_iso"] = start_iso
            entity["end_date_iso"] = end_iso
            status_key = (entity.get("event_status") or "scheduled").lower()
            entity["event_status_url"] = EVENT_STATUS_MAP.get(
                status_key, EVENT_STATUS_MAP["scheduled"]
            )

    # Title + meta description (kept in 140-165 sweet spot when we have signal).
    # Drop the " | Cork & Curve" suffix when it would push the title past
    # Google's ~70-char SERP truncation cap.
    _full_title = f"{display_name}, {topic_name} in {destination.get('name', '')} | Cork & Curve"
    _bare_title = f"{display_name}, {topic_name} in {destination.get('name', '')}"
    page_title = _full_title if len(_full_title) <= 70 else _bare_title
    base_desc = (entity.get("description") or "").strip().rstrip(".")
    city = destination.get("name", "")
    topic_l = topic_name.lower()

    # Extension fragments (added when base_desc is short, to land in 140-165).
    facts = []
    if entity.get("classification"):
        facts.append(entity["classification"])
    if entity.get("varietals"):
        _v = entity["varietals"]
        facts.append(", ".join(_v) if isinstance(_v, list) else str(_v))
    if entity.get("cuisine"):
        facts.append(entity["cuisine"])
    if entity.get("neighborhood"):
        facts.append(entity["neighborhood"])
    if entity.get("address"):
        facts.append(entity["address"].split(",")[0])  # street only
    facts_str = ", ".join(facts)

    # Build candidate descriptions across a length spectrum and pick the best
    # fit for the 140-165 sweet spot (rendered-length, HTML entities decoded).
    # Suffixes are listed from longest to shortest. _meta_desc picks the
    # longest variant whose total length lands in the band.
    variants: list[str] = []
    if base_desc:
        base = f"{base_desc}."
        # Place-and-context suffixes (when we have facts).
        if facts_str:
            variants += [
                f"{base} {display_name} in {city}, {facts_str}. Editor pick on Cork & Curve with address, hours, what to order and how to book.",
                f"{base} {display_name} in {city}, {facts_str}. Editor pick on Cork & Curve with address, hours and what to order.",
                f"{base} {display_name} in {city}, {facts_str}. Editor pick on Cork & Curve.",
                f"{base} {display_name} in {city}, {facts_str}.",
            ]
        variants += [
            f"{base} {display_name} in {city}, {topic_l}. Editor pick on Cork & Curve with address, hours, what to order, what to skip and how to book.",
            f"{base} {display_name} in {city}, {topic_l}. Editor pick on Cork & Curve with address, hours, what to order and how to book.",
            f"{base} {display_name} in {city}, {topic_l}. Editor pick on Cork & Curve with address, hours and what to order.",
            f"{base} {display_name} in {city}, {topic_l}. Editor pick on Cork & Curve.",
            # Tails for short bases: when {base} is 50-90 chars, these land
            # in 140-165 without the display_name+city repetition above.
            f"{base} Editor pick on Cork & Curve with address, hours, what to order, what to skip and how to book without queuing.",
            f"{base} Editor pick on Cork & Curve with address, opening hours, what to order, what to skip and how to book.",
            f"{base} Editor pick on Cork & Curve with address, hours, what to order and how to book without queuing.",
            f"{base} Editor pick on Cork & Curve with address, hours, what to order and how to book.",
            f"{base} Editor pick on Cork & Curve with address, hours and what to order.",
            f"{base} Editor pick on Cork & Curve with address and hours.",
            f"{base} Editor pick on Cork & Curve.",
            f"{base}",
        ]
    else:
        if facts_str:
            variants += [
                f"{display_name} in {city}, {topic_l}. {facts_str}. Editor pick on Cork & Curve with address, hours, what to order and how to book without queuing.",
                f"{display_name} in {city}, {topic_l}. {facts_str}. Editor pick on Cork & Curve with address, hours, what to order and how to book.",
                f"{display_name} in {city}, {topic_l}. {facts_str}. Address, hours, what to order and how to book on Cork & Curve.",
                f"{display_name} in {city}, {topic_l}. {facts_str}. Editor pick on Cork & Curve.",
            ]
        # Generic fallbacks for entities with no description and no facts.
        # The longer "review and tips" form lands in band when display_name +
        # city + topic_l combine to leave roughly 60-80 chars of headroom.
        variants += [
            f"{display_name} in {city}, {topic_l}: editor review on Cork & Curve with address, opening hours, what to order, what to skip and how to book without queuing.",
            f"{display_name} in {city}, {topic_l}: editor pick on Cork & Curve with address, opening hours, what to order, what to skip and tips on the best time to go.",
            f"{display_name} in {city}, {topic_l}: editor pick on Cork & Curve with address, opening hours, what to order and how to book without queuing.",
            f"{display_name} in {city}, {topic_l}: address, opening hours, what to order and how to book, plus editor notes on the night, on Cork & Curve.",
            f"{display_name} in {city}, {topic_l}. Address, opening hours, what to order and how to book on Cork & Curve.",
        ]

    desc = _meta_desc(*variants)

    # Breadcrumb: Home > Country > [State] > City > Topic > Entity
    country_name = destination.get("country", destination.get("name", ""))
    city_name = destination.get("name", "City")
    state_name = destination.get("state")
    state_slug = destination.get("state_slug")
    breadcrumb = [
        {"name": "Home", "url": "/"},
    ]
    if region_slug and country_name and country_name != city_name:
        breadcrumb.append({"name": country_name, "url": f"/{country_slug}/"})
    if state_name and state_slug:
        breadcrumb.append({"name": state_name, "url": f"/{country_slug}/{state_slug}/"})
    breadcrumb += [
        {"name": city_name, "url": city_url},
        {"name": topic_name, "url": topic_url},
        {"name": entity["name"], "url": None},
    ]

    # Cross-cut URLs. Only emit /cuisine/<slug>/ when (a) the raw cuisine
    # string resolves to a canonical entry in data/cuisines.json, AND (b)
    # the entity sits in a topic that the cross-cut aggregator actually
    # walks (restaurants/casual-dining/fine-dining). Other topics
    # (bakeries/cafes/bars/dietary etc.) can still carry a `cuisine`
    # value for display, but emitting a link to /cuisine/<slug>/ from a
    # dietary entity would 404 because the aggregator never produced
    # that page. Mirrors the cross-cut source-of-truth at
    # scripts/generate_cross_cuts.py:178.
    # Prefer the city-scoped cuisine page (/<country>/<region>/cuisine/<slug>/)
    # when it exists — same scope-down discipline we use on city × cuisines
    # index. Falls back to the global /cuisine/<slug>/ when the city page
    # wasn't emitted (no entities for that cuisine).
    cuisine_url = None
    if entity.get("cuisine") and topic_slug in {"restaurants", "fine-dining", "casual-dining"}:
        cc = _canon_cuisine(entity["cuisine"])
        if cc is not None:
            city_cuisine = (
                Path(__file__).resolve().parent.parent / "content"
                / country_slug / region_slug / "cuisine" / cc.slug / "index.html"
            ) if region_slug else None
            if city_cuisine and city_cuisine.exists():
                cuisine_url = f"/{country_slug}/{region_slug}/cuisine/{cc.slug}/"
            else:
                cuisine_url = f"/cuisine/{cc.slug}/"
    neighborhood_url = None
    if entity.get("neighborhood") and region_slug:
        neighborhood_url = f"/neighborhood/{region_slug}/{slugify(entity['neighborhood'])}/"

    # Pass through the `verified` block (checked_on date, source_url) so the
    # template can render a transparent provenance badge. Build a friendly
    # display date if checked_on is YYYY-MM-DD.
    _verified = entity.get("verified") or {}
    _checked_on = _verified.get("checked_on") if isinstance(_verified, dict) else None
    verified_display = None
    if isinstance(_checked_on, str) and len(_checked_on) == 10:
        try:
            y, m, d = _checked_on.split("-")
            _MONTHS = ["", "January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
            verified_display = f"{_MONTHS[int(m)]} {int(d)}, {y}"
        except (ValueError, IndexError):
            verified_display = _checked_on
    verified_source_url = _verified.get("source_url") if isinstance(_verified, dict) else None

    # Build a synthetic seo block for the template (entity-page-specific).
    seo = {
        "meta": {
            "title": page_title,
            "description": desc,
            "canonical_url": canonical,
            "robots": "index, follow, max-image-preview:large, max-snippet:-1",
        },
        "open_graph": {
            "og_title": entity["name"],
            "og_description": desc,
            "og_image": (
                # Prefer the destination's hero food photo (real Unsplash
                # shot) reformatted to 1200x630, so iMessage/Twitter/Slack
                # link previews show food instead of the typography card.
                # 2026-05-19.
                (destination.get("hero_image") or "")
                    .replace("w=1600", "w=1200")
                    .replace("h=900", "h=630")
                    .replace("h=1067", "h=630")
                or (region_seo.get("shared", {}) or {}).get("og_image")
                or f"{BASE}/og/default.jpg"
            ),
            "og_image_alt": f"{entity['name']} on Cork & Curve",
            "og_url": canonical,
            "og_type": "article",
            "og_locale": "en_US",
        },
        "twitter": {},
        "alternates": [],
        "geo": region_seo.get("geo", {}),
        "article": {
            "author": "Cork & Curve Editorial",
            "section": topic_name,
        },
    }

    return {
        "entity": entity,
        "entity_type": entity_type_label,
        "entity_schema": entity_schema_type,
        "topic": {"slug": topic_slug, "name": topic_name},
        "destination": destination,
        "country_slug": country_slug,
        "region_slug": region_slug or "",
        "city_url": city_url,
        "topic_url": topic_url,
        "cuisine_url": cuisine_url,
        "verified_display": verified_display,
        "verified_source_url": verified_source_url,
        "neighborhood_url": neighborhood_url,
        "directions_url": directions_url(entity.get("address", ""), destination.get("name", "")),
        "google_maps_url": google_maps_url(entity.get("address", ""), destination.get("name", ""), entity.get("geo")),
        "apple_maps_url": apple_maps_url(entity.get("address", ""), destination.get("name", ""), entity.get("geo")),
        "breadcrumb": breadcrumb,
        "siblings": siblings,
        "seo": seo,
        "base_path": "../../../.." if region_slug else "../../..",
        "analytics": {
            "page_type": "entity",
            "destination": region_slug or country_slug,
            "country": country_slug,
            "region": region_slug,
            "context": f"{country_slug}:{region_slug or ''}:{topic_slug}:{entity['slug']}",
        },
        # Date helpers for Event-shaped JSON-LD fallbacks (GSC 2026-05-23).
        "current_date_iso": _date.today().isoformat(),
        "next_year_iso": _date.today().replace(year=_date.today().year + 1).isoformat(),
    }


def _iter_entries_for_topic(research: dict, topic_slug: str):
    """Yield (entry_dict, siblings_excluding_self_list) for each entity in a topic.

    Siblings are picked by cyclic rotation rather than always-the-first-N so
    every entry shows up in roughly equal incoming-link counts. With a flat
    [:6] slice, the last few entries in the list never appear in any sibling
    rail and end up as low-incoming orphans.
    """
    if topic_slug in ("dietary", "nightlife"):
        # dict-of-lists; emit per-place under /<topic_slug>/<slug>/
        bucket = research.get(topic_slug) or {}
        all_places = []
        for places in bucket.values():
            if isinstance(places, list):
                all_places.extend(p for p in places if isinstance(p, dict) and p.get("slug"))
        for idx, p in enumerate(all_places):
            # Rotate the pool so each entry's first 6 siblings start
            # immediately after it. Tail entries (small sub-categories like
            # kosher / listening_bars) get crawled-into via mid-pool entries.
            rotated = all_places[idx + 1:] + all_places[:idx]
            sibs = [s for s in rotated if s.get("slug") != p.get("slug")][:6]
            yield p, sibs
        return

    research_key, _, _ = ENTITY_TOPICS[topic_slug]
    entries = research.get(research_key) or []
    entries = [e for e in entries if isinstance(e, dict) and e.get("slug")]
    for idx, entry in enumerate(entries):
        rotated = entries[idx + 1:] + entries[:idx]
        sibs = [s for s in rotated if s.get("slug") != entry.get("slug")][:6]
        yield entry, sibs


def generate_for_city(country_slug: str, region_slug: str | None) -> dict:
    """Render every entity page for a city. Returns counts dict.

    Also prunes stale entity directories under each topic so removed
    entries don't keep serving 200 OK after a subagent edit. Without
    this, every re-run grows the orphan set, creating duplicate-content
    SEO liability at scale.
    """
    import shutil as _shutil
    renderer = TemplateRenderer()
    template = renderer.env.get_template("entity-template.html")

    counts = {"pages": 0, "topics": 0, "skipped_no_slug": 0, "pruned": 0}

    # Load region.json once (for destination + seo geo).
    from utils.data_loader import load_file as _load_file
    region_payload = _load_file(country_slug, "region.json", region_slug)
    destination = region_payload.get("destination", {})
    region_seo = region_payload.get("seo", {})

    # Which topics actually have data — so the entity-page "Plan your visit"
    # sidebar only links to chapters that exist (no links to empty pages).
    from utils.data_loader import load_country_data as _lcd, populated_topic_slugs as _pts
    try:
        _populated_topics = sorted(_pts(_lcd(country_slug, region_slug=region_slug).get("research", {})))
    except Exception:
        _populated_topics = []

    # Build the valid /dish/<slug>/ set from this city's signature-dishes.json.
    # Used by build_entity_context to gate anchor emission so we never link
    # to a /dish/ page that the cross-cut generator hasn't written.
    valid_dish_slugs: set[str] = set()
    try:
        sd_payload = _load_file(country_slug, "signature-dishes.json", region_slug)
    except FileNotFoundError:
        sd_payload = {}
    for d in (sd_payload.get("signature_dishes") or sd_payload.get("research", {}).get("signature_dishes") or []):
        if isinstance(d, dict) and d.get("slug"):
            valid_dish_slugs.add(d["slug"])

    # Build a name -> rich-fields lookup from the "primary" topics so
    # secondary slim-schema entries (hidden-gems, late-night, brunch,
    # budget-eating, etc.) can borrow tagline / neighborhood / cuisine /
    # price_tier and render a full hero instead of a near-empty one.
    # Poznań 2026-05-19: Vine Bridge hidden-gems page rendered with just
    # the back-link + h1 + one stamp because hidden-gems.json doesn't
    # carry those fields, while restaurants/vine-bridge has all of them.
    # The merge runs in build_entity_context (per-entity) so all the
    # downstream context (facts string, schema, breadcrumbs) consume the
    # enriched record uniformly.
    PRIMARY_TOPICS = ("vineyards", "tasting-rooms", "wine-bars", "wine-restaurants")
    PROMOTE_FIELDS = ("description", "neighborhood", "classification", "varietals",
                      "owner", "winemaker", "hectares")

    def _norm_name(s: str) -> str:
        return (s or "").strip().lower()

    primary_lookup: dict[str, dict] = {}
    for _pt in PRIMARY_TOPICS:
        try:
            _pdata = load_for_topic(country_slug, _pt, region_slug=region_slug)
        except FileNotFoundError:
            continue
        _pres = _pdata.get("research", {})
        for _entry, _sibs in _iter_entries_for_topic(_pres, _pt):
            _key = _norm_name(_entry.get("name") or _entry.get("operator", ""))
            if not _key or _key in primary_lookup:
                continue
            primary_lookup[_key] = {f: _entry.get(f) for f in PROMOTE_FIELDS if _entry.get(f)}

    def _enrich_from_primary(entry: dict, topic: str) -> dict:
        if topic in PRIMARY_TOPICS:
            return entry
        rich = primary_lookup.get(_norm_name(entry.get("name") or entry.get("operator", "")))
        if not rich:
            return entry
        merged = dict(entry)
        for f, v in rich.items():
            if not merged.get(f):
                merged[f] = v
        return merged

    # Iterate over each entity-bearing topic (plus dietary, nightlife).
    extra_topics = list(ENTITY_TOPICS.keys()) + ["dietary", "nightlife"]
    for topic_slug in extra_topics:
        try:
            data = load_for_topic(country_slug, topic_slug, region_slug=region_slug)
        except FileNotFoundError:
            continue
        research = data.get("research", {})

        if topic_slug == "dietary":
            topic_display = "Biodynamic & Natural"
            research_key = "dietary"
            entity_label = "Estate"
            entity_schema = "Winery"
        elif topic_slug == "nightlife":
            topic_display = "Nightlife"
            research_key = "nightlife"
            entity_label = "Wine bar"
            entity_schema = "BarOrPub"
        else:
            research_key, entity_label, entity_schema = ENTITY_TOPICS[topic_slug]
            topic_display = TOPIC_DISPLAY_NAMES[topic_slug]

        # Collect the slugs we're about to (re)write for this topic so we
        # can prune anything left over from a prior generation.
        written_slugs: set[str] = set()
        topic_had_entries = False
        for entry, siblings in _iter_entries_for_topic(research, topic_slug):
            if not entry.get("slug"):
                counts["skipped_no_slug"] += 1
                continue
            # Honor verified.open_status: skip render for venues marked
            # permanently_closed or unknown. The provenance contract keeps
            # such entities in JSON for traceability (so we remember why
            # they were removed) but they MUST NOT render to a live URL.
            verified = entry.get("verified") or {}
            status = verified.get("open_status")
            if status in {"permanently_closed", "unknown"}:
                counts.setdefault("skipped_closed", 0)
                counts["skipped_closed"] += 1
                continue
            topic_had_entries = True

            enriched = _enrich_from_primary(entry, topic_slug)
            _ctx_populated = _populated_topics
            ctx = build_entity_context(
                entity=enriched,
                topic_slug=topic_slug,
                topic_name=topic_display,
                research_key=research_key,
                entity_type_label=entity_label,
                entity_schema_type=entity_schema,
                country_slug=country_slug,
                region_slug=region_slug,
                destination=destination,
                region_seo=region_seo,
                siblings=siblings,
                valid_dish_slugs=valid_dish_slugs,
            )

            ctx["populated_topics"] = _ctx_populated
            html = template.render(**ctx)

            # Output path
            parts = [CONTENT_DIR, country_slug]
            if region_slug:
                parts.append(region_slug)
            parts.extend([topic_slug, entry["slug"]])
            out_dir = Path(*parts)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html, encoding="utf-8")
            counts["pages"] += 1
            written_slugs.add(entry["slug"])

        if topic_had_entries:
            counts["topics"] += 1

        # Prune orphans: every entity dir under content/<country>/<city>/<topic>/
        # whose slug isn't in this run's written set.
        #
        # Reserve a few non-entity sub-paths so they survive pruning:
        # - dietary diet categories (vegan/, vegetarian/, gluten-free/,
        #   halal/, kosher/) are written by generate_city_dietary.py
        #   and live in the same topic dir as dietary entities.
        topic_dir_parts = [CONTENT_DIR, country_slug]
        if region_slug:
            topic_dir_parts.append(region_slug)
        topic_dir_parts.append(topic_slug)
        topic_dir = Path(*topic_dir_parts)
        reserved: set[str] = set()
        if topic_slug == "dietary":
            reserved |= {"vegan", "vegetarian", "gluten-free", "halal", "kosher"}
        if topic_slug == "nightlife":
            reserved |= {"dance-clubs", "live-music", "rooftop-bars", "speakeasies", "lgbtq", "listening-bars", "late-night-dives"}
        if topic_dir.exists():
            for sub in topic_dir.iterdir():
                if sub.is_dir() and sub.name not in written_slugs and sub.name not in reserved:
                    _shutil.rmtree(sub)
                    counts["pruned"] += 1

    return counts


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("country_slug", nargs="?")
    p.add_argument("city_slug", nargs="?")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    targets: list = []
    if args.all:
        for country in get_all_countries():
            for region in get_all_regions(country):
                targets.append((country, region))
            # also country-level (if it has data)
            from utils.data_loader import SITE_DATA
            if (SITE_DATA / country / "data" / "region.json").exists():
                targets.append((country, None))
    elif args.country_slug:
        targets.append((args.country_slug, args.city_slug))
    else:
        p.error("Pass <country> <city> or --all")
        return 2

    grand = {"pages": 0, "topics": 0, "skipped_no_slug": 0, "pruned": 0, "cities": 0}
    for country, region in targets:
        label = f"{country}/{region}" if region else country
        print(f"{label}")
        counts = generate_for_city(country, region)
        for k in ("pages", "topics", "skipped_no_slug", "pruned"):
            grand[k] += counts[k]
        grand["cities"] += 1
        print(f"  pages={counts['pages']}  topics_with_entities={counts['topics']}  skipped_no_slug={counts['skipped_no_slug']}  pruned={counts['pruned']}")

    print(f"\nDONE: {grand['cities']} cities, {grand['pages']} entity pages, {grand['topics']} topics covered, {grand['pruned']} stale pages pruned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
