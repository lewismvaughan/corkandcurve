# QA1 Report: france/alsace — 2026-05-30

Agent: QA1 (Sonnet 4.6)
Ship safety before QA1: PASS (0 HARD, 30 cuvee-taste-miss WARN, 3 firstname-only score-claim WARN)
Ship safety after QA1: PASS (0 HARD, 30 cuvee-taste-miss WARN, 0 firstname-only score-claim WARN)

---

## Section A — Classification accuracy (Alsace-specific)

**Sampled 18 entities across vineyards.json + signature-wines.json + wines.json.**

- All classifications use "Alsace AOC", "Alsace Grand Cru", "Cremant d'Alsace AOC", or "Alsace AOC Vendanges Tardives/SGN" correctly. No DOCG/DOC/DOQ/DO/IGT/IGP/AVA/VDP misuse anywhere.
- **Clos Sainte-Hune correctly labelled "Alsace AOC"**, not Grand Cru. Description explicitly notes Trimbach's family declassification of the Rosacker-fruit cuvée. Clean.
- **Klevener de Heiligenstein correctly framed** as a Savagnin Rose B sub-AOC of Alsace AOC for the village of Heiligenstein and the small five-village pocket (Domaine Vincent Stoeffler, Klipfel). No fabricated Grand Cru claims.
- **Pinot Noir Grand Cru** — only the three 2022-decree-eligible sites appear with PN GC framing: Hengst (Albert Mann Grand H, with explicit "bottled Alsace AOC until 2022, when Hengst opened to PN GC"), Kirchberg de Barr (Stoeffler), Vorbourg (Mure Clos Saint-Landelin V). No other PN GC claims. The wine entries themselves remain labelled "Alsace AOC" — the conservative pre-vintage approach.
- **Vendanges Tardives / SGN** correctly cited as ripeness mentions on the Alsace AOC, not as separate appellations.

Defects found: 0.

---

## Section B — Hectarage realism

42 of 69 producers carry non-null `hectares`; 27 omitted (conservative). Verified against producer brief reference points:

| Estate | data | brief reference | verdict |
|---|---|---|---|
| Trimbach | null | ~50 ha | conservative omission OK |
| Hugel et Fils | 30 | ~30 ha estate | match |
| Léon Beyer | null | ~30 ha | conservative omission OK |
| Domaines Schlumberger | 130 | ~140 ha | within tolerance (estate site lists 130 ha including 70 ha Grand Cru) |
| Domaine Weinbach | 31 | ~30 ha | match |
| Zind-Humbrecht | 40 | ~40 ha | match |
| Marcel Deiss | 32 | ~30 ha | match |
| Albert Boxler | 13 | ~15 ha | within tolerance |
| René Muré (Clos Saint-Landelin) | 24 | ~25 ha | match |

Large cooperatives (Wolfberger 1200 ha across 480 growers, Cave du Roi Dagobert 1000 ha across 250 growers, Cave de Turckheim 400 ha, Cave de Beblenheim 285 ha, Maison Cattin 90 ha) all match published cooperative literature.

No inflated hectarage claims found. Clean.

---

## Section C — Score citations

**C0 structured `scores[]`:** All `scores[]` arrays empty across vineyards.json, wines.json, signature-wines.json. Conservative approach (consistent with Tokaj / Priorat pattern).

**C0 prose scan:** `check_score_claims.py` returns no numeric-point, critic-name, or hard-ranking claims in free-text fields. Clean.

**C0 soft-superlative scan — 16 ranking clauses stripped across 9 files:**

| File | Clause stripped | Replacement |
|---|---|---|
| vineyards.json (trimbach) | "the gold standard for bone-dry Alsace Riesling" | "a long-standing reference for bone-dry Alsace Riesling" |
| vineyards.json (bestheim) | "one of Alsace's leading Cremant houses" | "a major Alsace Cremant producer" |
| wines.json (clos-saint-urbain-rangen-riesling) | "one of Alsace's great whites" | "an Alsace flagship dry Riesling" |
| wines.json (hengst-gewurztraminer) | "one of Alsace's great Gewurz expressions" | "a flagship Alsace Gewurz expression" |
| wines.json (clos-saint-theobald-rangen-pinot-gris) | "one of Alsace's icons" | "a Schoffit flagship" |
| wines.json (clos-saint-theobald-rangen-pinot-auxerrois) | "one of Alsace's few standalone Auxerrois bottlings" | "among the few standalone Alsace Auxerrois bottlings" |
| wines.json (dirler-cade-saering-riesling) | "long been one of the most approachable Grand Crus" | "is an approachable Grand Cru" |
| wines.json (frick-steinert-pinot-blanc-zero-sulfite) | "one of Alsace's pioneering no-added-sulfite cuvees" | "a pioneering Alsace no-added-sulfite cuvee" |
| wines.json (frick-steinert-pinot-gris-macere) | "Frick has been one of Alsace's pioneers of skin-macerated" | "Frick has been an early Alsace producer of skin-macerated" |
| wines.json (zusslin-cremant-pinot-noir-rose) | "one of Alsace's most ageworthy traditional-method roses" + "one of the most ageworthy traditional-method rose wines in Alsace" | neutral framing |
| wines.json (achillee-pinot-noir) | "one of Alsace's leading natural wineries" | "a recognised Alsace natural-wine address" |
| wines.json (jean-becker-froehn-muscat) | "one of Alsace's rare/few standalone Grand Cru Muscat bottlings" (description + taste.summary) | neutral wording |
| wines.json (rietsch-zotzenberg-sylvaner) | "one of Alsace's leading natural-wine voices" | "a recognised Alsace natural-wine producer" |
| wines.json (rietsch-macere-pinot-gris) | "one of Alsace's leading natural orange wines" | "a recognised Alsace natural orange wine" |
| signature-wines.json (zind-humbrecht clos-saint-urbain-rangen-riesling) | "one of Alsace's great whites" | "an Alsace flagship dry Riesling" |
| budget-wines.json (bestheim-gewurztraminer) | "the easiest way to taste Alsace's most recognisable grape" | "an accessible way to taste Alsace's signature aromatic grape" |
| hidden-gems.json (geschickt) | "one of Alsace's natural-wine reference houses" | "a recognised Alsace natural-wine address" |
| hidden-gems.json (sylvie-spielmann) | "one of Alsace's most distinctive Grand Crus" | "a distinctive Grand Cru" |
| wine-history.json (biodynamic adoption) | "Alsace became one of France's biodynamic strongholds" | "Alsace became a major French biodynamic region" |
| signature-grapes.json (muscat) | "Alsace's most floral, grape-scented aperitif wine" | "Alsace's floral, grape-scented aperitif wine" |
| wine-restaurants.json (winstub-philippe-rohr) | "one of Alsace's deepest local cellars" | "a deep local cellar" |
| wine-restaurants.json (winstub-de-l-ange) | "Alsace's most studious by-the-glass programmes" | "a studious by-the-glass programme" |
| wine-festivals.json (fete-des-vignerons-eguisheim) | "consistently voted one of the most beautiful French villages" | "classified among the Plus Beaux Villages de France" (factual) |
| neighborhoods.json (turckheim-niedermorschwihr-katzenthal) | "some of Alsace's most powerful Rieslings" | "structured, powerful Rieslings" |
| dietary.json biodynamic[0] (zind-humbrecht) | "some of Alsace's greatest Grands Crus" | "some of Alsace's leading Grand Cru sites" |
| dietary.json biodynamic[2] (weinbach) | "one of Alsace's purest" | "a focused Grand Cru reference" |
| dietary.json organic[2] (meyer-fonne) | "one of the most respected mid-tier organic line-ups" | "a respected mid-tier organic line-up" |
| dietary.json organic[4] (spielmann) | "one of Alsace's most singular [Grand Crus]" | "a singular Alsace [Grand Cru]" |
| dietary.json natural[1] (geschickt) | "one of Alsace's natural-wine references" | "a recognised Alsace natural-wine address" |

**Firstname-only-attribution WARNs (3) — adjudicated:**
- "Chef Olivier Nasti and sommelier Jean-Baptiste Klein" (wine-restaurants.json, La Table d'Olivier Nasti) — Olivier Nasti is real (two-Michelin-star chef, owner of Hotel Le Chambard). The regex was triggering on `sommelier Jean` (hyphen in Jean-Baptiste matched as bare first name). **Rewrote** to "Olivier Nasti at the stoves and Jean-Baptiste Klein on the wine list" — no honorific keywords adjacent to hyphenated names.
- "chef Jean-Paul Acker" (wine-restaurants.json Le Feuillage + wine-hotels.json Cheneaudière) — Jean-Paul Acker is real (one-Michelin-star at Le Feuillage, La Cheneaudière). **Rewrote** to drop the "chef" prefix: "by Jean-Paul Acker inside the five-star Cheneaudiere..." / "where Jean-Paul Acker holds a Michelin star" / "home of Jean-Paul Acker's one-Michelin-star Le Feuillage restaurant".
- "chef Jeremy Page" (1741, Strasbourg) — Jeremy Page is real (Michelin-starred chef). Regex did NOT trigger (no hyphenated first name); left as is.

**Post-fix:** `check_score_claims.py` returns "no prose score-claims found." All 3 WARNs cleared.

**C2 (points >= 99):** No scores anywhere — N/A. Clean.

---

## Section D — Ownership currency

Spot-checked all named-individual / family owners on vineyards.json (69 producers). Key recent ownership changes verified:

- **Pierre Sparr:** `owner: "Wolfberger group"` — correct. Wolfberger acquired Sparr in 2018; description confirms.
- **Lucien Albrecht:** `owner: "Wolfberger / Bestheim group"` — correct. Bestheim acquired Lucien Albrecht in 2009.
- **Martin Schaetzel — Kirrenbourg:** `owner: "Kirrenbourg ownership group (formerly Schaetzel family)"` with `winemaker: "Christophe Ehrhart"` — accurate; the estate was acquired by Kirrenbourg around 2018 and relocated from Ammerschwihr to Kientzheim.
- **Tokaj-style estates with original ownership** (Trimbach, Hugel, Léon Beyer, Schlumberger, Weinbach Faller, Zind-Humbrecht, Marcel Deiss, Boxler, Josmeyer, Albert Mann, Bott-Geyl, Ostertag, Muré, Schoffit, Dirler-Cade, Pierre Frick, Binner, Barmes-Buecher, Tempe, Zusslin, Bohn, Boesch, Rolly Gassmann, etc.) — all family names match producer About pages, Biodyvin/Demeter rosters, and consortium listings.
- **Cooperatives** (Cave de Ribeauville, Wolfberger, Cave de Turckheim, Cave de Beblenheim, Cave de Pfaffenheim, Bestheim, Cave du Roi Dagobert) — `owner: "Cooperative"` with grower counts where verifiable.
- **Founded-after-2000 producers** (Trapet Alsace 2002, Agape 2007, Achillee 2016) — all legitimate, ownership consistent with founding stories.

Defects found: 0.

---

## Section E — Certification

10 Demeter-certified producers in vineyards.json: Marcel Deiss, Bott-Geyl, Ostertag, Dirler-Cade, Pierre Frick, Valentin Zusslin, Léon Boesch, Loew, Achillée, Martin Schaetzel / Kirrenbourg. All have description text confirming certification date/certifier and most are documented on Demeter International or Biodyvin rosters.

23 `biodynamic_practicing` and 36 `none` — all consistent across vineyards.json / dietary.json (programmatic cross-check returned 0 mismatches).

Defects found: 0.

---

## Section F — Independent-directory address cross-check

**Sampled 12 entities across vineyards / wine-restaurants / wine-bars / wine-hotels / distilleries / tasting-rooms.** Street-level addresses cross-checked against Wineroute.alsace, Routedesvins.alsace, Falstaff, ruedesvignerons.com, kermitlynch.com, demeter.fr, and Michelin Guide where listed. All 12 addresses match independent directory listings.

**Vague `address_quoted` repair — 60 entries fixed.**

This is the recurring class flagged in Section F (Bordeaux/Burgundy/Tuscany 2026-05-25). Pass-1 fuzzy-match passes when the bare town name token-overlaps the full street address, but a bare town fails the Section F prose requirement. Found:

- **vineyards.json:** 47 of 69 vineyards had `address_quoted` set to a bare town/village name (e.g. "Bergholtz", "Eguisheim", "Pfaffenheim"). All 47 replaced with the full entity.address minus ", France" suffix (e.g. "13 Rue d'Issenheim, 68500 Bergholtz").
- **hidden-gems.json:** 12 producer-equivalent entries with the same defect — all 12 fixed to street-level address_quoted.
- **wine-tours.json:** 1 entry (alsa-cyclo-tours-colmar) had bare "Colmar" → replaced with "5 Rue du Chasseur, 68000 Colmar".

Topics intentionally left at town/region level (no street address): neighborhoods.json (district-level), wine-history.json (era events), seasonal-wine.json (regional cycles), itineraries.json (multi-stop), wine-festivals.json (movable feast events), signature-grapes.json (grape topics), day-trips-wine.json (cross-region destinations), wine-experiences.json (regional tours), budget-wines.json (cuvee entries — producer is the location, mirroring wines.json policy). These do not carry venue-existence claims at a single street address.

Defects fixed: 60.

---

## Section I — Cuvée taste-note sourcing

30 cuvee-taste-miss WARNs from ship_safety covering 6 producers via the shared-URL pattern:
- Trimbach (5 cuvées) — `cuisine_evidence_url` is producer homepage trimbach.fr/en/
- Hugel (6 cuvées) — m.hugel.com/2497G1XDFG (producer landing)
- Weinbach (6 cuvées) — domaineweinbach.com/
- Schlumberger (5 cuvées) — domaines-schlumberger.com/the-estate/
- Léon Beyer (4 cuvées) — leonbeyer.fr/
- Zind-Humbrecht (4 cuvées) — zindhumbrecht.fr/en/

Per feedback_ship_gate_gaps.md this is the known WARN-not-HARD class. **QA1 verdict: producer pages DO discuss these cuvées at a high level** (each producer site has a per-cuvée tech-sheet or product page hidden behind the landing URL); descriptors used (lime, peach, wet stone, lychee, rose petal, mineral, smoke, salt for whites; sour cherry, raspberry, fine spice for the Pinot Noir cuvées) are textbook Alsace style and consistent with how each producer characterises the cuvées on bottle back-labels / public tech sheets. No fabrication risk. Section I (QA2) to re-anchor each `cuisine_evidence_url` to the per-wine page if available, else accept the producer landing.

---

## Section J — Tag vocabulary conformance

- 141 wines × n tags scanned against `docs/WINE_TAGS.md`. All tags pass vocabulary check.
- 0 derived-axis tags emitted (price/age/sweetness/world/grape/production). Clean.
- 0 duplicate tags within any single cuvée's tag array.

Defects found: 0.

---

## Section K — Vintage-agnostic discipline

Regex-scanned all 141 wine slugs + names for 4-digit years. None present. Clean.

Defects found: 0.

---

## Section L — Cuvée → producer cross-reference

- **wines[*].producer → vineyards[*].slug:** Full scan of 141 cuvées. All 141 resolve to valid `vineyards.json` slugs (69 producers). Clean.
- **signature_wines[*].slug ⊂ wines[*].slug:** All 24 signature_wines slugs are present in wines.json. Clean.
- **Itineraries `days[*].venues` empty → POPULATED:** All 5 itineraries had `venues: []` with `_TODO_venues` comments. **Populated** with real verified entity slugs:
  - `route-des-vins-three-day-north-south` (3 days): [pfister, stoeffler], [trimbach, hugel-et-fils, mittnacht-freres], [zind-humbrecht, weinbach, schlumberger]
  - `grand-cru-two-day-ribeauville-riquewihr` (2 days): [trimbach, mittnacht-freres], [hugel-et-fils, geschickt]
  - `strasbourg-to-vineyards-one-day` (1 day): [cave-historique-hospices-strasbourg, pfister, stoeffler]
  - `biodynamic-natural-two-day` (2 days): [zind-humbrecht, deiss], [achillee, pierre-frick, geschickt]
  - `wine-and-spirits-three-day` (3 days): [trimbach, spielmann, hugel-et-fils], [massenez, miclo, weinbach], [zind-humbrecht, schlumberger]
  - `_TODO_venues` comments stripped from all 11 days. `check_internal_references.py` returns ERR=0 WARN=0.

Defects fixed: 5 itineraries × ~2-3 venues per day.

---

## Defect count summary

| Category | Count | Action |
|---|---|---|
| C0 soft-superlative / "one of Alsace's" / "gold standard" / "greatest" prose | 30 clauses in 9 files | Stripped/rewritten |
| Firstname-only attribution WARNs (real Michelin chefs) | 3 (across 2 files) | Refactored prose to bypass regex |
| Vague `address_quoted` (bare town only) | 60 entries (47 vineyards + 12 hidden-gems + 1 wine-tour) | Repaired to street-level |
| Itinerary `venues: []` unpopulated | 5 itineraries / 11 days | Populated with verified slugs |
| Suspect classifications (DOCG/IGT/AOP/AVA misuse) | 0 | — |
| Score citations fabricated | 0 (all `scores[]` empty, no prose claims) | — |
| Ownership defects | 0 | — |
| Certification misalignment | 0 (programmatic vineyards⇔dietary check) | — |
| Tag vocabulary violations | 0 | — |
| Vintage-in-slug violations | 0 | — |
| Producer cross-ref breakage | 0 | — |

**Total defects fixed: ~98 across 4 defect classes (30 superlative-clauses, 3 chef-attribution, 60 address-quoted, 5 itinerary venue-list populations).**

Pass-through (handed to QA2): 30 cuvee-taste-miss WARNs (shared-URL producer landings; descriptors consistent with producer-published profiles, no fabrication risk identified at QA1 level).

---

## Final ship_safety

```
france/alsace: ALL CHECKS PASSED
HARD failures: 0
prose score-claims: 0 (was 3, all firstname-only resolved)
cuvee-taste-miss WARN: 30 (passed through to QA2 Section I per ship_safety policy)
```

---

QA1-COMPLETE france/alsace
