#!/usr/bin/env python3
"""news-image-20261122 v3 — renderer for the Sunday 22 November 2026 poster.

Fresh build for the make.fun resubmit. Cream newspaper broadsheet, Pola 6
structure: masthead -> ticker -> UTC timeline -> BY THE NUMBERS -> region
bar -> 3 leads with scene illustrations -> Sparta II strip -> 10 cards ->
ALSO ON list -> DATE CHECK -> HOW SURE legend.

Every story was verified as having happened or first been reported on
Sunday 22 November 2026 (any time zone) from wire sources; see CONSENSUS.md
in the build directory for the title + wire source of each story.

Deterministic: no timestamps, no randomness, fixed font paths. Run:
    python3 build_image.py [output.png]
Default output is entry.png beside this file.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (248, 243, 230)      # cream newspaper
INK = (28, 26, 23)           # near-black
RED = (166, 25, 46)          # ticker / rules / kickers
NAVY = (31, 58, 95)          # secondary accent, night sky
PANEL = (239, 231, 211)      # numbers strip background
CARD = (255, 253, 247)       # card background
BORDER = (216, 208, 188)     # card border
GRAY = (107, 101, 96)        # muted text
SEA = (220, 232, 240)        # map sea
SEA_DK = (178, 204, 224)     # deeper sea
SAND = (233, 220, 180)       # map land
SMOKE = (120, 116, 108)
FIRE = (224, 122, 26)
WHITE = (255, 255, 255)

W = H = 1024
M = 28                        # side margin
CW = W - 2 * M                # content width: 968

# ---------------------------------------------------------------- fonts
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- helpers
def wrap(draw, text, font, max_w):
    """Wrap text to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_block(draw, x, y, text, font, max_w, leading, color=INK, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=color)
        y += leading
    return y


def centered(draw, cx, y, text, font, color=INK):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=color)
    return w


def hrule(draw, y, x0=M, x1=W - M, color=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def kicker(draw, x, y, text, color=RED):
    draw.text((x, y), text, font=F(SANS_B, 10), fill=color)
    return y + 14


# ---------------------------------------------------------------- illustrations
def illo_drones(img, x, y, w, h):
    """Night sky over Dymer: drones, a torn-open apartment block, smoke."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    for sx, sy in [(18, 10), (52, 22), (96, 8), (140, 18), (190, 9),
                   (232, 24), (268, 12), (296, 28), (70, 34), (210, 36)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(220, 225, 235))
    # moon
    d.ellipse([x + w - 34, y + 8, x + w - 14, y + 28], fill=(235, 230, 200))
    # drones: small body + rotor arms
    for dx, dy, s in [(30, 16, 1.0), (110, 30, 0.8), (185, 14, 1.1),
                      (250, 40, 0.7), (150, 48, 0.6)]:
        cx, cy = x + dx, y + dy
        d.ellipse([cx - 5 * s, cy - 2 * s, cx + 5 * s, cy + 2 * s], fill=(15, 15, 20))
        d.line([cx - 9 * s, cy - 4 * s, cx + 9 * s, cy - 4 * s], fill=(15, 15, 20), width=1)
        d.ellipse([cx - 11 * s, cy - 5 * s, cx - 7 * s, cy - 3 * s], fill=(200, 200, 205))
        d.ellipse([cx + 7 * s, cy - 5 * s, cx + 11 * s, cy - 3 * s], fill=(200, 200, 205))
        d.line([cx, cy + 2 * s, cx, cy + 7 * s], fill=(255, 120, 60), width=1)
    # ground
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(20, 24, 34))
    # apartment block, middle section torn open
    bx, bw, by, bh = x + 36, 130, y + h - 62, 50
    d.rectangle([bx, by, bx + bw, by + bh], fill=(150, 146, 138))
    d.rectangle([bx + 52, by, bx + 78, by + bh], fill=(30, 28, 26))  # torn gap
    for row in range(5):                      # windows
        for col in range(5):
            wx = bx + 6 + col * 25
            wy = by + 5 + row * 9
            if 52 <= wx - bx <= 78:
                continue
            lit = (row + col) % 3 == 0
            d.rectangle([wx, wy, wx + 12, wy + 6],
                        fill=(255, 190, 90) if lit else (60, 58, 54))
    # fire glow + smoke from the gap (kept inside the panel)
    d.polygon([(bx + 52, by + bh), (bx + 65, by + 8), (bx + 78, by + bh)],
              fill=(224, 122, 26))
    for ox, oy, r in [(58, -6, 7), (66, -12, 9)]:
        d.ellipse([bx + ox - r, by + oy - r, bx + ox + r, by + oy + r],
                  fill=(120, 116, 108))
    # second, intact block
    d.rectangle([x + 196, y + h - 44, x + 262, y + h - 12], fill=(120, 116, 110))
    for row in range(3):
        for col in range(3):
            d.rectangle([x + 202 + col * 20, y + h - 39 + row * 10,
                         x + 212 + col * 20, y + h - 33 + row * 10],
                        fill=(255, 190, 90) if (row + col) % 2 else (60, 58, 54))
    d.text((x + 8, y + h - 11), "DYMER · NORTH OF KYIV · 05:00",
           font=F(SANS_B, 9), fill=(235, 230, 210))
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


def illo_cop(img, x, y, w, h):
    """COP31: a globe cracked through, stamped NO DEAL."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=(236, 230, 210))
    # globe
    cx, cy, r = x + 62, y + h // 2 - 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3, fill=(205, 224, 240))
    d.ellipse([cx - r, cy - 12, cx + r, cy + 12], outline=NAVY, width=1)
    d.ellipse([cx - 12, cy - r, cx + 12, cy + r], outline=NAVY, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=NAVY, width=1)
    # crack through the globe
    d.line([cx - 20, cy - 30, cx - 4, cy - 8, cx - 14, cy + 6, cx + 8, cy + 30],
           fill=RED, width=3)
    # NO DEAL stamp, rotated, tucked top-right
    stamp = Image.new("RGBA", (170, 46), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([2, 2, 167, 43], outline=RED, width=3)
    sd.text((12, 8), "NO DEAL", font=F(SANS_B, 24), fill=RED)
    stamp = stamp.rotate(8, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (x + w - 182, y + 2), stamp)
    d.text((x + w - 66, y + h - 20), "ANTALYA", font=F(SANS_B, 9), fill=GRAY)
    d.text((x + 8, y + h - 11), "35% BY 2035 · $120BN DROPPED · 1.5°C OVERSHOOT",
           font=F(SANS_B, 9), fill=INK)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


def illo_bahrain(img, x, y, w, h):
    """The Gulf: Bahrain island, two radar domes, missile arcs. CLAIM."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # Arabian coast (left) and Qatar bump (right)
    d.polygon([(x, y), (x + 52, y), (x + 44, y + 30), (x + 58, y + 58),
               (x + 40, y + h), (x, y + h)], fill=SAND)
    d.polygon([(x + w, y + 40), (x + w - 44, y + 52), (x + w - 30, y + h),
               (x + w, y + h)], fill=SAND)
    # Bahrain island
    d.ellipse([x + 104, y + 30, x + 196, y + 68], fill=SAND, outline=(150, 130, 90))
    d.text((x + 204, y + 42), "BAHRAIN", font=F(SANS_B, 9), fill=INK)
    # radar domes on the island, spread apart
    for rx, lab in [(122, "AL-RIFFA"), (164, "AWALI")]:
        d.rectangle([x + rx, y + 42, x + rx + 3, y + 54], fill=INK)
        d.pieslice([x + rx - 8, y + 30, x + rx + 11, y + 49], 180, 360, fill=WHITE)
        d.arc([x + rx - 8, y + 30, x + rx + 11, y + 49], 180, 360, fill=INK, width=1)
        d.text((x + rx - 12, y + 54), lab, font=F(SANS_B, 7), fill=INK)
    # missile arcs from the upper left (Iran side), drawn as in-panel curves
    for k, x_end in enumerate((128, 164)):
        pts = []
        for t in range(0, 21):
            f = t / 20
            px = x + 12 + f * (x_end - 12)
            py = y + 6 + f * f * 34 + k * 4
            pts.append((px, py))
        d.line(pts, fill=RED, width=2)
    d.text((x + 6, y + 18), "IRAN", font=F(SANS_B, 9), fill=GRAY)
    d.text((x + w - 52, y + 4), "GULF", font=F(SANS_B, 9), fill=GRAY)
    # CLAIM tag
    d.rectangle([x + w - 74, y + h - 20, x + w - 6, y + h - 6], fill=RED)
    d.text((x + w - 66, y + h - 19), "CLAIM", font=F(SANS_B, 10), fill=WHITE)
    d.text((x + 8, y + h - 11), "2 PATRIOT RADARS 'HIT' — DENIED",
           font=F(SANS_B, 9), fill=INK)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


def illo_sparta(img, x, y, w, h):
    """Sparta II: burning freighter under tow off Loviisa, Gulf of Finland."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # Finnish coast (top)
    d.polygon([(x, y), (x + w, y), (x + w, y + 16), (x + 190, y + 22),
               (x + 90, y + 14), (x, y + 20)], fill=SAND)
    d.text((x + 8, y + 2), "FINLAND · LOVIISA", font=F(SANS_B, 9), fill=INK)
    # dashed maritime boundary
    for dx in range(0, w, 16):
        d.line([x + dx, y + 34, x + dx + 8, y + 34], fill=GRAY, width=1)
    # freighter hull + containers
    hx, hy = x + 40, y + h - 34
    d.polygon([(hx, hy), (hx + 190, hy), (hx + 178, hy + 18), (hx + 12, hy + 18)],
              fill=(52, 58, 66))
    for i, col in enumerate([(168, 60, 50), (60, 110, 150), (200, 170, 60),
                             (168, 60, 50), (70, 140, 90)]):
        d.rectangle([hx + 14 + i * 34, hy - 20, hx + 44 + i * 34, hy - 2],
                    fill=col, outline=INK)
    # fire on the aft containers (smoke omitted: no room above the ship)
    d.polygon([(hx + 20, hy - 20), (hx + 31, hy - 26), (hx + 42, hy - 20)],
              fill=FIRE)
    d.polygon([(hx + 26, hy - 20), (hx + 31, hy - 24), (hx + 36, hy - 20)],
              fill=(255, 200, 60))
    d.text((hx + 60, hy + 2), "SPARTA II", font=F(SANS_B, 9), fill=WHITE)
    # tow line + tug
    d.line([hx + 190, hy + 6, x + w - 30, y + h - 18], fill=INK, width=2)
    tx, ty = x + w - 34, y + h - 26
    d.polygon([(tx, ty), (tx + 26, ty), (tx + 22, ty + 12), (tx + 4, ty + 12)],
              fill=(140, 30, 30))
    d.rectangle([tx + 8, ty - 8, tx + 18, ty], fill=(140, 30, 30))
    d.text((x + 8, y + h - 11), "TOWED OUT SUNDAY · 7 VESSELS FOUGHT THE FIRE",
           font=F(SANS_B, 9), fill=INK)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


# ---------------------------------------------------------------- story data
# region codes: EU Europe, ME Middle East, AP Asia-Pacific, AM Americas,
# AF Africa, OC Oceania, WO World.
LEADS = [
    {
        "tag": "UKRAINE · WAR", "region": "EU",
        "head": "186 drones in one night — a Kyiv block falls",
        "body": ("Russia launched 186 drones overnight, 72 of them jet-powered "
                 "Shaheds; Ukraine says 161 were downed. In Dymer, north of Kyiv, "
                 "a five-storey block was torn open at 05:00; by nightfall 5 were "
                 "dead, 14 unaccounted for. A Vyshneve supermarket was hit later: "
                 "3 more killed."),
        "illo": illo_drones,
    },
    {
        "tag": "CLIMATE · ANTALYA", "region": "WO",
        "head": "COP31 ends with no deal — a first since 2000",
        "body": ("A final text tabled at dawn — 35% clean electricity by 2035, no "
                 "fossil-fuel mention, the $120bn adaptation target dropped — was "
                 "rejected in the closing plenary. \u201cI understand that there is no "
                 "agreement on this text,\u201d said president Murat Kurum. 90+ nations "
                 "signed a separate pledge."),
        "illo": illo_cop,
    },
    {
        "tag": "GULF · CLAIM", "region": "ME",
        "head": "Iran claims two US Patriot radars hit in Bahrain",
        "body": ("The IRGC says a missile-and-drone strike hit US Patriot radars at "
                 "al-Riffa and Awali, and released video it says shows the launches. "
                 "Bahrain says a civilian site was hit, a fire, no casualties; its "
                 "defence ministry says projectiles were intercepted. A US official "
                 "told CBS no US personnel or facilities were damaged."),
        "illo": illo_bahrain,
    },
]

SPARTA = {
    "tag": "GULF OF FINLAND",
    "head": "Sparta II still burning — towed out of Finnish waters",
    "body": ("Hit by two drones on Saturday, the sanctioned Russian cargo ship burned "
             "through Sunday as seven vessels fought the fire. A Russian rescue ship "
             "began towing it out on Sunday afternoon. Estonia warns of a further "
             "attack risk; Helsinki is probing a suspected Russian helicopter "
             "airspace violation."),
}

CARDS = [
    {"tag": "HONG KONG", "region": "AP",
     "head": "Record 98.79% vote in Hong Kong polls",
     "body": ("5,640 of 5,709 Election Committee voters cast ballots — up nine "
              "points on 2021. All 723 seats filled; results on Sunday evening.")},
    {"tag": "CRICKET · WELLINGTON", "region": "OC",
     "head": "India declare 720/9, highest ever in NZ",
     "body": ("Rahul 136, Pant 128 as India pile up 720/9, lead 352. NZ 119/2 at "
              "stumps on day four, trailing by 233.")},
    {"tag": "NBA", "region": "AM",
     "head": "Wembanyama drops 50 in Spurs win",
     "body": ("50 points, 19 rebounds, 5 blocks, 4 steals as San Antonio beat "
              "New Orleans 114–91 — a first in NBA history. Spurs 14–3.")},
    {"tag": "IRAN", "region": "ME",
     "head": "Iran starts rationing electricity",
     "body": ("Rolling cuts of up to two hours a day begin as war damage bites; "
              "gas processing is still ~130m cu m/day short after March strikes.")},
    {"tag": "INDONESIA", "region": "AP",
     "head": "Cikande fire: 3 dead, 34 missing",
     "body": ("Search at the Milkita candy factory is suspended for the night; "
              "24 body bags await DNA identification. 29 confirmed alive.")},
    {"tag": "FORMULA 1", "region": "AM",
     "head": "Verstappen wins Las Vegas GP",
     "body": ("1:27:39.624 from pole, Norris +0.639, Piastri +1.529 — a record "
              "352 overtakes and 35 lead changes on the Strip.")},
    {"tag": "TENNIS · TURIN", "region": "EU",
     "head": "Alcaraz wins ATP Finals at last",
     "body": ("Beats Zverev 6–2, 7–6(7) for a first title, saving three set "
              "points in the tiebreak. Zverev stays world No. 1.")},
    {"tag": "FOOTBALL", "region": "EU",
     "head": "Liverpool 4–0 Man Utd",
     "body": ("Szoboszlai, Wirtz, Ngumoha, Munoz sink United in Pochettino's "
              "first game; Yoro sent off after 8 minutes. United 19th.")},
    {"tag": "SAUDI ARABIA", "region": "ME",
     "head": "Houthi missiles downed over Riyadh",
     "body": ("Saudi defences intercept missiles aimed at the capital, the east "
              "and the south; an Aramco building is damaged by shrapnel.")},
    {"tag": "STRAIT OF HORMUZ", "region": "ME",
     "head": "Tanker Torkel still burning at anchor",
     "body": ("JMIC names the two tankers hit off Khasab on Saturday; a fresh "
              "tanker incident is reported in the Gulf of Oman on Sunday.")},
]

ALSO_ON = [
    ("AM", "FBI hack: Washington state suspends gun checks \u201cas of Nov 22\u201d"),
    ("AF", "Bayelsa boat toll rises to 29; Tinubu approves \u20a6250m for families"),
    ("ME", "Hamas seeks urgent mediator talks after Gaza aid-van strike"),
    ("ME", "IDF names 3 PIJ men it says were killed in that strike"),
    ("AP", "Nepal PM Shah arrives in Delhi on first foreign trip"),
    ("AP", "Manipur liquor toll reaches 17; 228 in hospital, 38 on dialysis"),
    ("EU", "Pope Leo shares lunch with 1,300 poor at the Vatican"),
    ("WO", "Bitcoin holds above $60,000, closes Sunday at $61,271"),
    ("ME", "Four nations demand unhindered Gaza aid access"),
    ("EU", "Hull 2–0 Brighton: McBurnie brace in added time"),
    ("EU", "Belgium: all flights grounded Monday in national strike"),
    ("AM", "Bolsonaro remains in intensive care in Bras\u00edlia"),
    ("ME", "Eisenkot–Likud unity talks end without deal after 4 hours"),
    ("ME", "IRGC releases video it says shows Bahrain drone launches"),
    ("ME", "UKMTO: Hormuz traffic 65% below pre-war levels"),
    ("EU", "Vyshneve supermarket hit: 3 killed, 15 hurt, incl. 3 children"),
    ("EU", "Dymer: 9 evacuated from the ruined block; search goes on"),
    ("WO", "COP31: 90+ nations sign separate electrification pledge"),
    ("OC", "India: six batsmen pass 70 — a Test first; Pant hits 108 sixes"),
    ("AM", "Wembanyama: first 50-15-5-4 game in NBA history; Spurs 14–3"),
    ("AM", "F1: record 352 overtakes, 35 lead changes in Las Vegas"),
    ("EU", "ATP doubles: Arribage/Olivetti win 3–6, 7–6(2), 10–6"),
]

TIMELINE = [
    ("01:00", "Hong Kong polls open"),
    ("05:00", "Dymer block hit"),
    ("05:44", "Verstappen wins in Vegas"),
    ("06:07", "Bahrain: missiles downed"),
    ("08:07", "186 drones, 161 downed"),
    ("10:00", "HK polls close — record"),
    ("21:56", "Dymer toll: 5 dead"),
]

NUMBERS = [
    ("186", "DRONES LAUNCHED"),
    ("161", "DOWNED"),
    ("98.79%", "HK TURNOUT"),
    ("720/9", "INDIA DECLARE"),
    ("50", "WEMBANYAMA PTS"),
    ("$61,271", "BITCOIN CLOSE"),
]

REGION_NAMES = {"EU": "EUROPE", "ME": "MIDDLE EAST", "AP": "ASIA-PACIFIC",
                "AM": "AMERICAS", "AF": "AFRICA", "OC": "OCEANIA", "WO": "WORLD"}

DATE_CHECK = (
    "Fri 20 Nov: Peru quake · El Chapo arrest · Kryvyi Rih · Nvidia probe · Roundup "
    "deal · Riemann claim · Denmark attaché · Estonia closure · Bayelsa capsize "
    "(toll: Sun). Sat 21 Nov: 400-drone barrage · BepiColombo orbit · Basra fire · "
    "EU–Indonesia deal · Sparta II hit (fire/tow: Sun) · Gaza aid-van strike (talks: "
    "Sun) · France UN move · Ladakh polls · England 37–12 NZ · F-16 denial · H-6 "
    "bomber · Banda M7.2 · Palawan M5.9 · Bolsonaro ICU (remains: Sun). Earlier: "
    "Patong fire (16 Nov) · Myanmar ruling (Thu) · Somalia envoy (Thu) · Japan–India "
    "deal (Thu) · Kenya Ebola (11 Nov) · Cantine (5–6 Nov)."
)


# ---------------------------------------------------------------- sections
def section_masthead(img, draw, y):
    draw.rectangle([0, 0, W, 6], fill=RED)
    centered(draw, W // 2, y + 4, "THE WORLD IN ONE DAY",
             F(SERIF_B, 46), INK)
    centered(draw, W // 2, y + 56,
             "SUNDAY, 22 NOVEMBER 2026  ·  FULL-DAY EDITION  ·  WIRES TO 23:59 UTC  ·  "
             "36 STORIES  ·  7 REGIONS",
             F(SANS_B, 12), INK)
    hrule(draw, y + 78, width=2)
    hrule(draw, y + 82, width=1)
    return y + 88


def section_ticker(img, draw, y):
    draw.rectangle([M, y, W - M, y + 26], fill=RED)
    text = ("186 DRONES OVER UKRAINE — DYMER BLOCK HIT   ·   COP31 ENDS WITH NO DEAL"
            "   ·   IRAN CLAIMS PATRIOT HITS IN BAHRAIN")
    size = 14
    while size > 10 and draw.textlength(text, font=F(SANS_B, size)) > CW - 16:
        size -= 1
    tw = draw.textlength(text, font=F(SANS_B, size))
    draw.text((W // 2 - tw / 2, y + 5), text, font=F(SANS_B, size), fill=WHITE)
    return y + 32


def section_timeline(img, draw, y):
    draw.text((M, y + 2), "THE DAY\nIN UTC", font=F(SANS_B, 9), fill=RED)
    x0, x1 = M + 78, W - M
    n = len(TIMELINE)
    line_y = y + 16
    d = draw
    d.line([(x0, line_y), (x1, line_y)], fill=INK, width=1)
    for i, (t, lab) in enumerate(TIMELINE):
        tx = x0 + i * (x1 - x0) // (n - 1)
        d.ellipse([tx - 3, line_y - 3, tx + 3, line_y + 3], fill=RED)
        tw = d.textlength(t, font=F(SANS_B, 10))
        d.text((tx - tw / 2, y + 1), t, font=F(SANS_B, 10), fill=INK)
        lw = d.textlength(lab, font=F(SANS, 9))
        lx = max(M + 78, min(tx - lw / 2, W - M - lw))
        d.text((lx, line_y + 5), lab, font=F(SANS, 9), fill=GRAY)
    return y + 32


def section_numbers(img, draw, y):
    draw.rectangle([M, y, W - M, y + 42], fill=PANEL, outline=BORDER)
    draw.text((M + 8, y + 4), "BY THE", font=F(SANS_B, 10), fill=RED)
    draw.text((M + 8, y + 16), "NUMBERS", font=F(SANS_B, 10), fill=RED)
    bx0 = M + 92
    bw = (W - M - bx0 - 8) // 6
    for i, (num, lab) in enumerate(NUMBERS):
        bx = bx0 + i * bw
        cx = bx + bw // 2
        centered(draw, cx, y + 2, num, F(SERIF_B, 21), INK)
        centered(draw, cx, y + 27, lab, F(SANS_B, 8), GRAY)
        if i:
            draw.line([(bx, y + 6), (bx, y + 36)], fill=BORDER, width=1)
    return y + 48


def section_regions(img, draw, y):
    counts = {}
    for lead in LEADS:
        counts[lead["region"]] = counts.get(lead["region"], 0) + 1
    counts["EU"] = counts.get("EU", 0) + 1  # Sparta II
    for c in CARDS:
        counts[c["region"]] = counts.get(c["region"], 0) + 1
    for r, _ in ALSO_ON:
        counts[r] = counts.get(r, 0) + 1
    order = ["EU", "ME", "AP", "AM", "AF", "OC", "WO"]
    parts = ["%s %d" % (REGION_NAMES[r], counts.get(r, 0))
             for r in order if counts.get(r, 0)]
    hrule(draw, y, color=BORDER)
    centered(draw, W // 2, y + 4, "   ·   ".join(parts), F(SANS_B, 11), INK)
    hrule(draw, y + 20, color=BORDER)
    return y + 26


def section_leads(img, draw, y):
    col_w, gap = 314, 13
    for i, lead in enumerate(LEADS):
        x = M + i * (col_w + gap)
        hrule(draw, y, x0=x, x1=x + col_w, color=RED, width=3)
        yy = kicker(draw, x, y + 6, lead["tag"])
        yy = draw_block(draw, x, yy, lead["head"], F(SERIF_B, 20),
                        col_w, 23, max_lines=3)
        iy = yy + 4
        lead["illo"](img, x, iy, col_w, 84)
        draw_block(draw, x, iy + 90, lead["body"], F(SERIF, 11),
                   col_w, 13, max_lines=6)
    return y + 242


def section_sparta(img, draw, y):
    draw.rectangle([M, y, W - M, y + 80], fill=CARD, outline=BORDER)
    illo_sparta(img, M + 6, y + 6, 300, 68)
    tx = M + 318
    yy = kicker(draw, tx, y + 8, SPARTA["tag"])
    yy = draw_block(draw, tx, yy, SPARTA["head"], F(SERIF_B, 17),
                    W - M - tx - 10, 20, max_lines=1)
    draw_block(draw, tx, yy + 2, SPARTA["body"], F(SERIF, 11),
               W - M - tx - 10, 13, max_lines=3)
    return y + 86


def section_cards(img, draw, y):
    cw, ch, gap = 188, 101, 7
    for i, card in enumerate(CARDS):
        row, col = divmod(i, 5)
        x = M + col * (cw + gap)
        cy = y + row * (ch + gap)
        draw.rectangle([x, cy, x + cw, cy + ch], fill=CARD, outline=BORDER)
        draw.text((x + 7, cy + 5), card["tag"], font=F(SANS_B, 9), fill=RED)
        yy = draw_block(draw, x + 7, cy + 19, card["head"], F(SERIF_B, 13),
                        cw - 14, 15, max_lines=2)
        draw_block(draw, x + 7, yy + 2, card["body"], F(SANS, 10),
                   cw - 14, 12, max_lines=4)
    return y + 2 * ch + gap + 6


def section_also(img, draw, y):
    draw.text((M, y), "ALSO ON SUNDAY", font=F(SANS_B, 11), fill=RED)
    hrule(draw, y + 15, color=BORDER)
    col_w = (CW - 24) // 2
    font = F(SANS, 10)
    for i, (_, line) in enumerate(ALSO_ON):
        col = 0 if i < 11 else 1
        row = i % 11
        x = M + col * (col_w + 24)
        ly = y + 20 + row * 11
        num = "%d." % (i + 1)
        draw.text((x, ly), num, font=F(SANS_B, 10), fill=RED)
        draw.text((x + 22, ly), line, font=font, fill=INK)
    return y + 20 + 11 * 11 + 4


def section_datecheck(img, draw, y):
    draw.rectangle([M, y, W - M, y + 70], outline=RED, width=2, fill=(252, 247, 236))
    draw.text((M + 8, y + 5), "DATE CHECK — NOT SUNDAY, DESPITE THE HEADLINES",
              font=F(SANS_B, 11), fill=RED)
    draw_block(draw, M + 8, y + 20, DATE_CHECK, F(SANS, 9), CW - 16, 11,
               max_lines=4)
    return y + 76


def section_footer(img, draw, y):
    # HOW SURE legend with hand-drawn dots (no font glyph dependency)
    lx = M
    draw.text((lx, y), "HOW SURE:", font=F(SANS_B, 9), fill=INK)
    lx += 62
    items = [("filled", "Confirmed by 2+ wires"),
             ("half", "Single source or labelled CLAIM"),
             ("open", "Developing — tolls may rise")]
    for kind, lab in items:
        cx, cy = lx + 5, y + 5
        if kind == "filled":
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)
        elif kind == "half":
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=INK)
            draw.pieslice([cx - 4, cy - 4, cx + 4, cy + 4], 90, 270, fill=INK)
        else:
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=INK)
        draw.text((lx + 12, y), lab, font=F(SANS, 9), fill=GRAY)
        lx += 12 + int(draw.textlength(lab, font=F(SANS, 9))) + 18
    centered(draw, W // 2, y + 13,
             "SOURCES: Reuters · AP · AFP · BBC · Al Jazeera · RFE/RL · info.gov.hk · "
             "ESPNcricinfo · formula1.com · FIA · UKMTO · JMIC · Vatican News · Finnhub",
             F(SANS, 9), GRAY)
    return y + 26


# ---------------------------------------------------------------- main
def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = 0
    y = section_masthead(img, draw, y)
    y = section_ticker(img, draw, y)
    y = section_timeline(img, draw, y)
    y = section_numbers(img, draw, y)
    y = section_regions(img, draw, y)
    y = section_leads(img, draw, y)
    y = section_sparta(img, draw, y)
    y = section_cards(img, draw, y)
    y = section_also(img, draw, y)
    y = section_datecheck(img, draw, y)
    y = section_footer(img, draw, y)
    img.save(out_path, format="PNG")
    return y


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    end_y = build(out)
    print("wrote %s (%d bytes), content ends at y=%d" % (
        out, os.path.getsize(out), end_y))
