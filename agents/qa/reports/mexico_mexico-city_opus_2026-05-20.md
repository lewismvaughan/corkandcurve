# QA report — Mexico City (Opus final pass)

Scope: site-data/mexico/mexico-city/data/*.json
Date: 2026-05-20
Builds on QA1 (23 fixes) + QA2 (17 edits).
- /station/repo/agents/qa/reports/mexico_mexico-city_2026-05-20.md
- /station/repo/agents/qa/reports/mexico_mexico-city_qa2_2026-05-20.md

## Pass-1/QA1/QA2 carry-forward

- All QA1 + QA2 decisive fixes verified intact on disk.
- check_internal_references.py: ERR=0 WARN=0 across 140 names / 167 slugs.
- validate_data.py: exit 0 (length WARNs only, pre-existing agent voice).
- 81 address_quoted "synced to entity.address" entries: still flagged for next research-stage pass (QA1 noted, no ship-safety impact).

## Opus judgment defects found

### E1 / E2. Editorial-prose echoes after QA2 removals + renames

- **region.json `seo.pages.wine-bars.description`**: still listed "Tintoque" (REMOVED in QA2 as Puerto Vallarta venue falsely claimed in CDMX) and "Mia Domenica" (corrected to "Mia Domenicca" with double-c in QA2). FIXED to: "Loup Bar, Mia Domenicca, Felina, Blanco Colima."
- **region.json `seo.pages.breweries.description`**: listed "Cerveceria Hercules" (NOT an entity in breweries.json -- Hercules is a Queretaro brewery, not CDMX) and "Tasting Room" (QA2 renamed slug to Morenos Tasting Room). FIXED to: "Cru Cru taproom in La Romita, Falling Piano Brewing Co, Morenos Tasting Room and El Deposito multi-tap beer halls."
- **region.json `seo.pages.cooking-classes.description`**: said "Mexico Soul and Essence in Coyoacan" but QA1 corrected the venue to Condesa (Amsterdam 269), not Coyoacan. FIXED to reference Mexican Home Cooking School in Coyoacan (which IS the verified Coyoacan cooking class entity).

### E3. Phantom-venue editorial sweep

- **day-trips-food.json `valle-de-bravo`**: claimed "Cerveceria Hercules taproom on the malecon" -- Cerveceria Hercules is a Queretaro brewery, not in Valle de Bravo. Phantom-venue placement. FIXED `signature` + `description` to reference Saturday market trout and craft beer terraces generically without the Hercules misattribution.

### B/Itinerary. Hours / day-of-week × venue contradiction

- **itineraries.json `mexico-city-michelin-three-days` day 3 evening**: prose said "Late dinner at Contramar: tuna tostada and the talla" but Contramar is **lunch-only** (operator's own tip: "Open lunch only; arrive by 13:00"). Same defect class as Esther's bombolini Vegas QA2. FIXED: late dinner moved to Lardo (Elena Reygadas Condesa, daily 08:00-23:00), prose + venues[] both updated.

### Geographic adjacency

- **itineraries.json `mexico-city-weekend-classics` day 1 evening**: "After dinner walk to Hanky Panky or Handshake Speakeasy in Juarez" from Pujol (Tennyson 133, Polanco). Pujol-to-Juarez is ~4-5 km, NOT a walk. SOFTENED to "After dinner cab south to..."
- Other "walk to" claims in the itineraries reviewed (El Huequito -> Buna ~2.5km, Em -> Hanky Panky ~1.5km, Mercado de San Juan -> Plaza Garibaldi ~1km, El Cardenal -> Mercado de San Juan ~700m) all within the upper-end-but-defensible walking range. No further edits.

### Neighborhood-vs-address mismatches

- **bars.json `la-no-10`**: `neighborhood: "centro-historico"` but address is "Calle Marsella 33, Juarez, Cuauhtemoc, 06600" -- Marsella is in Juarez. FIXED neighborhood to "juarez". Description already said "Juarez cantina" (so internally consistent now).
- **restaurants.json `nicos`**: `neighborhood: "miguel-hidalgo"` but address is "Av. Cuitlahuac 3102, Clavería, Azcapotzalco, 02080" -- Azcapotzalco is a different alcaldía from Miguel Hidalgo. FIXED to "azcapotzalco" (matches the fine-dining.json `nicos` entry's neighborhood).

### A2. Specific-fact match (Michelin Bib Gourmand)

- **signature-dishes.json `tuna-tostada` history**: claimed "The 2024 Michelin Guide recognised Contramar as a Bib Gourmand recommendation." Contramar is listed in the Michelin Guide Mexico City selection but is NOT confirmed as a Bib Gourmand (the QA1 caught Esquites Don Fermin's false Bib Gourmand claim already; same pattern). SOFTENED to "Contramar is recognised in the 2024 Michelin Guide Mexico City selection" -- factually defensible without the Bib Gourmand-specific claim that I could not verify.
- (Verified: Los Cocuyos + El Vilsito Bib Gourmand claims are correct and well-documented; left intact.)

### Minor factual correction

- **food-history.json era 3 + immigrant_influences French**: called Maximilian "President" -- Maximilian I was Emperor of the Second Mexican Empire, never president. FIXED both to "Emperor Maximilian" / "Second Mexican Empire under Maximilian".

### Festival 2026 dates re-verified (no defects)

- Mundo Mezcal CDMX Oct 16-18 + La Ola Festival Vegano April 18-19 + Feria del Tamal Jan 29-Feb 2 + Feria Nacional del Mole October + Dia de Muertos Parade Nov 1 + Chiles en Nogada Season late July-early Sep: all match independent 2026 sources.

### Brewery + wine-bar + restaurant + casa-de-tono fixes from QA2 re-verified

All 4 brewery addresses now correct, wine-bar removals + corrections held, Loma Linda + Pasteleria Suiza + Casa de Toño addresses across all referenced files self-consistent, Hanky Panky hours + signature drink correct.

## Defects total: 10 atomic edits

1. region.json wine-bars description (Tintoque + Mia Domenica name)
2. region.json breweries description (Cerveceria Hercules + Tasting Room)
3. region.json cooking-classes description (Mexico Soul and Essence Coyoacan -> correct Coyoacan operator)
4. day-trips-food.json valle-de-bravo Cerveceria Hercules misattribution
5. itineraries.json michelin-three-days day 3 Contramar dinner -> Lardo (hours-mismatch)
6. itineraries.json weekend-classics day 1 evening "walk" to Juarez -> "cab"
7. bars.json la-no-10 neighborhood centro-historico -> juarez
8. restaurants.json nicos neighborhood miguel-hidalgo -> azcapotzalco
9. signature-dishes.json tuna-tostada Bib Gourmand claim softened
10. food-history.json Maximilian "President" -> "Emperor" (x2 fields)

## Below-floor topics

(Unchanged from QA2; no new removals.)
- breweries: 4 entries (floor 6) -- research backfill
- cooking-classes: 4 entries (floor 6) -- unchanged
- itineraries: 4 entries (floor 10) -- unchanged
- dietary.kosher: 2 entries -- unchanged
- dietary.halal: 2 entries -- unchanged
- wine-bars: 6 entries (at floor) -- unchanged
- nightlife.dance_clubs: 1 entry (Patrick Miller restored) -- by-design thin

## Items deliberately NOT chased

- 81 address_quoted "synced to entity.address" -- noted by QA1, no ship blocker; deferred to research pass.
- Length-cap WARNs across ~40 description fields -- pre-existing.
- Mercado Medellin/El Hidalguense/Cumbe etc. neighborhood = "roma-norte" with address "Roma Sur" -- acceptable, no roma-sur slug registered; Roma Sur is part of Cuauhtemoc and falls under the roma-norte slug aliases ["roma-norte", "roma", "cuauhtemoc"]. Geocodes will resolve from the full address.
- La Ola Festival Vegano neighborhood "roma-norte" with Roma Sur address -- same acceptable convention.
- Fonda Margarita neighborhood "del-valle" (not a registered neighborhood slug) -- validator accepts; no resolver failure.
- Restaurants.json El Hidalguense neighborhood "roma-norte" while address is Roma Sur -- same pattern, acceptable.

## Defects summary paragraph

Opus pass caught 10 residual atomic defects after QA1+QA2: three stale SEO descriptions in region.json (wine-bars still listed Tintoque + misspelled Mia Domenica; breweries listed Cerveceria Hercules which is a Queretaro brewery not in our CDMX entity set, and the old "Tasting Room" name; cooking-classes placed Mexico Soul and Essence in Coyoacan after QA1 corrected it to Condesa), one phantom-venue echo (day-trips Valle de Bravo claimed a Cerveceria Hercules taproom that doesn't exist there), one itinerary venue-hours contradiction in `michelin-three-days` day 3 (Contramar served as "late dinner" while Contramar is lunch-only -- replaced with Lardo for the dinner slot to preserve the chef-driven Mediterranean ending), one geographic-adjacency overreach (Pujol Polanco "walk to" Juarez ~4-5 km; softened to "cab"), two neighborhood-address mismatches (La No. 10 was Centro Historico but is at Marsella in Juarez; Nicos was Miguel Hidalgo but is in Azcapotzalco -- the fine-dining.json entry had it correct), one specific-fact softening (Contramar Bib Gourmand claim could not be verified, kept the Michelin selection wording without the Bib Gourmand specificity), and one historical title correction (Maximilian was Emperor, not President). The pattern is the residue you would expect after QA1+QA2 did the heavy address-fab and category-mismatch work: SEO descriptions that reference removed/renamed entities are the most common Opus-pass surface. No fresh fabrications were introduced and no E4 verified-block contradictions were detected; ship_safety.sh should pass cleanly.

## Verdict

VERDICT: PASS

10 atomic edits across 5 files (region.json, day-trips-food.json, itineraries.json, bars.json, restaurants.json, signature-dishes.json, food-history.json). All JSON validates (exit 0). Internal references all resolve (ERR=0 WARN=0). No new below-floor moves. No fabricated replacements.
