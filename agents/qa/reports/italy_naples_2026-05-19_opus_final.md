# Opus final QA report -- Naples (4th-stage validation)

## Headline

Opus pass found defects. Per Lewis 2026-05-19 directive ("preferably the
opus pass shouldnt actually find any issues; if you do, we need to refine
more"), this signals that QA1 and QA2 missed a systemic defect class.
**Upstream prompts need refinement** (see Section "Upstream gap" below).

## QA1 + QA2 carry-forward verification

All four QA1 removals and four QA2 removals confirmed gone from data tree:
- `lebbrezza-vomero`, `stanza-vomero`, `lebbrezza-noe-vomero-bar`,
  `secret-food-tours-pizza-class` (QA1) -- clean.
- `lantiquario`, `lantiquario-wine`, `lantiquario-late`, `freccia-azzurra`
  (QA2) -- clean.

QA2 prose rewrites in `itineraries.json`, `region.json`, `bars.json`,
`late-night.json` verified.

## Sample sweep (10 entities QA1 + QA2 likely did not re-check)

Sampled with `random.seed(42)`. Confirmed clean against
`cuisine_evidence_url` or external search:

1. `starita-fritti` (street-food) -- pizzeriastarita.it own-site (TLS flake)
   + 50topitaly mentions confirm real venue. Clean.
2. `poppella-brunch` (brunch) -- pasticceriapoppella.com confirms Sanita
   pastry shop, fiocco di neve since 1920. Clean.
3. `mary-galleria-bakery` (bakeries) -- 50topitaly URL stale (404 after
   redirect) but Yelp + TripAdvisor confirm Galleria Umberto I 66.
   Operator real; evidence URL needs refresh in next research pass.
4. `osteria-della-mattonella` (casual-dining) -- own-site is mostly spam
   shell, but Culinary Backstreets + TripAdvisor + Yelp all confirm Via
   G. Nicotera 13, family trattoria since 1978. Clean. Evidence URL
   should be moved off own-site to Culinary Backstreets in next pass.
5. `il-garibaldino-cd` (casual-dining) -- **DEFECT (see Section A.1)**.
6. `trattoria-nennella-cd` (casual-dining) -- own-site confirms
   Piazza Carita, Quartieri Spagnoli, since 1949. Clean.
7. `di-matteo-budget` (budget-eating) -- own-site TLS flake but Yelp +
   anticapizzeriadimatteo.it confirm Via Tribunali 94 since 1936. Clean.
8. `luminist-cafe-bistrot` (brunch) -- Michelin guide URL returns 403
   (anti-bot); operator existence corroborated. Clean.
9. `berevino-storico` (wine-bars) -- **DEFECT (see Section A.4)**.
10. `pizzeria-brandi` (restaurants) -- own-site confirms Via Chiaia 1889
    Margherita origin. Clean.

## QA2-flagged cuisine_unverified resolutions

QA2 left three entries flagged for evidence URL replacement.

### `archivio-storico` (bars) + `archivio-storico-late` (late-night)

**REMOVED.** Real venue exists, but at Via Alessandro Scarlatti 30,
Vomero (per the operator's own page archiviostorico.com and apetime.com
listing) -- NOT at Vico Belledonne a Chiaia 23 as JSON claims. The
"Belledonne strip" framing came from QA2's prose rewrite when it
replaced removed `lantiquario` ("Mediterranean spritz, fig and
absinthe"). The Vomero venue does serve Mediterranean-flair cocktails,
but the Chiaia address is fabricated. Per Lewis's "no fabricated
replacements" rule, removing rather than papering over with a
description rewrite to Vomero (which would conflict with the QA2
itineraries prose anchor and the description's "alongside Le Caveau"
clause that depends on the now-removed Le Caveau).

### `la-stanza-del-gusto` (wine-bars) + `stanza-del-gusto-bar` (bars)

**FIXED.** Real venue at Via Costantinopoli 100 corroborated by
Lonely Planet, Luciano Pignataro Wine Blog, Yelp, TripAdvisor.
`source_url` + `open_evidence_url` updated to Yelp listing;
`cuisine_evidence_url` updated to Lonely Planet entry.

### `le-caveau` (wine-bars) + `le-caveau-bar` (bars)

**REMOVED.** The Naples venue named "Le Caveau" is a discoteca near
Mergellina station (per angelipierre.it) -- NOT a French-style wine
bar at Vico Belledonne a Chiaia 26 as JSON claims. Address fabricated;
"300-bottle natural wine list / Burgundy cellar" character entirely
fabricated. The lecaveau.it placeholder source_url cannot support
existence at the claimed address.

## Judgment defects found

### A. Fabricated or hallucinated-address venues

**A.1 `il-garibaldino-cd` (casual-dining) + `il-garibaldino` (restaurants)** --
REMOVED in both topics. The booking_url / source_url `ilgaribaldino.it`
resolves to a B&B + restaurant in San Giovanni in Marignano (Romagna),
not Naples. No restaurant by that name exists in Naples (Pignasecca
search returns Trattoria Pignasecca, Pizzeria al 22, etc., none called
Il Garibaldino). Other Il Garibaldino restaurants exist in Portoferraio
(Elba) and Viareggio. Naples claim wholly fabricated. **Same defect
class as QA2's `lantiquario` (Miami tile co) and `freccia-azzurra`
(Vienna model railway co): a real .it domain that points to a different
business, address invented to match the city.**

**A.2 `archivio-storico` (bars) + `archivio-storico-late` (late-night)** --
REMOVED. See "QA2-flagged" section above.

**A.3 `le-caveau` (wine-bars) + `le-caveau-bar` (bars)** -- REMOVED.
See "QA2-flagged" section above.

**A.4 `berevino-storico` (wine-bars)** -- REMOVED. JSON claims a
"Berevino Centro Storico branch" at Vico San Filippo e Giacomo 31,
sharing TripAdvisor source_url with `berevino`. The single TripAdvisor
listing is for ONE Berevino WineBar in Chiaia; no second Centro
Storico branch exists per web search ("due sedi" / "second location"
search returned no results). Fabricated branch.

### B. Hallucinated address on real venue (fixed in place)

**B.1 `barril` (bars), `barril-wine` (wine-bars), `barril-late`
(late-night)** -- FIXED. Real cocktail bar Barril in Naples is at
**Via Giuseppe Fiorelli 11, 80121 Napoli** (per apetime.com listing,
confirmed by multiple Naples cocktail-bar guides). JSON had **Via Santa
Maria della Neve 9, 80132 Napoli** -- street fabricated, plausible
postal code. All three Barril topic entries corrected (address +
verified.address_quoted updated).

### C. Cuisine-mismatch reflagged

None beyond Sections A/B.

### D. Festival dates

Not re-checked at Opus stage -- QA1 + QA2 both did this work and
ship_safety pass-1 covers month evidence.

### E. Editorial-prose closed-venue echoes

After Section A removals:
- `itineraries.json` day-1 evening prose referenced "Pre-dinner aperitivo
  at Archivio Storico on Vico Belledonne a Chiaia 23". Rewritten to
  "Pre-dinner aperitivo at Barril on Via Giuseppe Fiorelli 11".
- `itineraries.json` day-1 venues array contained `archivio-storico`.
  Replaced with `barril`.
- `region.json` bars SEO description "Archivio Storico, Barril,
  Gambrinus and 11 more". Rewritten to "Barril, Gran Caffe Gambrinus,
  L'Ebbrezza di Noe and four more".
- `region.json` bars SEO title count "14 Cocktail Bars" updated to
  "5 Cocktail Bars" (reflects actual count after removals).
- Final grep for `Garibaldino`, `Le Caveau`, `Archivio Storico`,
  `Santa Maria della Neve`, `Berevino Centro` returned zero matches.

## Entities removed (Opus pass)

1. `il-garibaldino-cd` (casual-dining) -- fabricated Naples venue (URL
   points to Romagna B&B).
2. `il-garibaldino` (restaurants) -- same.
3. `archivio-storico` (bars) -- real Vomero venue, fabricated Chiaia
   address.
4. `archivio-storico-late` (late-night) -- same.
5. `le-caveau` (wine-bars) -- Naples Le Caveau is a discoteca near
   Mergellina, not a French wine bar in Chiaia.
6. `le-caveau-bar` (bars) -- same.
7. `berevino-storico` (wine-bars) -- fabricated second branch.

## Entities fixed (Opus pass)

1. `barril` (bars) -- address Via Santa Maria della Neve 9 -> Via
   Giuseppe Fiorelli 11.
2. `barril-wine` (wine-bars) -- same.
3. `barril-late` (late-night) -- same.
4. `la-stanza-del-gusto` (wine-bars) -- evidence URL rotated to
   Lonely Planet + Yelp.
5. `stanza-del-gusto-bar` (bars) -- same.

## Defects total: 7 removals + 5 entity-level fixes + 4 prose-echo fixes

## Below-floor topics after Opus pass

- dietary/vegan: 3 (floor 4)
- dietary/vegetarian: 2 (floor 4)
- dietary/gluten_free: 3 (floor 4)
- dietary/halal: 2 (floor 4)
- cooking-classes: 3 (floor 4)
- bars: 5 (down from 7 after Opus; floor varies by topic)
- wine-bars: 5 (down from 7; floor varies)
- late-night: 5 (down from 6)

Section needs research backfill before next ship_safety; below-floor is
acceptable per Lewis's standing rule (do not fabricate replacements).

## Production smoke test

- `curl -sI https://tablejourney.com/italy/naples/` -> HTTP 200.
- `curl -sI https://tablejourney.com/italy/naples/restaurants/` -> HTTP 200.
- `curl -sI https://tablejourney.com/italy/naples/wine-bars/` -> HTTP 200.
- `curl -sI https://tablejourney.com/italy/naples/bars/` -> HTTP 200.
- Page body grep: zero matches for "Il Garibaldino", "Le Caveau",
  "Archivio Storico", "Santa Maria della Neve". Removed entities are
  not leaked.
- Price tier renders as Euro symbols (9 x EUR EUR, 7 x EUR EUR EUR in
  restaurants page). No placeholders, no FIXME, no TODO in body.

## Upstream gap (defect class for prompt refinement)

The defect class Opus surfaced is **address hallucination on real
domains**:

- A real .it/.com domain serves as `source_url`. HEAD-check passes
  (pass-1 verify_entities.py is satisfied).
- The address in the JSON is plausible-Naples (correct postal code,
  real street) but is NOT the venue's actual address.
- `address_quoted` in the verified block mirrors the JSON address
  (since the research agent wrote both), so the fuzzy-match check
  trivially passes.
- The venue at the JSON address either does not exist, or is a
  different establishment, or is the same operator at a different
  location.

QA1 caught the pure URL-fabrication subclass (Miami tile co, Vienna
model railway co) because the .com pointed to wrong industries. QA2
deepened this with the `lantiquario` cluster. **Neither QA pass
caught the harder subclass where the URL matches the operator name
but the address is invented**: `il-garibaldino.it` is a real
restaurant domain (Romagna), `barril.it` is the real Naples Barril
domain but at a different street, `archivio-storico.it` is the real
Vomero Archivio Storico site at a different neighborhood, etc.

**Recommended prompt updates:**

1. **Food-research SCHEMA.md provenance block**: add a hard requirement
   that `address_quoted` be lifted from an INDEPENDENT directory
   (Yelp / TripAdvisor / 50topitaly / Lonely Planet / official tourism
   board), not from the venue's own site. Own-site placeholder pages
   and "Coming Soon" templates cannot quote the address.

2. **verify_entities.py extension**: when `source_url` is the venue's
   own domain and `address_quoted == entity.address` verbatim,
   trigger a warning to require a second independent source (Yelp,
   TripAdvisor, or a directory) whose address also fuzzy-matches.
   This catches the case where the research agent invented an address
   and then echoed it into address_quoted.

3. **QA prompt.md Section A extension**: when sampling for cuisine
   match, also fetch one independent directory entry (Yelp /
   TripAdvisor / Lonely Planet) and confirm the street name in JSON
   appears on the directory page. Naples Opus would have caught
   `barril`, `il-garibaldino`, `le-caveau`, `berevino-storico` in 4
   independent-directory checks.

4. **Specific Naples cleanup before next research backfill**: the
   `berevino` (chiaia) entry has neighborhood field "chiaia" but
   description and address claim Centro Storico. The TripAdvisor
   listing locates it in Chiaia. Address `Via Sant'Anna dei Lombardi
   31` (centro storico) may also be hallucinated. Flag for research
   agent: re-verify Berevino's actual address against Yelp / Italian
   directories.

## Verdict

VERDICT: NEEDS_FIXES

Opus removed 7 fabricated entities and fixed 5 + 4 prose echoes that
QA1 and QA2 missed. The volume + the systematic nature (address
hallucination on real-operator URLs) means the upstream QA prompt
needs the four refinements listed above. After those land, future
cities should see Opus find zero or near-zero defects on a properly
researched dataset.
