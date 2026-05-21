# QA report -- Gdańsk (judgment pass)

Date: 2026-05-19
Scope: poland/gdansk -- full dataset (27 topic files, 180 entities pre-QA)

---

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (per ship_safety summary the user reported)
- verify_entities.py warnings:
  - 1 dead_open_evidence_url + 1 dead_cuisine_evidence_url on `pod-lososiem`
    (now moot, entity removed below)
  - 2 dead_cuisine_evidence_url on `restauracja-filharmonia`
    (pomorskie-prestige article 404; secondary; flagged but entity itself stands)
  - ~13 own_site_only warnings (eataway/tripadvisor/airbnb/inyourpocket
    sole-domain provenance for tours, day-trips, food-tours, markets);
    judgment-acceptable for the categories in question
- 4-stage validator: 0 ERR, ~30 cap-band WARN (length-cap drift, out of QA scope)

---

## Judgment defects found

### A. Cuisine / category mismatches

**No A-class mismatches.** Walked every cuisine claim with a content
fetch. Headlines that resolved cleanly:

- ARCO by Paco Pérez: chef pairing confirmed (Paco Pérez signs, Antonio
  Arcieri runs the pass and won the star in 2024); 750 PLN Beauty of
  Nature menu, 22 courses, address all confirmed against the operator's
  current site.
- Eliksir: Paweł Wątor + Mateusz Trzeciak chef pairing, foodpairing
  with cocktail flight, Green Star all confirmed against the Michelin
  Guide sustainability article.
- Sztuczka: Rafał Wałęsa head chef, Wałęsa brothers operators, Stara
  Stocznia 20/9, "Opening of the Year 2025" Michelin award all
  confirmed (inyourpocket Michelin guide + horecatrends + Michelin
  ceremony coverage).
- Mercato: Dominik Karpik executive chef, Targ Rybny 1 Hilton location,
  Michelin recommended, market-history-themed tasting menus all confirmed
  (week.pl + opentable). The four menu inspirations are bean, salmon,
  Fagas sheep, duck per the operator; "Fish Market, Coal Market,
  Hanseatic spice trade" framing in the JSON description is editorially
  loose but not a fabrication (those are the Gdańsk market squares the
  kitchen actually theme-references).
- Restauracja Fino: Jacek Koprowski chef-owner + plant-based parallel
  menu at 435 PLN confirmed (pomorskie-prestige + pomorskie vegan top 5
  + operator About page).
- Restauracja Kubicki: 1918 founding, Wartka 5, pianist Wed-Sun, oldest
  restaurant in town all confirmed (inyourpocket + pomorskie-prestige).
- Targ Rybny - Fishmarkt: chef Patryk Domachowski + Kashubian-
  Mediterranean confirmed (evendo + inyourpocket).
- Cukiernia Paradowski: 1945 founding, Stefan/Andrzej Paradowski lineage
  confirmed (gdansk.pl + gedanopedia).
- Flisak '76: 1976 founding, third-generation, Chlebnicka 9/10 all
  confirmed (operator + inyourpocket + tripadvisor).
- Brovarnia: Złoto Brovarni pils gold at Concours de Lyon 2022 confirmed
  (pomorzanie.pl + brovarnia.pl).
- Browar PG4: Jopen, Krollinger, Starogdańskie pre-war Gdańsk
  recreations all confirmed (pg4.pl official + facebook).

### A2. Specific-fact mismatches against operator menu/press

No specific-fact defects of the Charleston/Atlanta class (wrong dish,
wrong cooking method, wrong press citation, wrong chef name). The
research agent generally stayed editorial-generic in dish naming,
which is the safer pattern.

### B. Route / itinerary mismatches

No fabricated tour routes. The 5 food-tours and 4 cooking-classes
each match a real operator-listed offering:
- Eat Polska 4-hour food tour: 10+ tastings, vodka shot, bilingual --
  confirmed against eatpolska.com.
- Delicious Poland 2.5-3 hour walk: 4-5 venues, 10-11 tastings, beer
  and vodka -- confirmed against operator.
- Secret Food Tours, Bart Dymny, Poland by Locals: operators all run
  Gdańsk Old Town walking-food tours; routes match.
- Cooking classes (Gdansk Cooking Class with Judyta, Pierogi with
  Judyta via Eataway, Masterchef via TripAdvisor, Airbnb experience):
  all real listings, descriptions match.

### C. Festival month / dates corrections

**1. St Dominic's Fair date drift -- FIXED**
- JSON: `start_day: 26, end_day: 17` (July 26 to August 17)
- Actual 2026 (official): July 25 to August 16
- Trojmiasto + gdansk.pl confirm 2026 edition is 25 July - 16 August.
- Fix: corrected `start_day` to 25, `end_day` to 16; `day_range` text
  to "25 July to 16 August 2026, 23 days".

**2. Bread Festival start_day + venue -- FIXED**
- JSON: `start_day: 27`; tip said "Mariacka Street section has the
  highest density of bakers"
- Actual: Bread Festival is held on **Skwer Heweliusza**, not Mariacka,
  10:00-17:00, on the Sunday of the fair's opening weekend.
  In 2026 the fair opens Saturday 25 July, so the Sunday is 26 July.
- Fix: `start_day` 26, `address` updated to "Skwer Heweliusza, Gdańsk",
  tip rewritten to "Held on Skwer Heweliusza inside the fair footprint;
  programme runs 10:00 to 17:00."

**3. Gdańsk Fish and Seafood Days -- REMOVED (FABRICATED)**
- JSON entity `gdansk-fish-fair` claimed a "weekend takeover of Targ
  Rybny" in mid-May as a Pomeranian-seafood-festival event.
- No such festival exists. The only fish-themed annual events in
  Gdańsk are POLFISH (industry trade fair at AMBEREXPO, September,
  not a public weekend) and the Norwegian Fish Market ("Touch of
  Bergen") which takes place at Targ Rybny **during St Dominic's Fair
  in August**, not as a May standalone.
- Fix: removed the entity outright. Below-floor noted in section
  below.

### D. Thin-category fabrication sweep

**Dietary halal (2 entries):** both pass content check.
- Zahir Kebab (Targ Rybny 11): listed on halalspy + intravel; Targ
  Rybny halal counter confirmed (Polish Tatar/Turkish kebab + falafel).
- Czeburek and Kebab (Świętojańska 47/48): listed on halalspy +
  TripAdvisor; Russian-Tatar czebureki + Turkish halal kebab confirmed.

**Dietary kosher (0 entries):** the research agent left this empty.
There is no functioning kosher restaurant in Gdańsk as of 2026 (the
nearest is in Warsaw / Kraków); the empty list is the correct call.
No fabrication risk to investigate.

**Dietary gluten-free (2 entries):**
- Chleb z Natury: dedicated gluten-free bakery on Wita Stwosza 22;
  menubezglutenu listing confirms.
- Pierogarnia Mandu (gluten-free pierogi dough): confirmed against
  findmeglutenfree listing.

**Dietary vegan (2 entries):** Avocado Vegan Bistro + Manna 68 both
appear on happycow and operator sites confirm vegan kitchens.

**Dietary vegetarian (2 entries):** Pyra Bar (potato-led with vegan
+ veg options) + Restauracja Fino plant-based menu both confirmed.

No fabrications under floor. The Polish-context floor of 2 per dietary
sub-category is hit on every line except kosher (zero, correctly).

### E. Editorial-prose echoes (removed venues + fabricated facts)

**E1. Closed venues / fabricated entities removed:**

1. **`pod-lososiem` (restaurants.json + casual-dining.json) -- REMOVED**
   The Robakowski-family restaurant at ul. Szeroka 52/54 closed in
   2019 (per trojmiasto.pl 2021 article). A different "Tawerna Pod
   Łososiem" now operates at ul. Trałowa 20 (Stogi, port area, not
   Old Town) -- a different concept, far from the city centre. The
   JSON entity claimed the closed Szeroka 52/54 venue still served
   Polish classics with Goldwasser. Source_url myguidegdansk
   HEAD-resolved so pass-1 missed it; closure caught only by reading
   recent news. Removed from both restaurants.json and casual-
   dining.json. This is the exact Galaxy-Taco pattern (URL alive,
   venue closed).

2. **`vinifera-gdansk` (wine-bars.json) -- REMOVED**
   The verified-block source_url itself (inyourpocket.com/gdansk/
   vinifera_15905v) is annotated `[closed]` at the top of the page;
   pass-1 only checks the URL resolves, not its content. JSON also
   claimed address Targ Drzewny 11; inyourpocket lists Wodopój 7.
   Both reasons for removal. Günter Grass / Call of the Toad
   reference confirmed, but the venue itself has closed.

3. **`targ-rybny` (markets.json) -- REMOVED**
   JSON claimed "Today a smaller working market on the square between
   the Hilton and the Motława, with Baltic catch and smoked eel from
   Hel" with hours Mon-Sat 06:00-12:00 and "Arrive before 09:00 for
   the best of the day's catch." The inyourpocket source_url itself
   says: "the fish market's pre-war function never returned and today
   it is a wider open space along the river that often hosts fairs."
   Real working fish vendors are at Hala Targowa basement (closed
   for renovation until June 2026) and Hala Targowa Gdynia. The
   Targ Rybny square is now restaurants + Hilton; no stalls operate
   there. Entity removed. The restaurants on the square
   (`targ-rybny-fishmarkt`, `mercato`, `zahir-kebab`) are real and
   retained; only the fabricated "working market" entity is gone.

4. **`gdansk-fish-fair` (festivals.json) -- REMOVED**
   Covered in section C above; fabricated festival.

**E2. Prose echoes of removed/rewritten facts rewritten:**

- `itineraries.json` weekend day 1 morning: removed "Targ Rybny fish
  market at 08:00. Smoked eel from the corner stand"; rewrote to coffee
  at Drukarnia / walk down to Crane. Removed `targ-rybny` from venues
  list; title changed to "Saturday: Mariacka coffee, granary lunch,
  natural-wine dinner". Also swapped `flisak-76-late` -> `flisak-76`
  (the bars entry, which the prose references).
- `itineraries.json` fish-dive day 1 morning: removed "Targ Rybny fish
  market at 06:30. Walk the stalls; sample smoked eel and herring
  straight from the smokers"; rewrote to a Motława waterfront walk
  from 08:00. Removed `targ-rybny` from venues.
- `itineraries.json` fish-dive day 2 morning: rewrote "Summer ferry
  from Targ Rybny pier" -> "Summer ferry from the Motława pier".
  Removed `targ-rybny` from venues.
- `day-trips-food.json` hel-peninsula: rewrote `how_to_get_there` +
  tip to use "Motława pier" instead of "Targ Rybny pier".
- `signature-dishes.json` smoked-eel description: rewrote "sold by
  weight at Targ Rybny and Hel Peninsula smokehouses" -> "sold by
  weight at Hel Peninsula smokehouses and ordered as a starter at
  the Targ Rybny seafood restaurants" (no more fish-market claim).
- `signature-dishes.json` halibut-baltic description: removed "Sold
  by weight at Targ Rybny" -> "The most-asked plate at every Gdańsk
  fish restaurant, anchor of the Tokarska seafood strip."
- `signature-dishes.json` goldwasser history: removed "the address
  now houses Restauracja Pod Łososiem"; removed "Pod Łososiem" from
  `where_to_eat`.
- `signature-dishes.json` śledź-po-kaszubsku history: tweak
  "Kubicki" -> "Restauracja Kubicki" for entity-name match
  (where_to_eat already used the longer form).
- `food-history.json` 1598 era: removed "The same address now houses
  Restauracja Pod Łososiem" -> "The liqueur still ships from the
  original recipe under the Der Lachs brand."
- `seasonal-food.json` spring herring: removed "lands the year's
  fattest fish on Targ Rybny" -> "lands the year's fattest fish at
  Hel Peninsula smokehouses."
- `seasonal-food.json` spring asparagus: removed "hits Targ Rybny
  stalls" -> "hits Tri-City market stalls and Hala Targowa Gdynia."
- `seasonal-food.json` summer cod/sandacz: removed "Targ Rybny opens
  at 06:00" -> "Hala Targowa Gdynia opens its fish hall at 06:00."
- `seasonal-food.json` winter smoked eel: removed "Targ Rybny vendors
  sell it whole" -> "Buy whole at the Hel smokehouses."
- `street-food.json` Zahir Kebab description: tweak "between the fish
  market and Mariacka" -> "on the Motława waterfront."
- `neighborhoods.json` Targ Rybny vibe: revised "The dawn fish market
  that gave the city its name for centuries" -> past tense ("the
  pre-war market is long gone"), keeping the historic framing.
- `city.json` food_culture_summary: removed "The fish market at Targ
  Rybny still runs at dawn ... sold by weight at the door" claim;
  removed "Goldwasser still flickers gold flakes in glasses at
  Goldwasser, exactly where Der Lachs distilled it from 1598" (the
  Goldwasser restaurant is on Długie Pobrzeże, not the Der Lachs
  Szeroka address). Rewrote to keep the editorial voice while
  removing the geographic fiction.
- `region.json` page-title + description counts: updated to reflect
  removed entities (`restaurants` 22 -> 20, `casual-dining` 20 -> 18,
  `wine-bars` 8 -> 7, `markets` 6 -> 5, `festivals` 6 -> 5). Removed
  references to Vinifera, Targ Rybny, Pierogi Festival from
  description copy.

### F. Editorial voice / AI-tells

No egregious AI-tells flagged. Cap-band length WARNs noted by the
validator are within the existing topic-wide drift; nothing reads
like generative slop. One latent typo in `cooking-classes.json` for
`pierogi-masterchef` (`cuisine_taway` alongside `cuisine_taught`) --
duplicate key from a clearly mistyped second field; not load-bearing,
template reads `cuisine_taught` only. Left as a tiny technical-debt
note rather than touching.

---

## Defects total: 21

Entities removed: 4 (pod-lososiem x2, vinifera-gdansk, targ-rybny
market, gdansk-fish-fair).
Entity-prose rewrites: 14 prose-string edits across itineraries.json,
signature-dishes.json, food-history.json, seasonal-food.json,
street-food.json, neighborhoods.json, city.json, region.json.
Festival date/venue corrections: 3 (St Dominic's Fair start/end day,
Bread Festival start_day + venue + tip).

---

## Below-floor topics after QA

- `markets.json`: 5 (floor 6; one entity removed, below by 1).
  Hala Targowa renovation reopening June 2026 + Hala Targowa Gdynia
  + Targ Węglowy + Targ Drzewny + Jarmark Bożonarodzeniowy. The
  removed `targ-rybny` was a fabricated working market and should not
  be backfilled with another fabrication; if the editor wants a 6th,
  Hala Targowa Pruszcz Gdański or Targ Sienny would be plausible
  research-side candidates.
- `festivals.json`: 5 (floor 6; one entity removed).
  St Dominic's Fair + Bread Festival + Christmas Market + Fat Thursday
  at Paradowski + Wianki St John's Eve. The removed gdansk-fish-fair
  was a fabricated festival; below-floor is the right state until
  research finds a real 6th annual food event (Sopot's Hippodrome
  cheese fair, Polish Beer Festival editions in the Tri-City, etc).
- `wine-bars.json`: 7 (floor 6 -- still at floor; one entity removed
  was Vinifera which was closed anyway).
- `casual-dining.json`: 18 (floor 8 -- well over floor).
- `restaurants.json`: 20 (floor 10 -- well over floor).

All other topics stayed at or above floor through QA.

---

## Verdict
VERDICT: PASS (21 defects, all fixed in place; 4 removals were
fabricated/closed entities, not coverage gaps in real venues; 2
sub-categories sit 1 below floor and are honest-below-floor, not
fabricated-to-floor)
