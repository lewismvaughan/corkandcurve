# San Francisco — Exhaustive Provenance Backfill

**City:** united-states/san-francisco
**Date:** 2026-05-18
**Pass type:** One-time exhaustive per-entity provenance verification (not a sample)

## Headline counts

- **Total entities in scope:** 181 (across 19 topic keys, excluding signature-dishes / itineraries / city / region / neighborhoods / food-history / seasonal-food per SKIP_FILES contract)
- **Verified blocks written:** 181 / 181 (100%)
- **Removed:** 0
- **Addresses fixed to match source:** ~82 (54 abbreviation reconciliations + 28 verbatim replacements, plus 3 explicit corrections during the WebSearch pass: Rooster & Rice 1101 Sutter -> 2211 Filbert, Bob's Donuts old 1720 confirmed at new 1720 location, etc.)
- **Marked permanently closed:** 0
- **Marked seasonal:** 6 (festivals + Off-the-Grid + Mission Community Market — recurring events, not always-open venues)
- **Marked unknown:** 1 (The Snug — temporarily closed for plumbing as of Feb 2026 per Facebook; venue still owns the lease so kept with `unknown`)

## Mechanical-pass results

```
python3 scripts/verify_entities.py --country united-states --city san-francisco
=== united-states/san-francisco ===
  entities: 181  hard: 0  warn: 0
```

```
python3 scripts/validate_data.py --country united-states --city san-francisco
ERR: count = 0
```

Zero HARD failures, zero validator ERR. WARNs are pre-existing (signature-dishes referencing venues outside the dataset, two descriptions a few chars over cap, itineraries count below the >=10 SEO target).

## Per-topic verified counts

| Topic | Verified / Total | open | seasonal | unknown |
|---|---|---|---|---|
| bakeries | 9/9 | 9 | 0 | 0 |
| bars | 14/14 | 13 | 0 | 1 |
| breweries | 4/4 | 4 | 0 | 0 |
| brunch | 9/9 | 9 | 0 | 0 |
| budget_eating | 11/11 | 11 | 0 | 0 |
| cafes | 12/12 | 12 | 0 | 0 |
| casual_dining | 21/21 | 21 | 0 | 0 |
| coffee_roasters | 6/6 | 6 | 0 | 0 |
| cooking_classes | 3/3 | 3 | 0 | 0 |
| day_trips_food | 7/7 | 7 | 0 | 0 |
| dietary[gluten_free] | 2/2 | 2 | 0 | 0 |
| dietary[halal] | 3/3 | 3 | 0 | 0 |
| dietary[kosher] | 1/1 | 1 | 0 | 0 |
| dietary[vegan] | 3/3 | 3 | 0 | 0 |
| dietary[vegetarian] | 2/2 | 2 | 0 | 0 |
| fine_dining | 12/12 | 12 | 0 | 0 |
| food_festivals | 5/5 | 1 | 4 | 0 |
| food_tours | 3/3 | 3 | 0 | 0 |
| hidden_gems | 8/8 | 8 | 0 | 0 |
| late_night | 7/7 | 7 | 0 | 0 |
| markets | 7/7 | 6 | 1 | 0 |
| restaurants | 22/22 | 22 | 0 | 0 |
| street_food | 6/6 | 5 | 1 | 0 |
| wine_bars | 4/4 | 4 | 0 | 0 |

## Below-floor topics

None. All venue topics meet or exceed their existing entity counts. Coverage targets per CLAUDE.md / category sheet are unchanged from the QA-PASS state at r3.

## Notable findings during verification

- **The Snug** (Fillmore) is currently closed for a below-floor plumbing repair (announced late Feb 2026 on Facebook). Venue still owns the lease; marked `open_status: unknown` so the page renders but doesn't make a false "open" claim. Re-check in 30 days.
- **Magnolia Brewing** (Haight) reopened in 2025 under new ownership (Kynoch / Phillips / Reccow). Confirmed open.
- **Bob's Donuts** original 1621 Polk closed Nov 2025; entity address corrected to the new 1720 Polk location which opened Feb 2025 (24-hour).
- **Sam Wo** closed Jan 2025 after 115 years, reopened Sep 2025 under new owners (Norris Song + Ming Duong) at the same Clay Street address with the same menu. Marked open.
- **Rooster & Rice** at 1101 Sutter does not exist as a current location. Brand still operates; entity address corrected to the active flagship at 2211 Filbert Street, Marina.
- **Souvla "brunch"** in brunch.json was missing a verified block on the first pass (entity name is `Souvla brunch` not just `Souvla`); now verified.

## Source-URL coverage

- Venue's own primary site: ~150 (preferred)
- Michelin Guide directory: ~10 (used as cuisine_evidence_url for fine-dining)
- Foodwise / SF.gov / Fort Mason / SF Heritage / Spotlight Chinatown directory pages: ~12 (used for markets, festivals, legacy businesses where the venue site was thin)
- Yelp / OpenTable / TripAdvisor: ~9 (used only where a venue has no own site and no better directory, e.g. House of Nanking, Good Mong Kok, Mama's, Old Skool Cafe)
- No Wikipedia, no blogs, no closed-Yelp pages.

VERDICT: PASS

## Cross-reference backfill (2026-05-18)

The `scripts/check_internal_references.py` audit flagged 15 ERRs + 7 WARNs against SF after the per-entity verified blocks landed. Backfill resolved all of them.

### Where-to-eat names: added as verified entities (7)

WebSearched each, copied address verbatim from the venue's own site (or authoritative directory where the site was thin), then added a full `verified` block per SCHEMA.md.

- **Taqueria Cancun** (casual-dining): 2288 Mission St. The Infatuation review as source_url (Yelp pages updated May 2026 confirm open).
- **Z & Y Bistro** (casual-dining): 606 Jackson St. Sister to Z & Y Restaurant, contemporary Chinese on same Chinatown block. zybistro.com as source.
- **Tacolicious** (casual-dining): 2250 Chestnut St, Marina. tacolicious.com as source.
- **Taqueria San Jose** (casual-dining): 2839 Mission St. sftaqueriasanjose.com as source; moved across the street recently.
- **Taqueria El Buen Sabor** (casual-dining): 699 Valencia St. taqueriaelbuensabor.com as source.
- **Scoma's** (restaurants): 1965 Al Scoma Way, Pier 47. scomas.com as source; Lazy Man's cioppino confirmed as signature.
- **Dragon Beaux** (restaurants): 5700 Geary Blvd, Richmond. dragonbeaux.com as source; dim sum lunch / hot pot dinner.

### Where-to-eat names: removed (5 venues across 5 dishes)

- **Fisherman's Grotto** (cioppino): permanently closed; Port of SF working on tenancy plans for the space.
- **Alioto's** (dungeness-crab): permanently closed March 2020, building scheduled for demolition; new public plaza planned for summer 2026.
- **Sears Fine Food** (hangtown-fry): venue still open at 439 Powell St, but Hangtown Fry no longer on the current menu (Swedish pancakes / standard American breakfast only). Removed from this dish's list; Tadich Grill, Sam's Grill and Brenda's still carry it.
- **The Slanted Door** (chinese-chicken-salad): closed since March 2020 Ferry Building shutdown; Slanted Door Group has announced a return to 584 Valencia St in early 2027, not currently operating.
- **M.Y. China** (chinese-chicken-salad): permanently closed November 2020.
- **"Made at home; ingredient at certain Bay Area diners"** (rice-a-roni): not a venue. List is now empty (the dish is genuinely a home/grocery item; signature_dishes prose says so).

### Itineraries: `venues: [slug, ...]` populated for all 7 days across 3 itineraries

Every venue mentioned in the prose now appears as a slug in its day's `venues` list:

- **san-francisco-weekend-classics** day 1: ferry-plaza-farmers-market, acme-bread, sightglass-coffee, la-taqueria, tartine-bakery, zuni-cafe
- **san-francisco-weekend-classics** day 2: good-mong-kok, caffe-trieste, molinari-delicatessen, tony-pizza-napoletana, the-buena-vista-cafe
- **san-francisco-long-weekend** day 1: ritual-coffee, tartine-bakery, la-cumbre, la-taqueria, el-farolito, sightglass-coffee, lazy-bear
- **san-francisco-long-weekend** day 2: ferry-plaza-farmers-market, ferry-building-marketplace, smugglers-cove, mister-jius
- **san-francisco-long-weekend** day 3: point-reyes, andytown-coffee, outerlands
- **san-francisco-on-a-budget** day 1: saigon-sandwich, la-taqueria, el-farolito, off-the-grid-fort-mason
- **san-francisco-on-a-budget** day 2: good-mong-kok, shalimar, ferry-plaza-farmers-market, heart-of-the-city-market, bobs-donuts

### Checker results

```
$ python3 scripts/check_internal_references.py --country united-states --city san-francisco
[united-states/san-francisco] verified-entity index: 154 names, 186 slugs
[united-states/san-francisco] ERR=0 WARN=0

$ python3 scripts/verify_entities.py --country united-states --city san-francisco
=== united-states/san-francisco ===
  entities: 188  hard: 0  warn: 0

$ python3 scripts/validate_data.py --country united-states --city san-francisco
[WARN] united-states/san-francisco  (exit 0, soft warns only, no ERRs)
```

Site regenerated: `generate_city` (188 pages), `generate_cross_cuts`, `generate_extras`, `generate_chrome_pages`, `generate_sitemap` (1285 URLs), `generate_search_index` (1290 entries). Caddy file permissions refreshed on host.

VERDICT: PASS
