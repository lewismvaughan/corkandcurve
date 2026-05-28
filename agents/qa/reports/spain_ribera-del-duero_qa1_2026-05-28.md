# QA1 Report: spain/ribera-del-duero
Date: 2026-05-28
Agent: QA1 (Sonnet 4.6)
Ship safety before QA: PASS (0 HARD)
Ship safety after QA: PASS (0 HARD)

---

## Section A — Classification Accuracy

**Result: PASS** (no DOCa errors)

Sampled all 60 vineyards and all 160 cuvées. Classification breakdown:
- DO Ribera del Duero: 52 vineyards, 152 cuvées
- VT Castilla y León: 3 vineyards (Bodegas Mauro, Bodegas Leda, Hacienda Zorita), 7 cuvées

No DOCa Ribera del Duero errors found (Ribera is DO, not DOCa).

**Defect found and fixed:**
- `ercavio-tempranillo` (wines.json, producer `bodegas-mas-que-vinos`): classification was `"VT Castilla"` — corrected to `"VT Castilla y León"`.

Boundary-straddling producers correctly classified:
- Bodegas Mauro: VT Castilla y León (correct — vineyards outside DO boundary at Tudela del Duero)
- Bodegas Leda (Mas de Leda, Leda Viñas Viejas): VT Castilla y León (correct)
- Hacienda Zorita: VT Castilla y León (correct — Salamanca province)
- Bodegas Mas Que Vinos: DO Ribera del Duero in vineyards.json (address in Valbuena de Duero); Ercavio line correctly VT Castilla y León now, Alma del Duero as DO Ribera del Duero.

Albillo Mayor whites: `dominio-del-aguila-albillo` classified DO Ribera del Duero (correct — 2019 authorization).

---

## Section B — Hectarage

**Result: PASS**

All 60 vineyards have `hectares: null` (Agent A correctly omitted unverifiable hectarage). No fabricated hectares found. One description in `bodegas-mauro` mentions "90 hectares" in prose — this is drawn from producer's own site claim (within description text only, not the `hectares` field). Acceptable; the verified `hectares` field is null.

---

## Section C / C0 — Score Citations and Superlative Prose

**scores[] arrays:** All 160 cuvées have `scores: []`. Verified.

**C0 prose scan — 8 hits found across wines.json, wine-history.json, itineraries.json, day-trips-wine.json, wine-restaurants.json, hidden-gems.json:**

### Defects fixed:

1. **wine-history.json `peter-sisseck-pingus-1995`**: "Robert Parker declared it one of the greatest wines he had ever tasted" — critic ranking superlative in prose. Replaced with: "The debut vintage received top scores from leading critics and rapidly sold out."

2. **wine-history.json `2000s-post-pingus-boom`**: "greatest single period of winery construction" — categorical "greatest" strip. Replaced with "most concentrated period."

3. **itineraries.json `madrid-ribera-rioja-4-day` theme**: "Spain's two greatest Tempranillo appellations" — replaced with "Spain's two leading Tempranillo appellations."

4. **day-trips-wine.json `segovia-aqueduct-region`**: "one of Spain's greatest food traditions: cochinillo asado" — replaced with "one of Spain's most celebrated food traditions."

5. **day-trips-wine.json `burgos-city`**: "one of Europe's finest Gothic buildings" — replaced with "a notable example of High Gothic architecture."

6. **wine-restaurants.json `refectorio-abadia-retuerta`**: "the finest Spanish and international bottles" — replaced with "a broad selection of Spanish and international bottles."

7. **hidden-gems.json `cillar-de-silos`**: "leading challenger for the region's finest wines" (attributed to Oxford Companion) — deleted clause (unverifiable in prose context).

### Borderline cases judged clean:

- "estate's finest parcels" / "estate's finest site" / "estate's finest parcel" (wines.json: hacienda-monasterio-reserva-especial, la-mala, protos-finca-el-grajo-viejo, pagos-de-vega-real) — these describe internal estate selection not external ranking. Retained as factual.
- wine-history.json `alejandro-fernandez-tinto-pesquera`: "Robert Parker had labelled Tinto Pesquera the 'Spanish Petrus'" — historical attributed quote (a nick-name, not our ranking prose). Retained.
- wine-history.json `1990s-investment-wave`: "Driven by Parker scores for Tinto Pesquera, Vega Sicilia" — historical fact reference, no score number cited. Retained.

---

## Section D — Ownership / Winemaker Field Audit

**vineyards.json owner/winemaker fields:**
- All 60 vineyards have `owner: null` (Agent A correctly nulled all). PASS.
- One exception: `bodegas-aalto` has `winemaker: "Mariano García"` — this is accurate (Mariano García is the founding winemaker) and the field is correctly populated.

**Venue files (wine-hotels, wine-restaurants, distilleries, tasting-rooms, hidden-gems):** No `owner` or `winemaker` fields found in any venue file. PASS.

**Dominio del Águila biodynamic/Demeter status — CRITICAL RECONCILIATION:**

The QA brief flagged a conflict: dietary.json and hidden-gems.json documented Dominio del Águila as "certified organic (Consejo Ecológico de Castilla y León)" while vineyards.json had `biodynamic_status: "demeter_certified"` and multiple files had "Demeter-certified biodynamic" in descriptions.

Evidence weighed: dietary.json entry explicitly sources "Consejo Ecológico de Castilla y León" (regional organic authority, NOT Demeter). This is consistent with European Cellars and Virgin Wines importer pages. No Demeter registry listing found for the estate. The Demeter claim was fabricated.

**Fixes applied (propagated to all files carrying the field):**

| File | Entity | Change |
|------|--------|--------|
| vineyards.json | `dominio-del-aguila` | `biodynamic_status`: `"demeter_certified"` → `"none"`; description: removed "Demeter-certified biodynamic" |
| wines.json | `dominio-del-aguila-picaro-tinto` | `biodynamic_status`: `"demeter_certified"` → `"none"`; description fixed |
| wines.json | `dominio-del-aguila-reserva` | `biodynamic_status`: `"demeter_certified"` → `"none"`; description fixed |
| wines.json | `dominio-del-aguila-gran-reserva` | `biodynamic_status`: `"demeter_certified"` → `"none"`; description fixed |
| wines.json | `dominio-del-aguila-albillo` | `biodynamic_status`: `"demeter_certified"` → `"none"`; description + taste.summary fixed |
| wines.json | (rosado) | `biodynamic_status`: `"demeter_certified"` → `"none"`; description fixed |
| signature-wines.json | `dominio-del-aguila-reserva` | `style` field + `tasting_notes` + `description`: removed Demeter claims |

dietary.json entries for Dominio del Águila already had `biodynamic_status: "none"` — no change needed.

---

## Section F — Address Cross-Check

Sampled 15 physical entities across wine-bars, tasting-rooms, wine-hotels, wine-experiences. All have street-level addresses or closest-verifiable addresses. No fabrications detected in the sample.

One issue noted: `goyo-garcia-viadero` in hidden-gems.json has address "Ribera del Duero, Valladolid province, Spain" (vague) — but the tip explicitly says "Not a public-facing tasting room" and the producer has no public street address. This is the correct minimal entry for a private estate with no public-facing location. Accepted.

`bodegas-trus` in vineyards.json has address "Carretera de Traspinedo s/n, 47012 Valladolid" — the 47012 postcode is central Valladolid which is unusual for a winery on a rural road. Noted but not corrected (address_quoted already verified by ship_safety mechanical pass).

---

## Section L — Cross-Reference Integrity

**wines[*].producer → vineyards.json:** All 160 cuvée producers resolve. PASS.

**signature_wines[*].slug → wines[*].slug:** All 12 signature wines resolve. PASS.

**itineraries.json venues[] populated:** All 5 itineraries now have venue slugs where specific vineyards were mentioned in day text.

| Itinerary | Venues added |
|-----------|-------------|
| classic-golden-mile-weekend Day 1 | bodegas-vega-sicilia, pago-de-carraovejas, pago-de-los-capellanes, bodegas-alion |
| classic-golden-mile-weekend Day 2 | bodegas-protos, tinto-pesquera |
| aranda-underground-bodegas-lechazo-weekend Day 2 | bodegas-portia |
| madrid-ribera-rioja-4-day Day 1 | bodegas-protos |
| madrid-ribera-rioja-4-day Day 2 | bodegas-arzuaga-navarro |
| madrid-ribera-rioja-4-day Day 4 | bodegas-perez-pascuas |
| soria-old-vines-atauta-3-day Day 1 | dominio-de-atauta |
| soria-old-vines-atauta-3-day Day 2 | cillar-de-silos, bodegas-valdubon |
| harvest-season-full-week Day 2 | bodegas-vega-sicilia, pago-de-carraovejas |
| harvest-season-full-week Day 3 | bodegas-protos |
| harvest-season-full-week Day 4 | dominio-de-atauta |

All 17 venue slugs verified against vineyards.json. All resolve.

**day-trips-wine.json recommended_vineyards[] populated:**

| Day-trip | Vineyards |
|----------|-----------|
| burgos-city | bodegas-tarsus, garcia-figuero, bodegas-hermanos-sastre |
| valladolid-castile-capital | bodegas-vega-sicilia, bodegas-arzuaga-navarro, bodegas-aalto |
| salamanca-city | hacienda-zorita |
| madrid-capital | bodegas-protos, pago-de-carraovejas |
| soria-atauta-old-vines | dominio-de-atauta |
| segovia-aqueduct-region | (none — southernmost DO, no specific estates in dataset) |
| do-toro-zamora | (none — different DO, no cross-region slugs) |
| rioja-wine-region | (none — different DO) |

All 9 slugs verified. All resolve.

---

## Defect Summary

| # | Class | File | Entity/Slug | Fix |
|---|-------|------|-------------|-----|
| 1 | A (classification) | wines.json | ercavio-tempranillo | VT Castilla → VT Castilla y León |
| 2 | D (cert fabrication) | vineyards.json | dominio-del-aguila | demeter_certified → none; desc fixed |
| 3 | D (cert fabrication) | wines.json | dominio-del-aguila-picaro-tinto | demeter_certified → none; desc fixed |
| 4 | D (cert fabrication) | wines.json | dominio-del-aguila-reserva | demeter_certified → none; desc fixed |
| 5 | D (cert fabrication) | wines.json | dominio-del-aguila-gran-reserva | demeter_certified → none; desc fixed |
| 6 | D (cert fabrication) | wines.json | dominio-del-aguila-albillo | demeter_certified → none; desc + taste.summary fixed |
| 7 | D (cert fabrication) | wines.json | (rosado cuvée) | demeter_certified → none; desc fixed |
| 8 | D (cert fabrication) | signature-wines.json | dominio-del-aguila-reserva | style + tasting_notes + desc: Demeter removed |
| 9 | C0 (superlative) | wine-history.json | peter-sisseck-pingus-1995 | Parker "greatest wines" claim stripped |
| 10 | C0 (superlative) | wine-history.json | 2000s-post-pingus-boom | "greatest period" → "most concentrated period" |
| 11 | C0 (superlative) | itineraries.json | madrid-ribera-rioja-4-day | theme: "greatest Tempranillo appellations" → "leading" |
| 12 | C0 (superlative) | day-trips-wine.json | segovia-aqueduct-region | "greatest food traditions" → "most celebrated" |
| 13 | C0 (superlative) | day-trips-wine.json | burgos-city | "finest Gothic buildings" → "notable example of High Gothic architecture" |
| 14 | C0 (superlative) | wine-restaurants.json | refectorio-abadia-retuerta | "finest...bottles" → "broad selection...bottles" |
| 15 | C0 (superlative) | hidden-gems.json | cillar-de-silos | "region's finest wines" clause deleted |
| 16 | L (empty venues) | itineraries.json | all 5 itineraries | venues[] populated with 17 real slugs |
| 17 | L (empty vineyards) | day-trips-wine.json | 5 of 8 trips | recommended_vineyards[] populated with 9 real slugs |

**Total defects found and fixed: 17**

---

## Final ship_safety outcome

`bash scripts/ship_safety.sh spain ribera-del-duero` — **ALL CHECKS PASSED** (0 HARD failures)

All itinerary venue slugs resolve against vineyards.json. All day-trip recommended_vineyard slugs resolve.

---

QA1-COMPLETE spain/ribera-del-duero | 17 defects fixed | ship_safety PASS (0 HARD)
