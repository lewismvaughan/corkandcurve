# Cross-linking contract: Cork & Curve ↔ TableJourney

Both sites are owned by Lewis. They are sister properties — different
verticals, complementary content, mutual referrals. The cross-linking
strategy is designed to **strengthen authority on both sides** without
triggering Google's PBN / mirror-site / footprint detection signals.

## The big rules

1. **Distinct content.** Never reuse entity descriptions verbatim across
   sites. A vineyard's description on Cork & Curve is wine-focused. The
   parent château's TableJourney listing (if it has a restaurant) is
   food-focused. Different paragraphs, different angle.

2. **Distinct visual identity.** Different palette (TJ uses a warm-red
   accent; C&C uses burgundy + cream). Different favicon. Different
   hero treatment. Templates may share macros but they should not look
   like a re-skin.

3. **Distinct legal / about / privacy / editorial pages.** Google
   detects identical boilerplate. Each site writes its own.

4. **Distinct author bylines.** Separate `Person` schemas — different
   names + email + bio (or same Person but with `worksFor`
   distinguishing the publisher Organization).

5. **No bulk reciprocal links.** Not a 50-link footer-blogroll. Footer
   mention of the sister site is fine + canonical.

6. **Editorial deep-linking only when contextual.** Don't link every
   page on TJ to every page on C&C. Link when it's actually useful to
   the reader.

## Concrete cross-link surfaces

### Footer mention (both sites)

TJ base.html footer carries (already wired):
```
<p class="tj-footer-sister">
  Drinking too? Visit
  <a href="https://corkandcurve.com/" rel="noopener">Cork &amp; Curve</a>,
  our wine and spirits travel atlas.
</p>
```

C&C base.html footer carries (already wired):
```
<p class="tj-footer-sister">
  Hungry too? Visit
  <a href="https://tablejourney.com/" rel="noopener">TableJourney</a>,
  our food travel guide.
</p>
```

Note: `rel="noopener"` not `nofollow`. These links DO pass PageRank
to the sister site, and that's the point.

### Entity-level cross-links

On C&C vineyard pages — IF the vineyard has a restaurant + that
restaurant is on TJ:
```
<a href="https://tablejourney.com/<country>/<city>/restaurants/<slug>/">
  Eat at <name> on TableJourney →
</a>
```

On TJ wine-bars topic page — IF the city has a corresponding C&C wine
region:
```
<a href="https://corkandcurve.com/<country>/<region>/">
  Plan a wine trip to <region> on Cork &amp; Curve →
</a>
```

These are auto-rendered by the generators when an entity has a
`cross_site_ref` field pointing at the sister site's slug. NOT manually
maintained per page.

### Cross-region topic page

C&C `food-pairing` topic (per-region) links to the matching TJ city
food guide. The wine-research agent populates entries like:

```json
{
  "slug": "bordeaux-red-with-entrecote",
  "pairing": "Bordeaux red blend with entrecôte à la bordelaise",
  "tablejourney_url": "https://tablejourney.com/france/bordeaux/signature-dishes/entrecote-a-la-bordelaise/",
  "wine_entities": ["chateau-margaux", "chateau-haut-brion"],
  "verified": { ... }
}
```

The TJ side reciprocally renders a "Wine pairing on Cork & Curve" block
on the dish page.

### Geographic-overlap regions

These TJ cities have direct C&C wine-region overlap and are highest-
priority cross-link targets:

| TJ city | C&C wine region |
|---|---|
| `france/bordeaux` (city) | `france/bordeaux` (wine region) |
| `italy/florence` | `italy/tuscany` |
| `spain/san-sebastian` | `spain/rioja` (nearby) |
| `spain/madrid` | `spain/ribera-del-duero` (region) |
| `portugal/porto` | `portugal/douro` (wine region) |
| `france/lyon` | `france/burgundy` / `france/beaujolais` |
| `germany/munich` | `germany/franken` / `germany/baden` |
| `austria/vienna` | `austria/wachau` / `austria/burgenland` |
| `argentina/buenos-aires` (when shipped) | `argentina/mendoza` |
| `australia/adelaide` (future TJ) | `australia/barossa` |
| `usa/san-francisco` | `usa/napa-valley`, `usa/sonoma` |
| `south-africa/cape-town` (future TJ) | `south-africa/stellenbosch` |

When these regions ship on C&C, the orchestrator (Cork-station session)
adds a "Wine trip from this city" block to the matching TJ city hub.
The TJ orchestrator (TJ-station session) does the reciprocal injection.

## How the generators handle cross-links

- `generate_region_page.py` (C&C) checks for matching TJ city via
  destination → if found, renders a "Eat in <city>" CTA in the C&C
  region hub's sidebar pointing at the TJ city.
- `generate_region_page.py` (TJ) checks for matching C&C region via
  destination → if found, renders a "Drink wine in <region>" CTA on
  the TJ city hub's sidebar.
- `generate_topic_page.py` does the same on relevant topic chapters
  (TJ wine-bars → C&C nearest region; C&C wine-bars → TJ nearest city).

The cross-link is hand-rendered (or auto-rendered from a `cross_site`
field) — NOT a bulk for-loop over every page.

## Robots / SEO sanity

- Both sites' robots.txt is open to all crawlers.
- Sitemap entries on each site only list its own URLs (don't include
  sister-site URLs in the sitemap — Google needs each property to
  declare its own).
- Use canonical tags — every page is self-canonical.
- Hreflang only if multi-language. Currently both sites are en-only.

## When this contract evolves

If we add a third sister property (e.g. craft beer, day trips), update
this doc. The same rules apply: distinct content, distinct visual,
distinct legal, editorial deep-links only.
