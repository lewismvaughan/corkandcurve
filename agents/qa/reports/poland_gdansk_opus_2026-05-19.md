# QA report -- Gdańsk (Opus final pass)

Date: 2026-05-19
Scope: poland/gdansk -- full dataset, 27 topic files, 180 entities
Prior passes: QA1 (Sonnet) PASS with 21 defects fixed; QA2 (Sonnet) PASS with 6 defects fixed.
Opus final = narrow third read on the cleaned dataset. Expectation per policy: zero defects.
Actual: 12 defects found. All fixed in place. Verdict: PASS, but a research-stage regression
report is included below for harvesting into agents/qa/PROMPT.md and
agents/food-research/PROMPT.md.

---

## Pass-1 carry-forward (re-verified)

- check_internal_references.py: ERR=0 WARN=0 after Opus edits.
- validate_data.py: 0 ERR, 175 cap-band WARN (length-cap drift, out of QA scope per
  prompt section F; unchanged in count from QA2).
- No em-dashes or en-dashes anywhere in the dataset (grep clean).
- All QA1 + QA2 entity removals (pod-lososiem, vinifera-gdansk, targ-rybny market,
  gdansk-fish-fair) confirmed absent.

---

## Judgment defects found (and root cause vs prior passes)

### A. Cuisine / specific-fact mismatches against operator's actual source

**A1. Cukiernia Paradowski address `Wajdeloty 19` is fabricated. Correct: `Wajdeloty 11` -- FIXED**

- Slipped past QA1+QA2 because pass-1's `address_quoted` fuzzy match is against
  the JSON's own `entity.address` field, not against the cited source page content.
  Both fields agreed (both wrong), so pass-1 passed.
- The cited source itself (gedanopedia.pl, the article the JSON quotes) says
  "Gdańsk-Wrzeszcz, ul. Wajdeloty 11" and explicitly describes Andrzej "odzyskał
  on lokal przy ul. Wajdeloty 11" (recovered the premises at ul. Wajdeloty 11).
  The trojmiasto.pl listing and gdansk.pl Fat-Thursday article both confirm
  Wajdeloty 11.
- This is the Naples Opus 2026-05-19 defect class (address fabrication where
  both fields agree but neither matches the real venue address from the cited
  source).
- Fix applied to bakeries.json (entity address + verified.address_quoted) and
  festivals.json (fat-thursday-paradowski entity address + verified.address_quoted).

**A2. Drukarnia Cafe "from 08:00" in itineraries weekend day 1 morning -- FIXED**

- Itineraries weekend day 1 morning said "Coffee at Drukarnia on Mariacka from 08:00".
- Drukarnia opens 10:00 daily (inyourpocket; yelp). The cafe entity itself in
  cafes.json correctly says "Arrive before 11:00 weekends for a seat by the
  front window" -- consistent with 10:00 open.
- Slipped past QA1+QA2 because the itinerary prose carried a different opening
  time than the entity it referenced. Section A2 "Itinerary editorial sweep --
  ALL strings" plus hours-cross-check would catch this; neither prior pass
  ran the hours cross-check against entity data.
- Fix: "from 08:00" -> "from 10:00".

**A3. Cafe Kamienica "at 10:00" in itineraries weekend day 2 morning -- FIXED**

- Cafe Kamienica opens 11:00 daily (restaurant guru listing).
- Same class as A2: itinerary prose time-anchored before venue actually opens.
- Fix: "Cafe Kamienica at 10:00" -> "Cafe Kamienica at 11:00".

**A4. Flisak '76 close time -- FIXED**

- bars.json tip claimed "Closes 03:00 Friday and Saturday".
- Operator's own site (flisak76.com): Sun-Thu 18:00-01:00, Fri-Sat 18:00-02:00.
- 03:00 close is wrong by one hour.
- Slipped past QA1+QA2 because hours are not in scope for verify_entities.py;
  no LLM pass cross-checked operator pages for hours.
- Fix: "Closes 03:00" -> "Closes 02:00".

**A5. signature-dishes.json pierogi-z-dorszem QA2 rewrite carries unverifiable specifics -- FIXED**

- QA2 rewrote the history field to replace the Mandu cod-pierogi fabrication
  with "Pierogarnia Stary Młyn turns out a cod, bacon and béchamel filling in
  black pastry." Stary Młyn does carry a cod pierog on the menu, but the
  specific characterization (bacon, béchamel, black pastry) was a QA2-introduced
  detail not visible on the operator's accessible menu pages, and one TripAdvisor
  review explicitly notes Stary Młyn's cod pierogi LACK bacon and béchamel.
- This is the A2 "specific dish detail not on operator menu" class. QA2 fixed
  a Mandu fabrication and introduced a Stary Młyn one as the cure.
- Fix: softened to "Pierogarnia Stary Młyn carries a cod pierog on the menu" --
  factual without inventing the preparation.

### C. Festival month / venue / date corrections

**C1. Bread Festival 2026 venue moved to Targ Rybny, NOT Skwer Heweliusza -- FIXED**

- QA1 set Bread Festival address to "Skwer Heweliusza, Gdańsk" based on prior
  editions (2024 XXIX edition at Skwer Heweliusza; 2025 XXX edition at
  Przystanek Równość on Skwer Heweliusza).
- For 2026, organisers have relocated to **Targ Rybny**. Confirmed from:
  - odkryjpomorze.pl "Jarmark Dominikański Gdańsk 2026 program imprezy"
  - media.gdansk.pl press release "Ceremonia otwarcia 764. Jarmarku
    św. Dominika"
  - Multiple Polish-language coverage noting new venue.
- 2026 Bread Festival date confirmed: Sunday 26 July 2026 (the Sunday after
  the fair opens Saturday 25 July).
- Slipped past QA1+QA2 because QA1 corrected the entity from a stale prior-edition
  framing to "Skwer Heweliusza" without re-checking the 2026 organiser
  announcement. QA2 verified 2024+2025 editions and held the QA1 venue.
- Fix: `address` -> "Targ Rybny, Gdańsk"; tip rewritten to "Held on Targ Rybny
  in 2026 (the new venue; prior editions ran on Skwer Heweliusza); programme
  runs 10:00 to 17:00." Kept `start_day` 26 (correct).

**C2. St Dominic's Fair tip carries stale date "27 July in recent editions" -- FIXED**

- The St Dominic's Fair entity's `tip` field said "Bread Festival day, 27 July
  in recent editions, is the food highlight; arrive at 10:00." This contradicts
  the cross-linked Bread Festival entity's `start_day: 26`.
- 27 July was the 2025 edition Bread Festival date; 26 July is the 2026 date.
- Slipped past QA1+QA2 because the tip referenced "recent editions" generically,
  and the date inconsistency between the two festival entities was not caught
  on internal cross-check.
- Fix: tip rewritten to "Bread Festival day on Sunday 26 July 2026 is the food
  highlight; arrive at 10:00." Matches the bread-festival entity's start_day.

### E. Editorial-prose echoes / closed-fact echoes

**E1. food-history.json + signature-dishes.json Goldwasser chronological conflation -- FIXED**

The 1598 narrative in two files conflated two events 106 years apart:

- food-history.json `1598, Goldwasser and the Mennonite merchants` summary:
  "distilled the first Goldwasser at the Der Lachs house on Szeroka."
- food-history.json `immigrant_influences[Dutch Mennonite]`:
  "Distilling Goldwasser at Der Lachs from 1598."
- signature-dishes.json goldwasser description:
  "Distilled in Gdańsk since 1598 at the Der Lachs house on Szeroka."
- signature-dishes.json goldwasser history:
  "distilled the first Goldwasser at his Szeroka Street factory. The salmon
  (Lachs) signboard on the building gave the brand its name."

Per Wikipedia (the cited source in signature-dishes.json) and corroborating
liquor-history sources:

- 1598 = Ambrosius Vermeulen took Danzig citizenship; first distillation.
- 1704 = his grandson Salomon Vermöllen moved production to a Breitgasse
  building (today ul. Szeroka) whose salmon-house facade gave the brand its
  Der Lachs name.

The 1598 Goldwasser was NOT distilled at the Der Lachs house and NOT on
Szeroka. Der Lachs branding came 106 years later when production moved to
Szeroka.

- Slipped past QA1+QA2 because both passes accepted the cited Wikipedia source
  HEAD-resolved and treated the 1598/Der Lachs framing as standard. Neither pass
  cross-checked the source page content for the actual chronology -- the
  same defect class as the Mandu cod-pierogi miss in QA1 (cited source agrees
  with the existence claim but contradicts the specific detail).
- Fix: rewrote both files to keep the 1598 first-distillation claim accurate
  and separate the 1704 Der Lachs / Szeroka relocation. The new narrative is
  factually accurate per Wikipedia's account.

**E2. region.json SEO descriptions reference non-existent entities -- FIXED**

- `bakeries.description` named "Cukiernia Trafik, Cynamonu and seven more".
  Cukiernia Trafik is a real Gdańsk/Gdynia bakery but is NOT in the topic.
  "Cynamonu" is malformed and not an entity slug (the actual entity is
  "Cynamonka Bakery").
- `coffee-roasters.description` named "Nieczapla, Kawana, HOC Coffee Roasters
  and three more". HOC Coffee Roasters is not in the topic.
- Slipped past QA1+QA2 because SEO description copy is not in any internal-
  reference check; pass-1 doesn't touch it; QA1+QA2 only updated counts on
  topics they reduced (restaurants, casual-dining, wine-bars, markets,
  festivals).
- Fix: bakeries description -> "Pellowski, Cukiernia Paradowski, Cynamonka and
  seven more"; coffee-roasters description -> "Nieczapla, Kawana, Drukarnia
  and two more".

**E3. region.json SEO title counts stale -- FIXED**

QA1 updated counts on the 5 topics it reduced. Eight other titles carry
counts that don't match the actual dataset:

- cafes title "14 Filter and Espresso Picks" -- actual 12.
- coffee-roasters title "6 Picks" -- actual 5.
- bars title "14 Cocktail and Hotel Bars" -- actual 12.
- street-food title "12 Counters" -- actual 9.
- breweries title "6 Taprooms" -- actual 5.
- budget-eating title "14 Picks Under 40 PLN" -- actual 9.
- hidden-gems title "10 Local Picks" -- actual 9.
- brunch title "10 Spots to Book" -- actual 8.

- Slipped past QA1+QA2 because SEO titles are not validated against entity
  counts by any script. QA1 updated counts only on the topics it touched;
  the other topics had drift from research-stage planning numbers that never
  matched the actual entity count.
- Fix: corrected all eight titles to match actual entity counts; updated the
  matching description "and N more" phrases.

---

## Defects total: 12

Class breakdown:
- A (cuisine / specific-fact): 5 (Paradowski address, Drukarnia open time,
  Cafe Kamienica open time, Flisak '76 close time, pierogi-z-dorszem QA2-
  introduced specifics)
- C (festival month/venue/date): 2 (Bread Festival 2026 venue, St Dominic's
  tip date)
- E (prose echoes / stale SEO copy): 5 (Goldwasser/Der Lachs chronology in
  food-history.json era + immigrant_influences, signature-dishes.json
  description + history, region.json SEO descriptions/titles)

No entity removals. All defects fixed in place via Edit.

---

## Below-floor topics after Opus

Unchanged from QA1 + QA2:
- markets.json: 5 (floor 6, 1 below)
- festivals.json: 5 (floor 6, 1 below)
- All other topics at or above floor.

Below-floor state is honest-thin, not Opus-driven. No removals.

---

## Root-cause analysis for harvesting into prompts

Opus finding 12 defects across 27 files means upstream regressed in three
distinct ways. Recommended harvest:

### 1. agents/food-research/PROMPT.md -- address fabrication mitigation

The Paradowski Wajdeloty 19 defect is the classic "agent reads source, copies
a number from somewhere else (or hallucinates a building number near a
familiar street)". The cited gedanopedia article literally says "Wajdeloty
11" in the title; the research agent wrote "Wajdeloty 19" and `address_quoted`
to match. Pass-1's fuzzy match cleared it because both fields agreed.

Add to research prompt:
- **Address verification rule**: "When you write `address` for an entity, the
  building number in `address` MUST appear character-for-character in at
  least one of: source_url page text, open_evidence_url page text, or
  Google Maps listing page for the venue. Do not write a building number
  you cannot string-match in your fetched evidence."

### 2. agents/qa/PROMPT.md -- expand A2 to time-of-day claims

Three of five A-class defects were operating-hour mismatches (Drukarnia 08:00,
Cafe Kamienica 10:00, Flisak '76 03:00). The Atlanta QA1 catch (wrong hours
30% of the time) confirms this is a known recurring class. The QA prompt
already calls out hours cross-check, but only for itinerary venues against
day-of-week. Strengthen:

- Section A2: "For every itinerary morning narration that names a time
  ('coffee at X from 08:00', 'lunch at Y at 13:00'), the time MUST be at or
  after the venue's opening time in the venue's `hours` field (or, where
  hours are not in JSON, in the operator's page text). Fail-and-fix any
  mismatch."
- Section A2 (new): "For every closing time in any `tip` field ('closes
  03:00', 'last orders 23:30', 'open until 02:00'), fetch the operator's
  current hours page and confirm. Operator-claimed hours are the source of
  truth, not the agent's memory."

### 3. agents/qa/PROMPT.md -- annual-date drift for festivals

The Bread Festival 2026 Targ Rybny venue change was announced by the
organiser before the QA pass but neither QA1 nor QA2 re-checked
"is this year's edition at the SAME venue as the prior years' editions?".
Strengthen:

- Section C: "For every festival entity, fetch the organiser's official
  2026 program/news page (not a static landing page). Confirm: (a) date
  matches start_day/end_day, (b) VENUE matches address. Festivals
  relocate; the prior-edition venue is not a safe default for the new
  edition."

### 4. agents/qa/PROMPT.md -- region.json SEO copy sweep

QA1 updated counts on the topics it reduced but not on topics that were
already drifted from earlier research-stage planning. QA2 didn't sweep
SEO at all. Add:

- Section E (new sub-section): "For every entry in `region.json:seo.pages`,
  (a) count entities in the matching topic file, (b) confirm the title's
  numerical count matches, (c) confirm every name in the description
  appears as a `name` or `slug` in the matching topic file. Any entity
  named in SEO copy that is not in the topic file is a fabrication; remove
  it from the description and replace with a real entity name from the
  topic."

### 5. agents/qa/PROMPT.md -- history-claim chronology check

The Goldwasser/Der Lachs/Szeroka conflation is the "specific historical
claim doesn't match the cited source" defect class. QA1 and QA2 both took
the 1598 Der Lachs framing on its face. Strengthen:

- Section A2 (new): "For every editorial history claim that combines a
  date with a place or entity name (e.g. 'distilled at Der Lachs from 1598',
  '1918 founding of Kubicki Cafe International'), fetch the source URL and
  confirm the date AND the place AND the entity name all appear together
  in the source. A claim that combines three correct atoms in a wrong
  configuration is still a fabrication."

---

## Verdict

VERDICT: PASS

12 judgment defects found and fixed in place. None required entity removal;
all were prose / specifics / chronology / SEO-copy errors that pass-1 and
the deterministic checks cannot mechanically catch.

The defect count is higher than the Opus "ideally zero" target (the policy
expectation). The breakdown above identifies five concrete prompt
improvements that, if applied, would have caught 10+ of these 12 at QA1
or earlier. The remaining 2 (Bread Festival 2026 venue change, Goldwasser
chronology) need targeted festival-relocation and history-chronology
checks that current prompts do not require.

Internal references resolve cleanly (ERR=0 WARN=0). JSON shape valid.
No em/en dashes. No fabricated entity replacements introduced.

Ready to ship.
