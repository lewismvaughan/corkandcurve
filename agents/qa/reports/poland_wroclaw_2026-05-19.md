# QA report -- Wrocław (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety passed pre-QA per task brief)
- verify_entities.py warnings: ~20 `own_site_only` (cuisine_evidence_url and source_url share one domain on a number of street-food, brewery, and Michelin Guide entries; structural, not falsified) + 1 `dead_open_evidence_url` Unicode encoding flake on winogrono (Polish ł in URL). Both classes are out of QA scope; surfaced for research-agent follow-up.

## Spot-check of the Wrocław fixup-agent shortcut (address_quoted = entity.address)

Per the task brief, the previous fixup agent set many `address_quoted` values equal to `entity.address` to satisfy the validator. I spot-checked ten random entities against independent directories (Google search + operator sites + Yelp/TripAdvisor when accessible). Two of the ten checks surfaced address fabrications (see A below). Many others had hours and minor postal-code discrepancies that needed correction.

## Judgment defects found

### A. Cuisine / category mismatches AND address fabrications

**Address fabricated against directory cross-check:**

- `huta-grabiszynska` / `huta-hidden` (markets, hidden-gems): JSON claimed HUTA at "Henryka Pobożnego 7-9, 50-241 Wrocław" in Nadodrze. Independent directory cross-check (wroclawmagazine.com, wroclaw.pl, naszemiasto.pl, dolnyslask.travel) all confirm HUTA at **Grabiszyńska 241, 53-234 Wrocław** (former Hutmen industrial complex, Borek/Grabiszynek area, opened 27 June 2025). Address fully fabricated by the fixup shortcut. Fixed: address, slug, description, source URLs all updated in markets.json and hidden-gems.json. Echo removed from neighborhoods.json Nadodrze vibe ("the HUTA arts complex that opened mid-2025" was false location attribution). The original slug `huta-nadodrze` was renamed to `huta-grabiszynska` to avoid the false neighborhood implication in the URL.

- `niewinnosc` / `niewinnosc-hidden` (wine-bars, hidden-gems): JSON claimed Niewinność Wine Bar at "Świętej Marii Magdaleny 8, 50-103 Wrocław". The source_url (zjedz.my) lists actual address as **Szewska 27/27A lok. 1B, 50-529 Wrocław** (per their own booking page, restaurantguru, cojestgrane, tripadvisor). Address fabricated; the venue is near St. Mary Magdalene Church (hence the "Marii Magdaleny" reference) but the operator's address is on Szewska. Hours were also wrong (JSON said "Tue-Sat 17:00-23:00", actual = Mon-Thu+Sun 16:30-22:00, Fri-Sat 16:30-01:00). Fixed: address, address_quoted, hours, description in both wine-bars.json and hidden-gems.json.

- `el-gato-roasters` (coffee-roasters): JSON claimed "Łokietka 5, 50-243 Wrocław" in Nadodrze. Actual per operator's own contact page and European Coffee Trip: **Odrzańska 8/1, 50-113 Wrocław** (Stare Miasto, not Nadodrze). Hours also wrong (JSON: "Mon-Fri 08:00-18:00", actual: Mon-Thu 08:00-20:00, Fri-Sat 08:00-21:00, Sun 08:00-20:00). Fixed: address, hours, source URLs, and description in coffee-roasters.json.

**Cuisine / specific-fact mismatches:**

- `acquario-monopol` (restaurants): JSON description said "Acquario sits on the first floor of Hotel Monopol". Operator's own page confirms **sixth floor**. Fine-dining.json's `acquario-fd` description already correctly says "sixth floor". Fixed.

- `cookly-pierogi-traditional` (cooking-classes): source_url pointed to a Cookly class actually located in **Warsaw** (Stawki 3, 00-193 Warszawa), not Wrocław. JSON falsely claimed the class is in Wrocław Old Town teaching pierogi + żurek + bigos + Polish breads. Removed entity entirely. cooking-classes now has 4 entries (below floor 4 boundary maintained but `cookly` was the false addition).

**Confirmed clean (section A samples):**

- BABA: Bib Gourmand confirmed; address Nożownicza 1D verified.
- IDA kuchnia i wino: Bib Gourmand confirmed; chef Małgorzata Karkocha-Jakubowska in Hotel Jazz, Łazienna 4 verified.
- Tarasowa: Bib Gourmand 2025 confirmed (operator's own announcement page).
- All 19 "Michelin Selected 2025" claims in restaurants.json (Acquario, CAMPO, dinette, Gustaw, Korill 180, La Maddalena, Lwia Brama, Martim, Mercado, Między Mostami, Młoda Polska, Monopol, Most, Nafta, OK Wine Bar, Przystań & Marina, Warsztat, Wierzbowa 15, Wrocławska) cross-checked against the convention.wroclaw.pl Michelin announcement -- all 19 confirmed.
- STÓŁ na Szwedzkiej: chef Grzegorz Firkowski confirmed; address Szwedzka 17a confirmed. Not in Michelin 2025 list -- JSON doesn't claim Michelin status for STÓŁ.
- Pijalni Wino & Bistro: chef Tomek Wencek with Alkimia/Coure/Dinette experience confirmed via operator's own About page.
- Vega: oldest Polish vegetarian (est. 1987), vegan since 2013 -- confirmed.
- Cocofli: books + art + cafe + wine bar with Polish Lower Silesian wines -- confirmed.
- Konspira: 1980s Solidarity theme, hidden apartment behind a wardrobe -- confirmed.
- Browar Stu Mostów: founded 2014 -- confirmed.
- Restauracja Wrocławska: Szewska 59/60 -- confirmed (est. 1990, JSON says "nearly thirty years" -- close).
- Bistro Narożnik: Rydygiera 30/1B Nadodrze -- confirmed.
- Mariusz Kozak chef of Acquario -- confirmed via WROT page.

### A2. Specific-fact corrections (operator-contradicted or unverified)

- `most-restaurant` description: JSON claimed "Six to nine courses, low-intervention pairings, room for twelve". Operator's own page says only "tasting menu" without course count or seat count. Softened to "an intimate space at the back of the building with low-intervention pairings". Must_order changed from "full nine-course tasting" to "chef's tasting menu". Echoes in itineraries.json (long-weekend summary + day 1 evening) updated.

- `delicious-poland-wroclaw-food-tour`: price was 320 zł (operator's actual price = **385 PLN**); duration was 3.5h (actual 2.5-3h); meeting point was "Wrocław Rynek (Market Square)" (actual = "Small Iglica Fountain at Plac Solny"). All three corrected against operator's page.

- `whistling-hound-polish-food-tour`: price 295 zł was fabricated -- the operator's page explicitly says "The cost of food is not included in the tour charges and may vary depending on the group size" and gives no specific number. Price changed to "Contact operator for current pricing" and tip rewritten to surface the fact that food cost is not included.

- `jarmark-bozonarodzeniowy` (festivals): tip said "Closed December 24-25. Reopens December 26 from 13:00." Actual per wroclaw.pl: closed Dec 24-25 AND Jan 1, New Year's Eve catering booths stay open to 02:00. Tip corrected.

- `restaurantweek-wroclaw` (festivals): must_order specifically named "Book at Młoda Polska, Wrocławska or Lwia Brama; the three-course set is half the usual price." None of these specific restaurants are documented in the source as RestaurantWeek 2025 participants (49 restaurants participate; specific names not verifiable from the source URL). Softened to "Check the official RestaurantWeek line-up the week of release and book the participating Michelin-recognised rooms first."

### B. Route / itinerary mismatches

- `cookly-pierogi-traditional` (cooking-classes): removed (see A above). Route was for a Warsaw class, not Wrocław.

- All other food-tours and cooking-classes verified against operator pages: Delicious Poland (corrected price/duration/meeting), Whistling Hound (price unverifiable, softened), byFood Wrocław private tour (403 anti-bot, listing exists in search results), Viator beer tasting (real platform), Wroclaw Food & Vodka Culture Tours (TripAdvisor real), Discover Wrocław Pierogi class (operator page confirmed bilingual 6-12 group at Rynek glass fountain from €80), byFood Pierogi class (403 anti-bot, real platform), Viator Pierogi & Beer class (real platform), STÓŁ na Szwedzkiej cooking class (operator confirmed). No routes fabricated other than Cookly.

### C. Festival month / dates corrections

- `wroclaw-feta-festival`: JSON claimed start_day 22, end_day 24 (August 22-24). Source page (wroclawguide.com) confirms **August 1-3, 2025** -- three weeks earlier than claimed. start_day fixed to 1, end_day to 3, day_range updated to "First weekend of August, 3 days".

- `gastro-miasto` (July 25-27): verified, correct.
- `festiwal-delicje` (June 6-8): verified, correct.
- `festiwal-pasibrzucha` (June 13-15): verified, correct (already fixed by ship_safety per task brief).
- `restaurantweek-wroclaw` (Oct 7 - Nov 19): verified, correct.
- `beer-geek-madness` (April 25-26): verified, correct.
- `jarmark-bozonarodzeniowy` (Nov 21 - Jan 7): verified, correct (tip-text correction filed under A2).

### D. Thin-category dietary verification

Per task brief: vegan (5), vegetarian (2), gluten_free (2), halal (0), kosher (0). Both halal and kosher are empty by research-agent choice. Below floor of 4 for vegetarian + gluten_free + halal + kosher and below floor for cooking-classes after Cookly removal.

- vegan (5 -> 5): all 5 entries (Vega, Bez Lukru, Warzywniak, CUDO Vegan Sushi, Vegan AF Ramen) cuisine_evidence_url is happycow.net/best-vegan-restaurants/wroclaw-poland -- the canonical dietary directory. Vega independently confirmed by visitwroclaw, wroclawguide, tripadvisor as Poland's oldest vegetarian (est. 1987, vegan since 2013). Pod Przykrywką (vegetarian) and other listings on the happycow source URL corroborate addresses. No fabrications.
- vegetarian (2 -> 2): Pod Przykrywką (Więzienna 18/1) and Talerzyki (Bogusławskiego 34) -- both confirmed against happycow + wroclawguide.
- gluten_free (2 -> 2): Bez Lukru-gf (Igielna 14) and iBO Falafel-gf (Mikołaja 15) -- both confirmed against happycow source. These are not gluten-free-only kitchens; they offer GF options across menu. JSON description for Bez Lukru-gf correctly notes "cross-contamination is controlled but not gluten-free-only kitchen. Verify with staff if coeliac." That phrasing is accurate and not overpromising.
- halal (0): empty by research-agent choice. Not a defect for QA to invent.
- kosher (0): empty by research-agent choice. Not a defect for QA to invent.

### E. Editorial-prose echoes (closed-venue + QA-removed-fact)

**E1. Closed-venue echoes**: No closed-venue removals this round. No echoes.

**E2. QA-removed-fact echoes**: From my Section A and A2 edits, the following echoes were tracked and fixed:

- HUTA in Nadodrze claim: `neighborhoods.json` Nadodrze vibe said "the HUTA arts complex that opened mid-2025" -- rewritten to remove the false location attribution (HUTA is at Grabiszyńska 241, not Nadodrze).
- Most "nine-course" claim: removed from `itineraries.json` long-weekend summary (line 42) and day 1 evening (line 50). Also removed from `fine-dining.json` Most entry description and must_order.
- Zapiekarnik hours echo: street-food.json, late-night.json, budget-eating.json all corrected from "Daily 11:00-23:00" / "Daily 23:00" to actual hours (Tue-Sun starting 13:00, closed Mon, Fri-Sat to midnight).
- Bar Mleczny Mewa "Closed weekends" tip echo: budget-eating.json AND hidden-gems.json both softened (multiple sources actually show weekend hours 09:00-16:00).
- Niewinność address echo: wine-bars.json AND hidden-gems.json both corrected to Szewska 27/27A lok. 1B.

**Itinerary day-of-week x venue-hours cross-check** (per A2 contract):
- `wroclaw-budget-two-days` day 2 (Sunday): JSON sent visitors to **Bar Mleczny Miś on Kuźnicza at 12:30**. Bar Mleczny Miś is **CLOSED Sundays** per operator and three independent sources (inyourpocket, gdziezjescwroclaw, yelp). Swapped to **Bar Mleczny Różowa Krowa** (Świdnicka 36, open 7 days per JSON's own note "useful Sunday when most milk bars close"). Both prose and `venues[]` array updated; `bar-rozowa-krowa` slug is valid in budget-eating.json. Cross-reference checker passes.
- `wroclaw-tasting-menu-long-weekend` day 3 (Sunday): JSON booked **STÓŁ na Szwedzkiej at 19:00**. Operator's own site says Sunday hours are 13:00-21:00 with **last reservation at 18:00**. Booking at 19:00 won't be accepted. Rewrote to 17:30 early dinner so the seat lands before the 18:00 cutoff, and added an explanatory sentence about the Sunday cutoff to help readers.
- All other itinerary venues x day cross-checks pass: Most Thu-Fri 17-22/Sat 14-23 (Friday 19:30 dinner OK, tight close at 22:00 acknowledged); Pijalni Sat 16-23 (Sat 19:30 OK); Lwia Brama Sun 12-22 (Sun 13:00/13:30 OK); Browar Stu Mostów Sun 14-22 (Sun 19:00 OK); Hala Targowa Sat/Fri 08:00-18:30 (09:00/09:30 OK after hours correction).

**Hours corrections (echoes + standalone)**:
- `hala-targowa`: JSON said "Mon-Sat 06:00-18:00, postal 50-156". Actual per operator's own contact page: "Mon-Sat 08:00-18:30, postal 50-158". Hours, postal, and tip text all corrected.
- `charlotte-bakery`: JSON Sunday opening was 09:00. Actual per operator confirmed via Yelp + bistrocharlotte.com: Sun 08:00-22:00. Corrected.
- `winogrono` (Wino.grono): hours "Tue-Sat 16:00-23:00" -- actual per cityon.pl source = closed Mon-Wed, Thu-Fri 17:00-21:00, Sat-Sun 14:00-21:00. Corrected.
- `zapiekarnik` + `zapiekarnik-late` + `zapiekarnik-budget`: "Daily 11:00-23:00" / "Daily 23:00" wrong. Actual per multiple sources = Mon closed, Tue-Sun starts 13:00, Fri-Sat to midnight, Sun-Thu to 22:00. All three echoes corrected.

### F. Editorial voice + length caps

Validator-only WARNs (length caps over a few characters) are pre-existing and out of QA scope. The new HUTA description and hidden-gems why_hidden initially exceeded caps; both tightened post-edit. Validator final pass after all edits: 0 ERR, only the same length-cap WARNs as before (mostly description fields running 165-210 chars vs the 165 soft cap). No purple language, no obvious AI tells, no em/en dashes introduced.

## Entities removed

1. `cookly-pierogi-traditional` (cooking-classes) -- source_url goes to a Warsaw class; venue claimed to be in Wrocław is fabricated. Total: 1 removal.

## Entity edits (non-prose facts changed)

1. `huta-grabiszynska` (markets) -- address, slug rename, hours, vendor count, description, source URLs all corrected.
2. `huta-hidden` (hidden-gems) -- address, why_hidden, tip, source URLs corrected.
3. `niewinnosc` (wine-bars) -- address, address_quoted, hours, description, must_order, tip, signature_pour updated.
4. `niewinnosc-hidden` (hidden-gems) -- address, address_quoted, why_hidden, tip updated.
5. `el-gato-roasters` (coffee-roasters) -- address, hours, beans_from, description, source URLs corrected.
6. `acquario-monopol` (restaurants) -- description corrected from "first floor" to "sixth floor".
7. `most-restaurant` (fine-dining) -- description (six-to-nine-courses + room for twelve removed), must_order, tip updated.
8. `wroclaw-feta-festival` (festivals) -- start_day/end_day/day_range corrected (Aug 22-24 -> Aug 1-3).
9. `jarmark-bozonarodzeniowy` (festivals) -- tip corrected (Jan 1 closure + New Year's Eve hours added).
10. `restaurantweek-wroclaw` (festivals) -- must_order softened (specific restaurant names removed).
11. `delicious-poland-wroclaw-food-tour` (food-tours) -- price, duration, meeting_point, tip corrected.
12. `whistling-hound-polish-food-tour` (food-tours) -- price softened, meeting_point softened, tip rewritten.
13. `hala-targowa` (markets) -- hours, postal, tip, source URLs corrected.
14. `charlotte-bakery` (bakeries) -- Sunday open time corrected.
15. `winogrono` (wine-bars) -- hours corrected.
16. `zapiekarnik` (street-food) -- hours, tip corrected.
17. `zapiekarnik-late` (late-night) -- closes, description, tip corrected.
18. `zapiekarnik-budget` (budget-eating) -- tip corrected.
19. `bar-mleczny-mewa` (budget-eating) -- tip rewritten (false "closed weekends" claim removed).
20. `bar-mleczny-mewa-hidden` (hidden-gems) -- tip softened.

## Entity-prose rewrites (cross-file echoes)

1. `neighborhoods.json` Nadodrze vibe -- HUTA reference removed.
2. `itineraries.json` `wroclaw-tasting-menu-long-weekend` summary + day 1 evening -- Most's "nine-course" generalised to "chef's tasting".
3. `itineraries.json` `wroclaw-tasting-menu-long-weekend` day 3 evening -- STÓŁ booking time moved from 19:00 to 17:30 with explanation of Sunday cutoff.
4. `itineraries.json` `wroclaw-budget-two-days` day 2 -- Bar Mleczny Miś (Sunday-closed) swapped for Bar Mleczny Różowa Krowa; venues array updated; title and prose adjusted.

## Defects total: 23

- 3 address fabrications removed (HUTA, Niewinność, El Gato)
- 1 entity removal for source-mismatch fabrication (Cookly)
- 1 sixth-floor / first-floor correction (Acquario)
- 1 Most course-count softening (operator silent)
- 4 festival/tip date corrections (Feta dates, Jarmark Christmas tip, RestaurantWeek must_order, Most tip)
- 2 food-tour price/duration corrections (Delicious Poland, Whistling Hound)
- 1 market hours + postal correction (Hala Targowa)
- 1 bakery hours correction (Charlotte Sunday)
- 1 wine-bar hours correction (Wino.grono)
- 3 Zapiekarnik hours corrections across files
- 2 Bar Mleczny Mewa tip corrections across files
- 2 itinerary day-of-week defects (Bar Mleczny Miś Sunday-closed, STÓŁ Sunday-cutoff)
- 1 neighborhood-vibe echo (Nadodrze/HUTA)

## Below-floor topics after QA

- dietary/halal: 0 entries (floor 4) -- research-agent choice, not a defect
- dietary/kosher: 0 entries (floor 4) -- research-agent choice
- dietary/vegetarian: 2 entries (floor 4) -- below floor pre-QA
- dietary/gluten_free: 2 entries (floor 4) -- below floor pre-QA
- cooking-classes: 4 entries (floor 4) -- now at floor exactly after Cookly removal; was 5 pre-QA
- itineraries: 3 entries (target 10) -- below SEO floor pre-QA, not a defect

## Flagged for research-agent follow-up

- 20 `own_site_only` verify_entities warnings on street-food, breweries, several Michelin Guide-source-only restaurants, OK Wine Bar, Pijalni, Cocofli, Vertigo, Mleczarnia, Etno -- add an independent-directory URL each (Google Maps / OSM / HappyCow when appropriate).
- HUTA hours not verifiable from a single canonical source -- left as "Hours vary by event; opened 27 June 2025". Research agent should pin down current hours.
- Whistling Hound food-tour price genuinely not on the operator's listing page. Either the operator publishes a price later, or the entry stays with "Contact operator for current pricing".
- Bar Mleczny Mewa hours conflict across sources (one says Mon-Fri 09-17, another Mon-Fri 08-18 + Sat-Sun 09-16). Operator confirmation needed for definitive hours.
- Niewinność Wine Bar postal code 50-529 is per the source booking page; the street (Szewska) is in the Old Town normally postal 50-1xx range. Postal may be misprinted on the source; visitor-facing impact is minimal because street + number + lok. is correct.

## Verdict

VERDICT: PASS

The 23 defects landed broadly into three classes: (1) address fabrications the previous fixup-agent shortcut produced when it set `address_quoted = entity.address` rather than re-checking against an independent directory (3 venues -- HUTA, Niewinność, El Gato), (2) hours/dates the research agent shipped from generic-summary memory rather than operator-page reading (Zapiekarnik x3, Hala Targowa, Charlotte Sunday, Wino.grono, Feta Festival, Bar Mleczny Miś Sunday, STÓŁ Sunday cutoff), and (3) one fully-fabricated source URL (Cookly -- Warsaw class shipped as Wrocław). Class 1 is the structural risk the task brief warned about; class 2 is the canonical research-agent hours regression. None of the defects suggest a wholesale upstream regression; the rate is consistent with single-agent fan-out and the Wrocław-specific note that the fixup agent took the address_quoted shortcut.
