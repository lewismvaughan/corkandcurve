# TableJourney — operational flow (2026-05-19)

This is the playbook I (Claude) follow when shipping changes to
tablejourney.com. Future-me: read this before doing anything below.

## TL;DR

| Scenario | Command(s) |
|---|---|
| Fill missing topics in a shipped city | dispatch research agent (scoped to empty topics) → QA1 → QA2 → Opus → `cleanup_broken_urls.py` → `ship_safety.sh` → `generate_city.py` → chmod |
| Build a new city from scratch | `new_city.py` (scaffold) → research → QA chain → ship_safety → `generate_city.py` → chmod |
| Hotfix a single defect | edit JSON (atomic) → `ship_safety.sh` → `generate_city.py` → chmod |
| Site-wide structural change | edit script → regen all 28 cities in a loop → `generate_extras.py` → `generate_search_index.py` → chmod |

`generate_city.py` now auto-runs `generate_sitemap.py` + `indexnow_ping.py`
at the end (added 2026-05-19). Don't re-run those manually after a city
regen.

## The full flow, expanded

### 1. Research dispatch

For filling EMPTY TOPICS in a shipped city:

- Use `Agent` tool, `subagent_type: "general-purpose"`, `run_in_background: true`
- Brief tightly: "Read `/station/repo/agents/food-research/PROMPT.md`",
  list ONLY the empty topic files, "DO NOT touch other files"
- Cite the top-of-prompt 11-item PRE-WRITE CHECKLIST as the contract
- For Tokyo-style full builds: pass `new_city.py` step as part of the agent's job

Typical sub-agent budget: 100-300k tokens per city. Tokyo's full build
took ~380k.

### 2. QA chain (per city)

Dispatch sequentially per city, all via `Agent` with
`run_in_background: true`:

1. **QA1** (general-purpose, default model): scope to NEW entries only.
   Brief with `agents/qa/PROMPT.md` and the Section A2 sub-classes.
2. **QA2** (general-purpose, default model): same scope, "different
   angle" — focus on what QA1 likely missed (independent-directory
   address cross-check, itinerary editorial sweep, day-of-week × hours).
3. **Opus final** (general-purpose, `model: "opus"`, MEDIUM thinking in
   the prompt text): safety net for what only end-to-end reading catches
   — cross-entry contradictions, itinerary prose specific-facts,
   sibling-credit borrowing, multi-gen ownership drift.

Each pass writes its findings to
`agents/qa/reports/<country>_<city>_<YYYY-MM-DD>.md` under its own
section.

**Closed-loop prompt updates** are mandatory: after each QA returns,
scan for NEW defect classes (not yet documented in PROMPT.md). Harvest
into:

- `agents/food-research/PROMPT.md` — for prevention at write-time
- `agents/qa/PROMPT.md` — so future QA passes look for the class
- Sometimes `scripts/verify_entities.py` or `check_external_urls.py`
  if it's structurally detectable (e.g. US state name normalization,
  504 anti-bot, compound strasse handling)

Don't ship a city until the chain is complete OR Opus returns 0.
Ideally Opus returns 0; non-zero means QA1/QA2 punted.

### 3. URL hygiene

Before ship_safety, run `cleanup_broken_urls.py`:

```bash
python3 scripts/cleanup_broken_urls.py --country <c> --city <s>
```

Strips dead URL fields (404/410/451/ERR) from `booking_url`,
`affiliate_url`, `hero_image_source_url`. Preserves transient (5xx,
anti-bot 401/403/405/429). Idempotent.

### 4. ship_safety gate

```bash
bash scripts/ship_safety.sh <country> <city>
```

Seven mechanical layers. Common failures and fixes:

| Failure | Cause | Fix |
|---|---|---|
| Layer 4 (check_evidence_content) MISS on dietary | Page text doesn't mention cuisine word | Find a HappyCow/Zabihah/Atly URL; or add synonym to `DIETARY_SYNONYMS` in `check_evidence_content.py` |
| Layer 6 (check_external_urls) BROKEN | OpenTable/booking site timed out | Re-run `cleanup_broken_urls.py` first; if persistent, edit JSON to drop booking_url |
| Layer 6 single URL 500/504 | Transient server (Williams-Sonoma, jimbochoden) | Already in anti-bot allowlist as of 2026-05-19 |
| Layer 2 (verify_entities) HARD addr_mismatch | German strasse compound, US state name vs abbreviation | Already in normalizer as of 2026-05-19 |
| Layer 1 (validate_data) ERR empty topic | Topic list is `[]` | Research never filled — go back to research step |

**Gotcha**: piping ship_safety output through `tail -N` swallows the
exit code. Use `set -o pipefail` or capture exit code separately.
Don't trust `&&` after a piped ship_safety call.

### 5. Regenerate HTML

```bash
python3 scripts/generate_city.py <country> <city>
```

Renders city hub + 24 topic pages + entity pages. **Auto-runs**:
- `generate_sitemap.py` (refresh full-site sitemap)
- `indexnow_ping.py --city <c> <s>` (Bing/Yandex re-crawl signal)

For site-wide structural changes (template change, OG-image logic
change, etc.) loop over all 28 cities:

```bash
for cdir in /station/repo/site-data/*/; do
  country=$(basename "$cdir")
  [ "$country" = "README.md" ] && continue
  for citydir in "$cdir"*/; do
    [ -d "$citydir" ] || continue
    city=$(basename "$citydir")
    [ -f "$citydir/data/region.json" ] || continue
    python3 /station/repo/scripts/generate_city.py "$country" "$city" > /dev/null 2>&1
  done
done
# then regen the cross-cut topic pages (/topics/<slug>/) too:
python3 /station/repo/scripts/generate_extras.py > /dev/null 2>&1
# and the country/city scoped cross-cuts (/<country>/cuisines/,
# /<country>/<city>/neighborhoods/, etc.) — depends on cross_cuts manifests:
python3 /station/repo/scripts/generate_cross_cuts.py > /dev/null 2>&1
python3 /station/repo/scripts/generate_scoped_cross_cuts.py > /dev/null 2>&1
python3 /station/repo/scripts/generate_sitemap.py > /dev/null 2>&1
```

`generate_extras.py` produces `/topics/<slug>/` global cross-cut pages
and is NOT triggered by `generate_city.py`. Run it manually after any
template change that touches those pages.

`generate_scoped_cross_cuts.py` produces country + city scoped indexes
(`/united-states/cuisines/`, `/france/paris/neighborhoods/`, etc.) and
MUST run after `generate_cross_cuts.py` (reads its enriched manifests)
and before `generate_sitemap.py` (so scoped URLs ship to Google).
`ship_city.sh` chains all three in order automatically.

### 6. Chmod (Caddy needs world-read)

```bash
sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content'
```

The sudo prompt always echoes "[sudo] password for lewis:" to stderr
even when the password pipes correctly — that's NOT a failure signal.

Without this, new files 404 silently for the public.

### 7. Verify live

```bash
sshp host 'curl -sSI https://tablejourney.com/<country>/<city>/ | head -3'
```

## Background-agent ops

**Agent dispatch tooling**:
- `subagent_type: "general-purpose"` for all research + QA passes
- `model: "opus"` ONLY for the Opus final pass (cost trade-off)
- `run_in_background: true` for parallel work; sequential dispatch
  blocks the orchestrator
- Multiple `Agent` calls in ONE message = true concurrency

**Background-agent lifecycle**: bg agents DIE if the parent session
ends. Partial JSON survives on disk; agent process is killed. Budget
session lifetime accordingly. For Tokyo-scale (~50 min single-agent),
consider sequential dispatch instead of fan-out.

**Sub-agent prompt structure** (works well):
- 1 paragraph: who they are + what they're doing
- "SCOPE — STRICT" section listing exact files to touch / not touch
- "Required reading" pointing at PROMPT.md
- Defect classes to focus on (specific, with prior-failure examples)
- "Out of scope" listing what NOT to do (other cities, downstream steps)
- "Procedure" with numbered steps
- "Budget" sentence at the end

Pass the full PROMPT.md by reference (agent reads it), don't quote it.
Agents read effectively and the PROMPT carries provenance/voice rules.

## Lewis's preferences (durable)

- Terse responses, no trailing summaries (`[[feedback]]` memories)
- No `AskUserQuestion` (Lewis's terminal can't render the picker; ask
  inline if needed)
- "Don't redo done work" — scope every research/QA to NEW entities only,
  never re-validate already-shipped data unless explicitly asked
- Approve per change, don't batch-confirm for prod
- Hard ban on em/en dashes anywhere — `validate_data.py` enforces ERR
- Background agents OK for parallel speed when he wants it; default
  sequential for session-survival safety
- When QA finds a new defect class, IMMEDIATELY harvest into prompts
  before dispatching the next pass — closed loop is non-negotiable

## Where the prompts live

| File | Purpose |
|---|---|
| `agents/food-research/PROMPT.md` | Research-time contract. Top-of-prompt 11-item PRE-WRITE CHECKLIST is the canonical enforcement. |
| `agents/food-research/SCHEMA.md` | Per-topic JSON shape spec. |
| `agents/qa/PROMPT.md` | QA pass contract. Section A2 lists every specific-fact subclass to check. Sections E (echoes), F (voice) etc. |
| `agents/qa/reports/` | Per-city QA reports, dated. Read prior city reports if defect-class question is unclear. |

## What auto-runs vs manual

Auto (don't repeat manually):
- `generate_city.py` chains `generate_cross_cuts.py` →
  `generate_scoped_cross_cuts.py` → `generate_city_dietary.py` →
  `generate_city_cuisine.py` → `generate_search_index.py` →
  `generate_sitemap.py` → `indexnow_ping.py`. Per-city regens keep
  every SEO surface fresh: scoped indexes, city × dietary, city × cuisine,
  search index, and the section-sharded sitemap.
- `ship_city.sh` triggers the FULL 12-step pipeline including all of the above
- Caddy serves from `content/` automatically; no deploy step

Sitemap is section-sharded: `/sitemap.xml` is a sitemap-index pointing at
`/sitemap-core.xml`, `/sitemap-cities.xml`, `/sitemap-entities.xml`,
`/sitemap-crosscuts.xml`. Per-URL `<lastmod>` reflects the actual file
mtime, so Google's crawl budget is spent on pages that genuinely changed.

Schema graph emitted (verified by Rich Results test):
- Entity pages: `Restaurant`/`Festival`/etc + `Review` + **`AggregateRating`** (drives SERP stars)
- Festival entity pages also carry `Event` with computed next-occurrence date
- City × itineraries pages: `HowTo` per itinerary, `HowToSection` per day, `HowToStep` per (morning/afternoon/evening)
- Topic pages, scoped indexes, city × dietary, city × cuisine: all carry `ItemList` + `ItemListElement`

Manual (must run yourself):
- `generate_extras.py` for `/topics/<slug>/` cross-cuts
- `generate_scoped_cross_cuts.py` for `/<country>/cuisines/`,
  `/<country>/<city>/neighborhoods/`, etc. Always preceded by
  `generate_cross_cuts.py`. ship_city.sh runs both in order; only run
  manually after a site-wide template change or city data edit outside
  the ship pipeline.
- `generate_search_index.py` if you want the Qwen tagger re-indexed (it's
  incremental, so cheap)
- `generate_homepage.py` after homepage data change
- `cleanup_broken_urls.py` before each ship_safety
- Chmod after content changes

## Recent structural improvements (2026-05-19 batch)

- `validate_data.py`: empty list-shaped topics now ERR (not WARN)
- `verify_entities.py`: US state name normalization (Minnesota↔MN),
  compound German strasse (Gipsstrasse↔Gipsstr.), 500+504 anti-bot
- `check_external_urls.py`: 500+504 anti-bot, TimeoutError retry with
  3× longer timeout
- `check_evidence_content.py`: "shojin"/"shojin ryori" recognized as
  vegetarian synonyms
- `agents/food-research/PROMPT.md`: 11-item PRE-WRITE CHECKLIST at top,
  ~12 specific-fact defect-class sections
- `agents/qa/PROMPT.md`: Section A2 with chef/owner structural rule,
  itinerary editorial sweep (summary + day titles + meal prose),
  day-of-week × venue-hours cross-check, slug-vs-prose drift, geographic
  adjacency, stale verified-block URLs after rewrites
- `scripts/utils/template_renderer.py`: og:image fallback now prefers
  `destination.hero_image` (real food photo) over typography card
- `scripts/generate_homepage.py`: homepage og:image = Paris hero photo
- `scripts/generate_city.py`: auto-sitemap + auto-indexnow appended
