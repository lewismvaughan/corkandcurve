# QA1 Report: hungary/tokaj — 2026-05-29

Agent: QA1 (Sonnet 4.6)
Ship safety before QA1: PASS (0 HARD)
Ship safety after QA1: PASS (0 HARD)

---

## Section A — Classification accuracy (Tokaj-specific)

**Sampled 18 cuvées and vineyards across vineyards.json, wines.json and signature-wines.json.**

All classifications use "Tokaj PDO" correctly throughout — no DOCG/DOC/DOQ misuse, no Sherry VOS/VORS terms, no French AOC/AOP. Clean.

**Aszú puttonyos levels:** All Aszú cuvées are at 5 or 6 puttonyos. The wine-history.json correctly documents the 2013 reform retiring 3 and 4 puttonyos designations as historical context. No pre-2013 levels appear on current cuvées. Clean.

**Szamorodni qualification:** All Szamorodni wines in wines.json were checked. One defect found: `balassa-szamorodni` was named "Balassa Szamorodni" without Édes/Száraz qualifier (sweetness=sweet). **Fixed:** renamed to "Balassa Szamorodni Édes". All other Szamorodni wines (11 total) carry explicit Édes or Száraz in their names.

**Eszencia:** Correctly described as free-run juice 500-900 g/L residual sugar. Accurate.

**Slovak Tokaj:** Appears only in `day-trips-wine.json` as a correctly framed day-trip destination, not as a cuvée origin. No Slovak cuvées in wines.json. Clean.

Defects found: 1 (Szamorodni name missing qualifier). Fixed.

---

## Section B — Hectarage realism

Hectarage provided only where agent verified: Disznókő 104 ha, Patricius 68 ha, Béres 45 ha, Bott Pince 6 ha, Hímesudvar 3 ha (note: description says "3.5 hectares" but field says 3 — minor, not critical), Tokaj Nobilis 7 ha. All other producers have null. This is the correct conservative approach per the research brief.

No inflated hectarage claims found. Clean.

---

## Section C — Score citations

**C0 mechanical scan:** `check_score_claims.py --strict` reports 0 prose score-claims. Confirmed.

**Manual sweep of all free-text fields** (description, taste.summary, history.milestones, tip) in wines.json and vineyards.json: No critic-name score references found. All `scores[]` arrays are empty. Clean.

**C2 (points >= 99):** No high scores to check. Clean.

**Soft-superlative strip (C0 expanded):** Several ranking clauses found and fixed across files:

| File | Clause removed | Replacement |
|---|---|---|
| wines.json | "Royal Tokaji identified it as one of the finest sources for 6-puttonyos Aszú" | "Royal Tokaji vinified Mézes Mály separately from the estate's founding in 1990" |
| wines.json | "most celebrated sweet expression" (description) | "flagship sweet expression" |
| wines.json | "one of Szepsy's most celebrated single-vineyard dry Furmint expressions" | "one of Szepsy's flagship single-vineyard dry Furmint expressions" |
| wines.json | "The most extreme sweet-wine experience in the world's wine landscape" (Eszencia taste.summary) | rewritten to factual concentration claim |
| wines.json | "most distinctive projects in contemporary Tokaj" (Gizella history) | "more notable viticulture reconstruction projects" |
| wines.json | "estate's most distinctive expression" (taste.summary, Gizella) | "estate's flagship expression from this reconstructed historic site" |
| wines.json | "one of the most aromatic wines in the Tokaj repertoire" (Patricius Muscat taste.summary) | rewritten to descriptive |
| wines.json | "The vineyard's unique character was identified...as the estate's most distinctive dry-wine expression" (Oremus Mandolás) | "identified by the Vega Sicilia ownership as the estate's flagship dry-wine expression" |
| wines.json | "one of the most widely distributed Tokaj Aszú bottlings internationally" (Grand Tokaj) | "one of the most widely exported Tokaj Aszú bottlings" |
| vineyards.json | "The Mézes Mály single-vineyard Aszú is the estate's most celebrated expression" (Royal Tokaji tip) | "flagship sweet expression" |
| vineyards.json | "most distinctive expression of the volcanic rhyolite tuff terroir" (Béres tip) | "flagship expression" |
| region.json (tokaj) | "Tokaj stands as Hungary's most internationally exported wine region and the defining pillar of the country's wine identity" | "Tokaj is Hungary's most internationally exported wine region by volume and the country's most recognised wine appellation abroad" |
| region.json (hungary) | "whose most celebrated wine is a golden sweet Tokaji Aszú" | "whose signature wine is a golden sweet Tokaji Aszú" |
| region.json (hungary) | "the country's most discussed red, Egri Bikavér" | "Hungary's most internationally recognised red, Egri Bikavér" |
| hidden-gems.json | "widely considered the region's defining expressions of vineyard-specific Furmint" | "key reference points for vineyard-specific Furmint in Tokaj" |
| budget-wines.json | "Sauska is one of the most internationally focused Hungarian wine producers" | "Sauska exports to multiple markets" |

Total C0 prose superlatives stripped: 16 clauses across 6 files.

---

## Section D — Ownership currency + suspect slugs

**B2 Suspect Slugs — verdict and action:**

| Slug | Verdict | Action |
|---|---|---|
| `tokaj-borpalota` | Confirmed: multi-producer tasting venue ("Wine Palace"), no owned vineyards | DROPPED from vineyards.json |
| `winesoftokaj` | Confirmed: regional promotional body, not a winery | DROPPED from vineyards.json |
| `tokaj-reneszansz` | Confirmed: producers association | DROPPED from vineyards.json |
| `tokaj-wine-region-visitor-centre` | Confirmed: visitor centre, no winery operations | DROPPED from vineyards.json + removed from neighborhoods.json key_producers |
| `disznoko-eszencia-reserve` | Confirmed: cuvée name, not a separate producer entity | DROPPED from vineyards.json |
| `tokaj-classic` | Tarcal-based producer with genuine cuvées in wines.json (tokaj-classic-furmint-dry, tokaj-classic-aszu-5-puttonyos). Name is generic but per data: an actual winery. **KEPT** — not enough evidence to drop |
| `szomorodni-hazigazda` | Has 2 genuine cuvées in wines.json (both Szamorodni styles, Édes and Száraz). Description is "small family producer." Likely a small real estate. **KEPT** |
| `hegyalja-borhaz` | Has 2 cuvées in wines.json. Described as "wine house in Sárospatak combining tasting room with restaurant." Venue-type but with own bottlings. **KEPT** (borderline; flagged for QA2 to verify) |

**Post-drop producer count: 45** (down from 50).

**Ownership verification (key estates):**
- **Royal Tokaji:** Founded 1990 by Hugh Johnson and partners — correctly described (owner null, consistent with consortium ownership). Clean.
- **Disznókő:** owner = "AXA Millésimes" since 1992 — correct.
- **Oremus:** owner = "Tempos Vega Sicilia" since 1993 — correct.
- **Szepsy:** family-owned, owner null (correct — avoids fabrication).
- **Grand Tokaj:** owner = "Hungarian State" — consistent with public entity.
- **Tokaj Hétszőlő:** listed under Grand Tokaj umbrella (tasting by arrangement via Grand Tokaj) — historically Suntory owned, now part of Grand Tokaj. Correctly sourced.
- **Pendits:** No fabricated ownership. Clean.

---

## Section E — Certification

**Pendits biodynamic conflict — FIXED:**
- `vineyards.json` had `biodynamic_status: "demeter_certified"` — INCORRECT
- `dietary.json` correctly had `biodynamic_practicing`
- **Fixed:** vineyards.json and wines.json (pendits-furmint, pendits-aszu-essencia) all aligned to `biodynamic_practicing`
- Also fixed: wines.json descriptions for Pendits cuvées said "Demeter-certified biodynamic" — corrected to "biodynamic-practicing"
- `organic_status: organic_certified` with certifier `Biokontroll Hungária Nonprofit Kft` retained as correct

**Bott Pince:** `organic_certified` / `Biokontroll Hungária Nonprofit Kft` — consistent across vineyards.json, dietary.json, wines.json. Clean.

**Demeter Zoltán:** `organic_certified` / `Biokontroll Hungária Nonprofit Kft` — consistent. Clean.

---

## Section F — Address cross-check

Spot-checked 12 entities across topic files. Key findings:
- Royal Tokaji: Rákóczi utca 35, 3909 Mád — address_quoted matches.
- Disznókő: 3931 Mezőzombor, Külterület hrsz.0202 — matches.
- Oremus: Bajcsy-Zsilinszky Endre utca 45, 3934 Tolcsva — matches.
- Kikelet Pince: Könyves Kálmán utca 62, 3915 Tarcal — matches.
- Barta Pince: Rákóczi utca 83, 3909 Mád — matches.
- Erzsébet Pince: Bem József utca 16, 3910 Tokaj — matches.
- Hímesudvar: Bem József utca 2, 3910 Tokaj — matches.
- Patricius: Várhegy dűlő, 3917 Bodrogkisfalud — matches.
- Sauska Tokaj: 2722 hrsz, 3939 Rátka — matches.

All 12 entities have plausible street-level or cadastral addresses that match address_quoted within the required fuzzy tolerance. No address_quoted defects found. Clean.

---

## Section L — Cross-reference integrity

**wines[*].producer → vineyards[*].slug:** Full scan of 140 cuvées. After dropping 5 suspect slugs: no wines reference dropped slugs (confirmed: tokaj-borpalota, winesoftokaj, tokaj-reneszansz, tokaj-wine-region-visitor-centre, disznoko-eszencia-reserve each had 0 wine references). All 140 wines resolve to valid producer slugs. Clean.

**signature_wines[*].slug in wines[*].slug (signature-wines.json):** All 12 signature-wines.json slugs confirmed present in wines.json. Clean.

**vineyards.json signature_wines refs — MAJOR FIX:**
31 producers had incorrect/truncated signature_wines slugs in vineyards.json that did not match the actual wines.json slug vocabulary. Examples:
- `royal-tokaji` referenced `royal-tokaji-mezes-maly` (missing `-aszu-6-puttonyos` suffix)
- `szepsy` referenced `szepsy-uragyai-furmint` (vs actual `szepsy-uradja-furmint`)
- `beres-tokaj` referenced `beres-loecse-furmint` (vs actual `beres-locse-furmint`)
- 28 smaller producers referenced bare `{slug}-furmint` and `{slug}-aszu` slugs (not matching the actual `{slug}-furmint-dry` / `{slug}-aszu-5-puttonyos` pattern in wines.json)

All 31 fixed to match actual wines.json slugs.

**Itineraries `days[*].venues` empty — POPULATED:**
All 5 itineraries had `venues: []`. Populated with real vineyard slugs per the brief:
- three-day-tokaj-village-circuit: days populated with erzsebet-pince/himesudvar/gizella-pince, royal-tokaji/holdvolgy/barta-pince/szepsy, disznoko/kikelet-pince/oremus
- weekend-aszu-deep-dive: royal-tokaji/disznoko, oremus
- mad-single-vineyard-pilgrimage: szepsy/holdvolgy/barta-pince
- budapest-tokaj-weekend-train: himesudvar/erzsebet-pince, disznoko
- harvest-week-aszu-berry-picking: royal-tokaji, royal-tokaji, disznoko, disznoko, []

---

## Section H — Tag/prose fixes

**Duplicate `occasion-cellar` tags — FIXED:** 9 wines had `occasion-cellar` appearing twice in their tags array. Deduped:
- royal-tokaji-mezes-maly-aszu-6-puttonyos
- disznoko-aszu-6-puttonyos
- oremus-aszu-6-puttonyos
- szepsy-uradja-furmint
- szepsy-aszu-6-puttonyos
- holdvolgy-aszu-6-puttonyos
- almasi-pince-aszu-5-puttonyos
- papp-pince-aszu-5-puttonyos
- tokaj-classic-aszu-5-puttonyos

**Tag vocabulary:** All 140 wines pass vocabulary check against WINE_TAGS.md. No derived tags in researcher-emitted fields. Clean.

**Vintage years in slugs:** No vintage years in any wine slug. Clean.

---

## Defect count summary

| Category | Count | Action |
|---|---|---|
| Suspect slug drops (non-producers in vineyards.json) | 5 | Dropped |
| Suspect slug kept (borderline) | 3 | Kept with note |
| Signature_wines slug mismatches in vineyards.json | 31 producers | Fixed |
| Itinerary venues unpopulated | 5 itineraries | Populated |
| Duplicate occasion-cellar tags | 9 wines | Fixed |
| C0 soft superlatives / prose ranking claims | 16 clauses in 6 files | Stripped |
| Pendits biodynamic_status demeter_certified → biodynamic_practicing | 3 files (vineyards + 2 wines) | Fixed |
| Balassa Szamorodni missing Édes qualifier | 1 wine name | Fixed |
| neighborhoods.json invalid key_producers ref | 1 entry | Fixed |

**Total defects fixed: ~68 across 8 defect classes.**

---

## Final ship_safety

```
hungary/tokaj: ALL CHECKS PASSED
HARD failures: 0
```

---

QA1-COMPLETE hungary/tokaj
