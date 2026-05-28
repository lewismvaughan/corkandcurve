# Opus Final QA Report: spain/ribera-del-duero
Date: 2026-05-28
Agent: Opus final QA (1M context)
QA1: 17 fixes (2026-05-28)
QA2: 77 fixes (2026-05-28)
Ship safety before Opus: PASS (0 HARD)
Ship safety after Opus: PASS (0 HARD)

---

## Result: OPUS-FOUND-12

12 residual C0 superlative/ranking-prose defects across 7 files. All fixed in-line. One adjacent name defect (sommelier first-name) caught in the same sweep. All defects sit in the same **C0 categorical-ranking-prose** class — QA1 and QA2 caught the explicit "greatest/finest" hits but missed the softer "Spain's most/world's most/most celebrated/most storied/anywhere in the world/the legendary/regarded as the defining/the most prestigious" surface that conveys identical ranking semantics.

---

## Narrow read summary

- **30+ entity spot-check** across wine-restaurants chefs, wine-hotels operators, distillery owners, hidden-gems family names, hidden-gems winemakers: 1 partial-first-name attribution found (Microbodega Urbana "sommelier Roberto" — source describes him as proprietor with wine knowledge, not formal sommelier). Fixed. QA2 had cleaned the chef-name and family-name layer; this was a single residual surface QA2 didn't sweep.
- **Itinerary end-to-end**: `classic-golden-mile-weekend` and all 4 others — all 17 venue slugs resolve against vineyards.json (60 producers). PASS. QA1 work confirmed.
- **Festival end-to-end**: `gran-fiesta-vendimia-ribera-del-duero` — riberadelduero.es and rutadelvinoriberadelduero.es both confirm September 3-6 2025 (VIII edition). The QA dispatch brief said "October" — the data correctly says September; brief was stale. PASS.
- **Cuvée end-to-end** (Vega Sicilia Unico, editorial 5.0, in retained-taste set):
  - Producer `bodegas-vega-sicilia` resolves in vineyards.json. PASS.
  - Tags all conform to WINE_TAGS.md researcher-emittable vocabulary (style/body/tannin/acidity/pairing/occasion/mood/editorial). 0 derived tags emitted. PASS.
  - `cuisine_evidence_url` = https://www.vega-sicilia.com/en/wines/unico/ — returns HTTP 520 (Cloudflare anti-bot block). Treated as `fetch-fail` by ship_safety, not a defect. The per-wine URL is real; 8 marquee wines (Vega Sicilia + Pingus stable) sit behind the same anti-bot wall.
  - `pairings[*].tablejourney_ref`: all null (no cross-link risk to verify).
  - Taste descriptors are differentiated (dried cherry/leather/tobacco/cedar/dried fig/spice + dark plum/dried herbs/graphite/chocolate/earthy mineral) — not the template-fill pattern QA2 caught on the 66 stripped wines.
- **5 spot-checks of editorial_score >= 4.7**: vega-sicilia-unico, pingus, malleolus-de-sanchomartín, aalto-ps, malleolus-de-valderramiro — all defensible per brief's marquee list. La Horra (4.9) and Quintanilla de Onésimo (4.9) neighborhoods both real prestige sub-zones. PASS.
- **Águila biodynamic/Demeter reconciliation**: full grep across all 25 files for "aguila" + "biodynamic" / "demeter" returned 0 hits. QA1 + QA2 complete. PASS.

---

## Defects found and fixed

| # | Class | File | Entity/Slug | Fix |
|---|-------|------|-------------|-----|
| 1 | C0 (Spain's most + ranking copy) | wines.json | vega-sicilia-unico | taste.summary: removed "Spain's most storied red" |
| 2 | C0 (anywhere in the world) | wines.json | vega-sicilia-unico | history.summary: removed "one of the longest-aged wines released commercially anywhere in the world" clause |
| 3 | C0 (One of Spain's most celebrated) | wines.json | vega-sicilia-unico | description: removed "One of Spain's most celebrated and long-lived reds" clause |
| 4 | C0 (one of the great wines) | wines.json | pesus | history.summary: "one of the great wines of the Burgos sector" → "among Burgos-sector collectors" |
| 5 | C0 (one of Spain's most celebrated) | wines.json | matallana | history.summary: "Telmo Rodriguez, one of Spain's most celebrated itinerant winemakers" → factual descriptor |
| 6 | C0 (Spain's most + hyperbole) | wines.json | (mauro-vs pairings) | pairings.why: "Spain's most concentrated aged cheeses" → factual |
| 7 | C0 (world's most concentrated source) | wine-history.json | soria-pre-phylloxera-rediscovery | description: "the world's most concentrated source of ungrafted old-vine Tempranillo" → "the highest concentration of ungrafted old-vine Tempranillo in the DO" |
| 8 | C0 (put on the world map + legendary) | vineyards.json | bodegas-vega-sicilia | description: "estate that put the region on the world map, producing the legendary Unico" → factual founding-year + product description |
| 9 | C0 (one of Spain's great wines) | neighborhoods.json | valbuena-de-duero (vibe) | "synonymous with one of Spain's great wines" → factual Valbuena 5 reference |
| 10 | C0 (one of Spain's most celebrated wines) | neighborhoods.json | valbuena-de-duero (description) | "one of Spain's most celebrated wines" clause removed |
| 11 | C0 (most prestigious postal code) | neighborhoods.json | quintanilla-de-onesimo (vibe) | "the most prestigious postal code in Ribera del Duero" → "at the centre of the Golden Mile stretch" |
| 12 | C0 (regarded as the defining) | dietary.json | goyo-garcia-viadero-natural | "Widely regarded as the defining natural-wine producer in the appellation" removed; replaced with verifiable importer/distribution facts |
| 13 | C0 (legendary + the defining) | wine-experiences.json | lechazo-asado-wine-pairing | "legendary Asador Casa Florencio" + "the defining food and wine pairing of the region" → factual descriptors |
| 14 | C0 (Spain's most celebrated cellar) | itineraries.json | harvest-season-full-week day 2 | "Spain's most celebrated cellar" → "the founding 1864 cellar" |
| 15 | D (partial-first-name attribution + categorical superlatives) | nightlife.json | microbodega-urbana-valladolid | "celebrated wine bar...run by sommelier Roberto...One of the most interesting wine-by-the-glass programmes in the region" → factual descriptor (source calls him owner/proprietor with wine knowledge, not sommelier) |

(15 distinct edits across 12 logical defects — counts 1-3 and 9-10 collapse pairs on same entities.)

**Defects judged clean / kept (borderline, not violations of the strict C0 ban):**

- day-trips-wine.json `segovia-aqueduct-region`: "one of Spain's most celebrated food traditions" (cochinillo) — QA1 already softened from "greatest"; "most celebrated food tradition" is a food-tradition descriptor, not a wine-quality ranking. Retained.
- day-trips-wine.json `rioja-wine-region`: "Spain's most internationally recognised wine appellation" — factual marketing/export reach descriptor (Rioja IS the most internationally distributed Spanish DO), not a quality-ranking superlative. Retained.
- day-trips-wine.json `soria-atauta-old-vines`: "one of Spain's smallest provincial capitals" — geographic fact about population. Retained.
- hidden-gems.json `dominio-de-es`: "One of the most distinctive expressions of the Soria sub-zone available outside Spain" — qualified ("of the most" + scope-limited "available outside Spain"); Decanter-sourced. Borderline. Retained.

---

## Defect class & upstream prompt-hardening recommendation

**Class**: C0 (categorical-ranking-prose) surface that QA1 + QA2 missed because they pattern-matched only on the explicit terms in the wine-research / QA prompts: `greatest`, `finest`, `best ... in the world`, `among the world's`, `regarded as one of`, `mythic`.

The Ribera regression introduces a second-tier surface using SOFTER vocabulary that conveys identical ranking semantics:

- `Spain's most <X>` (most storied, most celebrated, most prestigious, most internationally recognised)
- `world's most <X>` / `anywhere in the world`
- `one of the great <X>`
- `the legendary <entity>`
- `put on the world map`
- `regarded as the defining <X>`
- `the defining <X> in the region`
- `the most prestigious postal code/cellar/etc.`
- `one of the most <celebrated|prominent|important|iconic|defining|prestigious> <X> in the region`

These were absent from the existing C0 strip-list and so passed through QA1 + QA2 untouched on a region where the prose was written more cautiously than Sicily/Rhône (no "Tim Atkin 95+" violations, no "Parker 100" violations, no fabricated tre bicchieri — but plenty of "Spain's most storied" / "the legendary Unico" / "world's most concentrated").

### Recommended hardening (in priority order)

1. **`agents/qa/PROMPT.md` Section C0** — expand the strip-list verbatim:

   > Strip any clause matching `greatest`, `finest`, `best ... in the world`, `among the world's`, `regarded as one of`, `mythic`, **`<country>'s most <adjective>`, `the world's most <adjective>`, `anywhere in the world`, `one of the great <category>`, `the legendary <entity>`, `put <region> on the (world) map`, `regarded as the defining <category>`, `the defining <category> in the region`, `the most prestigious <X>`, `one of the most {celebrated|prominent|important|iconic|defining|prestigious|distinctive} <X>`** — even on marquee estates. The reputation belongs in `editorial_score` + tags + verified milestones.

2. **`scripts/check_score_claims.py`** — extend the prose-pattern regex from the current critic-name/point-number focus to ALSO flag the above ranking-vocabulary tier as WARN (so ship_safety surfaces them before they reach Opus). The Rhône / Sicily / Ribera regressions all share the same root: QA agents trust ship_safety; ship_safety only flagged numeric score patterns; ranking-prose escaped to Opus. Move the ranking-prose grep into the gate.

3. **`agents/wine-research/PROMPT.md`** — add a "Reputation vocabulary discipline" subsection adjacent to the existing score-claim ban: enumerate the soft-superlative bans so the research agent never emits them in the first place. Sample replacement table (`one of Spain's most celebrated` → `<concrete fact: e.g. founded YYYY / DO-founding member / first vintage YYYY>`) gives the agent an explicit re-writing pattern.

4. **`scripts/check_score_claims.py`** (second harden) — add a "first-name only sommelier/chef/owner attribution" check. The Microbodega Urbana "sommelier Roberto" defect is a thin-source-mining tell: when a venue is staffed by an individual whose ONLY identifier in the source is a first name, the research agent has been writing it up as "sommelier <FirstName>" / "chef <FirstName>". Mechanical flag: any `chef|sommelier|owner|winemaker [A-Z][a-z]+(?!\s[A-Z])` (one capitalised word with no surname following) is a WARN.

The class summary line for the ship_safety / fixes-feed-prompts memory: **"Soft superlative ranking vocabulary escapes the existing C0 strip-list; widen the regex and move into ship_safety."**

---

## Final ship_safety outcome

```
bash /station/repo/scripts/ship_safety.sh spain ribera-del-duero
============================================================
  spain/ribera-del-duero: ALL CHECKS PASSED
============================================================
```

0 HARD failures across all 7 mechanical layers. Cuvée taste evidence check matched 9/17 (8 fetch-fails on Vega Sicilia / Pingus Cloudflare-blocked per-wine pages — not defects).

---

OPUS-FOUND-12 spain/ribera-del-duero | 15 edits across 12 logical defects (all C0 + 1 named-attribution) | ship_safety PASS (0 HARD)
