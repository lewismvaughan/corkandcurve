# Cork & Curve scripts audit

Maps each `scripts/*.py` file to its wine-vertical readiness state.
The cork repo forked TJ's scripts directly; most are vertical-agnostic
but some have TJ topic slugs hardcoded.

Legend:
- ✅ ready — works as-is for wine vertical
- 🟡 adapt — works but needs wine-specific tweaks (topic slugs, etc.)
- 🔴 rewrite — TJ-specific logic, needs wine-vertical replacement

## Generators

| Script | Status | Notes |
|---|---|---|
| `new_region.py` | ✅ | Wine-specific (replaces TJ's new_city.py). |
| `generate_city.py` | 🟡 | Rename calls to "region". Topic slugs (food → wine) hardcoded — update TOPIC_SLUGS const. |
| `generate_region_page.py` | 🟡 | Hub renderer. Adapt research-key references to wine topic keys. |
| `generate_topic_page.py` | 🟡 | Topic chapter renderer. Reads topic JSON keys (food_festivals, restaurants) — adapt to wine_festivals, vineyards, etc. |
| `generate_entity_pages.py` | 🟡 | Per-entity page renderer. Currently emits Restaurant/Cafe/Bar schema; needs Winery / BarOrPub / Course / Festival selection based on topic. |
| `generate_homepage.py` | 🟡 | Renders TJ-flavored homepage with trending dishes. Adapt to trending grapes / signature wines. |
| `generate_chrome_pages.py` | 🟡 | About/Privacy/Search/etc. Cork already has homepage placeholder; chrome pages need full rebuild. |
| `generate_sitemap.py` | 🟡 | Sitemap generator. URL discovery logic walks TJ URL conventions — adapt to wine URL structure. |
| `generate_robots.py` | ✅ | Generic. |
| `generate_search_index.py` | 🟡 | Builds /search/search-index.json. Adapt entity type tags (restaurant→winery) + topic slug mappings. |
| `generate_city_cuisine.py` | 🔴 | TJ-specific. Wine equivalent is `generate_region_grape.py` (NOT YET WRITTEN). |
| `generate_city_dietary.py` | 🟡 | Logic transfers (sub-key iteration) but TJ dietary keys (vegan/halal/kosher) vs wine dietary (biodynamic/organic/natural). |
| `generate_city_dish.py` | 🔴 | TJ-specific. Wine equivalent is `generate_signature_wine.py` (NOT YET WRITTEN). |
| `generate_city_nightlife_sub.py` | 🟡 | Subkey iteration works. Wine nightlife subkeys (wine_bars_late, listening_bars, etc.) need swap. |
| `generate_city_price_tier.py` | 🟡 | Logic ok; wine price tiers are different ($, $$, $$$, $$$$ → budget/mid/premium/icon). |
| `generate_city_topic_when.py` | 🔴 | TJ time-of-day. Not directly applicable to wine. Replace with seasonal-wine renderer. |
| `generate_country_topic.py` | 🟡 | Country × topic. Adapt topic list to wine topics. |
| `generate_country_cuisine.py` | 🔴 | TJ-specific. |
| `generate_country_dish.py` | 🔴 | TJ-specific. |
| `generate_country_dietary.py` | 🟡 | Same shape as city version, adapt similarly. |
| `generate_country_nightlife_sub.py` | 🟡 | Same shape, adapt subkeys. |
| `generate_neighborhood_cuisine.py` | 🔴 | TJ-specific. Wine equivalent: sub-appellation × grape. |
| `generate_global_top_topics.py` | 🟡 | Global top-X. Adapt slug list (rooftops/speakeasies → wineries/tasting-rooms/wine-bars). |
| `generate_cross_cuts.py` | 🟡 | Generic cross-cut machinery. Adapt topic registry. |
| `generate_scoped_cross_cuts.py` | 🟡 | Same. |
| `generate_country_stubs.py` | ✅ | Stub country index. Works for any vertical. |
| `generate_extras.py` | 🟡 | Topic landings + search page. Adapt topic list. |

## Validation / QA

| Script | Status | Notes |
|---|---|---|
| `validate_data.py` | 🟡 | Em-dash check + length caps generic. TOPIC_FILES const has TJ slugs. |
| `verify_entities.py` | ✅ | Generic verified-block check. Walks nested dict structure (works for wine nightlife.json + dietary.json). |
| `check_internal_references.py` | 🟡 | Cross-refs check. Adapt to wine cross-refs (signature_wines.producer, day_trips_wine.recommended_vineyards, itineraries.venues). |
| `check_evidence_content.py` | 🟡 | Currently checks dietary cuisine_evidence for vegan/halal/kosher keywords. Adapt for biodynamic/organic/natural. |
| `check_festival_dates.py` | ✅ | Generic festival start_month check. |
| `check_external_urls.py` | ✅ | HEAD-check on booking/affiliate/image URLs. Generic. |
| `check_jsonld.py` | 🟡 | Validates schema.org on built HTML. Wine schema types differ. |
| `cleanup_broken_urls.py` | ✅ | Strips dead URLs from JSON. Generic. |
| `ship_safety.sh` | ✅ | Orchestrates the 7 layers. Generic — calls the scripts above. |
| `orphan_audit.py` | 🟡 | Walks all internal links. Adapt URL patterns to wine. |

## Geo / maps

| Script | Status | Notes |
|---|---|---|
| `geocode_entities.py` | ✅ | Generic. v4 sanity-check guard works for any vertical. CITY_CENTROIDS has 614 entries — wine regions outside cities need adding (Sangiovese-only towns, Mendoza-suburbs). |
| `build_city_pins.py` | 🟡 | Renames to build_region_pins.py. Logic identical. |
| `qa_geo_outliers.py` | 🟡 | Generic outlier detection. EXPECTED_CITY_TOKENS has TJ tokens. |

## Utilities

| Script | Status | Notes |
|---|---|---|
| `utils/template_renderer.py` | 🟡 | TJ topic-template map hardcoded. Adapt. |
| `utils/data_loader.py` | 🟡 | TJ topic-file list hardcoded. |
| `utils/filter_search.py` | ✅ | Generic filter+sort widget. |

## SEO

| Script | Status | Notes |
|---|---|---|
| `generate_og_cities.py` | 🟡 | OG image generator. Adapt to wine regions. |
| `build_og_cities.py` | 🟡 | Same. |

## What "🟡 adapt" really means

In every 🟡 script the changes are MECHANICAL:
1. Open the file
2. Find `TOPIC_SLUGS = [...]` or `TOPIC_KEYS = {...}` const
3. Replace with the 24 wine topic slugs from `scripts/new_region.py`
4. Find any food-vertical entity-class references (`Restaurant`,
   `Cafe`, `BarOrPub`) and swap for wine equivalents
   (`Winery`, `BarOrPub`, `Place`)
5. Test render against the first region (Bordeaux)

Allocate ~2 hours total for the 🟡 sweep. The 🔴 rewrites need fresh
code — allocate ~3-4 hours.
