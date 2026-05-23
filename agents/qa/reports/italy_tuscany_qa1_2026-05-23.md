# QA1 Report: italy/tuscany — 2026-05-23

## Summary

- **Entities checked:** 43 vineyards, 135 wines, 12 signature-wines, 10 food-pairings, 4 itineraries, plus all other topic files (89 venues across 10 venue files, 107 editorial entities across 9 editorial files)
- **ship_safety.sh post-fix:** ALL 7 CHECKS PASS, 0 HARD failures
- **Critical defects fixed:** 12 (10 score-tuple inflations / inflated WS-WOTY-implies-100 myth, 1 fabricated milestone, 1 classification error)
- **Year-tuple corrections:** 2 (Sassicaia 1985 WA review year 1990 to 1992; Tua Rita Redigaffi 2000 WA review year 2003 to 2002)
- **Entities removed:** 0 (all defects fixable in place; one Vinous 99-pt score block deleted from soldera-case-basse-toscana-igt as unverifiable)
- **Foundation-gap recommendation:** see "Six-producer gap" section below

---

## Section A — Classification accuracy

Sampled 30 cuvées + 15 vineyards across the canonical Tuscan DOCGs and DOCs.

**Verified correct:**
- Tignanello, Solaia, Sassicaia signature reds: Toscana IGT (Tignanello, Solaia) / Bolgheri Sassicaia DOC (Sassicaia, the single-estate DOC since 1994) — OK
- Masseto: Toscana IGT (never DOC, never Bolgheri DOC) — OK
- Brunello di Montalcino DOCG, Rosso di Montalcino DOC — correctly distinguished across Biondi-Santi, Casanova di Neri, Il Poggione, Argiano, Banfi, Caparzo, Poggio Antico, Mastrojanni, Col d'Orcia, Castelgiocondo
- Soldera Case Basse: correctly listed as Toscana IGT (withdrew from Brunello DOCG in 2013) — OK
- Vino Nobile di Montepulciano DOCG (DOCG since 1980, correctly not DOC) across Avignonesi, Boscarelli, Salcheto, Poliziano — OK
- Chianti Classico DOCG correctly distinguished from Chianti DOCG (Castiglioni Chianti is the only Chianti DOCG; everything Classico-zone is DOCG Classico)
- Chianti Rufina DOCG, Carmignano DOCG, Morellino di Scansano DOCG, Vernaccia di San Gimignano DOCG — all confirmed against consortium sources
- Sant'Antimo DOC (Banfi Summus, Col d'Orcia Olmaia), Maremma Toscana DOC (Rocca di Frassinello) — confirmed
- Pomino DOC (Frescobaldi Castello Pomino) — confirmed

**DEFECT A1 — `tua-rita-perlato-del-bosco` misclassified as Suvereto DOCG (FIXED):**
- JSON had `"classification": "Suvereto DOCG"`.
- Per producer site (tuarita.it/en/perlato-del-bosco-rosso): "I.G.T. Toscana Sangiovese". Multiple importer listings (Winebow, Artisan, Wine.com 2019) confirm Toscana IGT. Suvereto DOCG exists but Tua Rita does not currently bottle Perlato del Bosco Rosso under it.
- **Fix:** Updated `classification` to `Toscana IGT`.
- **Class:** Classification promotion (IGT → DOCG), the canonical wine-vertical defect class.

**0 other classification defects in sample of 45.**

---

## Section B — Hectarage realism

Spot-checked 12 estates against producer About pages and consortium fact sheets.

| Estate | JSON (ha) | Cross-check | Assessment |
|---|---|---|---|
| Castello Banfi | 850 | 850 ha vines within 2,830-ha estate (banfi.it) | OK |
| Castelgiocondo | 235 | 235 ha vines within 815-ha estate (frescobaldi.com) | OK |
| Guado al Tasso | 320 | 320 ha vines within ~1000-ha estate (antinori.it) | OK |
| Castello di Nipozzano | 250 | 240-280 ha range per Frescobaldi | OK |
| Tenuta San Guido | 90 | 90 ha Sassicaia DOC | OK |
| Tenuta dell'Ornellaia | 115 | matches ornellaia.com | OK |
| Masseto | 7 | 7-ha blue-clay parcel | OK |
| Il Poggione | 125 | matches ilpoggione.it | OK |
| Argiano | 125 | matches argiano.net | OK |
| Soldera Case Basse | 8 | matches soldera.it | OK |
| Marchesi Antinori | 270 | see DEFECT B1 below | FLAG |
| Le Pupille | 80 | matches elisabettageppetti.com | OK |

**FLAG B1 — `marchesi-antinori` hectares=270 is interpretive, not a defect:**
- The `marchesi-antinori` vineyard entry represents the Chianti Classico Antinori footprint (Guado al Tasso is a separate producer slug per the description).
- Tenuta Tignanello alone: 165 ha vines within 319-ha estate (antinori.it).
- Pèppoli adds 55 ha (per antinori.it/en/tenuta/estates-antinori/peppoli-estate).
- Badia a Passignano adds ~50 ha (Antinori-managed estate within Chianti Classico).
- 165 + 55 + 50 = ~270 ha. The figure is plausible as the sum of Antinori's Chianti Classico vineyards but is not explicitly stated on any single producer page.
- **Action:** Left as-is. QA2 should consider explicitly listing component estates in the description, or replace with the Tenuta Tignanello figure (165 ha) for tighter sourcing.
- **Class:** Soft documentation gap, not a fabrication.

**0 other hectarage defects in sample.**

---

## Section C / C2 — Score citations (99+ NUMERIC verification)

Bordeaux pilot's hard lesson applied: every `points >= 99` tuple was source-verified against the publication archive, Wine-Searcher / Liv-ex digests, or a retailer page quoting the review verbatim.

**Initial 99+ count:** 13 in wines.json, 11 in vineyards.json (mirroring), 0 in signature-wines.json.

**Verified-correct (kept):**
| Entity | Tuple | Source |
|---|---|---|
| sassicaia | Wine Advocate 100 / 1985 / 1992 | Parker's first 100 for an Italian wine, published Wine Advocate 1992 (winejournal.robertparker.com/100-point-wines-from-italy) |
| masseto | Wine Advocate 100 / 2015 / 2018 | Larner, September 2018 (robertparker.com / Wines of Kings retailer) |
| tua-rita-redigaffi | Wine Advocate 100 / 2000 / 2002 | Parker 2002; **year corrected from 2003 to 2002** (rarewineinvest.com Tua Rita digest) |

**Defects fixed (score and/or year corrected; full table below):**

| # | Entity | Original tuple (defective) | Fixed tuple | Defect class |
|---|---|---|---|---|
| C1 | solaia | WS 100 / 1997 / 2000 | WS **98** / 1997 / 2000 | WS WOTY 2000 was Solaia 1997 but score was 98; James Suckling (then at WS) later gave 100 in a retrospective — the published-at-WOTY score was 98 (Wine Spectator archive; johnfodera.com Tuscan Vines essay; rare-wine-investing summaries) |
| C2 | argiano-brunello-di-montalcino | WS 100 / 2018 / 2023 | WS **95** / 2018 / 2023 | WS WOTY 2023 score was 95 (top100.winespectator.com/2023/wine/wine-no-1-argiano; wineindustryadvisor.com 2023-11-14) |
| C3 | casanova-di-neri-tenuta-nuova | WS 100 / **2010** / **2015** | WS 97 / **2001** / **2006** | Fully fabricated vintage+year; 2010 Tenuta Nuova actually received WS 95. Tenuta Nuova **2001** was WS WOTY 2006 with score 97 (winespectator.com/wine/wine-detail/id/200860) |
| C4 | casanova-di-neri-cerretalto | WA 99 / 2016 / 2021 | WA **98** / 2016 / 2021 | Larner WA review scored 98 (Wine Advocate archive; Vinfolio 2016 Brunello critic round-up) |
| C5 | ornellaia | WS 100 / 1998 / 2001 | WS **96** / 1998 / 2001 | WS WOTY 2001 was 1998 Ornellaia but score was 96 (winespectator.com/articles/1998-ornellaia-wine-of-the-year) |
| C6 | ornellaia | WA 99 / 2015 / 2018 | WA **98** / 2015 / 2018 | 2015 Ornellaia WA score was 98 (rarewineinvest.com 2024 Ornellaia digest; 99bottlz Ornellaia critic round-up) |
| C7 | masseto | WA **100** / **2001** / **2004** | WA **98** / 2001 / 2004 | 2001 Masseto WA score was 98 (cultwine 2001 Masseto archive lists ~96-98 critic range; rarewineinvest Masseto digest) — the 100 claim conflated with the verified 2015/2018 100 below |
| C8 | guado-al-tasso | WA 99 / 2015 / 2018 | WA **97** / 2015 / 2018 | 2015 Guado al Tasso WA score was 97 (rarewineinvest.com 2020 Guado al Tasso digest; 99bottlz Antinori critic round-up) |
| C9 | sassicaia | WS 100 / 1985 / **1988** | **DROPPED** | WS's first Wine of the Year (1988) was Château Lynch-Bages 1985, NOT Sassicaia (winespectator.com/articles/wines-of-the-year-1988-2018). Sassicaia 1985 received an original WS 99, the 100 came retroactively from James Suckling's 2008 vertical. Cleanest fix: drop the tuple entirely; the Wine Advocate 100 below carries the iconic-status signal. |
| C10 | sassicaia | WA 100 / 1985 / **1990** | WA 100 / 1985 / **1992** | Robert Parker's review of 1985 Sassicaia was 1992, not 1990 (winejournal.robertparker.com; ersanwein.com Parker biography) |
| C11 | tua-rita-redigaffi | WA 100 / 2000 / **2003** | WA 100 / 2000 / **2002** | Parker's published 100 for 2000 Redigaffi was 2002 (wineinvestment.com Tua Rita Academy; rarewineinvest 2023 Redigaffi digest) |
| C12 | soldera-case-basse-toscana-igt | Vinous 99 / 2010 / 2017 | **DROPPED** | Vinous 2010 Soldera review at 99 could not be corroborated; verified scores at 96-98 from Galloni for adjacent vintages (1990-2014). Cleaner to drop than fabricate. Remaining WA 98/2007/2013 tuple kept (verified). |

**Mirror updates applied to `vineyards.json`** for soldera-case-basse, casanova-di-neri, argiano, tenuta-san-guido, tenuta-dell-ornellaia, masseto, tenuta-guado-al-tasso, tua-rita.

**Mirror updates applied to `signature-wines.json` `tasting_notes` and `description` prose** for sassicaia, tignanello, solaia, ornellaia, masseto, soldera-case-basse-toscana-igt, casanova-di-neri-cerretalto, argiano-brunello-di-montalcino, tua-rita-redigaffi — every prose claim like "Wine Spectator 100 points" was either corrected to the actual score or rewritten around the verified-correct review.

**DEFECT C13 — Fabricated milestone in sassicaia.history.milestones (FIXED):**
- `wines.json` sassicaia entry had milestone `{ "year": 1988, "event": "Wine Spectator names 1985 Sassicaia its Wine of the Year" }`.
- This is a hard fabrication: WS's first Wine of the Year (1988 list inaugural) was Château Lynch-Bages 1985, not Sassicaia. Confirmed against winespectator.com/articles/wines-of-the-year-1988-2018.
- The summary prose for the entry also stated "Sassicaia became its 1988 Wine of the Year" — also corrected.
- **Fix:** Replaced milestone and prose with the verified Parker 100/1992 milestone — the truly historic moment for this wine.
- **Class:** Fabricated industry-recognition claim. Hard defect.

---

## Section F — Independent-directory address cross-check

Sampled 12 venues across tasting-rooms, wine-bars, wine-restaurants, wine-retailers, wine-schools, wine-tours, wine-museums, wine-hotels, wine-experiences. Cross-checked against the venue's own site, Tripadvisor, Yelp, the relevant consortium directory, or the Michelin Guide.

| Venue | Address claimed | Cross-check | Result |
|---|---|---|---|
| Officina della Bistecca (Dario Cecchini) | Via XX Luglio 11, Panzano in Chianti | dariocecchini.com confirms | OK |
| Enoteca Italiana Siena | Fortezza Medicea, Siena | Reopened July 2025 after 7-year closure; correct address (gamberorosso.it; enotecaitalianasiena.it 2026) | OK |
| L'Andana | Localita Badiola, Castiglione della Pescaia | andana.it confirms (Tenuta La Badiola) | OK |
| Castello di Casole (Belmond) | Localita Querceto, Casole d'Elsa | belmond.com confirms | OK |
| Locale Firenze | Via delle Seggiole 12, Firenze | localefirenze.it confirms (World's 50 Best Bars #22 in 2025) | OK |
| La Sala dei Grappoli (Castello Banfi) | Castello di Poggio alle Mura 1, Montalcino | banfi.it/eng/restaurants confirms; Michelin one-star | OK |
| Apicius Florence wine school | Via Guelfa 85, Firenze | apicius.it/florenceculinaryinstitute confirms | OK |
| Vernaccia experience wine school | Villa della Rocca di Montestaffoli, San Gimignano | vernacciasangimignano.it confirms (consortium HQ) | OK |
| Frescobaldi CastelGiocondo tasting | Localita Castelgiocondo, Montalcino | frescobaldi.com confirms | OK |
| Enoteca di Piazza Wine Shop Montalcino | Via Matteotti 35, Montalcino | enotecadipiazza.com confirms | OK |
| Casa del Vino Siena | Via di Citta 14, Siena | casadelvinosiena.it confirms | OK |
| Museo del Vino Vernaccia San Gimignano | Villa della Rocca di Montestaffoli | vernacciasangimignano.it confirms (co-located with the consortium) | OK |

**0 address fabrications detected in sample of 12.** Section F clean.

---

## Section L — Cuvée → producer cross-reference

Mechanically verified all 135 cuvées' `producer` slugs against vineyards.json:
- **Result: 100% resolve (135/135). 0 dangling producer slugs.**
- B's research note that all cuvée producer slugs cleanly resolve in A's vineyards is confirmed.

Mechanically verified all 12 signature-wines slugs against wines.json:
- **Result: 100% resolve (12/12). 0 dangling signature-wine refs.**

Mechanically verified all 10 food-pairing `wine_entities` arrays against wines.json:
- **Result: 100% resolve (29/29 individual refs across the 10 pairings).**

Mechanically verified all itinerary `days[*].venues[*]` against the union of vineyards + venue topics + hidden-gems:
- **Result: 100% resolve.** (Includes `massa-vecchia` which is in hidden-gems.json + dietary.json — correctly cross-referenced from the Bolgheri/Maremma four-day itinerary.)

Section L is clean.

---

## Section J — Tag vocabulary conformance

Scanned all 135 cuvées' `tags[]` arrays.

- **0 unknown tags** (every emitted tag appears in `/station/repo/docs/WINE_TAGS.md`).
- **0 derived-axis tags** emitted by researcher (no `price-*`, no `cellar-worthy` / `drink-young`, no `biodynamic` / `organic` / `vegan`, no grape-axis tags, no `old-world` / `new-world`).
- Researcher correctly emits only `style` / `body` / `tannin` / `acidity` / `pairing` / `occasion` / `mood` / `editorial` axes.

Section J is clean.

---

## Section K — Vintage-agnostic discipline

- **0 cuvée slugs containing a 4-digit year.**
- **0 cuvée names containing a 4-digit year.**

All 135 cuvée slugs are vintage-agnostic (`tignanello`, `sassicaia`, `flaccianello-della-pieve`, etc.). Section K is clean.

---

## Six-producer foundation gap — RECOMMENDATION

Agent B reported 6 iconic producers were briefed but missing from A's vineyards.json. Assessment:

| Producer | Significance | Verdict |
|---|---|---|
| Castello di Fonterutoli (Mazzei) | Major Chianti Classico estate; Siepi flagship | NOTABLE GAP |
| Castello di Brolio (Ricasoli) | 1872 Chianti formula creator — historic anchor | CRITICAL GAP |
| Montevertine (Sergio Manetti family) | Le Pergole Torte = canonical Sangiovese-only IGT | CRITICAL GAP |
| Cesani (Vernaccia di San Gimignano) | Top Vernaccia producer | NOTABLE GAP |
| Petrolo (Bazzocchi family) | Galatrona = top Bolgheri-adjacent Merlot | NOTABLE GAP |
| Poggio di Sotto (ColleMassari Group) | Top-tier Brunello | CRITICAL GAP |

**Recommendation: extend-foundation.** Three of the six (Brolio, Montevertine, Poggio di Sotto) are not optional for a Tier-1 Tuscany atlas — Brolio is the historic source of the Chianti recipe, Montevertine defined the IGT-by-choice Sangiovese movement, and Poggio di Sotto is in nearly every modern Brunello critical top-five. The other three (Fonterutoli, Cesani, Petrolo) are notable but not catastrophic to omit.

At 43 producers, foundation is healthy but it is missing region-defining estates. Orchestrator should dispatch a foundation-extension run targeting at minimum the three CRITICAL slugs (and ideally all six) before final ship. If that run lands cleanly, Agent B can also extend `wines.json` with the corresponding cuvées (Siepi, Brolio, Casalferro, Le Pergole Torte, Pian del Ciampolo, Cesani Vernaccia Riserva, Galatrona, Boggina, Poggio di Sotto Brunello + Riserva).

This is the kind of gap QA2 cannot reasonably backfill — needs the research-agent treatment.

---

## Voice / prose defects (Section H spot-check)

- **0 em-dashes / en-dashes** across wines.json, vineyards.json, signature-wines.json (existing ship_safety enforcement)
- **0 AI-tells** ("nestled in", "vibrant atmosphere", "culinary journey", "carefully crafted", "must-visit", "to die for") in sampled prose
- **editorial_score coefficient of variation:** wines.json CV = 0.0578 (healthy), vineyards.json CV = 0.0479 (at the threshold but not suspicious for a curated 43-estate set, all of which are intentionally Tuscany's gravity centres)

---

## Defect Index

| # | Slug | File | Class | Severity | Action |
|---|---|---|---|---|---|
| A1 | `tua-rita-perlato-del-bosco` | wines.json | A — IGT promoted to DOCG (Suvereto DOCG → Toscana IGT) | HIGH | FIXED |
| C1 | `solaia` | wines.json | C2 — WS 100 inflated from real 98 (WOTY 2000) | HIGH | FIXED |
| C2 | `argiano-brunello-di-montalcino` | wines.json, vineyards.json | C2 — WS 100 inflated from real 95 (WOTY 2023) | HIGH | FIXED |
| C3 | `casanova-di-neri-tenuta-nuova` | wines.json, vineyards.json | C2 — vintage+year fabricated (2010/2015 → 2001/2006); score 100 → 97 | CRITICAL | FIXED |
| C4 | `casanova-di-neri-cerretalto` | wines.json, vineyards.json | C2 — WA 99 corrected to 98 (Larner) | MEDIUM | FIXED |
| C5 | `ornellaia` | wines.json, vineyards.json | C2 — WS 100 inflated from real 96 (WOTY 2001) | HIGH | FIXED |
| C6 | `ornellaia` | wines.json, vineyards.json | C2 — WA 99 corrected to 98 | MEDIUM | FIXED |
| C7 | `masseto` | wines.json, vineyards.json | C2 — 2001 vintage WA 100 inflated from real 98 | HIGH | FIXED |
| C8 | `guado-al-tasso` | wines.json, vineyards.json | C2 — WA 99 corrected to 97 | MEDIUM | FIXED |
| C9 | `sassicaia` | wines.json, vineyards.json | C2 — WS 100/1985/1988 fabricated (1988 WOTY was Lynch-Bages); DROPPED | CRITICAL | FIXED |
| C10 | `sassicaia` | wines.json, vineyards.json | C2 — WA year 1990 corrected to 1992 | MEDIUM | FIXED |
| C11 | `tua-rita-redigaffi` | wines.json, vineyards.json | C2 — WA year 2003 corrected to 2002 | LOW | FIXED |
| C12 | `soldera-case-basse-toscana-igt` | wines.json, vineyards.json | C2 — Vinous 99 unverifiable; DROPPED | MEDIUM | FIXED |
| C13 | `sassicaia` | wines.json | C2 — Fabricated milestone "Wine Spectator names 1985 Sassicaia its Wine of the Year" (1988) | CRITICAL | FIXED |
| Inf1 | `marchesi-antinori` | vineyards.json | B — hectares=270 plausible but interpretive | FLAG | Left as-is; QA2 may tighten |
| GAP1 | 6 producers missing | vineyards.json | Foundation gap (Brolio, Montevertine, Poggio di Sotto critical; Fonterutoli, Cesani, Petrolo notable) | RECOMMEND | Orchestrator extension run |
| Url1 | `poliziano` | vineyards.json | Booking URL www.carlettipoliziano.com timed out | LOW | FIXED (www stripped to carlettipoliziano.com) |
| Inf2 | Podere Le Boncie | dietary.json, hidden-gems.json | naturalwineco.com source_url timeout | WARN | Soft-infrastructure flag; QA2 can replace if it stays dead |

**Entities removed:** 0. All defects fixable in place; only 2 inflated score blocks were dropped.

**Files modified:**
- `site-data/italy/tuscany/data/wines.json` (10 score-tuple corrections + 1 milestone fix + 1 classification fix + 1 prose summary fix)
- `site-data/italy/tuscany/data/vineyards.json` (8 mirror score-tuple corrections + booking_url normalisation)
- `site-data/italy/tuscany/data/signature-wines.json` (9 tasting_notes and 2 description prose rewrites)

---

## ship_safety.sh post-fix output

```
[1/7] validate_data.py — PASS
[2/7] verify_entities.py — PASS (0 HARD, 2 WARN soft-infrastructure)
[3/7] check_internal_references.py — PASS (ERR=0 WARN=0)
[4/7] check_evidence_content.py — PASS (14/14 matched)
[5/7] check_festival_dates.py — PASS (no festivals.json)
[6/7] check_external_urls.py — PASS (85/85 URLs OK)
[7/7] check_jsonld.py — WARN (global, not city-scoped)

italy/tuscany: ALL CHECKS PASSED
```

0 HARD failures. Ready for QA2 dispatch.
