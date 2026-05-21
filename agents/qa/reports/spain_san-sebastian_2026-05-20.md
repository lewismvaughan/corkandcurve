# QA report — San Sebastian (judgment pass-2)

## Pass-1 carry-forward

- ship_safety.sh exited green prior to this pass.
- verify_entities.py: ~70 WARN own_site_only flags (acceptable; deeply Basque
  venue ecosystem is heavy on operator-direct sources).
- All 27 JSON files load cleanly post-edit.

## Judgment defects found and fixed

### A. Cuisine / category mismatches
- None removed. Spot-checked Casa Valles, Hidalgo 56, Sirimiri Gastroleku,
  Casa Senra, Sakona, Old Town Coffee, Bar Tamboril — all real, addresses
  match independent directories.

### A2. Specific-fact + chef/owner structural check (Charleston QA1 rule)
- `fine-dining.json` Casa 887: chef listed as "Jorge Asenjo"; operator's
  own site (grupo887.com) and Repsol/LQCDM/Sisters press confirm chef is
  Antonio Belotti (Sao Paulo, b.1993). The "sister kitchen to the Galerna
  team" line was also unsupported. Fixed: chef → "Antonio Belotti", name
  disambiguated to "Casa 887 (Dining Room)", description rewritten to
  drop the false sibling-credit borrowing.
- `fine-dining.json` Ni Neu: chef listed as "Mikel Gallo" (the founding
  chef who departed). Current 2025-2026 chef per multiple sources is
  Raul Cabrera. Fixed: chef → "Raul Cabrera", description rewritten.
- `food-tours.json` Tenedor Tours: claimed "led by Gabriella Ranelli for
  25 years"; actual founding 1997 (29 years). Fixed: "founded by
  Gabriella Ranelli in 1997".
- Arzak (Juan Mari + Elena), Akelarre (Pedro Subijana), Amelia (Paulo
  Airaudo), Kokotxa (Dani Lopez), Eme Be Garrote (Berasategui + Javi
  Izquierdo), Mirador de Ulia (Ruben Trincado), Galerna (Asenjo +
  Barainca), Casa Urola (Pablo Loureiro Rodil) — all confirmed via
  operator About pages / Michelin Guide / Pintxos.es chef profiles.

### A2.5. Existence / phantom-venue removal
- `dietary.json` "Sorginzulo Vegan" at Calle Egia 7: Sorginzulo is a
  Bilbao bar (Plaza Nueva, Bizkaia), NOT a San Sebastian venue. No
  Donostia "Sorginzulo" listing on any directory (HappyCow,
  sansebastianveganfood, tourism office). Removed entity; updated
  region.json dietary description echo accordingly.

### B. Route / itinerary mismatches
- None. Mimo, Devour, Tenedor, San Sebastian Food, Potluck all operate
  the routes claimed (verified each operator's listings).

### C. Festival month corrections (cross-source rule, Poznan precedent)
- `festivals.json` Sagardo Apurua: claimed late December (Dec 26-29) at
  Plaza de la Constitucion. Actual 2025/2026 dates are early December
  (Dec 6-9) on the Boulevard next to City Hall, per sagardotegiak.com
  and multiple Basque tourism sources. Fixed start_day/end_day, month
  label, address, address_quoted, source_url and cuisine_evidence_url.
- Gastronomika (Oct 5-7), Semana Grande (Aug 8-15), Film Festival
  (Sep 18-26), Sagardo Berriaren Eguna (Jan 14), Tamborrada (Jan 20):
  all matched 2026-specific sources.

### D. Thin-category fabrications
- Dietary post-removal: vegan 1, vegetarian 2, gluten_free 2, halal 0,
  kosher 0. Halal+kosher were already 0 (no fabricated replacements per
  Lewis rule). Vegan now 1 (below floor); see "Below-floor".

### E. Editorial-prose echoes (E1/E2/E3/E4)
- E3 phantom-venue in region.json `seo.pages.bars.description`: named
  "Dickens" as a San Sebastian bar entity; no Dickens entity exists in
  bars.json or anywhere in the data. Rewrote to reference "Akerbeltz"
  which IS a verified bars entity.
- E3 phantom in region.json `seo.pages.festivals.description`: named
  "Pintxos de Autor" as a festival; no such festival entity. Rewrote
  to reference "Sagardo Apurua" which IS in festivals.json.
- E3 phantom in region.json `seo.pages.dietary.description`: named
  "Sorginzulo" (removed as Bilbao-only). Rewrote to reference Kafe
  Botanika + Old Town Coffee + Ni Neu (all in data).
- E4 Sagardo Apurua: when fixing dates/venue, also re-pointed
  `verified.address_quoted`, `source_url` and `cuisine_evidence_url`
  to new 2026-specific sources.

### F. Editorial voice — minor cleanups
- `neighborhoods.json` Antiguo vibe: "Akelarre funicular climbs" was
  imprecise (it's the Igueldo funicular, climbing toward Akelarre).
  Rewrote.
- `city.json` food_culture_summary: "Astigarraga, 6 kilometres out"
  contradicted day-trips/festivals/breweries which all say 7 km.
  Aligned to "7 kilometres".

### Itinerary day-of-week vs venue-hours sweep
- **Itinerary 1 day 2 Sunday lunch at Kokotxa**: Kokotxa is closed
  Sundays + Mondays per official reservation page. Rewrote to lunch
  at Mirador de Ulia (open Sunday 13:30-18:00 per Michelin and
  operator hours).
- **Itinerary 2 day 3 Sunday lunch at Amelia**: Amelia is closed
  Sunday + Monday + Tuesday per ameliarestaurant.com/faq. Swapped
  the entire Saturday-Sunday day order: Saturday is now Amelia
  (open Sat 13:00-14:00), Sunday is now Akelarre (open Sun 13:00-
  14:30 per multiple sources). The Michelin-triple structure of the
  itinerary preserved.
- **Itinerary 3 day 3 Sunday at Antonio Bar**: Antonio Bar is closed
  Sundays per Yelp + operator confirmation. Rewrote to swap Antonio
  Bar for La Vina at 19:00 (open Sun 19:00-23:00 evening service),
  shifted the afternoon block accordingly so Old Town break
  (15:30-19:00) is respected.

### Markets accuracy (high-confidence fact corrections)
- `markets.json` Mercado de Gros: claimed Plaza Catalunya; actual
  location is Plaza Nafarroa Beherea per marketsinspain + Bizkaia
  tourism. Fixed address + address_quoted + verified source URL.
- `markets.json` Saturday Outdoor Producer Stalls: claimed Plaza
  Catalunya only; actual is a rotation across four Donostia plazas
  (Easo / Berri / San Francisco Gros / Gaskuna) with only the 3rd
  Saturday landing in Gros. Rewrote name and description; updated
  evidence URL.

### Wine-bars slug consistency
- `wine-bars.json`: entity for Galerna Jan Edan carried slug
  "casa-urola-rooftop" (legacy template artifact, semantically wrong
  and confusing). Renamed slug to "galerna-wine". No internal
  cross-refs used the old slug, no breakage.

### Gluten-free evidence-URL alignment
- `dietary.json` Old Town Coffee GF entry's open_evidence_url pointed
  at KafeBotanika's atly.com page (cross-pasted). Repointed to
  atly.com OldTownCoffee1.

## Defects total: 16

## Below-floor topics after QA
- dietary/vegan: 1 (was 2 after Sorginzulo removed). Floor for vegan is
  typically >=2; flag for research backfill. Kafe Botanika is the only
  verified vegan-positive operator left; HappyCow San Sebastian listings
  thin out fast after Kafe Botanika and Kilometro Cero. Not fabricating
  a replacement (Lewis rule).
- dietary/halal: 0 (no Halal listing in San Sebastian per Zabihah).
  Acceptable below-floor.
- dietary/kosher: 0 (no Kosher listing per chabad.org / kosher Spain
  directories for Donostia). Acceptable below-floor.
- itineraries: 3 (target >=10). Not in QA scope to backfill.
- breweries: structural note — Petritegi (Astigarraga) and Zelaia
  (Hernani) are 7-8 km outside city limits but appear in
  `breweries.json` as well as `day-trips-food.json`. Left in both:
  sagardotegi tradition is inseparable from Donostia drinking culture
  per region tourism positioning, and the duplication is parallel to
  Galerna/Topa appearing across fine-dining + restaurants + wine-bars
  (multi-category venue surface, not city-misplacement). Not removing.

## Out-of-city exclusion sweep (E3 sweep)
- Confirmed NO active-operator references for Martin Berasategui in
  city-proper files except as: (a) the chef-of-record at Eme Be Garrote
  in Ibaeta (which IS city-proper); (b) the day-trip entity for
  Lasarte-Oria; (c) historical/biographical mentions in food-history
  + signature-dishes + cooking-classes prose. All correct.
- Mugaritz: only in day-trips-food, food-history. Correct.
- Elkano (Getaria): only in day-trips-food (within Getaria entry).
  Correct.
- Alameda (Hondarribia): only in day-trips-food (within Hondarribia
  entry). Correct.
- Bar Zeruko: zero occurrences anywhere in the dataset. Confirmed.

## Verdict
VERDICT: PASS

16 judgment defects fixed, no fabricated replacements introduced, no
em/en dashes added, atomic edits throughout, scope held to
site-data/spain/san-sebastian/data/. Below-floor on dietary/vegan and
itineraries flagged for research-stage backfill; both halal and kosher
correctly empty per Lewis rule.
