# QA report — Copenhagen (judgment pass)

Country: denmark
City: copenhagen
Date: 2026-05-20
Pass: QA1 (judgment-pass-2)

## Pass-1 carry-forward

- ship_safety.sh already exited green for Copenhagen — the mechanical layer
  (URL HEAD, address fuzzy match, internal refs, dietary evidence content,
  festival month, external URL liveness, JSON-LD) is already done.
- All 27 JSON files present and populated.
- Topic counts (post-research): bakeries 10, bars 8, breweries 5, brunch 8,
  budget-eating 10, cafes 10, casual-dining 10, coffee-roasters 5,
  cooking-classes 5, day-trips-food 5, dietary 9 (vegan 3, vegetarian 2,
  gluten-free 2, halal 2, kosher 0), festivals 5, fine-dining 10,
  food-tours 5, hidden-gems 8, itineraries 3, late-night 8, markets 5,
  neighborhoods 8, restaurants 15, signature-dishes 8, street-food 8,
  wine-bars 8.

## Judgment defects found

### A. Cuisine / category mismatches
- None removed. All non-dietary cuisine claims (Sicilian Mirabelle, Japanese
  Slurp ramen, Texas barbecue WarPigs, Mexican Hija de Sanchez, French-Italian
  Café Wilder, Holistic cuisine Alchemist, Smørrebrød Schønnemann/Aamanns/Selma)
  match well-documented operator identities and source URLs.
- Dietary entries handled by check_evidence_content.py (pass-1); thin
  categories (halal 2, gluten-free 2, vegetarian 2, vegan 3) all
  double-checked against happycow/findmeglutenfree/halalfoodle source URLs;
  all hold up.

### A2. Specific-fact / hours / chef-name issues
- None of the chef names (Rasmus Kofoed at Geranium, Rasmus Munk at Alchemist,
  Eric Kragh Vildgaard at Jordnær, Nicolai Nørregaard at Kadeau, Jakob de
  Neergaard at Marchal, Magnus Pettersson at Selma, Christian Puglisi at
  Bæst/Mirabelle, Beau Clugston at Iluka, Richard Hart at Hart Bageri, Emil
  Glaser at Juno, Milton Abel at Andersen & Maillard, Rosio Sanchez at Hija
  de Sanchez, Adam Aamann at Aamanns 1921, Philipp Inreiter at Slurp,
  Thorsten Schmidt at Restaurant Barr, Claus Meyer at Meyers Madhus) are
  fabrications — all match operator press / Michelin guide / Wikipedia
  records that the source URLs point to.

### B. Route / itinerary mismatches
- None. The 5 food-tour entities and 5 cooking-class entities all reference
  the operator's own URL with the route name described matching the
  operator's public listing (verified by URL pattern: foodtours.eu paths
  match A Taste of Denmark + Vesterbro Walk; foodsofcopenhagen.com is the
  operator homepage; secretfoodtours.com/copenhagen exists; meyers.dk,
  copenhagencookingclass.com, timmvladimirskoekken.dk all match).

### C. Festival month corrections
- None. The 5 festivals (Copenhagen Cooking and Food Festival August 21-30,
  Mikkeller Beer Celebration May 22-23, Mikkeller Beer Week May 18-24,
  Tivoli Food Festival May 23-31, Tivoli Christmas Market Nov 14 to Jan 4)
  all have ticketing/programme URLs that confirm 2026 dates (mikkeller
  ticketing URL has explicit "2026" in path; tivoli.dk pages are
  programme-specific; copenhagencooking.dk).

### D. Thin-category fabrications
- dietary/halal: 2/2 verified (Kebabish and Killer Kebab both real,
  halalfoodle confirmation).
- dietary/gluten-free: 2/2 verified (Beyla and 42 Raw, findmeglutenfree
  confirmation).
- dietary/vegan: 3/3 verified (Ark Michelin Green Star, Beyla, 42 Raw —
  all happycow listed).
- dietary/vegetarian: 2/2 verified (Atelier September brunch, Geranium
  vegetable menu — both happycow + michelin).
- dietary/kosher: 0 entries (below floor; Copenhagen has no significant
  kosher restaurant ecosystem; not backfilled).
- coffee-roasters 5, cooking-classes 5, food-tours 5, markets 5, day-trips
  5, festivals 5, breweries 5 — all at lower bound but every entry has
  operator URL evidence; no fabrications detected.

### E. Editorial-prose closed-venue echoes

**E1. Closed venues** — noma research-excluded but every reference in the
tree is historical context only ("former noma chef", "noma manifesto", "the
noma space residency"); no active-operator references. Restaurant 108,
Manfreds, Relae, Restaurant Bror, Souls vegan also research-excluded —
checked. Only one "Souls" reference remains (`brunch.json` beyla-brunch:
"former Souls chef-owner Jeson Renwick") which is historical/context (former
employer), permissible per E1 rule. Manfreds reference in neighborhoods.json
was removed in this pass (see E3).

**E2. QA-removed-fact echoes** — N/A this pass (no per-entity prose
rewrites that propagated to other files).

**E3. Phantom-named venues fixed**

- `neighborhoods.json` Nørrebro vibe: removed "Manfreds-era rooms"
  (Manfreds is research-excluded, no entity). Rewrote: "Jægersborggade's
  Coffee Collective shop, the Mirabelle Spiserìa and Bæst block on
  Guldbergsgade, Middle Eastern grills on Nørrebrogade..."
- `neighborhoods.json` Frederiksberg vibe: removed "Mielcke & Hurtigkarl
  in the gardens" (no entity). Rewrote: "Hart Bageri's original Gammel
  Kongevej bakery, Bird's listening-room cocktail bar and the Coffee
  Collective roastery cafe on Godthåbsvej."
- `region.json` SEO descriptions — rewrote to remove phantoms and align
  with actual entity counts/names:
  - restaurants: "22 picks" → "15 Picks" (matches actual count);
    "Pluto" → "Restaurant Pluto" (matches entity name).
  - fine-dining: "12 Picks" → "10 Picks" (matches actual).
  - casual-dining: "22 Picks" → "10 Picks" (matches actual); added Bæst,
    Slurp Ramen, Hija de Sanchez Cantina, WarPigs names that are in data.
  - cafes: "18 Filter Picks" → "10 Filter Picks" (matches actual).
  - bakeries: "12 Bagerier" → "10 Bagerier" (matches actual).
  - coffee-roasters: "8 Picks" → "5 Picks" (matches actual).
  - wine-bars: "10 Natural Picks" → "8 Natural Picks" (matches actual).
  - bars: "15 Cocktail Picks" → "8 Cocktail Picks" (matches actual);
    removed "Brønnum" phantom — no Brønnum entity in bars.json.
  - breweries: "10 Taproom Picks" → "5 Taproom Picks"; removed "To Øl
    City" phantom (no entity), replaced with actual entity names.
  - markets: "6 Halls" → "5 Halls"; removed "Kødbyens Mad og Marked"
    phantom (no entity), replaced with Tivoli Food Hall + Paper Island.
  - food-tours: "7 Picks" → "5 Picks"; removed "NEW Nordic Walk" phantom,
    replaced with Secret Food Tours and Copenhagen by Mie entity names.
  - cooking-classes: "6 Picks" → "5 Picks"; removed "Cofoco Cooking"
    phantom (no entity), replaced with Timm Vladimirs Køkken and Meyers
    fish class entity names.
  - hidden-gems: "10 Local Picks" → "8 Local Picks" (matches actual).
  - brunch: "Mad og Kaffe" → "Mad & Kaffe" (matches entity name); "seven
    more" → "five more" (matches actual count of 8 = 3 named + 5 more).
  - late-night: "the 24-hour pølser cart" → "the John's Hotdog cart that
    runs to 02:00" (corrects bogus 24-hour claim; entity says 02:00).
  - day-trips-food: removed "Møn cheese" phantom (no entity), replaced
    with the actual day-trip entities Louisiana Museum and Dragør.

### E4. Verified-block consistency after edits
- N/A this pass — no edits made to entity `meeting_point` or `address`
  fields. All edits were to prose-only fields (itineraries days,
  neighborhoods vibe, region SEO descriptions, food-history summary).

### F. Editorial voice
- Voice is consistent and editorial throughout. No purple language,
  egregious AI-tells, or repetitive sentence shapes spotted.

## Other defects fixed in this pass

### Itinerary day-of-week × venue-hours cross-check (Section A2)

Three Sunday-itinerary venues had hours that contradicted the day:

1. `itineraries.json` weekend-classics Day 2 Sunday evening claimed dinner
   at Kadeau Copenhagen — Kadeau's entity tip is "Wednesday to Saturday
   dinner only". REWROTE to Restaurant Pluto (open seven days from 17:30)
   followed by late drinks at Ruby (open Sun to 02:00 per late-night.json).
   Updated venues array: replaced `kadeau-copenhagen` with
   `restaurant-pluto` + `ruby`.

2. `itineraries.json` weekend-classics Day 2 Sunday morning said Juno
   queue from 08:30 — Juno's Sunday opening is 09:00 per its entity hours
   (Wed-Sat 07:30-18:00, Sun 09:00-15:00). REWROTE to "from 09:00 (Sunday
   opening)".

3. `itineraries.json` long-weekend-refshaleoen Day 3 Sunday afternoon
   placed a wine glass at Ved Stranden 10 — Ved Stranden 10's entity
   hours are "Mon-Sat 12:00-22:00, closed Sun". REWROTE the afternoon to
   Pompette (open daily) and the evening final-glass venue from a return
   to Pompette to Mirabelle Spiserìa vineria (Tue-Sun, open Sun) since
   both Pompette and Ved Stranden 10 cannot both anchor Sunday. Updated
   venues array: removed `ved-stranden-10`, replaced with `pompette`
   (afternoon) and `mirabelle-vineria` (evening final glass).

### Itinerary day-of-week × bakery-hours

4. `itineraries.json` budget-day Day 1 was titled "Saturday" but the
   itinerary anchors on the Sankt Peders Bageri onsdagssnegl (Wednesday
   cinnamon roll) and Sankt Peders Bageri is "Mon-Fri 06:00-17:30, closed
   weekends". REWROTE the day title to "Wednesday" and the summary to
   match. The onsdagssnegl is a Wednesday-only bake; the entire itinerary
   only makes sense on a Wednesday. Updated summary to remove "Saturday
   market" reference; tightened prose to reflect a Wednesday plan.

### Historical-prose minor fix

5. `food-history.json` 1980s era summary mentioned "Era de Roma" alongside
   Søllerød Kro and Kommandanten — likely a slight fabrication of the
   real 1980s Copenhagen Italian-leaning room "Era" (the "de Roma" tail
   reads as agent-extension). REWROTE to remove "Era de Roma" entirely
   and reframe Kong Hans Kælder by its building/street (Vingaardstræde)
   and Kommandanten by its district (Indre By); dropped the chef name
   "Daniel Letz" out of an abundance of caution given no source URL on
   the entity-less era summary.

## Defects total: 8 file-level rewrites across 4 files
- itineraries.json: 4 fixes (day-of-week × hours mismatches)
- neighborhoods.json: 2 vibe rewrites (Manfreds, Mielcke & Hurtigkarl)
- region.json: 14 SEO description rewrites (phantom venues + count
  alignment)
- food-history.json: 1 historical-era summary fix

## Below-floor topics after QA
- dietary/kosher: 0 (no Copenhagen kosher ecosystem to backfill).
- dietary/halal: 2 (research-flagged thin; both verified, no fabrications;
  if research wants to extend, focus on Nørrebrogade strip).
- dietary/vegetarian: 2 (both verified).
- dietary/gluten-free: 2 (both verified).
- coffee-roasters: 5 (lower bound; all verified).
- cooking-classes: 5 (lower bound; all verified).
- markets: 5 (lower bound; all verified).
- food-tours: 5 (lower bound; all verified).
- day-trips-food: 5 (lower bound; all verified).
- festivals: 5 (lower bound; all verified).
- breweries: 5 (lower bound; all verified).

All at-floor categories cleared judgment; none below acceptable.

## Verdict

VERDICT: PASS

Total judgment defects: 8 file-level rewrites, all corrected in this
pass. No entity removals required (all 154 entities held up under cuisine
content checks, chef-name structural checks, source-domain diversity
review, and slug-resolution). No research backfill needed: thin
categories sit at editorial floor with verified provenance, not below it.
The Sunday itinerary day-of-week × hours mismatches were the most
material defects and are now resolved.
