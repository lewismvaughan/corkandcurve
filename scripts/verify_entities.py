#!/usr/bin/env python3
"""Mechanical pass-1 verifier: read each entity's `verified` provenance
block and check it deterministically. No WebSearch, no LLM judgment, no
randomness — same input, same output every run.

Checks per entity:
  1. `verified.source_url` HEAD-resolves (retries GET on 403/404/405 for
     anti-bot; honors 401/429 as anti-bot, not broken).
  2. `verified.open_evidence_url` HEAD-resolves (same retry shape).
  3. `verified.cuisine_evidence_url` HEAD-resolves (if present).
  4. `verified.address_quoted` fuzzy-matches `entity.address`. Normalized
     (lowercased, punctuation->space, whitespace collapsed); one must be a
     substring of the other. Catches the address-hallucination defect class
     at the source: if the researcher quoted "84 Rue de Varenne" from
     source_url but wrote "84 Rue Saint-Maur" into entity.address, the
     mismatch shows up here, deterministically.
  5. `verified.checked_on` is not older than 90 days (stale flag).
  6. `verified.open_status == "open"` (anything else excludes from ship).

Designed to replace the multi-round WebSearch-based QA loop. Pass-1 runs
in seconds and catches ~all existence + address-class defects. Pass-2
(narrow LLM judgment in agents/qa/PROMPT.md) handles what this can't:
route-vs-operator matches, cuisine-evidence content (this script only
HEADs, doesn't read), festival-month sanity, editorial-prose closed-venue
echoes.

Usage:
    python3 scripts/verify_entities.py --country united-states --city new-york-city
    python3 scripts/verify_entities.py --all
    python3 scripts/verify_entities.py --country france --city paris --report verify-paris.json

Exit code: 0 if all entities pass, 1 if any HARD failure (dead source_url
or address mismatch). Stale checked_on (>90d) is a WARN, not a fail.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

TIMEOUT = 10
WORKERS = 12
UA = "TableJourney-Verifier/1.0 (+https://tablejourney.com)"
STALE_DAYS = 90
ANTI_BOT_CODES = {401, 402, 403, 405, 429, 500, 503, 504, 521}
# 504 (Gateway Timeout) added 2026-05-19: Vegas Goodwich shipped with HARD on
# thegoodwich.com returning 504 from a Cloudflare-style cache. 504 means the
# proxy reached the origin but the origin was slow; it's transient like 503,
# not permanent like 404/410/451. Treat as WARN, not HARD.
# 500 (Internal Server Error) added 2026-05-19: Vegas Williams-Sonoma Rampart
# store page returned 500 transiently. 500 from a major retailer is overwhelmingly
# transient (deploy mid-progress, app crash, DB blip); not a "domain gone" signal.
# 4xx-without-405 still HARDs (404 means page genuinely missing).

ENTITY_LIST_KEYS = (
    # Wine-vertical entity lists (Cork & Curve). These carry real
    # addresses + provenance URLs and MUST be HEAD-checked + address
    # fuzzy-matched. They were missing on the fork, so layer 2 never
    # verified vineyards (the credibility-critical entity) — flagged
    # during the Rioja ship 2026-05-25.
    "vineyards", "tasting_rooms", "wine_restaurants", "wine_retailers",
    "wine_schools", "wine_tours", "distilleries", "wine_museums",
    "wine_hotels", "wine_experiences",
    # Shared / overlapping keys (also valid wine entities):
    "wine_bars", "hidden_gems",
    # Legacy food-vertical keys (harmless; no C&C file uses them):
    "restaurants", "fine_dining", "casual_dining", "cafes", "bakeries",
    "coffee_roasters", "bars", "street_food", "breweries",
    "markets", "food_tours", "food_festivals", "cooking_classes",
    "budget_eating", "brunch", "late_night",
    "day_trips_food",
)
SKIP_FILES = {
    "itineraries.json", "signature-dishes.json", "region.json",
    "city.json", "neighborhoods.json", "food-history.json",
    "seasonal-food.json",
}

_PUNCT_RE = re.compile(r"[^a-z0-9]+")

# Postal-code patterns to strip pre-tokenization. Address fields routinely
# carry postcodes on one side (entity.address) but not the other (quoted
# from source page). The numeric token noise (e.g. "61-728" -> ["61", "728"])
# breaks the token-subset comparison even when the street + city are an
# exact match. Strip before normalization so they never reach the matcher.
_POSTCODE_PATTERNS = [
    re.compile(r"\b\d{2}-\d{3}\b"),       # Polish (00-374, 61-728)
    re.compile(r"\b\d{5}-\d{4}\b"),       # US ZIP+4
    re.compile(r"\b\d{5}\b"),             # US ZIP, German PLZ, French CP
    re.compile(r"\b\d{4}\s?[A-Z]{2}\b"),  # Dutch (1012 JS)
    re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", re.IGNORECASE),  # UK postcode
]
def _strip_postcodes(s: str) -> str:
    for pat in _POSTCODE_PATTERNS:
        s = pat.sub(" ", s)
    return s

# Strip combining diacritic marks so e.g. "Hôpital" -> "hopital", "Vendôme" ->
# "vendome", "Algérie" -> "algerie". Agents often quote diacritics verbatim
# from a source page while entity.address has the ASCII form (or vice versa);
# we don't want that stylistic difference to fail the substring match.
import unicodedata as _unicodedata
# Special-case characters that NFKD does NOT decompose (no combining marks).
# Polish ł/Ł, Danish/Norwegian ø/Ø/æ/Æ, French œ/Œ, German ß, Icelandic þ/Þ,
# Croatian/Vietnamese đ/Đ. Without this map, "Wrocław" normalizes to
# "wroc aw" (the ł is non-alpha to punct-strip and becomes a space),
# producing endless false addr_mismatch HARDs across Polish cities.
_STROKE_CHAR_MAP = str.maketrans({
    "ł": "l", "Ł": "L",
    "ø": "o", "Ø": "O",
    "æ": "ae", "Æ": "AE",
    "œ": "oe", "Œ": "OE",
    "ß": "ss",
    "þ": "th", "Þ": "TH",
    "đ": "d", "Đ": "D",
})
def _strip_diacritics(s: str) -> str:
    s = s.translate(_STROKE_CHAR_MAP)
    return "".join(
        c for c in _unicodedata.normalize("NFKD", s)
        if not _unicodedata.combining(c)
    )

# Token-level normalizations. Each maps a word found in addresses to its
# canonical (short) form so e.g. "Avenue" and "Ave" both compare as "ave".
# Bidirectional, word-boundary only — applied after lowercasing/punct strip.
# Goal: eliminate false-positive addr_mismatch HARDs caused by stylistic
# abbreviation differences between source pages and entity.address copy.
# (e.g. "350 University Avenue" vs "350 University Ave" should match.)
# Real defects — different street name, different building number, wrong
# city — still don't match.
_ADDR_TOKEN_NORM = {
    # street suffixes
    "avenue": "ave", "av": "ave",
    "street": "st", "str": "st",
    "road": "rd",
    "boulevard": "blvd", "boul": "blvd",
    "drive": "dr",
    "highway": "hwy", "hiway": "hwy",
    "parkway": "pkwy",
    "place": "pl",
    "court": "ct",
    "lane": "ln",
    "square": "sq",
    "terrace": "ter",
    "circle": "cir",
    "plaza": "plz",
    # cardinal directions
    "north": "n", "south": "s", "east": "e", "west": "w",
    "northwest": "nw", "southwest": "sw",
    "northeast": "ne", "southeast": "se",
    # US state name <-> abbreviation (Minneapolis shipped with 9 addr_mismatch
    # HARDs from "Minnesota, 55403" vs "MN 55403" — agent had to harmonize
    # every entity by hand. Canonicalize here so future US cities don't repeat
    # the same paperwork.)
    "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar",
    "california": "ca", "colorado": "co", "connecticut": "ct",
    "delaware": "de", "florida": "fl", "georgia": "ga", "hawaii": "hi",
    "idaho": "id", "illinois": "il", "indiana": "in", "iowa": "ia",
    "kansas": "ks", "kentucky": "ky", "louisiana": "la", "maine": "me",
    "maryland": "md", "massachusetts": "ma", "michigan": "mi",
    "minnesota": "mn", "mississippi": "ms", "missouri": "mo", "montana": "mt",
    "nebraska": "ne", "nevada": "nv", "ohio": "oh", "oklahoma": "ok",
    "oregon": "or", "pennsylvania": "pa", "tennessee": "tn", "texas": "tx",
    "utah": "ut", "vermont": "vt", "virginia": "va", "washington": "wa",
    "wisconsin": "wi", "wyoming": "wy",
    # Multi-word states need to be hyphenated pre-tokenization OR matched
    # separately; the simple token map can't reach them. Handled as known
    # gap — if a future city ships HARDs from "New York" vs "NY", extend.
    # unit / suite synonyms
    "suite": "ste", "unit": "ste", "apt": "ste", "apartment": "ste",
    # number words (limited; cover common ordinal street names)
    "first": "1st", "second": "2nd", "third": "3rd", "fourth": "4th",
    "fifth": "5th", "sixth": "6th", "seventh": "7th", "eighth": "8th",
    "ninth": "9th", "tenth": "10th",
    # German (Berlin shipped with 31 addr_mismatch HARDs from "Str." vs
    # "Strasse" before the agent patched each by hand; canonicalize here so
    # Vienna/Hamburg/Munich never hit it again). Diacritic-strip already
    # collapses "Straße" -> "strasse" before this map runs.
    "strasse": "str", "strase": "str",
    "platz": "pl",
    "weg": "weg",
    # Italian
    "via": "via", "viale": "vle",
    "piazza": "pza", "piazzale": "pzle",
    "corso": "cso",
    "vicolo": "vico",
    # Spanish
    "calle": "c", "carrer": "c",
    "avenida": "av", "avinguda": "av",
    "paseo": "po", "passeig": "po",
    # French (additions; existing entries already handle Avenue/Boulevard)
    "rue": "rue",
    "place": "pl",
    "impasse": "imp",
    "quai": "qu",
    "cours": "crs",
    # Polish (Kraków/Poznań shipped with 80+ addr_mismatch HARDs from
    # "ul. Józefa 23, Kraków" vs "Józefa 23, 31-056 Kraków" — "ul."
    # ("ulica" = street) is a prefix article often dropped in canonical
    # forms, and "św." ("świętego" / "świętej" / "święty" = saint) varies
    # between abbreviated and expanded forms across sources). Same pattern
    # as the Berlin "Strasse/Str." fix below. Note: "al." (Polish "aleja"
    # = avenue) deliberately NOT mapped here — it collides with US state
    # Alabama. "aleja"/"aleje" full spellings are safe to drop.
    "ul": "",
    "ulica": "",
    "aleja": "al",
    "aleje": "al",
    "plac": "pl",
    "swietego": "sw",
    "swietej": "sw",
    "swiety": "sw",
    "swieta": "sw",
    "nr": "",
    "polska": "poland",
    "warszawa": "warsaw",
    "praha": "prague",
    "vaclavske": "wenceslas",
    "namesti": "square",
    "ceska": "czech",
    "republika": "republic",
    "wien": "vienna",
    "napoli": "naples",
    "firenze": "florence",
    "venezia": "venice",
    "roma": "rome",
    "muenchen": "munich",
    "munchen": "munich",
    "deutschland": "germany",
    "bayern": "",
    "kobenhavn": "copenhagen",
    "kobenhavns": "copenhagen",
    "lisboa": "lisbon",
    "atene": "athens",
    "atenas": "athens",
    "athina": "athens",
    "athinas": "athens",
    "greece": "",
    "moskva": "moscow",
    # Mexico / Spanish — abbreviation collapses for CDMX addresses.
    # Maps before _ADDR_TOKEN_NORM exists. "av" already maps via Spanish
    # block above. Add Mexican-specific forms.
    "av": "av", "avda": "av",
    # Basque (Donostia-San Sebastian uses Basque alongside Spanish)
    "kalea": "",           # "Kalea" = Basque for "Street"
    "pasealekua": "paseo", # Basque "Pasealekua" = Spanish "Paseo" / promenade
    "donostia": "donostia",  # canonical
    # Thai transliteration variants (Bangkok)
    "wattana": "watthana", "watthana": "watthana",
    "klongtan": "khlongtan", "khlong": "khlongtan", "klong": "khlongtan",
    "bangrak": "bangrak", "bang": "bangrak",
    "phayathai": "phayathai", "phaya": "phayathai",
    "krung": "bangkok",
    "thep": "bangkok",
    "maha": "bangkok",
    "nakhon": "bangkok",
    # Donostia / San Sebastian conflation — both refer to the same city
    "sansebastian": "donostia",
    "nte": "norte",
    "ote": "este",
    "pte": "poniente",
    "sur": "sur",
    "col": "",   # "Col. Centro" -> "centro"
    "colonia": "",
    "esq": "",   # "esq Amsterdam" (corner)
    "cdmx": "",
    "df": "",
    "mexico": "mexico",
    "ciudad": "",  # collapse "Ciudad de Mexico" → "de mexico"
    "centro": "centro",
    "in": "", "at": "", "on": "", "of": "", "the": "",
    "and": "",
}


def _normalize_addr(s: str) -> str:
    """Lowercase, replace punctuation with space, collapse whitespace,
    then canonicalize street-suffix and direction tokens so "Avenue"
    and "Ave" compare equal. Punctuation already stripped before token
    swap so "Ave." and "Ave" both become "ave"."""
    if not s:
        return ""
    s = _strip_diacritics(s).lower()
    s = _strip_postcodes(s)
    s = _PUNCT_RE.sub(" ", s)
    # Compound-suffix substitution before token split (German compound
    # words like "Gipsstrasse" / "Gipsstr." need to collapse to a single
    # canonical form even though "strasse" isn't a standalone token).
    # Berlin 2026-05-19: Cocolo Ramen shipped with HARD on
    # "Gipsstr." vs "Gipsstrasse" because the per-token map couldn't
    # see strasse as a suffix.
    s = s.replace("strasse", "str")
    # Compound suffix: "Maximiliansplatz" should match "Maximilianspl." since
    # "platz" is the suffix. Pre-tokenize substitution mirrors strasse → str.
    s = s.replace("platz", "pl")
    tokens = s.split()
    tokens = [_ADDR_TOKEN_NORM.get(t, t) for t in tokens]
    return " ".join(tokens)


def _address_matches(quoted: str, actual: str) -> bool:
    """Fuzzy match in layers. First substring. Then token-set subset.
    Final fallback: Jaccard overlap >= 0.5 — Polish addresses commonly
    carry building-range suffixes like "/42" or "/1u" on one side but
    not the other (e.g. "Długa 33/34" vs "Długa 33") and stylistic
    extras like "Stary Rynek" neighborhood inside the quote. Strict
    subset rejects these even though they're the same address. Real
    defects (different street, wrong number) still fall below 0.5."""
    q = _normalize_addr(quoted)
    a = _normalize_addr(actual)
    if not q or not a:
        return False
    if q in a or a in q:
        return True
    qt = set(q.split())
    at = set(a.split())
    if not qt or not at:
        return False
    if qt.issubset(at) or at.issubset(qt):
        return True
    inter = qt & at
    union = qt | at
    if not union:
        return False
    return len(inter) / len(union) >= 0.5


def _check_url(url: str) -> int | str:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status
    except urllib.error.HTTPError as e:
        if e.code in (403, 404, 405):
            try:
                req2 = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
                with urllib.request.urlopen(req2, timeout=TIMEOUT) as r:
                    return r.status
            except urllib.error.HTTPError as e2:
                return e2.code
            except urllib.error.URLError as e2:
                try:
                    name = type(e2.reason).__name__
                except Exception:
                    name = "URLError"
                return f"ERR:{name}"
            except Exception as e2:
                return f"ERR:{type(e2).__name__}"
        return e.code
    except urllib.error.URLError as e:
        try:
            name = type(e.reason).__name__
        except Exception:
            name = "URLError"
        return f"ERR:{name}"
    except Exception as e:
        return f"ERR:{type(e).__name__}"


_TRANSIENT_ERR_TYPES = {
    "SSLCertVerificationError",
    "SSLError",
    "TimeoutError",
    "timeout",
    "RemoteDisconnected",
    "IncompleteRead",
    "ConnectionResetError",
}


def _url_is_dead(status) -> bool:
    """Anti-bot codes (401/403/405/429/503/521) are NOT dead. Anything else
    >= 400 or any ERR is dead."""
    if isinstance(status, str):
        return True
    if status in ANTI_BOT_CODES:
        return False
    return status >= 400


def _url_is_transient(status) -> bool:
    """Real-but-flaky failures: SSL cert mismatch on venue's own www subdomain,
    expired cert, timeouts, connection resets. The URL points at a real host
    that resolved in DNS — the venue's website is just badly configured. These
    are downgraded from HARD to WARN so they don't block ship for cases where
    the address/cuisine data is otherwise verified."""
    if not isinstance(status, str):
        return False
    if not status.startswith("ERR:"):
        return False
    return status[4:] in _TRANSIENT_ERR_TYPES


def _walk_entities(data_dir: Path):
    """Yield (fname, topic_key, idx, entity) for every entity in a city
    that should carry a `verified` block (i.e. excluding itineraries,
    signature dishes, etc.)."""
    for f in sorted(data_dir.glob("*.json")):
        if f.name in SKIP_FILES:
            continue
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if f.name == "dietary.json":
            outer = payload.get("dietary")
            if isinstance(outer, dict):
                for diet_key, entries in outer.items():
                    if isinstance(entries, list):
                        for i, e in enumerate(entries):
                            if isinstance(e, dict):
                                yield f.name, f"dietary[{diet_key}]", i, e
            continue
        if f.name == "nightlife.json":
            outer = payload.get("nightlife")
            if isinstance(outer, dict):
                for sub_key, entries in outer.items():
                    if isinstance(entries, list):
                        for i, e in enumerate(entries):
                            if isinstance(e, dict):
                                yield f.name, f"nightlife[{sub_key}]", i, e
            continue
        for k in ENTITY_LIST_KEYS:
            entries = payload.get(k)
            if isinstance(entries, list):
                for i, e in enumerate(entries):
                    if isinstance(e, dict):
                        yield f.name, k, i, e


def _entity_label(e: dict) -> str:
    return e.get("name") or e.get("operator") or e.get("slug") or "?"


def verify_city(country: str, city: str) -> dict:
    data_dir = SITE_DATA / country / city / "data"
    if not data_dir.exists():
        return {"country": country, "city": city, "error": f"no such city: {data_dir}"}

    entities = list(_walk_entities(data_dir))
    if not entities:
        return {
            "country": country, "city": city,
            "entities": 0, "hard_failures": 0, "warnings": 0, "rows": [],
        }

    today = datetime.date.today()
    stale_cutoff = today - datetime.timedelta(days=STALE_DAYS)

    urls_to_check: dict[str, list[tuple]] = {}
    rows: list[dict] = []

    for fname, topic, idx, e in entities:
        label = _entity_label(e)
        v = e.get("verified")
        row = {
            "file": fname, "topic": topic, "idx": idx,
            "slug": e.get("slug"), "name": label,
            "missing_block": v is None,
            "issues": [],  # list of dicts
        }
        if not isinstance(v, dict):
            row["issues"].append({"level": "WARN", "code": "no_verified", "msg": "no `verified` block (run backfill)"})
            rows.append(row)
            continue

        # Date staleness
        co = v.get("checked_on")
        if isinstance(co, str):
            try:
                d = datetime.date.fromisoformat(co)
                if d < stale_cutoff:
                    age = (today - d).days
                    row["issues"].append({"level": "WARN", "code": "stale", "msg": f"checked_on {co} is {age}d old (cutoff {STALE_DAYS}d)"})
            except ValueError:
                row["issues"].append({"level": "HARD", "code": "bad_date", "msg": f"checked_on={co!r} not ISO YYYY-MM-DD"})

        # Open status
        status = v.get("open_status")
        if status not in {"open", "permanently_closed", "seasonal", "unknown"}:
            row["issues"].append({"level": "HARD", "code": "bad_status", "msg": f"open_status={status!r}"})
        elif status == "permanently_closed":
            row["issues"].append({"level": "HARD", "code": "closed", "msg": "open_status=permanently_closed (must be removed or pages will 404 on next research pass)"})

        # Address fuzzy match — only when both sides exist (skip for tours/etc
        # using meeting_point or for dishes/itineraries).
        actual_addr = e.get("address") or e.get("meeting_point") or ""
        quoted = v.get("address_quoted") or ""
        if actual_addr and quoted and not _address_matches(quoted, actual_addr):
            row["issues"].append({
                "level": "HARD", "code": "addr_mismatch",
                "msg": f"address_quoted={quoted!r} does not fuzzy-match entity.address={actual_addr!r}",
            })
        # (banned-host check removed — Google Maps / Yelp / Wikipedia do
        # prove venue existence, which is source_url's job. Cuisine
        # claims are validated separately by check_evidence_content.py
        # which actually fetches the cuisine_evidence_url and matches
        # content. Banning hosts at source_url created false-positive
        # work without catching real defects.)

        # Queue URL checks; we'll resolve in parallel after the walk.
        for kind in ("source_url", "open_evidence_url", "cuisine_evidence_url"):
            url = v.get(kind)
            if isinstance(url, str) and url.startswith("http"):
                urls_to_check.setdefault(url, []).append((row, kind))

        # Independent-domain check: at least one verified-block URL must
        # live on a domain different from source_url. Otherwise we have
        # "own-site-only" verification — the operator's own page is the
        # only thing vouching for the venue, which can't catch the
        # real-URL + fake-address defect class (Naples Opus 2026-05-19
        # removed 7 of these). Anchor-required tags / dishes / itineraries
        # are exempt because they don't carry a venue-existence claim.
        import urllib.parse as _up
        def _host(u: str) -> str:
            try:
                h = _up.urlparse(u).hostname or ""
                return h.lower().lstrip("www.")
            except Exception:
                return ""
        urls = [v.get("source_url"), v.get("open_evidence_url"), v.get("cuisine_evidence_url")]
        hosts = {_host(u) for u in urls if isinstance(u, str) and u.startswith("http")}
        hosts.discard("")
        if len(hosts) == 1 and fname not in SKIP_FILES:
            row["issues"].append({
                "level": "WARN", "code": "own_site_only",
                "msg": f"all verified-block URLs share one domain ({next(iter(hosts))}); "
                       f"add an independent-directory URL (Google Maps, OSM, Time Out, Eater, "
                       f"Michelin, OpenTable/Resy, HappyCow/Zabihah) so the venue + address are "
                       f"corroborated outside the operator's own site",
            })

        rows.append(row)

    # Parallel URL HEAD checks.
    if urls_to_check:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(_check_url, u): u for u in urls_to_check}
            for fut in as_completed(futures):
                url = futures[fut]
                status = fut.result()
                dead = _url_is_dead(status)
                transient = _url_is_transient(status)
                for row, kind in urls_to_check[url]:
                    if dead:
                        # source_url dead is HARD by default, but downgrade
                        # to WARN when the host resolved and responded
                        # (SSL/timeout/reset) — the URL is real, just flaky.
                        if kind == "source_url" and not transient:
                            level = "HARD"
                        else:
                            level = "WARN"
                        row["issues"].append({
                            "level": level,
                            "code": f"dead_{kind}",
                            "msg": f"{kind}={url} returned {status}",
                        })

    hard = sum(1 for r in rows for x in r["issues"] if x["level"] == "HARD")
    warn = sum(1 for r in rows for x in r["issues"] if x["level"] == "WARN")
    return {
        "country": country, "city": city,
        "entities": len(rows),
        "hard_failures": hard,
        "warnings": warn,
        "rows": rows,
    }


def _print_summary(report: dict) -> None:
    print(f"\n=== {report['country']}/{report['city']} ===")
    if "error" in report:
        print(f"  ERROR: {report['error']}")
        return
    print(f"  entities: {report['entities']}  hard: {report['hard_failures']}  warn: {report['warnings']}")
    for row in report["rows"]:
        if not row["issues"]:
            continue
        bad = [i for i in row["issues"] if i["level"] == "HARD"]
        warn_only = [i for i in row["issues"] if i["level"] == "WARN" and i["code"] != "no_verified"]
        if not bad and not warn_only:
            continue
        print(f"  [{row['file']}] {row['name']} ({row['slug']}):")
        for x in row["issues"]:
            if x["code"] == "no_verified":
                continue
            print(f"    {x['level']:<4} {x['code']}: {x['msg']}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--all", action="store_true")
    p.add_argument("--report", help="Write JSON report to this path")
    args = p.parse_args()

    if args.all:
        targets = []
        for country_dir in sorted(SITE_DATA.iterdir()):
            if not country_dir.is_dir():
                continue
            for city_dir in sorted(country_dir.iterdir()):
                if (city_dir / "data").exists():
                    targets.append((country_dir.name, city_dir.name))
    elif args.country and args.city:
        targets = [(args.country, args.city)]
    else:
        p.error("Pass --all or both --country and --city")
        return 2

    full = []
    total_hard = 0
    for country, city in targets:
        report = verify_city(country, city)
        full.append(report)
        _print_summary(report)
        total_hard += report.get("hard_failures", 0)

    if args.report:
        Path(args.report).write_text(json.dumps(full, indent=2), encoding="utf-8")
        print(f"\nReport written to {args.report}")

    print(f"\nTotal HARD failures across {len(targets)} cities: {total_hard}")
    return 1 if total_hard else 0


if __name__ == "__main__":
    sys.exit(main())
