# Cork & Curve station (claude code-management workstation for corkandcurve.com)

You manage the live code AND the live site of **corkandcurve.com**, a static
SEO-driven wine + spirits travel atlas. Sister site to **tablejourney.com**
(food travel guide). Cross-linking strategy is light footer + contextual
entity cross-references, NOT bulk reciprocal links.

## READ FIRST (before any non-trivial work)

1. **[docs/HANDOFF.md](docs/HANDOFF.md)** — latest session state, what's
   pending, what was last completed. Always start here on a fresh session.
2. **[docs/STANDARDS.md](docs/STANDARDS.md)** — SEO + perf + correctness
   invariants every generator and agent must respect.
3. **[docs/DATA_TO_PAGES.md](docs/DATA_TO_PAGES.md)** — what every JSON
   field produces. Research agents need this to see the downstream
   impact of each field they fill.
4. **[docs/FLOW.md](docs/FLOW.md)** — operational playbook
   (research → QA chain → ship pipeline).
5. **[agents/wine-research/PROMPT.md](agents/wine-research/PROMPT.md)** —
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

## What to NOT do

- Do not put secrets / drafts / sensitive content under `content/` (publicly served).
- Do not change Caddyfile without asking Lewis.
- Do not duplicate TJ content. Wine entities must be wine-vertical-specific
  even when in the same region as a TJ city.
- Do not invent vineyard ownership, hectarage, or classification details.
  Wine is a credibility vertical — verified-block discipline is doubly
  important here.
