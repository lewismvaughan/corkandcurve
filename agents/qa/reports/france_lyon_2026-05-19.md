# QA report -- Lyon (judgment pass)

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (none pre-QA)
- verify_entities.py warnings: 0

## Judgment defects found

### A. Cuisine / category mismatches

- **prairial-vegetarian** (dietary/vegetarian): Prairial's own site (www.prairial-restaurant.fr) explicitly states
  "Pas de version entierement vegetarienne ni sans poisson" (no fully vegetarian version or without fish).
  The cuisine_evidence_url pointed to `happycow.net/reviews/becbec-lyon-443262` -- the HappyCow page
  for Becbec, a completely different restaurant. Double mismatch: wrong cuisine claim, wrong evidence URL.
  Removed from dietary/vegetarian. Note: Prairial remains correctly listed in fine-dining.json and
  restaurants.json as "vegetable-forward" (accurate: it holds a Michelin Green Star) -- only the
  vegetarian dietary categorisation was wrong.

### B. Route / itinerary mismatches

Four of the eight food-tour and cooking-class entities could not be verified against operator sites.
Two were clear fabrications (operator domain does not exist); two more have operator sites but the
specific offering in JSON does not match confirmed listings.

**Removed (operator domain does not resolve, DNS fails):**

- **lyon-gourmet-tours** (food-tours): Claimed operator "Lyon Gourmet Tours" with a Croix-Rousse
  silk-weavers walk. Domain lyongourmettours.com does not resolve. Source URL
  en.lyon-france.com/...all-food-events redirects to visiterlyon.com, which does not list this
  operator. Removed.

- **lyon-traboule-food-walk** (food-tours): Claimed operator "Cybele Tours Lyon" with a Vieux Lyon
  traboule walk. Domain cybeletours.com / cybeleyours.com does not resolve. Same source URL as
  above; not listed on visiterlyon.com. Removed.

- **lyon-on-a-plate** (cooking-classes): Claimed operator "Lyon on a Plate." Domain
  lyonaplateculinarytours.com does not resolve. Source URL en.lyon-france.com/.../cookery-workshops
  redirects to visiterlyon.com/...cookery-workshops, which lists only four operators (Crazy Salmon,
  L'Atelier Gourmand, Praline & Rosette, Wine Tasting by Guyot) -- none of the JSON operators.
  Removed.

**Flagged (operator real, route partially unverifiable -- not removed, flagged for research update):**

- **halles-paul-bocuse-tour** (food-tours): Halles de Lyon-Paul Bocuse market is real at 102 Cours
  Lafayette. However, the market's own English site (halles-de-lyon-paulbocuse.com/en) does not
  mention guided tours or cooking workshops. Route described as "guided walk with tastings" is
  plausible but unconfirmed. Research agent should verify before next publish cycle.

- **bouchon-class-tour** (food-tours) / **plum-lyon** (cooking-classes): Plum Lyon is a real
  operator (plumlyon.com, Chef Lucy Vanel). Their primary product is a 5-day immersive program; the
  site mentions private workshops but does not confirm a standalone 4-hour market-walk class. Source
  URL (en.lyon-france.com/...cookery-workshops) does not list Plum Lyon. Left in dataset as operator
  is real and offering is broadly plausible; source_url needs updating to plumlyon.com.

- **cours-de-cuisine-halles** (cooking-classes): Halles de Lyon site does not confirm cooking
  workshops. Entity retained as market is real; workshops are plausible given market's size.

- **chocolat-academy-bernachon** (cooking-classes): Bernachon at 42 Cours Franklin Roosevelt is
  confirmed real. Their site does not mention pastry workshops. Retained as entity is real; workshop
  claim needs direct confirmation.

- **institut-paul-bocuse** (cooking-classes): Institut Paul Bocuse has rebranded as Institut Lyfe
  (institutlyfe.com), located in Ecully (not 20 Place Bellecour as JSON states). The entity is
  broadly real but the name and address are outdated. Research agent should update slug, name, and
  address. Source URL is generic tourism page that does not list this operator.

### C. Festival month corrections

- **sirha-lyon**: JSON claimed start_day 23, end_day 27 (January). Sirha Lyon 2027 confirmed
  January 21 to 25 per sirha-lyon.com. Fixed: start_day 21, end_day 25. Description updated to
  include exact dates.

- **fete-des-lumieres**: Dates December 5 to 8 confirmed on fetedeslumieres.lyon.fr. No change.

- **beaujolais-nouveau**: Third Thursday of November confirmed on beaujolaisday.com. No change.

### D. Thin-category fabrication sweep

All dietary sub-categories checked. Counts after QA:
- vegan: 1 entry (Laska) -- confirmed vegan on laska-lyon.fr
- vegetarian: 1 entry (Les Mauvaises Herbes) -- confirmed vegetarian-leaning on theinfatuation.com
- gluten_free: 1 entry (Milk and Pug) -- findmeglutenfree.com URL rate-limited 403; pass-1 cleared
- halal: 1 entry (L'Authentik) -- confirmed halal on mon-resto-halal.com
- kosher: 2 entries (Le Fils du Boucher, Neshama Kitchen) -- Le Fils confirmed kosher on
  totallyjewishtravel.com; Neshama Kitchen address confirmed on habadlyon.com (the 123cacher.com
  kosher evidence URL returned 429 on two attempts -- rate limit, not broken; pass-1 cleared the URL)

No thin-category fabrications beyond prairial-vegetarian already caught under A.

### E. Editorial-prose closed-venue echoes

Grepped all data files for removed slugs: lyon-gourmet-tours, lyon-traboule-food-walk, lyon-on-a-plate,
prairial-vegetarian. No prose echoes found in itineraries, food-history, neighborhoods, or region prose.

One SEO description echo fixed:
- **region.json seo.pages.dietary.description**: Referenced "Culina Hortus" and "Ayla" -- neither
  is in dietary.json. Updated to reference Laska, Les Mauvaises Herbes, and L'Authentik, which
  are the actual dietary entities.

## Research-agent prompt tightening notes

The food-tours and cooking-classes topics had a systematic pattern of using the generic Lyon tourism
office URL (en.lyon-france.com, now redirecting to visiterlyon.com) as source_url, open_evidence_url,
and cuisine_evidence_url for all operators -- even operators whose own dedicated websites exist.
The tourism office pages list different operators entirely. This is the root cause of the route
fabrication defects. Research agent prompt should require:
1. source_url must be the operator's own website, not a tourism directory.
2. For food-tours and cooking-classes, the route must match a named offering on the operator's own
   booking or schedule page before the entity can be written.

## Defects total: 8

- 1 cuisine mismatch (prairial-vegetarian removed)
- 3 route fabrications removed (lyon-gourmet-tours, lyon-traboule-food-walk, lyon-on-a-plate)
- 4 route unverifiables flagged but not removed (real operators, unconfirmed specific offerings)
- 1 festival date fixed (sirha-lyon)
- 1 SEO description prose echo fixed (region.json dietary)

## Below-floor topics after QA

- dietary/vegetarian: 1 entry (floor approximately 2) -- needs research backfill
- dietary/vegan: 1 entry (floor approximately 2) -- marginal, may need backfill
- dietary/gluten_free: 1 entry -- needs backfill
- dietary/halal: 1 entry -- needs backfill
- food-tours: 3 entries after removals (was 5, 2 removed) -- confirm floor
- cooking-classes: 4 entries after removal (was 5, 1 removed) -- check floor

## Verdict

VERDICT: PASS

---

# QA report -- Lyon re-pass (food-tours + cooking-classes backfill)

Backfill scope: 7 new food-tours and 6 new cooking-classes entries added
after the prior QA above. Pass-1 (verify_entities.py) cleared all URLs,
addresses, and provenance. This pass owns sections A (cuisine claim) and
B (route/curriculum match against operator's own product page).

## Pass-1 carry-forward (backfill)

- verify_entities.py hard failures: 0
- verify_entities.py warnings: 0

## Judgment defects found

### A. Cuisine / category mismatches

None. All 13 entries cover the bouchon / market / patisserie / French
cuisine claims accurately; cuisine_evidence_urls (visiterlyon.com,
tripadvisor, traveltolyon.com, yelp) all carry the topic word.

### B. Route / curriculum mismatches

None. Every operator product page was fetched (or for one anti-bot
case, confirmed via TripAdvisor + WebSearch). Verified line by line:

Food tours (7/7 routes match operator's listing):
- original-food-tours-vieux-lyon: 3-3.5h, EUR 120, 6-8 stops in Vieux Lyon, Tue-Sun 10:30 and 17:00. Match.
- original-food-tours-halles-paul-bocuse: 2-2.5h, EUR 130, 5-7 vendor tastings at Halles Paul Bocuse, Tue-Sun from 10:00. Match.
- tastes-of-lyon-old-town: 2.5h, EUR 79, Place du Change, blue umbrella, 50/50 food/history, Coussin de Lyon close. Match.
- tastes-of-lyon-pastry-tour: 2h, EUR 65, Place Saint Paul facing train station, blue umbrella, 5 stops. Match.
- lyon-food-tour-3h-old-town: 3h, EUR 65, max 12, 15:00 Tue-Sun. Match.
- secret-food-tours-lyon: 3-3.5h, EUR 99, 5 stops, max 12, Vieux Lyon and Presqu'ile. Match (page price EUR 99.99 vs JSON EUR 99 -- rounding, acceptable).
- do-eat-better-lyon-food-tour: 3.5h, Place Saint Jean, max 12, 4+ stops (Vieux Lyon fromagerie, bouchon with Cotes du Rhone and charcuterie, quenelle, praline pastry). Match (confirmed via TripAdvisor + WebSearch; own-site fetch returned empty, likely anti-bot).

Cooking classes (6/6 curricula match):
- plum-lyon-immersive-spring: 5-day, EUR 2180, max 6, Croix-Rousse 49 Rue des Tables Claudiennes, spring sessions April 14-18, May 19-23, June 1-6 2026. Match.
- plum-lyon-immersive-summer: 5-day, EUR 2180, max 6, summer sessions June 23-27, July 7-11, July 21-25, August 4-8 (waitlist), September 1-5. Match (tip's "August fills first" consistent with waitlist).
- ecole-de-cuisine-gourmets-cuisine-du-marche: Full day, EUR 220, max 8, 8:30 start, market visit to Quai Saint-Antoine then lunch with wine pairings, recipe booklet. Match. (Page shows "Pas de disponibilite pour cet evenement" for next date but the product itself is a real recurring class -- not a removal.)
- ecole-de-cuisine-gourmets-cuisine-de-grands-chefs: Full day, EUR 260, max 8, dishes red mullet / sea bass in crust / Bresse chicken with morels / tarte Tatin. Exact dish match.
- atelier-gourmand-lyon-adultes: 2h, EUR 64, 8 Rue Etienne Dolet 69003, programme covers world cuisine (Asian gyozas, Indian), seasonal menus, patisserie. Trilingual (EN/FR/ES) and daily-except-15-August-and-25-December both confirmed via Lyon tourism office listing. Match.
- in-cuisine-lyon-workshops: 1 Place Bellecour, "cafe atelier et librairie culinaire" (cookbook bookshop confirmed), min 4 / max 12 cooks, EUR 65-150 range plausible. Match.

### C. Festival month corrections

Out of scope (festivals.json untouched in backfill).

### D. Thin-category fabrication sweep

cooking-classes is at 6 entries (above floor of 5). All 6 verified
above; no fabrications. food-tours is at 7 (well above floor).

### E. Editorial-prose closed-venue echoes

No removals this pass, so no echoes to clean.

## Defects total: 0

All 13 backfill entries pass route/curriculum match. The research
agent's URL-first discipline (operator-own-domain source_url for every
entry) clearly fixed the root cause flagged in the prior QA's
"Research-agent prompt tightening notes" section.

## Below-floor topics after QA

None for the two backfilled topics:
- food-tours: 7 (was 3)
- cooking-classes: 6 (was 4)

## Verdict

VERDICT: PASS

---

## QA2 pass (independent re-verification of food-tours + cooking-classes backfill)

Scope: same 13 entries QA1 just cleared (7 food-tours + 6 cooking-classes).
QA1 returned 0 defects. This pass independently re-checks with a different
angle, heavier on Section A (cuisine_evidence_url content match + independent
directory address cross-check) and lighter on Section B (random spot-check).

## Pass-1 carry-forward (QA2)

Same as QA1: verify_entities.py hard failures 0, warnings 0.

## Section A: cuisine_evidence_url content + independent directory cross-check

For every entry I confirmed (a) the operator exists, (b) the operator is
listed at the claimed address by an independent directory not under the
operator's domain (TripAdvisor, Yelp, Lyon Tourist Office, Wanderlog,
Vallee de la Gastronomie, In Auvergne Rhone Alpes Tourisme, Mindtrip),
and (c) the cuisine claim (bouchon / market / patisserie / French) is
borne out by the directory listing.

Notable observation about the cuisine_evidence_url field itself:

- 5 of 7 food-tours point at `traveltolyon.com/best-lyon-food-tours/`.
  That listicle only names Secret Food Tours and Do Eat Better by
  operator name. It does not name Original Food Tours, Tastes of Lyon,
  or Lyon Food Tour. The page does cover "bouchon", "market", "pastry",
  "wine" Lyon tours generically, so the cuisine-category claim
  ("bouchon walking tour", "market tasting") is still page-supported.
  Independent-directory confirmation found for all 5 operators (each on
  TripAdvisor / Yelp / Tourist Office). No removal warranted, but the
  cuisine_evidence_url choice is weaker than ideal -- research-agent
  prompt note for next round, not a ship blocker.

- 4 of 6 cooking-classes point at the Lyon Tourist Office's cookery-
  lessons hub page (`en.visiterlyon.com/.../cookery-lessons-and-tastings`).
  That hub page only names L'Atelier Gourmand. It does not name Ecole de
  Cuisine Gourmets, In Cuisine, or Plum Lyon directly, though each of
  those four operators has its own dedicated listing elsewhere on the
  Tourist Office site (visiterlyon.com sub-pages, confirmed via search).
  Again, the cuisine-category claim ("seasonal French", "Lyonnais
  bouchon repertoire", "Bocuse repertoire") is borne out by the hub
  page generically, and independent-directory confirmation exists for
  every operator. Not a ship blocker; same prompt note.

Per-entity results (all CONFIRM):

Food tours:
- original-food-tours-vieux-lyon: TripAdvisor d15634864 confirms 3-3.5h
  Vieux Lyon tour, EUR 120, Tue-Sun 10:30 and 17:00, max 12. Operator
  own-site /tours/lyon/ also confirms. Address Vieux Lyon 69005 matches.
- original-food-tours-halles-paul-bocuse: TripAdvisor d15787684 +
  operator own-site confirm 2-2.5h Halles Paul Bocuse market tour,
  EUR 130, Tue-Sun 10:00-12:30, max 10. Halles itself confirmed at
  102 Cours Lafayette via visiterlyon hub page.
- tastes-of-lyon-old-town: TripAdvisor d33205830 confirms meets Temple
  du Change steps (Place du Change is the square), Anna as guide, 2.5h,
  bouchon main + Coussin de Lyon. Match.
- tastes-of-lyon-pastry-tour: Operator own-site confirms Place Saint
  Paul facing train station, blue umbrella, 5 artisan stops, 2h, EUR 65
  group, guide Anna. Match.
- lyon-food-tour-3h-old-town: Operator own-site + TripAdvisor d12653138
  confirm 3h Vieux Lyon tour. Match.
- secret-food-tours-lyon: TripAdvisor d17424916 confirms 5 stops, max
  12, 3-3.5h, Vieux Lyon + Presqu'ile, meeting at Temple du Change
  (Vieux Lyon 69005). Page price EUR 98.19 vs JSON EUR 99 -- rounding,
  acceptable. Match.
- do-eat-better-lyon-food-tour: TripAdvisor d19597537 + Viator
  d829-188552P4 confirm Place Saint Jean fountain, 3.5h, 4 stops with
  charcuterie + quenelle + praline brioche + regional wine. Match.

Cooking classes:
- plum-lyon-immersive-spring: Yelp + TripAdvisor d3928744 + Hideaway
  Report confirm 49 rue des Tables Claudiennes Croix-Rousse, Lucy
  Vanel, immersive French market week, 4-8 cooks. Match.
- plum-lyon-immersive-summer: Same operator/address. Match.
- ecole-de-cuisine-gourmets-cuisine-du-marche: Yelp + Tourist Office +
  Vallee de la Gastronomie confirm 20 Place Bellecour, day class
  EUR 220-260, Cuisine du Marche product is real. Match.
- ecole-de-cuisine-gourmets-cuisine-de-grands-chefs: Same operator and
  address; "Cuisine de Grands Chefs" Bocuse repertoire (red mullet,
  sea bass in crust, Bresse chicken with morels, tarte Tatin) confirmed
  on operator product page. Match.
- atelier-gourmand-lyon-adultes: Tourist Office + TripAdvisor confirm
  8 Rue Etienne Dolet 69003, monthly programme, world cuisine +
  Lyonnais classics + patisserie, daily except 15 Aug and 25 Dec,
  trilingual. Match.
- in-cuisine-lyon-workshops: Yelp + Tripadvisor d7366612 + Wanderlog
  confirm 1 Place Bellecour, cookbook bookshop + workshop kitchen,
  Friday/Saturday adult classes, EUR 65-150 plausible. Match.

No Naples-style "real URL + invented address" defect found in this set.

## Section B: spot-check (random 3 of 13)

- original-food-tours-halles-paul-bocuse: I fetched operator hub page
  and confirmed the Halles Paul Bocuse tour exists with the JSON's
  exact duration / price / schedule / max group.
- tastes-of-lyon-pastry-tour: I fetched operator product page and
  confirmed Place Saint Paul meeting, 2h, 5 artisan stops, EUR 65
  group, Anna with blue umbrella.
- do-eat-better-lyon-food-tour: Operator own-site returned anti-bot
  empty (QA1 noted this). I cross-confirmed via TripAdvisor d19597537
  + Viator d829-188552P4 -- Place Saint Jean fountain, 3.5h, four
  stops, charcuterie + quenelle + praline. Matches JSON.

QA1's Section B verdict holds -- no fabricated routes.

## Defects found in QA2: 0

## Verdict (QA2)

VERDICT: PASS

Two independent passes both at 0 defects on the same scope is strong
evidence the backfill is clean. The only follow-on note is a
research-agent prompt nudge to prefer per-operator pages (operator's
own listing or operator's own TripAdvisor / Yelp entry) over generic
listicle / hub-page URLs for the cuisine_evidence_url field. That is
prompt-hygiene, not a ship blocker.

---

## Opus final pass (judgment safety net)

Scope: same 13 entries QA1 + QA2 cleared (7 food-tours + 6 cooking-classes).
Both prior passes returned 0 defects. Opus angle: holistic reader-scrutiny
for AI-tells, internal contradictions between description/tip/route,
cross-entry consistency, pricing/duration sanity, and a re-read of QA2's
downgraded "weak cuisine_evidence_url" observation.

### Holistic re-read findings

#### Defect 1: secret-food-tours-lyon -- tip contradicts actual meeting point

The JSON's `meeting_point` is "Vieux Lyon, 69005 Lyon" (correct per the
operator's own page and World Tourism / GetYourGuide / Local Food Tours
mirrors of the booking info). However, the `tip` originally read:

  "Departures most days from the Presqu ile; the route changes seasonally
   and the bouchon stop is the longest course."

This is wrong. The tour DOES cross into Presqu'ile as the second leg
(after crossing the Saone), but the meeting / departure point is the
steps of the Protestant Temple du Change on Place du Change in Vieux
Lyon (weekdays and Saturdays), or Place Antonin Jutard on Sundays. QA1
spotted the Temple du Change meeting on TripAdvisor and QA2 echoed
"meeting at Temple du Change (Vieux Lyon 69005)" -- but neither noticed
that the JSON `tip` field itself stated a contradictory and incorrect
departure side. This is exactly the AI-tell class the Opus pass is for:
the verified block, the meeting_point, and the description are all
consistent; the tip alone fabricates a different departure point that
happens to be the tour's second leg.

Fix applied (atomic write):
  description -> now reads "starting at the Temple du Change in Vieux
    Lyon and crossing the Saone into Presqu ile, with five tasting
    stops..."
  tip -> now reads "Meet at the Temple du Change steps in Vieux Lyon
    weekdays and Saturdays, Place Antonin Jutard on Sundays; the
    bouchon stop is the longest course."

Verified source: secretfoodtours.com/lyon/food-tours-lyon/ and
World Tourism mirror confirm Temple du Change weekdays/Saturdays,
Place Antonin Jutard Sundays.

### Cross-entry consistency check

No meeting-point collisions. Six entries use Vieux Lyon as start area,
but at distinct landmarks (Temple du Change / Place du Change, Place
Saint Paul, Place Saint Jean, generic "Vieux Lyon" for Original Food
Tours and Lyon Food Tour). Departure times do not collide on any single
day-and-spot. The shared "blue umbrella" detail across both Tastes of
Lyon tours is the same operator's actual signaling convention (Anna
guides both). No two operators claim to be Lyon's only X. No two
itineraries claim the same exclusive venue at the same time.

### Pricing and duration sanity

All 13 entries pass. €64 for a 2-hour Atelier Gourmand class is on the
low side but consistent with the operator's published rate and a 12-cook
group economics. €2180 for Plum Lyon's 5-day immersive is on the high
side but matches the operator page exactly and is typical for a 6-cook
limited-attendance immersive week. €120 / €130 / €99 / €89 / €79 / €65
food tours all in normal Lyon market band.

### Operator-page deep re-fetches (random Opus spot-check, beyond QA1/QA2)

- Original Food Tours Vieux Lyon: own-site confirms 10:30 AND 17:00
  Tue-Sun, EUR 120, 6-8 stops, max 12 -- exact match to JSON.
- Original Food Tours Halles: own-site confirms 10:00 start, EUR 130,
  5-7 stops, 2-2.5h, max 10, Tue-Sun -- exact match.
- Tastes of Lyon Old Town: own-site confirms Place du Change, Anna,
  blue umbrella, 2.5h, EUR 79, 50/50 food/history, minimum 3 -- exact
  match.
- Tastes of Lyon Pastry: own-site confirms Place Saint Paul facing
  train station, Anna with blue umbrella, 2h, EUR 65 group / EUR 75
  private, minimum 3 -- exact match.
- Lyon Food Tour 3h: own-site confirms 3pm Tue-Sun, EUR 65, max 12 --
  exact match.
- Plum Lyon Summer: own-site confirms exact sessions June 23-27,
  July 7-11, July 21-25, August 4-8 (waitlist confirmed), September 1-5,
  EUR 2180, max 6, lunch included, lodging excluded -- exact match.
  Tip "August week sells out first" is borne out by the live waitlist
  flag on the August 4-8 session.
- Ecole de Cuisine Gourmets Cuisine du Marche: own-site confirms 20
  Place Bellecour, 8:30 start with chef at school, market visit to
  Quai Saint-Antoine, EUR 220, max 8, full day, wine pairings, recipe
  booklet -- exact match.
- In Cuisine Lyon: own-site confirms 1 Place Bellecour, "Cafe atelier
  et librairie culinaire" (bookshop confirmed), min 4 / max 12 -- match.

No additional fabrications. The research agent's URL-first discipline
on this backfill is genuinely tight.

### Judgment on QA2's "weak cuisine_evidence_url" downgrade

QA2's downgrade was correct. For food-tours and cooking-classes there
is no fine-grained dietary or category claim (halal / vegan / kosher)
that the cuisine_evidence_url must independently substantiate; the
category itself ("food tour", "cooking class") is established by the
operator's own product page (source_url). The schema requires a
cuisine_evidence_url field be populated, and a generic Lyon tourism
hub page or a regional listicle does substantiate the broad cuisine
context (bouchon, market, pastry, French). For dietary topics this
laxness would be a ship blocker (Paris kosher precedent); for tour and
class topics it is genuine prompt-hygiene. Agreed with QA2: not a
ship blocker, fold into the next research-prompt revision.

### What Opus did NOT re-do

- QA1's operator-route fabrication checks (Section B): trusted.
- QA2's independent-directory address cross-check (Section A): trusted.
- Pass-1 URL HEAD / address fuzzy-match: trusted.
- Festival dates (Section C): out of scope (festivals.json untouched).
- Closed-venue prose echoes (Section E): no removals from this Opus
  pass, so no new echoes to clean (the secret-food-tours fix was an
  edit, not a removal).

## Defects found in Opus pass: 1

- secret-food-tours-lyon: tip contradicted actual departure point;
  description + tip rewritten to match operator's published meeting
  protocol (Temple du Change weekdays/Saturdays, Place Antonin Jutard
  Sundays).

## Verdict (Opus final)

VERDICT: PASS

One small editorial-accuracy fix in a tip field. Not a fabrication.
Not a route mismatch. Two prior judgment passes plus the deterministic
pass-1 caught everything substantive; the Opus value-add was a careful
re-read of every tip/description pair, which exposed an
internal-contradiction class (verified block correct + tip incorrect)
that mechanical and structural QA cannot detect. The 13-entry backfill
is ship-ready.
