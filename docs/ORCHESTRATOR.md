# Cork & Curve — orchestrator role

The Claude session inside the Cork station container IS the orchestrator.
This doc explains that role, scoped to wine-vertical specifics.

## What the orchestrator does

1. **Dispatches** research + QA agents per `docs/PIPELINE.md` 5-stage
   pipeline.
2. **Adapts** the TJ-forked scripts/templates to wine vertical (one-time
   work; see `docs/SCRIPTS_AUDIT.md` + `docs/TEMPLATES_AUDIT.md`).
3. **Runs the generation step** after each region's Opus pass.
4. **Runs the orchestrator passthrough** — deterministic heuristic scan
   for AI-tells, score-CV, address realism.
5. **Commits + pushes** to GitHub on each clean batch.
6. **Manages the Caddy vhost** (one-time setup done; sudo on host
   needed for further config changes).

## What the orchestrator does NOT do

- Does NOT run self-QA inside the research dispatch.
- Does NOT re-fetch URLs that ship_safety already checked.
- Does NOT dispatch QA only on demand — it's automatic per
  `feedback_qa_automatic`.
- Does NOT skip the orphan_audit (must be 0).
- Does NOT push HARD failures.

## Cross-station ops

When a region overlaps a TJ city:

1. After C&C region ships, the orchestrator updates the matching TJ
   city's region.json to include a `cross_site_ref` field pointing at
   `https://corkandcurve.com/<country>/<region>/`.
2. The TJ orchestrator (TJ station) regenerates that city's hub +
   topic pages so the C&C link renders.
3. Conversely, when a TJ city ships with a wine-region overlap, the
   C&C orchestrator updates the corresponding region.json `cross_site_ref`.

These updates are reciprocal but NOT bulk — only happen on the
specific city/region pair that overlaps.

## Memory rules that apply here

- `feedback_qa_automatic` — QA chain runs automatically, never ask.
- `feedback_canonical_pipeline` — 5 stages per region.
- `feedback_no_em_dashes` — hard ban across all content.
- `feedback_url_fabrication` — self-HEAD every URL before writing.
- `feedback_qa_decisive` — QA1/QA2 remove defects, don't flag-for-followup.
- `feedback_geocode_gates_ship` — pin coverage >= some threshold before
  declaring ship.

(See `~/.claude/projects/-station-repo/memory/MEMORY.md` for the index.
That memory is per-station; cross-station session-startup should
read its own MEMORY.md.)
