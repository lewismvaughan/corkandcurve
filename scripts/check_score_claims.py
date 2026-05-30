#!/usr/bin/env python3
"""Flag fabricated critic-score / ranking claims that hide in PROSE.

Score fabrication is the #1 recurring credibility defect on this site
(see memory feedback-score-fabrication-pattern). QA's `scores[]` audit
does not catch claims buried in free text: Sicily 2026-05-26 shipped
research with `scores: []` on every cuvée yet 26 fabricated claims
("WA awarded 95+ points", "Wine Spectator Top 100", "world's 50 greatest
dessert wines") sat in `wines.json` `history.milestones[*].event` and
`description`. Both Sonnet QA passes missed the class; Opus caught it.

This gate scans every free-text field of wines.json + vineyards.json for:
  1. a numeric point score (90-100 near point/pt/punti/100)
  2. a critic/publication name adjacent to a high number
  3. a "Top N / greatest / best in the world" ranking phrase

It is WARN-only by default (exit 0): a regex cannot tell a fabricated
claim from a REAL score that a researcher merely placed in prose instead
of the structured `scores[]` array (e.g. Margaux's genuine 100-pt William
Kelley review). It SURFACES the class so QA Section C0 can adjudicate each
hit (move a real score into scores[] with a full citation, or delete a
fabrication). Genuine non-numeric awards (Tre Bicchieri, gold medal, DOC
granted) do NOT match. Pass --strict to make any hit a HARD fail (exit 1)
for a region you've already cleaned and want to keep clean.

Usage:
    python3 scripts/check_score_claims.py --country italy --city sicily
    python3 scripts/check_score_claims.py --all
    python3 scripts/check_score_claims.py --country italy --city sicily --strict
Exit 0 (WARN) unless --strict and a claim is found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# Free-text fields worth scanning across any entity dict.
# Priorat 2026-05-29: Opus found 11 soft-superlatives surviving in looser-
# register colour-copy fields (`vibe`, `what_locals_love`, `wine_program`,
# `where_to_buy`) where research agents tuck "punchy takes" — added below.
TEXT_FIELDS = ("event", "description", "summary", "tip", "note", "history",
               "blurb", "why", "headline", "intro",
               "vibe", "what_locals_love", "wine_program", "where_to_buy",
               "highlight", "atmosphere", "scene", "service")

CRITICS = (r"parker", r"wine\s*advocate", r"\bWA\b", r"wine\s*spectator",
           r"\bWS\b", r"james\s*suckling", r"\bJS\b", r"vinous", r"galloni",
           r"tim\s*atkin", r"decanter", r"falstaff", r"robert\s*parker",
           r"wine\s*enthusiast", r"\bWE\b", r"jancis\s*robinson")

# 90-100 next to a points word, e.g. "95 points", "95+ pts", "100/100".
RE_POINTS = re.compile(r"\b(?:9[0-9]|100)\s*\+?\s*(?:point|pt|pts|punti|/\s*100)\b", re.I)
# A critic/publication name within ~25 chars of a high (85-100) number.
RE_CRITIC_NUM = re.compile(r"(?:" + "|".join(CRITICS) + r")\D{0,25}\b(?:8[5-9]|9[0-9]|100)\b", re.I)
RE_NUM_CRITIC = re.compile(r"\b(?:8[5-9]|9[0-9]|100)\b\D{0,25}(?:" + "|".join(CRITICS) + r")", re.I)
# Ranking phrases (hard ranking claims).
RE_RANK = re.compile(
    r"\btop\s*\d+\b(?:[^.]{0,40}\bwines?\b)?"
    r"|world'?s\s+\d+\s+(?:greatest|best|finest)"
    r"|(?:greatest|best|finest)\s+\d+\s+wines?"
    r"|best\b[^.]{0,40}\bin the world\b"
    r"|top\s+\d+\s+[^.]{0,30}(?:wine|dessert|sweet|sparkling)",
    re.I,
)

# Soft-superlative phrases (added 2026-05-28 after Ribera Opus found 12).
# Same categorical C0 ban applies — these belong to the same fabrication class
# as the hard rankings, just dressed softer. Examples Opus stripped:
# "Spain's most storied red", "anywhere in the world", "one of the great
# wines of the Burgos sector", "the legendary Unico", "put the region on
# the world map", "regarded as the defining natural-wine producer in the
# appellation", "the most prestigious postal code in Ribera del Duero".
SOFT_ADJ = r"(?:celebrated|prominent|important|iconic|defining|prestigious|storied|legendary|celebrated|renowned|concentrated|benchmark|reference|famous|prized|sought-after|coveted|serious|refined|finest|best-known|powerful|unparalleled|unmatched|extraordinary|premier|significant)"
COUNTRIES = r"(?:spain|italy|france|portugal|germany|austria|chile|argentina|south\s*africa|australia|new\s*zealand|hungary|greece)"
RE_SOFT_RANK = re.compile(
    # "<country>'s most <adj>" / "the world's most <adj>"
    rf"\b(?:{COUNTRIES}|the\s+world)'?s\s+most\s+\w+"
    # "anywhere in the world", "best ... in the world"
    rf"|\banywhere\s+in\s+the\s+world\b"
    # "one of the great <category>", "one of the most <adj> <X>"
    rf"|\bone\s+of\s+the\s+(?:great|most\s+{SOFT_ADJ})\b"
    # "the legendary <entity>"
    rf"|\bthe\s+legendary\s+\w+"
    # "put <region> on the (world) map"
    rf"|\bput\s+(?:the\s+)?\w[\w\s-]{{0,30}}?\s+on\s+the\s+(?:world\s+)?map\b"
    # "regarded as the defining", "the defining X"
    rf"|\bregarded\s+as\s+the\s+defining\b"
    rf"|\bthe\s+defining\s+\w[\w-]*\s+(?:in|of)\b"
    # "the most prestigious X"
    rf"|\bthe\s+most\s+prestigious\s+\w+"
    # "the single most <adj>" (Tokaj 2026-05-29 — Opus found 14 in this variant)
    rf"|\bthe\s+single\s+most\s+\w+"
    # "the most historically significant"
    rf"|\bmost\s+historically\s+significant\b"
    # "synonymous with <country>'s great X"
    rf"|\bsynonymous\s+with\s+(?:one\s+of\s+)?{COUNTRIES}'?s\s+(?:great|greatest)\b"
    # Comparative-ranking tier (Alsace 2026-05-30 — Opus found 16). Researchers
    # default to assuming "the largest" claims are factual scaffolding; they
    # require producer-site / consortium-roster sourcing. State an absolute
    # number ("130 hectares") instead of the relative rank.
    # "the largest/leading/biggest <X>" where X is a wine-trade entity
    rf"|\bthe\s+(?:largest|leading|biggest|finest|oldest|earliest|first|highest|widest|youngest|smallest)\s+(?:[A-Za-zé\-]+\s+){{0,4}}(?:cooperative|producer|estate|operator|distillery|cellar|maison|domaine|house|grower|cuv[ée]e|cremant|champagne|appellation|cru|landholder|reference|bottling)\b"
    # "<world|continent|country>'s oldest/largest/biggest/first <X>"
    rf"|\b(?:world|europe|france|germany|italy|spain|austria|hungary|portugal|alsace|burgundy|tuscany|piedmont|veneto|champagne|rh[oô]ne|bordeaux|loire|sicily|priorat|rioja|tokaj|wachau|mosel|douro)'?s\s+(?:oldest|largest|biggest|first|finest|highest|widest|earliest|second[- ]largest|third[- ]largest)\b"
    # Ordinal ranks
    rf"|\b(?:second|third|fourth|fifth)[- ](?:largest|biggest|oldest|finest|earliest|first)\b"
    # "one of the (rank)" softener exploited to bypass the strict-strip
    rf"|\bone\s+of\s+the\s+(?:largest|leading|biggest|oldest|earliest|first|finest|widest|smallest)\s+\w+\s+(?:in|of)\s+(?:the\s+)?(?:world|europe|france|germany|italy|spain|austria|hungary|portugal|alsace|burgundy|tuscany|piedmont|veneto|champagne|rh[oô]ne|bordeaux|loire|sicily|priorat|rioja|tokaj|wachau|mosel|douro)\b",
    re.I,
)

# Additional adjective-noun benchmark phrases (Wachau Opus 2026-05-28 caught
# 21 surviving). These don't fit the "one of the most X" template but carry
# the same ranking implication.
RE_BENCHMARK_NOUN = re.compile(
    r"\b(?:the\s+)?benchmark\s+(?:wine|riesling|gr[uü]ner|tempranillo|"
    r"chardonnay|amarone|barolo|champagne|cabernet|syrah|nebbiolo|"
    r"sangiovese|merlot|pinot|gamay|carignan|grenache|examples?|expression|estate)\b"
    r"|\bthe\s+village\s+benchmark\b"
    r"|\bnot\s+to\s+be\s+missed\b"
    r"|\bthe\s+reference\s+(?:wine|producer|estate|expression)\b",
    re.I,
)

# Double-hyphen as em-dash substitute (Wachau Opus 2026-05-28 caught 6 in
# long-form prose). The em-dash ban is already on real em-dashes; this
# catches the ASCII-typewriter workaround.
RE_DOUBLE_HYPHEN = re.compile(r"(?<!\w)--(?!\w)")

# Critic-attention prose without scores[] (Rheingau Opus 2026-05-30 — Kesseler
# R Spätburgunder claimed "the R label drew Wine Advocate's attention to
# Rheingau Pinot Noir in the late 1990s" with no `scores[]` citation). The
# existing RE_CRITIC_NUM only fires when a number is nearby; bare critic-
# attention prose ("Parker's attention", "WS focus", "Suckling praise")
# slips through. This regex flags any critic + attention-verb combination.
RE_CRITIC_ATTENTION = re.compile(
    r"\b(?:Parker|Wine\s+Advocate|WA|Wine\s+Spectator|WS|"
    r"James\s+Suckling|Suckling|Vinous|Galloni|Decanter|"
    r"Tim\s+Atkin|Gault|Gault\s+Millau|Falstaff|Vinum|"
    r"Jancis\s+Robinson|Robinson|Eichelmann)(?:'s)?\s+"
    r"(?:attention|focus|spotlight|praise|review|coverage|"
    r"interest|notice|nod|seal\s+of\s+approval)\b",
    re.I,
)


# First-name-only chef/sommelier/winemaker attribution risk.
# "Chef Marina" / "sommelier Roberto" without a verifiable last name +
# source is a fabrication risk (Ribera 2026-05-28 — Ambivium's fabricated
# "Chef Cristobal Munoz" was actually Marina de la Hoz).
# Alsace 2026-05-30: exclude "single-owner <Place>" and "owner <Place>"
# constructions where the capitalised following word is a known wine-region
# place name, not a first name. Place names that recurred as false positives:
# Guebwiller (Alsace), plus common Alsace/French/Italian/Spanish wine towns.
_PLACE_FALSE_POS = (
    r"Guebwiller|Ribeauvill[eé]|Riquewihr|Eguisheim|Colmar|Strasbourg|Mulhouse|"
    r"Bergheim|Hunawihr|Kaysersberg|Turckheim|Andlau|Barr|Mittelbergheim|"
    r"Dambach|Marlenheim|Wettolsheim|Wintzenheim|Rouffach|Pfaffenheim|"
    r"Bordeaux|Burgundy|Beaune|Reims|[EÉ]pernay|Avignon|Beaujeu|"
    r"Florence|Siena|Montalcino|Montepulciano|Verona|Alba|Asti|Barolo|Barbaresco|"
    r"Madrid|Logro[nñ]o|Haro|Jerez|Porto|Pinh[aã]o|Budapest|Tokaj|"
    r"Single|Family|Estate|Domaine|Maison|Castello|Bodega|Quinta|Pince"
)
RE_FIRSTNAME_ATTRIB = re.compile(
    rf"\b(?:chef|sommelier|owner|winemaker|head\s*chef)\s+"
    rf"(?!(?:{_PLACE_FALSE_POS})\b)"
    rf"[A-Z][a-z]+\b(?!\s+[A-Z])",
)


def _scan_text(s: str) -> str | None:
    if not isinstance(s, str) or not s.strip():
        return None
    if RE_POINTS.search(s):
        return "numeric-point-score"
    if RE_CRITIC_NUM.search(s) or RE_NUM_CRITIC.search(s):
        return "critic-name-near-score"
    if RE_RANK.search(s):
        return "ranking-claim"
    if RE_SOFT_RANK.search(s):
        return "soft-superlative"
    if RE_BENCHMARK_NOUN.search(s):
        return "benchmark-noun"
    if RE_DOUBLE_HYPHEN.search(s):
        return "double-hyphen-emdash"
    if RE_CRITIC_ATTENTION.search(s):
        return "critic-attention-prose"
    if RE_FIRSTNAME_ATTRIB.search(s):
        return "firstname-only-attribution"
    return None


def _walk(obj):
    """Yield (field_path, text) for every scannable string in a nested dict/list."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in TEXT_FIELDS:
                yield k, v
            else:
                yield from _walk(v)
    elif isinstance(obj, list):
        for it in obj:
            yield from _walk(it)


def check_city(country: str, city: str, strict: bool = False) -> int:
    data_dir = SITE_DATA / country / city / "data"
    if not data_dir.is_dir():
        print(f"[{country}/{city}] no such city")
        return 1
    hits = []
    # Scan ALL JSON files in the region's data/ dir, not just wines/vineyards/
    # signature-wines (Jerez 2026-05-28 Opus found 14 soft-superlatives leaked
    # into wine-festivals/wine-history/neighborhoods/budget-wines/day-trips/
    # distilleries/region.json because they weren't scanned). The same
    # categorical C0 ban applies to every prose field on every entity.
    for f in sorted(data_dir.glob("*.json")):
        fname = f.name
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        # Find list-of-entity payloads at the top level (entities are inside).
        # Some files (region.json) are a single dict — scan as one entity.
        entries = []
        if isinstance(d, dict):
            list_payloads = [v for v in d.values() if isinstance(v, list)]
            if list_payloads:
                for arr in list_payloads:
                    entries.extend(x for x in arr if isinstance(x, dict))
            else:
                entries = [d]
        elif isinstance(d, list):
            entries = [x for x in d if isinstance(x, dict)]
        for e in entries:
            if not isinstance(e, dict):
                continue
            name = e.get("name") or e.get("slug") or "?"
            for field, text in _walk(e):
                cls = _scan_text(text)
                if cls:
                    hits.append((fname, name, field, cls, text.strip()[:120]))
    if hits:
        tag = "HARD" if strict else "WARN"
        print(f"[{country}/{city}] PROSE SCORE-CLAIM(S): {len(hits)} ({tag})")
        for fname, name, field, cls, snippet in hits[:40]:
            print(f"  [{cls}] {fname} :: {name} :: {field}: \"{snippet}\"")
        print("  -> QA Section C0 must adjudicate each: move a REAL score "
              "(reviewer+points+vintage+year+source) into scores[], or DELETE a "
              "fabrication. Prose should not carry a bare critic number.")
        return 1 if strict else 0
    print(f"[{country}/{city}] no prose score-claims found.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--all", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="HARD-fail (exit 1) on any hit; default is WARN (exit 0)")
    a = p.parse_args()
    if a.all:
        rc = 0
        for cdir in sorted(SITE_DATA.iterdir()):
            if not cdir.is_dir():
                continue
            for citydir in sorted(cdir.iterdir()):
                if citydir.is_dir() and citydir.name != "data" and (citydir / "data").is_dir():
                    rc |= check_city(cdir.name, citydir.name, strict=a.strict)
        return rc
    if not (a.country and a.city):
        print("Usage: check_score_claims.py --country <c> --city <city> | --all")
        return 1
    return check_city(a.country, a.city, strict=a.strict)


if __name__ == "__main__":
    sys.exit(main())
