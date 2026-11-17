"""Low-level compositing helpers: easing, RGBA sprite blending, outlined text sprites."""
import math
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import style


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def spring(t, freq=4.5, damp=6.0):
    """Underdamped spring 0->1 (overshoots slightly). t in seconds."""
    if t <= 0:
        return 0.0
    return 1 - math.exp(-damp * t) * math.cos(2 * math.pi * freq * t * 0.5)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def pop_scale(t, peak=1.22, dur=0.16):
    """Scale-pop: starts at `peak`, settles to 1 with a small spring."""
    if t < 0:
        return 0.0
    if t >= 0.5:
        return 1.0
    return 1 + (peak - 1) * math.exp(-t / (dur / 3)) * math.cos(t * 18)


# ---------------------------------------------------------------- blending
def blend(frame, sprite, cx, cy, scale=1.0, alpha=1.0, anchor="center"):
    """Alpha-blend an RGBA numpy sprite onto frame (HxWx3 uint8) in place.
    (cx, cy) is the sprite's anchor point in frame pixels."""
    if sprite is None or alpha <= 0.003 or scale <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        h, w = sprite.shape[:2]
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        sprite = cv2.resize(sprite, (nw, nh), interpolation=cv2.INTER_LINEAR if scale > 1 else cv2.INTER_AREA)
    h, w = sprite.shape[:2]
    if anchor == "center":
        x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    elif anchor == "topleft":
        x0, y0 = int(round(cx)), int(round(cy))
    else:  # top-center
        x0, y0 = int(round(cx - w / 2)), int(round(cy))
    H, W = frame.shape[:2]
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx0 >= fx1 or fy0 >= fy1:
        return
    s = sprite[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = s[..., 3:4].astype(np.float32) * (alpha / 255.0)
    roi = frame[fy0:fy1, fx0:fx1].astype(np.float32)
    frame[fy0:fy1, fx0:fx1] = (roi * (1 - a) + s[..., :3].astype(np.float32) * a).astype(np.uint8)


def pil_to_np(img):
    return np.asarray(img.convert("RGBA"))


# ---------------------------------------------------------------- text
@lru_cache(maxsize=4096)
def text_sprite(text, size, color=style.WHITE, stroke=style.CAPTION_STROKE, italic=True,
                shadow=True, weight="ExtraBold"):
    """Outlined, drop-shadowed text as an RGBA numpy array (cached)."""
    f = style.font(size, italic, weight)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    pad = stroke + 18
    w, h = r - l + pad * 2, b - t + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 3, pad - t + 6), text, font=f, fill=(0, 0, 0, 200),
                                stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        img.alpha_composite(sh)
    ImageDraw.Draw(img).text((pad - l, pad - t), text, font=f, fill=tuple(color) + (255,),
                             stroke_width=stroke, stroke_fill=style.OUTLINE + (255,))
    return np.asarray(img)


def text_width(text, size, italic=True, stroke=style.CAPTION_STROKE):
    f = style.font(size, italic)
    l, _, r, _ = f.getbbox(text, stroke_width=stroke)
    return r - l


def text_pad(stroke=style.CAPTION_STROKE):
    return stroke + 18


def panel(w, h, radius=26, fill=(15, 15, 18, 225), border=None, border_w=4):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=fill,
                        outline=border, width=border_w if border else 0)
    return img
