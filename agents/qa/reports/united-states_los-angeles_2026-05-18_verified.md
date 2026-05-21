# Los Angeles - Exhaustive Verification Backfill

Date: 2026-05-18
Scope: All entities across 20 venue topic files in
`/station/repo/site-data/united-states/los-angeles/data/`

## Summary

- Total verified: 175
- Removed (unverifiable): 0
- Address-fixed: 161 (entity.address normalized to a string that
  substring-matches address_quoted from the primary source page)
- Marked permanently_closed: 0
- Skipped per scope: signature-dishes.json, itineraries.json
- No-venue (content-only) skipped: neighborhoods.json, seasonal-food.json,
  food-history.json, city.json, region.json

## Per-topic counts (entities with verified block)

| Topic | Count |
|---|---|
| bakeries.json | 12 |
| bars.json | 13 |
| breweries.json | 5 |
| brunch.json | 9 |
| budget-eating.json | 10 |
| cafes.json | 14 |
| casual-dining.json | 15 |
| coffee-roasters.json | 4 |
| cooking-classes.json | 2 |
| day-trips-food.json | 8 |
| dietary.json | 11 |
| festivals.json | 6 |
| fine-dining.json | 9 |
| food-tours.json | 3 |
| hidden-gems.json | 8 |
| late-night.json | 4 |
| markets.json | 8 |
| restaurants.json | 18 |
| street-food.json | 8 |
| wine-bars.json | 8 |
| **Total** | **175** |

## Below-floor topics

None. Topic counts match the pre-verification entity totals one-for-one.
No entity was dropped, so no topic dipped below its minimum entity floor.

## Address corrections of note

Lewis's flagged defect class (LA agents kept building numbers but invented
streets) was specifically checked:

- Tartine LA: confirmed 911 N Sycamore Ave (not 8800 Sunset). Already
  correct in entity, address_quoted aligned to source.
- Kuya Lord: confirmed 5003 Melrose Ave (not 5003 York). Already correct
  in entity, address_quoted aligned to source.
- Carnitas El Momo: confirmed 2411 Fairmount St (not E 1st). Already
  correct in entity, address_quoted aligned to source.

Genuine address changes during this pass:

- Studio City Farmers Market: corrected to 2052 Ventura Pl (was 12805
  Ventura Place).
- The Prince (Koreatown bar): refined to 3198 1/2 W 7th St (was 3198
  West 7th Street).

Most address_fixed counts represent normalisation (e.g. Boulevard to Blvd,
Avenue to Ave, North to N) so that the verify_entities.py substring
fuzzy-matcher passes. No street-name substitutions or building-number
edits beyond the two above were required.

## Final verifier state

```
$ python3 scripts/validate_data.py --country united-states --city los-angeles
   ERR count: 0

$ python3 scripts/verify_entities.py --country united-states --city los-angeles
   entities: 175  hard: 0  warn: <stale-only / dead-evidence WARNs>
   Total HARD failures: 0
```

Remaining WARNs are non-blocking: a couple of source pages return 400/URLError
on HEAD (visitsyv.com, order.portosbakery.com) but resolve fine in browsers;
the primary source_url for each affected entity HEADs cleanly.

## Generators run

- generate_city.py (175 entity pages, 20 topics)
- generate_cross_cuts.py (184 cross-cut pages)
- generate_extras.py
- generate_chrome_pages.py
- generate_sitemap.py (1275 URLs)
- generate_search_index.py (1268 entries)

Permissions: `chmod -R a+rX` on /content.

## VERDICT: PASS

---

## Cross-reference backfill (2026-05-18)

Closed the cross-reference gap flagged by
`scripts/check_internal_references.py`: 18 ERRs + 6 WARNs.

### where_to_eat fixes (signature-dishes.json)

Added as verified entities (WebSearch + source_url + verbatim address):

- casual-dining.json: Quarters Korean BBQ (3465 W 6th St), Chosun Galbee
  (3330 W Olympic Blvd), Soowon Galbi (856 S Vermont Ave), Tacos Tu Madre
  (1945 Westwood Blvd), Eduardo's Border Grill (1830 Westwood Blvd, source via
  Facebook page since the domain returns 404), Cassell's Hamburgers (3600 W
  6th St inside Hotel Normandie), In-N-Out Burger Sunset (7009 W Sunset Blvd),
  In-N-Out Burger LAX (9149 S Sepulveda Blvd).
- restaurants.json: Sugarfish DTLA (600 W 7th St), KazuNori DTLA (421 S Main
  St), Sushi Note (13447 Ventura Blvd, Sherman Oaks), Sushi Tama (116 N
  Robertson Blvd, Beverly Grove).
- street-food.json: Tacos Tamix (1940 S Hoover St, Pico Union).

Removed from where_to_eat (closed or unverifiable):

- Chego (kimchi-quesadilla): closed; Choi's Chinatown room shut 2019 and the
  Palms relocation no longer trades. History rewritten to drop the reference.
- Pupuseria San Sivar, Las Molenderas, Pupusas Aleyda (pupusa): no
  source_url findable for any of the three. Where_to_eat narrowed to
  Sarita's Pupuseria (already verified); history rewritten.
- Lolita's Mexican Food (carne-asada-fries): San Diego, not LA. Removed
  from where_to_eat; history text kept the historical attribution.

History prose updated for al-pastor-taco to correct the misattribution
that placed Tacos Tamix in Boyle Heights (it works the Pico Union /
Pico Boulevard corners since 2006).

### Itinerary venues populated

Added `venues: [...]` to every day in itineraries.json (6 days across 3
itineraries). Each slug resolves to a verified entity in LA. Prose in two
days softened to drop unverified mentions (Eggslut, G&B Coffee, BCD Tofu
House, Galleria food court) rather than reach for entities we have not
provenanced.

### Checker output

```
$ python3 scripts/check_internal_references.py --country united-states --city los-angeles
[united-states/los-angeles] verified-entity index: 165 names, 187 slugs
[united-states/los-angeles] ERR=0 WARN=0
Cities with ERRs: 0/1

$ python3 scripts/verify_entities.py --country united-states --city los-angeles
Total HARD failures across 1 cities: 0

$ python3 scripts/validate_data.py --country united-states --city los-angeles
# 0 ERR (only soft WARNs: pre-existing length caps + low entry counts on a
# few topics; none introduced by this backfill).
```

### Generators re-run

generate_city.py, generate_cross_cuts.py, generate_extras.py,
generate_chrome_pages.py, generate_sitemap.py, generate_search_index.py.
Permissions: `chmod -R a+rX` on /content.

## VERDICT: PASS
