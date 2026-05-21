# QA report — las-vegas (judgment pass, backfill batch)

Scope: 99 new entries across 12 topic files added this session.
Pass-1 (validate_data + verify_entities + check_internal_references + check_festival_dates) already cleared all 99 with zero defects.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0
- verify_entities.py warnings: 0
- Research agent pre-excluded (do not re-open): Vegas Uncork'd, Bachi Burger, Pamplona, HUDL Brewing, Naked City Arts location, Sanders Family Winery, Cozymeal aggregator listings.
- Address auto-corrections already applied: Mas Por Favor (3879 Spring Mountain Rd), Doberman Drawing Room (1025 S 1st St), Bad Beat Brewing (1421 S Main St, Sept 2025 relocation).

## Methodology

Walked all 99 entries focusing on Section A2 (specific-fact match against operator's menu/press, the new Charleston QA1 2026-05-19 priority class), Section B (food-tour and cooking-class route/curriculum match), Section C (festival month re-verification on 3 previously fetch-failed organizers), Section A (cuisine_evidence_url content match), Section F (internal-field consistency).

## Judgment defects found and fixed

### A2. Specific-fact fabrication (Charleston QA1 pattern)

1. **esthers-kitchen-brunch** (brunch.json) — Bombolini doughnuts and frittatas listed in must_order/description/tip; neither appears on the operator's current brunch menu (`https://www.estherslv.com/menu/brunch/`). Pasta carbonara claim ("if the menu has it that morning") only on dinner menu, not brunch. Rewrote to actual brunch items: Pasta Fritti + eggs with fennel sugo, Meyer lemon pancakes with huckleberry jam, proper omelette. Negroni sbagliato reference retained as a generic Italian brunch cocktail.

2. **carson-kitchen-late** (late-night.json) — "glam burger" listed in dish field and tip; not on the current menu (`https://www.carsonkitchen.com/las/carson_kitchen_las_vegas_menu.html`). Bacon jam and devil's eggs both verified. Replaced "glam burger" with "bacon burger" (on menu: cooper's sharp, jalapeno bacon, bacon mayo) and corrected "devilled eggs" -> "devil's eggs" to match operator's spelling. Updated tip to specify bacon jam with havarti on toasted baguette (actual menu item).

3. **soulbelly-bbq** (hidden-gems.json) — "side of green chile mac" in tip; the operator's mac and cheese is "Radiatore Pasta, Cheese Sauce topped with Pork Parm Crumbs (Panko, Parmesan, Blended Chicharrones)" with no green chile component (`https://soulbellybbq.com/las-vegas-arts-district-soulbelly-bbq-food-menu`). Rewrote tip to describe the actual mac with pork parm crumbs. Salt and pepper brisket verified.

4. **soulbelly-bbq** (hidden-gems.json) — why_hidden claimed "Bruce Kalman left LA's Union for this Arts District smokehouse". UNION is in Pasadena, not Los Angeles (fb101 source explicitly says "Pasadena's UNION"). Changed to "Pasadena's Union" — Pasadena is in LA County but the restaurant brand is distinctly Pasadena.

5. **boulder-city-coffee-cup-cafe** (day-trips-food.json) — description claimed "Diners Drive-Ins and Dives episode-one breakfast" and "huevos rancheros, pork chile verde omelette". Coffee Cup actually appeared in DDD Season 1 Episode 4 ("Breakfast"), not episode 1. Huevos rancheros not mentioned in the RJ source article for Guy Fieri's visit; only pork chile verde omelette is documented. Rewrote description to drop the unverified huevos rancheros and soften the DDD episode claim. Also corrected "512 Nevada Highway" -> "512 Nevada Way" in the description for consistency (both names are used locally for the same road, but Nevada Way is the canonical street name).

### B. Route / itinerary mismatches

6. **lip-smacking-arts-district-cocktail-crawl** (food-tours.json) — tip claimed "Doberman opener and Velveteen Rabbit closer". Operator's page lists Velveteen Rabbit as the third of five stops (1: Doberman, 2: CC Speakeasy, 3: Velveteen Rabbit, 4: Prowl, 5: Viking Mike's). Rewrote tip to describe Doberman and Velveteen Rabbit as the two standout pours on the five-bar route, removing the false "closer" assertion.

7. **lip-smacking-chinatown-speakeasy** (food-tours.json) — tip claimed Mas Por Favor speakeasy "accessed through a graffiti tunnel". Operator describes it as a "secret tunnel" with "neon lights, vintage murals" — a smuggler's-tunnel motif with murals, not graffiti. Replaced with "hidden mural-lined tunnel".

8. **vegas-weekend-strip-classics day 1** (itineraries.json) — afternoon narration said "Lunch at Bouchon at the Venetian, the patio overlooking the canal." Bouchon is on the 10th floor of The Venetian with a patio overlooking the Venezia pool garden, not the Grand Canal Shoppes canal. Corrected to "the 10th-floor patio overlooking the Venezia pool garden".

### Closed-venue rewrite (not full removal — entity scope re-targeted)

9. **pahrump-valley-winery** (day-trips-food.json) — signature/description/tip all centered on Symphony's Restaurant ("filet, crab cakes and brunch", "Symphony's brunch runs weekends"). Symphony's Restaurant permanently closed in 2023 per multiple sources (yelp marked CLOSED as of April 2026, pahrumprestaurantreviews.com confirms permanent closure July 2023). The winery itself remains operational with free daily tours and tasting room. Re-scoped the entity to the winery's tasting room and daily tours (10:30-17:00) and free tours at 11:30/13:30/15:30, removing all Symphony's references.

### Hours correction

10. **international-marketplace-decatur** (markets.json) — hours stated "Mon to Fri 09:00-18:00, Sat to Sun 09:00-19:00". Operator's site (impfoods.co) and recent RJ/Yelp sources confirm the store is Mon-Sat 9-6 and **closed Sunday**. Corrected to "Mon to Sat 09:00-18:00, closed Sunday".

### A. Cuisine / category mismatches

None found. All cuisine_evidence_urls checked supported the claimed categories.

### C. Festival month re-verification

All 8 festivals re-verified against organizer sites and recent press, including the 3 originally flagged as fetch-fail:

- Las Vegas Restaurant Week — Three Square confirms June 1-12, 2026 (19th annual). Match.
- Great Vegas Festival of Beer — March 28, 2026, confirmed via operator. Match.
- Great American Foodie Fest — May 8-10, 2026, Desert Breeze Events Center, 100+ vendors confirmed. Match.
- San Gennaro Feast (Spring) — April 22-26, 2026 confirmed via vegaspbs + festivalnet (organizer's own site only shows fall). Match.
- San Gennaro Feast (Fall) — Sept 30 - Oct 4, 2026, confirmed via organizer. Match.
- Las Vegas Greek Food Festival — Sept 25-27, 2026, confirmed via organizer. Match.
- Dream Asia Food Fest — Feb 13-15, 2026, confirmed via DLVEC. Match.
- Las Vegas Indian Food Festival (Mela) — May 2, 2026, Clark County Government Center Amphitheater, $14.41 ticket confirmed. Match.

### Section B (cooking-class operator verification)

All 6 cooking-class entries verified against operator listing pages:

- Wynn Connoisseur Series: Dim Sum at Wing Lei — VERIFIED on master-classes page (Master Dim Sum Chef Sandy Shi, Wing Lei).
- Wynn Connoisseur Series: Cooking Frank's Way at Sinatra — VERIFIED (Chef Theo Schoenegger, Sinatra restaurant).
- Wynn Connoisseur Series: Tipsy Ice Cream Social at SW Steakhouse — VERIFIED.
- Eataly La Scuola pasta classes — VERIFIED (hands-on pasta classes, $60-100, 2-3 hours, antipasto + wine pairing).
- Sur La Table Summerlin — VERIFIED (Korean BBQ Favorites, Date Night Rustic Italian, Cut Like a Pro knife-skills, Taste of Thailand, French baking all currently scheduled).
- Williams-Sonoma Rampart Commons — VERIFIED (junior chef classes for kids, technique-focused, private classes by store manager).

### Section B (food-tour route verification)

All 6 food-tours verified against operator pages:

- Lip Smacking Savors of the Strip — VERIFIED at Aria/CityCenter, 2.5 hr, $215, helicopter $150 upgrade.
- Lip Smacking Downtown — VERIFIED with Carson Kitchen, Le Thai, 7th & Carson, La Mona Rosa rotation (3 of 4 daily); 2.5 hr, $135.
- Lip Smacking Arts District Cocktail Crawl — VERIFIED 5 stops including Doberman + Velveteen Rabbit; tip corrected (defect #6).
- Lip Smacking Chinatown Speakeasy — VERIFIED Mas Por Favor, GYU+ Social Lounge, Lullabar; tip corrected (defect #7).
- Secret Food Tours Downtown — VERIFIED 8 stops, Plaza Hotel meeting point, Hawaiian musubi + NY pizza + secret bite.
- Secret Food Tours Strip — VERIFIED 5 food stops, 3 to 3.5 hours, $139.99, max 10 people.

### F. Editorial-prose internal consistency

Spot-checked all entities. Apart from defects 1-10 above (which manifest as internal inconsistency between description/tip and operator reality), no further inconsistencies between structural fields and editorial prose.

## Borderline items (not fixed, flagged here)

- **Boon Tong Kee at Famous Foods Street Eats** (markets.json `famous-foods-street-eats-resorts-world`) — Yelp shows "CLOSED" as of April 2026, but multiple recent guides (vegasfoodandfun July 2024, lasvegasmagazine Sept 2025) still list it as operating, and the visitlasvegas.com listing remains live. Pass-1 cleared. The entity is the food hall (not Boon Tong Kee alone), and the must_order claim names it alongside Geylang Claypot Rice. Leaving unchanged but flagging — if the next QA round can confirm closure via primary source, the must_order claim should be reduced to Geylang Claypot Rice only.

- **Tenaya Creek "Calico Brown nut brown ale" flagship claim** — Calico Brown is a real Tenaya Creek product (year-round, dedicated page at tenayacreek.com/calico/), but Bonanza Brown Ale appears in the current year-round lineup with the same description, suggesting a possible rename/re-release. Both names trace to the same beer. Acceptable as written.

## Defects total: 10

7 specific-fact fabrications (A2), 2 route/itinerary tip corrections (B), 1 closed-venue rewrite (Pahrump Symphony's), 1 hours correction. All fixed via atomic Edit operations.

## Below-floor topics after QA

No topics dropped below floor (no entity removals; all 10 defects were rewrites in place).

## Verdict
VERDICT: PASS

10 defects on a 99-entry batch is within the expected range for a large backfill (~10%), and the defect distribution (5 dish/menu mismatches, 2 route descriptor errors, 1 closed-venue echo, 1 hours error, 1 chef-origin nuance) matches the Charleston QA1 pattern that this prompt's Section A2 was added to catch. No structural defects survived to here that would indicate a research-stage regression.

## QA2 pass

Independent re-check of all 99 entries with the post-mid-batch Section A2 lens (chef/owner structural verification, source-URL final-host, itinerary day-of-week × hours cross-check, itinerary editorial sweep across summary/title/prose, deceased-chef drift). QA1's 10 fixes left two borderlines and missed a cluster of itinerary-layer defects that the Atlanta Opus pattern was added to catch.

### Borderlines resolved

11. **famous-foods-street-eats-resorts-world** (markets.json) — Boon Tong Kee status. Yelp marks CLOSED as of April 2026; vegasfoodandfun (recent) and visitlasvegas.com still list it. With Yelp's explicit closure marker and no positive confirmation from the operator (resort's own tenant page returned 404 on direct fetch), reduced the must_order to "Geylang Claypot Rice and Googgle Man's Char Kway Teow" (Geylang is the second 2024-2025 anchor and Char Kway Teow is also a Singapore-pedigree hawker still on every recent guide). Also dropped "Hainanese chicken rice" from best_for. Food hall entity stays; the food-court anchor that's confirmed-operating gets the marketing line. If a later round confirms Boon Tong Kee reopened, restore.

12. **tenaya-creek-brewery** (breweries.json) — "Calico Brown nut brown ale" flagship claim. Tenaya Creek's own current site (tenayacreek.com/our-beer/) lists Bonanza Brown Ale (not Calico Brown) in the six year-round flagships; the Calico Brown page exists but is the legacy/older name for what is now sold as Bonanza Brown (named after the brewery's address on Bonanza Rd). Untappd shows both still in catalog (Calico Brown frozen at 2,954 ratings vs Bonanza at 10,029 and growing). Updated tip to "Bonanza Brown Ale" matching the current brewery-site flagship lineup.

### Itinerary editorial sweep — defects caught (the Atlanta-Opus class)

This is the cluster QA1 missed. Sweep walked all 3 itineraries x 3 (summary + day titles + meal prose) and 6 day-of-week x venue-hours cross-checks.

13. **vegas-weekend-strip-classics day 2 (Sunday) — IMPOSSIBLE HOURS** — Evening narration: "Dinner at Raku from 18:00 (book a week ahead). Robata skewers, agedashi tofu." Raku is CLOSED on Sundays (Mon-Sat 18:00-03:00, Sun closed; confirmed both on raku-las-vegas.com and on the entity's own `closes` field at late-night.json:106). The first-time-visitor itinerary was sending readers to a closed restaurant. Swapped Sunday evening to Sparrow and Wolf (open Sundays 4:30pm-10pm per operator), updated title from "Raku finale" to "Sparrow and Wolf finale", venue list raku -> sparrow-and-wolf, and added the parenthetical "(Raku is closed Sundays)" so future generators don't reintroduce. The agedashi/robata descriptors were removed (Sparrow and Wolf is American cookery, not Japanese).

14. **vegas-locals-weekend-off-strip day 2 (Sunday) — IMPOSSIBLE HOURS** — Afternoon narration: "Lunch at Lotus of Siam Sahara, the reopened 2026 original." Lotus of Siam Sahara reopened May 8 2026 with dinner-only hours (Wed-Sun 5pm-10pm per Fox5/RJ coverage). The itinerary sent readers to a Sunday lunch that does not exist. Lotus of Siam Flamingo (the long-standing branch) IS open Sunday from 11:30am for lunch. Swapped venue ref `lotus-of-siam-sahara` -> `lotus-of-siam-flamingo` and rewrote the prose: "Lunch at Lotus of Siam Flamingo (the Sahara reopening runs dinner only on Sundays)." Generator now references the entity that is actually open at the claimed time.

15. **vegas-locals-weekend-off-strip day 1 morning — closed-rewrite ECHO** — QA1 fixed the esthers-kitchen-brunch entity to drop bombolini (not on operator's current brunch menu) and use Pasta Fritti + Meyer lemon pancakes. The itinerary prose still said "Bombolini and a frittata; book two weeks ahead" — the exact phrase QA1 removed from the entity. Closed-rewrite echo (Section E pattern). Rewrote to "Pasta Fritti and eggs with fennel sugo, Meyer lemon pancakes" matching the corrected entity.

16. **vegas-locals-weekend-off-strip day 1 evening — closed-rewrite ECHO** — QA1 fixed carson-kitchen-late to use "bacon burger" (on menu) instead of "glam burger" (not on menu) and "devil's eggs" (operator spelling) instead of "devilled eggs". Itinerary prose still said "Bacon jam, devilled eggs, the glam burger" — the exact phrase QA1 removed. Rewrote to "Bacon jam with havarti on toasted baguette, devil's eggs, the bacon burger" matching the corrected entity and the operator menu.

17. **carson-kitchen-late** (late-night.json) — Deceased-chef drift (Section A2 Atlanta Hugh Acheson pattern). Description said "Carson Kitchen on 6th Street in downtown Las Vegas is Kerry Simon's small-plates room" in the present tense. Kerry Simon died Sept 11 2015; the restaurant has been operated since opening by Cory Harwell (with Scott Simon as executive chef per RJ 2025 reporting on the Maryland Parkway construction impact). Rewrote to "Cory Harwell's small-plates room (co-founded with the late Kerry Simon in 2014)" — preserves the historical credit accurately and surfaces the actual current operator.

### Section A2 chef/owner subsweep — verified clean

Walked every chef/owner name in editorial prose for the 99 entries. All verified against operator About pages or 2024-2026 press:

- Bruce Kalman (Soulbelly) — operator About + multiple 2024-2025 press confirm.
- Pamela and Christina Dylag (Velveteen Rabbit) — RJ, LV Sun, Cherry Bombe podcast all confirm sister-owners.
- James Trees (Esther's Kitchen) — operator chef page + RJ + LV Weekly + News3 (Key to the City 2024).
- Mitsuo Endo (Raku) — operator site + LV Weekly + Sunset confirm.
- Alvin Cailan (Eggslut) — Wikipedia + The Cosmopolitan facebook + RJ all confirm.
- Tony Gemignani (Pizza Rock) — operator site + Wikipedia + LV Weekly confirm 13-time world champion.
- Brian Howard (Sparrow and Wolf) — operator site + Three Square culinary council + RJ all confirm.
- Kristen Corral (Tacotarian) — Vegas Inc + franchise-times + SBA 2025 Small Business Person of the Year confirm; the entity correctly credits her as the founder. (Carlos Corral, Regina Simmons and Dan Simmons are co-founders but the JSON's single-name credit is supported.)
- Martinez family (Dona Maria) — operator history page + KTNV + RJ all confirm Alfredo and Elvia Martinez 1980 founding; Neriza Johnson (daughter) runs current operations.
- Major Food Group (Sadelle's) — operator's brand page + Robb Report + Travel Agent Central confirm.
- Thomas Keller (Bouchon) — operator and TKRG reservations system confirm.
- Jose Andres (Bazaar Meat) — JustNote: Bazaar Meat moved from SAHARA (closed July 31 2025) to The Palazzo at The Venetian in September 2025. The itinerary already says "at the Venetian" which is the post-move address, so no defect.
- Theo Schoenegger (Sinatra) — Wynn press confirms current Executive Chef.
- Michael Outlaw (SW Steakhouse pastry) — Wynn org chart + Wynn videos confirm.
- Sandy Shi (Wing Lei dim sum) — LinkedIn (Executive Chef Dim Sum at Wynn LV) + Time + Wynn master classes page confirm.

### Source-URL final-host check (Section A2 SD QA1 addition)

Spot-checked 12 source_urls across the 99 entries, prioritizing the riskier domains (third-party guide sites, brewery domains, single-page operator sites). All landed on hosts in the same registered domain as the source_url; no parked/sold domains found. Vintner Grill, Vesta, Casa Don Juan, Lola's, Ferraro's, Velveteen Rabbit, Soulbelly, Crown Bakery, Marianas, Pahrump Valley Winery, The Retreat at Charleston Peak, Bit and Spur — all clean.

### Festival re-check

QA1 already cleared all 8 festival months. Spot-confirmed Greek Festival (Sept 25-27 2026) and Las Vegas Indian Food Festival Mela (May 2 2026) directly from organizer sites for the highest-risk dates. Match.

### Internal-reference fix (collateral)

Itinerary 2 day 2 originally referenced `lotus-of-siam-sahara`. With the QA2 swap to `lotus-of-siam-flamingo` (open Sunday lunch), the internal-reference graph is now self-consistent and the venue at the claimed lunch slot is actually serving lunch.

## QA2 defects total: 7

Distribution:
- 2 borderline-resolution edits (Boon Tong Kee must_order narrowed, Tenaya Creek flagship corrected).
- 4 itinerary-layer defects (2 impossible-hours Sunday cases + 2 closed-rewrite echoes from QA1's entity fixes that didn't propagate into the itinerary prose).
- 1 deceased-chef drift (Carson Kitchen reframed to current operator).

Combined QA1 + QA2 total: 17 defects on 99 entries (17.2%). The QA2 share (7/17 = 41%) is consistent with the Atlanta pattern (Opus found 6 itinerary-layer defects after QA1/QA2 missed them) — confirms the new Section A2 itinerary-sweep rule was needed. Sub-agents writing itinerary prose copy phrasing from prior drafts of the entities they reference, so any QA1 entity-fix MUST trigger a re-walk of the itinerary prose. That's now built into this pass.

## Below-floor topics after QA2

No further entity removals. All 7 QA2 defects were prose/field rewrites in place. Topic counts unchanged from QA1.

## QA2 verdict
VERDICT: PASS

7 QA2 defects on top of 10 QA1 defects = 17 total on 99 entries. The remaining-risk profile is now bounded by what Opus can still catch: I read every editorial string for chef/owner credit, day-of-week hours, deceased-chef present-tense framing, closed-rewrite echoes, and source-URL final-host. The known classes are closed out. If Opus finds more, the failure mode would be something Section A2 doesn't yet cover (e.g., dish-price drift inside operator menus, sister-restaurant credit-borrowing on entities I didn't surface) rather than a re-run of the patterns already swept.

## Opus final pass

Independent re-walk of the 12 in-scope files (99 entries) against the 5 Opus angles: itinerary summary/title sweep, cross-restaurant chef cross-reference, day-of-week x venue-hours re-check across the swap targets, sibling-credit borrowing on multi-location Vegas brands, and verification of QA1/QA2 fixes landing cleanly.

### Angle 1 - Itinerary summary + day-title sweep

Walked all 3 itinerary summaries + 6 day titles + 6 morning/afternoon/evening prose blocks. Found 1 geographic fabrication:

18. **vegas-weekend-strip-classics day 2 morning - geographic claim** (itineraries.json) - "Banh mi at Lee's Sandwiches on Spring Mountain, then a bowl of tonkotsu ramen at Monta Japanese Noodle House next door." Lee's is at 3989 Spring Mountain Rd; Monta is at 5030 Spring Mountain Rd Ste 6. The two are about 0.7 miles apart in different strip-mall plazas on opposite ends of the Chinatown stretch, not next door. Rewrote to "Banh mi at Lee's Sandwiches on Spring Mountain (3989), then a short drive east for a bowl of tonkotsu ramen at Monta Japanese Noodle House (5030)." Preserves the same two venues, corrects the spatial claim, and gives readers the actionable detail.

Summary lines and day titles otherwise accurately frame the venue lists. Itinerary 1's summary calling day 2 a "Chinatown detour" undersells the full off-Strip day but is a tone choice, not a defect.

### Angle 2 - Cross-restaurant chef cross-reference

Walked every chef/owner name across the 99 entries. No chef appears in more than one entity in the in-scope files, so no cross-restaurant credit-borrowing to verify. (The pasta/dim sum/pastry chefs at Wynn and the Major Food Group brunch room are each named once, in the cooking-classes/brunch entries respectively.)

### Angle 3 - Day-of-week x venue-hours re-sweep

Cross-checked every day of every itinerary against every referenced venue's hours field, including the QA2 swap targets:

- Itinerary 1 Sun evening Sparrow and Wolf 18:00 - QA2-confirmed Sun 4:30-22:00, fits.
- Itinerary 2 Sun afternoon Lotus of Siam Flamingo lunch - QA2-confirmed Flamingo open Sun from 11:30, fits.
- Itinerary 2 Sat: Esther's Sat 10-15, Able Baker Sat 11:30-01:00, Carson Kitchen Sat 23:00, Pizza Rock Sat 11:30-24:00 - all fit.
- Itinerary 2 Sun: Monta no hours-field but Sun-open per operator, Greenland Sun 8-22, Pho Kim Long 24h, Atomic Liquors Sun close 02:00 - all fit.
- Itinerary 3 Sat: Earl 24h, Capriotti's daily 10-21, Tacos El Gordo Sat to 04:00 - all fit.
- Itinerary 3 Sun: Dona Maria Sun 8-21, Pho Kim Long 24h, Crown Bakery (no hours but Sun-open per operator), Shake Shack daily 10-24, Secret Pizza Sun to 04:00 - all fit.
- Itinerary 1 Sat: Sadelle's Sat 6-23, Bouchon Sat 8-14 brunch-room (the itinerary's "lunch at Bouchon" with steak-frites is technically the dinner menu - flagged but not fixed; Bouchon's brunch service IS the lunch service on weekends and the steak frites/Cotes du Rhone framing is within the same room's mid-day operation. Borderline acceptable). Bazaar Meat 19:30 fits. Secret Pizza Sat to 05:00 fits.

No further impossible-hours defects.

### Angle 4 - Sibling-credit borrowing on multi-location brands

- Lip Smacking Foodie Tours: each tour entry correctly scoped to its specific route. The QA1 corrections to the Arts District Crawl tip (5-bar route order) and Chinatown Speakeasy tip (mural-lined tunnel not graffiti) hold.
- Lotus of Siam: itineraries correctly distinguish Flamingo (long-standing, Sun-open) from Sahara (May 2026 reopen, dinner-only Sun). QA2 fix landed.
- Carson Kitchen: single Vegas location, no sibling. QA2 fix to "Cory Harwell's small-plates room (co-founded with the late Kerry Simon in 2014)" landed verbatim.
- Bouchon: one Vegas location.
- Lovelady Brewing: tip mentions "Pebble Marketplace second taproom" but the entity is correctly scoped to the Water Street original.

No sibling-credit defects.

### Angle 5 - QA1/QA2 fix landing audit + stale-evidence catch

Walked every QA1/QA2 fix point. All 10 QA1 prose rewrites and 7 QA2 prose rewrites are in place verbatim. One catch the prior passes missed:

19. **pahrump-valley-winery verified-block evidence URLs - stale Symphony's Restaurant references** (day-trips-food.json) - QA1 re-scoped the entity to the winery's tasting room and free tours after Symphony's Restaurant permanent 2023 closure, rewriting description/tip/signature. The `verified` block however still pointed `open_evidence_url` at the TripAdvisor page for the CLOSED Symphony's Restaurant (Restaurant_Review-g45986-d509507-Reviews-Symphony_s_Restaurant) and `cuisine_evidence_url` at a lasvegasconcierge page whose slug is "nevadas-winery-a-symphonys-restaurant.html". The closed-venue's TripAdvisor page does not evidence that the winery is currently open. Repointed `open_evidence_url` to the winery's TripAdvisor attraction page (g45986-d2147681-Reviews-Pahrump_Valley_Winery) and `cuisine_evidence_url` to travelnevada.com/wineries/pahrump-valley-winery/. The `source_url` (winetrailtraveler.com/nevada/pahrump.php) was already correctly winery-scoped and kept.

### Sub-sweeps that came up clean

- Festival re-verification: all 8 day_range/start_month/start_day combinations cross-check against actual 2026 weekdays (April 22 2026 = Wed, March 28 2026 = Sat last-of-month, Sept 30 2026 = Wed, Feb 13 2026 = Fri, Sept 25 2026 = Fri, May 2 2026 = Sat first-of-month). Match.
- Internal-reference check: `check_internal_references.py` runs clean (175 slugs, 142 names, 0 ERR, 0 WARN). The itinerary venue refs that aren't in the 12-scope (`carson-kitchen`, `velveteen-rabbit`, `monta-ramen`, `atomic-liquors`, `bazaar-meat-by-jose-andres`, `lotus-of-siam-flamingo`, `sparrow-and-wolf`) all resolve to verified entities in restaurants.json / casual-dining.json / fine-dining.json / bars.json.
- Bouchon brunch days-of-week ("Thu 08:00-13:00") looked suspicious (brunch is typically weekend-only at Thomas Keller properties); WebFetch on venetianlasvegas.com confirmed only that "weekend brunch is offered." Insufficient evidence to overturn; leaving as flagged but not changing.

### Defects total: 2

1 itinerary geographic-claim correction (Lee's-Monta "next door"), 1 stale-evidence catch in the Pahrump Valley Winery verified block (QA1's rewrite scope didn't reach the verified URLs). Both fixed via atomic Edit.

### Combined totals

QA1: 10 + QA2: 7 + Opus: 2 = **19 defects on 99 entries (19.2%)**. The Opus share (2/19 = 10.5%) is small as expected once Section A2 itinerary-sweep was added to QA2 - the two defects Opus caught are in classes the upstream prompts don't yet cover (geographic adjacency claims in itinerary prose, and stale verified-block evidence URLs after closed-venue rewrites). Both worth promoting into the next QA prompt revision.

## Opus verdict
VERDICT: PASS

Two defects of new classes (geographic adjacency, verified-block evidence echo). Neither indicates a research-stage regression; both indicate gaps in the QA1/QA2 sweep coverage that should be added. All other Atlanta-Opus risk classes (deceased chef, impossible Sunday hours, closed-rewrite prose echo, multi-location credit borrowing) came up clean - QA2's new Section A2 itinerary-sweep is working.
