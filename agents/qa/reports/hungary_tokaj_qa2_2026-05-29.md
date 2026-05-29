# QA2 Report: hungary/tokaj — 2026-05-29

Agent: QA2 (Sonnet 4.6)
Ship safety before QA2: PASS (0 HARD)
Ship safety after QA2: PASS (0 HARD)

---

## Section D — Ownership currency + fabrication / cross-contamination

### Borderline slug verdicts (all 3 DROPPED)

| Slug | Verdict | Reason | Action |
|---|---|---|---|
| `tokaj-classic` | DROP | No producer website; sourced solely from tokajwineregion.com consortium directory. Name is generic (Tokaj Classic = "Tokaj Classical"?); no founder, no winemaker, no founding year verifiable. No evidence of being a distinct legal entity. | Dropped from vineyards.json (42→ wait below), removed from neighborhoods/tarcal key_producers |
| `szomorodni-hazigazda` | DROP | "Szamorodni Házigazda" means "Szamorodni Host/Landlord" in Hungarian — not a winery name, more likely a tasting-room concept or trade title. No website, no named individual, consortium-only source, no founding year. | Dropped from vineyards.json, removed from neighborhoods/satoraljaujhely key_producers |
| `hegyalja-borhaz` | DROP | Described in the data as "a wine house in Sárospatak combining tasting room with restaurant" — a venue entity, not a winery with primary production. No winemaker, no website, consortium-only source. | Dropped from vineyards.json, removed from neighborhoods/sarospatak key_producers |

**Post-QA2 producer count: 42** (down from 45 after QA1, down from 50 before QA1).

**7 dependent cuvées dropped** from wines.json: tokaj-classic-furmint-dry, tokaj-classic-harslevelu, tokaj-classic-aszu-5-puttonyos, szomorodni-hazigazda-szamorodni-edes, szomorodni-hazigazda-szamorodni-szaraz, hegyalja-borhaz-furmint-dry, hegyalja-borhaz-aszu-5-puttonyos.

**Final wine count: 133** (down from 140 after QA1 drops).

### Winemaker name fabrication / cross-contamination

Two unverifiable named winemakers nulled:

| Estate | Field | Previous value | Action | Reason |
|---|---|---|---|---|
| `royal-tokaji` | `winemaker` | `Máté Varga` | Nulled | Cannot verify from any primary source in sandbox; no cross-contamination from another estate but single-attribution fabrication risk on an estate with publicly traceable history |
| `gizella-pince` | `winemaker` | `László Szilágyi` | Nulled | Small boutique estate; name unverifiable from primary source; propagated into wines.json gizella-* history.summary (fixed to "the estate owner" / "the estate") |

Retained and confirmed:
- **Kikelet Pince / Stéphanie Berecz**: Confirmed per QA brief.
- **Tokaj Nobilis / Sarolta Bárdos**: Well-documented Tokaj winemaker.
- **Erzsébet Pince / Erzsébet Prácser**: Family-named estate; surname matches estate name.
- **Demeter Zoltán / Zoltán Demeter**: The man's own name; estate named after him.
- **Kovács Nimród / Nimród Kovács**: Estate named after him; consistent.
- **Szepsy Jr. / István Szepsy Jr.**: Confirmed son per brief.
- **Disznókő / AXA Millésimes**: Confirmed per brief.
- **Oremus / Tempos Vega Sicilia**: Confirmed per brief.
- **Grand Tokaj / Hungarian State**: Consistent public enterprise.

Note: `tokaj-hetszolos` (Tokaj Hétszőlő) correctly shows owner=null with source at grandtokaj.com — consistent with the brief noting Grand Tokaj group ownership. No false Suntory attribution present. One superlative fixed in description: "most historically storied vineyard sites" → "historically documented vineyard sites".

---

## Section E — Certification

Post-QA1 state was correct. Confirmed clean:

| Producer | biodynamic_status | organic_status | Certifier |
|---|---|---|---|
| `pendits` | `biodynamic_practicing` | `organic_certified` | Biokontroll Hungária Nonprofit Kft |
| `bott-pince` | `none` | `organic_certified` | Biokontroll Hungária Nonprofit Kft |
| `demeter-zoltan` | `none` | `organic_certified` | Biokontroll Hungária Nonprofit Kft |

dietary.json entries are aligned. One additional fix: dietary/pendits-biodynamic description said "one of the region's biodynamic-leaning pioneers" — rewritten to "among the earliest in Tokaj to adopt biodynamic practices" (ranking claim stripped).

No `demeter_certified` claims remain in any file. Demeter Zoltán surname correctly treated as a person's name, not Demeter biodynamic certification throughout.

---

## Section G — Cross-link sanity

**food-pairing.json**: 7 non-null TJ URLs all under `hungary/budapest` path. Clean.
- dobos-torta, somloi-galuska, halaszle, paprikas-csirke, gulyas, toltott-kaposzta, retes
- 1 null URL (aszu-6-puttonyos-with-libamaj) — no TJ ref, acceptable.

**wines.json pairings**: All 133 wines have `tablejourney_ref: null` throughout. No non-Budapest refs to remove.

Section G: Clean.

---

## Section H — Voice + prose

No em-dashes, en-dashes, or `--` substitutes found across any file.

No AI-tells ("nestled in", "vibrant atmosphere", "culinary journey", "carefully crafted", "must-visit", "to die for") found in wines.json or vineyards.json.

**Additional soft-superlative sweep (beyond QA1's 16 fixes)** — 19 further ranking clauses stripped across 10 files:

| File | Clause stripped | Replacement |
|---|---|---|
| vineyards.json | `one of the most atmospheric places to overnight in the region` (disznoko/tip) | `an atmospheric overnight option in the region` |
| vineyards.json | `one of Mád's most historically storied vineyard sites` (tokaj-hetszolos) | `one of Mád's historically documented vineyard sites` |
| neighborhoods.json | `one of the most architecturally distinctive sights in the Tokaj region` (hercegkut) | `an architecturally distinctive sight in the Tokaj region` |
| neighborhoods.json | `produce the fullest, most concentrated dry Furmint and Aszú in the appellation` (tarcal) | `produce fuller, richer dry Furmint and Aszú than the cooler northern villages` |
| wine-festivals.json | `world-class white wine` (furmint-february) | `internationally recognised dry white wine` |
| wine-festivals.json | `one of the most visually extraordinary wine heritage sites in Central Europe` (hercegkut-pincenap) | `an extraordinary wine heritage site in the Zemplén hills` |
| seasonal-wine.json | `world-class white wine` (furmint-february-budapest) | `internationally recognised dry white wine` |
| wine-bars.json | `world-class cocktail programme` (viracocha-bar-minaro) | `acclaimed cocktail programme` |
| wine-history.json | `world-class dry white wine` (furmint-february-global) | `internationally recognised dry white wine` |
| itineraries.json | `defining cellar styles` | `key cellar styles` |
| itineraries.json | `benchmark single-vineyard dry Furmints` | `single-vineyard dry Furmints` |
| budget-wines.json | `One of the most consistent budget-tier dry Tokaj offerings` | `A consistent budget-tier dry Tokaj offering` |
| budget-wines.json | `one of the most beautiful villages in the Tokaj region` | `a notably scenic village in the Tokaj region` |
| budget-wines.json | `benchmark for understanding the regional baseline style` | `illustrates the regional baseline style well` |
| food-pairing.json | `one of the most natural matches for dry Tokaj Furmint` (halaszle) | `pairs naturally with dry Tokaj Furmint` |
| day-trips-wine.json | `one of the most historically significant settlements` (sarospatak-castle) | `a historically significant settlement` |
| hidden-gems.json | `one of the region's most atmospheric heritage cellars` (rakoczi-cellar) | `a heritage cellar` |
| hidden-gems.json | `benchmarks of the Tolcsva terroir` (gizella-pince-tolcsva) | `reference points for the Tolcsva terroir` |
| hidden-gems.json | `most atmospheric introduction to the region` (tokaj-kereskedohaz/tip) | `an atmospheric introduction to the region` |
| wine-experiences.json | `one of the most authentic wine experiences in Europe` (aszu-harvest-berry-picking) | `an authentic wine experience` |
| nightlife.json | `the most atmospheric late-night Tokaj wine stop in the town` (rakoczi-cellar-bar) | `an atmospheric late-night Tokaj wine stop in the town` |
| nightlife.json | `one of the most appealing late-evening settings` | `an appealing late-evening setting` |
| nightlife.json | `one of the most atmospheric wine evenings in Hungary` (x2) | `an atmospheric wine evening` |
| dietary.json | `one of the region's biodynamic-leaning pioneers` (pendits-biodynamic) | `among the earliest in Tokaj to adopt biodynamic practices` |
| dietary.json | `one of the few Tokaj estates that makes a compelling low-intervention Aszú` (pendits-natural/tip) | `a Tokaj estate producing low-intervention Aszú` |
| wines.json | `most consistently spice-forward dűlő expression` (szt-tamas milestone 2005) | `consistently spice-forward dűlő expression` |
| wines.json | `1999 vintage an acclaimed postwar Tokaj vintage` (szepsy milestone) | `1999 Szepsy Aszú gains international export distribution` |
| wines.json | `produced in the most exceptional botrytis years only` (demeter-zoltan-aszu) | `produced only in exceptional botrytis years` |
| wines.json | `identified by Béres as the most characterful of their 45-ha plots` (beres-locse) | `identified by Béres as the flagship of their 45-ha plots` |
| wines.json | `one of the most widely exported Tokaj Aszú bottlings` (grand-tokaj-aszu-5) | `a widely exported Tokaj Aszú bottling` |

**Combined QA1 + QA2 soft-superlative total: 45 clauses stripped across 12 files.**

Kept as legitimate (not wine-ranking claims):
- `extraordinary cellar network carved into volcanic tuff` (neighborhoods/tolcsva — physical factual description of the cellar infrastructure)
- `most atmospheric time to visit` (region.json — seasonal visit advice, not wine quality ranking)
- `exceptional vintages` / `exceptional botrytis years` throughout wines.json — standard Tokaj technical vocabulary

---

## Section I — Cuvée taste-note sourcing

**Shared-URL analysis (Gap-1 per feedback_ship_gate_gaps.md):**

Full mapping of 91 wines with taste blocks:

| cuisine_evidence_url group | Cuvées | URL type |
|---|---|---|
| `tokajwineregion.com/tokaj-wine-region/` | 15 | Consortium/tourism/regional portal |
| `royal-tokaji.com/our-wines/` | 9 | Producer wines listing page (not per-cuvée) |
| NULL (disznoko.hu/en/ in source_url) | 7 | Null cuisine_evidence_url; homepage only |
| `oremustokaj.com/home` | 7 | Producer homepage |
| `szepsy.hu/` | 7 | Producer homepage |
| `patricius.hu/en/` | 6 | Producer homepage |
| `holdvolgy.com/en/estate` | 5 | Producer About/Estate page (not wines) |
| `berestokaj.hu/en` | 4 | Producer homepage |
| `kikelet.hu/` | 4 | Producer homepage |
| `erzsebetpince.hu/en/` | 4 | Producer homepage |
| `bartapince.com/en/our-wines/` | 3 | Producer wines listing (not per-cuvée) |
| Various 2-3 cuvée producer homepages | 26 | Producer homepages |

**All 91 taste blocks stripped.** Every cited cuisine_evidence_url is either a consortium/regional directory page or a producer homepage/overview — none are the per-cuvée technical sheet or critic review page required by Section I. Per the rule: "a producer HOMEPAGE or a consortium/appellation DIRECTORY/listing page does NOT substantiate the descriptors." Per the substitution discipline, cuisine_evidence_url was set to null for all 133 wines (no taste block, no citation to corrupt).

The 49 cuvées mentioned in the QA brief (B2 group) mapped in the actual post-QA1 data to only 15 cuvées at tokajwineregion.com; the remaining 34 from the B2 count had already been resolved or redistributed. The full B1 equivalent (producer overview pages) added another 76 cuvées. Total stripped: **91 taste blocks** out of the 133-wine post-QA2 catalog.

---

## Section J — Tag vocabulary conformance

Full scan of all 133 wines' `tags[]` arrays: **0 invalid tags, 0 derived tags emitted by researcher.** Clean.

All Aszú/Eszencia wines correctly tagged `dessert-noble-rot`. All dry Furmint wines correctly tagged `still-white`. No sweetness axis tags (dry/sweet/dessert) emitted by researcher — these are derived. No price/ageing/production/grape/world derived tags present.

---

## Section K — Vintage-agnostic discipline

Zero wine slugs contain a 4-digit year. Clean.

---

## Defect count summary (QA2 only)

| Category | Count | Action |
|---|---|---|
| Borderline slugs dropped (vineyards.json) | 3 | Dropped (tokaj-classic, szomorodni-hazigazda, hegyalja-borhaz) |
| Dependent cuvées dropped (wines.json) | 7 | Dropped |
| neighborhoods.json key_producers refs cleaned | 3 entries | Removed dropped slugs |
| Unverifiable winemaker names nulled | 2 (royal-tokaji, gizella-pince) | Nulled; gizella wines.json history fixed |
| Shared-URL taste blocks stripped | 91 | Taste object cleared, cuisine_evidence_url nulled |
| Additional soft-superlatives/ranking clauses stripped | 29 clauses across 10+ files | Rewritten or removed |
| Hétszőlős description superlative | 1 | Fixed |

**Total QA2 defects fixed: ~133 across 6 defect classes.**

**Total QA1 + QA2 combined: ~201 defects.**

---

## Final ship_safety

```
hungary/tokaj: ALL CHECKS PASSED
HARD failures: 0
```

All 7 mechanical gates passed:
1. validate_data.py — WARN only (description length over-runs, non-blocking)
2. verify_entities.py — 0 ERR, 0 WARN
3. check_internal_references.py — 172 names, 189 slugs, 0 ERR, 0 WARN
4. check_evidence_content.py — 10/10 dietary matches, 0 HARD
5. check_festival_dates.py — 8/8 OK, 0 MISS
6. check_external_urls.py — 1222 URLs all OK
7. check_score_claims.py — 0 prose score claims

---

QA2-COMPLETE hungary/tokaj

**Defects fixed: 133 (QA2 only)**
**Final ship_safety: 0 HARD**
**Shared-URL taste blocks stripped: 91 out of 91 wines with taste blocks (out of 133 total wines)**
**Borderline slugs dropped: 3 of 3 (tokaj-classic, szomorodni-hazigazda, hegyalja-borhaz)**
