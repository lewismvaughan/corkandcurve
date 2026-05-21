# TableJourney city roadmap

**This doc explains the editorial reasoning** for which cities ship in what
order. The machine-readable state (which city is queued/researching/shipped)
lives in [`data/locations.json`](../data/locations.json). The orchestrator
loop semantics live in [docs/ORCHESTRATOR.md](ORCHESTRATOR.md).

When you scaffold or ship a city, update `data/locations.json`. When you
re-order priorities, edit BOTH this doc (the human reasoning) and
`data/locations.json` (the machine state).

## Site language

**English only.** All editorial copy is written in English (British spelling
per [agents/food-research/PROMPT.md](../agents/food-research/PROMPT.md)).
There is no multi-language plan. Don't translate dish names, neighbourhood
names, or place names; render them in their native form (Latin script only,
with diacritics preserved, e.g. "Soufflé au Grand Marnier", "Bistrot Paul
Bert"). For non-Latin scripts (Japanese, Chinese, Korean, Thai, Arabic,
Hebrew, etc.), use the standard romanisation (Hepburn for Japanese, Pinyin
for Mandarin) plus a one-time gloss in parentheses on first mention.

OG locale is hardcoded `en_US` in every generator. `<html lang="en">` in
`base.html`. RSS feed declares `<language>en</language>`. If we ever add
real multi-language coverage it will be a separate, deliberate project.

## Priority order

We work the United States first, then EU countries, then rest of world.
Within each tier, ordered by food-search-volume and editorial gravity.

### Tier 1 - United States (do these first)

The US is the highest-value market for ad rates, the largest English food
audience, and the deepest local-search demand. All other tiers wait until
Tier 1 is at least 80% complete.

| Order | Country slug | City slug | Display name | Status |
|---|---|---|---|---|
| 1 | `united-states` | `new-york-city` | New York City | not scaffolded |
| 2 | `united-states` | `los-angeles` | Los Angeles | not scaffolded |
| 3 | `united-states` | `san-francisco` | San Francisco | not scaffolded |
| 4 | `united-states` | `chicago` | Chicago | not scaffolded |
| 5 | `united-states` | `new-orleans` | New Orleans | not scaffolded |
| 6 | `united-states` | `austin` | Austin | not scaffolded |
| 7 | `united-states` | `portland` | Portland (Oregon) | not scaffolded |
| 8 | `united-states` | `seattle` | Seattle | not scaffolded |
| 9 | `united-states` | `boston` | Boston | not scaffolded |
| 10 | `united-states` | `miami` | Miami | not scaffolded |
| 11 | `united-states` | `nashville` | Nashville | not scaffolded |
| 12 | `united-states` | `houston` | Houston | not scaffolded |
| 13 | `united-states` | `philadelphia` | Philadelphia | not scaffolded |
| 14 | `united-states` | `washington-dc` | Washington DC | not scaffolded |
| 15 | `united-states` | `charleston` | Charleston (SC) | not scaffolded |
| 16 | `united-states` | `las-vegas` | Las Vegas | not scaffolded |
| 17 | `united-states` | `san-diego` | San Diego | not scaffolded |
| 18 | `united-states` | `atlanta` | Atlanta | not scaffolded |
| 19 | `united-states` | `minneapolis` | Minneapolis | not scaffolded |
| 20 | `united-states` | `denver` | Denver | not scaffolded |

Country slug is `united-states` (full name, matches the `france` / `japan`
pattern already in `site-data/`). If you ever want `us` instead, change it
across this doc, every directory, and every `seo.geo.country_code` field.

### Tier 2 - European Union and adjacent (after US is mostly done)

Order within Tier 2 is broadly by food-tourism volume. Adjust freely.

**France** (Paris is the worked example, already shipped):
1. `france` / `lyon` (done? no - not scaffolded)
2. `france` / `marseille`
3. `france` / `nice`
4. `france` / `bordeaux`
5. `france` / `strasbourg`

**Italy:**
1. `italy` / `rome`
2. `italy` / `florence`
3. `italy` / `bologna`
4. `italy` / `naples`
5. `italy` / `milan`
6. `italy` / `venice`
7. `italy` / `palermo`

**Spain:**
1. `spain` / `madrid`
2. `spain` / `barcelona`
3. `spain` / `san-sebastian`
4. `spain` / `seville`
5. `spain` / `valencia`

**Portugal:**
1. `portugal` / `lisbon`
2. `portugal` / `porto`

**United Kingdom & Ireland** (English-speaking, lower SEO leverage than
non-English EU but high traffic):
1. `united-kingdom` / `london`
2. `united-kingdom` / `edinburgh`
3. `ireland` / `dublin`

**Germany:**
1. `germany` / `berlin`
2. `germany` / `munich`
3. `germany` / `hamburg`

**Netherlands / Belgium / Denmark / Sweden / Norway / Austria:**
- `netherlands` / `amsterdam`
- `belgium` / `brussels`
- `denmark` / `copenhagen`
- `sweden` / `stockholm`
- `norway` / `oslo`
- `austria` / `vienna`

**Mediterranean + Central Europe:**
- `greece` / `athens`
- `czech-republic` / `prague`
- `hungary` / `budapest`
- `poland` / `warsaw`
- `croatia` / `split`

### Tier 3 - Rest of world (after Tier 2)

Order: Japan -> rest of Asia -> Mexico + Latin America -> Australia + NZ
-> Canada -> Middle East -> Africa.

- `japan` / `tokyo` (stub already exists, deferred)
- `japan` / `osaka`, `kyoto`, `fukuoka`
- `thailand` / `bangkok`
- `singapore` / `singapore`
- `hong-kong` / `hong-kong`
- `south-korea` / `seoul`
- `vietnam` / `hanoi`, `ho-chi-minh-city`
- `taiwan` / `taipei`
- `mexico` / `mexico-city`, `oaxaca`
- `peru` / `lima`
- `argentina` / `buenos-aires`
- `brazil` / `sao-paulo`
- `australia` / `sydney`, `melbourne`
- `canada` / `toronto`, `montreal`, `vancouver`
- `turkey` / `istanbul`
- `israel` / `tel-aviv`
- `morocco` / `marrakech`
- `south-africa` / `cape-town`

This is a starter list. Lewis edits freely; once a city's `site-data/`
dir exists, the priority shifts to "finish that one" no matter where in the
tier list it sits.

## Already shipped

| Country | City | Status |
|---|---|---|
| France | Paris | live, worked example |

## Stub-only (scaffolded, not filled)

| Country | City | Why deferred |
|---|---|---|
| Japan | Tokyo | Pre-US-priority leftover. Stays as stub; refill after Tier 1 complete. |

## Launching a city

Standard flow (from [PIPELINE.md](PIPELINE.md)):

1. Scaffold: `python scripts/new_city.py <country> <city> --name "<Name>" --country "<Country>"`
2. Run the food-research subagent against the new data dir
   ([prompt](../agents/food-research/PROMPT.md))
3. `bash scripts/ship_city.sh <country> <city>` to validate + render +
   chmod for Caddy

The subagent's quality gate runs `validate_data.py` to exit 0. The
post-render gate is `validate_seo.py`. Both have hard ERRs on em-dashes and
placeholder text.

## Subagent dispatch rules

- One subagent per city. Subagents do not coordinate; they each write to
  their own `site-data/<country>/<city>/data/` dir.
- Lewis decides batch size. Recommend 1 city for the first launch (to
  validate the pipeline end to end on a US city), then 2-3 at a time.
- Each subagent must finish a city to `validate_data` exit 0 before
  declaring done. WARNs are OK to defer.
- After every city ships, run `python scripts/generate_cross_cuts.py` and
  the chrome/sitemap/search-index refresh from `PIPELINE.md` step 8.

## Out of scope (do not work on these without explicit asks)

- Per-chef pages
- Per-recipe pages outside the `make_it_yourself` block on signature dishes
- Multi-language anything
- User reviews or aggregateRating
