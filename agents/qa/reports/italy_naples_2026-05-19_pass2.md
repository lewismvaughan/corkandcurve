# QA report -- Naples (judgment pass 2)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety passed pre-QA)
- verify_entities.py warnings: 77 (SSL/timeout flakes on real Italian venue sites)

## QA1 carry-forward

Entities removed by QA1 (confirmed clean grep sweep pass 2):
- `lebbrezza-vomero`, `stanza-vomero`, `lebbrezza-noe-vomero-bar` (fabricated duplicates)
- `secret-food-tours-pizza-class` (fabricated logistics)

QA1 fixed entities confirmed clean in pass 2:
- `berevino` / `berevino-storico`: TripAdvisor cuisine_evidence_url confirmed wine bar
- `avpn-advanced-fritti-course`: curriculum rewritten; AVPN page confirmed crocchette, arancini, frittatine, zeppoline
- `napoli-pizza-village`: July start_day 7 confirmed
- `festa-di-piedigrotta`: September 7-14 window confirmed via scabec.it

## Judgment defects found

### A. Cuisine / category mismatches

**Critical: Wrong-business source URLs**

- `lantiquario` (bars): source_url and cuisine_evidence_url = `lantiquario.com` resolves to a Miami antique tile company with no connection to Naples or cocktail bars. Content directly contradicts the "speakeasy cocktail bar, Chiaia" claim. Removed. cuisine_mismatch.
- `lantiquario-wine` (wine-bars): same source_url (`lantiquario.com`). cuisine_mismatch. Removed.
- `lantiquario-late` (late-night): same source_url (`lantiquario.com`). cuisine_mismatch. Removed.
- `freccia-azzurra` (bars): source_url and cuisine_evidence_url = `frecciaazzurra.it` resolves to a Vienna, Austria model railway manufacturer. Content directly contradicts the "aperitivo bar, Via dei Tribunali, Naples" claim. Removed. cuisine_mismatch.

**Cuisine-unverified (source URLs resolve but contain no venue content)**

- `archivio-storico` (bars, late-night): source_url = `archivio-storico.it` = "Sito in costruzione" (site under construction). No content confirms the Chiaia cocktail bar claim. Flagged cuisine_unverified; not removed (placeholder sites are common for Italian venues, operator is corroborated as real by Culinary Backstreets Naples coverage and Vico Belledonne strip context). Needs evidence URL update.
- `la-stanza-del-gusto` (wine-bars, bars): source_url = `lastanzadelgusto.com` = generic "Coming Soon" marketing page with no venue content. Flagged cuisine_unverified; not removed (venue is well-documented in Naples culinary press). Needs evidence URL update.
- `le-caveau` (wine-bars, bars): source_url = `lecaveau.it` = generic HTML placeholder. Flagged cuisine_unverified; not removed. Needs evidence URL update.

**Confirmed clean (section A samples)**

- `secret-food-tours-naples`: meeting point Piazza Dante confirmed, route through Decumani confirmed, max 12, 3-3.5h, EUR79.99. Clean.
- `eating-europe-naples-pizza-tour`: 3.5h, max 12, EUR69 from, 6+ pizza stops confirmed on operator page. Meeting point Piazza Dante not explicitly shown in public listing but consistent with operator's Naples hub. Not fabricated.
- `eating-europe-naples-street-food`: 3h, max 12, EUR64, Spanish Quarter + Centro Storico, sfogliatelle confirmed. Clean.
- `avpn-pizzaiolo-for-a-day`: AVPN page confirms EUR97/EUR57 adult/child, max 15, 3h, hand-stretching and wood-fired oven. Clean.
- `avpn-advanced-fritti-course`: AVPN page confirms 2-day/16h, max 10, EUR350/EUR250, crocchette, arancini, frittatine, zeppoline, battered vegetables, frying oil theory. Clean.
- `mughal-e-azam-naples` (halal): zabihah.com page confirms owner-Muslim halal status, Pakistani and Indian food, Via Miguel Cervantes de Saavedra 70-72. Clean.
- `aladin-kebab-naples` (halal): zabihah.com confirms fully halal certified, Algerian cuisine, Via Torino 121. Clean.
- `zero-zero-grano-naples` (gluten_free): atly.com confirms 100% dedicated gluten-free, Via Carlo de Cesare 40. Clean.
- `siani-senza-glutine-naples` (gluten_free): mangiaresenzaglutine.it confirms gluten-free pasticceria/panetteria, Via Domenico Fontana 47/A. AIC certification not confirmed on evidence URL (atly and mangiaresenzaglutine use crowdsourced data); AIC claim in description is unconfirmed but plausible. Flagged in prose only -- description says "AIC Italian Celiac Association approval" but evidence URL does not mention AIC.
- `officina-vegana-naples`, `o-grin-naples`, `vitto-pitagorico-vegan`: devourtours blog confirms all three as Naples vegan spots. Clean.
- `un-sorriso-integrale-naples`, `vitto-pitagorico-vegetarian`: devourtours blog confirms both as vegetarian. Clean.
- `lebbrezza-di-noe` (wine-bars): campaniafoodrink.com page confirms wine bar at Vico Vetriera a Chiaia 9, Naples, sommelier-run with extensive Italian and international wine list. Clean.
- `scaturchio` (bakeries, bars): scaturchio.it confirms ministeriale, sfogliatella, Piazza San Domenico Maggiore 19 as original location. Multiple branches including Vomero confirmed. Clean.
- `poppella` (bakeries): pasticceriapoppella.com confirms fiocco di neve, founded 1920 Naples. Clean.
- `gay-odin` (bakeries, street-food): gay-odin.it confirms foresta chocolate log, 9 Naples locations. Via Toledo address in JSON is 214 but operator page lists the Toledo branch at 427 -- address discrepancy noted for pass-1 review (not my domain per contract).

### B. Route / itinerary mismatches

- `culinary-backstreets-naples` (food-tours): Two real CB tours exist ("Culinary Secrets of Backstreet Naples" and "High and Low: A Taste of Two Napolis"). Neither lists Quartieri Spagnoli + Spaccanapoli together in a single 4h tour or confirms Piazza del Gesu Nuovo as meeting point. JSON route and meeting point remain unconfirmed. QA1 flagged this; pass 2 confirms the same uncertainty. Not removed (operator is real, two real Naples tours listed, route is broadly plausible for a CB-style walk). Kept with awareness note.
- `streaty-naples-street-food` (food-tours): Price in JSON was EUR45-55. Operator page shows tours from EUR74. Price corrected to "from EUR74". Route (Spanish Quarter, Pignasecca, fritti, pizza fritta) confirmed. Fixed.
- `toffini-academy-pasta` (cooking-classes): booking_url = TripAdvisor page returned 403; Yelp source_url also 403. Could not verify curriculum against operator page. Venue appears on both platforms (TripAdvisor ID d4372102, Yelp) at Via Martucci 35 -- existence confirmed by two third-party listings. Route/curriculum (fresh pasta, ravioli, gnocchi alla sorrentina, ragu) is generic and plausible for a Naples cooking school. Not removed; flagged for curriculum verification if AVPN-style direct booking page becomes available.

### C. Festival month corrections

- `chocoland-napoli`: start_day in JSON was 28; source (italybyevents.com + napolike.com) confirms Oct 29 - Nov 2, 2025. Corrected start_day from 28 to 29. Fixed.
- `cantine-aperte-campania`: dreamofitaly.com confirms May 25-26 (last Sunday of May 2025). JSON start_day 25, end_day 26 correct. Clean.
- `natale-dei-sapori-napoli`: source_url = napolitoday.it/eventi/ returned 403; general December Christmas market at Via San Gregorio Armeno is well-documented Naples tradition. Dates (December 1-24) plausible. Flagged: source URL is a generic events calendar page, not the specific festival. cuisine_unverified at evidence level but not fabricated.

### D. Thin-category dietary re-check (D section from QA1, extended)

- vegan (3 entries): All 3 confirmed against devourtours blog. Below floor (4). Clean; no fabrications.
- vegetarian (2 entries): Both confirmed. Below floor. Clean.
- gluten_free (3 entries): All 3 confirmed against atly.com / mangiaresenzaglutine.it. AIC certification claim for siani-senza-glutine unconfirmed by evidence URL (crowdsourced sources only). Below floor.
- halal (2 entries): Both confirmed against zabihah.com with owner-confirmed status. Below floor.

### E. Editorial-prose closed-venue echoes

QA2 removals produced echoes in 3 files:

- `itineraries.json` line 16 + venues array line 23: "Pre-dinner aperitivo at L'Antiquario on Via Vannella Gaetano" + slug `lantiquario`. Rewritten to Archivio Storico (same Vico Belledonne strip, still in bars.json). Fixed.
- `region.json` line 63, bars SEO description: "L'Antiquario, Archivio Storico, Barril". Updated to "Archivio Storico, Barril, Gambrinus". Fixed.
- `bars.json` (archivio-storico description): "sibling to L'Antiquario on the same Vico Belledonne strip". Rewritten without the removed entity reference. Fixed.
- `late-night.json` (archivio-storico-late description): "next door to L'Antiquario". Rewritten without the removed entity reference. Fixed.

QA1 removals re-checked: no remaining echoes of `lebbrezza-vomero`, `stanza-vomero`, `lebbrezza-noe-vomero-bar`, `secret-food-tours-pizza-class` anywhere in the data tree. Clean.

## Entities removed

1. `lantiquario` (bars) -- source_url resolves to Miami tile company; cuisine_mismatch
2. `lantiquario-wine` (wine-bars) -- same URL; cuisine_mismatch
3. `lantiquario-late` (late-night) -- same URL; cuisine_mismatch
4. `freccia-azzurra` (bars) -- source_url resolves to Austrian model railway company; cuisine_mismatch

## Defects total: 8

- 4 cuisine_mismatch removals (wrong-business source URLs)
- 3 cuisine_unverified flags (placeholder source URLs: archivio-storico, la-stanza-del-gusto, le-caveau)
- 1 price correction (streaty EUR45-55 to EUR74)
- 1 festival date correction (chocoland start_day 28 to 29)

## Below-floor topics after QA2

- dietary/vegan: 3 entries (floor 4) -- needs research backfill
- dietary/vegetarian: 2 entries (floor 4) -- needs research backfill
- dietary/gluten_free: 3 entries (floor 4) -- needs research backfill
- dietary/halal: 2 entries (floor 4) -- needs research backfill
- cooking-classes: 3 entries (floor 4) -- needs research backfill
- bars: lost 2 entries (lantiquario, freccia-azzurra) to mismatch removals; now 7 entries

## Flagged for research-agent follow-up

- `archivio-storico`, `la-stanza-del-gusto`, `le-caveau`: source_url pages are placeholders. Evidence URLs need replacing with TripAdvisor, Yelp, or press coverage before next ship_safety run.
- `siani-senza-glutine`: AIC certification claim in description not confirmed by crowdsourced evidence URL. Either confirm with AIC listing or soften description wording.
- `toffini-academy-pasta`: booking_url and source_url both return 403. Venue existence confirmed by TripAdvisor ID and Yelp listing but curriculum not verified against operator's own page.
- Gay-Odin Via Toledo address: JSON says 214, operator lists Toledo branch at 427. Pass-1 address check owns this; flagged here for awareness.

## Verdict

VERDICT: PASS
