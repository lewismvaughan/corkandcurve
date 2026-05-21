# QA report - Poznań (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety passed pre-QA)
- verify_entities.py warnings: 0 (per task brief)
- check_internal_references.py post-QA: ERR=0 WARN=0 (65 names, 97 slugs resolve)

## Judgment defects found

### A. Cuisine / category mismatches
- None removed; all cuisine-evidence URLs spot-checked against operator pages or independent directories pass.
- Edit: SPOT. cuisine described as "Modern Polish" - operator self-describes as "seasonal Polish blended with classic European (especially French)." Existing JSON is acceptable shorthand; not changed.

### A2. Specific-fact mismatches (the bulk of this round)

**Cukiernia Kandulski (bakeries.json)**
- Address fabrication: JSON address `Os. Bolesława Chrobrego 117, 60-681 Poznań` does NOT correspond to any Kandulski branch per the operator's own `/lokalizacje/` page (8 branches listed, none on Chrobrego). Replaced with the real central branch at `Plac Cyryla Ratajskiego 1, 61-728 Poznań`. Updated verified.address_quoted and open_evidence_url to match.
- Founding-year fabrication: JSON description claimed "since 1891." Real founding 1983 by Wojciech Kandulski (confirmed via Wikipedia, official site, multiple press sources). Rewrote description.

**Cukiernia Pawlova (bakeries.json)**
- Postcode typo: 62-031 -> 62-030 (per operator's own site).
- Specialty/description softened: JSON billed Pawlova as making "Rogal świętomarciński (butter, World Master Confectioner)" but Pawlova is NOT on the Cech Cukierników i Piekarzy certified list (the Luboń certified producer is Anika Butka). Pawlova's own product page says "TRADYCYJNE ROGALE NA MAŚLE" (traditional butter rogale), not "rogale świętomarcińskie" (PGI protected term). Rewrote specialty to "Traditional butter rogale by a World Master Confectioner" and description to "traditional butter rogale baked to the Master's recipe."

**Rogalowe Muzeum Poznania (food-tours.json + cooking-classes.json)**
- Show duration fabrication: JSON claimed "40 minutes." Real duration about 60-65 minutes per official site. Corrected to "About 1 hour."
- Ticket-price fabrication: JSON claimed "20 PLN adult, 15 PLN child." Real price 41 PLN normal / 37 PLN reduced for croissant show, 47/43 for croissant + goats. Corrected.
- Group-size fabrication: cooking-classes.json claimed "40 max." Show capacity isn't published as a hard number; replaced with "Limited seats per show."
- Address normalisation: full address is "Stary Rynek 41/2"; updated entry addresses + meeting_point + address_quoted to match.

**Poznań Feast Tour (food-tours.json)**
- Capacity fabrication: JSON tip said "the tour caps at 12." Operator's own page lists tiered pricing for groups up to 60 (190 PLN at 21+, 220 PLN at 10-15). Rewrote tip without invented cap.
- Duration: 2.5 h -> "Up to 3 hours" (operator says "up to 3 hours").
- Price: "from 220 PLN" -> "from 190 PLN per person, scales by group size" (220 is the small-group rate).

**Vine Bridge (fine-dining.json + restaurants.json + hidden-gems.json)**
- Outdated superlative: JSON claimed "the country's smallest serious restaurant by table count" with "three tables and a counter." The room expanded with an additional eight-table room (per multiple press sources). Softened to "one of the country's smallest serious tasting restaurants." Removed "slam-cuisine" framing in favour of "new Polish cuisine" (chef Nejman's own description per press).

**Cucina (fine-dining.json)**
- Unverified tip detail: "Book the chef's table near the wine wall...the only mid-service tasting menu add-ons." No source confirms a chef's table or mid-service add-ons. Rewrote tip to focus on the verified wine wall + VIP wine pairing tasting.

**Marino Bistrot (casual-dining.json)**
- Vague address: JSON had `address: "Jeżyce, Poznań"` (no street/number). Real address is `ul. Poznańska 50/2, 60-848 Poznań` per operator's own site (also confirmed via inyourpocket.com). Updated address, description prose to include street, and verified.address_quoted.
- Description updated to "2024+2025 Michelin Guide recommendation" (both years confirmed on Michelin Guide listing).

**WINO - Targi Polskich Win i Winnic (festivals.json)**
- Date off-by-one: JSON said 19-21 March 2026; official site says 18-20 March 2026. Updated start_day/end_day/day_range.
- Description "100 native producers" -> "over 140 exhibitors" (per organizer).

**Story Coffee Roasters Poznań (coffee-roasters.json)**
- has_cafe inverted: JSON said `has_cafe: false` and "the roastery does not run a public-facing cafe." Operator runs a campus speciality-coffee point at Politechnika Poznańska (Centrum Wykładowego, "pod zegar"). Set `has_cafe: true` and rewrote description + tip.

**Stragan Kawiarnia (brunch.json + cafes.json + coffee-roasters.json)**
- Postcode wrong: JSON had `61-815`, correct is `61-816` (per official directories incl. gdziezjescpoznan.com).
- Brunch hours fabrication: JSON said "Daily 08:00-21:00." Real hours Mon-Fri 08:00-22:00, Sat 12:00-18:00, **closed Sunday**. Corrected hours field.

**Pączuś i Kawusia (brunch.json)**
- Hours fabrication: JSON said "Daily 08:00-19:00." Real hours Mon-Sat 10:00-18:00, Sun 12:00-18:00 (per operator's eatbu page). Corrected.

**Dram (late-night.json)**
- Days-of-week wrong: JSON `closes: "Thu-Sat 01:00"` (implied 3-day operation). Operator's own site says Mon-Fri 18:00-01:00, Sat 12:00-01:00, Sun 12:00-23:00 (open 7 days). Rewrote.

### B. Route / itinerary mismatches

**Itinerary `poznan-weekend-regional` day 2 (Sunday)**
- Stragan-closed-Sunday violation (day-of-week x hours): JSON evening said "a final filter at Stragan before the room closes at 21:00." Stragan is **closed Sunday**. Removed the Stragan stop; updated venues array.
- Rogalowe Muzeum showtime wrong: JSON said "the 10:30 baking show." First show is **11:00** per museum site (Sun-Fri 11:00-15:30 window). Corrected.
- Pączuś i Kawusia Sunday opening: real opening 12:00 on Sundays (not earlier morning). Reworded morning to acknowledge Sunday noon opening.
- Added Piwna Stopa Sunday 13:00 opening note to the evening.

### C. Festival month / date corrections
- WINO Targi: 19-21 March -> 18-20 March 2026 (covered in A2 above; logged here too).
- St. Martin's Day (Nov 11): JSON correct, no change.
- Restaurant Week (4 Mar - 22 Apr 2026): JSON correct, no change.

### D. Thin-category fabrications
- Halal: 1 entry. Turkish Kebab (Halal) at Święty Marcin 45 - verified via halalfoodle.com, multiple Polish directories, real phone +48 575 064 741. Kept.
- Kosher: 0 entries. Leave below floor (no Jewish dietary infrastructure surfaced in Poznań research, not fabricated).
- Gluten-free: 2 entries (Just Friends + Krowarzywa). Just Friends confirmed on Find Me Gluten Free directory. Krowarzywa - vegan-burger chain with GF bun. Both pass.
- Vegan: 3 entries. Wypas, Miłość, Krowarzywa - all verified open, real addresses. Miłość had an older "closed" HappyCow entry for a defunct Woźna street location; the active operation at Garbary 54 has multiple live delivery listings (Wolt, UberEats, pyszne.pl) and an active Instagram - kept.
- Vegetarian: 2 entries (SPOT + Weranda) - both real.

### E. Editorial-prose echoes (closed venues AND QA-removed facts)

Echo-fix pass after Section A2 edits:
- "Os. Bolesława Chrobrego" / "1891" Kandulski strings: grep confirms only the bakeries.json entry contained these. No itinerary or food-history echo to fix. (1891 also appears in markets.json for Rynek Jeżycki founding - separate, verified-true claim.)
- Stragan removed from itinerary day 2 venues array; matching prose update made in the same edit.
- "Plac Cyryla Ratajskiego 10" / Bar Mleczny Pod Arkadami address - already correct in budget-eating.json (the brief flagged this as a concern but the entity address was already the right value).
- "Woźna 21" / LAGACCA - already correct in cafes.json (matches the brief's pre-fix state).
- "Święty Marcin 45" / Turkish Kebab Halal - already correct in dietary.json (matches the brief).

### E2. Food-history immigrant-influences cleanup
- German (Prussian) contribution: rewrote the conflated "Stary Browar + Brovaria-style brewpub culture" sentence. Brovaria opened 2004 by Polish operators; it doesn't belong in the 19th-century German immigrant influence paragraph. Replaced with the historically accurate Hugger family brewery on Półwiejska that became Stary Browar.

### F. Editorial voice / AI-tells
- No egregious AI-tell cases flagged. Length-cap warnings are pre-existing (validator) and not in scope.
- Note for next round: many descriptions are 170-220 chars vs the 140-165 cap. Not corrected here (validator handles, length-only is not judgment scope), but the research agent should compress on the next pass.

## Defects total: 17

Breakdown:
- A2 entity-fact rewrites: 13 (Kandulski x2 issues, Pawlova x2, Rogalowe Muzeum x4 fields across 2 files, Feast Tour x3 fields, Vine Bridge x3 files, Cucina, Marino Bistrot, Story Coffee, Stragan postcode+hours, Pączuś hours, Dram hours)
- B itinerary fix: 1 (Sunday day-2 cascade in poznan-weekend-regional)
- C festival fix: 1 (WINO dates)
- E2 history rewrite: 1 (Brovaria sentence in German-influence paragraph)
- Entity removals: 0 (every defect was a rewrite, not a removal)
- Entity additions: 0 (no fabricated replacements - hard rule)

## Below-floor topics after QA
(Pre-existing, unchanged by this pass; not the QA agent's job to backfill)
- bakeries: 4 (target 10)
- coffee-roasters: 2 (target 10)
- wine-bars: 3 (target 10)
- street-food: 4 (target 10)
- breweries: 3 (target 10)
- markets: 4 (target 10)
- food-tours: 2 (target 10)
- festivals: 3 (target 10)
- cooking-classes: 1 (target 10)
- late-night: 4 (target 10)
- day-trips-food: 4 (target 10)
- itineraries: 3 (target 10)
- dietary/halal: 1, kosher: 0

Poznań is the smallest city in the Polish batch - some of these floors are structurally hard to hit honestly (single certified coffee roastery, single cooking-class operator). Research agent should backfill the easier categories (bakeries, wine-bars, street-food, late-night).

## Verdict
VERDICT: PASS

Rationale: 17 defects in 113 entities (~15% touch rate) is at the typical judgment-pass-2 level for a regional EU city. All defects were rewrites or corrections to verified-true content; no fabricated replacements; no entity removals. The biggest single defect class was the cukiernia Kandulski fabrications (wrong address + wrong founding year) - the research agent should be flagged for that one. Pass-1 mechanical gates remained clean throughout, and post-QA internal-references check passes 0 ERR.
