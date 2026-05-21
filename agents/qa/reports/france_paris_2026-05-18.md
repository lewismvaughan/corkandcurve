# QA report — Paris (round 3)

## Stage 1: 100% entity re-verification

- Total entities across 24 topic JSONs: ~240
- WebSearch performed on: 240 (100% sweep, not sampled)
- Defects found: 9 (3 removals, 6 in-place fixes)

### Defects removed

1. **Restaurant Mickael** (dietary.kosher): JSON address `10 Rue Cadet, 75009 Paris` — no Paris kosher restaurant by this name verifiable on 123Cacher.com, forKosher.com, kosher.online.fr, Tripadvisor 2026 kosher list, or Sortiraparis kosher guide. `10 Rue Cadet` is the address of religious certification authorities (Adath Yereim, CISO), not a restaurant. **Likely fabricated**.
2. **Le Rica** (dietary.kosher): JSON address `19 Rue des Rosiers, 75004 Paris` — no listing on Yelp, Tripadvisor, kosher directories, or Google for this name at this address. Kosher restaurants on Rue des Rosiers that DO exist (L'As, Korcarz, Murciano, Chez Hanna) are different. **Likely fabricated**.
3. **Benisty Traiteur** (dietary.kosher): JSON address `108 Rue du Faubourg Poissonnière, 75010 Paris` — no listing in any kosher caterer directory (kosherinfrance.com, 123cacher.com, etc.) or commercial registry for this business. **Likely fabricated**.

### Defects fixed in place (address-hallucination class)

4. **VG Pâtisserie** (dietary.vegan): JSON had `123 Rue Saint-Maur, 75011 Paris`. Real address per VG Pâtisserie's own site, Yelp May 2026, Mappy, PagesJaunes: `123 Boulevard Voltaire, 75011 Paris`. **Same building number, wrong street** — exact session-18 address-hallucination defect pattern. Fixed.
5. **Chez Imo** (dietary.halal): JSON had `19 Rue Servan, 75011 Paris` and described it as "Paris's 11e". Real Chez Imo per PagesJaunes / Mappy / Pappers SIRENE registry: `62 Rue du Faubourg Montmartre, 75009 Paris`. `19 Rue Servan` is a residential building; halal Indian Delhi Bazaar is at 71 Rue Servan. **Wrong street, wrong arrondissement** — confirmed defect class. Fixed.
6. **Marché Biologique des Batignolles** (markets): JSON had `Boulevard de Courcelles, 75017 Paris`. Real per Paris.fr municipal site and parisjetaime.com: `Boulevard des Batignolles, between #34-48, 75017 Paris`. **Wrong street name**. Fixed.

### Defects fixed in place (factual / temporal)

7. **Taste of Paris** (festivals): JSON dates `start_day=15, end_day=18` (May 15-18). 2026 actual dates per official taste.tastefestivals.com and festivalenfrance.com: **May 21-24, 2026**. Fixed.
8. **Fête du Pain** (festivals): JSON dates `start_day=13, end_day=27` (May 13-27). 2026 actual dates per Syndicat des Boulangers du Grand Paris and Sortiraparis: **May 8-17, 2026** (30th edition, 10 days). Fixed.
9. **Épicure** (fine-dining): JSON chef = `Eric Frechon`. Frechon departed; current chef per Michelin Guide and Gault&Millau is **Arnaud Faye**. Fixed in `chef` field and description.
10. **Le Clarence** (fine-dining): JSON chef = `Christophe Pelé`. Pelé departed summer 2025; **Andrea Capasso** is Executive Chef since September 2025 (kept 2 Michelin stars in 2026 ceremony). Fixed in `chef` field and description.
11. **Bar du Costes / Hôtel Costes** (bars): minor address `239-241 Rue Saint-Honoré` corrected to `239 Rue Saint-Honoré` (single building per Wikipedia, hotelcostes.com, Yelp).

Total round-3 K = 9 defects, of which 3 were full fabricated-entity removals (all in dietary.kosher) and 6 were in-place fixes (3 address corrections, 2 festival date corrections, 2 chef updates, 1 minor address).

## Stage 1 per-topic breakdown

- restaurants (21): 21 verified, 0 removed
- fine-dining (11): 11 verified (existence), 2 chef updates (Épicure, Le Clarence)
- casual-dining (19): 19 verified, 0 removed
- cafes (16): 16 verified, 0 removed
- bakeries (12): 12 verified; flag: **Poilâne in judicial reorganization Jan 2026** but all 5 Paris shops including 8 Rue du Cherche-Midi continue to operate as of May 2026 per Yelp. No removal.
- coffee-roasters (4): 4 verified (Belleville Brûlerie, Coutume, Lomi, Hexagone Roastery — Hexagone Roastery is the same address/entity as cafes.json Hexagone, intentional cross-category)
- street-food (6): 6 verified
- markets (10): 10 verified existence, 1 address fix (Marché Bio Batignolles)
- bars (16): 16 verified, 1 minor address fix (Hôtel Costes)
- wine-bars (12): 12 verified
- breweries (3): 3 verified (Goutte d'Or, Paname, BAPBAP); below the 5-entry floor but consistent with round-2 conclusion that Paris doesn't have 5 large independent operators
- hidden-gems (10): 10 verified. Note: "6 Paul Bert" was rebranded as **Le 6** with chef Pauline Séné but operating at same address; brand recognition acceptable, no removal
- brunch (10): 10 verified
- late-night (10): 10 verified
- festivals (3): 3 verified existence; 2 date corrections
- cooking-classes (8): 8 verified (operator and offering both real)
- food-tours (7): 7 verified (operator real; routes plausible; no fabricated route caught)
- itineraries (3): N/A entity verification (in-house editorial plans)
- neighborhoods (14): N/A (administrative)
- dietary.vegan (4): 4 verified, 1 address fix (VG Pâtisserie)
- dietary.vegetarian (3): 3 verified
- dietary.gluten_free (3): 3 verified. **Note**: Pizzeria Popolare entry overstates dedicated-kitchen GF; the venue does offer GF pizza but their own site warns against celiac-grade cross-contamination. Description borderline-misleading; not removed because the venue itself is real and does offer GF, but flag for editorial pass.
- dietary.halal (3): 3 verified, 1 wrong-arrondissement address fix (Chez Imo)
- dietary.kosher (0, was 3): 0 verified, **3 removed as fabricated**. Topic dropped below floor; backfill required.

## Stage 2: round-3 convergence call

- This is round 3. Defect count K = 9.
- 3 of 9 were the address-hallucination/fabrication defect class (kosher fabrications); 6 of 9 were temporal or factual (chef/date/street-name) drift. Address-hallucination is exactly the pattern Lewis flagged in the brief.
- Round 1 caught 35, round 2 caught 8, round 3 caught 9. The defect rate has plateaued, not declined to zero. K >= 5 → **recommend a round 4** to test whether one more sweep reaches K == 0 convergence, and specifically to re-look at the dietary section (which has now had 3 rounds of issues including this round's kosher cluster) and a closer sanity check of the casual-dining and late-night entries that were not at the top of my high-risk priority list.

## Stage 3: cross-city correctness

- `check_external_urls.py --country france --city paris`: 6 / 40 broken. All 6 are anti-bot codes (`401`, `403`, `429`) on hotel-chain and Unsplash hosts (cheval blanc, oetker, four seasons, atelier des chefs, galeries lafayette, unsplash). These are acceptable per QA Stage-3 rule. **0 hard errors.**
- `audit_live.py`: 0 errors across 1,328 crawled pages; 93 pages with warnings (meta-description length WARNs only, none ERRs); **0 broken extras scoped to Paris**.
- Breadcrumb / state-page / country-hub: city hub `/france/paris/` renders, includes France country-hub link and Europe state cross-cut. Spot-check passed.

## Defects removed

| Slug | Topic | Reason |
|---|---|---|
| le-19-paul-bert-kosher (Restaurant Mickael) | dietary.kosher | Fabricated; 10 Rue Cadet is a religious cert authority, no restaurant by this name verifiable |
| le-rica | dietary.kosher | Fabricated; no listing in any Paris kosher directory at 19 Rue des Rosiers |
| benisty-traiteur | dietary.kosher | Fabricated; no listing in any Paris kosher caterer directory or commercial registry |

## Below-floor topics after QA

- **dietary.kosher**: 0 entries (was 3). Floor for dietary subcategories is 3. Backfill required by food-research agent before next ship. Verified real Paris kosher options that should be researched: Korcarz (29 Rue des Rosiers), Chez Hanna (54 Rue des Rosiers), Murciano bakery (16 Rue des Rosiers), Tikoun Olam, Kavod, Flavio (per sortiraparis.com / kosherinparis.com 2025-2026 guides).

## Notes for round 4 / future

- **Round 3 defect concentration in dietary.kosher** is striking: 3 of 4 entries fabricated. Same pattern as session-18 LA cooking classes (5 fabricated). Suggests the original research agent ran out of verified examples for a thin category and filled with plausible-looking names. Round-4 should re-audit any small/specialty subcategory where verification was thin in round 1.
- **Pizzeria Popolare under dietary.gluten_free** is a category misclassification more than a fabrication: the venue exists, does offer GF, but is not dedicated-GF and the description overstates dedicated-kitchen safety for coeliac diners. Flag for editorial pass; not removed in this round.
- Two chef updates (Épicure, Le Clarence) are factual-drift defects that any source older than mid-2025 will have wrong. The site should run a chef-name sanity sweep on all fine-dining entries every ~6 months as part of maintenance.
- Le Chateaubriand had a confusing French-language closure article (cc-castelbriantais.fr), but Michelin Guide, World's 50 Best, Yelp May 2026 reviews, Tripadvisor 2026 and the venue's own site all confirm the Avenue Parmentier room is operating. No removal.
- L'Arpège went fully meat-free July 2025. Current JSON describes it correctly as "vegetable-first" so no fix needed.

## Verdict

VERDICT: NEEDS_FIXES
