# Opus Final QA — portugal/douro (Cork & Curve)

- Date: 2026-05-25
- Agent: Opus final QA (narrow read; verifies QA1 + QA2 + taste-evidence re-pass held)
- Inputs: post-re-pass JSON in `site-data/portugal/douro/data/` (vineyards 33, wines 94,
  signature-wines 12, + topic files), QA1 + QA2 reports
- Edits made: **0** (nothing material found)
- Verdict: **OPUS-CLEAR portugal/douro**

---

## Result

**OPUS-CLEAR portugal/douro.** No material defect found. QA1 (4 score fixes), QA2
(Sogevinus -> Kopke Group ownership + Section I taste-class flag), and the taste-evidence
re-pass all held under spot-check. Two non-material gate artifacts noted below for upstream
hardening; neither blocks ship.

---

## What I verified

### Taste-evidence re-pass HELD (the headline risk class)

- **Counts match the re-pass claim exactly.** 94 cuvées; **31 retain** `taste.aroma`/`taste.palate`
  arrays, **63 removed**. Matches "31 cuvées retain a substantiated taste block."
- **5 retained cuvées spot-checked by opening the cited URL** — descriptors confirmed verbatim on
  the page:
  - `taylors-20-year-tawny` -> taylor.pt page: "spicy, jammy and nutty aromas, hints of orange
    flower... rich and concentrated... long mellow finish." All 7 data descriptors present.
  - `dows-colheita` -> dows-port.com/colheita/12: "vanilla and orange blossom... mandarin, walnuts...
    coffee... dry and spicy finish." All present.
  - `wine-and-soul-guru` -> wineandsoul.com/en/wine/guru: "white flowers, grapefruit, lime... mineral
    touch... great texture and aftertaste." All present.
  - `quinta-do-crasto-vinha-maria-teresa` and `-reserva-old-vines` -> per-vintage PDF fichas técnicas
    (real, specific). Descriptors (wild berry, gum cistus, structured tannin) trace to the sheet.
- **3 removed cuvées confirmed structurally clean** — `taylors-vintage`, `quinta-do-noval-nacional`,
  `sandeman-20-year-tawny` (also kopke-colheita, niepoort-batuta, chryseia, vesuvio, quinta-nova):
  `taste` now carries only `body / tannin / acidity / finish / summary` (structural + editorial
  prose). No aroma/palate arrays. The summaries are rarity/ageing/structure editorial copy, not
  fabricated sensory descriptors. Correct.
- **Both critic-cited cuvées resolve and contain the descriptors:**
  - `ferreira-barca-velha` -> Farr Vintners (farrvintners.com/wine.php?wine=63785): correct wine
    (Barca Velha / Casa Ferreirinha 2011); page carries "black cherry, some nutmeg, graphite,
    leather, firm tannins" (Farr Vintners note) plus James Suckling and Julia Harding MW notes.
    All data descriptors present.
  - `quinta-do-vale-meao-tinto` -> Greg Sherwood MW (gregsherwoodmw.com, 2019 release): "pressed
    violets, sappy black currant, bramble berry spice... graphite and crushed granite... firm
    polished marble tannins, black and blueberry fruit." All data descriptors present.

### Classification (two-DOC) — CLEAN

- wines.json: only `DOC Porto` (62) and `DOC Douro` (32). vineyards: DOC Porto / DOC Douro / both
  (dual-licence estates). Zero `DOCa`, `AOC`, `DOCG`, `IGT`, `AVA` tokens anywhere. Port STYLE
  (Vintage/LBV/Tawny) is carried in `style`, not `classification`. Correct.

### Ownership currency — CLEAN

- `calem`, `kopke`, `burmester` all = "Kopke Group (formerly Sogevinus Fine Wines)". Every
  remaining "Sogevinus" string in vineyards.json is the intentional "formerly Sogevinus" context
  in owner + description. No stale standalone Sogevinus. QA2 fix held.

### Score discipline (>=4.7 backing + no fabricated 99+) — CLEAN

- 19 cuvées at editorial_score >= 4.7; each backed by a real top critic score (94-100).
- Only TWO scores >= 99 in the whole catalog, both on `quinta-do-noval-nacional`:
  WA 100 / 2011 and Robert Parker (WA) 99 / 1994 — both QA1-source-verified, KEPT.
- QA1 fixes held: `dows-vintage` top = WS 98 (not 99); `ferreira-barca-velha` top = WA 97 (not 98);
  Noval Nacional 1994 reviewer = "Robert Parker (Wine Advocate)" (not Wine Spectator). Signature
  prose mirrors confirmed: "98 points 2016 vintage" (Dow's), "Wine Advocate 97 points 2011" (Barca
  Velha). No fabricated >=99 reintroduced.

### Itinerary end-to-end — CLEAN

- `porto-and-gaia-port-weekend` (2 days, 7 venue slugs): all resolve —
  `taylors-port-cellars-gaia` + `grahams-1890-lodge-gaia` (tasting-rooms), `the-yeatman-gaia`
  (wine-hotels), `wow-world-of-wine-gaia` (wine-museums), `vinologia-porto` + `prova-porto` +
  `capela-incomum-porto` (wine-bars). No dangling stop refs.

### Festival month — CLEAN

- 5 festivals; `start_month` matches source/known dates: Essência do Vinho (Feb, late-Feb fair),
  Festa de São João (June 23-24), Douro Vindima harvest (Sept), Douro Wine Festival Régua (Aug,
  harvest start), São Martinho/Magusto (Nov, matches the Nov-11 St-Martin source). All correct.

### 30-entity cross-topic scan — CLEAN

- Sampled 30 of 299 entities across all topics. All real Douro estates/venues (Quinta do Noval,
  Quinta Nova, Quinta do Vesúvio, Niepoort/Quinta de Nápoles, Quinta do Poeira/Jorge Moreira —
  real winemaker, Quevedo, Quinta da Avessada Moscatel de Favaios). Addresses street-level where
  one exists; rural quintas use the named-estate address (QA1-adjudicated). `open_status` all
  within enum. No fabricated names or claim/source mismatch.

---

## Non-material notes for upstream hardening (NOT ship blockers)

1. **`check_evidence_content.py` recurring WARN on removed taste blocks.** ship_safety's
   cuvée-taste check reports `cuvee-taste-miss (WARN): 9` for cuvées whose aroma/palate arrays
   were *correctly* removed by the re-pass (cockburns-special-reserve, fonseca-lbv, fonseca-vintage,
   taylors-late-bottled-vintage, taylors-vintage, warres-otima-10, warres-vintage, warres-warrior,
   +1). Cause: the checker (scripts/check_evidence_content.py L172-182) still falls back to matching
   the editorial `taste.summary` prose against the producer page when aroma/palate are empty.
   Editorial summary prose is not expected to appear verbatim on a producer page, so the WARN fires
   on every ship even though the content is correct. **It is WARN (non-blocking) and there is no
   content defect** — the aroma/palate arrays are gone as intended. Recommend the gate skip the
   `summary` fallback when aroma/palate were deliberately removed, so the WARN reflects real
   taste-descriptor misses only. Class to harden, not a defect to fix.

2. **taylor.pt transient flap fails `check_external_urls` (the only red CHECK).** 2 URLs
   (taylor.pt/en, taylor.pt/en/visit-taylors/port-cellars) returned TimeoutError under the
   12-worker/10s concurrency. Re-checked single-threaded with a UA header: **200/200/200 on three
   tries each**. Same documented class as QA1 (wow.pt 502) and QA2 (taylor.pt flaps). The URLs are
   live; this is anti-bot/concurrency throttling on taylor.pt, not a broken link. No edit warranted.

---

## ship_safety status

`bash scripts/ship_safety.sh portugal douro` — the only failing check is `check_external_urls`
(2 taylor.pt timeouts, confirmed live 200 on retry). All other layers PASS: classification clean,
festival 5/5 month-match, internal refs ERR=0, cuvée-taste 0 HARD (9 WARN = summary-fallback
artifact above), JSON-LD clean. No JSON edited by Opus, so no post-edit re-run required.

**OPUS-CLEAR portugal/douro**
