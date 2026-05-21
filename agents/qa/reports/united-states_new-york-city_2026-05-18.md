# QA report — New York City (round 3)

Date: 2026-05-18
Agent: TableJourney QA agent (round 3 adversarial)

## Summary

Round 3 found 20 defects, materially more than the round 2 trajectory (5 defects) predicted. Defect mix is dominated by venue closures the validator missed (10 entities) and address hallucinations of the exact pattern called out as a P0 defect class in PROMPT.md (8 entities, same building number with wrong street name). Two further venue-state defects: one venue relocated, one hours/operating model claim is now wrong. K=20 triggers a recommendation for round 4 per the K>=5 rule.

## Stage 1: 100% entity re-verification

- Total entities across 24 topic JSONs (pre-round-3): 235
- WebSearch performed on: 235 (100%, every entity touched)
- Defects found: 20
- Action: 12 removals, 8 address fixes (no replacements fabricated)

### Closed-venue defects (10)

These shipped to JSON as currently operating; WebSearch confirmed closure via venue's own site, Yelp, Foursquare, NYC Tourism, or direct news.

| Slug | Topic | Closure evidence |
|---|---|---|
| `transmitter-brewing` | breweries | Moved out of 53-02 11th St LIC in 2019; only Brooklyn Navy Yard taproom remains. The Yelp page for the LIC address is dead. |
| `bronx-brewery` | breweries | Permanently closed at 856 E 136th St on Feb 9, 2026 (the East Village location at 64 2nd Ave still operates but is a separate entity). |
| `she-wolf-bakery` | bakeries | Moved entire operation to Brooklyn Navy Yard in 2024; no retail storefront at 63 Newel St. Sells through greenmarkets and wholesale only. |
| `regalia-coffee` | coffee-roasters | Address `2017 Bleecker Street, Queens` is fabricated. Real roastery at LIC (39-26 24th St) is by appointment only, no retail cafe. Roasting Collective Yelp marked CLOSED. |
| `city-of-saints` | coffee-roasters | JSON address `139 Chrystie Street` not in their location list. East Village location (79 E 10th St) marked CLOSED on Yelp April 2026. Only retail cafe is in Brooklyn (297 Meserole St). |
| `two-hands` | cafes | 164 Mott Street CLOSED per Yelp May 2026. Brand continues at 251 Church St (Tribeca). |
| `bluestone-lane` | cafes | 55 Greenwich Avenue CLOSED per Yelp December 2025 + Foursquare "Now Closed". |
| `totto-ramen` | casual-dining | 366 W 52nd St CLOSED since 2020, replaced by Toribro Ramen. Yelp marked CLOSED Feb 2026. |
| `the-meatball-shop` | casual-dining | 84 Stanton Street CLOSED per Yelp April 2026 + NYC Tourism "Out of Business". |
| `champs-diner` | dietary/vegan | CLOSED January 2023 after 12 years. Successor "Ro's Diner" at the same Meserole St address also closed October 6, 2024. |

### Operating-state / hours defects (2)

| Slug | Topic | Issue |
|---|---|---|
| `fresco-tortillas` (Tehuitzingo) | street-food | Yelp + Foursquare both marked CLOSED. The venue's own gotoeat.net is templated and may be auto-maintained. Conservative removal per "when in doubt, remove" rule. |
| `wo-hop` | late-night | JSON claims "Daily until 05:00, the canonical post-bar Chinese". Wo Hop expanded to street-level in 2025 and reduced hours to 10pm daily. No longer a late-night entry. |

### Address hallucination defects (8)

This is the exact pattern PROMPT.md flags as P0 — agent kept a plausible building number but invented the street name or kept the right name with the wrong street.

| Slug | Topic | JSON address (wrong) | Real address (fixed) |
|---|---|---|---|
| `variety-coffee` | coffee-roasters | `146 Wythe Avenue, Brooklyn` williamsburg | `146 Wyckoff Avenue, Brooklyn 11237` bushwick (different street, also wrong borough). 9 Variety locations verified via their site; no Wythe Avenue location exists. |
| `king-souvlaki-of-astoria` | street-food | `31-12 30th Avenue, Queens 11102` | `31st Street and 31st Avenue, Astoria 11106` (different cross-street AND zip) |
| `adels-famous-halal` | street-food | `West 53rd Street & 6th Avenue 10019` | `1221 6th Avenue 10020` (SW corner of 49th & 6th). 53rd & 6th is The Halal Guys territory; Adel's is 4 blocks south. |
| `biang-biang` (Xi'an Famous Foods) | street-food | `111 St Marks Place 10009` | `45 Bayard Street 10013` (Chinatown). 81 St Marks closed in 2020; 111 St Marks is fabricated. |
| `arepa-lady` | casual-dining | `77-02 Roosevelt Avenue 11372` | `77-17 37th Avenue 11372` (moved March 2024 for a development; previous address vacated). |
| `miss-lily-s` | casual-dining | `132 West Houston Street 10012` (closed; replaced by Song E Napule) | `109 Avenue A 10009` (active East Village location). |
| `rosella-wine-bar` | wine-bars | `137 First Avenue 10003` | `137 Avenue A 10009` (Avenue A and First Avenue are parallel; classic hallucination). |
| `etc-steakhouse` | dietary/kosher | `1409 Queen Anne Road, Teaneck NJ` | `1409 Palisade Avenue, Teaneck NJ 07666` (same building number, fabricated street). |

## Stage 1 per-topic breakdown

Walked in the prescribed order (largest first):

- restaurants (23): 23 verified, 0 removed. All Michelin-tier and indie names check out at listed addresses.
- casual-dining (21 -> 19): 19 verified, 2 removed (totto-ramen, the-meatball-shop), 2 address-fixed (arepa-lady, miss-lily-s).
- fine-dining (15): 15 verified, 0 removed. (Atomix 2-star, Per Se 3-star, Le Bernardin 3-star, EMP 3-star, Masa 3-star, Atera 2-star, Daniel 2-star, Sushi Noz 2-star, Cote 2-star, Casa Mono 1-star, Rezdora 1-star, Kochi 1-star, Frenchette OpenTable Icon 2025/2026, Jungsik 3-star, Tatiana Michelin-listed all current.)
- cafes (12 -> 10): 10 verified, 2 removed (two-hands, bluestone-lane).
- bars (16): 16 verified, 0 removed. Amor y Amargo confirmed reopened at original 443 E 6th in Jan 2025.
- brunch (7): 7 verified, 0 removed.
- hidden-gems (4): 4 verified, 0 removed (note: 3 slug/name mismatches persist from pass 1, all cosmetic).
- bakeries (13 -> 12): 12 verified, 1 removed (she-wolf-bakery).
- breweries (6 -> 4): 4 verified, 2 removed (transmitter-brewing, bronx-brewery). NEW FLOOR FLAG: breweries now at 4 entries, below the 5-15 floor in food-research PROMPT. Backfill recommended.
- wine-bars (9): 9 verified, 0 removed, 1 address-fixed (rosella-wine-bar).
- speakeasies: file not present (NYC has no separate speakeasies file).
- late-night (7 -> 6): 6 verified, 1 removed (wo-hop). Veselka 24/7 description verified accurate per April 17 2026 return to 24-hour weekend service.
- street-food (12 -> 11): 11 verified, 1 removed (fresco-tortillas/Tehuitzingo), 3 address-fixed (king-souvlaki-of-astoria, adels-famous-halal, biang-biang/Xi'an Famous Foods).
- food-halls: file not present.
- markets (8): 8 verified, 0 removed.
- coffee-roasters (8 -> 6): 6 verified, 2 removed (regalia-coffee, city-of-saints), 1 address-fixed (variety-coffee). NEW FLOOR FLAG: coffee-roasters at 6 entries, within 5-12 floor but near low end. Note that stumptown-coffee-roasters here duplicates the cafes.json entry (cosmetic).
- neighborhoods (16): 16 listed neighborhoods verified as real NYC neighborhoods.
- festivals (7): 7 verified. Recurrence checks: NYCWFF Oct 15-19 2025 confirmed (JSON Oct 14-18 close enough, 2026 dates will shift); San Gennaro Sept 11-21 2025 + Sept 17-27 2026 confirmed (JSON Sept 11-21 matches 2025); Smorgasburg every Saturday April-October confirmed (2026 season started April 4); Queens Night Market 2026 starts April 18; Ninth Avenue Food Festival Saturday May 16 + Sunday May 17 2026 (JSON May 17-18 matches 2025 - acceptable). Taste of Times Square September 8 2025 month-matches JSON. Burger Bash within NYCWFF October confirmed.
- cooking-classes (3): 3 verified (ICE 225 Liberty St correct; La Scuola at Eataly Flatiron 200 5th Ave correct; League of Kitchens private-homes model correct).
- food-tours (3): 3 verified (Joe DiStefano's Chopsticks and Marrow Flushing tour real; Scott's Pizza Tours running with documented routes; Harlem Heritage Tours running with Sylvia's/Amy Ruth's/Charles Pan Fried route - verified the route matches operator's documented tour).
- itineraries (3): 3 verified. The pass-2 Absolute Bagels regression is resolved (Russ & Daughters substituted on day 1; route still walkable).
- dietary/vegan (4 -> 3): 3 verified, 1 removed (champs-diner).
- dietary/vegetarian (3): 3 verified (Dirt Candy Michelin-listed, Hangawi Michelin-listed, Saravanaa Bhavan Lexington Ave open).
- dietary/gluten_free (2): 2 verified (Senza Gluten, Noglu).
- dietary/halal (2): 2 verified (The Halal Guys 53rd/6th, Kabab King 73-01 37th Rd).
- dietary/kosher (2): 2 verified, 1 address-fixed (etc-steakhouse). 2nd Ave Deli verified.

## Stage 2: round-3 convergence call

- This is round 3. K = 20.
- Recommendation: **round 4** required (K >= 5 trigger).
- Rationale: the validator pass-2 explicitly verified Absolute Bagels was the only material regression. Round 3's 100% sweep found 20 more problems the validator missed. The defect rate (20 / 235 = 8.5%) is consistent with the session 18 ~10% baseline that motivated the QA stage in the first place. Pass-2's report under-counted by an order of magnitude. We are not yet at convergence.
- Round 4 should re-verify the FIXED entries (the new addresses I wrote for 8 venues), independently check the remaining 215 unchanged entries for any I missed (especially address hallucinations), and confirm no further closed/relocated venues slip through.

## Stage 3: cross-city correctness

- `scripts/check_external_urls.py --country united-states --city new-york-city`: 4 / 144 broken, all 401/403 anti-bot (alibabarestaurant.com 403, etcsteakhouse.com 403, unsplash photo URL 401, nanxiangxiaolongbao.com 403). Per PROMPT.md these are acceptable. No real broken URLs.
- `scripts/audit_live.py | tail -10`: 0 errors site-wide (1328 pages crawled, 0 errors, 94 length-cap warnings on meta descriptions). NYC-scoped broken-extra-links: 4 (`/neighborhood/new-york-city/corona/`, `/elmhurst/`, `/governors-island/`, `/sunset-park/`). These are neighborhood cross-cut pages referenced from venue entries but not generated — a pre-existing issue unrelated to round 3 changes.
- Breadcrumb / state-page / country-hub spot-checks: pass. `/united-states/`, `/united-states/new-york/`, `/united-states/new-york-city/` all resolved during audit_live crawl.

## Defects removed (atomic .tmp + os.replace per file)

| Slug | Topic | Reason | Action |
|---|---|---|---|
| transmitter-brewing | breweries | Moved out of LIC 2019; only BK Navy Yard taproom | REMOVE |
| bronx-brewery | breweries | Permanently closed Feb 9 2026 | REMOVE |
| she-wolf-bakery | bakeries | Moved to BK Navy Yard 2024; no retail at Newel St | REMOVE |
| regalia-coffee | coffee-roasters | Address fabricated; no public retail | REMOVE |
| city-of-saints | coffee-roasters | 139 Chrystie Street fabricated; East Village closed | REMOVE |
| two-hands | cafes | 164 Mott Street CLOSED (Yelp) | REMOVE |
| bluestone-lane | cafes | 55 Greenwich Avenue CLOSED (Yelp + Foursquare) | REMOVE |
| totto-ramen | casual-dining | CLOSED since 2020 | REMOVE |
| the-meatball-shop | casual-dining | 84 Stanton St CLOSED (Yelp + NYC Tourism) | REMOVE |
| fresco-tortillas (Tehuitzingo) | street-food | CLOSED per Yelp + Foursquare | REMOVE |
| wo-hop | late-night | No longer late-night (closes 10pm) | REMOVE from late-night topic |
| champs-diner | dietary/vegan | CLOSED Jan 2023, successor closed Oct 2024 | REMOVE |

## Address fixes (atomic .tmp + os.replace)

| Slug | Topic | From | To |
|---|---|---|---|
| variety-coffee | coffee-roasters | 146 Wythe Avenue, williamsburg | 146 Wyckoff Avenue 11237, bushwick |
| king-souvlaki-of-astoria | street-food | 31-12 30th Avenue 11102 | 31st Street and 31st Avenue, Astoria 11106 |
| adels-famous-halal | street-food | West 53rd Street & 6th Avenue 10019 | 1221 6th Avenue 10020 |
| biang-biang | street-food | 111 St Marks Place 10009 | 45 Bayard Street 10013, chinatown |
| arepa-lady | casual-dining | 77-02 Roosevelt Avenue 11372 | 77-17 37th Avenue 11372 |
| miss-lily-s | casual-dining | 132 West Houston Street 10012, soho | 109 Avenue A 10009, east-village |
| rosella-wine-bar | wine-bars | 137 First Avenue 10003 | 137 Avenue A 10009 |
| etc-steakhouse | dietary/kosher | 1409 Queen Anne Road, Teaneck NJ | 1409 Palisade Avenue, Teaneck NJ 07666 |

## Below-floor topics after QA

- breweries: 4 entries (target 5-15). Below floor after removing transmitter and bronx. Recommend research agent backfill with at least 1-3 verified breweries (e.g. Other Half Domino Park, Finback LIC, Greenpoint Beer & Ale, Industry City breweries) in round 4 / next research pass.
- dietary/vegan: 3 entries (target 3+ per diet category). At floor; no backfill required but tight.
- food-tours (3), cooking-classes (3), dietary/vegetarian (3), dietary/gluten_free (2), dietary/halal (2), dietary/kosher (2), hidden-gems (4) all remain at the same below-target counts as before round 3. None made worse by round 3 actions; these are pre-existing thin topics.

## Notes the round-4 agent should pay attention to

- The 8 address-hallucination defects all followed the same pattern: same building number, fabricated street name. The food-research agent appears to be assembling addresses from partial training memory rather than reading off the venue's own current page. This is a recurring P0 pattern.
- Two venue-name/slug mismatches in hidden-gems persist (cosmetic per pass-2): `ducks-eatery` -> "Wu's Wonton King" (also duplicates restaurants.json); `barneys-grain-and-grocery` -> "Court Street Grocers". Slugs are URL-stable assets per CLAUDE.md so they don't get retroactively renamed, but the entries are otherwise OK.
- The Tehuitzingo case is borderline (own site loading, Yelp+Foursquare closed). I removed conservatively; if the next pass finds it actually operational, re-add at 695 10th Avenue.
- Round 4 should recheck my 8 fixed addresses against the venue's current website to make sure I didn't introduce a new error.

## Verdict

VERDICT: NEEDS_FIXES
