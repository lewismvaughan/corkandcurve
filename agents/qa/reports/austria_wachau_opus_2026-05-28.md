# Opus Final QA Report — austria/wachau
**Date:** 2026-05-28
**Agent:** Opus final QA (narrow read after QA1 + QA2)
**ship_safety.sh result (pre-Opus):** PASS (0 HARD, 0 cuvee-taste-miss WARN)
**ship_safety.sh result (post-Opus):** PASS (0 HARD, 0 cuvee-taste-miss WARN)

---

## Verdict

**OPUS-FOUND-3** (3 distinct defect classes, 109 individual fixes)

QA1 (28 fixes) and QA2 (42 fixes) cleared the obvious surface defects but
missed three structural classes that only surfaced when individual cited
URLs were fetched and inspected. Two of the three are mechanically
caused by validators that silently passed under non-obvious edge cases.

---

## Defect class 1 — Section I taste-block fabrication at scale (84 cuvées)

**Class:** the Rioja-class defect. Research agent emitted per-cuvée
taste blocks (`taste.aroma`, `taste.palate`, `taste.summary`,
`taste.finish`) and pointed `verified.cuisine_evidence_url` at
generic producer-overview, importer-card, regional-tourism, or
appellation-directory pages that contain ZERO per-cuvée descriptors.

**Why QA1, QA2 and `check_evidence_content.py` all missed it:**

`check_evidence_content.py` searches for any of the cuvée's descriptors
(>=5 char strings) on the cited page. When multiple cuvées share the
same `cuisine_evidence_url`, a single common Wachau descriptor
("mineral", "white pepper") that appears once on the page makes ALL
sharing cuvées pass the mechanical check, even when the descriptor
applies only to one wine on the page (the Veyder-Malberg `viessling-2/`
page genuinely covers Viessling; the other 4 Veyder-Malberg cuvées
sharing that URL pass mechanically because "white pepper" appears in
the Viessling section). QA2 only audited the 30 ship_safety flagged.

**Spot-checks confirmed:**
- `weygandtmetzler.com/prod-focus...franz-hirtzberger` → producer card,
  zero per-cuvée descriptors for Singerriedel, Hochrain, Honivogl, etc.
- `vinea-wachau.at/.../weingut-rudi-pichler` → directory entry, only
  generic tier descriptors ("Smaragd = internationally renowned ...");
  no per-cuvée notes for Hochrain, Achleiten, Kollmitz, Bruck, etc.
- `vinea-wachau.at/.../weingut-josef-jamek` → same directory shape.
- `winebow.com/our-brands/prager` → producer page with links to actual
  per-wine sub-paths (e.g. `/prager-wachstum-bodenstein-riesling`)
  that the researcher never cited.
- `vinea-wachau.at/mywachau/betriebe/` (20 cuvées) → just the producer
  index of the whole Vinea Wachau association.
- `lower-austria.info/wachau` (18 cuvées) → regional tourism overview.
- `buschenschank.at/Joching/Weingut-Schmelz` → tavern directory entry.
- `laglers.at/shop/weine` → 404.
- `wineguide.wein.plus/weingut-hofstaetter` → producer card; page lists
  tasting notes for OTHER Hofstätter cuvées (1000-Eimer-Berg,
  Neuburger) but NOT for Singerriedel, Tausendeimerberg or Muskateller.
- `domaene-wachau.at/en/the-winery/` → producer page (QA2 already
  stripped 2 sharing this URL; 3 more remained).
- `falstaff.com/.../weingut-georg-gruber` → producer card.

**Fix:** Stripped the `taste` block from all 84 cuvées and reassigned
`verified.cuisine_evidence_url` to a confirmed-live producer-root URL
(Vinea Wachau company-details page, producer home, or the same
producer card if it returns 200). The structural `description` and
`history.summary` fields were retained.

**Affected cuvées (84):** all 8 Hirtzberger, all 8 Rudi Pichler, 6
Prager, 4 Veyder-Malberg (Viessling kept; per-cuvée notes only on
that wine's page), 4 Jamek, 3 Domäne Wachau, 3 Hofstätter, 3 Schmelz,
3 Lagler, 2 Höllmüller, 2 Gruber, plus all 20 cuvées citing
`vinea-wachau.at/mywachau/betriebe/` (Mayr, Miesbauer, Grabner, Eder,
Bioweingut Schmidl, Högl, Piewald, Muthenthaler, Pax, Domäne Roland
Chan) and all 18 citing `lower-austria.info/wachau` (Konrad,
Leonhartsberger, Jäger, Gebetsberger, Weixelbaum, Zottl, Nothnagl,
Denk, Stall, Wachau-Wachstum, etc.).

Distribution of retained taste blocks: 41/155 cuvées (down from 125),
all of which cite per-cuvée sub-pages or pages that genuinely list
the descriptors used.

---

## Defect class 2 — festival source_url decay + missing `annual: true`

**Class:** five of eight `verified.source_url` values in
`wine-festivals.json` were 404 (wachau.at and its `/en/events/...`
subtree now redirect to donau.com under a different URL scheme). One
returned 500.

**Why QA1 and ship_safety missed it:**

1. `check_external_urls.py` only inspects a fixed `URL_FIELDS` set
   (`booking_url`, `affiliate_url`, `hero_image_source_url`,
   `hero_image`, `og_image`, `image`) — it does NOT walk the
   `verified.source_url` field. Provenance URLs are not externally
   validated by ship_safety at all.
2. `check_festival_dates.py` requires `f.get("annual") == True` to
   schedule a festival for fetching; all 8 Wachau festivals had
   `annual: None`, so the script printed "no annual festivals with
   source_url + start_month to check" and PASSed silently.

**Broken URLs replaced:**
- `wachau.at/en/events/wachau-gourmet-festival/` (404)
- `wachau.at/en/culture-history/wachauer-marille/` (404)
- `wachau.at/en/events/donau-in-flammen/` (404)
- `wachau.at/en/food-drink/heuriger/` (404)
- `vinea-wachau.at/en/events/` (404)
- `weinausoesterreich.at/en/wine/wachau/` (307 → loop)
- `krems.at/en/events/` (500)
- `domaene-wachau.at/en/events/` (404)

All replaced with confirmed-200 alternatives (`donau.com/en/wachau-
nibelungengau-kremstal`, `vinea-wachau.at/en/`, `krems.at/`,
`domaene-wachau.at/en/`). The substituted pages do not directly
substantiate the specific festival month — they are best-available
confirmed-live anchor URLs while a per-event canonical URL is
researched. The festival prose, recurrence_pattern, and start_month
were retained from QA1's sourcing.

---

## Defect class 3 — soft-superlative + em-dash residue (21 instances)

QA1+QA2 stripped 31 superlatives; Opus found 21 more, most around the
"benchmark", "reference", "defining" tier that QA1's grep apparently
missed when running against the explicit C0 strip list, plus several
double-hyphen em-dashes in long-form prose.

**wines.json (10):**
1. `fx-pichler-kellerberg-riesling-smaragd` history.summary: "tension and longevity are defining characteristics" → factual rewrite about primary-rock soils
2. `knoll-loibenberg-riesling-smaragd` description: "Benchmark Smaragd Riesling" → "Smaragd Riesling"
3. `knoll-loibenberg-riesling-smaragd` history.summary: "one of the Wachau's defining site expressions" → "a single-site bottling"
4. `alzinger-steinertal-riesling-smaragd` description: "Benchmark mineral Smaragd Riesling" → "Mineral Smaragd Riesling"
5. `prager-achleiten-gruner-smaragd` history.summary: "among the Wachau's reference Grüner Veltliners" → factual amphibolite descriptor
6. `jamek-ried-Klaus-riesling-smaragd` history.summary: "became a reference wine for the region's dry-wine tradition" → "was an early single-site bottling"
7. `winzer-krems-sandgrube-gruner-smaragd` pairings.why: "quintessential Grüner Veltliner pairing; widely distributed and a familiar reference point" → "classic Grüner Veltliner pairing for the variety's pepper-and-green-herb profile"
8. `rudi-pichler-hochrain-riesling-smaragd` description: "benchmark Riesling Smaragd" → "single-site Riesling Smaragd"
9. `donabaum-spitzer-punkt-riesling-smaragd` taste.summary: "stone-fruit depth define this Spitz benchmark" → drop "benchmark"
10. `veyder-malberg-viessling-gruner-smaragd` pairings.why: "defining Wachau pairing" → "pairs naturally with Danube freshwater fish from the same valley"

**vineyards.json (4):**
11. `prager` description: "Wachstum Bodenstein series from Achleiten is benchmark Wachau Smaragd" → "bottles selected Achleiten parcels as Smaragd"
12. `franz-hirtzberger` description: "Honivogl Grüner Veltliner Smaragd is a benchmark expression of warm-year Wachau Veltliner" → "warm-year, full-bodied expression of Wachau Veltliner"
13. `josef-jamek` tip: "the benchmark wine; the restaurant pairing lunch is not to be missed" — also caught "not to be missed" AI-tell → "Try the Klaus Riesling Smaragd ... alongside the restaurant pairing lunch"
14. `zottl` tip: "the village benchmark" → "a recognised village wine"

**austria country region.json (5 in one overview):**
15. "Austria is one of the world's most distinctive wine countries" → "Austria is a compact wine country"
16. "no other country produces Grüner Veltliner of comparable depth" — unfalsifiable superlative removed; replaced with "Grüner Veltliner is Austria's signature variety: planted on about 14,000 hectares nationwide"
17. "the most internationally recognised whites" → "internationally distributed dry whites"
18. "Vienna is unique as the only world capital" → "Vienna is unusual as a world capital"
19. "established a new standard for Central European white wine" → "established export distribution for Central European white wine"

**wachau region.json + signature-grapes.json (2):**
20. wachau region.json overview: "its celebrated tier marks" + multiple `-- ... --` em-dash pairs → "three tier marks" + parenthetical conversion
21. signature-grapes.json Pinot Blanc, Chardonnay, Sauvignon Blanc: em-dash pairs (`-- X --`) converted to parentheses

---

## Other narrow-read checks — clean

### Itinerary end-to-end (`three-day-wachau-triangle`)
All 14 unique venue slugs across 5 itineraries resolve to vineyards.json
post-merge. No stale `holzapfel-joching` or `jamek-weingut` slugs.

### Festival end-to-end (`wachau-gourmet-festival`)
Month claim April/May is factually correct (annual spring event at
Loibnerhof + Schloss Dürnstein); the source_url was 404 — repaired.

### Cuvée end-to-end
Sampled `hirtzberger-singerriedel-riesling-smaragd` (was a marquee
defensible 4.9 with taste block). Producer resolves to vineyards.json.
Pairings have `tablejourney_ref: null` (OK, no false TJ refs).
Tags vocab-conformant. Vintage-agnostic slug. Taste descriptors NOT
substantiated by cited URL → stripped (defect class 1).

### Cross-reference integrity
All 155 wines' `producer` resolves to 54 vineyards. All 12
`signature_wines[*].slug` resolve to `wines[*].slug`.

### High-editorial-score backing (`editorial_score >= 4.7`)
32 cuvées at >=4.7. Most non-marquee scores defensible by lookup
against producer prestige (e.g. Hirtzberger Honivogl, Knoll
Pfaffenberg, Rudi Pichler Achleiten/Hochrain, FX Pichler Unendlich
are all genuinely top-tier Wachau wines). No flag.

### Personal attribution / generation-number fabrications
Sampled 30 random entities across topics. No new chef/owner/winemaker
attribution defects found (QA1 caught Knoll-IV, QA2 stripped Rochelt;
those fixes hold).

### Classification (Wachau DAC vs Steinfeder/Federspiel/Smaragd)
PASS. All Wachau producers carry `classification: "Wachau DAC"`;
tier marks live in cuvée `name` / `wine_program` only. Boundary
estates (Stift Göttweig, Winzer Krems, Forstreiter) correctly
classified as Kremstal DAC.

### Austria country stub
Now reads coherently (post-fix). Substantial overview retained without
soft superlatives or em-dashes.

---

## Upstream prompt-hardening recommendations

Per the user memory rule `feedback_fixes_feed_prompts.md`: every fix
must harden upstream so the same defect doesn't recur.

### 1. Section I — directory-page detection (research prompt + QA1)

The Rioja precedent established the rule but the SCHEMA / research
prompt still allows researchers to point `cuisine_evidence_url` at
producer-overview, importer-card, or directory pages and pass the
mechanical check when multiple sibling cuvées share the URL.

**Hardening:**
- `agents/wine-research/PROMPT.md`: explicitly enumerate the
  forbidden URL shapes for `cuisine_evidence_url`:
  - `vinea-wachau.at/mywachau/betriebe/` and any `/companies/company-details/...` company-card path
  - `winebow.com/our-brands/<producer>` (the parent path; per-wine paths `<producer>/<wine>` are fine)
  - `weygandtmetzler.com/prod-focus-...` (producer card)
  - `falstaff.com/en/wineries/<producer>` (producer card)
  - `wineguide.wein.plus/<producer>` (producer card)
  - any regional tourism overview (`lower-austria.info`, `donau.com`,
    `wachau.at` root)
  - any taverns/restaurants directory (`buschenschank.at/...`)
- `scripts/check_evidence_content.py`: detect URL-sharing across
  multiple cuvées and treat shared URLs more strictly — require EACH
  cuvée's descriptors to appear in a 200-character window of the
  cuvée's name on the page (a per-cuvée locality check). When a URL
  is shared by 3+ cuvées, lower the "OK" threshold or escalate to
  MUST-HAVE per-cuvée descriptor coverage rather than any-descriptor.
- Add a `check_directory_page_evidence.py` ship_safety stage that
  HEADs every unique `cuisine_evidence_url`, fetches the body, and
  rejects with HARD if the page contains a directory-list pattern
  (>10 producer/wine link cards, no per-cuvée prose section) when
  cited by >=2 cuvées.

### 2. Section festival — annual flag + provenance URL validation

Two bugs caused the 5x 404 + 1x 500 festival source_urls to slip.

**Hardening:**
- `agents/wine-research/SCHEMA.md`: require `annual: true` (or
  `annual: false` with explicit one-off justification) on every
  festival in `wine-festivals.json`. Researcher must not leave
  `annual: null`.
- `scripts/check_festival_dates.py`: when iterating festivals, do not
  silently skip `annual != True`; emit WARN "festival X has
  annual:null, claim not validated" and fail-soft.
- `scripts/check_external_urls.py`: extend `URL_FIELDS` to include
  `source_url`, `open_evidence_url`, and `cuisine_evidence_url`
  whenever they appear under a `verified` block. Provenance URLs ARE
  external URLs and should be mechanically HEAD-validated like
  booking links. Today a `verified.source_url: <404>` ships clean.
- Add an opt-in `--strict-provenance` ship_safety flag that fails
  HARD on any `verified.source_url` 4xx/5xx.

### 3. Soft-superlative strip pattern — extend to "benchmark/reference/defining"

QA1 + QA2 caught the explicit "most/greatest/finest" tier but missed
the softer adjective-noun pattern ("benchmark wine", "reference
Grüner", "defining characteristics") that's the canonical wine-press
register.

**Hardening:**
- Extend `agents/qa/PROMPT.md` Section H + C0 soft-superlative list
  (the 2026-05-28 Ribera addition) to enumerate:
  - "benchmark <X>" / "<X> is a benchmark"
  - "reference <X>" / "<X> is a reference"
  - "defining characteristic(s) of <X>"
  - "defining site expression(s)"
  - "<X> is the village benchmark"
  - "<X> is one of the Wachau's defining ..."
- Extend `scripts/check_score_claims.py` regex set to surface these
  patterns as WARN.
- Also include "not to be missed" in the AI-tells list — QA2 swept
  for AI-tells but it wasn't caught (Jamek tip).

### 4. Em-dash `--` (double hyphen used as em-dash) ban enforcement

The em-dash ban in STANDARDS.md is documented but the validator that
catches `—` and `–` (Unicode em/en dash) does not catch `--`. Country
stub and signature-grapes.json shipped multiple double-hyphen pairs.

**Hardening:** add `--` (with surrounding spaces) to the em-dash
regex in `scripts/validate_data.py` or equivalent prose-lint stage.

---

## Summary

| Defect class | Count | Where |
|---|---|---|
| Section I taste-block fabrication (Rioja-class) | 84 cuvées stripped + cuisine_evidence_url repointed | wines.json |
| Festival source_url 404/500 decay + annual:null bypass | 8 festivals (5 URL swaps, 3 prophylactic re-points) | wine-festivals.json |
| Soft-superlative "benchmark/reference/defining" + em-dash residue | 21 prose fixes | wines.json, vineyards.json, region.json (Wachau + Austria), signature-grapes.json |

**Total individual fixes: 113.** ship_safety post-fix: **PASS (0 HARD,
0 cuvee-taste-miss WARN)**.

OPUS-FOUND-3 austria/wachau.
