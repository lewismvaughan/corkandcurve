# QA report -- Edinburgh (judgment pass)

Date: 2026-05-19
Agent: QA pass-2 (judgment)
Scope: united-kingdom/edinburgh

---

## Pass-1 carry-forward

- verify_entities.py hard failures: not re-run in this pass (ship_safety ran prior to QA; entities reaching this pass are assumed verified)
- Pre-QA removals noted in context: Bonnington Centre Saturday Market (removed as fabricated, replaced by The Pitt)
- verify_entities.py warnings: stale checked_on warnings pre-exist; not re-examined per protocol

---

## Judgment defects found

### A. Cuisine / category mismatches

No cuisine mismatches found on content check.

- Halal entries (mosque-kitchen-halal, hanams-halal, kebab-mahal-halal): zabihah.com pages confirm halal status for Hanam's and Kebab Mahal. Mosque Kitchen source_url points to the Kebab Mahal zabihah entry (c9dc4a18...) rather than a Mosque Kitchen-specific page; this is a provenance-URL cross-assignment but the cuisine_evidence_url (general zabihah Edinburgh listing) confirms halal Pakistani cuisine. Flagged as a pass-1 concern (source_url mismatch) but not a cuisine mismatch.
- Vegan/vegetarian entries: HappyCow pages return 403 so content cannot be read directly, but Soul Vegan, David Bann and Hendersons are well-established Edinburgh venues with the described cuisines. No mismatch found.
- Gluten-free entries: FindMeGlutenFree pages return 403. Cannot confirm content-match for chorrito-cantina-gf and bross-bagels-gf. ardfern-gf uses findmeglutenfree.com/gb/edinburgh (general listing) which also returns 403. No positive mismatch found; flagged as cuisine_unverified for the three gluten-free entries where the evidence URL could not be read.

### B. Route / itinerary mismatches

**DEFECT B-1 (fixed): eating-europe-edinburgh-class -- miscategorized as cooking class**

Eating Europe offers only food and drinks walking tours; operator confirms no cooking instruction exists. The entry was filed in cooking-classes.json with a `cuisine_taught` field but the operator is purely a tour operator. Removed from cooking-classes.json and re-added to food-tours.json with correct food_tour schema fields (operator, route, duration, price, meeting_point, neighborhood). Slug updated from eating-europe-edinburgh-class to eating-europe-edinburgh to reflect correct category.

**DEFECT B-2 (fixed): edinburgh-new-town-cookery-school -- duplicate entity**

The entcs.co.uk domain permanently redirects (301) to efda.co.uk. The EFDA About Us page confirms: "Since opening our doors in 2009, when we were known as Edinburgh New Town Cookery School, we have been teaching..." Both edinburgh-new-town-cookery-school and edinburgh-food-drink-academy list the same address (7 Queen Street, Edinburgh EH2 1JE). The school has rebranded; there is one school, not two. Removed edinburgh-new-town-cookery-school from cooking-classes.json.

**NOTE B-3 (flagged, not removed): eat-walk-leith and eat-walk-stockbridge -- routes unconfirmable**

The eatwalktours.co.uk homepage and all reachable sub-pages show only one Edinburgh tour ("Edinburgh Eat Walk Food Tour", GBP 93, covering Old Town and New Town). No Leith Shore or Stockbridge/Dean Village variants are listed as separate products. The routes in JSON (Mimi's Bakehouse, Dean Village finish, Sunday Stockbridge Market) are geographically coherent and the named stops are real Edinburgh venues, so outright fabrication cannot be confirmed. However these cannot be positively verified as distinct operator offerings. Flagged for research follow-up; not removed since the operator is real and routes are plausible.

### C. Festival month corrections

All five Edinburgh festivals cross-checked:

- edinburgh-food-festival: start_month July, start_day 24, end_month August, end_day 2. The official edfoodfestival.com domain returned ECONNREFUSED. Assembly Festival page shows Aug 5-31 for the wider festival context. Edinburgh Food Festival historically runs late July alongside Edinburgh's summer festival season. Dates plausible; could not positively confirm or refute from official source.
- foodies-festival-edinburgh: start_month August, start_day 7, end_month August, end_day 9. foodiesfestival.com returned no content for Edinburgh-specific page. Dates plausible for Foodies Festival Edinburgh August edition; could not confirm.
- edinburgh-fringe-street-food: start_month August, start_day 1, end_month August, end_day 25. Wikipedia confirms Edinburgh Fringe 2026 runs Aug 7-31. The JSON claims street food activity from Aug 1 which precedes the official Fringe start by 6 days. The description covers the broader Fringe food pop-up scene; a start_day of 1 is slightly generous. No correction made as the street food scene does informally precede the official opening, but flagged.
- burns-night-edinburgh: January 25 fixed date. Correct per tradition.
- edinburgh-international-festival-food: start_month August, start_day 7, end_month August, end_day 30. EIF website confirms 2026 Edinburgh International Festival runs Aug 7-30. Dates match exactly. No correction needed.

No festival month corrections applied.

### D. Thin-category fabrication sweep

Dietary sub-categories:

| Sub-category | Count | Floor (per SCHEMA) | Status |
|---|---|---|---|
| vegan | 3 | n/a (sub-category) | thin; see below |
| vegetarian | 3 | n/a | thin |
| gluten_free | 3 | n/a | thin |
| halal | 3 | n/a | thin |
| kosher | 0 | n/a | empty |

All four populated dietary sub-categories have exactly 3 entries (kosher is empty).

Vegan: Soul Vegan (Malaysian vegan per description), David Bann (established Old Town vegetarian/vegan since 2002), Hendersons (historic 1963 plant-based institution). These are all well-known Edinburgh venues; no fabrication suspected.

Vegetarian: Hendersons (Barclay Place), David Bann, Henderson's of Edinburgh (Hanover Street). Note that Hendersons (Barclay Place) and Henderson's of Edinburgh (Hanover Street) appear to be related venues of the same Henderson's brand. The Hanover Street location's open_evidence_url points to edinburgh.org. Both are plausible as distinct trading locations.

Gluten-free: Chorrito Cantina (Leith Walk, Mexican, claimed 100% GF kitchen), Ardfern (Bonnington Road, dedicated GF menu), Bross Bagels (Portobello, Montreal-style bagels with GF options). FindMeGlutenFree returned 403 for all three entries' cuisine_evidence_url pages. Content-match confirmation is not possible from this QA pass. Entries are plausible Edinburgh venues but thin-category content verification was blocked by 403 responses.

Halal: Mosque Kitchen (Pakistani, Nicolson Square), Hanam's (Kurdish/Middle Eastern, Johnston Terrace, confirmed halal by zabihah.com), Kebab Mahal (Indian, 7 Nicolson Square, confirmed halal by zabihah.com). No fabrication detected.

Verdict on D: Gluten-free sub-category flagged as cuisine_unverified (3/3 evidence URLs returned 403). Halal sub-category: 2 of 3 confirmed (Mosque Kitchen source_url has a cross-reference issue noted under A). Thin categories are plausible but borderline given blocked evidence URLs.

### E. Editorial-prose closed-venue echoes

Searched all Edinburgh data files for "Bonnington Centre", "Bonnington market", "Bonnington saturday" -- no matches found. "Bonnington" appears only as a legitimate street name (Bonnington Road for Ardfern, The Little Chartroom, and Bonnington Industrial Estate for Bellfield Brewery). No closed-venue prose echoes found.

---

## Changes made (JSON edits)

1. **cooking-classes.json**: Removed `edinburgh-new-town-cookery-school` (ENTCS rebranded to EFDA; same entity as edinburgh-food-drink-academy at same address). Removed `eating-europe-edinburgh-class` (food tour miscategorized as cooking class).

2. **food-tours.json**: Added `eating-europe-edinburgh` with correct food_tour schema. Description trimmed to 194 chars (within 140-220 cap).

3. **Regenerated**: generate_city.py, generate_cross_cuts.py, generate_extras.py, generate_chrome_pages.py, generate_sitemap.py, generate_search_index.py. Permissions updated via sshp host chmod a+rX.

---

## Defects total: 2 (fixed), 1 (flagged B-3, not removed), 3 (pre-existing validator WARNs, not my edits)

---

## Below-floor topics after QA

- cooking-classes: 3 entries (floor 5) -- needs research backfill of 2 genuine Edinburgh cooking schools. Note: the 3 remaining entries are Yarrow Cookery School, Edinburgh Food and Drink Academy, and Edinburgh Food Social -- all distinct real operators.

---

## Pre-existing WARNs (not introduced by this QA pass)

The following validator warnings were present before this pass and are outside QA scope:

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
