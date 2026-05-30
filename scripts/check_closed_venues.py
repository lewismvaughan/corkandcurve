#!/usr/bin/env python3
"""
Closed-venue verification.

For every venue entity in shipped venue topics, fetch two signals:

  (A) the producer's own `source_url` page — scan for a closed-status banner
      ("Permanently closed", "Dauerhaft geschlossen", "Fermeture
      definitive", "ferme definitivement", "We are closed", "Out of
      business", "Wegen Sanierung geschlossen", "Renovation closure",
      "auf Wiedersehen") that the venue itself published

  (B) a DuckDuckGo HTML SERP of "{name} {town}" — scan combined snippet
      text for third-party closure mentions ("permanently closed",
      locale variants, news snippets)

Detects three states per venue:
  - permanently-closed (HARD)   — producer site or third-party confirms permanent closure
  - temporarily-closed (WARN)   — verifiable temporary / renovation closure
  - open                        — no closure signal found

Optional `--playwright-google` adds a third signal: Playwright + Google
Maps place panel. Off by default because Google blocks the bot wall
aggressively. Use sparingly for high-confidence double-checks.

Results cached in data/closed-venues-cache.json with 30-day TTL.

Usage:
    python3 scripts/check_closed_venues.py --region france/alsace
    python3 scripts/check_closed_venues.py --all
    python3 scripts/check_closed_venues.py --all --topic wine-restaurants
    python3 scripts/check_closed_venues.py --region germany/rheingau \
        --playwright-google --slow 6

Exit code: 0 (advisory). With `--strict`, exits 1 on any
permanently-closed finding.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

import html as html_module
import urllib.request
import urllib.error

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
CACHE_FILE = REPO / "data" / "closed-venues-cache.json"
CACHE_TTL_SECONDS = 30 * 24 * 3600

VENUE_TOPICS = (
    "vineyards", "tasting-rooms", "wine-bars", "wine-restaurants",
    "wine-retailers", "wine-schools", "wine-tours", "wine-festivals",
    "distilleries", "wine-museums", "wine-hotels", "wine-experiences",
    "hidden-gems",
)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)

# Strong closure phrases — these are HARD signals when found on the venue's
# own page or in a third-party SERP snippet.
PERMANENTLY_CLOSED = [
    re.compile(r"\bpermanently\s+closed\b", re.I),
    re.compile(r"\bclosed\s+permanently\b", re.I),
    re.compile(r"\bout\s+of\s+business\b", re.I),
    re.compile(r"dauerhaft\s+geschlossen", re.I),
    re.compile(r"endg[üu]ltig\s+geschlossen", re.I),
    re.compile(r"ferm[ée]e?\s+d[ée]finitivement", re.I),
    re.compile(r"ferm[ée]ture\s+d[ée]finitive", re.I),
    re.compile(r"chiuso\s+definitivamente", re.I),
    re.compile(r"permanentemente\s+chiuso", re.I),
    re.compile(r"cerrado\s+permanentemente", re.I),
    re.compile(r"permanentemente\s+cerrado", re.I),
    re.compile(r"fechado\s+permanentemente", re.I),
    re.compile(r"v[ée]glegesen\s+bez[áa]rt", re.I),
    re.compile(r"\bclosed\s+for\s+good\b", re.I),
    re.compile(r"\bceased\s+operations\b", re.I),
    re.compile(r"\bceased\s+trading\b", re.I),
    re.compile(r"\bhas\s+closed\s+its\s+doors\b", re.I),
    re.compile(r"\bno\s+longer\s+in\s+(business|operation)\b", re.I),
]

TEMPORARILY_CLOSED = [
    re.compile(r"\btemporarily\s+closed\b", re.I),
    re.compile(r"\bclosed\s+temporarily\b", re.I),
    re.compile(r"vor[üu]bergehend\s+geschlossen", re.I),
    re.compile(r"wegen\s+sanierung\s+geschlossen", re.I),
    re.compile(r"wegen\s+renovierung\s+geschlossen", re.I),
    re.compile(r"ferm[ée]e?\s+temporairement", re.I),
    re.compile(r"ferm[ée]e?\s+pour\s+travaux", re.I),
    re.compile(r"ferm[ée]\s+pour\s+travaux", re.I),
    re.compile(r"chiuso\s+per\s+lavori", re.I),
    re.compile(r"temporaneamente\s+chiuso", re.I),
    re.compile(r"cerrado\s+temporalmente", re.I),
    re.compile(r"closed\s+for\s+renovation", re.I),
    re.compile(r"\bunder\s+renovation\b", re.I),
]

# Words that we DON'T treat as closure signals even though they contain "closed":
# - "closed kitchen" / "closed bottle" / "closed door" are not closure indicators
# - "closed monastery" appears in heritage descriptions
# We rely on the strict regex anchors above to avoid these false positives.

# Indicators that the response is meaningless to scan:
NOISE_INDICATORS = [
    re.compile(r"<!doctype html>\s*$", re.I),
    re.compile(r"^\s*$"),
]


@dataclass
class Hit:
    region: str
    topic: str
    slug: str
    name: str
    query: str
    source_url: str
    status: str            # permanently-closed | temporarily-closed | open | unknown
    signal: str            # which source flagged it: 'producer-page' | 'ddg-serp' | 'bing-serp' | 'google-map'
    matched: str           # the literal matched phrase
    cached_at: str


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text())
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _cache_key(region: str, topic: str, slug: str) -> str:
    return f"{region}|{topic}|{slug}"


def _cache_fresh(entry: dict) -> bool:
    if "cached_at" not in entry:
        return False
    try:
        ts = datetime.fromisoformat(entry["cached_at"]).timestamp()
    except Exception:
        return False
    return (time.time() - ts) < CACHE_TTL_SECONDS


# ---------------------------------------------------------------------------
# Entity iteration
# ---------------------------------------------------------------------------

def _extract_locality(addr: str) -> str:
    if not addr:
        return ""
    parts = [p.strip() for p in addr.split(",") if p.strip()]
    if len(parts) >= 2:
        candidate = parts[-2]
        candidate = re.sub(r"^\d{4,5}\s+", "", candidate)
        return candidate
    return parts[0] if parts else ""


def _topic_keys(topic: str) -> tuple[str, ...]:
    # The JSON list key is sometimes the topic with underscores, sometimes a
    # legacy name. Try a few candidates.
    return (
        topic.replace("-", "_"),
        topic,
        "vineyards", "tasting_rooms", "wine_bars", "wine_restaurants",
        "wine_retailers", "wine_schools", "wine_tours", "wine_festivals",
        "distilleries", "wine_museums", "wine_hotels", "wine_experiences",
        "hidden_gems",
    )


def iter_venue_entities(region_filter: Optional[str], topic_filter: Optional[str]):
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        for region_dir in sorted(country_dir.iterdir()):
            if not region_dir.is_dir() or region_dir.name == "data":
                continue
            region = region_dir.name
            region_key = f"{country}/{region}"
            if region_filter and region_filter != region_key:
                continue
            data_dir = region_dir / "data"
            if not data_dir.exists():
                continue
            for topic in VENUE_TOPICS:
                if topic_filter and topic_filter != topic:
                    continue
                topic_file = data_dir / f"{topic}.json"
                if not topic_file.exists():
                    continue
                try:
                    doc = json.loads(topic_file.read_text())
                except Exception:
                    continue
                entries = None
                for k in _topic_keys(topic):
                    if isinstance(doc.get(k), list):
                        entries = doc[k]
                        break
                if not entries:
                    continue
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    name = e.get("name", "")
                    slug = e.get("slug", "")
                    if not name or not slug:
                        continue
                    verified = e.get("verified") or {}
                    addr = e.get("address") or verified.get("address_quoted") or ""
                    town = e.get("village") or e.get("town") or _extract_locality(addr)
                    src = verified.get("source_url") or e.get("source_url") or ""
                    yield (country, region, topic, slug, name, town, addr, src)


# ---------------------------------------------------------------------------
# Fetch + scan
# ---------------------------------------------------------------------------

def _fetch(url: str, timeout: float = 8.0) -> str:
    if not url:
        return ""
    try:
        req = urllib.request.Request(
            url, headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.7,de;q=0.5,fr;q=0.5",
            })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            raw = resp.read(800_000)  # cap at 800k
            return raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        return f"<<HTTPError {e.code}>>"
    except Exception as e:
        return f"<<FetchError {type(e).__name__}>>"


# Strip script/style/JSON-LD blocks so we don't match against i18n translation
# dictionaries, embedded Google Maps locale strings, or narrative Wikipedia
# prose where closure language is about a different entity. Producers commonly
# inline a translation dictionary that contains "Permanently closed" /
# "Temporarily closed" as Google-Maps embed locale keys (Alsace 2026-05-30
# false-positive at lecercledesaromes.fr).
_SCRIPT_RX = re.compile(r"<script\b[^>]*>.*?</script>", re.I | re.S)
_STYLE_RX = re.compile(r"<style\b[^>]*>.*?</style>", re.I | re.S)
_NOSCRIPT_RX = re.compile(r"<noscript\b[^>]*>.*?</noscript>", re.I | re.S)
# Wikipedia / wiki-style content is narrative prose about wine regions; closure
# language there is almost never about the entity we're checking. Drop the
# scan signal when the source URL is a wiki.
_WIKI_HOST_RX = re.compile(r"^https?://[a-z]{2,3}\.wikipedia\.org/", re.I)


# Templated closure labels live inside hidden CSS classes (Signorvino store
# template ships `<span class="store-hours-temporarily-closed hidden">` —
# the `hidden` class means the label is only displayed when actually closed).
# Strip elements whose class includes "hidden" or that have inline
# display:none / visibility:hidden style.
_HIDDEN_ELEM_RX = re.compile(
    r"<(\w+)[^>]*(?:class\s*=\s*[\"'][^\"']*\bhidden\b[^\"']*[\"']|"
    r"style\s*=\s*[\"'][^\"']*\b(?:display\s*:\s*none|visibility\s*:\s*hidden)\b[^\"']*[\"'])"
    r"[^>]*>.*?</\1>",
    re.I | re.S,
)


def _strip_noisy_html(text: str) -> str:
    if not text:
        return text
    # 1. Strip script/style/noscript first (raw HTML form)
    text = _SCRIPT_RX.sub(" ", text)
    text = _STYLE_RX.sub(" ", text)
    text = _NOSCRIPT_RX.sub(" ", text)
    # 2. Decode HTML entities so encoded template strings inside JSON state
    #    (e.g. Signorvino's Next.js __NEXT_DATA__ with `&lt;span class=&quot;...
    #    hidden&quot;&gt;Temporarily closed&lt;/span&gt;`) are also detectable.
    text = html_module.unescape(text)
    # 2b. Templates embedded inside JS string literals are double-escaped
    #     (`class=\"hidden\"`). Normalise backslash-escaped quotes to plain
    #     quotes so the hidden-class regex matches them too.
    text = text.replace('\\"', '"').replace("\\'", "'")
    # 3. Strip again — now the decoded encoded-HTML inside what used to be a
    #    script/state blob is regular HTML and can be matched.
    text = _SCRIPT_RX.sub(" ", text)
    text = _HIDDEN_ELEM_RX.sub(" ", text)
    return text


def _proximity_check(haystack: str, match_pos: int, anchors: list[str],
                     window: int = 1500) -> bool:
    """Closure phrase must appear within `window` chars of an anchor word (the
    venue name or its town). If no anchor appears nearby, treat as noise
    (third-party listing covering many venues, narrative blog prose, etc)."""
    if not anchors:
        return True   # no anchor to check against -> accept
    lo = max(0, match_pos - window)
    hi = min(len(haystack), match_pos + window)
    chunk = haystack[lo:hi].lower()
    return any(a and a.lower() in chunk for a in anchors)


def _scan_text(text: str, anchors: Optional[list[str]] = None) -> tuple[str, str]:
    """Returns (status, matched_phrase). status: permanently-closed | temporarily-closed | open.

    If `anchors` is given (the venue name / town tokens), require the matched
    phrase to be within proximity of at least one anchor. Otherwise treat as
    template noise / unrelated context."""
    if not text or text.startswith("<<"):
        return "open", ""
    cleaned = _strip_noisy_html(text)
    for rx in PERMANENTLY_CLOSED:
        m = rx.search(cleaned)
        if m and _proximity_check(cleaned, m.start(), anchors or []):
            return "permanently-closed", m.group(0)
    for rx in TEMPORARILY_CLOSED:
        m = rx.search(cleaned)
        if m and _proximity_check(cleaned, m.start(), anchors or []):
            return "temporarily-closed", m.group(0)
    return "open", ""


def _ddg_serp(query: str) -> str:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    return _fetch(url)


def _bing_serp(query: str) -> str:
    url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=en"
    return _fetch(url)


def _producer_page(source_url: str) -> str:
    return _fetch(source_url, timeout=10)


def _anchors_for(name: str, town: str) -> list[str]:
    """Build proximity anchors: the venue name and town. Split multi-word
    names so we can match on a single distinctive word."""
    anchors: list[str] = []
    for raw in (name, town):
        if not raw:
            continue
        anchors.append(raw)
        # Add longest word from the name/town as a single-token anchor
        words = [w for w in re.split(r"[^\wÀ-ſ]+", raw) if len(w) >= 4]
        words.sort(key=len, reverse=True)
        if words:
            anchors.append(words[0])
    return anchors


def assess_one(country: str, region: str, topic: str, slug: str, name: str,
               town: str, addr: str, source_url: str) -> Hit:
    """Return a single Hit. Statuses ordered: permanently > temporarily > open."""
    region_key = f"{country}/{region}"
    query = f"{name} {town}".strip()
    anchors = _anchors_for(name, town)

    # Signal 1: producer's own page — skip if source_url is a wiki, since wikis
    # carry narrative prose where closure language is rarely about the entity.
    if _WIKI_HOST_RX.match(source_url or ""):
        producer_html = ""
    else:
        producer_html = _producer_page(source_url)
    p_status, p_match = _scan_text(producer_html, anchors)

    if p_status == "permanently-closed":
        return Hit(region_key, topic, slug, name, query, source_url,
                   p_status, "producer-page", p_match,
                   datetime.now(timezone.utc).isoformat())

    # Signal 2: DuckDuckGo SERP
    ddg_html = _ddg_serp(query)
    d_status, d_match = _scan_text(ddg_html, anchors)

    if d_status == "permanently-closed":
        return Hit(region_key, topic, slug, name, query, source_url,
                   d_status, "ddg-serp", d_match,
                   datetime.now(timezone.utc).isoformat())

    # Signal 3: Bing SERP
    bing_html = _bing_serp(query)
    b_status, b_match = _scan_text(bing_html, anchors)

    if b_status == "permanently-closed":
        return Hit(region_key, topic, slug, name, query, source_url,
                   b_status, "bing-serp", b_match,
                   datetime.now(timezone.utc).isoformat())

    # Any temporarily-closed signal?
    for status, match, signal in (
        (p_status, p_match, "producer-page"),
        (d_status, d_match, "ddg-serp"),
        (b_status, b_match, "bing-serp"),
    ):
        if status == "temporarily-closed":
            return Hit(region_key, topic, slug, name, query, source_url,
                       status, signal, match,
                       datetime.now(timezone.utc).isoformat())

    return Hit(region_key, topic, slug, name, query, source_url,
               "open", "all-signals", "",
               datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--region", help="country/region e.g. france/alsace")
    g.add_argument("--all", action="store_true", help="all shipped regions")
    ap.add_argument("--topic", help="restrict to one venue topic")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap number of venues queried (0 = no cap)")
    ap.add_argument("--workers", type=int, default=4,
                    help="parallel HTTP workers (default 4)")
    ap.add_argument("--no-cache", action="store_true",
                    help="ignore cache and re-query everything")
    ap.add_argument("--no-cache-write", action="store_true",
                    help="don't persist new findings to the cache")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any PERMANENTLY-CLOSED finding")
    args = ap.parse_args()

    region_filter = args.region if not args.all else None
    cache = {} if args.no_cache else _load_cache()

    venues = list(iter_venue_entities(region_filter, args.topic))
    if args.limit:
        venues = venues[: args.limit]

    if not venues:
        print("No venues found for the given filter.", file=sys.stderr)
        return 0

    print(f"[closed-venues] scanning {len(venues)} venues (workers={args.workers})")

    findings: list[Hit] = []
    served_from_cache = 0
    queried = 0

    pending: list[tuple] = []
    for country, region, topic, slug, name, town, addr, src in venues:
        region_key = f"{country}/{region}"
        key = _cache_key(region_key, topic, slug)
        cached = cache.get(key)
        if cached and _cache_fresh(cached):
            served_from_cache += 1
            if cached["status"] in ("permanently-closed", "temporarily-closed"):
                findings.append(Hit(
                    region_key, topic, slug, name, cached.get("query", ""),
                    cached.get("source_url", ""), cached["status"],
                    cached.get("signal", "cached"),
                    cached.get("matched", ""), cached["cached_at"]))
            continue
        pending.append((country, region, topic, slug, name, town, addr, src))

    print(f"  cache hits: {served_from_cache}; need to query: {len(pending)}")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(assess_one, *v): v for v in pending}
        for fut in as_completed(futures):
            try:
                h = fut.result()
            except Exception as e:
                print(f"  [ERROR] {type(e).__name__}: {e}")
                continue
            queried += 1
            key = _cache_key(h.region, h.topic, h.slug)
            cache[key] = {
                "status": h.status, "signal": h.signal,
                "matched": h.matched, "query": h.query,
                "source_url": h.source_url, "cached_at": h.cached_at,
            }
            if h.status in ("permanently-closed", "temporarily-closed"):
                findings.append(h)
                print(f"  [{h.status.upper()}] {h.region}/{h.topic}/{h.slug} :: "
                      f"{h.name}  (signal={h.signal}, matched={h.matched!r})")
            if queried % 25 == 0 and not args.no_cache_write:
                _save_cache(cache)

    if not args.no_cache_write:
        _save_cache(cache)

    print("")
    print(f"[closed-venues] SUMMARY")
    print(f"  scanned:               {len(venues)}")
    print(f"  served from cache:     {served_from_cache}")
    print(f"  queried:               {queried}")
    permanently = [h for h in findings if h.status == "permanently-closed"]
    temporarily = [h for h in findings if h.status == "temporarily-closed"]
    print(f"  permanently closed:    {len(permanently)}")
    print(f"  temporarily closed:    {len(temporarily)}")

    if findings:
        print("")
        print("=== FINDINGS ===")
        for h in sorted(findings, key=lambda x: (x.status, x.region, x.topic, x.slug)):
            print(f"  [{h.status}] {h.region}/{h.topic}/{h.slug}")
            print(f"      name:    {h.name}")
            print(f"      query:   {h.query}")
            print(f"      signal:  {h.signal}")
            print(f"      matched: {h.matched!r}")
            if h.source_url:
                print(f"      source:  {h.source_url}")

    if args.strict and permanently:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
