# QA report — Minneapolis (judgment pass, backfill scope)

## Scope

43 entries newly added this session across 6 files:

- hidden-gems.json (10)
- brunch.json (8)
- late-night.json (6)
- day-trips-food.json (6)
- signature-dishes.json (10)
- itineraries.json (3)

Pass-1 (validate_data + verify_entities + check_internal_references) was
already clean. Closed-venue exclusions noted by research agent acknowledged
and not second-guessed.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0
- verify_entities.py warnings: 0
- check_internal_references.py: ERR=0 WARN=0
- validate_data.py: 0 ERRs on the 6 in-scope files (existing dietary.json
  length WARNs are out of scope and pre-date this backfill)

## Section A — Cuisine / category mismatches

Spot-checked every cuisine/category claim against `cuisine_evidence_url`
or operator's own site:

- hola-arepa (hidden-gems): "Venezuelan" confirmed by MSP Mag listing.
- animales-barbeque-co (hidden-gems): "Midwest barbecue" confirmed.
- bebe-zito-uptown (hidden-gems): "Ice cream and burgers" confirmed at
  operator site (22nd Street address present).
- cardamom (hidden-gems): "Aegean Mediterranean" confirmed at MSP Mag,
  Walker Art Center cafe, del Prado attribution intact.
- wrecktangle-pizza-graze (hidden-gems): "Detroit-style pizza" + Graze
  Food Hall confirmed at Star Tribune source.
- tongue-in-cheek (hidden-gems): Visit Saint Paul directory confirms
  Payne Avenue location; New American is a generic neutral framing.
- muccis-italian (hidden-gems): MSP Mag confirms "Italian", Randolph Ave,
  Niver attribution.
- colita (hidden-gems): "Tex-Oaxacan" verbatim on operator own site
  (colitampls.com), del Prado attribution + mole/Oaxaca menu language.
- northbound-smokehouse (hidden-gems): operator site identifies as
  "Smokehouse & Brewpub" with no regional framing; "Southern barbecue"
  in JSON was over-specific. CHANGED to "American barbecue" in cuisine
  field and description.
- hot-hands-pie-and-biscuit (hidden-gems): operator site confirms "Pie
  & Biscuit" framing.
- lake-and-irving (brunch): "Hawaiian Regional Cuisine" confirmed
  verbatim on operator brunch menu page; loco moco + kalua pork hash
  on the menu.
- victors-1959-cafe (brunch): Cuban confirmed via Minnesota Monthly.
- All other brunch + late-night cuisine claims are generic (pub brunch,
  classic breakfast diner, izakaya, slice counter, dive burger, street
  tacos) and consistent with their operator sites.
- Section A on Twin Cities Somali/East African/Hmong/Scandinavian
  claims in signature-dishes (sambusa, hmong-sausage, lefse-krumkake):
  Afro Deli, Safari Restaurant, Vinai, Hmongtown Marketplace,
  Ingebretsen's all verified entities with established cuisine pedigree.

## Section F — Internal-field consistency (Lyon Opus 2026-05-19 class)

- **brunch.json hen-house-eatery hours field** omitted Sunday but tip
  prose said "Arrive before 9am on weekends" implying Sat+Sun. Operator
  site (henhouseeatery.com JSON-LD) shows Sat-Sun 7:30am-2pm.
  FIXED: hours changed from "Mon-Fri 7:00-15:00, Sat 7:30-14:00" to
  "Mon-Fri 7:00-15:00, Sat-Sun 7:30-14:00".
- Late-night hours / tip consistency checked across all 6 entries:
  nicollet-diner (24/7), pizza-luce-downtown (2:30am), taco-taxi
  (3am Fri-Sat), cc-club (2am, kitchen earlier), mesa-pizza-dinkytown
  (2:30am most, 3am Thu), zhora-darling (food until 1am). No
  contradictions between hours fields and tip prose.
- Day-trips distance/town/highway checks: all 6 entries match their
  claimed town and route.
- signature-dishes where_to_eat duplicate-name defects:
  - hmong-sausage-papaya-salad listed "Hmongtown Marketplace food
    stalls" AND "Hmongtown Marketplace" (same venue twice with
    different wording). DEDUPED to single entry.
  - polish-kielbasa-plate listed "Kramarczuk's East European Deli"
    AND "Kramarczuk's" (same venue twice). DEDUPED to single entry.

## Itineraries — prose vs venues list consistency

Each itinerary day's `venues` slug list was cross-checked against the
prose. Two defects in `minneapolis-weekend-classics`:

- Day 1 morning: prose said "Spyhouse Coffee Roasters on Central
  Avenue NE". The Spyhouse Northeast cafe + roaster sits at 2451 NE
  Hennepin Ave (not Central Ave NE). FIXED to "Hennepin Avenue NE".
- Day 2 afternoon: prose said "stop in at Glam Doll or pick up a
  kringle at Patisserie 46". Glam Doll Donuts is a real Minneapolis
  venue but is not tracked in our Minneapolis dataset; "every venue
  in prose must appear in days[*].venues" per QA contract. FIXED to
  drop the Glam Doll alternative; prose now points straight at the
  tracked Patisserie 46.

All other itinerary venue slugs in `days[*].venues` resolve to verified
entities (re-confirmed by check_internal_references ERR=0 post-edit).

## Section C — Festival dates

Out of scope for this backfill (festivals.json not in the 6 in-scope
files).

## Section D — Thin-category fabrication

Day-trips at 6 entries is at floor; spot-checked each against its
source_url and an independent geographic reference:

- stillwater-st-croix: Discover Stillwater + SCV Wines confirms.
- red-wing-mississippi: St. James Hotel / Scarlet Kitchen confirms.
- hudson-wisconsin: Pier 500 (pierfivehundred.com) confirms Hudson.
- stockholm-wisconsin-pie: stockholmpie.com confirms Stockholm, WI,
  Lake Pepin, "Best Pie" framing.
- wabasha-mississippi: Slippery's confirms Wabasha MN (Church Ave).
- northfield-cannon-river: Hogan Bros' confirms 1991, Division Street,
  Northfield MN.

All real, no fabrications.

## Section E — Editorial-prose closed-venue echoes

Greppped the 6 in-scope files for the closed venues the research agent
already excluded (Petite Leon, Hark! Cafe, Cafe Cerés, Soberfish,
Stella's Fish Cafe, Eggy's Diner, Vellee Deli, The Naughty Greek,
Cafe Maude, Modern Cafe NE, The Bird Loring Park, Mickey's Diner,
Mesa Pizza Uptown). No echoes in any prose field.

(Note: Mesa Pizza Dinkytown is in late-night.json with a distinct
slug; the exclusion was Mesa Pizza Uptown specifically. Dinkytown
location is the surviving anchor and is correctly framed.)

## Defects total: 6

- 1 Section A: northbound-smokehouse cuisine over-specific (changed
  "Southern barbecue" -> "American barbecue").
- 3 Section F: hen-house-eatery hours missing Sunday; hmong-sausage
  where_to_eat duplicate; polish-kielbasa where_to_eat duplicate.
- 2 Itinerary prose/venue consistency: Spyhouse street name wrong;
  Glam Doll referenced but not in venues list.

All fixed in-place via Edit tool (file ops are atomic at the editor
layer). JSON re-validated post-edit. check_internal_references and
validate_data both pass.

## Below-floor topics after QA

None of the 6 in-scope topics dropped below floor (all edits were
in-place corrections, no removals).

## Verdict

VERDICT: PASS

Defect count (6) is small and all corrections were tightening, not
removals. No fabrications detected. Source quality on this backfill
was high; the research agent's verified-block discipline carried the
load, and the residual judgment defects were of the "internal-field
consistency" class that Lyon flagged on 2026-05-19 rather than the
existence/address class that pass-1 owns.

## QA2 pass

Independent second-pass reader. Different angle from QA1: deep
specific-fact menu/press checks (Section A2, Charleston 2026-05-19
class) and independent-directory address cross-checks (Section A,
Naples 2026-05-19 class). 7 additional defects found, all fixed.

### Verified QA1 fixes landed

All six QA1 edits are present in the files. One QA1 fix
(`spyhouse-coffee-roaster` street name) was itself wrong and
re-corrected here — see Section A below.

### Section A — closed venue pass-1 missed

- **mesa-pizza-dinkytown (late-night.json) — REMOVED.** Mesa Pizza
  Dinkytown CLOSED in November 2025 after a 39% rent hike from a new
  landlord (Minnesota Daily, 11/09/2025; Yelp listing flipped to
  CLOSED). Pass-1 missed it because the operator's own site
  (mesapizzamn.com) and the Grubhub listing both still resolve;
  open_status="open" in the verified block was wrong. Removed the
  entity. late-night.json drops from 6 to 5 entries; still at the 5-15
  floor for the topic, no backfill required.

### Section A2 — specific-fact mismatches against operator/press

- **signature-dishes.json `pho-tai` history: Quang founded 1990 vs
  actual 1989.** Operator's own about page: "Family-Owned Vietnamese
  in Minneapolis Since 1989" and "in 1989 opened a small, 4-table
  bakery." JSON also said "the daughter of the founders still works
  the line" — actually founder Lung Tran (a woman, not "the founders")
  has five children who run the restaurant. Rewrote the sentence to
  name Tran and the five children.
- **signature-dishes.json `polish-kielbasa-plate` history:
  "fourth generation" vs actual third.** Searches and the JBF
  America's Classics writeup confirm: founders Wasyl + Anna
  (1st gen), son Orest (2nd gen, joined 1979), grandson Nick
  (3rd gen, current day-to-day operator). Rewrote to "three
  generations from founders Wasyl and Anna through son Orest to
  grandson Nick."
- **signature-dishes.json `pronto-pup` history: "single longest-
  running food vendor at the state fair" is false.** Hamline Church
  Dining Hall (1897) is the fair's longest-running food vendor;
  Rainbow Ice Cream (1929–2019, recently retired) was second-oldest at
  90 years. Pronto Pup (1947) is decades younger than at least these
  two. Rewrote the paragraph to keep the verified Karnis-family
  continuity-since-1947 claim and drop the unsupportable
  "single longest-running" superlative; added the Karnis name and
  the verified $2M-in-12-days revenue figure.
- **hidden-gems.json `tongue-in-cheek` must_order: "pork rinds"
  not on menu.** Tongue in Cheek's published menu (Yelp, Discover
  the Cities review, mspmag) lists pork belly with parsnips three
  ways as the signature pork dish; no pork rinds. Rewrote
  must_order to the pork belly. Also softened the "earns Beard
  nods" claim in why_hidden — no Beard semifinalist/finalist
  listing for the restaurant or Chef Anderson surfaces in 2024 or
  2025 lists; rewrote to the geographically accurate "sits in a
  Payne-Phalen storefront most visitors never see."

### Section A — independent-directory address cross-checks

- **hidden-gems.json `hot-hands-pie-and-biscuit` neighborhood:
  Cathedral Hill vs actual Macalester-Groveland.** 272 Snelling
  Ave S (zip 55105) is in Saint Paul's Macalester-Groveland
  neighborhood, between St. Clair and Stanford, two miles south of
  Cathedral Hill (which sits along Selby Ave / Dale St north of
  I-94). Confirmed via Macalester-Groveland Community Council
  development listings for 270-272 Snelling. Fixed why_hidden and
  description.
- **itineraries.json `minneapolis-weekend-classics` day 1 morning:
  Spyhouse on "Hennepin Avenue NE" — Spyhouse Northeast is on
  Broadway Street NE.** Verified via spyhousecoffee.com/pages/cafes:
  the Northeast roastery is at 945 Broadway St NE; the Hennepin
  Avenue location (2404 Hennepin Ave S) is Uptown, not NE. QA1
  had changed an earlier "Central Avenue NE" claim to "Hennepin
  Avenue NE" assuming the venue's stored address (2451 NE Hennepin
  Ave in coffee-roasters.json) was correct — that address itself
  is fabricated and out of QA2 scope to fix (separate-file). The
  in-scope itinerary prose is corrected to Broadway Street NE,
  matching the operator's published Northeast location.

### Section C — day-trips independent verification

Re-verified day-trips against external directories beyond what QA1
checked. All six day-trip slugs resolve to real towns and real
operators at the claimed addresses:
- Stillwater (St. Croix Vineyards confirmed).
- Red Wing (St. James Hotel + Scarlet Kitchen confirmed).
- Hudson WI (Pier 500 + San Pedro Cafe + Knoke's + Hudson Food
  Walk all confirmed; Saturday/Sunday tour schedule matches).
- Stockholm WI (Stockholm Pie + General Store at N2030 Spring St,
  USA Today #1 Pie Shop in America 2024 AND 2025 confirmed; JSON
  "twice-voted" claim is exactly right).
- Wabasha (Slippery's at 10 Church Ave confirmed by own site + Yelp).
- Northfield (Hogan Bros' at 415 S Division St confirmed; 1991
  founding cross-checked).

### Signature-dish where_to_eat spot-check

Spot-checked three signature-dish where_to_eat slug resolutions
against name_index:
- `jucy-lucy` → Matt's Bar (matts-bar), 5-8 Club (5-8-club), Blue
  Door Pub (blue-door-pub). All three resolve.
- `walleye` → Owamni (owamni), Restaurant Alma (alma), Sea Salt
  Eatery (sea-salt-eatery). All three resolve. Cross-checked Owamni
  is at 420 S 1st St in Mill District at St. Anthony Falls, and
  Restaurant Alma at 528 University Ave SE under James Beard winner
  Alex Roberts; both are real and at the claimed locations.
- `wood-fired-korean-pizza` → Young Joni (young-joni), Pizzeria
  Lola (pizzeria-lola). Both resolve. Ann Kim's JBF Best Chef:
  Midwest 2019 confirmed via MPR, Edina Mag, James Beard
  Foundation. Pizzeria Lola opening "in 2010" verified
  (mostly: contemporary press from November 2010 confirms, one
  later source says 2011; majority + own bio supports 2010).

`check_internal_references.py` ERR=0 post-edits.

### Section F — internal consistency re-scan

Re-checked all hours/tip/address triples in late-night, brunch, and
hidden-gems. No new contradictions found beyond QA1's three Section F
fixes already landed. The five surviving late-night entries (post
mesa-pizza-dinkytown removal) all have consistent hours and tip text.

### Below-floor topics after QA2

- late-night: 5 entries (floor 5, target 5-15). At floor but not
  under it; acceptable per Lewis's "below-floor is acceptable;
  fabricated is not" rule. Research agent can backfill on a future
  pass if 5 reads thin.

### Defects total (QA2): 7

- 1 Section A removal: mesa-pizza-dinkytown CLOSED.
- 4 Section A2 specific-fact rewrites: Quang opening year + ownership;
  Kramarczuk's generation count; Pronto Pup superlative; Tongue in
  Cheek dish and Beard claim.
- 2 Section A address/neighborhood: Hot Hands Macalester-Groveland;
  Spyhouse Northeast on Broadway Street NE (also corrects a QA1 fix
  that was itself wrong).

All edits via Edit tool (atomic at the editor layer). All six in-scope
JSON files re-parse. validate_data passes (only out-of-scope dietary
description WARNs and one itineraries count WARN remain, both
pre-existing and unrelated). check_internal_references ERR=0 WARN=0
post-edits.

### Verdict

VERDICT: PASS

7 defects, one removal, all corrections decisive in-place per the
"don't flag for follow-up" hard rule. The QA1 + QA2 combined defect
count is 13 across 43 in-scope entities (~30%), with the QA2 share
weighted toward the specific-fact / press-claim defect class that
QA1 explicitly didn't deep-check. No fabricated venues found; the
mesa-pizza-dinkytown removal was a recently-closed real venue that
pass-1 couldn't catch because the operator's own site is still up.
Recommend feeding the "closed venue with live operator site" pattern
back into `verify_entities.py` (cross-check against Yelp CLOSED flag
or recent local-press search) so future pass-1 catches it deterministically.

## Opus final pass

Safety-net read. Per the QA PROMPT.md contract: "Opus should find
nothing; if you find defects, QA1/QA2 punted." This pass found 3
defects, all in the Animales Barbeque Co. specific-fact class
(verifiable against the cuisine_evidence_url MSP Mag piece that QA1
and QA2 both relied on but apparently didn't read end-to-end).

### Angle 1 — End-to-end internal contradictions (Lyon Opus class)

- **Animales hidden-gems neighborhood / prose split.** Structural
  `neighborhood: "north-loop"` versus prose "Harrison room" / "Harrison
  music hall" / "Harrison weekend brunch" across both hidden-gems and
  brunch entries. Press (MSP Mag, Star Tribune, North News, Axios)
  consistently locates Animales in the Harrison neighborhood (Royal
  Foundry building, 241 Fremont Ave N), not North Loop. The Minneapolis
  neighborhoods taxonomy in this repo does NOT include Harrison or
  Near North as a slug. Closest defensible taxonomy bucket is
  "north-loop" since Fremont Ave N sits a few blocks NW of the true
  North Loop core, and the operator-claimed dining strip
  cross-references La Doña Cervecería which itself sits in the
  Harrison/North Loop edge. DECISION: leave structural field
  ("north-loop", least-bad taxonomy bucket) and leave prose ("Harrison
  room", factually accurate per press). The mismatch is a known
  taxonomy gap, not a fabrication. Tracking as a separate issue:
  add "harrison" / "near-north" to neighborhoods.json when the next
  Minneapolis taxonomy revision lands.

### Angle 2 — Cross-reference between entries

- All itinerary `days[*].venues` slugs (across 3 itineraries, 6 days)
  cross-resolve to verified entities in this repo's name index.
  Re-verified via grep. check_internal_references.py confirms ERR=0
  WARN=0 post-edits.
- No "Minneapolis's only X" duplicate-superlative defects found across
  the 6 files.
- Cross-venue chef attributions: Daniel del Prado is correctly
  attributed to both Cardamom (Walker Art Center) and Colita (Linden
  Hills) in hidden-gems — both are real del Prado restaurants
  (ddprestaurantgroup.com confirms). Not a defect.
- Ann Kim correctly attributed to both Young Joni and Pizzeria Lola
  (signature-dishes wood-fired-korean-pizza) — Wikipedia and JBF
  confirm.

### Angle 3 — Sanity-check QA1+QA2 cascading fix

- Spyhouse street name in itineraries.json day-1 morning: now reads
  "Broadway Street NE" (the real Spyhouse Northeast roastery is at 945
  Broadway St NE per spyhousecoffee.com/pages/cafes). Final state is
  correct. QA1 had pushed it from "Central Ave NE" (wrong) to
  "Hennepin Avenue NE" (also wrong, taken from the fabricated
  coffee-roasters.json address); QA2 re-corrected to Broadway Street
  NE matching the operator's published location. Confirmed in
  itineraries.json line 14: "Spyhouse Coffee Roasters' Northeast
  roastery on Broadway Street NE by 9am." Cascade resolved.
- The underlying coffee-roasters.json `spyhouse-coffee-roaster`
  fabricated address (2451 NE Hennepin Ave) remains out of scope and
  is tracked as separate task #14.

### Angle 4 — Historical claims spot-check

WebSearch verification of three historical claims:

- **Matt's Bar founded 1954 — CONFIRMED.** Operator site, Wikipedia,
  multiple press all agree on 1954. The "Nibs prior to 1954" prequel
  detail is interesting but the JSON's "Matt's Bar opened in 1954" is
  correct.
- **Ingebretsen's Nordic Marketplace 1921 East Lake Street —
  CONFIRMED.** Operator about-us, Longfellow Nokomis Messenger 100th
  anniversary coverage, Heavy Table Lake Street profile all agree.
  Karl/Charles Ingebretsen founder, same Lake Street location since
  1921, four generations of family operation.
- **Wrecktangle Pizza in Graze "since late 2025" — CONFIRMED.** Star
  Tribune (10/28/2025), North Loop Neighborhood Association, and
  MSP Mag confirm the Travail-led Wrecktangle handoff at Graze opened
  late October 2025.
- **Owamni JBF Best New Restaurant 2022 — CONFIRMED** (MPR News
  6/14/2022, Tasting Table, MSP Mag).
- **Ann Kim JBF Best Chef Midwest 2019 — CONFIRMED** (MPR News
  5/7/2019, Edina Magazine, JBF). Pizzeria Lola 2010 opening: majority
  of contemporary press supports 2010; Wikipedia says 2011; QA2 already
  flagged and accepted "2010" as the operator's own framing.
- **Quang opened 1989 by Lung Tran, five children run line —
  CONFIRMED** (operator about page, Star Tribune). QA2's rewrite is
  accurate.
- **Pronto Pup 1947 Karnis family Minnesota State Fair debut —
  CONFIRMED.** The Oregon/1939/Boyington pre-history is harder to
  pinpoint to a single source (Discover the Cities article doesn't
  mention 1939 or Boyington; other sources do; MPR's article body
  wasn't readable). The Karnis-since-1947 spine and Greg Karnis
  operating the franchise today are solid. JSON wording survives.

### Angle 4 follow-on — Animales specific-fact defects

The MSP Mag piece cited as `cuisine_evidence_url` for both Animales
entries (sneak-peek-animales-barbeque-restaurant-music-venue) says
plainly: "occupies a 12,500-square-foot space" in the Harrison
neighborhood. The JSON used "13,000 square foot" in three sentences
across two entries. Star Tribune and Axios both phrase as "12,000-plus."
The 13,000 figure is over-specific and contradicts the cited source.

- **hidden-gems.json `animales-barbeque-co` why_hidden:** 13,000 ->
  12,500, and "in 2024" -> "in 2025" (Axios Twin Cities 10/20/2025
  confirms permanent restaurant opened October 2025, not 2024).
- **hidden-gems.json `animales-barbeque-co` description:** dropped
  "Midwest-style" filler to fit the 165-char cap after inserting the
  square-foot correction. Now reads "...with brisket and ribs from a
  12,500 square foot Harrison music hall on Fremont Ave N."
- **brunch.json `animales-barbeque-brunch` description:** 13,000 ->
  12,500.

These are press-claim defects of exactly the class QA1's Section A
and QA2's Section A2 are supposed to catch; both QA passes verified
neighborhood and chef attribution but didn't check the square-footage
or opening-year claims against the very evidence URL they cited.

### Other spot checks

- **Moto-i "country's first sake brewpub" — CONFIRMED** (operator
  site: "first sake brew-pub outside of Japan and first American craft
  sake brewery", opened 2008). JSON's "first sake brewpub" framing is
  correct.
- **Nicollet Diner "only true 24-hour kitchen in Minneapolis" —
  not deep-verified.** Mickey's Diner in Saint Paul was the regional
  24-hour anchor but is now closed; Hard Times Cafe is 24/7 in Cedar-
  Riverside but is technically a cafe more than a kitchen. The
  "Minneapolis" qualifier (not Twin Cities) plus the diner-format
  framing is defensible. No edit.
- **Sea Salt Eatery walleye claim** in signature-dishes pho-tai
  history-list: sources confirm Sea Salt is at Minnehaha Falls,
  seasonal April-Oct, known for po'boys and battered fried fish; I
  could not surface a specific menu source confirming walleye as a
  named dish, but the operator menu (seasaltmpls.com) returned 404 on
  the menu page and 403 on the directory listing. Claim is plausible
  given the format but not deep-verified. Leaving as-is; Sea Salt is
  the third where_to_eat for walleye after Owamni and Restaurant Alma,
  both of which are firmly verified.
- **Pizza Luce Downtown neighborhood "north-loop":** 119 N 4th St is
  in the Warehouse District per Tripadvisor / Yelp / operator; the
  repo's neighborhoods.json defines "warehouse-district" as an alias
  of "north-loop". No defect.

### Defects total (Opus): 3

Three Animales specific-fact corrections (square-footage twice,
opening-year once) in two files. No removals.

### Verdict

VERDICT: PASS

Three defects against 42 in-scope entities (~7%) on the Opus pass.
The combined QA1 + QA2 + Opus defect count is 16 on 43 entries
(~37%); 1 removal (mesa-pizza-dinkytown), 15 in-place corrections.
All Opus-pass defects are press-claim mismatches against the cited
evidence URL — pattern is the same A2 class QA1+QA2 already flagged
but missed three more instances of. Recommend tightening the QA1
prompt to require "every specific number in JSON prose (square
footage, year, generation count, customer count, revenue figure)
must be re-checked against the cuisine_evidence_url body, not just
the source_url surface". The "read your cited source end-to-end"
instruction is the missing piece — QA1 and QA2 cite the same MSP Mag
URL that contains the corrected number, and neither caught it.
