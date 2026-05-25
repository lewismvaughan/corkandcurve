# Opus final QA — france/champagne — 2026-05-25

Agent: Opus final QA (narrow read; confirm QA1+QA2 fixes held, sample for
fabrication, end-to-end one itinerary + one festival, spot-check high scores
and taste re-anchors). Did NOT redo QA1 (A/B/C/F/L) or QA2 (D/E/G/H/I/J/K)
sweeps. No re-HEAD of URLs ship_safety already checks.

Entry state: QA1-COMPLETE (38 corrected) + QA2-COMPLETE (21 corrected),
ship_safety PASS 0 HARD.

## Result: OPUS-CLEAR france/champagne

No material defects found. Zero edits made. ship_safety re-confirmed PASS,
0 HARD (no edits, so the entry-state result stands).

---

## What I checked and found clean

### Classification (QA1 fixes + cuvée/producer level)
- wines.json: 93/93 cuvées classification == "AOC Champagne". vineyards.json:
  39/39 == "AOC Champagne". budget-wines: 10/10 "Champagne AOC".
  signature-wines: classification null (correct, not a misfill).
- Zero DOCG / DOCa / DOC / IGT / IGP / AVA token anywhere in the 26 data files.
- The 4 QA1 Échelle-des-Crus fixes HELD: pierre-paillard, bereche-et-fils,
  champagne-marguet, david-leclapart all == "Champagne AOC" in hidden-gems.json.
- neighborhoods.json carries "AOC Champagne (… Grand Cru, …)" strings on the
  12 sub-region/village ENTITIES. These are place entities, not cuvées/
  producers; the cru status is a factual attribute of the village in
  parentheses, matching QA1's place-vs-cuvée distinction. Not a defect.
- distilleries.json classification = spirit GIs (Ratafia Champenois IG, Marc
  de Champagne IG, Fine de Champagne) — correct for region spirits, not
  misplaced wine IGT. Matches QA1.

### Certification (QA2 fixes held)
- Cross-file scan (nested dietary structure included): 0 inconsistent
  organic_status / biodynamic_status across vineyards / dietary / hidden-gems.
- Larmandier-Bernier = demeter_certified everywhere (vineyards + dietary +
  hidden-gems). organic_status = ecocert consistent on all certified estates.
- Leclerc-Briant correctly remains biodynamic_practicing (NOT promoted to
  certified). Georges Laval = organic/ecocert only, no biodynamic claim.
  No practising→certified promotion anywhere.

### Scores
- 93 structured scores, range 88–97, mean ~92. **No score >= 98**, so C2
  numeric source-verification not triggered; no fabricated 99–100.
- 53 cuvées at editorial_score >= 4.7; every one backed by a real top score
  91–97 from Vinous / Decanter / Wine Spectator (each carries reviewer +
  points + vintage + year). Marquee spot-checks: Cristal (Decanter 97/2013),
  Krug Clos du Mesnil (Vinous 97/2008), Comtes (Vinous 96/2012), Salon
  (Vinous 96/2008), Dom Pérignon (Decanter 95/2013) — all real, in-range.

### QA2 taste re-anchors (3 spot-checked)
- deutz-brut-classic: official Deutz technical-sheet PDF FETCHED and its text
  confirms "white flowers", "fresh brioche" (toast/marzipan-led), "mousse of
  great finesse" — substantiates the recorded aroma/palate. VERIFIED on page.
- deutz-cuvee-william-deutz: Falstaff per-vintage review → 403 to bots
  (documented anti-bot, same as the rest of the catalog's citations);
  recorded descriptors (orchard fruit / toast / spice / white flowers)
  consistent with the cuvée. URL is a correct per-wine critic page.
- piper-heidsieck-rare: thefinestbubble per-cuvée Rare page → anti-bot;
  correct per-wine page, consistent descriptors.

### Itinerary end-to-end
- All 3 itineraries: every `days[*].venues[*]` slug resolves to an indexed
  entity (23 venue refs total, 0 unresolved). Reims grandes-marques weekend
  fully traced: champagne-taittinger, champagne-ruinart, le-bocal-reims,
  le-wine-bar-by-le-vintage, champagne-veuve-clicquot, champagne-perrier-jouet,
  c-comme-epernay — all indexed.

### Festival end-to-end
- Habits de Lumière: start_month "December", recurrence "second weekend of
  December", Épernay — matches the real event. source_url present.
  ship_safety check_festival_dates passed. Other 5 festivals carry valid
  source_urls; month info in start_month/recurrence_pattern (the `month`
  key is null by schema, dates live in start_month).

### Style + food-pairing scope
- wines.json: 93/93 cuvées tagged `sparkling-traditional` (single correct
  style; no still/dessert/fortified leakage). 0 derived-axis tag leakage
  (no price-/grape/world/sweetness/production tags emitted by researcher).
- 7 distinct TJ refs, ALL `france/paris/*` (Paris-scoped — no TJ Reims city).
  Re-confirmed france/paris/restaurants/clamato resolves to a real Paris 11th
  arr. seafood restaurant. food-pairing.json: 8 entries all map to the same
  Paris set. 0 off-city refs.

### Fabrication sample (30 entities across non-wines topics)
- Random 30-entity sample (nightlife, wine-schools, hidden-gems, vineyards,
  dietary, day-trips, hotels, retailers, neighborhoods, signature-wines,
  food-pairing, seasonal). All real, canonical producers/venues with
  appropriate source hosts (producer sites, tourism boards, Gault-Millau,
  UNESCO, SNCF). No fabricated names or credentials, no claim/source mismatch.
- open_status: 0 invalid (all in {open, seasonal, unknown, permanently_closed}).
- Cuvée→producer: 0 unresolved. signature→wines: 0 missing. 0 year-in-slug.

### Prose
- 0 em/en dashes across all files. 0 AI-tells (QA2's 2 "in the heart of"
  rewrites held; none remain).

## Non-defect notes
- "Bare-town" address_quoted remains on budget-wines cuvées, day-trips,
  itineraries, seasonal-wine, wine-history, and city-wide festivals. All are
  NON-venue entities (products, regions, calendar phenomena, historical eras,
  city-wide events) with `address: null` — a town/region quote is the correct
  value, same exemption class QA1 applied to neighborhoods. Not the vague-
  venue-address defect class.
- fetch-fail 30 in ship_safety = anti-bot/Cloudflare on thefinestbubble /
  Decanter / Falstaff per-wine pages. Non-defect (consistent across catalog).
- Region hub HTML not yet built (FAQ/JSON-LD/geocode gates are the
  orchestrator's post-QA steps 2-13). FAQ source data present in region.json
  (4 entries) and will render id="faq" + FAQPage at build.

OPUS-CLEAR france/champagne
