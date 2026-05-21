# TableJourney site skeleton (locked in 2026-05-17)

This is the locked-in URL + entity + template architecture. Designed to scale
to 100k+ pages without re-plumbing. Any change to the patterns below should
be a deliberate, reviewed decision, not a drive-by edit.

## URL map (page types)

| Pattern | Page type | Generator | Template | Count at scale |
|---|---|---|---|---|
| `/` | Homepage | `generate_homepage.py` | `home.html` | 1 |
| `/<country>/<city>/` | City hub | `generate_region_page.py` | `region-template.html` | ~250 |
| `/<country>/<city>/<topic>/` | City topic page | `generate_topic_page.py` | `topics/<topic>-topic.html` | ~5,000 |
| `/<country>/<city>/<topic>/<entity-slug>/` | Entity detail | `generate_entity_pages.py` | `entity-template.html` | ~75,000 |
| `/topics/<topic>/` | Cross-city topic landing | `generate_extras.py` | `topics/<topic>-topic.html` (or chrome) | 20 |
| `/cuisine/<cuisine-slug>/` | Cross-cut: cuisine, global | `generate_cross_cuts.py` | `cross-cuts/cuisine.html` | ~50 |
| `/cuisine/<cuisine-slug>/<city-slug>/` | Cross-cut: cuisine × city | `generate_cross_cuts.py` | `cross-cuts/cuisine-city.html` | ~12,000 |
| `/dish/<dish-slug>/` | Cross-cut: dish, global | `generate_cross_cuts.py` | `cross-cuts/dish.html` | ~500 |
| `/neighborhood/<city-slug>/<hood-slug>/` | Cross-cut: neighborhood | `generate_cross_cuts.py` | `cross-cuts/neighborhood.html` | ~3,000 |
| `/cities/`, `/cuisines/`, `/dishes/`, `/neighborhoods/`, `/topics/` | Index pages | `generate_chrome_pages.py` | `chrome/page.html` | 5 |
| `/about/`, legal pages, `/search/`, `/404.html` | Chrome | `generate_chrome_pages.py` | `chrome/page.html` | ~12 |

Total at 250 cities, 20 entries per topic-with-entities × 15 such topics:
~95,000 pages. Headroom for chefs, recipes, neighbourhoods to push past 100k.

## Entity model

An "entity" is a unique real-world thing with a URL: a restaurant, cafe, bar,
brewery, market, food tour, cooking class, festival, hidden gem,
brunch/late-night/budget place, dietary venue, day-trip destination.

**Stable slug rule.** Every entity has a `slug` field in JSON. Slug is
generated once when the entry is first written, then frozen. Renaming the
entry (`name` field) does NOT change the slug. The slug is the URL forever.

If an entity needs to move to a new slug (rare): add the old slug to its
`aliases: []` list; the generator emits a `meta http-equiv=refresh` redirect
from the old path. (TODO: when we have a real backend, switch to 301s.)

**Where slug lives:** in the topic JSON next to `name`. Example:

```json
{
  "restaurants": [
    {
      "slug": "bistrot-paul-bert",
      "name": "Bistrot Paul Bert",
      "address": "18 Rue Paul Bert, 75011",
      "cuisine": "French bistro",
      ...
    }
  ]
}
```

**Topics with entities** (get per-entity pages):
restaurants, fine-dining, casual-dining, cafes, bars, street-food, breweries,
markets, food-tours, festivals, cooking-classes, budget-eating, hidden-gems,
brunch, late-night, day-trips-food, dietary (per sub-bucket).

**Topics without entities** (stay as topic page only):
signature-dishes (dishes are cross-cut, not entities), food-history,
seasonal-food (both are editorial content, not place lists).

## Slug generation rule

```python
def slugify(name: str) -> str:
    # lowercase, normalize unicode (NFKD), strip diacritics, keep [a-z0-9-]
    # collapse hyphens, strip leading/trailing hyphens
```

Already implemented as `_slugify` in `template_renderer.py` and registered as
a Jinja filter. New helper `utils.slug.slugify` exposes it to Python code
(scripts can import and call directly).

## Address rule

Every entity entry has a single canonical `address` field (string). The old
`location` field is renamed to `address` everywhere. Festivals + tours that
genuinely have no fixed address use `meeting_point` instead, which the
template renders identically.

The address renders as a clickable Google Maps directions URL:
`https://www.google.com/maps/dir/?api=1&destination=<urlencoded address + city>`.

## Schema.org coverage

| Page type | Schemas |
|---|---|
| Homepage | `WebSite` + `SearchAction` |
| City hub | `Place` + `geo` + `BreadcrumbList` + `ItemList` (topics) |
| City topic page | `CollectionPage` + `BreadcrumbList` + `ItemList` (entities) |
| Entity detail | `Restaurant`/`LocalBusiness`/`FoodEstablishment` + `BreadcrumbList` + (where present) `OpeningHours`, `PostalAddress`, `geo`, `priceRange`, `servesCuisine`, `sameAs` |
| Cross-cut landing | `CollectionPage` + `BreadcrumbList` + `ItemList` |
| Chrome | `WebPage` + `BreadcrumbList` |

`BreadcrumbList` is on EVERY non-home page. Always.

## Internal link graph rules

Every entity page links out to:
- Its city hub (parent)
- Its topic page (sibling)
- Its cuisine cross-cut (if `cuisine` is set)
- Its neighborhood cross-cut (if `neighborhood` is set)
- Each signature dish cross-cut (if `signature_dishes` is set)
- Up to 4 "more in <topic> in <city>" siblings

Every cross-cut page links to:
- Every entity that qualifies for it
- The city hubs of cities represented

Every topic page links to:
- Every entity card (now linked to its entity page)
- Related topics in same city (already there)
- Up-stream: city hub (already there)

## Template structure

```
templates/
  base.html                   # shell: head, nav, footer, JSON-LD root
  home.html                   # homepage body
  region-template.html        # city hub body
  entity-template.html        # NEW: per-entity body (parameterised)
  topics/
    _topic_base.html          # extends base.html, defines topic-page shell
    _macros.html              # ALL card macros live here. one source of truth.
    <topic>-topic.html (x20)  # each extends _topic_base, calls macros from _macros
  cross-cuts/                 # NEW
    cuisine.html              # global cuisine landing
    cuisine-city.html         # cuisine × city landing
    dish.html                 # dish landing
    neighborhood.html         # neighborhood landing
  chrome/
    page.html                 # plain chrome shell
```

**Rule:** topic templates MUST NOT inline card markup. All cards live in
`_macros.html`. Adding a new field to a card is a one-edit change.

## Backwards compatibility

- Existing URLs (`/france/paris/restaurants/` etc.) keep working unchanged.
- Entity pages are ADDITIVE; they don't remove or rename anything.
- Cross-cut pages are ADDITIVE.
- The card-macro change updates *internals* of the topic pages but their URLs
  and titles do not change. Browser bookmarks and Google's index stay valid.

## What this skeleton does NOT include (yet)

- Per-chef pages (decided: defer, low ranking value vs. cost).
- Per-recipe pages (out of scope; we are a guide, not a recipe site).
- User reviews / aggregateRating (we don't have real reviews, never fake).
- Programmatic SEO for events (festivals are once a year, low refresh value).
- A real CMS or backend (everything stays static; Caddy serves files).
