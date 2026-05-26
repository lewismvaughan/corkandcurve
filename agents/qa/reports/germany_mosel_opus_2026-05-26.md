# Opus final QA report — germany/mosel

- Date: 2026-05-26
- Agent: Opus final QA (narrow read, post QA1 + QA2)
- Region: Mosel (Germany)
- Inputs: post-QA1 (6 vague-address fixes; German classification clean) and
  post-QA2 (von Kesselstatt + Vollenweider ownership currency, 1 broken
  vineyard_ref) JSON. ship_safety PASSED prior. Did NOT re-HEAD URLs or redo
  QA1/QA2 mechanical layers.

## Result: OPUS-FOUND-1

One material style/sweetness defect found and fixed. Everything else clean.

## DEFECT (fixed) — peter-lauer-fass-18-kupp-gg sweetness mislabel

- File: wines.json
- Was: `"sweetness": "off-dry"`.
- Defect: This cuvée is a VDP Grosses Gewachs. A GG is legally trocken/dry
  (VDP statute). It was the ONLY one of 31 GG cuvées in the dataset marked
  anything other than `dry` — the other 30 are all `dry`. The entity's own
  copy contradicted the field three times: `taste.summary` and
  `history.summary` both say "the barrel-fermented **dry** Grosses Gewachs...
  the estate's flagship **dry** wine," and `description` says "the
  barrel-fermented **dry** Grosses Gewachs."
- Verified: producer page (lauer-ayl.de Fass 18 Kupp GG) + multiple merchant
  listings describe a "very long, dry finish" and "premium German dry wine
  classification."
- Fix: `sweetness` "off-dry" -> "dry". (No tag change needed: sweetness tags
  are derived by the generator from this field; no `off-dry`/`dry` tag was
  emitted by the researcher.)
- ship_safety re-run after the edit: ALL CHECKS PASSED, 0 HARD.

## Checks that came back clean

### 30-entity random spot-check (across all topics) — CLEAN
Sampled 30 named entities spanning wines, vineyards, restaurants, nightlife,
tasting-rooms, hotels, dietary, signature-wines, festivals, day-trips,
seasonal, signature-grapes. Every entity is a real, recognizable Mosel/Saar
estate/venue (Karthauserhof, Kerpen, Max Ferd. Richter, Monchhof, A.J. Adam,
Knebel, Stein, Waldhotel Sonnora, Zum Domstein, von Nell, etc.) with a
coherent producer-domain source URL. No fabricated names, no
claim/source-domain mismatch.

### Classification (German system) — CLEAN
Only three values across the whole dataset: `VDP.Grosse Lage Mosel`,
`Mosel Pradikatswein`, `Mosel QbA`. Zero DOCG/DOCa/DOC/IGT/IGP/AOC/AOP/AVA/WO
anywhere (recursive scan). No Pradikat ladder term or GG/Grosses Gewachs
leaked into a `classification` field (they live in cuvée NAME, correct).

### Ownership currency — QA2 fixes held + 4 spot-checks current
- von Kesselstatt = "Reh family (managing director Dr. Karsten Weyand)" in
  vineyards.json; no stale Annegret Reh-Gartner reference survives in any file.
- Vollenweider = "Moritz Hoffmann (estate founded by Daniel Vollenweider)",
  winemaker "Moritz Hoffmann", consistent across vineyards.json +
  hidden-gems.json; description reconciled to founder-vs-current phrasing.
- Spot-checked Dr. Loosen (Ernst Loosen), Fritz Haag (Oliver Haag), Maximin
  Grunhaus (Maximin von Schubert), Schloss Lieser (Thomas Haag) — all current.

### Certification — CLEAN, consistent
- Clemens Busch = `biodynamic_practicing` + `organic_certified`, certifier
  `respekt-BIODYN` (NOT Demeter), consistent across vineyards.json,
  dietary.json, hidden-gems.json.
- Melsheimer = `demeter_certified` + Demeter certifier (2013), consistent.
- Weiser-Kunstler / Trossen / Weingut Stein: no practising->certified
  promotion; bodies named correctly. dietary.json `weiser-kunstler-organic`
  vineyard_ref correctly = `weiser-kuenstler` (QA2 fix held).

### Scores / editorial — CLEAN
Max published score = 97 (Egon Muller Scharzhofberger Auslese, Wine Advocate,
2018). ZERO scores >= 98 (so no fabricated 98+; no C2 numeric tuple step
triggered). Spot-checked the editorial_score >= 4.7 cuvées: backing scores are
real and proportionate (Egon Muller Spatlese 95 / Auslese 97; J.J. Prum
Spatlese 94 / Auslese 95; Markus Molitor Gold Capsule 96; Maximin Grunhaus
Abtsberg GG 94; Heymann-Lowenstein Uhlen 94; all Wine Advocate or Vinous).
Note (non-material): 4 iconic cuvees carry editorial_score >= 4.7 with an
empty `scores` array (Egon Muller Kabinett 4.9 + TBA 5.0, J.J. Prum Kabinett
4.8, Willi Schaefer Kabinett 4.7). These are editorial-confidence ratings on
benchmark wines, not fabricated numeric critic scores — left as-is.

### Style / sweetness — 1 defect (above), rest CLEAN
- After the Peter Lauer fix, all 31 GG cuvees = dry + still-white.
- Eiswein (Mulheimer Helenenkloster) = dessert + dessert-ice-wine.
- TBA (Egon Muller) = dessert + dessert-noble-rot.
- Auslese fruity-style = sweet/dessert; Kabinett/Spatlese fruity = medium-sweet.
- 3 Sekt cuvees = sparkling-traditional (the "bA" suffix is Sekt b.A., not
  Beerenauslese).

### Itinerary end-to-end — CLEAN
All 3 itineraries' venue slugs (14 references) resolve to indexed entities
in vineyards.json / hidden-gems.json. (J.J. Prum is keyed `joh-jos-pruem` as
the producer/vineyard slug; cuvee slug prefix `jj-pruem-*` is cosmetic — all
143 cuvee `producer` values resolve to a vineyard slug.)

### Festival end-to-end — CLEAN
Mythos Mosel: `start_month` "June" matches its source ("from 10 to 12 June");
recurrence "weekend after Whitsun, late May or June" consistent. All 6
festivals' start_month aligns with recurrence_pattern. ship_safety festival
check: 5/6 OK, 1 UNKNOWN (Zeller Schwarze Katz — source page not date-specific;
anti-bot/non-specific UNKNOWN is allowed).

### Other
- 0 em/en dashes (recursive scan). All 26 JSON files parse.
- Tag vocabulary + vintage-agnostic discipline confirmed clean by QA2; no
  regression introduced.

## ship_safety
Re-run after the single edit: `germany/mosel: ALL CHECKS PASSED` (0 HARD;
1 WARN = QA2-acknowledged Selbach-Oster/Maximin Grunhaus site-level taste
note; 1 festival UNKNOWN allowed).

OPUS-FOUND-1 germany/mosel
