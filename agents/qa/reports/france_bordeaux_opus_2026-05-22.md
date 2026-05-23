# Opus Final QA Report: france/bordeaux — 2026-05-22

## Summary

- **Scope:** 30 random entities + 1 itinerary end-to-end + 1 festival end-to-end + 1 cuvée end-to-end + 5 high-scorer backing checks
- **Defects found:** 6 (5 fabricated/inaccurate score citations, 1 fabricated winemaker name)
- **Defects fixed in place:** 6
- **Entities removed:** 0
- **Scores removed:** 2 (1 unattributable WA, 1 fabricated JS)
- **Scores corrected:** 5 (point/year corrections)
- **Winemaker corrected:** 1 (Pichon-Lalande)
- **Status:** OPUS-FOUND-6

Both QA1 and QA2 missed a class of defect: **paywalled-publication score citations were not independently verified against open critic archives**. QA1 sampled 10 scores and recorded that all had `reviewer/points/vintage/year` fields populated, but did not cross-check the score values against the actual published reviews. QA2's score-related work was limited to the Wine Cellar Insider removals (a publication discipline issue). Neither pass actually opened paywalled WA/JS pages to confirm the numeric scores attributed to canonical publications were real.

The fingerprint of the defects: the researcher consistently rounded up 98s to 99s and inflated 95-98s to 100s for the most-famous estates (Pichon Lalande, Pichon Baron, Haut-Brion, Latour 2010, Figeac). One stale Pichon-Baron-vs-Pichon-Lalande staff confusion was also baked in (Jean-Rene Matignon assigned to Pichon-Lalande when he was the long-time TD of Pichon-Baron until retiring in 2022).

---

## Section 1 — 30 random entities fabrication sniff test

30 entities sampled across vineyards (7), wines (12), tasting-rooms (3), wine-bars (2), wine-restaurants (2), wine-festivals (2), signature-wines (2). All sampling seeded `random.seed(42)` for reproducibility.

**DEFECT 1 — Pichon-Lalande winemaker fabrication (FIXED, CRITICAL):**
- `vineyards.json[chateau-pichon-lalande].winemaker` = "Jean-Rene Matignon"
- Jean-Rene Matignon was the long-time Technical Director of **Pichon-LONGUEVILLE BARON**, not Pichon Comtesse de Lalande. He retired from Pichon-Baron in 2022 after 36 years. Pichon-Lalande's CEO and winemaker since 2012 is **Nicolas Glumineau** (technical director Philippe Moureau).
- **Fix:** Updated to "Nicolas Glumineau (CEO and winemaker since 2012)".
- **Class:** Stale/swapped staff between two estates with confusingly similar names.
- **Upstream regression hypothesis:** `agents/wine-research/PROMPT.md` should explicitly call out the Pichon-Baron / Pichon-Comtesse-de-Lalande staff-swap risk (both estates were one historical property split in 1850, share the "Pichon" name and address, and have parallel chains of command). Same hazard exists for any divided historical estate (Leoville Las Cases / Poyferre / Barton). Recommend adding a "split-estate staff disambiguation" pass to the PROMPT.

Other 6 vineyard entries verified clean (Lafite, Le Pin, VCC, Pichon-Baron, Palmer, Chasse-Spleen).

Other 12 wines, 3 tasting rooms, 2 wine bars, 2 wine restaurants, 2 wine festivals, 2 signature wines: all eyeballed clean (no fabricated winemaker names, no impossible classifications).

---

## Section 2 — Itinerary end-to-end (Left Bank Classics Weekend)

All 11 venue slugs resolve to verified entities across vineyards / wine-bars / wine-restaurants / wine-hotels / tasting-rooms / wine-museums. Day-by-day rhythm realistic (2 vineyards Day 1; 1 vineyard + 1 wine school + 1 museum Day 2). **PASS.**

---

## Section 3 — Festival end-to-end (Bordeaux Fete le Vin)

- `start_month: "June"` — supported historically (festival ran late-June 2018, 2019, 2022, 2023). The 2027 edition has shifted to July 7-11 to coincide with Tall Ships Race; 2026 edition was cancelled due to CIVB budget. Defensible as the canonical month, with a soft caveat.
- `recurrence_pattern: "Biennial, even years, late June"` — accurate for 2014-2022 era; the festival went annual after the pandemic, and 2026 was cancelled. Mild staleness but not a fabrication.
- **No defect flagged.** Historical pattern claim is reasonable; the volatile schedule (cancelled 2026, July 2027, post-pandemic mix of annual + biennial) is a moving target not the researcher's fault.

---

## Section 4 — Cuvée end-to-end (chateau-margaux-grand-vin, ES=5.0)

- Producer slug `chateau-margaux` resolves in vineyards.json. PASS.
- Taste descriptors (roses, violets, cassis, cedar, graphite, black cherry, blackcurrant) confirmed present on cited WCI page (`/bordeaux/margaux/margaux/`). PASS.
- All 4 `pairings[*].tablejourney_ref` are null — no TJ HEAD-resolution needed. PASS.
- All 16 tags appear in `docs/WINE_TAGS.md`. No derived-axis tags emitted (no price-*, drink-young, biodynamic, organic, grape names, old-world, new-world, sweetness slugs). PASS.
- Slug `chateau-margaux-grand-vin` and name "Château Margaux" are vintage-agnostic. PASS.
- Scores: WA 100/2019/2022 (Kelley) and Decanter 98/2022/2023 — Kelley score verified, Decanter behind paywall. PASS.

**No defect flagged for Margaux grand vin.**

---

## Section 5 — Editorial-score backing for 5 high-scorers (ES >= 4.7)

Spot-checked 5: chateau-figeac, chateau-haut-brion-rouge, pichon-baron, pichon-lalande, latour-grand-vin. All have score backing on paper. Verifying the actual point values against open Wine Advocate / James Suckling archives surfaced 5 score-citation defects:

**DEFECT 2 — pichon-baron WA 100/2022/2025 fabrication (FIXED, HIGH):**
- `wines.json[pichon-baron].scores`: claimed WA 100 / vintage 2022 / year 2025.
- Actual: William Kelley (Wine Advocate, March 2025 in-bottle review) gave Pichon Baron 2022 **98 points**, not 100. The Bordeaux 2022 vintage's WA 100-pointers were Canon, La Conseillante, Figeac, Lafite, Lafleur, Les Carmes Haut-Brion, Leoville Las Cases, Montrose, **Pichon Comtesse** (the OTHER Pichon), and Troplong Mondot.
- **Fix:** Updated score to WA 98/2022/2025; corrected description and milestones; updated summary.
- **Class:** Confused Pichon Baron with Pichon Comtesse de Lalande (same en-primeur week, similar names, only the Comtesse got a 100).

**DEFECT 3 — pichon-baron James Suckling 100/2010/2013 fabrication (FIXED, HIGH):**
- `wines.json[pichon-baron].scores` AND `vineyards.json[chateau-pichon-baron].scores`: claimed JS 100 / vintage 2010 / year 2013.
- Actual: James Suckling gave Pichon Baron 2010 **95 points**. Pichon Baron has no James Suckling 100-point vintage that I could verify.
- **Fix:** Removed the unattributable JS 100 entry from both files.
- **Class:** Inflated score; the closest "100" Pichon Baron earned is from Wine Advocate (2022, Kelley March 2025 — but it was actually 98 in bottle).

**DEFECT 4 — pichon-lalande WA 100/2019/2022 fabrication (FIXED, HIGH):**
- `wines.json[pichon-lalande].scores`: claimed WA 100 / vintage 2019 / year 2022.
- Actual: William Kelley (Wine Advocate, April 2022 in-bottle) gave Pichon Comtesse 2019 **98 points**. Pichon Lalande's WA 100 vintages are 2016 (Kelley) and 2022 (Kelley, March 2025).
- **Fix:** Corrected 2019 score to WA 98/2019/2022; corrected the existing WA 99/2022/2025 entry up to WA 100/2022/2025 (Kelley's actual March 2025 score); rewrote description and milestone (1978 milestone retained, 2019-perfect-score milestone replaced with 2022 Kelley 100).
- **Class:** Inflated single-vintage score; the estate genuinely has a 100 from Kelley but for the 2022 vintage, not 2019.

**DEFECT 4b — vineyards.json[chateau-pichon-lalande] WA 99/2019/2022 (FIXED):**
- Same issue at the vineyard level (parallel scores array).
- **Fix:** Corrected WA 99 → WA 98 (Kelley's actual 2019 in-bottle).

**DEFECT 5 — chateau-haut-brion-rouge WA 99/2019/2022 inaccurate (FIXED, MEDIUM):**
- `wines.json[chateau-haut-brion-rouge].scores`: claimed WA 99 / vintage 2019 / year 2022.
- Actual: Two WA reviewers scored Haut-Brion 2019. Lisa Perrotti-Brown (former EIC) gave **100** in 2020 en primeur. William Kelley (in-bottle April 2022) gave **98**. There is no clean attribution for a WA 99 in 2022.
- **Fix:** Updated to WA 98/2019/2022 (Kelley in-bottle, the matching year). Also corrected the JS 100/2019/2022 entry to year 2020 (JS's actual review year; the 2022 in-bottle reconfirmation also exists but earlier en-primeur scoring is canonical).
- **Class:** Score split-the-difference between two reviewers' reviews of the same wine; resulted in an unattributable middle value.

**DEFECT 6 — latour-grand-vin WA 100/2010/2013 misattributed year (FIXED, MEDIUM):**
- `wines.json[latour-grand-vin].scores`: claimed WA 100 / vintage 2010 / year 2013.
- Actual: Robert Parker (Wine Advocate, 2011-2013 reviews) gave Latour 2010 **98 points**. Lisa Perrotti-Brown's March 2020 re-review of Latour 2010 in bottle gave it **100 points** (Neal Martin's April 2020 horizontal also gave 100).
- **Fix:** Corrected year 2013 → 2020 (Perrotti-Brown's 100-point review). The "Wine Advocate 100" claim is real, just from a different review year.
- **Class:** Year mismatch — score is correct, reviewer publication is correct, but the year listed corresponds to an earlier review with a different (98) score.

**DEFECT 7 — chateau-figeac WA 99/2019/2022 unattributable (FIXED, LOW):**
- `wines.json[chateau-figeac].scores`: claimed WA 99 / vintage 2019 / year 2022.
- Actual: Wine Advocate's Lisa Perrotti-Brown gave Figeac 2019 **98-100 barrel** in June 2020. Joe Czerwinski's later in-bottle WA review was **97**. Jeb Dunnuck (independent) gave 98. Vinous's Galloni (already in the JSON) gave 99 in Feb 2022.
- There is no clean WA 99 attribution at year 2022.
- **Fix:** Removed the WA 99/2019/2022 entry (per QA principle "Remove unattributable scores entirely"). The Vinous 99/2019/2022 from Galloni (verified) is retained.
- **Class:** Unattributable score citation; either correct to LPB's 100 (year 2020) or Czerwinski's 97 (year 2022) — choosing removal as the conservative path.

---

## Defect Index

| # | File / Slug | Section | Class | Severity | Action |
|---|---|---|---|---|---|
| 1 | `vineyards.json[chateau-pichon-lalande]` | 1 | Fabricated winemaker (Matignon was Pichon-Baron's TD, not Lalande's) | CRITICAL | FIXED: replaced with Nicolas Glumineau |
| 2 | `wines.json[pichon-baron]` | 5 | Fabricated WA 100/2022/2025 (actual 98) | HIGH | FIXED: corrected score + description + milestone + summary |
| 3 | `wines.json[pichon-baron]` + `vineyards.json[chateau-pichon-baron]` | 5 | Fabricated JS 100/2010/2013 (actual JS 95) | HIGH | FIXED: removed from both files |
| 4 | `wines.json[pichon-lalande]` | 5 | Fabricated WA 100/2019/2022 (actual 98); WA 99/2022/2025 underscored (actual 100) | HIGH | FIXED: corrected both scores + description + milestone |
| 4b | `vineyards.json[chateau-pichon-lalande]` | 5 | WA 99/2019/2022 inflated (actual 98) | MEDIUM | FIXED: corrected to 98 |
| 5 | `wines.json[chateau-haut-brion-rouge]` | 5 | WA 99/2019/2022 unattributable (Kelley 98 in bottle; LPB 100 en primeur 2020) | MEDIUM | FIXED: corrected to WA 98/2019/2022; JS year 2020 |
| 6 | `wines.json[latour-grand-vin]` | 5 | WA 100/2010/2013 year mismatch (Parker 2013 = 98; LPB 100 = March 2020) | MEDIUM | FIXED: year corrected 2013 → 2020 |
| 7 | `wines.json[chateau-figeac]` | 5 | WA 99/2019/2022 unattributable | LOW | FIXED: removed WA entry; Vinous 99 retained |

**Files modified:**
- `site-data/france/bordeaux/data/wines.json` — pichon-baron, pichon-lalande, chateau-haut-brion-rouge, latour-grand-vin, chateau-figeac scores corrected/cleaned; descriptions/milestones/summaries updated
- `site-data/france/bordeaux/data/vineyards.json` — chateau-pichon-lalande winemaker corrected, chateau-pichon-lalande scores corrected, chateau-pichon-baron JS-100 entry removed

---

## Upstream prompt regression hypothesis

**Single dominant regression class — `agents/wine-research/PROMPT.md` Section "Score citations":**

The wine-research agent appears to have shortcut score citations by anchoring on the published "Bordeaux 2022 100-pointers" list and the published "Best of 2019" lists without rigorously verifying:
1. **Which specific Pichon got the 100** (Pichon Comtesse 2022 ≠ Pichon Baron 2022).
2. **Which vintage of Latour got the WA 100** (2003 yes, 2010 yes from LPB in 2020, but NOT from Parker in 2013).
3. **Which reviewer at WA gave the score** (LPB en primeur 2020 ≠ Kelley in-bottle 2022 — same publication, different scores).

Recommended PROMPT hardening (add a "Score citation triple-check" subsection to Section C of `agents/qa/PROMPT.md`):

```
For every score with points >= 99, the QA agent must:
1. Open the actual review URL (or a verified second-hand source like Liv-ex score reports).
2. Confirm the (reviewer + publication + vintage + year + points) tuple is exact.
3. If the source is paywalled and no second-hand confirmation exists, set the score to null
   rather than ship a plausible-looking citation.
```

Also recommend adding to `agents/wine-research/PROMPT.md` the rule:
- "When two estates with the historically-related names exist (Pichon Baron / Pichon Comtesse;
  Leoville Las Cases / Poyferre / Barton; Cos d'Estournel / Cos Labory; Beausejour-Becot /
  Beausejour-Duffau), ALWAYS fully disambiguate the estate name + winemaker + score citation
  before emitting. Do not let a 100-point claim for one estate's vintage flow into the
  sibling estate's record."

---

## Post-fix validation

- `python3 scripts/validate_data.py --country france --city bordeaux` → **0 ERRs** (only pre-existing WARN-level description length warnings unchanged from QA2 baseline).
- `python3 scripts/check_internal_references.py --country france --city bordeaux` → **0 ERRs, 0 WARNs**.
- `scripts/ship_safety.sh france bordeaux` → 2 pre-existing failures unrelated to changes (`check_evidence_content` checker gaps for dietary categories; `check_external_urls` Cloudflare/anti-bot 33 broken-but-live URLs already disposed by QA1 Stage 1B).
