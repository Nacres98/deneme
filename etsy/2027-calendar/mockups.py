#!/usr/bin/env python3
"""Etsy listing images (2700x2025, 4:3) for the four 2027 calendar listings.
Run after build.py:  python3 etsy/2027-calendar/mockups.py
Keep key content inside the centre square: Etsy crops thumbnails."""
import json, subprocess
from pathlib import Path
from build import ROOT, BUILD, UPLOAD, LISTINGS, PALETTES, font_css

W, H = 2700, 2025
PAGES = BUILD / "pages"


def pdf(lst, rel):
    return BUILD / LISTINGS[lst][0] / "pdf" / rel


def page_png(src, n, key, dpi=150):
    """Render page n of a PDF to PNG (cached)."""
    out = PAGES / f"{key}-p{n}"
    png = Path(f"{out}.png")
    if not png.exists():
        PAGES.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", "-f", str(n), "-l", str(n), str(src), str(out)], check=True)
    return png


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:2700px;height:2025px;overflow:hidden;position:relative;font-family:'Inter';background:var(--bg);color:var(--ink)}
.p{position:absolute;box-shadow:0 30px 60px rgba(40,30,20,.18),0 6px 14px rgba(40,30,20,.10);background:#fff}
.h1{position:absolute;font-family:'Fraunces';font-weight:400;font-size:118px;line-height:1.02;letter-spacing:-.02em}
.h1 em{font-style:italic;color:var(--acc)}
.kick{position:absolute;font-size:34px;font-weight:600;letter-spacing:.32em;text-transform:uppercase;color:var(--acc)}
.chips{position:absolute;display:flex;flex-wrap:wrap;gap:22px}
.chip{font-size:38px;font-weight:500;padding:20px 38px;border-radius:60px;background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.06)}
.chip.d{background:var(--ink);color:#fff}
.lab{position:absolute;font-size:40px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;text-align:center}
.lab small{display:block;font-size:30px;font-weight:400;letter-spacing:.04em;text-transform:none;color:#777;margin-top:10px}
.list{position:absolute;font-size:46px;line-height:1.9}
.list div:before{content:'';display:inline-block;width:22px;height:22px;border-radius:50%;background:var(--acc);margin-right:28px;vertical-align:4px}
.step{position:absolute;width:700px;text-align:center}
.step .num{width:200px;height:200px;border-radius:50%;background:#fff;margin:0 auto 50px;display:flex;align-items:center;justify-content:center;font-family:'Fraunces';font-size:96px;color:var(--acc);box-shadow:0 10px 30px rgba(0,0,0,.07)}
.step b{display:block;font-size:56px;font-weight:600;margin-bottom:22px}
.step span{font-size:40px;color:#666;line-height:1.45}
.tablet{position:absolute;background:#1f1f22;border-radius:70px;padding:56px;box-shadow:0 40px 80px rgba(0,0,0,.25)}
.tablet img{display:block;border-radius:10px}
.call{position:absolute;z-index:5;font-size:40px;font-weight:600;background:var(--ink);color:#fff;padding:22px 36px;border-radius:50px}
.dot{position:absolute;width:44px;height:44px;border-radius:50%;border:8px solid var(--ink);background:#fff}
.sw{display:inline-block;width:70px;height:70px;border-radius:50%;margin-right:22px;vertical-align:middle;border:6px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,.12)}
.zoom{position:absolute;overflow:hidden;border-radius:30px;box-shadow:0 30px 60px rgba(40,30,20,.2);background:#fff}
.zoom img{position:absolute}
"""


def img(src, x, y, w, rot=0, z=1, cls="p"):
    return f'<img class="{cls}" src="file://{src}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);z-index:{z}">'


def scene(body, bg, acc, ink="#1d1d1d"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}{CSS}'
            f'body{{--bg:{bg};--acc:{acc};--ink:{ink}}}</style></head><body>{body}</body></html>')


def steps(acc_word):
    s = [("1", "Buy", "Checkout on Etsy.<br>No shipping, no waiting."),
         ("2", "Download", f"Get your {acc_word} files<br>instantly from Purchases."),
         ("3", "Print or use", "Print at home or a print<br>shop, any time.")]
    return ('<div class="kick" style="left:0;right:0;top:330px;text-align:center">Instant digital download</div>'
            '<div class="h1" style="left:0;right:0;top:420px;text-align:center">How it <em>works</em></div>'
            + "".join(f'<div class="step" style="left:{200 + i * 800}px;top:860px"><div class="num">{n}</div><b>{t}</b><span>{d}</span></div>'
                      for i, (n, t, d) in enumerate(s))
            + '<div class="lab" style="left:0;right:0;top:1700px;font-size:34px;color:#777">This is a digital product &middot; nothing will be shipped</div>')


def listing1():
    L = lambda o, s="Sunday", size="A4": pdf(1, f"{size}/2027-Minimal-Calendar_{size}_{o}_{s}-Start.pdf")
    k = lambda *a: "l1-" + "-".join(a)
    jan_l = page_png(L("Landscape"), 3, k("janL"))
    jan_p = page_png(L("Portrait", "Monday"), 3, k("janP"))
    cover = page_png(L("Portrait"), 1, k("coverP"))
    year_l = page_png(L("Landscape"), 2, k("yearL"))
    year_p = page_png(L("Portrait"), 2, k("yearP"))
    jan_mon = page_png(L("Landscape", "Monday"), 3, k("janLmon"))
    bg, acc = "#EEECE8", "#1d1d1d"
    out = []
    out.append(scene(
        '<div class="kick" style="left:150px;top:240px">Printable &middot; 2027</div>'
        '<div class="h1" style="left:150px;top:320px">Minimal<br><em>monthly</em><br>calendar</div>'
        '<div class="chips" style="left:150px;top:1180px;width:900px"><div class="chip d">A4 + US Letter</div>'
        '<div class="chip">Portrait &amp; Landscape</div><div class="chip">Sunday &amp; Monday start</div><div class="chip">Instant download</div></div>'
        + img(jan_p, 1150, 230, 900, -4, 1) + img(jan_l, 1240, 640, 1330, 3, 2), bg, acc))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:150px;text-align:center">What you get</div>'
        '<div class="h1" style="left:0;right:0;top:230px;text-align:center;font-size:100px">8 PDFs &middot; 14 pages each</div>'
        + img(cover, 170, 620, 520, -2) + img(year_p, 760, 620, 520, 1) + img(jan_p, 1350, 620, 520, -1)
        + img(year_l, 1950, 700, 640, 2) +
        '<div class="list" style="left:300px;top:1450px;columns:2;column-gap:180px;width:2200px">'
        '<div>Cover page</div><div>Year at a glance</div><div>12 monthly pages</div><div>Notes on portrait pages</div></div>', bg, acc))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:150px;text-align:center">Two paper sizes</div>'
        '<div class="h1" style="left:0;right:0;top:230px;text-align:center;font-size:100px">A4 <em>and</em> US Letter</div>'
        + img(page_png(L("Landscape", "Sunday", "A4"), 4, k("febA4")), 220, 640, 1080)
        + img(page_png(L("Landscape", "Sunday", "US-Letter"), 4, k("febLT")), 1400, 640, 1040)
        + '<div class="lab" style="left:220px;width:1080px;top:1470px">A4<small>210 &times; 297 mm &middot; Europe, UK, worldwide</small></div>'
          '<div class="lab" style="left:1400px;width:1040px;top:1470px">US Letter<small>8.5 &times; 11 in &middot; USA &amp; Canada</small></div>', bg, acc))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:150px;text-align:center">Your week, your way</div>'
        '<div class="h1" style="left:0;right:0;top:230px;text-align:center;font-size:100px">Sunday <em>or</em> Monday start</div>'
        + img(jan_l, 220, 640, 1080, -1.5) + img(jan_mon, 1400, 640, 1080, 1.5)
        + '<div class="lab" style="left:220px;width:1080px;top:1490px">Sunday start</div>'
          '<div class="lab" style="left:1400px;width:1080px;top:1490px">Monday start</div>', bg, acc))
    thumbs = "".join(img(page_png(L("Landscape"), m + 2, k(f"m{m}"), 60), 230 + (m - 1) % 4 * 570, 520 + (m - 1) // 4 * 470, 530)
                     for m in range(1, 13))
    out.append(scene('<div class="kick" style="left:0;right:0;top:170px;text-align:center">January to December</div>'
                     '<div class="h1" style="left:0;right:0;top:250px;text-align:center;font-size:100px">All 12 months, clean &amp; ink-friendly</div>'
                     + thumbs, bg, acc))
    out.append(scene(steps("PDF"), bg, acc))
    return out


def listing2():
    P = lambda pal, size="A4", s="Sunday": pdf(2, f"{pal}/2027-Calendar-Holidays_{pal}_{size}_{s}-Start.pdf")
    k = lambda *a: "l2-" + "-".join(a)
    sage_jul = page_png(P("Sage", "US-Letter"), 9, k("sage-jul"))
    sage_nov = page_png(P("Sage", "US-Letter"), 13, k("sage-nov"))
    bg, acc, ink = "#F1EEE9", "#6F8467", "#2f3a2c"
    sw = "".join(f'<span class="sw" style="background:{PALETTES[p][0]}"></span>' for p in PALETTES)
    out = []
    out.append(scene(
        '<div class="kick" style="left:150px;top:230px">Printable &middot; 2027</div>'
        '<div class="h1" style="left:150px;top:310px">Monthly<br>calendar <em>with</em><br><em>US holidays</em></div>'
        f'<div style="position:absolute;left:150px;top:1010px">{sw}</div>'
        '<div class="chips" style="left:150px;top:1180px;width:900px"><div class="chip d">4 colors included</div>'
        '<div class="chip">A4 + US Letter</div><div class="chip">Notes on every page</div></div>'
        + img(sage_nov, 1220, 260, 1300, -3, 1) + img(sage_jul, 1150, 760, 1380, 2, 2), bg, acc, ink))
    four = "".join(img(page_png(P(p), 3, k(p, "jan")), 290 + i % 2 * 1160, 390 + i // 2 * 790, 960)
                   + f'<div class="lab" style="left:{290 + i % 2 * 1160}px;width:960px;top:{1095 + i // 2 * 790}px;font-size:32px;color:{PALETTES[p][0]}">{p.replace("-", " ")}</div>'
                   for i, p in enumerate(PALETTES))
    out.append(scene('<div class="h1" style="left:0;right:0;top:170px;text-align:center;font-size:96px;top:150px">Pick your <em>color</em> &middot; all 4 included</div>'
                     + four, bg, acc, ink))
    big = page_png(P("Terracotta", "US-Letter"), 13, k("terra-nov-hi"), 300)
    out.append(scene(
        '<div class="kick" style="left:150px;top:300px">Up close</div>'
        '<div class="h1" style="left:150px;top:380px;font-size:104px">Holidays<br>already<br><em>printed in</em></div>'
        '<div class="list" style="left:150px;top:1050px;font-size:42px"><div>21 US holidays &amp; key dates</div><div>Federal holidays highlighted</div>'
        '<div>Prev / next month minis</div><div>Notes column every month</div></div>'
        f'<div class="zoom" style="left:1250px;top:220px;width:1300px;height:1580px"><img src="file://{big}" style="left:-1120px;top:-260px;width:3300px"></div>',
        bg, PALETTES["Terracotta"][0], ink))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:160px;text-align:center">Plan the whole year</div>'
        '<div class="h1" style="left:0;right:0;top:240px;text-align:center;font-size:100px">Year at a glance <em>+ holiday list</em></div>'
        + img(page_png(P("Dusty-Blue"), 2, k("blue-year")), 420, 600, 1860), bg, PALETTES["Dusty-Blue"][0], ink))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:170px;text-align:center">What you get</div>'
        '<div class="h1" style="left:0;right:0;top:250px;text-align:center;font-size:100px">16 PDFs, ready to print</div>'
        '<div class="list" style="left:300px;top:640px;font-size:50px"><div>4 colors: Sand, Sage, Terracotta, Dusty Blue</div>'
        '<div>A4 + US Letter sizes</div><div>Sunday + Monday start</div><div>14 pages: cover, year, 12 months</div>'
        '<div>Landscape, white background (ink-saving)</div><div>How-to-print guide</div></div>'
        + img(page_png(P("Sand"), 1, k("sand-cover")), 1650, 820, 860, 3), bg, acc, ink))
    out.append(scene(steps("4 colour"), bg, acc, ink))
    return out


def listing3():
    F = lambda size="A4", s="Sunday": pdf(3, f"{size}/2027-Hyperlinked-Calendar_{size}_{s}-Start.pdf")
    k = lambda *a: "l3-" + "-".join(a)
    mar = page_png(F(), 7, k("mar"))
    year = page_png(F(), 2, k("year"))
    plan = page_png(F(), 8, k("plan-mar"))
    cover = page_png(F(), 1, k("cover"))
    bg, acc, ink = "#ECE7E0", "#9a8f82", "#2C2A28"
    out = []
    out.append(scene(
        '<div class="kick" style="left:150px;top:250px">2027 &middot; Digital + Printable</div>'
        '<div class="h1" style="left:150px;top:330px">Hyperlinked<br><em>calendar</em><br>for iPad &amp; print</div>'
        '<div class="chips" style="left:150px;top:1180px;width:900px"><div class="chip d">Clickable tabs</div>'
        '<div class="chip">GoodNotes &amp; Notability</div><div class="chip">A4 + US Letter</div></div>'
        f'<div class="tablet" style="left:1180px;top:300px;transform:rotate(-2deg)"><img src="file://{mar}" style="width:1240px"></div>', bg, acc, ink))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:150px;text-align:center">Tap to navigate</div>'
        '<div class="h1" style="left:0;right:0;top:230px;text-align:center;font-size:100px">Every tab is a <em>link</em></div>'
        + img(mar, 500, 560, 1700)
        + '<div class="call" style="left:1700px;top:1830px">Month tabs: jump anywhere</div>'
          '<div class="call" style="left:1650px;top:440px">Plan &amp; notes page</div>'
          '<div class="call" style="left:500px;top:1830px">Prev / next month buttons</div>', bg, acc, ink))
    out.append(scene(
        '<div class="kick" style="left:150px;top:330px">Every month</div>'
        '<div class="h1" style="left:150px;top:410px;font-size:110px">A plan page<br><em>after each</em><br>month</div>'
        '<div class="list" style="left:150px;top:1080px"><div>Goals</div><div>To-do checklist</div><div>Dot-grid notes</div></div>'
        + img(plan, 1150, 330, 1400, 2), bg, acc, ink))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:160px;text-align:center">Clickable overview</div>'
        '<div class="h1" style="left:0;right:0;top:240px;text-align:center;font-size:100px">Tap a month on the <em>year page</em></div>'
        + img(year, 450, 600, 1800), bg, acc, ink))
    out.append(scene(
        '<div class="kick" style="left:0;right:0;top:170px;text-align:center">What you get</div>'
        '<div class="h1" style="left:0;right:0;top:250px;text-align:center;font-size:100px">One file, two ways to use it</div>'
        '<div class="list" style="left:250px;top:640px;font-size:48px"><div>26 pages: cover, year, 12 months, 12 plan pages</div>'
        '<div>A4 + US Letter, Sunday + Monday start</div><div>GoodNotes, Notability, Xodo, any PDF app</div>'
        '<div>Prints like a normal wall / desk calendar</div><div>Clean neutral design, landscape</div></div>'
        + img(cover, 1600, 1030, 940, -3), bg, acc, ink))
    out.append(scene(steps("PDF"), bg, acc, ink))
    return out


def listing4():
    Y = lambda o, s="Sunday", size="US-Letter": pdf(4, f"{size}/2027-Year-at-a-Glance_{size}_{o}_{s}-Start.pdf")
    k = lambda *a: "l4-" + "-".join(a)
    pp = page_png(Y("Portrait"), 1, k("P"))
    pl = page_png(Y("Landscape"), 1, k("L"))
    bg, acc = "#E9ECEE", "#1d1d1d"
    return [
        scene('<div class="kick" style="left:150px;top:300px">Printable &middot; one page</div>'
              '<div class="h1" style="left:150px;top:380px">2027<br><em>year at</em><br>a glance</div>'
              '<div class="chips" style="left:150px;top:1180px;width:950px"><div class="chip d">US holidays marked</div>'
              '<div class="chip">A4 + US Letter</div><div class="chip">Portrait &amp; Landscape</div></div>'
              + img(pp, 1400, 160, 1150, 2), bg, acc),
        scene('<div class="h1" style="left:0;right:0;top:180px;text-align:center;font-size:100px">Portrait <em>or</em> landscape</div>'
              + img(pp, 250, 520, 900, -1.5) + img(pl, 1300, 700, 1200, 1.5)
              + '<div class="lab" style="left:0;right:0;top:1820px;font-size:34px;color:#555">8 PDFs &middot; A4 + US Letter &middot; Sunday + Monday start</div>', bg, acc),
        scene(steps("PDF"), bg, acc),
    ]


def main():
    jobs = []
    tmp = BUILD / "mockups-html"
    tmp.mkdir(parents=True, exist_ok=True)
    for lst, fn in [(1, listing1), (2, listing2), (3, listing3), (4, listing4)]:
        dst = UPLOAD / LISTINGS[lst][0] / "images"
        dst.mkdir(parents=True, exist_ok=True)
        for i, html in enumerate(fn(), 1):
            h = tmp / f"{lst}-{i}.html"
            h.write_text(html)
            jobs.append({"html": str(h), "png": str(dst / f"{i:02d}.png"), "w": W, "h": H})
    jf = BUILD / "mockup-jobs.json"
    jf.write_text(json.dumps(jobs))
    subprocess.run(["node", str(ROOT / "render.js"), str(jf)], check=True)


if __name__ == "__main__":
    main()
