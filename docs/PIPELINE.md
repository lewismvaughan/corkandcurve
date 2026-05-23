# Cork & Curve — pipeline reference

5-stage canonical pipeline per region. Mirrors TableJourney pattern;
see `agents/DISPATCH_TEMPLATE.md` for the full prompt skeletons.

```
1. Sonnet wine-research agent  →  ship_safety PASS
2. Sonnet QA1 (judgment pass)
3. Sonnet QA2 (judgment pass)
4. Opus final QA               (small, narrow read)
5. Orchestrator generation     (geocode + pins + regen + sitemap + index)
   + orchestrator passthrough  (AI-tells / score-CV / address realism)
```

## Stage detail

### 1. Research (Sonnet) — SPLIT INTO PARALLEL AGENTS

Dispatch: see `agents/DISPATCH_TEMPLATE.md` Stage 1 skeleton.

**Split the dispatch.** One agent trying to fill the whole region in
one go hits the 32k model output token cap (Bordeaux 2026-05-22: died
at 38 min having written only `vineyards.json` + `region.json`).
Default split into 4 parallel agents on non-overlapping files:

1. **Agent A — foundation**: `region.json` + `neighborhoods.json` +
   `vineyards.json` + `signature-grapes.json`.
2. **Agent B — cuvée vertical** (waits on A's vineyards): `wines.json`
   + `signature-wines.json` + `food-pairing.json`.
3. **Agent C — venue topics**: tasting-rooms, wine-bars,
   wine-restaurants, wine-retailers, wine-schools, wine-tours,
   distilleries, wine-museums, wine-hotels, wine-experiences.
4. **Agent D — editorial + nested**: wine-history, seasonal-wine,
   wine-festivals, budget-wines, hidden-gems, day-trips-wine,
   itineraries, nightlife, dietary.

Run in background. Token cost: 250-500k aggregate per region. Time:
30-50 min wallclock per agent; A/C/D run concurrently, B waits on A.

Outputs: 24 wine topic JSONs + region.json + neighborhoods.json under
`site-data/<country>/<region>/data/`. ship_safety.sh PASS at end.

### 2. QA1 (Sonnet)

Dispatch when Stage 1 prints `READY-TO-SHIP <country>/<region>`.

Reads `agents/qa/PROMPT.md` sections A-C.

Defect classes caught:
- Classification accuracy (DOCG/DOC/IGT/AOC/AVA)
- Hectarage realism
- Score citations (reviewer + vintage + year)

Cost: 60-100k. Output: defect list + flagged removals + report at
`agents/qa/reports/<country>_<region>_qa1_<date>.md`.

### 3. QA2 (Sonnet)

Dispatch when Stage 2 prints `QA1-COMPLETE`.

Reads `agents/qa/PROMPT.md` sections D-H.

Defect classes:
- Ownership currency (stale acquisitions)
- Biodynamic / organic certification (Demeter / Ecocert / ICEA)
- Independent-directory address cross-check (10-15 sample)
- Voice + prose (em-dashes, AI-tells, score-bunching, clones)
- Cross-link sanity (food_pairing TJ URLs)

Cost: 60-100k.

### 4. Opus final

Dispatch when Stage 3 prints `QA2-COMPLETE`.

Narrow read; should find NOTHING. If it does, upstream prompt
regressed. Sample 30 entities, verify one itinerary + one festival
end-to-end, spot-check `editorial_score >= 4.7` for backing creds.

Cost: 40-80k.

### 5. Orchestrator (this session)

Run sequentially:

```bash
cd /station/repo
python3 scripts/geocode_entities.py --city <region>
python3 scripts/build_city_pins.py --city <region>  # rename to build_region_pins
python3 scripts/qa_geo_outliers.py --bugs-only

python3 scripts/generate_city.py <country> <region>  # rename to generate_region
# Cross-cut generators per docs/SCRIPTS_AUDIT.md
python3 scripts/generate_sitemap.py
python3 scripts/generate_search_index.py
python3 scripts/orphan_audit.py  # must be 0
```

Then a deterministic heuristic passthrough (AI-tell regex, score CV,
address realism). If clean, chmod + commit + push.

## Token budget per region (typical)

| Stage | Tokens | Time |
|---|---|---|
| Research (Sonnet) | 250-500k | 30-50 min |
| QA1 (Sonnet) | 60-100k | 15-25 min |
| QA2 (Sonnet) | 60-100k | 15-25 min |
| Opus QA | 40-80k | 5-10 min |
| Generation + passthrough | <10k | 2-5 min |

Per-region total: ~450-800k, 70-110 min wallclock.

5 regions parallel: ~2.5-4M, 1.5-2 hrs wallclock.

## What NOT to do (lessons from TJ batches)

1. Don't conflate self-QA with the dedicated QA agent.
2. Don't skip QA stages "to ship faster" — Valencia self-dropped 35
   fabrications because of one honest agent; cross-agent quality varies.
3. Don't run QA inside the research agent's run. Separate orchestrator
   stages.
4. Don't dispatch QA after generation. Order is research → QA1 → QA2
   → Opus → generation → passthrough.
5. Don't push HARD failures. ship_safety must exit 0 before any
   commit + push.
