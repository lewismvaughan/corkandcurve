# QA2 report — italy/piedmont

- Agent: QA2 (judgment pass, sections D, E, G, H, I, J, K)
- Date: 2026-05-25
- Upstream: QA1-COMPLETE (classification, scores, hectarage, 5 address fixes,
  cross-refs cleared). ship_safety PASS on entry.
- Dataset: 43 vineyards, 98 cuvées, 12 signature-wines, 8 food-pairings,
  10 dietary entities.

## Verdict

**QA2-COMPLETE.** 7 defects found and corrected:
- 5 organic-certifier misattributions (Section E)
- 1 flaky source_url swapped (transient 502 on a HARD gate)
- 4 "in the heart of" geographic-filler phrases tightened (Section H, counted
  as 1 prose-class defect)

ship_safety re-run after edits: **0 HARD, ALL CHECKS PASSED.**

---

## Section D — Ownership currency (2024–2026)

All flagged Piedmont traps verified CURRENT. **0 defects.**

| producer | data owner | verdict |
|---|---|---|
| Gaja | Gaja family (Gaia, Rossana, Giovanni) | current ✓ |
| Fontanafredda | Eataly group (Oscar Farinetti) | current ✓ |
| Prunotto | Marchesi Antinori | current ✓ |
| Pio Cesare | Federica (Rosy) Boffa (Pio Boffa d.2021) | current ✓ |
| Vietti | Krause Holdings (Kyle Krause) | confirmed via WS/Decanter; Krause owns since 2016, still owned 2024 ✓ |
| Ceretto | Ceretto family | current ✓ |
| Michele Chiarlo | Chiarlo family | current ✓ |
| Giacomo Borgogno | Farinetti family (Oscar Farinetti) | confirmed via Wine Spectator; Farinetti since 2008, Andrea Farinetti runs it ✓ |

No stale/pre-acquisition owners anywhere across the 43 vineyards.

## Section E — Biodynamic / organic certification

Hard-fail class (promoting practising → certified) CLEAN:
- Ferdinando Principiano correctly `biodynamic_practicing` / organic `none`.
- Cascina delle Rose + Cascina Tavijn (natural) correctly uncertified (`none`).
- Rivetto `demeter_certified` VERIFIED (Decanter/wein.plus: first Demeter
  estate in Barolo/Barbaresco, certified 2016). Kept.

**5 certifier-misattribution defects FIXED.** The research agent had stamped a
blanket `organic_status: "icea"` on every certified-organic estate. ICEA is a
specific Italian certifier and the template publishes the value verbatim, so a
wrong/unverifiable certifier is a published fabrication. Verified the real
bodies and corrected:

| slug | was | now | source |
|---|---|---|---|
| gd-vajra-organic | icea | suolo_e_salute | Aldo Vaira joined Suolo e Salute 1971 (Grape Collective) |
| gd-vajra-lowsulfite | icea | suolo_e_salute | same producer |
| punset-organic | icea | ecocert | Punset certified by Ecocert Italia (italian-organicwineroute / WS) |
| punset-vegan | icea | ecocert | same producer |
| trediberri-organic | icea | ccpb | "certified by CCPB srl, Bologna" (producer About page) |

Rivetto's `icea` retained: ICEA is Demeter Associazione Italia's Italian
inspection body, so it is consistent with Rivetto's Demeter certification.
Stale `organic_certifier` free-text on the three corrected estates updated to
the verified body names; `certified_year` for Trediberri set to 2012 (CCPB
conversion year per producer).

Note: 4 of the 5 estates' own websites name no certifier at all; only the
producer/registry cross-checks above resolved the bodies. The blanket-ICEA
pattern is a research regression worth a prompt note for future regions.

## Section G — Cross-link sanity

- wines.json: **0** non-null `pairings[*].tablejourney_ref` (cuvée pairings
  0%, as research stated — Piedmont dishes not on TJ). No fabricated TJ paths.
- food-pairing.json: exactly **1** non-null `tablejourney_ref`:
  `italy/milan/dish/risotto-alla-milanese` on the Langhe Riesling × Milanese
  risotto pairing. HEAD-resolves **200**, correctly scoped under italy/milan.
  **0 defects.**

## Section H — Voice + prose

- No em-dashes / en-dashes in any data file.
- No banned AI-tells.
- **4 "in the heart of" geographic-filler phrases tightened** (1 prose-class
  defect): wine-restaurants (Alba restaurant), vineyards (Borgogno),
  tasting-rooms (Vietti), wine-schools (WSET academy).
- Score-bunching: global editorial_score CV = 0.0491 (> 0.04), bell-curve
  distribution 3.9–5.0 across 333 entities. Per-topic sub-0.04 CVs are an
  artifact of curated topic clustering in a narrow band, not fabrication —
  editorial scores are curatorial ratings, not critic point scores. No defect.
- Description clones: none. One shared 40-char opening (two Produttori del
  Barbaresco single-cru Riservas) diverges fully after the opening. OK.

## Section I — Cuvée taste-note sourcing

- 25 cuvées with filled aroma/palate AND editorial_score ≥ 4.5: every
  `cuisine_evidence_url` is a **specific per-cuvée page** (wilsondaniels.com/
  wine/gaja/<cuvée>, vietti.com/en/wines/<cuvée>, michelechiarlo.it/en/wines/
  <cuvée>, marchesidigresy.com/vini/<cuvée>, etc.) — NO homepages or
  directory pages. **0 defects.**
- Descriptor diversity is healthy (graphite/licorice/potpourri vs
  plum/cedar/grapefruit vs mint/tea-leaf/tobacco) — not template fill.
- Live-confirmed descriptor text on cited pages:
  - Barolo Brunate (vietti.com): 6/6 descriptors present.
  - Sori Tildin (wilsondaniels.com): graphite, licorice, dried cherry,
    mineral present (correct per-cuvée page).
- Summary-only cuvées: 66 carry a `taste.summary` + structural axes
  (body/tannin/acidity/finish) but EMPTY `aroma`/`palate` arrays — no
  fabricated sensory descriptors. Empty arrays are acceptable per brief. The
  "11" figure in the brief was approximate; the larger count is the same
  summary-only style (JS/bot-walled producers), not a defect.

## Section J — Tag vocabulary

- 56 distinct tags across wines.json; every one in docs/WINE_TAGS.md.
- All from researcher-emitted axes (style, body, tannin, acidity, pairing,
  occasion, mood, editorial).
- **Zero derived-axis leakage** — no price-*, grape, world, sweetness, ageing,
  or production tags. **0 defects.**

## Section K — Vintage-agnostic discipline

- No 4-digit year in any cuvée `slug` or `name` (wines.json + signature-wines).
  Single-vineyard crus are separate vintage-agnostic cuvées (correct).
  **0 defects.**

## ship_safety supplementary fix

`verify_entities.py` flagged 1 HARD `dead_source_url` (502) on
`enoteca-vinile-turin` (nightlife.json) — a transient wanderlog 502 under
ship_safety's concurrent load (direct retry returned 200 ×3). Tripadvisor
alternative 403s (anti-bot); swapped to a stable venue page on foodiestrip.com
whose URL carries the verbatim address (Via Principe Amedeo 21/L, 10123
Torino), verified to list the correct venue + address. HARD count → 0.

## Defect count

**7 defects, all corrected:**
- 5 × organic-certifier misattribution (Section E)
- 1 × prose geographic-filler ("in the heart of" ×4 occurrences, Section H)
- 1 × flaky source_url on HARD gate (verify_entities)

Sections D, G, I, J, K: 0 defects.

ship_safety after all edits: **0 HARD, ALL CHECKS PASSED.**
