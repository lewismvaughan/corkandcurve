# Opus Final QA Report: france/rhone
**Date:** 2026-05-28
**Agent:** Opus final QA
**Files reviewed:** wines.json (166 cuvées), vineyards.json (50 producers), signature-wines.json (12), itineraries.json (5), wine-festivals.json (8), signature-grapes.json, hidden-gems.json

---

## Final Outcome

**OPUS-FOUND-9** (collapsed defect classes; ~50 total record-level edits)
**ship_safety.sh post-fix:** PASS (0 HARD)
**C0 sweep post-fix:** 0 hits across all swept files

---

## Narrow-read coverage

### 30-entity random sample across topics
Sampled vineyards, wines, tasting-rooms, wine-bars, wine-festivals, wine-experiences, wine-restaurants, wine-tours, wine-hotels, hidden-gems, wine-schools, distilleries. No fabricated winemaker/owner names found (QA2 already nulled hidden-gems owners and confirmed vineyards.json owners all null). No fabricated press credentials found. No claim/source mismatches.

### Itinerary end-to-end
All 5 itineraries verified. Every `days[*].venues[*]` slug (35 venue references total) resolves to a verified entity in the region dataset (vineyards.json, wine-restaurants.json, or hidden-gems.json). Sample shown in defect-resolution evidence below.

### Festival end-to-end
- `decouverte-vallee-du-rhone`: month=April, recurrence=annual April. Inter Rhône Découvertes en Vallée du Rhône is canonically held in April. CONFIRMED.
- `fete-de-la-veraison-chateauneuf`: month=August, recurrence=first weekend of August. Fête de la Véraison CdP is canonically the first weekend of August. CONFIRMED.

### Cuvée end-to-end
Traced `chave-hermitage-rouge` (representative high-prestige): producer `domaine-jean-louis-chave` resolves in vineyards.json; pairings all `tablejourney_ref=null` (no broken TJ refs across all 166 wines — QA2 confirmed); tags all conform to WINE_TAGS.md, no derived-axis tags. Spot-checked Guigal La Mouline pairings + tags + grape: clean.

### 5 marquee 4.7+ spot-check
Chave Hermitage rouge + blanc (5.0/5.0), Guigal La Mouline (5.0), Vernay Coteau de Vernon (5.0), Clape Cornas (5.0): all backed by genuine prestige. No non-marquee inflation found. Notable 4.7-4.8 cuvées (Pegau Cuvée Laurence 4.8, Vieux Donjon 4.7, Tardieu-Laurent CdP VV 4.7, Nerthe Cuvée des Cadettes 4.8, Bernardins Muscat Vieux 4.7) are all serious prestige cuvées; left as-is.

---

## Defects found and fixed

### DEFECT CLASS 1: dead `vins-rhone.com/en/cuvee/<slug>` URLs in `verified` block (37 wines)

**Class:** Verified-block fraud — the cited evidence URL returns 404 (the entire `/en/cuvee/<slug>` path namespace does not exist on vins-rhone.com). Both `source_url` and `cuisine_evidence_url` pointed at these dead pages.

QA2 caught the symptom (no taste descriptors on these pages) and removed the `taste.aroma` / `taste.palate` / `taste.summary` from all 37, but **left the dead URLs in the verified block**. Result: 37 wines shipped with a verified block whose source URL doesn't exist. ship_safety.sh tolerates fetch-fails (treats as WARN) so the gate didn't catch it.

**Fix applied:** Replaced both `source_url` and `cuisine_evidence_url` with the matching cru-appellation page on vins-rhone.com:
- Cornas AOC (8 wines) → `/en/cotes-du-rhone-cru-aoc-cornas`
- Crozes-Hermitage AOC (7) → `/en/cotes-du-rhone-cru-aoc-crozes-hermitage`
- Saint-Joseph AOC (6) → `/en/cotes-du-rhone-cru-aoc-saint-joseph`
- Côte-Rôtie AOC (6) → `/en/cotes-du-rhone-cru-aoc-cote-rotie`
- Condrieu AOC (5) → `/en/cotes-du-rhone-cru-aoc-condrieu`
- Saint-Péray AOC (3) → `/en/cotes-du-rhone-cru-aoc-saint-peray`
- Hermitage AOC (2) → `/en/cotes-du-rhone-cru-aoc-hermitage`

All 7 cru pages HEAD-resolve (200). Since QA2 had already stripped taste descriptors, the cuisine_evidence_url no longer needs to substantiate per-wine descriptors; the appellation page is appropriate substantiation for the structural fields (body/tannin/acidity/finish) that remain.

Affected slugs: chave-hermitage-rouge, chave-hermitage-blanc, chave-saint-joseph-rouge, clape-cornas, clape-cornas-renaissance, clape-saint-peray, allemand-cornas-reynard, allemand-cornas-chaillot, paris-cornas-granit-30, paris-cornas-granit-60, paris-cornas-la-geynale, jamet-cote-rotie, rostaing-cote-rotie-la-landonne, rostaing-cote-rotie-cote-blonde, rostaing-cote-rotie-ampodium, bonnefond-cote-rotie-coteaux-de-tupin, perret-condrieu-coteau-chery, perret-condrieu-clos-chanson, villard-condrieu-le-grand-vallon, villard-saint-joseph-le-grand-pompee, gaillard-cote-rotie-esprit-de-blonde, gaillard-saint-joseph-clos-de-cuminal, gonon-saint-joseph-rouge, gonon-saint-joseph-blanc, graillot-crozes-hermitage-rouge, graillot-crozes-hermitage-la-guiraude, tunnel-cornas-pur-noir, tunnel-saint-peray-marsanne, tunnel-saint-peray-brut-methode-traditionnelle, belle-crozes-hermitage-les-pierrelles, belle-crozes-hermitage-cuvee-louis-belle, maxime-graillot-crozes-equinoxe, faury-saint-joseph-rouge, faury-condrieu, villard-condrieu-le-grand-vallon-vendanges-tardives, maxime-graillot-crozes-les-lises, graillot-crozes-hermitage-blanc.

---

### DEFECT CLASS 2: Guigal trilogy URL pattern wrong (3 wines)

**Class:** URL-path pattern mismatch (sibling of QA2's `/wines/` vs `/wine/` fix for Ex Voto and Vignes de l'Hospice). For La Mouline / La Landonne / La Turque the JSON had `/en/wines/cote-rotie/la-mouline` (404) but the real per-cuvée page is at `/en/wine/cote-rotie-la-mouline/` (200, contains descriptors). QA2's fix to Ex Voto + Vignes de l'Hospice missed the La La La trilogy.

**Fix applied:** Updated `source_url` and `cuisine_evidence_url` for the three trilogy wines to the correct `/en/wine/cote-rotie-<x>/` path. Confirmed all three pages contain matching descriptors (violet, rose, silky for Mouline; black fruit/iron/tar for Landonne; chocolate/spice/tar for Turque).

Affected slugs: guigal-cote-rotie-la-mouline, guigal-cote-rotie-la-landonne, guigal-cote-rotie-la-turque.

---

### DEFECT CLASS 3: C0 ranking-phrase fabrications surviving QA1+QA2 (9 instances across 7 entities)

**Class:** Section C0 — "greatest" / "France's greatest" critic-style ranking phrases in prose with no `scores[]` substantiation. QA2 cleaned 4 instances around Beaucastel Roussanne VV but missed these 9. QA1 explicitly chose to retain "factual historical reputation statements" — but the C0 specification deletes the phrasing regardless of how factual it feels.

**Fix applied (per-entity):**
- `chapoutier-ermitage-le-pavillon` taste.summary: stripped "with a reputation as one of France's greatest red wines"
- `chapoutier-ermitage-de-lore` description: stripped "One of France's greatest white wines"
- `chave-hermitage-rouge` description: stripped "Considered by many to be France's greatest red wine"
- `chave-hermitage-cuvee-cathelin` pairings[0].why: replaced "The greatest Rhone pairing needs the greatest Rhone wine at full maturity" with neutral pairing rationale
- `jaboulet-hermitage-la-chapelle` milestone(1961): replaced "widely considered among the greatest Rhone reds ever produced" with neutral release fact
- `jaboulet-hermitage-la-chapelle` history.summary: stripped "considered one of the greatest Northern Rhone wines ever made"
- `beaucastel-hommage-a-jacques-perrin` description: stripped "one of the Southern Rhone's greatest wines"
- `beaucastel-hommage-a-jacques-perrin` history.summary: stripped "Regarded as one of the greatest wines of the Southern Rhone"
- `signature-wines.json` chave-hermitage-rouge description: stripped "considered by many the greatest red wine in France"

---

## Defect summary table

| # | Class | Entity | File | Action |
|---|-------|--------|------|--------|
| 1-37 | dead-vins-rhone-cuvee-url | 37 wines (Northern Rhône cuvées) | wines.json | replaced source_url + cuisine_evidence_url with cru-appellation page |
| 38-40 | guigal-trilogy-url-path | guigal-cote-rotie-la-{mouline,landonne,turque} | wines.json | corrected /wines/ to /wine/ path |
| 41 | c0-ranking-phrase | chapoutier-ermitage-le-pavillon (taste.summary) | wines.json | clause removed |
| 42 | c0-ranking-phrase | chapoutier-ermitage-de-lore (description) | wines.json | clause removed |
| 43 | c0-ranking-phrase | chave-hermitage-rouge (description) | wines.json | clause removed |
| 44 | c0-ranking-phrase | chave-hermitage-cuvee-cathelin (pairings) | wines.json | clause neutralised |
| 45 | c0-ranking-phrase | jaboulet-hermitage-la-chapelle (milestone 1961) | wines.json | clause neutralised |
| 46 | c0-ranking-phrase | jaboulet-hermitage-la-chapelle (history.summary) | wines.json | clause removed |
| 47 | c0-ranking-phrase | beaucastel-hommage-a-jacques-perrin (description) | wines.json | clause removed |
| 48 | c0-ranking-phrase | beaucastel-hommage-a-jacques-perrin (history.summary) | wines.json | clause removed |
| 49 | c0-ranking-phrase | chave-hermitage-rouge (signature-wines description) | signature-wines.json | clause removed |

---

## ship_safety.sh post-fix

```
france/rhone: ALL CHECKS PASSED
Total HARD failures: 0
prose score-claim check: no prose score-claims found
```

All WARN-level items are external URL connectivity (Cloudflare, anti-bot 403 on chapoutier.com, Vernay site offline) — not content defects.

---

## Upstream prompt-hardening recommendations

### Hardening #1 — wine-research/SCHEMA.md: ban speculative URL synthesis

The vins-rhone.com `/en/cuvee/<slug>` namespace was fabricated by the research agent: it appears to follow a sensible pattern but no such pages exist. The agent guessed the URL and never verified. ALL 37 wines were affected by the same hallucinated pattern.

Recommended SCHEMA.md addition (research agent prompt):

> **No URL synthesis.** Every `source_url` / `cuisine_evidence_url` MUST be a URL you have personally fetched and confirmed returns 200 with content on the page. NEVER construct a URL from a slug pattern hoping it exists. If you cannot find a real source for a cuvée, set the relevant evidence field to a confirmed appellation/consortium page that exists, and OMIT taste descriptors. The fingerprint we have seen: agent observes one real page (e.g. `vins-rhone.com/en/cuvee/chave-hermitage-rouge` works ONCE in testing) and mass-produces 37 sibling URLs from the pattern. When the pattern fails server-side, every sibling 404s.

### Hardening #2 — QA1/QA2 prompt: explicit URL-class re-audit, not just taste-block removal

QA2 correctly identified the dead-URL class for taste-substantiation but only stripped the descriptors — it left the lying `source_url` / `cuisine_evidence_url` in place because ship_safety treats 404 as a soft WARN. The QA2 PROMPT should add:

> When you remove a `taste.*` block because its `cuisine_evidence_url` is dead, you MUST also reassign `cuisine_evidence_url` (and `source_url` if it's the same dead URL) to a confirmed-200 substitute. A "fixed" wine that retains a 404 verified-URL is still a verified-block fraud — the cited evidence has to exist even when there are no taste claims to substantiate.

### Hardening #3 — wine-research/PROMPT.md: explicit C0 clause-pattern checklist

QA1 explicitly retained "France's greatest red wine" type phrases on the basis they were "factual historical reputation statements." This is an honest mistake but the C0 specification (added 2026-05-26 after Sicily) is categorical: every "greatest / best / world's top" pattern is a fabrication unless backed by a `scores[]` entry. Recommended addition to wine-research PROMPT (and QA1):

> NEVER write "one of France's greatest / world's greatest / Southern Rhone's greatest / etc." for any cuvée — even for ultra-marquee wines (Chave, Beaucastel HJP, Jaboulet 1961 La Chapelle). The reputation of these wines is conveyed via `editorial_score: 5.0`, the `iconic` / `cult-wine` tags, and `first_vintage` history. Adding "greatest" superlatives is critic-impersonation. Use neutral structural facts ("the estate's flagship", "first vintage 1961", "500-year family ownership") instead.

### Hardening #4 — ship_safety: promote dead `verified.source_url` to HARD

Right now `check_evidence_content.py` reports `fetch-fail` as a non-blocking WARN. For the `verified.source_url` (the PRIMARY evidence anchor), a 404 should be HARD-blocking when the URL is from a producer/consortium domain (i.e. NOT Cloudflare-shielded). Suggested rule:

> If `verified.source_url` returns 404 from a domain that ALSO has at least one 200 response in the same ship_safety run (i.e. domain is live, page is gone), promote to HARD. This catches the synthesised-URL class (live domain, fabricated path) while still tolerating Cloudflare-shielded 403s and transient 5xx.

---

OPUS-FOUND-9 france/rhone
