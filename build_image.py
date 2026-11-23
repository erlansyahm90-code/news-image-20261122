#!/usr/bin/env python3
"""Build the news-image-20261122 poster (Sunday 22 November 2026).

Local build tool only: renders entry.png with Pillow + DejaVu fonts.
The graded program is main.ts, which simply copies the bundled entry.png
to /output/entry.png (Node stdlib only, deterministic bytes).

Design (v2): midnight-blue broadsheet with a neon-yellow accent,
restructured to the winner pattern from ~/workspace/makefun/
winners-study.md (Pattern 6): giant date masthead, red ticker of the
3 biggest headlines, UTC timeline, a BY THE NUMBERS strip, a 9-region
bar, THREE big leads with detailed illustrations, 10 small stories
(2 rows x 5), then a world map with numbered pins beside a DATE CHECK
box, a HOW SURE legend and a pin index, followed by a numbered "also"
list and sources.
37 stories, every one verified as having happened or first been
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
GREEN = (110, 220, 130)      # CONFIRMED dot in HOW SURE legend

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
    ("LEAD2_H", "DejaVuSerif-Bold.ttf", 17),  # 3-col lead heads
    ("NUM_BIG", "DejaVuSans-Bold.ttf", 26),   # BY THE NUMBERS figures
    ("TICK", "DejaVuSans-Bold.ttf", 12),      # ticker headlines
    ("TIME_B", "DejaVuSans-Bold.ttf", 10),    # timeline times
    ("MAP_LAB", "DejaVuSans-Bold.ttf", 8),    # map / pin labels
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
F_LEAD2_H = _F["LEAD2_H"]
F_NUM_BIG = _F["NUM_BIG"]
F_TICK = _F["TICK"]
F_TIME_B = _F["TIME_B"]
F_MAP_LAB = _F["MAP_LAB"]


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


# ------------------------------------------- lead illustrations (v2)
# Wide strips (~324x85) for the three big leads. Each tells its story
# at a glance: a picture on the left, the key fact in text on the right.

def _mini_flag_eu(d, fx, fy, w=26, h=15):
    d.rectangle([fx, fy, fx + w, fy + h], fill=(0, 51, 153))
    for i in range(12):
        ang = math.pi * i / 6
        d.ellipse([fx + w // 2 + 5 * math.cos(ang) - 1,
                   fy + h // 2 + 5 * math.sin(ang) - 1,
                   fx + w // 2 + 5 * math.cos(ang) + 1,
                   fy + h // 2 + 5 * math.sin(ang) + 1],
                  fill=(255, 204, 0))


def _mini_flag_uk(d, fx, fy, w=26, h=15):
    d.rectangle([fx, fy, fx + w, fy + h], fill=(0, 36, 125))
    d.line([(fx, fy), (fx + w, fy + h)], fill=(255, 255, 255), width=3)
    d.line([(fx + w, fy), (fx, fy + h)], fill=(255, 255, 255), width=3)
    d.rectangle([fx + w // 2 - 2, fy, fx + w // 2 + 2, fy + h],
                fill=(255, 255, 255))
    d.rectangle([fx, fy + h // 2 - 2, fx + w, fy + h // 2 + 2],
                fill=(255, 255, 255))
    d.rectangle([fx + w // 2 - 1, fy, fx + w // 2 + 1, fy + h],
                fill=(207, 0, 15))
    d.rectangle([fx, fy + h // 2 - 1, fx + w, fy + h // 2 + 1],
                fill=(207, 0, 15))


def _mini_flag_panama(d, fx, fy, w=26, h=15):
    d.rectangle([fx, fy, fx + w // 2, fy + h // 2], fill=(255, 255, 255))
    d.rectangle([fx + w // 2, fy, fx + w, fy + h // 2],
                fill=(210, 16, 52))
    d.rectangle([fx, fy + h // 2, fx + w // 2, fy + h], fill=(0, 84, 159))
    d.rectangle([fx + w // 2, fy + h // 2, fx + w, fy + h],
                fill=(255, 255, 255))
    _star5(d, fx + 6, fy + 4, 2, (0, 84, 159))
    _star5(d, fx + 20, fy + 11, 2, (210, 16, 52))


def _mini_flag_marshall(d, fx, fy, w=26, h=15):
    d.rectangle([fx, fy, fx + w, fy + h], fill=(0, 56, 147))
    d.polygon([(fx, fy + h), (fx + 8, fy + h), (fx + w, fy + 2),
               (fx + w, fy + 6)], fill=(255, 255, 255))
    d.polygon([(fx, fy + h), (fx + 4, fy + h), (fx + w, fy + 4),
               (fx + w, fy + 6)], fill=(255, 120, 0))
    _star5(d, fx + 5, fy + 4, 2, (255, 255, 255))


def _mini_flag_norway(d, fx, fy, w=26, h=15):
    d.rectangle([fx, fy, fx + w, fy + h], fill=(186, 12, 47))
    d.rectangle([fx + 7, fy, fx + 12, fy + h], fill=(255, 255, 255))
    d.rectangle([fx, fy + 5, fx + w, fy + 10], fill=(255, 255, 255))
    d.rectangle([fx + 8, fy, fx + 11, fy + h], fill=(0, 32, 91))
    d.rectangle([fx, fy + 6, fx + w, fy + 9], fill=(0, 32, 91))


def ill_lead_cop31(d, x, y, w, h):
    """Cracked globe + NO DEAL + the five flags that said no."""
    _sky(d, x, y, w, h, (12, 24, 48), (30, 55, 95))
    cx, cy, r = x + 44, y + h // 2, 32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(45, 110, 180),
              outline=(150, 200, 240), width=2)
    d.ellipse([cx - 20, cy - 20, cx - 3, cy - 6], fill=(110, 190, 110))
    d.ellipse([cx + 2, cy + 2, cx + 20, cy + 18], fill=(110, 190, 110))
    d.ellipse([cx - 24, cy + 8, cx - 11, cy + 20], fill=(110, 190, 110))
    d.line([(cx - 23, cy - 21), (cx - 9, cy - 8), (cx - 17, cy + 5),
            (cx - 2, cy + 17), (cx + 8, cy + 29)], fill=(8, 12, 26),
           width=3)
    tx = x + 88
    d.text((tx, y + 6), "NO DEAL", font=F_LEAD2_H, fill=YELLOW)
    d.text((tx, y + 28), "44+ HOURS OVERTIME", font=F_ILL, fill=WHITE)
    d.text((tx, y + 42), "THE FIVE WHO SAID NO", font=F_MAP_LAB,
           fill=YELLOW_SOFT)
    fy = y + 56
    flags = (_mini_flag_eu, _mini_flag_uk, _mini_flag_panama,
             _mini_flag_marshall, _mini_flag_norway)
    fx = tx + (w - 88 - (5 * 26 + 4 * 3)) // 2
    for fn in flags:
        fn(d, fx, fy)
        d.rectangle([fx, fy, fx + 26, fy + 15],
                    outline=(200, 210, 230))
        fx += 29
    d.text((tx, y + 73), "NEXT: COP32 \u00b7 ADDIS ABABA \u00b7 NOV 2027",
           font=F_MAP_LAB, fill=MUTED)


def ill_lead_fire(d, x, y, w, h):
    """Burning factory + the toll in a dark panel."""
    _sky(d, x, y, w, h, (255, 140, 40), (255, 200, 80))
    d.rectangle([x + 14, y + 34, x + 170, y + h - 4], fill=(50, 45, 45))
    d.rectangle([x + 170, y + 12, x + 184, y + h - 4], fill=(50, 45, 45))
    for fx in (26, 52, 78, 104, 130):
        d.polygon([(x + fx, y + 34), (x + fx + 7, y + 22),
                   (x + fx + 14, y + 34)], fill=(255, 230, 120))
    _burst(d, x + 177, y + 10, 5, color=(255, 120, 30))
    _smoke(d, x + 190, y + 16, 0.8, color=(90, 90, 90))
    d.text((x + 20, y + h - 18), "CIKANDE \u00b7 BANTEN", font=F_ILL,
           fill=(255, 255, 255))
    px, pw = x + 205, w - 213
    d.rectangle([px, y + 8, px + pw, y + h - 8], fill=(30, 22, 20),
                outline=(255, 200, 80), width=1)
    d.text((px + 10, y + 12), "36", font=F_NUM_BIG, fill=YELLOW)
    d.text((px + 62, y + 22), "MISSING", font=F_ILL, fill=WHITE)
    d.text((px + 10, y + 46), "3 DEAD \u00b7 4 HURT", font=F_MAP_LAB,
           fill=(255, 200, 160))
    d.text((px + 10, y + 58), "15 SURVIVED", font=F_MAP_LAB,
           fill=(255, 200, 160))


def ill_lead_cartel(d, x, y, w, h):
    """Gold badge + FBI TOP 10 + the shootout toll."""
    d.rectangle([x, y, x + w, y + h], fill=(28, 30, 40))
    _star5(d, x + 44, y + h // 2, 30, (220, 180, 60),
           outline=(255, 230, 140))
    d.ellipse([x + 33, y + h // 2 - 11, x + 55, y + h // 2 + 11],
              fill=(28, 30, 40))
    d.text((x + 39, y + h // 2 - 11), "$", font=F_LEAD2_H,
           fill=(220, 180, 60))
    tx = x + 88
    d.text((tx, y + 6), "FBI TOP 10", font=F_LEAD2_H, fill=(255, 210, 90))
    d.text((tx, y + 28), "CAPTURED IN SINALOA", font=F_ILL, fill=WHITE)
    d.text((tx, y + 44), "11 KILLED IN THE SHOOTOUT", font=F_ILL,
           fill=(255, 130, 120))
    d.text((tx, y + 60), "FAUSTO ISIDRO MEZA FLORES", font=F_MAP_LAB,
           fill=MUTED)
    # police-light stripe along the bottom edge
    for i in range(12):
        col = (200, 40, 40) if i % 2 == 0 else (40, 90, 220)
        d.rectangle([x + i * (w // 12), y + h - 5,
                     x + (i + 1) * (w // 12), y + h], fill=col)


# ------------------------------------------------------------- world map
# Rough continent outlines in (lon, lat); projected equirectangular
# into the map panel. Readable at poster size; the numbered pins carry
# the precision. Lat range shown: 85..-55.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-115, 73), (-100, 72),
     (-90, 74), (-80, 73), (-70, 62), (-60, 55), (-55, 52), (-60, 47),
     (-70, 42), (-75, 35), (-80, 26), (-88, 21), (-95, 18), (-100, 20),
     (-108, 24), (-114, 30), (-120, 36), (-125, 42), (-128, 50),
     (-135, 57), (-150, 60), (-162, 60)],
    # South America
    [(-78, 8), (-70, 12), (-62, 9), (-52, 4), (-44, -3), (-36, -8),
     (-39, -15), (-47, -24), (-53, -33), (-60, -40), (-66, -47),
     (-69, -52), (-73, -40), (-73, -28), (-73, -18), (-79, -8), (-81, 0)],
    # Europe
    [(-10, 36), (-9, 43), (-3, 48), (0, 51), (5, 53), (8, 57), (12, 55),
     (18, 56), (22, 60), (26, 66), (32, 70), (40, 68), (35, 62), (30, 58),
     (28, 52), (25, 46), (29, 45), (24, 41), (20, 42), (16, 44), (12, 44),
     (8, 44), (4, 42), (-1, 38)],
    # Africa
    [(-17, 15), (-14, 24), (-10, 31), (-4, 35), (5, 37), (12, 34),
     (20, 32), (30, 31), (35, 28), (40, 20), (44, 12), (51, 11), (47, 4),
     (41, -6), (38, -14), (35, -22), (33, -27), (29, -32), (23, -34),
     (18, -34), (15, -27), (12, -18), (9, -3), (4, 4), (-6, 5), (-12, 8)],
    # Asia
    [(28, 45), (32, 42), (36, 36), (42, 39), (48, 38), (50, 30), (57, 26),
     (62, 25), (67, 24), (72, 20), (77, 8), (81, 14), (86, 20), (91, 22),
     (96, 18), (100, 14), (103, 2), (105, 9), (109, 14), (107, 19),
     (111, 21), (116, 23), (120, 28), (122, 32), (126, 36), (128, 39),
     (132, 43), (137, 45), (141, 42), (143, 49), (150, 55), (158, 58),
     (168, 62), (178, 65), (172, 68), (160, 70), (145, 72), (130, 72),
     (115, 73), (100, 75), (85, 73), (72, 72), (62, 69), (52, 68),
     (44, 67), (36, 66), (32, 62), (30, 55), (28, 50)],
    # Australia
    [(113, -22), (114, -29), (116, -34), (122, -34), (127, -32),
     (132, -32), (135, -35), (139, -37), (144, -38), (149, -37),
     (153, -31), (153, -27), (150, -23), (146, -19), (142, -11),
     (138, -13), (135, -15), (132, -12), (128, -14), (124, -17),
     (119, -19)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
     (142, -8), (137, -7), (132, -4)],
    # Borneo
    [(109, 1), (113, 4), (118, 6), (119, 1), (117, -3), (112, -3),
     (109, -1)],
    # Sumatra
    [(95, 5), (99, 2), (102, -2), (105, -5), (104, -6), (100, -3),
     (97, 1)],
    # Java
    [(105, -6), (110, -7), (115, -8), (114, -8), (109, -7), (106, -6)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 57), (1, 53), (-1, 51)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 37), (141, 41), (143, 44),
     (141, 44), (140, 39), (137, 36), (133, 34), (130, 33)],
    # New Zealand
    [(167, -46), (170, -43), (173, -40), (175, -38), (178, -38),
     (175, -41), (171, -44), (168, -47)],
    # Madagascar
    [(44, -16), (47, -15), (49, -18), (47, -24), (45, -25), (44, -20)],
]

# (story num, lon, lat, display dx, dy, pin-index label). dx/dy shift the
# disc away from a crowded true spot; a leader line joins disc to spot.
PINS = [
    (1, 30, 36, 0, 0, "COP31 collapses \u00b7 Antalya"),
    (2, 106, -6, 0, 0, "Cikande fire \u00b7 Banten"),
    (3, -108, 25, 0, 0, "El Chapo captured \u00b7 Sinaloa"),
    (4, 35, 32, 0, -15, "Eisenkot \u00b7 Israel"),
    (5, 34, 31, 0, 15, "Gaza aid \u00b7 Gaza"),
    (6, 37, 55, 14, -8, "US envoys \u00b7 Moscow"),
    (7, 135, -25, 0, 0, "AUKUS \u00b7 Australia"),
    (8, 56, 26, 0, 0, "Hormuz \u00b7 Strait"),
    (9, 30, 50, -14, 6, "Kyiv power \u00b7 Ukraine"),
    (10, 139, 35, 0, 0, "Japan cuts \u00b7 Tokyo"),
    (12, -115, 36, 0, 0, "Las Vegas GP \u00b7 F1"),
    (13, -3, 53, 0, 0, "Liverpool 4\u20130 \u00b7 Anfield"),
]


def _project(mx, my, mw, mh, lon, lat):
    """Equirectangular: lon -180..180, lat 85..-55."""
    px = mx + (lon + 180) / 360.0 * mw
    py = my + (85 - lat) / 140.0 * mh
    return px, py


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

# v2: THREE big leads, all global (winner Pattern 6). No local story
# leads the poster.
LEADS = [
    dict(num=1, region="GLOBAL", beat="COP31 \u00b7 ANTALYA",
         head="COP31 COLLAPSES \u2014 NO DEAL",
         body=("The longest climate summit ever ends with no deal \u2014 "
               "the first COP to fail since 2009. The final text never "
               "mentions fossil fuels."),
         ill=ill_lead_cop31),
    dict(num=2, region="INDONESIA", beat="DISASTER \u00b7 CIKANDE",
         head="Factory fire: 36 missing, 3 dead",
         body=("Rescuers search the Milkita candy plant in Banten after "
               "Saturday\u2019s blaze. Four hurt, 15 survived; the fire "
               "is still burning as families wait."),
         ill=ill_lead_fire),
    dict(num=3, region="AMERICAS", beat="CRIME \u00b7 SINALOA",
         head="\u201cEl Chapo Isidro\u201d captured; 11 killed",
         body=("Fausto Isidro Meza Flores, one of the FBI\u2019s 10 most "
               "wanted, is seized after a shootout in Guasave, Sinaloa. "
               "At least 11 people are killed."),
         ill=ill_lead_cartel),
]

TICKER = ["COP31 COLLAPSES \u2014 NO DEAL",
          "CIKANDE FIRE: 36 MISSING, 3 DEAD",
          "\u201cEL CHAPO ISIDRO\u201d CAPTURED; 11 KILLED"]

# (UTC time, event) -- key moments of the day, in order.
TIMELINE = [
    ("01:25", "\u201cEl Chapo Isidro\u201d captured"),
    ("03:56", "Cikande search begins"),
    ("06:00", "COP31 ends with no deal"),
    ("14:00", "Hull 2\u20130 Brighton"),
    ("16:30", "Liverpool 4\u20130 Man Utd"),
]

# (big figure, label) -- six verified numbers, one per column.
NUMBERS = [
    ("36", "MISSING IN THE CIKANDE FACTORY FIRE"),
    ("44+", "HOURS OF COP31 OVERTIME"),
    ("11", "KILLED IN THE SINALOA SHOOTOUT"),
    ("150,000", "TENTS STUCK AT THE GAZA BORDER"),
    ("4\u20130", "LIVERPOOL ROUT MAN UTD"),
    ("$60K", "BITCOIN RETAKES $60,000"),
]

# (region, story count) -- 9 regions, 37 stories, ordered by count.
REGIONS = [
    ("EUROPE", 9), ("INDONESIA", 8), ("GLOBAL", 6), ("MIDDLE EAST", 4),
    ("SPORT", 4), ("AMERICAS", 3), ("ASIA", 1), ("OCEANIA", 1),
    ("AFRICA", 1),
]

# 10 small stories (2 rows x 5): kicker band + 2-line headline, no body.
# kicker = the big stat/keyword; icon = sport icon or None.
SMALL = [
    dict(num=4, region="MIDDLE EAST", beat="POLITICS",
         kicker="EISENKOT",
         head="Eisenkot tapped to form Israel\u2019s government",
         icon=None),
    dict(num=5, region="MIDDLE EAST", beat="DIPLOMACY",
         kicker="150,000 TENTS",
         head="Four nations demand Gaza aid access",
         icon=None),
    dict(num=6, region="GLOBAL", beat="DIPLOMACY",
         kicker="MOSCOW \u2192 DUBLIN",
         head="US envoys head to Moscow, then Dublin",
         icon=None),
    dict(num=7, region="OCEANIA", beat="DEFENCE",
         kicker="VIRGINIA CLASS",
         head="Australia slams US office over AUKUS",
         icon=None),
    dict(num=8, region="MIDDLE EAST", beat="ENERGY",
         kicker="2 DAYS",
         head="Iran shortens Hormuz reopening to two days",
         icon=None),
    dict(num=9, region="EUROPE", beat="WAR",
         kicker="3 PLANTS DOWN",
         head="Ukraine\u2019s energy crisis deepens before winter",
         icon=None),
    dict(num=10, region="ASIA", beat="DEFENCE",
         kicker="CUTS",
         head="Japan weighs cutting missile and warship buys",
         icon=None),
    dict(num=11, region="GLOBAL", beat="MARKETS",
         kicker="BTC $60K",
         head="Bitcoin climbs back above $60,000",
         icon=None),
    dict(num=12, region="SPORT", beat="F1 \u00b7 LAS VEGAS GP",
         kicker="VERSTAPPEN WINS",
         head="Verstappen wins Las Vegas GP from pole",
         icon=icon_f1),
    dict(num=13, region="SPORT", beat="PREMIER LEAGUE",
         kicker="LIV 4\u20130 MAN UTD",
         head="Liverpool rout United in Pochettino\u2019s debut",
         icon=icon_ball),
]

# (num, place, text, region) -- one line each, no sub-line.
ALSO = [
    (14, "Jakarta", "Prabowo to name two VP candidates on 25 Nov",
     "INDONESIA"),
    (15, "Jakarta", "Mahfud: recount the MPR session to replace Gibran",
     "INDONESIA"),
    (16, "Riau", "RAPP loses 338,536-ha permit over environmental "
     "breaches", "INDONESIA"),
    (17, "Gaza", "Winter storm floods shelters; 1m+ displaced face cold",
     "MIDDLE EAST"),
    (18, "Kyiv", "Zelensky faults lack of US intel warning before "
     "Russian strikes", "EUROPE"),
    (19, "Berlin", "Germany plans a new national fare for occasional "
     "transit users", "EUROPE"),
    (20, "Berlin", "Health minister: insurance contributions stable "
     "through 2027", "EUROPE"),
    (21, "Washington", "House revises college sports bill to allow "
     "22-team leagues", "AMERICAS"),
    (22, "Rome", "Italy budget bill lifts flat tax cap to \u20ac100,000",
     "EUROPE"),
    (23, "Stuttgart", "Bosch deepens AI partnership with Microsoft",
     "EUROPE"),
    (24, "Wolfsburg", "Volkswagen plans to freeze pay rises in cost "
     "push", "EUROPE"),
    (25, "Frankfurt", "Lufthansa to cut 1,000 jobs as fuel costs bite",
     "EUROPE"),
    (26, "Jakarta", "Jakarta\u2019s 2027 minimum wage hits Rp6.13m, "
     "highest in RI", "INDONESIA"),
    (27, "Jakarta", "Coal, CPO, ferroalloy exports to run via DSI from "
     "2027", "INDONESIA"),
    (28, "Jakarta", "242,482 part-time teachers go full-time in 2027",
     "INDONESIA"),
    (29, "Jakarta", "OJK sanctions 10 stock cases; Rp23.77bn gains "
     "returned", "INDONESIA"),
    (30, "Hull", "Hull 2\u20130 Brighton as McBurnie scores twice in "
     "injury time", "SPORT"),
    (31, "Washington", "KC Current win first NWSL title, 2\u20131 over "
     "Spirit", "SPORT"),
    (32, "Mercury", "BepiColombo\u2019s MIXS telescope sends first cosmic "
     "views", "GLOBAL"),
    (33, "Orbit", "China\u2019s broadband constellations left 52 rocket "
     "bodies", "GLOBAL"),
    (34, "Gaming", "GTA 6: critics score it 99, users just 5.6",
     "GLOBAL"),
    (35, "Lagos", "Young Nigerians register to vote in lower numbers "
     "than in 2023", "AFRICA"),
    (36, "USA", "Teen gamer and his mother help the FBI rescue a "
     "missing girl", "AMERICAS"),
    (37, "London", "Princess of Wales fronts papers ahead of her new "
     "documentary", "EUROPE"),
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
#   ticker 90..112 / timeline 114..134 / numbers 136..192
#   regions 194..214 / leads 216..406 / small header 412, rows 428..584
#   map header 590, map+right col 606..800 / also header 806, list 824..950
#   footer 956..1013
LEAD_W = (CW - 2 * 8) // 3          # 326
LEAD_H = 190
LEAD_Y = 216
SMALL_W = (CW - 4 * 8) // 5         # 192
SMALL_H = 77
SMALL_Y0 = 428
MAP_X, MAP_Y, MAP_W, MAP_H = MX, 606, 400, 194
RIGHT_X, RIGHT_W = 430, 580
ALSO_Y0 = 824


def draw_top(d):
    d.text((MX, 7), "ONE DAY OF WORLD NEWS \u00b7 ONE PICTURE", font=F_TOP,
           fill=YELLOW)
    r = "37 STORIES \u00b7 9 REGIONS \u00b7 ALL FROM THIS SUNDAY"
    d.text((W - MX - d.textlength(r, font=F_TOP_R), 7), r, font=F_TOP_R,
           fill=MUTED)
    d.line([(MX, 25), (W - MX, 25)], fill=RULE, width=1)


def draw_masthead(d):
    t = "Sunday, 22 November 2026"
    tw = d.textlength(t, font=F_MAST)
    d.text(((W - tw) / 2, 28), t, font=F_MAST, fill=WHITE)
    d.line([(MX, 87), (W - MX, 87)], fill=YELLOW, width=2)


def draw_ticker(d):
    """Red breaking-news band: the 3 biggest headlines."""
    d.rectangle([MX, 90, W - MX, 112], fill=(140, 25, 25))
    line = " \u25cf ".join(TICKER)
    lw = d.textlength(line, font=F_TICK)
    d.text(((W - lw) / 2, 94), line, font=F_TICK, fill=WHITE)


def draw_timeline(d):
    """UTC timeline: five key moments of the day, in order."""
    x = MX
    d.text((x, 117), "UTC TIMELINE", font=F_TIME_B, fill=YELLOW)
    x += d.textlength("UTC TIMELINE  ", font=F_TIME_B)
    for i, (t, ev) in enumerate(TIMELINE):
        if i:
            d.text((x, 117), "\u00b7", font=F_ALSO, fill=MUTED)
            x += d.textlength("\u00b7 ", font=F_ALSO)
        d.text((x, 117), t, font=F_TIME_B, fill=YELLOW_SOFT)
        x += d.textlength(t + " ", font=F_TIME_B)
        d.text((x, 117), ev, font=F_ALSO, fill=MUTED)
        x += d.textlength(ev + " ", font=F_ALSO)
    d.line([(MX, 134), (W - MX, 134)], fill=RULE, width=1)


def draw_numbers(d):
    """BY THE NUMBERS strip: label cell + 6 big-stat columns."""
    d.rectangle([MX, 136, W - MX, 192], fill=PANEL, outline=RULE, width=1)
    lx = MX
    d.rectangle([lx, 136, lx + 120, 192], fill=PANEL2)
    d.text((lx + 12, 150), "BY THE", font=F_TOP, fill=YELLOW)
    d.text((lx + 12, 164), "NUMBERS", font=F_TOP, fill=YELLOW)
    cols = (CW - 120) // 6
    for i, (big, label) in enumerate(NUMBERS):
        cx = MX + 120 + i * cols
        if i:
            d.line([(cx, 140), (cx, 188)], fill=RULE, width=1)
        d.text((cx + 8, 141), big, font=F_NUM_BIG, fill=YELLOW)
        text_block(d, cx + 8, 171, label, F_MAP_LAB, cols - 14,
                   MUTED, 10, max_lines=2)


def draw_regions(d):
    """9-region bar: segment widths proportional to story counts."""
    total = sum(n for _, n in REGIONS)
    x = MX
    for name, n in REGIONS:
        seg = CW * n // total
        col = REGION_COLORS[name]
        d.rectangle([x, 194, x + seg - 1, 214], fill=col)
        if seg >= 60:
            lab = "%s %d" % (name, n)
            lw = d.textlength(lab, font=F_MAP_LAB)
            d.text((x + (seg - lw) / 2, 200), lab, font=F_MAP_LAB,
                   fill=(10, 16, 30))
        else:
            lab = "%d" % n
            lw = d.textlength(lab, font=F_MAP_LAB)
            d.text((x + (seg - lw) / 2, 200), lab, font=F_MAP_LAB,
                   fill=(10, 16, 30))
        x += seg


def draw_lead3(d, s, x, y):
    """One of the three big leads: illustration + tag + head + body."""
    col = REGION_COLORS[s["region"]]
    d.rectangle([x, y, x + LEAD_W, y + LEAD_H], fill=CARD, outline=RULE,
                width=1)
    s["ill"](d, x + 1, y + 1, LEAD_W - 2, 85)
    d.rectangle([x, y, x + LEAD_W, y + 86], outline=RULE, width=1)
    badge(d, x + 4, y + 90, s["num"], col)
    tag = "%s \u00b7 %s" % (s["region"], s["beat"])
    d.text((x + 24, y + 92), tag, font=F_TAG, fill=col)
    text_block(d, x + 4, y + 106, s["head"], F_LEAD2_H, LEAD_W - 8,
               WHITE, 20, max_lines=2)
    text_block(d, x + 4, y + 148, s["body"], F_MED_B, LEAD_W - 8, MUTED,
               13, max_lines=3)


def draw_block_header(d, y, title, span):
    d.rectangle([MX, y + 1, MX + 10, y + 11], fill=YELLOW)
    d.text((MX + 16, y), title, font=F_SEC, fill=YELLOW)
    d.text((W - MX - d.textlength(span, font=F_TOP_R), y + 1), span,
           font=F_TOP_R, fill=MUTED)


def draw_small(d, s, x, y):
    """One small story: kicker band + tag + 2-line headline."""
    col = REGION_COLORS[s["region"]]
    d.rectangle([x, y, x + SMALL_W, y + SMALL_H], fill=CARD, outline=RULE,
                width=1)
    d.rectangle([x + 1, y + 1, x + SMALL_W - 1, y + 25], fill=PANEL2)
    d.text((x + 6, y + 6), s["kicker"], font=F_SCORE, fill=YELLOW)
    if s["icon"] is not None:
        s["icon"](d, x + SMALL_W - 24, y + 5)
    badge(d, x + 4, y + 28, s["num"], col)
    tag = "%s \u00b7 %s" % (s["region"], s["beat"])
    d.text((x + 24, y + 30), tag, font=F_TAG, fill=col)
    text_block(d, x + 4, y + 44, s["head"], F_MED_H, SMALL_W - 8, WHITE,
               14, max_lines=2)


def draw_map(d):
    """World map: dark ocean, green continents, numbered pins."""
    d.rectangle([MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H],
                fill=(16, 32, 60), outline=RULE, width=1)
    for poly in CONTINENTS:
        pts = [_project(MAP_X + 6, MAP_Y + 6, MAP_W - 12, MAP_H - 12,
                        lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(110, 140, 110), outline=(70, 100, 70))
    for num, lon, lat, dx, dy, _label in PINS:
        px, py = _project(MAP_X + 6, MAP_Y + 6, MAP_W - 12, MAP_H - 12,
                          lon, lat)
        cx, cy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (cx, cy)], fill=YELLOW_SOFT, width=1)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=YELLOW,
                  outline=(10, 16, 30), width=1)
        lab = "%d" % num
        lw = d.textlength(lab, font=F_MAP_LAB)
        d.text((cx - lw / 2, cy - 5), lab, font=F_MAP_LAB,
               fill=(10, 16, 30))


def draw_datecheck(d, x, y, w):
    """DATE CHECK box: stories deliberately left out."""
    d.rectangle([x, y, x + w, y + 60], fill=PANEL, outline=YELLOW, width=1)
    d.text((x + 8, y + 6), "DATE CHECK", font=F_TIME_B, fill=YELLOW)
    body = "L" + DATE_CHECK[14:]
    text_block(d, x + 8, y + 22, body, F_FOOT, w - 16, WHITE, 12,
               max_lines=3)


def draw_howsure(d, x, y, w):
    """HOW SURE legend: confidence levels of the stories."""
    d.text((x, y), "HOW SURE", font=F_TIME_B, fill=YELLOW)
    items = [(GREEN, "CONFIRMED"), (YELLOW, "OFFICIAL"),
             ((255, 140, 0), "REPORTED")]
    ix = x + 90
    for col, lab in items:
        d.ellipse([ix, y + 2, ix + 8, y + 10], fill=col)
        d.text((ix + 12, y), lab, font=F_ALSO_B, fill=WHITE)
        ix += 12 + d.textlength(lab, font=F_ALSO_B) + 28


def draw_pin_index(d, x, y):
    """PIN INDEX: the 12 numbered map pins, 2 columns x 6 rows."""
    d.text((x, y), "PIN INDEX", font=F_TIME_B, fill=YELLOW)
    colw = (RIGHT_W - 8) // 2
    for i, (num, _lon, _lat, _dx, _dy, label) in enumerate(PINS):
        cx = x + (i // 6) * (colw + 8)
        ry = y + 14 + (i % 6) * 12
        d.text((cx, ry), "%d" % num, font=F_ALSO_B, fill=YELLOW)
        d.text((cx + 16, ry), label, font=F_ALSO, fill=MUTED)


def draw_also(d):
    half = (len(ALSO) + 1) // 2
    col_x = (MX, MX + 506)
    for ci, chunk in enumerate((ALSO[:half], ALSO[half:])):
        cx = col_x[ci]
        for ri, (num, place, text, region) in enumerate(chunk):
            ry = ALSO_Y0 + ri * 10.5
            col = REGION_COLORS[region]
            pre = "%d. %s: " % (num, place)
            d.text((cx, ry), pre, font=F_ALSO_B, fill=col)
            tx = cx + d.textlength(pre, font=F_ALSO_B)
            d.text((tx, ry), text, font=F_ALSO, fill=WHITE)


def draw_footer(d):
    d.line([(MX, 956), (W - MX, 956)], fill=RULE, width=1)
    d.text((MX, 963), FOOTER_L1, font=F_FOOT, fill=MUTED)
    d.text((MX, 975), FOOTER_L2, font=F_FOOT, fill=FAINT)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=2)
    draw_top(d)
    draw_masthead(d)
    draw_ticker(d)
    draw_timeline(d)
    draw_numbers(d)
    draw_regions(d)
    for i, s in enumerate(LEADS):
        draw_lead3(d, s, MX + i * (LEAD_W + 8), LEAD_Y)
    draw_block_header(d, 412, "MORE OF THE DAY", "STORIES 04\u201313")
    for r in range(2):
        for i, s in enumerate(SMALL[r * 5:(r + 1) * 5]):
            draw_small(d, s, MX + i * (SMALL_W + 8), SMALL_Y0 + r * 79)
    draw_block_header(d, 590, "WHERE IT HAPPENED", "12 PINNED STORIES")
    draw_map(d)
    draw_datecheck(d, RIGHT_X, 606, RIGHT_W)
    draw_howsure(d, RIGHT_X, 676, RIGHT_W)
    draw_pin_index(d, RIGHT_X, 706)
    draw_block_header(d, 806, "ALSO ON SUNDAY 22 NOVEMBER",
                      "STORIES 14\u201337")
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

    # top bar + masthead
    r = "37 STORIES \u00b7 9 REGIONS \u00b7 ALL FROM THIS SUNDAY"
    if d.textlength(r, font=F_TOP_R) > 400:
        note("top right", "too wide")
    if d.textlength("Sunday, 22 November 2026", font=F_MAST) > CW:
        note("masthead", "too wide")
    # ticker: one line, centred in the red band
    tick = " \u25cf ".join(TICKER)
    if d.textlength(tick, font=F_TICK) > CW - 16:
        note("ticker", "%.0f px > %d"
             % (d.textlength(tick, font=F_TICK), CW - 16))
    # timeline: label + 5 items on one line
    tl = d.textlength("UTC TIMELINE  ", font=F_TIME_B)
    for i, (t, ev) in enumerate(TIMELINE):
        if i:
            tl += d.textlength("\u00b7 ", font=F_ALSO)
        tl += d.textlength(t + " ", font=F_TIME_B)
        tl += d.textlength(ev + " ", font=F_ALSO)
    if tl > CW:
        note("timeline", "%.0f px > %d" % (tl, CW))
    # BY THE NUMBERS: big figures + 2-line labels
    cols = (CW - 120) // 6
    for big, label in NUMBERS:
        if d.textlength(big, font=F_NUM_BIG) > cols - 16:
            note("numbers %s" % big, "too wide")
        if len(wrap(d, label, F_MAP_LAB, cols - 14)) > 2:
            note("numbers %s" % big, "label > 2 lines")
    # region bar: labels must fit their segments
    total = sum(n for _, n in REGIONS)
    for name, n in REGIONS:
        seg = CW * n // total
        if seg >= 60:
            lab = "%s %d" % (name, n)
            if d.textlength(lab, font=F_MAP_LAB) > seg - 4:
                note("region %s" % name, "label too wide")
    # three leads: tag, 2-line head, 3-line body
    for s in LEADS:
        tag = "%s \u00b7 %s" % (s["region"], s["beat"])
        if d.textlength(tag, font=F_TAG) > LEAD_W - 28:
            note("lead #%d tag" % s["num"], "too wide")
        heads = wrap(d, s["head"], F_LEAD2_H, LEAD_W - 8)
        if len(heads) > 2:
            note("lead #%d head" % s["num"], "%d lines" % len(heads))
        bodies = wrap(d, s["body"], F_MED_B, LEAD_W - 8)
        if len(bodies) > 3:
            note("lead #%d body" % s["num"], "%d lines" % len(bodies))
    # small stories: kicker, tag, 2-line head
    for s in SMALL:
        lim = SMALL_W - 32 if s["icon"] is not None else SMALL_W - 12
        if d.textlength(s["kicker"], font=F_SCORE) > lim:
            note("#%d kicker" % s["num"], "too wide")
        tag = "%s \u00b7 %s" % (s["region"], s["beat"])
        if d.textlength(tag, font=F_TAG) > SMALL_W - 28:
            note("#%d tag" % s["num"], "too wide")
        heads = wrap(d, s["head"], F_MED_H, SMALL_W - 8)
        if len(heads) > 2:
            note("#%d head" % s["num"], "%d lines" % len(heads))
    # date-check box body: 3 lines max
    body = "L" + DATE_CHECK[14:]
    if len(wrap(d, body, F_FOOT, RIGHT_W - 16)) > 3:
        note("date check", "body > 3 lines")
    # pin index: each label fits its column
    colw = (RIGHT_W - 8) // 2
    for num, _lon, _lat, _dx, _dy, label in PINS:
        got = 16 + d.textlength(label, font=F_ALSO)
        if got > colw:
            note("pin #%d" % num, "%.0f px > %d" % (got, colw))
    # ALSO list: one line each
    for num, place, text, region in ALSO:
        pre = "%d. %s: " % (num, place)
        got = d.textlength(pre, font=F_ALSO_B) + d.textlength(
            text, font=F_ALSO)
        if got > 490:
            note("also #%d" % num, "%.0f px > 490" % got)
    # footer lines
    for name, line in (("footer 1", FOOTER_L1), ("footer 2", FOOTER_L2)):
        if d.textlength(line, font=F_FOOT) > CW:
            note(name, "%.0f px > %d"
                 % (d.textlength(line, font=F_FOOT), CW))
    # counts: 3 leads + 10 small + 24 also = 37; regions sum to 37
    n_stories = len(LEADS) + len(SMALL) + len(ALSO)
    if n_stories != 37:
        note("story count", "%d != 37" % n_stories)
    if sum(n for _, n in REGIONS) != 37:
        note("region sum", "%d != 37" % sum(n for _, n in REGIONS))
    if len(REGIONS) != 9:
        note("region count", "%d != 9" % len(REGIONS))
    for p in problems:
        print("FIT PROBLEM:", p)
    print("fit check: %d problem(s), %d stories"
          % (len(problems), n_stories))
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
