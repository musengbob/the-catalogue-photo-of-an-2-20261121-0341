#!/usr/bin/env python3
"""The Self-Pouring Teapot (SP-1) — catalogue photograph, drawn with Pillow.

A glossy teal teapot floats tilted mid-air, pouring a bright amber stream
into a white porcelain cup below it. No hand anywhere. Exactly one
accessory: the cup. Clean light studio background, soft floor shadow.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

TEAL = (18, 122, 128)
TEAL_DARK = (9, 84, 92)
TEAL_LIGHT = (64, 178, 184)
TEAL_GLOSS = (150, 225, 228)
AMBER = (214, 132, 26)
AMBER_DEEP = (176, 96, 10)
AMBER_CORE = (255, 196, 80)
CREAM = (250, 247, 240)
INK = (32, 38, 40)


def font(size, bold=True):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def vgrad(size, top, bottom):
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        d.line([(0, y), (size[0], y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def soft_ellipse(base, box, fill, blur):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=fill)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def main():
    img = vgrad((W, H), (252, 250, 245), (226, 219, 205)).convert("RGBA")
    d = ImageDraw.Draw(img)

    # --- studio floor -------------------------------------------------
    d.rectangle([0, 838, W, H], fill=(214, 206, 190, 255))
    d.rectangle([0, 838, W, 842], fill=(196, 187, 170, 255))

    # --- soft floor shadows (cup + pot) -------------------------------
    soft_ellipse(img, (300, 872, 620, 918), (90, 80, 64, 110), 14)
    soft_ellipse(img, (360, 884, 560, 908), (70, 62, 50, 130), 8)

    # --- cup: white porcelain, exactly one accessory ------------------
    # body: tapered cup, rim ellipse on top, foot at bottom
    d.polygon([(330, 762), (590, 762), (560, 872), (360, 872)],
              fill=(255, 255, 255, 255))
    d.polygon([(330, 762), (590, 762), (586, 800), (334, 800)],
              fill=(238, 236, 230, 255))
    d.ellipse([330, 742, 590, 782], fill=(255, 255, 255, 255))
    d.ellipse([330, 742, 590, 782], outline=(190, 186, 178, 255), width=3)
    # tea surface inside the cup
    d.ellipse([348, 748, 572, 778], fill=(196, 116, 18, 255))
    d.ellipse([360, 752, 560, 774], fill=(232, 156, 44, 255))
    # splash ring where the stream lands
    d.ellipse([428, 748, 492, 776], outline=(255, 214, 110, 255), width=4)
    d.ellipse([440, 754, 480, 770], outline=(255, 236, 170, 255), width=3)
    # cup shading + foot
    d.polygon([(560, 800), (590, 762), (560, 872), (540, 872)],
              fill=(224, 221, 214, 255))
    d.ellipse([392, 866, 528, 884], fill=(226, 223, 216, 255))
    d.ellipse([392, 866, 528, 884], outline=(198, 194, 186, 255), width=2)
    # cup highlight
    d.rounded_rectangle([352, 792, 372, 856], radius=10,
                        fill=(255, 255, 255, 160))

    # --- teapot body on its own layer, tilted -------------------------
    pot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pot)
    cx, cy, rx, ry = 560, 420, 235, 165
    pd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=TEAL + (255,))
    pd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
               outline=TEAL_DARK + (255,), width=5)
    # belly shading: darker lower half
    pd.pieslice([cx - rx, cy - ry, cx + rx, cy + ry], 20, 160,
                fill=TEAL_DARK + (55,))
    # lid dome + knob
    pd.ellipse([cx - 95, cy - ry - 52, cx + 95, cy - ry + 38],
               fill=TEAL_LIGHT + (255,))
    pd.ellipse([cx - 95, cy - ry - 52, cx + 95, cy - ry + 38],
               outline=TEAL_DARK + (255,), width=4)
    pd.ellipse([cx - 26, cy - ry - 78, cx + 26, cy - ry - 30],
               fill=TEAL_DARK + (255,))
    pd.ellipse([cx - 14, cy - ry - 72, cx + 14, cy - ry - 48],
               fill=TEAL_GLOSS + (255,))
    # gloss streaks on the body
    pd.ellipse([cx - 190, cy - 120, cx - 90, cy + 40],
               fill=(255, 255, 255, 70))
    pd.ellipse([cx + 120, cy - 60, cx + 190, cy + 90],
               fill=(255, 255, 255, 45))
    pot = pot.rotate(-14, resample=Image.BICUBIC, center=(cx, cy))
    img.alpha_composite(pot)

    # --- spout: tapered, from body lower-left down to the tip ---------
    d.polygon([(392, 470), (430, 428), (352, 596), (318, 612)],
              fill=TEAL + (255,))
    d.polygon([(392, 470), (430, 428), (352, 596), (318, 612)],
              outline=TEAL_DARK + (255,))
    d.polygon([(400, 462), (428, 434), (366, 584), (340, 596)],
              fill=TEAL_LIGHT + (255,))
    # amber rim + tea visible at the spout tip
    d.ellipse([306, 596, 352, 632], fill=AMBER_DEEP + (255,))
    d.ellipse([314, 604, 344, 624], fill=AMBER + (255,))

    # --- handle: thick arc welded to the body, right side -------------
    # arc box chosen so both ends land on the body edge; weld dots sit
    # exactly on the arc ends so the handle reads as attached.
    d.arc([620, 330, 820, 540], start=285, end=75,
          fill=TEAL_DARK + (255,), width=30)
    d.arc([628, 338, 812, 532], start=285, end=75,
          fill=TEAL + (255,), width=18)
    d.ellipse([730, 318, 762, 350], fill=TEAL_DARK + (255,))  # upper weld
    d.ellipse([730, 520, 762, 552], fill=TEAL_DARK + (255,))  # lower weld

    # --- tea stream: spout tip -> cup, bright core --------------------
    stream = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stream)
    pts = [(329, 626), (352, 664), (398, 700), (436, 728), (460, 756)]
    sd.line(pts, fill=AMBER + (235,), width=26, joint="curve")
    sd.line(pts, fill=AMBER_CORE + (255,), width=11, joint="curve")
    for (x, y, r) in [(345, 650, 7), (392, 696, 8), (428, 724, 7)]:
        sd.ellipse([x - r, y - r, x + r, y + r], fill=AMBER_CORE + (255,))
    stream = stream.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(stream)
    # splash droplets above the cup
    for (x, y, r) in [(452, 742, 6), (472, 738, 4), (442, 734, 4)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=AMBER_CORE + (255,))

    # --- product label: LEVEL, legible, on the pot body ---------------
    d.rounded_rectangle([452, 392, 668, 492], radius=12,
                        fill=(255, 255, 255, 255),
                        outline=(30, 40, 42, 255), width=3)
    d.text((560, 414), "SP-1", font=font(46), fill=INK + (255,),
           anchor="ma")
    d.text((560, 466), "SELF-POURING", font=font(24), fill=INK + (255,),
           anchor="ma")

    # --- AUTO-POUR gauge dial on the pot body --------------------------
    gx, gy, gr = 668, 560, 46
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr],
              fill=(255, 255, 255, 255), outline=(30, 40, 42, 255), width=4)
    # red pour zone (upper-right arc)
    d.arc([gx - gr + 8, gy - gr + 8, gx + gr - 8, gy + gr - 8],
          start=300, end=20, fill=(214, 48, 32, 255), width=10)
    # tick marks
    for ang in range(150, 391, 30):
        a = math.radians(ang)
        x0 = gx + int((gr - 8) * math.cos(a)); y0 = gy + int((gr - 8) * math.sin(a))
        x1 = gx + int((gr - 16) * math.cos(a)); y1 = gy + int((gr - 16) * math.sin(a))
        d.line([(x0, y0), (x1, y1)], fill=INK + (255,), width=3)
    # needle swung into the red zone (pointing up-right)
    na = math.radians(325)
    d.line([(gx, gy), (gx + int((gr - 12) * math.cos(na)),
                        gy + int((gr - 12) * math.sin(na)))],
           fill=(214, 48, 32, 255), width=5)
    d.ellipse([gx - 7, gy - 7, gx + 7, gy + 7], fill=INK + (255,))
    d.text((gx, gy + 28), "AUTO-POUR", font=font(12), fill=INK + (255,),
           anchor="ma")

    # --- final gloss + vignette ---------------------------------------
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).ellipse([380, 250, 520, 330],
                                  fill=(255, 255, 255, 60))
    img.alpha_composite(gloss.filter(ImageFilter.GaussianBlur(18)))

    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
