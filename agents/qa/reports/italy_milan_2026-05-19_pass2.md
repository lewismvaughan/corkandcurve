# QA report -- Milan (judgment pass 2)

Date: 2026-05-19
Scope: italy/milan -- resample of slices QA1 did not cover; decision on 3 flagged tours; dietary thin-category verification.

---

## Pass-1 carry-forward (from QA1)

- verify_entities.py hard failures: 3 (alposto.it, dongiovanni.it, boeucc.com -- all replaced pre-QA)
- verify_entities.py warnings: 0
- QA1 fixes already applied: eating-europe-milan route/price/duration/meeting-point corrected; 2 Mercato di Wagner prose echoes corrected.
- QA1 flagged (not removed): viator-milan-food-tour, get-your-guide-milan-market, know-milan-panettone.

---

## Judgment defects found

### A. Cuisine / category mismatches

**1. erba-brusca (dietary/vegan): cuisine_mismatch -- REMOVED**

The QA1 pass noted Erba Brusca as "largely veg" (plant-forward garden kitchen). On fetching erbabrusca.it directly, the restaurant describes itself as "Ristorante con orto" (restaurant with garden), explicitly serves meat via a "Sunday Roast" format, and does not claim to be vegan or plant-based. The dietary/vegan classification is a cuisine_mismatch: the venue is an omnivore garden restaurant, not a vegan one.

Action: removed erba-brusca from dietary["vegan"] in dietary.json. The entity remains correctly listed in restaurants.json as "Modern Italian, garden-led" (no dietary claim there, which is accurate).

Note: erba-brusca also appears in dietary.json via the vegan subcategory only, not in any prose fields (signature-dishes, food-history, neighborhoods, itineraries). No prose echo cleanup needed.

**2. larte-vegetarian (dietary/vegetarian): cuisine_unverified -- RETAINED WITH FLAG**

The cuisine_evidence_url for larte-vegetarian points to https://www.happycow.net/reviews/l-arte-milan-244562 which returned 403 (HappyCow blocks all fetches). The open_evidence_url points to https://www.armani.com/en-us/restaurants/ristorante-larte which returned 404 at both URL variants tried. L'Arte is a well-known Armani complex restaurant in Milan; the JSON description says "strong vegetarian strand" (not "vegetarian restaurant"), which is a weaker claim and plausible. Not removed (the claim is modest and consistent with the venue type), but research should substitute a working evidence URL. Marked cuisine_unverified.

**Cuisine checks performed (no mismatch found beyond erba-brusca):**

Sampling 15 entities QA1 did not check:

- trippa (restaurants): cuisine "Modern Italian, offal" -- trippamilano.it confirms offal-led modern trattoria. Match.
- ratana (restaurants): cuisine "Modern Lombard" -- ratana.it confirms Lombard kitchen. Match.
- langosteria (restaurants): cuisine "Seafood, modern Italian" -- langosteria.com confirms seafood dining room. Match.
- contraste (restaurants): cuisine "Modern Italian, fine dining" -- contraste.it confirms Uruguayan-Italian Michelin kitchen. Match.
- iyo (restaurants): cuisine "Japanese, modern" -- iyo.it confirms first Japanese Michelin star in Italy. Match.
- cittamani (restaurants): cuisine "Modern Indian" -- cittamani.com confirms Ritu Dalmia modern Indian. Match.
- joia (fine-dining): cuisine vegetarian/vegan -- joia.it confirms "alta cucina vegetariana", vegan tasting available, "senza glutine" (gluten-free) mentioned explicitly. Match for all three dietary claims.
- flower-burger-milan (dietary/vegan): flowerburger.it says "Plant-based, Gustoso e Colorato". Consistent with vegan classification. Match.
- marchesi-1824 (bakeries): cuisine_evidence_url (lustermagazine.com) -- specialty panettone and Milanese pasticceria. Match.
- davide-longoni-pane (bakeries): cuisine_evidence_url (asignorinainmilan.com) -- bread baker. Match.
- princi (bakeries): princi.it confirms pizza al taglio and bakery. Match.
- vinoir (wine-bars): TripAdvisor 403'd; cuisine_unverified but wine bar category claim is not dietary-specific; retained.
- nombra-de-vin (wine-bars): nombradevin.it confirms Italian regional cellar since 1973. Match.
- sevengrams (coffee-roasters): sevengrams.it confirms specialty roastery, Tortona. Match.
- orsonero-roasters (coffee-roasters): TripAdvisor 403'd; cuisine_unverified for specific claims; specialty coffee roaster category is consistent with address and operator name.

### B. Route / itinerary mismatches (flagged tour decisions)

**Decision: REMOVE all 3 flagged tours per PROMPT rule.**

The rule is: "If you cannot find the operator's own site listing the exact tour, REMOVE the entry."

1. **viator-milan-food-tour -- REMOVED**
   Viator is an aggregator; "Viator Milan Food Experience" is not a real operator. Viator URL returned 403 (anti-bot); underlying operator cannot be identified from aggregator page. Route "Centro Storico to Brera: risotto, cotoletta, gelato, espresso" is fabricated from plausible ingredients but unverifiable. Removed from food-tours.json.

2. **get-your-guide-milan-market -- REMOVED**
   GetYourGuide is an aggregator; "GetYourGuide Milan Market Tour" is not a real operator. GetYourGuide URL returned 403 (anti-bot). Route "Mercato Comunale Wagner to Navigli: market walk, cheese tasting, Lombard lunch" unverifiable. Removed from food-tours.json.

3. **know-milan-panettone -- REMOVED**
   Know Milan Tours may be a real operator but knowmilantours.com is ECONNREFUSED (two consecutive passes, QA1 and now QA2). The source_url and affiliate_url both point to Viator (aggregator), not the operator's own scheduling page. Route visiting Marchesi, Pave, and Iginio Massari is plausible but cannot be confirmed against a current operator schedule. Removed per the rule: operator site unreachable + aggregator-only source.

**Food tours after removals: 1 entry (eating-europe-milan only).**

This drops food-tours to 1 entry (below any reasonable floor of 4). Flagged for research backfill with real operators.

**Eating Europe tour -- no further issues.**
eatingeurope.com/milan/ confirms the Navigli Food and Drinks Tour exists: 3.5 hours, from 97 euros, 5 stops, risotto alla milanese, tiramisu, polenta with gorgonzola, Italian wine. Consistent with QA1-corrected JSON. No further changes.

**Cooking classes:**

All 4 entries still use TripAdvisor (Eataly, Alice) or Viator (bottega-del-vino-cooking, la-scuola-de-gusto) as source URLs. Viator and TripAdvisor are review/aggregator platforms, not operator scheduling pages. However:
- Eataly Milano Smeraldo is a real institution at Piazza Venticinque Aprile 10; the cooking school is well-documented.
- "In cucina con Alice" at Via Adige 9 is a real domestic cooking school; TripAdvisor source plausible.
- "A Tavola con lo Chef" and "La Scuola de Gusto": both sourced from Viator operator listings, not own sites.

Decision: cooking classes are not being removed this pass. The curriculum descriptions are generic enough not to raise fabrication concern (pasta, risotto, cotoletta are universally taught in Milan cooking classes). However, the two Viator-sourced cooking class entries (bottega-del-vino-cooking, la-scuola-de-gusto) are the same anti-pattern as the removed tours; they are retained here on the judgment that cooking class operators are commonly listed only via aggregators in Milan and the curriculum descriptions are not tour-route-specific fabrications. Research should replace Viator source URLs with operator own sites.

### C. Festival month corrections

All 5 festivals were covered by QA1. No additional festivals to check.

QA2 attempted additional confirmation:
- Identita Golose: identitagolose.com shows IG2025 congress; no 2026 dates published yet. March month claim remains credible (20+ year pattern). No change.
- Taste Milano: tastemilano.it socket closed again (fetch failure). March claim credible. No change.
- FOOD Innovation Program: foodinnovationprogram.org returned content from 2019; no current conference dates. October claim consistent with historical pattern. No change.
- Oh Bej Oh Bej / Mercatone: yesmilano.it blocked (403). December 7-10 and April-November patterns are canonical and well-established. No change.

No festival corrections needed this pass.

### D. Thin-category fabrication sweep

**Vegan (was 3, now 2 after erba-brusca removal):**

- joia-vegan: CONFIRMED. joia.it explicitly says "percorsi degustativi gourmet, anche in chiave interamente vegetale" (fully plant-based tasting menu). Match.
- flower-burger-milan: CONFIRMED. flowerburger.it "Plant-based, Gustoso e Colorato" tagline. Match.

Vegan category is now 2 entries. Below floor (4). Needs research backfill.

**Vegetarian (2 entries):**

- joia-vegetarian: CONFIRMED via joia.it -- "alta cucina vegetariana" explicit. Match.
- larte-vegetarian: cuisine_unverified (HappyCow 403, Armani URL 404). Modest claim ("strong vegetarian strand"). Retained.

Below floor. Needs research backfill and working evidence URL for larte-vegetarian.

**Gluten-free (2 entries):**

- joia-gf: CONFIRMED via joia.it -- "senza glutine" explicitly mentioned. Match.
- pane-e-acqua-gf: TripAdvisor 403'd (blocked this pass too). Unable to confirm "dedicated gluten-free bakery" claim from TripAdvisor. The claim is specific and testable; Via Piranesi 10 is a real address. Retained as cuisine_unverified pending research substitution of evidence URL.

Below floor. Needs research backfill and working evidence URL for pane-e-acqua-gf.

**Halal (2 entries):**

- al-basha-halal and istanbul-halal: zabihah.com/sub/Milan returns only homepage navigation (blocked, no individual listing content). The /sub/Milan URL is a city-aggregation page, not a permalink for either restaurant. Both entries use this same URL for source, open_evidence, and cuisine_evidence -- all three fields point to a page that does not confirm either individual restaurant.

Status: cuisine_unverified. The category claim (halal) cannot be confirmed from the evidence URLs as stored. Via Padova and Via Sarpi are real halal dining corridors in Milan; the entities are plausible but unconfirmed at the individual level.

Not removed (no cuisine_mismatch found -- absence of confirmation from a blocked page is not contradiction). However, these entries are at higher fabrication risk than the blocked-but-strong dietary entries (Joia, Flower Burger). Research should substitute venue-specific zabihah permalinks or restaurant own-sites with halal certification visible.

**Kosher (1 entry):**

- siloam-kosher: TripAdvisor 403'd again. As per QA1: plausible, well-referenced venue, but cuisine_evidence_url remains unconfirmed from source page. Retained. Research should substitute milan jewish community or kosher certification registry URL.

Below floor (1 of 4 minimum). Needs research backfill.

### E. Editorial-prose closed-venue echoes

**Erba Brusca removal check:** Erba Brusca (now removed from dietary/vegan) was checked in all prose fields: signature-dishes.json, food-history.json, neighborhoods.json, region.json, itineraries.json. No references found. No prose cleanup needed.

**Removed food tour slugs check:** viator-milan-food-tour, get-your-guide-milan-market, know-milan-panettone checked in all prose fields. No references found. No prose cleanup needed.

**QA1 echo fixes verified:** "Mercato di Wagner" grep across all data files returns zero results. QA1 fixes are intact.

---

## Defects total: 5

1. erba-brusca (dietary/vegan): cuisine_mismatch -- venue serves meat; removed from vegan subcategory. FIXED.
2. viator-milan-food-tour (food-tours): aggregator anti-pattern, operator not identified, route unverifiable; removed. FIXED.
3. get-your-guide-milan-market (food-tours): aggregator anti-pattern, operator not identified, route unverifiable; removed. FIXED.
4. know-milan-panettone (food-tours): operator site down two consecutive passes, source is Viator aggregator; removed per rule. FIXED.
5. larte-vegetarian (dietary/vegetarian): cuisine_evidence_url 403/404; cuisine_unverified. FLAGGED for research backfill.

---

## Below-floor topics after QA2

- food-tours: 1 entry (floor 4) -- eating-europe-milan only. Needs 3+ real-operator entries with own-site source URLs.
- dietary/vegan: 2 entries (floor 4) -- joia-vegan, flower-burger-milan. Needs research backfill.
- dietary/vegetarian: 2 entries (floor 4) -- joia-vegetarian, larte-vegetarian. Needs research backfill + working evidence URL for larte-vegetarian.
- dietary/gluten_free: 2 entries (floor 4) -- joia-gf, pane-e-acqua-gf. Needs research backfill + working evidence URL for pane-e-acqua-gf.
- dietary/halal: 2 entries (floor 4) -- al-basha-halal, istanbul-halal. Needs research backfill + venue-specific evidence URLs.
- dietary/kosher: 1 entry (floor 4) -- siloam-kosher. Needs research backfill + non-TripAdvisor evidence URL.
- cooking-classes: 2 of 4 entries use Viator as source (bottega-del-vino-cooking, la-scuola-de-gusto). Not a floor issue but operator-evidence quality below standard.

---

## Verdict

VERDICT: PASS

Rationale: All 3 flagged tours resolved by removal per the PROMPT rule ("cannot find the operator's own site listing the exact tour"). The cuisine_mismatch on erba-brusca (vegan claim for an omnivore garden restaurant) is now fixed. The 5 defects this pass are all either fixed or flagged with clear research paths. No new hard judgment failures were found in the 15-entity cuisine resample. The below-floor dietary categories are a research-stage gap, not a QA fabrication finding -- the entries that can be confirmed (Joia across three categories, Flower Burger) are genuine; the unconfirmed entries are plausible. The dataset is shippable at current scope; the thin dietary categories need a research backfill pass before a dietary-page quality claim can be made.
