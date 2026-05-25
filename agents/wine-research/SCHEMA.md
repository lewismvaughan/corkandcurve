# Cork & Curve — Wine Research Schema

Field shapes the wine-research agent must emit per topic. Mirrors the TJ
SCHEMA.md pattern but adapted for wine vertical fields and credibility.

## Provenance block (`verified`) — MANDATORY on every entity

```json
"verified": {
  "source_url": "https://producer.com/contact",
  "address_quoted": "Verbatim address string from source_url page",
  "open_status": "open" | "seasonal" | "unknown" | "permanently_closed",
  // ^ EXACTLY one of these four. verify_entities HARD-rejects any other
  //   value (e.g. "seasonal_only", "by_appointment"). Use "seasonal" for
  //   seasonal opening, "unknown" if you cannot confirm. Note:
  //   "permanently_closed" excludes the entity from ship (drop it).
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

Iconic bottles of the region — the editorial top 8-15 per region. Each is a wine, not a venue.

Required: `slug`, `name`, `producer` (links to vineyard slug),
`varietals`, `style` (e.g. "still red Bordeaux blend"), `vintage_range`
(typical years), `price_band` (e.g. "€400-1500 at retail"), `tasting_notes`
(brief, source-cited), `verified` (source_url confirms the wine exists
+ is the iconic bottle of the producer).

Each `signature_wines[*].slug` MUST also exist as an entry in the same
region's `wines.json`. Signature-wines is a curated subset; the full
cuvée page (taste profile, pairings, history, tags) lives in
`wines.json` and is what the page at `/wine/<producer>/<slug>/` renders.

### wines (per-cuvée catalog) — the wine-page topic

Full cuvée catalog. One entry per producer cuvée, **vintage-agnostic**
(e.g. "Antinori Tignanello" not "Tignanello 2019"). Drives
`/wine/<producer-slug>/<cuvee-slug>/` pages and the global wine search.

Region scope: every wine in this file is made by a producer in the
parent region (i.e. `producer` slug resolves to a `vineyards[*].slug`
in the same region's `vineyards.json`). A cuvée appears in exactly one
region's `wines.json` — the region of its producer.

```json
{
  "slug": "tignanello",
  "name": "Tignanello",
  "producer": "marchesi-antinori",
  "producer_name": "Marchesi Antinori",
  "first_vintage": 1971,
  "varietals": [
    { "grape": "Sangiovese", "pct": 80 },
    { "grape": "Cabernet Sauvignon", "pct": 15 },
    { "grape": "Cabernet Franc", "pct": 5 }
  ],
  "style": "still-red",
  "classification": "Toscana IGT",
  "oak_regime": "14 months in French and Hungarian oak barriques, 50% new",
  "abv_typical": 14.0,
  "sweetness": "dry",
  "production_bottles_typical": 350000,
  "price_band": "€90-130 at retail",
  "drinking_window_years": "5-25 from vintage",

  "taste": {
    "aroma": ["dark cherry", "leather", "tobacco", "violets"],
    "palate": ["black plum", "dried herbs", "espresso", "cedar"],
    "body": "full",
    "tannin": "firm",
    "acidity": "high",
    "finish": "long",
    "summary": "Sangiovese-led Super Tuscan with Bordeaux structure: firm tannins, savoury herb-and-leather core, long graphite finish."
  },

  "pairings": [
    {
      "dish": "Bistecca alla fiorentina",
      "why": "The wine's grippy tannins cut through the marbling; charred crust echoes the cedar notes.",
      "tablejourney_ref": "italy/florence/restaurants/trattoria-mario"
    },
    {
      "dish": "Aged pecorino toscano",
      "why": "Crystalline sheep's-milk salt sharpens Sangiovese's red-cherry lift.",
      "tablejourney_ref": null
    },
    {
      "dish": "Wild boar pappardelle",
      "why": "Gamey ragu finds a peer in the wine's leather and dried-herb register.",
      "tablejourney_ref": "italy/florence/dishes/pappardelle-al-cinghiale"
    }
  ],

  "history": {
    "origin_year": 1971,
    "summary": "Created by Piero Antinori and Giacomo Tachis as a deliberate break from Chianti Classico DOCG rules — Sangiovese blended with Cabernet, aged in barrique. Declassified to vino da tavola at launch; the regulatory revolt birthed the Super Tuscan category and ultimately the Toscana IGT classification.",
    "milestones": [
      { "year": 1971, "event": "First vintage released as vino da tavola" },
      { "year": 1978, "event": "Cabernet Sauvignon added to the blend" },
      { "year": 1992, "event": "Toscana IGT classification created, partly in response to wines like Tignanello" }
    ]
  },

  "tags": [
    "still-red", "full-body", "high-tannin", "dry",
    "pairs-with-red-meat", "pairs-with-aged-cheese", "pairs-with-game",
    "cellar-worthy", "iconic", "super-tuscan",
    "price-luxury",
    "occasion-special", "mood-contemplative",
    "sangiovese", "cabernet-sauvignon",
    "old-world", "italy", "tuscany"
  ],

  "scores": [
    { "reviewer": "Wine Advocate", "points": 97, "vintage": 2019, "year": 2022 },
    { "reviewer": "Vinous", "points": 96, "vintage": 2019, "year": 2022 }
  ],

  "biodynamic_status": "none",
  "organic_status": "none",
  "vegan": true,

  "description": "Sangiovese-led Super Tuscan from Marchesi Antinori, first released in 1971. Bordeaux-style barrique ageing on a Tuscan backbone.",
  "editorial_score": 4.7,
  "verified": { /* required — source_url is producer or critic page that names this exact cuvée */ }
}
```

**Field rules:**

- `slug`: kebab-case; unique within the producer (not the region). Combined `producer/slug` is globally unique and drives the URL.
- `producer`: MUST resolve to a `vineyards[*].slug` in the same region.
- `varietals`: array of `{grape, pct}`. `pct` is omitted when the producer does not publicly disclose the blend (do not invent — leave the percentage off, keep the grape).
- `style`: one of the controlled `style` tag values in [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md). The single style tag is mirrored into `tags[]`.
- `sweetness`: one of `dry | off-dry | medium-sweet | sweet | dessert`.
- `classification`: exact label (DOCG / DOC / IGT / AOC / AVA / etc.). Promoting IGT to DOCG is a deal-breaker QA finding.
- `oak_regime`: free text but must be sourceable to producer technical sheet.
- `abv_typical`: float; the typical vintage. Vintage-specific ABVs are NOT recorded here — this page is vintage-agnostic.
- `production_bottles_typical`: integer; only when producer publishes it. Omit otherwise.
- `price_band`: range string; retail at primary market (€ in EU, $ in US, £ in UK, AU$ in Australia). Used to derive the `price-*` tag.
- `drinking_window_years`: string like `"3-10 from vintage"`; used to derive `cellar-worthy` vs `drink-young` tags.
- `taste.aroma` / `taste.palate`: arrays of short descriptors. Each descriptor must come from a published tasting note (producer, critic, or consortium) — `verified.cuisine_evidence_url` covers this.
- `taste.body` / `taste.tannin` / `taste.acidity`: controlled values from WINE_TAGS.md.
- `pairings`: 3-8 dish recommendations. `tablejourney_ref` is a TJ path (e.g. `italy/florence/restaurants/trattoria-mario`) when a matching TJ entity exists; `null` otherwise. The renderer turns non-null refs into outbound links to tablejourney.com per [docs/CROSS_LINKING.md](../../docs/CROSS_LINKING.md). NEVER invent TJ paths — verified at ship-time by `check_external_urls.py`.
- `history.origin_year`: 4-digit year of the first vintage of THIS cuvée (may differ from the producer's founding year).
- `history.milestones`: 1-5 dated facts. Each must be sourceable.
- `tags`: controlled vocabulary from [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md). Generators reject unknown tags. Tag taxonomy covers style / body / tannin / acidity / sweetness / pairing / occasion / mood / price / grape / world. A cuvée typically carries 10-20 tags.
- `scores`: same shape as the vineyards `scores` block. Reviewer + points + vintage + year of review are all required per entry — score without provenance is removed.
- `vegan`: boolean. True iff the producer documents no animal-derived fining agents (or it is independently certified). Default to omitting the field if unknown — do NOT default to `true`.

**Cross-reference rules:**

- Every `wines[*].producer` MUST resolve to a `vineyards[*].slug` in the same region's `vineyards.json`.
- Every `signature_wines[*].slug` MUST also exist as a `wines[*].slug` in the same region.
- Every `pairings[*].tablejourney_ref` (when non-null) must HEAD-resolve at `tablejourney.com/<ref>/` at ship-time.
- Every tag in `wines[*].tags` MUST be defined in [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md).

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

## Sister-site cross-links (TableJourney) — see docs/CROSS_LINKING.md

Contextual, follow-link cross-references to matching TableJourney food
content. Only populate when a real geographic overlap exists. NEVER bulk.

- **`region.json` → `destination.cross_site_ref`**: path (or full URL) of the
  matching TJ food city, e.g. `"france/bordeaux"`. `destination.cross_site_name`
  is that city's display name (e.g. `"Bordeaux"`). Renders an "Eat in <city> on
  TableJourney" CTA on the region hub and on the wine-restaurants / wine-bars /
  food-pairing topic pages. Leave both empty when there is no overlapping TJ
  city (most regions). Overlap matrix is in docs/CROSS_LINKING.md.
- **Venue entity (vineyard etc.) → `cross_site_ref`**: path or full URL of the
  entity's TableJourney listing, set ONLY when the estate has a restaurant (or
  other food entity) actually covered on TJ. Optional `cross_site_label`
  overrides the default "Dine at <name>" CTA text. Renders a "Dine at <name> on
  TableJourney" link on the entity page. Omit entirely otherwise.
