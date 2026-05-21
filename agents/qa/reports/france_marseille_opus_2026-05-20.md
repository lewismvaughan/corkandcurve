# Opus final QA report - Marseille

Third and final reader after QA1 (K=18 fixes) and QA2 (K=13 fixes). Per the
"Opus should find nothing" rule, every defect below is an upstream regression
that QA1 or QA2 should have caught. Tightening notes at the end.

## Pass-1 carry-forward

Pre-Opus `verify_entities.py`: 0 HARD failures, WARNs are acceptable
(own_site_only on dietary directory sources, anti-bot 403s, dead third-party
URLs that are non-blocking).

## Judgment defects found in Opus

### A. Address fabrication / cross-entry contradiction

- **bakeries.json + brunch.json + cafes.json `oh-faon`: WRONG ADDRESS shipped
  in 3 of the 4 Oh Faon entries.** All three claimed "92 Cours Lieutaud,
  13006 Marseille" but Mappy, the SIRET-registered firmania listing, Pages
  Jaunes, marseille-tourisme, lucky-miam, avis-de-gourmets, love-spots and
  the Société company registry all place Oh Faon at **6 Rue Edmond Rostand**
  (patisserie) and **2 Rue Edmond Rostand** (biscuiterie) — two storefronts
  on the same street, one doorway apart. The Cours Lieutaud address does not
  exist for this venue anywhere. Meanwhile dietary.json's two Oh Faon
  entries had **6 Rue Edmond Rostand** (correct).

  Three-file cross-entry contradiction missed by QA1+QA2's address-quality
  sweep. Fixed all three bakeries/brunch/cafes entries to 6 Rue Edmond
  Rostand (the patisserie+cafe storefront, which is what those entries
  describe — viennoiserie, brunch counter, cafe corner — not the biscuiterie
  at #2). Updated address_quoted, descriptions, and the "Cours Lieutaud"
  prose echoes in each. dietary entries already correct, no change.

- **breweries.json `la-rade-torpille`: PHANTOM BREWERY.** Entity shipped as
  an "Independent Marseille craft brewery" at "33 Rue Sainte-Cecile, 13005
  Marseille" with `taproom_hours` and `editorial_score`. None of this exists.
  "La Torpille" is a SESSION IPA BEER produced by **Bière de la Rade**, a
  micro-brewery in **Toulon** (300 Rue Amiral Nomy, 83000 Toulon) — 65km
  from Marseille. The "33 Rue Sainte-Cecile, 13005" address is a hair salon
  and carpentry workshop per Société.com's business registry. No brewery at
  that address. The beer is served on guest tap at La Brasserie Communale
  in Marseille, which is the legitimate way to drink it locally; that's why
  it appears in our `la-brasserie-communale` tip ("Local taps include La
  Rade Torpille and Sulauze"). Removed the fabricated entity. **breweries
  topic now at 4 (below floor of 5)**; needs research backfill of 1+ real
  Marseille brewery (e.g. Beer'Ocratie at 173 Boulevard Chave 13005,
  Brasserie de Mars).

### A2. Hours fabrication (operator-contradicted)

- **bars.json + late-night.json `le-melo`: WRONG OPENING DAYS.** Both
  entries claimed "Tue-Sat" hours (late-night `closes: "Tue-Sat until 02:00"`
  + bars description "DJ sets through the week"). Operator melocafe.fr is
  explicit: **Thursday-Saturday 19h-2h**, Monday-Wednesday and Sunday by
  reservation only. Two-day overstatement. Fixed `closes`, description, and
  `tip` in both files to match operator.

- **street-food.json `chez-yassine-street`: WRONG DAILY CLAIM.** Entry
  shipped as "Daily 11:00-22:00, no reservations" but operator
  chezyassine.com/contact and Yelp/Yelp-Yelp/tourist office all confirm
  **Tue-Sun 11:30-21:30, closed Monday**. Daily-vs-Tue-Sun = wrong closed
  day. Fixed.

- **late-night.json `chez-yassine-late`: 30-minute closing-time
  overstatement.** Shipped as "Tue-Sun until 22:00" but operator says
  closes 21:30 (some pages say 21:00). Fixed to "Tue-Sun until 21:30" and
  description prose.

- **bakeries.json `patisserie-saint-victor`: WRONG CLOSED DAY.** Shipped as
  "Tue-Sun 7:00-19:00, closed Monday". Mappy and tarpin-bien (two
  independent directories) both show **Daily 6:30-21:00, no closed days**.
  Wrong closed day AND wrong hours window. Fixed to "Daily 6:30-21:00".

### A2. Numerical fabrication

- **fine-dining.json `am-par-alexandre-mazzia` must_order + itineraries.json
  day 3 evening: PLATE-COUNT OVERSTATEMENT.** Shipped as "between 60 and 80
  small plates" (fine-dining) and "60-plus small plates" (itineraries).
  Documented count from a published meal (Identitàgolose Carlo Mangio
  review) is **44 plates**. Tightened the fine-dining `must_order` to
  "around 40 to 50 small plates served in successive waves over a long
  evening" and the itineraries prose to "dozens of small plates served in
  waves" (more durable than a specific number).

### Address Nominatim cleanup (per item #12 of food-research PROMPT)

- **cooking-classes.json `provence-gourmet`: prose prefix.** Shipped as
  "Marseille Tourist Office, 11 La Canebiere, 13001 Marseille" — the
  building-name prefix would force the geocoder to fall back to
  strip-venue-prefix. Stripped to "11 La Canebiere, 13001 Marseille" and
  moved the Tourist Office context to `tip`.

- **cooking-classes.json `chef-clement-marseille`: non-geocodable prose.**
  Shipped as "At your home in Marseille and Provence" — a sentence, not an
  address. Nominatim can't pin it. Chef Clement's operating model is
  at-home only, operator HQ in Aix-en-Provence (outside city scope), so per
  item #12's mobile-venue rule, set to the city-area postcode "13006
  Marseille" so the entry pins to the city centre on the map. At-home
  format clarified in `tip`.

- **cooking-classes.json `ateliers-de-valentine`: prose prefix.** Shipped
  as "Chateau Gombert, Marseille 13eme arrondissement, 13013" — three
  problems (district name prefix, the word "arrondissement", missing
  street). Real address per mappy.com and lesateliersdevalentine.com
  contact page is **220 Chemin de Chateau Gombert, 13013 Marseille**.
  Fixed both `address` and `address_quoted`.

- **festivals.json `foire-aux-santons`: parenthetical address shape.** QA2
  left the address as "Vieux-Port (Quai du Port), 13002 Marseille". The
  parenthetical breaks Nominatim parsing. Rewrote to "Quai du Port,
  Vieux-Port, 13002 Marseille" (comma form preserves both the street and
  the well-known POI tokens, so the geocoder finds the quay and the
  address_quoted "Vieux-Port" still token-set matches).

- **festivals.json `marseille-provence-gastronomie`: non-geocodable
  vague.** Shipped as "Various venues, Marseille" — the documented anti-
  pattern from item #12. Festival is an umbrella programme across the
  city with no fixed venue. Set to "13001 Marseille" (centre-ville
  postcode centroid for map pin); address_quoted "Marseille" still token-
  set matches.

- **fine-dining.json `le-petit-nice-passedat`: address too long for fuzzy
  match.** Shipped as "17 rue des Braves, Anse de Maldorme, Corniche John
  Fitzgerald Kennedy, 13007 Marseille" — five comma-separated tokens that
  the postal-form normalizer chokes on. Trimmed to canonical "17 rue des
  Braves, 13007 Marseille" (verified via Yelp + Tourism PACA + Booking).
  Updated address_quoted to "17 rue des Braves, Marseille" to maintain
  token-subset match.

### Itinerary defects

- **itineraries.json `marseille-noailles-maghreb` Day 2 morning title +
  prose: VENUE-HOURS CONTRADICTION + WRONG-CUISINE TITLE.** Title was
  "Saturday: brik counter, Lebanese lunch, Carry Nation late" — but La
  Kahena is Tunisian, not Lebanese (QA1 fixed the same defect in source
  pointer, missed this title prose). Morning said "Breakfast brik at Chez
  Yassine" — but Yassine opens at 11:30, not breakfast time. Fixed title
  to "Saturday: brik counter, couscous lunch, Carry Nation late" and
  morning to "Late-morning brik at Chez Yassine on Rue d'Aubagne from
  11:30 opening".

- **itineraries.json `marseille-weekend-classics` Day 1 morning: SLUG-VS-
  PROSE LOCATION DRIFT.** Prose said "Walk back along Rue Sainte and have
  an espresso at La Tisserie if the doors are open" — but La Tisserie is
  on Rue d'Endoume (the entity address is `142 Rue d'Endoume, 13007`), not
  Rue Sainte. The two streets meet near Saint-Victor but don't overlap.
  Rewrote to "Walk back along Rue Sainte and continue uphill onto Rue
  d'Endoume for an espresso at La Tisserie if the doors are open" — the
  walking path is now correct.

- **itineraries.json `marseille-weekend-classics` Day 1 afternoon:
  GEOGRAPHIC ADJACENCY FABRICATION.** Prose said "Walk it off across the
  harbour to La Caravelle" — but Chez Madie (138 Quai du Port) and La
  Caravelle (34 Quai du Port) are both on the SAME quay (north side of the
  Vieux Port), ~600m walk along the same Quai du Port. Crossing the
  harbour would go to Quai de Rive Neuve / Quai des Belges (south side).
  Rewrote to "Walk it off along the quay to La Caravelle for an espresso
  on the balcony above the harbour".

### E. Editorial-prose echoes

- **food-history.json `immigrant_influences[].community="Corsican"`:
  PHANTOM VENUE PAIR.** Shipped as "the U Borgu and A Casetta rooms the
  explicit Corsican kitchens". **U Borgu** is a restaurant in Porto-
  Vecchio (Corsica), 600km away — NOT a Marseille kitchen. **A Casetta**
  is real and in Marseille at 218 Quai du Port, 13002, but is not a
  verified entity in our data. Per E3 phantom-named-venue rule, rewrote
  to drop both named references and reframe generically ("the island just
  an overnight ferry from the Vieux Port"). QA1/QA2 had walked
  immigrant_influences and missed this entry entirely.

## Other findings (no action)

- **Brasserie de la Plaine + Biere de la Plaine Shop**: same operator,
  same physical address (16 Rue Saint-Pierre, 13006). The brewery
  production is actually at 43 Chemin vicinal de la Millière, 13011 (not
  open to public). The two entries effectively duplicate the retail
  taproom address. With breweries already at 4 after the La Rade Torpille
  removal, removing one more drops to 3 (well below floor). Left both.
  Worth a single-entity collapse in a future research pass.

- **markets.json `marche-des-capucins`**: shipped as "Rue du Marche des
  Capucins, 13001 Marseille" — Nominatim resolves the street centroid
  fine, but the canonical street-number address per tripadvisor +
  whereistheaddress is "5 Rue du Marche des Capucins". Adding the number
  is a polish, not a defect. Left.

- **Address quality across remaining 130 entities**: scanned all entity
  addresses for prose, floors, building modifiers, and arrondissement
  prefixes. After fixes above, all addresses are canonical Nominatim form.

- **Source-URL final-host check, sampled 10**: melocafe.fr → Le Melo
  (confirmed), lebouchonprovencal.com → Le Bouchon Provencal (confirmed),
  epicerielideal.com → Epicerie L'Ideal grocery (real venue, also runs
  restaurant), lefooding.com Pain Salvator (confirmed), pagesjaunes
  Patisserie Saint Victor (confirmed). No host-mismatch defects (no
  domain-sale signals).

- **Chef / press credential structural checks**: AM par Mazzia 3-star
  (confirmed via Michelin 2026 + operator); Petit Nice 3-star Passedat
  family since 1917 (confirmed via passedat.fr); Une Table au Sud
  Ludovic Turac 1-star (confirmed regained 2025/26); Auffo 1-star March
  2026 Coline Faulquier (confirmed); Dame Jeanne Samy Leroy + Ohannes
  Kachichian Feb 2025 (confirmed via cotemagazine + Grand Pastis); Sepia
  Paul Langlere on Puget Hill (confirmed); Chez Aldo 1964 (confirmed);
  Pain Salvator Nicole + Etienne Weber (confirmed via lefooding); Le
  Femina 1921 Algerian Berber 4-generation family (confirmed).

- **Sepia menu claim "smoked mackerel, bottarga and shrimp broth"**:
  confirmed via Gault Millau Sepia page ("smoked mackerel, anchovies,
  bottarga or shrimp broth"). Accurate.

- **Le Petit Nice signature dishes "Ma Bouille Abaisse" and "Loup Lucie
  Passedat"**: both confirmed real on multiple Passedat reviews + 50 Best
  + operator site (Loup Lucie is the tribute-to-grandmother sea bass,
  Bouille Abaisse is Passedat's three-service bouillabaisse).

## Defects total

- A address fabrication: 2 entities (3 file edits: Oh Faon 92 Cours
  Lieutaud propagation across bakeries+brunch+cafes; La Rade Torpille
  phantom brewery removal)
- A2 wrong hours: 4 (Le Melo Tue-Sat→Thu-Sat, Chez Yassine street-food
  Daily→Tue-Sun, Chez Yassine late-night 22:00→21:30, Patisserie Saint
  Victor closed-Monday→daily 6:30-21)
- A2 numerical: 1 (AM Mazzia 60-80 plates → 40-50; itinerary echo of
  same)
- Nominatim cleanup: 5 (provence-gourmet, chef-clement, ateliers-de-
  valentine, foire-aux-santons, marseille-provence-gastronomie, le-petit-
  nice)
- Itinerary: 3 (noailles-maghreb Day 2 title+morning, weekend-classics
  Day 1 morning Tisserie street drift, weekend-classics Day 1 afternoon
  Caravelle "across the harbour" adjacency)
- E3 phantom-venue: 1 (food-history Corsican community U Borgu + A
  Casetta)

**K = 16 net new defects**

This is a non-trivial Opus surface — well above the "Opus finds nothing"
target. Patterns the QA1+QA2 prompts should be tightened for:

1. **Cross-file address contradiction sweep.** QA1+QA2 cross-checked
   individual entity addresses against directories but didn't compare
   the same venue's address across the 4-5 files it appears in. Oh
   Faon's 92 Cours Lieutaud appeared in 3 files with the same wrong
   address; dietary.json had the correct 6 Rue Edmond Rostand. The
   contradiction was visible by simply joining on entity name. Add a
   structural pre-check: for every venue name that appears in >=2 files,
   the `address` field must match.

2. **Brewery (or any operator-style topic) name-vs-product distinction.**
   La Rade Torpille is a beer name treated as a brewery name. Single
   WebSearch for "La Rade Torpille address" would have shown the
   product-vs-producer distinction immediately. Add a check: for
   breweries / coffee-roasters / wineries, confirm the entity name maps
   to a producer site (not a SKU page on a retailer).

3. **Same-name-across-cities Italian/Corsican defect.** U Borgu is a
   real Corsican restaurant — just in Porto-Vecchio, not Marseille. The
   prose said "Marseille's Corsican kitchens" but the venue was in
   another city. Add a geo-scope check on every named venue in
   editorial prose: confirm the venue exists IN THE SCOPED CITY, not
   just somewhere in the country/region.

4. **Hours overstatement: Tue-Sat→Thu-Sat overstates by 2 days; Daily
   →Tue-Sun overstates by 1.** Both are off-by-N defects on hours,
   already a known weak class (Atlanta QA1 hours pattern). Suggests
   pass-1 could mechanically cross-check entity `hours` against the
   `cuisine_evidence_url` / `source_url` page text for the day-of-week
   tokens before letting hours ship.

5. **Plate-count / serving-count "exact-looking" numbers from memory.**
   60-80 small plates is a memory number for AM; documented count is 44.
   Either anchor the number to a fetched URL or use "dozens" / "around
   N".

## Below-floor topics after Opus

- **breweries.json: 4 entries (floor 5)** — La Rade Torpille removed for
  fabrication. Needs 1+ real Marseille brewery added in next research
  pass. Candidates worth verifying: Beer'Ocratie (173 Boulevard Chave,
  13005), Brasserie de Mars, La Cane Bière (32 Boulevard Philippon,
  13004).
- **cooking-classes.json: 4 entries (floor 5)** — unchanged from QA2
  (L'Atelier des Chefs closed June 2025 in QA2). Backfill candidates
  flagged by QA2 still apply.

## Pass-1 verify_entities after Opus edits

`scripts/verify_entities.py --country france --city marseille` → 0 HARD
failures, only acceptable WARNs (own_site_only on directory sources,
anti-bot 403s, dead third-party content URLs).

`scripts/validate_data.py --city marseille` → exit 0, length WARNs
unchanged from QA2 (per-entity descriptions intentionally over the 165
cap, accepted), plus breweries-below-floor WARN (expected).

## Verdict

VERDICT: PASS

City data is now ship-ready. All 16 defects were fixed in place
(decisive, not flagged). Deterministic gates are green:
`verify_entities.py` 0 HARD, `validate_data.py` exit 0 with only
length-cap WARNs and the expected breweries-below-floor flag.

PROCESS NOTE: K=16 is above the "Opus finds nothing" target. Two
fabrication classes (Oh Faon 3-file address contradiction; La Rade
Torpille phantom brewery at a hair-salon address) and one phantom-
venue pair (U Borgu in food-history Corsican community) indicate
QA1+QA2 sweeps had structural gaps for Marseille. Recommend
tightening the QA1+QA2 prompts per the 5 patterns enumerated above
before the next French city dispatch.
