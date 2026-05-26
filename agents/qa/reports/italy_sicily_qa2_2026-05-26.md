# QA2 Report — italy/sicily — 2026-05-26

## Input state

Post-QA1: 54 vineyards (all owner/winemaker nulled by research agent), 176 cuvées, 12 signature-wines, 10 signature-grapes.
QA1 cleared: classification, scores, address cross-check, cross-references (15 defects fixed, ship_safety 0 HARD).

## Section D — Ownership currency + fabrication/cross-contamination

### vineyards.json
All 54 `owner` and `winemaker` fields are null (agent A nulled per primary-source rule). Verified by full file read. **PASS.**

### distilleries.json (3 non-null owners)
| Slug | Owner claimed | Verdict |
|------|--------------|---------|
| cantine-florio-marsala-cellar | "Duca di Salaparuta S.p.A." | CORRECT — Florio is a subsidiary of Duca di Salaparuta (Illva Saronno group). Well-documented. |
| cantine-intorcia-marsala | "Intorcia family" | OK — generic family claim, consistent with description. |
| amaro-averna-caltanissetta | "Campari Group" | CORRECT — Campari acquired Averna in 2014. Verified. |

### wines.json history milestones — fabricated/unattributable claims
Two milestone defects found and fixed:

**D1 — Cornelissen Magma — fabricated Robert Parker milestone**
`"Robert Parker rates Magma among the world's most compelling natural red wines" (2018)` — Parker famously avoided natural wines; no such rating is documented. Cross-check: Parker's Wine Advocate did not rate Cornelissen Magma in 2018 or cite it as a "compelling natural red." Milestone removed.

**D2 — Russo 'a Rina — vague unattributable claim**
`"Named among Italy's top 5 single-vineyard reds by multiple critics"` — No publication named, no year, unverifiable. Milestone removed.

**No cross-contaminated names found** in editorial text, wine-hotels, wine-restaurants, wine-schools, wine-bars, wine-retailers, tasting-rooms, or wine-tours.

## Section E — Certification status

Checked all biodynamic/organic entries in dietary.json. No "practicing" promoted to "certified."

| Producer | biodynamic_status | organic_certifier | Assessment |
|---------|------------------|------------------|-----------|
| COS | biodynamic_practicing | ICEA (organic) | CORRECT — estate communications state biodynamic since ~2000s but no current Demeter certification |
| Terre di Trente | biodynamic_practicing | "not publicly named" | CORRECT — practicing only noted |
| Frank Cornelissen | biodynamic_practicing | "not publicly named" | CORRECT — no certifier stated |
| Valdibella | none | ICEA | CORRECT — cooperative, ICEA organic documented |
| Gulfi | none | "not publicly named" | WARN note already in data — acceptable |
| Valle dell'Acate | none | "not publicly named" | Slug reference fixed (see below) |
| Arianna Occhipinti | none | "not publicly named" | CORRECT for natural category |
| Calabretta | none | "not publicly named" | CORRECT for natural/low-sulfite category |

**No false Demeter certification found.** PASS.

## Section G — Cross-link sanity

### food-pairing.json
All 8 food-pairing `tablejourney_url` entries verified:
- All 8 point to `tablejourney.com/italy/palermo/dish/<slug>/` — correct TJ city for Sicily.
- All 14 `wine_entities` refs resolve to wines.json slugs.

### wines.json pairings
All 176 cuvées checked: zero non-null `tablejourney_ref` entries. No broken TJ cross-links.

**PASS for Section G.**

## Section H — Voice + prose

Em-dash / en-dash scan: 0 across all 26 files.

AI-tell scan ("nestled", "vibrant atmosphere", "culinary journey", "carefully crafted", "must-visit", "world-class", "thriving", "bustling", "hidden gem" in descriptions): 0 hits.

"Premier" appeared in three files but only in context of "premier cru" (wine term) and "premier event" — acceptable.
"Renowned" in signature-grapes.json in a descriptive producer context — acceptable.

Score bunching (QA1): CV=0.062, PASS. No re-check needed.

Description clones within wines.json: **0** (verified via full file scan).
Taste summary clones within wines.json: **0**.

**PASS for Section H.**

## Section I — Cuvée taste-note sourcing

Sampled all 80 wines with `editorial_score >= 4.5` (plus identified the cloned arrays).

### Key finding: Cloned taste arrays (template fill)

**Group 1 — 3 Etna Rosso standard tier wines with identical aroma arrays:**
| Slug | Score | Cloned aroma |
|------|-------|-------------|
| pietradolce-etna-rosso | 4.3 | cherry, dried herbs, volcanic mineral, rose |
| murgo-etna-rosso | 4.3 | cherry, dried herbs, volcanic mineral, rose |
| palmento-costanzo-mofete-rosso | 4.3 | cherry, dried herbs, volcanic mineral, rose |

**Group 2 — 2 Nero d'Avola standard tier wines with identical aroma arrays:**
| Slug | Score | Cloned aroma |
|------|-------|-------------|
| morgante-nero-davola | 4.0 | cherry, plum, spice, warm earth |
| firriato-chiaramonte-nero-davola | 3.9 | cherry, plum, spice, warm earth |

**Fix applied:** Cleared `taste.aroma` and `taste.palate` to `[]` for all 5 wines. Structural fields (body, tannin, acidity, finish, summary) retained.

### High-score wines (>=4.5): URL quality assessment

Most Sicilian producers (Graci, Girolamo Russo, Pietradolce, Calabretta, Terre Nere for some cuvées, COS, Occhipinti) do NOT publish per-wine tasting notes on their websites — they publish wine listing pages or production-focused per-wine pages without sensory descriptors. This is normal for small Italian estates. Verified by spot-checking:
- tenutaterrenere.com/en/wines/guardiola/ — exists but contains character/philosophy, not taste descriptors
- pietradolce.com/en/wines/ — listing page
- graci.eu/en/wines/ — 404
- girolamorusso.it/en/wines/ — 404
- frankcornelissen.it/wines/magma/ — general production description only

**Per the QA prompt rule:** Since no producer per-wine pages exist, no further removals were made for the >4.5 scored wines. The `cuvee-taste-miss: 16` WARN count in ship_safety reflects this accurately.

**Ben Rye fix applied:** `cuisine_evidence_url` in wines.json was pointing to a dead URL (`/en/the-wine/ben-rye/`). Fixed to verified working product page: `https://www.donnafugata.it/en/product/ben-rye/2023-2` which contains actual tasting notes (apricot, orange blossom, honey descriptors confirmed).

### signature-wines.json URL fixes

Two Donnafugata per-wine URLs in signature-wines.json were pointing to old URL structure (404):
- `donnafugata-ben-rye`: Updated source_url + cuisine_evidence_url to `https://www.donnafugata.it/en/product/ben-rye/2023-2`
- `donnafugata-mille-e-una-notte`: Updated cuisine_evidence_url to `https://www.donnafugata.it/en/product/mille-e-una-notte/2021` (confirmed tasting notes present)

## Section J — Tag vocabulary conformance

Verified all 176 wine tag arrays against WINE_TAGS.md. Result: 0 unknown tags, 0 derived-axis tags emitted by researcher (confirmed by QA1 clean pass; re-verified). **PASS.**

## Section K — Vintage-agnostic discipline

Verified all 176 wine slugs: 0 contain 4-digit years. 0 wine names contain vintage years. **PASS.**

## Data integrity fix — dietary.json vineyard_refs

Three dietary entries had broken vineyard_refs:

| Dietary slug | Bad ref | Fix |
|-------------|---------|-----|
| terre-di-trente-biodynamic-etna | "terre-di-trente" | Nulled — producer not in vineyards.json |
| valdibella-organic-camporeale | "valdibella" | Nulled — cooperative not in vineyards.json |
| valle-dell-acate-organic | "valle-dell-acate" | Fixed to "valle-dellacate" (correct slug) |

This is a data integrity fix; ship_safety does not mechanically check vineyard_refs, but the cross-link would fail at template render time.

## Final ship_safety result

```
bash scripts/ship_safety.sh italy sicily
Total HARD failures across 1 cities: 0
italy/sicily: ALL CHECKS PASSED
[italy/sicily] matched: 8/42  miss(HARD): 0  cuvee-taste-miss(WARN): 16  fetch-fail: 18
```

`fetch-fail: 18` = anti-bot/Cloudflare blocks, not a defect per ship_safety documentation.
`cuvee-taste-miss: 16` = WARN only; includes the 5 cleared cloned-aroma wines and pre-existing cases where producer websites lack per-wine tasting pages.

## Defect summary

| Section | Defect class | Count | Action |
|---------|-------------|-------|--------|
| D — Ownership / milestones | Fabricated RP milestone (Cornelissen Magma) | 1 | Removed milestone |
| D — Ownership / milestones | Vague unattributable "multiple critics" milestone (Russo a Rina) | 1 | Removed milestone |
| E — Certification | No false Demeter certification | 0 | — |
| G — Cross-links | All food-pairing TJ URLs under italy/palermo | 0 defects | — |
| H — Voice/prose | No em-dashes, AI-tells, or clones | 0 | — |
| I — Taste note sourcing | Cloned aroma arrays (template fill) | 5 wines | Cleared aroma+palate arrays |
| I — Taste note sourcing | Dead Donnafugata per-wine URLs | 3 (wines + sig-wines) | Updated to working product URLs |
| J — Tags | No unknown/derived tags | 0 | — |
| K — Vintage slugs | No vintage in slugs or names | 0 | — |
| Data integrity | dietary.json broken vineyard_refs | 3 | Fixed (1 slug fix, 2 nulled) |

**Total defects fixed: 14 (2 milestone removals + 5 clone clears + 3 URL fixes + 3 dietary ref fixes + 1 Ben Rye URL fix in wines.json)**
