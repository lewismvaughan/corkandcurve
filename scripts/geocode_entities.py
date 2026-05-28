#!/usr/bin/env python3
"""Geocode every entity address via Nominatim, persistently cached on disk.

Walks every site-data JSON for entities with an address. For each, looks
up `(address, city_name)` against Nominatim's public free API
(1 req/sec rate limit, per their usage policy) and stores the result in
data/geocode-cache.json keyed by SHA1 of the lookup string.

The cache is committed to git so subsequent runs (and future agents)
don't pay the API cost again. The geocoder is idempotent on cache hit.

The resulting cache feeds generate_entity_pages.py, which adds
`geo: {latitude, longitude}` to the Restaurant schema for local search.

Usage:
    python scripts/geocode_entities.py                # process all
    python scripts/geocode_entities.py --limit 50     # cap for testing
    python scripts/geocode_entities.py --city paris   # one city only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from math import asin, cos, radians, sin, sqrt
from pathlib import Path


# City-centroid lookup used by the sanity-check filter in _geocode_one.
# Currently-shipped 53 cities are sourced from each city's _pins.json median.
# Forward-looking entries (cities on the roadmap or likely candidates) are
# seeded from public knowledge — they cost nothing if unused, and they
# enable v4 guard to work the first time a new city ships.
# ISO-3166 country code per country slug. Constrains Nominatim queries to
# the right country and prevents the homonym-fallback class of bug:
# Rhône 2026-05-28 sent 136 producers to "Rhone Valley Way" in California;
# Ribera del Duero 2026-05-28 sent 26 producers to "Urbanización Ribera
# del Duero" in Simancas (both via the postcode_centroid fallback querying
# "<postcode>, <region_name>" without a country anchor).
COUNTRY_ISO: dict[str, str] = {
    "france": "fr", "italy": "it", "spain": "es", "portugal": "pt",
    "germany": "de", "austria": "at", "hungary": "hu", "greece": "gr",
    "united-kingdom": "gb", "united-states": "us", "usa": "us",
    "argentina": "ar", "chile": "cl", "australia": "au",
    "new-zealand": "nz", "south-africa": "za", "georgia": "ge",
    "canada": "ca", "mexico": "mx", "japan": "jp", "switzerland": "ch",
    "netherlands": "nl", "belgium": "be", "ireland": "ie", "poland": "pl",
    "czech-republic": "cz", "denmark": "dk", "sweden": "se",
}

CITY_CENTROIDS: dict[tuple[str, str], tuple[float, float]] = {
    # ===== SHIPPED CITIES (sourced from existing pins.json medians) =====
    ("austria", "vienna"):           (48.20707, 16.3684),
    ("czech-republic", "prague"):    (50.08793, 14.41855),
    ("denmark", "copenhagen"):       (55.68216, 12.57007),
    ("france", "lyon"):              (45.76634, 4.83323),
    ("france", "marseille"):         (43.29478, 5.37448),
    ("france", "paris"):             (48.86286, 2.3475),
    ("germany", "berlin"):           (52.51844, 13.41014),
    ("germany", "munich"):           (48.13768, 11.5751),
    ("greece", "athens"):            (37.97791, 23.7273),
    ("hungary", "budapest"):         (47.50001, 19.06054),
    ("ireland", "dublin"):           (53.34201, -6.26429),
    ("italy", "bologna"):            (44.49519, 11.34228),
    ("italy", "florence"):           (43.77042, 11.25529),
    ("italy", "milan"):              (45.46667, 9.18981),
    ("italy", "naples"):             (40.83699, 14.24935),
    ("italy", "rome"):               (41.89947, 12.4789),
    ("italy", "venice"):             (45.43855, 12.32699),
    ("japan", "tokyo"):              (35.66167, 139.71306),
    ("mexico", "mexico-city"):       (19.42699, -99.16719),
    ("netherlands", "amsterdam"):    (52.36683, 4.89148),
    ("poland", "gdansk"):            (54.34788, 18.65273),
    ("poland", "krakow"):            (50.06296, 19.94018),
    ("poland", "poznan"):            (52.40627, 16.93211),
    ("poland", "warsaw"):            (52.22977, 21.0122),
    ("poland", "wroclaw"):           (51.10884, 17.03253),
    ("portugal", "lisbon"):          (38.71321, -9.13815),
    ("spain", "barcelona"):          (41.39111, 2.16399),
    ("spain", "madrid"):             (40.41783, -3.7035),
    ("spain", "san-sebastian"):      (43.31968, -1.98212),
    ("thailand", "bangkok"):         (13.74343, 100.55194),
    ("turkey", "istanbul"):          (41.0438, 28.97705),
    ("united-kingdom", "edinburgh"): (55.95018, -3.18888),
    ("united-kingdom", "london"):    (51.51393, -0.13196),
    ("united-states", "atlanta"):       (33.7717, -84.3771),
    ("united-states", "austin"):        (30.26299, -97.74165),
    ("united-states", "boston"):        (42.35433, -71.06091),
    ("united-states", "charleston"):    (32.78213, -79.93145),
    ("united-states", "chicago"):       (41.87976, -87.63137),
    ("united-states", "denver"):        (39.74471, -104.99098),
    ("united-states", "houston"):       (29.75748, -95.36275),
    ("united-states", "las-vegas"):     (36.10822, -115.17501),
    ("united-states", "los-angeles"):   (34.07832, -118.36107),
    ("united-states", "miami"):         (25.79236, -80.19227),
    ("united-states", "minneapolis"):   (44.97791, -93.27066),
    ("united-states", "nashville"):     (36.16244, -86.78198),
    ("united-states", "new-orleans"):   (29.95369, -90.07042),
    ("united-states", "new-york-city"): (40.72997, -73.98718),
    ("united-states", "philadelphia"):  (39.95273, -75.16382),
    ("united-states", "portland"):      (45.52221, -122.67485),
    ("united-states", "san-diego"):     (32.71606, -117.16542),
    ("united-states", "san-francisco"): (37.78269, -122.41824),
    ("united-states", "seattle"):       (47.60572, -122.33207),
    ("united-states", "washington-dc"): (38.90686, -77.03695),

    # ===== PRE-SEEDED FUTURE CITIES =====
    # Western Europe
    ("belgium", "brussels"):         (50.85045, 4.34878),
    ("belgium", "antwerp"):          (51.21989, 4.40346),
    ("belgium", "ghent"):            (51.05432, 3.7174),
    ("belgium", "bruges"):           (51.20892, 3.22424),
    ("france", "bordeaux"):          (44.83779, -0.5792),
    ("france", "nice"):              (43.7102, 7.262),
    ("france", "toulouse"):          (43.60466, 1.44422),
    ("france", "strasbourg"):        (48.5734, 7.7521),
    ("france", "nantes"):            (47.21845, -1.55362),
    ("france", "montpellier"):       (43.61092, 3.87723),
    ("france", "lille"):             (50.6293, 3.05726),
    ("germany", "hamburg"):          (53.55108, 9.99368),
    ("germany", "cologne"):          (50.93753, 6.9603),
    ("germany", "frankfurt"):        (50.11092, 8.68213),
    ("germany", "stuttgart"):        (48.7758, 9.1829),
    ("germany", "dusseldorf"):       (51.22774, 6.77346),
    ("germany", "dresden"):          (51.05041, 13.73721),
    ("germany", "leipzig"):          (51.33976, 12.37313),
    ("germany", "nuremberg"):        (49.45203, 11.07675),
    ("italy", "genoa"):              (44.4056, 8.94626),
    ("italy", "verona"):             (45.4384, 10.99169),
    ("italy", "turin"):              (45.07049, 7.68682),
    ("italy", "palermo"):            (38.11569, 13.36149),
    ("italy", "catania"):            (37.50795, 15.08303),
    ("italy", "bari"):               (41.11148, 16.86697),
    ("italy", "trieste"):            (45.6495, 13.77679),
    ("italy", "padua"):              (45.40643, 11.87681),
    ("spain", "valencia"):           (39.46975, -0.37739),
    ("spain", "seville"):            (37.38821, -5.99534),
    ("spain", "granada"):            (37.17827, -3.59971),
    ("spain", "bilbao"):             (43.26271, -2.92528),
    ("spain", "malaga"):             (36.72016, -4.42034),
    ("spain", "salamanca"):          (40.96989, -5.6635),
    ("portugal", "porto"):           (41.14961, -8.61099),
    ("netherlands", "rotterdam"):    (51.9244, 4.47776),
    ("netherlands", "the-hague"):    (52.07054, 4.30074),
    ("netherlands", "utrecht"):      (52.09074, 5.12142),
    ("switzerland", "zurich"):       (47.37689, 8.54169),
    ("switzerland", "geneva"):       (46.20222, 6.14569),
    ("switzerland", "basel"):        (47.55814, 7.58769),
    ("switzerland", "lucerne"):      (47.05016, 8.30932),
    ("switzerland", "bern"):         (46.94797, 7.44744),
    ("ireland", "galway"):           (53.27084, -9.05687),
    ("ireland", "cork"):             (51.89798, -8.4706),
    ("united-kingdom", "manchester"):(53.48075, -2.24264),
    ("united-kingdom", "liverpool"): (53.40069, -2.99186),
    ("united-kingdom", "glasgow"):   (55.86423, -4.25181),
    ("united-kingdom", "bristol"):   (51.45422, -2.58791),
    ("united-kingdom", "cardiff"):   (51.4816, -3.17909),
    ("united-kingdom", "belfast"):   (54.59729, -5.93012),
    ("united-kingdom", "oxford"):    (51.75222, -1.25596),
    ("united-kingdom", "cambridge"): (52.20534, 0.12182),
    ("greece", "thessaloniki"):      (40.6401, 22.9444),
    ("malta", "valletta"):           (35.89972, 14.51472),

    # Nordic + Baltic
    ("sweden", "stockholm"):         (59.32932, 18.06858),
    ("sweden", "gothenburg"):        (57.70887, 11.97456),
    ("sweden", "malmo"):             (55.60498, 13.00382),
    ("norway", "oslo"):              (59.91387, 10.7522),
    ("norway", "bergen"):            (60.39299, 5.32415),
    ("finland", "helsinki"):         (60.16952, 24.93545),
    ("iceland", "reykjavik"):        (64.14661, -21.94236),
    ("estonia", "tallinn"):          (59.43696, 24.75353),
    ("latvia", "riga"):              (56.94965, 24.10519),
    ("lithuania", "vilnius"):        (54.68716, 25.27989),

    # Central + Eastern Europe
    ("austria", "salzburg"):         (47.80949, 13.05501),
    ("austria", "innsbruck"):        (47.26939, 11.4041),
    ("czech-republic", "brno"):      (49.19522, 16.60796),
    ("hungary", "debrecen"):         (47.5316, 21.6273),
    ("romania", "bucharest"):        (44.42677, 26.10254),
    ("bulgaria", "sofia"):           (42.69751, 23.32184),
    ("serbia", "belgrade"):          (44.78657, 20.44893),
    ("croatia", "zagreb"):           (45.81504, 15.96618),
    ("croatia", "split"):            (43.50891, 16.43874),
    ("croatia", "dubrovnik"):        (42.6507, 18.0944),
    ("slovenia", "ljubljana"):       (46.05108, 14.50513),
    ("bosnia-and-herzegovina", "sarajevo"): (43.85643, 18.41315),
    ("ukraine", "kyiv"):             (50.45047, 30.5238),
    ("ukraine", "lviv"):             (49.83968, 24.02972),

    # Asia
    ("china", "beijing"):            (39.9042, 116.40739),
    ("china", "shanghai"):           (31.23039, 121.4737),
    ("china", "chengdu"):             (30.5728, 104.06624),
    ("china", "xian"):                (34.34127, 108.94022),
    ("china", "guangzhou"):           (23.12911, 113.26436),
    ("china", "shenzhen"):            (22.54286, 114.05956),
    ("hong-kong", "hong-kong"):       (22.31931, 114.16937),
    ("japan", "osaka"):               (34.69374, 135.50218),
    ("japan", "kyoto"):               (35.01163, 135.76803),
    ("japan", "hiroshima"):           (34.38528, 132.45528),
    ("japan", "sapporo"):             (43.0618, 141.35451),
    ("japan", "fukuoka"):             (33.58964, 130.40173),
    ("japan", "okinawa"):             (26.2125, 127.6792),
    ("south-korea", "seoul"):         (37.5665, 126.978),
    ("south-korea", "busan"):         (35.17955, 129.07556),
    ("taiwan", "taipei"):             (25.03296, 121.5654),
    ("singapore", "singapore"):       (1.35208, 103.81984),
    ("malaysia", "kuala-lumpur"):     (3.139, 101.68685),
    ("malaysia", "penang"):           (5.41123, 100.33543),
    ("indonesia", "jakarta"):         (-6.20876, 106.84559),
    ("indonesia", "bali"):            (-8.34054, 115.092),
    ("philippines", "manila"):        (14.59951, 120.9842),
    ("vietnam", "hanoi"):             (21.02776, 105.83416),
    ("vietnam", "ho-chi-minh-city"):  (10.82302, 106.62965),
    ("vietnam", "da-nang"):           (16.04788, 108.20623),
    ("cambodia", "phnom-penh"):       (11.55639, 104.92822),
    ("cambodia", "siem-reap"):        (13.36167, 103.85),
    ("myanmar", "yangon"):            (16.86609, 96.19528),
    ("thailand", "chiang-mai"):       (18.78832, 98.98531),
    ("thailand", "phuket"):           (7.8804, 98.3923),
    ("sri-lanka", "colombo"):         (6.92708, 79.86124),
    ("nepal", "kathmandu"):           (27.71724, 85.32401),
    ("india", "mumbai"):              (19.07598, 72.87766),
    ("india", "delhi"):               (28.7041, 77.10249),
    ("india", "bangalore"):           (12.97194, 77.59369),
    ("india", "kolkata"):             (22.57264, 88.36389),
    ("india", "chennai"):             (13.0827, 80.27072),
    ("india", "goa"):                 (15.29927, 74.12399),

    # Middle East + North Africa
    ("israel", "tel-aviv"):           (32.0853, 34.78177),
    ("israel", "jerusalem"):          (31.76833, 35.21371),
    ("lebanon", "beirut"):            (33.88863, 35.49548),
    ("jordan", "amman"):              (31.94531, 35.92837),
    ("united-arab-emirates", "dubai"): (25.2048, 55.27078),
    ("united-arab-emirates", "abu-dhabi"): (24.45385, 54.37734),
    ("qatar", "doha"):                (25.28545, 51.5326),
    ("saudi-arabia", "riyadh"):       (24.71355, 46.67529),
    ("egypt", "cairo"):               (30.04442, 31.23571),
    ("morocco", "marrakech"):         (31.62947, -7.98152),
    ("morocco", "casablanca"):        (33.57311, -7.58954),
    ("morocco", "fez"):               (34.0181, -5.0078),
    ("tunisia", "tunis"):             (36.80649, 10.18156),

    # Africa
    ("south-africa", "cape-town"):    (-33.92487, 18.42406),
    ("south-africa", "johannesburg"): (-26.20227, 28.04363),
    ("kenya", "nairobi"):             (-1.28333, 36.81667),
    ("ethiopia", "addis-ababa"):      (9.02497, 38.74689),
    ("ghana", "accra"):               (5.55602, -0.1969),
    ("nigeria", "lagos"):             (6.5244, 3.3792),
    ("senegal", "dakar"):             (14.71667, -17.46667),

    # Latin America
    ("argentina", "buenos-aires"):    (-34.60368, -58.38157),
    ("argentina", "mendoza"):         (-32.88945, -68.84583),
    ("brazil", "rio-de-janeiro"):     (-22.90685, -43.17296),
    ("brazil", "sao-paulo"):          (-23.5505, -46.63331),
    ("brazil", "salvador"):           (-12.97304, -38.50232),
    ("peru", "lima"):                 (-12.04637, -77.04279),
    ("peru", "cusco"):                (-13.53195, -71.96746),
    ("peru", "arequipa"):             (-16.40904, -71.5375),
    ("colombia", "bogota"):           (4.711, -74.07209),
    ("colombia", "medellin"):         (6.24407, -75.58133),
    ("colombia", "cartagena"):        (10.39972, -75.51444),
    ("ecuador", "quito"):             (-0.18065, -78.46784),
    ("chile", "santiago"):            (-33.44889, -70.66927),
    ("uruguay", "montevideo"):        (-34.90328, -56.18816),
    ("bolivia", "la-paz"):            (-16.5, -68.15),
    ("guatemala", "guatemala-city"):  (14.6349, -90.50689),
    ("guatemala", "antigua"):         (14.5586, -90.7338),
    ("costa-rica", "san-jose"):       (9.93333, -84.08333),
    ("panama", "panama-city"):        (8.9824, -79.51992),
    ("cuba", "havana"):               (23.1136, -82.3666),
    ("dominican-republic", "santo-domingo"): (18.4861, -69.93121),
    ("mexico", "oaxaca"):             (17.0732, -96.7266),
    ("mexico", "guadalajara"):        (20.6597, -103.34938),
    ("mexico", "monterrey"):          (25.68661, -100.31611),
    ("mexico", "merida"):             (20.96737, -89.59259),
    ("mexico", "puebla"):             (19.04132, -98.20627),
    ("mexico", "san-miguel-de-allende"): (20.91435, -100.7437),
    ("mexico", "puerto-vallarta"):    (20.65389, -105.22531),

    # North America
    ("canada", "toronto"):            (43.65107, -79.34702),
    ("canada", "montreal"):           (45.50884, -73.58781),
    ("canada", "vancouver"):          (49.28273, -123.12074),
    ("canada", "quebec-city"):        (46.81387, -71.20827),
    ("canada", "ottawa"):             (45.42153, -75.6972),
    ("canada", "calgary"):            (51.04473, -114.07189),
    ("united-states", "phoenix"):       (33.44838, -112.07404),
    ("united-states", "salt-lake-city"):(40.76078, -111.89105),
    ("united-states", "detroit"):       (42.33143, -83.04575),
    ("united-states", "cleveland"):     (41.4993, -81.69541),
    ("united-states", "pittsburgh"):    (40.44062, -79.99589),
    ("united-states", "indianapolis"):  (39.76838, -86.15804),
    ("united-states", "san-antonio"):   (29.42412, -98.49363),
    ("united-states", "kansas-city"):   (39.09973, -94.57857),
    ("united-states", "saint-louis"):   (38.62727, -90.19789),
    ("united-states", "tampa"):         (27.95058, -82.45718),
    ("united-states", "orlando"):       (28.53834, -81.37924),
    ("united-states", "honolulu"):      (21.30694, -157.85833),
    ("united-states", "savannah"):      (32.0809, -81.0912),
    ("united-states", "santa-fe"):      (35.687, -105.9378),
    ("united-states", "richmond"):      (37.5407, -77.436),
    ("united-states", "milwaukee"):     (43.0389, -87.9065),
    ("united-states", "raleigh"):       (35.7796, -78.6382),
    ("united-states", "providence"):    (41.824, -71.4128),

    # Oceania
    ("australia", "sydney"):          (-33.86882, 151.20929),
    ("australia", "melbourne"):       (-37.81363, 144.96306),
    ("australia", "brisbane"):        (-27.46977, 153.02513),
    ("australia", "perth"):           (-31.95224, 115.8614),
    ("australia", "adelaide"):        (-34.92866, 138.59863),
    ("australia", "hobart"):          (-42.88276, 147.32753),
    ("new-zealand", "auckland"):      (-36.84846, 174.76332),
    ("new-zealand", "wellington"):    (-41.28664, 174.77557),
    ("new-zealand", "queenstown"):    (-45.0312, 168.6626),
    ("new-zealand", "christchurch"):  (-43.5321, 172.6362),
    ("new-zealand", "rotorua"):       (-38.1368, 176.2497),

    # ===== EVEN MORE — exhaustive global food-city coverage =====
    # Additional EU
    ("united-kingdom", "york"):           (53.9591, -1.0815),
    ("united-kingdom", "brighton"):       (50.8225, -0.1372),
    ("united-kingdom", "bath"):           (51.3811, -2.3590),
    ("united-kingdom", "newcastle"):      (54.9783, -1.6178),
    ("united-kingdom", "leeds"):          (53.8008, -1.5491),
    ("united-kingdom", "birmingham"):     (52.4862, -1.8904),
    ("united-kingdom", "sheffield"):      (53.3811, -1.4701),
    ("united-kingdom", "nottingham"):     (52.9548, -1.1581),
    ("united-kingdom", "norwich"):        (52.6309, 1.2974),
    ("united-kingdom", "exeter"):         (50.7184, -3.5339),
    ("united-kingdom", "st-andrews"):     (56.3398, -2.7967),
    ("united-kingdom", "inverness"):      (57.4778, -4.2247),
    ("ireland", "kilkenny"):              (52.6541, -7.2448),
    ("ireland", "kinsale"):               (51.7059, -8.5222),
    ("ireland", "dingle"):                (52.1409, -10.2683),
    ("france", "avignon"):                (43.9493, 4.8055),
    ("france", "aix-en-provence"):        (43.5297, 5.4474),
    ("france", "rennes"):                 (48.1173, -1.6778),
    ("france", "reims"):                  (49.2583, 4.0317),
    ("france", "dijon"):                  (47.3220, 5.0415),
    ("france", "annecy"):                 (45.8992, 6.1294),
    ("france", "biarritz"):               (43.4832, -1.5586),
    ("france", "perpignan"):              (42.6886, 2.8949),
    ("france", "saint-malo"):             (48.6492, -2.0254),
    ("france", "colmar"):                 (48.0794, 7.3585),
    ("france", "lyon-saint-etienne"):     (45.4339, 4.3909),
    ("france", "rouen"):                  (49.4432, 1.0993),
    ("france", "le-havre"):               (49.4944, 0.1079),
    ("france", "cannes"):                 (43.5528, 7.0174),
    ("france", "saint-tropez"):           (43.2728, 6.6407),
    ("germany", "bremen"):                (53.0793, 8.8017),
    ("germany", "hannover"):              (52.3759, 9.7320),
    ("germany", "essen"):                 (51.4556, 7.0116),
    ("germany", "dortmund"):              (51.5136, 7.4653),
    ("germany", "bonn"):                  (50.7374, 7.0982),
    ("germany", "wurzburg"):              (49.7913, 9.9534),
    ("germany", "regensburg"):            (49.0134, 12.1016),
    ("germany", "freiburg"):              (47.9990, 7.8421),
    ("germany", "heidelberg"):            (49.3988, 8.6724),
    ("germany", "rothenburg"):            (49.3776, 10.1879),
    ("italy", "lucca"):                   (43.8430, 10.5079),
    ("italy", "pisa"):                    (43.7228, 10.4017),
    ("italy", "siena"):                   (43.3188, 11.3308),
    ("italy", "perugia"):                 (43.1107, 12.3908),
    ("italy", "ravenna"):                 (44.4173, 12.1965),
    ("italy", "modena"):                  (44.6471, 10.9252),
    ("italy", "parma"):                   (44.8015, 10.3279),
    ("italy", "matera"):                  (40.6664, 16.6043),
    ("italy", "lecce"):                   (40.3515, 18.1750),
    ("italy", "amalfi"):                  (40.6340, 14.6027),
    ("italy", "sorrento"):                (40.6262, 14.3754),
    ("italy", "positano"):                (40.6280, 14.4849),
    ("italy", "capri"):                   (40.5532, 14.2222),
    ("italy", "alba"):                    (44.6997, 8.0344),
    ("italy", "san-gimignano"):           (43.4673, 11.0432),
    ("italy", "spoleto"):                 (42.7400, 12.7383),
    ("italy", "syracuse"):                (37.0755, 15.2866),
    ("italy", "taormina"):                (37.8528, 15.2895),
    ("spain", "santiago-de-compostela"):  (42.8782, -8.5448),
    ("spain", "cordoba"):                 (37.8882, -4.7794),
    ("spain", "toledo"):                  (39.8628, -4.0273),
    ("spain", "tarragona"):               (41.1188, 1.2445),
    ("spain", "alicante"):                (38.3452, -0.4810),
    ("spain", "ronda"):                   (36.7427, -5.1660),
    ("spain", "santander"):               (43.4623, -3.8099),
    ("spain", "girona"):                  (41.9794, 2.8214),
    ("spain", "logrono"):                 (42.4651, -2.4456),
    ("spain", "vigo"):                    (42.2406, -8.7207),
    ("spain", "oviedo"):                  (43.3614, -5.8593),
    ("spain", "burgos"):                  (42.3439, -3.6969),
    ("spain", "valladolid"):              (41.6523, -4.7245),
    ("spain", "leon"):                    (42.5987, -5.5671),
    ("spain", "zaragoza"):                (41.6488, -0.8891),
    ("spain", "palma-de-mallorca"):       (39.5696, 2.6502),
    ("spain", "ibiza"):                   (38.9067, 1.4206),
    ("portugal", "coimbra"):              (40.2033, -8.4103),
    ("portugal", "evora"):                (38.5713, -7.9135),
    ("portugal", "sintra"):               (38.7972, -9.3905),
    ("portugal", "braga"):                (41.5454, -8.4265),
    ("portugal", "faro"):                 (37.0194, -7.9322),
    ("portugal", "funchal"):              (32.6669, -16.9241),  # Madeira
    ("portugal", "lagos-portugal"):       (37.1028, -8.6735),
    ("netherlands", "haarlem"):           (52.3873, 4.6462),
    ("netherlands", "leiden"):            (52.1601, 4.4970),
    ("netherlands", "delft"):             (52.0116, 4.3571),
    ("netherlands", "groningen"):         (53.2194, 6.5665),
    ("netherlands", "eindhoven"):         (51.4416, 5.4697),
    ("netherlands", "maastricht"):        (50.8514, 5.6910),
    ("denmark", "aarhus"):                (56.1572, 10.2107),
    ("denmark", "odense"):                (55.4038, 10.4024),
    ("sweden", "uppsala"):                (59.8586, 17.6389),
    ("norway", "trondheim"):              (63.4305, 10.3951),
    ("norway", "stavanger"):              (58.9700, 5.7331),
    ("norway", "tromso"):                 (69.6492, 18.9553),
    ("finland", "tampere"):               (61.4978, 23.7610),
    ("finland", "turku"):                 (60.4518, 22.2666),
    ("estonia", "tartu"):                 (58.3776, 26.7290),
    ("austria", "graz"):                  (47.0707, 15.4395),
    ("austria", "linz"):                  (48.3064, 14.2858),
    ("austria", "hallstatt"):             (47.5622, 13.6493),
    ("czech-republic", "cesky-krumlov"):  (48.8127, 14.3175),
    ("czech-republic", "kutna-hora"):     (49.9484, 15.2670),
    ("czech-republic", "olomouc"):        (49.5938, 17.2509),
    ("czech-republic", "pilsen"):         (49.7475, 13.3776),
    ("hungary", "szeged"):                (46.2530, 20.1414),
    ("hungary", "eger"):                  (47.9025, 20.3772),
    ("hungary", "pecs"):                  (46.0727, 18.2323),
    ("slovakia", "bratislava"):           (48.1486, 17.1077),
    ("slovakia", "kosice"):               (48.7164, 21.2611),
    ("croatia", "rovinj"):                (45.0813, 13.6387),
    ("croatia", "pula"):                  (44.8666, 13.8496),
    ("croatia", "hvar"):                  (43.1729, 16.4413),
    ("croatia", "zadar"):                 (44.1194, 15.2314),
    ("montenegro", "kotor"):              (42.4247, 18.7712),
    ("montenegro", "podgorica"):          (42.4304, 19.2594),
    ("albania", "tirana"):                (41.3275, 19.8187),
    ("north-macedonia", "skopje"):        (41.9981, 21.4254),
    ("turkey", "ankara"):                 (39.9334, 32.8597),
    ("turkey", "izmir"):                  (38.4192, 27.1287),
    ("turkey", "antalya"):                (36.8969, 30.7133),
    ("turkey", "bodrum"):                 (37.0344, 27.4304),
    ("turkey", "cappadocia"):             (38.6431, 34.8289),  # Goreme
    ("turkey", "gaziantep"):              (37.0660, 37.3833),
    ("greece", "santorini"):              (36.3932, 25.4615),
    ("greece", "mykonos"):                (37.4467, 25.3289),
    ("greece", "crete"):                  (35.3387, 25.1442),  # Heraklion
    ("greece", "rhodes"):                 (36.4413, 28.2225),
    ("greece", "corfu"):                  (39.6243, 19.9217),

    # Additional Asia
    ("japan", "nagoya"):                  (35.1815, 136.9066),
    ("japan", "kobe"):                    (34.6901, 135.1955),
    ("japan", "yokohama"):                (35.4437, 139.6380),
    ("japan", "kanazawa"):                (36.5613, 136.6562),
    ("japan", "nara"):                    (34.6851, 135.8048),
    ("japan", "nagasaki"):                (32.7503, 129.8779),
    ("japan", "kumamoto"):                (32.8033, 130.7079),
    ("japan", "sendai"):                  (38.2682, 140.8694),
    ("japan", "takayama"):                (36.1429, 137.2517),
    ("japan", "naha"):                    (26.2125, 127.6792),
    ("japan", "kyoto-uji"):               (34.8841, 135.7997),
    ("south-korea", "jeju"):               (33.4996, 126.5312),
    ("south-korea", "incheon"):            (37.4563, 126.7052),
    ("south-korea", "gyeongju"):           (35.8562, 129.2247),
    ("south-korea", "jeonju"):             (35.8242, 127.1480),
    ("taiwan", "tainan"):                 (22.9999, 120.2270),
    ("taiwan", "kaohsiung"):              (22.6273, 120.3014),
    ("taiwan", "taichung"):               (24.1477, 120.6736),
    ("china", "hangzhou"):                (30.2741, 120.1551),
    ("china", "suzhou"):                  (31.2989, 120.5853),
    ("china", "tianjin"):                 (39.3434, 117.3616),
    ("china", "chongqing"):               (29.4316, 106.9123),
    ("china", "wuhan"):                   (30.5928, 114.3055),
    ("china", "kunming"):                 (24.8801, 102.8329),
    ("china", "harbin"):                  (45.8038, 126.5340),
    ("china", "qingdao"):                 (36.0671, 120.3826),
    ("china", "macau"):                   (22.1987, 113.5439),
    ("china", "guilin"):                  (25.2735, 110.2900),
    ("china", "dalian"):                  (38.9140, 121.6147),
    ("china", "lijiang"):                 (26.8721, 100.2257),
    ("indonesia", "yogyakarta"):          (-7.7956, 110.3695),
    ("indonesia", "surabaya"):            (-7.2575, 112.7521),
    ("indonesia", "bandung"):             (-6.9175, 107.6191),
    ("indonesia", "lombok"):              (-8.6500, 116.3242),
    ("philippines", "cebu"):              (10.3157, 123.8854),
    ("philippines", "boracay"):           (11.9674, 121.9248),
    ("philippines", "davao"):             (7.1907, 125.4553),
    ("vietnam", "hue"):                   (16.4637, 107.5909),
    ("vietnam", "hoi-an"):                (15.8801, 108.3380),
    ("vietnam", "nha-trang"):             (12.2388, 109.1967),
    ("malaysia", "george-town"):          (5.4141, 100.3288),  # Penang
    ("malaysia", "melaka"):               (2.1896, 102.2501),
    ("malaysia", "kota-kinabalu"):        (5.9804, 116.0735),
    ("india", "jaipur"):                  (26.9124, 75.7873),
    ("india", "udaipur"):                 (24.5854, 73.7125),
    ("india", "jodhpur"):                 (26.2389, 73.0243),
    ("india", "amritsar"):                (31.6340, 74.8723),
    ("india", "varanasi"):                (25.3176, 82.9739),
    ("india", "agra"):                    (27.1767, 78.0081),
    ("india", "rishikesh"):               (30.0869, 78.2676),
    ("india", "kochi"):                   (9.9312, 76.2673),
    ("india", "kerala-backwaters"):       (9.4981, 76.3388),  # Alleppey
    ("pakistan", "karachi"):              (24.8607, 67.0011),
    ("pakistan", "lahore"):               (31.5204, 74.3587),
    ("pakistan", "islamabad"):            (33.6844, 73.0479),
    ("bangladesh", "dhaka"):              (23.8103, 90.4125),
    ("nepal", "pokhara"):                 (28.2096, 83.9856),
    ("bhutan", "thimphu"):                (27.4716, 89.6386),
    ("mongolia", "ulaanbaatar"):          (47.8864, 106.9057),

    # Additional Middle East / Caucasus / Central Asia
    ("israel", "haifa"):                  (32.7940, 34.9896),
    ("turkey", "trabzon"):                (41.0027, 39.7168),
    ("georgia", "tbilisi"):               (41.7151, 44.8271),
    ("armenia", "yerevan"):               (40.1792, 44.4991),
    ("azerbaijan", "baku"):               (40.4093, 49.8671),
    ("uzbekistan", "samarkand"):          (39.6270, 66.9750),
    ("uzbekistan", "bukhara"):            (39.7681, 64.4556),
    ("uzbekistan", "tashkent"):           (41.2995, 69.2401),
    ("iran", "tehran"):                   (35.6892, 51.3890),
    ("iran", "isfahan"):                  (32.6546, 51.6680),
    ("iran", "shiraz"):                   (29.5918, 52.5837),

    # Additional Africa
    ("ethiopia", "lalibela"):             (12.0312, 39.0431),
    ("kenya", "mombasa"):                 (-4.0435, 39.6682),
    ("tanzania", "dar-es-salaam"):        (-6.7924, 39.2083),
    ("tanzania", "zanzibar"):             (-6.1659, 39.2026),
    ("rwanda", "kigali"):                 (-1.9706, 30.1044),
    ("uganda", "kampala"):                (0.3476, 32.5825),
    ("south-africa", "stellenbosch"):     (-33.9321, 18.8602),
    ("south-africa", "durban"):           (-29.8587, 31.0218),
    ("mauritius", "port-louis"):          (-20.1641, 57.5012),
    ("madagascar", "antananarivo"):       (-18.8792, 47.5079),
    ("morocco", "chefchaouen"):           (35.1715, -5.2697),
    ("morocco", "essaouira"):             (31.5085, -9.7595),
    ("morocco", "rabat"):                 (33.9716, -6.8498),
    ("algeria", "algiers"):               (36.7538, 3.0588),

    # Additional Latin America
    ("brazil", "florianopolis"):          (-27.5954, -48.5480),
    ("brazil", "fortaleza"):              (-3.7172, -38.5433),
    ("brazil", "manaus"):                 (-3.1190, -60.0217),
    ("brazil", "porto-alegre"):           (-30.0277, -51.2287),
    ("brazil", "recife"):                 (-8.0476, -34.8770),
    ("brazil", "curitiba"):               (-25.4244, -49.2654),
    ("brazil", "brasilia"):               (-15.7975, -47.8919),
    ("argentina", "cordoba-argentina"):   (-31.4201, -64.1888),
    ("argentina", "bariloche"):           (-41.1335, -71.3103),
    ("argentina", "salta"):               (-24.7821, -65.4232),
    ("argentina", "iguazu"):              (-25.5947, -54.5867),  # Puerto Iguazu
    ("argentina", "ushuaia"):             (-54.8019, -68.3030),
    ("peru", "trujillo"):                 (-8.1116, -79.0288),
    ("peru", "puno"):                     (-15.8402, -70.0219),  # Lake Titicaca
    ("colombia", "cali"):                 (3.4516, -76.5320),
    ("colombia", "santa-marta"):          (11.2408, -74.1990),
    ("chile", "valparaiso"):              (-33.0472, -71.6127),
    ("chile", "san-pedro-de-atacama"):    (-22.9098, -68.2003),
    ("ecuador", "guayaquil"):             (-2.1709, -79.9224),
    ("ecuador", "cuenca"):                (-2.9001, -79.0059),
    ("ecuador", "galapagos"):             (-0.7893, -91.0152),
    ("paraguay", "asuncion"):             (-25.2637, -57.5759),
    ("venezuela", "caracas"):             (10.4806, -66.9036),
    ("guyana", "georgetown"):             (6.8013, -58.1551),
    ("suriname", "paramaribo"):           (5.8520, -55.2038),
    ("nicaragua", "granada-nicaragua"):   (11.9344, -85.9560),
    ("honduras", "tegucigalpa"):          (14.0723, -87.1921),
    ("el-salvador", "san-salvador"):      (13.6929, -89.2182),
    ("belize", "belize-city"):            (17.5046, -88.1962),
    ("haiti", "port-au-prince"):          (18.5944, -72.3074),
    ("jamaica", "kingston"):              (17.9714, -76.7920),
    ("trinidad-and-tobago", "port-of-spain"): (10.6596, -61.5170),
    ("barbados", "bridgetown"):           (13.0975, -59.6167),
    ("bahamas", "nassau"):                (25.0480, -77.3554),
    ("puerto-rico", "san-juan"):          (18.4655, -66.1057),

    # Additional Canada
    ("canada", "halifax"):                (44.6488, -63.5752),
    ("canada", "winnipeg"):               (49.8951, -97.1384),
    ("canada", "edmonton"):               (53.5461, -113.4938),
    ("canada", "victoria"):               (48.4284, -123.3656),
    ("canada", "niagara-on-the-lake"):    (43.2557, -79.0712),
    ("canada", "banff"):                  (51.1784, -115.5708),
    ("canada", "whistler"):               (50.1163, -122.9574),

    # Additional US — all states' major food cities
    ("united-states", "buffalo"):         (42.8864, -78.8784),
    ("united-states", "albany"):          (42.6526, -73.7562),
    ("united-states", "syracuse"):        (43.0481, -76.1474),
    ("united-states", "rochester"):       (43.1566, -77.6088),
    ("united-states", "burlington"):      (44.4759, -73.2121),  # VT
    ("united-states", "portland-maine"):  (43.6591, -70.2568),
    ("united-states", "hartford"):        (41.7658, -72.6734),
    ("united-states", "new-haven"):       (41.3083, -72.9279),
    ("united-states", "baltimore"):       (39.2904, -76.6122),
    ("united-states", "annapolis"):       (38.9784, -76.4922),
    ("united-states", "norfolk"):         (36.8508, -76.2859),
    ("united-states", "charlotte"):       (35.2271, -80.8431),
    ("united-states", "asheville"):       (35.5951, -82.5515),
    ("united-states", "charleston-wv"):   (38.3498, -81.6326),
    ("united-states", "louisville"):      (38.2527, -85.7585),
    ("united-states", "lexington"):       (38.0406, -84.5037),
    ("united-states", "memphis"):         (35.1495, -90.0490),
    ("united-states", "birmingham-al"):   (33.5186, -86.8104),
    ("united-states", "tuscaloosa"):      (33.2098, -87.5692),
    ("united-states", "mobile"):          (30.6954, -88.0399),
    ("united-states", "jackson"):         (32.2988, -90.1848),  # MS
    ("united-states", "little-rock"):     (34.7465, -92.2896),
    ("united-states", "tulsa"):           (36.1539, -95.9928),
    ("united-states", "oklahoma-city"):   (35.4676, -97.5164),
    ("united-states", "des-moines"):      (41.5868, -93.6250),
    ("united-states", "omaha"):           (41.2565, -95.9345),
    ("united-states", "wichita"):         (37.6872, -97.3301),
    ("united-states", "fargo"):           (46.8772, -96.7898),
    ("united-states", "sioux-falls"):     (43.5460, -96.7313),
    ("united-states", "rapid-city"):      (44.0805, -103.2310),
    ("united-states", "billings"):        (45.7833, -108.5007),
    ("united-states", "boise"):           (43.6150, -116.2023),
    ("united-states", "spokane"):         (47.6588, -117.4260),
    ("united-states", "tacoma"):          (47.2529, -122.4443),
    ("united-states", "eugene"):          (44.0521, -123.0868),
    ("united-states", "sacramento"):      (38.5816, -121.4944),
    ("united-states", "oakland"):         (37.8044, -122.2712),
    ("united-states", "san-jose"):        (37.3382, -121.8863),
    ("united-states", "fresno"):          (36.7378, -119.7871),
    ("united-states", "long-beach"):      (33.7701, -118.1937),
    ("united-states", "santa-monica"):    (34.0195, -118.4912),
    ("united-states", "anaheim"):         (33.8366, -117.9143),
    ("united-states", "palm-springs"):    (33.8303, -116.5453),
    ("united-states", "tucson"):          (32.2226, -110.9747),
    ("united-states", "albuquerque"):     (35.0844, -106.6504),
    ("united-states", "el-paso"):         (31.7619, -106.4850),
    ("united-states", "fort-worth"):      (32.7555, -97.3308),
    ("united-states", "dallas"):          (32.7767, -96.7970),
    ("united-states", "corpus-christi"):  (27.8006, -97.3964),
    ("united-states", "baton-rouge"):     (30.4515, -91.1871),
    ("united-states", "lafayette"):       (30.2241, -92.0198),
    ("united-states", "mobile-bay"):      (30.6954, -88.0399),
    ("united-states", "key-west"):        (24.5551, -81.7800),
    ("united-states", "tallahassee"):     (30.4383, -84.2807),
    ("united-states", "jacksonville"):    (30.3322, -81.6557),
    ("united-states", "myrtle-beach"):    (33.6891, -78.8867),
    ("united-states", "outer-banks"):     (35.5587, -75.4665),
    ("united-states", "wilmington"):      (34.2257, -77.9447),
    ("united-states", "columbia"):        (34.0007, -81.0348),  # SC
    ("united-states", "athens-georgia"):  (33.9519, -83.3576),
    ("united-states", "newport"):         (41.4901, -71.3128),  # RI
    ("united-states", "provincetown"):    (42.0584, -70.1786),
    ("united-states", "anchorage"):       (61.2181, -149.9003),
    ("united-states", "juneau"):          (58.3019, -134.4197),
    ("united-states", "fairbanks"):       (64.8378, -147.7164),
    ("united-states", "boulder"):         (40.0150, -105.2705),
    ("united-states", "aspen"):           (39.1911, -106.8175),
    ("united-states", "vail"):            (39.6403, -106.3742),
    ("united-states", "telluride"):       (37.9375, -107.8123),
    ("united-states", "park-city"):       (40.6461, -111.4980),
    ("united-states", "jackson-hole"):    (43.4799, -110.7624),
    ("united-states", "sun-valley"):      (43.6976, -114.3517),
    ("united-states", "lake-tahoe"):      (39.0968, -120.0324),
    ("united-states", "napa"):            (38.2975, -122.2869),
    ("united-states", "sonoma"):          (38.2919, -122.4580),
    ("united-states", "carmel"):          (36.5552, -121.9233),
    ("united-states", "santa-barbara"):   (34.4208, -119.6982),
    ("united-states", "santa-cruz"):      (36.9741, -122.0308),
    ("united-states", "monterey"):        (36.6002, -121.8947),
    ("united-states", "sedona"):          (34.8697, -111.7610),
    ("united-states", "flagstaff"):       (35.1983, -111.6513),
    ("united-states", "taos"):            (36.4072, -105.5734),

    # Additional Mexico
    ("mexico", "tulum"):                  (20.2114, -87.4654),
    ("mexico", "playa-del-carmen"):       (20.6296, -87.0739),
    ("mexico", "cancun"):                 (21.1619, -86.8515),
    ("mexico", "tijuana"):                (32.5149, -117.0382),
    ("mexico", "san-cristobal-de-las-casas"): (16.7370, -92.6376),
    ("mexico", "morelia"):                (19.7008, -101.1844),
    ("mexico", "queretaro"):              (20.5888, -100.3899),
    ("mexico", "guanajuato"):             (21.0190, -101.2574),
    ("mexico", "san-luis-potosi"):        (22.1565, -100.9855),
    ("mexico", "cabo-san-lucas"):         (22.8905, -109.9167),
    ("mexico", "loreto"):                 (26.0125, -111.3438),
    ("mexico", "valladolid-yucatan"):     (20.6896, -88.2017),
    ("mexico", "chiapas-tuxtla"):         (16.7569, -93.1292),

    # Additional Oceania
    ("australia", "darwin"):              (-12.4634, 130.8456),
    ("australia", "cairns"):              (-16.9186, 145.7781),
    ("australia", "gold-coast"):          (-28.0167, 153.4000),
    ("australia", "byron-bay"):           (-28.6474, 153.6020),
    ("australia", "noosa"):               (-26.4000, 153.0833),
    ("australia", "broome"):              (-17.9614, 122.2359),
    ("australia", "alice-springs"):       (-23.6980, 133.8807),
    ("australia", "margaret-river"):      (-33.9550, 115.0750),
    ("new-zealand", "dunedin"):           (-45.8788, 170.5028),
    ("new-zealand", "napier"):            (-39.4928, 176.9120),

    # Pacific + Caribbean
    ("french-polynesia", "papeete"):      (-17.5516, -149.5585),
    ("fiji", "suva"):                     (-18.1248, 178.4501),
    ("samoa", "apia"):                    (-13.8506, -171.7513),
}

# Reject Nominatim results that land more than this many km from the
# city centroid. Legit suburb day-trips (Boulder for Denver, Carlsbad
# for San Diego) fit under 50km. Anything beyond is almost always a
# country-fallback or a misread street token. Day-trips that genuinely
# live further out (Lowell/Boston, Driftwood/Austin) simply won't show
# on the city map; they still appear on the day-trips topic page.
MAX_DISTANCE_FROM_CITY_KM = 50.0


def _haversine_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    R = 6371.0
    dlat = radians(b_lat - a_lat)
    dlon = radians(b_lng - a_lng)
    h = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(h))

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
CACHE_PATH = REPO / "data" / "geocode-cache.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CorkAndCurve/1.0 (lewis@corkandcurve.com)"
SLEEP_SECONDS = 1.05  # Nominatim policy is 1/sec; small buffer to be safe.


def _cache_key(address: str, city_name: str) -> str:
    blob = f"{address.lower().strip()}|{city_name.lower().strip()}"
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _nominatim_query(q: str, country_code: str | None = None) -> dict | None:
    """Single Nominatim call. Returns {'lat':..., 'lon':..., 'queried': q}
    on a hit or None on a miss / error.

    `country_code` constrains the search to a specific ISO-3166 country
    (e.g. "fr", "es"). This prevents the postcode_centroid fallback class
    of bug where `"<postcode>, <region_name>"` matches a homonym in a
    different country — Rhône 2026-05-28 sent 136 producers to a "Rhone
    Valley Way" road in Chula Vista, California; Ribera del Duero
    2026-05-28 sent 26 producers to a "Urbanización Ribera del Duero"
    residential subdivision in Simancas (wrong centroid). Always pass
    the region's country_code when you know it."""
    payload = {"q": q, "format": "json", "limit": "1", "addressdetails": "1"}
    if country_code:
        payload["countrycodes"] = country_code.lower()
    params = urllib.parse.urlencode(payload)
    url = f"{NOMINATIM_URL}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        if isinstance(data, list) and data:
            d0 = data[0]
            return {
                "lat": float(d0["lat"]),
                "lon": float(d0["lon"]),
                "source": "nominatim",
                "queried": q,
                "display_name": d0.get("display_name", ""),
                "address_detail": d0.get("address") or {},
            }
    except Exception as exc:  # noqa: BLE001
        print(f"  [WARN] nominatim error for {q!r}: {exc}")
    return None


def _strip_venue_prefix(address: str) -> str | None:
    """Drop the part before the first comma if it doesn't start with a
    digit (i.e. it's a venue name, not a street number).

    `Ritz Paris, 15 Place Vendôme, 75001 Paris` -> `15 Place Vendôme, 75001 Paris`
    `15 Place Vendôme, 75001 Paris`             -> None (already starts with a digit)
    `Throughout Berlin`                         -> None (no comma to strip past)
    """
    if "," not in address:
        return None
    head, rest = address.split(",", 1)
    rest = rest.strip()
    head_stripped = head.strip()
    if not head_stripped or head_stripped[:1].isdigit():
        return None  # head is already a street number, prefix retry is pointless
    return rest


# Strip suite / unit / apt / # / building-letter modifiers from US-style
# addresses. Nominatim chokes on `1036 White St SW Suite A`; the same
# address without `Suite A` matches. Conservative: only the well-known
# trailing modifiers, never anything before the street name.
#
# Without re.VERBOSE on purpose — VERBOSE treats `#` as a comment char,
# which silently turned this regex into "match any whitespace + word"
# during dev. Lesson learned.
_SUITE_RE = re.compile(
    r"\s+(?:suite|ste\.?|unit|apt\.?|apartment|building|bldg\.?|fl\.?|floor|room|rm\.?|#)\s*[\w\-/]+",
    re.IGNORECASE,
)


def _strip_suite_unit(address: str) -> str:
    """Remove suite/unit/apt modifiers. Returns the cleaned string;
    identical to input if no modifier was present."""
    cleaned = _SUITE_RE.sub("", address).strip(" ,")
    return cleaned


_POSTCODE_RE = re.compile(
    r"""(?<![\w])(
        \d{5}(?:-\d{4})?         |  # US ZIP / ZIP+4
        \d{4,5}\s?[A-Z]{2}       |  # UK postal (W1F 7DE) — captured loose
        \d{5}                    |  # Generic 5-digit (DE/FR/IT/ES)
        [A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}  # UK full
    )(?![\w])""",
    re.IGNORECASE | re.VERBOSE,
)


def _extract_postcode(address: str) -> str | None:
    """Pull the postcode out of an address, if there is one. Used by the
    v3 fallback to query the postcode centroid when an exact match
    fails."""
    m = _POSTCODE_RE.search(address)
    return m.group(1).strip() if m else None


# When an address contains "Borough", "Township", "Suite", etc. patterns,
# the part before the postcode usually names the *actual* city (which
# may differ from the destination city — e.g. Brooklyn vs New York City,
# Avondale Estates vs Atlanta). Use the address's own city, not the
# destination, when we have one.
def _city_in_address(address: str) -> str | None:
    """Return the city slot in a "<street>, <city>, <region/postcode>"
    address, or None if the structure isn't there."""
    parts = [p.strip() for p in address.split(",")]
    if len(parts) < 3:
        return None
    # The "city" slot is the second from the end (region/postcode at end).
    candidate = parts[-2]
    # Reject if it looks like a region code or postcode rather than a city.
    if _POSTCODE_RE.search(candidate):
        return None
    if re.fullmatch(r"[A-Z]{2,3}", candidate.strip()):
        return None
    return candidate or None


def _clean_for_geocode_query(address: str) -> str:
    """Pre-process an entity.address to a Nominatim-friendlier query.

    Does NOT mutate the stored address (which keeps prose context for
    display). Only the query sent to Nominatim gets the cleaned form.

    Transforms (safe — preserves digit-bearing parens since those often
    ARE the real address):
      - "650 Gough Street (between McAllister & Fulton Streets)"
            -> "650 Gough Street"
      - "1235 6th Avenue North in Nashville's historic Germantown neighborhood"
            -> "1235 6th Avenue North"
      - "Acqualagna, Pesaro Urbino (130km from Rome)"
            -> "Acqualagna, Pesaro Urbino"
      - "100 Bridge Rd (Apt 5)"  (digit in parens, KEEP)
            -> "100 Bridge Rd (Apt 5)"
      - "Inside Penn Station (40 W 31st St)"  (digit in parens, KEEP)
            -> "Inside Penn Station (40 W 31st St)"

    Strategy chain still wraps this; if the cleaned canonical query
    doesn't resolve to a sanity-checked hit, the venue-prefix /
    suite-strip / postcode-centroid passes still run.
    """
    if not isinstance(address, str):
        return address
    # 1) Strip parens content UNLESS it contains digits (likely a real
    #    address slot like "Suite 5" or "40 W 31st St").
    cleaned = re.sub(
        r"\s*\(([^)]*)\)\s*",
        lambda m: " " if not re.search(r"\d", m.group(1)) else m.group(0),
        address,
    )
    # 2) Strip trailing prose tails that geocoders consistently choke on.
    PROSE_TAILS = (
        r",?\s+in\s+(the\s+)?[\w' .]+\s+(neighborhood|neighbourhood|district|quarter|zone|area)\s*$",
        r",?\s+between\s+[\w &]+(?:\s+and\s+[\w &]+)?\s*$",
        r",?\s+at\s+the\s+corner\s+of\s+[\w &]+(?:,?\s+in\s+[\w &]+)?\s*$",
        r",?\s+a\s+short\s+walk\s+from\s+[\w &']+\s*$",
        r",?\s+about\s+\d+\s+minutes?\s+(walk\s+)?from\s+[\w &']+\s*$",
    )
    for pat in PROSE_TAILS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    # 3) Collapse whitespace + trailing comma noise
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(",").strip()
    return cleaned or address


def _smart_city_join(address: str, destination_city: str) -> str:
    """Use the address's own city when present (avoids appending the
    destination city onto an address that already names a *different*
    one — e.g. "Avondale Estates, GA 30002" shouldn't have "Atlanta"
    bolted onto the end)."""
    own_city = _city_in_address(address)
    target_city = own_city or destination_city
    if not target_city or target_city.lower() in address.lower():
        return address
    return f"{address}, {target_city}"


def _geocode_one(address: str, city_name: str,
                  city_centroid: tuple[float, float] | None = None,
                  country_code: str | None = None) -> dict | None:
    """v4 geocoder fallback chain with city-centroid sanity check. Returns
    {'lat', 'lon', ...} or None.

    Strategies, in order. First hit wins; each pass annotates the cache
    entry with how it resolved so we can audit success patterns later.

      1. **canonical**: full address, smart-joined to its city
      2. **strip_venue_prefix**: drop the part before the first comma if
         it doesn't start with a digit (Ritz Paris → 15 Place Vendôme...)
      3. **strip_suite**: drop "Suite A", "Unit 5", "#1A", etc.
      4. **strip_suite + strip_venue_prefix**: both, for the long-tail
      5. **postcode_centroid**: query just the postcode (gives a coarse
         pin at the postcode level — better than no pin for intersections,
         building names, malformed entries)

    NEW (v4): each candidate result is sanity-checked against the city
    centroid. Anything more than MAX_DISTANCE_FROM_CITY_KM (100km default)
    from the centroid is rejected so we fall through to the next strategy
    instead of caching the bad coords. This catches Nominatim's country-
    centroid fallbacks (Greek venues geocoded to Lamia, NYC venues to
    Albany) and venue-name confusion ("Lower Camden Street, Dublin" -> NZ).

    Each pass costs one Nominatim call. Outer loop sleeps once per
    entity, so retries inside one entity need their own sleeps to stay
    under the 1 req/sec policy.
    """
    if not address.strip():
        return None

    # City-name aliases — local-language ↔ English (+ historic forms,
    # native scripts, common variants). When Nominatim returns
    # address_detail.city/town in the local language, the destination
    # English city_name won't match exactly; this table bridges them.
    # Keys are folded (lowercase, diacritics stripped) destination names.
    CITY_NAME_ALIASES = {
        # Western Europe
        "vienna":          ("wien",),
        "munich":          ("munchen", "münchen"),
        "cologne":         ("koln", "köln"),
        "nuremberg":       ("nurnberg", "nürnberg"),
        "frankfurt":       ("frankfurt am main",),
        "dusseldorf":      ("dusseldorf", "düsseldorf"),
        "naples":          ("napoli",),
        "florence":        ("firenze",),
        "venice":          ("venezia",),
        "rome":            ("roma",),
        "milan":            ("milano",),
        "turin":            ("torino",),
        "genoa":            ("genova",),
        "padua":            ("padova",),
        "lisbon":           ("lisboa",),
        "seville":          ("sevilla",),
        "san sebastián":    ("donostia",),
        "san sebastian":    ("donostia",),
        "brussels":         ("brussel", "bruxelles"),
        "antwerp":          ("antwerpen", "anvers"),
        "ghent":            ("gent", "gand"),
        "bruges":           ("brugge",),
        "the hague":        ("den haag", "'s-gravenhage"),
        "geneva":           ("geneve", "genève", "genf"),
        "basel":            ("basle", "bâle"),
        "lucerne":          ("luzern",),
        "bern":             ("berne",),

        # Central / Eastern Europe
        "prague":           ("praha",),
        "warsaw":           ("warszawa",),
        "krakow":           ("kraków",),
        "gdansk":           ("gdańsk",),
        "wroclaw":          ("wrocław",),
        "poznan":           ("poznań",),
        "lviv":             ("lvov", "lwow", "lwów", "lemberg"),
        "kyiv":             ("kiev", "kyïv"),
        "sofia":            ("софия",),
        "belgrade":         ("beograd",),
        "bucharest":        ("bucuresti", "bucurești"),
        "tallinn":          ("reval",),
        "vilnius":          ("wilno",),

        # Greece / Cyprus
        "athens":           ("athina", "αθήνα", "athínai"),
        "thessaloniki":     ("salonika", "thessalonike"),

        # Nordic
        "copenhagen":       ("kobenhavn", "københavn"),
        "stockholm":        ("stockholm city",),
        "gothenburg":       ("goteborg", "göteborg"),
        "malmo":            ("malmö",),
        "helsinki":         ("helsingfors",),
        "reykjavik":        ("reykjavík",),

        # Asia
        "tokyo":            ("東京", "tōkyō", "tokio"),
        "kyoto":            ("京都", "kyōto"),
        "osaka":            ("大阪", "ōsaka"),
        "fukuoka":          ("福岡",),
        "sapporo":          ("札幌",),
        "hiroshima":        ("広島",),
        "seoul":            ("서울",),
        "busan":            ("부산", "pusan"),
        "taipei":           ("台北", "taibei"),
        "beijing":          ("北京", "peking"),
        "shanghai":         ("上海",),
        "guangzhou":        ("广州", "canton"),
        "chengdu":          ("成都",),
        "xian":             ("西安", "xi'an", "sian"),
        "shenzhen":         ("深圳",),
        "hong kong":        ("香港", "xianggang"),
        "bangkok":          ("krung thep", "krungthep", "กรุงเทพมหานคร",
                              "phra nakhon"),
        "chiang mai":       ("เชียงใหม่",),
        "ho chi minh city": ("saigon", "sài gòn", "tp. hồ chí minh"),
        "hanoi":            ("ha noi", "hà nội"),
        "manila":           ("maynila",),

        # Middle East / North Africa
        "jerusalem":        ("yerushalayim", "al-quds"),
        "tel aviv":         ("tel-aviv", "tel aviv-yafo"),
        "beirut":           ("بيروت", "beyrouth"),
        "cairo":            ("al-qahira", "القاهرة"),
        "marrakech":        ("marrakesh", "مراكش"),
        "fez":              ("fes", "fès"),
        "casablanca":       ("الدار البيضاء",),
        "dubai":            ("دبي",),
        "doha":             ("الدوحة",),
        "riyadh":           ("ar-riyad", "الرياض"),
        "tunis":            ("تونس",),

        # Latin America
        "mexico city":      ("ciudad de méxico", "ciudad de mexico", "cdmx",
                              "mexico, d.f.", "méxico d.f.", "distrito federal"),
        "havana":           ("la habana",),
        "san jose":         ("san josé",),  # Costa Rica
        "buenos aires":     ("ciudad autónoma de buenos aires", "caba"),
        "sao paulo":        ("são paulo",),
        "rio de janeiro":   ("rio",),
        "salvador":         ("salvador da bahia",),

        # Misc
        "moscow":           ("moskva", "москва"),
        "saint petersburg": ("st petersburg", "st. petersburg",
                              "sankt-peterburg", "санкт-петербург"),
    }

    def _ok(hit: dict | None) -> bool:
        """Two-tier sanity-check on a Nominatim hit.

        Tier-1 distance (always applies):
            <=20km from centroid -> accept (close enough; name check unneeded)
            >MAX_DISTANCE_FROM_CITY_KM (50km) -> reject (country-fallback bug)

        Tier-2 city-name match (only for 20-50km hits):
            Nominatim's structured address.city/town/municipality/village
            must equal the destination city OR a known alias (Prague=Praha,
            Munich=München, Bangkok=Krung Thep, etc.). Catches same-named-
            town bugs ("Carrer del Palau" exists in Barcelona AND Moià).
        """
        if not hit:
            return False
        if not city_centroid:
            return True
        try:
            lat = float(hit["lat"])
            lng = float(hit["lon"])
        except (KeyError, TypeError, ValueError):
            return False
        d = _haversine_km(city_centroid[0], city_centroid[1], lat, lng)
        # Tier 1a: definitely too far
        if d > MAX_DISTANCE_FROM_CITY_KM:
            return False
        # Tier 1b: clearly in town, skip name check
        if d <= 20:
            return True
        # Tier 2: 20-50km from centroid — could be a same-name suburb,
        #
        # We check the *actual locality* slots (city / town / municipality
        # / village) for an EXACT match on the destination city. Loose
        # substring matching is wrong: it counts "lyon" inside
        # "chazelles-sur-lyon" or "bologna" as a province name. Wider slots
        # (county, state_district) we deliberately skip — Nominatim puts
        # the actual town name there when the venue is in a suburb, and
        # the county/state often contains the destination city's name as
        # a province (Bologna county for Imola, Madrid Comunidad for
        # Aranjuez).
        ad = hit.get("address_detail") or {}
        if not ad or not city_name:
            return True
        import unicodedata
        def _fold(s):
            if not isinstance(s, str):
                return ""
            return "".join(c for c in unicodedata.normalize("NFKD", s.lower())
                           if not unicodedata.combining(c))
        cn = _fold(city_name)
        # Accept the destination city or any known local-language alias
        # (Prague=Praha, Munich=München, Bangkok=Krung Thep, etc.).
        acceptable = {cn} | {_fold(a) for a in CITY_NAME_ALIASES.get(cn, ())}
        locality_slots = [_fold(ad.get(k, ""))
                          for k in ("city", "town", "municipality", "village")]
        if not any(s and s in acceptable for s in locality_slots):
            return False
        return True

    def _try(q: str, strategy: str, sleep_first: bool = False) -> dict | None:
        if sleep_first:
            time.sleep(SLEEP_SECONDS)
        hit = _nominatim_query(q, country_code=country_code)
        if hit:
            hit["strategy"] = strategy
            if _ok(hit):
                return hit
            # Reject and let the next strategy try.
            hit["_rejected_distance"] = round(_haversine_km(
                city_centroid[0], city_centroid[1], float(hit["lat"]), float(hit["lon"])
            ), 1) if city_centroid else None
            return None
        return None

    # Pre-clean: strip non-digit parens content + prose tails. Used for
    # all canonical-style passes; postcode_centroid still runs on the
    # raw address so a postcode buried in prose still gets extracted.
    cleaned = _clean_for_geocode_query(address)

    # Pass 1: full address, smart-joined.
    q = _smart_city_join(cleaned, city_name)
    hit = _try(q, "canonical")
    if hit:
        return hit

    # Pass 1b: only retry if cleaning actually changed the address —
    # otherwise the raw form was already tried in pass 1.
    if cleaned != address:
        q = _smart_city_join(address, city_name)
        hit = _try(q, "canonical_raw", sleep_first=True)
        if hit:
            return hit

    # Pass 2: venue prefix strip (Ritz Paris → 15 Place Vendôme).
    stripped = _strip_venue_prefix(cleaned)
    if stripped:
        q = _smart_city_join(stripped, city_name)
        hit = _try(q, "strip_venue_prefix", sleep_first=True)
        if hit:
            return hit

    # Pass 3: suite/unit strip (1036 White St SW Suite A → 1036 White St SW).
    desuited = _strip_suite_unit(cleaned)
    if desuited != cleaned:
        q = _smart_city_join(desuited, city_name)
        hit = _try(q, "strip_suite", sleep_first=True)
        if hit:
            return hit

        # Pass 4: combo strip — strip suite AND venue prefix.
        combined = _strip_venue_prefix(desuited)
        if combined and combined != stripped:
            q = _smart_city_join(combined, city_name)
            hit = _try(q, "strip_suite+strip_venue_prefix", sleep_first=True)
            if hit:
                return hit

    # Pass 5: postcode centroid. Gives a coarse pin which is fine for
    # intersection-only or unresolvable-by-design entries (festivals,
    # food tours whose precise venue we don't have). Skip when no
    # postcode is present — that's the truly-vague class ("Throughout X")
    # which correctly stays unpinnable.
    postcode = _extract_postcode(address)
    if postcode:
        q = f"{postcode}, {city_name}" if city_name else postcode
        hit = _try(q, "postcode_centroid", sleep_first=True)
        if hit:
            hit["coarse"] = True  # flag for downstream consumers
            return hit

    return None


def _collect_entities(only_city: str | None = None) -> list[tuple[str, str, str, str, tuple[float, float] | None, str | None]]:
    """Return list of (entity_slug, address, city_name, source_file_rel, city_centroid, country_code).

    Walks every entity-bearing JSON file. Skips entities with no slug or
    no address. Dedups by (address, city_name) — many entities share an
    address (markets, festivals at fixed venues).

    city_centroid is the (lat, lng) tuple from CITY_CENTROIDS for the
    sanity-check guard in _geocode_one; None when unknown city.

    country_code is the ISO-3166 code from COUNTRY_ISO (e.g. "fr", "es"),
    passed to Nominatim to prevent homonym-fallback bugs; None when the
    country slug isn't mapped.
    """
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str, str, str, tuple[float, float] | None, str | None]] = []
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            if only_city and city_dir.name != only_city:
                continue
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            city_name = (rdata.get("destination") or {}).get("name") or city_dir.name.replace("-", " ").title()
            centroid = CITY_CENTROIDS.get((country_dir.name, city_dir.name))
            country_code = COUNTRY_ISO.get(country_dir.name)
            for f in sorted((city_dir / "data").glob("*.json")):
                if f.name == "region.json":
                    continue
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                # Walk every list-of-entity field. Dietary uses nested dict
                # of lists; everything else is a flat list under a topic key.
                stack = [d]
                while stack:
                    node = stack.pop()
                    if isinstance(node, list):
                        for e in node:
                            if isinstance(e, dict) and e.get("slug") and e.get("address"):
                                addr = e["address"]
                                key = (addr.lower().strip(), city_name.lower().strip())
                                if key in seen:
                                    continue
                                seen.add(key)
                                out.append((e["slug"], addr, city_name, str(f.relative_to(REPO)), centroid, country_code))
                            elif isinstance(e, dict):
                                stack.append(e)
                    elif isinstance(node, dict):
                        for v in node.values():
                            if isinstance(v, (list, dict)):
                                stack.append(v)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None, help="Cap requests this run.")
    p.add_argument("--city", default=None, help="Restrict to one city slug.")
    args = p.parse_args()

    cache = _load_cache()
    targets = _collect_entities(only_city=args.city)
    n_success_in_cache = sum(1 for v in cache.values() if v.get("ok"))
    n_failed_in_cache = sum(1 for v in cache.values() if not v.get("ok"))
    print(
        f"Found {len(targets)} unique entity addresses to consider; "
        f"cache has {n_success_in_cache} successes and {n_failed_in_cache} prior failures."
    )
    if n_failed_in_cache:
        print(f"  Prior failures WILL be retried with the v2 algorithm (venue-prefix fallback).")

    queried = 0
    cache_hits = 0
    misses = 0
    recovered = 0  # prior failures we successfully geocoded this run
    for slug, addr, city_name, src, centroid, country_code in targets:
        if args.limit is not None and queried >= args.limit:
            print(f"  --limit {args.limit} reached; stopping.")
            break
        ck = _cache_key(addr, city_name)
        cached = cache.get(ck)
        if cached and cached.get("ok"):
            # Already geocoded successfully — but still sanity-check the
            # cached coords against the centroid. Old cache entries from
            # before the v4 guard may be country-fallbacks; if so, treat
            # as a miss and re-query.
            if centroid:
                try:
                    d_km = _haversine_km(centroid[0], centroid[1],
                                          float(cached["lat"]), float(cached["lon"]))
                    if d_km > MAX_DISTANCE_FROM_CITY_KM:
                        print(f"  [PURGE] stale outlier {addr!r}: cached coords {d_km:.0f}km from {city_name}")
                        cache.pop(ck, None)
                        # Fall through to re-geocode below.
                    else:
                        cache_hits += 1
                        continue
                except (KeyError, TypeError, ValueError):
                    cache_hits += 1
                    continue
            else:
                cache_hits += 1
                continue
        was_prior_failure = bool(cached) and not cached.get("ok")
        result = _geocode_one(addr, city_name, city_centroid=centroid, country_code=country_code)
        if result is None:
            cache[ck] = {"address": addr, "city": city_name, "ok": False, "source": "nominatim"}
            misses += 1
        else:
            cache[ck] = {"address": addr, "city": city_name, "ok": True, **result}
            if was_prior_failure:
                recovered += 1
        queried += 1
        # Persist every 25 lookups so a kill mid-run doesn't lose state.
        if queried % 25 == 0:
            _save_cache(cache)
            print(f"  ... {queried} queried ({misses} miss, {recovered} recovered), {cache_hits} cache hits — saved")
        time.sleep(SLEEP_SECONDS)

    _save_cache(cache)
    print(
        f"DONE. queried={queried} miss={misses} recovered_from_prior_fail={recovered} "
        f"cache_hits={cache_hits} cache_size={len(cache)}"
    )

    # Drop a human-readable failure report next to the cache so the
    # post-run review is one file open. Same path Lewis can grep.
    fail_report = REPO / "data" / "geocode-failures.txt"
    fails = [v for v in cache.values() if not v.get("ok")]
    if fails:
        lines = [f"# {len(fails)} addresses still unresolved after v2 algorithm.\n"]
        for v in sorted(fails, key=lambda x: (x.get("city", ""), x.get("address", ""))):
            lines.append(f"[{v.get('city', '?'):25}] {v.get('address', '')}\n")
        fail_report.write_text("".join(lines), encoding="utf-8")
        print(f"Wrote {fail_report} ({len(fails)} unresolved).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
