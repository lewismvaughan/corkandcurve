# Image sources ledger

Every image hosted on tablejourney.com (whether served from
`content/images/...` or hot-linked from a third-party CDN) is logged
here with its source, license, and photographer. This file is the
single takedown-defence document for the site.

**Rule:** if an image is on the live site and not in this ledger, it
gets removed. No exceptions.

## Allowed sources

| Source | License | Attribution required? | Commercial OK? |
|--------|---------|----------------------|----------------|
| Unsplash (https://unsplash.com) | Unsplash License | No (appreciated) | Yes |
| Pexels (https://pexels.com) | Pexels License | No (appreciated) | Yes |
| Wikimedia Commons CC0 / PD | Public Domain | No | Yes |
| Wikimedia Commons CC-BY | CC-BY-4.0 | **Yes** (credit on page) | Yes |
| Wikimedia Commons CC-BY-SA | CC-BY-SA-4.0 | **Yes** (credit on page) | Yes, with attribution |
| AI-generated | n/a | No (mark as AI in metadata) | Yes |
| Custom photography (Lewis) | Owner-licensed | No | Yes |

## Forbidden sources

Google Image search. Pinterest. Instagram. TikTok. Any news site (AP,
Reuters, NYT, etc.). Restaurant or hotel sites (rights not yours).
Stock-photo previews with watermarks (Getty, Shutterstock, Alamy).
Anything where the license cannot be named.

## Live ledger

| File / URL | Source | License | Photographer | Date added | Notes |
|------------|--------|---------|--------------|------------|-------|
| `https://images.unsplash.com/photo-1616091216791-a5360b5fc78a` | Unsplash | Unsplash License | Celine Ylmz | 2026-05-18 | Paris hero (used in `site-data/france/paris/data/region.json` as `destination.hero_image`). Source: https://unsplash.com/photos/L2ost-ZEmK8 |
| `https://images.unsplash.com/photo-1581683705068-ca8f49fc7f45` | Unsplash | Unsplash License | Camille Brodard | 2026-05-18 | Paris card image (reserved; not yet referenced in JSON, available for future use). Source: https://unsplash.com/photos/iH5qFLZS390 |
| `content/og/default.jpg` | Generated locally by `scripts/generate_extras.py` (PIL) | Public Domain (machine-generated brand card) | n/a | 2026-05-18 | 1200x630 brand card, plain text on solid colour. |
| `content/og/paris.jpg` | Generated locally by `scripts/generate_extras.py` (PIL) | Public Domain (machine-generated brand card) | n/a | 2026-05-18 | 1200x630 brand card, plain text on solid colour. |
| `content/og/tokyo.jpg` | Generated locally by `scripts/generate_extras.py` (PIL) | Public Domain (machine-generated brand card) | n/a | 2026-05-18 | 1200x630 brand card, plain text on solid colour. |

## Process

**When a subagent adds a city image:**

1. Image URL goes into `site-data/<country>/<city>/data/region.json` under
   `destination.hero_image` (and matching `_source`, `_source_url`,
   `_photographer`, `_license` fields).
2. Subagent adds a line to this ledger before validation runs.
3. Validator (future) will refuse to ship a city whose `destination.hero_image`
   doesn't have a matching row here.

**When Lewis adds his own photography:**

1. Drop the file under `content/images/<city>/` or `content/og/`.
2. Add a row here with `Source: Custom photography (Lewis)`, `License: Owner-licensed`.

**When something is unknown:**

Don't include it on the live site. Better thin than borrowed.

## Auditing

Periodic spot-check command:

```
# Every image referenced in JSON should have a ledger row.
grep -roh 'hero_image[^"]*' site-data/ | sort -u
```
