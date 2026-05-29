# QA2 Report — spain/priorat — 2026-05-29

**Agent:** QA2 (judgment pass)
**Sections covered:** D, E, G, H, I, J, K
**Input state:** Post-QA1 — 50 producers, 135 cuvées, 0 HARD ship_safety
**ship_safety after QA2 edits:** ALL CHECKS PASSED — 0 HARD

---

## Section D — Ownership currency + fabrication/cross-contamination (venue + editorial files)

### Defect 1 — Sara Pérez surname misspelled as "Perea" (tasting-rooms.json, two instances) [HIGH]

`tasting-rooms.json` slug `mas-martinet-tasting-falset`: description read "Sara Perea's family estate" — surname fabricated/garbled.

`tasting-rooms.json` slug `venus-la-universal-tasting-falset`: description read "Sara Perea and Dani Tarda's Falset project" — two errors: surname "Perea" (should be "Pérez") and co-founder "Dani Tarda" is not cited in any source. Vineyards.json, wines.json, and the QA brief all confirm Venus la Universal was co-founded by Sara Pérez (Mas Martinet) and René Barbier Jr (Clos Mogador).

**Action:** Both descriptions corrected:
- `mas-martinet-tasting-falset`: "Sara Perea's" → "Sara Perez's"
- `venus-la-universal-tasting-falset`: "Sara Perea and Dani Tarda's" → "Sara Perez and Rene Barbier Jr's"

### Defect 2 — L'Infernal owner "Belondrade family" unverifiable acquisition claim [MEDIUM]

`vineyards.json` slug `linfernal`: `owner: "Belondrade family"` with description "Acquired by the Belondrade family in 2023." The Belondrade family is a known Spanish winemaking family from Rueda — a different region, different producer. No cited source supports an acquisition of L'Infernal. The open_evidence_url still points to `doqpriorat.org/en/wineries/combier-fischer-gerin-sl/` (the original founders' page slug), contradicting the ownership claim.

**Action:** Nulled `owner` and rewrote description to factual founding statement without the unverifiable acquisition claim. Description now: "Established in 2002 by Rhone winemakers on 18 hectares in Torroja del Priorat, producing Garnacha and Cariñena blends from llicorella terraces."

---

## Section E — Certification status consistency

### Defect 3 — Clos Erasmus biodynamic/organic status discrepancy across files [MEDIUM]

`vineyards.json` slug `clos-erasmus`: `biodynamic_status: "none"`, `organic_status: "none"`
`dietary.json` slug `clos-erasmus-biodynamic`: `biodynamic_status: "biodynamic_practicing"`, `organic_status: "organic_certified"` with source URLs at europeancellars.com and terroirtalking.com confirming the organic + biodynamic-practicing status since 2004.

The dietary.json entry has better evidenced sourcing and matches the QA brief ("Clos Erasmus organic + biodynamic-practicing 2004"). The vineyards.json entry was left at "none/none" — same pattern as the Clos Mogador discrepancy fixed in QA1 (Defect 6).

**Action:** Updated `vineyards.json` clos-erasmus to `biodynamic_status: "biodynamic_practicing"`, `organic_status: "organic_certified"`.

### Defect 4 — Mas Martinet biodynamic status discrepancy [MEDIUM]

`vineyards.json` slug `mas-martinet`: `biodynamic_status: "none"` while `dietary.json` slug `mas-martinet-organic` shows `biodynamic_status: "biodynamic_practicing"` with CCPAE organic certification, sourced from masmartinet.com and winepredator.com. QA brief confirms "Mas Martinet CCPAE organic + biodynamic-practicing."

**Action:** Updated `vineyards.json` mas-martinet to `biodynamic_status: "biodynamic_practicing"`.

---

## Section G — Cross-link sanity

`food-pairing.json`: All 9 TJ tablejourney_url values are under spain/barcelona. Confirmed: Cal Pep, 7 Portes, El Xampanyet, Quimet i Quimet, Bar Brutal, Monvinic are all barcelona-scoped paths. PASS.

`wines.json`: Zero `wines[*].pairings[*].tablejourney_ref` entries found across all 135 cuvées. PASS.

---

## Section H — Voice + prose

- Em-dash / en-dash scan across all data files: 0 hits. PASS.
- AI-tell scan (nestled, vibrant, culinary journey, carefully crafted, must-visit): 0 hits. PASS.
- Score-bunching check: editorial_score CV = 0.0727 (above 0.04 suspicious threshold). PASS.
- Description clone check: 1989 revival / Cinc Pioners founding story across five cuvées — all use distinct phrasings. No exact clones. PASS.

### Defect 5 — Soft superlative in wines.json milestone [LOW]

`ferrer-bobet-selecci-especial` history milestone: "First vintage of Ferrer Bobet Selecció Especial from the finest old-vine parcels" — "finest" is an unverifiable superlative.

**Action:** Rewritten to "First vintage of Ferrer Bobet Selecció Especial from selected old-vine parcels in Porrera."

---

## Section I — Cuvée taste-note sourcing (Gap 1 audit)

**Gap 1 found and resolved: 124 cuvées sharing unsourceable directory/homepage URLs**

Audit methodology: counted distinct `cuisine_evidence_url` values vs cuvée count. Found:
- 38 cuvées: `cuisine_evidence_url = https://www.doqpriorat.org/en/wineries/` (DOQ wineries listing — a directory, not per-cuvée). All 38 had populated taste blocks (aroma, palate) that cannot be verified against this listing page.
- 57 cuvées: `source_url = https://www.doqpriorat.org/en/` (DOQ homepage), `cuisine_evidence_url = null`. These 57 had taste blocks with no per-cuvée citation.
- 29 cuvées: `source_url = https://www.wine-searcher.com/find/[producer]/1/spain/...` (wine-searcher retailer-price search pages). These are aggregator/price pages that carry no per-cuvée tasting notes.

Total: **124 unsourceable cuvées** across 46 producers. Only **11 cuvées** had per-wine source URLs (Val Llach, Mas Doix, Mas d'en Gil, Buil & Giné, Vinícola del Priorat).

The Álvaro Palacios 6-cuvée group specifically: source_url=doqpriorat.org/en/ (homepage), cuisine_evidence_url=null. Adjudication: taste blocks stripped (same as the broader 57 group).

**Action taken:**
- Stripped `taste.aroma`, `taste.palate`, and `taste.summary` for all 124 unsourceable cuvées.
- Reassigned `source_url` to the producer's confirmed website (where available) or the DOQ wineries directory. Specific substitutions made:
  - Álvaro Palacios → alvaropalacios.com/
  - Clos Mogador → closmogador.com
  - Mas Martinet → masmartinet.com/
  - Clos Erasmus → prioratwines.nl/en/wineries/clos-i-terrasses
  - Terroir Al Limit → terroir-al-limit.com/
  - Cellers Scala Dei → cellersdescaladei.com/en
  - [36 more producers — see producer_sites mapping in edit script]
  - Smaller producers without confirmed live websites: DOQ wineries directory maintained or upgraded to per-producer DOQ subpage where available (e.g., Saó del Coster → doqpriorat.org/en/wineries/sao-del-coster/)
- One additional fix: `cellerelmasroig.com/` returned URLError (unreachable domain) for 3 cuvées; replaced with confirmed wine-searcher retailer page.

**11 cuvées retained taste blocks** (per-wine evidence URLs confirmed):
- Val Llach: mas-de-la-rosa, idus-de-vall-llach, embruix-de-vall-llach (vallllach.com/en/wines/[wine])
- Mas Doix: salanques-mas-doix (masdoix.com/en/wine/salanques)
- Mas d'en Gil: coma-vella, clos-fonta, bellmunt-mas-den-gil (masdengil.com/en/wines/[wine])
- Buil & Giné: gine-gine, pleret, joan-gine (builgine.com/en/wines/[wine])
- Vinícola del Priorat: onix-fusio (vinicoladelpriorat.com/en/wines/onix-fusio)

Note: ship_safety `check_evidence_content.py` reports 3 WARN (non-blocking) for the 3 Vall Llach cuvées — the page fetches 200 but the English descriptor terms don't appear verbatim in the Catalan/Spanish-language wine page text. This is a language-matching limitation of the checker, not a data defect. The per-wine evidence URLs are correct.

---

## Section J — Tag vocabulary conformance

Full sweep of all 135 `wines[*].tags` entries:
- Unknown tags (not in WINE_TAGS.md): 0
- Derived-axis tags in researcher output: 0
- arrels-vi-ranci: correctly tagged `fortified-vdn`. PASS.
- All reds: `still-red`. All whites: `still-white`. PASS.

---

## Section K — Vintage-agnostic discipline

- Slugs with 4-digit year: 0
- Names with vintage year: 0
- References to old slug `1902-carinena-centenaria` or `doix-1902`: 0 found anywhere in data directory.

---

## Defect count summary

| Class | Count |
|---|---|
| Sara Pérez surname misspelling + Venus co-founder fabrication (tasting-rooms) | 2 |
| L'Infernal unverifiable acquisition claim ("Belondrade family") | 1 |
| Clos Erasmus biodynamic/organic status discrepancy (vineyards vs dietary) | 1 |
| Mas Martinet biodynamic status discrepancy (vineyards vs dietary) | 1 |
| Taste blocks stripped: 124 cuvées with directory/homepage-only citations | 124 |
| source_url substitution: 127 cuvées fixed (124 directory + 3 broken domain) | 127 |
| "finest" soft superlative in ferrer-bobet milestone | 1 |
| **Total** | **130** |

---

## Final ship_safety outcome

```
spain/priorat: ALL CHECKS PASSED
0 HARD failures
```

3 non-blocking WARNs in `check_evidence_content.py` (Vall Llach cuvées — language-match limitation, per-wine URLs are correct).
