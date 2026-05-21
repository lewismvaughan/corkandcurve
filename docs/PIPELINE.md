# TableJourney Pipeline

End-to-end flow for taking a city from idea to live on tablejourney.com.

The site is **live as of 2026-05-17**. There is no separate deploy step:
Caddy on the host reads `content/` straight from disk and serves it at
`https://tablejourney.com/`. Any change to `content/` is public on the next
HTTP request (after the chmod step below). See `CLAUDE.md` for hosting layout.

**Site language: English only.** No multi-language plan; do not introduce
locale/translation fields. Hardcoded `en_US` OG locale, `<html lang="en">`,
`<language>en</language>` in the feed. See
[CITY_ROADMAP.md](CITY_ROADMAP.md) for the per-city priority order
(United States first, then EU, then rest of world).

---

## Quick reference: one command per city

```
bash scripts/ship_city.sh <country_slug> <city_slug>
```

That runs every step below in order. Use the long form if you want to inspect
each phase, or if something blew up and you need to re-enter mid-pipeline.

---

## 1. Scaffold the data tree

```
python scripts/new_city.py <country_slug> <city_slug> --name "<Name>" --country "<Country>"
# example: python scripts/new_city.py italy rome --name Rome --country Italy
```

Creates `site-data/<country>/<city>/data/` with 23 empty-but-shaped JSON files.
Idempotent on re-run (will not clobber filled files unless `--force`).

## 2. Run the food-research agent

Brief: [agents/food-research/PROMPT.md](../agents/food-research/PROMPT.md).
Schema: [agents/food-research/SCHEMA.md](../agents/food-research/SCHEMA.md).

The agent fills the 23 JSON files. Editorial voice, SEO rules, the
`make_it_yourself` recipe block on signature dishes, the slug + address
requirements on every entity, and the **zero em/en dashes** rule are all baked
into the prompt.

## 3. Finalise slugs + addresses

```
python scripts/inject_slugs.py <country_slug> <city_slug>
```

Idempotent. Walks every entity-bearing topic file and:

- Injects a stable `slug` field on entries that lack one (unicode-aware,
  collision-free within the file). These slugs become permanent URLs
  (`/<country>/<city>/<topic>/<slug>/`), so the agent can either pre-set them
  or let this script generate them.
- Renames legacy `location` → `address` where present.

## 4. Validate the JSON

```
python scripts/validate_data.py --city <city_slug>
```

Hard gates:

- Required files exist, JSON parses
- Topic lists are non-empty and above minimum entry counts
- Every entity has `slug` + `name` + `address` (or `meeting_point`)
- No placeholder text (TODO, TBD, FIXME, XXX, Lorem ipsum, "placeholder")
- SEO essentials present (title, description, geo)
- Signature dishes: warns if `make_it_yourself` is missing (recipes are
  strongly encouraged; warning is not a blocker but should not be ignored)

Iterate until exit 0.

## 5. Render the city's HTML

```
python scripts/generate_city.py <country_slug> <city_slug>
```

Outputs:
- `content/<country>/<city>/index.html` (city hub)
- `content/<country>/<city>/<topic>/index.html` (one per topic)

## 6. Render the per-entity pages

```
python scripts/generate_entity_pages.py <country_slug> <city_slug>
```

For each entry in restaurants / cafes / bars / fine-dining / casual-dining /
brunch / late-night / breweries / street-food / markets / food-tours /
festivals / cooking-classes / dietary / budget-eating / hidden-gems /
day-trips-food, emits `/<country>/<city>/<topic>/<slug>/index.html` with full
schema.org type, breadcrumbs, and a Google Maps directions link.

## 7. Refresh cross-cut landings

```
python scripts/generate_cross_cuts.py
```

Walks every city and re-emits `/cuisine/<slug>/`, `/dish/<slug>/`,
`/neighborhood/<city>/<slug>/`. Dish pages pick up the `make_it_yourself`
block and emit a schema.org `Recipe` block. Run after any new city or
content change.

## 8. Refresh chrome, homepage, search index, sitemap, feed, OG images

```
python scripts/generate_extras.py          # cross-city topic pages + 404 + feed + /og/<city>.jpg + /logo.png
python scripts/generate_chrome_pages.py    # /about/, /cities/, /cuisines/, /dishes/, /neighborhoods/, /topics/, legal pages
python scripts/generate_homepage.py        # /index.html (featured cities, trending dishes)
python scripts/generate_sitemap.py         # walks content/ for every URL
python scripts/generate_robots.py
python scripts/generate_search_index.py
```

Re-run any of these whenever the underlying data set changes. They are all
idempotent and fast.

## 9. Make new files world-readable (Caddy)

```
sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content'
```

Caddy runs on the host as the `caddy` user. Without this step, newly created
files 404 silently for the public even though they exist on disk.

## 10. Audit the rendered HTML

```
python scripts/validate_seo.py
```

Hard gates (ERR):
- Any em/en dash in body copy (banned, treat as build break)
- Any placeholder string in body copy (TODO, lorem ipsum, unrendered Jinja, etc.)
- Missing canonical, missing OG image, broken JSON-LD
- Legacy `/destinations/` or `opentravelguide` strings

Or run the [SEO-validator agent](../agents/seo-validator/PROMPT.md) for a
deeper editorial pass on a city.

## 11. Smoke-test the live URLs

```
sshp host 'curl -sSI https://tablejourney.com/<country>/<city>/ | head -3'
sshp host 'curl -sS -o /dev/null -w "%{http_code}\n" https://tablejourney.com/<country>/<city>/restaurants/<slug>/'
```

Both should return `200`. If the hub returns 200 but an entity returns 404,
re-run the chmod step.

---

## File layout reference

```
templates/
  base.html                    single root all templates extend
  home.html                    homepage
  region-template.html         city hub
  entity-template.html         per-entity detail
  chrome/page.html             about, cities, legal, etc.
  topics/
    _topic_base.html           shared chrome for all 20 topics
    _macros.html               card macros (place_card, dish_card, title_link, address_link)
    <topic>-topic.html         one per food topic
  cross-cuts/
    cuisine.html               /cuisine/<slug>/
    dish.html                  /dish/<slug>/  (includes Recipe schema + Make it at home)
    neighborhood.html          /neighborhood/<city>/<slug>/
  partials/
    _ad_slot.html              the only place ad markup lives

content/css/
  base.css                     layout, components, responsive, recipe styles
  theme.css                    auto dark mode + finishing touches

scripts/
  new_city.py                  scaffold a city's JSON files
  inject_slugs.py              finalise slug + rename location -> address
  validate_data.py             JSON validator (run before render)
  generate_region_page.py      render one city hub
  generate_topic_page.py       render one or all topic pages
  generate_city.py             one-shot: hub + all topics
  generate_entity_pages.py     per-entity detail pages
  generate_cross_cuts.py       /cuisine/, /dish/, /neighborhood/ landings
  generate_extras.py           cross-city topic pages + 404 + feed.xml + /og/*.jpg + /logo.png
  generate_chrome_pages.py     /about/, /cities/, /cuisines/, /dishes/, /neighborhoods/, /topics/, legal
  generate_homepage.py         /index.html
  generate_sitemap.py          walk content/, write sitemap.xml
  generate_robots.py           write robots.txt
  generate_search_index.py     walk site-data, write search-index.json
  validate_seo.py              HTML validator (run after render)
  ship_city.sh                 one-shot wrapper that runs the full chain
  utils/
    template_renderer.py       Jinja env + context prep + filters
    data_loader.py             JSON file loaders + _url injection
    slug.py                    unicode-aware slugify + unique_slug

agents/
  food-research/PROMPT.md      city onboarding agent brief
  food-research/SCHEMA.md      per-file JSON cheat sheet (recipes documented)
  seo-validator/PROMPT.md      post-render auditor brief

site-data/
  home.json                    featured cities + trending dishes for /
  <country>/<city>/data/       23 JSON files per city

content/                       served directly by Caddy. never hand-edited
  index.html, sitemap.xml, robots.txt, logo.png, feed.xml
  og/default.jpg, og/<city>.jpg
  <country>/<city>/index.html
  <country>/<city>/<topic>/index.html
  <country>/<city>/<topic>/<slug>/index.html
  cuisine/<slug>/index.html
  dish/<slug>/index.html
  neighborhood/<city>/<slug>/index.html
```

## Ad slot taxonomy

Every ad slot is rendered via `templates/partials/_ad_slot.html`. To wire a real ad network later:

1. Pick the network (AdSense, Mediavine, Freestar, etc.).
2. Update `_ad_slot.html` to set `data-tj-ad-network="<network>"`.
3. Add a small bootstrap script that queries `document.querySelectorAll('[data-tj-ad-slot]')` and mounts the appropriate unit into `[data-tj-ad-mount]`.
