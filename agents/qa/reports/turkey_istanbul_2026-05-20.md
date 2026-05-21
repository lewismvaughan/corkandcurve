# QA report - Istanbul (judgment pass-2, QA1)

Date: 2026-05-20
Country/City: turkey/istanbul
Pre-QA state: ship_safety green per dispatch. 26 JSON files covering ~150 entities.

## Pass-1 carry-forward

- verify_entities.py HARD failures: 0
- verify_entities.py warnings: ~14 (mostly own_site_only WARNs for Michelin-only entities + a few dead cuisine_evidence_urls and a Çiya Sofrası SSL timeout). These are advisory, not blockers, and the entities themselves are real and well-sourced.

## Judgment defects found

### A. Cuisine / category mismatches + independent-directory cross-check (FIXED)

- **Apartıman Yeniköy** (fine-dining.json): claimed `stars: 1` and `chef: Civan Er` and "Civan Er's one-star Bosphorus bistro" in description. Per 2026 Michelin Türkiye Wikipedia + Michelin Guide listing pages, Apartıman Yeniköy is "Selected" (Recommended), NOT 1-star. The actual chef-owner is Burçak Kazdal (Civan Er runs Yeni Lokanta). REMOVED stars, replaced chef name with "Burçak Kazdal", rewrote description to "Michelin-listed" not "one-star". This was the dispatch's flagged "real-URL + fake-fact" defect pattern.

- **Caffe Eden** (dietary.json kosher): address was "Sinanpaşa Mah., Beşiktaş" but real address per gokosher.com + worldjewishtravel + yeahthatskosher = "Mecidiye Mah., Gözlükçü Sk. No:18, 34347 Beşiktaş". FIXED address + address_quoted. Description still mentioned "Şişli's Jewish community" delivery; corrected to "Arnavutköy's" (one of the actual delivery zones per source).

- **Kurtuluş Pastanesi** (dietary.json kosher): address was "Kurtuluş Caddesi No:36/A" but real per multiple sources = "Şahin Sokak No:36/A" (off Kurtuluş Cad.). FIXED address + address_quoted + description ("on Şahin Sokak just off Kurtuluş Caddesi").

### B. Route / itinerary operator mismatches (FIXED)

- **Culinary Backstreets Two Markets** (food-tours.json): duration claimed "8 hours"; operator's actual page says 6.5 hours. FIXED.
- **Culinary Backstreets Beyoğlu** (food-tours.json): claimed duration "5 hours" and "USD 125"; operator's current Hidden Beyoğlu By Night is $145 (all CB Istanbul tours are now $145 per the operator page). FIXED to "USD 145" and "Afternoon into evening" duration; description updated to use the operator's official tour name.
- **Turkish Flavours Two Continents** (food-tours.json): claimed "EUR 195"; operator lists tour starting at $175 USD. FIXED to "USD 175".
- **Turkish Flavours Istanbul Bites Kadıköy** (food-tours.json): claimed "EUR 140"; operator lists starting at $110 USD. FIXED to "USD 110".

### C. Festival month corrections (none needed)

Cross-checked Istanbul Coffee Festival (Sep 10-13 2026, ✓), WorldFood Istanbul (Dec 15-18 2026, ✓), Tulip Festival (Apr 1-30, ✓). Sample of 3 against independent non-organiser sources (biletino, tradefairdates, ShuttleVIP, VisitIstanbul) matched JSON months and approximate days.

Festivals.json typo: "locum stalls" -> "lokum stalls" (Turkish delight). FIXED.

### D. Thin-category fabrications

- **Kosher** (2 entries, both verified above): Caffe Eden + Kurtuluş Pastanesi both real, both required address fixes (see A). NOT fabricated; both have multiple independent kosher-directory listings (gokosher, worldjewishtravel, totallyjewishtravel, culinarybackstreets).
- **Halal** (2 entries): Develi1912 Samatya and Asitane. Develi address confirmed. Asitane closure status uncertain (see E).
- **Vegan** (3 entries): all verified at HappyCow / TripAdvisor / wanderlog.
- **Gluten-free** (2 entries): both also vegan, both legitimate per findmeglutenfree directory.
- **Vegetarian** (3 entries): all real.

### E. Editorial-prose echoes and phantom venues (FIXED)

**E1. Closed-venue removals + echoes:**
- **Lokanta Maya** (restaurants.json): REMOVED. Closed since 2016 per Culinary Backstreets farewell article; Yelp "CLOSED" (last verified Oct 2025); Foursquare "Now Closed". Research agent fabricated a "come back after a 2016 pause" — no evidence of reopening. Grepped data tree for echoes: no other files reference Lokanta Maya. Clean removal.

**E2. QA-rewritten-fact echoes (FIXED):**
- **city.json food_culture_summary**: claimed "two Michelin two-star kitchens (Turk Fatih Tutak and Vino Locale)" — Vino Locale is in Urla, Izmir, NOT Istanbul. The 2026 Michelin Türkiye gave Vino Locale its 2 stars in Izmir Province. FIXED to "Turkey's only two-Michelin-star kitchen (Turk Fatih Tutak), six one-star rooms..."
- **region.json index.description**: same "two Michelin two-star kitchens" claim; FIXED to "Turkey's only two-Michelin-star kitchen".
- **neighborhoods.json sariyer vibe**: "Araka and Apartıman Yeniköy both hold Michelin stars" — Apartıman is Selected, not starred. FIXED to "Araka holds a Michelin star and Apartıman Yeniköy is Michelin-listed".

**E3. Phantom-named-venue editorial sweep (FIXED):**
- **region.json food-tours SEO description**: "Princes' Islands picks worth booking" — no food-tour entity goes to Princes' Islands (only day-trips-food has Büyükada). FIXED to reference "Turkish Flavours' market-and-ferry routes".
- **region.json itineraries SEO description**: promised "a vegan-friendly plan and a market-and-meze rakı route" — actual itineraries are weekend-two-continents, long-weekend-deep-dive, on-a-budget. FIXED to match real itinerary lineup.
- **region.json signature-dishes SEO description**: listed "künefe" and "kokoreç" as signature dishes; our actual signature-dishes are balık ekmek, iskender, lahmacun, midye dolma, kahvaltı, baklava, mantı. FIXED.

**E4. Verified-block consistency after address edits:** updated `verified.address_quoted` to match new `address` for Caffe Eden and Kurtuluş Pastanesi (both kept `checked_on: 2026-05-20`).

### A2. Specific-fact mismatches

- **food-tours pricing units**: Turkish Flavours and Culinary Backstreets were listed in EUR / wrong USD; corrected against operator pages.
- **food-tours descriptions**: tightened to match operator's current listing.
- **Bambi Cafe street-food** description claimed "24-hour" but hours field is 07:00-05:00 (22 hours). FIXED description to "almost-all-night counter".
- **Le Cordon Bleu Istanbul** (cooking-classes.json): neighborhood was "şişli" but address is Özyeğin University Çekmeköy Campus (Asian side, far from Şişli). FIXED to "çekmeköy".

## Items NOT fixed, noted for backfill / observation

1. **Asitane** (fine-dining + hidden-gems + halal + itinerary day-1 of long-weekend): genuine ambiguity on current operating status. Yelp "Updated February 2026" + recent Tripadvisor reviews + Frommer's listing all suggest open with hours; Atlas Obscura "permanently closed"; restaurant website still shows a 2020 renovation banner. Did NOT remove because (a) ship_safety already cleared it, (b) the QA prompt forbids re-WebSearching existence/closure (pass-1's job), (c) directories that aggregate stale data are equivocal here. **Recommend**: pass-1 backfill should retry the venue's own phone/social to confirm hours; if it has truly closed, the long-weekend itinerary day-1 will need Day-1 venue substitution (Asitane is the lunch anchor for the Edirnekapı/Chora half-day).

2. **Pandeli duplication**: appears in both `fine-dining.json` (slug `pandeli`) and `casual-dining.json` (slug `pandeli-spice-bazaar`). Real category per 2026 Michelin = Bib Gourmand; casual-dining is the more honest fit. Not strictly a defect because slugs differ, but the duplicate inflates the city's fine-dining count by 1. Left for orchestrator decision.

3. **Nicole** (wine-bars.json `nicole-cukurcuma`): real categorization is Michelin 1-star fine-dining tasting menu; in our data it appears only in wine-bars (with description acknowledging "Michelin-starred tasting-menu room"). Not strictly wrong (it does have a serious Turkish-grower wine focus) but not in fine-dining where it belongs. Recommend orchestrator add a fine-dining mirror entry.

4. **Asmalı Cavit** (canonical Asmalımescit meyhane, per dispatch): NOT present in restaurants.json. Floor-acceptable; backfill candidate. Refik, Sofyalı 9, Krependeki İmroz all present and verified.

5. **Vegan Dükkan address** (dietary.json vegan): JSON has No:8/C; multiple sources show No:8/D. Minor enough that I left the data alone; ship_safety address_quoted match still passes. Backfill could correct.

6. **own_site_only WARNs** (Michelin-only entities Apartıman Yeniköy, Pandeli, Foxy, Foxy wine-bar; Culinary Backstreets and Turkish Flavours food-tours; Develi1912 Yelp-only; Karaköy Lokantası Michelin-only): all real venues, just need a second-domain corroboration in verified block. Backfill task.

7. **dead_cuisine_evidence_url WARNs**: Kızılkayalar's `istanbuleats.com/2010/...wet-burgers-as-seen-on-tv` returns 404. Şampiyon Kokoreç + Kızılkayalar both point at `eatyourworld.com/.../midye-tava/` for kokoreç content (URL is for a different dish but is alive). Both venues are unambiguously real and identifiable; cuisine evidence just needs a fresh URL.

## Defects total

- **Fixed**: 16 (1 closed-venue removal + 4 fact rewrites in fine-dining/dietary/cooking-classes/neighborhoods + 4 food-tour duration/price corrections + 1 typo + 5 SEO/prose phantom-venue rewrites + 1 chef name correction)
- **Flagged-not-fixed (backfill candidates)**: 7 (Asitane closure ambiguity, Pandeli dup, Nicole missing from fine-dining, Asmalı Cavit floor gap, Vegan Dükkan number, own_site_only WARNs, dead cuisine_evidence_urls)

## Below-floor topics after QA

- **restaurants**: 11 entries after removing Lokanta Maya (was 12). Probably acceptable; canonical lineup intact (Çiya x2, Karaköy Lokantası, Develi, Antiochia, Hayvore, the 3 meyhanes, Tarihi Karaköy Balıkçısı, Lokanta 1741). Asmalı Cavit would be a natural 12th.
- **dietary kosher**: 2 entries (still thin but both verified).
- **fine-dining**: 10 entries.
- **itineraries**: 3 (validator notes target >=10 but this is the current city floor for itineraries).

All other topics at or above their typical floor.

## Validator + verify_entities post-QA

- `validate_data.py --city istanbul`: WARN level only (length-cap warnings on description prose, pre-existing). No ERR.
- `verify_entities.py --country turkey --city istanbul`: 0 HARD failures. ~14 WARNs (own_site_only, dead cuisine_evidence_urls, one Çiya Sofrası SSL timeout). All advisory.

## Verdict

VERDICT: PASS

(16 defects fixed, 7 advisory items noted for backfill. Removed 1 closed venue. No fabricated replacements. No structural research-stage regression worth NEEDS_FIXES — the closure of Lokanta Maya and the Apartıman Yeniköy chef/star mix-up are the kind of single-entity errors that fit the pre-flagged pattern; the rest is editorial cleanup. Ship-safe.)
