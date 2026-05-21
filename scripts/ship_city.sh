#!/usr/bin/env bash
# ship_city.sh, one-shot pipeline runner for a single city.
#
# Runs every step from finalised JSON to live URLs:
#   inject_slugs -> validate_data -> cleanup_broken_urls -> qa_gate -> generate_city -> generate_entity_pages
#   -> generate_cross_cuts -> generate_extras -> generate_chrome_pages
#   -> generate_homepage -> generate_sitemap -> generate_robots
#   -> generate_search_index -> chmod -> smoke-test
#
# Pre-conditions:
#   - site-data/<country>/<city>/data/*.json filled by the food-research agent.
#   - You are on server-3 (or another host that can reach the live site).
#
# Usage:
#   bash scripts/ship_city.sh france paris
#   bash scripts/ship_city.sh japan tokyo
#
# Exits non-zero the moment any step fails. Validators are hard gates;
# generators are not retried.

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <country_slug> <city_slug>" >&2
    echo "Example: $0 france paris" >&2
    exit 2
fi

COUNTRY="$1"
CITY="$2"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Source local secrets (TJ_SUDO_PASS for the host chmod step). Optional —
# the chmod is conditional on `command -v sshp`, so missing .env.local just
# means the chmod step warns instead of fixing perms.
if [[ -f .env.local ]]; then
    set -a; source .env.local; set +a
fi

DATA_DIR="site-data/${COUNTRY}/${CITY}/data"
if [[ ! -d "$DATA_DIR" ]]; then
    echo "ERROR: $DATA_DIR does not exist. Did you run new_city.py?" >&2
    exit 1
fi

step() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
}

step "1/11  inject slugs + normalise addresses (${COUNTRY}/${CITY})"
python3 scripts/inject_slugs.py "$COUNTRY" "$CITY"

step "2/11  validate JSON (hard gate)"
python3 scripts/validate_data.py --city "$CITY"

step "2b/11  verify outbound URLs (hard gate: removes 404/dead-domain booking_urls)"
# Idempotent: removes broken booking_url / affiliate_url / hero_image_source_url
# fields from the JSON. 401/403 (anti-bot) are preserved. See
# scripts/cleanup_broken_urls.py for the policy. This MUST run before HTML is
# rendered, otherwise we ship pages with "Book to" links to dead domains.
python3 scripts/cleanup_broken_urls.py --country "$COUNTRY" --city "$CITY"

step "2c/11  mechanical per-entity provenance check (hard gate)"
# Reads each entity's `verified` block: HEAD-checks source_url,
# fuzzy-matches address_quoted vs entity.address, flags stale/closed.
# This is pass-1 of the two-pass QA architecture: existence and address
# class are mechanical and reproducible here, so the LLM QA pass-2 below
# is free to focus on judgment defects (route fabrication, cuisine vs
# evidence mismatch, festival month sanity, prose echoes). Exits non-zero
# on hard failures.
python3 scripts/verify_entities.py --country "$COUNTRY" --city "$CITY"

step "2d/11  cross-reference check: itinerary + signature-dish venue mentions (hard gate)"
# Every venue named in signature-dishes.where_to_eat must resolve to a
# verified entity in this city. Each itinerary day must list `venues:
# [slugs]` and each slug must resolve. Closes the last fabrication path:
# research agent can no longer mention a venue in editorial content that
# doesn't exist as a verified entity elsewhere in the dataset.
python3 scripts/check_internal_references.py --country "$COUNTRY" --city "$CITY"

step "2e/11  QA judgment-pass gate (must have today's QA report with VERDICT: PASS)"
# The agent flow for a city is research -> validate -> QA1 -> QA2 -> Opus
# final -> ship. Each LLM pass writes a separate report; the LATEST pass's
# verdict is what gates ship. QA1 can return NEEDS_FIXES — that's a normal
# upstream-defect signal, fixed by QA2/Opus later. What matters is the final
# pass (Opus, or QA2 if Opus hasn't run yet) signs off with VERDICT: PASS.
TODAY=$(date -u +%Y-%m-%d)
QA1_REPORT="agents/qa/reports/${COUNTRY}_${CITY}_${TODAY}.md"
QA2_REPORT="agents/qa/reports/${COUNTRY}_${CITY}_qa2_${TODAY}.md"
OPUS_REPORT="agents/qa/reports/${COUNTRY}_${CITY}_opus_${TODAY}.md"
# Walk newest-first: Opus, then QA2, then QA1.
QA_REPORT=""
for candidate in "$OPUS_REPORT" "$QA2_REPORT" "$QA1_REPORT"; do
    if [[ -f "$candidate" ]]; then
        QA_REPORT="$candidate"
        break
    fi
done
if [[ -z "$QA_REPORT" ]]; then
    echo "BLOCKED: no QA report found for ${COUNTRY}/${CITY} on ${TODAY}." >&2
    echo "         Run QA1 (agents/qa/PROMPT.md) against $COUNTRY/$CITY first." >&2
    exit 1
fi
if ! grep -qE '^VERDICT: PASS\b' "$QA_REPORT"; then
    echo "BLOCKED: latest QA report at $QA_REPORT does not end with 'VERDICT: PASS'." >&2
    echo "         If this was QA1 or QA2 and you intended to continue, run the" >&2
    echo "         next pass (QA2 or Opus final) — its verdict is what gates ship." >&2
    exit 1
fi
echo "QA pass confirmed: $QA_REPORT"

step "2f/11  geocode entity addresses (post-QA, idempotent via cache)"
# Runs ONLY after every QA gate has passed (mechanical pass-1 in 2a-2d,
# judgment pass-2 in 2e, and the 4-stage wrapper in ship_city_full.sh
# requires QA1/QA2/Opus reports). That way we never spend the
# rate-limited Nominatim budget on addresses an agent later corrects or
# an entity QA later drops. Cache lives at data/geocode-cache.json and
# is committed to git — re-shipping a city is free on cache hits.
# v3 algorithm: canonical -> venue-prefix strip -> suite strip -> combo
# strip -> postcode centroid. Each cache entry records which strategy
# resolved it.
python3 scripts/geocode_entities.py --city "$CITY"

step "2g/11  geocode coverage report (soft — flags addresses needing refinement)"
# Lists any entities whose address still didn't resolve after v3, so an
# editor can either refine the address text or accept the entity as
# inherently un-mappable (food tour with no fixed venue, "throughout X").
# SOFT FAIL by default — surfaces gaps without blocking ship. Switch to
# --hard --threshold 0.85 if a hard ship-gate becomes desirable.
python3 scripts/check_geocode_coverage.py "$COUNTRY" "$CITY" || true

step "2h/11  geocode outlier sweep (soft — pins >50km from city centroid)"
# Catches Nominatim country-fallback bugs (entity.address says in-city but
# coords landed in Lamia / Albany / Seville / etc.). Soft gate — informational
# only. See `scripts/qa_geo_outliers.py` + memory note `reference_qa_geo_outliers`.
python3 scripts/qa_geo_outliers.py --threshold 50 --bugs-only 2>&1 | head -40 || true

step "3/11  render city hub + topic pages"
python3 scripts/generate_city.py "$COUNTRY" "$CITY"

step "4/11  render per-entity pages"
python3 scripts/generate_entity_pages.py "$COUNTRY" "$CITY"

step "5/11  refresh cross-cut landings (cuisine, dish, neighborhood)"
python3 scripts/generate_cross_cuts.py

step "5b/11 refresh country + city scoped cross-cut indexes (/<country>/cuisines/ etc.)"
# Must run AFTER generate_cross_cuts.py (reads its enriched manifests) and
# BEFORE generate_sitemap.py (so the scoped URLs ship to Google).
python3 scripts/generate_scoped_cross_cuts.py

step "5c/11 refresh city × dietary pages (/<country>/<city>/dietary/<diet>/)"
# Reads each city's dietary.json directly; >= 2 entities per (city, diet)
# combination to avoid thin pages.
python3 scripts/generate_city_dietary.py

step "5d/11 refresh city × cuisine pages (/<country>/<city>/cuisine/<slug>/)"
# Buckets restaurants/casual_dining/fine_dining by canonical cuisine class;
# >= 2 entities per (city, cuisine) to avoid thin pages.
python3 scripts/generate_city_cuisine.py

step "5e/11 refresh city × dish pages (/<country>/<city>/dish/<slug>/)"
# Resolves dish.where_to_eat venue names against every entity-bearing
# topic in the same city; targets "where to eat <dish> in <city>" queries.
python3 scripts/generate_city_dish.py

step "5e1/11 refresh city × nightlife-subcategory pages"
# /<country>/<city>/nightlife/{dance-clubs,live-music,rooftop-bars,speakeasies,lgbtq,listening-bars,late-night-dives}/
python3 scripts/generate_city_nightlife_sub.py

step "5e2/11 refresh country × topic rollup pages"
# /<country>/<topic>/  top entities across the country for each food topic
python3 scripts/generate_country_topic.py

step "5e3/11 refresh country × nightlife-subcategory rollups"
# /<country>/nightlife/<sub>/  top nightlife rooms across the country
python3 scripts/generate_country_nightlife_sub.py

step "5e4/11 refresh country × cuisine rollups"
# /<country>/cuisine/<x>/  top cuisine rooms across the country
python3 scripts/generate_country_cuisine.py

step "5e5/11 refresh country × dish rollups"
# /<country>/dish/<x>/  signature-dish variants across the country
python3 scripts/generate_country_dish.py

step "5e6/11 refresh country × dietary rollups"
# /<country>/dietary/<diet>/  top dietary rooms across the country
python3 scripts/generate_country_dietary.py

step "5e7/11 refresh neighborhood × cuisine pages"
# /neighborhood/<city>/<nbhd>/<cuisine>/  + injects "Cuisines in this
# neighborhood" block back into each parent /neighborhood/<city>/<nbhd>/
# (no-orphan wiring).
python3 scripts/generate_neighborhood_cuisine.py

step "5e8/11 refresh global top-topic rollups"
# /rooftops/, /speakeasies/, /best-brunch/, etc — cross-city editor lists.
python3 scripts/generate_global_top_topics.py

step "5e9/11 refresh city × price-tier pages"
# /<country>/<city>/cheap-eats/, /mid-range/, /upscale/, /splurge/
python3 scripts/generate_city_price_tier.py

step "5e10/11 refresh city × topic × time-of-day pages"
# /<country>/<city>/brunch/sunday/, /restaurants/sunday/, /bars/late/, etc.
python3 scripts/generate_city_topic_when.py

step "5e11/11 emit stub indexes for countries missing region.json"
# /<country>/index.html for any country whose data lacks data/region.json
# but whose subtree contains cities or rollups (Germany etc). Prevents
# orphan country rollup pages.
python3 scripts/generate_country_stubs.py

step "5f/11 (re)build branded per-city OG cards (/og/<city>.jpg)"
# Downloads each city's hero_image, applies the same gradient + wordmark
# treatment as the homepage OG. Idempotent (caches the downloads).
python3 scripts/build_og_cities.py

step "5g/11 build static map thumbnails per geocoded entity + city pins.json"
# Static JPEG per entity (entity page thumbnail) + lean pins JSON per
# city (consumed by the city-hub Leaflet map, lazy-loaded). Both are
# idempotent: only entities present in data/geocode-cache.json get
# mapped, so a partial cache produces partial maps.
python3 scripts/build_entity_maps.py --city "$CITY"
python3 scripts/build_city_pins.py --city "$CITY"

step "6/11  refresh chrome (homepage extras, OG, logo, 404, feed, cross-city topics)"
python3 scripts/generate_extras.py

step "7/11  refresh chrome pages (/about/, /cities/, /topics/, legal)"
python3 scripts/generate_chrome_pages.py

step "8/11  re-render homepage"
python3 scripts/generate_homepage.py

step "8b/11  refresh country + state index pages"
python3 scripts/generate_region_page.py "$COUNTRY"
python3 scripts/generate_state_pages.py "$COUNTRY"

step "9/11  refresh sitemap + robots + search index"
python3 scripts/generate_sitemap.py
python3 scripts/generate_robots.py
python3 scripts/generate_search_index.py

step "10/12  chmod content/ for Caddy"
if command -v sshp >/dev/null 2>&1; then
    sshp host 'echo "${TJ_SUDO_PASS:?TJ_SUDO_PASS not set; source .env.local first}" | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content' >/dev/null
    echo "chmod a+rX applied via sshp host"
else
    echo "WARNING: 'sshp' not on PATH, skipping chmod. New files will 404 publicly until you run:"
    echo "  sshp host 'echo "${TJ_SUDO_PASS:?TJ_SUDO_PASS not set; source .env.local first}" | sudo -S chmod -R a+rX /opt/claude-stations/tablejourney/repo/content'"
fi

step "11/12  validate rendered HTML (hard gate on em/en dashes + placeholders)"
python3 scripts/validate_seo.py | tail -10

step "12/12  IndexNow ping (Bing + Yandex same-day re-crawl)"
python3 scripts/indexnow_ping.py --city "$COUNTRY" "$CITY" || echo "  (indexnow non-fatal; skipping)"

step "smoke test live URLs"
if command -v sshp >/dev/null 2>&1; then
    URLS=(
        "/"
        "/${COUNTRY}/${CITY}/"
        "/${COUNTRY}/${CITY}/restaurants/"
        "/${COUNTRY}/${CITY}/signature-dishes/"
    )
    for url in "${URLS[@]}"; do
        code=$(sshp host "curl -sS -o /dev/null -w '%{http_code}' https://tablejourney.com${url}" 2>/dev/null || echo "ERR")
        echo "  ${code}  https://tablejourney.com${url}"
    done
else
    echo "  (sshp not available; skipping live smoke test)"
fi

echo ""
echo "DONE: ${COUNTRY}/${CITY} shipped. Pages live at https://tablejourney.com/${COUNTRY}/${CITY}/"
