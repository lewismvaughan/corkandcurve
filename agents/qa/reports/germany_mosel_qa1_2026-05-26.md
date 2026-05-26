# QA1 report — germany/mosel

- Date: 2026-05-26
- Agent: QA1 (judgment pass, sections A-F + L)
- Region: Mosel (Germany)
- Entities: 42 vineyards, 143 cuvées, 12 signature wines, plus 24 topic files.
- Inputs: ship_safety PASSED prior (0 HARD, all 7 layers, cuvée-taste-evidence clean).
  Per PROMPT.md, did NOT re-HEAD URLs, re-fuzzy-match addresses, or re-validate JSON shape.

## Section A — Classification accuracy (German system) — PASS

Sampled all 42 vineyards + 12 signature wines + the full set of distinct
`classification` values in wines.json (143 cuvées).

- Only three classification values appear across the whole region:
  `VDP.Grosse Lage Mosel`, `Mosel Pradikatswein`, `Mosel QbA`. All are
  valid German legal/VDP classifications.
- ZERO leakage of `DOCG / DOCa / DOC / IGT / IGP / AOC / AOP / AVA / WO`
  into any `classification` field anywhere in the dataset (recursive scan).
- Pradikat ladder terms (Kabinett / Spatlese / Auslese / BA / TBA /
  Eiswein) and `GG` / `Grosses Gewachs` correctly live in cuvée NAME /
  style / prose, NOT in `classification`.
- Vineyard names (Wehlener Sonnenuhr, Scharzhofberger, Bernkasteler
  Doctor, Erdener Pralat, Brauneberger Juffer) correctly appear only as
  cuvée names, never as classifications.

Defects: 0.

## Section B — Hectarage realism — PASS

No structured `hectares` numeric field is claimed on any vineyard.
The only hectarage references are in hidden-gems.json prose, all small
(Vollenweider ~6 ha, Weiser-Künstler "a few hectares", a "barely a
hectare" startup figure) — realistic for boutique steep-slope Mosel
estates. No fabricated estate-scale figures.

Defects: 0.

## Section C — Score citations — PASS

- 35 score tuples across wines.json; every one has reviewer + points +
  vintage + year (0 missing fields).
- Reviewers all legitimate for the German vertical: Wine Advocate,
  Vinous, Mosel Fine Wines (the regional specialist), Falstaff.
- Max score = 97 (Egon Müller Scharzhofberger Auslese, Wine Advocate,
  2018 vintage, reviewed 2020) — matches research's stated ceiling.
- ZERO scores >= 99, so no C2 numeric tuple verification required.
- Top band (95-97): Egon Müller Spätlese 95 / Auslese 97, J.J. Prüm
  Wehlener Sonnenuhr Auslese 95, Fritz Haag Juffer-Sonnenuhr Auslese 95,
  Markus Molitor Wehlener Sonnenuhr Gold Capsule 96 — all Wine Advocate
  (Reinhardt), all plausible for top Mosel Auslese. No fabrication signal.

Defects: 0.

## Section F — Independent-directory address cross-check — 6 DEFECTS FIXED

Checked open_status enum (all `open`/`seasonal`/`unknown` — valid) and
scanned for vague (non-street-level) `address_quoted` on physical-venue
topics.

The bare-town `address_quoted` values flagged across abstract entities
(neighborhoods, wine-history eras, seasonal phenomena, festivals,
day-trips, budget cuvées) are appropriate granularity for those
non-venue entity classes and were left as-is (ship_safety passed them).

DEFECT (vague address on real fixed venues) — all in nightlife.json,
each had a full street address in `entity.address` but a bare-town
`address_quoted`. Tightened each quote to street level:

1. `wirtshaus-zur-glocke-trier`        Trier → Glockenstrasse 12, 54290 Trier
2. `mosel-vinothek-bernkastel`         Bernkastel-Kues → Cusanusstrasse 2, 54470 Bernkastel-Kues
3. `strausswirtschaften-bernkastel`    Bernkastel-Kues → Gestade 18, 54470 Bernkastel-Kues
4. `bonsai-und-wein-vinothek-der-saar` Saarburg → Kunohof 20, 54439 Saarburg
5. `weingut-bindges-vinothek-rosenhof` Traben-Trarbach → Rosengasse 1, 56841 Traben-Trarbach
6. `sekthaus-lieser`                   Lieser → Moselstrasse 30, 54470 Lieser

Defects: 6 (all corrected in-place).

## Section L — Cuvée → producer + signature → cuvée cross-reference — PASS

- All 143 `wines[*].producer` values resolve to a `vineyards[*].slug`.
- All 12 `signature_wines[*].slug` exist in `wines[*].slug`.
- All 12 `signature_wines[*].producer` resolve to a vineyard slug.
- No cuvée slug or name contains a 4-digit vintage year (vintage-agnostic
  discipline intact).

Defects: 0.

## Style / sweetness sanity — PASS

- All `GG` / `Grosses Gewachs` cuvées are `dry` + `still-white`.
- `Eiswein` (Mülheimer Helenenkloster) = `dessert` + `dessert-ice-wine`.
- `Trockenbeerenauslese` = `dessert` + `dessert-noble-rot`.
- Spätlese / Auslese fruity-style cuvées all `off-dry`/`sweet`/`dessert`.
- All Sekt cuvées = `sparkling-traditional` (the "bA" suffix is the Sekt
  b.A. designation, not Beerenauslese — verified, no mislabel).
- Tag vocabulary: every tag in wines.json appears in WINE_TAGS.md; no
  derived-axis tags (price/sweetness/grape/world/etc.) emitted by the
  researcher.

Defects: 0.

## Summary

Total defects: 6 (all Section F vague-address, all corrected in-place).
No structural regressions. No classification, score, hectarage, or
cross-reference defects — a clean German-system dataset. Re-ran
ship_safety after fixes to confirm 0 HARD.
