# QA2 report - Munich (independent judgment pass-2)

## QA1 carry-forward

- QA1 fixed 14 defects (Komu address rewrite, 5 day-of-week conflicts, fine-dining 3-day restructure, 11 phantom names cleaned in region.json + city.json, JB Kaffee Dachau removal, Ratskeller echo).
- ship_safety.sh prior to QA1 returned green; QA1 verdict PASS.
- QA2 scope: independent-directory cross-check on entities QA1 did not deeply sample, plus Munich-proper boundary check, E2/E3/E4 echoes, festival cross-source, beer-garden seasonality, and itinerary day-of-week × hours re-walk.

## Independent-directory address cross-check (Section A2)

Cross-checked addresses of ~25 Munich entities that were NOT in QA1's deep sample, using Michelin Guide, Falstaff, OpenTable, Yelp, Tripadvisor, geheimtipp-muenchen, mit-vergnuegen, simply-Munich, muenchen.de, fachinternen Falstaff/CremeGuides, mvsm.coffee, vits.coffee, schneider-weisse.de, dallmayr.com, schuhbeck.de.

Confirmed correct (no defect): Alois Dallmayr Fine Dining (Dienerstrasse 14-15), Tantris DNA (Johann-Fichte-Strasse 7), Sparkling Bistro (Amalienstrasse 89 / Türkenstrasse 86a), Gabelspiel (Zehentbauernstrasse 20), Brothers (Kurfürstenstrasse 31), Mural (Hotterstrasse 12), Pageou (Kardinal-Faulhaber-Strasse 10), Broeding (Schulstrasse 9), Brenner Grill (Maximilianstrasse 15), Osteria Italiana (Schellingstrasse 62), Mamma Bao (Augustenstrasse 31), bnb Banh Mi (Parkstrasse 30), Augustiner-Stammhaus (Neuhauser Str. 27), Augustiner-Bräu (Landsberger Strasse 31-35), Giesinger Bräu (Martin-Luther-Strasse 2), Löwenbräukeller (Nymphenburger Str. 2), Schuhbecks Kochschule (Platzl 4a, reopened autumn 2024 confirmed), Bilou Kitchen (Schrenkstr. 13), Genusswerkstatt (Steinstrasse 24), Mangostin Asia (Maria-Einsiedel-Str. 2), Vinzenzmurr (Marienplatz 8), Vits der Kaffee (Rumfordstrasse 49), Standl 20 (Elisabethmarkt 80796), Kaffeerösterei Viktualienmarkt (Stand 3/26), Fausto Kaffeerösterei (Birkenleiten 43, Untergiesing), Man versus Machine (Müllerstrasse 23), Rischart (Marienplatz 18), Cotidiano Promenadeplatz (Maxburgstr. 4), GRAPES Weinbar (Ledererstrasse 8), Pfälzer Residenz Weinstube (Residenzstr. 1), Weinhaus Neuner (Herzogspitalstr. 8), Walter und Benjamin (Rumfordstrasse 6), nineOfive (Herzogstrasse 29), Garibaldi (Burgstrasse 2), Café Reitschule (Königinstrasse 34), Café Glockenspiel (Marienplatz 28 / 5. Stock), Prinz Myshkin (Hackenstrasse 2), Max Pett (Pettenkoferstrasse 8), Bodhi (Ligsalzstrasse 23), Tushita Teehaus (Klenzestrasse 53), Restaurant Einstein (St.-Jakobs-Platz 18), Westends Best Döner (Trappentreustr. 17 confirmed by yelp/orte.muenchen.de/unilocal; joinhalal listing shows "7" but is the only outlier source, address-quoted matches).

Komu's QA1 address fix (Hackenstrasse 4) re-confirmed via operator impressum.

No new fabricated-address defects of the Naples / QA1-Komu class found. The pattern did not extend beyond the Komu instance QA1 caught.

## Defects found and fixed

### A. Closed venue (must remove)

- `aroma-kaffeebar` (cafes): CremeGuides source page marked "Dauerhaft geschlossen" (permanently closed); cross-confirmed via Yelp ("CLOSED"), Foursquare ("Now Closed"), AbendzeitungMünchen ("Aroma Kaffeebar schließt nach 24 Jahren"), Instagram, and a 2022 takeover announcement. Permanently closed 30 June 2022; subsequently replaced by "Luffy Pancake". REMOVED from cafes.json. Drops cafes 9 -> 8.

### A2. Hours mismatch against operator

- `nine-of-five` (wine-bars): JSON hours "Mon-Sat 18:00-00:00" did not match operator schedule. Real hours: Mon-Fri 11:30-14:30 & 17:30-23:00, Sat-Sun 12:00-23:00. Updated hours.

### E. Editorial-prose / SEO cascade fix

- `region.json` `seo.pages.cafes`: title "9 Filter and Espresso Picks" and description "five more" updated to "8 Filter and Espresso Picks" and "four more" to reflect Aroma removal. Cafes still meets typical floor.

## A2 source-URL final-host check (sample)

Final-host check on a sample of source_url fields (operator impressums, brand pages): none redirected to a different registered domain than expected. Schneider Bräuhaus schneider-brauhaus.de → weisses-brauhaus-tal.de (already noted PASS by QA1 - same operator).

## C. Festival month / dates cross-source verification

Cross-checked each of the 7 festivals against at least one non-organizer source. ALL PASS.

- Oktoberfest: Sep 19 - Oct 4 2026 confirmed via munich.travel, muenchen.de, oktoberfest-guide, oktoberfesttoday. JSON correct.
- Münchner Frühlingsfest: Apr 17 - May 10 2026 confirmed via muenchen.de, mymuenchen.de, in-muenchen, fesch-magazin (this year extended to 3 weeks for 60th anniversary). JSON correct.
- Tollwood Sommerfestival: Jun 19 - Jul 19 2026 confirmed via munich.travel, rausgegangen, musicfestivalwizard. JSON correct.
- Tollwood Winterfestival: Nov 24 - Dec 23 2026 confirmed via songkick, takeyourbackpack, rausgegangen. JSON correct.
- Starkbierfest Nockherberg: Mar 6 - 29 2026 confirmed via munichskiclub.com, tempestinatankard, paulaner-nockherberg shop. JSON correct.
- Auer Maidult: Apr 25 - May 3 2026 confirmed via muenchen.de official, iamexpat, stripes-europe. JSON correct.
- Magdalenenfest: Jul 4-19 2026 already cross-confirmed by QA1.

## Itinerary day-of-week × venue hours re-walk

Walked every itinerary day with each venue's hours:

`munich-weekend-classics`
- Day 1 Saturday: Viktualienmarkt open Sat ✓, Rischart Sat 07:00-20:00 ✓, Wurststandl Teltschik Sat 09:00-15:00 ✓ (Weisswurst pre-noon ✓), Kaffeerösterei Viktualienmarkt Sat 08:00-18:00 ✓, Hofbräuhaus daily ✓, Tohru in der Schreiberei Tue-Sat from 19:00 ✓ (QA1 fix verified), Zephyr Bar Sat 20:00-03:00 ✓ (QA1 fix verified).
- Day 2 Sunday: Café Luitpold Sun 09:00-19:00 ✓ (QA1 fix verified), Augustiner-Stammhaus Sun 11:00-22:00 ✓, Wirtshaus in der Au Sun 10:00-01:00 ✓.

`munich-fine-dining-three-days` (Thu-Fri-Sat sequence per QA1 fix)
- Day 1 Thu: Vits der Kaffee Mon-Fri 10:00-19:00 ✓ (after 10:00), Viktualienmarkt open ✓, Komu Thu-Sat 12:00-14:00 lunch ✓, Schumann's Mon-Fri 09:00-02:00 ✓ (18:00 Thu OK), Tantris Wed-Sat 18:30 ✓ (19:30 Thu OK).
- Day 2 Fri: Man versus Machine Fri 08:00-19:00 ✓, Mural Thu-Sat 12:00-15:00 lunch ✓ (Fri OK), Zephyr Bar Fri ✓, JAN Fri 19:00-19:30 ✓ (QA1 fix verified).
- Day 3 Sat: Café Luitpold Sat 08:00-19:00 ✓, Alois Dallmayr Fine Dining lunch Fri-Sat from 12:30 ✓ (Sat 12:30 OK), Tohru Sat from 19:00 ✓ (19:30 OK), Bar Gabányi Sat 20:00-05:00 ✓ (22:00 nightcap OK, QA1 fix verified).

`munich-oktoberfest-plan` (Sat-Sun-Mon since Oktoberfest 2026 opens Sat Sep 19)
- Day 1 Sat: Schneider Bräuhaus Sat 09:30 ✓ (Weisswurst pre-noon ✓), Oktoberfest tent Sat opening day ✓, Augustiner Klosterwirt Sat daily 09:30-00:00 ✓.
- Day 2 Sun: Rischart Sun 08:00-20:00 ✓ (QA1 fix verified), Café Luitpold Sun 09:00-19:00 ✓ (QA1 fix verified), Oktoberfest Sun ✓, Bar Gabányi Sun 20:00-04:00 ✓ (20:00 OK).
- Day 3 Mon: Cotidiano Gärtnerplatz daily 08:00-22:00 ✓, Hofbräukeller daily 10:00-00:00 ✓, Schneider Bräuhaus Mon ✓ (kitchen til 22:30, dinner 19:30 OK).

NO new day-of-week conflicts found. The fine-dining itinerary explicitly anchored to Thursday-Friday-Saturday now resolves cleanly.

## Beer garden seasonal Nov-Mar check

Hofbräukeller's beer garden (mentioned munich-oktoberfest-plan Day 3) is referenced for late September with "if the weather holds" qualifier - acceptable (Bavarian beer-garden season runs through mid-October typically). Aumeister Steckerlfisch in street-food.json correctly marked `open_status: seasonal` with "Apr-Oct daily 10:00-22:00 (beer garden weather-dependent)". No itinerary places a beer garden in Nov-Mar.

## Munich-proper boundary check (post QA1 JB Kaffee removal)

Walked every entity address. All Munich postcodes are in the 80xxx-81xxx range, all within Munich proper:
- 80331 (Altstadt-Lehel core), 80333 (Maxvorstadt/Altstadt), 80335 (Maxvorstadt), 80336 (Ludwigsvorstadt), 80339 (Westend/Schwanthalerhöhe), 80469 (Isarvorstadt/Glockenbach), 80539 (Lehel/Altstadt East), 80634 (Neuhausen), 80796 (Schwabing-West), 80799 (Maxvorstadt-Schwabing), 80801 (Schwabing), 80802 (Schwabing/Englischer Garten), 80803 (Schwabing-Freimann), 80805 (Schwabing), 80809 (Olympiapark), 80939 (English Garden north), 81241 (Pasing), 81379 (Thalkirchen-Sendling), 81539 (Au-Giesing), 81541 (Au), 81543 (Untergiesing), 81667 (Haidhausen), 81669 (Au), 81677 (Bogenhausen), 81829 (Trudering-Riem).

All postcodes resolve to Stadt München (Munich administrative city), not separate municipalities. Pasing (81241) was its own town until 1938, Thalkirchen (81379) is part of Munich, Riem (81829) is part of Munich.

Day-trips correctly outside Munich: Andechs (Bayern), Tegernsee, Freising (Weihenstephan), Salzburg (Austria), Garmisch-Partenkirchen.

### Geographic note (no fix made, structural)

- `hofbraeu-muenchen` brewery (breweries.json): address Hofbräuallee 1, 81829 München-Riem (the brewing facility). The neighborhood field is `altstadt-lehel`, which reflects the Hofbräuhaus brand home at Platzl 9 rather than the brewery's actual east-Munich site. Since no `trudering-riem` neighborhood entity exists and the entity is brand-anchored for UX, leaving `altstadt-lehel`. Note: a clean fix would require adding a Trudering-Riem neighborhood entry or splitting the entity. Both are upstream structural decisions.

## E2/E3/E4 phantom-venue and echo sweep

Walked region.json `seo.pages.*`, region.json `destination.overview`, city.json `food_culture_summary`, neighborhoods.json every `vibe`, food-history.json every era + immigrant_influence + signature_innovation, signature-dishes.json every `history`, seasonal-food.json every `note`, itineraries.json every summary/day-title/prose, per-entity description/tip/why_hidden.

All proper-noun venue references resolve to entities in the data tree OR are clearly historical/geographic (Wildmosers/Sepp Moser 1857 origin, Theresienwiese, Marienplatz, Frauenkirche, Hofgarten, English Garden, Chinesischer Turm, Westpark, Grossmarkthalle, Wiener Platz, Mariahilfplatz, Hirschgarten, Olympiapark Süd, Sebastiansplatz, Bayerischer Hof Hotel, MUCA Museum, Hauptbahnhof, Bavarian State Opera, Aumeister beer garden = aumeister-steckerlfisch entity, Tegernseer Brauhaus / Naturkäserei / Augustiner Bräustübl Mülln are day-trip venues outside Munich proper, acceptable in day-trips-food).

No phantom-named-venue echoes found post-QA1 cleanup.

Komu address-quoted (verified.address_quoted "Hackenstraße 4\n80331 München") correctly matches entity.address (Hackenstrasse 4, 80331 München) after QA1's fix; E4 consistency verified.

## D. Thin-category re-verification

QA1 already content-matched dietary entries via check_evidence_content.py. Re-walked the sub-categories:
- vegan (3): Max Pett, Bodhi, Tushita ✓ (HappyCow/veganfreundlich confirmations live).
- vegetarian (2): Prinz Myshkin (since 1984 confirmed via prinzmyshkin.com), Tushita ✓.
- gluten_free (2): cross-refs to Max Pett + Tushita, both already content-matched.
- halal (1): Westends Best Döner ✓ (joinhalal cert page live).
- kosher (1): Restaurant Einstein ✓ (Glatt kosher, inside IKG, totallyjewishtravel + gokosher confirmations).

No new fabrications.

## Below-floor topics after QA2

- coffee-roasters: 4 entries (was 4 after QA1; unchanged; awaiting research backfill per QA1 note).
- cafes: 8 entries (post Aroma removal; still within typical 5-floor).
- bars, street-food, bakeries, markets, cooking-classes, brunch, late-night: each 5 entries unchanged (already noted by QA1).

No fabricated replacements.

## Defects total QA2: 3

Breakdown:
- Closed venue removal (A): 1 (Aroma Kaffeebar, closed 2022)
- Hours mismatch (A2): 1 (nineOfive)
- SEO cascade fix (E): 1 (region.json cafes count + "five more" -> "four more")

Plus one structural geographic note (Hofbräu brewery neighborhood tag), not fixed because no valid target neighborhood entity exists.

## Verdict

VERDICT: PASS

Notes for Opus final pass:
- Naples-class real-URL + fake-address defect did NOT extend beyond Komu (QA1's fix). 24-entity independent-directory sample produced zero new address fabrications.
- Aroma Kaffeebar (cafes) closure escaped QA1; was the only operational defect in QA2's sweep. The CremeGuides verified page text itself flagged "Dauerhaft geschlossen", suggesting the research agent did not read the page text before quoting from it.
- nineOfive hours typo was the only operator-hours mismatch QA2 caught beyond QA1's day-of-week sweep.
- All 7 festivals' next-occurrence dates 2026 are correct per non-organizer cross-source verification.
- Itinerary day-of-week × hours: every venue's day-of-week matches its hours field. QA1's fine-dining rewrite (explicit Thu-Fri-Sat sequence) holds cleanly.
- Hofbräu brewery neighborhood tag (altstadt-lehel vs. actual Riem location) is the one structural data choice worth flagging upstream; not a fix-able QA defect.
