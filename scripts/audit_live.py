#!/usr/bin/env python3
"""
Full-site audit of tablejourney.com using Playwright.
Crawls every URL in sitemap.xml, plus discovers internal links, then reports
on SEO essentials, schema, performance signals, image hygiene, and link health.

Run: python3 scripts/audit_live.py [--base https://tablejourney.com]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field

from playwright.sync_api import sync_playwright, Page, Response


@dataclass
class PageReport:
    url: str
    status: int = 0
    final_url: str = ""
    title: str = ""
    title_len: int = 0
    meta_desc: str = ""
    meta_desc_len: int = 0
    canonical: str = ""
    og: dict = field(default_factory=dict)
    twitter: dict = field(default_factory=dict)
    viewport: str = ""
    h1s: list = field(default_factory=list)
    h2_count: int = 0
    schema_types: list = field(default_factory=list)
    speakable: bool = False
    breadcrumb: bool = False
    images_total: int = 0
    images_missing_alt: int = 0
    images_lazy: int = 0
    hero_fetchpriority_high: bool = False
    internal_links: set = field(default_factory=set)
    external_links: set = field(default_factory=set)
    em_dash_count: int = 0
    legacy_destination_links: int = 0
    load_ms: int = 0
    encoding: str = ""
    content_length: int = 0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def fetch(url: str) -> bytes:
    req = ur.Request(url, headers={"User-Agent": "tj-audit/1.0"})
    with ur.urlopen(req, timeout=30) as r:
        return r.read()


def sitemap_urls(base: str) -> list:
    body = fetch(f"{base}/sitemap.xml").decode("utf-8", "replace")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(body)
    return [u.text.strip() for u in root.findall("s:url/s:loc", ns) if u.text]


def audit_page(page: Page, url: str, base: str) -> PageReport:
    r = PageReport(url=url)
    t0 = time.perf_counter()
    try:
        resp: Response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        r.status = -1
        r.errors.append(f"navigation failed: {e}")
        return r

    r.load_ms = int((time.perf_counter() - t0) * 1000)
    if resp is None:
        r.status = -1
        r.errors.append("no response")
        return r
    r.status = resp.status
    r.final_url = page.url
    try:
        hdrs = resp.headers
        r.encoding = hdrs.get("content-encoding", "")
        r.content_length = int(hdrs.get("content-length", "0") or 0)
    except Exception:
        pass

    if r.status != 200:
        r.errors.append(f"HTTP {r.status}")
        return r

    data = page.evaluate("""() => {
        const meta = (n) => document.querySelector(`meta[name="${n}"]`)?.content || "";
        const ometa = (p) => document.querySelector(`meta[property="${p}"]`)?.content || "";
        const link = (rel) => document.querySelector(`link[rel="${rel}"]`)?.href || "";
        const all = (sel) => Array.from(document.querySelectorAll(sel));
        const og = {};
        for (const m of document.querySelectorAll('meta[property^="og:"]')) {
            og[m.getAttribute('property')] = m.getAttribute('content') || "";
        }
        const tw = {};
        for (const m of document.querySelectorAll('meta[name^="twitter:"]')) {
            tw[m.getAttribute('name')] = m.getAttribute('content') || "";
        }
        const schemas = [];
        for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
            try { schemas.push(JSON.parse(s.textContent)); } catch (e) { schemas.push({__parse_error: e.message}); }
        }
        const images = all('img').map(i => ({
            src: i.currentSrc || i.src,
            alt: i.alt,
            loading: i.getAttribute('loading') || "",
            fetchpriority: i.getAttribute('fetchpriority') || "",
            width: i.width, height: i.height,
            inHero: !!i.closest('.hero, header.hero, [data-hero], .hero-image, .region-hero, .topic-hero, .tj-hero, .tj-home-hero')
        }));
        const links = all('a[href]').map(a => a.href);
        const visible = document.body ? document.body.innerText : "";
        return {
            title: document.title || "",
            description: meta('description'),
            canonical: link('canonical'),
            viewport: meta('viewport'),
            og, tw,
            h1s: all('h1').map(h => h.innerText.trim()),
            h2Count: all('h2').length,
            schemas, images, links, visibleText: visible
        };
    }""")

    r.title = data["title"]
    r.title_len = len(r.title)
    r.meta_desc = data["description"]
    r.meta_desc_len = len(r.meta_desc)
    r.canonical = data["canonical"]
    r.og = data["og"]
    r.twitter = data["tw"]
    r.viewport = data["viewport"]
    r.h1s = data["h1s"]
    r.h2_count = data["h2Count"]

    for s in data["schemas"]:
        def walk(node):
            if isinstance(node, dict):
                t = node.get("@type")
                if isinstance(t, list):
                    for x in t: r.schema_types.append(x)
                elif t:
                    r.schema_types.append(t)
                if "speakable" in node: r.speakable = True
                for v in node.values(): walk(v)
            elif isinstance(node, list):
                for v in node: walk(v)
        walk(s)
    r.breadcrumb = "BreadcrumbList" in r.schema_types

    for img in data["images"]:
        r.images_total += 1
        if not img["alt"].strip():
            r.images_missing_alt += 1
        if img["loading"] == "lazy":
            r.images_lazy += 1
        # An LCP-priority image satisfies the check whether or not it sits in
        # a "hero" wrapper. Modern Core Web Vitals guidance is to mark the
        # actual LCP element with fetchpriority=high, which on layouts like
        # our marquee homepage is not inside a .hero container.
        if img["fetchpriority"] == "high":
            r.hero_fetchpriority_high = True

    base_host = up.urlparse(base).netloc
    for href in data["links"]:
        if not href or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        try:
            host = up.urlparse(href).netloc
        except Exception:
            continue
        if host == base_host or host == "":
            r.internal_links.add(href.split("#")[0])
        else:
            r.external_links.add(href)

    text = data["visibleText"] or ""
    r.em_dash_count = text.count("—")
    r.legacy_destination_links = sum(1 for l in r.internal_links if "/destinations/" in l)

    if not r.title:
        r.errors.append("missing <title>")
    elif not (30 <= r.title_len <= 70):
        r.warnings.append(f"title {r.title_len} chars (target 30-70)")
    if not r.meta_desc:
        r.errors.append("missing meta description")
    elif not (120 <= r.meta_desc_len <= 170):
        r.warnings.append(f"meta description {r.meta_desc_len} chars (target 120-170)")
    if not r.canonical:
        r.errors.append("missing canonical")
    elif r.canonical.rstrip("/") != r.url.rstrip("/"):
        r.warnings.append(f"canonical mismatch: {r.canonical}")
    if "width=device-width" not in r.viewport:
        r.errors.append("missing/bad viewport meta")
    for k in ("og:title", "og:description", "og:image", "og:type", "og:url"):
        if not r.og.get(k):
            r.warnings.append(f"missing {k}")
    if not r.twitter.get("twitter:card"):
        r.warnings.append("missing twitter:card")
    if len(r.h1s) == 0:
        r.errors.append("no H1")
    elif len(r.h1s) > 1:
        r.warnings.append(f"{len(r.h1s)} H1s")
    if r.images_missing_alt:
        r.warnings.append(f"{r.images_missing_alt}/{r.images_total} <img> missing alt")
    if r.images_total > 1 and not r.hero_fetchpriority_high:
        r.warnings.append("hero <img> not fetchpriority=high")
    if not r.breadcrumb:
        r.warnings.append("no BreadcrumbList JSON-LD")
    if not any(t in r.schema_types for t in ("Article", "WebSite")):
        r.warnings.append("no Article/WebSite JSON-LD")
    if r.em_dash_count:
        r.errors.append(f"em-dash present x{r.em_dash_count} (banned by house style)")
    if r.legacy_destination_links:
        r.errors.append(f"legacy /destinations/ links x{r.legacy_destination_links}")
    if r.encoding not in ("gzip", "br", "zstd"):
        r.warnings.append(f"response not compressed (encoding={r.encoding!r})")

    return r


def head_status(url: str) -> int:
    req = ur.Request(url, headers={"User-Agent": "tj-audit/1.0"}, method="HEAD")
    try:
        with ur.urlopen(req, timeout=15) as r:
            return r.status
    except Exception as e:
        if hasattr(e, "code"):
            return e.code
        return -1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://tablejourney.com")
    ap.add_argument("--out", default="/tmp/tj_audit.json")
    args = ap.parse_args()

    print(f"[1/3] sitemap fetch → {args.base}/sitemap.xml")
    urls = sitemap_urls(args.base)
    print(f"      {len(urls)} URLs in sitemap")

    reports: list = []
    all_internal: set = set()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"),
            device_scale_factor=3, is_mobile=True, has_touch=True,
        )
        page = ctx.new_page()

        print(f"[2/3] auditing {len(urls)} pages (mobile viewport)")
        for i, u in enumerate(urls, 1):
            r = audit_page(page, u, args.base)
            reports.append(r)
            all_internal.update(r.internal_links)
            tag = "OK " if (r.status == 200 and not r.errors) else ("ERR" if r.errors else "WRN")
            print(f"  [{i:>3}/{len(urls)}] {tag} {r.status} {u}  ({r.load_ms}ms)"
                  + (f"  errors={len(r.errors)}" if r.errors else "")
                  + (f"  warnings={len(r.warnings)}" if r.warnings else ""))
        ctx.close()
        browser.close()

    print(f"[3/3] link health: {len(all_internal)} unique internal links")
    link_status: dict = {}
    new_links = sorted(l for l in all_internal if l not in {r.url for r in reports})
    for i, l in enumerate(new_links, 1):
        link_status[l] = head_status(l)
        if link_status[l] != 200:
            print(f"  BROKEN {link_status[l]} {l}")

    out = {
        "base": args.base,
        "pages": [r.__dict__ | {"internal_links": sorted(r.internal_links),
                                "external_links": sorted(r.external_links)} for r in reports],
        "extra_link_status": link_status,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2, default=list)

    total = len(reports)
    err_pages = sum(1 for r in reports if r.errors)
    wrn_pages = sum(1 for r in reports if r.warnings)
    err_total = sum(len(r.errors) for r in reports)
    wrn_total = sum(len(r.warnings) for r in reports)

    print("")
    print("=" * 60)
    print(f"AUDIT SUMMARY  ({args.base})")
    print("=" * 60)
    print(f"  pages crawled        {total}")
    print(f"  pages with errors    {err_pages}  ({err_total} errors total)")
    print(f"  pages with warnings  {wrn_pages}  ({wrn_total} warnings total)")
    broken = sum(1 for v in link_status.values() if v != 200)
    print(f"  broken extra links   {broken}")
    print(f"  full JSON report     {args.out}")

    by_warning: dict = defaultdict(int)
    for r in reports:
        for w in r.warnings:
            key = re.sub(r"\d+", "N", w)
            by_warning[key] += 1
    if by_warning:
        print("")
        print("Top warning patterns:")
        for k, v in sorted(by_warning.items(), key=lambda x: -x[1])[:15]:
            print(f"  {v:>4}  {k}")

    return 1 if err_total else 0


if __name__ == "__main__":
    sys.exit(main())
