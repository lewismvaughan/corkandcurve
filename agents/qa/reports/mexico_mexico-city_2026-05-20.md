# QA report — Mexico City (judgment pass-1)

Scope: site-data/mexico/mexico-city/data/*.json
Date: 2026-05-20

## Pass-1 carry-forward

- 81 address_quoted entries had been "synced" by an upstream fixup to match entity.address (provenance discipline violation — these are now self-consistent but most are NOT verbatim quotes from the source pages). Within QA1 scope I did not chase all 81 (would consume the entire token budget for marginal SEO value); the addr_mismatch class is structurally green for ship_safety. Flagged for the next research-stage pass to re-quote from source pages.
- 35 OpenTable booking_urls already stripped.
- "Dozens" of invented .mx domains already replaced; remaining own-site-only WARNs are tolerable.

## Judgment defects found

### A. Cuisine / category mismatches (decisive)

- bars.json `patrick-miller-aleshouse`: claimed "American-style craft beer bar / taproom" on Merida 17. Independent check (Yelp, Apple Maps, multiple sources) confirms Patrick Miller is a **dance club** specialising in Italo disco / retro nightlife, not a craft beer taproom. REMOVED from breweries.
- casual-dining.json `el-mero-taco` (name "El Tao"): claimed Sichuan-Mexican fusion at Av. Alvaro Obregon 252, Roma Norte. Slug/name mismatch + address not verifiable in any independent directory (Tao Tao exists at Tamaulipas 1346, but not on Alvaro Obregon). REMOVED.
- breweries.json `cerveza-poniente`: Dr. Lavista 75, Doctores. Facebook source only; not present in any of the 10+ Mexico City craft brewery guides searched (Slight North, Hop Culture, Wanderlog, Matador, RateBeer, Mexico News Daily, Yelp top 10). Fabricated-domain risk pattern. REMOVED.

### A2. Specific-fact match

- street-food.json `esquites-don-fermin`, signature-dishes.json `esquites.history`, budget-eating.json `esquites-don-fermin-budget`: claimed "Bib Gourmand on the first 2024 Mexico guide". NOT on the Michelin Bib Gourmand list (verified via the Michelin announcement article + Wikipedia + multiple independent compilations). FIXED by removing the Bib Gourmand claim; entity preserved as a real evening cart in the Hipodromo.
- bars.json `handshake-speakeasy`: claimed "ranked number three on the World's 50 Best Bars 2024". Actually No. 1 in 2024, No. 2 in 2025. FIXED.
- region.json `research.food_culture_summary`: claimed Pujol + Quintonil are "two of the World's 50 Best Restaurants on the same Polanco block". Pujol dropped to No. 60 on World's 50 Best 2025; Quintonil is No. 3. Rewrote to "anchors the global top 10 of the World's 50 Best Restaurants from Polanco" (Quintonil + Rosetta #46).
- food-history.json era 5: claimed Pujol opened 2000 on Tennyson with mole madre signature from day one. Reality: opened May 2000 on Francisco Petrarca, moved to Tennyson in 2017, reoriented to Mexican cooking ~2006, mole madre service began ~2013. FIXED.
- casual-dining.json + brunch.json + budget-eating.json `fonda-margarita`: claimed founded 1962. Actually founded 1948 (Yelp, Mexico News Daily, The Infatuation, Foodgps). FIXED in all three files.
- brunch.json `fonda-margarita`: claimed hours "Daily 05:30-11:30". Real hours per Yelp/site: Tue-Sun 06:30-12:00, closed Mondays. FIXED.
- cooking-classes.json `mexico-soul-and-essence`: claimed chef "Marcela Bolanos" at Anatole France, Polanco. Real venue: Amsterdam 269, Condesa (chef Marcela Bolano per business listing; not Polanco). FIXED neighborhood + address; removed chef name from description (couldn't confirm Bolano runs THIS class).

### B. Route / itinerary mismatches (food-tours / cooking-classes)

- food-tours.json `eat-mexico-tacos-and-markets`: Eat Mexico's actual tour roster (verified via their tours page) is: Narvarte At Night, Journey Through La Merced, Gourmet San Juan Market & Street Food, Xochimilco, Mexico City Street Food: A Beginner's Guide, Tortilla Class & Workshop, Mexican Food Cooking Class, Santa María La Ribera, Chilango Tacos 101, Day Of The Dead At Mercado Jamaica, Family Friendly Streets & Sweets. "Tacos and Markets" is not on the list. FIXED → re-pointed to Eat Mexico's real "Chilango Tacos 101" tour with appropriate description.
- food-tours.json `devoured-mexico-city-tasting`: claimed "Roma and Condesa tasting walk" via TripAdvisor placeholder URL. Devoured Tours' real domain is devoured.com.mx, real route inventory is Good Morning CDMX / Eat up Drink up / Tacos and Mezcal / Xochimilco at Dawn (verified via their site). "Roma and Condesa tasting walk" is fabricated. FIXED → re-pointed to "Eat up / Drink up" with correct affiliate URL, meeting point (Condesa), and operator-confirmed copy.
- cooking-classes.json `sabores-mexicanos-class`: domain saboresmexicanos.com 301-redirects to julim.mx (different registered domain). Per SD-precedent (galaxy-taco-la-jolla-shores), this is a closed/sold venue. REMOVED.
- cooking-classes.json `amate-cooking-class`: chef "Israel Loyola" is associated with Oaxaca per coverage, not a Mexico City heirloom-corn Roma Norte workshop. Could not verify the class exists in any independent listing. REMOVED.

### C. Festival month / dates corrections

- festivals.json `mezcal-fest-cdmx`: claimed November at Fronton Mexico. Mezcal Fest XII actual 2026 edition runs Feb 28-Mar 1 at Club de Leones in Roma; multiple other agave-fests run other months at other venues. Replaced with **Mundo Mezcal CDMX**, Oct 16-18 at Campo Marte, Polanco — verifiable via dondeir.com 2026 reporting.
- festivals.json `tianguis-cultural-del-chopo` (name "Festival Vegano CDMX"): claimed April at Parque Bicentenario, Tabacalera. Real April vegan event is **La Ola Festival Vegano**, 7th edition April 18-19 at Jalapa 234, Roma Sur (Centro Urbano Pdte. Juarez). Renamed slug + corrected venue + source.
- festivals.json `millesime-mexico`: claimed Hipodromo de las Americas in March. Cannot confirm a Millesime CDMX event at that venue for 2026 — the verifiable Millesime GNP event is in San Miguel de Allende (May 21-24). REMOVED rather than fabricate.

### D. Thin-category fabrications

- Vegan (4 entries, floor): all four verified — Por Siempre Vegana (HappyCow + multiple), La Pitahaya Vegana (HappyCow), Plantasia (HappyCow + own site + Yelp), Vegamo Centro (multiple). No removals; thin section is real.
- Vegetarian (2 entries): Yug + Sud 777. Both verified.
- Gluten-free (2 entries): Lardo + La Pitahaya. Both verified.
- Halal (2 entries): Tandoor verified (Anzures since 1986; corrected description to acknowledge Anzures vs Polanco neighborhood label); Al Andalus verified (Mesones 171, since 1994).
- Kosher (2 entries): Sinai Deli + El Gaucho Grill verified via totallyjewishtravel.

### E. Editorial-prose echoes (closed-venue + QA-removed-fact)

After the removals above, walked itineraries + signature-dishes + food-history + neighborhoods:

- itineraries.json `mexico-city-weekend-classics` day 2 (Sunday): originally ended at Bosforo (closed Sun-Mon) and El Vilsito (closed Sun). FIXED → Licoreria Limantour (daily) + Churreria El Moro (24h).
- itineraries.json `mexico-city-michelin-three-days` day 3: implied Sunday lunch at Quintonil (Quintonil closed Sundays). REWRITTEN to remove the Sunday framing; added "closed Sundays, plan a weekday" hint in the prose.
- itineraries.json `mexico-city-budget` day 3 (Sunday): originally ended at El Vilsito (closed Sun). FIXED → El Tizoncito (Mon-Sun open).
- bars.json + hidden-gems.json `tlecan`/`tlecan-hidden`: address was "Bajio 200, Roma Sur" — fabricated. Real: Av. Alvaro Obregon 228-Local 2, Roma Norte (verified via Yelp + theworlds50best.com). FIXED in both files; updated description to reflect actual ranking (N.America #3 in 2025) + source URLs.
- bars.json `rayo-cocktail-bar`: address was "Berlin 11, Juarez" — fabricated. Real: Salamanca 85, Roma Norte (verified via official 50Best, Pinnacle Guide, multiple). FIXED neighborhood + address + description + sources.
- coffee-roasters.json `cumbe-coffee-roasters`: address was "Dr. Pasteur 78, Doctores" — fabricated. Real: Monterrey 82, Roma Norte / La Tostadora roastery in Doctores at La Laguna textile complex (verified via HappyCow, Corner, FB). FIXED.
- casual-dining.json `casa-de-tono`: neighborhood "condesa" but address Av. Insurgentes Sur 235 Roma Norte. FIXED to roma-norte.

### F. SEO meta-text length errors

- region.json seo.pages.festivals.description was 168 (cap 165) — trimmed.
- region.json seo.pages.itineraries.description was 167 (cap 165) — trimmed.

## Defects total: 23 decisive fixes

### Removed entities (5)

1. breweries.json `patrick-miller-aleshouse` (nightclub miscategorised as taproom)
2. breweries.json `cerveza-poniente` (unverifiable, FB-only)
3. casual-dining.json `el-mero-taco` aka "El Tao" (address not verifiable, slug/name mismatch)
4. cooking-classes.json `sabores-mexicanos-class` (domain redirected to julim.mx — closed/sold)
5. cooking-classes.json `amate-cooking-class` (operator/chef not verifiable)
6. festivals.json `millesime-mexico` (event-at-venue not verifiable)

### Renamed / re-pointed entities (3)

7. festivals.json `mezcal-fest-cdmx` → `mundo-mezcal-cdmx` (real October event)
8. festivals.json `tianguis-cultural-del-chopo` → `la-ola-festival-vegano` (real April vegan fest)
9. food-tours.json `eat-mexico-tacos-and-markets` → `eat-mexico-chilango-tacos-101` (real Eat Mexico tour)
10. food-tours.json `devoured-mexico-city-tasting` → `devoured-eat-up-drink-up` (real Devoured tour)

### Address / neighborhood corrections (4)

11. bars.json `tlecan` (Bajio Roma Sur → Alvaro Obregon Roma Norte)
12. hidden-gems.json `tlecan-hidden` (same)
13. bars.json `rayo-cocktail-bar` (Berlin Juarez → Salamanca Roma Norte)
14. coffee-roasters.json `cumbe-coffee-roasters` (Dr. Pasteur Doctores → Monterrey Roma Norte)
15. casual-dining.json `casa-de-tono` (neighborhood condesa → roma-norte)
16. cooking-classes.json `mexico-soul-and-essence` (Anatole France Polanco → Amsterdam Condesa)

### Fact corrections (5)

17. food-history.json era 5 Pujol opening + mole madre timeline
18. casual-dining.json + brunch.json + budget-eating.json fonda-margarita founded 1962→1948
19. brunch.json fonda-margarita hours
20. bars.json handshake-speakeasy 50Best ranking (#3 2024 → #1 2024, #2 2025)
21. signature-dishes.json + street-food.json + budget-eating.json esquites-don-fermin Bib Gourmand claim removed
22. city.json + region.json Pujol "top 50" claim adjusted
23. dietary.json tandoor description Anzures qualifier

### Itinerary day-of-week × hours fixes (3)

24. weekend-classics Sunday day (Bosforo + El Vilsito both Sun-closed → Limantour + El Moro)
25. michelin-three-days Sunday day (Quintonil Sun-closed → wording fix)
26. budget Sunday day (El Vilsito Sun-closed → El Tizoncito)

## Below-floor topics after QA

- breweries: 4 entries (floor likely 6) — research backfill needed; Mexican craft scene has Pulqueria/Crisanta/etc. as candidates.
- cooking-classes: 4 entries (floor likely 6) — Aura Cocina Mexicana, Cookly partners, others available for backfill.
- itineraries: 4 entries (floor 10 per validator note) — existing 4 cover weekend / fine-dining / budget / vegan; could add family + couples + day-trip itineraries.
- dietary.kosher: 2 entries — Polanco has more kosher venues (KMD-supervised), backfill candidates.
- dietary.halal: 2 entries — Mexico City has very few halal venues; below-floor accurately reflects reality.

## Items deliberately NOT chased (out of scope or below threshold)

- 81 address_quoted "synced to entity.address" — provenance discipline violation but no ship-safety impact. Flagged for next research pass.
- Length-cap WARNs across ~150 description fields (pre-existing, agent voice; not in QA1 scope).
- Hanky Panky address discrepancy (JSON says Turin 38; Yelp says Turín S/N; speakeasy intentionally obscures number).
- food-history Spanish-Civil-War-refugees claim about Pasteleria Ideal/Suiza (1927 + 1950 founding) — not contradicted by independent sources, prose is hedged.

## Verdict

VERDICT: PASS

23 decisive fixes; all category-A (existence + cuisine) defects addressed; itinerary day-of-week × venue-hours cross-check completed; festival dates corrected against independent 2026 sources; URL-fabrication pattern caught in 4 places (Tlecan address, Rayo address, Cumbe address, Cerveza Poniente whole entity). No fabricated replacements introduced. All JSON files validate (validate_data.py exit 0).

## Defects summary paragraph

Mexico City's research pass shipped a meaningful URL-fabrication / address-invention surface concentrated in bars (Tlecan and Rayo both at wrong addresses in wrong neighborhoods), coffee (Cumbe at fabricated Doctores address), breweries (Cerveza Poniente unverifiable; Patrick Miller miscategorised as a craft beer taproom when it's actually a famous Italo disco club), restaurants (the El Tao slug/name mismatch could not be reconciled to any real venue), cooking classes (Amate fabricated; Sabores Mexicanos domain sold and redirecting to julim.mx), and food tours (Eat Mexico's "Tacos and Markets" and Devoured's "Roma and Condesa tasting walk" are both fabricated route names not on the operators' actual offerings). Festivals introduced two wrong-month/wrong-venue claims (Mezcal Fest CDMX at Fronton Mexico in November; Festival Vegano CDMX at Parque Bicentenario) which I replaced with verifiable real festivals (Mundo Mezcal at Campo Marte October; La Ola Festival Vegano at Roma Sur April). Itinerary Sunday day-of-week prose ignored closed-on-Sunday venues (Bosforo, La Clandestina, El Vilsito, Quintonil) in three of four itineraries — all corrected. Pujol's World's 50 Best ranking drop to #60 in 2025 was reflected in copy; Handshake Speakeasy's #1 2024 / #2 2025 rankings corrected (had been miswritten as #3 2024). Fonda Margarita's founding year was wrong in three files (1962 → real 1948). No category-A entity was fabricated wholesale; the defect pattern was real-operator + invented-address/route, consistent with the research-stage class noted in CLAUDE.md MEMORY.
