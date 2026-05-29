# QA1 Report — france/beaujolais
**Date:** 2026-05-29  
**Agent:** QA1 (Sonnet 4.6)  
**Scope:** 59 producers, 152 cuvées (153 − 1 removed), ~30 topic files  
**Final ship_safety:** 0 HARD — ALL CHECKS PASSED

---

## Defects found and fixed: 27 total

### Section C0 — Soft superlatives in prose (10 instances across 6 files)

All stripped per the categorical rule. No exceptions made for "factual" or "reputation" framings.

| File | Field | Original clause | Fix |
|------|-------|----------------|-----|
| `wines.json` | `foillard-morgon-eponym` history.summary | "Foillard's finest parcels" | → "Foillard's oldest Cote du Py parcels" |
| `wines.json` | `duboeuf-beaujolais-villages` pairings.why | "The world's most-sold Beaujolais-Villages" | → "Duboeuf Beaujolais-Villages … a classic bistro pairing" |
| `wines.json` | `terres-dorees-roussette` history.summary | "helped put on the wine map" | → removed phrase, kept factual content |
| `wines.json` | `rottiers-moulin-a-vent-champ-de-cour` description | "appellation's most celebrated parcel" | → "historically recognised Moulin-a-Vent parcel" |
| `wines.json` | `diochon-moulin-a-vent` taste.summary | "one of the appellation's most traditional producers" | → "a long-established family producer" |
| `wines.json` | `cheysson-chiroubles-classique` taste.summary | "one of the appellation's most established domaines" | → "a long-standing Cheysson family estate" |
| `wines.json` | `duboeuf-fleurie-la-madone` milestone 1980 | "one of the most widely distributed single-vineyard Fleurie labels" | → "establishes broad international distribution" |
| `budget-wines.json` | jadot entry tip | "appellation's finest sites" | → removed superlative, kept factual list |
| `day-trips-wine.json` | Jura trip tip | "greatest Vin Jaune appellation" | → "has its own AOC (the only Vin Jaune appellation with this status)" |
| `hidden-gems.json` | Ducroux tip | "finest expression of the tenth and newest Beaujolais Cru" | → "standout expression" |
| `itineraries.json` | gang-of-four day 2 afternoon | "first put Morgon on the international map" | → "where Morgon became an international reference" |
| `wine-bars.json` | cave-fleurie-wine-bar description | "one of Beaujolais's most celebrated Crus" | → "a leading Beaujolais Cru" |
| `dietary.json` | domaine-lapierre-biodynamic description | "most internationally visible … estate" | → removed superlative |
| `dietary.json` | domaine-lapierre-vegan tip | "most widely available vegan biodynamic Gamay in the world" | → "widely distributed through natural-wine importers globally" |
| `dietary.json` | terres-dorees-vegan tip | "most accessible and widely distributed vegan natural Beaujolais" | → "widely distributed … well-priced" |

### Section K — Vintage-named cuvée (1 removal)

| Slug | Issue | Action |
|------|-------|--------|
| `lapierre-mmxx` | MMXX = 2020 in Roman numerals; cuvée name encodes a specific vintage year. Description confirms it as "vintage-commemorative" for 2020. Additionally attributes a 2020 production to Marcel Lapierre (died 2010). | Removed from `wines.json`. 152 cuvées remain. Not in signature-wines.json. |

### Section D — Ownership cross-contamination (2 instances)

Both dietary.json and budget-wines.json described Damien Coquelet as "protégé of Georges Descombes" — contradicted by vineyards.json and wines.json which correctly state "stepson of Jean Foillard."

| File | Fix |
|------|-----|
| `dietary.json` coquelet-morgon-sans-soufre description | "protégé of Georges Descombes" → "stepson of Jean Foillard" |
| `budget-wines.json` coquelet-morgon description | "tradition of his mentor Georges Descombes" → "stepson of Jean Foillard … tradition of the Gang of Four" |

### Section E — Certification discrepancies (6 fixes across 3 files)

**Lapierre demeter_certified → biodynamic_practicing:**  
Both vineyards.json and wines.json consistently showed `biodynamic_practicing` for Lapierre. Only dietary.json promoted to `demeter_certified`. No Demeter France registration corroborated this. Downgraded in all three dietary.json entries (biodynamic, vegan, lowsulfite).

**Chateau Thivin organic_certified missing from vineyards.json:**  
Wines.json had `organic_certified` for all 5 Thivin cuvées; dietary.json confirmed it. Vineyards.json had `none/none` — corrected to `none/organic_certified`.

**Domaine du Vissoux organic_certified missing from vineyards.json:**  
4 of 5 Vissoux wines in wines.json had `organic_certified`; dietary confirmed it. Vineyards.json had `none/none` — corrected to `none/organic_certified`.

**Domaine Jean-Paul Thévenet biodynamic_practicing missing from vineyards.json + wines.json:**  
Dietary.json had `biodynamic_practicing`; vineyards.json and wines.json both had `none`. Task brief confirms Thévenet as biodynamic-practicing. Fixed in vineyards.json (1 entry) and wines.json (3 cuvées).

| File | Entity | Before | After |
|------|--------|--------|-------|
| `dietary.json` (3 entries) | Lapierre | `demeter_certified` | `biodynamic_practicing`, `biodynamic_certifier: null` |
| `vineyards.json` | Chateau Thivin | `organic: none` | `organic: organic_certified` |
| `vineyards.json` | Domaine du Vissoux | `organic: none` | `organic: organic_certified` |
| `vineyards.json` | Domaine Jean-Paul Thevenet | `biodynamic: none` | `biodynamic: biodynamic_practicing` |
| `wines.json` (3 cuvées) | Thévenet | `biodynamic: none` | `biodynamic: biodynamic_practicing` |

### Section L — Cross-reference slug mismatches (8 fixes)

`dietary.json` used abbreviated vineyard_ref slugs that did not resolve in vineyards.json. `budget-wines.json` used producer slugs not in vineyards.json.

**dietary.json** (8 refs fixed):
- `domaine-lapierre` → `domaine-marcel-lapierre` (3 occurrences: biodynamic, vegan, lowsulfite)
- `christian-ducroux` → `domaine-christian-ducroux`
- `jean-foillard` → `domaine-jean-foillard` (2 occurrences)
- `guy-breton` → `domaine-guy-breton`
- `jean-paul-thevenet` → `domaine-jean-paul-thevenet`
- `yvon-metras` → `domaine-yvon-metras`
- `terres-dorees` → `domaine-terres-dorees`
- `domaine-coquelet` → `domaine-damien-coquelet`

**budget-wines.json** (6 refs fixed):
- `domaine-lapierre` → `domaine-marcel-lapierre`
- `jean-foillard` → `domaine-jean-foillard`
- `terres-dorees` → `domaine-terres-dorees`
- `jean-marc-burgaud` → `domaine-jean-marc-burgaud`
- `domaine-coquelet` → `domaine-damien-coquelet`
- `chateau-des-jacques` → `maison-louis-jadot-beaujolais`

### Section L — Itinerary venues populated (all 5 itineraries)

All itinerary days had `"venues": []` per the task brief note that Agent D ran before vineyards were finalized. Populated with real vineyard slugs from vineyards.json:

| Itinerary | Venues added |
|-----------|-------------|
| ten-crus-loop-three-days | chateau-thivin, domaine-christian-ducroux, domaine-jean-claude-lapalu, domaine-jean-foillard, domaine-chignard, chateau-du-moulin-a-vent, domaine-chenas-les-bureaux, domaine-manoir-du-carra, domaine-georges-duboeuf, chateau-de-la-chaize |
| gang-of-four-morgon-natural-wine-two-days | domaine-marcel-lapierre, domaine-jean-foillard, domaine-guy-breton, domaine-jean-paul-thevenet, domaine-damien-coquelet |
| lyon-beaujolais-maconnais-weekend | domaine-yvon-metras, domaine-chignard, domaine-lafarge-vial, domaine-jean-marc-burgaud, chateau-du-moulin-a-vent, maison-louis-jadot-beaujolais, domaine-terres-dorees |
| harvest-week-cellar-pilgrimage-september | domaine-marcel-lapierre, domaine-jean-foillard, domaine-yvon-metras, domaine-chignard, chateau-du-moulin-a-vent, chateau-thivin, domaine-guy-breton, domaine-jean-paul-thevenet, domaine-georges-duboeuf |
| pierres-dorees-golden-stone-weekend | domaine-terres-dorees, domaine-des-nugues |

---

## Section A — Classification accuracy: PASS

Sampled 35 cuvées + 20 vineyards. All classifications use correct AOC nomenclature:
- No DOCG/DOC/IGT appearing on French wines
- No "Côte du Py AOC" — correctly labeled "Morgon AOC" with Côte du Py as lieu-dit
- No "Premier Cru" or "Grand Cru" — Beaujolais has no such official designations
- Beaujolais-Villages correct; Beaujolais Blanc AOC correct; Coteaux Bourguignons not misused
- All 10 Crus use their standalone AOC name (Morgon AOC, Fleurie AOC, etc.)

## Section B — Hectarage: PASS

Agent A correctly omitted all hectares fields as unverifiable. No hectarage claims present.

## Section C — Scores: PASS

All `scores[]` arrays empty across 152 cuvées. No prose score claims. `check_score_claims.py` reports clean.

## Section D — Ownership: PASS (after cross-contamination fix above)

All 59 vineyard `owner` fields null except Chateau Thivin (`Famille Geoffray` — verifiable, correct per brief). All `winemaker` fields null. Descriptions for Chateau des Jacques, Chateau de la Chaize, Chateau du Moulin-à-Vent correctly attribute owners in prose without mis-using the owner field. Christophe Pacalet correctly identified as Marcel Lapierre's nephew throughout. Foillard family attribution reviewed — no specific attribution of 2022+ vintages to Jean alone.

## Section F — Address cross-check: PASS

12 entities sampled across wine-restaurants, wine-hotels, wine-bars. All have street-level addresses with street numbers, fuzzy-matching address_quoted. No bare town-level addresses detected in the sample. All open_status values are valid enum members.

## Section I — Taste-note evidence: PASS (no shared-URL fabrication)

153 cuisine_evidence_urls across 152 wines (1 shared 2×). No URL shared by 3+ wines. The Rioja/Wachau shared-URL fabrication pattern does not apply here.

## Section J — Tag vocabulary: PASS

All tags in wines.json validated against WINE_TAGS.md. No unknown or derived-axis tags found.

## Section K — Vintage-agnostic slugs: FIXED (lapierre-mmxx removed)

No numeric year digits in any slug. One Roman-numeral vintage cuvée removed.

---

## Post-fix ship_safety outcome

```
france/beaujolais: ALL CHECKS PASSED
0 HARD   |   WARN: SEO title lengths + description char-count (pre-existing, non-blocking)
```

---

## Notes for QA2

1. **foillard-morgon-eponym taste block is empty** — `taste.summary` was blank in the research output. QA2 should verify if taste descriptors exist or if the block should remain absent.
2. **Yvon Métras visitor access** — three dietary/hidden-gems entries say `open_status: unknown`. This is intentional (no walk-in visits). QA2 confirm these are accurate.
3. **Section I deeper dive** — several wines cite `beaujolais.com/en/domain/<slug>` as cuisine_evidence_url. These are appellation-directory pages, not per-cuvée tech sheets. QA2 should anchor any taste blocks citing directory pages to per-wine pages or strip the taste block. This was not a QA1 scope item (taste block section I was not assigned to QA1) but should be flagged.
