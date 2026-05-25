# QA1 Report — spain/rioja

- **Agent:** QA1 (judgment pass, PROMPT.md sections A-F + L)
- **Date:** 2026-05-25
- **Entry state:** ship_safety PASS (0 HARD, 7 layers incl. strict verify_entities HEAD + address-match on vineyards)
- **Data:** 40 vineyards, 120 cuvées (wines.json), 13 signature wines

## Verdict

**1 defect corrected** (the flagged Artadi classification trap, applied across
6 records). All other sections clean. No entity removals required.

---

## Section A — Classification accuracy

Region appellation is **DOCa Rioja** (Denominación de Origen Calificada, one of
two in Spain). All 120 cuvées + 40 vineyards carry `classification: "DOCa Rioja"`.

### DEFECT D1 (corrected) — Artadi misclassified as DOCa Rioja

Artadi **left DOCa Rioja in 2015** and now labels as Vino de España. The prose
(vineyard description + every Artadi cuvée `history.milestones`) correctly records
the 2015 departure, but the `classification` field still read "DOCa Rioja", which
is factually wrong for the current/post-2015 vintages the records describe
(El Pisón scored 2018, Viñas de Gain 2019, etc. — all post-departure).

**Fix applied:** set `classification` to
`"Vino de Espana (formerly DOCa Rioja, left 2015)"` on:
- `vineyards.json` → `artadi`
- `wines.json` → `vina-el-pison`, `valdegines`, `la-poza-de-ballesteros`, `vinas-de-gain`

`signature-wines.json` → `vina-el-pison` already used `style: "still red
single-vineyard"` (no DOCa assertion) so needed no change.

### Ageing-tier conflation — CLEAN

Joven/Crianza/Reserva/Gran Reserva are correctly kept OUT of the appellation
`classification` field (which is uniformly DOCa Rioja). Ageing tiers appear only
in names/prose (e.g. "Castillo Ygay Gran Reserva Especial", "Viña Ardanza
Reserva"). The two axes are not conflated.

Sampled ~20 vineyards + all 13 signature wines + the 4 Artadi cuvées. Only the
Artadi case (the pre-flagged trap) surfaced. No broadening to 40 needed.

## Section B — Hectarage / area realism

**N/A — no defect possible.** No vineyard record carries a `hectares` field
(0 of 40). Nothing to source-check; no fabricated hectarage was shipped. The
large-house vs boutique-Alavesa size realism check is therefore moot.

## Section C — Score citations

- **132 score tuples**, all structurally complete (reviewer + points + vintage +
  year present on every entry; 0 missing).
- Reviewer mix legitimate for Rioja: Tim Atkin 118, Wine Advocate 6, Decanter 3,
  Vinous 3, Wine Spectator 2. No ambiguous "RP".
- **Points range 86–98. ZERO scores ≥99.** The research cap at 98 held — no
  fabricated 99-100 slipped into `scores[]`.
- **C2:** no tuples ≥99, so no numeric source-verify obligation triggered.
- Two 98pt tuples spot-verified against independent sources:
  - La Rioja Alta GR 890 2010 = Tim Atkin **98** — CONFIRMED. (Wine notably also
    drew a 100 from Sobremesa and 99 elsewhere; data correctly cites the 98 Atkin
    figure, not an inflated 100.)
  - Contador 2019 = Wine Advocate **98** — defensible; within Contador's
    established WA band (95-98, Luis Gutiérrez). Retained.
- **100-pt claims live in PROSE only, not as scores[] tuples** (per spec):
  - `vineyards.json/bodega-contador` description: "earned 100-point recognition"
    (prose).
  - `signature-wines.json/contador` tasting_notes: "the 2004 and 2005 earned 100
    points from Wine Advocate" (prose). Acceptable placement.
  - Artadi El Pisón: no fabricated 100; scores[] cite WA 97 / Atkin 97. Clean.

## Section F — Independent-directory address cross-check

Spot-checked across topics; representative results:
- **Baron de Ley** — independently confirmed at Ctra. Mendavia-Lodosa km 5.5,
  31587 Mendavia, Navarra; 16th-c. Benedictine monastery, est. 1985. Exact match.
  (Legitimately a DOCa Rioja bodega physically in Navarra — Rioja Oriental edge,
  not a defect.)
- Barrio de la Estación Haro cluster (La Rioja Alta, CVNE, López de Heredia, Muga,
  Roda, Gómez Cruzado, Bilbaínas) — addresses internally consistent and match the
  well-documented station-district cluster.
- Prose award claims verified: Castillo Ygay 2010 = WS Wine of the Year 2020;
  CVNE Imperial 2004 = WS Wine of the Year 2013 (first Spanish). Both correct;
  both stated as awards in prose without a fabricated points figure.

No fabrications found; sample stayed under the >2 broaden trigger.

## Section L — Cuvée → producer / signature → cuvée cross-reference

- All 120 `wines[*].producer` slugs resolve in `vineyards.json` (0 orphans).
- All 13 `signature_wines[*].slug` exist in `wines[*].slug` (0 orphans).
- All 13 `signature_wines[*].producer` resolve in `vineyards.json`.
- No invented-producer pattern detected.

## Incidental checks (no defects)

- **Tags (J):** 48 distinct tags used, all in WINE_TAGS.md; zero derived-axis
  leakage (no price-*, grape, sweetness, ageing, world, production tags in
  `tags[]`).
- **Vintage-agnostic (K):** no 4-digit year in any cuvée slug or name.
- **Certification (E):** only Artadi flags organic (`ecocert`) — correct, and NOT
  promoted to biodynamic. No "practicing → certified" inflation anywhere.

## Removals

None.

## Corrections applied

- D1: Artadi classification corrected on 6 records (1 vineyard + 4 cuvées; the
  signature wine already avoided the DOCa assertion).
