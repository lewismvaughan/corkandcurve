#!/usr/bin/env python3
"""Generate per-city topic × day-of-week / time-of-day rollup pages.

For every (city, topic, when-pattern) with >= MIN_ENTITIES entities,
emit a hyper-targeted long-tail page:

  /<country>/<city>/brunch/sunday/         (brunch places open Sundays)
  /<country>/<city>/brunch/saturday/       (brunch places open Saturdays)
  /<country>/<city>/restaurants/sunday/    ("sunday dinner <city>")
  /<country>/<city>/restaurants/monday/    (Monday is the closed day in
                                            many cities — these are the
                                            exceptions)
  /<country>/<city>/cafes/sunday/
  /<country>/<city>/bakeries/sunday/
  /<country>/<city>/bars/late/             (bars open past 23:00)
  /<country>/<city>/bars/weekend-late/     (Fri/Sat past 01:00)
  /<country>/<city>/late-night/weekend/    (late-night topic, weekend
                                            availability confirmed)

Walks entity.hours strings, extracts day-set + latest close time per
weekday with a tolerant regex parser. False-positives are fine — we
exclude entities only when the parser is confident they're CLOSED on
that day.

Re-runnable; rewrites every page each run; prunes stale leaves.

Usage:
    python scripts/generate_city_topic_when.py
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
from utils.filter_search import filter_search_widget  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
CONTENT = REPO_ROOT / "content"
BASE = "https://tablejourney.com"

MIN_ENTITIES = 3

# Topic + when-pattern combinations to emit.
# `pattern_fn(parsed_hours)` returns True if the entity qualifies.
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _is_open_day(parsed: dict, day: str) -> bool:
    """Returns True only when the parser is CONFIDENT the entity is open
    that day. If we can't parse the hours at all, return False (safer
    to under-include than to fabricate)."""
    if not parsed or "days_open" not in parsed:
        return False
    return day in parsed["days_open"]


def _is_open_late(parsed: dict, day: str | None = None) -> bool:
    """Open past 23:00 on any day (or specific day if given)."""
    if not parsed:
        return False
    late = parsed.get("late_close_days") or set()
    if day is None:
        return bool(late)
    return day in late


def _is_open_past_midnight(parsed: dict, day: str | None = None) -> bool:
    past = (parsed or {}).get("past_midnight_days") or set()
    if day is None:
        return bool(past)
    return day in past


# (topic_slug, when_slug, display, requirement_fn, blurb)
PATTERNS = [
    ("restaurants", "sunday",     "Sunday Dinner",
     lambda h: _is_open_day(h, "sun"),
     "where to eat a sit-down dinner on Sunday."),
    ("restaurants", "monday",     "Monday Dinner",
     lambda h: _is_open_day(h, "mon"),
     "open on Monday — the day most kitchens go dark."),
    ("brunch",      "saturday",   "Saturday Brunch",
     lambda h: _is_open_day(h, "sat"),
     "the Saturday brunch spots worth queuing for."),
    ("brunch",      "sunday",     "Sunday Brunch",
     lambda h: _is_open_day(h, "sun"),
     "the Sunday brunch destinations editors return to."),
    ("cafes",       "sunday",     "Cafes Open Sunday",
     lambda h: _is_open_day(h, "sun"),
     "cafes serving on Sundays."),
    ("bakeries",    "sunday",     "Bakeries Open Sunday",
     lambda h: _is_open_day(h, "sun"),
     "bakeries baking on Sundays."),
    ("bars",        "late",       "Bars Open Late",
     lambda h: _is_open_late(h),
     "bars serving past 23:00."),
    ("bars",        "weekend-late","Bars Open Past Midnight Friday or Saturday",
     lambda h: _is_open_past_midnight(h, "fri") or _is_open_past_midnight(h, "sat"),
     "bars going past midnight on Friday or Saturday."),
    ("late-night",  "weekend",    "Late-Night Weekend Eats",
     lambda h: _is_open_late(h, "fri") or _is_open_late(h, "sat"),
     "where to eat past midnight on a weekend night."),
]


# Day name → canonical key
_DAY_MAP = {
    "monday": "mon", "mon": "mon", "m": "mon",
    "tuesday": "tue", "tues": "tue", "tue": "tue", "tu": "tue",
    "wednesday": "wed", "weds": "wed", "wed": "wed", "w": "wed",
    "thursday": "thu", "thurs": "thu", "thu": "thu", "th": "thu",
    "friday": "fri", "fri": "fri", "f": "fri",
    "saturday": "sat", "sat": "sat", "s": "sat",
    "sunday": "sun", "sun": "sun", "su": "sun",
}


def _day_range(start: str, end: str) -> list[str]:
    s = _DAY_MAP.get(start.lower())
    e = _DAY_MAP.get(end.lower())
    if not s or not e:
        return []
    si = DAYS.index(s)
    ei = DAYS.index(e)
    if si <= ei:
        return DAYS[si:ei + 1]
    # wrap (e.g. fri-mon) — return start-week-end + week-start-end
    return DAYS[si:] + DAYS[:ei + 1]


_TIME_RE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?")
_RANGE_RE = re.compile(
    r"(?P<dstart>[a-z]+)\s*[-–—]\s*(?P<dend>[a-z]+)"
)


def _parse_time(s: str) -> int | None:
    """Return hour-of-day 0-47 (cross-midnight uses 24+).
    Returns None when the string isn't a time."""
    if not s:
        return None
    m = _TIME_RE.match(s.strip())
    if not m:
        return None
    h = int(m.group(1))
    ampm = (m.group(3) or "").lower()
    if ampm == "pm" and h < 12:
        h += 12
    elif ampm == "am" and h == 12:
        h = 0
    return h


def _parse_hours(raw: str) -> dict:
    """Parse the entity.hours string into a structured dict:
       {days_open: set[str], late_close_days: set[str], past_midnight_days: set[str]}
    The parser is tolerant — falls back to days_open=∅ when shape is unrecognized."""
    if not isinstance(raw, str) or not raw.strip():
        return {}
    text = raw.lower()
    days_open: set[str] = set()
    late: set[str] = set()
    past_mid: set[str] = set()

    # Daily-everything
    if re.search(r"\b(daily|every day|7 days|7\s*-?\s*days|7\s*nights)\b", text):
        days_open = set(DAYS)
        # Extract late close from the time tail if present
        tail = re.search(r"-(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
        if tail:
            end_h = _parse_time(f"{tail.group(1)}:{tail.group(2) or '00'} {tail.group(3) or ''}")
            if end_h is not None:
                if end_h >= 23 or end_h < 6:
                    late = set(DAYS)
                if end_h < 6:
                    past_mid = set(DAYS)
        return {"days_open": days_open, "late_close_days": late, "past_midnight_days": past_mid}

    # Split into clauses
    clauses = re.split(r"[,;]", text)
    for clause in clauses:
        c = clause.strip()
        if not c or "closed" in c:
            continue
        # Day range first
        rng = _RANGE_RE.search(c)
        clause_days: set[str] = set()
        if rng:
            clause_days.update(_day_range(rng.group("dstart"), rng.group("dend")))
        # Individual day mentions (run after range so we catch standalone days too)
        for token in re.findall(r"\b([a-z]+)\b", c):
            if token in _DAY_MAP:
                clause_days.add(_DAY_MAP[token])
        if not clause_days:
            continue
        days_open.update(clause_days)
        # Extract close time
        close_match = re.search(r"-\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", c)
        if close_match:
            close_str = f"{close_match.group(1)}:{close_match.group(2) or '00'} {close_match.group(3) or ''}"
            end_h = _parse_time(close_str)
            if end_h is not None:
                if end_h >= 23 or end_h < 6:
                    late.update(clause_days)
                if end_h < 6:
                    past_mid.update(clause_days)
    return {"days_open": days_open, "late_close_days": late, "past_midnight_days": past_mid}


def _country_display(slug: str) -> str:
    return {
        "usa": "USA", "united-states": "United States", "united-kingdom": "United Kingdom",
    }.get(slug, slug.replace("-", " ").title())


# Entity-list keys per topic
TOPIC_KEYS = {
    "restaurants": "restaurants",
    "fine-dining": "fine_dining",
    "casual-dining": "casual_dining",
    "brunch": "brunch",
    "cafes": "cafes",
    "bakeries": "bakeries",
    "coffee-roasters": "coffee_roasters",
    "bars": "bars",
    "wine-bars": "wine_bars",
    "late-night": "late_night",
    "street-food": "street_food",
}


def _extract_price_int(e: dict) -> int | None:
    """Mirror of TemplateRenderer._price_to_int for sort widget consistency."""
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
    hours = html.escape(e.get("hours", "")) if e.get("hours") else ""
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
    parts = [title_html, f'<h3 class="tj-entity-name">{name}{score_html}</h3>']
    if locale:
        parts.append(f'<p class="tj-entity-locale">{locale}</p>')
    if hours:
        parts.append(f'<p class="tj-entity-locale"><strong>Hours:</strong> {hours}</p>')
    if desc:
        parts.append(f'<p class="tj-entity-desc">{desc}</p>')
    if e.get("tip"):
        parts.append(f'<p class="tj-entity-desc"><strong>Tip:</strong> {html.escape(e["tip"])}</p>')
    parts.append(closer)
    return "".join(parts)


def _render(renderer: TemplateRenderer, *, country_slug: str, country_name: str,
            city_slug: str, city_name: str, topic_slug: str, when_slug: str,
            when_display: str, blurb: str, entries: list[dict],
            other_patterns_for_topic: list[tuple[str, str]]) -> Path:
    n = len(entries)
    canonical = f"{BASE}/{country_slug}/{city_slug}/{topic_slug}/{when_slug}/"
    topic_display = topic_slug.replace("-", " ").title()
    title = f"{when_display} in {city_name}: {n} editor picks | TableJourney"
    description = (
        f"{n} {topic_display.lower()} in {city_name} that are open as needed for "
        f"{when_display.lower()}, editor-picked. {blurb.capitalize()}"
    )
    if len(description) > 165:
        description = description[:162].rsplit(" ", 1)[0] + "..."

    cards_html = "".join(_entity_card(e, country_slug, city_slug, topic_slug) for e in entries)

    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": f"{when_display} in {city_name}", "numberOfItems": n,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "url": f"https://tablejourney.com/{country_slug}/{city_slug}/{topic_slug}/{e.get('slug','')}/",
             "name": e.get("name", "")}
            for i, e in enumerate(entries, start=1) if e.get("slug")
        ],
    }
    itemlist_html = '<script type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":")) + '</script>'

    # Sibling when-pattern cross-links for this topic
    cross_html = ""
    if other_patterns_for_topic:
        items_html = "".join(
            f'<li><a href="/{country_slug}/{city_slug}/{topic_slug}/{ws}/">{wd} in {city_name}</a></li>'
            for ws, wd in other_patterns_for_topic
        )
        cross_html = (
            '<div class="tj-cross-links" style="margin:24px 0 8px; padding:14px; '
            'background:var(--tj-surface); border:1px solid var(--tj-border); border-radius:var(--tj-radius);">'
            f'<h3 style="margin:0 0 8px; font-size:1rem;">More {topic_display.lower()} timing guides in {city_name}</h3>'
            f'<ul class="tj-sidebar-list" style="margin:0;">{items_html}</ul></div>'
        )

    body_html = (
        f'<p class="tj-topic-headline">'
        f'<strong>{n}</strong> {topic_display.lower()} in {city_name}, editor-picked for {when_display.lower()}. '
        f'{blurb.capitalize()} <a href="/{country_slug}/{city_slug}/{topic_slug}/">All {topic_display.lower()} in {city_name}</a>.'
        f'</p>'
        + filter_search_widget(target_id="tj-entity-list", item_selector=".tj-entity-card",
                                placeholder="Filter by name, neighborhood…",
                                aria_label=f"Filter {when_display.lower()}")
        + f'<div id="tj-entity-list" class="tj-entity-grid">{cards_html}</div>'
        + cross_html + itemlist_html
    )
    breadcrumb = [
        {"position": 1, "name": "Home", "url": f"{BASE}/"},
        {"position": 2, "name": country_name, "url": f"{BASE}/{country_slug}/"},
        {"position": 3, "name": city_name, "url": f"{BASE}/{country_slug}/{city_slug}/"},
        {"position": 4, "name": topic_display, "url": f"{BASE}/{country_slug}/{city_slug}/{topic_slug}/"},
        {"position": 5, "name": when_display, "url": None},
    ]
    page_ctx = {
        "title": title, "meta_description": description,
        "h1": f"{when_display} in {city_name}",
        "subtitle": f"{n} editor-picked rooms in {city_name}.",
        "canonical_url": canonical, "body_html": body_html,
        "breadcrumb_items": breadcrumb, "page_type": "collection",
        "updated": "May 2026", "modified": "2026-05-20",
    }
    seo = {
        "meta": {"title": title, "description": description, "canonical_url": canonical,
                 "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"},
        "open_graph": {"og_title": title, "og_description": description, "og_url": canonical,
                       "og_type": "website", "og_image": "https://tablejourney.com/og/default.jpg",
                       "og_image_alt": "TableJourney food guide", "og_locale": "en_US"},
        "twitter": {"twitter_title": title, "twitter_description": description},
        "structured_data": {"breadcrumb_items": breadcrumb}, "alternates": [],
    }
    template = renderer.env.get_template("chrome/page.html")
    out = CONTENT / country_slug / city_slug / topic_slug / when_slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.render(
        page=page_ctx, seo=seo,
        analytics={"page_type": "city-topic-when", "destination": f"{city_slug}-{topic_slug}-{when_slug}"},
        base_path="", topic_nav=FOOD_TOPIC_NAV, breadcrumb=breadcrumb, current_year=2026,
    ), encoding="utf-8")
    return out


def _inject_when_block_into_parent(*, country_slug: str, city_slug: str,
                                    topic_slug: str, city_name: str,
                                    patterns: list[tuple[str, str]]) -> None:
    """Patch /<country>/<city>/<topic>/index.html to link DOWN to the
    when-pattern sub-pages we just emitted. No-orphan wiring."""
    if not patterns:
        return
    idx = CONTENT / country_slug / city_slug / topic_slug / "index.html"
    if not idx.exists():
        return
    items = "".join(
        f'<li><a href="/{country_slug}/{city_slug}/{topic_slug}/{ws}/">'
        f'{html.escape(wd)} in {html.escape(city_name)}</a></li>'
        for ws, wd in patterns
    )
    block = (
        '<!-- when-block -->'
        '<section class="tj-section" id="when-to-go">'
        f'<h2>By when you want to eat</h2>'
        f'<ul class="tj-grid-list">{items}</ul>'
        '</section>'
        '<!-- /when-block -->'
    )
    src = idx.read_text(encoding="utf-8")
    start = src.find("<!-- when-block -->")
    end = src.find("<!-- /when-block -->")
    if start != -1 and end != -1:
        idx.write_text(src[:start] + block + src[end + len("<!-- /when-block -->"):], encoding="utf-8")
        return
    marker = "</main>"
    pos = src.rfind(marker)
    if pos == -1:
        marker = "</article>"
        pos = src.rfind(marker)
    if pos == -1:
        marker = "</body>"
        pos = src.rfind(marker)
    if pos == -1:
        return
    idx.write_text(src[:pos] + block + src[pos:], encoding="utf-8")


def main() -> int:
    renderer = TemplateRenderer()
    written: set[Path] = set()
    inject_queue: dict[tuple[str, str, str, str], list[tuple[str, str]]] = defaultdict(list)

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
                hub = CONTENT / country_slug / city_slug / "index.html"
                if not hub.exists():
                    continue
            city_name = region.get("destination", {}).get("name") or city_slug.replace("-", " ").title()

            # First pass: figure out which patterns clear MIN_ENTITIES
            # per (topic, pattern) so we can render sibling-cross-links.
            cleared_by_topic: dict[str, list[tuple[str, str]]] = defaultdict(list)
            buckets: dict[tuple[str, str], list[dict]] = {}
            for topic_slug, when_slug, when_display, fn, blurb in PATTERNS:
                key = TOPIC_KEYS.get(topic_slug)
                if not key:
                    continue
                p = city_dir / "data" / (topic_slug + ".json")
                if not p.exists():
                    continue
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                items = d.get(key) or []
                matching = []
                for e in items:
                    if not isinstance(e, dict):
                        continue
                    parsed = _parse_hours(e.get("hours", ""))
                    if fn(parsed):
                        matching.append(e)
                if len(matching) >= MIN_ENTITIES:
                    matching.sort(key=lambda x: x.get("editorial_score", 0) or 0, reverse=True)
                    buckets[(topic_slug, when_slug)] = matching
                    cleared_by_topic[topic_slug].append((when_slug, when_display))

            for (topic_slug, when_slug), entries in buckets.items():
                when_display = next(p[2] for p in PATTERNS if p[0] == topic_slug and p[1] == when_slug)
                blurb = next(p[4] for p in PATTERNS if p[0] == topic_slug and p[1] == when_slug)
                others = [t for t in cleared_by_topic[topic_slug] if t[0] != when_slug]
                p = _render(renderer,
                            country_slug=country_slug, country_name=country_name,
                            city_slug=city_slug, city_name=city_name,
                            topic_slug=topic_slug, when_slug=when_slug,
                            when_display=when_display, blurb=blurb, entries=entries,
                            other_patterns_for_topic=others)
                written.add(p)
                inject_queue[(country_slug, city_slug, topic_slug, city_name)].append((when_slug, when_display))

    # Inject "By when" link blocks into each parent topic chapter page
    # so the new when-pattern sub-pages aren't orphan.
    for (cs, cy, ts, cn), patterns in inject_queue.items():
        _inject_when_block_into_parent(country_slug=cs, city_slug=cy,
                                        topic_slug=ts, city_name=cn,
                                        patterns=sorted(patterns))

    # Prune stale (city, topic, when) pages — only known when-slugs under
    # known topic dirs to avoid collateral damage.
    known_when_slugs = {p[1] for p in PATTERNS}
    pruned = 0
    for country_dir in CONTENT.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            for topic_dir in city_dir.iterdir():
                if not topic_dir.is_dir() or topic_dir.name not in TOPIC_KEYS:
                    continue
                for when_dir in topic_dir.iterdir():
                    if not when_dir.is_dir() or when_dir.name not in known_when_slugs:
                        continue
                    idx = when_dir / "index.html"
                    if idx.exists() and idx not in written:
                        shutil.rmtree(when_dir)
                        pruned += 1

    print(f"wrote {len(written)} city × topic × time-of-day pages")
    if pruned:
        print(f"pruned {pruned} stale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
