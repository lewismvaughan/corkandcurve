# QA report - Atlanta (judgment pass-1, backfill scope)

Scope: 53 entries across 7 topic files added in this backfill session.
- cooking-classes.json (5)
- budget-eating.json (12)
- hidden-gems.json (10)
- brunch.json (9)
- late-night.json (8)
- day-trips-food.json (6)
- itineraries.json (3)

Pass-1 (validate_data + verify_entities + check_internal_references)
already cleared all 53. Existence, source URL liveness, address-quoted
fuzzy match, and cross-file slug resolution are owned upstream.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (per backfill agent's report).
- verify_entities.py warnings: 0 reported.
- Research agent self-caught + fixed pre-QA: Waffle House Ponce moved
  to Howell Mill; Snackboxe Doraville closed - switched to Duluth;
  Publix Aprons chain omitted; Majestic Diner dropped (no longer
  24h); R Thomas NW->NE corrected.

## Judgment defects found

### A. Cuisine / category mismatches
- None requiring removal. Cuisine claims in scope held up against
  operator sites or independent directories (Eater, Atlanta Magazine,
  Yelp, Michelin). Cook's Warehouse cuisine list (Italian, French,
  Thai, Mexican, knife skills, baking, pasta, vegan) is unverified
  on the cited kidsoutandabout page but is plausible for an 800-class
  school; not contradicted, retained.

### B. Route / curriculum fabrications (cooking classes - the highest-risk class for this batch)
- cooks-warehouse-midtown: location, hands-on cap 16, school exists,
  cuisines plausibly cover the broad menu of an 800-class school.
  No fabrication found. PASS.
- the-cooking-schools-tri-cities: Hapeville location confirmed,
  Creole / Italian / Thai cuisines confirmed independently (jambalaya,
  Italian seafood night, Massaman curry on schedule). French regional
  not specifically confirmed but plausible. PASS.
- vino-venue-atlanta-wine-cooking-school: Operator listings confirm
  Italian (Northern Italian Classics, Spring in Southern Italy),
  French (Flavors of France), Spanish Tapas Bar, Steakhouse series,
  Pizza & Gelato. Wine-paired by sommelier confirmed. Price $59-119
  matches JSON $60-120. PASS.
- salud-cooking-school-avalon: scoopotp.com confirms Indian, Greek,
  French, seafood technique 101, knife skills, kids classes - all
  matched. Themed-night names (Girls Night Out, Date Night) not
  verified but plausible. PASS.
- unexpected-atlanta-biscuit-class: operator and venue confirmed at
  Sweet Auburn. **Section F defect** on price + group_size:
  JSON had $95 / 12-max; actual (Tripadvisor + GetYourGuide
  listings) is $65 / 14-max per class. FIXED.

### C. Festival month corrections
- N/A. No festivals in this scope.

### D. Thin-category fabrications
- N/A. None of these 7 files is a dietary sub-category. Cooking-classes
  count (5) is on-floor for the topic.

### E. Editorial-prose closed-venue echoes
- Snackboxe Doraville (closed 2024) reference: only appears in the
  hidden-gems Snackboxe entry, which already correctly describes the
  Doraville closure and Duluth reopen. No stale echoes.
- Naga Bistro space (previously Wild Ginger Thai) -> JSON does not
  mention the prior tenant; no echo to scrub.

### F. Internal-field consistency (the new Lyon defect class - hunted hard)

Findings, all FIXED in-place via Edit (atomic writes per Edit tool):

1. **Snackboxe Bistro + Naga Bistro chef attribution** (hidden-gems).
   JSON credited both restaurants to "Chef Anthony and Diana Hayek".
   Actual owners (Atlanta Magazine, Rough Draft Atlanta, AJC): Thip
   Athakhanh and Vanh Sengaphone. Two slugs touched (snackboxe-bistro-duluth,
   naga-bistro-chamblee). Description, why_hidden, and tip rewritten
   to credit Thip Athakhanh. This is a hard fabrication and the largest
   defect in the batch.

2. **Naga Bistro Michelin claim**. Description said "Michelin-recognized
   Cambodian small plates". Michelin recognition is for Snackboxe
   (Lao); Naga is the new 2025 spin-off and has not been Michelin-
   listed yet. Removed the false Michelin claim from Naga.

3. **Petit Chou hours + days** (hidden-gems). JSON said "Lunch 11:00-15:00
   walk-in; dinner only Wed-Sat from 18:00". Actual (Yelp, AJC, axios):
   8AM-3PM daily + dinner Thu-Sat 18:00-22:00. Wrong day-of-week
   (Wed -> Thu) and wrong lunch window (11:00-15:00 -> 08:00-15:00).
   Description also said "dinner four nights a week"; now three.

4. **Unexpected Atlanta biscuit class price + group size** (cooking-classes).
   $95 -> $65, group 12 -> 14. See section B above.

5. **El Rey del Taco closing times** (late-night + itineraries).
   JSON said "Mon-Thu, Sun until 01:00; Fri-Sat until 02:00". Actual
   (operator site): "Mon-Thu, Sun until 02:00; Fri-Sat until 04:30".
   Description claimed weekend 02:00; corrected to 04:30. Itinerary
   echo ("open until 02:00 on Friday") also corrected to 04:30.

6. **R Thomas Deluxe Grill late-night days** (late-night). JSON tip
   said "Cuts off at 05:00 Thursday through Saturday now". Actual
   (Rough Draft April 2024 + multiple sources): late hours are
   Wed-Sat, not Thu-Sat. Fixed.

7. **Maepole proteins + sides** (budget-eating). JSON tip + description
   pushed "brisket on red rice with okra and pickled green tomato".
   Operator menu lists seared chicken, shredded pork, tofu - no
   standard brisket. Red rice / pickled green tomato are not on the
   public side menu (collards, mac and cheese are the highlighted
   Georgia toppings). Rewrote to verified proteins and sides.

8. **Pielands square pizza style** (budget-eating). JSON said "Square
   Detroit-style with pesto and pulled mozzarella". Operator copy
   explicitly states the Noni square pie has "a thinner and denser
   crust than Sicilian or Detroit style pizza". Renamed to the actual
   square (Green Granny / Noni); description updated to "16-inch
   square Noni pies" instead of mis-claiming Detroit.

9. **Argosy tap count** (hidden-gems). JSON said "32 taps". Operator
   site and Pixelation feature say "41 rotating taps". Fixed in
   why_hidden + description.

10. **Day trip Athens attribution** (day-trips-food). JSON listed
    "Hugh Acheson's Five and Ten". Acheson sold the restaurant to
    Peter Dale in April 2024; Dale also owns SeaBear. Updated the
    signature line to attribute Five and Ten and SeaBear to Peter
    Dale.

11. **Naga Bistro prahok ktis description** (hidden-gems). My first
    pass tightened "fermented-fish dip" to "fermented-pork dip";
    on re-check prahok ktis is fermented-fish-paste + pork dip.
    Reverted to "fermented-fish and pork dip" - more accurate than
    either original or first edit.

## Itinerary venue cross-check (Section F deep-dive)

Re-walked every `days[*].venues` slug in itineraries.json against the
source-of-truth file for each venue:

- atlanta-weekend-classics day 1: lees-bakery-banh-mi (Buford Hwy),
  prose says "banh mi at Lee's Bakery" - consistent.
- atlanta-weekend-classics day 2: home-grown-brunch (Reynoldstown),
  yalla-krog-street (Inman Park), bell-street-burritos-krog (Inman Park),
  octopus-bar (East Atlanta Village) - all neighborhoods + prose match.
- atlanta-buford-highway-deep-dive: drive direction (LanZhou Hwy 5231
  Doraville south to Crawfish Shack 4337) consistent with prose
  "drive south on Buford Highway". Naga Bistro Chamblee, El Rey del
  Taco Doraville all consistent.
- atlanta-budget-three-days day 1-3: all venue slugs map to actual
  Westside, Decatur, Buford Highway addresses matching the prose.

No itinerary-prose contradictions found beyond the El Rey closing-time
fix above.

## Defects total: 11 (all fixed)

By category:
- Section A: 0
- Section B: 1 (price/group size on the cooking class)
- Section C: 0
- Section D: 0
- Section E: 0
- Section F: 10 (the new Lyon-class hunt was the productive one)

## Below-floor topics after QA
- All 7 in-scope files remain at the entry counts they had pre-QA
  (no removals). No floor regressions caused by this pass.

## Verdict

VERDICT: PASS

Rationale: K=11 defects all internal-field-consistency or curriculum-
detail fixes; zero entities removed; zero existence/fabrication
defects at the entity level (the prior research agent's self-catches
already cleared the closed-venue risks). The Section F volume confirms
the Lyon finding generalizes - "real venue, wrong details" is now the
dominant defect class once verify_entities owns existence/address.

## QA2 pass

Independent second pass on the same 53-entry scope. QA1's 11 fixes
were verified - all landed cleanly, no over-corrections that needed
walk-back. Specifically re-confirmed:

- Petit Chou: 08:00-15:00 daily + dinner Thu-Sat 18:00 - matches FAQ.
- El Rey del Taco: weekend close 04:30 - matches operator site.
- R. Thomas: Wed-Sat 07:00-05:00 late shift - matches operator site.
- Snackboxe / Naga: Thip Athakhanh attribution is correct (real owners
  are Thip + husband Vanh Sengaphone; crediting only Thip is incomplete
  but not wrong, no edit needed).
- Naga Michelin claim removal: correct - Naga's own about page promotes
  "Chef Thip is MICHELIN-recognized" but the recognition is for
  Snackboxe; QA1's removal from Naga prose was right.
- Naga prahok ktis "fermented-fish and pork dip" wording: correct -
  authoritative sources (SreyDa, Wikipedia, multiple recipe sites)
  all describe prahok ktis as fermented fish paste (prahok) + ground
  pork; Naga's own menu shortens to "spicy pork dip" but the JSON's
  longer phrasing is the accurate culinary description.
- Pielands square pie (not Detroit-style), Argosy 41 taps, Maepole
  proteins, Acheson -> Dale Five and Ten attribution, biscuit class
  $65 / 14-max: all verified.

### New A2 defects found (QA1 missed)

4 new defects found and FIXED in-place via Edit (atomic):

1. **Octopus Bar closed-day defect** (late-night + hidden-gems).
   Operator (and Atlanta Magazine guide) say "every night except
   Sunday" - i.e., open Mon-Sat. JSON in both files said "Tue-Sat,
   closed Sun-Mon" and "Tuesday through Saturday." Same defect class
   QA1 caught for R. Thomas / Petit Chou - day-of-week from memory,
   wrong by one day. Fixed `closes` field to "Mon-Sat 22:30-02:30;
   closed Sun" and edited the why_hidden / description prose in both
   files to "Monday through Saturday."

2. **Octopus Bar stale ownership** (late-night). Description said
   "run by Nhan Le and Angus Brown." Angus Brown died January 4, 2017
   (AJC, Creative Loafing, WSB-TV). Same defect class as the Hugh
   Acheson / Five and Ten stale-ownership entry QA1 caught for Athens
   day-trip. Rewrote to "So Ba owner Nhan Le's late shift" - Nhan Le
   continues to run Octopus Bar per Atlanta Magazine.

3. **The General Muir hours fabrication** (brunch). JSON said "Daily
   07:00-15:00; weekend brunch 08:00-15:00." Operator's official
   Emory Point page: Mon-Tue 08:00-14:00, Wed-Sun 08:00-15:00 then
   dinner 17:00-21:00 (Wed-Thu/Sun) or 17:00-21:00 (Fri-Sat). Never
   opens at 07:00 on any day. Fixed to "Mon-Tue 08:00-14:00; Wed-Sun
   08:00-15:00 then dinner from 17:00."

4. **Buena Gente hidden-gems open-time** (hidden-gems). JSON tip said
   "croquetas and Cuban coffee from 08:00." Operator site: Thu-Fri
   8AM-2PM, Sat-Sun 9AM-2PM. The 08:00 claim only holds Thu-Fri.
   Fixed to "from 08:00 Thu-Fri and 09:00 Sat-Sun."

### Knock-on itinerary defect

5. **atlanta-weekend-classics day 2** referenced Octopus Bar on a
   Sunday night. After fixing #1 (Octopus closed Sun), the Sunday
   itinerary became impossible. Cleanest fix without rebuilding the
   itinerary: swap Octopus Bar for **El Rey del Taco** (open Sun
   until 02:00 per its operator site). Edited the day_number 2 title
   to "late-night Buford Highway tacos," the evening prose to "Late
   tacos at El Rey del Taco on Buford Highway; al pastor with
   pineapple and an agua fresca, kitchen open Sunday until 02:00,"
   and the venues array to swap `octopus-bar` -> `el-rey-del-taco-late-night`.
   Day 1 (Saturday) untouched - Bacchanalia is open Sat.

### Other A2 / A spot-checks - PASS

- Reuben's Deli "The Eastsider" - on menu, closed Sunday confirmed.
- Ria's Bluebird Mon/Tue/Thu-Sun 08:00-15:00 closed Wed - matches.
- Home Grown daily 08:00-14:00 + Michelin-recommended - matches.
- Folk Art Mon-Fri 07:30-15:00 / Sat-Sun 09:00-17:00 - matches.
- Murphy's brunch Sat-Sun 09:00-16:00 + crab cake benedict - matches.
- Toast on Lenox "Lobster Sweet Potato Waffle" - exact menu item;
  Black-owned + woman-owned confirmed.
- Marcus Bar Sat-Sun 10:30-14:00 + $55 buffet + Samuelsson - matches.
- BeetleCat Sat-Sun 10:00-14:30 + Ford Fry seafood - matches.
- Southern National Sun brunch 11:00-15:00 + Duane Nutter - matches.
- Landmark Diner 24/7 + 1994 founding - matches.
- Bucket Shop Cafe Mon-Sat 11:00-03:00 / Sun 11:00-00:00 - matches.
- OK Yaki Tue-Sat per JSON closes match operator - matches.
- Velvet Taco Buckhead day-by-day hours - matches.
- Waffle House Howell Mill 24/7 + 1700 Howell Mill - matches.
- Quoc Huong closed Thursdays - confirmed.
- Hankook Taqueria closed Sunday - confirmed.
- Crawfish Shack closes 19:00 most nights - 4/7 days at 19:00, 2 at
  20:00, 1 at 18:00 - JSON wording holds.
- Arepa Mia chef-owner Lis Hernandez closed Sun-Mon - confirmed.
- Day trips: Nic and Norman's (Reedus + Nicotero still credited),
  Bistro Hilary (Chef Hilary White still running), Easy Bistro (Niel
  family + James Beard nom), Serenbe 4 restaurants confirmed,
  Dahlonega 4 wineries all open, Madison restaurants confirmed.

### Defect counts

- QA2 new defects found: 5 (4 A2 + 1 itinerary knock-on)
- QA2 over-corrections of QA1: 0
- Removals: 0
- Below-floor regressions: 0

VERDICT (QA2): PASS

Combined QA1 + QA2 defect tally: 16. The QA1 pass cleared most of
the heavy lifting (chef name fabrications, big hours errors, the
Pielands inversion); QA2's residual catches were tighter (one
neighbouring-day-of-week mistake on Octopus Bar that cascaded into
a Sunday-itinerary mismatch, plus one stale-co-owner reference, plus
two hours-on-margin errors). No fabricated entities; the entity-level
quality of this backfill batch is solid.

## Opus final pass

Independent third pass, narrow scope: itinerary-prose A2 sweep,
day-of-week x venue-hours cross-check, end-to-end entity-field read,
and verification that QA1+QA2 fixes landed cleanly (per the
Charleston-Opus precedent that itinerary prose hides defects the
entity-level sweep misses).

QA1+QA2 fix verification: all 16 fixes confirmed landed cleanly.
Specifically re-checked: octopus-bar Mon-Sat closes + prose in both
late-night.json and hidden-gems.json (clean); el-rey-del-taco Sunday
swap in atlanta-weekend-classics day 2 venues array + prose + hours
field (clean - kitchen open Sunday until 02:00 matches operator);
the-general-muir hours (clean); buena-gente hidden-gems open-time
wording (clean); Pielands "Noni square" vs "Detroit-style" wording
(clean); Snackboxe/Naga chef attribution to Thip Athakhanh (clean);
R. Thomas Wed-Sat late shift (clean); Petit Chou Thu-Sat dinner +
08:00-15:00 daily lunch (clean); Maepole proteins/sides (clean);
Argosy 41 taps (clean); Five and Ten -> Peter Dale (clean);
biscuit class $65 / 14-max (clean).

### Opus-class defects found

4 new defects found in itinerary prose + entity-itinerary
cross-checks, all FIXED in-place via Edit (atomic):

1. **Holeman and Finch Bread impossible open time** (itineraries
   atlanta-weekend-classics day 1). Prose said "Holeman and Finch
   Bread at 08:00 for the morning bun and laminated pastries."
   bakeries.json shows H&F Bread hours: "Wed-Sat 09:00-15:00." The
   08:00 timestamp is impossible - bakery does not open until 09:00.
   Fixed prose to "Holeman and Finch Bread in Buckhead at 09:00".
   Same defect class as QA1 Petit Chou hours - hour-from-memory off
   by an hour. Day_number 1 is "Saturday" so the Wed-Sat operating
   window holds.

2. **Holeman and Finch wrong-neighbourhood + wrong-product day title**
   (same itinerary, same day). Title said "Saturday: Westside biscuits,
   Buford Highway lunch, fine-dining dinner." H&F Bread is at 2277
   Peachtree Rd NE in Buckhead, not the Westside, and produces
   sourdough + viennoiserie (croissants, morning buns), not biscuits.
   Two errors in three words. Rewrote title to "Saturday: Buckhead
   bakery, Buford Highway lunch, Westside fine-dining dinner" (which
   now correctly places the Westside frame on Bacchanalia where it
   belongs). Same defect class as Lyon "right venue, wrong details" -
   the venue itself is correct but the framing prose lies about its
   neighbourhood and what it makes.

3. **Buena Gente dinner-service fabrication** (itineraries
   atlanta-budget-three-days day 2). Prose said "Dinner at Buena
   Gente Cuban Bakery in Decatur if it's Thursday-Sunday; Cubano
   sandwich ($14) and a colada coffee. Otherwise a Mary Mac's Tea
   Room Southern Special for $23 in Midtown." Buena Gente operates
   Thu-Fri 08:00-14:00, Sat-Sun 09:00-14:00 (confirmed against
   buenagenteatl.com - QA2 already fixed the hidden-gems open-time
   wording). The bakery closes at 14:00 every day it's open and
   serves no dinner. The "Dinner at Buena Gente" branch is impossible.
   Cleanest fix without bloating the day: drop the Buena Gente
   branching alternative, drop the slug from the venues array, and
   collapse the evening to Mary Mac's Tea Room as the dinner. Also
   dropped the unverified "$23" price claim - swapped to a
   menu-shape description ("three meat-and-three sides, free pot
   likker with cornbread to start") that matches Mary Mac's actual
   Southern Special composition. Same defect class as the QA2
   octopus-bar Sunday cascade - one entity's wrong hours assumption
   broke a downstream itinerary day.

4. **Inman Park and Decatur day title without Decatur venue** (same
   itinerary, same day, knock-on of #3). After removing Buena Gente
   the only Decatur reference disappeared. Title "Day 2: Inman Park
   and Decatur" was no longer accurate. Updated title to "Day 2:
   Virginia Highland, Inman Park and Midtown" which matches the
   actual venue neighbourhoods (Pielands VaHi, Aurora VaHi, Yalla
   Inman Park, Bell Street Inman Park, Mary Mac's Midtown).

### Itinerary summary-line fabrications (also Opus-class)

Two summary lines for itineraries.json overpromised content not
present in the days:

5. **atlanta-weekend-classics summary** had "soul food on the
   Westside, Korean BBQ on Buford Highway, biscuits and BeltLine
   bakeries." The itinerary actually contains: H&F Bread Buckhead
   (morning buns/sourdough, not biscuits, not BeltLine), So Kong
   Dong (Korean tofu/soondubu, not BBQ), Lee's Bakery banh mi,
   Bacchanalia (New American tasting, not soul food), Home Grown
   brunch (Reynoldstown, not Westside soul food), Krog Street Market
   stalls, El Rey late-night tacos. Three claims in the summary
   were either wrong-cuisine (soul food, Korean BBQ) or wrong-place
   (BeltLine bakery). Rewrote to a faithful summary covering what
   the days actually contain.

6. **atlanta-buford-highway-deep-dive summary** had "from Doraville
   Korean to Chamblee Cambodian to Vietnamese banh mi counters."
   The itinerary starts at LanZhou Ramen in Doraville (Chinese
   hand-pulled noodles), not Korean. No Korean venue is on this
   itinerary day at all. Same defect class as #5 - summary line
   mis-claims a cuisine the day doesn't visit. Fixed "Doraville
   Korean" to "Doraville hand-pulled noodles" (which is what LanZhou
   actually serves).

### Spot checks that PASSED

- Bacchanalia open Sat dinner (Mon-Sat 5:30pm per operator) - clean.
- LanZhou Ramen open Fri 11:30 (11:00-21:30 daily per operator) - clean.
- El Rey Sunday 02:00 close - matches `closes` field.
- El Rey Friday 04:30 close - matches `closes` field.
- Crawfish Shack afternoon visit Friday - hours support (closes 19:00).
- Folk Art Sat-Sun 09:00-17:00 - matches.
- Home Grown Daily 08:00-14:00, 08:30 Sunday visit - clean.
- Hankook closed Sundays - itinerary day 1 doesn't pin a day, neutral.
- Quoc Huong closed Thursdays - itinerary day 3 doesn't pin a day, neutral.
- Itinerary day venue slugs all resolve (cross-file references intact).
- All entity neighbourhoods match address fields in source files.
- No duplicate "Atlanta's only X" claims found across hidden-gems
  (Snackboxe = only Lao kitchen, Naga = only Cambodian small plates,
  Arepa Mia = only fully-gluten-free Venezuelan, all non-overlapping).
- No stale chef-name borrowing across entries (Snackboxe/Naga both
  correctly credit Thip Athakhanh, no cross-contamination with
  Octopus Bar's Nhan Le or any other operator).

### Defect counts

- Opus new defects found: 6 (4 itinerary-prose + 2 summary-line)
- Opus over-corrections of QA1/QA2: 0
- Removals: 0
- Below-floor regressions: 0

VERDICT (Opus): PASS

Combined QA1 + QA2 + Opus defect tally: 22. Opus's catches were
itinerary-layer defects that the entity-level QA passes structurally
cannot see: an impossible open time in narrative prose (08:00 H&F
Bread), a wrong-neighbourhood + wrong-product day title (Westside
biscuits at a Buckhead viennoiserie bakery), a no-dinner-service
fabrication (Buena Gente dinner branch when bakery closes 14:00),
and two summary-line cuisine misclaims (Korean BBQ, soul food on
Westside, Doraville Korean) overpromising content the days don't
deliver. Charleston-Opus precedent confirmed for Atlanta: itinerary
prose hides a defect class the entity-field sweep misses, even after
two judgment passes. Recommend QA agents add an explicit pass-3
itinerary-prose + summary-line check, or roll this lens into QA2.
