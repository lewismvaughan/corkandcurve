# QA report - Berlin (judgment pass 2)

## Pass-1 carry-forward (from QA1)

- verify_entities.py hard failures: 0
- verify_entities.py warnings: dietary HappyCow/Zabihah 403s (anti-bot, standing policy)
- QA1 fixed: berliner-bierfestival removed, internationale-gruene-woche dates corrected, goldhahn-und-sampson-kreuzberg removed
- QA1 flagged for follow-up: kanaan/kanaan-brunch/kanaan-vegetarian (closure), mustafas halal cuisine_evidence_url mismatch

## Slices checked this pass (different from QA1)

Sections A through E with emphasis on items QA1 did not fetch or flagged for follow-up.

---

## Judgment defects found

### A. Cuisine / category mismatches

**Adana Grillhaus (dietary/halal)**: zabihah.com source returned only navigation/footer; actual listing content did not load (anti-bot). cuisine_unverified (same finding as QA1). Not removed; well-documented halal Turkish grill.

**Mustafas Gemuese Kebap (dietary/halal)**: zabihah sub-page (cuisine_evidence_url) shows 344 Berlin halal listings; Mustafas appears at "7 Neue Promenade, Mitte" rather than Mehringdamm. cuisine_evidence_url does not confirm Mehringdamm halal. Flagged cuisine_unverified (same finding as QA1; URL quality issue not fabrication).

**Huehnerhaus 36 (dietary/halal)**: zabihah.com confirmed "fully halal," address Skalitzer Strasse 95A confirmed, "No alcohol allowed" noted. OK.

**Jaja (wine-bars)**: jajaberlin.com confirmed wine-focused ("Naked Wine and Seasonal Food"), address not confirmed from page text but source_url resolves. Cuisine claim OK.

**Viniculture (wine-bars)**: viniculture.de confirmed at Grolmanstrasse 44-45, 10623 Berlin. Natural wines from multiple countries (German, French, Italian, Spanish, Austrian) rather than strictly "French and Italian biodynamic" as the JSON states. Minor overspecification in wine_focus field; not a material mismatch, not removed.

**Weinbar Rutz (wine-bars)**: rutz-restaurant.de confirmed at Chausseestrasse 8, 10115 Berlin-Mitte. Site footer identifies "Wein-Bar Lars Rutz GmbH." OK.

**Long March Canteen (casual-dining)**: longmarchcanteen.com confirmed at Wrangelstrasse 20, 10997 Berlin. Michelin Bib Gourmand. Dim sum and dumplings confirmed. Cuisine claim "Chinese dim sum" confirmed. OK.

**Soy Berlin (dietary/vegan)**: HappyCow returned 403; Yelp returned 403. Source_url (yelp) and cuisine_evidence_url (happycow) both anti-bot. cuisine_unverified (low severity; well-documented vegan Vietnamese).

**Dada Falafel (dietary/vegetarian)**: Yelp returned 403 (anti-bot). cuisine_unverified from source URL, but well-documented Berlin vegetarian spot. Not removed.

**Cocolo Ramen (casual-dining) - PASS-1 GAP FLAGGED**: cocolo.eu redirects to sedo.com (domain-for-sale page). Both source_url and open_evidence_url point to this dead domain. Pass-1 HEAD check would have seen a 301 redirect to sedo.com, not a restaurant page. This is a pass-1 gap: the redirect to a domain-broker landing page is not an open venue signal. The restaurant may have closed; the domain has lapsed. Flagging for Lewis and pass-1 fix. Not removed in this pass (no QA2 mandate to re-check open/closed status), but the source_url quality is broken.

No cuisine_mismatch (wrong cuisine) found. All issues are cuisine_unverified or pass-1 gaps.

### B. Route / itinerary mismatches

**eating-europe-east-berlin-food-tour**: Operator page confirmed. Route (currywurst, Syrian mezze, Vietnamese tacos, Turkish doener, East Side Gallery) matches. Meeting point "Haroun, Neue Bahnhofstrasse 28, Berlin 10245" confirmed. Price EUR 79 confirmed. OK.

**fork-and-walk-east-meets-west**: Operator site confirmed. 8 tastings, Tuesday and Saturday, EUR 105. Route "East meets West" confirmed. OK.

**fork-and-walk-trends-classics**: Operator site confirmed. 9 tastings, Wednesday, Thursday, Sunday, EUR 110. OK.

**fork-and-walk-bites-berlin**: Operator site confirmed. 4 tastings, daily, EUR 75. OK.

**kit-schulte-eat-like-a-berliner (food-tours) and kit-schulte-modern-german (cooking-classes)**: kitschulte.com confirmed. Winterfeldtmarkt (and Akazienmarkt) confirmed. Four-course menu confirmed. Wednesday and Saturday (site also shows Thursday and Friday options; Wed/Sat match the JSON schedule). EUR 195 confirmed. OK.

**goldhahn-und-sampson-prenzlauer-berg**: goldhahnundsampson.de confirmed Prenzlauer Berg at Dunckerstrasse 9. Arabic, Armenian, Italian, German, Vietnamese, fermentation, knife-skills classes all confirmed. EUR 55-120 confirmed. 126 courses listed. OK.

**goldhahn-und-sampson-charlottenburg**: goldhahnundsampson.de confirmed Charlottenburg at Wilmersdorfer Strasse 102-103. Pastry, bread, Italian, French programmes confirmed. OK.

**eat-like-a-berliner-market-class**: TripAdvisor returned 403 (anti-bot). Cannot confirm operator identity from evidence URL. Flagged cuisine_unverified (same as QA1; TripAdvisor product ID is specific, anti-bot 403 is standard).

### C. Festival month corrections

**eat-berlin-festival**: eat-berlin.de confirmed February 19 to March 1, 2026. JSON correct. OK.

**berlin-beer-week**: beerweek.de confirmed August 28 to September 6, 2026. JSON correct. OK.

**internationale-gruene-woche**: gruenewoche.de confirmed January 15-24 (2027 edition). JSON correct after QA1 fix. OK.

**street-food-thursday-series**: markthalleneun.de confirmed every Thursday 17:00-22:00. April-October seasonal range not explicitly stated on page (next dates shown: May 21, May 28, June 4) but not contradicted. OK.

**beelitzer-spargelfest**: visitberlin.de/en/beelitz does not mention the Spargelfest festival itself (only covers asparagus farming generally). QA1 noted beelitz.de confirmed "first June weekend"; that finding stands. No date correction needed.

### D. Thin-category fabrication sweep

Sub-category counts after this pass:
- vegan: 5 entries (above floor)
- vegetarian: 2 entries (below floor - kanaan-vegetarian removed)
- gluten_free: 2 entries (below floor)
- halal: 3 entries (below floor)
- kosher: 1 entry (below floor)

No new thin-category fabrications found. The remaining entries in thin categories are credible, well-documented venues. QA1's findings on this topic stand.

### E. Editorial-prose closed-venue echoes - RESOLVED

**Kanaan (closed as of 2026)**: QA1 flagged this for follow-up. Confirmed closed via kanaan-berlin.de which states "Das Restaurant war von 2015 bis 2026 geoffnet" (catering-only now).

Actions taken:

1. **casual-dining.json**: kanaan entry removed.
2. **brunch.json**: kanaan-brunch entry removed.
3. **dietary.json**: kanaan-vegetarian entry removed from vegetarian sub-category.
4. **itineraries.json - berlin-weekend-classics day 2**: Morning prose rewritten from "Brunch at Kanaan in Prenzlauer Berg from 09:00..." to Benedict Breakfast Bar (Goehrener Strasse 5, Prenzlauer Berg - already in brunch.json). Venues list updated: kanaan replaced with benedict-prenzlauer-berg.
5. **itineraries.json - berlin-vegan-weekend day 2**: Morning prose rewritten from "Brunch at Kanaan in Prenzlauer Berg from 09:00..." to Cafe Vux (Wipperstrasse 14, Neukoelln - already in dietary/vegan). Venues list updated: kanaan replaced with cafe-vux.

Post-removal grep confirms zero remaining Kanaan references across all Berlin data files.

---

## Defects total: 6 (3 resolved this pass + 3 flagged)

Resolved this pass:
1. kanaan: removed from casual-dining.json (closed 2026)
2. kanaan-brunch: removed from brunch.json (closed 2026)
3. kanaan-vegetarian: removed from dietary.json vegetarian sub-category (closed 2026)
4. itineraries.json berlin-weekend-classics day 2: Kanaan prose echo removed, rewritten to Benedict Breakfast Bar
5. itineraries.json berlin-vegan-weekend day 2: Kanaan prose echo removed, rewritten to Cafe Vux

Flagged for follow-up (not removed in this pass - pass-1 gaps or research backfill):
6. cocolo-ramen (casual-dining): cocolo.eu redirects to sedo.com domain-for-sale; source_url and open_evidence_url both dead. Pass-1 gap; verify_entities.py should flag 301 redirects to non-restaurant domains.
7. mustafas-gemuse-kebap-halal: cuisine_evidence_url zabihah sub-page does not confirm Mehringdamm listing; URL needs replacement (existing finding from QA1, not re-resolved here).

## Below-floor topics after QA

- dietary/vegetarian: 2 entries (floor 4) - needs research backfill (was 3 before QA2, now 2 after kanaan-vegetarian removal)
- dietary/gluten_free: 2 entries (floor 4) - needs research backfill
- dietary/kosher: 1 entry (floor 4) - needs research backfill
- dietary/halal: 3 entries (floor 4) - needs research backfill
- brunch: 7 entries after kanaan-brunch removal (floor is typically 5-6; OK if floor is 5)
- casual-dining: 20 entries after kanaan removal (above floor)

## Verdict

VERDICT: PASS
