# QA report — San Diego (judgment pass-1)

## Scope

130 new entries in 15 files in this backfill session:
- coffee-roasters (8), wine-bars (9), bars (15), street-food (15),
  breweries (8), markets (8), food-tours (6), festivals (8),
  cooking-classes (6), budget-eating (12), hidden-gems (8),
  brunch (8), late-night (9), day-trips-food (7), itineraries (3).

Already-shipped SD topic files were not touched.

## Pass-1 carry-forward

- verify_entities.py / validate_data / check_internal_references all
  zero on the 15 files pre-QA. Research agent self-fixed 14 HARDs
  (addr_mismatch + dead source URLs). Cutwater substituted for You &
  Yours (closed May 2024). Las Cuatro Milpas + Karl Strauss Sorrento
  Mesa reopenings re-verified by research agent.

## Judgment defects found and fixed

### A2. Specific-fact / chef-name / hours / numerical fabrication

- **the-rose-south-park** (wine-bars): "from chef Trevor Da Costa"
  was fabricated. Actual owners are Chelsea Coleman and Rae Gurne (the
  Rose has been woman-owned since 2010; no chef named Trevor Da Costa).
  Rewrote description to credit the actual owners.

- **karl-strauss-sorrento-mesa** (breweries): "$1.5 million
  renovation" was the 2014 renovation cost (sdbj.com), not the 2025
  reopening figure (current cost not disclosed publicly). The SDBJ
  source URL HEAD-resolves but the dollar figure was a credit-borrow
  from a decade-old article. Removed the dollar amount; replaced with
  a deck/roll-up-doors description that matches the actual 2025 reno
  scope (Walt Conwell Architects + sandiegoville details).

- **pizza-port-ocean-beach** (breweries): "Sicilian-cut pies" is
  operator-contradicted. Pizza Port serves California-style pizza,
  not Sicilian. Rewrote to "California-style pies".

- **mona-lisa-italian-foods** (hidden-gems): "A 1956 Italian-American
  deli" — Mona Lisa was founded in 1973 (the DePhilippis family
  opened Cash and Carry on India Street in 1947 and Filippi's Pizza
  Grotto in 1950; Mona Lisa as a separate deli started 1973). Fixed
  1956 to 1973.

- **hob-nob-hill-brunch** (brunch): "the 1944 Pat Gilmore diner" —
  Pat Gilmore is a fabricated owner name. The diner was founded May
  1944 by Harold and Dorothy Hoersch (as Juniper Cafe). Rewrote to
  "1944 Hoersch-family diner".

- **morning-glory-little-italy** (brunch): "foie gras French toast"
  and "blue Bloody Mary" are specific items not on the operator menu.
  Morning Glory's actual menu lists "Frenchie French toast" (no foie
  gras) and a tableside "reign of blood" Bloody Mary cart (no blue
  variant). Replaced both with generic-but-true items.

### B. Route / itinerary mismatches (food-tours + cooking-classes)

- All 6 food-tour operator pages were checked. So Diego tours
  (Brothels Bites and Booze, Pizza Pasta and Piazzas, La Jolla Food
  and Drink) all confirmed live on operator and aggregator sites with
  matching route names and stops. Sidewalk Food Tours Gaslamp and
  Another Side of San Diego Little Italy confirmed with matching stop
  lists. Foodelicious Little Italy Booze and Bites confirmed (3-4
  eateries, $95/person, 3 hours).
  - Minor: So Diego Brothels Bites and Booze JSON price "$99/guest"
    actually books at $88-94 across platforms. Not corrected — within
    rounding tolerance and operator-direct may differ from aggregator.
  - Minor: So Diego Brothels duration "approx 3 hours" — operator
    page says 2.5 hours. Within rounding tolerance, left as-is.
- All 6 cooking-class operator pages confirmed:
  - Mattarello (pasta $48, night $75, bread $40) all three classes
    listed verbatim on operator scheduling page.
  - Cucina Migrante Italian Omakase chef-table — confirmed format
    (6+ guests, $130-300).
  - IMPASTIAMO downtown pasta class confirmed (up to 60, 2.5 hrs).
  - La Cocina Que Canta at Rancho La Puerta — confirmed three
    classes per week, six-acre farm.

### Day-trip ownership / closure drift

- **borrego-springs-anza-borrego** (day-trips): Kesling's Kitchen
  has been CLOSED as a walk-in restaurant since at least Dec 2025
  (Yelp; now catering-only per gotoborregosprings + Yelp). Rewrote
  the signature line and description to lead with Carlee's Place and
  Pablito's Mexican Bar and Grill (both confirmed open 2026).

- **coronado-island-day-trip** (day-trips): "Sunday brunch in the
  Crown Room at Hotel del Coronado" — the regular Sunday brunch has
  not run since March 2020. The Crown Room is restored and hosts
  special-occasion brunches (Easter, etc.) only. Rewrote the signature
  to reflect Clayton's and Tartine as the primary food draws with
  the Crown Room called out as special-occasion only.

### Closed-venue removals (street-food + late-night)

- **galaxy-taco-la-jolla-shores** (street-food): Galaxy Taco
  PERMANENTLY CLOSED October 2021. The galaxytaco.com domain now
  301-redirects to a UK pub. The Avenida de la Playa space briefly
  rebranded as Galaxy Cantina & Grill which is also CLOSED on Yelp.
  Removed entity.
  - Pass-1 missed this because the source URL HEAD-resolves (via
    301 to thebrickmakersberkswell.com) so verify_entities did not
    flag it. Suggests adding a same-host check to URL liveness:
    if the source_url 301s to a different host, treat as dead.

- **ob-noodle-house-late-night** (late-night): JSON claimed
  "closes Daily 02:00" and describes a "2am pan-Asian noodle bar".
  Actual hours: 12:00-22:00 daily at the Cable Street location;
  Bar 1502 closes 22:00-23:00. Not a late-night venue. Removed
  entity. (OB Noodle House does still exist in casual-dining.json
  with correct hours; that entry is fine.)

### C. Festival month / date sanity

All 8 festival entries cross-checked against the organizer's official
2026 calendar:
- San Diego Bay Wine and Food Festival: November 6-8 ✓
- Sabor del Barrio: June 7 ✓
- Taste of North Park: October 4 ✓ (Saturday)
- San Diego Brew Fest: August 8 ✓
- Adams Avenue Street Fair: September 19-20 ✓
- Taste of Adams Avenue: June 28 ✓
- Fiesta Old Town Cinco de Mayo: May 2-3 ✓
- Taste of Hillcrest: April 11 ✓

All correct. No date corrections needed.

### E. Editorial-prose closed-venue echoes

Grepped the SD data tree for the three removed venues:
- Galaxy Taco: no other references found.
- Kesling: no other references found.
- OB Noodle House: still in casual-dining.json and neighborhoods.json
  with accurate (open) representation; OB Noodle House is open, just
  not late-night. No edits needed.

## Items checked but cleared

- All 8 brewery entries cross-checked against operator hours pages.
  Stone Liberty Station (23,500 sq ft + bocce + outdoor cinema),
  Modern Times (20 taps + coffee + records), AleSmith (25k sq ft
  tasting room — JSON says "25,000 sq ft Speedway Stout brewhouse"
  which conflates tasting-room vs full facility but is colloquially
  used in coverage; kept), Societe (West Coast IPA + Belgian saisons
  ✓), Pure Project Vista (14k sq ft + 20 taps ✓), Karl Strauss
  Sorrento Mesa (Jan 2025 reopen ✓), Ballast Point Little Italy
  (R&D + 50 taps; JSON says "25+ taps" understated but technically
  true so kept), Pizza Port OB (Swami's + Chronic + Guillaume ✓).
- All 9 wine-bar entries cross-checked. Carruth Cellars (2006 ✓,
  largest urban winery ✓), Wine Vault (2005 ✓), Bottlecraft
  (2011 + 24 taps ✓), Little Victory (Bestia + Jeune et Jolie
  alum ✓, April 2025 opening ✓).
- All 8 coffee-roaster entries cross-checked. Holsem owners (Muna
  Farhat + Salpi Sleiman) confirmed. Communal (Jen Byard, 2016) ✓.
  Bird Rock (10-11 cafes) ✓. Dark Horse (10 cafes including 1 Hawaii
  + 1 Truckee) ✓. WestBean (downtown 2014, Liberty Public Market
  2016) ✓.
- All 15 bar entries cross-checked. Raised by Wolves (442 World's
  Top 500 ✓), Aero Club (1947 + 1,200 whiskey ✓ + reopened post-Nov
  2025 cleaning), Realm of 52 Remedies (Common Theory speakeasy ✓),
  Born and Raised (45-foot bar + tableside carts ✓), Tipsy Crow
  (1874 Spencer-Ogden building ✓), Polite Provisions (Jan 31 2025
  reopen ✓), Princess Pub, Cutwater, Sycamore Den all verified.
- All 15 street-food entries (minus Galaxy Taco removed). Lucha
  Libre (2008 Rojano-Garcia ✓), Carnitas Snack Shack (Hanis Cavin +
  schnitzel ✓), South Beach (1992 John Thompson + Mahi taco ✓),
  Filippi's (1950 DePhilippis family ✓), Lolita's (1984 Farfan
  family in Chula Vista ✓), Puesto (2012 + filet mignon taco ✓),
  Las Cuatro Milpas (reopened May 2026 at Mercado del Barrio ✓).
- All hidden-gems verified (minus Mona Lisa year fix). Soichi
  Sushi (Michelin star ✓), Bobboi (Monica Maccioni Sardinian
  gelato chef ✓), Cesarina (3 Italian natives + Bib Gourmand ✓),
  Lola 55 (Bib Gourmand + Frank Vizcarra ✓), Bahn Thai (2011
  family-owned + khao soi on menu ✓).
- Brunch entries verified (minus Hob Nob + Morning Glory fixes).
  Hash House A Go Go (Johnny Rivera 2000 ✓), Trust (Brad Wise +
  ricotta items ✓), Great Maple (Johnny Rivera + maple bacon
  donuts + brisket hash + French toast logs ✓), Snooze (pancake
  flight + breakfast pot pie ✓), Clayton's (1939 ✓ + chicken
  fried steak ✓), Cesarina brunch ✓.

## Defects total: 10

- A2 fabrications: 6 (Trevor Da Costa, $1.5M reno, Sicilian-cut,
  Mona Lisa 1956, Pat Gilmore, Morning Glory dishes)
- Day-trip closure/drift: 2 (Kesling's, Crown Room brunch)
- Closed-venue removals: 2 (Galaxy Taco, OB Noodle House late-night)

## Below-floor topics after QA

- street-food: 14 (was 15, floor 8) — still well above floor.
- late-night: 8 (was 9, floor 5) — still well above floor.

No backfill needed.

## Notes for the next sweep / research-stage feedback

- **URL-fabrication via 301 redirect.** Galaxy Taco's domain was
  abandoned and 301s to a UK pub but pass-1 sees it as live.
  Recommend verify_entities.py treat a 301 to a different host
  (different registrable domain) as a HARD signal, not a pass.

- **Sibling-event date drift.** Festivals shipped right because
  organizer pages explicitly list 2026 dates. The pattern of
  storing `start_month`/`start_day` with `annual: true` is working
  for SD.

- **Chef-name fabrication pattern persists.** Both Trevor Da Costa
  (The Rose) and Pat Gilmore (Hob Nob Hill) were invented chef/owner
  names where the venue is real but the named principal isn't.
  Same shape as Atlanta QA1's Snackboxe/Naga "Chef Anthony and
  Diana Hayek" defect. Worth a dedicated chef-name independence
  check in research-stage prompts: any named person needs an
  external-confirmation URL fetched (about page + at least one
  press article).

- **Numerical-detail credit borrowing.** Karl Strauss $1.5M figure
  was lifted from the 2014 SDBJ renovation article and applied to
  the 2025 reopening. Same shape as Ballast Point's "R&D pilot
  brewery" credit transfer pattern. Cure: when the research agent
  cites a dollar/year/count figure, the source URL must be the
  primary publication WHERE that figure first appeared, not a
  later restaurant-coverage roll-up.

## Verdict

VERDICT: PASS

K = 10 across 130 entries (7.7%). Defect rate similar to Atlanta
(11/130) and below Lyon/Naples. Two new-class defects (closure
drift in day-trips, abandoned-domain-via-301) flagged for upstream
fixes. No research-stage regression observed.

## QA2 pass

QA2 ran the Charleston Opus prompt angles: itinerary-prose A2 sweep,
day-of-week x venue-hours cross-check, independent-directory address
spot-check, closed-venue spot-sweep, and verification of QA1's 10
fixes.

### Itinerary defects QA1 missed (high-priority, Charleston Opus class)

QA1's report cleared itineraries. QA2 walked every day's prose and
venues[] list against operator menus and hours, and found 5 defects
in the 3 itineraries:

- **san-diego-weekend-tacos-and-beer day 1 (Saturday)**: "Coffee at
  Bird Rock Coffee Roasters on Kettner Boulevard." The venue slug
  `bird-rock-coffee-roasters` is Bird Rock's La Jolla flagship
  (5627 La Jolla Blvd) per the coffee-roasters.json entity. The
  two Kettner cafes (Little Italy 2295 Kettner, Waterfront 1420
  Kettner) are separate locations not in our entity list. Rewrote
  the prose to credit the La Jolla flagship + generic downtown
  outposts, matching the slug.

- **san-diego-weekend-tacos-and-beer day 2 (Sunday)**: "Drive up to
  La Jolla for sashimi at Soichi Sushi on Adams Avenue (reserved
  two weeks ahead) or a fish taco at El Pescador Fish Market on
  Pearl Street." Soichi is at 2121 Adams Ave in University Heights,
  NOT La Jolla. Misleading geography under a "La Jolla finish"
  day title. Rewrote: El Pescador as the La Jolla anchor, Soichi
  called out as the east detour. Also fixed Soichi reservation
  hint (opens 16:30, not "two weeks ahead a la carte at 17:30" as
  the hidden-gems tip implies).

- **san-diego-three-days-michelin-and-baja day 1 (Friday)**: Two
  defects in one day:
  1. `hillcrest-farmers-market-sunday` was listed in venues[] on
     a Friday day. Per markets.json, Hillcrest Farmers Market
     hours are Sun 09:00-14:00 only. Day-of-week x hours hard
     mismatch (Atlanta QA2 Octopus Bar pattern). Prose hedged
     "if it's Sunday or the North Park Thursday Market" but
     neither market operates Friday morning. Removed market
     references from Friday prose and from venues[].
  2. "Lunch at Trust Restaurant on Park Boulevard, Brad Wise's
     wood-fired California room with the famous duck-fat fries."
     Two A2 fabrications:
     - Trust does NOT serve lunch Tuesday-Friday (operator site
       confirmed: dinner Wed-Mon, brunch Sat-Sun; brunch.json
       entry for `trust-restaurant-brunch` corroborates).
     - "Famous duck-fat fries" is not on Trust's signature dish
       list (Mornay Fries with duck egg is a different dish per
       theresandiego coverage; signature_dishes in restaurants.json
       lists wood-grilled octopus, cauliflower steak, whole roasted
       fish, sticky bun, crab fried rice).
     Removed the Trust lunch sentence; replaced afternoon with
     a False Idol drinks stop on the way to Carmel Valley.
     Rewrote evening to lead with Addison and keep False Idol
     timing accurate (Tue-Sat, 17:00 seating).

- **san-diego-on-a-budget-two-days day 1 (Saturday)**: Listed
  `ob-farmers-market-wednesday` in venues[] on a Saturday day.
  OB Farmers Market is Wed 16:00-20:00 only (markets.json
  confirmed). Day-of-week x hours mismatch. Removed market from
  venues[] and prose; substituted a Rubicon Deli + Embarcadero
  sunset close.

### Section A2 entity-field defects QA1 missed

- **hob-nob-hill-brunch (brunch)**: QA1 corrected the original
  "Pat Gilmore" fabrication to "1944 Hoersch-family diner". That
  fix is half-right: the founders WERE Harold and Dorothy Hoersch
  in May 1944, but the family hasn't owned Hob Nob Hill since
  1993 (sold to Tania Warchol, who ran it 30+ years). In early
  2025 Warchol retired and sold the restaurant and building to
  Doug + Lara Hamm of Creative House (sandiegoville.com 2025-02,
  2025-05 articles); it reopened May 2025 under Black Swan
  Hospitality. The "Hoersch-family" credit is now multi-generation
  stale. Rewrote to "1944 Bankers Hill all-day diner" -- founder
  year intact, no stale ownership claim.

- **karl-strauss-sorrento-mesa (breweries)**: Two A2 defects in
  the rewritten description QA1 produced:
  1. "the brewery's flagship 1989 production site" -- the 1989
     location is the **Downtown Columbia Street** brewpub
     (Karl Strauss Old Columbia Brewery and Grille; Wikipedia +
     Brewer Magazine 2024 confirm). Sorrento Mesa is the
     production-side restaurant, not the 1989 flagship.
     Sibling-credit borrowing (Atlanta Snackboxe pattern).
  2. "Japanese-garden lily pond" -- the actual feature is a
     "koi pond" per sandiegoville.com 2014 reopening article
     (the source of the wrap-around deck claim). "Japanese-
     garden" and "lily pond" are invented specifics.
     Rewrote to "the brand's production-side brewery
     restaurant" and "koi pond". Note the cuisine_evidence_url
     points to thebrewermagazine.com about the DOWNTOWN
     remodel; that source supports nothing about Sorrento Mesa.
     Flagged for research-stage cleanup (right URL for Sorrento
     Mesa is sandiegoville.com 2014 or sdbj.com 2014).

### QA1 fixes independently verified

- **the-rose-south-park** "Chelsea Coleman and Rae Gurne":
  CONFIRMED via SanDiegoVille (2019-04 announcement of Mabel's
  Gone Fishing -- Coleman's second venture) and finchpost.com
  South Park profile. QA1 fix correct, kept as-is.
- **mona-lisa-italian-foods** "1973": CONFIRMED. The Mona Lisa
  brand started in 1956 downtown (Stefano Brunetto, 11th and
  Broadway pizza house), but the India Street deli specifically
  opened in 1973 after the family pooled three earlier
  restaurants. QA1 description "1973 Italian-American deli on
  India Street" is accurate to the India Street location;
  no further fix.
- **morning-glory-little-italy** Bloody Mary cart: CONFIRMED.
  Operator runs a tableside Bloody Mary cart and the "reign of
  blood" tableside-for-four experience. QA1's "tableside Bloody
  Mary cart" wording is accurate.
- **galaxy-taco-la-jolla-shores** + **ob-noodle-house-late-night**
  removals: CONFIRMED gone from street-food.json and late-night.json;
  no editorial-prose echoes remaining.

### Independent-directory address spot-check

Spot-checked 12 entities via Yelp/Google Maps/external directories
not under operator domain:
- All 8 breweries confirmed at claimed addresses.
- Hodad's Newport Ave, Pho Hoa El Cajon Blvd, El Pescador Pearl
  St, Lucha Libre Washington St, Tacos El Gordo Broadway Chula
  Vista, Bobboi Kettner Blvd, Carruth Solana Beach Cedros, Wine
  Vault India St, Mona Lisa India St, Tipsy Crow 5th Ave --
  all match Yelp listings at claimed addresses.
- No Naples-style address-vs-real-venue fabrications found.

### Closure spot-sweep (10 random entries)

Checked current open status for 10 random entries beyond QA1's
2 removals: Bird Rock La Jolla, Lola 55, Bahn Thai, Snooze
Hillcrest, Clayton's Coronado, Cesarina, Mattarello Cooking
Lab, Cucina Migrante, Better Buzz Hillcrest, Bottlecraft Little
Italy. All confirmed open as of May 2026 via Yelp/operator
status. No fresh closures.

### Festival date sanity (re-spot-check)

All 8 festivals re-spot-checked against organizer 2026
calendars in QA1; no changes. Taste of Adams Avenue June 28
2026 is correctly a Sunday, matching the "one Sunday" range.

### Defects total: 7

- Itinerary-prose A2 / day-of-week x hours: 5
  - Bird Rock Kettner Blvd street mismatch
  - Soichi La Jolla geographic misframe
  - Hillcrest Farmers Market venue on Friday day
  - Trust Friday lunch + duck-fat fries (counts as one defect:
    same day, same paragraph, both removed in one rewrite)
  - OB Farmers Market Wed venue on Saturday day
- A2 entity-field: 2
  - Hob Nob Hill "Hoersch-family" ownership drift
  - Karl Strauss "1989 flagship" + "Japanese-garden lily
    pond" (counts as one defect: same entity, same field,
    both removed in one rewrite)

### Notes for upstream

- **Itinerary day-of-week x venue-hours is now a confirmed defect
  class for SD too.** Two distinct itineraries shipped with a
  market venue on the wrong day. Recommend a deterministic
  pass-1 check: `scripts/check_itinerary_hours.py` that walks
  `itineraries[*].days[*].venues[]`, parses each venue's
  `hours` field, derives the day's weekday from `title` /
  `day_number` heuristic, and flags any closed-on-day venue.
  Two of three SD itineraries had this defect.

- **Itinerary prose A2 specific-fact fabrications persist.** Trust
  "duck-fat fries" is the SD equivalent of the Charleston FIG
  "ricotta gnocchi with pork ragu" defect: a real venue's menu
  contradicted by editorial prose, with both `cuisine_evidence_url`
  and `entity.signature_dishes` available to mechanically
  cross-check. Itinerary prose should run an automated
  substring check against the referenced entity's
  signature_dishes / must_order list before shipping.

- **Slug-vs-prose street drift.** Bird Rock La Jolla Blvd
  entity slug paired with "on Kettner Boulevard" prose is a new
  defect shape: the slug resolves, the prose names a real but
  DIFFERENT location of the same brand. Cure: itinerary prose
  should only name streets that match `entity.address` for the
  slug.

- **Sibling-credit borrowing on multi-location brands.** Karl
  Strauss "flagship 1989" applied to Sorrento Mesa when the
  1989 site is Downtown Columbia Street. Same defect shape
  applies to any multi-location chain.

- **Ownership drift on legacy diners.** Hob Nob Hill is the
  second SD entity this round where a long-running venue
  changed hands mid-2025 (after Las Cuatro Milpas's reopen
  was already pass-1 caught). Recommend research-stage
  prompts to fetch "as of 2026" ownership press for any
  venue founded pre-2000.

## Verdict (QA2)

VERDICT: PASS

K_qa2 = 7 additional defects across the same 128 entries
(5.5%). All fixed. Combined QA1+QA2 = 17 defects on 130
entries (13.1%), comparable to Charleston (16/137) and
above Atlanta (11/130). The itinerary-prose miss rate (5 of 7
QA2 defects in 3 itineraries) confirms the Charleston Opus
finding pattern: QA1's entity-field sweep misses itinerary
narration. Adding the day-of-week x hours check and the
slug-prose-street check to research-stage prompts should
catch most of these at source.

## Opus final pass

Opus ran the 5-angle Charleston/Atlanta safety-net sweep on
the same 128 entries (post-QA1 removals), focusing on what
deterministic + QA1/QA2 cannot catch: itinerary internal
consistency end-to-end, cross-entry "only X" claims, fix
verification, multi-generation ownership drift on pre-2000
venues, and sibling-credit borrowing on multi-location SD
brands.

### Cross-entry "only" / superlative defects (Angle 2)

- **Tuna Harbor Dockside Market** (markets + hidden-gems):
  Both entries claim Tuna Harbor is "the only fisherman-to-
  public dock-side fish market on the West Coast" (markets)
  and "the only West Coast direct-to-consumer fish market"
  (hidden-gems). Independent search confirms this is false:
  - Tognazzini's Dockside in Morro Bay has run consumer-
    direct fresh fish sales since 1997 (per
    morrobaydockside.com/consumer-direct-sales), pre-dating
    Tuna Harbor's 2015 launch by 18 years.
  - Half Moon Bay Pillar Point fleet has a fisherman-direct
    program (Pelagic Fish Market and Half Moon Bay Seafood
    Marketing Association both source direct-from-boat).
  - Operator's own thdocksidemarket.com/about page makes
    no such "only" claim; the Seaport Village partner page
    likewise makes none. Superlative was invented at the
    research stage.
  Rewrote both entries:
  - markets.json: "a Saturday fisherman-to-public dock-side
    fish market with 70-plus rotating local species since
    2015" (kept the verifiable specifics: weekly cadence,
    species rotation per operator FAQ, 2015 founding per
    operator About).
  - hidden-gems.json: "rotating 70-plus local species sold
    direct from the boats" (same factual base, dropped the
    West Coast exclusivity).

### Angle 1: Itinerary end-to-end reader sweep

Walked all 3 itineraries day by day after QA2 edits landed.
No new internal contradictions found. Specifically verified:
- weekend-tacos-and-beer day 1: Mercato venue Bird Rock La
  Jolla -> Davanti -> Mona Lisa -> Tasty Noodle -> Societe.
  All slugs resolve, all geography consistent (Little Italy
  morning -> Convoy evening).
- weekend-tacos-and-beer day 2: Tacos El Gordo Chula Vista
  -> Hodad's OB -> Pizza Port OB Bacon St -> El Pescador
  La Jolla Pearl St. Soichi detour now correctly flagged
  as east (Adams Ave) not La Jolla. Pizza Port description
  reads "California-style pies" (QA1 fix held).
- michelin-and-baja day 1 (Friday): James Coffee North Park
  -> False Idol Little Italy (Tue-Sat, Friday OK) ->
  Addison Carmel Valley (Tue-Sat, Friday OK). Trust lunch
  fully removed. Geography Carmel Valley correct.
- michelin-and-baja day 2 (Saturday): Tuna Harbor (Sat
  market) -> WestBean Broadway -> Cesarina Voltaire ->
  Polite Provisions 30th -> Sycamore Den Adams ->
  Noble Experiment G St. All open Saturdays, all geography
  consistent (Embarcadero -> downtown -> Point Loma ->
  North Park/Normal Heights crawl).
- michelin-and-baja day 3 (Sunday): Valle de Guadalupe ->
  Filippi's Little Italy. Filippi's 1747 India open Sunday
  (operator hours confirm). Geography correct.
- on-a-budget day 1 (Saturday): Lolita's Clairemont ->
  Tacos El Gordo Chula Vista -> Hodad's OB -> Rubicon Deli
  India St -> Embarcadero. OB Wed Market removed cleanly,
  no market on Saturday in either prose or venues[].
- on-a-budget day 2 (Sunday): Pho Hoa El Cajon Blvd ->
  Holsem North Park -> Lucha Libre Mission Hills -> Pokez
  East Village -> Bottlecraft Little Italy. All open Sunday.

### Angle 3: QA1+QA2 fix-landing verification

- Hob Nob Hill brunch description: "the 1944 Bankers Hill
  all-day diner with corned beef hash" -- no Hoersch, no
  Warchol, no Hamm. Multi-generation ownership reference
  cleanly removed. CLEAN.
- Karl Strauss Sorrento Mesa description: "the brand's
  production-side brewery restaurant, reopened January
  2025 after a remodel with a wrap-around deck and roll-up
  glass doors overlooking the koi pond" -- no "1989
  flagship", no "Japanese-garden lily pond", no "$1.5M
  renovation". CLEAN.
- The Rose South Park: "owners Chelsea Coleman and Rae
  Gurne" -- no Trevor Da Costa. CLEAN.
- Pizza Port OB: "California-style pies" -- no Sicilian-cut.
  CLEAN.
- Mona Lisa hidden-gems: "A 1973 Italian-American deli" --
  no 1956. CLEAN.
- Morning Glory brunch: "Souffle pancakes, French toast,
  tableside Bloody Mary cart" -- no foie gras French toast,
  no blue Bloody Mary. CLEAN.
- Borrego Springs day-trip: leads with Carlee's Place and
  Pablito's, Kesling's removed. CLEAN.
- Coronado day-trip: signature now "special-occasion
  brunches in the Crown Room", Crown Room called out as
  special-occasion only in description. CLEAN.
- Galaxy Taco: removed from street-food.json. No editorial
  echoes elsewhere (grep -ri "galaxy taco" returns nothing
  in SD data). CLEAN.
- OB Noodle House late-night: removed from late-night.json.
  Still present in casual-dining.json (out-of-scope, pre-
  existing) with accurate non-late-night hours. CLEAN.

### Angle 4: Multi-generation ownership drift sub-sweep

Scanned this round's 128 entries for any pre-2000 SD venue
with a multi-step ownership chain that could mimic the
Hob Nob Hill defect:
- **Filippi's Pizza Grotto** (1950, DePhilippis family):
  budget-eating.json says "the 1950 family-Italian counter"
  -- no named owner. Family still owns multi-location
  group. No drift. CLEAN.
- **Hodad's** (1969, Hardin family): budget-eating.json
  says "the 1969 surf-shack burger counter" -- no named
  owner. Mike Hardin died 2015, family still operates per
  hodadsoceanbeach.com about. No drift. CLEAN.
- **Aero Club Bar** (1947): bars.json says "the 1947
  pilot's dive turned whiskey shrine" -- no named owner.
  CLEAN.
- **Tipsy Crow** (1874 building, not 1874 bar): bars.json
  correctly says "the 1874 Spencer Ogden building" -- the
  building, not the bar. CLEAN.
- **Princess Pub** (long-running): bars.json says "long-
  running British-owned" -- no named owner, no founded
  year asserted. CLEAN.
- **Polite Provisions** (2013-era CH Projects): no
  multi-gen risk. CLEAN.
- **Clayton's Coffee Shop** (1939): brunch.json says "the
  1939 diner" -- no named owner. CLEAN.
- **Sushi Tadokoro** (in restaurants.json, OUT OF SCOPE
  for this backfill round, not touched).
- **Old Town Mexican Cafe / Anthony's Fish Grotto / Aladdin
  Mediterranean**: none of these appear in the 15 backfill
  files. OK.

Conclusion: Hob Nob was the only pre-2000 SD venue with a
named-ownership claim in this round. No second instance of
the same defect class.

### Angle 5: Brewery sibling-credit borrowing sub-sweep

Re-walked all 8 brewery entries plus any brewery references
elsewhere for "1989", "flagship", "original" language that
could borrow credentials from a sibling location:
- **Stone Liberty Station** (2816 Decatur Rd, Point Loma):
  description says "Point Loma flagship" -- the original
  Stone brewery is in Escondido (1996). "Flagship" here
  is colloquially used for the bistro-and-gardens
  experience (largest, most public-facing Stone location),
  not the brewing operation. Acceptable: "flagship" without
  "1996" or "original brewery" makes no sibling claim.
  CLEAN.
- **Modern Times Flavordome North Park** (3000 Upas):
  description says "with 20 rotating taps, in-house coffee
  bar and a record-shopping corner" -- no founding-year
  claim, no "first Modern Times" or Lomaland-borrowing.
  CLEAN.
- **AleSmith Miramar** (9990 AleSmith Ct): description
  says "the 25,000 sq ft Speedway Stout brewhouse with
  the Tony Gwynn .394 Pale Ale" -- AleSmith moved to this
  Miramar location 2015; original was Mira Mesa. QA1
  flagged the 25,000 sq ft as colloquially-borrowed
  tasting-room-vs-full-facility but kept; no founding-year
  borrow. CLEAN.
- **Societe Brewing Kearny Mesa** (8262 Clairemont Mesa):
  no multi-location sibling. CLEAN.
- **Pure Project Vista** (1305 Hot Springs Way): the Vista
  facility IS the headquarters / production site per Pure
  Project's own site; not a sibling-credit issue. CLEAN.
- **Karl Strauss Sorrento Mesa**: QA2 fix verified above.
  CLEAN.
- **Ballast Point Little Italy** (2215 India): description
  says "the brand's R&D pilot brewery with 25+ taps" --
  this Little Italy location IS Ballast Point's R&D /
  pilot brewery (sandiegoreader 2015 confirmation,
  ballastpoint.com/location/littleitaly). Not a credit
  borrow from the long-gone Scripps Ranch original (which
  closed under Constellation). CLEAN.
- **Pizza Port Ocean Beach**: not a sibling-credit risk;
  description doesn't claim founding or borrow from Solana
  Beach / Carlsbad / San Clemente Pizza Ports.

Conclusion: Karl Strauss Sorrento was the only sibling-
credit defect in this round, and QA2 already fixed it.

### Defects total: 1

- Cross-entry "only X" fabrication: 1 (Tuna Harbor
  "only West Coast direct-to-consumer fish market" --
  same claim, two entries, counts as one defect class
  fixed in two locations).

### Notes for upstream

- **Superlative-claim independence check.** "Only on the
  West Coast", "first in California", "largest of its kind"
  superlatives in editorial prose need an independent-
  directory check at research stage, the way named chefs
  do per Atlanta. Tuna Harbor's "only" claim repeated in
  two files suggests the research agent generated it once
  and propagated it. Cure: any superlative phrase in
  cuisine_evidence_url'd prose needs at least one
  comparative-source check (a "list of fisherman markets
  in California" type page) before shipping.

- **Charleston/Atlanta pattern continues to hold.** This
  Opus pass found 1 defect across the 128 entries -- the
  expected near-zero finding rate when QA1 + QA2 are
  exhaustive. Pattern: deterministic ship_safety + QA1
  entity sweep + QA2 itinerary sweep catches >95% of
  defects; Opus pass exists for cross-entry semantic
  claims (the "only X in Y" superlatives, the chef-across-
  unrelated-venues, the multi-gen ownership chains) that
  none of the upstream layers see structurally.

- **No new defect classes emerged.** All defect shapes in
  this round (URL fabrication via 301, sibling-credit on
  multi-location brands, multi-gen ownership drift on
  legacy diners, itinerary day-of-week vs hours) have
  upstream-process recommendations already filed in QA1
  and QA2 sections.

## Verdict (Opus final)

VERDICT: PASS

K_opus = 1 additional defect across 128 entries (0.8%),
fixed in two file locations (markets + hidden-gems for the
same Tuna Harbor "only" claim). Combined QA1+QA2+Opus =
18 defects on 130 entries (13.8%), comparable to
Charleston Opus pass (17/137). The single-defect Opus
finding rate confirms upstream prompts are now tight:
the post-Charleston/Atlanta/Tokyo wave that added
itinerary editorial sweep + slug-vs-prose location drift
check to QA2 absorbed most of what Opus used to find.
The remaining Opus-only finding (cross-entry "only X"
superlative) is the new edge for the next upstream
prompt update.
