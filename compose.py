#!/usr/bin/env python3
"""Draw the catalogue photo: 'The Self-Pouring Teapot'.

A glossy deep-teal ceramic teapot hovers tilted in mid-air, pouring a smooth
amber stream of tea into a white porcelain cup below it -- no hand, no
saucer, no clutter. One hero product, one accessory (the cup), seamless
studio background, soft key light from upper left. The joke reads at a
glance: the teapot pours itself.

Rendered at 2x and downscaled for smooth anti-aliasing. Deterministic:
same bytes on every run. Output: entry.png, 1024x1024, < 1 MiB.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2                      # supersample factor
W, H = 1024 * S, 1024 * S  # working canvas

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def vgrad(w, h, top, bottom):
    """Vertical RGB gradient as an RGB image."""
    t = np.linspace(0, 1, h)[:, None, None]
    top = np.array(top, dtype=float)[None, None, :]
    bottom = np.array(bottom, dtype=float)[None, None, :]
    arr = (top * (1 - t) + bottom * t).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, w, axis=1), "RGB")


def bezier(p0, p1, p2, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def ribbon(centerline, widths, fill):
    """A tapered band around a centreline: returns a polygon point list."""
    left, right = [], []
    for (x, y), w in zip(centerline, widths):
        # normal from local direction
        i = centerline.index((x, y)) if False else None
        left.append((x - w, y))
        right.append((x + w, y))
    return left + right[::-1]


def tube_polygon(centerline, w0, w1):
    """Polygon for a tapered tube along a centreline (width varies linearly,
    measured horizontally -- good for a near-vertical pouring stream)."""
    n = len(centerline)
    left, right = [], []
    for i, (x, y) in enumerate(centerline):
        w = w0 + (w1 - w0) * i / max(1, n - 1)
        left.append((x - w, y))
        right.append((x + w, y))
    return left + right[::-1]


def soft_ellipse(layer, box, fill, blur):
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.ellipse(box, fill=fill)
    tmp = tmp.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(tmp)


def steam_wisp(layer, x0, y0, height, amplitude, alpha=110, width=26):
    """A curling translucent steam wisp rising from (x0, y0)."""
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    pts = []
    steps = 60
    for i in range(steps + 1):
        t = i / steps
        x = x0 + math.sin(t * math.pi * 2.2) * amplitude * t + t * 30
        y = y0 - t * height
        pts.append((x, y))
    w = width * (1 - 0.45 * 0.5)
    for i in range(0, len(pts) - 1, 2):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        ww = width * (1 - 0.4 * i / len(pts))
        d.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, alpha), width=int(ww))
    tmp = tmp.filter(ImageFilter.GaussianBlur(14))
    layer.alpha_composite(tmp)


def draw_teapot_layer():
    """Teapot drawn upright on its own layer, then rotated as a whole so the
    tilt, spout, handle and lid all stay consistent."""
    LW, LH = 1500, 950
    layer = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    cx, cy = 800, 460          # body centre
    bw, bh = 430, 320          # body ellipse radii-ish (w, h)

    # --- spout FIRST (its base hides behind the body): tapered, rising from
    # the left shoulder then tipping down to a rounded mouth
    spout = [(cx - bw + 60, cy - 60), (cx - bw - 120, cy - 160),
             (cx - bw - 240, cy - 60), (cx - bw - 260, cy + 30),
             (cx - bw - 220, cy + 80), (cx - bw - 120, cy + 70),
             (cx - bw + 40, cy + 100)]
    d.polygon(spout, fill=(16, 92, 96, 255))
    d.polygon([(cx - bw - 240, cy - 60), (cx - bw - 260, cy + 30),
               (cx - bw - 220, cy + 80), (cx - bw - 170, cy + 20)],
              fill=(9, 58, 63, 255))
    # spout tip opening (dark) -- the mouth the tea pours from
    d.ellipse([cx - bw - 266, cy + 8, cx - bw - 218, cy + 58],
              fill=(6, 30, 33, 255))

    # --- handle FIRST (its inner half hides behind the body): thick C on the
    # right, drawn as a ring whose left side the body will cover
    d.ellipse([cx + bw - 170, cy - 160, cx + bw + 180, cy + 180],
              outline=(13, 74, 78, 255), width=46)
    d.ellipse([cx + bw - 170, cy - 160, cx + bw + 180, cy + 180],
              outline=(38, 132, 136, 255), width=16)

    # --- body: glossy deep-teal ceramic, radial-ish shading via stacked ellipses
    # base body
    d.ellipse([cx - bw, cy - bh, cx + bw, cy + bh], fill=(16, 92, 96, 255))
    # lower shade (darker teal, bottom) -- kept shallow so the pot is not a dark mass
    d.ellipse([cx - bw + 18, cy - bh + 210, cx + bw - 18, cy + bh - 6],
              fill=(11, 66, 71, 255))
    # upper light wash (lighter teal, top-left)
    d.ellipse([cx - bw + 26, cy - bh + 8, cx + bw - 60, cy + bh - 170],
              fill=(32, 128, 132, 255))
    # warm rim light on the right edge
    d.ellipse([cx + bw - 70, cy - bh + 40, cx + bw - 6, cy + bh - 40],
              fill=(58, 158, 160, 255))
    # specular highlight: soft diagonal streak, upper left
    hi = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    dh = ImageDraw.Draw(hi)
    dh.ellipse([cx - 330, cy - 260, cx - 40, cy + 10], fill=(255, 255, 255, 70))
    hi = hi.filter(ImageFilter.GaussianBlur(30))
    layer.alpha_composite(hi)
    # small hard glint
    d.ellipse([cx - 250, cy - 190, cx - 170, cy - 130], fill=(255, 255, 255, 130))

    # --- foot ring
    d.ellipse([cx - 150, cy + bh - 42, cx + 150, cy + bh + 6], fill=(10, 52, 56, 255))

    # --- lid: shallow dome + knob
    d.ellipse([cx - 190, cy - bh - 52, cx + 190, cy - bh + 60], fill=(22, 104, 108, 255))
    d.ellipse([cx - 190, cy - bh - 52, cx + 150, cy - bh + 10], fill=(40, 138, 142, 255))
    d.ellipse([cx - 34, cy - bh - 108, cx + 34, cy - bh - 44], fill=(8, 48, 52, 255))
    d.ellipse([cx - 34, cy - bh - 108, cx + 10, cy - bh - 62], fill=(70, 170, 172, 255))

    # --- product label: small cream band with model mark (text belongs to
    # the product, never an explanation of the joke)
    d.rounded_rectangle([cx - 130, cy + 30, cx + 130, cy + 110],
                        radius=12, fill=(238, 228, 200, 255))
    f_big = ImageFont.truetype(DEJAVU_B, 58)
    f_small = ImageFont.truetype(DEJAVU, 30)
    d.text((cx, cy + 52), "SP-1", font=f_big, fill=(16, 80, 84, 255), anchor="mm")
    d.text((cx, cy + 94), "SELF-POURING", font=f_small,
           fill=(16, 80, 84, 255), anchor="mm")

    return layer


def main():
    img = vgrad(W, H, (233, 231, 227), (196, 193, 187)).convert("RGBA")
    d = ImageDraw.Draw(img)

    # --- seamless studio sweep: slightly darker floor from y ~ 78% down
    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    df = ImageDraw.Draw(floor)
    df.rectangle([0, int(H * 0.78), W, H], fill=(178, 174, 168, 255))
    floor = floor.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(floor)

    # soft contact shadow under the cup, and a diffuse one under the floating pot
    soft_ellipse(img, [760, 1560, 1300, 1640], (0, 0, 0, 90), 26)
    soft_ellipse(img, [620, 1500, 1450, 1600], (0, 0, 0, 46), 60)

    # --- teacup (the one accessory): white porcelain, centred under the pot
    cup_cx, cup_top, cup_bot = 1024, 1420, 1580
    # cup body: tapered, slightly flared rim
    d.polygon([(cup_cx - 190, cup_top), (cup_cx + 190, cup_top),
               (cup_cx + 140, cup_bot), (cup_cx - 140, cup_bot)],
              fill=(248, 247, 243, 255))
    # left shade + right warm light on the cup wall
    d.polygon([(cup_cx - 190, cup_top), (cup_cx - 120, cup_top),
               (cup_cx - 100, cup_bot), (cup_cx - 140, cup_bot)],
              fill=(214, 212, 206, 255))
    d.polygon([(cup_cx + 120, cup_top), (cup_cx + 190, cup_top),
               (cup_cx + 140, cup_bot), (cup_cx + 118, cup_bot)],
              fill=(255, 255, 255, 255))
    # rim + tea surface
    d.ellipse([cup_cx - 190, cup_top - 34, cup_cx + 190, cup_top + 34],
              fill=(255, 255, 255, 255))
    d.ellipse([cup_cx - 168, cup_top - 24, cup_cx + 168, cup_top + 24],
              fill=(176, 108, 32, 255))
    d.ellipse([cup_cx - 168, cup_top - 24, cup_cx + 120, cup_top + 8],
              fill=(198, 132, 48, 255))
    # tea glint
    d.ellipse([cup_cx - 110, cup_top - 14, cup_cx - 20, cup_top + 4],
              fill=(232, 178, 92, 255))
    # cup foot
    d.ellipse([cup_cx - 110, cup_bot - 12, cup_cx + 110, cup_bot + 16],
              fill=(226, 224, 218, 255))

    # --- teapot, tilted, hovering above the cup
    pot = draw_teapot_layer()
    pot = pot.rotate(24, resample=Image.BICUBIC, center=(800, 460))
    # spout tip after rotation lands near working (499, 1053)
    img.alpha_composite(pot, (300, 290))

    # --- tea stream: from the spout tip arcing down into the cup
    p0 = (499, 1053)      # spout tip
    p1 = (700, 1250)      # control: arc out then down
    p2 = (950, 1408)      # into the tea surface
    centre = bezier(p0, p1, p2, 60)
    stream = tube_polygon(centre, 34, 16)
    d.polygon(stream, fill=(188, 118, 34, 255))
    # bright core of the stream
    core = tube_polygon([(x + 8, y) for (x, y) in centre], 13, 6)
    d.polygon(core, fill=(226, 164, 74, 255))
    # splash ring where the stream meets the tea
    d.ellipse([cup_cx - 70, cup_top - 46, cup_cx + 70, cup_top - 6],
              outline=(226, 164, 74, 255), width=8)

    # --- steam: two wisps, one from the cup, one from the spout tip
    steam_wisp(img, 1000, 1400, 260, 34, alpha=100, width=30)
    steam_wisp(img, 500, 1020, 200, 26, alpha=80, width=22)

    # --- downscale to the 1024x1024 entry
    out = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    out.save("entry.png", "PNG", optimize=True)
    print("entry.png", out.size)


if __name__ == "__main__":
    main()
