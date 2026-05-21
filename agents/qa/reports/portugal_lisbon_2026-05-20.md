# QA report — Lisbon (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (post-edit re-run also 0)
- verify_entities.py warnings: 10 (pre-existing: own_site_only for Hello Kristof, Lisbon Cooking Academy, off-path Portugal day-trips; dead `oct.co` open_evidence URL on three brewery entities)
- check_internal_references.py: ERR=0, WARN=0 (131 names, 151 slugs)
- check_external_urls.py: 43/43 alive
- check_festival_dates.py: 3/5 OK, 2 fetch-fail (anti-bot), 0 month mismatches

## Judgment defects found

### A2. Specific-fact match (chef/owner/address/menu/hours)

- `fine-dining.json` `encanto`: chef listed as "Joao Diogo Formiga" (executive chef name garbled with extra first name). Michelin Guide credits Encanto to **Jose Avillez** (Diogo Formiga is the executive chef under Avillez). Rewrote `chef` to "Jose Avillez" to match Michelin headline credit and the description's own attribution. Also re-pointed source_url to Avillez's own page.
- `fine-dining.json` `encanto` + `dietary.json` vegetarian `encanto`: address claimed "Largo do Duque do Cadaval 17, 1200-160 Lisboa" — **WRONG**. Verified via joseavillez.pt official site: real address is **Largo de Sao Carlos 10, 1200-410 Lisboa** (across from the Sao Carlos opera house in Chiado). Updated address + address_quoted in both files; re-pointed source_url to operator's official page.
- `bakeries.json` `manteigaria-belem`: address "Calcada da Ajuda 12, 1300-018 Lisboa" — **WRONG**. Verified via manteigaria.com: real Belem branches are at **Rua de Belem 31** (2022) and Rua de Belem 100 (2025). Updated to Rua de Belem 31, 1300-082 Lisboa. Also fixed hours from "09:00-22:00" to operator's stated "08:00-21:00".
- `cafes.json` + `brunch.json` + `dietary.json` (gluten_free) `comoba`/`comoba-brunch`/`comoba-gluten-free`: address "Rua do Poco dos Negros 1, 1200-336 Lisboa" — **WRONG** (that's The Mill cafe's address, which also exists in coffee-roasters.json under slug `the-mill`). Verified via comoba-lisboa.com official contact page: real address is **Rua da Boavista 90, 1200-068 Lisboa**. Updated address + address_quoted + source_url across all three files. Also fixed neighborhood from "bairro-alto" to "cais-do-sodre" (Rua da Boavista sits between Cais do Sodre and Bica). Hours updated to operator's "08:30-17:00".
- `casual-dining.json` `cervejaria-liberdade`: address "Avenida da Liberdade 195, 1269-050" — **WRONG**. Tivoli Avenida Liberdade hotel (which houses the restaurant) is at Av. da Liberdade **185**. Fixed.
- `wine-bars.json` `black-sheep-lisboa`: description named "Brian Patterson's natural-wine bar" — **fabricated owner name** (chef/owner fabrication defect class). Real owners per blacksheeplisboa.com are Bruna Ventura and Lucas Ferreira, a Brazilian couple. Rewrote to "a natural-wine bar from a Brazilian husband-and-wife team" (generic-but-true). Also corrected hours from "Tue-Sat 17:00-24:00" to operator's actual "Tue-Sat 19:00-23:30".
- `signature-dishes.json` `pastel-de-nata`: `typical_price` was `"€1.50 to €1.40"` — backwards range, low > high. Fixed to "€1.20 to €1.50" (matches Manteigaria 1.50 standard and entry-level kiosks at 1.20).
- `day-trips-food.json` `sintra`: claim "travesseiros, the puff pastry... invented at Casa Piriquita in 1862" — **WRONG**. Casa Piriquita was *founded* 1862 by Amaro dos Santos, but travesseiros were created in the **1940s** by Constancia Luisa Cunha (founder's daughter). Rewrote to acknowledge founding year vs. travesseiro development decade.

### A2. Day-of-week × venue-hours conflicts in itineraries

- `itineraries.json` itin 1 day 2 (Sunday): lunch at `o-velho-eurico` — **O Velho Eurico is closed Sundays and Mondays** (verified via four sources). Swapped to Casa do Alentejo in Restauradores (open Sunday 12-16:00); rewrote prose to feature acorda alentejana + carne de porco a alentejana; updated venues slug list.
- `itineraries.json` itin 2 day 3 (Sunday): lunch at `ze-dos-cornos` — **Ze dos Cornos is closed Sundays**. First swap to Solar dos Presuntos also failed (Solar is also closed Sundays). Final swap: **Pap'Acorda at Time Out Market** (open Sundays 12-24:00); rewrote prose to feature acorda de marisco.
- `itineraries.json` itin 3 day 2 (Sunday): late drinks at `black-sheep-lisboa` — **Black Sheep Lisboa is closed Sundays and Mondays** (operator confirms Tue-Sat only). Swapped to By The Wine on Rua das Flores (open daily 12-24:00); rewrote prose.
- `itineraries.json` itin 2 day 1 + itin 3 day 1 prose: "Comoba in Bairro Alto" — geographic-drift defect; Comoba is on Rua da Boavista in Cais do Sodre, not Bairro Alto. Rewrote both occurrences to "Comoba in Cais do Sodre".

### B. Route / itinerary mismatches (food-tours operator-vs-JSON)

- `food-tours.json` `devour-tours-tastes-traditions`: JSON claimed "Bairro Alto and Chiado" + meeting "Largo Trindade Coelho". Operator page lists route as **Baixa, Chiado, and Cais do Sodre** with meeting at **Praca da Figueira** by the King Joao I statue. Fixed route, meeting_point, neighborhood, and description; address_quoted updated.
- `food-tours.json` `eating-europe-undiscovered-lisbon`: JSON claimed "Mouraria and Alfama" + "4 hours" + "ten tastes" + meeting "Martim Moniz" + price €95. Operator page lists route as **Baixa and Mouraria** (no Alfama), **3.5 hours**, **5 stops**, meeting at **Praca dos Restauradores**, price from **€59**. Fixed all five fields.
- `food-tours.json` `taste-of-lisboa-roots`: JSON claimed meeting "Largo do Intendente" + price €85. Operator/booking pages list meeting at **Largo de Sao Domingos** (by the Star of David sculpture) + price **€75**. Fixed meeting_point and price; description tightened to "seven tasting stops" per operator.

### C. Festival corrections

- `festivals.json` `vinhos-a-descobrir`: venue "Hotel Tivoli Avenida Liberdade, 1269-050 Lisboa" — **WRONG**. 2026 edition (per The Portugal News article that's the source_url) is at **Olissippo Oriente Hotel in Parque das Nacoes**, May 16-17. Fixed address, address_quoted, neighborhood.
- `festivals.json` `wine-affair-lisboa`: venue address "Hyatt Regency Lisboa, Rua Joaquim Antonio de Aguiar 6, 1099-080" — **WRONG**. Hyatt Regency Lisboa is at **Rua da Junqueira 65, 1300-343 Lisboa** in Belem. Fixed address and address_quoted; neighborhood lowercased to "belem" to match neighborhood slug.

### D. Thin-category check

- `dietary.kosher`: empty (correctly flagged below-floor by research agent). Left at 0; did not invent. Note in below-floor section.
- `dietary.halal`: 2 entries (Taste of Pakistan, Taste of Lahore) — both content-checked already by `check_evidence_content.py` per ship_safety. Confirmed both real venues on Rua do Benformoso (Mouraria's Little Bangladesh). No fabrication.
- `dietary.gluten_free`: 2 entries (Comoba, Fauna and Flora) — Comoba address fixed above; both confirmed real venues serving gluten-free.
- `dietary.vegan`: 3 entries (Ao 26, The Food Temple, Fauna and Flora Anjos) — confirmed real.
- `dietary.vegetarian`: 2 entries (Encanto, The Food Temple) — Encanto address fixed above.

### Fabricated entities removed (closed-venue / phantom-branch)

- `casual-dining.json` `pap-acorda-misericordia` at "Rua da Misericordia 14, 1200-273 Lisboa" — **REMOVED**. Pap'Acorda has only ONE current location (Mercado da Ribeira / Time Out Market since 2016 move from old Bairro Alto room which closed). No Misericordia branch exists; entity was a phantom duplicate.
- `late-night.json` `pap-acorda-late` at "Rua da Misericordia 14" — **REMOVED** for same reason (same phantom address, different entity).
- `street-food.json` `queijadas-sapa` at "Rua Garrett 41, 1200-203 Lisboa" — **REMOVED**. Queijadas da Sapa is at 12 Volta do Duche in Sintra (verified via Uber Eats listing). No Lisbon branch exists; fabricated.
- `casual-dining.json` slug-vs-name mismatch: slug `atira-te-ao-rio-cacilhas` carried name "Pateo Bairro do Avillez" (Cacilhas-suggestive slug pointing at Chiado entity). Renamed slug to `pateo-bairro-do-avillez` to match the entity. No other files referenced the old slug.

### E1. Closed-venue echoes

- `food-history.json` 2010s era summary said "Henrique Sa Pessoa at Alma" — **Alma closed end-2025** (Sa Pessoa moved his 2-star to a new room at Pateo Bagatela in February 2026). Also "with two-star rooms anchoring Chiado" — only Belcanto is in Chiado now; Henrique Sa Pessoa is in Sao Sebastiao/Amoreiras and Fifty Seconds in Parque das Nacoes. Rewrote both clauses to drop "at Alma" and to describe the three 2-star rooms by their actual neighborhoods.

### E2. QA-removed-fact echoes

Walked itineraries, signature-dishes, food-history, and per-entity descriptions for any prose still referencing removed venues (pap-acorda-misericordia, queijadas-sapa) — no echoes found. The signature-dishes `acorda` where_to_eat list does include "Pateo Bairro do Avillez" which now resolves cleanly to the renamed `pateo-bairro-do-avillez` slug in casual-dining.json.

### E3. Phantom-named-venue sweep

Walked region.json, city.json, neighborhoods.json, food-history.json, signature-dishes.json, seasonal-food.json, itineraries.json prose for capitalised proper-noun venue mentions that don't resolve to an entity:

- All venues named in `food-history.json` (Belcanto, Tasca da Esquina, Loco, Pasteis de Belem, Confeitaria Nacional) resolve to entities or are correctly historical (Jeronimos monastery).
- All venues named in `signature-dishes.json` where_to_eat lists pass `check_internal_references` (Pateo Bairro do Avillez now resolves after slug rename).
- All venues named in `neighborhoods.json` vibes (Belcanto, Bairro do Avillez, Manteigaria, Pasteis de Belem, Feitoria, Time Out Market, A Cevicheria, Dois Corvos, Musa) resolve.
- `city.json` food_culture_summary names Avillez (Belcanto), Sa Pessoa (now own restaurant — fine), Antonio Galapito (Prado), Alexandre Silva (Loco), Manteigaria, Pasteis de Belem — all resolve.
- `seasonal-food.json` names Confeitaria Nacional (resolves).
- `itineraries.json` after my rewrites: every venue named in prose now resolves to entity via slug.

No phantom-named-venue defects found.

### E4. Verified-block consistency after meeting-point/address edits

- After updating Vinhos a Descobrir address → updated `verified.address_quoted` to match new entity address.
- After updating Eating Europe meeting_point → updated `verified.address_quoted` to match (also re-aligned wording).
- After updating Comoba address (three files) → updated `verified.address_quoted` to match new "rua da boavista 90, 1200-068 lisboa, portugal".
- After updating Encanto address (two files) → updated `verified.address_quoted` to match new "Largo de Sao Carlos, 10, 1200-410 Lisboa".
- After updating Manteigaria Belem address → updated `verified.address_quoted`.
- After updating Wine Affair Lisboa address → updated `verified.address_quoted`.
- Re-ran verify_entities.py after fixes: 0 HARD failures.

### F. Editorial voice / length caps

No new egregious AI-tells. validate_data.py emits the usual length WARNs (description 134-139 chars on a handful of entities just under the 140 floor; signature-dishes history fields 240-293 chars just under the 300 floor); these are pre-existing soft warnings the research agent backfills, not blockers.

## Cross-checks performed but no defect found

- Pasteis de Belem address "Rua de Belem 84-92" — confirmed via operator (Lewis prompt also noted).
- Casa Portuguesa do Pastel de Bacalhau address Rua Augusta 106 — confirmed (operator + Yelp).
- Cafe A Brasileira at Rua Garrett 120 — confirmed (multiple sources, founded 1905).
- Confeitaria Nacional founded 1829 + Bolo Rei introduced 1875 — confirmed via operator.
- Cervejaria Trindade as 1836 beer hall in former convent — confirmed.
- Cervejaria Ramiro hours/address — confirmed (Av. Almirante Reis 1-H, closed Mondays, Saturday lunch fine).
- Belcanto Saturday evening — confirmed open Tue-Sat 19:00-22:00.
- Loco Friday evening — confirmed open Tue-Sat 19:00-23:00, Alexandre Silva confirmed chef.
- Pap'Acorda Sunday lunch — confirmed open Sundays at Time Out Market (replaced Solar dos Presuntos which is also closed Sundays).
- Time Out Market hours/address — confirmed (Av. 24 Julho 49, 1200-479; open daily 10:00).
- Mercado de Alvalade Norte Bourdain claim — confirmed (No Reservations S8 ep with Henrique Sa Pessoa).
- Encanto Sunday closure — itinerary 3 day 1 (Saturday) Encanto dinner stays in-window.
- The Food Temple "candlelit room from 2013" — confirmed operator says "opened 13 years ago" (~2013).
- 2026 Michelin claims: Belcanto 2, Henrique Sa Pessoa 2, Fifty Seconds 2 (new 2026), Loco 1, Epur 1, Feitoria 1, Marlene 1, Encanto 1, JNcQUOI Table 1 (Opening of the Year), Eleven 0 (lost star) — all confirmed via Michelin Portugal 2026 announcement + Portugal Confidential coverage.
- Pasteis de Belem 1834 monastery closure (post-1820 liberal revolution) — historically defensible, prose retained.

## Defects total: 19

Breakdown:
- A2 specific-fact match: 8 (Encanto chef, Encanto address x2, Manteigaria Belem address, Comoba address x3, Cervejaria Liberdade address, Black Sheep owner, Pastel de nata price, Sintra travesseiro history)
- A2 day-of-week × venue-hours: 3 itinerary swaps (Velho Eurico Sun, Ze dos Cornos Sun, Black Sheep Sun)
- A2 geographic-drift prose: 1 ("Comoba in Bairro Alto" x2 = 1 defect class)
- B route / itinerary operator-mismatch: 3 (Devour, Eating Europe, Taste of Lisboa Roots)
- C festival venue corrections: 2 (Vinhos a Descobrir, Wine Affair)
- Fabricated/phantom-branch entities removed: 3 (pap-acorda-misericordia, pap-acorda-late, queijadas-sapa)
- Slug-vs-name mismatch repair: 1 (atira-te-ao-rio-cacilhas → pateo-bairro-do-avillez)
- E1 closed-venue prose echo: 1 (food-history "Alma" + "two-star rooms anchoring Chiado")

(Counted as ~22 individual edits across 19 distinct defect classes.)

## Below-floor topics after QA

- `dietary.kosher`: 0 entries (floor 2). Research agent should backfill or the topic accepts below-floor — Lisbon has no clearly kosher-certified standalone Portuguese restaurant; closest is the small Beit HaShoel synagogue community kitchen which is private. Acceptable to ship below floor.
- `itineraries.json`: 3 entries (validate_data.py target >=10 for SEO). Pre-existing; not a fabrication risk to backfill aggressively.

## Verdict

VERDICT: PASS

(19 defects total; all decisively fixed, no flag-for-followup. ship_safety re-runs clean: verify_entities 0 HARD, check_internal_references 0 ERR, check_external_urls 43/43 alive, check_festival_dates 0 month mismatches. Below-floor kosher topic noted for research-agent backfill if Lisbon kosher floor relaxes, otherwise ship as-is.)
