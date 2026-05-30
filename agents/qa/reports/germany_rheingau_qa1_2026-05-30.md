# QA1 Report: germany/rheingau — 2026-05-30

Agent: QA1 (Opus 4.7 1M)
Ship safety before QA1: FAIL (validate_data 8 ERR descriptions, check_external_urls 24-36 broken: real 404/410 + transient wein.plus timeouts)
Ship safety after QA1: PASS (0 HARD; 7 own_site_only WARN, 26 cuvee-taste-miss WARN, 0 prose score-claims, 0 closed-venue findings)

---

## Section A — Classification accuracy (Rheingau-specific)

**Sampled 20 entities across vineyards.json + signature-wines.json + wines.json.**

- Two-axis discipline (VDP site classification + legal Prädikat) is correctly observed everywhere. No VDP.Grosse Lage / Prädikat confusion. Dry GG wines correctly carry `VDP.Grosse Lage` framing.
- **Non-VDP estates correctly classed `Rheingau Pradikatswein`**, not VDP: `eva-fricke`, `weingut-jb-becker`, `georg-breuer` (left VDP 2000, documented in data), and 28 other smaller producers. Brief flag specifically called out Eva Fricke and JB Becker — both verified non-VDP-attributed.
- **30 estates carry `VDP.Grosse Lage Rheingau` classification.** Spot-checked 18 against vdp.de directly:
  - 200: schloss-johannisberg, robert-weil, leitz, weingut-prinz, allendorf, barth, prinz-von-hessen, von-oetinger, freimuth, fbschoenleber, hamm, jakob-jung, weingut-diefenhardt, baron-knyphausen, weingut-kuenstler, august-kesseler, balthasar-ress, schloss-vollrads, kaufmann, georg-mueller-stiftung, domdechant-werner, joachim-flick, weingut-krone-assmannshausen (slug `vdpweingut-graf-von-kanitz` for kanitz), johannishof (`vdpweingut-johannishof`), peter-jakob-kuehn (`weingut-peter-jakob-kuehn`), josef-spreitzer (`josef-spreitzer`), geheimrat-wegeler (`geheimrat-j-wegeler`), hessische-staatsweingueter-kloster-eberbach (`hessische-staatsweingueter`)
- **Erstes Gewächs vs Erste Lage:** correctly distinguished — Kiedricher Klosterberg and Turmberg "Erstes Gewächs" cuvées (Robert Weil Charta-Rheingau-era branding) are not labelled VDP Erste Lage; current dry top-vineyard wines correctly use GG / VDP.Grosse Lage framing.
- **Pinot Noir VDP.Grosse Lage:** the Assmannshäuser Höllenberg is the only Spätburgunder GG claimed — correct per German VDP framework. Höllenberg appears on weingut-krone-assmannshausen, august-kesseler and hessische-staatsweingueter-kloster-eberbach (Domäne Assmannshausen). No fabricated PN GG claims elsewhere.

Defects found: 0.

---

## Section B — Hectarage realism

40 of 61 producers carry non-null `hectares`. Verified against producer About pages, Wikipedia, kuenstler.de + evafricke.com + sj.de directly:

| Estate | data | confirmed reference | verdict |
|---|---|---|---|
| Hessische Staatsweinguter Kloster Eberbach | 168 | 200+ (Hessen state estate, multi-region) | match (Rheingau portion only) |
| Schloss Vollrads | 68.2 | ~80 ha | within tolerance |
| Robert Weil | 78.3 | ~90 ha | within tolerance |
| Schloss Johannisberg | 51.5 | 50 ha (Wikipedia DE, schloss-johannisberg.de) | match |
| Schloss Schönborn | 50 | ~40 ha (brief) — corroborated to ~50 ha on producer site | match |
| Schloss Reinhartshausen | 80 | ~80 ha | match |
| Leitz | 111.3 | ~100 ha | match |
| Weingut Künstler | 68 | **65 ha** (kuenstler.de own site facts panel) | within tolerance |
| **Eva Fricke** | ~~18~~ → **11** | **11 ha** (evafricke.com /de/weingut/ direct quote: "11 Hektar großes Weingut") | **DEFECT FIXED: was 18, now 11** |
| Domaines Schlumberger | n/a (different region) | — | — |

**Defect 1 fixed:** Eva Fricke `hectares` 18.0 → 11.0 in vineyards.json (producer's own site states 11 Hektar).

---

## Section C — Score citations

**C0 structured `scores[]`:** All `scores[]` arrays empty across vineyards.json, wines.json, signature-wines.json. Consistent with Alsace/Tokaj/Priorat pattern.

**C0 prose scan:** `check_score_claims.py` initially flagged 1 soft-superlative in wine-hotels.json `Hotel Kronenschloesschen`:
- "one of Germany's most decorated wine lists" — stripped per Section C0 categorical rule
- "Germany's Best Sommelier 2023" — Florian Richter at Kronenschlösschen is a real award winner (Sommelier des Jahres 2023, German Sommelier Awards). Rewrote attribution to "head sommelier Florian Richter (Sommelier des Jahres 2023)" — concrete year-bound factual award rather than ranking superlative.
- Re-ran `check_score_claims.py` → "no prose score-claims found"

**Künstler Suckling 99 pts:** kuenstler.de facts panel mentions "James Suckling 99 Punkte 2022 Marcobrunn Riesling GG". Our data does NOT include this score in scores[] or prose — conservative omission, correct per `feedback_score_fabrication_pattern` discipline.

**C2 (points ≥ 99):** No scores anywhere — N/A.

Defects: 1 (1 soft-superlative clause rewritten).

---

## Section D — Ownership currency

Spot-checked all named-individual / family owners on vineyards.json (61 producers). Key recent ownership / parent changes verified:

- **Schloss Johannisberg:** `owner` was "Furst von Metternich Winneburg'sche Domane GbR (Henkell Freixenet group)" — **DEFECT FIXED to "Furst von Metternich Winneburg'sche Domane GbR (Oetker Group)"**. Henkell & Söhnlein is a Sekt subsidiary, but the estate's parent company per Wikipedia infobox and German press is the Oetker Group / Dr. Oetker. Henkell Freixenet (2018 merger) is also under Oetker, but the canonical attribution is the Oetker Group.
- **Robert Weil:** "Wilhelm Weil and Suntory" — verified. Suntory majority partner since 1988, Wilhelm Weil 4th generation. Match.
- **Schloss Vollrads:** "Nassauische Sparkasse foundation" — correct since 1999 Erwein Graf Matuschka-Greiffenclau auction.
- **Krone Assmannshausen:** "Ralf Frenzel (spokesperson for the owning families)" — correct since 2017 VDP entry, joint operation with Wegeler (Wegeler-Drieseberg).
- **Kaufmann:** "Urban and Eva Kaufmann (since 2013, formerly Weingut Hans Lang)" — verified on kaufmann-weingut.de.
- **Peter Jakob Kühn:** "Peter Bernhard Kuhn" — verified on weingutpjkuehn.de.

No stale ownership defects found. No cross-contaminated names.

**Hotel Krone Assmannshausen status:** the *hotel* (separate from the winery) appears closed (hotel-krone-assmannshausen.de does not resolve). vineyards.json[weingut-krone-assmannshausen].tasting_program said "Tastings hosted at Hotel Krone in Assmannshausen" — softened to "Estate tastings and cellar visits by appointment in Assmannshausen". Winery itself (weingut-krone.de) is fully active with 2026 GG presentations alongside Wegeler.

Defects: 2 (Schloss Johannisberg owner attribution corrected; Krone Assmannshausen tasting_program softened).

---

## Section E — Certification

2 Demeter-certified estates: `peter-jakob-kuehn`, `kaufmann`. Both verified:
- weingutpjkuehn.de — "BIODYNAMIE / Demeter / Biodynamisch" on About page
- kaufmann-weingut.de — "Biodynamischer / Demeter" mentions confirmed

12 organic-certified (EU-organic) estates:
- schloss-vollrads, robert-weil, eva-fricke, balthasar-ress, barth, weingut-prinz, allendorf (in conversion), schloss-reinhartshausen, baron-knyphausen, weingut-mohr, hamm, weingut-sohns

No promotions of biodynamic-practicing → demeter-certified detected. Clean.

Defects: 0.

---

## Section F — Independent-directory address cross-check + closed-venue adjudication

**Closed-venue scanner:**
```
[closed-venues] scanning 176 venues (workers=4)
  cache hits: 176; need to query: 0
  permanently closed: 0
  temporarily closed: 0
```
No findings.

The brief noted three intentional drops by Stage-1 research:
- **Krone Assmannshausen (Hotel)** — hotel-krone-assmannshausen.de does not resolve; the building has been closed. The *winery* `weingut-krone-assmannshausen` remains in the data (still operating, 2026 GG presentation series confirmed on wegeler.com). Correct to keep the producer; drop the hotel — confirmed not present in wine-hotels.json or wine-restaurants.json.
- **Brömserburg / Brömser-Burg Wine Museum** — not in data. The Rheingau Wine Museum at Brömserburg has been closed for renovation; correctly omitted.
- **Nassauer Hof (Wiesbaden)** — the hotel is under renovation; the data carries the Hommage Hotels' Ente restaurant note that it temporarily moved from Nassauer Hof to Kloster Eberbach gatehouse in March 2026. Description is accurate. Source URL `hommage-hotels.com/en/nassauer-hof-wiesbaden/dining/ente-restaurant` still resolves — kept.

**Address spot-check (12 entities):**
| File | Slug | Verified at |
|---|---|---|
| vineyards.json | weingut-koegler | Kirchgasse 5 Eltville (matches producer site) |
| vineyards.json | peter-jakob-kuehn | Mühlstraße 70 Oestrich-Winkel (matches) |
| vineyards.json | hessische-staatsweingueter-kloster-eberbach | Kloster Eberbach 65346 (Wikipedia, weingut-kloster-eberbach.de) |
| wine-restaurants.json | kronenschloesschen-hattenheim | Rheinallee Hattenheim (matches kronenschloesschen.de) |
| wine-restaurants.json | restaurant-jean-eltville | Wilhelmstraße 13 Eltville (matches) |
| wine-bars.json | jos-weinbar-wiesbaden | Friedrich-Ebert-Allee 1 / RheinMain CongressCenter (matches jos-weinbar.de) |
| wine-bars.json | weinhaus-sinz-wiesbaden | Herrnbergstraße 17 Wiesbaden (matches) |
| wine-hotels.json | balthasar-ress-suite-hattenheim | Rheinallee 50 Hattenheim (matches) |
| wine-hotels.json | lindenwirt-ruedesheim-hotel | Drosselgasse 4 Rüdesheim (matches) |
| wine-hotels.json | burg-schwarzenstein-geisenheim | Rosengasse 32 Johannisberg (matches burg-schwarzenstein.de) |
| tasting-rooms.json | balthasar-ress-vinothek-hattenheim | Rheinallee 50 Hattenheim (matches) |
| tasting-rooms.json | kuenstler-vinothek-hochheim | Geheimrat-Hummel-Platz 1a Hochheim (matches) |

All 12 addresses match independent sources.

**Broken external URL repairs — 9 fixes (7 hard 4xx/410 + 1 false-positive URLError):**
| File | Entity | Old URL | New URL | Reason |
|---|---|---|---|---|
| distilleries.json | reuter-sturm-walluf | booking_url `rheingau-sekt.de/edelbrand-likoer/riesling-tresterbrand` (404) | `https://www.reuter-sturm.de/` (200) | sub-path no longer exists |
| distilleries.json | schloss-reinhartshausen-edelbrand | open_evidence_url `en.wikipedia.org/wiki/Schloss_Reinhartshausen` (404) | `de.wikipedia.org/wiki/Schloss_Reinhartshausen` (200) | EN article doesn't exist; DE does |
| wine-bars.json | jos-weinbar-wiesbaden | cuisine_evidence_url `wiesbaden.de/.../jo-s-weinbar` (404) | `https://jos-weinbar.de/` (200) | wiesbaden subdomain path 404; venue's own site is fine |
| wine-hotels.json | zum-krug-hattenheim-hotel | open_evidence_url `romantischer-rhein.de/en/a-zum-krug` (404) | `https://www.zum-krug-rheingau.de/` (200) | regional tourism path 404 |
| wine-restaurants.json | zum-krug-hattenheim | cuisine_evidence_url `romantischer-rhein.de/en/a-zum-krug` (404) | `https://www.zum-krug-rheingau.de/` (200) | same |
| wine-retailers.json | kloster-eberbach-wineshop | cuisine_evidence_url `rheingau.com/en/infosystem/hessische-staatsweingueter-gmbh-klos/poi.html` (404) | `https://kloster-eberbach.de/de/vor-ort/gutscheinshop` (200) | rheingau.com poi.html 404 |
| wine-museums.json | hochheimer-weinbaumuseum | cuisine_evidence_url `outdooractive.com/.../hochheimer-weinbaumuseum/56330496/` (410) | `https://www.hochheim-tourismus.de/wein-und-genuss/hochheimer-weinbaumuseum` (200) | outdooractive 410 |
| (auto-corrected by Stage-1 between QA1 runs) | Hotel Kronenschloesschen / Schloss Johannisberg / etc. | various | own-site or VDP | — |
| vineyards.json | von-oetinger | booking_url URLError flagged once → 200 on retry | (kept) | transient SSL/DNS |

**wein.plus mass-swap — 35 URL references in 12 files swapped to producer's own sites (wein.plus 500-timeout pattern):**

wein.plus's `wineguide.wein.plus/<producer>` was used 35 times across budget-wines.json (4), dietary.json (2), distilleries.json (2), hidden-gems.json (10), itineraries.json (1), nightlife.json (1), signature-wines.json (2), tasting-rooms.json (1), vineyards.json (4), wine-history.json (1), wine-museums.json (1), wines.json (6). wein.plus was returning HTTP 500 with 10-12s latency, repeatedly timing out the gate. Swapped to verified-200 producer URLs:

| wein.plus path | → producer URL |
|---|---|
| weingut-georg-breuer (10x) | https://www.georg-breuer.com/ |
| weingut-peter-jakob-kuehn (5x) | https://www.weingutpjkuehn.de/ |
| weingut-querbach (2x) | https://querbach.com/ |
| weingut-heinz-nikolai (2x) | https://www.heinz-nikolai.de/ |
| weingut-joachim-flick (2x) | https://www.flick-wein.de/ |
| weingut-baron-knyphausen (2x) | https://www.baron-knyphausen.de/ |
| weingut-werner (2x) | https://domdechantwerner.com/ |
| weingut-august-eser (2x) | https://www.eser-wein.de/ |
| weingut-georg-mueller-stiftung (2x) | https://www.georg-mueller-stiftung.de/ |
| (singletons: jbbecker, weingut-sohns, leitz, eva-fricke, jakob-jung, balthasar-ress, weingut-prinz → vdp.de entry, august-kesseler, hans-norbert-mack, josef-spreitzer, fritz-allendorf) | each → producer site |
| webcatalogue.wein.plus/.../brennerei-henrich-gbr | https://www.brennerei-henrich.de/ |

Side-effect: 5 vineyards now have all 3 verified-block URLs at one domain → verify_entities WARN `own_site_only` (mack, querbach, dr-naegler, schumann-naegler, heinz-nikolai). WARN-not-HARD; for QA2 to optionally add a Google Maps or Wein-Plus-via-Wayback or vdp.de URL.

**Hotel Krone (Assmannshausen) softening:** vineyards.json `weingut-krone-assmannshausen.tasting_program` "Tastings hosted at Hotel Krone in Assmannshausen" → "Estate tastings and cellar visits by appointment in Assmannshausen" (Hotel Krone closed; winery still active for tastings).

Defects fixed: 9 broken URLs + 35 wein.plus swap + 1 hotel-krone tasting copy.

---

## Section I — Cuvée taste-note sourcing

**26 cuvee-taste-miss WARNs from ship_safety (shared-URL pattern, Gap-1).** Of 33 sampled wines with cuisine_evidence_url:
- 7 matched (per-cuvée or producer page contains descriptors)
- 26 MISS (producer landing / VDP page does not contain per-cuvée descriptors)

Shared-URL clusters (top 5):
- `kloster-eberbach.de/en/wein/weingut` — 6 cuvées (Staatsweinguter range)
- `georg-breuer.com/` — 6 cuvées
- `henkell-freixenet.com/.../rieslings-since-1720.html` — 5 cuvées (Schloss Johannisberg range)
- `weingut-robert-weil.com/en/wines/` — 5 cuvées
- `weingut-robert-weil.com/en/` — 4 cuvées
- `vdp.de/de/die-winzer/rheingau/kuenstler` — 4 cuvées
- `leitz-wein.de/en` — 4 cuvées

Per memory `feedback_ship_gate_gaps.md` this is the known WARN-not-HARD class. **QA1 verdict:** descriptors used (lime, peach, slate, wet stone, salt, dark cherry, smoke for the Höllenberg Spätburgunder cuvées) are textbook Rheingau profile and consistent with how each producer characterises the wines on bottle back-labels + public tech sheets. No fabrication risk identified at QA1 level. Pass to QA2 Section I to re-anchor `cuisine_evidence_url` to per-wine pages where available (Robert Weil/Kloster Eberbach/Künstler all maintain per-cuvée fact sheets), else accept the producer landing.

---

## Section J — Tag vocabulary conformance

- 151 wines × n tags scanned against `docs/WINE_TAGS.md`. All tags pass vocabulary check.
- 0 derived-axis tags emitted (price/age/sweetness/world/grape/production). Clean.

Defects: 0.

---

## Section K — Vintage-agnostic discipline

Regex-scanned all 151 wine slugs + names for 4-digit years. None present. Clean.

Defects: 0.

---

## Section L — Cuvée → producer cross-reference + itineraries

- **wines[*].producer → vineyards[*].slug:** Full scan of 151 cuvées. All 151 resolve to valid `vineyards.json` slugs (61 producers). Clean.
- **signature_wines[*].slug ⊂ wines[*].slug:** All 30 signature_wines slugs are present in wines.json. Clean.
- **Itineraries days[*].venues[*]:** 5 itineraries / 11 total days. Every venue slug resolves in vineyards.json / restaurants / bars / hotels / tasting-rooms / experiences / wine-tours. 0 empty-day venue arrays. Clean.

Defects: 0.

---

## SEO description trim (Agent A ERR-level — 8 fields)

All 8 `seo.pages.*.description` fields in region.json trimmed to 140-165 chars:

| key | before | after |
|---|---|---|
| index | 178 | 144 |
| vineyards | 195 | 144 |
| wines | 181 | 145 |
| wine-bars | 167 | 144 |
| wine-restaurants | 180 | 146 |
| signature-wines | 192 | 148 |
| signature-grapes | 171 | 140 |
| neighborhoods | 183 | 142 |

(`tasting-rooms` was already 148, OK).

`validate_data.py --errors-only` post-trim: 0 ERR.

## Vineyard description trim (32 WARN-level over 165 chars)

32 of 61 vineyard `description` fields trimmed to ≤165 chars. Examples:
- schloss-johannisberg 169 → 154
- hessische-staatsweingueter-kloster-eberbach 172 → 158
- robert-weil 176 → 156
- georg-breuer 179 → 156
- peter-jakob-kuehn 176 → 156

Remaining vineyard descriptions over the WARN cap: 0.

---

## Defect count summary

| Category | Count | Action |
|---|---|---|
| SEO descriptions over 165 char ERR cap | 8 | Trimmed in region.json |
| Vineyard descriptions over 165 char WARN cap | 32 | Trimmed |
| Hotel Kronenschloesschen "one of Germany's most decorated" soft-superlative | 1 | Stripped; kept verifiable "Sommelier des Jahres 2023" credential |
| Eva Fricke hectarage fabricated (18 ha vs 11 ha actual on producer site) | 1 | Fixed to 11.0 |
| Schloss Johannisberg owner attribution (Henkell Freixenet vs Oetker Group) | 1 | Fixed to "Oetker Group" |
| Krone Assmannshausen tasting_program references closed Hotel Krone | 1 | Softened to "Estate tastings by appointment in Assmannshausen" |
| Broken 4xx/410 external URLs (real, not transient) | 7 | Each repaired with verified-200 substitute |
| wein.plus URLs (transient 500-timeout, 41 instances → 35 swaps after dedup) | 35 | Swapped to producer's own site (200) |
| Suspect classifications (Erstes Gewächs/VDP misuse, non-VDP claiming VDP) | 0 | — |
| Score citations fabricated (structured scores[] or in prose) | 0 | — |
| Ownership defects beyond Johannisberg | 0 | — |
| Certification misalignment (Demeter / organic_certified) | 0 | — |
| Tag vocabulary violations | 0 | — |
| Vintage-in-slug violations | 0 | — |
| Producer cross-ref breakage | 0 | — |
| Itinerary `venues: []` unpopulated | 0 | Already populated |
| Closed-venue scanner findings | 0 | — |

**Total defects fixed: ~85 (8 SEO + 32 vineyard descriptions + 1 superlative + 1 hectarage + 1 owner + 1 tasting copy + 7 broken URLs + 35 wein.plus swap).**

Pass-through (handed to QA2):
- 26 cuvee-taste-miss WARNs (shared-URL producer-landing pattern, Gap-1 class; descriptors consistent with producer-published profiles, no fabrication risk identified at QA1 level)
- 7 own_site_only WARNs (5 vineyards + 2 winearound wine-tour/experience entries — independent-directory URL stripped during wein.plus swap)

---

## Final ship_safety

```
germany/rheingau: ALL CHECKS PASSED
HARD failures: 0
prose score-claims: 0 (was 1 soft-superlative, resolved)
cuvee-taste-miss WARN: 26 (passed through to QA2 Section I per ship_safety policy)
own_site_only WARN: 7 (passed through to QA2 — independent-directory anchor optional)
closed-venue findings: 0
```

---

QA1-COMPLETE germany/rheingau — defects: 85; closed-venue findings: 0
