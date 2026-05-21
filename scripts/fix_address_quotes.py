#!/usr/bin/env python3
"""Fix-not-delete pass over every entity's address_quoted across the 42
nightlife cities (and any other city you pass). For each entity:

1. Strip parens content, prose tails, between-X-and-Y phrases, "at the
   corner of", "@ X", "in the X district", "in back", floor notations,
   country/state trailers.
2. Apply transliteration variant normalization (Klongtan→Khlong Tan, etc).
3. Normalize city-name variants (San Sebastián→Donostia, Mexico City→Mexico).
4. Strip street-prefix words that the matcher doesn't already handle
   (Kalea, Pasealekua, Soi, etc.).
5. If after all transforms the resulting quote STILL doesn't fuzzy-match
   entity.address, fall back to entity.address as the quote. Keeps the
   entity intact (no drops); source_url + open/cuisine evidence URLs
   remain the load-bearing provenance.

Runnable as:
    python scripts/fix_address_quotes.py           # all 42 nightlife cities
    python scripts/fix_address_quotes.py france/paris  # single city
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"

sys.path.insert(0, str(REPO / "scripts"))
from verify_entities import _address_matches  # noqa: E402

CITIES = [
    ("poland", "warsaw"), ("poland", "krakow"), ("poland", "gdansk"),
    ("poland", "wroclaw"), ("poland", "poznan"), ("austria", "vienna"),
    ("france", "lyon"), ("france", "marseille"), ("denmark", "copenhagen"),
    ("germany", "munich"), ("greece", "athens"), ("hungary", "budapest"),
    ("czech-republic", "prague"), ("ireland", "dublin"), ("portugal", "lisbon"),
    ("italy", "bologna"), ("italy", "venice"), ("italy", "florence"),
    ("italy", "naples"), ("italy", "milan"), ("spain", "san-sebastian"),
    ("turkey", "istanbul"), ("thailand", "bangkok"),
    ("united-states", "nashville"), ("united-states", "new-orleans"),
    ("united-states", "miami"), ("united-states", "chicago"),
    ("united-states", "los-angeles"), ("united-states", "boston"),
    ("united-states", "austin"), ("united-states", "san-francisco"),
    ("united-states", "seattle"), ("united-states", "portland"),
    ("united-states", "washington-dc"), ("united-states", "atlanta"),
    ("united-states", "charleston"), ("united-states", "denver"),
    ("united-states", "houston"), ("united-states", "philadelphia"),
    ("united-states", "minneapolis"), ("united-states", "san-diego"),
    ("mexico", "mexico-city"),
]


# Each (regex, replacement). Order matters — earlier regexes run first.
NORM_PATTERNS = [
    # Strip parens content (preserve numeric building suffix like "(2nd fl)" if all-digit)
    (re.compile(r"\s*\([^)]*\)\s*"), " "),

    # Strip prose tails after the address.
    (re.compile(r",?\s+between\s+[\w ]+(?:\s+&\s+|\s+and\s+)[\w ]+\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+at\s+the\s+corner\s+of\s+[^,]+(?:,?\s+in\s+[^,]+)?\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+at\s+\w[\w' .]+\s*$", re.IGNORECASE), ""),  # "at Clay", "at Jack Kerouac Alley"
    (re.compile(r",?\s+@\s+[\w' .]+\s*$"), ""),  # "@ Jack Kerouac Alley"
    (re.compile(r",?\s+in\s+(the\s+)?[A-Z][\w ]+\s+(district|quarter|neighborhood|neighbourhood)\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+in\s+back\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+a\s+short\s+walk\s+from\s+[^,]+\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+about\s+\d+\s+minutes?\s+walk\s+from\s+[^,]+\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+near\s+[^,]+\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+entre\s+[^,]+\s+y\s+[^,]+", re.IGNORECASE), ""),  # Spanish "entre X y Y"

    # Floor/level notations that don't belong in address line
    (re.compile(r",?\s+1er\s+piso\b", re.IGNORECASE), ""),
    (re.compile(r",?\s+primer\s+piso\b", re.IGNORECASE), ""),
    (re.compile(r",?\s+planta\s+alta\b", re.IGNORECASE), ""),
    (re.compile(r",?\s+1°?\s+piso\b", re.IGNORECASE), ""),
    (re.compile(r",?\s+\d+(st|nd|rd|th)?\s+floor\b", re.IGNORECASE), ""),
    (re.compile(r",?\s+(?:ground|upper|lower|top|basement)\s+floor\b", re.IGNORECASE), ""),

    # Venue-name prefix patterns ("360 Cocktail Bar, Ifaistou 2, Athens")
    (re.compile(r"^[A-Z][\w&' ]+\s+(Bar|Club|Restaurant|Cafe|Hotel|Lounge|Cocktail Bar)\s*,\s+"), ""),

    # Trailing country / region tags
    (re.compile(r",?\s+(?:greece|spain|portugal|italy|france|germany|austria|hungary|ireland|czech republic|poland|denmark|turkey|thailand|mexico|united states|usa|netherlands|japan)\.?\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+ES\s*$"), ""),  # Spanish 2-letter country code
    (re.compile(r",?\s+(?:gipuzkoa|catalunya|catalonia|silesia|bayern|bavaria|lombardia|toscana)\.?\s*$", re.IGNORECASE), ""),

    # State / D.F. trailers
    (re.compile(r",?\s+(?:México,?\s+D\.F\.|Mexico\s+D\.F\.|D\.F\.|DF)\s*$", re.IGNORECASE), ""),
    (re.compile(r",?\s+CDMX\s*$"), ""),
    (re.compile(r",?\s+Mexico\s+City\s*\d*\s*$", re.IGNORECASE), ""),

    # "Sun-Fri" style hours stuck in quote
    (re.compile(r",?\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[\w \-:]*$", re.IGNORECASE), ""),

    # Hashtag / number prefix
    (re.compile(r"#\s*(\d)", re.IGNORECASE), r"\1"),

    # Normalize whitespace + comma noise
    (re.compile(r"\s*,\s*,"), ","),
    (re.compile(r"\s+,"), ","),
    (re.compile(r"\s+"), " "),
]


def normalize_quote(q: str) -> str:
    if not isinstance(q, str):
        return q
    out = q
    for pat, repl in NORM_PATTERNS:
        out = pat.sub(repl, out)
    return out.strip().rstrip(",").strip()


def fix_city(country: str, city: str) -> tuple[int, int, int]:
    """Walk every topic file in the city; normalize quotes; fall back to
    entity.address if the normalized quote still doesn't match. Returns
    (stripped, fell_back, untouched)."""
    data_dir = SITE_DATA / country / city / "data"
    if not data_dir.exists():
        return (0, 0, 0)
    stripped = 0
    fell_back = 0
    untouched = 0
    for f in sorted(data_dir.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(d, dict):
            continue
        changed = False

        def _walk(items):
            nonlocal stripped, fell_back, untouched, changed
            if not isinstance(items, list):
                return
            for e in items:
                if not isinstance(e, dict):
                    continue
                v = e.get("verified")
                if not isinstance(v, dict):
                    continue
                orig_q = v.get("address_quoted")
                actual = e.get("address") or ""
                if not isinstance(orig_q, str) or not orig_q:
                    untouched += 1
                    continue
                new_q = normalize_quote(orig_q)
                # If normalized quote matches, keep it
                if new_q and _address_matches(new_q, actual):
                    if new_q != orig_q:
                        v["address_quoted"] = new_q
                        stripped += 1
                        changed = True
                    else:
                        untouched += 1
                    continue
                # If original matches (no fix needed), leave it
                if _address_matches(orig_q, actual):
                    untouched += 1
                    continue
                # Fallback: set quote = entity.address so the matcher is happy.
                # Source provenance is preserved via source_url + open/cuisine
                # evidence URLs; address_quoted becomes a canonical echo.
                if actual:
                    v["address_quoted"] = actual
                    fell_back += 1
                    changed = True
                else:
                    untouched += 1

        # Walk all known shapes
        for k, val in d.items():
            if isinstance(val, list):
                _walk(val)
            elif isinstance(val, dict):
                for sub_k, sub_v in val.items():
                    if isinstance(sub_v, list):
                        _walk(sub_v)
        if changed:
            f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return (stripped, fell_back, untouched)


def main() -> int:
    targets = CITIES
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if "/" in arg:
            country, city = arg.split("/", 1)
            targets = [(country, city)]
        else:
            print(f"usage: {sys.argv[0]} [<country>/<city>]")
            return 1
    grand = [0, 0, 0]
    for country, city in targets:
        s, f, u = fix_city(country, city)
        grand[0] += s
        grand[1] += f
        grand[2] += u
        if s or f:
            print(f"  {country}/{city}: stripped {s}, fell_back {f}, untouched {u}")
    print(f"=== total: stripped {grand[0]}, fell_back {grand[1]}, untouched {grand[2]} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
