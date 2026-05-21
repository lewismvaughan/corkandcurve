# Opus final QA report — Lisbon

## Reading-in

- QA1 fixed 19 defects (address fabrications, chef-name fabrications,
  itinerary day-of-week swaps, food-tour route mismatches, festival
  venue corrections, phantom-branch removals, slug-vs-name repairs,
  Alma closed-venue echo).
- QA2 fixed 12 more (4 address fabrications, 1 chef-name removal,
  1 Saigon style-claim, 1 festival wrong month, 3 food-tour fact
  errors, 1 historical-date echo across 3 files, 1 SEO undercount).
- Expectation per brief: zero defects. Anything found = upstream prompt
  regression.

## Narrow checks executed

1. 1820 → 1834 sweep across data tree. Only surviving "1820" is the
   historically correct framing in food-history.json line 14
   ("1834 dissolution of religious orders that followed the 1820
   liberal revolution"). Accept.
2. Itinerary day-of-week × hours re-walk. All venues verified open on
   their scheduled day via independent operator / Time Out / Yelp
   sources: Pasteis de Belem Sat, Ramiro Sat lunch, Belcanto Sat 20:30,
   Manteigaria Chiado Sun morning, Casa do Alentejo Sun lunch, Sol e
   Pesca Sun, O Bom O Mau e O Vilao Sun, Comoba Fri/Sat morning,
   A Cevicheria Fri lunch, Loco Fri evening, Time Out Market Sat
   morning, Manteigaria Mercado Sat, Prado Sat lunch, Taberna Rua das
   Flores Sat evening, Cafe A Brasileira Sun, Pap'Acorda Sun lunch,
   Dois Corvos Sun afternoon, Musa Sun afternoon, Pinoquio Sun evening,
   Ao 26 Sat lunch, Encanto Sat evening, Fauna and Flora Sun morning,
   The Food Temple Sun evening, By The Wine Sun late.
3. Geographic adjacency claims (next door / across the street / around
   the corner / short walk). 5 hits, all verified accurate or
   historically correct: Manteigaria Belem to Pasteis de Belem (same
   street, ~50m), Jeronimos refinery (historical "next door"),
   Cafe de Sao Bento next to Assembleia da Republica (confirmed),
   Pasteis de Belem to Jeronimos monastery (~200m, "next door"
   defensible), Time Out Market "next door" to original market (same
   building, defensible).
4. Sibling-credit borrowing: none found. Each Michelin-star claim,
   Green Star, James Beard, Bourdain credit matches the specific
   entity it's attached to.
5. Multi-generational / deceased-chef / sold-business drift: none.
   Chef Sá Pessoa correctly attributed to new eponymous restaurant
   after Alma close (QA1 fix held). Avillez at Belcanto + Encanto
   confirmed current.
6. E4 verified-block consistency for all QA1+QA2 edited entities:
   re-checked address_quoted against current address for Encanto x2,
   Manteigaria Belem, Comoba x3, Cervejaria Liberdade, Black Sheep,
   Wine Affair, Vinhos a Descobrir, Buna, Olisipo, Pensão Amor,
   Tasca Kome x2, Boa-Bao, Devour, Eating Europe, Taste of Lisboa
   Roots. All consistent. checked_on = 2026-05-20 across all
   edited entities.
7. Cross-source festival dates: Wine Affair Lisboa May 30 2026 confirmed
   via bebida.pt non-organiser article (17:00-22:00, Hyatt Regency
   courtyard). Peixe em Lisboa April 4-14 confirmed via oturismo.pt
   and portaldeportugal.com. Vinhos a Descobrir May 16-17 confirmed
   via The Portugal News, Wine & Stuff, Agroportal.
8. Phantom-named-venue sweep across region.json, city.json,
   neighborhoods.json, food-history.json, signature-dishes.json,
   seasonal-food.json, itineraries.json: 1 phantom found
   ("Lisbon Wine Week" in region.json SEO description — no such
   festival exists in Lisbon). All other named venues
   (Belcanto, Bairro do Avillez, Manteigaria, Pasteis de Belem,
   Feitoria, Time Out Market, A Cevicheria, Dois Corvos, Musa, Lince,
   Cervejaria Trindade, Mercado da Ribeira, Cantinho do Aziz,
   Pavilhao Carlos Lopes, Olissippo Oriente, Hyatt Regency,
   Santos Populares, Peixe em Lisboa, Vinhos a Descobrir, Wine Affair
   Lisboa, Lisbon Coffee Fest, Restaurante Tavares historical, Jeronimos
   historical, Casa Piriquita, all chef names) resolve.
9. Olisipo Coffee Roasters re-verification: address Rua do Cruzeiro 84
   1300-167 Ajuda confirmed via operator's own homepage path and
   Sprudge feature; hours "Sat 14:00-18:00" confirmed via Coffee
   Insurrection ("opens on the weekend"). description's
   "Sofia and Anthony" found: real founders are Antony Watson + Sofia
   Gonçalves (per Sprudge / specialtycoffeemap / operator About
   page). Spelling correction below.

## Judgment defects found (8 distinct)

### A2. Specific-fact match (chef/owner/dish/hours)

- `coffee-roasters.json` `olisipo-coffee-roasters`: description spelled
  founder "Anthony" (operator spells "Antony"). Fixed to "Antony and
  Sofia". Order also reversed to match operator's narrative.
- `restaurants.json` `a-cevicheria` reference in `itineraries.json` itin
  2 day 1 afternoon: prose claimed visitors should order "ceviche puro
  and the codfish ceviche portugues". Operator's CURRENT menu at
  acevicheria.pt/menu-restaurante-lisboa lists only Corvina+Batata
  Doce, Salmão+Pitaia, Lavagante+Choclo, Atum+Beterraba, Camarão. The
  ceviche puro and Ceviche Português appear in 2024 press writeups but
  not on the current menu. Rewrote itinerary prose to operator's
  current ceviches; left entity signature_dishes intact since press
  source backs them.
- `fine-dining.json` `loco`: tasting_menu_price was €145; operator's
  menu-beverage page lists LOCO Menu at €160 and Experience Menu (with
  pairing) at €250. Updated price range. Confirmed "16 courses" via
  operator (had been called into question by one out-of-date third-
  party source).
- `fine-dining.json` `henrique-sa-pessoa`: neighborhood was
  "Sao Sebastiao". Páteo Bagatela (Rua da Artilharia 1) is actually in
  Rato/São Mamede per multiple property and city sources. Fixed
  neighborhood to "Rato".
- `food-history.json` key-era 1986-today summary: said "three two-star
  rooms across Chiado, Sao Sebastiao and Parque das Nacoes". Per the
  fix above, Sá Pessoa is in Rato, not Sao Sebastiao. Updated to
  "Chiado, Rato and Parque das Nacoes".
- `street-food.json` `o-trevo`: hours "Daily 08:00-23:00" and
  cash_only=false were both wrong. Operator and Time Out confirm
  Mon-Sat 07:00-21:00, closed Sunday, cash only. Fixed both fields.
- `street-food.json` `as-bifanas-do-afonso`: hours "Mon-Sat 06:30-24:00"
  and cash_only=false were both wrong. Yelp / Atlas Obscura / multiple
  sources confirm Mon-Fri 07:30-19:30, Sat 09:00-14:00, closed Sunday,
  cash only. Fixed both fields.
- `wine-bars.json` `black-sheep-lisboa`: description said "Brazilian
  husband-and-wife team". Operator's About page and Culinary
  Backstreets profile confirm they are "two Brazilian wine geeks" /
  "Brazilian couple" but do NOT confirm marital status. Per QA contract
  ("don't substitute a different invented fact, generalize"), rewrote
  to "Brazilian wine-geek duo".

### Phantom-named-venue / SEO accuracy

- `region.json` `seo.pages.festivals.description`: named "Lisbon Wine
  Week" as one of three flagship festivals. No festival by that name
  exists in Lisbon (verified via WebSearch + bebida.pt + vinhosabeber
  + The Portugal News). Replaced with Vinhos a Descobrir in May.
- `region.json` `seo.pages.dietary.description`: claimed "vegan,
  vegetarian, halal and kosher picks". Lisbon dietary.kosher is
  empty (acceptable below-floor per QA1+QA2). Removing the kosher
  claim from the SEO description so users searching kosher don't
  land on a page with zero kosher entries. Rewrote to "vegan, vegetarian,
  halal counters and gluten-free picks" (all three of which DO have
  entries).

## Cross-checks performed but no defect found

- All chef names in fine-dining + bars + restaurants editorial prose
  reconfirmed (Avillez, Sá Pessoa, Silvestre, Silva, Farges, Cruz,
  Vieira, Carvalho, Galápito, Kiko Martins, Brian Patterson removed
  in QA1, Tasca Kome name removed in QA2).
- Wine Affair Lisboa May 30 2026 cross-source confirmed via bebida.pt.
- Peixe em Lisboa April 4-14 2026 cross-source confirmed.
- Vinhos a Descobrir May 16-17 2026 cross-source confirmed.
- Itinerary day-of-week × hours: 23 venues across 3 itineraries,
  zero collisions after this walkthrough.
- Adjacency claims: 5 hits, all geometrically and historically valid.
- Pap'Acorda Sunday open at Time Out Market: re-confirmed.
- Encanto Saturday open (Sunday closed): confirmed in itinerary 3 day 1.
- Mouraria "Bangladeshi, Chinese, Indian, Mozambican" five-minute
  cluster claim: confirmed via Time Out Mouraria + Cantinho do Aziz
  35-year history.
- Pasteis de Belem Rua de Belem 84-92, hours Daily 08:00-21:00, 22:00
  summer: matches operator.
- Casa das Bifanas Praca Dom Joao da Camara, Mon-Sat 11:30-22:00 closed
  Sunday: matches multiple sources.
- Hyatt Regency Lisbon at Rua da Junqueira 65 1300-343 Belém:
  matches official Hyatt site.
- Lince Brewery founders ex-Vodafone + Iberian lynx fund: confirmed via
  visitmylisbon and PortugalConfidential.
- 2026 Michelin star count for Lisbon (Belcanto 2, Sá Pessoa 2,
  Fifty Seconds 2, Loco 1, Epur 1, Feitoria 1, Marlene 1, Encanto 1,
  JNcQUOI Table 1, Eleven 0): held per QA1+QA2.
- 1834 monastery dissolution / 1837 Pasteis de Belem opening / monks
  perfected pre-dissolution recipe (city.json, food-history.json,
  signature-dishes.json, region.json): all consistent.

## E2 / E3 / E4 sweeps

- E2 (removed-fact echoes): grepped for "1820", "Lisbon Wine Week",
  "kosher" in SEO descriptions, "Anthony" in Olisipo, "Daily
  08:00-23:00" near O Trevo, "Sao Sebastiao" near Sá Pessoa, "ceviche
  puro" — no echoes survive after my edits.
- E3 (phantom venue sweep): walked region/city/neighborhoods/food-
  history/signature-dishes/seasonal-food/itineraries. Only phantom
  was "Lisbon Wine Week" in region.json SEO descriptions (fixed).
- E4 (verified-block consistency): re-verified address_quoted matches
  current address for all QA1+QA2+Opus-edited entities.
  verify_entities.py re-run after my edits: 0 HARD failures, 10
  pre-existing WARNs (own_site_only + dead oct.co URLs).

## Below-floor topics after QA

- `dietary.kosher`: 0 entries (no kosher-certified standalone restaurant
  in Lisbon; acceptable per QA1+QA2). SEO description now rewritten so
  it no longer advertises kosher.
- `food-tours.json`: 4 entries (target ≥10). Pre-existing after QA2
  removed fabricated CB tour.
- `itineraries.json`: 3 entries (target ≥10). Pre-existing.

## Defects total: 8

Breakdown:
- A2 spelling correction (Olisipo "Anthony" → "Antony"): 1
- A2 itinerary dish-list drift (A Cevicheria current menu): 1
- A2 fine-dining price update (Loco): 1
- A2 neighborhood correction (Henrique Sá Pessoa from Sao Sebastiao
  to Rato): 1, plus its echo in food-history.json key-era summary: 1
- A2 wrong hours + cash_only (O Trevo + As Bifanas do Afonso): 2
- A2 over-claimed owner relationship (Black Sheep husband-and-wife):
  1
- A2 verified-block source URL pointing at wrong venue (O Bom O Mau e
  O Vilão source_url was lifecooler "boa-bao-lisboa" page): 1
  (Repointed source_url to operator's own site, open_evidence_url to
  Time Out's listing.)
- E3 phantom in SEO description (Lisbon Wine Week): 1
- E3/SEO accuracy (kosher in dietary SEO description with 0 kosher
  entries): 1

(Counted as ~10 individual edits across 7 files.)

## Upstream prompt regression notes

- **Research agent**: Olisipo founder name spelled inconsistently
  (Anthony vs Antony). The operator's About page is the ground truth
  — research agent should always check the operator's own About page
  for chef/founder names before lifting from Sprudge / Coffee
  Insurrection / press where spelling can drift.
- **Research agent**: hours and cash_only fields for street-food
  entities (O Trevo, As Bifanas do Afonso) were both wrong on initial
  capture. Suggests the agent isn't pulling from a primary source for
  these two binary-but-checkable fields.
- **Research agent**: O Bom O Mau e O Vilão's source_url was a
  lifecooler URL about Boa-Bao (an entirely different venue). The URL
  appears to have been copy-pasted from the next entity in the same
  prompt batch. Spot-check during research to ensure source_url is
  about the entity being written.
- **Research agent**: chef relationship over-claims ("husband-and-wife"
  when sources only say "couple" or "duo") repeat the pattern Lewis
  flagged in earlier cities. Default to "duo" / "couple" / "team" when
  marital status isn't directly confirmed.
- **QA1**: neighborhood assignment for Henrique Sá Pessoa was based on
  reading press summaries that said "São Sebastião / Amoreiras area".
  Páteo Bagatela is actually in Rato/São Mamede (per Lisbon parish
  data). QA1 should always cross-check neighborhood with a Lisbon
  city-services site (jfsantoantonio.pt / informacoeseservicos.lisboa.pt)
  rather than press paraphrase.
- **QA2**: missed the same neighborhood error since it was paraphrasing
  QA1's "Sao Sebastiao/Amoreiras" note rather than re-deriving from
  the address.
- **QA1+QA2**: missed the cevicheria dish-list drift because
  Portugal Confidential (cuisine_evidence_url) confirms ceviche puro
  and ceviche português, but operator's current menu doesn't. Need a
  rule: itinerary prose dishes must appear on the operator's CURRENT
  menu, not on an older press article.

## Verdict

VERDICT: PASS

(8 defects total. All decisively fixed, no flag-for-followup.
verify_entities.py post-fix: 0 HARD failures (10 pre-existing WARNs).
check_internal_references.py: 0 ERR, 0 WARN. validate_data.py: 0 ERR,
only pre-existing length WARNs. check_festival_dates.py: 3/5 OK, 2
anti-bot fetch-fails, 0 month mismatches. Below-floor kosher and
food-tours and itineraries noted but acceptable. Defects skew
"research-stage soft hours/cash claims + one neighborhood mistake +
two SEO phantom references" — not a structural pattern, but enough to
demonstrate QA2 was not exhaustive on hours/cash fields and on
neighborhood derivation. Recommend tightening QA1 prompt to mandate
neighborhood derived from Lisbon parish/city services rather than
press paraphrase, and tightening research prompt on copy-paste
source_url discipline.)
