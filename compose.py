#!/usr/bin/env python3
"""Draw the catalogue photo: 'The Self-Pouring Teapot'.

A glossy deep-teal ceramic teapot hovers tilted in mid-air, pouring a smooth
amber stream of tea into a white porcelain cup below it -- no hand, no
saucer, no clutter. One hero product, one accessory (the cup), seamless
studio background, soft key light from upper left. The joke reads at a
glance: the teapot pours itself.

Revision notes (this pass): the product label is now drawn level and much
larger AFTER the pot is rotated, so "SP-1 / SELF-POURING" is legible at a
glance; the handle is a thick arc welded to the body with mount blobs
instead of a thin floating ring; the spout carries a top-edge highlight and
an amber-rimmed mouth; a small AUTO-POUR gauge dial on the body sharpens
the engineered-absurdity cue; the cup is slightly larger with a soft floor
reflection.

Rendered at 2x and downscaled for smooth anti-aliasing. Deterministic:
same bytes on every run. Output: entry.png, 1024x1024, < 1 MiB.
"""
import math
import os
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
    for i in range(0, len(pts) - 1, 2):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        ww = width * (1 - 0.4 * i / len(pts))
        d.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, alpha), width=int(ww))
    tmp = tmp.filter(ImageFilter.GaussianBlur(14))
    layer.alpha_composite(tmp)


def draw_teapot_layer():
    """Teapot drawn upright on its own layer, then rotated as a whole so the
    tilt, spout, handle and lid all stay consistent. No label here: the
    label is drawn level on the finished image, after rotation."""
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
    # spout top-edge highlight: a lighter strip along the upper edge so the
    # spout reads as a solid cast piece, not a flat slab
    d.polygon([(cx - bw + 40, cy - 44), (cx - bw - 110, cy - 140),
               (cx - bw - 226, cy - 52), (cx - bw - 210, cy - 18),
               (cx - bw - 110, cy - 104), (cx - bw + 30, cy - 8)],
              fill=(38, 132, 136, 255))
    # shaded underside of the spout
    d.polygon([(cx - bw - 240, cy - 60), (cx - bw - 260, cy + 30),
               (cx - bw - 220, cy + 80), (cx - bw - 170, cy + 20)],
              fill=(9, 58, 63, 255))
    # spout tip opening (dark) with an amber rim of tea at the mouth
    d.ellipse([cx - bw - 266, cy + 8, cx - bw - 218, cy + 58],
              fill=(6, 30, 33, 255))
    d.ellipse([cx - bw - 258, cy + 16, cx - bw - 226, cy + 50],
              fill=(188, 118, 34, 255))

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
    # second, smaller glint low on the body for a glazed-ceramic read
    d.ellipse([cx + 120, cy + 130, cx + 190, cy + 180], fill=(255, 255, 255, 70))

    # --- handle: a thick arc hugging the body's right side, welded on with
    # two mount blobs where it meets the body -- reads as one cast piece
    d.arc([cx - 500, cy - 390, cx + 500, cy + 390], start=-72, end=72,
          fill=(13, 74, 78, 255), width=64)
    d.arc([cx - 500, cy - 390, cx + 500, cy + 390], start=-72, end=72,
          fill=(38, 132, 136, 255), width=18)
    # mount blobs at the arc ends (top and bottom joints)
    for mx, my in [(cx + 118, cy - 330), (cx + 118, cy + 330)]:
        d.ellipse([mx - 52, my - 52, mx + 52, my + 52], fill=(16, 92, 96, 255))
        d.ellipse([mx - 52, my - 52, mx + 8, my + 8], fill=(38, 132, 136, 255))

    # --- AUTO-POUR gauge dial on the upper body: white face, red pour zone,
    # needle swung into it -- the engineered-absurdity cue
    gx, gy, gr = cx + 150, cy - 190, 54
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(8, 48, 52, 255))
    d.ellipse([gx - gr + 7, gy - gr + 7, gx + gr - 7, gy + gr - 7],
              fill=(244, 241, 232, 255))
    # red pour zone (upper-right quadrant of the dial face)
    d.arc([gx - gr + 14, gy - gr + 14, gx + gr - 14, gy + gr - 14],
          start=-78, end=8, fill=(178, 52, 36, 255), width=10)
    # tick marks
    for ang in range(-120, 121, 30):
        a = math.radians(ang - 90)
        x1 = gx + (gr - 20) * math.cos(a)
        y1 = gy + (gr - 20) * math.sin(a)
        x2 = gx + (gr - 12) * math.cos(a)
        y2 = gy + (gr - 12) * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=(16, 80, 84, 255), width=4)
    # needle pointing into the red zone (up-right)
    na = math.radians(-45 - 90)
    d.line([(gx, gy), (gx + (gr - 24) * math.cos(na),
                       gy + (gr - 24) * math.sin(na))],
           fill=(178, 52, 36, 255), width=7)
    d.ellipse([gx - 9, gy - 9, gx + 9, gy + 9], fill=(16, 80, 84, 255))

    # --- foot ring
    d.ellipse([cx - 150, cy + bh - 42, cx + 150, cy + bh + 6], fill=(10, 52, 56, 255))

    # --- lid: shallow dome + knob
    d.ellipse([cx - 190, cy - bh - 52, cx + 190, cy - bh + 60], fill=(22, 104, 108, 255))
    d.ellipse([cx - 190, cy - bh - 52, cx + 150, cy - bh + 10], fill=(40, 138, 142, 255))
    d.ellipse([cx - 34, cy - bh - 108, cx + 34, cy - bh - 44], fill=(8, 48, 52, 255))
    d.ellipse([cx - 34, cy - bh - 108, cx + 10, cy - bh - 62], fill=(70, 170, 172, 255))

    return layer


def draw_label(d, cx, cy):
    """Product label, drawn LEVEL on the finished image after the pot is
    rotated, so it reads at a glance: cream band, model mark, function line.
    Text belongs to the product, never an explanation of the joke."""
    d.rounded_rectangle([cx - 220, cy - 64, cx + 220, cy + 64],
                        radius=14, fill=(238, 228, 200, 255),
                        outline=(16, 80, 84, 255), width=3)
    f_big = ImageFont.truetype(DEJAVU_B, 72)
    f_small = ImageFont.truetype(DEJAVU, 38)
    d.text((cx, cy - 26), "SP-1", font=f_big, fill=(16, 80, 84, 255), anchor="mm")
    d.text((cx, cy + 34), "SELF-POURING", font=f_small,
           fill=(16, 80, 84, 255), anchor="mm")


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
    cup_cx, cup_top, cup_bot = 1024, 1400, 1600
    # cup body: tapered, slightly flared rim
    d.polygon([(cup_cx - 210, cup_top), (cup_cx + 210, cup_top),
               (cup_cx + 155, cup_bot), (cup_cx - 155, cup_bot)],
              fill=(248, 247, 243, 255))
    # left shade + right warm light on the cup wall
    d.polygon([(cup_cx - 210, cup_top), (cup_cx - 130, cup_top),
               (cup_cx - 112, cup_bot), (cup_cx - 155, cup_bot)],
              fill=(214, 212, 206, 255))
    d.polygon([(cup_cx + 132, cup_top), (cup_cx + 210, cup_top),
               (cup_cx + 155, cup_bot), (cup_cx + 130, cup_bot)],
              fill=(255, 255, 255, 255))
    # rim + tea surface
    d.ellipse([cup_cx - 210, cup_top - 36, cup_cx + 210, cup_top + 36],
              fill=(255, 255, 255, 255))
    d.ellipse([cup_cx - 186, cup_top - 26, cup_cx + 186, cup_top + 26],
              fill=(176, 108, 32, 255))
    d.ellipse([cup_cx - 186, cup_top - 26, cup_cx + 132, cup_top + 8],
              fill=(198, 132, 48, 255))
    # tea glint
    d.ellipse([cup_cx - 122, cup_top - 16, cup_cx - 22, cup_top + 4],
              fill=(232, 178, 92, 255))
    # cup foot
    d.ellipse([cup_cx - 122, cup_bot - 12, cup_cx + 122, cup_bot + 16],
              fill=(226, 224, 218, 255))
    # faint floor reflection of the cup
    soft_ellipse(img, [cup_cx - 130, cup_bot + 6, cup_cx + 130, cup_bot + 60],
                 (255, 255, 255, 40), 18)

    # --- teapot, tilted, hovering above the cup
    pot = draw_teapot_layer()
    pot = pot.rotate(24, resample=Image.BICUBIC, center=(800, 460))
    # spout tip after rotation lands near working (499, 1053)
    img.alpha_composite(pot, (300, 290))

    # --- level product label on the pot body (screen coords, after rotation)
    draw_label(d, 1100, 860)

    # --- tea stream: from the spout tip arcing down into the cup
    p0 = (499, 1053)      # spout tip
    p1 = (700, 1250)      # control: arc out then down
    p2 = (950, 1408)      # into the tea surface
    centre = bezier(p0, p1, p2, 60)
    stream = tube_polygon(centre, 36, 18)
    d.polygon(stream, fill=(188, 118, 34, 255))
    # bright core of the stream
    core = tube_polygon([(x + 8, y) for (x, y) in centre], 14, 7)
    d.polygon(core, fill=(226, 164, 74, 255))
    # splash ring where the stream meets the tea
    d.ellipse([cup_cx - 78, cup_top - 48, cup_cx + 78, cup_top - 6],
              outline=(226, 164, 74, 255), width=8)

    # --- steam: two wisps, one from the cup, one from the spout tip
    steam_wisp(img, 1000, 1400, 260, 34, alpha=100, width=30)
    steam_wisp(img, 500, 1020, 200, 26, alpha=80, width=22)

    # --- downscale to the 1024x1024 entry
    out = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    out.save("entry.png", "PNG", optimize=True)
    print("entry.png", out.size, os.path.getsize("entry.png"), "bytes")


if __name__ == "__main__":
    main()
