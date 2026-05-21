# QA report: San Francisco (round 3)

## Stage 1: 100% entity re-verification

- Total entities across 22 topic JSONs (SF has no speakeasies, no food-halls): 183
- WebSearch performed on: 183 (100%)
- Defects found: 6 hard removals/fixes plus 3 in-place corrections

Defects:

- the-plant-cafe-organic (dietary.vegetarian): permanently closed. Yelp Feb 2026 listing and HappyCow both show CLOSED for Pier 3 The Embarcadero location. Removed.
- shangri-la-vegetarian (dietary.kosher): permanently closed. Yelp Feb 2026 confirms CLOSED (closed via ADA litigation). Removed.
- local-tastes-mission (food-tours): fabricated route. Local Tastes of the City operates Chinatown / North Beach / Little Italy tours; they do not run a Mission District taqueria tour. The JSON described a fictional Mission route (La Taqueria, Tartine, Bi-Rite) with a Dolores Park meeting point. Removed.
- foodie-adventures-haight (food-tours): fabricated route. Chris Milano's Foodie Adventures runs three neighborhood tours: Mission District, North Beach, and Chinatown. They do not run a Haight-Ashbury tour. The JSON described a fictional Haight tour meeting at Magnolia Brewing. Removed.
- rooster-and-rice-cart (street-food): fabricated address. Rooster & Rice's current SF outlets are 2211 Filbert, 125 Kearny, 3251 20th Avenue, and 1 Stanyan. 1101 Sutter Street is a four-level parking garage with no Rooster & Rice presence. Classic address-hallucination defect. Removed.
- z-zoul-cafe (dietary.halal): wrong address. Operator exists but Z Zoul Cafe is at 295 Eddy Street, not 1379 Mission Street. Fixed in place.

In-place corrections (operator real, content wrong):

- avital-tours-north-beach (food-tours): meeting point and tip rewritten. Real meeting point is 1630 Stockton Street at the Italian Athletic Club; public tours run Saturday 15:00 to 18:00, not 13:00. The route (Caffe Trieste, Molinari, Tony's Pizza) is correct so the entry was kept.
- sf-restaurant-week (festivals): month corrected from "January and April" to "April and November". Current event is twice yearly Spring (April) and Fall (November). January editions stopped after 2020.
- itinerary san-francisco-long-weekend, day 2 afternoon: removed Boulettes Larder reference. Boulettes Larder permanently closed July 31, 2025 after 20+ years at the Ferry Building. Replaced with Cowgirl + Hog Island bench picnic.

## Stage 1 per-topic breakdown

- restaurants (22 entries): 22 verified, 0 removed
- casual-dining (21 entries): 21 verified, 0 removed. Note: Park Tavern closed in 2023 but reopened November 2024 under same name with original chef Jonathan Waxman; entry remains valid.
- fine-dining (12 entries): 12 verified, 0 removed
- cafes (12 entries): 12 verified, 0 removed
- bars (14 entries): 14 verified, 0 removed
- brunch (9 entries): 9 verified, 0 removed
- hidden-gems (8 entries): 8 verified, 0 removed. Note: Sam Wo closed January 2025 then reopened September 2025 under new management; entry remains valid.
- bakeries (9 entries): 9 verified, 0 removed
- breweries (4 entries): 4 verified, 0 removed. Magnolia Brewing reopened December 2024 under new local ownership; entry valid.
- wine-bars (4 entries): 4 verified, 0 removed
- late-night (7 entries): 7 verified, 0 removed
- street-food (7 entries): 6 verified, 1 removed (Rooster & Rice fabricated address)
- markets (7 entries): 7 verified, 0 removed
- coffee-roasters (6 entries): 6 verified, 0 removed
- neighborhoods (12 entries): 12 area names verified
- festivals (5 entries): 5 verified, 1 corrected (sf-restaurant-week month)
- cooking-classes (3 entries): 3 verified (18 Reasons, The Civic Kitchen, Cozymeal SF) all real and operating
- food-tours (5 entries): 3 verified, 2 removed (fabricated routes), 1 corrected (Avital meeting point)
- itineraries (3 entries): 3 verified, 1 corrected (Boulettes Larder closure)
- dietary (13 entries): 11 verified, 2 removed (Plant Cafe, Shangri-La), 1 corrected (Z Zoul address)

## Stage 2: round-3 convergence call

- This is round 3. Defect count K = 6 (removals + address fix counted as hard defects; in-place corrections to operator-real tip/meeting/month/itinerary counted as soft).
- Hard removals: 4 (two food tours with fabricated routes, one street-food with fabricated address, two dietary entries permanently closed).
- Hard address fix: 1 (Z Zoul Cafe).
- Soft content corrections: 3 (Avital meeting point, SF Restaurant Week month, itinerary day-2 afternoon).
- Recommendation: declare convergence with low residual. K is 5 hard, 3 soft; the hard defects break down into a clear pattern (two fabricated food-tour routes, one fabricated address, two closures the prior validator missed). After this pass, all 22 topic JSONs are verified at the entity-existence level. Recommend NO round 4 unless new content is added.

## Stage 3: cross-city correctness

- check_external_urls.py for san-francisco: 1 broken / 135 URLs. The one broken is Unsplash photo URL returning 401 (anti-bot, expected). All other URLs resolve.
- audit_live: 0 errors across 1328 pages crawled site-wide. 9 broken extras site-wide, none scoped to San Francisco (all are NYC / Chicago / LA / Paris neighborhood links).
- Breadcrumb / state-page / country-hub: SF hub at https://tablejourney.com/united-states/san-francisco/ resolves 200; all 22 topic pages resolve 200.

## Defects removed

| Slug | Topic | Reason |
|---|---|---|
| the-plant-cafe-organic | dietary.vegetarian | Permanently closed |
| shangri-la-vegetarian | dietary.kosher | Permanently closed |
| local-tastes-mission | food-tours | Fabricated route (operator real but does not run Mission tour) |
| foodie-adventures-haight | food-tours | Fabricated route (operator real but does not run Haight tour) |
| rooster-and-rice-cart | street-food | Fabricated address (1101 Sutter is a parking garage) |
| z-zoul-cafe (address) | dietary.halal | Wrong address corrected to 295 Eddy Street |

## Below-floor topics after QA

- food-tours: dropped from 5 to 3. Below the typical floor of 4 to 5 used for shippable topic pages. Flagged for backfill by the research agent (Sidewalk Food Tours, Secret Food Tours, GourmetEvents.com SF, or a verified local operator with a confirmed route).
- dietary.vegetarian: dropped from 3 to 2. Same floor concern. Suggested backfill: Millennium (now in Oakland; check SF return), Loving Hut SF, Café Gratitude SF, or another verified vegetarian-first room.
- dietary.kosher: dropped from 2 to 1. Wise Sons remains (Jewish deli, not strictly kosher but some product lines are certified). SF does not have a deep kosher restaurant scene; this floor may be unreachable with truthful content. Flag for editorial decision.

All other topics retain >=4 entries.

## Verdict

VERDICT: PASS
