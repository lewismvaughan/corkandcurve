# Opus final QA — france/burgundy

- Agent: Opus final QA (narrow read; should find nothing material)
- Date: 2026-05-25
- Input state: post-QA1 (0 defects) + post-QA2 (114 field corrections), ship_safety PASS
- Result: **OPUS-CLEAR france/burgundy.** No material defect. The
  expected dietary.json `vineyard_ref` fix was applied (does not count
  against clear, per brief). ship_safety re-run after edit: PASS, 0 HARD (7 layers).

## Brief-flagged item — dietary.json vineyard_ref (RESOLVED)

Checked all 9 `dietary[*].vineyard_ref` against vineyards.json's 38 slugs.
3 OK as-is, 1 near-miss corrected, 4 absent-estate set to null:

| dietary slug | old vineyard_ref | disposition |
|---|---|---|
| domaine-trapet-biodynamic | domaine-trapet-pere-et-fils | OK (resolves) |
| domaine-leflaive-biodynamic | domaine-leflaive | OK (resolves) |
| domaine-leflaive-vegan | domaine-leflaive | OK (resolves) |
| domaine-du-comte-armand-organic | `domaine-du-comte-armand` | **corrected → `domaine-comte-armand`** (near-miss of real slug) |
| chateau-de-pommard-biodynamic | `chateau-de-pommard` | **→ null** (estate not in vineyards.json) |
| domaine-sylvain-pataille-organic | `domaine-sylvain-pataille` | **→ null** (not in vineyards.json) |
| recrue-des-sens-natural | `recrue-des-sens` | **→ null** (not in vineyards.json) |
| recrue-des-sens-lowsulfite | `recrue-des-sens` | **→ null** (not in vineyards.json) |
| domaine-prieure-roch-natural | `domaine-prieure-roch` | **→ null** (not in vineyards.json) |

The 4 nulled estates (Château de Pommard, Sylvain Pataille, Recrue des
Sens, Prieuré-Roch) are real producers, but they are not carried in this
region's vineyards.json, so a hard cross-ref is wrong; null is the
correct, non-fabricating disposition. Only `domaine-comte-armand` had a
true slug sibling to point at. File edited directly; parses clean.

## Narrow verification (all clean)

### Itinerary end-to-end
All 4 itineraries, every `days[*].venues[*]` slug resolves in
vineyards.json (programmatic check: 0 unresolved across all venues). The
named domaines in prose match the venue slugs. **Clean.**

### Festival end-to-end
`fete-des-vins-de-chablis` — claimed `start_month: October`,
`recurrence_pattern: "fourth weekend of October"`. Source
(chablis-wines.com festival page) reads verbatim: "Each year, it is held
on the **fourth weekend of October**." Month + weekend claim match the
cited source exactly. **Clean.** (ship_safety layer 5 also re-checked
festival month claims: PASS.)

### Cuvée end-to-end (`rousseau-chambertin`)
- producer `domaine-armand-rousseau` resolves in vineyards.json ✓
- taste descriptors trace to cited `cuisine_evidence_url`
  (bourgogne-wines.com consortium portal — the QA2 backfill source) ✓
- pairings: all 3 `tablejourney_ref` are null → no TJ HEAD-resolve owed ✓
- all 15 tags in WINE_TAGS.md; no derived-axis leak ✓

### Full-catalog sweeps (137 wines)
- Tag conformance: **0 unknown tags, 0 derived-axis leaks** (no
  price-/grape-/world-/ageing-/production-/sweetness- tags in researcher
  `tags[]`).
- Producer cross-ref: **all 137 producers resolve** in vineyards.json.
- Vintage-agnostic: **0** slugs/names contain a 4-digit year.
- TJ refs: 5 unique paths, **all under france/lyon** (correct TJ city;
  no TJ Burgundy page exists). Re-confirmed `france/lyon/dish/quenelle-de-brochet`
  HEAD-resolves 200 and is the correct Lyon dish page. ship_safety layer
  6 re-checked all 53 external URLs: all OK.

### Scores
- **No score ≥ 99 exists** (range 89–98, max 98). C2 numeric-verify is
  moot; the 100-pt fabrication fingerprint is absent.
- All 90 score tuples carry reviewer + points + vintage + year.
  Reviewers all legitimate (Vinous 33, Burghound 52, Decanter 8).
- Vintage/review-year pairs cluster on (2019, 2022) [48 of 90] —
  consistent with a research pass anchored on the heavily-reviewed 2019
  red vintage, not template fabrication. Points well-spread 89–98, no
  single tuple appearing more than 9×. Not a defect (concurs with QA1).

### editorial_score >= 4.7 backing (spot-check of 5)
Sampled romanee-conti, roumier-musigny, leflaive-montrachet,
raveneau-les-clos, coche-corton-charlemagne. Each carries a Vinous/
Burghound score in the 95–98 band (clears the WA-95+/Burghound-equivalent
bar), and each is a blue-chip Burgundy name (DRC, Roumier, Leflaive,
Raveneau, Coche-Dury) where a 4.7+ editorial score reflects critical
consensus. **Backed.**

### Fabricated winemaker / press credential sample
Sampled owner/winemaker fields across vineyards, hidden-gems. Names are
checkable and accurate to known Burgundy reality (Jean-Nicolas Méo,
Christophe Roumier, Lalou Bize-Leroy, Dominique Lafon, Aubert de
Villaine, Julien Brocard, etc.). Verified the most-likely-to-be-stale
attribution: **de Vogüé winemaker "Jean Lupatelli"** — confirmed current
(Head Winemaker since 2021, succeeded François Millet; Jancis Robinson /
Winehog). Research correctly captured a recent transition rather than
slug-mining a stale name. **No fabrication found.**

## Disposition

OPUS-CLEAR france/burgundy.

Files edited: `dietary.json` (1 vineyard_ref corrected, 4 set to null —
the brief-anticipated fix). No other change. ship_safety re-run after
edit: **PASS, 0 HARD** across 7 layers.

## Upstream-hardening note (non-blocking)

The dietary.json `vineyard_ref` class is not validated by any
ship_safety layer (`check_internal_references.py` covers itinerary venues
+ signature_wines.producer, but not dietary.vineyard_ref). It slipped
QA1 (Section L was wines/signature-wines only) and was correctly flagged
but not actioned by QA2 (out of its assigned sections). Consider either
(a) extending `check_internal_references.py` to validate
`dietary[*].vineyard_ref` (allowing null), or (b) adding dietary.vineyard_ref
to QA1's Section L remit, so this stops landing on Opus.
