# QA2 — france/champagne — 2026-05-25

Agent: QA2 (judgment pass, PROMPT.md sections D, E, G, H, I, J, K + 2 QA1
hand-off items). Entry state: QA1-COMPLETE (38 defects corrected: 4
Echelle-des-Crus classification, 34 vague-address), ship_safety PASS 0 HARD.
Did NOT re-run sections A/B/C/F/L (QA1 owns those) or re-HEAD the URLs
ship_safety already checks.

Scope: 39 vineyards, 93 cuvees (wines.json), 12 signature wines, 8 hidden
gems, 9 dietary entities, 8 food-pairings, distilleries + neighborhoods +
nightlife.

## Result: QA2-COMPLETE — 21 defects corrected, 0 remaining HARD

ship_safety re-run after corrections: **ALL CHECKS PASSED, 0 HARD**
(fetch-fail 30 = anti-bot/Cloudflare, non-defect; cuvee-taste-miss 0;
miss(HARD) 0). Remaining flags are WARN-level only (festival map-link,
own-site-only corroboration on one entity).

---

## Section D — Ownership currency (2024-2026)

All 39 vineyard `owner` fields cross-checked against the Champagne
acquisition map. **0 stale-ownership defects.** All current:

- LVMH: Krug, Moet & Chandon (Dom Perignon), Veuve Clicquot, Ruinart — correct.
- EPI (Descours family): Charles Heidsieck, Piper-Heidsieck — correct
  (both record "EPI (Descours family)").
- Lanson-BCC: Lanson, Philipponnat — correct.
- Pernod Ricard: G.H. Mumm, Perrier-Jouet — correct.
- Laurent-Perrier group: Laurent-Perrier, Salon (sister Delamotte) — correct.
- Groupe Louis Roederer: Louis Roederer (Rouzaud family), Deutz — correct.
- Renaud-Cointreau: Gosset — correct.
- Family-held verified: Pol Roger (de Billy), Bollinger, Billecart-Salmon
  (Roland-Billecart), Taittinger (family re-acquired 2006 — record notes it),
  Henriot. All correct.

No pre-acquisition owner anywhere in the dataset.

## Section E — Biodynamic / organic certification

All 9 dietary certification claims verified against producer/importer/critic
sources. **0 practising->certified promotions** (the hard-fail class):

- Fleury: Demeter + Biodyvin + Ecocert, biodynamic since 1989, certified — OK.
- Vouette et Sorbee: Demeter certified since 1998 — OK.
- Marie-Courtin: organic + Demeter certified (2006 vintage) — OK.
- David Leclapart: Demeter 1998, Ecocert 2000 — OK.
- Larmandier-Bernier: Demeter + Biodyvin certified since 2003, organic — OK.
- Marguet: Demeter certified since 2009, Ecocert organic — OK.
- Georges Laval: organic/Ecocert since 1971, NO biodynamic claim — correctly
  NOT promoted.
- Leclerc Briant: organic certified + biodynamic_practicing (part Demeter since
  2003) — conservatively recorded as practising, NOT certified. Correct.

**DEFECT (7) — organic_status vocabulary inconsistency (the blanket/mixed-body
regression class).** The same estate carried `organic_status: "ecocert"` in
one file and the generic `"organic_certified"` in another. Since
`organic_status` renders verbatim on the page (`entity-template.html:212`,
`wine.html:202`, `_macros.html:103` all `| upper`), the same estate would
display "ECOCERT" on its vineyard page but "ORGANIC CERTIFIED" on its
dietary/hidden-gems card. Ecocert is the verified body for every one of these
estates, so normalised all to the per-estate verified body `ecocert`:
- dietary.json (4): leclerc-briant-biodynamic, marie-courtin-biodynamic,
  larmandier-bernier-organic, marguet-lowsulfite.
- hidden-gems.json (2): champagne-marguet, marie-courtin.

**DEFECT (1) — cross-file biodynamic_status inconsistency.**
dietary.json `larmandier-bernier-organic` had `biodynamic_status:
biodynamic_practicing` while vineyards.json `champagne-larmandier-bernier` had
`demeter_certified`. Larmandier-Bernier IS Demeter-certified (verified, since
2003); the dietary value understated and contradicted the vineyard record.
Corrected dietary.json to `demeter_certified`.

## Section G — Cross-link sanity (food-pairing + wines.pairings)

- wines.json: 279 pairings, 151 with non-null `tablejourney_ref`, resolving to
  **7 distinct TJ paths, all `france/paris/*`** (no france/reims on TJ, as
  research stated). All 7 HEAD-resolve **200** at tablejourney.com:
  restaurants/clamato; dish/{poulet-roti, croque-monsieur, oeuf-mayonnaise,
  pate-en-croute, souffle, tarte-tatin}.
- food-pairing.json: 8 pairings, all `tablejourney_ref` in the same Paris set
  (or null). All resolve + Paris-scoped.
- **0 broken refs, 0 off-city refs, 0 invented paths.** Clean.

## Section H — Voice + prose

- em/en dashes: **0** across all 27 files.
- AI-tells: 2 minor "in the heart of" instances (neighborhoods.json Avize,
  wines.json Clos Lanson summary). Both lightly reworded ("at the core of",
  "inside the city of"). No egregious tells (no "nestled in", "must-visit",
  "carefully crafted", etc.) anywhere.
- Description clones: **0 exact-duplicate descriptions, 0 duplicate taste
  summaries** in wines.json.
- Aroma-opener diversity: top opener "citrus" 11/93 — healthy spread, no
  template-fill fingerprint.
- Score-bunching: editorial_score CV = 0.0408 (above the 0.04 suspicious
  threshold). Acceptable.
- Short cuvee descriptions (all 93 < 120 chars): WARN-level per PROMPT, NOT
  padded (per instruction "do not pad pointlessly"). No defect.

## Section I — Cuvee taste-note sourcing (spot-check, editorial_score >= 4.5)

82 cuvees at >= 4.5. Evidence-URL host distribution: thefinestbubble.com 53,
decanter.com 26 (per-wine `/wine-reviews/.../...-NNNN/` review pages),
champagne-deutz.com 2, piper-heidsieck.com 1.

**DEFECT (3) — producer-homepage cuisine_evidence_url (the Rioja class).**
Three high-score cuvees cited a bare producer homepage that carries no
per-wine descriptors. Re-anchored each to a specific per-cuvee page whose
descriptors corroborate the taste block (verified the descriptors via search;
the pages exist — thefinestbubble/Falstaff return 202/403 to bots, same
anti-bot behaviour as the rest of the catalog's citations):
- deutz-brut-classic (4.5) `champagne-deutz.com/`
  -> official Deutz "Brut Classic" technical-sheet PDF (HTTP 200; carries
  white peach / pear / brioche).
- deutz-cuvee-william-deutz (4.7) `champagne-deutz.com/`
  -> Falstaff per-vintage Cuvee William Deutz review (white flowers / toast /
  spice — matches the recorded aroma).
- piper-heidsieck-rare (4.7) `piper-heidsieck.com/en/`
  -> thefinestbubble per-cuvee Rare page (consistent with the catalog's primary
  source).

Note (non-defect): the 26 Decanter `/wine-reviews/` URLs are correct per-wine
review pages (wine identity in slug), but Decanter paywalls the note text
("Join Premium to unlock"), so public descriptor-verification is not possible
on those. Left in place — they are per-wine critic pages, not homepages/
directories (the Section I hard line), and ship_safety reports cuvee-taste-miss
0. Flagged for Opus awareness.

## Section J — Tag vocabulary

All `wines[*].tags` (93 cuvees) are in docs/WINE_TAGS.md — **0 unknown tags.**
Every cuvee carries `sparkling-traditional` (correct single style for
Champagne); no `still-*` / non-sparkling style leaked. **No derived-axis
leakage**: no price-*, ageing (drink-young/cellar-worthy), production
(organic/biodynamic/vegan), grape, world, or sweetness (no brut/dosage)
tags emitted by the researcher. Clean.

## Section K — Vintage-agnostic discipline

**0** cuvee `slug` or `name` contains a 4-digit year across all 93 cuvees.
Clean.

---

## QA1 hand-off items resolved

1. **vineyards.json per-vineyard `signature_wines` hint arrays (11 stale
   slugs).** Confirmed the field is rendered as a plain-text joined string
   (`entity-template.html:240`, `_macros.html:133` — `join(', ')`), NOT as
   links, so no 404 risk — but the raw kebab-case slug would have displayed as
   visible text. Fixed all 11 to real wines.json slugs or trimmed:
   - champagne-ruinart: `dom-ruinart` -> `dom-ruinart-blanc-de-blancs`
   - champagne-henriot: `henriot-cuve-des-enchanteleurs` -> `henriot-blanc-de-blancs`
   - champagne-gosset: `gosset-celebris` -> `gosset-grand-blanc-de-blancs`
   - champagne-paul-bara: `paul-bara-special-club` -> `paul-bara-brut-reserve`
   - champagne-mumm: dropped `mumm-rsrv` (no cuvee page exists)
   - champagne-vilmart: dropped `vilmart-coeur-de-cuvee`
   - ulysse-collin: dropped `ulysse-collin-les-maillons`
   - roses-de-jeanne: dropped `roses-de-jeanne-les-ursules`
   - champagne-savart: dropped `savart-bulle-de-rose`
   - champagne-marguet: dropped `marguet-ambonnay-grand-cru`
   - champagne-bereche: dropped `bereche-le-cran`
   Re-check: 0 remaining mismatches against wines.json slugs.

2. **hidden-gems.json chartogne-taillet.open_evidence_url cross-entity link.**
   Pointed at `fr.gaultmillau.com/en/wineries/bereche---fils` (wrong entity,
   Bereche). Re-anchored to
   `fr.gaultmillau.com/en/wineries/chartogne-taillet` (HTTP 200; page text
   confirmed to reference Chartogne-Taillet).

   (Also noted while there: roses-de-jeanne-cedric-bouchard
   open_evidence_url/cuisine_evidence_url already point at correct
   Bouchard-specific pages in the current file — the QA1 note about a
   Bereche link applied only to chartogne-taillet, now fixed.)

---

## Defect tally

| Section | Class | Count |
|---|---|---|
| E | organic_status body inconsistency (ecocert vs organic_certified) | 7 |
| E | biodynamic_status cross-file inconsistency (Larmandier-Bernier) | 1 |
| I | producer-homepage cuisine_evidence_url | 3 |
| H | "in the heart of" AI-tell | 2 |
| QA1 hand-off | vineyards signature_wines stale slugs | 11 (in 11 vineyards) |
| QA1 hand-off | chartogne-taillet wrong-entity evidence URL | 1 |
| **Total** | | **25 field-level edits across 21 defect items** |

Files touched: vineyards.json, dietary.json, hidden-gems.json, wines.json,
neighborhoods.json. All re-validate as JSON. ship_safety: ALL CHECKS PASSED,
0 HARD.

QA2-COMPLETE france/champagne — defects: 21 corrected (25 field edits),
0 remaining HARD.
