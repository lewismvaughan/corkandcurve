"""SEO helpers shared across page generators."""

import html as _html
import re as _re


def _rendered_len(s: str) -> int:
    """Length of a meta-description string AS GOOGLE COUNTS IT: HTML entities
    decoded so &#39; counts as 1 char, not 5."""
    return len(_html.unescape(s))


def title_truncate(s: str, max_len: int = 65) -> str:
    """Cap a <title> string at `max_len` rendered chars. Google truncates
    SERP titles around 50-65 chars on mobile / 60-70 on desktop; 65 is the
    safe upper bound.

    Strategy: drop the " | Cork & Curve" brand suffix first (saves 15
    chars without losing meaning). If still over, trim at last word
    boundary. Returns RAW (decoded) text; callers that embed in HTML
    should html.escape() after.
    """
    if not s:
        return s
    r = _html.unescape(s)
    if len(r) <= max_len:
        return r
    if " | Cork & Curve" in r:
        r2 = r.replace(" | Cork & Curve", "")
        if len(r2) <= max_len:
            return r2
        r = r2
    if len(r) <= max_len:
        return r
    cut = r[:max_len - 3].rfind(" ")
    if cut > 30:
        return r[:cut].rstrip(",;:- ")
    return r[:max_len]


_DANGLING_ALWAYS = frozenset({
    "and", "or", "but", "nor", "yet", "than",
    "the", "an", "this", "these", "those",
    "told", "covered",
})

_DANGLING_PREPOSITIONS = frozenset({
    "of", "to", "from", "in", "on", "at", "by", "with", "for",
    "into", "onto", "upon", "over", "under", "between", "among",
    "across", "through", "behind", "beside", "around", "near",
})


def _trim_dangling_tail(s: str, *, aggressive: bool = True) -> str:
    drop = _DANGLING_ALWAYS | _DANGLING_PREPOSITIONS if aggressive else _DANGLING_ALWAYS
    out = s.rstrip()
    while out:
        body = out.rstrip(".!?,;:- ")
        last_space = body.rfind(" ")
        if last_space < 0:
            break
        last_word = body[last_space + 1:].lower().rstrip(",;:-.")
        if last_word in drop:
            out = body[:last_space].rstrip(",;:- ")
            continue
        out = body
        break
    if out and out[-1] not in ".!?":
        out = out.rstrip(",;:- ") + "."
    return out


def _smart_truncate(s: str, max_len: int = 158) -> str:
    rendered = _html.unescape(s)
    if len(rendered) <= max_len:
        return _trim_dangling_tail(rendered, aggressive=False)
    window = rendered[:max_len + 1]
    m = list(_re.finditer(r"[.!?](?:\s|$)", window))
    if m:
        cut = m[-1].end()
        out = rendered[:cut].rstrip()
        if len(out) >= 120:
            return _trim_dangling_tail(out, aggressive=True)
    space = rendered[:max_len].rfind(" ")
    if space > 100:
        out = rendered[:space].rstrip(",;:- ").rstrip()
        return _trim_dangling_tail(out, aggressive=True)
    return _trim_dangling_tail(rendered[:max_len - 1].rstrip(), aggressive=True)


def meta_desc(*variants: str) -> str:
    in_range = [v for v in variants if 140 <= _rendered_len(v) <= 165]
    if in_range:
        return max(in_range, key=_rendered_len)
    under = [v for v in variants if _rendered_len(v) <= 165]
    if under:
        return max(under, key=_rendered_len)
    return _smart_truncate(min(variants, key=_rendered_len), max_len=158)
