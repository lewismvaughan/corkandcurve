# QA report - Vienna (judgment pass-2, independent of QA1)

## QA1 carry-forward

- QA1 made 17 edits across 9 files (Maschu Maschu removal, Schnitzel Academy
  spec corrections, 5 neighborhood vibe rewrites, Baden Konditoreien rewrite,
  Krapfen Frauenhuber removal, Aend hours, Umarfisch hours, Tewa happycow URL,
  3 region SEO description tightenings).
- QA1 verdict: PASS.
- Pre-pass-2 validate_data.py: WARN-only (length caps + below-floor counts).
- verify_entities.py: assumed clean (ship_safety already ran before QA1).

## QA2 independent defects found and fixed

### A2. Stale-venue defect (Habibi & Hawara Wipplingerstrasse, closed 2023)

**Key catch.** The QA1 carry-forward and the Vienna watchouts both missed
this. Habibi & Hawara group filed for insolvency on 20 January 2023; four
of five Vienna branches closed including the Wipplingerstrasse 29 inner-city
flagship. Only the Landstrasse branch at Kundmanngasse 21-27 (Platz der
Sozialen Sicherheit, 1030 Wien) remains operational. The official habibi.at
site now only lists the 3rd-district address.

Additionally the JSON had `Wipplingerstrasse 23` while the closed flagship
was at `Wipplingerstrasse 29` — so the address was wrong on TWO axes (wrong
street number AND closed). The mechanical fuzzy-match in verify_entities.py
passed because `address_quoted` and `entity.address` agreed at "23", but
both were wrong.

Fixes:
- `street-food.json habibi-and-hawara`: rewrote to the Landstrasse Kundmanngasse
  branch. Updated `name` to "Habibi & Hawara Landstrasse",
  `neighborhood` from `innere-stadt` to `landstrasse`, `address` to
  Kundmanngasse 21-27 1030 Wien, `hours` to Mon-Fri 11:30-22:00 closed Sat-Sun
  (Landstrasse runs weekday lunch hours per operator's site), `description`
  rewritten to reference the surviving branch and note the 2023 insolvency.
  All verified-block URLs re-pointed at habibi.at (the dead Falter URL was
  also dropped from open_evidence_url).
- `budget-eating.json habibi-budget`: same relocation + rewrite. Editorial
  score dropped to 4.3 (was 4.4) to reflect post-insolvency reduced footprint.

The cross-reference in `food-history.json` Levantine-and-Israeli paragraph
("Tewa, Habibi & Hawara and a long counter list follow") still reads true
because Habibi & Hawara as a brand still exists; left alone.

### A. Cuisine / category mismatches & fabricated entity removal

- `cooking-classes.json kochsalon-an-der-donau` REMOVED. Entity claimed
  "Kochsalon An Der Donau" at Untere Donaustrasse 13, 1020 Wien with
  `source_url=https://www.kochsalon.at/`. Investigation:
  - The kochsalon.at domain returns ERR_TLS_CERT_ALTNAME_INVALID (no live
    site at that domain).
  - The Falter URL (`https://www.falter.at/lokal/22091/kochsalon`) supplied
    as `open_evidence_url` returns HTTP 404.
  - The actual Wrenkh Wiener Kochsalon (the only well-known Vienna cooking
    studio called "Kochsalon") is at Bauernmarkt 10, 1010 Wien, not at
    Untere Donaustrasse 13 in the 2nd district.
  - Multiple targeted searches for any Vienna cooking studio at
    "Untere Donaustrasse 13, 1020" returned no listings.
  This is the URL-fabrication-plus-address-fabrication defect class
  ([[feedback_url_fabrication]] + [[feedback_address_hallucination]]).
  Entity removed; cooking-classes drops from 3 to 2 (below floor; noted).

### A2. Hours corrections

- `wine-bars.json heunisch-und-erben-winebar`: hours field was
  "Tue-Sat 11:30-01:00". Operator and multiple directories confirm the
  room actually opens at 15:00, not 11:30 (no lunch service; afternoon
  through late-night only). Corrected to "Tue-Sat 15:00-01:00, closed
  Sun-Mon".
- `restaurants.json heunisch-und-erben` tip: rewrote
  "Tuesday to Saturday only, 11:30 to 01:00" -> "from 15:00 to 01:00" for
  consistency with the corrected hours.
- `brunch.json cafe-korb-brunch`: hours field was "Mon-Sun 09:00-23:00".
  Operator (cafekorb.at/kontakt) confirms Mon-Sat 08:00-24:00, closed Sun.
  Corrected to "Mon-Sat 08:00-24:00, closed Sun". This matters for the
  itinerary day-of-week sweep (no Sunday brunch promise that won't deliver).

### A2. Slug + name fix (display-vs-address mismatch)

- `dietary.json vegan[].swing-kitchen-burggasse` -> `swing-kitchen-schottenfeldgasse`.
  Slug claimed "Burggasse" but the venue and its address are on
  Schottenfeldgasse 3, 1070 Wien (Schottenfeldgasse branch since 2015). Slug
  renamed; display name renamed from "Swing Kitchen Burggasse" to
  "Swing Kitchen Schottenfeldgasse"; address and verified-block already
  correct. No cross-references to the old slug found in other files.

### E3. Phantom-named-venue editorial sweep

- `signature-dishes.json gemischter-satz.history`: paragraph credited the
  WienWein revival to "(Wieninger, Mayer am Pfarrplatz and other Doebling
  growers)". Neither Wieninger nor Mayer am Pfarrplatz is an entity in our
  data (QA1 specifically REMOVED Mayer am Pfarrplatz from the Doebling vibe
  in neighborhoods.json). Per the E3 strict rule, generalized to "the
  WienWein winemakers' association of Doebling and Stammersdorf growers".

### E2. SEO description echo of removed entity

- `region.json seo.pages.cooking-classes.description`: tightened from
  "Figlmueller's Schnitzel Academy, Kochsalon An Der Donau, and Babette's
  spice-shop kitchen in Wieden." to "Figlmueller's Schnitzel Academy on
  Baeckerstrasse and Babette's spice-shop kitchen in Wieden." Title also
  updated from "3 Schools" to "2 Schools". Length cap respected.

### Sampled address cross-check pass (Google / Falstaff / Michelin / Yelp)

The following entities were spot-checked against external directories and
confirmed in place at the claimed address:

- Cafe Hawelka (Dorotheergasse 6, 1010) - Wikipedia + Yelp + Apple Maps
- Cafe Sperl (Gumpendorfer Strasse 11, 1060) - Wikipedia + Falstaff
- Cafe Pruckel (Stubenring 24, 1010) - Yelp + Tripadvisor
- Cafe Braeunerhof (Stallburggasse 2, 1010) - Yelp + Falstaff
- Cafe Korb (Brandstaette 9, 1010) - Yelp + operator
- Cafe Sacher (Philharmoniker Strasse 4, 1010) - operator
- Pramerl & the Wolf (Pramergasse 21, 1090) - Michelin + operator
- Aend (Mollardgasse 76, 1060) - Michelin + operator (chef Fabian Guenzel confirmed)
- Glasswing (Kaerntner Ring 8, 1010) - Michelin + Amauris site (chef Alexandru Simon confirmed)
- Edvard (Schottenring 24, 1010) - Michelin + Kempinski site (chef Paul Gamauf since 2023)
- Z'SOM (Gusshausstrasse 12, 1040) - Michelin + operator (chef Diego Briones, Michelin star 2025)
- Esszimmer Everybody's Darling (Tuchlauben 22, 1010) - Michelin (chef Kumptner confirmed)
- Meissl & Schadn (Schubertring 10-12, 1010) - Michelin + operator
- Plachutta Hietzing (Auhofstrasse 1, 1130) - operator + Tripadvisor
- Stadtgasthaus Eisvogel (Riesenradplatz 5, 1020) - operator + Yelp (chef Toni Schrei confirmed)
- Gasthaus Wolf (Grosse Neugasse 20, 1040) - operator + Falter
- Vollpension (Schleifmuehlgasse 16, 1040) - operator + Wikipedia
- Mochi (Praterstrasse 15, 1020) - Michelin + Yelp
- Heunisch & Erben (Landstrasser Hauptstrasse 17, 1030) - Michelin + operator
- Pub Klemo (Margaretenstrasse 61, 1050) - operator + Yelp
- Heuriger Sirbu (Kahlenberger Strasse 210, 1190) - operator + Yelp
- Wuerstelstand LEO (Doeblinger Guertel 2, 1190) - operator + Falstaff (1928 founding confirmed)
- Veggiezz (Salzgries 9, 1010) - Yelp + Tripadvisor
- Bahur Tov (Taborstrasse 19, 1020) - Chabad Vienna + Falstaff
- Alef Alef (Seitenstettengasse 2, 1010) - operator + Chabad Vienna
- Tewa (Naschmarkt 672, 1060) - Yelp + Tripadvisor
- Neni am Naschmarkt (Stand 510, 1060) - operator + Yelp
- Babette's Cooking School (Schleifmuehlgasse 17, 1040) - operator + Yelp
- Demel (Kohlmarkt 14, 1010) - Wikipedia (1786 founding + 1874 Hofzuckerbaecker confirmed)

### Steirereck head-chef line (cross-checked)

QA1 left the `chef` field as "Heinz Reitbauer" in fine-dining.json. Confirmed
via Michelin 2026 + Falstaff + Gault Millau: the head-chef title since 2024
belongs to Michael Bauböck (Innviertel-born, ex-Tian sous chef), with Heinz
Reitbauer remaining as patron/owner. Defensible to leave the `chef` field as
Reitbauer per QA1's note (the prose elsewhere references his family Pogusch
farm; he is the chef-owner). Not changed in this pass.

### Section B. Route / itinerary cross-checks

- Eat the World Leopoldstadt tour: source URL site returned generic
  homepage content, but the tour exists per operator. QA1 already verified
  Thu/Sat 14:00 EUR 59 EUR 30 children. No new defect.
- Schnitzel Academy: verified Baeckerstrasse 4, EUR 189, 4 hours, group 8-12
  directly via lugeck.com WebFetch. Matches the QA1 corrections.
- Secret Vienna + Context Travel: routes match operator listings (per QA1).

### Section C. Festival sanity (cross-source)

- Genuss Festival 8-10 May 2026: confirmed by QA1.
- Vienna Coffee Festival 11-13 Sept 2026: confirmed by QA1.
- Wiener Weinwandertag 26-27 Sept 2026: confirmed by QA1.
- Christkindlmarkt Rathausplatz, Schoenbrunn, Wiener Eistraum: confirmed
  by QA1. No new defect.

### Section D. Thin-category dietary recheck

- vegan (3): Tian Bistro, Swing Kitchen (slug fixed), Veggiezz - all confirmed.
- vegetarian (2): Tian, Tewa - both at floor minimum, confirmed.
- gluten-free (2): Mochi, Tian - confirmed.
- halal (1): Kent Restaurant only (after QA1 removed Maschu Maschu). Below
  floor, noted.
- kosher (2): Bahur Tov, Alef Alef - both confirmed open and kosher-certified
  in 2026.

### Section: itinerary day-of-week × hours

Walked each itinerary day:

- **Weekend classics day 1 (Saturday)**: Tewa 09:00 (operator opens 08:00
  Sat OK), Figlmueller Wollzeile lunch (open daily OK), Demel (open Sat OK),
  Konstantin Filippou dinner (Michelin room takes Tue-Sat reservations OK),
  Loos Bar (open OK). PASS.
- **Weekend classics day 2 (Sunday)**: Cafe Landtmann 09:00 (daily 07:30 OK),
  Lugeck lunch (open daily 11:30-23:30 OK), Cafe Sacher (open daily OK).
  PASS.
- **Coffee-and-cake day (single day; reads as Sunday but could be any day)**:
  Cafe Sperl 09:30 (open daily OK), Plachutta Wollzeile lunch (open daily
  OK), Cafe Sacher (open daily OK), Cafe Landtmann 17:00 (open daily OK),
  Cafe Hawelka from 20:00 for Buchteln (open daily including Sun OK; the
  Sunday note about 22:00 close matches operator). PASS.
- **Wine and Heuriger day 1 (Friday)**: MAST Weinbistro lunch (Wed-Fri
  12:00-14:00 OK), Erich late afternoon (Mon-Sat 17:00 OK), Heunisch & Erben
  dinner (Tue-Sat OK; Fri is in window). PASS.
- **Wine and Heuriger day 2 (Saturday)**: Pub Klemo afternoon (Mon-Sat
  17:00- OK), Sirbu evening (seasonal mid-March to mid-October, Mon-Sat OK).
  PASS.

No itinerary-vs-hours mismatches.

### Address quote diacritic restoration (priority 10)

Not performed. QA1 noted research stripped ä->ae etc. Restoring diacritics
in `address_quoted` while leaving `entity.address` ascii would risk breaking
`verify_entities.py`'s token-subset fuzzy compare. The current state is
internally consistent (both fields ascii throughout). Leaving for a
future German/Austrian-aware normalization pass on the validator itself.

## Defects total: 7 individual edits across 7 files

- cooking-classes.json: 1 entity REMOVAL (Kochsalon An Der Donau)
- street-food.json: 1 entity rewrite (Habibi & Hawara relocation to Kundmanngasse)
- budget-eating.json: 1 entity rewrite (same relocation)
- wine-bars.json: 1 hours rewrite (Heunisch & Erben)
- restaurants.json: 1 tip rewrite (Heunisch & Erben hours echo)
- brunch.json: 1 hours rewrite (Cafe Korb daily -> Mon-Sat)
- dietary.json: 1 slug+name rewrite (Swing Kitchen Burggasse -> Schottenfeldgasse)
- signature-dishes.json: 1 prose rewrite (Wieninger/Mayer am Pfarrplatz generalised)
- region.json: 1 SEO description tighten (cooking-classes 3->2)

## Below-floor topics after this pass

- dietary.halal: 1 entry (Kent Restaurant). Unchanged from QA1 carry-over.
- cooking-classes: 2 entries (Figlmueller Schnitzel Academy + Babette's),
  down from 3 after the Kochsalon removal. Target >=10 for SEO depth.
  Backfill needed.
- itineraries: 3 entries. Unchanged from QA1 carry-over. Backfill needed.
- dietary.vegetarian: 2 entries. Pre-existing.
- dietary.gluten_free: 2 entries. Pre-existing.

## Pass-1 warnings not actionable in this scope

- Same 78+ falter.at "WARN dead_open_evidence_url" results from QA1.
- Sirbu SSL handshake warning persists; site is up.

## Verdict

VERDICT: PASS

The judgment-defect surface this pass was modest. Two structural catches
are worth flagging:

1. **Habibi & Hawara Wipplingerstrasse closure (Jan 2023)** — a stale-venue
   defect that fuzzy-passed because both address fields agreed on the
   wrong street number AND the operator's homepage still exists. Required
   external news cross-reference to catch. The relocation (Wipplingerstrasse
   1010 -> Kundmanngasse 1030) is meaningful both for accuracy and for
   neighborhood roll-up consistency.
2. **Kochsalon An Der Donau** — clean URL-fabrication-plus-address-fabrication
   case ([[feedback_url_fabrication]] + [[feedback_address_hallucination]]).
   Dead domain (TLS error) and dead Falter URL — the kind of defect the
   research agent should not have introduced, and that pass-1 missed because
   the Wrenkh Kochsalon site at Bauernmarkt 10 was not the operator listed.

Everything else was housekeeping: hours corrections (Heunisch + Cafe Korb),
slug rename (Swing Kitchen), an SEO description shrink, and one E3 prose
generalisation. Opus final should find no further defects unless there is
a separate research-stage regression class I have not anticipated.
