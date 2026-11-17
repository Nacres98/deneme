"""Motion-graphics components. Each component is `fn(frame, t, dur, S, W, H, **params)`:
t = seconds since the component started, dur = its on-screen duration, S = canvas scale (1.0 = 1080 wide).
All text/graphics are drawn in code (PIL) - nothing baked from images."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from . import style
from .draw import (blend, text_sprite, spring, ease_out, ease_in_out, pop_scale, clamp, panel, pil_to_np)

G, R, Wt, O = style.GREEN, style.RED, style.WHITE, style.OUTLINE
REGISTRY = {}


def component(fn):
    REGISTRY[fn.__name__] = fn
    return fn


def env(t, dur, tin=0.18, tout=0.14):
    """(alpha, scale) envelope: spring in, quick fade out."""
    if t < 0 or t > dur:
        return 0.0, 0.0
    a_in = clamp(t / tin)
    a_out = clamp((dur - t) / tout)
    s = 0.6 + 0.4 * min(1.0, spring(t)) if t < 0.6 else 1.0
    return min(a_in, a_out), s * (0.92 + 0.08 * a_out)


# ---------------------------------------------------------------- icons (drawn at 1080 scale, cached)
@lru_cache(maxsize=256)
def icon(name, size=150, color=Wt):
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(4, s // 14)
    c = tuple(color) + (255,)
    o = O + (255,)

    def stroke_ellipse(box, width):
        d.ellipse(box, outline=o, width=width + 8)
        d.ellipse([box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4], outline=c, width=width)

    if name == "clock":
        d.ellipse((6, 6, s - 6, s - 6), fill=o)
        d.ellipse((6 + lw, 6 + lw, s - 6 - lw, s - 6 - lw), fill=c)
        cx = cy = s / 2
        d.line((cx, cy, cx, s * 0.2), fill=o, width=lw)          # 12 o'clock
        d.line((cx, cy, cx + s * 0.18, cy + s * 0.08), fill=o, width=lw)
        d.ellipse((cx - lw, cy - lw, cx + lw, cy + lw), fill=o)
    elif name == "download":
        d.rounded_rectangle((10, s * 0.62, s - 10, s - 10), 14, fill=o)
        d.rounded_rectangle((10 + lw, s * 0.62 + lw, s - 10 - lw, s - 10 - lw), 10, fill=c)
        pts = [(s * .38, 10), (s * .62, 10), (s * .62, s * .38), (s * .8, s * .38), (s * .5, s * .66),
               (s * .2, s * .38), (s * .38, s * .38)]
        d.polygon(pts, fill=c, outline=o, width=lw // 2)
    elif name == "disc":
        d.ellipse((8, 8, s - 8, s - 8), fill=o)
        d.ellipse((8 + lw, 8 + lw, s - 8 - lw, s - 8 - lw), fill=(200, 200, 210, 255))
        d.ellipse((s * .4, s * .4, s * .6, s * .6), fill=o)
        d.line((14, s - 14, s - 14, 14), fill=R + (255,), width=lw + 4)
    elif name == "gift":
        d.rectangle((14, s * .4, s - 14, s - 10), fill=o)
        d.rectangle((14 + lw, s * .4 + lw, s - 14 - lw, s - 10 - lw), fill=G + (255,))
        d.rectangle((8, s * .28, s - 8, s * .44), fill=o)
        d.rectangle((8 + lw, s * .28 + lw, s - 8 - lw, s * .44 - lw), fill=G + (255,))
        d.rectangle((s * .44, s * .28, s * .56, s - 10), fill=Wt + (255,), outline=o, width=3)
        d.ellipse((s * .22, 6, s * .5, s * .32), outline=o, width=lw)
        d.ellipse((s * .5, 6, s * .78, s * .32), outline=o, width=lw)
    elif name == "pc":
        d.rounded_rectangle((8, 10, s - 8, s * .7), 10, fill=o)
        d.rounded_rectangle((8 + lw, 10 + lw, s - 8 - lw, s * .7 - lw), 6, fill=(60, 70, 90, 255))
        d.rectangle((s * .42, s * .7, s * .58, s * .84), fill=o)
        d.rounded_rectangle((s * .25, s * .82, s * .75, s * .92), 6, fill=o)
    elif name == "cloud":
        for bx in [(s * .08, s * .38, s * .5, s * .8), (s * .3, s * .18, s * .76, s * .64),
                   (s * .52, s * .36, s * .94, s * .8)]:
            d.ellipse(bx, fill=o)
        d.rectangle((s * .26, s * .56, s * .76, s * .8), fill=o)
        for bx in [(s * .08 + lw, s * .38 + lw, s * .5 - lw, s * .8 - lw), (s * .3 + lw, s * .18 + lw, s * .76 - lw, s * .64 - lw),
                   (s * .52 + lw, s * .36 + lw, s * .94 - lw, s * .8 - lw)]:
            d.ellipse(bx, fill=c)
        d.rectangle((s * .26, s * .56, s * .76, s * .8 - lw), fill=c)
    elif name == "comment":
        d.rounded_rectangle((8, 8, s - 8, s * .72), 26, fill=o)
        d.rounded_rectangle((8 + lw, 8 + lw, s - 8 - lw, s * .72 - lw), 20, fill=c)
        d.polygon([(s * .25, s * .68), (s * .45, s * .68), (s * .2, s * .92)], fill=o)
        for i in range(3):
            x = s * (.3 + .2 * i)
            d.ellipse((x - lw, s * .4 - lw, x + lw, s * .4 + lw), fill=o)
    elif name == "check":
        d.ellipse((4, 4, s - 4, s - 4), fill=o)
        d.ellipse((4 + lw, 4 + lw, s - 4 - lw, s - 4 - lw), fill=G + (255,))
        d.line([(s * .27, s * .52), (s * .44, s * .68), (s * .74, s * .34)], fill=o, width=lw + 4, joint="curve")
    elif name == "cross":
        d.ellipse((4, 4, s - 4, s - 4), fill=o)
        d.ellipse((4 + lw, 4 + lw, s - 4 - lw, s - 4 - lw), fill=R + (255,))
        d.line([(s * .32, s * .32), (s * .68, s * .68)], fill=o, width=lw + 4)
        d.line([(s * .68, s * .32), (s * .32, s * .68)], fill=o, width=lw + 4)
    elif name == "star":
        pts = []
        for i in range(10):
            r = s * (.48 if i % 2 == 0 else .2)
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
        d.polygon(pts, fill=c, outline=o, width=max(3, lw // 2))
    elif name == "warning":
        d.polygon([(s / 2, 6), (s - 6, s - 10), (6, s - 10)], fill=o)
        d.polygon([(s / 2, 6 + lw * 2), (s - 6 - lw * 2, s - 10 - lw), (6 + lw * 2, s - 10 - lw)], fill=style.YELLOW + (255,))
        d.rectangle((s * .46, s * .36, s * .54, s * .66), fill=o)
        d.ellipse((s * .45, s * .72, s * .55, s * .82), fill=o)
    return np.asarray(img)


def _icon_np(name, px, color=Wt):
    return icon(name, int(px), tuple(color))


# ---------------------------------------------------------------- components
@component
def heading(frame, t, dur, S, W, H, n=1, text="", icon_name=None):
    """Numbered fact heading: green '1.' + white italic text, icon underneath (reference style)."""
    a, sc = env(t, dur)
    if a <= 0:
        return
    sz = int(style.HEADING_SIZE * S)
    words = text.upper().split()
    lines, cur = [], f"{n}."
    for w in words:   # wrap at ~ 15 chars
        if len(cur) + 1 + len(w) > 16 and cur != f"{n}.":
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}"
    lines.append(cur)
    y = style.HEADING_Y * H - 40 * S * (1 - ease_out(t / 0.25))
    for i, ln in enumerate(lines):
        yy = y + i * sz * 1.08
        if i == 0:
            num, rest = ln.split(" ", 1) if " " in ln else (ln, "")
            sn = text_sprite(num, sz, G)
            sr = text_sprite(rest, sz, Wt) if rest else None
            wn = sn.shape[1]; wr = sr.shape[1] if sr is not None else 0
            pad = 2 * (style.CAPTION_STROKE + 18)
            total = wn + wr - pad * 0.75
            x0 = W / 2 - total * sc / 2
            blend(frame, sn, x0 + wn * sc / 2, yy, sc, a)
            if sr is not None:
                blend(frame, sr, x0 + (wn - pad * 0.75 + wr / 2) * sc, yy, sc, a)
        else:
            blend(frame, text_sprite(ln, sz, Wt), W / 2, yy, sc, a)
    if icon_name:
        ti = t - 0.15
        if ti > 0:
            k = pop_scale(ti, 1.35)
            ic = _icon_np(icon_name, 150 * S)
            blend(frame, ic, W / 2, y + len(lines) * sz * 1.08 + 70 * S, k, a)


@component
def title(frame, t, dur, S, W, H, lines=(("5 THINGS", "g"), ("TO KNOW BEFORE", "w"), ("YOU PLAY", "w")), y=0.2, size=96):
    a, sc = env(t, dur)
    if a <= 0:
        return
    sz = int(size * S)
    for i, (txt, col) in enumerate(lines):
        ti = t - i * 0.09
        if ti < 0:
            continue
        k = pop_scale(ti, 1.3)
        blend(frame, text_sprite(txt, sz, style.COLORS[col]), W / 2, y * H + i * sz * 1.05, k * sc, a)


@component
def label(frame, t, dur, S, W, H, text="", x=0.5, y=0.5, color="w", size=54, bg=True, icon_name=None):
    """Feature label / pill. Optionally with an icon on the left."""
    a, sc = env(t, dur)
    if a <= 0:
        return
    sz = int(size * S)
    spr = text_sprite(text.upper(), sz, style.COLORS[color], stroke=max(3, int(5 * S)))
    cx, cy = x * W, y * H
    if bg:
        w, h = spr.shape[1] - int(30 * S) + (int(sz * 1.3) if icon_name else 0), int(sz * 1.55)
        p = pil_to_np(panel(w, h, radius=int(h / 2), border=style.COLORS[color] + (255,), border_w=max(2, int(4 * S))))
        blend(frame, p, cx, cy, sc, a * 0.95)
    if icon_name:
        ic = _icon_np(icon_name, sz * 1.05)
        blend(frame, ic, cx - spr.shape[1] / 2 * sc + sz * 0.25, cy, sc, a)
        cx += sz * 0.55
    blend(frame, spr, cx, cy, sc, a)


@component
def clock(frame, t, dur, S, W, H, frm="11:59", to="12:00", suffix="AM", frm_suffix=None, flip_at=0.9, y=0.42, sub="YOUR LOCAL TIME"):
    """Digital clock panel that flips from `frm` to `to`."""
    a, sc = env(t, dur)
    if a <= 0:
        return
    pw, ph = int(640 * S), int(300 * S)
    blend(frame, pil_to_np(panel(pw, ph, radius=int(36 * S), border=G + (255,), border_w=int(6 * S))), W / 2, y * H, sc, a * 0.92)
    flipped = t >= flip_at
    txt = to if flipped else frm
    k = pop_scale(t - flip_at, 1.25) if flipped else 1.0
    col = G if flipped else Wt
    blend(frame, text_sprite(txt, int(150 * S), col, italic=False, stroke=int(6 * S)), W / 2 - 50 * S, y * H - 20 * S, sc * k, a)
    blend(frame, text_sprite(suffix if flipped or not frm_suffix else frm_suffix, int(60 * S), col, italic=False, stroke=int(4 * S)), W / 2 + 230 * S, y * H - 5 * S, sc, a)
    if sub:
        blend(frame, text_sprite(sub, int(40 * S), Wt, stroke=int(4 * S)), W / 2, y * H + 100 * S, sc, a)


@component
def timezones(frame, t, dur, S, W, H, rows=(("NEW YORK", "12:00 AM", "PLAYING", "g"),
                                             ("LOS ANGELES", "9:00 PM", "WAITING", "r")), gap_label="3 HOURS", y=0.38):
    """Stacked city cards with a time-gap arrow between them."""
    a, _ = env(t, dur)
    if a <= 0:
        return
    cw, ch = int(820 * S), int(190 * S)
    for i, (city, tm, status, col) in enumerate(rows):
        ti = t - i * 0.35
        if ti < 0:
            continue
        slide = (1 - ease_out(ti / 0.3)) * (W * 0.6) * (1 if i else -1)
        cy = y * H + i * (ch + 150 * S)
        cx = W / 2 + slide
        blend(frame, pil_to_np(panel(cw, ch, radius=int(30 * S), border=style.COLORS[col] + (255,), border_w=int(6 * S))), cx, cy, 1, a * 0.93)
        blend(frame, text_sprite(city, int(46 * S), Wt, stroke=int(4 * S)), cx - 160 * S, cy - 38 * S, 1, a)
        blend(frame, text_sprite(tm, int(64 * S), Wt, italic=False, stroke=int(5 * S)), cx - 160 * S, cy + 34 * S, 1, a)
        k = pop_scale(ti - 0.3, 1.3) if ti > 0.3 else 0
        if k:
            blend(frame, _icon_np("check" if col == "g" else "cross", 84 * S), cx + 210 * S, cy - 30 * S, k, a)
            blend(frame, text_sprite(status, int(38 * S), style.COLORS[col], stroke=int(4 * S)), cx + 240 * S, cy + 48 * S, k, a)
    tg = t - 0.8
    if tg > 0:
        mid = y * H + (ch + 150 * S) / 2
        L = (ch + 150 * S - ch) * ease_out(tg / 0.25)
        img = Image.new("RGBA", (int(60 * S), int(150 * S)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(img)
        x = img.width / 2
        dd.line((x, 5, x, max(6, L - 20 * S)), fill=style.YELLOW + (255,), width=int(10 * S))
        if L > 40 * S:
            dd.polygon([(x - 22 * S, L - 30 * S), (x + 22 * S, L - 30 * S), (x, L - 2)], fill=style.YELLOW + (255,))
        blend(frame, np.asarray(img), W / 2 - 300 * S, mid, 1, a)
        blend(frame, text_sprite(gap_label, int(46 * S), style.YELLOW, stroke=int(5 * S)), W / 2 - 80 * S, mid, pop_scale(tg, 1.3), a)


@component
def storage_bar(frame, t, dur, S, W, H, value=212, unit="GB", head="DOWNLOAD SIZE", sub="UP TO · DEPENDS ON CONSOLE",
                y=0.4, fill_time=1.2):
    a, sc = env(t, dur)
    if a <= 0:
        return
    pw, ph = int(860 * S), int(420 * S)
    cx, cy = W / 2, y * H
    blend(frame, pil_to_np(panel(pw, ph, radius=int(36 * S), border=R + (255,), border_w=int(6 * S))), cx, cy, sc, a * 0.93)
    blend(frame, _icon_np("download", 110 * S), cx - 300 * S, cy - 120 * S, sc, a)
    blend(frame, text_sprite(head, int(48 * S), Wt, stroke=int(4 * S)), cx + 60 * S, cy - 120 * S, sc, a)
    p = ease_out(t / fill_time)
    num = int(round(value * p))
    k = pop_scale(t - fill_time, 1.2) if t >= fill_time else 1.0
    blend(frame, text_sprite(f"{num} {unit}", int(118 * S), R, italic=False, stroke=int(6 * S)), cx, cy + 10 * S, sc * k, a)
    bw, bh = int(720 * S), int(44 * S)
    bar = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle((0, 0, bw - 1, bh - 1), bh // 2, fill=(55, 55, 62, 255))
    if p > 0.02:
        bd.rounded_rectangle((0, 0, max(bh, int((bw - 1) * p)), bh - 1), bh // 2, fill=R + (255,))
    blend(frame, np.asarray(bar), cx, cy + 115 * S, sc, a)
    blend(frame, text_sprite(sub, int(32 * S), Wt, stroke=int(3 * S)), cx, cy + 172 * S, sc, a)


@component
def calendar(frame, t, dur, S, W, H, month="NOV", day="10", caption="PRE-LOAD OPEN SINCE", color="g", y=0.42):
    a, sc = env(t, dur)
    if a <= 0:
        return
    cw, chh = int(360 * S), int(380 * S)
    img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = style.COLORS[color]
    d.rounded_rectangle((0, 0, cw - 1, chh - 1), int(34 * S), fill=(245, 245, 245, 255), outline=O + (255,), width=int(8 * S))
    d.rounded_rectangle((0, 0, cw - 1, int(120 * S)), int(34 * S), fill=col + (255,), outline=O + (255,), width=int(8 * S))
    d.rectangle((int(8 * S), int(80 * S), cw - int(9 * S), int(112 * S)), fill=col + (255,))
    k = pop_scale(t, 1.25)
    blend(frame, np.asarray(img), W / 2, y * H, k * sc, a)
    blend(frame, text_sprite(caption, int(44 * S), Wt, stroke=int(5 * S)), W / 2, y * H - chh / 2 - 60 * S, sc, a)
    blend(frame, text_sprite(month, int(66 * S), Wt, italic=False, stroke=int(5 * S)), W / 2, y * H - chh / 2 + 62 * S, k * sc, a)
    blend(frame, text_sprite(day, int(170 * S), O, italic=False, stroke=0, shadow=False), W / 2, y * H + 60 * S, k * sc, a)


@component
def checklist(frame, t, dur, S, W, H, items=(("PS5", "check"), ("XBOX SERIES X|S", "check"), ("PC", "cross")),
              y=0.36, stagger=0.35, head=None, width=820):
    """Rows of ✓/✕ items that pop in one by one."""
    a, _ = env(t, dur)
    if a <= 0:
        return
    rh = int(150 * S)
    n = len(items)
    top = y * H - (n - 1) * rh / 2
    if head:
        blend(frame, text_sprite(head, int(50 * S), style.YELLOW, stroke=int(5 * S)), W / 2, top - 120 * S, 1, a)
    for i, (txt, ic) in enumerate(items):
        ti = t - i * stagger
        if ti < 0:
            continue
        k = pop_scale(ti, 1.2)
        cy = top + i * rh
        col = G if ic == "check" else (R if ic == "cross" else Wt)
        pw = int(width * S)
        blend(frame, pil_to_np(panel(pw, int(118 * S), radius=int(59 * S), border=col + (255,), border_w=int(5 * S))), W / 2, cy, k, a * 0.92)
        blend(frame, _icon_np(ic, 86 * S), W / 2 - pw / 2 + 70 * S, cy, k, a)
        blend(frame, text_sprite(txt, int(50 * S), Wt, stroke=int(4 * S)), W / 2 + 40 * S, cy, k, a)


@component
def box_reveal(frame, t, dur, S, W, H, y=0.42, code="XXXX-XXXX-XXXX"):
    """Generic (unbranded) game case opens: empty disc tray + red NO DISC stamp, code card slides out."""
    a, sc = env(t, dur)
    if a <= 0:
        return
    bw, bh = int(520 * S), int(640 * S)
    open_p = ease_in_out((t - 0.25) / 0.45)
    img = Image.new("RGBA", (int(bw * 1.9), bh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox = int(bw * 0.45)
    # right half: tray (always visible)
    d.rounded_rectangle((ox, 10, ox + bw, bh), int(24 * S), fill=(30, 60, 140, 255), outline=O + (255,), width=int(10 * S))
    d.rounded_rectangle((ox + 30 * S, 40 * S, ox + bw - 30 * S, bh - 30 * S), int(18 * S), fill=(22, 22, 28, 255))
    cxr, cyr, rr = ox + bw / 2, bh / 2, bw * 0.36
    d.ellipse((cxr - rr, cyr - rr, cxr + rr, cyr + rr), outline=(120, 120, 130, 255), width=int(6 * S))
    d.ellipse((cxr - rr * .2, cyr - rr * .2, cxr + rr * .2, cyr + rr * .2), outline=(120, 120, 130, 255), width=int(6 * S))
    # lid swinging open (shrinks horizontally to the left)
    lw = int(bw * (1 - open_p))
    if lw > 6:
        d.rounded_rectangle((ox, 10, ox + lw, bh), int(24 * S), fill=(30, 60, 140, 255), outline=O + (255,), width=int(10 * S))
        d.rectangle((ox + 30 * S, 60 * S, ox + max(31 * S, lw - 30 * S), 160 * S), fill=(240, 240, 240, 255))
    elif open_p > 0.5:
        lw2 = int(bw * (open_p - 0.5) * 2 * 0.9)
        d.rounded_rectangle((ox - lw2, 10, ox, bh), int(24 * S), fill=(25, 50, 120, 255), outline=O + (255,), width=int(10 * S))
    blend(frame, np.asarray(img), W / 2, y * H, sc, a)
    # code card slides out
    tc = t - 0.9
    if tc > 0:
        p = ease_out(tc / 0.35)
        card = pil_to_np(panel(int(560 * S), int(150 * S), radius=int(20 * S), fill=(250, 250, 250, 255), border=O + (255,), border_w=int(8 * S)))
        cy = y * H + (bh * 0.15) + p * 320 * S
        blend(frame, card, W / 2 + 90 * S, cy, sc, a)
        blend(frame, text_sprite("DOWNLOAD CODE", int(34 * S), O, stroke=0, shadow=False), W / 2 + 90 * S, cy - 30 * S, sc, a)
        blend(frame, text_sprite(code, int(40 * S), (40, 40, 40), italic=False, stroke=0, shadow=False), W / 2 + 90 * S, cy + 28 * S, sc, a)
    ts = t - 0.6
    if ts > 0:
        k = pop_scale(ts, 1.6)
        stamp = text_sprite("NO DISC", int(120 * S), R, stroke=int(8 * S))
        blend(frame, stamp, W / 2 + 120 * S, y * H - 40 * S, k * sc, a)


@component
def wanted(frame, t, dur, S, W, H, stars=5, total=6, y=0.13):
    """Game-HUD style wanted-level stars, filling one by one."""
    a, _ = env(t, dur)
    if a <= 0:
        return
    sp = 92 * S
    x0 = W / 2 - (total - 1) * sp / 2
    pw = int(total * sp + 60 * S)
    blend(frame, pil_to_np(panel(pw, int(130 * S), radius=int(16 * S), fill=(10, 10, 12, 200), border=(220, 190, 60, 255))), W / 2, y * H, 1, a)
    for i in range(total):
        on = t > 0.12 * i and i < stars
        ic = _icon_np("star", 78 * S, (240, 240, 240) if on else (70, 70, 74))
        blend(frame, ic, x0 + i * sp, y * H, pop_scale(t - 0.12 * i, 1.4) if on else 1, a)


@component
def counter(frame, t, dur, S, W, H, n=1, total=5, y=0.035):
    """Small progress dots (top centre) shown during each fact."""
    a, _ = env(t, dur, 0.1, 0.1)
    if a <= 0:
        return
    sp = 36 * S
    x0 = W / 2 - (total - 1) * sp / 2
    for i in range(total):
        col = G if i < n else (90, 90, 96)
        r = int(11 * S) if i != n - 1 else int(14 * S)
        img = Image.new("RGBA", (r * 2 + 6, r * 2 + 6), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((3, 3, 3 + 2 * r, 3 + 2 * r), fill=col + (255,), outline=O + (255,), width=3)
        k = pop_scale(t, 1.6) if i == n - 1 else 1
        blend(frame, np.asarray(img), x0 + i * sp, y * H, k, a)


@component
def icon_pop(frame, t, dur, S, W, H, name="comment", x=0.5, y=0.5, size=170, color=(255, 255, 255), bounce=True):
    a, _ = env(t, dur)
    if a <= 0:
        return
    k = pop_scale(t, 1.4)
    dy = math.sin(t * 6) * 10 * S if bounce and t > 0.4 else 0
    blend(frame, _icon_np(name, size * S, tuple(color)), x * W, y * H + dy, k, a)


@component
def flash(frame, t, dur, S, W, H, strength=0.55):
    """Impact flash: quick white fade (use dur ~0.12)."""
    if 0 <= t <= dur:
        k = strength * (1 - t / dur)
        frame[:] = (frame.astype(np.float32) * (1 - k) + 255 * k).astype(np.uint8)
