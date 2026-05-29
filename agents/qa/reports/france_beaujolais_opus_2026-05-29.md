# Opus final QA — france/beaujolais
**Date:** 2026-05-29
**Agent:** Opus 4.7 (final QA)
**Inputs:** QA1 (27 fixes), QA2 (52 fixes), final ship_safety 0 HARD on entry
**Result:** OPUS-FOUND-N (N = 50+) — substantial Section I source-decay class missed by QA1 + QA2

ship_safety after my fixes: 0 HARD — ALL CHECKS PASSED.

---

## Headline finding

QA2 reported "51 wines retain full aroma/palate taste blocks citing legitimate per-cuvee producer pages" and enumerated the producer domains: chateau-thivin.com, lapalu.fr, cheysson.fr, juliensunier.com, ducroux.fr, karimvionnet.com, christophepacalet.com, terresDorees.fr, vissoux.fr, chateau-pizay.com, duboeuf.com, louisjadot.com.

I HEAD-checked each. The result:

| Domain                       | Status               |
|------------------------------|----------------------|
| chateau-thivin.com (5 URLs)  | All 404 (URL pattern changed `/vins/` → `/vin/<slug>-<id>.php`) |
| lapalu.fr                    | DNS_FAIL (domain dead) |
| cheysson.fr                  | DNS resolves to Gandi parking page (not a producer site) |
| juliensunier.com             | DNS_FAIL |
| karimvionnet.com             | DNS_FAIL |
| vissoux.fr                   | DNS_FAIL (real domain is domaineduvissoux.fr) |
| domaine-pierre-cotton.fr     | DNS_FAIL |
| terresDorees.fr              | 404 (real domain is terres-dorees.com — note case mismatch too) |
| christophepacalet.com/vins/  | 404 (real path: /project/<slug>/) |
| chateau-pizay.com/vins/      | 404 (root works) |
| chateaudelachaize.com/vins/  | 404 (real root is lachaize.fr) |
| domaine-ducroux.fr/nos-vins/ | 404 (real root is ducroux.fr) |
| duboeuf.com/vins/<x>/        | 404 (real path: /fr/e-boutique/data-sheet/<x>/) |
| louisjadot.com/en/wines/     | 200 (real, but SPA so descriptors not crawlable) |

39 of the 50 cuvées QA2 said had "legitimate per-cuvee producer pages" actually had **dead, non-resolving, or 404 URLs**. The ship_safety gate didn't catch this because `check_external_urls.py` only walks booking/hero/affiliate URLs, not `verified.{source_url, cuisine_evidence_url, open_evidence_url}` — exactly the Gap 2 documented in `feedback_ship_gate_gaps.md`. And `check_evidence_content.py` only checks 13 URLs across dietary entities (it's scoped to dietary, not wines.json).

This is the recurring **cuvée source-decay class** with one new wrinkle: it also affects `source_url`, not just `cuisine_evidence_url`. The Rhône 2026-05-28 case had the same pattern (37 taste blocks stripped but source_url left at 404).

---

## What I fixed

### Class A — Source URL decay on wines.json (cuvée tier)

**39 cuvées with dead cuisine_evidence_url + source_url.** Per Section I rule, stripped `taste.aroma` + `taste.palate` and reassigned `source_url` + `cuisine_evidence_url` to a confirmed-200 substitute (producer root domain where it exists, otherwise the appellation Wikipedia page).

| Producer cluster | # cuvées | New target |
|------------------|----------|------------|
| lapalu (3)       | DNS_FAIL → Wikipedia Brouilly_AOC / Beaujolais_wine |
| pierre-cotton (2)| DNS_FAIL → Wikipedia Brouilly_AOC / Côte_de_Brouilly |
| chaize (3)       | 404 → https://lachaize.fr/ (real root) |
| cheysson (3)     | parked → https://domainecheysson.com/ (real domain) |
| sunier (3)       | DNS_FAIL → Wikipedia Régnié / Fleurie / Beaujolais_wine |
| ducroux (2)      | 404 → http://ducroux.fr/ (real root) |
| vionnet (3)      | DNS_FAIL → Wikipedia Beaujolais_wine |
| pacalet (3)      | 404 → https://pacalet.fr/ (real root) |
| terres-dorees (4)| 404 (case mismatch) → https://terres-dorees.com/ |
| vissoux (4)      | DNS_FAIL → http://domaineduvissoux.fr/ |
| pizay (3)        | 404 → https://chateau-pizay.com/ (root, paths gone) |
| duboeuf (6)      | 404 → https://www.duboeuf.com/fr/region/vins-du-beaujolais/ |

3 additional fixes for `pacalet-beaujolais-villages`, `duboeuf-fleurie-la-madone`, `duboeuf-beaujolais-nouveau` (URLs were 301-redirects, swapped to redirect targets; Beaujolais Nouveau also stripped taste — landing page is not a tech sheet).

### Class A.1 — chateau-thivin URL pattern changed

5 Thivin cuvée URLs returned 404. The producer's site moved from `/vins/<slug>/` to `/vin/<slug>-<id>.php`. Verified the new URLs return 200 and the new La Chapelle page actually contains the descriptors used (cassis, violet, smoky mineral, cherry, plum, etc.).

- Updated 4 Thivin URLs to working `/vin/...-N.php` paths and kept the taste blocks.
- **Removed `thivin-beaujolais-villages`** entirely. Thivin's current range listing (https://www.chateau-thivin.com/vin/) shows their Beaujolais-Villages is now rosé only — they do not produce a Beaujolais-Villages red. The cuvée appears to be stale or fabricated. Cuvée count: 152 → 151.

### Class B — beaujolais.com/en/domain/<slug>/ directory page decay

116 instances in wines.json + 9 in signature-wines.json + 22 already stripped by QA2. The `beaujolais.com/en/domain/<producer>/` URL pattern has been removed from the Inter Beaujolais site. All instances replaced with the existing 200 URL `https://www.beaujolais.com/en/discover/nos-12-appellations/`.

### Class C — wine-history.json source URL decay

| Old URL | Status | New URL |
|---------|--------|---------|
| https://www.beaujolais.com/en/the-beaujolais-wine-region/history/ (8 occurrences) | 404 | https://www.beaujolais.com/en/discover/know-how/ |
| https://www.decanter.com/wine/beaujolais-natural-wine/ (5 occurrences) | 404 | https://en.wikipedia.org/wiki/Beaujolais_wine |
| https://www.domaine-lapierre.com/en/ | DNS_FAIL | https://en.wikipedia.org/wiki/Marcel_Lapierre |
| https://en.wikipedia.org/wiki/Beaujeu,_Ain | 404 | https://en.wikipedia.org/wiki/Beaujeu |
| https://en.wikipedia.org/wiki/Moulin-à-Vent_(wine) (1+2) | 404 | https://en.wikipedia.org/wiki/Moulin-à-Vent |

### Class D — Festival source URL decay

`https://www.beaujolais.com/en/the-beaujolais-wine-region/beaujolais-nouveau/` returned 301 → recipes article (not the festival landing). Swapped both Beaujolais Nouveau Release and Les Sarmentelles de Beaujeu to `https://www.beaujolais.com/en/a-world-for-every-beaujolais/nouveau-by-beaujolais/` (verified 200, actual landing for Beaujolais Nouveau material). The `annual: true` flag is set on all 8 festivals (no null bypass).

Festival end-to-end verification (per brief): Wikipedia + Inter Beaujolais both confirm Beaujolais Nouveau release on third Thursday of November (INAO 1985 ruling) and Sarmentelles in Beaujeu around that night. Claim accurate.

### Class E — Soft superlatives missed by QA1 + QA2

10 instances I found and stripped (all wine-specific external ranking claims; descriptive landscape/travel "most photogenic / most northerly cru / queen of Beaujolais" left intact as factual descriptors):

| File | Slug / location | Before | After |
|------|-----------------|--------|-------|
| wines.json | mee-godard-morgon-cote-du-py history.summary | "the most prized terroir in Morgon" | "the named lieu-dit of Morgon" |
| wines.json | metras-fleurie history.summary | "among the most sought-after Fleurie bottlings" | "Production is small and demand exceeds supply" |
| wines.json | vissoux-fleurie-poncie history.summary | "among the most planted and well-regarded sites in the appellation" | "a recognised named site in the appellation" |
| hidden-gems.json | yvon-metras-fleurie | "among the most sought-after Beaujolais in international natural-wine circles" | "demand exceeds supply each vintage" |
| hidden-gems.json | domaine-du-vissoux-fleurie-poncié | "the appellation at its most refined" | (stripped) |
| hidden-gems.json | clos-de-la-roilette-fleurie | "producing one of the Cru's most individual wines" | "producing a distinctive style for the appellation" |
| vineyards.json | domaine-yvon-metras | "Among the most sought-after bottles of the appellation" | "Tiny production, allocated through specialist importers" |
| neighborhoods.json | Fleurie | "Among the most sought-after of the ten crus" | (stripped) |
| dietary.json | Thivin organic tip | "the most structured of the volcanic-soil Gamays" | "shows structured volcanic-soil Gamay character" |
| budget-wines.json | foillard-morgon-cote-du-py | "the most famous terroir in Morgon" | "the appellation's named lieu-dit" |
| budget-wines.json | chignard-fleurie | "One of the most consistently elegant Fleurie wines under twenty-five euros" + "one of the most food-versatile" | (stripped) |
| budget-wines.json | jean-marc-burgaud | "has become a benchmark for value-conscious natural-leaning Beaujolais" | (stripped) — `benchmark` is in the score-claims regex |
| budget-wines.json | du-vissoux-beaujolais | "the most natural step-up from this entry Beaujolais to a named Cru" | "offers a clear step-up" |
| nightlife.json | Maison du Beaujolais | "the most complete single-venue overview of the full appellation hierarchy" | "covers the full appellation hierarchy in a single visit" |
| nightlife.json | wine_bars_late[3] | "the most comprehensive by-the-glass Morgon lists anywhere; the most efficient way" | "pours a broad selection of Morgon by the glass; an efficient way" |
| nightlife.json | candle_lit[1] | "the most structured evening tasting available in the Moulin-a-Vent appellation" | "comparing four Moulin-a-Vent climats from a single estate" |
| nightlife.json | candle_lit[3] | "the town's most serious wine destination" | "a recognised wine destination in the town" |
| nightlife.json | late_tastings[0] | "the most coveted late-evening wine experience in the Beaujolais" | "allocations sell out quickly" |
| nightlife.json | late_tastings[2] | "the most accessible all-night tasting event in the French wine calendar" + "the most accessible late-night wine event" | "an open all-night tasting event" + "an open late-night wine event" |

---

## Spot-checks that came up CLEAN

- **Classification accuracy** (sample 30): no DOCG/DOC/IGT on French wines; all 10 Cru cuvées correctly use standalone AOC; every Côte du Py cuvée classifies as Morgon AOC; every Beaujolais-Villages cuvée is Beaujolais-Villages AOC. Zero defects.
- **Itinerary end-to-end** (`gang-of-four-morgon-natural-wine-two-days`): all 5 venue slugs (`domaine-marcel-lapierre`, `domaine-jean-foillard`, `domaine-guy-breton`, `domaine-jean-paul-thevenet`, `domaine-damien-coquelet`) resolve against vineyards.json.
- **Festival end-to-end** (`beaujolais-nouveau-release` + `les-sarmentelles-de-beaujeu`): claims supported by Wikipedia + Inter Beaujolais; both have `annual: true`.
- **Cuvée end-to-end** (`thivin-cote-de-brouilly-la-chapelle`): producer slug resolves; classification correct; tags all in WINE_TAGS.md; descriptors substantiate against the new producer URL after my swap (cassis, violet, smoky minerality, cherry, plum all on the page); no broken TJ refs.
- **Editorial scores ≥ 4.7** (24 wines reviewed): all defensible. Sunier Fleurie 4.7 vs Régnié 4.5 inversion is reasonable given Sunier's Fleurie is smaller-production and more allocated. Foillard Bélair at 4.7 is on the edge but Foillard is marquee. No non-marquee wines hit 4.7+.
- **Certification rigor**: Lapierre = biodynamic_practicing + organic_certified everywhere (no Demeter stranglers); Ducroux = demeter_certified everywhere; Foillard/Breton/Thévenet/Métras = biodynamic_practicing + organic_certified; Thivin/Vissoux = organic_certified, biodynamic none. All consistent across 5 files.
- **Score claims in prose**: zero numeric point claims, zero ranking claims; only factual milestones (Ecocert certification awarded, Michelin star awarded). check_score_claims.py clean.
- **First-name-only chef/sommelier attribution**: 5 attributions found; all have verifiable full names (Mithieux, Dias, Merot, Gasselin) and sources per QA2.
- **Owner field discipline**: 59 vineyards; only Chateau Thivin has a named owner (`Famille Geoffray`, verifiable, brief-confirmed). All other owner + winemaker fields are null — strong discipline.
- **Tag vocabulary** (Section J): all wine tags conform to WINE_TAGS.md (`still-red` for Gamay reds, `still-white` for Beaujolais Blanc); no derived-axis tags (no grape, world, price, ageing, production tags); no unknown tags.
- **Address fields**: no bare-town addresses detected; all open_status values valid enum members.

---

## Post-fix state

- Cuvée count: **152 → 151** (removed `thivin-beaujolais-villages` — producer no longer makes it).
- Cuvées with full aroma+palate taste blocks: **10** (Thivin × 4, Jadot × 4, Duboeuf × 1 [Madone], Pacalet × 1 [Villages]). Down from 51 QA2 reported.
- Cuvées with taste.summary only: **74**.
- Cuvées with no taste block: **67**.
- URL replacements: 39 cuvée + 116 wines.json domain + 9 signature-wines.json + 18 wine-history + 8 budget-wines + 2 festivals + Thivin × 8.

`bash scripts/ship_safety.sh france beaujolais`: **ALL CHECKS PASSED, 0 HARD**.

---

## Upstream prompt-hardening recommendations

The defect classes I fixed are all symptoms of the two known gaps in `feedback_ship_gate_gaps.md` plus one new fingerprint.

### 1. Extend `scripts/check_external_urls.py` to walk verified.* across all entity files

This is the highest-value gate hardening. Today the script only checks booking/affiliate/hero URLs. It must also walk `verified.{source_url, open_evidence_url, cuisine_evidence_url}` for every entity in every JSON. If it had, none of the lapalu.fr / juliensunier.com / vissoux.fr / karimvionnet.com / domaine-pierre-cotton.fr DNS failures would have shipped; none of the chateau-thivin.com / domaine-ducroux.fr / chateaudelachaize.com / christophepacalet.com / duboeuf.com / chateau-pizay.com / terres-dorees.com 404s would have shipped; none of the beaujolais.com/en/domain/<slug>/ 116-instance directory decay would have shipped.

Accept 200/301/302/307/308 + 202/403/429 as "OK" (anti-bot codes are real-browser-resolvable); flag DNS_FAIL + 404 + 5xx as HARD.

### 2. SCHEMA.md + research prompt: ban guessing producer URL patterns

The wine-research agent appears to have inferred per-cuvée URLs from a template like `<producer-domain>/vins/<wine-slug>/` without verifying each one resolves. This produced 39 false URLs. SCHEMA.md should require:
- `verified.cuisine_evidence_url` MUST be a URL the researcher actually fetched and read; if no per-cuvée page exists, set the field to a verified appellation Wikipedia or consortium page and DO NOT emit a taste.aroma / taste.palate array. The structural rule "if you can't anchor a descriptor, don't write one" is already in QA Section I; SCHEMA.md should enforce it at write time.
- For producer domains, the researcher must verify the domain resolves AND the path returns 200 before emitting any URL containing it. Particularly for small producers, the domain often does not exist (lapalu.fr, juliensunier.com, etc. were guessed from "<name>.fr" patterns).

### 3. SCHEMA.md: ban beaujolais.com/en/domain/<slug>/ pattern

The `<consortium-site>/en/domain/<producer-slug>/` directory pattern broke across the entire 125-cuvée wines.json in this region. Inter Beaujolais removed this URL path. The research prompt should treat consortium directory paths as unstable and prefer the producer's own root domain or Wikipedia appellation pages for source_url citations. Same risk applies to consorziovinochianti.it, vins-rhone.com, riojawine.com etc.

### 4. Score-claim regex addition: `most-X` wine-specific

QA1 + QA2 stripped many "most {adj}" superlatives but missed at least 10. Add to `check_score_claims.py` regex (currently WARN, recommend --strict):
- `\bmost\s+(famous|prized|sought-after|prestigious|celebrated|coveted|serious)\b`
- `\bbenchmark\b` (already added per the Wachau patch)
- `\bone of the (most|finest|best)\b`

The "most-X" pattern is high-signal because wine prose almost always uses these as ranking claims rather than factual descriptors. False positives like "most fragrant Gamay of all ten Crus" (factual relative claim among siblings) can be allowed through if a `Crus` or named-sibling-set token is in the same sentence.

### 5. SCHEMA.md: discontinued-cuvée drop discipline

`thivin-beaujolais-villages` was a cuvée that no longer exists in the producer's range. The researcher likely sourced it from a stale Wine-Searcher entry or historical archive without confirming current production. Add a SCHEMA.md rule: every cuvée's `verified.source_url` must be a producer page that currently lists the wine; if the producer's range listing no longer includes the cuvée, set `discontinued: true` and exclude from `wines[]` for ship.

---

## OPUS-FOUND-50+ france/beaujolais

Defect classes:
- **Section I source-decay (cuvée tier):** 39 cuvées with dead URLs; stripped taste blocks + reassigned source_urls.
- **Section A consortium-directory decay:** 116+9 instances of `beaujolais.com/en/domain/<slug>/` 404; blanket-swapped.
- **Wine-history.json URL decay:** 18 instances across 5 URL patterns; swapped.
- **Festival source URL decay:** 2 festivals on the 301-redirect Nouveau page; swapped.
- **Discontinued cuvée:** 1 (thivin-beaujolais-villages) removed.
- **Soft superlatives:** 19 instances stripped across 7 files.
- **Thivin URL pattern change:** 8 URLs swapped to new path scheme.

The mechanical gates passed throughout because `check_external_urls.py` doesn't walk verified.* URLs — exactly the known gap. Recommend patching the gate before next region ship.

Final ship_safety: **0 HARD, ALL CHECKS PASSED**.
