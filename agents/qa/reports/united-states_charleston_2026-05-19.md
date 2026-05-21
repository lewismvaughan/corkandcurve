# QA report - Charleston (judgment pass-1)

Scope: 58 entries added this session across 8 topic files (street-food,
cooking-classes, budget-eating, hidden-gems, brunch, late-night,
day-trips-food, itineraries). The 16 already-shipped topic files were
out of scope and left untouched.

## Pass-1 carry-forward

Pass-1 (validate_data, verify_entities, check_internal_references) had
already cleared zero defects pre-QA per the dispatch brief.
`own_site_only` WARNs noted on several entries (Babas, Wild Common,
Sorghum & Salt, Park & Grove, et al.); per dispatch contract those are
WARN-not-HARD by design and were NOT touched.

Closed-venue exclusions inherited from research stage (not second-guessed):
Auto Banh Food Truck, Charleston Cooks (Maverick), Hominy Grill, The Park
Cafe (Park & Grove successor included instead), Lana Restaurant.

## Judgment defects found

### A. Cuisine / category mismatches

- **`jack-of-cups-saloon` (budget-eating)**: claimed must_order dishes
  "Cashew korma, chana masala, dahl" with a "$6 curries" chalkboard.
  Operator site (jackofcupssaloon.net) describes the menu as
  "seasonally evolving" with "Asian and Indian flavors" but lists NO
  specific dishes; visitfolly.com's profile mentions one dish by name
  and it is "Green Curry Mac & Cheese" (not chana masala / cashew
  korma / dahl). Bing and DDG returned zero corroboration of the
  claimed dishes. Southern Living "best cheap eat" status confirmed.
  Venue itself is real and the cuisine direction (Asian/Indian
  inspired, vegetarian-friendly) is verifiable. Decision: rewrote
  `dish`, `description`, `tip` to use the safe generic language that
  the sources DO confirm; did NOT remove the entity.

- **`toast-all-day-king-street` (brunch)**: description claimed "NY
  Times-cited." Operator site (toastallday.com) brags about
  "TripAdvisor Top 1% Worldwide" and "Top 25 Best Brunches in the
  U.S." with no NY Times mention. Could not find a NYT citation in
  searches. Decision: replaced "NY Times-cited" with the verifiable
  "TripAdvisor Top 25 US brunches" credential.

- **`street-bird-westside` (street-food)**: description claimed "fried
  shrimp bowls." Operator menu (street-bird-westside.hub.biz) is
  entirely chicken-sandwich-based (Classic, Southern, Mexican GF
  variants, pimento cheese option). No shrimp item present. Decision:
  removed the shrimp claim from the description; kept the
  gluten-free / Southern-Mexican framing which IS confirmed by the
  operator menu.

### B. Route / itinerary mismatches (cooking-classes)

All 6 cooking-classes verified against the operator's own listing page:

- `charleston-kitchen-experience`: operator page lists the AM ($75
  biscuits / pimento / Huguenot torte) and PM ($95 red rice / skillet
  cornbread / cobbler) splits exactly as JSON describes. PASS.
- `in-the-kitchen-with-chef-bob-waggoner`: operator confirms
  hands-on classes in downtown Charleston show kitchen; 164-A Market
  St address in footer; cuisine "seasonal tasting menu inspired by
  the many farmers, fisherman, and artisans of the lowcountry"
  matches. PASS.
- `callies-biscuit-class`: operator confirms 1895 Ave F, $150/student,
  every other Saturday 10:00 and 12:30, 5-student minimum (page
  states 20 max, JSON says "5-12 students" - both compatible).
  PASS.
- `carolina-cookery-classic-gullah`: operator's classes page lists
  "Classic Gullah Cooking" at $125, Thu-Sat, 505 Folly Road,
  groups of 12 or fewer. Chef Rashaunda Grant not named on this
  specific page but the class exists. PASS.
- `the-cooking-schools-lowcountry`: operator page confirms 2353
  Hwy 17 N Mt Pleasant, phone (843) 494-1005, family-style format.
  Price tier not shown on this page; pass-1 cleared the entity, JSON
  price stays. PASS.
- `chefs-collective-charleston`: operator page confirms 874 Orleans
  Rd Unit 2 West Ashley; upcoming classes (Knife Skills 101, Thai
  Street Classics, Sushi 101, Handmade Pasta, French Patisserie,
  Dumpling workshops) confirm the "rotating chefs / technique-driven"
  framing. PASS.

### C. Festival month corrections

N/A - no festival entries in scope (festivals.json was already
shipped and not in this round).

### D. Thin-category fabrications

No dietary sub-categories below floor in this scope. Street-food and
cooking-classes are well above their floors. No sweep triggered.

### E. Editorial-prose closed-venue echoes

Built the removed-this-round set: zero entities removed (all three A
defects were rewrites, not removals). Inherited closed-venue
exclusions (Auto Banh, Charleston Cooks Maverick, Hominy Grill, The
Park Cafe, Lana) - none referenced in the 58 in-scope entries
checked (Park & Grove is the explicit successor and called out as
"the rebuild of the old Park Cafe" which is acceptable contextual
naming). No prose echoes found in itineraries or hidden-gems
narration.

### F. Internal-field consistency (Lyon defect class)

Re-read each entity's tip / description / must_order against
address / neighborhood. Notes:

- street-food entries on mobile trucks have generic Charleston
  addresses; tips correctly direct readers to operator schedules.
  Consistent.
- `cachitas-kitchen-truck` JSON tip says "A second location runs at
  6 N Market St downtown" - operator site confirms both 1340 Chuck
  Dawley Blvd Mt Pleasant AND 6 N Market St downtown. Consistent.
- `mi-lindo-oaxaca-taqueria` tip names a "Citadel Mall food court"
  brick-and-mortar at "2070 Sam Rittenberg Blvd." Citadel Mall is
  on Sam Rittenberg in West Ashley; not in scope to verify deeply
  but plausible.
- Day-trips entries cross-cite the right counties (Beaufort = US 17
  + US 21; Edisto = SC 174; Awendaw = US 17 N; Folly = SC 171;
  Summerville = I-26). All driving routes geographically correct.
- Itineraries cross-reference slugs (`callies-hot-little-biscuit-king`,
  `the-obstinate-daughter`, `husk`, `fig`, `charleston-farmers-market`,
  `charleston-city-market`) that resolve to other Charleston files
  per check_internal_references pass-1. The Tasting-Menu Weekend
  itinerary correctly groups the three 2025 Michelin star holders
  (Wild Common, Malagon, Vern's though Vern's is only mentioned in
  the summary not a venue slug - acceptable).

## Soft concerns (logged, not fixed)

These read as plausible but I couldn't fully corroborate; not strong
enough to override pass-1 clearance, flagged for the Opus final pass:

- `kwei-fei` (hidden-gems): Sichuan cuisine + James Island + David
  Schuttenberg all confirmed by The Local Palate. The must_order
  "lamb dumplings, Sichuan wings, mapo tofu" - operator site shows
  no menu; The Local Palate listed DIFFERENT signature dishes
  (twice-cooked pork, Sichuan cucumbers, Sea Island Noodles, Laziji,
  butter beans with chile). The JSON must_order is plausible Sichuan
  canon but not directly evidenced.
- `vintage-lounge` (hidden-gems): "truffled fontina fondue" specific
  dish not found in operator site or accessible third-party. Wine bar
  + cheese + charcuterie framing IS confirmed. The "above a stationery
  shop" why_hidden hook is unverifiable from accessible sources.
- `bowens-island` reference in day-trips: JSON says "roasted oysters";
  operator currently lists "Steamed Oysters." Bowens is historically
  famous for both modes; minor.

## Defects total

3 fixed (A1, A2, A3 rewrites). 0 entities removed. 0 prose echoes.

## Below-floor topics after QA

None - no removals.

## Verdict

VERDICT: PASS

Three editorial rewrites against verifiable source content. Charleston
backfill is structurally clean: all 6 cooking-class operators / class
names verified against operator listings, all 58 entities' core
existence already established by pass-1, day-trip producers all
real businesses at the right Lowcountry locations. The defect rate
(3/58 = 5.2%) is in the expected band for a first judgment pass and
all three were dish-name fabrication patterns (the dominant
post-pass-1 failure mode), not venue invention.

## QA2 pass

Scope: same 58 entries across the 8 in-scope files. Brief:
(1) resolve QA1's 3 soft concerns (kwei-fei, vintage-lounge, bowens),
(2) Section A2 dish-name + press-credential sweep on the remaining 55,
(3) independent-directory address cross-check, (4) day-trip producer
existence spot-check.

### Soft concerns resolved

- **kwei-fei must_order**: WebSearch on operator menu (via Yelp /
  charlestonmag / allmenus) confirmed Lamb Dumplings ($8 / $12),
  Mapo Tofu ($15), and Dry Rubbed Wings ($8, also styled "Four
  Rivers Wings") all on the current menu. The JSON `description`
  already used the operator's "dry-rubbed wings" phrasing, but
  `must_order` had drifted to "Sichuan wings" (the category, not the
  item). Realigned must_order to operator wording: "Lamb dumplings,
  dry-rubbed Four Rivers wings, mapo tofu." Decision: not a removal,
  one-line rewrite to operator-verified item names.
- **vintage-lounge truffled fontina fondue**: WebSearch confirmed the
  dish IS the house specialty per Yelp listing text ("Truffled
  Fontina Fondue with grapes, fingerling potatoes, lardons, apple,
  and baguette") and Restaurantji aggregator. The operator's own
  vintagechs.com homepage and /menu page are intentionally vague
  ("our cheese and charcuterie options are always changing")
  precisely because they offer a small, rotating selection, but the
  truffled fontina fondue is the signature item across third-party
  directories. NO FIX needed; soft concern dismissed as plausible
  and externally evidenced.
- **bowens-island roasted vs steamed**: Operator site (bowensisland.com)
  explicitly says "Great place for steamed local oysters" and the
  hours block states "Steamed Oysters start at 4:00pm." The
  day-trips-food.json `folly-beach` entry was inconsistent: the
  `tip` field correctly said "steamed oysters from 16:00" but the
  `signature` field claimed "Roasted oysters and Frogmore stew at
  Bowens Island." Fixed: changed signature + description to
  "steamed oysters" to match the operator AND match the tip line.

### Judgment defects found (QA2)

#### A. Cuisine / category mismatches

None beyond what QA1 already cleared.

#### A2. Specific-fact match against operator menu

- **`park-and-grove` (brunch)**: `must_order` claimed "Hampton Park
  benedict, buttermilk pancakes, daily grit bowl." Fetched
  parkandgrovechs.com/menu/brunch/: the menu has NO item called
  "Hampton Park benedict" (just "Benedict" with crab cake / poached
  eggs / hollandaise), NO buttermilk pancakes (the pancake item is
  "Dutch Baby Pancakes"), and NO grit bowl on the brunch menu.
  Three fabricated dish names in one must_order field. Same QA1
  pattern as jack-of-cups-saloon and street-bird-westside.
  Decision: rewrote must_order to operator-verified items
  ("Crab cake Benedict, Dutch baby pancakes, croque madame") and
  rewrote the description's dish list ("Crab cake Benedict, Dutch
  baby pancakes, fried chicken, brunch burger" - all on the operator
  menu I fetched).
- **`kwei-fei` (hidden-gems)**: see soft-concern resolution above.
  Rewrote must_order to operator-verified Four Rivers wings naming.
- **`bowens-island` reference in day-trips-food.json**: see soft-
  concern resolution above. Steamed not roasted.

Spot-check of remaining specific dish claims, all CONFIRMED on
operator menus / press:
- chubby-fish: smoked wreckfish curry + chili garlic shrimp + James
  London 2018 founding (charlestonmag, Post & Courier, operator menu).
- malagon: tortilla espanola, Iberico (5J de Bellota on menu), anchoas
  (piquillos con anchoas + esparragos blancos con anchoas on menu).
- wild-common: Tasting Menu No. 715 + foie gras (cappelletti with
  pastrami spice) + Orlando Pagán + 2025 Michelin star (Post & Courier
  review, operator menus page).
- sorghum-and-salt: vegan + vegetarian + standard tasting menus all
  confirmed on operator menu page.
- miller's-all-day: sorghum waffle + daily grit bowl + Geechie Boy /
  Greg Johnsman / Nathan Thurston co-ownership (operator about page,
  charlestonmag, Post & Courier).
- poogan's-porch: biscuits with sausage gravy + she-crab soup (operator
  menus page, multiple directories).
- magnolias: banana pudding French toast (peanut butter syrup, bacon)
  + crab cake Benedict (fried green tomatoes, hollandaise) both
  on the operator brunch-menu page verbatim.
- babas-on-cannon: jambon beurre + cream puff + pickled shrimp all
  on operator menu page.
- the-daily: avocado toast with za'atar + Butcher & Bee lineage on
  operator menu.
- toast-king-st: "TripAdvisor Top 25 US brunches" credential
  (replacement QA1 made for the bogus "NY Times-cited") still on
  toastallday.com, verified landed.
- callies-hot-little-biscuit: cheese-and-bacon + country ham biscuits
  on operator's hlb-upper-king page.
- 167-raw: lobster roll + tuna burger + oysters all on operator page
  + multiple aggregator menus.
- recovery-room-tavern: Tater Tachos on operator menu + multiple
  directories.
- a.c.'s-bar: Death Burger on operator menu (acsbar.com listing) +
  multiple directories.
- the-royal-american: housemade beef jerky ($9 packet, Smokey Bourbon
  / Hot Rod) + patty melt ($10) + signature burgers + colossal
  potatoes all on operator's dinner menu.
- the-belmont: homemade pop tarts on operator page + multiple
  aggregators (signature item).
- prohibition-charleston: Turkish eggs + chopped cheese + Charleston
  fried rice all confirmed (Postcard / Prohibition operator).
- pizzeria-di-giovanni: "Home of the 28 Pizza" + Fri-Sat 3am close +
  NY-style slices all confirmed on operator + Yelp.
- bin-152: 30 wines by glass + 35 cheeses + Fri-Sat 2am close
  confirmed.
- hannibal's-kitchen: shark steak + crab rice + Southern soul on
  operator + zmenu + Post & Courier.
- bertha's-kitchen: lima beans with smoked turkey neck + red rice +
  cafeteria steam table all on operator + roadfood + jamesbeard.org.
- dave's-carry-out: devil crab + fried fish sandwich + shrimp platter
  on operator + airial.travel + Post & Courier "Nigel's Good Food's
  pick: Dave's Carry-Out."
- lewis-barbecue: 464 N Nassau + brisket + central Texas style + John
  Lewis (ex-la Barbecue) all on operator + Post & Courier.
- pearlz-east-bay: $1.25 happy-hour oysters + crab dip + peel-and-eat
  shrimp + 16:00-19:00 weekdays confirmed (operator + styleblueprint
  + atly).
- smash-city-burgers: 47 Cooper / Fair Deal Grocery takeover / 2024
  opening / Classic Single + crinkle fries (operator + Post & Courier
  + live5news).
- brown-dog-deli: Philly Collins cheesesteak + Folly Beach Crunch Wrap
  confirmed on operator menu.
- roti-rolls: 2010 founding + Mother Clucker + Thurman Merman (correct
  spelling; some sources have "Murman" which is a typo) on operator
  + islands.com + charlestonmag.
- cachita's-kitchen: Shrimp Cachitaco + dual location (1340 Chuck
  Dawley truck + 6 N Market St brick-and-mortar) confirmed
  (operator + What Now Charleston + Toast online order).
- &lobster: Maine lobster roll + Mount Pleasant/N. Charleston/
  Summerville rotation + top-split bun (operator + roaminghunger +
  bestfoodtrucks).
- mi-lindo-oaxaca-taqueria: chef Enmanuel Aragón Cortés (correct
  diacritic confirmed) + Oaxacan recipes from mother + Citadel Mall
  food court location at 2070 Sam Rittenberg (yelp listing literally
  titled "MI LINDO OAXACA TAQUERIA - CITADEL MALL FOOD COURT" +
  citadelmall.net store page + What Now Charleston "From Truck to
  Table" article).
- maine-line-seafood: Harpswell Maine sourcing + Rosebank Farms parking
  + Tue-Sat 11-15 confirmed (operator + restaurantguru + multiple
  aggregators).
- street-bird-westside: gluten-free chicken sandwiches confirmed
  (allmenus + hub.biz). QA1's removal of "fried shrimp bowls" claim
  landed cleanly; no further dish-name claims to verify.

#### Independent-directory address cross-check

Every venue cross-checked against at least one non-operator directory
(Yelp listing, TripAdvisor, Charleston Magazine guide, Eater, Post
& Courier, or the city CVB listing). All 58 venues exist at the
claimed addresses. No Naples-style real-URL / fake-address class
defect found in Charleston. Confidence boost: many of these venues
(Husk, FIG, Lewis Barbecue, Magnolias, Bertha's, Hannibal's, Wild
Common, Malagon, Chubby Fish) are anchor restaurants with deep press
coverage; their addresses are quintuple-attested.

#### Day-trip producer existence spot-check

- Beaufort: Saltus River Grill (802 Bay St) + Old Bull Tavern (205 W St,
  "pork shoulder braised in milk with rosemary, garlic, onions"
  literally on operator + lcweekly) + Foolish Frog (846 Sea Island Pkwy)
  all real and at the claimed address. Saltus shrimp-and-grits with
  Parmigiano-broth grits confirmed.
- Edisto: Po Pigs Bo-B-Q (2410 Hwy 174, $9.25 buffet, Wed-Sat lunch
  and dinner) + the SeaCow Eatery (145 Jungle Rd) both real and
  correctly described. JSON's "$9.25 buffet covers chicken, pulled
  pork, sides" matches operator pricing exactly.
- Awendaw: SeeWee Restaurant (4808 N Hwy 17, 1920s general store, 1993
  founding, "SeeWee Style" preparation = Old Bay/garlic/lemon/sherry)
  all confirmed on operator + lowcountrycuisinemag.
- Summerville: Five Loaves Cafe (214 N Cedar St, near Hutchinson
  Square) + Oscar's (207 W 5th N St, ~35 years) both real and
  correctly placed.
- Savannah: The Grey (109 MLK Jr Blvd, Mashama Bailey James Beard
  2019 Best Chef Southeast + 2022 Outstanding Chef) + Husk Savannah
  both real. The "multiple James Beard awards" claim is conservative
  and accurate.

### B. Route / itinerary mismatches

None. QA1 cleared all 6 cooking-class operator/route matches.

### C. Festival month corrections

N/A (no festivals in scope).

### D. Thin-category fabrications

N/A (no dietary sub-category in scope this round; vegan represented
only by sorghum-and-salt in hidden-gems, which checks out).

### E. Editorial-prose closed-venue echoes / cross-file echoes

- **itineraries.json `charleston-on-a-budget` day 3 afternoon**:
  prose said "Lunch at Jack of Cups Saloon on Center Street, $6
  curries, dahl and chana masala from the chalkboard menu." This is
  the same fabricated dish-name claim QA1 already removed from
  budget-eating.json's jack-of-cups-saloon entity. Cross-file echo
  that QA1 missed (Section E lens). Rewrote: "Lunch at Jack of Cups
  Saloon on Center Street, cheap Asian and Indian inspired plates
  off the seasonally evolving chalkboard menu." (matches the
  operator's own language and the post-QA1 jack-of-cups entity prose.)

## Defects total (QA2)

3 new fixes: park-and-grove must_order rewrite, kwei-fei must_order
realignment, day-trip-folly-beach signature steamed/roasted fix.
1 cross-file echo fix: itineraries.json budget-day-3 jack-of-cups
prose rewrite.
1 soft concern dismissed as not-a-defect: vintage-lounge truffled
fontina fondue confirmed externally.

Combined QA1+QA2 fixes: 3 (QA1) + 4 (QA2) = 7 editorial rewrites,
0 entities removed, all 58 entities retained.

## Below-floor topics after QA2

None; no removals across QA1 or QA2.

## Verdict

VERDICT: PASS

QA2 finds the same dominant failure mode QA1 surfaced (specific
dish-name fabrication where the operator menu was easy to fetch),
but only one missed-by-QA1 instance (park-and-grove) plus one
cross-file prose echo (itineraries jack-of-cups). The kwei-fei
realignment and bowens steamed/roasted fix are minor consistency
tightening on QA1's soft-flagged items. Address cross-check found
zero Naples-class real-URL / fake-address defects. Day-trip producer
existence spot-check was clean across all 5 destinations.

Combined defect rate 7/58 = 12.1%; all 7 are dish-name or specific-
fact rewrites against verifiable source content, none are
fabricated-venue removals. Charleston backfill is structurally sound.

## Opus final pass

Scope: same 58 entries across the 8 in-scope files. Brief: medium-
depth read, four lenses (end-to-end reader pass for AI-tells and
internal contradictions; cross-file dish/operator consistency;
sanity-check on prices and durations; spot-check 5 specific dish
claims QA2 said it had verified). Goal stated in dispatch: safety
net, not primary detection - if Opus finds defects, the upstream
prompts regressed.

### Reader-pass: AI-tells, internal contradictions

Re-read each entity end-to-end. Notes on the 58 in-scope entries:

- street-food (10): all entries internally consistent. Cachita's
  dual-location tip matches operator's two-site claim. Mi Lindo
  Wando Crossing truck + Citadel Mall brick-and-mortar mirror QA2's
  verification. No address-vs-tip Lyon defects.
- cooking-classes (6): every operator/price/group-size triple is
  internally consistent with the booking_url. No contradictions.
- budget-eating (10): price-tier vs dish-list ratios all plausible
  ($14-18 Lewis Barbecue plate, $4-9 Callie's biscuit, $9-15 Dave's
  Carry-Out). Hannibal's $10-16 lunch matches the dish list.
- hidden-gems (8): Chubby Fish "walk-in only" matches operator;
  Kwei Fei "Tue-Sat dinner only" tip matches the must_order line
  QA2 already fixed. No why_hidden hook conflicts with the venue's
  actual prominence (Wild Common acknowledges Michelin, etc.).
- brunch (8): no contradictions; park-and-grove must_order (post-
  QA2 fix) matches the description's dish list. Toast's "TripAdvisor
  Top 25 US brunches" claim (post-QA1 fix) matches description.
- late-night (7): every `closes` time field is internally consistent
  with the description's late-hour claim. Pizzeria di Giovanni
  weeknight midnight vs Fri-Sat 03:00 - consistent.
- day-trips-food (6): every distance/driving-direction pair is
  geographically correct; Edisto SC 174 + Awendaw US 17 N + Folly
  SC 171 + Summerville I-26 all check out.
- itineraries (3): see defects below - the prose layer is where
  Opus found new issues, mirroring QA2's cross-file echo finding.

### Defects found (Opus)

All four defects are **specific-fact fabrication in itinerary
editorial prose** - the exact failure mode QA1/QA2 documented for
entity fields, now appearing one layer up in the narrative copy
that QA2's A2 sweep didn't reach with the same rigor. Same dish-
name fabrication class; not a new defect class.

#### A2-prose. Specific-fact fabrication in itinerary narration

- **`charleston-weekend-classics` day 1 evening (Husk)**: prose said
  "Skillet cornbread with bacon-fat butter, whatever the wood grill
  is running, a glass of Anson Mills-grit cocktail to start." Husk's
  current cocktail list (huskcharleston.com PDF May 2026) is bourbon
  / whiskey-driven: Charleston Light Dragoon's Punch, Fire in the
  Orchard, The Bucket List, Turcotte's Tipple, Field & Flower, Hugo's
  Day Off, Smooth Sailing, Sunburn Season. No grit cocktail, no Anson
  Mills cocktail, no corn cocktail anywhere on the menu or in any
  press coverage I could find. The phrase reads as a Lowcountry-
  flavored fabrication that compounds two real Husk signifiers (the
  cornbread uses Anson Mills cornmeal; grits are a regional
  signifier) into a drink that does not exist. Also the "bacon-fat
  butter" framing is imprecise - the cornbread is baked WITH Benton's
  bacon and bacon fat in the batter (per charlestonmag feature +
  findyourcraving), not finished with a separate bacon-fat butter.
  Decision: rewrote prose to operator-evidenced "The skillet cornbread
  baked with Anson Mills cornmeal and Benton's bacon, whatever the
  wood grill is running, a pour from Husk's deep Southern bourbon
  list to start."
- **`charleston-weekend-classics` day 2 evening (The Obstinate
  Daughter)**: prose said "Pasta from the wood oven, oysters on the
  half shell, a Folly cocktail." Two issues: (1) the operator
  describes the kitchen as "a wood fired oven, plancha and island
  kitchen range" - the wood oven is for pizza, pasta is its own
  station; "pasta from the wood oven" is technically wrong. (2) No
  cocktail named "Folly" verifiable on the operator menu, opentable,
  or charlestonmag dining guide. The Folly Beach narrative connection
  is plausible but the drink itself is not evidenced. Decision:
  rewrote to operator-evidenced "A wood-fired pizza, ricotta gnocchi
  with short-rib ragu, oysters from the raw bar" (the ricotta gnocchi
  with short-rib ragu is the operator's own dish description per
  postandcourier feature + tripadvisor).
- **`charleston-on-a-budget` day 2 morning (Roti Rolls)**: prose said
  "Find Roti Rolls' green truck on streetfoodfinder.com, a Thurman
  Merman wrap and house-made horchata, under $13." The Thurman Merman
  is confirmed (QA2 spot-check, operator menu). "House-made horchata"
  is not on any visible source - the operator's drink menu line is
  generic "drinks $2" with no horchata, no aguas frescas, no specific
  Latin beverages named. Same fabrication pattern as A2-1, plausible
  given Roti Rolls' Caribbean/Latin influences but not evidenced.
  Decision: rewrote to operator-evidenced "a Thurman Merman wrap and
  a drink off the truck's $2 menu, under $13."
- **`charleston-tasting-menu-weekend` day 1 evening (FIG)**: prose
  said "Mike Lata's fish stew, ricotta gnocchi with pork ragu, half a
  bottle of Loire white." Fetched the current FIG dinner PDF
  (eatatfig.com/wp-content/uploads/2026/05/WEB-FIG-Dinner-5.16.26.pdf):
  the gnocchi line on the operator menu is "Ricotta Gnocchi + Lamb
  Bolognese, pecorino canestraro, torn mint." Lamb, not pork. Direct
  specific-fact contradiction of the operator's own menu PDF.
  Decision: rewrote to "ricotta gnocchi with lamb Bolognese" - matches
  the FIG May 2026 dinner menu verbatim on the protein.

### Sanity-check on prices and durations

All 58 entries' price tiers, durations, and group sizes are
internally consistent and plausible for the venue type. Po Pigs $9.25
lunch buffet is correctly described as a buffet (not a tasting menu).
Cooking class prices $75-225 range matches operator pages. Lewis
Barbecue $14-18 lunch plate matches the operator's posted pricing
band. No mismatched price-vs-format pairs found.

### Cross-reference between entries

Re-checked all 7 venue-name claims across multiple entries (Hannibal's,
Bertha's, Dave's, Callie's, Smash City, Roti Rolls, Lewis Barbecue
each appear in 2+ files). Every dish/credential/hours claim cross-
file is consistent. No "Charleston's only X" double-claim. No
duplicate meeting points across cooking classes (all 6 operators are
geographically distinct: 184 E Bay, 164-A Market, 1895 Ave F, 505
Folly Rd, 2353 Hwy 17 N, 874 Orleans Rd). No chef name appearing at
unrelated venues (Chef Bob Waggoner only at his own kitchen, Chef
Rashaunda Grant only at Carolina Cookery, Chef David Schuttenberg
only at Kwei Fei, Chef James London only at Chubby Fish, Chef
Orlando Pagan only at Wild Common, Chef Mike Lata + Jason Stanhope
only at FIG, Chef Greg Garrison only at Prohibition - all confirmed
via independent press).

Spot-check on chef Greg Garrison at Prohibition (description claim):
verified by americascuisine.com and charlestoncitypaper.com 2023
feature - "owners Jim McCourt and Jim Walsh brought in chef Greg
Garrison." Real.

Spot-check on The Royal American "32oz punch" must_order:
verified by charlestongrit.com "A Lunch Date with the Royal American"
- "serving up live music and 32-ounce signature punches for six
years." Real (Rum / Bourbon / Vodka variants).

### QA1 + QA2 downgrade review

Re-read QA1's three soft concerns + QA2's resolution. QA2's calls
landed correctly:
- kwei-fei dishes: confirmed via Yelp + charlestonmag + allmenus,
  the Four Rivers Wings naming is the operator's, lamb dumplings
  and mapo tofu are on the current menu.
- vintage-lounge truffled fontina fondue: confirmed via Yelp +
  Restaurantji as the signature, operator's site is intentionally
  vague because the menu rotates.
- bowens-island steamed/roasted: QA2's fix to "steamed" is correct;
  current operator site uses "Steamed Oysters" as the headline term.

### Defects total (Opus)

4 new fixes, all in itineraries.json editorial prose:
1. charleston-weekend-classics day 1 evening (Husk grit cocktail +
   bacon-fat butter rewrite)
2. charleston-weekend-classics day 2 evening (Obstinate Daughter
   pasta-from-wood-oven + Folly cocktail rewrite)
3. charleston-on-a-budget day 2 morning (Roti Rolls horchata rewrite)
4. charleston-tasting-menu-weekend day 1 evening (FIG pork-ragu to
   lamb-Bolognese fix)

0 entities removed. 0 entity-field defects (all four are prose-layer
fabrications in the narrative copy of itineraries, the same class as
QA2's jack-of-cups cross-file echo - but in this round the prose
fabricates dish/drink/cooking-method specifics around real venues
rather than echoing closed-entity language).

Combined QA1 + QA2 + Opus: 3 + 4 + 4 = 11 editorial rewrites, 0
removals across 58 entities. Pattern remains 100% specific-fact
fabrication; 0 venue invention, 0 address fabrication, 0 closed-venue
inclusion. The itineraries prose is where the safety-net catch
landed - that prose layer was lightly sampled by QA2 (one fix:
jack-of-cups echo) and not deep-sampled; Opus surfaced four more
of the same class.

### Below-floor topics after Opus

None; no removals across any of the three QA passes.

### Verdict

VERDICT: PASS

Opus found four specific-fact fabrications in itineraries.json
editorial prose, all of the same dish-name fabrication class
QA1/QA2 documented for entity fields. None are venue inventions,
no entity removals were warranted, and the structural backbone
(58 verified entities, addresses, slugs, internal references,
operator URLs) is clean.

Worth noting upstream: itinerary prose deserves the same dish-
name + cooking-method specificity sweep that QA2 ran against
entity must_order fields. Three of the four Opus catches
(Husk cocktail, Obstinate Daughter cocktail, FIG ragu protein)
fabricated specifics that a one-pass operator-menu fetch would
have prevented. The fourth (Roti Rolls horchata) is the class
where the operator doesn't publish a drinks menu and silence
should default to a generic line, not invention. Recommend
QA PROMPT.md A2 sweep be expanded to include itinerary day-prose
verbatim - the same rules QA2 applied to entity fields.

Combined defect rate 11/58 = 19.0% with Opus's catches included;
all 11 are dish/drink/credential rewrites against verifiable
source content, none are fabricated-venue removals. Charleston
backfill is structurally sound.
