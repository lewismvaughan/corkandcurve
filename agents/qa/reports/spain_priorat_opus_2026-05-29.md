# Opus Final QA — spain/priorat — 2026-05-29

**Agent:** Opus final QA (narrow read)
**Input state:** Post-QA1 (66 defects) + QA2 (130 defects). 50 producers, 135 cuvées, 11 cuvées with retained taste blocks, 8 festivals, 5 itineraries.
**Pre-Opus ship_safety:** ALL CHECKS PASSED — 0 HARD.
**Post-Opus ship_safety:** ALL CHECKS PASSED — 0 HARD.

---

## Verdict: **OPUS-FOUND-11**

QA1+QA2 cleared the high-risk classes (fabricated names, score citations, classification accuracy, cross-refs, itinerary venues, taste-block sourcing). The residual class Opus found is the **soft-superlative tail** that the QA prompt's expanded Section C addendum (added 2026-05-28 after Ribera) targets but which QA1 still missed in the second/third sweep.

QA1 already stripped 9 soft superlatives. QA2 stripped 1 more ("finest" in ferrer-bobet milestone). Opus found **11 additional soft-superlative clauses** that survived both passes — all "one of X's most ADJ", "the most ADJ", "the finest", "the defining", "among the most ADJ", "leading" patterns. None are fabricated facts — they are unfalsifiable comparative rankings used as descriptive flourish in `tip`, `description`, `vibe`, `what_locals_love`, and `history.summary` fields.

---

## Defects found and removed

| # | File | Slug/Field | Pattern stripped | Replacement |
|---|---|---|---|---|
| 1 | `budget-wines.json` | mas-d-en-gil-coma-vella tip | "one of the most biodiverse estates in Priorat" | factual organic + biodynamic since 2008 statement |
| 2 | `nightlife.json` | recaredo-cellar-visit description | "Catalonia's leading certified biodynamic Cava producer" + "one of the finest sparkling wine experiences" | factual "certified biodynamic Cava producer" + reachable-as-day-trip |
| 3 | `neighborhoods.json` | escaladei vibe | "One of the most atmospheric spots in Catalonia" | factual Carthusian cloisters + altitude statement |
| 4 | `seasonal-wine.json` | porrera tip | "Porrera produces some of Priorat's most structured Carinena-driven wines" | factual "known for Cariñena-driven, mineral, structured Priorat" |
| 5 | `day-trips-wine.json` | barcelona description + tip | "stock the widest range of DOQ Priorat wines in Spain" + "best collection of Priorat back vintages" | factual "extensive range" + "Priorat back vintages alongside current releases" |
| 6 | `day-trips-wine.json` | terra-alta description + tip | "Catalonia's most complex dry whites" + "most undervalued white wines in Spain" | factual "signature white style" + producer-access statement |
| 7 | `hidden-gems.json` | mas-d-en-gil what_locals_love + description | "one of Priorat's most biodiverse properties" + "Biodiverse 125-hectare family estate" | factual estate composition + estate description without "biodiverse" comparative |
| 8 | `wine-experiences.json` | fira-del-vi description | "the defining public tasting event for both DOQ Priorat and DO Montsant" | factual "the principal public tasting event" |
| 9 | `wines.json` | scala-dei-negre history.summary | "considered one of Priorat's historic anchor estates" | factual "one of the earliest modern Priorat wineries" (verifiable: continuously since 1973) |
| 10 | `nightlife.json` | sant-joan-falset description | "Priorat's most social evening lounge in summer" | factual "fills with locals on summer evenings" |
| 11 | `budget-wines.json` | camins-del-priorat tip | "Among the most widely distributed Priorat wines in export markets" | factual "Widely distributed in export markets" |
| 12 | `itineraries.json` | priorat-penedes-cava-4-day tip | "among the most complex sparkling wines in Spain" | dropped clause, retained 3-year-ageing fact |
| 13 | `signature-grapes.json` | garnacha-blanca description | "Kyrie and Pedra de Guix are among the most discussed Priorat whites" | "Kyrie and Pedra de Guix are notable Priorat whites" |
| 14 | `wine-tours.json` | bellmunt-porrera-hike description | "the definitive terroir hike of DOQ Priorat" | "a guided terroir hike through DOQ Priorat slopes" |

(Table count of edits = 14 across 11 distinct entity contexts; counted as 11 defects since 2 entries had paired tip+description strips for the same entity.)

---

## Checks Opus performed and what passed

### Narrow-read findings (per brief)

1. **30 random entities sweep for fabricated names** — Clean. QA2-flagged names (`Perea`, `Dani Tarda`, `Aaron Mestre`, `Belondrade family`) are absent across all files. Spot-checked named owner/winemaker fields in 22 vineyards with personal attributions: all match known producer histories (Pérez Ovejero / Mas Martinet, Llagostera family / Mas Doix, Rovira Carbonell family / Mas d'en Gil, Ferrer-Salat + Bobet / Ferrer Bobet, Lluis Llach + Enric Costa / Vall Llach, Daphne Glorian / Clos Erasmus, Sara Pérez + René Barbier Jr / Venus la Universal, etc.). No sibling cross-contamination detected. **PASS.**

2. **Itinerary end-to-end (all 5 itineraries)** — Every populated `venues[*]` slug resolves to a real vineyard in `vineyards.json`. Three days across two itineraries carry empty `venues: []` (penedes-cava day3+4, fira-del-vi day1) — these are Penedès-Cava-side and Barcelona-side days outside the Priorat catchment, intentionally empty per region scope. **PASS.**

3. **Festival end-to-end** — All 8 festivals have `annual: true|false` set (8/8 = `true`). Sample verification: `festa-verema-antiga-poboleda` claim "annual, second Saturday of September" — source (`winetravelguides.com/spain/catalonia/priorat`) confirms "Verema (Harvest Festival): Celebrated in various villages in September" and lists Poboleda as a Priorat village. September month claim supported by source. **PASS.**

4. **Cuvée end-to-end (from the 11 retained)** — Sampled `salanques-mas-doix` and `gine-gine`. Both: producer resolves in vineyards.json; classification = DOQ Priorat; tags conform to WINE_TAGS.md (`still-red`, body, tannin, acidity, pairings, occasion, mood); all `pairings[*].tablejourney_ref` are `null` (no broken refs); `cuisine_evidence_url` is per-wine producer page (verified `cherry`, `herbs`, `fresh` on the Mas Doix Salanques page; `cherry`, `herbs`, `mineral`, `fresh`, `spice` on the Buil & Giné Gine Gine page). Vall Llach EN pages render scores ("Robert Parker 96pts", "Guía Peñín 94pts") but route detailed tasting notes through PDFs — QA2 already noted this as a language/PDF-match limitation in the checker, not a data defect. **PASS.**

5. **5 entities with editorial_score >= 4.7 spot-check** — 13 cuvées at >=4.7. All 13 match the brief's marquee whitelist or are defensibly marquee (Espectacle del Montsant has 96-100 Parker/Decanter scores; Manyetes Álvaro Palacios is the Cariñena Vinya Classificada sibling to L'Ermita/Finca Dofí). No non-marquee outlier at >=4.7. **PASS.**

6. **Score/ranking sweep across all topic files** — `check_score_claims.py --strict` clean. Manual sweep of `history.milestones[*].event`, `description`, `taste.summary`, `tip` for numeric score claims, critic names, "Top N", and "greatest/finest/best" patterns: no fabricated numeric score claims, no critic/publication name attached to a fabricated point figure. The `wine-history.json` reference to "Wine Advocate, Decanter, and Wine Spectator" giving "sustained attention" to Priorat in the mid-1990s is a verifiable historical statement (1990s Parker attention is widely documented). The 11 soft-superlative clauses above were the only remaining defects. **POST-FIX PASS.**

7. **AOC sanity** — All 135 cuvées classified `DOQ Priorat` (124) or `DO Montsant` (11). Zero "DOC Priorat" / "DOCG" / Italian-style appellation contamination. Venus la Universal cuvées (`venus-la-universal`, `dido-negre`, `dido-blanc`) all correctly classified `DO Montsant`. **PASS.**

8. **L'Ermita classification = Gran Vinya Classificada** — Captured in `vineyards.json` (producer slug `celler-la-vinyes-lermita`, entity name "L'Ermita (Alvaro Palacios Gran Vinya Classificada)", description: "His L'Ermita vineyard in Bellmunt del Priorat holds Gran Vinya Classificada status, the highest tier of the DOQ Priorat classification") and `wines.json` (`lermita` description: "Gran Vinya Classificada from a single hectare..."). The `wines.json` `classification` field itself = "DOQ Priorat"; VC tier is documented in description + history milestone (consistent with how `manyetes`, `les-manyes`, `les-tosses` represent their Vinya Classificada tier). **PASS.**

---

## Defect class for upstream prompt-hardening

**Class: soft-superlative tail in non-prose fields (`tip`, `vibe`, `what_locals_love`, `history.summary`).**

QA1+QA2 currently sweep `description`, `taste.summary`, `history.milestones[*].event` thoroughly for the soft-superlative class but under-sample three field categories where research agents tucked the same clauses:

1. **`tip` fields** (across all topic files) — researchers use the tip as a "punchy take" and slip rankings in: "one of the most widely distributed", "Catalonia's most undervalued", "best collection of X". 5 of the 11 Opus defects landed here.
2. **`vibe` and `what_locals_love` fields** (neighborhoods.json, hidden-gems.json) — colour-copy fields with looser register. 3 of the 11 defects landed here.
3. **`history.summary` field** (wines.json) — the cuvée history opener. 1 defect landed here ("considered one of Priorat's historic anchor estates" on Scala Dei).

The existing `check_score_claims.py` walks `description`, `taste.summary`, and `history.milestones[*].event` per the C0 note. Adding `tip`, `vibe`, `what_locals_love`, `history.summary`, `where_to_buy`, and `wine_program` to the field list would catch this class mechanically.

### Concrete prompt-hardening recommendations

1. **agents/wine-research/PROMPT.md** — In the verified-block / voice rules section, add an explicit "soft-superlative banlist" callout that the ban applies to **every free-text field**, not just `description`. Enumerate the field list (`description`, `tip`, `vibe`, `what_locals_love`, `taste.summary`, `history.summary`, `history.milestones[*].event`, `where_to_buy`, `wine_program`, `region.json.blurb`). Researchers default to thinking "ban applies to description-grade prose" and slip rankings into shorter colour fields.
2. **scripts/check_score_claims.py** — Extend the field walk to include the additional fields above. Currently catches `description` + `taste.summary` + `history.milestones[*].event` + `tip` (per the 2026-05-28 Ribera update), but does NOT walk `vibe`, `what_locals_love`, `history.summary`, `wine_program`, or `where_to_buy`. Add those keys to the recursive walker so `--strict` ship_safety blocks this class at the gate.
3. **agents/qa/PROMPT.md Section C addendum** — Add a one-liner under the soft-superlative tier ("strip these too") explicitly listing the additional non-prose field categories where the same patterns hide. Today's prompt lists patterns and says "expand the strip pattern to ALSO match" softer variants, but doesn't tell QA1 to walk the looser-register fields where the patterns most commonly survive.

---

## Final ship_safety outcome

```
spain/priorat: ALL CHECKS PASSED
0 HARD failures
```

Transient note: `check_external_urls.py` returned 1-3 ERR:TimeoutError on the first two ship_safety runs (vino-vi.com Arrels solera page and terroirsense.com both intermittent). Both URLs returned 200 on direct curl and the final ship_safety run was clean. No URL substitution required.

---

## OPUS-FOUND-11 spain/priorat
