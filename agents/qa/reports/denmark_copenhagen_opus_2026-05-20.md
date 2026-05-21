# QA report — Copenhagen (Opus final pass)

Country: denmark
City: copenhagen
Date: 2026-05-20
Pass: Opus final (judgment pass-3)

## QA1 and QA2 carry-forward

QA1 (2026-05-20) made 8 file-level rewrites across 4 files: 3 Sunday
itinerary day-of-week × hours fixes, 1 Wednesday onsdagssnegl fix, 2
neighborhood vibe rewrites (Manfreds, Mielcke & Hurtigkarl phantoms),
14 region.json SEO description rewrites (count-alignment + phantom
removal), 1 food-history era summary fix. Verdict: PASS.

QA2 (2026-05-20) made 16 file-level edits plus 1 entity removal across
15 files: Pompette/Andersen Bakery/Timm Vladimirs Køkken address
fixups (with `verified.address_quoted` rolls), Café Wilder 1972 to
1984 propagated across 4 files, Sankt Annæ 1897 to 1894 propagated
across 2 files, chef-name corrections (Hiroshi Andersen to Takaki
family, Sebastian Vinther Olsen to Quistorff, Jeson to Jason
Renwick), fabricated vendor lists at Tivoli Food Hall and Broens
Gadekøkken, removal of Copenhagen Food Tours Vesterbro (route
fabrication on real operator) leaving food-tours at 4, Geranium and
Alchemist booking-claim honesty rewrites, Geranium dietary "fully
vegetarian 2022" framing fix, Home of Carlsberg rebrand handling.
Verdict: PASS.

## Opus judgment defects found

Three factual-drift defects survived QA1+QA2. None are
existence-level; all are specific-fact claims that needed an
operator-history deep-read.

### A2. Specific-fact / press-credential drift

1. **food-history.json, 2003 era: "noma topped the World's 50 Best
   list four times"** — incorrect count. The original noma was #1 in
   2010, 2011, 2012 and 2014 (four times). After the 2018 relocation,
   noma 2.0 topped the list again in 2021. The total is **five times
   ever**, putting noma on par with El Bulli as the only restaurants
   to ever top the list five times. Fixed to "noma topped the World's
   50 Best list five times (2010, 2011, 2012, 2014 and 2021)."
   Confirmed via The World's 50 Best Restaurants official site and
   Identità Golose retrospective.

   **Upstream regression**: research agent. The "four times" framing
   counts only the original noma; agents researching this in 2026
   should be writing the cumulative 50 Best figure.

2. **food-history.json, immigrant-influences Japanese:
   "Austrian chef Philipp Inreiter (formerly Tokyo's RyuGin)"** —
   wrong Tokyo restaurant. Inreiter trained at Tokyo's **Konjiki
   Hototogisu** (the one-Michelin-star Shinjuku ramen shop), not at
   RyuGin (a three-Michelin kaiseki). His earlier kitchens were
   noma and Relae in Copenhagen. Fixed to: "Austrian chef Philipp
   Inreiter (formerly noma and Relae in Copenhagen, with a ramen
   apprenticeship at Tokyo's Konjiki Hototogisu)." Confirmed via
   Slurp Ramen About + The Shift List interview + Creative Chefs
   Summit bio.

   **Upstream regression**: research agent. The agent reached for a
   famous Tokyo kitchen and substituted RyuGin without checking the
   ramen-specific apprenticeship. Same defect class as Naples
   sibling-credit borrowing (a Michelin nod transferring to the
   wrong restaurant): one Tokyo Michelin name swapped for another
   despite different cuisine genre. QA1/QA2 didn't catch because
   neither did a chef-bio cross-check on a non-entity prose
   reference.

### Other minor drift

3. **bakeries.json, Hart Bageri Frederiksberg: "now runs nine
   locations across Copenhagen"** — count is **ten** as of early
   2026 per Hart's own locations page (Frederiksberg, Holmen,
   Vesterbro Kødbyen, Nørrebro, Østerbro, Reffen, Carlsberg Byen,
   Islands Brygge, city centre, plus a tenth opening). Fixed to "ten
   locations across greater Copenhagen". Confirmed via Hart Bageri
   official + Colorful Nordic 2026 January feature.

   **Upstream regression**: research agent (count drift on
   fast-expanding chain; was probably nine when researched). Not a
   QA1/QA2 miss per se since the count was right at some point in
   recent memory; just stale.

4. **casual-dining.json, Restaurant Sankt Annæ description: "a
   short walk from the Royal Palace with a charming canal-side
   terrace"** — Sankt Annæ Plads is a tree-lined square (former
   parade ground / promenade), NOT canal-side. The nearest canal is
   ~100m east at the harbour-front Kvæsthusbroen pier; the square
   itself doesn't sit on a canal. The restaurant's outdoor seating
   is on the tree-lined sidewalk on the square. Rewrote to "with
   tree-lined outdoor seating on the square in warmer months."
   Confirmed via VisitCopenhagen + Sankt Annæ Plads Wikipedia +
   Danish Design Review.

   **Upstream regression**: research agent. Generic
   "Copenhagen-canal-side" geographic template slapped onto a
   square that isn't canal-side. A2 caught the Pompette
   triangulation defect in QA2; this is the same defect class one
   level milder.

### Cross-source festival re-check (Section C)

Re-confirmed two of the five festivals against a non-organizer
source independent of QA2's checks:

- **Mikkeller Beer Celebration 22-23 May 2026** confirmed via the
  Mikkeller UnitedTickets event page (cuisine_evidence_url) which
  has "2026" literally in the URL slug. QA2 noted the same.
- **Copenhagen Cooking and Food Festival 21-30 August 2026**
  confirmed via VisitCopenhagen events listing as 10-day late-
  August window. QA2 noted the same.

No festival date defects found.

### Itinerary geographic-adjacency re-walk

Re-checked all "next door" / "around the corner" / short-walk
phrases:

- "Mirabelle Spiserìa vineria next door" to Bæst — both at
  Guldbergsgade 29 (sister venues in the same Puglisi building).
  Verified accurate.
- "Mikkeller Baghaven next door" to Lille Bakery (bakeries.json tip
  + itinerary Day 2) — addresses Refshalevej 213A and 169B are
  ~250-400m apart on the same Refshaleøen island. Multiple
  contemporary sources (Refshaleøens Ejendomsselskab listings,
  travel features) treat them as adjacent; the framing holds as
  same-block-on-the-island language. Accept.
- "Walk down to the Coffee Collective on Jægersborggade in Nørrebro"
  after Juno on Århusgade — ~2km between Østerbro and Nørrebro,
  framed as a walk. Acceptable framing.

No adjacency defects.

### Phantom-named-venue (E3) safety sweep

Walked every prose-bearing field across all 27 files. No surviving
phantom venues. All capitalized proper nouns in prose resolve to
either an entity in the data or a research-excluded venue used in
historical context only (noma, Relae, Souls, Manfreds for context).

### Stale verified-block URLs (E4) safety sweep

All `checked_on` rolled to 2026-05-20 across QA2's entity edits
(Pompette wine-bars + hidden-gems, Andersen Bakery, Timm Vladimirs
Køkken, Home of Carlsberg). For my three prose-only edits
(food-history era summary, food-history immigrant-influences,
casual-dining Sankt Annæ description) no `verified` blocks were
touched (these are not entity prose with addresses; food-history
has no entity provenance, casual-dining edit was the descriptive
text not the address). bakeries.json Hart Bageri Frederiksberg
edit is a count change in the description; `verified` block is
already at 2026-05-20 and the address remains accurate.

### Sibling-credit, deceased-chef, generational-ownership scan

- Andersen & Maillard (Milton Abel + Hans Kristian Andersen at
  Nørrebrogade in 2018) verified against the operator's About page
  and Visit Copenhagen press kit. Active, both founders alive,
  Milton Abel correctly credited as former noma pastry chef. ✓
- Hija de Sanchez and Cantina credited to Rosio Sanchez (former
  noma); operator owned and chef alive. ✓
- Bæst, Mirabelle Spiserìa, Mirabelle Vineria all credited to
  Christian Puglisi. All three are part of his Madhuset Bæst group
  (former Relae owner). No sibling-credit borrowing. ✓
- Geranium credited to Rasmus Kofoed (chef-owner, alive, currently
  running). ✓
- Alchemist credited to Rasmus Munk (chef-owner, alive). ✓
- Kadeau Copenhagen credited to Nicolai Nørregaard. ✓
- Jordnær credited to Eric Kragh Vildgaard. ✓
- Marchal credited to Jakob de Neergaard. ✓
- Iluka credited to Beau Clugston. ✓
- Slurp Ramen credited to Philipp Inreiter (Konjiki Hototogisu
  apprentice; fixed above). ✓
- Hart Bageri credited to Richard Hart (former Tartine head baker).
  ✓
- Juno credited to Emil Glaser (former noma cook). ✓
- Restaurant Barr credited to Thorsten Schmidt. The reopening at
  Strandgade 93 from June 1, 2026 (after the noma kitchen
  residency) is consistent across restaurants.json, fine-
  dining.json, neighborhoods.json, and food-history.json. ✓
- Beyla, Ark and Beyla-gluten-free all credited to Jason Renwick /
  Ark Collection. Beyla framed as the daytime vegan-and-gluten-
  free Ark Collection cafe in Carlsberg Byen, not as a successor
  to Souls (per QA2's rebrand clarification). ✓
- Café Wilder (1984, not 1972) propagated to all 4 files; no
  surviving 1972 echo. ✓
- Restaurant Sankt Annæ (1894, not 1897) propagated to 2 files
  plus food-history era references (which say "1880s" generically
  for the smørrebrød era — fine). ✓
- Schønnemann (1877) propagated correctly. ✓
- Lê Lê (Vesterbrogade, 2003) — opened 2003 by the Lê family in
  collaboration with Pierre Truchot. Operator confirmed. ✓
- Adam Aamann at Aamanns 1921; Magnus Pettersson at Selma; Claus
  Meyer at Meyers Madhus all current and accurate. ✓

### Itinerary day-of-week × hours full re-walk (Section A2)

All venues in all 3 itineraries × all days × all venue hours
verified consistent against entity hours fields after QA1's 4 fixes
and QA2's confirmation. No surviving day-of-week mismatches.

### Excluded-venue active-reference scan

Re-checked Noma, Restaurant 108, Manfreds, Relae, Restaurant Bror,
Souls. All references in the tree are historical/context-only:
- Noma: "ended regular service in late 2024 / 2024", "former noma
  pastry chef" / "former noma cook" / "former noma chef" credits,
  "Restaurant Barr briefly hosted a residency in the noma kitchen
  in early 2026". All historical / former-employer framing. ✓
- Relae: One context-only reference in the Slurp Ramen chef bio
  (Philipp Inreiter at Relae before Slurp). Acceptable.
- Souls: Beyla framed as the same restaurant rebranded under the
  Ark Collection (per QA2 clarification), not as successor.
- Manfreds: removed in QA1; no surviving reference. ✓
- Restaurant 108 / Bror: no references. ✓

## Defects total: 4 file-level rewrites across 3 files

- food-history.json: 2 fixes (noma 50 Best count; Slurp Ramen chef
  Tokyo apprenticeship)
- bakeries.json: 1 fix (Hart Bageri location count nine → ten)
- casual-dining.json: 1 fix (Restaurant Sankt Annæ canal-side →
  tree-lined square)

## Upstream prompt regressions to tighten

1. **Research agent**: chef-bio Tokyo training defaults to a
   marquee fine-dining name when the chef actually trained at a
   ramen-specific shop. Specifically: when a chef opens a
   format-specific restaurant (ramen, sushi, BBQ), confirm the
   training kitchen matches that format's specialization, not
   generic "famous Tokyo restaurant". This is a sibling-credit
   borrowing defect class within a single chef's CV.
2. **Research agent**: cumulative-count claims for famous
   restaurants ("X has been #1 N times") drift across years and
   need a recheck against the current authoritative source for the
   ranking. Pattern: agent uses memory-cached count from a year or
   two ago.
3. **Research agent**: geographic templates ("canal-side terrace"
   for any Copenhagen restaurant) get glued onto venues that don't
   match. Confirm the geographic specifics from a map source, not
   from a city-template.
4. **QA1/QA2**: chef-name structural check (per QA PROMPT.md
   A2) was scoped to entity prose but did not cover non-entity
   prose in food-history.json immigrant-influences. Worth adding
   to QA1 walk in future: "every chef name in food-history must
   verify against current operator About page or 2024-2026
   press."

## Below-floor topics after Opus pass

Unchanged from QA2:
- dietary/kosher: 0 (no Copenhagen kosher ecosystem)
- dietary/halal: 2
- dietary/vegetarian: 2
- dietary/gluten-free: 2
- coffee-roasters: 5
- cooking-classes: 5
- markets: 5
- food-tours: 4 (one below floor after QA2 route-fabrication
  removal; do NOT backfill from invention)
- day-trips-food: 5
- festivals: 5
- breweries: 5

## Verdict

VERDICT: PASS

The four Opus defects are all specific-fact research-agent drift
that QA1/QA2 didn't catch because they require an external
chef-bio / map / count cross-check rather than entity-prose
internal consistency. The shipping-blocking defects (existence,
addresses, day-of-week × hours, festival months) are all clean
after QA1 and QA2. The four edits here are factual hygiene
improvements; none invalidate the city's overall accuracy budget.
Copenhagen is ship-ready.
