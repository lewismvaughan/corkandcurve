# QA report - Marseille (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety.sh exited green pre-QA)
- verify_entities.py warnings: none flagged by orchestrator

## Judgment defects found

### A. Cuisine / category mismatches + independent-directory address cross-check

- restaurants.json `le-femina`: research labeled "Tunisian and Berber"; Gault&Millau plus Mon Resto Halal both confirm Algerian/Amazigh heritage (Algerian and Amazigh flags on display, founded 1921 by Algerian family). Rewrote cuisine to "Algerian Berber". Also removed booking_url that was a fabrication pointing at La Kahena's directory page.
- casual-dining.json `le-cafe-de-la-banque`: research said neighborhood 6e but address "26 Rue Paradis, 13001" (1er postcode contradicted neighborhood). Operator's own site (lecafedelabanque.com) gives 24 boulevard Paul Peytral, 13006 Marseille. Fixed address, address_quoted, source_url, and description ("in Marseille's 1er opposite the Banque de France" was wrong twice).
- bars.json + late-night.json `bar-de-la-marine`: address listed as "15 Quai de Rive Neuve, 13001 Marseille" but Quai de Rive Neuve is 13007 (Saint-Victor neighborhood, south side of Vieux Port). Google Maps and Marseille-tourisme both confirm 13007. Fixed postcode and arrondissement label in both files.
- dietary.json `la-kahena-halal`: source_url pointed at `mon-resto-halal.com/restaurants/top/13055-marseille/libanais` (Lebanese category); La Kahena is Tunisian. Repointed to operator's own site lakahena.fr.

### A2. Specific-fact match

- bakeries.json `maison-saint-honore`: research claimed "white baguettes, charcoal focaccia, king's cakes" and signature item "Charcoal focaccia". Pierre Ragot's actual operation is 100 percent organic sourdough bread plus viennoiserie, no pastries, no focaccia. Rewrote description, specialty, and signature_item to match Pierre Ragot's real grain-to-bread philosophy.
- cooking-classes.json `miramar-bouillabaisse-class`: research said "third Thursday of the month, 9:30-14:00, EUR 120, max 10". Cote Magazine + Tourist Office confirm "one or two Thursdays per month, 10:30-14:00, EUR 112, 8 to 10 max". Corrected price, group_size, format, hours.

### B. Route / itinerary mismatches

- food-tours.json `culinary-backstreets-marseille`: route confirmed (starts at Gare Saint-Charles, into Noailles, west toward Vieux Port and Panier).
- food-tours.json `do-eat-better-marseille`: meeting point 66 Quai du Port in front of Le New Terrasse confirmed.
- cooking-classes.json `miramar-bouillabaisse-class`: class exists and is real (was just mis-priced and mis-scheduled, fixed above).

### C. Festival month / date corrections

- festivals.json `street-food-festival-mpg`: research said month August, start_day June 12, end_day June 14, location "Esplanade J4". Operator's 2026 page confirms September 10-12, 2026 at Esplanade Jean-Paul II (la Major). Fixed month, day_range, start_month, start_day, end_month, end_day, address, and address_quoted.
- festivals.json `foire-aux-santons`: location was "Place Charles de Gaulle, 13001". 2025/26 edition (and the typical recent annual location) is the Vieux-Port / Quai du Port (13002), per madeinmarseille + Frequence-Sud. Updated address, description, and address_quoted. Date window (Nov 15 to Jan 4) confirmed for the 2025/26 edition.

### D. Thin-category fabrications

- vegan 2/2 confirmed (Oh Faon via HappyCow; De Bon'heur Cafe via HappyCow + love-spots).
- vegetarian 2/2 confirmed (Le Cours en Vert via HappyCow; Tabla via operator site tablamarseille.fr).
- gluten_free 2/2 confirmed (La Pepite via love-spots + HappyCow; Oh Faon via HappyCow + findmeglutenfree.com).
- halal 3/3 confirmed (Le Femina via mon-resto-halal; Chez Yassine via mon-resto-halal + operator chezyassine.com; La Kahena via lakahena.fr — fixed source_url defect above).
- kosher 2/2 confirmed (Le 8eme Sud and La Maronaise Cafe via Beth Habad 8eme; dec 2023 list still current per phone numbers).

### E. Editorial-prose echoes

- E1: L'Epuisette and Restaurant Saisons echo check. L'Epuisette appears only in historical "Auffo took over the L'Epuisette site" context in fine-dining, restaurants, and itineraries — acceptable. Saisons not referenced anywhere.
- E2: Le Femina cuisine rewrite (Tunisian -> Algerian Berber) — propagated to city.json food_culture_summary, food-history.json (immigrant_influences + Maghrebi-era paragraph), dietary.json halal entry, street-food.json (no change needed, language was neutral), itineraries.json (Day 1 Friday afternoon lunch prose). All Tunisian-Femina strings purged.
- E2: Cafe de la Banque rewrite (1er Banque de France -> 6e Estrangin) — corrected the description block; no other files reference Cafe de la Banque.
- E3 phantom-venue sweep in region.json SEO descriptions: festivals.description named "Fete du Vin", "Festival des Soupes", "La Bonne Mere" and "Christmas market on Cours Belsunce" — none of these exist in festivals.json. Rewrote to reference only the 5 entities that are actually in the data: Foire aux Santons, Vieux-Port Christmas market, MPG, Street Food Festival, Chandeleur.
- E3: walked region.json other SEO descriptions, city.json food_culture_summary, neighborhoods.json vibe, food-history.json paragraphs, signature-dishes.json history blocks, seasonal-food.json blurbs, itineraries.json day prose, and per-entity descriptions/tips/why_hidden. No further phantom venues found.

### Itinerary day-of-week × venue-hours

- itineraries.json `marseille-weekend-classics` Day 2 was labeled "Sunday: Capucins morning, Le Panier lunch". Marche des Capucins is closed Sunday AND Chez Etienne is closed Sunday (and Wednesday). Both venues in the day's prose are dark on Sunday. Renamed itinerary to "Friday-and-Saturday" framing and changed Day 1 title from "Saturday" to "Friday" and Day 2 title from "Sunday" to "Saturday". Friday + Saturday is now consistent with all referenced venues (Four des Navettes Mon-Sat, La Tisserie Tue-Sat, Chez Madie Mon-Sat, La Caravelle daily, Chez Fonfon daily, Marche des Capucins Mon-Sat, Coogee Mon-Sat, Chez Etienne Tue-Sat closed Wed, Tuba Club daily).
- itineraries.json `marseille-noailles-maghreb` Day 1 Friday and Day 2 Saturday already consistent with venue hours (Femina Tue-Sat, La Cantinetta closed Sunday only, Pepie Tue-Sat, Pelle-Mele nightly, Chez Yassine Tue-Sun, La Kahena daily, Mama Shelter daily, La Mercerie Tue-Sat, Carry Nation Wed-Sun).
- itineraries.json `marseille-fine-dining-three-days` does not name specific weekdays. Venue closure profile (Le Petit Nice Tue-Sat, AM Wed-Sat, Sepia Tue-Sat, Auffo Tue-Sat, Pain Salvator Tue-Sun, Marche des Capucins Mon-Sat, Une Table au Sud Tue-Sat) requires a Wed-Thu-Fri or Tue-Wed-Thu or Thu-Fri-Sat schedule. Compatible; no edit needed.

### Markets / day-trips polish

- markets.json `marche-de-noailles-extension`: name was "Marche d'Aubagne" which reads as the Aubagne town market 17km away. Renamed to "Marche de Noailles (Rue d'Aubagne)" to disambiguate.
- day-trips-food.json `aix-en-provence-markets`: description named "Place Comtales" — actual second market square is Place des Precheurs. Fixed.

### F. Editorial voice

- No purple-language or AI-tell issues spotted beyond the validator's reach.

### Other cleanups

- budget-eating.json `pizza-charly-budget`: duplicate `cuisine_evidence_url` key in the verified block; removed the duplicate (one of the JSON keys was repeated verbatim).
- bakeries.json `pain-salvator`: hours field claimed Sunday morning service (7:30-13:00); operator and tourism listings confirm closed Sunday AND Monday. Updated to "Tue-Sat 9:00-19:00, closed Sunday and Monday".

### Validation

- `python3 scripts/validate_data.py --city marseille` returns FAIL marker for SEO title length warnings only (no errors); exit code 0.
- No em or en dashes anywhere across the 27 files (grep clean).

## Defects total

- A cuisine/cross-check: 4
- A2 specific-fact: 2
- B route: 0
- C festival: 2
- D thin-category: 0
- E echoes: 5 (Tunisian-Femina propagation across 4 files, phantom-festival names in region.json)
- Itinerary day-of-week: 1
- Polish: 4 (Marche d'Aubagne rename, Place Comtales -> Place des Precheurs, duplicate JSON key, Pain Salvator hours)

K = 18

## Below-floor topics after QA

- None. No entity removals this pass; all defects were rewrites/corrections, all topics stay above floor.

## Verdict

VERDICT: PASS
