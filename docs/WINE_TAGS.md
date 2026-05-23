# Cork & Curve — Wine Tag Vocabulary

Controlled vocabulary for `wines[*].tags` in every region's `wines.json`.
Every tag a research agent emits MUST come from this file. Generators
(`generate_tag_page.py`, `generate_search_index.py`, `validate_data.py`)
load this file as the source of truth and reject unknown tags so the
filter UI never breaks on free-form input.

Each tag belongs to exactly one **axis**. The user-facing filter UI
groups tags by axis. Indexing produces `/tag/<slug>/` and
`/tag/<slug>/<region>/` pages.

## How to read this file

- `slug` — what appears in `wines[*].tags`. kebab-case. Stable.
- `display` — the label shown in UI and `<h1>` of the tag page.
- `axis` — which filter group the tag belongs to.
- `derived_from` (optional) — if non-empty, the tag is computed by the
  generator from another field rather than emitted by the researcher.
  Researchers should NOT include derived tags in `tags[]` — they're
  added automatically. Listed here so the vocabulary stays exhaustive.

## Axes

1. **style** — what kind of wine it is. Single-valued per cuvée.
2. **body** — perceived weight on the palate. Single-valued.
3. **tannin** — astringency level. Single-valued. Red/orange wines only.
4. **acidity** — perceived freshness. Single-valued.
5. **sweetness** — residual sugar perception. Single-valued.
6. **pairing** — food categories the wine works with. Multi-valued.
7. **occasion** — when to drink it. Multi-valued.
8. **mood** — vibe / emotional register. Multi-valued.
9. **price** — retail price band. Single-valued, derived.
10. **ageing** — drink young vs cellar. Single-valued, derived.
11. **production** — biodynamic / organic / natural / vegan flags. Multi-valued, derived.
12. **grape** — the varietals in the cuvée. Multi-valued, derived.
13. **world** — old world vs new world. Single-valued, derived.
14. **editorial** — curatorial flags. Multi-valued.

## The vocabulary

### style (single-valued, researcher-emitted)

| slug | display |
|---|---|
| `still-red` | Still red |
| `still-white` | Still white |
| `still-rose` | Still rosé |
| `sparkling-traditional` | Traditional-method sparkling (Champagne / Cava / Franciacorta / Crémant) |
| `sparkling-tank` | Tank-method sparkling (Prosecco / Lambrusco) |
| `sparkling-ancestral` | Ancestral-method sparkling (Pet-Nat) |
| `orange` | Orange / skin-contact white |
| `dessert-late-harvest` | Late-harvest dessert |
| `dessert-noble-rot` | Botrytised (Sauternes / Tokaji / Trockenbeerenauslese) |
| `dessert-ice-wine` | Ice wine |
| `dessert-passito` | Dried-grape (passito / vin santo / Amarone) |
| `fortified-port` | Port |
| `fortified-sherry` | Sherry |
| `fortified-madeira` | Madeira |
| `fortified-marsala` | Marsala |
| `fortified-vdn` | Vin doux naturel |
| `vermouth` | Vermouth |

### body (single-valued)

| slug | display |
|---|---|
| `light-body` | Light-bodied |
| `medium-body` | Medium-bodied |
| `full-body` | Full-bodied |

### tannin (single-valued — red & orange only)

| slug | display |
|---|---|
| `low-tannin` | Low tannin |
| `medium-tannin` | Medium tannin |
| `firm-tannin` | Firm tannin |
| `high-tannin` | High tannin |

### acidity (single-valued)

| slug | display |
|---|---|
| `low-acid` | Low acidity |
| `medium-acid` | Medium acidity |
| `high-acid` | High acidity |
| `racy-acid` | Racy acidity |

### sweetness (single-valued — derived from `wines.sweetness`)

| slug | display | derived_from |
|---|---|---|
| `dry` | Dry | `sweetness=="dry"` |
| `off-dry` | Off-dry | `sweetness=="off-dry"` |
| `medium-sweet` | Medium sweet | `sweetness=="medium-sweet"` |
| `sweet` | Sweet | `sweetness=="sweet"` |
| `dessert` | Dessert | `sweetness=="dessert"` |

### pairing (multi-valued, researcher-emitted)

Coarse categories chosen to map cleanly to TableJourney food topics.
Researchers should pick all that apply, typically 2-5 per cuvée.

| slug | display |
|---|---|
| `pairs-with-red-meat` | Red meat |
| `pairs-with-game` | Game |
| `pairs-with-poultry` | Poultry |
| `pairs-with-pork` | Pork |
| `pairs-with-charcuterie` | Charcuterie |
| `pairs-with-aged-cheese` | Aged cheese |
| `pairs-with-soft-cheese` | Soft cheese |
| `pairs-with-blue-cheese` | Blue cheese |
| `pairs-with-oily-fish` | Oily fish |
| `pairs-with-white-fish` | White fish |
| `pairs-with-shellfish` | Shellfish |
| `pairs-with-oysters` | Oysters |
| `pairs-with-sushi` | Sushi |
| `pairs-with-pasta-red-sauce` | Pasta with red sauce |
| `pairs-with-pasta-cream` | Pasta with cream sauce |
| `pairs-with-pizza` | Pizza |
| `pairs-with-risotto` | Risotto |
| `pairs-with-mushroom` | Mushroom dishes |
| `pairs-with-truffles` | Truffles |
| `pairs-with-vegetable-forward` | Vegetable-forward |
| `pairs-with-salad` | Salads |
| `pairs-with-spicy-food` | Spicy food |
| `pairs-with-asian-cuisine` | Asian cuisine |
| `pairs-with-bbq` | BBQ |
| `pairs-with-burgers` | Burgers |
| `pairs-with-fried-food` | Fried food |
| `pairs-with-chocolate` | Chocolate |
| `pairs-with-fruit-desserts` | Fruit desserts |
| `pairs-with-creme-brulee` | Crème brûlée / custards |
| `pairs-with-foie-gras` | Foie gras |
| `pairs-with-aperitif` | Aperitif (no food) |
| `pairs-with-digestif` | Digestif (no food) |

### occasion (multi-valued, researcher-emitted)

| slug | display |
|---|---|
| `occasion-weeknight` | Weeknight |
| `occasion-dinner-party` | Dinner party |
| `occasion-special` | Special occasion |
| `occasion-celebration` | Celebration |
| `occasion-gift` | Gift |
| `occasion-cellar` | Cellar candidate |
| `occasion-summer` | Summer drinking |
| `occasion-winter` | Winter drinking |
| `occasion-picnic` | Picnic |
| `occasion-bbq` | BBQ |
| `occasion-aperitivo` | Aperitivo |

### mood (multi-valued, researcher-emitted)

| slug | display |
|---|---|
| `mood-easygoing` | Easygoing |
| `mood-contemplative` | Contemplative |
| `mood-romantic` | Romantic |
| `mood-festive` | Festive |
| `mood-rustic` | Rustic |
| `mood-elegant` | Elegant |
| `mood-bold` | Bold |
| `mood-refreshing` | Refreshing |
| `mood-savoury` | Savoury |
| `mood-fruity` | Fruity |
| `mood-funky` | Funky / wild |

### price (single-valued, DERIVED from `price_band`)

Derived by the generator from the lower bound of `price_band` converted
to EUR at the exchange rate snapshot. Researcher should NOT emit these.

| slug | display | derived_from |
|---|---|---|
| `price-everyday` | Everyday (under €15) | lower < 15 |
| `price-trade-up` | Trade-up (€15-30) | 15 ≤ lower < 30 |
| `price-premium` | Premium (€30-75) | 30 ≤ lower < 75 |
| `price-fine` | Fine (€75-200) | 75 ≤ lower < 200 |
| `price-luxury` | Luxury (€200-500) | 200 ≤ lower < 500 |
| `price-collector` | Collector (€500+) | lower ≥ 500 |

### ageing (single-valued, DERIVED from `drinking_window_years`)

Parses the lower + upper bound of the drinking window.

| slug | display | derived_from |
|---|---|---|
| `drink-young` | Drink young | upper ≤ 5 |
| `medium-term` | Medium-term ageing | 5 < upper ≤ 15 |
| `cellar-worthy` | Cellar-worthy | upper > 15 |

### production (multi-valued, DERIVED from producer / cuvée fields)

| slug | display | derived_from |
|---|---|---|
| `biodynamic` | Biodynamic | `biodynamic_status` in (demeter_certified, biodynamic_practicing) |
| `biodynamic-certified` | Biodynamic (Demeter-certified) | `biodynamic_status=="demeter_certified"` |
| `organic` | Organic | `organic_status` ≠ none |
| `natural` | Natural wine | `vineyards[producer].natural_wine == true` |
| `vegan` | Vegan | `vegan == true` |
| `low-sulfite` | Low-sulfite | producer flag — see SCHEMA.md dietary block |

### grape (multi-valued, DERIVED from `varietals[*].grape`)

One tag per grape, slug = kebab-case of grape name. Researcher does
NOT emit; generator builds these from `varietals[]`.

Examples: `sangiovese`, `cabernet-sauvignon`, `pinot-noir`, `riesling`,
`nebbiolo`, `chardonnay`, `merlot`, `tempranillo`, `syrah`, `garnacha`,
`gruner-veltliner`, `chenin-blanc`, `cabernet-franc`, `barbera`,
`montepulciano`, `aglianico`, `vermentino`, `albarino`, `verdejo`,
`malbec`, `carmenere`, `zinfandel`, `pinotage`.

Full list is generated at build time from every region's
`signature-grapes.json` + `vineyards[*].varietals` union, so this file
does not need to be updated when a new grape appears.

### world (single-valued, DERIVED from country)

| slug | display | derived_from |
|---|---|---|
| `old-world` | Old World | country in (France, Italy, Spain, Portugal, Germany, Austria, Greece, Hungary, Switzerland) |
| `new-world` | New World | everywhere else |

### editorial (multi-valued, researcher-emitted)

Curatorial — use sparingly. These are the high-signal flags that drive
the most-clicked filter chips.

| slug | display |
|---|---|
| `iconic` | Iconic |
| `hidden-gem` | Hidden gem |
| `value-pick` | Value pick |
| `super-tuscan` | Super Tuscan |
| `first-growth` | First growth |
| `grand-cru` | Grand cru |
| `cult-wine` | Cult wine |
| `garagiste` | Garagiste |
| `single-vineyard` | Single-vineyard |
| `old-vines` | Old vines |
| `field-blend` | Field blend |
| `library-release` | Library release |

## Adding new tags

1. Open this file, find the right axis, add a row.
2. If the axis is single-valued, document the validator constraint.
3. If derived, document the `derived_from` formula and update the
   generator that produces it.
4. Update `validate_data.py` only if the tag's axis is new (existing
   axes pick up new slugs automatically from this file).
5. Tag slugs are stable contracts — the `/tag/<slug>/` URL is canonical.
   Never rename a tag in-place; deprecate it (add `deprecated: true`),
   keep the page redirecting to whatever replaces it.
