# Agent Dispatch Pipeline (CANONICAL)

Per Lewis (2026-05-21) and `docs/FLOW.md`, the per-region pipeline is:

```
1. Sonnet wine-research agent  (writes JSON incl. wines.json, runs ship_safety)
2. Sonnet QA1 agent             (judgment pass: classification, hectarage, score citation, addr cross-check)
3. Sonnet QA2 agent             (judgment pass: ownership currency, biodynamic certs, taste-note sourcing, tag conformance, TJ refs)
4. Opus QA agent                (small narrow final read; should find nothing)
5. Orchestrator: generation     (geocode skipping wines, build_pins, regen all generators incl. wine + tag pages, sitemap, search index)
6. Orchestrator: final pass     (passthrough — AI-tells, score CV, address realism, orphans)
```

**Memory rule:** `feedback_qa_automatic` says the QA chain is **automatic, never ask** — the orchestrator chains stages 2/3/4 after every successful research dispatch without being reminded.

**Memory rule:** `feedback_qa_decisive` — QA1/QA2 remove defects, don't flag-for-followup. Opus should ideally find nothing. If it does, upstream prompt regressed.

---

## Stage 1 — Sonnet research

Tool: `Agent` with `subagent_type: general-purpose`. Background.

**SPLIT THE DISPATCH.** A single agent trying to write all 24 topics +
region.json + neighborhoods.json hits the model's 32k output token cap
mid-pipeline (observed on Bordeaux 2026-05-22: agent died after 38 min
having written only `vineyards.json` + `region.json`). Default to a
parallel split on non-overlapping files. A clean 4-way split:

- **Agent A — foundation**: `region.json` + `neighborhoods.json` +
  `vineyards.json` + `signature-grapes.json`. Other agents depend on
  the vineyards slugs, so this one runs first (or together with B
  if you've pre-seeded vineyards).
- **Agent B — cuvée vertical** (depends on A's vineyards): `wines.json`
  + `signature-wines.json` + `food-pairing.json`.
- **Agent C — venues**: tasting-rooms, wine-bars, wine-restaurants,
  wine-retailers, wine-schools, wine-tours, distilleries, wine-museums,
  wine-hotels, wine-experiences.
- **Agent D — editorial + nested**: wine-history, seasonal-wine,
  wine-festivals, budget-wines, hidden-gems, day-trips-wine,
  itineraries, nightlife, dietary.

Each agent's prompt MUST be explicit: "Touch ONLY these files. A
sibling agent owns the rest." All four can run concurrently except
B which waits on A. QA1/QA2/Opus do not write much output, so they
do NOT need splitting — one agent per QA stage is fine.

Memory rule: `feedback-research-output-cap`.

Skeleton prompt:

```
You are the wine-research agent for **<Region>, <Country>** on Cork & Curve.
Empty scaffold at /station/repo/site-data/<country>/<region>/data/.

READ FIRST:
1. /station/repo/CLAUDE.md
2. /station/repo/agents/wine-research/PROMPT.md
3. /station/repo/agents/wine-research/SCHEMA.md
4. /station/repo/docs/STANDARDS.md
5. /station/repo/docs/DATA_TO_PAGES.md
6. /station/repo/docs/WINE_TAGS.md  (controlled tag vocabulary for wines.json)

TARGETS (median or above; see PROMPT.md "24 wine topics" table):
<per-topic counts including wines.json @ 80-200 per region>

REGION-SPECIFIC GUIDANCE:
<curated bullets — signature wines, sub-appellations, day-trip neighbours, festivals, biodynamic/natural aggregators>

NON-NEGOTIABLE RULES (from agents/wine-research/PROMPT.md):
- Every entity carries a full `verified` block.
- NO em-dashes or en-dashes anywhere — hard ban.
- Source-domain diversity: 3+ unique domains per topic.
- address_quoted verbatim from source page.
- Self-HEAD every URL BEFORE writing it.
- Wines (wines.json) are vintage-agnostic — slug is `tignanello`, not `tignanello-2019`.
- Every wines[*].producer MUST resolve in vineyards.json (same region).
- Every signature_wines[*].slug MUST also exist in wines[*].slug.
- Every wines[*].tags entry MUST be in docs/WINE_TAGS.md.
- Researcher emits style/body/tannin/acidity/pairing/occasion/mood/editorial tags only.
  Do NOT emit price/ageing/production/grape/world/sweetness tags — generators derive those.
- pairings[*].tablejourney_ref: HEAD-verify before populating. Use `null` if unsure.

WORKFLOW (chain automatically; do not stop to ask):
1. RESEARCH every topic to target.
2. WRITE JSONs. wines.json comes AFTER vineyards.json so producer slugs resolve.
3. Run `bash /station/repo/scripts/ship_safety.sh <country> <region>`.
   0 HARD required — fix and re-run until clean.
4. Print READY-TO-SHIP <country>/<region>.

DO NOT:
- Re-fetch URLs you just wrote ("self-QA"). ship_safety did that.
- "Self-QA1" / "self-QA2" — those are SEPARATE agents in the chain
  dispatched by the orchestrator.
- Skip checklist items 1-19 for any entity. Drop instead.
- Invent producer domains, TJ paths, or tag slugs.
- Invent cuvées. If a producer's full lineup isn't documented on
  their site or in critic coverage, list the cuvées that ARE
  documented and stop. Better 4 verified cuvées than 8 fabricated.

DELIVERABLES (final message back to orchestrator):
- Per-topic entry count (including wines count)
- ship_safety outcome (PASS / HARD count + reasons)
- Deliberate drops + why
- Top 3 source domains per major topic
- For wines.json: distribution of style tags, distribution of pairings (e.g. "67% of cuvées have at least 1 TJ-cross-linked pairing")
```

---

## Stage 2 — Sonnet QA1

Dispatched **after** the research agent prints READY-TO-SHIP. Background.

Skeleton prompt:

```
You are the QA1 agent for **<country>/<region>** on Cork & Curve. The
wine-research agent has finished; ship_safety mechanical gate PASSED.
Your job is the QA1 judgment pass from /station/repo/agents/qa/PROMPT.md
sections A-F + L — catch classification mistakes, hectarage fabrications,
unsourced scores, ownership staleness, independent-directory address
cross-check failures, and producer cross-ref breakage in wines.json.

READ FIRST:
1. /station/repo/agents/qa/PROMPT.md (entire file)
2. /station/repo/site-data/<country>/<region>/data/*.json (the work-in-progress)
3. /station/repo/docs/WINE_TAGS.md (for the L/J tag checks)

YOU MUST NOT:
- Re-HEAD URLs (`source_url`, `open_evidence_url`, etc.) — pass-1 did that.
- Re-check `address_quoted` fuzzy-match — pass-1 did that.
- Re-validate JSON shape, em-dashes, description length, internal x-refs.

YOU MUST:
- Section A: classification accuracy (DOCG / DOC / IGT / IGP / AOC / AVA /
  VDP / DOCa / WO). Sample 15-20 vineyards + signature-wines + wines.
  >2 defects → broaden to 40.
- Section B: hectarage realism. Confirm every `vineyards[*].hectares`
  against producer About page or consortium fact sheet.
- Section C: score citations. Every `scores[*]` has reviewer + points
  + vintage + year. Remove unattributable scores. Applies to vineyards
  AND wines.
- Section F: independent-directory address cross-check, 10-15 random
  entities across topics. Skip wines.json (no addresses; producer is
  the location).
- Section L: every `wines[*].producer` slug resolves in vineyards.json.
  Every `signature_wines[*].slug` exists in `wines[*].slug`.

DELIVERABLES: write
/station/repo/agents/qa/reports/<country>_<region>_qa1_<YYYY-MM-DD>.md
with a defect list. Remove flagged entities directly from the JSONs.
Re-run ship_safety.sh after your changes. Print
QA1-COMPLETE <country>/<region> with a defect count.

One continuous run, no escape hatches.
```

---

## Stage 3 — Sonnet QA2

Dispatched **after** QA1 prints QA1-COMPLETE. Background.

Skeleton prompt:

```
You are the QA2 agent for **<country>/<region>** on Cork & Curve. QA1
already cleared classification, hectarage, scores, address cross-check,
and producer/cuvée cross-references. Your job is the remaining QA
classes in /station/repo/agents/qa/PROMPT.md sections D, E, G, H, I, J, K.

READ FIRST:
1. /station/repo/agents/qa/PROMPT.md
2. /station/repo/docs/WINE_TAGS.md
3. The post-QA1 JSON state
4. The QA1 report

YOU MUST:
- Section D: ownership currency. Every `vineyards[*].owner` against
  2024-2026 press / consortium roster. Pre-Constellation Mondavi,
  pre-LVMH Lambrays etc. are stale-ownership defects.
- Section E: biodynamic / organic certification — Demeter / Ecocert /
  ICEA / USDA Organic / CCPB / SQNPI registry checks for 10 entries
  marked `*_certified`. Promoting practising to certified is hard-fail.
- Section G: cross-link sanity. Every food-pairing TJ URL HEAD-resolves
  AND is in the matching TJ city. PLUS every non-null
  `wines[*].pairings[*].tablejourney_ref` HEAD-resolves AND is in the
  matching TJ city.
- Section H: voice + prose — no em/en dashes, no AI-tells, no
  score-bunching, no description clones within a topic.
- Section I: cuvée taste-note sourcing. Sample 10 wines with
  editorial_score >= 4.5. Confirm taste descriptors trace to a
  producer tech sheet or named critic note at the cited
  `verified.cuisine_evidence_url`. Watch for "every cuvée opens with
  'dark cherry, leather'" template-fill.
- Section J: tag vocabulary conformance. Every tag in `wines[*].tags`
  must be in docs/WINE_TAGS.md AND must NOT be from a DERIVED axis
  (price / ageing / production / grape / world / sweetness — generators
  add those).
- Section K: vintage-agnostic discipline. No wines slug with a 4-digit
  year. No wines name like "Tignanello 2019".

DELIVERABLES: write
/station/repo/agents/qa/reports/<country>_<region>_qa2_<YYYY-MM-DD>.md.
Remove flagged entities directly. Re-run ship_safety.sh.
Print QA2-COMPLETE <country>/<region>.

One continuous run, no escape hatches.
```

---

## Stage 4 — Opus QA

Dispatched **after** QA2 prints QA2-COMPLETE. Small-model Opus call,
background.

Skeleton prompt:

```
You are the Opus final QA for **<country>/<region>** on Cork & Curve.
QA1 + QA2 have already removed obvious defects. You should ideally
find NOTHING. If you find anything, it means QA1 or QA2 regressed —
flag the class of defect so the upstream prompt can be hardened.

READ:
1. /station/repo/agents/qa/PROMPT.md
2. /station/repo/docs/WINE_TAGS.md
3. QA1 + QA2 reports under /station/repo/agents/qa/reports/
4. Final JSON state

NARROW READ — do NOT re-do QA1 or QA2:
- Skim 30 random entities across topics. Sample for: fabricated
  winemaker names, fabricated press credentials, claim/source mismatch.
- Verify one itinerary end-to-end: every `days[*].venues[*]` slug
  resolves to a verified entity in the same region.
- Verify one festival end-to-end: source page text matches month claim.
- Verify one cuvée end-to-end: producer slug resolves in vineyards.json,
  taste descriptors trace to the cited evidence URL, every non-null
  pairings TJ ref HEAD-resolves, every tag is in docs/WINE_TAGS.md.
- Spot-check 5 entities with editorial_score >= 4.7 — that score
  needs to be backed by Decanter top-rated / Wine Spectator Top 100 /
  Wine Advocate 95+ / equivalent.

DELIVERABLES:
/station/repo/agents/qa/reports/<country>_<region>_opus_<YYYY-MM-DD>.md
Print OPUS-CLEAR <country>/<region> if nothing found, else OPUS-FOUND-N
with the defect list. Re-run ship_safety.sh after any removal.

One continuous run.
```

---

## Stage 5 — Generation (orchestrator)

After Opus prints OPUS-CLEAR (or OPUS-FOUND-N where the defects were
fixed in place):

```bash
cd /station/repo
# Geocoding skips wines.json automatically (wines aren't a location;
# their producer is). The pin map reflects producer locations only.
python3 scripts/geocode_entities.py --city <region>
python3 scripts/build_city_pins.py --city <region>
python3 scripts/qa_geo_outliers.py --bugs-only

python3 scripts/generate_city.py <country> <region>
# Wine cuvée pages: /wine/<producer>/<cuvee>/ — generated from wines.json
python3 scripts/generate_wine_pages.py
# Tag indices: /tag/<slug>/ + /tag/<slug>/<region>/
python3 scripts/generate_tag_pages.py
for g in city_cuisine city_dietary city_dish city_nightlife_sub city_price_tier \
         city_topic_when country_topic country_cuisine country_dish country_dietary \
         country_nightlife_sub neighborhood_cuisine global_top_topics cross_cuts \
         scoped_cross_cuts chrome_pages homepage country_stubs; do
    python3 scripts/generate_${g}.py
done
python3 scripts/generate_search_index.py
python3 scripts/generate_sitemap.py
python3 scripts/orphan_audit.py     # MUST be 0
```

If orphan_audit > 0, the typical fix is re-injecting parent blocks:

```bash
python3 scripts/generate_neighborhood_cuisine.py  # re-injects nbhd parents
python3 scripts/generate_city_topic_when.py        # re-injects when-blocks
python3 scripts/generate_country_stubs.py          # adds single-city-country indexes
```

---

## Stage 6 — Orchestrator final passthrough

After generation, the orchestrator does a deterministic heuristic scan
across all NEW cities in the batch:

```python
# Per-city in the batch:
#  - 0 AI-tell phrases (regex set from prior QA findings)
#  - 0 generic openers ("This cozy/charming/elegant/iconic ...")
#  - Score CV in [0.04, 0.10]  (lower = bunched, higher = noise)
#  - Description length distribution healthy (avg 150-220 chars)
#  - Address realism (digit-start or street-prefix per locale)
#  - Description "clones" only across same-entity-in-multiple-topics
#    (cross-reference via slug, expected)
#  - Pin coverage >= 75%
#  - 0 real geo bugs from qa_geo_outliers
#  - 0 orphans
```

Findings → fix mechanically (URL swap, address normalize) OR queue a
narrow fix agent. Then chmod + commit + push.

---

## Token budget per city (typical)

| Stage | Tokens | Time |
|---|---|---|
| Research (Sonnet) | 250-500k | 30-50 min |
| QA1 (Sonnet) | 60-100k | 15-25 min |
| QA2 (Sonnet) | 60-100k | 15-25 min |
| Opus QA | 40-80k | 5-10 min |
| Generation (orchestrator local) | 0 | 1-2 min |
| Orchestrator passthrough | <10k inline | <1 min |

Per-city total: ~450-800k tokens, 70-110 min wallclock. 5 cities in
parallel = ~2.5M-4M tokens, 1.5-2 hours wallclock if running well.

The big variance is research; QA stages are deterministically scoped
to the JSON state and are bounded.

---

## What NOT to do (lessons from prior batches)

1. **Don't conflate self-review with QA.** "QA1 (self): re-read your
   own work" inside the research prompt is theater — it doesn't catch
   what an independent reader catches. Run real QA1/QA2/Opus agents.

2. **Don't skip stages "to ship faster".** This was the failure mode
   on the 10-city batch on 2026-05-21. Mechanical gate (ship_safety)
   passed everywhere but Valencia self-flagged 35 URL fabrications
   from its own self-HEAD — proof that without independent QA, defect
   honesty varies by agent.

3. **Don't dispatch the QA chain only on demand.** Memory rule
   `feedback_qa_automatic`: AUTOMATIC, never ask.

4. **Don't run the QA agents IN the research agent's run.** They are
   separate orchestrator-dispatched calls with their own scoped prompts
   and JSON state snapshots. Bundling them into research breaks the
   stage-1 / stage-2 separation that makes defects findable.

5. **Don't dispatch QA after generation.** QA must complete BEFORE
   generation runs — otherwise pin/index/sitemap regen happens on
   defective JSON. Order is research → QA1 → QA2 → Opus → generation
   → orchestrator pass.
