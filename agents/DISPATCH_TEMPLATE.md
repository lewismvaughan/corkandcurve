# Agent Dispatch Pipeline (CANONICAL)

Per Lewis (2026-05-21) and `docs/FLOW.md`, the per-city pipeline is:

```
1. Sonnet research agent       (writes JSON, runs ship_safety)
2. Sonnet QA1 agent             (judgment pass: cuisine match, addr cross-check)
3. Sonnet QA2 agent             (judgment pass: specific-fact match, chef names, dishes)
4. Opus QA agent                (small narrow final read; should find nothing)
5. Orchestrator: generation     (geocode, build_pins, regen all generators, sitemap, search index)
6. Orchestrator: final pass     (passthrough — AI-tells, score CV, address realism, orphans)
```

**Memory rule:** `feedback_qa_automatic` says the QA chain is **automatic, never ask** — the orchestrator chains stages 2/3/4 after every successful research dispatch without being reminded.

**Memory rule:** `feedback_qa_decisive` — QA1/QA2 remove defects, don't flag-for-followup. Opus should ideally find nothing. If it does, upstream prompt regressed.

---

## Stage 1 — Sonnet research

Tool: `Agent` with `subagent_type: general-purpose`. Background.

Skeleton prompt:

```
You are the research agent for **<City>, <Country>** on TableJourney.
Empty scaffold at /station/repo/site-data/<country>/<city>/data/.

READ FIRST:
1. /station/repo/CLAUDE.md
2. /station/repo/agents/food-research/PROMPT.md
3. /station/repo/agents/food-research/SCHEMA.md
4. /station/repo/docs/STANDARDS.md
5. /station/repo/docs/DATA_TO_PAGES.md

TARGETS (median or above):
<per-topic counts>

CITY-SPECIFIC GUIDANCE:
<curated bullets — signature dishes, neighborhoods, day-trips, festivals, dietary aggregators>

NON-NEGOTIABLE RULES (from agents/food-research/PROMPT.md):
- Every entity carries a full `verified` block with the 6 keys.
- NO em-dashes or en-dashes anywhere — hard ban.
- Source-domain diversity: 3+ unique domains per topic.
- address_quoted verbatim from source page.
- Self-HEAD every URL BEFORE writing it.

WORKFLOW (chain automatically; do not stop to ask):
1. RESEARCH every topic to target.
2. WRITE JSONs.
3. Run `bash /station/repo/scripts/ship_safety.sh <country> <city>`.
   0 HARD required — fix and re-run until clean.
4. Print READY-TO-SHIP <country>/<city>.

DO NOT:
- Re-fetch URLs you just wrote ("self-QA"). ship_safety did that.
- "Self-QA1" / "self-QA2" — those are SEPARATE agents in the chain
  dispatched by the orchestrator. Doing them inside the research run
  burns tokens and produces uneven coverage.
- Skip checklist items 1-11 for any entity. Drop instead.
- Invent venue domains.

DELIVERABLES (final message back to orchestrator):
- Per-topic entry count
- ship_safety outcome (PASS / HARD count + reasons)
- Deliberate drops + why
- Top 3 source domains per major topic
```

---

## Stage 2 — Sonnet QA1

Dispatched **after** the research agent prints READY-TO-SHIP. Background.

Skeleton prompt:

```
You are the QA1 agent for **<country>/<city>** on TableJourney. The
research agent has finished; ship_safety mechanical gate PASSED. Your
job is the judgment-pass A and A2 from /station/repo/agents/qa/PROMPT.md
— catch cuisine-claim content mismatches and independent-directory
address cross-check failures.

READ FIRST:
1. /station/repo/agents/qa/PROMPT.md (entire file)
2. /station/repo/site-data/<country>/<city>/data/*.json (the work-in-progress)

YOU MUST NOT:
- Re-HEAD URLs (`source_url`, `open_evidence_url`, etc.) — pass-1 did that.
- Re-check `address_quoted` fuzzy-match — pass-1 did that.
- Re-validate JSON shape, em-dashes, description length, internal x-refs.

YOU MUST:
- Section A: for every entity with a `cuisine` claim, fetch
  `cuisine_evidence_url` and confirm the page text supports the claim.
  EXCEPT dietary entries (handled by check_evidence_content.py).
- Sampled independent-directory address cross-check (10-15 entities,
  random sample across topics): Google Maps / OSM / Time Out / Eater /
  Michelin / Tripadvisor / OpenTable. If sample hits >2 fabrications,
  broaden to 30. Remove fabricated entities.
- Section A2: validate every SPECIFIC FACT — dish names, press
  citations, chef names, cooking methods — against operator menu or
  press URL. Remove or generalize claims that fail.

DELIVERABLES: write
/station/repo/agents/qa/reports/<country>_<city>_qa1_<YYYY-MM-DD>.md
with a defect list. Remove flagged entities directly from the JSONs.
Re-run ship_safety.sh after your changes. Print
QA1-COMPLETE <country>/<city> with a defect count.

One continuous run, no escape hatches.
```

---

## Stage 3 — Sonnet QA2

Dispatched **after** QA1 prints QA1-COMPLETE. Background.

Skeleton prompt:

```
You are the QA2 agent for **<country>/<city>** on TableJourney. QA1
already cleared the cuisine-match and address cross-check classes.
Your job is the remaining QA classes in /station/repo/agents/qa/PROMPT.md
— specifically: tour-route fabrication, festival-prose echoes,
thin-category fabrication, chef-name URL-slug mining, name + address
fabrication on dietary entries (since QA1 skipped those by rule).

READ FIRST:
1. /station/repo/agents/qa/PROMPT.md (sections C-H or whatever covers
   tours, festivals, thin-category, voice/echo)
2. The post-QA1 JSON state
3. The QA1 report

YOU MUST:
- Section C: for every food-tour entity, verify the route claim is the
  operator's actual route (fetch operator site, find a "what we visit"
  page). Remove fabricated routes.
- Section D: for every festival entity, confirm the festival month +
  prose echoes (don't repeat language from the source page verbatim
  in 'description').
- Section E: identify any topic where the entries are suspiciously
  uniform (description openers identical, scores tightly clustered,
  addresses all on same one or two streets). Spot-fix.
- Section F: scan editorial prose for AI-tells (em/en-dash variants in
  unicode chars, generic-vibe phrases, "nestled in", "to die for", etc.)
- Dietary names + addresses: QA1 skipped these per rule because
  check_evidence_content.py already did content match. YOU spot-check
  5-10 dietary entries on an independent directory.

DELIVERABLES: write
/station/repo/agents/qa/reports/<country>_<city>_qa2_<YYYY-MM-DD>.md.
Remove flagged entities directly. Re-run ship_safety.sh.
Print QA2-COMPLETE <country>/<city>.

One continuous run, no escape hatches.
```

---

## Stage 4 — Opus QA

Dispatched **after** QA2 prints QA2-COMPLETE. Small-model Opus call,
background.

Skeleton prompt:

```
You are the Opus final QA for **<country>/<city>**. QA1 + QA2 have
already removed obvious defects. You should ideally find NOTHING.
If you find anything, it means QA1 or QA2 regressed — flag the class
of defect so the upstream prompt can be hardened.

READ:
1. /station/repo/agents/qa/PROMPT.md
2. QA1 + QA2 reports under /station/repo/agents/qa/reports/
3. Final JSON state

NARROW READ — do NOT re-do QA1 or QA2:
- Skim 30 random entities across topics. Sample for: fabricated chef
  names, fabricated press credentials, claim/source mismatch.
- Verify one itinerary end-to-end: every `days[*].venues[*]` slug
  resolves to a verified entity in the same city.
- Verify one festival end-to-end: source page text matches month claim.
- Spot-check 5 entities with editorial_score >= 4.7 — that score
  needs to be backed by either Michelin/50best or a strong press cite.

DELIVERABLES:
/station/repo/agents/qa/reports/<country>_<city>_opus_<YYYY-MM-DD>.md
Print OPUS-CLEAR <country>/<city> if nothing found, else OPUS-FOUND-N
with the defect list. Re-run ship_safety.sh after any removal.

One continuous run.
```

---

## Stage 5 — Generation (orchestrator)

After Opus prints OPUS-CLEAR (or OPUS-FOUND-N where the defects were
fixed in place):

```bash
cd /station/repo
python3 scripts/geocode_entities.py --city <city>
python3 scripts/build_city_pins.py --city <city>
python3 scripts/qa_geo_outliers.py --bugs-only

python3 scripts/generate_city.py <country> <city>
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
