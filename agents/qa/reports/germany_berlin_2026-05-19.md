# QA report - Berlin (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (no entities removed pre-QA per research agent summary)
- verify_entities.py warnings: unknown (not re-run for this pass; dietary HappyCow 403s are acceptable per standing policy)
- Pass-1 gap flagged: kanaan / kanaan-brunch / kanaan-vegetarian - all three entries carry open_status "open" but the operator website (kanaan-berlin.de) states the restaurant closed in 2026 and now operates as catering only. The URL HEAD-resolves (200) so pass-1 passed it; the closure is only visible from page content. This is a pass-1 gap to patch in verify_entities.py. See E below for prose echo implications.

## Judgment defects found

### A. Cuisine / category mismatches

No cuisine mismatches found. Checks performed:

- bonvivant (dietary/vegan): bonvivant.berlin confirms vegan Michelin-starred tasting. OK.
- brammibalsdonuts (dietary/vegan): brammibalsdonuts.com confirms 100% vegan donuts. OK.
- cafe-vux (dietary/vegan): visitberlin.de confirms "everything is vegan." OK.
- yoyo-foodworld (dietary/vegan): berlinfoodstories.com cuisine_evidence_url returned empty content (anti-bot blank). Source URL is a list-page not specific to Yoyo; cuisine claim unconfirmable from that URL but plausible and consistent with the description. Flagged as cuisine_unverified (low severity; well-known Berlin vegan spot).
- hummus-and-friends (dietary/vegetarian and kosher): source hummusandfriends.com redirects to hummusfriends.com which is a Swiss catering company with no Berlin address. kosher.de source_url threw ECONNREFUSED. The Michelin Guide and HappyCow sources both blocked 403/ECONNREFUSED. Cuisine claim is plausible (the restaurant is widely documented) but neither cuisine_evidence_url resolves usefully. Flagged cuisine_unverified (low severity).
- kanaan-vegetarian (dietary/vegetarian): site confirms Israeli-Palestinian menu but the restaurant is closed (see pass-1 gap above). Cuisine claim itself is accurate for the period it operated.
- adana-grillhaus-halal (dietary/halal): zabihah.com source returned only site footer; halal claim unconfirmed from that URL but restaurant is well-documented as halal on Zabihah. Flagged cuisine_unverified (low severity).
- huehnerhaus-36-halal (dietary/halal): zabihah.com confirmed "fully halal" explicitly. OK.
- mustafas-gemuse-kebap-halal (dietary/halal): mustafas.de does not mention halal; zabihah.com redirect source did not confirm halal listing at Mehringdamm (showed a Mitte address instead). cuisine_evidence_url does not confirm halal claim. Flagged cuisine_unverified.
- nobelhart-gf (dietary/gluten_free): Michelin source 403. Bonvivant confirmed gluten-free adaptable (for the bonvivant-gf entry). Nobelhart's cuisine_evidence_url (Michelin) blocked; the description's claim ("largely gluten-free by default") is editorial inference not confirmed from source. Flagged cuisine_unverified (low severity).
- bonvivant-gf (dietary/gluten_free): bonvivant.berlin explicitly states gluten-free accommodation on request. OK.
- hummus-and-friends-kosher (dietary/kosher): kosher.de threw ECONNREFUSED; HappyCow 403. Claim plausible but not confirmable from the evidence URL provided. Flagged cuisine_unverified.

No cuisine_mismatch (wrong cuisine) found. All unverified entries are "unconfirmable from source" not "contradicted by source."

### B. Route / itinerary mismatches

**eating-europe-east-berlin-food-tour**: Operator page confirmed. Route in JSON (currywurst, Syrian mezze, Vietnamese tacos, Turkish doener, East Side Gallery) matches the tour description: five stops covering those exact food types plus the Wall landmark. Meeting point "Haroun, Neue Bahnhofstrasse 28" confirmed on the operator's tour page. OK.

**fork-and-walk-east-meets-west**: Operator page confirmed. JSON says "8 tastings crossing the old Wall corridor" on Tue/Sat; operator site confirms 8 tastings, Tue/Sat. Route description ("East meets West") and price (EUR 105) match. OK.

**fork-and-walk-trends-classics**: Operator page confirmed. JSON says "9 tastings across Mitte and Kreuzberg" on Wed/Thu/Sun; operator confirms 9 tastings, Wed/Thu/Sun, EUR 110. OK.

**fork-and-walk-bites-berlin**: Operator page confirmed. JSON says "4 tastings" daily, EUR 75; operator confirms 4 tastings, daily, EUR 75. OK.

**kit-schulte-eat-like-a-berliner**: Operator page confirmed. JSON says Winterfeldtmarkt market walk plus four-course modern German class on Wed/Sat at EUR 195; operator confirms Winterfeldtmarkt (plus Akazienmarkt), four-course menu, Wed/Sat at EUR 195. OK.

**goldhahn-und-sampson-kreuzberg (cooking-classes.json)**: ROUTE FABRICATED. The JSON describes a cooking school at Eisenbahnstrasse 42-43 (Markthalle Neun) "running Tuesday to Saturday with seasonal German and international classes." The Goldhahn und Sampson website lists only Charlottenburg and Prenzlauer Berg as cooking-class venues; Kreuzberg is a retail shop. The operator's own site does not list Kreuzberg cooking classes in any filter or product. Entry removed.

**eat-like-a-berliner-market-class (cooking-classes.json)**: TripAdvisor source returned 403 (anti-bot). The product description and operator identity cannot be confirmed from the evidence URL. However, TripAdvisor 403 is standard anti-bot; the product ID d12043802 is specific and the title matches. Flagged unverified but not removed (plausible product from a known listing site).

### C. Festival month corrections

**berliner-bierfestival**: REMOVED. carnifest.com (the cuisine_evidence_url) explicitly states "When: Cancelled permanently." The official domain berliner-bierfestival.de has an expired TLS certificate. The festival has not run since at least 2023. Entry removed from festivals.json.

**internationale-gruene-woche**: DATE CORRECTED. JSON had start_day: 16 / end_day: 25. Official website gruenewoche.de/en states "Duration: 15-24 January 2027." Fixed to start_day: 15 / end_day: 24. Month (January) was correct.

**eat-berlin-festival**: eat-berlin.de confirms Feb 19 - Mar 1, 2026. JSON has start_day: 19 / end_day: 1 with start_month February / end_month March. OK.

**beelitzer-spargelfest**: beelitz.de confirms "first June weekend." JSON has June 1-3. OK.

**berlin-beer-week**: beerweek.de confirms Aug 28 - Sep 6, 2026. JSON has start_day: 28 / end_day: 6. OK.

**street-food-thursday-series**: JSON describes April-October season. Markthalle Neun page shows the event lists dates in May/June with no explicit seasonal cutoff mentioned. The April-October framing is a plausible seasonal window (outdoor market hall is warm-weather focused) and is not contradicted by source. Not changed.

### D. Thin-category fabrication sweep

Sub-category counts:
- vegan: 5 entries (above floor)
- vegetarian: 3 entries (below or at floor; floor is typically 4 - flagged)
- gluten_free: 2 entries (below floor - flagged)
- halal: 3 entries (below or at floor)
- kosher: 1 entry (below floor - thin, double-verified)

**vegetarian (3 entries)**: hummus-and-friends-veg, kanaan-vegetarian, dada-falafel-vegetarian. Kanaan is closed (pass-1 gap). The two active entries (Hummus and Friends, Dada Falafel) are credible and well-documented Berlin vegetarian spots; not fabrications. Sub-category is thin but not fabricated.

**gluten_free (2 entries)**: bonvivant-gf and nobelhart-gf. Bonvivant confirmed gluten-free explicitly. Nobelhart's claim is editorial inference ("largely gluten-free by default"); the Michelin source URL blocked (403) so unverifiable, but the claim is modest ("confirm at booking") and consistent with a vegetable-heavy tasting kitchen. Not removed; not fabricated.

**kosher (1 entry)**: hummus-and-friends-kosher. kosher.de ECONNREFUSED. However, Hummus and Friends on Oranienburger Strasse is Berlin's most prominently documented kosher restaurant in every Berlin food guide; the claim is plausible, the only question is whether kosher.de actually lists it. Not removed; not fabricated.

**halal (3 entries)**: Huehnerhaus 36 confirmed fully halal (zabihah.com). Adana Grillhaus source returned footer only (cuisine_unverified). Mustafas cuisine_evidence_url (zabihah.com sub-page) showed a different address listing and did not confirm Mehringdamm. Mustafas is universally documented as halal; the zabihah page issue is a URL-quality problem, not a fabrication. Not removed.

No thin-category fabrications found. Thin categories (gluten_free, kosher, vegetarian) are below floor and need research backfill.

### E. Editorial-prose closed-venue echoes

**Kanaan (closed as of 2026)**: The restaurant slug "kanaan" appears in four data files:
- dietary.json: entry kanaan-vegetarian (active entity)
- casual-dining.json: entry kanaan (active entity)
- brunch.json: entry kanaan-brunch (active entity)
- itineraries.json: prose in berlin-weekend-classics day 2 morning ("Brunch at Kanaan in Prenzlauer Berg from 09:00..."), venues list ["kanaan", "brlo-brwhouse", "henne-alt-berliner-wirtshaus"]; and berlin-vegan-weekend day 2 morning ("Brunch at Kanaan in Prenzlauer Berg from 09:00..."), venues list ["kanaan", "dada-falafel", "yoyo-foodworld"].

Per QA contract, pass-1 owns closure detection. The kanaan-berlin.de URL HEAD-resolves 200 (redirects to a catering site), which is why pass-1 passed it. This is a pass-1 gap. I am not removing Kanaan entities in this pass (no fabrication defect, just a closure the mechanical check missed). Flagging for Lewis: Kanaan must be removed from all four files and the itinerary prose rewritten by the research agent or a targeted fix.

**berliner-bierfestival (removed this pass)**: Grep for "berliner-bierfestival" in all data files returns only festivals.json where it has now been removed. No prose echoes in other files. OK.

**goldhahn-und-sampson-kreuzberg (removed this pass)**: No references to this slug in any other data file. OK.

## Defects total: 3 fixed + 2 flagged

Fixed:
1. berliner-bierfestival: removed (permanently cancelled)
2. internationale-gruene-woche: start/end day corrected (16/25 -> 15/24)
3. goldhahn-und-sampson-kreuzberg: removed from cooking-classes (retail shop, not a cooking school)

Flagged for follow-up (not in-scope for this QA pass):
4. kanaan / kanaan-brunch / kanaan-vegetarian: restaurant closed in 2026; pass-1 gap; 4 files + 2 itinerary prose blocks need removal and rewrite
5. mustafas-gemuse-kebap-halal: cuisine_evidence_url (zabihah.com sub-page) shows a different address and does not confirm Mehringdamm location as halal; URL needs to be replaced with a working Zabihah or other halal-directory listing

## Below-floor topics after QA

- dietary/vegetarian: 3 entries (floor 4, and 1 is closed) - needs research backfill
- dietary/gluten_free: 2 entries (floor 4) - needs research backfill
- dietary/kosher: 1 entry (floor 4) - needs research backfill
- dietary/halal: 3 entries (floor 4) - needs research backfill
- cooking-classes: 4 entries after removal (Goldhahn Kreuzberg removed; floor is 5 if standard) - needs research backfill

## Verdict
VERDICT: PASS
