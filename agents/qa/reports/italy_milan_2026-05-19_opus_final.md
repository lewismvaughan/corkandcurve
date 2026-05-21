# QA report -- Milan (Opus final, 4th-stage pass)

Date: 2026-05-19
Scope: italy/milan -- final Opus validation after QA1 + QA2 PASS verdicts.
Inputs reviewed: agents/qa/reports/italy_milan_2026-05-19.md (QA1), agents/qa/reports/italy_milan_2026-05-19_pass2.md (QA2), agents/qa/PROMPT.md.

---

## Carry-forward from QA1 + QA2

- QA1 fixes: eating-europe-milan route/price/duration/meeting-point; 2 Mercato di Wagner prose echoes.
- QA2 removals: viator-milan-food-tour, get-your-guide-milan-market, know-milan-panettone (3 aggregator tours); erba-brusca pulled from dietary/vegan.
- After QA2, residual below-floor topics: food-tours (1), vegan (2), vegetarian (2), gluten_free (2), halal (2), kosher (1).

---

## What this Opus pass did

Four targeted checks per task scope:

1. Below-floor decisioning (food-tours + 5 dietary subcategories).
2. Spot-check of 10 random entities QA1+QA2 did not sample.
3. Prose echo grep for QA1+QA2 removed slugs.
4. Production smoke test on 3 representative live URLs.

---

## 1. Below-floor decisions

### food-tours (1 of 4)

- **eating-europe-milan**: VERIFIED. Direct fetch of eatingeurope.com/milan/ confirms "Eating Milan: Navigli Food and Drinks Tour" at 3.5 hours, from EUR 97, 5 stops, risotto alla milanese, tiramisu, polenta with gorgonzola, Italian wine. JSON matches confirmed tour. SHIP.
- Result: 1 entry retained. Below floor (4), flagged for research backfill.

### dietary -- alternative evidence sweep + decisive ship-or-remove

Strategy per task: find ONE alternative evidence source for each remaining entry (happycow/zabihah/shamash/atly fallback); if no working source confirms the dietary claim, REMOVE. Do not ship cuisine_unverified.

Findings forced both cuisine and address-fabrication removals:

**Vegan (was 2, now 1):**
- **joia-vegan**: CONFIRMED via joia.it own site -- "alta cucina vegetariana" with "interamente vegetale" (fully plant-based) tasting menu explicit. Address Via Panfilo Castaldi 18 confirmed via Michelin Guide, Yelp, multiple sources. SHIP.
- **flower-burger-milan**: REMOVED. Address fabrication. JSON address "Via Bezzecca 5, 20135 Milano, porta-romana" does not exist. flowerburger.it locations page lists Milan stores at Viale Vittorio Veneto, Corso Garibaldi, Via Russolo (Santa Giulia), Via Tortona, Viale Sarca/Bicocca -- none on Via Bezzecca. The brand is real and plant-based; this individual entry is fabricated.

**Vegetarian (was 2, now 1):**
- **joia-vegetarian**: CONFIRMED via joia.it own site (Michelin-starred vegetarian since 1989). SHIP.
- **larte-vegetarian**: REMOVED. Address fabrication. JSON places L'Arte at "Via Manzoni 5". The Armani Milan restaurant lineup (locations.armani.com, michelin.guide, Yelp, TheFork, OpenTable) does not include a restaurant called "L'Arte". Armani's Milan restaurants are Armani/Ristorante (Via Manzoni 31), Armani/Bamboo Bar, Emporio Armani Caffe & Ristorante, Nobu Milano. No L'Arte at Manzoni 5.

**Gluten-free (was 2, now 1):**
- **joia-gf**: CONFIRMED via joia.it own site ("senza glutine" explicit accommodation on tasting menu). SHIP.
- **pane-e-acqua-gf**: REMOVED. Multiple defects. (a) Address fabrication: real Pane e Acqua is at Via Matteo Bandello 14, 20123 Milano (per milanotoday.it, identitagolose.it, restaurantguru.com), NOT Via Piranesi 10. (b) Cuisine mismatch: real Pane e Acqua serves Piedmontese cuisine (scallops, daily fish catch, farmhouse rabbit), not a "dedicated gluten-free bakery and restaurant". (c) Foursquare reports the venue closed.

**Halal (was 2, now 0):**
- **al-basha-halal**: REMOVED. Address fabrication. JSON places "Al Basha" at Via Padova 8. The real halal Lebanese/kebab venue is "El Basha" at Via Padova 149 (per ordina-online-ristoranti.it, eatscanner.com, deliveroo.it, sluurpy.it, italiarecensioni.com). Name spelling is wrong (Al vs El) and address number is off by 141.
- **istanbul-halal**: REMOVED. Address fabrication. JSON places "Istanbul Kebab" at Via Sarpi 48 (Chinatown). Real Istanbul Kebab(p) restaurants in Milan are at Via Vitruvio 30 (Zone 2) and Via Foppa 58 (Zone 6). The Via Sarpi area kebab option is "Kebhouze - Sarpi" at #53, a different operator entirely.

**Kosher (was 1, now 0):**
- **siloam-kosher**: REMOVED. Likely fabrication. The Chabad House of Milan's authoritative kosher restaurant directory lists 5 venues -- Ba'Ghetto (Via Sardegna 45), Denzel (Via Washington 9), My Kafe (Via Soderini 44), Carmel by Lolita (Viale San Gimignano 10), Snubar (Via Washington 13). No "Siloam" anywhere. Yelp and milanotoday's "best Jewish restaurants of Milan" listings do not mention Siloam either. The Via Morozzo della Rocca 1 address returned no online presence for a kosher restaurant of that name.

**Net dietary result:** vegan 1, vegetarian 1, gluten_free 1, halal 0, kosher 0. All three retained entries are Joia (the same restaurant fits all three categories cleanly under one own-site evidence URL).

---

## 2. Spot-check of 10 random entities

Random sample (seed 42) from the 120 entities QA1+QA2 did not sample:

| Slug | Verdict |
| ---- | ------- |
| iyo-aalto (fine-dining) | PASS -- confirmed at Piazza Alvar Aalto via iyo.it |
| el-brellin (street-food) | PASS -- real, address minor formatting quibble (Alzaia Naviglio Grande 14 / Vicolo dei Lavandai corner, JSON only quotes the Vicolo side) |
| taglio-milano (brunch) | REMOVED -- venue permanently closed since May 30, 2022 (Facebook + Foursquare confirmation) |
| mercato-di-isola-gems (hidden-gems) | REMOVED -- address fabrication. Actual Mercato Comunale Isola is at Piazzale Lagosta 7; the open-air Mercato Rionale Isola runs on Via Garigliano/Sebenico/Volturno on Tuesdays + Saturdays. Neither is on Via Carmagnola 4. |
| pavillion-cafeteria (brunch) | REMOVED -- likely fabrication. No "Pavillion Cafeteria" found at Via Quadronno 17 or anywhere in Milan. The Via Quadronno food landmark is Bar Quadronno at #34 (panini), not a brunch cafeteria. |
| ugo-bar (bars) | PASS -- real cocktail bar, JSON address #8 vs actual #12 on Via Corsico (minor); confirmed via ugobar.it |
| pave-brunch (brunch) | PASS -- confirmed at Via Felice Casati 27 via pavemilano.com |
| mercato-centrale-milano-market (markets) | PASS -- confirmed at Via Sammartini 2 inside Stazione Centrale |
| marchesi-brunch (brunch) | PASS -- confirmed at Via Santa Maria alla Porta 11/a via tripadvisor + yelp |
| caffe-san-carlo (cafes) | REMOVED -- fabrication. The famous "Caffe San Carlo" at "Piazza San Carlo" is in **Turin**, not Milan. Milan has no notable Piazza San Carlo. The "20100 Milano" postcode in JSON is a generic catch-all (real Milan postcodes are 20121-20162). |

**Spot-check failure rate: 4/10 entities removed.** Plus markets.json had the same Mercato di Isola fabrication mirrored from hidden-gems and was also removed (5th removal triggered by the spot-check finding).

This rate is high enough to suggest the food-research agent had address-hallucination problems on Milan beyond what QA1/QA2 caught. Flagging this in the verdict section.

---

## 3. Editorial-prose echo cleanup

### Removed-slug grep across all 27 Milan JSON files

Slugs removed this pass (in addition to QA1+QA2 removals):
- flower-burger-milan, larte-vegetarian, pane-e-acqua-gf
- al-basha-halal, istanbul-halal, siloam-kosher
- taglio-milano, mercato-di-isola-gems, pavillion-cafeteria, caffe-san-carlo
- mercato-di-isola (from markets.json)

Echoes found and rewritten:

1. **region.json seo.pages.dietary.description**: old description listed "Joia, Soulgreen, Radicetonda, Flower Burger" -- rewrote to refer only to Joia and the three retained dietary subcategories. Also rewrote title to match new state ("Vegan, Vegetarian and Gluten-Free Milan 2026 | TableJourney").
2. **region.json seo.pages.markets.description**: old description listed "Mercato Comunale Wagner, Mercato Comunale Isola, Eataly Smeraldo" -- rewrote to list the 4 actual market entries. Title corrected from "8 Mercati" to "4 Mercati".
3. **region.json seo.pages.food-tours.description**: old description listed "Eating Europe, Devour Tours, Casa Mia, Withlocals" (three of those operators are not in the JSON) -- rewrote to describe only the single Eating Europe tour. Title corrected from "8 Picks to Book" to "Navigli + Eating Europe".
4. **region.json seo.pages.cooking-classes.description + title**: old listed "The Cooking Hub, Cooking Classes in Milan, Casa Mia, Cook in Italy" -- none of those names match the 4 actual entries (Eataly Smeraldo, In cucina con Alice, A Tavola con lo Chef, La Scuola de Gusto). Rewrote to list the real entries. Title corrected from "7 Schools" to "4 Schools".
5. **food-tours.json eating-europe-milan description**: trimmed from 255 chars to 165 chars to clear length-cap WARN.

QA1+QA2 removed slugs (viator-milan-food-tour, get-your-guide-milan-market, know-milan-panettone, erba-brusca in dietary context, eating-europe-milan-corrected) all confirmed absent from prose by direct grep. Mercato di Wagner old-name echo confirmed absent. The four "Pizza al taglio" / "Tagliolini" matches in bakeries/street-food/late-night/restaurants are the dish name, not references to the removed Taglio restaurant -- preserved.

---

## 4. Production smoke test

After regen sequence (`generate_city.py italy milan` + cross_cuts + extras + chrome + sitemap + search_index) and `chmod a+rX` on the host's content tree:

| URL | HTTP | EUR EUR? | Raw tokens? | Placeholders? |
| --- | ---- | --------- | ----------- | -------------- |
| https://tablejourney.com/italy/milan/ | 200 | no | no | no |
| https://tablejourney.com/italy/milan/restaurants/ | 200 | no | no | no |
| https://tablejourney.com/italy/milan/food-tours/ | 200 | no | no | no |

Additional URLs confirmed 200 + clean (dietary, brunch, markets). Price tier rendering confirmed as `€` / `€€` / `€€€` glyph symbols (not "EUR EUR"). Removed-slug grep across served HTML returned zero hits for: pavillion, caffe san carlo, mercato di isola, flower burger, al basha, istanbul kebab, siloam, pane e acqua, l'arte, taglio (excluding "pizza al taglio" dish references).

Validators after edits:
- `scripts/validate_data.py --city milan`: WARN-level only (below-floor SEO depth on 6 topics, expected per scope).
- `scripts/check_internal_references.py --country italy --city milan`: 0 errors, 0 warnings.
- em-dash/en-dash sweep: clean.

---

## Defects total this pass: 11 removals + 5 prose rewrites

Removals:
1. flower-burger-milan (dietary/vegan) -- address fabrication.
2. larte-vegetarian (dietary/vegetarian) -- venue does not exist at JSON address.
3. pane-e-acqua-gf (dietary/gluten_free) -- address fabrication + cuisine mismatch + closed.
4. al-basha-halal (dietary/halal) -- name + address fabrication.
5. istanbul-halal (dietary/halal) -- address fabrication.
6. siloam-kosher (dietary/kosher) -- not found in any kosher directory.
7. taglio-milano (brunch) -- permanently closed May 2022.
8. mercato-di-isola-gems (hidden-gems) -- address fabrication.
9. pavillion-cafeteria (brunch) -- venue not found.
10. caffe-san-carlo (cafes) -- fabrication (Turin venue, not Milan).
11. mercato-di-isola (markets) -- mirror of #8.

Prose rewrites:
1. region.json dietary description + title.
2. region.json markets description + title.
3. region.json food-tours description + title.
4. region.json cooking-classes description + title.
5. food-tours.json eating-europe-milan description (length-cap trim).

---

## Below-floor topics after Opus pass

- food-tours: 1 entry (floor 4) -- eating-europe-milan only.
- dietary/vegan: 1 entry (floor 4) -- joia-vegan.
- dietary/vegetarian: 1 entry (floor 4) -- joia-vegetarian.
- dietary/gluten_free: 1 entry (floor 4) -- joia-gf.
- dietary/halal: 0 entries (floor 4) -- category empty.
- dietary/kosher: 0 entries (floor 4) -- category empty.
- cooking-classes: 4 entries (floor 4 -- at floor).
- hidden-gems: 4 entries.
- brunch: 3 entries.
- markets: 4 entries.
- itineraries: 3 entries.

The dietary page template defaults to "Vegan, vegetarian, gluten-free, halal and kosher options across Milan" intro text. With halal + kosher now empty, that intro slightly oversells; the H2 anchor menu and section bodies correctly show only Vegan / Vegetarian / Gluten-free. Not a P0 blocker; flag for the templates layer (out of QA scope) or a city-level intro override field.

---

## Verdict

**VERDICT: PASS** with significant research-stage flagging.

Rationale: All hard judgment defects this pass are now fixed or removed. The site builds clean, validates with WARNs only, and serves 200 across the spot-checked URLs with no leaked tokens, em-dashes, or removed-slug echoes. The 4/10 spot-check failure rate (40%) and 6/9 dietary-entry removal rate (67%) point to a research-stage address-hallucination problem on Milan that needs a backfill pass before the city can claim dietary, food-tours, brunch, hidden-gems, markets or cooking-classes coverage. The retained entities (Joia x3, the four cooking classes, Eating Europe tour, the spot-checked PASSing entities, plus everything QA1+QA2 cleared in their 15-entity resample) are credible and ship. The dataset is in a defensibly-true state -- the categories below floor are genuinely below floor, not silently padded with fabrications.

VERDICT: PASS
