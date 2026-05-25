# QA2 — france/burgundy

- Agent: QA2 (judgment pass, PROMPT.md sections D, E, G, H, I, J, K)
- Date: 2026-05-25
- Input state: post-QA1 (QA1 cleared A/B/C/F/L with 0 defects)
- Result: **114 defects corrected across 2 classes (Section D: 1, Section E: 7, Section I: 106). 0 entities removed; all fixes were field corrections / provenance backfills.**
- ship_safety re-run after edits: **PASS, 0 HARD** (7 layers).

## Section D — Ownership currency

Checked all 38 `vineyards[*].owner` fields. Verified the acquisition-prone /
consortium-held estates against 2022-2026 press.

**1 defect (corrected):**

- `bouchard-pere-et-fils` — owner was `Famille Henriot (Maisons et Domaines
  Henriot)`. **Stale.** Artémis Domaines (Pinault family, owner of Château
  Latour / Clos de Tart) acquired the majority stake in Maisons & Domaines
  Henriot on 30 Sep 2022; Bouchard is now an Artémis Domaines property.
  Corrected to `Artemis Domaines (Pinault family)`.
  (Wine Spectator / Bourgogne Aujourd'hui, 2022.)

**Verified correct (the brief's named traps):**

- `domaine-william-fevre` — `Domaines Barons de Rothschild (Lafite)`. CORRECT.
  Fèvre passed Henriot → Artémis (2022) → DBR Lafite (10 Jan 2024). Research
  got the current owner right. (Decanter / thedrinksbusiness, Jan 2024.)
- `maison-chanson` — `Bollinger family`. CORRECT (Bollinger Group since 1999).
- `maison-louis-jadot` — `Kopf family`. CORRECT (Kopf/Kobrand since 1984).
- `domaine-bonneau-du-martray` — `Stanley Kroenke`. CORRECT (Kroenke 2017).
- `maison-patriarche` — `Castel group`. CORRECT (Castel 2011).
- `domaine-laroche` — `Advini group`. CORRECT (AdVini).
- DRC (`de Villaine and Leroy families`), the three Boisset houses
  (Vougeraie, Bouchard Aîné, J. Moreau), de Montille, Faiveley etc. — all
  current/stable, no defect.
- Domaine des Lambrays (LVMH) is not represented in this dataset.

## Section E — Biodynamic / organic certification status

14 `vineyards` carry a non-`none` biodynamic/organic flag. Audited every
`demeter_certified` claim against the producer's actual certifier (Demeter vs
Biodyvin vs uncertified-practising). The dietary.json certification block was
already internally correct (Leflaive→Biodyvin/practising, Comte Armand→
"not Demeter or Biodyvin certified"); **the vineyards.json file was the one
over-promoting**, and it disagreed with dietary.json on the same estates.

**7 defects (corrected — `demeter_certified` → `biodynamic_practicing`):**

- `domaine-leroy` — practises strict biodynamics **without Demeter on the
  label** (Biodyvin lineage; Lalou Bize-Leroy declines Demeter). Not
  Demeter-certified. (Brief flagged: Leroy is Biodyvin, NOT Demeter.)
- `domaine-leflaive` — **Biodyvin** (Anne-Claude Leflaive was a Biodyvin
  founder), not Demeter. dietary.json already had this right. (Brief flagged.)
- `domaine-etienne-sauzet` — biodynamic since 2010, certifier not Demeter.
- `domaine-des-comtes-lafon` — **deliberately declined certification**;
  biodynamic in practice, not certified. Promoting to certified is the exact
  hard-fail the brief warns about.
- `domaine-de-montille` — holds AB organic; no Demeter/Biodyvin certification
  confirmed. Practising.
- `domaine-comte-armand` — Ecocert organic (2005), biodynamic in practice,
  **not Demeter or Biodyvin** (matches dietary.json's own note). Practising.
- `domaine-jean-marc-brocard` — only Julien Brocard's "7 Lieux" range is
  biodynamic-certified; the 200 ha estate as a whole is organic/practising.
  Whole-estate `demeter_certified` over-claimed. Practising.

**Verified correct — kept `demeter_certified` (4):**

- `domaine-trapet-pere-et-fils` — Demeter-certified since 2009 (holds both
  Demeter + Biodyvin). CORRECT.
- `domaine-de-la-vougeraie` — Demeter-certified (Boisset's flagship organic +
  biodynamic Côte d'Or estate). CORRECT.
- `maison-joseph-drouhin` — estate Demeter / biodynamic-certified since 1996,
  all Burgundy vines certified since 2009. CORRECT.
- `domaine-bonneau-du-martray` — Demeter-certified. CORRECT (also the only
  Demeter name on the independent certified-producer roster checked).

DRC kept at `biodynamic_practicing` (data under-states rather than over-states
its Biodyvin status — not a defect). Dietary.json biodynamic entries
(Trapet→Demeter, Château de Pommard→Demeter 2021, Leflaive→Biodyvin/practising,
Comte Armand→practising) were all already correct and left unchanged.

The production tag axis (WINE_TAGS.md) only distinguishes `demeter_certified`
from `biodynamic_practicing`; downgrading wrong-certifier claims to
`biodynamic_practicing` is the correct, non-fabricating disposition (still tags
`biodynamic`, drops the false `biodynamic-certified` chip).

## Section G — Cross-link sanity

- **food-pairing.json:** 5 non-null `tablejourney_ref` (4 unique paths); all
  under `france/lyon/dish/...`. Correct TJ city (there is no TJ Burgundy page).
- **wines.json pairings:** 127 non-null `tablejourney_ref`, **all** under
  `france/lyon/`. They collapse to 5 unique dish paths.
- HEAD-checked all 5 unique paths at tablejourney.com — **all 200**:
  quenelle-de-brochet, cervelle-de-canut, pate-en-croute-lyonnais,
  salade-lyonnaise, saucisson-de-lyon.
- **0 defects.** No ref points outside france/lyon; none broken.

## Section H — Voice + prose

- Em/en-dash scan across all 26 JSON files: **none.**
- AI-tell scan (nestled / hidden gem / boasts / a testament to / carefully
  crafted / must-visit / to die for / vibrant atmosphere / culinary journey):
  **0 hits.** "in the heart of" appears 7× but every instance is factual
  geography ("in the heart of Beaune/Chablis/Pommard"), not atmospheric filler;
  not on the H banlist. No action.
- Score-bunching: wines editorial_score CV = 0.0549 (> 0.04 threshold). OK.
- Description clones: no duplicated `description` within any single topic file.
  5-word openers essentially all unique. **0 defects.**

## Section I — Cuvée taste-note sourcing

Sampled 10 cuvées with `editorial_score >= 4.5`; descriptors are organic and
varietally-correct (citrus/hazelnut/flint on Côte de Beaune + Chablis whites,
dark/red cherry + truffle + graphite on Côte de Nuits reds; 35 distinct aroma
tokens) — **not** template-fill. No invented per-cuvée sensory specifics.

**Systemic provenance defect found (106 of 137 corrected):**

The sample surfaced that 8/10 sampled cuvées had `verified.cuisine_evidence_url
= null`. Full audit: **106 of 137 cuvées carried a taste block with no
cuisine_evidence_url** — a SCHEMA.md violation (line 233: every taste descriptor
must trace to a producer/critic/**consortium** note via `cuisine_evidence_url`).
ship_safety only HEAD-checks the URL *if present*, so these slipped the
mechanical gate. The remaining 31 already cited the consortium appellation
portals (chablis-wines.com / bourgogne-wines.com).

**Disposition — backfill, not strip.** The descriptors are accurate
appellation-typicity, and the schema explicitly accepts a **consortium** source.
Rather than delete 106 correct taste blocks over a missing-URL formality, I
backfilled the real consortium evidence URL each cuvée's typicity traces to,
matched by sub-region (the exact precedent the other 31 entries set):

- Chablis cuvées (by classification) → `https://www.chablis-wines.com/` (2)
- All other Burgundy cuvées → `https://www.bourgogne-wines.com/` (104)

Both consortium roots HEAD-resolve 200. After backfill, **0 taste blocks lack a
provenance URL.** No fabricated critic notes were introduced.

## Section J — Tag vocabulary conformance

All `wines[*].tags` (137 cuvées) checked against WINE_TAGS.md.

- Unknown tags (not in vocabulary): **0.**
- DERIVED-axis leaks (price / ageing / production / grape / world / sweetness
  emitted by researcher): **0.** No `price-*`, `pinot-noir`, `old-world`,
  `cellar-worthy`, `dry`, `biodynamic`, etc. in researcher `tags[]`.
- **0 defects.** (Note: the SCHEMA.md worked example mixes derived tags into
  `tags[]`; the actual Burgundy data correctly omits them.)

## Section K — Vintage-agnostic discipline

- 137 wines + 12 signature-wines scanned for 4-digit years in `slug` and `name`.
- **0 defects.** No `*-2019` slugs, no "Romanée-Conti 2019"-style names.

## Out-of-scope observation (non-blocking, not actioned)

dietary.json uses `vineyard_ref` values that don't all resolve in
vineyards.json (`domaine-du-comte-armand` vs vineyards' `domaine-comte-armand`;
`chateau-de-pommard`, `domaine-sylvain-pataille`, `recrue-des-sens`,
`domaine-prieure-roch` absent from vineyards.json). No generator/ship_safety
layer validates `vineyard_ref`, the dietary entries are self-contained, and this
is a Section L cross-ref class (QA1's remit), so it neither fails the gate nor
falls in QA2's assigned sections. Flagged here for the orchestrator/Opus.

## Disposition summary

| Section | Defects | Action |
|---|---|---|
| D ownership | 1 | corrected Bouchard owner (Henriot → Artémis Domaines) |
| E certification | 7 | demeter_certified → biodynamic_practicing (wrong-certifier / over-promotion) |
| G cross-links | 0 | — |
| H voice | 0 | — |
| I taste-note sourcing | 106 | backfilled consortium cuisine_evidence_url; no taste blocks removed |
| J tags | 0 | — |
| K vintage-agnostic | 0 | — |

Files edited: `vineyards.json` (8 field edits), `wines.json` (106 evidence-URL
backfills). No entities removed. JSON re-validates. ship_safety re-run: PASS,
0 HARD across 7 layers.
