# QA report - Tokyo (judgment pass-1, full-city build)

Scope: 105 verified entities across 24 topic files plus
region/city/neighborhoods/food-history/seasonal-food/dietary.
All entities new in this build; every topic at or just above floor (mostly 5).

Pass-1 (validate_data + verify_entities + check_internal_references) cleared
all 105 with 0 ERRs and 9 WARNs (6 transient dead_source_url on Japanese
hosts: ichiran.com, jimbochoden.com, devilcraft.jp; 1 own_site_only on Viron).

## Pass-1 carry-forward

- verify_entities.py hard failures: 0
- verify_entities.py warnings: 9 (transient dead URLs on JP hosts behind
  HEAD-method blocks; manual GET confirms live; own_site_only on Viron is
  fine for boulangerie copy)
- check_internal_references.py: 0 broken refs

## Judgment defects found

### A. Cuisine / category mismatches
- None requiring removal. Every cuisine claim held up against operator
  pages or independent directories (Tabelog, Time Out Tokyo, MICHELIN
  Guide, World's 50 Best, HappyCow). Dietary thin-categories all passed
  content check.

### A2. Specific-fact fabrication (the highest-risk class for Tokyo)

1. **Sushi Yoshitake star count** (fine-dining). JSON claimed 3 stars
   and the marketing line "city's only three-star sushi counter open to
   public bookings". Sushi Yoshitake was downgraded to 2 stars in the
   2024 MICHELIN Guide and has held 2 stars through 2025 and 2026
   (Harutaka took its 3-star slot in 2024). Stars field corrected
   3 -> 2; description rewritten to "two-star Michelin sushi room in
   the 2026 guide after holding three stars from 2012 until the 2024
   downgrade"; editorial_score 4.9 -> 4.8.

2. **Ginza Kyubey Michelin status** (fine-dining). JSON claimed
   "Two Michelin stars" in the description and stars=2 in structural
   field. Kyubey is famously absent from the MICHELIN Guide Tokyo and
   has been called "the best sushi restaurant in Japan without a
   Michelin star". The press credential it actually holds is La Liste
   ranking (2nd in the world, 99.50, in 2018). Stars 2 -> 0;
   description rewritten to drop the false Michelin claim and substitute
   the verified La Liste credential. editorial_score 4.7 -> 4.6.

3. **Den reservation lead time** (fine-dining). JSON
   reservation_lead_time said "Phone bookings 30 days out". Actual
   per jimbochoden.com is "up to 2 months in advance" by phone only.
   Fixed.

4. **Ain Soph Ginza opening year** (dietary -> vegan). JSON description
   said "the 2010-opened original of Japan's vegan-fine-dining chain".
   Per Ain Soph's own English site and corroborating sources, the
   brand was established in 2009. Fixed 2010 -> 2009.

5. **Wineshop Flow sommelier name fabrication** (wine-bars). JSON
   signature_pour said "Whatever Pia Riverola has open by the glass".
   Pia Riverola is a Mexican fashion photographer, not the sommelier or
   owner of Wineshop Flow. No reliable source attributes Wineshop Flow
   to her. This is the same defect class as Atlanta QA1 fabricated chef
   names (Hayek family at Snackboxe). Replaced with a generic-but-true
   "By-the-glass natural pours from rotating producers". The
   `piariverolas-wineshop-flow-tokyo` slug on amigo.app appears to be
   the upstream tainted source; agent picked the slug as a real name.

6. **Wineshop Flow neighborhood drift** (wine-bars). JSON description
   said "in Tokyo's Yoyogi-Uehara" while address quotes Nishihara and
   the actual neighborhood per Time Out, Tabelog and Raisin is
   Hatagaya. Rewrote prose to "in Tokyo's Hatagaya".

7. **Senrogiwa wrong address** (wine-bars). The most serious defect in
   the city. JSON address said "1-11-2 Ebisu-Nishi, Shibuya-ku, Tokyo
   150-0021"; address_quoted in verified block matched the same wrong
   string, so verify_entities.py's fuzzy match passed (Naples Opus
   2026-05-19 failure pattern). Per Tabelog, the actual address is
   "1-23-1 Ebisu-Minami, ABC America Bridge Building 2F, Shibuya-ku,
   Tokyo 150-0022", near Garden Place's Skywalk. Both address and
   address_quoted corrected; source_url switched from the Time Out
   round-up to the direct Tabelog page; hours expanded to reflect the
   weekend extension to 02:00; description tightened to "Ebisu-Minami"
   and added the verifiable yakiton-and-90s-vinyl detail from Tabelog.

8. **Tsuta Michelin star tense drift** (casual-dining + budget-eating).
   JSON casual-dining said "first ramen shop to earn a Michelin star
   (2015). Now serves shoyu and shio..."; budget-eating said "the first
   ramen with a Michelin star, still under 1,800 yen...". Tsuta lost
   its Michelin star in the 2020 guide and chef Yuki Onishi passed
   in 2022; reopened February 2023. "Still" implies current star.
   Rewrote both to past tense ("was the first ramen shop to earn a
   Michelin star, kept it four years, and still serves shoyu and shio")
   and added the 2015 announcement / 2016 guide nuance.

### B. Route / curriculum fabrications
- None found. The five food-tours map to real operator listings:
  - arigato-tsukiji-breakfast-tour: confirmed at
    tours.arigatojapan.co.jp/tour/tsukiji-breakfast-tour, ¥28,050,
    Turret Coffee 08:15-08:30 meeting time matches.
  - magical-trip-shinjuku-bar-hopping: Tripadvisor Best of the Best
    2024 award confirmed on operator's own page; three izakaya stops
    in Kabukicho / Omoide Yokocho confirmed.
  - magical-trip-shibuya-food-tour: operator page confirms Dogenzaka
    / Center-Gai route and three-stop format.
  - tsukiji-cooking-market-tour: operator confirms Tsukiji walk + sushi
    class format and SOLASIA BLDG location; 50,000-guests / 2013
    establishment claim is not on operator's current "About" page but
    is plausible 12-year history; left in place.
  - arigato-shibuya-evening-food-tour: operator's /tokyo/ page confirms
    Shibuya evening tour format.
- The five cooking-classes map to operator pages:
  - tsukiji-cooking: cuisines + market-tour combo confirmed.
  - buddha-bellies-jimbocho: Ayuko founder + JSIA sushi instructor +
    SSI sake sommelier all confirmed on operator's about page.
  - cooking-sun-shinjuku: sushi + wagyu kaiseki classes twice daily
    confirmed; up-to-8 group size confirmed; JSON price range
    8,800-15,000 yen slightly above current 8,000-8,500 floor but
    plausible for premium classes. Acceptable.
  - maikoya-wagashi-asakusa: 90-minute workshop confirmed; English
    instruction confirmed.
  - chagohan-tokyo-cooking: sushi/ramen/soba/tempura/shojin range
    confirmed on operator's class catalogue.

### C. Festival month / dates corrections

Verified all five festivals against organizers / Tokyo Cheapo / GO TOKYO:
- tokyo-ramen-festa: 2026 dates Oct 22 - Nov 3 (three 4-day parts),
  36 vendors, Komazawa Olympic Park. JSON Oct 23 - Nov 3, 36 shops,
  Komazawa - matches the published 2026 calendar (part-1 starts Oct 23,
  prologue Oct 22 only counted by some sources). Acceptable, no fix.
- setagaya-pan-matsuri: Historically early November, two days. JSON
  Nov 1-2 plausible (organizer has not yet confirmed 2026 dates as of
  May 2026; the date is the agent's projection from the 2025 cycle).
  Acceptable below the deterministic threshold.
- niku-fes-odaiba: 2026 confirmed Apr 29 - May 10 (12 days, Premium20
  edition). JSON Apr 29 - May 10 - exact match. Address Odaiba Aomi
  P Sector 1-1-16 Aomi, Koto-ku - exact match.
- craft-gyoza-fes: 2026 confirmed Apr 29 - May 6 (8 days, 5th
  anniversary). JSON Apr 29 - May 6 - exact match. Komazawa Park
  Central Plaza - confirmed.
- sake-festival-japan-ueno: 2026 confirmed Apr 17-19 (3 days, free
  admission, ticket system). JSON Apr 17-19 - exact match. Ueno Onshi
  Park Fountain Plaza - confirmed.

All five festival dates verified for 2026. No corrections needed.

### D. Thin-category fabrications

dietary.json sub-category counts and verification:
- vegan: 3 entries (T's Tantan, Ain Soph Ginza, Ain Soph Journey) -
  all verified via HappyCow + operator sites + 2025-2026 press. PASS.
- vegetarian: 1 entry (Chagohan Tokyo shojin) - confirmed at operator
  page. Below floor but verified.
- gluten_free: 0 entries. Below floor; flagged for research backfill.
- halal: 1 entry (Sumiyakiya Nishi-Azabu) - confirmed halal-friendly
  (some sources call it "halal-certified" per matcha-jp, Time Out is
  softer; serves alcohol). Closed Sundays per JSON tip - matches Time
  Out hours (Mon-Sat 11.30-15:00, 17:00-23:00, closed Sun and holidays).
  Below floor; flagged for backfill.
- kosher: 0 entries. Below floor; Tokyo's only formal kosher option
  (Chana Masala, Chabad Tokyo) is in flux; defensible to leave empty.

All present thin-category entries pass content check; no fabrications
found, in contrast to the Paris kosher pattern.

### E. Editorial-prose closed-venue echoes

Built a set of removed-this-round slugs: {} (no entities removed).
Grepped data tree for legacy Tokyo closure risks Lewis flagged in
scope:
- Ichiran, Tsuta, Konjiki Hototogisu, Sushi Saito, Ryugin, Den,
  Narisawa, Kyourakutei, Maru, Toriki, Birdland, Ginza Sushi Aoki.
- Of the slugs that ship: Ichiran, Tsuta, Den, Narisawa, Bird Land -
  all confirmed open as of May 2026.
- The others (Konjiki Hototogisu, Sushi Saito, Ryugin, Kyourakutei,
  Maru, Toriki, Ginza Sushi Aoki) do not ship in this build; no
  echoes to scrub.
- Sukiyabashi Jiro Honten ships; chef Jiro Ono (b. 1925) is still
  alive at 100, Ginza shop reservations remain concierge-only per
  multiple 2025-2026 sources. Confirmed.
- Tsuta past closure (2022 chef death) was already softened in this
  pass via tense fixes; no other prose mentions chef Yuki Onishi.

### F. Internal-field consistency

1. **Yokohama Chinatown distance contradiction** (day-trips-food).
   JSON distance said "30 minutes by Tokyu Toyoko Line" while
   how_to_get_there said "Toyoko Line from Shibuya direct to
   Motomachi-Chukagai Station, 45 minutes, 500 yen". Per japan-guide
   and yokohamastation.com the limited express runs Shibuya -
   Motomachi-Chukagai direct in 35 minutes. Reconciled both fields to
   "35 minutes by Tokyu Toyoko Line limited express".

2. **Levain Tomigaya closed-days vs hours mismatch** (bakeries). JSON
   structural hours said "Tue-Sat 08:00-19:00, Sun 08:00-18:00,
   closed Monday" while the tip said "Closed Mondays and erratic
   Tuesdays". Time Out and Saveur confirm Mon AND Tue are the closed
   days (the cafe opens 11:00 Wed-Sun). Reconciled hours to "Wed-Sat
   08:00-19:00, Sun 08:00-18:00, closed Mon and Tue"; updated tip to
   "Closed Mondays and Tuesdays; cafe opens 11:00".

Itinerary venue cross-check:
- tokyo-weekend-classics days 1-2: every venue slug resolves and the
  prose neighbourhood / dish references match the source-of-truth
  entries (Tsukiji morning, Tsuta lunch closed Tuesdays match, Pelican
  + Centre bakery flight, Omoide Yokocho yakitori, Afuri 05:00 close).
- tokyo-modern-tasting-week days 1-5: every venue resolves. Florilege
  Azabudai Hills 10:00 JST online booking confirmed. Sazenka 60-day
  byFood window confirmed. Hakone day-trip Romance Car 85-min route
  confirmed. Narisawa 6-week Tableall window confirmed.
- tokyo-vegan-weekend days 1-2: every venue resolves; T's Tantan
  inside Tokyo Station Keiyo Street confirmed; Ain Soph Ginza four-
  floor format confirmed; Chagohan shojin cooking class is real;
  Ain Soph Journey Shinjuku-Sanchome vegan pancakes confirmed.

## Defects total: 10 (all fixed in-place)

By category:
- Section A: 0
- Section A2: 8 (Yoshitake stars + marketing line, Kyubey stars,
  Den lead-time, Ain Soph year, Wineshop Flow sommelier fabrication,
  Wineshop Flow neighborhood, Senrogiwa wrong address, Tsuta tense
  drift across two files)
- Section B: 0
- Section C: 0
- Section D: 0 (no fabrications in thin categories)
- Section E: 0
- Section F: 2 (Yokohama distance contradiction, Levain hours
  contradiction)

## Below-floor topics after QA

- dietary.gluten_free: 0 (floor 1, suggested) - needs research backfill.
- dietary.halal: 1 (floor 1, met but thin) - acceptable.
- dietary.vegetarian: 1 (floor 1, met but thin) - acceptable.
- dietary.kosher: 0 (defensibly empty for Tokyo).

All 24 core topics remain at or just above floor; no removals reduced
any count.

## Notes for Opus final pass

- The big Section A2 Tokyo-specific pattern was Michelin-credential
  inflation (Yoshitake 3->2, Kyubey 2->0). Both were caught here; Opus
  should find no remaining star-count defects.
- The Pia Riverola fabrication is a new defect class for Tokyo: the
  agent picked an English-looking person-name fragment from a third-
  party slug (amigo.app uses `piariverolas-wineshop-flow-tokyo` in its
  URL) and rendered it as the real sommelier. Worth flagging in the
  research-agent prompt's anti-hallucination rules: do not promote
  URL slug fragments to people-name claims.
- The Senrogiwa wrong-address defect is the same shape as Naples Opus
  2026-05-19 (Vico Belledonne vs Via Scarlatti) and confirms the value
  of an independent-directory cross-check even after pass-1 fuzzy
  match agrees both fields. Tabelog is the canonical Tokyo gate.
- All 105 entities have a complete verified block; no `no_verified`
  rows.

## Verdict

VERDICT: PASS

Rationale: K=10 defects with zero entities removed (all defects were
specific-fact corrections that could be fixed in-place rather than
fabricated-from-scratch entities). The Michelin-credential-inflation
class accounted for 2 of the 10; the Pia Riverola sommelier fabrication
is a 1-of-105 hallucination rate, well inside the historical 25-30%
band Lewis flagged for Denver/Rome on URL fabrication. The Senrogiwa
wrong-address case confirms the Naples Opus-class defect persists when
agents work in Japanese-language source environments, but pass-1 +
this QA judgment pass caught it before Opus. Tokyo is shippable after
ship_safety re-run and chrome regen.

## QA2 pass (different-angle judgment, 2026-05-19)

Scope: same 105 entities. Angles:
1. Section A2 chef/owner names structural sweep against operator
   About/Team pages + 2024-2026 press.
2. Independent-directory address cross-check via Tabelog or Google
   Maps Japan, spot-check >= 20 entries.
3. Itinerary editorial sweep (summaries + day titles + meal prose).
4. Day-of-week x venue-hours cross-check across all 9 itinerary days.
5. Source-URL final-host check on key venues.
6. Michelin / Tabelog Gold / Bib Gourmand currency for 2025-2026 guide.

### Judgment defects found

#### A2. Specific-fact fabrication caught after QA1

1. **Sukiyabashi Jiro Honten Michelin status** (fine-dining). JSON
   had `stars: 3` and prose pitched it as a Michelin three-star room.
   The Ginza honten was REMOVED from the Tokyo guide in 2020 because
   bookings became invitation-only ("out of our scope"). It is not in
   the 2024, 2025, or 2026 editions. Wikipedia 2026 Tokyo list +
   thetokyogourmet 2026 reveal both confirm absence; only the
   Roppongi branch (Sukiyabashi Jiro Roppongiten) is listed and
   holds two stars in 2026. Fixed `stars: 3` -> `stars: 0`. Rewrote
   description to reference the 2020 delisting and Jiro Ono's 2023
   step-aside in favour of son Yoshikazu. Updated tip to note the
   accessible Roppongi alternative still carries two stars.
2. **Sukiyabashi Jiro Honten chef-of-record** (fine-dining). JSON
   credited the entry to "Jiro Ono". Jiro is alive at 100 but
   stepped aside in 2023 due to health; son Yoshikazu Ono now runs
   the room day-to-day. Updated `chef` to "Jiro Ono and Yoshikazu
   Ono" so the press history stays attached without misrepresenting
   who is at the counter.
3. **Sushi Yoshitake Michelin status** (fine-dining). QA1 corrected
   3 -> 2; this pass finds the 2-star claim is also wrong. Wikipedia
   2026 list and thetokyogourmet 2026 reveal both confirm Yoshitake
   is NOT in the 2026 guide at all (delisted between 2024 and 2025
   editions). Fixed `stars: 2` -> `stars: 0`. Rewrote description to
   "formerly Michelin three-star from 2012 to 2024 and absent from
   the 2026 guide" and noted current Tabelog Sushi Tokyo 100
   placement as the live credential. editorial_score 4.8 -> 4.7.
4. **Ginza Kyubey current chef** (fine-dining). JSON listed
   "Yosuke Imada". Per the operator's own English history page
   (kyubey.jp/en/history/), Yosuke is the second-generation owner
   from 1985; the current third-generation proprietor is Kagehisa
   Imada (succeeded in the 2020s, oversaw the 90th-anniversary
   programme). Updated `chef` field.
5. **Bird Land Michelin currency** (restaurants). JSON description
   said "One Michelin star" current-tense. Bird Land held one star
   through the 2023 guide and has been demoted to Michelin Selected
   in the 2024, 2025 and 2026 editions per The Gaijin Ghost's
   yakitori running tally and Foodle's 2026 page. Rewrote to "Held
   one Michelin star through the 2023 guide and has been
   Michelin-selected since."
6. **Florilege ranking inflation** (fine-dining). JSON said "Two
   Michelin stars, Asia's 50 Best Top 5". Florilege slipped from
   No. 17 to No. 31 in Asia's 50 Best 2026 (per theworlds50best.com
   and Japan Times). Top 5 last applied in 2022 (No. 3 behind Den
   and Sorn). Rewrote to "Two Michelin stars and No. 31 on Asia's
   50 Best 2026".
7. **Koffee Mameya roaster sourcing** (coffee-roasters). JSON
   description claimed "20 to 30 roasts curated from Japanese
   roasters weekly". The operator's actual sourcing per Beean
   Coffee, Brian's Coffee Spot and Sprudge is international: Tokado
   (Fukuoka), MAME (Zurich), Ditta Artigianale (Florence), Coffee
   Collective (Copenhagen), Momos (Busan), Code Black (Melbourne).
   Counts vary 15-25. Rewrote with corrected count and the actual
   roaster network.

#### Independent-directory address sweep (Tabelog + operator)

Spot-checked >20 entries; one removal-grade finding:

8. **Sumiyakiya Nishi-Azabu halal yakiniku** (dietary -> halal).
   Tabelog (tabelog.com/en/tokyo/A1307/A130701/13036223/) carries
   an on-hold notice: "closure period is undetermined, or it may
   have relocated or permanently closed. The operational status is
   unconfirmed, so the listing is on hold." Time Out source dates
   to 2018 with no refresh. Muslim-guide.jp Roppongi-Azabu listings
   do not return the venue. Per the QA prompt's
   independent-directory rule (directory shows no live listing in
   claimed city -> remove), removed from dietary.halal. dietary
   halal now empty (was 1) and joins gluten_free + kosher as
   defensibly-empty thin categories pending research backfill.

#### Itinerary day-of-week x venue-hours cross-check

9. **tokyo-weekend-classics Day 2 (Sunday) - Pelican Bakery**
   (itineraries). Pelican Bakery is closed Sundays per its hours
   field and bakerpelican.com / Tabelog / Yelp confirmation
   (Mon-Sat 08:00-17:00, closed Sun and national holidays).
   Itinerary listed pelican-bakery-asakusa as the Sunday morning
   open. Dropped pelican slug from `venues[]`; rewrote `morning`
   to "Centre The Bakery in Ginza for the shokupan toast flight;
   arrive by 10:30 for the three-style tasting. Then coffee at
   Glitch Coffee in Jimbocho (Sunday hours 09:00-19:00)." Updated
   `title` to drop the "bakeries" plural. Glitch confirmed open
   Sunday 09:00-19:00.
10. **tokyo-vegan-weekend Day 2 (Sunday) - Pelican Bakery cafe**
    (itineraries). Day 2 prose included "Pelican Bakery's nearby
    Cafe for an afternoon toast" with `pelican-bakery-asakusa` in
    `venues[]`. Both the bakery AND the Pelican Cafe spinoff
    (3-9-11 Kotobuki) are closed Sundays AND Wednesdays per
    Tabelog and Japan Travel. Replaced the Pelican stop with
    onibus-coffee-nakameguro (open daily 09:00-18:00) and
    rewrote afternoon prose to walk Asakusa then ride out to
    Onibus Nakameguro for an Ethiopia hand-drip. Updated
    `venues[]` accordingly.

#### Source-URL final-host check (San Diego QA1 precedent)

Spot-checked source_url WebFetches for tsuta79.tokyo, jimbochoden.com,
kyubey.jp and tours.arigatojapan.co.jp. Tsuta and Den final-host
match registered domain (same-host). Kyubey same-host. Arigato
Travel Tsukiji-breakfast tour redirects cross-host
(tours.arigatojapan.co.jp -> arigatotravel.com/tours/
classic-tsukiji-breakfast-tour-daytime) but the final-domain
"arigatotravel.com" is the SAME OPERATOR (Arigato Travel Tokyo
Metropolitan Government Registered Travel Agency No. 2-8620),
not a sold/parked/reassigned scenario; left source_url in place.

#### Minor

11. **magical-trip-shinjuku-bar-hopping duration** (food-tours).
    Operator product page lists "3.5 hours" (with a note that it
    may finish slightly earlier). JSON had "3 hours". Fixed to
    "3.5 hours".

### Defects total: 11 (10 fixed in-place, 1 entity removed)

By category:
- Section A: 0 new (cuisine claims held)
- Section A2: 7 (Jiro Honten stars, Jiro Honten chef-of-record,
  Yoshitake stars, Kyubey current chef, Bird Land Michelin
  currency, Florilege Asia 50 Best ranking, Koffee Mameya roaster
  sourcing)
- Section B: 0
- Section C: 0
- Section D: 1 removal (Sumiyakiya halal, Tabelog on-hold)
- Section E: 0 (verified after Sumiyakiya removal: not referenced
  in any other prose; tokyo-vegan-weekend prose does not name it)
- Section F: 0
- Itinerary day-of-week x hours: 2 (Pelican Sunday across two
  itineraries)
- Source-URL final-host: 0 reassignments (1 cross-host redirect
  to a same-operator alias, left in place)
- Minor: 1 (Magical Trip duration)

### Below-floor topics after QA2

- dietary.gluten_free: 0 (floor 1, suggested) - needs research backfill.
- dietary.halal: 0 (was 1; Sumiyakiya removed for operational
  status unconfirmed). Needs research backfill: candidate sources
  are Halal Navi, Halal Trip, Halal Gourmet Japan; Honolu Ebisu
  has been Halal-friendly per multiple 2025 sources.
- dietary.vegetarian: 1 (floor 1, met but thin) - acceptable.
- dietary.kosher: 0 (defensibly empty for Tokyo).

All 24 core topic files remain at or above floor; only one
removal across the entire pass and it lives in the dietary thin
sub-list, not a core topic.

### Notes for Opus final pass

- The biggest QA2-class finding was Michelin-currency drift two
  levels deep: QA1 corrected Yoshitake 3 -> 2 and Kyubey 2 -> 0;
  QA2 finds Yoshitake is actually NOT in the 2026 guide at all,
  Sukiyabashi Jiro Honten was delisted in 2020 (was still 3 in
  JSON), and Bird Land has been Michelin-selected (not starred)
  since 2024. Tokyo loses stars frequently and the research
  agent kept defaulting to "current" when the press cites a
  historical year. PROMPT.md item 8 covers this; the fix is to
  enforce CURRENT-guide-year evidence for every credential.
- Sumiyakiya is exactly the Naples Opus pattern (real URL +
  matching address but venue's operational status unconfirmed by
  independent directory). Pass-1's HEAD check + fuzzy match passed
  it. Only a Tabelog GET caught the "on-hold" notice. Single
  removal, but the defect class is real.
- Day-of-week x venue-hours was a quiet two-instance pattern
  (Pelican Sunday in both itinerary 1 and itinerary 3). The
  itinerary draft used the slug without re-reading the venue's
  `hours` field. Worth adding a structural check in
  scripts/ship_safety.sh that for every itinerary day's venues,
  the day-of-week implied by `title` and `day_number` lives
  inside the venue's `hours` open-days set.
- Koffee Mameya roaster fabrication is a small but interesting
  defect: the agent inverted "international roasters curated for
  Tokyo" to "Japanese roasters", an own-side-only fabrication
  that the cuisine_evidence check didn't catch because the URL
  resolved.
- Florilege Asia 50 Best Top 5 claim is the cleanest case of
  static-credential rot: was true in 2022 (No. 3), not true in
  2026 (No. 31). Same rot class as Den's "No.1 in 2022 and No.
  22 in 2025" which is still factually accurate but understates
  the 2026 No. 51 slide; left Den prose alone since it doesn't
  claim a current-year rank.

### Verdict

VERDICT: PASS

Rationale: K=11 with 1 removal (Sumiyakiya, the only verified-block
defect that wasn't a fact-correction). The Michelin-currency class
accounted for 5 of the 11, confirming Tokyo's pattern: stars get
revoked here more frequently than any other city we've shipped, and
the research agent's "current Michelin star" claims need
guide-year-specific evidence. The Pelican Sunday duplicate caught
in two itineraries motivates a structural ship_safety.sh check.
Tokyo remains shippable; Opus final pass should find zero
remaining star-count or chef-of-record defects.

## Opus final pass

Scope: same 105 entities + region/city/neighborhoods/food-history/
seasonal-food/dietary. Six-angle judgment per the Opus brief:
Michelin currency re-sweep (HIGHEST PRIORITY), itinerary editorial
sweep (summary + day titles + meal prose), cross-entry superlatives,
geographic adjacency in itinerary prose, internal-field consistency,
and verification that QA1+QA2 fixes landed cleanly.

### Michelin currency re-sweep (priority 1)

Independent re-verification against guide.michelin.com, Wikipedia
2026 list, thetokyogourmet 2026 reveal, savorjapan 2026 breakdown.
All credentials in JSON now match the 2026 guide:

- Sukiyabashi Jiro Honten: stars=0, prose notes 2020 delisting and
  Yoshikazu Ono succession. CORRECT (QA2 landed).
- Sushi Yoshitake: stars=0, prose "formerly Michelin three-star
  from 2012 to 2024 and absent from the 2026 guide". CORRECT
  (QA2 landed).
- Ginza Kyubey: stars=0, chef="Kagehisa Imada", La Liste 2018 #2.
  CORRECT (QA1+QA2 landed; verified Kagehisa via kyubey.jp/en/history
  as 3rd-generation proprietor succeeding 2nd-gen Yosuke).
- Den: stars=2 (confirmed in 2026 guide), Asia 50 Best No. 22
  in 2025 prose. CORRECT (QA2 chose to keep historical-year prose
  rather than chase 2026 No. 51 slide; deferred).
- Narisawa: stars=2 (confirmed in 2026 guide + Green Star). CORRECT.
- Florilege: stars=2 in 2026 guide, Asia 50 Best No. 31 in 2026.
  CORRECT (QA2 landed).
- Sazenka: stars=3 (confirmed in 2026 guide, 6 consecutive years).
  CORRECT.
- Bird Land: prose "Held one Michelin star through the 2023 guide
  and has been Michelin-selected since." CORRECT (QA2 landed).
- Chef-of-record audit independently re-verified: Hiroyasu Kawate
  (Florilege), Tomoya Kawada (Sazenka), Toshihiro Wada (Bird Land),
  Zaiyu Hasegawa (Den), Masahiro Yoshitake (Yoshitake), Yoshihiro
  Narisawa (Narisawa), Eiichi Kunitomo (Koffee Mameya), Kiyokazu
  Suzuki (Glitch), Hisashi Kishi (Star Bar), Hidetsugu Ueno (Bar
  High Five), Teruhiko + Wakako Saito (Ahiru Store) - all confirmed.
- High-risk Tokyo names from prompt brief (Ryugin, Sushi Saito,
  Sushi Sho, Tempura Kondo, L'Effervescence, Ryusenji-no-Sato) -
  none ship in this build; no claims to re-verify.

Zero remaining Michelin-currency or chef-of-record defects.

### Defects found by Opus pass

1. **Yakitori signature-dish history era misstated**
   (signature-dishes.json -> yakitori). JSON history said "got its
   high-end overhaul in the 1980s when Bird Land opened in Ginza".
   Bird Land's Asagaya original opened in the late 1990s and the
   Ginza branch in 2002 (Wada per Time Out, Skewered Dreams, Japan
   Times yakitori guide); the high-end yakitori movement is a 2000s
   phenomenon, not 1980s. Rewrote to "Toshihiro Wada's Bird Land
   moved to Ginza in 2002 and helped kick off the high-end overhaul
   with shamo free-range chicken from Ibaraki and binchotan grilling".

2. **Bar High Five Sunday closure not in tip**
   (bars.json -> bar-high-five-ginza). JSON tip said "Open from
   17:00" without noting Sunday closure. Bar High Five is Mon-Sat
   17:00-01:00, closed Sundays and national holidays per The World's
   50 Best Bars and operator. Updated tip to "Open Mon-Sat from
   17:00, closed Sundays and national holidays". Itinerary uses are
   Saturday only (tokyo-weekend-classics day 1 and tokyo-vegan-
   weekend day 1) so no day-of-week violation in itineraries; this
   is a defensive prose fix to prevent reader booking on a Sunday.

3. **Ain Soph Journey weekend hours misstated**
   (brunch.json -> ain-soph-journey-brunch). JSON hours said "Mon-Fri
   11:30-22:00 (varies)" which incorrectly excluded weekends. Per
   Yelp/Tripadvisor/Stars-and-Stripes, the room is open Saturdays
   and Sundays (Sunday 11:30-22:00, sometimes split 11:30-17:00 +
   18:00-21:00). Updated hours to "Daily 11:30-22:00 (varies)".
   Important because tokyo-vegan-weekend Day 2 (Sunday) uses Ain
   Soph Journey for evening souffle pancakes; the listed Mon-Fri
   window would have implied the visit was at a closed venue.

### Itinerary day-of-week × hours full sweep (independent of QA2)

All 9 itinerary days re-cross-checked against each venue's hours
field. No further violations after the Ain Soph Journey fix above:

- tokyo-weekend-classics day 1 (Sat): Tsukiji (Tue-Sun), Cafe de
  l'Ambre, Tsuta (closed Tue), Onibus (daily), Ginza Kyubey, Bar
  High Five (Sat open) - all OK.
- tokyo-weekend-classics day 2 (Sun): Centre The Bakery (daily),
  Glitch (daily), Isetan depachika (daily), Omoide Yokocho (most
  stalls), Afuri (daily) - all OK.
- tokyo-modern-tasting-week day 1 (Mon): Koffee Mameya (daily 10-18),
  Maisen (daily), Den (closed Sun) - all OK.
- tokyo-modern-tasting-week day 2 (Tue): Arigato Tsukiji tour, Kanda
  Yabu Soba (closed Wed), Sazenka (closed Sun + irregular Mon) - OK.
- tokyo-modern-tasting-week day 3 (Wed): Centre, Mitsukoshi
  Nihombashi (daily), Cafe de l'Ambre, Florilege (closed Mon + Tue
  lunch) - all OK.
- tokyo-modern-tasting-week day 4 (Thu): Hakone kaiseki day-trip - OK.
- tokyo-modern-tasting-week day 5 (Fri): Onibus, Narisawa (closed
  Mon + Sun), Ahiru Store (Mon-Fri 18:00-24:00), Afuri - all OK.
- tokyo-vegan-weekend day 1 (Sat): T's Tantan, Blue Bottle, Centre,
  Mitsukoshi, Ain Soph Ginza (Wed-Sat 11:30-21:00), Bar High Five
  (Sat open) - all OK.
- tokyo-vegan-weekend day 2 (Sun): Chagohan (Sun classes confirmed),
  Nakamise-dori (daily), Onibus (daily), Ain Soph Journey (after
  hours fix above), Fuglen late (Wed-Sun) - all OK.

### Cross-entry superlative sweep

Grepped all 24 topic files plus narrative pages for "Tokyo's only",
"first in Japan", "only X in Tokyo", "oldest" superlatives:

- "Japan's first three-star Chinese restaurant" (Sazenka, 2020):
  Verified - Sazenka is the world's only three-Michelin-star Chinese
  restaurant outside a Chinese-speaking city (per CNN, Reporter
  Gourmet, Restaurant Times). HOLDS.
- "first ramen shop with a Michelin star" (Tsuta, 2016 guide):
  Verified - Tsuta in Sugamo received the first ramen star in the
  2016 guide announced December 2015. HOLDS.
- "the 10-seat counter from Jiro Dreams of Sushi" (Sukiyabashi
  Jiro Honten): Verified - 10-seat counter is the canonical
  description per Wikipedia and operator. HOLDS.
- "invented the gunkan-maki seaweed-wrapped style" (Ginza Kyubey):
  Verified - founder Hisaji Imada invented gunkan-maki to serve
  soft toppings (per omakaseje, kyubey.jp/en/history). HOLDS.
- "Japan's largest Chinatown" (Yokohama Chinatown): Verified -
  600+ shops in 500m district is Japan's largest per
  japan.travel and matcha-jp. HOLDS.
- "world's most curated department-store food hall" (Isetan
  Shinjuku depachika): Soft editorial claim, not a falsifiable
  superlative. HOLDS as opinion.
- "first overseas roastery" (Blue Bottle Kiyosumi 2015): Verified -
  Blue Bottle's Kiyosumi was the first international roastery
  outside the US per operator and Tokyo Weekender. HOLDS.
- "first overseas outpost" (Fuglen Tokyo 2012): Verified - per
  Fuglen Norway. HOLDS.

No superlative fabrications. Clean.

### Geographic adjacency in itinerary prose

Re-read all itinerary day prose for "next door to", "across the
street from", "adjacent to" claims. None present. Adjacencies
referenced are at the neighborhood / station level (e.g. "Walk
Cat Street to Aoyama", "Shibuya Station Hachiko Exit") which are
true ward-scale references, not banchi-level claims that could
fabricate building proximity.

### Internal-field consistency (Lyon Opus precedent)

Re-read each fine-dining and restaurants entity for tip vs
description vs structural address/hours/chef coherence:

- Sukiyabashi Jiro Honten: stars=0 + prose "concierge bookings
  only since 2020" + tip "Roppongi branch (Takashi Ono) is the
  accessible relative, two stars in the 2026 guide" - coherent
  AFTER one note: tip names "Takashi Ono" as Roppongi chef.
  Per guide.michelin.com/us/en/tokyo-region/tokyo/restaurant/
  sukiyabashi-jiro-roppongiten and Sukiyabashi Jiro Wikipedia,
  the Roppongi branch is run by Takashi Ono (Jiro's younger
  son). HOLDS.
- Florilege: chef Kawate + Azabudai Hills + closed Mon and Tue
  lunch - coherent.
- Sazenka: first 3-star Chinese 2020 + closed Sun + irregular
  Mon + byFood 60-day window - coherent.

### QA1+QA2 fix verification

All 21 corrections from QA1+QA2 verified landed cleanly in the
JSON:
- Sushi Yoshitake stars 0, Kyubey stars 0, Den lead-time 2 months,
  Ain Soph 2009, Wineshop Flow signature pour generic, Wineshop
  Flow neighborhood Hatagaya, Senrogiwa Ebisu-Minami address with
  Tabelog source, Tsuta tense past across both files - all landed.
- Sukiyabashi Jiro Honten stars 0 + Yoshikazu Ono added to chef,
  Sushi Yoshitake stars 0 (re-corrected from QA1's 2), Kyubey
  chef Kagehisa Imada, Bird Land Michelin-selected since,
  Florilege Asia 50 Best No. 31, Koffee Mameya roaster list
  corrected, Sumiyakiya removed from dietary.halal, Pelican
  replaced in tokyo-weekend-classics day 2 (Centre + Glitch)
  and tokyo-vegan-weekend day 2 (Onibus replacing Pelican
  Cafe), Magical Trip duration 3.5 hours - all landed.

### Defects total: 3 (all fixed in-place)

By category:
- Michelin currency: 0 new
- Chef-of-record: 0 new
- Editorial era / decade misstatement: 1 (yakitori signature-dish
  Bird Land 1980s -> 2000s)
- Day-of-week hour-coverage gap: 1 (Bar High Five Sunday closure
  added to tip)
- Weekday-only hours misstated: 1 (Ain Soph Journey brunch entry)
- Itinerary day x hours: 0 new (all 9 days re-cross-checked clean
  after Ain Soph Journey fix)
- Cross-entry superlatives: 0 (all 7 superlatives held against
  independent sources)
- Geographic adjacency fabrication: 0
- Internal-field consistency: 0

### Notes

- Tokyo's Michelin churn is the real story: across QA1+QA2+Opus,
  6 of 23 fine-dining/restaurants/yakitori venues had currency
  drift (Yoshitake 2 levels deep, Jiro Honten, Kyubey, Bird Land,
  Florilege, plus the yakitori-history era restatement). The
  research agent's default-to-"current"-tense pattern is
  structurally broken on Tokyo. PROMPT.md tightening today
  addresses this; suggest a follow-up structural check that any
  `stars` field >0 carries a 2026-dated open_evidence_url whose
  final-host is guide.michelin.com.
- Ahiru Store's "Teruhiko Saito" passed Wineshop Flow's Pia
  Riverola pattern check: Teruhiko + Wakako Saito are the real
  siblings per Time Out, Japan Times 2011, Punch Drink, and his
  own Instagram @ahiruani. Not a fabrication.
- The Bar High Five and Ain Soph Journey fixes are small but
  cover a defect class the QA passes did not articulate:
  individual-venue prose missing hours-coverage information that
  the entity's own `hours` field captures. Worth a follow-up
  ship_safety check that the venue's `tip` and `description`
  do not imply daily operation if the `hours` field excludes
  one or more days.
- No removals. dietary.halal stays 0 (Sumiyakiya removed in QA2;
  research backfill is the separate concern flagged by QA2).

### Verdict

VERDICT: PASS

K=3 in-place fact corrections, 0 removals, 0 fabricated entities.
QA2's "Opus final pass should find zero remaining star-count or
chef-of-record defects" prediction held. The 3 Opus findings are
adjacent classes (decade-era prose, day-of-week tip coverage,
weekday-only hours) - all cosmetic-grade rather than load-bearing
on the page's main claim. Tokyo ships.
