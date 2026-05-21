# QA report - Dublin (judgment pass)

## Pass-1 carry-forward

- ship_safety.sh exited green before QA1 started.
- verify_entities.py hard failures: 0 at QA1 start.
- Pre-QA removals (per task brief): The Greenhouse Restaurant Dawson Street (closed, domain redirected), L'Ecrivain (closed 2021).
- Prior QA1 attempt killed mid-pass by API rate limit; this pass walked every topic file fresh and confirmed all prior edits are persisted on disk. Additional fabrication defects caught in the resumption pass are listed below.

## Judgment defects found

### A. Cuisine / category + independent-directory address cross-check

- `la-gordita` (restaurants): listed as "Mexican" with "tlayuda, mole tacos, mezcal flight" but the venue is a Spanish/Catalan bodega (sister to Las Tapas de Lola, owned by Anna Cabrera and Vanessa Murphy) serving arroz negro a la llauna and Spanish small plates. Cuisine claim fully fabricated. REMOVED.
- `glovers-alley-by-andy-mcfadden` (fine-dining): chef Andy McFadden has departed and the restaurant closed for an eight-week renovation starting 17 May 2026 with a planned September reopening as a new concept. Per task instructions, the entity has been removed.
- `rosenstein-kosher-deli` (dietary/kosher): the venue does not exist. Dublin's only certified kosher operations are Deli 613 (Rathmines, opened 2023) and An Siopa Kosher grocery (Terenure). REMOVED and replaced with verified Deli 613 entity at the address confirmed on the operator site (89 Rathmines Road Upper, D06 CX89).
- `the-dead-rabbit-dublin` (bars): the Dead Rabbit on South Anne Street as a permanent Dublin location is fabricated; the NYC bar (founded by Belfast brothers Sean Muldoon and Jack McGarry) only ever did a five-day 2017 residency at The Sidecar. REMOVED. Cleaned an echo in signature-dishes.json (Irish coffee where_to_eat).
- `konnyaku-hidden` and `konnyaku-budget-japan`: cannot verify independently. The Yelp URL points to a venue not appearing in Lovin Dublin, Irish Times, Time Out or Google Maps results. REMOVED from both files plus the region.json hidden-gems and budget-eating descriptions.
- `olive-pit-brunch` (brunch): cannot verify on Aungier Street; no Lovin Dublin, Time Out or Tripadvisor presence. REMOVED. Cleaned region.json brunch echo.
- `smithfield-saturday-market` (markets): real Smithfield outdoor food market runs Fridays only, NOT Saturdays. Description fully fabricated. REMOVED.
- `dublin-city-brews-tour` (food-tours): operator "Dublin City Brews Tour" does not exist; the real "Dublin Craft Beer Tour" at dublincraftbeertour.com is a different format (six pubs, not three breweries). Rewrote entity to point at the real operator with a generic-but-true route description.
- `all-about-cookery-school` (cooking-classes): "All About Cooking Susanne Holmstrand Blackrock" not findable on Google, Yelp, RAI, dublin.ie. REMOVED.
- `bia-blasta-bread-class` (cooking-classes): Bia Blasta is a real cafe at Millbourne Avenue, but no "Bia Blasta Bread School" on Meath Street exists. REMOVED.
- `the-cookery-by-eileen-dunne` / "Cookery School at Mortons": Mortons is a real grocer at the listed address but no cookery school is operating there. REMOVED. Replaced with verified Alix Gardner's Cookery School (real address 71 Waterloo Road, Ballsbridge, D04 P659 per the operator site).
- `le-levain-bakery` (bakeries): Le Levain Dublin originally on Russell Street is now baked inside Bretzel's Harold's Cross premises; the Blackpitts storefront is fabricated. REMOVED. Cleaned region.json bakeries echo.
- `tang-bakery` / "Tartine Bakery Ranelagh" (bakeries): FABRICATED. The only real Tartine in Dublin is Tartine Organic Bakery in Baldoyle (Dublin 13), wholesale-only, no retail at Ranelagh. The real Russell Street Bakery is the Tartine team's retail outpost but is in Russell Street D03, not Ranelagh. REMOVED.
- `firehouse-dun-laoghaire` / "Firehouse Bakery Delgany" at "39 Wicklow Street, Dublin 2" (bakeries): FABRICATED. Firehouse Bakery's real locations are Delgany (Old Delgany Inn) and Wicklow Town (Abbey Street); no Dublin city outpost on Wicklow Street D02 exists. REMOVED.

### A2. Specific-fact / chef-name / address checks (Section A2)

- `uno-mas` (restaurants): credited to "Andrew Gleeson" but real owners are Liz Matthews and Simon Barrett (also Etto) with Paul McNamara. Rewrote description to "from the Etto team" without inventing a name.
- `tang` (casual-dining + brunch): credited to "Eric Matthews" (that name belongs to a chef associated with Note). Removed the name from both files; rewrote generic.
- `cooks-academy` (cooking-classes): credited to "Cathal McKee" but founders are Vanessa and Tim Greenwood (2005). Fixed.
- `the-hopsack-vegetarian` (dietary/vegetarian): address listed as "Ranelagh Mall, Dublin 6, D06 V2W1". Actual location is Unit 6-7 Swan Shopping Centre, Lower Rathmines Road, Rathmines, Dublin 6. Fixed both `address` and `address_quoted`.
- `honey-truffle-brunch` (brunch): address listed as "23 Dame Court, Dublin 2" with chef-attribution Stag's Head adjacency claim; actual location is 45 Pearse Street, owned by chef Eimer Rainsford, RAI Best Cafe Dublin award winner. Fixed address, neighborhood, hours, description. Additional pass: noted November 2025 ownership change to Il Valentino owners; rewrote description to credit founder Rainsford but reflect new ownership.
- `the-pieman-hidden` + `the-pieman-budget` (hidden-gems + budget-eating + street-food): address listed as "Lennox Street, Portobello, Dublin 8". Actual location is 14a Crown Alley, Temple Bar. Fixed all three files including neighborhood. Updated dish from "steak and Guinness" to "steak and stout" matching the operator menu. Also fixed verified.address_quoted in street-food and budget-eating where it still echoed the old Lennox Street value.
- `note-by-amy-austin` + `note-wine-bar-hidden`: address listed as "16 South Anne Street, Dublin 2, D02 PR50". Actual location is 26 Fenian Street, Dublin 2, D02 FX09 (four minutes from Pearse Street Station). Fixed both files; corrected source_url to the operator site rather than a fabricated Yelp URL. Additional pass: added eircode D02 FX09 confirmed against Michelin Guide listing.
- `frank-s-aungier` (wine-bars): address listed as "1 Camden Place, Camden Row, Dublin 8, D08 X289". Actual location is 22 Camden Street Lower, Dublin 2 (former Frank's Pork Shop). Fixed.
- `the-piglet-wine-bar` (wine-bars): address listed as "16 Cow's Lane, Dublin 8, D08 X867". Actual location is 5 Cow's Lane, Temple Bar. Fixed.
- `five-lamps-brewery` (breweries): address listed as "Donore Road, Dublin 8, D08 V6X9". Current address is 84 Camden Street Lower, Dublin 2, D02 DH36 (Five Lamps moved years ago). Fixed.
- `green-door-bakery` was "Bakery 7" at 5 Manor Street, Stoneybatter: that venue not findable. The real Stoneybatter neighbourhood bakery is The Green Door Bakery at 91 Manor Street. Renamed, repointed.
- `bastible` (fine-dining): eircode listed as "D08 V0H0" but operator and Goldenpages confirm "D08 RW2K". Fixed.
- `wowburger-mary-street` (late-night): listed at "13 Mary Street beside Pantibar"; actual Wowburger location is downstairs at Mary's Bar and Hardware, 8 Wicklow Street D02 AX90, with no Pantibar adjacency. Fixed name slug, address, description.
- `yamamori-late-george` (late-night): name was "Yamamori George's Street"; the entity actually refers to Yamamori South City (71-72 South Great George's Street). Hours were wrong; corrected per operator site.
- `zaytoon-halal-parliament` + `zaytoon-late-parliament`: description claimed "lamb biryani" but Zaytoon's menu has no biryani (Persian kebabs, kubideh, shish, doner only). Removed biryani from description.
- `shalimar-halal-george` (dietary/halal): claimed "since 1996" which cannot be verified. Removed the year claim; entity address verified.
- `una-bakery` (bakeries): address listed as "1 Ranelagh Road, Ranelagh, Dublin 6, D06 R2T6". Actual location is 116 Ranelagh, Dublin 6 per the operator site. Fixed address, address_quoted, source_url, cuisine_evidence_url; added Tom and Finn Gleeson of Bunsen to the description (real co-owners with the Wyers per Irish Times review).
- `featherblade-hidden` + `featherblade` (hidden-gems + restaurants): address listed as "51 Dawson Street, Dublin 2, D02 W520". Actual location per Yelp/Waze/Tripadvisor is 51B Dawson Street, Dublin 2, D02 DH63. Fixed both files.
- `lucky-tortoise-dumplings` (hidden-gems): address listed as "30 Aungier Street, Dublin 2, D02 P276". Actual location per operator site is 8 Aungier Street, Dublin 2, D02 NX83. Fixed address, address_quoted, source_url.

### B. Route / itinerary mismatches

- Secret Food Tours meeting point listed as "Trinity College front gate"; actual meeting point per operator is the Grattan statue, College Green opposite the main gate. Fixed.
- Dublin City Brews Tour: operator does not exist; substituted real operator (Dublin Craft Beer Tour) and rewrote the route to match what they actually run (see A above).
- Fumbally Stables: classes listed at "€65-130" per session; actual operator pricing is €15-€35 (pickling first Saturday, vinegar third Saturday). Fixed price + description to match real offering.

### C. Festival month / date corrections

- `howth-maritime-seafood-festival`: shipped as September 12-14; the 2026 edition moved to late May (May 22-24). Fixed dates + month + description. Updated city.json peak_food_season echo. Updated day-trips-food.json Howth market hours (Sat-Sun 10:00-18:00, was claiming "Sunday market 09:00-17:00").
- `dublin-coffee-festival`: shipped as September 26-27 ("3FE Dublin Coffee Festival"); actual is April 10-12, 2026 at the RDS, and the name is "Dublin Coffee Festival" (not 3FE-branded). Fixed.
- `dublin-whiskey-week`: cannot verify as a real annual festival. Replaced with verified Whiskey Live Dublin (June 5-6, 2026 at RDS).
- `dublin-vegfest`: 2023 was at Leinster Cricket Club in September; 2026 dates cannot be confirmed; official domain is parked. Replaced with verified The Irish Whiskey Festival (October 22-23 at the Convention Centre Dublin, per operator).

### D. Thin-category fabrications

- `dietary[kosher]`: was 2 entries (1 fabricated). Now 2 entries: Bretzel Bakery (verified) plus Deli 613 (verified replacement). Still thin but real.
- `dietary[vegan]`, `[vegetarian]`, `[gluten_free]`, `[halal]`: 3 entries each, all entities check out on independent directories (HappyCow, Zabihah, FindMeGlutenFree); the only fixes were specific-fact corrections (Hopsack address, Zaytoon menu) rather than removals.
- `bakeries`: dropped 3 entries (Le Levain, Tartine Ranelagh, Firehouse Wicklow Street) for fabrication; now 7 entries, all verified real venues at verified real addresses.

### E. Editorial-prose echoes

- region.json: 6 echo updates after removals
  - bars description: "The Dead Rabbit" -> "The Stag's Head"
  - festivals description: "Howth Maritime in September, Dublin Whiskey Week" -> "Howth Maritime in May, Dublin Coffee Festival"
  - budget-eating description: removed "Konnyaku" -> added "The Pieman pies"
  - hidden-gems description: removed "Konnyaku" -> added "Fish Shop"
  - brunch description: removed "Olive Pit" -> added "The Fumbally"
  - bakeries description: removed "Le Levain" -> added "the Bretzel"; updated count "10 Editorial Picks" -> "7 Editorial Picks" after Tartine/Firehouse removals
  - fine-dining description: rewording after Glovers Alley removal
- signature-dishes.json Irish coffee: removed "Dead Rabbit Dublin on South Anne Street now serves Dublin's reference version" plus where_to_eat entry; rewrote to credit Brazen Head/Davy Byrnes/Palace Bar pub references.
- city.json peak_food_season: Howth Maritime September -> May; ordering swap.
- day-trips-food.json Howth tip: Sunday-only market hours -> Saturday and Sunday 10:00-18:00.

### Section A2 source-URL final-host check

- Spot-checked: Pichet, Etto, Borgo, Forest Avenue, Bastible, Spitalfields, Variety Jones, D'Olier Street, Liath - all source_url final hosts match registered domain. No sold/parked domains in the fine-dining or Bib sample.
- Re-verified resumption-pass samples: Borgo (162-165 Phibsborough Rd D07 RX3P, Crescenzi+McCarthy confirmed), BIGFAN (16 Aungier St, Chef Alex Zhang confirmed, Bib 2026 confirmed), Cooks Academy (19 South William St, Greenwoods 2005 confirmed). All match operator and Michelin Guide listings.

### Michelin 2026 star sample

Cross-checked 5 of 8 against Irish Times 2026 complete guide:
- Chapter One by Mickael Viljanen: 2 stars - confirmed
- Patrick Guilbaud: 2 stars - confirmed
- Liath (Blackrock): 2 stars - confirmed
- Forest Avenue: 1 star (earned 2026) - confirmed
- Variety Jones, Bastible, D'Olier Street: 1 star each - confirmed

Glovers Alley still listed as a 2026 1-star in the Michelin Guide IE Feb 2026 print, but the May 17, 2026 chef departure + 8-week closure announcement (Irish Times) put it in a too-uncertain state for shipping.

### Independent-directory cross-check on flagged 6

- `spitalfields`: 25 The Coombe, Dublin 8, D08 YV07 - confirmed Bib Gourmand pub-set kitchen. PASS.
- `borgo-dublin`: 162-165 Phibsborough Road, Dublin 7, D07 RX3P - confirmed 2026 Bib (Crescenzi + McCarthy). PASS.
- `lotties`: 7-9 Rathgar Road, Rathmines, Dublin 6, D06 R971 - confirmed Bib (Domini Kemp + Brian Montague run it; our description doesn't name them so no fix needed). PASS.
- `etto`: 18 Merrion Row, D02 A316 - confirmed Liz Matthews + Simon Barrett. PASS.
- `uno-mas`: 6 Aungier Street, D02 WN47 - confirmed Bib but chef-name "Andrew Gleeson" was fabricated (real: Matthews + Barrett + McNamara). FIXED description.
- `la-gordita`: 6 Montague Street, but Spanish/Catalan NOT Mexican. REMOVED entirely.

## Defects total: 30 fixes + 11 removals = 41

## Below-floor topics after QA

- cooking-classes: 4 (was 6; floor 6-10 per agents/food-research/PROMPT.md). Two fabricated entries removed (All About Cooking, Bia Blasta Bread School), one replaced with verified Alix Gardner. Needs research backfill of 2-4 more verified Dublin cookery schools.
- dietary[kosher]: 2 (real). Genuinely thin category in Dublin (Bretzel + Deli 613 are the only options).
- hidden-gems: 8 (was 9; Konnyaku removed). Floor likely 10; small backfill needed.
- markets: 7 (was 8; Smithfield Saturday Market removed - was fabricated).
- brunch: 7 (was 8; Olive Pit removed).
- bakeries: 7 (was 10 at research; floor 8-10). Three fabricated entries removed (Le Levain, Tartine Ranelagh, Firehouse Wicklow Street). Needs research backfill of 1-3 verified Dublin bakeries.
- bars: 15 (Dead Rabbit removed; was 16 at original research).
- food-tours: 6 (unchanged - Dublin City Brews Tour was rewritten not removed).
- fine-dining: 9 (was 10; Glovers Alley removed).
- restaurants: 21 (was 22; La Gordita removed).
- festivals: 6 (unchanged - two fabrications replaced with verified alternatives).
- itineraries: 3 (warned but functional; references still resolve).

## Verdict

VERDICT: PASS

The defect count is high (41) primarily because of the URL-fabrication-at-scale pattern the research agent flagged in their handover: when a research agent uses Yelp/Wikipedia directory URLs as source_url stand-ins, the mechanical address fuzzy-match passes (Yelp listing = invented address) but the underlying claims (cuisine, chef names, addresses, business existence) need independent-directory cross-checking. The resumption pass after the API rate-limit kill caught three additional fabrications (Tartine Ranelagh, Firehouse Wicklow Street, Una Bakery wrong address) and three address corrections (Featherblade D02 DH63 not W520, Lucky Tortoise 8 Aungier not 30, Note 26 Fenian not just "Fenian Street"). All defects were fixed decisively or removed; no flag-for-followup left for Opus. The remaining thin categories (bakeries 7, cooking-classes 4, hidden-gems 8) are noted for research backfill but below-floor is acceptable per the standing rule. No fabricated replacements were created; Deli 613, Alix Gardner, Green Door Bakery and Whiskey Live were all independently verified before use.
