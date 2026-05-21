# Cork & Curve — site skeleton

The complete URL inventory + page-type breakdown. Helps future-me
visualize what content exists / will exist + how URLs nest.

## Chrome / global pages

| URL | Source generator | Purpose |
|---|---|---|
| `/` | `generate_homepage.py` | Site homepage (currently a placeholder; richer once first regions land) |
| `/regions/` | `generate_chrome_pages.py` | All-regions index |
| `/grapes/` | `generate_chrome_pages.py` | Grape varietal index |
| `/styles/` | `generate_chrome_pages.py` | Style index (sparkling/still/sweet/fortified/orange/natural) |
| `/world/` | `generate_chrome_pages.py` | Old World vs New World |
| `/about/` | `generate_chrome_pages.py` | About page |
| `/about/editorial/` | static | Editorial standards |
| `/contact/` | static | Contact |
| `/privacy/`, `/terms/`, `/cookies/`, `/disclaimer/` | static | Legal |
| `/search/` | static | Client-side search UI |
| `/topics/` | `generate_chrome_pages.py` | Topic landing index |
| `/sitemap.xml`, `/sub-sitemap-*.xml`, `/robots.txt` | `generate_sitemap.py` + `generate_robots.py` | Crawler files |

## Country-level pages

| URL | Source | Purpose |
|---|---|---|
| `/<country>/` | `generate_country_stubs.py` (or fuller country index when 2+ regions exist) | Country wine overview |
| `/<country>/<topic>/` | `generate_country_topic.py` | Country × topic rollup (e.g. all `vineyards` in `france`) |
| `/<country>/grape/<varietal>/` | `generate_country_grape.py` | Country × grape rollup |

## Region-level pages

| URL | Source | Purpose |
|---|---|---|
| `/<country>/<region>/` | `generate_region_page.py` | Region hub (24 topics + map + signature wines + grapes + dishes pairings) |
| `/<country>/<region>/<topic>/` | `generate_topic_page.py` | Topic chapter |
| `/<country>/<region>/<topic>/<slug>/` | `generate_entity_pages.py` | Per-entity page |
| `/<country>/<region>/grape/<varietal>/` | `generate_region_grape.py` | Region × grape ("Sangiovese in Tuscany") |
| `/<country>/<region>/cellars/` | scoped cross-cut | Sub-appellation breakdown |
| `/<country>/<region>/neighborhoods/` | `generate_region_page.py` | Sub-appellation index |
| `/<country>/<region>/dietary/<diet>/` | `generate_city_dietary.py` (adapt for wine) | Biodynamic / organic / natural |
| `/<country>/<region>/nightlife/<sub>/` | `generate_city_nightlife_sub.py` (adapt) | Wine bars late, listening bars, etc. |
| `/<country>/<region>/itineraries/<slug>/` | `generate_region_page.py` (inline) | Multi-day plans |

## Global cross-cuts

| URL | Source | Purpose |
|---|---|---|
| `/grape/<varietal>/` | `generate_global_top_topics.py` (adapt) | All regions for one grape |
| `/grape/<varietal>/<country>/<region>/` | scoped cross-cut | Specific grape in a region |
| `/style/<style>/` | scoped cross-cut | Sparkling / still / sweet / etc. across regions |
| `/world/old-world/`, `/world/new-world/` | scoped cross-cut | World category index |
| `/wineries/`, `/tasting-rooms/`, `/wine-bars/`, etc. | `generate_global_top_topics.py` | Top topic indexes |

## Entity-page anatomy (mirrors TJ)

Every vineyard / tasting-room / wine-bar / etc. detail page renders:

1. Hero — name + score + tagline + verified date badge + breadcrumb back
2. Byline — type, neighborhood (sub-appellation), classification, hectares
3. JSON-LD `@graph` — Winery / BarOrPub / Restaurant / Festival / Course / Product schema as appropriate
4. Details grid — varietals, classification, hectarage, owner, winemaker, founded year, tasting program, booking
5. Description + tip + signature wines list
6. Map (when geocoded) — Apple/Google/Waze deep-links
7. "Also in this sub-appellation" cross-link block
8. Related entities (other vineyards in same varietal cluster, etc.)
9. Sidebar — related topics, cross-link to TJ city food page (if applicable), book a flight CTA

## Topic chapter anatomy

1. Hero + breadcrumb
2. ToC sidebar
3. Topic intro paragraph
4. Filter + sort widget (when >=8 entities) — same shared widget as TJ
5. Entity grid (cards via macros)
6. Topic sections (per macro by topic type)
7. "Open now" badges client-side
8. FAQ schema (when populated)
9. Related topic links
10. Sidebar — plan your eating/drinking trip, browse across regions

## What's currently rendering

| Surface | Status |
|---|---|
| `/` homepage | placeholder rendering (burgundy single-page) |
| favicon set | rendering (svg + 4 PNGs + ICO) |
| `/robots.txt` | rendering |
| `/sitemap.xml` | rendering (homepage-only stub) |
| All other surfaces | NOT YET — need first region research + generator adaptations |

## Page-count projection (per docs/HANDOFF.md)

100 wine regions × ~200 pages each ≈ 20,000 pages. Plus global cross-cuts
(grape, style, world) ≈ 1,000-1,500 pages. Plus spirits if folded in
later ≈ +5,000-10,000.
