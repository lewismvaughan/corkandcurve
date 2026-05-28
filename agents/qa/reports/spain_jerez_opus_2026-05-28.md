# Opus Final QA Report — spain/jerez

**Date:** 2026-05-28
**Agent:** Opus final QA
**Predecessors:** QA1 (43 defects), QA2 (104 defects), ship_safety 0 HARD before Opus
**Final state:** ship_safety ALL CHECKS PASSED, 0 HARD failures

---

## Verdict

**OPUS-FOUND-14**

QA1+QA2 closed the structural defect classes cleanly (slug merges, taste-block shared-URL strip, dietary HARD evidence, cross-contamination scrubs) but a single defect class survived in the support-topic prose: **soft-superlative/categorical-ranking adjectives** in non-wine free-text fields. The ranking ban applies categorically (per the C0/Rhône/Ribera amendments to the QA playbook); it has historically been enforced against `wines.json` + `vineyards.json` + `signature-wines.json` but enforcement on support topics (`wine-festivals`, `wine-bars`, `wine-history`, `signature-grapes`, `neighborhoods`, `budget-wines`, `day-trips-wine`, `region.json`, `distilleries`) has been spotty. This region demonstrated that the same prose patterns will recur across every support file unless QA1 sweeps them all.

All wines.json + vineyards.json fields verified clean of ranking patterns (the wine-vertical-critical files were correctly disciplined). All 41 wines with `editorial_score >= 4.7` are recognizable marquee Sherry releases (matched against the brief's enumerated list). All festival `verified.source_url` values HEAD-resolved 200. All festivals have `annual: true|false` set (no nulls). All 5 itineraries' days[*].venues[*] slugs resolve in vineyards.json. The 3 dropped slugs (sanchez-ayala-la-gitana, gutierrez-colosia-premium, el-cortijo-de-los-saints) are confirmed absent from all data files. All 12 signature_wines slugs resolve in wines.json. All 155 wines[*].producer slugs resolve in vineyards.json. Tag vocabulary clean (0 unknown, 0 derived in researcher emissions). All non-null `tablejourney_ref` confirmed under `spain/seville` (QA2 verified, no change). All `style: fortified-sherry` correct for sherry cuvées.

---

## Defects found and removed (14 prose violations)

### Class: categorical ranking / soft-superlative in support-topic prose

These patterns are categorically banned per the QA playbook strip-list (greatest, finest, most prestigious, most celebrated, most storied, world's most, in the world, the defining, benchmark, one of the great, the most recognised). All 14 were in support-topic free-text fields, not in wines.json / vineyards.json (which were clean).

| # | File | Entity | Pattern | Action |
|---|------|--------|---------|--------|
| 1 | wine-festivals.json | festival-de-jerez-flamenco | "one of the world's most prestigious flamenco events" + "global capital of flamenco" | Rewrote to factual: "an international flamenco festival held annually in late February and early March" + "draws flamenco scholars and performers from across Europe and Latin America" |
| 2 | wine-bars.json | tabanco-el-pasaje-jerez | "One of Jerez's most storied tabancos" | "A long-running Jerez tabanco" |
| 3 | wine-bars.json | casa-balbino-sanlucar | "among the most celebrated tapas bars" | "a long-established tapas bar" |
| 4 | wine-history.json | first-do-spain-1933 | "one of the earliest appellations of origin in the world" | "an early statutory wine appellation in Europe" |
| 5 | wine-history.json | vos-vors-carbon-dating-certification | "one of the few wine categories in the world" | "one of the few wine categories" |
| 6 | wine-history.json | pedro-ximenez-sweet-sherry-tradition | "one of the world's most intense dessert wines" | "among the most concentrated dessert-wine styles produced commercially" |
| 7 | wine-history.json | albariza-terroir-contemporary | "among the world's most distinctive viticultural terroirs" | "recognized by the Consejo Regulador and a body of viticultural research as a distinctive Andalusian terroir" |
| 8 | signature-grapes.json | pedro-ximenez | "form one of the world's great dessert wine categories" + "one of Andalusia's defining food moments" | Replaced with factual production description and "a traditional Andalusian dessert pairing" |
| 9 | signature-grapes.json | palomino-fino-albariza | "the defining terroir factor" | "the principal terroir factor" |
| 10 | neighborhoods.json | jerez-de-la-frontera | "Home to the greatest concentration of major bodegas" | "Home to the densest cluster of major bodegas" |
| 11 | neighborhoods.json | anina | "a benchmark albariza terroir" | "a classic albariza terroir" |
| 12 | neighborhoods.json | miraflores | "some of Sanlúcar's finest Manzanilla Pasada" | "a noted source for Sanlúcar Manzanilla Pasada" |
| 13 | budget-wines.json | la-gitana-manzanilla-hidalgo | "The most recognised Manzanilla in the world" + "benchmark Manzanilla" | "Among the most widely distributed Manzanillas internationally" + "A classic entry-point Manzanilla" |
| 14 | day-trips-wine.json | cadiz-atlantic-city | "the world's oldest inhabited city in the western world" + "the finest spot to drink fino" + "one of the great pleasures" | Replaced all three with factual phrasing |
| 14a | region.json | destination.blurb | "the world's most complex fortified wine category" | "the fortified-wine category that spans biologically aged Fino and Manzanilla through oxidative Amontillado, Oloroso and Palo Cortado" |
| 14b | region.json | seo.pages.signature-wines.description | "The defining sherries of Jerez" | "Iconic sherries of Jerez" (then padded to satisfy 140-165 char SEO cap by adding "Bodegas Tradición VORS") |
| 14c | distilleries.json | sanchez-romate-cardenal-mendoza | "one of the most recognised Brandy de Jerez Solera Gran Reserva labels" | "a long-established Brandy de Jerez Solera Gran Reserva label widely distributed in Spain and export markets" |

(Counted as 14 by primary defect; sub-entries 14a/14b/14c are same-class second sweeps within the same support-topic decay.)

---

## Verified clean (no defects found)

### Itinerary end-to-end (sherry-triangle-3-day)

- day 1: gonzalez-byass, bodegas-tradicion — both resolve
- day 2: osborne — resolves
- day 3: bodegas-barbadillo, bodegas-hidalgo-la-gitana, bodegas-argueso — all resolve
- All 5 itineraries' venues populated and resolving. No orphan references to the 3 dropped slugs.

### Festival end-to-end (festival-de-jerez-flamenco + others)

- All 8 festivals have `annual` set (7 true, 1 false for copa-jerez-forum which is biennial-style)
- All 8 `verified.source_url` HEAD-resolved 200 (festivaldejerez.es, sherry.wine, barbadillo.com, osborne.es)
- start_month + recurrence_pattern consistent per claim (Vendimia September, Feria del Caballo May, Festival de Jerez February, Caballos August, Pisada September, Encuentro September, Sherry Day November)

### Cuvée end-to-end (lustau-palo-cortado-peninsula, editorial_score 4.7)

- producer `emilio-lustau` resolves in vineyards.json
- style `fortified-sherry` (correct per WINE_TAGS.md)
- All 11 tags conform to WINE_TAGS.md (style/body/tannin/acid/pairing/occasion/mood)
- `verified.cuisine_evidence_url` is producer per-wine page (`lustau.es/en/product/peninsula-palo-cortado/`)
- Taste descriptors specific and varied (orange bitters, mahogany, roasted hazelnuts vs. boilerplate)
- All 3 pairings have `tablejourney_ref: null` (correct — no fabricated TJ paths)

### Editorial-score >= 4.7 backing credentials (41 wines)

All match the brief's defensible-marquee enumeration:
- González Byass: Tio Pepe Fino, Tio Pepe En Rama, Matusalem VORS, Noé VORS, Apóstoles VORS
- Lustau: Emperatriz Eugenia VORS, Almacenista Amontillado del Castillo, Palo Cortado Península
- Valdespino: Inocente Fino (Macharnudo single-vineyard), Tío Diego Amontillado, Don Gonzalo VOS
- Bodegas Tradición: Amontillado VORS, Oloroso VORS, Palo Cortado VORS, Pedro Ximénez VOS
- Equipo Navazos: La Bota Fino, Manzanilla, Amontillado, Palo Cortado, Oloroso, Pedro Ximénez (all single-cask)
- Sanchez Romate: NPU Amontillado VORS
- Williams & Humbert: Jalifa VORS Amontillado
- Hidalgo La Panesa Especial Fino, Maestro Sierra (Fino/Amontillado/Oloroso), Fernando de Castilla Antique series, Sibarita VORS Oloroso, Diez Merito Imperial VORS, Barbadillo Solear En Rama, Versos 1891, Reliquia Amontillado (5.0), Hidalgo Pastrana Pasada + Faraón Oloroso, Delgado Zuleta Quo Vadis VORS, Argüeso Reserva de Familia, Osborne AOS VORS — all genuine marquee sherries

No non-marquee at >= 4.7. Score-bunching coefficient of variation is healthy (4.1 to 5.0 range).

### Ownership currency

Verified clean per QA1+QA2. Spot-confirmed:
- Hidalgo La Gitana (Bodegas Hidalgo La Gitana) distinct from Vinicola Hidalgo (different families); descriptions correctly state this
- Caballero/Lustau ownership chain not contradicted
- Sogrape-Sandeman correctly attributed
- Grupo Estévez umbrella for Real Tesoro/Valdespino correctly attributed
- González Byass family ownership preserved without naming current generation (correct abstention)

### Section C0 score-prose scan

`check_score_claims.py` clean. No critic-name + score-figure patterns in any free-text field (wines.json, vineyards.json, signature-wines.json, dietary.json `history.milestones[*].event`, `description`, `taste.summary`, `tip`). One Tim Atkin MW reference in wine-history.json #16 is a journalistic-coverage citation (no score claim).

### Section J tag conformance (155 wines)

0 unknown tags, 0 derived-axis tags emitted by researcher. All 155 wines correctly carry `fortified-sherry` style tag. Curated `cult-wine` editorial-tag usage matches the controlled vocabulary.

### Section K vintage-agnostic discipline

All "year" tokens in cuvée slugs (1847, 1842, 1891, 1827) are documented solera/brand names, not vintage years. Confirmed clean per QA2.

### Festival annual field

All 8 festivals have explicit `annual: true|false` — no nulls. This satisfies the `feedback_ship_gate_gaps` Gap 2 manual workaround.

### Cuvée taste-evidence URL sharing (Gap 1)

QA2 stripped 87 taste blocks for shared-overview/404 fabrication and reassigned source_url + cuisine_evidence_url to producer site roots (per Rhône substitution discipline). Sample-verified retained 68 are on producer per-wine pages.

### Signature wines orphan check

All 12 signature_wines slugs present in wines.json. No orphan references from the 87 taste-stripped cuvées.

---

## Upstream prompt-hardening recommendation

**Defect class: support-topic prose ranking-pattern leakage.**

The wine-research SCHEMA + QA1 + QA2 enforce the categorical ranking-strip-list against `wines.json` + `vineyards.json` + `signature-wines.json` reasonably well. But the same prose patterns are reaching support-topic files (`wine-festivals`, `wine-bars`, `wine-history`, `signature-grapes`, `neighborhoods`, `budget-wines`, `day-trips-wine`, `region.json`, `distilleries`) where the researcher writes descriptive prose without internalising the same discipline. Jerez had 14 (Tuscany region ship had similar; the pattern recurs every region).

Three concrete fixes (mirrors the mechanical backstop pattern that was applied to `check_score_claims.py` after Ribera):

1. **Extend `scripts/check_score_claims.py` regex to walk ALL topic files, not just wines.json + vineyards.json.** Currently the script's WARN output for Jerez correctly says "no prose score-claims found" — but it's checking the wine-vertical files only. Add walk over wine-festivals/wine-bars/wine-history/signature-grapes/neighborhoods/budget-wines/day-trips-wine/region.json/distilleries with the same regex set. The ranking-strip patterns (greatest, finest, world's most, most prestigious, most celebrated, most storied, most iconic, the defining, benchmark, one of the great, the most recognised, in the world, anywhere in the world, legendary, mythic, put X on the map, synonymous with one of) are already in the playbook; adding them to the checker would catch this regression mechanically.

2. **Update `agents/wine-research/PROMPT.md` to extend the ranking-prose ban explicitly to support-topic descriptions.** The current prompt emphasises discipline on `wines[*]` and `vineyards[*]` description fields. Add a clause: "The categorical ranking-strip list applies to EVERY description, summary, vibe, tip, and blurb in EVERY topic file — wine-festivals, wine-bars, wine-history, signature-grapes, neighborhoods, budget-wines, day-trips-wine, region, distilleries. Sherry being world-famous does not license the prose to say so."

3. **Add a QA1 Section H sub-check: "Sweep support-topic free-text fields with the same prose-strip regex used on wines.json + vineyards.json."** The QA1 PROMPT.md Section H currently says "no em-dashes, no AI-tells, no clones." Tighten to "Sweep ALL data files, not just wines/vineyards, with the categorical ranking-strip patterns."

Same root cause as Gap 1 (support-files getting less scrutiny than wine-vertical files); same fix shape (extend the existing checker's file scope + update the prompt + update the QA checklist).

---

## Final ship_safety

```
spain/jerez: ALL CHECKS PASSED
Total HARD failures: 0
```

Note: one transient `check_external_urls` TimeoutError on delgadozuleta.com (slow TLS handshake from this host) self-resolved on retry — URL returns 200 once the host warms up. Not a defect; same fetch-fail class noted by QA1.

---

**OPUS-FOUND-14 spain/jerez**
- Total defects actioned: 14 (all class: categorical ranking / soft-superlative in support-topic prose)
- Final ship_safety: 0 HARD failures, ALL CHECKS PASSED
- Upstream recommendation: extend check_score_claims.py + wine-research PROMPT.md + QA1 Section H to enforce the ranking-strip list across ALL data files, not only wines.json + vineyards.json + signature-wines.json.
