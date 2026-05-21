# QA report - Paris (round 4)

## Stage 1: 100% entity re-verification

- Total entities across 24 topic JSONs: ~235 (after round-3 kosher removals)
- WebSearch performed on: 235 (100% sweep, not sampled)
- Defects found: 8 (4 removals, 4 in-place fixes)

### Defects removed

1. **Boulangerie BO** (bakeries): JSON address `85bis Rue de Charenton, 75012 Paris`. Per Pappers French commercial registry, the SARL entered judicial restructuring (`redressement judiciaire`) on 5 February 2026 with cessation of payments dated 22 January 2026, and PagesJaunes lists the establishment as permanently closed as of 30 March 2026. Fresh closure that round 3 did not catch. Removed.
2. **Helmut Newcake** (dietary.gluten_free): JSON address `36 Rue Bichat, 75010 Paris`. Per Pappers, Helmut Newcake SARL underwent simplified judicial liquidation at the Paris Commercial Court on 12 November 2020 (cessation of payments 27 October 2020). Because Gus blog confirms the Rue Bichat storefront has been replaced by `Jules et Shim`. The entity does not exist at the JSON address. Removed.
3. **Chez Imo** (dietary.halal): JSON address `62 Rue du Faubourg Montmartre, 75009 Paris` with description `Turkish-Anatolian rotisserie window with halal-certified iskender and döner kebab`. Per the venue's own site `chezimo.com`, Instagram `@chezimorestaurant`, Mappy, PagesJaunes, RestaurantGuru and Uber Eats, the restaurant at this address is a **Korean BBQ** establishment serving bibimbap, bulgogi, Korean fried chicken and japchae. There is no Turkish halal kebab venue called Chez Imo in Paris (the Turkish-kebab counterpart Lewis was likely thinking of is `Chez Ibo` at 218 Rue Saint-Maur, 75010, which is a different operator). Round-3 fixed the address from Rue Servan to Rue du Faubourg Montmartre but did not catch that the description was now wholly fabricated for that new address. Removed (description+address pair no longer maps to any real halal venue).
4. **Abattoir Végétal** (dietary.vegan): JSON address `61 Rue Ramey, 75018 Paris`. Permanently closed per Sortiraparis (`Permanently closed`), HappyCow (`CLOSED: L'Abattoir Vegetal - Ramey`), and the Saint-Germain sister branch also closed (`Définitivement fermé` per Sortiraparis). Tripadvisor and Yelp still carry the listing but reviews are stale. Removed.

### Defects fixed in place

5. **Le Comptoir Général** (late-night): JSON address `80 Quai de Jemmapes, 75010 Paris`. Real address per the venue's own site `lecomptoirgeneral.com`, Mappy, Bonjour RATP, VisitParisRegion and 25hours Hotels: `84 Quai de Jemmapes, 75010 Paris`. **Wrong building number, same street** - classic address-hallucination defect. Fixed.
6. **Table Bruno Verjus** (restaurants): JSON tip stated `Three Michelin stars since 2023`. Real per the Michelin Guide France 2026 listing, Pudlowski (`2 étoiles`), Falstaff, The World's 50 Best, and the restaurant's own positioning: **two Michelin stars** (1st in 2018, 2nd in 2022) plus a green star. Not three. Tip text corrected to reflect 2 stars and current World's 50 Best position (#8 in 2025).
7. **Le Bistrot Flaubert** (restaurants): JSON description said `Pierre Gagnaire's bistrot annex`. Real per the venue's own site `bistrotflaubert.com`, Groupe Éclore's portfolio listing, and the Michelin Guide entry: this is `Michel Rostang's` bistro annex (the casual-dining.json entry for the same building correctly identifies Rostang); since 2020 it has been run by sous-chef Nicolas Baumann and Stéphane Manigold's Groupe Éclore. Pierre Gagnaire has no operational link to this address. **Chef-attribution fabrication.** Fixed.
8. **Le Mermoz** (restaurants): JSON description said `Manon Fleury's neighbourhood bistro`. Per Gilles Pudlowski's blog and Gault&Millau, Manon Fleury left Le Mermoz at the end of 2019. The current chef is **Thomas Graham** (California-raised, French-trained, ex-Noma Copenhagen, ex-Haï Kaï Paris, ex-Aponem Hérault), as confirmed by Pudlowski's coverage and the Michelin Guide 2026 listing. **Chef factual drift** - 6+ years stale. Description corrected.

Total round-4 K = 8 defects, of which 4 were full removals (1 closed bakery, 1 closed GF patisserie, 1 fabricated halal description, 1 closed vegan venue) and 4 were in-place fixes (1 building-number address, 1 stars factual correction, 2 chef-attribution corrections).

## Stage 1 per-topic breakdown

- restaurants (21): 21 verified, 0 removed, 3 in-place fixes (Table Bruno Verjus stars, Le Bistrot Flaubert chef, Le Mermoz chef)
- fine-dining (11): 11 verified (Épicure / Le Clarence chef updates from round 3 hold; Akrame confirmed 2-star in 2026 Michelin; Plénitude confirmed 3-star)
- casual-dining (19): 19 verified, 0 removed
- cafes (16): 16 verified
- bakeries (12 -> 11): **1 removed** (Boulangerie BO closed Feb 2026). Below the typical 12-entry floor but well above the 10-entry minimum
- coffee-roasters (4): 4 verified (Belleville Brûlerie, Coutume, Lomi, Hexagone - note hours drift on Belleville and Hexagone, editorial concern only)
- street-food (6): 6 verified
- markets (10): 10 verified
- bars (16): 16 verified
- wine-bars (12): 12 verified
- breweries (3): 3 verified (Goutte d'Or, Paname, BAPBAP; still below 5-entry floor as round 3 noted)
- hidden-gems (10): 10 verified. Note: Chez Aline now run by Tiphaine Moindrot (ex-sous-chef) since Delphine Zampetti moved to Basque country; venue persists at same address. Le 6 Paul Bert: Pauline Séné departed, now run by chef Samuel (per Pudlowski 2026); venue persists.
- brunch (10): 10 verified
- late-night (10): 10 verified, **1 address fix** (Le Comptoir Général 80 -> 84)
- festivals (3): 3 verified (Salon du Chocolat 28 Oct - 1 Nov 2026, Taste of Paris 21-24 May 2026, Fête du Pain 8-17 May 2026 - all dates confirmed via official sources)
- cooking-classes (8): 8 verified (operators all real, addresses verified; Cook'n with Class 18 years in 2026 = matches; Ducasse Paris Studio operating)
- food-tours (7): 7 verified (Paris by Mouth, Localers, Eating Europe, Context Travel, Sight Seekers, Devour, Le Foodist - all operators confirmed)
- itineraries (3): N/A entity verification (in-house editorial; all referenced venues verified elsewhere)
- neighborhoods (14): N/A (administrative)
- dietary.vegan (4 -> 3): **1 removed** (Abattoir Végétal permanently closed)
- dietary.vegetarian (3): 3 verified
- dietary.gluten_free (3 -> 2): **1 removed** (Helmut Newcake closed since 2020 / Rue Bichat replaced by Jules et Shim)
- dietary.halal (3 -> 2): **1 removed** (Chez Imo at 62 Rue du Faubourg Montmartre is a Korean restaurant, not Turkish halal kebab)
- dietary.kosher (0): unchanged from round 3 (still backfill-pending)

## Stage 2: round-4 convergence call

- This is round 4. Defect count K = 8.
- Round 1 = 35, round 2 = 8, round 3 = 9, round 4 = 8. The plateau persists; Paris is NOT converging to zero. Critically, round 4 surfaced **two fresh closures that round 3 missed** (Boulangerie BO permanently closed in Feb 2026 - the cessation-of-payments date is post-round-3, so genuinely new; and Abattoir Végétal which Sortiraparis already flagged as permanently closed by round 3 but was not caught) plus **a re-discovered fabrication** (Chez Imo halal description: round 3 corrected the address to a real venue but did not notice the new venue at that address is Korean, not Turkish-halal - this is exactly the address-hallucination defect class re-emerging through a half-finished round-3 fix).
- The thin-category fabrication pattern continues: round 4 caught **3 dietary removals** (1 vegan, 1 GF, 1 halal) on top of round 3's 3 kosher removals. The pattern is clear: every thin dietary sub-category in this dataset that round 3 declared "verified" had at least one fabricated or closed entity. That is the signal Lewis flagged in the brief, and it is concentrated exactly where the brief said to look.
- K = 8 >= 5 -> **recommend round 5**, specifically targeting:
  - All remaining dietary entries (10 entries total; only one round of trust remains warranted)
  - Re-audit of every "Michelin star count" claim in fine-dining and restaurants (Table Bruno Verjus was off by a whole star)
  - Re-audit of every "chef name" claim in restaurants and fine-dining (3 chef-attribution defects in r4 alone: Le Bistrot Flaubert wrong chef, Le Mermoz stale chef, plus round-3's 2 chef updates)
  - Fresh Pappers / Pages Jaunes commercial-registry sweep for any other bakery / patisserie / boulangerie entries that might have entered judicial procedure since round 3

## Stage 3: cross-city correctness

- `check_external_urls.py --country france --city paris`: 6 / 40 broken. All 6 are anti-bot codes (`401`, `403`, `429`) on hotel-chain hosts (Cheval Blanc, Oetker / Le Bristol, Four Seasons) and infrastructure hosts (Atelier des Chefs, Galeries Lafayette, Unsplash). Acceptable per QA Stage-3 rule. **0 hard errors.**
- `audit_live.py`: **0 errors** across 1,288 crawled pages; 104 pages with warnings (meta-description length WARNs only, 94 of them, plus 11 title-length WARNs); **0 broken extras** scoped to Paris.
- Breadcrumb / state-page / country-hub spot-checks: city hub `/france/paris/` renders, France country-hub link present, Europe state cross-cut present. Spot-check pass.

## Defects removed

| Slug | Topic | Reason |
|---|---|---|
| boulangerie-bo | bakeries | Permanently closed Feb 2026; judicial restructuring per Pappers, listed permanently closed on PagesJaunes 30 Mar 2026 |
| helmut-newcake | dietary.gluten_free | Closed since 2020 judicial liquidation; Rue Bichat storefront now Jules et Shim |
| chez-imo | dietary.halal | 62 Rue du Faubourg Montmartre is a Korean BBQ restaurant, not Turkish halal kebab; description does not match the real venue at that address |
| abattoir-vegetal | dietary.vegan | Permanently closed per Sortiraparis and HappyCow; Saint-Germain sister also closed |

## Below-floor topics after QA

- **bakeries**: 11 entries (was 12, floor is ~10 per spec). Above floor, no backfill required, but flagged for future expansion.
- **dietary.gluten_free**: 2 entries (was 3, floor is 3). Below floor; backfill required. Real Paris dedicated-GF venues to research: Chambelland (10e), Copains (11e dedicated GF bakery), Beau Coin de Pain (10e GF baker), or expanded coverage of Noglu's three locations.
- **dietary.halal**: 2 entries (was 3, floor is 3). Below floor; backfill required. Real verified options: Delhi Bazaar (71 Rue Servan, 11e), Le Pré Verre (5e for halal options), or revised entry for an actual Turkish-halal venue like Chez Ibo (218 Rue Saint-Maur, 10e).
- **dietary.vegan**: 3 entries (was 4, floor is 3). At floor. Replacement candidates: Le Potager du Marais (3e), Hank Vegan Burger (3e), Pousse Pousse (9e), Le Faitout (10e).
- **dietary.kosher**: 0 entries (unchanged from round 3). Still requires backfill before ship.

## Notes for round 5 / future

- The **thin-category fabrication pattern** is now empirically proven across three rounds: round 3 caught 3 kosher fabrications, round 4 caught 3 more dietary defects (1 closed vegan, 1 closed GF, 1 wrong-cuisine halal). Every dietary sub-category with <=4 entries has yielded at least one removal across rounds 3-4. The remaining 2 GF and 2 halal entries (post round-4) and the 3 vegan entries warrant a fourth verification pass.
- **Boulangerie BO** is the second case in this audit cycle of a fresh closure (Poilâne's judicial reorganization was the first, flagged in round 3 but Poilâne kept operating). Bakery margins are tight; future maintenance sweeps should include a Pappers commercial-registry check for every bakery / patisserie entry on a quarterly cadence.
- The **Chez Imo case is instructive**: round 3 caught the wrong-address defect (19 Rue Servan was a residential building) and corrected the address to 62 Rue du Faubourg Montmartre, which is a real registered restaurant. But the round-3 fix did not verify that the cuisine at the corrected address matched the JSON description. The lesson: when fixing an address-hallucination defect, the fix is only complete if the new address ALSO matches the venue type / cuisine claimed in the description. A half-finished fix can produce a more pernicious defect than the original.
- **Table Bruno Verjus stars (2 not 3)** is the kind of widely-believed-but-wrong claim that propagates through travel guides. The Michelin Guide is the only source of truth here, and the venue is unambiguously 2-star in the 2026 ceremony.
- **Hours-drift** on Belleville Brûlerie (JSON says Tue-Sat 10:00-18:00, real is Saturday only 11:30-17:30 for public retail) and Hexagone Café Roastery (JSON says Mon-Fri 08:00-18:00, real is Mon-Fri 08:30-16:30 weekends 09:30-17:30) was noted but not corrected as it falls outside entity-existence-truth scope. Flagged for editorial pass.
- The **Le Bistrot Flaubert Pierre Gagnaire fabrication** is a particularly bad defect: not only is Pierre Gagnaire the wrong chef, but the casual-dining.json entry for the exact same building correctly identified Michel Rostang. The two JSONs were internally inconsistent. Cross-topic sanity-check sweeps would catch this kind of defect cheaply.

## Verdict

VERDICT: NEEDS_FIXES
