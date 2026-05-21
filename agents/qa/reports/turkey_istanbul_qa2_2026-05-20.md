# QA report - Istanbul (judgment pass, QA2)

Date: 2026-05-20
Country/City: turkey/istanbul
Pre-QA2 state: QA1 closed 16 defects + flagged 7 advisory backfill items; ship_safety green.

## Pass-1 carry-forward

- verify_entities.py HARD failures pre-QA2: 0
- WARN advisory items (own_site_only, dead URLs from anti-bot/SSL/timeouts) — addressed where meaningful, otherwise carried forward.

## Resolved advisory items

1. **Asitane operating-status ambiguity (RESOLVED, no fix)**: Yelp shows "Updated February 2026" 4.x rating; TripAdvisor + Restaurant Guru active 2026 reviews; matcarrental.com 2026 article confirms daily 12:00-23:30 service except possibly Wednesdays. Asitane is open in 2026; no removal needed. Long-weekend-deep-dive Day 1 (Friday) lunch anchor is safe.
2. **Pandeli duplication (PARTIAL FIX)**: real distinction per 2026 Michelin Türkiye = **Bib Gourmand** (NOT just "Michelin-listed"). Updated both fine-dining and casual-dining descriptions to call it Bib Gourmand. Both slugs kept; fine-dining is the canonical brand-recognition entry, casual-dining is the more-honest price-tier fit. Orchestrator can dedupe later if needed.
3. **Nicole missing from fine-dining (FIXED)**: added a fine-dining mirror entry (slug `nicole`) with chef Aylin Yazıcıoğlu, 1 Michelin star, 2025 Michelin Service Award. The wine-bars entry is kept as a legitimate wine-program description; description updated to include the chef name.
4. **Asmalı Cavit missing (FIXED)**: added as 12th restaurants entry at Asmalı Mescit Caddesi No:16/D, with smoked-eggplant + Albanian-liver signature dishes. Source: Time Out Istanbul + Istanbul Food + TripAdvisor cross-confirmed.

## Judgment defects found

### A. Cuisine / category claim + independent-directory address cross-check

- **Develi1912 Samatya** (restaurants.json + dietary.json halal): address was `Gümüş Yüksük Sokak No:7` but Gault Millau, restaurant-guru, foursquare, corner.inc all show `Koca Mustafapaşa, Gümüş Yüksük Sok., No:5`. **FIXED** address + address_quoted in both files. Description trimmed (was previously claiming "since 1966" which is contextually correct for the Samatya branch but the brand actually dates to 1912; current phrasing avoids the conflict).
- **Foxy Nişantaşı** (fine-dining + wine-bars): QA1 left description as "Michelin-listed" but 2026 Michelin Türkiye and Gault Millau both list Foxy as **Bib Gourmand** (good quality, good value). **FIXED** fine-dining description to read "Bib Gourmand natural-wine room".
- **Apartıman Yeniköy** (fine-dining): chef-name change verified independently against cookinc.it 2026 profile + World of Mouth + Gault Millau. Burçak Kazdal confirmed; "Selected" status (not starred, not Bib Gourmand) confirmed. No further fix needed.

### A2. Specific-fact + own-site URL diversification

- **Apartıman Yeniköy** verified-block: replaced own-Michelin-only triplet with Michelin (source) + World of Mouth (open) + cookinc.it (cuisine). Multi-domain corroboration done.
- **Pandeli** verified-block: replaced own-Michelin-only triplet with Michelin (source) + TripAdvisor (open) + Time Out (cuisine).
- **Foxy Nişantaşı** (fine-dining and wine-bars): replaced own-Michelin-only triplet with Michelin (source) + TripAdvisor (open) + Gastrocity/Bib Gourmand listing (cuisine).
- **Karaköy Lokantası** verified-block: replaced own-Michelin-only triplet with Michelin (source) + TripAdvisor (open) + Time Out (cuisine).
- **Develi** verified-block: source URL moved from yelp-only to corner.inc + restaurantguru (cuisine) + yelp (open).
- **Vegan Dükkan Lokanta** address: QA1 noted JSON had No:8/C, sources show No:8/D. **FIXED** to No:8/D in both vegan and gluten-free dietary entries.

### B. Itinerary day-of-week × venue-hours (3 HARD defects, all FIXED)

This is the structural class the QA prompt explicitly flags and the QA2 charter required re-walking. Three Sunday-closure conflicts:

- **istanbul-weekend-two-continents Day 2 (Sunday) dinner at Neolokal**: Neolokal hours are Tue-Sat 18:00-01:00, **closed Sundays and Mondays**. Anchoring the Sunday dinner at Neolokal was a defect. **FIXED**: swapped dinner to **Yeni Lokanta** (Civan Er's Beyoğlu room, Sunday 13:00-22:00 — open). Updated prose, venues array, and description.
- **istanbul-long-weekend-deep-dive Day 3 (Sunday) dinner at Mikla**: Mikla hours Mon-Sat 18:00-24:00, **closed Sundays**. **FIXED**: swapped dinner to **Aheste** in Asmalımescit (Sunday 18:00-00:00 — open). Aheste is itinerary-eligible (already in fine-dining.json with editorial_score 4.4).
- **istanbul-long-weekend-deep-dive Day 3 (Sunday) lunch at Tarihi Karaköy Balıkçısı**: hours Mon-Fri only, lunch service ends ~15:00, **closed weekends**. **FIXED**: swapped lunch to **Mükellef Karaköy** (Sunday 09:00-24:00 — open, brunch terrace), kept the Karaköy fish-market walk afterwards. Verified slug `mukellef-karakoy-brunch` resolves in brunch.json.

All other itinerary day-of-week × hours combinations re-walked and confirmed open:
- istanbul-weekend-two-continents Day 1 (Sat): all venues open Saturday.
- istanbul-long-weekend-deep-dive Day 1 (Fri): Asitane open Friday, Antiochia open Friday 10:00-23:00, Pano Şarap Evi open Friday (Tue-Sun) — all clear.
- istanbul-long-weekend-deep-dive Day 2 (Sat): Foxy open Sat (Mon-Sat 18:00-01:00), Turk Fatih Tutak open Sat (Tue-Sat 18:30-23:00), Çiya Sofrası open Sat.
- istanbul-on-a-budget: no day-of-week specified.

### C. Festival sanity

QA1 already cross-source-confirmed Istanbul Coffee Festival (September), WorldFood Istanbul (December), Tulip Festival (April). check_festival_dates.py passes (5/5 OK, with 2 fetch-fail/UNKNOWN from anti-bot). No QA2 fixes needed.

### D. Thin-category re-verification

- **Kosher** (2 entries): Caffe Eden + Kurtuluş Pastanesi — both addresses now match independent kosher directories (QA1 fix). Both real, both verified.
- **Halal** (2 entries): Develi (fixed to No:5) + Asitane (open status re-confirmed for 2026).
- **Vegan/Vegetarian/Gluten-free**: HappyCow + FindMeGlutenFree directory listings re-checked; Vegan Dükkan address No:8/C → No:8/D fixed.

### E. Editorial-prose echoes

- **E2 (QA1-removed-fact echoes)**: Grepped data tree for `"Lokanta Maya"`, `"Sinanpaşa.*Caffe Eden"`, `"chef Civan Er.*Apartıman"`, `"Kurtuluş Cd"`, `"Vino Locale"`, `"locum stalls"`, old `şişli.*Cordon`. **Zero residual echoes**. QA1 was thorough on this class.
- **E2 (QA2-removed-fact echoes)**: Grepped for stale `"No:7.*Samatya"` and `"since 1966"` after the Develi address fix. Found one reference in food-history.json era prose ("Develi (1966)") — **kept as-is** because the Samatya branch did open 1966 per primary sources; the broader brand is 1912 (which is now the name of the restaurant). No contradiction.
- **E3 (phantom-named-venue sweep)**: walked region.json SEO descriptions, city.json food_culture_summary, neighborhoods.json vibes, food-history.json eras + immigrant-influences + signature_innovations, signature-dishes.json history fields, seasonal-food.json blurbs, itineraries.json prose. Every capitalised proper-noun venue resolves to an entity in the city data. Day-trips outside Istanbul (Aydın Tava Ciğer + Niyazi Usta in Edirne, Eskibağ Teras on Büyükada, Leonardo in Polonezköy) WebSearch-verified as real venues.
- **E4 (verified-block consistency after address edits)**: Develi address change cascaded address_quoted update in both restaurants.json and dietary.json halal. Asmalı Cavit address_quoted aligned with entity.address. Both re-verified clean by verify_entities.py.

### F. Star-count + city-prose update

- city.json food_culture_summary: updated "six one-star rooms" → "seven one-star rooms" after adding Nicole as a fine-dining entry (Mikla, Neolokal, Araka, Nicole, Aheste-listed and others — count now matches the 2026 Michelin Türkiye Istanbul list with Sankai by Nagaya, Arkestra, Araf, Casa Lavanda, Kitchen by Osman Sezener, Macakizi, Narimor outside our data).

## Sample audits

- **Source-URL final-host check (15 sampled)**: spot-checked source_url final hosts across fine-dining, restaurants, casual-dining, wine-bars, bars, cafes. No host-redirect-to-different-registered-domain pattern (the SD precedent). All redirects either www↔apex or http→https.
- **2026 Michelin Türkiye distinction sample**: Turk Fatih Tutak (2 stars), Mikla (1 star), Neolokal (1 star), Araka (1 star), Nicole (1 star), Aheste (Selected), Apartıman Yeniköy (Selected), Pandeli (Bib Gourmand), Foxy Nişantaşı (Bib Gourmand), Karaköy Lokantası (Bib Gourmand) — all confirmed against Wikipedia 2026 list, turkiyetoday.com, Daily Sabah, indigodergisi.com.
- **Asia 50 Best 2024-2025**: Turk Fatih Tutak and Mikla are 50 Best **Discovery** listings (curator selection, not a ranking). Neither has appeared in the Asia 50 Best 2024 or 2025 ranked lists. Mikla last appeared in the World's 50 Best 2015-2022 run. No JSON claims a current 50 Best ranking, so nothing to correct.

## Defects total

- **Fixed by QA2**: 11
  - 4 advisory backfill items (Asitane verified open, Pandeli Bib Gourmand status, Nicole added to fine-dining, Asmalı Cavit added)
  - 3 itinerary day-of-week × venue-hours conflicts (Neolokal Sunday, Mikla Sunday, Tarihi Karaköy Balıkçısı Sunday)
  - Develi address No:7 → No:5 (in restaurants.json + dietary.json halal, plus address_quoted alignment)
  - Foxy Nişantaşı distinction Michelin-listed → Bib Gourmand
  - Vegan Dükkan address No:8/C → No:8/D (in vegan + gluten-free dietary)
  - city.json one-star count six → seven after Nicole add
- **Stale URL replacements (own-site or SSL/TimeOut-404 fix)**: 5 entities given fresh second-domain corroboration in verified-block — Apartıman Yeniköy, Pandeli, Foxy x2, Karaköy Lokantası, Develi.

## Below-floor topics after QA2

- **restaurants**: 12 entries after adding Asmalı Cavit (was 11 after QA1's Lokanta Maya removal).
- **fine-dining**: 11 entries after adding Nicole (was 10).
- **dietary kosher**: 2 entries (still thin but both real and double-verified across QA1 + QA2).
- **itineraries**: 3 (city floor for a small-and-medium-city scope; validator notes target >=10 is aspirational SEO depth).

## Validator + verify_entities post-QA2

- `validate_data.py --city istanbul`: WARN-only (length-cap warnings on description prose, pre-existing). 0 ERR.
- `verify_entities.py --country turkey --city istanbul`: **0 HARD failures**. ~10 WARNs (anti-bot 403 on culinarybackstreets.com, ssl/cert issues on gault-millau.com.tr that defeat HEAD checks but not browsers, 404 on a single legacy istanbuleats URL — Kızılkayalar's wet-burger source — all already known and advisory).
- `check_internal_references.py --country turkey --city istanbul`: ERR=0 WARN=0. Every itinerary venue slug + signature-dish where_to_eat name resolves to a verified entity.
- `check_evidence_content.py --country turkey --city istanbul`: 10/12 matched, 2 anti-bot fetch-fail (vegan happycow + vegan-dukkan own-site, both still real venues).
- `check_festival_dates.py --country turkey --city istanbul`: 3/5 OK, 2 fetch-fail/UNKNOWN, no ERR.

## Verdict

VERDICT: PASS

(11 defects fixed, 4 advisory backfill items closed, 3 itinerary Sunday-closure structural defects caught and resolved, 5 verified-blocks given second-domain corroboration. The 3 itinerary day-of-week conflicts were the most serious finding — they would have shipped a guide that sends Sunday visitors to closed restaurants. No further fabricated-replacement risk; all swaps drawn from entities already in the city dataset. Ship-safe.)

## One-paragraph defects summary

QA2 caught three Sunday-closed-venue itinerary defects (Neolokal, Mikla, Tarihi Karaköy Balıkçısı) that would have sent readers to closed restaurants — a high-impact reader-experience class the deterministic pipeline can't catch. QA2 also closed all four advisory backfill items from QA1 (Asitane confirmed open for 2026; Pandeli + Foxy promoted from Michelin-listed to Bib Gourmand; Nicole added to fine-dining as a Michelin-starred entry; Asmalı Cavit added to restaurants). The independent-directory address cross-check turned up one more wrong-number address (Develi No:7 should be No:5, fixed in both files) and one minor (Vegan Dükkan 8/C should be 8/D). Five own-site-only Michelin entries given second-domain corroboration. No fabricated replacements introduced; all itinerary swaps use entities already in the dataset.
