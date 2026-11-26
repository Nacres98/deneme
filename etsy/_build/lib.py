"""Shared design system for the NexaGlobe Christmas printables.

Palette: "Evergreen Minimal" - white pages (printer friendly), pine green, berry red, warm gold.
"""
import math
import os
import random

from reportlab.lib.colors import HexColor, white, Color
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

for name in ["Playfair-Regular", "Playfair-Bold", "Playfair-Black", "Playfair-Italic",
             "Montserrat-Regular", "Montserrat-Medium", "Montserrat-SemiBold", "Montserrat-Bold"]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, name + ".ttf")))
pdfmetrics.registerFont(TTFont("GreatVibes", os.path.join(FONTS, "GreatVibes-Regular.ttf")))

PINE = HexColor("#1E3A2B")
PINE2 = HexColor("#2F5A43")
SAGE = HexColor("#8FA98F")
BERRY = HexColor("#A3302B")
BERRY2 = HexColor("#C4544C")
GOLD = HexColor("#B8913A")
CREAM = HexColor("#FBF7EF")
CREAM2 = HexColor("#F1E9D8")
INK = HexColor("#2A2A2A")
MUTED = HexColor("#8A847A")
LINE = HexColor("#D9D2C3")
KRAFT = HexColor("#D8B98C")

BRAND = "NexaGlobe Studio"
SIZES = {"US-Letter": letter, "A4": A4}

S = ParagraphStyle
STY = {
    "body": S("body", fontName="Montserrat-Regular", fontSize=10.5, leading=15, textColor=INK),
    "bodyc": S("bodyc", fontName="Montserrat-Regular", fontSize=10.5, leading=15, textColor=INK, alignment=TA_CENTER),
    "small": S("small", fontName="Montserrat-Regular", fontSize=8.5, leading=12, textColor=INK),
    "smallc": S("smallc", fontName="Montserrat-Regular", fontSize=8.5, leading=12, textColor=MUTED, alignment=TA_CENTER),
    "card": S("card", fontName="Montserrat-Medium", fontSize=11, leading=14.5, textColor=INK, alignment=TA_CENTER),
    "cardbig": S("cardbig", fontName="Playfair-Bold", fontSize=17, leading=21, textColor=PINE, alignment=TA_CENTER),
    "story": S("story", fontName="Montserrat-Regular", fontSize=12.5, leading=20, textColor=INK),
    "h3": S("h3", fontName="Montserrat-Bold", fontSize=10.5, leading=14, textColor=BERRY),
}


def para(c, text, x, y_top, w, style="body", h=1000):
    """Draw a paragraph with its top at y_top. Returns the height used."""
    st = STY[style] if isinstance(style, str) else style
    p = Paragraph(text, st)
    _, ph = p.wrap(w, h)
    p.drawOn(c, x, y_top - ph)
    return ph


def para_center_v(c, text, x, y, w, h, style="card"):
    """Draw a paragraph centred vertically and horizontally inside a box."""
    st = STY[style] if isinstance(style, str) else style
    p = Paragraph(text, st)
    _, ph = p.wrap(w, h)
    p.drawOn(c, x, y + (h - ph) / 2)
    return ph


def spaced(c, text, x, y, font="Montserrat-SemiBold", size=9, color=BERRY, spacing=2.2, anchor="center"):
    """Letter-spaced small caps style label."""
    text = text.upper()
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    if anchor == "center":
        x -= total / 2
    elif anchor == "right":
        x -= total
    c.setFont(font, size)
    c.setFillColor(color)
    for ch, w in zip(text, widths):
        c.drawString(x, y, ch)
        x += w + spacing
    return total


def fit_font(text, font, size, maxw, minsize=8):
    while size > minsize and pdfmetrics.stringWidth(text, font, size) > maxw:
        size -= 0.5
    return size


# --------------------------------------------------------------------------- drawings
def _style(c, mode, fill, stroke=INK, lw=1.6):
    if mode == "line":
        c.setFillColor(white)
        c.setStrokeColor(INK)
        c.setLineWidth(lw)
    else:
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)


def leaf_path(c, x, y, length, angle, width=0.42, spikes=3):
    """Holly leaf: spiky almond shape pointing along angle (deg) from (x, y)."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    n = spikes * 2
    for side in (1, -1):
        rng = range(n + 1) if side == 1 else range(n, -1, -1)
        for i in rng:
            t = i / n
            half = math.sin(math.pi * t) * length * width / 2
            if i % 2 == 1:
                half *= 0.72  # notch between spikes
            px = x + ux * length * t + nx * half * side
            py = y + uy * length * t + ny * half * side
            pts.append((px, py))
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    return p, (x, y), (x + ux * length, y + uy * length)


def holly(c, x, y, s, mode="color"):
    for ang in (155, 25):
        p, a, b = leaf_path(c, x, y, s, ang)
        _style(c, mode, PINE2, PINE, 0.8 if mode == "color" else 1.6)
        c.drawPath(p, fill=1, stroke=1)
        c.setStrokeColor(SAGE if mode == "color" else INK)
        c.setLineWidth(0.6 if mode == "color" else 1)
        c.line(a[0], a[1], b[0] * 0.15 + a[0] * 0.85 + (b[0] - a[0]) * 0.7, b[1] * 0.15 + a[1] * 0.85 + (b[1] - a[1]) * 0.7)
    for dx, dy in ((-0.11, 0.05), (0.11, 0.05), (0, -0.09)):
        _style(c, mode, BERRY, BERRY, 0.6 if mode == "color" else 1.6)
        c.circle(x + dx * s, y + dy * s, s * 0.12, fill=1, stroke=1)


def snowflake(c, x, y, r, color=SAGE, lw=1.0):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    c.setLineCap(1)
    for i in range(6):
        a = math.radians(90 + 60 * i)
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        c.line(x, y, ex, ey)
        for f in (0.45, 0.72):
            bx, by = x + r * f * math.cos(a), y + r * f * math.sin(a)
            for d in (35, -35):
                b = a + math.radians(d)
                L = r * (0.32 if f < 0.5 else 0.22)
                c.line(bx, by, bx + L * math.cos(b), by + L * math.sin(b))
    c.restoreState()


def star(c, x, y, r, points=5, inner=0.45, rot=90):
    p = c.beginPath()
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / points)
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        (p.moveTo if i == 0 else p.lineTo)(px, py)
    p.close()
    return p


def draw_star(c, x, y, r, mode="color", fill=GOLD):
    _style(c, mode, fill, fill if mode == "color" else INK, 0.8 if mode == "color" else 1.8)
    c.drawPath(star(c, x, y, r), fill=1, stroke=1)


def tree(c, x, y, w, h, mode="color", decorate=True, seed=1):
    """Tree with base at (x, y) centre bottom."""
    rnd = random.Random(seed)
    lw = 2.2 if mode == "line" else 0.8
    # trunk
    _style(c, mode, HexColor("#7A5232"), HexColor("#5C3D25"), lw)
    c.rect(x - w * 0.07, y, w * 0.14, h * 0.1, fill=1, stroke=1)
    top = y + h
    tiers = [(0.08, 1.00, 0.50), (0.32, 0.80, 0.70), (0.54, 0.58, 0.94)]
    cols = [PINE, PINE2, HexColor("#3E7356")]
    for i, (b, tw_f, apex_f) in enumerate(tiers):
        ty = y + h * b
        tw = w * tw_f
        apex = y + h * apex_f
        p = c.beginPath()
        p.moveTo(x - tw / 2, ty)
        p.curveTo(x - tw / 4, ty - h * 0.035, x + tw / 4, ty - h * 0.035, x + tw / 2, ty)
        p.lineTo(x, apex)
        p.close()
        _style(c, mode, cols[i], PINE, lw)
        c.drawPath(p, fill=1, stroke=1)
    if decorate:
        for i in range(9):
            frac = 0.14 + 0.66 * rnd.random()
            fy = y + h * frac
            span = (0.94 - frac) / 0.86 * w * 0.36
            fx = x + rnd.uniform(-span, span)
            _style(c, mode, [BERRY, GOLD, CREAM][i % 3], INK if mode == "line" else PINE, 1.4 if mode == "line" else 0.4)
            c.circle(fx, fy, w * 0.04, fill=1, stroke=1)
    draw_star(c, x, y + h * 0.94, w * 0.1, mode)


def ornament(c, x, y, r, mode="color", fill=BERRY, pattern="stripes"):
    lw = 2 if mode == "line" else 0.8
    _style(c, mode, GOLD, HexColor("#8E6F2A"), lw)
    c.rect(x - r * 0.22, y + r * 0.9, r * 0.44, r * 0.28, fill=1, stroke=1)
    c.setFillColor(white if mode == "line" else Color(0, 0, 0, 0))
    c.setStrokeColor(INK if mode == "line" else HexColor("#8E6F2A"))
    c.circle(x, y + r * 1.32, r * 0.14, fill=0, stroke=1)
    _style(c, mode, fill, fill if mode == "color" else INK, lw)
    c.circle(x, y, r, fill=1, stroke=1)
    c.saveState()
    p = c.beginPath()
    p.circle(x, y, r)
    c.clipPath(p, stroke=0, fill=0)
    c.setStrokeColor(CREAM if mode == "color" else INK)
    c.setFillColor(CREAM if mode == "color" else white)
    c.setLineWidth(r * 0.12 if mode == "color" else 1.6)
    if pattern == "stripes":
        for dy in (-0.45, 0, 0.45):
            if mode == "color":
                c.line(x - r, y + dy * r, x + r, y + dy * r)
            else:
                c.line(x - r, y + dy * r - r * 0.07, x + r, y + dy * r - r * 0.07)
                c.line(x - r, y + dy * r + r * 0.07, x + r, y + dy * r + r * 0.07)
    elif pattern == "zigzag":
        c.setLineWidth(r * 0.1 if mode == "color" else 1.6)
        for dy in (-0.3, 0.3):
            p2 = c.beginPath()
            p2.moveTo(x - r, y + dy * r)
            for k in range(9):
                p2.lineTo(x - r + (k + 1) * r * 2 / 9, y + dy * r + (r * 0.18 if k % 2 == 0 else -r * 0.18))
            c.drawPath(p2, fill=0, stroke=1)
    elif pattern == "dots":
        c.setLineWidth(1.4)
        for dx in (-0.6, -0.2, 0.2, 0.6):
            for dy in (-0.5, 0, 0.5):
                c.circle(x + dx * r + (0.2 * r if dy == 0 else 0), y + dy * r, r * 0.09, fill=1, stroke=1 if mode == "line" else 0)
    elif pattern == "star":
        c.restoreState()
        c.saveState()
        _style(c, mode, CREAM, CREAM, 1.6)
        c.drawPath(star(c, x, y, r * 0.5), fill=1, stroke=1)
    c.restoreState()


def gift(c, x, y, w, h, mode="color", fill=BERRY, ribbon=GOLD):
    lw = 2 if mode == "line" else 0.8
    _style(c, mode, fill, fill if mode == "color" else INK, lw)
    c.rect(x, y, w, h * 0.78, fill=1, stroke=1)
    c.rect(x - w * 0.05, y + h * 0.78, w * 1.1, h * 0.16, fill=1, stroke=1)
    _style(c, mode, ribbon, ribbon if mode == "color" else INK, lw)
    c.rect(x + w * 0.42, y, w * 0.16, h * 0.94, fill=1, stroke=1)
    # bow
    for side in (-1, 1):
        p = c.beginPath()
        bx, by = x + w / 2, y + h * 0.94
        p.moveTo(bx, by)
        p.curveTo(bx + side * w * 0.35, by + h * 0.28, bx + side * w * 0.05, by + h * 0.32, bx, by)
        c.drawPath(p, fill=1, stroke=1)


def candy_cane(c, x, y, h, mode="color", lw=None):
    lw = lw or h * 0.13
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x, y + h * 0.72)
    p.curveTo(x, y + h * 1.02, x + h * 0.42, y + h * 1.02, x + h * 0.42, y + h * 0.78)
    c.saveState()
    c.setLineCap(1)
    if mode == "color":
        c.setStrokeColor(white)
        c.setLineWidth(lw)
        c.drawPath(p, fill=0, stroke=1)
        c.setStrokeColor(BERRY)
        c.setLineCap(0)
        c.setDash(lw * 0.55, lw * 0.55)
        c.drawPath(p, fill=0, stroke=1)
        c.setDash()
        c.setLineCap(1)
        c.setStrokeColor(HexColor("#C9C2B4"))
        c.setLineWidth(0.6)
    else:
        c.setStrokeColor(INK)
        c.setLineWidth(lw)
        c.drawPath(p, fill=0, stroke=1)
        c.setStrokeColor(white)
        c.setLineWidth(lw - 3.2)
        c.drawPath(p, fill=0, stroke=1)
        c.setStrokeColor(INK)
        c.setLineCap(0)
        c.setLineWidth(1.4)
        c.setDash(1.4, lw * 0.6)
        c.setLineWidth(lw - 3.2)
        c.setStrokeColor(HexColor("#BDBDBD"))
        c.setDash(lw * 0.12, lw * 0.6)
        c.drawPath(p, fill=0, stroke=1)
        c.setDash()
    c.restoreState()


def bell(c, x, y, s, mode="color"):
    lw = 2 if mode == "line" else 0.8
    _style(c, mode, GOLD, HexColor("#8E6F2A"), lw)
    p = c.beginPath()
    p.moveTo(x - s * 0.5, y)
    p.curveTo(x - s * 0.38, y + s * 0.15, x - s * 0.36, y + s * 0.4, x - s * 0.32, y + s * 0.62)
    p.curveTo(x - s * 0.28, y + s * 0.95, x + s * 0.28, y + s * 0.95, x + s * 0.32, y + s * 0.62)
    p.curveTo(x + s * 0.36, y + s * 0.4, x + s * 0.38, y + s * 0.15, x + s * 0.5, y)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.circle(x, y - s * 0.06, s * 0.09, fill=1, stroke=1)


def snowman(c, x, y, s, mode="color"):
    """Snowman with base at (x, y); s = total height."""
    lw = 2.4 if mode == "line" else 1
    _style(c, mode, white, HexColor("#BFC9CF"), lw)
    r1, r2, r3 = s * 0.2, s * 0.15, s * 0.11
    c.circle(x, y + r1, r1, fill=1, stroke=1)
    c.circle(x, y + 2 * r1 + r2 * 0.85, r2, fill=1, stroke=1)
    hy = y + 2 * r1 + 2 * r2 * 0.85 + r3 * 0.8
    c.circle(x, hy, r3, fill=1, stroke=1)
    # hat
    _style(c, mode, PINE, PINE, lw)
    c.rect(x - r3 * 1.1, hy + r3 * 0.75, r3 * 2.2, r3 * 0.22, fill=1, stroke=1)
    c.rect(x - r3 * 0.72, hy + r3 * 0.97, r3 * 1.44, r3 * 1.05, fill=1, stroke=1)
    _style(c, mode, BERRY, BERRY, lw)
    c.rect(x - r3 * 0.72, hy + r3 * 0.97, r3 * 1.44, r3 * 0.25, fill=1, stroke=1)
    # scarf
    c.roundRect(x - r3 * 1.15, hy - r3 * 1.15, r3 * 2.3, r3 * 0.38, r3 * 0.15, fill=1, stroke=1)
    c.roundRect(x + r3 * 0.35, hy - r3 * 2.2, r3 * 0.42, r3 * 1.2, r3 * 0.12, fill=1, stroke=1)
    # face
    c.setFillColor(INK)
    for dx in (-0.38, 0.38):
        c.circle(x + dx * r3, hy + r3 * 0.2, r3 * 0.1, fill=1, stroke=0)
    _style(c, mode, HexColor("#E07A2E"), HexColor("#B95E1C"), lw * 0.6)
    p = c.beginPath()
    p.moveTo(x, hy + r3 * 0.05)
    p.lineTo(x + r3 * 0.85, hy - r3 * 0.12)
    p.lineTo(x, hy - r3 * 0.22)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(INK)
    for k in range(5):
        a = math.radians(225 + k * 22)
        c.circle(x + r3 * 0.55 * math.cos(a) + r3 * 0.05, hy - r3 * 0.05 + r3 * 0.5 * math.sin(a), r3 * 0.06, fill=1, stroke=0)
    # buttons
    for k in range(3):
        c.circle(x, y + 2 * r1 + r2 * (0.4 - 0.45 * k) + r2 * 0.5, r2 * 0.1, fill=1, stroke=0)
    # arms
    c.setStrokeColor(HexColor("#6B4A2E") if mode == "color" else INK)
    c.setLineWidth(max(2, s * 0.012))
    c.setLineCap(1)
    ay = y + 2 * r1 + r2
    for side in (-1, 1):
        x0 = x + side * r2 * 0.9
        x1 = x + side * r2 * 2.3
        c.line(x0, ay, x1, ay + r2 * 0.75)
        c.line(x1 - side * r2 * 0.3, ay + r2 * 0.55, x1 - side * r2 * 0.05, ay + r2 * 1.0)


def gingerbread(c, x, y, s, mode="color"):
    """Gingerbread figure centred on x with base at y; s = height."""
    lw = 2.4 if mode == "line" else 1
    _style(c, mode, HexColor("#B9773E"), HexColor("#8A5428"), lw)
    hr = s * 0.17
    hx, hy = x, y + s - hr
    body = c.beginPath()
    bw = s * 0.26
    # torso + legs + arms as one rounded polygon
    pts = [(-bw * 0.55, s * 0.62), (-bw * 1.55, s * 0.6), (-bw * 1.6, s * 0.46), (-bw * 0.6, s * 0.46),
           (-bw * 0.62, s * 0.3), (-bw * 1.05, s * 0.04), (-bw * 0.6, 0), (0, s * 0.22),
           (bw * 0.6, 0), (bw * 1.05, s * 0.04), (bw * 0.62, s * 0.3), (bw * 0.6, s * 0.46),
           (bw * 1.6, s * 0.46), (bw * 1.55, s * 0.6), (bw * 0.55, s * 0.62)]
    body.moveTo(x + pts[0][0], y + pts[0][1])
    for px, py in pts[1:]:
        body.lineTo(x + px, y + py)
    body.close()
    c.saveState()
    c.setLineJoin(1)
    if mode == "color":
        c.setLineWidth(s * 0.06)
        c.setStrokeColor(HexColor("#B9773E"))
        c.drawPath(body, fill=1, stroke=1)
    else:
        c.setLineWidth(s * 0.06)
        c.setStrokeColor(INK)
        c.drawPath(body, fill=0, stroke=1)
        c.setLineWidth(s * 0.06 - 4.4)
        c.setStrokeColor(white)
        c.drawPath(body, fill=1, stroke=1)
    c.restoreState()
    _style(c, mode, HexColor("#B9773E"), HexColor("#B9773E") if mode == "color" else INK, lw)
    c.circle(hx, hy, hr, fill=1, stroke=1)
    if mode == "line":  # hide neck seam
        c.setFillColor(white)
        c.rect(hx - bw * 0.45, hy - hr - 2, bw * 0.9, 6, fill=1, stroke=0)
    # face + icing
    c.setFillColor(INK)
    for dx in (-0.35, 0.35):
        c.circle(hx + dx * hr, hy + hr * 0.15, hr * 0.11, fill=1, stroke=0)
    c.setStrokeColor(white if mode == "color" else INK)
    c.setLineWidth(max(1.5, s * 0.012))
    c.arc(hx - hr * 0.45, hy - hr * 0.6, hx + hr * 0.45, hy - hr * 0.05, 200, 140)
    for k in range(3):
        _style(c, mode, BERRY if k != 1 else PINE2, INK if mode == "line" else white, 1.2)
        c.circle(x, y + s * (0.52 - k * 0.1), s * 0.03, fill=1, stroke=1)
    # icing zigzags on wrists/ankles
    c.setStrokeColor(white if mode == "color" else INK)
    c.setLineWidth(max(1.5, s * 0.01))
    for side in (-1, 1):
        zx = x + side * bw * 1.25
        p = c.beginPath()
        p.moveTo(zx - bw * 0.15 * side, y + s * 0.62)
        for k in range(5):
            p.lineTo(zx + (k % 2) * bw * 0.12 * side, y + s * (0.6 - k * 0.035))
        c.drawPath(p, fill=0, stroke=1)
        zx2 = x + side * bw * 0.72
        p = c.beginPath()
        p.moveTo(zx2 - bw * 0.25, y + s * 0.09 + (0 if side < 0 else 0))
        for k in range(5):
            p.lineTo(zx2 - bw * 0.25 + k * bw * 0.12, y + s * (0.09 + (k % 2) * 0.03))
        c.drawPath(p, fill=0, stroke=1)


def stocking(c, x, y, s, mode="color", fill=BERRY):
    """Stocking with top-left corner at (x, y + s)."""
    lw = 2.4 if mode == "line" else 0.8
    w = s * 0.42
    p = c.beginPath()
    p.moveTo(x, y + s * 0.82)
    p.lineTo(x, y + s * 0.32)
    p.curveTo(x, y + s * 0.02, x + w * 0.4, y, x + w * 1.25, y + s * 0.02)
    p.curveTo(x + w * 1.75, y + s * 0.04, x + w * 1.8, y + s * 0.28, x + w * 1.35, y + s * 0.34)
    p.lineTo(x + w, y + s * 0.42)
    p.lineTo(x + w, y + s * 0.82)
    p.close()
    _style(c, mode, fill, fill if mode == "color" else INK, lw)
    c.drawPath(p, fill=1, stroke=1)
    _style(c, mode, white, LINE if mode == "color" else INK, lw)
    c.roundRect(x - w * 0.1, y + s * 0.8, w * 1.2, s * 0.2, s * 0.06, fill=1, stroke=1)
    # heel/toe patches
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    _style(c, mode, GOLD, GOLD if mode == "color" else INK, lw * 0.8)
    c.circle(x + w * 1.6, y + s * 0.12, s * 0.17, fill=1, stroke=1)
    c.circle(x - s * 0.02, y + s * 0.14, s * 0.13, fill=1, stroke=1)
    c.setStrokeColor(CREAM if mode == "color" else INK)
    c.setLineWidth(s * 0.025 if mode == "color" else 1.6)
    for k in range(3):
        c.line(x, y + s * (0.5 + k * 0.1), x + w, y + s * (0.5 + k * 0.1))
    c.restoreState()


def mitten(c, x, y, s, mode="color", fill=PINE2):
    lw = 2.4 if mode == "line" else 0.8
    w = s * 0.62
    p = c.beginPath()
    p.moveTo(x, y + s * 0.2)
    p.lineTo(x, y + s * 0.75)
    p.curveTo(x, y + s * 1.05, x + w, y + s * 1.05, x + w, y + s * 0.75)
    p.lineTo(x + w, y + s * 0.58)
    p.curveTo(x + w * 1.45, y + s * 0.7, x + w * 1.5, y + s * 0.4, x + w, y + s * 0.38)
    p.lineTo(x + w, y + s * 0.2)
    p.close()
    _style(c, mode, fill, fill if mode == "color" else INK, lw)
    c.drawPath(p, fill=1, stroke=1)
    _style(c, mode, white, LINE if mode == "color" else INK, lw)
    c.roundRect(x - w * 0.08, y, w * 1.16, s * 0.22, s * 0.05, fill=1, stroke=1)
    snowflake(c, x + w / 2, y + s * 0.6, s * 0.16, CREAM if mode == "color" else INK, 1.4)


def santa_hat(c, x, y, s, mode="color"):
    lw = 2.4 if mode == "line" else 0.8
    p = c.beginPath()
    p.moveTo(x - s * 0.45, y + s * 0.12)
    p.curveTo(x - s * 0.35, y + s * 0.8, x + s * 0.1, y + s * 0.9, x + s * 0.55, y + s * 0.55)
    p.curveTo(x + s * 0.3, y + s * 0.55, x + s * 0.3, y + s * 0.3, x + s * 0.45, y + s * 0.12)
    p.close()
    _style(c, mode, BERRY, BERRY if mode == "color" else INK, lw)
    c.drawPath(p, fill=1, stroke=1)
    _style(c, mode, white, LINE if mode == "color" else INK, lw)
    c.roundRect(x - s * 0.52, y, s * 1.04, s * 0.2, s * 0.09, fill=1, stroke=1)
    c.circle(x + s * 0.58, y + s * 0.52, s * 0.1, fill=1, stroke=1)


def wreath(c, x, y, r, mode="color"):
    lw = 1.6
    rnd = random.Random(7)
    for i in range(22):
        a = i * 360 / 22
        rr = r * (0.92 + 0.08 * rnd.random())
        px, py = x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a))
        p, _, _ = leaf_path(c, px, py, r * 0.42, a + 100 + rnd.uniform(-15, 15), 0.45, 2)
        _style(c, mode, [PINE, PINE2, HexColor("#3E7356")][i % 3], PINE if mode == "color" else INK, 0.6 if mode == "color" else lw)
        c.drawPath(p, fill=1, stroke=1)
    for i in range(8):
        a = math.radians(i * 45 + 20)
        _style(c, mode, BERRY, BERRY if mode == "color" else INK, 0.6 if mode == "color" else lw)
        c.circle(x + r * 1.05 * math.cos(a), y + r * 1.05 * math.sin(a), r * 0.07, fill=1, stroke=1)
    # bow
    _style(c, mode, BERRY, BERRY if mode == "color" else INK, lw)
    bx, by = x, y - r * 1.15
    for side in (-1, 1):
        p = c.beginPath()
        p.moveTo(bx, by)
        p.curveTo(bx + side * r * 0.45, by + r * 0.35, bx + side * r * 0.5, by - r * 0.25, bx, by)
        c.drawPath(p, fill=1, stroke=1)
        p = c.beginPath()
        p.moveTo(bx, by)
        p.lineTo(bx + side * r * 0.3, by - r * 0.5)
        p.lineTo(bx + side * r * 0.12, by - r * 0.45)
        p.close()
        c.drawPath(p, fill=1, stroke=1)
    c.circle(bx, by, r * 0.08, fill=1, stroke=1)


# --------------------------------------------------------------------------- page chrome
def footer(c, W, H, product, page_no=None):
    c.setFont("Montserrat-Regular", 6.5)
    c.setFillColor(MUTED)
    txt = f"{product}  ·  {BRAND}  ·  personal use only"
    c.drawCentredString(W / 2, 22, txt)
    if page_no:
        c.drawRightString(W - 36, 22, str(page_no))


def sprig_divider(c, cx, y, w=150):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.line(cx - w / 2, y, cx - 16, y)
    c.line(cx + 16, y, cx + w / 2, y)
    holly(c, cx, y - 2, 13)


def page_header(c, W, H, title, kicker=None, top=None, title_size=30):
    """Classic header: holly divider, kicker label, big serif title. Returns y below header."""
    y = top or H - 54
    sprig_divider(c, W / 2, y, 170)
    if kicker:
        spaced(c, kicker, W / 2, y - 26, size=8.5)
        y -= 14
    size = fit_font(title, "Playfair-Bold", title_size, W - 100)
    c.setFont("Playfair-Bold", size)
    c.setFillColor(PINE)
    c.drawCentredString(W / 2, y - 26 - size * 0.8, title)
    return y - 26 - size * 0.8 - 18


def how_to_box(c, x, y_top, w, text, label="How to play"):
    """Soft cream box with rule text. Returns bottom y."""
    pad = 12
    st = ParagraphStyle("ht", parent=STY["small"], fontSize=8.8, leading=12.5)
    p = Paragraph(text, st)
    _, ph = p.wrap(w - pad * 2 - 70, 400)
    h = max(ph, 14) + pad * 2
    c.setFillColor(CREAM)
    c.setStrokeColor(CREAM2)
    c.setLineWidth(0.8)
    c.roundRect(x, y_top - h, w, h, 8, fill=1, stroke=1)
    c.setFillColor(BERRY)
    c.setFont("Montserrat-Bold", 7.2)
    c.drawString(x + pad, y_top - pad - 7, label.upper())
    p.drawOn(c, x + pad + 70, y_top - pad - ph)
    return y_top - h


def cut_grid(c, x, y, w, h, cols, rows):
    c.saveState()
    c.setStrokeColor(LINE)
    c.setDash(3, 3)
    c.setLineWidth(0.7)
    for i in range(cols + 1):
        c.line(x + i * w / cols, y, x + i * w / cols, y + h)
    for j in range(rows + 1):
        c.line(x, y + j * h / rows, x + w, y + j * h / rows)
    c.restoreState()


def rounded_card(c, x, y, w, h, fill=white, stroke=LINE, r=8, lw=0.9):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1)


def corner_sprigs(c, W, H, s=26):
    holly(c, 40, H - 40, s)
    holly(c, W - 40, 40, s)


def cover_page(c, W, H, title_lines, subtitle, badge, collection, items=None, accent=BERRY, scene=True):
    """Full-colour cover: pine background, cream card, gold details."""
    c.setFillColor(PINE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    rnd = random.Random(3)
    for _ in range(38):
        snowflake(c, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(5, 13), HexColor("#2E5442"), 0.9)
    m = 46
    c.setFillColor(CREAM)
    c.roundRect(m, m, W - 2 * m, H - 2 * m, 14, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.roundRect(m + 9, m + 9, W - 2 * m - 18, H - 2 * m - 18, 10, fill=0, stroke=1)
    holly(c, W / 2, H - 120, 30)
    spaced(c, collection, W / 2, H - 165, size=9, color=GOLD, spacing=3)
    y = H - 230
    for i, line in enumerate(title_lines):
        font = "Playfair-Black" if i == 0 else "Playfair-Italic"
        size = fit_font(line, font, 50 if i == 0 else 34, W - 2 * m - 70)
        c.setFont(font, size)
        c.setFillColor(PINE if i == 0 else accent)
        c.drawCentredString(W / 2, y, line)
        y -= size * 1.12
    y -= 8
    para(c, subtitle, m + 60, y, W - 2 * m - 120, ParagraphStyle("cs", parent=STY["bodyc"], fontSize=11.5, leading=17, textColor=INK))
    # little scene
    if scene:
        sy = 322
        avail = (y - 30) - sy
        sh = max(90, min(170, avail))
        tree(c, W / 2, sy, sh * 0.72, sh, seed=4)
        gift(c, W / 2 - sh * 0.62, sy, sh * 0.26, sh * 0.26, fill=BERRY)
        gift(c, W / 2 - sh * 0.36, sy, sh * 0.18, sh * 0.2, fill=PINE2, ribbon=CREAM)
        gift(c, W / 2 + sh * 0.3, sy, sh * 0.3, sh * 0.22, fill=GOLD, ribbon=BERRY)
        c.setStrokeColor(CREAM2)
        c.setLineWidth(1.2)
        c.line(W / 2 - sh * 0.9, sy, W / 2 + sh * 0.9, sy)
    # badge
    bx, by = W / 2, 250
    c.setFillColor(accent)
    c.circle(bx, by, 58, fill=1, stroke=0)
    c.setStrokeColor(CREAM)
    c.setLineWidth(1)
    c.circle(bx, by, 51, fill=0, stroke=1)
    big, small = badge
    c.setFillColor(CREAM)
    c.setFont("Playfair-Black", fit_font(big, "Playfair-Black", 40, 86))
    c.drawCentredString(bx, by - 4, big)
    spaced(c, small, bx, by - 24, size=7, color=CREAM, spacing=1.5)
    if items:
        para(c, "  ·  ".join(items), m + 50, 172, W - 2 * m - 100, STY["smallc"])
    spaced(c, BRAND, W / 2, m + 26, font="Montserrat-Medium", size=7, color=MUTED, spacing=2.5)


def terms_page(c, W, H, product, cross_sell):
    page_header(c, W, H, "Thank you & enjoy!", "a little note")
    y = H - 175
    txt = (f"Thank you so much for choosing <b>{product}</b>. We hope it brings a lot of laughter to your table this season. "
           "If it did, a quick review on Etsy means the world to a small shop like ours, and it helps other hosts find us.")
    y -= para(c, txt, 80, y, W - 160, "bodyc") + 26
    c.setFont("Montserrat-Bold", 9)
    c.setFillColor(BERRY)
    c.drawCentredString(W / 2, y, "PRINTING TIPS")
    y -= 10
    tips = ("Print at <b>100% / Actual size</b> (not 'fit to page') on US Letter or A4 paper. "
            "Cardstock (65-110 lb / 176-300 gsm) makes cards sturdier. "
            "Use the dashed lines as your cutting guide. A paper trimmer saves a lot of time.")
    y -= para(c, tips, 80, y, W - 160, "bodyc") + 26
    c.setFont("Montserrat-Bold", 9)
    c.setFillColor(BERRY)
    c.drawCentredString(W / 2, y, "TERMS OF USE")
    y -= 10
    terms = ("This file is for <b>personal and non-commercial use</b> (your home, classroom or office party). "
             "You may print as many copies as you need for your own events. Please do not resell, share or "
             "redistribute the digital files, in whole or in part. Because this is a digital download, no physical item will be shipped.")
    y -= para(c, terms, 80, y, W - 160, "bodyc") + 30
    if cross_sell:
        rounded_card(c, 90, y - 98, W - 180, 98, CREAM, CREAM2)
        spaced(c, "more from our holiday collection", W / 2, y - 24, size=7.5, color=GOLD)
        yy = y - 44
        for line in cross_sell:
            c.setFont("Playfair-Italic", 11.5)
            c.setFillColor(PINE)
            c.drawCentredString(W / 2, yy, line)
            yy -= 17
    c.setFont("GreatVibes", 30)
    c.setFillColor(BERRY)
    c.drawCentredString(W / 2, 90, "Merry Christmas")
    c.setFont("Montserrat-Regular", 7)
    c.setFillColor(MUTED)
    c.drawCentredString(W / 2, 64, f"© 2026 {BRAND}. All rights reserved.")


# --------------------------------------------------------------------------- emoji
_EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def emoji_png(ch):
    from PIL import Image, ImageDraw, ImageFont
    key = "-".join(f"{ord(x):x}" for x in ch)
    path = os.path.join(CACHE, f"emoji_{key}.png")
    if not os.path.exists(path):
        f = ImageFont.truetype(_EMOJI_FONT, 109)
        im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((30, 30), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        im.save(path)
    return path


def draw_emoji(c, ch, x, y, size):
    """Draw a single emoji centred at (x, y) with box size."""
    from PIL import Image
    path = emoji_png(ch)
    w, h = Image.open(path).size
    k = size / max(w, h)
    c.drawImage(path, x - w * k / 2, y - h * k / 2, w * k, h * k, mask="auto")


def emoji_row(c, seq, x, y, size, gap=4):
    """Draw a list of emoji centred horizontally at x."""
    total = len(seq) * size + (len(seq) - 1) * gap
    sx = x - total / 2 + size / 2
    for i, ch in enumerate(seq):
        draw_emoji(c, ch, sx + i * (size + gap), y, size)


def scramble(word, seed):
    rnd = random.Random(seed)
    out = []
    for w in word.split():
        letters = list(w.upper())
        for _ in range(20):
            rnd.shuffle(letters)
            if "".join(letters) != w.upper() or len(set(letters)) == 1:
                break
        out.append("".join(letters))
    return "  ".join(out)
