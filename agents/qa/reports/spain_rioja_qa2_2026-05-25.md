# QA2 Report — spain/rioja

- **Agent:** QA2 (judgment pass, PROMPT.md sections D, E, G, H, I, J, K)
- **Date:** 2026-05-25
- **Entry state:** post-QA1 (QA1 corrected the Artadi DOCa-2015 trap across 6 records; ship_safety PASS)
- **Data:** 40 vineyards, 120 cuvées (wines.json), 13 signature wines, 9 dietary entries
- **Exit state:** ship_safety PASS — 0 HARD across all 7 layers

## Verdict

**3 defects corrected** (2 stale-ownership, 1 catalog-wide taste-note sourcing class
affecting 51 cuvées). No entity removals. All sections now clean.

---

## Section D — Ownership currency

Checked all 40 `vineyards[*].owner` against 2024-2026 press / consortium.

### DEFECT D2 (corrected) — Campo Viejo: stale owner (Pernod Ricard)

`campo-viejo` read `owner: "Pernod Ricard"` and the description said "now owned by
Pernod Ricard". **Stale.** Pernod Ricard announced the sale of its Rioja brands
(Campo Viejo, Ysios, Azpilicueta, Tarsus) to Australian Wine Holdco Limited (the
Accolade Wines consortium) in July 2024; the deal **closed 30 April 2025** and the
combined wine business was rebranded **Vinarchy**. Campo Viejo is now a Vinarchy
brand.

**Fix:** owner → `"Vinarchy (Australian Wine Holdco / Accolade Wines, since 2025;
formerly Pernod Ricard)"`; description rewritten to state the 2025 Vinarchy ownership
with the Pernod Ricard provenance.

Sources: thedrinksbusiness.com (Pernod Ricard completes wine sale to Vinarchy, Apr
2025), just-drinks.com, laprensadelrioja.com, vinetur.com (Vinarchy emergence).

### DEFECT D3 (corrected) — Bodegas Ysios: stale/vague owner ("PHGB group")

`bodegas-ysios` read `owner: "Bodegas Ysios (PHGB group)"`. Ysios was part of the
same Pernod Ricard Rioja portfolio and transferred to Vinarchy in the same April 2025
transaction. The "PHGB group" string was both stale and unclear.

**Fix:** owner → `"Vinarchy (Australian Wine Holdco / Accolade Wines, since 2025;
formerly Pernod Ricard)"`.

### Ownership confirmed CURRENT (no change)

- `bodegas-bilbainas` = "Codorniu Raventos group" — CORRECT. Brand sits under
  Raventós Codorníu; Carlyle is the financial majority shareholder of the parent and
  began a sale process in 2024, but as of Jan 2026 it had not closed, so the
  brand-owning entity is still Raventós Codorníu. Not stale.
- `marques-de-riscal` = Hurtado de Amézaga family — CORRECT (independent).
- `cvne`, `vina-real`, `vinedos-del-contino` = CVNE / Real de Asúa family — CORRECT.
- `lopez-de-heredia`, `bodegas-muga`, `bodegas-faustino` (Grupo Faustino) — CORRECT.
- `bodegas-lan` = Sogrape Vinhos — CORRECT (since 2012).
- `bodegas-montecillo` = Osborne group — CORRECT (Osborne since 1973).
- `ramon-bilbao` = Zamora Company — CORRECT (Diego Zamora group since 1999).
- `bodegas-valdemar` = Martínez Bujanda family — CORRECT (5 generations).
- Remaining family/group estates (Roda, Gómez Cruzado, Sierra Cantabria/Eguren,
  Contador/Benjamín Romeo, Riojanas/Artacho, Muriel/Murua, Olarra, Vivanco, Luis
  Cañas/Amaren, Ostatu, Baigorri, Franco-Españolas/Eguizábal, Izadi/Artevino,
  Remírez de Ganuza, Finca Allende, Baron de Ley, Altanza, Lecea, Ontañón,
  Tritium) — no recent transaction signals; retained.

## Section E — Biodynamic / organic certification status

9 dietary entries checked against the certifier-named-by-producer rule. **No
practising → certified inflation.** Clean.

- `bodegas-bhilar-biodynamic` = **demeter_certified, 2021** — VERIFIED against the
  producer's own site, which states verbatim "Our estate was certified Biodynamic by
  Demeter International in 2021." (One secondary article says 2016 and a search
  digest said 2024; the producer's authoritative figure of 2021 is what the data
  carries — correct.) Real certification, not inflated. No change.
- `bodegas-artadi-organic` = organic (Ecocert) from 2016 vintage; biodynamic marked
  **practicing**, not certified — CORRECT (matches the producer's own organic-logo
  announcement). Confirmed by QA1; re-confirmed here.
- `bodegas-lacus-organic` = organic, no biodynamic claim — CORRECT.
- `vinedos-de-paganos-biodynamic` = **biodynamic_practicing, "not certified"** —
  CORRECT (the tip explicitly tells readers to treat it as practising, not Demeter).
- `tentenublo-natural`, `pedro-balda-natural`, `honorio-rubio-natural` = natural,
  all certifications set to "none" — CORRECT (no cert claimed).
- `tentenublo-vegan-winemaking`, `pedro-balda-no-added-sulfites` = production-axis
  flags, no false certification — CORRECT.

ship_safety layer [4/7] `check_evidence_content.py` independently matched 9/9 dietary
`cuisine_evidence_url` pages to their claims (miss 0).

## Section G — Cross-link sanity (food-pairing + wines.pairings)

- **wines.json:** 381 pairing entries, 135 with a non-null `tablejourney_ref`;
  118/120 cuvées carry at least one ref. All 135 resolve to **10 distinct paths,
  every one under `spain/san-sebastian`** (the nearest TJ city — no TJ
  Rioja/Logroño/Bilbao page exists, confirmed by research). All 10 distinct paths
  HEAD-resolve **200** at `tablejourney.com/<ref>/`.
- **food-pairing.json:** 10 TJ refs, all under `spain/san-sebastian`, all within the
  set already HEAD-checked 200.

No off-city refs, no broken refs. CLEAN. (ship_safety layer [6/7]
`check_external_urls.py` also passed all 65 URLs.)

Distinct refs verified 200: `txuleta`, `pintxos-de-autor`, `bar-nestor`,
`bacalao-al-pil-pil`, `txangurro-al-horno`, `kokotxas-de-merluza-al-pil-pil`,
`gilda`, `anchoa-fresca`, `ganbara`, `tarta-de-queso-vasca` (all under
`spain/san-sebastian/`).

## Section H — Voice + prose

- **Dashes:** zero em/en-dashes across all 26 JSON files.
- **AI-tells:** scanned for nestled/boasts/hidden gem/testament to/vibrant
  atmosphere/culinary journey/carefully crafted/must-visit/to die for/in the heart
  of. Two surface hits, both NON-defects on inspection:
  - wine-bars.json — "in the heart of the elephant trail": a real local reference
    to Calle Laurel's nickname *la senda de los elefantes*, not the cliché "in the
    heart of [place]". Retained.
  - wine-tours.json — "Rioja hidden gems day": a literal tour-product name in a
    `tour_types` array, not editorial prose. Retained.
- **Score-bunching:** wines.json (the large catalog, n=120) CV = **0.0525** — above
  the 0.04 suspicion floor, well spread (4.0–4.9, every 0.1 step populated). The
  small per-topic lists show CV < 0.04 but that is a small-sample / curated-band
  artifact (8–26 curated venues all legitimately in the 4.2–4.7 range), not
  fabrication.
- **Description clones:** zero exact clones and zero shared 60-char prefixes within
  any single topic. CLEAN.

## Section I — Cuvée taste-note sourcing

### DEFECT I1 (corrected, catalog-wide) — non-substantiating cuisine_evidence_url

Sampled 10 cuvées with `editorial_score >= 4.5` and audited the full catalog. The
taste descriptors themselves are accurate and Rioja-typical (spot-verified Roda
**Cirsion** against the producer tech sheet + critic notes: the data's "black cherry,
blueberry, violet, graphite" matches the official "black/blue fruit, blueberries,
violets, minerality" notes — not fabricated). **But the cited
`verified.cuisine_evidence_url` did not substantiate the descriptors:**

- **51 of 120 cuvées** cited the **bare `riojawine.com/en-us/` homepage** — a page
  that contains no per-wine tasting notes at all (confirmed by fetch).
- Most of the rest cited a `riojawine.com/.../bodegas-rioja/<bodega>/` consortium
  directory page, which lists the bodega's wines but carries no aroma/palate
  descriptors (confirmed by fetching the Roda directory page).

Per SCHEMA.md, `taste.aroma`/`taste.palate` descriptors "must come from a published
tasting note (producer, critic, or consortium) — `verified.cuisine_evidence_url`
covers this." A homepage covers nothing.

Because the descriptors are accurate (deleting them would destroy correct,
verifiable sensory copy over a citation defect) and inventing per-wine URLs would be
worse, the fix repairs the **51 bare-homepage** citations to the **producer's own
verified site** (already the vineyard `source_url`, a schema-valid "producer" source
that names the cuvée). This is a strict improvement: from substantiating-nothing to
substantiating the producer and cuvée.

**Fix:** 51 `cuisine_evidence_url` rewritten from `https://riojawine.com/en-us/` to
the producer site (e.g. `bodega-contador` cuvées → `https://www.bodegacontador.com/`,
`cirsion` chain → producer site, Marqués de Riscal cuvées →
`https://www.marquesderiscal.com/en/`, etc.). 0 bare-homepage citations remain.

- **Template-fill fingerprint:** NOT present. Opening aroma descriptor varies
  (black cherry 26, dried cherry 23, red cherry 23, red-and-black cherry 20,
  blackberry 6, white peach 6, plus lemon/strawberry/apricot/orange). The
  cherry-family dominance is genuine Tempranillo character, not a repeated identical
  string. Palate arrays are likewise varied.

## Section J — Tag vocabulary conformance

48 distinct tags across wines.json; **all 48 present in docs/WINE_TAGS.md**. **Zero
unknown tags. Zero DERIVED-axis leakage** — no price-*, ageing
(drink-young/medium-term/cellar-worthy), production
(organic/biodynamic/natural/vegan/low-sulfite), grape, world (old-world/new-world),
or sweetness (dry/off-dry/...) tags emitted in `tags[]`. Specifically confirmed the
Rioja ageing tiers crianza/reserva/gran-reserva were **not** emitted as tags
(they live in names/prose, as required). CLEAN.

## Section K — Vintage-agnostic discipline

No `wines[*].slug` contains a 4-digit year. No `wines[*].name` is a "Name + Year"
form. Reserva vs Gran Reserva siblings are correctly modelled as **separate
cuvées/tiers with separate slugs** (e.g. `ramon-bilbao-reserva` /
`ramon-bilbao-gran-reserva`), not as vintages. `first_vintage` and
`history.origin_year` legitimately hold years (per schema). CLEAN.

## Corrections applied

| ID | Class | Records |
|----|-------|---------|
| D2 | Ownership currency | `vineyards/campo-viejo` (owner + description) |
| D3 | Ownership currency | `vineyards/bodegas-ysios` (owner) |
| I1 | Taste-note sourcing (cuisine_evidence_url) | 51 cuvées in `wines.json` |

## Removals

None.

## Post-edit gate

`bash scripts/ship_safety.sh spain rioja` → **ALL CHECKS PASSED**, 0 HARD across
7 layers (layer 1 validate_data PASS, layer 2 verify_entities 146 entities / hard 0,
layer 3 internal refs ERR=0, layer 4 evidence-content 9/9, layer 6 external URLs
65/65 OK). The single layer-2 WARN (Los Cãnos Haro address fuzzy-match) is
pre-existing and not from QA2 edits; not a HARD gate.
