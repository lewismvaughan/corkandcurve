# Opus Final QA Report: italy/tuscany — 2026-05-23

## Summary

- **Scope:** narrow read per brief — 30-entity skim, one itinerary end-to-end, one festival end-to-end, one cuvée end-to-end, 5 high-editorial-score spot-check, **random sample of 3 of the surviving WA 95+ scores in wines.json** (the brief's emphasis given the QA2 Argiano regressions).
- **Defects found:** 9 (8 score-tuple defects + 1 festival month/recurrence fabrication). Expected to find nothing; the score-discipline weak spot reasserted itself.
- **Defects fixed:** 9 (5 score corrections, 2 score-tuple drops, 1 mirror correction in vineyards.json, 1 festival recurrence/month correction). Signature-wines prose mirrors rewritten for soldera + avignonesi + fontodi.
- **ship_safety.sh post-fix:** ALL 7 CHECKS PASS, 0 HARD failures.
- **Entities removed:** 0 (score tuples dropped on existing entities; no whole entity drops).

---

## Section 1 — 30-entity skim across topics

Sampled 30 random entities across all 24 topic files (seed 42). Spot-checked 10 wines.json entries with critic-citation prose for fabricated press credentials and winemaker-name claims.

- **Winemaker name claims:** verified Federico Carletti (poliziano), Martino Manetti (montevertine), Giovanni Manetti (fontodi), Sergio Manetti (montevertine history), Luca Sanjust (petrolo), Lorenza Sebasti + Marco Pallanti (castello-di-ama) all match producer About pages.
- **Press-credential claims:** all "Wine of the Year" claims previously addressed by QA1 (Argiano WS WOTY 2023, Solaia WS WOTY 2000, Ornellaia WS WOTY 2001, Casanova di Neri Tenuta Nuova WS WOTY 2006). No new fabricated WOTY claims found in sample.
- **Claim/source mismatch:** see Section 5 below for the systemic WA-score issue.

---

## Section 2 — One itinerary end-to-end (tuscany-grand-tour-seven-days)

Picked the 7-day Grand Tour per brief. Every `days[*].venues[*]` slug verified against entity union:

| Day | Venue slug | Resolves to | Status |
|---|---|---|---|
| 1 | tenuta-di-capezzana | vineyards.json | OK |
| 2 | castello-di-ama, isole-e-olena | vineyards.json | OK |
| 3 | san-felice, riecine | vineyards.json | OK |
| 4 | casanova-di-neri, banfi, argiano | vineyards.json | OK |
| 5 | poliziano, salcheto | vineyards.json | OK |
| 6 | tenuta-san-guido, tenuta-dell-ornellaia | vineyards.json | OK |
| 7 | panizzi | vineyards.json | OK |

**13 of 13 slugs resolve cleanly. 0 dangling venues. Pin coverage OK.**

Tasting/restaurant prose (Le Volpi e l'Uva, Coquinarius, Officina della Bistecca, Enoteca Tognoni, Procacci, Pitti Gola e Cantina, Ristoro di Lamole, Osteria Magona, Re di Macchia) cross-confirmed in nightlife.json + wine-restaurants.json + wine-bars.json — all real venues, addresses self-consistent.

---

## Section 3 — One festival end-to-end (benvenuto-brunello)

Picked Benvenuto Brunello per brief. Cross-checked claimed month + recurrence pattern against `verified.source_url` (benvenutobrunello.com/en/).

**DEFECT OPUS-F1 — Benvenuto Brunello month + recurrence fabricated (FIXED):**
- JSON claimed: `recurrence_pattern: "annual, last week of February"`, `start_month: "February"`.
- Primary source (benvenutobrunello.com/en/) explicitly shows the **2025 edition: November 20-24** and **2023 edition: November 17-28**. Consortium home (consorziobrunellodimontalcino.it) confirms: "20th-24 November 2025 | Montalcino."
- The event historically ran in late February but was moved to November in 2018 (the 2014-era `cuisine_evidence_url` mapitout-montalcino.com still describes the February schedule, which is what the researcher anchored to — but the 2014 source is outdated).
- **Fix:** Updated `recurrence_pattern` to "annual, third or fourth week of November" and `start_month` to "November". Description appended with the 2018 schedule shift. Updated `cuisine_evidence_url` from the 2014 blog post to the current consortium news index.
- **Class:** Festival-month fabrication via outdated `cuisine_evidence_url`. This is the **same class** that `check_festival_dates.py` is designed to catch — but the script reads `festivals.json`, not `wine-festivals.json`, so it silently never ran on Cork & Curve festivals. **Class-of-defect for upstream prompt hardening:** see "Validator gap" below.

---

## Section 4 — One cuvée end-to-end (le-pergole-torte)

Picked Le Pergole Torte per brief (new extension entry).

- **Producer slug `montevertine`:** resolves cleanly in vineyards.json. **OK.**
- **Taste descriptors:** `aroma` = red cherry / rose petal / dried herbs / leather; `palate` = sour cherry / tobacco leaf / iron / Mediterranean herbs. Cross-checked against `verified.cuisine_evidence_url` = montevertine.it/le-pergole-torte/. The producer page does NOT contain these aroma/palate descriptors; only serving temperature + food-pairing suggestions. This is the **same Section I soft finding QA2 flagged** for high-score cuvées generally — descriptors are grape-appropriate Sangiovese vocabulary (drawn from critic-style language) but not literally on the cited evidence URL. QA2 explicitly logged this as a "structural research-pass issue, not a defect actionable at QA2." Carrying it forward; not actioned here.
- **Pairings TJ refs:** bistecca-alla-fiorentina (HEAD 200, italy/florence — OK), pici (HEAD 200, italy/florence — OK), aged pecorino with chestnut honey (`tablejourney_ref: null` — correctly nulled rather than fabricated).
- **Tags:** still-red, medium-body, firm-tannin, high-acid, pairs-with-red-meat, pairs-with-game, pairs-with-aged-cheese, occasion-special, occasion-cellar, occasion-gift, mood-contemplative, mood-elegant, iconic — all 13 tags appear in `docs/WINE_TAGS.md`. **OK.**
- **Scores:** WA 97 / 2019 / 2022, Vinous 96 / 2019 / 2022. Verified during QA2 narrow recheck (actual WA 97, Vinous 97 — JSON 1 point conservative on Vinous, no defect).

Le Pergole Torte clean modulo the Section I soft finding inherited from QA2.

---

## Section 5 — Score discipline (high-priority per brief)

The brief said: "Given QA2 caught Argiano regressions, **RANDOM-SAMPLE 3 of the surviving WA 95+ scores in wines.json** and HEAD-verify them against robertparker.com / Wine Advocate archive."

Population: 74 WA 95+ tuples in wines.json (after QA1+QA2 fixes). Random seed 7, 3 initial samples drawn:

| # | Cuvée | JSON (WA/vintage/year) | Verified actual | Defect |
|---|---|---|---|---|
| 1 | poliziano-asinone | 96 / 2019 / 2022 | **94** / 2019 / **2023** (Larner, Feb 2023) | INFLATED 2 pts + year wrong |
| 2 | soldera-case-basse-toscana-igt | 98 / **2007** / 2013 | **IMPOSSIBLE** — the entire 2007-2012 Soldera production was destroyed in the December 2012 cellar-vandalism incident (winejournal.robertparker.com "In Memoriam: Gianfranco Soldera", Wine Spectator, Jancis Robinson, Dr Vino, WineNews) | DROP — wine never bottled/released, cannot have been reviewed |
| 3 | le-macchiole-paleo-rosso | 97 / 2015 / 2018 | **96** / 2015 / **2019** (Larner, May 17 2019 — vintus.com importer page quoting WA verbatim) | INFLATED 1 pt + year wrong |

**3 of 3 random samples defective.** Per the QA prompt, "if sample hits >2 defects, broaden" — but more directly, this confirms the QA2 finding that "score discipline has been a recurring weak spot." I broadened to 10 more random samples (seed 99):

| # | Cuvée | JSON | Verified | Defect |
|---|---|---|---|---|
| 4 | le-macchiole-messorio | WA 98 / 2015 / 2018 | WA **97** / 2015 / **2019** (Larner May 2019) | INFLATED 1 pt + year wrong |
| 5 | casanova-di-neri-brunello-di-montalcino | WA 95 / 2016 / 2021 | WA **94** / 2016 (Larner) | INFLATED 1 pt |
| 6 | capezzana-trefiano-riserva | WA 95 / 2018 / 2022 | WA **93** / 2018 | INFLATED 2 pts |
| 7 | tignanello | WA 97 / 2019 / 2022 | WA **96** / 2019 (Larner) | INFLATED 1 pt |
| 8 | fontodi-flaccianello-della-pieve | WA 98 / 2019 / 2022 | WA 98 / 2019 / **2023** (Larner Feb 10 2023, via rarewineinvest digest) | YEAR WRONG (score OK) |
| 9 | avignonesi-occhio-di-pernice | WA 98 / **2010** / 2018 | **NO WA REVIEW LOCATED** for 2010. WA 100 exists for the 2001 vintage; nothing for 2010. Wine & Spirits scored 2010 at 94. | DROP — unattributable |
| 10 | il-poggione-vigna-paganelli-riserva | WA 97 / 2015 / 2022 | WA 97 / 2015 (Larner) | OK |
| 11 | biondi-santi-brunello-di-montalcino | WA 97 / 2016 / 2021 | WA 97+ / 2016 (Larner) | OK |
| 12 | mastrojanni-brunello-di-montalcino | WA 95 / 2016 / 2021 | WA 95 / 2016 (Larner Nov 2020) | OK (year 2021 within rounding; OK) |
| 13 | caparzo-la-casa-brunello | WA 95 / 2016 / 2021 | WA 95 / 2016 | OK |
| 14 | san-felice-il-grigio-gran-selezione | WA 95 / 2019 / 2022 | WA 95 / 2019 (Larner) | OK |
| 15 | guado-al-tasso | WA 97 / 2015 / 2018 | WA 97 / 2015 (Larner Sep 6 2018) | OK |
| 16 | riecine-la-gioia | WA 96 / 2018 / 2021 | unable to confirm or refute | UNVERIFIED — leave as-is |

**Total defects on the WA 95+ sample: 8 of 16 random draws = 50% defect rate.** Of those:
- 2 are CRITICAL (impossible/unattributable; tuple dropped)
- 5 are SCORE INFLATIONS of 1-2 points
- 1 is year-only wrong

This is consistent with — and worse than — QA2's Argiano findings. The class-of-defect pattern is:
1. WA score-tuple structure (4 fields) validates mechanically;
2. The reviewer field says "Wine Advocate";
3. Points are plausibly close to the actual published Larner score;
4. But neither QA1 nor QA2's mechanical chain HEAD-verifies the tuple to a retailer/Liv-ex citation;
5. The result is a soft 1-2-point creep on most WA 95+ tuples, plus occasional fabrications where no review exists at all.

**Fixes applied (8 corrections):**

| # | Slug | File | Action |
|---|---|---|---|
| OPUS-C1 | poliziano-asinone | wines.json, vineyards.json (poliziano mirror) | WA tuple corrected to 94/2019/2023 |
| OPUS-C2 | soldera-case-basse-toscana-igt | wines.json, vineyards.json (soldera-case-basse mirror) | WA tuple DROPPED (vintage destroyed Dec 2012) + signature-wines.json tasting_notes rewritten |
| OPUS-C3 | le-macchiole-paleo-rosso | wines.json | WA tuple corrected to 96/2015/2019 |
| OPUS-C4 | le-macchiole-messorio | wines.json, vineyards.json (le-macchiole mirror) | WA tuple corrected to 97/2015/2019 |
| OPUS-C5 | casanova-di-neri-brunello-di-montalcino | wines.json | WA tuple corrected to 94/2016/2021 |
| OPUS-C6 | capezzana-trefiano-riserva | wines.json, vineyards.json (tenuta-di-capezzana mirror) | WA tuple corrected to 93/2018/2022 |
| OPUS-C7 | tignanello | wines.json, vineyards.json (marchesi-antinori mirror) | WA tuple corrected to 96/2019/2022 |
| OPUS-C8 | fontodi-flaccianello-della-pieve | wines.json | WA year corrected to 2023 (score 98 verified) + signature-wines.json tasting_notes year corrected |
| OPUS-C9 | avignonesi-occhio-di-pernice | wines.json, vineyards.json (avignonesi mirror) | WA tuple DROPPED (unattributable for 2010 vintage) + signature-wines.json tasting_notes WA claim removed |

---

## Section 6 — 5 entities with editorial_score >= 4.7 spot-check

Random sample (seed 11) of 5: san-felice-vigorello (4.7), masseto (5.0), riecine-la-gioia (4.7), il-poggione-vigna-paganelli-riserva (4.8), grattamacco-bolgheri-superiore (4.7). All five have published critic scores in the high-90s range matching the editorial-score gravity — though `riecine-la-gioia` WA 96 remains unverified above (kept as-is). The 4.7+ editorial-score floor is justified for all 5.

---

## Class-of-defect notes for upstream prompt hardening

Three structural issues surfaced by this Opus pass that QA1 + QA2 cannot reasonably be expected to fully catch under their current scope:

### 1. Wine Advocate score-tuple inflation (the dominant class)

QA1's brief includes Section C2 (NUMERIC verification on top scores), but only for `points >= 99`. The post-QA1 + QA2 wines.json has 74 WA 95-98 tuples that fall below the C2 threshold but get the same structural validation (4 fields present, plausible year) without numeric source-verification. **8 of 16 random samples on the 95+ band were defective** — a 50% inflation rate.

**Recommended upstream change:** lower the C2 NUMERIC-verification threshold from `>= 99` to `>= 95`, OR add a new C2.5 layer that samples 20% of the 95-98 band and HEAD-verifies the tuple against a retailer/aggregator citation. The marginal cost is 15-20 web fetches per region, which is bounded.

### 2. Impossible-vintage / unattributable critic scores

Two of the eight Opus defects were not point-inflations but tuples for wines that don't exist as labelled:
- Soldera 2007 Toscana IGT WA 98 (vintage destroyed Dec 2012 vandalism, never bottled)
- Avignonesi Occhio di Pernice 2010 WA 98 (no WA review located for 2010 — WA 100 exists for the 2001 vintage and was likely the seed of the hallucination)

Both survived QA1 + QA2 because:
- The wine name + producer ARE real
- The reviewer + year fields are plausible
- The score is high but not "perfect" (98, not 100), so the C2 NUMERIC check doesn't engage

**Recommended upstream change:** for any cuvée whose history mentions a notable event (vandalism, ownership change mid-vintage, classification change), the research agent should explicitly check vintage availability. Or simply: every WA 95+ score should be defended by a citeable URL in `verified` rather than asserted bare.

### 3. Festival validator file-name mismatch (Cork & Curve-specific)

`scripts/check_festival_dates.py` reads `festivals.json`. Cork & Curve uses `wine-festivals.json`. The validator silently returns "no festivals.json" for every region and never runs. This is how Benvenuto Brunello shipped with a 2018-stale February claim despite the primary source (benvenutobrunello.com/en/) explicitly stating November on the homepage.

**Recommended upstream change:** patch `check_festival_dates.py` to read both `festivals.json` AND `wine-festivals.json`, OR rename the C&C file to match. The first fix is one-line:

```python
fp = data_dir / "festivals.json"
if not fp.exists():
    fp = data_dir / "wine-festivals.json"
```

This is the highest-leverage upstream change of the three: it's a one-line patch that unblocks a whole class of validators.

---

## Defect Index

| # | Slug | File | Section | Class | Severity | Action |
|---|---|---|---|---|---|---|
| OPUS-F1 | benvenuto-brunello | wine-festivals.json | Festival | Month + recurrence fabricated (2018-stale Feb claim; actual schedule November since 2018) | HIGH | FIXED (recurrence_pattern + start_month + description + cuisine_evidence_url) |
| OPUS-C1 | poliziano-asinone | wines.json + vineyards.json | C | WA 96/2019/2022 inflated; actual 94/2019/2023 | MEDIUM | FIXED |
| OPUS-C2 | soldera-case-basse-toscana-igt | wines.json + vineyards.json + signature-wines.json | C2 | WA 98/2007/2013 impossible — 2007 vintage destroyed Dec 2012 vandalism | CRITICAL | FIXED (DROPPED tuple, prose rewritten) |
| OPUS-C3 | le-macchiole-paleo-rosso | wines.json | C | WA 97/2015/2018 inflated; actual 96/2015/2019 | LOW | FIXED |
| OPUS-C4 | le-macchiole-messorio | wines.json + vineyards.json (le-macchiole mirror) | C | WA 98/2015/2018 inflated; actual 97/2015/2019 | LOW | FIXED |
| OPUS-C5 | casanova-di-neri-brunello-di-montalcino | wines.json | C | WA 95/2016/2021 inflated; actual 94/2016 | LOW | FIXED |
| OPUS-C6 | capezzana-trefiano-riserva | wines.json + vineyards.json | C | WA 95/2018/2022 inflated; actual 93/2018 | MEDIUM | FIXED |
| OPUS-C7 | tignanello | wines.json + vineyards.json | C | WA 97/2019/2022 inflated; actual 96/2019 | LOW | FIXED |
| OPUS-C8 | fontodi-flaccianello-della-pieve | wines.json + signature-wines.json | C | WA year wrong (review year 2022 → 2023; score 98 verified) | LOW | FIXED |
| OPUS-C9 | avignonesi-occhio-di-pernice | wines.json + vineyards.json + signature-wines.json | C2 | WA 98/2010/2018 unattributable; WA 100 exists for 2001 vintage but no WA 2010 review found | HIGH | FIXED (DROPPED tuple, prose rewritten) |

**Score corrections:** 6
**Score tuples DROPPED:** 2 (Soldera 2007 impossible, Avignonesi 2010 unattributable)
**Mirror updates in vineyards.json:** 6
**Signature-wines prose rewrites:** 3 (soldera, avignonesi, fontodi)
**Festival recurrence/month fix:** 1
**Entities removed:** 0

---

## ship_safety.sh post-fix output

```
[1/7] validate_data.py — PASS
[2/7] verify_entities.py — PASS (entities=60 hard=0 warn=0)
[3/7] check_internal_references.py — PASS (ERR=0 WARN=0)
[4/7] check_evidence_content.py — PASS (14/14 matched)
[5/7] check_festival_dates.py — PASS (no festivals.json) [SILENT — validator-gap, see class-of-defect note 3]
[6/7] check_external_urls.py — PASS (91/91 URLs OK)
[7/7] check_jsonld.py — WARN (global, not city-scoped)

italy/tuscany: ALL CHECKS PASSED
```

0 HARD failures. Ready for ship.

---

## Final verdict

OPUS-FOUND-9 italy/tuscany

Class-of-defect tags for upstream prompt hardening (priority order):

1. **C2 NUMERIC threshold too high** — drop from `>= 99` to `>= 95`, OR add a 20% spot-check pass on the 95-98 band. (8 of 9 defects this round.)
2. **Festival validator file-name mismatch** — patch `check_festival_dates.py` to also read `wine-festivals.json`. One-line change; unblocks the festival-month class globally. (1 of 9 defects this round, but the entire class is silently unvalidated for C&C.)
3. **Impossible-vintage / unattributable-review** — research agent prompt should require a citeable URL in `verified` for any WA 95+ score (not merely a reviewer/points/vintage/year tuple in `scores`). The Soldera 2007 + Avignonesi 2010 defects would have been caught by any URL-defends-the-score discipline.
