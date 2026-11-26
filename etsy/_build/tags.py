"""Ribbon & Pine gift tags (editable + print-and-write)."""
import math
import random

from reportlab.lib.colors import white, HexColor, Color
from reportlab.pdfgen import canvas

from lib import *  # noqa
import games as G

NAME = "Ribbon & Pine Gift Tags"


class Fields:
    def __init__(self, c, editable):
        self.c, self.editable, self.n = c, editable, 0

    def add(self, x, y, w, h, color=INK, tip="Name"):
        if not self.editable:
            return
        self.n += 1
        self.c.acroForm.textfield(name=f"tag{self.n}", tooltip=tip, x=x, y=y, width=w, height=h,
                                  borderWidth=0, fillColor=None, borderColor=None, textColor=color,
                                  fontName="Helvetica", fontSize=0, forceBorder=False)


def tag_shape(c, x, y, w, h):
    n = h * 0.22
    p = c.beginPath()
    p.moveTo(x + n, y)
    p.lineTo(x + w - 8, y)
    p.arcTo(x + w - 16, y, x + w, y + 16, -90, 90)
    p.lineTo(x + w, y + h - 8)
    p.arcTo(x + w - 16, y + h - 16, x + w, y + h, 0, 90)
    p.lineTo(x + n, y + h)
    p.lineTo(x, y + h - n)
    p.lineTo(x, y + n)
    p.close()
    return p


def to_from(c, F, x, y, w, color=INK, line=LINE, size=9):
    c.setFont("Montserrat-SemiBold", size)
    c.setFillColor(color)
    for i, lab in enumerate(("To:", "From:")):
        yy = y - i * 24
        c.drawString(x, yy, lab)
        lw = pdfmetrics.stringWidth(lab, "Montserrat-SemiBold", size)
        c.setStrokeColor(line)
        c.setLineWidth(0.8)
        c.line(x + lw + 6, yy - 2, x + w, yy - 2)
        F.add(x + lw + 6, yy - 1, w - lw - 6, 15, color, lab)


def plaid(c, x, y, w, h):
    c.setFillColor(BERRY)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.saveState()
    for k, (col, a, step, lw) in enumerate([(PINE, 0.55, 28, 10), (HexColor("#7E2420"), 0.5, 28, 4), (CREAM, 0.6, 28, 1.2)]):
        c.setStrokeColor(col)
        c.setStrokeAlpha(a)
        c.setLineWidth(lw)
        off = k * 9
        xx = x - 20 + off
        while xx < x + w + 20:
            c.line(xx, y, xx, y + h)
            xx += step
        yy = y - 20 + off
        while yy < y + h + 20:
            c.line(x, yy, x + w, yy)
            yy += step
    c.restoreState()


def draw_tag(c, F, x, y, w, h, design, variant):
    p = tag_shape(c, x, y, w, h)
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    hole = (x + h * 0.2, y + h / 2)
    tx = x + h * 0.5  # text start
    msg = ["Merry Christmas", "Happy Holidays", "Season's Greetings", "Merry & Bright"][variant % 4]
    if design == "pine":
        c.setFillColor(white)
        c.rect(x, y, w, h, fill=1, stroke=0)
        holly(c, x + w - 34, y + h - 26, 22)
        snowflake(c, x + w - 30, y + 26, 10, SAGE)
        title_col, txt_col, line_col = BERRY, INK, LINE
    elif design == "stripe":
        c.setFillColor(CREAM)
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setStrokeColor(BERRY)
        c.setLineWidth(9)
        k = x - h
        while k < x + w * 0.3:
            c.line(k, y, k + h, y + h)
            k += 22
        c.setFillColor(CREAM)
        c.rect(x + w * 0.3, y, w * 0.7, h, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.4)
        c.line(x + w * 0.3, y, x + w * 0.3, y + h)
        tx = x + w * 0.34
        title_col, txt_col, line_col = PINE, INK, CREAM2
    elif design == "midnight":
        c.setFillColor(PINE)
        c.rect(x, y, w, h, fill=1, stroke=0)
        rnd = random.Random(variant + 3)
        for _ in range(9):
            snowflake(c, x + rnd.uniform(w * 0.82, w - 8), y + rnd.uniform(8, h - 40), rnd.uniform(4, 8), HexColor("#4C7A60"), 0.9)
        draw_star(c, x + w - 30, y + h - 26, 11)
        title_col, txt_col, line_col = GOLD, CREAM, HexColor("#5E8A70")
    elif design == "kraft":
        c.setFillColor(KRAFT)
        c.rect(x, y, w, h, fill=1, stroke=0)
        tree(c, x + w - 42, y + 18, 46, h * 0.62, decorate=True, seed=variant + 1)
        title_col, txt_col, line_col = PINE, HexColor("#3A2C1E"), HexColor("#B99A6E")
    elif design == "plaid":
        plaid(c, x, y, w, h)
        c.setFillColor(CREAM)
        c.roundRect(x + h * 0.42, y + 12, w - h * 0.42 - 14, h - 24, 8, fill=1, stroke=0)
        tx = x + h * 0.42 + 12
        title_col, txt_col, line_col = BERRY, INK, CREAM2
    elif design == "ornament":
        c.setFillColor(CREAM)
        c.rect(x, y, w, h, fill=1, stroke=0)
        for i, (ox, col, pat) in enumerate([(0.82, BERRY, "stripes"), (0.89, PINE2, "dots"), (0.95, GOLD, "zigzag")]):
            oy = y + h * (0.55 if i != 1 else 0.42)
            c.setStrokeColor(GOLD)
            c.setLineWidth(0.8)
            c.line(x + w * ox, oy + 18, x + w * ox, y + h)
            ornament(c, x + w * ox, oy, 8, fill=col, pattern=pat)
        title_col, txt_col, line_col = PINE, INK, CREAM2
        tx = x + h * 0.36
    c.restoreState()
    # outline + hole
    c.setStrokeColor(LINE if design in ("pine", "stripe", "ornament") else Color(0, 0, 0, 0.15))
    c.setLineWidth(0.8)
    c.drawPath(p, fill=0, stroke=1)
    c.setFillColor(white)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.circle(*hole, 6, fill=1, stroke=1)
    # message
    area = (x + w - 60) - tx if design in ("pine", "kraft", "midnight") else (x + w * (0.78 if design == "ornament" else 1) - 14) - tx
    size = fit_font(msg, "GreatVibes", 26, area)
    c.setFont("GreatVibes", size)
    c.setFillColor(title_col)
    c.drawString(tx, y + h * 0.62, msg)
    to_from(c, F, tx, y + h * 0.42, min(area, w * 0.5), txt_col, line_col)


def tag_sheet(ctx, F, design, title):
    c, W, H = ctx.c, ctx.W, ctx.H
    spaced(c, title, W / 2, H - 38, size=8, color=GOLD)
    cols, rows = 2, 4
    gx, gy = 34, 44
    gw, gh = W - 68, H - 44 - 58
    cw, ch = gw / cols, gh / rows
    for i in range(cols * rows):
        col, r = i % cols, i // cols
        draw_tag(c, F, gx + col * cw + 8, gy + gh - (r + 1) * ch + 8, cw - 16, ch - 16, design, i)
    ctx.end()


def round_sheet(ctx, F):
    c, W, H = ctx.c, ctx.W, ctx.H
    spaced(c, "round tags · cut along the circles", W / 2, H - 38, size=8, color=GOLD)
    cols, rows = 3, 4
    gw, gh = W - 60, H - 100
    cw, ch = gw / cols, gh / rows
    r = min(cw, ch) / 2 - 10
    msgs = ["Ho Ho Ho", "Joy", "Noel", "Merry & Bright", "Peace", "Let It Snow"]
    styles = [(PINE, GOLD, CREAM), (CREAM, BERRY, INK), (BERRY, CREAM, CREAM), (KRAFT, PINE, HexColor("#3A2C1E"))]
    for i in range(cols * rows):
        col, row = i % cols, i // cols
        cx = 30 + col * cw + cw / 2
        cy = 50 + gh - row * ch - ch / 2
        bg, tc, lc = styles[i % 4]
        c.setFillColor(bg)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.8)
        c.circle(cx, cy, r, fill=1, stroke=1)
        c.setStrokeColor(GOLD)
        c.circle(cx, cy, r - 6, fill=0, stroke=1)
        c.setFillColor(white)
        c.circle(cx, cy + r - 16, 4.5, fill=1, stroke=1)
        m = msgs[i % len(msgs)]
        c.setFont("GreatVibes", fit_font(m, "GreatVibes", 28, r * 1.5))
        c.setFillColor(tc)
        c.drawCentredString(cx, cy + r * 0.12, m)
        c.setFont("Montserrat-SemiBold", 7.5)
        c.setFillColor(lc)
        c.drawString(cx - r * 0.62, cy - r * 0.3, "To:")
        c.drawString(cx - r * 0.62, cy - r * 0.55, "From:")
        c.setStrokeColor(lc)
        c.setLineWidth(0.6)
        c.line(cx - r * 0.62 + 16, cy - r * 0.3 - 2, cx + r * 0.62, cy - r * 0.3 - 2)
        c.line(cx - r * 0.62 + 26, cy - r * 0.55 - 2, cx + r * 0.62, cy - r * 0.55 - 2)
        F.add(cx - r * 0.62 + 16, cy - r * 0.3 - 1, r * 1.24 - 16, 12, lc)
        F.add(cx - r * 0.62 + 26, cy - r * 0.55 - 1, r * 1.24 - 26, 12, lc)
    ctx.end()


def santa_sheet(ctx, F):
    c, W, H = ctx.c, ctx.W, ctx.H
    spaced(c, "special delivery from the north pole", W / 2, H - 38, size=8, color=GOLD)
    cols, rows = 2, 4
    gx, gy = 34, 44
    gw, gh = W - 68, H - 44 - 58
    cw, ch = gw / cols, gh / rows
    for i in range(cols * rows):
        col, r = i % cols, i // cols
        x, y, w, h = gx + col * cw + 8, gy + gh - (r + 1) * ch + 8, cw - 16, ch - 16
        c.setFillColor(CREAM)
        c.setStrokeColor(BERRY)
        c.setLineWidth(1.2)
        c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
        c.setDash(3, 2)
        c.roundRect(x + 6, y + 6, w - 12, h - 12, 7, fill=0, stroke=1)
        c.setDash()
        if i % 2 == 0:
            spaced(c, "official · north pole post", x + w / 2, y + h - 24, size=6.5, color=BERRY, spacing=1.6)
            c.setFont("Playfair-Black", 18)
            c.setFillColor(PINE)
            c.drawCentredString(x + w / 2, y + h - 50, "From Santa")
            c.setFont("Montserrat-SemiBold", 9)
            c.setFillColor(INK)
            c.drawString(x + 22, y + 34, "Special delivery for:")
            c.setStrokeColor(LINE)
            c.line(x + 120, y + 32, x + w - 22, y + 32)
            F.add(x + 120, y + 33, w - 142, 15)
            santa_hat(c, x + 34, y + h - 50, 30)
        else:
            c.setFont("Playfair-Black", fit_font("Do Not Open", "Playfair-Black", 22, w - 60))
            c.setFillColor(BERRY)
            c.drawCentredString(x + w / 2, y + h - 46, "Do Not Open")
            c.setFont("Playfair-Italic", 14)
            c.setFillColor(PINE)
            c.drawCentredString(x + w / 2, y + h - 68, "until December 25th")
            c.setFont("Montserrat-SemiBold", 9)
            c.setFillColor(INK)
            c.drawString(x + 22, y + 26, "For:")
            c.setStrokeColor(LINE)
            c.line(x + 46, y + 24, x + w - 22, y + 24)
            F.add(x + 46, y + 25, w - 68, 15)
        # nice list stamp
        sx, sy = x + w - 40, y + h - 40 if i % 2 == 0 else y + 46
        if i % 2 == 0:
            c.saveState()
            c.translate(sx, sy)
            c.rotate(-14)
            c.setStrokeColor(BERRY)
            c.setLineWidth(1.4)
            c.circle(0, 0, 22, fill=0, stroke=1)
            c.circle(0, 0, 18, fill=0, stroke=1)
            c.setFont("Montserrat-Bold", 5.6)
            c.setFillColor(BERRY)
            c.drawCentredString(0, 2, "NICE LIST")
            c.drawCentredString(0, -6, "APPROVED")
            c.restoreState()
    ctx.end()


def how_page(ctx, editable):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "How to Use Your Tags", "ribbon & pine")
    steps = []
    if editable:
        steps.append("<b>Type the names first (optional).</b> Open this PDF in the free Adobe Acrobat Reader (desktop or phone) and click the To and From lines. Type the names, then print. Other PDF apps may not show the typing fields.")
    else:
        steps.append("<b>This is the print-and-write version.</b> Print the sheets and write the names by hand. Gold or white gel pens look lovely on the dark tags!")
    steps += ["<b>Print at 100% / Actual size</b> on US Letter or A4 paper. White cardstock (65-110 lb / 176-300 gsm) gives the best result.",
              "<b>Cut out the tags</b> with scissors or a paper trimmer, following the outlines.",
              "<b>Punch the hole</b> on the gold circle with a hole punch and tie with twine or ribbon. Or just tape the tag on.",
              "<b>Print as many as you like</b> for your own gifts, every year."]
    for i, s in enumerate(steps):
        c.setFillColor(BERRY)
        c.circle(86, y - 9, 11, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Montserrat-Bold", 10)
        c.drawCentredString(86, y - 12.5, str(i + 1))
        y -= max(para(c, s, 110, y, W - 190, "body"), 22) + 16
    y -= 10
    rounded_card(c, 90, y - 120, W - 180, 120, CREAM, CREAM2, 12)
    spaced(c, "what's inside", W / 2, y - 24, size=8)
    items = ["Pine & Berry · 8 tags", "Candy Stripe · 8 tags", "Midnight Snow · 8 tags", "Kraft Tree · 8 tags",
             "Holiday Plaid · 8 tags", "Ornament Glow · 8 tags", "Round Tags · 12 tags", "From Santa & Do Not Open · 8 tags"]
    for i, it in enumerate(items):
        col, r = i % 2, i // 2
        c.setFont("Montserrat-Medium", 9.5)
        c.setFillColor(INK)
        c.drawCentredString(W / 2 + (col - 0.5) * (W - 240) / 2, y - 48 - r * 18, it)
    ctx.end()


def build_tags(W, H, path, editable):
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(NAME + (" (Editable)" if editable else " (Print & Write)"))
    c.setAuthor(BRAND)
    ctx = G.Ctx(c, W, H, NAME)
    F = Fields(c, editable)
    cover_page(c, W, H, ["Ribbon & Pine", "Gift Tags"],
               "68 printable Christmas gift tags in 8 designs. " + ("Type the names right into the PDF, then print." if editable else "Print, write and tie on."),
               ("68", "gift tags"), "the holiday paper collection",
               ["6 tag designs", "round tags", "From Santa tags", "editable To/From" if editable else "print & write"])
    ctx.end(footer_on=False)
    how_page(ctx, editable)
    for design, title in [("pine", "pine & berry"), ("stripe", "candy stripe"), ("midnight", "midnight snow"),
                          ("kraft", "kraft tree"), ("plaid", "holiday plaid"), ("ornament", "ornament glow")]:
        tag_sheet(ctx, F, design, title)
    round_sheet(ctx, F)
    santa_sheet(ctx, F)
    terms_page(c, W, H, NAME, ["Merry Mayhem Party Pack · 21 games", "Little Elf Workshop · kids activities", "Jingle Grid Bingo · 60 cards"])
    ctx.end(footer_on=False)
    c.save()
    return F.n
