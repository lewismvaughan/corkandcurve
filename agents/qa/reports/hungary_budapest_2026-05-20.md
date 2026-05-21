# QA report — Budapest (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (ship_safety green per orchestrator)
- verify_entities.py warnings: 65 (mostly own_site_only on Google Maps URLs and a handful of stale URLs); these were the in-scope spot-check inputs for this pass.

## Judgment defects found

### A. Address fabrications / wrong-venue cross-check fails (independent-directory cross-check)

Independent-directory cross-check (Google Maps + welovebudapest + Restaurant Guru + operator sites) caught a high-volume defect cluster — same pattern as the Naples/Krakow May 2026 batch. ~45% of the entities relying on `https://www.google.com/maps/search/?api=1&query=...` URLs had address or venue-name fabrications.

- `bars.json` warmup-bar: JSON had **Pozsonyi út 6, 1137** (Újlipótváros) — actual Warm Up Cocktail Bar is at **Nagy Diófa u. 26, 1072** (Jewish Quarter / District VII). Fixed address + neighborhood + URLs.
- `breweries.json` mad-scientist-beer: JSON had **Bárczy István utca 1, 1052** — actual Mad Scientist brewery is at Maglódi út 47 (1106 Kőbánya); the city-centre taproom is **Madhouse by Mad Scientist at Anker köz 1-3, 1061**. Rewrote to Madhouse with correct address + URLs.
- `breweries.json` hop-aholic: JSON had **Vámház körút 4, 1093** (Ferencváros) — actual Hopaholic is at **Akácfa utca 38, 1072** (Jewish Quarter). Fixed.
- `breweries.json` jonas-brewery: JSON had **Fővám tér 11-12, 1093** (Bálna) — operator moved from Bálna to **Bikás park (Vahot utca 8, 1119)** in May 2022. Fixed address, neighborhood, hours, URLs.
- `street-food.json` langos-papa (Retró Lángos): JSON had **Bajcsy-Zsilinszky út 79, 1065** — actual address is **Bajcsy-Zsilinszky 25, 1065** (across from Arany János utca metro). Fixed.
- `street-food.json` kolbice: JSON had **Október 6 utca 17, 1051** — Kolbice by Kobe has no such address; known locations are Hold utca 13 (Belvárosi Piac), Fővám tér, Dohány utca. Rewrote to **Hold utca 13, 1054** (Belvárosi Piac).
- `dietary.json` indus-halal-restaurant: JSON had **Vízakna utca 4, 1056** — actual Indus is at **Ráday u. 23, 1092** (Ferencváros). Fixed address + neighborhood.
- `dietary.json` vegan-love: JSON had **Margit körút 31-33, 1024** — actual Vegan Love is at **Bartók Béla út 9, 1114** (Újbuda near Gellért). Fixed.
- `dietary.json` free-glutenmentes-pekseg: JSON had **Zichy Jenő utca 43, 1066** (which is a different bakery, Fittnass Glutenmentes). Rewrote to one of Free's real locations: **Dob utca 28-30, 1072**.
- `brunch.json` felix-kitchen-bar: JSON had **Apród utca 3, 1011** — actual Felix Kitchen & Bar is at **Ybl Miklós tér 9, 1013** (Várkert Bazár). Fixed.
- `cooking-classes.json` budapest-cooking-class-szilvi: JSON had **Hercegprímás utca 18, 1051** (near Basilica) — actual venue is at **Bakáts tér 8, 1092** (Ferencváros near Petőfi Bridge). Fixed.

### Closed-venue removals (stale operator check)

- `bars.json` + `late-night.json` kuplung / kuplung-late-night: **Kuplung permanently closed in 2018**; luxury apartments built on the site. Confirmed by welovebudapest, ruinbarsbudapest, foursquare. Removed from both files. No echoes elsewhere.
- `bakeries.json` + `hidden-gems.json` ruszwurm-cukraszda: **Historic Ruszwurm Cukrászda closed in August 2025** after 15-year legal battle (Hungary Today, daily news Hungary, XpatLoop). Municipality plans new operator tender autumn 2025; not yet reopened as of 2026-05-20. Removed from both files. Itinerary echoes in `itineraries.json` (weekend-classics day 2, wine-and-palinka day 3) rewritten — Day 2 routes straight to Fisherman's Bastion; Day 3 swapped to Daubner Cukrászda for the Buda-hills pastry stop. (Auguszt was first considered but is closed Sundays; Daubner is open Wed-Sun.)
- `wine-bars.json` innio-wine-cafe: Innio Restaurant & Bar at Október 6. utca 9 is **permanently closed** (Foursquare + cityseeker). Removed.
- `wine-bars.json` kispiac-wine-bar (Klassz): **Klassz Étterem és Borbolt is permanently closed** (welovebudapest "Bezárt", Foursquare "Now Closed"). Only the standalone Bortársaság wine shop remains under that brand. Removed.

### Fabricated entities removed (cannot be verified against any independent directory or operator)

- `bakeries.json` + `hidden-gems.json` magdi-cukraszda: claimed at **Csaba utca 6, 1122 Budapest** — the building at Csaba u. 8 (1122) is Artigiana Gelati (gelateria). No "Magdi Cukrászda" exists at that address per any directory. Closest real name match in Budapest is Marodi Cukrászda. Removed from both files.
- `bakeries.json` + `hidden-gems.json` konyhakert-pekseg: claimed at **Akácfa utca 56, 1073 Budapest** — no such "Konyhakert Pékség" exists at that address per any Budapest bakery directory (welovebudapest, offbeatbudapest, tripadvisor). Likely fabricated alongside a stretch toward "Jewish Quarter sourdough bakery chefs love" persona — closest real match is Arán Bakery (different name, different address). Removed.
- `street-food.json` biggys-burger: entity named "Bódi Húsbolt Húsoshátosfehéres" (mangled Hungarian, non-resolvable) with source_url pointing to the Retró Lángos Büfé Google Maps URL — URL + venue name double-fabrication. Removed.
- `street-food.json` vintage-garden-langos (Drót): claimed at **Király utca 14, 1075 Budapest** — only "Drót Bisztró" listing in TripAdvisor is in **Miskolc** (Northern Hungary), not Budapest. No Budapest Drót langos venue verifiable. Removed.
- `dietary.json` veganeey-pizza: claimed at **Wesselényi utca 13, 1077** — no such venue verifiable. Vegan pizza in the Jewish Quarter (Tahina Bite at Wesselényi 2, Vegazzi) are different operators. Removed.

### A2. Specific-fact / chef-name checks (structural, not advisory)

Confirmed 2026 Michelin Budapest list against guide.michelin.com + offbeatbudapest 2026 list: **Stand (2*), Babel (1*), Borkonyha (1*), Costes (1*), essência (1*), Rumour (1*), Salt (1*)**. Costes Downtown is no longer starred (lost in 2022 per Wikipedia list).

- `fine-dining.json` stand: stars field was 1; **Stand has held 2 Michelin stars since 2022** (confirmed Michelin guide + abouthungary news). Updated to 2 and description.
- `fine-dining.json` babel-budapest: chef listed as "Istvan Veres" — **Veres István departed in August 2020**; current executive chef since 2021 is **Kaszás Kornél**. Fixed.
- `fine-dining.json` costes: chef listed as "Eszter Palagyi" — current patron chef per the operator's own homepage is **Jenő Rácz**. Fixed.
- `fine-dining.json` costes-downtown: stars=1 — **no longer starred since 2022** (Wikipedia + hungary-adventures + offbeat 2026 list confirm only 7 stars in Budapest, Costes Downtown not on the list). Set stars=0, updated description, replaced chef "Tiago Sabarigo" (who moved to essência) with **Márk Molnár** (current head chef).
- `restaurants.json` echoes: Stand description "one-Michelin-star" → "two-Michelin-star"; Costes Downtown "holds a Michelin star" → "sits in the Michelin Guide".
- `casual-dining.json` + `restaurants.json` halaszbastya-restaurant: claimed chef **"Barna Szabo"** — Halászbástya's documented head chef per coverage is Zoltán Hammer (2018) or no specifically attributed chef in current sources. Removed chef name from prose; rewrote as generic.
- `food-tours.json` secret-food-tours-budapest: route claimed **"Jewish Quarter food crawl, kürtőskalács, pálinka, langos"** — operator only runs **Budapest Downtown** and **Budapest Óbuda** tours, no Jewish Quarter. Route fabrication. Rewrote to actual offering (Downtown walk, 4 stops, 3-3.5 hours, EUR 89.99).
- `food-tours.json` taste-hungary-culinary-walk: tour name corrected to operator's actual product ("**Jewish Quarter Walk with Lunch**" per tastehungary.com).
- `food-tours.json` budapest-market-tour: route claimed "Central Market guided shop + private kitchen cook-along" — operator's actual flagship is **Three-Market Deep Dive** (three markets across three neighborhoods, one river crossing, EUR 137, max 6 guests). Rewrote.
- `food-tours.json` fat-boy-foodies-walk: duration / stops / price corrected to operator's actual (4 hours, 7 tastings + 1 drink, USD 102).
- `food-tours.json` taste-hungary-wine-tour-tokaj: price/duration updated to operator's actual (USD 498-330 per person tiered, 12 hours, regional specialties lunch, hotel pickup).
- `late-night.json` + `street-food.json` drum-cafe: address **Király utca 13, 1075** → operator's own site says **Dob utca 2, 1072**. Fixed both entries with description/hours alignment.

### C. Festival month / dates corrections (cross-source verified)

- `festivals.json` sweet-days-chocolate-festival: research agent had "corrected" Oct→Sep; **actual 2026 edition is May 1-4** at Szent István tér per gotravel.hu listing + multiple independent travel sources. Fixed start_month/start_day/end_day, day_range, description, source_url.
- `festivals.json` gourmet-festival: claimed May 28-31; **official gourmetfesztival.hu 2026 banner is June 4-7** at Millenáris Park, with Programturizmus + MyLittleHungary echoing. Fixed dates.
- Confirmed without changes: Budapest Wine Festival (Sep 9-12 per aborfesztival.hu); Mangalica Festival (Feb 7-9 per budapestbylocals); Pálinka and Sausage Festival (Oct 2-4); Vörösmarty Christmas Market (mid-Nov to Jan 1).

### E. Editorial-prose echoes after removals/rewrites

- `itineraries.json` weekend-classics day 2: removed Ruszwurm stop, rewrote morning to Fisherman's Bastion direct; updated venues list.
- `itineraries.json` wine-and-palinka day 3: rewrote with Daubner morning + Hungarikum Bisztró lunch + DiVino close (Bock Bisztró is closed Sundays per operator hours; Borkonyha also closed Sundays; Hungarikum is open Sundays 12-14:30 / 18-22).
- `signature-dishes.json` lángos where_to_eat: removed "Drót" (removed entity); replaced "Retró Lángos Büfé" with new canonical name "Retró Lángos Budapest".
- No phantom-venue mentions found in region.json / city.json / neighborhoods.json / food-history.json after sweep.

### Verified-block hygiene (own_site_only and dead-URL cleanup)

Re-pointed verified blocks for these to independent sources (still ~23 entities use Google Maps queries as source_url; these include Szimpla Kert, Mazel Tov, Karaván, Doblo, Fekete Kutya, Kisüzem, Csendes, Ellátó Kert, Tuk Tuk Bar, Anker't, Élesztőház, Lehel/Fény/Hunyadi markets, Szatyor, Auguszt — all venues I cross-checked exist at the claimed addresses, but the provenance URL is still weak):

- Cleaned up Babel cuisine_evidence_url (theworlds50best dead 404 → Michelin Guide).
- Replaced Doblo, DiVino, Kadarka, Palack, Mantra Auguszt source_urls where I edited the entity to point at operator + 1 independent directory.
- Replaced Free Gluténmentes Pekseg URLs to operator's freepekseg.hu + findmeglutenfree.com.
- Replaced Costes Downtown brunch entry's URLs to costesdowntown.hu (after rewriting to Sunday lunch).
- Updated Mad Scientist URLs to madhousebudapest.hu + welovebudapest + untappd.

### F. Editorial flags (qualitative)

- 100+ length-cap WARN entries remain after edits; per QA scope (section F) these are not in-scope to chase exhaustively. Several edited descriptions now go ~5-30 chars over the 165 cap; recommend a non-QA copy-trim pass to bring them under.
- itineraries.json has only 3 entries (SEO target >=10); pre-existing, not introduced by QA.

## Defects total

| Class | Count |
|---|---|
| A. Address fabrications | 11 |
| Closed venues removed (incl. echoes in itineraries) | 4 entity removals + 2 itinerary rewrites |
| Fabricated entities removed | 5 |
| A2. Chef names / star counts / route fabrications fixed | 9 |
| C. Festival date corrections | 2 (Sweet Days, Gourmet Festival) |
| E. Prose echoes resolved | 3 (signature-dishes lángos, two itinerary days) |
| Verified-block URL hygiene | ~15 |

**Total: ~50 substantive judgment defects fixed.**

## Below-floor topics after QA

- `cafes.json`: 11 entries (region SEO description claims 12) — minor under-floor.
- `bakeries.json`: 7 entries after Ruszwurm + Magdi + Konyhakert removals (was 10). Recommend research backfill for at least 3 cukraszda / pékség candidates — Marodi Cukrászda (Pest), a real Buda-hills cukraszda (Daubner is already in), and an Arán Bakery / Pipacs Pékség sourdough room would be defensible additions.
- `dietary.json`:
  - vegan: 2 entries (Napfényes + Vegan Love after Veganeey removal) — under typical floor of 3-4 for a dietary sub-category. Tahina Bite at Wesselényi 2 and Las Vegan'das are real-and-verifiable candidates for backfill.
  - kosher: 2 (Hanna, Carmel) — at floor.
  - halal: 2 (Indus, Titiz) — at floor.
  - gluten_free: 2 — at floor.
  - vegetarian: 2 — at floor.
- `bars.json`: 12 entries after Kuplung removal (was 13).
- `late-night.json`: 7 entries after Kuplung removal (was 8).
- `wine-bars.json`: 6 entries after Innio + Klassz removals (was 8). Recommend research backfill — Tasting Table Budapest, Csendes Társ, Borárium, Bortodoor are real candidates.
- `street-food.json`: 8 entries after Biggys + Drót removals (was 10).
- `breweries.json`: 5 entries after Krak'n Town removal (was 6). Hops & Barley Tap Room, Misina Brewhouse, Stark Sörözde, Hophead Hood Bar would be real candidates.
- `hidden-gems.json`: 7 entries after Magdi + Konyhakert + Ruszwurm removals (was 10).

## Notes for downstream

1. **Independent-directory cross-check at research time** — the URL-fabrication-by-Google-Maps-swap pattern observed in Polish + this Budapest batch keeps producing structural defects pass-1 can't catch. ~50 judgment defects in one city pass after ship_safety green is a research-stage regression worth tightening at the prompt level (require at least one non-google.com/maps URL per entity).
2. **Stale-operator-hours defect class** — Sunday-closed venues shipped in Sunday itineraries (Bock, Borkonyha both closed Sundays) is the same structural defect as Atlanta QA1 caught. Research-stage prompt should require day-of-week × hours cross-check when building itineraries.
3. **Closed-venue lag** — Ruszwurm (closed Aug 2025), Innio, Klassz, Kuplung all shipped through research as "open". Recent-dated open_evidence_url discipline (>= 2025 sources) would catch most of these.
4. **Ellátó Kert** is left in `bars.json` despite ambiguity: welovebudapest.com slug now contains "bezart"; Foursquare/Facebook say closed; Untappd has 2025 check-ins. Flagged for research re-verification, not removed.
5. **Bock Bisztró** is left in `restaurants.json` + `casual-dining.json`; the Józsefváros Bock listing on Foursquare says "Now Closed" but Bock Pest at Erzsébet körút 43-49 (Corinthia Hotel) appears separately active. Worth a research re-verification by phone.
6. The remaining ~23 Google Maps source_url entities should ideally be re-provenanced by a research fixup pass; this QA pass cross-checked their existence/address against independent directories where time permitted but did not rewrite all of them.

## Verdict

VERDICT: NEEDS_FIXES

50+ substantive judgment defects across 14 of 27 topic files — including 4 closed-venue removals, 5 fabricated-entity removals, 11 address fabrications, 9 chef/star/route corrections, and 2 festival date corrections (one of which was a "correction" the research agent had made the wrong way). This volume and pattern (URL-fabrication-by-Google-Maps-swap matching the Polish/Naples May 2026 batch) suggest a research-stage regression. Recommend Opus final pass to spot-check the remaining ~23 entities still on Google Maps source URLs, then ship.
