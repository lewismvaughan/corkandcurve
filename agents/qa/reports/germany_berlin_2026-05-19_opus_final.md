# Opus FINAL validation - Berlin (stage 4 of QA pipeline)

Date: 2026-05-19
Scope: Narrow, decisive Opus pass after Sonnet QA1 (germany_berlin_2026-05-19.md) and Sonnet QA2 (germany_berlin_2026-05-19_pass2.md), both PASS.

## 1. Cocolo Ramen resolution (QA2 flag)

Verified cocolo.eu still redirects 301 to sedo.com (domain-for-sale lander). WebSearch + WebFetch confirm Cocolo Ramen is still operating at Gipsstr. 3, 10119 Berlin, now under KUCHI Restaurants. Live page: https://kuchi.de/restaurant/cocolo-ramen/. Confirmed:

- Address: "Gipsstr. 3, 10119 Berlin"
- Hours: "Di - Sa 18-23 (Last order 22:00)" / "So 18-22"
- Cuisine: Japanese ramen (page is branded "Cocolo Ramen Mitte")
- Status: open (Mo closed, otherwise operating)

Action: replaced source_url + open_evidence_url + cuisine_evidence_url across two entries (cocolo-ramen in casual-dining.json, cocolo-ramen-budget in budget-eating.json). No removal needed.

## 2. Below-floor dietary evidence URLs

### 2a. Hummus and Friends source/open URL (broken across 3 files)

Discovered hummusandfriends.com now redirects to hummusfriends.com (Swiss caterer in Lonay, not the Berlin restaurant). 10 references across dietary.json, budget-eating.json, casual-dining.json point at the broken Swiss-redirect URL.

The actual Berlin restaurant lives at http://hummus-and-friends.com/?lang=en (different domain), which confirms address Oranienburger Strasse 27, "vegetarian & kosher" cuisine, Mon-Sun 11:00-23:00.

Action: atomic bulk replace of all 10 hummusandfriends.com references to hummus-and-friends.com across the 3 files.

### 2b. Hummus and Friends kosher cuisine_evidence_url (QA2 cuisine_unverified)

Previously pointed at kosher.de which threw ECONNREFUSED. Replaced with https://www.visitberlin.de/en/hummus-friends which loads and confirms in page text: "you will find tasty kosher and vegan dishes that are freshly and quickly prepared."

### 2c. Mustafas Gemuese Kebap halal cuisine_evidence_url (QA1 + QA2 flag)

Previous zabihah.com/mob/sub URL showed wrong address (Mitte 7 Neue Promenade rather than Mehringdamm 33). Replaced with https://www.halalhelden.de/eintrag/mustafas-gemuse-kebap-berlin-kreuzberg/ which loads and confirms in page text: "Ein Halal-Zertifikat bei Mustafas Gemuese Kebap liegt vor. Es wurde entweder muendlich zugesagt oder sichtbar im Laden einzusehen" plus "Super Halalheld" designation.

### 2d. Adana Grillhaus halal (QA1 + QA2 cuisine_unverified)

Existing zabihah listing title states "Adana Grillhaus | Halal Turkish in Kreuzberg, Berlin." Content body is anti-bot blocked (acceptable). Halalhelden has a different Adana location at Manteuffelstrasse 86 with weaker certification language. Existing zabihah URL is the best available; left as-is. Not a defect.

## 3. Spot-check of 10 random entities (topics QA1+QA2 likely skipped)

Sampled one entity per topic: bakeries, bars, breweries, cafes, coffee-roasters, fine-dining, hidden-gems, late-night, markets, restaurants, street-food.

| Topic | Entity | Verification |
|-------|--------|--------------|
| bars | Bar Tausend | Confirmed: Schiffbauerdamm 11, cocktail/dance bar |
| breweries | BRLO Brwhouse | Confirmed: Schoeneberger Strasse 16, working brewery + restaurant |
| cafes | Cafe Anna Blume | Confirmed: Kollwitzstrasse 83, active cafe with terrace |
| coffee-roasters | The Barn | Confirmed: active coffee roaster site |
| fine-dining | Coda Dessert Dining | Michelin source 403 (anti-bot, acceptable) |
| hidden-gems | Henne Alt Berliner Wirtshaus | Confirmed: Leuschnerdamm 25, traditional roast chicken Wirtshaus |
| late-night | Curry 36 (Mehringdamm) | Confirmed: hours 09:00-05:00 daily |
| markets | Biomarkt Kollwitzplatz | Confirmed via visitberlin.de: Thursday ecomarket since 1996 |
| restaurants | Lode und Stijn | Michelin source 403 (anti-bot, acceptable) |
| street-food | Maroush | berlinfoodstories anti-bot blank (acceptable) |
| **bakeries** | **Endorphina** | **DEFECT FOUND** (see below) |

### Spot-check defect: Endorphina (bakeries.json)

The JSON listed Endorphina at Weichselstrasse 65, 12045 Berlin. The actual bakery is at Elsenstrasse 52, 12059 Berlin per its own site endorphina.de and every external directory (HappyCow, Tripadvisor, Foursquare, visitberlin, top10berlin). The Weichselstrasse 65 address is fabricated.

The fabrication slipped past pass-1 because both `entity.address` and `verified.address_quoted` carried the same wrong string, so fuzzy-match passed. This is a Class "address hallucination" defect of the kind logged in memory (feedback_address_hallucination.md): plausible building number on the wrong street.

Additional finding: the Hofbaeckerei (the cafe / shop at Elsenstrasse 52) is currently closed for renovation per the site, but the bakery continues to operate via seven weekly Berlin farmers' markets.

Action: rewrote the entity with correct address, status, hours, description, tip, source_url, open_evidence_url, cuisine_evidence_url (happycow page for vegan-bakery cuisine confirmation). Description trimmed to within 2 chars of the 165-char soft cap (167; in line with ~30 other bakeries.json entries at WARN level).

## 4. Final prose echo grep (QA1 + QA2 removed slugs)

Grepped all 27 site-data/germany/berlin/data/*.json for: berliner-bierfestival, goldhahn-und-sampson-kreuzberg, kanaan, kanaan-brunch, kanaan-vegetarian. Also case-insensitive Kanaan name search.

All clean. Zero prose echoes remain.

## 5. Production smoke test

```
HTTP/2 200  https://tablejourney.com/germany/berlin/
HTTP/2 200  https://tablejourney.com/germany/berlin/restaurants/
HTTP/2 200  https://tablejourney.com/germany/berlin/dietary/
```

Currency rendering:
- /germany/berlin/ : EUR symbols render as "€" / "€€€" (no "EUR EUR" / "GBP GBP" leakage)
- /germany/berlin/restaurants/ : same, mix of €, €€, €€€
- /germany/berlin/dietary/ : dietary entries don't carry price_tier (zero EUR symbols as expected)

Placeholder leak check on rendered HTML: only HTML5 `<input placeholder="...">` attributes (UI text for the search bar) match the "placeholder" grep. No template `{{ }}` leakage, no TODO/FIXME strings.

Entities still rendered:
- "Cocolo Ramen" appears 3 times on /germany/berlin/casual-dining/
- "Mustafas" appears 5 times on /germany/berlin/dietary/

## 6. Regeneration sequence

Ran the full procedure step 5 sequence:
- scripts/generate_city.py germany berlin (193 entity pages, 20 topics)
- scripts/generate_cross_cuts.py (783 cross-cut pages)
- scripts/generate_extras.py
- scripts/generate_chrome_pages.py
- scripts/generate_sitemap.py (7042 URLs)
- scripts/generate_search_index.py (7118 entries)

Then `sshp host 'sudo chmod -R a+rX /opt/claude-stations/tablejourney/repo/content'` for Caddy.

## Defects total: 4 fixed this pass

1. **cocolo-ramen** (casual-dining.json): source_url + open_evidence_url + cuisine_evidence_url replaced (cocolo.eu->kuchi.de) - resolves QA2 flag.
2. **cocolo-ramen-budget** (budget-eating.json): same URL replacement applied - resolves QA2 flag.
3. **Hummus and Friends** source_url and open_evidence_url across 3 files (10 references): hummusandfriends.com (now Swiss caterer redirect) replaced with hummus-and-friends.com (the Berlin restaurant's actual site). Net effect: 3 entities' source/open evidence now resolve correctly. Also: hummus-and-friends-veg cuisine_evidence_url was happycow (unchanged); kosher cuisine_evidence_url switched from kosher.de (ECONNREFUSED) to visitberlin.de (working, kosher term in body); mustafas halal cuisine_evidence_url switched from a zabihah sub-page (wrong address) to halalhelden.de (halal certified, correct Mehringdamm address).
4. **endorphina** (bakeries.json): wrong address corrected (Weichselstrasse 65 -> Elsenstrasse 52), description rewritten, evidence URLs upgraded to own-site + happycow. Cafe-closed-for-renovation noted in description and tip. This was a pass-1 / QA1 / QA2 miss because the fabricated address was internally consistent.

## Below-floor topics (unchanged from QA2)

- dietary/vegetarian: 2 (floor 4)
- dietary/gluten_free: 2 (floor 4)
- dietary/kosher: 1 (floor 4)
- dietary/halal: 3 (floor 4)
- bakeries: 17 (floor met)

No new below-floor topics created by this pass.

## Pass-1 gaps observed (for verify_entities.py future fix)

1. 301 redirect to a domain-broker landing page should be a failure, not a pass. Both cocolo.eu->sedo.com and hummusandfriends.com->hummusfriends.com (Swiss caterer with different brand) were passing pass-1 because HEAD returned 200 after redirect.
2. Address consistency check (entity.address == verified.address_quoted) is insufficient when both fields carry the same hallucinated address. Pass-1 cannot catch a same-on-same fabrication; external cross-reference is needed.

## Verdict

VERDICT: PASS
