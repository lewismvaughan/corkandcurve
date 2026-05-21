# TableJourney engineering standards

This doc encodes the SEO + performance + correctness invariants every
generator script and every research / QA / orchestrator agent must
respect when shipping pages. The rules are derived from real Lighthouse
+ GSC + structured-data audits; each comes with the failure mode that
motivated it.

If you are about to write a new generator, page type, or template,
**read this first.** If you are about to break a rule, document why
in the PR / commit message.

## 1. Internal linking — no orphans

**Rule:** every URL we ship must have at least one inbound link from
*page content* (not just from global header / footer / nav). When two
related pages exist (a global cross-cut and a city-scoped child), the
parent always links DOWN to the child, not UP to a wider scope.

**Why:** Google discovers + ranks pages via the link graph. An "orphan"
page in the sitemap-only state gets indexed slowly (often weeks), passes
no PageRank-equivalent, and rarely ranks. Audit on 2026-05-19 found 405
orphans (city × dish, city × cuisine, city × dietary).

**How to apply:**
- Scoped-cuisines pages (`/<country>/<city>/cuisines/`) link each cuisine
  to the city × cuisine page (`/<country>/<city>/cuisine/<slug>/`) when
  it exists, otherwise the global cross-cut.
- City signature-dishes chapter links each dish to the city × dish page
  when it exists, otherwise the global cross-cut. Handled by
  `utils/data_loader.py:_inject_entity_urls`.
- City dietary chapter wraps each diet's section heading in a link to
  the city × dietary sub-page when it exists. Handled by
  `templates/topics/dietary-topic.html`.
- Cross-link sibling sub-pages: city × dietary `vegan/` page links to
  `vegetarian/`, `gluten-free/`, etc. in the same city. Handled by
  `scripts/generate_city_dietary.py`.

**Pipeline check:** `scripts/orphan_audit.py` (run manually for now;
worth wiring into ship_city.sh as a soft fail) walks the link graph and
reports orphans grouped by page type.

## 2. Performance — Core Web Vitals must pass

**Targets:**
- LCP ≤ 2.5s on mobile, simulated 4G
- INP ≤ 200ms
- CLS ≤ 0.1
- Total Blocking Time ≤ 200ms

**Rules:**

**2a. CSS load order.** `base.css` is critical (header, hero, layout) —
load synchronously, blocking render. `theme.css` is non-critical (cards,
footer, sub-systems) — load async via the `rel=preload` + `onload` swap
pattern. See `templates/base.html`.

**2b. OG image preload.** Every page emits a `<link rel=preload as=image
fetchpriority=high href={seo.open_graph.og_image}>` in `<head>`. Cheap;
mandatory because the OG image (or its first tile on cross-cut map pages)
is often the LCP candidate.

**2c. Layout stability for dynamic UI.** Any JS-inserted DOM element
that affects layout must have its space reserved in static HTML. Maps
wrap in `.tj-citymap-wrap { min-height: 480px }` so the lazy-loaded
legend doesn't shift content below. Audited because Paris hub had CLS
0.194 before the fix.

**2d. Skip heavy JS on tiny payloads.** When a Leaflet map would show
fewer than `data-min-pins` (default 5) pins, hide the map container
instead of loading Leaflet. The card grid below already communicates the
result. Audited because a 2-pin city × cuisine page had 7.2s LCP almost
entirely from Leaflet + the first tile becoming the LCP element.

**2e. Lazy-load anything below the fold.** Static map thumbnails ship
with `loading=lazy decoding=async`. Interactive maps lazy-load Leaflet
via `IntersectionObserver` only when the container scrolls into view.

## 3. Schema — every page type carries the right structured data

| Page type | Required schema graph |
|---|---|
| Entity (Restaurant / Festival / etc) | type-specific schema + `AggregateRating` + `Review` (with `Person` author + `Organization` publisher) + `geo: GeoCoordinates` when coords cached + `BreadcrumbList` |
| City × itineraries chapter | `Article` + `HowTo` per itinerary, `HowToSection` per day, `HowToStep` per (morning/afternoon/evening) + `BreadcrumbList` |
| Festival entity | `Festival` (Event subtype) + `startDate` + `endDate` from computed next-occurrence + `AggregateRating` |
| Topic / scoped / city × dietary / city × cuisine / city × dish | `CollectionPage` + `ItemList` + `ItemListElement` per card (capped at 50) + `BreadcrumbList` |

**Rules:**
- `AggregateRating` is emitted whenever `editorial_score` is present —
  drives SERP star ratings (~15-30% CTR uplift). Required fields:
  `ratingValue`, `bestRating`, `worstRating`, `ratingCount`, `reviewCount`.
- `Review.author` is `@type: Person`, not `Organization` — Google's
  E-E-A-T framework heavily prefers Person-authored content for YMYL.
  Person has `worksFor: Organization` linking back.
- `BreadcrumbList` last position omits `item` URL (per Google spec).
- All schemas use absolute `https://tablejourney.com/...` URLs.

## 4. Slugs — stable, ASCII, hyphen-only

**Rule:** every slug matches `^[a-z0-9-]+$`. Once a slug is committed,
it never changes — if an entity renames, add the old slug to its
`aliases: []` list; the generator emits a redirect.

**Apostrophes, accents, parentheses, slashes are forbidden in slugs.**
`utils/slug.py:slugify()` normalises them all, but if an agent
hand-edits the JSON and writes `"slug": "cutty's"` the apostrophe
escapes URL handling and the page becomes uncrawlable. Audit 2026-05-19
found one of these (Boston / casual-dining / cutty-s). Fix any future
recurrence in `validate_data.py`.

## 5. Sitemap — section-sharded, honest lastmod

- `/sitemap.xml` is a `sitemapindex` pointing at section files:
  `sitemap-core.xml`, `sitemap-cities.xml`, `sitemap-entities.xml`,
  `sitemap-crosscuts.xml`. Per-section indexing stats become trivial in
  GSC.
- Per-URL `<lastmod>` reflects the file's actual `mtime`, not the build
  date. Google's crawl budget goes to pages that genuinely changed.
- Every new URL emitted by a generator must be added to the sitemap
  walker in `generate_sitemap.py`.

## 6. Geocoding — post-QA, idempotent, v3 fallback chain

- Geocoder runs in `ship_city.sh` step 2f, AFTER all QA gates pass.
  Never spend the rate-limited Nominatim budget on addresses an agent
  later corrects.
- Fallback chain (each strategy logged on the cache entry):
  canonical → venue-prefix strip → suite/unit strip → combo strip →
  postcode centroid.
- Cache lives at `data/geocode-cache.json`, committed to git so
  re-shipping is free on hits.
- Soft-fail report (`check_geocode_coverage.py`) lists addresses that
  still didn't resolve so editors can refine them. Currently soft — flip
  to `--hard --threshold 0.85` if a ship-gate becomes desirable.

## 7. Maps — interactive on discovery pages, static on detail pages

- City hub + cross-cut pages get an interactive Leaflet map (lazy-loaded).
- Entity detail pages get a static 600×400 JPEG thumbnail (no JS).
- Apple Maps + Google Maps + Waze deep-link buttons accompany every
  entity with cached coords; fall back to address-string queries
  otherwise.
- Pin colour groups (`Eat`, `Coffee & bakery`, `Drink`, `Markets &
  tours`, `Dietary`, `Day trips`) are clickable legend toggles —
  keyboard-reachable.
- Wheel zoom is OFF by default; clicking the map enables it for that
  map until cursor leaves. Don't trap page scroll.

## 8. Generation order — what runs when

`ship_city.sh france paris` chain (the contract):

1. mechanical pass-1 (validate / verify / check_internal_references)
2. QA report gate (4-stage in ship_city_full.sh)
3. geocode (post-QA, v3 chain)
4. soft coverage report
5. render city + topic pages
6. render entity pages (with AggregateRating + geo + map thumbs)
7. cross-cuts → scoped → city × dietary → city × cuisine → city × dish
8. branded OG cards
9. entity map JPEGs + city pins JSON
10. global topic pages + chrome + homepage
11. sitemap (section-sharded, honest lastmod)
12. robots + search index
13. chmod + IndexNow ping

`generate_city.py` (dev mode) runs the equivalent subset for fast
iteration. Both paths are wired in the same generators; no manual step.

## 9. When to write a new doc

Update **this doc** if you change a rule. Update
**`docs/DATA_TO_PAGES.md`** if you change what data feeds what page.
Update **`agents/food-research/PROMPT.md`** if you change what the
research agent must do.

Don't fork standards across multiple docs — the consequence is the kind
of drift that produced 405 orphan pages between Phase 1 and Phase 3.
