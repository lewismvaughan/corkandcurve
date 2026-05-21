#!/usr/bin/env bash
# ship_city_full.sh — canonical end-to-end ship pipeline for a city.
#
# Enforces the 4-stage validation architecture:
#
#   sonnet research  ->  mechanical pass-1 (ship_safety.sh)
#                    ->  sonnet QA pass-1   (judgment defects)
#                    ->  sonnet QA pass-2   (resample, different slices)
#                    ->  small Opus final   (narrow read on residual flags)
#                    ->  ship_city.sh       (push live + chmod + smoke)
#
# Built 2026-05-19 after batch-3 (Berlin, Edinburgh, Milan, Naples) shipped
# pre-QA because their research agents ran ship_city.sh themselves. The
# foreground orchestrator now uses THIS wrapper instead of ship_city.sh
# directly. The wrapper REFUSES to push pages live until all three QA
# reports exist at known paths and each ends with `VERDICT: PASS`.
#
# Research-agent prompts (agents/food-research/PROMPT.md) must instruct
# agents to stop at READY-TO-SHIP and never run ship_city.sh / generators
# themselves; the orchestrator dispatches QA agents and runs ship_city.sh.
#
# Usage:
#   bash scripts/ship_city_full.sh france lyon
#   bash scripts/ship_city_full.sh italy naples 2026-05-19   # explicit date suffix
#
# Exit codes:
#   0   shipped clean
#   1   mechanical pass-1 failed, fix and retry
#   2   QA report missing for a stage, dispatch the agent and retry
#   3   QA report present but VERDICT != PASS, fix and retry
#   4   ship_city.sh itself failed (rare; see its output)

set -euo pipefail

if [[ $# -lt 2 ]]; then
    cat >&2 <<EOF
Usage: $0 <country_slug> <city_slug> [<date_yyyy-mm-dd>]

The optional date is the suffix expected on QA report filenames; defaults to
today (UTC). Use it to ship from QA reports written on a prior date.
EOF
    exit 2
fi

COUNTRY="$1"
CITY="$2"
DATE="${3:-$(date -u +%Y-%m-%d)}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

REPORT_DIR="agents/qa/reports"
PASS1_REPORT="${REPORT_DIR}/${COUNTRY}_${CITY}_${DATE}.md"
PASS2_REPORT="${REPORT_DIR}/${COUNTRY}_${CITY}_${DATE}_pass2.md"
FINAL_REPORT="${REPORT_DIR}/${COUNTRY}_${CITY}_${DATE}_opus_final.md"

banner() {
    echo
    echo "============================================================"
    echo "  $*"
    echo "============================================================"
}

require_pass_verdict() {
    local stage="$1"
    local report="$2"
    if [[ ! -f "$report" ]]; then
        cat >&2 <<EOF

BLOCKED: ${stage} report not found at:
   $report

Dispatch a ${stage} agent before retrying:
  - Sonnet QA pass 1 / 2: agents/qa/PROMPT.md
  - Opus final: agents/qa/PROMPT.md (small, narrow read on residual flags)
  - All run as Sonnet 4.6 except the final, which is Opus on a tight scope.

Foreground orchestrator (Claude Code main session) dispatches via the
Agent tool with model=sonnet / model=opus. Agents write to the report
path above. Then re-run this script.
EOF
        exit 2
    fi
    if ! grep -qE '^VERDICT: PASS\b' "$report"; then
        cat >&2 <<EOF

BLOCKED: ${stage} report at $report does NOT end with 'VERDICT: PASS'.

The QA agent flagged defects it could not auto-resolve, or it kicked the
city back for research. Read the report, address each defect, re-dispatch
the same stage's QA agent (it will rewrite the report), then re-run this
script. Do not edit the verdict by hand.
EOF
        exit 3
    fi
    echo "  ✓ ${stage}: $report (VERDICT: PASS)"
}

banner "ship_city_full ${COUNTRY}/${CITY} (date suffix ${DATE})"

banner "Stage 0/4  mechanical pass-1: ship_safety.sh (fast, deterministic)"
# ship_safety runs 7 checks. Any HARD/FAIL means we stop before any agent
# does judgment work that would be wasted on a city with mechanical defects.
if ! bash scripts/ship_safety.sh "$COUNTRY" "$CITY"; then
    cat >&2 <<EOF

BLOCKED: ship_safety.sh failed.

Mechanical defects must be resolved before QA. Common causes:
  - HARD addr_mismatch (verified.address_quoted does not match entity.address)
  - HARD dead_source_url (a verified.source_url returns 404 / dead domain)
  - check_internal_references ERR (signature-dishes mentions a venue not in any topic)
  - check_external_urls broken (booking_url / hero_image / og_image dead)

Either dispatch a research agent to fix, or patch the JSON by hand. Re-run
this script after fixes.
EOF
    exit 1
fi

banner "Stage 1/4  Sonnet QA pass 1 report gate"
require_pass_verdict "QA pass 1" "$PASS1_REPORT"

banner "Stage 2/4  Sonnet QA pass 2 report gate"
require_pass_verdict "QA pass 2" "$PASS2_REPORT"

banner "Stage 3/4  small Opus final report gate"
require_pass_verdict "Opus final" "$FINAL_REPORT"

banner "Stage 4/4  ship_city.sh (push live + chmod + smoke)"
# ship_city.sh re-runs its own QA gate looking for a single pass-1 report;
# both gates being satisfied is intentional (the wrapper's gates are
# stricter; ship_city's gate is the per-day-report contract that already
# exists). The expectation is that pass-1, pass-2, and opus_final reports
# all sit at the path layout above.
if ! bash scripts/ship_city.sh "$COUNTRY" "$CITY"; then
    cat >&2 <<'EOF'

BLOCKED: ship_city.sh failed AFTER all QA gates cleared.

This is unusual; ship_city.sh runs its own pass-1 (validate_data,
cleanup_broken_urls, verify_entities, check_internal_references). If
it failed, something changed between QA agent run and now (the agent
edited a file, or a URL went dead). Re-run this script.
EOF
    exit 4
fi

banner "DONE: ${COUNTRY}/${CITY} shipped via the 4-stage QA pipeline."
echo "Live at https://tablejourney.com/${COUNTRY}/${CITY}/"
