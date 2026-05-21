# QA report — San Sebastian (QA2 judgment pass)

## QA1 carry-forward
- QA1 fixed 16 defects (Casa 887 chef, Ni Neu chef rewrite, Sorginzulo
  removal, festival dates, Mercado Gros address, slug rename, several
  itinerary Sunday-hours fixes, region.json phantom-venue rewrites).
- QA1 left "VERDICT: PASS" but introduced two propagated defects (see E2)
  and missed a closed-venue class (Ni Neu) plus a fabricated-address
  brewery entity and a fabricated-category cafe entity.

## QA2 judgment defects found and fixed

### A. Closed-venue class — Ni Neu permanently closed 2022-02-06
The verified.source_url (restaurantenineu.com) HARD-redirects to
muka.eus, which then 301-redirects to suamuka.eus. Independent press
(directoalpaladar.com, donostitik.com, sivarious.com) confirms Aduriz
closed Ni Neu in Feb 2022 after 12 years and opened MUKA in the same
Kursaal space July 14 2022. The Kursaal's own ni-neu page now returns
404. QA1's "Raul Cabrera" chef fix was the right name for a venue that
no longer exists in this space.

Removed all 8 Ni Neu entities (no fabricated MUKA replacement per Lewis
no-fabrication rule; if MUKA is to ship it needs research-stage
provenance):
- restaurants.json: `ni-neu`
- fine-dining.json: `ni-neu-fine`
- casual-dining.json: `ni-neu-casual`
- dietary.json (vegetarian): `ni-neu-vegetarian`
- wine-bars.json: `ni-neu-wine`
- hidden-gems.json: `ni-neu-gem`
- cafes.json: `ni-neu-cafe`
- brunch.json: `ni-neu-brunch`

### A2. Source-URL final-host check — pass-1 gap (SD precedent)
ship_safety.sh / verify_entities.py HEAD-checked restaurantenineu.com
and saw HTTP 200 / 301 chains as "alive", missing that the final
landing host (muka.eus → suamuka.eus) is a different registered domain.
This is the SD `galaxy-taco-la-jolla-shores` precedent class
(verify_entities.py should follow redirects and flag final-host
mismatch as a structural fail). Flagging this for the orchestrator.

### A3. Fabricated brewery address — Basqueland Brewing
breweries.json entity `basqueland-brewing` claimed taproom address
"Paseo Miraconcha 6, 20007 Donostia-San Sebastian". Independent check
against breweryvisits.eu / restaurantguru / tripadvisor confirms
Basqueland Brewing's main brewery taproom is at "Akarregi Ind., 4B,
20120 Hernani" (~5km outside Donostia). Paseo Miraconcha 6 is a real
San Sebastian seafront address but Basqueland operates no taproom
there. Removed entity (the in-city Basqueland presence is the
Basqueland Izakaia at Zabaleta 53 which already has its own
`basqueland-izakaia-brewery` entity).

### A4. Fabricated category — Casa 887 daytime cafe
cafes.json `casa-887-cafe` claimed espresso service from 11:00 and
"quiet workspace feel". Operator hours per OpenTable + Michelin Guide
+ macarfi: dinner Mon-Sat 20:00-23:00, lunch Wed-Sun 13:00-16:00. No
daytime cafe service. Category fabrication. Removed.

### A5. Address + hours fix — Koh Tao Cafe
3 entries (cafes/koh-tao-cafe, coffee-roasters/koh-tao-cafe-roaster,
brunch/koh-tao-brunch) carried "Calle Bengoetxea 8, 20003 Donostia".
Verified against Yelp, Foursquare, multiple cafe directories: the
canonical address is "Calle Bengoetxea, 2, 20004 San Sebastian"
(postcode 20004 Centro, not 20003 Old Town; door number 2, not 8).
Hours in 2 of 3 entries said "Mon-Sat 08:00-19:00, closed Sundays";
the actual hours per Yelp + EncuentreAbierto include Sundays
(approximately Mon-Sun 09:00-22:00). Fixed address, postcode, hours
and source_url across all three entries. The itinerary 1 day 2 Sunday
coffee stop at Koh Tao Cafe is now hours-consistent.

### B. E2 echo — Casa 887 "sister kitchen to Galerna" claim persisted
QA1 reported the Casa 887 description was rewritten to drop the false
"Galerna sibling" credit, but the claim survived in TWO other places:
- `fine-dining.json` Casa 887 `tip`: "Less expensive than Galerna; the
  kitchen is the same partner team. Book through OpenTable." Rewrote
  to factual venue detail (stone-basement room, neon lighting, dinner
  Mon-Sat, lunch Wed-Sun, OpenTable booking).
- `hidden-gems.json` `casa-887-gem.why_hidden`: "Gros sister kitchen
  to Galerna with a 65-euro tasting...". Rewrote to "Gros stone-basement
  room of Brazilian chef Antonio Belotti with a 65-euro tasting that
  locals book midweek and tourists rarely find." Also fixed tip's
  "Closed Sundays" (incorrect — closed Mon-Tue lunch and Sun-Mon
  dinner pattern) to "Lunch Wed to Sun, dinner Mon to Sat."

### C. Itinerary day-of-week × venue-hours
Itinerary 1 day 2 (Sunday) had "Sunset drinks at Ni Neu in the Kursaal
over Zurriola at 19:00". Ni Neu is closed (see A). Rewrote to "Sunset
Txakoli at Atari Gastroteka on the Santa Maria church steps from 19:00"
(open Sun-Thu 12:00-01:00 per bars.json). Updated venues list:
`atari-gastroteka` replaces `ni-neu`. The remainder of the itinerary
(Sakona Sun-open, Mirador Sun-open per QA1 fix, Koh Tao now Sun-open
per A5, Galerna Sun-open) is hours-consistent.

QA1's other Sunday fixes (Itin 2 day 3 Akelarre instead of Amelia,
Itin 3 day 3 La Vina instead of Antonio Bar) confirmed by re-walk.

### E3. Phantom-venue prose sweep
- `region.json` `seo.pages.dietary.description`: "Kafe Botanika, Old
  Town Coffee, Ni Neu and rooms that take dietary needs seriously".
  Ni Neu was removed in A. Rewrote to "Kafe Botanika and Old Town
  Coffee anchor the dietary-friendly counters in the city." (165-char
  cap compliant).
- `region.json` `seo.pages.breweries.description`: "Mala Gissona,
  Basqueland and four more taprooms" — Basqueland-brewing removed in
  A3, total count was wrong even pre-A3 (was 5, claimed 6, now 4).
  Rewrote to "Mala Gissona, Basqueland Izakaia and two more taprooms
  with Basque small-batch beer and tasting flights" (165 cap compliant).
- Walked neighborhoods.json vibes, city.json food_culture_summary +
  must_try_dishes_summary, food-history.json eras and immigrant
  influences, seasonal-food.json, signature-dishes.json history and
  recipe notes, itineraries.json titles + prose + venues, per-entity
  description/tip/why_hidden across all 27 files. No remaining
  phantom-venue named that doesn't resolve to a verified entity in
  the same city.

### E4. Editorial count drift after removals
Removing 8 Ni Neu + 1 Basqueland-Brewing + 1 Casa-887-cafe + 1 dietary
echo dropped multiple per-topic counts. Updated region.json
seo.pages.*.title and .description to match new counts:
- restaurants: 22 → 21 Editor Picks ("and 17 more")
- fine-dining: 10 → 9 Picks ("and five more")
- casual-dining: 20 → 19 Picks (description didn't mention count by name)
- cafes: was missing count, now "and 9 more"
- wine-bars: 9 → 8 Picks ("and five more")
- breweries: 6 → 4 Picks (was already wrong pre-edit at 5)
- hidden-gems: 10 → 9 Local Picks ("and six more")
- brunch: 8 → 7 Spots ("and four more")

### Independent-directory address cross-check (sampled per prompt)
Checked addresses against external directories for entities NOT
touched by QA1:
- Sirimiri Gastroleku: Calle Mayor 4, 20003 (confirmed corner.inc +
  cityseeker + tripadvisor) — match
- Bar Astelena: Calle Inigo 1, 20003 (confirmed Yelp + foursquare) —
  match
- Casa Senra: San Francisco 32, 20002 (confirmed cityseeker + Yelp) —
  match
- La Madame: San Bartolome 35 (confirmed lamadamesansebastian.com +
  Yelp) — match. Brunch menu "gilda burger" claim verified
  (lamadamesansebastian.com/en/brunch/ lists Gilda burger as a savoury
  brunch item).
- Bideluze: Plaza Gipuzkoa 14, 20004 (confirmed eatingeurope) — match
- Sakona Coffee: Ramon Maria Lili 2, 20002 (sakonacoffee.com) — match
- Old Town Coffee: Reyes Catolicos 6, 20006 (oldtowncoffeeroasters.com)
  — match
- Mala Gissona: Zabaleta 53, 20002 (sansebastianturismoa.eus) — match
- Petritegi: Petritegi Bidea 8, 20115 Astigarraga (petritegi.com) —
  match
- Eme Be Garrote: Camino de Igara 33, 20018 Ibaeta (emeberestaurante)
  — match; chef Javi Izquierdo confirmed under Berasategui as
  per QA1 spot-check.
No fabricated addresses in the sampled set beyond the Basqueland
finding above.

### Chef/owner structural re-check (QA1-untouched)
- Casa Urola: Pablo Loureiro Rodil (confirmed via casaurolajatetxea +
  Michelin Guide) — match
- Bodegon Alejandro: Inaxio Valverde currently runs the kitchen
  (per restaurants.json description). Berasategui's "first Michelin
  star 1986" claim is well-attested historical fact. Match.
- Ganbara: Martinez-Ortuzar family since 1984 (consistent with
  ganbarajatetxea + sansebastianpintxobars) — match
- La Vina: Santiago Rivera 1990 invention of tarta de queso
  (lavinarestaurante.com self-attests) — match
- A Fuego Negro: Edorta Lamo (verified pintxos.es chef profile) —
  match
- La Cuchara de San Telmo: 1999 founding by Lasarte + El Bulli
  trained chefs (sansebastianpintxobars) — match
- Bar Nestor: 1980 founding, 4-things menu, tortilla x2/day ritual
  (Yelp + sansebastianpintxobars) — match

### Festival dates cross-source verification (Section C)
- Gastronomika: Oct 5-7 2026 confirmed via theupcoming.co.uk article
  dated 2026-04-29 (NOT the organizer homepage) — match
- Film Festival: Sep 18-26 2026 confirmed via sansebastianfestival.com
  registration page + tourism.euskadi.eus — match
- Tamborrada: Jan 20 fixed-date municipal festival — match
- Sagardo Apurua: QA1 fixed to Dec 6-9 (was Dec 26-29); confirmed
  cross-source via sagardotegiak.com event calendar — match (QA1 fix
  holds).
- Sagardo Berriaren Eguna: mid-Jan, citywide txotx opening per
  sansebastianturismoa.eus — match
- Semana Grande: Aug 8-15 around the city saint's week — match

### Astigarraga sagardotegi placement check
- Petritegi (Astigarraga, 7km out) appears in breweries.json AND
  day-trips-food.json — QA1's structural-multi-category note holds
  (sagardotegi tradition is inseparable from Donostia drinking
  culture; parallel to Galerna/Topa cross-listing pattern).
- Zelaia (Hernani, 8km out) appears only in breweries.json. Placement
  is consistent with QA1's reasoning.
- Petritegi Sagardotegi referenced in itinerary 3 day 2 Saturday as a
  day-trip from San Sebastian — correctly identified as a bus/taxi
  destination, not in-city.

## Defects total: 12

(8 Ni Neu removals counted as 1 closed-venue defect; A3/A4/A5/E3 dietary/
E3 breweries/E4 count drift/B fine-dining tip/B hidden-gems gem/C itin1
day2 = 11 unique judgment defects total. Counting individually: 12.)

## Below-floor topics after QA2
- dietary/vegan: 1 (unchanged from QA1) — below floor of >=2. Research
  backfill needed.
- dietary/vegetarian: 1 (was 2 before ni-neu-vegetarian removal). Below
  floor of >=2. Research backfill needed.
- dietary/gluten_free: 2 (unchanged) — at floor.
- dietary/halal: 0 (unchanged, acceptable per Zabihah Spain).
- dietary/kosher: 0 (unchanged, acceptable per chabad.org / Spanish
  kosher dirs).
- itineraries: 3 (unchanged from QA1) — below floor of >=10.
- breweries: 4 (was 5 pre-A3) — below floor of >=5. Research backfill
  needed; Basqueland-Brewing was a fabricated entity, not a real city
  brewery presence beyond the Izakaia.

No fabricated replacements introduced. Lewis no-fabrication rule held.

## Pass-1 gaps surfaced for orchestrator
1. **Final-host redirect check**: verify_entities.py should follow
   `source_url` redirects to terminal host and fail if the final
   registered domain differs from the source. Ni Neu (closed Feb 2022,
   restaurantenineu.com → muka.eus) would have been caught
   structurally; instead 8 stale entities reached QA1 + QA2.
2. **Independent-directory address cross-check should be sampled in
   pass-1**: Basqueland Brewing's "Paseo Miraconcha 6" passed
   verify_entities.py (HEAD-checked fine, address_quoted == address)
   but is fabricated; only Google Maps / brewery directories show the
   real Hernani location. Pass-1 currently can't catch this; QA2
   sampled-check did. Same defect class as Naples Opus 2026-05-19
   ilgaribaldino.it / archivio-storico.
3. **Category fabrication check**: Casa 887 cafes.json entity claimed
   day-cafe hours that contradicted operator's actual lunch/dinner-only
   schedule. Pass-1 doesn't compare claimed hours against operator's
   page hours; this is a research-stage discipline gap.

## Verdict
VERDICT: PASS

12 judgment defects fixed (closed-venue removal class, two fabricated
entities, address+hours correction across 3 entries, two E2 echoes of
QA1's "sister kitchen to Galerna" rewrite that QA1 missed, one
phantom-venue E3 echo from QA1's own rewrite, count-drift catch-up
across region.json titles+descriptions, Sunday itinerary swap). No
fabricated replacements introduced, no em/en dashes added, atomic
edits throughout, scope held to site-data/spain/san-sebastian/data/.
All 27 JSON files parse clean. validate_data.py [WARN] only (no ERR).
check_internal_references.py 0 ERR 0 WARN. Below-floor on
dietary/vegan + dietary/vegetarian + itineraries + breweries flagged
for research backfill.

Three pass-1 gaps surfaced to the orchestrator for verify_entities.py
hardening (final-host redirect, sampled directory cross-check,
category-claim vs operator-hours check).
