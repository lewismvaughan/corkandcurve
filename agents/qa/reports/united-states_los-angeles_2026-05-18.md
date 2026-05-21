# QA report - Los Angeles (round 3)

## Stage 1: 100% entity re-verification

- Total entities across topic JSONs (excluding neighborhoods/itinerary containers): ~163
- WebSearch performed on: 100% of venue-style entities across restaurants, casual-dining, fine-dining, cafes, bars, brunch, hidden-gems, bakeries, breweries, wine-bars, late-night, street-food, markets, coffee-roasters, festivals, cooking-classes, food-tours, dietary, plus itinerary venue mentions
- Defects found: K = 10 (counting Blue Bottle as 1 logical defect that propagated to 2 files, and the itinerary defect as 1 record)

Defect list with sources:

- `broken-mouth` (casual-dining): JSON address `718 South Hill Street` is wrong. Yelp, eatbrokenmouth.com and brokenmouthcafe.com all show `718 S Los Angeles St, Los Angeles, CA 90014`. Classic LA right-number-wrong-street defect. FIXED.
- `blue-bottle-aresenal` (cafes) and `tonx-blue-bottle` (coffee-roasters): JSON address `8951 Beverly Boulevard` is fabricated. Blue Bottle's own cafe page, Tripadvisor and Sprudge confirm `8301 Beverly Boulevard, West Hollywood, CA 90048`. Same building number wrong, in two files. FIXED in both files.
- `old-lightning` (bars): JSON address `1100 Abbot Kinney Boulevard, Venice` is wrong. Old Lightning is hidden inside Scopa Italian Roots at `2905 Washington Boulevard, Marina del Rey, CA 90292` per LAmag, Foursquare, and the bar's own OpenTable listing. Wrong street and wrong municipality. FIXED, description scrubbed of Abbot Kinney reference.
- `shojin-arts-district` (dietary/vegan): The Downtown LA Shojin location at 333 S Alameda St closed permanently April 2024 per Foursquare, Yelp ("CLOSED"), and Happy Cow. The Culver City Shojin still operates but is a different address than the JSON claimed. REMOVED.
- `plant-food-and-wine` (dietary/vegan): Closed May 2023 per Columbian, GoLocalProv, Gayot ("THIS RESTAURANT IS CLOSED"), and Yelp ("CLOSED"). Matthew Kenney was evicted. REMOVED.
- `sun-cafe` (dietary/gluten-free): Two-layer defect. Address `10911 Magnolia Boulevard, North Hollywood, CA 91601` is wrong: the real address is `10820 Ventura Blvd, Studio City, CA 91604` (wrong street, wrong neighborhood). Also currently closed for renovation per their own site and Yelp ("CLOSED - May 2026"); reopen uncertain. Per "when in doubt, remove." REMOVED.
- `wahibs-middle-east` (dietary/halal): Closed per Yelp ("CLOSED"), Foursquare ("Now Closed"). Chef Wahib has relocated to Star Buffet in Covina. REMOVED.
- `darya-persian` (dietary/halal): JSON address `12130 West Olympic Boulevard, Los Angeles, CA 90064` is wrong. Yelp, Tripadvisor, daryarestaurant.com, Timeout all show `12130 Santa Monica Blvd, West Los Angeles, CA 90025`. Right building number, wrong street name. Classic LA defect. FIXED, description scrubbed of Olympic mention.
- `got-kosher` (dietary/kosher): JSON address `8914 West Pico Boulevard` is wrong. Yelp, Grubhub, and the bakery's own listings show `8758 W Pico Blvd, Los Angeles, CA 90035`. Wrong building number. FIXED.
- `los-angeles-westside-chef-day` (itineraries) day 2: References Cassia for brunch (closed Feb 22, 2025 per Santa Monica Mirror, Yelp "CLOSED") and Bar Nine in Culver City for pour-over (Culver City location closed per Yelp; only El Segundo location remains). FIXED: replaced with Milo and Olive brunch and Gjusta afternoon.

## Stage 1 per-topic breakdown

- restaurants (18): 18 verified, 0 removed
- casual-dining (15): 15 verified, 1 address fix (broken-mouth)
- fine-dining (9): 9 verified, 0 removed
- cafes (14): 14 verified, 1 address fix (blue-bottle-aresenal)
- bakeries (12): 12 verified, 0 removed
- coffee-roasters (4): 4 verified, 1 address fix (tonx-blue-bottle, dup of Blue Bottle bug)
- street-food (8): 8 verified, 0 removed (Carnitas El Momo at 2411 Fairmount confirmed clean per round-1 fix)
- food-halls: file does not exist (out of scope)
- markets (8): 8 verified, 0 removed
- bars (13): 13 verified, 1 address fix (old-lightning)
- wine-bars (8): 8 verified, 0 removed
- breweries (5): 5 verified, 0 removed
- speakeasies: file does not exist (out of scope)
- hidden-gems (8): 8 verified, 0 removed (Kuya Lord at 5003 Melrose confirmed clean per round-1 fix)
- brunch (9): 9 verified, 0 removed (Cassia not in brunch.json; itinerary-only reference)
- late-night (8): 8 verified, 0 removed
- festivals (6 recurring events): 6 verified - months match, 2025 editions confirmed held, 2026 historically certain
- cooking-classes (2): 2 verified, schedules current
- food-tours (3 with operator schemas): 3 verified, routes match what operators advertise (Six Taste East LA tacos, Six Taste Thai Town, Avital Koreatown progressive)
- neighborhoods (15): informational containers, no individual address check
- itineraries (3): 1 needed stale-venue cleanup (westside-chef-day)
- dietary (15 across vegan/vegetarian/gluten_free/halal/kosher): 4 removed (closed), 2 address fixes
  - vegan: 4 -> 2 (shojin and plant-food removed)
  - vegetarian: 2 verified
  - gluten_free: 3 -> 2 (sun-cafe removed)
  - halal: 3 -> 2 (wahibs removed); darya address fixed
  - kosher: 3 verified; got-kosher address fixed

## Stage 2: round-3 convergence call

- This is round 3. Defect count K = 10.
- Round 1 caught 35. Round 2 caught 10. Round 3 caught 10. The address-class is still leaking despite two prior passes, and there were 4 outright closed venues that round 2 missed entirely. The defect rate has not bottomed out.
- Recommendation: round 4. Defects of this kind compound in SEO indexes; convergence has not been reached. Round 4 should specifically:
  - Re-verify every dietary entry with closed-status searches (highest concentration of closures this round)
  - Run a third address sweep on remaining venues (4 of 10 round-3 defects were wrong addresses)
  - Audit every itinerary's referenced venues for closure since prior pass

## Stage 3: cross-city correctness

- `check_external_urls.py --country united-states --city los-angeles`: 3 broken / 130, all anti-bot codes (521 The Prince, 403 Vespertine Tock, 401 Unsplash hero image). Pass.
- `audit_live.py`: 1328 pages crawled, 0 errors, 0 broken extras LA-scoped, 0 broken extras non-anti-bot. Pass.
- 83 warnings are meta-description length (validator territory, not QA).
- Breadcrumb spot-check: content tree intact (`content/united-states/los-angeles/` contains all 24 topic dirs plus index.html).

## Defects removed

| Slug | Topic | Reason |
|---|---|---|
| broken-mouth | casual-dining | Address fixed: 718 S Hill St -> 718 S Los Angeles St |
| blue-bottle-aresenal | cafes | Address fixed: 8951 Beverly -> 8301 Beverly |
| tonx-blue-bottle | coffee-roasters | Address fixed: 8951 Beverly -> 8301 Beverly |
| old-lightning | bars | Address fixed: 1100 Abbot Kinney -> 2905 Washington Blvd Marina del Rey |
| shojin-arts-district | dietary/vegan | REMOVED - DTLA location closed permanently April 2024 |
| plant-food-and-wine | dietary/vegan | REMOVED - closed May 2023 |
| sun-cafe | dietary/gluten_free | REMOVED - closed for renovation + wrong street + wrong neighborhood |
| wahibs-middle-east | dietary/halal | REMOVED - closed, chef relocated to Covina |
| darya-persian | dietary/halal | Address fixed: 12130 W Olympic -> 12130 Santa Monica Blvd |
| got-kosher | dietary/kosher | Address fixed: 8914 W Pico -> 8758 W Pico |
| los-angeles-westside-chef-day | itineraries | Day-2 stale Cassia and Bar Nine references replaced with Milo and Olive + Gjusta |

## Below-floor topics after QA

- dietary/vegan: dropped from 4 -> 2 entries. Per food-research/PROMPT.md dietary section, vegan floor is typically 3. NEEDS BACKFILL.
- dietary/gluten_free: dropped from 3 -> 2 entries. May be below floor.
- dietary/halal: dropped from 3 -> 2 entries. May be below floor.

Other 21 topic JSONs remain at or above floor.

## Verdict

VERDICT: NEEDS_FIXES
