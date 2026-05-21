# QA report -- Gdańsk (QA2 judgment pass)

Date: 2026-05-19
Scope: poland/gdansk -- full dataset, 27 topic files
QA1 verdict: PASS (4 entities removed, 14 prose rewrites, 3 festival
corrections). QA2 = independent re-pass.

---

## Pass-1 carry-forward (re-verified)

- verify_entities.py hard failures: 0
- check_internal_references.py: ERR=0 WARN=0 after QA2 edits
- validate_data.py: 0 ERR, ~60 cap-band WARN (length-cap drift, pre-existing,
  out of QA scope per prompt section F)

QA1's 4 removed slugs (pod-lososiem, vinifera-gdansk, targ-rybny market,
gdansk-fish-fair) confirmed absent across the full data tree. QA1's 14
entity-prose rewrites largely held; two missed echoes found below.

---

## QA2 judgment defects found and fixed

### A2. Specific-fact mismatches against operator menu/press (new defects)

**1. Pierogarnia Mandu cod pierogi fabrication -- FIXED**
- JSON claimed across 4 entity entries + 1 signature-dish history that
  Mandu's signature is "cod-and-dill pierogi" / "Pierogi z dorszem (cod
  pierogi)" / "the Baltic cod pierogi are the local pick".
- Actual: WebFetch of Mandu's own menu page
  (pierogarnia-mandu.pl/en/gdansk-centrum/menu/) returned ONLY salmon as
  the fish pierogi -- "Hand-made salmon paste, sundried tomatoes and
  cream cheese served with dill sauce". No cod. No dorsz. Cod pierogi
  fabricated as Mandu's pick.
- Stary Młyn DOES serve cod pierogi (cod, bacon, béchamel in black pastry,
  confirmed via search). The signature-dishes entry stays valid; only the
  Mandu attribution is the defect.
- Fix:
  - `restaurants.json` Mandu Śródmieście: signature_dishes -> ["Salmon-
    and-dill pierogi", "Pelmeni"]; description rewritten to lead with
    salmon-and-dill on the fish side; must_order swapped to salmon.
  - `casual-dining.json` Mandu Śródmieście: same fix.
  - `casual-dining.json` Mandu Oliwa: signature_dishes -> ["Salmon
    pierogi", "Sweet plum pierogi"]; must_order swapped to salmon.
  - `budget-eating.json` Mandu: description rewritten so salmon-and-dill
    is the room's fish pick.
  - `signature-dishes.json` `pierogi-z-dorszem`: history rewritten to
    remove "Pierogarnia Mandu was the first Tri-City room" fabrication.
    Replaced with Stary Młyn's actual cod-bacon-béchamel preparation +
    Cała Naprzód's zander pierogi. where_to_eat reduced from 4 -> 2
    (Pierogarnia Stary Młyn, Cała Naprzód) -- both confirmed to actually
    serve fish/cod pierogi.

**2. Avocado Vegan Bistro "first vegan kitchen in Poland" overclaim -- FIXED**
- `dietary.json[vegan]` claimed Avocado is "the first vegan kitchen in
  Poland." Operator site does not assert this. Independent search:
  Avocado is the FIRST VEGAN RESTAURANT IN GDAŃSK (open since 2013) and
  "the first vegan catering in Poland, one of the first vegan
  restaurants in Poland." The Gdańsk-first claim is true; the
  Poland-first claim is not.
- Note: `restaurants.json` and `casual-dining.json` already used the
  softer "one of the first vegan kitchens in Poland" phrasing; only the
  dietary.json copy was overclaimed.
- Fix: rewrote dietary.json description to "the first vegan room in
  Gdańsk and among the earliest in Poland (open since 2013)" -- matches
  external sourcing.

**3. Mała Sztuka "stand at the bar" tip contradicts operator policy -- FIXED**
- `bars.json` Mała Sztuka tip said "arrive before 21:00 or expect to
  stand at the bar."
- Operator-confirmed: Mała Sztuka runs a "no-standing" policy. If no
  seats, you wait or come back.
- Fix: rewrote tip to "About fifteen seats and a no-standing policy;
  arrive before 21:00 or expect to wait for a table to open."

### C. Festival month / dates re-check

Re-verified St Dominic's Fair 2026 = 25 July to 16 August (QA1
correction holds; cross-confirmed via Tripadvisor 2026 forum thread,
bimcal.com 2026 listing, eventseye.com). Bread Festival on Skwer
Heweliusza, Sunday of opening weekend, 26 July (QA1 correction holds).

Wianki / St John's Eve: Gdańsk's St John's Day festivities span 21-27
June historically (local-life.com source), with the Wianki wreath-
floating concentrated on the 23rd; the JSON's start_day 22, end_day 23
"two-evening" framing is consistent with that. Left as-is.

Christmas Market, Fat Thursday at Paradowski, all confirmed against
external sources. No further date defects.

### E. Editorial-prose echoes (QA1 rewrite verification)

**E2. Two QA1-missed echoes of removed "Targ Rybny working market" claim -- FIXED**

- `itineraries.json` Baltic-fish-deep-dive summary: read "Three days
  following the Baltic catch from boat to plate: **the dawn market**,
  a Granary Island fish kitchen, a Hel Peninsula smokehouse day..."
  The "dawn market" phrase echoes the removed Targ Rybny morning
  fish-market claim. Rewrote to "a Motława waterfront morning, a
  Granary Island fish kitchen, a Hel Peninsula smokehouse day..."

- Same itinerary day-1 title: "Day 1: Targ Rybny morning, lunch at
  Zafishowani, ARCO tasting" + morning prose "Walk Targ Rybny on the
  Motława waterfront from 08:00". Title implied the removed fish-
  market context; rewrote title to "Day 1: Motława waterfront, lunch
  at Zafishowani, ARCO tasting" and prose to "Walk the Targ Rybny
  restaurant square on the Motława from 08:00" (accurate now: square
  has Mercato, Targ Rybny - Fishmarkt, Zahir Kebab as real
  restaurants, no working market).

All other Targ Rybny references across the tree describe the square as
a present-day restaurant location or refer to the named restaurants on
it -- accurate per QA1's framework.

### Other QA2 spot-checks (no defects)

- ARCO by Paco Pérez, 33rd floor Olivia Star, Antonio Arcieri running
  the pass, first Michelin star in Gdańsk 2024 -- all reverified.
- Eliksir, Paweł Wątor + Mateusz Trzeciak, foodpairing concept, first
  Polish Green Star -- reverified.
- Sztuczka, Wałęsa Brothers, Rafał Wałęsa chef-owner, Stara Stocznia
  20/9, Opening of the Year 2025 -- reverified.
- Restauracja Kubicki, 1918, Wartka 5 (opened January 1919 per gdansk.pl
  centennial article; "operating since 1918" framing is the Kubicki
  company's own version, acceptable editorial latitude) -- reverified.
- Restauracja Fino, Jacek Koprowski, 435 PLN plant-based parallel menu
  -- reverified.
- Treinta y Tres, 33rd-floor sister to ARCO, Bib Gourmand 2024 + 2025
  -- reverified.
- True, Surf & Turf concept on Granary Island -- reverified.
- Tygle Gdańskie, three-track meat/seafood/vegetarian Michelin
  Recommended -- reverified; vegetarian-itinerary use is accurate.
- Cała Naprzód, fourth-floor Maritime Culture Centre at Długie
  Pobrzeże, Kashubian/Baltic menu -- reverified.
- Velevetka, Kashubian cellar room at Długa 45 -- reverified.
- Brovarnia, Złoto Brovarni gold at Concours de Lyon 2022 -- reverified.
- Eat Polska 4-hour food tour: 10+ tastings, vodka shot, bilingual,
  meet at Scandic Hotel ul. Podwale Grodzkie 8 -- reverified.
- 1911 Sopot Bib Gourmand + Fisherman Sopot Michelin-recommended (day-
  trips Sopot entry) -- reverified.

### D. Thin-category re-check

All dietary sub-categories at floor (2 each except kosher at 0, where 0
is the correct call -- no functioning kosher restaurant in Gdańsk).
QA1's content checks for each entry hold. No fabrications.

### F. Editorial voice / AI-tells

No new egregious AI-tells. The cap-band length WARNs noted by the
validator are within the existing topic-wide drift (mostly +20 to +60
chars over the cap upper bound) -- not regressions, not the QA scope.

QA1's noted typo `cuisine_taway` in `cooking-classes.json` for the
Pierogi Masterchef entry left as-is per QA1's call.

---

## Defects total: 6

- A2 specific-fact: 3 (cod pierogi fabrication across 5 files; vegan
  primacy overclaim; Mała Sztuka no-standing policy)
- E2 echoes: 2 (fish-dive summary "dawn market"; fish-dive day 1 title +
  morning prose still anchored on fish-market framing)
- C festival: 0 corrections (QA1 corrections all hold; spot-checks
  confirm)

Six defects across 180+ entities and 27 files; all fixed in place.
None required entity removal.

---

## Below-floor topics after QA2

Unchanged from QA1:
- `markets.json`: 5 (floor 6, 1 below)
- `festivals.json`: 5 (floor 6, 1 below)
- All other topics at or above floor.

QA2 did not remove any entities. Below-floor state is honest-thin, not
QA2-driven.

---

## Verdict

VERDICT: PASS

6 judgment defects found and fixed. All A2 / E2 / overclaim class.
No fabricated entities to remove. No festival date defects beyond
QA1's catches. Internal references and JSON shape clean after edits.

Key learning for upstream prompts: when an entity claims a specific
dish that is also a city-wide signature dish, the research agent must
content-check the operator's actual menu -- not just the operator's
existence. The Mandu cod pierogi fabrication is the same Charleston /
Atlanta defect class (Jack of Cups chana masala, Street Bird fried
shrimp) flagged in section A2 of the QA prompt; tighten the research
prompt to require a menu-string substring check for every "signature_
dishes" item it writes.
