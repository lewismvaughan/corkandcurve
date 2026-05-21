"""Shared client-side filter widget for list-everything index pages.

Returns a self-contained HTML snippet: a search <input> + a small inline
<script> that filters items in a target container by text match.

Usage: inject the returned string into a page body just BEFORE the
container that holds the list. Add an `id="<id>"` to that container so
the input can target it.

The script is idempotent — re-running it on an already-wired input is a
no-op (gates on a `data-wired` attribute).
"""

import html


def filter_search_widget(*, target_id: str, item_selector: str = "li, .tj-entity-card, .tj-card",
                          placeholder: str = "Filter…",
                          aria_label: str = "Filter list",
                          with_sort: bool = True) -> str:
    """Render input + (optional) sort dropdown + inline script.
    target_id is the DOM id of the container holding the filterable
    items. item_selector picks the children to show/hide AND sort.

    When with_sort=True, a <select> appears next to the input with options:
      - Editor score, high to low (default)
      - Editor score, low to high
      - Name, A→Z
      - Name, Z→A

    Sort axis reads each item's data-score (numeric) and data-name (string)
    attributes — added by entity-card emitters. Items without those
    attributes fall back to extracting from .tj-entity-score / heading text.
    """
    sort_html = ""
    if with_sort:
        sort_html = (
            f'<select class="tj-filter-sort-select" '
            f'aria-label="Sort list" '
            f'data-filter-target="#{html.escape(target_id)}" '
            f'data-filter-item="{html.escape(item_selector)}" '
            'style="padding:10px 14px;border:1px solid var(--tj-border);'
            'border-radius:var(--tj-radius);background:var(--tj-surface);'
            'color:inherit;font-size:1rem;margin-left:8px;">'
            '<option value="score-desc">Score (high to low)</option>'
            '<option value="score-asc">Score (low to high)</option>'
            '<option value="name-asc">Name (A→Z)</option>'
            '<option value="name-desc">Name (Z→A)</option>'
            '<option value="price-asc">Price (low to high)</option>'
            '<option value="price-desc">Price (high to low)</option>'
            '</select>'
        )
    return (
        '<div class="tj-filter-search" style="margin:12px 0 16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">'
        '<input type="search" autocomplete="off" spellcheck="false" '
        'class="tj-filter-search-input" '
        f'placeholder="{html.escape(placeholder)}" '
        f'aria-label="{html.escape(aria_label)}" '
        f'data-filter-target="#{html.escape(target_id)}" '
        f'data-filter-item="{html.escape(item_selector)}" '
        'style="flex:1 1 280px;min-width:220px;padding:10px 14px;'
        'border:1px solid var(--tj-border);border-radius:var(--tj-radius);'
        'background:var(--tj-surface);color:inherit;font-size:1rem;">'
        + sort_html +
        '</div>'
        '<script>(function(){'
        'function getScore(el){'
        'var d=el.getAttribute("data-score");'
        'if(d!==null&&d!==""){var n=parseFloat(d);if(!isNaN(n))return n;}'
        'var s=el.querySelector(".tj-entity-score");'
        'if(s){var m=(s.textContent||"").match(/(\\d+(?:\\.\\d+)?)/);'
        'if(m)return parseFloat(m[1]);}'
        'return -Infinity;'
        '}'
        'function getName(el){'
        'var d=el.getAttribute("data-name");'
        'if(d)return d.toLowerCase();'
        'var h=el.querySelector("h1,h2,h3,h4,strong");'
        'return ((h?h.textContent:el.textContent)||"").trim().toLowerCase();'
        '}'
        'function getPrice(el){'
        'var d=el.getAttribute("data-price");'
        'if(d!==null&&d!==""){var n=parseFloat(d);if(!isNaN(n))return n;}'
        'return null;'
        '}'
        'function sortItems(t,sel,mode){'
        'var items=Array.prototype.slice.call(t.querySelectorAll(sel));'
        'if(!items.length)return;'
        'var parent=items[0].parentNode;'
        'items.sort(function(a,b){'
        'if(mode==="score-desc")return getScore(b)-getScore(a);'
        'if(mode==="score-asc")return getScore(a)-getScore(b);'
        'if(mode==="name-desc"){return getName(b).localeCompare(getName(a));}'
        'if(mode==="price-asc"){var pa=getPrice(a),pb=getPrice(b);'
        'if(pa===null&&pb===null)return getName(a).localeCompare(getName(b));'
        'if(pa===null)return 1;if(pb===null)return -1;return pa-pb;}'
        'if(mode==="price-desc"){var pa2=getPrice(a),pb2=getPrice(b);'
        'if(pa2===null&&pb2===null)return getName(a).localeCompare(getName(b));'
        'if(pa2===null)return 1;if(pb2===null)return -1;return pb2-pa2;}'
        'return getName(a).localeCompare(getName(b));'
        '});'
        'items.forEach(function(it){parent.appendChild(it);});'
        '}'
        'function wire(){'
        'var inputs=document.querySelectorAll("input.tj-filter-search-input:not([data-wired])");'
        'inputs.forEach(function(inp){'
        'inp.setAttribute("data-wired","1");'
        'var t=document.querySelector(inp.getAttribute("data-filter-target"));'
        'if(!t)return;'
        'var sel=inp.getAttribute("data-filter-item");'
        'inp.addEventListener("input",function(){'
        'var q=inp.value.trim().toLowerCase();'
        'var items=t.querySelectorAll(sel);'
        'items.forEach(function(it){'
        'var txt=(it.textContent||"").toLowerCase();'
        'it.style.display=(!q||txt.indexOf(q)!==-1)?"":"none";'
        '});'
        '});'
        '});'
        'var selects=document.querySelectorAll("select.tj-filter-sort-select:not([data-wired])");'
        'selects.forEach(function(sl){'
        'sl.setAttribute("data-wired","1");'
        'var t=document.querySelector(sl.getAttribute("data-filter-target"));'
        'if(!t)return;'
        'var sel=sl.getAttribute("data-filter-item");'
        'sl.addEventListener("change",function(){sortItems(t,sel,sl.value);});'
        '});'
        '}'
        'if(document.readyState==="loading"){'
        'document.addEventListener("DOMContentLoaded",wire);'
        '}else{'
        'wire();'
        '}'
        '})();</script>'
    )
