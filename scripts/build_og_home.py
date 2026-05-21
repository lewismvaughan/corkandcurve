"""Build the homepage OG card (content/img/og-home.jpg).

Takes scripts/assets/og-home-source.png (Midjourney render of a globally laid
table), crops to the OG 1200x630 aspect, fades a soft dark gradient along the
bottom edge, and stamps the TABLEJOURNEY wordmark + tagline on top. Output is
served at https://tablejourney.com/img/og-home.jpg.

Re-run any time the source render changes.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "scripts" / "assets" / "og-home-source.png"
OUTPUT = REPO / "content" / "img" / "og-home.jpg"
FONT_BOLD = REPO / "scripts" / "fonts" / "PlayfairDisplay-Bold.ttf"

OG_W, OG_H = 1200, 630

WORDMARK = "TABLEJOURNEY"
TAGLINE = "where the world eats"

CREAM = (250, 247, 240)
SHADOW = (0, 0, 0)


def crop_to_og(img: Image.Image) -> Image.Image:
    """Scale to width=1200 keeping aspect, then center-crop to 1200x630."""
    src_w, src_h = img.size
    scale = OG_W / src_w
    new_h = round(src_h * scale)
    img = img.resize((OG_W, new_h), Image.LANCZOS)
    if new_h < OG_H:
        raise RuntimeError(
            f"source too short for OG aspect after scaling: {OG_W}x{new_h}"
        )
    top = (new_h - OG_H) // 2
    return img.crop((0, top, OG_W, top + OG_H))


def add_bottom_gradient(img: Image.Image, height: int = 200, max_alpha: int = 170) -> Image.Image:
    """Paint a soft black gradient along the bottom edge so the wordmark reads."""
    gradient = Image.new("RGBA", (OG_W, height), (0, 0, 0, 0))
    px = gradient.load()
    for y in range(height):
        # ease-in: alpha grows quadratically from 0 at top to max_alpha at bottom
        t = y / (height - 1)
        alpha = int(max_alpha * (t * t))
        for x in range(OG_W):
            px[x, y] = (0, 0, 0, alpha)
    base = img.convert("RGBA")
    base.alpha_composite(gradient, dest=(0, OG_H - height))
    return base


def draw_wordmark(img: Image.Image) -> Image.Image:
    """Stamp TABLEJOURNEY + tagline centered on the bottom strip."""
    draw = ImageDraw.Draw(img)

    word_font = ImageFont.truetype(str(FONT_BOLD), 64)
    tag_font = ImageFont.truetype(str(FONT_BOLD), 22)

    # Wordmark with extra letter-spacing for a magazine-cover feel.
    spaced = " ".join(list(WORDMARK))
    word_w = draw.textlength(spaced, font=word_font)
    word_x = (OG_W - word_w) / 2
    word_y = OG_H - 110

    # Soft shadow underlay (offset + blur) for legibility on any background.
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.text((word_x + 2, word_y + 3), spaced, font=word_font, fill=(0, 0, 0, 180))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(shadow_layer)

    draw.text((word_x, word_y), spaced, font=word_font, fill=CREAM)

    # Tagline below, smaller, also center-aligned.
    tag_w = draw.textlength(TAGLINE, font=tag_font)
    tag_x = (OG_W - tag_w) / 2
    tag_y = word_y + 74
    draw.text((tag_x + 1, tag_y + 2), TAGLINE, font=tag_font, fill=(0, 0, 0, 160))
    draw.text((tag_x, tag_y), TAGLINE, font=tag_font, fill=CREAM)

    return img


def main() -> None:
    img = Image.open(SOURCE)
    img = crop_to_og(img)
    img = add_bottom_gradient(img)
    img = draw_wordmark(img)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUTPUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"wrote {OUTPUT} ({OG_W}x{OG_H})")


if __name__ == "__main__":
    main()
