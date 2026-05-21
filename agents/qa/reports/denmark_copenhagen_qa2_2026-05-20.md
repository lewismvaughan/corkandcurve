# QA report — Copenhagen (judgment pass 2)

Country: denmark
City: copenhagen
Date: 2026-05-20
Pass: QA2 (independent second judgment pass)

## QA1 carry-forward

QA1 (2026-05-20) made 8 file-level rewrites across 4 files: itineraries
(4 day-of-week mismatches), neighborhoods (2 vibe rewrites), region
(14 SEO description rewrites), food-history (1 era summary fix).
Returned VERDICT: PASS.

QA2 ran an independent fresh pass, focused on:
- E2/E3/E4 echoes of QA1 rewrites
- Independent-directory address cross-check of 10-15 entities NOT
  sampled by QA1
- Section A2 specific-fact + chef-name structural checks
- Section B food-tour route-vs-operator-offering verification
- Section C festival cross-source (2026-specific independent sources,
  not just operator homepages)
- Itinerary geographic-adjacency claims
- Source-URL final-host redirect checks

## Judgment defects found

### A. Cuisine / category mismatches
- None. All non-dietary cuisine claims hold up (Sicilian Mirabelle,
  Japanese ramen Slurp, Texas BBQ WarPigs, Mexican Hija de Sanchez,
  French-Italian Café Wilder, Holistic Cuisine Alchemist, Northern
  European Barr, Smørrebrød Schønnemann/Aamanns/Selma/Sankt Annæ).

### A2. Specific-fact / address / chef-name / hours issues

1. **Pompette** wine bar — `address` was generic "Nørrebro, 2200
   København N" (no street), `verified.address_quoted` echoed the same.
   Real address per VisitCopenhagen: Møllegade 3, 2200 København N.
   Fixed in `wine-bars.json` and `hidden-gems.json`. Source URL
   re-pointed from `shop.pompette.dk/pages/about` (timeout) to the
   VisitCopenhagen listing for both. Also rewrote the hidden-gems
   `why_hidden` which claimed Pompette sits "between Pluto and the
   Coffee Collective shop" — Pluto is in Indre By (2km south),
   Coffee Collective Jægersborggade is 600m north; the geographic
   triangulation didn't work. Replaced with "a short walk north of
   Nørrebrogade".

2. **Café Wilder** — three files claimed "since 1972" / "1972" /
   "50-year-old" / "50 years"; real founding per Visit Copenhagen and
   multiple sources is **1984** (12 years off). Fixed in `cafes.json`,
   `casual-dining.json`, `hidden-gems.json`, `brunch.json`. The
   "50 years" must_order claim corrected to generic "decades".

3. **Restaurant Sankt Annæ** — two files claimed "since 1897"; the
   operator's own About page says **1894**. Fixed in `casual-dining.json`
   and `hidden-gems.json`.

4. **Andersen Bakery (Nimb/Tivoli, Bernstorffsgade 5)** — Visit
   Copenhagen's current listing for Andersen Bakery is
   **Thorshavnsgade 26 in Islands Brygge**, not Bernstorffsgade 5.
   The Bernstorffsgade Nimb branch appears to have closed or moved;
   no current operator-confirmed listing remains at Bernstorffsgade 5.
   Repointed the entity to the live Islands Brygge address, renamed
   slug to `andersen-bakery-islands-brygge`, updated description and
   tip. ALSO fixed: chef/founder name "Hiroshi Andersen" was a
   conflation of Hiroshima (the city where the Andersen chain was
   founded in 1967) and a Japanese first name. The actual founder
   is **Shunsuke Takaki**; the bakery brand is named for Hans
   Christian Andersen. Rewrote prose to reflect the Takaki family
   in Hiroshima.

5. **Prolog Coffee** — tip credited founders as "Jonas Gehl and
   Sebastian Vinther Olsen". Sebastian's surname is **Quistorff**,
   not Vinther Olsen (confirmed via World Coffee Events bio + multiple
   roaster profiles). Fixed.

6. **Beyla brunch (Jeson Renwick)** — typo: founder's name is
   **Jason Renwick**, not "Jeson". Fixed in `brunch.json` and
   `dietary.json`. Also reframed the brunch description: data said
   "former Souls chef-owner" but Beyla IS Souls under a new name (the
   same restaurant under a rebranded mythological name), not a
   successor. Rewrote to "Ark Collection founder Jason Renwick".

7. **Geranium booking** — tip claimed "Booking opens four months
   ahead on the first of the month"; the operator's actual booking
   policy is **three months ahead via SevenRooms** with a 1,500
   kroner deposit per guest. The
   "first of the month at 13:00 Copenhagen time" specificity is
   uncited and not on the operator page. Fixed restaurants.json tip
   and `fine-dining.json` reservation_lead_time from 4 months to 3.

8. **Alchemist booking** — tip claimed "Booking opens three months
   ahead via Tock at 13:00 Copenhagen time on the first of the month.
   The wine pairing adds DKK 3,800." Three-month booking via Tock is
   confirmed; "13:00 first-of-month" is uncited; the operator's
   ticket page says beverages are charged at end of meal (not a
   fixed DKK 3,800 add-on). Rewrote to verified language about
   "tickets release roughly every three months via Tock and disappear
   in seconds; beverages charged separately at end of meal."

9. **Timm Vladimirs Køkken** address — data had "Vesterbrogade 27,
   1620 København V" with prose "on Vesterbrogade in Vesterbro";
   real Copenhagen location per timmvladimirskoekken.dk is
   **Raffinaderivej 10F, Bygning 1, 2300 København S** (Amager).
   Vesterbrogade 27 is a 200m-off-from-anything fabrication. Fixed
   address, address_quoted, source_url, and description.

### B. Route / itinerary mismatches (food-tours/cooking-classes)

10. **Copenhagen Food Tours "Vesterbro food walk"** entity — REMOVED.
    The operator (foodtours.eu) IS real and DOES run a Vesterbro/
    Kødbyen tour, but the actual route is "The West End Gourmet Tour"
    starting at Vesterbros Torv (Vesterbrogade 49), and the stops are
    coffee, Middle Eastern lunch, gourmet ice cream, gourmet pizza,
    chocolate, craft beer — NOT "tacos, Texas BBQ, natural wine and
    craft beer from Mikkeller", and NOT covering "WarPigs counter and
    Hija de Sanchez". The route description, meeting point, and
    described stops are a route fabrication on a real operator.
    Per QA prompt rule "do not try to substitute a different route
    from the same operator", removed the entity. Topic drops from 5
    to 4 (below the 5 floor but acceptable per prompt).

11. **Copenhagen by Mie food tour** — `route`, `meeting_point`,
    `duration`, `price`, and `affiliate_url` all needed correction.
    Real tour: "Yummy Copenhagen: A Food Tour of Past & Present", 4
    hours (not 3), EUR 130 (not DKK 695, which is half the real
    price), meeting point Fiolstræde 44 in front of Pincho Nation
    (not Nytorv 17), starts 11:30 daily. Rewrote whole entity to
    real route specifics, kept operator and slug.

### C. Festival month corrections (cross-source verification)

All 5 festivals cross-checked against at least one independent
2026-specific source (not just operator homepage):
- **Copenhagen Cooking and Food Festival** Aug 21-30 2026 — confirmed
  via VisitDenmark events calendar + Carnifest + neventum tradeshow
  listings.
- **Mikkeller Beer Celebration (MBCC)** May 22-23 2026 — confirmed
  via independent ticketing (UnitedTickets) showing explicit "22-23
  May 2026" in event title + AllEvents listing.
- **Mikkeller Beer Week** May 18-24 2026 — confirmed via Mikkeller's
  2026 news post.
- **Tivoli Food Festival** May 23 onwards, 9 days — confirmed via
  Falstaff 2026 preview + Wonderful Copenhagen 2026 events listing.
- **Tivoli Christmas Market** Nov 14 to Jan 4 — confirmed via
  multiple 2026 guides (ultimatechristmasmarkets, livelikeitstheweekend
  etc.). All four annual recurrence patterns hold.

### D. Thin-category fabrication sweep

- dietary/kosher: 0 (no Copenhagen kosher ecosystem; below-floor
  acceptable).
- dietary/halal: 2 (both real: Kebabish + Killer Kebab; halalfoodle
  confirms).
- dietary/vegetarian: 2. Geranium (vegetable menu) description
  rewritten — said "turned fully vegetarian in 2022", which is
  inaccurate; Geranium removed land meat in January 2022 but still
  serves seafood. Reframed as "removed land meat from its menu in
  2022, with Rasmus Kofoed's tasting now built on vegetables and
  seafood, three Michelin stars retained."
- dietary/gluten-free: 2 (Beyla + 42 Raw; both findmeglutenfree
  confirmed).
- dietary/vegan: 3 (Ark + Beyla + 42 Raw; happycow confirms all).
- coffee-roasters: 5 (one chef-name typo fixed at Prolog; no other
  defects).
- markets: 5 — multiple vendor-list defects (see E3).
- food-tours: 4 after removal in B (was 5, floor is 5; acceptable
  below-floor per prompt rules; do NOT fabricate).
- cooking-classes: 5 (one address defect fixed at Timm Vladimirs).

### E. Editorial-prose echoes

**E1. Closed-venue echoes** — re-checked Noma/Souls/Restaurant 108/
Manfreds/Relae/Bror. After QA1's removal of "Manfreds-era rooms"
from neighborhoods.json Nørrebro vibe, no other active-operator
Manfreds reference remains. The single Souls reference in brunch.json
(former chef-owner) was rewritten this pass (E2/A2 #6).

**E2. QA-removed-fact echoes** — grepped data tree for every value
QA1 changed (22 strings). Found one residual: "seven more" cafes
phrase in region.json cafes description, but verified: 3 named + 7
more = 10 cafes total, count is correct (not an echo of brunch
"seven more" which QA1 changed to "five more"). No false-positive
echoes found from QA1's other rewrites.

**E3. Phantom-named-venue / fabricated-vendor sweep**

12. **Broens Gadekøkken vendor list** — described as "Gasoline Grill,
    GRØD and Palægade" (markets.json) and "Gasoline Grill, GRØD,
    Palægade and Dhaba" (street-food.json). Per broensstreetfood.dk
    food page, actual current vendors include Gasoline Grill (real),
    Hija de Sanchez (real), Hooked (real), Strangas Gyros, Rørt
    smørrebrød, Pasta la pasta, Crêpes à la cart, Haddock's Seafood,
    Kejser Sausage, Fuego, District Tonkin, Phago, Abrikos. GRØD,
    Palægade, and Dhaba do NOT appear at Broens (GRØD is at
    Torvehallerne; Dhaba is at Tivoli Food Hall; Palægade is an
    independent smørrebrød restaurant in Indre By). Rewrote both
    market and street-food descriptions to real vendors.

13. **Tivoli Food Hall vendor list** — described as "22 stalls
    including Hallernes, Gorm's pizza and Hooked sushi". Per
    tivoli.dk food hall page, actual count is **15 stalls**;
    Hallernes Smørrebrød and Gorm's are real; Hooked sushi is NOT
    at Tivoli Food Hall (the actual sushi vendor is **Sushi Market**).
    Fixed both vendor count (22 to 15) and the vendor name.

14. **Restaurant Knold og Tot (Roskilde)** — day-trips-food.json
    Roskilde entity prose claimed "traditional smørrebrød at
    Restaurant Knold og Tot". "Knold og Tot" is the Danish title of
    the Katzenjammer Kids comic strip — no restaurant by that name
    exists in Roskilde per RestaurantGuru and TripAdvisor (which list
    Delikatessen Roskilde, Bryggergården, Restaurant Tante Anna,
    Klaptræet). Removed the named phantom; replaced with generic
    "traditional smørrebrød counters in the old town centre".

15. **Café Wilder echoes** — see A2 #2 above (3 echo files fixed).

16. **Sankt Annæ echoes** — see A2 #3 above (1 echo file fixed).

### E4. Verified-block consistency after entity edits

- Updated `verified.address_quoted` to match new entity `address`
  for: Pompette (wine-bars + hidden-gems), Andersen Bakery (was
  Bernstorffsgade 5, now Thorshavnsgade 26), Timm Vladimirs Køkken
  (was Vesterbrogade 27, now Raffinaderivej 10F).
- Updated `verified.source_url` for: Pompette (broken shop.pompette
  → visitcopenhagen), Timm Vladimirs (subpage → root domain),
  Home of Carlsberg (visitcarlsberg.dk now redirects to
  homeofcarlsberg.com — a different registered domain; rebrand, not
  closure; repointed source_url to the VisitCopenhagen listing as
  the stable third-party reference).
- All `checked_on` already 2026-05-20; no rolls needed.

### Source-URL final-host redirect check

- `visitcarlsberg.dk` → 301 → `homeofcarlsberg.com` (different
  registered domain). Not a closure — Carlsberg rebranded the
  Visitor Centre to "Home of Carlsberg" in December 2023. Updated
  entity name from "Carlsberg Visitor Centre" to "Home of
  Carlsberg" and source_url to the stable VisitCopenhagen listing.
- All other entity source_urls sampled (~25) resolve to the same
  registered domain or a canonical www↔apex variant.

### Itinerary geographic-adjacency cross-check

- Day 3 of long-weekend-refshaleoen says "final glass at the
  Mirabelle Spiserìa vineria next door" after Bæst. Confirmed:
  both Bæst and Mirabelle Spiseria share Guldbergsgade 29, 2200
  København N (sister venues in the same building from the Puglisi
  team). "Next door" is accurate.
- Day 2 of weekend-classics references "Coffee Collective on
  Jægersborggade in Nørrebro" after Juno on Århusgade in Østerbro
  — these are ~2km apart and the day prose says "Walk down to" the
  Collective, which is fine framing.
- No fabricated "next door / across the street / around the corner"
  claims found.

### Itinerary day-of-week × hours re-walk

Re-verified all 3 itineraries' venues × day hours after QA1's 4
day-of-week fixes:
- copenhagen-weekend-classics Day 1 (Saturday): all venues open Sat
  (Hart Bageri daily, Schønnemann closed Sun but open Sat, Apollo
  Bar Tue-Sun, Restaurant Pluto daily, Ruby daily). OK.
- copenhagen-weekend-classics Day 2 (Sunday): Juno open Sun 09:00,
  Coffee Collective open Sun, Torvehallerne open Sun 11-17, Hija
  de Sanchez Torvehallerne open Sun 11-17, Restaurant Pluto daily,
  Ruby daily 02:00. OK (QA1's Pluto+Ruby fix holds).
- copenhagen-long-weekend-refshaleoen Day 1 (Friday): all venues
  open Fri (Hart Kødbyen daily, Mad & Kaffe daily, Aamanns daily,
  Sonny weekdays, Mikkeller Bar Viktoriagade daily, WarPigs daily,
  Lidkoeb daily). OK.
- Day 2 (Saturday): Lille Bakery Wed-Sun, Mikkeller Baghaven open
  Sat, Reffen daily (seasonal — March to Sept; itinerary doesn't
  call out winter), Alchemist Wed-Sat dinner. OK.
- Day 3 (Sunday): Beyla weekends, Coffee Collective Godthåbsvej
  daily, Andersen & Maillard Nørrebrogade daily, Pompette daily,
  Bæst (closed Mon-Tue per source, open Sun), Mirabelle vineria
  Tue-Sun. OK (QA1's Pompette+Mirabelle replacement of Ved Stranden
  10 holds).
- copenhagen-budget-day Day 1 (Wednesday): Sankt Peders Mon-Fri,
  Democratic Coffee library hours, DØP Round Tower daily, GRØD
  Torvehallerne Mon-Sat, Slurp daily, Mikkeller Bar daily. OK
  (QA1's Saturday→Wednesday rewrite holds).

### F. Editorial voice
- Voice is consistent and editorial throughout. No purple language,
  egregious AI-tells, or repetitive sentence shapes spotted.

## Defects total: 16 file-level edits + 1 entity removal

- bakeries.json: 1 fix (Andersen Bakery address + chef-name + slug)
- brunch.json: 2 fixes (Beyla Jeson→Jason + Souls reframe; Café
  Wilder 50-year echo)
- cafes.json: 1 fix (Café Wilder 1972→1984)
- casual-dining.json: 2 fixes (Sankt Annæ 1897→1894; Café Wilder
  1972→1984 + 50-year echo)
- coffee-roasters.json: 1 fix (Prolog co-founder surname)
- cooking-classes.json: 1 fix (Timm Vladimirs address + source_url)
- day-trips-food.json: 1 fix (Roskilde Knold og Tot phantom)
- dietary.json: 2 fixes (Beyla Jeson→Jason; Geranium vegetable
  description framing)
- food-tours.json: 1 removal (Copenhagen Food Tours Vesterbro
  route fabrication) + 1 edit (Copenhagen by Mie route/price/
  meeting-point/duration correction)
- hidden-gems.json: 3 fixes (Café Wilder 1972 echo; Sankt Annæ
  1897 echo; Pompette address + why_hidden geography)
- markets.json: 2 fixes (Tivoli Food Hall vendor count + Hooked
  sushi → Sushi Market; Broens Gadekøkken fabricated vendors)
- region.json: 1 fix (food-tours description aligned to 4 entities
  after Vesterbro removal)
- restaurants.json: 2 fixes (Geranium booking 4mo→3mo, more
  honest tip; Alchemist booking tip rewrite removing uncited
  specificities)
- street-food.json: 1 fix (Broens Gadekøkken fabricated vendors)
- wine-bars.json: 1 fix (Pompette address + verified-block)
- breweries.json: 1 fix (Carlsberg Visitor Centre rebranded to
  Home of Carlsberg + source_url updated)
- fine-dining.json: 1 fix (Geranium reservation_lead_time)

## Below-floor topics after QA2

- dietary/kosher: 0 (no Copenhagen kosher ecosystem; not
  backfilled).
- dietary/halal: 2 (both verified).
- dietary/vegetarian: 2 (both verified).
- dietary/gluten-free: 2 (both verified).
- coffee-roasters: 5 (lower bound).
- cooking-classes: 5 (lower bound).
- markets: 5 (lower bound).
- food-tours: 4 (one below the 5 floor after fabricated-route
  removal; do NOT backfill until research finds a real fifth
  operator).
- day-trips-food: 5 (lower bound).
- festivals: 5 (lower bound).
- breweries: 5 (lower bound).

## Verdict

VERDICT: PASS

Total QA2 judgment defects: 16 edits + 1 removal across 15 files.
The pattern that emerged was specific-fact drift the original
research agent could not have caught without operator deep-reads:
wrong founding years (Café Wilder, Sankt Annæ), invented chef names
(Hiroshi Andersen, Sebastian Vinther Olsen, Jeson Renwick),
fabricated vendor lists at street markets (Tivoli Food Hall,
Broens Gadekøkken), real operator + fabricated route (Copenhagen
Food Tours Vesterbro), wrong addresses for active venues (Pompette,
Timm Vladimirs Køkken, Andersen Bakery), and over-specific booking
claims (Geranium "first of month at 13:00", Alchemist DKK 3,800 wine
pairing). One Section B removal was warranted; one Section A2
slug-renaming was the cleanest fix for the closed-then-relocated
Andersen Bakery. Below-floor food-tours at 4 is acceptable per the
"don't fabricate" rule.
