# QA report — Amsterdam (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety green pre-QA per scope note).
- verify_entities.py warnings: a known cohort of transient anti-bot 401/403/429s on dignita.nl, moakpancakes.com, feijoa.nl, opentable.com/r/tempo-doeloe-amsterdam — research-stage flagged, verified live in-browser, not touched here.

## Judgment defects found

### A. Cuisine / category mismatches
- `tarim-uyghur` (casual-dining) and `tarim-uyghur-halal` (dietary/halal): claimed address `Sint Jacobsstraat 16, 1012 NC` (centrum, near Centraal). Independent-directory cross-check on the cited Zabihah listing AND multiple Amsterdam directories show the actual venue at **Aalsmeerweg 34H, 1059 AK Amsterdam** in Amsterdam-Zuid. Fixed both entries (address, neighborhood, prose). This is the "real-URL + fake-address" defect class from the memory file — agent had the correct Zabihah source URL but invented a centrum address.
- `sham-syrian` (dietary/halal): claimed `Nieuwendijk 116, 1012 MS Amsterdam`. Operator's own site (restaurantsham.nl) lists ONLY three Sham locations: Witte de Withstraat 125-H (West), Borneosteiger 1 (Oost), Jan Evertsenstraat 69H (Maza). Nieuwendijk 116 does not exist. Rewrote entry to Sham West at the verified Witte de Withstraat address.

### A2. Specific-fact / chef / hours / closure drift
- `spectrum` (fine-dining): claimed 2-star room operating. Multiple Dutch press sources (entreemagazine.nl, derestaurantkrant.nl, hospitality-management.nl, bcbgmagazine.nl, May 2026) confirm Spectrum closes end of May 2026 (within days of publish), with a new dining concept arriving 2027. REMOVED. Cleaned the prose echo in `neighborhoods.json` Centrum vibe ("city's two Michelin two-stars at Flore and Spectrum" → reframed around Flore at De L'Europe).
- `vermeers-wijnkamer` (wine-bars): hours stated "Tue-Sat 16:00-00:00, closed Sun-Mon". Operator's actual hours per multiple 2026 sources (FavorFlav, novacircle) are **Daily 16:00-00:00, Fri-Sat to 01:00**. Fixed.
- `frens-haringhandel` (street-food): hours stated "Tue-Sat 10:00-18:00". Operator site says **Mon and Sun 12:00-18:00, Tue-Sat 11:00-18:00**. Fixed (zip code also corrected from 1017 BB to 1017 AW per operator site).
- `stubbe-s-haring` (street-food): address `Singel 504, 1017 AX` "next to the Munttoren" — the real Stubbe's is at **Singel 8 / Haarlingersluis 1013 GA** near Centraal/Haarlemmerstraat. Singel 504 is south end by the Bloemenmarkt; Stubbe's is the opposite end. Fixed address and prose. Also fixed the corresponding echo in `signature-dishes.json` hollandse-nieuwe-haring history.
- Sampurna tip: "The Singel branch closed; Lijnbaansgracht is the one." Sampurna's own site/contact lists only Lijnbaansgracht 161; no current or former Singel branch is referenced. The "branch closed" claim is fabricated narrative. Rewrote tip.
- `bakhuys-amsterdam` (bakeries): address `Witte de Withstraat 89, 1057 ZA Amsterdam` (West). Operator's own site puts Bakhuys at **Sarphatistraat 61, 1018 EX Amsterdam** (Oost, near Weesperplein). The Witte de Withstraat address is incorrect; venue is the right one (1926 family bakery is real). Fixed address and "West" → "Oost" framing.
- `bonboon` (dietary/vegan): address `Boekhorststraat 5, 1018 SK`. Both operator site and HappyCow list **Rozenstraat 12, 1016 NX** (Jordaan, inside Hotel Mercier). Fixed.
- `hearth` (dietary/vegan): address `Eerste Helmersstraat 88, 1054 DR Amsterdam` (Oud-West). HappyCow + operator site confirm the venue **moved to Camperstraat 26, 1091 AG** in Oost in January 2022. The Albert Cuypstraat origin closed and the current Hearth is in Oost. Fixed.
- `soil-vegan-cafe` (dietary/vegetarian): address `De Wittenkade 1, 1052 AB`. Operator and HappyCow both confirm **Bilderdijkstraat 141H, 1053 KN** is the location. Fixed.

### B. Route / itinerary mismatches
- No food-tour route fabrications detected. Hungry Birds Original confirmed at the cited 4.5h/De Pijp format; Eating Europe Jordaan tour confirmed; Sherpa, Secret Food Tours and Hungry Birds Bike all match operator listings.

### C. Festival month corrections
- `taste-of-amsterdam` → renamed to `bite-of-amsterdam`. Taste of Amsterdam was rebranded "Bite of Amsterdam" in 2024 (operator confirms succession). 2026 dates corrected from **June 5-8** (data) to **June 19-21** (operator + cross-source). Source URL repointed to biteofamsterdam.com.
- `tapt-festival`: `annual: false` (defensive flag). TAPT is in fact a multi-city annual touring festival; Amsterdam Oost (Flevopark) edition is **May 8-9, 2026**. Restored `annual: true`, added start/end dates. Renamed entry to "TAPT Beer Festival Amsterdam Oost" to clarify it's the Amsterdam stop on the tour.
- `pint-bockbierfestival`: `annual: false` (defensive flag). Operator site confirms it's the 44th annual edition, **October 2-3, 2026** at De Hallen Studio's (matches Bellamyplein 51 address). Restored `annual: true`, added start/end dates.
- `amsterdamse-terrassen-festival`: shipped as single day July 26. Operator (hatf.nl, followthebeat) confirms **July 23-26, 2026** (4 days) at Rembrandtpark. Fixed day_range and dates. Source URL repointed to operator hatf.nl.
- `rollende-keukens`: confirmed May 13-17 2026 per operator and Amsterdam municipality calendar. No change.

### D. Thin-category fabrications

Dietary sub-counts after this pass (floor in parens):
- vegan: 3 (floor 4) — Mr & Mrs Watson REMOVED (closed per HappyCow + Foursquare + several 2024+ confirmations); below floor.
- vegetarian: 1 (floor 2) — De Bolhoed REMOVED (closed Feb 2019 per HappyCow/Foursquare/Yelp; agent shipped a venue closed for over six years); below floor.
- gluten_free: 2 (floor 2) — no defects.
- halal: 3 (floor 3) — addresses fixed (Tarim Aalsmeerweg, Sham West), nothing removed.
- kosher: 2 (floor 2) — both Chabad House entries are distinct concepts (restaurant vs. Shabbat meals), allowed.

Bakeries: Lefebvre REMOVED. The cited entity at "Hartenstraat 2" does not exist as a viennoiserie — independent searches return no Amsterdam patisserie by that name; the Hartenstraat address is occupied by a different bakery (Madame Croissant at 29H, not Lefebvre). Source URL was an Amsterdam Foodie best-restaurants page, not a Lefebvre-specific listing. Total bakeries went 10 → 9 (floor unknown but above 8). Cleaned echo in `seasonal-food.json` strawberries note.

### E. Editorial-prose closed-venue echoes

- `region.json` SEO descriptions (E1 + E3 echoes):
  - `fine-dining.description`: named "Spectrum" → removed; substituted "Vinkeles, RIJKS"; count 12 → 11.
  - `bakeries.description`: named "Lefebvre" → removed; substituted "Petit Gateau"; count 12 → 9.
  - `dietary.description`: named "Mr & Mrs Watson" → removed; rewrote opening to "Vegan Junk Food Bar, Bonboon, Hearth, Bazar".
  - `festivals.description`: named phantom "BroodKaas" (E3 — no such entity in our data) AND outdated "Taste of Amsterdam" → rewrote with the four real festival names; count 8 → 6.
- `neighborhoods.json` Centrum vibe: named Spectrum → reframed around Flore (the surviving two-star room).
- `seasonal-food.json` strawberries note: named Lefebvre → swapped to Ree7.
- `signature-dishes.json` hollandse-nieuwe-haring history: said "Stubbe's at Singel" with implied Munttoren context — rewrote to "Stubbe's at the Haarlingersluis on the Singel".
- `signature-dishes.json` stamppot `where_to_eat`: listed both "Moeders" and "Moeders Dutch Kitchen" — those are the same operator (the casual-dining entry uses a longer display name). Deduped to "Moeders".

### F. Editorial voice
Nothing egregious; voice is consistent with house style.

## Defects total: 23

Breakdown:
- 4 venues removed (Spectrum, Mr & Mrs Watson, De Bolhoed, Lefebvre).
- 6 address corrections (Bonboon, Hearth, SOIL, Tarim Uyghur ×2, Bakhuys, Stubbe's, Sham Syrian).
- 4 festival corrections (Bite of Amsterdam rename + dates, TAPT annual + dates, PINT annual + dates, Terrassen Festival dates).
- 3 hours / phone-detail corrections (Vermeers, Frens, Stubbe's).
- 5 prose echoes cleaned (region.json ×4, neighborhoods.json, seasonal-food.json, signature-dishes.json hollandse-nieuwe + stamppot).
- 1 fabricated narrative fix (Sampurna "Singel branch closed").

## Below-floor topics after QA

- dietary/vegan: 3 (floor 4) — needs one research backfill (Watson was the missing fourth; HappyCow's main Amsterdam vegan listing is the canonical source for candidates).
- dietary/vegetarian: 1 (floor 2) — needs one research backfill (De Bolhoed gone; candidates include Vegan Junk Food Bar's vegetarian cousins or longstanding rooms like Golden Temple).
- fine-dining: 11 (no formal floor) — Spectrum removed; remaining list still dense.
- bakeries: 9 (no formal floor) — Lefebvre removed; still well-stocked.

`signature-dishes.json` `make_it_yourself` recipe blocks remain blank by research-stage decision (budget). Not a QA defect, flagged per scope brief.

## Verdict
VERDICT: PASS

(23 defects, but >half are deterministic facts the research agent should have caught — address fabrications and a defensive `annual: false` on festivals. Pattern-wise this is the "real-URL + fake-address" + "agents pick venues from old must-eat lists without verifying current operation" defect cluster from memory; verify_entities.py token-subset normalizer didn't catch the Tarim Sint-Jacobsstraat / Bakhuys Witte-de-With substitutions because the fake addresses were internally consistent with their `address_quoted` fields. Worth a research-prompt tightening pass before the next NL dispatch.)
