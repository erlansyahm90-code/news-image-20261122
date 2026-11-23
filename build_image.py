#!/usr/bin/env python3
"""Build the news-image-20261122 poster (Sunday 22 November 2026).

Local build tool only: renders entry.png with Pillow + DejaVu fonts.
The graded program is main.ts, which simply copies the bundled entry.png
to /output/entry.png (Node stdlib only, deterministic bytes).

Design: midnight-blue broadsheet with a neon-yellow accent, in four
blocks ordered by news weight --
  (1) COP31 + climate/environment, led by the summit's collapse;
  (2) politics & global diplomacy; (3) Indonesia + economy; (4) sport --
followed by a numbered "also" list, a date-check footer and sources.
48 stories, every one verified as having happened or first been
reported on Sunday 22 November 2026 (see the research file
news-image-20261122-research.md, refreshed 23 Nov 09:20 WIB).

Lead fact, stated plainly: COP31 COLLAPSED. The closing session ended
with no deal -- the first COP to fail since Copenhagen 2009 and the
longest climate summit in history. President Kurum: "there is no
agreement on this text." The final text never mentions fossil fuels.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W, H = 1024, 1024
MX = 14                      # side margin
CW = W - 2 * MX              # content width (996)

# ------------------------------------------------------------- palette
# Midnight blue + neon yellow. All text colours are bright enough to
# read on the dark ground; region tags use light, distinct hues.
BG = (9, 18, 36)             # midnight blue ground
PANEL = (15, 27, 50)         # lead panel
PANEL2 = (21, 36, 64)        # sport score band
CARD = (13, 24, 45)          # medium card ground
YELLOW = (255, 230, 0)       # neon yellow accent
YELLOW_SOFT = (255, 242, 130)
WHITE = (245, 248, 252)
MUTED = (168, 183, 208)      # body text on dark
FAINT = (122, 142, 172)      # footer / small print
RULE = (48, 68, 100)         # hairlines
RED = (255, 110, 100)        # disaster accent (sparingly)

REGION_COLORS = {
    "CLIMATE": (120, 230, 160),
    "EUROPE": (125, 175, 255),
    "MIDDLE EAST": (255, 175, 90),
    "ASIA": (205, 145, 255),
    "AMERICAS": (255, 120, 120),
    "AFRICA": (110, 225, 135),
    "OCEANIA": (95, 225, 215),
    "GLOBAL": (215, 215, 215),
    "INDONESIA": (255, 145, 145),
    "SPORT": (255, 220, 80),
}

# --------------------------------------------------------------- fonts
_FONT_SPECS = (
    ("MAST", "DejaVuSerif-Bold.ttf", 48),   # masthead date
    ("TOP", "DejaVuSans-Bold.ttf", 11),     # top bar
    ("TOP_R", "DejaVuSans.ttf", 11),
    ("LEAD_H", "DejaVuSerif-Bold.ttf", 35),  # COP31 headline
    ("LEAD_B", "DejaVuSans.ttf", 12),       # lead body
    ("CHIP", "DejaVuSans-Bold.ttf", 10),    # stat chips
    ("SEC", "DejaVuSans-Bold.ttf", 12),     # block headers
    ("TAG", "DejaVuSans-Bold.ttf", 9),      # card tags
    ("MED_H", "DejaVuSerif-Bold.ttf", 13),  # medium heads
    ("MED_B", "DejaVuSans.ttf", 10),        # medium bodies
    ("SCORE", "DejaVuSerif-Bold.ttf", 12),  # sport score line
    ("SPORT_B", "DejaVuSans.ttf", 9),       # sport detail
    ("ALSO", "DejaVuSans.ttf", 9),          # also list
    ("ALSO_B", "DejaVuSans-Bold.ttf", 9),
    ("FOOT", "DejaVuSans.ttf", 9),
    ("NUM", "DejaVuSans-Bold.ttf", 9),
    ("ILL", "DejaVuSans-Bold.ttf", 9),      # labels inside drawings
)


def _load_font(filename, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, filename), size)


_F = {key: _load_font(fname, pt) for key, fname, pt in _FONT_SPECS}
F_MAST = _F["MAST"]
F_TOP = _F["TOP"]
F_TOP_R = _F["TOP_R"]
F_LEAD_H = _F["LEAD_H"]
F_LEAD_B = _F["LEAD_B"]
F_CHIP = _F["CHIP"]
F_SEC = _F["SEC"]
F_TAG = _F["TAG"]
F_MED_H = _F["MED_H"]
F_MED_H = _F["MED_H"]
F_MED_B = _F["MED_B"]
F_SCORE = _F["SCORE"]
F_SPORT_B = _F["SPORT_B"]
F_ALSO = _F["ALSO"]
F_ALSO_B = _F["ALSO_B"]
F_FOOT = _F["FOOT"]
F_NUM = _F["NUM"]
F_ILL = _F["ILL"]


# -------------------------------------------------------------- helpers
def wrap(d, text, fnt, max_w):
    """Greedy word wrap: pack as many words per line as fit in max_w."""
    fitted = []
    current = ""
    for piece in text.split():
        candidate = piece if not current else current + " " + piece
        if d.textlength(candidate, font=fnt) <= max_w:
            current = candidate
        else:
            if current:
                fitted.append(current)
            current = piece
    if current:
        fitted.append(current)
    return fitted


def text_block(d, x, y, text, fnt, max_w, fill, leading, max_lines=None):
    """Draw wrapped text starting at (x, y); return the y just below it."""
    rows = wrap(d, text, fnt, max_w)
    if max_lines:
        rows = rows[:max_lines]
    cursor = y
    for row in rows:
        d.text((x, cursor), row, font=fnt, fill=fill)
        cursor += leading
    return cursor


def badge(d, x, y, num, color):
    """Draw a numbered disc at (x, y); return the x just past it."""
    radius = 8
    d.ellipse([x, y, x + 2 * radius, y + 2 * radius], fill=color,
              outline=BG)
    label = str(num)
    label_w = d.textlength(label, font=F_NUM)
    d.text((x + radius - label_w / 2, y + 2.5), label, font=F_NUM,
           fill=(10, 10, 10))
    return x + 2 * radius + 4


def chip(d, x, y, text):
    """Yellow-outlined stat chip; return the x just past it."""
    pad = 8
    tw = d.textlength(text, font=F_CHIP)
    box = [x, y, x + tw + 2 * pad, y + 18]
    d.rounded_rectangle(box, radius=4, outline=YELLOW, width=1)
    d.text((x + pad, y + 3), text, font=F_CHIP, fill=YELLOW)
    return box[2] + 8


def _sky(d, x, y, w, h, top, bot):
    """Vertical gradient: one horizontal line per row, top to bottom."""
    span = max(1, h - 1)
    for row in range(h):
        blend = row / span
        shade = tuple(
            int(top[c] + (bot[c] - top[c]) * blend) for c in range(3)
        )
        d.line([(x, y + row), (x + w, y + row)], fill=shade)


def _burst(d, cx, cy, r, color=(255, 140, 0), core=(255, 230, 120)):
    """Starburst: 16 alternating long/short spikes around a bright core."""
    def spike(index):
        angle = math.pi * index / 8
        reach = r if index % 2 == 0 else r * 0.45
        return (cx + reach * math.cos(angle),
                cy + reach * 0.8 * math.sin(angle))

    star = [spike(i) for i in range(16)]
    d.polygon(star, fill=color)
    d.ellipse([cx - r * 0.35, cy - r * 0.3, cx + r * 0.35, cy + r * 0.3],
              fill=core)


def _smoke(d, cx, cy, s, color=(120, 120, 120)):
    """Cluster of four overlapping puffs, scaled by s."""
    puffs = ((0, 0, 9), (8, -6, 7), (-8, -5, 6), (3, -12, 6))
    for off_x, off_y, puff_r in puffs:
        px = cx + off_x * s
        py = cy + off_y * s
        spread = puff_r * s
        d.ellipse([px - spread, py - spread, px + spread, py + spread],
                  fill=color)


def _star5(d, cx, cy, r, fill, outline=None):
    """Five-pointed star centred on (cx, cy)."""
    pts = []
    for i in range(10):
        ang = math.pi * i / 5 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=outline)


def _hstripes(d, x, y, w, h, colors):
    """Horizontal flag stripes across [x, y, x+w, y+h]."""
    band = h / len(colors)
    for i, col in enumerate(colors):
        d.rectangle([x, y + i * band, x + w, y + (i + 1) * band], fill=col)


def _vstripes(d, x, y, w, h, colors):
    """Vertical flag stripes across [x, y, x+w, y+h]."""
    band = w / len(colors)
    for i, col in enumerate(colors):
        d.rectangle([x + i * band, y, x + (i + 1) * band, y + h], fill=col)


# ------------------------------------------------------------- drawings
# Every illustration stays strictly inside its own [x, y, x+w, y+h] box:
# nothing may paint over the card above it. Medium strips are 243x30;
# the lead illustration is about 196x142. All drawings are original.

def ill_cop31(d, x, y, w, h):
    """Cracked globe over Antalya, and the five flags that said no."""
    _sky(d, x, y, w, h, (12, 24, 48), (30, 55, 95))
    cx, cy, r = x + w // 2, y + 52, 42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(45, 110, 180),
              outline=(150, 200, 240), width=2)
    d.ellipse([cx - 26, cy - 26, cx - 4, cy - 8], fill=(110, 190, 110))
    d.ellipse([cx + 2, cy + 2, cx + 26, cy + 24], fill=(110, 190, 110))
    d.ellipse([cx - 30, cy + 10, cx - 14, cy + 26], fill=(110, 190, 110))
    # the crack through the globe
    d.line([(cx - 30, cy - 28), (cx - 12, cy - 10), (cx - 22, cy + 6),
            (cx - 2, cy + 22), (cx + 10, cy + 38)], fill=(8, 12, 26),
           width=3)
    d.line([(cx - 12, cy - 10), (cx + 2, cy - 16)], fill=(8, 12, 26),
           width=2)
    lab = "THE FIVE WHO SAID NO"
    lw = d.textlength(lab, font=F_ILL)
    d.text((x + (w - lw) / 2, y + 100), lab, font=F_ILL, fill=YELLOW)
    # five flags, 34x20 each: EU, UK, Panama, Marshall Islands, Norway
    fy = y + 114
    fx = x + (w - (5 * 34 + 4 * 3)) // 2
    d.rectangle([fx, fy, fx + 34, fy + 20], fill=(0, 51, 153))
    for i in range(12):
        ang = math.pi * i / 6
        d.ellipse([fx + 17 + 7 * math.cos(ang) - 1,
                   fy + 10 + 7 * math.sin(ang) - 1,
                   fx + 17 + 7 * math.cos(ang) + 1,
                   fy + 10 + 7 * math.sin(ang) + 1], fill=(255, 204, 0))
    ux = fx + 37
    d.rectangle([ux, fy, ux + 34, fy + 20], fill=(0, 36, 125))
    d.line([(ux, fy), (ux + 34, fy + 20)], fill=(255, 255, 255), width=4)
    d.line([(ux + 34, fy), (ux, fy + 20)], fill=(255, 255, 255), width=4)
    d.line([(ux, fy), (ux + 34, fy + 20)], fill=(207, 0, 15), width=2)
    d.line([(ux + 34, fy), (ux, fy + 20)], fill=(207, 0, 15), width=2)
    d.rectangle([ux + 14, fy, ux + 20, fy + 20], fill=(255, 255, 255))
    d.rectangle([ux, fy + 7, ux + 34, fy + 13], fill=(255, 255, 255))
    d.rectangle([ux + 15, fy, ux + 19, fy + 20], fill=(207, 0, 15))
    d.rectangle([ux, fy + 8, ux + 34, fy + 12], fill=(207, 0, 15))
    px = fx + 74
    d.rectangle([px, fy, px + 17, fy + 10], fill=(255, 255, 255))
    d.rectangle([px + 17, fy, px + 34, fy + 10], fill=(210, 16, 52))
    d.rectangle([px, fy + 10, px + 17, fy + 20], fill=(0, 84, 159))
    d.rectangle([px + 17, fy + 10, px + 34, fy + 20], fill=(255, 255, 255))
    _star5(d, px + 8, fy + 5, 3, (0, 84, 159))
    _star5(d, px + 26, fy + 15, 3, (210, 16, 52))
    mx = fx + 111
    d.rectangle([mx, fy, mx + 34, fy + 20], fill=(0, 56, 147))
    d.polygon([(mx, fy + 20), (mx + 10, fy + 20), (mx + 34, fy + 2),
               (mx + 34, fy + 8)], fill=(255, 255, 255))
    d.polygon([(mx, fy + 20), (mx + 5, fy + 20), (mx + 34, fy + 5),
               (mx + 34, fy + 8)], fill=(255, 120, 0))
    _star5(d, mx + 7, fy + 5, 3, (255, 255, 255))
    nx = fx + 148
    d.rectangle([nx, fy, nx + 34, fy + 20], fill=(186, 12, 47))
    d.rectangle([nx + 8, fy, nx + 16, fy + 20], fill=(255, 255, 255))
    d.rectangle([nx, fy + 6, nx + 34, fy + 14], fill=(255, 255, 255))
    d.rectangle([nx + 10, fy, nx + 14, fy + 20], fill=(0, 32, 91))
    d.rectangle([nx, fy + 8, nx + 34, fy + 12], fill=(0, 32, 91))
    for bx in (fx, ux, px, mx, nx):
        d.rectangle([bx, fy, bx + 34, fy + 20], outline=(200, 210, 230))


def ill_eisenkot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 52))
    # Israel flag, left
    d.rectangle([x + 8, y + 5, x + 66, y + 25], fill=(255, 255, 255))
    d.rectangle([x + 8, y + 5, x + 66, y + 9], fill=(0, 56, 184))
    d.rectangle([x + 8, y + 21, x + 66, y + 25], fill=(0, 56, 184))
    d.polygon([(x + 37, y + 10), (x + 32, y + 19), (x + 42, y + 19)],
              outline=(0, 56, 184))
    d.polygon([(x + 37, y + 20), (x + 32, y + 11), (x + 42, y + 11)],
              outline=(0, 56, 184))
    d.text((x + 74, y + 10), "EISENKOT", font=F_ILL, fill=(255, 255, 255))
    # Knesset dome, right
    d.pieslice([x + 168, y + 4, x + 228, y + 30], start=180, end=360,
               fill=(140, 150, 165))
    d.rectangle([x + 168, y + 17, x + 228, y + 26], fill=(140, 150, 165))


def ill_gaza_aid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 196, 150))
    # four mini flags: Australia, Canada, Italy, UK
    ax = x + 8
    d.rectangle([ax, y + 3, ax + 26, y + 15], fill=(0, 36, 125))
    for dx, dy in [(4, 3), (18, 8), (10, 9), (20, 3)]:
        d.ellipse([ax + dx, y + dy, ax + dx + 2, y + dy + 2],
                  fill=(255, 255, 255))
    cx = x + 38
    _vstripes(d, cx, y + 3, 26, 12, [(210, 16, 52), (255, 255, 255),
                                     (210, 16, 52)])
    d.rectangle([cx + 10, y + 5, cx + 16, y + 11], fill=(210, 16, 52))
    ix = x + 68
    _vstripes(d, ix, y + 3, 26, 12, [(0, 140, 70), (255, 255, 255),
                                     (205, 33, 42)])
    kx = x + 98
    d.rectangle([kx, y + 3, kx + 26, y + 15], fill=(0, 36, 125))
    d.line([(kx, y + 3), (kx + 26, y + 15)], fill=(255, 255, 255), width=3)
    d.line([(kx + 26, y + 3), (kx, y + 15)], fill=(255, 255, 255), width=3)
    d.rectangle([kx + 11, y + 3, kx + 15, y + 15], fill=(255, 255, 255))
    d.rectangle([kx, y + 7, kx + 26, y + 11], fill=(255, 255, 255))
    d.text((x + 8, y + 18), "150,000 TENTS", font=F_ILL, fill=(120, 40, 30))
    # tents, right
    d.polygon([(x + 150, y + 27), (x + 172, y + 10), (x + 194, y + 27)],
              fill=(180, 80, 60))
    d.polygon([(x + 200, y + 27), (x + 219, y + 12), (x + 238, y + 27)],
              fill=(230, 230, 225))


def ill_diplomacy(d, x, y, w, h):
    _sky(d, x, y, w, h, (40, 70, 120), (140, 180, 220))
    # dashed route arc under the plane
    for i in range(11):
        t = i / 10
        px = x + 20 + t * (w - 40)
        py = y + 26 - 10 * math.sin(math.pi * t)
        d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))
    # plane silhouette
    cx, cy = x + w // 2, y + 12
    d.ellipse([cx - 34, cy - 4, cx + 34, cy + 4], fill=(240, 240, 240))
    d.polygon([(cx - 6, cy), (cx + 6, cy - 2), (cx + 22, cy - 12),
               (cx + 14, cy - 12)], fill=(220, 220, 220))
    d.polygon([(cx + 26, cy - 2), (cx + 34, cy - 8), (cx + 30, cy - 2)],
              fill=(200, 200, 200))
    d.text((x + 6, y + 18), "MOSCOW \u2192 DUBLIN", font=F_ILL,
           fill=(255, 255, 255))


def ill_cartel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 30, 40))
    _star5(d, x + 30, y + 15, 11, (220, 180, 60), outline=(255, 230, 140))
    d.ellipse([x + 24, y + 9, x + 36, y + 21], fill=(28, 30, 40))
    d.text((x + 27, y + 9), "$", font=F_MED_H, fill=(220, 180, 60))
    d.text((x + 48, y + 4), "FBI TOP 10", font=F_ILL, fill=(255, 210, 90))
    d.text((x + 48, y + 17), "CAPTURED IN SINALOA", font=F_ILL,
           fill=(255, 255, 255))


def ill_aukus(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 80, 110), (90, 150, 190))
    d.text((x + 6, y + 4), "VIRGINIA CLASS", font=F_ILL,
           fill=(255, 255, 255))
    d.rounded_rectangle([x + 60, y + 13, x + 190, y + 24], radius=5,
                        fill=(40, 48, 60))
    d.rectangle([x + 110, y + 7, x + 140, y + 13], fill=(40, 48, 60))
    d.line([(x + 132, y + 7), (x + 132, y + 3)], fill=(40, 48, 60), width=2)
    d.line([(x + 60, y + 25), (x + 190, y + 25)], fill=(200, 220, 235),
           width=1)


def ill_hormuz(d, x, y, w, h):
    _sky(d, x, y, w, h, (168, 205, 220), (222, 235, 240))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(64, 130, 158))
    d.polygon([(x, y + h - 8), (x + 50, y + h - 12), (x + 110, y + h - 8),
               (x + 80, y + h - 3), (x, y + h - 2)], fill=(214, 196, 150))
    d.polygon([(x + w, y + h - 8), (x + w - 50, y + h - 12),
               (x + w - 110, y + h - 8), (x + w - 80, y + h - 3),
               (x + w, y + h - 2)], fill=(214, 196, 150))
    d.rectangle([x + 95, y + 16, x + 148, y + 23], fill=(150, 40, 40))
    d.rectangle([x + 132, y + 10, x + 142, y + 16], fill=(230, 230, 230))
    _burst(d, x + 110, y + 12, 5)
    d.text((x + 6, y + 4), "2 DAYS", font=F_ILL, fill=(20, 60, 80))


def ill_ukraine_power(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 18, 32))
    d.text((x + 6, y + 4), "KYIV: 3 PLANTS DOWN", font=F_ILL,
           fill=(255, 210, 90))
    for bx, bw, bh in [(10, 26, 14), (44, 18, 18), (70, 30, 12),
                       (108, 22, 16)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(48, 58, 85))
    d.rectangle([x + 16, y + h - 10, x + 20, y + h - 6],
                fill=(255, 210, 90))
    d.rectangle([x + 76, y + h - 8, x + 80, y + h - 4],
                fill=(255, 210, 90))
    # leaning pylon, right, with a sagging line
    d.line([(x + 196, y + h), (x + 186, y + 6)], fill=(140, 150, 165),
           width=2)
    d.line([(x + 212, y + h), (x + 196, y + 6)], fill=(140, 150, 165),
           width=2)
    d.line([(x + 186, y + 6), (x + 130, y + 12)], fill=(140, 150, 165),
           width=1)
    d.line([(x + 186, y + 6), (x + 158, y + 18)], fill=(140, 150, 165),
           width=1)


def ill_japan(d, x, y, w, h):
    _sky(d, x, y, w, h, (180, 200, 220), (210, 222, 232))
    d.rectangle([x, y + h - 7, x + w, y + h], fill=(40, 90, 130))
    d.polygon([(x + 60, y + 18), (x + 180, y + 18), (x + 170, y + 26),
               (x + 70, y + 26)], fill=(120, 130, 140))
    d.rectangle([x + 140, y + 10, x + 158, y + 18], fill=(120, 130, 140))
    d.line([(x + 150, y + 10), (x + 150, y + 4)], fill=(90, 100, 110),
           width=2)
    d.line([(x + 215, y + 6), (x + 215, y + 20)], fill=(200, 40, 40),
           width=3)
    d.polygon([(x + 215, y + 24), (x + 209, y + 16), (x + 221, y + 16)],
              fill=(200, 40, 40))
    d.text((x + 6, y + 4), "CUTS", font=F_ILL, fill=(180, 30, 30))


def ill_fire(d, x, y, w, h):
    _sky(d, x, y, w, h, (255, 140, 40), (255, 200, 80))
    d.rectangle([x + 30, y + 12, x + 150, y + 28], fill=(50, 45, 45))
    d.rectangle([x + 150, y + 4, x + 162, y + 28], fill=(50, 45, 45))
    for fx in (44, 70, 96, 122):
        d.polygon([(x + fx, y + 12), (x + fx + 6, y + 4),
                   (x + fx + 12, y + 12)], fill=(255, 230, 120))
    _burst(d, x + 156, y + 4, 4, color=(255, 120, 30))
    d.rectangle([x + 168, y + 16, x + 238, y + 28], fill=(50, 45, 45))
    d.text((x + 174, y + 19), "CIKANDE", font=F_ILL, fill=(255, 255, 255))


def ill_prabowo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h // 2], fill=(200, 30, 40))
    d.rectangle([x, y + h // 2, x + w, y + h], fill=(245, 245, 245))
    d.text((x + 8, y + 3), "VP NAMES", font=F_ILL, fill=(255, 255, 255))
    d.text((x + 8, y + 16), "25 NOV", font=F_ILL, fill=(180, 30, 40))
    d.rectangle([x + 100, y + 10, x + 145, y + 26], fill=(60, 90, 150))
    d.rectangle([x + 106, y + 6, x + 139, y + 10], fill=(60, 90, 150))
    d.rectangle([x + 116, y + 4, x + 128, y + 7], fill=(255, 255, 255))
    d.line([(x + 110, y + 20), (x + 118, y + 24), (x + 136, y + 13)],
           fill=(255, 255, 255), width=2)
    d.text((x + 158, y + 17), "MPR", font=F_ILL, fill=(180, 30, 40))


def ill_mahfud(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 36, 48))
    d.polygon([(x + 30, y + 6), (x + 72, y + 12), (x + 68, y + 19),
               (x + 26, y + 13)], fill=(180, 140, 90))
    d.line([(x + 48, y + 16), (x + 36, y + 27)], fill=(150, 110, 70),
           width=3)
    d.rectangle([x + 18, y + 26, x + 66, y + 29], fill=(120, 90, 60))
    for ox, oy in [(78, 4), (82, 12), (76, 20)]:
        d.line([(x + 74, y + 12), (x + ox, y + oy)], fill=(255, 220, 130),
               width=1)
    d.text((x + 96, y + 10), "MPR \u00b7 14 DAYS", font=F_ILL,
           fill=(255, 255, 255))


def ill_btc(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 36))
    for gy in (y + 8, y + 16):
        d.line([(x + 6, gy), (x + w - 6, gy)], fill=(52, 58, 70))
    d.line([(x + 10, y + 4), (x + 60, y + 10), (x + 110, y + 18)],
           fill=(230, 60, 60), width=3, joint="curve")
    d.line([(x + 110, y + 18), (x + 160, y + 12), (x + 200, y + 8),
            (x + 233, y + 5)], fill=(80, 220, 120), width=3, joint="curve")
    d.text((x + 6, y + 19), "BTC $60K", font=F_ILL, fill=(255, 220, 80))
    d.text((x + 164, y + 19), "$55.3K LOW", font=F_ILL,
           fill=(255, 120, 120))


def ill_ump(d, x, y, w, h):
    _sky(d, x, y, w, h, (20, 30, 60), (60, 80, 120))
    for bx, bw, bh in [(10, 22, 12), (36, 18, 16), (60, 24, 10),
                       (128, 20, 14), (152, 26, 11), (182, 22, 15),
                       (208, 24, 9)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(48, 66, 100))
    d.rectangle([x + 100, y + 4, x + 112, y + 28], fill=(210, 210, 220))
    d.ellipse([x + 100, y + 1, x + 112, y + 9], fill=(255, 210, 90))
    d.rectangle([x + 96, y + 26, x + 116, y + 29], fill=(255, 210, 90))
    d.text((x + 130, y + 3), "Rp6.13 JT", font=F_ILL, fill=(255, 230, 0))


def ill_dsi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 210, 220))
    for j, col in enumerate([(200, 60, 50), (60, 120, 200), (60, 180, 80)]):
        d.rectangle([x + 10 + j * 28, y + 14, x + 36 + j * 28, y + 26],
                    fill=col)
    d.rectangle([x + 24, y + 4, x + 50, y + 14], fill=(220, 170, 50))
    d.polygon([(x + 130, y + 18), (x + 230, y + 18), (x + 220, y + 27),
               (x + 140, y + 27)], fill=(50, 60, 75))
    d.rectangle([x + 150, y + 10, x + 176, y + 18], fill=(200, 60, 50))
    d.rectangle([x + 178, y + 10, x + 204, y + 18], fill=(60, 120, 200))
    d.text((x + 150, y + 1), "DSI 2027", font=F_ILL, fill=(30, 50, 80))


def ill_pppk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 110, 70))
    d.rectangle([x, y, x + w, y + h], outline=(25, 70, 45), width=2)
    d.text((x + 10, y + 4), "242,482", font=F_MED_H, fill=(255, 255, 255))
    d.text((x + 10, y + 19), "GURU JADI PENUH WAKTU", font=F_ILL,
           fill=(220, 245, 225))
    d.rectangle([x + 160, y + 22, x + 230, y + 26], fill=(180, 160, 120))
    d.rectangle([x + 170, y + 18, x + 186, y + 22], fill=(255, 255, 255))
    d.rectangle([x + 192, y + 18, x + 208, y + 22], fill=(255, 230, 120))


def ill_umk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 225, 210))
    d.rectangle([x + 10, y + 12, x + 110, y + 28], fill=(90, 100, 115))
    d.polygon([(x + 10, y + 12), (x + 35, y + 4), (x + 60, y + 12),
               (x + 85, y + 4), (x + 110, y + 12)], fill=(90, 100, 115))
    d.rectangle([x + 112, y + 4, x + 122, y + 28], fill=(90, 100, 115))
    d.ellipse([x + 196, y + 7, x + 214, y + 25], outline=(180, 60, 40),
              width=3)
    for ang in range(0, 360, 60):
        r = math.radians(ang)
        d.line([(x + 205, y + 16),
                (x + 205 + 8 * math.cos(r), y + 16 + 8 * math.sin(r))],
               fill=(180, 60, 40), width=2)
    d.text((x + 130, y + 2), "Rp6.48 JT", font=F_ILL, fill=(150, 40, 40))


# --------------------------------------------------- sport band icons
def icon_f1(d, x, y):
    """Checkered flag, 16x12."""
    for r in range(3):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle([x + c * 4, y + r * 4, x + c * 4 + 4,
                             y + r * 4 + 4], fill=(255, 255, 255))
            else:
                d.rectangle([x + c * 4, y + r * 4, x + c * 4 + 4,
                             y + r * 4 + 4], fill=(20, 20, 20))


def icon_ball(d, x, y):
    """Football, 16x16."""
    d.ellipse([x, y, x + 16, y + 16], fill=(255, 255, 255),
              outline=(30, 30, 30))
    for dx, dy in [(7, 4), (3, 9), (11, 10)]:
        d.ellipse([x + dx, y + dy, x + dx + 3, y + dy + 3],
                  fill=(30, 30, 30))


def icon_basket(d, x, y):
    """Basketball, 16x16."""
    d.ellipse([x, y, x + 16, y + 16], fill=(230, 120, 40),
              outline=(160, 70, 20))
    d.line([(x, y + 8), (x + 16, y + 8)], fill=(160, 70, 20), width=1)
    d.line([(x + 8, y), (x + 8, y + 16)], fill=(160, 70, 20), width=1)
    d.arc([x, y, x + 16, y + 16], start=300, end=60, fill=(160, 70, 20),
          width=1)


def icon_trophy(d, x, y):
    """Gold cup, 16x16."""
    d.polygon([(x + 2, y), (x + 14, y), (x + 12, y + 8), (x + 4, y + 8)],
              fill=(255, 210, 60))
    d.arc([x - 2, y, x + 6, y + 8], start=90, end=270,
          fill=(255, 210, 60), width=2)
    d.arc([x + 10, y, x + 18, y + 8], start=270, end=90,
          fill=(255, 210, 60), width=2)
    d.rectangle([x + 7, y + 8, x + 9, y + 12], fill=(255, 210, 60))
    d.rectangle([x + 4, y + 12, x + 12, y + 15], fill=(255, 210, 60))


# ---------------------------------------------------------------- stories
# Every story happened or was first reported on Sunday 22 November 2026.
# Figures trace to the research file (Reuters, BBC, AP, Formula 1, Sky
# Sports, industry.co.id, CNBC Indonesia, Nexus Europa, The Paris Eye).
# Traps avoided: COP31 is NO DEAL (not "close to a deal"); F1 is the
# 2026 result (Verstappen, Norris +0.639, Piastri +1.529 -- NOT the 2025
# disqualifications); Cikande uses Reuters numbers (36 missing, 3 dead).

LEAD = dict(
    num=1, region="CLIMATE", beat="COP31 \u00b7 ANTALYA",
    head="COP31 COLLAPSES \u2014 NO DEAL",
    body=("The longest climate summit in history ends with no deal \u2014 "
          "the first COP to fail since Copenhagen 2009. President Kurum: "
          "\u201cthere is no agreement on this text.\u201d The final text "
          "never mentions fossil fuels; the EU, UK, Panama, Marshall "
          "Islands and Norway refuse to back it."),
    chips=["44+ HOURS OVERTIME", "FIRST NO-DEAL COP SINCE 2009",
           "NEXT: COP32 \u00b7 ADDIS ABABA \u00b7 NOV 2027"],
    ill=ill_cop31,
)

# Two more climate/environment stories riding in the lead block.
CLIMATE_EXTRA = [
    dict(num=2, region="INDONESIA", beat="ENVIRONMENT",
         text="RAPP loses 338,536-ha permit in Riau over environmental "
              "breaches"),
    dict(num=3, region="MIDDLE EAST", beat="WEATHER",
         text="Winter storm floods Gaza shelters; 1m+ displaced face cold "
              "and disease"),
]

# Block 2: politics & global diplomacy (medium cards, illustrated).
POLITICS = [
    dict(num=4, region="MIDDLE EAST", beat="POLITICS",
         head="Eisenkot tapped to form Israel\u2019s government",
         body="Herzog passes over Netanyahu; Eisenkot invites Likud to "
              "coalition talks.",
         ill=ill_eisenkot),
    dict(num=5, region="MIDDLE EAST", beat="DIPLOMACY",
         head="Four nations demand Gaza aid access",
         body="Australia, Canada, Italy, UK urge open access; 150,000 "
              "tents stuck at the border.",
         ill=ill_gaza_aid),
    dict(num=6, region="GLOBAL", beat="DIPLOMACY",
         head="US envoys head to Moscow, then Dublin",
         body="Kushner and Witkoff carry Abu Dhabi talks to Putin, then "
              "Zelensky.",
         ill=ill_diplomacy),
    dict(num=7, region="AMERICAS", beat="CRIME",
         head="\u201cEl Chapo Isidro\u201d captured; 11 killed",
         body="Fausto Isidro Meza Flores seized after a shootout in "
              "Guasave, Sinaloa.",
         ill=ill_cartel),
    dict(num=8, region="OCEANIA", beat="DEFENCE",
         head="Australia slams US budget office over AUKUS",
         body="Marles calls the CBO \u201cwrong\u201d on Virginia-class "
              "sales shrinking the US fleet.",
         ill=ill_aukus),
    dict(num=9, region="MIDDLE EAST", beat="ENERGY",
         head="Iran shortens Hormuz reopening plan to two days",
         body="Tehran cuts the timeline amid the tanker war and the US "
              "blockade.",
         ill=ill_hormuz),
    dict(num=10, region="EUROPE", beat="WAR",
         head="Ukraine\u2019s energy crisis deepens before winter",
         body="Strikes knock out heat and power; Kyiv loses all three "
              "heating plants.",
         ill=ill_ukraine_power),
    dict(num=11, region="ASIA", beat="DEFENCE",
         head="Japan weighs cutting missile and warship buys",
         body="Nikkei: Tokyo reviews its security build-up under budget "
              "pressure.",
         ill=ill_japan),
]

# Block 3: Indonesia + economy (medium cards, illustrated).
INDONESIA = [
    dict(num=12, region="INDONESIA", beat="DISASTER",
         head="Factory fire in Cikande: 36 missing, 3 dead",
         body="Rescuers search the Milkita candy plant in Banten; 4 hurt, "
              "15 survived.",
         ill=ill_fire),
    dict(num=13, region="INDONESIA", beat="POLITICS",
         head="Prabowo to name two VP candidates on 25 Nov",
         body="Two names go to the MPR; election and inauguration set for "
              "9 December.",
         ill=ill_prabowo),
    dict(num=14, region="INDONESIA", beat="POLITICS",
         head="Mahfud: recount the MPR session to replace Gibran",
         body="Mahfud MD: count 14 working days from the President\u2019s "
              "submission.",
         ill=ill_mahfud),
    dict(num=15, region="GLOBAL", beat="MARKETS",
         head="Bitcoin climbs back above $60,000",
         body="After plunging to $55,300, its lowest since September "
              "2024, BTC retakes $60,000.",
         ill=ill_btc),
    dict(num=16, region="INDONESIA", beat="ECONOMY",
         head="Jakarta\u2019s 2027 minimum wage hits Rp6.13m",
         body="Up 7.1% \u2014 the highest provincial wage in Indonesia.",
         ill=ill_ump),
    dict(num=17, region="INDONESIA", beat="TRADE",
         head="Coal, CPO, ferroalloy exports to run via DSI",
         body="From 1 January 2027, three strategic exports must go via "
              "Danantara\u2019s DSI.",
         ill=ill_dsi),
    dict(num=18, region="INDONESIA", beat="EDUCATION",
         head="242,482 part-time teachers go full-time in 2027",
         body="PPPK teachers convert without a test from 1 January.",
         ill=ill_pppk),
    dict(num=19, region="INDONESIA", beat="ECONOMY",
         head="Bekasi\u2019s 2027 wage Rp6.48m, highest in Indonesia",
         body="City UMK Rp6,480,058, up 8.01%; regency Rp6,427,655. Both "
              "await confirmation.",
         ill=ill_umk),
]

# Block 4: sport (score-band cards, no illustration strip).
SPORTS = [
    dict(num=20, region="SPORT", beat="F1 \u00b7 LAS VEGAS GP",
         score="VERSTAPPEN WINS",
         body="From pole in 1:27:39.624; Norris +0.639, Piastri +1.529. "
              "35 lead changes; Russell hits the wall on lap 48.",
         icon=icon_f1),
    dict(num=21, region="SPORT", beat="PREMIER LEAGUE",
         score="LIV 4\u20130 MAN UTD",
         body="Szoboszlai 10\u2019, Wirtz 13\u2019, Ngumoha 66\u2019, Munoz "
              "82\u2019. Yoro sent off at 8\u2019. Pochettino\u2019s first "
              "game.",
         icon=icon_ball),
    dict(num=22, region="SPORT", beat="PREMIER LEAGUE",
         score="HULL 2\u20130 BRIGHTON",
         body="McBurnie scores twice in injury time (90+2\u2019, "
              "90+5\u2019). Costinha sent off at 89\u2019.",
         icon=icon_ball),
    dict(num=23, region="SPORT", beat="NWSL FINAL",
         score="KC WIN NWSL TITLE",
         body="First title, 2\u20131 over Washington Spirit. "
              "DiBernardo\u2019s corner (54\u2019), Debinha in injury "
              "time; Rodman replies at 98\u2019.",
         icon=icon_trophy),
    dict(num=24, region="SPORT", beat="NBA",
         score="SPURS CRUISE 114\u201391",
         body="Pelicans beaten at home. San Antonio cruise in the "
              "regular season.",
         icon=icon_basket),
]

# (num, place, text, region) -- one line each, no sub-line.
ALSO = [
    (25, "Berlin", "Germany plans a new national fare for occasional "
     "transit users", "EUROPE"),
    (26, "Berlin", "Health minister: insurance contributions stable "
     "through 2027", "EUROPE"),
    (27, "Kyiv", "Zelensky faults lack of US intel warning before "
     "Russian strikes", "EUROPE"),
    (28, "Washington", "House revises college sports bill to allow "
     "22-team leagues", "AMERICAS"),
    (29, "Rome", "Italy budget bill lifts flat tax cap to \u20ac100,000",
     "EUROPE"),
    (30, "Stuttgart", "Bosch deepens AI partnership with Microsoft",
     "EUROPE"),
    (31, "Wolfsburg", "Volkswagen plans to freeze pay rises in cost "
     "push", "EUROPE"),
    (32, "Frankfurt", "Lufthansa to cut 1,000 jobs as fuel costs bite",
     "EUROPE"),
    (33, "Jakarta", "BMKG: rain possible in 38 regions today",
     "INDONESIA"),
    (34, "Jakarta", "OJK sanctions 10 stock-trading cases; Rp23.77bn "
     "illegal gains to be returned", "INDONESIA"),
    (35, "Jakarta", "New rail timetable from 1 Dec: 79 trains from "
     "Gambir and Pasarsenen", "INDONESIA"),
    (36, "Jakarta", "Madrasah exams start 23 Nov; semester break from "
     "21 Dec", "INDONESIA"),
    (37, "Jakarta", "Vehicle tax amnesty still open in 7 provinces "
     "into December", "INDONESIA"),
    (38, "Tangerang", "IMOS day 2: Honda shows new Super Cub C125, "
     "Vario Evo, ADV 160", "INDONESIA"),
    (39, "Mercury", "BepiColombo\u2019s MIXS X-ray telescope sends first "
     "cosmic views", "GLOBAL"),
    (40, "Orbit", "China\u2019s broadband constellations left 52 rocket "
     "bodies in low orbit", "GLOBAL"),
    (41, "Gaming", "GTA 6: critics score it 99, users just 5.6 \u2014 "
     "review bombing suspected", "GLOBAL"),
    (42, "Lagos", "Young Nigerians register to vote in lower numbers "
     "than in 2023", "AFRICA"),
    (43, "USA", "Teen gamer and his mother help the FBI rescue a "
     "missing girl", "AMERICAS"),
    (44, "London", "Princess of Wales fronts papers ahead of her new "
     "documentary", "EUROPE"),
    (45, "London", "Parents urged to spot the warning signs of online "
     "stalking", "EUROPE"),
    (46, "London", "Service stations transform from pit stops into "
     "destinations", "EUROPE"),
    (47, "London", "Employers urged to give interview feedback to "
     "every applicant", "EUROPE"),
    (48, "London", "Nicola Coughlan\u2019s new drama \u201cI Am Helen\u201d "
     "divides critics", "EUROPE"),
]

DATE_CHECK = ("DATE CHECK \u2014 left out on purpose, they broke before "
              "today: Wall Street\u2019s crash, Anthropic\u2019s IPO, the "
              "Bayer Roundup deal, the Riemann proof claim, the UK\u2013EU "
              "reset (all 20 Nov); the 2025 Las Vegas GP result "
              "(Nov 2025).")
FOOTER_L1 = ("Every story here happened or was first reported on Sunday "
             "22 November 2026.")
FOOTER_L2 = ("Sources: Reuters, BBC, AP, Formula 1, Sky Sports, "
             "industry.co.id, CNBC Indonesia, Nexus Europa, The Paris "
             "Eye \u00b7 Original drawings.")


# ------------------------------------------------------------------ layout
# Vertical plan (1024 tall, all sections measured, nothing overflows):
#   top bar 7 / rule 25 / masthead 28 / yellow rule 87
#   lead panel 92..260 / block 2 header 266, cards 284..492
#   block 3 header 498, cards 516..724 / sport header 730, row 748..826
#   also header 832, list 850..976 / footer 982..1013
MED_W = (CW - 3 * 8) // 4          # 243
MED_H = 102
SPORT_W = (CW - 4 * 9) // 5        # 192
SPORT_H = 78
LEAD_Y0, LEAD_Y1 = 92, 260
ILL_X, ILL_Y, ILL_W, ILL_H = 806, 100, 196, 152


def draw_top(d):
    d.text((MX, 7), "ONE DAY OF WORLD NEWS \u00b7 ONE PICTURE", font=F_TOP,
           fill=YELLOW)
    r = "48 STORIES \u00b7 10 REGIONS \u00b7 ALL FROM THIS SUNDAY"
    d.text((W - MX - d.textlength(r, font=F_TOP_R), 7), r, font=F_TOP_R,
           fill=MUTED)
    d.line([(MX, 25), (W - MX, 25)], fill=RULE, width=1)


def draw_masthead(d):
    t = "Sunday, 22 November 2026"
    tw = d.textlength(t, font=F_MAST)
    d.text(((W - tw) / 2, 28), t, font=F_MAST, fill=WHITE)
    d.line([(MX, 87), (W - MX, 87)], fill=YELLOW, width=2)


def draw_lead(d):
    d.rectangle([MX, LEAD_Y0, W - MX, LEAD_Y1], fill=PANEL, outline=RULE,
                width=1)
    d.rectangle([MX, LEAD_Y0, MX + 6, LEAD_Y1], fill=YELLOW)
    # illustration, right
    LEAD["ill"](d, ILL_X, ILL_Y, ILL_W, ILL_H)
    d.rectangle([ILL_X, ILL_Y, ILL_X + ILL_W, ILL_Y + ILL_H], outline=RULE,
                width=1)
    tag = "%02d \u00b7 %s \u00b7 %s" % (LEAD["num"], LEAD["region"],
                                       LEAD["beat"])
    d.text((30, 100), tag, font=F_TAG, fill=YELLOW)
    d.text((30, 118), LEAD["head"], font=F_LEAD_H, fill=YELLOW)
    text_block(d, 30, 162, LEAD["body"], F_LEAD_B, 752, WHITE, 15,
               max_lines=3)
    cx = 30
    for c in LEAD["chips"]:
        cx = chip(d, cx, 212, c)
    d.line([(30, 236), (790, 236)], fill=RULE, width=1)
    # the two extra climate stories, one line each, side by side
    halves = [(30, 470), (510, 480)]
    for s, (hx, hw) in zip(CLIMATE_EXTRA, halves):
        col = REGION_COLORS[s["region"]]
        pre = "%02d \u00b7 " % s["num"]
        d.text((hx, 241), pre, font=F_ALSO_B, fill=col)
        tx = hx + d.textlength(pre, font=F_ALSO_B)
        d.text((tx, 241), s["text"], font=F_ALSO, fill=WHITE)


def draw_block_header(d, y, title, span):
    d.rectangle([MX, y + 1, MX + 10, y + 11], fill=YELLOW)
    d.text((MX + 16, y), title, font=F_SEC, fill=YELLOW)
    d.text((W - MX - d.textlength(span, font=F_TOP_R), y + 1), span,
           font=F_TOP_R, fill=MUTED)


def draw_medium(d, s, x, y):
    col = REGION_COLORS[s["region"]]
    d.rectangle([x, y, x + MED_W, y + MED_H], fill=CARD, outline=RULE,
                width=1)
    s["ill"](d, x + 1, y + 1, MED_W - 2, 30)
    d.rectangle([x, y, x + MED_W, y + 31], outline=RULE, width=1)
    badge(d, x + 4, y + 34, s["num"], col)
    tag = "%s \u00b7 %s" % (s["region"], s["beat"])
    d.text((x + 24, y + 36), tag, font=F_TAG, fill=col)
    text_block(d, x + 4, y + 50, s["head"], F_MED_H, MED_W - 8, WHITE,
               14, max_lines=2)
    text_block(d, x + 4, y + 79, s["body"], F_MED_B, MED_W - 8, MUTED,
               11, max_lines=2)


def draw_sport(d, s, x, y):
    col = REGION_COLORS[s["region"]]
    d.rectangle([x, y, x + SPORT_W, y + SPORT_H], fill=CARD, outline=RULE,
                width=1)
    d.rectangle([x + 1, y + 1, x + SPORT_W - 1, y + 25], fill=PANEL2)
    d.text((x + 6, y + 6), s["score"], font=F_SCORE, fill=YELLOW)
    s["icon"](d, x + SPORT_W - 24, y + 5)
    badge(d, x + 4, y + 28, s["num"], col)
    tag = "%s \u00b7 %s" % (s["region"], s["beat"])
    d.text((x + 24, y + 30), tag, font=F_TAG, fill=col)
    text_block(d, x + 4, y + 44, s["body"], F_SPORT_B, SPORT_W - 8,
               MUTED, 11, max_lines=3)


def draw_also(d):
    half = (len(ALSO) + 1) // 2
    col_x = (MX, MX + 506)
    for ci, chunk in enumerate((ALSO[:half], ALSO[half:])):
        cx = col_x[ci]
        for ri, (num, place, text, region) in enumerate(chunk):
            ry = 850 + ri * 10.5
            col = REGION_COLORS[region]
            pre = "%d. %s: " % (num, place)
            d.text((cx, ry), pre, font=F_ALSO_B, fill=col)
            tx = cx + d.textlength(pre, font=F_ALSO_B)
            d.text((tx, ry), text, font=F_ALSO, fill=WHITE)


def draw_footer(d):
    d.text((MX, 982), DATE_CHECK, font=F_FOOT, fill=YELLOW_SOFT)
    d.text((MX, 993), FOOTER_L1, font=F_FOOT, fill=MUTED)
    d.text((MX, 1004), FOOTER_L2, font=F_FOOT, fill=FAINT)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=2)
    draw_top(d)
    draw_masthead(d)
    draw_lead(d)
    draw_block_header(d, 266, "POLITICS & DIPLOMACY", "STORIES 04\u201311")
    for r in range(2):
        for i, s in enumerate(POLITICS[r * 4:(r + 1) * 4]):
            draw_medium(d, s, MX + i * (MED_W + 8), 284 + r * 106)
    draw_block_header(d, 498, "INDONESIA & ECONOMY", "STORIES 12\u201319")
    for r in range(2):
        for i, s in enumerate(INDONESIA[r * 4:(r + 1) * 4]):
            draw_medium(d, s, MX + i * (MED_W + 8), 516 + r * 106)
    draw_block_header(d, 730, "SPORT", "STORIES 20\u201324")
    for i, s in enumerate(SPORTS):
        draw_sport(d, s, MX + i * (SPORT_W + 9), 748)
    draw_block_header(d, 832, "ALSO ON SUNDAY 22 NOVEMBER",
                      "STORIES 25\u201348")
    draw_also(d)
    draw_footer(d)
    return img


# -------------------------------------------------------------- fit check
def check_fit():
    """Measure every text block against its box; report overflows.

    Returns the number of problems found. Nothing here draws -- it only
    measures with a scratch Draw, so it is safe to run before rendering.
    """
    probe = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(probe)
    problems = []

    def note(where, detail):
        problems.append("%s: %s" % (where, detail))

    if d.textlength(LEAD["head"], font=F_LEAD_H) > 752:
        note("lead head", "too wide")
    rows = wrap(d, LEAD["body"], F_LEAD_B, 752)
    if len(rows) > 3:
        note("lead body", "%d lines" % len(rows))
    total = sum(d.textlength(c, font=F_CHIP) + 16 for c in LEAD["chips"])
    total += 8 * (len(LEAD["chips"]) - 1)
    if total > 752:
        note("lead chips", "%.0f px wide" % total)
    for s, hw in zip(CLIMATE_EXTRA, (470, 480)):
        pre = "%02d \u00b7 " % s["num"]
        got = d.textlength(pre, font=F_ALSO_B) + d.textlength(
            s["text"], font=F_ALSO)
        if got > hw:
            note("climate #%d" % s["num"], "%.0f px > %d" % (got, hw))
    for s in POLITICS + INDONESIA:
        tag = "%s \u00b7 %s" % (s["region"], s["beat"])
        if d.textlength(tag, font=F_TAG) > MED_W - 28:
            note("#%d tag" % s["num"], "too wide")
        heads = wrap(d, s["head"], F_MED_H, MED_W - 8)
        if len(heads) > 2:
            note("#%d head" % s["num"], "%d lines" % len(heads))
        bodies = wrap(d, s["body"], F_MED_B, MED_W - 8)
        if len(bodies) > 2:
            note("#%d body" % s["num"], "%d lines" % len(bodies))
    for s in SPORTS:
        if d.textlength(s["score"], font=F_SCORE) > SPORT_W - 32:
            note("#%d score" % s["num"], "too wide")
        tag = "%s \u00b7 %s" % (s["region"], s["beat"])
        if d.textlength(tag, font=F_TAG) > SPORT_W - 28:
            note("#%d tag" % s["num"], "too wide")
        bodies = wrap(d, s["body"], F_SPORT_B, SPORT_W - 8)
        if len(bodies) > 3:
            note("#%d body" % s["num"], "%d lines" % len(bodies))
    for num, place, text, region in ALSO:
        pre = "%d. %s: " % (num, place)
        got = d.textlength(pre, font=F_ALSO_B) + d.textlength(
            text, font=F_ALSO)
        if got > 490:
            note("also #%d" % num, "%.0f px > 490" % got)
    for name, line in (("date check", DATE_CHECK), ("footer 1", FOOTER_L1),
                       ("footer 2", FOOTER_L2)):
        if d.textlength(line, font=F_FOOT) > CW:
            note(name, "%.0f px > %d"
                 % (d.textlength(line, font=F_FOOT), CW))
    if d.textlength("Sunday, 22 November 2026", font=F_MAST) > CW:
        note("masthead", "too wide")
    for p in problems:
        print("FIT PROBLEM:", p)
    print("fit check: %d problem(s), %d stories"
          % (len(problems), 1 + len(CLIMATE_EXTRA) + len(POLITICS)
             + len(INDONESIA) + len(SPORTS) + len(ALSO)))
    return len(problems)


def main():
    problems = check_fit()
    img = build()
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    print(out, size, "bytes", img.size,
          "UNDER 1 MiB" if size <= 1048576 else "OVER 1 MiB")
    if problems:
        print("WARNING: fix the fit problems above and re-render.")


if __name__ == "__main__":
    main()
