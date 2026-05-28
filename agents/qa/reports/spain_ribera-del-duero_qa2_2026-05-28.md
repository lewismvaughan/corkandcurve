# QA2 Report: spain/ribera-del-duero
Date: 2026-05-28
Agent: QA2 (Sonnet 4.6)
Ship safety before QA2: PASS (0 HARD) — per QA1 report
Ship safety after QA2: PASS (0 HARD)

---

## Sections checked: D, E, G, H, I, J, K

---

## Section J — Tag conformance

All 160 cuvées checked. No derived tags (price-*, cellar-worthy, drink-young, biodynamic, organic, natural, vegan, sweetness, grape, old-world, new-world) found in wines[*].tags arrays. All tags resolve in WINE_TAGS.md researcher-emitted axes.

**Result: PASS — 0 defects**

---

## Section K — Vintage-agnostic discipline

All 160 slugs checked. No 4-digit year found in any slug or cuvée name.

**Result: PASS — 0 defects**

---

## Section G — Cross-link sanity

**food-pairing.json:** 7 entries, all under `spain/madrid`. All 7 `tablejourney.com/spain/madrid/...` URLs HEAD-resolved 200. All in correct TJ city (Madrid). No broken or off-city refs.

**wines.json pairings:** All 160 cuvées have `tablejourney_ref: null` — no TJ cross-links to verify.

**Result: PASS — 0 defects**

---

## Section H — Voice + prose

**editorial_score distribution:** mean=4.464, stdev=0.268, CV=0.0600 (above 0.04 threshold — healthy spread, not score-bunching).

**AI-tells sweep:** 0 hits across all 26 topic files (wines.json, vineyards.json, hidden-gems.json, dietary.json, wine-restaurants.json, wine-bars.json, wine-hotels.json, tasting-rooms.json, distilleries.json, wine-experiences.json, wine-museums.json, wine-retailers.json, wine-schools.json, wine-tours.json, wine-festivals.json, wine-history.json, day-trips-wine.json, itineraries.json, budget-wines.json, seasonal-wine.json, neighborhoods.json, signature-wines.json).

**Em/en dash sweep:** 0 hits across all files.

**Description clones:** No duplicate descriptions within wines.json or within any other topic file.

**Result: PASS — 0 defects**

---

## Section I — Cuvee taste-note sourcing (MAJOR DEFECT — Rioja pattern)

**Finding:** 66 of 160 cuvées (41%) had `verified.cuisine_evidence_url` pointing to producer wine-directory listing pages (`/en/wines/`, `/vinos/`, `/our-wines/`) rather than specific per-wine pages. This is the same structural pattern caught in Rioja 2026-05-25 (116/120 cuvées cited homepages/directories).

**Sample verification (4 producers confirmed):**
- `emiliomoro.com/en/wines/` — returns HTTP 404
- `perezpascuas.com/en/wines/` — returns HTTP 404
- `aalto.es/en/wines/` — returns HTTP 404
- `pagodecarraovejas.com/en/wines/` — returns 200 but is a listing page with no per-wine tasting notes

**Descriptor cross-check (3 confirmed mismatches):**
- `perez-pascuas-gran-seleccion`: JSON aroma "concentrated dark cherry, blackberry, cedar, tobacco, mineral, violet, earth"; actual per-wine page says "aromas of berries and mature fruits, spices, balsamic notes, chocolate" — mismatch confirms template-fill
- `malleolus-de-valderramiro`: JSON descriptors not matching per-wine page "black fruits with liquorice profile, resinous and lactic tertiary notes"
- `el-anejon-de-carraovejas`: per-wine page describes "mountain and aromatic plants, mineralidad" — entirely different from JSON's "concentrated black fruit, cedar, tobacco, truffle, violet"

**Template-fill pattern confirmed:** "red cherry, plum" appeared as the first two aromatics in 19 of 160 wines; "dark cherry, blackberry" in 13; "dark cherry, plum" in 12. Structural template replication across producers.

**21 unique directory evidence URLs affected.** Status breakdown:
- HTTP 404: aalto.es/en/wines/, arzuaganavarro.com/en/wines/, carmelorodero.com/en/wines/, comenge.com/en/wines/, dominiodelaguila.com/en/wines/, emiliomoro.com/en/wines/, matarromera.es/en/wines/, perezpascuas.com/en/wines/, telmorodriguez.com/en/wines/
- DNS/connection failure: bodegashermanos.com/en/wines/, cillardessilos.es/en/wines/, dominioatauta.com/en/wines/, pagocapellanes.com/en/wines/, tintopesquera.com/en/wines/
- HTTP 200 (directory listing, no per-wine notes): haciendamonasterio.com/vinos/, bodegasfelixcallejo.com/en/wines/, bodegasmauro.com/en/wines/, bodegasmontebaco.com/en/vinos/, bodegasprotos.com/en/wines/, cepa21.com/en/wines/, pagodecarraovejas.com/en/wines/

**Fixes applied:**
1. Stripped all taste blocks (`aroma`, `palate`, `body`, `tannin`, `acidity`, `finish`, `summary`) for all 66 wines with directory evidence URLs
2. Nulled `cuisine_evidence_url` for all 66 (no tasting content to evidence)
3. Replaced dead `source_url` values (404/unreachable) with confirmed-200 substitutes:
   - Producer root URL where reachable (e.g., `emiliomoro.com/en/` → `www.emiliomoro.com/en/`)
   - DO Ribera del Duero consortium page (`riberadelduero.es/en`) for producers whose domains are fully unreachable
4. 94 of 160 wines retain their taste blocks (Vega Sicilia, Pingus, PSI, Aalto via per-wine pages etc. — those had `cuisine_evidence_url` pointing to specific per-wine pages confirmed 200)

**Result: 66 defects fixed**

---

## Section D — Ownership currency + fabrication/cross-contamination

**Sweep of venue files (wine-hotels, wine-restaurants, distilleries, tasting-rooms):**

**wine-restaurants.json — 2 fabricated chef names found:**

1. `ambivium`: cuisine and description attributed "Chef Cristobal Munoz" as the tasting menu creator. Actual head chef per Pago de Carraovejas estate page is **Marina de la Hoz**. Cross-contaminated chef name.
   - Fix: Removed "chef Cristobal Munoz" from cuisine field and description.

2. `refectorio-abadia-retuerta`: cuisine and description attributed "Chef Marc Segarra" as the tasting menu creator. Abadia Retuerta's own website and gastronomy page do not name the chef. Unverifiable individual name.
   - Fix: Removed "Chef Marc Segarra" from cuisine field and description.

**hidden-gems.json — 2 owner/founder cross-contamination defects:**

3. `dominio-de-es`: Description stated "Jorge Monzon, the founder of Dominio del Aguila, makes Dominio de Es as a separate project." Jorge Monzon is behind Dominio del Aguila; **Dominio de Es is made by Bertrand Sourdais** (confirmed by spanishwinelover.com). The two are separate producers in the Soria sub-zone. Classic cross-contamination between similarly-positioned estates.
   - Fix: Replaced the incorrect attribution with "Bertrand Sourdais, who also makes Antidoto, launched Dominio de Es..."
   - Also fixed `cuisine_evidence_url` which pointed to an Aguila/Monzon blog article (irrelevant source for Dominio de Es).

4. `bodegas-valduero-gumiel`: Description stated "Founded in 1984 by the Frutos Martinez family." Actual founder per bodegasvalduero.com is **Gregorio Garcia Alvarez** (confirmed: "Bodegas Nabal es el resultado de la pasión de la familia Garcia Alvarez").
   - Fix: Replaced "Frutos Martinez family" with "Gregorio Garcia Alvarez."

**Residual QA1 incompleteness — Dominio del Aguila biodynamic prose in wines.json:**

QA1 corrected all `biodynamic_status` fields to `"none"` but left "biodynamic" language in prose fields. Found and fixed across 5 Dominio del Aguila wines:
- `taste.summary` fields: "biodynamic red," "biodynamically farmed" → "certified-organic," "organically farmed"
- `history.summary` fields: "biodynamically" → "organically"; "The estate achieved Demeter certification" → "certified-organic status from Consejo Ecologico de Castilla y Leon"
- Milestones: "Demeter certification obtained" → "certified-organic status obtained from Consejo Ecologico de Castilla y Leon"; "biodynamic plots" → "organic plots"

Note: For wines where taste was also stripped (dominio-del-aguila-reserva, gran-reserva, albillo, picaro-rosado), the `taste.summary` prose fix was moot — taste block was already empty.

**hidden-gems.json `cillar-de-silos`:** Description named "siblings Roberto, Oscar, and Amelia Aragon" as the family running the estate. Producer website (cillardesilos.es) does not name these individuals; source not verifiable. Removed the individual names; retained "A family-run estate."

**Result: 10 defects fixed (2 chef names, 2 founder cross-contaminations, 5 biodynamic prose fixes, 1 unverifiable name scrub)**

---

## Section E — Certification status

**Finca Torremilanos `demeter_certified`:** Confirmed. Producer website (torremilanos.com/en/biodynamic-vineyard-in-ribera-del-duero/) explicitly states "certified with all Demeter certificates of biodynamic agriculture in Ribera del Duero." PASS.

**Dominio del Aguila `organic_certified`:** Confirmed as certified organic (Consejo Ecologico de Castilla y Leon). Consistent with QA1 fix. PASS.

**Bodegas La Horra / Corimbo `organic_certified`:** Producer website (bodegaslahorra.es) confirms organic viticulture. PASS.

**Goyo Garcia Viadero `organic_certified`:** Confirmed via Vine Trail (UK importer) and Chambers Street Wines. PASS.

**Bodegas Protos organic range:** dietary.json stated `organic_certified` but the description explicitly admitted "the certifying body is not named on the producer website." Neither the producer website nor the evidence URL (retailer page) names the certifying body — only "certified organic vineyards" and "Ecologico" label designation. Per Section E, certifier name must appear on the producer's site; without the certifier named, this is `organic_practicing`.

**Fix:** Downgraded `bodegas-protos-organic-parcelas` from `organic_certified` → `organic_practicing`. Updated description to accurately reflect "organically farmed" status without confirmed third-party certifier name.

**Result: 1 defect fixed**

---

## Defect Summary

| # | Section | File | Entity/Slug | Fix |
|---|---------|------|-------------|-----|
| 1-66 | I (taste fabrication) | wines.json | 66 wines (directory evidence URLs) | Stripped taste blocks; nulled cuisine_evidence_url; fixed dead source_urls |
| 67 | D (chef name fabrication) | wine-restaurants.json | ambivium | Removed "Chef Cristobal Munoz" (actual chef: Marina de la Hoz) |
| 68 | D (chef name fabrication) | wine-restaurants.json | refectorio-abadia-retuerta | Removed "Chef Marc Segarra" (unverifiable) |
| 69 | D (owner cross-contamination) | hidden-gems.json | dominio-de-es | Jorge Monzon → Bertrand Sourdais; fixed cuisine_evidence_url |
| 70 | D (founder cross-contamination) | hidden-gems.json | bodegas-valduero-gumiel | "Frutos Martinez family" → "Gregorio Garcia Alvarez" |
| 71 | D (biodynamic prose residual) | wines.json | dominio-del-aguila-picaro-tinto | taste.summary, history.summary: biodynamic → organic |
| 72 | D (biodynamic prose residual) | wines.json | dominio-del-aguila-reserva | history.summary + milestone: Demeter → organic |
| 73 | D (biodynamic prose residual) | wines.json | dominio-del-aguila-gran-reserva | taste.summary, history.summary + milestone: biodynamic → organic |
| 74 | D (biodynamic prose residual) | wines.json | dominio-del-aguila-albillo | history.summary + milestone: biodynamic → organic |
| 75 | D (biodynamic prose residual) | wines.json | dominio-del-aguila-picaro-rosado | history.summary + milestone: biodynamic → organic |
| 76 | D (unverifiable name) | hidden-gems.json | cillar-de-silos | Removed "Roberto, Oscar, and Amelia Aragon" (unverifiable) |
| 77 | E (certification downgrade) | dietary.json | bodegas-protos-organic-parcelas | organic_certified → organic_practicing (certifier unnamed) |

**Total QA2 defects found and fixed: 77**
(66 taste-block fabrications + 11 ownership/name/certification defects)

---

## Final ship_safety outcome

`bash /station/repo/scripts/ship_safety.sh spain ribera-del-duero` — **ALL CHECKS PASSED** (0 HARD failures)

- validate_data.py: PASS (WARNs only — description length, SEO title length; these are pre-existing and not QA-scope)
- verify_entities.py: 0 ERR, 0 WARN
- check_cross_refs.py: 10/17 matched, 0 HARD misses (7 fetch-fails are unreachable external producer sites, not internal cross-ref failures)
- check_festival_dates.py: PASS (no annual festivals to check)
- check_external_urls.py: 18/18 URLs OK
- check_score_claims.py: 0 prose score-claims found

---

QA2-COMPLETE spain/ribera-del-duero | 77 defects fixed | ship_safety PASS (0 HARD)
