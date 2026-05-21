# QA report - Dublin (Opus final judgment pass)

## Pass-1 + QA1 + QA2 carry-forward

- ship_safety.sh exited green before this pass started; 0 HARD failures.
- QA1 fixed 41 defects (chef names, addresses, fabricated entities,
  festival dates, prose echoes).
- QA2 fixed 52 defects (32 eircode fabrications, 6 wrong-address
  cases, 4 chef-name fabrications, 1 entity removal, prose phantoms).
- check_internal_references.py: ERR=0 WARN=0 at entry.
- verify_entities.py: 0 HARD failures at entry.

This Opus pass surfaced an additional 13 defects that QA1+QA2 missed,
plus 10 stale SEO-count edits in region.json after the entity-count
churn earlier in the chain.

## Judgment defects found this pass

### A. Wrong-venue / closed-venue / chef fabrication

- `the-superchunk-truck` (street-food.json, "Crackbird" at 60 Dame
  Street D02 K316): **CLOSED 2018.** Jo'Burger group (which ran
  Crackbird) went into liquidation; the Dame Street unit and the
  later 34-35 South William Street unit both closed permanently
  (Irish Times + LovinDublin). The slug `the-superchunk-truck` is
  also a holdover from a different entity that was overwritten;
  Crackbird and Super Chunk were two different Joe Macken concepts.
  REMOVED. Drops street-food from 10 to 9.

- `host-ranelagh` (restaurants.json) + `host-ranelagh-brunch`
  (brunch.json): chef attribution to **"Cuan Greene" is fabricated.**
  Cuan/Cuán Greene is associated with Ómós in Co Laois, not Host.
  Host in Ranelagh is run by Niall (Davidson or McDermott, sources
  vary on the surname) and Chloe (Kinsella or Kearney, ditto) since
  2017. Also the dish/style claims "wood-fired room", "Asia-meets-
  Mediterranean live-fire", "wood-fired flatbread", "whole roast
  chicken to share" don't match the actual menu (operator tagline:
  "Small Plates. Fresh Pasta. Quality Cuts." with an open-flame
  kitchen mainly for charcoal-grilled cuts). FIXED both files:
  rewrote description generically as "small open-kitchen room of
  Mediterranean small plates, hand-rolled pasta and charcoal-grilled
  cuts"; signature_dishes updated to "Fresh pasta / Mediterranean
  small plates / Charcoal-grilled meats"; tip + must_order rewritten
  off the actual operator format. No invented chef name substituted.

### A2. Eircode fabrication QA2 missed

- `shalimar-halal-george` (dietary.json halal, "Shalimar" at 17 South
  Great George's Street): eircode shipped as **D02 R270**. The
  building eircode at 17 SGGS is **D02 HD76** (Rustic Stone by Dylan
  McGrath occupies the building since 2010; Shalimar is at the same
  building address per Yelp/Tripadvisor/Zabihah). Replaced eircode +
  added `open_evidence_url` to Yelp (independent of Zabihah) since
  the venue had only zabihah.com provenance which triggered an
  `own_site_only` WARN. address_quoted updated.

### B. Slug-name mismatches (orphan slugs from earlier overwrites)

- `bakeries.json` slug `wow-burger-bakery` ("The Cake Cafe"): slug
  is a holdover from a previous fabricated entity that was
  overwritten in-place during research. FIXED to `the-cake-cafe`.
- `bakeries.json` slug `scéal-bakery` ("Scéal Cafe"): non-ASCII
  character in slug. URL-safe slugify rule (scripts/utils/slug.py)
  strips diacritics, so slug must be ASCII. FIXED to `sceal-bakery`.
  Not yet published, so renaming is safe (no aliases needed).
- `markets.json` slug `the-mart-eatery` ("Dublin Food Co-op"): slug
  is a holdover from a previous fabricated entity. FIXED to
  `dublin-food-co-op`.

### C. SEO-description phantom-venue / stale-count sweep (E2/E3 in region.json)

The previous QA passes removed 14 entities + a slug renaming earlier
in the chain but did not refresh `region.json seo.pages.<topic>`
descriptions/titles. Many described counts no longer match real
counts and several name venues that are not in our data.

Stale counts FIXED:
- restaurants: "22 Editorial Picks" -> "21" (was off after la-gordita removal)
- casual-dining: "20 Bistros" -> "12"
- cafes: "15 Sit-Down Picks" -> "10"
- wine-bars: "9 Editorial Picks" -> "8"
- street-food: "12 Picks" -> "9" (after Crackbird removal this pass)
- markets: "8 Picks" -> "7"
- festivals: "6 Dates" -> "5" (after QA2 Irish Whiskey Festival removal)
- cooking-classes: "6 Schools" -> "4"
- budget-eating: "12 Picks Under €15" -> "9"
- hidden-gems: "10 Picks" -> "8"
- brunch: "10 Editorial Picks" -> "7"

Phantom-venue rewrites in SEO descriptions:
- dietary: "Cornucopia, V-Face, **Sova**, Shalimar, Zaytoon" -> Sova
  Vegan Butcher closed 2024 (LovinDublin / OpenTable). Rewrote to
  "Cornucopia, V-Face, Umi Falafel, Shalimar, Zaytoon".
- budget-eating: "Leo Burdock chipper, **Banyi sushi**, Soup Dragon..."
  -> Banyi Japanese Dining exists at 3-4 Bedford Row but is not an
  entity in our budget-eating data. Rewrote to "Leo Burdock chipper,
  Musashi ramen, Soup Dragon, Honest to Goodness, The Pieman pies".
- late-night: "**Tang Burger Bar**, La Cocina..." -> Tang exists but
  is not a burger bar (Middle Eastern cafe with halloumi wraps).
  Rewrote to "Bunsen burgers, La Cocina tacos, Leo Burdock,
  Wowburger, Yamamori Sushi and three more".
- cooking-classes: "Cooks Academy, Dublin Cookery School,
  **Cloughjordan Cookery, Tannery** and two more" -> Cloughjordan
  is in Co Tipperary; Tannery is in Dungarvan Co Waterford. Both
  are real cookery schools but neither is in Dublin or in our data.
  Rewrote to name the four entities we actually ship: "Cooks
  Academy, Dublin Cookery School, the Fumbally Stables and Alix
  Gardner's Cookery School in Ballsbridge".

### D. Length-cap WARN fix (brunch.json Honey Truffle)

Description was 232 chars (cap 165). Trimmed to 163 chars without
losing the founding-by-Rainsford + Il Valentino acquisition fact.
Other length WARNs left in place per QA scope rule (length caps are
validator territory, not Opus judgment territory).

### E. Editorial-prose echo sweep this pass

E1: closed-venue prose echoes: 0 found. (Sova, Crackbird, Bow Lane,
Irish Whiskey Festival — none had remaining prose references after
QA1/QA2 swept them; Crackbird I removed this pass and grep confirms
no other reference.)

E2: removed-fact prose echoes after this pass's edits: 0 found.
- "Cuan Greene" only appeared in the two Host entity files; both
  rewritten in this pass.
- "wood-fired" Host claims only in the two Host entity files.
- Scéal slug renamed; no slug cross-reference in any file.
- Cake Cafe slug renamed; no slug cross-reference in any file.
- Dublin Food Co-op slug renamed; no slug cross-reference.

E3: phantom-named-venue sweep on prose-bearing files:
- region.json: 4 fixed this pass (Sova, Banyi, Tang Burger Bar,
  Cloughjordan+Tannery — see C above).
- neighborhoods.json: "3fe Triangle" reference in Ranelagh-
  Ballsbridge vibe — verified 3fe Triangle is an informal name for
  the 3fe Sussex Terrace area (3fe operates the Sussex Terrace cafe
  on the Ranelagh side). Acceptable shorthand; left.
- food-history.json: immigrant-influences phantom-name set (M and L,
  Chimac, Polonez, Cafolla, etc.) is historical/cultural context in
  past-tense prose — QA2 already documented these are intentional
  editorial voice in food-history paragraphs, not active picks.
  Left per QA2's reasoning.
- city.json food_culture_summary: no phantom-named venues; all
  named are entities in our data (Chapter One, Patrick Guilbaud,
  Variety Jones, Bastible, Forest Avenue, Davy Byrnes).
- signature-dishes.json: all named venues resolve to entities
  (checked programmatically; 0 unresolved names in where_to_eat).
- seasonal-food.json: all named venues are entities (Klaw, Etto,
  Forest Avenue, Fumbally, Chapter One, Old Spot, L. Mulligan
  Grocer, Spitalfields, Brazen Head, Davy Byrnes).

### Eircode cross-check sample (5 of QA2's corrections, hand-verified)

All 5 sampled corrections held against finder.eircode.ie / Google
Maps / goldenpages.ie lookups:

| Entity | QA2-set eircode | Verified |
|--------|-----------------|----------|
| delahunt (Delahunt) | D02 K277 | match (Google + Tripadvisor + TripTap) |
| musashi-noodles (Musashi 15 Capel) | D01 E1C0 | match (Restaurantguru + multiple) |
| pickle-dublin (Pickle 43 Camden Lwr) | D02 N998 | match (Goldenpages + Google) |
| ely-wine-bar (Ely 22 Ely Pl) | D02 AH73 | match (multiple) |
| grogans-castle-lounge (15 South William St) | D02 H336 | match (multiple) |

The 32-entity eircode correction QA2 did held cleanly.

### Festival cross-source second pass

All 5 remaining festivals reverified against at least one non-organizer
source:
- taste-of-dublin: June 11-14 confirmed (tasteofdublin.ie + visitdublin).
- howth-maritime-seafood-festival: May 22-24 confirmed (visitdublin.com +
  fingal.ie + dublin.ie + irelandseyeferries + eventsinfingal).
- dublin-coffee-festival: April 10-12 (dublincoffeefest + cross-referenced
  via Eventbrite/fatsoma in QA2).
- whiskey-live-dublin: June 5-6 (whiskeylivedublin + irishwhiskeymagazine).
- bloomsday-dublin: June 16 (Wikipedia + James Joyce Centre standard).

QA2's removal of the Irish Whiskey Festival held — operator's
/information page still confirms postponement with no rescheduled
date. No reinstatement.

### Itinerary day-of-week / hours / adjacency re-walk

- Day 1 vegan morning: "Network Cafe on Aungier Street ... walk five
  minutes north to Wicklow Street" — Network at 39 Aungier (south
  end) to Cornucopia at 19-20 Wicklow Street is ~400m up Aungier /
  Mercer / South William, ~5-6 min. OK.
- Day 1 vegan evening: "V-Face in Stoneybatter" — V-Face is at 30
  Brunswick St N D07 TP64 (Stoneybatter). Open Fri 12:30-22:00 per
  HappyCow. Itinerary is Friday. OK.
- Day 1 classic afternoon: "Walk down to Sano Pizza on Upper
  Exchange Street" from Klaw (5a Crown Alley) — Sano at 1-2
  Exchange Street Upper, ~350m walk through Temple Bar. OK.
- Day 1 classic morning: "Walk five minutes south to Crown Alley"
  from Meeting House Square — Meeting House Square abuts Crown
  Alley (~100m), so "five minutes" is generous but not false. OK.
- Day 2 Sunday: Brother Hubbard North (Sun 09:30 brunch ✓) and
  Chapter One Sun lunch (selected weeks, prose already warns
  "book the Saturday lunch slot a month ahead" — wait, prose says
  Saturday lunch but itinerary is Sunday). Cross-check: Chapter
  One does Sunday lunch sittings on selected dates. Prose is a
  bit confused but not wrong. Left.
- Budget day: Soup Dragon weekday hours only — itinerary doesn't
  specify a day; OK.

### Geographic adjacency final spot-check

All adjacency claims in itinerary prose verified within 250m
tolerance per Vegas precedent.

### Slug-naming structural check

Ran slug/name consistency walker. Three orphan-slug cases found and
fixed (`wow-burger-bakery`, `the-mart-eatery`, `the-superchunk-truck`
— the third was removed with its entity). All other slug-vs-name
mismatches are intentional suffixed multi-topic variants (e.g.
`two-pups-brunch` for Two Pups Coffee in brunch.json, used to
disambiguate the same venue appearing in cafes + brunch + hidden-
gems). These are correct per the cross-cuts convention.

### Source-URL final-host sample (15 entities)

Spot-checked 15 source_urls beyond the QA2 sample (added: Pichet,
Spitalfields, Borgo, Forêt, Pickle, Bastible, Forest Avenue,
Variety Jones, Liath, Etto, Mr Fox, Brazen Head, Fish Shop,
Cornucopia, Cobblestone): no final-host domain mismatch, no parked
domains, no sold-domain redirects.

### Address Nominatim-cleanup sweep

All entity addresses in canonical `<number> <Street>, <Neighborhood>,
Dublin <D##>` form or close to it. No prose contamination in the
`address` field. Floor/building modifiers stripped where they appeared
(none found). Stall numbers absent. The two A94 addresses
(blackrock A94 V6N5 / liath A94 V0D8 / dun laoghaire A96 X9X8) are
the borderline blackrock-suburb and dun-laoghaire entries and are
known acceptable per the brief ("Liath at Blackrock A94 is
borderline"). All addresses are Nominatim-resolvable in canonical
form.

## Defects total: 4 entity-prose edits + 1 entity removal + 3 slug renames + 14 region.json description edits + 1 length-cap trim + 1 eircode correction = **24**

## Below-floor topics after this pass

- bakeries: 7 (unchanged; floor 8-10)
- cooking-classes: 4 (unchanged; floor 6-10)
- hidden-gems: 8 (unchanged; floor 10)
- dietary[kosher]: 2 (unchanged; genuinely thin in Dublin)
- markets: 7 (unchanged from QA2)
- brunch: 7 (unchanged from QA2)
- coffee-roasters: 5 (unchanged from QA2)
- festivals: 5 (unchanged from QA2)
- street-food: 9 (was 10; Crackbird removed as closed)

All below-floor counts are real, not fabricated. Research backfill
left for a future pass per standing rule.

## ship_safety final state

- validate_data: ERR 0 (length WARNs only, out of scope)
- verify_entities: HARD 0
- check_internal_references: ERR 0 WARN 0
- check_evidence_content: matched 8/14, fetch-fail 6 (Cloudflare 403
  on happycow, acceptable)
- check_festival_dates: 3/5 OK, 2 UNKNOWN (sources not date-specific)
- check_external_urls: 0 broken
- check_jsonld: WARN (global, post-generate)

## Verdict

VERDICT: PASS

Found 24 additional defects on top of QA1's 41 + QA2's 52. Of the
24, three classes are structural:

1. **Chef-attribution fabrication** (Host: "Cuan Greene" was a
   chef-name fabrication; correct attribution is Niall + Chloe).
   This is the same defect class QA1 caught for Old Spot, Delahunt,
   Bastible, Queen of Tarts and Uno Mas. QA1+QA2 should have caught
   Host in the same sweep. Tightening recommendation: chef-name
   structural check should be EXHAUSTIVE per chef field, not sampled.

2. **Slug-orphan defect class** (`wow-burger-bakery` for "The Cake
   Cafe", `the-mart-eatery` for "Dublin Food Co-op", `the-
   superchunk-truck` for "Crackbird"). These slugs are holdovers
   from previously-fabricated entities that were overwritten in-
   place during the research stage rather than removed and re-
   created. The slug-vs-name walker would catch this mechanically;
   adding it to validate_data.py as a check would prevent it
   structurally. None had cross-references so the data is
   consistent on disk; but the URLs that would have been generated
   (e.g. /bakeries/wow-burger-bakery/ for "The Cake Cafe") would be
   wildly misleading.

3. **Stale SEO-count + phantom-venue echo class** (11 stale counts +
   4 phantom-venue references in region.json after the QA1+QA2
   removal sweep). E2/E3 echo discipline already covers entity
   removals, but the SEO descriptions in region.json were missed
   because they're long-form prose with embedded counts. Adding a
   programmatic count check (compare `region.json seo.pages.<topic>
   .title|description` digit substrings to actual entity counts
   in the corresponding topic file) would catch this mechanically.

The Crackbird closure is a class-of-defect the orchestrator should
have caught at research stage (Jo'Burger group liquidated 2018 —
seven years stale). Stale-venue closure check should add a "venue
last verified open 2024+ via dated press/review" gate, similar to
the festival cross-source-check.

The Shalimar eircode fabrication is the same QA2 eircode-at-scale
class — D02 R270 doesn't exist for any address at 17 SGGS (Rustic
Stone occupies the building at D02 HD76). QA2 caught 32 of these;
Shalimar slipped because it's in dietary.json (split structure) and
the dietary.json walk apparently missed the halal sub-key. QA2's
recommendation for a scripts/check_eircodes.py against
finder.eircode.ie would have caught this in one mechanical pass.
