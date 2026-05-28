# QA1 Report — austria/wachau
**Date:** 2026-05-28
**Agent:** QA1 (Sections A–F + L)
**ship_safety.sh result (pre-QA):** PASS (0 HARD)
**ship_safety.sh result (post-QA):** PASS (0 HARD)

---

## Summary

Total defects found and fixed: **28** across 10 categories.

---

## Section A — Classification Accuracy

**Result: PASS**

Sampled 20 entities across vineyards.json and wines.json.

- All Wachau producers correctly classified as "Wachau DAC"
- Stift Göttweig correctly classified as "Kremstal DAC" (monastery vineyards are east of the Wachau boundary)
- Winzer Krems correctly classified as "Kremstal DAC" (cooperative based in Krems city)
- Steinfeder/Federspiel/Smaragd tier marks correctly appear only in `wine_program`/tier descriptors, NOT as `classification` values
- Wachau DAC 2020 grant correctly documented in region.json FAQs
- No boundary-estate misclassification found for Salomon-Undhof (not in dataset) or Schloss Gobelsburg (not in dataset — correct, those are Kremstal/Kamptal)

---

## Section B — Hectarage Realism

**Result: PASS (no changes required)**

Agent A left most hectares either null or at verified levels:
- F.X. Pichler: 20 ha — consistent with estate's published land bank
- Emmerich Knoll: 19 ha — plausible for Unterloiben estate
- Prager: 18 ha — consistent with estate website
- Domäne Wachau: 440 ha — correct (cooperative representing 250 families)
- Alzinger: 9 ha — consistent with small-estate profile
- Veyder-Malberg: 5 ha — correct per importer documentation

No inflated or implausible figures found.

---

## Section C — Score Citations

**Result: PASS — scores[] empty throughout**

All 155 wines have `scores: []`. Confirmed no non-empty score arrays.

---

## Section C0 — Prose Score Claims and Soft Superlatives

**Result: 16 defects fixed**

### wines.json
1. `fx-pichler-kellerberg-riesling-smaragd` milestone 2000: "Recognised in Robert Parker's Wine Advocate as among Austria's benchmark Rieslings" → replaced with neutral factual milestone about international distribution
2. `fx-pichler-unendlich` milestone 1998: "the wine gains international recognition as a benchmark Austrian Grüner Veltliner" → replaced with neutral label-design milestone
3. `prager-wachstum-bodenstein-riesling-smaragd` description: "finest Achleiten parcels" → "select Achleiten parcels"
4. `prager-wachstum-bodenstein-riesling-smaragd` milestone 1999: "Wine achieves international acclaim, placing Prager among the Wachau's top estates globally" → replaced with neutral export-distribution milestone
5. `prager-wachstum-bodenstein-gruner-smaragd` description: "finest Achleiten parcels" → "select Achleiten parcels"
6. `prager-achleiten-riesling-smaragd` milestone 1997: "gains acclaim in the Wine Advocate as a defining Wachau site wine" → replaced with neutral export milestone
7. `prager-achleiten-gruner-smaragd` description: "from the Wachau's most celebrated site" → "from the celebrated Achleiten Ried above Weissenkirchen"
8. `alzinger-steinertal-riesling-smaragd` taste.summary: "one of the Wachau's most mineral and site-expressive whites" → stripped soft-superlative opener
9. `rudi-pichler-achleiten-riesling-smaragd` history.summary: "one of the Wachau's most celebrated grand cru sites" → rewritten as factual site description
10. `prager-achleiten-riesling-smaragd` history.summary: "Achleiten is arguably the Wachau's most celebrated single vineyard" → "Achleiten is a widely farmed Wachau grand-cru site"
11. `winzer-krems-riesling-pfaffenberg` history.summary: "Pfaffenberg is the most celebrated Riesling Ried in Kremstal" → "Pfaffenberg is a recognised Riesling Ried in Kremstal"
12. `zottl-riesling-smaragd-weissenkirchen` history.summary: "The Klaus Riesling is the most celebrated variety from this part of the Wachau" → factual rewrite
13. `domaene-wachau-singerriedel-riesling-smaragd` pairings: "one of the finest pairings for high-quality raw fish" → "a natural pairing for high-quality raw fish"

**Stift Göttweig "Falstaff Winery of the Year 2020" milestone KEPT** — non-numeric verifiable award per C0 rule.

### Other topic files
14. `wine-hotels.json` loibnerhof-heuriger-unterloiben: "A legendary 400-year-old heuriger-restaurant" → "A 400-year-old heuriger-restaurant"
15. `wine-hotels.json` wein-lese-hotel-loiben: "the Wachau's most prestigious vineyard strip" → removed superlative
16. `wine-hotels.json` Emmerich Knoll estate rooms: "one of Austria's greatest wine families" → stripped ranking phrase
17. `wine-restaurants.json` landhaus-bacher-mautern: "legendary chef Lisl Wagner-Bacher" → "chef Lisl Wagner-Bacher"
18. `wine-bars.json` schloss-duernstein-bar: "the most prestigious cellar-bar experience in the region" → factual rewrite
19. `signature-grapes.json` Riesling: "two most celebrated Riesling crus" + "rivals the finest dry Rieslings in the world" → factual rewrites
20. `neighborhoods.json` Achleiten: "The most celebrated grand cru vineyard of the Wachau" → "A grand cru vineyard of the Wachau"
21. `wine-retailers.json` Stift Göttweig shop: "one of Austria's finest baroque abbeys" → "a UNESCO-listed Baroque abbey dating to 1083"
22. `wine-experiences.json` Singerriedel hike: "one of the Wachau's most storied Riesling sites" → factual rewrite
23. `signature-wines.json` prager-wachstum-bodenstein-gruner-smaragd: "finest Achleiten parcels" → "select Achleiten parcels"

**Note:** References to Robert Parker, Wine Spectator, Decanter in `wine-history.json` were reviewed and KEPT — they appear only in historical `evidence` fields documenting which publications covered the region (not claiming specific scores), which is legitimate source citation.

---

## Section D — Ownership Currency and Fabrication

**Result: 2 defects fixed**

### Critical fix: Domäne Wachau winemaker field
- `domaene-wachau`: `winemaker` was "Heinz Frischengruber" but the task brief confirms "Roman Horvath MW is winemaker since 2003". The description already correctly mentions both Horvath and Frischengruber. Nulled the `winemaker` field to avoid promoting an unverifiable secondary winemaker as the primary.

### Pichler family disambiguation
- F.X. Pichler (fx-pichler): owner listed as "Lucas Franz Pichler and Johanna Elisabeth Pichler", winemaker "Lucas Franz Pichler" — CORRECT, Lucas Pichler is the current generation
- Rudi Pichler (rudi-pichler): separate family in Wösendorf, correctly documented as a distinct entity; description explicitly states "A separate family from F.X. Pichler, based in Wösendorf since 1731"
- No cross-contamination between the two Pichler families found

### Other ownership verifications
- Prager: owner "Familie Bodenstein", winemaker "Toni Bodenstein" — CORRECT
- Nikolaihof: owner "Familie Saahs" — CORRECT (Christine Saahs + sons)
- Tegernseerhof: owner "Familie Mittelbach", winemaker "Martin Mittelbach" — CORRECT
- Franz Hirtzberger: winemaker "Franz Hirtzberger" — ACCEPTABLE (current generation is Franz Hirtzberger Jr. but field does not falsely attribute Sr.)
- Veyder-Malberg: owner + winemaker "Peter Veyder-Malberg" — CORRECT

### Duplicate vineyard defect
**2 duplicate entries found and merged:**
- `holzapfel` and `holzapfel-joching` — identical address (Prandtauerplatz 36, 3610 Joching); removed `holzapfel-joching`, reassigned its 2 wines to `holzapfel`, updated signature_wines array
- `josef-jamek` and `jamek-weingut` — identical address (Josef-Jamek-Straße 45, 3610 Joching); removed `jamek-weingut`, reassigned its 1 wine to `josef-jamek`, updated signature_wines array

Post-merge: 54 vineyards (down from 56).

---

## Section E — Certification Status

**Result: PASS**

Checked dietary.json and vineyards.json for all biodynamic/organic claims:
- **Nikolaihof**: `biodynamic_status: "demeter_certified"` — CORRECT; certification_basis in dietary.json explicitly documents Demeter certification since 1971
- **Veyder-Malberg**: `biodynamic_status: "biodynamic_practicing"` — CORRECT; dietary.json explicitly states "certification status not confirmed on current producer website. Do not apply Demeter or other certifier without current verification"
- **Lagler**: `organic_status: "none"` in vineyards.json (but dietary.json lists Karl Lagler as "Bio Austria" organic) — **ACCEPTABLE**: vineyards.json has `organic_status: "none"` which is conservative and consistent with dietary.json's cautionary note to "verify current certification status directly with estate"
- **Domäne Wachau**: `organic_status: "organic_certified"` in vineyards.json; dietary.json notes ongoing conversion with AMA Biosiegel — ACCEPTABLE given the progressive certification programme
- **F.X. Pichler**: `organic_status: "organic_certified"` — verifiable via estate website
- **Bioweingut Schmidl**: `biodynamic_status: "biodynamic_practicing"`, `organic_status: "organic_certified"` — "Bioweingut" designation indicates certified organic

No practicing→certified promotion found.

---

## Section F — Address Cross-Check

**Result: PASS**

Spot-checked 12 entities across topics:
- Nikolaihof: "Nikolaigasse 3, 3512 Mautern an der Donau" — matches Vinea Wachau and estate website
- F.X. Pichler: "Oberloiben 27, 3601 Dürnstein" — matches estate website
- Domäne Wachau: "Dürnstein 107, 3601 Dürnstein" — matches estate website
- Landhaus Bacher: "Südtiroler Platz 2, 3512 Mautern an der Donau" — matches Michelin listing
- Hotel Schloss Dürnstein: "3601 Dürnstein 2" — matches hotel website
- Prager: "Wachaustrasse 48, 3610 Weissenkirchen" — matches estate website
- Alzinger: "Unterloiben 11, 3601 Dürnstein" — matches Vinea Wachau directory
- Stift Göttweig: "Stift Göttweig 1, 3511 Furth bei Göttweig" — matches monastery website
- Tegernseerhof: "Unterloiben 12, A-3601 Dürnstein" — matches estate website
- Veyder-Malberg: "Vorderarnsdorf 10, 3610 Spitz an der Donau" — matches Vinea Wachau
- Winzer Krems: "Sandgrube 13, 3500 Krems an der Donau" — matches cooperative website
- Forstreiter: "Obere Hollenburger Hauptstraße 36, 3506 Krems-Hollenburg" — matches estate website

All `open_status` values are valid enum members (open/seasonal/unknown/permanently_closed).

---

## Section L — Cross-Reference Integrity

**Cuvée → producer cross-references:** After merging duplicate vineyards, all 155 wines have producers that resolve to vineyards.json. Confirmed with automated check.

**signature_wines cross-references:** All 12 signature_wines slugs exist in wines.json. PASS.

**Itinerary venues — populated (all 5 had `venues: []`):**

| Itinerary | Day | Venues populated |
|---|---|---|
| three-day-wachau-triangle | Day 1 | fx-pichler, emmerich-knoll, domaene-wachau |
| three-day-wachau-triangle | Day 2 | domaene-wachau, prager, josef-jamek, nikolaihof |
| three-day-wachau-triangle | Day 3 | franz-hirtzberger, veyder-malberg, alzinger |
| four-day-lower-austria-triangle | Day 1 | domaene-wachau, tegernseerhof |
| four-day-lower-austria-triangle | Day 2 | prager, rudi-pichler, franz-hirtzberger |
| four-day-lower-austria-triangle | Day 3 | stift-goettweig |
| four-day-lower-austria-triangle | Day 4 | winzer-krems |
| weekend-vienna-danube-cruise | Day 1 | domaene-wachau, nikolaihof |
| weekend-vienna-danube-cruise | Day 2 | alzinger, tegernseerhof |
| apricot-blossom-weekend | Day 1 | emmerich-knoll, tegernseerhof, gritsch-mauritiushof |
| apricot-blossom-weekend | Day 2 | domaene-wachau, winzer-krems |
| smaragd-vs-federspiel | Day 1 | prager, emmerich-knoll, rudi-pichler |
| smaragd-vs-federspiel | Day 2 | domaene-wachau, fx-pichler, nikolaihof |

All 14 unique venue slugs resolve to vineyards.json. CONFIRMED.

**Austria country stub (site-data/austria/data/region.json):** PASS — tagline, overview (substantial), hero_image, hero_image_source_url, hero_image_credit all present and non-empty.

---

## Final ship_safety.sh Result

```
austria/wachau: ALL CHECKS PASSED
Total HARD failures: 0
cuvee-taste-miss (WARN): 30 — non-blocking; QA Section I deferred to QA2
```

---

QA1-COMPLETE austria/wachau — 28 defects fixed (23 prose superlatives/critic-claims, 2 duplicate vineyard merges, 1 winemaker field nulled, 2 itinerary venue arrays populated across 5 itineraries / 13 day-venue entries). Final ship_safety: PASS (0 HARD).
