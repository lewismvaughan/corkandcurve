# Cork & Curve — data to pages

Every JSON field maps to a downstream HTML surface. This doc tells
the research agent + future-me which fields are HIGH-LEVERAGE (drive
many pages) vs nice-to-have.

## Region-level (`region.json`)

```
{
  "destination": {
    "slug": "bordeaux",
    "name": "Bordeaux",
    "country": "France",
    "country_slug": "france",
    "type": "wine-region",
    "hero_image": "https://...",
    "hero_image_source_url": "https://unsplash.com/...",
    "blurb": "Short region intro paragraph",
    "lat": 44.84,
    "lng": -0.58
  },
  "seo": {
    "pages": {
      "vineyards": "Top vineyards in Bordeaux: 24 producer-direct picks for 2026",
      "tasting-rooms": "Bordeaux tasting rooms guide ...",
      ...
    }
  },
  "faqs": [...]
}
```

| Field | Drives |
|---|---|
| `destination.name` | h1 + title + meta + JSON-LD Place name |
| `destination.country_slug` | URL path component |
| `destination.hero_image` | hero on region hub + OG image (when no per-page override) |
| `destination.blurb` | first paragraph on region hub |
| `destination.lat/lng` | region centroid for map default + geocoding sanity check |
| `seo.pages.<topic>` | per-topic chapter meta description |
| `faqs[]` | FAQPage JSON-LD on region hub + visible accordion |

## Vineyard entity

```
{
  "slug": "chateau-margaux",
  "name": "Château Margaux",
  "address": "Margaux 33460, France",
  "neighborhood": "Margaux AOC",
  "varietals": ["Cabernet Sauvignon", "Merlot", "Cabernet Franc", "Petit Verdot"],
  "classification": "Premier Cru Classé (1855)",
  "hectares": 99,
  "owner": "Mentzelopoulos family",
  "winemaker": "Philippe Bascaules",
  "founded": 1572,
  "tasting_program": "By appointment only ...",
  "booking_url": "https://chateau-margaux.com/visites",
  "signature_wines": ["chateau-margaux", "pavillon-rouge", "pavillon-blanc"],
  "scores": [{ "reviewer": "Wine Advocate", "points": 100, "vintage": 2016, "year": 2019 }],
  "biodynamic_status": "none",
  "organic_status": "none",
  "description": "First-growth Bordeaux at Margaux AOC ...",
  "tip": "Visits book out months ahead.",
  "editorial_score": 4.9,
  "verified": { ... required ... }
}
```

| Field | Drives |
|---|---|
| `slug` | URL: `/<country>/<region>/vineyards/<slug>/` |
| `name` | h1 + JSON-LD `@type: Winery` name |
| `address` | Place / PostalAddress in JSON-LD + map pin + Apple/Google deep-links |
| `neighborhood` | `/<country>/<region>/neighborhoods/<slug>/` cross-cut |
| `varietals[]` | `/grape/<varietal>/` cross-cut + region × grape cross-cut |
| `classification` | classification chip in byline + JSON-LD additionalProperty |
| `hectares` | byline detail + JSON-LD `Place.area` |
| `owner` | byline detail + Winery `sameAs` (when sourced) |
| `founded` | byline detail + JSON-LD `foundingDate` |
| `tasting_program` | details grid |
| `booking_url` | CTA button + JSON-LD `Reservation.url` |
| `signature_wines[]` | cross-link to signature-wines pages in same region |
| `scores[]` | aggregateRating + Review JSON-LD |
| `biodynamic_status` | `/dietary/biodynamic/` cross-cut + dietary chip |
| `organic_status` | `/dietary/organic/` cross-cut |
| `editorial_score` | star rating + sort key for filter widget |
| `verified` | mechanical pass-1 gate |

## Signature wine

```
{
  "slug": "chateau-margaux-grand-vin",
  "name": "Château Margaux Grand Vin",
  "producer": "chateau-margaux",
  "varietals": ["Cabernet Sauvignon-dominant blend"],
  "style": "still red Bordeaux blend",
  "vintage_range": "2010-2018",
  "price_band": "€600-1500 retail",
  "tasting_notes": "Cassis + cedar + tobacco; vintage variance...",
  "verified": { ... }
}
```

`producer` MUST resolve to a vineyard slug in the same region. The
generator renders the signature-wine page with a back-link to that
producer.

## Tasting room

```
{
  "slug": "max-bordeaux",
  "name": "Max Bordeaux Wine Gallery",
  "address": "14 Cours de l'Intendance, 33000 Bordeaux",
  "varietals_focus": ["Bordeaux reds", "white Bordeaux"],
  "pricing": "€30-50 per 3-pour flight",
  "walk_in": true,
  "appointment_required": false,
  "parent_vineyard": null,  // urban gallery, not a single producer
  "description": "Curated Bordeaux flight gallery ...",
  "verified": { ... }
}
```

If `parent_vineyard` is set, the generator cross-links to that vineyard.

## Festival

```
{
  "slug": "bordeaux-fete-le-vin",
  "name": "Bordeaux Fête le Vin",
  "recurrence_pattern": "biennial, June even years",
  "start_month": "June",
  "duration": "4 days",
  "host_organization": "Bordeaux Convention Bureau + CIVB",
  "ticket_required": true,
  "ticket_url": "https://www.bordeaux-fete-le-vin.com/",
  "featured_producers": ["chateau-margaux", "chateau-haut-brion"],
  "description": "...",
  "verified": { ... }
}
```

`recurrence_pattern` + `start_month` together drive a Festival JSON-LD
with a `startDate` derived for the next occurrence each generator run.

## Day-trip-wine (cross-region cross-cut)

```
{
  "slug": "saint-emilion-half-day",
  "name": "Saint-Émilion right bank",
  "distance_km": 40,
  "travel_time": "45 min by car",
  "recommended_vineyards": ["chateau-cheval-blanc", "chateau-ausone"],
  "signature_pours": ["Saint-Émilion Grand Cru Classé"],
  "verified": { ... }
}
```

`recommended_vineyards` slugs must resolve in `france/saint-emilion`'s
vineyards.json (or wherever the cross-region target is). The generator
renders the day-trip card with cross-region links.

## Cross-site (food-pairing)

```
{
  "slug": "bordeaux-red-with-entrecote",
  "pairing": "Bordeaux red blend with entrecôte à la bordelaise",
  "tablejourney_url": "https://tablejourney.com/france/bordeaux/signature-dishes/entrecote-a-la-bordelaise/",
  "wine_entities": ["chateau-margaux"],
  "verified": { "source_url": "https://tablejourney.com/...", ... }
}
```

`tablejourney_url` is treated as an `external_url` by ship_safety —
HEAD-checked alive at ship time.

## Topic-by-topic page coverage

| Topic | Pages produced per region | What renders |
|---|---|---|
| vineyards | 1 chapter + N entity pages | grid of vineyard cards + per-vineyard detail |
| tasting-rooms | 1 chapter + N entities | as above |
| wine-bars | 1 chapter + N entities | bar-card variant |
| wine-restaurants | 1 chapter + N entities | restaurant-card variant |
| wine-retailers | 1 chapter + N entities | retailer-card |
| wine-schools | 1 chapter + N entities | course-card + Course JSON-LD |
| wine-tours | 1 chapter + N entities | tour-card + TouristTrip JSON-LD |
| wine-festivals | 1 chapter + N entities | festival-card + Festival JSON-LD |
| distilleries | 1 chapter + N entities | distillery-card |
| wine-museums | 1 chapter + N entities | museum-card |
| wine-hotels | 1 chapter + N entities | hotel-card (Hotel JSON-LD) |
| wine-experiences | 1 chapter + N entities | experience-card |
| wine-history | 1 chapter | era cards + immigration influences + innovations |
| seasonal-wine | 1 chapter | season-by-season prose |
| signature-wines | 1 chapter + N detail pages | wine-card (Product JSON-LD) |
| signature-grapes | 1 chapter + N detail pages | grape-card + key-producers cluster |
| budget-wines | 1 chapter | under-€25 finds |
| hidden-gems | 1 chapter | locals-only producers |
| day-trips-wine | 1 chapter + N entities | cross-region day-trip cards |
| itineraries | 1 chapter + N detail pages | multi-day plans with embedded HowTo JSON-LD |
| neighborhoods | 1 index page | sub-appellation cards |
| nightlife | 1 chapter + 7 subkey pages | per-subkey grids |
| dietary | 1 chapter + 5 subkey pages | per-subkey grids |
| food-pairing | 1 chapter | cross-link blocks to TJ |
