# QA report -- Edinburgh (Opus FINAL pass)

Date: 2026-05-19
Agent: Opus FINAL (stage 4 of 4)
Scope: united-kingdom/edinburgh
Prior passes:
- united-kingdom_edinburgh_2026-05-19.md (QA1, PASS)
- united-kingdom_edinburgh_2026-05-19_pass2.md (QA2, PASS)

---

## Scope of this pass

Per the dispatch contract, four narrow tasks:

1. Below-floor decision-making (cooking-classes 3, vegetarian 2).
2. Spot-check 10 random entities QA1+QA2 likely did not sample.
3. Final prose-echo grep for all QA1+QA2 removed slugs.
4. Production smoke test (3 URLs, price_tier render, placeholder leaks).

---

## Task 1: Below-floor decision-making

### cooking-classes (3 entries, floor 5)

All three remaining entries independently verified via own-domain own-evidence:

- `yarrow-cookery-school`: yarrowcookeryschool.com confirms active operator at 11 Longniddry Steading (18 min from Edinburgh by train). Adult, kids, teen, evening, family classes; "3-Day Course" scheduled Jan 2025; contact present (+44 7305 002 167). Restored 450-year-old steading kitchen confirmed.
- `edinburgh-food-drink-academy`: efda.co.uk confirms operator at 7 Queen Street, Edinburgh New Town. Baking, Desserts and Pastry; Children and Teens; Cookery Evenings; World Cuisine; Special Diets classes. Upcoming Baking Masterclass with Peter Sawkins May 30 2026.
- `edinburgh-food-social`: edinburghfoodsocial.org confirms active operator with public hands-on cookery classes and private/corporate sessions at 47 Peffer Place EH16 4BB (Craigmillar). Sliding-scale pricing confirmed; "stories behind our food" framing confirmed.

All retained. Below floor (3 / 5) carried forward for research backfill; not a removal trigger.

### vegetarian dietary (2 entries)

Both remaining entries independently confirmed via own-site:

- `hendersons-vegetarian`: hendersonsrestaurant.com confirms 7-13 Barclay Place, Edinburgh EH10 4HW. Vegetarian and vegan menu with Henderson Haggis, mushroom steak, oat groats risotto. Michelin 2024 + 2026 Selected Restaurant badges confirm active status.
- `david-bann-vegetarian`: davidbann.co.uk confirms 56-58 St Mary's Street, Edinburgh. Self-described as a "vegetarian all-day restaurant"; open 7 days from noon; 2023 Experts' Choice Award. Vegetarian menu confirmed.

Both retained. Below floor (2 / suggested 3) carried forward for research backfill.

---

## Task 2: Spot-check 10 random entities

Random seed 20260519 produced this sample:

| # | Slug | Topic | cuisine_evidence_url status |
|---|---|---|---|
| 1 | hula-juice-bar | cafes | FAIL: own domain hulahappy.com returns HTTP 404 at HEAD; redirects on GET to hugedomains.com parking page; no alternative live evidence findable |
| 2 | dishoom-edinburgh-brunch | brunch | PASS: dishoom.com/edinburgh confirms Bombay comfort food, 8am-11pm hours, walk-in cafe at St Andrew Square |
| 3 | lyla-fine-dining | fine-dining | PASS: Michelin guide confirms Stuart Ralston tasting counter at 30 The Shore |
| 4 | oink-budget | budget-eating | PASS: oinkhogroast.co.uk/shops/victoria-street confirms hog roast rolls, GBP 6.45-10.95 |
| 5 | howies-casual | casual-dining | PASS: howies.uk.com confirms Modern Scottish bistro, Victoria Street |
| 6 | union-of-genius-hidden | hidden-gems | UNVERIFIED: yelp.com returned 403 (anti-bot, not a fail per QA protocol). Carried forward as cuisine_unverified |
| 7 | fishers-bar-the-shore | bars | PASS: fishersrestaurants.co.uk confirms seafood at 1 The Shore Leith; "oysters" not explicitly on landing page but seafood focus confirmed |
| 8 | bross-bagels | bakeries | UNVERIFIED: edinburgh.org Forever Edinburgh listing confirms 177 Portobello High Street, Mon-Sat 09:00-16:00, Montreal-style bagels, est. 2017 |
| 9 | eating-europe-edinburgh | food-tours | PARTIAL: eatingeurope.com confirms 3-hour 5-stop tour, GBP 92, meeting point at Melville Monument; haggis + fish and chips + Scottish cheeses confirmed; "Scotch pies and whisky pairings" in JSON description not matched on page (fixed below) |
| 10 | urban-angel-brunch | brunch | PASS: urban-angel.co.uk confirms all-day breakfast and brunch at 121 Hanover Street |

### Sample-derived defects fixed

**Defect 1 (REMOVED): hula-juice-bar (cafes.json) and hula-juice-bakery (bakeries.json)**

Both entries point source_url, open_evidence_url and cuisine_evidence_url at `https://hulahappy.com/`. Direct HEAD check returns HTTP 404 (server: Kestrel); GET follows a 302 to `https://www.hugedomains.com/domain_profile.cfm?d=hulahappy.com` which is the for-sale parking page. The verify_entities.py pass-1 follows redirects and accepts the 200-OK parking page as "alive", which is the structural gap this Opus pass catches.

Attempted alternative evidence sources:
- happycow.net/reviews/hula-juice-bar-edinburgh-32812 -- 403
- tripadvisor.co.uk/...Hula_Juice_Bar_Cafe-Edinburgh -- 403
- list.co.uk/place/55193-hula-juice-bar-and-gallery -- 404
- thefork.co.uk/restaurant/hula-juice-bar-cafe-r673895 -- 403
- edinburgh.org/point-of-interest/hula-juice-cafe -- 404
- google.com / bing.com search -- anti-bot / no clean signal
- web.archive.org wayback API -- 429 rate-limited

No alternative live evidence located within budget; own-domain is dead. Per the dispatch contract ("if unverifiable, REMOVE"), both Hula entries removed.

**Defect 2 (FIXED): eating-europe-edinburgh description mentioned "Scotch pies and whisky pairings"; operator page advertises haggis with whisky marmalade, fish and chips, Scottish cheeses.**

Description rewritten to: "Eating Europe's Edinburgh food and drink tour, a three-hour guided walk through five stops covering haggis with whisky marmalade, fish and chips and Scottish cheeses in Old and New Town." Loose claim aligned with operator's own page.

---

## Task 3: Final prose-echo grep

Searched all 27 Edinburgh JSON files for the QA1+QA2 removed slugs and brand names. Slugs grepped:
- eating-europe-edinburgh-class
- edinburgh-new-town-cookery-school
- eat-walk-leith
- eat-walk-stockbridge
- henderson-of-edinburgh-veg
- hendersons-vegetarian-casual
- "Edinburgh New Town Cookery" (any case)
- "The Food Studio"
- eatwalktours / "eat walk leith" / "eat walk stockbridge"
- "Hanover.*Henderson" / "Henderson.*Hanover" (closed location)
- hendersonsofedinburgh (hijacked domain)

Found and resolved:
- `region.json` brunch.description used to read "Hula, Urban Angel, Lovecrumbs, Twelve Triangles..." Updated to "Ardfern, Urban Angel, Lovecrumbs, Twelve Triangles..." reflecting current brunch.json roster.
- `food-history.json` references "Henderson's Vegetarian Restaurant opened on Hanover Street in 1962" as historical context (1962 founding fact). QA2 E-3 explicitly cleared this as legitimate history, not a currently-open claim. No edit.

No other echoes found.

---

## Task 4: Production smoke test

All three target URLs returned 200 from the public internet:

- https://tablejourney.com/united-kingdom/edinburgh/ -> HTTP 200
- https://tablejourney.com/united-kingdom/edinburgh/restaurants/ -> HTTP 200
- https://tablejourney.com/united-kingdom/edinburgh/dietary/ -> HTTP 200

Price-tier rendering on /restaurants/: 6 entities render `£`, 5 render `££`, 17 render `£££`. No "GBP GBP" double-glyph leaks.

Placeholder/leak scan on /restaurants/: only HTML `placeholder=""` attributes on the chrome search input survived the grep; no TODO/FIXME/lorem/`{{}}` leaks.

Hula sweep on built HTML:
- /united-kingdom/edinburgh/ -- no hula matches
- /united-kingdom/edinburgh/cafes/ -- no hula matches
- /united-kingdom/edinburgh/bakeries/ -- no hula matches
- /united-kingdom/edinburgh/brunch/ -- only "Ardfern" remains in the SEO description (replaces "Hula")

Generator run pruned 2 stale entity pages (the removed Hula slugs).

---

## Changes made (JSON edits, atomic .tmp + os.replace)

1. **cafes.json**: removed `hula-juice-bar` (dead own-domain, no alternative evidence). 14 -> 13 entries.
2. **bakeries.json**: removed `hula-juice-bakery` (same dead own-domain at same address). 11 -> 10 entries.
3. **region.json**: brunch SEO description "Hula, Urban Angel, Lovecrumbs..." -> "Ardfern, Urban Angel, Lovecrumbs..."
4. **food-tours.json**: eating-europe-edinburgh description "haggis, Scotch pies and whisky pairings" -> "haggis with whisky marmalade, fish and chips and Scottish cheeses" (matches operator page).

Regen sequence run end-to-end:
- generate_city.py united-kingdom edinburgh (192 pages, 2 pruned)
- generate_cross_cuts.py (783 cross-cut pages)
- generate_extras.py
- generate_chrome_pages.py (13 chrome pages)
- generate_sitemap.py (7029 URLs)
- generate_search_index.py (7116 entries)

Permissions: `sshp host chmod -R a+rX /opt/claude-stations/tablejourney/repo/content` completed.

---

## Defects total: 4 (2 removed Hula entries, 1 ghost SEO description, 1 tour description loosening)

---

## Below-floor topics after Opus FINAL

- cooking-classes: 3 entries (validator suggests >=10 for SEO depth) -- carried forward, owner backlog
- vegetarian (dietary sub-category): 2 entries -- carried forward, owner backlog
- itineraries: 3 entries (validator suggests >=10) -- carried forward, owner backlog
- cafes: 13 entries after Hula removal (no formal floor breach noted)
- bakeries: 10 entries after Hula removal (no formal floor breach noted)

---

## Pre-existing WARNs (validator)

Carried forward from QA1 + QA2, outside Opus scope:

- seo.pages.cafes.title: 73 chars (cap 55-70)
- seo.pages.bars.title: 71 chars (cap 55-70)
- seo.pages.budget-eating.title: 71 chars (cap 55-70)
- fine-dining.json 'Fhior' must_order: 113 chars (cap 30-110)
- cooking-classes.json 'Yarrow Cookery School' description: 237 chars (cap 140-220)
- signature-dishes.json 'Haggis, neeps and tatties' make_it_yourself.tip: 184 chars (cap 60-160)
- signature-dishes.json 'Fish and chips' make_it_yourself.tip: 166 chars (cap 60-160)
- signature-dishes.json 'Deep-fried Mars bar' where_to_eat references 'Clamshell' which is not in any venue file
- itineraries.json has only 3 entries

---

## Note for verify_entities.py improvement

This pass surfaced a structural gap in pass-1: domains that redirect via 302 to parking pages (hugedomains.com, etc.) are accepted as 200-OK because the redirect target returns 200. A future enhancement would either (a) check the URL host against a known-parking-domain list (sedo, hugedomains, godaddy, dan.com, namecheap.com/domains) or (b) treat any redirect to a different second-level domain as suspect. The Hula entries are the first instance in Edinburgh of this defect class. Worth filing as a verify_entities.py enhancement.

---

## Verdict

VERDICT: PASS
