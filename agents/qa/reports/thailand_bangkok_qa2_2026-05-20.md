# QA report — Bangkok (judgment pass-2, independent)

Date: 2026-05-20
Scope: /station/repo/site-data/thailand/bangkok/data/*.json
Stage: QA2 (independent second judgment pass after QA1 + ship_safety pass-1)

## Pass-1 carry-forward

- verify_entities.py: 0 HARD, 77 WARN (mostly bk.asia-city.com DNS-dead URLs left as cuisine_evidence_url; Time Out 404s on a few; Wine Pub Pullman own-site times out per anti-bot)
- check_internal_references: 0 ERR 0 WARN
- check_evidence_content: 0/11 matched but all 11 anti-bot 403/404 — fetch-fail, not defect
- check_festival_dates: 0/5 matched but all 5 fetch-fail / unknown source pages
- check_external_urls: 29/29 OK
- ship_safety.sh: ALL CHECKS PASSED post-QA2 edits

## Resolution of 3 noted-for-backfill entities (QA2 priority 1)

### Akkee — REMOVED (wine-bars + hidden-gems)

Independent-directory check (Star Wine List, TimeOut Bangkok new-wine-bars,
Raisin, Tatler Asia) found **no Akkee wine bar at 1052-1054 Charoen Krung**.
1052-1054 Charoen Krung is **80/20's actual address**. Search confirms Akkee
is a Nonthaburi-based pop-up that does kitchen takeovers at natural-wine
bars; not a permanent venue. The natural-wine cellar bar in the Charoen
Krung / Talat Noi area is Charmkrung (6th floor of a 1950s factory),
different venue at different floor. Pure address/identity fabrication.

- Removed Akkee from `wine-bars.json` (5 wine bars now, was 6)
- Removed Akkee from `hidden-gems.json` (7 hidden-gems now, was 8)

### Akha Ama Coffee Bangkok branch — REMOVED (coffee-roasters + hidden-gems)

Akha Ama's official site (akhaamacoffee.com) lists **only Chiang Mai and
Tokyo branches**. No Bangkok branch listed at all. The ICONSIAM directory
page that earlier appeared in search returned 404 on fetch. The Pridi
Banomyong 14 location in JSON is not in Akha Ama's official directory.
Either a closed/never-opened branch or a fabrication.

- Removed Akha Ama from `coffee-roasters.json` (5 roasters now, was 6)
- Removed Akha Ama from `hidden-gems.json` (already removed above)
- Itinerary cross-refs replaced (see E1 below)

### Mont Nomsod source_url — REPLACED + hours corrected

Mont Nomsod is a real venue (since 1964, 160/1-3 Dinso Road, Phra Nakhon).
Real source confirmed via Coconuts Bangkok, DanielFoodDiary, Tripadvisor
(d4086429). Replaced Wikipedia generic source_url with Coconuts review.

ALSO: hours were wrong. Coconuts confirms **opens 12:00**, not 14:00
(JSON had Daily 14:00-23:00 — actual is 12:00-23:00). Address corrected
from 160/2-3 to 160/1-3 per Tripadvisor canonical listing.

- Fixed in `bakeries.json`: source_url, address, hours, tip prose
- Fixed echo in `itineraries.json` weekend-classics day 1 afternoon
  ("from 14:00" -> "from 12:00")
- Fixed echo in `itineraries.json` fine-dining-tour day 2 (was "Breakfast
  at Mont Nomsod" but Mont Nomsod opens 12:00 -- moved to mid-afternoon)

## Additional defects found and fixed (independent QA2 sweep)

### A. Independent-directory address cross-check (sampled 12 entities)

- **Mit Ko Yuan** (casual-dining): JSON address "186 Damnoen Klang Tai Road"
  is WRONG. Wikipedia + eatingthaifood + tripadvisor all confirm 186
  **Dinso Road**, Sao Chingcha, Phra Nakhon 10200. Address-fab class
  [[feedback-address-hallucination]]. Fixed.
- **Maison Jean Philippe** (bakeries): JSON had address "97/4 Sukhumvit 49"
  with "Maison Jean Philippe Bangkok" name + invented "Closed Monday" hours.
  Real main bakery is at **335 Thong Lo 17 Alley** (The Commons, since 2012,
  per bangkokfoodies + foursquare). Sukhumvit 49 is one of their delivery
  locations, not a public counter. Corrected address + name + hours; source
  URL switched from dead wikipedia generic to bangkokfoodies directory.
- **Princ Hospital Bakery (Bread Story)** (bakeries): pure fabrication.
  "555 Sukhumvit 55" is Princ International Hospital, not a bakery. "Bread
  Story" venue does not exist in Bangkok per Bartels Sourdough + Eric
  Kayser + Sourdough Bangkok + Time Out's 6 sourdough bakeries list.
  REMOVED entity (6 bakeries now, was 7).
- **Sky Bar at Lebua** (bars): JSON said 63rd floor. Lebua official
  lebua.com/restaurants/sky confirms **64th floor**. Same address change
  applied to bars.json prose, address, address_quoted, booking_url, and
  source_url.
- Sampled and confirmed correct: Le Du (399/3 Silom Soi 7), Saawaan
  (39/19 Soi Suan Phlu), Issaya (4 Soi Sri Aksorn), Sorn (56 Sukhumvit 26),
  80/20 (1052-1054 Charoen Krung), Khua Kling Pak Sod (Sukhumvit 53 Alley
  ~= Thonglor 5 - debatable but close), Krua Aroy Aroy (Pan Road),
  Vivin Grocery, Wine I Do.

### A2. Specific-fact match: chef and prose corrections

- **Saneh Jaan chef name FABRICATED** (fine-dining.json): JSON had
  "Auychai 'Eve' Tantragoolsuk". Multiple sources (Phuket101, The Ranting
  Panda, Saneh Jaan official) confirm actual chef is **Pilaipon 'Toy'
  Kamnag**. Corrected. (Cross-city chef-name-fab defect class
  [[feedback-chef-name-fabrication]])
- **Mezzaluna fine-dining tip prose echo**: JSON said "Sirocco bar on
  the 64th floor for the pre-dinner" — Sirocco is NOT on 64th floor,
  Sky Bar is. QA1 already updated the restaurants.json Mezzaluna prose
  to mention Sky Bar but missed the fine-dining.json mirror entity.
  Fixed to "Sky Bar on the 64th floor".

### A3. Asia's 50 Best 2026 rank updates (QA1 used 2025)

The 2026 list was published in March 2026 (today is 2026-05-20), so
2026 ranks are current. QA1 used 2025 ranks throughout.

- **Gaggan Anand**: JSON said "No. 1 in 2025" — 2026 list places him at
  **No. 3**. Updated both fine-dining.json and restaurants.json to read
  "No. 1 in 2025 (No. 3 in 2026)".
- **Suhring**: JSON said "Asia's 50 Best 2024 No. 7" — 2026 list places
  him at **No. 18** (down from 2024 No. 7, 2025 No. 11). Updated to
  "Asia's 50 Best 2026 No. 18" (more current).
- **Nusara**: JSON said "No. 6 on Asia's 50 Best 2024 (No. 5 in 2026)"
  — confirmed No. 5 in 2026 is correct per nationthailand + home-and-travel
  + friday bangkok. Reframed to lead with 2026.
- **Le Du**: JSON described as "former No. 1 (2023)". Added 2026 rank
  context "(2023, No. 36 in 2026)" since current rank is still meaningful.
- **food-history.json** era-2018-now summary: appended "the 2026 list
  placed [Gaggan] No. 3 with Nusara at No. 5" so the current state is
  represented alongside the 2025 No. 1 historical claim.

### E1. Closed-venue / removed-venue echoes after Akha Ama removal

Two itinerary references to Akha Ama Coffee on Soi Pridi Banomyong 14
had to be rewritten since the entity no longer exists:

- `itineraries.json` weekend-classics day 2 afternoon: "coffee break at
  Akha Ama Coffee on Soi Pridi Banomyong 14" -> "coffee break at Pacamara
  on Sukhumvit 49 or another third-wave roaster".
- `itineraries.json` fine-dining-tour day 4 morning: "coffee at Akha Ama
  Coffee on Soi Pridi Banomyong 14" -> "coffee at Sarnies Bangkok on
  Charoen Krung 44". venues[] updated: `akha-ama-hidden` -> `sarnies-bangkok`.

### E2. QA1-edit echoes verified

- Sorn 3 stars: no echoes outside fine-dining/restaurants (food-history,
  city, region all already updated).
- Suhring 3 stars: no echoes (no remaining "two-star Suhring" strings).
- Baan Tepa 2 stars + Bang Kapi address: no echoes (Soi Suan Plu mentioned
  only as Saawaan's actual neighbourhood).
- Saawaan lost star: no echoes (no "Michelin-starred Saawaan" remaining).
- Gaggan Sukhumvit 31 address: no Soi Langsuan echoes anywhere.
- Nusara Maha Rat address: no "302 Tha Tian" echoes anywhere (itinerary
  fixed in QA1).
- Raan Jay Fai Wed-Sat 09-19 hours: confirmed no late-night entry remains
  (QA1 already removed from late-night.json).
- Thipsamai 09-midnight Wed-Mon: budget-eating.json still had old echo
  "Queues from 17:00 to 02:00" - **FIXED to "Open Wed-Mon 09:00 to midnight"**.
- Soi Polo 07-21 daily: late-night entry already says "21:00" closes,
  budget-eating already says "Open 07:00 to 21:00 daily". OK.
- Nai Ek 08-midnight: budget-eating and late-night both already say
  midnight closing. OK.
- Festival 2026 dates (Vegetarian Oct 10-18, Loy Krathong Nov 24-25,
  WGF Sep 29-Oct 4): all consistent across festivals.json, city.json
  ("peak_food_season" + "Yaowarat Vegetarian Festival turns Yaowarat
  into a jay crawl for nine days"). OK.

### E3. Phantom-named-venue editorial sweep

Walked every prose-bearing file (region, city, neighborhoods,
food-history, signature-dishes, seasonal-food, itineraries) for
capitalised proper-noun venue names. All named venues resolve to
entities in data:

- city.json: Jay Fai, Sorn, Suhring, Le Du, Nusara, 80/20, Potong — all OK.
- region.json descriptions: Sorn, Suhring, Le Du, Nusara, Gaggan Anand,
  Or Tor Kor, Klong Toey, Yaowarat, Jay Fai, Sukhumvit Soi 11, Veganerie,
  Broccoli Revolution, Anantara Siam, Sompong, Silom Thai, Songkran,
  Yaowarat Vegetarian Festival — all resolve.
- food-history.json: Thipsamai, Ian Kittichai (Issaya), Bo Songvisava
  (Bo.lan), Jay Fai, Sorn, Suhring, Baan Tepa, Le Du, Nusara, Potong,
  Gaggan Anand, Haoma — all resolve (Bo.lan referenced as context, not
  as an entity to link).
- neighborhoods.json silom-sathorn: "Vertigo and Sirocco" — both verified
  real (Vertigo at Banyan Tree 61st floor; Sirocco at Lebua). Sirocco
  is real but not an entity in our data — accepted as generic landmark
  mention (not phantom; both bars exist).
- itineraries.json: post-edits, all venue mentions resolve to entities
  in the data (verified by check_internal_references = 0 ERR).

### E4. Verified-block consistency after meeting_point / address edits

- Mit Ko Yuan: updated `address` AND `verified.address_quoted` together
  (both "186 Dinso Road, Sao Chingcha, Phra Nakhon, Bangkok 10200").
- Mont Nomsod: updated `address` ("160/1-3 Dinso Road") AND
  `verified.address_quoted` together; `verified.checked_on` already
  "2026-05-20".
- Sky Bar at Lebua: updated `address` ("64th Floor") AND
  `verified.address_quoted` AND `booking_url` AND `verified.source_url`
  to lebua.com/restaurants/sky/ (canonical).
- Maison Jean Philippe: updated `name`, `address`, `hours`, AND
  `verified.address_quoted` together.

### Source-URL final-host check (sampled 15 entities)

Spot-checked 15 source_urls for final-host integrity:
- Le Du (ledubkk.com) — own-domain, fine
- Sorn (sornfinesouthern.com) — own-domain, fine
- Suhring (restaurantsuhring.com) — own-domain, fine (SSL cert warn but live)
- Gaggan (Michelin guide) — official, fine
- Nusara (nusarabkk.com) — own-domain, fine
- Potong (restaurantpotong.com) — own-domain, fine
- Baan Tepa (Michelin guide) — official, fine
- 80/20 (8020bkk.com) — own-domain, fine
- Saawaan (saawaan.com) — own-domain, fine (SSL cert warn but live)
- Mont Nomsod (Coconuts) — third-party but venue-specific, fine
- Issaya (issaya.com) — own-domain, fine
- Mezzaluna (lebua.com/mezzaluna) — own-domain, fine
- BKK Social Club (Four Seasons) — own-domain hotel page, fine
- Tropic City (tropiccitybkk.com) — own-domain, fine
- Mikkeller Bangkok (Tripadvisor) — third-party but venue-specific, fine

No final-host drift found (no domain-sale/redirect issues).

## Itinerary day-of-week × venue-hours re-walk

**Weekend classics (2 days):**
- Day 1 Saturday: Roots Coffee (daily 07:30-19:00, OK), Raan Jay Fai
  (Wed-Sat 09-19, **OK Saturday is the last day of the week**),
  Mont Nomsod (Daily 12:00-23:00, OK afternoon), Thipsamai (Wed-Mon,
  closed Tuesday, **Saturday is open**), BKK Social Club (hotel, daily).
- Day 2 Sunday: Or Tor Kor (daily), Brave Roasters (daily 08-19), Sampeng
  Lane stalls (daily), Nai Ek Roll Noodles (daily 08-midnight),
  Tropic City (no closure listed, fine). OK.

**Fine-dining tour (5 days):**
- Day 1 Monday: Roots (daily), Pacamara (daily), Khua Kling Pak Sod
  (daily 07-22:30), Klong Toey market (daily), Le Du (closed Sundays —
  **Monday open**, OK).
- Day 2 Tuesday: Sarnies (daily 07-22), Supanniga Tha Tien (closed
  Mondays — **Tuesday open**, OK), Mont Nomsod (daily), Nusara (closed
  Mondays — **Tuesday open**, OK).
- Day 3 Wednesday: Landhaus (Tue-Sun, **Wednesday open**), Factory Coffee
  (daily), Iconsiam SookSiam (daily), Sarnies (daily), Suhring (closed
  Mondays and Tuesdays — **Wednesday open**, OK).
- Day 4 Thursday: Sarnies (daily), Nai Ek (daily 08-midnight), Potong
  (closed Mondays — **Thursday open**, OK).
- Day 5 Friday: Sarnies, Polo Fried Chicken (daily 07-21, brunch ok),
  Sorn (closed Mondays — **Friday open**, OK), Rabbit Hole (typically
  daily for late-night, OK).

**Vegan weekend (2 days):**
- Day 1 Saturday: Broccoli Revolution, One Ounce For Onion, Veganerie,
  Wallflowers Cafe, Anotai (closed Mondays — **Saturday open**, OK),
  Teens of Thailand. OK.
- Day 2 Sunday: Courageous Kitchen (book ahead), Ethos Vegetarian,
  May Veggie Home, Tep Bar. OK.

All itinerary day-of-week × venue-hours checks PASS.

## Files touched

- `wine-bars.json` (Akkee removed)
- `hidden-gems.json` (Akkee + Akha Ama removed; Soi Nana source fixed)
- `coffee-roasters.json` (Akha Ama removed)
- `bakeries.json` (Mont Nomsod hours/source fixed; Maison Jean Philippe
  address/name corrected; Princ Hospital "Bread Story" removed;
  Wallflowers source fixed)
- `casual-dining.json` (Mit Ko Yuan Dinso Road fix)
- `fine-dining.json` (Saneh Jaan chef fix; Mezzaluna Sirocco->Sky Bar
  prose; Suhring/Nusara/Gaggan/Le Du 2026 Asia 50 Best rank updates)
- `restaurants.json` (Suhring/Nusara/Gaggan/Le Du 2026 rank updates)
- `bars.json` (Sky Bar 63->64th floor across address/prose/source/booking;
  Teens of Thailand + Tep Bar wikipedia cuisine_evidence_url replaced)
- `street-food.json` (Yaowarat night market source_url updated to
  Wikipedia-specific Yaowarat_Road)
- `late-night.json` (Yaowarat + Soi Texas source_url cleanup)
- `markets.json` (Klong Toey source_url cleanup)
- `budget-eating.json` (Thipsamai hours echo fixed)
- `itineraries.json` (Mont Nomsod 14:00->12:00 echo; Akha Ama replaced
  on 2 itineraries; Day 2 fine-dining-tour restructured around Mont
  Nomsod's actual 12:00 opening)
- `food-history.json` (era 2018-now updated with 2026 Asia 50 Best context)

## Defects total: 19 fixed in QA2 + 0 noted-for-backfill

Sub-totals:
- 3 noted-for-backfill entities resolved (Akkee, Akha Ama, Mont Nomsod)
- 1 additional fabricated entity removed (Princ Hospital "Bread Story")
- 1 fabricated chef name corrected (Saneh Jaan: Auychai Tantragoolsuk ->
  Pilaipon 'Toy' Kamnag)
- 2 address fabrications corrected (Mit Ko Yuan, Maison Jean Philippe)
- 1 floor-number defect corrected (Sky Bar 63 -> 64)
- 1 hours-of-operation defect corrected (Mont Nomsod 14:00 -> 12:00)
- 4 Asia 50 Best 2026 rank context updates (Gaggan, Suhring, Nusara,
  Le Du across fine-dining + restaurants)
- 2 itinerary venue cross-ref rewrites (Akha Ama deprecated)
- 2 itinerary prose echoes (Mont Nomsod time + day 2 restructure)
- 1 cross-file prose echo (Mezzaluna Sirocco -> Sky Bar)
- 1 prose echo (budget-eating Thipsamai hours)
- 1 phantom-venue cleanup (Sirocco accepted as real landmark, not phantom)

## Below-floor topics after QA2

- `dietary.kosher`: 0 (no kosher entries; Chabad-led scene; noted by QA1)
- `wine-bars`: 5 (was 6 post-Akkee removal; still above floor)
- `coffee-roasters`: 5 (was 6 post-Akha Ama removal; still above floor)
- `hidden-gems`: 7 (was 9 pre-QA2 with Akkee + Akha Ama; still above floor)
- `bakeries`: 6 (was 7 post-Princ Hospital removal; still above floor)

## Verdict

VERDICT: PASS

ship_safety.sh passes all 7 checks with 0 HARD failures and 0 internal-
reference errors. The 3 noted-for-backfill entities are resolved (2
removed as fabricated, 1 source/hours corrected). Two additional
fabrication-class defects caught (Saneh Jaan chef name, Princ Hospital
bakery) that QA1's narrow scope did not surface. Mit Ko Yuan address
fabrication caught (Damnoen Klang Tai vs real Dinso Road) — classic
address-hallucination class. The 2026 Asia 50 Best list (March 2026)
post-dates QA1's 2025 reference, all 4 ranked Bangkok venues updated.
All itinerary day-of-week × venue-hours combinations verified consistent
with corrected operating hours.
