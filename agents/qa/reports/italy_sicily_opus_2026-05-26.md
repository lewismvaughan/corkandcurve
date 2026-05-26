# Opus Final QA — italy/sicily — 2026-05-26

**Verdict: OPUS-FOUND-4** (4 defect classes; 29 individual fixes). All
removed/fixed directly. ship_safety.sh re-run: 0 HARD, all JSON valid.

QA1 (15 fixes) + QA2 (14 fixes) did real work, but a systematic
fabrication class survived both passes and was the single biggest find.

## Narrow-read checks that PASSED

- **Itinerary end-to-end** (`etna-contrade-three-day-trail` + all 5
  itineraries): every `days[*].venues[*]` slug resolves to a real
  vineyard entity (passopisciaro, benanti, frank-cornelissen,
  terre-nere, calabretta, gulfi, occhipinti, cos, florio, pellegrino,
  de-bartoli, donnafugata, donnafugata-pantelleria, tasca-dalmerita).
- **Festival end-to-end**: Sicilia en Primeur (April/May, Assovini
  Sicilia, Palermo) and Contrade dell'Etna (April, Etna DOC) — both
  recurrence/month claims accurate. All 8 festivals consistent.
- **Cuvée end-to-end** (de-bartoli-vecchio-samperi 5.0 + 5 others):
  producer resolves in vineyards.json, tags all in WINE_TAGS.md with
  zero derived-axis leakage, zero non-null wines.pairings TJ refs
  (nothing to break). Tag vocabulary clean across all 176 cuvées.
- **editorial_score >= 4.7 backing** (43 cuvées): dominated by genuine
  Sicily marquee (Benanti Pietramarina, Terre Nere contradas,
  Passopisciaro Franchetti, Pietradolce Barbagalli, Cornelissen Magma,
  COS, Occhipinti, Tasca Rosso del Conte, de Bartoli, Donnafugata Ben
  Rye/Mille e una Notte, Florio Vergine). Defensible. No obscure estate
  carrying an inflated score.
- **Owner/winemaker fabrication**: all 54 vineyards nulled (per agent);
  only 3 distillery owners exist, all correct (QA2). No fabricated
  named individuals anywhere.

## Defects FOUND and FIXED

### Class 1 (PRIMARY) — Fabricated critic-score & publication-ranking milestones — 26 removed
`wines.json` `history.milestones[*].event`. QA2 caught exactly 2 of
these (Cornelissen Magma "Robert Parker rates Magma" + Russo 'a Rina
"top 5 by multiple critics") but the class was **systematic**: a
templated second milestone on ~26 cuvées asserting invented numeric
scores or unverifiable rankings. No source backs any of them; the
wines.json `scores[]` arrays are all empty, so nothing in the dataset
corroborates a single point figure. Removed:

- Invented numeric scores: terre-nere-guardiola "WA awarded 95+ points";
  terre-nere-calderara-sottana "earning 93+ points"; graci-arcuria
  "Tim Atkin MW awarded 95 points"; terre-nere-feudo-di-mezzo "93+
  scores from multiple major critics" (also AI-tell "must-seek").
- "Top-N by critics" superlatives: de-bartoli-bukkuram "Italy's top 5
  sweet wines by multiple critics" (exact sibling of removed Russo
  claim); passopisciaro-franchetti / passopisciaro-rampante "top-10
  reds by WA/Decanter"; benanti-serra-della-contessa "Sicily's top 3
  reds"; russo-san-lorenzo "Sicily's top 10 (Tim Atkin)";
  pietradolce-barbagalli "Suckling rated among Italy's top wines" +
  "immediate critical acclaim from Wine Advocate"; benanti-pietramarina
  "Italy's top whites (Gambero Rosso)"; donnafugata-ben-rye "world's 50
  greatest dessert wines (Wine Spectator)".
- Unverifiable "featured in" publication claims:
  donnafugata-mille-e-una-notte / planeta-santa-cecilia "Wine Spectator
  Top 100"; benanti-rovittello + morgante-don-antonio "featured in Wine
  Spectator"; planeta-chardonnay "Wine Spectator recognition";
  passopisciaro-passobianco + calabretta-vigne-vecchie "Decanter
  comparison/overview"; florio-targa-riserva "wins major Decanter
  award"; cos-pithos-rosso "influential natural wine guides";
  occhipinti-sp68-rosso "Natural Wine by Isabelle Legeron";
  serragghia-passito "most extreme natural passito"; tasca-rosso-del-conte
  "first major international survey"; de-bartoli-vecchio-samperi
  "ultimate recognition by Gambero Rosso".

**KEPT** (verifiable): the 4 genuine Gambero Rosso **Tre Bicchieri**
awards (Ben Rye 1996, Hauner 1995, Pietradolce Archineri 2014-vintage,
Murgo Brut 2005) and all DOC/regulatory + first-vintage factual
milestones. Tre Bicchieri winners are documented and citeable; left
intact. pietradolce-barbagalli now has an empty milestones array
(history.summary retained) — valid.

### Class 2 — Dangling reference to a DROPPED entity — 1 fixed
`neighborhoods.json` `faro-messina.famous_producers` still listed
`pietramadre`, which QA2 dropped from vineyards.json. The Opus brief
explicitly flagged pietramadre but only named itinerary/dietary/
hidden-gems as places to check — it was hiding in neighborhoods.
Removed; `tenuta-gatti` (valid) retained.

### Class 3 — Cross-contaminated/fabricated producer slug — 1 fixed (5 occurrences)
`vineyards.json` carried Gabrio Bini's **Serragghia** estate (name +
description + source all correctly = Serragghia) under the slug
`donnafugata-pantelleria-vecchio-samperi-style` — a slug minted from
THREE unrelated producers (Donnafugata, De Bartoli's Vecchio Samperi,
and the real Serragghia). Internally consistent so it never tripped a
mechanical gate, but it would publish a wrong, SEO-damaging canonical
URL for a real cult producer. Renamed to `serragghia` across all 5
occurrences (vineyards, neighborhoods, signature-grapes, 2 wines).

### Class 4 — Broken producer cross-ref (slug typo) — 1 fixed
`budget-wines.json` `tasca-d-almerita-regaleali-bianco.producer` was
`tasca-d-almerita`; the vineyard slug is `tasca-dalmerita` (no hyphen
before d). Would fail at template render. Every other budget-wines
producer resolved correctly. Fixed.

## Upstream prompt-hardening recommendations

1. **(Highest priority) Add a QA gate + research-prompt rule for
   milestone press claims.** The Parker-class is not a one-off; it is
   the research agent's default way of padding `history.milestones`.
   Harden:
   - **Research prompt / SCHEMA.md**: a `history.milestones[*].event`
     that asserts a numeric score (`\b9\d\b.*point`, `9\d\+`), a critic
     name (Parker/Atkin/Suckling/Larner/etc.), a publication ranking
     ("top N", "world's greatest/50"), or "multiple critics" MUST carry
     a citeable source URL in the milestone, OR be omitted. Default to
     omission. Tre Bicchieri / DOC-regulatory / first-vintage facts are
     fine without a per-claim URL.
   - **QA1 Section C / D**: extend the score-fabrication scan from
     `scores[]` into `history.milestones[*].event` AND `description` /
     `history.summary` prose. QA1+QA2 both scoped only the `scores`
     array (all empty here) and missed 26 prose-embedded score claims.
     Add a regex gate to ship_safety so this fails mechanically.

2. **Add a dropped-entity orphan sweep across ALL ref fields.** When an
   entity is dropped, QA must grep the slug across every file including
   `neighborhoods.famous_producers`, not just the topics named in a
   brief. Add `famous_producers` to the ship_safety vineyard-ref check
   (it is not currently mechanically validated — neither pietramadre nor
   the Serragghia slug were caught by any gate).

3. **Slug-coherence check.** Flag any `vineyards[*].slug` whose tokens
   don't appear in its own `name` (the Serragghia case: slug shared zero
   tokens with "Serragghia"). Cheap mechanical signal for
   cross-contaminated slug minting.

4. **Producer-ref normalisation.** The `tasca-d-almerita` vs
   `tasca-dalmerita` typo and the QA1/QA2 slug fixes are all the same
   class: free-form producer slugs drift from the canonical
   vineyards.json slug. ship_safety already checks `wines.producer`;
   extend the same check to `budget-wines.producer`,
   `dietary.vineyard_refs`, and `neighborhoods.famous_producers`.

## Final state

```
bash scripts/ship_safety.sh italy sicily
Total HARD failures across 1 cities: 0
italy/sicily: ALL CHECKS PASSED
```
All 26 JSON files valid. All vineyard/producer cross-refs resolve (0
unresolved). 26 fabricated milestones removed + 3 ref/slug fixes.

**OPUS-FOUND-4 italy/sicily**
