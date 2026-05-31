#!/usr/bin/env python3
"""
Source-URL relevance verification — catches 200-but-unrelated pages.

`check_external_urls.py` HEAD-checks each URL for 4xx/5xx/timeouts but
accepts ANY 200 as healthy. That misses two real defect classes:
  (1) Soft-404 — page returns 200 with "Page not found" body (SPA
      routers, custom WordPress 404 pages).
  (2) Wrong-URL — page returns 200 with substantive content, but the
      content is about a different entity. E.g. Domaine Charvin's
      source_url points at vieux-telegraphe.fr, or molnar-pince points
      at a generic Tokaj tourism index that never mentions Molnar.

For every venue entity (vineyards, wine-restaurants, wine-bars,
wine-hotels, distilleries, wine-museums, wine-retailers, wine-schools,
wine-tours, wine-experiences, tasting-rooms, hidden-gems) — i.e. the
topics whose "name" is a venue name, not a historical-event title — fetch
verified.source_url + open_evidence_url + cuisine_evidence_url and:

  - Check for soft-404 phrases in body text
  - Check whether the venue's distinctive name tokens appear in the page

If NONE of the verified.* URLs both (a) avoid soft-404 markers and
(b) mention the venue name, the entity is flagged. The fix is
researcher-side: replace the wrong source_url with the venue's actual
page, or drop the entity.

Editorial topics (wine-history, seasonal-wine, wine-festivals,
day-trips-wine, signature-grapes, itineraries, nightlife, dietary)
are skipped — their "name" is an event/concept that legitimately may
not appear verbatim on a source page.

Cached in data/source-relevance-cache.json with 30-day TTL.

Usage:
    python3 scripts/check_source_relevance.py --region france/rhone
    python3 scripts/check_source_relevance.py --all
    python3 scripts/check_source_relevance.py --region germany/rheingau --strict
"""
from __future__ import annotations

import argparse
import html as html_module
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
CACHE_FILE = REPO / "data" / "source-relevance-cache.json"
CACHE_TTL_SECONDS = 30 * 24 * 3600

# Topics whose "name" is a venue name (so we can look for the name on the
# producer page). Editorial topics get skipped.
VENUE_TOPICS = (
    "vineyards", "tasting-rooms", "wine-bars", "wine-restaurants",
    "wine-retailers", "wine-schools", "wine-tours",
    "distilleries", "wine-museums", "wine-hotels", "wine-experiences",
    "hidden-gems",
)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)

# Bot-challenge pages return 200 + body like "security check / please enable
# javascript" rather than the real content. They aren't soft-404s and they
# aren't wrong-URL — the URL is correct, the bot just can't see the content.
# Skip these and report 'bot-wall' so they're not conflated with real defects.
BOT_WALL = [
    re.compile(r"security\s+check", re.I),
    re.compile(r"please\s+(?:turn|enable)\s+javascript", re.I),
    re.compile(r"checking\s+(?:your|the)\s+browser", re.I),
    re.compile(r"cloudflare", re.I),
    re.compile(r"verify\s+you\s+are\s+human", re.I),
    re.compile(r"verify\s+you\'?re\s+a\s+human", re.I),
    re.compile(r"je\s+ne\s+suis\s+pas\s+un\s+robot", re.I),
    re.compile(r"test\s+de\s+s[ée]curit[ée]", re.I),
    re.compile(r"unusual\s+traffic", re.I),
    re.compile(r"access\s+denied", re.I),
    re.compile(r"ddos\s+protection", re.I),
]

SOFT_404 = [
    re.compile(r"\b404\s*[-:]?\s*(?:not\s+found|error|page\s+not\s+found)", re.I),
    re.compile(r"\bpage\s+not\s+found\b", re.I),
    re.compile(r"\bseite\s+nicht\s+gefunden\b", re.I),
    re.compile(r"\bpage\s+introuvable\b", re.I),
    re.compile(r"\bpagina\s+non\s+trovata\b", re.I),
    re.compile(r"\bp[áa]gina\s+no\s+encontrada\b", re.I),
    re.compile(r"\bsorry,?\s+(?:we\s+)?(?:can'?t|couldn'?t)\s+find", re.I),
    re.compile(r"\bthe\s+page\s+you\s+(?:are\s+|were\s+)?looking\s+for", re.I),
    re.compile(r"\bno\s+longer\s+available\b", re.I),
    re.compile(r"\bcouldn'?t\s+be\s+found\b", re.I),
    re.compile(r"\bcould\s+not\s+be\s+found\b", re.I),
    re.compile(r"\bdoesn'?t\s+exist\b", re.I),
    re.compile(r"\bdiese\s+seite\s+existiert\s+nicht", re.I),
    re.compile(r"\bcette\s+page\s+n'?existe\s+pas", re.I),
    re.compile(r"\berror\s+404\b", re.I),
    re.compile(r"\boops!?\s+(?:something|the\s+page|that\s+page)", re.I),
]

SCRIPT_RX = re.compile(r"<script\b[^>]*>.*?</script>", re.I | re.S)
STYLE_RX = re.compile(r"<style\b[^>]*>.*?</style>", re.I | re.S)
NAV_RX = re.compile(r"<nav\b[^>]*>.*?</nav>", re.I | re.S)
FOOTER_RX = re.compile(r"<footer\b[^>]*>.*?</footer>", re.I | re.S)
TAG_RX = re.compile(r"<[^>]+>")
WS_RX = re.compile(r"\s+")

# Stopwords that are too common to be a usable name anchor. "Domaine",
# "Weingut", "Cave", "Château", "Maison", "Bodega", "Quinta", "Tenuta",
# "Castello", "Pince", "Estate", "Winery" are wine-industry boilerplate
# that appear on many unrelated pages.
NAME_STOPWORDS = {
    "domaine", "domaines", "weingut", "wein", "winery", "vineyards", "vineyard",
    "estate", "estates", "maison", "cave", "caves", "chateau", "château",
    "schloss", "tenuta", "castello", "bodega", "bodegas", "quinta", "azienda",
    "pince", "borhaz", "cellar", "cellars", "vigna", "tenute", "villa",
    "cantina", "cantine", "podere", "moulin", "champagne", "rheingau", "alsace",
    "vins", "vine", "rosso", "blanco", "noir", "blanc", "rouge", "wine", "wines",
    "vignobles", "vignoble", "vintners", "growers", "winemaker", "winemakers",
    "association", "consortium", "consorzio", "syndicat", "verein", "verband",
    "haus", "hof", "hofgut", "schlossgut", "kellerei", "weinhof", "the",
}


@dataclass
class Hit:
    region: str
    topic: str
    slug: str
    name: str
    status: str        # 'soft-404' | 'name-absent' | 'open' | 'unknown'
    urls_checked: dict   # field -> (http_status, page_status)
    cached_at: str


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


def _fold(text: str) -> str:
    """Lowercase + strip diacritics + normalise German digraphs for fuzzy
    comparison. 'Château Mouton-Rothschild' -> 'chateau mouton-rothschild'.
    'Rüdesheimer Schloss' and 'Ruedesheimer Schloss' both -> 'rudesheimer schloss'."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    folded = "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()
    # German ASCII transliterations: many wine-region sources use ü/ö/ä but
    # our slugs / display names use ue/oe/ae. Normalise both directions to
    # the base letter so fuzzy match works either way.
    folded = (folded
              .replace("ue", "u")
              .replace("oe", "o")
              .replace("ae", "a")
              .replace("ß", "ss"))
    return folded


def _name_tokens(name: str) -> list[str]:
    """Distinctive lowercase tokens of length >= 4 that aren't generic
    wine-industry stopwords. Returns up to the 3 most distinctive."""
    folded = _fold(name)
    raw = [w for w in re.split(r"[^\w]+", folded) if len(w) >= 4]
    tokens = [w for w in raw if w not in NAME_STOPWORDS]
    # If filtering removed everything, fall back to longest non-stopword OR
    # longest raw word so we still have something to match against.
    if not tokens:
        tokens = sorted(raw, key=len, reverse=True)[:3]
    # Prefer longer tokens (more distinctive)
    tokens.sort(key=len, reverse=True)
    return tokens[:3]


def _strip_chrome(text: str) -> str:
    text = SCRIPT_RX.sub(" ", text)
    text = STYLE_RX.sub(" ", text)
    text = NAV_RX.sub(" ", text)
    text = FOOTER_RX.sub(" ", text)
    text = html_module.unescape(text)
    text = TAG_RX.sub(" ", text)
    text = WS_RX.sub(" ", text)
    return text


def _fetch(url: str) -> tuple[str, str]:
    """Returns (http_status_str, cleaned_body)."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.7,de;q=0.5,fr;q=0.5,it;q=0.5,es;q=0.5,hu;q=0.5",
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read(400_000).decode("utf-8", errors="replace")
            return str(r.status), _strip_chrome(raw)[:80_000]
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}", ""
    except Exception as e:
        return f"ERR:{type(e).__name__}", ""


def _scan_bot_wall(body: str) -> Optional[str]:
    if not body:
        return None
    for rx in BOT_WALL:
        m = rx.search(body)
        if m:
            return m.group(0)[:60]
    return None


def _scan_soft_404(body: str) -> Optional[str]:
    if not body:
        return None
    for rx in SOFT_404:
        m = rx.search(body)
        if m:
            return m.group(0)[:80]
    return None


def _scan_name_present(body: str, tokens: list[str]) -> bool:
    if not body or not tokens:
        return True   # nothing to check against -> defer to other signals
    folded = _fold(body)
    # Need at least one distinctive name token to appear
    return any(t in folded for t in tokens)


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
                tf = data_dir / f"{topic}.json"
                if not tf.exists():
                    continue
                try:
                    doc = json.loads(tf.read_text())
                except Exception:
                    continue
                entries = None
                for k in (topic.replace("-", "_"), topic,
                          "vineyards", "tasting_rooms", "wine_bars",
                          "wine_restaurants", "wine_retailers", "wine_schools",
                          "wine_tours", "distilleries", "wine_museums",
                          "wine_hotels", "wine_experiences", "hidden_gems"):
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
                    urls = {}
                    for field in ("source_url", "open_evidence_url",
                                  "cuisine_evidence_url"):
                        v = verified.get(field) or e.get(field)
                        if v and isinstance(v, str) and v.startswith("http"):
                            urls[field] = v
                    yield (country, region, topic, slug, name, urls)


def assess_one(country: str, region: str, topic: str, slug: str,
               name: str, urls: dict) -> Hit:
    region_key = f"{country}/{region}"
    tokens = _name_tokens(name)
    urls_checked = {}
    soft_404_count = 0
    name_present_any = False

    for field, url in urls.items():
        http_status, body = _fetch(url)
        page_status = "open"
        if http_status.startswith("HTTP") or http_status.startswith("ERR"):
            page_status = http_status
        elif http_status == "200":
            bw = _scan_bot_wall(body)
            if bw:
                # Bot-wall: the URL is probably fine; we just can't see the
                # content. Treat as 'open' so we don't accuse the entity of
                # having a wrong source URL when in fact our scraper got
                # blocked by Cloudflare / a security challenge.
                page_status = f"bot-wall:{bw[:30]}"
                name_present_any = True
            else:
                sm = _scan_soft_404(body)
                if sm:
                    page_status = f"soft-404:{sm[:40]}"
                    soft_404_count += 1
                elif _scan_name_present(body, tokens):
                    page_status = "name-present"
                    name_present_any = True
                else:
                    page_status = "name-absent"
        urls_checked[field] = (http_status, page_status)

    # Decision: if any URL says name-present, OK. Else if any soft-404,
    # flag soft-404. Else if all URLs returned content but none mentioned
    # the name, flag name-absent.
    if name_present_any:
        status = "open"
    elif soft_404_count > 0:
        status = "soft-404"
    elif urls_checked and any(s[1] == "name-absent" for s in urls_checked.values()):
        status = "name-absent"
    else:
        status = "unknown"

    return Hit(region_key, topic, slug, name, status, urls_checked,
               datetime.now(timezone.utc).isoformat())


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--region", help="country/region e.g. germany/rheingau")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--topic", help="restrict to one venue topic")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6,
                    help="parallel HTTP workers (default 6)")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--no-cache-write", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any soft-404 or name-absent finding")
    ap.add_argument("--only-status", choices=("soft-404", "name-absent"),
                    help="only print findings of this status")
    args = ap.parse_args()

    region_filter = args.region if not args.all else None
    cache = {} if args.no_cache else _load_cache()

    venues = list(iter_venue_entities(region_filter, args.topic))
    if args.limit:
        venues = venues[: args.limit]

    if not venues:
        print("No venues found for the given filter.", file=sys.stderr)
        return 0

    print(f"[source-relevance] scanning {len(venues)} venues (workers={args.workers})")

    findings: list[Hit] = []
    served_from_cache = 0
    queried = 0
    pending = []
    for v in venues:
        country, region, topic, slug, name, urls = v
        region_key = f"{country}/{region}"
        key = _cache_key(region_key, topic, slug)
        cached = cache.get(key)
        if cached and _cache_fresh(cached):
            served_from_cache += 1
            if cached["status"] in ("soft-404", "name-absent"):
                findings.append(Hit(
                    region_key, topic, slug, name, cached["status"],
                    cached.get("urls_checked", {}), cached["cached_at"]))
            continue
        pending.append(v)

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
                "status": h.status,
                "urls_checked": h.urls_checked,
                "cached_at": h.cached_at,
            }
            if h.status in ("soft-404", "name-absent"):
                if args.only_status and h.status != args.only_status:
                    pass
                else:
                    findings.append(h)
                    print(f"  [{h.status.upper()}] {h.region}/{h.topic}/{h.slug} :: {h.name}")
                    for field, (hs, ps) in h.urls_checked.items():
                        print(f"      {field}: {hs} -> {ps}")
            if queried % 50 == 0 and not args.no_cache_write:
                _save_cache(cache)

    if not args.no_cache_write:
        _save_cache(cache)

    soft_404s = [h for h in findings if h.status == "soft-404"]
    name_absent = [h for h in findings if h.status == "name-absent"]

    print("")
    print(f"[source-relevance] SUMMARY")
    print(f"  scanned:           {len(venues)}")
    print(f"  served from cache: {served_from_cache}")
    print(f"  queried:           {queried}")
    print(f"  soft-404:          {len(soft_404s)}")
    print(f"  name-absent:       {len(name_absent)}")

    if findings:
        print("")
        print("=== FINDINGS (group by region/topic) ===")
        from collections import defaultdict
        by_region = defaultdict(list)
        for h in findings:
            by_region[h.region].append(h)
        for region in sorted(by_region):
            print(f"  {region}: {len(by_region[region])} finding(s)")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
