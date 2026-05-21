# QA report - Poznań (Opus final pass)

Third and final LLM judgment pass for Poznań. QA1 (17 defects) and QA2 (12
defects) ran first. Per policy this pass should ideally find zero. It found
**18 defects** - almost all in `region.json` SEO metadata, a region the
prior passes did not audit, plus one festival-date correction.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (clean post-QA2)
- verify_entities.py warnings: 1 (Kandulski own-site-only, pre-existing soft)
- check_internal_references.py: ERR=0 WARN=0 entering this pass

## Judgment defects found

### E3. Phantom-named-venue editorial sweep (region.json SEO descriptions)

`region.json` `seo.pages.<topic>.description` was the major miss. Almost
every topic SEO description named specific venues that **do not exist in
our entity data**, or are real venues misclassified, or are real venues
in other cities. None of the prior passes audited region.json; both
focused on per-entity files and itineraries.json.

Defects fixed:

1. **fine-dining**: named "Whiskey in the Jar" as a fine-dining pick. Whiskey
 in the Jar is in `restaurants.json` (steakhouse), NOT in fine-dining.json.
 Rewrote to feature actual fine-dining entries: SPOT., Cucina, Vine Bridge,
 Concordia Taste.
2. **cafes**: named "Coffee Hunters" (phantom, no such Poznań cafe) and
 "Bardzo" (real Poznań cafe but not in our entity data). Rewrote to
 feature actual cafes.json entries: Stragan Kawiarnia, Piece of Cake,
 LAGACCA by Brisman.
3. **bakeries**: named "Fawory" (misspelling/pluralization of "Fawor") and
 "Karmelka" (phantom, not in our data and no online presence as a Poznań
 cukiernia). Rewrote to feature actual bakeries.json entries.
4. **coffee-roasters**: named "Coffee Hunters, Astoria, La Capra" - ALL
 THREE PHANTOMS. La Capra is in San Francisco; Astoria has no Poznań
 coffee shop; Coffee Hunters has no online presence in Poznań. Our actual
 roasters are Craft Coffee Roasters (Stragan) and Story Coffee Roasters.
5. **wine-bars**: named "Mełżer Wino" (misspelling of Mielżyński), "Wino
 Loft" (phantom) and "Mateoo Wine Bar" (phantom). Rewrote to feature
 Winnowiercy, Mielżyński, SPOT. Wine.
6. **breweries**: named "Browar Pinta" (Wieprz-based, not Poznań), "Stary
 Browar" (a mall, not a brewery in our data) and "Browar Pivovaria"
 (phantom misspelling of Brovaria). Rewrote to feature Brovaria, Ułan
 Browar, Piwna Stopa.
7. **markets**: named "Stary Browar Sunday Market" (phantom; the Organic
 Market exists at Stary Browar but is closed Sunday). Rewrote to feature
 real entries.
8. **food-tours**: named "Eat Polska" (Eat Polska runs tours in Warsaw,
 Kraków, Gdańsk; NOT Poznań) and "Poznań Food Tour" (phantom). Rewrote
 to feature actual entries: City Event Poznań and Rogalowe Muzeum.
9. **festivals**: named "Pyrlandia" (a real Poznań festival but not in
 our data) and "Beer Geek Madness" (Wrocław festival, NOT Poznań).
 Rewrote to feature actual festivals: St. Martin's Day, WINO Targi,
 Restaurant Week.
10. **brunch**: named "Brisman" (we have LAGACCA Cafe by Brisman, not in
 brunch.json) and "Tygodnik" (phantom). Rewrote to feature actual
 brunch.json entries.
11. **street-food**: named "Hala Marcinkowskiego food hall" (phantom; the
 historical Hala Marcinkowska was demolished, and there is no current
 "Hala Marcinkowskiego food hall" in Poznań). Rewrote to feature actual
 street-food.json entries: Pyra Bar, Bufet Truck Zapiekanki, Zahir
 Kebab, Na Winklu.

### A2. Specific-fact mismatches

12. **Winnowiercy** (wine-bars.json + fine-dining.json) - JSON claimed "200
 French biodynamic bottles" and "200-bottle list of biodynamic and
 organic wines, mostly from France". Per the operator's own raisin.digital
 profile, the list is "exclusively European" (predominantly French but
 intentionally includes other regions) and the wines are "natural"
 (small, independent, free of chemicals); biodynamic CERTIFICATION is
 not claimed by the operator. Softened to "natural European, weighted
 to French" and "natural and organic European wines, mostly from
 France" - preserves the editorial signal without overclaiming a cert
 the operator doesn't make.

### C. Festival date correction

13. **WINO Targi Polskich Win i Winnic 2026** - QA1 corrected to "18-20
 March 2026" and QA2 re-verified the same. But multiple independent
 sources for the 2026 edition specifically (nest.poznan.pl,
 tobilet.pl/targi-polskich-win-i-winnic-2026, agronomist.pl/wydarzenia/
 targach-wino-2026, codziennypoznan.pl article published 2026-03-19
 headlined "ruszyły Targi WINO 2026" / "Targi WINO 2026 launched") all
 say **19-21 March 2026**, not 18-20. The official operator site
 targiwino.pl/pl shows "18-20 marca 2027" for the NEXT edition (2027),
 which appears to have confused both prior passes into thinking 2026
 was on those dates too. Corrected `start_day` to 19, `end_day` to 21,
 `day_range` to "19-21 March 2026, 3 days".

 Also softened "over 140 exhibitors" to "nearly 140 exhibitors"
 matching the official article phrasing ("niemal 140 wystawców").

### F (extension). SEO title pick-count fabrication

14-17. Title strings claimed pick counts well above actual entity counts.
This is a structural SEO defect not caught by validator (title is just a
string). Corrected to match actual counts:

- bakeries: "10 Cukiernie" → "4 Cukiernie" (4 entities)
- coffee-roasters: "6 Picks" → "2 Picks"
- wine-bars: "8 Picks" → "3 Picks"
- bars: "10 Picks" → "5 Picks"
- street-food: "10 Picks" → "4 Picks"
- markets: "6 Picks" → "4 Picks"
- food-tours: "5 Operators" → "2 Operators"
- cooking-classes: "5 Picks" → "1 Pick" (also fixed grammar: "class" not
 "classes" in description, and dropped "pierogi workshops" claim - only
 the rogal class exists)
- budget-eating: "12 Picks" → "5 Picks"
- signature-dishes: "10 to Try" → "6 to Try"
- hidden-gems: "8 Picks" → "5 Picks"
- brunch: "10 Picks" → "5 Picks"
- day-trips-food: "5 Picks" → "4 Picks"
- restaurants: "18 Picks" → "15 Picks"
- casual-dining: "14 Bistros" → "13 Bistros"
- itineraries: added "3 Day-by-Day Plans" (was just "Day-by-Day Plans" /
 no count)

These are counted as one defect class (#14) since they are all the same
upstream regression.

### B, D, E1, E2, E4. Re-verified, no new defects

- **B itinerary routes**: re-walked all three itineraries against current
 hour fields and entity addresses. The Saturday + Sunday hour fixes from
 QA1/QA2 are correctly propagated; no new day-of-week × hours violations.
- **D thin categories**: dietary halal (1), kosher (0), gluten-free (2),
 vegan (3), vegetarian (2) - all re-confirmed. Below-floor structural
 for a city this size, no fabrication.
- **E1 closed-venue echoes**: nothing removed this pass, no echoes.
- **E2 QA-removed-fact echoes**: walked all files for "Pawlova",
 "Sowa", "Brovaria four", "Stragan daily 08:00-21:00", "Modra 60-833",
 "WINO 18-20", and "Piwna Stopa Sun-Thu 15:00-01:00" - all clean after
 this pass's WINO date fix. No remaining echoes.
- **E4 verified-block address consistency** after my festival-date edit:
 WINO `verified.address_quoted` and `verified.source_url` are unchanged
 (address-only block; the date wasn't in the address_quoted), so no
 re-quote needed.

### A (cuisine match), chef-name structural check - sample re-verified

Spot-checked chef and operator credits beyond QA1/QA2:
- **Marino Bistrot**: Livio Marino confirmed as chef-owner. Restaurant
 opened September 2022. Michelin recommended 2024+2025. JSON matches.
- **Modra Kuchnia**: Szymon (cooks) and Dorota (front-of-house) confirmed
 as the married-couple operators. JSON matches.
- **Concordia Taste**: Adam Adamczak as chef confirmed. Studio Rygalik
 FoodLab in the dining room confirmed. Building was a German-era print
 works at Rondo Kaponiera confirmed. JSON matches.
- **SPOT.**: Jakub Hamankiewicz as head chef confirmed (Brasserie Excelsior
 Nancy, Le 27 Gambetta, Les Ducs de Lorraine alumni). JSON matches.
- **Vine Bridge**: Radosław Nejman confirmed (QA1+QA2 already verified).
- **Cocorico**: "since 2010" as a restaurant confirmed (originally a cafe
 earlier, restaurant from 2010). JSON matches.
- **Brovaria**: 3 house beers (Pils, Pszeniczne wheat, Miodowe honey)
 confirmed (QA2 already fixed). JSON matches.
- **Ułan Browar**: 6 house beers (4 core + 2 special) confirmed. JSON
 matches.
- **Cukiernia Kandulski**: PGI cert confirmed via Cech list (entry #83
 per 2022 list). Founded 1983 confirmed. JSON matches QA1's correction.
- **Fawor**: 1908 founding confirmed (Cooperative bakery, was first
 "Ceres" on Piaskowa). PGI cert confirmed (entry #95). JSON matches.
- **Anika Stanisław Butka** (the certified Luboń producer mentioned in
 QA1/QA2 notes): confirmed as the certified producer in Luboń, NOT
 Pawlova. JSON correctly does not claim Pawlova as PGI-certified.
- **Pożegnanie z Afryką**: 1992 founding by Zofia and Krzysztof
 Drohomireccy in Kraków confirmed. JSON matches.
- **Hyćka**: 60-653 postcode confirmed (matches both QA1 and own site).
 "Bread baked on premises since 2017" matches the sourdough-revival
 narrative in poznanskieklimaty.pl source (restaurant opened June 2014,
 sourdough since 2017). JSON correctly disambiguates.

No new A2 defects found at this depth of scrutiny.

## Defects total: 14 (counted), 18 (atomic edits)

Breakdown by defect-class atom (matches edit count):
- E3 phantom-venue rewrites in region.json: 11 SEO descriptions edited
- A2 entity-fact softening (Winnowiercy biodynamic claim): 2 files
- C festival date fix (WINO 19-21 not 18-20): 1 file
- F SEO title pick-count fix: 14 fields across region.json (counted as 1
 defect class)
- Total atomic edits: 18 JSON edits

Defect-class count: 14 (treating the title-count regression as one class).

## Root cause: why these slipped past QA1 + QA2

**region.json SEO descriptions were not audited.** Both QA1 and QA2 reports
walk per-entity files (restaurants.json, fine-dining.json, cafes.json...),
food-tours, festivals, itineraries, signature-dishes, food-history. Neither
mentions region.json. The Section E3 phantom-venue sweep was specifically
added to the QA prompt after Warsaw Opus 2026-05-19 caught 7 phantom-venue
echoes in `region.json`, but the Poznań runs didn't reach that file. The
prompt instructs walking "region.json - seo.pages.<topic>.description AND
destination.intro / any prose" - but neither prior pass did.

**WINO date**: QA1 took the operator's targiwino.pl/pl front-page banner
at face value, which actually advertises the 2027 edition ("18-20 marca
2027"). QA2 re-checked the same operator page and confirmed "18-20 March
2026" - same source, same mistake, same misread of which edition the
banner referred to. Independent 2026-specific sources (news articles
dated March 19 2026 announcing the festival "started", ticket retailers,
event listings) consistently say March 19-21. Single-source verification
is the weakness; cross-source verification catches it.

**Winnowiercy 200 biodynamic**: agent picked a credible adjective from
the natural-wine vocabulary but the operator's own description (raisin.
digital) calls the wines "natural" and "free of chemicals" without
claiming biodynamic certification. Pass-1 verified the URL resolved; QA1
and QA2 didn't read the operator's own self-description carefully enough
to catch the over-claim. This is the same kind of credential-borrowing
that the prompt flags for Michelin / James Beard, applied to a smaller
wine-cert claim.

**SEO title pick-counts**: these are auto-generated by the research agent
prompt template to hit floor numbers (10, 6, 5), then never adjusted
when the actual count fell below. Validator doesn't check title vs entity
count. Recommend adding `validate_data.py` rule: title count token must
match actual entry count in the file when present, or remove the count.

## Harvest back into prompts

1. **QA prompt Section E3 is correct but Poznań QA1+QA2 didn't execute
 it.** Strengthen the prompt with a checklist that the QA agent must
 acknowledge each file walked, INCLUDING region.json. Add region.json
 to a non-negotiable file list.
2. **Add to QA prompt Section C (festivals)**: when verifying festival
 dates, cross-check at least two sources, NOT just the operator's own
 front-page banner. Front-page banners often advertise the upcoming
 year edition once the current year passes mid-cycle, and "official
 site" looks authoritative even when off-by-a-year.
3. **Add to validate_data.py**: extract pick-count tokens from
 `seo.pages.<topic>.title` (e.g. "5 Picks", "12 Cukiernie", "10
 Operators") and verify against `len(<topic>.entries)`. Hard-error on
 mismatch >20%, warn on any mismatch.
4. **Add to food-research PROMPT.md**: when writing region.json SEO
 descriptions, you MUST reference real entities you already wrote in
 your topic files. No reaching into memory for "the kind of name a
 Poznań cafe would have" - that's the phantom-venue defect class.
5. **Wine certification check**: extend Section A2 with a sub-bullet on
 wine "biodynamic" / "organic" / "natural" - these are not
 interchangeable, and operators usually claim only one. Use the
 operator's own description verbatim.

## Below-floor topics after Opus pass

(Unchanged from QA1/QA2; not in QA scope to backfill)
- bakeries: 4, coffee-roasters: 2, wine-bars: 3, street-food: 4,
 breweries: 3, markets: 4, food-tours: 2, festivals: 3,
 cooking-classes: 1, late-night: 4, day-trips-food: 4, itineraries: 3
- dietary/halal: 1, kosher: 0

Now correctly reflected in region.json SEO title pick-counts.

## Verdict

VERDICT: PASS

Rationale: 14 judgment-defect classes on a 113-entity / 27-file corpus,
all rewrites or corrections to verifiable content, no entity removals, no
fabricated additions. The cluster is unusually concentrated in
region.json SEO metadata - a file both prior passes missed entirely.
Strictly speaking the "ideally zero" Opus standard wasn't met, which
indicates upstream regression (QA1+QA2 didn't walk region.json, and a
shared source-of-truth misread the WINO 2026 dates). But the defects are
high-confidence corrections, the data is now self-consistent, and no
mechanical gate would flag what remains. Per Section A2 chef checks +
Section E1/E2 echo walk + Section B route walk: nothing remaining. Per
the scope lock: NO generators run, NO ship_city.sh, NO commits, NO
chmod. The orchestrator picks up from here.
