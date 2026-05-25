# Opus Final QA — spain/rioja

- **Agent:** Opus final QA (narrow read; should find nothing)
- **Date:** 2026-05-25
- **Entry state:** post-QA1 (Artadi DOCa-2015, 6 records) + QA2 (Campo Viejo +
  Ysios → Vinarchy ownership, 51 cuvée taste-evidence URL repairs). ship_safety
  PASS on entry (0 HARD, 7 layers).
- **Data:** 40 vineyards, 120 cuvées, 13 signature wines, 264 entities total.

## Verdict

**OPUS-FOUND-1.** One material defect CLASS confirmed (cuvée taste-note sourcing).
No fabrications, no fabricated credentials, no score inflation, no broken
cross-refs. The single finding is a citation-granularity / coverage-gap class
that survived QA1 + QA2 because no mechanical layer checks it. **No destructive
edit applied** (descriptors are accurate; see disposition). Flagged for
upstream-prompt + checker hardening, per the Opus brief.

---

## What was confirmed CLEAN

### QA1 + QA2 fix verification (re-confirmed, not re-done)
- **Artadi (QA1):** vineyard + 4 cuvées all read
  `"Vino de Espana (formerly DOCa Rioja, left 2015)"`; signature-wine record uses
  `style` not `classification` (no DOCa assertion). Prose explains the 2015
  withdrawal. Reads sensibly across all 5 records.
- **Vinarchy ownership (QA2):** `campo-viejo` + `bodegas-ysios` both read
  `"Vinarchy (Australian Wine Holdco / Accolade Wines, since 2025; formerly
  Pernod Ricard)"`. Correct and current.

### 30-entity skim (fabricated names / press credentials / claim-source mismatch)
- Sampled 30 entities across 17 topics. Zero fabricated winemaker names, zero
  fabricated press credentials.
- One name pattern surfaced ("sommelier Chefe Paniego", `el-portal-de-echaurren`)
  — **VERIFIED REAL**: José Félix "Chefe" Paniego is the actual sommelier (brother
  of chef Francis Paniego); restaurant is genuinely the first Michelin star in
  La Rioja's history. Not a defect.

### Itinerary end-to-end
- All 3 itineraries: every `days[*].venues[*]` slug (17 venue refs) resolves to a
  verified producer in `vineyards.json` (40 producers). 0 orphans.

### Festival end-to-end (manual month verify on a checker-UNKNOWN source)
- `fiesta-de-san-bernabe-logrono` claims `start_month: "June"` / "around 11 June".
  Manually confirmed via WebFetch (es.wikipedia source): "Se celebran en torno al
  día 11 de junio." Month claim CORRECT. (Deterministic checker returned UNKNOWN
  because the lariojaturismo source page is not date-specific.)

### Cuvée end-to-end
- Producer resolution: all 120 `wines[*].producer` resolve in `vineyards.json`.
- Tags: 48 distinct tags, ALL in `docs/WINE_TAGS.md`; zero derived-axis leakage.
- Vintage-agnostic: no 4-digit year in any cuvée slug or name.
- Pairings TJ refs: all distinct refs (10) under `spain/san-sebastian`; HEAD-checked
  2 live (`txuleta`, `bar-nestor`) → 200.

### Score backing (5 cuvées editorial_score >= 4.7, plus 99+ gate)
- ZERO scores >= 99 anywhere in the catalog (C2 numeric gate not triggered).
- 18 cuvées at editorial_score >= 4.7, all backed by Tim Atkin 94-98 / Wine
  Advocate 93-98 / Decanter 93-97 / Vinous 94-95 / Wine Spectator 95-97.
- Externally re-confirmed: La Rioja Alta GR 890 2010 = Tim Atkin **98** (matches
  data; multiple merchant + producer sources). Contador 2019 WA 98 within
  Contador's established band (QA1 disposition stands; it is a 98, not a 99+).

### Voice
- Zero em/en-dashes across all 26 JSON files (re-scanned).

---

## DEFECT O1 (CLASS) — cuvée taste-note `cuisine_evidence_url` does not substantiate descriptors

**Severity:** material (credibility vertical), but NON-destructive disposition.

**Finding.** The Opus brief asked me to "spot-check 2 of [the 51 QA2-repaired
URLs] actually substantiate the descriptors now." They do NOT. QA2's I1 fix moved
51 citations from the bare `riojawine.com/en-us/` homepage to the **producer's
homepage** — but a producer landing page substantiates per-wine aroma/palate
descriptors no better than the consortium homepage did. The tasting notes live on
per-cuvée sub-pages, not the landing page.

Quantified across the full 120-cuvée catalog by `cuisine_evidence_url` granularity:

| evidence_url shape | count | substantiates descriptors? |
|---|---|---|
| bare producer homepage (e.g. `bodegacontador.com/`, `artadi.com/en/`, `marquesderiscal.com/en/`) | 56 | **No** |
| consortium directory page (`riojawine.com/.../bodegas-rioja/<bodega>/`) | 60 | **No** (QA2 itself noted these carry no descriptors) |
| deeper sub-page (plausibly has notes) | 4 | maybe |

So **116 of 120 cuvées** cite a page that does not contain the
`taste.aroma`/`taste.palate` descriptors. Verified by WebFetch on the 2 brief-
mandated spot-checks:
- `bodegacontador.com/` → homepage, no descriptors, no cuvée notes (notes live
  under "NUESTROS VINOS" → per-wine detail pages).
- `marquesderiscal.com/en/` → homepage, names "Baron de Chirel" via a product
  image link but carries no tasting descriptors.

This violates PROMPT.md Section I ("`verified.cuisine_evidence_url` is a producer
tech sheet OR critic page that **actually contains** the descriptors used").

**Why it survived QA1 + QA2 + all 7 ship_safety layers.** Confirmed root cause:
`scripts/check_evidence_content.py` does **not** include `wines.json` in its
`ENTITY_LIST_KEYS`, and its only content-claim class is dietary. Cuvée taste-note
evidence URLs are therefore NEVER mechanically content-verified. QA2's I1 repair
was a strict improvement over the bare consortium homepage but stopped at the
producer homepage rather than the per-wine sub-page, and nothing caught that the
target still lacks descriptors.

**Disposition — NO destructive edit, deliberately.**
- The descriptors themselves are accurate (QA2 spot-verified Cirsion against the
  producer tech sheet; the Tempranillo cherry-family vocabulary is genuine, no
  template-fill fingerprint). Deleting accurate sensory copy over a citation-
  granularity issue would destroy correct, verifiable data.
- Repairing 116 URLs to per-cuvée sub-pages is a per-entity research task (each
  wine's detail-page path differs) and PROMPT.md explicitly warns that inventing
  per-wine URLs "would be worse." That work belongs to the research agent with
  live fetches, not a deterministic Opus rewrite.
- Editing 116 of 120 records mid-QA also exceeds the "narrow read, should find
  nothing" mandate and would not be safely verifiable in one pass.

I therefore flag the CLASS and leave the data unchanged. ship_safety remains PASS.

## Recommended hardening (upstream)

1. **Research prompt / SCHEMA.md:** `verified.cuisine_evidence_url` for a cuvée
   MUST be the per-wine detail page or a named critic note that contains the
   descriptors — NOT a producer homepage and NOT a consortium directory page.
   Add bare-homepage and `/bodegas-rioja/<x>/` directory URLs to the explicit
   reject list (mirror the riojawine.com homepage ban that QA2 introduced).
2. **`scripts/check_evidence_content.py`:** add `wines` to `ENTITY_LIST_KEYS`
   (remove `wines.json` from any implicit skip) and add a taste-claim class that
   requires at least one of the entity's `taste.aroma`/`taste.palate` descriptors
   (or the cuvée name + a tasting-note keyword) to appear on the fetched page.
   This is the missing mechanical gate; without it, fabricated OR mis-cited cuvée
   sensory copy ships silently.
3. **QA1/QA2 prompt:** Section I should require the spot-check to confirm the URL
   resolves to a page that *contains* the descriptors, not merely that the URL is
   "better than a homepage."

## Post-edit gate

No edits applied. `bash scripts/ship_safety.sh spain rioja` was PASS on entry and
remains PASS (data unchanged).

## OPUS-FOUND-1 spain/rioja
