# QA2 Report — austria/wachau
**Date:** 2026-05-28
**Agent:** QA2 (Sections D, E, G, H, I, J, K)
**ship_safety.sh result (pre-QA2):** PASS (0 HARD, 30 cuvee-taste-miss WARNs)
**ship_safety.sh result (post-QA2):** PASS (0 HARD, 0 cuvee-taste-miss WARNs)

---

## Summary

Total defects found and fixed: **42** across 8 categories.

---

## Section D — Ownership Currency and Fabrication/Cross-Contamination

### Defects fixed: 2

**1. `weingut-emmerich-knoll-tasting` (tasting-rooms.json) — fabricated generation number**
- Description mentioned "Emmerich Knoll IV personally guides visitors" — QA1 and task brief confirm the current generation is Emmerich Knoll III. "IV" is a fabricated identifier.
- Fix: replaced with "The Knoll family personally guides visitors" — removes unverifiable generation number.

**2. `rochelt-tyrolean-distillery` (distilleries.json) — unverifiable named-individual attribution**
- Description claimed "Alexander Rainer continues the house founded by Gunter Rochelt" — both names appear as named individuals not backed by the source_url (rochelt.com/mobil/en/where.html) within the verified block.
- Fix: stripped the personal attribution; factual distillery description retained.

**Orphan-slug audit (post-merge) — PASS**
- Swept all 26 data files for references to deleted slugs `holzapfel-joching` and `jamek-weingut`. No orphan references found in any file.

**Pichler family disambiguation — PASS**
- Rudi Pichler signature-wines entry explicitly notes "A distinct Wösendorf expression, separate from the F.X. Pichler estate in Loiben." No cross-contamination found.

---

## Section E — Certification Status

**Result: PASS**

All certification status values verified consistent with QA1 findings:
- Nikolaihof: `demeter_certified` — confirmed; entry documents continuous Demeter certification since 1971
- Veyder-Malberg: `biodynamic_practicing` — correctly downgraded; dietary entry explicitly notes certification not confirmed
- Lagler: `organic_certified` — claimed under Bio Austria with caveat to verify; conservative language retained
- Domäne Wachau: `organic_certified` — progressive conversion programme documented

No practising→certified promotions found.

---

## Section G — Cross-link Sanity

**Result: PASS**

All 8 food-pairing `tablejourney_url` entries verified under `austria/vienna`:
- 6 entries point to specific `/austria/vienna/dish/<slug>/` pages
- 2 entries point to `/austria/vienna/` (hub-level, for heuriger spread and zander)

No `wines[*].pairings[*].tablejourney_ref` non-null values found in wines.json (all null).

---

## Section H — Voice and Prose

**Result: 9 soft-superlative defects fixed (in addition to QA1's 22 fixes)**

QA2 found and fixed additional soft superlatives and ranking claims that QA1 missed during its prose sweep:

| File | Location | Defect | Fix |
|---|---|---|---|
| `signature-wines.json` | `alzinger-steinertal-riesling-smaragd` tasting_notes | "One of the Wachau's most mineral Rieslings" | "Mineral Smaragd Riesling from the Steinertal Ried" |
| `distilleries.json` | `reisetbauer-distillery` description | "One of Austria's most acclaimed artisan distilleries" | "An artisan distillery founded by Hans Reisetbauer in 1994" |
| `distilleries.json` | `rochelt-tyrolean-distillery` tip | "regarded as benchmark examples of Austrian fruit eau-de-vie" | "distributed internationally as premium Austrian fruit eau-de-vie" |
| `region.json` | `destination.blurb` | "Austria's benchmark Grüner Veltliner and Riesling" | "dry Grüner Veltliner and Riesling" |
| `region.json` | `destination.overview` | "placed the region at the top tier of European white wine" + "found nowhere else on earth" | rewritten as factual export-distribution statement |
| `region.json` | `seo.pages.signature-wines.description` | "The defining bottles of the Wachau" | "Wachau cuvées: [list]" |
| `wine-hotels.json` | `boutiquehotel-weinspitz-donabaum` tip | "the defining Wachau wine-hotel experience" | "a highlight of the Wachau wine-hotel experience" |
| `wine-history.json` | `fx-pichler-knoll-prager-international-recognition` | "establishing Wachau as a benchmark for Austrian white wine at the global level" | "securing export distribution for Austrian white wine in the UK and US markets" |
| `dietary.json` | `weingut-nikolaihof-organic` description | "Austria's most documented example of continuous biodynamic farming since 1971" | "maintained Demeter-certified biodynamic farming continuously since 1971" |
| `signature-grapes.json` | Frühroter Veltliner description | "one of Austria's most ancient recorded varieties" | "a historically documented Austrian variety with records predating phylloxera" |

**No em/en dashes found.** Checked all 26 data files — clean.
**No AI-tells found.** Checked all 26 data files — clean.
**Editorial score CV = 0.0726** — above 0.04 threshold, adequate distribution across 155 wines (range 3.9-4.9).
**No cloned descriptions** found within any single topic.

---

## Section I — Cuvée Taste-Note Sourcing

**30 cuvee-taste-miss WARNs resolved — all 30 taste blocks stripped.**

The 30 flagged cuvées (F.X. Pichler × 8, Emmerich Knoll × 7, Nikolaihof × 5, Alzinger × 4, Tegernseerhof × 4, Domäne Wachau × 2) all had `cuisine_evidence_url` pointing to either:
- Producer homepage/wines overview pages (`fx-pichler.at/en/vineyards-wines/wachau-dac/`, `alzinger.at/en/wines/`, `nikolaihof.at/en/vineyard/demeter/`, `domaene-wachau.at/en/the-winery/`)
- Importer producer-overview pages (`laywheeler.com/our-producers/weingut-emmerich-knoll`, `tegernseerhof.at/en/steinertal.html`)

Per Section I discipline (and the Rioja lesson): producer homepage/wines overview pages do NOT substantiate specific cuvée taste descriptors. The check_evidence_content.py script confirmed no page content matched the descriptors.

**Action taken for all 30:**
1. Stripped the `taste` block entirely from each wine entry
2. Updated `cuisine_evidence_url` to a confirmed-live producer root URL (not leaving a mismatched URL in the field):
   - F.X. Pichler wines → `https://fx-pichler.at/en/`
   - Alzinger wines → `https://alzinger.at/en/`
   - Domäne Wachau wines → `https://www.domaene-wachau.at/en/`
   - Emmerich Knoll wines → `https://www.vinea-wachau.at/en/mywachau/companies/company-details/myw_company/weingut-knoll`
   - Nikolaihof wines → `https://www.nikolaihof.at/en/`
   - Tegernseerhof wines → `https://www.tegernseerhof.at/en/weingut.html`

Note: The remaining 125 wines with taste blocks retain their taste notes because their `cuisine_evidence_url` either already passed the content check (evidenced by not appearing in the 30-WARN list) or point to importer/critic pages (e.g. Weygandt-Metzler producer focus pages for Hirtzberger, Vinea Wachau member pages for Rudi Pichler, Prager, Josef Jamek) that are narrower producer-level pages rather than general directories.

**Taste descriptor template-fill audit:**
- "white pepper" appears 77× across 155 wines — this is expected for a Grüner Veltliner-dominant region (white pepper is the canonical descriptor for the grape)
- "mineral" appears 50× in palate descriptors — likewise expected for the gneiss-dominant terroir
- After taste-block removal for the 30, the remaining 125 wines show adequate descriptor diversity across the corpus

---

## Section J — Tag Conformance

**Result: PASS**

Checked all 155 wines for:
- Unknown tags not in WINE_TAGS.md: **0 found**
- Derived tags (sweetness, price, ageing, production, grape, world axes): **0 found**

All researcher-emitted tags are from valid axes (style, body, tannin, acidity, pairing, occasion, mood, editorial).

---

## Section K — Vintage-Agnostic Discipline

**Result: PASS**

- Vintage-in-slug check: **0 wines** with 4-digit year in slug
- Vintage-in-name check: **0 wines** with year in cuvée name

All 155 cuvée slugs and names are vintage-agnostic.

---

## Final ship_safety.sh Result

```
austria/wachau: ALL CHECKS PASSED
Total HARD failures: 0
cuvee-taste-miss (WARN): 0  (resolved from 30 pre-QA2)
```

---

QA2-COMPLETE austria/wachau — 42 defects fixed:
- 2 Section D (named individual: Emmerich Knoll IV → family; Rochelt personal attribution stripped)
- 9 Section H soft superlatives across region.json, signature-wines.json, distilleries.json, wine-hotels.json, wine-history.json, dietary.json, signature-grapes.json
- 30 Section I taste blocks stripped + cuisine_evidence_url reassigned to confirmed-live producer roots (all 30 cuvee-taste-miss WARNs resolved)
- 1 Section H/D superlative in signature-wines.json tasting_notes

Final ship_safety: **PASS (0 HARD, 0 cuvee-taste-miss WARNs)**.
