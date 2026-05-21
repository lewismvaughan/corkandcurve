# QA report - Vienna (Opus final pass)

## QA1 + QA2 carry-forward

- QA1: 17 edits across 9 files (Maschu Maschu removal, Schnitzel Academy spec
  corrections, 5 neighborhood vibe rewrites, Baden Konditoreien rewrite,
  Krapfen Frauenhuber removal, Aend hours, Umarfisch hours, Tewa happycow URL,
  3 region SEO description tightenings). VERDICT: PASS.
- QA2: 9 edits across 7 files (Habibi & Hawara relocation in 2 files,
  Kochsalon An Der Donau fabricated entity removed, Heunisch & Erben hours,
  Cafe Korb brunch hours, Swing Kitchen slug+name fix, signature-dishes
  Wieninger/Mayer am Pfarrplatz generalisation, region.json cooking-classes
  SEO tighten). VERDICT: PASS.
- Pre-Opus state: validate_data.py 0 ERR (WARN-only length caps + below-floor
  itineraries:3); verify_entities.py 0 HARD failures (WARNs are falter.at
  /lokal/ archive 404s, Sirbu SSL cert, plus a handful of own-site-only
  warnings).

## Opus defects found and fixed

Six defects across five files. The Opus surface was small because QA1 + QA2
covered most ground; what remained were slug-vs-name mismatches that the
mechanical checks don't catch and two phantom-named-venue echoes in prose.

### A2 / E2. Slug-vs-name canonicalisation (4 fixes)

QA2 already caught one slug-vs-name case (Swing Kitchen Burggasse ->
Schottenfeldgasse). Three more slipped through that pattern, plus an
apostrophe-mangled slug:

- `wine-bars.json weinschank-am-augarten` -> `sirbu-heuriger-winebar`.
  Slug claimed "Weinschank am Augarten" but the entity is Heuriger Sirbu at
  Kahlenberger Strasse 210, 1190 Wien (Doebling Heuriger). Slug renamed to
  match the actual venue; no cross-references to the old slug.
- `bakeries.json schwarzes-kameel-imbiss` -> `joseph-brot-albertinaplatz`.
  Slug was a leftover from an earlier draft (Schwarzes Kameel Imbiss); the
  entity is Joseph Brot Albertinaplatz at Albertinaplatz 1, 1010 Wien.
- `breweries.json schoenramer-am-platz` -> `ottakringer-braumanufaktur`.
  Slug was a phantom; the entity is Ottakringer Braumanufaktur at
  Ottakringer Platz 1, 1160 Wien.
- `bars.json barfly-s` -> `barflys-club`. Apostrophe-mangled slug; the
  venue is Barfly's Club. Slug now matches the name.

All four slug renames cleared `check_internal_references.py` (0 ERR, 0 WARN).

### E3. Phantom-named-venue echoes (2 fixes)

- `signature-dishes.json apfelstrudel.history`: removed "Cafe Hofburg
  public-baking demonstration runs the canonical method daily." Cafe Hofburg
  is not an entity in our data and the Apfelstrudel show in Vienna is
  more commonly associated with Cafe Residenz Schoenbrunn. Per E3, replaced
  the named-venue reference with the generic "the paper-thin dough is the
  test of every Konditorei." Vollpension / Demel / Cafe Landtmann references
  remain (all data-resident).
- `region.json seo.pages.brunch.description`: phantom venue "Magazin" named
  in the description but no entity named Magazin exists in any Vienna file.
  Replaced with Meierei im Stadtpark, which IS an entity in brunch.json
  (and matches the kind of upscale-brunch room the description teases).
- `region.json seo.pages.late-night.description`: named "Naschmarkt Deli"
  as a late-night room, but Naschmarkt Deli only appears in street-food.json
  and budget-eating.json (hours close at 23:00 Mon-Sat, not a late-night
  topic-file entry). Replaced with "Wuerstelstand LEO" (4am close, in
  late-night.json). The "and five more" count still matches the eight
  entries in late-night.json.

### Section 7. Address Nominatim-cleanup (5 edits across 4 files)

Per food-research PROMPT.md item #12 (Nominatim-resolvable addresses,
stripping floor / building / stall modifiers). The Naschmarkt entities
used "Naschmarkt Stand <num>" form, which inserts the word "Stand" between
the thoroughfare token and the house number, breaking Nominatim's address
parser. Canonical form for the Vienna Naschmarkt is "Naschmarkt <num>"
(the market is OSM-tagged as a thoroughfare and uses numbered stalls as
house numbers).

- `casual-dining.json neni-am-naschmarkt`: `Naschmarkt Stand 510` ->
  `Naschmarkt 510` in `address`. Description still references "Stand 510"
  in prose (acceptable).
- `brunch.json neni-brunch`: same.
- `street-food.json naschmarkt-deli`: `Naschmarkt Stand 421-436` ->
  `Naschmarkt 421-436` in `address`.
- `budget-eating.json naschmarkt-deli-budget`: same.

Tewa (`Naschmarkt 672, 1060 Wien`) and Umarfisch (`Naschmarkt 76-79, 1060 Wien`)
were already in canonical form; no edit needed. Markets and squares stay
as their canonical names (Wienzeile, Karmeliterplatz, Yppenplatz, etc.) per
the Nominatim rule.

`verified.address_quoted` for the Neni and Naschmarkt Deli entries still
contains "Stand" verbatim from the operator's source page; that's correct
provenance (the operator's own page lists "Stand 510") and verify_entities
fuzzy compare passes because the digit + Wien + postcode tokens match.

### Sampled E4 verified-block re-check

Sampled 12 entities QA1 + QA2 edited. All verified-block URLs still point
at the operator's current page and not at the closed sub-venue. The
Schnitzel Academy verified.address_quoted reads Baeckerstrasse 4 (matches
the corrected meeting_point); the Habibi & Hawara Landstrasse block reads
Kundmanngasse 21-27 (matches the corrected entity.address). No stale-target
verified URLs found.

### Section 5. Source-URL final-host check (sample 10)

Sampled 10 entities across topics (Loos American Bar, Steirereck,
Konstantin Filippou, Demel, Cafe Sacher, Plachutta Wollzeile, Heunisch &
Erben, Pub Klemo, MAST, Habibi & Hawara). All `source_url` final hosts
resolve to the operator's own current domain (or a Michelin / Falstaff
guide page that still lists the venue). No sold/parked/reassigned domains
in the sample.

### Section 3. Geographic adjacency cross-check

Walked the three itineraries:

- Weekend classics Day 1 (Saturday): Tewa (Naschmarkt 672) -> Figlmueller
  Wollzeile (Wollzeile 5) -> Demel (Kohlmarkt 14) -> Konstantin Filippou
  (Dominikanerbastei 17) -> Loos American Bar (Kaerntner Durchgang 10). All
  within the 1010 Innere Stadt + a 2km Naschmarkt walk. No "next door" /
  "around the corner" prose claims to verify.
- Weekend classics Day 2 (Sunday): Cafe Landtmann (Universitaetsring 4) ->
  Lugeck (Lugeck 4) -> Cafe Sacher (Philharmoniker Strasse 4). All within
  the Ringstrasse circuit, short walks.
- Coffee-and-cake day: Sperl -> Plachutta -> Sacher -> Landtmann -> Hawelka.
  All within walking distance of each other through 1010 and the
  Mariahilf-Innere-Stadt seam. Tram or short walk between each.
- Wine & Heuriger Day 1 (Friday): MAST (Porzellangasse 53) -> Erich
  (Lerchenfelder Strasse 22) -> Heunisch & Erben (Landstrasser Hauptstrasse
  17). Cross-city via tram (Alsergrund to Josefstadt to Landstrasse) - the
  itinerary prose calls this out ("Tram into the 8th"). Geographically
  plausible.
- Wine & Heuriger Day 2 (Saturday): Pub Klemo (Margaretenstrasse 61) ->
  Sirbu (Kahlenberger Strasse 210). The itinerary prose names the
  connecting bus 38A from Heiligenstadt. Plausible.

No "next door" / "across the street" / "two doors down" claims to verify.
No adjacency fabrication found.

### Section 2. Itinerary day-of-week x venue hours re-walk

QA2 already walked this in detail and confirmed PASS. Re-checked the
Saturday touchpoints:

- Konstantin Filippou Saturday dinner (Day 1): Michelin room runs Tue-Sat,
  Saturday is in window. PASS.
- Demel Saturday: open daily (per operator), Saturday OK.
- Tewa Saturday 09:00 brunch: Tewa operator confirms 08:00 Sat open. PASS.
- Sirbu Saturday evening: Mon-Sat 15:30-00:00 seasonal. PASS.
- Cafe Korb (now Mon-Sat per QA2 fix) - not currently in any itinerary.
  Brunch description "weekend brunch" with closed-Sunday hours is slightly
  loose but defensible (Saturday is part of the weekend).

No new day-of-week x hours mismatches.

### Section 1. Cross-entry contradictions after QA1 + QA2

Searched the tree for residual references to:
- Maschu Maschu: 0 hits (QA1 cleaned).
- Kochsalon: 0 hits (QA2 removed).
- swing-kitchen-burggasse: 0 hits (QA2 fixed slug).
- Wipplingerstrasse: 2 hits, both intentional historical context explaining
  the 2023 Habibi & Hawara closure.
- Mayer am Pfarrplatz: 0 hits (QA1 + QA2 cleaned vibe + signature-dishes).
- Wieninger: 0 hits (same).

No stale prose echoes from prior removals.

### Section: Address quote diacritic restoration

Not performed. QA2 made the same call. Restoring `address_quoted`
diacritics (ä, ö, ü, ß) while leaving `entity.address` ascii risks
breaking the verify_entities token-subset fuzzy compare. The
current state is internally consistent (both fields ascii). Defer to
a future validator-side normaliser pass.

## Defects total: 11 individual edits across 8 files

- wine-bars.json: 1 slug rename (weinschank-am-augarten -> sirbu-heuriger-winebar)
- bakeries.json: 1 slug rename (schwarzes-kameel-imbiss -> joseph-brot-albertinaplatz)
- breweries.json: 1 slug rename (schoenramer-am-platz -> ottakringer-braumanufaktur)
- bars.json: 1 slug rename (barfly-s -> barflys-club)
- signature-dishes.json: 1 prose rewrite (Apfelstrudel history, Cafe Hofburg removed)
- region.json: 2 SEO description rewrites (brunch Magazin -> Meierei;
  late-night Naschmarkt Deli -> Wuerstelstand LEO)
- casual-dining.json: 1 address normalisation (Naschmarkt Stand 510 -> Naschmarkt 510)
- brunch.json: 1 address normalisation (same on Neni)
- street-food.json: 1 address normalisation (Naschmarkt Stand 421-436 -> Naschmarkt 421-436)
- budget-eating.json: 1 address normalisation (same on Naschmarkt Deli)

## Below-floor topics after this pass (unchanged from QA2)

- dietary.halal: 1 entry (Kent Restaurant). Below floor (>=2).
- cooking-classes: 2 entries (Figlmueller Schnitzel Academy, Babette's).
  Below SEO depth target (>=10).
- itineraries: 3 entries. Below SEO depth target (>=10).
- dietary.vegetarian: 2 entries (Tian, Tewa). At floor.
- dietary.gluten_free: 2 entries (Mochi, Tian). At floor.

None of these are net-new floor issues; backfill is research's job, not QA's.

## Pass-1 warnings not actionable in this scope (unchanged)

- 78+ falter.at /lokal/ "WARN dead_open_evidence_url" 404s: structural
  archive-rot affecting the German-speaking city batch; fixup pass concern.
- Sirbu SSL cert verification warning persists; site is up per WebSearch.
- If Dogs Run Free + Le Troquet + Tewa SSL/timeout warnings; the venues
  exist (per Falter + Yelp + Tripadvisor cross-references).

## Verdict

VERDICT: PASS

The Opus surface was modest and mostly housekeeping. The four slug-vs-name
catches are the most consequential structural finding because the slug
drives the generated URL path (`/austria/vienna/wine-bars/sirbu-heuriger-winebar/`
not `/austria/vienna/wine-bars/weinschank-am-augarten/`) and these would
have shipped as confusing URLs that don't match the page heading. The
Naschmarkt address normalisations bring the four affected entities into
Nominatim canonical form so they geocode at ship step 2f.

Two phantom-venue echoes in region.json SEO descriptions are E2/E3 catches
that QA1 + QA2 walked the major prose files for but missed in the
region.json sweep. Lesson for next city: walk every named venue in
`region.json seo.pages.<topic>.description` against the actual
entities in the matching topic JSON, not just against the city-wide
slug+name index.
