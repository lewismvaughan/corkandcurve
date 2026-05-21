# QA2 report -- Wrocław (independent second-pass judgment)

QA1 verdict was PASS with a Wrocław-specific note that the fixup agent had
taken the `address_quoted = entity.address` shortcut and that more masked
address fabrications might remain. QA2 brief asked for an independent 20-30
entity address cross-check on top of the standard sections.

## Pass-1 carry-forward

- verify_entities.py hard failures: 0
- verify_entities.py warnings (post-QA2): same `own_site_only` cluster carried
  forward from QA1 (street-food roclawguide.com bundle, several Michelin Guide
  source-only restaurants, Pijalni, OK Wine Bar, Cocofli, etc.) plus the
  `winogrono` Unicode-encoded URL flake. All structural, no falsified data.

## Independent-directory address audit (Section A priority)

Cross-checked 25 distinct venues against external directories
(operator-own + Google Maps + Yelp + restaurantguru + happycow + Michelin
Guide + tour-listing platforms), focusing on entities whose
`address_quoted` equals `entity.address` (44 such cases, the fixup-shortcut
risk class).

**Two more address fabrications found beyond QA1's three (HUTA, Niewinność,
El Gato):**

### A1. Hala Świebodzki (markets) -- address fully fabricated

- JSON claimed: `Piłsudskiego 105, 50-016 Wrocław`
- Independent confirmation across operator (halaswiebodzki.pl),
  wroclawturysta.pl, gdziezjescwroclaw.com, pyszne.pl, kupbilecik.pl,
  pik.wroclaw.pl all give actual address: **Plac Orląt Lwowskich 20B,
  53-605 Wrocław** (the historic Świebodzki Station building).
- Fixed: address, address_quoted, source_url repointed to
  gdziezjescwroclaw.com directory listing, hours corrected
  (Sun-Wed 12:00-23:00, Thu-Sat 12:00-00:00).

### A2. Wrocławski Bazar Smakoszy (markets) -- address fully fabricated

- JSON claimed: `Browar Mieszczański, Hubska 44, 50-502 Wrocław`
- Operator (bazarsmakoszy.com), wroclawguide.com events page, pik.wroclaw.pl,
  pl.revieweuro.com all give actual address: **ul. Paczkowska 26, 50-525
  Wrocław**. Operating hours also wrong (JSON said "Saturday 09:00-15:00",
  actual is Saturday 09:00-13:00, Sunday 10:00-14:00).
- Fixed: address, address_quoted, source_url, hours, tip language updated
  to match the Paczkowska location.

**This confirms a systemic Wrocław data-integrity issue.** Five venues
across the city had fabricated street addresses in the same delivery batch
(HUTA, Niewinność, El Gato from QA1; Hala Świebodzki and Wrocławski Bazar
Smakoszy from QA2). The pattern is consistent: the research agent picked a
plausible Wrocław street name and a plausible building number, the fixup
agent then made `address_quoted = entity.address` to satisfy the validator's
fuzzy match, and pass-1 cleared both. Independent-directory cross-check is
the only catch. Flagging for upstream: the Wrocław research+fixup batch
specifically should be assumed to have higher residual risk than other
cities; future Wrocław additions must pass the directory cross-check as part
of pass-1 not just QA judgement.

**Confirmed clean against independent directories (QA2 sample):**

- Pierogarnia Stary Młyn (Rynek 29, Tenement House Under the Golden Crown) -- pierogarnie.com + multiple
- Pierogarnia Rynek 26 (Rynek 26) -- operator + tripadvisor
- Dwór Polski (Rynek 5, 16th-century townhouse) -- dworpolski.wroclaw.pl + multiple
- Karczma Lwowska (Rynek 4, tenement Pod Złotym Orłem) -- operator + multiple
- Restauracja Konspira (Plac Solny 11) -- inyourpocket + tripadvisor + operator
- Restauracja Monopol (Heleny Modrzejewskiej 2) -- guide.michelin + operator
- Vega vegan (Rynek-Ratusz 27a) -- happycow + visitwroclaw
- poké poké (Świętego Antoniego 27/29) -- restaurantguru + happycow
- Pampa empanadas (Podwale 19/1A) -- operator empanadaspampa.com
- Pan Precel (Ruska 66/67) -- restaurantguru + operator
- Frytki + sos (Świętego Antoniego 14) -- wroclawguide.com + operator
- Mleczarnia (Pawła Włodkowica 5) -- inyourpocket + multiple
- Bema Cafe (Drobnera 38) -- inyourpocket + tripadvisor
- Gniazdo (Świdnicka 36) -- inyourpocket + yelp + operator instagram
- Cafe Rozrusznik (Cybulskiego 15, Nadodrze) -- artystycznenadodrze.pl
- Czekoladziarnia (Więzienna 31) -- inyourpocket + restaurantguru
- Cocofli (Włodkowica 9) -- operator + gdziezjescwroclaw.com
- OK Wine Bar (Księcia Witolda 1) -- operator
- Paloma Coffee (Plac Solny 8-9) -- operator + restaurantguru
- Chleboteka (Ruska 64/65) -- gdziezjescwroclaw.com + multiple
- Piekarnia Złoto Nadodrza (Henryka Pobożnego 20) -- est. 1979 Krzysztof Krajewski, multi-source
- Tandyr House (Stanisława Dubois 14) -- restaurantguru + operator
- Lwia Brama² (Katedralna 9) -- operator + multiple
- Korill 180 (Krakowska 180/K3) -- operator + Michelin Guide
- La Maddalena (Pomorska 1) -- operator + Michelin
- Pod Fredrą (Rynek-Ratusz 1) -- operator
- Bar Mleczny Różowa Krowa (Świdnicka 36) -- inyourpocket + restaurantguru
- Bułka z Masłem (Włodkowica 8a) -- operator + multiple
- Etno Cafe Okrąglak (Plac Kościuszki) -- pitupitu.pl + operator
- Charlotte (Świętego Antoniego 2/4) -- operator

## Section A2 -- specific-fact corrections beyond addresses

### A2a. Wierzbowa 15 -- chef + cuisine + dish claims rewritten

- JSON `chef`: "House team" -- updated to "Juan Luis Fernández (patron)".
  Two-Michelin-star Spanish chef Juan Luis Fernández took over patronage in
  April 2025 (e-hotelarz.pl, destigohotels.com, mindtrip.ai sources).
- JSON cuisine `Nordic-Polish` and "big on fermentation, smoked fish and
  game" softened to "Polish-European fusion with Nordic accents", which is
  what the operator's own page says.
- JSON must_order "house-cured trout starter and venison main" softened
  to "marinated mackerel with dill granita and seasonal trout" -- the
  mackerel-and-dill-granita dish IS on Michelin Guide and Tripadvisor
  copy; venison is not corroborated. Both restaurants.json + fine-dining.json
  entries updated. Slugs unchanged.

### A2b. Gustaw -- chef name added, description corrected

- JSON `chef`: "House team" updated to "Kacper Sawoń" (per Michelin Guide
  copy: "Head Chef Kacper Sawoń continues the culinary legacy of
  Taschenbastion").
- Description "on a side street locals favour" rewritten to surface the
  actual landmark context: Gustaw sits inside the old Bastion Sakwowy
  fortification, a sunken dining room with marble tables. Updated in both
  restaurants.json + fine-dining.json.

### A2c. Bułka z Masłem -- hours field corrected

- JSON hours "Daily 08:00-22:00" was wrong. Operator's own contact page:
  Mon-Wed 10:00-22:00, Thu 10:00-23:00, Fri-Sat 09:00-00:00, Sun
  09:00-22:00.
- Fixed in brunch.json. Cafes.json tip "Weekday breakfast before 10:00 is
  the move" reworked because the room doesn't OPEN before 10:00 weekdays.

### A2d. poké poké -- hours field corrected

- JSON said "Daily 12:00-21:00", actual Mon-Thu 12:00-18:00, Fri-Sun
  12:00-20:00 (Tripadvisor + restaurantguru). Updated in street-food.json.

### A2e. Wino bars hours corrected

- OK Wine Bar: JSON "Tue-Sat 12:00-23:00" was wrong. Actual: Mon-Thu
  17:00-23:00, Fri-Sat 12:00-23:00, Sun 12:00-21:00 (inyourpocket +
  operator). Fixed in wine-bars.json.
- Cocofli: JSON "Mon-Sat 09:00-23:00, Sun 11:00-21:00" was wrong. Actual
  per gdziezjescwroclaw.com (operator-info): Mon-Thu and Sun 10:00-23:00,
  Fri-Sat 10:00-00:00. Fixed.

### A2f. Vertigo Jazz Club -- closes field corrected

- JSON late-night.json said "Fri-Sat 01:00", actual Sun-Thu 00:00, Fri-Sat
  02:00 (operator + WROT). Updated.

### A2g. Paloma Coffee -- hours extended

- JSON said "Daily 08:00-19:00", actual 08:00-21:00 (Yelp + operator info
  on inyourpocket). Updated in coffee-roasters.json.

### A2h. Enklawa Hala Targowa -- postal code fixed

- JSON said "Hala Targowa, Piaskowa 17, 50-156 Wrocław". Actual postal is
  50-158 (matches the markets.json entry already fixed by QA1). Updated.

### A2i. Viator Pierogi & Beer Class -- group size corrected

- JSON said `group_size: "2-10"`. Operator (Viator listing) says max 5.
  Fixed.

### A2j. byFood Wroclaw Private Tour -- duration broadened

- JSON said duration "3 hours" / price "510 zł per person". byFood offers
  three tiers (Budget 2.5h, Standard 3.5h, Premium 5h) -- the
  "3 hours" misrepresents the Standard tier (3.5h). Generalized to
  "2.5-5 hours (tier dependent)" with "Tier dependent; see operator" price
  and description rewritten to mention the three tiers honestly.

## Section B -- itinerary route + day-of-week cross-check

- **Wrocław weekend classics** day 1 (Saturday): Hala Targowa Sat 08:00-18:30
  (09:00 OK), Restauracja Wrocławska open, BABA 19:30 books fine. Day 2
  (Sunday): Charlotte Sun 08:00-22:00 (08:30 OK), Lwia Brama Sun 12-22
  (13:00 OK), Browar Stu Mostów Sun open. **PASS.**

- **Wrocław tasting-menu long weekend** day 3 (Sunday) STÓŁ at 17:30 cutoff
  fix from QA1 still in place. Day 1 IDA 13:00 lunch + Most 19:30 dinner
  fine. Day 2 Tarasowa 13:00 + Pijalni 19:30 fine. **PASS.**

- **Wrocław budget two days** day 1: Piekarnia Sąsiedzi Sat 07:30-18:00
  (09:00 OK), Bar Pierożek Mon-Sat 11:00-19:00 (12:30 OK), Browar Stu
  Mostów Sat open. Day 2 (Sunday): Bułka z Masłem Sun 09:00-22:00 (09:30
  is just after open), Bar Mleczny Różowa Krowa Sun 09:00-20:00 (12:30
  OK), Zapiekarnik Sun 13:00-22:00 (20:00 OK with Sun-Thu close at 22:00).
  **Itinerary 09:30 Bułka z Masłem prose lightly rephrased to "just after
  Sunday doors open" so the timing is explicit.** PASS.

No fabricated tour routes found beyond what QA1 already removed (Cookly
Warsaw). Other food-tour operators (Delicious Poland, Whistling Hound,
byFood, Viator, Wroclaw Food & Vodka) re-checked against operator pages
where accessible; no further defects.

## Section C -- festivals re-verified

- Gastro Miasto: July 25-27, Bulwar Xawerego Dunikowskiego -- confirmed.
- Festiwal Delicje: June 6-8, Rynek -- confirmed.
- Festiwal Pasibrzucha: June 13-15, Partynice -- confirmed (QA1 fix).
- Wrocław Feta Festival: August 1-3 (Aug 1-3 per QA1 fix) -- confirmed.
- RestaurantWeek: Oct 7 - Nov 19 (per source) -- confirmed.
- Beer Geek Madness: April 25-26 2025 at Czasoprzestrzeń, Tramwajowa 1-3
  -- confirmed (Untappd + operator).
- Jarmark Bożonarodzeniowy: Nov 21 - Jan 7, Rynek -- confirmed.

No festival date defects beyond what QA1 already fixed.

## Section D -- thin-category dietary recheck

QA1 already verified all 9 dietary entries (5 vegan, 2 vegetarian, 2 GF)
against happycow.net + wroclawguide. QA2 sample re-verification:

- CUDO Vegan Sushi (vegan): operator's Wolt page + 50-140 postal code
  cross-check **uncovered a postal-code defect** (JSON said 53-310, actual
  50-140). Fixed.
- Vegan AF Ramen (vegan): Oławska 12B 50-123 confirmed across operator +
  veganport + wegerestauracje.
- Talerzyki (vegetarian): Bogusławskiego 34 confirmed (happycow + tripadvisor).
- Pod Przykrywką (vegetarian): Więzienna 18/1 confirmed via wroclawguide.

No new fabrications in dietary. Floor-below counts (halal 0, kosher 0,
vegetarian 2, gluten_free 2) are research-agent choices per QA1's report,
not defects for QA to invent against.

## Section E -- editorial-prose echoes (QA1 carry-forward + this round)

QA1's E section captured all closed-venue echoes and the major rewrites
(HUTA/Nadodrze, Most/nine-course, Bar Mleczny Miś/STÓŁ Sunday, Niewinność
address). QA2-introduced rewrites checked for echoes:

- Wierzbowa 15 chef-name change "House team" -> "Juan Luis Fernández":
  searched for "House team" string across the data tree -- still appears
  on Gustaw's restaurants.json entry which I also updated. Wierzbowa 15
  doesn't appear in itineraries.json or signature-dishes.json
  `where_to_eat` lists, so no further echo to chase.
- Wierzbowa 15 dish-name change (cured-trout + venison -> mackerel +
  trout): not echoed elsewhere in data tree (grepped). PASS.
- Gustaw chef "Kacper Sawoń" addition: not echoed elsewhere. PASS.
- Hala Świebodzki address change: appears only in markets.json and
  generically as "Hala Świebodzki" elsewhere (region.json descriptions);
  no fabricated-address echo to fix.
- Wrocławski Bazar Smakoszy address change: appears as
  "Wrocławski Bazar Smakoszy" or "Bazar Smakoszy" in seasonal-food.json
  autumn paragraph; the prose just says they sell "borowiki and kurki",
  no address echo. PASS.
- Bułka z Masłem hours rewrite: cafes.json tip already corrected;
  itineraries day 2 morning prose explicitly mentions "just after Sunday
  doors open" so the new hours field and the prose are consistent. PASS.

## Section F -- editorial voice and length caps

Validator post-edit pass: 0 ERR, only the same length-cap WARNs as QA1
(mostly description fields running 165-200 chars vs the 165 soft cap), plus
the new Wierzbowa 15 entries which tightened to 180-185 (close to
QA1-pre-existing band). No em/en dashes introduced. Voice consistent.

**Slug-vs-name oddity flagged (not fixed)**: `late-night.json` has a
`slug: "lviv-croissants-late"` entry whose `name` is "Pan Precel". The
slug appears to be residue from an earlier swap; renaming it would require
a redirect since it would change the URL. Leaving as-is for the research
agent to handle as a planned slug-rename if desired; the page renders
fine, no public-facing defect.

## Entities removed by QA2

(None.)

## Entity edits by QA2 (non-prose facts changed)

1. `wierzbowa-15-fd` (fine-dining): chef field "House team" -> "Juan Luis
   Fernández (patron)"; description and must_order rewritten to match
   operator's actual cuisine claim and verifiable signature dishes.
2. `wierzbowa-15` (restaurants): cuisine "Nordic-Polish" -> "Polish-European
   fusion"; description rewritten; signature_dishes changed from "Cured
   fish small plates"/"Game tasting" to "Marinated mackerel with dill
   granita"/"Seasonal trout"; must_order updated.
3. `gustaw-fd` (fine-dining): chef "House team" -> "Kacper Sawoń";
   description rewritten with Bastion Sakwowy context.
4. `gustaw` (restaurants): description rewritten with Bastion Sakwowy +
   chef name.
5. `hala-swiebodzki` (markets): address fabrication corrected to Plac
   Orląt Lwowskich 20B 53-605; hours corrected; source URL repointed to
   gdziezjescwroclaw.
6. `wroclaw-gourmet-bazaar` (markets): address fabrication corrected to
   Paczkowska 26 50-525; hours corrected (Saturday + Sunday window);
   source URL repointed to operator.
7. `bulka-z-maslem-brunch` (brunch): hours field corrected to operator's
   actual schedule; tip rephrased.
8. `bulka-z-maslem` (cafes): tip corrected (room opens 10:00 weekdays).
9. `poke-poke` (street-food): hours corrected (Mon-Thu 12:00-18:00,
   Fri-Sun 12:00-20:00).
10. `ok-wine-bar-wb` (wine-bars): hours corrected (Mon-Thu 17:00-23:00,
    Fri-Sat 12:00-23:00, Sun 12:00-21:00).
11. `cocofli-wine-bar` (wine-bars): hours corrected (Mon-Thu and Sun
    10:00-23:00, Fri-Sat 10:00-00:00).
12. `vertigo-late` (late-night): closes corrected (Sun-Thu 00:00, Fri-Sat
    02:00).
13. `paloma-roasters` (coffee-roasters): hours corrected (Daily 08:00-21:00).
14. `enklawa-hala-targowa` (coffee-roasters): postal code corrected
    (50-156 -> 50-158).
15. `viator-pierogi-and-beer-class` (cooking-classes): group_size corrected
    to "Up to 5".
16. `byfood-wroclaw-private-tour` (food-tours): duration/price/description
    softened to honestly reflect operator's three-tier offering rather than
    claim a single 3-hour 510-zł version.
17. `cudo-vegan-sushi` (dietary/vegan): postal code corrected
    (53-310 -> 50-140).

## Entity-prose rewrites (cross-file echoes)

1. `itineraries.json` `wroclaw-budget-two-days` day 2 Sunday morning prose
   on Bułka z Masłem -- explicit "just after Sunday doors open" added so
   the time matches the corrected hours.

## Defects total: 17 (this round) + carry-forward awareness

This is below the level that would suggest a wholesale upstream
regression. But it confirms the Wrocław-specific structural risk QA1 flagged.
Beyond the 23 defects QA1 caught, QA2 caught:

- 2 additional address fabrications (Hala Świebodzki, Wrocławski Bazar
  Smakoszy) -- bringing the Wrocław-wide total to 5 (HUTA, Niewinność,
  El Gato, Hala Świebodzki, Bazar Smakoszy). The pattern is consistent
  enough that it warrants a structural fix upstream rather than just
  case-by-case QA.
- 1 postal-code defect (CUDO Vegan Sushi: 53-310 -> 50-140).
- 4 hours-field defects (Bułka z Masłem, poké poké, OK Wine Bar, Cocofli,
  Vertigo, Paloma -- 6 if you count individually).
- 2 specific-fact defects on Michelin Selected rooms (Wierzbowa 15 chef
  switch + dish accuracy, Gustaw chef name).
- 2 cooking-class/tour scope softenings (Viator group size, byFood tier
  honesty).

## Below-floor topics after QA2

(Unchanged from QA1.)
- dietary/halal: 0 entries (floor 4) -- research-agent choice
- dietary/kosher: 0 entries (floor 4) -- research-agent choice
- dietary/vegetarian: 2 entries (floor 4) -- below floor pre-QA
- dietary/gluten_free: 2 entries (floor 4) -- below floor pre-QA
- cooking-classes: 4 entries (floor 4) -- exactly at floor
- itineraries: 3 entries (target 10) -- below SEO floor pre-QA

## Flagged for upstream

- **Structural Wrocław data integrity issue**: 5 address fabrications in
  this batch (3 caught by QA1, 2 caught by QA2). Either the research agent
  that built Wrocław regressed on address verification, or the fixup pass
  that ran `address_quoted = entity.address` was systemically copying bad
  addresses forward. Recommendation: every new Wrocław entity should pass
  an independent-directory cross-check at the research stage, not just at
  QA2. Other cities in this batch should also be spot-checked.
- 4 entries with `chef: "House team"` remain in fine-dining.json (only 2
  fixed by QA2 -- Wierzbowa 15 and Gustaw). The pattern of generic chef
  names where a real chef name exists is a low-grade tell. Acceptable per
  schema, not fixed by QA2 because the JSON isn't lying, just generic.
- `late-night.json` slug `lviv-croissants-late` should eventually be
  renamed to `pan-precel-late` (and a redirect from the old slug added) on
  the next research-agent pass.
- All `own_site_only` WARNs from verify_entities (carried from QA1) still
  need independent-directory URLs added by the research agent.
- Whistling Hound food-tour price still unverifiable from the operator's
  page; left at "Contact operator for current pricing".

## Verdict

VERDICT: PASS

The 17 QA2 defects are all judgment-pass corrections (hours, postal codes,
specific dish names, chef-name precision, two more fabricated addresses).
None block ship; all are now corrected in the data tree. The two
additional address fabrications confirm the Wrocław-specific structural
risk QA1 flagged, but the catch rate (5/118 distinct venues = ~4 percent)
is at the high end of "single-agent fan-out drift" rather than evidence of
a complete research regression. The 25-venue sample I cross-checked
against independent directories surfaced only the two new fabrications;
the other 23 venues confirmed cleanly. With the QA1+QA2 sweep complete,
the data tree is ready for the deterministic ship_safety pipeline to run,
followed by generator + sitemap + chmod, with one note for upstream:
the Wrocław batch's address-fabrication rate is higher than other cities
in this round and warrants a process tightening rather than another QA
pass.
