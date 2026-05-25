# Opus final QA — italy/piedmont

- Agent: Opus final QA (narrow read; verdict pass)
- Date: 2026-05-25
- Upstream: QA1-COMPLETE (5 address fixes; Gaja crus verified Barbaresco DOCG),
  QA2-COMPLETE (5 organic-certifier fixes, 1 prose class, 1 flaky source_url).
  ship_safety PASS on entry.
- Dataset: 43 vineyards, 98 cuvées, 12 signature-wines, 8 food-pairings,
  10 dietary, 343 entities total.

## Verdict

**OPUS-FOUND-1.**

One material defect: QA2 fixed the blanket-`icea` organic-certifier fabrication
only in `dietary.json`, leaving the SAME fabrication un-scrubbed in the two
source files that actually carry the producer org status — `vineyards.json`
(7 estates) and `hidden-gems.json` (1 estate). This is the exact regression
documented in `agents/wine-research/SCHEMA.md` ("Piedmont 2026-05-25: 'icea'
was wrongly stamped on every organic estate"). Fixed in this pass.

Everything else in the narrow-read scope is clean.

---

## DEFECT (FIXED) — residual blanket-`icea` in vineyards.json + hidden-gems.json

QA2 identified and corrected the blanket-ICEA pattern, but only on the
`dietary.json` mirrors (gd-vajra-organic, punset-organic, trediberri-organic +
vegan/lowsulfite variants). The primary producer records still carried the
fabricated certifier:

vineyards.json — 7 estates, all `organic_status: "icea"`, no `organic_certifier`
free-text, no `certified_year` (the fabrication fingerprint):
ceretto, cavallotto, fontanafredda, oddero, e-pira-chiara-boschis,
matteo-correggia, conterno-fantino.

hidden-gems.json — `trediberri` still `icea`.

These estates ARE genuinely organic-certified (verified: Fontanafredda is the
largest certified-organic estate in Piedmont since 2018; Ceretto organic-
certified from the 2015 vintage and biodynamic-practicing), but published
sources do NOT name the certifying body. Per SCHEMA.md the correct value when
the body is unnamed is the generic `"organic_certified"`, never a guessed body.

Fix applied:
- vineyards.json ×7: `icea` → `organic_certified` (body genuinely unnamed in
  sources; Ceretto's `biodynamic_practicing` left intact).
- hidden-gems.json trediberri: `icea` → `ccpb` (CCPB srl Bologna was already
  source-verified by QA2 for the same producer's dietary.json record).

Not changed (correctly retained):
- dietary.json `rivetto-biodynamic`: `organic_status: "icea"` paired with
  `biodynamic_status: "demeter_certified"`. ICEA is Demeter Associazione Italia's
  Italian inspection body, so this is internally consistent and was QA2's
  deliberate, documented call. Left as-is.

## Narrow-read checks — all clean

**Gaja crus classification.** All Gaja records read sensibly:
barbaresco-gaja / sori-tildin / sori-san-lorenzo / costa-russi =
**Barbaresco DOCG**; sperss / conteisa = **Barolo DOCG**. Correct (the three
crus returned to Barbaresco DOCG from the 2013 vintage; Sperss/Conteisa are
Barolo). Confirmed in both wines.json and signature-wines.json.

**30-entity skim (across all topics).** All real, well-known Piedmont
producers/cuvées with correct classifications (Barolo/Barbaresco/Roero DOCG,
Langhe Nebbiolo DOC, Dolcetto d'Alba DOC, Alta Langa DOCG, Cortese di Gavi DOCG).
No fabricated names, no claim/source mismatch, no implausible classification.
Spot-verified the one less-obvious pairing (Pecchenino Barolo Le Coste di
Monforte — a Dogliani house's Barolo) against producer + Decanter: real,
Barolo DOCG. 0 defects.

**editorial_score ≥ 4.7 backing scores + no fabricated ≥99.**
Max `points` anywhere = 98; ZERO entries ≥ 99 (C2 numeric gate not triggered).
Verified 5 scored tuples against live sources — all real, and if anything the
data is conservative:
- Sori San Lorenzo: data James Suckling 98 / v2021; published JS is 99
  (data UNDERSTATES — not a fabrication).
- Sperss: data Wine Advocate 98 / v2021; Monica Larner published 98+ (consistent).
- Sori Tildin (JS 97), Costa Russi (JS 97 + Jeb Dunnuck 97), Conteisa
  (Decanter 95): all real and plausible.
The many ≥4.7 cuvées with empty `scores[]` (Monfortino, Bartolo Mascarello,
Vietti single-crus, etc.) are iconic wines carrying a curatorial editorial
score only — allowed; editorial_score is not a critic point score.

**QA2 certifier fixes (dietary.json) confirmed in place:**
gd-vajra-organic = suolo_e_salute, punset-organic = ecocert, trediberri-organic
= ccpb, rivetto-biodynamic = demeter_certified (organic icea retained as above).

**Itinerary end-to-end.** `barolo-villages-two-day-weekend`: all venue slugs
(trediberri, marchesi-di-barolo, cavallotto, massolino) resolve to real
entities in the dataset. Full scan across all itineraries: 0 unresolved venues.

**Festival.** `fiera-internazionale-tartufo-bianco-alba`: start_month October,
recurrence "weekends mid October to early December" — correct for Alba's White
Truffle Fair. ship_safety festival check: 1 OK, 4 anti-bot fetch-fails
(allowed per brief; no MISS).

**Empty aroma/palate (summary-only) cuvées.** Sampled barolo-parafada,
barbaresco-cotta, barolo-arborina (of 66 summary-only): summaries are factual
(cru / commune / style or movement) with genuinely empty aroma/palate arrays —
NO fabricated sensory descriptors. Clean.

**TJ pairing ref.** Single non-null ref `italy/milan/dish/risotto-alla-milanese`
HEAD-resolves 200, H1 "Where to eat Risotto alla milanese in Milan", correctly
Milan-scoped. The Langhe-Riesling × Milanese-risotto cross-border pairing is
contextually justified.

## ship_safety

Re-run after the org-status edits: **italy/piedmont — ALL CHECKS PASSED**
(0 HARD; festival 1 OK / 4 anti-bot fetch-fail; 71/71 external URLs OK).

## Defect count

**1 defect, fixed** — residual blanket-`icea` organic certifier in the
producer-source files (vineyards.json ×7 → `organic_certified`; hidden-gems.json
trediberri → `ccpb`), the same fabrication class QA2 caught but only scrubbed in
dietary.json.

OPUS-FOUND-1 italy/piedmont
