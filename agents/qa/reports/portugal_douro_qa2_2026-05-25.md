# QA2 Report — portugal/douro (Cork & Curve)

- Date: 2026-05-25
- Agent: QA2 (judgment pass, PROMPT.md sections D, E, G, H, I, J, K)
- Inputs: post-QA1 JSON in `site-data/portugal/douro/data/` — vineyards.json (33 estates),
  wines.json (94 cuvées), signature-wines.json (12), food-pairing.json (8), dietary.json (9 entries)
- ship_safety on entry: 0 HARD (transient external-URL flaps only). After QA2 edits: 0 HARD (see end).
- Defects fixed directly: **5** (3 ownership-currency in vineyards.json + 2 prose mirrors)
- Structural finding flagged for re-research: **1 class** (Section I — cuvée taste-note sourcing, ~30+ cuvées)
- Advisories (non-blocking): 3

---

## Section D — Ownership currency  →  3 defects fixed + 1 briefing correction

Audited every `owner` against the Douro trap list.

**CORRECT / current (no change):**
- Symington Family Estates — Graham's, Dow's, Warre's, Cockburn's, Vesúvio, Bomfim, (Vale Meão is NOT Symington — correctly Olazabal). ✓
- The Fladgate Partnership — Taylor's, Fonseca, Croft, Panascal. ✓
- Sogrape — Ferreira, Sandeman, Quinta do Seixo. ✓
- Quinta do Noval = AXA Millesimes. ✓
- Real Companhia Velha = Silva Reis family. ✓
- Vale Meão = Olazabal family; Quinta Nova = Amorim family. ✓

**DEFECT — stale corporate name (Sogevinus → Kopke Group rebrand, July 2025).**
The briefing's note "Sogevinus … now owned by Roullier group" is **inaccurate on two points** and is
corrected here:
1. Sogevinus is NOT owned by the Roullier group. Its ultimate parent is **Banesco** (Juan Carlos
   Escotet), via the former Caixa Nova / Galician-bank lineage. The data never claimed Roullier, so no
   fabrication — but the briefing reference would have led a careless agent to inject a wrong owner.
2. The real currency issue: **Sogevinus Fine Wines rebranded to "Kopke Group" in July 2025**
   (the-buyer, thedrinksbusiness, winebusiness, drinks-intel). As of 2026-05-25 the current corporate
   name is Kopke Group, so `owner: "Sogevinus Fine Wines"` was stale.

   FIX (3 entities) — `owner` "Sogevinus Fine Wines" → "Kopke Group (formerly Sogevinus Fine Wines)"
   on `calem`, `kopke`, `burmester`.
   FIX (2 prose mirrors) — Calem description "part of the Sogevinus group" → "part of the Kopke Group
   (formerly Sogevinus)"; Kopke description "now Sogevinus-owned" → "namesake brand of the Kopke Group
   (formerly Sogevinus)"; Burmester description "part of Sogevinus" → "part of the Kopke Group
   (formerly Sogevinus)". (Counted as the 2 prose-mirror defects alongside the 3 owner fixes.)

   Source: https://www.thedrinksbusiness.com/2025/07/sogevinus-sheds-corporate-identity-in-kopke-group-rebrand/

**ADVISORY (not a defect):** `quinta-da-romaneira` carries `owner: "Quinta da Romaneira"` (self-name
placeholder). Real structure is an anonymous South American majority investor + Christian Seely as
minority owner / managing director (Wine Spectator). Since the majority owner is deliberately
unnamed in public sources, the self-name placeholder is preferable to fabricating a name. Left as-is.

## Section E — Biodynamic / organic certification  →  0 hard defects (hard-fail check CLEAN) + 1 advisory

Hard-fail check (practising → certified promotion) is **clean**:
- `niepoort-biodynamic`: `biodynamic_status: biodynamic_practicing`, `biodynamic_certifier: "none,
  practising only"`, tip explicitly says it does NOT promote full Demeter. NOT promoted. ✓ (matches
  briefing: "Niepoort biodynamic_practicing not Demeter-certified").
- `quinta-do-crasto-vegan`: `vegan: true`, `biodynamic_status: none`, `organic_status: none`, tip says
  "does not hold organic certification." CONFIRMED held as vegan-only — NOT promoted to organic/
  biodynamic. ✓ (matches briefing).
- Vallado/Orgal organic (certified 2015) and Tedo organic — both genuinely certified organic. ✓
- Folias de Baco natural + low-sulfite — natural_wine flags, no certification claimed. ✓
- ship_safety check_evidence_content.py matched **9/9** dietary cuisine_evidence_urls (the organic /
  vegan / natural CLAIMS are substantiated on-page). ✓

**ADVISORY — certifier body misnamed by enum (not user-facing).** Niepoort's actual organic certifier
is **SATIVA** (since 2012; winewithseth WineWiki, garrafeiranacional), not Ecocert. The two Niepoort
dietary entries carry `organic_status: "ecocert"`. However:
- `organic_status` is a controlled enum `{usda_organic, ecocert, icea, ccpb, none}` (SCHEMA.md) in
  which **SATIVA is not an available value**; here `ecocert` functions as the generic "certified-
  organic" token, and the generator only derives a boolean `organic` tag from `≠ none`.
- No user-facing prose anywhere names "Ecocert" as anyone's certifier (grep confirmed). The only
  certifier named in prose is the Niepoort tip correctly stating it does NOT hold Demeter.
- The certification STATUS (certified organic) is true; only the (non-displayed) enum token is the
  wrong body. Changing it to an out-of-enum "sativa" would break the validator.
  → Left as-is; **recommend adding `sativa` to the `organic_status` enum in
  agents/wine-research/SCHEMA.md** (Portugal-specific certifier) so future Portuguese regions can name
  it precisely. Not a ship blocker.

## Section G — Cross-link sanity  →  PASS (0 defects)

- wines.json: **73** non-null `pairings[*].tablejourney_ref` across 5 distinct paths; food-pairing.json:
  8 refs across the same 5 distinct paths. **All under `portugal/porto`** (the nearest TJ city — there
  is no TJ Douro page; this is the correct target). Zero non-Porto refs.
- HEAD-resolved all 5 distinct paths at tablejourney.com — **all 200**:
  - portugal/porto/dish/bacalhau-a-gomes-de-sa
  - portugal/porto/dish/bolinhos-de-bacalhau
  - portugal/porto/dish/port-wine-flight
  - portugal/porto/restaurants/muu-steakhouse
  - portugal/porto/restaurants/o-paparico
- All food-pairing.json `tablejourney_ref` HEAD-resolve and are in portugal/porto. PASS.

## Section H — Voice + prose  →  PASS (0 defects)

- Em-dash / en-dash scan across every string value in wines.json: **0 hits**.
- AI-tell scan (nestled, vibrant atmosphere, culinary journey, carefully crafted, must-visit, to die
  for, etc.): **0 hits**.
- Score-bunching: editorial_score mean 4.423, stdev 0.234, **CV 0.0528** (> 0.04 suspicious floor;
  distribution spans 4.0–5.0 across 11 buckets). Not bunched.
- Description clones: **0 exact clones**, **0 shared 45-char prefixes** within wines.json.
- 10 cuvée descriptions sit at 131–139 chars (research/QA1 noted ~23 in the 131–139 band; this is the
  WARN-level "just under 140–165 preferred" note, not a defect — none are clones, so left unpadded).

## Section I — Cuvée taste-note sourcing  →  STRUCTURAL DEFECT (flagged for re-research)

**This is the Rioja-2026-05-25 regression repeating.** Sampled well beyond the mandated 10 cuvées with
`editorial_score ≥ 4.5` (41 such cuvées exist; I opened 18 distinct cited `cuisine_evidence_url` pages
and inspected the full 65-URL map across all 94 cuvées).

**Finding:** the `taste.aroma` / `taste.palate` descriptor arrays are **style-templated, not page-
sourced**, and the cited `cuisine_evidence_url` for a large share of cuvées is a producer HOMEPAGE,
a wines OVERVIEW/SECTION landing, a wine-TOURISM/visit page, or a JS-only SPA shell that carries **no
per-wine descriptors at all**. Template fingerprint: every Vintage Port = "black cherry / blackberry
or cassis / violet / liquorice"; every 20-year tawny = "dried fig, orange peel, roasted nut /
butterscotch, candied citrus, walnut"; every flagship still red = "black cherry, violet, cedar/graphite,
dried herb / concentrated dark fruit, fine firm tannin, mineral."

URLs verified to carry NO matching per-wine descriptors (opened and read):
| cuvée(s) | cited URL | verdict |
|---|---|---|
| taylors-vintage | taylor.pt/en/port-wine/classic-vintage | generic "massive structure, aromatic power" — none of the data descriptors |
| sandeman-20-year-tawny | sandeman.com/port-wine/tawny/ | generic category text only |
| chryseia | chryseia.com/wines | notes only for OTHER wines (Post Scriptum, Prazo), not Chryseia |
| quinta-do-noval-nacional, -vintage (+2) | quintadonoval.com/en/our-wines | overview landing, no per-wine notes |
| niepoort-redoma/-batuta/-charme/-dialogo (5), niepoort-vintage/-colheita (2) | niepoort.pt/en/douro-wines/ and /en/ports/ | JS SPA shells, identical 1.8 KB markup for every path, zero content |
| wine-and-soul-* (4) | wineandsoul.com/en/ | site root / tourism page, no per-wine notes |
| ferreira-barca-velha, -vintage-port, -dona-antonia (3) | winetourism.sogrape.com/en/visit/ferreira | tour-booking page, no notes |
| quinta-do-vale-meao-tinto, meandro (2) | quintadovalemeao.pt/wine-olive-oil | shell, no descriptors |
| quinta-nova-referencia/-grande-reserva (2) | quintanova.com/en/wines | shell, no descriptors |
| quinta-do-vesuvio-vintage-port | quintadovesuvio.com/wines | shell, no descriptors |
| kopke-colheita, -10-year-white (2) | kopke1638.com/ | homepage, no descriptors |
| alves-de-sousa-abandonado, gaivosa (2) | alvesdesousa.com/ | homepage, no descriptors |
| quinta-do-vallado-adelaide, -reserva (2) | quintadovallado.com/en/ | homepage, no descriptors |
| quinta-do-crasto-vinha-maria-teresa (+2 Crasto) | quintadocrasto.wine/en/products/... | per-vintage PDF tech-sheets are LINKED but no descriptors in the cited HTML |

Producer pages that DO carry on-page tasting notes (so re-anchoring is feasible for these, but the
notes are impressionistic and only partially overlap the data arrays):
- Dow's `/wine-cat/vintage-port` and `/wine-cat/aged-tawny` — real per-vintage notes (plum, cassis,
  rockrose, violet; "honeysuckle, butterscotch").
- Graham's `/wine/.../24` — short note ("opulent, intense, fresh, layered fruit").
- Wine & Soul has real per-wine pages at `/en/wine/<slug>/` (e.g. /en/wine/pintas/, /en/wine/guru/)
  with genuine descriptors (black cherry, black currant, minerality; lime, quince, white flowers).
- Crasto product pages link per-vintage PDF fichas técnicas that carry the real notes.

**Disposition:** This is a structural research regression in `wines.json` taste sourcing affecting
30+ cuvées (every homepage/landing/SPA-shell citation), with the descriptor arrays templated rather
than transcribed from the cited source. Per PROMPT.md Section I the remedy is to re-anchor each cuvée
to its real per-wine page (Wine & Soul, Dow's, Graham's, Crasto-PDF exist; Niepoort/Noval/Kopke/
Sandeman/Taylor's/Vale Meão/Quinta Nova publish NO per-wine sensory notes on their own sites and would
need a named-critic source or block removal). Re-sourcing + re-writing 30+ descriptor arrays against
verbatim per-wine sources exceeds a single QA2 in-pass remediation and risks the exact "repaired to a
homepage that still has no note" error Opus caught on Rioja. **Flagged HARD for a wine-research
re-pass on `wines.json` taste blocks + `cuisine_evidence_url` before ship**, with the URL map above as
the worklist. Not silently shipped, not silently homepage-repaired.

NOTE: this is distinct from ship_safety's check_evidence_content.py, which only inspects the **dietary**
cuisine_evidence_urls (9/9 pass) — it does NOT inspect wines.json per-cuvée evidence URLs, so this
class is invisible to the mechanical gate.

## Section J — Tag vocabulary  →  PASS (0 defects)

- All 52 distinct tags across `wines[*].tags` appear in docs/WINE_TAGS.md.
- No derived-axis leakage: zero price-*, grape, world, ageing (drink-young/medium-term/cellar-worthy),
  production (organic/vegan/natural/biodynamic/low-sulfite), or sweetness (dry/off-dry/…) tags in
  researcher-emitted `tags[]`. (Confirms QA1's opportunistic Section J pass.)

## Section K — Vintage-agnostic discipline  →  PASS (0 defects)

- Zero `wines[*].slug` or `wines[*].name` contains a 4-digit year (regex `(19|20)\d{2}`).
- Age-tier tawnies (10/20/30/40yr) and Colheita are correctly modelled as separate vintage-agnostic
  cuvées, not vintage-stamped pages.

---

## Advisories for the orchestrator (non-blocking)

1. **Folias de Baco dangling `vineyard_ref`.** 3 dietary entries (natural + low-sulfite) reference
   `vineyard_ref: "folias-de-baco"`, but no such slug exists in vineyards.json (nor anywhere outside
   dietary.json). `vineyard_ref` is NOT consumed by any generator or template (grep confirmed), so it
   produces no broken link and does not break generation; the dietary entries are self-contained with
   their own verified blocks. Folias de Baco / Uivo (Tiago Sampaio) is a real Douro natural producer,
   so the content is accurate. Recommend either adding a proper Folias de Baco vineyards.json record
   (own verified block) or accepting the informational ref. Left as-is.
2. **`organic_status` enum lacks `sativa`** (see Section E) — recommend adding to SCHEMA.md.
3. **Transient external-URL flaps under ship_safety's 12-worker / 10 s concurrency:** taylor.pt/en and
   /en/visit-taylors/port-cellars time out on first hit then return 200 (verified 200 on retry 2/3 and
   3/3 with a UA header); a Zomato URL and oportoblog URL also flap. Same class as QA1's wow.pt 502.
   Not broken URLs.

---

## Files modified by QA2

- `site-data/portugal/douro/data/vineyards.json` — 3 owner-currency fixes (Sogevinus Fine Wines →
  Kopke Group on calem/kopke/burmester) + 3 description prose mirrors.

## Post-edit verification

- vineyards.json parses cleanly.
- `bash scripts/ship_safety.sh portugal douro` → **0 HARD failures** (transient external-URL flaps
  only; verify_entities 0 HARD / 4 advisory WARN; dietary evidence-content 9/9; internal refs ERR=0;
  classification/JSON-LD clean).
- Section I structural defect is flagged HARD for a wine-research re-pass — it is a judgment finding
  outside the mechanical ship_safety gate and MUST be resolved before ship.
