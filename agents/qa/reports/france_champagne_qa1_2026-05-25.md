# QA1 — france/champagne — 2026-05-25

Agent: QA1 (judgment pass, PROMPT.md sections A–F + L).
Entry state: research finished, ship_safety PASSED (0 HARD, all 7 layers,
cuvée-taste-evidence clean). Did NOT re-HEAD URLs, re-fuzzy address, or
re-validate JSON shape (ship_safety owns those).

Scope counts: 39 vineyards, 93 cuvées (wines.json), 12 signature wines,
8 hidden gems, 9 dietary entities, 4 distilleries, neighborhoods + nightlife.

## Result: QA1-COMPLETE — 38 defects corrected, 0 remaining HARD

ship_safety re-run after corrections: **PASS, 0 HARD** (fetch-fail 30 =
anti-bot, non-defect; cuvee-taste-miss 0).

---

## Section A — Classification accuracy

Every wine/cuvée/producer is **AOC Champagne** (France's AOC). Verified:

- No cuvée or vineyard carries DOCG / DOCa / DOC Porto / IGT / IGP / AVA
  anywhere in the dataset (word-boundary grep across all 27 files: zero hits).
- wines.json: all 93 cuvées classification == "AOC Champagne". budget-wines:
  all "Champagne AOC". Clean.
- Still wines of the zone are referenced correctly in PROSE ONLY and labelled
  right: region.json FAQ explicitly states "Still wines are AOC Coteaux
  Champenois and the pink still wine is AOC Rose des Riceys"; Bouzy Rouge
  described as "still red Coteaux Champenois"; Rose des Riceys AOC in
  day-trips. None mislabelled as AOC Champagne. Clean.
- Distilleries carry spirit GIs (Ratafia Champenois IG, Marc de Champagne IG,
  Fine de Champagne) — correct for Champagne-region spirits, NOT misplaced
  wine IGT/IGP. Clean.

**DEFECT (4) — Grand Cru / Premier Cru in the `classification` field.**
hidden-gems.json carried the Échelle-des-Crus village tier inside
`classification`, which per Section A is a village-sourcing attribute that
belongs in cuvée name / prose, not the AOC field. Corrected to "Champagne AOC":
- `pierre-paillard`        "Champagne AOC Grand Cru"   -> "Champagne AOC"
- `bereche-et-fils`        "Champagne AOC Premier Cru" -> "Champagne AOC"
- `champagne-marguet`      "Champagne AOC Grand Cru"   -> "Champagne AOC"
- `david-leclapart`        "Champagne AOC Premier Cru" -> "Champagne AOC"
(Grand Cru / Premier Cru fact preserved in `neighborhood` + `what_locals_love`
prose for each — no information lost.)

## Section B — Hectarage realism

No structured `hectares` / `planted_hectares` / `vineyard_area` field exists
anywhere. Hectarage appears in prose only (Fleury ~15 ha, Leclerc Briant
~13 ha, Vouette et Sorbée ~5 ha, Georges Laval ~2.5 ha, Leclapart ~3 ha) —
all realistic for these growers and matching published figures. Nothing to
null. Clean.

## Section C — Score citations

93 structured `scores[*]` entries in wines.json. Every entry has reviewer +
points + vintage + year (0 missing fields). Reviewers all legitimate Champagne
critics/publications: Vinous 52, Decanter 23, Wine Spectator 17, Wine Advocate 1.
Points range 88–97, mean 92.4, well-distributed (no bunching). Top scores:
Cristal 97, Krug Clos du Mesnil 97, Comtes/Salon/Winston Churchill 96 — matches
research's stated 96–97 cap. **No score >= 98, none >= 99** so C2 numeric
source-verification not triggered. No fabricated 99–100 found. Clean.

## Section F — Independent-directory address cross-check

Sampled the marquee houses + growers (Krug 5 rue Coquebert, Moët 20 av de
Champagne, Ruinart 4 rue des Crayères, Salon Le Mesnil, Selosse 59 rue de
Cramant, Egly-Ouriet Ambonnay, Pierre Péters Le Mesnil, etc.) — all real,
canonical, correctly addressed. No fabricated venues; open_status values all in
{open, seasonal, unknown, permanently_closed}.

**DEFECT (34) — vague `address_quoted` (bare town/region).** This is the
recurring vague-quote class. ship_safety's verify_entities passed these because
a bare town ("Reims", "Bouzy") is a substring of the full address, so the
substring layer of `_address_matches` returns True — exactly the case the
PROMPT routes to QA1. Tightened each to the verbatim street-level line of
`entity.address`:
- dietary.json (9): champagne-fleury-biodynamic, leclerc-briant-biodynamic,
  vouette-et-sorbee-biodynamic, marie-courtin-biodynamic, larmandier-bernier-organic,
  georges-laval-organic, david-leclapart-natural, champagne-fleury-lowsulfite,
  marguet-lowsulfite.
- hidden-gems.json (8): roses-de-jeanne-cedric-bouchard, vouette-et-sorbee,
  pierre-paillard, bereche-et-fils, champagne-marguet, chartogne-taillet,
  david-leclapart, marie-courtin.
- nightlife.json (17): le-wine-bar-by-le-vintage, la-vinocave-reims,
  le-bistrot-du-forum-reims, the-glue-pot-reims, latino-cafe-reims,
  les-berceaux-epernay, lapostrophe-reims, sacre-bistro-epernay,
  c-comme-champagne-epernay, le-25bis-by-leclerc-briant-epernay,
  le-cellier-perrier-jouet-epernay, la-cave-de-lavenue-epernay,
  tresors-de-champagne-sparkling-reims, le-wine-bar-sparkling-reims,
  le-25bis-sparkling-epernay, la-vinocave-sparkling-reims,
  le-bocal-oyster-champagne-reims.

NOT changed (correct as-is):
- neighborhoods.json sub-region entities (Reims, Epernay, Montagne de Reims,
  Côte des Blancs, etc.) — these are region-level entities by design, not
  street venues; a region/town name is the appropriate quote.
- vineyards.json `champagne-drappier` "Rue des Vignes" — verbatim; Drappier's
  address genuinely has no street number.

## Section L — Cuvée -> producer cross-reference

- All 93 `wines[*].producer` resolve to a `vineyards[*].slug`. Clean.
- All 12 `signature_wines[*].slug` exist in `wines[*].slug`; all
  signature-wines producers resolve in vineyards. Clean.
- No `wines[*].slug` contains a 4-digit year (vintage-agnostic discipline OK).

## Observations passed to QA2 (non-blocking, outside QA1 A–F+L)

- vineyards.json `signature_wines` arrays reference 11 cuvée slugs not present
  in wines.json (e.g. `dom-ruinart`, `mumm-rsrv`, `vilmart-coeur-de-cuvee`,
  `gosset-celebris`). The canonical signature-wines.json file is fully
  consistent (Section L passes), but the per-vineyard `signature_wines` hint
  arrays are stale relative to wines.json slugs. If a generator renders those
  arrays as links they would 404. Worth QA2 / Opus confirming the generator
  does not consume vineyards[*].signature_wines for links.
- hidden-gems.json `chartogne-taillet.open_evidence_url` points at a
  Bérêche gaultmillau page (cross-entity), and `open_evidence_url` for
  `chartogne-taillet` likewise. URL HEAD-resolves so ship_safety passed it;
  flagging as a wrong-entity evidence link for QA2 to re-anchor.

QA1-COMPLETE france/champagne — defects: 38 (4 classification + 34 vague-address), all corrected.
