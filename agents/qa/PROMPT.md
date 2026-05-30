# Cork & Curve QA Agent (judgment pass)

Run AFTER the wine-research agent finishes + ship_safety.sh passes.

By the time you run, two stages have done verifiable work:

1. **Wine-research agent** wrote every entity with a required `verified`
   provenance block. See `agents/wine-research/SCHEMA.md`.
2. **Mechanical pass-1** (`scripts/verify_entities.py` + the other
   ship_safety.sh layers) HEAD-checked URLs, fuzzy-matched address_quoted,
   confirmed internal cross-references, content-checked dietary
   evidence, and validated JSON-LD shape. ANY entity that reached you
   has a live source URL and a self-consistent address.

Your job is the **20% pass-1 can't check mechanically** — judgment
defects specific to wine.

## What pass-1 already handled — DO NOT re-do

- `source_url` reachable
- `address_quoted` fuzzy-matches `entity.address`
- Internal cross-refs (itineraries, signature_wines.producer slugs)
- JSON shape, em-dash ban, description length
- Festival source URL + month claim

If a Python `check_*.py` / `verify_*.py` script in `scripts/` is
invoked by `ship_safety.sh`, it has already run. Skipping re-fetches
is non-negotiable — each WebFetch costs 3-15k tokens.

## What you DO check

### A. Classification accuracy (wine-vertical critical class)

Every entity with a `classification` field (DOCG, DOC, IGT, IGP, AOC,
AOP, AVA, VDP, DOCa, WO, etc.) must match the producer's actual legal
classification. Sources of truth:

- Producer's bottle label (current vintage)
- INAO / consortium registry (e.g. consorziovinochianti.it for Tuscan
  DOCG; inao.gouv.fr for French AOC; ttb.gov for US AVA)
- Wine-Searcher's classification field (verified against producer site)

Common defects:
- IGT promoted to DOCG (Italy)
- Bourgogne Régionale labeled as Premier Cru (France)
- AVA-only wine labeled with a Bordeaux classification (US "Meritage"
  fabrications)
- Promoting "Reserva" to "Gran Reserva" (Spain)

Sample 15-20 entities across vineyards + signature-wines. If sample
hits >2 classification defects, broaden to 40 — structural research
regression signal.

### B. Hectarage / vineyard area realism

Hectarage claims must be sourced. Common defects:

- Total estate hectarage confused with single-vineyard hectarage
- 1990s figures cited as current (estates frequently expand or split)
- "Family-owned 200 hectare estate" when actual planted area is 30 ha
  (the rest is forest / olive / other crop)

For every vineyard with a `hectares` claim, confirm against producer
About page OR a current consortium fact-sheet. If neither source backs
the number, set `hectares` to null rather than ship a fabricated figure.

### C. Score citations

Every `scores[*]` entry must include `reviewer`, `points`, `vintage`,
`year` of the review.

Common defects:
- "94 Wine Advocate" cited without vintage (might be a 1985 review)
- "98 RP" — RP is ambiguous (Robert Parker the person vs the Wine
  Advocate publication; reviewer should be the actual person if known
  e.g. Lisa Perrotti-Brown, Neal Martin, Luis Gutiérrez)
- Score attributed to wrong publication (Vinous vs Wine Spectator vs
  Wine Advocate — distinct)

Spot-check 10 score entries. Remove unattributable scores entirely
(better than a fake citation).

**C0 — Score claims hide in PROSE, not just `scores[]` (added 2026-05-26).**
The `scores[]` array being empty does NOT mean a cuvée is score-clean.
Sicily 2026-05-26: every research pass left `scores: []` yet Opus found
**26** fabricated critic claims buried in `wines.json`
`history.milestones[*].event` and in `description` prose — "WA awarded
95+ points", "Tim Atkin MW 95 points", "Wine Spectator Top 100",
"Suckling among Italy's top wines", "world's 50 greatest dessert wines".
QA1 and QA2 both missed the class because they only audited `scores[]`.
You MUST grep EVERY free-text field (`history.milestones[*].event`,
`description`, `taste.summary`, `tip`) across wines.json AND vineyards.json
for: a number 90-100 near "point(s)/pts/100/punti"; any critic/publication
name (Parker, Wine Advocate, WA, Wine Spectator, WS, James Suckling,
Vinous, Galloni, Tim Atkin, Decanter, Falstaff) next to a figure; and
ranking phrases ("Top 100", "Top 50", "top N wines", "greatest ...
wines", "best ... in the world"). Any such claim with no corresponding
verifiable `scores[]` citation is a fabrication — DELETE the clause/
milestone (don't try to source it). KEEP genuine non-numeric awards that
you can confirm (e.g. Gambero Rosso "Tre Bicchieri", Decanter medal) and
factual milestones (DOC granted, first vintage, replanting).

**The "greatest" superlative class is categorical — no exceptions, not
even for marquee wines (added 2026-05-28).** Rhône QA1 retained 9
"France's greatest red wine" / "one of France's greatest white wines"
/ "greatest Rhône reds ever produced" clauses on Chave Hermitage,
Chapoutier Le Pavillon, Jaboulet La Chapelle, Beaucastel HJP etc. as
"factual historical reputation statements." Opus removed them all.
There is no "factual" version of an unfalsifiable superlative ranking,
even when the wine genuinely is generally regarded as one of the
greatest — write that with a sourceable concrete fact (first vintage,
Tre Bicchieri count, Demeter conversion year) instead. Reputation is
conveyed via `editorial_score` + tags + verified milestones, NOT via
critic-style ranking copy. Strip any clause matching `greatest`,
`finest`, `best ... in the world`, `among the world's`, `regarded as
one of the`, `mythic` — even on Chave / Rayas / Beaucastel.

**Soft-superlative tier — strip these too (added 2026-05-28 after
Ribera).** Opus found 12 ranking clauses that QA1+QA2 missed because
the explicit strip-list above didn't enumerate the softer variants.
Same categorical rule applies; expand the strip pattern to ALSO match:
- `<country>'s most <adj>` (e.g. "Spain's most storied", "Italy's most celebrated")
- `the world's most <adj>` (e.g. "the world's most concentrated")
- `anywhere in the world`, `in the world`-tail boasts
- `one of the great <category>` (e.g. "one of the great wines of Burgos")
- `the legendary <entity>` (e.g. "the legendary Unico")
- `put <region> on the (world) map`
- `regarded as the defining`, `the defining <category>`, `the defining ... in the region`
- `the most prestigious <X>` (e.g. "the most prestigious postal code in Ribera")
- `one of the most {celebrated|prominent|important|iconic|defining|prestigious|storied} <X>`
- `synonymous with one of <country>'s great <X>`
Also: a first-name-only `chef|sommelier|owner|winemaker` attribution
("sommelier Roberto", "chef Marina") without a verifiable last name on
the producer/restaurant site is a fabrication risk — require a
last-name+source or strip the personal attribution. Mechanical backstop:
`scripts/check_score_claims.py` now also scans for these patterns and
surfaces them in ship_safety (WARN); use --strict to enforce.

**Comparative-ranking tier — strip these too (added 2026-05-30 after
Alsace).** Opus found 16 clauses that QA1+QA2 missed because the
soft-superlative strip-list focused on `"one of <region>'s most <adj>"`
and missed the ranking axis. Researchers default to assuming "the
largest" claims are factual scaffolding, but they require the same
source-verification as a critic score. Same categorical rule applies;
expand the strip pattern to ALSO match:
- `the (largest|leading|biggest|smallest|oldest|youngest|first|earliest|finest|highest|widest) <X> in <region/country/continent>` (e.g. "the largest Alsace cooperative", "the leading Bas-Rhin cooperative")
- `<region/country>'s (largest|oldest|finest|first|earliest) <X>` (e.g. "Alsace's largest cooperative")
- `(world|Europe|France|Germany|Italy|Spain)'?s (oldest|largest|biggest|first|finest) <X>` (e.g. "Europe's largest straw-bale cellar", "the world's oldest barrel-aged white wine")
- Ordinal ranks: `second-largest`, `third-largest`, `n-th largest` — these need a producer-site or trade-roster source OR get stripped to the absolute number ("400 hectares") instead of the relative rank
- Landholding ranks: `the largest landholder on <Grand Cru>` without consortium-roster source
- `one of the (largest|leading|biggest|oldest|earliest|first|finest) <X> in <region>` (the "one of" softener that exploits the strict-strip)

Concrete replacement: state the absolute number ("130 hectares", "1,200
hectares across 480 growers", "founded in 1902") instead of the relative
rank. Mechanical backstop: `scripts/check_score_claims.py` RE_SOFT_RANK
now catches all of the above patterns.

**C2 — NUMERIC verification on top scores (added 2026-05-22).**
For every score with `points >= 99`, you must verify the
`(reviewer, points, vintage, year)` tuple against a real, citeable
source. Liv-ex score-report digests, the publication's own archive
when accessible, or a retailer/merchant page that quotes the review
verbatim are all acceptable. The fingerprint that QA1/QA2 missed on
the Bordeaux pilot (Opus had to catch them): 100-point claims for
wines where the published score was actually 98, year mismatches
where the in-bottle review fell in a different year than the
en-primeur review, and points migrating between en-primeur and
in-bottle reviews of the same vintage. **Do not ship `points >= 99`
without source-verifying the tuple.** Lower scores are still subject
to C above (structural completeness); only 99+ gets the extra step.

**C3 — Split-estate disambiguation (added 2026-05-22).**
Bordeaux + Saint-Émilion have historically-divided estates whose
"sibling" properties share part of a name. A 100-point claim for one
sibling MUST NEVER flow into the other's record. Confirm at the
producer slug level:
- Pichon-Longueville Baron ≠ Pichon-Longueville Comtesse de Lalande
  (slugs: `chateau-pichon-baron`, `chateau-pichon-lalande`).
- Léoville Las-Cases ≠ Léoville Poyferré ≠ Léoville Barton
  (slugs: `chateau-leoville-las-cases`, `chateau-leoville-poyferre`,
  `chateau-leoville-barton`).
- Beauséjour Bécot ≠ Beauséjour Duffau-Lagarrosse
  (slugs: `chateau-beausejour-becot`, `chateau-beausejour-duffau`).
- Cos d'Estournel ≠ Cos Labory
  (slugs: `chateau-cos-destournel`, `chateau-cos-labory`).
For each sibling pair represented in vineyards.json or wines.json,
sample 1 score entry per sibling and confirm the score attaches to
the correct sibling (Liv-ex / Wine-Searcher / wineterminus.com are
helpful disambiguators since they keep the siblings on separate pages).

### D. Ownership currency

Wine estates change hands. A 2018 article saying "owned by the Smith
family" is stale if Constellation or LVMH bought them in 2022.

Sample EVERY vineyard that carries a named-individual or family `owner`
(and `winemaker`), NOT just the marquee estates. The dangerous defects
cluster on the small/non-famous producers, where the researcher had thin
sourcing and aggregators carry wrong names. For each, confirm against:
- Producer's current About page (mentions the current owner)
- A 2024-2026 press article OR consortium roster

Two defect classes to catch:

1. **Stale ownership** — a current name superseded by an acquisition:
   - Pre-Constellation ownership of Robert Mondavi
   - Pre-LVMH ownership of Domaine des Lambrays (acquired 2014)
   - Pre-Treasury ownership of Penfolds (TWE owns since 2011)

2. **Fabricated / cross-contaminated ownership** (Veneto 2026-05-26, Opus
   found 5 in one region after QA1+QA2 missed them): a name that the cited
   source does NOT support, OR a name lifted from a DIFFERENT producer —
   often a similarly-named or same-region estate (e.g. Bele Casel stamped
   with "Gregoletto family"; a DOCG name like "Malanotte" mistaken for a
   family; a wrong sibling like "Matteo Bisol" assigned to Ruggeri). For
   each named owner ask: does the producer's OWN site or a consortium
   roster name this exact person/family? If the only source is a
   wine-searcher / Vivino / retailer listing, or the name actually belongs
   to another estate, NULL the field (and scrub any copy of it that
   propagated into wines.json history milestones). Also flag any
   `owner`/`winemaker` whose value contradicts the entity's own
   `origin_year` / founding history.

### E. Biodynamic / organic certification status

Binary check. Either the certifier name appears on the producer's site
(Demeter / Ecocert / ICEA / USDA Organic / CCPB / SQNPI) or the entity
is "biodynamic_practicing" / "biodynamic_inspired", NOT certified.

Promoting "practicing" to "certified" is a deal-breaker. Run a sample
of 10 entities marked `biodynamic_status: demeter_certified` against
the Demeter International registry.

### F. Independent-directory address cross-check

10-15 random entities across topics. Open each on Google Maps OR
Wine-Searcher OR Vinous OR a regional consortium roster — confirm
venue exists at the claimed address. If sample hits >2 fabrications,
broaden to 30 — structural regression signal.

Also flag **vague `address_quoted`** (a recurring class found 2026-05-25
across Bordeaux/Burgundy/Tuscany): `address_quoted` must be a
street-level address that fuzzy-matches `entity.address`. A bare town,
appellation, or region name ("Cote de Beaune", "Florence, Tuscany",
"Val d'Orcia", "Vougeot", "Multiple estates, 33330 Saint-Emilion") is a
hard defect (verify_entities `addr_mismatch`). Fix the quote to the real
verbatim street address, or drop the entity if no street address is
verifiable. Also confirm `open_status` is exactly one of
{open, seasonal, unknown, permanently_closed}.

### G. Cross-link sanity (food-pairing topic + wines.pairings)

Every `food_pairing[*].tablejourney_url` must HEAD-resolve AND the
linked TJ entity/page must actually be in the matching TJ city. A
Bordeaux food-pairing pointing at a TJ Paris entity is a defect.

For the **wines topic** (`wines.json`), every non-null
`wines[*].pairings[*].tablejourney_ref` must:
- HEAD-resolve at `tablejourney.com/<ref>/`
- Be a path in the matching TJ city (Cork & Curve Tuscany cuvées
  cross-link to TJ Florence; pointing a Tuscan cuvée at TJ Tokyo is a
  defect).
If sample hits >2 broken TJ refs, broaden to 50% of cuvées — research
agent likely fabricated TJ paths.

### I. Cuvée taste-note sourcing (wines topic)

Every `wines[*].taste.aroma` and `wines[*].taste.palate` descriptor
must trace to a producer technical sheet OR a named critic note
(Decanter, Wine Advocate, Vinous, James Suckling, Jancis Robinson,
Decanter, Wine Spectator, World of Fine Wine).

The fingerprint of fabricated taste notes: every cuvée's aroma array
opens with the same 1-2 descriptors ("dark cherry, leather" repeated
30 times = template fill). Diversity of descriptors across the
catalog is a signal. Sample 10 cuvées with `editorial_score >= 4.5`
and confirm:
- `verified.cuisine_evidence_url` is a producer tech sheet OR critic
  page that actually contains the descriptors used. It must be the
  SPECIFIC per-cuvée page — a producer HOMEPAGE or a consortium/
  appellation DIRECTORY/listing page does NOT substantiate the
  descriptors and is a defect (Rioja 2026-05-25: 116/120 cuvées cited
  homepages/directories; QA2 had "repaired" them to producer homepages
  which still carried no per-wine notes — Opus caught it). When you find
  this, the fix is to locate the real per-wine page; only if none exists
  do you remove the taste block. Verify by actually opening 2-3 of the
  cited URLs and confirming the descriptor text is on the page.
- **If you remove a taste block because the cited URL is dead (4xx) or
  doesn't substantiate, ALSO reassign `verified.source_url` away from
  that dead URL to a confirmed-200 substitute (the producer's verified
  per-wine page on a different path, the appellation's consortium page,
  or the producer site root). Do NOT leave a 404 URL in `source_url`
  after stripping the taste — that ships a broken citation (Rhône
  2026-05-28: QA2 stripped 37 taste blocks for dead `vins-rhone.com/en/
  cuvee/<slug>` URLs but left the 404 source_url; Opus had to swap them
  to the real appellation pages).**
- The descriptors aren't all generic mass-market vocabulary ("notes
  of red fruit" with no specificity).

Remove unsourceable taste blocks rather than ship invented sensory copy.

### J. Tag vocabulary conformance (wines topic)

Every tag in `wines[*].tags` must appear in
[docs/WINE_TAGS.md](../../docs/WINE_TAGS.md). Generators reject unknown
tags and the build fails, so this check is the last line of defence
before generation breaks the build.

Also: the researcher must NOT emit tags from the DERIVED axes (price,
ageing, production, grape, world, sweetness). The generator computes
those from `price_band`, `drinking_window_years`, producer fields,
`varietals`, country, `sweetness`. If `wines[*].tags` contains entries
like `price-luxury` or `pinot-noir`, that's a regression: strip them.

### K. Vintage-agnostic discipline (wines topic)

Cuvée slugs MUST be vintage-agnostic. Reject any `wines[*].slug` that
contains a 4-digit year (e.g. `tignanello-2019`). Vintage information
belongs in `scores[*]` (with reviewer + points + year of review) and
in prose, NEVER in the URL.

Also reject any cuvée whose `name` is "Tignanello 2019" rather than
"Tignanello" — the page is meant to summarise the cuvée across
vintages.

### L. Cuvée → producer cross-reference

Every `wines[*].producer` MUST resolve to a `vineyards[*].slug` in
the same region's `vineyards.json`. Mechanically checked at ship_safety
gate but worth eyeballing during QA — when an agent invents a cuvée,
the producer is often a real-sounding-but-fictional name.

Also: every `signature_wines[*].slug` must appear in `wines[*].slug`.
Curated subset, not parallel data.

### H. Voice + prose defects

Same as TJ:
- No em-dashes / en-dashes anywhere
- No AI-tells ("nestled in", "vibrant atmosphere", "culinary journey",
  "carefully crafted", "must-visit", "to die for")
- No score-bunching (coefficient of variation < 0.04 = suspicious)
- No description "clones" within the SAME topic (across topics is
  expected — same vineyard in both `vineyards` and `dietary` is normal)

## Workflow

1. Open the city's data dir + read every JSON.
2. Run the 8 checks above in order.
3. Write findings to
   `agents/qa/reports/<country>_<region>_qa1_<YYYY-MM-DD>.md` with a
   defect list (entity slug + class).
4. Remove flagged entities directly from the JSONs. When a defect is a
   FIELD value (e.g. a wrong `organic_status`, `owner`, or classification),
   scrub it in EVERY file that carries that field for the same entity, not
   just the topic where you first spotted it — the same producer appears in
   vineyards.json, dietary.json, hidden-gems.json, signature-wines.json, etc.
   (Piedmont 2026-05-25: a blanket-`icea` fix that touched only dietary.json
   left the same fabrication live in vineyards.json + hidden-gems.json.)
5. Re-run `bash scripts/ship_safety.sh <country> <region>` to confirm
   structural integrity after your removals.
6. Print QA1-COMPLETE <country>/<region>.

One continuous run, no escape hatches.

## What QA2 + Opus pick up after you

QA2: tour-route fabrication on real operators, festival prose echoes,
thin-category fabrication, chef/winemaker name URL-slug mining.

Opus final: narrow read; should find nothing. Sample 30 entities,
confirm one itinerary + one festival end-to-end, spot-check 5 entries
with `editorial_score >= 4.7` for backing credentials.
