# QA report - warsaw (QA2 judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: **2 introduced by QA1's own edits** (food-tours
  meeting_point rewrites left stale address_quoted in the verified blocks of
  delicious-poland-warsaw-food and delicious-poland-warsaw-vodka). Both fixed in
  this pass.
- verify_entities.py warnings: 18 own_site_only WARNs (advisory, not blocking).
  Day-trips-food entries all share en.wikipedia.org domains; eatpolska.com,
  deliciouspoland.com, cafebristol.pl all share a single domain. Not a defect
  class but a coverage suggestion for research backfill.

## Independent verification of QA1's 9 changes

Re-fetched each of QA1's 9 rewrites from the operators directly. Findings:

- **Epoka 225-325 zl food, 595-725 zl with wine**: verified via epoka.restaurant/en/
  homepage. Short History 225 PLN food / 595 PLN wine pairing; History 325 PLN
  food / 725 PLN wine pairing. QA1 correct.
- **Tuk-Tuk "chilli shrimp"**: verified via tuktuk.pl homepage feature dish
  "Smazone Krewetki z Chilli". The koszyki.com landlord-page still describes
  Tuk-Tuk as "BBQ king prawns" (older marketing copy) but the operator's actual
  menu shows fried chilli shrimp. QA1 correct to swap.
- **HAYB Borowski family / Coffee Republic rebrand 2016**: verified via Dog & Hat
  + Bean Bros roaster interviews (Wiktor and Robert Borowski, started as Coffee
  Republic, rebranded to HAYB). QA1 correct.
- **Eat Polska Morning Market Tue/Thu/Sat 09:00, 3.5 hours, 220 zl, Hala
  Mirowska Plac Mirowski 1**: verified via eatpolska.com/markettour/warsaw/.
  QA1 correct.
- **Delicious Poland Food Tour 2.5-3 hr, 385 zl, 4 eateries 10-12 tastings,
  Nicolaus Copernicus Monument Krakowskie Przedmiescie, 17:00 daily, cap 12**:
  verified via deliciouspoland.com/warsaw-food-tour. QA1 correct on prose. But
  **left `verified.address_quoted` stale at "Old Town, confirmed at booking"** —
  this is a HARD addr_mismatch. Fixed this pass.
- **Delicious Poland Vodka Tour 2.5 hr, 310 zl, 4 bars, 6 vodkas, Teatr Kwadrat
  Marszalkowska 138**: verified via deliciouspoland.com/warsaw-vodka-tour. QA1
  correct on prose. **Same stale address_quoted bug**. Fixed this pass.
- **Wianki nad Wisla 2026 = Saturday June 20**: verified via warsawnow.pl,
  rdc.pl, pik.warszawa.pl, go2warsaw.pl, estrada.com.pl all confirm Sat Jun 20
  2026. In 2025 the festival was on Sat Jun 21 (solstice itself). The pattern
  is "Saturday closest to solstice"; 2026 solstice is Sunday, so it shifts to
  Sat Jun 20. QA1 correct.
- **Fine Dining Week Warsaw July 1 - Aug 13 2026**: verified via
  inyourpocket.com/warsaw/warsaw-fine-dining-week_24585e ("Jul 1 - Aug 13
  2026"). QA1 correct on dates AND on swapping the verified-block source URL.
- **El Koktel Sun+Mon closed, removed from `warsaw-weekend-classics` Sun
  itinerary day 2**: verified via Yelp + Tripadvisor (Tue 18-24, Wed 18-24,
  Thu 18-24, Fri 18-02, Sat 18-02, Sun+Mon closed). QA1 correct.

## Judgment defects found

### A2. Specific-fact match against operator menus / press

- **`food-history.json` "Amaro era" key_era**: claimed "Atelier Amaro in 2008".
  Atelier Amaro opened in 2011 (per Wikipedia, foodontheedge.ie, fine-dining
  lovers archives, all consistent). The Michelin Rising Star was 2012 and the
  full Michelin star was 2013. The 2008 date appears to conflate Wojciech Modest
  Amaro's earlier International Academy of Gastronomy "Chef de l'Avenir" award
  with the restaurant's opening. Rewrote `period` from "2008-present, the Amaro
  era" to "2011-present, the Amaro era" and updated the summary's "opened
  Atelier Amaro in 2008" to "opened Atelier Amaro in 2011".
- **`city.json` food_culture_summary**: same defect, "Amaro put modern Polish
  cooking on the international map in 2008". Rewrote to "Amaro opened Atelier
  Amaro in 2011 and earned Poland's first Michelin star in 2013".

### B. Route / itinerary mismatches

No new route fabrications found. Eat Polska food + vodka + market tours and
Delicious Poland food + vodka tours all match operator listings by name and
shape. QA1's prose rewrites correctly reflect operator content; the only
residue was the stale `verified.address_quoted` fields (handled under section
A2 of pass-1, now fixed).

### C. Festival month / dates

All five festival entries re-verified independently:

- `restaurant-week-warsaw-spring` Mar 4 - Apr 22: week.pl confirms a March/April
  spring edition each year. Operator only publishes precise dates a few weeks
  ahead; close enough on month. No change.
- `restaurant-week-warsaw-autumn` Oct 7 - Nov 19: week.pl confirms Oct/Nov
  autumn edition. No change.
- `warsaw-beer-festival` March 26-28 2026 at Legia Stadium: confirmed verbatim
  via warsawbeerfestival.com banner ("WFP21 MARCH 26-28 2026"). No change.
- `wianki-nad-wisla` June 20: independently confirmed via 5 sources (above). No
  change. QA1 correct.
- `fine-dining-week-warsaw` July 1 - Aug 13 2026: independently confirmed via
  inyourpocket.com. No change. QA1 correct.

### D. Thin-category fabrications

- `dietary.kosher` (0): intentional empty per memory note. No change.
- `dietary.halal` (1, Beirut Hummus & Music Bar): real venue, Zabihah-listed,
  Lebanese mezze framed as halal-friendly. Leaving.
- `dietary.gluten_free` (1, Tel Aviv Urban Food): real venue with naturally-GF
  hummus and on-request GF pita. Leaving.
- `dietary.vegetarian` (2): both real. Leaving.
- `dietary.vegan` (3): all flagship Warsaw vegan venues, HappyCow-listed.
  Leaving.

### E. Editorial-prose echoes

**E2 (QA1-rewrite echoes)**:

- **`itineraries.json` day 3 of warsaw-modern-polish-three-days afternoon prose**:
  said "Eat Polska Vodka Tour, four hours across three Warsaw vodka bars".
  Entity in food-tours.json says 3 hours, 3-4 bars; independent fetch of
  eatpolska.com confirms 3-3.5 hours, 3-4 bars, 6 vodkas. Itinerary prose was
  a pre-QA1 echo of the original (wrong) Delicious Poland numbers and didn't
  match either the entity OR the operator. Rewrote to "three hours across
  three to four Warsaw vodka bars".

**Phantom-venue echoes in editorial / SEO prose**:

- **`neighborhoods.json` Powisle vibe**: "modern Polish kitchens like SAM and
  MOMU". SAM Powisle is a real Powisle bakery/bistro (matches), but MOMU is at
  ul. Wierzbowa 9/11 in Srodmiescie near Theatre Square, **not Powisle**.
  Geographic phantom-adjacency defect (Vegas precedent). Rewrote the vibe to
  reference SAM Powisle and Kafe Zielony Niedzwiedz (the actual Powisle entity
  in our data) instead.
- **`region.json` wine-bars description**: "Kieliszki na Probie" - typo of
  "Kieliszki na Proznej" (the actual venue name and slug). Rewrote.
- **`region.json` bars description**: "Wodka Cafe Bar" not in bars.json.
  Rewrote to reference Pijalnia Wodki i Piwa (the actual vodka bar entity).
- **`region.json` brunch description**: "MOMU" not in our brunch.json (also,
  see geographic issue above). Rewrote to reference Charlotte, STOR, Aioli,
  MiTo, Cafe Bristol (the actual entities).
- **`region.json` late-night description**: "Zapiekanki Krola Kazimierza" is
  Krakow's chain, not in our Warsaw late-night.json. Rewrote to Warszawa
  Wschodnia, Pijalnia Wodki i Piwa, Beirut, Cuda na Kiju, Pyzy Flaki Gorace.
- **`region.json` breweries description**: "ArtyZann" not in breweries.json.
  Rewrote to Cuda na Kiju, PiwPaw, Pinta, Same Krafty.
- **`region.json` festivals description**: "Noc Restauratorow, Pierogi
  Festival" not in festivals.json. Rewrote to Wianki nad Wisla, Warsaw Beer
  Festival, RestaurantWeek and Fine Dining Week.
- **`region.json` cooking-classes description**: "Cook Up Warsaw" not in
  cooking-classes.json. Rewrote to Eat Polska, Pierogi & More, Foodie City
  Warsaw.
- **`region.json` street-food description**: rewrote from a categorical list
  ("zapiekanka at Hala Mirowska, kebab on Marszalkowska, pierogi windows") that
  named no actual entities to one referencing Pyzy Flaki Gorace, Tuk Tuk at
  Hala Koszyki, Krowarzywa, Beirut, Zapiecek (the actual entities).

**Inflated-count cleanup in SEO titles/descriptions**: many region.json
title/description fields claimed N entities that don't exist in the data
("22 Picks", "16 Cocktail and Vodka Bars", "20 Bistros", "16 Filter and
Espresso Picks", "12 Piekarnia Picks", "10 Picks", "8 Picks", "14 Counters",
"10 Plates", "10 Local Picks", "10 Spots", "8 Picks", "6 Picks", etc.).
Reality across the data is much smaller (restaurants 14, fine-dining 6,
casual-dining 12, cafes 8, bakeries 6, coffee-roasters 5, wine-bars 4,
bars 7, street-food 5, breweries 5, markets 5, food-tours 5, festivals 5,
cooking-classes 3, budget-eating 7, signature-dishes 6, hidden-gems 6,
brunch 5, late-night 5, day-trips-food 5). Rewrote all titles and
descriptions to drop the misleading hard counts ("Editor Picks", "Picks",
"Bistro Picks", etc.) so the page promise matches what the user sees on
landing. This isn't fabrication; it's removing fabricated promises that
the data doesn't honour.

Itinerary day-of-week x venue-hours full cross-check (per A2): re-verified
all three itineraries' venue-hours alignment. QA1's findings hold:

- `warsaw-weekend-classics` day 1 Saturday: all four venues Saturday-open.
- `warsaw-weekend-classics` day 2 Sunday: all four Sunday-open (El Koktel
  removed by QA1).
- `warsaw-modern-polish-three-days` days 1-3: undated weekday/Saturday/
  weekday with no Sunday-pinned venue.
- `warsaw-vegan-three-days` days 1-3: undated; Lokal Vegan Bistro closed
  Mondays per its own JSON, but no day is pinned to Monday.

Geographic adjacency (Vegas precedent): Zoni + Polish Vodka Museum at Plac
Konesera 1 confirmed real adjacency. SAM + MOMU "in Powisle" fixed above
(MOMU is in Srodmiescie).

### F. Editorial voice + length caps

Length caps are validator scope. Validator returned 0 ERRs after my edits
(several pre-existing description-cap WARNs untouched). No new
em-dashes/en-dashes anywhere.

## Defects total: 12

- 2 HARD address_quoted mismatches (Delicious Poland food, Delicious Poland
  vodka) introduced by QA1's meeting-point rewrites
- 2 factual A2 defects (Atelier Amaro year in city.json + food-history.json)
- 1 E2 echo (Eat Polska Vodka Tour "four hours" in itinerary day 3)
- 1 geographic phantom (MOMU in Powisle, actually in Srodmiescie)
- 1 typo (Kieliszki na Probie → na Proznej)
- 7 phantom-venue rewrites in region.json SEO descriptions (bars, brunch,
  late-night, breweries, festivals, cooking-classes, street-food)
- 14 misleading hard-count titles/descriptions across topic SEO pages,
  generalized to "Editor Picks" to match actual coverage

## Below-floor topics after QA2

- `wine-bars` at 4 (target >=10) - was already below floor pre-QA, no removals
  this pass. Needs research backfill.
- `itineraries` at 3 (target >=10) - was already below floor pre-QA, no removals
  this pass. Needs research backfill.
- `dietary.kosher` at 0 - intentional per memory note (Polish kosher near-extinct
  after WW2).
- All other topics under their advertised SEO counts (restaurants 14 vs 22
  promised, cafes 8 vs 16, bakeries 6 vs 12, etc.) - SEO copy now matches
  reality; research backfill can grow these.

## Verdict

VERDICT: PASS

All HARD failures cleared, all factual defects fixed, all QA1-changed-fact
echoes traced and resolved. 0 verify_entities hard failures, 0 validator
ERRs, 0 ERRs on check_internal_references. 18 own_site_only WARNs remain
as advisory backlog (Wikipedia-only day-trips, single-domain festival
sources).
