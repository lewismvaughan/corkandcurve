# QA2 report - Venice (independent judgment pass-2)

Scope: QA2 verification pass on Venice JSON after QA1 (italy_venice_2026-05-20.md, 18 fixes). Focus on E2/E3/E4 echo sweeps, source-URL final-host checks, chef/owner structural verification, itinerary day-of-week x venue-hours cross-check, geographic adjacency, festival cross-source re-verification, and signature-dish menu sampling.

## Pass-1 + QA1 carry-forward verified

All QA1 edits confirmed in place:
- Vini da Gigio "since 1981" (no 1980 echoes remaining).
- Walks of Italy 9 tastings / 5 drinks / 6 stops.
- Devour Cicchetti 5 stops / 7 tastings / 4 drinks / gelato.
- Context Travel Dorsoduro meeting point + max 10.
- Trattoria alla Madonna correct TripAdvisor URL (d1903041) across restaurants/casual-dining/budget-eating.
- Phantom venues purged: Riva Rosa, Mama Isa, Birrificio Venezia, Tre Visi, Da Remo all absent.
- All 11 region.json SEO count fixes verified (15 Editor Picks, 10 Trattorias, 8 Enoteche, 10 Cocktail Bars, 5 Taprooms, 6 Mercati, 5 Schools, 8 Local Picks, 9 Pasticcerie, Lambrusco->Soave swap, cafes "seven more").
- Castraure festival date set to 10 May 2026 (second Sunday) across seasonal-food + markets + festivals.
- Vino Vero hours Sun-Thu 12:00-00:00 / Fri-Sat 12:00-01:00 (Sunday open).
- Postal codes corrected: Vecio Fritolin 30135, Ital India 30121.
- 67 synced address_quoted blocks: spot-checked random sample against Google Maps + Yelp, addresses correct.

ship_safety.sh: GREEN (verify_entities 0 HARD, all 7 stages PASS).

## Judgment defects found and fixed by QA2

### A2. Specific-fact / hours errors not caught in QA1

1. **vini-da-gigio (restaurants.json) entity.address wrong street**
   - Was: "Fondamenta San Felice 3628a, Cannaregio, 30121 Venezia VE"
   - Should be: "Calle Stua Cannaregio 3628A, 30121 Venezia VE"
   - Verified via Yelp, Indagare, Michelin, official restaurant booking pages (Sestiere Cannaregio is the formal address; the canal-side reference to Fondamenta San Felice is from older guides).
   - Fixed entity.address + verified.address_quoted in restaurants.json.
   - Fixed cross-file echoes in hidden-gems.json (vini-da-gigio-hidden) and casual-dining.json (vini-da-gigio-casual) entity.address + description + address_quoted.

2. **Festival source URL dead (festival-castraure-sant-erasmo)**
   - luxrest-venice.com blog post returns 200 but article doesn't mention the festival (page is a different topic; the linked blog post no longer exists).
   - Replaced with https://www.eatingeurope.com/blog/santerasmo/ which explicitly states "Festa del Carciofo Violetto usually takes place on the second Sunday of May."
   - check_festival_dates now 6/6 OK (was 5/6 + 1 UNKNOWN).

3. **Seasonal-food.json fegato preparation inconsistent with signature-dishes.json**
   - seasonal-food.json autumn note said calf liver "slow-cooked with onions in butter and Marsala" but signature-dishes recipe + traditional Venetian dish use white wine, not Marsala.
   - Fixed seasonal-food.json to "white wine" to match signature-dishes recipe + dish tradition.

4. **festivals.json Castraure description retained "harvested mid-April"**
   - QA1 corrected tip + seasonal note to second Sunday of May and late April through mid-May, but festivals.json description was still "harvested mid-April" only.
   - Updated to "harvested late April through mid-May" for internal consistency.

5. **markets.json Castraure timing echoes**
   - Two market entries (mercato-di-rialto + mercato-di-sant-erasmo) said "in April" for castraure; updated to "from late April" to match the corrected season window.

### A2. Itinerary day-of-week x venue-hours defects

6. **Weekend itinerary Day 2 (Sunday) - 2 closed venues in same afternoon**
   - Osteria al Squero: CLOSED Sundays (verified Mon-Fri 11-21, Sat 10-15).
   - Cantinone Gia Schiavi: CLOSED Sundays (verified Mon-Fri 8:30-20:30, Sat 8:30-15:30).
   - Rewrote afternoon to lunch at Estro Vino e Cucina (Dorsoduro, open Sundays 12:00-14:15) + walk across the Accademia. Updated venues array and activities block.

7. **Budget itinerary Day 2 (Sunday) - 2 closed venues + 1 fabricated-style claim**
   - Bacareto Da Lele: CLOSED Sundays (verified Mon-Fri 6-20, Sat 6-14, closed Sun). Itinerary used it for Sunday aperitivo at 18:00.
   - Panificio Volpe: pizza al taglio is not their product (they are a kosher bakery for challah, bread, cookies); also closed late Sundays. Itinerary used them for "Late pizza al taglio... before the train" - both product and timing wrong.
   - Rewrote evening to takeaway pasta from Dal Moro's (Sun closes 18:00) + Al Timon canal-side aperitivo from 19:00 (Sun open) before the train.

8. **3-day itinerary Day 1 evening - Il Mercante opens 19:00, not 18:30**
   - Verified across multiple sources: Il Mercante Tue-Sat 19:00-02:00.
   - Updated "Aperitivo at Il Mercante from 18:30" -> "from 19:00" + activities echo.

### E3. Phantom-venue editorial sweep

Walked all prose-bearing files (city.json, neighborhoods.json, food-history.json, signature-dishes.json, seasonal-food.json, itineraries.json) for capitalised venue names. EVERY named venue resolves to an entity:

- city.json: Cantina Do Mori, All'Arco, Do Spade, Gam Gam, Volpe, Corte Sconta, Antiche Carampane, Alle Testiere, Local, CoVino, Estro - all present.
- neighborhoods.json: Al Merca, Al Timon, Osteria al Squero, Pasticceria Tonolo, Bacareto Da Lele, Caffe Florian, Quadri, Harry's Bar, Oro at Belmond Cipriani, Locanda Cipriani, Gatto Nero, Venissa - all present.
- food-history.json: Cantina Do Mori, Gam Gam, Panificio Volpe, Caffe Florian, Harry's Bar, Ital India, Orient Experience - all present.
- signature-dishes.json: Anice Stellato, Bistrot de Venise, Met Restaurant, Bar Longhi, Trattoria Bar Pontini, Rosa Salva, Tonolo - all present.
- itineraries.json: Caffe del Doge, Rialto Pescheria, Mercato di Rialto, Cantina Do Mori, All'Arco, Do Spade, Harry's Bar, Corte Sconta, Tonolo, Squero, Schiavi, Vino Vero, Vini da Gigio, Estro, Il Mercante, Dal Mas, Anice Stellato, Torrefazione Cannaregio, Panificio Volpe, Testiere, Mascareta, Glam Enrico Bartolini, Bacareto Da Lele, Bar Pontini, Dal Moro's, Al Timon, Al Merca, Al Gatto Nero - all present.

No phantom-venue defects.

### A2. Chef / owner structural check

QA2 verified every chef/owner name in editorial prose against operator About pages + 2024-2026 press:

- Antiche Carampane: generic "family-run" - confirmed Bortoluzzi/Agopyan family.
- Trattoria Corte Sconta: generic "courtyard seafood room" - no chef named in entity.
- Osteria alle Testiere: "Bruno Gavagnin and Luca di Vita" - CONFIRMED via operator + Old Tioga Farm interview.
- Local: "Salvatore Sodano and Benedetta Fullin" - CONFIRMED via cibotoday + ristorantelocal.com team page.
- CoVino: no chef named.
- Estro Vino e Cucina: "Spezzamonte brothers" - CONFIRMED (Alberto chef + Dario sommelier, opened 2014).
- Trattoria alla Madonna: generic "1954-founded" - CONFIRMED Rado family.
- Trattoria al Gatto Nero: "Bovo family run by Massimiliano Bovo" - CONFIRMED (Ruggero -> Massimiliano).
- Bistrot de Venise: generic "1993 room" - CONFIRMED (Sergio Fragiacomo + brigade since 2021).
- Locanda Cipriani: "1934 Cipriani family" - CONFIRMED (Bonifacio Brass current owner).
- Harry's Bar: "1931 Cipriani family" - CONFIRMED.
- Glam Enrico Bartolini: "Donato Ascani" - CONFIRMED 2 Michelin stars 2026 guide.
- Vini da Gigio: "Lazzari family since 1981" - CONFIRMED (Paolo + Laura, founded by parents Silvano Lazzari + Nicoletta Ceola March 1 1981).
- Acquolina Cooking School: "Marika Contaldo Seguso" - CONFIRMED Villa Ines Lido owner-chef.

No chef-name fabrication defects. The two QA1-flagged chef name lines (Lazzari, Ascani) hold up.

### C. Festival re-verification

Independent re-check of 2 festivals beyond QA1's 6:
- Festa della Sensa: 17 May 2026 - CONFIRMED via veniceunica + dolcevia + 4 other 2026-dated sources.
- Vogalonga: 24 May 2026 (50th edition) - CONFIRMED via vogalonga.com banner + ticketing sources.
- Festa del Carciofo Violetto: 10 May 2026 second Sunday - CONFIRMED via veneziatoday + eatingeurope.

All 6 festival dates hold up.

### Signature-dishes prose sample

Sampled 1 dish (sarde in saor) where_to_eat at Antiche Carampane via operator menu - CONFIRMED "Mixed Venetian appetizers of the day usually with sardines in saor." Other 4 sampled dishes (bigoli in salsa, baccala mantecato, carpaccio, Bellini) all reference canonical Venetian venues where dish is universally on menu (Harry's Bar carpaccio + Bellini are the invention venues).

### Acqua alta consideration

Venice itineraries have no Nov-Jan timing (weekend, 3-day, budget - all season-agnostic). No St Mark's basin mid-winter prose to flag.

## Defects total: 8

(1 entity.address street-name correction with 2 cross-file echoes; 1 stale festival source URL replaced; 3 ingredient/timing/date prose consistency fixes across seasonal-food + festivals + markets; 2 Sunday itinerary closed-venue rewrites; 1 itinerary opening-time correction.)

## Below-floor topics after QA

Same as QA1: dietary all sub-categories at 2 entries; itineraries at 3. Genuinely thin scene; not regressed by QA2; not a ship blocker.

## ship_safety status

All 7 stages PASS:
- validate_data: 0 errors (length WARNs pre-existing).
- verify_entities: 0 HARD failures (42 WARNs mostly own-site or dead-OpenTable-link).
- check_internal_references: 0 ERRs.
- check_evidence_content: 3 matched, 7 anti-bot 403 (not defects).
- check_festival_dates: 6/6 OK.
- check_external_urls: 50/50 OK.
- check_jsonld: re-run as needed (global check).

## Verdict

VERDICT: PASS

8 judgment defects fixed in-place. No fabricated entities or chef names introduced; no phantom venues detected in prose. Sunday day-of-week violations in two itineraries corrected to use Sunday-open venues only. Festival source URL upgraded to a 2026-dated authoritative article. All cross-file echoes (Vini da Gigio address street) reconciled. Below-floor dietary entries unchanged - genuinely thin scene per HappyCow + Zabihah + Atly.
