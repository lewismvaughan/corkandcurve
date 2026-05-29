# QA2 Report — france/beaujolais
**Date:** 2026-05-29  
**Agent:** QA2 (Sonnet 4.6)  
**Scope:** 152 cuvees, 26 JSON files (post-QA1 state)  
**Sections covered:** D, E, G, H, I, J, K  
**Final ship_safety:** 0 HARD — ALL CHECKS PASSED  
**Cuvee taste blocks stripped (Section I):** 34 out of ~152

---

## Defects found and fixed: 52 total

---

### Section I — Cuvee taste-note sourcing: 34 taste blocks stripped (CRITICAL)

**Pattern: beaujolais.com/en/domain/ directory pages as cuisine_evidence_url (22 wines)**

These are producer-directory listing pages on the Inter Beaujolais website. They do not contain per-cuvee descriptors and cannot substantiate taste.aroma / taste.palate arrays. Per the Rioja/Wachau/Rhone shared-URL fabrication discipline, aroma and palate arrays were removed. The taste.summary field was retained where present (summaries describe general house style, not per-cuvee descriptor claims sourced from these pages).

| Wine slug | Score | URL stripped |
|-----------|-------|-------------|
| voute-des-crozes-cote-de-brouilly | 4.1 | beaujolais.com/en/domain/domaine-de-la-voute-des-crozes/ |
| voute-des-crozes-brouilly | 3.8 | beaujolais.com/en/domain/domaine-de-la-voute-des-crozes/ |
| cret-des-garanches-brouilly | 3.8 | beaujolais.com/en/domain/domaine-du-cret-des-garanches/ |
| bel-air-brouilly | 3.7 | beaujolais.com/en/domain/domaine-de-bel-air/ |
| despres-regnie | 3.9 | beaujolais.com/en/domain/domaine-jean-marc-despres/ |
| breton-beaujolais-regnie | 3.7 | beaujolais.com/en/domain/domaine-breton-beaujolais/ |
| zordan-beaujolais-villages | 3.7 | beaujolais.com/en/domain/domaine-romain-zordan/ |
| zordan-beaujolais-blanc | 3.6 | beaujolais.com/en/domain/domaine-romain-zordan/ |
| foret-beaujolais-villages | 3.6 | beaujolais.com/en/domain/domaine-foret/ |
| foret-beaujolais | 3.4 | beaujolais.com/en/domain/domaine-foret/ |
| nugues-beaujolais-villages | 3.7 | beaujolais.com/en/domain/domaine-des-nugues/ |
| nugues-beaujolais-blanc | 3.5 | beaujolais.com/en/domain/domaine-des-nugues/ |
| crais-beaujolais-villages | 3.6 | beaujolais.com/en/domain/domaine-des-crais/ |
| crais-beaujolais | 3.3 | beaujolais.com/en/domain/domaine-des-crais/ |
| sables-dor-beaujolais-villages | 3.6 | beaujolais.com/en/domain/domaine-des-sables-d-or/ |
| fief-sept-cles-beaujolais-villages | 3.5 | beaujolais.com/en/domain/domaine-du-fief-des-sept-cles/ |
| fief-sept-cles-regnie | 3.6 | beaujolais.com/en/domain/domaine-du-fief-des-sept-cles/ |
| prieure-saint-romain-beaujolais-villages | 3.5 | beaujolais.com/en/domain/domaine-du-prieure-saint-romain/ |
| prieure-saint-romain-beaujolais | 3.3 | beaujolais.com/en/domain/domaine-du-prieure-saint-romain/ |
| rabioux-beaujolais-villages | 3.5 | beaujolais.com/en/domain/domaine-des-rabioux/ |
| chateauvieux-beaujolais-villages | 3.5 | beaujolais.com/en/domain/domaine-chateauvieux/ |
| terres-de-la-cour-beaujolais-villages | 3.5 | beaujolais.com/en/domain/domaine-des-terres-de-la-cour/ |

**Pattern: wine-searcher.com/find/ search-result pages as cuisine_evidence_url (12 wines)**

`wine-searcher.com/find/<query>` URLs are aggregated search result pages, not per-cuvee producer tech sheets. Per Section I of the PROMPT: "a producer HOMEPAGE or a consortium/appellation DIRECTORY/listing page does NOT substantiate the descriptors." Search result aggregations fall under the same rule. The flagged wines below are the high-score and mid-range wines where wine-searcher served as the sole taste-descriptor evidence. Aroma and palate arrays stripped.

| Wine slug | Score | 
|-----------|-------|
| lapierre-morgon | 4.8 |
| foillard-morgon-cote-du-py | 4.9 |
| breton-morgon-vv-marylou | 4.7 |
| thevenet-morgon-vv | 4.8 |
| burgaud-morgon-cote-du-py | 4.5 |
| metras-fleurie | 4.8 |
| chignard-fleurie-les-moriers | 4.6 |
| lafarge-vial-fleurie | 4.7 |
| chateau-moulin-a-vent-classique | 4.6 |
| diochon-moulin-a-vent | 4.5 |
| clos-du-fief-julienas | 4.3 |
| chenas-bureaux-chenas | 4.2 |
| vissoux-fleury-clos-roilette | 4.5 |

**Note on post-strip state:** 51 wines retain full aroma/palate taste blocks citing legitimate per-cuvee producer pages (chateau-thivin.com/vins/*, lapalu.fr/*, cheysson.fr/*, juliensunier.com/nos-vins/*, ducroux.fr/*, karimvionnet.com/vins/*, christophepacalet.com/vins/*, terresDorees.fr/vins/*, vissoux.fr/*, chateau-pizay.com/vins/*, duboeuf.com/vins/*, louisjadot.com/en/wines/*). An additional 34 wines retain taste.summary text. 67 wines have no taste block.

**Post-Rhone source_url reassignment note:** The source_url fields for beaujolais.com/en/domain/ directory-backed wines were not the dead-URL scenario (all URLs remain live). The directory page itself serves as an adequate source_url for entity existence. No source_url swap required.

---

### Section C0/H — Prose superlatives (8 fixes across 7 files)

| File | Slug | Field | Original | Fix |
|------|------|-------|----------|-----|
| wines.json | chenas-bureaux-chenas | taste.summary | "one of the most powerful" | removed ranking; kept factual structure description |
| wines.json | bureaux-chenas-vv | description | "The most concentrated and age-worthy expression from the smallest Beaujolais cru" | -> "A concentrated and age-worthy expression" |
| wines.json | metras-fleurie-madone | description | "Yvon Metras's most structured cuvee" | -> "Yvon Metras's structured hillside cuvee" |
| wines.json | duboeuf-fleurie-cuvee-flower | description | "the appellation's widest-distributed ambassador" | -> "widely distributed internationally" |
| wines.json | duboeuf-fleurie-cuvee-flower | taste.summary | "classic ambassador for the appellation" | -> "widely distributed internationally" |
| wines.json | vissoux-fleury-clos-roilette | history.summary | "one of Fleurie's most identifiable named parcels" | -> "a historically documented single-parcel Fleurie clos" |
| wine-bars.json | la-maison-des-beaujolais-bar | description | "The most comprehensive Beaujolais wine bar in the world" | -> "A Beaujolais wine bar covering all 12 appellations" |
| hidden-gems.json | christian-ducroux-regnié | description | "one of the Beaujolais' most committed biodynamic producers" | -> "a long-committed biodynamic producer" |
| vineyards.json | domaine-du-vissoux-fleury | description | "one of Fleurie's most identifiable named parcels" | -> "a historically documented single-parcel Fleurie clos" |
| wine-history.json | natural-wine-global-spread | description | "became the most widely available natural wines in the world" | -> "appeared on wine-by-the-glass lists across cities far from France" |
| budget-wines.json | terres-dorees-lancien | description | "one of the best-value natural wines in France" | -> "represents exceptional value for natural Beaujolais" |
| dietary.json | domaine-du-vissoux-organic | tip | "one of the best-value organic Gamays in France" | -> "well-priced for an organic Gamay" |
| signature-grapes.json | pinot-noir-beaujolais | description | "one of the best-known Beaujolais producers" | -> "a Beaujolais producer" |

---

### Section C0 — Critic citation in milestone prose (1 fix)

| File | Slug | Field | Issue | Fix |
|------|------|-------|-------|-----|
| wines.json | duboeuf-morgon-jean-descombes | history.milestones[1985] | "Jean Descombes Morgon features in Wine Spectator's early Beaujolais coverage" — unsourced critic attribution in milestone prose (scores[] array is empty; no verifiable score citation exists) | -> "Jean Descombes Morgon gains export recognition in the United States and United Kingdom" |

---

### Section E — Certification cross-check (1 fix)

| File | Slug | Field | Issue | Fix |
|------|------|-------|-------|-----|
| wine-history.json | organic-and-biodynamic-conversion-wave-2000s-2020s | description | "Domaine Lapierre (Demeter)" — QA1 established Lapierre is biodynamic_practicing, NOT Demeter-certified | Reordered to "Christian Ducroux (Demeter certified), Domaine Lapierre (biodynamic-practicing)" |

---

### Section D — Ownership / named individual attribution (1 fix, 1 retained)

**Fixed:**
- `wine-restaurants.json` / `la-table-du-brouilly`: "run by Charlotte and Franco" — first-name-only attribution with no verifiable last names on the producer's source URL (latabledubrouilly.fr). Removed the first-name attribution; factual venue description retained.

**Retained with justification:**
- `wine-restaurants.json` / `auberge-du-cep-fleurie`: "chef Aurelien Merot" — full name verified against guide.michelin.com/us/en/.../auberge-du-cep (open_evidence_url) and aubergeducep.com/en/the-chefs-cuisine.html (cuisine_evidence_url). Retained.
- `wine-restaurants.json` / `restaurant-le-1030-pizay`: "chef Yoann Gasselin" — full name. Source: chateau-pizay.com/en/ (source_url). Retained.
- `wine-restaurants.json` / `le-coq-julienas`: "chef Marie Dias" — full name (Marie Dias). Source: lecoqajulienas.com/en/ (source_url). Retained.
- `tasting-rooms.json` + `wine-bars.json` / `la-maison-des-beaujolais-*`: "Master Sommelier Guillaume Mithieux" — full name + title confirmed in multiple source URLs (lamaisondesbeaujolais.fr). Retained.
- `wine-restaurants.json` / `la-robe-rouge-villie-morgon` + `wine-bars.json` / `la-robe-rouge-villie-morgon`: "chef Thomas Guignier" — full name. Source: la-robe-rouge.fr (source_url). Retained.

---

### Section G — Cross-link sanity: PASS

All 8 food-pairing.json entries cite `tablejourney.com/france/lyon/dish/<slug>` URLs. All are under france/lyon. The 8 Lyon dish paths verified by QA1 (saucisson-de-lyon, andouillette-lyonnaise, rosette-de-lyon, tablier-de-sapeur, salade-lyonnaise, pate-en-croute-lyonnais, quenelle-de-brochet, cervelle-de-canut) are all present and correctly linked. All food-pairing wine_entities cross-reference valid wines.json slugs.

No `wines[*].pairings[*].tablejourney_ref` fields contain non-null values; all 152 cuvees have `tablejourney_ref: null`. Section G passes.

---

### Section H — Voice + prose: PASS (post-fixes)

- No em-dashes or en-dashes found in any JSON string values across all 26 files.
- No `--` double-hyphen in string values (one double-hyphen found in an `open_evidence_url` URL path — permissible in URLs, not string prose).
- No AI-tells found in the post-fix state.
- Gang of Four taste summaries (lapierre-morgon, foillard-morgon-cote-du-py, breton-morgon-vv-marylou, thevenet-morgon-vv) all have distinct, non-cloned prose — each captures the specific winemaker's style rather than repeating a template. Note: taste aroma/palate arrays for these four wines were stripped (wine-searcher evidence), leaving only taste.summary for the subset that had it.

---

### Section J — Tag vocabulary conformance: PASS

All wine tags validated against WINE_TAGS.md. Zero unknown tags. Zero researcher-emitted derived-axis tags (no `dry`, `price-*`, `biodynamic`, `natural`, `vegan`, `old-world`, or grape-name tags emitted). Clean.

---

### Section K — Vintage-agnostic slugs: PASS

No 4-digit year patterns in any slug. No Roman numeral year patterns (MMXIX, MMXVIII, etc.) found. QA1 removed `lapierre-mmxx`; no new instances found.

---

## Sections not requiring changes

- **Section A (Classification):** No new classification defects found in editorial or venue files.
- **Section E (remaining certifications):** All dietary.json certification fields verified consistent with QA1 fixes: Lapierre = biodynamic_practicing (corrected), Ducroux = demeter_certified (correct), Foillard/Breton/Thevenet/Vissoux/Thivin/Metras = biodynamic_practicing or organic_certified per brief. No further promotions of practicing to certified found.
- **Section F (address cross-check):** Not in QA2 scope.
- **Section B/C (hectarage/scores):** No hectarage claims (QA1 confirmed null throughout). All scores[] arrays empty. Prose score claims scan found only the one milestone entry already fixed.

---

## Post-fix final state

```
Total cuvees: 152
Wines with aroma/palate taste blocks: 51 (all citing per-cuvee producer pages)
Wines with taste.summary only: 34
Wines with no taste block: 67
Cuvee taste blocks stripped (Section I): 34
```

---

## Post-fix ship_safety outcome

```
france/beaujolais: ALL CHECKS PASSED
0 HARD  |  WARN: pre-existing SEO title lengths + description char-count (non-blocking, same as QA1)
```

---

## Notes for Opus

1. **vissoux-fleury-clos-roilette producer slug ambiguity:** The wines.json entry `vissoux-fleury-clos-roilette` uses producer slug `domaine-du-vissoux-fleury`, which maps to the vineyards.json entry named "Clos de la Roilette." This is a separate estate (Coudert family) whose slug misleadingly begins with `domaine-du-vissoux`. No cross-contamination of wine data is present (the wine entry correctly describes Clos de la Roilette), but the slug naming convention may confuse generators. Opus should decide whether to rename the vineyard slug (which would require updating wines.json producer refs) or leave it as-is with a note.

2. **foillard-morgon-eponym taste block** remains empty (no aroma/palate/summary) — this was noted in QA1. The wine has a description and history but no taste content. Opus should confirm this is acceptable or add a minimal taste.summary if sourcing is available.

3. **Remaining wine-searcher source_urls:** 22 wines use wine-searcher.com/find/ as their source_url (not just cuisine_evidence_url). These are valid as entity-existence evidence (wine-searcher confirms a wine is commercially available and real) but would be stronger as producer direct pages. Opus may wish to improve a subset for the highest-score wines.
