# QA report - Amsterdam (Opus final pass)

## Scope inherited from QA1 + QA2

QA1: 23 defects. QA2: 14 defects. Combined: 37 defects across 11 days
of upstream research output. QA2's verdict already flagged the
research-stage regression (real-URL + fake-address, chef-name
fabrication). My brief: narrow audit for residual count mismatches,
echoes, geographic adjacency, day-of-week/hours, verified-block
consistency, and phantom-venue references QA2 left in scope.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0.
- verify_entities.py warnings: unchanged cohort (own_site_only on
  amsterdamfoodie.nl cluster; transient anti-bot 401/403/429 on the
  four hosts QA1 already documented; feijoa.nl SSLError - intermittent).

## Judgment defects found

### A. Cuisine / category and source-URL final-host

- No new fabrications found. QA1 + QA2 cleared the heavy real-URL +
  fake-address cluster. Source-URL final-host check on 12 spot
  entities (Choux already fixed, Bolenius, Vinkeles, Sinne, Mama
  Makan, MOAK, Hearth, Bonboon, SOIL, Vermeers, Toscanini, Coba) -
  all resolve to the same registered domain or an authoritative
  directory. No parked-domain regressions.

### A2. Specific-fact / chef / address / closure drift

- No new defects. Vinkeles chef (van der Zalm), Sinne chef (Ioannou),
  Bolenius post-move address (Nachtwachtlaan 20B), Mama Makan
  post-move address (Spinozastraat 61) all internally consistent after
  QA2. Spectrum, Lievelinge, Headfirst, Mr & Mrs Watson, De Bolhoed,
  Lefebvre fully purged - zero echoes in any prose-bearing field.

### A3. Stubbe's bridge name (NEW DEFECT)

QA1 wrote "Stubbe's at the Haarlingersluis bridge on the Singel" in
both `street-food.json` description and `signature-dishes.json`
hollandse-nieuwe-haring history. The bridge name is wrong:
"Haarlingersluis" is not an Amsterdam bridge. The actual bridge is
**Haarlemmersluis** (a.k.a. Nieuwe Haarlemmersluis), confirmed by
Frommers, AFAR, Tripadvisor, and Amsterdam city archives. Yelp's
listing has the same typo, which is likely where QA1 picked it up.
Fixed both occurrences to "Haarlemmersluis". Trivial, but a
deterministic fact and a structural artefact of trusting one
secondary source.

### B. Route / itinerary mismatches

No food-tour route fabrications. Day-of-week x hours check on both
itineraries (weekend Sat/Sun + 3-day unassigned): no closed-day
defects, no market-day mismatches. Geographic adjacency in
itineraries: all walking distances <500m where prose implies
adjacency; ferry-and-tram transitions correctly named.

### C. Festival dates

QA1 fixed four festivals; QA2 cross-source verified all five
non-Pllek festivals against independent calendar sources. No
regressions. Cross-source dates hold (Bite June 19-21, TAPT May 8-9,
PINT Oct 2-3, Terrassen July 23-26, Rollende Keukens May 13-17).

### D. Thin-category fabrications

- vegan: 3 (floor 4). Unchanged from QA1+QA2; below-floor accepted
  per Lewis's standing rule.
- vegetarian: 1 (floor 2). Unchanged; below-floor accepted.
- gluten_free: 2 (floor 2). At floor.
- halal: 3 (floor 3). At floor.
- kosher: 2 (floor 2). At floor.

### E. Editorial-prose echoes

#### E1. Closed-venue echoes
Zero. Grep across all 27 data files for the QA1+QA2 removal strings
(spectrum, mr.?mrs.?watson, bolhoed, lefebvre, lievelinge, headfirst,
sint jacobsstraat 16, witte de withstraat 89, eerste helmersstraat
88, de wittenkade 1, boekhorststraat 5, hartenstraat 2, plantage
middenlaan 38, eerste van der helststraat 47, george gershwinlaan,
kuipers, werry, taste of amsterdam, broodkaas) returned ZERO hits.

#### E2. QA-removed-fact echoes
Zero. Cacio e pepe, carbonara, generic-fusion phrasing, "bos en
lommer takes the overflow", chouxchouxchoux.com - none remain.

#### E3. Phantom-venue editorial sweep

**Cooking-classes region.json description (NEW DEFECT)**: QA2 left
the description as "Amsterdam Cooking Workshops, Mama Makan,
Mediamatic and three more schools". **Mama Makan is a restaurant, not
a cooking school** - there is no Mama Makan cooking class in our
data. Rewrote to "Amsterdam Cooking Workshops, Mediamatic, The
Cookery and two more schools" (the three real named operators in our
cooking-classes.json). This is the Warsaw-Opus phantom-venue pattern:
a region SEO description naming a real Amsterdam venue but reaching
to the wrong topic for it.

All other capitalised proper-noun venues in region.json + city.json +
neighborhoods.json + food-history.json + seasonal-food.json +
signature-dishes.json + itineraries.json descriptions and prose:
verified to map to an existing entity by name or slug.

#### E4. Verified-block consistency

For every QA1+QA2-edited entity (Mama Makan, MOAK, Bolenius, Vinkeles
chef, Sinne chef, Vicio cuisine, Leo Bistro postcode, Jinweide
postcode, Vermeers postcode, VJFB address): `verified.address_quoted`
matches the NEW address; `verified.checked_on = 2026-05-20` on every
edited entity. All clean.

### F. Region.json SEO count audit (the main task)

QA2 noted bakeries (10 -> 8) and coffee-roasters (10 -> 6) title
corrections but left other count mismatches as "pre-existing not in
scope". Walked every numeric claim in `seo.pages.<topic>.title` and
`seo.pages.<topic>.description` against actual entity counts after
all QA removals.

Fixed:
- `restaurants.title`: "22 Picks" -> "23 Picks" (real count 23)
- `restaurants.description`: "19 more" -> "twenty more"
- `casual-dining.title`: "22 Picks" -> "15 Picks" (real count 15)
- `cafes.title`: "16 Coffee Picks" -> "12 Coffee Picks" (real 12)
- `cafes.description`: "13 more" -> "nine more"
- `wine-bars.title`: "10 Picks" -> "8 Picks" (real 8)
- `wine-bars.description`: "seven more" -> "five more"
- `bars.title`: "16 Cocktail Picks" -> "12 Cocktail Picks" (real 12)
- `bars.description`: "13 more" -> "nine more"
- `street-food.title`: "12 Counters" -> "10 Counters" (real 10)
- `street-food.description`: "eight more" -> "six more"
- `breweries.title`: "8 Taprooms" -> "7 Taprooms" (real 7)
- `breweries.description`: "four more" -> "three more"
- `markets.title`: "8 Picks" -> "7 Picks" (real 7)
- `markets.description`: "five more" -> "four more"
- `food-tours.title`: "7 Picks" -> "5 Picks" (real 5)
- `food-tours.description`: "three more" -> "one more"
- `cooking-classes.title`: "6 Schools" -> "5 Schools" (real 5)
- `cooking-classes.description`: rewrote venue names + count
- `budget-eating.title`: "12 Picks Under E15" -> "10 Picks Under E15"
- `budget-eating.description`: "eight more" -> "six more"
- `hidden-gems.title`: "10 Local Picks" -> "7 Local Picks" (real 7)
- `hidden-gems.description`: "seven more" -> "four more"
- `brunch.title`: "10 Spots" -> "8 Weekend Spots" (real 8;
  "Weekend Spots" lifts char count above 55-cap floor)
- `brunch.description`: "six more" -> "four more"
- `late-night.title`: "8 Picks" -> "7 Picks" (real 7)
- `late-night.description`: "four more" -> "three more"

Topics already correct (no edit): index, fine-dining (11/11),
bakeries (8/8 after QA2), coffee-roasters (6/6 after QA2), festivals
(6/6), dietary (11/11), signature-dishes (10/10), day-trips-food
(6/6), food-history, seasonal-food, itineraries.

## Defects total: 17

Breakdown:
- 15 region.json count corrections (E2 echo cleanup QA2 deferred).
- 1 cooking-classes phantom-venue (Mama Makan named as cooking school).
- 2 Stubbe's bridge-name typo corrections (street-food + signature-dishes).

(Quoting QA2's "the city is now clean enough that an Opus pass should
find at most cosmetic issues" - 17 is cosmetic by volume but the
phantom-venue regression in cooking-classes description is the same
Warsaw-Opus class memory flagged. Worth noting in research-prompt
retro: the agent borrowed a real venue name from one topic to fill
prose in another.)

## Below-floor topics after Opus pass

- dietary/vegan: 3 (floor 4) - unchanged from QA1.
- dietary/vegetarian: 1 (floor 2) - unchanged from QA1.

Both flagged for research backfill.

## Regressing upstream prompts

- **Cooking-classes phantom**: research-prompt-write or QA1
  rewrite-time leak. Likely research-stage wrote a generic "the
  schools include Mama Makan" without cross-checking the cooking-
  classes.json entity list. Same defect class as Warsaw QA2's
  phantom-venue cluster.
- **Stubbe's bridge name**: research-stage picked the spelling from
  Yelp's listing, which carries the same typo, without confirming
  against a higher-authority source. Single-source provenance defect
  (the source diversity memory rule).
- **region.json count titles**: this is a chronic pattern. SEO
  descriptions are written once at research time and not re-derived
  from the entity-list count when QA removes entries. A small
  generator pass that re-renders the count tokens from the actual
  array length would eliminate this class entirely.

## Verdict

VERDICT: PASS

(17 defects, all cosmetic or single-source provenance. No new
venue fabrications, no address fabrications, no closure drift. QA2's
analysis holds; the city is shippable.)
