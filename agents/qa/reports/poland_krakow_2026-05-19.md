# QA report - Kraków (judgment pass)

Date: 2026-05-19
Scope: 163 entities across 27 JSON files, post-fixup pass.

## Pass-1 carry-forward (verify_entities.py)

- HARD failures pre-QA: 0 (ship_safety baseline clean)
- WARNs: mostly `own_site_only` (multiple inyourpocket-only or happycow-only entries) and several `dead_cuisine_evidence_url` on `culture.pl/en/article/12-of-the-most-iconic-polish-foods` (404). These are non-blocking but should be addressed in a follow-up evidence-URL sweep.
- After my edits: 0 HARD, similar WARN profile (one new tripadvisor own-site warn for Trezo, one new krakow.travel warn for Sukiennice; both replacements for previously-fabricated source_urls).

## Judgment defects found

### A. Cuisine / category mismatches + independent-directory cross-checks

The fixup pass left a substantial trail of WRONG inyourpocket cuisine_evidence_urls that point to BELFAST venues, not Krakow:
- `trzy-rybki` (fine-dining): inyourpocket URL `_27966v` is Madison's Hotel, Belfast - REPLACED with operator site.
- `szara-gesi` (fine-dining + restaurants): inyourpocket `_28069v` is Bridge House (JD Wetherspoons pub), Belfast - REPLACED with operator site.
- `copernicus` (fine-dining): inyourpocket `_28051v` is Kitchen Bar, Belfast - REPLACED with operator site.

### A2. Specific-fact match failures (the bulk of defects)

**Address hallucinations (kept building number, invented street):**
- `trezo` (restaurants): JSON said Świętej Anny 5 Old Town; real address is Miodowa 33 Kazimierz. ADDRESS + NEIGHBORHOOD + booking_url + source_url all CORRECTED.
- `weze-krafta-bar` (bars) + `wezze-krafta-multitap` (breweries): JSON said Józefińska 15 Podgórze; real is Dajwór 16 Kazimierz (Tytano complex). FIXED both files.
- `fiorentina` (restaurants): JSON said Grodzka 65, real is Grodzka 63 (+ wrong ZIP). FIXED.
- `piekarnia-mojego-taty` (bakeries) + `piekarnia-mojego-taty-hidden` (hidden-gems): JSON said Józefa 23; real main location is Karmelicka 68a. FIXED both + source_url switched to eatbu mirror (operator site has SSL failure). Itinerary prose ("on Józefa") also UPDATED.
- `ciastkarnia-vanilla` (bakeries): JSON said Bracka 8; real is Brzozowa 13. FIXED.
- `amarylis-hidden` (hidden-gems): JSON said Piłsudskiego 19; real is Józefa Dietla 60 (Queen Hotel basement); chef Grzegorz Bucki. FIXED.
- `andrus-maczanka` (street-food) + `andrus-budget` (budget-eating): JSON said Sławkowska 19; real food truck is Św. Wawrzyńca 16 (Kazimierz); other branches are Sienna and Mały Rynek. FIXED both.
- `vinosfera` (wine-bars): JSON said Rynek Główny 33; real Winosfera is Plac Szczepański 8. RENAMED + ADDRESS FIXED.

**Fabricated facts in description/tip:**
- `pod-baranem` (casual-dining): "the way Anthony Bourdain ordered them in 2014" - Bourdain never visited Poland for Parts Unknown. REWRITTEN.
- `noworolski` (cafes): "Lenin sat at table 9" - Lenin connection real but "table 9" fabricated specific. REWRITTEN.
- `filipa-18` (fine-dining + restaurants): "six tables / counter-top fine-dining" - actual venue has 50 seats; chef Marcin Sołtys correctly identified (fortnightly menu confirmed). PROSE CORRECTED.
- `szara-gesi` (fine-dining + restaurants): "autumn roast-goose tradition every November" - not on operator site as a tradition. SOFTENED to "seasonal goose feature".
- `morskie-oko` (casual-dining): "Folk music every evening from 18:00" - operator only confirms "live singing" with no schedule. TIP SOFTENED.
- `chimera` (casual-dining + dietary.vegetarian): "since 1992" + "40-strong salads" + "two floors basement" - all unsupported. REWRITTEN as covered-courtyard salad bar.
- `polakowski` (casual-dining + budget-eating): "Two locations; Sukiennice branch on the Rynek" - operator only lists Miodowa. ECHO REMOVED.
- `pod-norenami` (restaurants + dietary.vegan): "Two locations: Krupnicza and Meiselsa" - operator only has Krupnicza per search. ECHO REMOVED + gluten-free entry's Meiselsa address corrected to Krupnicza.
- `wesele` (restaurants): "15 zl terrace seat fee in summer" - not on operator site. REMOVED.
- `starka-wine-cellar` (wine-bars): "Cellar-aged vodka in 8, 12, and 25-year vintages" - operator menu only confirms Starka 25yo. CORRECTED.
- `klezmer-hois` (restaurants): "19th-century mikveh" - Great Mikveh built ~1567 (16th c) with 19th-c renovation. CORRECTED to 16th-century.
- `stary-kleparz` (markets): "since 1798" - real market founded mid-14th century. CORRECTED.

**Wrong hours/days:**
- `milkbar-tomasza` (casual-dining + brunch + budget-eating): "Closed Sunday" - actually closed Monday per Yelp/cityseeker. FIXED in all three files.
- `mercy-brown` (bars): "Closed Sunday and Monday" - actually closed Monday/Tuesday (Wed-Sat 19:00-02:00, Sun 18:00-23:00). FIXED.

**Wrong taps/numbers:**
- `viva-la-pinta` (bars + breweries): "18 Pinta taps" - real ~14 taps. CORRECTED.
- `wezze-krafta-bar` (bars): "30 Polish craft taps" - real 25 taps. CORRECTED.

**Wrong star count:**
- `bottiglieria-1881` (fine-dining): JSON said stars=1; Bottiglieria has been a 2-star since June 2023 (Poland's first two-star). FIXED.

### B. Route / itinerary mismatches (food-tours + cooking-classes)

- `krakow-cellar-vodka-tour` (food-tours): "Cracow Local Tours vodka cellar tour" - operator real but does NOT offer a vodka tour (Auschwitz/Wieliczka/Zakopane day trips only). REMOVED.
- `tasty-poland-class` (cooking-classes): operator real but based in GDAŃSK, not Kraków - REMOVED. cooking-classes now empty (was already at floor of 1; needs research backfill).
- `eat-polska-krakow-food-tour`: corrected price (399 zl not 375), tastings (10+ not 6), schedule (daily 13:00 not Tue-Sat 11:00/17:00), group size (2-8 not 12).
- `eat-polska-vodka-tour`: corrected duration (3.5 hrs not 3), price (420 zl not 295), schedule (daily 17:00 not Wed-Sat 18:00), vodkas (6-7 not 6).
- `secret-food-tours-krakow`: corrected stops (6 not 8), group max (10 not "small groups of 10").
- `delicious-poland-jewish-tour`: tour exists per blog but operator main product page lists 4 different tours; softened tip to require operator contact.

### C. Festival month / dates corrections

- `soup-festival` (festivals): JSON said October at Plac Wolnica - actual is end of MAY at Plac NOWY (per pl.wikipedia.org/wiki/Festiwal_Zupy). MONTH + LOCATION + start_day/end_day all CORRECTED. Seasonal-food.json's "autumn" prose also CORRECTED to remove Soup Festival; spring prose UPDATED to include it.
- `wine-festival-krakow` (festivals): JSON said October at ICE Kraków Congress Centre; real ENOEXPO is NOVEMBER 4-6 at EXPO Krakow (Galicyjska 9). RENAMED to ENOEXPO, MONTH + ADDRESS + dates CORRECTED; noted B2B nature.
- `jewish-culture-festival`: 35th edition is July 1-5, 2026 (5 days), not 10 days. start_day/end_day UPDATED to July 1-5.
- `pierogi-festival`: kept (mid-August Mały Rynek confirmed); removed false "tasting pass" claim (admission is free).

### D. Thin-category fabrications + closures

- `pochlebstwo-bakery` (bakeries) + `pochlebstwo-hidden` (hidden-gems): venue CLOSED per krakowianie.pl ("legendarne Pochlebstwo zamyka swoje drzwi"); fabricated founder "Marcin Czerwiński" (real: Kubacka + Pytlewski); wrong address (Romanowicza Podgórze, not Józefa 38). REMOVED both entries.
- `afera-piekarnia` (bakeries): not found in any independent search; specialty + cinnamon-roll claims unverifiable. REMOVED.
- `cukiernia-noworolski` (bakeries): duplicate of `noworolski` (cafes) at same address; "Polish honey torte" specialty unsupported by sources. REMOVED bakery entry; signature-dishes Sernik krakowski where_to_eat updated from "Cukiernia Noworolski" to "Noworolski".
- `wino-i-przyjaciele` (wine-bars): operator winoiprzyjaciele.pl is an ONLINE WINE SHOP, not a physical wine bar. REMOVED.
- `bottiglieria-1881-wine-bar` (wine-bars): operates as combined fine-dining + wine bar in one room (no separate concept); duplicate of fine-dining entry. REMOVED.
- `winosfera-kazimierz` (wine-bars): there is only ONE Winosfera in Kraków (Plac Szczepański); the "Józefa 22 Kazimierz" branch is fabricated. REMOVED.
- `vis-a-vis-wine-bar` (wine-bars): real venue but it's a general drink bar / cafe-bar from 1978, NOT a Mediterranean wine specialist. REPOSITIONED.
- dietary.kosher's `miodova-kosher`: Miodova is not under rabbinic supervision; not kosher per Chabad Krakow listing. REMOVED from kosher category.

Dietary halal section remains EMPTY (0 entries). Research-stage left it blank; that is acceptable as below-floor rather than fabricated.

### E. Editorial-prose echoes

- `seasonal-food.json` spring: removed "Pochlebstwo" reference (closed) -> "Cafe Camelot".
- `seasonal-food.json` autumn: removed Soup Festival (it's a spring festival) and the "Szara Gęś roasts birds" specific (operator doesn't confirm).
- `food-history.json` Michelin era: fixed "first Michelin star in the 2019 Guide" -> 2020 (real); updated to note 2023 second-star promotion.
- `itineraries.json` weekend-classics day 2: "Piekarnia Mojego Taty on Józefa" -> "on Karmelicka" (entity moved).
- `itineraries.json` jewish-quarter-deep-dive day 1: "Klezmer band plays from 20:00" softened (operator doesn't fix the time); day 2 lunch at Miodova: "goose pierogi and cholent" softened (operator menu doesn't confirm these as signatures).
- `signature-dishes.json` Sernik krakowski: "Cukiernia Noworolski" entry removed (was bakery duplicate); replaced with "Noworolski" (cafe entry).
- `restaurants.json` Karakter: neighborhood changed from `stare-miasto` to `kazimierz` (per Michelin/Yelp/Tripadvisor all consistently say Kazimierz/Brzozowa).

### F. Editorial voice / AI-tells

No egregious AI-tells observed beyond the fabrication patterns above (no purple language, no repeated sentence shapes that would warrant flagging on top of length-cap validator).

## Defects total: 35+ entities edited or removed

**Removed (10 entities + 1 bakery duplicate = 11):**
- `tasty-poland-class` (cooking-classes - operator in Gdańsk)
- `krakow-cellar-vodka-tour` (food-tours - operator doesn't run vodka tours)
- `pochlebstwo-bakery` (closed)
- `pochlebstwo-hidden` (closed)
- `afera-piekarnia` (unverifiable)
- `cukiernia-noworolski` (duplicate of cafe Noworolski)
- `wino-i-przyjaciele` (online wine shop, not a bar)
- `bottiglieria-1881-wine-bar` (duplicate of restaurant)
- `winosfera-kazimierz` (fabricated second location)
- `miodova-kosher` (not kosher-certified)

**Edited (24+ entities across 17 files):**
- bottiglieria-1881 (stars 1->2 + description)
- trzy-rybki, szara-gesi (x2), copernicus, filipa-18 (x2) - cuisine_evidence_url + prose
- karakter (neighborhood + prose), pod-aniolami (source_url), wesele (tip)
- pod-norenami (x2 - tip + source_url), miodova (source_url + prose + tip)
- trezo (address + neighborhood + URLs + prose), fiorentina (address + prose)
- klezmer-hois (mikveh century + tip)
- milkbar-tomasza (x3 - hours), morskie-oko (tip), chimera (x2 - prose), polakowski (tip)
- pod-baranem (Bourdain removed), bar-mleczny-pod-temida (tip)
- mercy-brown (tip), viva-la-pinta (x2 - taps), wezze-krafta (x2 - address + prose)
- piekarnia-mojego-taty (x2 - address + source + prose), ciastkarnia-vanilla (address)
- noworolski (description), jama-michalika (description), cheder-cafe (description)
- vinosfera (full rename + address), vis-a-vis-wine-bar (repositioning), starka-wine-cellar (vodka claim)
- soup-festival (month + location + dates), wine-festival-krakow (rename + month + address)
- jewish-culture-festival (dates), pierogi-festival (tip)
- eat-polska x2, secret-food-tours (specifics), delicious-poland (tip)
- amarylis-hidden (address + chef), andrus-maczanka (address + URLs + prose)
- andrus-budget (address), stary-kleparz (founding year)
- targ-pietruszkowy days (Sat + Wed not Sat-only)
- sukiennice-cloth-hall (source_urls), gluten-free pod-norenami (Krupnicza address)

**Prose / echo rewrites: 6 (itineraries x2 days, seasonal-food spring + autumn, food-history Michelin era, signature-dishes sernik)**

## Below-floor topics after QA

- `dietary.halal`: 0 entries (floor 1+; was already 0 - research-stage choice, not new)
- `cooking-classes`: 0 entries (Tasty Poland removal dropped from 1 to 0; needs research backfill)
- `coffee-roasters`: 4 entries (already below the 10 SEO-depth target pre-QA; not changed by this pass)

## Pre-existing issues NOT touched

- Numerous length-cap ERRs on `description` fields 166-175 chars (target 140-165) across most files; these are research-stage drift. The QA contract says length caps are validator territory, not QA judgment. Did NOT trim these.
- `coffee-roasters.json` and `itineraries.json` below the SEO-depth target (4 and 3 respectively). Research-stage gap.
- `signature-dishes.json` two entries missing `make_it_yourself` recipe blocks (Pierogi ruskie, Sernik krakowski). Research-stage gap.
- WARN `own_site_only` flags across ~15 entities (single-domain verified blocks): present pre-QA; not addressed in this pass.
- WARN `dead_cuisine_evidence_url` for the culture.pl 12-iconic-foods article (404); used on ~6 entries; not replaced this pass (not blocking).

## Verdict

VERDICT: NEEDS_FIXES

Rationale: 35+ defects in one judgment pass on a 163-entity city is well above the threshold that signals a research-stage regression. The fixup pass left a trail of wrong inyourpocket URLs (Belfast venues), wrong addresses (kept-building-number-invented-street pattern recurring 8+ times across files), fabricated founder names, fabricated tour offerings, two closed venues still in the dataset, three duplicates posing as separate entities, and structural festival errors (wrong month + wrong square). All edits applied atomically; ship_safety still passes (0 HARD), but the rate suggests Kraków research-stage was the lowest-quality batch in Poland and warrants a Sonnet QA1 follow-up before next ship.
