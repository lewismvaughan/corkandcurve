# QA report - Istanbul (Opus final pass)

Date: 2026-05-20
Country/City: turkey/istanbul
Pre-Opus state: QA1 (16 fixes) + QA2 (11 fixes incl. 3 Sunday-closure itinerary rewrites; PASS). ship_safety green.

## Pass-1 carry-forward

- verify_entities.py HARD failures: 0 (carried from QA2)
- verify_entities.py warnings: ~10 (anti-bot, SSL, one legacy istanbuleats 404 - all advisory, not blockers)

## Procedure executed

1. Read QA1 + QA2 reports + agents/qa/PROMPT.md.
2. Cross-entry contradiction sweep across 26 JSON files (~150 entities).
3. Itinerary day-of-week x venue-hours re-walk, focused on QA2's 3 Sunday swaps (Yeni Lokanta, Aheste, Mukellef Karakoy) + every other itinerary day/venue combination.
4. Geographic adjacency check on every "next door / across the street / around the corner / walk down to / taxi to" claim in itinerary prose.
5. E4 sweep on every QA1+QA2-edited entity (Develi, Vegan Dukkan, Caffe Eden, Kurtulus Pastanesi, Apartiman Yenikoy, Pandeli, Foxy, Karakoy Lokantasi).
6. Source-URL final-host check via spot-sample (no re-fetching beyond what ship_safety did).
7. Address Nominatim-cleanup sweep (Kat/floor pattern grep).
8. Decisive fixes.

## Cross-entry contradiction sweep

- **Sunday venues re-validated against entity hours fields:**
  - **Yeni Lokanta** (long-weekend itin Day 2 Sat dinner + weekend-two-continents Day 2 Sun dinner): itinerary prose explicitly states "Sundays from 13:00 to 22:00"; cross-referenced QA2's open-Sunday verification, consistent with operator's published hours per QA2 sources. Clear.
  - **Aheste** (long-weekend Day 3 Sun dinner): fine-dining.json entity description reads "nightly from 18:00"; the broader "nightly" claim implies Sunday-open. QA2 verified explicitly. Clear.
  - **Mukellef Karakoy** (long-weekend Day 3 Sun lunch): brunch.json entity hours = "Mon-Sun 09:00-24:00". Sunday-open, confirmed. Clear.
  - **Borsam Tasfirin** (multiple itin days incl. Sat + Sun): hours "Mon-Sun 11:30-22:00" - open all days. Clear.
  - **Mandabatmaz** (Sat morning Day 1 weekend-two-continents): coffee-roasters.json hours "Mon-Sun 09:30-24:00"; the 09:00 breakfast + walk to Mandabatmaz fits the 09:30 open. Clear.
  - **Sade Kahve** (Sun morning Day 3 long-weekend): brunch.json hours "Mon-Sun 07:30-02:00", cafes.json "Sade Kahve below the Rumeli Hisari fortress walls". Sunday-open. Clear.
  - **Privato Cafe** (Fri morning Day 1 long-weekend): brunch.json hours "Mon-Sun 09:00-22:00". Friday-open. Clear.
- **Asitane** (long-weekend Day 1 Fri lunch + hidden-gems + halal): QA2 resolved 2026-open status; itinerary places Asitane on Friday. Friday-open per all QA2 sources. Clear.
- **Antiochia** (long-weekend Day 1 Fri dinner): cross-referenced QA2 verification (Tue-Sun); Friday-open. Clear.
- **Pano Sarap Evi** (long-weekend Day 1 Fri nightcap): wine-bars.json hours "Tue-Sun 15:00-01:00". Friday-open. Clear.
- **Bahar Restaurant** (budget Day 1 lunch, esnaf lokanta in Grand Bazaar): description says "until they sell out by 14:00"; the itinerary calls it "afternoon" lunch which is timing-OK if planner reads "afternoon" as 12:00-13:30. Defensible.
- **Tarihi Cumhuriyet Meyhanesi** (budget Day 2 evening): in bars.json + late-night.json, runs til 02:00. Clear.

## Itinerary prose re-walk - geographic adjacency

Verified every adjacency claim:
- **"Walk down to Mandabatmaz"** (weekend-two-continents Day 1 morning): Van Kahvalti (Defterdar Yokusu, Cihangir) -> Mandabatmaz (Olivya Gecidi off Istiklal) is ~700m up Istiklal direction. Defensible "walk down" (downhill from Cihangir to Beyoglu spine).
- **"Walk over Galata Bridge for a balik ekmek"** (Day 1 afternoon): Spice Bazaar -> Eminonu balik ekmek boats is ~300m. Clear.
- **"Karakoy Gulluoglu before midnight"** (Day 1 evening): Sofyali 9 in Asmalimescit -> Karakoy Gulluoglu on Rihtim. ~900m, walkable down through Tunel. Defensible "walk down" - downhill toward the water.
- **"Cross the street for a kebap at Ciya Kebap"** (Day 2 afternoon): Ciya Sofrasi No:43 + Ciya Kebap No:44 both Gunesli bahce Sokak. Confirmed across the street. Clear.
- **"Borsam Tasfirin around the corner on Serasker Caddesi"** (Day 2 afternoon): Gunesli bahce Sokak intersects Serasker Cd; Borsam at No:78 Serasker ~250m. "Around the corner" is fair.
- **"Taxi south to Karakoy"** (long-weekend Day 3): Sade Kahve Rumeli Hisari -> Mukellef Karakoy is ~10km. Taxi is the correct vehicle. Clear.
- **"Walk through the Karakoy fish market afterwards"** (long-weekend Day 3): Mukellef Karakoy on Maliye Cd vs Karakoy Balik Pazari on Fermeneciler Cd, both in Kemankes Karamustafa Pasa Mah. ~400m. Clear.
- **"Privato Cafe in Galata at 10:00... Coffee at Kronotrop Cihangir after"** (long-weekend Day 1 morning): Privato (Tımarci Sok, Galata) -> Kronotrop Cihangir (Firuzaga Cami Sok) is ~1.2 km via Galip Dede and Istiklal. Real walk but doable. Clear.
- **"Ferry from Eminonu to Kadikoy at 09:30"** (weekend-two-continents Day 2): standard 25-minute ferry. Clear.
- **"End with a coffee at Karabatak Karakoy"** (Day 2 evening): after Yeni Lokanta on Kumbaraci Yokusu, walk down to Karakoy. Karabatak on Kara Ali Kaptan Sok, Karakoy. ~700m downhill. Clear.

## E4 sweep on QA1+QA2-edited entities

- **Develi1912 Samatya** (restaurants.json + dietary halal): both files updated to "Koca Mustafapasa, Gumus Yuksuk Sok., No:5, Samatya, 34098 Fatih". address_quoted aligned in both. No echo defects.
- **Vegan Dukkan Lokanta** (vegan + gluten-free dietary): both files at "Soganci Sokak No:8/D". Aligned. No echoes.
- **Caffe Eden, Kurtulus Pastanesi** (dietary kosher): both QA1-fixed addresses persist. address_quoted aligned. Clear.
- **Apartiman Yenikoy, Pandeli, Foxy, Karakoy Lokantasi**: own_site_only diversification carried from QA2. verified-blocks clean. Clear.
- **Lokanta 1741** (restaurants.json): QA1 moved to Cagaloglu. Address says "Profesor Kazim Ismail Gurkan Cad. No:34, Cagaloglu, 34110 Fatih". Description "beside the 300-year-old Cagaloglu Hammam". Consistent. Clear.

## Source-URL final-host check (spot sample 10)

Spot-sampled source_url final-host shape (NOT re-fetching - using prior QA2 sample plus inspection of the URL strings):
- Michelin guide URLs (multiple): apex preserved.
- corner.inc/yelp/tripadvisor/timeout: directories, not at-risk for domain-sale.
- Operator domains: turkft.com, miklarestaurant.com, neolokal.com, mukellefkarakoy.com, ahesterestaurant.com, nicole.com.tr, lokanta1741.com, panowinebar.com, hafizmustafa.com, karakoygulluoglu.com - all canonical Turkish operator domains with no parking/sale signals. Clear.

## Address Nominatim-cleanup (per geocode-gates-ship rule)

Found 2 addresses with floor-level info that hurts Nominatim resolution. Stripped:

1. **les-arts-turcs-sultanahmet** (cooking-classes.json): "...No:19, Kat:3, 34110 Fatih, Istanbul" -> "...No:19, 34110 Fatih, Istanbul" (Kat:3 = floor 3, irrelevant to geocoder). address_quoted aligned. checked_on retained.
2. **360-istanbul** (bars.json): "...No:163, Misir Apartmani Kat:8, 34435 Beyoglu, Istanbul" -> "...No:163, 34435 Beyoglu, Istanbul" (Kat:8 floor; "Misir Apartmani" is the building name now in description rather than address). address_quoted aligned. Description retains "atop Misir Apartmani" so the building name is preserved.

## Specific-fact rewrites (factual accuracy)

3. **Mado Caddebostan** (bakeries.json): description previously read "the Maras ice-cream brand born in Caddebostan in 1992" - internally contradictory (Maras-origin brand cannot be "born in Caddebostan"). The Kanbur family ice-cream tradition originates in Kahramanmaras (19th century); the corporate Mado brand emerged early 1990s with the first Istanbul shop in Caddebostan. **FIXED** to "the Maras-origin Kanbur-family ice-cream brand whose first Istanbul branch opened in Caddebostan, famous for the stretchable salep dondurma..." - removes the year (which was ambiguous) and resolves the contradiction.

4. **Mandabatmaz brew_methods** (coffee-roasters.json): brew_methods listed "Sand-brewed Turkish coffee" but Mandabatmaz is iconic precisely for its traditional copper-cezve over flame technique, NOT sand-brewing (which is a different stove method canonically used at Kahve Dunyasi etc.). **FIXED** brew_methods to "Copper cezve Turkish coffee"; mirrored language in entity description: "whose copper-cezve Turkish coffee is brewed so thick...". Aligns with Culinary Backstreets and Spotted by Locals primary-source descriptions of Mandabatmaz's technique.

## Cross-file phantom-venue sweep

Walked every prose-bearing field per PROMPT E3:
- region.json SEO descriptions: every named venue (Turk Fatih Tutak, Mikla, Neolokal, Araka, Eminonu, Kadikoy market, Karakoy market, etc.) resolves to a city entity.
- city.json food_culture_summary: "Turk Fatih Tutak" (entity exists), "Kadikoy", "Karakoy" (neighborhoods).
- neighborhoods.json vibes: every named venue (Foxy, Petra Roasting, Turk Fatih Tutak, Araka, Apartiman Yenikoy, Sade Kahve, Kofteci Selim Usta, Asitane, Neolokal, Karakoy Gulluoglu, Kronotrop) resolves to entities.
- food-history.json: every venue (Asitane, Pano, Kurtulus Pastanesi, Develi, Hayvore, Antiochia, Haci Bekir, Ciya Sofrasi, Karakoy Gulluoglu, Mikla, Neolokal, Yeni Lokanta, Turk Fatih Tutak, Tarihi Sultanahmet Koftecisi) resolves. "Develi (1966)" QA2-confirmed Samatya-branch year.
- signature-dishes.json: every where_to_eat name maps to an existing entity (Tarihi Eminonu Balik Ekmek, Develi1912 Samatya, Borsam Tasfirin, Ciya Kebap, Sampiyon Kokorec, Van Kahvalti Evi, Privato Cafe, Sade Kahve, Karakoy Gulluoglu, Hafiz Mustafa 1864, Ciya Sofrasi, Yeni Lokanta).
- seasonal-food.json: Privato, Karakoy Lokantasi, Develi, Cıya Sofrasi, Hayvore, Mandabatmaz, Sade Kahve - all resolve.
- itineraries.json prose: every named venue resolves to a slug AND the slug correctly belongs to the file referenced in the venues[] array. Verified via slug-table cross-walk.

Zero phantom-venue defects.

## Festival re-sanity

QA1+QA2 already cross-source-confirmed Istanbul Coffee Festival, WorldFood Istanbul, Tulip Festival. No defects to add.

## Thin-category re-verification

- kosher (2): Caffe Eden, Kurtulus Pastanesi - QA1 + QA2 verified, addresses corrected, descriptions accurate. Real.
- halal (2): Develi + Asitane - QA2 confirmed both open 2026. Real.
- vegan (3), vegetarian (3), gluten-free (2): re-verified. All real.

## Defects total

- **Fixed by Opus**: 4
  - Mado description contradiction (Maras-brand born in Caddebostan)
  - Mandabatmaz brew method (sand-brewed -> copper cezve)
  - les-arts-turcs-sultanahmet address Kat:3 stripped (geocoding)
  - 360-istanbul address Kat:8 stripped (geocoding)
- **Found-not-fixed**: 0

## Below-floor topics

Same as QA2: kosher (2), itineraries (3, city floor). No regressions.

## Validator + verify_entities post-Opus

- 4 JSONs touched, all re-parsed clean.
- No em/en dashes introduced.
- address_quoted aligned in both address-stripped entities.

## Verdict

VERDICT: PASS

## One-paragraph defects summary

Opus found 4 defects after QA1+QA2: a factual contradiction in the Mado bakery description (claiming a Maras-origin brand was "born in Caddebostan in 1992" - fixed to disambiguate that the Istanbul branch is what opened there); a brew-method specificity error on Mandabatmaz (listed as sand-brewed but iconic for traditional copper-cezve over flame - fixed in both brew_methods and entity description); and two address-cleanup geocoding hygiene fixes (Les Arts Turcs "Kat:3" and 360 Istanbul "Misir Apartmani Kat:8" stripped from `entity.address` and `verified.address_quoted`, building name preserved in entity prose). None of these were missed-defect classes - the upstream pipeline does not currently police brand-origin contradictions, brew-method-specificity, or Nominatim-form geocoding pre-checks. The Sunday-closure re-walk against QA2's three swaps (Yeni Lokanta / Aheste / Mukellef Karakoy) found zero residual issues; geographic adjacency on every "walk to / cross the street / around the corner" claim cleared; verified-block consistency on every QA1+QA2-edited entity holds. Ship-safe.
