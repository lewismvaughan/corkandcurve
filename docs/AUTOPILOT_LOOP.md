# Autopilot loop prompt

Paste the body below into `/loop` (no interval — let the model self-pace).
Each tick advances whatever stage is next per city, and spins up new cities
from `docs/CITY_ROADMAP.md` whenever the in-flight count drops below 5.

---

## /loop prompt body (copy from here down)

You are running the TableJourney city pipeline on autopilot.

Read these first (every tick):
1. `docs/HANDOFF.md` — current state, pipeline stages, soft-error checklist
2. `docs/FLOW.md` — pipeline contract
3. `docs/CITY_ROADMAP.md` — next cities to research (priority order)
4. `agents/food-research/PROMPT.md`, `agents/qa/PROMPT.md` — agent contracts

### Stages per city (THE pipeline — do not skip)

```
1. food-research        — agent fills site-data/<country>/<city>/data/*.json
2. ship_safety.sh       — deterministic gate (0 HARD required to advance)
3. fixup agent          — only if ship_safety failed; re-run gate after
4. QA1                  — Sonnet judgment pass; writes reports/<c>_<city>_<date>.md
5. QA2                  — independent Sonnet pass; reads QA1 report; writes _qa2_
6. Opus final           — Opus narrow read; writes _opus_; ideally zero defects
7. ship_city.sh         — generates HTML, geocodes, sitemap, OG, maps
8. chmod                — sshp host with TJ_SUDO_PASS from .env.local
9. live smoke           — curl HTTPS for the city + one entity, expect 200
```

### Each tick: do the following IN ORDER

#### Step A — survey in-flight state

List which Polish (and any other in-flight) cities exist in `site-data/`,
and determine their current stage:

- Stage 1 done if `site-data/<c>/<city>/data/<topic>.json` files are non-empty
- Stage 2 done if `bash scripts/ship_safety.sh <c> <city>` exits 0
- Stage 4-6 done if the matching report exists in `agents/qa/reports/`
  (filenames: `<c>_<city>_2026-MM-DD.md` for QA1, `_qa2_` for QA2,
  `_opus_` for Opus final)
- Stage 7 done if `content/<c>/<city>/index.html` exists and `mtime` is
  newer than the latest QA report for that city
- Stage 9 done if a recent curl shows HTTP 200 on the city URL

#### Step B — advance every city by exactly one stage if it's ready

For each city, run the lowest-numbered unfinished stage. **Run multiple
cities in parallel** — they're independent. Use `Agent` background dispatches
for stages 1, 3, 4, 5, 6. Use `Bash run_in_background` for stages 2, 7, 8, 9.

Dispatch templates (always brief like the Polish-batch session — include
Polish-batch defect classes from memory if applicable: address_quote
discipline, source_domain diversity, stale_venue_check, address_hallucination,
url_fabrication; plus the QA prompt's E3 phantom-venue + E4 verified-block
consistency rules).

#### Step C — refill the pipeline

Count in-flight cities (those not at stage 9). If `< 5`:

1. Open `docs/CITY_ROADMAP.md`, pick the next un-scaffolded city
   (skip any already in `site-data/`)
2. `python3 scripts/new_city.py <country_slug> <city_slug> --name <Name> --country <Country>`
3. Dispatch the stage-1 research agent for it (background)
4. Update `data/locations.json` if it exists with `status: "researching"`

Repeat until in-flight count reaches 5.

#### Step D — wait + tick again

You will be notified when background agents complete. Don't poll. After
all current notifications drain, call `ScheduleWakeup` with
`delaySeconds: 1800` (30 min — past prompt-cache TTL, but worth the cost
since most stages take 10-30 min wall time) and prompt = this same
`/loop` body. The runtime clamps to [60, 3600].

### Hard rules (do NOT violate)

1. **NEVER skip stages 5 (QA2) or 6 (Opus final).** Single-pass QA leaks.
2. **NEVER ship a city with non-zero HARD ship_safety failures.** Re-run
   the fixup agent or fix the JSON yourself.
3. **NEVER commit or push to git** unless the user explicitly asks.
4. **chmod uses `.env.local` for `TJ_SUDO_PASS`** — source it first, then
   `sshp host "echo $TJ_SUDO_PASS | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content"`.
5. **Geocode 429s**: if Nominatim returns 429 mid-ship, the ship_city
   step 2f run will record failures in `data/geocode-failures.txt`. Don't
   block ship on that — the soft-fail-report covers it. Re-geocode the
   affected city later when rate-limit clears (probe with a single
   `Plac Solny 4 Wroclaw` lookup; 429 = wait 5 min and retry; JSON body
   = proceed). The city ships either way.
6. **Em-dash / en-dash ban** is enforced by validate_data.py — agent
   prompts must repeat this.
7. **Polish characters** (`ł`, `ż`, `ę`, `ń`, `ś`, `ć`, `ó`, `ą`)
   preserved literally. `ł` is not a diacritic, don't strip it.
8. **Fixup agents must NOT copy `entity.address` into `address_quoted`** —
   re-fetch the source URL and quote what's actually displayed.
9. **One source domain per ~5 entities max** — diversify URLs to avoid
   single-directory-collapse defects (Polish-batch inyourpocket pattern).

### End-of-tick validation

Before scheduling the next wakeup, run:

```bash
# How many cities are at each stage
for c in site-data/poland/*/; do
  city=$(basename "$c")
  printf "%-12s " "$city"
  # quick stage probe: any QA report present?
  ls agents/qa/reports/poland_${city}_*.md 2>/dev/null | wc -l
done
```

If any city has been stuck on the same stage for >3 ticks, dump its
latest log to a one-line summary in your end-of-turn message so the user
sees it on next session.

### State persistence between ticks

You don't have a state file. Treat the filesystem (site-data/, content/,
agents/qa/reports/, data/locations.json) as the canonical state. If state
seems unclear, **survey before acting**.

### Stopping criteria (BE CONSERVATIVE — when in doubt, reschedule)

`ScheduleWakeup` is the heartbeat. **Omit it ONLY** when BOTH of these
are true on this tick:

1. `docs/CITY_ROADMAP.md` lists zero un-scaffolded cities (or doesn't exist), AND
2. Every city in `site-data/` has shipped (content/<c>/<city>/index.html
   exists AND a recent curl returned 200 AND there are no fresh
   in-flight markers under `.autopilot/in_flight/`).

If either condition is false → ScheduleWakeup MUST be called.

When omitting ScheduleWakeup as the final tick:
- Run global sweep (sitemap + robots + search_index + chmod)
- Print a one-paragraph end-of-batch summary (cities shipped, defect
  patterns observed, anything queued for follow-up)
- Then end the response without ScheduleWakeup

### Safety guards (read this every tick — these prevent "dumb stuff")

**G1. Never schedule a duplicate-stage agent for a city.**

When you dispatch a stage-K agent for city X, IMMEDIATELY write a marker:

```bash
mkdir -p /station/repo/.autopilot/in_flight
date -u +%s > /station/repo/.autopilot/in_flight/<city>_<stage>.ts
```

At the top of every tick, list `.autopilot/in_flight/` and treat each
file as "this stage is in flight, do NOT dispatch again." Compare the
timestamp to `date +%s`:
- < 90 min old → assume still running, skip
- 90-240 min old → likely dead (parent timeout, network issue), check
  whether the expected output file exists; if yes, clear the marker;
  if no, the agent crashed — dispatch ONE retry
- > 240 min old → stale, clear and re-dispatch

When the expected output appears (e.g. the QA report file), remove the
marker before advancing to the next stage.

**G2. Never start ship_city.sh for two cities at once.**

ship_city.sh step 9 regenerates the GLOBAL sitemap + search index. Two
runs racing here corrupt the output. Treat ship_city as a city-level
mutex: at most one running at a time. Marker:
`.autopilot/in_flight/SHIP_GLOBAL_LOCK.ts`. Acquire before invoking
ship_city.sh, release after.

Other stages (research, ship_safety, QA1/QA2/Opus) are independent and
SHOULD run in parallel.

**G3. Never re-dispatch a stage whose output already exists.**

Before dispatching stage K for city X, check that the output file for
stage K does NOT already exist:
- Stage 4 (QA1): `agents/qa/reports/<c>_<city>_<TODAY>.md`
- Stage 5 (QA2): `agents/qa/reports/<c>_<city>_qa2_<TODAY>.md`
- Stage 6 (Opus): `agents/qa/reports/<c>_<city>_opus_<TODAY>.md`
- Stage 7 (ship): `content/<c>/<city>/index.html` AND mtime newer than
  Opus report

If output exists, the stage is DONE — advance, don't re-dispatch.

**G4. Never ship a city whose latest QA verdict is NEEDS_FIXES.**

The ship_city.sh gate enforces this, but check it yourself first to
avoid burning the dispatch slot. If Opus says NEEDS_FIXES → dispatch
a targeted fixup agent first, then re-run Opus, THEN ship.

**G5. Never call ScheduleWakeup with a prompt other than the /loop body.**

The `prompt` arg to ScheduleWakeup must be the EXACT /loop input the
user provided. Don't paraphrase, don't add context — re-paste it
verbatim. This is what keeps the loop self-sustaining.

**G6. Never assume "nothing to do" without surveying.**

The filesystem is the source of truth. If `ls .autopilot/in_flight/`
shows nothing AND no city is at a finishable stage AND the roadmap is
empty → THEN you can end. Otherwise always ScheduleWakeup.

**G7. Polling external state must respect rate limits.**

If you find Nominatim returning 429 mid-tick, log it and proceed. Do
NOT block the tick on polling Nominatim — the geocode failures are a
soft-error to be addressed during stage 9 cleanup, not a ship blocker.

**G8. Crash-safety for marker files.**

If a tick begins with markers older than 240 min, those agents are
almost certainly dead (parent session terminated). Clear them and
dispatch the corresponding stages from scratch — don't assume "still
running."

### Memory check

Before dispatching a research agent, scan memory for defect classes:
- `feedback-address-quote-discipline`
- `feedback-source-domain-diversity`
- `feedback-stale-venue-check`
- `feedback-address-hallucination`
- `feedback-url-fabrication`
- `feedback-provenance-required`
- `feedback-no-em-dashes`
- `feedback-real-url-fake-address`
- `feedback-booking-url-flaky`
- `feedback-dietary-evidence-sources`

Include the relevant rules in every research and QA dispatch prompt so the
agent doesn't relearn defects we already cataloged.
