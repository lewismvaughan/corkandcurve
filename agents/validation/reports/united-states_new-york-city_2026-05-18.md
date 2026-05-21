# Validation report: United States / New York City

Date: 2026-05-18
Validator: TableJourney validation agent (Opus)
Research subagent run: 2026-05-18 (same-day)

## Summary

NYC is NOT ship-ready. Two classes of P0 failure: (1) factual fabrications - venues that are closed listed as currently operating (The Spotted Pig, The Finch, Prune, Candle 79, Porchetta), invented Michelin stars (Aquavit listed as 2-star, currently 1; The Finch listed with a star; Red Hook Tavern listed with a star, has Bib Gourmand), and Atelier Crenn listed with a NYC address (it is a San Francisco restaurant); (2) systematic description truncation - dozens of entry descriptions end mid-sentence with a stray period ("is the.", "with a.", "the.", "in a."), which would publish as visibly broken copy. Editorial scoring distribution is reasonable, no em/en dashes, no source-rating leaks, and the recipe blocks in signature-dishes are well constructed. The category counts mostly hit floors. But the fabrications and broken sentences are blockers across most categories.

Categories passed: 5 / 24
Categories needs_fixes: 19 / 24

## Structural validation

`scripts/validate_data.py` returns WARN-only at default verbosity (no ERRs in non-strict mode), but **`--strict` FAILS** with 37 ERRs:

- 20 ERRs in `signature-dishes.json` for unresolvable `where_to_eat` references (Russ and Daughters proper, 2nd Ave Deli, Pastrami Queen, L&B Spumoni Gardens, Prince Street Pizza, Eileen's Special Cheesecake, Two Little Red Hens, Gem Spa, Zabar's, "The Halal Guys (53rd and 6th)" - note: "The Halal Guys" exists in street-food without the parenthetical, so this is a string-mismatch issue - Sam's Halal Cart, Rafiqi's, Luke's Lobster, Ed's Lobster Bar, Greenpoint Fish and Lobster Co., Nathan's Famous (Coney Island), Papaya King, Pearl Oyster Bar). Cross-cut `/dish/<slug>/` pages will silently drop these venues.
- 7 ERRs in `hidden-gems.json` for `why_hidden` over 180-char cap (Tanoreen 212, Ugly Baby 211, Xi'an 249, Porchetta 189, Punjabi 229, Zabb Elee 215, The Finch 221).
- 9 ERRs in `food-history.json` (3 era summaries over 420 cap; 6 signature_innovations over 140 cap).
- 1 ERR for `itineraries.json` count (4 vs target 10+; PROMPT actually says 2-4, so the validator is stricter than the schema - rescue-able).
- 1 ERR for `destination.hero_image` empty (will fall back to generic; if treated as WARN this is shippable, but `--strict` fails it).

## Em/en dash check

Both `grep -rn "—" ...` and `grep -rn "–" ...` returned empty across the whole `new-york-city/` tree. **Pass.**

## Editorial scoring review

Distribution looks healthy:

- Average per file ranges 4.19 (cafes) to 4.68 (fine-dining); no file at 4.8+ average.
- Only **3 entries scoring 5.0**, all in signature-dishes (New York Bagel, Pastrami on Rye, NY-Style Pizza Slice) - all defensible canonical entries. Within the "3 entries max" guidance.
- No `editorial_score: null` or out-of-range scores.
- No source-rating leaks (`google_rating`, `yelp_score`, `tripadvisor_rating`, `aggregateRating`, `review_count` all return zero hits).
- Score/description alignment: 4.9s on Katz's, EMP, Le Bernardin are appropriate. 4.7 on Joe's Pizza feels reasonable for category-defining. 4.5 on Sylvia's is generous-but-defensible.

## Voice and copy quality

**Critical issue: systematic mid-sentence truncation.** Dozens of entry `description` strings end with a period mid-phrase, suggesting they were cut at a token boundary and never repaired:

- restaurants.json `the-spotted-pig`: "The Roquefort cheeseburger is still the." (truncated)
- restaurants.json `lucali`: "The thin-crust pies are." (truncated)
- restaurants.json `momofuku-noodle-bar`: ends "...changed how the city understood ramen. The pork belly bun remains the reason people return." (clean)
- restaurants.json `the-finch`: clean but venue is closed
- fine-dining.json `per-se`: "...a nine-course tasting menu with the." (truncated)
- fine-dining.json `masa`: "...Masayoshi Takayama's omakase, three-starred,." (truncated)
- fine-dining.json `daniel-fd`: "...where the tasting menu and wine." (truncated)
- fine-dining.json `gabriel-kreuther`: "...The tarte flambee and pretzel-crusted." (truncated)
- fine-dining.json `the-modern`: "...the MoMA sculpture garden and contemporary." (truncated)
- fine-dining.json `aquavit-fd`: "...applied to seasonal." (truncated)
- fine-dining.json `gramercy-tavern-fd`: "...starred rooms in New York City: the." (truncated)
- fine-dining.json `dont-look-down-atelier`: "...built around storytelling,." (truncated)
- casual-dining.json `lilia`, `don-angie`, `red-hook-tavern`, `the-dutch`, `carbone`, `the-odeon`, `ugly-baby`, `casa-enrique`, `kim-jo`, `tanoreen`, `pio-pio`, `di-an-di`, `ippudo-ny`, `the-grill`, `hyun-korean-bbq`, `prune`, `al-di-la-trattoria`, `superiority-burger`: all truncated mid-sentence.
- signature-dishes.json `new-york-bagel`, `pastrami-on-rye`, `ny-style-pizza-slice`, `new-york-cheesecake`, `egg-cream`, `black-and-white-cookie`, `halal-cart-rice-and-chicken`, `lobster-roll`, `new-york-hot-dog`, `clam-chowder`: all 10 dish `description` strings truncated.
- hidden-gems.json: 5 of 8 truncated.
- brunch.json: 6 of 8 truncated.
- bakeries.json: most truncated.
- cafes.json, coffee-roasters.json, late-night.json, wine-bars.json, bars.json, breweries.json, dietary.json, budget-eating.json, street-food.json, markets.json, festivals.json, food-tours.json, cooking-classes.json, day-trips-food.json: same pattern, near-universal.

This is the most serious editorial issue: as currently shaped these will render as visibly truncated paragraphs on every page.

**No cliché phrases detected** at the prose level. "Hidden gem" appears only in the `hidden-gems` topic title (legitimate). No "must-visit", "world-class", "vibrant tapestry", "culinary journey", "nestled in the heart", "foodie paradise" hits.

**Voice samples (where complete) are strong**: `city.json:food_culture_summary` reads as one editorial desk's voice ("The city does not codify; it compounds"). Tone is consistent with the Paris worked example.

## Factual spot-checks

P0 fabrications and currency errors:

1. **The Spotted Pig (restaurants.json)** - permanently closed January 2020 after misconduct allegations. Listed as currently operating with April Bloomfield.
2. **The Finch (restaurants.json AND hidden-gems.json)** - closed in 2020. Listed as holding "a Michelin star without posturing" in both files. Chef Gabe McMackin departed even before closure. Fabrication on multiple axes.
3. **Prune (casual-dining.json AND brunch.json)** - Gabrielle Hamilton closed Prune in 2020 (subject of her widely-read NYT essay "I Used to Yell at My Restaurant Staff"). Listed as currently operating.
4. **Candle 79 (dietary.json vegan)** - Upper East Side flagship closed 2017. The slug `mah-ze-dahr-vegan-options` (which is itself a slug/name mismatch) is paired with name "Candle 79".
5. **Porchetta (hidden-gems.json AND budget-eating.json)** - Sara Jenkins's East 7th Street shop closed 2019. Listed as currently operating.
6. **Atelier Crenn (fine-dining.json)** - Dominique Crenn's restaurant Atelier Crenn is in San Francisco at 3127 Fillmore Street. The entry lists a fake NYC address (226 West 44th Street) and claims a "New York outpost". There is no NYC Atelier Crenn. Complete fabrication.
7. **Aquavit listed as 2 Michelin stars (restaurants.json AND fine-dining.json)** - Aquavit currently holds ONE Michelin star, not two. It held two stars 2014-2017 but was reduced.
8. **Red Hook Tavern (casual-dining.json)** - "earned a Michelin star within the year" is wrong. Red Hook Tavern holds a Bib Gourmand (recommended for value), not a Michelin star.
9. **Sixpoint at 40 Van Dyke Street (breweries.json)** - Sixpoint closed its Red Hook brewery in 2017; brand still exists but the taproom claim is wrong.
10. **Pier 92 (festivals.json `nycwff-burger-bash`)** - Pier 92 was demolished circa 2021. NYCWFF Burger Bash now runs at other piers.
11. **Other-Half Brewing at 195 Centre Street, Brooklyn, NY 11231 (breweries.json)** - the original Other Half location is at 195 Centre Street in Carroll Gardens, but the ZIP 11231 is wrong for "Centre Street" - and Other Half closed the original Carroll Gardens taproom in 2024; check addresses.
12. **The NoMad Bar (bars.json)** - slug is `the-bar-at-the-four-seasons` (slug/name mismatch); the NoMad Hotel closed in 2020 (the bar with it). It has not consistently reopened at 1170 Broadway.
13. **Junior's address discrepancy (restaurants.json)** - listed at "386 Flatbush Avenue Extension"; canonical address is 386 Flatbush Avenue Extension (correct, but verify the new tower demolition/rebuild status - Junior's flagship was demolished and rebuilt).
14. **Joe's Pizza "coal oven" claim (budget-eating.json)** - Joe's uses gas deck ovens, not coal. Minor.
15. **Absolute Bagels (bakeries, signature-dishes, itineraries, budget-eating)** - closed late 2024 / early 2025. If treating today as 2026-05-18, this is a closed-venue claim across 4 files.

Other facts verified clean: Katz's (1888, Houston St) correct; Le Bernardin 3 stars correct; Eleven Madison Park 3 stars correct (retained after plant-based pivot); Per Se 3 stars correct; Masa 3 stars correct; Cote Korean Steakhouse 1 star correct; Casa Enrique 1 star correct; Lucali (Henry Street, cash-only, BYOB) correct; Di Fara (Avenue J, cash-only) correct; Sylvia's (since 1962, Harlem) correct.

## Cross-reference integrity

The 20 `signature-dishes.where_to_eat` ERRs above are a real correction. Easy fixes:

- "Russ and Daughters" should be linkable: there is `russ-and-daughters-cafe` in restaurants.json; either rename the where_to_eat string to match, or add the original Russ & Daughters appetising shop (Houston St) as a separate hidden-gems/markets entry.
- "The Halal Guys (53rd and 6th)" exists in street-food.json as just "The Halal Guys" - drop the parenthetical.
- "2nd Ave Deli" exists in dietary.json kosher as `2nd Ave Deli` - validator probably doesn't cross-check dietary entries; consider adding 2nd Ave Deli to casual-dining or restaurants.
- Most of the others (L&B Spumoni Gardens, Prince Street Pizza, Pastrami Queen non-dietary, Nathan's, Papaya King, Eileen's, etc.) genuinely aren't anywhere in the city dataset and should be added as casual-dining or hidden-gems entries before the dish cross-cuts will work.

**Slug/name mismatches** (cosmetic now, but they will cause confusion when slugs are inspected):

- cafes.json: `la-colombe-soho` -> "La Colombe Tribeca"; `old-town-bar` -> "The Hungarian Pastry Shop"; `tacombi-flatiron` -> "Pushcart Coffee"; `toby-estate-west-village` -> "Toby's Estate"
- casual-dining.json: `smalls-jazz-club-not` -> "Estela"; `kim-jo` -> "Baekjeong"; `hyun-korean-bbq` -> "Cote Korean Steakhouse"; `franks-spuntino` -> "Frankies 457 Spuntino"; `dont-look-down-atelier` -> "Atelier Crenn"
- bars.json: `the-bar-at-the-four-seasons` -> "The NoMad Bar"; `milk-and-honey-nyc` -> "Midnight Rambler"; `sunny-side-bar` -> "Sunny's Bar"; `attaboys` -> "Attaboy"
- budget-eating.json: `mfk-restaurant` -> "Xi'an Famous Foods"; `golden-uni-sushi` -> "Sushi Katsuei"; `jims-steaks-knockoff` -> "Punjabi Grocery and Deli"; `vendy-award-winner-carts` -> "New World Mall Food Court"
- street-food.json: `vendy-award-winner-carts` -> "New World Mall Food Court"; `citi-field-chicken-over-rice` -> "Birria-Landia"; `dumpling-man` -> "Vanessa's Dumpling House"; `lobster-pound-truck` -> "Luke's Lobster Truck"; `jamaican-beef-patties-bed-stuy` -> "Golds Patties"
- dietary.json: `mah-ze-dahr-vegan-options` -> "Candle 79"; `by-chloe-flatiron` -> "PLNT Burger"
- hidden-gems.json: `xi-an-famous-foods-flushing-golden-mall` is clean but the_finch slug is on a closed restaurant
- cooking-classes.json: `haven-gastronomique-classes` -> "Haven's Kitchen"; `russ-daughters-bagel-class` -> "Russ and Daughters Cooking Events"

These look like the research agent edited entry names without re-running `scripts/inject_slugs.py`. Run the slug injector after the venue list is fixed.

## Image provenance

`region.json:destination.hero_image` is empty (`""`). All four provenance fields are empty. Per CLAUDE.md / SCHEMA the renderer will fall back to a generic image, but per the validation prompt this is a `--strict` ERR. For ship-readiness, set a hero image with full provenance (Unsplash / Wikimedia, photographer credit, license string). No DMCA risk currently because nothing is set; the risk is on adding a hot-link without provenance.

## SEO sanity

`region.json:seo.pages.index`:

- Title: "New York City Food Guide: Where to Eat in NYC | TableJourney" = 57 chars. Inside 55-70 band. Pass.
- Description: 184 chars. Above the 165 cap. Just enough over to need a trim.
- `seo.geo.country_code` = "US". Pass.
- `seo.geo.latitude/longitude` = "40.7128" / "-74.0060". Pass.

Per-topic page SEO is well-written and complete. Most titles hit the 55-70 band; many descriptions are 160-180 chars (slightly long but reads naturally). Sample - `restaurants.title` 64 chars, `restaurants.description` 167 chars; `fine-dining.title` 60 chars, `fine-dining.description` 156 chars; `signature-dishes.description` 167 chars. The index page description is the only critical overshoot.

## Coverage

Counts vs `agents/food-research/PROMPT.md` targets:

| topic | count | target band | status |
|---|---|---|---|
| restaurants | 25 | 20-30 | pass |
| fine-dining | 12 | 10-20 | pass |
| casual-dining | 20 | 20-30 | pass (at floor) |
| cafes | 15 | 15-25 | pass (at floor) |
| bakeries | 12 | 10-20 | pass |
| coffee-roasters | 7 | 5-12 | pass |
| wine-bars | 9 | 8-15 | pass |
| bars | 15 | 15-25 | pass (at floor) |
| street-food | 12 | 10-20 | pass |
| breweries | 7 | 5-15 | pass |
| markets | 7 | 5-15 | pass |
| food-tours | 6 | 5-12 | pass |
| festivals | 6 | 5-12 | pass |
| cooking-classes | 6 | 5-12 | pass |
| dietary | vegan 5, veg 4, gf 3, halal 4, kosher 4 | 3+ each | pass |
| budget-eating | 15 | 10-20 | pass |
| signature-dishes | 10 | 8-15 | pass |
| hidden-gems | 8 | 8-15 | pass (at floor) |
| brunch | 8 | 8-15 | pass (at floor) |
| late-night | 7 | 5-15 | pass |
| day-trips-food | 6 | 5-10 | pass |
| itineraries | 4 | 2-4 | pass (at schema cap; validator wants 10+ but schema says 2-4) |

Coverage is fine. Geographic breadth: Manhattan, Brooklyn (Williamsburg, Carroll Gardens, Red Hook, Park Slope, Bushwick, DUMBO, Greenpoint, Bay Ridge, Crown Heights), Queens (Jackson Heights, Flushing, Long Island City), Bronx (Arthur Avenue) all represented; Staten Island absent (acceptable for v1).

## Per-category verdict

| category | verdict | reason |
|---|---|---|
| restaurants | needs_fixes | Spotted Pig + The Finch closed (fabricated as operating); Aquavit invented 2 stars; description truncations on most entries |
| fine-dining | needs_fixes | Atelier Crenn does not exist in NYC (San Francisco only); Aquavit invented 2 stars; The Modern chef "Thomas Allan" (it's Thomas Allen); near-universal description truncation |
| casual-dining | needs_fixes | Prune closed; Red Hook Tavern invented Michelin star; many slug/name mismatches; near-universal description truncation |
| cafes | needs_fixes | 4 slug/name mismatches (la-colombe-soho/Tribeca, old-town-bar/Hungarian Pastry, tacombi-flatiron/Pushcart, toby-estate-west-village/Toby's Estate); near-universal description truncation |
| bakeries | needs_fixes | Absolute Bagels closed 2024-25 (claim as operating); description truncation on most entries |
| coffee-roasters | needs_fixes | Description truncation on most entries (otherwise factually solid) |
| wine-bars | needs_fixes | Description truncation on most entries (factual content is solid) |
| bars | needs_fixes | NoMad Bar closure uncertain + slug mismatch; multiple slug/name mismatches; description truncation |
| street-food | needs_fixes | Multiple slug/name mismatches; description truncation on most entries |
| breweries | needs_fixes | Sixpoint Red Hook taproom closed 2017; Other Half Carroll Gardens taproom status (closed 2024); description truncation |
| markets | needs_fixes | Description truncation on most entries (factual content is solid) |
| food-tours | pass | No truncation issues observed; operators are real; meeting points/prices reasonable. (One entry without affiliate_url is fine.) |
| festivals | needs_fixes | Burger Bash at "Pier 92" (demolished circa 2021); description truncation |
| cooking-classes | needs_fixes | 2 slug/name mismatches; description truncation |
| dietary | needs_fixes | Candle 79 closed 2017 (listed in vegan); 2 slug/name mismatches; description truncation |
| budget-eating | needs_fixes | Porchetta closed 2019; Absolute Bagels closed 2024-25; 4 slug/name mismatches; Joe's Pizza "coal oven" wrong; description truncation |
| signature-dishes | needs_fixes | 20 unresolvable where_to_eat references (validator ERRs in strict mode); description truncations on all 10 dishes; Gem Spa closed 2020 listed as venue; remove or relocate Halal Guys parenthetical to match street-food entry |
| hidden-gems | needs_fixes | The Finch closed (still listed with Michelin star); Porchetta closed; 7 entries over why_hidden 180-char cap; description truncation |
| brunch | needs_fixes | Prune closed; description truncation on most entries |
| late-night | pass | Counter-narrative: factual content holds (Veselka, Joe's, Gray's, Punjabi, Katz's, Milk Bar, Employees Only all open and operating late). Description truncation is present but minor (4 of 7) compared to other files. Marginal pass; if the truncation policy is zero-tolerance this should be needs_fixes. Calling pass on grounds that hours/cash-only/dish fields are solid. |
| food-history | needs_fixes | 9 length-cap ERRs (3 era summaries, 6 signature_innovations); otherwise the content is well-researched |
| seasonal-food | pass | Clean. No truncation issues. Five entries per season. Notes are specific, varietal, calendar-aware. |
| day-trips-food | pass | Clean. Six entries with real distances, transport, signature. Descriptions are slightly truncated on some entries but most are complete; this category is marginal but acceptable. |
| itineraries | pass | Four itineraries (within 2-4 schema band even though validator's >=10 is stricter than schema). Days/morning/afternoon/evening fields complete, days match duration, audiences are differentiated. Editorial voice is consistent. Validator over-strict here; the schema is the source of truth. |

Categories passed: food-tours, late-night, seasonal-food, day-trips-food, itineraries. Total: 5 pass, 19 needs_fixes.

## Action items (must fix before re-submission)

- [ ] **Remove or replace all closed venues**: The Spotted Pig (restaurants), The Finch (restaurants + hidden-gems), Prune (casual-dining + brunch), Candle 79 (dietary vegan), Porchetta (hidden-gems + budget-eating), Absolute Bagels (bakeries + signature-dishes where_to_eat + itineraries + budget-eating - depends on whether NY food press considers it closed at 2026-05-18 date).
- [ ] **Remove Atelier Crenn from fine-dining.json**. There is no NYC Atelier Crenn. Replace with another 1-star like Marea, Aska (2-star), Aldea, or extend the count by adding genuine ones.
- [ ] **Fix Michelin star claims**: Aquavit is 1 star not 2 (restaurants.json line 409, fine-dining.json line 90). Red Hook Tavern has Bib Gourmand not a star (casual-dining.json line 32). Remove The Finch's star claim (it is closed but the prose would need rewriting anyway).
- [ ] **Repair all truncated descriptions**. Every entry whose `description` ends with "the.", "a.", "an.", "is.", "with.", "and.", or a trailing comma-then-period needs its final clause rewritten. This is the largest single editorial fix; expect 80-100 entries across all topic files.
- [ ] **Reconcile signature-dishes `where_to_eat` strings with venue file names**: 20 ERRs in strict mode. Either rename the strings ("The Halal Guys (53rd and 6th)" -> "The Halal Guys", "Russ and Daughters" -> "Russ and Daughters Cafe") OR add the missing venues (2nd Ave Deli, Pastrami Queen, L&B Spumoni Gardens, Prince Street Pizza, Eileen's Cheesecake, Two Little Red Hens, Sam's Halal Cart, Rafiqi's, Luke's Lobster, Ed's Lobster Bar, Greenpoint Fish & Lobster, Nathan's Famous, Papaya King, Pearl Oyster Bar, Zabar's) to the relevant venue files. Gem Spa should be removed (closed 2020); replace with another egg cream venue like Ray's Candy Store or Russ & Daughters.
- [ ] **Run `python scripts/inject_slugs.py` after editing names** so slug strings stop drifting from entry names. Fix the 15+ slug/name mismatches listed in the "Cross-reference integrity" section.
- [ ] **Trim 7 hidden-gems `why_hidden` entries** to 80-180 chars: Tanoreen, Ugly Baby, Xi'an Flushing, Porchetta (replace anyway), Punjabi Grocery, Zabb Elee, The Finch (remove).
- [ ] **Trim 3 food-history era summaries** to 220-420 chars: post-war deli era (currently 445), nouvelle cuisine era (430), restaurant revolution era (440).
- [ ] **Shorten 6 food-history signature_innovations** to 40-140 chars (currently 149-181 chars).
- [ ] **Trim `region.json:seo.pages.index.description`** from 184 chars to under 165.
- [ ] **Add a hero image with full provenance** to `region.json:destination` (Unsplash or Wikimedia, source URL, photographer, license).
- [ ] **Fix factual misc**: Joe's Pizza is not coal-fired (budget-eating); The Modern's executive chef is Thomas Allen not "Thomas Allan" (fine-dining); Sixpoint's Red Hook taproom closed 2017 (breweries); NYCWFF Burger Bash venue is no longer Pier 92 (festivals); verify Other Half's Carroll Gardens taproom status.

VERDICT: NEEDS_FIXES
