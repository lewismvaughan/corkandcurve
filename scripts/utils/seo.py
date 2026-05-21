"""SEO helpers shared across page generators."""

import html as _html


def _rendered_len(s: str) -> int:
    """Length of a meta-description string AS GOOGLE COUNTS IT: HTML entities
    decoded so &#39; counts as 1 char, not 5."""
    return len(_html.unescape(s))


def meta_desc(*variants: str) -> str:
    """Pick the best meta-description variant for the SERP snippet length band.

    Prefers the longest variant whose rendered length sits in [140, 165]
    (Google's practical snippet sweet spot). Falls back to the longest
    variant <=165, else the shortest variant (last resort, will be truncated
    by Google).
    """
    in_range = [v for v in variants if 140 <= _rendered_len(v) <= 165]
    if in_range:
        return max(in_range, key=_rendered_len)
    under = [v for v in variants if _rendered_len(v) <= 165]
    if under:
        return max(under, key=_rendered_len)
    return min(variants, key=_rendered_len)
