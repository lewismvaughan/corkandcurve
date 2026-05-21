# QA report -- Lyon (judgment pass 2)

## Pass-1 carry-forward (from QA1 report)

- verify_entities.py hard failures: 0
- verify_entities.py warnings: 0
- QA1 defects already fixed: 4 tour fabrications removed, 1 festival date fixed,
  1 SEO prose echo fixed, 1 cuisine mismatch removed.

## Judgment defects found

### A. Cuisine / category mismatches

No new cuisine mismatches found in pass-2.

Sampled and confirmed:
- `laska` (dietary/vegan): laska-lyon.fr confirms "100% vegetable cuisine, completely vegan". PASS.
- `les-mauvaises-herbes-veg` (dietary/vegetarian): theinfatuation.com review confirms vegetarian,
  "one of the first restaurants to cater to Lyon's herbivores", address 3 Rue du Jardin des Plantes
  confirmed. PASS. Note: cuisine_evidence_url points to happycow.net/europe/france/lyon/ (directory
  page rather than specific listing) -- the source_url carries the verification weight here.
- All fine-dining entries: cuisine_evidence_url is operator own site or theinfatuation.com review;
  no mismatches found on spot-checks.

### B. Route / itinerary mismatches

**Removed (operator real, specific route/format fabricated):**

- **lyon-food-tour-original** (food-tours): Operator Lyon Food Tour is confirmed real at
  lyonfoodtour.com. However, the JSON described a "3.5-hour Vieux Lyon bouchon crawl with stops at
  four traditional bouchons, plus a guided walk through Halles Paul Bocuse" with meeting point
  "Place Saint-Jean." The operator's site lists these as separate offerings: a 3h Vieux Lyon tour
  (1.8 km) and a standalone 2.5h Halles de Lyon tour. No combined 3.5h bouchon-plus-Halles tour
  appears in any named listing. Meeting point "Place Saint-Jean" not confirmed. Source URL was the
  generic tourism office URL (same pattern as QA1 fabrications). Removed.

**Removed (fabricated address, outdated name):**

- **institut-paul-bocuse** (cooking-classes): QA1 flagged this for research update. Pass-2
  confirms removal is appropriate: the school rebranded to Institut Lyfe and moved; its real
  address is Chateau du Vivier, 1A Chemin de Calabert, 69130 Ecully -- NOT 20 Place Bellecour as
  stated. The source_url (generic tourism office cookery-workshops page) does not list this operator.
  The tip ("Saturday-only bouchon class") is unverifiable. Fabricated address + unverified
  curriculum = remove. Research agent should re-enter as Institut Lyfe with the Ecully address
  confirmed from institutlyfe.com.

**QA1 flagged, not escalated (retain with caveat):**

- **halles-paul-bocuse-tour** (food-tours): Halles de Lyon-Paul Bocuse website does not confirm
  guided tours. No new evidence found. Retaining per QA1 decision (market is real); remains flagged
  for research verification.
- **bouchon-class-tour / plum-lyon** (food-tours / cooking-classes): Plum Lyon site confirms
  5-day immersive programs but no standalone 4-hour market-walk class. Retaining per QA1 decision
  (operator real); flagged for research verification of standalone offering.
- **cours-de-cuisine-halles** (cooking-classes): No workshop program confirmed on Halles site.
  Retaining per QA1 decision; flagged for research.
- **chocolat-academy-bernachon** (cooking-classes): Bernachon site shows only a "Visite de la
  chocolaterie" (factory visit) in navigation -- no hands-on pastry workshop page found. Retaining
  per QA1 decision (operator real); flagged for research.

### C. Festival month corrections

No new festival month errors found.

- `beaujolais-nouveau`: Third Thursday of November confirmed as 19 November 2026.
  JSON start_day: 19 -- matches. PASS.
- `fete-des-lumieres`: December 5 to 8 confirmed per QA1. PASS.
- `sirha-lyon`: Fixed by QA1. PASS.

### D. Thin-category fabrication sweep

No new thin-category fabrications found in pass-2. Re-checked all four single-entry dietary
sub-categories with fresh evidence:

- `laska` (vegan): laska-lyon.fr confirms 100% vegan. CONFIRMED.
- `les-mauvaises-herbes-veg` (vegetarian): theinfatuation.com confirms vegetarian. CONFIRMED.
- `milk-and-pug-gf` (gluten-free): findmeglutenfree.com was 403 rate-limited at QA1 and again
  at pass-2. Source URL pass-1-cleared. No new contradicting evidence. RETAIN (pass-1 gate holds).
- `lauthentik` (halal): mon-resto-halal.com URL pass-1-cleared at QA1. RETAIN.
- `le-fils-du-boucher` / `neshama-kitchen` (kosher): pass-1-cleared at QA1. RETAIN.

### E. Editorial-prose closed-venue echoes

Two new prose echoes found and fixed. Removed slugs this pass: lyon-food-tour-original,
institut-paul-bocuse.

**Fixed:**

- **region.json seo.pages.food-tours.title**: Stale count "6 Picks to Book" (was correct before
  QA1 removed 3 + pass-2 removed 1 = only 2 tours remain). Changed to "Picks to Book" (no count,
  avoids staleness).

- **region.json seo.pages.food-tours.description**: "Vieux Lyon traboule walks" was an echo of
  the removed lyon-traboule-food-walk (QA1 removal) and the style of lyon-food-tour-original
  (pass-2 removal). Updated to "Halles Paul Bocuse market tours and bouchon-style cooking walks."

- **region.json seo.pages.cooking-classes.title**: Stale count "6 Schools" -- only 3 remain after
  QA1 removal of lyon-on-a-plate + pass-2 removal of institut-paul-bocuse. Fixed to "3 Schools."

- **region.json seo.pages.cooking-classes.description**: Referenced "Institut Paul Bocuse short
  courses" (removed entity with old name). Updated to reference Plum Lyon, Halles Paul Bocuse
  workshops, and Bernachon pastry sessions -- the actual remaining entities.

No echoes found in: itineraries, food-history, signature-dishes, neighborhoods, festivals,
bars, street-food, markets, fine-dining, restaurants, casual-dining, seasonal-food, day-trips-food.

## Defects total: 6

- 1 food-tour route fabrication removed (lyon-food-tour-original)
- 1 cooking-class fabricated-address + wrong-name entity removed (institut-paul-bocuse)
- 4 prose echoes fixed (region.json food-tours title, food-tours description,
  cooking-classes title, cooking-classes description)

## Below-floor topics after QA

- food-tours: 2 entries (floor approximately 4) -- both are flagged as unverified operator
  offerings; needs significant research backfill
- cooking-classes: 3 entries, all with unconfirmed specific offerings -- needs research verification
- dietary/vegetarian: 1 entry (floor approximately 2) -- carry-forward from QA1
- dietary/vegan: 1 entry -- carry-forward from QA1
- dietary/gluten_free: 1 entry -- carry-forward from QA1
- dietary/halal: 1 entry -- carry-forward from QA1

## Research-agent prompt tightening notes (carry-forward from QA1)

- food-tours and cooking-classes source_url must be the operator's own website, not a tourism
  directory page.
- For cooking-classes, the specific curriculum (course name on operator's booking page) must be
  confirmed before the entity is written.
- Institut Lyfe (formerly Institut Paul Bocuse) should be re-entered with the correct name, Ecully
  address (1A Chemin de Calabert, 69130 Ecully), and a source_url pointing to institutlyfe.com.

## Verdict

VERDICT: PASS
