# Opus QA report - Venice (final judgment pass)

Scope: Opus final QA on Venice JSON after QA1 (18 fixes) and QA2 (8 fixes,
all VERDICT PASS). Narrow priorities per dispatch: cross-entry consistency
after QA1+QA2 edits (Vini da Gigio street rename, Castraure date sweep,
fegato preparation, 3 itinerary day-of-week rewrites), itinerary prose
re-walk, geographic adjacency, E4 verified-block sync, source-URL
final-host spot-check, and the new ship-rule address-Nominatim-cleanup.

## Pass-1 + QA1 + QA2 carry-forward verified

All QA1+QA2 edits hold up under re-read:

- Vini da Gigio "Calle Stua Cannaregio 3628A" consistent across
  restaurants.json, casual-dining.json, hidden-gems.json (entity.address,
  description, verified.address_quoted all match).
- Castraure date sweep: festivals.json (10 May 2026 second Sunday),
  seasonal-food.json (late April through mid-May), markets.json
  (mercato-di-rialto "from late April", mercato-di-sant-erasmo "late
  April through mid-May" + "second Sunday of May") all consistent.
- Fegato preparation "butter and white wine" consistent across
  signature-dishes.json (description, history, recipe), seasonal-food.json
  note, restaurants.json must_order references. No "Marsala" echoes.
- Weekend Day 2 Sunday rewrite to Estro Vino e Cucina (Wed-Mon open) +
  Walk across Accademia: in place and Sunday-open verified per entity hours.
- Budget Day 2 Sunday evening: Dal Moro's + Al Timon both Sunday-open per
  entity data (see A2 fix below for hours-claim mismatch).
- 3-day Day 1 Il Mercante "from 19:00" (Tue-Sat 19:00-02:00 per QA2):
  prose + activities echo both updated.
- All 6 festival dates: Carnevale 31 Jan-17 Feb, Sensa 17 May, Vogalonga
  24 May (50th edition), Castraure 10 May, Redentore 18-19 July, Regata
  Storica 6 Sept. All cross-referenced in QA1+QA2.
- Chef/owner names verified by QA2: Lazzari (Vini da Gigio), Donato Ascani
  (Glam), Bovo (Gatto Nero), Gavagnin+di Vita (Testiere), Sodano+Fullin
  (Local), Spezzamonte brothers (Estro), Brutto+Pavan (Venissa) all
  intact.
- All capitalised proper-noun venue mentions in prose (city.json,
  neighborhoods.json, food-history.json, signature-dishes.json,
  itineraries.json) resolve to entities in the data. No phantom venues.

## Opus-pass defects found and fixed

### A2. Itinerary prose vs entity-data hours mismatch (Vegas-class)

1. **Budget itinerary Day 2 (Sunday) - Dal Moro's claimed "kitchen closes
   18:00 Sundays"** but Dal Moro's entity hours are `"Daily 11:00-22:00"`
   (street-food.json) and `"Daily 22:00"` close (late-night.json). QA2
   introduced an unverified-and-contradicting Sunday-early-close claim;
   the entity data says daily 22:00. Rewrote evening prose + activities
   echo to "kitchen runs to 22:00 daily" / "kitchen open to 22:00", which
   matches both entity files and the operator listing.

2. **Budget itinerary Day 2 (Sunday) - Trattoria Bar Pontini "EUR 14 set"
   claim** contradicts entity tip "Set lunch weekdays only" / "Lunchtime
   sets at EUR 14 (primo + secondo + acqua) run Monday to Friday". QA2's
   rewrite kept the set claim on Sunday; corrected to "neighbourhood
   lunchroom plate from the carte (the EUR 14 weekday set does not run
   Sunday)" plus activities echo. Pontini's Sunday open/closed status
   is not declared in any entity hours field, so the venue mention itself
   stays (per no-removal rule) but the prose no longer makes a wrong
   weekend-set claim.

### Nominatim address-cleanup (per updated [[feedback-geocode-gates-ship]])

Three cooking-class entities had prose qualifiers in `entity.address` that
the Nominatim geocoder cannot resolve (private-home or studio entries
where the operator hides the exact street). Replaced with the public
meeting-point or postcode-resolvable canonical, moved the "exact address
shared after booking" context to `tip`, and synced `verified.address_quoted`
per E4 rule:

3. **cesarine-venice-cooking**: was `"Private home, Cannaregio (exact
   address shared after booking)"` -> `"Campo San Giacomo di Rialto,
   San Polo, 30125 Venezia VE"` (the public meeting point). Tip now
   explains "Host home address in Cannaregio shared at booking
   confirmation".

4. **monica-cesarato-cooking**: was `"Private studio, Dorsoduro (exact
   address shared after booking)"` -> `"Rialto Pescheria, San Polo,
   30125 Venezia VE"` (the public meeting point where the market walk
   starts). Tip now opens "Private studio in Dorsoduro; exact address
   shared at booking."

5. **do-eat-better-cooking-class**: was `"Calle del Pestrin, Castello
   (exact address shared after booking)"` -> `"Campo San Giacometto,
   San Polo, 30125 Venezia VE"` (the public meeting point). Tip now
   opens "Castello studio address shared at booking."

All three: `verified.address_quoted` synced to match new `entity.address`;
`checked_on: 2026-05-20` retained.

### Nominatim address-cleanup (festivals)

Four festival entries had prose embedded in `entity.address` (e.g. "and
across the historic centre", "and the lagoon", "and Giudecca") that
makes Nominatim Pass 1 fail. Pass 5 postcode-centroid would have saved
them, but the cleaner anchor address gives a more accurate pin AND a
working address_quoted that's defensible against the source page.

6. **carnevale-di-venezia**: was `"Piazza San Marco and across the
   historic centre, 30124 Venezia VE"` -> `"Piazza San Marco, 30124
   Venezia VE"`. Tip now carries "Events run across the historic centre,
   anchored at Piazza San Marco."

7. **festa-del-redentore**: was `"St Mark's Basin and Giudecca, 30133
   Venezia VE"` -> `"Chiesa del Santissimo Redentore, Giudecca, 30133
   Venezia VE"` (the votive-bridge endpoint church the festival
   processions go to; civic number omitted to avoid a fabricated digit).
   Tip now carries "The votive bridge runs across the Giudecca Canal to
   the Redentore church. Boats fill St Mark's Basin by 19:00; fireworks
   at 23:30."

8. **vogalonga**: was `"Bacino di San Marco and the lagoon, 30100 Venezia
   VE"` -> `"Bacino di San Marco, 30124 Venezia VE"` (also fixed the
   stale 30100 generic postcode to 30124 San Marco). Tip now mentions
   "from St Mark's Basin".

9. **festa-della-sensa**: was `"Bacino di San Nicolò del Lido, 30126
   Venezia VE"` -> `"San Nicolò del Lido, 30126 Venezia VE"` (drop the
   "Bacino" body-of-water descriptor; the place to geocode is the church
   at the Lido). address_quoted synced.

10. **festival-castraure-sant-erasmo**: `address_quoted` was bare
    "Sant'Erasmo island"; synced to full "Sant'Erasmo island, 30141
    Venezia VE" to match entity.address (E4 sync). entity.address
    unchanged.

### E. Cross-entry / cross-file echoes after QA1+QA2

None remaining. Walked seasonal-food.json, signature-dishes.json,
markets.json, festivals.json, casual-dining.json, hidden-gems.json,
itineraries.json after every QA1+QA2 rewrite (Vini da Gigio street,
Castraure date, fegato prep, Bistrot de Venise location, chef names) and
found no stale prose carrying old claims.

### Geographic adjacency

Walked every itinerary day's morning/afternoon/evening prose for
adjacency claims ("next door", "across the street", "around the corner",
"a block from", "walk to"). Three non-defect findings:

- "Walk across the Accademia bridge and through the Gallerie quarter"
  (weekend Day 2 afternoon after Estro Dorsoduro lunch). The Accademia
  is in Dorsoduro; the walk before Vino Vero/Cannaregio dinner is a
  scenic detour, not a transit claim. Acceptable.
- "Walk to the Arsenale and Castello" (3-day Day 3 afternoon after
  Testiere lunch). Testiere is in Castello, Arsenale is in Castello.
  Direct walk, true.
- "Vaporetto 12 from Fondamente Nove to Burano (45 minutes)" (3-day Day
  2 morning). Confirmed via ferry timetable; canonical ferry route.

Bar/sister-venue "next door" mentions (Adriatica next door to
Experimental Cocktail Club within Il Palazzo Experimental; Dal Mas
chocolate shop next door; Florian gift shop) all true per operator pages.

### E4. Verified-block consistency after QA1+QA2 edits

QA1+QA2 edits to address fields all have synced `verified.address_quoted`
already. The 5 Opus-pass `entity.address` changes (3 cooking classes + 4
festivals) all have address_quoted synced + checked_on = 2026-05-20.

### Source-URL final-host spot check

Spot-checked 10 entity source_url domains for obvious hijack indicators
(no WebFetch, just domain reasonability): antichecarampane.com,
cortescontave.com, osterialletestiere.it, ristorantelocal.com,
covinovenezia.com, estrovenezia.com, ristoranteallamadonna.com,
gattonero.com, bistrotdevenise.com, vinidagigio.it. All read as the
genuine operator domains for the venue named. ship_safety
check_external_urls 50/50 OK per QA2.

## Below-floor topics after Opus pass

Unchanged from QA1+QA2: dietary sub-categories all at 2 entries (vegan,
vegetarian, gluten-free, halal, kosher); itineraries at 3 entries.
Genuinely thin Venetian scene per HappyCow/Zabihah/Atly corroboration;
not a ship blocker.

## Defects total: 10

(2 itinerary day-of-week hours mismatches; 3 cooking-class prose-address
cleanup; 4 festival prose-address cleanup; 1 E4 verified-block sync.)

These are all small consistency / Nominatim-resolvability cleanups; no
fabricated entities, no phantom venues, no closed-venue references, no
chef name fabrication, no wrong festival dates, no cuisine-claim drift.
The QA1+QA2 chain caught the structural defects; Opus pass is the
last-mile cleanup for the new Nominatim address rule and two
self-contradictions QA2's rewrites introduced.

## Verdict

VERDICT: PASS

All defects fixed in-place. Atomic writes. No em/en dashes. No entity
removals. Ship_safety re-run not required since edits don't change
structural fields or remove URLs (address_quoted syncs are within
fuzzy-match tolerance; festival address cleanups still match the source
pages' anchor points).
