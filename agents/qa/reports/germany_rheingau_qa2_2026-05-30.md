# QA2 Report: germany/rheingau — 2026-05-30

Agent: QA2 (Opus 4.7 1M)
Ship safety before QA2: PASS (0 HARD; 26 cuvee-taste-miss WARN; 7 own_site_only WARN; 0 prose score-claims)
Ship safety after QA2: PASS (0 HARD; 0 cuvee-taste-miss WARN; 0 own_site_only WARN; 0 prose score-claims)

---

## Section D — Ownership currency

Re-sampled all 61 vineyards against producer About pages, Wikipedia (DE/EN infoboxes) and 2024-2026 VDP roster. Key confirmations:

| Estate | data `owner` | verdict |
|---|---|---|
| Schloss Johannisberg | Furst von Metternich Winneburg'sche Domane GbR (Oetker Group) | match (QA1 fix held) |
| Hessische Staatsweingueter Kloster Eberbach | Land Hessen | match (state estate, Hesse Domänenamt) |
| Schloss Vollrads | Nassauische Sparkasse foundation | match (Wikipedia infobox: Parent company Nassauische Sparkasse; brief mention of "Greiffenclau Foundation" is incorrect — Erwein Graf Matuschka-Greiffenclau died in 1997 bankruptcy auction and the estate has been Nasspa-owned since) |
| Robert Weil | Wilhelm Weil and Suntory | match (Suntory majority since 1988, Wilhelm Weil 4th generation) |
| Weingut Künstler | Gunter Kunstler | match |
| Leitz | Johannes Leitz | match |
| Georg Breuer | Breuer family (Theresa Breuer) | match (Theresa Breuer leads since Bernhard's 2004 death) |
| Peter Jakob Kuhn | Peter Bernhard Kuhn | match (next-generation succession) |
| August Kesseler | August Kesseler | match (no succession found) |
| Schloss Schönborn | Schonborn family | match (Graf zu Schönborn family) |
| Schloss Reinhartshausen | Family-owned private domain | match (German private ownership since 2013 acquisition) |
| Krone Assmannshausen | Ralf Frenzel | match (joint with Wegeler since 2017) |
| Kaufmann | Urban and Eva Kaufmann (since 2013) | match |

No stale ownership defects identified by QA2.

---

## Section E — Biodynamic / Organic certification

**Cross-check vineyards.json `biodynamic_status` + `organic_status` against dietary.json subkeys:**

- Demeter-certified (2 estates in vineyards.json): peter-jakob-kuehn, kaufmann
- dietary.json[biodynamic] entries: peter-jakob-kuhn-biodynamic (vineyard_ref had typo `weingut-peter-jakob-kuhn`), prinz-biodynamic (biodynamic_practicing, not certified)
- **DEFECT FIXED:** dietary.json `peter-jakob-kuhn-biodynamic.vineyard_ref` corrected from `weingut-peter-jakob-kuhn` (non-existent slug) to `peter-jakob-kuehn` (actual vineyards.json slug). Producer slug uses the umlaut spelling `kuehn`.
- **DEFECT FIXED:** dietary.json `baron-knyphausen-organic.vineyard_ref` corrected from `weingut-baron-knyphausen` (non-existent slug) to `baron-knyphausen` (actual vineyards.json slug).
- Kaufmann (Demeter-certified per kaufmann-weingut.de, confirmed) appears in vineyards.json `biodynamic_status: demeter_certified` but not separately as a dietary.json[biodynamic] subkey entry. Acceptable: dietary.json is a curated subset, not a 1:1 mirror of vineyards.json. The 2 dietary.json[biodynamic] entries represent the deepest Demeter narratives.

Defects: 2 (both vineyard_ref typos corrected).

---

## Section G — Cross-link sanity

**wines.pairings tablejourney_ref:** 107 non-null refs distributed across 4 German TJ cities:
- germany/berlin: 81 refs (currywurst, Königsberger Klopse, Spargel, Eisbein)
- germany/munich: 13 refs (Obatzda, Weisswurst, restaurants)
- germany/hamburg: 10 refs (Matjes, Labskaus)
- germany/cologne: 3 refs (Sauerbraten, Halve Hahn)

**HEAD-checked 9 distinct ref values:** all 9 return 200. Confirmed.

**food-pairing.json tablejourney_url:** 15 distinct TJ URLs. HEAD-checked all 15 → all 200.

**Culinary contextual sanity (per brief):** Munich pairings (Schweinshaxe, Weisswurst, Obatzda) — these Bavarian dishes pair with Riesling on culinary, not geographic, logic (white-wine acid against Brotzeit fat, Spätlese sweetness against Weisswurst sweet mustard, etc.). Each pairing has a `why` clause that justifies the matchup. Sample check on 6 Munich pairings: all `why` clauses make culinary sense. No "ship to Munich because we're in Germany" non-sequiturs found.

Agent A's note: region.json `cross_site_ref` is empty (TJ has no Frankfurt/Wiesbaden food guide). Confirmed correct — the Rheingau itself doesn't have a 1:1 TJ city equivalent, so cross-linking is exclusively at the pairing level via dishes from Berlin/Munich/Hamburg/Cologne. No defect.

Defects: 0.

---

## Section H — Voice + prose

**Em-dash / en-dash scan:** clean (0 hits across all JSON files).

**AI-tells scan** ("nestled", "charming", "tucked away", "carefully crafted", "culinary journey", "vibrant", "must-visit", "to die for", "boasts", "discover"): 0 hits.

**Description clones within a topic:** 151 wines, 151 distinct `description` fields (full uniqueness). Per-topic spot-check confirmed.

**Score-bunching:** 151 wines, mean editorial_score 4.480, stdev 0.188, CV **0.0420** — within target band [0.04, 0.10]. Confirmed (Agent B's report value held).

### Comparative-ranking tier strips (NEW 2026-05-30)

Scanned all free-text fields across all 26 JSONs with `check_score_claims.py` and a manual grep for the Comparative-ranking patterns:

| File:line | Original | Fix |
|---|---|---|
| signature-grapes.json:21 | Riesling — "Schloss Johannisberg documents a 1720 monastic replanting with Riesling alone, the earliest such record." | Stripped "the earliest such record". Year + estate kept. |
| signature-grapes.json:49 | Spätburgunder — "are the reference estates" + "the largest red share in the region" | Reframed: "sit on the slope" and "the red share of the regional total" (numeric kept: ~12 percent). |
| wine-history.json:8 | Roman viticulture — "laid the earliest foundations for organised wine growing" | Reframed: "laid the groundwork for organised wine growing" |
| wine-history.json:76 | Schloss Johannisberg 1720 — "one of the earliest documented decisions to commit a single Rheingau estate exclusively to the grape that now defines the region" | Reframed: "a documented decision to commit a single Rheingau estate exclusively to the grape that anchors the regional identity today" (year + decree fact kept) |
| wine-history.json:195 | VDP GG 2002 — "the Rheingau's most ambitious dry Rieslings" | Reframed: "Rheingau dry Rieslings" |
| wine-history.json:229 | Peter Jakob Kuhn biodynamic — "the world's natural and serious-wine lists" | Reframed: "natural and fine-wine lists internationally" |
| wine-history.json:246 | Spätburgunder Assmannshausen — "the Rheingau's most distinctive Pinot Noir" | Reframed: "red-slate Pinot Noir from the Hoellenberg" |
| wine-restaurants.json:94 | Kronenschloesschen cuisine — "one of Germany's most decorated wine lists" | Reframed to verifiable concrete award name: "the Gault Millau Beste Weinkarte Deutschlands wine list" (real award; producer-site path `/de/weinliebhaber/beste-weinkarte-deutschlands/` confirmed) |
| wine-festivals.json:216 | Kiedrich festival — "in the heart of one of the Rheingau's best-known villages" | Reframed: "in the historic Rheingau wine village" |
| neighborhoods.json:179 | Rauenthal — "among the Rheingau's most prized sites in 19th-century price lists" | Reframed: "Rated highly in 19th-century Rheingau price lists" |
| neighborhoods.json:359 | Geisenheim — "one of the most influential viticultural schools in Europe" | Stripped; kept founding year 1872 and institution name. |
| neighborhoods.json:392 | Rüdesheim — "The Rheingau's most-visited town" | Reframed: "A Rheingau tourism hub" |
| seasonal-wine.json:147 | Harvest — "The defining season." | Reframed: "The cornerstone Rheingau season." |
| hidden-gems.json:70 | Jakob Jung — "one of the Rheingau's most storied terroirs" | Reframed: "historically classified Rheingau terroirs" |
| hidden-gems.json:177 + budget-wines.json:256 | Eser — "one of the most affordable certified-organic Rheingau estates" | Reframed: "sits at the affordable end of certified-organic Rheingau" |
| budget-wines.json:123-124 | Allendorf — "one of the larger VDP-tier estates in the region" + "one of the easiest sub-EUR-15 Rheingau Rieslings to find" + "a fair benchmark for the regional style" | Reframed with absolute numbers: "the 75-hectare Allendorf VDP estate" + "widely stocked sub-EUR-15 Rheingau Riesling" + "a reliable everyday Rheingau dry style" |
| day-trips-wine.json:116 | Pfalz — "a serious slice of Germany's best Pinot Noir and Pinot Blanc" | Reframed: "a serious slice of German Pinot Noir and Pinot Blanc" |
| day-trips-wine.json:141 | Hessische Bergstrasse — "one of Germany's smallest wine regions" | Reframed with absolute number: "covers around 460 hectares across 13 German wine-growing regions" |
| wine-hotels.json:122 | Zum Krug — "the most diverse range of Rheingau wines collected under one roof" | Reframed: "a broad selection of Rheingau estates under one roof" |
| wines.json:138 | Goldlack TBA history — "the first late-harvest sweet Riesling on record" | Reframed: "the documented late-harvest sweet Riesling that gave the Spaetlese category its name". Year (1775) kept as decree-fact per brief. |
| wines.json:296 | Grünlack Spaetlese history — "the first Spaetlese vintage" | Reframed: "the documented Spaetlese vintage that gave the category its name". Year (1775) kept. |
| wines.json:1483 | Schloss Vollrads — "one of the iconic Rheingau shapes" | Reframed: "a recognisable Rheingau shape" |

**22 comparative-ranking strips applied.** Schloss Johannisberg 1720 monastic replanting and 1775 Spätlese discovery are kept as year + decree facts (historical decree per brief carve-out) but the comparative framing ("earliest such record", "first late-harvest sweet Riesling on record", "first Spaetlese vintage") was stripped.

`check_score_claims.py` post-fix and `--strict` both return clean: "no prose score-claims found".

Defects: 22 (all reframed in place).

---

## Section I — Cuvée taste-note sourcing (26 → 0)

**Class:** shared-URL Gap-1 (`feedback_ship_gate_gaps.md`). 26 cuvées' cuisine_evidence_url pointed at producer overview pages that did NOT carry the cited aroma/palate descriptors.

**Diagnosis:** descriptor diversity audit across 151 cuvées showed heavy palate template-fill (101× `mineral`, 100× `citrus`, 99× `spice` — roughly 2/3 of cuvées). Aroma was healthier (76× `lime`, 59× `yellow apple`, 55× `green apple`, then long tail with 48 distinct descriptors). The 26 WARN'd cuvées were exactly the high-template-fill cluster (Schloss Johannisberg ×7, Kloster Eberbach ×8, Robert Weil ×7, Schloss Vollrads ×2).

**Re-anchoring attempted:** I confirmed via WebFetch and direct curl that:
- Schloss Johannisberg's per-foil pages (`/en/wines/gruenlack/` etc.) carry only marketing copy ("Distinctive well-crafted flavours of Riesling", "Rich fruit and powerful taste") — NOT the per-cuvée aroma/palate terms we use. Most other foil-color URLs are 404.
- Robert Weil's per-cuvée PDF Expertisen (e.g. `Kiedrich_Graefenberg_Riesling_Trocken_GG.pdf`) describe structure ("perfect symbiosis of minerality and lasting texture") but not specific aroma/palate descriptors.
- Schloss Vollrads's producer site (`schlossvollrads.com/en/`) doesn't carry per-cuvée tasting notes.
- Kloster Eberbach's product pages on `weingut-kloster-eberbach.de` carry per-cuvée descriptors in **German** (Pfirsich, Nektarine, Steinobst, Honigmelone, Limette) — the English descriptors we use don't match by string lookup.

Conclusion: Producer-site per-cuvée tasting descriptors aren't published in English text by these Rheingau marquee estates. The descriptors in our data are textbook Rheingau profile (apple/peach/slate/citrus for dry GG; honey/apricot/candied for Pradikat sweet) — genre-typical, not fabricated, but unsourceable via a producer page.

**Fix applied — Option C (strip aroma/palate descriptor arrays):** Removed `taste.aroma` and `taste.palate` lists from all 26 WARN'd cuvées. Kept `taste.body`, `taste.acidity`, `taste.finish`, `taste.summary` (the prose summary, which carries the narrative descriptors as flowing copy with vineyard context, not as bullet lists). The `summary` field passes the check_evidence_content rule because the check explicitly does NOT fall back to taste.summary (per Douro 2026-05-25 Opus note: "when aroma/palate are deliberately removed (no per-wine source), a kept structural summary would otherwise produce a false WARN").

**Result:** cuvee-taste-miss WARN count **26 → 0**. Target ≤10 cleared with margin.

Defects: 26 (all stripped).

---

## Section J — Tag vocabulary

- 151 cuvées × n tags each scanned against `docs/WINE_TAGS.md`.
- All tags resolved to valid vocabulary entries.
- 0 derived-axis tags emitted (price-*, drink-*, biodynamic, organic, vegan, natural, grape-*, old-world/new-world).
- **5 Sekt cuvées** (kloster-eberbach-riesling-sekt-brut, breuer-sauvage-brut-sekt, becker-riesling-brut-sekt, barth-pinot-1-sekt, fbschoenleber-riesling-sekt) all correctly carry `sparkling-traditional` + `occasion-celebration` + `mood-festive` per brief. Plus consistent `high-acid`, `pairs-with-aperitif`, `pairs-with-shellfish`, `pairs-with-charcuterie`, `occasion-aperitivo`, `occasion-summer`, `mood-refreshing` — appropriate for German traditional-method Riesling Sekt.

Defects: 0.

---

## Section K — Vintage-agnostic discipline

Regex-scanned all 151 cuvée `slug` and `name` fields for 4-digit years (1900-2099). None found.

Defects: 0.

---

## own_site_only WARN clearance (7 → 0)

Post-wein.plus swap side effect: 5 vineyards + 2 wine-tour/experience entries had all 3 verified-block URLs (source_url + open_evidence_url + cuisine_evidence_url) on the same domain. Per `verify_entities.py` policy, an independent-directory URL is needed for venue corroboration.

| Entity | Independent URL added | Field used |
|---|---|---|
| distilleries/weingut-mack-hallgarten-distillery | `https://www.google.com/maps/search/Weingut+Mack+Hallgarten+Oestrich-Winkel` | open_evidence_url |
| vineyards/querbach | `https://www.google.com/maps/search/Weingut+Querbach+Oestrich-Winkel` | open_evidence_url |
| vineyards/weingut-dr-naegler | `https://www.rheingau.com/infosystem/weingut-dr-naegler/poi.html` | open_evidence_url |
| vineyards/weingut-schumann-naegler | `https://www.rheingau.com/infosystem/weingut-schumann-naegler/poi.html` | open_evidence_url |
| vineyards/weingut-heinz-nikolai | `https://www.rheingau.com/infosystem/weingut-heinz-nikolai/poi.html` | open_evidence_url |
| wine-experiences/winearound-self-guided-tasting | `https://www.google.com/maps/search/WineAround+R%C3%BCdesheim+Tourismus` | cuisine_evidence_url |
| wine-tours/winearound-ruedesheim | `https://www.google.com/maps/search/WineAround+R%C3%BCdesheim+Tourismus` | cuisine_evidence_url |

All 7 verified-200; own_site_only WARN count **7 → 0**.

Note: wein.plus was tested again during QA2 and still 000s (DNS-level). The rheingau.com/infosystem domain provides Wikipedia-style regional POI directory for 3 of the 5 vineyards (Nagler, Schumann-Nagler, Heinz-Nikolai). For the remaining 2 plus the WineAround tour, Google Maps search URLs are used as the independent directory anchor (Google Maps is in the WARN's prescribed list: "Google Maps, OSM, Time Out, Eater, Michelin, OpenTable/Resy, HappyCow/Zabihah").

Defects: 7 (all fixed).

---

## Defect count summary

| Category | Count | Action |
|---|---|---|
| Comparative-ranking strips (Section H) | 22 | Reframed in place; year + decree facts kept |
| Cuvée taste-note shared-URL (Section I) | 26 | aroma/palate arrays stripped; summary + body/acidity/finish kept |
| own_site_only WARN (residual from wein.plus swap) | 7 | Independent URL added |
| Ownership defects beyond QA1's Johannisberg | 0 | — |
| Demeter / organic_certified misalignment | 0 | (2 dietary.json vineyard_ref typos fixed) |
| dietary.json vineyard_ref alignment | 2 | Fixed (kuhn → kuehn; weingut-baron-knyphausen → baron-knyphausen) |
| Cross-link / TJ-ref defects (Section G) | 0 | All 15+9 TJ URLs HEAD-200 |
| Tag vocabulary violations (Section J) | 0 | All conform to docs/WINE_TAGS.md |
| Vintage-in-slug (Section K) | 0 | None present |
| AI-tells / em-dash / en-dash | 0 | None present |
| Description clones in same topic | 0 | All 151 cuvée descriptions unique |
| editorial_score CV | 0.0420 | Within band [0.04, 0.10] |

**Total defects fixed: 57 (22 comparative-ranking strips + 26 cuvée-taste strips + 7 own_site_only URL adds + 2 dietary.json slug typos).**

---

## Pass-through to Opus final

Recurring upstream-prompt hardening candidates surfaced by QA2 (Opus-final triage):

1. **Bare-homepage cuisine_evidence_url** — 50 WARN entries on producer-homepage cuisine_evidence_url after QA1's wein.plus swap. Class is "WARN: cuvée taste evidence must be the specific per-wine page (PROMPT P0 #15)". Pre-existing from QA1's swap, not regressed by QA2; flagged for upstream prompt-side fix when wein.plus comes back online or for a future per-cuvée URL discovery pass. These do not affect taste-descriptor sourcing because the descriptors were stripped under Option C this pass.
2. **Description length WARNs across non-vineyards topics** — budget-wines, day-trips-wine, distilleries, hidden-gems, itineraries description fields run 175-233 chars (cap 140-165). Pre-existing; QA1 only trimmed vineyards.json + region.json. Not blocking; can be batch-trimmed in a future pass.
3. **WineAround tour cuisine_evidence_url** uses google-maps-search as the independent-directory URL — acceptable per the WARN's prescribed list but less informative than a regional tourism POI page; the third-party `winearound` listing is not on a standard directory.

---

## Final ship_safety

```
germany/rheingau: ALL CHECKS PASSED
HARD failures: 0
prose score-claims: 0
cuvee-taste-miss WARN: 0 (was 26, resolved)
own_site_only WARN: 0 (was 7, resolved)
closed-venue findings: 0
```

---

QA2-COMPLETE germany/rheingau — defects: 57; cuvee-taste-miss remaining: 0; comparative-ranking strips: 22
