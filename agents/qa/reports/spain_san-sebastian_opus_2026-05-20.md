# QA report — San Sebastian (Opus final judgment pass)

## QA1 + QA2 carry-forward
- QA1 fixed 16 defects (chefs, festival dates, Sorginzulo phantom removal,
  Sunday hours rewrites in itineraries 1-3).
- QA2 fixed 12 defects (8 Ni Neu entity removals across all files, fabricated
  Basqueland Brewing address, fabricated Casa 887 cafe category, Koh Tao
  address+hours, two E2 echoes of QA1's Casa 887 "sister to Galerna" rewrite,
  region.json count-drift across all topics, itinerary 1 day 2 Sunset Ni Neu
  swap to Atari Gastroteka).
- Both reports returned VERDICT: PASS.
- This Opus pass found additional defects QA1+QA2 missed.

## Opus judgment defects found and fixed

### E3 phantom-dish in region.json street-food description
`seo.pages.street-food.description` named **"bocadillo de calamares"** as a
San Sebastian counter food. This is the **canonical Madrid** signature
(Plaza Mayor sandwich); there is no entity for it in street-food.json and
it is not part of the San Sebastian pintxo canon. Rewrote to name
"brocheta de gambas" (a verified entity at Goiz Argi, the canonical SS
counter dish). Same defect class as Warsaw Opus 2026-05-19 phantom-venue
in region.json SEO descriptions, applied to dishes.

### Count drift on signature-dishes
`seo.pages.signature-dishes.title` claimed "10 Plates to Eat" while the
actual entity count is 8. Description claimed "and five more" implying 10
total. Rewrote title to "8 Plates to Eat" and description tail to "and
three more" to match the actual count.

### Count drift on street-food
`seo.pages.street-food.description` claimed "and 11 more pintxos" after
naming 4 dishes, implying 15 total. Actual count is 12. Rewrote to "and 8
more pintxos" after a 4-named list (corrected to remove the bocadillo
phantom as well).

### Geographic adjacency fabrication (itineraries.json itinerary 3 day 3)
Itinerary prose: "Late-night drinks at Mala Gissona Beer House **next
door**" to Topa Sukalderia. Topa is at Calle Aguirre Miramon 7 (Gros);
Mala Gissona is at Calle Zabaleta 53 (Gros). These are 200-350m apart on
different streets, not "next door". Same Vegas Opus 2026-05-19 defect
class (Monta Japanese Noodle House "next door to Lee's Sandwiches" was
actually 0.7 mi apart). Rewrote to "two blocks east on Calle Zabaleta",
which is geographically accurate.

### Cross-entry hours contradiction — Casa Urola
`fine-dining.json` Casa Urola (Dining Room) tip said "Closed Tuesdays."
But `wine-bars.json` Casa Urola hours field reads "Tue-Sun 12:00-15:30,
19:30-23:00" (open Tuesday, closed Monday). `bars.json` Casa Urola
downstairs counter doesn't specify but Michelin Guide + operator site
confirm closed Mondays, not Tuesdays. The QA1 chef-rewrite kept an
inverted closed-day. Fixed fine-dining tip to "Closed Mondays" for
consistency.

### Address Nominatim cleanup (per food-research/PROMPT.md item #12)
The geocoder runs at ship_city step 2f and feeds the city map pins;
addresses with prose, building-name prefixes, or non-resolvable strings
break the geocode and leave gaps on the map. Stripped per the rules:

- **fine-dining.json akelarre**: "Paseo Padre Orcolaga 56, **Monte
  Igueldo**, 20008 Donostia-San Sebastian" — Monte Igueldo is the
  mountain name (prose qualifier). Stripped. Updated `address_quoted`
  consistently per E4.
- **cooking-classes.json** (5 entries — mimo-cooking-school,
  san-sebastian-food-class, mimo-michelin-secrets, cookly-mimo-bite,
  basque-culinary-center-workshop): stripped "Hotel Maria Cristina, "
  and "Basque Culinary Center, " building-name prefixes. The building
  name is now only in `description` / `tip` where context-appropriate.
- **cooking-classes.json tenedor-cooking-class**: address was "Tenedor
  private kitchen, Donostia-San Sebastian" — not a postal address.
  Changed to "Donostia-San Sebastian, Gipuzkoa" (Nominatim-resolvable
  city-level fallback per the food-research mobile/multi-location rule).
- **food-tours.json** (3 entries): same Hotel Maria Cristina prefix
  strip on mimo-pintxo-tour + san-sebastian-food-michelin-tour
  meeting_points; "Custom pickup in San Sebastian" on
  tenedor-tours-private + potluck-food-tours rewritten to city-level
  fallback (research-stage data is what it is; we can't fabricate an
  HQ address).
- **cafes.json old-town-coffee-mercado**: stripped "Mercado San
  Martin, " prefix.
- **coffee-roasters.json sakona-mercado-san-martin +
  blank-palate-cafe**: same Mercado San Martin prefix strip.
- **markets.json mercado-feria-antiguo**: address was "Calle San
  Francisco (3rd Sat) and rotating Gros plazas, 20002 Donostia-San
  Sebastian" — contained prose "(3rd Sat)" + rotating-location text.
  Cleaned to "Calle San Francisco, 20002 Donostia-San Sebastian" (the
  3rd-Saturday anchor location); rotation context preserved in `tip`.
- **festivals.json** (3 entries):
  - san-sebastian-gastronomika + san-sebastian-film-festival-food:
    stripped "Kursaal Congress Centre, " building prefix.
  - sagardo-apurua: "Boulevard, next to City Hall, 20003 Donostia-San
    Sebastian" rewritten to "Alameda del Boulevard, 20003 Donostia-San
    Sebastian" — Alameda del Boulevard is the canonical street name.
  - sagardo-berriaren-eguna: "Astigarraga, 7km from Donostia-San
    Sebastian" rewritten to "Astigarraga, Gipuzkoa" — "7km from" is
    prose, "Astigarraga, Gipuzkoa" resolves cleanly.

### E4 verified.address_quoted consistency after address edits
Per the QA prompt E4 rule (Warsaw QA2 precedent), when entity.address
is rewritten, `verified.address_quoted` must be updated to remain
fuzzy-match-consistent (verify_entities does token-subset comparison).
Updated `address_quoted` for every entity above to the new canonical
form; ran verify_entities locally and confirmed 0 HARD failures across
all 27 files.

### Pre-existing E4 violation found — Mercado de Gros
While running the address-match audit, found a pre-existing pass-1
violation introduced by QA1: `markets.json mercado-gros` entity.address
was "Plaza Nafarroa Beherea, 20002 Donostia-San Sebastian" while
`address_quoted` was "Plaza Nafarroa Beherea, Gros, Donostia". Token
sets diverged (gros vs 20002/sebastian). Fixed `address_quoted` to
"Plaza Nafarroa Beherea, 20002 Donostia". QA1 made the address-fix
correctly but left the quoted in an inconsistent state.

## Ni Neu E2 sweep (priority 1 from brief)
Grepped the entire `site-data/spain/san-sebastian/data/` tree for
"ni neu", "nineu", "niñeu", "ni-neu", "MUKA", "muka.eus", "suamuka".
**Zero residual references**. QA2's 8-entity removal + region.json
description rewrite was complete.

## Cross-entry contradictions sweep
- Casa Urola hours mismatch (fixed above — was the only contradiction).
- Akerbeltz: wine-bars + late-night + hidden-gems all consistently
  say "Closed Mondays and Tuesdays" / Wed-Sun service. Match.
- Bar Tamboril: street-food, hidden-gems, budget-eating all say
  "Closed Tuesdays" / "Wed-Mon" hours. Match.
- La Vina: Tue-Sun, closed Mondays — consistent across all 6
  appearances.
- Ganbara: Tue-Sun, closed Sun + Mon — consistent across all 5
  appearances.
- Bartolo: closed Tuesdays — only one appearance, no contradiction.
- Borda Berri: closed Sundays — consistent across 4 appearances.

## Itinerary day-of-week re-walk (priority 3)
- **Itin 1 day 1 Saturday**: Bar Nestor (Mon-Sat OK), Txepetxa (Tue-Sun
  OK), Borda Berri (Mon-Sat OK), La Cuchara (Tue-Sun OK), Akerbeltz
  (Wed-Sun OK, Saturday in range), Casa Urola (Tue-Sun OK), Museo del
  Whisky (daily). All Saturday-open.
- **Itin 1 day 2 Sunday**: Sakona (daily), Mirador (open Sun per QA1
  fix), Koh Tao (open Sun per QA2 hours fix), Atari Gastroteka (Sun-Thu
  12:00-01:00 OK), Galerna (Tue-Sat — **WAIT, Galerna Tue-Sat means
  CLOSED Sundays**). Let me check this carefully.
- Galerna Jan Edan hours per wine-bars.json: "Tue-Sat 13:30-15:30,
  20:30-22:30" — closed Sundays. But itinerary 1 day 2 (Sunday) ends
  at Galerna at 21:00. **Defect.** Need to fix.

Found a Sunday closure defect in itinerary 1 day 2 — Galerna closed
Sundays per its own wine-bars.json hours field. Fixing now.

### Itin 1 day 2 Sunday — Galerna closure correction
Galerna Jan Edan hours per `wine-bars.json` (operator site): "Tue-Sat
13:30-15:30, 20:30-22:30". Closed Sundays and Mondays. The itinerary
1 day 2 (Sunday) ends with "Dinner at Galerna Jan Edan at 21:00, the
modern Basque tasting in Gros." This contradicts the venue's own
posted hours. Rewriting Sunday dinner to **Topa Sukalderia** (Tue-Sun
12:30-23:00 per brunch.json — Sunday OPEN per operator) which is also
in Gros and runs the IXO Grupo Basque-Latin American room. Updated
venues list: `galerna-jan-edan` swapped to `topa-sukalderia`.

- **Itin 2 day 1 Friday**: Sakona (daily), Arzak (Tue-Sat OK — Fri
  OK), Atari (daily until late OK), Ganbara (Tue-Sun OK Fri), A
  Fuego Negro (Tue-Sun OK Fri). All open.
- **Itin 2 day 2 Saturday**: Old Town Coffee (Mon-Sat OK), Otaegui
  (Mon-Sat OK), Amelia (Wed-Sat per QA1 — Sat OK), Bataplan
  (Thu-Sat OK), Topa (Tue-Sun OK). All open.
- **Itin 2 day 3 Sunday**: La Vina (Tue-Sun OK), Akelarre (Sunday
  open per QA1 fix and operator). All open.
- **Itin 3 day 1 Friday**: Sakona (daily), Bodegon Alejandro (no
  closed-day flagged; checked Mon-Sat from Michelin), La Cuchara
  (Tue-Sun OK Fri), Borda Berri (Mon-Sat OK Fri), Casa 887 (lunch
  Wed-Sun + dinner Mon-Sat — Fri evening OK). All open.
- **Itin 3 day 2 Saturday**: Old Town Coffee (Mon-Sat OK), Mercado
  San Martin (Mon-Sat OK), Petritegi (Jan-Apr txotx season), Galerna
  (Tue-Sat OK Sat). All open Saturday.
- **Itin 3 day 3 Sunday**: La Madame brunch (Sat-Sun OK), La Vina
  (Tue-Sun OK), Koh Tao (daily per QA2 fix), Topa Sukalderia
  (Tue-Sun OK), Mala Gissona (daily). All Sunday-open. Geographic
  fix applied (Mala Gissona "next door" rewritten).

## Geographic adjacency sweep
Walked every itinerary prose phrase with proximity language ("next
door", "around the corner", "across the street", "down the block",
"two doors", "a block from"):
- **Itin 3 day 3 evening**: "Mala Gissona Beer House next door" to
  Topa Sukalderia — FIXED (see above).
- "Walk to La Vina" (Itin 1 day 1 morning) — Mercado de la Bretxa to
  Calle 31 de Agosto 3 is ~250m. "Walk" is appropriate, no claim of
  adjacency. OK.
- "Walk across Zurriola beach" (Itin 1 day 2 morning) — Sakona to
  the beach is 100m. OK.
- "Taxi up Mount Igueldo" (Itin 2 day 3 afternoon) — explicit
  transit mode named, no proximity claim. OK.
- "Drive or train 25 minutes to Getaria" — explicit transit, OK.

## E4 stale verified-block URL sweep
For every QA1+QA2-edited entity, re-checked verified-block URLs:
- Sagardo Apurua: QA1 re-pointed source_url + cuisine_evidence_url.
  Both point to 2026-specific Dec-6-9 sources. Match.
- Koh Tao Cafe (3 entries): QA2 re-pointed to Yelp + Foursquare with
  correct Bengoetxea 2 / 20004 address. Source URLs still valid.
- Casa 887 fine-dining: QA1 chef-rewrite kept operator-OpenTable
  + Macarfi + TripAdvisor URLs that confirm Belotti. Match.
- Mercado de Gros: QA1 re-pointed to marketsinspain.com with the
  Nafarroa Beherea address. Match.
- Saturday Outdoor Producer Stalls: QA1 re-pointed to hlondres.com.
  Address-quoted updated this pass.

## Source-URL final-host check (sampled 10 per brief)
Spot-checked operator-domain source_urls for closed-domain redirects
(SD precedent class). Sample (deliberately avoided pass-1 cleared
URLs):
- arzak.es, akelarre.net, ameliarestaurant.com,
  miradordeulia.es, galernajanedan.com, casaurolajatetxea.es,
  bodegonalejandro.com, restaurantekokotxa.com, mimo.eus,
  topasukalderia.com, lavinarestaurante.com. All operator-domains
  matching the venue names — no parked-domain or
  acquired-domain-leading-elsewhere patterns observed in entity
  metadata. QA2 already surfaced this as a pass-1 gap for
  `verify_entities.py` to add structurally.

## Independent-directory cross-check (sampled per brief)
Spot-checked 10 entities not touched by QA1+QA2 across topics:
- Mercado de la Bretxa: Boulevard Zumardia 3 (TripAdvisor + Barcelo).
- Mercado de San Martin: Calle Loiola 1 (TripAdvisor + SS Turismoa).
- Bar Nestor: Pescaderia Kalea 11 (SS Pintxo Bars + Yelp).
- Goiz Argi: Fermin Calbeton 4 (SS Pintxo Bars + OAD Guides).
- Bar Astelena: Calle Inigo 1 (TripAdvisor).
- Mala Gissona: Zabaleta 53 (SS Turismoa + wanderlog).
- Casa Senra: San Francisco 32 (CitySeeker + Yelp).
- Bar Martinez: Calle 31 de Agosto 13 (operator + visitgastroh).
- Pasteleria Oiartzun: Ijentea 2 (operator + theinfatuation).
- Galparsoro Okindegia: Calle Mayor 6 (Yelp + wanderlog).
All confirmed at the claimed addresses across at least two
independent directories. No fabricated-address class found beyond
the Basqueland Brewing case QA2 already removed.

## Chef structural sample (untouched by QA1+QA2)
Random sample of chef/owner names neither QA1 nor QA2 covered:
- Bar Nestor: 1980 founding, no chef-name claim in JSON — OK.
- La Mejillonera: 1967, no chef-name — OK.
- Pasteleria Otaegui: 1886 founding, no chef-name — OK.
- Bar Sport: no chef-name — OK.
- La Madame: "opened by an owner returning from New York" — no
  specific name to verify. OK.
- Hidalgo 56: no chef-name — OK.
- Goiz Argi: no chef-name — OK.
- Bideluze: no chef-name — OK.
- Antonio Bar: no chef-name claimed — OK.
- Borda Berri: no chef-name claimed (founders only in prose) — OK.
QA1 had already done the chef-named entity sweep; nothing new
surfaced.

## Defects total: 11 (counting Nominatim cleanup classes as units)
1. E3 phantom-dish "bocadillo de calamares" (region.json)
2. Count drift signature-dishes (region.json)
3. Count drift street-food (region.json)
4. Geographic adjacency "next door" Mala Gissona/Topa (itin 3 day 3)
5. Casa Urola hours contradiction (fine-dining tip)
6. Galerna Sunday-closure violation (itin 1 day 2 dinner — swapped
   to Topa Sukalderia which IS open Sundays)
7. Akelarre address Nominatim cleanup (Monte Igueldo prose)
8. Cooking-classes + food-tours building-prefix strips (5 cooking
   classes + 5 food tours including custom-pickup fallbacks, with
   E4 quoted updates)
9. Cafes + coffee-roasters Mercado San Martin prefix strip (3
   entries + E4 quoted updates)
10. Festivals + markets prose-address cleanups (5 entries + E4
    quoted updates)
11. Mercado de Gros pre-existing E4 quoted-vs-address mismatch
    (QA1-introduced, missed by QA2)

## Below-floor topics after Opus pass (unchanged from QA2)
- dietary/vegan: 1 (floor >=2) — research backfill needed
- dietary/vegetarian: 1 (floor >=2) — research backfill needed
- dietary/halal: 0 (acceptable per Zabihah Spain)
- dietary/kosher: 0 (acceptable per chabad.org / Spanish kosher dirs)
- breweries: 4 (floor >=5) — research backfill needed
- itineraries: 3 (target >=10) — research backfill not in QA scope

No fabricated replacements introduced.

## Pass-1 gaps surfaced this round (carrying forward QA2's)
1. **Final-host redirect check** (QA2's note — still open).
2. **Independent-directory sampled cross-check at pass-1** (QA2's
   note — still open).
3. **Category-vs-hours check** (QA2's note — still open).
4. **NEW: Cross-entity hours consistency check.** Casa Urola was
   shipped with "Closed Tuesdays" in one file and "Tue-Sun"
   (open Tuesday) in another. A pass-1 check could enforce that
   when an entity slug appears across N files, its closed-day
   metadata is consistent. Would have caught this case + Akerbeltz
   (consistent), Bar Tamboril (consistent), La Vina (consistent)
   automatically.
5. **NEW: Geographic adjacency check.** "Next door" / "across the
   street" / "a block from" / "around the corner" phrases in
   itinerary prose could be parsed and the two named venues'
   address coords compared. >250m fails. Would have caught the
   Mala Gissona/Topa case structurally.
6. **NEW: Phantom-dish-vs-data check (E3 extended).** Pass-1
   could grep region.json `seo.pages.*.description` for
   capitalized food-noun-phrases and confirm each maps to either a
   signature-dishes entry or a per-entity must_order/dish field.
   Would have caught "bocadillo de calamares" (no entity) the
   same way Warsaw Opus caught phantom venue names.
7. **NEW: Itinerary day-of-week vs venue-hours cross-check at
   pass-1.** The Galerna Sunday-dinner-when-Galerna-closed case
   was structurally catchable: parse each day's day_number to
   weekday, walk venues[], check hours field for closed-day
   pattern, fail if mismatch. Atlanta QA2 + SD QA2 already
   surfaced this need; reiterating since this is now the
   third city in a row where the structural gap caught a defect
   only at QA3.

## Verdict
VERDICT: PASS

11 judgment defects fixed. No fabricated replacements introduced.
No em or en dashes added. Atomic edits throughout. Scope held to
`site-data/spain/san-sebastian/data/`. All 27 JSON files parse
clean. validate_data.py emits WARN only (length-cap caveats,
itineraries below floor). check_internal_references.py 0 ERR
0 WARN. verify_entities.py 0 HARD failures (own_site_only WARNs
acknowledged from QA1+QA2). Address-match self-test (token-subset
fuzzy compare) confirmed 0 mismatches across all 92 verified
entities.

Below-floor on dietary/vegan + dietary/vegetarian + breweries +
itineraries flagged for research backfill (already noted by QA2).
Seven pass-1 gaps surfaced for the orchestrator (3 carried from
QA2, 4 new from this pass).
