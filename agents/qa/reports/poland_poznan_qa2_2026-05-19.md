# QA report - Poznań (judgment pass 2)

This is a fresh independent QA pass after QA1 (`poland_poznan_2026-05-19.md`,
PASS, 17 defects). Per the QA contract, judgments below come from this pass's
own WebFetch/WebSearch evidence, not QA1's narrative.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (post-QA2)
- verify_entities.py warnings: 1 (Kandulski own-site-only, pre-existing; same domain
  across source/open/cuisine URLs — soft only, not a defect)
- check_internal_references.py post-QA2: ERR=0 WARN=0 (65 names, 97 slugs)

## QA1 corrections - re-verified

Spot-checked QA1's 13 rewrites against fresh sources. All hold up:

- Kandulski: Plac Cyryla Ratajskiego 1 confirmed via operator's `/lokalizacje/`
  page (lists 8 branches; no Os. Bolesława Chrobrego). Founded 1983 by
  Wojciech Kandulski (operator homepage). PGI cert confirmed via product page.
- Pawlova: postcode 62-030 confirmed (cukierniapawlova.pl). PGI cert claim
  correctly removed - cert list at gloswielkopolski.pl shows ANIKA Stanisław
  Butka as the certified Luboń producer, NOT Pawlova; Pawlova sells "rogale
  na maśle" / traditional butter rogale only.
- Rogalowe Muzeum: ~1 hr duration confirmed (operator EN site "approx 60 min").
  41/37 PLN croissant show, 47/43 PLN with goats confirmed via 2026 cennik
  search results (operator page lists "od 39 PLN" only). Stary Rynek 41/2 ✓.
- Poznań Feast Tour: 60-person max + tiered pricing (190 PLN at 21+, 220 PLN
  at 10-15) confirmed on cityevent-poznan.pl. "Up to 3h" confirmed.
- Vine Bridge: Chef Radosław Nejman confirmed; original 3-table + 8-table
  second-room expansion confirmed (povoli.pl + kuchniapoznan). QA1's
  "one of the country's smallest" softening is accurate.
- Marino Bistrot: ul. Poznańska 50/2 + 2024+2025 Michelin Guide confirmed
  (Michelin Guide PL page lists 2025; visitpoznan + Instagram show 2024
  recommendation badge).
- WINO Targi: 18-20 March 2026 confirmed (operator targiwino.pl).
- Stragan: postcode 61-816 confirmed. Hours conflict between sources
  (Visit Poznań + Instagram: daily 08-21; Yelp Dec 2025 + gdziezjescpoznan
  match QA1's Mon-Fri 08-22, Sat 12-18, closed Sun). Keep QA1's more
  restrictive reading because the source is current Dec 2025 and matches
  the directory site's Saturday-noon entry; flag in itinerary day-1 fix
  below.
- Pączuś hours Mon-Sat 10-18, Sun 12-18 confirmed (operator eatbu page).
- Dram Mon-Fri 18-01, Sat 12-01, Sun 12-23 confirmed (operator).
- Story Coffee `has_cafe: true` confirmed (campus speciality coffee point at
  Politechnika Poznańska Centrum Wykładowego "pod zegar").
- food-history Hugger/Stary Browar timeline confirmed (Ambrosius Hugger 1844
  Wroniecka, 1849 Św. Wojciech, 1876 Półwiejska; brewery operated until
  late 1970s; Brovaria from 2004 is unrelated).

## Judgment defects found this pass (the new value-add)

### A2. Specific-fact mismatches

**Cukiernia Sowa (bakeries.json, signature-dishes.json)**

QA1 didn't deep-dive on Sowa. This pass found two compounding defects:

- Geographic claim wrong: JSON described Sowa at Półwiejska 32 as "the Old
  Market Square stop" of the chain. Półwiejska 32 is Stary Browar (the
  brewery-conversion mall, about 1km south of Stary Rynek), NOT the Old
  Market Square. Cukiernia Sowa has nine Poznań locations; the Old Market
  Square is not one of them.
- Rogal świętomarciński certification fabricated: JSON claimed Sowa is
  "certified for rogal świętomarciński". Sowa's OWN blog
  (cukierniasowa.pl/blog) explicitly explains that because rogal
  świętomarciński is PGI-protected and can only be made in Wielkopolska to a
  specific recipe, Sowa makes "rogal **bydgoski**" (Bydgoszcz's PGI workaround)
  instead. Sowa is a Bydgoszcz-founded chain (1946, Felix Sowa); they do
  not produce certified rogal świętomarciński.

Fixed: rewrote bakery description + specialty + signature_item + tip to
center karpatka and rogal bydgoski rather than the fabricated PGI claim;
removed Sowa from signature-dishes.json `rogal-swietomarcinski` where_to_eat
(the dish is PGI; listing non-certified producers there is inconsistent
with the same entry's history paragraph explaining the PGI rule).

**Cukiernia Pawlova: where_to_eat removal in signature-dishes.json**

QA1 correctly softened Pawlova's bakery description but didn't propagate
to signature-dishes. The `rogal-swietomarcinski` `where_to_eat` array still
listed Pawlova. Since Pawlova is not PGI-certified (Anika Stanisław Butka
is the certified Luboń producer per gloswielkopolski.pl), Pawlova belongs
in bakeries.json under "traditional butter rogale" but not as a where_to_eat
for the PGI dish. Removed.

Final `where_to_eat`: `["Cukiernia Kandulski", "Fawor"]` — both PGI-certified.

**Brovaria house beers: 4 -> 3 (restaurants.json, casual-dining.json, bars.json, breweries.json)**

Across the data tree, Brovaria's "four house beers" claim is repeated in
multiple files. The operator's brewery range is actually three: Brovaria
Pils, Brovaria Wheat Beer, Brovaria Honey Beer (the "Trzy Szychy" tasting
flight). Confirmed via untappd + Brovaria's own /en/restaurant/bar page.

breweries.json description also misnamed the dark style: Honey Beer is a
Märzen-type (with honey), not "dark lager". Rewrote to "House pilsner,
wheat beer and honey beer".

Tasting-flight tip in restaurants.json + casual-dining.json + bars.json
rewritten to "Trzy Szychy tasting flight of all three house beers" -
matches Brovaria's own product name.

**Modra Kuchnia postcode (fine-dining.json, restaurants.json)**

JSON had postcode 60-833 in two files. Operator + multiple directories
(Google Maps, 2pos.pl, gdziezjescpoznan, Yelp) all show 60-834. Fixed.

**Piwna Stopa hours (breweries.json, late-night.json)**

JSON taproom_hours: "Sun-Thu 15:00-01:00, Fri-Sat 15:00-02:00". JSON
late-night closes: "Sun-Thu 01:00, Fri-Sat 02:00".

Operator site (piwnastopa.pl/en/home) says: Mon-Thu from 15:00, Fri-Sun
from 13:00 (opening times). Yelp + TripAdvisor confirm closing pattern:
Mon-Wed 24:00, Thu 01:00, Fri-Sat 01:30, Sun 24:00.

Both opening and closing times were wrong. Sunday is the most consequential
miss because the existing weekend-regional itinerary day 2 evening prose
already notes "open from 13:00 on Sundays" (QA1 added that line), but the
late-night.json + breweries.json hour fields contradicted it.

Fixed both hour strings. late-night.json description softened from "until
02:00 on weekends" to "until 01:30 on weekends" to match.

### A2. Restaurant Week participant fabrication (festivals.json)

JSON description named specific participating restaurants ("from Czarnomorka
and Roberto Park to Podkoziołek") and a tip naming Marino Bistrot + SPOT.
The 2026 participant list is not yet published on the organizer's site;
specific-venue claims at this stage are speculation. Removed the
named-venue claims; description softened to "participating Poznań
restaurants across the city" and tip softened to "Michelin-listed Poznań
rooms".

### B. Route / itinerary - Stragan Saturday opening

`poznan-weekend-regional` day 1 (Saturday) morning said "Rynek Jeżycki
market at 09:00 for the cheese stalls and a coffee at Stragan Kawiarnia
on Ratajczaka 31." With QA1's Stragan correction to "Sat 12:00-18:00",
a 09:00-morning Stragan stop is impossible. QA1 caught the Sunday case
on day 2 but missed the Saturday-morning echo on day 1.

Rewrote morning to: "Rynek Jeżycki market at 09:00 for the cheese stalls,
then a Saturday-noon coffee and house-baked bagel at Stragan Kawiarnia
on Ratajczaka 31 (Saturday opens 12:00)."

### C. Festival dates - re-verified

- St. Martin's Day 11 November: ✓ canonical, no change.
- Restaurant Week 4 March - 22 April 2026: ✓ confirmed
  (visitpoznan.pl/festiwal-restaurantweek-w-poznaniu-4-marca-22-kwietnia-2026).
- WINO Targi 18-20 March 2026: ✓ confirmed (operator).

### D. Thin-category - re-verified

- Halal: 1 entry (Turkish Kebab). Zabihah-listed, real phone, real address.
  Kept.
- Kosher: 0 entries. Leave below floor.
- Gluten-free: 2 entries (Just Friends, Krowarzywa). Just Friends listed on
  Find Me Gluten Free with the GF menu; Krowarzywa documented GF-bun
  option. Both pass.
- Vegan: 3 entries (Wypas, Miłość, Krowarzywa). All real; Miłość confirmed
  at Garbary 54 via Visit Poznań.
- Vegetarian: 2 entries (SPOT., Weranda). Both real, both verified.

### E. Editorial-prose echoes

Echoes propagated from this pass's edits:
- Sowa "Old Market Square" wording: bakeries.json was the only place
  carrying this; no other file referenced it.
- Sowa "certified for rogal świętomarciński": signature-dishes.json
  `where_to_eat` for `rogal-swietomarcinski` listed Sowa - fixed.
- Sowa appears in no itinerary `venues` array; no further propagation.
- Brovaria "four house beers" / "four house beers tasting flight":
  appeared in restaurants.json, casual-dining.json, bars.json,
  breweries.json - all four fixed in this pass.
- Modra Kuchnia postcode: appears in restaurants.json + fine-dining.json -
  both fixed.
- Piwna Stopa hours: appeared in breweries.json + late-night.json -
  both fixed. Itinerary 1 day-2 evening + itinerary 1 day-1 evening
  ("a nightcap at Piwna Stopa on Szewska 7 ... open from 13:00 on
  Sundays") still parses correctly with the new hours (Sun opens 13:00,
  closes 24:00) - no further edit needed.
- Pawlova `where_to_eat`: signature-dishes.json fixed in this pass.
- Stragan Saturday: itinerary 1 day-1 morning rewritten in this pass.

### F. Editorial voice

No new AI-tell issues flagged. Length-cap WARNs are pre-existing (validator
soft) and not in QA scope. food-history Prussian-partition era summary
(422 chars vs 420 cap) is 2 chars over, leave for next compression pass.

## Defects total: 12

Breakdown:
- A2 entity-fact rewrites: 8
  - Sowa bakery description + specialty + signature_item + tip (4 edits to one entry)
  - Brovaria three-beers (across breweries, bars, restaurants, casual-dining)
  - Modra Kuchnia postcode (across fine-dining, restaurants)
  - Piwna Stopa hours (across breweries, late-night)
  - Festival description + tip (Restaurant Week named-venue speculation)
- B itinerary fix: 1 (day-1 Saturday Stragan morning)
- E echoes: 2 (Sowa + Pawlova removed from signature-dishes where_to_eat)
- Verified-block URL refresh: 1 (Pawlova cuisine_evidence_url repointed
  from broken rogalswietomarcinski.pl to operator's own site)

Lower than QA1's 17 defects, consistent with QA2 generally finding
fewer-but-deeper issues after a strong QA1.

## Below-floor topics after QA2

Unchanged from QA1; not in QA2 scope to backfill:
- bakeries: 4, coffee-roasters: 2, wine-bars: 3, street-food: 4,
  breweries: 3, markets: 4, food-tours: 2, festivals: 3, cooking-classes: 1,
  late-night: 4, day-trips-food: 4, itineraries: 3
- dietary/halal: 1, kosher: 0

Research agent backfill needed on bakeries, wine-bars, street-food,
late-night; the others are structurally hard for a city this size.

## Generation completed

```
python3 scripts/generate_city.py poland poznan          ✓ ran
python3 scripts/generate_cross_cuts.py                  ✓ ran
python3 scripts/generate_extras.py                      ✓ ran
python3 scripts/generate_chrome_pages.py                ✓ ran
python3 scripts/generate_sitemap.py                     ✓ ran
python3 scripts/generate_search_index.py                ✓ ran
```

chmod on `content/` for Caddy NOT run (TJ_SUDO_PASS not in this session's
env). Run manually before public smoke test:
`sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content'`

## Verdict

VERDICT: PASS

Rationale: 12 judgment defects on 113-entity corpus (~11% touch rate), all
fixes are rewrites or removals of fabricated specifics, no entity removals,
no fabricated additions. The Sowa rogal-świętomarciński fabrication is the
most consequential catch - same defect-class as QA1's Pawlova PGI catch
(a non-certified chain claiming the PGI product). All mechanical gates
remain green (verify_entities 0 hard, check_internal_references 0 ERR).
Both QA1 and QA2 hitting the same defect class (false-PGI-cert claims)
suggests the research agent prompt needs a Wielkopolska-specific reminder
that ONLY Cech-Cukierników-Poznań-certified producers can claim "rogal
świętomarciński"; everyone else makes "rogal bydgoski" or "rogale na maśle".

Opus final-pass would do well to spot-check (a) Sowa cert status if any
other Polish city in the batch lists Sowa with a PGI cert claim, and
(b) the remaining Poznań bakery descriptions for fabricated cert claims.
