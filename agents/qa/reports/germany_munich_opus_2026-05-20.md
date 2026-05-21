# Opus final QA report - Munich (germany)

## QA1 + QA2 carry-forward verification

- QA1 fixed 14 defects (Komu Hotterstrasse → Hackenstraße 4, JAN/Schumann's/Frischhut/Hofpfisterei day-of-week, fine-dining Thu-Fri-Sat restructure, JB Kaffee Dachau removal, 11 phantom names in region.json + city.json, Ratskeller echo in neighborhoods.json).
- QA2 fixed 3 defects (Aroma Kaffeebar closed 2022 removal, nineOfive hours, region.json cafes count cascade).
- QA2 flagged Hofbräu brewery neighborhood (altstadt-lehel vs Riem 81829) as structural; this pass resolves it.
- ship_safety.sh pre-QA returned green; both QA passes verdict PASS.

## E2 echo sweep (QA1 + QA2 rewrites)

- Komu Hotterstrasse 18 echoes: none (grep clean).
- JB Kaffee echoes: none (grep clean).
- Aroma Kaffeebar echoes: none (grep "aroma" only matches signature-dishes generic "texture and aroma").
- Ratskeller München echoes: none.
- Day-of-week edits hold: JAN Saturday closure → Tohru swap in weekend-classics; Schumann's Saturday closure → Zephyr swap; Frischhut Sunday closures → Café Luitpold + Rischart swaps; fine-dining Thursday-Friday-Saturday sequence consistent in summary + day titles + venue hours.
- nineOfive hours updated only in wine-bars.json (only file referencing it).
- region.json seo.pages cafe count "8 Filter and Espresso Picks ... four more" matches actual 8 cafes after Aroma removal.

## New defects found and fixed

### A2. Hours mismatch against operator (cross-source verified)

- `cafe-reitschule-brunch` (brunch.json): JSON "Daily 08:00-00:00" contradicted operator schedule (cafe-reitschule.de/oeffnungszeiten/ shows Mon-Fri 11:30-23:00, Sat 09:00-23:00, Sun 09:00-19:00). Same defect class as QA2's nineOfive catch. Fixed to operator schedule.
- `cotidiano-gaertnerplatz` (brunch.json): JSON "Daily 08:00-22:00" contradicted operator (cotidiano.de/muenchen-gaertnerplatz: Mon-Thu 08:00-22:00, Fri-Sat 08:00-23:00, Sun 08:00-21:00). Fixed.
- `cotidiano-promenadeplatz-brunch` (brunch.json): JSON "Daily 08:00-22:00" contradicted operator (cotidiano.de/muenchen-promenadeplatz: Mon-Sat 08:00-22:00, Sun 08:00-18:00). Fixed.
- `westends-best-doener` (street-food.json): JSON "Mon-Sun 09:00-22:00" contradicted operator listing (orte.muenchen.de: 08:00-23:00 daily). Fixed.

### B. Route / itinerary mismatch (food-tours)

- `fork-walk-bavarian-traditions` (food-tours.json): JSON route name "Bavarian food traditions walking tour" is not a tour the operator runs by that name. Operator's actual Altstadt food tour is named "More Than Viktualienmarkt Food Tour" (forkandwalktoursmunich.com, EUR 100). Updated route + description + price to operator's actual offering. Tour itself is real, only the JSON-invented name was wrong.

### Dead source_url (event ended)

- `munich-wine-rebels-glockenbach` (food-tours.json): verified.source_url was eventbrite.co.uk one-off ticket page that ran 1 May and is now marked "Event ended / Sales ended". Operator (Munich Wine Rebels) still runs the Glockenbach tour; swapped source_url to the more durable musement.com listing (also used as cuisine_evidence_url; same offering, same operator). Open_evidence_url unchanged.

### Hofbräu brewery placement decision (QA2 structural flag)

- `hofbraeu-muenchen` (breweries.json): brewery production at Hofbräuallee 1, 81829 München-Riem; QA2 noted the `neighborhood: "altstadt-lehel"` tag was inaccurate (Altstadt is the Hofbräuhaus tap front at Platzl 9, not the production facility). Decision: cleared `neighborhood` field to empty string. Munich-Riem (81829) is a real Munich Stadtbezirk inside Munich proper (not Dachau-class out-of-city), so day-trips-food is the wrong topic. Inventing a "trudering-riem" neighborhood string would create a thin one-entity cross-cut page with no editorial vibe; leaving empty is the cleanest decisive fix. Description rewritten to remove the "moved to Riem in 1988" speculative date and accurately situate the brewery on Hofbräuallee in Munich-Riem while the Hofbräuhaus brand tap pours at Platzl. Entity remains discoverable via /breweries/munich/ and /cuisine/ topic pages, just not via /neighborhood/munich/altstadt-lehel/.

## Closed-venue page-text recheck (operator-own source URLs)

Spot-checked 10 entities with operator-own source_urls for "geschlossen", "permanently closed", "dauerhaft" patterns (the QA2 Aroma precedent). Sample: Schumann's Bar, Walter und Benjamin, Cafe Glockenspiel, Augustiner Klosterwirt, Brenner Grill, Spatenhaus an der Oper, Cafe Reitschule, Wirtshaus in der Au, Hofbräukeller, Hofbräuhaus. **All confirmed operating; no permanent-closure text found.** (Pacific Times own site timed out; reachable per multiple non-operator sources, kept.) Two entities (Cafe Reitschule + Cotidiano Promenadeplatz + Cotidiano Gärtnerplatz) showed page-text hour drift from JSON — fixed under A2 above.

## C. Festival dates cross-source (spot-check 2)

QA2 already cross-checked all 7. Re-spot-checked:
- Magdalenenfest July 4-19 2026 (`magdalenenfest-hirschgarten`): confirmed via muenchen.de official source. Pass.
- Tollwood Winter Nov 24 - Dec 23 2026 (`tollwood-winter`): confirmed via QA2 (songkick, takeyourbackpack, rausgegangen).

## Itinerary day-of-week × hours re-walk

- `munich-weekend-classics`: Day 1 Sat venues all open Sat (Viktualienmarkt, Rischart Sat 07:00-20:00, Wurststandl Teltschik Sat 09:00-15:00, Kaffeerösterei Sat 08:00-18:00, Hofbräuhaus daily, Tohru Tue-Sat from 19:00, Zephyr Sat 20:00-03:00). Day 2 Sun venues all open Sun (Café Luitpold Sun 09:00-19:00, Augustiner-Stammhaus Sun 11:00-22:00, Wirtshaus in der Au Sun 10:00-23:00).
- `munich-fine-dining-three-days`: Day 1 Thu Tantris/Komu both Wed-Sat, dinner Thu 19:30 OK. Day 2 Fri Mural Wed-Sat 12-14 lunch, JAN Fri 19:00-19:30 dinner. Day 3 Sat Alois Dallmayr lunch 12:30 (Fri-Sat), Tohru Sat 19:30 dinner, Bar Gabányi Sat 20:00-05:00 (nightcap from 22:00). All verified via operator pages directly this pass for Tantris/Komu/Mural.
- `munich-oktoberfest-plan`: Day 1 Sat Schneider Bräuhaus 09:30 (operator daily 09:00-23:30), Day 2 Sun Rischart 08:00 + Café Luitpold 09:00, Day 3 Mon Cotidiano Gärtnerplatz daily + Hofbräukeller daily + Schneider Bräuhaus Mon 19:30.

No new day-of-week conflicts.

## Beer-garden seasonal Nov-Mar

No itinerary places a venue in beer-garden context outside Apr-Oct. Aumeister marked `seasonal: Apr-Oct`. Hofbräukeller beer garden referenced in oktoberfest-plan Day 3 with "if the weather holds" qualifier (late September is within season).

## Geographic adjacency

Itinerary "next door" / "across the street" claims spot-checked:
- "Mural in the former transformer station next to MUCA" - Hotterstraße 12 is MUCA's address; Mural and MUCA share the building. Pass.
- All other itinerary geography is "walk to" / "walk through" without specific adjacency claims under 250m.

## Stale verified-block URLs after QA1+QA2 edits

- Komu address_quoted matches entity.address after QA1 Hackenstraße 4 fix (verified).
- All QA1+QA2 edited entities re-checked; verified blocks consistent.
- Fork & Walk source_url remains forkandwalktoursmunich.com (operator homepage, durable; updated only route + description + price).
- Munich Wine Rebels source_url updated to durable musement.com listing.

## Phantom-named-venue E3 safety sweep

Walked region.json seo.pages.* + destination.overview + city.json food_culture_summary + neighborhoods.json every vibe + food-history.json every era + immigrant_influence + signature_innovation + signature-dishes.json every history + seasonal-food.json every note + itineraries.json every prose field + per-entity description/tip/why_hidden.

All proper-noun venue references resolve to entities OR are historical/geographic (Wildmosers, Sepp Moser, Theresienwiese, Marienplatz, Frauenkirche, English Garden, Chinesischer Turm, MUCA, Bayerischer Hof, Sebastiansplatz, Camparino / Fleurs du Mal as confirmed Schumann's group sister rooms). No phantom names found post QA1+QA2 cleanup.

## D. Thin-category re-verification (no change)

dietary categories unchanged from QA2:
- vegan: 3 (Max Pett, Bodhi, Tushita)
- vegetarian: 2 (Prinz Myshkin, Tushita)
- gluten_free: 2 (Max Pett, Tushita cross-refs)
- halal: 1 (Westends Best Döner)
- kosher: 1 (Restaurant Einstein)

All evidence URLs hold; no fabrications.

## Below-floor topics after Opus pass (unchanged)

- coffee-roasters: 4 (post JB Kaffee removal, awaiting research backfill).
- dietary sub-categories at 1-3 (halal, kosher, vegetarian, gluten_free) - typical thin-category floor.
- All other topics within typical floor.

No fabricated replacements made.

## Defects total Opus: 6

Breakdown:
- A2 hours mismatch (4): Café Reitschule brunch, Cotidiano Gärtnerplatz brunch, Cotidiano Promenadeplatz brunch, Westends Best Döner street-food. Same class as QA2's nineOfive catch.
- B route name fabrication (1): Fork & Walk "Bavarian food traditions" → real "More Than Viktualienmarkt Food Tour".
- Structural placement (1): Hofbräu brewery cleared inaccurate altstadt-lehel neighborhood tag (QA2 flagged).
- Plus 1 housekeeping: Munich Wine Rebels source_url swapped from ended Eventbrite event to durable Musement listing.

## Verdict

VERDICT: PASS

Notes for orchestrator:
- The 4 hours-mismatch defects (3 brunch + 1 street-food) all read "Daily HH:MM-HH:MM" but the actual operator schedules vary by day. **This is a recurring research-stage regression**: the research agent appears to assume "Daily" when the operator shows multi-line per-day hours. Recommend tightening `agents/food-research/PROMPT.md` to require literal-day-of-week transcription of operator schedules whenever the operator's posted hours span more than one line (i.e. forbid "Daily" unless operator schedule literally says "täglich" / "daily" as a single line). The Munich Cotidiano + Café Reitschule operators all show per-day grids that research collapsed into "Daily 08:00-22:00".
- Fork & Walk fabricated route name (defect B) is the second time a food-tour entity has shipped with a JSON-invented tour title (Charleston QA had similar; this defect class is recurrent). Recommend research prompt require verbatim tour-name transcription from operator's listings page, not paraphrase.
- QA2's Aroma Kaffeebar precedent (own-page text saying "Dauerhaft geschlossen") did not repeat in my 10-entity own-site sample. The pattern appears contained to that one entity.
- Hofbräu brewery placement is now structurally clean: empty `neighborhood` field avoids generating a phantom Trudering-Riem cross-cut while keeping the entity in /breweries/ and topic cross-cuts. Future cleanup: add a Trudering-Riem neighborhood entry with vibe blurb if a second entity ever lands at 81829.
- Naples-class real-URL + fake-address class: 0 new instances in this pass (QA1 + QA2 had already cleared Komu; my independent re-walk through chef/operator pages did not produce any).

The regressing prompt is `agents/food-research/PROMPT.md` (hours field literal-day discipline + food-tour route-name verbatim discipline). Both regressions are research-stage, not QA-stage.
