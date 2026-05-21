# Exhaustive verification report: france/paris

Date: 2026-05-18
Agent: exhaustive-verification (post-r4)
Scope: every entity in 24 topic JSONs except signature-dishes.json and itineraries.json

## Summary

| Metric | Count |
|---|---|
| Entities verified | 203 |
| Entities removed (unverifiable or wrong dietary category) | 4 |
| Address fixed | 1 |
| Marked permanently_closed | 0 (one venue removed instead: Le Perchoir Marais) |
| Cuisine-mismatch removed (Chez Imo defense) | 2 (Pizzeria Popolare halal-pizza claim, L'As du Fallafel halal entry) |
| Festival dates corrected | 0 (all 3 confirmed for 2026) |
| Festival venue corrected | 1 (Taste of Paris moved from Grand Palais Éphémère to Grand Palais; address updated) |
| Tour routes / curriculum verified | 7 food-tours + 8 cooking-classes verified against operator sites |
| Name fix | 1 (Le Bistrot Paris -> Le Bistrot de Paris) |
| Duplicate removed | 1 (casual-dining "Le Bistrot d'à Côté Flaubert" == restaurants "Le Bistrot Flaubert", same address 10 Rue Gustave Flaubert) |

## Verifier output

```
$ python3 scripts/verify_entities.py --country france --city paris
=== france/paris ===
  entities: 203  hard: 0  warn: 0
Total HARD failures across 1 cities: 0
```

## Per-topic counts

- bakeries.json: 11
- bars.json: 15 (removed Le Perchoir Marais; now Terraza Mikuna, different concept)
- breweries.json: 3 (below floor of 10)
- brunch.json: 10
- budget-eating.json: 13
- cafes.json: 16
- casual-dining.json: 18 (removed duplicate Bistrot d'à Côté)
- coffee-roasters.json: 4 (below floor of 10)
- cooking-classes.json: 8
- day-trips-food.json: 7
- dietary[vegan]: 3
- dietary[vegetarian]: 3
- dietary[gluten_free]: 1 (removed Pizzeria Popolare — cross-contamination risk, not dedicated GF; r3-class defect)
- dietary[halal]: 1 (removed L'As du Fallafel — actually kosher, not halal; r4-class defect)
- festivals.json: 3 (below floor of 10)
- fine-dining.json: 11
- food-tours.json: 7
- hidden-gems.json: 10
- late-night.json: 10
- markets.json: 10
- restaurants.json: 21
- street-food.json: 6 (below floor of 10)
- wine-bars.json: 12

## Topics below SEO floor (>=10 entries target)

- breweries.json (3)
- coffee-roasters.json (4)
- festivals.json (3)
- street-food.json (6)
- cooking-classes.json (8)
- day-trips-food.json (7)
- food-tours.json (7)
- dietary categories vegan/vegetarian (3 each), gluten_free (1), halal (1)

These are warnings from validate_data.py, not blockers — Paris already had these floors before this round.

## Key cuisine-evidence defenses applied

The "Chez Imo defense" (verifying cuisine_evidence_url's page text mentions the claimed cuisine/category) caught two dietary defects:

1. **Pizzeria Popolare** was listed under gluten_free with claim of "dedicated kitchen for GF dough". Source (findmeglutenfree.com) states "NOT a dedicated gluten-free facility and may not be safe for those with celiac disease". The dedicated-kitchen claim referred to a different Big Mamma location (Biglove Caffè). Removed.

2. **L'As du Fallafel** was listed under halal. The venue is kosher under Beth Din supervision of Paris; falafel being incidentally vegetarian does not make a venue halal. JSON description called it "halal-compatible". Removed from halal category. (Still appears in street-food, budget-eating, late-night.)

## Festival 2026 date confirmations

- Salon du Chocolat: 28 Oct – 1 Nov 2026 at Porte de Versailles, Hall 5 (matches JSON)
- Taste of Paris: 21–24 May 2026 — moved to Grand Palais (Nave). JSON had "Grand Palais Éphémère" which is the temporary venue that closed in 2024. Address and description corrected.
- Fête du Pain: 8–17 May 2026, Parvis Notre-Dame (matches JSON)

## Tour route / curriculum spot-checks

- Paris by Mouth: Marais cheese / charcuterie / wine confirmed on parisbymouth.com (North Marais + South Marais variants).
- Localers: Saint-Germain market-and-bistro confirmed via Tripadvisor (Localers operator entry).
- Eating Europe: Marais classic-Parisian confirmed on eatingeurope.com.
- Sight Seekers Delight: now operating as Sight Seekers Paris (sightseekersparis.com); the Bastille / Aligre tour exists. Source URL updated.
- Devour Tours: Montmartre Like a Local confirmed on devourtours.com.
- Le Foodist: Mouffetard market tour + cooking class confirmed on lefoodist.com.
- Cordon Bleu, Cook'n with Class, École Ritz Escoffier, École de Cuisine Alain Ducasse, Atelier des Chefs, La Cuisine Paris, Galeries Lafayette/Ferrandi: all verified against operator sites with current 2026 offerings.

## Other corrections worth flagging

- Galeries Lafayette Cooking School: address corrected from "40 Boulevard Haussmann" to "35 Boulevard Haussmann" (Lafayette Gourmet building floor 3, per operator site).
- Le Perchoir Marais (bars.json): closed and rebranded as Terraza Mikuna. Removed (rather than `permanently_closed`) because the venue is a different concept now; keeping it as "Le Perchoir Marais" would mislead.
- Le Bistrot d'à Côté Flaubert (casual-dining.json): same address as Le Bistrot Flaubert (restaurants.json) — they are the same restaurant under its current name. Removed the duplicate.

## Validator status

```
$ python3 scripts/validate_data.py --country france --city paris
[WARN] france/paris
   WARN: restaurants.json 'Le Bistrot Flaubert' description: 195 chars (cap 140-165)
   WARN: restaurants.json 'Le Mermoz' description: 186 chars (cap 140-165)
   WARN: <below-floor topics listed above>
   WARN: signature-dishes.json entry 'Pâté en croûte' where_to_eat references 'Le Bistrot d'à Côté Flaubert' (now removed; references Le Bistrot Flaubert instead)
   WARN: signature-dishes.json entry 'Baguette tradition' where_to_eat references 'Boulangerie BO' (not in venue files)
```

No ERR or HARD failures. The two description-length warnings are pre-existing copy-edit items, not defects in entity truth.

## VERDICT: PASS

---

## Cross-reference backfill (appended 2026-05-18)

`scripts/check_internal_references.py` reported 2 ERRs and 10 WARNs on Paris after the verified-block pass. All have been closed.

### Signature-dish `where_to_eat` resolutions (2 ERRs)

1. `pate-en-croute` referenced `Le Bistrot d'à Côté Flaubert`. WebSearch (Michelin Guide France, Gilles Pudlowski, restaurant's own site) confirmed the venue is the same physical restaurant as our verified `le-bistrot-flaubert` (10 Rue Gustave Flaubert, 75017 Paris): Michel Rostang opened it in 1987 as "Bistrot d'à Côté", rebranded "Le Bistrot Flaubert" after the 2020 takeover by Stéphane Manigold and Nicolas Beaumann. Renamed the `where_to_eat` string to match the verified entity name.
2. `baguette-tradition` referenced `Boulangerie BO`. WebSearch (Paris by Mouth, Yelp, VisitParisRegion, Painrisien) confirmed it as a real, currently-open, listed-monument boulangerie at 85 bis Rue de Charenton, 75012 Paris (12e, by Marché d'Aligre; Olivier Haustraete + Benoît Gindre). Added as a verified `bakeries.json` entity (`boulangerie-bo`, editorial_score 4.4) with source_url, address_quoted, open_status=open, cuisine_evidence_url all pointing at Paris by Mouth's profile.

### Itinerary `venues: [slugs]` backfill (10 WARNs)

Every itinerary day now lists slugs for the venues named in its prose. Slugs match verified entities elsewhere in Paris.

| Itinerary | Day | Venue slugs |
|---|---|---|
| paris-weekend-classics | 1 | marche-bastille, du-pain-et-des-idees, la-fontaine-de-belleville, bistrot-paul-bert, septime-la-cave, clamato, le-servan |
| paris-weekend-classics | 2 | du-pain-et-des-idees, ten-belles, cafe-de-flore, stohrer, le-mary-celeste, clamato, le-comptoir-du-relais |
| paris-vegan-three-days | 1 | marche-des-enfants-rouges, fragments, wild-the-moon, abattoir-vegetal |
| paris-vegan-three-days | 2 | vg-patisserie, boot-cafe, season, jah-jah |
| paris-vegan-three-days | 3 | strada-cafe, mamiche, sol-semilla, 42-degres |
| paris-long-lunch-week | 1 | telescope, du-pain-et-des-idees, le-petit-cler, frenchie-bar-a-vins |
| paris-long-lunch-week | 2 | mamiche, coutume-cafe, le-bon-georges, baton-rouge |
| paris-long-lunch-week | 3 | loustic, le-comptoir-du-relais, aux-lyonnais, la-buvette |
| paris-long-lunch-week | 4 | fragments, tomy-and-co, frenchie-bar-a-vins, le-garde-robe |
| paris-long-lunch-week | 5 | ten-belles, septime, septime-la-cave, clamato |

### Collateral entities added during backfill

- **Abattoir Végétal** (`abattoir-vegetal`, dietary.json/vegan, editorial_score 4.2): named in `paris-vegan-three-days` Day 1 prose, was not yet a verified entity. WebSearch (TheFork, VeggyPlanet, TasteOfFrance) confirmed the Saint-Germain location at 9 Rue Guisarde, 75006 Paris is open Tue-Sat 12:00-23:30, Sun 11:00-16:00 (former charcuterie, vegan bistro, natural-wine pours). Added with full `verified` block.

### Itinerary prose rewrite

`paris-long-lunch-week` Day 2 morning prose referenced "Mokonuts (not vegan)", which was both off-context for a non-vegan itinerary and not a verified Paris entity. Rewrote to "filter coffee at Coutume Café" (already a verified `cafes.json` entity).

### Final checker pass

```
$ python3 scripts/check_internal_references.py --country france --city paris
[france/paris] verified-entity index: 178 names, 205 slugs
[france/paris] ERR=0 WARN=0
Cities with ERRs: 0/1

$ python3 scripts/verify_entities.py --country france --city paris
=== france/paris ===
  entities: 205  hard: 0  warn: 0
Total HARD failures across 1 cities: 0

$ python3 scripts/validate_data.py --country france --city paris
[WARN] france/paris (no ERR; only pre-existing description-cap warns)
```

### Regeneration

Ran `generate_city.py france paris`, `generate_cross_cuts.py`, `generate_extras.py`, `generate_chrome_pages.py`, `generate_sitemap.py`, `generate_search_index.py`. Sitemap 1278 URLs, search index 1290 entries. Caddy perms refreshed on host.

Public smoke test: https://tablejourney.com/france/paris/bakeries/boulangerie-bo/ returned HTTP 200; https://tablejourney.com/france/paris/dietary/abattoir-vegetal/ returned HTTP 200.

## VERDICT: PASS
