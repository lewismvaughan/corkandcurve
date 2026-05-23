#!/usr/bin/env python3
"""
Walk site-data/ and emit content/sitemap.xml covering every page TableJourney
publishes: homepage, each city hub, each city subregion hub, and each topic
page that has a corresponding *.json data file with non-empty contents.

Auto-shards once the URL count exceeds SHARD_SIZE: /sitemap.xml becomes a
sitemap-index pointing at /sitemap-1.xml, /sitemap-2.xml, etc. Below the
threshold, /sitemap.xml is a single flat urlset (one fewer HTTP round-trip
for crawlers and validators).
"""

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = REPO_ROOT / "site-data"
OUT_DIR = REPO_ROOT / "content"
BASE = "https://corkandcurve.com"


# Section-based sitemap shards. Search Console reports indexing stats per
# sitemap file, so splitting by section gives us a clean per-area
# crawl/coverage breakdown without us having to filter in their UI.
SECTION_FILES = {
    "core":       "sitemap-core.xml",        # homepage + chrome + /topics/
    "cities":     "sitemap-cities.xml",      # country/state/city hubs + per-city topic pages
    "entities":   "sitemap-entities.xml",    # /<country>/<city>/<topic>/<slug>/ leaves
    "crosscuts":  "sitemap-crosscuts.xml",   # /cuisine/<slug>/, /dish/, /neighborhood/, scoped, city × dietary
}


def _mtime_iso(url: str) -> str:
    """Map a full https://tablejourney.com/... URL back to its on-disk
    index.html and return that file's mtime as a YYYY-MM-DD lastmod.

    Honest per-URL lastmod tells Google which pages actually changed, so
    crawl budget gets spent on the changed ones — significantly better
    than every URL claiming today's date.
    """
    rel = url.replace(BASE, "").strip("/")
    target = OUT_DIR / rel / "index.html" if rel else OUT_DIR / "index.html"
    if target.exists():
        return date.fromtimestamp(target.stat().st_mtime).isoformat()
    # Fallback (rare): the URL was emitted speculatively without a file
    # on disk. Use today rather than skip; Google tolerates this.
    return date.today().isoformat()

TOPIC_SLUGS = [
    "vineyards", "wines", "tasting-rooms", "wine-bars", "wine-restaurants",
    "wine-retailers", "wine-schools", "wine-tours", "wine-festivals",
    "distilleries", "wine-museums", "wine-hotels", "wine-experiences",
    "wine-history", "seasonal-wine", "signature-wines", "signature-grapes",
    "budget-wines", "hidden-gems", "day-trips-wine", "itineraries",
    "neighborhoods", "nightlife", "dietary", "food-pairing",
]


def topic_has_content(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    for v in data.values():
        if isinstance(v, list) and v:
            return True
        if isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list) and vv:
                    return True
                if isinstance(vv, str) and vv.strip():
                    return True
        if isinstance(v, str) and v.strip():
            return True
    return False


CHROME_PAGES = [
    ("about", "monthly", "0.6"),
    ("about/editorial", "monthly", "0.5"),
    ("editorial-standards", "yearly", "0.5"),
    ("contact", "yearly", "0.5"),
    ("regions", "weekly", "0.8"),
    ("grapes", "monthly", "0.6"),
    ("styles", "monthly", "0.6"),
    ("world", "monthly", "0.6"),
    ("topics", "weekly", "0.8"),
    ("privacy", "yearly", "0.3"),
    ("terms", "yearly", "0.3"),
    ("cookies", "yearly", "0.3"),
    ("disclaimer", "yearly", "0.3"),
    ("search", "monthly", "0.4"),
]


_DIETARY_CATEGORY_SLUGS = frozenset({"vegan", "vegetarian", "gluten-free", "halal", "kosher"})
_NIGHTLIFE_CATEGORY_SLUGS = frozenset({"dance-clubs", "live-music", "rooftop-bars", "speakeasies", "lgbtq", "listening-bars", "late-night-dives"})
# Time-of-day sub-pages live inside time-aware topic directories (e.g.
# /brunch/sunday/, /bars/late/) — they're NOT entity pages and must be
# skipped by the entity walker. The crosscuts loop emits them with their
# own priority, so without this skip we'd double-list them in the sitemap.
_WHEN_SLUGS = frozenset({"sunday", "monday", "saturday", "late", "weekend-late", "weekend"})


def _walk_entity_pages(country: str, city: str | None) -> list:
    """Return URLs for every entity page (one per content/.../<topic>/<slug>/)."""
    base_dir = OUT_DIR / country / (city or "")
    base_url = f"/{country}/" if not city else f"/{country}/{city}/"
    urls = []
    if not base_dir.exists():
        return urls
    for topic_slug in TOPIC_SLUGS:
        topic_dir = base_dir / topic_slug
        if not topic_dir.is_dir():
            continue
        for entity_dir in sorted(topic_dir.iterdir()):
            if not entity_dir.is_dir() or not (entity_dir / "index.html").exists():
                continue
            # The dietary topic dir holds both per-entity pages AND the new
            # diet-category landing pages (vegan/, vegetarian/, etc.). The
            # category pages are emitted separately with their own priority,
            # so skip them here to avoid duplicate sitemap entries.
            if topic_slug == "dietary" and entity_dir.name in _DIETARY_CATEGORY_SLUGS:
                continue
            if topic_slug == "nightlife" and entity_dir.name in _NIGHTLIFE_CATEGORY_SLUGS:
                continue
            # Time-of-day sub-pages are not entities.
            if entity_dir.name in _WHEN_SLUGS:
                continue
            urls.append(f"{base_url}{topic_slug}/{entity_dir.name}/")
    return urls


def _walk_cross_cuts() -> list:
    """Return URLs for cross-cut landing pages."""
    out = []
    for kind in ("cuisine", "dish"):
        kdir = OUT_DIR / kind
        if not kdir.is_dir():
            continue
        # Include the parent index page (/cuisine/, /dish/) when it exists.
        if (kdir / "index.html").exists():
            out.append(f"/{kind}/")
        for slug_dir in sorted(kdir.iterdir()):
            if slug_dir.is_dir() and (slug_dir / "index.html").exists():
                out.append(f"/{kind}/{slug_dir.name}/")
    ndir = OUT_DIR / "neighborhood"
    if ndir.is_dir():
        for city_dir in sorted(ndir.iterdir()):
            if not city_dir.is_dir():
                continue
            for hood_dir in sorted(city_dir.iterdir()):
                if hood_dir.is_dir() and (hood_dir / "index.html").exists():
                    out.append(f"/neighborhood/{city_dir.name}/{hood_dir.name}/")
    return out


def _is_stub_region(region_json_path: Path) -> bool:
    """Return True if the region.json marks the city as a stub (queued/scaffolded
    but with no real content rendered). Such cities have no HTML under content/
    yet, so they must be excluded from the sitemap to avoid 404s for crawlers."""
    try:
        data = json.loads(region_json_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    meta = data.get("_metadata") or {}
    return meta.get("status") == "stub"


def _add(urls: list, url: str, changefreq: str, priority: str, section: str) -> None:
    """Append a URL tuple with per-URL mtime + section label."""
    urls.append((url, _mtime_iso(url), changefreq, priority, section))


def collect_urls() -> list:
    urls: list = []
    _add(urls, f"{BASE}/", "daily", "1.0", "core")

    for slug, freq, prio in CHROME_PAGES:
        if (OUT_DIR / slug / "index.html").exists():
            _add(urls, f"{BASE}/{slug}/", freq, prio, "core")
    for topic in TOPIC_SLUGS:
        if (OUT_DIR / "topics" / topic / "index.html").exists():
            _add(urls, f"{BASE}/topics/{topic}/", "weekly", "0.7", "core")

    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name
        # Country hub. Include it whenever the content/<country>/index.html
        # actually exists — even if the country lacks data/region.json,
        # generate_country_stubs.py may have emitted a minimal stub
        # (e.g. /germany/) and we want it in the sitemap.
        country_region = country_dir / "data" / "region.json"
        country_index_exists = (OUT_DIR / country / "index.html").exists()
        if country_index_exists:
            _add(urls, f"{BASE}/{country}/", "weekly", "0.9", "cities")
        if country_region.exists():
            for topic in TOPIC_SLUGS:
                if topic_has_content(country_dir / "data" / f"{topic}.json"):
                    _add(urls, f"{BASE}/{country}/{topic}/", "monthly", "0.7", "cities")
            for url in _walk_entity_pages(country, None):
                _add(urls, f"{BASE}{url}", "monthly", "0.6", "entities")
            # Country-scoped cross-cuts (cuisines, signature-dishes, neighborhoods).
            for sub in ("cuisines", "signature-dishes", "neighborhoods"):
                if (OUT_DIR / country / sub / "index.html").exists():
                    _add(urls, f"{BASE}/{country}/{sub}/", "weekly", "0.75", "crosscuts")

        # State-level hub pages (virtual, generated by generate_state_pages.py).
        state_slugs_seen: set = set()
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            region_json = city_dir / "data" / "region.json"
            if not region_json.exists():
                continue
            try:
                rdata = json.loads(region_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            state_slug = rdata.get("destination", {}).get("state_slug")
            if state_slug and state_slug not in state_slugs_seen:
                state_slugs_seen.add(state_slug)
                state_index = OUT_DIR / country / state_slug / "index.html"
                if state_index.exists():
                    _add(urls, f"{BASE}/{country}/{state_slug}/", "weekly", "0.7", "cities")

        # Sub-region (city) hubs
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            city = city_dir.name
            region_json = city_dir / "data" / "region.json"
            if not region_json.exists():
                continue
            if _is_stub_region(region_json):
                continue
            _add(urls, f"{BASE}/{country}/{city}/", "weekly", "0.9", "cities")
            for topic in TOPIC_SLUGS:
                if topic_has_content(city_dir / "data" / f"{topic}.json"):
                    _add(urls, f"{BASE}/{country}/{city}/{topic}/", "monthly", "0.8", "cities")
            for url in _walk_entity_pages(country, city):
                _add(urls, f"{BASE}{url}", "monthly", "0.6", "entities")
            # City-scoped cross-cuts (cuisines + neighborhoods only; the city
            # signature-dishes URL is already emitted above as a topic page).
            for sub in ("cuisines", "neighborhoods"):
                if (OUT_DIR / country / city / sub / "index.html").exists():
                    _add(urls, f"{BASE}/{country}/{city}/{sub}/", "weekly", "0.75", "crosscuts")
            # City × dietary sub-pages (vegan/vegetarian/gluten-free/halal/kosher).
            dietary_dir = OUT_DIR / country / city / "dietary"
            if dietary_dir.is_dir():
                for diet in ("vegan", "vegetarian", "gluten-free", "halal", "kosher"):
                    if (dietary_dir / diet / "index.html").exists():
                        _add(urls, f"{BASE}/{country}/{city}/dietary/{diet}/",
                             "weekly", "0.75", "crosscuts")
            # City × cuisine sub-pages.
            cuisine_dir = OUT_DIR / country / city / "cuisine"
            if cuisine_dir.is_dir():
                for slug_dir in sorted(cuisine_dir.iterdir()):
                    if slug_dir.is_dir() and (slug_dir / "index.html").exists():
                        _add(urls, f"{BASE}/{country}/{city}/cuisine/{slug_dir.name}/",
                             "weekly", "0.7", "crosscuts")
            # City × dish sub-pages ("where to eat <dish> in <city>").
            dish_dir = OUT_DIR / country / city / "dish"
            if dish_dir.is_dir():
                for slug_dir in sorted(dish_dir.iterdir()):
                    if slug_dir.is_dir() and (slug_dir / "index.html").exists():
                        _add(urls, f"{BASE}/{country}/{city}/dish/{slug_dir.name}/",
                             "weekly", "0.7", "crosscuts")
            # City × nightlife-subcategory pages.
            nl_dir = OUT_DIR / country / city / "nightlife"
            if nl_dir.is_dir():
                for sub_dir in sorted(nl_dir.iterdir()):
                    if not sub_dir.is_dir() or sub_dir.name == "":
                        continue
                    idx = sub_dir / "index.html"
                    if idx.exists() and sub_dir.name in {
                        "dance-clubs", "live-music", "rooftop-bars", "speakeasies",
                        "lgbtq", "listening-bars", "late-night-dives",
                    }:
                        _add(urls, f"{BASE}/{country}/{city}/nightlife/{sub_dir.name}/",
                             "weekly", "0.7", "crosscuts")
            # City × price-tier pages (cheap-eats / mid-range / upscale / splurge).
            for tier in ("cheap-eats", "mid-range", "upscale", "splurge"):
                if (OUT_DIR / country / city / tier / "index.html").exists():
                    _add(urls, f"{BASE}/{country}/{city}/{tier}/",
                         "weekly", "0.7", "crosscuts")
            # City × topic × time-of-day pages
            # (e.g. /<country>/<city>/brunch/sunday/, /bars/late/, /late-night/weekend/).
            when_slugs = {
                "sunday", "monday", "saturday", "late", "weekend-late", "weekend",
            }
            time_aware_topics = {
                "restaurants", "brunch", "cafes", "bakeries", "bars", "late-night",
            }
            for tslug in time_aware_topics:
                tdir = OUT_DIR / country / city / tslug
                if not tdir.is_dir():
                    continue
                for child in tdir.iterdir():
                    if child.is_dir() and child.name in when_slugs and (child / "index.html").exists():
                        _add(urls, f"{BASE}/{country}/{city}/{tslug}/{child.name}/",
                             "weekly", "0.6", "crosscuts")

        # Country-level rollup surfaces added 2026-05-20: /<country>/<topic>/,
        # /<country>/cuisine/<x>/, /<country>/dish/<x>/, /<country>/dietary/<d>/,
        # /<country>/nightlife/<sub>/. Listed unconditionally — emitted by the
        # country generators when content threshold cleared.
        country_dir_c = OUT_DIR / country
        if country_dir_c.is_dir():
            for topic in TOPIC_SLUGS:
                if (country_dir_c / topic / "index.html").exists():
                    # Only emit if not already added by data/region.json branch above
                    cand = f"{BASE}/{country}/{topic}/"
                    if not any(u[0] == cand for u in urls):
                        _add(urls, cand, "weekly", "0.7", "crosscuts")
            for parent in ("cuisine", "dish", "dietary", "nightlife"):
                pdir = country_dir_c / parent
                if not pdir.is_dir():
                    continue
                for child in sorted(pdir.iterdir()):
                    if not child.is_dir():
                        continue
                    if not (child / "index.html").exists():
                        continue
                    _add(urls, f"{BASE}/{country}/{parent}/{child.name}/",
                         "weekly", "0.7", "crosscuts")

    # Cross-cut landings (global /cuisine/<slug>/, /dish/, /neighborhood/)
    for url in _walk_cross_cuts():
        _add(urls, f"{BASE}{url}", "weekly", "0.7", "crosscuts")

    # Per-cuvée wine pages: /wine/<producer>/<cuvee>/
    # Emitted by generate_wine_pages.py from wines.json. The cuvée page is
    # the canonical entry for each producer cuvée; we index every one we
    # rendered so Google can discover them off the sitemap rather than
    # having to crawl through region hubs.
    wine_root = OUT_DIR / "wine"
    if wine_root.is_dir():
        for producer_dir in sorted(wine_root.iterdir()):
            if not producer_dir.is_dir():
                continue
            for cuvee_dir in sorted(producer_dir.iterdir()):
                if cuvee_dir.is_dir() and (cuvee_dir / "index.html").exists():
                    _add(urls, f"{BASE}/wine/{producer_dir.name}/{cuvee_dir.name}/",
                         "monthly", "0.7", "wines")

    # Tag pages: /tag/<slug>/ (global) + /tag/<slug>/<region>/ (scoped).
    # Emitted by generate_tag_pages.py from wines.json across all regions.
    # Filter-style landing pages with a known intent (pairs-with-lamb,
    # cellar-worthy, biodynamic, etc.) — surface them so Search can serve
    # the "best <X> wines" intent without us hand-curating a top-10 list.
    tag_root = OUT_DIR / "tag"
    if tag_root.is_dir():
        for tag_dir in sorted(tag_root.iterdir()):
            if not tag_dir.is_dir() or not (tag_dir / "index.html").exists():
                continue
            _add(urls, f"{BASE}/tag/{tag_dir.name}/", "weekly", "0.7", "tags")
            for region_dir in sorted(tag_dir.iterdir()):
                if region_dir.is_dir() and (region_dir / "index.html").exists():
                    _add(urls, f"{BASE}/tag/{tag_dir.name}/{region_dir.name}/",
                         "monthly", "0.6", "tags")

    # Neighborhood × cuisine deep pages
    # /neighborhood/<city>/<nbhd>/<cuisine>/
    ndir2 = OUT_DIR / "neighborhood"
    if ndir2.is_dir():
        for city_dir in sorted(ndir2.iterdir()):
            if not city_dir.is_dir():
                continue
            for hood_dir in city_dir.iterdir():
                if not hood_dir.is_dir():
                    continue
                for cuisine_dir in hood_dir.iterdir():
                    if cuisine_dir.is_dir() and (cuisine_dir / "index.html").exists():
                        _add(urls,
                             f"{BASE}/neighborhood/{city_dir.name}/{hood_dir.name}/{cuisine_dir.name}/",
                             "monthly", "0.6", "crosscuts")

    # Global cross-city top-topic rollups
    # /rooftops/, /speakeasies/, /best-brunch/, etc.
    GLOBAL_TOP_SLUGS = {
        "rooftops", "speakeasies", "dance-clubs", "live-music", "lgbtq-nightlife",
        "listening-bars", "late-night-dives", "best-brunch", "best-coffee",
        "best-wine-bars", "best-bakeries", "best-markets", "best-breweries",
        "best-cocktail-bars",
    }
    for slug in GLOBAL_TOP_SLUGS:
        if (OUT_DIR / slug / "index.html").exists():
            _add(urls, f"{BASE}/{slug}/", "weekly", "0.7", "crosscuts")

    # Dedup: every shipped URL must appear EXACTLY ONCE across the whole
    # sitemap, regardless of how many sections/strategies added it. Keep
    # the FIRST occurrence (which carries the most-specific section tag);
    # drop later duplicates. Defensive — protects future surface additions
    # from accidentally getting double-emitted.
    seen: set[str] = set()
    deduped: list = []
    duplicates_dropped = 0
    for tup in urls:
        u = tup[0]
        if u in seen:
            duplicates_dropped += 1
            continue
        seen.add(u)
        deduped.append(tup)
    if duplicates_dropped:
        print(f"  dedup: dropped {duplicates_dropped} duplicate URL entries")
    return deduped


# Google sitemap protocol caps: 50,000 URLs and 50 MB uncompressed per file.
# We shard well below the URL cap (40k) so individual sitemaps stay small
# and Search Console parses them faster.
SHARD_SIZE = 40_000


def _serialise_urls(urls: list) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for tup in urls:
        url, lastmod, changefreq, priority = tup[0], tup[1], tup[2], tup[3]
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(url)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>\n")
    return "\n".join(lines)


def _clean_old_shards() -> None:
    """Remove any sitemap-*.xml files left over from prior runs. Keeps the
    sitemap directory in sync with whatever this run produces; old shards
    that aren't overwritten get deleted so Search Console never crawls a
    stale one. Matches both numeric (sitemap-1.xml, sitemap-42.xml) and
    section-named (sitemap-core.xml, sitemap-entities.xml) shards."""
    for f in OUT_DIR.glob("sitemap-*.xml"):
        try:
            f.unlink()
        except OSError:
            pass


def _max_mtime(urls_in_section: list) -> str:
    """Most-recent lastmod across a section, used as the sitemap-index
    <lastmod> for that section. Lets Google know if any URL in the section
    changed without re-reading every entry."""
    if not urls_in_section:
        return date.today().isoformat()
    return max(t[1] for t in urls_in_section)


def main() -> int:
    urls = collect_urls()
    sitemap_path = OUT_DIR / "sitemap.xml"

    _clean_old_shards()

    # Section-shard, always (we get per-section coverage stats in Search
    # Console even at small totals). Sections that emit zero URLs are
    # skipped so /sitemap.xml never points at an empty shard.
    by_section: dict[str, list] = {k: [] for k in SECTION_FILES}
    for t in urls:
        section = t[4] if len(t) > 4 else "core"
        by_section.setdefault(section, []).append(t)

    shard_entries = []  # (url, lastmod) for the index file
    total_written = 0
    for section, filename in SECTION_FILES.items():
        section_urls = by_section.get(section) or []
        if not section_urls:
            continue
        shard_path = OUT_DIR / filename
        shard_path.write_text(_serialise_urls(section_urls), encoding="utf-8")
        shard_entries.append((f"{BASE}/{filename}", _max_mtime(section_urls)))
        total_written += len(section_urls)

    # Sitemap index at /sitemap.xml points at each section file.
    idx_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for shard_url, last in shard_entries:
        idx_lines.append("  <sitemap>")
        idx_lines.append(f"    <loc>{escape(shard_url)}</loc>")
        idx_lines.append(f"    <lastmod>{last}</lastmod>")
        idx_lines.append("  </sitemap>")
    idx_lines.append("</sitemapindex>\n")
    sitemap_path.write_text("\n".join(idx_lines), encoding="utf-8")
    print(
        f"Wrote {sitemap_path} as section-sharded index of {len(shard_entries)} "
        f"sub-sitemaps, {total_written} URLs total"
    )
    for url, last in shard_entries:
        print(f"  {url}  (lastmod {last})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
