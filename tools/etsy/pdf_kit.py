"""Drawing kit for printable PDF products (US Letter + A4 from the same page functions).

A page function has the signature  page(k: Kit)  and draws inside k.frame (x, y, w, h)
below a header made with k.header(). Everything is vector, so prints stay sharp.
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
_FONTS = False


def _fonts():
    global _FONTS
    if not _FONTS:
        pdfmetrics.registerFont(TTFont("Mont", str(ROOT / "assets" / "fonts" / "Montserrat-SemiBold.ttf")))
        _FONTS = True


@dataclass(frozen=True)
class Theme:
    ink: str = "#3A3A3A"
    accent: str = "#8FA79A"      # headers, rules
    soft: str = "#EEF2EF"        # fills
    line: str = "#C9CFCB"        # writing lines


SIZES = {"Letter": LETTER, "A4": A4}
M = 36  # page margin (pt)


class Kit:
    def __init__(self, c: canvas.Canvas, size, theme: Theme, brand: str):
        self.c, self.W, self.H, self.t, self.brand = c, size[0], size[1], theme, brand
        self.frame = (M, M + 14, self.W - 2 * M, self.H - 2 * M - 14)

    # ---- primitives ----
    def color(self, hex_, stroke=False):
        (self.c.setStrokeColor if stroke else self.c.setFillColor)(HexColor(hex_))

    def text(self, x, y, s, size=10, font="Helvetica", color=None, align="left"):
        self.color(color or self.t.ink)
        self.c.setFont(font, size)
        {"left": self.c.drawString, "center": self.c.drawCentredString,
         "right": self.c.drawRightString}[align](x, y, s)

    def rect(self, x, y, w, h, fill=None, stroke=None, r=0, lw=0.8):
        if fill:
            self.color(fill)
        if stroke:
            self.color(stroke, True)
        self.c.setLineWidth(lw)
        if r:
            self.c.roundRect(x, y, w, h, r, fill=1 if fill else 0, stroke=1 if stroke else 0)
        else:
            self.c.rect(x, y, w, h, fill=1 if fill else 0, stroke=1 if stroke else 0)

    def hline(self, x1, x2, y, color=None, lw=0.6):
        self.color(color or self.t.line, True)
        self.c.setLineWidth(lw)
        self.c.line(x1, y, x2, y)

    def vline(self, x, y1, y2, color=None, lw=0.6):
        self.color(color or self.t.line, True)
        self.c.setLineWidth(lw)
        self.c.line(x, y1, x, y2)

    def checkbox(self, x, y, s=9):
        self.rect(x, y, s, s, stroke=self.t.accent, r=1.5, lw=0.9)

    def circle(self, x, y, r, fill=None, stroke=None, lw=0.8):
        if fill:
            self.color(fill)
        if stroke:
            self.color(stroke, True)
        self.c.setLineWidth(lw)
        self.c.circle(x, y, r, fill=1 if fill else 0, stroke=1 if stroke else 0)

    # ---- layout pieces ----
    def header(self, title, subtitle="", fields=("",)):
        """Big title top-left, optional 'Month: ____' style fields top-right. Shrinks self.frame."""
        x, y, w, h = self.frame
        top = y + h
        self.text(x, top - 26, title.upper(), 24, "Mont", self.t.accent)
        if subtitle:
            self.text(x, top - 42, subtitle, 9, "Helvetica-Oblique", "#8A8A8A")
        fx = x + w
        for f in reversed([f for f in fields if f]):
            fw = 120
            self.text(fx - fw, top - 22, f.upper(), 7, "Helvetica-Bold", "#8A8A8A")
            self.hline(fx - fw, fx, top - 32, self.t.accent)
            fx -= fw + 14
        cut = 58 if subtitle else 46
        self.frame = (x, y, w, h - cut)
        return self.frame

    def footer(self):
        self.text(self.W / 2, M - 4, self.brand, 7, "Helvetica", "#A0A0A0", "center")

    def section(self, x, y_top, w, label):
        """Small caps label bar; returns y below it."""
        self.rect(x, y_top - 16, w, 16, fill=self.t.accent, r=3)
        self.text(x + 8, y_top - 11.5, label.upper(), 8, "Helvetica-Bold", "#FFFFFF")
        return y_top - 16

    def lines(self, x, y_top, w, y_bottom, gap=18):
        y = y_top - gap
        while y >= y_bottom:
            self.hline(x, x + w, y)
            y -= gap

    def box(self, x, y, w, h, label=None, lined=True, gap=18):
        self.rect(x, y, w, h, stroke=self.t.line, r=6)
        top = y + h
        if label:
            self.text(x + 8, top - 13, label.upper(), 7.5, "Helvetica-Bold", self.t.accent)
            top -= 18
        if lined:
            self.lines(x + 8, top, w - 16, y + 6, gap)

    def checklist(self, x, y_top, w, y_bottom, items=(), gap=18, size=9):
        y = y_top - gap
        i = 0
        while y >= y_bottom:
            self.checkbox(x, y + 1, 8)
            self.hline(x + 14, x + w, y)
            if i < len(items):
                self.text(x + 16, y + 3, items[i], size)
            i += 1
            y -= gap

    def table(self, x, y_top, w, y_bottom, headers, widths=None, row_h=18, first_col=None, zebra=True,
              header_h=20, font_size=8):
        """Grid with a coloured header row. widths are fractions summing to 1. Returns row count."""
        n = len(headers)
        widths = widths or [1 / n] * n
        xs = [x]
        for f in widths:
            xs.append(xs[-1] + f * w)
        self.rect(x, y_top - header_h, w, header_h, fill=self.t.accent)
        for i, hd in enumerate(headers):
            self.text((xs[i] + xs[i + 1]) / 2, y_top - header_h + 7, hd.upper(), font_size - 0.5,
                      "Helvetica-Bold", "#FFFFFF", "center")
        y = y_top - header_h
        rows = 0
        while y - row_h >= y_bottom - 0.1:
            if zebra and rows % 2:
                self.rect(x, y - row_h, w, row_h, fill=self.t.soft)
            if first_col and rows < len(first_col):
                self.text(x + 5, y - row_h + 6, first_col[rows], font_size)
            self.hline(x, x + w, y - row_h)
            y -= row_h
            rows += 1
        for xx in xs[1:-1]:
            self.vline(xx, y, y_top - header_h)
        self.rect(x, y, w, y_top - y, stroke=self.t.line)
        return rows

    def month_grid(self, x, y, w, h, year, month, sunday=True, label_size=9):
        cal = calendar.Calendar(firstweekday=6 if sunday else 0)
        weeks = cal.monthdayscalendar(year, month)
        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"] if sunday else \
               ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        cw = w / 7
        hh = 18
        self.rect(x, y + h - hh, w, hh, fill=self.t.accent)
        for i, d in enumerate(days):
            self.text(x + cw * i + cw / 2, y + h - hh + 6, d, 8, "Helvetica-Bold", "#FFFFFF", "center")
        rh = (h - hh) / len(weeks)
        for r, wk in enumerate(weeks):
            for ci, d in enumerate(wk):
                cx, cy = x + ci * cw, y + h - hh - (r + 1) * rh
                self.rect(cx, cy, cw, rh, stroke=self.t.line, fill=None if d else self.t.soft, lw=0.6)
                if d:
                    self.text(cx + 5, cy + rh - 12, str(d), label_size, "Helvetica-Bold")

    def mini_month(self, x, y_top, w, year, month, sunday=True):
        cal = calendar.Calendar(firstweekday=6 if sunday else 0)
        self.text(x + w / 2, y_top - 12, calendar.month_name[month].upper(), 9, "Mont", self.t.accent, "center")
        days = "SMTWTFS" if sunday else "MTWTFSS"
        cw = w / 7
        for i, d in enumerate(days):
            self.text(x + cw * i + cw / 2, y_top - 26, d, 6.5, "Helvetica-Bold", "#8A8A8A", "center")
        for r, wk in enumerate(cal.monthdayscalendar(year, month)):
            for ci, d in enumerate(wk):
                if d:
                    self.text(x + cw * ci + cw / 2, y_top - 38 - r * 11, str(d), 7, "Helvetica", None, "center")

    def dots(self, x, y_top, w, y_bottom, step=14):
        self.color(self.t.line)
        yy = y_top - step / 2
        while yy > y_bottom:
            xx = x + step / 2
            while xx < x + w:
                self.c.circle(xx, yy, 0.7, fill=1, stroke=0)
                xx += step
            yy -= step


def cover(k: Kit, title: str, subtitle: str, year: str | None = None):
    k.rect(0, 0, k.W, k.H, fill=k.t.soft)
    k.rect(M, M, k.W - 2 * M, k.H - 2 * M, stroke=k.t.accent, lw=1.2, r=10)
    cy = k.H * 0.56
    if year:
        k.text(k.W / 2, cy + 70, year, 64, "Mont", k.t.accent, "center")
    words = title.upper().split()
    line1, line2 = (" ".join(words[: (len(words) + 1) // 2]), " ".join(words[(len(words) + 1) // 2:])) \
        if len(title) > 18 else (title.upper(), "")
    k.text(k.W / 2, cy, line1, 30, "Mont", k.t.ink, "center")
    if line2:
        k.text(k.W / 2, cy - 38, line2, 30, "Mont", k.t.ink, "center")
    k.hline(k.W / 2 - 40, k.W / 2 + 40, cy - (64 if line2 else 26), k.t.accent, 1.5)
    k.text(k.W / 2, cy - (88 if line2 else 50), subtitle, 11, "Helvetica-Oblique", "#7A7A7A", "center")


def render(path: Path, size_name: str, pages, theme: Theme, brand: str, title: str):
    """pages: list of callables page(k). Writes one PDF."""
    _fonts()
    size = SIZES[size_name]
    c = canvas.Canvas(str(path), pagesize=size)
    c.setTitle(title)
    c.setAuthor(brand)
    for p in pages:
        k = Kit(c, size, theme, brand)
        p(k)
        k.footer()
        c.showPage()
    c.save()
    return path
