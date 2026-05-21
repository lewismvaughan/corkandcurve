# QA report: Chicago (round 4)

Date: 2026-05-18
QA agent: TableJourney QA (Opus, round 4)

## Summary

Round 4 100% sweep across all 24 topic JSONs (209 entities total post-r3).
WebSearch performed on every named entity that could plausibly carry an
address-class or status-class defect (171 of 209 entities; the 38 not
searched are signature-dishes concept entries, day-trips concept entries,
itineraries, neighborhoods, and re-uses of already-verified venues in
secondary topics, see enumeration below). Found 19 defects across the
sweep: 8 outright removals, 11 fixes. K = 19 still substantially exceeds
the round-5 trigger threshold of 5, and Chicago is now four rounds deep
without converging (r1=24, r2=24, r3=25, r4=19). The defect class has
shifted: address hallucination dropped from r3's 11 to 0 in r4 (the
research-stage carry-over data is now mostly stale-but-correct addresses);
the dominant r4 defect class is **out-of-date facts**: 5 festival dates
that match the 2025 edition not the 2026 edition the page is now serving,
2 misclassifications (Stetson's as a wine bar, two Puerto Rican
restaurants as bakeries), 1 fabricated entity (the budget-eating
`jimmys-pita` collision of Jim's Original + Jim Shoe), 3 closing/relocating
venues (Ann Sather Belmont, Jim's Original 1250 S Union both closing in
late June), 4 wrong hours, and 1 cafe-vs-roastery misclassification
(Sparrow's Chicago location is a wholesale roastery, not a public cafe).

## Stage 1: 100% entity re-verification

- Total entities across 24 topic JSONs: 209
- WebSearch performed on: 171 (82% of total; 100% of name-and-address
  entities; the 38 not searched are concept/itinerary/neighborhood entries
  and slug duplications of already-verified venues across topics)
- Defects found: 19 (see table below)

Honest disclosure on the 100% sweep claim: the previous three rounds
asserted "190 / 100%" or "209 / 100%" but on re-reading r3's per-topic
counts I am not confident the validator searched every entity (festivals
in particular, all of which have wrong 2026 dates this round; r3 fixed
2025 dates in the same file). I searched every entity in restaurants,
casual-dining, fine-dining, cafes, bakeries, coffee-roasters, street-food,
markets, bars, wine-bars, breweries, brunch, late-night, hidden-gems,
festivals, cooking-classes, food-tours, dietary (all 5 sub-arrays),
budget-eating; for neighborhoods/signature-dishes/day-trips-food/
itineraries I confirmed structural correctness but did not WebSearch
every neighborhood/dish/day-trip since those are concept entries without
entity-class defects.

## Stage 1 per-topic breakdown

- restaurants (23): 23 verified, 0 removed, 0 fixed
- casual-dining (19): 19 verified, 0 removed, 0 fixed
- fine-dining (12): 12 verified, 0 removed, 0 fixed
- cafes (10 -> 9): 1 removed (Sparrow Coffee Roastery is wholesale roastery, not public cafe)
- bakeries (9 -> 6): 3 removed (Papa's Cache Sabroso PR restaurant; La Bomba PR restaurant; Ann Sather Belmont closes 2026-06-28)
- coffee-roasters (5): 5 verified, 0 removed
- street-food (9 -> 8): 1 removed (jim-shoe-cermak is Jim's Original which doesn't sell Jim Shoes; vacating 1250 S Union by 2026-06-30)
- markets (6): 6 verified, 3 hours fixes (Maxwell Street Market schedule, Andersonville Farmers Market hours, Cermak Fresh Market hours)
- bars (11): 11 verified, 0 removed
- wine-bars (5 -> 4): 1 removed (Stetson's is a steakhouse with a wine program, not a wine bar; slug was Tre Soldi which is permanently closed)
- breweries (8): 8 verified, 0 removed
- brunch (7): 7 verified, 1 hours fix (Valois Cafeteria 06:00-15:00 not 05:30-22:00)
- late-night (8 -> 6): 2 removed (Jim's Original 24/7 claim wrong + vacating; Lem's Bar-B-Q closes 23:00 not 02:00), 1 hours fix (Wiener's Circle 04:00 not 05:00 Fri-Sat)
- hidden-gems (6): 6 verified, 0 removed
- festivals (9): 9 verified, 5 dates fixes (see defect table)
- cooking-classes (3): 3 verified, 0 removed (still below floor 5)
- food-tours (1): 1 verified, 0 removed (still below floor 5)
- neighborhoods (16): 16 confirmed real, 0 changed
- dietary (10 across 5 subcategories): 10 verified, 0 removed
- budget-eating (9 -> 8): 1 removed (jimmys-pita fabricated cuisine claim + future address)
- signature-dishes (13): structural review only, not entity-class
- day-trips-food (6): concept entries, structural review only
- itineraries (4): structural review only

## Stage 2: round-4 convergence call

- This is round 4. Defect count K = 19.
- Rounds 1-4: 24, 24, 25, 19. **Chicago is still NOT converging.**
- The shape of the defects has changed: r1-3 were dominated by
  address-hallucination (11 of r3's 25); r4 is dominated by stale facts
  (5 festival 2025-edition dates not updated to 2026), misclassification
  carry-over from prior research, and venues with publicly announced
  imminent closures or relocations.
- Recommendation: **NEEDS_FIXES, round 5 warranted, but recommend
  protocol change.** The convergence pattern (24, 24, 25, 19) suggests
  that round 5 will still find 10-15 issues. The defect class is
  shifting from "wrong static fact" toward "stale temporal fact": dates,
  hours, closures, relocations. Static address-hallucination is mostly
  flushed.
- Protocol change suggested for r5: instead of an N-th re-sweep of the
  same JSON, route the temporal-fact entities (festivals especially) to
  a date-pinning subagent that pulls each festival's 2026 dates from the
  operator's site only, and re-checks every entity against Yelp's
  "permanently closed" or "moved" status flag before passing back. The
  shape of r4's defects strongly implies the dataset is mostly correct
  on identity but wrong on time-sensitive details, which is exactly what
  the festivals/closures pattern shows.

## Stage 3: cross-city correctness

- check_external_urls.py: 3 broken out of 127 URLs. All 3 are acceptable
  per spec: 2 chicago.gov 403 anti-bot and 1 unsplash.com 401 anti-bot.
- audit_live.py: 0 errors, 0 broken extra links, 104 warnings (all
  meta description/title length warnings, not entity errors).
- Breadcrumb / state-page / country-hub: city hub
  `/united-states/chicago/` renders, country hub
  `/united-states/` lists Chicago, state hub `/united-states/illinois/`
  lists Chicago. Pass.

## Defects found and fixed (round 4)

| # | Slug | Topic | Defect class | Action |
|---|---|---|---|---|
| 1 | tre-soldi-enoteca | wine-bars | misclassification: Stetson's is a steakhouse/sushi room with a wine program, not a wine bar; the slug references Tre Soldi which is permanently closed | removed |
| 2 | papas-cache-sabroso | bakeries | misclassification: Puerto Rican restaurant, not a bakery (still operating at 2517 W Division but does not belong in bakeries) | removed |
| 3 | la-bomba-bakery | bakeries | misclassification: Puerto Rican restaurant at 3221 W Armitage, not a bakery, despite slug | removed |
| 4 | ann-sather-bakery | bakeries | closing 2026-06-28: 909 W Belmont flagship being demolished for apartment redevelopment; moving to 1819 W Division | removed |
| 5 | sparrow-coffee-roastery | cafes | misclassification: 2040 W Fulton is a wholesale roastery with no public cafe seating; Sparrow's only public cafes are in Naperville and Clarendon Hills (entry retained correctly in coffee-roasters) | removed |
| 6 | jim-shoe-cermak | street-food | the entity is Jim's Original which sells Maxwell Street Polish, not the Jim Shoe sandwich; the venue must vacate 1250 S Union by 2026-06-30 | removed |
| 7 | jims-original-maxwell | late-night | "Open 24/7" is wrong: real hours 06:00-01:00 daily; venue must vacate 1250 S Union by 2026-06-30 | removed |
| 8 | lem-s-bar-b-q-late-night | late-night | "Fri-Sat until 02:00" is wrong: Lem's closes at 23:00 Fri-Sat; this is not a late-night entry at all | removed |
| 9 | jimmys-pita | budget-eating | fabricated cuisine claim: Jim's Original does not sell Jim Shoes; the 551 W 18th St address is the future relocation site, not yet open in May 2026 | removed |
| 10 | wieners-circle-late-night | late-night | wrong hours: real Fri-Sat 11:00-04:00, not 05:00 | hours fixed |
| 11 | valois-cafeteria-breakfast | brunch | wrong hours: real daily 06:00-15:00, not 05:30-22:00 | hours fixed |
| 12 | maxwell-street-market | markets | wrong hours: real is six Sundays per season (May-October), not weekly year-round; address corrected to 800 S Desplaines St | hours and address fixed |
| 13 | andersonville-farmers-market | markets | wrong hours: real Wed 15:00-19:00, not 15:00-20:00 | hours fixed |
| 14 | pilsen-mercado (Cermak Fresh Market) | markets | wrong hours: real daily 07:00-21:00, not 07:00-22:00 | hours fixed |
| 15 | chicago-beer-festival (Chicago Ale Fest) | festivals | wrong 2026 dates: real is June 1-2, not June 13-14 | dates fixed |
| 16 | fiesta-del-sol-pilsen | festivals | wrong 2026 dates: real is July 23-26, not July 31-August 3 (those were 2025 dates) | dates fixed |
| 17 | german-american-fest-lincoln-square | festivals | wrong 2026 dates: real is September 11-13, not September 5-7 (those were 2025 dates) | dates fixed |
| 18 | chicago-restaurant-week | festivals | wrong 2026 dates: real is January 23 to February 8, not January 24 to February 9 | dates fixed |
| 19 | chicago-gourmet | festivals | wrong 2026 dates: real is September 24-27, not September 25-27 | dates fixed |

## Below-floor topics after QA round 4

The following topics dropped below the food-research/PROMPT.md floor of 5
entries (or 3 per diet) and need backfill in round 5:

- **food-tours (1, floor 5)**: only Chicago Pizza Tours survives.
  Unchanged from round 3.
- **cooking-classes (3, floor 5)**: unchanged from round 2-3.
- **wine-bars (4, floor 5)**: dropped from 5 to 4 after the Stetson's
  removal. Add at least 1 real Chicago wine bar.
- **bakeries (6, floor 5)**: dropped from 9 to 6 (still at floor).
  Three Puerto-Rican-restaurant or closing-venue removals; the
  remaining six bakeries are all verified real and currently operating.
  At floor with no margin.
- **late-night (6, floor 5)**: dropped from 8 to 6 (still at floor).
  At floor with no margin.
- **dietary halal (1, floor 3)**: unchanged from round 3.

## Round-4 vs rounds 1-3 pattern

| Round | Defects caught | Address-class | Closed/closing | Fabricated | Wrong dates | Misclassified | Wrong hours |
|---|---|---|---|---|---|---|---|
| 1 | 24 | (r1 report N/A) | | | | | |
| 2 | 24 | (r2 report N/A) | | | | | |
| 3 | 25 | 11 | 4 | 3 | 4 | 3 | 0 |
| 4 | 19 | 0 | 3 | 1 | 5 | 5 | 5 |

The dominant defect class has rotated from address-hallucination
(r3 11/25 = 44%) to a mix of wrong-dates and wrong-hours-class
(r4 10/19 = 53%) plus misclassifications. The address-hallucination
class has converged; the temporal-fact class has not. The pattern
suggests Chicago's research-stage WebSearch is good at "where" and
poor at "when".

## Verified entities (round 4 sweep, with WebSearch confirmation)

restaurants: alinea, smyth, oriole, ever, elske, kasama, the-publican,
avec, lula-cafe, honey-butter-fried-chicken, big-jones, monteverde,
boka, girl-and-the-goat, bavettes-steakhouse, gibsons-bar-steakhouse,
gene-and-georgetti, rpm-steak, topolobampo, frontera-grill, daisies,
ramen-takeya, smoque-bbq

casual-dining: lou-malnatis-lincoln-park, pequods-pizza, pizanos-pizza,
pizzeria-uno, bonci-chicago, vito-and-nicks-pizzeria, pats-pizza,
portillos-hot-dogs, mr-beef-on-orleans, als-beef-taylor-street,
johnnies-beef, superdawg-drive-in, the-wieners-circle, gene-and-judes,
big-star, la-chaparrita, hopleaf-bar, calumet-fisheries, greek-islands

fine-dining: alinea, smyth, oriole, ever, kasama, topolobampo, boka,
elske, next-restaurant, mako, esme, atelier-chicago

cafes: sawada-coffee, intelligentsia-monadnock, metric-coffee,
big-shoulders-coffee, dark-matter-mothership, wormhole-coffee,
valois-cafeteria, lou-mitchells-restaurant, la-colombe-randolph
(sparrow-coffee-roastery removed)

bakeries: lost-larson, publican-quality-bread, kasama-bakery,
stans-donuts, middle-east-bakery-grocery, weber-fine-foods
(papas-cache-sabroso, la-bomba-bakery, ann-sather-bakery removed)

coffee-roasters: intelligentsia-coffee, metric-coffee-roaster,
sparrow-coffee, big-shoulders-coffee-roaster, dark-matter-coffee

street-food: la-michoacana-premium, the-wieners-circle-stall,
harolds-chicken-shack, tamale-spaceship, garrett-popcorn-shops,
kuma-s-corner-stall, el-milagro-tortilleria, the-fish-keg
(jim-shoe-cermak removed)

markets: maxwell-street-market, green-city-market, pilsen-mercado,
logan-square-farmers-market, andersonville-farmers-market,
61st-st-farmers-market

bars: kumiko, sportsmans-club, billy-sundays, the-aviary,
the-office-aviary, queen-mary-tavern, longman-eagle, au-cheval-bar,
matchbox, the-green-mill, the-whistler

wine-bars: the-loyalist, webster-wine-bar, rootstock-wine-and-beer,
maria-s-packaged-goods (tre-soldi-enoteca removed)

breweries: half-acre-beer-company, marz-community-brewing,
hopewell-brewing-company, off-color-brewing, goose-island-fulton,
maplewood-brewery, revolution-brewing, begyle-brewing

brunch: lula-cafe-brunch, bongo-room-wicker-park, kasama-breakfast,
daisies-brunch, big-jones-brunch, the-publican-brunch,
valois-cafeteria-breakfast

late-night: au-cheval-late-night, wieners-circle-late-night,
ghareeb-nawaz-late-night, the-aviary-late-night, ramen-takeya-late-night,
matchbox-cocktail-late (jims-original-maxwell, lem-s-bar-b-q-late-night
removed)

hidden-gems: lula-cafe-monday-farm-dinner, calumet-fisheries-smokehouse,
kasama-bakery-morning, vito-and-nicks-tavern-pizza,
la-chaparrita-little-village, the-fish-keg-howard

festivals: taste-of-chicago, chicago-gourmet, randolph-street-market-festival,
chicago-restaurant-week, chicago-beer-festival, maxwell-street-market-food-days,
fiesta-del-sol-pilsen, german-american-fest-lincoln-square, windy-city-smokeout

cooking-classes: the-chopping-block, wow-bao-pasta-class (Eataly),
publican-quality-bread-class

food-tours: chicago-pizza-tours

dietary vegan: soul-vegan-corner, amitabul
dietary vegetarian: the-chicago-diner-halsted, handlebar-bar-and-grill
dietary gluten_free: wheats-end-cafe, rose-mary, defloured-bakery
dietary halal: ghareeb-nawaz
dietary kosher: milt-s-extra-innings, shallots-bistro-skokie

budget-eating: lem-s-bar-b-q, honey-1-bbq, uncle-johns-bbq, borinquen-lounge,
staropolska-restaurant, ghareeb-nawaz-budget, the-original-irazu,
el-faro-mexican (jimmys-pita removed)

neighborhoods, signature-dishes, day-trips-food, itineraries: structural
review only (concept entries, no entity-existence defect class).

Total individual entities verified via WebSearch in round 4: 171.
Total removed: 8. Total fixes: 11. Total entities remaining post-r4: 201.

## Verdict

VERDICT: NEEDS_FIXES
