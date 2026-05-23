#!/usr/bin/env python3
"""
One-shot generator: render a city hub + all 20 topic pages for a single city.

Usage:
    python scripts/generate_city.py france paris        # subregion under france
    python scripts/generate_city.py france              # treat france itself as the destination

Wraps generate_region_page + generate_topic_page so the daily workflow is one command.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def run(cmd: list) -> int:
    print(">", " ".join(str(c) for c in cmd))
    return subprocess.call([sys.executable, *cmd])


def main() -> int:
    p = argparse.ArgumentParser(description="Generate a full TableJourney city in one shot.")
    p.add_argument("country_slug")
    p.add_argument("city_slug", nargs="?", help="optional subregion slug")
    args = p.parse_args()

    region_args = [str(SCRIPTS / "generate_region_page.py"), args.country_slug]
    topic_args = [str(SCRIPTS / "generate_topic_page.py"), args.country_slug, "--all"]
    entity_args = [str(SCRIPTS / "generate_entity_pages.py"), args.country_slug]
    if args.city_slug:
        region_args += ["--region", args.city_slug]
        topic_args += ["--region", args.city_slug]
        entity_args += [args.city_slug]

    rc = run(region_args)
    if rc != 0:
        return rc
    rc = run(topic_args)
    if rc != 0:
        return rc
    rc = run(entity_args)
    if rc != 0:
        return rc

    # Refresh the cross-cut surfaces this city contributes to.
    # cross_cuts re-aggregates manifests (cuisine/dish/neighborhood) used
    # by scoped_cross_cuts; both must run before sitemap. city_dietary is
    # cheap and keeps /<country>/<city>/dietary/<diet>/ in sync with the
    # JSON. Non-fatal: a per-city regen still ships the city even if a
    # downstream index step hiccups.
    for step in (
        "generate_cross_cuts.py",
        "generate_region_grape.py",
        "generate_scoped_cross_cuts.py",
        "generate_city_dietary.py",
        "build_og_cities.py",
        "build_entity_maps.py",
        "build_city_pins.py",
        "generate_search_index.py",
    ):
        if run([str(SCRIPTS / step)]) != 0:
            print(f"  ({step} failed; continuing — non-fatal)")

    # Refresh sitemap so Google/Bing see the new entity URLs on next
    # crawl, and ping IndexNow so Bing/Yandex re-crawl this city's
    # changed pages within minutes. Both are idempotent; safe to run on
    # every regen. 2026-05-19.
    rc = run([str(SCRIPTS / "generate_sitemap.py")])
    if rc != 0:
        print("  (sitemap refresh failed; continuing — non-fatal)")

    if args.city_slug:
        rc = run([str(SCRIPTS / "indexnow_ping.py"),
                  "--city", args.country_slug, args.city_slug])
        if rc != 0:
            print("  (indexnow ping failed; continuing — non-fatal)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
