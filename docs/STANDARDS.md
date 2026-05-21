# Cork & Curve engineering standards

SEO + performance + correctness invariants every generator script and
every research / QA / orchestrator agent must respect when shipping
pages on corkandcurve.com.

Mirrors `tablejourney.com`'s STANDARDS.md in shape; deltas are
wine-vertical.

## 1. URL layout

| URL | Source | Notes |
|---|---|---|
| `/` | `content/index.html` | homepage |
| `/<country>/<region>/` | region hub | wine region (e.g. `/france/bordeaux/`) |
| `/<country>/<region>/<topic>/` | topic chapter | 24 wine topics per region |
| `/<country>/<region>/<topic>/<slug>/` | entity page | every vineyard/tasting-room/wine-bar entity |
| `/grape/<varietal>/` | grape index | global cross-cut |
| `/grape/<varietal>/<country>/<region>/` | grape × region | long-tail SEO |
| `/style/<style>/` | style index | sparkling / still / sweet / fortified / orange / natural |
| `/world/<old-world\|new-world>/` | world cross-cut |  |
| `/regions/` | all-regions index | chrome |
| `/grapes/`, `/styles/` | cross-cut indexes | chrome |
| `/sitemap.xml`, `/robots.txt` | served by Caddy as files | not template-rendered |
| `/favicon.svg`, `/favicon-32x32.png`, `/apple-touch-icon.png`, `/icon-192.png`, `/favicon.ico` | favicon set | burgundy + cream C glyph |

URLs end in `/`. Caddy serves the `index.html` inside each dir.

## 2. Schema.org graph (entity pages)

- Vineyards / wineries → `@type: Winery` (sub-type of Place) with
  `address`, `geo`, `image`, `description`, `priceRange` (where retail
  range applicable), `openingHoursSpecification` (tasting hours).
- Tasting rooms → `@type: Place` with `parentOrganization` pointing at
  the parent vineyard.
- Wine bars → `@type: BarOrPub` with `servesCuisine: "Wine focus"`.
- Wine restaurants → `@type: Restaurant` with `servesCuisine` reflecting
  food program + `additionalType` for wine focus.
- Festivals → `@type: Festival` with `startDate` derived from
  `recurrence_pattern`, `eventStatus`, `eventAttendanceMode`.
- Tours → `@type: TouristTrip` with `provider` + `departureLocation`.
- Wine schools → `@type: Course` with `provider`.
- Signature wines → `@type: Product` with `brand`, `productionDate` (vintage
  range), `aggregateRating` derived from `scores[*].points`.
- Signature grapes → `@type: Thing` with `description` + `sameAs` to
  Wikipedia + Wine Folly OR consortium pages.

Every region hub page emits a `BreadcrumbList` + an `ItemList` of the
top entities + an `Article` block with `datePublished` / `dateModified`.

## 3. Provenance block (`verified`) — mandatory

Every entity ships with the 6-key `verified` block. No verified block,
no entity. See `agents/wine-research/SCHEMA.md` for the field shape.

Pass-1 (`scripts/ship_safety.sh`) enforces:
- HEAD `source_url`, `open_evidence_url`, `cuisine_evidence_url` (alive)
- Fuzzy-match `address_quoted` ⊆ `entity.address`
- Internal cross-references resolve
- Dietary `cuisine_evidence_url` content match (biodynamic/organic
  keyword on the page)
- Festival source URL mentions `start_month`
- External URLs (`booking_url`, `affiliate_url`, `tasting_url`,
  `hero_image_source_url`) alive (anti-bot 401/403/429 → OK, not broken)
- JSON-LD schema validity

## 4. Wine-vertical correctness invariants

- Classification (DOCG/DOC/IGT/AOC/AOP/AVA/VDP/WO/DOCa) MUST match the
  producer label or consortium registry. Promotion (IGT → DOCG) is a
  deal-breaker QA finding.
- Hectarage MUST come from producer site OR a 2024-2026 press article.
  Wikipedia hectarage is often stale; do not cite without a current
  secondary check.
- Ownership MUST be current (estates change hands; LVMH/Constellation/
  Treasury Wine Estates portfolios shift yearly).
- Wine scores MUST cite reviewer + vintage + year of review. Generic
  "highly rated" without sourced number is removed by QA1.
- Biodynamic / organic certification MUST name the certifier (Demeter,
  Ecocert, ICEA, USDA Organic, CCPB, SQNPI). "Biodynamic-practicing"
  without certification is a different field.

## 5. Page performance (mirrors TJ)

- LCP < 2.5s. Hero image preload + width/height attrs to avoid CLS.
- Inline critical CSS in `<head>`. Other CSS deferred.
- Lazy-load all images below the fold (`loading="lazy"`).
- All JS deferred (`<script defer>` or DOMContentLoaded gate).
- Map (Leaflet) only loaded when a `.tj-citymap` enters viewport.

## 6. Sitemap discipline

- Sitemap-index at `/sitemap.xml`, sub-sitemaps sharded by section
  (core / regions / entities / cross-cuts) per the same pattern as TJ.
- Each URL appears EXACTLY ONCE site-wide (dedup pass at end of
  `generate_sitemap.py`).
- robots.txt is open to all crawlers including AI bots; sitemap line
  references the index URL.

## 7. Cross-linking to TableJourney

See `docs/CROSS_LINKING.md` for the full contract.

Short version:
- Footer mention on both sites (single brand + link, not a bulk
  link list)
- Editorial deep-links only when contextual (vineyard ↔ TJ city
  food page; TJ wine-bars page ↔ C&C region)
- NOT identical About / Privacy / Editorial pages on both sites
- NOT shared author bylines (separate Person schemas)
- NOT bulk reciprocal links
