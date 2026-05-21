#!/usr/bin/env python3
"""Normalize price_tier strings across every entity JSON.

Background — 2026-05-19: Lewis spotted that batch-3 cities (Lyon, Berlin,
Milan, Edinburgh, Naples) shipped with `price_tier` written as 'EUR EUR EUR'
or 'GBP GBP GBP' instead of the symbol form '€€€' / '£££'. Some entities
even shipped with 'E', 'EE', 'EEE'. The filter generator in
generate_extras.py exposes each unique price string as a filter chip,
which exploded the filter list with 12+ format variants.

This script walks every entity JSON, parses each price_tier string into a
tier integer (1-4), and rewrites it in the symbol form for the entity's
country. Idempotent — re-running on already-clean JSON is a no-op.

Symbol map (by country):
  france, italy, spain, germany               -> €
  united-kingdom                              -> £
  japan                                       -> ¥
  united-states, default                      -> $

Usage:
  python3 scripts/normalize_price_tiers.py             # walk every city
  python3 scripts/normalize_price_tiers.py --dry-run   # show changes only
  python3 scripts/normalize_price_tiers.py --country france --city lyon
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"

# Country slug -> primary currency symbol. Cities inherit their country's
# slug from the path, not from a JSON field. Add new countries here.
COUNTRY_SYMBOL = {
    "france": "€", "italy": "€", "spain": "€", "germany": "€",
    "netherlands": "€", "portugal": "€", "ireland": "€", "austria": "€",
    "united-kingdom": "£",
    "japan": "¥",
    "china": "¥", "taiwan": "¥",
    "switzerland": "CHF",  # CHF is conventional, not a single character
    "united-states": "$", "canada": "$", "mexico": "$",
}

# Already-canonical symbols — preserve. The filter chip generator wants
# strings like "€€€" verbatim, so any run of these characters is fine.
SYMBOL_CHARS = set("$€£¥") | {"CHF"}

# 3-letter ISO codes the agents sometimes spell out. Map to count==1 each.
ISO_CODES = {"USD", "EUR", "GBP", "JPY", "CHF", "CNY", "CAD", "MXN", "AUD", "NZD"}


def parse_tier(s: str) -> int:
    """Return the tier 1-4 implied by a free-form price string. 0 means
    'could not infer' — caller should leave the original alone."""
    if not s:
        return 0
    s = s.strip()
    # Symbol-only string (e.g. "€€€", "$$") — count the chars directly.
    if all(c in "$€£¥" for c in s):
        return min(4, len(s))
    # Tokens separated by spaces ("EUR EUR EUR", "GBP GBP")
    tokens = s.split()
    if all(t.upper() in ISO_CODES for t in tokens):
        return min(4, len(tokens))
    # Single-letter shorthand the agents sometimes use ("E", "EE", "EEE")
    # — single contiguous letter, length 1-4 of the same letter, with the
    # letter being a currency initial (E, G, U, J).
    if re.fullmatch(r"[EGUJ]{1,4}", s):
        return len(s)
    # Mixed (e.g. "EUR EE") — unparseable, leave alone.
    return 0


def canonicalize(s: str, country: str) -> str | None:
    """Return the canonical symbol form for a parseable price_tier, or
    None if it should be left alone."""
    if not s:
        return None
    tier = parse_tier(s)
    if tier == 0:
        return None
    # Already canonical (symbol-only and right length)?
    if all(c in "$€£¥" for c in s.strip()) and len(s.strip()) == tier:
        return None
    symbol = COUNTRY_SYMBOL.get(country, "$")
    if symbol == "CHF":
        # Switzerland: keep the 3-letter form but normalise spacing.
        return " ".join(["CHF"] * tier)
    return symbol * tier


def walk_entities(d):
    """Yield every dict in `d` that looks like an entity (has a `slug`
    key). Lets us catch price_tier on entities regardless of which
    parent-key list they're nested under."""
    if isinstance(d, dict):
        if "slug" in d and isinstance(d.get("slug"), str):
            yield d
        for v in d.values():
            yield from walk_entities(v)
    elif isinstance(d, list):
        for v in d:
            yield from walk_entities(v)


def normalize_file(path: Path, country: str, dry: bool = False) -> int:
    """Returns number of price_tier values rewritten in this file."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    n = 0
    for ent in walk_entities(d):
        pt = ent.get("price_tier")
        if not isinstance(pt, str):
            continue
        new = canonicalize(pt, country)
        if new is not None and new != pt:
            if dry:
                print(f"  {path.relative_to(REPO_ROOT)} {ent.get('slug')!r}: {pt!r} -> {new!r}")
            ent["price_tier"] = new
            n += 1
    if n and not dry:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)
    return n


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--country")
    p.add_argument("--city")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.country and args.city:
        targets = [(args.country, args.city)]
    else:
        targets = []
        for cdir in sorted(SITE_DATA.iterdir()):
            if not cdir.is_dir():
                continue
            for sdir in sorted(cdir.iterdir()):
                data = sdir / "data"
                if data.is_dir() and sdir.name != "data":
                    targets.append((cdir.name, sdir.name))

    total = 0
    for country, city in targets:
        data = SITE_DATA / country / city / "data"
        if not data.exists():
            continue
        n = 0
        for f in sorted(data.glob("*.json")):
            n += normalize_file(f, country, dry=args.dry_run)
        if n:
            print(f"[{country}/{city}] {'would rewrite' if args.dry_run else 'rewrote'} {n} price_tier values")
        total += n
    print(f"\nTotal price_tier values {'would change' if args.dry_run else 'changed'}: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
