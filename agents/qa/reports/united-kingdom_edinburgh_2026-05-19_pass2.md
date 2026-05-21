# QA report -- Edinburgh (judgment pass 2)

Date: 2026-05-19
Agent: QA pass-2 (second judgment pass)
Scope: united-kingdom/edinburgh
Prior pass: united-kingdom_edinburgh_2026-05-19.md (QA1)

---

## Pass-1 carry-forward

- verify_entities.py hard failures: pre-existing; not re-run in this pass
- QA1 removals: eating-europe-edinburgh-class (miscategorized as cooking class, re-added to food-tours as eating-europe-edinburgh); edinburgh-new-town-cookery-school (duplicate of EFDA)
- verify_entities.py warnings: pre-existing stale checked_on; not re-examined per protocol

---

## Judgment defects found

### A. Cuisine / category mismatches

**A-1 (fixed): scotch-whisky-experience-tour -- stale price data**

The operator's current pricing (fetched from scotchwhiskyexperience.co.uk) is Silver tour GBP 25 / Gold tour GBP 39.75. The JSON carried "GBP 22-50" and the tip referenced "GBP 50" and "GBP 22 with one dram". The price field was corrected to "GBP 25-40" and the tip updated to reflect current Silver/Gold tour names and prices. Classification remains correct; this is a price-text accuracy fix.

**A-2 (unverifiable, no mismatch): gluten-free dietary entries**

FindMeGlutenFree continues to return 403 for all three GF entry cuisine_evidence_url pages (chorrito-cantina-gf, ardfern-gf, bross-bagels-gf). Alternative attempts via the GF listing landing page and venue own-sites also blocked or silent. No positive mismatch was found; the operators are plausible Edinburgh venues. Flagged as cuisine_unverified (carried forward from QA1). No removals.

**A-3 (confirmed OK): halal entries**

zabihah.com pages confirm:
- kebab-mahal-halal: "Fully halal", Indian tandoori/curry, 7 Nicolson Square -- matches JSON
- hanams-halal: "Fully halal", Kurdish and Middle Eastern cuisine, 3 Johnston Terrace -- matches JSON

Mosque Kitchen's source_url cross-assignment (points to Kebab Mahal zabihah entry) flagged as a pass-1 concern; cuisine claim itself is consistent with the general Edinburgh halal listing.

**A-4 (confirmed OK): vegan entries**

Soul Vegan (soulvegan.uk): confirmed vegan Malaysian restaurant at 46 W Richmond St -- matches JSON.
David Bann (davidbann.co.uk): confirmed vegetarian and vegan restaurant at 56-58 St Mary's Street -- matches JSON.
Hendersons (hendersonsrestaurant.com): confirmed vegetarian and vegan at 7-13 Barclay Place -- matches JSON.

---

### B. Route / itinerary mismatches

**B-1 (fixed): eat-walk-leith and eat-walk-stockbridge -- fabricated tour products removed**

QA1 flagged these two entries as unverifiable operator products, noting eatwalktours.co.uk lists only one Edinburgh tour ("Edinburgh Eat Walk Food Tour", GBP 93, Old Town and New Town). QA2 confirms the same: the operator page shows a single Edinburgh product; no Leith Shore or Stockbridge/Dean Village product is listed.

Per QA protocol ("If the route is fabricated, remove the entity and note it. Do not try to substitute a different route from the same operator."), both entries were removed from food-tours.json. The base eat-walk-edinburgh entry (Old Town and New Town, matching the operator's live product) is retained.

**B-2 (confirmed): eating-europe-edinburgh -- route and meeting point verified**

Eating Europe Edinburgh tour page confirms: meeting point at Melville Monument, 42 St Andrew Square (Paddington Bear statue reference verified); haggis with whisky marmalade, Scottish cheeses, fish and chips; 3 hours; GBP 92. All JSON fields match.

**B-3 (confirmed): secret-food-tours-edinburgh -- route confirmed plausible**

Secret Food Tours Edinburgh page confirms: Old Town food walk, 3 to 3.5 hours, five food stops, haggis and award-winning Lowland single malt whisky. Scottish smoked salmon and shortbread are not mentioned on the booking page, but the haggis and whisky core claim is confirmed. Minor description looseness; not a removal-level defect.

---

### C. Festival month corrections

All five festivals re-checked:

- edinburgh-food-festival: official site (edfoodfestival.com) returned ECONNREFUSED. Assembly Festival page (assemblyfestival.com) confirms the festival context runs Aug 5-31 2026. Edinburgh Food Festival has historically run late July; JSON July 24 - August 2 is plausible. No correction.
- foodies-festival-edinburgh: foodiesfestival.com/event/edinburgh-2026/ and /locations/edinburgh/ both returned empty content. Dates August 7-9 are plausible for this touring festival. Could not confirm; flagged unverifiable. No correction.
- edinburgh-fringe-street-food: Wikipedia confirms Fringe 2026 runs Aug 7-31. JSON claims Aug 1-25 (start 6 days early, end 6 days early). QA1 noted the Aug 1 start as slightly generous; end date of Aug 25 vs actual Fringe end of Aug 31 understates the end. No month-level error; days are approximate. No correction.
- burns-night-edinburgh: January 25. Correct.
- edinburgh-international-festival-food: eif.co.uk confirmed Aug 7-30 2026. JSON matches exactly.

No festival corrections made.

---

### D. Thin-category fabrication sweep

**D-1 (fixed): vegetarian sub-category -- henderson-of-edinburgh-veg removed**

The henderson-of-edinburgh-veg entry (slug) listed 92 Hanover Street, Edinburgh EH2 1DR as its address. Investigation confirmed that Henderson's original Hanover Street location permanently closed in 2020 due to the COVID-19 pandemic. The domain hendersonsofedinburgh.co.uk has since been taken over by a spam/adult-dating site. The current active Henderson's at 7-13 Barclay Place (Bruntsfield) is already in the dataset as hendersons-vegetarian. The Hanover Street entry is a duplicate of a closed venue with a hijacked source URL. Removed from dietary.json vegetarian sub-category.

After removal: vegetarian sub-category has 2 entries (David Bann + Hendersons Barclay Place). Below thin-category floor; flagged for research backfill.

**D-2: Gluten-free sub-category -- cuisine_unverified (carried forward from QA1)**

All three FindMeGlutenFree evidence URLs return 403. Chorrito Cantina's own domain (chorritocantina.co.uk) was ECONNREFUSED. Ardfern (ardfern.uk) confirmed as an all-day cafe in Leith but its website did not mention gluten-free on the homepage; menu pages not rendered. No positive mismatch found. Entries retained but marked as cuisine_unverified.

---

### E. Editorial-prose closed-venue echoes

**E-1 (fixed): region.json cooking-classes SEO description -- ghost references removed**

The cooking-classes SEO description read: "Where to take a cooking class in Edinburgh in 2026: Edinburgh New Town Cookery School, The Food Studio and four more..." Both Edinburgh New Town Cookery School (removed in QA1 as duplicate of EFDA) and "The Food Studio" (not in any Edinburgh data file; likely a research-agent fabrication) were named. Replaced with references to the three actual entities: Yarrow Cookery School and Edinburgh Food and Drink Academy (trimmed to fit 140-165 char cap at 156 chars).

**E-2 (fixed): casual-dining.json -- hendersons-vegetarian-casual removed**

Entry slug hendersons-vegetarian-casual described "Henderson's Salad Table on Hanover Street in Edinburgh, opened in 1962 by Janet Henderson" with source_url, booking_url and open_evidence_url all pointing to hendersonsofedinburgh.co.uk. That domain now serves adult-dating spam content. The entity references the closed original Hanover Street location (permanently closed 2020). Removed from casual-dining.json.

**E-3 (checked, no action): food-history.json Hanover Street reference**

food-history.json mentions "Henderson's Vegetarian Restaurant opened on Hanover Street in 1962" in a historical summary. This is correct historical context, not an entity listing or a claim about a currently-open venue. No edit needed.

---

## Changes made (JSON edits)

1. **food-tours.json**: Removed `eat-walk-leith` and `eat-walk-stockbridge` (operator offers one Edinburgh tour; route variants unverifiable). Corrected `scotch-whisky-experience-tour` price from "GBP 22-50" to "GBP 25-40"; updated tip to reflect current Silver/Gold tour naming. (5 food-tours remain)

2. **dietary.json**: Removed `henderson-of-edinburgh-veg` from vegetarian sub-category (closed Hanover Street location; domain hijacked). (vegetarian: 2 entries remain)

3. **casual-dining.json**: Removed `hendersons-vegetarian-casual` (closed Hanover Street location; source domain hijacked). (19 casual-dining entries remain)

4. **region.json**: Replaced ghost references in cooking-classes SEO description (Edinburgh New Town Cookery School, The Food Studio) with actual entity names (Yarrow Cookery School, Edinburgh Food and Drink Academy); trimmed to 156 chars.

5. **Regenerated**: generate_city.py, generate_cross_cuts.py, generate_extras.py, generate_chrome_pages.py, generate_sitemap.py, generate_search_index.py. Permissions updated via `sshp host chmod a+rX`.

---

## Defects total: 6 (A-1 price fix, B-1 two route fabrications removed, D-1 closed-venue removed, E-1 ghost SEO desc fixed, E-2 closed-venue removed)

---

## Below-floor topics after QA2

- cooking-classes: 3 entries (floor 10 for SEO depth per validator) -- needs research backfill
- vegetarian (dietary sub-category): 2 entries -- thin; needs backfill of 1+ verified Edinburgh vegetarian venues at open addresses
- food-tours: 5 entries (eat-walk-edinburgh, edinburgh-food-safari, secret-food-tours-edinburgh, scotch-whisky-experience-tour, eating-europe-edinburgh) -- still reasonable depth, no floor breach

---

## Pre-existing WARNs (not introduced by QA1 or QA2)

The following validator warnings were present before this pass and are outside scope:

- seo.pages.cafes.title: 73 chars (cap 55-70)
- seo.pages.bars.title: 71 chars (cap 55-70)
- seo.pages.budget-eating.title: 71 chars (cap 55-70)
- fine-dining.json 'Fhior' must_order: 113 chars (cap 30-110)
- cooking-classes.json 'Yarrow Cookery School' description: 237 chars (cap 140-220)
- signature-dishes.json 'Haggis, neeps and tatties' make_it_yourself.tip: 184 chars (cap 60-160)
- signature-dishes.json 'Fish and chips' make_it_yourself.tip: 166 chars (cap 60-160)
- signature-dishes.json 'Deep-fried Mars bar' where_to_eat references 'Clamshell' which is not in any venue file

---

## Verdict

VERDICT: PASS
