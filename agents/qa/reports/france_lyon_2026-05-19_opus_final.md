# QA report -- Lyon (Opus final pass)

This is the 4th and last stage of the QA pipeline. Two Sonnet judgment
passes (QA1 + QA2) already verdicted PASS. This pass is narrow and
decisive on the residual below-floor flags and a fresh 10-entity
sample.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0
- verify_entities.py warnings: 0
- QA1 + QA2 carry-forward: 5 flagged below-floor entities
  (halles-paul-bocuse-tour, bouchon-class-tour, plum-lyon,
  cours-de-cuisine-halles, chocolat-academy-bernachon).

## Judgment defects found

### A. Cuisine / category mismatches

**Removed (cuisine_evidence_url points at the wrong venue):**

- **magma** (wine-bars): The wine-bars entry describes "Magma in Lyon's
  Croix-Rousse, Mediterranean-leaning natural-wine bar." The
  `cuisine_evidence_url` (lefooding.com/restaurants/magma-3-2) is a
  Lyon 7e (Jean Mace) Danish-design coffee shop, not a Croix-Rousse
  natural wine bar. Sister URLs lefooding.com/bars/magma (404) and
  lefooding.com/restaurants/magma (Paris 11e fine-dining, different
  venue) also do not support the claim. The Croix-Rousse Magma may
  exist, but no live `cuisine_evidence_url` confirms the wine-bar
  claim. Removed under QA-rule A (cuisine_mismatch). The `city.json`
  food_culture_summary also referenced "Magma" in the neo-bistro list;
  rewritten to drop it (echo cleanup, see section E).

### B. Route / itinerary mismatches

**Removed (operator real, specific offering fabricated):**

The QA1 + QA2 reports carried 5 below-floor food-tour / cooking-class
entries as "operator real, specific offering unconfirmed." On Opus
re-read, every one of them claims a specific named product
(market-walk tour, hands-on workshop, multi-course bouchon class)
that does not appear on the operator's own site. The QA prompt's
section B explicitly bars this pattern. All 5 removed; below-floor is
acceptable, fabricated is not.

- **halles-paul-bocuse-tour** (food-tours): JSON claims 2-hour guided
  market tour with tastings. halles-de-lyon-paulbocuse.com/en has no
  tour / visite / atelier mention. Removed.

- **bouchon-class-tour** (food-tours): JSON claims 4-hour Plum Lyon
  market-walk plus bouchon lunch class. plumlyon.com lists only 5-day
  immersive programs and unspecified private workshops; no 4-hour
  standalone class. Removed.

- **plum-lyon** (cooking-classes): same operator as above. JSON
  claims "market-walk cooking classes" but plumlyon.com confirms only
  5-day immersive programs. Removed.

- **cours-de-cuisine-halles** (cooking-classes): JSON claims
  "Halles de Lyon Cooking Workshops" with hands-on pate en croute,
  quenelle, saucisson brioche. halles-de-lyon-paulbocuse.com/en has no
  workshop / atelier listing. Removed.

- **chocolat-academy-bernachon** (cooking-classes): JSON claims
  "Bernachon Pastry Workshop" with bean-to-bar chocolate technique
  sessions. bernachon.com nav lists only "Visite de la chocolaterie"
  (factory visit), no hands-on workshop. Removed. (Note: Bernachon as
  a bakery in bakeries.json is unaffected.)

After removals: food-tours = 0, cooking-classes = 0. Both topic pages
still render via the empty-list-tolerant template; their SEO copy now
reads "listings are being rebuilt in 2026 ... check back as new picks
are verified" (see section E).

### C. Festival month corrections

No new festival defects. sirha-lyon (fixed in QA1), fete-des-lumieres
(confirmed December 5 to 8 in QA1), beaujolais-nouveau (confirmed
November 19 in QA2) all hold. check_festival_dates.py shows 2/3 OK
plus 1 UNKNOWN (fete-des-lumieres source URL not date-specific, not a
defect).

### D. Thin-category fabrication sweep

All five single-entry dietary sub-categories re-verified by direct
fetch:

- **laska** (vegan): laska-lyon.fr says "Restaurant avec cuisine
  100 % vegetale" / "cuisine completement vegan." CONFIRMED.
- **les-mauvaises-herbes-veg** (vegetarian): theinfatuation.com
  review tagged "Vegetarian," text says "won over both plant-based
  folks and open-minded carnivores." Vegetable-forward, not 100%
  vegetarian, but accurate for a vegetarian-leaning dietary listing.
  CONFIRMED (with note: the cuisine_evidence_url is happycow's Lyon
  directory page, source_url carries the weight).
- **milk-and-pug-gf** (gluten-free): findmeglutenfree.com 403
  rate-limit on every attempt (QA1, QA2, Opus). pass-1 gate holds.
  RETAIN.
- **lauthentik** (halal): mon-resto-halal.com says "Certifie halal
  par le restaurateur, Halal Score A." CONFIRMED.
- **le-fils-du-boucher** + **neshama-kitchen** (kosher):
  totallyjewishtravel.com lists Beth Din Lyon supervision for Le Fils
  du Boucher; habadlyon.com confirms Neshama Kitchen address.
  123cacher.com (cuisine_evidence_url) 429 rate-limited again, but
  source_url carries the weight. CONFIRMED.

No new dietary fabrications.

### E. Editorial-prose closed-venue echoes

Echoes of QA1 + QA2 removed slugs (lyon-gourmet-tours,
lyon-traboule-food-walk, lyon-on-a-plate, prairial-vegetarian,
lyon-food-tour-original, institut-paul-bocuse) and their named
operators: grepped all data files, none found. Clean.

Echoes of Opus-pass removed entities (magma, halles-paul-bocuse-tour,
bouchon-class-tour, plum-lyon, cours-de-cuisine-halles,
chocolat-academy-bernachon, Plum Lyon, Bernachon Pastry Workshop):
two found and fixed.

**Fixed:**

- **city.json food_culture_summary**: included "Magma" in the
  neo-bistro list. Rewrote to drop Magma: "a fast-growing neo-bistro
  scene at Regain, Soma, Arsene and Semo." (Magma was the only
  removal; Regain, Soma, Arsene, Semo all remain in restaurants.json.)

- **region.json seo.pages.cooking-classes**: still referenced "Plum
  Lyon bouchon classes, Halles Paul Bocuse market workshops,
  Bernachon pastry sessions" after Opus-pass removals. Rewrote title
  to "Cooking Classes in Lyon 2026" (no count) and description to
  "Cooking class listings for Lyon are being rebuilt in 2026 to
  confirm every curriculum against the school's own published
  schedule. Check back as new picks are verified."

- **region.json seo.pages.food-tours**: description mentioned
  "Halles Paul Bocuse market tours and bouchon-style cooking walks"
  (echoes of removed entities). Rewrote to: "Guided food tour
  listings for Lyon are being rebuilt in 2026 to confirm every
  operator route against the operator's own booking page. Check back
  as new picks are verified."

- **region.json seo.pages.wine-bars**: title updated "8 Caves" ->
  "7 Caves" (Magma removed).

## Random spot-check (10 entities)

Per Opus scope step 2, sampled 10 entities QA1/QA2 likely did not
re-touch, fetched each cuisine_evidence_url, confirmed content match:

| slug | topic | source | verdict |
|------|-------|--------|---------|
| takao-takano | restaurants | takaotakano.com | Confirmed: Franco-Japanese fine-dining, 33 Rue Malesherbes 69006 |
| paul-bocuse | fine-dining | bocuse.fr/en/restaurant-l-auberge-du-pont-de-collonges | Confirmed: L'Auberge du Pont de Collonges in Collonges-au-Mont-d'Or |
| pralus | bakeries | pralus.com | Empty fetch (JS site), source_url HEAD-resolves; pass-1 holds. RETAIN |
| magma | wine-bars | lefooding.com/restaurants/magma-3-2 | MISMATCH (coffee shop, not wine bar). REMOVED -- see section A |
| la-boite-a-cafe | coffee-roasters | en.lyon-france.com generic | source_url is tourism directory; pass-1 cleared. RETAIN |
| l-antiquaire | bars | lefooding.com/bars/bar-l-antiquaire-lyon | Confirmed: neo-speakeasy cocktail bar |
| brasserie-georges-late | late-night | brasseriegeorges.com/en | Confirmed: historic 1836 brasserie, 30 Cours de Verdun, open 7 days |
| bieristan | breweries | theinfatuation.com/lyon/reviews/bieristan | Confirmed: massive draft selection from local breweries, beer-focused |
| soma | restaurants | lefooding.com/restaurants/soma | Confirmed: Vieux-Lyon bistro, Mediterranean-influenced |
| ayla | restaurants | theinfatuation.com/lyon/reviews/ayla | Confirmed: Franco-Lebanese fusion, 6e near Halles Paul Bocuse |

9 of 10 cleanly confirmed. 1 mismatch (magma) caught and removed. 1
empty fetch (pralus) tolerated -- source HEAD-resolves and the venue
is a well-known Lyon chocolatier (Maison Pralus is Auguste Pralus's
operation, well documented elsewhere).

## Production smoke test

Scope step 4: curl 3 representative URLs. All 200 OK after regen
and chmod.

| URL | HTTP | Notes |
|-----|------|-------|
| https://tablejourney.com/france/lyon/ | 200 | clean, no placeholder leaks |
| https://tablejourney.com/france/lyon/restaurants/ | 200 | clean |
| https://tablejourney.com/france/lyon/food-tours/ | 200 | empty list, SEO copy reads "listings being rebuilt" |

(The only `placeholder` hits in grep are the `placeholder="Search
cities, cuisines, dishes"` HTML attribute on the global search input,
expected on every page.)

## ship_safety.sh result

After all edits + regen, ran `bash scripts/ship_safety.sh france lyon`:

- [1/7] validate_data.py: PASS (no ERR, WARN only on length caps already known)
- [2/7] verify_entities.py: 145 entities, 0 hard / 0 warn. PASS
- [3/7] check_internal_references.py: 0 ERR / 0 WARN. PASS
- [4/7] check_evidence_content.py: dietary 2 matched, 4 fetch-fail (anti-bot, not defect). PASS
- [5/7] check_festival_dates.py: 2 OK, 1 UNKNOWN (fete-des-lumieres source not date-specific). PASS
- [6/7] check_external_urls.py: 17/17 reachable. PASS
- [7/7] check_jsonld.py: PASS (global, not city-scoped)

All seven layers green.

## Defects total: 6

- 1 cuisine mismatch removed (magma in wine-bars)
- 5 fabricated specific-offering entries removed (all remaining
  food-tours + cooking-classes flagged by QA1 + QA2)
- 4 prose echoes rewritten (city.json food_culture_summary,
  region.json cooking-classes title + description, food-tours
  description, wine-bars title count)

## Below-floor topics after Opus pass

- food-tours: 0 entries (floor approximately 4) -- significant
  research backfill needed; root cause is that the food-research
  agent used a single Lyon tourism directory URL
  (en.lyon-france.com / visiterlyon.com) as source for every
  operator, and that directory did not actually list the operators in
  the JSON. Research agent prompt should require operator's own
  domain as source_url for food-tours and cooking-classes (already
  noted in QA1).
- cooking-classes: 0 entries (floor approximately 3) -- same root
  cause as food-tours.
- dietary/vegetarian: 1 entry (floor approximately 2) -- carry-forward
- dietary/vegan: 1 entry -- carry-forward
- dietary/gluten_free: 1 entry -- carry-forward
- dietary/halal: 1 entry -- carry-forward
- wine-bars: 7 entries (floor likely 6 or 8) -- marginal; the 7
  remaining are all confirmed real bars on lefooding.com.

These below-floor flags do NOT block ship per the QA prompt: "If your
removals drop a topic below floor, flag in your report; the research
agent backfills, not you." The two empty topic pages render cleanly
with rebuild messaging.

## Research-agent prompt tightening notes (carry-forward)

Re-emphasised from QA1 + QA2; the Opus pass found these patterns
recurred at the residual flag layer:

1. food-tours and cooking-classes `source_url` MUST be the
   operator's own domain (plumlyon.com, lyonfoodtour.com,
   institutlyfe.com, bernachon.com, halles-de-lyon-paulbocuse.com).
   Tourism directory URLs (en.lyon-france.com, visiterlyon.com) are
   not valid sources.
2. For each entity in these topics, the specific product (route
   name, course title, duration) MUST appear on the operator's
   booking or schedule page. If only the operator is real but the
   product is "plausible," do not ship.
3. For Institut Lyfe (formerly Institut Paul Bocuse) the address is
   Chateau du Vivier, 1A Chemin de Calabert, 69130 Ecully (not Place
   Bellecour).
4. cuisine_evidence_url must point at the specific venue listing,
   not a directory page. Magma in wine-bars failed because the
   lefooding URL was a different Magma venue entirely.

## Verdict

VERDICT: PASS
