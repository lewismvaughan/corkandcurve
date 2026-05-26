# QA2 report — germany/mosel

- Date: 2026-05-26
- Agent: QA2 (judgment pass, sections D, E, G, H, I, J, K)
- Region: Mosel (Germany)
- Inputs: post-QA1 JSON (QA1 cleared A/B/C/F/L + style/sweetness). ship_safety
  PASSED prior. Per PROMPT.md, did NOT re-HEAD all URLs or re-validate JSON shape;
  targeted web verification only where ownership/certification currency required it.

## Section D — Ownership currency (2024-2026) — 2 DEFECTS FIXED

Scanned all 42 vineyard `owner`/`winemaker` fields; web-verified the flagged traps.

**FIXED — `reichsgraf-von-kesselstatt` (stale, names deceased owner):**
- Was: `owner: "Annegret Reh-Gartner estate (Gartner family)"`. Annegret
  Reh-Gartner's directorship ended 2016 and she died in 2020. Naming her as
  current owner is stale.
- Verified (winewithseth WineWiki, Wine Enthusiast/Wine Spectator obituaries):
  the **Reh family still owns** the estate (since 1978); managing director since
  July 2020 is **Dr. Karsten Weyand**, with David Nicolay as Kellermeister.
  (The brief's "Christian Vogt direction" hint did not hold — current director
  is Weyand, not Vogt.)
- Now: `owner: "Reh family (managing director Dr. Karsten Weyand)"`.

**FIXED — `vollenweider` (stale founder-as-sole-owner; also cross-file inconsistency):**
- Was: `owner: "Daniel Vollenweider"`, `winemaker: "Daniel Vollenweider"`.
- Verified on producer site: jointly led with **Moritz Hoffmann since 2019**;
  since 2025 Hoffmann with Vinzent Ewest. Entity is "Weingut Vollenweider GbR".
  hidden-gems.json already carried the corrected "Moritz Hoffmann (founded by
  Daniel Vollenweider)" — vineyards.json was the stale, inconsistent copy.
- Now: `owner: "Moritz Hoffmann (estate founded by Daniel Vollenweider)"`,
  `winemaker: "Moritz Hoffmann"`. Present-tense "Daniel Vollenweider's estate"
  description softened to founder-vs-current phrasing to match.

**VERIFIED CLEAN (trap list):**
- Wwe. Dr. H. Thanisch — correct sibling: the dataset uses
  `wwe-dr-h-thanisch-erben-mueller-burggraef` (owner "Muller-Burggraef heirs",
  Junkerland 14, Bernkastel-Kues/Andel), confirmed against dr-thanisch.de. NOT
  conflated with the Erben Thanisch / Sofia Thanisch estate.
- Dr. Loosen = Ernst Loosen; Maximin Grunhaus = von Schubert; Schloss Lieser =
  Thomas Haag; Nik Weis = St. Urbans-Hof; Fritz Haag = Oliver Haag; Willi
  Schaefer = Christoph Schaefer; J.J. Prum = Katharina Prum; Markus Molitor =
  self. All current. No other stale owner among the 42.

## Section E — Biodynamic / organic certification — PASS (0 defects), 1 ref-typo fixed

7 dietary/hidden-gems certification claims checked; per-estate verified bodies,
no blanket application, no practising→certified promotion.

- **Clemens Busch** — `biodynamic_practicing` + `organic_certified` consistent
  across vineyards.json, dietary.json, hidden-gems.json. respekt-BIODYN (NOT
  Demeter) correctly named in dietary.json. The apparent prose date conflict
  (vineyards "certified biodynamic since 2015" vs dietary/hidden-gems
  "biodynamic since 2005") is NOT a defect: web-verified timeline is 1984
  organic, 2005 biodynamic practice, **2015 respekt-BIODYN certification** —
  both dates are accurate references to different milestones. Status field
  correctly stays `biodynamic_practicing`, not certified.
- **Melsheimer** — `demeter_certified` + Demeter certifier + 2013 cert year,
  consistent in dietary.json and hidden-gems.json. Genuine Demeter estate.
- **Weiser-Kunstler** — `organic_certified` (not promoted to biodynamic
  certified), consistent. Status `biodynamic_practicing` retained.
- **Trossen** — natural + organic_certified; **Weingut Stein** — natural only,
  consistent in dietary.json and hidden-gems.json. No certified-body fabrication.

**FIXED — broken `vineyard_ref` (referential, not gated by ship_safety):**
- dietary.json `weiser-kunstler-organic` had `vineyard_ref: "weiser-kunstler"`,
  but the real vineyards.json slug is `weiser-kuenstler`. Corrected to
  `weiser-kuenstler`. (Melsheimer/Trossen `vineyard_ref` values point at their
  own dietary/hidden-gems slugs by design — those growers are intentionally
  dietary/hidden-gems-only, not in the 42 vineyards — so they are self-references,
  left as-is.)

## Section G — Cross-link sanity — PASS

- `wines[*].pairings[*].tablejourney_ref`: 0 non-null across all 143 cuvées
  (research correctly nulled them — no TJ Mosel city). ✓
- food-pairing.json: all 8 TJ refs HEAD-resolve **200** and sit under real TJ
  German cities (germany/munich + germany/berlin):
  schweinshaxe, obatzda, weisswurst, munich/restaurants (Munich);
  currywurst, eisbein, koenigsberger-klopse, berlin/restaurants (Berlin).
  No invented paths. ✓

## Section H — Voice + prose — PASS

- 0 em/en dashes anywhere (recursive scan).
- 0 AI-tells (nestled/vibrant atmosphere/culinary journey/carefully crafted/
  must-visit/to die for/tucked away).
- editorial_score CV across 376 scored entities = 0.0518 (> 0.04 threshold) —
  no score-bunching.
- 0 description clones within any single topic file. (Same producer appearing
  in vineyards + dietary + hidden-gems with distinct copy is expected and fine.)
- The 165-220 char descriptions QA1 flagged are WARN-level length only; no clones.

## Section I — Cuvée taste-note sourcing — PASS (gate clean, 1 acknowledged WARN)

24 cuvées carry taste blocks; 21 with editorial_score >= 4.5 spot-checked. Opened
the cited `cuisine_evidence_url` for the suspect clusters:

- **Dr. Loosen** (per-product + collection pages), **Van Volxem** (per-product),
  **Heymann-Lowenstein** (per-site Uhlen/Roettgen pages), **Peter Lauer** (single
  product page): descriptors confirmed present on the cited page (e.g. Loosen WS
  Kabinett "white peach... green apple... slate"; Lauer Fass 6 "aromatic, juicy,
  vibrant, fine"). Sound.
- **Selbach-Oster** (6 cuvées → /lagen-2/) and **Maximin Grunhaus** (5 cuvées →
  /vineyards): the descriptors used ARE present verbatim on the cited producer
  pages ("salty minerality", "yellow-fruity, fine-floral", "herbaceous spicy,
  smoky-salty", "refined terroir", "delicate fruit") — but at **Lage (site)
  granularity**, applied to multiple cuvées from the same site, not per-bottling.
  This is the producer's own sourced text, NOT fabrication and NOT a homepage/
  third-party directory (the Rioja failure mode), so the descriptors are retained.
  Logged as the single acknowledged cuvee-taste WARN (matches QA1's "1 WARN" /
  ship_safety WARN=1). Not a hard defect; no taste blocks removed.
- Descriptor diversity across the catalog is good (no template "dark cherry,
  leather" repetition). No invented sensory copy found.

## Section J — Tag vocabulary conformance — PASS

- All `wines[*].tags` across 143 cuvées appear in docs/WINE_TAGS.md. 0 unknown tags.
- 0 derived-axis leakage: no price-*, ageing, production (biodynamic/organic/
  natural/vegan), grape, world, or sweetness (dry/off-dry/etc.) tags emitted by
  the researcher. Residual sweetness correctly NOT present as a tag (it's derived
  from `sweetness`).

## Section K — Vintage-agnostic discipline — PASS

- 0 cuvée slugs or names contain a 4-digit year. Different Pradikat levels of the
  same vineyard are separate cuvées (correct), not vintage-split.

## Summary

Total defects: 3 (all corrected in-place)
1. [D] reichsgraf-von-kesselstatt — stale owner (deceased Annegret Reh-Gartner)
   → Reh family / Dr. Karsten Weyand.
2. [D] vollenweider — stale owner/winemaker (Daniel Vollenweider sole) → Moritz
   Hoffmann; description reconciled.
3. [E] dietary.json weiser-kunstler-organic — broken vineyard_ref
   (weiser-kunstler → weiser-kuenstler).

1 acknowledged WARN (Section I site-level descriptor sourcing on Selbach-Oster +
Maximin Grunhaus — real producer text, retained). No fabrication found in
classification (QA1), scores (QA1), ownership, certification, TJ cross-links,
taste notes, tags, or vintage discipline. ship_safety re-run after fixes: 0 HARD,
PASS.
