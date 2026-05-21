# Data → Pages map

Every JSON field a food-research or QA agent fills feeds one or more
public pages. This document maps each field to the SEO surfaces it
unlocks, so an agent can see what's at stake when they fill (or skip)
a value.

Read this **before** filling a new city. The cost of a skipped field is
usually a missing rich-result class, not a missing page — but missing
rich results is a real SERP penalty.

## City-level surfaces

Every city ships with these chapters (URL = `/<country>/<city>/<topic>/`):

| Topic | Source JSON | What gets generated |
|---|---|---|
| Restaurants, fine-dining, casual-dining, cafes, bakeries, coffee-roasters, wine-bars, bars, street-food, breweries, markets, food-tours, festivals, cooking-classes, budget-eating, hidden-gems, brunch, late-night, day-trips-food | `<topic>.json` | Topic chapter + per-entity detail page at `/<country>/<city>/<topic>/<entity-slug>/` |
| Dietary | `dietary.json` (5 sub-keys: vegan, vegetarian, gluten_free, halal, kosher) | Topic chapter + per-entity page + **`/<country>/<city>/dietary/<diet>/` for each diet with ≥2 entries** |
| Signature dishes | `signature-dishes.json` | Topic chapter + **`/<country>/<city>/dish/<slug>/` per dish with ≥1 resolved venue mention** |
| Itineraries | `itineraries.json` | Renders inline on `/<country>/<city>/itineraries/` (no entity pages); each itinerary emits a `HowTo` schema block |
| Food history, seasonal food | `<topic>.json` (text) | Topic chapter, no entity pages |

## Cross-city surfaces (built by the cross-cut generator)

These pages aggregate entities ACROSS every city we cover. They are
fully auto-generated; an agent never edits them directly. But the
agent's data choices determine which cross-cuts exist.

| URL pattern | Source field on each entity | Page contents |
|---|---|---|
| `/cuisine/<slug>/` | `entity.cuisine` (controlled vocab in data/cuisines.json) | Every restaurant in this cuisine across every city |
| `/dish/<slug>/` | `signature_dishes[].slug` | Every city that has this signature dish, with where-to-eat venues |
| `/neighborhood/<city>/<slug>/` | `entity.neighborhood` | Every entity in this district across all topics |

## Scoped indexes (country + city)

Same data, narrower scope. Build the long-tail SEO surface.

| URL pattern | Filter | Source |
|---|---|---|
| `/<country>/cuisines/` | `entity.country_slug == country` | Aggregated cuisine list, country-scoped |
| `/<country>/<city>/cuisines/` | `entity.city_slug == city` | Cuisine list scoped to one city |
| `/<country>/signature-dishes/` | dishes referenced in the country | Country dish index |
| `/<country>/neighborhoods/` | hoods in the country, grouped by city | Country hood index |
| `/<country>/<city>/cuisine/<cuisine>/` | restaurants in this city with `cuisine == <cuisine>` (≥2) | High-intent "italian paris" query target |
| `/<country>/<city>/dish/<dish>/` | `signature_dishes[where_to_eat resolves in this city]` (≥1) | "where to eat croissant in paris" query target |
| `/<country>/<city>/dietary/<diet>/` | `dietary[<diet>]` entries (≥2) | "vegan paris", "halal new york" query targets |

## Field → rich-result map

Get these right or pages lose SERP enhancements:

| Field | What you get | What you lose if missing |
|---|---|---|
| `entity.editorial_score` (1.0-5.0) | `AggregateRating` + `Review` schema → SERP star ratings | No stars in search results; falls out of `ItemList` ordering on topic pages |
| `entity.name` | Page title, schema name, sitemap, search index | Entity is unindexable |
| `entity.address` | `PostalAddress` schema, "Get directions" CTA, future `geo:` block | Local search loses signal |
| `entity.cuisine` | `servesCuisine` on Restaurant schema; cuisine cross-cut eligibility | No `/<country>/<city>/cuisine/<x>/` page contribution |
| `entity.neighborhood` | Neighborhood cross-cut eligibility, on-card location | Drops from `/neighborhood/<x>/<y>/` page |
| `entity.verified` block (provenance) | Survives `ship_safety.sh` gates | **Entity blocked from shipping** |
| `dietary.<diet>` ≥2 entries | `/<country>/<city>/dietary/<diet>/` page is born | No page for that diet in that city |
| `signature_dishes[].where_to_eat` (resolvable names) | `/<country>/<city>/dish/<slug>/` page; dish cross-cut card | No "where to eat" surface for this dish |
| `signature_dishes[].description` + `.history` | `Article`-like body on dish page, schema description | Thin dish page |
| `itineraries[].days[].morning/afternoon/evening` | `HowTo` + `HowToSection` + `HowToStep` schema → step-by-step rich snippet | No rich snippet eligibility |
| `festivals.start_month`/`day_range` | `Event` schema with computed next-occurrence → Events knowledge panel | No event rich card |
| `destination.hero_image` | Per-city OG card (`/og/<city>.jpg`) is rebuilt with this photo | Falls back to typography card |
| `entity.address` quality (street number + street + postcode + city) | Geocoded by Nominatim; `geo.latitude` + `geo.longitude` on Restaurant schema, static map thumbnail (`<img>`) on the entity page, pin on the city-hub Leaflet map, pin on every cross-cut page that includes the entity, Apple Maps / Google Maps / Waze deep-links use the coordinates instead of a string lookup | No `geo:` block, no map thumbnail, no pin on any map. Deep-link buttons fall back to address-string queries (still work but less precise). |

## What gets auto-regenerated, and when

When `ship_city.sh france paris` runs, the chain is:

1. `inject_slugs.py` + `validate_data.py` + `cleanup_broken_urls.py` + `verify_entities.py` + `check_internal_references.py` → mechanical gates
2. QA report check (`ship_city_full.sh` wrapper enforces all 4 QA stages: pass-1, pass-2, Opus final)
3. **`geocode_entities.py --city <city>`** → geocode every address via Nominatim, cached on disk. **Post-QA on purpose**: never spend Nominatim's 1/sec budget on addresses that QA later corrects or entities QA later drops. v3 fallback chain: canonical → venue-prefix strip → suite/unit strip → combo strip → postcode centroid. Each cache entry records which strategy resolved it.
4. **`check_geocode_coverage.py <country> <city>`** → SOFT report. Lists every entity whose address still didn't resolve. Doesn't block ship; surfaces gaps so an editor can refine the address text or accept the entity as inherently un-mappable.
5. `generate_city.py france paris` → city hub + 24 topic pages, entity pages with map thumbnails + `geo:` schema, branded OG cards, lazy Leaflet maps with pins.
4. `generate_entity_pages.py` → individual entity pages (with **AggregateRating**, **Author/Person**, breadcrumbs)
5. `generate_cross_cuts.py` → global `/cuisine/<x>/`, `/dish/<x>/`, `/neighborhood/<city>/<hood>/`
6. `generate_scoped_cross_cuts.py` → country + city scoped indexes
7. `generate_city_dietary.py` → city × dietary pages (Vegan/Vegetarian/etc.)
8. `generate_city_cuisine.py` → city × cuisine pages (Italian/Japanese/etc.)
9. `generate_city_dish.py` → city × dish pages (Croissant/Pizza/etc.)
10. `build_og_cities.py` → branded per-city OG cards
11. `generate_extras.py` → global topic pages (`/topics/<x>/`)
12. `generate_chrome_pages.py` → `/cities/`, `/about/`, legal pages
13. `generate_homepage.py` → `/`
14. `generate_sitemap.py` → section-sharded sitemap with honest per-URL lastmod
15. `generate_robots.py` + `generate_search_index.py` → robots + 7,900-entry search index
16. chmod + smoke test + IndexNow ping

`generate_city.py` (dev mode) chains 4-7, 9, 10, 14, 15 in one shot, so
quick iteration during development also keeps every SEO surface fresh.

## What an agent should NOT skip

P0 (page won't ship):
- `verified` block (every entity)
- `slug` + `name` + `address` for venues

P1 (page ships but loses rich results / SERP power):
- `editorial_score` (loses stars)
- `cuisine` on restaurants (loses cuisine cross-cuts)
- `neighborhood` (loses neighborhood cross-cuts)
- `description` (thin page)

P2 (lost long-tail SEO surfaces):
- Dietary sub-buckets with ≥2 entities per diet
- `signature_dishes[].where_to_eat` populated with real venue names that resolve
- `destination.hero_image` (loses branded OG)
- Address quality matters: a precise `street number + street + postcode + city` geocodes 95%+ on the v3 algorithm. Venue-name-only ("Le Bristol") or vague ("Throughout Berlin") will not geocode and the entity ships without a map pin. After ship, `scripts/check_geocode_coverage.py <country> <city>` lists every entity that still lacks coords so you can refine the address text.

If a field is genuinely unavailable (e.g. no halal venues we'd recommend),
**leave the sub-bucket empty rather than fabricating**. The thresholds
(≥2 dietary, ≥1 dish, ≥2 cuisine) gracefully skip thin pages so the
empty array doesn't ship a low-quality page.
