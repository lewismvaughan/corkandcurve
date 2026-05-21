# New York City Provenance Backfill Report

Date: 2026-05-18
Scope: All 24 NYC topic JSONs at `/station/repo/site-data/united-states/new-york-city/data/`
Skipped per SCHEMA: `signature-dishes.json`, `itineraries.json`
Tool: WebSearch primary verification + `scripts/verify_entities.py` mechanical pass

## Summary

- **Entities verified** (entered with `verified` block): **191**
- **Entities removed** (no usable source / fabricated): **1**
  - `budget-eating.json` -> `katzs-budget` ("Yonah Schimmel Bagel & Lox" at 138 East Houston Street): duplicate fabricated entry. The real Yonah Schimmel's is at 137 East Houston Street (already verified under slug `yonah-schimmels`). No "138 East Houston" location exists.
- **Entities address-fixed** (mismatch corrected to match source quote): **70+ across 19 files**
  - Notable: Xi'an Famous Foods budget-eating entry was at fabricated "111 St Marks Place" (Xi'an's actual St Marks location was 81 St Marks, closed 2020). Repointed to current Union Square location at 139 4th Avenue per xianfoods.com locations page.
  - Numerous "Avenue/Street" vs "Ave/St" normalizations to satisfy fuzzy match.
- **Entities marked permanently_closed**: **0** (no closures found among the 191)
- **Entities marked seasonal**: **1** (`country-boys-tamales` at Red Hook Ball Fields - operates May-Oct per Time Out + Gayot)

## Per-topic counts after the pass

| Topic | Count | Floor | Status |
|---|---|---|---|
| bakeries | 12 | 8 | OK |
| bars | 16 | 8 | OK |
| breweries | 4 | 8 | **BELOW FLOOR** |
| brunch | 7 | 8 | **BELOW FLOOR** |
| budget-eating | 11 | 8 | OK (was 12, one fabricated entity removed) |
| cafes | 10 | 8 | OK |
| casual-dining | 18 | 8 | OK |
| coffee-roasters | 6 | 8 | **BELOW FLOOR** |
| cooking-classes | 3 | 3 | AT FLOOR |
| day-trips-food | 7 | 5 | OK |
| dietary | 11 | n/a | OK |
| festivals | 7 | 5 | OK |
| fine-dining | 15 | 8 | OK |
| food-tours | 3 | 3 | AT FLOOR |
| hidden-gems | 4 | 4 | AT FLOOR |
| late-night | 6 | 5 | OK |
| markets | 8 | 5 | OK |
| restaurants | 23 | 12 | OK |
| street-food | 11 | 8 | OK |
| wine-bars | 9 | 8 | OK |

## Below-floor topics flagged

- **breweries** (4 of 8): NYC craft beer scene has many more candidates (Singlecut, Threes, Talea, Strong Rope, etc.). Pre-existing under-fill; not introduced by this pass.
- **brunch** (7 of 8): one short. Pre-existing.
- **coffee-roasters** (6 of 8): two short. Pre-existing.

These were already below floor before the verification pass; this audit did not delete entities to drop them below floor (only the duplicate Yonah Schimmel in budget-eating, which was already at 12).

## Mechanical pass results

```
=== united-states/new-york-city ===
  entities: 191  hard: 0  warn: 0

Total HARD failures across 1 cities: 0
```

- 0 dead source_url
- 0 address mismatches
- 0 stale (all checked_on=2026-05-18)
- 0 missing verified blocks
- 0 permanently_closed entries blocking ship

## Validator pass

```
$ python3 scripts/validate_data.py --country united-states --city new-york-city 2>&1 | grep ERR:
(no output - 0 errors)
```

## Pages regenerated

- `generate_city.py`: 191 entity pages, 20 topics covered, 1 stale pruned
- `generate_cross_cuts.py`: 184 cross-cut pages
- `generate_extras.py`: OG images and logo refreshed
- `generate_chrome_pages.py`: 13 chrome pages
- `generate_sitemap.py`: 1274 URLs in sitemap.xml
- `generate_search_index.py`: 1268 entries in search-index.json (532 KB)

## Notable defect classes caught

1. **Address hallucination at source**: Xi'an Famous Foods at "111 St Marks Place" was a fabricated address (Xi'an never had a 111 St Marks location). Fixed to current 139 4th Avenue per official site.
2. **Duplicate-with-fake-address**: A second "Yonah Schimmel" entry as a separate "Bagel & Lox" at 138 East Houston was a fabricated duplicate of the real 137 East Houston location. Removed.
3. **Street/Avenue normalization**: ~70 entities had "Street" vs "St", "Avenue" vs "Ave", "Third" vs "3rd", "East" vs "E" mismatches between source and entity.address. Each fixed to match `address_quoted` verbatim from the venue's own site.
4. **Seasonal venue handled correctly**: Country Boys at Red Hook Ball Fields is seasonal (May-Oct); marked `open_status: "seasonal"` rather than open.

## VERDICT: PASS

---

## Cross-reference backfill (added 2026-05-18)

The new `scripts/check_internal_references.py` flagged 16 ERRs and 4 WARNs after the provenance pass: signature-dish `where_to_eat` names that did not resolve to a verified entity in the city, and itinerary days missing the required `venues` slug list.

### signature-dishes.json (16 ERRs cleared)

Removed 8 unresolvable names (closed, fabricated, status uncertain, or not the same business):

- `Absolute Bagels` (original closed Dec 2024 over rat-infestation violations; the 2025 "New Absolute Bagels" is a separate operation in legal dispute over the name)
- `Andrew & Alan's` (no current black-and-white-cookie operation found at search)
- `Shanghai You Garden` (suffered a major fire at the 40th Road location in April 2026; current status uncertain)
- `Drunken Dumpling` (Yelp marks the 137 1st Ave room CLOSED as of March 2026)
- `ZZ's Clam Bar` (original Thompson Street location shut in 2023; replaced by the private members-only ZZ's Club in Hudson Yards)
- `Pearl Oyster Bar` (closed October 2022 after 25 years on Cornelia Street)
- `John Dory Oyster Bar` (closed February 2019 at the Ace Hotel)
- `Eisenberg's Sandwich Shop` (closed 2021; the space reopened in 2022 as S&P Lunch under separate ownership)

Added 8 new verified entities so the remaining where_to_eat names resolve cleanly:

- `restaurants.json`:
  - `pastrami-queen` — Pastrami Queen, 1125 Lexington Avenue (kosher UES deli, since 1956)
  - `sammys-roumanian` — Sammy's Roumanian Steakhouse, 112 Stanton Street (reopened April 2024)
  - `grand-central-oyster-bar` — Grand Central Oyster Bar, 89 E 42nd Street (since 1913)
  - `hwa-yuan-szechuan` — Hwa Yuan Szechuan, 42 E Broadway (Sichuan, since 2017 rebuild)
- `casual-dining.json`:
  - `mile-end-deli` — Mile End Deli, 97 Hoyt Street, Brooklyn (Montreal-Jewish, since 2010)
  - `tim-ho-wan` — Tim Ho Wan, 85 4th Avenue (Cantonese dim sum, since 2016)
- `cafes.json`:
  - `lexington-candy-shop` — Lexington Candy Shop, 1226 Lexington Avenue (since 1925)
  - `s-and-p-lunch` — S&P Lunch, 174 Fifth Avenue (Flatiron luncheonette, since 2022)
- `bars.json`:
  - `maison-premiere` — Maison Premiere, 298 Bedford Avenue, Williamsburg (since 2011)

Also added `S&P Lunch` to the `egg-cream` where_to_eat list to replace Eisenberg's. Every where_to_eat name in `signature-dishes.json` now resolves to a verified entity in the city.

### itineraries.json (4 WARNs cleared)

Added the required `venues` slug list to all four itinerary days. Slugs verified against the entity-slug index:

- `new-york-weekend-classics` day 1: `russ-and-daughters`, `joes-pizza`, `nan-xiang-xiao-long-bao`, `joes-shanghai`
- `new-york-weekend-classics` day 2: `katzs-delicatessen`, `frankies-457`, `peter-luger`
- `queens-borough-crawl` day 1: `tibetan-momo-cafe`, `nan-xiang-xiao-long-bao`, `king-souvlaki-of-astoria`
- `brooklyn-pizza-and-natural-wine` day 1: `lindustrie-pizzeria`, `lucali`, `the-four-horsemen`

`queens-borough-crawl` day 1 prose mentioned "Bohemian Hall" which has no verified entity in the NYC dataset; rewrote the closing clause to drop the Bohemian Hall reference rather than add a beer-hall entity outside the food guide's editorial scope.

### Final checker pass

```
$ python3 scripts/check_internal_references.py --country united-states --city new-york-city
[united-states/new-york-city] verified-entity index: 187 names, 193 slugs
[united-states/new-york-city] ERR=0 WARN=0

$ python3 scripts/verify_entities.py --country united-states --city new-york-city
  entities: 200  hard: 0  warn: 0

$ python3 scripts/validate_data.py --country united-states --city new-york-city 2>&1 | grep -E "ERR|HARD"
(no output - 0 errors / 0 HARD)
```

### Counts

- where_to_eat names removed: 8 (across 7 signature-dish entries)
- where_to_eat names added: 1 (S&P Lunch -> egg-cream)
- itinerary days backfilled with `venues`: 4
- new verified entities added: 9 (Pastrami Queen, Sammy's Roumanian Steakhouse, Grand Central Oyster Bar, Hwa Yuan Szechuan, Mile End Deli, Tim Ho Wan, Lexington Candy Shop, S&P Lunch, Maison Premiere)
- entity count after pass: 200 (was 191)

VERDICT: PASS
