# Cork & Curve templates audit

Forked from TJ. Each template's wine-vertical readiness state.

Legend: ✅ ready · 🟡 adapt · 🔴 rewrite

## Top-level

| Template | Status | Notes |
|---|---|---|
| `base.html` | 🟡 | Brand rebrand done (sed pass). Navigation links + footer carry. Body container OK. Hero block expects food fields; topic-specific blocks override. |
| `region-template.html` | 🟡 | Forked from TJ region-template. h1 + structured-data block + sidebar. Topic loops use TJ keys (research.restaurants, research.signature_dishes). Adapt to wine keys (research.vineyards, research.signature_wines). |
| `entity-template.html` | 🟡 | Per-entity page. Conditional sections (`{% if entity.cuisine %}`, `{% if entity.chef %}`) → need wine equivalents (`{% if entity.varietals %}`, `{% if entity.classification %}`, `{% if entity.scores %}`). |

## Topic templates

| Template | Status | Notes |
|---|---|---|
| `_topic_base.html` | 🟡 | Shared topic-chapter base. Filter widget + topic_sections block carry. _ent_list expression has TJ topic-key list — adapt to wine keys. |
| `_macros.html` | 🔴 | Card macros — `place_card`, `festival_card`, `class_card`, `tour_card`, `market_card`. ALL are food-vertical. Need wine equivalents: `vineyard_card`, `tasting_room_card`, `wine_bar_card`, `wine_restaurant_card`, `signature_wine_card`, `signature_grape_card`, `festival_card` (wine festivals), `tour_card`, `school_card`, `museum_card`, `hotel_card`, `experience_card`. |
| `restaurants-topic.html` | 🔴 | TJ topic. Wine equivalent: `wine-restaurants-topic.html`. |
| `cafes-topic.html` | 🔴 | Drop (no equivalent in wine). |
| `bars-topic.html` | 🔴 | Replace with `wine-bars-topic.html`. |
| `bakeries-topic.html` | 🔴 | Drop. |
| `brunch-topic.html` | 🔴 | Drop. |
| `fine-dining-topic.html` | 🔴 | Drop (folded into wine-restaurants). |
| `street-food-topic.html` | 🔴 | Drop. |
| `wine-bars-topic.html` | 🟡 | Already wine-shaped on TJ! Carries over almost as-is. Just review pour-list field names. |
| `breweries-topic.html` | 🔴 | Wine analog: `distilleries-topic.html` (overlap regions only). |
| `markets-topic.html` | 🔴 | Wine: `wine-retailers-topic.html`. |
| `food-tours-topic.html` | 🟡 | Wine: `wine-tours-topic.html`. Card macro adapts; topic schema (TouristTrip) carries. |
| `cooking-classes-topic.html` | 🟡 | Wine: `wine-schools-topic.html`. Card macro adapts; Course schema carries. |
| `festivals-topic.html` | 🟡 | Wine: `wine-festivals-topic.html`. Festival JSON-LD already added. Reuse. |
| `food-history-topic.html` | 🟡 | Wine: `wine-history-topic.html`. Eras/influences/innovations structure works. |
| `seasonal-food-topic.html` | 🟡 | Wine: `seasonal-wine-topic.html`. Season-by-season structure works. |
| `signature-dishes-topic.html` | 🔴 | Wine: `signature-wines-topic.html` AND `signature-grapes-topic.html` (two separate topics). |
| `itineraries-topic.html` | 🟡 | Wine: `itineraries-topic.html`. Multi-day structure works. |
| `hidden-gems-topic.html` | 🟡 | Same. |
| `day-trips-food-topic.html` | 🟡 | Wine: `day-trips-wine-topic.html`. |
| `late-night-topic.html` | 🔴 | Drop. |
| `coffee-roasters-topic.html` | 🔴 | Drop. |
| `casual-dining-topic.html` | 🔴 | Drop. |
| `budget-eating-topic.html` | 🟡 | Wine: `budget-wines-topic.html`. |
| `nightlife-topic.html` | 🟡 | Wine: `nightlife-topic.html` — subkey structure works, swap subkeys. |
| `dietary-topic.html` | 🟡 | Wine: `dietary-topic.html` — subkey structure works (biodynamic/organic/natural instead of vegan/halal/kosher). |
| `neighborhoods-topic.html` | 🟡 | Sub-appellation listing. Works as-is structurally. |

## Partials

| Template | Status | Notes |
|---|---|---|
| `partials/_ad_slot.html` | ✅ | Generic ad slot. Same on both sites. |
| `partials/_breadcrumb.html` | ✅ | Generic. |
| `partials/_meta_seo.html` | ✅ | Title / OG / Twitter / hreflang. Generic. |

## Cross-cut templates

| Template | Status | Notes |
|---|---|---|
| `cross-cut/*` | 🔴 | TJ has /cuisine/<x>/, /dish/<x>/, /neighborhood/<city>/<x>/ patterns. Wine analogs: /grape/<x>/, /style/<x>/, /world/<x>/. New cross-cut templates needed. |

## What "🟡 adapt" really means here

Per-template:
1. Open the template
2. Find Jinja `{% if entity.cuisine %}` / `entity.chef` / `entity.must_order` / `entity.signature_dishes` (food fields)
3. Replace with wine equivalents (`entity.varietals` / `entity.winemaker` / `entity.scores` / `entity.signature_wines`)
4. For 🔴 rewrites, copy the structure from the closest TJ analog and re-skin

## Order of work

1. `_macros.html` — write the wine card macros first; everything else
   depends on them
2. `entity-template.html` — single-entity page
3. `_topic_base.html` — topic chapter base
4. Per-topic templates (top-priority: vineyards, wine-bars, signature-wines,
   wine-festivals, wine-tours, wine-schools)
5. Cross-cut templates (grape/, style/, world/)
6. Region-template.html (sidebar + topic loops)

## Time estimate

~3-4 hours of focused work to bring all templates to first-region-ready.
Recommend doing this work in the Cork station after the next session
boots up, before dispatching the first wine-research agent.
