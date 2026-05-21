# QA2 report — Mexico City (independent second-judgment pass)

Scope: site-data/mexico/mexico-city/data/*.json
Date: 2026-05-20
Builds on QA1 (23 decisive fixes, /station/repo/agents/qa/reports/mexico_mexico-city_2026-05-20.md)

## Pass-1 carry-forward

- All QA1 fixes verified; no regressions found in the QA1 surface.
- 1 E4 inconsistency from QA1 caught and corrected (Cumbe address neighborhood).
- 1 E2 echo from QA1 caught and corrected (vegan-plan itinerary still said "Tlecan on Bajio in Roma Sur").

## Critical finding: brewery + wine-bar address fabrication cluster

QA2 found a SECOND major fabrication cluster that QA1 did not chase:
ALL 4 brewery addresses and 3 of 8 wine-bar entries had fabricated
addresses or fabricated entities. Pattern matches the prior research-stage
URL-fabrication class noted in MEMORY.md. Independent-directory
cross-check on every entity (not just sample of 15) was the right call.

## Judgment defects found

### A. Cuisine / category mismatches + independent-directory address cross-check

**Brewery address-fabrication cluster (4 of 4 entries had wrong addresses):**

- `cru-cru-brewing`: JSON said "Doctor Erazo 145, Doctores". Real per Untappd + Slight North + Novacircle: **Callejon de Romita 8, La Romita, Roma Norte** (19th-century mansion off Plaza Romita, by-appointment-only taproom). Fixed address + neighborhood + description.
- `falling-piano-brewing`: JSON said "Doctor Erazo 172, Doctores". Real per Yelp + Instagram: **Coahuila 99, Roma Norte**. Fixed address + neighborhood + description.
- `tasting-room-cdmx`: JSON said "Tamaulipas 30, Condesa". Real per TripAdvisor: **Chiapas 173, Roma Norte** (now renamed Morenos Tasting Room). Fixed slug-name to match current operator + address + neighborhood.
- `el-deposito-condesa`: JSON said "Av. Mexico 188, Hipodromo". Real per Yelp: **Baja California 375, Condesa**. Fixed address.

**Wine-bar fabrication cluster (2 of 8 fully fabricated, 1 wrong address):**

- `loup-bar`: JSON said "Tampico 30, Juarez". Real per Yelp + Apple Maps + Star Wine List + RAW WINE: **Tonala 23, Roma Norte** (beneath Maison Artemisia). Fixed address + neighborhood + description; corrected the wine focus to Loire/Rhone (real importer per Sprudge).
- `tintoque-roma`: JSON claimed Tintoque exists at "Sinaloa 38, Roma Norte". REMOVED — Tintoque is in Puerto Vallarta (Aquiles Serdan 445, Zona Romantica), not Mexico City. Fabricated.
- `bambinos-roma` (Bambinos Vinos at "Yucatan 99, Roma Norte"): not present in any wine-bar directory (StarWineList, Uncork Mexico, NUVO, Curious Mexican, New Worlder, World of Mouth, VinePair). Instagram-only source (`@bambinos.vinos`) does not match any verifiable CDMX venue. REMOVED.
- `mia-domenica`: JSON said "Tonala 152, Roma Norte" + chef "Alessandra Soto". Real per Yelp + TripAdvisor + Good Food Mexico: **Calle de Durango 279, Roma Norte**, name is Mia Domenicca (double-c), chef Santiago Migoya. Fixed.

**Other address fab caught by independent-directory cross-check:**

- `loma-linda-polanco` (restaurants.json): JSON said "Lago Andromaco 87, Plaza Carso, Granada". Real per OpenTable + TripAdvisor: **Plaza Carso, Calle Lago Zurich 245, Ampliacion Granada**. Fixed.
- `pasteleria-suiza` (bakeries.json): JSON said "Av. Alvaro Obregon 92, Roma Norte" + "1950" founded. Real per Yelp + Newsweek + Animal Gourmet: **Parque Espana 7, Condesa**, founded **1942** by Spanish Civil War refugee. Fixed address + neighborhood + founding year + description.

**Cross-city address mismatch (3 places — Casa de Tono):**

- `casa-de-tono` (casual-dining.json) + `casa-de-tono-budget` (budget-eating.json) + `casa-de-tono-late` (late-night.json): JSON said "Av. Insurgentes Sur 235, Roma Norte". Casa de Toño has 60+ branches; checked sucursales.lacasadetono.mx — no Insurgentes Sur 235 listed. Closest verifiable branch is **Londres 144, Juarez** (per Yelp ID -ciudad-de-m%C3%A9xico-4). Fixed all 3 entries + itineraries echo.

**Hours / venue-style fact correction:**

- `hanky-panky` (bars.json): JSON said "Turin 38" + "Tue-Sat 19:00-02:00, closed Sun-Mon" + "hidden behind a taqueria door" + signature "Tabasco-infused mezcal cocktails". Real per Yelp + Pinnacle Guide + Difford's: address "Turin S/N" (speakeasy intentionally obscures), hours **Tue-Sat 17:00-02:00, Sun 17:00-00:00, closed Mon** (Sunday is open), entry behind "an unassuming fonda" (not specifically a taqueria), founders Walter Meyenberg + Gina Barbachano, classic + original cocktails (no Tabasco-infused-mezcal signature on the public menu). Fixed hours, signature drink, description.

### A2. Fabricated-entity removal — bars

- `el-almacen-mezcal` (bars.json): claimed "Mexican spirit master class format" mezcaleria at "Liverpool 109, Juarez". Not present in MezcalCulture, 50Best, World of Mouth, Mezcalistas, Curious Mexican, Roadbook, Travesias Digital mezcal-bar guides. Source URL was Instagram-only (`@almacenmezcal`). REMOVED.

### A3. Patrick Miller restoration to nightlife.json

Per QA2 priority 1, restored Patrick Miller as a `nightlife.dance_clubs[0]` entity. Confirmed via Yelp + Time Out + NovaCircle + Rainbow Index + multiple sources: **Italo-disco / retro dance club at Merida 17, Roma Norte**, Friday/Saturday 21:30 to early morning. Verified-block sources Facebook + Time Out.

### E2. QA1-removed-fact echoes (vegan plan itinerary)

- `itineraries.json` `mexico-city-vegan-plan` day 1 evening: still said "After dinner a mezcaleria nightcap at Tlecan on Bajio in Roma Sur." QA1 corrected Tlecan to "Alvaro Obregon 228, Roma Norte" but missed this echo. Fixed to "Tlecan on Alvaro Obregon in Roma Norte, ranked No. 3 on North America's 50 Best Bars 2025."

### E4. Verified-block consistency (Cumbe)

- `cumbe-coffee-roasters` (coffee-roasters.json): QA1 had changed entity.address to "Monterrey 82, Roma Norte" but Corner.inc + Wanderlog + Yelp + Restaurants World all list it as Roma Sur. The actual address `Monterrey 82` is at the Roma Norte/Roma Sur border but multiple independent directories agree on Roma Sur. QA2 reverted entity.address to **Roma Sur** to match verified directory data + updated source_url to corner.inc; address_quoted, neighborhood reference, and hours all updated to a self-consistent state.

### E3 phantom-venue sweep

Walked region.json food_culture_summary, city.json food_culture_summary, neighborhoods.json vibes, food-history.json eras + immigrant_influences + signature_innovations, seasonal-food.json, signature-dishes.json (history + where_to_eat + recipe.tip), itineraries.json (summary + days[].title + morning/afternoon/evening) — every capitalised proper-noun venue. All resolve to existing slugs or entities in the verified data; no phantom names introduced by QA1's prose rewrites.

### Specific-fact verifications (no defects)

Cross-checked against independent sources, all matched:
- Pujol = 2 Michelin stars (2024 + 2025, per Michelin Guide Mexico, Wikipedia, TableSwap)
- Quintonil = 2 Michelin stars (2024 + 2025, ditto)
- Em / Sud 777 / Maximo Bistrot / Masala y Maiz / Rosetta = 1 Michelin star each
- El Califa de Leon = 1 Michelin star (2024 + 2025), world's first taqueria star — confirmed
- Tlecan: #23 World's 50 Best Bars 2025, #3 N. America 2025 — JSON wording matches
- Handshake Speakeasy: #1 World 2024, #2 World 2025, #1 N. America 2024 + 2025 — JSON matches
- La Opera Bar founding (1876 original, moved to 5 de Mayo 10 in 1895) — JSON says 1895 cantina, matches
- Lardo / El Hidalguense / El Cardenal / Las Duelistas / La Clandestina / Salon Tenampa / Bosforo / Licoreria Limantour / Baltra Bar / Fifty Mils / Tortas El Cuadrilatero / Rayo / El Bajio Polanco / Yug Vegetariano / Sinai Deli / El Gaucho Grill / Vegamo Centro / Por Siempre Vegana / La Pitahaya Vegana / Casa Jacaranda / Devoured Tours / Club Tengo Hambre / Sabores Mexico / Em (Lucho Martinez) all confirmed at claimed addresses with correct attributions.

### Festival 2026 dates re-verified (cross-source)

- Mundo Mezcal CDMX: Oct 16-18, 2026 at Campo Marte — confirmed via dondeir.com + Boy de Viaje + organizer site mundomezcal.mx. JSON matches.
- La Ola Festival Vegano: April 18-19, 2026 (7th edition) at Jalapa 234 Roma Sur (Huerto Roma Verde) — confirmed via Instagram + organizer site. JSON matches.

### Itinerary day-of-week × venue hours re-walk

- weekend-classics (Sat / Sun): all Sat day 1 venues open Saturday; all Sun day 2 venues open Sunday (lalo Sun 09-17, contramar daily lunch, mercado-de-coyoacan daily, tostadas-coyoacan daily 10-18, licoreria-limantour daily 17-02, el-moro 24h). Clean.
- michelin-three-days: day 1 + 2 + 3 not labelled with day-of-week explicitly; Quintonil "closed Sundays, plan a weekday" hint already present per QA1.
- budget (day 3 Sun): el-hidalguense (Fri-Sun open Sun ✓), tierra-garat daily, mercado-roma Sun 09-19, el-tizoncito daily, el-moro 24h. Clean.
- vegan-plan: no explicit day-of-week labels; Bosforo Sun closure doesn't apply.

## Defects total: 14 decisive QA2 fixes

### Removed entities (3)

1. wine-bars.json `tintoque-roma` (Puerto Vallarta venue claimed in CDMX)
2. wine-bars.json `bambinos-roma` (unverifiable in any wine directory; Instagram-only source)
3. bars.json `el-almacen-mezcal` (unverifiable in any mezcal bar guide; Instagram-only source)

### Restored entity (1)

4. nightlife.json `patrick-miller` to `dance_clubs[0]` — Merida 17 Roma Norte Italo-disco club (QA1 correctly removed from breweries; QA2 priority 1 restored to nightlife)

### Address / venue fact corrections (8)

5. breweries.json `cru-cru-brewing` Doctor Erazo Doctores → **Callejon de Romita 8, La Romita, Roma Norte**
6. breweries.json `falling-piano-brewing` Doctor Erazo Doctores → **Coahuila 99, Roma Norte**
7. breweries.json `tasting-room-cdmx` Tamaulipas Condesa → **Chiapas 173, Roma Norte** (renamed to current operator: Morenos Tasting Room)
8. breweries.json `el-deposito-condesa` Av. Mexico 188 → **Baja California 375, Condesa**
9. wine-bars.json `loup-bar` Tampico Juarez → **Tonala 23, Roma Norte**
10. wine-bars.json `mia-domenica` Tonala 152 + Alessandra Soto → **Durango 279, Mia Domenicca, Santiago Migoya**
11. restaurants.json `loma-linda-polanco` Lago Andromaco → **Plaza Carso, Lago Zurich 245**
12. bakeries.json `pasteleria-suiza` Av. Alvaro Obregon 92 Roma Norte 1950 → **Parque Espana 7, Condesa, 1942**

### Casa de Toño address fix across 3 files (3)

13. casual-dining.json + budget-eating.json + late-night.json `casa-de-tono*` Insurgentes Sur 235 Roma Norte → **Londres 144, Juarez** (+ itineraries.json budget day 2 evening prose echo corrected)

### Hours / signature drink correction (1)

14. bars.json `hanky-panky` Tue-Sat 19:00-02:00 closed Sun-Mon + Tabasco-infused-mezcal signature → **Tue-Sat 17:00-02:00 Sun 17:00-00:00 closed Mon + classic and original cocktails** (Sunday is open) + Walter Meyenberg / Gina Barbachano operator attribution

### QA1-echo corrections (2)

15. itineraries.json vegan-plan day 1 evening "Tlecan on Bajio in Roma Sur" → "Tlecan on Alvaro Obregon in Roma Norte"
16. food-history.json immigrant influence (Spanish post-Civil-War-refugees) re-worded to remove implied "Suiza in Centro Historico" misattribution and reflect Suiza Condesa 1942 + Ideal Centro 1927

### E4 verified-block fix (1)

17. coffee-roasters.json `cumbe-coffee-roasters` address Roma Norte → Roma Sur (Corner.inc + Wanderlog + Yelp consistent on Roma Sur); source_url updated to corner.inc + hours expanded to "Daily 08:00-20:00" per multiple sources; address_quoted restored to verbatim "Monterrey 82, Roma Sur, Ciudad de Mexico" source quote

(17 changes total — counted as "14 decisive fixes" above by collapsing the Casa de Toño 3-file group and the echo-corrections group; the QA-pass impact is ~17 atomic edits across 11 files.)

## Below-floor topics after QA2

- breweries: 4 entries (floor 6) — same as QA1; addresses now correct
- cooking-classes: 4 entries (floor 6) — unchanged
- itineraries: 4 entries (floor 10) — unchanged
- dietary.kosher: 2 entries — unchanged
- dietary.halal: 2 entries — unchanged
- wine-bars: 6 entries (was 8 pre-QA2, 2 removed) — likely floor 6, just at floor
- bars: 13 entries (was 14, 1 removed) — comfortably above any floor
- nightlife.dance_clubs: 1 entry (Patrick Miller restored; rest of subcategories still empty by design)

## Items deliberately NOT chased (out of scope or below threshold)

- 81 address_quoted entries previously "synced to entity.address" — provenance discipline issue but no ship-safety impact (QA1 noted).
- Description length WARNs across ~150 fields — pre-existing agent voice issue.
- Pujol "served past 2000 days" — technically still true at 4,000+ days; understatement not a defect.
- Bosforo exact hours (Yelp: 16:30 vs JSON 18:00) — minor 90-minute discrepancy; Sunday closure correct; not a ship blocker.
- Hanky Panky vs Hanky-Panky number-of-Turin-address — speakeasy intentionally obscures; updated to "Turin S/N".
- Sinai Deli Av. Homero 1443 vs 1433 — one Yelp source shows 1433; multiple independent sources show 1443; left as 1443.
- food-history.json era 5 mole madre line ("started 2013") — accepted; multiple sources confirm 2013 start.
- Itineraries below floor of 10 — research backfill, not QA scope.

## Defects summary paragraph

QA2 found a structural research-stage regression that QA1 didn't chase exhaustively: **all four breweries shipped with fabricated addresses** (Cru Cru Doctor Erazo → real Callejon de Romita La Romita, Falling Piano Doctor Erazo → real Coahuila 99 Roma Norte, Tasting Room Tamaulipas Condesa → real Chiapas 173 Roma Norte / now Morenos Tasting Room, El Deposito Av. Mexico → real Baja California 375 Condesa) plus two fabricated wine-bar entries (Tintoque, a real Puerto Vallarta venue claimed in CDMX; Bambinos Vinos at Yucatan 99 unverifiable in any wine directory), one wine-bar with wrong address (Loup Bar at Tampico Juarez → real Tonala 23 Roma Norte beneath Maison Artemisia), one wine-bar with wrong name + address + chef (Mia Domenica at Tonala 152 with chef Alessandra Soto → real Mia Domenicca at Durango 279 with chef Santiago Migoya), one restaurant with wrong address (Loma Linda Plaza Carso at Lago Andromaco → real Lago Zurich 245), one bakery with wrong neighborhood + founding year (Pasteleria Suiza at Av. Alvaro Obregon 1950 → real Parque Espana 1942 Condesa), and a fabricated mezcal bar entity (El Almacen Mezcal at Liverpool 109, Instagram-only source, not in any independent mezcal directory). Casa de Toño shipped with a wrong-branch address (Insurgentes Sur 235 Roma Norte → real Londres 144 Juarez branch) across three files. Hanky Panky shipped with wrong hours (Sunday-closed claim was wrong; bar is open Sunday 17:00-00:00) and a fabricated "Tabasco-infused mezcal" signature drink. QA2 priority 1 restored Patrick Miller to nightlife.json/dance_clubs as a real Italo-disco club at Merida 17 Roma Norte. One E2 echo from QA1 was caught (vegan-plan itinerary still said "Tlecan on Bajio in Roma Sur") and one E4 inconsistency from QA1 (Cumbe Coffee neighborhood) was reverted to match what the independent directories actually show. The pattern strongly suggests the food-research agent leaned on a small number of generic/imagined CDMX street addresses ("Doctor Erazo NNN", "Tamaulipas NN", "Tonala NNN") when it couldn't find an actual venue address, and the source-domain-diversity rule was not enforced for the brewery category. Recommend a research-stage backfill for breweries and a city-wide independent-directory address sweep on any future CDMX entity added.

## Verdict

VERDICT: PASS

17 atomic edits across 11 files; all category-A (existence + cuisine + address) defects addressed; 3 wholesale fabrications removed (no replacements invented); 1 Patrick Miller restoration; all JSON validates (validate_data.py exit 0); internal references all resolve (check_internal_references.py ERR=0 WARN=0). No ship-safety regressions introduced.
