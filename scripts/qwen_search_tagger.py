#!/usr/bin/env python3
"""Enrich the static search index with Qwen-generated semantic tags.

Background
----------
content/search/search-index.json already supports lexical match (name,
subtitle, slug). It misses synonym / occasion / vibe queries:

    "noodles" -> never finds ramen, soba, udon entries
    "date night" -> never finds romantic-bistro entries
    "Japanese tapas" -> never finds izakaya entries
    "gluten free pizza" -> only matches if the phrase appears literally

This script calls the self-hosted Qwen 2.5 7B vLLM (the same instance that
serves the newswire tagger) and asks for a small structured set of search
tags per entity. Those tags are appended to the entry's `tokens` blob, so
the existing client-side fuzzy matcher picks them up with no client change.

Pipeline
--------
1. Read content/search/search-index.json.
2. For each entry of type {entity, dish, neighborhood, cuisine, city, country, topic}:
      a. Compute a stable content hash of (type, name, subtitle, country, city).
      b. If the hash is in the cache file, reuse cached tags.
      c. Else call Qwen with a fixed system prompt + entity-specific user msg,
         constrained to a strict JSON schema. Append result to cache.
3. Merge `synonyms`, `occasions`, `vibe`, `dietary` tags into each entry's
   `tokens` blob (lowercase, diacritic-stripped to match the existing
   normaliser).
4. Write the enriched index back. Cache persists at
   data/search-tags-cache.json so subsequent runs only call Qwen for new
   or changed entries.

Compliance with News-Api/docs/qwen-shared-access.md
---------------------------------------------------
- Stable system prompt across every call (prefix cache stays hot).
- Variable part lives in the user message.
- Response constrained via response_format=json_schema strict=true.
- Concurrency capped at 10 in-flight requests.
- 30s client timeout.
- X-Caller header set so the newswire side can attribute traffic.
- Writes only to our own cache file; never touches newswire schema.

Usage
-----
    AI_URL=http://172.17.0.1:8000 AI_KEY=... python3 scripts/qwen_search_tagger.py
    python3 scripts/qwen_search_tagger.py --limit 50    # bench / pilot
    python3 scripts/qwen_search_tagger.py --force       # ignore cache

Defaults pick the local vLLM if AI_URL/AI_KEY are not set so the build
machine doesn't have to plumb secrets through env. Override in CI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "content" / "search" / "search-index.json"
CACHE_PATH = REPO_ROOT / "data" / "search-tags-cache.json"

# Local vLLM bridge IP (host's docker0 gateway). Same Qwen 2.5 7B AWQ that
# the newswire tagger uses; running on the same machine, so no Tailscale
# Funnel round-trip.
DEFAULT_URL = "http://172.17.0.1:8000"
# AI_KEY lookup order: env var > data/.qwen-key (gitignored) > empty.
# data/.qwen-key persists the key across sessions so every ship_city run
# auto-tags new entries without anyone having to remember an env var.
def _load_default_key() -> str:
    env_key = os.environ.get("AI_KEY", "").strip()
    if env_key:
        return env_key
    key_file = Path(__file__).resolve().parent.parent / "data" / ".qwen-key"
    if key_file.exists():
        try:
            return key_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return ""
DEFAULT_KEY = _load_default_key()
MODEL = "newswire-tagger"

# §3.3 says concurrent batches are fine but cap at 10 to avoid evicting the
# newswire prefix cache. §3.2 says <=30s timeout.
CONCURRENCY = int(os.environ.get("QWEN_CONCURRENCY", "10"))
TIMEOUT = 30
X_CALLER = "search-tagger@tablejourney"
MAX_RETRIES = 2

# Types we tag. Chrome / topic-hub pages don't get semantic enrichment;
# they're navigational and the existing tokens blob is already exhaustive.
TAGGED_TYPES = {"entity", "dish", "cuisine", "neighborhood", "city", "country"}

# Stable system prompt — byte-identical across every call so vLLM keeps it
# pinned in its prefix cache (per the shared-access guide §3.1). Do NOT
# inline per-call data here.
SYSTEM_PROMPT = """You generate search tags for entries in a food-travel directory.

Given one entry (restaurant, dish, cuisine, neighbourhood, city, country, etc.) you return JSON with four short arrays:

- synonyms: alternate names and category words a real user might type to find this entry. Include cuisine words, dish words, ingredient words, the slug spelled out, neighbourhood nicknames. Skip meta-phrases ("food guide", "dining"), redundant phrasings ("X, X"), and generic words ("food", "restaurant", "place", "country", "city") that match everything. 0 to 8 items.
- occasions: when this entry is right for. Use ONLY if the entry CLEARLY fits. Choose from: date_night, business_lunch, family, quick_bite, splurge, casual_drinks, brunch_spot, late_night, group_dinner, solo, romantic, celebration, kid_friendly, vegan_friendly, halal_friendly, kosher_friendly, gluten_free_friendly, alfresco, hidden_gem, michelin, classic, modern, breakfast, dessert_focus, coffee_focus, drinks_focus.
- vibe: the feel of the place. Use ONLY if it clearly applies. Choose from: cozy, lively, refined, neighborhood, scene, hole_in_wall, see_and_be_seen, no_frills, design_forward, family_run, fast_paced, slow_paced, raucous, intimate.
- dietary: dietary categories that strongly apply to THIS specific entry. Choose from: vegan, vegetarian, halal, kosher, gluten_free, dairy_free, nut_free. ONLY tag dietary if the entry's name or subtitle clearly references it (e.g. "vegan bakery", "halal kebab", "gluten-free pizzeria"). Never tag dietary on countries, cities, neighbourhoods, or generic dishes.

Type-specific rules (apply strictly):
- type=country or type=city or type=neighborhood: occasions=[], vibe=[], dietary=[]. Only synonyms (alt names, native spellings, cuisine class).
- type=cuisine: occasions=[], vibe=[]. Only synonyms (alt names, related cuisine words) and dietary if the cuisine itself is inherently dietary (e.g. cuisine=vegan → dietary=[vegan]; otherwise dietary=[]).
- type=dish: occasions and vibe stay short or empty. Synonyms cover dish variants and ingredient words. Dietary only if the dish itself is inherently dietary (e.g. dish=vegan ramen).
- type=entity: full tag set is fair game, but stay conservative. If the subtitle says "fine dining" or "Michelin", tag splurge and/or michelin and refined. If it says "café" or "coffee", tag coffee_focus. If it says "wine bar" or "natural wine", tag drinks_focus. Do NOT default to dessert_focus / drinks_focus / casual_drinks on every entity.

Conservative default: empty arrays are better than wrong tags. If you are not sure, return a shorter list."""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "synonyms": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        "occasions": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "date_night", "business_lunch", "family", "quick_bite", "splurge",
                    "casual_drinks", "brunch_spot", "late_night", "group_dinner",
                    "solo", "romantic", "celebration", "kid_friendly",
                    "vegan_friendly", "halal_friendly", "kosher_friendly",
                    "gluten_free_friendly", "alfresco", "hidden_gem", "michelin",
                    "classic", "modern", "breakfast", "dessert_focus",
                    "coffee_focus", "drinks_focus",
                ],
            },
            "maxItems": 6,
        },
        "vibe": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "cozy", "lively", "refined", "neighborhood", "scene",
                    "hole_in_wall", "see_and_be_seen", "no_frills", "design_forward",
                    "family_run", "fast_paced", "slow_paced", "raucous", "intimate",
                ],
            },
            "maxItems": 4,
        },
        "dietary": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["vegan", "vegetarian", "halal", "kosher", "gluten_free", "dairy_free", "nut_free"],
            },
            "maxItems": 4,
        },
    },
    "required": ["synonyms", "occasions", "vibe", "dietary"],
    "additionalProperties": False,
}

# Mirrors generate_search_index._norm so merged tags hit the same client-side
# normaliser. Lowercase + diacritic-strip + collapse whitespace.
_COMBINING_RE = re.compile(r"[̀-ͯ]")


def _norm(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = _COMBINING_RE.sub("", s)
    return re.sub(r"\s+", " ", s.lower()).strip()


def _hash_entry(entry: dict) -> str:
    """Stable hash over the fields that would change the tag set. If the
    entry's name/subtitle/country/city change, retag. If only the URL
    changes (e.g. a slug rename), keep the cached tags."""
    key = "|".join([
        entry.get("type", ""),
        entry.get("name", ""),
        entry.get("subtitle", ""),
        entry.get("country", ""),
        entry.get("city", ""),
    ])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _build_user_message(entry: dict) -> str:
    parts = [f"Entry name: {entry.get('name', '')}", f"Type: {entry.get('type', '')}"]
    if entry.get("subtitle"):
        parts.append(f"Subtitle: {entry['subtitle']}")
    if entry.get("city"):
        parts.append(f"City: {entry['city']}")
    if entry.get("country"):
        parts.append(f"Country: {entry['country']}")
    return ". ".join(parts) + "."


def _call_qwen(entry: dict, url: str, key: str) -> dict | None:
    """One HTTP call. Returns tag dict on success, None on failure."""
    body = {
        "model": MODEL,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 220,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(entry)},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "search_tags", "strict": True, "schema": RESPONSE_SCHEMA},
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/v1/chat/completions",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Caller": X_CALLER,
        },
    )
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                resp = json.loads(r.read().decode("utf-8"))
                content = resp["choices"][0]["message"]["content"]
                return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))
                continue
            return None
    return None


def _tags_to_token_blob(tags: dict) -> str:
    """Flatten the tag dict into a single normalised token string suitable
    for appending to the search-index entry's `tokens` field."""
    parts: list[str] = []
    for arr_key in ("synonyms", "occasions", "vibe", "dietary"):
        for tok in tags.get(arr_key, []) or []:
            # underscores in enum values become spaces so 'date_night' is
            # findable both as 'date night' and 'date_night'
            parts.append(_norm(tok.replace("_", " ")))
            parts.append(_norm(tok))
    return " ".join(p for p in parts if p)


def load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(CACHE_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(CACHE_PATH)


def tag_entries(entries: list[dict], url: str, key: str, force: bool = False) -> dict:
    """Tag every eligible entry. Returns the (possibly updated) cache."""
    cache = {} if force else load_cache()
    to_call: list[tuple[str, dict]] = []
    for e in entries:
        if e.get("type") not in TAGGED_TYPES:
            continue
        h = _hash_entry(e)
        if h not in cache:
            to_call.append((h, e))
    if not to_call:
        print(f"[tagger] 0 entries to tag (cache covers {len(cache)} hashes).")
        return cache

    print(f"[tagger] {len(to_call)} entries to tag; cache covers {len(cache)} already.")
    print(f"[tagger] URL={url} concurrency={CONCURRENCY} timeout={TIMEOUT}s")

    start = time.time()
    done = 0
    failures = 0
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(_call_qwen, e, url, key): (h, e) for h, e in to_call}
        for fut in as_completed(futures):
            h, e = futures[fut]
            tags = fut.result()
            done += 1
            if tags is None:
                failures += 1
            else:
                cache[h] = tags
            if done % 100 == 0 or done == len(to_call):
                elapsed = time.time() - start
                rate = done / elapsed if elapsed else 0
                print(f"[tagger] {done}/{len(to_call)}  fail={failures}  {rate:.1f} req/s")
            # Periodic cache flush so a long-running pass survives interruption.
            if done % 500 == 0:
                save_cache(cache)
    save_cache(cache)
    print(f"[tagger] done. cache size={len(cache)}  failures={failures}  elapsed={time.time() - start:.1f}s")
    return cache


def enrich_index(entries: list[dict], cache: dict) -> int:
    """Mutate entries in-place: append cache tags into the tokens blob.
    Returns number of entries enriched."""
    enriched = 0
    for e in entries:
        if e.get("type") not in TAGGED_TYPES:
            continue
        tags = cache.get(_hash_entry(e))
        if not tags:
            continue
        blob = _tags_to_token_blob(tags)
        if not blob:
            continue
        e["tokens"] = (e.get("tokens") or "") + " " + blob
        enriched += 1
    return enriched


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=os.environ.get("AI_URL", DEFAULT_URL))
    p.add_argument("--key", default=os.environ.get("AI_KEY", DEFAULT_KEY))
    p.add_argument("--limit", type=int, default=0,
                   help="Tag only the first N eligible entries (for dry runs).")
    p.add_argument("--force", action="store_true",
                   help="Ignore cache and re-tag everything.")
    p.add_argument("--index", default=str(INDEX_PATH),
                   help="Path to search-index.json (default content/search/search-index.json).")
    p.add_argument("--no-write", action="store_true",
                   help="Compute tags + cache but don't overwrite the index file.")
    args = p.parse_args()

    if not args.key:
        print("ERROR: AI_KEY env var or --key is required.", file=sys.stderr)
        return 2

    index_path = Path(args.index)
    data = json.loads(index_path.read_text(encoding="utf-8"))
    entries = data["entries"] if isinstance(data, dict) else data

    if args.limit > 0:
        # Slice the eligible subset for a pilot run.
        kept = []
        n = 0
        for e in entries:
            if e.get("type") in TAGGED_TYPES and n < args.limit:
                kept.append(e)
                n += 1
        cache = tag_entries(kept, args.url, args.key, force=args.force)
        enriched = enrich_index(entries, cache)
    else:
        cache = tag_entries(entries, args.url, args.key, force=args.force)
        enriched = enrich_index(entries, cache)

    print(f"[tagger] enriched {enriched} index entries with cached tags.")

    if args.no_write:
        print("[tagger] --no-write set, leaving index file untouched.")
        return 0

    tmp = index_path.with_suffix(index_path.suffix + ".tmp")
    if isinstance(data, dict):
        data["entries"] = entries
        tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    else:
        tmp.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    tmp.replace(index_path)
    print(f"[tagger] wrote {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
