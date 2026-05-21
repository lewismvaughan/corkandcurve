"""Build branded per-city OG cards at content/og/<city>.jpg.

For each city with a `hero_image` in region.json:
  1. Download the photo (cached on disk so re-runs are free).
  2. Crop/scale to the OG 1200x630 aspect.
  3. Apply a soft dark gradient along the bottom edge.
  4. Stamp the city name (display font) + a 'TableJourney' wordmark.

Result: link previews on iMessage / Slack / WhatsApp / Twitter show a
real food photo from the city with TJ branding overlaid, instead of a
raw Unsplash URL or a typography-only card.

Pair with the template_renderer priority change: `/og/<city>.jpg` is
preferred over the raw hero URL so the branded card wins.

Re-runnable; only re-downloads if the source URL changed.

Usage:
    python scripts/build_og_cities.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parent.parent
SITE_DATA = REPO / "site-data"
OUT_DIR = REPO / "content" / "og"
CACHE_DIR = REPO / "scripts" / "assets" / "og-cache"
FONT_BOLD = REPO / "scripts" / "fonts" / "PlayfairDisplay-Bold.ttf"

OG_W, OG_H = 1200, 630
CREAM = (250, 247, 240)


def _download(url: str, dest: Path) -> bool:
    """Download URL to dest. Returns True on success, False on failure.
    Uses a 30s timeout so a slow CDN doesn't hang the whole batch."""
    if dest.exists():
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TableJourney/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  [WARN] download failed for {url}: {exc}")
        return False


def _crop_to_og(img: Image.Image) -> Image.Image:
    """Scale + center-crop to 1200x630. Mirrors build_og_home.crop_to_og."""
    src_w, src_h = img.size
    scale_w = OG_W / src_w
    scale_h = OG_H / src_h
    scale = max(scale_w, scale_h)
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - OG_W) // 2
    top = (new_h - OG_H) // 2
    return img.crop((left, top, left + OG_W, top + OG_H))


def _add_bottom_gradient(img: Image.Image, height: int = 240, max_alpha: int = 200) -> Image.Image:
    gradient = Image.new("RGBA", (OG_W, height), (0, 0, 0, 0))
    px = gradient.load()
    for y in range(height):
        t = y / (height - 1)
        alpha = int(max_alpha * (t * t))
        for x in range(OG_W):
            px[x, y] = (0, 0, 0, alpha)
    base = img.convert("RGBA")
    base.alpha_composite(gradient, dest=(0, OG_H - height))
    return base


def _draw_text_with_shadow(img: Image.Image, text: str, font: ImageFont.FreeTypeFont,
                           x: float, y: float, fill: tuple,
                           shadow_alpha: int = 180, shadow_blur: int = 3) -> None:
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.text((x + 2, y + 3), text, font=font, fill=(0, 0, 0, shadow_alpha))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
    img.alpha_composite(shadow_layer)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, font=font, fill=fill)


def _draw_overlay(img: Image.Image, city_display: str) -> Image.Image:
    """Stamp city name + TableJourney wordmark on the bottom strip."""
    city_font = ImageFont.truetype(str(FONT_BOLD), 78)
    word_font = ImageFont.truetype(str(FONT_BOLD), 26)

    draw = ImageDraw.Draw(img)

    # City name (large, left-anchored)
    city_x = 60
    city_y = OG_H - 165
    _draw_text_with_shadow(img, city_display, city_font, city_x, city_y, CREAM)

    # Wordmark (smaller, left-anchored, below the city name)
    word_text = "TableJourney"
    word_y = city_y + 100
    _draw_text_with_shadow(img, word_text, word_font, city_x, word_y, CREAM,
                            shadow_alpha=150, shadow_blur=2)

    return img


def _city_display_from_data(payload: dict, fallback_slug: str) -> str:
    return (payload.get("destination") or {}).get("name") or fallback_slug.replace("-", " ").title()


def main() -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    failed = 0
    for country_dir in sorted(SITE_DATA.iterdir()):
        if not country_dir.is_dir():
            continue
        for city_dir in sorted(country_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name == "data":
                continue
            rj = city_dir / "data" / "region.json"
            if not rj.exists():
                continue
            try:
                payload = json.loads(rj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            dest = payload.get("destination") or {}
            hero = dest.get("hero_image") or (payload.get("research") or {}).get("hero_image")
            if not hero:
                skipped += 1
                continue

            city_slug = city_dir.name
            city_display = _city_display_from_data(payload, city_slug)
            url_hash = hashlib.sha1(hero.encode("utf-8")).hexdigest()[:12]
            cache_path = CACHE_DIR / f"{city_slug}-{url_hash}.jpg"

            if not _download(hero, cache_path):
                failed += 1
                continue

            try:
                img = Image.open(cache_path).convert("RGB")
            except Exception as exc:  # noqa: BLE001
                print(f"  [WARN] could not open cached image for {city_slug}: {exc}")
                failed += 1
                continue

            img = _crop_to_og(img)
            img = _add_bottom_gradient(img)
            img = _draw_overlay(img, city_display)
            out_path = OUT_DIR / f"{city_slug}.jpg"
            img.convert("RGB").save(out_path, "JPEG", quality=86, optimize=True, progressive=True)
            written += 1

    print(f"wrote {written} city OG cards to {OUT_DIR}")
    if skipped:
        print(f"skipped {skipped} cities with no hero_image in region.json")
    if failed:
        print(f"failed {failed} cities (download or decode)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
