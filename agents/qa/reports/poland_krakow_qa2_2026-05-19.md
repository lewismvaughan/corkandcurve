# QA report - Kraków (judgment pass-2)

Date: 2026-05-19
Scope: 153 entities across 27 JSON files (post-QA1).

## Pass-1 carry-forward (verify_entities.py at QA2 start)

- HARD failures pre-QA2: 0 (QA1 left ship-safety baseline clean).
- WARNs pre-QA2: ~83, mostly `own_site_only` and `dead_cuisine_evidence_url` for the culture.pl 12-iconic-foods 404. Non-blocking; not the QA2 mandate.

## QA1 echo verification (the explicit ask)

### QA1 removals: clean.

Grep across all 27 files for QA1-removed slugs and names (pochlebstwo, afera-piekarnia, tasty-poland-class, krakow-cellar-vodka-tour, cukiernia-noworolski, wino-i-przyjaciele, bottiglieria-1881-wine-bar, winosfera-kazimierz, miodova-kosher): no surviving references in entity slugs or prose.

### QA1 fact rewrites: clean.

- "Bourdain" — one echo found and fixed in `signature-dishes.json` zapiekanka history ("Bourdain's 2007 Krakow filming of No Reservations" - Wikipedia No Reservations episode guide confirms NO Poland episode). REWRITTEN.
- "since 1798" (Stary Kleparz) — two echoes found and fixed in `region.json` SEO description and `neighborhoods.json` Kleparz vibe (markets.json was correct at mid-14th century). FIXED both.
- "Cukiernia Noworolski" / "Vanilla on Bracka" - one combined echo found in `signature-dishes.json` sernik history. REWRITTEN to "Vanilla on Brzozowa" and "Noworolski".
- "40 cold salads" (Chimera) - one echo found in `itineraries.json` day 3 prose. SOFTENED to "the cold salad counter".
- Lenin "table 9", filipa-18 "six tables fortnightly", chimera "since 1992 / two floors", Bourdain elsewhere, "15 zl terrace", "Krupnicza and Meiselsa", "Polakowski Sukiennice branch", "Plac Wolnica" for Soup Festival - all clean.

### QA1 address fixes: clean.

No surviving Świętej Anny 5 (Trezo old), Józefińska 15 (Krafta old), Grodzka 65 (Fiorentina old), Józefa 23 (Mojego Taty old), or Bracka 8 (Vanilla old).

### QA1 Belfast IYP fixes: significantly expanded.

QA1 found three IYP-Belfast cross-overs (trzy-rybki, szara-gesi fine-dining, copernicus). My broader audit of all 31 unique inyourpocket.com/krakow/* URLs in the dataset (via WebFetch on each) found 13 more wrong-city collisions and produced full fixes. The IYP `_NNNNNv` database ID silently resolves to non-Kraków pages for many entries. See defect group A below.

## Judgment defects found and fixed

### A. Cuisine / category mismatches + independent-directory cross-checks

**IYP wrong-city URLs (13 newly identified by WebFetch sweep of all 31 unique IYP IDs):**

| URL ID | Real venue | Action |
|---|---|---|
| `europejska_27991v` | Clements (Belfast) | cuisine_evidence_url replaced in `cafes.json` |
| `marchewka-z-groszkiem_28031v` | Northern Whig (Belfast) | cuisine_evidence_url replaced in `casual-dining.json` + `brunch.json` |
| `miod-i-wino_28030v` | Superior Keys (Belfast) | cuisine_evidence_url replaced in `restaurants.json` |
| `pierogi-u-vincenta_28013v` | Scalini (Belfast) | entity REMOVED (`street-food.json`) - venue fabricated |
| `pijalnia-wina_28017v` | Café India (Belfast) | entity REMOVED (`wine-bars.json`) - fabricated Floriańska 26 address |
| `ranny-ptaszek_137080v` | MAL'CA (Maribor, Slovenia) | cuisine_evidence_url replaced in `cafes.json` + `brunch.json` + `hidden-gems.json` |
| `smakolyki_137075v` | Swanky Bar (Zagreb, Croatia) | source/open/cuisine replaced with smakolyki.eu in `casual-dining.json` + `budget-eating.json` |
| `starka_27933v` | Ten Square (Belfast) | cuisine_evidence_url replaced in `restaurants.json` + `wine-bars.json` |
| `szara-ges_28069v` | Bridge House (Belfast) | cuisine_evidence_url replaced in `restaurants.json` (fine-dining was already fixed by QA1) |
| `vanilla_28003v` | Rajput (Belfast) | cuisine_evidence_url replaced in `bakeries.json` |
| `wesele_27923v` | Linen Hall Library (Belfast) | cuisine_evidence_url replaced in `restaurants.json` |
| `christmas-market_137081v` | Waldschwimmbad (Lucerne, Switzerland) | source/open/cuisine replaced with visitkrakow.com/krakow-christmas-markets/ in `festivals.json` + `markets.json` |
| `hummus-falafel-king_137060v` | Bianchi Café (Milan) | entity REMOVED from `street-food.json` + `late-night.json` - venue fabricated |

After verification, the remaining 18 IYP URLs in the dataset resolve to genuine Kraków venues (Mini-Bar-Endzior, Alchemia, Andrus-Maczanka, Camelot, Filipa-18, Hamsa, Karma, Morskie-Oko, Plac-Nowy, Plac-Targowy-Unitarg, Singer, Targ-Pietruszkowy, The-Blue-Truck, Vis-a-Vis, Wodka-Cafe-Bar, Zazie-Bistro, Cloth-Hall, Bunkier-Sztuki).

### A2. Specific-fact match against operator

- **`europejska` (cafes.json)**: "has poured coffee on the main square since 1962" - operator europejska.pl/en/main_page/ does not state any founding year, search engines (no Wikipedia article exists for it) cannot corroborate 1962. REWRITTEN: removed year, kept "inside the historic Krzysztofory Palace" (operator-confirmed).
- **`ciastkarnia-vanilla` (bakeries.json)**: "operating since 1984" - operator cukierniavanilla.pl shows two Kraków locations (Brzozowa 13, Na Szaniec 14) with no founding year. DuckDuckGo turned up a "2010" reference but that was for a Warsaw branch. REWRITTEN: drop the year, name both Kraków shops.
- **Vegab `vegab`, `vegab-late`, `vegab-kebab`, dietary.vegan `vegab` (4 entries)**: address "Starowiślna 4" - independent DDG search across visitkrakow, instagram, TripAdvisor, Google Maps all consistently show **Starowiślna 8** (1-block-off building-number hallucination). FIXED all 4 entries; removed "Two branches" / "Two locations" claim (operator has one Kraków location). 4 files touched: casual-dining.json, dietary.json, street-food.json, late-night.json.
- **`youmiko-sushi` (casual-dining.json + dietary.json)**: per operator youmiko.pl/en/contact, the venue **RELOCATED TO WARSAW** (Al. Jana Pawła II 45A/50A, 01-008 Warsaw) and now operates "delivery and personal pickup only" - no dine-in. The "Two seatings 18:30 and 21:00" itinerary claim is structurally broken (no dine-in in Warsaw, and they're not in Kraków at all). ENTITY REMOVED from both files. Day-1 vegetarian itinerary venue substituted (Veganic).
- **`veganic` (casual-dining.json + dietary.json + brunch.json)**: per operator veganic.restaurant, the venue **MOVED to Karmelicka 34** (Old Town/Piasek), not Dietla 19. The veganic.pl domain redirects to a health foundation (parked). FIXED address Dietla 19 → Karmelicka 34, neighborhood kazimierz → stare-miasto, prose "on Dietla" → "on Karmelicka", source_url veganic.pl → veganic.restaurant in all 3 files; itinerary day-2 vegetarian rewrote to remove the "65 zl Sunday brunch set" specific.
- **`pijalnia-wina-krakow` (wine-bars.json)**: "Pijalnia Wina on Floriańska 26" - DuckDuckGo finds **Pijalnia Win Francuskich** at Zamenhofa 6/1 (different name, different street) and **Pijalnia Wódki i Piwa** at Floriańska 34 (vodka/beer, not wine). No "Pijalnia Wina" exists at Floriańska 26 in Kraków. Entity REMOVED.
- **`smaczne-pierogi-window` / Pierogi u Vincenta (street-food.json)**: DDG turns up NO references to a "Pierogi u Vincenta" on Józefa 11 in Kraków. The only source was the Belfast-Scalini IYP URL. Entity REMOVED.
- **`kazimierz-falafel` / Hummus Falafel King (street-food.json + late-night.json)**: DDG turns up NO references to a "Hummus Falafel King" in Kraków. The only source was the Milan-Bianchi IYP URL. Both entries REMOVED.
- **`hamsa-hummus-kosher` (dietary.kosher)**: Tip explicitly says "Kosher-style, not under rabbinic certification". Same category-mismatch defect that QA1 used to remove `miodova-kosher`. REMOVED.

### B. Route / itinerary mismatches

- **`delicious-poland-jewish-tour` (food-tours.json)**: operator's product page lists 4 tours (Traditional Polish Food, Vodka and Culture, Craft Beer, Pierogi Cooking Class) - no Kazimierz Jewish-food tour. QA1 softened the tip; QA2 went further: renamed entity to `delicious-poland-traditional-tour`, replaced fabricated stops ("hummus, gefilte fish, cholent, bagel and the Plac Nowy zapiekanka rotunda"), generic meeting point, generic prose tied to the operator's actual listed offerings.

### C. Festival month / dates corrections

None this pass beyond QA1.

### D. Thin-category fabrications

- `dietary.halal`: 0 entries (unchanged from QA1).
- `dietary.kosher`: now 0 entries after Hamsa removal (was 1 - acceptable below-floor per QA contract).
- `cooking-classes`: 0 entries (unchanged from QA1; needs research backfill).

### E. Editorial-prose echoes

See QA1 echo verification above (Bourdain, since-1798, Vanilla-on-Bracka, 40-cold-salads).

Additional rewrites by QA2:

- `itineraries.json` vegetarian day-1: Youmiko → Veganic dinner + venues list updated.
- `itineraries.json` vegetarian day-2 lunch: Veganic-on-Dietla → Moment-on-Józefa (Sunday brunch fit; Veganic is no longer in Kazimierz after relocation).
- `itineraries.json` vegetarian summary: rewrote to remove Youmiko + Tektura (Tektura was already unverified, never an entity).
- `itineraries.json` jewish-quarter-deep-dive day-2 evening: "Dinner at Pod Norenami in Kazimierz" → "on Krupnicza for vegan pan-Asian, then walk back to Kazimierz" (Pod Norenami is on Krupnicza/Piasek, not Kazimierz - slug-vs-prose location drift defect).
- `region.json` dietary SEO description: "kosher Hamsa in Kazimierz" → reframed without false-kosher claim, also retitled the dietary tag "Vegan, Vegetarian and Gluten-Free" (Kosher and Halal both 0 after QA2).
- `region.json` markets SEO description: "since 1798" → "since the 14th century".

### F. Editorial voice / AI-tells

None observed beyond defects above.

## Defects total: 14 entities removed/edited + 13 URL replacements + 6 prose rewrites + 4 cross-file address fixes

**Removed (7 entities):**
- `youmiko-sushi` (casual-dining.json) - relocated to Warsaw, delivery only
- `youmiko-sushi` (dietary.json) - same
- `pijalnia-wina-krakow` (wine-bars.json) - fabricated address (Floriańska 26 has no wine bar by that name)
- `smaczne-pierogi-window` / Pierogi u Vincenta (street-food.json) - fabricated venue
- `kazimierz-falafel` / Hummus Falafel King (street-food.json) - fabricated venue
- `hummus-falafel-king-late` (late-night.json) - fabricated venue
- `hamsa-hummus-kosher` (dietary.kosher) - not rabbinic-certified, same logic as QA1's miodova-kosher removal

**Edited entities (key changes):**
- `veganic` (casual-dining + dietary + brunch) - address Dietla 19 → Karmelicka 34, source_url, neighborhood, prose
- `vegab` (4 files: casual-dining + dietary + street-food + late-night) - Starowiślna 4 → Starowiślna 8, removed "two branches" claim
- `europejska` (cafes) - removed "since 1962" unsourced claim
- `ciastkarnia-vanilla` (bakeries) - removed "since 1984" unsourced; added both Kraków locations
- `delicious-poland-jewish-tour` → `delicious-poland-traditional-tour` (food-tours) - operator real, jewish-tour route fabricated
- Vis-a-Vis Krakow note: already pre-fixed by QA1; no change needed

**URL fixes (Belfast/wrong-city replacements):** 13 entries across cafes, restaurants, bakeries, brunch, casual-dining, hidden-gems, festivals, markets, wine-bars, budget-eating.

**Prose rewrites:** 6 (signature-dishes zapiekanka + sernik histories, itineraries day-1/day-2/jewish day-2, region.json dietary + markets descriptions, neighborhoods.json Kleparz vibe).

## Below-floor topics after QA2

- `dietary.halal`: 0 entries (unchanged).
- `dietary.kosher`: 0 entries (was 1; Hamsa removed for non-certification).
- `cooking-classes`: 0 entries (unchanged).
- `coffee-roasters`: 4 entries (unchanged from QA1; pre-existing depth gap).
- `wine-bars`: 4 entries (was 5; Pijalnia Wina removed).

All below-floor and acceptable per QA contract; not fabricated to fill.

## Pipeline state at QA2 end

- `verify_entities.py`: 146 entities, 0 HARD, 76 WARN (mostly `own_site_only`).
- `check_internal_references.py`: 0 ERR, 0 WARN (all itinerary venue slugs and signature-dish where_to_eat names resolve).
- `validate_data.py --city krakow`: 1 ERR (cooking-classes empty - pre-existing research-stage gap), length-cap WARNs (pre-existing, validator territory).

## Verdict

VERDICT: NEEDS_FIXES

Rationale: 14 entities removed/edited (7 fabricated or relocated, 7 substantially rewritten) plus 13 URL fixes is well above the threshold that signals a research-stage regression. The Belfast/wrong-city IYP URL pattern is structural across the Polish fixup-agent batch (13 wrong-city URLs out of 31 unique IYP IDs is ~42% bad). Two major venue-relocation defects (Youmiko to Warsaw, Veganic to Karmelicka) survived QA1 because the operator's own pages were not opened. Three fully-fabricated venues (Pijalnia Wina at Floriańska 26, Pierogi u Vincenta, Hummus Falafel King) had all their verified-block URLs pointing at unrelated Belfast/Milan pages, demonstrating that the fixup-agent's URL-replacement pass shipped placeholders. This is a pattern, not a one-off; the Sonnet final-pass + verify_entities.py pipeline needs to gain an IYP-domain-content check and an operator-page-relocation check before the next Polish ship.

Kraków JSON is now structurally safe to ship (0 HARD, 0 internal-ref ERR), but the defect rate over both QA1 and QA2 (35+ and 14+ respectively) means a research-stage rebuild for this city is warranted if SEO publication priority changes.
