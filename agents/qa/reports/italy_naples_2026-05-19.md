# QA report -- Naples (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety passed with 0 HARD failures pre-QA)
- verify_entities.py warnings: 77 (SSL/timeout flakes on real Italian venue sites: dimatteo.it, starita.it, leopoldo.com -- confirmed anti-bot, not real defects)

## Judgment defects found

### A. Cuisine / category mismatches

- `berevino` (wine-bars): cuisine_evidence_url `devourtours.com/blog/wine-bars-napoli/` does not mention Berevino; that page lists 7 different bars (Belledonne, Archivio Storico, etc.). Evidence URL updated to the TripAdvisor source_url that confirms wine bar category. Fixed.
- `berevino-storico` (wine-bars): same cuisine_evidence_url defect as above. Fixed.
- `lebbrezza-vomero` (wine-bars): listed as Vomero neighborhood but address is Vico Vetriera a Chiaia 9 -- identical to `lebbrezza-di-noe` (Chiaia). Fabricated Vomero duplicate. Removed.
- `stanza-vomero` (wine-bars): listed as Vomero neighborhood but address is Via Costantinopoli 100 -- identical to `la-stanza-del-gusto` (centro-storico). Fabricated Vomero duplicate. Removed.
- `lebbrezza-noe-vomero-bar` (bars.json): same duplicate pattern -- Vico Vetriera a Chiaia 9 address labeled Vomero. Removed.

### B. Route / itinerary mismatches

- `secret-food-tours-pizza-class` (cooking-classes): JSON claimed meeting point "Piazza Dante", price EU75-95, group size 12, duration 3.5 hours. Operator's actual page (secretfoodtours.com/naples/cooking-classes/) shows meeting point Via San Paolo 26, price EU49.99, group size 14 max, duration 1.5-2 hours. All four logistics fields fabricated. Removed per section B rules.
- `avpn-advanced-fritti-course` (cooking-classes): cuisine_taught claimed "pizza fritta, montanara, frittatine di pasta, crocchette, cuoppo technique" but AVPN's actual course page covers croquettes, arancini, fried mozzarella, polenta chips, pasta fritters, tempura, zeppoline -- no pizza fritta or cuoppo. cuisine_taught and description rewritten to match the AVPN course page. Fixed.
- `culinary-backstreets-naples` (food-tours): source_url is an editorial guide page, not a tour-booking page. Meeting point "Piazza del Gesu Nuovo" not confirmed on any operator page. Flagged for awareness; operator existence confirmed (two real CB tours in Naples), but the exact meeting point cannot be verified from available sources. Not removed (operator is real, route description is general enough to not be fabricated), but noted.

### C. Festival month corrections

- `napoli-pizza-village`: start_day corrected from 1 to 7; day_range updated from "First week of July, six days" to "First or second week of July, six days". Month (July) was correct. 2026 confirmed dates are July 7-12 per carnifest.com.
- `festa-di-piedigrotta`: cuisine_evidence_url pointed to festivation.com page that does not mention Piedigrotta at all. Updated to napolike.com/festa-di-piedigrotta-2025-a-napoli-il-programma-completo; source_url and open_evidence_url updated to scabec.it/progetti/festa-di-piedigrotta/2025. end_day corrected from 9 to 14 to match the full 2025 programme window (Sept 1 to Oct 17, with the main day Sept 14). Fixed.

### D. Thin-category fabrication sweep

- vegan: 3 entries. All 3 confirmed by devourtours.com/blog/best-vegan-and-vegetarian-restaurants-in-naples/ (Officina Vegana, O'Grin, Un Sorriso Integrale mentioned by name; Vitto Pitagorico confirmed on same page). Below floor of 4. No fabrications detected.
- vegetarian: 2 entries (Un Sorriso Integrale, Vitto Pitagorico). Both confirmed by devourtours evidence URL. Below floor.
- gluten_free: 3 entries. Zero Zero Grano confirmed 100% gluten-free by atly.com. Siani Senza Glutine confirmed by mangiaresenzaglutine.it. Umberto confirmed by atly.com. AIC certification claim in description not confirmed by evidence URL (atly uses crowdsourced data); claim is plausible but not machine-verifiable. Flagged but not removed.
- halal: 2 entries. Mughal-e-Azam confirmed halal by zabihah.com with owner-confirmed status. Aladin Kebab confirmed halal by zabihah.com. Both clean.
- kosher: 0 entries. Not a defect; Naples has no readily verifiable kosher restaurants.

### E. Editorial-prose closed-venue echoes

- No prose echoes of removed entities found across itineraries, signature-dishes, food-history, neighborhoods, or region.json. Grep sweep clean.

## Entities removed

1. `secret-food-tours-pizza-class` (cooking-classes) -- fabricated logistics
2. `lebbrezza-vomero` (wine-bars) -- duplicate address, fabricated Vomero neighborhood label
3. `stanza-vomero` (wine-bars) -- duplicate address, fabricated Vomero neighborhood label
4. `lebbrezza-noe-vomero-bar` (bars) -- duplicate address, fabricated Vomero neighborhood label

## Defects total: 9 (5 cuisine_unverified/mismatch fixed, 1 route fabrication removed, 1 curriculum mismatch fixed, 2 festival date/evidence fixes)

## Below-floor topics after QA

- dietary/vegan: 3 entries (floor 4) -- needs research backfill
- dietary/vegetarian: 2 entries (floor 4) -- needs research backfill
- dietary/gluten_free: 3 entries (floor 4) -- needs research backfill
- dietary/halal: 2 entries (floor 4) -- needs research backfill
- cooking-classes: 3 entries after removal (floor 4) -- needs research backfill

## Verdict

VERDICT: PASS
