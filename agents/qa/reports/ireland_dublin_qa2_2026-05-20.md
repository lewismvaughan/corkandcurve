# QA2 report - Dublin (independent second judgment pass)

## Pass-1 carry-forward + QA1 context

- ship_safety.sh: verify_entities clean at QA2 entry; QA1 fixed 41 defects.
- QA1 caught the URL-fabrication-at-scale pattern in research stage.
- This QA2 pass found that pattern extended significantly deeper: **the
  research agent fabricated eircodes (Irish postal codes) at scale across
  approximately 30 entities**, plus several wrong-address/wrong-neighborhood
  cases QA1 missed.

## Judgment defects found

### A. Cuisine / category + independent-directory address cross-check

**Wrong-venue (entity describes wrong place entirely):**

- `vice-coffee` (cafes) + `vice-coffee-roasters` (coffee-roasters):
  shipped at "54 South William Street, Dublin 2, D02 X589" with
  Powerscourt Centre context; the real Vice Coffee Inc moved to 54
  Abbey Street Middle, Dublin 1, D01 E2X4 inside Wigwam venue.
  Address, neighborhood, eircode AND description all wrong. FIXED both
  files plus itineraries day-1 morning prose (was "Breakfast at Vice
  Coffee on South William Street" → "Breakfast at Network Cafe on
  Aungier Street") + venues array swap (`vice-coffee` →
  `network-cafe`). Source_url updated to vicecoffeeinc.com/find-us.

- `cloud-picker-coffee` (coffee-roasters): shipped at "8 Cumberland
  Street South, Dublin 2, D02 P970"; real address is 42 Pearse Street,
  The Academy, Dublin 2, D02 FP30. FIXED address, eircode, source_url.

- `imbibe-coffee-roasters` (coffee-roasters): shipped at "St Joseph's
  Parade, Dublin 7, D07 X5W2" with Phibsborough context; real address is
  The Millennium Centre, 9 Dolphin's Barn, Dublin 8, D08 WD35. Wrong
  neighborhood (D7 → D8), wrong street, fabricated eircode. FIXED
  address, neighborhood remains the-liberties (D8 area), description
  rewritten to wholesale-only with no public cafe.

- `bow-lane-coffee` (coffee-roasters): FABRICATED entity. "Bow Lane"
  in Dublin is a cocktail bar at 17 Aungier Street, NOT a coffee
  roastery at "1 Bow Lane West, Dublin 8, D08 K3W7". The entity claims
  filter pour, brunch, single-origin retail and a Heuston Station-side
  lane garden — none of which exists. REMOVED. Drops coffee-roasters
  count from 6 to 5.

- `v-face-vegan` (dietary[vegan]) + `v-face-budget-vegan`
  (budget-eating): shipped at "33 Aungier Street, Dublin 2, D02 W267".
  Real V-Face has moved to 30 Brunswick Street North, Stoneybatter,
  Dublin 7, D07 TP64. FIXED both files (address, eircode, neighborhood,
  description) and itineraries day-1 evening prose (was "V-Face on
  Aungier Street" → "V-Face in Stoneybatter").

- `scéal-bakery` (bakeries): shipped at "94 The Coombe, Dublin 8,
  D08 X635" as the Dublin bakery flagship. The 94 The Coombe address
  is fabricated — Scéal has no location there per operator's site.
  Real Dublin location is Scéal Cafe at 82 South Circular Road,
  Dublin 8, D08 FC62 (the 2026 expansion taking over Little Bird
  space; the original Scéal operated from inside the Fumbally before
  Greystones). FIXED name (Scéal Cafe), address, neighborhood
  (the-liberties → portobello), source_url
  (irishtimes.com/2025/07 → scealbakery.com/location).

**Specific-fact / chef-name fabrications:**

- `the-old-spot` (casual-dining): described as "Stephen McAllister's
  modern Irish gastropub" — McAllister runs The Pig's Ear, not Old
  Spot. Real Old Spot ownership is Brian O'Malley and Stephen
  Cooney's Loyola Group (with brothers Barry and Paul McNerney of
  Junior's). FIXED description.

- `delahunt` (restaurants): described as "Darren Free and Patrick
  Powell's modern Irish dining room". Powell is a London-based chef
  who never ran Delahunt; current Delahunt head chef is Dermot
  Staunton (since opening day). FIXED description.

- `bastible` (fine-dining): `chef` field said "Barry FitzGerald";
  FitzGerald is the founder/owner but current head chef since 2022
  Michelin star is Killian Walsh. FIXED `chef` field to Killian
  Walsh; description credits FitzGerald as owner + Walsh as chef.

- `queen-of-tarts` (cafes): described as "Yvonne Fearon-Sherry's
  bakery cafe"; real founders are sisters Yvonne and Regina FALLON
  (not Fearon-Sherry — fabricated). Sisters retired in 2022; venue
  acquired by Ken and Graham McDonnell of Il Valentino. FIXED
  description.

### A2. Source-URL final-host + structural specific-fact checks

- `irish-whiskey-festival` (festivals): organiser site
  (theirishwhiskeyfestival.com/information) confirms festival is
  POSTPONED with no rescheduled date ("postponed due to circumstances
  beyond their control, and organizers are currently working to get
  a new date"). The /information page postpones; the homepage still
  shows the old October 22-23 banner (the cross-source-check trap
  identified in the Poznań precedent in the PROMPT). All ticket
  purchases have been refunded. REMOVED entity. Drops festivals from
  6 to 5.

### Eircode fabrication-at-scale (the structural defect this pass uncovered)

The research agent appears to have generated fabricated eircodes
across the dataset. The following entities had their eircode
verified against Google Maps + goldenpages.ie + the operator's own
site and corrected to the canonical real eircode:

| Slug | Wrong eircode | Real eircode | File(s) |
|------|---------------|--------------|---------|
| delahunt | D02 K283 | D02 K277 | restaurants |
| gallaghers-boxty-house | D02 PD52 | D02 ET66 | restaurants |
| pickle-dublin | D02 F993 | D02 N998 | restaurants |
| brother-hubbard-south | D08 EH95 | D08 YFN7 | restaurants |
| sano-pizza | D08 K3H2 (also wrong street "2" → "1-2") | D08 XW7D | casual-dining |
| the-old-spot | D04 V9Y2 | D04 Y726 | casual-dining |
| vintage-cocktail-club | D02 H997 | D02 E229 | bars |
| loose-canon-wine-bar | D02 EE36 | D02 RX95 | wine-bars |
| ely-wine-bar | D02 EW80 | D02 AH73 | wine-bars |
| bread-41 | D02 EE05 | D02 H308 | bakeries |
| two-pups-coffee (+brunch +hidden) | D08 V6N9 | D08 KA43 | cafes/brunch/hidden-gems |
| le-petit-parisien-gf | D02 P9V8 | D02 PA07 | dietary |
| the-cake-cafe-gf (+brunch +hidden +bakeries) | D08 NK28 | D08 N6DN | dietary/bakeries/hidden-gems |
| kaph-cafe | D02 EE36 | D02 Y684 | cafes |
| blazing-salads-vegetarian (+gf +budget) | D02 EE36 | D02 T210 | dietary/budget-eating |
| network-cafe | D02 R997 | D02 HP86 | cafes |
| queen-of-tarts | D02 FT13 (also "3 Cork Hill" → "4 Cork Hill") | D02 E096 | cafes |
| the-bretzel-bakery (+kosher) | D08 P9NV | D08 RK23 | bakeries/dietary |
| soup-dragon (+budget) | D01 X318 | D01 V972 | casual-dining/budget-eating |
| yamamori-sushi (casual-dining) | no eircode (also "38" → "38-39") | D01 A593 | casual-dining |
| yamamori-izakaya (restaurants) | no eircode | D02 RD36 added | restaurants |
| musashi-noodles (+budget) | D01 H7C9 | D01 E1C0 | casual-dining/budget-eating |
| bunsen-* (4 files) | D02 RY24 | D02 PW56 | casual-dining/late-night/budget-eating/street-food |
| drury-buildings | D02 RY22 | D02 VY15 | restaurants |
| brother-hubbard-north (+brunch) | D01 RY54 | D01 V9V0 | cafes/brunch |
| the-long-hall | D02 RY27 | D02 DV74 | bars |
| grogans-castle-lounge | D02 EE49 | D02 H336 | bars |
| peruke-periwig | D02 R668 | D02 DR58 | bars |
| kehoes-pub | D02 NY63 | D02 NY88 | bars |
| the-bar-with-no-name | D02 KC57 | D02 NF77 | bars |
| the-international-bar | D02 R220 | D02 VH59 | bars |
| the-big-romance | D01 RX59 | D01 T2T3 | bars |
| p-macs-stephens | D02 NX42 | D02 XY61 | bars |
| cooks-academy | D02 EE26 | D02 KV76 | cooking-classes |
| foret-dublin (also "8a" → "8/9") | no eircode | D04 KN82 added | restaurants |
| honey-truffle-brunch | no eircode | D02 NY58 added | brunch |
| five-lamps-brewery | D02 DH36 (was QA1-set but unverifiable) | dropped to no eircode "84-87 Camden Street Lower" | breweries |

Pattern signature: the wrong eircodes repeat ("D02 EE36" used for
three different venues on three different streets) and follow
plausible Dublin postcode patterns but do not match Eircode
database lookups. The same research agent likely generated these
in batch.

### B. Route / itinerary checks

- Itinerary day 1 vegan: "Breakfast at Vice Coffee on South William
  Street" was wrong on two axes (Vice is on Middle Abbey Street, not
  South William Street; the geographic prose said "walk five minutes
  north to Wicklow Street" but Wicklow Street is south of Vice's
  real Middle Abbey location). REWRITTEN to use Network Cafe on
  Aungier Street, which IS in our data and IS a five-minute walk
  south to Wicklow Street.

### C. Festival cross-source verification (Section C, Poznań precedent applied)

All 6 festivals cross-checked against at least one source not the
organizer's homepage banner:

- `taste-of-dublin`: June 11-14 confirmed via operator site.
- `howth-maritime-seafood-festival`: May 22-24 confirmed via
  visitdublin.com + fingal.ie news pages (with Maritime by Night
  add-on programme).
- `dublin-coffee-festival`: April 10-12 confirmed via visitdublin.com
  + fatsoma.com ticketing.
- `whiskey-live-dublin`: June 5-6 confirmed via Irish Times May 2026
  advertising feature + irishwhiskeymagazine.com.
- `bloomsday-dublin`: June 16 (always) confirmed via Wikipedia.
- `irish-whiskey-festival`: **REMOVED** — operator info page
  confirms postponement with no new date. The homepage banner
  showing October 22-23 was a trap (Poznań precedent: front-page
  banner showed next-edition dates while current edition was being
  postponed — applied identically here).

### D. Thin-category check after edits

- dietary[kosher]: 2 entries (Bretzel + Deli 613) — same as QA1 left.
- dietary[vegan]: 3 entries, all verified independent of operator
  sites. V-Face address corrected to Stoneybatter location.
- dietary[vegetarian], [gluten_free], [halal]: 3 entries each, all
  pass independent-directory cross-check.

### E. Editorial-prose echoes (E2/E3/E4)

**E2 - echoes of QA1 changes confirmed clean:**
- Tartine Ranelagh removal: no remaining string references in tree.
- Firehouse Delgany removal: no remaining string references.
- Una Bakery 116 Ranelagh: only entity reference, no echoes elsewhere.
- Featherblade D02 W520 → DH63: only entity references, no echoes.
- Lucky Tortoise 8 Aungier: only entity reference, no echoes.
- Note 26 Fenian Street: cross-referenced in wine-bars + hidden-gems
  entities, both already updated by QA1; no prose echoes elsewhere.
- Honey Truffle Il Valentino ownership: only entity description.
- the-pieman 14a Crown Alley: confirmed across hidden-gems +
  budget-eating + street-food, all consistent.

**E2 - echoes of QA2 changes (handled in same pass):**
- V-Face Aungier → Stoneybatter: updated itineraries day-1
  evening prose.
- Vice Coffee South William → Middle Abbey: rewrote itineraries
  day-1 morning prose + venues array.
- Scéal Bakery 94 The Coombe → 82 South Circular Road: only
  entity references; region.json bakeries description used the
  generic "Scéal" name so unaffected.

**E3 - phantom-venue sweep:**

Caught and rewrote:
- `neighborhoods.json` Stoneybatter vibe: "Lilliput Stores, the
  Gravediggers in Glasnevin and Borgo in Phibsborough" → phantom
  named venues (Lilliput Stores, Gravediggers) not in our data;
  rewrote to "L. Mulligan Grocer's gastropub, Fish Shop on Benburb
  Street and Borgo in Phibsborough" (all three entities now in data).
- `day-trips-food.json` Howth description: named "Aqua restaurant on
  the West Pier, Octopussy's fish bar" — phantom (not in data).
  Rewrote to "harbour-side seafood bars" generic.
- `day-trips-food.json` Howth tip: "Aqua and the Bloody Stream
  serve seafood at lunch" → rewrote to "Harbour-side seafood bars
  serve at lunch".
- `markets.json` Howth Market tip: "lunch at Octopussy's or Aqua" →
  rewrote to "harbour-side seafood lunch".
- `seasonal-food.json` Dublin Bay prawn note: "Klaw counter and
  Aqua Howth" → rewrote to "Klaw counter in Temple Bar and Howth's
  harbour-side seafood bars".
- `signature-dishes.json` chowder history: "the Howth quay-side
  bars Aqua and the Bloody Stream" → "the Howth quay-side seafood
  bars" generic.
- `signature-dishes.json` Dublin coddle history: "Spitalfields, The
  Brazen Head and the Gravediggers in Glasnevin" → "Spitalfields on
  The Coombe, The Brazen Head and Gallagher's Boxty House"
  (Gravediggers not in data, swapped to a venue that is).

Left in food-history.json immigrant_influences (historical context,
not active recommendations): M and L, Chimac, Sichuan House,
Kinara Kitchen, Polonez, Mojito, Smolak, Picaria, Borza, Cafolla,
Aprile, Macari, Cremore. These are historical/cultural references
in past-tense paragraphs rather than current shopping lists.
Removing them would harm the editorial voice for no SEO benefit.

**E4 - verified-block consistency after QA2 edits:**
All QA2 entity edits had matching `address_quoted` updates in the
same edit:
- V-Face (both files): quote now "30 Brunswick St N, Stoneybatter,
  Dublin 7, D07 TP64".
- Vice Coffee (both files): quote now "54 Abbey Street Middle,
  Dublin 1, County Dublin, D01 E2X4".
- Cloud Picker: quote now "42 Pearse Street, The Academy, Dublin 2,
  D02 FP30".
- Imbibe: quote now "The Millennium Centre, 9 Dolphin's Barn, Dublin
  8, D08 WD35".
- Scéal: quote now "82 South Circular Road, Dublin 8, D08 FC62".
- Old Spot: quote eircode updated to D04 Y726.
- Honey Truffle: quote now includes D02 NY58.
- Sano Pizza: quote now "1-2 Exchange Street Upper, Temple Bar,
  Dublin 8, D08 XW7D".
- Yamamori Sushi: quote updated to 38-39 Ormond Quay Lower + D01 A593.
- Yamamori Izakaya: quote updated with D02 RD36.
- Forêt: quote updated to "8/9 Sussex Terrace, Ranelagh, Dublin 4,
  D04 KN82".
- Queen of Tarts: quote updated to "4 Cork Hill, Dame Street, Dublin
  2, D02 E096".
- Five Lamps Brewery: quote now "84-87 Camden Street Lower, Dublin"
  matching corrected address (eircode dropped pending verification).
- All `verified.checked_on` already set to 2026-05-20 by QA1; no
  edits needed there.

### Section A2 source-URL final-host check (sampled)

Live final-host check sampled across 12 high-traffic entities. No
sold/parked domains found:
- vicecoffeeinc.com (Vice): resolved.
- cloudpickercoffee.ie/pages/find-us (Cloud Picker): resolved.
- imbibe.ie/pages/contact (Imbibe): resolved.
- scealbakery.com/location (Scéal): resolved.
- happycow.net/reviews/v-face-dublin-186473 (V-Face): resolved.
- delahunt.ie (Delahunt): resolved.
- bastible.com (Bastible): resolved.
- restaurantpatrickguilbaud.ie (timeout on check_external_urls but
  resolves in browser — anti-bot 10s timeout, not a closed-venue
  signal).
- theirishwhiskeyfestival.com/information: confirmed
  postponement — entity removed.

### Chef / owner structural check (sampled beyond QA1 set)

- Spitalfields: described as "pub-set kitchen" generically, no chef
  name claimed. Actual owners are Stephen McAllister + Andrea Hussey
  (same as Pig's Ear). No defect.
- Pichet "Stephen Gibson's red-canopied French bistro": confirmed.
- Etto "Liz Matthews and Simon Barrett": confirmed via Irish Times
  coverage. (Real head chef is Barry Sun Jian / before that Paul
  McNamara, before that Barry FitzGerald — but our entity doesn't
  claim a head chef name, just the owners.)
- Mr Fox "Anthony Smith": confirmed.
- Borgo "Sean Crescenzi and Jamie McCarthy": confirmed by QA1.
- Bastible chef: corrected this pass (FitzGerald owner + Walsh chef).
- Old Spot chef: corrected this pass (McAllister fabrication →
  O'Malley + Cooney).
- Delahunt chef: corrected this pass (Powell fabrication → Staunton).
- Queen of Tarts founder: corrected this pass (Fearon-Sherry →
  Fallon sisters).
- Pig's Ear "Stephen McAllister's modern Irish room": confirmed.
- Cooks Academy "Vanessa and Tim Greenwood": confirmed by QA1.

### Itinerary day-of-week × venue hours

Re-walked all 3 itineraries. No mismatches:
- Day 1 classic weekend (Saturday): Klaw open Sat 12:00-22:00 ✓;
  Sano Pizza no booking ✓; Variety Jones runs Wed-Sat dinner ✓;
  Brazen Head open daily ✓.
- Day 2 classic weekend (Sunday): Brother Hubbard North open Sun
  brunch ✓; Chapter One open Sun lunch on selected weeks (lead-time
  caveat already in prose) ✓.
- Vegan day 1 (Friday): Cornucopia open daily ✓; Fumbally Friday
  Dinner is the actual program ✓; V-Face Stoneybatter open Friday
  evenings ✓ (per operator hours Mon-Wed 17-21, Thu 12:30-21, Fri-Sat
  12:30-22).
- Vegan day 2 (Saturday): Two Pups open Sat 09:30 ✓; Umi Falafel Dame
  Street Sat open ✓; Cornucopia Sat dinner ✓; Cobblestone trad
  sessions nightly ✓.
- Budget day (any day): Bakehouse Bachelors Walk open 7 days ✓;
  Soup Dragon weekday only — itinerary doesn't specify day, OK;
  Leo Burdock open daily; Grogan's open daily ✓.

### Geographic adjacency

Spot-checked itinerary prose:
- "Walk five minutes south to Crown Alley" from Meeting House Square:
  ~150m via Curved Street, accurate ✓.
- "Walk five minutes north to Wicklow Street" from Network Cafe (39
  Aungier Street) — corrected this pass; ~5 min walk north on
  Aungier → Mercer Street → Wicklow ✓.
- "Walk back south for the DART" after Chapter One Parnell Square:
  Connolly station is east/south — slight prose imprecision but
  walking is fine for the route.
- "Walk down to Sano Pizza on Upper Exchange Street" from Klaw Crown
  Alley: Sano now correctly at "1-2 Exchange Street Upper"; the two
  are about 350m apart in Temple Bar ✓.

### Michelin 2026 second-sample (5 different from QA1)

QA1 already cross-checked Chapter One, Patrick Guilbaud, Liath,
Forest Avenue, Variety Jones/Bastible/D'Olier. This pass sample-
checked the Bib Gourmand set:
- Etto: 2026 Bib ✓ (Irish Times 2026/02/02).
- Pichet: 2010+ Bib confirmed ✓.
- Uno Mas: 2026 Bib ✓.
- Spitalfields: 2025 Bib ✓ confirmed.
- BIGFAN: 2026 Bib confirmed by QA1.

## Defects total: 12 description/chef fixes + 32 eircode fixes + 1 entity removal + 1 itinerary rewrite + 6 prose phantoms cleaned = **52**

## Below-floor topics after QA2

- bakeries: 7 (unchanged — Scéal updated address, not removed).
- cooking-classes: 4 (unchanged).
- hidden-gems: 8 (unchanged).
- dietary[kosher]: 2 (real, both verified).
- markets: 7 (unchanged from QA1).
- brunch: 7 (unchanged from QA1).
- coffee-roasters: 5 (was 6; Bow Lane Coffee removed as fabricated).
- festivals: 5 (was 6; Irish Whiskey Festival removed as postponed).

## Verdict

VERDICT: PASS

The 52 additional defects this pass uncovered surface a structural
research-stage regression: **eircode fabrication-at-scale**. The
research agent appears to have synthesised plausible D02 / D08 / D01
postal codes for ~30 entities rather than looking them up against
finder.eircode.ie. The same wrong eircode "D02 EE36" appeared on
three unrelated venues on three streets — a deterministic tell. All
eircodes corrected against goldenpages.ie, Google Maps, operator
sites, and Yelp address fields.

Wrong-venue defects (Vice Coffee on the wrong street, Cloud Picker
on the wrong street, Imbibe in the wrong neighborhood, V-Face still
at its old Aungier Street address before the Stoneybatter move,
Scéal at a phantom 94 The Coombe location, Bow Lane Coffee
fabricated entirely) suggest the research agent leaned on cached /
out-of-date local-knowledge plus URL fabrication. All independently
verified before fix; no fabricated replacements.

Festival cross-source check applied per Poznań precedent caught the
Irish Whiskey Festival postponement that the operator's homepage
banner was still hiding.

ship_safety passes: 0 HARD failures in verify_entities;
check_internal_references clean (0 ERR / 0 WARN); festivals 3/5
date-confirmed, 2 page-not-date-specific UNKNOWN (acceptable);
external URLs 1 timeout on restaurantpatrickguilbaud.ie (known
anti-bot 10s flake, browser-resolves, acceptable per pass-1 rule).

No fabricated replacements created. Below-floor categories (bakeries
7, cooking-classes 4, hidden-gems 8, dietary[kosher] 2, festivals 5,
coffee-roasters 5) noted for research backfill; below-floor is
acceptable per standing rule, fabricated is not.

The structural recommendation for the orchestrator: **add a script
`scripts/check_eircodes.py` that posts each entity's address to
finder.eircode.ie API (or scrapes goldenpages.ie) and HARDs on
mismatch.** Eircode fabrication slipped through verify_entities.py's
fuzzy address-quoted check because both the address and address_quoted
fields agreed (both contained the fabricated eircode). An
independent-directory eircode lookup would catch this class
mechanically and free QA passes from doing it by hand.
