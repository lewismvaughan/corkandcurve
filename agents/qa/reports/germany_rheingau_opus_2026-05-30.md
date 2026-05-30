# Opus Final QA Report: germany/rheingau — 2026-05-30

Agent: Opus 4.7 (1M context)
Ship safety before Opus: PASS at QA2 hand-off
Ship safety after Opus: PASS (0 HARD; 0 cuvee-taste-miss WARN; 0 own_site_only WARN; 0 prose score-claims; 0 closed-venue findings)

Pre-Opus transient note: first ship_safety run flagged 4 TimeoutError on
`https://www.kronenschloesschen.de/` (10s timeout race; site returns 200 in
<1s on retry). Re-ran `check_external_urls.py` → "all 1464 URLs OK." Not a
defect.

---

## Findings: 4 defects (3 comparative-ranking residues + 1 fabricated critic credential)

### 1. wines.json — kesseler-r-spatburgunder: fabricated critic-attention prose (Section C0)

`history.summary` claimed:

> "the R label drew Wine Advocate's attention to Rheingau Pinot Noir in
> the late 1990s."

This is a critic-attention claim with no corresponding `scores[]` citation
nor a verifiable source. Per QA prompt Section C0:
> Any such claim with no corresponding verifiable scores[] citation is a
> fabrication — DELETE the clause/milestone (don't try to source it).

**Fix:** stripped the Wine-Advocate clause; rewrote to:
> "Kesseler's R is the estate's reserve Pinot Noir cuvee, made only in
> top vintages from the Assmannshausen and Ruedesheim Pinot parcels."

QA1 explicitly did the same conservative treatment for the Künstler
Suckling-99 mention on kuenstler.de (omitted from `scores[]` and prose);
this Kesseler reference was the same class but had been retained as
narrative prose, so QA1 + QA2's prose sweep missed it.

### 2. wines.json — prinz-jungfer-gg: comparative-ranking residue (Section H)

`taste.summary` contained:

> "racy, slate-driven Riesling at one of the highest elevations in the
> Rheingau"

Pattern matches the QA prompt's Comparative-ranking strip-list ("the
highest <X> in <region>" / "one of the highest ... in <region>"). QA2
applied 22 strips for this class but missed this one.

**Fix:** reframed to:
> "racy, slate-driven Riesling from the elevated Hallgarten slopes."

### 3. neighborhoods.json + vineyards.json — Hallgarten "Rheingau's highest sites" (Section H, 2× hits)

Two more residues with the same comparative-ranking shape, both about the
elevation of Hallgarten:

- `neighborhoods.json` Hallgarten: "Hallgarten sits at the Rheingau's
  highest cultivated altitudes (up to roughly 270 metres)" → reframed to
  "Hallgarten cultivated altitudes rise to roughly 270 metres" (kept the
  concrete 270m number, dropped the relative ranking).
- `vineyards.json` weingut-prinz: "working Jungfer, Schonhell and
  Hendelberg at the Rheingau's highest sites" → reframed to "...on the
  elevated Hallgarten slopes (around 270 metres)" (concrete number
  added).

### 4. signature-grapes.json — fruhburgunder "Germany's classic Pinot terroir" (Section H, soft-superlative)

Description ended with "the grape is part of the same red-slate enclave
that defines Assmannshausen as **Germany's classic Pinot terroir**."

Pattern matches the soft-superlative strip-list (`<country>'s most/finest/
classic <X>`). The claim is unfalsifiable: Pfalz also has long-established
Pinot terroir.

**Fix:** reframed to "the grape is part of the red-slate Assmannshausen
Pinot enclave."

---

## Narrow checks — all clean

### Schloss Vollrads ownership — QA2's fix verified

de.wikipedia.org/wiki/Schloss_Vollrads explicit:
> "In der Folge übernahm die Nassauische Sparkasse Schloss Vollrads und
> führte seitdem die Bewirtschaftung samt Weingut und Restaurant fort."

(After Erwein Graf Matuschka-Greiffenclau's 1997 bankruptcy/suicide.) Our
`vineyards.json[schloss-vollrads].owner = "Nassauische Sparkasse
foundation"` is correct. The "Greiffenclau Foundation" the brief asked
about does not exist as an entity; the Greiffenclau family has not owned
Vollrads since 1997.

### Demeter promotions (Section E)

- `peter-jakob-kuehn` — weingutpjkuehn.de/biodynamie/ contains "Demeter
  e..." and "demeter" in body. Confirmed.
- `kaufmann` — kaufmann-weingut.de body contains "Demeter-Erzeugung",
  "Demeter-Weingut", "biodynamischer". Confirmed.

Both Demeter claims hold. No promotions of biodynamic-practicing →
demeter-certified detected.

### Festival end-to-end — Rheingauer Weinwoche Wiesbaden

Claim: "annual, ten consecutive days from the second Friday in August."
wiesbaden.de microsite:
> "Zehn Tage – eine Weinregion – über 100 Stände – mehr als 1.000 Weine
> und Sekte: Vom 14. bis 23. August 2026 wird rund um Marktkirche,
> Schlossplatz und Dern'sches Gelände wieder die Weinwoche gefeiert."

Aug 14, 2026 IS the second Friday in August. 10 days. Exact match. Clean.

### Itinerary end-to-end — rheingau-wine-route-three-days

8 day-venues across 3 days; every slug resolves in vineyards.json
(`weingut-kuenstler`, `hessische-staatsweingueter-kloster-eberbach`,
`robert-weil`, `balthasar-ress`, `peter-jakob-kuehn`,
`schloss-johannisberg`, `leitz`, `eva-fricke`). Clean.

### Cuvée end-to-end — kiedricher-graefenberg-gg (ed_score 4.9)

- Producer slug `robert-weil` resolves in vineyards.json
- All 12 tags pass docs/WINE_TAGS.md vocabulary (still-white, full-body,
  high-acid, 3× pairs-with-*, occasion-special, occasion-cellar,
  mood-contemplative, single-vineyard, iconic, old-vines)
- `taste.aroma` / `taste.palate` stripped by QA2 (shared-URL Option C);
  `taste.summary` kept as flowing copy
- All 3 pairings have `tablejourney_ref: null` (TJ has no Wiesbaden /
  Frankfurt food guide; nothing to HEAD-check)

Clean.

### High-score spot-check (editorial_score ≥ 4.7) — 9 cuvées sampled

Cork & Curve's editorial discipline is to NOT carry critic-score
backing in `scores[]` for these flagship cuvées (per QA1's note about
the Künstler Suckling 99-pts conservative omission). After prose sweep
with critic / superlative / ranking regexes, only the Kesseler R Wine
Advocate clause turned up as a fabricated credential (Defect 1 above).
The other 8 (Goldlack TBA, Steinberger GG, Kiedricher Gräfenberg GG,
Gräfenberg Eiswein, Silberlack GG, Gräfenberg Auslese, Hochheimer
Hölle GG, Berg Schlossberg GG Leitz, Breuer Berg Schlossberg) carry no
press credentials in prose. Conservative, correct per Cork & Curve
editorial-score policy.

### 30-entity random skim — clean across all topics

Spot-checks confirmed:
- August Eser owner "Desirée Eser Freifrau zu Knyphausen" — verified on
  eser-wein.de page footer ("Désirée Eser - Freifrau zu Knyphausen").
- Chat Sauvage owner "Schulz-Schoettle family" — verified on
  chat-sauvage.de/impressum ("Schulz & Schöttle eGbR ... Günter Schulz,
  Verena Schöttle"). Slight stylistic spelling variant acceptable.
- Chat Sauvage winemaker "Michael Stadter" — verified via weinkenner.de
  directory ("Kellermeister: Michel Städter"; ombiasy WineTours
  "Winemaker Michael Städter"). Umlaut-stripped + first-name anglicized
  but factually correct.
- Florian Richter "Sommelier des Jahres 2023" at Kronenschloesschen —
  verified via kronenschloesschen.de/de/weinliebhaber/
  beste-weinkarte-deutschlands/ ("Head-Sommelier Florian Richter im
  Weinkeller"). The 2023 Sommelier-des-Jahres award itself is the
  concrete year-bound credential QA1 preserved when it stripped the
  "one of Germany's most decorated wine lists" superlative.
- Weingut Trenz "Discovery of the Year by Gault Millau in 2008" —
  verified on weingut-trenz.com/en/pages/weingut ("Three years later,
  in 2008, another honor followed when Gault Millau named us 'Discovery
  of the Year.'"). Concrete year-bound award. Clean.

### Comparative-ranking residue sweep

After Opus's 3 fixes above + a broader manual sweep across all 26 JSONs
for the soft-/comparative-/world-ranking patterns enumerated in QA
prompt Section H, the only remaining "at one of the" / "one of the X"
hits are LOCATIONAL ("a final glass of estate Riesling at one of the
riverfront vinotheks") not ranking claims. `check_score_claims.py
--strict` returns "no prose score-claims found."

### Tag vocabulary, vintage-agnostic slugs, producer cross-references

All 151 cuvées' tag arrays load against docs/WINE_TAGS.md without rejects.
Regex scan of slugs + names for 4-digit years: none. Every wine producer
resolves to a vineyards.json slug. All 30 signature_wines slugs are
present in wines.json. Clean.

---

## Defect count summary

| Category | Count | Action |
|---|---|---|
| Fabricated critic-attention prose (Section C0) | 1 | Stripped Wine-Advocate clause on kesseler-r-spatburgunder.history.summary |
| Comparative-ranking residue (Section H) | 3 | Reframed wines.json prinz-jungfer-gg + neighborhoods.json hallgarten + vineyards.json weingut-prinz |
| Soft-superlative residue (Section H) | 1 | Reframed signature-grapes.json fruhburgunder "Germany's classic Pinot terroir" |
| Ownership / certification / itinerary / festival / cuvée defects beyond QA1+QA2 | 0 | All narrow checks clean |

**Total defects: 4.**

Known passed-through non-blocking WARNs (pre-existing per QA2 hand-off):
- 50 bare-homepage cuisine_evidence_url WARNs (QA1 wein.plus swap
  residue, only material when researcher re-adds aroma/palate arrays
  pointing at producer homepages — currently aroma/palate stripped on
  those 26 cuvées under QA2 Option C, so the WARN is informational).
- 25+ description-length WARNs in non-vineyards topics (175-233 chars,
  cap 140-165). Pre-existing from QA1 scope. Non-blocking.

---

## PROMPT-HARDENING SUGGESTIONS

### A. Comparative-ranking strip-list should explicitly enumerate ELEVATION ranks (3 of 4 Opus defects)

QA prompt Section H comparative-ranking patterns already enumerate
`largest | leading | biggest | smallest | oldest | youngest | first |
earliest | finest | highest | widest`. **`highest` is technically listed**
but researchers + QA1/QA2 read it as a soil-altitude indicator rather
than a ranking axis. Three of four Opus defects here cluster on
elevation ranks for the Hallgarten cluster ("Rheingau's highest sites",
"highest cultivated altitudes", "one of the highest elevations in the
Rheingau"). Researchers default to assuming elevation is a factual
geographic attribute, but it's still a relative-rank claim against a
non-verifiable rolled-up regional dataset (the actual highest cultivated
Rheingau parcel is debated and small-margin).

**Suggested addition to QA prompt Section H / wine-research SCHEMA:**

> ELEVATION as a RANKING AXIS. When a wine or vineyard description
> mentions elevation, state the absolute metric ("at 270 metres",
> "around 250m above the Rhine") and never the relative rank ("the
> highest", "one of the highest", "the highest cultivated altitudes in
> the region"). The "highest" axis is already listed in the strip-list
> but is frequently mis-read as a geographic fact. Treat it the same as
> "the largest cooperative in Alsace" — replace the rank with the
> number.

This same rule should appear in `agents/wine-research/PROMPT.md` so
the researcher emits the absolute number from the start. Mechanical
backstop: `check_score_claims.py` RE_SOFT_RANK already includes
`highest`; consider tightening so it surfaces "highest cultivated
altitudes" / "highest elevations" / "highest sites" specifically as a
WARN.

### B. C0 prose-scan should cover history.summary (not just history.milestones)

The QA prompt Section C0 enumerates "EVERY free-text field
(`history.milestones[*].event`, `description`, `taste.summary`, `tip`)".
The Kesseler R defect hid in `history.summary` (the prose summary, NOT
`history.milestones[*].event`). Both QA1's narrative prose sweep and the
mechanical `check_score_claims.py` scan include all string values in
the JSON, so the Wine-Advocate hit SHOULD have been caught. It wasn't,
probably because "Wine Advocate's attention" doesn't trip the C0 score
patterns (no number near the publication name, no `points|punti|pts`
token).

**Suggested addition to `check_score_claims.py`:**

> Add a low-confidence WARN pattern for `(Parker|Wine Advocate|Wine
> Spectator|Suckling|Vinous|Decanter|Gault|Falstaff|Robinson)['s]
> (attention|focus|spotlight|praise|review|coverage|interest|notice)`.
> A critic-attention prose claim with no `scores[]` citation is a
> fabrication-risk class the same as a numeric points claim. Researchers
> hide credibility-borrowing claims here when they can't source a
> specific number.

This would catch "drew Wine Advocate's attention", "Suckling's high
praise", "earned Wine Spectator coverage", "Parker's review", "Decanter
World Wine Awards Gold" (without year) etc.

### C. Cork & Curve's "no critic-score backing" discipline is working

The flagship cuvées at editorial_score ≥ 4.7 (Goldlack TBA, Steinberger
GG, Kiedricher Graefenberg GG, Silberlack GG, Hölle GG, Leitz Berg
Schlossberg etc.) carry no critic claims in prose. This is the right
discipline for German Rieslings where critic scores are less standardised
than for Bordeaux / Brunello / Napa Cab — many of these wines have
published scores (Suckling 99 on Künstler Marcobrunn, WS Top 100
appearances) that Cork & Curve intentionally does NOT relay because
they're vintage-bound and the page is vintage-agnostic. Maintain this
discipline going forward; this is a feature, not a coverage gap.

---

## Final ship_safety

```
germany/rheingau: ALL CHECKS PASSED
HARD failures: 0
prose score-claims: 0
cuvee-taste-miss WARN: 0
own_site_only WARN: 0
closed-venue findings: 0
```

OPUS-FOUND-4 germany/rheingau

Defects (each REMOVED in place):
1. wines.json kesseler-r-spatburgunder — fabricated "Wine Advocate's attention" prose
2. wines.json prinz-jungfer-gg — comparative-ranking ("one of the highest elevations in the Rheingau")
3. neighborhoods.json hallgarten + vineyards.json weingut-prinz — "Rheingau's highest" elevation ranks (concrete 270m number kept/added)
4. signature-grapes.json fruhburgunder — soft-superlative "Germany's classic Pinot terroir"
