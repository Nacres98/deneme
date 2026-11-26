#!/usr/bin/env python3
"""Generate the 2027 printable calendar products (PDF), page previews and upload ZIPs.

    python3 etsy/2027-calendar/build.py            # everything
    python3 etsy/2027-calendar/build.py --only 1   # one listing (1-4)

PDFs are rendered from HTML with the pre-installed Chromium (render.js), so fonts are
embedded and internal hyperlinks (listing 3) survive. Mockups: mockups.py.
"""
import argparse, calendar, datetime as dt, json, shutil, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
BUILD = ROOT / "build"
UPLOAD = ROOT / "upload"
YEAR = 2027

SIZES = {"A4": (297.0, 210.0), "US-Letter": (279.4, 215.9)}  # landscape w, h in mm
STARTS = {"Sunday": 6, "Monday": 0}
MONTHS = list(calendar.month_name)[1:]
DOW = {6: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
       0: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}


# ---------------------------------------------------------------- holidays (computed by rule)
def nth_weekday(y, m, weekday, n):
    """n-th weekday (0=Mon) of month; n=-1 for last."""
    days = [d for d in range(1, calendar.monthrange(y, m)[1] + 1) if dt.date(y, m, d).weekday() == weekday]
    return dt.date(y, m, days[n] if n < 0 else days[n - 1])


def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)


def us_holidays(y):
    D = dt.date
    h = {
        D(y, 1, 1): ("New Year's Day", True),
        nth_weekday(y, 1, 0, 3): ("MLK Jr. Day", True),
        D(y, 2, 14): ("Valentine's Day", False),
        nth_weekday(y, 2, 0, 3): ("Presidents' Day", True),
        nth_weekday(y, 3, 6, 2): ("Daylight Saving begins", False),
        D(y, 3, 17): ("St. Patrick's Day", False),
        easter(y): ("Easter Sunday", False),
        nth_weekday(y, 5, 6, 2): ("Mother's Day", False),
        nth_weekday(y, 5, 0, -1): ("Memorial Day", True),
        D(y, 6, 19): ("Juneteenth", True),
        nth_weekday(y, 6, 6, 3): ("Father's Day", False),
        D(y, 7, 4): ("Independence Day", True),
        nth_weekday(y, 9, 0, 1): ("Labor Day", True),
        nth_weekday(y, 10, 0, 2): ("Columbus Day", True),
        D(y, 10, 31): ("Halloween", False),
        nth_weekday(y, 11, 6, 1): ("Daylight Saving ends", False),
        D(y, 11, 11): ("Veterans Day", True),
        nth_weekday(y, 11, 3, 4): ("Thanksgiving", True),
        D(y, 12, 24): ("Christmas Eve", False),
        D(y, 12, 25): ("Christmas Day", True),
        D(y, 12, 31): ("New Year's Eve", False),
    }
    return dict(sorted(h.items()))


HOL = us_holidays(YEAR)


def weeks(m, fw):
    return calendar.Calendar(firstweekday=fw).monthdayscalendar(YEAR, m)


def is_weekend_col(i, fw):
    return (fw == 6 and i in (0, 6)) or (fw == 0 and i in (5, 6))


# ---------------------------------------------------------------- shared HTML bits
def font_css():
    faces = []
    for fam, stem, weights, italic in [
        ("Inter", "inter-latin-{w}-normal", (300, 400, 500, 600, 700), False),
        ("Fraunces", "fraunces-latin-{w}-normal", (300, 400, 500, 600), False),
        ("Fraunces", "fraunces-latin-{w}-italic", (300, 400, 500, 600), True),
        ("Cormorant", "cormorant-garamond-latin-{w}-normal", (300, 400, 500, 600), False),
        ("Cormorant", "cormorant-garamond-latin-{w}-italic", (300, 400, 500, 600), True),
    ]:
        for w in weights:
            faces.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{'italic' if italic else 'normal'};"
                         f"src:url('file://{FONTS / stem.format(w=w)}.woff2') format('woff2')}}")
    return "\n".join(faces)


BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;color:#1d1d1d;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Inter',sans-serif;font-feature-settings:'tnum' 1}
.page{width:var(--pw);height:var(--ph);overflow:hidden;position:relative;page-break-after:always;break-after:page;display:flex;flex-direction:column}
.page:last-child{page-break-after:auto;break-after:auto}
a{color:inherit;text-decoration:none}
.mini{display:flex;flex-direction:column}
.mini .t{font-weight:600;text-transform:uppercase;letter-spacing:.16em}
.mini .g{display:grid;grid-template-columns:repeat(7,1fr);text-align:center}
.mini .g span{display:block}
.mini .g .h{font-weight:600;color:#999}
.lines{display:flex;flex-direction:column}.lines i{flex:1;border-bottom:.45pt solid var(--lc)}
"""


def mini(m, fw, mark_holidays=False, show_title=True):
    hdr = "".join(f'<span class="h">{d[0]}</span>' for d in DOW[fw])
    cells = []
    for wk in weeks(m, fw):
        for i, d in enumerate(wk):
            cls = []
            if d and mark_holidays and dt.date(YEAR, m, d) in HOL and HOL[dt.date(YEAR, m, d)][1]:
                cls.append("hol")
            if is_weekend_col(i, fw):
                cls.append("we")
            cells.append(f'<span class="{" ".join(cls)}">{d or ""}</span>')
    for _ in range(6 - len(weeks(m, fw))):
        cells += ["<span>&nbsp;</span>"] * 7
    title = f'<div class="t">{MONTHS[m - 1]}</div>' if show_title else ""
    return f'<div class="mini">{title}<div class="g">{hdr}{"".join(cells)}</div></div>'


def doc(pages, css, pw, ph):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css()}
@page{{size:{pw}mm {ph}mm;margin:0}}
:root{{--pw:{pw}mm;--ph:{ph}mm}}
{BASE_CSS}
{css}
</style></head><body>{''.join(pages)}</body></html>"""


def month_grid(m, fw, cell_extra=None, weekend_cls=False, cls="grid"):
    wk = weeks(m, fw)
    out = [f'<div class="{cls}" style="grid-template-rows:auto repeat({len(wk)},1fr)">']
    for i, d in enumerate(DOW[fw]):
        out.append(f'<div class="dow{" we" if weekend_cls and is_weekend_col(i, fw) else ""}">{d}</div>')
    for w in wk:
        for i, d in enumerate(w):
            c = ["cell"]
            if not d:
                c.append("off")
            if weekend_cls and is_weekend_col(i, fw):
                c.append("we")
            extra = cell_extra(m, d) if (cell_extra and d) else ""
            out.append(f'<div class="{" ".join(c)}"><span class="n">{d or ""}</span>{extra}</div>')
    out.append("</div>")
    return "".join(out)


def hol_extra(m, d):
    h = HOL.get(dt.date(YEAR, m, d))
    return f'<span class="hl{" fed" if h[1] else ""}">{h[0]}</span>' if h else ""


# ---------------------------------------------------------------- listing 1: minimal monochrome
CSS1 = """
.page{padding:13mm 14mm 11mm}
.mhead{display:flex;align-items:flex-end;justify-content:space-between;padding-bottom:3mm;border-bottom:.7pt solid #111;margin-bottom:3mm}
.mhead .nm{font-weight:300;font-size:31pt;letter-spacing:-.02em;line-height:1}
.mhead .nm small{font-size:10pt;font-weight:500;letter-spacing:.2em;color:#888;margin-right:4mm;vertical-align:.9em}
.mhead .yr{font-weight:300;font-size:13pt;letter-spacing:.35em;color:#666}
.grid{flex:1;display:grid;grid-template-columns:repeat(7,1fr)}
.dow{font-size:6.5pt;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#777;padding:0 0 2mm 1.6mm}
.cell{border-top:.45pt solid #c9c9c9;border-left:.45pt solid #e3e3e3;padding:1.4mm 1.6mm}
.cell:nth-child(7n+1){border-left:none}
.n{font-size:9.5pt;font-weight:500}
.portrait .grid{flex:0 0 58%}
.notes{flex:1;margin-top:6mm;display:flex;flex-direction:column}
.lab{font-size:6.5pt;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:#777;margin-bottom:2mm}
.notes .lines{flex:1;--lh:7.5mm;--lc:#d6d6d6}
.cover{align-items:center;justify-content:center;text-align:center}
.cover .big{font-weight:200;font-size:150pt;letter-spacing:-.04em;line-height:.9}
.cover .sub{font-size:9pt;font-weight:500;letter-spacing:.6em;text-transform:uppercase;color:#666;margin-top:8mm}
.cover .rule{width:24mm;border-top:.7pt solid #111;margin:10mm auto 0}
.year .ttl{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:.7pt solid #111;padding-bottom:3mm;margin-bottom:7mm}
.year .ttl b{font-weight:300;font-size:31pt;letter-spacing:-.02em}
.year .ttl span{font-size:7pt;font-weight:600;letter-spacing:.3em;color:#888;text-transform:uppercase}
.ygrid{flex:1;display:grid;gap:6mm 10mm;align-content:space-between}
.ygrid .mini .t{font-size:8.5pt;margin-bottom:2.2mm}
.ygrid .mini .g{font-size:8pt;row-gap:1.4mm}
.ygrid .mini .g .h{font-size:6pt}
.portrait .ygrid .mini .g{font-size:9pt;row-gap:1.8mm}
"""


def pages1(fw, portrait):
    P = []
    P.append(f'<section class="page cover"><div class="big">{YEAR}</div><div class="sub">Calendar</div><div class="rule"></div></section>')
    cols = "repeat(3,1fr)" if portrait else "repeat(4,1fr)"
    P.append(f'<section class="page year{" portrait" if portrait else ""}"><div class="ttl"><b>{YEAR}</b><span>Year at a glance</span></div>'
             f'<div class="ygrid" style="grid-template-columns:{cols}">{"".join(mini(m, fw) for m in range(1, 13))}</div></section>')
    for m in range(1, 13):
        notes = '<div class="notes"><div class="lab">Notes</div><div class="lines">' + '<i></i>' * 14 + '</div></div>' if portrait else ""
        P.append(f'<section class="page{" portrait" if portrait else ""}"><div class="mhead">'
                 f'<div class="nm"><small>{m:02d}</small>{MONTHS[m - 1]}</div><div class="yr">{YEAR}</div></div>'
                 f'{month_grid(m, fw)}{notes}</section>')
    return P


# ---------------------------------------------------------------- listing 2: neutral tones + holidays
PALETTES = {
    "Sand":       ("#A9825C", "#F4EDE4", "#5B4636"),
    "Sage":       ("#6F8467", "#EDF1EA", "#3C4A37"),
    "Terracotta": ("#B5603F", "#F7EAE4", "#5E3122"),
    "Dusty-Blue": ("#5F7A96", "#E9EEF3", "#2F3F52"),
}
CSS2 = """
.page{padding:12mm 13mm 11mm;flex-direction:row;gap:9mm}
.side{width:60mm;display:flex;flex-direction:column}
.side .no{font-size:8pt;font-weight:600;letter-spacing:.3em;color:var(--acc)}
.side .nm{font-family:'Fraunces';font-style:italic;font-weight:400;font-size:34pt;line-height:1;color:var(--ink);margin:2mm 0 1mm}
.side .yr{font-size:9pt;font-weight:500;letter-spacing:.45em;color:#777}
.side .minis{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin:8mm 0 7mm;padding:4mm 0;border-top:.5pt solid var(--acc);border-bottom:.5pt solid var(--acc)}
.side .mini .t{font-size:5.6pt;color:var(--acc);margin-bottom:1.3mm}
.side .mini .g{font-size:5.4pt;row-gap:.6mm;color:#555}
.side .mini .g .h{font-size:4.6pt}
.lab{font-size:6.5pt;font-weight:600;letter-spacing:.25em;text-transform:uppercase;color:var(--acc);margin-bottom:2mm}
.side .lines{flex:1;--lh:7mm;--lc:#d9d4ce}
.main{flex:1;display:flex;flex-direction:column}
.grid{flex:1;display:grid;grid-template-columns:repeat(7,1fr);border:.6pt solid var(--acc);border-radius:2.5mm;overflow:hidden}
.dow{background:var(--acc);color:#fff;font-size:6.6pt;font-weight:600;letter-spacing:.2em;text-transform:uppercase;text-align:center;padding:2.2mm 0}
.cell{border-top:.45pt solid #ddd6cf;border-left:.45pt solid #ddd6cf;padding:1.5mm 1.8mm;display:flex;flex-direction:column;gap:.8mm}
.cell:nth-child(7n+1){border-left:none}
.cell.we{background:var(--soft)}
.cell.off{background:repeating-linear-gradient(135deg,transparent 0 2.2mm,#f1ede8 2.2mm 2.6mm)}
.n{font-size:9.5pt;font-weight:500;color:var(--ink)}
.hl{font-size:5.6pt;line-height:1.2;color:#8a8079;font-weight:500}
.hl.fed{color:var(--acc);font-weight:600}
.foot{display:flex;justify-content:space-between;font-size:5.6pt;color:#999;letter-spacing:.12em;margin-top:2mm}
.foot i{display:inline-block;width:2mm;height:2mm;border-radius:50%;background:var(--acc);vertical-align:-.3mm;margin-right:1mm}
.cover{align-items:center;justify-content:center;flex-direction:column}
.cover .disc{width:120mm;height:120mm;border-radius:50%;background:var(--soft);display:flex;flex-direction:column;align-items:center;justify-content:center}
.cover .big{font-family:'Fraunces';font-weight:300;font-size:92pt;color:var(--ink);line-height:1}
.cover .sub{font-family:'Fraunces';font-style:italic;font-size:17pt;color:var(--acc);margin-top:2mm}
.cover .tag{font-size:7pt;letter-spacing:.45em;text-transform:uppercase;color:#888;margin-top:7mm}
.year .ylist{width:62mm;display:flex;flex-direction:column}
.year h2{font-family:'Fraunces';font-weight:400;font-style:italic;font-size:30pt;color:var(--ink);line-height:1;margin-bottom:6mm}
.year .hrow{display:flex;justify-content:space-between;font-size:6.6pt;padding:1.25mm 0;border-bottom:.4pt solid #e4ded8;color:#444}
.year .hrow b{font-weight:600;color:var(--acc);width:15mm}
.year .hrow span{flex:1}
.year .ygrid{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:6mm 7mm;align-content:space-between}
.year .ygrid .mini .t{font-size:7pt;color:var(--acc);margin-bottom:1.6mm}
.year .ygrid .mini .g{font-size:8.2pt;row-gap:1.7mm}
.year .ygrid .mini .t{font-size:7.6pt}
.year .ygrid .mini .g .h{font-size:5.2pt}
.year .ygrid .mini .g .hol{background:var(--soft);color:var(--acc);font-weight:700;border-radius:50%}
"""


def pages2(fw, palette):
    acc, soft, ink = PALETTES[palette]
    style = f'style="--acc:{acc};--soft:{soft};--ink:{ink}"'
    P = [f'<section class="page cover" {style}><div class="disc"><div class="big">{YEAR}</div>'
         f'<div class="sub">monthly calendar</div></div><div class="tag">with US holidays &amp; notes</div></section>']
    hl = "".join(f'<div class="hrow"><b>{d.strftime("%b %d")}</b><span>{n}</span></div>' for d, (n, _) in HOL.items())
    P.append(f'<section class="page year" {style}><div class="ylist"><h2>{YEAR}</h2><div class="lab">Holidays &amp; dates</div>{hl}</div>'
             f'<div class="ygrid">{"".join(mini(m, fw, mark_holidays=True) for m in range(1, 13))}</div></section>')
    for m in range(1, 13):
        prev_m, next_m = (m - 2) % 12 + 1, m % 12 + 1
        side = (f'<div class="side"><div class="no">{m:02d} / 12</div><div class="nm">{MONTHS[m - 1]}</div><div class="yr">{YEAR}</div>'
                f'<div class="minis">{mini(prev_m, fw) if m > 1 else mini_dec_prev(fw)}{mini(next_m, fw) if m < 12 else mini_jan_next(fw)}</div>'
                f'<div class="lab">Notes</div><div class="lines">' + '<i></i>' * 14 + '</div></div>')
        main = (f'<div class="main">{month_grid(m, fw, hol_extra, weekend_cls=True)}'
                f'<div class="foot"><span><i></i>Federal holiday</span><span>{MONTHS[m - 1].upper()} {YEAR}</span></div></div>')
        P.append(f'<section class="page" {style}>{side}{main}</section>')
    return P


def _mini_other_year(y, m, fw):
    hdr = "".join(f'<span class="h">{d[0]}</span>' for d in DOW[fw])
    wk = calendar.Calendar(firstweekday=fw).monthdayscalendar(y, m)
    cells = "".join(f"<span>{d or ''}</span>" for w in wk for d in w) + "<span>&nbsp;</span>" * 7 * (6 - len(wk))
    return f'<div class="mini"><div class="t">{MONTHS[m - 1]} {y}</div><div class="g">{hdr}{cells}</div></div>'


def mini_dec_prev(fw):
    return _mini_other_year(YEAR - 1, 12, fw)


def mini_jan_next(fw):
    return _mini_other_year(YEAR + 1, 1, fw)


# ---------------------------------------------------------------- listing 3: hyperlinked digital + printable
CSS3 = """
.page{flex-direction:row;padding:0}
.body{flex:1;padding:11mm 9mm 10mm 13mm;display:flex;flex-direction:column}
.tabs{width:15mm;display:flex;flex-direction:column;padding:9mm 0;gap:.8mm}
.tabs a{flex:1;display:flex;align-items:center;justify-content:center;background:#EEEAE4;color:#6b645c;font-size:6pt;font-weight:600;letter-spacing:.12em;border-radius:2mm 0 0 2mm}
.tabs a.on{background:#2C2A28;color:#fff}
.tabs a.yr{background:#D9D2C8;color:#2C2A28}
.head{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:4mm}
.head .nm{font-family:'Cormorant';font-weight:500;font-size:38pt;line-height:.9;color:#2C2A28}
.head .nm em{font-style:italic;font-weight:400;color:#9a8f82;font-size:22pt;margin-left:3mm}
.head .nav{display:flex;gap:2mm}
.head .nav a{font-size:6.4pt;font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:1.6mm 3mm;border:.5pt solid #cfc7bc;border-radius:5mm;color:#6b645c}
.grid{flex:1;display:grid;grid-template-columns:repeat(7,1fr);gap:1.2mm}
.dow{font-size:6.2pt;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#9a8f82;text-align:center;padding-bottom:1mm}
.cell{background:#F7F5F1;border-radius:1.6mm;padding:1.6mm 2mm}
.cell.off{background:transparent;border:.4pt dashed #e3ddd5}
.n{font-size:9pt;font-weight:500;color:#2C2A28}
.plan{flex:1;display:grid;grid-template-columns:1fr 1fr 1.25fr;gap:7mm}
.box{display:flex;flex-direction:column}
.lab{font-size:6.5pt;font-weight:600;letter-spacing:.25em;text-transform:uppercase;color:#9a8f82;margin-bottom:2.5mm;padding-bottom:2mm;border-bottom:.6pt solid #2C2A28}
.box .lines{flex:1;--lh:7.2mm;--lc:#e3ddd5}
.todo{flex:1;display:flex;flex-direction:column}
.todo div{flex:1;border-bottom:.4pt solid #e3ddd5;display:flex;align-items:center}
.todo div:before{content:'';width:2.8mm;height:2.8mm;border:.6pt solid #b5ab9f;border-radius:.6mm}
.dots{flex:1;display:block}
.cover .body{align-items:center;justify-content:center;text-align:center}
.cover .big{font-family:'Cormorant';font-weight:300;font-size:120pt;line-height:.85;color:#2C2A28}
.cover .sub{font-family:'Cormorant';font-style:italic;font-size:20pt;color:#9a8f82;margin-top:4mm}
.cover .go{margin-top:10mm;font-size:7pt;font-weight:600;letter-spacing:.3em;text-transform:uppercase;padding:2.5mm 6mm;border:.6pt solid #2C2A28;border-radius:6mm}
.ygrid{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}
.ygrid a{background:#F7F5F1;border-radius:2mm;padding:3mm 3.5mm}
.ygrid .mini .t{font-family:'Cormorant';font-weight:600;font-size:12pt;text-transform:none;letter-spacing:0;color:#2C2A28;margin-bottom:1.2mm}
.ygrid .mini .g{font-size:6.4pt;row-gap:.7mm;color:#3d3a36}
.ygrid .mini .g .h{font-size:5pt;color:#9a8f82}
"""
TABS3 = [("y", "YEAR")] + [(f"m{m}", MONTHS[m - 1][:3].upper()) for m in range(1, 13)]


def tabs3(active):
    return '<nav class="tabs">' + "".join(
        f'<a href="#{k}" class="{"on" if k == active else ""}{" yr" if k == "y" and k != active else ""}">{lbl}</a>' for k, lbl in TABS3) + "</nav>"


def pages3(fw):
    P = [f'<section class="page cover" id="cover"><div class="body"><div class="big">{YEAR}</div>'
         f'<div class="sub">digital &amp; printable calendar</div><a class="go" href="#y">Open the year &rarr;</a></div>{tabs3("")}</section>']
    yg = "".join(f'<a href="#m{m}">{mini(m, fw)}</a>' for m in range(1, 13))
    P.append(f'<section class="page" id="y"><div class="body"><div class="head"><div class="nm">{YEAR}<em>year at a glance</em></div>'
             f'<div class="nav"><a href="#m1">Start: January &rarr;</a></div></div><div class="ygrid">{yg}</div></div>{tabs3("y")}</section>')
    for m in range(1, 13):
        nav = (f'<div class="nav">{"<a href=\"#m%d\">&larr; %s</a>" % (m - 1, MONTHS[m - 2][:3]) if m > 1 else ""}'
               f'<a href="#p{m}">Plan &amp; notes</a>{"<a href=\"#m%d\">%s &rarr;</a>" % (m + 1, MONTHS[m][:3]) if m < 12 else ""}</div>')
        P.append(f'<section class="page" id="m{m}"><div class="body"><div class="head"><div class="nm">{MONTHS[m - 1]}<em>{YEAR}</em></div>{nav}</div>'
                 f'{month_grid(m, fw)}</div>{tabs3(f"m{m}")}</section>')
        todo = "<div></div>" * 12
        P.append(f'<section class="page" id="p{m}"><div class="body"><div class="head"><div class="nm">{MONTHS[m - 1]}<em>plan</em></div>'
                 f'<div class="nav"><a href="#m{m}">&larr; Back to {MONTHS[m - 1]}</a></div></div>'
                 f'<div class="plan"><div class="box"><div class="lab">Goals</div><div class="lines">' + '<i></i>' * 14 + '</div></div>'
                 f'<div class="box"><div class="lab">To-do</div><div class="todo">{todo}</div></div>'
                 f'<div class="box"><div class="lab">Notes</div><svg class="dots" width="100%" height="100%"><defs><pattern id="dp" width="14.17" height="14.17" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="1" fill="#c9c0b4"/></pattern></defs><rect width="100%" height="100%" fill="url(#dp)"/></svg></div></div></div>{tabs3(f"m{m}")}</section>')
    return P


# ---------------------------------------------------------------- listing 4: one-page year at a glance
CSS4 = """
.page{padding:13mm 14mm 11mm}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:.8pt solid #111;padding-bottom:3mm;margin-bottom:6mm}
.top b{font-weight:200;font-size:46pt;letter-spacing:-.03em;line-height:.85}
.top span{font-size:7pt;font-weight:600;letter-spacing:.32em;color:#777;text-transform:uppercase}
.ygrid{flex:1;display:grid;gap:6mm 8mm;align-content:space-between}
.ygrid .mini .t{font-size:8pt;margin-bottom:2mm}
.ygrid .mini .g{font-size:7.8pt;row-gap:1.2mm}
.portrait .ygrid .mini .g{font-size:9pt;row-gap:1.6mm}
.ygrid .mini .g .h{font-size:5.8pt}
.ygrid .mini .g .hol{font-weight:700;text-decoration:underline;text-underline-offset:.6mm}
.hols{margin-top:6mm;padding-top:3mm;border-top:.5pt solid #ccc;columns:4;column-gap:6mm;font-size:5.8pt;color:#555;line-height:1.7}
.hols b{font-weight:600;color:#111;margin-right:1.5mm}
.portrait .hols{columns:3}
"""


def pages4(fw, portrait):
    cols = "repeat(3,1fr)" if portrait else "repeat(4,1fr)"
    hols = "".join(f"<div><b>{d.strftime('%b %d')}</b>{n}</div>" for d, (n, fed) in HOL.items() if fed)
    return [f'<section class="page{" portrait" if portrait else ""}"><div class="top"><b>{YEAR}</b><span>Year at a glance</span></div>'
            f'<div class="ygrid" style="grid-template-columns:{cols}">{"".join(mini(m, fw, mark_holidays=True) for m in range(1, 13))}</div>'
            f'<div class="hols">{hols}</div></section>']


# ---------------------------------------------------------------- how-to-print card (every listing)
GUIDE_CSS = """
.page{padding:22mm 22mm 18mm;justify-content:space-between}
h1{font-weight:300;font-size:28pt;letter-spacing:-.02em;margin-bottom:3mm}
.lead{font-size:10pt;color:#555;line-height:1.55;max-width:150mm}
h3{font-size:7pt;font-weight:600;letter-spacing:.28em;text-transform:uppercase;color:#888;margin:9mm 0 3mm}
ol,ul{padding-left:5mm;font-size:9.5pt;line-height:1.75;color:#333}
.foot{font-size:8.5pt;color:#777;line-height:1.6;border-top:.6pt solid #ddd;padding-top:5mm}
"""


def guide_pages(product, files_note):
    return [f"""<section class="page"><div><h1>Thank you!</h1>
<p class="lead">Your {product} is ready to print. Here is how to get the best result at home or at a print shop.</p>
<h3>What's inside</h3><ul>{files_note}</ul>
<h3>How to print</h3><ol>
<li>Unzip the folder, then open the PDF for your paper size (A4 or US Letter).</li>
<li>In the print dialog choose <b>Actual size / 100%</b>. If your printer trims the edges, use <b>Fit</b>.</li>
<li>Print one page first to check margins, then print the rest. Matte 120&ndash;200 gsm paper looks best.</li>
<li>Single pages or the whole year: pick a page range in the print dialog.</li></ol>
<h3>Good to know</h3><ul>
<li>This is a digital file. Nothing will be shipped.</li>
<li>Personal use only. Please don't resell or share the files.</li>
<li>Holiday dates follow US federal rules for {YEAR}.</li></ul></div>
<div class="foot">Questions or a problem with your file? Send us a message on Etsy and we'll help you quickly.<br>
If you enjoy your calendar, a short review means the world to a small shop. Thank you!</div></section>"""]


# ---------------------------------------------------------------- build
def dims(size, portrait):
    w, h = SIZES[size]
    return (h, w) if portrait else (w, h)


def plan():
    """(listing, pdf_name, pages_fn, css, pw, ph)."""
    from themes import pages5, CSS5, pages6, CSS6
    jobs = []
    for size in SIZES:
        for start, fw in STARTS.items():
            for orient in ("Landscape", "Portrait"):
                pw, ph = dims(size, orient == "Portrait")
                jobs.append((1, f"{size}/2027-Minimal-Calendar_{size}_{orient}_{start}-Start.pdf",
                             lambda fw=fw, o=orient: pages1(fw, o == "Portrait"), CSS1, pw, ph))
                jobs.append((4, f"{size}/2027-Year-at-a-Glance_{size}_{orient}_{start}-Start.pdf",
                             lambda fw=fw, o=orient: pages4(fw, o == "Portrait"), CSS4, pw, ph))
                jobs.append((5, f"{size}/2027-Boho-Calendar_{size}_{orient}_{start}-Start.pdf",
                             lambda fw=fw, o=orient: pages5(fw, o == "Portrait"), CSS5, pw, ph))
                jobs.append((6, f"{size}/2027-Seasonal-Calendar_{size}_{orient}_{start}-Start.pdf",
                             lambda fw=fw, o=orient: pages6(fw, o == "Portrait"), CSS6, pw, ph))
            pw, ph = dims(size, False)
            for pal in PALETTES:
                jobs.append((2, f"{pal}/2027-Calendar-Holidays_{pal}_{size}_{start}-Start.pdf",
                             lambda fw=fw, p=pal: pages2(fw, p), CSS2, pw, ph))
            jobs.append((3, f"{size}/2027-Hyperlinked-Calendar_{size}_{start}-Start.pdf",
                         lambda fw=fw: pages3(fw), CSS3, pw, ph))
    return jobs


LISTINGS = {
    1: ("01-minimal-monochrome", "2027 Minimal Calendar",
        "<li>8 PDFs: A4 + US Letter, portrait + landscape, Sunday + Monday start</li><li>14 pages each: cover, year at a glance, 12 months</li>"),
    2: ("02-neutral-holidays", "2027 Calendar with Holidays",
        "<li>16 PDFs: 4 colors (Sand, Sage, Terracotta, Dusty Blue), A4 + US Letter, Sunday + Monday start</li><li>14 pages each: cover, year + holiday list, 12 months with notes</li>"),
    3: ("03-hyperlinked-digital", "2027 Digital &amp; Printable Calendar",
        "<li>4 PDFs: A4 + US Letter, Sunday + Monday start (landscape)</li><li>26 pages: cover, clickable year, 12 months + 12 plan pages, side tabs</li><li>Works in GoodNotes, Notability, Xodo or any PDF app, and prints like a normal calendar</li>"),
    4: ("04-year-at-a-glance", "2027 Year at a Glance",
        "<li>8 one-page PDFs: A4 + US Letter, portrait + landscape, Sunday + Monday start</li><li>US federal holidays marked</li>"),
    5: ("05-boho", "2027 Boho Calendar",
        "<li>8 PDFs: A4 + US Letter, portrait + landscape, Sunday + Monday start</li><li>14 pages each: cover, year at a glance, 12 months, each with its own boho art and colors</li><li>US holidays printed in</li>"),
    6: ("06-seasonal", "2027 Seasonal Calendar",
        "<li>8 PDFs: A4 + US Letter, portrait + landscape, Sunday + Monday start</li><li>14 pages each: cover, year at a glance, 12 months, each with its own seasonal color and motif</li><li>US holidays printed in</li>"),
}


def run(only):
    jobs = [j for j in plan() if not only or j[0] in only]
    BUILD.mkdir(exist_ok=True)
    render = []
    for lst, name, fn, css, pw, ph in jobs:
        out = BUILD / LISTINGS[lst][0] / "pdf" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        html = out.with_suffix(".html")
        html.write_text(doc(fn(), css, pw, ph))
        render.append({"html": str(html), "pdf": str(out)})
    for lst in (only or LISTINGS):
        slug, product, note = LISTINGS[lst]
        for size in SIZES:
            pw, ph = dims(size, True)
            html = BUILD / slug / f"guide_{size}.html"
            html.write_text(doc(guide_pages(product, note), GUIDE_CSS, pw, ph))
            render.append({"html": str(html), "pdf": str(BUILD / slug / f"READ-ME-How-to-Print_{size}.pdf")})
    jf = BUILD / "jobs.json"
    jf.write_text(json.dumps(render))
    subprocess.run(["node", str(ROOT / "render.js"), str(jf)], check=True, cwd=ROOT)
    for f in BUILD.rglob("*.html"):
        f.unlink()
    package(only or LISTINGS)


def package(lists):
    """Etsy allows max 5 files (20 MB each) per digital listing -> zip per size / colour."""
    for lst in lists:
        slug = LISTINGS[lst][0]
        src = BUILD / slug / "pdf"
        dst = UPLOAD / slug / "files"
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for group in sorted(p for p in src.iterdir() if p.is_dir()):
            size_guides = [BUILD / slug / f"READ-ME-How-to-Print_{s}.pdf" for s in SIZES if s in group.name] or \
                          [BUILD / slug / "READ-ME-How-to-Print_US-Letter.pdf"]
            prefix = {1: "2027-Minimal-Calendar", 2: "2027-Calendar-Holidays", 3: "2027-Hyperlinked-Calendar",
                      4: "2027-Year-at-a-Glance", 5: "2027-Boho-Calendar", 6: "2027-Seasonal-Calendar"}[lst]
            zp = dst / f"{prefix}_{group.name}.zip"
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                for p in sorted(group.glob("*.pdf")):
                    z.write(p, f"{zp.stem}/{p.name}")
                for g in size_guides:
                    z.write(g, f"{zp.stem}/{g.name}")
        if lst == 2:  # one guide alongside the 4 colour zips (5 files total)
            shutil.copy(BUILD / slug / "READ-ME-How-to-Print_US-Letter.pdf", dst / "READ-ME-How-to-Print.pdf")
        n = len(list(dst.iterdir()))
        assert n <= 5, f"{slug}: {n} files > Etsy limit of 5"
        print(slug, [f"{p.name} {p.stat().st_size // 1024} KB" for p in sorted(dst.iterdir())])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, nargs="*")
    run(ap.parse_args().only)
