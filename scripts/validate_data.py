#!/usr/bin/env python3
"""
Food-aware data validator. Walks site-data/ and reports per-city:
  - missing required files
  - empty topic files (lists with 0 items)
  - placeholder / TODO leakage
  - missing SEO essentials (title, description, canonical-shaping geo)
  - mismatched JSON shapes

Exit code is non-zero if any errors are found unless --warn-only is set.

Usage:
    python scripts/validate_data.py
    python scripts/validate_data.py --country france
    python scripts/validate_data.py --country france --city paris
    python scripts/validate_data.py --errors-only
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

REQUIRED_FILES = ["region.json", "neighborhoods.json"]
TOPIC_FILES_TO_KEY = {
    "vineyards.json":         "vineyards",
    "wines.json":             "wines",
    "tasting-rooms.json":     "tasting_rooms",
    "wine-bars.json":         "wine_bars",
    "wine-restaurants.json":  "wine_restaurants",
    "wine-retailers.json":    "wine_retailers",
    "wine-schools.json":      "wine_schools",
    "wine-tours.json":        "wine_tours",
    "wine-festivals.json":    "wine_festivals",
    "distilleries.json":      "distilleries",
    "wine-museums.json":      "wine_museums",
    "wine-hotels.json":       "wine_hotels",
    "wine-experiences.json":  "wine_experiences",
    "wine-history.json":      "wine_history",
    "seasonal-wine.json":     "seasonal_wine",
    "signature-wines.json":   "signature_wines",
    "signature-grapes.json":  "signature_grapes",
    "budget-wines.json":      "budget_wines",
    "hidden-gems.json":       "hidden_gems",
    "day-trips-wine.json":    "day_trips_wine",
    "itineraries.json":       "itineraries",
    "food-pairing.json":      "food_pairing",
    "dietary.json":           "dietary",
    "nightlife.json":         "nightlife",
}
DICT_TOPICS = {"dietary.json", "nightlife.json"}
# wine-history + seasonal-wine may be EITHER a dict keyed by era/season
# buckets (Bordeaux pilot convention) OR a flat list of era/season entries
# (the canonical convention for regions from Burgundy onward). Both render.
# Accept either; SCHEMA documents the list form as canonical going forward.
DICT_OR_LIST_TOPICS = {"wine-history.json", "seasonal-wine.json"}

# Topics where every entry is a fixed venue and MUST have slug+name+address.
# NB: budget-wines is NOT here — budget wines are bottles, not venues; they
# carry `where_to_buy`/`price_band` instead of a street address.
VENUE_TOPICS = {
    "vineyards.json", "tasting-rooms.json", "wine-bars.json",
    "wine-restaurants.json", "wine-retailers.json", "wine-museums.json",
    "wine-hotels.json", "distilleries.json",
    "hidden-gems.json",
}
# Topics where every entry needs slug+name and SHOULD have address or
# meeting_point (WARN if both missing). Tours/festivals/schools roam.
SOFT_ADDRESS_TOPICS = {
    "wine-tours.json", "wine-festivals.json", "wine-schools.json",
    "wine-experiences.json",
}
# Topics where every entry needs slug+name only (day-trips are regions,
# itineraries/signature wines+grapes/pairings are abstract content,
# wines are cuvées tied to a producer rather than a venue).
ENTITY_NO_ADDRESS_TOPICS = {
    "day-trips-wine.json",
    "itineraries.json",
    "signature-wines.json",
    "signature-grapes.json",
    "food-pairing.json",
    "wines.json",
    "budget-wines.json",
}
ENTITY_LIST_TOPICS = VENUE_TOPICS | SOFT_ADDRESS_TOPICS | ENTITY_NO_ADDRESS_TOPICS
# Topics where the per-entity `verified` provenance block is OPTIONAL.
# Itineraries reference other entities; signature wines/grapes and food
# pairings are abstract; all get their truth from the venues they reference.
# Everything else must carry its own provenance. See SCHEMA.md.
# wines.json is NOT optional — every cuvée has its own source URL
# (producer tech sheet or critic page) and carries its own verified block.
VERIFIED_OPTIONAL_TOPICS = {
    "itineraries.json", "signature-wines.json", "signature-grapes.json",
    "food-pairing.json",
}

PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|Lorem ipsum|placeholder)\b", re.IGNORECASE)
EM_EN_DASH_RE = re.compile(r"[—–]")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)

# URL fields on entity entries that we want to look like URLs (warn otherwise).
URL_FIELDS = ("booking_url", "affiliate_url")

# Image provenance fields required on every shipped city's region.json
# (warn-level so subagents are nudged but a half-filled stub city doesn't
# error out during early scaffolding). See agents/food-research/PROMPT.md
# "Image sourcing" section for the policy.
IMAGE_PROVENANCE_FIELDS = (
    "hero_image_source",
    "hero_image_source_url",
    "hero_image_photographer",
    "hero_image_license",
)


# ──────────────────────────────────────────────────────────────────────────
# Length caps. Single source of truth — referenced from
# agents/food-research/PROMPT.md "Length caps" section. Each entry is
# (min, max, severity). Severity ERR fails the city; WARN nudges.
#
# Counts are characters of the html-decoded string. Tuples are inclusive.
# ──────────────────────────────────────────────────────────────────────────

LENGTH_CAPS: dict[str, tuple[int, int, str]] = {
    # region.json
    "destination.tagline":                              (40, 80,  "WARN"),
    "destination.overview":                             (160, 280, "WARN"),
    "destination.hero_image_alt":                       (40, 110, "WARN"),
    "seo.pages.<topic>.title":                          (55, 70,  "WARN"),
    "seo.pages.<topic>.description":                    (140, 165, "ERR"),
    "research.food_culture_summary":                    (600, 1200, "WARN"),
    # neighborhoods.json
    "neighborhood.vibe":                                (80, 180, "WARN"),
    # any venue-style entry (restaurants, casual_dining, fine_dining, etc.).
    # Description is the seed for the entity page's meta description: the
    # renderer's _meta_desc() selector will extend short sources by appending
    # editor's-tail variants, so a too-short description is non-optimal but
    # not broken — hence WARN, not ERR. Subagents should still write to the
    # cap so we don't depend on the fallback chain for SEO copy.
    "entity.description":                               (140, 165, "WARN"),
    "entity.must_order":                                (30, 110, "WARN"),
    "entity.tip":                                       (60, 160, "WARN"),
    "entity.why_hidden":                                (80, 180, "WARN"),
    # signature dishes
    "dish.description":                                 (140, 220, "WARN"),
    "dish.history":                                     (300, 700, "WARN"),
    "dish.make_it_yourself.tip":                        (60, 160, "WARN"),
    # food history
    "food_history.key_eras[].summary":                  (220, 420, "WARN"),
    "food_history.immigrant_influences[].contribution": (80, 220, "WARN"),
    "food_history.signature_innovations[]":             (40, 140, "WARN"),
    # seasonal food
    "seasonal_food.season":                             (120, 240, "WARN"),
    # itineraries
    "itineraries[].days[].activities":                  (140, 280, "WARN"),
    # festivals / tours / classes (description fields used as page-leads
    # in addition to meta description). WARN-level so existing cities still
    # ship; subagents writing new cities should hit the cap.
    "food_festivals.description":                       (140, 220, "WARN"),
    "food_tours.description":                           (140, 220, "WARN"),
    "cooking_classes.description":                      (140, 220, "WARN"),
}


def _dec_len(value: object) -> int:
    """HTML-entity-aware character length. Mirrors utils.seo._rendered_len.
    Non-string values return 0 (caller skips them)."""
    if not isinstance(value, str):
        return 0
    import html as _html
    return len(_html.unescape(value))


def _band_label(key: str) -> str:
    lo, hi, _ = LENGTH_CAPS[key]
    return f"{lo}-{hi} chars"


def _check_length(value: object, key: str, where: str, issues: list) -> None:
    """If LENGTH_CAPS has a band for `key`, check value's decoded length."""
    if key not in LENGTH_CAPS or value is None or value == "":
        return
    lo, hi, sev = LENGTH_CAPS[key]
    n = _dec_len(value)
    if n == 0:
        return
    if not (lo <= n <= hi):
        issues.append((sev, f"{where}: {n} chars (cap {lo}-{hi})"))


def _entry_address(entry: dict) -> str:
    """Address-equivalent for an entry. Tours/festivals may use meeting_point."""
    return entry.get("address") or entry.get("meeting_point") or ""


def _check_editorial_score(fname: str, entry: dict, label: str, issues: list) -> None:
    """editorial_score: WARN if missing, ERR if present but out of [1.0, 5.0]
    or not a number. Subagents are expected to assign one per entity; missing
    is WARN-level so stub cities don't ERR out before research lands."""
    if "editorial_score" not in entry:
        issues.append(("WARN", f"{fname} entry '{label}' missing editorial_score (see SCHEMA.md 'Editorial scoring')"))
        return
    score = entry["editorial_score"]
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        issues.append(("ERR", f"{fname} entry '{label}' editorial_score={score!r} must be a number 1.0 to 5.0"))
        return
    if score < 1.0 or score > 5.0:
        issues.append(("ERR", f"{fname} entry '{label}' editorial_score={score} out of range 1.0 to 5.0"))


_VERIFIED_REQUIRED_FIELDS = ("source_url", "open_status", "checked_on")
_VERIFIED_OPEN_STATUSES = {"open", "permanently_closed", "seasonal", "unknown"}
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# ─── Wine cuvée vocabularies ────────────────────────────────────────────────
# Single source of truth for these controlled values lives in
# docs/WINE_TAGS.md. The validator parses the tag list from there at startup
# but the small enumerations below (sweetness / body / tannin / acidity /
# style) are duplicated here so the validator stays self-contained when run
# without docs/WINE_TAGS.md (e.g. on a stripped CI image).
WINE_SWEETNESS = {"dry", "off-dry", "medium-sweet", "sweet", "dessert"}
WINE_BODY = {"light", "medium", "full"}
WINE_TANNIN = {"low", "medium", "firm", "high"}
WINE_ACIDITY = {"low", "medium", "high", "racy"}
WINE_STYLES = {
    "still-red", "still-white", "still-rose",
    "sparkling-traditional", "sparkling-tank", "sparkling-ancestral",
    "orange",
    "dessert-late-harvest", "dessert-noble-rot", "dessert-ice-wine",
    "dessert-passito",
    "fortified-port", "fortified-sherry", "fortified-madeira",
    "fortified-marsala", "fortified-vdn",
    "vermouth",
}
# Tag axes the RESEARCHER is allowed to emit. The other axes
# (price, ageing, production, grape, world, sweetness) are derived by the
# page generators from other fields; emitting them in wines[*].tags is a
# regression that QA2 should have caught.
WINE_DERIVED_TAG_PREFIXES = ("price-", "drink-young", "medium-term", "cellar-worthy")
WINE_DERIVED_TAGS = {
    "dry", "off-dry", "medium-sweet", "sweet", "dessert",
    "biodynamic", "biodynamic-certified", "organic", "natural", "vegan",
    "low-sulfite", "old-world", "new-world",
}

_WINE_TAGS_DOC = REPO_ROOT / "docs" / "WINE_TAGS.md"
_WINE_TAG_TABLE_ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|", re.MULTILINE)


def _load_wine_tag_vocabulary() -> set[str]:
    """Parse the controlled vocabulary out of docs/WINE_TAGS.md.

    Tags in that doc are rendered in markdown tables, one slug per row,
    formatted as `| `<slug>` | <display> | ... |`. We pick the first
    backticked token from each row. Returns an empty set if the doc is
    missing — validator falls back to a WARN-only tag check in that case.
    """
    if not _WINE_TAGS_DOC.exists():
        return set()
    try:
        text = _WINE_TAGS_DOC.read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(_WINE_TAG_TABLE_ROW.findall(text))


_WINE_TAGS_CACHED: set[str] | None = None


def _wine_tags() -> set[str]:
    global _WINE_TAGS_CACHED
    if _WINE_TAGS_CACHED is None:
        _WINE_TAGS_CACHED = _load_wine_tag_vocabulary()
    return _WINE_TAGS_CACHED


def _check_verified_block(fname: str, entry: dict, label: str, issues: list) -> None:
    """Per-entity provenance block. See SCHEMA.md 'Provenance block (`verified`)'.

    All shipped cities have been backfilled with provenance, so a missing
    block is now a hard ERR. The mechanical verifier at
    `scripts/verify_entities.py` consumes this block to fuzzy-match
    address_quoted vs entity.address and HEAD-check source_url; both
    checks short-circuit if the block is absent, which is why we
    refuse to ship without it.
    """
    if "verified" not in entry:
        issues.append(("ERR", f"{fname} entry '{label}' missing required 'verified' block (SCHEMA.md 'Provenance block')"))
        return
    v = entry["verified"]
    if not isinstance(v, dict):
        issues.append(("ERR", f"{fname} entry '{label}' verified={v!r} must be an object"))
        return
    for req in _VERIFIED_REQUIRED_FIELDS:
        if not v.get(req):
            issues.append(("ERR", f"{fname} entry '{label}' verified missing required '{req}'"))
    src = v.get("source_url")
    if src and not URL_RE.match(str(src)):
        issues.append(("ERR", f"{fname} entry '{label}' verified.source_url={src!r} not a URL"))
    for u in ("open_evidence_url", "cuisine_evidence_url"):
        val = v.get(u)
        if val and not URL_RE.match(str(val)):
            issues.append(("ERR", f"{fname} entry '{label}' verified.{u}={val!r} not a URL"))
    status = v.get("open_status")
    if status and status not in _VERIFIED_OPEN_STATUSES:
        issues.append(("ERR", f"{fname} entry '{label}' verified.open_status={status!r} not in {sorted(_VERIFIED_OPEN_STATUSES)}"))
    checked = v.get("checked_on")
    if checked and not _ISO_DATE_RE.match(str(checked)):
        issues.append(("ERR", f"{fname} entry '{label}' verified.checked_on={checked!r} must be YYYY-MM-DD"))
    # Cuvée taste-evidence must point at a SPECIFIC per-wine page, not a
    # producer homepage / appellation directory landing (Rioja 2026-05-25:
    # 116/120 cuvées cited homepages that substantiate no tasting note).
    # WARN, not ERR, so already-shipped regions aren't retro-broken; the
    # research PROMPT now bans it and QA Section I catches it.
    if fname == "wines.json":
        cev = str(v.get("cuisine_evidence_url") or "")
        path = re.sub(r"^https?://[^/]+", "", cev)
        if cev and path.strip("/") == "":
            issues.append(("WARN", f"{fname} entry '{label}' verified.cuisine_evidence_url={cev!r} is a bare homepage; cuvée taste evidence must be the specific per-wine page (PROMPT P0 #15)"))


def _entry_name(entry: dict) -> str:
    """Display name for an entry. Tours use 'operator' instead of 'name'."""
    return entry.get("name") or entry.get("operator") or ""


def discover_cities(only_country: str | None, only_city: str | None):
    if not SITE_DATA.exists():
        return
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        if only_country and country_dir.name != only_country:
            continue
        # country-level data
        if (country_dir / "data" / "region.json").exists() and not only_city:
            yield country_dir.name, None, country_dir / "data"
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            if only_city and city_dir.name != only_city:
                continue
            if (city_dir / "data" / "region.json").exists():
                yield country_dir.name, city_dir.name, city_dir / "data"


def has_placeholder(value) -> bool:
    if isinstance(value, str):
        return bool(PLACEHOLDER_RE.search(value))
    if isinstance(value, dict):
        return any(has_placeholder(v) for v in value.values())
    if isinstance(value, list):
        return any(has_placeholder(v) for v in value)
    return False


def has_em_dash(value) -> bool:
    if isinstance(value, str):
        return bool(EM_EN_DASH_RE.search(value))
    if isinstance(value, dict):
        return any(has_em_dash(v) for v in value.values())
    if isinstance(value, list):
        return any(has_em_dash(v) for v in value)
    return False


# Truncation detector. Sonnet has been observed truncating prose fields at
# word boundaries to hit a length cap, leaving descriptions ending in:
#   1) a stop-word + period: "...is the." / "...applied to seasonal."
#   2) a comma + period:     "...storytelling,."
#   3) a transitive verb that needs an object: "The approach requires."
#   4) a short prep phrase that needs more: "...common in restaurant."
# All four make the rendered page read as visibly broken copy.
# A description that matches is treated as a P0 defect. See PROMPT.md
# "CRITICAL: complete sentences win over hitting the cap".

# Pattern 1+2: stop-word/comma cliffhangers
# The negative lookbehind for an apostrophe stops the conjunction "or"
# inside an elided proper noun (Cote d'Or, Cotes d'Or) being read as a
# trailing stop-word: the apostrophe creates a \b before "Or", so without
# the guard every description ending "...Cote d'Or." false-positived as a
# truncation (recurring Burgundy bug, 2026-05-25).
TRUNCATION_TAIL_RE = re.compile(
    r"(?:(?<!['’])\b(?:the|a|an|is|are|was|were|with|and|or|of|to|in|on|at|for|by|"
    r"from|as|into|onto|that|which|whose|but|so|nor|yet|its|their|his|her)"
    r"\s*[,;:]?\s*\.\s*|,\s*\.\s*)$",
    re.IGNORECASE,
)

# Pattern 3: a short SHORT final sentence ending in a transitive verb that
# clearly needs an object. Assembled from real Sonnet truncations on NYC
# bars.json:
#   Attaboy:        "The approach requires."
#   Temple Bar:     "...that feels."
#   Midnight Rambler: "...practice more common in restaurant kitchens."
#                     (the truncation cut "kitchens" -> "in restaurant.")
# We deliberately keep the verb list small. Larger lists false-positive on
# natural editorial-terse closers like "The whole point of Paris." or
# "Folded in half." We trust the PROMPT.md voice contract to keep noun-
# cliffhanger truncations like "...prioritises regional." out of the data;
# the validator catches the verb-cliffhanger subset that's mechanically
# detectable without misfiring.
TRUNCATION_VERB_RE = re.compile(
    r"\b(?:requires|prioritises|prioritizes|applies|features|includes|"
    r"emphasises|emphasizes|highlights|allows|enables|presents|reflects|"
    r"represents|signals|carries|attempted|feels|tastes|smells)\.\s*$",
    re.IGNORECASE,
)

# Pattern 4: a short final fragment STARTING with a coordinating conjunction.
# Catches "...and a cocktail." style cut-offs where the agent was building a
# compound predicate and stopped early. Only fires on short (<=6 words) final
# sentences so that natural conjunction-led sentences ("And so it goes.") in
# longer text aren't flagged.
TRUNCATION_CONJ_FRAGMENT_RE = re.compile(
    r"^(?:and|or|but)\s+\w+(?:\s+\w+){0,3}\.\s*$",
    re.IGNORECASE,
)

# Pattern 5 (v4): stranded modifier. "...prioritises regional." style: a
# transitive verb followed by exactly ONE bare adjective-shaped token and a
# period. The agent meant to say "prioritises regional cuisine" or similar
# and stopped before the object noun. Hard to catch without false-positives,
# so the rule is deliberately strict:
#   - the clause ends `<verb> <single-token>.`
#   - the verb is in the known transitive-truncation set
#   - the tail token has an adjective-typical suffix (al/ic/ous/ive/ent/ant/
#     ful/less/ish/ern) AND length >= 5
# This filters out legitimate noun-object closers like "features wine." or
# "covers basics." while catching "prioritises regional." and "applies
# national.". Empirically zero false-positives on shipped NYC + Paris data
# as of 2026-05-18; revisit the suffix list if real text trips it.
_STRANDED_VERBS = (
    "requires", "prioritises", "prioritizes", "applies", "features",
    "includes", "emphasises", "emphasizes", "highlights", "allows",
    "enables", "presents", "reflects", "represents", "signals",
    "carries", "attempted",
)
_STRANDED_ADJ_SUFFIXES = (
    "al", "ic", "ous", "ive", "ent", "ant", "ful", "less", "ish", "ern",
)


def _stranded_modifier_truncation(last_clause: str) -> bool:
    s = last_clause.rstrip(".").strip()
    tokens = s.split()
    if len(tokens) < 2:
        return False
    verb_idx = -1
    for i, tok in enumerate(tokens):
        if tok.lower().strip(",;:") in _STRANDED_VERBS:
            verb_idx = i
    # verb must sit exactly one token before the period
    if verb_idx < 0 or verb_idx != len(tokens) - 2:
        return False
    tail = tokens[-1].lower().strip(",;:")
    if len(tail) < 5:
        return False
    return any(tail.endswith(suf) for suf in _STRANDED_ADJ_SUFFIXES)


def looks_truncated(value: str) -> bool:
    """True if a prose field appears cut mid-sentence. Catches the failure
    modes observed in real Sonnet output:
      (1) stop-word + period or comma + period   ("...is the.", "...,.")
      (2) final CLAUSE ending in transitive verb ("...that feels.")
      (3) final CLAUSE of <=4 words led by a conjunction ("...and a cocktail.")
    For patterns 2 and 3, the "final clause" is the tail after the last comma
    or semicolon inside the last sentence. This catches compound-sentence
    truncations like "...full kitchen open until 3am, and a cocktail." that
    a last-sentence-only check would miss.
    Conservative: patterns 2 and 3 only fire on short final clauses, so
    editorial-terse closers like "Folded in half." don't false-positive."""
    if not isinstance(value, str) or not value:
        return False
    s = value.strip()
    if TRUNCATION_TAIL_RE.search(s):
        return True
    last_sentence = re.split(r"(?<=[.!?])\s+", s)[-1].strip()
    # Take the tail clause after the last comma/semicolon. This is what catches
    # "...3am, and a cocktail." and "...martini programme and a dark-lit
    # atmosphere that feels."
    last_clause = re.split(r"[,;]\s+", last_sentence)[-1].strip()
    clause_words = len(last_clause.split())
    # Verb cliffhangers: relax the clause-length limit because some Sonnet
    # truncations end a 10-14 word trailing clause with the verb
    # (e.g. "...martini programme and a dark-lit atmosphere that feels.").
    if clause_words <= 14 and TRUNCATION_VERB_RE.search(last_clause):
        return True
    if clause_words <= 4 and TRUNCATION_CONJ_FRAGMENT_RE.match(last_clause):
        return True
    if _stranded_modifier_truncation(last_clause):
        return True
    return False


def _topic_slug_set(data_dir: Path, fname: str, key: str) -> set[str]:
    """Read a topic file, return the set of `slug` values it contains.
    Used for cross-reference validation across topic files. Returns an
    empty set if the file is missing or unreadable so callers can degrade
    gracefully (cross-ref check becomes a no-op rather than a crash)."""
    p = data_dir / fname
    if not p.exists():
        return set()
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    items = d.get(key) or []
    return {x["slug"] for x in items if isinstance(x, dict) and x.get("slug")}


_VINTAGE_IN_SLUG_RE = re.compile(r"(?:19|20)\d{2}")


def _check_wine_entries(fname: str, entries: list, vineyard_slugs: set[str], issues: list) -> None:
    """Cuvée-specific validation for wines.json (per-producer cuvée catalog).

    Enforces the contract from agents/wine-research/SCHEMA.md "wines" section
    and the controlled vocabulary in docs/WINE_TAGS.md:

      - vintage-agnostic discipline: no year in slug, no year in name
      - producer cross-ref resolves in same region's vineyards.json
      - style / sweetness / body / tannin / acidity from controlled sets
      - tags ⊆ docs/WINE_TAGS.md AND no DERIVED-axis tags
        (price / ageing / production / grape / world / sweetness — those
         are generator-derived; researcher emitting them is a regression)
      - taste block shape: aroma + palate are arrays, summary present
      - varietals[] each carry a `grape` key
      - pairings[] each carry both `dish` and `why`
      - tablejourney_ref is null or a path (not a full URL)
      - first_vintage / history.origin_year are 4-digit years

    The slug+name+address+verified+editorial_score+truncation checks are
    handled by the existing _check_entity_entries pass.
    """
    tag_vocab = _wine_tags()
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            continue
        label = e.get("name") or e.get("slug") or f"index {i}"
        slug = e.get("slug") or ""
        if _VINTAGE_IN_SLUG_RE.search(slug):
            issues.append((
                "ERR",
                f"wines.json entry '{label}' slug={slug!r} contains a year — "
                f"cuvée slugs are vintage-agnostic (e.g. 'tignanello', not "
                f"'tignanello-2019'). See SCHEMA.md 'wines'.",
            ))
        name = e.get("name") or ""
        if _VINTAGE_IN_SLUG_RE.search(name):
            issues.append((
                "ERR",
                f"wines.json entry '{label}' name={name!r} contains a year — "
                f"cuvée pages aggregate across vintages. Vintage belongs in "
                f"scores[*] and prose, not in name.",
            ))
        for req in ("producer", "producer_name"):
            if not e.get(req):
                issues.append((
                    "ERR",
                    f"wines.json entry '{label}' missing required '{req}'",
                ))
        prod = e.get("producer")
        if prod and vineyard_slugs and prod not in vineyard_slugs:
            issues.append((
                "ERR",
                f"wines.json entry '{label}' producer={prod!r} does not resolve "
                f"to any vineyards.json slug in this region. Every cuvée must "
                f"belong to a verified producer.",
            ))
        style = e.get("style")
        if style and style not in WINE_STYLES:
            issues.append((
                "ERR",
                f"wines.json entry '{label}' style={style!r} not in controlled "
                f"vocabulary (docs/WINE_TAGS.md style axis). Valid: "
                f"{sorted(WINE_STYLES)}",
            ))
        sw = e.get("sweetness")
        if sw and sw not in WINE_SWEETNESS:
            issues.append((
                "ERR",
                f"wines.json entry '{label}' sweetness={sw!r} not in "
                f"{sorted(WINE_SWEETNESS)}",
            ))
        taste = e.get("taste")
        if taste is None:
            issues.append((
                "WARN",
                f"wines.json entry '{label}' missing 'taste' object — page "
                f"hero will be bare without aroma/palate/body/tannin/acidity",
            ))
        elif not isinstance(taste, dict):
            issues.append((
                "ERR",
                f"wines.json entry '{label}' taste must be an object",
            ))
        else:
            for axis_key, vocab in (("body", WINE_BODY),
                                    ("tannin", WINE_TANNIN),
                                    ("acidity", WINE_ACIDITY)):
                val = taste.get(axis_key)
                if val and val not in vocab:
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' taste.{axis_key}={val!r} "
                        f"not in {sorted(vocab)}",
                    ))
            for arr_key in ("aroma", "palate"):
                arr = taste.get(arr_key)
                if arr is not None and not isinstance(arr, list):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' taste.{arr_key} must be "
                        f"an array of descriptor strings",
                    ))
            if not taste.get("summary"):
                issues.append((
                    "WARN",
                    f"wines.json entry '{label}' taste.summary missing — "
                    f"renders as cuvée page hero",
                ))
        var = e.get("varietals")
        if var is None:
            issues.append((
                "ERR",
                f"wines.json entry '{label}' varietals missing — every cuvée "
                f"declares at least one grape",
            ))
        elif not isinstance(var, list) or not var:
            issues.append((
                "ERR",
                f"wines.json entry '{label}' varietals must be a non-empty "
                f"array of {{grape, pct?}} objects",
            ))
        else:
            for j, v in enumerate(var):
                if not isinstance(v, dict) or not v.get("grape"):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' varietals[{j}] must be "
                        f"an object with 'grape' key (pct optional)",
                    ))
        pairings = e.get("pairings")
        if not pairings:
            issues.append((
                "WARN",
                f"wines.json entry '{label}' pairings empty — the food-and-wine "
                f"section is the cuvée page's strongest TJ cross-link surface",
            ))
        elif not isinstance(pairings, list):
            issues.append((
                "ERR",
                f"wines.json entry '{label}' pairings must be an array",
            ))
        else:
            for j, p in enumerate(pairings):
                if not isinstance(p, dict):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' pairings[{j}] must be an "
                        f"object {{dish, why, tablejourney_ref}}",
                    ))
                    continue
                if not p.get("dish") or not p.get("why"):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' pairings[{j}] requires "
                        f"both 'dish' and 'why'",
                    ))
                tjref = p.get("tablejourney_ref")
                if tjref is None:
                    continue
                if not isinstance(tjref, str):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' pairings[{j}].tablejourney_ref "
                        f"must be a path string or null",
                    ))
                elif tjref.startswith("http") or tjref.startswith("/"):
                    issues.append((
                        "WARN",
                        f"wines.json entry '{label}' pairings[{j}].tablejourney_ref"
                        f"={tjref!r} should be a path like "
                        f"'italy/florence/restaurants/trattoria-mario', not a URL "
                        f"or leading-slash path",
                    ))
        tags = e.get("tags")
        if not tags:
            issues.append((
                "WARN",
                f"wines.json entry '{label}' tags empty — cuvée will not appear "
                f"in any /tag/<slug>/ filter index (target 10-20 tags)",
            ))
        elif not isinstance(tags, list):
            issues.append((
                "ERR",
                f"wines.json entry '{label}' tags must be an array of strings",
            ))
        else:
            for t in tags:
                if not isinstance(t, str):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' tags contains non-string "
                        f"value {t!r}",
                    ))
                    continue
                is_derived = (
                    t in WINE_DERIVED_TAGS
                    or any(t.startswith(p) for p in WINE_DERIVED_TAG_PREFIXES)
                )
                if is_derived:
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' has DERIVED tag {t!r} — "
                        f"price / ageing / production / grape / world / "
                        f"sweetness tags are added by generators automatically "
                        f"from other fields. See docs/WINE_TAGS.md.",
                    ))
                    continue
                if tag_vocab and t not in tag_vocab:
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' has unknown tag {t!r} — "
                        f"not defined in docs/WINE_TAGS.md",
                    ))
        hist = e.get("history")
        if hist is not None:
            if not isinstance(hist, dict):
                issues.append((
                    "ERR",
                    f"wines.json entry '{label}' history must be an object",
                ))
            else:
                yr = hist.get("origin_year")
                if yr is not None and not (isinstance(yr, int) and 1100 <= yr <= 2100):
                    issues.append((
                        "ERR",
                        f"wines.json entry '{label}' history.origin_year="
                        f"{yr!r} must be a 4-digit year between 1100 and 2100",
                    ))
        fv = e.get("first_vintage")
        if fv is not None and not (isinstance(fv, int) and 1100 <= fv <= 2100):
            issues.append((
                "ERR",
                f"wines.json entry '{label}' first_vintage={fv!r} must be a "
                f"4-digit year between 1100 and 2100",
            ))


def _check_entity_entries(fname: str, entries: list, issues: list) -> None:
    """Every entry must have slug+name; address requirement depends on topic class."""
    seen_slugs: set[str] = set()
    address_required = fname in VENUE_TOPICS
    address_optional_warn = fname in SOFT_ADDRESS_TOPICS  # tours/festivals/classes
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            issues.append(("ERR", f"{fname}[{i}] is not a dict"))
            continue
        ent_label = _entry_name(e) or e.get("slug") or f"index {i}"
        if not e.get("slug"):
            issues.append(("ERR", f"{fname} entry '{ent_label}' missing required 'slug'"))
        elif e["slug"] in seen_slugs:
            issues.append(("ERR", f"{fname} duplicate slug '{e['slug']}'"))
        else:
            seen_slugs.add(e["slug"])
        if not _entry_name(e):
            issues.append(("ERR", f"{fname} entry '{ent_label}' missing required 'name' (tours may use 'operator')"))
        addr = _entry_address(e)
        if address_required and not addr:
            issues.append(("ERR", f"{fname} entry '{ent_label}' missing required 'address'"))
        elif address_optional_warn and not addr:
            issues.append(("WARN", f"{fname} entry '{ent_label}' has no 'address' or 'meeting_point' (map link will not render)"))
        _check_editorial_score(fname, e, ent_label, issues)
        # price_tier must be symbol form ($/€/£/¥). 2026-05-19: batch-3
        # agents shipped 'EUR EUR EUR' literal strings which exploded the
        # filter chip UI on every topic page. Reject ASCII / spelled-out
        # forms here so it can't happen again.
        pt = e.get("price_tier")
        if isinstance(pt, str) and pt.strip():
            pt_chars = set(pt.strip())
            if not pt_chars.issubset({"$", "€", "£", "¥"}):
                issues.append((
                    "ERR",
                    f"{fname} entry '{ent_label}' price_tier={pt!r} must be symbol-only "
                    f"($, €, £, ¥), not ASCII or spelled-out currency codes. "
                    f"Run scripts/normalize_price_tiers.py to mass-fix.",
                ))
        if fname not in VERIFIED_OPTIONAL_TOPICS:
            _check_verified_block(fname, e, ent_label, issues)
        # Truncation detector on prose fields. Sonnet has been observed
        # truncating to hit length caps, ending fields with stop-word+period.
        # SKIPPED for wines.json — cuvée descriptions legitimately end in
        # flavor descriptors ("vivid, textured, and tropical."), drinking
        # windows ("...and extraordinary longevity."), and other terse
        # closers that trip the venue-tuned patterns. QA1's taste-note
        # sourcing check (section I) is the right line of defence for
        # wine prose quality.
        if fname != "wines.json":
            for prose_field in ("description", "why_hidden", "tip", "must_order"):
                v = e.get(prose_field)
                if v and looks_truncated(v):
                    issues.append((
                        "ERR",
                        f"{fname} entry '{ent_label}' {prose_field} ends mid-sentence (truncation): {v!r}"
                    ))
        # URL-shape check on booking/affiliate links. We can't verify the URL
        # is reachable, but we can catch the common subagent failure of
        # writing the restaurant homepage WITHOUT the scheme.
        for url_field in URL_FIELDS:
            v = e.get(url_field)
            if v and not URL_RE.match(str(v)):
                issues.append((
                    "WARN",
                    f"{fname} entry '{ent_label}' {url_field}={v!r} does not look like a URL (missing http:// or https://)"
                ))
        # Length caps. Description is ERR (becomes the meta description
        # verbatim and falls back to auto-generated copy if out of band);
        # the rest are WARN nudges. Festivals/tours/classes have their own
        # description cap since those pages render the description as the
        # page lede, not just SEO.
        desc_key = "entity.description"
        if fname == "festivals.json":
            desc_key = "food_festivals.description"
        elif fname == "food-tours.json":
            desc_key = "food_tours.description"
        elif fname == "cooking-classes.json":
            desc_key = "cooking_classes.description"
        _check_length(e.get("description"),  desc_key,            f"{fname} '{ent_label}' description",  issues)
        _check_length(e.get("must_order"),  "entity.must_order",  f"{fname} '{ent_label}' must_order",   issues)
        _check_length(e.get("tip"),         "entity.tip",         f"{fname} '{ent_label}' tip",          issues)
        _check_length(e.get("why_hidden"),  "entity.why_hidden",  f"{fname} '{ent_label}' why_hidden",   issues)


def validate_city(country: str, city: str | None, data_dir: Path, errors_only: bool, strict: bool = False):
    label = f"{country}/{city}" if city else country
    issues = []  # list of (level, message)

    # Country-level data dir (city=None) only carries destination + seo +
    # optional rollups. It doesn't ship the 24 topic files — those live
    # under each region's data dir. Skip the topic-file required-set in
    # this case.
    is_country_level = city is None

    # 1. required files exist
    if is_country_level:
        # Country needs only region.json. neighborhoods + 24 topics belong to regions.
        required_files = ["region.json"]
    else:
        required_files = REQUIRED_FILES + list(TOPIC_FILES_TO_KEY)
    for fname in required_files:
        if not (data_dir / fname).exists():
            issues.append(("ERR", f"missing {fname}"))

    # 2. region.json shape and SEO essentials
    region_path = data_dir / "region.json"
    if region_path.exists():
        try:
            region = json.loads(region_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(("ERR", f"region.json invalid JSON: {exc}"))
            region = {}
        dest = region.get("destination", {})
        seo = region.get("seo", {})
        if not dest.get("name"):
            issues.append(("ERR", "destination.name is empty"))
        if not dest.get("country"):
            issues.append(("WARN", "destination.country is empty"))
        if not dest.get("hero_image"):
            # Required for ship. Without a hero_image the homepage marquee,
            # the /<country>/ country stub, and the region hub all render
            # a bare letter placeholder. Bumped from WARN -> ERR on
            # 2026-05-23: agent prompt now mandates image sourcing per
            # docs/IMAGE_SOURCES.md.
            issues.append((
                "ERR",
                "destination.hero_image is empty (required; see docs/IMAGE_SOURCES.md — Unsplash first, then Wikimedia Commons)"
            ))
        else:
            # If the hero_image is set, it's hosted somewhere; we must record
            # provenance to defend against takedown / DMCA. WARN-level so a
            # stub city in progress doesn't ERR, but the warning is loud.
            for fld in IMAGE_PROVENANCE_FIELDS:
                if not dest.get(fld):
                    issues.append((
                        "WARN",
                        f"destination.{fld} is empty (image provenance required; see docs/IMAGE_SOURCES.md)"
                    ))
            # hero_image URL shape (if remote).
            hi = str(dest.get("hero_image", ""))
            if hi and "://" in hi and not URL_RE.match(hi):
                issues.append(("WARN", f"destination.hero_image={hi!r} does not look like a URL"))
        # destination-level length caps
        _check_length(dest.get("tagline"),          "destination.tagline",          "destination.tagline",          issues)
        _check_length(dest.get("overview"),         "destination.overview",         "destination.overview",         issues)
        _check_length(dest.get("hero_image_alt"),   "destination.hero_image_alt",   "destination.hero_image_alt",   issues)
        # research.food_culture_summary is on region.json under research{}
        _check_length(region.get("research", {}).get("food_culture_summary"),
                      "research.food_culture_summary",
                      "region.json:research.food_culture_summary", issues)

        all_pages = seo.get("pages") or {}
        if not all_pages.get("index", {}).get("title"):
            issues.append(("ERR", "seo.pages.index.title is empty"))
        if not all_pages.get("index", {}).get("description"):
            issues.append(("ERR", "seo.pages.index.description is empty"))
        # Per-topic SEO caps: every populated <topic> page (and index) gets banded.
        for topic_key, page in all_pages.items():
            if not isinstance(page, dict):
                continue
            _check_length(page.get("title"),       "seo.pages.<topic>.title",       f"seo.pages.{topic_key}.title",       issues)
            _check_length(page.get("description"), "seo.pages.<topic>.description", f"seo.pages.{topic_key}.description", issues)

    # 3. topic files: shape + non-empty + no placeholder
    for fname, key in TOPIC_FILES_TO_KEY.items():
        path = data_dir / fname
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(("ERR", f"{fname} invalid JSON: {exc}"))
            continue
        if not isinstance(data, dict) or key not in data:
            issues.append(("ERR", f"{fname} must be a dict containing key '{key}'"))
            continue
        payload = data[key]
        if fname in DICT_OR_LIST_TOPICS:
            # Either a bucketed dict (Bordeaux) or a flat list (canonical).
            if not isinstance(payload, (dict, list)):
                issues.append(("ERR", f"{fname}[{key}] expected dict or list, got {type(payload).__name__}"))
            elif isinstance(payload, dict) and not any(payload.values()):
                issues.append(("WARN", f"{fname} is empty (no categories filled)"))
            elif isinstance(payload, list) and len(payload) == 0:
                issues.append(("ERR", f"{fname} has 0 entries (skeleton state — research never filled this topic)"))
        elif fname in DICT_TOPICS:
            if not isinstance(payload, dict):
                issues.append(("ERR", f"{fname}[{key}] expected dict, got {type(payload).__name__}"))
            else:
                if not any(payload.values()):
                    issues.append(("WARN", f"{fname} is empty (no categories filled)"))
        else:
            if not isinstance(payload, list):
                issues.append(("ERR", f"{fname}[{key}] expected list, got {type(payload).__name__}"))
            elif len(payload) == 0:
                issues.append(("ERR", f"{fname} has 0 entries (skeleton state — research never filled this topic)"))
            elif len(payload) < 5:
                issues.append(("WARN", f"{fname} has only {len(payload)} entries (target >=10 for SEO depth)"))
        if has_placeholder(data):
            issues.append(("ERR", f"{fname} contains TODO/placeholder text"))
        if has_em_dash(data):
            issues.append(("ERR", f"{fname} contains em/en dashes (banned, looks AI-generated). Replace with commas/periods/colons or rephrase."))

        # 3a. per-entry shape checks on entity-list topics
        if fname in ENTITY_LIST_TOPICS and isinstance(payload, list):
            _check_entity_entries(fname, payload, issues)

        # 3a'. wines.json: cuvée-specific shape + cross-ref checks.
        # Requires vineyards.json so the producer cross-reference can
        # validate. If vineyards.json is missing the cross-ref check
        # becomes a no-op (other layers complain about the missing file).
        if fname == "wines.json" and isinstance(payload, list):
            vineyard_slugs = _topic_slug_set(data_dir, "vineyards.json", "vineyards")
            _check_wine_entries(fname, payload, vineyard_slugs, issues)

        # 3a''. signature-wines.json: every slug must also appear in
        # wines.json (signature-wines is a curated subset, NOT parallel
        # data). The full page lives at /wine/<producer>/<slug>/ from
        # wines.json; signature-wines drives the region's "iconic bottles"
        # carousel only.
        if fname == "signature-wines.json" and isinstance(payload, list):
            wines_slugs = _topic_slug_set(data_dir, "wines.json", "wines")
            if wines_slugs:  # only enforce once wines.json exists
                for e in payload:
                    if not isinstance(e, dict) or not e.get("slug"):
                        continue
                    if e["slug"] not in wines_slugs:
                        sw_label = e.get("name") or e["slug"]
                        issues.append((
                            "ERR",
                            f"signature-wines.json '{sw_label}' slug={e['slug']!r} "
                            f"not in wines.json. signature-wines is a curated "
                            f"subset of wines.json — every slug must reference "
                            f"a real cuvée page. See SCHEMA.md 'wines'.",
                        ))

        # 3b. dietary is a dict-of-lists; check each leaf list
        if fname == "dietary.json" and isinstance(payload, dict):
            for diet_key, places in payload.items():
                if isinstance(places, list) and places:
                    _check_entity_entries(f"dietary.json[{diet_key}]", places, issues)

        # 3b'. neighborhoods.json: dict with "neighborhoods" list. Each entry
        # has a vibe blurb; aliases (entity.neighborhood values it covers) and
        # slug are recommended for cross-cut bridging.
        if fname == "neighborhoods.json":
            hoods = payload.get("neighborhoods") if isinstance(payload, dict) else payload
            if isinstance(hoods, list):
                for i, n in enumerate(hoods):
                    if not isinstance(n, dict):
                        continue
                    n_label = n.get("name") or n.get("slug") or f"index {i}"
                    _check_length(n.get("vibe"), "neighborhood.vibe",
                                  f"neighborhoods.json '{n_label}' vibe", issues)
                    if not n.get("slug"):
                        issues.append(("WARN", f"neighborhoods.json '{n_label}' missing slug — hub card can't link to a cross-cut"))
                    if not n.get("aliases"):
                        issues.append(("WARN", f"neighborhoods.json '{n_label}' missing aliases — entity.neighborhood values won't map to this editorial entry"))

        # 3b''. food-history.json: dict with key_eras + immigrant_influences +
        # signature_innovations. The page is mostly prose so caps matter.
        if fname == "food-history.json" and isinstance(payload, dict):
            for i, era in enumerate(payload.get("key_eras") or []):
                if not isinstance(era, dict):
                    continue
                era_label = era.get("name") or era.get("period") or f"key_eras[{i}]"
                summary = era.get("summary") or era.get("description")
                _check_length(summary, "food_history.key_eras[].summary",
                              f"food-history.json era '{era_label}' summary", issues)
            for i, inf in enumerate(payload.get("immigrant_influences") or []):
                if isinstance(inf, dict):
                    inf_label = inf.get("community") or f"immigrant_influences[{i}]"
                    _check_length(inf.get("contribution"),
                                  "food_history.immigrant_influences[].contribution",
                                  f"food-history.json influence '{inf_label}' contribution", issues)
            for i, inn in enumerate(payload.get("signature_innovations") or []):
                if isinstance(inn, str):
                    _check_length(inn, "food_history.signature_innovations[]",
                                  f"food-history.json signature_innovations[{i}]", issues)

        # 3b'''. seasonal-food.json: dict keyed by season. Each season is a
        # blurb (string) or {summary, ...} dict.
        if fname == "seasonal-food.json" and isinstance(payload, dict):
            for season, blurb in payload.items():
                if isinstance(blurb, str):
                    _check_length(blurb, "seasonal_food.season",
                                  f"seasonal-food.json '{season}'", issues)
                elif isinstance(blurb, dict):
                    _check_length(blurb.get("summary") or blurb.get("description"),
                                  "seasonal_food.season",
                                  f"seasonal-food.json '{season}' summary", issues)

        # 3b''''. itineraries.json: list of plans with days[*].activities.
        if fname == "itineraries.json" and isinstance(payload, list):
            for i, it in enumerate(payload):
                if not isinstance(it, dict):
                    continue
                it_label = it.get("title") or it.get("slug") or f"index {i}"
                for j, day in enumerate(it.get("days") or []):
                    if not isinstance(day, dict):
                        continue
                    _check_length(day.get("activities"),
                                  "itineraries[].days[].activities",
                                  f"itineraries.json '{it_label}' day {j} activities", issues)

        # 3c. signature-dishes entries need slug+name (no address) and
        #     should have make_it_yourself (WARN, not ERR; recipes are
        #     strongly encouraged but allowed to be added later).
        if fname == "signature-dishes.json" and isinstance(payload, list):
            sd_slugs: set[str] = set()
            for i, e in enumerate(payload):
                if not isinstance(e, dict):
                    issues.append(("ERR", f"signature-dishes.json[{i}] is not a dict"))
                    continue
                dish_label = e.get("name") or e.get("slug") or f"index {i}"
                if not e.get("slug"):
                    issues.append(("ERR", f"signature-dishes.json entry '{dish_label}' missing required 'slug'"))
                elif e["slug"] in sd_slugs:
                    issues.append(("ERR", f"signature-dishes.json duplicate slug '{e['slug']}'"))
                else:
                    sd_slugs.add(e["slug"])
                if not e.get("name"):
                    issues.append(("ERR", f"signature-dishes.json entry '{dish_label}' missing required 'name'"))
                _check_editorial_score("signature-dishes.json", e, dish_label, issues)
                # make_it_yourself: WARN if absent
                miy = e.get("make_it_yourself")
                if not miy:
                    issues.append(("WARN", f"signature-dishes.json entry '{dish_label}' missing make_it_yourself recipe block (strongly encouraged; see SCHEMA.md)"))
                elif isinstance(miy, dict):
                    if not miy.get("ingredients"):
                        issues.append(("ERR", f"signature-dishes.json entry '{dish_label}' make_it_yourself.ingredients is required"))
                    if not miy.get("method"):
                        issues.append(("ERR", f"signature-dishes.json entry '{dish_label}' make_it_yourself.method is required"))
                    _check_length(miy.get("tip"), "dish.make_it_yourself.tip",
                                  f"signature-dishes.json '{dish_label}' make_it_yourself.tip", issues)
                # Dish-level length caps. description is the page lede; history
                # is the body copy that powers the speakable schema.
                _check_length(e.get("description"), "dish.description",
                              f"signature-dishes.json '{dish_label}' description", issues)
                _check_length(e.get("history"),     "dish.history",
                              f"signature-dishes.json '{dish_label}' history", issues)

            # 3d. where_to_eat cross-reference. Each entry in
            # signature_dishes[].where_to_eat should be the NAME of a
            # restaurant that exists in restaurants.json /
            # casual-dining.json / fine-dining.json for this city. The
            # cross-cut generator resolves these references by name, and
            # silently drops the ones that don't match. Surface that here
            # so the subagent fixes the references before render.
            # Cross-cut generator resolves where_to_eat names against EVERY
            # venue-style topic, not just restaurants. Mirror that pool here
            # so the validator doesn't false-positive on perfectly fine refs
            # to bouillons (budget-eating), bakeries (cafes), street stalls
            # (street-food), etc.
            restaurant_names: set[str] = set()
            for ref_fname in (
                "restaurants.json", "casual-dining.json", "fine-dining.json",
                "cafes.json", "bakeries.json", "coffee-roasters.json",
                "wine-bars.json", "bars.json", "street-food.json",
                "breweries.json", "markets.json", "budget-eating.json",
                "hidden-gems.json", "brunch.json", "late-night.json",
            ):
                ref_path = data_dir / ref_fname
                if not ref_path.exists():
                    continue
                try:
                    ref_data = json.loads(ref_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                ref_key = TOPIC_FILES_TO_KEY[ref_fname]
                for r in ref_data.get(ref_key) or []:
                    if isinstance(r, dict) and r.get("name"):
                        restaurant_names.add(r["name"])
            if restaurant_names:  # only validate when we have something to match against
                for e in payload:
                    if not isinstance(e, dict):
                        continue
                    dish_label = e.get("name") or e.get("slug") or "?"
                    wte = e.get("where_to_eat") or []
                    if isinstance(wte, list):
                        for ref in wte:
                            if isinstance(ref, str) and ref not in restaurant_names:
                                issues.append((
                                    "WARN",
                                    f"signature-dishes.json entry '{dish_label}' where_to_eat references {ref!r} which is not in any venue file (restaurants / casual-dining / fine-dining / cafes / bakeries / coffee-roasters / wine-bars / bars / street-food / breweries / markets / budget-eating / hidden-gems / brunch / late-night); cross-cut /dish/<slug>/ will skip it"
                                ))

    # 4. city.json sanity
    city_path = data_dir / "city.json"
    if city_path.exists():
        try:
            city_data = json.loads(city_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(("ERR", f"city.json invalid JSON: {exc}"))
            city_data = {}
        if not city_data.get("food_culture_summary"):
            issues.append(("ERR", "city.json.food_culture_summary is empty (city hub will look bare)"))

    # In --strict mode, every WARN is upgraded to ERR. Subagents publishing
    # new cities should run with --strict so length caps act as hard gates;
    # ship_city.sh runs without --strict so already-shipped cities (whose
    # descriptions predate the cap policy) still ship while the renderer's
    # _meta_desc fallback handles the short ones.
    if strict:
        issues = [("ERR", msg) if lvl == "WARN" else (lvl, msg) for lvl, msg in issues]

    # report
    filtered = [(lvl, msg) for lvl, msg in issues if not errors_only or lvl == "ERR"]
    status = "PASS"
    if any(lvl == "ERR" for lvl, _ in issues):
        status = "FAIL"
    elif any(lvl == "WARN" for lvl, _ in issues):
        status = "WARN"
    print(f"[{status}] {label}")
    for lvl, msg in filtered:
        print(f"   {lvl}: {msg}")
    return any(lvl == "ERR" for lvl, _ in issues)


def main() -> int:
    p = argparse.ArgumentParser(description="Validate TableJourney site-data.")
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--errors-only", action="store_true")
    p.add_argument("--warn-only", action="store_true", help="never exit non-zero")
    p.add_argument("--strict", action="store_true",
                   help="treat every WARN as ERR (use when launching a fresh "
                        "city via a subagent so length caps act as hard gates)")
    args = p.parse_args()

    any_errors = False
    found = False
    for country, city, data_dir in discover_cities(args.country, args.city):
        found = True
        any_errors |= validate_city(country, city, data_dir, args.errors_only, strict=args.strict)
    if not found:
        print("No cities found.")
        return 0
    return 0 if (args.warn_only or not any_errors) else 1


if __name__ == "__main__":
    raise SystemExit(main())
