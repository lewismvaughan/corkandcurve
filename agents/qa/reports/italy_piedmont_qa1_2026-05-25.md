# QA1 report — italy/piedmont

- Agent: QA1 (judgment pass, sections A–F + L)
- Date: 2026-05-25
- Upstream state on entry: research complete; `ship_safety.sh` PASS
  (0 HARD, all 7 layers; cuvée-taste-evidence 28/28 clean).
- Dataset: 36 vineyards, 98 cuvées (wines.json), 12 signature-wines, 8 food-pairings.

## Verdict

**QA1-COMPLETE.** 5 defects found and corrected (all one class:
vague `address_quoted` on physical venues). 0 classification defects,
0 score defects, 0 cross-reference defects.

---

## Section A — Classification accuracy (PRIMARY mandate)

Sampled 35 cuvées across vineyards + wines + signature-wines (well above the
15–20 floor). **0 defects.**

- **Gaja crus trap (verified, NOT a defect):** Sori Tildin, Sori San Lorenzo,
  and Costa Russi are labelled **Barbaresco DOCG** in wines.json + signature-wines.
  This is correct: Gaja declassified the three single-vineyard crus to Langhe
  Nebbiolo from the 1996–2012 vintages, then returned them to Barbaresco DOCG
  from the 2013 vintage. These are vintage-agnostic cuvée pages whose current
  vintages carry the DOCG, so Barbaresco DOCG is the right label. Sperss and
  Conteisa correctly carry Barolo DOCG.
- No forbidden tokens anywhere (`DOCa`, `AOC`, `AOP`, `DOC Porto`, `AVA`,
  `IGT`, `IGP` all absent from every classification field).
- DOCG/DOC boundary correctly observed across the region's dense appellation
  map: Barbera d'Asti DOCG / Nizza DOCG vs Barbera d'Alba DOC; Dogliani DOCG
  vs Dolcetto d'Alba DOC; Roero DOCG (red) vs Roero Arneis DOCG (white); Gavi
  DOCG; Moscato d'Asti DOCG; Langhe Nebbiolo DOC; Alta Langa DOCG.
- Single-vineyard cru names (Cannubi, Monfortino, Brunate, Rocche di
  Castiglione, Monprivato, etc.) appear only in cuvée names, never promoted to
  the classification field.

No broadening to 40 required (defects ≤ 2 beyond Gaja, and Gaja is clean).

## Section B — Hectarage realism

No `hectares` field exists on any vineyard record. Nothing to verify, no
fabricated figures to remove. (Estate-size claims in prose, e.g. Fontanafredda
"largest contiguous estate in the Langhe", are qualitative and uncontested.)

## Section C — Score citations

10 score tuples in wines.json; all complete with `reviewer` + `points` +
`vintage` + `year`. **0 defects.**

- No score with `points >= 99` anywhere → C2 numeric verification not triggered.
  Top scores are Sori San Lorenzo (James Suckling 98/2021) and Sperss
  (Wine Advocate 98/2021), both plausible and below the 99 verification gate.
- Publications used as `reviewer` (Wine Advocate, Wine Spectator, Vinous,
  Decanter) are acceptable per Section C (person preferred only "if known").
- Jancis Robinson 17/20 on Barbaresco Gaja correctly uses the 20-point scale.
- signature-wines embedded scores (Sori Tildin JS 97/2021; Barbaresco Gaja
  JR 17/2020) are consistent with the wines.json tuples.
- No fabricated 99–100 scores.

## Section F — Independent-directory address cross-check

Sampled physical-venue topics. **5 defects found and FIXED** — all the same
class: `address_quoted` was a bare town name rather than a verbatim street
address. (These passed ship_safety's mechanical `addr_mismatch` because the
bare town is a substring of the full entity address, but Section F treats a
bare town/appellation as a hard defect.) All five are real venues with a
correct street-level `entity.address`; the quote was tightened to match:

| file | slug | old `address_quoted` | new `address_quoted` |
|---|---|---|---|
| nightlife.json | vinoteca-centro-storico-serralunga | `Serralunga d'Alba` | `Via Cappellano 1, 12050 Serralunga d'Alba` |
| nightlife.json | all-enoteca-alba | `Canale` | `Via Roma 57, 12043 Canale` |
| nightlife.json | fracchia-e-berchialla-alba | `Alba` | `Via Vittorio Emanuele II 17, 12051 Alba` |
| wine-tours.json | tour-in-vespa-langhe | `Barolo` | `Piazza Municipio 9, 12060 Barolo CN` |
| wine-experiences.json | barolo-vespa-cru-ride | `Barolo` | `Piazza Municipio 9, 12060 Barolo CN` |

Bare town/appellation quotes on NON-venue entity types (signature-grapes =
grape origin; neighborhoods = town/appellation; itineraries, wine-festivals,
seasonal-wine, wine-history, day-trips-wine, budget-wines = conceptual /
non-address entities) are expected and were NOT flagged.

`open_status` is one of {open, seasonal, unknown, permanently_closed} on
every entity (full scan, 0 violations).

## Section L — Cuvée → producer cross-reference

- All 98 `wines[*].producer` resolve to a `vineyards[*].slug`. **0 orphans.**
- All 12 `signature_wines[*].slug` exist in `wines[*].slug`; all
  `signature_wines[*].producer` resolve in vineyards. **0 defects.**
- food-pairing `wine_entities` (all 25 refs) resolve in wines.json.

## Supplementary checks (cleared in passing)

- **Tag vocabulary (J):** every `wines[*].tags` entry is in WINE_TAGS.md;
  no derived-axis tags (price-*, grape, world, etc.) emitted. 0 defects.
- **Vintage-agnostic slugs (K):** no `wines[*].slug` contains a 4-digit year.
- **Cross-link sanity (G):** food-pairing has one non-null
  `tablejourney_ref` → `italy/milan/dish/risotto-alla-milanese`, on the
  explicitly cross-border Langhe Riesling + Milanese-risotto pairing. The
  Milan target is contextually justified (not a city mismatch); ship_safety
  already HEAD-checked it.
- **Voice (H):** no em-dashes / en-dashes in any data file. editorial_score
  CV = 0.0491 (> 0.04 threshold; no score-bunching).

## Defect count

**5 defects, all corrected** (vague address_quoted → verbatim street address;
nightlife ×3, wine-tours ×1, wine-experiences ×1).

ship_safety re-run after edits: see end of run.
