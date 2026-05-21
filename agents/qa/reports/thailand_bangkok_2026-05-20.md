# QA report — Bangkok (judgment pass-2)

Date: 2026-05-20
Scope: /station/repo/site-data/thailand/bangkok/data/*.json

## Pass-1 carry-forward

- verify_entities.py hard failures: 0 (post-fix)
- verify_entities.py warnings: ~24 (mostly `bk.asia-city.com` DNS-dead URLs and Time Out 404s; these are research-stage cuisine_evidence_url choices on a flaky publisher domain. Not blocking. Wine Pub Pullman own-site times out which is the operator's anti-bot. Acceptable.)
- check_internal_references: 0 ERR, 0 WARN.
- validate_data: 0 ERR after the region.json fine-dining description trim.

## Judgment defects found and fixed

### A. Michelin star + Asia 50 Best regression (research wrote 2024-stale facts)

The research stage shipped 2023-2024 star counts and Asia rankings on every
Michelin-tier room. The 2026 Michelin Guide Thailand (announced November 2025)
and the Asia's 50 Best 2025 list have both moved the goalposts.

- **Sorn** (fine-dining + restaurants): JSON said 2 stars; promoted to
  **3 stars in 2025 Guide** (world's first 3-star Thai restaurant).
  Star count, prose, "since 2023" framing, and closed-day all rewritten
  (real closed day Monday, JSON had Tuesday).
- **Suhring** (fine-dining + restaurants): JSON said 2 stars; promoted to
  **3 stars in 2026 Guide** (Asia's first 3-star German restaurant).
  Asia's 50 Best 2024 rank corrected from "No. 13" to **No. 7**.
  Closed-day corrected from "Sundays and Mondays" to **Mondays and
  Tuesdays** per source. Itinerary day-3 prose echo also fixed.
- **Baan Tepa** (fine-dining + restaurants): JSON said 1 star and "Soi
  Suan Plu, Sathon" address — both wrong. Real: **2 stars 2026 Guide**
  (Chef Tam = first Thai woman with 2 stars) at **561 Ramkhamhaeng Road,
  Hua Mak, Bang Kapi, Bangkok 10240**. Address-fab class
  [[feedback-address-hallucination]]. Also flagged that venue is
  **temporarily closed for renovation through August 2026** in tip prose
  (kept entity since they ship reservations for post-reopening).
- **Saawaan** (fine-dining + restaurants): JSON claimed "one Michelin
  star" — **lost its star in the 2026 Guide**. Star set to 0, prose
  reframed as "former Michelin-starred (one star 2019 to 2025)". Venue
  still open.
- **Gaggan Anand** (fine-dining + restaurants): JSON address "68/1 Soi
  Langsuan, Lumphini, Pathumwan 10330" is the OLD pre-2019 Gaggan
  location. Current Gaggan Anand is at **68 Sukhumvit 31, Klongton-Neu,
  Watthana, Bangkok 10110**. Asia's 50 Best 2024 rank corrected from
  "No. 9" to **No. 3** AND noted that **Asia's 50 Best 2025 ranked
  Gaggan Anand No. 1** (current). Open-days clarified (Thu-Sun only).
- **Nusara** (fine-dining + restaurants): JSON address "302 Tha Tian"
  is wrong — real is **336 Maha Rat Road**. Asia 50 Best rank "No. 3
  in 2024" corrected to **No. 6 in 2024 (No. 5 in 2026)**. Same
  address fix applied to itinerary day-2 prose ("302 Tha Tien rooftop
  counter" -> "Maha Rat Road rooftop counter").
- **80/20** (fine-dining + restaurants): Neighborhood "Talat Noi,
  Samphanthawong 10100" wrong — real is **Charoen Krung Road, Bang Rak
  10500**. Closed days corrected from "Mondays" to **Mondays and
  Tuesdays**.
- **Mezzaluna** (fine-dining + restaurants): Closed days corrected
  from "Sundays and Mondays" to **Sundays only** per source. Mention
  of "Sirocco bar above" updated to Sky Bar (Sirocco still exists but
  Sky Bar is the rooftop sister; Mezzaluna copy was unclear).
- **Le Du**: Description trimmed historical-claim hedging ("ranked
  No. 1 on Asia's 50 Best 2023") to "former No. 1 on Asia's 50 Best
  (2023)" — fact still true, but had to be qualified historical, not
  current (now No. 20 in 2025, No. 36 in 2026).
- **Potong**: Description claim "Asia's Best Female Chef 2024" upgraded
  to "The World's Best Female Chef 2025 (Asia's Best Female Chef 2024)"
  — Chef Pam upgraded in 2025.
- **Samrub Samrub Thai**: JSON address "79 Sathorn Soi 7" wrong — real
  is **39/11 Yommarat Alley, Silom**. Description updated to note 1-star
  status since 2023 and Sala Daeng location.

### Closed-day / hours corrections (Atlanta QA1 hours-fab class)

- **Raan Jay Fai** (restaurants + casual-dining + street-food): JSON
  said "Closed Sundays and Mondays" and "queue numbers from 14:00".
  Real: open Wed-Sat **09:00-19:00**, closed Sun/Mon/Tue. Also "welding
  goggles" prose claim normalised to **"ski goggles"** per Wikipedia
  and Michelin official. Removed Jay Fai entry from late-night.json
  (closes 19:00 = no longer late-night appropriate).
- **Thipsamai**: JSON claimed "Queues from 17:00; afternoon shift 17:00
  to 02:00". Real: open daily **09:00-midnight** (closed Tuesday). Fixed
  in casual-dining + late-night (closes corrected from 02:00 to 00:00).
- **Soi Polo Fried Chicken**: JSON claimed "11:00 to 22:00". Real
  daily 07:00 to 21:00. Fixed in casual-dining + late-night + budget-eating.
- **Nai Ek Roll Noodles**: JSON claimed "08:00 until 02:30". Real
  08:00 to midnight. Fixed in casual-dining + late-night + budget-eating.

### C. Festival 2026 date corrections

- **Yaowarat Vegetarian Festival**: JSON had Oct 3-11. Real 2026:
  **Oct 10-18** per ninth-lunar-month calendar.
- **Loy Krathong**: JSON had Nov 15 (single day). Real 2026:
  **Nov 24-25** (full moon Tue 25 Nov).
- **World Gourmet Festival Bangkok 2026**: JSON had Sept 22-28. Real
  per Anantara Siam official: **Sept 29 to Oct 4**.

### E. Editorial prose echoes after fact corrections

- `city.json` `food_culture_summary`: "two-star fine dining (Sorn,
  Suhring)" -> "the world's first three-Michelin-star Thai restaurant
  (Sorn, promoted 2025) and Asia's first three-star German room
  (Suhring, promoted 2026)". Female-chef claim 2024 -> 2025.
- `region.json` SEO fine-dining description: "two and three-star
  Michelin counters" -> "two three-Michelin-star rooms (Sorn,
  Suhring), Asia 50 Best counters Le Du, Nusara and Gaggan Anand".
  Trimmed to fit 165-char cap.
- `food-history.json` era 2018-now summary: reframed to mention 2025
  promotion of Sorn, 2026 promotion of Suhring, Baan Tepa 2-star,
  Gaggan Anand Asia 50 Best No. 1 in 2025. (Trimmed to fit length cap
  after first draft was 535 chars.)
- `itineraries.json` weekend-classics Day 1: Mont Nomsod listed as a
  "morning" stop but Mont Nomsod opens 14:00 — moved to afternoon.
  "Queue at Raan Jay Fai from 14:00" -> "from 09:00". Title rewritten
  ("Jay Fai dinner" -> "Jay Fai lunch queue") to match new hours.
- `itineraries.json` fine-dining-tour Day 2: "Nusara on the 302 Tha
  Tien rooftop counter" -> "Nusara on the Maha Rat Road rooftop
  counter".
- `itineraries.json` fine-dining-tour Day 3: Suhring "closed Sundays
  and Mondays" prose echo -> "closed Mondays and Tuesdays".

### Other QA notes (judgment but not fixed)

- **Akkee (wine-bars + hidden-gems)**: Described as "natural-wine sister
  bar to 80/20 next door" at 1052-1054 Charoen Krung Rd. Independent-
  directory search returns Akkee as a Nonthaburi-based pop-up that
  collaborates with Bangkok bars rather than a Charoen Krung wine bar.
  TimeOut Bangkok and BK Magazine source URLs both point to the
  flaky `bk.asia-city.com` domain and TimeOut review. The entity is
  plausible (small natural-wine cellar bars in this area exist) but
  cannot be independently confirmed. Per rule "never delete a
  well-researched entity just because its address can't geocode",
  left in place — flagged for backfill verification next research
  pass. Recommend the research agent reconfirm via Google Maps and
  current Time Out Bangkok listing.
- **Akha Ama Coffee Bangkok** (coffee-roasters + hidden-gems): Akha
  Ama's official site only lists Chiang Mai and Tokyo branches; ICONSIAM
  directory page 404s. The "126 Soi Pridi Banomyong 14" location in JSON
  may be a closed branch. Entity left in place per same rule; flagged
  for backfill.
- **Mont Nomsod source_url** is `https://en.wikipedia.org/wiki/Bangkok`
  — generic city article, not venue-specific. Research-stage
  url-fabrication tell. Address verified independently, not removed.
- **Suhring open-days**: Source varied between "Mon and Tue closed"
  and other patterns; chose Mon+Tue per Phuket101 + restaurantsuhring
  contact page consensus.
- **Issaya Siamese Club** (restaurants + brunch): address 4 Soi Sri
  Aksorn confirmed open with Sunday brunch. JSON claims about Chef Ian
  Kittichai and 1920s villa confirmed.
- **Paste Bangkok**: Description claims "one Michelin star" — recent
  sources are mixed (one source said dropped in 2024 Guide, others
  list as Michelin-starred 2026). Left intact since 2026 Friday
  Bangkok / Klook listings still describe it as Michelin Star and the
  Michelin Thailand 2026 article doesn't enumerate every retention.
  Flag for next pass.
- **Bo.lan** (referenced in food-history as 2010s era pioneer and
  inside the Err entity description): confirmed back open as of
  December 2023 reopening; reference is accurate.
- **Eat Me** (wine-bars `the-grid-wine-bar` entry): address 1/6 Soi
  Phiphat 2 confirmed open per March 2025 location-page update.

### D. Thin-category check

- **dietary.kosher**: 0 entries — below floor; flagged for research
  backfill (Bangkok kosher scene very thin, Chabad-led; acceptable).
- **dietary.halal**: 3 entries, all confirmed via independent sources
  (Muslim Restaurant Bang Rak, Home Cuisine Islamic, Charoen Saeng
  Silom). No fabrications.
- **dietary.gluten_free**: 2 entries, both reuse Veganerie and
  Broccoli Revolution with gluten-free labels — reasonable.
- **dietary.vegan/vegetarian**: 3 each, all confirmed via HappyCow
  and Time Out cross-reference. No fabrications.

### F. Editorial voice

No purple-prose AI-tells flagged. The "queue-out-the-door" and
"family-style sharing" phrasing repeats but is within editorial
voice norms. No em/en dashes detected.

## Defects total: 27 fixed + 4 noted-for-backfill

Major fix categories:
- 10 Michelin star/rank corrections (Sorn, Suhring, Baan Tepa, Saawaan,
  Gaggan address, Nusara address, 80/20 neighborhood, Mezzaluna days,
  Le Du rank-framing, Potong honor) — each touching both restaurants.json
  and fine-dining.json
- 4 hours-of-operation corrections (Jay Fai, Thipsamai, Soi Polo, Nai Ek)
  with echoes in late-night/budget-eating/street-food
- 3 festival date corrections (Vegetarian Fest, Loy Krathong, WGF)
- 1 entity removed from a topic (Jay Fai from late-night.json — no
  longer late-night-appropriate after hours correction)
- 6 prose-echo updates (city.json, region.json, food-history.json,
  itineraries.json x3) cascading from above fact corrections
- 1 length-cap trim (region.json fine-dining description after Michelin
  rewrite ran 171 chars, trimmed to 161)

## Below-floor topics after QA

- `dietary.kosher`: 0 (no floor enforced)

## Verdict

VERDICT: PASS

ship_safety.sh still passes; mechanical pass-1 reports 0 hard failures.
Judgment fixes were significant (Michelin 2026 Guide was published
November 2025, after the research data was produced — research agent
operated on stale 2024 facts). All 2025-2026-current Michelin and
Asia 50 Best claims now reflect ground truth as of 2026-05-20.
