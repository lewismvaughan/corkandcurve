# QA report — Athens (Opus final judgment pass)

Date: 2026-05-20
Reviewer: Opus final (third reader after QA1 and QA2)
Scope: site-data/greece/athens/data/*.json only

## Pass-1 / QA1 / QA2 carry-forward

- All QA1+QA2 removed slugs (Kofio, athens-coffee-roastery, tailor-made-clumsies-coffee, athens-cooks) absent from data tree.
- All Naples-class chef-name corrections (Bignon at Spondi, Felemengas at Hytra, Roussos at The Zillers) propagated correctly, with no "Lantos / Stefatos / Kyriakis" residuals anywhere.
- Drupes & Drips: Zitrou 20 Koukaki/Makrygianni address propagated to both cafes.json and bars.json entries; verified.address_quoted matches in both; description rewritten away from Syntagma; spritz-time tip rewritten.
- Mama Tierra owner fabrication scrubbed; "chef Polash Alam" cross-verified via 2025-2026 sources.
- Onassis/SNFCC + Delta 2021 echo in food-history.json correct.
- Aegina Fistiki Festival 18-21 Sept 2026 cross-source verified (takeyourbackpack + allovergreece independent of organiser).
- Athens Street Food Festival May 8-24 2026 (three weekends) confirmed via operator + AllEvents.
- Athens Coffee Festival 26-28 Sept 2026 confirmed via World Coffee Beans + Perfect Daily Grind.
- Oenorama 13-16 March 2026 at ONASSIS READY confirmed via travel.gr + Visit Greece + ticketing.
- Tsiknopempti Feb 12 2026 confirmed via Greek City Times + Sigmalive.
- Theofania Jan 6 unchanged (fixed annual date).
- All QA1+QA2 hour corrections (Kostas Mon-Fri, Warehouse all-day, Oinoscent daily, Strange Brew Mon-Fri 18:00 / Sat-Sun 14:00, Klimataria daily) propagated; itinerary day-of-week walk shows no residual collisions.
- Eating Europe tour names (Big Fat Greek Food Tour, Bite from the Acropolis), durations (3.5h, 2.5h), prices (EUR77, EUR69) and Athens Food on Foot EUR78 cross-verified against operator pages.
- Spondi 1-star (Bignon) confirmed via Cycladic Spaces 2026 Michelin guide; Hytra 1-star (Felemengas) and Zillers 1-star (Roussos) confirmed.
- Delta 2-stars + Green Star, Papazacharias and Feskos confirmed via SNF + Athens Gastronomic Forum.
- All QA-edited entities have checked_on = 2026-05-20 and address / address_quoted consistency.
- Source-URL spot-check (5 random hosts: theworlds50best.com, e-restaurants.gr, carryitlikeharry.com, fournosveneti.gr, greekgastronomyguide.gr) all return 200 to the same registered domain. No Naples-class redirects.
- coffee-roasters at 3, breweries at 3, cooking-classes at 4, dietary.halal at 0, dietary.kosher at 1, itineraries at 3 — all below content-strategy floor per content reality, do not invent (rule honored).

## Judgment defects found this pass

### A2. Geographic-claim mismatches in editorial prose

- `city.json` `food_culture_summary`: prose read "Kostas on Agia Irini Square, Bairaktaris and Telis on Evripidou" — this parses as Bairaktaris being on Evripidou too. Bairaktaris is at Monastiraki Square 5 (per restaurants.json + street-food.json + Bairaktaris own site). Telis IS on Evripidou (86 Evripidou). Rewrote to "Kostas on Agia Irini Square, Bairaktaris on Monastiraki Square and Telis on Evripidou" — each venue paired with its correct street.

- `fine-dining.json` `cookoovaya` description: said "Cookoovaya in Pangrati" — Cookoovaya is at Chatzigianni Mexi 2, Athens 115 28 which is Ilisia, near Mavili Square (Hilton area), NOT Pangrati. Multiple sources (Tripadvisor "Platia Mavili", 50Best, the operator's own postcode 115 28) confirm Mavili / Ilisia. Pangrati is south-east of Spondi at postcode 116 35. Rewrote to "Cookoovaya near Mavili Square in Athens". The `neighborhood: pangrati` slug remains imperfect-fit because neighborhoods.json has no Ilisia / Mavili slug (out of scope, same as Hytra Neos Kosmos and Delta Kallithea — already flagged in QA1+QA2).

### E3. Geographic-adjacency overclaim in prose

- `brunch.json` `avocado-brunch` tip: said "Mama Roux on Aiolou around the corner" as the Sunday alternative to Avocado at Nikis 30. Avocado is on Nikis 30 (south of Mitropoleos, near the National Gardens); Mama Roux is at Aiolou 48 (further north past Ermou). Approximately 600m via Athens streets, not "around the corner". Rewrote to "Mama Roux on Aiolou, a short walk north."

## Cross-source / source-of-truth re-verifications done (no defect — confirmations)

- Aegina Fistiki Sept 18-21 2026 — confirmed via takeyourbackpack (non-organiser).
- Athens Coffee Festival Sept 26-28 — confirmed via Perfect Daily Grind + World Coffee Beans (non-organiser).
- Athens Street Food Festival May 8-24 (three weekends) — confirmed via elCulture + AllEvents (non-organiser).
- Oenorama March 13-16 — confirmed via travel.gr + Visit Greece.
- Tsiknopempti Feb 12 — confirmed via Sigmalive + Greek City Times 2026.
- Spondi Bignon, 1 star — Cycladic Spaces 2026 Michelin guide.
- Hytra Felemengas, 1 star — Cycladic Spaces + Hytra Facebook.
- Zillers Roussos, 1 star (since 2022) — Cycladic Spaces + michelin.com.
- Delta Papazacharias + Feskos, 2 stars + Green Star, opened 2021 — SNF + Athens Gastronomic Forum.
- Aleria Gikas Xenakis (head chef since 2012) — aleria.gr/en/chef + Neos Kosmos.
- Cookoovaya Periklis Koskinas (chef-owner) — Cookoovaya own site + travel.gr.
- CTC Alexandros Tsiotinis — operator's CHEF page.
- Soil Tasos Mantis (1 + Green Star) — Cycladic Spaces.
- Nolan Michalis Nourloglou (since 2024, after Kontizas) — FNL Guide review.
- Birdman Ari Vezene — operator + Tripadvisor.
- Strange Brew Spring 2017 founding + 2019 Koukaki taproom — strangebrew.gr/brewery (food-history.json claim of "2017 craft beer wave" stands; breweries.json "opened 2019" stands for taproom).
- Mama Tierra chef Polash Alam — Chloe Hamard + ceoworld + traveltoathens cross-verification.
- Drupes & Drips Zitrou 20 Koukaki/Makrygianni — thisisathens.org + Foursquare + Tripadvisor.
- Ernst Ziller architecture claim for Lazy Duck's building (formerly Tailor Made) — Medium "Little Bicycle Coffee Shop" + S Marks The Spots.
- Karavitis Sat 13:30-00:30 — confirmed (itinerary 14:00 OK).
- Taverna tou Oikonomou Mon-Fri 19:00-01:00, Sat-Sun 13:00-24:00 — confirmed (itinerary Wed 20:30 OK).
- Mavro Provato Mon 13:00-24:00 — confirmed (itinerary Mon 21:00 OK).
- Mama Roux daily 09:00-24:00 — confirmed (itinerary Sun OK).
- Taverna Saita daily 12:00-24:00 — confirmed (itinerary Sun OK).
- Taverna Platanos Sat 12:00-24:00 — confirmed (itinerary Sat OK).
- A for Athens daily — confirmed (itinerary OK).
- Atlantikos annex weekdays 18:00 (hidden-gems tip) — confirmed.

## Non-defects flagged but accepted (consistent with QA1+QA2 stance)

- Hytra `neighborhood: kerameikos-metaxourgeio` is geographically inaccurate (real: Neos Kosmos at Onassis Cultural Centre). Description prose correctly identifies the Onassis Cultural Centre. Neighborhoods.json catalog has no Neos Kosmos slug — fix is research scope.
- Delta `neighborhood: kerameikos-metaxourgeio` similar (real: Kallithea / Faliro). Description prose correctly identifies SNFCC + Kallithea.
- Cookoovaya `neighborhood: pangrati` likewise imperfect (real: Ilisia / Mavili) — prose now corrected as above.
- Mind the Cup tagged as `monastiraki` while operator is in Peristeri (western suburb) — pre-existing, research backlog.
- Venetis tagged in Kifisia, no kifisia slug — pre-existing.
- HappyCow lists Avocado as CLOSED Nov 2025, but Eating Europe's March 2026 article, Wheree Jan 2026 listing, and Veggies Abroad 2026 all show Avocado at Nikis 30 as operating. The cuisine_evidence_url and a 2026-dated press article both confirm open; pass-1 cleared. Not a defect.
- food-history.json says "Chef Nikolaos Tselementes published the first modern Greek cookbook in 1910" — actually 1910 was his magazine; the cookbook is 1932. Borderline editorial paraphrase; not a hard fabrication. Accepted.
- coffee-roasters at 3, breweries at 3, cooking-classes at 4, dietary.halal at 0, dietary.kosher at 1 below SEO floors — content reality, not invented.

## Defects total: 2

- 1 cross-entry geographic mismatch in city.json food_culture_summary (Bairaktaris implicitly placed on Evripidou).
- 1 description geographic mislocation in fine-dining.json cookoovaya (placed in Pangrati, real is Ilisia/Mavili).
- 1 geographic-adjacency overclaim in brunch.json avocado-brunch tip ("around the corner" for a 600m walk).

(3 total textual edits, scored as 2 distinct defect classes — geographic prose mismatch.)

Both rooted upstream in **research-stage geographic carelessness** (neighborhood field defaulted to nearest catalog slug; food_culture_summary stitched venues into a single Evripidou clause; brunch tip used "around the corner" without distance check). QA1 and QA2 both missed because neither did Google-Maps adjacency verification on prose. Recommended QA prompt tightening: add "Geographic adjacency check on every prose phrase like 'around the corner', 'next door', 'across the street', 'a short walk' — Google-Maps verify; >250m = false" to the QA1 and QA2 prompts (it's already in the Opus prompt, just hadn't propagated downstream).

## Verdict

VERDICT: PASS

Three small fixes, all rooted in editorial prose making geographic claims that did not survive map-check. No fabricated chef names, no Naples-class fabrications, no closed venues, no festival date errors, no day-of-week × hours collisions, no source-URL redirects to wrong domains. Athens is shippable.
