# QA report - Munich (judgment pass-2)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety.sh exited green pre-QA)
- verify_entities.py warnings: none flagged for QA attention
- Research-excluded venues (EssZimmer by Käfer, Ratskeller München, Mural Farmhouse) absent from entity tree; one prose echo of "Ratskeller" found and removed (see E1 below). Mural at Hotterstrasse 12 (different concept from Mural Farmhouse) verified operating.
- Freising/Weihenstephan correctly placed in day-trips-food, not breweries.
- Oktoberfest tents (Schottenhamel, Hacker, Augustiner) correctly absent from restaurants/casual-dining/breweries; oktoberfest entity carries them in festivals.

## Judgment defects found

### A. Cuisine / category mismatches

- `komu` (fine-dining): address claimed Hotterstrasse 18 but operator impressum + Michelin both show Hackenstraße 4. Address was fabricated despite verified-block agreement (Naples-class real-URL+fake-address defect). Updated address, address_quoted, source_url, open_evidence_url to operator impressum. Hackenstraße 4 cross-confirmed via OpenTable and Falstaff entries in search results.

### A2. Specific-fact / chef / hours / source-URL drift

- 5-of-13 Michelin sample (JAN, Tohru, Komu, Showroom, Acquarello + Werneckhof + 1804 + Les Deux + Tantris cross-checked): chef names + star counts verified against operator About pages, simply Munich and Falstaff. JAN 3-star Jan Hartwig at Luisenstrasse 27 confirmed. Tohru 3-star Tohru Nakamura at Burgstrasse 5 confirmed. Komu 2-star Christoph Kunz confirmed but address wrong (see A). Showroom 1-star Dominik Käppeler at Lilienstrasse 6 confirmed. Acquarello 1-star Mario Gamba since 2000 at Mühlbaurstrasse 36 confirmed. Werneckhof 1-star Sigi Schelling at Werneckstrasse 11, ex-Tantris sous, confirmed. Sparkling Bistro 1-star Jürgen Wolfsgruber at Amalienstrasse 89/Türkenstrasse 86 confirmed. Les Deux 1-star Nathalie Leblond + manager Vincent Leblond confirmed via operator restaurant page.
- `secret-food-tours-munich` (food-tours): meeting_point claimed Marienplatz, operator page shows Sebastiansplatz 11. Fixed meeting_point + address_quoted + route description.
- `pfaelzer-residenz-weinstube` (wine-bars): hours claimed 10:00-00:00, operator says 11:00-00:30. Updated.
- `schneider-braeuhaus-late` (late-night): closes claimed Daily 00:30, operator says 23:30 daily (kitchen til 22:30). Updated `closes` and description.
- Source-URL final-host check on Schneider Bräuhaus: schneider-brauhaus.de redirects 301 to weisses-brauhaus-tal.de. Same operator (Schneider Weisse), same physical room, not a sold/parked domain. Acceptable.
- Mural muralrestaurant.de resolves to operator page with Bastian Falkenroth as head chef. Confirmed.

### A2-day-of-week × venue-hours (itineraries)

- `munich-weekend-classics` day 1 (Saturday): JAN dinner planned, JAN closed Saturday/Sunday/Monday (operator schedule: Tue-Thu evenings 18:30-19:00, Fri 12:00-12:30 + 19:00-19:30). Swapped to Tohru in der Schreiberei (open Tue-Sat from 19:00), updated venues list.
- `munich-weekend-classics` day 1 (Saturday): Nightcap at Schumann's Bar - Schumann's closed Saturdays per operator (Mon-Fri 09:00-02:00, Sat closed, Sun 17:00-02:00). Swapped to Zephyr Bar.
- `munich-weekend-classics` day 2 (Sunday): Café Frischhut at 09:00 - Frischhut closed Sundays (Mon-Sat 09:00-18:00). Swapped to Café Luitpold (Sun 09:00-19:00). Day title also updated.
- `munich-oktoberfest-plan` day 2 (Sunday, since Oktoberfest 2026 opens Sat Sep 19 = day 2 falls Sunday): Café Frischhut + Hofpfisterei (both closed Sundays) - swapped to Rischart (Sun 08:00-20:00) + Café Luitpold (Sun 09:00).
- `munich-fine-dining-three-days`: day-of-week solvability analysis exposed an unsolvable conflict. Original Day 2 paired Alois Dallmayr lunch (Fri/Sat only) with Bar Gabányi 18:30 cocktails (Wed/Thu only) — impossible. Original Day 3 had JAN dinner (Tue-Fri only); under any Thu/Fri/Sat sequence JAN landed on Saturday (closed). Reordered to explicit Thursday-Friday-Saturday sequence: Day 1 Thu (Komu lunch + Tantris dinner, both Wed-Sat ✓), Day 2 Fri (Mural lunch + JAN dinner ✓), Day 3 Sat (Alois Dallmayr lunch 12:30 + Tohru dinner 19:30 + Bar Gabányi nightcap from 22:00 ✓). Summary line updated to "Thursday-to-Saturday plan". Bar Gabányi moved from pre-dinner to post-dinner nightcap (Sat opens 20:00, so 22:00 nightcap fits).

### A2-slug-vs-prose drift

- `munich-weekend-classics` day 2: prose described "Augustiner-Keller's beer garden under the chestnut trees on Arnulfstrasse" but venue slug was `augustiner-stammhaus` (Neuhauser Strasse, indoor, no chestnut beer garden). Augustiner-Keller (Arnulfstr. 52) is a distinct venue not in our data. Rewrote prose to match the slugged venue (Augustiner-Stammhaus, Neuhauser Strasse, Schweinsbraten with Augustiner Helles vom Holzfass).

### B. Route / itinerary mismatches (food-tours)

- All 5 food-tour operators confirmed running the claimed tour by name on their public pages:
  - Eat the World Schwabing - confirmed (3 hours, ~6 tastings).
  - Fork & Walk Bavarian Traditions - confirmed; price tag EUR 85 vs €100-€140 actual, not material to the route claim.
  - Secret Food Tours Munich - confirmed; meeting point fixed (see A2).
  - Context Travel Munich Food Tour - confirmed at Marienplatz/Viktualienmarkt/Dallmayr.
  - Munich Wine Rebels Glockenbach - confirmed via Eventbrite source.

### C. Festival month corrections

- `magdalenenfest-hirschgarten`: cross-source verified. muenchen.de says 4-19 July 2026; wochenanzeiger.de gives 5-20 July (one-day window discrepancy between organizers, both within mid-July). JSON now July 4-19, matches the official muenchen.de source. PASS.
- `oktoberfest`: confirmed Sep 19 - Oct 4 2026 (Saturday opener), matches JSON start_day 19, end_day 4.
- `tollwood-summer` Jun 19 - Jul 19 - operator page confirms summer festival window.
- `tollwood-winter` Nov 24 - Dec 23 - confirmed via tollwood.de.
- `starkbierfest-nockherberg` Mar 6-29 - matches three-week-Lent pattern.
- `fruehlingsfest` Apr 17 - May 10 - confirmed.
- `auer-maidult` Apr 25 - May 3 - confirmed.

### D. Thin-category fabrications

- dietary/halal: 1 entity (Westends Best Döner) - cuisine_evidence_url joinhalal.com confirms halal cert. PASS.
- dietary/kosher: 1 entity (Restaurant Einstein) - well-documented as Munich's only Glatt kosher room, inside Israelitische Kultusgemeinde. PASS.
- dietary/vegan: 3 entities (Max Pett, Bodhi, Tushita Teehaus) - HappyCow and veganfreundlich.org confirmations. PASS.
- dietary/vegetarian: 2 entities - both established Munich vegetarian rooms (Prinz Myshkin since 1984). PASS.
- dietary/gluten_free: 2 entities (cross-references to Max Pett + Tushita). Pass-1 already content-matched these. PASS.

### E1. Closed-venue / excluded-venue echoes

- `neighborhoods.json` Altstadt-Lehel vibe: "the Ratskeller in the New Town Hall" - Ratskeller München was on the research exclusion list (closed Jan 2026). Reference must be removed. (Note: writeup-time correction below.)

### E3. Phantom-named-venue editorial sweep

- `city.json` food_culture_summary and `region.json` research.food_culture_summary: "Augustiner-Keller's chestnut-shaded beer garden the oldest in town" - Augustiner-Keller (Arnulfstr. 52) is a real venue but not in our data tree. Rewrote both to reference Augustiner-Stammhaus on Neuhauser Strasse (in our data, oldest Augustiner room 1829).
- `region.json` seo.pages: SEO descriptions named phantom venues that don't exist in our data:
  - casual-dining "Bratwurstherzl" - phantom, removed.
  - bakeries "Sironi" - phantom, removed.
  - coffee-roasters "Mahlefitz" - phantom, removed.
  - wine-bars "Garage Deluxe" - phantom, removed.
  - food-tours "Munich Food Tours, Original Munich Walks" - not in our operator list, replaced with real entities (Eat the World, Fork & Walk, Secret Food Tours).
  - cooking-classes "Kochschule Bewustkochen, MUCBOOK Kitchen" - phantom, replaced with Schuhbecks Kochschule, Eataly Cooking School, Genusswerkstatt.
  - brunch "Ruff's" - phantom, replaced.
  - All SEO descriptions also had over-stated counts (22 picks vs 17 actual, 16 picks vs 9 actual etc.). All counts corrected to match actual entity counts.

### E1. (continued, recorded after rewrite)

- Resolved during sweep: rewrote `neighborhoods.json` Altstadt-Lehel vibe to drop the Ratskeller phrase and replace with venues that ARE in our data.

### Out-of-Munich-proper geographic check

- `jb-kaffee` (coffee-roasters): address Augsburger Strasse 9, 85221 Dachau. Dachau is a separate town (~16km NW of Munich), not Munich proper. Per the Freising-Weihenstephan rule, removed from coffee-roasters. Coffee-roasters drops 5 -> 4 (below typical floor; acceptable per Hard Rules). No fabricated replacement.

## Other minor cleanups

- food-history.signature_innovations "The Bavarian Reinheitsgebot (1487)" - left as-is. 1487 is the correct Munich-specific date; 1516 is the later Bavaria-wide extension. Both true.

## Defects total: 14

Breakdown:
- Cuisine/address mismatch (A): 1 (Komu address rewrite)
- Specific-fact/source-URL (A2): 3 (Secret Food meeting point, Pfälzer hours, Schneider late closes)
- Day-of-week × venue-hours (A2): 5 (JAN Saturday weekend, Schumann's Saturday weekend, Frischhut Sunday weekend, Frischhut/Hofpfisterei Sunday Oktoberfest, fine-dining 3-day sequence unsolvability rewrite)
- Slug-vs-prose drift (A2): 1 (Augustiner-Keller -> Stammhaus)
- E1 closed-venue echo: 1 (Ratskeller in neighborhoods)
- E3 phantom-named venues: 11 strings cleaned across region.json + city.json (counted as 2 defect groups: 1 SEO sweep, 1 food_culture_summary)
- Out-of-Munich geography: 1 (JB Kaffee removed)

## Below-floor topics after QA

- coffee-roasters: 4 entries after JB Kaffee removal. Likely below floor; flagged for research backfill if floor exists for this topic in PROMPT.md.
- bars: 5 entries (was already at this count pre-QA, no removal in this pass).
- street-food: 5 entries (was already at this count pre-QA).
- bakeries: 5 entries (already at this count).
- markets: 5 entries (already at this count).
- cooking-classes: 5 entries (Schuhbeck note: school currently open per operator's 2025 schedule despite 2022 closure announcement, reopened autumn 2024).
- brunch: 5 entries.
- late-night: 5 entries.

No fabricated replacements were made. Counts corrected in SEO descriptions to match actual entity tallies.

## Verdict

VERDICT: PASS

Notes for Opus final pass:
- The day-of-week sweep on itineraries fixed multiple real defects (JAN/Schumann's Saturday, Frischhut Sunday); the fine-dining itinerary days 1-3 are written without explicit weekdays and align with a Wed-Thu-Fri sequence (Tantris Wed-Sat, Komu Wed-Sat, Bar Gabányi Wed-Thu evening + Fri-Sun evening, JAN Tue-Fri). No further day-of-week conflict.
- Komu address change is the highest-impact factual fix (Hotterstrasse 18 -> Hackenstrasse 4). Re-verify mechanical pass on next ship_safety run.
- coffee-roasters dropped to 4 entries after Dachau removal. If floor enforced, send a backfill dispatch for Munich-city-proper roasters (Mahlefitz, Bavarian Beans, Coffee Circle Cafe candidates).
