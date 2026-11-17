#!/usr/bin/env python3
"""Channel branding generator: profile picture (800x800) + banner (2560x1440, text inside YouTube's
1235x338 centre safe area). Everything is drawn in code - no game logos or third-party art.

    python3 tools/branding.py --name "FIVE STAR FACTS" --tagline "GTA 6 NEWS & SECRETS - VERIFIED, NEVER FAKED" \
        --badge 5 --out branding/
"""
import argparse, math, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.shorts import style  # noqa: E402

G, R, W, O = style.GREEN, style.RED, style.WHITE, style.OUTLINE
PINK, PURPLE, NAVY = (255, 60, 150), (120, 40, 200), (12, 10, 30)


def gradient(w, h, stops):
    """vertical gradient; stops = [(pos 0..1, (r,g,b)), ...]"""
    y = np.linspace(0, 1, h)[:, None]
    out = np.zeros((h, w, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = ((y >= p0) & (y <= p1)).astype(np.float32)
        t = np.clip((y - p0) / max(p1 - p0, 1e-6), 0, 1)
        col = np.array(c0) * (1 - t) + np.array(c1) * t
        out += m[..., None] * col[:, None, :] * np.ones((1, w, 1))
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def star_points(cx, cy, r_out, r_in, rot=-math.pi / 2):
    return [(cx + (r_out if i % 2 == 0 else r_in) * math.cos(rot + i * math.pi / 5),
             cy + (r_out if i % 2 == 0 else r_in) * math.sin(rot + i * math.pi / 5)) for i in range(10)]


def glow(img, radius, strength=1.6):
    g = img.filter(ImageFilter.GaussianBlur(radius))
    a = np.asarray(g).astype(np.float32)
    a[..., 3] = np.clip(a[..., 3] * strength, 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def synth_grid(w, h, horizon, color=(255, 60, 150), lines=18):
    """Retro neon perspective floor (original motif)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(1, lines):
        y = horizon + (h - horizon) * (i / lines) ** 2.2
        d.line((0, y, w, y), fill=color + (int(60 + 140 * i / lines),), width=max(2, int(4 * i / lines)))
    for k in range(-24, 25):
        x0 = w / 2 + k * w * 0.012
        x1 = w / 2 + k * w * 0.16
        d.line((x0, horizon, x1, h), fill=color + (150,), width=3)
    return img


def text(d, xy, s, size, fill, stroke=8, anchor="mm", italic=True):
    d.text(xy, s, font=style.font(size, italic), fill=fill, stroke_width=stroke, stroke_fill=O, anchor=anchor)


def fit_size(s, max_w, start, italic=True, stroke=8):
    size = start
    while size > 20 and style.font(size, italic).getlength(s) + 2 * stroke > max_w:
        size -= 4
    return size


def avatar(badge, out, S=800):
    bg = gradient(S, S, [(0, (40, 12, 70)), (0.55, (150, 30, 110)), (1, (255, 110, 60))]).convert("RGBA")
    # sun disc behind star
    sun = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sun).ellipse((S * .14, S * .14, S * .86, S * .86), fill=(255, 190, 70, 70))
    bg.alpha_composite(sun.filter(ImageFilter.GaussianBlur(30)))
    st = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pts = star_points(S / 2, S / 2 + 18, S * 0.40, S * 0.17)
    ImageDraw.Draw(st).polygon(pts, fill=W + (255,))
    bg.alpha_composite(glow(st, 26))
    d = ImageDraw.Draw(bg)
    d.polygon(pts, fill=W + (255,), outline=O + (255,), width=16)
    text(d, (S / 2, S / 2 + 46), str(badge), int(S * 0.36), G, stroke=14, italic=True)
    bg.convert("RGB").save(out, quality=95)
    # 98 px preview (how it looks in comments / Shorts feed), circular mask
    small = bg.resize((98, 98), Image.LANCZOS)
    mask = Image.new("L", (98, 98), 0); ImageDraw.Draw(mask).ellipse((0, 0, 97, 97), fill=255)
    prev = Image.new("RGBA", (98, 98), (0, 0, 0, 0)); prev.paste(small, (0, 0), mask)
    prev.save(Path(out).with_name("avatar_preview_98px.png"))


def banner(name, tagline, badge, sub, out, Wd=2560, Hd=1440):
    bg = gradient(Wd, Hd, [(0, NAVY), (0.38, (60, 16, 90)), (0.5, (190, 40, 120)), (0.53, (255, 120, 60)),
                           (0.535, (20, 8, 40)), (1, (8, 6, 20))]).convert("RGBA")
    horizon = int(Hd * 0.535)
    sun = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    r = Hd * 0.2
    sd.ellipse((Wd / 2 - r, horizon - r * 1.15, Wd / 2 + r, horizon + r * 0.85), fill=(255, 150, 70, 200))
    for i in range(6):  # retro sun stripes
        y = horizon - r * 0.05 - i * r * 0.16
        sd.rectangle((0, y, Wd, y + 6 + i * 3), fill=(0, 0, 0, 0))
    sun_np = np.asarray(sun).copy()
    for i in range(6):
        y = int(horizon - r * 0.08 - i * r * 0.17)
        sun_np[y:y + 8 + i * 2, :, 3] = 0
    sun = Image.fromarray(sun_np)
    bg.alpha_composite(glow(sun, 40, 1.0)); bg.alpha_composite(sun)
    floor = synth_grid(Wd, Hd, horizon)
    bg.alpha_composite(glow(floor, 6, 1.0)); bg.alpha_composite(floor)

    d = ImageDraw.Draw(bg)
    cx, cy = Wd / 2, Hd / 2
    safe_w = 1235
    # five stars (wanted-level HUD motif) above title
    sp = 120
    for i in range(5):
        x = cx - 2 * sp + i * sp
        pts = star_points(x, cy - 118, 48, 20)
        d.polygon(pts, fill=W + (255,), outline=O + (255,), width=6)
    size = fit_size(name, safe_w - 40, 150)
    words = name.split()
    # colour the first word (badge-style) green, rest white
    first, rest = words[0], " ".join(words[1:])
    f = style.font(size, True)
    total = f.getlength(name)
    x0 = cx - total / 2
    text(d, (x0, cy + 6), first, size, G, anchor="lm")
    if rest:
        text(d, (x0 + f.getlength(first + " "), cy + 6), rest, size, W, anchor="lm")
    tsize = fit_size(tagline, safe_w - 60, 46, stroke=5)
    text(d, (cx, cy + 112), tagline, tsize, W, stroke=5)
    if sub:
        # small pill, still inside safe area height (338 px total => cy +- 169)
        pass
    # upload schedule pill on the right (visible on TV/desktop only, outside safe area on purpose)
    if sub:
        sf = style.font(34, True)
        tw = sf.getlength(sub)
        px, py = Wd / 2 + 1025, cy + 6
        d.rounded_rectangle((px - tw / 2 - 26, py - 36, px + tw / 2 + 26, py + 36), 36, fill=(15, 15, 18, 235), outline=R + (255,), width=5)
        text(d, (px, py), sub, 34, W, stroke=4)
    bg.convert("RGB").save(out, quality=94)
    # previews of what each device shows
    full = bg.convert("RGB")
    full.crop((0, (Hd - 423) // 2, Wd, (Hd + 423) // 2)).resize((1280, 212)).save(Path(out).with_name("banner_preview_desktop.jpg"))
    full.crop(((Wd - 1546) // 2, (Hd - 423) // 2, (Wd + 1546) // 2, (Hd + 423) // 2)).save(Path(out).with_name("banner_preview_mobile.jpg"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--tagline", required=True)
    ap.add_argument("--badge", default="5")
    ap.add_argument("--sub", default="NEW SHORTS DAILY")
    ap.add_argument("--out", default="branding")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    avatar(a.badge, out / "avatar_800.jpg")
    banner(a.name, a.tagline, a.badge, a.sub, out / "banner_2560x1440.jpg")
    print("written to", out)


if __name__ == "__main__":
    main()
