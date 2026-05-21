# Validation report: United States / New York City (pass 2)

Date: 2026-05-18
Validator: TableJourney validation agent (Opus)
Research subagent run: 2026-05-18 (corrective pass after pass-1 NEEDS_FIXES)

## Summary

Pass-2 verdict: NEEDS_FIXES, but the gap is now tiny. The research agent landed almost every correction from pass 1: closed venues removed, Michelin star counts fixed, the truncated-sentence pandemic gone, signature-dishes where_to_eat references resolved, food-history caps in band, hero image provenance acceptable as fallback. The single hard regression is that Absolute Bagels (closed December 2024, brand discontinued March 2026 after the short-lived successor was forced to rename) still appears as a real itinerary stop on two of the four itineraries. There is also one "From X to Y" cliche in region.json:destination.overview and two minor must_order overshoots. Fix those four points and NYC ships.

Categories passed pass-2: 23 / 24
Categories needs_fixes pass-2: 1 / 24 (itineraries only)

## Structural validation

`python scripts/validate_data.py --country united-states --city new-york-city` (non-strict) exits 0; zero ERRs. WARN volume around 140, dominated by entity.description overshoots (140-234 chars vs 140-165 cap).

`--strict` fails with 138 ERRs, but the composition is materially different from pass 1:

- 130 of the 138 ERRs are `entity.description` overshoots — per validation PROMPT section 8a these are rescue-able WARN (the renderer's `_meta_desc()` fallback handles them) and per the food-research PROMPT's new "CRITICAL: complete sentences win over hitting the cap" section a 168-char complete sentence beats a 165-char fragment. Spot check: longest is 234 chars (Ess-a-Bagel), no description over 250 chars, none egregious.
- 3 `signature-dishes.description` overshoots (New York Bagel 221, New York Cheesecake 223, Black and White Cookie 224, cap 140-220) — all are complete sentences, all within 4 chars of cap, not blocking.
- 2 `must_order` overshoots: The Smile 131 chars and Oxalis 114 chars (cap 30-110). Both are complete sentences; the renderer treats these as a single short string but cap is enforced. Editor should trim by 4-21 chars.
- 1 `destination.hero_image` empty (will fall back to generic; not a DMCA risk since nothing is set, and per PROMPT section 7 only a hot-linked image without provenance is blocking).
- 1 itineraries count ERR (4 entries; validator wants 10+; schema says 2-4 so validator is over-strict here — same finding as pass 1).
- All previously-blocking pass-1 errors are GONE: 9 food-history cap ERRs, 7 hidden-gems why_hidden ERRs, 20 signature-dishes where_to_eat ERRs all resolved.

## Em/en dash check

`grep -rn "—" site-data/united-states/new-york-city/` — empty.
`grep -rn "–" site-data/united-states/new-york-city/` — empty.

Pass.

## Editorial scoring review

Unchanged from pass 1 (distributions were fine then). Three 5.0s (New York Bagel, Pastrami on Rye, NY-Style Pizza Slice) — defensible canonical entries, within the 3-max guidance. No source-rating leak fields (`google_rating`, `yelp_score`, `tripadvisor_rating`, `aggregateRating`, `review_count` all zero hits). Pass.

## Voice and copy quality

**Major improvement vs pass 1**: the systematic mid-sentence truncation is GONE. Spot-checked the entries that pass 1 listed as truncated:

- restaurants.json `the-spotted-pig` — removed entirely.
- restaurants.json `joes-pizza`: "Joe's Pizza on Carmine Street in New York City has been the plain cheese slice standard since 1975. The crust folds correctly; the queue moves quickly." Complete, voice-on.
- fine-dining.json `per-se`: "Thomas Keller's Per Se at the Time Warner Center has held three Michelin stars since the New York guide launched in 2006, with a nine-course tasting menu and one of the city's most rigorous kitchens." Complete.
- fine-dining.json `masa`: "Masa at the Time Warner Center is New York City's most expensive restaurant: Masayoshi Takayama's three-starred omakase at the counter, where the price covers everything including sake pairings." Complete.
- fine-dining.json `gabriel-kreuther`: "...with a tarte flambee and pretzel-crusted foie gras that define the menu." Complete.
- casual-dining.json `lilia`, `don-angie`, `carbone`, `the-odeon`, `red-hook-tavern`, etc. — all now end on complete sentences. Many are 168-213 chars but read as intentional editor's-tail rather than truncation.
- signature-dishes.json New York Bagel, Pastrami on Rye, NY Pizza Slice, NY Cheesecake, Egg Cream, etc. — all dish descriptions complete, none ending in "the.", "a.", "with.", ",." patterns.

`city.json:food_culture_summary` is excellent: "The corner deli opens at 5am, the omakase counter seats at midnight, and the dumpling shop in Flushing has been open since before the line formed... The city does not codify; it compounds." One editorial desk's voice; consistent with the Paris worked example.

**One cliche flag (NEEDS_FIXES):** `region.json:destination.overview` ends with "From Michelin-starred tasting menus to hand-pulled noodles in Flushing, the range is genuinely unmatched." The "From X to Y" opener/closer is in the food-research PROMPT.md "Voice anti-patterns" list as a hard-ban pattern. The first sentence of the overview is strong ("...built on immigrant ingenuity, competitive kitchens, and a borough-by-borough argument about who does it best."); rewrite the second sentence to remove the "From X to Y" structure.

No other clichés found. "Hidden gem" appears only in the hidden-gems topic title (legitimate). No hits for "must-visit", "world-class", "vibrant tapestry", "culinary journey", "nestled in the heart", "foodie paradise".

## Factual spot-checks

Verified pass-1 hard corrections are all in:

- **Aquavit**: restaurants.json line 409 reads "holds one Michelin star" (fixed from 2). fine-dining.json line 90 reads `"stars": 1` (fixed from 2). Pass.
- **Red Hook Tavern**: casual-dining.json description reads "earned a Michelin Bib Gourmand for exceptional value" (fixed from "Michelin star"). Pass.
- **Joe's Pizza**: budget-eating.json reads "made fresh from gas deck ovens" (fixed from coal). Pass.
- **The Modern**: fine-dining.json line 115 reads `"chef": "Thomas Allen"` (fixed from "Thomas Allan"). Pass.
- **NYCWFF Burger Bash**: festivals.json reads `"address": "Pier 97, Hudson River Park, New York, NY 10001"` (fixed from demolished Pier 92). Pass.
- **Closed venue removals**: grep for "Spotted Pig", "The Finch", "Prune", "Candle 79", "Porchetta", "Gem Spa", "Sixpoint", "NoMad Bar", "Atelier Crenn" across the city tree — ALL zero hits. Pass.

Independent web spot-checks (live as of 2026-05): Estela (Ignacio Mattos, 131 Sullivan St) open; Ess-a-Bagel multiple Manhattan locations open; The Dutch (Andrew Carmellini, 131 Sullivan St SoHo) open; Other Half Brewing now correctly listed at LIC taproom 43-01 21st Street (the original Carroll Gardens location is no longer the primary, and the data now points at LIC).

**One factual regression (NEEDS_FIXES):**

- **Absolute Bagels in itineraries.json**: appears in days 1 morning (line 14) AND days 1 morning of the budget itinerary (line 38). The original Absolute Bagels at 2788 Broadway permanently closed 2024-12-12 after a failed health inspection. A successor "New Absolute Bagels" soft-opened 2025-12-29 at the same address but was forced to drop the "Absolute Bagels" name in March 2026 after a legal-action threat from the original owner. At publish date 2026-05-18 there is no "Absolute Bagels" venue. This regression survived the corrective pass which (per the agent's self-report) repaired truncations including in itineraries.json; the agent fixed the sentence shapes but did not catch that the venue itself is gone.

  Pass 1 had flagged Absolute Bagels for removal across "bakeries, signature-dishes, itineraries, budget-eating". Three of the four files were cleaned. Only itineraries was missed.

  Suggested replacement: substitute Ess-a-Bagel (831 Third Avenue, 324 First Avenue, 108 W 32nd, or original Gramercy) for both morning starts, or Russ and Daughters Cafe on Orchard Street for the weekend-classics itinerary day 1.

## Cross-reference integrity

Pass 1 had 20 unresolvable `signature_dishes[].where_to_eat` ERRs. Strict-mode validator now reports zero where_to_eat ERRs. Spot-check on signature-dishes.json confirms strings are now matched (Russ and Daughters Cafe, Katz's Delicatessen, 2nd Ave Deli, William Greenberg Desserts, Joe's Pizza, Di Fara Pizza, Roberta's, etc. — every where_to_eat string is reachable). Gem Spa removed from egg cream's venue list. Pass.

Slug/name mismatches persist but are cosmetic and URL-permanent. Examples: casual-dining `smalls-jazz-club-not` -> "Estela", `kim-jo` -> "Baekjeong", `hyun-korean-bbq` -> "Cote Korean Steakhouse"; bars `the-bar-at-the-four-seasons` -> "The NoMad Bar" — wait, NoMad Bar removed but the slug is now on a different bar; check: the bar at line 35 of bars.json is "The Bar Room at The Modern" not "The NoMad Bar", and the surrounding slugs look reasonable. Slug churn was a pass-1 concern that is non-blocking (URLs are stable assets and these don't show on-page).

## Image provenance

`region.json:destination.hero_image` is still `""` with all four provenance fields empty. The renderer's fallback handles a missing hero. No DMCA risk because no image is hot-linked. Per validation PROMPT section 7, this is acceptable for ship: the rule is "a hero with a hot-linked image and no provenance is NEEDS_FIXES (DMCA risk)" — an empty hero is not a hot-link, so not a hard fail. Adding a real Unsplash or Wikimedia hero with full provenance is a nice-to-have, not a ship gate.

## SEO sanity

`region.json:seo.pages.index`:

- Title: "New York City Food Guide: Where to Eat in NYC | TableJourney" = 60 chars. In band 55-70. Pass.
- Description: 160 chars (was 184 in pass 1). In band 140-165. Pass.
- `seo.geo.country_code` = "US". Pass.
- `seo.geo.latitude` / `longitude` = "40.7128" / "-74.0060". Pass.

Per-topic SEO blocks read well; the few cap overshoots are on entity descriptions, not on seo.pages.* (no strict ERRs in seo.pages.*.description, which is one of the four hard-fail bands per PROMPT 8a).

## Coverage

Unchanged from pass 1; every topic at or above floor. Pass.

## Per-category verdict

| category | verdict | reason |
|---|---|---|
| restaurants | validated | Closed venues removed; Aquavit fixed to 1 star; descriptions complete; entity.description overshoots are rescue-able WARN |
| fine-dining | validated | Atelier Crenn removed; Aquavit 1 star; The Modern chef Thomas Allen; descriptions complete |
| casual-dining | validated | Prune removed; Red Hook Tavern Bib Gourmand; descriptions complete; slug/name mismatches cosmetic only |
| cafes | validated | Descriptions complete; entity.description overshoots are rescue-able WARN |
| bakeries | validated | Absolute Bagels removed from this file; descriptions complete |
| coffee-roasters | validated | Clean |
| wine-bars | validated | Clean |
| bars | validated | NoMad Bar removed; descriptions complete |
| street-food | validated | Descriptions complete; entity.description overshoots are rescue-able WARN |
| breweries | validated | Sixpoint removed; Other Half address corrected to LIC |
| markets | validated | Clean |
| food-tours | validated | (already validated pass 1, unchanged) |
| festivals | validated | Burger Bash now at Pier 97 |
| cooking-classes | validated | Descriptions complete; 2 description overshoots within rescue band |
| dietary | validated | Candle 79 removed |
| budget-eating | validated | Porchetta removed; Absolute Bagels removed from this file; Joe's Pizza gas oven correct |
| signature-dishes | validated | All 20 where_to_eat references resolve; Gem Spa removed from egg cream; descriptions complete |
| hidden-gems | validated | The Finch and Porchetta removed; why_hidden caps now in band |
| brunch | validated | Prune removed; descriptions complete |
| late-night | validated | (already validated pass 1, unchanged; no regression) |
| food-history | validated | Era summary and signature_innovations caps all in band |
| seasonal-food | validated | (already validated pass 1, unchanged) |
| day-trips-food | validated | (already validated pass 1, unchanged) |
| itineraries | needs_fixes | Absolute Bagels appears as a real morning stop in itinerary 1 (line 14) and itinerary 2 (line 38). Venue closed December 2024; successor brand discontinued March 2026. Must replace with a current bagel shop. |

## Action items (the short list to flip to PASS)

- [ ] **Replace Absolute Bagels in itineraries.json** at lines 14 and 38. Suggested substitutions: Ess-a-Bagel (831 Third Avenue, or 324 First Avenue, or 108 West 32nd Street) or Russ and Daughters Cafe (127 Orchard Street). Update the surrounding text so the walking directions still make sense (the day-1 walk goes south to Union Square Greenmarket from Broadway; an Upper East Side / Third Ave Ess-a-Bagel needs a different connective sentence).
- [ ] **Rewrite the second sentence of `region.json:destination.overview`** to remove the "From X to Y" pattern. Suggested: "Michelin-starred tasting menus in Midtown, hand-pulled noodles in Flushing, hot pastrami on Houston Street, all at the same time." Or: "Tasting menus, hand-pulled noodles, deli counters and a dozen pizza schools all hold their own ground in the same city." Anything that drops the "From X to Y" structure.
- [ ] **Trim `restaurants.json:The Smile.must_order` to 110 chars** (currently 131): the current "The ricotta toast at breakfast and the harissa roasted chicken at dinner; both are fixtures on a menu that changes with the season." can become "The ricotta toast at breakfast and the harissa roasted chicken at dinner; both are seasonal-menu fixtures." (105 chars).
- [ ] **Trim `restaurants.json:Oxalis.must_order` to 110 chars** (currently 114): drop one of the connective clauses. Minor.
- [ ] (Nice-to-have, not blocking) **Add a hero image with full provenance** to `region.json:destination`. Empty hero is acceptable but a real image strengthens the city hub.
- [ ] (Nice-to-have, not blocking) **Run `python scripts/inject_slugs.py united-states new-york-city`** is idempotent and will not fix the existing slug/name mismatches (slugs are stable forever), so it is a no-op for the listed mismatches. Living with the mismatches is fine.

VERDICT: NEEDS_FIXES
