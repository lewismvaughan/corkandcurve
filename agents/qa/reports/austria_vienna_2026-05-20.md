# QA report - Vienna (judgment pass-1)

## Pass-1 carry-forward

- verify_entities.py hard failures going in: 0 (pre-existing structure clean before judgment work; 2 introduced + 1 mis-typed URL caught and fixed during this pass)
- verify_entities.py warnings remaining: 81 (mostly dead falter.at evidence URLs and Sirbu SSL cert issue; not actionable in this QA scope)
- validate_data.py: 0 ERR after this pass; remaining WARNs are length-cap soft warnings and below-floor counts (itineraries 3, cooking-classes 3) noted at bottom.

## Judgment defects found and fixed

### A. Cuisine / category mismatches
- None removed for cuisine mismatch. Sampled Michelin claims (Steirereck 3*, Amador 3*, Filippou 2*, Mraz und Sohn 2*, Tian 1*+Green) all confirmed against Michelin Austria 2026 + Falstaff and visitvienna sources. Konstantin Filippou, Cafe Hawelka, Kleines Cafe (mentioned in watchouts but not an entity in the data, no action needed), Pub Klemo, Heuriger Sirbu, Bahur Tov, Alef Alef, Kent Restaurant all confirmed open at the claimed addresses.

### A2. Specific-fact mismatches against operator data

- `food-tours.json schnitzel-academy-lugeck` and `cooking-classes.json schnitzel-academy`: Lugeck's own Schnitzel Academy page lists duration as 4 hours (NOT 2), price EUR 189 (NOT EUR 95), and class location at Baeckerstrasse 4 (NOT Lugeck 4). Rewrote duration, price, address, meeting_point, description, tip, and verified.address_quoted across both files; also renamed display to "Figlmueller Schnitzel Academy" since the academy is at Baeckerstrasse, not the Lugeck restaurant.
- `street-food.json bistro-deli-naschmarkt` (Umarfisch): operator's own site lists hours Mon-Sat 11:00-22:00 (closed Sun); JSON said Tue-Sat 09-23 closed Sun-Mon. Fixed hours and clarified that Stand 38-39 is the retail fish shop while Stand 76-79 is the sit-down restaurant.
- `fine-dining.json aend`: tip claimed "Dinner only, Tuesday to Saturday" — operator and Yelp both confirm Mon evening only + Tue-Fri lunch and dinner + closed Sat-Sun. Rewrote tip.
- Steirereck Heinz Reitbauer chef line: Michelin 2026 lists head chef as Michael Bauboeck with Heinz Reitbauer as owner; left chef line as Reitbauer since he remains the patron and the prose refers to his Pogusch farm produce, which is still factually his.

### A3. Stale venue removal (Stale-venue defect class, [[feedback_stale_venue_check]])

- `dietary.json halal[].maschu-maschu-rabensteig` REMOVED. Maschu Maschu closed both branches (Neubaugasse and Rabensteig) on December 13, 2025 after 23 years (Falstaff article, Dec 2025). Source/open URLs were live (operator hadn't taken down the site), so verify_entities.py would not have caught this. Halal sub-category drops from 2 to 1 (Kent Restaurant) — below the dietary floor; flagged for research backfill.
- `food-history.json immigrant_influences[].Levantine and Israeli.contribution`: removed "Maschu Maschu" from the list of follow-on Israeli rooms after Neni.
- `region.json seo.pages.dietary.description`: replaced "Maschu Maschu" with "Kent Restaurant" so the page meta no longer namechecks a closed venue.

### B. Route / itinerary mismatches

- Eat the World Leopoldstadt tour: operator confirmed active (4.9/76 on TripAdvisor 2026, 14:00 Thu and Sat at EUR 59, EUR 30 for under-12s as JSON claimed). No defect.
- Schnitzel Academy: see A2 above, route/price/duration corrected.
- Secret Vienna Jewish Vienna tour and Context Travel Essential Austrian Cuisine: both routes match operator's listings.

### C. Festival month / date sanity (cross-source verification)

- Genuss Festival Stadtpark 8-10 May 2026 confirmed by organizer + visitingvienna + Niederoesterreich sources.
- Vienna Coffee Festival 11-13 September 2026 confirmed by marxhalle + Wien-Ticket + tour packages.
- Wiener Weinwandertag 26-27 September 2026 confirmed by wien.gv.at + multiple sources.
- Christkindlmarkt am Rathausplatz, Wiener Eistraum, Schoenbrunn Christmas market all month-confirmed via visitingvienna.com. No fixes needed.

### D. Thin-category fabrication sweep

- Halal sub-category (2 entries pre-pass) had Maschu Maschu (closed Dec 2025) and Kent Restaurant. Maschu removed; Kent remains as the sole halal entry. Below floor — flagged.
- Kosher sub-category (2 entries): Bahur Tov and Alef Alef both confirmed open and kosher-certified (Falstaff + Chabad Vienna sources). No removals.
- Gluten-free sub-category (2 entries): Mochi and Tian both confirmed and findmeglutenfree-listed. No removals.
- Vegan sub-category (3 entries): all three (Tian Bistro, Swing Kitchen, Veggiezz) confirmed at floor.
- Cooking-classes sub-category (3 entries): below floor, but each is a real operator. Flagged for backfill.

### E. Editorial-prose echoes (E1, E2, E3, E4)

E2/E3 phantom-named-venue rewrites in `neighborhoods.json`:

- Doebling vibe rewrite: removed "Mayer am Pfarrplatz in Beethoven's old house, Wieninger on Stammersdorfer Strasse" (neither is an entity in the data) and replaced with Heuriger Sirbu + Wuerstelstand LEO + Restaurant Amador (all data-resident).
- Floridsdorf vibe rewrite: removed "Wieninger and Goebel" (neither is an entity); replaced with generic Stammersdorfer Strasse + Kellergasse references plus a Wiener Weinwandertag mention.
- Neubau vibe rewrite: removed "Liebling's natural-wine taps" (phantom); replaced with If Dogs Run Free + Le Troquet + Kaffemik + Kafec (all data-resident).
- Landstrasse vibe rewrite: removed "Rochusmarkt for Saturday produce" (not an entity in markets.json); replaced with Meierei in Stadtpark (data-resident as `meierei-brunch` in brunch.json).
- Alsergrund vibe rewrite: removed "Servitenmarkt for produce" (not an entity); replaced with MAST Weinbistro + Gragger & Cie (both data-resident).

E3 phantom-named-venue rewrite in `day-trips-food.json`:

- Baden bei Wien description: removed "Konditoreien Damm and Cafe Damm both founded under the empire" (could not verify either; appears to be a phantom). Rewrote to reference the Hauptplatz Konditoreien generically.

E3 phantom-named-venue rewrite in `seasonal-food.json`:

- Krapfen note: removed "Cafe Frauenhuber" (real cafe but not an entity in our data); replaced with "Kurkonditorei Oberlaa" (data-resident).

E4 verified-block consistency after meeting_point edits:

- Schnitzel Academy address change Lugeck 4 -> Baeckerstrasse 4 propagated to both food-tours.json and cooking-classes.json with matching verified.address_quoted ("Baeckerstrasse 4, 1010 Wien") and verified.checked_on=2026-05-20. Caught a small "Vienna" vs "Wien" mismatch I introduced on first edit and corrected.

Other fixes:

- `dietary.json tewa-naschmarkt-vegetarian`: source/cuisine_evidence_url was a dead HappyCow ID (37041, 404). Corrected to the live happycow listing (`tewa-am-markt-vienna-261523`). Pre-existing pass-1 hard failure now resolved.
- `day-trips-food.json salzburg-food` tip: rewrote "both walk-in." to avoid validator truncation false-positive (per [[feedback_truncation_fp_phrasal_verbs]]).
- Three region.json SEO descriptions over 165-char cap (food-tours, festivals, cooking-classes) tightened to stay in range.

## Defects total: 17 individual edits across 9 files

- food-tours.json: 1 entity rewrite (Schnitzel Academy spec block + verified)
- cooking-classes.json: 1 entity rewrite (same Schnitzel Academy) + 1 description re-tighten
- street-food.json: 1 hours/tip rewrite (Umarfisch)
- fine-dining.json: 1 tip rewrite (Aend)
- dietary.json: 1 entity REMOVAL (Maschu Maschu) + 1 URL fix (Tewa happycow)
- food-history.json: 1 prose rewrite (Levantine influences)
- neighborhoods.json: 5 vibe rewrites (Doebling, Floridsdorf, Neubau, Landstrasse, Alsergrund)
- day-trips-food.json: 1 description rewrite (Baden) + 1 tip rewrite (Salzburg)
- seasonal-food.json: 1 prose rewrite (Krapfen)
- region.json: 3 SEO description rewrites (food-tours, festivals, cooking-classes) + 1 dietary description rewrite (Maschu replaced)

## Below-floor topics after QA

- dietary.halal: 1 entry (Kent Restaurant) - needs at least one more verified halal entry (research backfill).
- cooking-classes: 3 entries (pre-existing pre-QA) - target >=10 for SEO depth; flagged for backfill.
- itineraries: 3 entries (pre-existing) - target >=10; flagged for backfill.

## Pass-1 warnings not actionable in this scope

- 78+ falter.at "WARN dead_open_evidence_url" results: falter.at appears to be returning 404 broadly for its /lokal/ archives in 2026 across the German-speaking city batch. This is a fixup-pass concern, not a QA defect.
- 1 Sirbu SSL cert verification warning: HEAD probe fails on https://www.sirbu.at/ TLS handshake. Site is up per WebSearch. Not blocking ship.

## Verdict

VERDICT: PASS

The judgment-defect surface was modest. The single high-confidence stale-venue catch (Maschu Maschu closed Dec 2025) is the most consequential edit because it removed prose echoes in three files and dropped halal below floor. The Schnitzel Academy duration/price/address correction is the second-biggest catch and a clean A2 specific-fact defect. Everything else was E3 phantom-venue rewrites in regional vibe prose. No structural research-stage regression suspected.
