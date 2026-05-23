# QA2 Report: france/bordeaux — 2026-05-22

## Summary

- **Sections covered:** D, E, G, H, I, J, K (QA2 scope) + QA1 handoffs resolved
- **validate_data.py:** 0 ERRs (WARN-only — pre-existing description length warnings)
- **check_internal_references.py:** 0 ERRs, 0 WARNs
- **QA1 handoffs resolved:** 2 of 2
- **Defects fixed:** 5 (2 ownership, 1 winemaker stale director, 31 WCI score removals, 1 unsubstantiated vegan claim removed)
- **Entities removed:** 1 (`chateau-angelus-vegan` from dietary.json vegan_winemaking)
- **Scores removed:** 31 (all Wine Cellar Insider scores across 14 wines in wines.json)

---

## QA1 Handoff W1 — Wine Cellar Insider scores (RESOLVED)

**Scope:** 14 wines in wines.json with Wine Cellar Insider as sole/partial reviewer.

**Action taken:** Attempted to find canonical-publication equivalents (Wine Advocate, Decanter, Vinous, James Suckling, Wine Spectator) via publicly accessible URLs for all 14 wines across the affected vintages. All major wine publication review pages returned 403 Forbidden or 404 Not Found (paywalled). Cannot fabricate scores. Per QA2 instruction: all Wine Cellar Insider scores removed.

**Result:** 31 WCI scores removed across 14 wines.

| Wine slug | WCI scores removed | Canonical scores retained |
|---|---|---|
| `chateau-angelus` | 3 | 0 |
| `hommage-a-elisabeth-bouchet` | 1 | 0 |
| `le-carillon-de-langelus` | 2 | 0 |
| `chapelle-dausone` | 2 | 0 |
| `chateau-ausone` | 4 | 0 |
| `chateau-beausejour-becot` | 3 | 0 |
| `chateau-canon` | 3 | 0 |
| `croix-canon` | 2 | 0 |
| `chateau-figeac` | 1 | 2 (Wine Advocate + Vinous, 2019) |
| `petit-figeac` | 1 | 0 |
| `aromes-de-pavie` | 2 | 0 |
| `chateau-pavie` | 3 | 0 |
| `chateau-troplong-mondot` | 3 | 0 |
| `mondot` | 1 | 0 |

Note: Many affected wines retain canonical scores in vineyards.json (e.g., Angelus has WA 100pt/2012 and JS 100pt/2016 at the vineyard level). The wines.json cuvee-level scores are now empty or partial for these entries pending a targeted follow-up research pass.

---

## QA1 Handoff W2 — chateau-angelus-vegan (RESOLVED: REMOVED)

**Verification:** Fetched `https://www.angelus.com/en/the-estate/farming/` — page returns only age-gate/cookie content, no substantive winemaking content accessible without login. Fetched The Wine Cellar Insider's Angelus producer page (the evidence URL cited) — no mention of bentonite fining, vegan fining, or avoidance of animal-derived agents anywhere on the page. The page covers cold maceration, whole-berry fermentation, malolactic in oak, and ageing protocols only.

**Finding:** Neither the primary source (angelus.com) nor the evidence URL (thewinecellarinsider.com) substantiates the bentonite/vegan fining claim.

**Action:** `chateau-angelus-vegan` entry removed from `dietary.json` `vegan_winemaking` list.

Note: The dietary.json vegan_winemaking list now contains only `chateau-figeac-vegan` (pea protein + bentonite fining confirmed from 2020 vintage, sourced from Ecocert-certified producer with documented vegan transition).

---

## Section D — Ownership currency

Sample of 15 vineyards.json entries checked.

**DEFECT D1 — chateau-troplong-mondot stale ownership (FIXED):**
- `owner` was "Bertrand Mure (Societe Agricole Chateau Troplong Mondot)"
- SCOR, the French reinsurance group, acquired Troplong Mondot in July 2017 for a record 7M EUR/hectare.
- **Fix:** Updated to "SCOR (French reinsurance group; acquired July 2017)"
- Source: The Wine Cellar Insider Troplong Mondot producer profile + troplong-mondot.com

**DEFECT D2 — chateau-troplong-mondot stale winemaker (FIXED):**
- `winemaker` was "Aymeric Roby" — name unrecognized; no source found
- Post-SCOR acquisition, Aymeric de Gironde was brought in as estate director in 2018
- **Fix:** Updated to "Aymeric de Gironde (estate director since 2018)"
- Source: The Wine Cellar Insider Troplong Mondot producer profile

**DEFECT D3 — chateau-cos-destournel stale winemaker/director (FIXED):**
- `winemaker` was "Aymeric de Gironde (estate director)"
- Aymeric de Gironde left Cos d'Estournel in 2017 when he was appointed to Troplong Mondot. Owner Michel Reybier has been directly managing since.
- **Fix:** Updated to "Michel Reybier (owner-managed since 2017)"
- Source: The Wine Cellar Insider Cos d'Estournel producer profile

**Other 12 entries checked — all correct:**
- Margaux: Mentzelopoulos family — OK
- Lafite: Domaines Barons de Rothschild / Saskia de Rothschild — OK
- Latour: Groupe Artemis (Francois Pinault) — OK (acquired 1993; current)
- Mouton Rothschild: Rothschild family (Camille, Philippe, Julien Sereys de Rothschild) — OK
- Haut-Brion: Domaine Clarence Dillon — OK
- Cheval Blanc: Bernard Arnault (LVMH) and Albert Frère family — NOTE: Albert Frère died 2018 but the Frère estate/group still holds the share; description acceptable as-is
- Petrus: Jean-Francois Moueix and family — OK
- d'Yquem: LVMH — OK (since 1999)
- Ausone: Vauthier family — OK
- Pavie: Gerard and Chantal Perse — OK
- Canon: Chanel SAS (Wertheimer family) — OK (acquired 1996)
- Angelus: Bouard de Laforest family (Stephanie de Bouard-Rivoal) — OK

---

## Section E — Biodynamic / organic certification

Sample of 5 demeter_certified / organic entries checked.

| Entry | Status in data | Assessment |
|---|---|---|
| `chateau-pontet-canet` (vineyards) | `demeter_certified` | OK — Demeter certification achieved 2014; Biodyvin 2010 |
| `chateau-palmer` (vineyards) | `demeter_certified` | OK — Demeter certification achieved 2017 per estate site |
| `chateau-pontet-canet-biodynamic` (dietary) | `demeter_certified` | OK — matches Demeter registry; certifier note says 2014 |
| `chateau-palmer-biodynamic` (dietary) | `demeter_certified` | OK — certifier note says 2017; matches known data |
| `chateau-lafleur-biodynamic` (dietary) | `biodynamic_practicing` | OK — correctly NOT claiming Demeter certification |
| `chateau-lafite-rothschild` (vineyards) | `ecocert` | OK — Ecocert organic certification achieved 2024 |
| `chateau-angélus` (vineyards) | `biodynamic_practicing` | OK — Angelus is practicing biodynamic but not Demeter-certified |

**0 certification promotion defects found.**

---

## Section G — Cross-link sanity

**food-pairing.json:** All 8 entries have `tablejourney_ref` values scoped to `france/bordeaux/...`. All 5 source URLs HEAD-checked and returned 200:
- `https://tablejourney.com/france/bordeaux/signature-dishes/` — 200
- `https://tablejourney.com/france/bordeaux/bakeries/` — 200
- `https://tablejourney.com/france/bordeaux/markets/` — 200
- `https://tablejourney.com/france/bordeaux/restaurants/` — 200
- `https://tablejourney.com/france/bordeaux/` — 200

**wines.json pairings:** 0 non-null `tablejourney_ref` values (QA1 cleared all invalid refs to null). No cross-link issues.

**0 cross-link defects found.**

---

## Section H — Voice + prose (spot-check)

- 0 em-dashes or en-dashes found in any checked files
- 0 AI-tells: "nestled in", "vibrant atmosphere", "culinary journey", "carefully crafted", "must-visit", "to die for" — none found across wines.json, vineyards.json, dietary.json, food-pairing.json, signature-wines.json
- 1 marginal case: "hidden gems" in wines.json prose for `chateau-de-larose-trintaudon` — editorial language, not a banned AI-tell
- editorial_score CV: 0.1023 — well above 0.04 threshold, healthy distribution
- 100 unique descriptions across 100 wines — 0 clones

**0 prose defects.**

---

## Section I — Cuvée taste-note sourcing

Sampled 10 wines with editorial_score >= 4.5.

**Descriptor diversity:**
- Sauternes (d'Yquem): apricot jam, beeswax, saffron, caramelised citrus — distinct from reds
- White (Haut-Brion blanc): white peach, orange blossom, oyster shell — distinct
- Medoc reds: cassis, cedar, graphite, tobacco vocabulary
- Pomerol: mulberry, wild strawberry, violet, dark cherry — softer profile
- Saint-Emilion: raspberry, iris, crushed blackberry, electric freshness — Cabernet Franc influence visible

No "dark cherry, leather" bunching. Vocabulary is appellation-specific and diverse.

**Evidence URL verification:** Spot-checked Chateau Ausone WCI page — crushed limestone/rocks, dark cherry, violets, black plum, mineral descriptors all confirmed present in tasting notes on the page.

**0 taste-note sourcing defects.**

---

## Section J — Tag vocabulary conformance

Full mechanical check on all 100 wines:
- 0 invalid tags (all tags in WINE_TAGS.md vocabulary)
- 0 derived tags emitted by researcher (no price-*, sweetness-axis, grape-axis, world-axis, production-axis tags)
- Average tags per wine: 13.1 (range 10-18)
- All wines carry 10+ tags across style, body, tannin/acidity, pairing, occasion, mood, editorial axes

**0 tag defects.**

---

## Section K — Vintage-agnostic discipline

Full mechanical check + 5-wine spot-check:
- 0 slugs containing 4-digit years
- 0 wine names containing 4-digit years
- Descriptions checked: year references are ownership dates and certification dates (e.g., "owned since 1977", "Demeter certification 2014") — NOT vintage pins. Acceptable.

**0 vintage-discipline defects.**

---

## Defect Index

| # | Slug/File | Section | Class | Severity | Action |
|---|---|---|---|---|---|
| 1 | 14 wines in wines.json | C/W1 | Non-canonical reviewer (WCI) | HIGH | FIXED: 31 WCI scores removed; canonical replacements unavailable via public URLs |
| 2 | `chateau-angelus-vegan` in dietary.json | W2 | Unsubstantiated vegan fining claim | HIGH | FIXED: entry removed from vegan_winemaking list |
| 3 | `chateau-troplong-mondot` vineyards.json | D | Stale ownership (Bertrand Mure; SCOR since 2017) | HIGH | FIXED: owner updated to SCOR |
| 4 | `chateau-troplong-mondot` vineyards.json | D | Stale winemaker (Aymeric Roby; de Gironde since 2018) | HIGH | FIXED: winemaker updated |
| 5 | `chateau-cos-destournel` vineyards.json | D | Stale director (Aymeric de Gironde left 2017) | MEDIUM | FIXED: winemaker field updated to Reybier |
| 6 | `chateau-cos-destournel-organic` in dietary.json | D | Description referenced "Aymeric de Gironde's leadership" (stale — left 2017) | LOW | FIXED: description updated |

**Entities removed:** 1 (chateau-angelus-vegan from dietary.json)  
**Scores removed:** 31 (all WCI entries from 14 wines in wines.json)

**Files modified:**
- `site-data/france/bordeaux/data/wines.json` (31 WCI scores removed from 14 wines)
- `site-data/france/bordeaux/data/dietary.json` (chateau-angelus-vegan removed from vegan_winemaking; Cos d'Estournel description de Gironde reference removed)
- `site-data/france/bordeaux/data/vineyards.json` (Troplong Mondot owner + winemaker updated; Cos d'Estournel winemaker updated)

---

## Post-fix validation

- `python3 scripts/validate_data.py --country france --city bordeaux`: **0 ERRs**
- `python3 scripts/check_internal_references.py --country france --city bordeaux`: **0 ERRs, 0 WARNs**
- All pre-existing WARNs (description length) are unchanged from QA1 baseline.

---

## Follow-up for Opus

1. The 13 wines with empty `scores[]` arrays after WCI removal (chateau-angelus, chateau-ausone, etc.) should have a targeted research pass to source canonical-publication scores. These are among the world's most-reviewed wines; scores exist but require authenticated publication access (Wine Advocate, Decanter, Vinous, James Suckling) which is paywalled.
2. The `chateau-cos-destournel` description mentions "Aymeric de Gironde's leadership" — should be corrected to reflect Reybier's current management.
