# Cork & Curve — handoff state

## Current state (2026-05-21)

- Repo at `https://github.com/lewismvaughan/corkandcurve`
- Local clone at `/opt/claude-stations/corkandcurve/repo/`
- Domain: `corkandcurve.com` (Lewis registering)
- Hosting: server-3 (same machine as TableJourney)

## What's done

- Infrastructure forked from TableJourney (scripts, templates, agents, docs)
- `CLAUDE.md` written for wine vertical
- `agents/wine-research/PROMPT.md` written (wine-specific verified-block,
  DOCG/IGT/AOC/AVA classification, hectarage, scores, biodynamic certification)
- `scripts/new_region.py` written (24 wine topic JSONs + nightlife + dietary)
- Minimal template rebrand applied (TableJourney → Cork and Curve,
  tablejourney.com → corkandcurve.com across templates/*.html)
- Test scaffold at `site-data/france/bordeaux/data/` (25 files, all empty stubs)

## What's pending (in priority order)

### P0 — unblocks research-agent dispatch

1. **Station container setup** — there is no `cork` station container yet,
   meaning sub-agents dispatched from the TJ station can't reach the cork
   repo. Either:
   - Stand up a new station container (docker-compose, bind-mount
     `/opt/claude-stations/corkandcurve/repo` → `/station/repo`) so the
     orchestrator can work inside cork directly; OR
   - Continue work via `sshp host` commands (slower but doable for one-off ops)

2. **Domain DNS + Caddy vhost** — DNS A-record for `corkandcurve.com`
   pointing at home public IP; Caddy vhost block added (mirror TJ block
   below). Cannot get TLS until DNS resolves.

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

### P1 — needed before first generation

3. **Template adaptation for wine cards** — current macros in
   `templates/topics/_macros.html` expect food fields (`p.cuisine`,
   `p.chef`, `p.signature_dishes`). Need wine-specific macros that
   render: `p.varietals`, `p.classification`, `p.hectares`, `p.owner`,
   `p.biodynamic_status`, `p.scores`.

4. **Entity template adaptation** — `entity-template.html` renders
   restaurants; need wine-entity variant for vineyards/tasting rooms.

5. **Topic templates** — each of the 24 wine topics needs a topic
   chapter template (or one shared via _topic_base.html with topic-specific
   sections).

6. **Schema.org JSON-LD adapt** — Restaurant → Place/Winery; need
   Schema.org `Vineyard` or `Place` with sub-type `Winery`.

### P2 — operational

7. **First region research** — Bordeaux is scaffolded (overlaps with TJ
   Bordeaux for clean cross-link test). Run wine-research agent against
   `france/bordeaux/`, then QA1/QA2/Opus per canonical pipeline.

8. **Cross-link blocks** — TJ has C&C link in footer (pending), C&C
   has TJ link in footer (pending). Add to base.html on both sides.

9. **Sitemap submit to GSC** — once DNS live + first region shipped.

## Pipeline (mirrors TJ FLOW.md)

1. `new_region.py` → empty scaffold
2. Sonnet wine-research → fills JSONs + ship_safety.sh
3. Sonnet QA1
4. Sonnet QA2
5. Opus final QA
6. Orchestrator: geocode → build_region_pins → regen all generators
7. sitemap + search index + chmod + push

## Cross-link contract with TableJourney

- Footer mention on both sites: brand + tagline only, no bulk list
- Editorial deep-link only when contextual (TJ wine-bars page → C&C
  region's tasting trail; C&C vineyard → TJ city food guide if same city)
- NOT identical About / Privacy / Editorial pages
- NOT shared author bylines (separate Person schemas)
