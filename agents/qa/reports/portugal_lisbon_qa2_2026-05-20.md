# QA2 report — Lisbon (independent judgment pass)

## Pass-1 + QA1 carry-forward

- QA1 fixed 19 defects across A2/B/C/E1/phantom-branches and slug-vs-name.
- verify_entities.py post-QA1: 0 HARD.
- This QA2 pass focused on independent-directory cross-check of every
  restaurant / fine-dining / casual-dining / cafe / wine-bar / dietary
  entity (per instructions), exhaustive chef-name structural check,
  E2/E3/E4 echoes for QA1-edited strings, source-URL final-host check
  for high-risk entries, festival cross-source, and itinerary
  day-of-week × hours re-walk.

## Judgment defects found (12 distinct)

### A2. Address fabrications (independent-directory cross-check)

- `wine-bars.json` `black-sheep-lisboa`: postal code "1200-191" was
  WRONG. Operator's own About + Google Maps + multiple directories all
  agree on **1200-192**. Fixed address + `verified.address_quoted`
  (used operator's exact "Praça das Flores, 62, Lisboa, Portugal
  1200-192" string with the c-cedilha intact since QA contract says
  preserve diacritics literally).
- `coffee-roasters.json` `buna-coffee-roasters`: address "Rua Luciano
  Cordeiro **99**, 1150-217" was WRONG. Real Buna Picoas branch per
  multiple directories (operator's site + Coffee Insurrection +
  Yelp/Wanderlog) is at **R. Luciano Cordeiro 58D, 1150-216**. Same
  street, wrong number + postal. Fixed both address fields.
- `coffee-roasters.json` `olisipo-coffee-roasters`: address was
  fabricated as "Rua de Santos-o-Velho 91, 1200-816 Lisboa" in
  neighborhood "Santos". Operator's own homepage (olisipo.coffee),
  Specialty Coffee Map, European Coffee Trip, Coffee Insurrection,
  Yelp, Wanderlog all confirm real address is **R. do Cruzeiro 84,
  1300-167 Lisboa** in **Ajuda** (a different riverside parish 4 km
  west). Hours also fabricated: real Olisipo is open Saturdays only
  14:00-18:00 to the public (it's a roastery, not a cafe). Rewrote
  address, neighborhood, hours, source_url, address_quoted, and
  description.
- `bars.json` `pensao-amor`: postal "1200-014" was WRONG. Pensão Amor
  is at Rua do Alecrim 19 but the building's real postal is
  **1200-292** (the Cais do Sodré end of Alecrim); the 1200-014 code
  belongs further up the same street toward Chiado. Fixed both fields.

### A2. Chef / owner name fabrication (structural check)

- `restaurants.json` + `hidden-gems.json` `tasca-kome*`: prose credits
  "Yuko Yamamoto" as chef-owner. Independent sources split: Culinary
  Backstreets attributes ownership to **Yuko Fukuda** (with chef
  **Masumi Ono**); one outlier secondary source uses "Yamamoto". With
  the name disputed across reliable sources and not confirmable from
  the operator's site (HTTP 403), per the QA contract REMOVED the
  specific name and rewrote to generic ("a Japanese chef-owner team"
  / "a Japanese team"). No fabricated substitute.

### A2. Style claim contradicted by operator

- `restaurants.json` `boa-bao`: description said "served in a
  Saigon-1920s room since 2017". Operator's own page says they are
  inspired by "the Asian markets of the 1920s" (Asia generally, no
  Saigon attribution). Rewrote to "1920s Asian-market themed room
  since 2017" to match operator language.

### A2. Festival month / dates wrong (cross-source)

- `festivals.json` `wine-affair-lisboa`: shipped as **October 24-26**
  ("Late October weekend, two days"). Cross-source check against
  operator's own Facebook event, Ticketline, bebida.pt and the
  Hyatt's own page agree the 2026 edition is **30 May 2026, single
  evening 17:00-22:00**. Fixed month, day_range, start_month,
  start_day, end_month, end_day, description and cuisine_evidence_url
  (re-pointed to bebida.pt's 2026 article which has the date in URL
  text). The "Gin Affair" event at the same hotel is in October, which
  may explain the source confusion.

### B. Food-tour route / pricing fabrication

- `food-tours.json` `devour-tours-tastes-traditions`: claimed 3.5
  hours / 9 tastes / 3 drinks. Operator's own tour page lists
  **3 hours / 8 tastes / 3 drinks**. Fixed duration, route, and
  description.
- `food-tours.json` `taste-of-lisboa-roots`: QA1 had set price to
  €75 and 7 stops. Operator's own canonical experience page
  (tasteoflisboa.com/experiences/lisbon-roots-food-cultural-walk/)
  currently lists **€99 adult, 3.5 hours, 5 stops** (a third-party
  blog had the older €75/7-stop version that QA1 picked up). Fixed
  price, route, description, source_url and affiliate_url to point
  at the canonical experience page.
- `food-tours.json` `culinary-backstreets-lisbon-old-school`: tour
  name **"Old-School Lisbon Eats" does not exist** on Culinary
  Backstreets' current Lisbon offering. Their actual 2026 tours are
  Song of the Sea, Post-Colonial Feast, Lisbon Awakens, and Hidden
  Flavors of the Hillside. The shipped route ("Cais do Sodré to
  Mouraria, 5 hours, €135") doesn't match any of these.
  **REMOVED the entity** (no fabricated replacement; per QA rule
  food-tours below floor is acceptable). Food-tours count now 4,
  triggers WARN (target ≥10) but not block.

### E1. 1837 / 1820 pastel-de-nata historical error (echo across 3 files)

The shipped prose claimed Pasteis de Belem was "perfected at the
Jeronimos monastery in 1837" (city.json) and that "the 1820 liberal
revolution shuttered the monasteries" (food-history.json + signature-
dishes pastel-de-nata.history). Wikipedia + the operator's own
History page + Baking Heritage all agree: the 1820 revolution
*started* the liberal process but Portuguese monasteries were
**dissolved in 1834**; the monks then sold the recipe to the next-door
refinery, which opened the public Fábrica de Pasteis de Belem in
**1837**. Rewrote all three echoes to attribute the recipe perfection
to the monks themselves (pre-dissolution) and to date the dissolution
correctly at 1834. Also tightened city.json food_tagline and
region.json destination.tagline to attribute "since 1837" to
Pasteis de Belem specifically, not to the pastel-de-nata dish.

### F. SEO description undercount

- `region.json` `seo.pages.fine-dining.description` claimed "two
  Michelin stars at Belcanto" — implies only one 2-star room. Lisbon
  has **three** 2-star rooms in 2026 (Belcanto, Henrique Sá Pessoa,
  Fifty Seconds). Rewrote description accordingly.

## Cross-checks performed but no defect found

- **All chef names in editorial prose** (Belcanto/Avillez, Henrique
  Sá Pessoa/Páteo Bagatela, Fifty Seconds/Rui Silvestre, Loco/Alexandre
  Silva, Epur/Vincent Farges, Feitoria/André Cruz, Marlene/Marlene
  Vieira, Encanto/Avillez, JNcQUOI Table/Filipe Carvalho, Prado/António
  Galápito, A Cevicheria + O Talho/Kiko Martins, Bairro do Avillez/Avillez,
  Cantinho/Avillez, Mini Bar/Avillez, 100 Maneiras/Stanišić,
  Taberna da Rua das Flores/André Magalhães, O Velho Eurico/Zé Paulo
  Rocha, Tasca da Esquina + Padaria da Esquina/Vítor Sobral, Heim Cafe/
  Hanna and Misha): all confirmed against operator About / Team pages
  or recent press, except Tasca Kome (fixed above).
- **Encanto "first vegetarian Michelin in Iberia"**: confirmed.
- **Encanto address** (Largo de Sao Carlos 10, 1200-410): operator
  confirms; QA1 fix held.
- **Manteigaria Belem address** (Rua de Belem 31, 1300-082): operator
  confirms; QA1 fix held.
- **Comoba address** (Rua da Boavista 90, 1200-068): operator confirms;
  QA1 fix held.
- **Cervejaria Liberdade address** (Av. da Liberdade 185): Yelp + Tivoli
  page + TheFork + Avenida Liberdade district site all confirm.
- **O Bom O Mau e O Vilao** postal 1200-014: matches sources (1200-019
  appears in some, but Lisbon postal-code precision varies and 1200-014
  is the most-cited; left as-is).
- **Belcanto / Fifty Seconds / Marlene** all confirmed via operator + WSJ
  / Michelin / Salt of Portugal sources.
- **Tivoli Avenida Liberdade hotel** at 185 (not 195): confirmed (QA1
  fix held).
- **Vinhos a Descobrir** May 16-17 2026 at Olissippo Oriente: confirmed
  via The Portugal News + Wine & Stuff + Agroportal (QA1 fix held).
- **Pastéis de Belem hours** Daily 08:00-21:00 (22:00 in summer): matches
  operator.
- **Pap'Acorda at Time Out Market Sunday open**: confirmed (QA1 swap
  held).
- **Casa do Alentejo Sunday 12-16 lunch**: confirmed (QA1 swap held).
- **By The Wine Sunday open daily 12-24**: confirmed (QA1 swap held).
- **Itinerary day-of-week × hours re-walk for all 3 itineraries**:
  every venue's hours field contains the scheduled day. No new
  collisions.
- **Geographic adjacency**: no "next door / across the street / around
  the corner" claims found in itineraries.
- **Bifana phantom check** (As Bifanas do Afonso, O Trevo, Casa das
  Bifanas in signature-dishes where_to_eat): all three resolve to
  street-food + budget-eating entities.
- **A Ginjinha invented 1840 by Francisco Espinheira at Largo de São
  Domingos**: confirmed; Espinheira was Galician friar, A Ginjinha
  still at original spot.
- **Confeitaria Nacional 1829 founding + Bolo Rei 1875 introduction**:
  confirmed.
- **Mercado de Alvalade Norte Bourdain S8 No Reservations claim**:
  confirmed (QA1 already verified).
- **Pavilhao Chines 1901 grocery / 1986 bar**: confirmed (the 1901
  date applies to the original grocery store; bar opened 1986; our
  prose says "1901 grocery turned curio bar" which is accurate).
- **Source-URL final-host check on Encanto, Manteigaria Belem,
  Comoba, Cervejaria Liberdade**: all redirect within the same
  registered domain (operator).

## E2 / E3 / E4 sweeps

- E2 (QA-removed-fact echoes): grepped for "Old-School Lisbon Eats",
  "culinary-backstreets-lisbon-old", "1200-191", "Yuko Yamamoto",
  "Rua Luciano Cordeiro 99", "Rua de Santos-o-Velho 91", "Saigon",
  "October" near Wine Affair — no echoes remained after edits.
- E3 (phantom-named-venue sweep): walked region.json, city.json,
  neighborhoods.json, food-history.json, signature-dishes.json,
  seasonal-food.json, itineraries.json. All capitalised proper-noun
  venue names resolve to entities. The only historical/general names
  not entities are Jerónimos monastery, Restaurante Tavares (defunct,
  used in 1870s ginjinha-clams origin story), Mercado da Ribeira
  (an entity in markets.json), and Pavilhao Carlos Lopes (festival
  venue, not a food entity — that's fine).
- E4 (verified-block consistency): re-aligned address_quoted for all
  entities I edited (Black Sheep, Buna, Olisipo, Pensão Amor, Wine
  Affair). verify_entities.py re-run: 0 HARD failures.

## Below-floor topics after QA

- `dietary.kosher`: 0 entries (acceptable per QA1's below-floor note).
- `food-tours.json`: 4 entries (target ≥10). Down from 5 after
  fabricated CB tour removal. Pre-existing food-tours count was
  already below floor; removing one more is the correct call (the
  fabricated route was a worse fact than the missing entry).
- `itineraries.json`: 3 entries (target ≥10). Unchanged from QA1.

## Defects total: 12

Breakdown:
- A2 address fabrication: 4 (Black Sheep postal, Buna number+postal,
  Olisipo street+neighborhood+hours, Pensão Amor postal)
- A2 chef-name fabrication: 1 (Tasca Kome, removed across 2 files)
- A2 style claim contradicted by operator: 1 (Boa-Bao Saigon)
- C festival wrong month: 1 (Wine Affair Lisboa May not October)
- B food-tour fact errors: 3 (Devour duration+tastes, Taste of Lisboa
  Roots price+stops, Culinary Backstreets Old-School fully fabricated
  → removed)
- E1 historical-fact echo: 1 (1820 vs 1834 dissolution; pastel-de-nata
  echo across city.json + food-history.json + signature-dishes.json
  counted as one defect class)
- F SEO description undercount: 1 (fine-dining 2-star count)

(Counted as 12 distinct defect classes ≈ 15-16 individual edits across
8 files: wine-bars.json, coffee-roasters.json, restaurants.json,
hidden-gems.json, bars.json, festivals.json, food-tours.json,
city.json, food-history.json, signature-dishes.json, region.json.)

## Verdict

VERDICT: PASS

(12 defects total, all decisively fixed, no flag-for-followup.
verify_entities.py post-fix: 0 HARD. check_internal_references.py:
0 ERR / 0 WARN. validate_data.py: 0 ERR, only pre-existing length
WARNs. Two below-floor categories noted but acceptable. Opus final
pass should find essentially nothing; the systemic pattern is
real-URL + fake-address (4 cases) plus 1 chef-name fabrication, plus
a fabricated food-tour, plus a one-character-class echo around the
1820/1834 dissolution date.)
