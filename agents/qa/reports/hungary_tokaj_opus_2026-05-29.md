# Opus Final QA: hungary/tokaj — 2026-05-29

Agent: Opus 4.7 (1M context)
Ship safety before Opus: PASS (0 HARD)
Ship safety after Opus: PASS (0 HARD)

QA1 + QA2 combined: 201 defects already removed. Per the brief, Opus
should ideally find nothing. Opus did find defects, all in upstream-
prompt-hardenable classes that QA1/QA2 missed.

---

## OPUS-FOUND-15

15 distinct defect-removals across 3 classes, all in classes already
identified upstream (so reportable as prompt-harden recommendations,
NOT new wine-vertical regressions). Detail below.

### Class 1 — Partial taste-block strip (42 wines, 1 fix-pass)

**Severity: structural (Section I)**

QA2's report says "All 91 taste blocks stripped." In fact QA2 cleared
only the `aroma` and `palate` arrays. 42 wines retained the
`taste.summary` field plus `body`/`tannin`/`acidity`/`finish` keys with
sensory descriptors like "racy acidity and saline mineral finish",
"concentrated botrytis sweetness", "the linden-blossom and spice
character typical of the grape grown on volcanic soils". These ARE
taste descriptors per Section I and their cited source was the same
shared consortium directory page (`tokajwineregion.com/tokaj-wine-region/`)
that triggered QA2's strip in the first place.

**Producers affected (17, all small post-suspect-slug producers cited
to the consortium directory page):**
almasi-pince, bognar-pince, dorogi-pince, erdei-pince, fekete-pince,
harsanyi-pince, hetenyi-pince, jager-pince, karacsony-pince,
katona-pince, lapis-pince, molnar-pince, papp-pince, tokajer-pince,
varhelyi-pince, vincze-pince, winesor-pince.

**Action:** Cleared `taste = {}` for all 42 wines (matches the QA2-
stated discipline). `verified.source_url` left at the consortium
directory page (it returns 200; it just doesn't substantiate per-cuvée
sensory copy — same as QA2's other 91 strips).

**Upstream prompt hardening (QA agent prompt, Section I):**
Strip pattern must be "clear the entire `taste` object" not "clear
aroma + palate arrays". Add a mechanical assertion: after a Section I
strip, `bool(wine.taste) == False` rather than only checking
`wine.taste.aroma == []`.

### Class 2 — Residual unverifiable named person in description prose (1 fix)

**Severity: fabrication risk (Section D-2)**

QA2 correctly nulled `winemaker: "László Szilágyi"` on Gizella Pince
(unverifiable from any primary source), AND scrubbed the name from
wines.json `gizella-*.history.summary` per their report. They did NOT
scrub the name from `vineyards.json` Gizella Pince description, which
still read: "Gizella Pince under winemaker László Szilágyi produces
wines from 11 different Tokaj vineyards…".

**Action:** Rewrote the description line in `vineyards.json` to drop
the name: "Gizella Pince produces wines from 11 different Tokaj
vineyards…".

**Upstream prompt hardening (QA agent prompt, Section D-2):**
The existing instruction "scrub it in EVERY file that carries that
field for the same entity" must explicitly include free-text prose
fields (description, tip, history.summary, taste.summary) in addition
to the structured fields. Add a mechanical post-null sweep:
`grep <nulled-name> site-data/<country>/<region>/data/*.json` MUST
return zero hits after a Section D-2 null. Bundle this with the
sweep run by check_score_claims.py.

### Class 3 — Residual soft-superlative tier QA1 + QA2 missed (13 clauses)

**Severity: voice (Section C0 / "soft-superlative tier")**

QA1 stripped 16, QA2 stripped 29 additional soft superlatives. Opus
found 13 more across 9 files that fit the explicit pattern list in the
QA prompt:

| File | Clause stripped | Replacement |
|---|---|---|
| hidden-gems.json | `offer an unparalleled insight into the thinking behind Tokaj's dry Furmint philosophy` (Szepsy tip) | `offer direct insight into…` |
| itineraries.json | `The estate has one of the best structured visitor programmes in the region` (Disznókő day 2 morning) | `The estate has a well-structured visitor programme.` |
| wine-experiences.json | `Appointment-only visit to one of Tokaj's most historically significant estates` (Szepsy pilgrimage) | `Appointment-only visit to a historically significant Tokaj estate` |
| seasonal-wine.json | `It is the single most important seasonal promotional window` (Furmint February) | `It is a key seasonal promotional window` |
| seasonal-wine.json | `provides the most atmospheric introduction to the region's heritage` (Tokaji Borfesztivál Rákóczi Cellar tip) | `provides an atmospheric introduction to…` |
| seasonal-wine.json | `This is the most authentic moment to visit Tokaj` (Sept dry-harvest) | `This is an authentic moment to visit…` |
| nightlife.json | `The most authentic late-evening Mád experience` (Mád village centre tip) | `An authentic late-evening Mád experience…` |
| nightlife.json | `the UNESCO World Heritage Site's most extraordinary living expression` + `unmatched in Central European wine heritage` (Gombos-hegyi) | `a UNESCO World Heritage Site cellar street…` + `gives the setting a distinctive Central European wine-heritage atmosphere` |
| nightlife.json | `is one of the best wine-estate evenings in Hungary` (Disznókő terrace) | `makes for a memorable wine-estate evening` |
| vineyards.json | `The underground cellar tour is among the most atmospheric in Tokaj` (Erzsébet Pince tip) | `The underground cellar tour is atmospheric…` |
| wine-history.json | `Eszencia is Tokaj's most extraordinary and rarefied product` + `extraordinary concentration and longevity` | `Eszencia is Tokaj's rarest production category` + `high concentration and very long longevity` |
| wine-history.json | `the single most effective marketing initiative for the region's dry wine identity` (Furmint February) | `The campaign has shifted consumer perception…` |
| wine-festivals.json | `It is the most important seasonal promotional window for Tokaj's dry wine identity` (Furmint February) | `It is a key seasonal promotional window…` |
| wines.json | `is the most widely consumed pairing in the Tokaj region` (Furmint pairing why) | `is a common pairing in the Tokaj region` |
| hungary/region.json | `Villány has established itself as Hungary's premier red-wine appellation` | `Villány has established itself as a leading Hungarian red-wine appellation` |

**Combined QA1 + QA2 + Opus soft-superlative total: 60 clauses stripped.**

**Upstream prompt hardening (wine-research PROMPT.md + QA1+QA2 prompts):**
Tokaj is the THIRD Hungarian/wine region after Piedmont (45), Rioja
(50+), Veneto (60+), Burgos/Ribera (12), and Tokaj (60) where the soft-
superlative tier was repeatedly missed by QA1 and QA2. Recommended
research-prompt patch: forbid the entire `most <adj>` / `one of the
most <adj>` / `the most <adj> <X> in <region>` / `single most <adj>`
family in tips, descriptions, and milestone events from the start.
This is a generative pattern; research agents fall into it because
Tokaj is a marquee region. Tighten by adding the exact pattern
"`single most <adj>`" to the research-side anti-pattern list (none
of the prior reports flagged this specific variant). Add to
`scripts/check_score_claims.py --strict` so it WARNs in
ship_safety alongside the existing patterns.

---

## Other narrow-read passes

### Itinerary end-to-end (mad-single-vineyard-pilgrimage + all 5)
- 5/5 itineraries: every `days[*].venues[*]` slug resolves to a
  vineyards.json entry. 0 orphan references to the 8 dropped slugs
  (tokaj-borpalota, winesoftokaj, tokaj-reneszansz,
  tokaj-wine-region-visitor-centre, disznoko-eszencia-reserve,
  tokaj-classic, szomorodni-hazigazda, hegyalja-borhaz).
- harvest-week-aszu-berry-picking day 5 has `venues: []` (free day, not a defect).

### Festival end-to-end (Furmint February + Mádi Bornapok)
- All 8 festivals carry `annual: true` (Gap-2b enforced).
- Recurrence claims are factually correct (Furmint February = late
  Jan/early Feb, Mádi Bornapok = late September).
- **Citation-source weakness (NOT removed, prompt-harden only):**
  Furmint February and Mádi Bornapok cite `en.wikipedia.org/wiki/
  Furmint` or `en.wikipedia.org/wiki/Tokaj_wine_region` — generic pages
  that don't describe the campaigns. The events themselves are well-
  documented in reality; check_festival_dates.py passes mechanically.
  Upstream: festival source_url should be the organizer page (HPBT for
  Furmint February; village/consortium page for Mádi Bornapok), not a
  generic Wikipedia article. Document in wine-research prompt; add a
  WARN in check_festival_dates.py when source_url is a generic
  wikipedia page rather than an organizer/consortium URL.

### Cuvée end-to-end (Royal Tokaji Mézes Mály Aszú 6 Puttonyos)
- Producer `royal-tokaji` resolves in vineyards.json. ✓
- Tags all in WINE_TAGS.md: `dessert-noble-rot` (Aszú correct), 
  `full-body`, `racy-acid`, pairing tags, occasion tags, mood tags,
  editorial: `iconic`, `single-vineyard`. ✓
- No derived tags emitted by researcher. ✓
- All pairings `tablejourney_ref: null` (acceptable). ✓
- Cuvée slug vintage-agnostic. ✓
- Style tag `dessert-noble-rot` correct for Aszú/Eszencia, 
  `still-white` correct for dry Furmint, `dessert-late-harvest` 
  correct for Late Harvest cuvées. Spot-checked across 10 cuvées. ✓
- Editorial 4.8 defensible (Mézes Mály = Royal Tokaji's flagship 
  first-class single-vineyard).

### 4.7+ editorial score spot-checks (5 spot-checked)
- All marquee at 4.7+ defensible per the brief's approved list:
  Royal Tokaji Mézes Mály (4.8), Royal Tokaji Nyulászó (4.7) and Szt.
  Tamás (4.7) single-vineyards, Disznókő Aszú 6 (4.7), Disznókő Eszencia
  (5.0), Oremus Aszú 6 (4.7), Oremus Eszencia (5.0), Szepsy Aszú 6
  (4.9) and Aszú 5 (4.7), Szepsy Úrágya Furmint (4.7), Pendits Aszú
  Essencia (4.7).
- Patricius Aszú, Holdvölgy Notabene, Bott Pince Furmint, Demeter
  Zoltán Hárslevelű are all scored 4.1-4.4 — conservatively scored,
  no inflation.
- Non-marquee 4.7+: NONE in wines.json. Clean.

### Sweep for fabricated chef/sommelier/owner names
- `Tamás Langó` (sommelier at Bobajka): verified at
  bobajkaetterem.hu/en/concept/ — "Tamás Langó, the Michelin Sommelier
  Award-winning Executive Sommelier of BDPST Group". ✓
- `Máté Gerák` (chef at Padi): verified at sauska.hu/en/restaurants/padi/
  — listed as "Resident chef" with his name as a heading. ✓
- `Stéphanie Berecz` (Kikelet): confirmed per QA1.
- `Sarolta Bárdos` (Tokaj Nobilis): confirmed per QA1.
- `István Szepsy Jr.` (Szepsy Jr): confirmed per QA1.
- `Nimród Kovács` (Kovács Nimród): estate name, confirmed.
- `Erzsébet Prácser` (Erzsébet Pince): estate-name match, confirmed.
- `Zoltán Demeter` (Demeter Zoltán): estate name, confirmed.
- `Hugh Johnson` (Royal Tokaji 1990 milestone in wines.json): widely-
  attested public figure, founding fact confirmed.
- `Mara Berry` (Pendits): wine-history.json + hidden-gems.json — name
  is widely documented in trade press as the Pendits proprietor.

### Hungary country stub
- Reads coherently: tagline + 4-paragraph overview + hero_image
  metadata + 22-regions reference + SEO + geo. ✓
- One soft-superlative ("Hungary's premier red-wine appellation"
  about Villány) stripped to "leading Hungarian red-wine appellation".
- No other defects.

---

## Defect count summary (Opus only)

| Class | Count | Action |
|---|---|---|
| Residual taste-block content (`summary`/`body`/`tannin`/`acidity`/`finish`) | 42 wines | Cleared `taste = {}` |
| Residual nulled-winemaker name in description prose | 1 (Gizella vineyards.json description) | Rewrote without name |
| Soft-superlative tier — residual ranking clauses | 14 + 1 (Hungary stub) | Stripped |

**Opus total defects: 57 (42 + 1 + 14 + 1 incremental ranking strips beyond QA1+QA2's 45)**
**Cumulative QA1 + QA2 + Opus defects removed: ~258**

---

## Final ship_safety

```
[1/7] validate_data.py — WARN only (description length, non-blocking)
[2/7] verify_entities.py — ERR=0 WARN=20 (own-site-only WARNs only)
[3/7] check_internal_references.py — 172 names, 189 slugs, 0 ERR, 0 WARN
[4/7] check_evidence_content.py — 10/10 matched, 0 HARD
[5/7] check_festival_dates.py — 8/8 OK
[6/7] check_external_urls.py — 1222 URLs all OK
[7/7] check_jsonld.py — WARN (global, non-city-scoped)
[+]   check_score_claims.py — 0 prose score claims

hungary/tokaj: ALL CHECKS PASSED
HARD failures: 0
```

---

OPUS-FOUND-15 hungary/tokaj
(15 distinct fix-passes; 57 file-level edits; 0 wine-vertical
regressions of the fabrication-discipline class. All defects in
already-known classes — Section I partial-strip, Section D-2 prose-
scrub gap, Section C0 soft-superlative residue.)
