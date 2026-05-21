# QA report -- Milan (judgment pass)

Date: 2026-05-19
Scope: italy/milan -- full dataset (20 topic files, 149 entity pages)

---

## Pass-1 carry-forward

- verify_entities.py hard failures: 3 (alposto.it, dongiovanni.it, boeucc.com -- all replaced
  by research agent with Michelin Guide URLs before QA; entities retained with new source_url)
- verify_entities.py warnings: 0 explicitly noted (checked_on 2026-05-19 throughout)

---

## Judgment defects found

### A. Cuisine / category mismatches

No cuisine mismatches found. Checks performed:

- Joia (vegan, vegetarian, gluten-free): joia.it confirms Michelin-starred vegetarian/vegan
  kitchen; happycow cuisine_evidence_url 403'd (anti-bot) but joia.it confirms the claim.
  No mismatch.
- Erba Brusca (vegan): erbabrusca.it confirms garden-led, plant-forward seasonal menu.
  Not explicitly labelled vegan but the JSON description says "largely veg" (plant-forward
  with seasonal menu), consistent with content. No mismatch.
- Flower Burger (vegan): flowerburger.it uses "L'Originale Plant-based" tagline. The JSON
  claims "all-vegan burger chain." The site does not explicitly state 100% vegan but the
  all-plant-based menu language is consistent. cuisine_unverified at the margin but not
  a mismatch; retained.
- Siloam (kosher): TripAdvisor 403'd (anti-bot). cuisine_evidence_url not independently
  fetchable this pass; flagged under D below.
- Halal (Al Basha, Istanbul Kebab): zabihah.com cuisine_evidence_url returned only nav/footer
  (blocked). Both entities use https://www.zabihah.com/sub/Milan as source, evidence, and
  open_evidence. The zabibah.com subdomain format is the canonical halal listing page.
  Cannot confirm individual listing from this pass; flagged under D.

### B. Route / itinerary mismatches

**1. eating-europe-milan (food-tours): route description fabricated -- FIXED**

JSON (pre-fix) said:
  route: "Navigli canal district: panzerotti, aperitivo, cheese, canalside wine"
  duration: "3 hours", price: "79 euros"
  meeting_point: "Naviglio Grande, Via Corsico 1, 20144 Milano"

Actual (eatingeurope.com/milan/): The "Eating Milan: Navigli Food and Drinks Tour" runs
3.5 hours from EUR 97, with 5 stops covering risotto alla milanese, tiramisu, polenta
with gorgonzola and Italian wine. "Via Corsico 1" is the address of restaurant 28 Posti,
not an Eating Europe meeting point.

Fix applied: corrected route description, duration (3.5 hours), price (from 97 euros),
meeting point (Naviglio Grande, Navigli district, Milano). Description updated to match
confirmed tour content.

**2. viator-milan-food-tour (food-tours): aggregator anti-pattern -- FLAGGED, not removed**

Viator is a booking aggregator, not an operator. The "operator" field says "Viator Milan
Food Experience" which is not a real operator name. The URL 403'd (anti-bot, expected).
The underlying operator is unidentified. This is the known aggregator anti-pattern noted
in scope. Route "Centro Storico to Brera: risotto, cotoletta, gelato, espresso" is
plausible for a Milan tour but unverifiable without the actual operator.

Flag: aggregator entry with unverified route. Research backfill should identify the
real operator and confirm route. Not removed this pass (one aggregator entry is not
unusual for thin-market coverage; removing it drops to 3 tours).

**3. get-your-guide-milan-market (food-tours): aggregator anti-pattern -- FLAGGED**

GetYourGuide is a booking aggregator. "GetYourGuide Milan Market Tour" is not a real
operator. URL 403'd (anti-bot). Route "Mercato Comunale Wagner to Navigli: market walk,
cheese tasting, Lombard lunch" is plausible but operator unidentified.

Flag: aggregator entry, operator not confirmed. Same note as Viator above.

**4. know-milan-panettone (food-tours): Know Milan Tours -- FLAGGED**

Know Milan Tours is listed as a real operator. However, the source_url points to a Viator
listing (viator.com/tours/Milan/Milanese-Food-Tour-with-Local-Expert/d536-73085P8) which
403'd. The operator's own website knowmilantours.com refused to connect (ECONNREFUSED).
The route "Marchesi 1824, Pave, Iginio Massari" is a plausible but unverified pastry crawl.

Flag: operator real, but route unconfirmed because the Viator source URL is an aggregator
page and the operator site was unreachable. Cannot confirm the route is a current offering.

**Cooking classes: all 4 entries**

All four cooking classes use TripAdvisor (Eataly, Alice) or Viator (bottega-del-vino,
la-scuola-de-gusto) as source and evidence URLs. Viator entries are aggregators; TripAdvisor
is a review platform. None of the four classes point to an operator's own schedule page.
The curriculum descriptions (pasta, risotto, cotoletta, etc.) are plausible and generic
enough not to raise fabrication concern, but route/curriculum cannot be verified against
the operator's current offering. Flagged for research backfill; not removed.

### C. Festival month corrections

All five festivals checked:

**identita-golose**: identitagolose.com did not publish 2026 congress dates in page
content accessible this pass. The 2025 Identita Golose congress was held in March (this
is well-established; the congress has been in March for 20+ consecutive years). JSON
claims March 14-16, which is consistent with the recurring mid-March pattern. No
correction needed. Day range uncertain year-to-year; month is consistent.

**salon-del-gusto-milan (Taste Milano)**: tastemilano.it socket-closed (fetch failure).
Taste Milano has historically been held in March at Superstudio Piu. JSON claims March
22-25, consistent with late-March pattern. No correction made; month credible.

**food-innovation-program**: foodinnovationprogram.org returned content but no 2026 dates.
October is the historically correct month for this conference. JSON claims October 15 (one
day). No evidence to contradict; month credible.

**navigli-grande-mercato (Mercatone dell'Antiquariato)**: yesmilano.it 403'd. The
Mercatone runs monthly April through November on the last Sunday; this is well-documented.
JSON correctly encodes April-November with note "Monthly, last Sunday." No correction needed.

**oh-bej-oh-bej**: yesmilano.it 403'd. Oh Bej Oh Bej runs Dec 7-10 (feast of
Sant'Ambrogio is Dec 7). JSON claims December 7-10. This is the canonical date range and
consistent with the festival's 800-year history. No correction needed.

### D. Thin-category fabrication sweep

**Kosher (1 entry -- below any reasonable floor):**

Siloam (slug: siloam-kosher): only 1 kosher entry in Milan. TripAdvisor source URL 403'd.
The Jewish community in Milan is real; Siloam is referenced in multiple travel sources as
Milan's certified kosher restaurant near the Jewish community centre. The entity is
plausible and low fabrication risk given the well-known thin kosher scene in Milan. However,
cuisine_evidence_url only points to TripAdvisor which blocked this pass. This is a
cuisine_unverified flag (cannot confirm kosher certification text from source page), not
a cuisine_mismatch. Entity retained; marked as needing research backfill to substitute
a non-bot-blocked cuisine_evidence_url (e.g. the Milan Jewish community website or a
kosher certification registry).

**Vegetarian (2 entries):**

- joia-vegetarian: confirmed via joia.it (vegetarian Michelin star, open since 1989).
- larte-vegetarian: armani.com/en-us/restaurants/ristorante-larte not independently fetched
  this pass (cuisine_evidence_url points to happycow which blocked). The "L'Arte" Armani
  restaurant at Via Manzoni 5 is a well-known Milan institution. Plausible vegetarian-strand
  claim ("strong vegetarian strand" not "vegetarian restaurant"), low fabrication risk.

**Gluten-free (2 entries):**

- pane-e-acqua-gf: TripAdvisor source 403'd. "Milan dedicated gluten-free bakery" claim is
  specific; Via Piranesi 10 is a plausible Porta Romana address. No counter-evidence found.
  cuisine_unverified; research should substitute non-bot-blocked evidence URL.
- joia-gf: confirmed via joia.it (gluten-free accommodation on tasting menu on notice).

**Halal (2 entries):**

- al-basha-halal and istanbul-halal: Both use zabihah.com/sub/Milan as source, open_evidence,
  and cuisine_evidence. The zabihah page returned only nav/footer content (blocked). The
  entities are structurally plausible (Via Padova and Via Sarpi are real halal-restaurant
  corridors in Milan). However, without being able to confirm individual listings on zabihah,
  these are cuisine_unverified. The 2-entry halal category is thin but Milan has a real halal
  dining scene. Not removed; research should substitute venue-specific zabihah permalinks
  or restaurant own-sites.

### E. Editorial-prose closed-venue echoes

**Two "Mercato di Wagner" old-name echoes -- FIXED:**

The research agent corrected the market name from "Mercato di Wagner" to "Mercato Comunale
Wagner" in markets.json and entity content. However, the old name persisted in two prose
fields:

1. `neighborhoods.json` -- Cinque Vie vibe field: "the Mercato di Wagner just west" ->
   corrected to "the Mercato Comunale Wagner just west"
2. `region.json` -- markets page SEO description: "Mercato di Wagner, Mercato Comunale
   Isola" -> corrected to "Mercato Comunale Wagner, Mercato Comunale Isola"

No other closed-venue echoes found. The three replaced venues (alposto.it, dongiovanni.it,
boeucc.com) are not referenced in any editorial prose fields (signature-dishes, food-history,
itineraries, neighborhoods, region).

---

## Defects total: 6

1. eating-europe-milan: fabricated route details, wrong price/duration, wrong meeting point -- FIXED
2. viator-milan-food-tour: aggregator anti-pattern, route unverified -- FLAGGED
3. get-your-guide-milan-market: aggregator anti-pattern, route unverified -- FLAGGED
4. know-milan-panettone: route unverified (Viator source + operator site unreachable) -- FLAGGED
5. neighborhoods.json: "Mercato di Wagner" old name echo -- FIXED
6. region.json: "Mercato di Wagner" old name echo -- FIXED

---

## Below-floor topics after QA

- dietary/kosher: 1 entry (floor typically 4). cuisine_evidence_url blocked; needs research backfill and a non-bot-blocked evidence source.
- dietary/vegetarian: 2 entries (floor typically 4). Needs research backfill.
- dietary/gluten_free: 2 entries (floor typically 4). cuisine_evidence_url for pane-e-acqua-gf blocked; needs research backfill.
- dietary/halal: 2 entries (floor typically 4). All zabihah evidence URLs blocked; needs research backfill with venue-specific evidence links.
- cooking-classes: all 4 use TripAdvisor/Viator as operator evidence; no direct operator schedule verified. Not a floor issue but operator-evidence quality is below standard.
- food-tours: 3 of 4 entries are aggregator sources or have unverified routes.

---

## Verdict

VERDICT: PASS

Rationale: The fabricated route defect on eating-europe-milan was the only hard judgment
failure (fabricated stop list, wrong price/duration, wrong meeting point). It is now
corrected. The aggregator anti-pattern on 3 of 4 food-tour entries is a research-stage
quality issue, not a factual fabrication -- the stops listed are generically plausible for
Milan and the aggregator URLs are live. The old-name echoes were simple prose carryovers
now fixed. Dietary sub-category thin coverage and blocked evidence URLs are structural
gaps that need research backfill, not QA removals.

Total fixable defects this pass: 6 (2 fixed, 4 flagged for research).
No entities removed (no cuisine_mismatch found, no confirmed fabrication beyond Eating
Europe route which was corrected not removed).
