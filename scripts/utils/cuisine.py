"""Cuisine canonicalisation.

Maps the free-text `cuisine` field on a restaurant / casual-dining /
fine-dining entry to a controlled-vocabulary slug, so that all the
phrasing variants ("Bistro", "neo-bistro", "Bistro à vins") collapse
onto a single /cuisine/<slug>/ cross-cut page.

Source of truth: data/cuisines.json. Lookups are case-insensitive and
diacritic-insensitive.

Designed to scale: O(1) per lookup after a single-pass dict build at
import time. At 100k restaurant entries × 10 cuisines per page, the
lookup cost across a full site rebuild is microseconds.
"""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Optional, NamedTuple

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_VOCAB_PATH = _REPO_ROOT / "data" / "cuisines.json"


class CanonicalCuisine(NamedTuple):
    display: str
    slug: str


def _normalise(s: str) -> str:
    """Lowercase + strip diacritics. 'Café' -> 'cafe', 'Bistro à vins' -> 'bistro a vins'."""
    if not s:
        return ""
    s = s.strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )


@lru_cache(maxsize=1)
def _build_index() -> dict[str, CanonicalCuisine]:
    """Build a normalised-key -> CanonicalCuisine lookup table.

    Cached on first call. Subsequent calls are O(1).
    """
    with open(_VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    index: dict[str, CanonicalCuisine] = {}
    for row in vocab.get("cuisines", []):
        cc = CanonicalCuisine(display=row["canonical"], slug=row["slug"])
        index[_normalise(row["canonical"])] = cc
        for alias in row.get("aliases", []):
            index[_normalise(alias)] = cc
    return index


def canonicalise(raw_cuisine: str | None) -> Optional[CanonicalCuisine]:
    """Resolve a free-text cuisine string to its canonical (display, slug) pair.

    Returns None if the value is not in the controlled vocabulary. Callers
    decide how to handle that: cross-cut generator skips it (logs to
    unmapped), validator warns.
    """
    if not raw_cuisine:
        return None
    return _build_index().get(_normalise(raw_cuisine))


def all_canonical() -> list[CanonicalCuisine]:
    """Every canonical cuisine, sorted by display. Used by chrome page index."""
    seen: set[str] = set()
    out: list[CanonicalCuisine] = []
    for cc in _build_index().values():
        if cc.slug in seen:
            continue
        seen.add(cc.slug)
        out.append(cc)
    out.sort(key=lambda c: c.display.lower())
    return out
