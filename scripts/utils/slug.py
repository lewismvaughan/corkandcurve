"""Stable slug generation for entity URLs.

Slugs are URL-bearing identifiers. Once a slug is generated for an entry
and committed, it must NEVER change. Renaming the entry's display name
does not change the slug.

If an entity needs to move to a new slug (e.g., business renames),
add the old slug to its `aliases: []` list; generators emit a redirect.
"""

from __future__ import annotations

import re
import unicodedata


def slugify(text: str) -> str:
    """Convert text to a stable, URL-safe slug.

    - Normalizes unicode (NFKD), drops diacritics, so "Café" -> "cafe"
    - Lowercases
    - Replaces any non-[a-z0-9] run with a single hyphen
    - Strips leading/trailing hyphens
    - Returns empty string for empty/None input (caller must check)
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def unique_slug(base: str, existing: set) -> str:
    """Return `base`, suffixed with -2/-3/... if it collides with `existing`.
    Mutates `existing` to include the returned slug.
    """
    if not base:
        raise ValueError("Cannot generate unique slug from empty base")
    candidate = base
    n = 2
    while candidate in existing:
        candidate = f"{base}-{n}"
        n += 1
    existing.add(candidate)
    return candidate
