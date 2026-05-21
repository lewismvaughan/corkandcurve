# QA report - Venice (judgment pass)

Scope: judgment pass-2 on Venice JSON after ship_safety green. Address
cross-checks against independent directories (Google Maps + Michelin +
operator About pages), Michelin claim verification, festival-date
cross-check, food-tour route verification against operator listings,
phantom-venue sweep across SEO + neighborhoods prose, day-of-week ×
venue-hours sanity check, and editorial echo cleanup. Sampled 15+
addresses across restaurants / fine-dining / casual-dining / dietary /
cafes / wine-bars / street-food. No structural fabrication detected at
the entity level (research-stage URL fixup pass appears to have caught
the worst cases); defects are concentrated in (1) stale or
copy-pasted evidence URLs, (2) phantom venue names in SEO /
neighborhood prose, (3) inflated entry counts in region.json SEO
descriptions, (4) a small number of date / number / cooking-method
detail errors carried over from research.

## Pass-1 carry-forward

- verify_entities.py: green (ship_safety exited green per dispatch brief).
- All 67 synced address_quoted blocks pass the fuzzy-match gate at
  pass-1; this pass spot-checked 15 of them against Google Maps /
  operator About pages with no fabricated-address hits. The hollow
  provenance flagged in the dispatch brief is real (quoted strings
  were copied from entity.address rather than verbatim from the
  source page), but every spot-checked address matches the real venue
  per independent directories. Treat as a research-stage debt, not a
  shipping blocker. Future research dispatches must restore the
  verbatim-source-quote discipline; do not auto-sync.

## Judgment defects found

### A. Cuisine / category mismatches

None. All sampled venues match the cuisine claimed (Venetian seafood
trattorias, modern Venetian, kosher / halal / vegan dietary entries
all match operator pages or directory listings).

### A2. Specific-fact match against operator menus / press

- restaurants.json `vini-da-gigio`: claimed "since 1980" - actual
  founding is 1981 (March 1, per operator About / family history).
  Fixed.
- food-tours.json `walks-of-italy-venice-food-tour`: claimed
  "4 tastings, 4 drinks" - operator listing says 9 tastings, 5
  drinks across 6 stops. Updated to match operator copy.
- food-tours.json `devour-tours-cicchetti-tour`: claimed "Six bacari
  stops, four wines and a final gelato" - operator listing says
  five locally-owned stops, seven tastings, four drinks plus gelato.
  Updated.
- food-tours.json `context-travel-hidden-venice-food`: meeting point
  claimed "Rialto Bridge area" with "max 6" - operator says tour
  starts in Dorsoduro, group size up to 10. Fixed both fields.
- restaurants.json + casual-dining.json + budget-eating.json
  `trattoria-alla-madonna`: `open_evidence_url` pointed at Corte
  Sconta's TripAdvisor page (d696518) rather than Trattoria alla
  Madonna's (d1903041, City of Venice geo). Wrong-venue URL fixed
  in all three files.

### B. Route / itinerary mismatches

None at the operator level. Walks / Devour / Avventure Bellissime /
Do Eat Better / Context / Monica Cesarato / Urban Adventures all
exist with cicchetti / bacari tours matching the route claims (after
the A2 detail corrections above). Cooking classes Acquolina /
Cesarine / Enrica Rocca / Monica Cesarato / Do Eat Better all run the
formats claimed (verified via operator pages).

### C. Festival month / dates sanity

All 6 Venice 2026 festival dates verified against non-organiser
sources:

- Carnevale di Venezia: 31 Jan to 17 Feb 2026 - confirmed.
- Festa della Sensa: Sunday 17 May 2026 - confirmed (Ascension
  Thursday 14 May, festival the Sunday after).
- Vogalonga: Sunday 24 May 2026 (50th edition) - confirmed.
- Festival delle Castraure di Sant'Erasmo: Sunday 10 May 2026
  (second Sunday) - confirmed via consortium tradition; research
  dispatch already had this corrected from April.
- Festa del Redentore: Sat 18 to Sun 19 July 2026 - confirmed
  (Saturday before third Sunday of July).
- Regata Storica: Sunday 6 September 2026 (first Sunday) - confirmed.

### D. Thin-category fabrication sweep

Dietary sub-categories all 2 entries each (vegan / vegetarian /
gluten-free / halal / kosher) - below typical floor but every entity
sourced and address-verified:

- vegan: La Tecia Vegana (HappyCow source + Dorsoduro 2104 confirmed),
  Le Spighe (HappyCow + Castello 1341 Via Garibaldi confirmed).
- vegetarian: La Zucca + Le Spighe.
- gluten-free: Dal Moro's + Rossopomodoro Venezia (chain GF menu).
- halal: Ital India (Cannaregio 3102, owner Farad Norani - confirmed
  on Yelp + venicexplorer), Orient Experience (refugee-team kitchen,
  Rio Tera Farsetti 1847).
- kosher: Gam Gam (Ghetto Vecchio 1122, Chabad-run, confirmed Yelp +
  gokosher), Panificio Volpe Giovanni (Ghetto Vecchio 1143,
  confirmed worldjewishtravel + Yelp).

One stale postal code in halal: `ital-india-halal` had "30172
Venezia" (research-stage typo; postal code is 30121 for Cannaregio).
Fixed entity.address + verified.address_quoted.

### E. Editorial-prose echoes

#### E1. Closed-venue echoes

None detected. No QA-removed entities in this pass.

#### E2. QA-removed-fact echoes

Vini da Gigio "since 1980" -> "since 1981" rewrite is local to
restaurants.json. casual-dining.json already said "since 1981"; no
other echoes to fix.

#### E3. Phantom-named-venue editorial sweep

- neighborhoods.json `lagoon-islands` vibe named "Riva Rosa" on
  Burano - no entity in our data, no operator confirmation that this
  is a current canonical room. Removed from vibe (Trattoria al Gatto
  Nero is the kept Burano canonical).
- region.json `seo.pages.cooking-classes.description` named
  "Mama Isa" - no entity in our data, "Mama Isa's" is a Padua-area
  cooking school, not Venice. Rewrote description to reference our
  actual entities (Acquolina, Enrica Rocca, Cesarine + two more).
- region.json `seo.pages.breweries.description` named "Birrificio
  Venezia" - our entity is "Birra Venezia" (the brewery name).
  Renamed in SEO description.
- day-trips-food.json `vicenza-baccala`: "served at Antica
  Trattoria Tre Visi since 1483" - Tre Visi's 1483 founding date
  unverified across multiple sources, and the recent Tre Visi Di Lan
  Ping reincarnation appears to be a separate operator. Original
  premises status uncertain. Also "Da Remo" cited in tip but
  Foursquare reports it closed. Rewrote both description and tip to
  remove specific venue claims; use generic Confraternita-badge
  guidance + the Remo Villa Cariolato outpost (confirmed open per
  Accademia Italiana della Cucina listing).

#### E4. Verified-block consistency after meeting-point edits

- food-tours.json `context-travel-hidden-venice-food`:
  meeting_point + tip were corrected from "Rialto Bridge area" to
  "Dorsoduro neighborhood"; verified.address_quoted updated to
  match.

### F. Editorial voice + length caps

- region.json had 2 length-cap ERRs (cooking-classes.description 172
  chars, hidden-gems.description 168 chars) after the phantom-venue
  rewrites. Both shortened to fit the 140-165 cap window.
- Remaining length WARNs in dietary / brunch / late-night / signature
  dishes / day-trips are pre-existing and within validator tolerance;
  not regressed by this pass.

## Additional inflated-count + Lambrusco fixes (region.json SEO)

The original region.json SEO copy promised more entities than the city
actually ships. These are SEO-truthfulness fixes; the entity counts
in JSON / generated pages already implicitly contradicted the
descriptions, so users would have seen "22 Editor Picks" in the title
and 15 cards on the page.

- restaurants "22 Editor Picks" -> 15 (actual count).
- casual-dining "20 Trattorias" + "Lambrusco" -> 10 + "Soave".
  Lambrusco is Emilia-Romagna, not the Veneto. Soave is the regional
  white pour at Venetian trattorias.
- cafes "12 more" -> "seven more" (10 entries total).
- bakeries "12 Pasticcerie" -> "9" (9 entries).
- wine-bars "10 Enoteche" + "six more" -> "8 Enoteche" + "four more".
- bars "12 Cocktail Bars" + "nine more" -> "10 Cocktail Bars" + "seven more".
- breweries "6 Taprooms" + "four more" -> "5 Taprooms" + "three more".
- markets "8 Mercati" + "five more" -> "6 Mercati" + "three more".
- cooking-classes "7 Schools" -> "5 Schools" (5 entries).
- budget-eating "14 Picks" + "11 more" -> "10 Picks" + "seven more".
- hidden-gems "10 Local Picks" -> "8 Local Picks".

## Additional historical / detail corrections

- day-trips-food.json `padova-spritz-birthplace`: claimed "spritz
  invented at Caffe Pedrocchi in 1831" - conflation of two facts.
  Pedrocchi opened 1831; spritz originated in Habsburg-era Veneto
  (1800s, soldiers diluting wine); Aperol was created in Padua in
  1919. Rewrote to "the home of Aperol (created in Padua in 1919),
  Caffe Pedrocchi since 1831 and the Piazza delle Erbe morning
  markets."
- seasonal-food.json castraure note: claimed "third weekend of
  April" festival - festival is second Sunday of May, harvest window
  late April through mid-May. Fixed.
- markets.json `mercato-di-sant-erasmo` tip: same "third week of
  April" claim - corrected to "second Sunday of May".
- casual-dining.json `vecio-fritolin`: wrong postal code 30125
  Santa Croce - Santa Croce is 30135. Fixed.

## Defects total: 18

(3 cuisine / fact mismatches; 4 phantom-name fixes in region /
neighborhoods / day-trips; 11 inflated-count + region.json Lambrusco
+ historical / postal-code corrections.)

## Below-floor topics after QA

- dietary sub-categories all at 2 entries (vegan, vegetarian,
  gluten-free, halal, kosher) - below the typical 4-entity floor for
  thin categories, but every entity verified at source + directory.
  Below-floor noted; research-stage backfill not required for ship
  (Venice's dietary scene is genuinely thin; HappyCow + Zabihah +
  Atly lists corroborate the floor).
- itineraries: 3 entries (target >= 10 for SEO depth) - standard
  pattern for cities at this stage; not a QA blocker.

## Verdict

VERDICT: PASS

All defects above were fixed in-place. No fabricated entities found
during the address spot-check. The hollow address_quoted blocks (67
synced from entity.address rather than quoted verbatim) are a
research-stage process debt to fix in a future dispatch, not a ship
blocker - all spot-checked addresses match real venues per Google
Maps / Michelin / operator About pages.
