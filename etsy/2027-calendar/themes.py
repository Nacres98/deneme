"""Decorated 2027 calendars: listing 5 (boho, per-month palettes + vector art) and
listing 6 (seasonal, per-month colour + line-art motif). Imported by build.py."""
import math, random
from build import YEAR, MONTHS, mini, month_grid, hol_extra, HOL

# ---------------------------------------------------------------- listing 5: boho
BOHO = [  # light, mid, dark, pale
    ("#D9B8A0", "#B97C5E", "#8C5A45", "#EBD9C8"),
    ("#E7B8AE", "#C98579", "#9E5C55", "#F3DCD5"),
    ("#C7C9A7", "#9AA27A", "#6E7A57", "#E4E3CF"),
    ("#E9CFA3", "#D2A46A", "#A8774A", "#F4E6CC"),
    ("#D6B6C2", "#B58698", "#8A5E70", "#EDDDE3"),
    ("#F0C78A", "#E09D55", "#B86F3A", "#F7E2C0"),
    ("#A9C3C2", "#6F9A9A", "#4B7172", "#D7E5E3"),
    ("#E8B48F", "#D4804F", "#A85A33", "#F4D9C5"),
    ("#CDB78F", "#A88C5C", "#7A6440", "#E7DCC6"),
    ("#D99A6C", "#B8693C", "#8A4A2A", "#EED0B8"),
    ("#B9A694", "#8E7966", "#62523F", "#DED3C8"),
    ("#B7BFB1", "#7F8E7E", "#56655A", "#DCE1D8"),
]
CREAM = "#FBF7F1"


def _rainbow(c, w, h, cx):
    l, m, d, p = c
    r0 = h * .92
    out = []
    for i, col in enumerate((d, m, l, p)):
        R = r0 - i * h * .17
        out.append(f'<path d="M{cx - R},{h} A{R},{R} 0 0 1 {cx + R},{h} Z" fill="{col}"/>')
    out.append(f'<path d="M{cx - r0 + 4 * h * .17},{h} A1,1 0 0 1 {cx + r0 - 4 * h * .17},{h} Z" fill="{CREAM}"/>')
    return out


def boho_art(m, w=400, h=260, cover=False):
    """Abstract boho composition for month m (1-12), as SVG markup (viewBox w x h)."""
    c = BOHO[m - 1]
    l, mid, d, p = c
    kind = (m - 1) % 6
    flip = m > 6
    s = [f'<rect width="{w}" height="{h}" fill="{p}"/>']
    if kind == 0:  # rainbow + small sun
        s += _rainbow(c, w, h, w * (.5 if cover else .38 if not flip else .62))
        if cover:
            return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMax slice" width="100%" height="100%">{"".join(s)}</svg>'
        sx = w * (.8 if not flip else .2)
        s.append(f'<circle cx="{sx}" cy="{h * .3}" r="{h * .1}" fill="{mid}"/>')
    elif kind == 1:  # setting sun with rays over hills
        cx = w * (.5 if not flip else .45)
        for i in range(13):
            a = math.pi + i * math.pi / 12
            s.append(f'<line x1="{cx + math.cos(a) * h * .42}" y1="{h * .78 + math.sin(a) * h * .42}" x2="{cx + math.cos(a) * h * .62}" '
                     f'y2="{h * .78 + math.sin(a) * h * .62}" stroke="{mid}" stroke-width="3" stroke-linecap="round"/>')
        s.append(f'<circle cx="{cx}" cy="{h * .78}" r="{h * .34}" fill="{l}"/>')
        s.append(f'<path d="M0,{h * .82} Q{w * .25},{h * .62} {w * .5},{h * .84} T{w},{h * .74} V{h} H0Z" fill="{d}"/>')
        s.append(f'<path d="M0,{h * .92} Q{w * .3},{h * .8} {w * .62},{h * .94} T{w},{h * .88} V{h} H0Z" fill="{mid}"/>')
    elif kind == 2:  # layered hills + sun
        s.append(f'<circle cx="{w * (.7 if not flip else .3)}" cy="{h * .34}" r="{h * .16}" fill="{mid}"/>')
        s.append(f'<path d="M0,{h * .62} C{w * .2},{h * .42} {w * .4},{h * .44} {w * .55},{h * .6} S{w * .85},{h * .5} {w},{h * .58} V{h} H0Z" fill="{l}"/>')
        s.append(f'<path d="M0,{h * .76} C{w * .25},{h * .6} {w * .5},{h * .66} {w * .7},{h * .78} S{w * .9},{h * .7} {w},{h * .74} V{h} H0Z" fill="{mid}"/>')
        s.append(f'<path d="M0,{h * .9} C{w * .3},{h * .78} {w * .55},{h * .84} {w},{h * .88} V{h} H0Z" fill="{d}"/>')
    elif kind == 3:  # arch window with sun and stripes
        aw, ax = w * .34, w * (.33 if not flip else .67)
        s.append(f'<path d="M{ax - aw / 2},{h} V{h * .42} A{aw / 2},{aw / 2} 0 0 1 {ax + aw / 2},{h * .42} V{h}Z" fill="{l}"/>')
        s.append(f'<circle cx="{ax}" cy="{h * .5}" r="{aw * .24}" fill="{d}"/>')
        s.append(f'<rect x="{ax - aw / 2}" y="{h * .74}" width="{aw}" height="{h * .26}" fill="{mid}"/>')
        bx = w * (.72 if not flip else .28)
        for i in range(4):
            s.append(f'<rect x="{bx - w * .12}" y="{h * (.3 + i * .14)}" width="{w * .24}" height="{h * .06}" rx="{h * .03}" fill="{(mid, l, d, mid)[i]}"/>')
    elif kind == 4:  # waves
        for i, col in enumerate((l, mid, d, mid)):
            y = h * (.45 + i * .14)
            s.append(f'<path d="M0,{y} Q{w * .125},{y - h * .08} {w * .25},{y} T{w * .5},{y} T{w * .75},{y} T{w},{y} V{h} H0Z" fill="{col}"/>')
        s.append(f'<circle cx="{w * (.25 if not flip else .75)}" cy="{h * .25}" r="{h * .11}" fill="{d}"/>')
    else:  # half circles grid + dots
        r = h * .2
        for i in range(3):
            for j in range(2):
                x, y = w * (.22 + i * .28), h * (.42 + j * .4)
                col = (l, mid, d)[(i + j) % 3]
                rot = 180 if (i + j + flip) % 2 else 0
                s.append(f'<path transform="rotate({rot} {x} {y})" d="M{x - r},{y} A{r},{r} 0 0 1 {x + r},{y} Z" fill="{col}"/>')
        rnd = random.Random(m)
        for _ in range(14):
            s.append(f'<circle cx="{rnd.uniform(.05, .95) * w}" cy="{rnd.uniform(.06, .25) * h}" r="2.4" fill="{mid}"/>')
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" width="100%" height="100%">{"".join(s)}</svg>'


CSS5 = """
.page{padding:12mm 13mm 11mm;background:#fff}
.art{border-radius:4mm;overflow:hidden}
.nm{font-family:'Fraunces';font-style:italic;font-weight:400;line-height:1;color:var(--d)}
.yr{font-size:8.5pt;font-weight:600;letter-spacing:.45em;color:var(--m)}
.grid{flex:1;display:grid;grid-template-columns:repeat(7,1fr)}
.dow{font-size:6.4pt;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--m);text-align:center;padding:0 0 2mm}
.cell{border-top:.5pt solid var(--l);padding:1.4mm 1.6mm;display:flex;flex-direction:column;gap:.6mm}
.cell .n{font-size:9.5pt;font-weight:500;color:#3a332d}
.cell.we .n{color:var(--m)}
.cell.off{border-top-color:var(--p)}
.hl{font-size:5.6pt;line-height:1.2;color:#8b8079}
.hl.fed{color:var(--d);font-weight:600}
.pt .art{height:42%}
.pt .head{display:flex;justify-content:space-between;align-items:baseline;margin:6mm 0 4mm}
.pt .nm{font-size:36pt}
.ls{flex-direction:row;gap:10mm}
.ls .left{width:38%;display:flex;flex-direction:column}
.ls .art{flex:1}
.ls .nm{font-size:40pt;margin-top:6mm}
.ls .yr{margin-top:2mm}
.ls .right{flex:1;display:flex;flex-direction:column}
.ls .lab{font-size:6.4pt;font-weight:600;letter-spacing:.25em;color:var(--m);text-transform:uppercase;margin-top:5mm}
.ls .notes{display:flex;flex-direction:column;height:30mm}
.ls .notes i{flex:1;border-bottom:.45pt solid var(--l)}
.cover{align-items:center;justify-content:center}
.cover .art{width:70%;height:55%;border-radius:999mm 999mm 4mm 4mm}
.cover .big{font-family:'Fraunces';font-weight:300;font-size:64pt;color:var(--d);margin-top:8mm;line-height:1}
.cover .sub{font-family:'Fraunces';font-style:italic;font-size:15pt;color:var(--m);margin-top:2mm}
.ls.cover{flex-direction:column}
.ls.cover .art{flex:0 0 auto;width:42%;height:60%}
.year .ttl{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6mm}
.year .ttl b{font-family:'Fraunces';font-style:italic;font-weight:400;font-size:30pt;color:#5a4a3d}
.year .ttl span{font-size:7pt;font-weight:600;letter-spacing:.3em;color:#a08c7a;text-transform:uppercase}
.ygrid{flex:1;display:grid;gap:5mm 7mm;align-content:space-between}
.ygrid .mini{padding:3mm;border-radius:2.5mm;background:var(--p)}
.year.pt .ygrid .mini .g{font-size:8.4pt;row-gap:1.6mm}
.ygrid .mini .t{font-size:7.4pt;margin-bottom:1.6mm;color:var(--d)}
.ygrid .mini .g{font-size:7.2pt;row-gap:1mm;color:#3a332d}
.ygrid .mini .g .h{font-size:5.4pt;color:var(--m)}
.ygrid .mini .g .hol{color:var(--d);font-weight:700;text-decoration:underline}
"""


def _vars(m):
    l, mid, d, p = BOHO[m - 1]
    return f"--l:{l};--m:{mid};--d:{d};--p:{p}"


def pages5(fw, portrait):
    o = "pt" if portrait else "ls"
    P = [f'<section class="page {o} cover" style="{_vars(10)}"><div class="art">{boho_art(1, 300, 300, cover=True)}</div>'
         f'<div class="big">{YEAR}</div><div class="sub">boho monthly calendar</div></section>']
    cols = "repeat(3,1fr)" if portrait else "repeat(4,1fr)"
    minis = "".join(f'<div style="{_vars(m)}">{mini(m, fw, mark_holidays=True)}</div>' for m in range(1, 13))
    P.append(f'<section class="page year {o}" style="{_vars(11)}"><div class="ttl"><b>{YEAR}</b><span>Year at a glance</span></div>'
             f'<div class="ygrid" style="grid-template-columns:{cols}">{minis}</div></section>')
    for m in range(1, 13):
        g = month_grid(m, fw, hol_extra, weekend_cls=True)
        if portrait:
            P.append(f'<section class="page pt" style="{_vars(m)}"><div class="art">{boho_art(m)}</div>'
                     f'<div class="head"><div class="nm">{MONTHS[m - 1]}</div><div class="yr">{YEAR}</div></div>{g}</section>')
        else:
            P.append(f'<section class="page ls" style="{_vars(m)}"><div class="left"><div class="art">{boho_art(m, 300, 340)}</div>'
                     f'<div class="nm">{MONTHS[m - 1]}</div><div class="yr">{YEAR}</div>'
                     f'<div class="lab">Notes</div><div class="notes">{"<i></i>" * 5}</div></div>'
                     f'<div class="right">{g}</div></section>')
    return P


# ---------------------------------------------------------------- listing 6: seasonal line-art
SEASON = ["#6F9DBA", "#D27D8E", "#6FA56A", "#5E9ECF", "#9C7EC0", "#E0A42E",
          "#3C97AA", "#E27A55", "#B98E2C", "#D06A24", "#8C5E40", "#2F7350"]
SEASON_NAME = ["winter", "love", "spring", "rain", "bloom", "sunshine", "ocean", "summer", "harvest", "autumn", "cozy", "holiday"]


def _icon(m, col):
    """Line-art motif in a 100x100 box."""
    st = f'fill="none" stroke="{col}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'
    if m == 1:  # snowflake
        arms = []
        for i in range(6):
            a = i * 60
            arms.append(f'<g transform="rotate({a} 50 50)"><line x1="50" y1="50" x2="50" y2="12"/><polyline points="40,22 50,30 60,22"/></g>')
        return f'<g {st}>{"".join(arms)}</g>'
    if m == 2:
        return f'<path {st} d="M50,82 C20,62 14,42 26,30 C36,20 48,26 50,36 C52,26 64,20 74,30 C86,42 80,62 50,82Z"/>'
    if m == 3:
        return (f'<g {st}><path d="M50,88 V44"/><path d="M50,58 C34,58 24,46 24,32 C40,32 50,42 50,58Z"/>'
                f'<path d="M50,48 C64,48 76,38 76,24 C60,24 50,34 50,48Z"/></g>')
    if m == 4:
        return f'<g {st}><path d="M50,14 C50,14 26,46 26,60 a24,24 0 0 0 48,0 C74,46 50,14 50,14Z"/><path d="M38,62 a12,12 0 0 0 10,12"/></g>'
    if m == 5:
        pet = "".join(f'<ellipse cx="50" cy="28" rx="11" ry="17" transform="rotate({i * 72} 50 50)"/>' for i in range(5))
        return f'<g {st}>{pet}<circle cx="50" cy="50" r="7"/></g>'
    if m == 6:
        rays = "".join(f'<line x1="50" y1="12" x2="50" y2="22" transform="rotate({i * 45} 50 50)"/>' for i in range(8))
        return f'<g {st}><circle cx="50" cy="50" r="18"/>{rays}</g>'
    if m == 7:
        return f'<g {st}><path d="M10,40 q10,-12 20,0 t20,0 t20,0 t20,0"/><path d="M10,58 q10,-12 20,0 t20,0 t20,0 t20,0"/><path d="M10,76 q10,-12 20,0 t20,0 t20,0 t20,0"/></g>'
    if m == 8:
        seg = "".join(f'<line x1="50" y1="50" x2="50" y2="20" transform="rotate({i * 60} 50 50)"/>' for i in range(6))
        return f'<g {st}><circle cx="50" cy="50" r="34"/><circle cx="50" cy="50" r="28"/>{seg}</g>'
    if m == 9:
        return f'<g {st}><path d="M22,80 C18,44 44,20 82,18 C82,56 58,82 22,80Z"/><path d="M22,80 L66,36"/></g>'
    if m == 10:
        return (f'<g {st}><ellipse cx="50" cy="58" rx="16" ry="24"/><ellipse cx="34" cy="58" rx="16" ry="22"/>'
                f'<ellipse cx="66" cy="58" rx="16" ry="22"/><path d="M50,34 C50,26 54,20 60,18"/></g>')
    if m == 11:
        return (f'<g {st}><path d="M26,44 C26,30 74,30 74,44 Z"/><path d="M30,44 C30,64 40,78 50,82 C60,78 70,64 70,44"/>'
                f'<path d="M50,34 V24"/></g>')
    return (f'<g {st}><path d="M50,16 L72,50 H60 L78,78 H22 L40,50 H28 Z"/><line x1="50" y1="78" x2="50" y2="88"/></g>')


def season_pattern(m, w, h, col, rows=2):
    """Jittered half-drop grid of the month's motif, viewBox w x h (match the box aspect)."""
    rnd = random.Random(m * 7)
    cell = h / rows
    cols = int(w / cell) + 1
    items = []
    for r in range(rows):
        for c in range(cols):
            if rnd.random() < .18:
                continue
            x = (c + (.5 if r % 2 else 0)) * cell + rnd.uniform(-.1, .1) * cell
            y = (r + .5) * cell + rnd.uniform(-.08, .08) * cell
            sz = cell * rnd.uniform(.5, .66)
            items.append(f'<g transform="translate({x - sz / 2:.1f},{y - sz / 2:.1f}) scale({sz / 100:.3f}) rotate({rnd.uniform(-18, 18):.0f} 50 50)" '
                         f'opacity="{rnd.choice((.5, .75, 1))}">{_icon(m, col)}</g>')
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" width="100%" height="100%">{"".join(items)}</svg>'


def _mix(hexc, t):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(v + (255 - v) * t) for v in (r, g, b))


CSS6 = """
.page{padding:11mm 13mm 10mm;background:#fff}
.band{position:relative;border-radius:4mm;background:var(--soft);overflow:hidden;display:flex;align-items:center}
.band .pat{position:absolute;inset:0 0 0 38%}
.band .lbl{position:relative;padding:0 9mm}
.band .nm{font-family:'Fraunces';font-weight:500;font-size:34pt;line-height:1;color:var(--acc)}
.band .tg{font-family:'Fraunces';font-style:italic;font-size:12pt;color:var(--ink);margin-top:1.5mm}
.band .yr{position:absolute;right:7mm;top:5mm;font-size:8pt;font-weight:600;letter-spacing:.4em;color:var(--acc);background:#fff;padding:1.4mm 3mm;border-radius:3mm}
.ls .band{height:34mm;margin-bottom:5mm}
.pt .band{height:50mm;margin-bottom:6mm}
.grid{flex:1;display:grid;grid-template-columns:repeat(7,1fr);gap:1mm}
.dow{font-size:6.6pt;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--acc);text-align:center;padding:0 0 1mm}
.cell{border:.5pt solid var(--line);border-radius:1.6mm;padding:1.4mm 1.7mm;display:flex;flex-direction:column;gap:.6mm}
.cell.we{background:var(--wash)}
.cell.off{border-style:dashed;border-color:#eee}
.n{font-size:9.5pt;font-weight:600;color:#333}
.hl{font-size:5.6pt;line-height:1.2;color:#888}
.hl.fed{color:var(--acc);font-weight:600}
.pt .notes{height:34mm;margin-top:5mm;display:flex;flex-direction:column}
.pt .notes .lab{font-size:6.4pt;font-weight:600;letter-spacing:.25em;color:var(--acc);text-transform:uppercase;margin-bottom:1mm}
.pt .notes i{flex:1;border-bottom:.45pt solid var(--line)}
.cover{align-items:center;justify-content:center;text-align:center}
.cover .ring{display:grid;grid-template-columns:repeat(6,1fr);gap:3mm;width:150mm;margin-bottom:9mm}
.cover .ring div{aspect-ratio:1;border-radius:50%;display:flex;align-items:center;justify-content:center}
.pt.cover .ring{grid-template-columns:repeat(4,1fr);width:120mm}
.cover .big{font-family:'Fraunces';font-weight:400;font-size:70pt;line-height:1;color:#2f3a3a}
.cover .sub{font-family:'Fraunces';font-style:italic;font-size:15pt;color:#7b8a8a;margin-top:2mm}
.year .ttl{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6mm}
.year .ttl b{font-family:'Fraunces';font-weight:500;font-size:30pt;color:#2f3a3a}
.year .ttl span{font-size:7pt;font-weight:600;letter-spacing:.3em;color:#8a9a9a;text-transform:uppercase}
.ygrid{flex:1;display:grid;gap:5mm 7mm;align-content:space-between}
.ygrid .mini{padding:3mm;border-radius:2.5mm;border:.6pt solid var(--line);border-top:2.4mm solid var(--acc)}
.ygrid .mini .t{font-size:7.4pt;margin-bottom:1.6mm;color:var(--acc)}
.ygrid .mini .g{font-size:7.2pt;row-gap:1mm;color:#333}
.ygrid .mini .g .h{font-size:5.4pt}
.ygrid .mini .g .hol{color:var(--acc);font-weight:700;text-decoration:underline}
"""


def _svars(m):
    a = SEASON[m - 1]
    return f"--acc:{a};--soft:{_mix(a, .84)};--wash:{_mix(a, .93)};--line:{_mix(a, .72)};--ink:{_mix(a, .0)}"


def pages6(fw, portrait):
    o = "pt" if portrait else "ls"
    ring = "".join(f'<div style="background:{_mix(SEASON[m - 1], .84)}"><svg viewBox="0 0 100 100" width="62%">{_icon(m, SEASON[m - 1])}</svg></div>'
                   for m in range(1, 13))
    P = [f'<section class="page {o} cover"><div class="ring">{ring}</div><div class="big">{YEAR}</div>'
         f'<div class="sub">seasonal monthly calendar</div></section>']
    cols = "repeat(3,1fr)" if portrait else "repeat(4,1fr)"
    minis = "".join(f'<div style="{_svars(m)}">{mini(m, fw, mark_holidays=True)}</div>' for m in range(1, 13))
    P.append(f'<section class="page year"><div class="ttl"><b>{YEAR}</b><span>Year at a glance</span></div>'
             f'<div class="ygrid" style="grid-template-columns:{cols}">{minis}</div></section>')
    for m in range(1, 13):
        bw, bh, rows = (115, 50, 3) if portrait else (170, 34, 2)
        band = (f'<div class="band"><div class="pat">{season_pattern(m, bw, bh, SEASON[m - 1], rows)}</div>'
                f'<div class="lbl"><div class="nm">{MONTHS[m - 1]}</div><div class="tg">{SEASON_NAME[m - 1]}</div></div>'
                f'<div class="yr">{YEAR}</div></div>')
        notes = f'<div class="notes"><div class="lab">Notes</div>{"<i></i>" * 4}</div>' if portrait else ""
        P.append(f'<section class="page {o}" style="{_svars(m)}">{band}{month_grid(m, fw, hol_extra, weekend_cls=True)}{notes}</section>')
    return P
