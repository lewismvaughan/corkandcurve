# QA report — Athens (judgment pass)

Date: 2026-05-20
Reviewer: QA1 (judgment pass-2)
Scope: site-data/greece/athens/data/*.json only

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (per ship_safety.sh which exited green pre-QA)
- verify_entities.py post-QA WARNs: a handful of own_site_only and stale-link warnings on day-trips-food entries and a few dead `open_evidence_url` / `cuisine_evidence_url` (Bairaktaris Fodors 404, Oikonomou GCT 404, Birdman OpenTable timeout). These were pre-existing and would have been caught by pass-1 too; they do not block ship.

## Judgment defects found

### A. Cuisine / category mismatches

- `kofio` (coffee-roasters): cuisine_evidence_url and own About page confirm Kofio is an online retailer/aggregator that sells third-party roasters' beans. It is NOT a coffee roaster. Category mismatch -> entity removed.
- `athens-coffee-roastery` (coffee-roasters): no real venue named "Athens Coffee Roastery" appears in any specialty coffee guide for Athens, Greece. Address is the deliberately vague "Stadiou, central Athens". Cuisine_evidence_url returns 403. Almost certainly fabricated to pad the topic. Removed.

After both removals, coffee-roasters drops to 3 entries (below 10 target floor) — noted below.

### A2. Specific-fact / chef / hours mismatches

- `spondi` (fine-dining): JSON claimed `stars: 2`. Current Michelin Guide and 2025/2026 industry sources (cycladicspaces, Greek Reporter, thisisathens.org) confirm Spondi currently holds **one** Michelin star (it was downgraded from 2 stars in the most recent guide revision; Spondi has held a star continuously since 2002). Corrected to `stars: 1` and rewrote prose to "a Michelin star" (singular).
- `city.json` `food_culture_summary`: said "Spondi has held Michelin stars since 2002" (plural) — corrected to "a Michelin star".
- `food-history.json` "new Athenian wave" era summary: same plural-stars echo — corrected.
- `kostas-souvlaki` (street-food) and `kostas-souvlaki-budget` (budget-eating): JSON hours field said "Mon-Sat 10:00 to 17:00, closed Sundays". Real hours per multiple sources are Mon-Fri only, closed BOTH Saturday and Sunday. Updated hours + tip text in both files. This drove an itinerary correction (see below).
- `pnyka-pangrati` (bakeries): claimed "Founder Dimitris Kotsaris still trains the bakers". The founder is no longer the operator; per CulinaryBackstreets and Greek City Times the bakery has passed from founder Dimitris to son Giorgos to grandson Dimitris Kotsaris. Rewrote to "The Kotsaris family now runs the third generation of the bakery" — true and non-personal.
- `klimataria-taverna` / `klimataria-casual` / `klimataria-late`: claimed live rebetiko is "Friday and Saturday only" and `closes: Friday-Saturday until 02:00`. Operator site says daily 12:00 to 02:00 and live music runs on most evenings from around 22:00. Updated descriptions + `closes` field + tip text in all three files.

### B. Route / itinerary mismatches

(no operator-route fabrications found; food-tours and cooking-classes entries match the operators' actual offerings)

### B'. Itinerary day-of-week × venue-hours cross-check

- `athens-weekend-classics` itinerary:
  - Day 1 titled "Saturday" sent lunch to Kostas Souvlaki at 13:30. Kostas is closed Saturday. Retitled Day 1 to "Friday".
  - Day 2 titled "Sunday" routed through Varvakios Central Market 10:30 and Krinos at 17:00. Varvakios is closed Sundays and Krinos is closed Sundays per their JSON hours fields. Retitled Day 2 to "Saturday" and rewrote prose so Krinos becomes a 17:00 loukoumades stop on Aiolou (not "Greek coffee in the historic centre"). Itinerary name + summary updated from "weekend" to "Friday-Saturday" to match.
- `athens-souvlaki-three-days` itinerary:
  - Day 3 titled "Wednesday" sent lunch to Taverna tou Oikonomou at 14:30. Oikonomou is closed weekday lunch (opens 19:00 Mon-Fri, opens 13:00 Sat-Sun). Rewrote Day 3: lunch moves to Diporto (lunch-only basement koutouki) and Oikonomou moves to a 20:30 evening dinner slot. Strange Brew brought forward to 18:30. Klimataria dropped from this day. Venues array updated.
- `athens-family-trip` itinerary:
  - Day 2 titled "Sunday" routed through Varvakios Central Market 13:30. Varvakios is closed Sundays. Replaced with Kolonaki cheese-counter lunch at Kostarelos (open Sundays 10:00 to 18:00 per JSON). Venues array updated.

### C. Festival month / date corrections

- `oenorama-athens`: verified March 13-16, 2026 via two independent 2026-specific sources (travel.gr and tornosnews.gr) per the C-section cross-source requirement. JSON is correct, no change.
- `athens-street-food-festival`: JSON had `start_day: 2, end_day: 18`. Operator's 2026 site confirms three weekends: May 8-10, 15-17, 22-24. Corrected to start_day 8, end_day 24.
- `athens-coffee-festival`: JSON had `start_day: 25, end_day: 27`. Operator confirms Sept 26-28, 2026. Corrected.
- `aegina-fistiki-festival`: JSON had Sept 17-27 (10 days). Festival is a long weekend in mid-September (2024 was Sept 12-15; 2026 sources say "early to mid September"). Conservatively rewrote day_range, description, and dates to "mid-September long weekend" with Sept 10-14 as the indicative window. Also corrected the echo in seasonal-food.json (was "late September").
- `tsiknopempti-athens`: Feb 12 2026 confirmed via two independent sources, JSON correct.
- `theofania-athens`: Jan 6 fixed annual date, no change.

### D. Thin-category fabrication sweep

- `coffee-roasters` started at 5, dropped to 3 after removing the two non-roaster / phantom entries (kofio, athens-coffee-roastery). Remaining: Taf Coffee, The Underdog, Mind the Cup — all independently verifiable real roasters.
- `breweries` shipped at 3 (Strange Brew, Noctua, Barley Cargo). All three verified real. No removals.
- `dietary.halal` is `[]` (0 entries) — confirmed correct per the watchout note that Zabihah-Athens-Greece returns no halal listings. Did NOT invent entries.
- `dietary.kosher` has 1 entry (Chabad of Athens). Verified via koshergreece.com listing. Accepted as below floor but real.

### E. Editorial-prose echoes and phantom-named venues

Major E3 sweep of `region.json` SEO page descriptions found a heavy cluster of phantom or miscounted venue names:

- `cafes` description: listed "Kaya" — no Kaya entity in cafes.json. Replaced with Mind the Cup. Also fixed "11 more" (only 9 cafes total).
- `restaurants` description: "Aleria, Cookoovaya, Mavro Provato, Karavitis and 18 more" — Aleria + Cookoovaya are in fine-dining.json not restaurants.json (so cross-topic phantom). Restaurants topic has 15 entries. Rewrote with in-topic venue names.
- `casual-dining` description: "17 more" was wrong (13 total). Trimmed to generic "and more".
- `bakeries` description: "Veneti and eight more" — typo for Venetis, and only 4 more (7 total). Rewrote with full real list.
- `breweries` description: "Strange Brew, Noctua, Barley Cargo, Beerz and two more" — "Beerz" is a phantom venue and there are only 3 breweries. Rewrote.
- `markets` description: "Kypseli" market is phantom (no Kypseli entity in markets.json; 5 markets total: Varvakios, Kallidromiou, Pantopoleion, Evripidou, Kostarelos). Rewrote with real list.
- `festivals` description: "Vinexpo, Detrop" are phantom festival names (no such Athens festivals in our data — Vinexpo Bordeaux and Detrop Thessaloniki are unrelated trade fairs). Rewrote with the six real festivals.
- `cooking-classes` description: "Plaka Culinary Backstreets" — phantom (Culinary Backstreets runs food-tours, not cooking classes). Rewrote.
- `brunch` description: "Holy Spirit, Yi" — both phantom venues (no matching entity in brunch.json). Rewrote with the real 6 entries.
- `wine-bars` / `street-food` / `late-night` / `hidden-gems` / `budget-eating` / `signature-dishes`: count phrases (e.g. "and X more") off by 1-3 for most. Rewrote to use real venue names or generic "and more".
- `signature-dishes` description: named "bougatsa" as one of "10 dishes" but there are only 8 dishes in signature-dishes.json and bougatsa is not one (the 8 are souvlaki, gyros, moussaka, pastitsio, spanakopita, loukoumades, tzatziki, horiatiki). Rewrote with the real list.
- All over-cap descriptions trimmed to fit the 140-165 SEO description window.

No closed-venue echoes found:
- Tailor Made is mentioned only as a historical-context reference in the `lazy-duck` description ("Ernst Ziller neoclassical building that used to house Tailor Made") — this is correct and not an active recommendation.
- Funky Gourmet, Vezené, Hervé, Cookoovaya: searched for; Funky Gourmet not referenced anywhere; Vezené not referenced (Birdman by chef Ari Vezene is a separate live venue confirmed open); Hervé not referenced; Cookoovaya confirmed open per operator site, chef Periklis Koskinas verified.

### E (additional). Fabricated padding entities removed

- `tailor-made-clumsies-coffee` (bars): listed as "The Clumsies Daytime" at Praxitelous 30 — same venue, same address as `the-clumsies` already in bars.json (which already notes "Specialty coffee runs from 10:00"). This was a duplicate entry padding the bars count, with the suggestive slug fishing for the closed Tailor Made name. Removed. Bars count drops from 12 to 11.

### Other defects fixed

- Mavro Provato `booking_url`: pointed at `https://www.tomavroprovato.gr/` which is a "Coming soon" placeholder page (VocaHost). Removed booking_url from both restaurants.json and casual-dining.json.
- Atlantikos `booking_url`: pointed at `https://ristorante-atlantikos.weeblyte.com/` — implausible domain (likely typo of weebly.com), 403 unverifiable, no other source says Atlantikos has online booking (typically phone reservations). Removed booking_url from restaurants.json, casual-dining.json and late-night.json.
- Pnyka `cuisine_evidence_url` had a stray `]/` token: `https://www.gourmed.com/]/pnyka-bakery-distinctions`. Replaced in bakeries.json and hidden-gems.json with a working `greekcitytimes.com/2021/10/17/bakeries-in-athens-2/` source.

### F. Editorial voice / length

- All over-cap (ERR-level) SEO descriptions trimmed to within the 140-165 character window. `validate_data.py` now reports `[WARN]` not `[FAIL]` for Athens.
- No em/en dashes anywhere.
- Voice is consistent across files; nothing egregious.

## Defects total

- ~30 distinct defects fixed across 13 JSON files. (Spondi-stars, two coffee-roasters fabrications, Tailor Made/Clumsies duplicate, two broken booking URLs, two Pnyka URL typos, Pnyka founder claim, Kostas hours, Klimataria days x3, 4 itinerary day-of-week / venue-hours mismatches, 4 festival date corrections, ~10 phantom-venue/count fixes in region.json SEO descriptions, 8 SEO description length ERRs.)

## Below-floor topics after QA

- `coffee-roasters`: 3 (target 10, floor unspecified in PROMPT but the validator's 10 is aspirational). The Athens specialty coffee scene is genuinely concentrated in Taf, The Underdog and Mind the Cup as roastery-and-cafe operators; padding requires either reclassifying cafes that don't actually roast in-house (Kaya, Kaffeine, Plegma — these are cafes not roasters) or going to the wholesale-only roasters that don't have a public cafe (Kudu, Samba, Oven). Research backfill needed if floor is hard.
- `breweries`: 3 (Strange Brew, Noctua, Barley Cargo). Athens craft beer scene is small; this is roughly the floor of what exists. Research backfill optional.
- `dietary.halal`: 0 (correct — Zabihah-Athens-Greece returns nothing; do NOT invent).
- `dietary.kosher`: 1 (Chabad of Athens — only kosher restaurant in the city per koshergreece.com).
- `itineraries`: 3 (validator suggests >=10 for SEO depth — this is a content-strategy choice, not a fabrication risk).

## Geographic note (not a defect, just flagged)

- Hytra (fine-dining) is at Petrou Kokkali 1 in Neos Kosmos, on the 6th-7th floor of the Onassis Cultural Centre. Currently labelled neighborhood `kerameikos-metaxourgeio` which is geographically inaccurate (Kerameikos is west of central, Neos Kosmos is south). The neighborhoods.json catalog has 10 slugs and none of them fit Neos Kosmos. Same applies to Delta Restaurant at 364 Syngrou Avenue, Kallithea (suburb south of City of Athens). Both venues are real and Michelin-starred so were not removed; the neighborhood slug is an imperfect fit only. Adding a `neos-kosmos` slug to neighborhoods.json is the cleaner fix but is out of QA scope.

## Verdict

VERDICT: PASS

Caveat: coffee-roasters now sits at 3 (well below the 10 SEO target). Research agent backfill recommended for the next session, but the city is shippable as-is — below-floor is acceptable per PROMPT.md ("don't invent"), and the 3 remaining entries are all the genuinely independently verifiable specialty-coffee roasters in Athens.
