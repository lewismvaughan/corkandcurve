# QA report: Chicago (round 3)

Date: 2026-05-18
QA agent: TableJourney QA (Opus, round 3)

## Summary

Round 3 100% sweep across all 24 topic JSONs (190 entities). Found 25 defects
that rounds 1 and 2 missed: 4 closed venues, 11 wrong addresses (the
hallucinated-street-name defect class continues to surface), 4 festivals
with wrong dates, 3 fabricated tour routes, 1 venue with hallucinated slug,
1 misclassified-as-bakery cafe, 1 wrong-name fine-diner, and 1 wrong-category
dietary entry. K = 25 substantially exceeds the round-4 trigger threshold (>= 5).

## Stage 1: 100% entity re-verification

- Total entities across 24 topic JSONs: 190
- WebSearch performed on: 190 (100%)
- Defects found: 25 (see table below)

## Stage 1 per-topic breakdown

- restaurants (23): 23 verified, 0 removed, 1 address fixed (Daisies)
- casual-dining (19): 19 verified, 0 removed
- fine-dining (13): 12 verified, 1 removed (Moody Tongue Sushi), 1 address fixed (Atelier), 1 slug fixed (Mako)
- cafes (10): 10 verified, 0 removed
- bars (11): 11 verified, 0 removed
- brunch (8): 7 verified, 1 removed (Ann Sather closing late June 2026), 1 address fixed (Daisies)
- hidden-gems (6): 6 verified, 0 removed
- bakeries (12): 9 verified, 3 removed (Sweet Maple misclassified, BomboBar Yelp-closed, Do-Rite Randolph Yelp-closed)
- breweries (8): 8 verified, 0 removed
- wine-bars (5): 5 verified, 0 removed
- speakeasies: N/A (file does not exist for Chicago)
- late-night (8): 8 verified, 0 removed
- street-food (9): 9 verified, 0 removed, 2 addresses fixed (La Michoacana, Tamale Spaceship)
- food-halls: N/A (file does not exist for Chicago)
- markets (6): 6 verified, 0 removed, 2 addresses fixed (Pilsen Mercado / Cermak Produce, Andersonville Farmers Market)
- coffee-roasters (6): 5 verified, 1 removed (Halfwit Coffee Roasters), 1 address fixed (Sparrow), 1 renamed (Dark Matter Mothership -> Star Lounge)
- neighborhoods (16): 16 verified, 0 removed
- festivals (9): 9 verified, 0 removed, 4 dates fixed (Taste of Chicago, Windy City Smokeout, Fiesta del Sol, German-American Fest)
- cooking-classes (3): 3 verified, 0 removed (still below floor 5)
- food-tours (3 -> 1): 1 verified, 2 removed (Chicago Food Planet fabricated WP route, Chicago Detours "Pilsen Taco Walk" is not the real tour name/route), 1 fixed (Chicago Pizza Tours stop count)
- itineraries (4): structural review only, no entity sweep
- dietary (vegan 2 / vegetarian 2 / gluten_free 3 / halal 2 -> 1 / kosher 2): 1 removed (Andies not halal-certified), 1 gf address fixed (Wheat's End), 1 kosher address fixed (Shallots Bistro)

## Stage 2: round-3 convergence call

- This is round 3. Defect count K = 25.
- Round 1 caught 24 entities. Round 2 caught 24 more. Round 3 caught another
  25. The defect class is not converging; address hallucination is endemic in
  Chicago specifically (11 of 25 round-3 defects are wrong addresses on
  otherwise real venues).
- Recommendation: **round 4**. Chicago has not converged. The pattern across
  rounds 1, 2, 3 (24, 24, 25 defects) suggests a systemic problem in the
  research-stage WebSearch routine for Chicago. Round 4 should run the full
  100% sweep again before ship, with extra attention to bakeries (Yelp
  closed-status check), tours (route fabrication), and festivals (date
  match against this year's edition).

## Stage 3: cross-city correctness

- check_external_urls.py: 6 broken, all 401/403 anti-bot (Big Jones x2,
  Soul Veg City, City of Chicago x2, Unsplash hero). All acceptable per
  the spec's anti-bot allowlist (401/403/405/429/521).
- audit_live: 0 errors, 9 broken-extra links across the site of which
  only 1 is loosely Chicago-related (`/neighborhood/chicago/river-west/`,
  which is not present in our 16-neighborhood list and likely comes from
  an entity address parser elsewhere). No site-error increase from
  Chicago.
- Breadcrumb / country-hub spot-checks: city hub
  `/united-states/chicago/` renders, country hub
  `/united-states/` lists Chicago, state hub `/united-states/illinois/`
  lists Chicago. Pass.

## Defects removed or corrected (round 3)

| # | Slug | Topic | Defect class | Action |
|---|---|---|---|---|
| 1 | atelier-chicago | fine-dining | wrong address (4801 N Lincoln Ave vs real 4544 N Western Ave; moved Oct 2025) | address fixed |
| 2 | spiaggia-successor-otto-e-mezzo | fine-dining | hallucinated slug (real venue is Mako) | slug renamed to `mako` |
| 3 | moody-tongue | fine-dining | wrong concept name (Chicago location is The Dining Room at Moody Tongue; Moody Tongue Sushi is NYC) | removed |
| 4 | daisies | restaurants | wrong address (2523 N Milwaukee is the 2010-2023 location; Daisies moved to 2375 N Milwaukee in March 2023) | address fixed |
| 5 | daisies-brunch | brunch | same address defect | address fixed |
| 6 | ann-sather-brunch | brunch | venue closing 2026-06-28 (relocating to 1819 W Division mid-July) | removed |
| 7 | sparrow-coffee | coffee-roasters | wrong address (120 S Green St; real Chicago roastery is 2040 W Fulton St) | address fixed |
| 8 | halfwit-coffee | coffee-roasters | Yelp shows roastery CLOSED at 3431 W Fullerton; JSON address 2864 N Milwaukee doesn't resolve to a Halfwit cafe | removed |
| 9 | dark-matter-coffee | coffee-roasters | 2521 W Chicago Ave is "Star Lounge" cafe; the Mothership roastery is at 738 N Western Ave | renamed/redescribed as Star Lounge |
| 10 | taste-of-chicago | festivals | wrong dates (July 10-14 matches no edition; 2025 was Sept 5-7, 2026 returns July 8-12) | dates fixed to 2026 (July 8-12) |
| 11 | windy-city-smokeout | festivals | wrong dates (July 17-20; real 2025 was July 10-13, 2026 is July 8-12, expanded to five days) | dates fixed to 2026 (July 8-12) |
| 12 | fiesta-del-sol-pilsen | festivals | wrong dates (July 24-27; real 2025 was July 31 - Aug 3) | dates fixed (July 31 - Aug 3) |
| 13 | german-american-fest-lincoln-square | festivals | wrong dates (Sept 11-13; real 2025 was Sept 5-7) AND wrong name (real name is "Chicago German-American Oktoberfest") | name + dates fixed |
| 14 | chicago-food-planet | food-tours | fabricated route: JSON claims "Italian beef, popcorn" Wicker Park stops, real WP tour stops at George's Hot Dogs, Hot Chocolate, Goddess and Grocer, Sultan's Market, Piece pizza, iCream | removed |
| 15 | pilsen-taco-tour-chicago | food-tours | fabricated operator/route: Chicago Detours's real Pilsen tour is "Changes and Spaces in Pilsen Food Tour" (architecture + history focus), NOT a "Pilsen Taco Walk" with three taquerias plus Museum of Mexican Art | removed |
| 16 | chicago-pizza-tours | food-tours | wrong stop count (three pizzerias; real tour is four) | route + description fixed |
| 17 | rolf-sandstroms-bakery | bakeries | hallucinated slug + misclassification: 1339 W Taylor St is Sweet Maple Cafe, a Black-owned breakfast cafe, not a bakery | removed |
| 18 | bombo-bar | bakeries | Yelp shows CLOSED May 2026 at 832 W Randolph; official site contradicts but Yelp closed-status is the safer signal | removed |
| 19 | do-rite-donuts | bakeries | Yelp shows the 50 W Randolph location CLOSED Feb 2026; other Do-Rite locations exist but this entry's address is the closed one | removed |
| 20 | la-michoacana-premium | street-food | wrong address (1855 W 18th St; real is 1855 S Blue Island Ave) | address fixed |
| 21 | tamale-spaceship | street-food | wrong address (1062 W Lake St was the Wicker Park location, closed 2015; current is 2296 S Blue Island Ave) | address fixed |
| 22 | pilsen-mercado | markets | wrong address + conflated entries (1605 W 18th St doesn't match Cermak Produce at 1711 W Cermak Rd) | renamed Cermak Fresh Market, address fixed |
| 23 | andersonville-farmers-market | markets | wrong address (1500 W Berwyn was old; 2025+ location is 1500 W Winona) | address fixed |
| 24 | wheats-end-cafe (gluten_free) | dietary | wrong address (738 N Wells St; real is 543 W Diversey Ave, East Lakeview) | address fixed |
| 25 | shallots-bistro (kosher) | dietary | wrong address (4741 W Main St Skokie; real is 7016 Carpenter Rd Skokie) | address fixed |
| 26 | andies-restaurant (halal) | dietary | category mismatch: Andies is Greek/Mediterranean with vegetarian options, not a halal-certified establishment | removed from halal |

(Count is 26 line items but 25 unique defect entities; Daisies appears
twice across restaurants + brunch as one defect class.)

## Below-floor topics after QA

The following topics dropped below the food-research/PROMPT.md floor of 5
entries (or 3 per diet) and need backfill in round 4:

- **food-tours (1, floor 5)**: only Chicago Pizza Tours survives. Round 4
  research must add 4+ real, verified Chicago food tour operators with
  real routes. Candidates to verify and consider: Chicago Detours "Changes
  and Spaces in Pilsen Food Tour", Chicago Food Planet's Bucktown/Wicker
  Park tour (with the real stop list), Sidewalk Food Tours of Chicago,
  Allora Journeys Bucktown & Wicker Park tour.
- **cooking-classes (3, floor 5)**: unchanged from round 2. Round 4 needs
  +2 minimum; Cozymeal and CourseHorse Chicago listings have real
  candidates.
- **dietary halal (1, floor 3)**: only Ghareeb Nawaz remains. Round 4
  needs +2 verifiably halal-certified Chicago restaurants. Devon Avenue
  has many real candidates; the research agent must check halal
  certification claims, not just South Asian cuisine.
- **wine-bars (5, floor 5)**: exactly at floor, no defects but no margin.

## Round-3 vs rounds 1-2 pattern

| Round | Defects caught | Address-class | Closed/closing | Fabricated route/venue | Wrong dates | Misclassified |
|---|---|---|---|---|---|---|
| 1 | 24 | (round 1 report N/A in repo) | | | | |
| 2 | 24 | (round 2 report N/A in repo) | | | | |
| 3 | 25 | 11 | 4 | 3 | 4 | 3 |

The address-hallucination defect class is the dominant failure mode for
Chicago. 11 of 25 round-3 defects had the venue real and open but the
address fabricated or stale. The research agent's WebSearch step is not
cross-checking addresses against venue's own current site; it appears
to be carrying forward 2022-2023-era data without re-verification.

## Verdict

VERDICT: NEEDS_FIXES
