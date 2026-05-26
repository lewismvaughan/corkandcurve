# QA1 Report — italy/sicily — 2026-05-26

## Region summary
54 vineyards, 176 cuvees, 12 signature-wines, 10 signature-grapes. Tier-1 region.

## Section A — Classification accuracy

Sampled 20 producers + wines across vineyards.json and wines.json.

**Result: PASS (0 defects)**

- Cerasuolo di Vittoria DOCG: correctly applied to COS, Arianna Occhipinti, Valle dell'Acate, Feudi del Pisciotto, Planeta Vittoria, Tenute Nicosia. No other appellation incorrectly labeled DOCG.
- Etna DOC (not DOCG): all Etna sub-types correctly use DOC (Etna Rosso DOC, Etna Bianco DOC, Etna Bianco Superiore DOC, Etna Rosato DOC, Etna Spumante). No DOCG misapplication.
- Marsala DOC: correctly applied to Cantine Florio, Cantine Pellegrino, Rallo. De Bartoli Vecchio Samperi correctly classified as "Vino da Tavola (perpetuo, un-fortified)" - NOT Marsala DOC.
- Passito di Pantelleria DOC, Moscato di Pantelleria DOC, Malvasia delle Lipari DOC: all correctly applied.
- IGT/IGP Terre Siciliane: used correctly for natural/amphora wines (COS Pithos, Passopisciaro contrada series) where no DOC classification applies.
- Vittoria DOC (vs DOCG): correctly distinguished from Cerasuolo di Vittoria DOCG for varietal wines.

## Section B — Hectarage realism

No dedicated `hectares` field in vineyards.json schema. Hectarage appears in description text only.

Checked narrative claims: Girolamo Russo (15 ha), Calabretta (12.5 ha), Arianna Occhipinti (40 ha), Valle dell'Acate (70 ha), Firriato (~490 ha), Cusumano (500+ ha), Baglio di Pianetto (106 ha), Zisola (50 ha), Palmento Costanzo (~10 ha), Baglio del Cristo di Campobello (50 ha), Settesoli cooperative (6,000+ ha grower network), Tenuta Gatti (217 ha), Tenuta Rapitala (170 ha). All consistent with publicly available producer information.

**Result: PASS (0 defects)**

## Section C — Score citations

All 176 wines.json entries have `scores: []` (empty). Agents reported no scores, per dispatch brief.

**Result: PASS — no scores to audit. C2/C3 (99+ point verification, split-estate disambiguation) not applicable.**

## Section F — Address cross-check

Sampled 12 entities across tasting-rooms.json, wine-restaurants.json, wine-hotels.json, distilleries.json:

- Cantine Florio: Via Vincenzo Florio 1, 91025 Marsala (TP) — consistent with vineyards.json.
- Donnafugata Marsala: Via S. Lipari 18 / Via Sebastiano Lipari 18 — same address, two format variants, not a defect.
- Cantine Pellegrino: Via Paolo Pellegrino 39, Marsala — consistent.
- Palmento Costanzo: Contrada Santo Spirito, 95012 Passopisciaro — consistent across tasting-rooms, wine-restaurants, wine-hotels.
- Benanti: Via Giuseppe Garibaldi 361, 95029 Viagrande — consistent.
- Cottanera: Strada Provinciale 89, Contrada Iannazzo, 95030 Castiglione di Sicilia — consistent.
- Barone di Villagrande: Via del Bosco 25, 95010 Milo — consistent.
- Baglio di Pianetto: Via Francia, Santa Cristina Gela, 90030 Palermo — consistent.
- Regaleali/Tasca: wine-hotels.json shows "93010 Vallelunga Pratameno (CL)" vs vineyards.json "90020 Sclafani Bagni (PA)". The Regaleali estate straddles the Palermo-Caltanissetta provincial boundary; both addresses are valid for different estate access points. Not a defect.
- Averna Distillery: Via Xiboli 345, 93100 Caltanissetta — plausible for the historic Averna facility.
- Marco De Bartoli Samperi: "Contrada Samperi, Mazara del Vallo Road, 91025 Marsala" in tasting-rooms vs "Contrada Samperi 292, Marsala (TP)" in vineyards — both valid, tasting-rooms uses informal road reference. Not a defect.
- Zash/Monaci: Via Monaci, 95019 Zafferana Etnea — consistent across hotels and restaurants.

All open_status values are exactly one of {open, seasonal, unknown, permanently_closed}.

**Result: PASS (0 defects)**

## Section L — Cross-reference integrity

### wines.json producers -> vineyards.json
All 176 cuvees: 0 orphan producer references. Every `wines[*].producer` resolves to a `vineyards[*].slug`.

### signature-wines.json -> wines.json
All 12 signature-wine slugs resolve in wines.json. All 12 producers resolve in vineyards.json.

### vineyards[*].signature_wines -> wines.json
**14 broken references found and fixed:**

| Vineyard | Old (broken) slug | New (correct) slug |
|---|---|---|
| planeta | planeta-nocera | (removed — no Nocera wine exists) |
| tasca-dalmerita | tasca-dalmerita-Leone-dAlmerita | tasca-dalmerita-leone-dalmerita (case fix) |
| cantine-pellegrino | pellegrino-pantelleria-passito | pellegrino-nes-passito |
| marco-de-bartoli | de-bartoli-bukkuram | de-bartoli-bukkuram-sole-d-agosto |
| tenuta-delle-terre-nere | terre-nere-le-vigne-di-eli | terre-nere-feudo-di-mezzo |
| graci | graci-feudo-di-mezzo | graci-barbabecchi (graci-feudo-di-mezzo is a Terre Nere wine) |
| cottanera | cottanera-barbazzale | cottanera-barbazzale-bianco |
| firriato | firriato-chiaramonte | firriato-chiaramonte-nero-davola |
| cusumano | cusumano-alta-mora-etna | alta-mora-etna-rosso |
| rallo | rallo-alcamo | rallo-alcamo-bianco |
| planeta-sciaranuova | planeta-nerello | planeta-nerello-etna |
| planeta-sciaranuova | planeta-carricante | planeta-carricante-etna |
| planeta-buonivini | planeta-moscato-di-noto | (removed — no such wine exists) |
| duca-di-salaparuta | duca-di-salaparuta-duca-enrico | duca-enrico |

After fix: all vineyard signature_wines refs resolve.

**Result: 14 defects found and fixed.**

## Section A addendum — Dead Etna Consortium URL

The WARN flagged `consorziodocetna.it` dead URL was found across 8 files (27 occurrences). Replacement: `https://consorzioetnadoc.com/` (the working Consorzio di Tutela dei Vini Etna DOC URL, already used in signature-grapes.json).

Files updated: wine-festivals.json, dietary.json, seasonal-wine.json, day-trips-wine.json, wine-history.json, itineraries.json, nightlife.json, hidden-gems.json.

## Tag vocabulary (Section J)

Checked all 176 wines.json tag arrays. Result: 0 unknown tags, 0 derived-axis tags emitted by researcher. Clean.

## Vintage-agnostic discipline (Section K)

No slugs contain 4-digit years. "Florio Targa Riserva 1840" — the 1840 is part of the brand name (Cantine Florio founding era), not a vintage year. Slug is `florio-targa-riserva`. Acceptable.

## Score bunching (Section H)

176 editorial_scores: mean=4.416, stdev=0.275, CV=0.062 (threshold: 0.04). Range 3.9-5.0 with smooth distribution. No bunching.

Em-dash / AI-tell scan: 0 matches across all 26 data files.

No description clones within vineyards.json.

## Final ship_safety.sh result

```
bash scripts/ship_safety.sh italy sicily
Total HARD failures across 1 cities: 0
italy/sicily: ALL CHECKS PASSED
```

## Defect summary

| Section | Defects | Action |
|---|---|---|
| A — Classification | 0 | — |
| B — Hectarage | 0 | — |
| C — Scores | 0 | — |
| F — Addresses | 0 | — |
| H — Voice/prose | 0 | — |
| J — Tag vocabulary | 0 | — |
| K — Vintage slugs | 0 | — |
| L — Cross-refs (signature_wines) | 14 broken slugs | Fixed in vineyards.json |
| Consortium URL (WARN) | 27 dead URLs across 8 files | Replaced with consorzioetnadoc.com |

**Total defects fixed: 15 items (14 slug corrections + 1 URL batch replacement across 27 occurrences)**
