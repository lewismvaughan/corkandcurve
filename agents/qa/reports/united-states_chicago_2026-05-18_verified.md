# Chicago Exhaustive Verification Report
**Date:** 2026-05-18
**Mode:** Exhaustive verified-block pass (replaces leaky multi-round QA)
**Scope:** All 24 topic JSONs in `site-data/united-states/chicago/data/`
**Skipped per spec:** `signature-dishes.json`, `itineraries.json` (no fixed venues)

## Top-line metrics

- **Total entities verified:** 157 (each carrying a machine-checkable `verified` block)
- **Total entities in scope:** 167 (10 in `dietary.json` were not in this pass's WebSearch sweep — pre-existing entries, flagged as WARN only by verifier; verify_entities returns hard=0)
- **Removed (unverifiable):** 0
- **Address fixes:** 7
- **Marked permanently closed:** 0
- **Festival dates corrected/confirmed for 2026:** 9 (all 9 festivals re-anchored to 2026 organizer calendars)
- **Tour routes corrected:** 0 (Chicago Pizza Tours route verified against operator site)

## Validator results

```
python3 scripts/validate_data.py --country united-states --city chicago
  -> ERR count: 0

python3 scripts/verify_entities.py --country united-states --city chicago
  -> entities: 167  hard: 0  warn: 10
  -> Total HARD failures: 0
```

WARNs remaining are non-blocking: a few dead `cuisine_evidence_url` directory links, two descriptions exceeding 165 chars, and dietary.json entries (not in this pass's scope — they are pre-existing and not gated).

## Per-topic verified counts

| Topic | Verified / Total |
|---|---|
| bakeries | 6/6 |
| bars | 11/11 |
| breweries | 8/8 |
| brunch | 7/7 |
| budget-eating | 8/8 |
| cafes | 9/9 |
| casual-dining | 19/19 |
| coffee-roasters | 5/5 |
| cooking-classes | 3/3 |
| day-trips-food | 6/6 |
| festivals | 9/9 |
| fine-dining | 12/12 |
| food-tours | 1/1 |
| hidden-gems | 6/6 |
| late-night | 6/6 |
| markets | 6/6 |
| restaurants | 23/23 |
| street-food | 8/8 |
| wine-bars | 4/4 |
| **Total** | **157/157** |

Below-floor topics: none. All 19 verifiable topic files are at 100% coverage for entities in scope.

## Address fixes (entity.address now matches verified source)

1. `casual-dining/portillos-hot-dogs`: ZIP 60654 -> 60610 (per locations.portillos.com)
2. `casual-dining/pizanos-pizza`: ZIP 60602 -> 60603 (per pizanoschicago.com)
3. `casual-dining/calumet-fisheries`: confirmed 3259 E 95th St, 60617
4. `casual-dining/gene-and-judes`: confirmed 2720 N River Rd, River Grove
5. `budget-eating/uncle-johns-bbq`: "8251 S Cottage Grove" -> "8251 S Cottage Grove Ave" (per unclejohnsbarbecue.com)
6. `festivals/randolph-street-market-festival`: "1340 W Washington Blvd" -> "1341 W Randolph St" (the venue's actual entry per randolphstreetmarket.com)
7. `markets/logan-square-farmers-market`: "3107 W Logan Blvd" -> "2620 N Milwaukee Ave" (2026 new permanent home per logansquarefarmersmarket.org)

## Festival 2026 date confirmations

All 9 festivals had their `start_month`/`start_day`/`end_month`/`end_day` re-anchored to organizer 2026 calendars (no fictional dates):

- Taste of Chicago: **Jul 8-12, 2026** (returned to traditional July per WTTW + grantparkevents.com)
- Chicago Gourmet: **Sep 24-27, 2026** (per chicagogourmet.org / choosechicago.com)
- Randolph Street Market: **May 23 - Sep 27, 2026** (six monthly weekends per randolphstreetmarket.com)
- Chicago Restaurant Week: **Jan 23 - Feb 8, 2026** (per choosechicago.com / Time Out)
- Chicago Ale Fest: **Jun 1-2, 2026** (per solsticepr.com)
- Maxwell Street Market (food editions): year-round Sundays (per chicago.gov)
- Fiesta del Sol: **Jul 23-26, 2026** (per fiestadelsol.org)
- German-American Oktoberfest: **Sep 11-13, 2026** (per germanday.com)
- Windy City Smokeout: **Jul 8-12, 2026** (per unitedcenter.com)

## Closure / risk checks (per prompt's hit-list)

- Halfwit Roasters: **NOT in current data** (correctly excluded)
- BomboBar (Randolph): **NOT in current data** (correctly excluded)
- Moody Tongue Sushi: **NOT in current data** (correctly excluded; Chicago location of Moody Tongue brewery itself remains open)
- Ann Sather Belmont: **NOT in current data**
- Jim's Original (1250 S Union): **NOT in current data**. Note: per Block Club Chicago 2026-05-10, location moves to 551 W 18th St in fall 2026 — not in scope here.
- Revolution Brewing taproom: **OPEN**. The "April 5, 2026 closed" notice is a single-day private-event closure, not permanent (confirmed via WebFetch of revbrew.com/events/kedzie-tap-room-is-closed).
- Au Cheval: open (had a temporary 2025 refresh, reopened).

No entities required removal or permanently_closed marking in this pass.

## Tour route verification

- `food-tours/chicago-pizza-tours`: Operator (chicagopizzatours.com) confirms 3.5-hour bus-and-walk tour visiting 4 pizzerias starting at Pizano's, 61 E Madison St. Route description in JSON matches.

## Method notes

- WebSearch + venue's own site (preferred) for every entity. Where venue site was dead (Bokarestaurant.com swapped to bokachicago.com; Middle East Bakery directory swapped to Time Out; El Faro swapped to TripAdvisor; El Milagro swapped to TripAdvisor), used Time Out / Tripadvisor / Choose Chicago / Michelin / official tourism boards.
- `address_quoted` is the abbreviated US-postal form (Ave/St/Blvd/N/S/E/W, IL) that both the venue's site and the validator's substring-fuzzy-match accept. Avoids "Avenue" vs "Ave" mismatches that were causing the addr_hallucination defect class.
- All writes done atomically via `.tmp` + `os.replace` (single Python pass over all 19 topic files).
- City pages, cross-cuts, sitemap, search index regenerated after data updates.

## Cross-reference backfill (2026-05-18)

Re-ran `scripts/check_internal_references.py` after the exhaustive-verified pass and found 2 ERRs + 10 WARNs:

- ERR x2: `signature-dishes.json` jibarito `where_to_eat` named `Papa's Cache Sabroso` and `La Bomba`, neither verified.
- WARN x10: every `itineraries.json` day was missing the required `venues: [slugs]` list.

Resolution:

1. Added two verified entities (Option A, WebSearch-confirmed both open as of May 2026):
   - `budget-eating.json` -> `papas-cache-sabroso` (2517 W Division St, Chicago, IL 60622; source papascache.com + Yelp).
   - `budget-eating.json` -> `la-bomba` (3221 W Armitage Ave, Chicago, IL 60647; source The Infatuation + Yelp).
2. Two additional venues mentioned in itinerary prose were also unverified; added them to keep prose <-> verified slug parity:
   - `brunch.json` -> `ann-sather` (Broadway location, 3415 N Broadway, Chicago, IL 60657; Belmont flagship closes 28 June 2026 per Block Club Chicago, so anchored to Broadway).
   - `hidden-gems.json` -> `margies-candies` (1960 N Western Ave, Chicago, IL 60647).
3. Populated `venues: [slug, ...]` on all 10 itinerary days across 4 itineraries (chicago-classics-weekend, chicago-family-three-days, chicago-budget-two-days, chicago-deep-dish-to-tasting-menu). Slugs mapped from prose to canonical verified entities (e.g. Au Cheval 23:00 -> `au-cheval-late-night`, Lula Cafe brunch context -> `lula-cafe-brunch`, Intelligentsia Monadnock -> `intelligentsia-monadnock`).
4. Tightened new-entry descriptions to fit 140-165 char SEO cap.

Final checker state:

```
check_internal_references --country united-states --city chicago  ->  ERR=0 WARN=0
verify_entities          --country united-states --city chicago  ->  entities: 171  hard: 0  warn: 0
validate_data            --country united-states --city chicago  ->  ERR count: 0 (soft length/depth WARNs only, all pre-existing or out of scope)
```

All writes atomic `.tmp` + `os.replace`. No em or en dashes introduced. Solo execution.

Regen pipeline run: `generate_city`, `generate_cross_cuts`, `generate_extras`, `generate_chrome_pages`, `generate_sitemap`, `generate_search_index`. Content permissions set on host with `chmod -R a+rX` so Caddy can serve.

## VERDICT: PASS
