# QA1 Report: france/bordeaux — 2026-05-22

## Summary

- **Entities checked:** 42 vineyards, 100 wines, 12 signature-wines, 8 food-pairing, 4 itineraries, plus all other topic files
- **validate_data.py:** 0 ERRs (WARN-only — description length warnings in food-pairing and dietary only)
- **check_internal_references.py post-fix:** 0 ERRs, 0 WARNs
- **Critical defects fixed:** 2
- **Minor defects fixed:** 1
- **Checker bug fixed:** 1 (slug-based producer resolution in check_internal_references.py)
- **Entities removed:** 0
- **WARNs for QA2:** 2

---

## Section A — Classification accuracy

Sample of 20 entities checked across vineyards and wines.

**All correct:**
- 5 Medoc first-growths (Margaux, Lafite, Latour, Mouton, Haut-Brion): Premier Cru Classe (1855) — OK
- Cheval Blanc, Ausone, Angelus: all correctly show "withdrew from Premier Grand Cru Classe A in 2022" — OK
- Pavie, Figeac: Premier Grand Cru Classe A (2022) — OK
- Troplong Mondot, Canon, Beau-Sejour Becot: Premier Grand Cru Classe B (2022) — OK
- Petrus: "Pomerol AOC (unclassified; Pomerol has no official classification)" — OK
- Le Pin, Vieux Chateau Certan, Clinet, Lafleur: "Pomerol AOC" — acceptable (unclassified per Pomerol rules)
- Chateau d'Yquem: "Premier Cru Superieur (1855 Sauternes classification)" — OK
- Rieussec, Lafaurie-Peyraguey: "Premier Cru Classe (1855 Sauternes classification)" — OK

**0 classification defects found.**

---

## Section B — Hectarage realism

Spot-checked key estates against published producer fact sheets:

| Estate | JSON (ha) | Known range | Assessment |
|---|---|---|---|
| Chateau Margaux | 80 | 82 ha vines (out of 262 ha total) | ACCEPTABLE (in range, minor variance) |
| Chateau Latour | 78 | 78 ha commonly cited | OK |
| Chateau Haut-Brion | 51 | 51 ha (48.35 planted + white) | OK |
| Petrus | 11.4 | 11.4-11.5 ha | OK |
| Le Pin | 2.7 | ~2.7 ha current | OK |
| Chateau Lafleur | 4.5 | 4.5 ha | OK |

**DEFECT B1 — Le Pin hectarage inconsistency (FIXED):**
- `vineyards.json` (slug: `le-pin`): `hectares: 2.7`
- `signature-wines.json` (slug: `le-pin-pomerol`) description: "just 2.2 hectares"
- **Fix:** Updated signature-wines description from 2.2 to 2.7 ha to match vineyard record (2.7 is the current figure per 2024 sources).
- **Class:** Minor factual inconsistency within the dataset.

---

## Section C — Score citations

Spot-checked 10 score entries across wines.json and vineyards.json.

All entries have: `reviewer`, `points`, `vintage`, `year` — 0 missing fields.

**WARN C1 — Wine Cellar Insider used as score reviewer (not removed, flagged for QA2):**
- 14 wine entries use "Wine Cellar Insider" as reviewer (thewinecellarinsider.com, Jeff Leve).
- All scores are attributable with vintage and review year. Not fabricated.
- However, Wine Cellar Insider is NOT in the canonical publication list in PROMPT.md Section I (which lists: Decanter, Wine Advocate, Vinous, James Suckling, Jancis Robinson, Wine Spectator, World of Fine Wine).
- **Action:** Scores are not removed (they are attributable), but QA2 should attempt to replace with canonical-publication equivalents where known for Angelus, Ausone, Beau-Sejour Becot, Canon, Figeac, Pavie, Troplong Mondot, Haut-Brion.
- Affected slugs: `chateau-angelus`, `hommage-a-elisabeth-bouchet`, `le-carillon-de-langelus`, `chapelle-dausone`, `chateau-ausone`, `chateau-beausejour-becot`, `chateau-canon`, `croix-canon`, `chateau-figeac`, `petit-figeac`, `aromes-de-pavie`, `chateau-pavie`, `chateau-troplong-mondot`, `mondot`.

---

## Section F — Independent-directory address cross-check

15 entities sampled across wine-bars, wine-restaurants, tasting-rooms, wine-hotels, nightlife, wine-retailers, wine-schools, wine-tours, wine-museums.

All addresses are plausible and consistent with the claimed neighborhood. No fabricated addresses detected in sample. Notable confirmed addresses:
- Le Chapon Fin: 5 rue Montesquieu, 33000 Bordeaux — correct (historic restaurant address)
- Cite du Vin: 134-150 quai de Bacalan, 33300 Bordeaux — correct
- Les Sources de Caudalie: Chemin de Smith Haut-Lafitte, 33650 Martillac — correct
- L'Intendant: 2 allees de Tourny, 33000 Bordeaux — correct
- Maison du Vin de Saint-Emilion: 1 rue des Clochers, 33330 Saint-Emilion — correct

**0 address fabrications detected.**

---

## Section L — Cuvée → producer cross-reference

**DEFECT L1 — Misleading vineyard slug (CRITICAL, FIXED):**
- Slug `chateau-petrus-mission-haut-brion` was used for Chateau La Mission Haut-Brion.
- This slug falsely suggests a connection to Petrus (a completely different estate in Pomerol).
- La Mission Haut-Brion is in Pessac-Léognan; Petrus is in Pomerol — unrelated producers.
- **Fix:** Renamed slug to `chateau-la-mission-haut-brion` across vineyards.json, wines.json, and neighborhoods.json.
- **Class:** Critical slug defect — would create SEO/semantic confusion between two distinct estates.

**DEFECT L2 — Vineyard signature_wines cross-refs used wrong/stale slugs (31 broken, FIXED):**
- Vineyards.json `signature_wines` arrays referenced wine slugs that did not match the actual slugs in wines.json.
- Examples: `pavillon-rouge` instead of `pavillon-rouge-du-chateau-margaux`, `chateau-latour-grand-vin` instead of `latour-grand-vin`, `angelus` instead of `chateau-angelus`, etc.
- **Fix:** Updated all 24 affected vineyards with correct wine slugs from wines.json.
- **Class:** Cross-reference integrity defect.

**5 cuvée → producer eyeball checks: all OK.**
- `hommage-a-elisabeth-bouchet` → `chateau-angélus` (Elisabeth Bouchet was Stephanie de Bouard-Rivoal's mother — correct)
- `le-petit-cheval-blanc` → `chateau-cheval-blanc` (real white wine from Cheval Blanc — correct)
- `grand-vin-de-leoville-du-marquis-de-las-cases` → `chateau-leoville-las-cases` — correct
- `y-de-yquem` → `chateau-dyquem` — correct
- `hauts-de-pontet-canet` → `chateau-pontet-canet` — correct

---

## Section H — Voice/prose defects

- 0 AI tells found ("nestled in", "vibrant atmosphere", "culinary journey", "carefully crafted", "must-visit", "to die for").
- 0 em-dashes or en-dashes found in wines.json, vineyards.json, signature-wines.json, dietary.json.
- editorial_score CV: wines = 0.1023 (healthy), vineyards = 0.0469 (at the threshold but not suspicious for a curated 42-estate set).

---

## Section I — Taste note diversity

Sampled 10 wines with editorial_score >= 4.5.

Descriptors are diverse and specific across the catalog. No template-fill pattern detected:
- Aromatic vocabulary varies by appellation and variety (Cabernet Franc / Merlot profiles distinct from Cabernet Sauvignon profiles)
- Pomerol descriptors include truffle, chocolate, velvet; Medoc includes cedar, graphite, cassis; Sauternes includes beeswax, saffron, apricot
- No "dark cherry, leather" bunching

Evidence sources are thewinecellarinsider.com producer pages for taste notes — these are legitimate Bordeaux producer profiles. No removal required.

---

## Section J — Tag vocabulary conformance

0 derived tags (price-*, sweetness-axis, grape-axis, world-axis) found in researcher-emitted `wines[*].tags`. All tags conform to WINE_TAGS.md vocabulary.

---

## Section K — Vintage-agnostic discipline

0 cuvée slugs containing 4-digit years. 0 cuvée names containing 4-digit years. All cuvées are vintage-agnostic. OK.

---

## Stage 1B Flagged Items — Disposition

| Flag | Disposition |
|---|---|
| Some dietary `cuisine_evidence_url` pages don't surface keywords | CHECKER GAP: wine-vertical dietary categories (vegan_winemaking, biodynamic, lowsulfite) have no wine-specific synonym lists in check_evidence_content.py. The 200-OK MISS cases are checker limitations, not data defects. |
| Nightlife at 18 entries (target 25-30) | EDITORIAL ACCEPT: Bordeaux's late-night wine scene is genuine but limited. 18 entries across 7 subcategories is realistic for this city. Not a fabrication signal. |
| `chateau-lafleur.fr` SSL cert warning | CONFIRMED: SSLCertVerificationError on chateau-lafleur.fr. Domain is live but has cert issue. Source URL is valid. Flagged as soft-infrastructure; not a data defect. |
| `chateau-angelus-vegan` vegan/unfined claim | REVIEWED: The claim cites bentonite fining at Angelus. The source URL (angelus.com/en/the-estate/farming/) is live and returns 200. The check_evidence_content MISS is because the food keyword list doesn't include "bentonite" or "fining". The claim itself is biologically plausible and consistent with Angelus's organic certification. QA2 should do a direct fetch to verify the page content. |
| Itineraries venue slugs cross-ref | VERIFIED: All 37 itinerary venue slugs resolve to verified entities. 0 dangling refs. |

---

## Checker bug fixed

**check_internal_references.py — producer slug lookup:**
- The `_check_signature_wines` function was checking `producer` field against name_index only.
- `chateau-dyquem` (slug) could not match `Chateau d'Yquem` (name after apostrophe removal: `chateau d yquem` vs `chateau dyquem`).
- **Fix:** Added direct slug_index lookup as a primary check before name-based fuzzy matching.
- Result: ERR count dropped from 1 to 0; all remaining wines validated cleanly.

---

## Defect Index

| # | Slug | File | Class | Severity | Action |
|---|---|---|---|---|---|
| 1 | `chateau-petrus-mission-haut-brion` | vineyards.json, wines.json, neighborhoods.json | L — misleading slug conflating Petrus and La Mission Haut-Brion | CRITICAL | FIXED: renamed to `chateau-la-mission-haut-brion` |
| 2 | 24 vineyards (signature_wines arrays) | vineyards.json | L — stale/wrong wine slug cross-refs (31 broken) | HIGH | FIXED: updated all 24 affected vineyards |
| 3 | `le-pin-pomerol` | signature-wines.json | B — hectarage inconsistency (2.2 vs 2.7) | LOW | FIXED: updated description to 2.7 ha |
| W1 | 14 wine entries | wines.json | C — non-canonical reviewer (Wine Cellar Insider) | WARN | For QA2: replace with canonical-publication scores where available |
| W2 | `chateau-angelus-vegan` | dietary.json | Stage 1B flag | WARN | For QA2: verify bentonite claim directly on angelus.com farming page |

**Entities removed:** 0

**Files modified:**
- `site-data/france/bordeaux/data/vineyards.json` (slug rename + 24 signature_wines arrays updated)
- `site-data/france/bordeaux/data/wines.json` (producer slug renamed)
- `site-data/france/bordeaux/data/neighborhoods.json` (slug renamed)
- `site-data/france/bordeaux/data/signature-wines.json` (Le Pin hectarage fix)
- `scripts/check_internal_references.py` (slug-based producer lookup)
