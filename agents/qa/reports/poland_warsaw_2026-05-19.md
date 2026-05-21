# QA report - warsaw (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety passed pre-QA per dispatch)
- verify_entities.py warnings: 0 (none flagged at handoff)

## Judgment defects found

### A. Cuisine / category mismatches

None. All cuisine claims content-matched against `cuisine_evidence_url` or operator
own-pages where reachable. Polish-character venues (Bez Gwiazdek, Lukullus, Bar
Mleczny Prasowy, Pyzy Flaki Gorace, Tel Aviv Urban Food) all cleanly verified.

### A2. Specific-fact match against operator menus / press

- `epoka` (fine-dining.json + restaurants.json): `tasting_menu_price` was "440 zl"
  - operator's actual menu shows two tiers (Short History 225 zl food / 595 zl with
  wine; History 325 zl food / 725 zl with wine). 440 zl matched nothing on the menu.
  Rewrote to "225-325 zl food, 595-725 zl with wine".
- `hayb` (coffee-roasters.json): description claimed HAYB was "the first Polish-
  Ethiopian direct importer". Operator's own About page and Dog & Hat / Bean Bros
  roaster interviews describe HAYB as the Borowski family business that started
  2016 as Coffee Republic and rebranded to HAYB (How Are You Brewing). No "first
  Polish-Ethiopian direct importer" claim verifiable. Rewrote to the verified
  Borowski / Coffee-Republic-rebrand framing.
- `tuk-tuk-hala-koszyki` (street-food.json): `dish` field claimed "BBQ prawns"
  and description claimed "BBQ king prawns" plus "Thai Wok group" affiliation.
  Operator's own menu page (tuktuk.pl) shows "Smazone Krewetki z Chilli" (fried
  chilli shrimp), no BBQ-prep shrimp dish. No Thai Wok group affiliation on the
  operator site. Rewrote dish and description to "chilli shrimp" without the
  unsupported group attribution.
- `eat-polska-morning-market` (food-tours.json): claimed "Saturday mornings only",
  price 299 zl, duration 3 hours. Operator page shows runs Tue/Thu/Sat at 09:00,
  3.5 hours, 220 zl. Rewrote all three fields and the description's day-restriction
  claim.
- `delicious-poland-warsaw-food` (food-tours.json): claimed 4 hours, 350 zl, "six
  to eight tastings", meeting "Old Town, confirmed at booking". Operator page
  shows 2.5-3 hours, 385 zl, 10-12 samples across 4 eateries, meets at Nicolaus
  Copernicus Monument on Krakowskie Przedmiescie, 17:00 daily, group cap 12.
  Rewrote duration, price, route, meeting_point, and description.
- `delicious-poland-warsaw-vodka` (food-tours.json): claimed 3 hours, 320 zl,
  "three vodka bars", meeting "Old Town, confirmed at booking". Operator page
  shows 2.5 hours, 310 zl, 4 bars and pubs, 6 vodkas, meets at Teatr Kwadrat
  on Marszalkowska 138. Rewrote duration, price, route, meeting_point,
  description.

Chef-name structural checks all passed:
- Robert Trzopek (Bez Gwiazdek): Le Manoir + Noma + El Bulli prior career
  confirmed via warszawawarsaw.com interview + warsawinsider.pl.
- Marcin Przybysz (Epoka): Top Chef Poland 3rd-edition winner = 2014 confirmed
  (Polsat archive); Noma / Geranium / Atelier Amaro prior career confirmed via
  Akademia Inspiracji Makro biography.
- Albert Judycki + Jacek Malarski (Lukullus): Prix au Chef Patissier 2021
  confirmed via Akademia Gastronomiczna Polska press release.

Source-URL final-host check (San Diego precedent): spot-checked the operator
domains for all fine-dining and modern-Polish entries; none redirect to a
different registered domain. Bez Gwiazdek's Michelin Guide URL, Epoka's own
domain, Nolita's Michelin URL, Butchery & Wine's own domain all resolve to the
expected venue.

### B. Route / itinerary mismatches

None blocking. Three Eat Polska tours (food, vodka, market) and two Delicious
Poland tours (food, vodka) match operator-listed offerings by name and stop
shape. The two Delicious Poland tours had route-detail drift (covered under A2
above as numeric / meeting-point fixes); the routes themselves are real.

### C. Festival month corrections

- `warsaw-beer-festival`: claimed March 26-28 2026 at Legia Stadium. Confirmed
  via warsawbeerfestival.com banner "WFP21 MARCH 26-28 2026 WARSAW LEGIA
  STADIUM". No change.
- `restaurant-week-warsaw-spring`: spring edition exists; week.pl confirms two
  editions per year. Dates left as-is.
- `restaurant-week-warsaw-autumn`: claimed Oct 7 - Nov 19 2026. Operator page
  shows approximate Oct 7 - Nov 22 (the site says dates may change). Close
  enough on month and start day; left as-is per "match the month definitively,
  the days approximately".
- `wianki-nad-wisla`: claimed start/end day 21 (Sunday in 2026). Actual 2026
  date is Saturday June 20 (PIK Warsaw + rdc.pl + go2warsaw confirm). Festival
  is "Saturday before solstice" pattern, so the day shifts. Fixed start_day +
  end_day to 20 to match the 2026 occurrence.
- `fine-dining-week-warsaw`: claimed September, start_day 15 - end_day 28
  ("Two weeks"). Actual 2026 dates are July 1 - August 13 per InYourPocket
  Warsaw page (6 weeks, summer not autumn). Rewrote month, day_range, prose,
  start_month / end_month / start_day / end_day, and swapped the verified-block
  source/evidence URLs from the unreachable Facebook page to the InYourPocket
  Warsaw Fine Dining Week page that actually carries the 2026 schedule.

### D. Thin-category fabrications

`dietary.kosher`: empty array. Correct per memory note - Polish kosher near-
extinct after WW2; not a fabrication risk because the agent did NOT invent
entries to hit a floor. Leaving empty.

`dietary.halal`: 1 entry (Beirut Hummus & Music Bar). Cross-checked against
Zabihah Warsaw listing (in the verified block). Lebanese mezze with kofta /
shawarma, kitchen open to clarifying preparation. Real venue, real cuisine,
honestly framed as halal-friendly not strictly halal. Leaving.

`dietary.gluten_free`: 1 entry (Tel Aviv Urban Food). Plant-based Middle Eastern
with naturally-gluten-free hummus / shakshuka and on-request GF pita. Real venue,
real GF options. Leaving.

`dietary.vegetarian`: 2 entries (Beirut + Tel Aviv). Both real, both authentically
vegetarian-strong. Leaving.

`dietary.vegan`: 3 entries (Tel Aviv, Lokal Vegan Bistro, Krowarzywa). All three
are flagship Warsaw vegan venues, all match HappyCow listings. Leaving.

### E. Editorial-prose echoes (closed venues AND QA-removed facts)

E1 (closed-venue echoes): Atelier Amaro (closed during pandemic 2020-21,
ambiguous reopening as "Farm Dining" per Yelp / Instagram) is referenced in:
- `food-history.json` "Amaro era" key_era (historical framing, correct)
- `food-history.json` signature_innovations ("Atelier Amaro earned the country's
  first Michelin star in 2013" - historical statement, correct)
- `fine-dining.json` epoka description ("kitchens at Noma, Geranium and Atelier
  Amaro behind him" - past credential framing, correct)
- `city.json` food_culture_summary ("post-Amaro clock" / "Amaro put modern
  Polish cooking on the international map in 2008" - historical framing, correct)
All four references treat Amaro as a finished era / past credential, not as a
currently-open venue. No echo fix needed.

E2 (QA-removed-fact echoes after my own edits this round):
- `el-koktel` removed from `warsaw-weekend-classics` day 2: El Koktel is closed
  Sundays (Yelp + InYourPocket confirm Tue-Sat 18:00, Sun + Mon closed). Day 2
  of the weekend itinerary is Sunday. Rewrote the evening to drop the cocktail
  stop and go directly to Warszawa Wschodnia (24/7) for late dinner. Removed
  `el-koktel` from the day's `venues` array. El Koktel remains in bars.json and
  hidden-gems.json (both correctly note closed Sundays-by-implication via
  no Sun hours listed); no echo there.
- `tuk-tuk-hala-koszyki` BBQ-prawns rewrite: searched the data tree for "BBQ
  prawns" / "BBQ king prawns" / "Thai Wok" - no echoes in any other file.
- `eat-polska-morning-market` Saturday-only rewrite: searched for "Saturday
  mornings only" / "Saturday morning Hala Mirowska" - vegan three-days day 2
  references "Saturday morning Hala Mirowska market walk... with Eat Polska's
  morning-market tour", which is still accurate since Saturday is one of the
  three days the operator runs. No echo fix needed.
- Epoka price rewrite: no other file repeats the 440 zl figure.
- Fine Dining Week rewrite: searched for "September" near Fine-Dining-Week
  context - no other file echoes the wrong month.
- Wianki day rewrite (21 to 20): "Saturday before solstice" prose elsewhere is
  pattern-correct.

Itinerary day-of-week x venue-hours full cross-check (per A2):
- `warsaw-weekend-classics` day 1 (Saturday): Charlotte Plac Zbawiciela Sat
  9-23 OK; Bar Prasowy Sat 9-19 / 11-19 OK; Hala Koszyki Sat 8-01 OK; Bez
  Gwiazdek Sat 16-21 OK (Wed-Sat per Michelin + novacircle).
- `warsaw-weekend-classics` day 2 (Sunday): A. Blikle Nowy Swiat 9-21 daily
  OK; Zapiecek Swietojanska 11-23 daily OK; Pyzy Flaki Gorace 11-22 daily OK;
  Warszawa Wschodnia 24/7 OK. El Koktel removed (was the only Sun-closed
  venue).
- `warsaw-modern-polish-three-days` day 1: undated weekday - Relaks weekday
  OK, Stary Dom open daily OK, Alewino Mon-Sat OK (assumes not Sunday),
  Nolita Tue-Sat dinner OK, Charlotte evening daily OK. Plausible weekday
  reading.
- `warsaw-modern-polish-three-days` day 2: explicitly "Saturday morning"
  Hala Mirowska + Eat Polska market tour - Sat is one of Tue/Thu/Sat, OK.
  Tuk Tuk daily OK. STOR daily OK. Zoni undated but evidence_url suggests
  Tue-Sat dinner, plausible Sat reading. OK.
- `warsaw-modern-polish-three-days` day 3: STOR daily OK; Eat Polska vodka
  tour daily-bookable OK; Epoka Tue-Sat dinner per epoka.restaurant note,
  Sat would be tight after 4hr vodka tour; Cosmo Bar evening, not Sun-closed
  per InYourPocket. Plausible.
- `warsaw-vegan-three-days` all three days: venues either daily-open (Tel
  Aviv, Krowarzywa, MiTo, Etno, Beirut, STOR, Cuda na Kiju) or weekday-open
  (Lokal Vegan Bistro closed Mondays per its own JSON). No itinerary day
  is pinned to Monday, so Lokal Vegan Bistro days 1 + 3 are fine.

Geographic adjacency check (Vegas precedent): only "next door" claim in
itineraries is Zoni + Polish Vodka Museum at "Plac Konesera 1". Both occupy
the Koneser Praga Centre at Plac Konesera 1, confirmed via koneser.eu and the
vodka-museum site. Real adjacency, OK.

Slug-vs-prose location drift (SD precedent): spot-checked itinerary prose
neighborhoods against entity address fields. Praga / Powisle / Mokotow /
Old Town claims all match their entities' actual addresses.

### F. Editorial voice + length caps

Length caps are validator scope (32 entities over the 140-165 description cap).
Pre-existing, not in QA scope this pass. No egregious AI-tells observed. No
em-dashes or en-dashes anywhere in any edited file (`-` and `,` used).

## Defects total: 9 (3 entity-field rewrites, 5 numeric / detail corrections,
1 itinerary day-of-week fix dropping a Sun-closed venue from a Sun day)

## Below-floor topics after QA
- `wine-bars` at 4 (target >=10) - was already below floor pre-QA, no removals
  this pass. Needs research backfill.
- `itineraries` at 3 (target >=10) - was already below floor pre-QA, no removals
  this pass. Needs research backfill.
- `dietary.kosher` at 0 - intentional per memory note (Polish kosher near-extinct
  after WW2). Should be acknowledged on the dietary page rather than backfilled.

## Verdict
VERDICT: PASS
