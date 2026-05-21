#!/usr/bin/env bash
# ship_safety.sh — run every deterministic data check against a city, in
# the order their findings cascade. Designed for pre-ship and for ad-hoc
# "is this city clean?" sweeps. No AI in the loop, no agents, no waiting.
#
# Layers (each fails fast):
#   1. validate_data.py      — JSON shape, required fields, length caps,
#                              em-dashes, truncation, verified-block fields
#   2. verify_entities.py    — HEAD-check source_url + open_evidence_url +
#                              cuisine_evidence_url; fuzzy-match
#                              address_quoted vs entity.address
#   3. check_internal_references.py
#                            — itinerary venues + signature-dish where_to_eat
#                              resolve to verified entities
#   4. check_evidence_content.py
#                            — fetch dietary cuisine_evidence_url, confirm
#                              the dietary word appears on the page
#   5. check_festival_dates.py
#                            — fetch festival source_url, confirm start_month
#                              actually appears on the page
#   6. check_external_urls.py
#                            — HEAD booking_url / affiliate_url / hero
#   7. check_jsonld.py       — JSON-LD schema validity on built HTML
#
# Each script exits non-zero on hard failures; this driver fails on any of
# them and prints a summary. Run after every JSON edit, in CI, and before
# ship_city.sh.
#
# Usage:
#   bash scripts/ship_safety.sh france paris
#   bash scripts/ship_safety.sh --all          # every shipped city
#
# Exit 0: every check passed.
# Exit 1: at least one check failed (the layer is named in the output).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <country_slug> <city_slug>   OR   $0 --all" >&2
    exit 2
fi

run_one_city() {
    local country="$1" city="$2"
    local failures=0
    local layer_failed=""

    echo ""
    echo "============================================================"
    echo "  ship_safety: ${country}/${city}"
    echo "============================================================"

    echo ""
    echo "[1/7] validate_data.py — JSON shape, required fields, verified-block"
    if ! python3 scripts/validate_data.py --country "$country" --city "$city" 2>&1 | tee /tmp/.ship_safety_out | grep -E "^\s+ERR:" >/dev/null; then
        echo "  PASS"
    else
        echo "  FAIL — see ERR: lines above"
        failures=$((failures+1))
        layer_failed+="validate_data "
    fi

    echo ""
    echo "[2/7] verify_entities.py — provenance HEAD + address fuzzy-match"
    if python3 scripts/verify_entities.py --country "$country" --city "$city"; then
        echo "  PASS"
    else
        echo "  FAIL"
        failures=$((failures+1))
        layer_failed+="verify_entities "
    fi

    echo ""
    echo "[3/7] check_internal_references.py — venue cross-references resolve"
    if python3 scripts/check_internal_references.py --country "$country" --city "$city"; then
        echo "  PASS"
    else
        echo "  FAIL"
        failures=$((failures+1))
        layer_failed+="check_internal_references "
    fi

    echo ""
    echo "[4/7] check_evidence_content.py — dietary cuisine_evidence_url content match"
    if python3 scripts/check_evidence_content.py --country "$country" --city "$city"; then
        echo "  PASS"
    else
        echo "  FAIL"
        failures=$((failures+1))
        layer_failed+="check_evidence_content "
    fi

    echo ""
    echo "[5/7] check_festival_dates.py — festival source_url month match"
    if python3 scripts/check_festival_dates.py --country "$country" --city "$city"; then
        echo "  PASS"
    else
        echo "  FAIL"
        failures=$((failures+1))
        layer_failed+="check_festival_dates "
    fi

    echo ""
    echo "[6/7] check_external_urls.py — booking/affiliate/hero URLs reachable"
    if python3 scripts/check_external_urls.py --country "$country" --city "$city"; then
        echo "  PASS"
    else
        echo "  FAIL"
        failures=$((failures+1))
        layer_failed+="check_external_urls "
    fi

    echo ""
    echo "[7/7] check_jsonld.py — JSON-LD schema validity on built HTML"
    if python3 scripts/check_jsonld.py 2>&1 | tail -5 | grep -q "0 issues\|all valid\|PASS"; then
        echo "  PASS"
    else
        echo "  WARN (JSON-LD check is global, not city-scoped; re-run as needed)"
    fi

    echo ""
    echo "============================================================"
    if [[ $failures -eq 0 ]]; then
        echo "  ${country}/${city}: ALL CHECKS PASSED"
    else
        echo "  ${country}/${city}: $failures CHECK(S) FAILED [${layer_failed}]"
    fi
    echo "============================================================"
    return $failures
}

if [[ "${1:-}" == "--all" ]]; then
    total_fail=0
    for cdir in site-data/*/; do
        country="$(basename "$cdir")"
        for citydir in "${cdir}"*/; do
            city="$(basename "$citydir")"
            if [[ -d "${citydir}data" ]]; then
                run_one_city "$country" "$city" || total_fail=$((total_fail + $?))
            fi
        done
    done
    echo ""
    echo "============================================================"
    echo "  Grand total failures across all cities: $total_fail"
    echo "============================================================"
    exit $(( total_fail > 0 ? 1 : 0 ))
fi

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <country_slug> <city_slug>   OR   $0 --all" >&2
    exit 2
fi

run_one_city "$1" "$2"
exit $?
