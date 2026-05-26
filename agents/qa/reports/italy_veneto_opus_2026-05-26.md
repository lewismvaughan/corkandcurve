# Opus Final QA Report: italy/veneto — 2026-05-26

Agent: Opus final QA (narrow read)
Post-QA1 (17 fixes) + QA2 (35 fixes). ship_safety entered at 0 HARD.
Data scale: 51 vineyards, 162 cuvées, 26 topic files.

Result: **OPUS-FOUND-7** (all remediated; ship_safety still 0 HARD).

---

## Narrow-read checks performed

- **30-entity skim** across all topics for fabricated winemaker/owner names,
  fabricated press credentials, claim/source mismatch.
- **Itinerary end-to-end** (`natural-wine-gambellara-vinnatur` + others):
  the schema's `days[*].venues[*]` slug arrays are ABSENT from every Veneto
  itinerary (prose-only). `check_internal_references.py` flags this as WARN
  (backfill-pending), not ERR — known soft gap, not a QA1/QA2 regression.
  All producers named in itinerary prose that ARE in-dataset resolve.
- **Festivals end-to-end**: Vinitaly = April (PASS), Amarone Opera Prima =
  late Jan/early Feb with correct "formerly Anteprima Amarone" note (PASS).
  All 8 festivals have street-level `address_quoted` and month claims that
  match `recurrence_pattern`. No defects.
- **Cuvée end-to-end** (`gini-soave-classico-la-frosca`,
  `quintarelli-amarone-classico`): producer slugs resolve, per-cuvée
  `cuisine_evidence_url` is a real per-wine page (ginivini.com/la-frosca;
  wine-searcher per-wine listing for Quintarelli where no public tech sheet
  exists), every tag in WINE_TAGS.md, no derived-axis tag leakage, no vintage
  in slug/name. Full-catalog sweep: 0 unknown tags, 0 derived-axis tags,
  0 slugs/names with a year, all 162 producers resolve, all `pairings[*]`
  `tablejourney_ref` null (no broken TJ refs), 0 fabricated scores.
- **editorial_score >= 4.7 spot-check** (42 cuvées at >=4.7): all map to
  genuinely prestigious bottlings (Quintarelli, Dal Forno, Pieropan La
  Rocca/Calvarino, Allegrini La Poja, Masi Mazzano/Campolongo, Maculan
  Acininobili/Torcolato, Bertani Villa Novare, Anselmi I Capitelli). No
  no-name-estate inflation. Defensible.
- **Prose sweep** (all 26 files): 0 em-dashes, 0 en-dashes, 0 ` -- `,
  0 AI-tells. QA2's prose fixes held.

---

## Defects found and remediated (7)

### D-class — fabricated / garbled owner+winemaker attributions (5)

This is a **structural research regression**, concentrated on
Prosecco-zone and a few Valpolicella/Custoza producers where the research
agent guessed plausible-but-wrong family/personal names. QA2 Section D
sampled only the marquee estates (Bertani, Masi, Allegrini, Zenato) and
missed the smaller producers. Five confirmed:

1. **`bele-casel`** — `owner`/`winemaker` = "Gregoletto family". Bele Casel
   (Caerano di San Marco) is not the Gregoletto estate; Gregoletto is a
   separate, unrelated Veneto producer. Cited source (wine-searcher listing)
   does not establish any family name. **Fix:** nulled owner+winemaker;
   scrubbed "Gregoletto family" from wines.json history summary + milestone.

2. **`col-vetoraz`** — `owner` = "Dal Cero, De Bortoli and Malanotte
   families". De Bortoli is plausible; "Dal Cero" (a Soave producer) and
   "Malanotte" (a Raboso DOCG appellation, not a family) are wrong. **Fix:**
   nulled owner; rewrote wines.json history to "founded in 1993" without the
   fabricated family list.

3. **`gorgo`** — `owner`/`winemaker` = "Cristina Right" (propagated to
   3 wines.json fields incl. a "one of the few female winemakers" claim and
   a 1966-founded-by-Cristina-Right milestone). Not associated with Gorgo
   (Custoza). **Fix:** nulled owner+winemaker; scrubbed the name from
   vineyard description + 3 wines.json summaries/description.

4. **`ruggeri`** — `owner` = "Bisol family (Matteo Bisol as director)".
   Wrong-sibling cross-contamination (C3-class): Matteo Bisol directs
   Bisol 1542 / Venissa, not Ruggeri. **Fix:** trimmed to "Bisol family".

5. **`brigaldara`** — `owner`/`winemaker` = "Cesare Stefani" with a
   fabricated "acquired estate in 1986" milestone (propagated to 6
   locations) that also contradicted the entry's own `origin_year: 1988`.
   Real owner is the Cesari family. **Fix:** owner -> "Cesari family",
   winemaker -> null; rewrote history to drop the invented person and the
   contradictory 1986 acquisition year (milestone year aligned to 1988).

### Slug/name mismatch — fabricated slug stem (1)

6. **`wine-restaurants.json` `osteria-ambasciatore-verona`** — slug stem
   "osteria-ambasciatore" but `name`, `address` (Vicolo Scudo di Francia 3),
   and all evidence URLs are Antica Bottega del Vino. Same class QA2 caught
   with `inama-soave-classico-vulcaia`. The venue is real and correctly
   sourced; only the slug was wrong, and it collided conceptually with the
   genuine `antica-bottega-del-vino-verona` entity in wine-bars.json (a
   legitimate cross-TOPIC appearance, not a clone). **Fix:** slug renamed to
   `antica-bottega-del-vino-ristorante-verona` (matches its `name`, unique
   across restaurants, distinct from the wine-bar slug). No cross-refs to
   the old slug existed.

### H-class — factual conflation + soft superlative (1)

7. **`tasting-rooms.json` `villa-cordevigo-villabella-tasting`** —
   description claimed "the estate's 5-star Michelin setting makes this one
   of Veneto's most elegant winery visit experiences." "5-star Michelin" is
   a nonsense rating (conflates the property's 5-star hotel classification
   with the 1-Michelin-star Oseleta restaurant), plus a soft AI-tell
   superlative. **Fix:** rewritten to the accurate facts — five-star Villa
   Cordevigo Wine Relais + one-Michelin-star Oseleta restaurant.

---

## Quality observation (not a defect — for orchestrator)

**QA2 WARN assessed — NOT actionable as a HARD defect.** 17 of 37
Amarone/Valpolicella cuvées open their `taste.aroma` array with exactly
"dried cherry, tobacco". These are the canonical, accurate Amarone
descriptors (not fabricated), and the 3rd-6th descriptors do vary per cuvée
(leather / cedar / dark chocolate / dried herbs / dried violet / spice in
differing orders). Per the brief, I HARD-act only if descriptors are
fabricated rather than merely similar — these are real, so no removal.
Observation for the orchestrator: on the live cuvée pages the repeated
two-word opener will read as mildly templated across the Amarone category.
If desired, a future research-prompt tweak could ask for a distinctive
lead descriptor per cuvée. Cosmetic only; does not block ship.

---

## Files modified

1. `site-data/italy/veneto/data/vineyards.json` — owner/winemaker scrubs on
   bele-casel, col-vetoraz, gorgo, ruggeri, brigaldara (+ description prose)
2. `site-data/italy/veneto/data/wines.json` — history/description prose
   scrubs for bele-casel, col-vetoraz, gorgo (x3), brigaldara (x4)
3. `site-data/italy/veneto/data/wine-restaurants.json` — slug rename
   (osteria-ambasciatore-verona -> antica-bottega-del-vino-ristorante-verona)
4. `site-data/italy/veneto/data/tasting-rooms.json` —
   villa-cordevigo-villabella-tasting "5-star Michelin" conflation fixed

Counts unchanged: 162 wines, 51 vineyards. No entities removed.

---

## Post-edit verification

```
bash scripts/ship_safety.sh italy veneto          -> ALL CHECKS PASSED (0 HARD)
check_internal_references.py --country italy --city veneto -> ERR=0 WARN=14 (venues backfill)
JSON parse: vineyards/wines/tasting-rooms/wine-restaurants -> OK
Residual fabricated strings (Gregoletto / Dal Cero / Cristina Right /
  Cesare Stefani / "Matteo Bisol as director" / osteria-ambasciatore /
  "5-star Michelin")                               -> NONE FOUND
All 162 producers resolve; no duplicate restaurant slugs.
```

---

## Upstream prompt-hardening recommendation

The dominant finding is a **D-class owner/winemaker fabrication cluster**
(5 of the smaller/non-marquee producers). QA1/QA2 Section D only sampled
the famous estates. Recommended hardening, in priority order:

1. **wine-research PROMPT / SCHEMA:** `owner` and `winemaker` MUST be backed
   by a source that NAMES the person/family — a wine-searcher search/listing
   URL or a consortium directory does NOT establish a family name. If the
   only available source is a listing/aggregator, emit `null`, never a
   guessed family name. (Five Veneto producers had family names that the
   cited source could not support; two were cross-contaminated from
   unrelated Veneto names — Dal Cero, Malanotte, Gregoletto.)

2. **QA Section D:** broaden the ownership sample beyond the marquee estates
   to include EVERY producer carrying a named-individual or multi-family
   `owner` — these are exactly where the agent guesses. Add the wrong-sibling
   / cross-region-name check (C3-style) for owner names: a family name that
   belongs to a DIFFERENT known regional producer is a red flag (Gregoletto,
   Dal Cero).

3. **QA scrub discipline reminder (already in PROMPT step 4):** the
   fabrications propagated into wines.json history summaries + milestones,
   not just vineyards.json — confirms the cross-file scrub rule. The
   brigaldara case also paired a fabricated owner with a fabricated
   acquisition YEAR that contradicted the entry's own origin_year; QA should
   cross-check `history.origin_year` vs `milestones[*].year` for internal
   consistency.

4. **Slug-stem hygiene (recurring):** `osteria-ambasciatore-verona` repeats
   the `inama-soave-classico-vulcaia` pattern — a slug stem that doesn't
   match the entity's own `name`. Add a mechanical check: warn when the
   entity `name` shares no token with its `slug` stem.

OPUS-FOUND-7 italy/veneto
