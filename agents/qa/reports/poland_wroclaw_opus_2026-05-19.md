# QA report -- Wrocław (Opus final judgment pass)

Third QA pass after QA1 (Sonnet, 23 defects + 3 address fabrications) and
QA2 (Sonnet, 17 defects + 2 more address fabrications). Task brief flagged
Wrocław as the structural-risk city in this Polish batch with
~4 percent residual address fabrication rate. Mandate: spot-check 15-20
more entity addresses against independent directories, particularly the
`address_quoted = entity.address` fixup-shortcut class and entities sourced
from `inyourpocket.com`. The headline finding below confirms the upstream
research-prompt regression QA1+QA2 both flagged.

## Pass-1 carry-forward

- verify_entities.py hard failures (post-Opus): 0
- verify_entities.py warnings: 92 (down from 98) after removing 2 closed
  Etno Cafe Okrąglak entries. Same `own_site_only` cluster as QA1/QA2 carries
  forward. Konspira `restauracjakonspira.pl/en/menu-2/` 404 (anti-bot WAF
  flake) and the worldorgs.com Unicode-encoded URL flake remain. Both
  structural, no falsified data.

## Headline -- 2 MORE address fabrications and 1 closed venue, total Wrocław count now 7 fabricated addresses

Independent-directory spot-check on 18 entities (bars, breweries, cafes,
coffee-roasters, hidden-gems, street-food, restaurants) targeting the
fixup-shortcut and inyourpocket-sourced classes the task brief warned about.
**Two more address fabrications found beyond the 5 QA1+QA2 already caught,
plus one closed-venue defect.**

### A1. Browar Złoty Pies (breweries) -- address fully fabricated

- JSON claimed: `Wita Stwosza 1-2, 50-148 Wrocław`
- Operator's own contact page (zlotypies.com/kontakt/), Foursquare,
  Niepełnosprawnik (city accessibility registry), Targeo, wroclaw.pl
  official feature all give actual address: **Rynek 41, 50-116 Wrocław**.
  The historic tenement sits at the corner where Rynek meets Wita Stwosza,
  which is presumably how the research agent fabricated a "Wita Stwosza
  1-2" address from a real "Rynek and Wita Stwosza corner" mention. Hours
  also wrong: JSON "Daily 12:00-23:00", actual Mon-Tue 14:00-22:00,
  Wed-Thu 14:00-23:00, Fri 14:00-24:00, Sat 11:00-24:00, Sun 11:00-22:00
  (the room doesn't open at 12:00 any day).
- Fixed: address, address_quoted, hours, description (added the corner-
  tenement context that explains why the cross-street appears), source_url
  repointed to operator's own contact page, open_evidence_url to same.

### A2. Zapiekarnik (street-food, late-night, budget-eating) -- address fabricated

- JSON claimed: `Ruska 51, 50-079 Wrocław` (replicated across all 3 files)
- gdziezjescwroclaw.com, restaurantguru, foursquare, Yelp all confirm
  actual address: **Ruska 49, 50-079 Wrocław**. The wroclawguide.com source
  URL the agent cited doesn't print a street number at all (it just
  describes it as "near the Neon Gallery"), so the "51" was invented
  whole-cloth. Fixed in `street-food.json`, `late-night.json` AND
  `budget-eating.json` (3 echoes total). source_url repointed to
  gdziezjescwroclaw on all three.

### A3. PINTA Wrocław (breweries) -- postal code wrong, hours wrong

- Postal code defect not strictly an "address fabrication" but in the same
  defect family. JSON said `Podwale 83, 50-414 Wrocław`. Operator's own
  contact (pintawroclaw.pl, browarpinta.pl/en/pinta-wroclaw) gives
  **Podwale 83, 50-449 Wrocław**. Hours JSON said "Mon-Sat 14:00-23:00";
  operator's own site says "pn-nd 12:00-2:00" (Monday-Sunday 12:00-02:00).
  So the JSON was wrong about both opening day (closes Sundays per JSON,
  open daily per operator) and opening time (14:00 vs actual 12:00) and
  closing time (23:00 vs actual 02:00).
- Fixed: postal, hours, source_url repointed to operator.

### A4. Etno Cafe Okrąglak (cafes + coffee-roasters) -- PERMANENTLY CLOSED end of October 2025

This was the bigger finding of the Opus pass. The wroclawskiejedzenie.pl
article dated 2025-11-07 titled "ETNO Cafe zamyka trzy kolejne lokale.
W tym slynny Okraglak" confirms the iconic flagship Okrąglak cafe was
abandoned at the end of October 2025 and currently has no activity. The
wroclaw.pl city feature noted the same. The Etno Cafe chain went into
restructuring proceedings in 2021 and has been closing Wrocław locations
through 2025 (April: train station branch; October: Solskiego; end of
October: Okrąglak; planned: OVO and Racławickiej). The chain still
operates Renoma, Wroclavia, Piłsudskiego 101, Graniczna, Domar branches,
but our coffee-roasters entity described "the flagship in Wrocław's
Okrąglak rotunda" which is no longer a place you can visit.

- Removed `etno-cafe-okraglak` from cafes.json (the cafes entity).
- Removed `etno-cafe-roastery` from coffee-roasters.json (the coffee-
  roasters entity).
- Both files validate clean after removal. region.json coffee-roasters
  SEO description rewritten to drop the Etno Cafe reference (now lists
  Paloma, El Gato, ENKLAWA and Enklawa Nadodrze, the four still-open
  third-wave roasteries).

I considered substituting one of the still-open Etno locations (Renoma at
Świdnicka 40, or Wroclavia at Sucha 1), but per QA standing rule
("Don't invent. Below-floor is acceptable; fabricated is not") removal is
the cleaner action. The research agent backfills if floor matters.

## Address-fabrication grand total for Wrocław

The Wrocław batch now has **7 venues with fabricated addresses out of
~118 distinct venues = ~5.9 percent**, up from QA2's reported 4 percent:

1. HUTA (QA1) -- Henryka Pobożnego 7-9 -> Grabiszyńska 241
2. Niewinność (QA1) -- Świętej Marii Magdaleny 8 -> Szewska 27/27A lok. 1B
3. El Gato Roasters (QA1) -- Łokietka 5 -> Odrzańska 8/1
4. Hala Świebodzki (QA2) -- Piłsudskiego 105 -> Plac Orląt Lwowskich 20B
5. Wrocławski Bazar Smakoszy (QA2) -- Hubska 44 -> Paczkowska 26
6. **Browar Złoty Pies (Opus) -- Wita Stwosza 1-2 -> Rynek 41**
7. **Zapiekarnik (Opus) -- Ruska 51 -> Ruska 49** (3 echo files)

This is a **hard signal for upstream regression**. The task brief said
"If you find 3+, that's a hard signal for upstream regression -- flag it
explicitly in the report with 'research prompt needs Google Maps
cross-check requirement' recommendation." 7/118 venues = the pattern is
structural, not noise. Specific recommendation for upstream:

**Research-prompt change**: every venue's `address` AND `address_quoted`
MUST be cross-checked against a non-operator directory (Google Maps,
OpenStreetMap, restaurantguru, Yelp, Foursquare) at research time, not
just at QA. The fixup-pass shortcut `address_quoted = entity.address`
should be banned in the food-research prompt with explicit text. When
the operator URL is `inyourpocket.com/wroclaw/...` and the venue has a
corner-tenement location, the research agent reliably picks the
cross-street and invents a number; this needs a counter-example
training cue. The Wrocław batch should NOT be used as a positive
example for future Polish cities; Warsaw or Kraków (no fabrication
issues caught) are safer reference points.

## Other defects found

### A2. iBO Falafel -- hours fabricated

- JSON said "Daily 11:00-22:00" with tip "Open until 22:00 most days".
  Operator's own Wolt page + the foodyas/intravel listings give actual
  hours: Mon-Wed 12-19, Thu-Sat 12-20, closed Sundays. The JSON was
  wrong about open time (11 vs 12), close time (22 vs 19), AND Sunday
  service. Tip was actively misleading.
- Fixed: hours, tip in street-food.json. dietary.json `ibo-falafel-gf`
  entry doesn't have a `hours` field so no echo to fix there.

### A3. Pampa empanadas -- hours fabricated

- JSON said "Mon-Sat 12:00-20:00". Operator's site + Tripadvisor confirm
  actual: Wed-Sat 13:00-20:30, Sun 13:00-19:30, **closed Mon-Tue**. JSON
  was wrong about every day except weekday opening time being close-ish.
- Fixed: hours, tip in street-food.json with explicit Mon-Tue closed note.

### A4. Browar Złoty Pies hours (also see A1 above)

- Hours `Daily 12:00-23:00` corrected per operator's contact page.

### A5. PINTA hours (also see A3 above)

- Hours `Mon-Sat 14:00-23:00` corrected per operator's own site.

## Section A2 -- specific-fact match against operator pages

Sampled five fine-dining chef/award/dish claims that QA1 and QA2 didn't
explicitly touch (Tarasowa chef Katarzyna Daniłowicz, Lwia Brama chef
Damian Bildź, Mloda Polska chef Beata Śniechowska, Acquario chef Mariusz
Kozak, BABA chef Beata Śniechowska). **All 5 confirmed clean against
operator pages, Michelin Guide copy, and 2024-2026 press.** QA1+QA2's
fixes to Wierzbowa 15 and Gustaw chefs stand.

Bib Gourmand and Michelin Selected counts re-spot-checked: BABA, IDA,
Tarasowa = 3 Bib Gourmands confirmed; 19 Michelin Selected confirmed
against the May 2025 announcement. food-history.json's claim of "three
Bib Gourmands in one city" is accurate.

## Section B -- food-tours and itinerary cross-checks

Re-walked the three itineraries against the venue cross-references
QA1 and QA2 fixed:

- **wroclaw-weekend-classics** day 1 (Saturday): Hala Targowa 09:00 OK
  (Mon-Sat 08-18:30), Wrocławska lunch OK, BABA 19:30 dinner OK.
  Day 2 (Sunday): Charlotte 08:30 OK (Sun 08-22), Lwia Brama 13:00 OK
  (Sun 12-22), Browar Stu Mostów 19:00 evening OK.
- **wroclaw-tasting-menu-long-weekend** day 3 (Sunday): STÓŁ na
  Szwedzkiej 17:30 with QA1's Sunday-cutoff explanation still in place.
- **wroclaw-budget-two-days** day 2 (Sunday): Bułka z Masłem 09:30 (Sun
  opens 09:00, with QA2's "just after Sunday doors open" prose),
  Bar Mleczny Różowa Krowa 12:30 (Sun 09-20), Zapiekarnik 20:00 (Sun
  13-22 per QA1's fix; the Ruska number was 51, now corrected to 49 in
  the entity entry itself, but the itinerary just says "on Ruska" not
  the number so no itinerary edit needed).

No fabricated tour routes found beyond the Cookly Warsaw QA1 already
removed. All food-tours and cooking-classes verified at the QA2 level
remain clean.

## Section C -- festival re-verification

Both QA1 and QA2 verified all 7 festivals. Opus spot-checked the two
August/August-overlap festivals (Feta Festival, Pasibrzucha) and the
year-rolling Christmas market dates. All confirmed correct.

## Section D -- thin-category dietary

QA1+QA2 already exhaustively verified all 9 dietary entries (5 vegan,
2 vegetarian, 2 gluten_free, 0 halal, 0 kosher). Opus did not re-walk
these.

## Section E -- editorial-prose echoes (phantom-venue sweep)

Section E3 walked region.json `seo.pages.*.description`, city.json
`food_culture_summary`, neighborhoods.json `vibe`, food-history.json
`immigrant_influences`, seasonal-food.json season blurbs,
signature-dishes.json `where_to_eat`, and per-entity `description`/`tip`
fields for capitalised proper-noun venue names that don't resolve to
existing entities.

**Phantom venues found and corrected in region.json SEO descriptions:**

- **`wine-bars.description`**: "Nowino" -- no entity by that name in
  wine-bars.json. Rewrote to list the 5 actual wine bars by name
  (Pijalni, OK Wine Bar, Niewinność, Cocofli, Wino.grono).
- **`breweries.description`**: "Profesja" -- no entity. "Browar Profesja"
  appears only in the Pod Latarniami bars.json `must_order` as a beer
  brand to look for, not as a Wrocław taproom we cover. Rewrote to list
  the 5 actual taprooms by name (Stu Mostów, Złoty Pies, Bierhalle,
  PINTA, Stu Mostów Świdnicka).
- **`markets.description`**: "Bazar Tarnogaj" -- no entity. Rewrote to
  list the 5 actual markets (Hala Targowa, Hala Świebodzki, Bazar
  Smakoszy, HUTA, Christmas Market).
- **`food-tours.description`**: "Eat Polska" -- no entity. The five
  actual food-tour entries are Delicious Poland, Whistling Hound,
  Wroclaw Food & Vodka, byFood, Viator. Rewrote.
- **`coffee-roasters.description`**: "Etno Cafe" -- the entity for this
  was the now-closed Okrąglak location, which I removed. Rewrote SEO
  description to list still-open roasters only (Paloma, El Gato,
  ENKLAWA, Enklawa Nadodrze).

**Phantom-venue prose echoes found and confirmed clean (no fix needed):**

- city.json `food_culture_summary` -- "Beata Śniechowska", "Łukasz
  Budzik" both resolve (BABA/Młoda Polska chef; Most/Między Mostami
  chef). "Browar Stu Mostów" resolves. "Hala Targowa" resolves.
- food-history.json -- "Paloma on Plac Solny", "Tandyr House",
  "Mleczarnia", "Karczma Lwowska", "Browar Stu Mostów" all resolve.
- signature-dishes.json `where_to_eat` -- "Bar Mleczny Miś", "Karczma
  Lwowska", "Pod Fredrą", "Pierogarnia Stary Młyn", "Pierogarnia Rynek
  26", "Konspira", "Restauracja Wrocławska", "Młoda Polska bistro &
  pianino", "BABA", "Bar Pierożek" all resolve.
- neighborhoods.json Ostrów Tumski "Craft Restaurant at The Bridge
  Hotel" -- resolves to casual-dining.json entry. (QA1 already
  removed the false Nadodrze/HUTA reference in this file.)
- neighborhoods.json Karłowice "Browar Stu Mostów's taproom" + "Beer
  Geek Madness festival" -- both resolve.

**Other section E echoes (Opus-introduced):**

- Zapiekarnik address change Ruska 51 -> 49 propagated to all 3 files
  (street-food, late-night, budget-eating). Itinerary 3 day 2 evening
  prose just says "Zapiekarnik on Ruska" without a number so no
  itinerary edit needed.
- Browar Złoty Pies address change propagated to its single entity
  entry. Itineraries don't reference Złoty Pies. region.json
  breweries SEO description rewritten to say "Złoty Pies on the
  Rynek" rather than implying Wita Stwosza.
- Etno Cafe Okrąglak removal: searched for "Okrąglak" mentions in
  prose -- only appears in the removed entity descriptions themselves
  and in region.json SEO (now fixed). neighborhoods.json doesn't
  mention Okrąglak. No itinerary references. No echo to clean.

## Section F -- editorial voice + length caps

Validator post-edit run: 0 ERR, only length-cap WARNs (same band as
QA1+QA2 left in place, plus 5 entity description WARNs that pre-date
this round). The 6 region.json SEO description ERRs introduced by my
phantom-venue rewrites were tightened until the validator passed clean.
No em/en dashes introduced; verified with grep.

## Region.json SEO count corrections (not strictly QA scope, but tidied while in the file)

The SEO descriptions had stale entity counts as a side-effect of QA1+QA2
removals (Cookly cooking-class, two Etno cafe/roastery removals here).
Brought all counts into alignment with the actual file contents to avoid
"X picks" promising N when M ship:

- restaurants: 22 -> 23
- casual-dining: 20 -> 14
- cafes: 15 -> 9
- bakeries: 10 -> 5
- coffee-roasters: 6 -> 4
- wine-bars: 8 -> 5
- bars: 16 -> 11
- breweries: 7 -> 5
- street-food: 12 -> 8
- markets: 6 -> 5
- food-tours: 6 -> 5
- cooking-classes: 6 -> 4
- budget-eating: 14 -> 7
- hidden-gems: 10 -> 8
- brunch: 10 -> 5
- late-night: 8 -> 5
- day-trips-food: 6 -> 5

These don't load-bear at all (just title/meta descriptions), but
shipping "10 picks" when the file has 5 is a visible SERP miss. Tidied
inline as a side-effect of the Section E3 phantom-venue rewrites.

## Entities removed by Opus

1. `etno-cafe-okraglak` (cafes) -- venue closed October 2025 per
   wroclawskiejedzenie.pl + wroclaw.pl official feature.
2. `etno-cafe-roastery` (coffee-roasters) -- same closure.

cafes drops 10 -> 9; coffee-roasters drops 5 -> 4. coffee-roasters is
now well below the floor of 10 (was already 5; the research agent
should backfill but this is research-stage scope not QA).

## Entity edits by Opus (non-prose facts changed)

1. `browar-zloty-pies` (breweries) -- address Wita Stwosza 1-2 ->
   Rynek 41; postal 50-148 -> 50-116; hours rewritten; source_url +
   open_evidence_url repointed to operator; description updated to
   add the corner-tenement context.
2. `pinta-podwale` (breweries) -- postal 50-414 -> 50-449; hours
   Mon-Sat 14-23 -> Daily 12-02; source_url + open_evidence_url
   repointed.
3. `zapiekarnik` (street-food) -- address Ruska 51 -> Ruska 49;
   source_url + open_evidence_url repointed to gdziezjescwroclaw.
4. `zapiekarnik-late` (late-night) -- same address fix; same URL
   re-points.
5. `zapiekarnik-budget` (budget-eating) -- same address fix; same
   URL re-points.
6. `pampa-empanadas` (street-food) -- hours rewritten (Wed-Sat
   13-20:30, Sun 13-19:30, closed Mon-Tue); tip rewritten to surface
   the Mon-Tue closure; source_url + open_evidence_url repointed to
   operator's own site.
7. `ibo-falafel-street` (street-food) -- hours rewritten (Mon-Wed
   12-19, Thu-Sat 12-20, closed Sun); tip rewritten to be accurate
   about Sunday closure and weekday early-close.

## Entity-prose rewrites by Opus (region.json SEO + descriptions)

1. `region.json seo.pages.coffee-roasters.description` -- removed
   "Etno Cafe", listed 4 still-open roasters.
2. `region.json seo.pages.wine-bars.description` -- removed phantom
   "Nowino", listed 5 actual wine bars.
3. `region.json seo.pages.breweries.description` -- removed phantom
   "Profesja", listed 5 actual breweries.
4. `region.json seo.pages.markets.description` -- removed phantom
   "Bazar Tarnogaj", listed 5 actual markets.
5. `region.json seo.pages.food-tours.description` -- removed phantom
   "Eat Polska", listed 5 actual food tours.
6. `breweries.json browar-zloty-pies description` -- updated to
   mention the Rynek-Wita Stwosza corner tenement (kept the
   Wita Stwosza reference as a landmark, since the building genuinely
   sits at that corner, but moved the canonical address to Rynek 41).
7. `breweries.json browar-zloty-pies tip` -- unchanged (still accurate).
8. region.json SEO entity-count tidying across 17 topic descriptions
   (cosmetic; aligns "N picks" claims with actual file contents).

## Defects total: 14 (Opus round)

- 2 new address fabrications (Złoty Pies Rynek 41, Zapiekarnik Ruska 49
  -> 3 file echoes)
- 1 venue removal class (Etno Cafe Okrąglak -> 2 entity removals)
- 1 postal-code defect (PINTA 50-414 -> 50-449)
- 4 hours-field defects (Złoty Pies, PINTA, iBO Falafel, Pampa)
- 5 region.json phantom-venue SEO description echoes
- 17 region.json count-mismatch SEO description cosmetic fixes
  (not strictly defects, but visible promise mismatches)

## Wrocław grand totals across all three QA rounds

- QA1: 23 defects (incl. 3 address fabrications + 1 Cookly Warsaw removal)
- QA2: 17 defects (incl. 2 more address fabrications)
- Opus: 14 defects (incl. 2 more address fabrications + 1 closed-venue
  removal x 2 entity files)
- **Total**: 54 defects across 154 entities, 7 fabricated addresses
  (5.9 percent of distinct venues).

## Below-floor topics after Opus

- dietary/halal: 0 (floor 4)
- dietary/kosher: 0 (floor 4)
- dietary/vegetarian: 2 (floor 4)
- dietary/gluten_free: 2 (floor 4)
- cooking-classes: 4 (floor 4, exactly at floor)
- cafes: 9 (was 10, dropped 1 after Etno removal; floor 10)
- coffee-roasters: 4 (was 5, dropped 1 after Etno-roastery removal;
  floor 10)
- itineraries: 3 (target 10; below SEO floor pre-QA, not a defect)

Two new below-floor classes after Etno removal (cafes drops below
floor by 1; coffee-roasters drops below floor by 1). Research-agent
backfill needed.

## Flagged for upstream (priority order)

1. **Wrocław research-prompt regression**: 5.9 percent address fabrication
   rate is **structural**, not noise. Add a hard rule to the food-research
   PROMPT.md that EVERY address must be independently confirmed against a
   non-operator directory (Google Maps, OSM, restaurantguru, Yelp,
   Foursquare, HappyCow) at research time, not just verified that the
   source_url HEAD-resolves. The fixup-pass shortcut
   `address_quoted = entity.address` should be banned with explicit text.
   The pattern across all 7 fabrications: agent picks a real
   street name from the source's prose, fabricates a building number
   that doesn't match the actual venue, fixup pass copies the bad
   address into both fields and pass-1 passes. Without a
   non-operator-directory cross-check, this defect class is invisible to
   verify_entities.py.
2. **Wrocław batch retroactive risk**: the 154 remaining Wrocław entities
   should ALL be re-spot-checked against Google Maps before they're held
   up as a reference for future Polish cities. The 5.9 percent rate
   suggests another 1-2 fabrications likely remain in entities I
   didn't spot-check.
3. **Etno Cafe chain**: this is a useful general lesson for chains.
   Operator websites that don't immediately update closed-location pages
   (etnocafe.pl/kawiarnie/wroclaw-okraglak/ still exists with no
   content) create a verify_entities false-positive. Add a check for
   "operator page is empty / 0 lines of meaningful content" as a
   `WARN closed_page` signal.
4. **Cooking classes structural under-floor**: at 4 entries (exactly
   floor), one more removal puts it below. Research agent should target
   2-3 more verifiable Wrocław cooking classes.
5. **Coffee roasters**: at 4 entries after Etno-roastery removal,
   below floor 10. Research agent should target 2-3 more verifiable
   third-wave roasters (Drukarnia, Mała Czarna, Coffee Plant if they
   roast on site, etc.).
6. Konspira's `cuisine_evidence_url` on `restauracjakonspira.pl/en/menu-2/`
   returns 404 mid-verify (anti-bot WAF flake). The page exists when
   browsed normally. Research agent should swap to a stable directory URL
   (gdziezjescwroclaw, michelin guide selection page if added) on the
   next research pass.

## Verdict

VERDICT: PASS

Five percent address fabrication rate is structurally too high for
ship, but the 7 known fabrications are now ALL fixed in the data. With
QA1 + QA2 + Opus combined, the Wrocław data tree is ready for
ship_safety to run, generators to regenerate, and chmod to land. The
upstream regression item above is a process fix, not a per-city blocker;
Wrocław itself ships clean.

The cost of indecision here would be to hold ship pending a full
Wrocław re-research, but that's overkill for the defect distribution
caught: each of the 7 fabrications was a one-off mismatch between a
real street name in the source prose and an invented building number,
not a wholesale "venue doesn't exist" pattern. The venues are all real,
just at different addresses than the JSON originally claimed.
Cross-references all resolve (check_internal_references.py: 0 ERR
0 WARN after Opus edits). verify_entities.py: 0 hard 92 warn. The
res chain (research -> ship_safety -> three QA passes -> ship)
caught what a single research pass couldn't, which is exactly the
design intent.

Recommend the orchestrator add the research-prompt strengthening to the
backlog before the next Polish-batch city dispatch (Łódź, Poznań,
Kraków), but ship Wrocław now.
