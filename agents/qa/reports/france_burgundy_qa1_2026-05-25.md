# QA1 — france/burgundy

- Agent: QA1 (judgment pass, PROMPT.md sections A–F + L)
- Date: 2026-05-25
- Input state: wine-research complete; ship_safety mechanical gate PASSED (0 HARD, 7 layers)
- Result: **0 defects. No entities removed.**

## Scope checked

- vineyards.json — 39 producers
- signature-wines.json — 13 cuvées
- wines.json — 137 cuvées (full pass for A, C, J, K, L; sampled for I)
- 9 addressed topic files (tasting-rooms, wine-bars, wine-restaurants, wine-hotels,
  wine-museums, wine-retailers, wine-schools, nightlife, distilleries) for F

## Section A — Classification accuracy (the #1 Burgundy defect class)

Audited the Grand Cru / Premier Cru / Village / Régional label of **all 137**
wines.json cuvées + 13 signature-wines against the actual legal cru status of
the named climat. **No defects.**

Spot-confirmed the non-obvious cases that most often trip research agents:

- `chanson-corton-vergennes` "Corton-Vergennes Grand Cru" — correct; Vergennes
  is a recognised white Corton GC climat.
- `vogue-musigny-blanc` "Bourgogne Blanc Les Petits Musigny" labelled **Régional
  (Bourgogne)** — correct; de Vogüé deliberately declassifies its young-vine
  Musigny white to Bourgogne Blanc.
- `meo-vosne-cros-parantoux`, `rousseau-gevrey-clos-saint-jacques`,
  `roumier-chambolle-amoureuses` — all correctly **Premier Cru** (Cros Parantoux,
  Clos Saint-Jacques, Les Amoureuses are famously "GC-level" but legally 1er Cru).
- `vougeraie-clos-blanc-de-vougeot` correctly **Premier Cru** (the white Clos
  Blanc, distinct from the red Clos de Vougeot Grand Cru).
- `faiveley-mercurey-clos-rois` (Clos des Myglands) — **Premier Cru** confirmed
  via web (domaine + Wilson Daniels; promoted to 1er Cru in 1989).
- `bichot-chablis-long-depaquit-moutonne` (La Moutonne) — **Grand Cru** confirmed
  via web (Albert Bichot / Domaine Long-Depaquit; monopole straddling Vaudésir +
  Preuses).
- Meursault cuvées all Village or Premier Cru (no fabricated Meursault GC).

## Section B — Hectarage realism

All `hectares` figures checked against producer / known estate size. No
fabrications. The large-but-correct figures: Bouchard 130ha (largest Côte d'Or
estate holding), Drouhin 90ha, Latour 48ha, Chanson 45ha; Chablis legitimately
runs large (Fèvre 78ha, Laroche 90ha, Brocard 200ha). Two verified via web:

- Domaine Faiveley 120ha — confirmed (~120–127ha, one of Burgundy's largest
  domaine holdings; Wikipedia / BBR / Wilson Daniels).
- Jean-Marc Brocard 200ha — confirmed (~200–215ha in Chablis; wineanorak,
  Wine-Searcher).

Small Côte d'Or domaines all plausible (DRC 28, Leroy 22, Roumier 12, Comte
Armand 9, Mugneret-Gibourg 9). No 100ha+ claim attached to a small Côte d'Or
domaine.

## Section C — Score citations

93 score entries across wines.json. **Every** entry carries reviewer + points +
vintage + year. Reviewers are all legitimate Burgundy critics: Burghound,
Vinous, Decanter. No unattributable scores.

- C2 (99+ numeric verify): **no score ≥ 99 exists.** Distribution 89–98, max 98
  (a single entry), well-spread (mode 93). No fabricated 99–100pt scores — the
  known repeat defect is absent here.
- vineyards.json and signature-wines.json carry no `scores` field, so all score
  scrutiny lives in wines.json.

## Section F — Independent-directory address cross-check

13-entity random sample across 9 topics; 3 cross-checked against independent
directories (beaune-tourisme, Michelin, Tripadvisor, Petit Futé, official sites):

- Loiseau des Vignes — 31 Rue Maufoux, 21200 Beaune → exact match.
- Le Bissoh — 1A Rue du Faubourg Saint-Jacques, 21200 Beaune → match (data "1"
  vs official "1A", trivial; venue confirmed real at that street).
- Cassissium / Vedrenne — 8 Passage (des Frères) Montgolfier, 21700
  Nuits-Saint-Georges → match.

**0 fabrications.** No need to broaden.

## Section L — Cuvée → producer cross-reference

- All 137 `wines[*].producer` slugs resolve in vineyards.json. ✓
- All 13 `signature_wines[*].slug` exist in wines.json. ✓
- All `signature_wines[*].producer` resolve in vineyards.json. ✓
- No duplicate wine slugs.

## Additional checks (clean)

- **J (tag vocab):** every wines.tags entry is in WINE_TAGS.md; no derived-axis
  tags (price-/grape-/world-/ageing-/production-) leaked into researcher tags.
- **K (vintage-agnostic):** no 4-digit year in any slug or cuvée name.
- **I (taste-note sourcing):** 35 distinct aroma descriptors, distributed by
  varietal (citrus/white-flower on whites, dark/red cherry on reds) — organic,
  not template fill. No single descriptor pair repeated 30×+ verbatim.
- **H (voice):** no em/en-dashes, no AI-tells, editorial_score CV = 0.055
  (> 0.04 threshold → no score-bunching).

## Disposition

No entity met the removal bar on any section. JSONs unchanged.
ship_safety re-run below to confirm the gate still holds (it will, since nothing
was edited).
