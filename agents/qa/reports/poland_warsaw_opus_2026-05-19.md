# QA report - warsaw (Opus final pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (clean entering Opus pass; QA2 cleared
  the 2 HARDs QA1 introduced)
- verify_entities.py warnings: 18 own_site_only WARNs (advisory backlog from
  QA2: Wikipedia-only day-trips, single-domain festival/bakery/cooking-class
  sources). Not blocking.
- check_internal_references.py: ERR=0 WARN=0
- validate_data.py: 0 ERRs (only the standing length-cap WARNs that were
  already on file pre-Opus; these are validator scope, not QA scope)

## Independent re-verification of QA1 + QA2 corrections

Walked each documented fact-edit from both prior passes against the live
data tree:

- Atelier Amaro 2011-not-2008: present consistently in
  food-history.json (key_eras "2011-present, the Amaro era" + summary
  "opened Atelier Amaro in 2011"), city.json food_culture_summary
  ("opened Atelier Amaro in 2011 and earned Poland's first Michelin star
  in 2013"), and signature_innovations ("first Michelin star in 2013").
  The 2008 string remaining in food-history.json is the period marker
  "1989-2008, post-transition reinvention", which is the correct boundary
  before the Amaro era and is not a defect.
- Epoka 225-325 zl food / 595-725 zl wine: present in fine-dining.json.
  No other file echoes the old 440 zl figure (the 330-440 zl Nolita
  tasting price elsewhere is a different venue and stays).
- Tuk-Tuk chilli shrimp (not BBQ prawns): cleanly rewritten in
  street-food.json. No BBQ-prawns/Thai-Wok echoes anywhere in the tree.
- HAYB Borowski / Coffee Republic rebrand 2016: present in
  coffee-roasters.json. No "first Polish-Ethiopian direct importer"
  echo elsewhere.
- Eat Polska Morning Market Tue/Thu/Sat 09:00 / 220 zl / 3.5 hr: present
  in food-tours.json. The vegan-three-days and modern-Polish-three-days
  itinerary day prose only references "Saturday morning" which is one of
  the three operator-listed days, consistent.
- Delicious Poland Food 2.5-3 hr / 385 zl / Copernicus Monument: present
  in food-tours.json; verified.address_quoted now matches the rewritten
  meeting_point.
- Delicious Poland Vodka 2.5 hr / 310 zl / Teatr Kwadrat: present; same.
- Wianki nad Wisla 2026 Sat June 20: present in festivals.json with
  start_day=20, end_day=20. The Saturday-before-solstice prose stays
  accurate for 2026.
- Fine Dining Week Warsaw July 1 - August 13 2026: present in
  festivals.json with start_month=July, end_month=August. Source URL is
  the InYourPocket page that carries the 2026 schedule. No September
  echoes anywhere.
- El Koktel Sun+Mon closed, removed from warsaw-weekend-classics day 2:
  El Koktel correctly absent from the Sunday day's venues array; remains
  in bars.json and hidden-gems.json which is intentional.
- QA2's region.json phantom rewrites (bars, brunch, late-night,
  breweries, festivals, cooking-classes, street-food) all consistent
  with the actual entity slugs in our data. Inflated-count titles all
  generalized to "Editor Picks". Powisle vibe rewrote SAM/MOMU to SAM
  Powisle + Kafe Zielony Niedzwiedz.

## Judgment defects found

### A. Cuisine / category mismatches

None new. QA1's cuisine-evidence content match held up; pass-1 mechanical
checks remain clean.

### A2. Specific-fact match against operator menus / press

None new. Re-checked the Epoka Top-Chef-Poland-2014 framing (Marcin Przybysz
won the 3rd-edition Top Chef Poland in 2014 per QA1's Polsat-archive cite);
Bez Gwiazdek "ex-Noma, ex-El Bulli, ex-Le Manoir" Trzopek career; Lukullus
Albert Judycki + Jacek Malarski Prix au Chef Patissier 2021. All three
match QA1's verified citations.

Sibling-credit borrowing: spot-checked Butchery & Wine "Poland's first
proper dry-ageing steakhouse, opened 2010", Nolita "in the Warsaw Michelin
Guide since 2014", A. Blikle "Five generations across 157 years, fifteen
Warsaw locations", Cafe Bristol "1901", Wedel "1894 / 1851 chocolate
house". All standard well-established Warsaw venue facts confirmable in
basic press / Wikipedia coverage.

### B. Route / itinerary mismatches

None. Five food-tour entries and three cooking-class entries all
operator-listed offerings; QA1 + QA2 already corrected route, duration,
price, meeting point for the two Delicious Poland tours and the Eat
Polska market tour.

### C. Festival month / dates

None. QA2's re-verification held; nothing new to flag. All five festivals
have correct months for 2026.

### D. Thin-category fabrications

None. kosher=[] correct per memory note (Polish kosher near-extinct after
WW2); halal/gluten_free/vegetarian/vegan all real venues, all match
HappyCow/Zabihah listings.

Below-floor topics that remain:
- wine-bars: 4 entries (target >=10) - same as prior passes, awaiting
  research backfill, no fabrication.
- itineraries: 3 entries (target >=10) - same.
- cooking-classes: 3 entries (target >=10) - same.

### E. Editorial-prose echoes (closed venues AND QA-removed facts)

**Two phantom-venue echoes slipped past QA1 and QA2:**

- **`neighborhoods.json` Powisle vibe**: claimed Powisle has "modern
  Polish kitchens including SAM Powisle and Kafe Zielony Niedzwiedz".
  QA2 wrote this rewrite believing SAM Powisle was an entity already in
  the data; it is not. SAM Powisle is a real Warsaw bakery/bistro, but
  it has no entry in any of our 27 JSON files. **Fixed**: rewrote the
  vibe to "modern Polish kitchens including Bez Gwiazdek and Kafe
  Zielony Niedzwiedz" (Bez Gwiazdek at Wislana 8 is in Powisle and is
  present in fine-dining.json, restaurants.json, hidden-gems.json).

- **`city.json` food_culture_summary**: in the price-floor passage
  ("a bowl of zurek at a milk bar costs 12 zloty, a vodka shot at Wodka
  Bar 6 zloty, a pierogi-by-weight plate at Pyzy Flaki Gorace barely
  20"). "Wodka Bar" is capitalised as a venue name but no such entity
  exists; bars.json + late-night.json record the actual cheap-shot
  venue as Pijalnia Wodki i Piwa at 4 zl shots (not 6). The price was
  also wrong. **Fixed**: rewrote to "a vodka shot at Pijalnia Wodki i
  Piwa 4 zloty".

Both are variants of the same defect class QA2 caught seven times in
region.json (Wodka Cafe Bar, MOMU, Cook Up Warsaw, Pierogi Festival,
Noc Restauratorow, Zapiekanki Krola Kazimierza, ArtyZann): editorial
prose lists a venue that isn't in the data. QA2's region.json sweep
was thorough but didn't fan out to neighborhoods.json vibes or
city.json food_culture_summary, so two variants escaped.

### F. Editorial voice + length caps

No egregious AI-tells observed. All length-cap WARNs remaining are
pre-existing carry-over from prior passes (food-tours descriptions,
brunch descriptions, day-trips descriptions, food-history influence
contributions, market descriptions). Validator-scope, not QA-scope.

No em-dashes or en-dashes anywhere in the two files I edited.

## Defects total: 2 (both phantom-venue echoes that slipped past QA1+QA2)

## What slipped past QA1+QA2 and why (root-cause attribution)

QA2 caught seven phantom-venue references in `region.json` SEO
descriptions (bars, brunch, late-night, breweries, festivals,
cooking-classes, street-food) and one in `neighborhoods.json` Powisle
vibe (MOMU). The fix QA2 made to Powisle introduced **a different
phantom (SAM Powisle)** because QA2 assumed SAM Powisle was already an
entity in our data and didn't grep-confirm the slug existed before
naming it in the rewrite.

Separately, QA2's phantom-venue sweep walked `region.json` exhaustively
but did not also walk `city.json` or `neighborhoods.json` for the same
defect class. The "Wodka Bar 6 zloty" in city.json.food_culture_summary
is the same kind of phantom-named-venue as "Wodka Cafe Bar" QA2 caught
in region.json, but it lived in a different file and used a slightly
different name, so the QA2 sweep didn't catch it.

Root cause: phantom-venue grep needs to be done across **every editorial
prose field in the whole data tree** when one phantom is found, not
just the file the first phantom was found in. The defect class is
"agent named a venue that isn't in our data". One instance signals
others everywhere editorial prose lives.

## What to harvest back into agents/qa/PROMPT.md

Add to Section E (editorial-prose echoes), under E1/E2, a new sub-class:

**E3. Phantom-named-venue editorial sweep (Warsaw QA2/Opus 2026-05-19)**.
When research or any earlier QA pass adds editorial prose that names a
venue (with capitalised Proper Name styling) as a typical Warsaw / city
choice, the venue MUST exist as an entity slug in the same city's data.
Build the set of all entity slugs and entity `name` fields in the city
on first read, then walk every editorial prose field across all 27
files and flag every Proper-Noun-styled venue reference that doesn't
resolve to that set. Files to walk:

- region.json: shared.og_image_alt, destination.overview,
  pages.<topic>.title, pages.<topic>.description.
- city.json: food_culture_summary, peak_food_season, local_dining_hours,
  tipping_norm, food_tagline.
- neighborhoods.json: every neighborhood.vibe and signature_strips.
- food-history.json: key_eras[*].summary, immigrant_influences[*]
  .contribution, signature_innovations.
- signature-dishes.json: description, history, make_it_yourself.tip.
- itineraries.json: summary, days[*].title, days[*].morning/afternoon
  /evening narration (Section A2 already covers itinerary slugs, but
  this is the prose-named-venue defect distinct from venues[] slug
  resolution).
- seasonal-food.json: each season[].note.
- Per-entity description / tip / why_hidden fields across all topic
  files (these usually self-reference the venue, but cross-references
  to OTHER Warsaw venues should be checked).

If a Proper-Noun-styled venue name in prose has NO entity match (case-
insensitive on `name` and slug components), either: (a) replace with
an entity that IS in our data, or (b) generalize the prose to remove
the specific name. Never invent or leave the phantom in place. Two
Warsaw Opus catches (SAM Powisle, Wodka Bar) are the precedent.

Cure cost is low (one regex sweep across the tree on first read), and
this defect class can't survive ship_safety mechanical gates because
the phantom is editorial prose, not an entity provenance block.

## Below-floor topics after Opus

- `wine-bars` at 4 (target >=10) - same as prior passes, no removals
  this round. Awaiting research backfill.
- `itineraries` at 3 (target >=10) - same.
- `cooking-classes` at 3 (target >=10) - same.
- `dietary.kosher` at 0 - intentional per memory note (Polish kosher
  near-extinct after WW2).
- Per-topic SEO descriptions all use generalised "Editor Picks" copy
  matching actual coverage after QA2's inflated-count cleanup.

## Verdict

VERDICT: PASS

2 phantom-venue echo defects found and fixed. Both are the same defect
class as QA2 caught seven times in region.json, escaped because the
sweep didn't extend to neighborhoods.json vibe + city.json
food_culture_summary. Root cause + harvest-back recommendation written
above so the food-research and QA prompts can include an exhaustive
phantom-venue grep across the whole prose tree on first read going
forward. No new fact defects, no new festival-date defects, no new
fabrications, no thin-category surprises, no slug-resolution issues.
Pass-1 + validator + check_internal_references all clean after edits.
