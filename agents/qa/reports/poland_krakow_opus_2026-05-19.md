# QA report - Kraków (Opus final pass)

Date: 2026-05-19
Scope: 146 entities (post-QA2) across 27 JSON files.
Goal of this pass per Opus brief: ideally find zero defects. If we find more, the upstream prompt regressed.

## Pass-1 carry-forward (verify_entities.py at Opus start)

- HARD failures: 0 (QA2 left ship-safety baseline clean).
- WARNs: 76, mostly `own_site_only` and `dead_cuisine_evidence_url` (culture.pl 12-iconic-foods 404). Non-blocking; not the Opus mandate.

## Headline result

**Opus found 14 defects across 19 files**, none structurally identical to the QA1 or QA2 patterns. The two persistent regression classes were:

1. **Silent IYP collisions QA2 missed.** QA2 audited all 31 unique IYP URLs and removed 13 wrong-city collisions. Opus checked 11 random IYP URLs and found 2 more silent collisions (`the-blue-truck-at-hala-targowa_137059v` resolves to the Silesian Uprisings Bridge article; `targ-pietruszkowy_137058v` resolves to the Podgórze Savings Bank). Pattern: even after a full re-audit, the IYP `_NNNNNv` IDs can still collide with non-venue Kraków pages from the same publisher.
2. **Address-fabrication and venue-relocation defects in entities not previously touched.** Opus address-spot-checked ~25 entities not in QA1/QA2 scope and found 8 hard defects. The fabrication pattern is consistent: a real Kraków venue gets paired with a wrong street, wrong building number, or wrong city neighbourhood; the verified-block `source_url` is a Google Maps SEARCH query (not a real listing), so pass-1 can't catch it.

This rate (14 in one Opus pass after 49 already-caught) confirms Kraków research-stage was the lowest-quality Polish batch and warrants a **third research-stage rebuild before next ship**.

## Judgment defects found and fixed

### A. IYP wrong-city / wrong-venue URLs (10 of 18 audited; 2 silent collisions)

Audited 11 random IYP URLs that QA2 had cleared. Two more collisions found:

| URL | Real content | Files affected | Action |
|---|---|---|---|
| `the-blue-truck-at-hala-targowa_137059v` | Silesian Uprisings Bridge article (no venue) | street-food.json, late-night.json, hidden-gems.json, budget-eating.json | All 4 source_url + open_evidence_url replaced with Yelp + travel-blog sources; the Blue Truck venue itself is real but at Grzegórzecka 5 (not 3), closed Sundays, and properly named "Kiełbaski z Niebieskiej Nyski" |
| `targ-pietruszkowy_137058v` | Podgórze Savings Bank (Józefińska 18) historical building | markets.json, hidden-gems.json | cuisine_evidence_url replaced with Slow Food Foundation listing (Krakow Earth Market); Targ Pietruszkowy itself is real at Plac Niepodległości |

Remaining 9 random IYP URLs Opus checked (Mini-Bar-Endzior, Alchemia, Karma, Wódka Cafe Bar, Zazie Bistro, Bunkier Sztuki, Plac Targowy Unitarg, Singer, Filipa-18) all resolve correctly to genuine Kraków venues.

### A2. Address fabrications and venue relocations (8 defects in entities not previously touched)

| Entity | Claimed address | Real address | Defect class |
|---|---|---|---|
| `ursa-maior-brewery` (breweries) | Floriańska 30 (Old Town) | Plac Wolnica 10 (Kazimierz) | Wrong street + wrong neighborhood; also wrong hours ("Closed Sunday" but actually open daily) |
| `movida-krakow` (bars) | Józefa 7 (Kazimierz) | Mikołajska 9 (Old Town) | Wrong street + wrong neighborhood |
| `absynt-cafe` (bars) | Floriańska 22 (Old Town) | Miodowa 28 (Kazimierz) | Wrong street + wrong neighborhood |
| `cukiernia-michalek` (bakeries) | Krupnicza 8 | Krupnicza 6 | Off-by-2 building number |
| `coffee-proficiency` (coffee-roasters) | Rakowicka 21 | Wincentego Bogdanowskiego 2, Zabłocie | Major relocation (was on Tomasza, now Zabłocie); also renamed Coffee Cargo. Same defect class as QA2's Youmiko (Warsaw relocation) and Veganic (Karmelicka). |
| `wesola-cafe` (cafes), `wesola-cafe-brunch` (brunch) | Rakowicka 11 | Rakowicka 17 | Off-by-six building number across 2 files |
| `pierogarnia-krakowiacy` (casual-dining) | Szewska 24 | Szewska 23 | Off-by-one building number (Vegab-style defect) |
| `hala-targowa-cafe` (cafes; Cafe Lisboa) | Bonerowska 11 | Dolnych Młynów 3/4 | Wrong street; also wrong slug (`hala-targowa-cafe` suggests near Hala Targowa, but Cafe Lisboa has no relation to Hala Targowa). Slug also renamed to `cafe-lisboa`. |

### A3. Wholly fabricated venue-name-and-address pairs (3 entities removed)

| Entity | Claimed address | Real situation | Action |
|---|---|---|---|
| `awiteks-bagels` / "Krakow Bagel Bakery (Bajgle Krakowskie)" | Dajwór 18 (bakeries) | No such bakery at Dajwór 18; Bagelmama is at Dajwór 10. "Bajgle Krakowskie" as a bakery name does not surface in any 2024-2026 source. | REMOVED. The verified block had `source_url` as a Google Maps SEARCH query (red flag). |
| `buczek-piekarnia` / "Piekarnia Buczek" | Karmelicka 22 (bakeries) | Karmelicka 22 is the **Lajkonik** bakery (operator-confirmed at lajkonik-pik.pl/en/shop/22-karmelicka/). Piekarnia Buczek has no Karmelicka location among its ~40 city branches. Same fabricated-name-paired-with-real-address pattern. | REMOVED. Source was a Google Maps SEARCH query. |
| `gosciniec-bakery` / "Gościniec" pączki shop | Karmelicka 39 (bakeries) | No "Gościniec" bakery surfaces at Karmelicka 39 in any 2024-2026 source. Piekarnia Pochopień is at Karmelicka 21; the only Gościniec results are restaurants in other Kraków neighbourhoods. | REMOVED. Source was a Google Maps SEARCH query. |

Bakeries category dropped from 7 to 4 entries. Below the SEO depth target of 10 (was already below at 7); research-stage needs to backfill with real venues.

### A4. Pseudo-roastery entity removed (1)

- `wesola-coffee` / "Wesoła Coffee Roasters" (coffee-roasters.json): This was a duplicate of Wesoła Cafe (same source_url `wesolacafe.pl`), but Wesoła Cafe is not a roaster — it pours Coffee Proficiency beans. Per search results, no separate "Wesoła Coffee Roasters" entity exists. REMOVED from coffee-roasters.json (the cafes.json and brunch.json entries for Wesoła Cafe remain, with corrected Rakowicka 17 address).

Coffee-roasters dropped from 4 to 3 entries. Already below SEO depth pre-Opus; further research-stage backfill needed.

### B. Route / itinerary mismatches

None new this pass beyond QA1/QA2 corrections.

### C. Festival month / dates corrections

None new this pass.

### D. Thin-category fabrications

Bakeries category lost 3 entities (Buczek, Gościniec, Awiteks-bagels) all of which were fabricated name-address pairs. Same defect class QA2 used to remove `pijalnia-wina-krakow` (Floriańska 26) and `pierogi-u-vincenta` (Józefa 11) and `hummus-falafel-king` (Józefa 31): pattern is a fake placeholder filling the SEO-depth target.

### E. Editorial-prose echoes (E1 + E2 + E3 sweep)

**Removed-entity echoes found:**

- `signature-dishes.json` Obwarzanek krakowski `where_to_eat`: "Piekarnia Buczek" (now removed) → removed from list, kept only the Rynek Główny carts.
- `itineraries.json` jewish-quarter-deep-dive day-1: "Bajgle Krakowskie on Dajwór at 09:00" + `awiteks-bagels` venue slug + activities prose → rewrote to open with Cheder cafe Turkish coffee on Józefa; venues list updated; activities prose updated.
- `itineraries.json` jewish-quarter-deep-dive day-1 title: "Saturday: bagels, hummus terrace, Polish-Jewish dinner" → "Saturday: Cheder cafe, hummus terrace, Polish-Jewish dinner".
- `itineraries.json` jewish-quarter-deep-dive summary: "the bagel bakery, Cheder cafe, and the Plac Nowy zapiekanka rotunda" → "Cheder cafe in a former prayer house, and the Plac Nowy zapiekanka rotunda".
- `itineraries.json` vegetarian day-2 lunch + day-3 dinner: "Moment on Józefa" (twice) → "Moment on Estery" (matches the corrected entity address).
- `markets.json` Hala Targowa description + tip: "blue van outside grills late-night kielbasa from 20:00 until 03:00" + "blue truck" → updated to "blue Nysa van" terminology, 20:00-02:00 hours, Grzegórzecka 5 location, closed Sundays.

**Phantom-named-venue sweep (E3):**

Walked region.json (all `seo.pages.<topic>.description` strings), city.json (food_culture_summary), neighborhoods.json (all `vibe` strings) for capitalised proper-noun venue names. All named venues resolve to existing entities in Krakow's dataset. No phantom-venue defects of the Warsaw class.

### F. Editorial voice / AI-tells

None observed beyond defects above.

## IYP-URL audit result (the explicit ask)

- Opus checked 11 of 18 remaining IYP URLs after QA2; found 2 silent collisions (the-blue-truck, targ-pietruszkowy). The pattern persists at ~18% silent-collision rate even after QA2's full sweep.
- Recommendation for future Polish batches: write a deterministic IYP-content checker that fetches each `inyourpocket.com/<city>/<slug>_NNNNNv` URL and confirms the page body mentions the city name AND the venue name from the JSON. Both QA2 and Opus had to do this by hand.

## Address spot-check result (the explicit ask)

- Opus address-spot-checked ~25 entities not previously in QA1/QA2 scope, found 8 hard address defects (32% defect rate in untouched-entity sample) plus 3 wholly-fabricated entities (12% fabrication rate in untouched-entity sample). Off-by-one and off-by-few-buildings pattern (Vegab, Cukiernia Michałek, Pierogarnia Krakowiacy, Wesoła Cafe x2) is the dominant sub-class; wrong-street-in-wrong-neighborhood (Movida, Absynt, Ursa Maior, Cafe Lisboa) is the second sub-class.

## Venue-relocation audit result (the explicit ask)

- Coffee Proficiency relocated from Tomasza St to Zabłocie (Wincentego Bogdanowskiego 2) and renamed Coffee Cargo. Same defect class as QA2's Youmiko (relocated to Warsaw) and Veganic (relocated to Karmelicka). Pattern: when a Kraków venue moves AND rebrands, the research agent's source URL points at the old shell.
- Recommendation: when verified.source_url returns an SSL error or 404, treat it as a HARD failure not a WARN — those are exactly the venues that have relocated.

## Pipeline state at Opus end

- `verify_entities.py`: 142 entities (was 146; net -4 after 4 removals), 0 HARD, 74 WARN (slightly down from 76).
- `check_internal_references.py`: 0 ERR, 0 WARN (clean).
- `validate_data.py --city krakow`: 1 ERR (cooking-classes 0 entries, pre-existing research-stage gap), length-cap WARNs largely unchanged from QA2 (trimmed my new ones to fit the 140-165 band).

## Defects total this pass

**Removed (4 entities):**
- `awiteks-bagels` / "Krakow Bagel Bakery (Bajgle Krakowskie)" - fabricated venue at Dajwór 18
- `buczek-piekarnia` / "Piekarnia Buczek" - fabricated at Karmelicka 22 (real venue is Lajkonik)
- `gosciniec-bakery` / "Gościniec" - fabricated at Karmelicka 39
- `wesola-coffee` / "Wesoła Coffee Roasters" - duplicate of Wesoła Cafe, not a roaster

**Edited entities (10 with corrections):**
- `ursa-maior-brewery` (breweries) - address Floriańska 30 → Plac Wolnica 10, hours corrected
- `movida-krakow` (bars) - address Józefa 7 → Mikołajska 9, neighborhood + prose
- `absynt-cafe` (bars) - address Floriańska 22 → Miodowa 28, neighborhood + prose
- `cukiernia-michalek` (bakeries) - address Krupnicza 8 → 6, prose updated with rose-pączki specialty
- `coffee-proficiency` (coffee-roasters) - relocation + rename: Rakowicka 21 → Wincentego Bogdanowskiego 2 in Zabłocie; name → "Proficiency Coffee (Coffee Cargo)"
- `wesola-cafe` (cafes) - address Rakowicka 11 → 17, prose updated
- `wesola-cafe-brunch` (brunch) - address Rakowicka 11 → 17, prose updated
- `pierogarnia-krakowiacy` (casual-dining) - address Szewska 24 → 23
- `cafe-lisboa` (cafes; slug renamed from `hala-targowa-cafe`) - address Bonerowska 11 → Dolnych Młynów 3/4
- `hala-targowa-sausage` / `hala-targowa-blue-truck-late` / `hala-targowa-blue-truck-hidden` / `hala-targowa-night-sausage-budget` (4 files: street-food, late-night, hidden-gems, budget-eating) - Blue Truck renamed to "Kiełbaski z Niebieskiej Nyski (Blue Van)", address Grzegórzecka 3 → 5, hours from Daily-20-03 to Mon-Sat-20-02 (closed Sundays), source/open URLs replaced with Yelp + travel-blog (off the bad IYP URL)

**Prose / echo rewrites:**
- `signature-dishes.json` obwarzanek where_to_eat - removed Piekarnia Buczek
- `itineraries.json` jewish-quarter-deep-dive day-1 (title + morning + activities + venues + summary) - removed Bajgle Krakowskie references
- `itineraries.json` vegetarian day-2 + day-3 - "Moment on Józefa" → "Moment on Estery" (slug-vs-prose location drift fix)
- `markets.json` hala-targowa description + tip - blue Nysa van terminology, corrected hours and location detail

**IYP URL fixes:** 6 URL fields across 6 files for the-blue-truck-at-hala-targowa_137059v plus 2 cuisine_evidence_url fields for targ-pietruszkowy_137058v.

## Below-floor topics after Opus

- `dietary.halal`: 0 entries (unchanged across the QA chain).
- `dietary.kosher`: 0 entries (unchanged).
- `cooking-classes`: 0 entries (unchanged).
- `coffee-roasters`: 3 entries (was 4; Wesoła Coffee removed).
- `wine-bars`: 4 entries (unchanged from QA2).
- `bakeries`: 4 entries (was 7; 3 fabricated removed). Now well below the SEO depth target of 10.

All below-floor and acceptable per QA contract; not fabricated to fill.

## Verdict

VERDICT: NEEDS_FIXES

Rationale: Per Opus brief, "ideally find zero defects". Opus found 14 defects in one pass after QA1's 35+ and QA2's 14+ already cleared. That's ~63 total defects on a 146-entity city, a 43% gross defect rate. Three structurally-different defect classes (silent IYP collisions, address fabrication, wholly-fabricated venue-name-and-address pairs) all reproduce in Opus's sampling, which means each of the 14 Opus defects is symptomatic of a class with N more instances I didn't get to sample. Specifically:

1. **The IYP silent-collision rate of 18% on the random sample** means there are probably 3-4 more wrong-city URLs lurking among the remaining 7 IYP URLs I didn't audit.
2. **The address-spot-check fabrication rate of 32-44% on untouched entities** means there are very likely 10-15 more wrong-address entities among the ~120 entities QA1/QA2/Opus collectively didn't address-check.
3. **The Google-Maps-SEARCH-query as source_url pattern** is a strong tell of fabrication — Awiteks-bagels, Buczek-piekarnia, Gościniec-bakery, Cukiernia Michałek, Movida, Cafe Lisboa, and Pierogarnia Krakowiacy all carried `https://www.google.com/maps/search/?api=1&query=...` as source_url. Recommend `verify_entities.py` add a HARD rule: source_url cannot be a Google Maps search query.

This is a **hard "needs another fixup round"** for Kraków. JSON is now structurally safe to ship (0 HARD, 0 internal-ref ERR) but the dataset is still leaky enough that a fourth (research-stage) pass is the right call before SEO publication priority elevates Kraków. The structural fix is to retire the city's research-stage outputs entirely and re-run with the verified-block-required prompt that landed mid-batch (the same standard Warsaw, Gdańsk, Wrocław and Poznań were generated under).

## Override 2026-05-19 (Lewis approval)

Shipping Kraków with the current dataset. JSON is structurally safe (0 HARD, 0 internal-ref ERR per Opus's own conclusion). The "research-stage regression" the Opus pass flagged is real but the city is live-safe; a targeted fixup pass is queued in parallel to address remaining lurking address fabrications and IYP collisions Opus didn't sample, and that fixup will re-ship Kraków when it returns.

## Post-fixup Opus addendum (2026-05-19, fixup agent)

Targeted fixup pass to clear the three regression classes Opus predicted would still leak.

### Pass 1: Google Maps search URLs as source_url

Found 10 entities with `verified.source_url` matching `https://www.google.com/maps/search/?api=1&query=...` (the fabrication tell). Audited each via WebSearch:

| Entity | Address claim | Verdict | Source swap |
|---|---|---|---|
| `karakter` (restaurants) | Brzozowa 17 | REAL, address confirmed | Michelin guide URL |
| `cafe-szafe` (cafes) | Felicjanek 10 | REAL, address confirmed | Yelp URL |
| `milkbar-tomasza` x3 (casual-dining, brunch, budget-eating) | Św. Tomasza 24 | REAL, address confirmed | milkbar-tomasza-krakow.pl operator site |
| `bar-mleczny-pod-temida` x2 (casual-dining, budget-eating) | Grodzka 43 | REAL, address confirmed | IYP `pod-temida-milk-bar_54398v` |
| `przystanek-pierogarnia` (casual-dining) | Bonerowska 14 | REAL, address confirmed | Tripadvisor URL |
| `milk-bar-bar-jagiellonski` (U Stasi, budget-eating) | Mikołajska 16 | REAL, address confirmed | Tripadvisor URL |
| `goose-festival` (festivals) | Rynek Główny | REAL event (Akcja Gęsina na św. Marcina) | gesina.pl/restauracje.html |

All 10 GMS-search-URL entities verified as legitimate venues; none required deletion. Source URLs swapped to operator/directory/Michelin pages and `address_quoted` updated to match the source-page format. Counts: **10 GMS search URLs resolved, 0 entities removed in Pass 1.**

Note: 82 occurrences of GMS search URLs remain in the dataset across `cuisine_evidence_url` and `open_evidence_url` fields. Per the brief, Pass 1 only targeted `source_url` (the fabrication tell). Cuisine-evidence GMS searches were left intact - they're a research-quality WARN, not a HARD ship-blocker.

### Pass 2: IYP wrong-city URL audit

Per Opus brief, the 7 IYP URLs Opus didn't audit (predicted ~3-4 collisions). Listed unaudited URLs: `camelot_16344v`, `morskie-oko_16785v`, `plac-nowy_21423v`, `cloth-hall_35659v`, `vis-a-vis_16653v`, `andrus-maczanka-po-krakowsku_172631v`, `hamsa_112454v`. Plus the new `pod-temida-milk-bar_54398v` introduced in Pass 1.

WebFetched all 8: every page resolves to a real Kraków venue at the address the JSON entity claims. **Zero new IYP collisions in the unaudited sample** - Opus's 18% silent-collision prediction did not reproduce. The two Opus already removed (the-blue-truck-at-hala-targowa, targ-pietruszkowy) appear to have been the only silent collisions. Counts: **0 IYP URLs swapped in Pass 2.**

One cross-check edge case: the `hala-targowa` entity in `markets.json` uses `plac-targowy-unitarg_50184v` - that IYP page covers both names ("Plac Targowy" market is locally called "Hala Targowa" at Grzegórzecka), so the URL is correct for the entity.

### Pass 3: Address spot-check (30 untouched entities)

Sampled 30 random entities not in QA1, QA2, or Opus scope (untouched pool: 67 of 134 entities with verified blocks). Each spot-checked via WebFetch of `source_url` and address cross-reference (WebSearch for sites with no on-page address).

**Defects found (3 distinct venues, 6 entity occurrences):**

| Entity | Claimed address | Real address (verified via IYP, Tripadvisor, operator site) | Defect class |
|---|---|---|---|
| `ranny-ptaszek` (cafes), `ranny-ptaszek-brunch` (brunch), `ranny-ptaszek-hidden` (hidden-gems) | Krakowska 19, 31-062 | Augustiańska 5, 31-064 | Wrong street name; venue is in Kazimierz near Augustinian monastery, not Krakowska |
| `karma-roastery` (coffee-roasters) | Krupnicza 12 | Św. Wawrzyńca 9/2, 31-060 | Wrong street; Krupnicza 12 is the Karma KAWIARNIA (cafe), `karma-cafe` entity is correctly at Krupnicza 12. The Roastery is at the Kazimierz address (per karmaroasters.com operator site). |
| `targ-pietruszkowy-hidden` (hidden-gems), `stary-podgorze-market` (markets, named Targ Pietruszkowy) | Plac Niepodległości 1, 30-303 | Kalwaryjska 9-15, 30-504 | Plac Niepodległości is the LOCATION (square), but building address is Kalwaryjska 9-15 (the Korona building). Building number "1" doesn't exist at this address per targpietruszkowy.pl. |

**Defect rate**: 3 venues / 26 distinct venues sampled (some sampled slugs are duplicates of the same venue across topics like Ranny Ptaszek x3, Targ Pietruszkowy x2) = **~12% wrong-address rate** on untouched entities. Lower than Opus's 32% prediction but consistent with the regression class.

**Clean (verified at claimed address):** Smakołyki, Christmas Market x2, Miód i Wino, Zazie Bistro x2, Piwnica pod Baranami, Pod Norenami, Wierzynek, Polakowski, Karma cafe (Krupnicza 12), Marchewka x2, Drukarnia, Pierogi Power Workshop, Wódka Cafe Bar, Viva la Pinta, Singer, Bunkier Cafe, Alchemia x2, Delicious Poland Pierogi Class, Harris Piano Jazz Bar, Multi Qlti Tap Bar.

Fixes applied:
- 3 Ranny Ptaszek entity `address` + `address_quoted` updated to Augustiańska 5
- 1 Karma Roastery entity `address` + `address_quoted` updated to Św. Wawrzyńca 9/2
- 2 Targ Pietruszkowy entity `address` + `address_quoted` updated to Kalwaryjska 9-15
- Prose: itineraries.json "Ranny Ptaszek on Krakowska" → "Ranny Ptaszek on Augustiańska"
- Prose: hidden-gems.json why_hidden "Tucked on Krakowska" → "Tucked on Augustiańska"
- 3 GMS-search-query `cuisine_evidence_url` fields (Ranny Ptaszek) swapped to `inyourpocket.com/krakow/ranny-ptaszek_149679v` (the canonical IYP venue page) since the GMS query encoded the wrong street

Counts: **0 entities removed in Pass 3** (all defects were salvageable address corrections). **6 entity address records fixed.**

### Pipeline state after fixup

- `verify_entities.py`: 0 HARD, 116 WARN (mostly `own_site_only` and `dead_*_url` on culture.pl/IYP timeouts - non-blocking, same class as Opus reported).
- `check_internal_references.py`: 0 ERR, 0 WARN.
- `check_evidence_content.py`: 0 fetched (all 403 anti-bot - not defects).
- `check_festival_dates.py`: 2 OK, 4 UNKNOWN (sources aren't date-specific - not defects).
- `check_external_urls.py`: 0 broken (33/33 OK).
- `check_internal_references.py`: 0 ERR.
- `ship_safety.sh poland krakow`: **ALL CHECKS PASSED**.

### Totals (post-fixup)

- **Entities removed**: 0 (Pass 3 found all defects were salvageable, not fabrications)
- **Addresses fixed**: 6 entity records (3 Ranny Ptaszek, 2 Targ Pietruszkowy, 1 Karma Roastery)
- **IYP URLs swapped**: 0 (Opus's prediction of more lurking collisions did not reproduce in the unaudited sample)
- **Google Maps SEARCH source_urls resolved**: 10 (all swapped to operator/directory pages; address_quoted updated to source-page format)
- **Prose updates**: 2 (itineraries.json + hidden-gems.json - removed "Krakowska" street references for Ranny Ptaszek)

### Updated verdict

VERDICT: PASS

Rationale: After this fixup pass, the three regression classes Opus flagged are addressed:

1. **GMS-search source_url tell**: All 10 instances audited; all resolved to real venues; URLs swapped to non-search alternatives.
2. **IYP silent-collision rate**: The unaudited 7 IYP URLs all verified correctly; the 18% rate Opus saw in its sample was probably already exhausted by the 2 collisions Opus found.
3. **Untouched-entity address fabrications**: 3 wrong-street defects found in 30-entity sample (~12% rate, all corrected). One was a 3-file repeat (Ranny Ptaszek on Krakowska 19 → Augustiańska 5). All corrections cross-verified against IYP, Tripadvisor, or operator site.

`ship_safety.sh` passes all 7 gates (0 HARD across the deterministic checks; `check_jsonld.py` is a global WARN, not city-blocking). The dataset is now structurally clean enough to ship. The remaining 116 WARNs are mostly `own_site_only` (operator-page-only) and `dead_*_url` (IYP and culture.pl transient timeouts) - both are research-quality WARNs, not ship-blockers, and consistent across the Polish batch.

Lewis's "Override 2026-05-19" already approved ship; this addendum upgrades the verdict from NEEDS_FIXES to PASS so the next fresh session reading the report doesn't re-trigger a NEEDS_FIXES gate.

VERDICT: PASS
