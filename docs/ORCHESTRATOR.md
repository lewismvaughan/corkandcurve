# Orchestrator loop (master session)

This document describes how the **master Claude Code session** (Lewis is
the human running it) drives the city pipeline by spawning a research
subagent and a validation subagent per city.

## Roles and models

| Role | Where it runs | Model |
|---|---|---|
| Master / orchestrator | Lewis's interactive Claude Code session | Whatever Lewis is using (Opus) |
| Research subagent | Subagent spawned from master via `Agent` tool | **Sonnet** (fast, cheap, fine for research at this depth) |
| Validation subagent | Subagent spawned from master via `Agent` tool | **Opus** (judgment work; reads research output, applies editorial taste) |

Why this split: research is volume work, cost-bounded, and the failure
mode is "miss a few entries"; validation is judgment work, low-volume, and
the failure mode is "ship something embarrassing." Opus pays off where
taste matters, Sonnet pays off where speed does.

## State machine

`data/locations.json` (356 cities × 24 categories = 8,544 tracker rows)
is the single source of truth. It has **two granularities**: per-city
status (rollup) and per-category status (the real work tracker). Both
must move together; the orchestrator computes the city rollup from the
category statuses.

### Per-category status (the real work signal)

```
queued -> researching -> researched
                            |
                            v
                       validating
                       /        \
                      v          v
            validated         needs_fixes  -- back to researching
                |
                v
             deployed
```

### Per-city status (rollup)

```
queued        -> no categories started
scaffolded    -> new_city.py ran; JSON stubs exist; categories still queued
in_progress   -> at least one category past queued, not all deployed
ready_to_ship -> every entity-bearing category validated (awaiting ship_city.sh)
shipped       -> every category deployed
```

The orchestrator updates per-category statuses as work progresses, then
recomputes the city-level rollup. Agents that touch a category MUST
write the updated status back to `data/locations.json` so a session that
ends mid-flight can resume.

### Why both granularities

A research subagent for one city might fill 18 of 24 categories before
hitting a token cap or being interrupted. Without per-category tracking,
the next session has to re-research everything. With it, the orchestrator
resumes with `restaurants=researched, fine-dining=researched, ...,
bakeries=queued, coffee-roasters=queued, ...` and dispatches only the
remaining 6.

## The master loop (semantics)

Each iteration, the master does this:

```text
1. Read data/locations.json
2. Pick the next city by:
   - Find a city where any category has status != 'deployed' (i.e. work
     remains). Within such cities, prefer the one with the most
     'researched' / 'validated' categories already (finish what you
     started) and lower 'priority' / 'tier' number.
   - If a city has ALL categories 'deployed', skip; it's done.
3. If the city's status == 'queued':
     python scripts/new_city.py <country> <city> --name "<display_name>" --country "<country_name>"
   Then update locations.json: status = 'scaffolded'. The category
   statuses stay 'queued' until research touches them.
4. Decide what to dispatch:
   (a) If ANY category status == 'needs_fixes': re-research just those
       categories (pass the validation report URL to the research
       subagent as the brief).
   (b) Else if ANY category status == 'queued': dispatch a research
       subagent to fill ALL still-queued categories for this city.
       The subagent updates each category's status as it works:
         queued -> researching -> researched
       (Per-category writes mean a crashed/interrupted subagent leaves
       partial progress preserved.)
   (c) Else if EVERY entity-bearing category is 'researched' and none
       is 'validated' yet: dispatch the validation subagent.
   (d) Else if EVERY entity-bearing category is 'validated' but no
       category is 'deployed' yet: ship it.

5. Research subagent dispatch (Agent tool, model=sonnet):
     "You are a TableJourney food-research agent. Read
      agents/food-research/PROMPT.md and follow it precisely.
      Target city: country_slug=<x>, city_slug=<y>, display_name=<z>,
      country_name=<w>. Categories to fill (others are already
      researched, leave them alone): <list of category slugs whose
      status is queued or needs_fixes>. After filling each category's
      JSON, atomically update data/locations.json so that
      cities[<...>].categories.<slug> = 'researched'. When all
      assigned categories are 'researched', exit."

6. Validation subagent dispatch (Agent tool, model=opus):
     "You are the TableJourney validation agent. Read
      agents/validation/PROMPT.md and follow it precisely.
      Target city: country_slug=<x>, city_slug=<y>.
      Categories to validate: <list of category slugs whose status
      is researched or needs_fixes>. Write your report to
      agents/validation/reports/<country>_<city>_<YYYY-MM-DD>.md
      ending with VERDICT: PASS or VERDICT: NEEDS_FIXES on the last
      line. For each category, atomically update
      data/locations.json: cities[<...>].categories.<slug>
      becomes 'validated' on PASS or 'needs_fixes' on FAIL.
      The whole-city VERDICT line is the rollup signal for the
      orchestrator."

7. Orchestrator reads the verdict line:
     tail -n 5 agents/validation/reports/<country>_<city>_<date>.md \
       | grep -E '^VERDICT:'
   Then re-reads data/locations.json to see which categories validated.

8. If every entity-bearing category for this city is 'validated':
     bash scripts/ship_city.sh <country> <city>
   On exit 0: update every category's status to 'deployed', and bump
   the city-level status to 'shipped'.

9. Refresh global pages every N shipped cities (covers cross-city
   interactions that single-city ship_city.sh doesn't touch):
     python scripts/generate_cross_cuts.py
     python scripts/generate_chrome_pages.py
     python scripts/generate_extras.py
     python scripts/generate_sitemap.py
     python scripts/generate_robots.py
     python scripts/generate_search_index.py
     sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content'

10. Loop.
```

### Atomic writes to locations.json

Every status update is a read-modify-write. To avoid race conditions
between subagents (or a subagent and the master), each agent:

1. Reads the whole file.
2. Mutates only its city's category entries.
3. Writes to `data/locations.json.tmp`, then `os.replace()` over the
   original.

This is enough because the orchestrator dispatches subagents one at a
time per city. (Cross-city parallelism is a future optimisation; if
introduced, switch to per-city tracker files or add a real lock.)

Stop conditions:
- All cities in `queued`/`scaffolded`/`researching`/`validating`/
  `needs_fixes`/`ready_to_ship` have been processed.
- A research or validation subagent returns a fatal error and master
  decides to halt for Lewis review.
- Lewis Ctrl+Cs the loop.

## Why we read `VERDICT:` from the report (not return value)

A subagent's return text isn't structured. The report file is. Putting
the verdict on a single grep-able line in the file gives the orchestrator
a clean handoff and gives Lewis a durable artifact to read later.

`tail -n 5 ... | grep -E '^VERDICT:'` matches even if the report ends
with trailing newlines, and the regex prevents false positives on
casual mentions of "verdict" earlier in the report.

## Helper script (suggested, not yet built)

Eventually this loop should be `scripts/orchestrate.py` that:
- Reads `data/locations.json`
- Writes status transitions atomically (open + write + os.replace)
- Returns the next city to process or `None` if done

Until that exists, the master Claude session can read/write
`data/locations.json` directly via the `Edit` tool. Writing a Python
helper is a minor optimisation; the JSON file is the contract.

## What stays human-gated (per Lewis's prior rules)

- **First US city (NYC) gets a manual review** before
  `ship_city.sh` is invoked. Master pauses after `ready_to_ship` and asks
  Lewis to inspect the data.
- **Caddy config changes, DNS, port-forwarding, sudoers**: never touched
  by the orchestrator.
- **Pre-scaffolding a whole tier**: never. Scaffolding is lazy, one city
  per iteration.

## Cost / time expectations (Lewis to confirm)

- Research subagent (Sonnet) per city: roughly 30-60 minutes of
  thinking + tool calls. Cost ballpark: per Lewis's "$20-50 per city"
  envelope.
- Validation subagent (Opus): typically faster than research (reads
  rather than writes), but Opus is pricier per token. Roughly half the
  cost of research.
- A clean run on one US city: research -> validate (PASS) -> ship.
  ~1-1.5 hours wall clock.
- A run with one fix cycle: research -> validate (NEEDS_FIXES) ->
  research -> validate (PASS) -> ship. ~2-2.5 hours wall clock.

## Failure modes the orchestrator should NOT silently recover from

- Validation report file doesn't exist after the validation subagent
  returns. Halt; Lewis investigates.
- `validate_data.py` ERRs after a research subagent claims done. Halt.
- `ship_city.sh` exit non-zero. Halt.
- `locations.json` not parseable. Halt.

In all halt cases: leave the city's status as-is so the next loop start
can resume.
