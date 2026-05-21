# Per-file JSON Schema (cheat sheet)

All examples are minimal; add fields where you have signal. Empty fields are fine; lying fields are not.

**Length caps**: every text field has a target character band. The full
table lives in [`agents/food-research/PROMPT.md` → "Length caps"](PROMPT.md#length-caps-hard-gates--validator-enforces-every-one).
The validator enforces them with `python3 scripts/validate_data.py
--strict`. Counts are character-of-the-decoded-string (HTML entities are
unescaped before counting). Examples in this schema show typical
lengths; if your data lands outside the cap, rewrite, don't ship.

**`editorial_score` (1.0 to 5.0) is required on every entity entry, in every file.**
Examples below show it on a handful of files; the rule applies to all of them
(restaurants, fine-dining, casual-dining, cafes, bakeries, coffee-roasters,
wine-bars, bars, street-food, breweries, markets, food-tours, festivals,
cooking-classes, dietary entries, budget-eating, hidden-gems, brunch,
late-night, day-trips-food, signature-dishes, itineraries). See the
[Editorial scoring](#editorial-scoring) section for methodology.

## Mandatory fields on every entity entry

Every place/dish/tour/class/festival/etc. entry MUST have:

- `name` (string), the public display name. Tours use `operator` instead.
- `slug` (string, kebab-case, ASCII), the stable URL identifier. Once set, it never changes.
  Generated automatically by `python scripts/inject_slugs.py` if absent. You may also
  pre-set it; ASCII-safe and unique within the topic file.
- `editorial_score` (number, 1.0 to 5.0, one decimal), the TableJourney editorial
  verdict. See [Editorial scoring](#editorial-scoring) below for methodology.
- `verified` (object), per-entity provenance proving the entity exists,
  is open, and the address/cuisine match a real source. See
  [Provenance block](#provenance-block-verified) for the schema and
  rules. Entities without a usable `verified` block fail the mechanical
  pass at `scripts/verify_entities.py` and are excluded from ship.

## Provenance block (`verified`)

Every entity ships with a `verified` block that records the URLs the
researcher actually checked. The validator and `scripts/verify_entities.py`
read this block instead of re-WebSearching at QA time, which is what makes
the QA pipeline reproducible.

```json
"verified": {
  "source_url": "https://venue-site.com/",
  "address_quoted": "84 Rue de Varenne, 75007 Paris",
  "open_status": "open",
  "open_evidence_url": "https://venue-site.com/contact",
  "cuisine_evidence_url": "https://venue-site.com/about",
  "checked_on": "2026-05-18"
}
```

| Field | Type | Required? | Notes |
|---|---|---|---|
| `source_url` | string | **required** | Venue's own primary site OR an authoritative directory entry (Michelin Guide, Time Out, Le Fooding, Eater, official tourism board). NOT Wikipedia, NOT a blog, NOT a closed-already Yelp page. If you can't find one, the entity doesn't ship. |
| `address_quoted` | string | required for fixed-venue topics | Verbatim copy-paste of the address as it appears on the source. The mechanical check fuzzy-matches this against `entity.address`; if they diverge, the entity is flagged. This catches address hallucination at source. |
| `open_status` | string | required | One of `open`, `permanently_closed`, `seasonal`, `unknown`. Anything but `open` blocks render. |
| `open_evidence_url` | string | required | URL whose content asserts the venue is open. Often `source_url` itself; but for venues whose primary site is dead, point at the directory entry or Google Maps listing that confirms operating status. |
| `cuisine_evidence_url` | string | required for venues with `cuisine` claims | URL whose content matches the cuisine/style claim. E.g. for a halal Turkish restaurant, the page must mention "halal" or "Turkish". Catches the Chez Imo defect class (correct address, wrong cuisine). |
| `checked_on` | string (YYYY-MM-DD) | required | Date the researcher verified. Older than 90 days at ship time → flagged as stale. |

### Hard rules for researchers

- **If you can't find a `source_url` for a venue, drop the venue.** Do not invent. Do not use placeholder URLs. The downstream pipeline will reject it anyway.
- **`address_quoted` MUST be a verbatim string from `source_url`.** Don't reformat, don't simplify, don't translate. If the source spells it "Rue Saint-Maur" with a hyphen, write "Rue Saint-Maur" with a hyphen. The fuzzy match tolerates whitespace and punctuation but not whole-word substitutions.
- **Use the venue's own site when possible.** It is the single best signal. Only fall back to directories when the venue has no site.
- **`open_status: "permanently_closed"`** keeps the entity in the JSON for traceability but blocks render and excludes from cross-cuts. Use this when you find evidence of closure rather than silently deleting — it documents *why* an entity was removed.

### Per-topic exceptions

- **Itineraries**: `verified` is optional, but each itinerary day MUST list `venues: [slug, ...]` — the slugs of every venue mentioned in that day's prose. Each slug must resolve to a verified entity in the same city, checked by `scripts/check_internal_references.py`. Without this, an itinerary can mention an invented venue and nothing catches it.
- **Signature dishes**: `verified` is optional (dishes are abstract), but every entry in `where_to_eat` MUST match a verified entity name in the same city (fuzzy-matched, parenthetical location qualifiers stripped). Unresolved names are ERRs. If you want to recommend a venue we haven't covered yet, add it as a verified entity first.
- **Day-trips-food**: `verified` required. `source_url` should be the destination's tourism board or a Michelin/Time Out destination guide.

### Cross-reference contract

The provenance block guarantees each entity is real. The cross-reference checker (`scripts/check_internal_references.py`) guarantees the *editorial content* that references entities never mentions one that doesn't exist:

- `signature-dishes[*].where_to_eat[*]` → each name resolves to a verified entity in the city
- `itineraries[*].days[*].venues[*]` → each slug resolves to a verified entity in the city

This closes the last gap: a research agent could write a perfectly verified entity for "Joe's Bistro" and then invent "Mary's Cafe" in a Saturday-lunch itinerary slot. The checker catches that.

`slug` becomes the URL: `/<country>/<city>/<topic>/<slug>/`. Picking a stable,
human-readable slug matters, Google indexes it. Don't include the year or anything
that will become stale.

## Editorial scoring

`editorial_score` is a number between **1.0 and 5.0**, in increments of 0.1
(so 3.7, 4.2, 4.8, etc.). It is the TableJourney editorial verdict on the entity,
informed by every signal available but **not a cached source rating**.

### How to derive a score

Triangulate the score from multiple signals, then commit to one number. Inputs:

- **External reputation** — Google, Yelp, TripAdvisor, Resy, OpenTable, Time Out,
  Le Fooding, Michelin Guide, local press, food-critic writeups. Read the
  reviews, don't just look at the star number. A 4.6-star restaurant with
  twelve reviews scores lower than a 4.3-star restaurant with two thousand.
- **Recency** — a place that was strong in 2022 but has slipped (chef left,
  ownership changed, reviewers note decline) should score lower than its
  legacy reputation suggests. Use 2024-2026 sources where possible.
- **On-the-ground reporting** — first-hand visits, local correspondents,
  trusted-eater recommendations. These outrank aggregated star averages.
- **Editorial judgment** — does the kitchen do something distinctive? Is it
  doing the canonical version of its category? How essential is it to the
  city's food scene?

### Score bands (rough guide)

- **5.0** — defining, essential, would change the city's food story if it
  vanished. Use sparingly; not every guide should have a 5.0.
- **4.5 to 4.9** — excellent. Crosses categories from "good" into "go
  out of your way for this."
- **4.0 to 4.4** — strong recommend. Reliable, well-executed, worth the visit.
- **3.5 to 3.9** — solid pick for the category. Worth knowing about.
- **3.0 to 3.4** — fine, included for coverage breadth. Often a budget pick
  or a category we have thin coverage on.
- **Below 3.0** — if a place scores this low, ask whether it should be in
  the guide at all. Better thin than weak.

### Hard rules

- **Never display or cache source ratings.** Do not write `google_rating: 4.6`
  or `yelp_score: 4.2` into JSON. Only `editorial_score` ships.
- **Commit to one number per entity.** No ranges, no "between 4.0 and 4.5."
- **One decimal place.** Not `4.25`, not `4`. Use `4.2` or `4.3`.
- **Itineraries and signature dishes get scored too.** The score on a dish
  measures how essential the dish is to the city's food story. The score on
  an itinerary measures how strong the plan is.
- **The Editorial Standards page describes the methodology publicly.** Read
  `/editorial-standards/` before scoring. The on-site description says scores
  are an editorial verdict informed by reputation, reviews, on-the-ground
  reporting and judgment, and we cache no source ratings; your scoring must
  match that promise.

## Address requirement (varies by topic)

- **Fixed venues** (restaurants, fine-dining, casual-dining, cafes, bakeries,
  coffee-roasters, wine-bars, bars, street-food, breweries, markets, brunch,
  late-night, budget-eating, hidden-gems): `address` is REQUIRED. Validator
  hard-errors if missing.
- **Roaming events** (food-tours, festivals, cooking-classes): `address` OR
  `meeting_point` is required to render a Google Maps link. Validator warns if both
  are missing.
- **Regions** (day-trips-food): no address needed. Each entry IS a place
  (Reims, Versailles); `name` carries the geography.
- **Dish entries** (signature-dishes): no address needed. They are abstract entities;
  `where_to_eat` lists restaurants instead.
- **Itineraries** (itineraries): no address needed. They are editorial content
  (day-by-day plans), not places.

`address` replaced an older `location` field across the codebase; templates still
fall back to `p.location` so legacy data keeps rendering, but new entries should
use `address`.

Do NOT add `_url` to JSON, it's computed at render time by the data loader.

---

## `region.json`

```json
{
  "destination": {
    "name": "Paris",
    "country": "France",
    "tagline": "The capital of how the world eats.",
    "overview": "1-3 sentence overview shown if food_culture_summary is missing.",
    "population": "2.1M",
    "hero_image": "https://images.unsplash.com/photo-...?w=1600&h=900&fit=crop",
    "hero_image_alt": "Parisian cafe terrace at golden hour",
    "hero_image_source": "unsplash",
    "hero_image_source_url": "https://unsplash.com/photos/...",
    "hero_image_photographer": "Photographer Name",
    "hero_image_license": "Unsplash License"
  },
  "seo": {
    "base_url": "https://tablejourney.com",
    "shared": {
      "og_image": "https://tablejourney.com/og/paris.jpg",
      "og_image_alt": "Paris food guide on TableJourney"
    },
    "geo": {
      "place_name": "Paris",
      "country_code": "FR",
      "region": "Île-de-France",
      "latitude": "48.8566",
      "longitude": "2.3522"
    },
    "pages": {
      "index": {
        "title": "Paris Food Guide: Where to Eat, Drink and Wander | TableJourney",
        "description": "An editorial Paris food guide: signature dishes, the restaurants worth a reservation, markets, hidden bistros, brunch, late-night and beyond."
      },
      "restaurants": { "title": "...", "description": "..." },
      "signature-dishes": { "title": "...", "description": "..." }
    },
    "article": {
      "author": "TableJourney Editorial",
      "published_time": "2026-01-15T00:00:00Z",
      "modified_time": "2026-05-17T00:00:00Z",
      "modified_display": "May 2026"
    },
    "alternates": []
  },
  "research": {},
  "products": [],
  "_metadata": {
    "schema_version": "tj.v1",
    "status": "draft",
    "ready_to_publish": false
  }
}
```

Per-page SEO overrides go in `seo.pages.<topic-slug>`. If absent, the generator builds a sensible default from the topic config.

---

## `city.json`

```json
{
  "food_culture_summary": "100-180 word editorial paragraph about how this city eats.",
  "peak_food_season": "September to November, plus April to June. August: many small rooms close.",
  "local_dining_hours": "Lunch 12:00-14:00, Dinner 19:30-22:30.",
  "tipping_norm": "Service is included by law. A few coins for genuinely good service is welcome, never expected.",
  "food_tagline": "Optional short tagline shown under H1 if destination.tagline missing"
}
```

---

## `neighborhoods.json`

Each editorial neighborhood feeds the city hub's "by neighbourhood" cards AND
enriches the `/neighborhood/<city>/<alias>/` cross-cut pages. `best_for_meals`
is shown as inline tags on the city hub.

```json
{
  "neighborhoods": [
    {
      "name": "Le Marais",
      "slug": "le-marais",
      "aliases": ["3e", "4e"],
      "vibe": "1-2 sentence character sketch.",
      "best_for_meals": ["Falafel", "Cafes", "Wine bars"],
      "signature_strips": ["Rue des Rosiers"]
    }
  ]
}
```

**Required fields:**
- `name` — editorial name WITHOUT parens or codes. The hub card renders
  "Le Marais (3e/4e)" by joining aliases.
- `slug` — kebab-case, used by the validator and reserved for future use.
- `aliases` — the `entity.neighborhood` values that belong to this
  editorial entry. Without aliases, the hub card can't link to a cross-cut
  page and the cross-cut keeps a bare arr-code/district name.
- `vibe` — 80–180 chars character sketch.

**How the bridge works:** entities tag `neighborhood: "3e"` (the canonical
local code). The hub card for `Le Marais` links to `/neighborhood/<city>/3e/`
because `3e` is in its `aliases`. The cross-cut page at `/3e/` adopts the
editorial display name → "Eat in Le Marais (3e), Paris".

For cities without arrondissement-style codes (most US cities), use the
editorial slug as the alias too: `aliases: ["soho"]` and have entities tag
`neighborhood: "soho"`. The bridge collapses to a single label.

---

## `restaurants.json`, `casual-dining.json`

```json
{
  "restaurants": [
    {
      "slug": "bistrot-paul-bert",
      "name": "Bistrot Paul Bert",
      "cuisine": "French bistro",
      "price_tier": "€€",  // MUST be currency symbol(s) only: $/$$/$$$/$$$$ for USD, €/€€/€€€/€€€€ for EUR, £/££/£££/££££ for GBP, ¥/¥¥/¥¥¥/¥¥¥¥ for JPY/CNY. NEVER spell out "EUR EUR" or use letters like "EE". The filter UI exposes this string verbatim as a filter chip; ASCII forms break the chip list.
      "neighborhood": "11e",
      "address": "18 Rue Paul Bert, 75011",
      "signature_dishes": ["Steak frites", "Île flottante"],
      "description": "1-3 sentence editorial pick.",
      "booking_url": "https://www.bistrotpaulbert.fr/",
      "editorial_score": 4.5
    }
  ]
}
```
Use `casual_dining` as the top-level key in `casual-dining.json`.

---

## `fine-dining.json`

```json
{
  "fine_dining": [
    {
      "slug": "arpege",
      "name": "Arpège",
      "stars": 3,
      "chef": "Alain Passard",
      "address": "84 Rue de Varenne, 75007",
      "tasting_menu_price": "€490",
      "reservation_lead_time": "4 weeks",
      "description": "...",
      "booking_url": "https://alain-passard.com/",
      "editorial_score": 4.9
    }
  ]
}
```

---

## `cafes.json`

```json
{
  "cafes": [
    {
      "slug": "telescope",
      "name": "Telescope",
      "signature_drink": "Filter coffee",
      "work_friendly": true,
      "wifi": true,
      "address": "5 Rue Villedo, 75001",
      "description": "...",
      "editorial_score": 4.2
    }
  ]
}
```

---

## `bakeries.json`

```json
{
  "bakeries": [
    {
      "slug": "du-pain-et-des-idees",
      "name": "Du Pain et des Idées",
      "specialty": "Levain breads and laminated pastries",
      "signature_item": "Escargot pistache-chocolat",
      "walk_in_only": true,
      "hours": "Mon-Fri 07:15-20:00, closed weekends",
      "address": "34 Rue Yves Toudic, 75010",
      "description": "...",
      "editorial_score": 4.7
    }
  ]
}
```

`walk_in_only` (boolean) flags counters that don't take reservations. `specialty` is a short noun phrase (bread style, pastry tradition, regional focus). `signature_item` is the one bake worth crossing town for.

---

## `coffee-roasters.json`

Coffee roasters overlap with cafes but the editorial intent is different. cafes are *places to sit*; roasters are *where the beans come from*. Some roasters have a public cafe (`has_cafe: true`) and that is worth signalling.

```json
{
  "coffee_roasters": [
    {
      "slug": "belleville-brulerie",
      "name": "Belleville Brûlerie",
      "beans_from": ["Ethiopia", "Colombia", "Burundi"],
      "brew_methods": ["Espresso", "Filter", "Whole bean retail"],
      "has_cafe": true,
      "hours": "Tue-Sat 10:00-18:00",
      "address": "10 Rue Pradier, 75019",
      "description": "...",
      "editorial_score": 4.4
    }
  ]
}
```

`beans_from` is a list of origin countries. `brew_methods` is a list of how the roaster serves (Espresso, Filter, Pour over, Whole bean retail, Subscription).

---

## `wine-bars.json`

```json
{
  "wine_bars": [
    {
      "slug": "septime-la-cave",
      "name": "Septime La Cave",
      "wine_focus": "Natural French wines, growers' Champagne",
      "food_program": "Snacks and small plates",
      "signature_pour": "Domaine Pattes Loup Chablis, by the glass",
      "hours": "Mon-Sat 16:00-23:00",
      "address": "3 Rue Basfroi, 75011",
      "description": "...",
      "editorial_score": 4.6
    }
  ]
}
```

`wine_focus` is a one-line editorial summary of what the room pours (e.g. "Natural French growers", "Burgundy by the glass", "Mediterranean orange wines"). `signature_pour` is the bottle or glass worth ordering on a first visit.

---

## `bars.json`

```json
{
  "bars": [
    {
      "slug": "le-syndicat",
      "name": "Le Syndicat",
      "type": "Cocktail bar",
      "signature_drink": "All-French-spirits cocktails",
      "food_program": "Snacks",
      "address": "...",
      "description": "..."
    }
  ]
}
```

---

## `street-food.json`

```json
{
  "street_food": [
    {
      "slug": "l-as-du-fallafel",
      "name": "L'As du Fallafel",
      "dish": "Falafel sandwich",
      "address": "34 Rue des Rosiers, 75004",
      "hours": "11:00-24:00, closed Saturday",
      "cash_only": false,
      "description": "..."
    }
  ]
}
```

---

## `breweries.json`

```json
{
  "breweries": [
    {
      "slug": "brasserie-de-la-goutte-d-or",
      "name": "Brasserie de la Goutte d'Or",
      "style": "Modern French craft",
      "taproom_hours": "Wed-Sat evenings",
      "address": "...",
      "description": "..."
    }
  ]
}
```

---

## `markets.json`

```json
{
  "markets": [
    {
      "slug": "marche-des-enfants-rouges",
      "name": "Marché des Enfants Rouges",
      "hours": "Tue-Sun, closed Mondays",
      "vendors_count": 25,
      "best_for": ["Lunch", "Moroccan", "Italian"],
      "address": "...",
      "description": "..."
    }
  ]
}
```

---

## `food-tours.json`

Tour entries use `operator` instead of `name`. Either `address` or `meeting_point`
should be present so the Google Maps link renders (validator warns if both missing).

```json
{
  "food_tours": [
    {
      "slug": "paris-by-mouth-marais-crawl",
      "operator": "Paris by Mouth",
      "route": "Marais cheese, charcuterie, wine, pastry crawl",
      "duration": "3 hours",
      "price": "€135",
      "affiliate_url": "https://parisbymouth.com/",
      "description": "..."
    }
  ]
}
```

---

## `festivals.json`

Top-level key is `food_festivals` (the URL slug is `festivals` but the JSON key
keeps the `food_` prefix). Either `address` or `meeting_point` should be present.

```json
{
  "food_festivals": [
    {
      "slug": "salon-du-chocolat",
      "name": "Salon du Chocolat",
      "month": "October",
      "day_range": "Late Oct, ~5 days",
      "focus_cuisine": "Chocolate",
      "ticket_required": true,
      "description": "...",
      "annual": true,
      "start_month": "October",
      "start_day": 28,
      "end_month": "November",
      "end_day": 1,
      "event_status": "scheduled"
    }
  ]
}
```

### Recurrence fields (required for Google Event rich-card eligibility)

The entity template emits a full `Event` JSON-LD shape (startDate/endDate/
eventStatus/eventAttendanceMode/location) only when **all** of `annual: true`,
`start_month`, and `start_day` are present. The generator computes the next
future occurrence date at render time, so the site rolls forward each year
without JSON edits.

| Field | Type | Required? | Notes |
|---|---|---|---|
| `annual` | bool | **required for Event schema** | `true` if the festival recurs every year. Set `false` (or omit) for one-offs; the page renders bare Festival schema with no fabricated dates. |
| `start_month` | string | required when `annual: true` | Full English month name (`"January"` to `"December"`). |
| `start_day` | int | required when `annual: true` | Day of month for the canonical occurrence start. Best-effort approximate is OK; festivals shift a few days year to year. |
| `end_month` | string | optional | Defaults to `start_month`. Set when the festival spans a month boundary (e.g. Salon du Chocolat = `start_month: "October"`, `end_month: "November"`). |
| `end_day` | int | optional | Defaults to `start_day` (single-day events). Set the last day for multi-day. |
| `event_status` | string | optional | One of `scheduled` (default), `cancelled`, `postponed`, `rescheduled`. Maps to schema.org `EventScheduled`/etc. |

**Skip `annual: true` entirely** for festivals where the date is genuinely
unknowable or one-off. Bare Festival schema still renders; we just don't
fabricate dates.

For **series-shaped events** (e.g. a weekly night market that runs Apr-Oct),
use `start_month: "April"`, `start_day: 1`, `end_month: "October"`,
`end_day: 31` to represent the season window as a single Event.

---

## `cooking-classes.json`

`address` is preferred (most schools operate from a fixed studio); `meeting_point`
is accepted for market-walking classes that pick up off-site.

```json
{
  "cooking_classes": [
    {
      "slug": "la-cuisine-paris",
      "name": "La Cuisine Paris",
      "cuisine_taught": "French bistro classics, baking",
      "group_size": "8 max",
      "price": "€95-195",
      "description": "...",
      "booking_url": "https://lacuisineparis.com/"
    }
  ]
}
```

---

## `dietary.json`  (DICT shape)

Each inner list entry follows the same entity rules: `slug` + `name` + `address` are
required. Entities under `dietary` render to `/<country>/<city>/dietary/<slug>/`.

```json
{
  "dietary": {
    "vegan":        [ {"slug": "abattoir-vegetal", "name": "Abattoir Végétal", "address": "...", "description": "..."} ],
    "vegetarian":   [ ... ],
    "gluten_free":  [ ... ],
    "halal":        [ ... ],
    "kosher":       [ ... ]
  }
}
```

---

## `budget-eating.json`

```json
{
  "budget_eating": [
    {
      "slug": "bouillon-chartier",
      "name": "Bouillon Chartier",
      "dish": "Three-course bistro classics",
      "price": "€12-18",
      "address": "...",
      "description": "..."
    }
  ]
}
```

---

## `signature-dishes.json`

```json
{
  "signature_dishes": [
    {
      "slug": "steak-frites",
      "name": "Steak frites",
      "description": "1-3 sentence description, sensory.",
      "history": "Origin story, dates, names.",
      "where_to_eat": ["Le Relais de l'Entrecôte", "Bouillon Chartier", "Bistrot Paul Bert"],
      "typical_price": "€18-28",
      "allergens": ["Gluten"],
      "make_it_yourself": {
        "serves": "Serves 2",
        "active_time": "PT25M",
        "total_time": "PT55M",
        "difficulty": "Easy",
        "ingredients": [
          "2 entrecôte steaks, 200 to 250g each",
          "800g floury potatoes",
          "Sea salt, black pepper",
          "..."
        ],
        "method": [
          "Step 1, complete sentence with quantities and temperatures.",
          "Step 2...",
          "..."
        ],
        "tip": "One closing sentence: a substitution, a save, an editor's caveat."
      }
    }
  ]
}
```

### Recipe field rules (`make_it_yourself`)

Optional but **strongly encouraged** for every signature dish. The site emits
schema.org `Recipe` JSON-LD from this block (Google rich-result eligible), and
renders a "Make it at home" section on the dish cross-cut at `/dish/<slug>/`.

- `ingredients` (list of strings) and `method` (list of strings) are required if
  the block is present. Both are rendered as proper lists; do not put numbers or
  bullets inside the strings.
- `serves` is a free string ("Serves 2", "Makes 16 falafel"). Schema.org calls
  this `recipeYield`.
- `active_time` (hands-on) and `total_time` (incl. resting/proving) use **ISO 8601
  duration format**: `PT25M` (25 min), `PT1H30M` (1.5 hr), `PT24H` (a day).
  The site shows them as "25 min" / "1 hr 30 min" via a Jinja filter; the
  schema.org JSON-LD uses the raw ISO.
- `difficulty` is one of `Easy`, `Intermediate`, `Advanced`. Free text is fine.
- `tip` is a single closing sentence: a substitution, a common failure mode, a
  way to scale. Skip if there is nothing useful to add.
- Recipe should be the **canonical** version of the dish (one recipe per dish,
  not per city). If two cities both feature the same dish slug, the first
  non-empty `make_it_yourself` wins.
- Editorial voice: write the recipe like a chef explaining to another cook. No
  flowery cooking prose ("lovingly crafted"), no padding ("for that perfect
  finish"). Quantities, temperatures, times, sensory cues only.

---

## `hidden-gems.json`

```json
{
  "hidden_gems": [
    {
      "slug": "chez-aline",
      "name": "Chez Aline",
      "why_hidden": "Why locals love it and tourists miss it.",
      "address": "85 Rue de la Roquette, 75011",
      "tip": "Get there by 12:30 or they're out."
    }
  ]
}
```

---

## `brunch.json`

```json
{
  "brunch": [
    {
      "slug": "holybelly-5",
      "name": "Holybelly 5",
      "style": "All-day breakfast",
      "hours": "Daily 9:00-17:00",
      "price_range": "€18-25",
      "bookings": "Walk-in only",
      "must_order": "Pancake stack with bourbon-butter and bacon",
      "address": "...",
      "description": "..."
    }
  ]
}
```

---

## `late-night.json`

```json
{
  "late_night": [
    {
      "slug": "au-pied-de-cochon",
      "name": "Au Pied de Cochon",
      "closes": "Open 24/7",
      "dish": "Onion soup, pig's trotters",
      "cash_only": false,
      "address": "...",
      "description": "..."
    }
  ]
}
```

---

## `food-history.json`  (DICT shape)

```json
{
  "food_history": {
    "key_eras": [
      { "period": "1765, the first restaurant", "summary": "..." }
    ],
    "immigrant_influences": [
      { "community": "North African (Maghrebi)", "contribution": "Couscous restaurants since the 1950s..." }
    ],
    "signature_innovations": [
      "The restaurant as a public institution",
      "Nouvelle cuisine"
    ]
  }
}
```

---

## `seasonal-food.json`  (DICT shape)

```json
{
  "seasonal_food": {
    "spring": [ { "name": "Asparagus", "note": "Both white and green at markets through April-May." } ],
    "summer": [ ... ],
    "autumn": [ ... ],
    "winter": [ ... ]
  }
}
```

---

## `day-trips-food.json`

Each entry IS a place (a town, a wine region), so no `address` field. The
geography lives in `name` + `how_to_get_there`.

```json
{
  "day_trips_food": [
    {
      "slug": "reims-champagne",
      "name": "Reims (Champagne)",
      "distance": "45 min by TGV",
      "how_to_get_there": "Train from Gare de l'Est",
      "signature": "Champagne house tastings and bistro lunches",
      "description": "..."
    }
  ]
}
```

---

## `itineraries.json`

Itineraries are editorial content (not venues), so no `address`. Each entry is a
self-contained day-by-day plan for one type of traveller. Aim for 2-4 itineraries
per city, each pitched at a different audience (e.g. weekend, family, solo, vegan,
on-a-budget).

```json
{
  "itineraries": [
    {
      "slug": "paris-weekend-classics",
      "name": "Paris weekend: the classics, done right",
      "audience": "First-time visitor, two days",
      "duration": "2 days",
      "summary": "A weekend built around the dishes Paris invented, the cafes that wrote the rulebook, and one new-classic dinner.",
      "days": [
        {
          "day_number": 1,
          "title": "Saturday: market mornings, bistro lunch, natural-wine dinner",
          "morning": "Marché Bastille at 09:00. Buy a pain au levain, eat it on the bench.",
          "afternoon": "Lunch at Bistrot Paul Bert. Steak frites, île flottante, half a bottle of house red.",
          "evening": "Wine bar at Septime La Cave from 19:00. Walk-up only.",
          "venues": ["marche-bastille", "bistrot-paul-bert", "septime-la-cave"]
        },
        {
          "day_number": 2,
          "title": "Sunday: pastry, museum lunch, late dinner",
          "morning": "Du Pain et des Idées at 08:00. Escargot pistache-chocolat and a filter coffee.",
          "afternoon": "Lunch at Café Flore on Boulevard Saint-Germain. Croque-monsieur, glass of Sancerre.",
          "evening": "Dinner at Clamato, 20:30. Plates of oysters, lardo, hake.",
          "venues": ["du-pain-et-des-idees", "cafe-flore", "clamato"]
        }
      ]
    }
  ]
}
```

`audience` is a short editorial phrase (e.g. "First-time visitor, weekend",
"Family with kids", "Vegan, three days", "On a budget"). `duration` is a free
string ("Weekend", "3 days", "Long weekend"). `days` is an ordered list. Each
day has `day_number` (1-indexed), `title`, three meal-windows (`morning`,
`afternoon`, `evening`), and a **required `venues` list of slugs** for every
venue named in that day's prose. Day count must match `duration`.

`scripts/check_internal_references.py` verifies every slug in `venues` resolves
to a verified entity elsewhere in the same city. A venue mentioned in prose but
absent from `venues` will not be caught automatically; the rule is "if it
appears in the prose, it goes in `venues`". This is what prevents itineraries
from referencing invented venues.

Itineraries are not place entries; they have no `address`, do not need
`hero_image`, and are not aggregated by the cuisine or neighborhood cross-cuts.
They render to their own URL: `/<country>/<city>/itineraries/<slug>/`.

---

## Naming conventions

- File names use hyphenated slugs (`street-food.json`, `day-trips-food.json`).
- Top-level keys inside each file use snake_case (`street_food`, `day_trips_food`).
- This split is intentional: URL slugs match file names, template-facing keys match Python conventions.
