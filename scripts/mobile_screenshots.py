#!/usr/bin/env python3
"""Capture full-page screenshots at 375px (mobile) and 1440px (desktop)
for the key pages, plus surface horizontal-overflow issues.

Run: python3 scripts/mobile_screenshots.py
Outputs to /tmp/tj-screens/.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://corkandcurve.com"
PAGES = [
    ("/", "home"),
    ("/france/", "france-country-hub"),
    ("/france/paris/", "paris-hub"),
    # Topic pages (all 24 templates, one each)
    ("/france/paris/restaurants/", "paris-restaurants"),
    ("/france/paris/bakeries/", "paris-bakeries"),
    ("/france/paris/bars/", "paris-bars"),
    ("/france/paris/breweries/", "paris-breweries"),
    ("/france/paris/brunch/", "paris-brunch"),
    ("/france/paris/budget-eating/", "paris-budget-eating"),
    ("/france/paris/cafes/", "paris-cafes"),
    ("/france/paris/casual-dining/", "paris-casual-dining"),
    ("/france/paris/coffee-roasters/", "paris-coffee-roasters"),
    ("/france/paris/cooking-classes/", "paris-cooking-classes"),
    ("/france/paris/day-trips-food/", "paris-day-trips-food"),
    ("/france/paris/dietary/", "paris-dietary"),
    ("/france/paris/festivals/", "paris-festivals"),
    ("/france/paris/fine-dining/", "paris-fine-dining"),
    ("/france/paris/food-history/", "paris-food-history"),
    ("/france/paris/food-tours/", "paris-food-tours"),
    ("/france/paris/hidden-gems/", "paris-hidden-gems"),
    ("/france/paris/itineraries/", "paris-itineraries"),
    ("/france/paris/late-night/", "paris-late-night"),
    ("/france/paris/markets/", "paris-markets"),
    ("/france/paris/seasonal-food/", "paris-seasonal-food"),
    ("/france/paris/signature-dishes/", "paris-signature-dishes"),
    ("/france/paris/street-food/", "paris-street-food"),
    ("/france/paris/wine-bars/", "paris-wine-bars"),
    # Entity pages (sample of each kind)
    ("/france/paris/restaurants/bistrot-paul-bert/", "entity-restaurant"),
    ("/france/paris/cafes/telescope/", "entity-cafe"),
    ("/france/paris/markets/marche-des-enfants-rouges/", "entity-market"),
    # Cross-cuts
    ("/cuisine/french-bistro/", "cuisine-cross-cut"),
    ("/dish/steak-frites/", "dish-cross-cut"),
    ("/neighborhood/paris/11e/", "neighborhood-cross-cut"),
    # Topics chrome hubs
    ("/topics/restaurants/", "topics-restaurants"),
    ("/topics/breweries/", "topics-breweries"),
    ("/topics/", "topics-index"),
    ("/cuisines/", "cuisines-index"),
    ("/dishes/", "dishes-index"),
    ("/neighborhoods/", "neighborhoods-index"),
    # Chrome
    ("/search/", "search"),
    ("/about/", "about"),
    ("/cities/", "cities"),
    ("/contact/", "contact"),
    ("/privacy/", "privacy"),
    ("/terms/", "terms"),
    ("/cookies/", "cookies"),
    ("/editorial-standards/", "editorial-standards"),
    ("/disclaimer/", "disclaimer"),
    ("/404.html", "404"),
]
VIEWPORTS = [("mobile", 375, 812), ("desktop", 1440, 900)]
OUT = Path("/tmp/tj-screens")


def overflow_signals(page) -> dict:
    """Return basic horizontal-overflow + layout-pitfall signals."""
    return page.evaluate(
        """() => {
        const docW = document.documentElement.scrollWidth;
        const viewW = window.innerWidth;
        const overflowing = [];
        document.querySelectorAll('body *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.right > viewW + 1 && r.width > 8) {
                overflowing.push({
                    tag: el.tagName.toLowerCase(),
                    cls: el.className || '',
                    right: Math.round(r.right),
                    width: Math.round(r.width),
                });
            }
        });
        const overflowSample = overflowing.slice(0, 5);
        return {
            docScrollW: docW,
            innerW: viewW,
            horizontalScroll: docW > viewW + 1,
            overflowCount: overflowing.length,
            overflowSample,
        };
    }"""
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    issues: list = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for vp_name, w, h in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": w, "height": h})
            page = ctx.new_page()
            for url, slug in PAGES:
                try:
                    page.goto(BASE + url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as e:
                    print(f"  ERR loading {url}: {e}", file=sys.stderr)
                    continue
                shot = OUT / f"{slug}-{vp_name}.png"
                page.screenshot(path=str(shot), full_page=True)
                sig = overflow_signals(page)
                tag = "OK " if not sig["horizontalScroll"] else "OVR"
                print(f"  [{vp_name:7s}] {tag} {url}  doc={sig['docScrollW']}px / view={sig['innerW']}px  overflow={sig['overflowCount']}")
                if sig["horizontalScroll"]:
                    issues.append({"vp": vp_name, "url": url, **sig})
            ctx.close()
        browser.close()

    print("")
    print("=" * 60)
    print(f"Screenshots saved to {OUT}/")
    print(f"Pages with horizontal overflow: {len(issues)}")
    for it in issues:
        print(f"  {it['vp']}  {it['url']}  doc={it['docScrollW']}px vs view={it['innerW']}px")
        for o in it["overflowSample"]:
            print(f"    -> <{o['tag']} class=\"{o['cls'][:60]}\"> right={o['right']} width={o['width']}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
