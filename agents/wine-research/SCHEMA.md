# Cork & Curve — Wine Research Schema

Field shapes the wine-research agent must emit per topic. Mirrors the TJ
SCHEMA.md pattern but adapted for wine vertical fields and credibility.

## Provenance block (`verified`) — MANDATORY on every entity

```json
"verified": {
  "source_url": "https://producer.com/contact",
  "address_quoted": "Verbatim address string from source_url page",
  "open_status": "open" | "permanently_closed" | "seasonal_only",
  "open_evidence_url": "https://different-domain.com/listing",
  "cuisine_evidence_url": "https://consortium.org/page-mentioning-varietals",
  "checked_on": "YYYY-MM-DD"
}
```

Every entity ships with this block or it's dropped. `source_url` and
`open_evidence_url` MUST be different domains.

## Common wine entity fields

| Field | Shape | Notes |
|---|---|---|
| `slug` | string | kebab-case unique within region |
| `name` | string | venue / vineyard name; diacritics literal |
| `address` | string | street + town + postal |
| `neighborhood` | string | sub-appellation or village |
| `description` | string | 80-220 chars; no em/en dashes |
| `editorial_score` | float 1.0-5.0 | TJ-style internal score |
| `varietals` | array[string] | grape names (Cabernet Sauvignon, etc.) |
| `classification` | string | DOCG/DOC/IGT/AOC/AVA/etc. — exact match required |
| `hectares` | float | only when source-verified |
| `owner` | string | producer / owning family / corporate parent |
| `winemaker` | string | head winemaker if named in current press |
| `founded` | int (year) | 4-digit year |
| `biodynamic_status` | string | "demeter_certified", "biodynamic_practicing", "none" |
| `organic_status` | string | "usda_organic", "ecocert", "icea", "ccpb", "none" |
| `natural_wine` | bool | low/no intervention, minimal sulfites |
| `tip` | string | insider note |

## Per-topic specifics

### vineyards (estates / domaines / châteaux / wineries)

```json
{
  "slug": "chateau-margaux",
  "name": "Château Margaux",
  "address": "Margaux 33460, France",
  "neighborhood": "Margaux AOC",
  "varietals": ["Cabernet Sauvignon", "Merlot", "Cabernet Franc", "Petit Verdot"],
  "classification": "Premier Cru Classé (1855 classification)",
  "hectares": 99,
  "owner": "Mentzelopoulos family",
  "winemaker": "Philippe Bascaules",
  "founded": 1572,
  "tasting_program": "By appointment only; 90-min tour + flight, €120",
  "booking_url": "https://chateau-margaux.com/visites",
  "signature_wines": ["Château Margaux", "Pavillon Rouge du Château Margaux", "Pavillon Blanc"],
  "scores": [
    { "reviewer": "Wine Advocate", "points": 100, "vintage": 2016, "year": 2019 },
    { "reviewer": "Vinous", "points": 99, "vintage": 2018, "year": 2021 }
  ],
  "biodynamic_status": "none",
  "organic_status": "none",
  "description": "First-growth Bordeaux at Margaux AOC, 1572-founded estate currently owned by the Mentzelopoulos family. Classical Cabernet-dominant blends with century-long ageing.",
  "editorial_score": 4.9,
  "verified": { /* required */ }
}
```

### tasting-rooms

Urban tasting rooms + winery tasting spaces.

Required fields: `slug`, `name`, `address`, `neighborhood`, `varietals_focus`,
`pricing` (per flight or per hour), `walk_in` (bool), `appointment_required`
(bool), `verified`. Optional: `parent_vineyard` (links to a vineyard slug
if this is the urban tasting room of a producer).

### wine-bars

Sommelier-driven bars. Different from TJ's "wine_bars" topic which is
food-vertical; here the bar's by-the-glass list IS the menu.

Required: `slug`, `name`, `address`, `wine_program` (string describing the
list size + focus), `glass_count`, `verified`. Optional: `signature_pours`,
`sommelier_name` (only with press-source).

### wine-restaurants

Restaurants known for wine programs — cellar size, somm pedigree, James
Beard / Wine Spectator Award of Excellence holders.

Required: `slug`, `name`, `address`, `cuisine` (food-pairing focus),
`cellar_size` (bottle count if claimed), `awards` (array, each with
`source` + `year`), `verified`.

### wine-festivals

Annual fairs + en-primeur weeks. Recurrence patterns, NOT specific dates.

Required: `slug`, `name`, `recurrence_pattern` (e.g. "annual, late October",
"biennial, June even years"), `start_month`, `duration`, `host_organization`,
`signature_pours` or `featured_producers`, `ticket_required` (bool),
`verified`.

### signature-wines

Iconic bottles of the region. Each is a wine, not a venue.

Required: `slug`, `name`, `producer` (links to vineyard slug),
`varietals`, `style` (e.g. "still red Bordeaux blend"), `vintage_range`
(typical years), `price_band` (e.g. "€400-1500 at retail"), `tasting_notes`
(brief, source-cited), `verified` (source_url confirms the wine exists
+ is the iconic bottle of the producer).

### signature-grapes

Canonical varietals. Each is a grape, not a venue.

Required: `slug`, `name`, `style_focus` (red / white / rosé / sparkling /
fortified), `regions_grown` (array of related region slugs), `description`
(history, flavor profile, where it grows best in this region), `key_producers`
(array of vineyard slugs), `verified` (source_url is a wine reference site).

### day-trips-wine

Neighboring regions worth a half-day drive.

Required: `slug`, `name`, `distance_km`, `travel_time`, `signature_pours`,
`recommended_vineyards` (array of vineyard slugs in the neighboring region
— must exist in another region's vineyards.json), `verified`.

### itineraries

2-7 day estate-visit + region itineraries.

Required: `slug`, `name`, `length_days`, `days` (array of `{morning, lunch,
afternoon, evening, dinner, accommodation}`), `theme` (e.g. "First-growth
Médoc weekend"), `verified` (each venue referenced must resolve to a
verified entity in the same region's other topic JSONs).

### food-pairing

Cross-link to TableJourney. For wine + food intersections.

Required: `slug`, `pairing` (e.g. "Bordeaux red + entrecôte"),
`tablejourney_url` (link to the TJ entity or topic page), `wine_entities`
(array of vineyard/signature-wine slugs), `verified` (TJ URL HEAD-resolves).

## Nightlife (nested) — wine-night-out angles

```json
"nightlife": {
  "wine_bars_late": [ ... ],
  "listening_bars": [ ... ],     // vinyl + wine pairing rooms
  "candle_lit": [ ... ],
  "lounges": [ ... ],
  "fortified_specialists": [ ... ],  // port/madeira/sherry/marsala rooms
  "late_tastings": [ ... ],
  "sparkling_rooms": [ ... ]     // champagne/cava/franciacorta-only bars
}
```

## Dietary (nested) — wine-specific angles

```json
"dietary": {
  "biodynamic": [ ... ],          // demeter-certified estates
  "organic": [ ... ],
  "natural": [ ... ],             // raisin.app / sav-vin / pet-nat focus
  "vegan_winemaking": [ ... ],    // no animal-derived fining
  "lowsulfite": [ ... ]
}
```

## What you DO NOT fabricate

- Vineyard hectarage. Get it from the producer's own About page or a
  recent consortium fact-sheet. Wikipedia hectarage is frequently stale.
- Vineyard ownership. Changes hands often (Constellation, LVMH, Treasury
  Wine Estates, Gallo, Pernod Ricard portfolios shift yearly).
- Classification level (DOCG vs DOC vs IGT). The producer's own bottle
  label OR the INAO/consortium registry is the only acceptable source.
  Promoting IGT to DOCG is a deal-breaker QA finding.
- Wine scores. Always tie to a `reviewer` + `vintage` + `year of review`.
  "Highly rated" without a sourced number is removed.
- Biodynamic / organic status. The certifier MUST be named. "Biodynamic-
  inspired" without certification is `biodynamic_practicing`, not
  `demeter_certified`.

## Cross-reference rules (mirrors TJ contract)

- `signature_wines[*].producer` slug MUST resolve to a `vineyards[*].slug`
  in the same region.
- `day_trips_wine[*].recommended_vineyards` slugs must resolve to
  vineyards in the OTHER region's data dir.
- `itineraries[*].days[*].venues` slugs must resolve to verified
  entities in the same region's other topic JSONs.
- `food_pairing[*].tablejourney_url` must be a real TJ URL (will be
  validated by `check_external_urls.py` at ship-time).
