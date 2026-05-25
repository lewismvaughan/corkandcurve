# Cork & Curve station (claude code-management workstation for corkandcurve.com)

You manage the live code AND the live site of **corkandcurve.com**, a static
SEO-driven wine + spirits travel atlas. Sister site to **tablejourney.com**
(food travel guide). Cross-linking strategy is light footer + contextual
entity cross-references, NOT bulk reciprocal links.

## READ FIRST (before any non-trivial work)

1. **[docs/STANDARDS.md](docs/STANDARDS.md)** — SEO + perf + correctness
   invariants every generator and agent must respect.
2. **[docs/DATA_TO_PAGES.md](docs/DATA_TO_PAGES.md)** — what every JSON
   field produces. Research agents need this to see the downstream
   impact of each field they fill.
3. **[docs/FLOW.md](docs/FLOW.md)** — operational playbook
   (research → QA chain → ship pipeline).
4. **[agents/wine-research/PROMPT.md](agents/wine-research/PROMPT.md)** —
   the wine-vertical adaptation of the TJ research prompt. Includes
   wine-specific verified-block fields (DOCG/IGT/AOC/AVA classification,
   hectarage, ownership, biodynamic status, key scores from Decanter +
   Wine Advocate where applicable).

## What corkandcurve is

- A Python-based **static-site generator** (forked from TableJourney):
  Jinja2 templates plus per-region JSON datasets render to plain HTML
  under `content/`.
- Public-facing at **https://corkandcurve.com**
- Different unit of organization vs TJ: **wine REGIONS** (Bordeaux,
  Tuscany, Napa, Mendoza, Barossa, etc.) instead of cities. A "region"
  is a wine appellation or recognized wine-tourism area.

## Hosting layout on server-3

No app process. Caddy serves the built HTML directly.

| Path | Purpose |
|------|---------|
| `/opt/claude-stations/corkandcurve/repo/` | Repo root (bind-mount to `/station/repo`) |
| `/opt/claude-stations/corkandcurve/repo/content/` | **Caddy serves from here.** Public URLs map 1:1 |
| `/opt/claude-stations/corkandcurve/repo/templates/` | Jinja2 sources |
| `/opt/claude-stations/corkandcurve/repo/site-data/` | Per-region JSON datasets |
| `/opt/claude-stations/corkandcurve/repo/scripts/` | Generators, validators, sitemap |
| `/etc/caddy/Caddyfile` | TLS + reverse proxy for corkandcurve.com |

## URL conventions (mirrors TJ where it makes sense)

- Region hub: `https://corkandcurve.com/<country>/<region>/`
- Topic page: `https://corkandcurve.com/<country>/<region>/<topic>/`
- Cross-cuts: `/grape/<varietal>/`, `/grape/<varietal>/<region>/`,
  `/style/<sparkling|still|sweet|fortified|orange|natural>/`,
  `/world/<old-world|new-world>/`

## How content reaches the public

Same pattern as TJ:
```
templates/*.html  +  site-data/<country>/<region>/*.json
              |  v   scripts/generate_*.py
              v
   content/<country>/<region>/<topic>/index.html
              v   Caddy reads it
       https://corkandcurve.com/...
```

## Topic shape (24 topics per region — adapted from TJ's food topics)

- `vineyards` (the cornerstone — every estate / domaine / château)
- `tasting-rooms` (urban + at-vineyard)
- `wine-bars`
- `wine-restaurants`
- `wine-retailers`
- `wine-schools` (cooking-classes equivalent — wine education)
- `wine-tours`
- `wine-festivals`
- `distilleries` (when the region overlaps spirits)
- `wine-museums`
- `wine-hotels` (vineyard B&Bs + estate stays)
- `wine-experiences` (helicopter, harvest, blending)
- `wine-history` (heritage + viticultural eras)
- `seasonal-wine` (harvest, primeurs, en-primeur weeks)
- `signature-wines` (the region's iconic bottles)
- `signature-grapes` (the canonical varietals — Sangiovese in Tuscany)
- `budget-wines` (under €25 finds)
- `hidden-gems` (lesser-known estates locals love)
- `day-trips-wine` (neighboring regions worth a half-day)
- `itineraries` (multi-day estate visits)
- `neighborhoods` (sub-appellations within the region)
- `nightlife` (wine bars open late, evening tastings)
- `dietary` (vegan winemaking, biodynamic, natural wine — overlaps with vegan dining)
- `food-pairing` (cross-link to TableJourney where wine + food coexist)

## Cross-linking to TableJourney

- **Footer mention** on every page: "Hungry too? Visit [TableJourney logo]"
- **Editorial deep-link only when contextual:**
  - C&C vineyard page → if vineyard has a restaurant or recommended pairing venue, link to that entity's TJ page
  - C&C region page → link to the matching TJ city's food guide (e.g. C&C Bordeaux → TJ Bordeaux)
  - TJ city page → link to C&C if the city is also a wine region (Bordeaux, Florence, Cape Town, etc.)
- **NOT** reciprocal bulk links, **NOT** identical About / Privacy / Editorial pages, **NOT** shared author bylines.

## Standard flows (mirror TJ)

**Add a new region (idempotent):**
```
python scripts/new_region.py <country_slug> <region_slug> --name <Name> --country <Country>
```

**Run the wine-research agent:** see `agents/wine-research/PROMPT.md`.

**Validate:** `python scripts/validate_data.py --region <region_slug>`

**Ship pipeline (canonical 5-stage per agents/DISPATCH_TEMPLATE.md):**
1. Sonnet wine-research agent
2. Sonnet QA1
3. Sonnet QA2
4. Opus final QA
5. Orchestrator: geocode, build_region_pins, regen, sitemap, search index, push

## Permissions

```
sshp host 'echo "$TJ_SUDO_PASS" | sudo -S chmod -R a+rX /opt/claude-stations/corkandcurve/repo/content'
```

## Definition of region ship-done (HARD GATES — no exceptions)

`ship_safety.sh PASS` + `generate_city.py` is **NOT** enough. Both can
exit cleanly while a region is missing maps, pins, FAQ blocks, or
inbound chrome links. TableJourney 2026-05-23 shipped Hong Kong with
0% geocode coverage because the orchestrator stopped after
`generate_city.py`. Don't repeat the mistake here.

Before printing `SHIP-READY` for any region, EVERY step below must
pass. Full command list in `docs/FLOW.md`. Headlines:

1. `bash scripts/ship_safety.sh <country> <region>` — exit 0
2. `python3 scripts/geocode_entities.py --city <region>` — Nominatim ~1/s
3. `python3 scripts/check_geocode_coverage.py <country> <region>` — ≥95%
4. `python3 scripts/build_entity_maps.py --city <region>` — JPEGs on disk
5. `python3 scripts/build_city_pins.py` — `_pins.json` updated
6. `python3 scripts/generate_city.py <country> <region>` — auto-chains
   cross-cuts, scoped, dietary (vegan winemaking), cuisine (grape),
   search-index, sitemap, llms.txt
7. `python3 scripts/generate_chrome_pages.py` — refreshes `/regions/`,
   `/topics/`, `/grapes/`, `/styles/` so the new region appears
8. `python3 scripts/generate_homepage.py` — refreshes `/` featured-regions
   + featured-wines rotation. Auto-discovers regions with ≥1 vineyard,
   but is NOT in generate_city's chain, so a shipped region stays off the
   homepage until this runs (Burgundy 2026-05-25 shipped fully but was
   absent from the homepage featured list because this step was skipped).
9. `orphan_audit.py` — no new orphans for the region slug
10. FAQ check — `id="faq"` + `FAQPage` schema both ≥1 on region hub
11. `check_jsonld.py <country> <region>` — JSON-LD parses clean
12. Live smoke test — 6+ URLs return 200 (hub, entities, cross-cuts, OG card)
13. `/regions/` chrome page lists the new region display name
14. Homepage featured list includes the new region (`grep <slug> content/index.html`)
15. chmod `a+rX` on `content/`

`generate_city.py` does NOT auto-run #7 (`generate_chrome_pages.py`),
#8 (`generate_homepage.py`), or #2-5 (geocode + maps + pins). Those are
explicit-only. Most ship failures come from forgetting them.

## Claude Code prompt: `/usage-credits`

When Claude Code is approaching its credit budget, the CLI surfaces an
inline hint that says something like *"type `/usage-credits` to see your
usage."* That hint is INFORMATIONAL only — it does not block any tool,
including the `Agent` tool used to dispatch sub-agents.

If you see it:

- **Do NOT stop the current task.** The Sonnet sub-agent dispatch via
  `Agent(subagent_type="general-purpose", ...)` works regardless. Keep
  going.
- **Do NOT prompt the user to type the command.** They've already
  delegated the work; surfacing the hint at them is noise.
- **Do NOT call `/usage-credits` via the `Skill` tool unless the user
  explicitly asks for a credit-status check.** The slash command is
  read-only — it shows a usage report — and running it doesn't free up
  any budget. Save the round-trip.

If a sub-agent dispatch genuinely fails because the account is out of
credits (different error, usually an explicit "rate limited" or "credit
exhausted" response from the Anthropic API), pause and ask the user
once. Don't loop-retry against an exhausted budget.

The same rule applies inside sub-agent prompts: include the line "if
you see a `/usage-credits` prompt from Claude Code, ignore it and keep
working" in any dispatch brief so the sub-agent doesn't pause either.

## What to NOT do

- Do not put secrets / drafts / sensitive content under `content/` (publicly served).
- Do not change Caddyfile without asking Lewis.
- Do not duplicate TJ content. Wine entities must be wine-vertical-specific
  even when in the same region as a TJ city.
- Do not invent vineyard ownership, hectarage, or classification details.
  Wine is a credibility vertical — verified-block discipline is doubly
  important here.
