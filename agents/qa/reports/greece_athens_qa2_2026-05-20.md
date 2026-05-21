# QA2 report — Athens (independent second judgment pass)

Date: 2026-05-20
Reviewer: QA2 (independent pass after QA1)
Scope: site-data/greece/athens/data/*.json only

## Pass-1 carry-forward

- verify_entities.py hard failures (post-QA2): 0
- verify_entities.py WARNs: one stale Birdman OpenTable timeout, plus pre-existing day-trips-food warnings — these existed pre-QA and are not blockers.

## QA1 echo verification

- All QA1-removed slugs (Kofio, athens-coffee-roastery, tailor-made-clumsies-coffee) absent from the data tree.
- All QA1-removed phantom-venue names from region.json (Vinexpo, Detrop, Beerz, Kypseli, Holy Spirit, Plaka Culinary Backstreets) absent.
- Spondi "stars: 1" correct everywhere; no "two Michelin stars" / "2-stars" echoes for Spondi remain.
- Kostas hours (Mon-Fri, closed Sat-Sun) propagated correctly; no Mon-Sat echoes.
- Klimataria daily live music + daily hours propagated correctly.
- Pnyka founder line: QA1's "third generation" wording was slightly inaccurate per source (founder Dimitris passed, now son Giorgos runs it). Rewrote to "with the Kotsaris family running the bakery across generations" — true and non-specific.
- Mavro Provato/Atlantikos broken booking_url removals confirmed across all three files.
- Aegina Fistiki Festival corrected dates from QA1's Sept 10-14 to Sept 18-21, 2026 — verified via takeyourbackpack and aeginagreece independent sources. Seasonal-food.json echo "mid-September weekend" still accurate.
- Three festival date corrections (Athens Street Food, Athens Coffee Festival, Tsiknopempti) cross-source verified via independent 2026 sources.

## Judgment defects found (QA1 missed)

### A. Cuisine / category mismatches

- `athens-cooks` (cooking-classes): REMOVED. The domain athenscooks.com is a kitchen store in Athens, **Georgia, USA**, NOT Athens, Greece. Classic Naples-class "real URL + fabricated city" defect. Removed entity from cooking-classes.json. Removed echo from region.json `seo.pages.cooking-classes.description`. Cooking-classes count drops 5 -> 4.

### A2. Specific-fact / chef / address mismatches

- `spondi` (fine-dining): chef field was "Angelos Lantos". Lantos was chef ~2012-2018; current Executive Chef is **Arnaud Bignon** (Bignon was original chef, returned as Executive Chef and General Director of the Trastelis group). Verified via Les Grandes Tables du Monde and Cycladic Spaces 2026 Michelin guide. Corrected.
- `hytra` (fine-dining): chef field was "Tasos Stefatos". Stefatos is at Canaves (Santorini); current Hytra chef is **George (Yiorgos) Felemengas** since at least 2023. Verified via Cycladic Spaces, Instagram, and Hytra Facebook. Corrected.
- `the-zillers` (fine-dining): chef field was "Pavlos Kyriakis". Kyriakis was the previous Executive Chef; current chef per the operator's own Team page is **Vasilis Roussos**. Corrected.
- `drupes-and-drips-coffee` (cafes) and `drupes-and-drips` (bars): address was **"Pittaki 4, Athens 105 54"** in Syntagma — fabricated location. Real address per Foursquare, Tripadvisor and Travel Food People is **Zitrou 20, Athina 117 42** in Makrygianni / Koukaki (near Acropolis Museum). Major Naples-class address fabrication. Updated address, neighborhood, address_quoted, and description in both files. Tip text also adjusted (spritz flips at 13:00 not 19:00).
- `mama-tierra-vegan` (dietary): description claimed owners "Pegah and Hatef Hashemian" — not verifiable on operator's own site, This is Athens, or any 2024-2026 press article. The only named person on the operator's About page is **Chef Polash Alam**. Rewrote to credit Polash Alam, removed unverified owner names.
- `warehouse` (wine-bars): hours field was "Tue-Sun 19:00 to 02:00" with tip "Closed Mondays". Per source, Warehouse on Valtetsiou is an **all-day venue open Mon-Sun 09:00 to 02:30**. Corrected hours, description, and tip.
- `oinoscent` (wine-bars): hours field was "Mon-Sat 18:00 to 00:30" implying closed Sunday. Operator's official page says **Sun-Thu 17:30 to 01:00, Fri-Sat 18:00 to 01:30** — open daily. Corrected.
- `strange-brew-koukaki` (breweries): taproom_hours was "Daily 17:00 to 01:00". Operator's page says **Weekdays 18:00-01:00, Weekends 14:00-01:00**. Corrected.
- `eating-europe-athens-evening` (food-tours): tour name was "Athens Evening Food and Drink Tour" — not the operator's actual product name. Real name per eatingeurope.com: **"Eating Athens: Our Big, Fat, Greek Food Tour"**. Duration corrected 4h -> 3.5h. Price corrected EUR99 -> EUR77.
- `eating-europe-morning` (food-tours): duration 3.5h -> 2.5h. Price EUR89 -> EUR69. Meeting point "Plaka and Koukaki" -> "Tsokri Square, Koukaki" (per operator's listing).
- `athens-food-on-foot-ultimate` (food-tours): price EUR85 -> EUR78 (operator's actual price).
- `lazy-duck` (bars): address was "Agia Irini Square" (no number) — refined to specific "Platia Agias Irinis 2, Athens 105 60" per Tripadvisor / yourathensguide source. Ernst Ziller architectural claim re-verified as accurate (Karagiannis Mansion 1893, confirmed via thegreekfoundation).

### E. Editorial-prose echoes (E1/E2/E3 sweeps)

- `food-history.json` "new Athenian wave" era summary: claimed "The Onassis Foundation opened Delta in 2022". Wrong on two counts. Delta is at the **Stavros Niarchos Foundation Cultural Centre (SNFCC)**, not the Onassis Foundation (Onassis runs Stegi and READY); and Delta opened **July 2021**, not 2022. Rewrote to "Delta opened at the SNFCC in 2021" — true, succinct, and brings the era summary within length cap.
- `region.json` `seo.pages.cooking-classes.description`: removed "Athens Cooks" echo after entity removal; trimmed to fit 140-165 cap.

### E3 phantom-venue sweep

Walked every prose-bearing file/field:
- `city.json` food_culture_summary: Diporto, Karavitis, Oikonomou, Kostas, Bairaktaris, Telis, Spondi, Hytra, Soil, The Clumsies, Line — all map to entities.
- `neighborhoods.json` every vibe: every named venue (Platanos, Saita, Kostas, Bairaktaris, Atlantikos, Klimataria, Telis, Karamanlidika tou Fani, Spondi, Mavro Provato, Karavitis, Kostarelos, Athinaikon, Mama Tierra, Taf Coffee, Strange Brew, Peas, Oikonomou, Aleria, CTC, Ariston, Tzitzikas kai Mermigas, Nolan, The Zillers) maps to an entity.
- `food-history.json`: Spondi, Hytra, CTC, The Clumsies, Strange Brew, Delta, Karamanlidika tou Fani — all map.
- `seasonal-food.json`: Pantopoleion, Varvakios, Aegina Fistiki Festival — all map.
- `signature-dishes.json` every history + where_to_eat: Kostas Souvlaki, Bairaktaris, Diporto, Karavitis Tavern, Klimataria, Taverna tou Oikonomou, Ariston, Takis Bakery, Krinos, Lukumades, Taverna Saita, Taverna Platanos — all map.
- `region.json` SEO descriptions: every named venue matches an entity. No new phantoms introduced.
- `itineraries.json` every summary + day title + meal prose: every venue named (Kostas, Taf, Ariston, Saita, Clumsies, Little Tree, Varvakios, Karavitis, Krinos, A for Athens, Atlantikos, Underdog, Mavro Provato, Karamanlidika, Spondi, Strange Brew, Diporto, Oikonomou, Mama Roux, Kostarelos, Manimani, Platanos, Lukumades) maps to a venues[] slug.
- Per-entity description/tip/why_hidden: no cross-references to phantom venues found.

### E4 verified-block consistency

- Spondi/Hytra/The Zillers chef-name edits do NOT require verified-block updates (the chef field is editorial, not in the verified block).
- Drupes and Drips address change: verified.address_quoted updated to "Zitrou 20, Athina 117 42" in both files.
- Warehouse hours change: hours is editorial, no verified-block update needed.
- Oinoscent hours change: same.
- Strange Brew taproom_hours: same.
- Eating Europe tour name change: source_url remains valid (catalog page).
- Lazy Duck address refinement: verified.address_quoted updated to "Platia Agias Irinis 2, 105 60" to match.
- All edited entities retain checked_on = 2026-05-20.

### Section A2 source-URL final-host check (sampled)

Walked unique source_url hosts (57 hosts). Confirmed plausible operator/directory domains for all of them. Only flagged Naples-class redirect was the cooking-classes athenscooks.com (-> Athens, GA kitchen store) — entity removed.

### Itinerary day-of-week × venue-hours re-walk

- `athens-weekend-classics` day 1 (Friday): Taf (Mon-Sat) OK, Kostas (Mon-Fri) OK, Ariston (Mon-Sat) OK, Saita (daily) OK, Clumsies (daily) OK.
- `athens-weekend-classics` day 2 (Saturday): Little Tree (daily) OK, Varvakios (Mon-Sat) OK, Karavitis (Sat opens 13:30) OK at 14:00, Krinos (Mon-Sat) OK, A for Athens (daily) OK, Atlantikos (daily) OK.
- `athens-souvlaki-three-days` day 1 (Monday): Underdog (daily) OK, Kostas (Mon-Fri) OK, Varvakios (Mon-Sat) OK, Mavro Provato (Mon 13:00-24:00) OK.
- `athens-souvlaki-three-days` day 2 (Tuesday): Ariston (Mon-Sat) OK, Taf OK, Karamanlidika (Mon-Sat) OK, Spondi (Mon-Sun 19:30) OK at 21:00.
- `athens-souvlaki-three-days` day 3 (Wednesday): Krinos OK, Diporto (Mon-Sat lunch) OK, Strange Brew (Wed 18:00 open) OK at 18:30, Oikonomou (Mon-Fri opens 19:00) OK at 20:30.
- `athens-family-trip` day 1 (Saturday): Ariston OK, Manimani (closed Mon, Sat open) OK, Platanos (Sat 12:00-24:00) OK at 19:30, Lukumades (daily) OK.
- `athens-family-trip` day 2 (Sunday): Mama Roux (daily) OK, Kostarelos (Sun 10:00-18:00) OK at 13:30, Little Tree OK, Saita (daily) OK at 19:30.

No new day-of-week × hours collisions found beyond what QA1 fixed.

## Below-floor topics (unchanged from QA1)

- coffee-roasters: 3 (Taf, Underdog, Mind the Cup) — all genuinely independently verifiable
- breweries: 3 (Strange Brew, Noctua, Barley Cargo)
- cooking-classes: 4 (after Athens Cooks removal) — was 5
- dietary.halal: 0 (correct, do not invent)
- dietary.kosher: 1 (Chabad of Athens)
- itineraries: 3

## Geographic note (not a defect)

- Mind the Cup is in Peristeri (western suburb), Hytra at Onassis Cultural Centre in Neos Kosmos, Delta in Kallithea, Venetis Kifisia — all currently tagged to neighborhoods that are imperfect fits because neighborhoods.json has 10 city-centre slugs only. Adding `neos-kosmos`, `kifisia`, `peristeri` slugs is out of QA scope (research / catalog work).

## Defects total: 15

- 1 fabricated cooking-class entity removed (Athens Cooks — Athens GA defect)
- 3 fine-dining chef-name corrections (Spondi Bignon, Hytra Felemengas, Zillers Roussos)
- 1 cafe/bar address-fabrication double-correction (Drupes and Drips: Pittaki 4 -> Zitrou 20, neighborhood + description)
- 1 dietary owner-name fabrication scrubbed (Mama Tierra)
- 3 wine-bar / brewery hours corrections (Warehouse, Oinoscent, Strange Brew)
- 3 food-tour name/duration/price corrections (Eating Europe x2, Athens Food on Foot)
- 1 lazy-duck address refinement (square -> Platia Agias Irinis 2)
- 1 food-history.json era summary correction (Onassis Foundation -> SNFCC; Delta 2022 -> 2021)
- 1 region.json cooking-classes description trim after athens-cooks removal
- 1 Aegina Fistiki Festival 2026 dates correction (QA1 Sept 10-14 -> verified Sept 18-21)
- 1 Pnyka description wording trim (third-generation -> across generations)

## Verdict

VERDICT: PASS

The Naples-class defect class hit one cooking-class entity (Athens, GA) and one cafe/bar address-fabrication (Drupes & Drips). Both removed/fixed. Three high-profile fine-dining chef names were wrong; all three fixed against operator-team-pages or current 2026 Michelin sources. Festival date error in QA1 corrected via independent 2026 sources. Itinerary day-of-week walk produced no new collisions. Below-floor topics remain below floor by content-reality (do not invent).
