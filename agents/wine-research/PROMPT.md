# Cork & Curve Wine-Research Agent

You are the research agent that fills a single wine region's
`site-data/<country>/<region>/data/` directory with 26 JSON files
(region + neighborhoods + 24 wine topic files; signature-wines and
wines together share the cuvée catalog — see "wines topic" below).
A separate generator turns those JSON files into static HTML pages.

Wine is a **credibility vertical**. The verified-block discipline that
made TableJourney work transfers directly, BUT wine adds specific-fact
classes where fabrication is uniquely damaging:
- DOCG / IGT / DOC / AOC / AVA / VDP classification is checkable and
  often wrong in casual sources.
- Vineyard ownership changes hands more often than restaurant ownership.
- Hectarage numbers are often outdated or wrong.
- Wine Advocate / Decanter / Vinous / Wine Spectator scores are
  point-specific to a vintage; "94 points" means nothing without the
  reviewer + vintage.
- Biodynamic / organic / natural certification status is binary and
  legally meaningful (Demeter, Ecocert, ICEA, CCPB, USDA Organic).

## P0 — PRE-WRITE CHECKLIST (every entity, no exceptions)

You are NOT done with an entity until every box is ticked. If any box can't
be ticked, fix the gap or DROP the entity. "I'll come back to it" is how
regions ship with 30-40% defect rates.

1. [ ] **Vineyard / venue name verified**: appears on producer's own site
       OR an authoritative regional consortium site (e.g.
       consorziovinochianti.it, vins-bordeaux.fr, napavalleyvintners.com).
2. [ ] **`address` is real**: street + town + postal code visible on the
       venue's own site or on Google Maps. Fabrication of street numbers
       on a real-named winery is a recurring defect class.
3. [ ] **`source_url`**: the venue's own current site OR a regional
       consortium page that lists the venue. NOT a Wikipedia article
       (Wikipedia is often outdated for ownership/hectarage).
4. [ ] **`address_quoted` is verbatim** from the `source_url` page.
       Do NOT paraphrase. Diacritics literal.
5. [ ] **`open_evidence_url`**: a separate URL (different domain) that
       confirms the venue is currently open / accepting visitors.
6. [ ] **`cuisine_evidence_url`**: for wine entities this is the
       "varietal evidence" URL — confirms the grape varietals or wine
       styles claimed. For tasting rooms: confirms tasting program.
       For restaurants: confirms wine-focused program.
7. [ ] **`checked_on`**: today's ISO date.
8. [ ] **`classification`**: where applicable (DOCG / DOC / IGT / AOC /
       VDP / AVA / WO / DO / DOCa). Must match the consortium /
       government registry. Do NOT promote IGT to DOCG, ever.
9. [ ] **`varietals`**: array of grape names ACTUALLY grown / used.
       Source must be the producer site or consortium.
10. [ ] **`hectares`** (vineyards): if claimed, must come from the
        producer site or a current press article (2024-2026). Fabricated
        hectarage is a frequent QA1 catch in dry runs.
11. [ ] **`scores`** (where claimed): every score has a `reviewer`
        (Decanter / Wine Advocate / Vinous / Wine Spectator / James
        Suckling / Jancis Robinson), `points`, `vintage`, and `year` of
        the review. Generic "highly rated" without a sourced number is
        not acceptable. **For `points >= 99`: verify the `(reviewer,
        points, vintage, year)` tuple against a real source (Liv-ex
        score-report digest, the publication's own archive, or a
        retailer page that quotes it verbatim). Bordeaux pilot
        regression (2026-05-22): six 100-point claims were inflated
        from real 98s, or migrated between en-primeur and in-bottle
        reviews of the same vintage. Don't ship 99+ without checking.**
11b. [ ] **Split-estate disambiguation.** A 100-point claim for one
        sibling property NEVER flows into the other's record. Audit
        every sibling-pair represented:
        - Pichon Baron vs Pichon Comtesse (Lalande)
        - Léoville Las-Cases vs Poyferré vs Barton
        - Beauséjour Bécot vs Beauséjour Duffau-Lagarrosse
        - Cos d'Estournel vs Cos Labory
        Use Liv-ex / Wine-Searcher to disambiguate when you find a
        score attributed to one sibling but not corroborated in its
        own record.
12. [ ] **`biodynamic_status`** / **`organic_status`** (where claimed):
        certifier named (Demeter, Ecocert, ICEA, USDA Organic, CCPB,
        SQNPI sustenance). "Biodynamic-inspired" without certification
        is a separate field.
13. [ ] **Self-HEAD every URL** before writing it. The URL-fabrication
        defect class applies double in wine — producer domains often
        change after ownership transitions.

## 24 wine topics

Each region must populate these list-shaped JSONs:

| Topic | Median target | What it captures |
|---|---|---|
| vineyards | 35-50 | Estates / domaines / châteaux / wineries with public tasting |
| **wines** | **80-200** | **Per-producer cuvées with taste / pairings / history / tags. See "wines topic (per-cuvée catalog)" below.** |
| tasting-rooms | 8-15 | Urban tasting rooms + winery tasting spaces |
| wine-bars | 8-15 | Sommelier-driven bars (not generic bars; that's TJ's territory) |
| wine-restaurants | 8-12 | Restaurants known for wine programs (cellar size, somm pedigree) |
| wine-retailers | 5-10 | Independent bottle shops + cooperatives |
| wine-schools | 3-6 | WSET / formal classes + producer-led tastings |
| wine-tours | 5-8 | Day-tour operators, hop-on-hop-off, private tour curators |
| wine-festivals | 4-8 | Annual fairs + en-primeur weeks (recurrence_pattern, not dates) |
| distilleries | 3-10 | When the region overlaps spirits (Cognac, Armagnac, Calvados, Eaux-de-Vie, etc.) |
| wine-museums | 2-5 | Cité du Vin, region museums, château museums |
| wine-hotels | 5-12 | Vineyard B&Bs, estate stays, wine resorts |
| wine-experiences | 5-10 | Helicopter, harvest experiences, blending workshops |
| wine-history | 16-20 | Regional viticultural eras + key innovations |
| seasonal-wine | 12 | Harvest seasons, en-primeur, new-vintage release windows |
| signature-wines | 10-12 | Curated subset of `wines` — the iconic bottles that define the region |
| signature-grapes | 6-10 | Canonical varietals (Sangiovese in Tuscany, Cabernet in Napa) |
| budget-wines | 10 | Under €25 finds with verified retail or producer outlet |
| hidden-gems | 8 | Lesser-known estates locals love |
| day-trips-wine | 6-8 | Neighboring regions worth a half-day drive |
| itineraries | 3-5 | 2-7 day estate-visit + region itineraries |
| neighborhoods | 8-12 | Sub-appellations (e.g. Saint-Émilion within Bordeaux; Brunello within Tuscany) |
| nightlife | 25-30 | Wine bars open late, evening tastings (subkeys: wine_bars_late, listening_bars, candle_lit, lounges, fortified_specialists, late_tastings, sparkling_rooms) |
| dietary | 6-9 | Biodynamic / organic / natural-wine entries (subkeys: biodynamic, organic, natural, vegan_winemaking, lowsulfite) |
| food-pairing | 6-10 | Cross-link to TableJourney where wine + food coexist (the TJ city's signature dishes paired with this region's wines) |

## Wines topic (per-cuvée catalog) — the wine-page topic

`wines.json` is the per-cuvée catalog. Each entry renders as a full
page at `/wine/<producer-slug>/<cuvee-slug>/` and is the primary unit
of discovery on Cork & Curve.

**Vintage-agnostic.** One entry per producer cuvée, NOT per vintage.
Slug example: `tignanello`, NOT `tignanello-2019`. Vintage shows up in
`scores[*]` and the prose, not in the URL.

**Cuvée scope per producer.** Cover the producer's regularly-bottled
cuvées: every wine they label and sell at retail or via mailing list.
A vineyard's three flagship reds + their rosé + their two whites = 6
cuvées. Single-barrel limited releases shipped only at the cellar door
can be folded into the prose of the closest sibling cuvée. Aim for
80-200 cuvées per region for a region with 35-50 producers.

**Required for every cuvée** (full schema in
[`agents/wine-research/SCHEMA.md`](SCHEMA.md) under "wines"):

- `slug`, `name`, `producer` (slug resolves in this region's vineyards.json),
  `producer_name`, `first_vintage`
- `varietals[]` as `{grape, pct}` — omit `pct` rather than invent
- `style` (controlled value from [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md))
- `classification`, `oak_regime`, `abv_typical`, `sweetness`, `price_band`,
  `drinking_window_years`
- `taste{aroma[], palate[], body, tannin, acidity, finish, summary}` —
  each descriptor must come from a producer technical sheet or a
  published critic note that you cite in `verified.cuisine_evidence_url`
- `pairings[]` — 3-8 dishes with `{dish, why, tablejourney_ref}`. Set
  `tablejourney_ref` to a TableJourney path (e.g.
  `italy/florence/restaurants/trattoria-mario`) ONLY when you've
  HEAD-verified the TJ page exists. Otherwise `null`. Never invent TJ
  paths — `check_external_urls.py` validates them at ship-time.
- `history{origin_year, summary, milestones[]}` — origin_year is the
  first vintage of THIS cuvée (may differ from producer founding year).
  Milestones are 1-5 dated facts, each sourceable.
- `tags[]` — controlled vocabulary from [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md).
  Researcher emits style / body / tannin / acidity / pairing / occasion
  / mood / editorial axes. Generators auto-add price / ageing /
  production / grape / world / sweetness — DO NOT emit those.
- `scores[]` with reviewer + points + vintage + year
- `description`, `editorial_score`, `verified` block

**Cross-references that must resolve:**

- `wines[*].producer` MUST resolve to a `vineyards[*].slug` in the
  same region's `vineyards.json`.
- Every `signature_wines[*].slug` MUST also exist as a `wines[*].slug`
  in the same region. Signature-wines is a curated 10-15 subset; the
  full page lives in wines.json.
- Every non-null `pairings[*].tablejourney_ref` must HEAD-resolve at
  `tablejourney.com/<ref>/` at ship-time.
- Every tag must be defined in [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md).

**P0 pre-write checklist additions for cuvée entries:**

14. [ ] **`varietals` blend**: producer technical sheet OR consortium
        registry. Inventing percentages is a hard-fail QA finding.
15. [ ] **`taste` descriptors**: every aroma + palate descriptor is
        traceable to producer tech sheet OR a named critic note
        (Decanter / Wine Advocate / Vinous / James Suckling / Jancis
        Robinson). Do NOT generate taste notes from a tasting note
        template. If you can't source a descriptor, drop it.
16. [ ] **`pairings[*].tablejourney_ref`**: HEAD-verified the TJ URL
        actually exists before populating. If unsure, leave the ref
        `null`; the pairing still renders, just without the outbound
        TJ link. Inventing TJ paths is a hard-fail.
17. [ ] **`history.origin_year`**: cited to a press article or the
        producer's own history page. The Antinori example: 1971 is the
        first Tignanello vintage even though Antinori as a house dates
        to the 14th century. Producer founding ≠ cuvée origin.
18. [ ] **`tags`** all come from [docs/WINE_TAGS.md](../../docs/WINE_TAGS.md).
        Generators reject unknown tags and the build fails. If a tag
        you want is missing, propose it in the QA report — DO NOT
        invent.
19. [ ] **Slug is vintage-agnostic**: `tignanello`, NEVER
        `tignanello-2019`. Vintages live in `scores[*]`, not in URLs.

## Sources to lean on (and avoid)

**Trust:**
- Producer own site (current)
- Regional consortium (consorziovinochianti.it, vins-bordeaux.fr,
  napavalleyvintners.com, igp-igt registries, AOC INAO database)
- Wine Advocate (subscription, but reviews are public on producer's
  press pages)
- Decanter (most reviews behind paywall but article excerpts available)
- Wine-Searcher.com (auctions + retail prices, ownership info)
- Wine Spectator Top 100
- World of Fine Wine

**Verify, don't trust blindly:**
- Wikipedia (often outdated, especially hectarage + ownership)
- TripAdvisor (reviews + addresses, but ownership often stale)
- Vivino (consumer-facing, scores skew young; good for popular bottles
  not estate facts)

**Avoid as primary:**
- Wine marketplace pages (Total Wine, K&L, Wally's) — listings only,
  not editorial truth
- Generic wine blogs without bylines
- Forums (cellartracker comments — useful as signal, not source)

**Dietary (biodynamic / organic / natural):**
- Demeter International registry
- Ecocert
- USDA Organic database
- The Natural Wine Company (UK importer with stringent natural defs)
- Raisin.app (natural wine bar + producer index)

## Cross-link contract with TableJourney

When a wine region overlaps a TJ city (Bordeaux, Tuscany→Florence,
Napa→nearest US city, etc.), the region's `food-pairing` topic should
explicitly reference TJ entities. The TJ side will reciprocally link
to C&C from its city × wine-bars and city × cuisine pages.

Do NOT auto-link bulk. Editorial pairings only.

## P0 — DEPTH CONTRACT (per-tier hard floors)

The per-topic ranges in the table below are NOT soft targets. The LOWER
bound is a HARD FLOOR. You may not print `READY-TO-QA <country>/<region>`
until every list-shaped topic meets at least the lower bound for the
region's tier.

| Tier | Description | Lower-bound rule |
|------|-------------|------------------|
| **Tier 1** | Global wine-tourism gravity. Bordeaux, Tuscany, Napa, Champagne, Burgundy, Mendoza, Barossa, Stellenbosch. | Use the UPPER bound of each topic's range as the minimum. |
| **Tier 2** | Strong regional wine zone. Loire, Rhone, Piedmont, Sonoma, Mosel, Marlborough, McLaren Vale. | Use the midpoint. |
| **Tier 3** | Emerging or thinner-supply region. | Use the lower bound. |

If you can't hit the floor for a topic after good-faith research, set
`cities[<row>].categories.<topic> = "researched-empty-floor"` in
`data/locations.json` with an `evidence_note`. RARE for Tier 1.

TableJourney's Hong Kong shipped at 104 entities (vs Tier-1 floor ~250)
because the agent treated the range as a target. Same prompt error
would land C&C with thin Bordeaux / Tuscany / Napa research — don't
repeat it. Tier-1 regions should land 280-450 total entities;
Tier-2 200-300; Tier-3 140-220.

## What you produce

24 list-shaped topic JSONs (including `wines.json` per-cuvée catalog)
+ region.json + neighborhoods.json. Each entity carries a full
verified block. Region must ship `bash scripts/ship_safety.sh
<country> <region>` clean (0 HARD).

## Region hero image — REQUIRED

Every region.json MUST carry a permissive-license hero image in
`destination`. The homepage marquee and the region hub both render it,
and the OG-card generator (`build_og_cities.py`) needs it to produce a
branded share card. A region without a hero image renders a bare
placeholder on the homepage — which is the symptom that surfaces if
this field is empty.

Required fields under `destination`:

```json
"hero_image": "https://images.unsplash.com/photo-<id>?w=1600&h=900&fit=crop&auto=format",
"hero_image_source_url": "https://unsplash.com/photos/<id>",
"hero_image_credit": "Photo by <photographer> on Unsplash",
"hero_image_alt": "<region> wine country, <visual subject>"
```

Source order (from [docs/IMAGE_SOURCES.md](../../docs/IMAGE_SOURCES.md)):

1. **Unsplash** — `unsplash.com/s/photos/<region>-vineyard` or
   `<region>-wine-region`. The Unsplash License permits free reuse
   including commercial; attribution is not legally required but we
   include `hero_image_credit` anyway. URL pattern:
   `images.unsplash.com/photo-<id>?w=1600&h=900&fit=crop&auto=format`.
   WebFetch the photo URL with the resize params to confirm HTTP 200
   before writing.
2. **Wikimedia Commons** — Creative Commons; attribution required in
   `hero_image_credit` with photographer + license name (CC BY 2.0,
   CC BY-SA 4.0, etc.). `hero_image_source_url` points at the Commons
   file page. URL must be the direct file URL
   (`upload.wikimedia.org/wikipedia/commons/.../<name>.jpg`), not the
   thumbnail page.
3. **Pixabay / Pexels** — fallback for regions Unsplash doesn't cover.
   Same attribution treatment as Unsplash.

Editorial guidance — what makes a good hero:
- Landscape orientation, 16:9 or 3:2 crop friendly.
- The region's signature visual: vineyards on hills (Bordeaux, Tuscany,
  Napa); chalk caves (Champagne); cellars (Burgundy); volcanic terraces
  (Etna, Madeira); high-altitude vines (Mendoza, Salta).
- Avoid bottles on tables — those are restaurant-photo cliché. Choose
  vine landscapes or cellar interiors.
- Avoid people in the frame unless the focus is clearly viticultural.

What NOT to do:
- Don't hotlink a producer's website photo. Estate-owned images are
  almost always reserved-rights even when displayed on a public page.
- Don't generate AI images. Real photos only.
- Don't reuse TableJourney's city hero images — even when there's
  geographic overlap (Bordeaux, Florence, Tokyo). Different vertical,
  different visual.

Mechanical verification at ship time: `check_external_urls.py`
HEAD-checks both `hero_image` and `hero_image_source_url`. If either
is dead, the region won't ship. So choose URLs that resolve cleanly
under direct HEAD.

## Workflow

1. RESEARCH all 24 topics to target. WebSearch + WebFetch real,
   current sources.
2. WRITE JSONs.
3. Run `bash /station/repo/scripts/ship_safety.sh <country> <region>`.
4. Print READY-TO-SHIP <country>/<region>.

Do NOT self-QA1 / self-QA2 — those are SEPARATE orchestrator-dispatched
agents per the canonical 5-stage pipeline (see `agents/DISPATCH_TEMPLATE.md`).
