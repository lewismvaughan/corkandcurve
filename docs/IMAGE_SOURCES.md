# Cork & Curve — image sources

Where the research / orchestrator agents source hero images and OG
cards.

## Hero images per region

Order of preference:
1. **Producer-provided images** (only with explicit license — most
   estates retain rights). Skip unless the producer's site declares
   reusable media.
2. **Unsplash search** — license is permissive (Unsplash License) +
   doesn't require attribution but we attribute anyway in
   `hero_image_source_url`. Search queries:
   - `<region> vineyard landscape`
   - `<region> wine cellar`
   - `<region> tasting room`
   - `<country> wine region`
3. **Wikipedia Commons** — Creative Commons; attribution required;
   `hero_image_source_url` points at the Commons file page.
4. **Pixabay / Pexels** — fallback for less-photographed regions.

## OG image generation

The TJ `scripts/build_og_cities.py` generates OG cards (1200×630) from
region hero + region name overlay. Adapt for wine:
- `scripts/build_og_regions.py` (rename) — pulls hero from
  `region.json:destination.hero_image`, renders C&C-branded card
  (burgundy + cream typography).

## What NOT to do

- Don't host high-res producer photos without explicit license. We are
  a free editorial site — we don't have a budget for licensing fees.
- Don't reuse TJ hero images for C&C regions even when geographic
  overlap exists. Different vertical, different visual.
- Don't generate AI images for hero photography. Real photos
  (Unsplash / Commons) only.

## Image schema

In `region.json`:
```
"destination": {
  ...
  "hero_image": "https://images.unsplash.com/photo-1571867424488-...",
  "hero_image_source_url": "https://unsplash.com/photos/...",
  "hero_image_credit": "Photo by <photographer> on Unsplash"
}
```

`check_external_urls.py` HEAD-checks both URLs at ship time. If either
is dead, the region won't ship.
