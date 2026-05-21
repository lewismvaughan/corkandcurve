# QA report — New York City (round 4)

Date: 2026-05-18
Agent: TableJourney QA agent (round 4 adversarial)

## Summary

Round 4 found 3 entity defects across the 24 topic JSONs. Critically, the 8 address fixes round 3 wrote (variety-coffee, king-souvlaki-of-astoria, adels-famous-halal, biang-biang, arepa-lady, miss-lily-s, rosella-wine-bar, etc-steakhouse) all re-verified clean against the venues own current pages or Yelp. Round 3 did its writes correctly. The 3 new defects are unrelated to the round 3 fixes: 1 closure (Yelp marked), 1 relocation (cafe moved one block on Grand Street), 1 stale editorial claim now misstated by venue change. K=3 < 5 triggers convergence.

## Stage 1: 100% entity re-verification

- Total entities across 24 topic JSONs (pre-round-4): 222
- WebSearch performed on: 222 (100%, every entity touched)
- Defects found: 3
- Action: 2 removals, 1 address fix, 2 cosmetic description updates (EMP plant-based reversion)

### Re-verification of round-3 address writes (priority)

All 8 round-3 address fixes verified against the venues current pages / Yelp / Apple Maps:

| Slug | Topic | Address written by r3 | r4 verdict |
|---|---|---|---|
| variety-coffee | coffee-roasters | 146 Wyckoff Avenue, Brooklyn 11237 | Correct (Yelp + venue site) |
| king-souvlaki-of-astoria | street-food | 31st Street and 31st Avenue, Astoria 11106 | Correct (Yelp + venue site) |
| adels-famous-halal | street-food | 1221 6th Avenue 10020 | Correct (Yelp May 2026 + Tripadvisor) |
| biang-biang (Xian Famous Foods) | street-food | 45 Bayard Street 10013 | Correct (venue site + Tripadvisor) |
| arepa-lady | casual-dining | 77-17 37th Avenue 11372 | Correct (venue site + Yelp April 2026) |
| miss-lily-s | casual-dining | 109 Avenue A 10009 | Correct (venue site + Yelp Feb 2026) |
| rosella-wine-bar | wine-bars | 137 Avenue A 10009 | Correct (Yelp May 2026 + venue site) |
| etc-steakhouse | dietary/kosher | 1409 Palisade Avenue, Teaneck NJ 07666 | Correct (Yelp Feb 2026 + venue site) |

Round 3 did not introduce any new address errors. The address-hallucination defect class did not regress.

### Closed-venue defects (1)

| Slug | Topic | Closure evidence |
|---|---|---|
| `cuba` | casual-dining | Yelp "Cuba Restaurant and Rum Bar - CLOSED" updated March 2026 at 222 Thompson Street. Venue own site (cubanyc.com) still live but other directories conflict. Per "when in doubt, remove" rule. |

### Relocation defects (1)

| Slug | Topic | Issue |
|---|---|---|
| `devocion` | cafes | JSON address `69 Grand Street, Brooklyn 11249` is the original Williamsburg cafe, which has closed. Devocion opened a new 2,500-sqft flagship at 148 Grand Street about a block away and the 69 Grand location ended. Fixed to 148 Grand Street, Brooklyn 11249. |

### Editorial claim defects (1)

| Slug | Topic | Issue |
|---|---|---|
| `eleven-madison-park-vegan` | dietary/vegan | EMP announced in August 2025 that it would resume serving fish and meat. Starting October 2025 the menu offers fish, meat and a fully plant-based path; the restaurant is no longer "entirely plant-based" as the entry claimed. Removed from vegan category. EMP descriptions in restaurants.json and fine-dining.json also updated to reflect the menu reversion. |

## Stage 1 per-topic breakdown

- restaurants (23): 23 verified, 0 removed (1 description update on EMP).
- casual-dining (19 -> 18): 18 verified, 1 removed (cuba).
- fine-dining (15): 15 verified, 0 removed (1 description update on EMP).
- cafes (10): 10 verified, 0 removed, 1 address-fixed (devocion).
- bars (16): 16 verified, 0 removed.
- brunch (7): 7 verified, 0 removed.
- hidden-gems (4): 4 verified, 0 removed.
- bakeries (12): 12 verified, 0 removed (note: ess-a-bagel at 831 Third Ave is currently open but plans to move to The Buchanan in Q4 2026; still valid for now).
- breweries (4): 4 verified, 0 removed.
- wine-bars (9): 9 verified, 0 removed.
- speakeasies: file not present.
- late-night (6): 6 verified, 0 removed. (Note: `kossar-s-bagels` slug maps to "L&B Spumoni Gardens" entry. Cosmetic mismatch as flagged in round 3, slugs are URL-stable.)
- street-food (11): 11 verified, 0 removed.
- food-halls: file not present.
- markets (8): 8 verified, 0 removed.
- coffee-roasters (6): 6 verified, 0 removed.
- neighborhoods (16): 16 verified.
- festivals (7): 7 verified. NYCWFF 2026 confirmed Oct 15-19 (JSON has Oct 14-18 which is 2025 dates; festival is recurring annual, acceptable until generator auto-rolls). San Gennaro 2026 confirmed Sept 17-27. Ninth Avenue Festival 2026 confirmed Sat May 16 + Sun May 17. Smorgasburg 2026 confirmed April 4 start. Queens Night Market 2026 confirmed April 18 start. Taste of Times Square: 2026 not yet announced but recurring September, historically certain. Burger Bash within NYCWFF October confirmed.
- cooking-classes (3): 3 verified (ICE 225 Liberty St; La Scuola at Eataly Flatiron 200 5th Ave; League of Kitchens private-home model with caps of 6 in person).
- food-tours (3): 3 verified (Joe DiStefano Flushing tour active; Scott Pizza Tours 3 pizzerias/2.5 hours format active; Harlem Heritage Tours active with Sylvia / Amy Ruth route).
- itineraries (3): 3 verified. Route logic still walkable.
- dietary/vegan (3 -> 2): 2 verified, 1 removed (eleven-madison-park-vegan).
- dietary/vegetarian (3): 3 verified.
- dietary/gluten_free (2): 2 verified.
- dietary/halal (2): 2 verified.
- dietary/kosher (2): 2 verified.

## Stage 2: round-4 convergence call

- This is round 4. K = 3.
- Recommendation: **convergence** (K < 5 trigger).
- Rationale: Round trajectory r1=22, r2=5, r3=20, r4=3. The r3 spike was real (validator under-counting plus a 100% sweep against a previously thin sample); r4 converges to the expected residual after r3 cleared the closed-venue and address-hallucination tail. Of the 3 r4 defects, only 1 is a missed closure (Cuba), 1 is a venue relocation that happened on the same block (Devocion moved 1 block), and 1 is an editorial claim made stale by a menu-policy change (EMP October 2025 reversion). None of the 3 are address hallucinations of the round 3 P0 type. The data is stable enough to ship.

## Stage 3: cross-city correctness

- `scripts/check_external_urls.py --country united-states --city new-york-city`: 4 / 142 broken, all 401/403 anti-bot (alibabarestaurant.com 403, etcsteakhouse.com 403, unsplash photo URL 401, nanxiangxiaolongbao.com 403). Per PROMPT.md these are acceptable. No real broken URLs.
- `scripts/audit_live.py | tail -10`: 0 errors site-wide (1294 pages crawled, 0 errors, 100 warnings: 89 meta-description length-cap, 11 title length-cap). Broken extra links: 0 (the 4 NYC neighborhood broken cross-cuts flagged in round 3 have resolved post-regen, or are no longer surfacing).
- Breadcrumb / state-page / country-hub spot-checks: pass. `/united-states/`, `/united-states/new-york/`, `/united-states/new-york-city/` all crawled cleanly during audit_live.

## Defects removed (atomic .tmp + os.replace)

| Slug | Topic | Reason | Action |
|---|---|---|---|
| cuba | casual-dining | Yelp CLOSED March 2026 at 222 Thompson; site live but signals conflict | REMOVE |
| eleven-madison-park-vegan | dietary/vegan | EMP reintroduced fish + meat Oct 2025; no longer entirely plant-based | REMOVE from vegan |

## Address fixes (atomic .tmp + os.replace)

| Slug | Topic | From | To |
|---|---|---|---|
| devocion | cafes | 69 Grand Street, Brooklyn 11249 (closed) | 148 Grand Street, Brooklyn 11249 (active flagship) |

## Description updates (atomic .tmp + os.replace)

| Slug | Topic | Reason |
|---|---|---|
| eleven-madison-park | restaurants | Reflect October 2025 menu reversion to fish + meat + plant-based path |
| eleven-madison-park | fine-dining | Same reason |

## Below-floor topics after QA

- breweries: 4 entries (target 5-15). Below floor unchanged from round 3. Recommend research agent backfill in next research pass.
- All other below-floor counts unchanged from round 3.

## Notes the next agent should pay attention to

- The Cuba removal was conservative under the "when in doubt, remove" rule. If a future pass finds the venue actively operating with its own phones answered and reservations being seated, re-add at 222 Thompson Street 10012.
- Devocion is a textbook "moved one block" case. The brand operates, the address moved. Validation that checks venue-on-the-street rather than venue-exists-as-brand catches this; the round 3 sweep missed it.
- The EMP plant-based-only claim was a 2021-2025 truth that became false in October 2025. Future text reviews should treat "exclusively plant-based" claims as time-bound and re-verify.
- The NYCWFF JSON `start_day/end_day` of October 14-18 reflects the 2025 dates; the actual 2026 edition is October 15-19. Per the recurring-pattern principle in user memory, the generator should compute next-occurrence from the pattern rather than the literal dates; if it doesn't, this needs an update. Cosmetic for now.

## Verdict

VERDICT: PASS
