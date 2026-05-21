# QA2 report - Amsterdam (independent judgment pass)

## Scope inherited from QA1

QA1 had already addressed 23 defects (4 venue removals, 6 address corrections,
4 festival corrections, 3 hours fixes, 5 prose echoes, 1 fabricated narrative).
QA2's brief: independent-directory cross-check on EVERY entity (not sampled),
E2/E3/E4 echo sweep, festival cross-source, source-URL final-host check.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (re-run after QA2 fixes).
- verify_entities.py warnings: 92, mostly the known `own_site_only`
  (`amsterdamfoodie.nl`) cluster on entities where one editorial site is
  the only secondary source, plus the four transient anti-bot 401/403/429
  hosts QA1 already flagged (dignita.nl, moakpancakes.com, feijoa.nl,
  opentable.com tempo-doeloe).

## Judgment defects found

### A. Cuisine / category mismatches + Independent-directory address cross-check

This was QA1's largest miss class (real-URL + fake-address). QA2 ran the
independent-directory check on EVERY entity in restaurants, fine-dining,
casual-dining, cafes, wine-bars, dietary, bakeries, coffee-roasters, brunch,
food-tours, festivals. Defects found:

- `mama-makan` (restaurants): claimed address `Plantage Middenlaan 38, 1018 DG`.
  Independent directories (Yelp, Hyatt official, Hyatt Regency Amsterdam dining
  page, OpenTable, TripAdvisor) all confirm the Hyatt Regency Amsterdam location
  is **Spinozastraat 61, 1018 HJ**. Operator's own contact page corroborates.
  This is the same real-URL + fake-address class QA1 fixed for Tarim/Bakhuys/
  Stubbe's/Bonboon/Hearth/SOIL. Fixed address, prose ("in the Hyatt Regency on
  Spinozastraat"), `verified.address_quoted`, and re-pointed `open_evidence_url`
  to iamsterdam.com + `cuisine_evidence_url` to the Yelp listing for
  independent-directory backing.

- `bolenius` (fine-dining): claimed `George Gershwinlaan 30, 1082 MT Amsterdam`
  in Zuidas with prose "Bolenius in Zuidas runs a one-Michelin-starred kitchen
  with a private herb garden, an Amsterdam fine-dining room shipping vegetable-
  forward menus to the financial district." Independent directories (Michelin
  Guide, Wikipedia NL, De RestaurantKrant, TheFork) confirm Bolenius **moved
  to Rembrandtpark in April 2025**; new address is **Nachtwachtlaan 20B, 1058
  EA Amsterdam**. Renamed to "Bolenius Rembrandtpark", fixed address, rewrote
  description to reflect 2025 move and Green Star, repointed source_url +
  booking_url to `bolenius-rembrandtpark.nl` (the new operator domain;
  bolenius-restaurant.nl 301-redirects to it).

- `moak` (brunch/MOAK Pancakes): claimed `Eerste van der Helststraat 47, 1073
  AB Amsterdam`. Operator's own location page, Tripadvisor, Yelp, Apple Maps,
  and the De Pijp directory all confirm MOAK Pancakes De Pijp is at **Ferdinand
  Bolstraat 11, 1072 LA Amsterdam** (around the corner of Marie Heinekenplein).
  This is the same defect class as QA1's seven address fabrications. Fixed
  address, prose, verified-block, and re-pointed source_url to `moakpancakes.nl`
  (the .nl domain is the canonical operator site; .com is the older redirect).

- `lievelinge` (bakeries) and `lievelinge-hidden` (hidden-gems) and the
  itineraries.json weekend-classics day 2 morning echo: ENTITY DOES NOT
  EXIST. The source_url `https://lievelinge.nl/` resolves to **De Lievelinge,
  a camping site at Haarweg 6, 4214 KL Vuren** (Gelderland province, not
  Amsterdam). Independent searches for an Amsterdam bakery at "Eerste
  Sweelinckstraat 25, 1073 CL" or for any Amsterdam bakery named "Lievelinge"
  return nothing. The agent picked a real domain (lievelinge.nl) and invented
  every other field. REMOVED from bakeries.json (drops 10 → 9), removed from
  hidden-gems.json (drops 8 → 7), rewrote the itineraries weekend day 2
  morning to use Vlaamsch Broodhuys + Scandinavian Embassy instead. Updated
  `region.json` `bakeries.title`/`description` count 9 → 8.

- `headfirst-coffee-roasters` (coffee-roasters): claimed open at Westerstraat
  150HS. Independent directories (Yelp explicitly tagged "CLOSED", Foursquare
  "Now Closed", Sprudge confirms closure) show Headfirst **closed in November
  2015**, more than a decade ago. The thewaytocoffee.com source URL still
  resolves but the underlying venue has been dark for 10+ years. REMOVED
  (coffee-roasters drops 7 → 6). Updated `region.json` `coffee-roasters.title`/
  `description` count 8 → 6.

### A2. Specific-fact / chef / hours / closure drift

- `vinkeles` (fine-dining): chef field `"Dennis Kuipers"` AND description "two
  Michelin stars under Dennis Kuipers". Independent press (De RestaurantKrant,
  Hospitality Management, Misset Horeca, STRRN) confirms Kuipers **left Vinkeles
  in 2022** after 16 years; current executive chef is **Jurgen van der Zalm**.
  And the second Michelin star was awarded in 2023, AFTER Kuipers left, so it
  is structurally wrong to attribute it to him. Fixed `chef` to "Jurgen van der
  Zalm" and rewrote description.

- `sinne` (fine-dining): chef field `"Alexander Werry"`. Michelin Guide,
  restaurantsinne.nl, Restaurant Week 2026, multiple 2026 press sources all
  confirm the chef is **Alexander Ioannou** (Cypriot-Dutch, holding the star
  since 2015). "Werry" is fabricated. Fixed chef name, rewrote description to
  reference Ioannou, re-pointed source_url to the operator's actual domain
  (`restaurantsinne.nl`, not `sinne.nl` which redirects).

- `vicio-il-mastro-pastaio` (restaurants): cuisine framing was "Roman-leaning
  menu of cacio e pepe, carbonara and a daily ragu"; signature dishes listed
  "Cacio e pepe", "Carbonara", "Daily fresh pasta". Operator's own site
  (`vicioilmastropastaio.com`) and The Infatuation review both confirm Vicio
  is explicitly **Sicilian**, not Roman: busiate, caponata, ravioli, cannoli,
  Trapanese pesto, swordfish meatballs with raisins and pine nuts. Neither
  cacio e pepe nor carbonara appear on the menu. The "best Italian restaurant
  in the Netherlands" framing is right but the regional claim is inverted.
  Rewrote signature_dishes to "Hand-made fresh pasta / Sicilian busiate /
  Cannoli", rewrote description and must_order to match Sicilian focus,
  repointed `open_evidence_url` and `cuisine_evidence_url` to the operator
  site (replacing the duplicate amsterdamfoodie URLs).

- `neuf` (restaurants): description "Neuf opened on Haarlemmerstraat as
  Amsterdam's new French bistro". Independent verification: Neuf's own site,
  iamsterdam.com, Bib Gourmand registry all confirm **Bistrot Neuf has been
  open since 2009** and held its Michelin Bib Gourmand continuously since 2013.
  Not new. Rewrote description to reflect the actual 2009 opening date and
  use the full operator name "Bistrot Neuf".

- `kafe-kontrast` (restaurants) and `kafe-kontrast-brunch` (brunch):
  description called it generic "Fusion" with "third-wave coffee, a brunch
  menu, then small plates and natural wine after 18:00." Operator's site,
  yourlittleblackbook, culi-amsterdam, restaurplant, and theinfatuation
  reviews all confirm Kafe Kontrast is specifically **Swedish-Indonesian** under
  chef Ellinor Strinnholm (Swedish, partner from Jakarta), with a structured
  "Kontrast Experience" four-course tasting menu, smorrebrod and kaya toast
  at brunch, weekly rice dishes. Rewrote both descriptions to match the
  operator-stated concept and chef.

- `coba` (restaurants): `booking_url` was pointing to amsterdamfoodie.nl
  (which is not a booking platform). Repointed to operator's own site
  `coba-taqueria.com`.

- `spang-makandra` (restaurants): tip claimed "The west branch on Bos en
  Lommer takes the overflow." Operator's own site and Uber Eats listing
  identify the second branch as "Warung Spang Makandra - Nieuw West" (postcode
  1061 region serves both Bos en Lommer and Nieuw West but the Uber listing
  explicitly says Nieuw West). Fixed phrasing to "A second Spang Makandra
  branch in Nieuw West takes the overflow."

### A2.5. Address postcode corrections

- `leo-bistro` (restaurants): `Beukenplein 22, 1092 BB` → operator site,
  yourlittleblackbook and corner.inc all confirm **1091 KH**. Fixed.

- `jinweide` (restaurants): `Hobbemakade 63, 1071 XK` → Jinweide operator
  TikToks and corner.inc all confirm **1071 XL**. Fixed.

- `vermeers-wijnkamer` (wine-bars): `Zeedijk 11, 1012 AR` → TheFork, novacircle
  and Vermeer hotel listings all confirm **1012 AN** (NH Collection Amsterdam
  Barbizon Palace postcode is AN, not AR). Fixed.

- `vegan-junk-food-bar-de-pijp` (dietary/vegan): `Marie Heinekenplein 9-11`
  → operator's own location page confirms **9-10**. Fixed (address +
  `verified.address_quoted`).

### A3. Source-URL final-host check (Section A2 of PROMPT.md)

- `choux` (restaurants): source_url was `https://chouxchouxchoux.com/` AND
  booking_url the same. Final-host fetch returns BLANK (the page body has
  no business content, no markup identifying the restaurant). Independent
  searches show the official Choux operator domain is **choux.nl**, which
  fetches correctly and lists the De Ruijterkade 128 venue. The
  chouxchouxchoux.com domain is likely a parked/orphaned earlier domain
  (resolves but serves nothing). Repointed `source_url` and `booking_url`
  to `https://choux.nl/`.

All other entities passed the final-host check (source URLs resolve to the
same registered domain or to an authoritative directory).

### B. Route / itinerary mismatches

No food-tour route fabrications detected (QA1 also found none). Hungry Birds
Original, Eating Europe Jordaan, Sherpa, Secret Food Tours and Hungry Birds
Bike all confirmed against operator listings.

### C. Festival month / cross-source check

Re-verified each of QA1's four festival corrections against an independent
non-organiser source.

- `bite-of-amsterdam`: yourlittleblackbook food-festivals-nederland-2026
  page (already cited as `cuisine_evidence_url`) confirms June 19-21 2026.
  No change.

- `tapt-festival`: yourlittleblackbook same page confirms TAPT Amsterdam Oost
  May 8-9 2026 at Flevopark. No change.

- `pint-bockbierfestival`: Operator and PINT Bockbier (independent beer-press
  archive) both confirm Friday/Saturday of first October weekend = Oct 2-3
  2026 at De Hallen Studio's. No change.

- `amsterdamse-terrassen-festival`: hatf.nl and yourlittleblackbook confirm
  July 23-26 2026 at Rembrandtpark. No change.

- `rollende-keukens`: iamexpat.nl Rolling Kitchens calendar confirms May 13-17
  2026. No change.

- `pllek-summer-bbq`: open programme; not a dated festival.

All festival dates pass the cross-source check.

### D. Thin-category fabrications (post-QA1)

- dietary/vegan: 3 (floor 4). Below floor; needs research backfill (Vegan
  Junk Food Bar De Pijp, Bonboon, Hearth all verified open; floor not met
  because QA1 removed Mr & Mrs Watson as closed). NOT a QA2 defect - leaving
  as-is per "no fabricated replacements" rule.
- dietary/vegetarian: 1 (floor 2). Below floor (only SOIL remains after QA1
  removed De Bolhoed). Same - not a QA2 defect, leave for research backfill.
- dietary/gluten_free: 2 (floor 2). At floor, both verified.
- dietary/halal: 3 (floor 3). At floor, all three verified (Bazar at Albert
  Cuypstraat 182, Sham West at Witte de Withstraat 125H, Tarim Uyghur at
  Aalsmeerweg 34H - all cross-checked on Zabihah/Yelp/HappyCow/TripAdvisor).
- dietary/kosher: 2 (floor 2). Both Chabad concepts verified.
- bakeries: 10 → 9 after Lievelinge removal. No formal floor.
- coffee-roasters: 7 → 6 after Headfirst removal. No formal floor.

### E. Editorial-prose echoes

#### E1. Closed-venue echoes (Lievelinge + Headfirst)

- `bakeries.json`: Lievelinge entry removed.
- `hidden-gems.json`: Lievelinge entry removed.
- `itineraries.json` weekend-classics day 2 morning: "Lievelinge on Eerste
  Sweelinckstraat for sourdough by 09:30" → rewrote to "Vlaamsch Broodhuys
  on Haarlemmerstraat for sourdough by 09:30", updated the venues array.
- `coffee-roasters.json`: Headfirst entry removed. No prose echoes elsewhere.
- `region.json` bakeries title/description: "9 Picks" + "Bakhuys, Petit Gateau
  and six more" → updated to "8 Picks" + "five more". Coffee-roasters: "8
  Picks" + "five more" → "6 Picks" + "three more".

#### E2. QA1-removed-fact echoes (Spectrum, Mr & Mrs Watson, De Bolhoed, Lefebvre,
old Tarim/Bakhuys/Stubbe's/Sham/Bonboon/Hearth/SOIL addresses, Taste of
Amsterdam, BroodKaas, Sampurna "Singel branch closed")

Grep across entire data tree for the OLD strings returns ZERO hits. QA1
cleaned these thoroughly.

#### E3. Phantom-venue editorial sweep

Built a Python script that walks all prose-bearing fields in every JSON
file and checks every capitalised proper-noun phrase against the known
entity name/alias set. After excluding sentence-start false positives and
generic terms, ZERO unresolved venue names found. Every named venue in the
prose maps to an entity in the data.

#### E4. Verified-block consistency

For every QA2 address edit (Mama Makan, MOAK Pancakes, Bolenius, Vinkeles
chef, Sinne chef, plus QA1's six prior edits), confirmed the
`verified.address_quoted` matches the NEW canonical address (or is the
verbatim quote from the cited source page). `verified.checked_on` set to
2026-05-20 on every edited entity.

## Defects total: 14

Breakdown:
- 2 venues removed (Lievelinge entirely fabricated; Headfirst closed Nov 2015).
- 3 address corrections (Mama Makan Plantage→Spinozastraat, Bolenius Zuidas→
  Rembrandtpark, MOAK Helststraat→Ferdinand Bolstraat). All three are the
  same real-URL + fake-address defect class QA1's seven shared.
- 2 chef-name corrections (Vinkeles Kuipers→van der Zalm; Sinne Werry→Ioannou).
  Both fabrications - Werry doesn't exist at Sinne; Kuipers left in 2022.
- 3 postcode corrections (Leo Bistro 1092 BB→1091 KH; Jinweide 1071 XK→1071
  XL; Vermeers Wijnkamer 1012 AR→1012 AN; VJFB 9-11→9-10).
- 4 prose / facts corrections (Vicio Roman→Sicilian; Neuf "new"→2009 open
  date; Kafe Kontrast generic fusion→Swedish-Indonesian under Strinnholm;
  Spang Makandra "Bos en Lommer"→Nieuw West; Coba booking_url fix; Choux
  source_url chouxchouxchoux.com→choux.nl).
- 3 itinerary/region echo cleanups (itineraries weekend day 2; region.json
  bakeries + coffee-roasters titles/descriptions).

## Below-floor topics after QA2

- dietary/vegan: 3 (floor 4) - unchanged from QA1.
- dietary/vegetarian: 1 (floor 2) - unchanged from QA1.
- bakeries: 9 (no formal floor) - was 9 after QA1's Lefebvre removal; QA2's
  Lievelinge removal brings it to 8. Still above any plausible floor.
- coffee-roasters: 6 (no formal floor) - was 7; Headfirst removal makes 6.

## Verdict

VERDICT: PASS

(14 defects, three of which are the same real-URL + fake-address class QA1
called out as the structural research-stage regression, two are venue
fabrications/closures the agent missed, two are chef-name fabrications. The
remaining are postcode noise + prose drift. Pattern-wise the city is now
clean enough that an Opus pass should find at most cosmetic issues. The
research-prompt regression noted by QA1 is confirmed: the agent is leaning
on operator URLs without cross-checking the address on an independent
directory, and inventing chef names when sources are silent. Worth a
research-prompt tightening pass before the next NL dispatch.)
