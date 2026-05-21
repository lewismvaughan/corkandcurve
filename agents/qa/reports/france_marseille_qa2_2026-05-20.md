# QA2 report - Marseille (independent second judgment pass)

## QA1 carry-forward

QA1 (france_marseille_2026-05-20.md) fixed 18 defects. All QA1 edits
re-verified on disk in this pass:
- Le Femina cuisine (Tunisian -> Algerian Berber): confirmed correct, propagation done.
- Cafe de la Banque address (1er -> 24 boulevard Paul Peytral 13006): confirmed via operator site.
- Bar de la Marine arrondissement (1er -> 7e at 15 Quai de Rive Neuve): confirmed via Yelp, Marseille Tourisme, Google Maps.
- Le Miramar cooking class numerics (EUR 112, 8-10, 10:30-14:00): confirmed via Cote Magazine.
- Street Food Festival (Sep 10-12, Esplanade Jean-Paul II): confirmed via MPG 2026 operator page.
- Foire aux Santons (Vieux-Port, Nov 15 - Jan 4): confirmed via Made in Marseille, frequence-sud, maritima.
- 4 phantom festivals in region.json SEO: rewrite holds.
- Itinerary day-of-week (Sun -> Fri/Sat): hold.
- Pain Salvator hours (Tue-Sat 9-19, closed Sun-Mon): confirmed via lefooding, Petit Fute.
- Pizza Charly dup key: gone.
- Marche d'Aubagne -> Marche de Noailles: rename holds.
- Place Comtales -> Place des Precheurs: confirmed.
- Le Femina booking_url removed and La Kahena source_url repointed to lakahena.fr: holds.

## Pass-1 verify_entities at start of QA2

- HARD failures: 0 (after QA1)
- WARN: own_site_only and dead_evidence (acceptable per anti-bot rules)

## Judgment defects found in QA2

### A. Independent-directory address cross-check (sampled 100% of restaurants/fine-dining/casual-dining/cafes/wine-bars/dietary)

- restaurants.json `le-bouchon-provencal`: research shipped "5 Place aux Huiles, 13001"; operator's own site (lebouchonprovencal.com) and Yelp both confirm **6 Place aux Huiles, 13001 Marseille**. Building-number address fabrication. Fixed `address`, `verified.address_quoted` to operator's verbatim "6 Place aux Huiles 13001 MARSEILLE".

All other restaurants/fine-dining/casual-dining/cafes/wine-bars/dietary addresses cross-checked against Google Maps, Yelp, Mappy, marseille-tourisme.com, HappyCow, Beth Habad 8eme. No further address fabrications.

### A2. Specific-fact match (closures, hours, ownership)

- **cooking-classes.json `atelier-des-chefs-marseille`: PERMANENTLY CLOSED June 2025.** Yelp explicitly lists "CLOSED". The parent L'Atelier des Chefs chain has closed other locations too (Aix included). Removed entity. Cooking-classes now at 4 (below floor of 5-12); flagged below-floor in the report, not backfilled per QA scope rules.
- **casual-dining.json + dietary.json `le-cours-en-vert`: REBRANDED to "Mikala" 2024.** Same address (102 Cours Julien 13006), same vegetarian-and-now-vegan concept, different name. HappyCow no longer lists "Le Cours en Vert"; vegoresto and love-spots list "Mikala" at the same address. The QA1-era cuisine_evidence_url and source_url at happycow.net/europe/france/marseille/ no longer surface the venue. Renamed entity to Mikala in both files; repointed source_url, open_evidence_url, cuisine_evidence_url to current Mikala listings; description rewritten with "(formerly Le Cours en Vert)" disambiguation. Slug also changed (`le-cours-en-vert` -> `mikala`, `le-cours-en-vert-veg` -> `mikala-veg`).
- **restaurants.json `le-miramar` tip hours: "Closed Sunday and Monday" is WRONG.** Operator's own site + Yelp + multiple directories: Le Miramar is open Tuesday through Sunday, closed Monday only. Fixed tip to "Closed Monday".
- **casual-dining.json `chez-etienne` tip hours: "Closed Wednesday and Sunday" is WRONG.** Operator + Yelp + Mappy + Made in Marseille: open Monday-Saturday, closed Sunday only (Cassaro family runs single weekly close-day Sunday). Fixed tip to "Open Mon-Sat lunch and dinner, closed Sunday".
- **street-food.json `chez-etienne-walkup` hours: "Tue-Sat 11:30-14:30 and 19:00-22:30, closed Wed and Sunday" is WRONG.** Fixed to "Mon-Sat 12:00-14:00 and 20:00-23:00, closed Sunday" per multiple sources.
- **cooking-classes.json `provence-gourmet` address: "Marseille's Tourist Office (start), 13002 Marseille" — Tourist Office is at 11 La Canebiere 13001, not 13002.** Fixed address to "Marseille Tourist Office, 11 La Canebiere, 13001 Marseille" and verified.address_quoted to operator's verbatim "11 La Canebière 13001" (with accent in the verbatim quote only).
- **cooking-classes.json `chef-clement-marseille` description fabrication: "starts at the Marche des Capucins in Noailles, then back to the workshop".** Operator site (chefclement.com) describes the offering as "cours de cuisine a domicile" (at-home), with no fixed meeting point and no Marche des Capucins start. The fixed-workshop locations belong to partner workshops in Aix/Eguilles, not Marseille. Rewrote description, address, group_size, price to honestly describe the at-home format, retained the optional market-walk add-on language. Editorial score lowered 4.4 -> 4.2.

### A2. Chef / press credential structural checks

- AM par Alexandre Mazzia: 3 Michelin stars in 2021, Alexandre Mazzia at the pass — confirmed via Michelin operator site.
- Le Petit Nice: 3 Michelin stars, Gerald Passedat, Anse de Maldorme since 1917 — confirmed via passedat.fr.
- Une Table au Sud: 1 Michelin star (regained 2025/26 per france3-regions, confirmed Michelin 2026 1-star), Ludovic Turac — confirmed.
- Sepia: chef Paul Langlere (Puget Hill) — confirmed via operator site. Our data does NOT claim Michelin stars for Sepia (it's not in the Michelin guide for stars — checked: no defect).
- Auffo: 1 Michelin star (March 2026), Coline Faulquier, took over L'Epuisette site Jan 2025 — confirmed via Presse Agence.
- Dame Jeanne: Samy Leroy + Ohannes Kachichian, opened Feb 2025 at 86 rue Grignan 13001 — confirmed via cotemagazine, Le Grand Pastis.
- Limmat: Lilian Gadola — confirmed via operator site.
- Chez Madie: Delphine Roux since 1995 — confirmed via Yelp/Provence-Alpes.
- Le Femina: 4 generations of the founding family since 1921, Algerian Berber (Kabyle) tradition — confirmed via Yelp, Petit Fute (categorised "Restaurant algerien"), operator.

### A2. Source-URL final-host checks (sampled)

No source_url redirects to a different registered domain. Le Petit Pernod, La Caravelle, AM, Petit Nice, all stable on their canonical hosts. Marseille-tourisme.com URLs occasionally have wrong arrondissement in the slug (e.g. La Kahena "marseille-2eme" -> actually 1er; Carry Nation "marseille-1er" -> actually 6e) but the data on the page is correct; left as-is, no defect.

### B. Route / itinerary mismatches (food-tours, cooking-classes)

- Culinary Backstreets: route + meeting confirmed (Gare Saint-Charles -> Noailles -> Vieux Port).
- Do Eat Better: 66 Quai du Port meeting confirmed.
- Walking Food Tours, Top Tasting Tours, Food Lover Tour: operator pages match advertised offerings.
- Miramar bouillabaisse class: schedule confirmed (one or two Thursdays/month, 10:30-14:00, EUR 112, 8-10 max).
- Provence Gourmet: 9:30 AM start at Tourist Office, EUR 210 per person, max 8 — confirmed; address corrected to 13001.
- L'Atelier des Chefs: REMOVED (closed).
- Chef Clement: format clarified (at-home, not market-then-cook at Capucins) and editorialised honestly.

### C. Festival month / dates (cross-source verification)

Re-verified the 5 festivals with at least one source NOT being the organizer's homepage:

- Street Food Festival MPG: Sep 10-12 2026 at Esplanade Jean-Paul II (la Major), 17h-midnight, 42 stalls. Confirmed against operator's ticketing/event page AND eurotravelo. QA1 fix holds.
- Foire aux Santons: Nov 15 2025 - Jan 4 2026 at Vieux-Port (Quai du Port). 223rd edition. Confirmed against Made in Marseille, Frequence-Sud, maritima.fr (all 2025-dated), Ville de Marseille and JDS. QA1 fix holds.
- Chandeleur at Saint-Victor: Feb 2 procession start + 9 days. Saint-Victor at 3 Rue de l'Abbaye, 13007 confirmed. Archbishop processes from Vieux-Port through Rue Sainte. Confirmed via Diocese de Marseille, Departement13.
- Marseille Provence Gastronomie: March-October umbrella programme. Confirmed.
- Marche de Noel Vieux-Port: mid-November to early January. Confirmed via christmasmarketsineurope and madeinmarseille.

E4 verified-block alignment correction: Foire aux Santons HARD addr_mismatch after QA1 set address_quoted="Vieux-Port, Marseille" against entity.address="Quai du Port, 13002 Marseille" (token sets don't subset). Updated entity.address to "Vieux-Port (Quai du Port), 13002 Marseille" and address_quoted to "Vieux-Port" (verbatim from source), source_url repointed to a current Made in Marseille article that uses the same wording. Pass-1 now green.

### D. Thin-category fabrications (full sweep on dietary)

- vegan 2/2 confirmed (Oh Faon, De Bon'heur).
- vegetarian: `le-cours-en-vert-veg` renamed to `mikala-veg` (still exists at same address under new branding). Tabla confirmed at 106 Cours Julien 13006 via operator site tablamarseille.fr.
- gluten_free 2/2 confirmed (La Pepite at 145 Rue Sainte 13007; Oh Faon).
- halal 3/3 confirmed (Le Femina, Chez Yassine, La Kahena).
- kosher 2/2 confirmed (Le 8eme Sud, La Maronaise Cafe both still listed on Beth Habad 8eme directory at the documented addresses).

### E. Editorial-prose echoes (E2 / E3 sweep across all prose)

E2 (QA1 Femina rewrite Tunisian -> Algerian Berber) propagation gaps QA1 missed:
- **city.json food_culture_summary: "Tunisian couscous at Le Femina since 1921" -> "Algerian Berber couscous at Le Femina since 1921".** Fixed.
- **food-history.json `immigrant_influences[].community="Tunisian"`: "Le Femina the institution since 1921, La Kahena and Chez Yassine the follow-on counters" — Femina is Algerian Berber, not Tunisian.** Rewrote to attribute La Kahena (1978) and Chez Yassine (2014) as the Tunisian follow-ons, and moved Le Femina into the Algerian community paragraph as the city's oldest Maghrebi institution.
- **food-history.json `key_eras[].period="1947 to 1962, the Maghrebi arrival"` summary**: implication that Le Femina arrived in that wave was misleading (Femina opened 1921, pre-Independence). Reworded to make clear Femina (Algerian Berber) had already been operating since 1921 by the time the post-Independence wave arrived.

E1 (closed-venue echoes): L'Epuisette mentions in fine-dining, restaurants, itineraries are all in acceptable "Auffo took over the L'Epuisette site" historical context. Restaurant Saisons absent (QA1 verdict holds).

E3 (phantom venues): walked region.json SEO, city.json, neighborhoods.json vibe, food-history.json prose, signature-dishes.json history, seasonal-food.json blurbs, itineraries.json prose, per-entity descriptions/tips/why_hidden. No additional phantoms beyond QA1's already-fixed region.json festivals echo.

### E4. Verified-block consistency

- Foire aux Santons: fixed (see Section C above).
- Le Bouchon Provencal: updated `verified.address_quoted` to operator's verbatim "6 Place aux Huiles 13001 MARSEILLE" matching the new entity.address.
- Provence Gourmet: updated `verified.address_quoted` to operator's verbatim "11 La Canebière 13001" matching the new entity.address.
- All other QA1-edited entities have address_quoted matching new address.
- All checked_on dates already 2026-05-20.

### Itinerary day-of-week × hours re-walk

- marseille-weekend-classics (Fri+Sat): Four des Navettes Mon-Sat, La Tisserie Tue-Sat, Chez Madie Mon-Sat (closed Sun only confirmed), La Caravelle daily, Chez Fonfon daily (closed late Jan two weeks), Marche des Capucins Mon-Sat, Coogee Mon-Sat, **Chez Etienne corrected to Mon-Sat closed Sun only** (was incorrectly believed Tue-Sat closed Wed by QA1). Friday + Saturday still consistent with all venues; QA1's framing rename holds.
- marseille-noailles-maghreb (Fri+Sat): Femina Tue-Sun lunch (closed Sun evening + Mon), La Cantinetta closed Sun only, Pepie Tue-Sat, Pelle-Mele daily late, Chez Yassine Tue-Sun, La Kahena daily, Mama Shelter daily, La Mercerie Tue-Sat, Carry Nation Wed-Sun. Fri+Sat compatible. Hold.
- marseille-fine-dining-three-days: undated, compatible with Tue/Wed/Thu/Fri/Sat windows. Hold.

Geographic adjacency claims walked: "across the harbour" Chez Madie (138 Quai du Port) to La Caravelle (34 Quai du Port) ~500m walk along the same quay; "up the hill" Marche des Capucins (1er) to Coogee (100 Bd Baille 13005) ~1.5km southeast; "down through Endoume to the Catalans beach" Ben Mouture (34 Rue du Petit Chantier 13007) ~1km. All plausible. No "next door" / "across the street" claims that would need closer adjacency.

### Marseille municipality (13001-13016) check

Every entity has a 130xx postcode in the 1-16 range. No phantom postcodes.

## Polishes

- region.json `seo.pages.festivals.description` was 187 chars (over 165 cap). Tightened to "Marseille food festivals worth a date in 2026: Foire aux Santons, Vieux-Port Christmas market, MPG, Street Food Festival and Chandeleur at Saint-Victor." — under cap. No content lost.

## Defects total

QA2 net new fixes:
- A address fabrication: 1 (Le Bouchon Provencal building number)
- A2 closure: 1 entity removed (L'Atelier des Chefs)
- A2 rebrand: 2 entries renamed (Le Cours en Vert -> Mikala, in casual-dining + dietary)
- A2 wrong hours: 3 (Le Miramar, Chez Etienne x2 in casual-dining + street-food)
- A2 description fabrication: 1 (Chef Clement market start)
- A2 wrong address: 1 (Provence Gourmet postcode)
- E2 echo: 3 (city.json food_culture_summary, food-history Tunisian community contribution, food-history Maghrebi-era summary)
- E4 / Pass-1 alignment: 1 (Foire aux Santons address_quoted vs address token-set)
- Polish: 1 (festivals SEO description length)

K = 13

## Below-floor topics after QA2

- cooking-classes: 4 (floor 5) — L'Atelier des Chefs removed for permanent closure; needs research backfill of 1+ new entities (Cuisine de la Mer Marseille, Atelier Chef-Sandrine, etc.).

All other topics remain at or above floor.

## Pass-1 verify_entities after QA2 edits

```
Total HARD failures across 1 cities: 0
```

`check_internal_references.py`: ERR=0 WARN=0
`validate_data.py --city marseille`: exit 0, no ERR, length WARNs unchanged from QA1.

## Verdict

VERDICT: PASS
