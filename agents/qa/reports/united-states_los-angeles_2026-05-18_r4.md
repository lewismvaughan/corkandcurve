# QA report - Los Angeles (round 4)

## Stage 1: 100% entity re-verification

- Total entities across topic JSONs (excluding neighborhoods/region/itinerary containers and chrome): ~160 venue-style records plus 6 festivals, 2 cooking classes, 3 food tours, 3 itineraries.
- WebSearch performed on: 100% of venue-style entities across restaurants, casual-dining, fine-dining, cafes, bars, brunch, hidden-gems, bakeries, breweries, wine-bars, late-night, street-food, markets, coffee-roasters, festivals, cooking-classes, food-tours, dietary, plus seasonal-food, signature-dishes, budget-eating, region SEO and itinerary venue mentions.
- Defects found: K = 13.

Round-3 address writes verified intact:
- broken-mouth (casual-dining): `718 South Los Angeles Street, ... 90014` confirmed by Yelp, brokenmouthcafe.com, eatbrokenmouth.com.
- blue-bottle-aresenal (cafes) + tonx-blue-bottle (coffee-roasters): `8301 Beverly Boulevard, West Hollywood, ... 90048` confirmed by bluebottlecoffee.com, Tripadvisor.
- darya-persian (dietary/halal): `12130 Santa Monica Boulevard, ... 90025` confirmed by Yelp, daryarestaurant.com.
- got-kosher (dietary/kosher): `8758 West Pico Boulevard, ... 90035` confirmed by Yelp, Grubhub, official Toast site.
- old-lightning (bars): `2905 Washington Boulevard, Marina del Rey, ... 90292` confirmed by LAmag, OpenTable.

All five round-3 address corrections held. **No regressions on the LA-signature address-hallucination class this round.**

### Defect list with sources

Hours-of-operation defects (late-night.json claims invalidated by current operator hours):

- `park-s-bbq-late` (late-night): JSON claims "Daily until 02:00"; parksbbq.com and Yelp/May-2026 list Mon-Sun 11:00-22:00. Park's BBQ is not a late-night room. REMOVED from late-night.
- `casa-vega-late` (late-night): JSON claims "Daily until 02:00"; casavega.com lists Mon-Fri 11:30-24:00, Sat-Sun 11:00-24:00. Closes midnight, not 02:00. REMOVED from late-night.
- `fred-62` (late-night): JSON claims "Open 24/7"; Yelp/May-2026 lists Mon-Thu 07:30-01:00, Fri-Sat 07:30-03:00, Sun 08:00-01:00. No longer 24-hour. REMOVED.
- `ruen-pair` (late-night): JSON claims "Daily until 04:00"; ruenpairthai.com lists Mon-Tue + Thu-Fri 16:00-22:45, Sat-Sun 14:00-22:45, Wed closed. Closes 22:45, not 04:00. REMOVED.

Wrong-month-and-date festival defect:

- `la-wine-and-food-fest` (festivals): JSON ran the 2025 edition as mid-June at Banc of California Stadium. Actual 2025 edition was November 7-9, 2025 at Barker Hangar Santa Monica per Fine Dining Lovers, Tastemade, thedesk.net, and lamag.com. Wrong month, wrong venue. FIXED to November 7-9 at Barker Hangar.

Closed-venue references in copy:

- Cole's French Dip (signature-dishes "french-dip-sandwich"): claimed "both still operating" in 2026; Cole's closed permanently August 3, 2025 after 117 years per NBC Los Angeles, Yahoo News, TheStreet. FIXED - description and history reflect Cole's closure.
- region.json budget-eating SEO description: listed "French dip at Cole's"; Cole's closed. FIXED to Philippe.
- region.json late-night SEO description: listed "Cole's French dip"; Cole's closed. FIXED to Original Tommy's + Leo's al pastor.
- region.json dietary SEO description: listed "halal Wahib's" but `wahibs-middle-east` was removed in round 3. FIXED to Shaherzad halal Persian.
- neighborhoods.json santa-monica vibe: cited Cassia as a current room; Cassia closed February 22, 2025 per smmirror.com. FIXED to Birdie G's, Melisse, Milo and Olive.
- seasonal-food.json summer figs: cited "Lucques and Felix"; Lucques closed in 2020 per LAmag. FIXED to Felix Trattoria and AOC.
- seasonal-food.json autumn Dungeness: cited "Providence and Connie & Ted's"; Connie & Ted's announced May 13, 2026 closure July 1, 2026 per The Pride LA. FIXED to Providence and Water Grill.

Description-vs-reality factual defects (address correct, description naming wrong neighborhood/feature):

- `sarita-s-pupuseria` (budget-eating): address says Grand Central Market; description said "Mercado La Paloma". FIXED to Grand Central Market.
- `noodle-st` (budget-eating): address 10936 Weyburn Ave Los Angeles 90024 is Westwood near UCLA per Daily Bruin and noodlestusa.com; description said "San Gabriel Valley". FIXED to Westwood.
- `lucky-boy` (budget-eating): description claimed "Open 24 hours"; luckyboyburgers.com and Yelp list 05:00-24:00. FIXED to "Open from 05:00".
- `stereoscope` in cafes + coffee-roasters: descriptions said "South Park"; 1501 W Sunset Blvd is Echo Park per Yelp, Tripadvisor, fivestars rewards page. FIXED.
- `coffee-for-sasquatch` (cafes): description said "on 3rd Street"; address 7020 Melrose Ave is on Melrose at La Brea per coffeeforsasquatch.com. FIXED.
- `tartine-manufactory` (bakeries): description said "on Sunset, West Hollywood"; 911 N Sycamore Ave is Hollywood/Media District per tartinebakery.com. FIXED.
- `clark-street` (bakeries): description said "on Beverly, West Hollywood"; 139 1/2 N Larchmont Blvd is Larchmont Village per clarkstreetbakery.com. FIXED.
- `psychic-wine` (wine-bars): description said "Eagle Rock"; 2825 Bellevue Ave is Silver Lake / Echo Park border per Sprudge Wine and the shop's own page. FIXED to Silver Lake.
- `erewhon-cafe` (dietary/gluten-free): description said "Mid-City"; 7660 Beverly Blvd is Fairfax District per Tripadvisor. FIXED.
- `kuya-lord` (hidden-gems): description said "Highland Park"; 5003 Melrose Ave is Melrose Hills (Larchmont Buzz). FIXED.
- `morihiro` (fine-dining): description said "Atwater Village, ... Michelin star since 2022"; Morihiro moved to Echo Park (1115 W Sunset Blvd, Ste 100) in October 2025 per LAmag and Whatnow LA. Address was already correct; description was stale. FIXED to Echo Park with the 2025 relocation context.

Counting by defect-class (per LA round-3 schema):
- Address hallucination: 0 (all round-3 fixes held).
- Wrong-neighborhood-in-description (no address impact): 9 (folded into 1 logical defect for round count since none affect the address field that Google indexes for local SEO).
- Hours invalidated, venue still open: 4 (Park's BBQ, Casa Vega, Fred 62, Ruen Pair - all removed from late-night).
- Closed-venue still referenced in copy: 7 (Cole's three times, Cassia, Lucques, Connie & Ted's, Wahib's; rolled up as one logical defect class - same root cause: prose did not re-check open status after round 3 closures).
- Wrong-month festival: 1 (LA Wine and Food Fest).
- Description vs address mismatch on neighborhood-only attribute (Sarita's, Noodle ST, Lucky Boy 24/7 claim): 3.

K rolled-up = 13 (5 hard ones - the late-night-hours-removed, the wrong-month festival, and one for the Cole's-class closed-venue prose; description-only neighborhood mismatches counted as one logical class of 9 instances at lower severity).

If counted as the strict per-record defect tally instead: 25 distinct JSON edits across 14 files.

## Stage 1 per-topic breakdown

- restaurants (18): 18 verified, 0 removed.
- casual-dining (15): 15 verified, 0 changes; broken-mouth address re-verified clean.
- fine-dining (9): 9 verified; morihiro description fixed (Echo Park relocation Oct 2025).
- cafes (14): 14 verified; stereoscope and coffee-for-sasquatch descriptions fixed; blue-bottle-aresenal address re-verified clean.
- bakeries (12): 12 verified; tartine-manufactory and clark-street descriptions fixed.
- coffee-roasters (4): 4 verified; stereoscope description fixed; tonx-blue-bottle address re-verified clean.
- street-food (8): 8 verified, 0 changes; Carnitas El Momo (2411 Fairmount), Mariscos Jalisco, Tacos y Birria La Unica, Tire Shop Taqueria all confirmed.
- food-halls: file does not exist (out of scope).
- markets (8): 8 verified, 0 changes; Smorgasburg LA 2025 schedule confirmed, 626 Night Market dates confirmed.
- bars (13): 13 verified, 0 changes; old-lightning address re-verified clean.
- wine-bars (8): 8 verified; psychic-wine description fixed (Silver Lake, not Eagle Rock).
- breweries (5): 5 verified, 0 changes.
- speakeasies: file does not exist (out of scope).
- hidden-gems (8): 8 verified; kuya-lord description fixed (Melrose Hills, not Highland Park); Kuya Lord at 5003 Melrose re-verified clean.
- brunch (9): 9 verified, 0 changes; Botanica, Salazar, Great White, Bavel all open.
- late-night (8 -> 4): 4 removed for invalidated hours. **Below floor of 5.**
- festivals (6): 6 verified; LA Wine and Food Fest fixed from June to November.
- cooking-classes (2): 2 verified, schedules current.
- food-tours (3 with operator schemas): 3 verified, routes still match operator pages.
- neighborhoods (15): santa-monica vibe fixed (Cassia removed); thai-town vibe fixed (Ruen Pair past midnight removed).
- itineraries (3): 3 verified; westside-chef-day round-3 fixes (Milo and Olive, Gjusta) held; no new defects.
- dietary (13 across vegan / vegetarian / gluten_free / halal / kosher): 13 verified; darya-persian and got-kosher addresses re-verified clean; erewhon description fixed (Fairfax, not Mid-City).
- food-history: prose checked; Cole's reference left as historical (1908 invention) since the "still operating" claim is in signature-dishes which has been fixed.
- signature-dishes (~10 dishes): French dip dish description + history fixed for Cole's closure.
- seasonal-food: figs and Dungeness crab notes fixed to drop Lucques + Connie & Ted's.
- budget-eating (10): 10 verified; sarita-s-pupuseria, noodle-st, lucky-boy descriptions fixed.
- region.json SEO descriptions: three SEO description strings fixed (budget-eating, late-night, dietary).
- day-trips-food (8): 8 verified, 0 changes (Santa Barbara, Santa Ynez, Ojai, Palm Springs, San Diego, Los Olivos, San Gabriel Valley, Temecula - day-trip descriptions, not entity-existence claims).

## Stage 2: round-4 convergence call

- This is round 4. Defect count K = 13 rolled-up (25 distinct JSON edits across 14 files).
- Round counts so far: r1=35, r2=10, r3=10, r4=13.
- The number went up, not down, because round 4 audited categories that prior rounds had skipped or under-checked: festival dates against current schedules, hours-of-operation claims against operator pages, closed-venue references in editorial prose (region SEO, neighborhood vibes, seasonal-food notes, signature-dishes history), and description-vs-address neighborhood mismatches. The defects newly surfaced are real prior misses, not regressions.
- **Critically: the LA-signature address-hallucination class held at 0 this round.** All five round-3 address writes are intact.
- The newly-surfaced defect classes (hours invalidated by current operator pages, closed-venue prose echoes, wrong festival month, neighborhood-in-description mismatch) are now also part of the audit checklist.
- Recommendation: round 5 needed. Round 5 should specifically:
  - Re-check the late-night topic backfill once research adds entries to bring count back to floor.
  - Run a fifth address sweep on all venues (defense-in-depth - this class only stayed at 0 because round 3 hit them hard; assume regression risk).
  - Verify hours-of-operation claims on the remaining late-night, brunch, festivals topics against operator current pages.
  - Sweep editorial prose for closed-venue echoes (signature-dishes, food-history, seasonal-food, neighborhoods.vibe, region.seo.pages).
  - Re-verify all venues round 4 left untouched (the majority): every restaurants / casual-dining / fine-dining entry got a name + address search but several got only one round of confirmation; defects compound and a sixth sanity check on Bestia, Republique, Mother Wolf, etc, costs little.

## Stage 3: cross-city correctness

- `check_external_urls.py --country united-states --city los-angeles`: 4 broken / 130, all anti-bot codes (521 The Prince, 403 Vespertine Tock, 403 Hayato Tock, 401 Unsplash hero image). Pass.
- `audit_live.py`: 1288 pages crawled, 0 errors, 0 broken extras LA-scoped. Pass. 105 warnings remain (94 meta-description length, 11 title length - validator territory).
- Smoke test: `https://tablejourney.com/united-states/los-angeles/late-night/` returns 200; the now-shorter (4-entity) page renders.
- Breadcrumb / state-page / country-hub spot-checks: content tree intact (`content/united-states/los-angeles/` contains all topic dirs plus index.html, 175 entity pages, 20 topics covered, 4 stale pages pruned by city generator).

## Defects removed or rewritten

| Slug | Topic | Reason |
|---|---|---|
| park-s-bbq-late | late-night | REMOVED. Hours 11:00-22:00, not until 02:00. Not a late-night venue. |
| casa-vega-late | late-night | REMOVED. Closes 24:00, not 02:00. Borderline; per "when in doubt, remove." |
| fred-62 | late-night | REMOVED. No longer 24/7; closes 01:00-03:00 depending on day. |
| ruen-pair | late-night | REMOVED. Closes 22:45, not 04:00. |
| la-wine-and-food-fest | festivals | FIXED. June -> November (Nov 7-9 2025), venue corrected to Barker Hangar. |
| french-dip-sandwich | signature-dishes | FIXED. Cole's closure August 2025 reflected. |
| region budget-eating SEO | region | FIXED. Cole's -> Philippe. |
| region late-night SEO | region | FIXED. Cole's -> Tommy's + Leo's. |
| region dietary SEO | region | FIXED. Wahib's -> Shaherzad. |
| santa-monica vibe | neighborhoods | FIXED. Cassia (closed) -> Birdie G's, Melisse, Milo and Olive. |
| thai-town vibe | neighborhoods | FIXED. Removed "Ruen Pair past midnight" (closes 22:45). |
| seasonal-food summer figs | seasonal-food | FIXED. Lucques (closed 2020) -> Felix + AOC. |
| seasonal-food autumn crab | seasonal-food | FIXED. Connie & Ted's (closing July 2026) -> Water Grill. |
| sarita-s-pupuseria | budget-eating | FIXED. Mercado La Paloma -> Grand Central Market. |
| noodle-st | budget-eating | FIXED. San Gabriel Valley -> Westwood near UCLA. |
| lucky-boy | budget-eating | FIXED. Open 24h -> Open from 05:00. |
| stereoscope (cafes + coffee-roasters) | cafes, coffee-roasters | FIXED. South Park -> Echo Park. |
| coffee-for-sasquatch | cafes | FIXED. 3rd Street -> Melrose. |
| tartine-manufactory | bakeries | FIXED. Sunset West Hollywood -> Sycamore Avenue Hollywood. |
| clark-street | bakeries | FIXED. Beverly West Hollywood -> Larchmont Village. |
| psychic-wine | wine-bars | FIXED. Eagle Rock -> Silver Lake (border of Echo Park). |
| erewhon-cafe | dietary/gluten_free | FIXED. Mid-City -> Fairfax District. |
| kuya-lord | hidden-gems | FIXED. Highland Park -> Melrose Hills. |
| morihiro | fine-dining | FIXED. Atwater Village description -> Echo Park (Oct 2025 relocation, Michelin star renewed for 2025). |

## Below-floor topics after QA

- **late-night: dropped 8 -> 4. Floor per `agents/food-research/PROMPT.md` is 5-15. NEEDS BACKFILL.**
  - Candidate replacements for research agent: Saigon Dish (24-hour pho), Tacos La Esquina, BCD Tofu House (24/7), Mama's Hot Tamales, Hae Jang Chon (Koreatown until 02:00), 101 Coffee Shop. All need their own existence + hours WebSearch round before being added.

Other 24 topics remain at or above floor (dietary/vegan, gluten_free, halal still each at 2 from round-3 removals; food-research has not backfilled those either).

## Verdict

K rolled-up = 13. The PASS threshold per the prompt is K < 5. Despite address-class holding clean, hours and closure prose surfaced 13 logical defects this round, including a wrong-month festival and four late-night entries with invalidated hours.

VERDICT: NEEDS_FIXES
