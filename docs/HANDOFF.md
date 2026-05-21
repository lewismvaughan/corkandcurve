# Cork & Curve — handoff state (2026-05-21)

The Claude session inside the Cork station container picks up here.
Everything below has been verified before commit.

## Site state

- **Live:** https://corkandcurve.com/ → 200 (placeholder homepage with
  burgundy single-page design + TJ cross-link footer)
- **Favicon set:** svg + 16/32/180/192 PNG + favicon.ico — all 200
- **robots.txt:** open to all crawlers, sitemap reference
- **sitemap.xml:** homepage-only stub (will expand as regions ship)
- **www.corkandcurve.com:** 301 → apex (canonical)
- **HTTPS:** Let's Encrypt via tls-alpn-01 (Caddy)
- **Caddy vhost:** added to `/etc/caddy/Caddyfile`, validated, reloaded

## Repo state

- **GitHub:** https://github.com/lewismvaughan/corkandcurve (public)
- **Host path:** /opt/claude-stations/corkandcurve/repo/
- **Station container:** `claude-station-corkandcurve` (in admin panel)
- **Commits on main:** ~6 (initial scaffold → docs round → live site)

## What's adapted for wine

| Item | Status |
|---|---|
| `CLAUDE.md` | wine-vertical |
| `agents/wine-research/PROMPT.md` | wine-vertical (verified-block, DOCG/IGT/AOC, hectarage, scores) |
| `agents/wine-research/SCHEMA.md` | per-topic JSON shape for wine |
| `agents/qa/PROMPT.md` | wine-vertical QA (8 defect classes: classification, hectarage, scores, ownership, certification, address cross-check, cross-link sanity, voice) |
| `agents/DISPATCH_TEMPLATE.md` | shared with TJ — 5-stage canonical pipeline |
| `scripts/new_region.py` | wine-vertical scaffolding (24 topic JSONs + nightlife + dietary) |
| Templates | brand sed-pass done (`Cork and Curve`, `corkandcurve.com`); content adaptation NOT done — see `docs/TEMPLATES_AUDIT.md` |
| `docs/STANDARDS.md` | wine-vertical |
| `docs/FLOW.md` | wine-vertical operational playbook |
| `docs/DATA_TO_PAGES.md` | wine field → page mapping |
| `docs/SKELETON.md` | URL inventory + page-type breakdown |
| `docs/CROSS_LINKING.md` | TJ ↔ C&C contract |
| `docs/PIPELINE.md` | 5-stage pipeline reference |
| `docs/ORCHESTRATOR.md` | orchestrator role specifics |
| `docs/IMAGE_SOURCES.md` | wine image sourcing rules |
| `docs/SCRIPTS_AUDIT.md` | which scripts are ready / need adapt / need rewrite |
| `docs/TEMPLATES_AUDIT.md` | which templates are ready / need adapt / need rewrite |

## What's still TJ-shaped (next-session priority)

Per the audits:

1. `scripts/generate_*.py` — most generators have TJ topic slugs
   hardcoded. ~2 hours of mechanical adapt work (🟡 cases). Plus
   ~3-4 hours rewriting the food-specific generators that need wine
   equivalents (🔴 cases — generate_city_cuisine → generate_region_grape,
   generate_city_dish → generate_signature_wine, etc.). See
   `docs/SCRIPTS_AUDIT.md`.

2. `templates/topics/*.html` — TJ food topics. Need wine analogs
   per `docs/TEMPLATES_AUDIT.md`. Card macros (`templates/topics/_macros.html`)
   are the FIRST thing to write — everything else depends on them.
   Estimate ~3-4 hours.

3. `templates/entity-template.html`, `templates/region-template.html`
   — conditional sections expect food fields. Adapt to wine fields.

4. Cross-cut templates (`/grape/`, `/style/`, `/world/`) need writing
   from scratch (TJ has `/cuisine/` and `/dish/` but no direct wine
   analogs).

## Recommended next-session sequence

1. **Read** `docs/SKELETON.md`, `docs/PIPELINE.md`, `docs/CROSS_LINKING.md`.
2. **Adapt `templates/topics/_macros.html`** — write the 12 wine card
   macros first.
3. **Adapt `templates/entity-template.html`** — wine entity page.
4. **Adapt `templates/region-template.html`** — wine region hub.
5. **Adapt `scripts/utils/template_renderer.py` + `data_loader.py`**
   — topic registries.
6. **Adapt `scripts/generate_region_page.py`, `generate_topic_page.py`,
   `generate_entity_pages.py`** — top three generators.
7. **Adapt `scripts/generate_sitemap.py`** — wine URL discovery.
8. **Scaffold first region** — `python3 scripts/new_region.py france
   bordeaux --name Bordeaux --country France` (already done as test).
9. **Dispatch wine-research agent** for france/bordeaux per
   `agents/DISPATCH_TEMPLATE.md`.
10. **Chain QA1 → QA2 → Opus** per `feedback_qa_automatic`.
11. **Generation step** — geocode + pins + regen.
12. **Commit + push.**

## Cross-station ops with TableJourney

- Lewis manages both stations. TJ continues to ship cities; C&C ships
  wine regions.
- Geographic overlap matrix is in `docs/CROSS_LINKING.md` —
  Bordeaux/Tuscany/Napa/Burgundy/Stellenbosch/etc. cities + regions.
- When a C&C region ships overlapping a TJ city (or vice versa), the
  orchestrators on both sides update `cross_site_ref` fields + regen
  the affected pages. NOT bulk — only the overlap pair.

## Caddy vhost (already wired)

In `/etc/caddy/Caddyfile`:
```
corkandcurve.com {
    bind 192.168.1.101
    root * /opt/claude-stations/corkandcurve/repo/content
    encode gzip zstd
    file_server {
        hide .* *.py *.md
    }
}
www.corkandcurve.com {
    bind 192.168.1.101
    redir https://corkandcurve.com{uri} permanent
}
```

After regenerating HTML, always run:
```
sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/corkandcurve/repo/content'
```
(or use the explicit password from station.yaml ssh_hosts).

## Memory rules that apply

- `feedback_qa_automatic` — QA chain is automatic, never ask
- `feedback_canonical_pipeline` — 5 stages per region
- `feedback_no_em_dashes` — hard ban
- `feedback_url_fabrication` — self-HEAD every URL before writing
- `feedback_qa_decisive` — QA removes defects, doesn't flag-for-followup
- `feedback_geocode_gates_ship` — pin coverage threshold before ship
- `feedback_handoff_doc_age_check` — this HANDOFF.md is a snapshot;
  verify repo state before acting (`git status`, `ls site-data/`)

## Pages currently rendering on corkandcurve.com

- `/` homepage (placeholder — single-page burgundy)
- `/favicon.svg`, `/favicon-32x32.png`, `/apple-touch-icon.png`,
  `/icon-192.png`, `/favicon.ico`
- `/robots.txt`, `/sitemap.xml`

No regions yet. First region (Bordeaux) is scaffolded but JSONs are
empty stubs; research agent has not run yet.

## Test the site

```
curl -sSI https://corkandcurve.com/ | head -3       # 200 OK
curl -sSI https://corkandcurve.com/favicon.svg      # 200 OK
curl -sSI https://www.corkandcurve.com/             # 301 → apex
```

Goodbye + good luck, future-me.
