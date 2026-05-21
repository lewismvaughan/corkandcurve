# TableJourney Validation Agent — DEPRECATED 2026-05-18

**This agent is retired.** The multi-round LLM validation pipeline it
described did not converge: each round picked a different slice of
entities to re-check and the "100% sweep" was instruction-only with no
enforcement. ~199 closed/fabricated/wrong-address entities slipped
through across 5 cities (NYC, LA, SF, Chicago, Paris).

The work this agent used to do is now split across:

1. **Structural provenance (mandatory `verified` block on every entity)**
   — encoded in `agents/food-research/SCHEMA.md` "Provenance block
   (`verified`)" and enforced by `scripts/validate_data.py`.
2. **Deterministic mechanical pass-1** — `scripts/verify_entities.py`
   HEAD-checks every `source_url`, fuzzy-matches `address_quoted` against
   `entity.address`, rejects mismatches. No LLM needed.
3. **Cross-reference resolution** — `scripts/check_internal_references.py`
   confirms `signature-dishes[*].where_to_eat` and
   `itineraries[*].days[*].venues` resolve to verified entities.
4. **Evidence content match** — `scripts/check_evidence_content.py`
   fetches `cuisine_evidence_url` for dietary entries and confirms the
   dietary keyword appears.
5. **Festival month sanity** — `scripts/check_festival_dates.py` fetches
   organizer site and verifies claimed `start_month`.
6. **External URL liveness** — `scripts/check_external_urls.py` HEADs
   `booking_url`/`affiliate_url`/`hero_image_source_url`.
7. **JSON-LD schema validity** — `scripts/check_jsonld.py`.

The single canonical driver that runs all 7 checks in sequence is:

    bash scripts/ship_safety.sh <country> <city>

Any layer failing blocks ship. Research agent PROMPT (`agents/food-research/PROMPT.md`)
hard-references this gate.

The remaining judgment work that scripts can't catch — cuisine claim
content match (Chez Imo class), tour route fabrication on real
operators, festival prose / month echoes, thin-category fabrication —
is handled by **`agents/qa/PROMPT.md`** (judgment-only pass-2).

## If you arrived here looking for "the validation agent"

- For automated checks: `bash scripts/ship_safety.sh <country> <city>` is the gate.
- For LLM judgment review: `agents/qa/PROMPT.md`.
- For the contract research agents follow: `agents/food-research/PROMPT.md`.

Old reports under `agents/validation/reports/` are kept as historical
record of the multi-round pipeline. Do not write new validation reports
here.
