# Cork & Curve — operational flow

The playbook the Claude session inside the Cork & Curve station follows
when shipping changes to corkandcurve.com. Future-me: read this before
doing anything non-trivial.

## TL;DR by task

| Goal | Recipe |
|---|---|
| Ship a new wine region | `new_region.py` → 5-stage agent pipeline → orchestrator gen + push |
| Fill missing topics in a shipped region | scoped research dispatch (specific topics only) → QA1 → QA2 → Opus → ship_safety → regen → push |
| Update a single entity | edit JSON → `ship_safety.sh <country> <region>` → regen → chmod → push |
| Refresh sitemap / search index | `generate_sitemap.py` + `generate_search_index.py` → push |

## The full flow, expanded

### 1. Research dispatch (research agent OR direct edit)

For a new region:
- `python3 scripts/new_region.py <country> <region> --name <Name> --country <Country>`
- Dispatch the research agent with the prompt template in
  `agents/DISPATCH_TEMPLATE.md`, scoped to that region.
- Agent reads `agents/wine-research/PROMPT.md` and `agents/wine-research/SCHEMA.md`.

Don't bundle QA work into the research run — that conflates self-review
with the independent QA judgment pass and produces uneven defect catch.

### 2. QA chain (per region)

Automatic after every successful research dispatch — orchestrator
chains 2/3/4 without being reminded.

1. **Sonnet QA1** — read `agents/qa/PROMPT.md` sections A-C
   (classification accuracy, hectarage realism, score citations).
   Sample 15-20 entities across topics. Remove flagged entities
   directly. Write report to `agents/qa/reports/<country>_<region>_qa1_<YYYY-MM-DD>.md`.
2. **Sonnet QA2** — sections D-F (ownership currency, biodynamic
   certification, independent-directory address cross-check, voice
   defects, prose echoes).
3. **Opus final** — narrow read; ideally finds nothing. If it does,
   upstream prompt regressed.

Each stage MUST re-run `ship_safety.sh` after entity removals to
confirm structural integrity.

### 3. URL hygiene

After QA: `python3 scripts/cleanup_broken_urls.py` strips dead booking
/ affiliate / image URLs (anti-bot 401/403/429 retained — those resolve
for humans).

### 4. ship_safety gate

`bash scripts/ship_safety.sh <country> <region>` is the deterministic
mechanical gate. 7 layers:

1. `validate_data.py` — JSON shape, em-dash ban, length caps, verified-block presence
2. `verify_entities.py` — URL HEAD checks, address fuzzy match
3. `check_internal_references.py` — itineraries + signature-wines + day-trips cross-refs resolve
4. `check_evidence_content.py` — biodynamic/organic keyword on cuisine_evidence_url page
5. `check_festival_dates.py` — fetch festival source_url, confirm start_month
6. `check_external_urls.py` — booking/affiliate/tasting URLs alive
7. `check_jsonld.py` — schema.org validity on built HTML

Any HARD failure blocks ship.

### 5. Regenerate HTML

Orchestrator (Claude inside Cork station) runs:

```
python3 scripts/geocode_entities.py --city <region>
python3 scripts/build_city_pins.py --city <region>
python3 scripts/qa_geo_outliers.py --bugs-only

python3 scripts/generate_city.py <country> <region>
# Run all cross-cut generators (city_cuisine, city_dietary, etc.)
# Adapt these to wine-vertical analogs OR document which TJ scripts
# need wine adaptation. See docs/SCRIPTS_AUDIT.md.

python3 scripts/generate_sitemap.py
python3 scripts/generate_search_index.py
python3 scripts/orphan_audit.py   # must be 0
```

### 6. Chmod (Caddy reads world-read)

```
sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/corkandcurve/repo/content'
```

### 7. Push to GitHub

```
git add -A
git commit -m "..."
git push origin main
```

### 8. Verify live

```
curl -sSI https://corkandcurve.com/<country>/<region>/ | head -3
```

## 5-stage canonical pipeline (per region)

| Stage | Run by | Token cost | Time |
|---|---|---|---|
| 1. Research | Sonnet (background agent) | 250-500k | 30-50 min |
| 2. QA1 | Sonnet (background) | 60-100k | 15-25 min |
| 3. QA2 | Sonnet (background) | 60-100k | 15-25 min |
| 4. Opus final | Opus (background) | 40-80k | 5-10 min |
| 5. Generation + passthrough | Orchestrator (this session) | <10k inline | 2-5 min |

Total per region: ~450-800k tokens, 70-110 min wallclock. 5 regions
in parallel = ~2.5-4M tokens, 1.5-2 hours wallclock.

## Background-agent ops

- `subagent_type: "general-purpose"` for all research + QA passes
- Always `run_in_background: true` for research stages
- Per the dispatch template: each agent prompt is fully self-contained
  (no "ask user" escape hatches)
- Orchestrator chains stages automatically — `feedback_qa_automatic`
  is a hard rule

## Cross-linking work

See `docs/CROSS_LINKING.md` for the contract.

## Where the prompts + docs live

| Path | What it covers |
|---|---|
| `agents/wine-research/PROMPT.md` | Research-time discipline + 11-item pre-write checklist |
| `agents/wine-research/SCHEMA.md` | Per-topic JSON shape spec |
| `agents/qa/PROMPT.md` | QA pass contract (sections A-H) |
| `agents/DISPATCH_TEMPLATE.md` | Orchestrator dispatch skeletons + 5-stage pipeline |
| `docs/STANDARDS.md` | SEO + perf + correctness invariants |
| `docs/DATA_TO_PAGES.md` | Field → page mapping (what JSON drives what HTML) |
| `docs/SKELETON.md` | URL inventory + page-type breakdown |
| `docs/CROSS_LINKING.md` | TJ ↔ C&C cross-link contract |
| `docs/SCRIPTS_AUDIT.md` | Which scripts work as-is, which need wine adaptation |
| `docs/TEMPLATES_AUDIT.md` | Which templates work as-is, which need wine adaptation |

## Definition of region ship-done (the orchestrator's contract)

A region is NOT shipped until every gate below is green. Added
2026-05-23 after TJ shipped Hong Kong with 0% geocode coverage + no
inbound chrome listing because the orchestrator declared "done" off
`ship_safety` + `generate_city.py` alone. Both pass while the region
is missing maps, pins, and inbound chrome links.

```
# Mechanical gate
1. bash scripts/ship_safety.sh <country> <region>
   (exits 0 — 7 layers PASS)

# Geocode + maps + pins (NEW gates — these are the easiest to forget)
2. python3 scripts/geocode_entities.py --city <region>
   (Nominatim ~1/s, ~2 min per 100 entities)
3. python3 scripts/check_geocode_coverage.py <country> <region>
   (≥95% coverage)
4. python3 scripts/build_entity_maps.py --city <region>
5. python3 scripts/build_city_pins.py

# Render
6. python3 scripts/generate_city.py <country> <region>

# Chrome integration — NOT in generate_city.py's chain
7. python3 scripts/generate_chrome_pages.py
   (refreshes /regions/, /topics/, /grapes/, /styles/)

# Verification gates
8. orphan_audit.py: orphan count for the new region ≤ 0
9. FAQ presence on region hub (id="faq" + FAQPage schema)
10. check_jsonld.py — no JSON parse errors
11. Sitemap-vs-disk reconcile
12. Live smoke test — 6+ URLs return 200
13. Chrome regions listing — region appears in /regions/

# Permissions
14. chmod a+rX on content/
```

If ANY of these fail, the region is NOT ship-done.

