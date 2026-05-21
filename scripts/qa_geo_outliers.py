#!/usr/bin/env python3
"""QA — compile every venue whose geocoded coords are >N km from the city
centroid, with a heuristic split between REAL GEOCODE BUGS (address says
the venue IS in the city, but coords disagree) and HONEST DAY-TRIPS
(address explicitly mentions a different town).

How to find issues with this:
    1. Run this script. It walks every /<country>/<city>/_pins.json,
       cross-refs each pin's coords against city.center, lists outliers.
    2. The "REAL GEOCODE BUGS" section is what to fix: the venue is
       genuinely in the city per its address string, but the geocoder
       returned wildly off coordinates (often country-centroid fallback
       or a misread token).
    3. The "DAY-TRIPS" section is informational — these are venues whose
       address explicitly says they're elsewhere (Boulder for a Denver
       guide, Carlsbad for a San Diego guide, etc.). Usually fine.

Run it any time you suspect map pins are landing in wrong places:
    python scripts/qa_geo_outliers.py
    python scripts/qa_geo_outliers.py --threshold 50
    python scripts/qa_geo_outliers.py --json /tmp/outliers.json

Notes:
- Threshold defaults to 30km. Most legit day-trips fall under 100km;
  >100km is almost always a bug.
- Same venue across N topic files shows up N times (each topic page
  re-geocodes the address); fixing the cache entry fixes all of them.
- After fixing, see `scripts/fix_geo_outliers.py` (separate script):
  purges bad cache entries by SHA-of-address, then re-geocodes.
"""

from __future__ import annotations

import argparse
import json
import sys
from math import radians, cos, sin, asin, sqrt
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
SITE_DATA = REPO / "site-data"
CACHE_PATH = REPO / "data" / "geocode-cache.json"


# City slug → set of tokens we expect to find in entity.address when the
# venue is genuinely IN that city (case-insensitive substring match).
# Pre-seeded for global tier-1/2 food cities — entries cost nothing if
# unused and let the QA script categorize future-shipped cities correctly
# without code edits.
EXPECTED_CITY_TOKENS: dict[str, list[str]] = {
    "paris": ["paris"],
    "lyon": ["lyon"],
    "marseille": ["marseille"],
    "rome": ["roma", "rome"],
    "milan": ["milano", "milan"],
    "naples": ["napoli", "naples"],
    "florence": ["firenze", "florence"],
    "bologna": ["bologna"],
    "venice": ["venezia", "venice"],
    "berlin": ["berlin"],
    "munich": ["munich", "munchen", "münchen"],
    "amsterdam": ["amsterdam"],
    "london": ["london"],
    "edinburgh": ["edinburgh"],
    "madrid": ["madrid"],
    "barcelona": ["barcelona"],
    "san-sebastian": ["donostia", "san sebastian", "san sebastián"],
    "lisbon": ["lisboa", "lisbon"],
    "athens": ["athina", "athens"],
    "budapest": ["budapest"],
    "prague": ["praha", "prague"],
    "dublin": ["dublin"],
    "copenhagen": ["københavn", "kobenhavn", "copenhagen"],
    "vienna": ["vienna", "wien"],
    "istanbul": ["istanbul"],
    "bangkok": ["bangkok"],
    "tokyo": ["tokyo"],
    "mexico-city": ["ciudad de mexico", "cdmx", "mexico city", "mexico, d.f."],
    "warsaw": ["warszawa", "warsaw"],
    "krakow": ["kraków", "krakow"],
    "gdansk": ["gdańsk", "gdansk"],
    "wroclaw": ["wrocław", "wroclaw"],
    "poznan": ["poznań", "poznan"],
    "new-york-city": ["new york"],
    "los-angeles": ["los angeles", "west hollywood", "hollywood"],
    "san-francisco": ["san francisco"],
    "chicago": ["chicago"],
    "boston": ["boston"],
    "miami": ["miami", "miami beach"],
    "austin": ["austin"],
    "nashville": ["nashville"],
    "new-orleans": ["new orleans"],
    "philadelphia": ["philadelphia"],
    "washington-dc": ["washington"],
    "atlanta": ["atlanta"],
    "seattle": ["seattle"],
    "portland": ["portland"],
    "denver": ["denver"],
    "houston": ["houston"],
    "minneapolis": ["minneapolis"],
    "charleston": ["charleston"],
    "san-diego": ["san diego"],
    "las-vegas": ["las vegas"],

    # ===== PRE-SEEDED FUTURE CITIES =====
    # Western Europe
    "brussels": ["brussel", "bruxelles", "brussels"],
    "antwerp": ["antwerpen", "anvers", "antwerp"],
    "ghent": ["gent", "gand", "ghent"],
    "bruges": ["brugge", "bruges"],
    "bordeaux": ["bordeaux"],
    "nice": ["nice"],
    "toulouse": ["toulouse"],
    "strasbourg": ["strasbourg"],
    "nantes": ["nantes"],
    "montpellier": ["montpellier"],
    "lille": ["lille"],
    "hamburg": ["hamburg"],
    "cologne": ["koln", "köln", "cologne"],
    "frankfurt": ["frankfurt"],
    "stuttgart": ["stuttgart"],
    "dusseldorf": ["dusseldorf", "düsseldorf"],
    "dresden": ["dresden"],
    "leipzig": ["leipzig"],
    "nuremberg": ["nurnberg", "nürnberg", "nuremberg"],
    "genoa": ["genova", "genoa"],
    "verona": ["verona"],
    "turin": ["torino", "turin"],
    "palermo": ["palermo"],
    "catania": ["catania"],
    "bari": ["bari"],
    "trieste": ["trieste"],
    "padua": ["padova", "padua"],
    "valencia": ["valencia"],
    "seville": ["sevilla", "seville"],
    "granada": ["granada"],
    "bilbao": ["bilbao", "bilbo"],
    "malaga": ["málaga", "malaga"],
    "salamanca": ["salamanca"],
    "porto": ["porto"],
    "rotterdam": ["rotterdam"],
    "the-hague": ["den haag", "the hague", "'s-gravenhage"],
    "utrecht": ["utrecht"],
    "zurich": ["zürich", "zurich"],
    "geneva": ["genève", "geneve", "geneva"],
    "basel": ["basel", "bâle", "basle"],
    "lucerne": ["luzern", "lucerne"],
    "bern": ["bern", "berne"],
    "galway": ["galway"],
    "cork": ["cork"],
    "manchester": ["manchester"],
    "liverpool": ["liverpool"],
    "glasgow": ["glasgow"],
    "bristol": ["bristol"],
    "cardiff": ["cardiff"],
    "belfast": ["belfast"],
    "oxford": ["oxford"],
    "cambridge": ["cambridge"],
    "thessaloniki": ["thessaloniki", "salonika"],
    "valletta": ["valletta"],

    # Nordic + Baltic
    "stockholm": ["stockholm"],
    "gothenburg": ["göteborg", "goteborg", "gothenburg"],
    "malmo": ["malmö", "malmo"],
    "oslo": ["oslo"],
    "bergen": ["bergen"],
    "helsinki": ["helsinki", "helsingfors"],
    "reykjavik": ["reykjavík", "reykjavik"],
    "tallinn": ["tallinn"],
    "riga": ["riga", "rīga"],
    "vilnius": ["vilnius"],

    # Central / Eastern Europe
    "salzburg": ["salzburg"],
    "innsbruck": ["innsbruck"],
    "brno": ["brno"],
    "debrecen": ["debrecen"],
    "bucharest": ["bucurești", "bucuresti", "bucharest"],
    "sofia": ["sofia", "софия"],
    "belgrade": ["beograd", "belgrade"],
    "zagreb": ["zagreb"],
    "split": ["split"],
    "dubrovnik": ["dubrovnik"],
    "ljubljana": ["ljubljana"],
    "sarajevo": ["sarajevo"],
    "kyiv": ["kyiv", "kiev"],
    "lviv": ["lviv", "lvov"],

    # Asia
    "beijing": ["beijing", "北京", "peking"],
    "shanghai": ["shanghai", "上海"],
    "chengdu": ["chengdu", "成都"],
    "xian": ["xi'an", "xian", "西安"],
    "guangzhou": ["guangzhou", "广州", "canton"],
    "shenzhen": ["shenzhen", "深圳"],
    "hong-kong": ["hong kong", "香港"],
    "osaka": ["osaka", "大阪"],
    "kyoto": ["kyoto", "京都"],
    "hiroshima": ["hiroshima", "広島"],
    "sapporo": ["sapporo", "札幌"],
    "fukuoka": ["fukuoka", "福岡"],
    "okinawa": ["okinawa", "沖縄"],
    "seoul": ["seoul", "서울"],
    "busan": ["busan", "pusan", "부산"],
    "taipei": ["taipei", "台北"],
    "singapore": ["singapore"],
    "kuala-lumpur": ["kuala lumpur", "kl"],
    "penang": ["penang", "pulau pinang"],
    "jakarta": ["jakarta"],
    "bali": ["bali", "denpasar", "ubud"],
    "manila": ["manila", "maynila"],
    "hanoi": ["hanoi", "hà nội", "ha noi"],
    "ho-chi-minh-city": ["ho chi minh", "hcmc", "saigon", "sài gòn"],
    "da-nang": ["da nang", "đà nẵng"],
    "phnom-penh": ["phnom penh"],
    "siem-reap": ["siem reap"],
    "yangon": ["yangon", "rangoon"],
    "chiang-mai": ["chiang mai", "เชียงใหม่"],
    "phuket": ["phuket"],
    "colombo": ["colombo"],
    "kathmandu": ["kathmandu"],
    "mumbai": ["mumbai", "bombay"],
    "delhi": ["delhi", "new delhi"],
    "bangalore": ["bangalore", "bengaluru"],
    "kolkata": ["kolkata", "calcutta"],
    "chennai": ["chennai", "madras"],
    "goa": ["goa", "panaji"],

    # Middle East / North Africa
    "tel-aviv": ["tel aviv", "tel-aviv"],
    "jerusalem": ["jerusalem", "yerushalayim"],
    "beirut": ["beirut", "بيروت"],
    "amman": ["amman", "عمّان"],
    "dubai": ["dubai", "دبي"],
    "abu-dhabi": ["abu dhabi", "أبوظبي"],
    "doha": ["doha", "الدوحة"],
    "riyadh": ["riyadh", "الرياض"],
    "cairo": ["cairo", "القاهرة"],
    "marrakech": ["marrakech", "marrakesh", "مراكش"],
    "casablanca": ["casablanca", "الدار البيضاء"],
    "fez": ["fez", "fes", "fès"],
    "tunis": ["tunis"],

    # Africa
    "cape-town": ["cape town", "kaapstad"],
    "johannesburg": ["johannesburg", "joburg", "jozi"],
    "nairobi": ["nairobi"],
    "addis-ababa": ["addis ababa", "addis abeba"],
    "accra": ["accra"],
    "lagos": ["lagos"],
    "dakar": ["dakar"],

    # Latin America
    "buenos-aires": ["buenos aires", "caba"],
    "mendoza": ["mendoza"],
    "rio-de-janeiro": ["rio de janeiro", "rio"],
    "sao-paulo": ["são paulo", "sao paulo"],
    "salvador": ["salvador"],
    "lima": ["lima"],
    "cusco": ["cusco", "cuzco"],
    "arequipa": ["arequipa"],
    "bogota": ["bogotá", "bogota"],
    "medellin": ["medellín", "medellin"],
    "cartagena": ["cartagena"],
    "quito": ["quito"],
    "santiago": ["santiago"],
    "montevideo": ["montevideo"],
    "la-paz": ["la paz"],
    "guatemala-city": ["guatemala city", "guatemala"],
    "antigua": ["antigua"],
    "san-jose": ["san josé", "san jose"],
    "panama-city": ["panamá", "panama"],
    "havana": ["havana", "la habana"],
    "santo-domingo": ["santo domingo"],
    "oaxaca": ["oaxaca"],
    "guadalajara": ["guadalajara"],
    "monterrey": ["monterrey"],
    "merida": ["mérida", "merida"],
    "puebla": ["puebla"],
    "san-miguel-de-allende": ["san miguel de allende"],
    "puerto-vallarta": ["puerto vallarta"],

    # North America
    "toronto": ["toronto"],
    "montreal": ["montréal", "montreal"],
    "vancouver": ["vancouver"],
    "quebec-city": ["québec", "quebec"],
    "ottawa": ["ottawa"],
    "calgary": ["calgary"],
    "phoenix": ["phoenix"],
    "salt-lake-city": ["salt lake city"],
    "detroit": ["detroit"],
    "cleveland": ["cleveland"],
    "pittsburgh": ["pittsburgh"],
    "indianapolis": ["indianapolis"],
    "san-antonio": ["san antonio"],
    "kansas-city": ["kansas city"],
    "saint-louis": ["st. louis", "saint louis", "st louis"],
    "tampa": ["tampa"],
    "orlando": ["orlando"],
    "honolulu": ["honolulu"],
    "savannah": ["savannah"],
    "santa-fe": ["santa fe"],
    "richmond": ["richmond"],
    "milwaukee": ["milwaukee"],
    "raleigh": ["raleigh"],
    "providence": ["providence"],

    # Oceania
    "sydney": ["sydney"],
    "melbourne": ["melbourne"],
    "brisbane": ["brisbane"],
    "perth": ["perth"],
    "adelaide": ["adelaide"],
    "hobart": ["hobart"],
    "auckland": ["auckland"],
    "wellington": ["wellington"],
    "queenstown": ["queenstown"],
}


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


def _slug_to_address_index() -> dict[tuple[str, str], str]:
    """Build (city_slug, entity_slug) → entity.address from site-data so we
    can show the source address alongside the suspect coords."""
    out: dict[tuple[str, str], str] = {}
    for country_dir in SITE_DATA.iterdir():
        if not country_dir.is_dir():
            continue
        for city_dir in country_dir.iterdir():
            if not city_dir.is_dir():
                continue
            for f in (city_dir / "data").glob("*.json"):
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                _walk_into(d, city_dir.name, out)
    return out


def _walk_into(node, city_slug, out, depth=0):
    if depth > 6:
        return
    if isinstance(node, list):
        for e in node:
            if isinstance(e, dict) and e.get("slug") and e.get("address"):
                out[(city_slug, e["slug"])] = e["address"]
            elif isinstance(e, dict):
                _walk_into(e, city_slug, out, depth + 1)
    elif isinstance(node, dict):
        for v in node.values():
            _walk_into(v, city_slug, out, depth + 1)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--threshold", type=float, default=30,
                   help="Distance in km from city centroid above which a pin is flagged (default 30).")
    p.add_argument("--json", default=None,
                   help="Optional path to write the full outlier list as JSON.")
    p.add_argument("--bugs-only", action="store_true",
                   help="Print only the REAL-BUG section (skip the day-trips list).")
    p.add_argument("--unresolved", action="store_true",
                   help="Also list every entity without a pin, per city.")
    args = p.parse_args()

    addr_index = _slug_to_address_index()
    cache = {}
    if CACHE_PATH.exists():
        try:
            cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    cache_by_addr = {v.get("address"): v for v in cache.values() if isinstance(v, dict)}

    outliers: list[dict] = []
    for pins_path in sorted(CONTENT.glob("*/*/_pins.json")):
        try:
            d = json.loads(pins_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        city = d.get("city", {})
        center = city.get("center")
        if not isinstance(center, list) or len(center) != 2:
            continue
        clat, clng = center
        for pin in d.get("pins", []):
            lat = pin.get("lat")
            lng = pin.get("lng")
            if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
                continue
            dist = haversine_km(clat, clng, lat, lng)
            if dist < args.threshold:
                continue
            addr = addr_index.get((city["slug"], pin["slug"]), "?")
            cache_hit = cache_by_addr.get(addr) or {}
            outliers.append({
                "city": city["slug"],
                "country": city.get("country"),
                "slug": pin["slug"],
                "name": pin["name"],
                "topic": pin.get("topic"),
                "entity_address": addr,
                "geocoded_lat": lat,
                "geocoded_lng": lng,
                "distance_km": round(dist, 1),
                "cache_queried": cache_hit.get("queried"),
                "cache_source": cache_hit.get("source"),
                "cache_retry": cache_hit.get("retry"),
            })

    # Split into real-bugs vs day-trips by whether entity.address contains
    # any of the expected city-name tokens.
    real_bugs: list[dict] = []
    day_trips: list[dict] = []
    for o in outliers:
        addr_lc = (o["entity_address"] or "").lower()
        # Lookup priority: explicit override, else slug-as-tokens
        # (e.g. "san-diego" -> ["san diego"]) which works for the vast
        # majority of city names. Explicit entries only needed when the
        # local-language form differs from the slug (Tokyo/東京,
        # Munich/München, Kyiv/Kiev, etc.).
        tokens = EXPECTED_CITY_TOKENS.get(o["city"], [o["city"].replace("-", " ")])
        if any(t in addr_lc for t in tokens):
            real_bugs.append(o)
        else:
            day_trips.append(o)
    real_bugs.sort(key=lambda x: -x["distance_km"])
    day_trips.sort(key=lambda x: -x["distance_km"])

    # ---- Unresolved (no-pin) audit: every entity with an address that
    # isn't on any map. Two sources:
    #   1. Cache has the (address, city) entry marked ok=False
    #   2. Cache has no entry for this entity at all (never queried)
    # Build a (city_slug, name) → (country_slug, address) index from
    # site-data, then check each address against the cache by SHA(addr|city).
    import hashlib
    unresolved_by_city: dict[str, list[dict]] = {}
    total_entities = 0
    total_with_pin = 0
    # Build cache lookup by SHA key — same as geocode_entities._cache_key
    for cd in sorted(SITE_DATA.iterdir()):
        if not cd.is_dir():
            continue
        for ci in sorted(cd.iterdir()):
            if not ci.is_dir():
                continue
            rj = ci / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                rdata = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            city_name = (rdata.get("destination") or {}).get("name") or ci.name.replace("-", " ").title()
            # Walk all entities in city
            seen = set()
            for f in (ci / "data").glob("*.json"):
                if f.name == "region.json":
                    continue
                try:
                    payload = json.loads(f.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                stack = [payload]
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
                                total_entities += 1
                                ck = hashlib.sha1(f"{key[0]}|{key[1]}".encode()).hexdigest()
                                hit = cache.get(ck)
                                if hit and hit.get("ok"):
                                    total_with_pin += 1
                                else:
                                    unresolved_by_city.setdefault(ci.name, []).append({
                                        "slug": e["slug"],
                                        "name": e.get("name", ""),
                                        "address": addr,
                                        "status": "failed" if hit else "never_queried",
                                    })
                            elif isinstance(e, dict):
                                stack.append(e)
                    elif isinstance(node, dict):
                        for v in node.values():
                            if isinstance(v, (list, dict)):
                                stack.append(v)

    total_unresolved = sum(len(v) for v in unresolved_by_city.values())
    pct_mapped = (100 * total_with_pin / total_entities) if total_entities else 0

    print(f"=== Geo QA — outliers + unresolved ===")
    print(f"Coverage: {total_with_pin}/{total_entities} unique-address entities mapped ({pct_mapped:.1f}%)")
    print(f"Unresolved: {total_unresolved} entities across {len(unresolved_by_city)} cities have no pin")
    print(f"  (either Nominatim failed OR the city hasn't been geocoded yet — run scripts/geocode_entities.py --city <slug>)")
    print()
    print(f"=== Outliers (pin >{args.threshold:.0f} km from city centroid) ===")
    print(f"Total outliers: {len(outliers)}  |  Real bugs: {len(real_bugs)}  |  Day-trips: {len(day_trips)}")
    print()
    print(f"--- REAL GEOCODE BUGS ({len(real_bugs)}): address says in-city, coords disagree ---")
    print(f"{'CITY':16} {'DIST':>8}  {'TOPIC':14}  SLUG / ADDRESS")
    for o in real_bugs:
        print(f"{o['city']:16} {o['distance_km']:>7.1f}km  [{o['topic']:12}]  {o['slug']}")
        print(f"{'':16} {'':>8}  {'':14}    addr={o['entity_address']!r}")
        if o.get("cache_queried") and o["cache_queried"] != o["entity_address"]:
            print(f"{'':16} {'':>8}  {'':14}    queried as: {o['cache_queried']!r}  (retry={o['cache_retry']})")
        print(f"{'':16} {'':>8}  {'':14}    geocoded -> ({o['geocoded_lat']}, {o['geocoded_lng']})")
    if not args.bugs_only:
        print()
        print(f"--- DAY-TRIPS ({len(day_trips)}): address explicitly mentions another town ---")
        for o in day_trips:
            print(f"{o['city']:16} {o['distance_km']:>7.1f}km  [{o['topic']:12}]  {o['slug']} | {o['entity_address']}")

    if args.unresolved:
        print()
        print(f"--- UNRESOLVED ({total_unresolved}): no pin, no map presence ---")
        for cs, items in sorted(unresolved_by_city.items()):
            print(f"  [{cs}] ({len(items)} unresolved)")
            for it in items[:5]:
                print(f"    {it['status']:14} {it['slug']:38} | {it['address'][:60]}")
            if len(items) > 5:
                print(f"    ... +{len(items)-5} more")

    if args.json:
        Path(args.json).write_text(
            json.dumps({
                "threshold_km": args.threshold,
                "coverage": {"mapped": total_with_pin, "total": total_entities, "pct": pct_mapped},
                "real_bugs": real_bugs,
                "day_trips": day_trips,
                "unresolved_by_city": unresolved_by_city,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nWrote {args.json}")

    # Exit code matches real-bug count so it can be used as a CI soft gate.
    return 0 if not real_bugs else 1


if __name__ == "__main__":
    sys.exit(main())
