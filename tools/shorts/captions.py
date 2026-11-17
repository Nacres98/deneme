"""Word-synchronised gaming captions (reference style: heavy italic, narrow column,
words revealed as spoken with a scale pop, green/red emphasis)."""
from . import style
from .draw import text_sprite, text_width, blend, pop_scale

PUNCT_BREAK = (".", "?", "!", ":", ";")


def chunk_words(words, max_words=5, max_lines=3, max_w=style.CAPTION_MAX_W, size=style.CAPTION_SIZE):
    """Group aligned words into caption chunks; each chunk is laid out into lines."""
    chunks, cur = [], []

    def flush():
        if cur:
            chunks.append(list(cur))
            cur.clear()

    for i, w in enumerate(words):
        if cur:
            gap = w["s"] - cur[-1]["e"]
            if len(cur) >= max_words or gap > 0.45 or w.get("brk"):
                flush()
        cur.append(w)
        if w["text"].endswith(PUNCT_BREAK) or w["text"].endswith(","):
            if w["text"].endswith(PUNCT_BREAK) or len(cur) >= 3:
                flush()
    flush()

    out = []
    for c in chunks:
        lines = layout(c, max_w, size)
        if len(lines) > max_lines:  # split in half and retry
            h = len(c) // 2
            out += [{"words": c[:h], "lines": layout(c[:h], max_w, size)},
                    {"words": c[h:], "lines": layout(c[h:], max_w, size)}]
        else:
            out.append({"words": c, "lines": lines})
    for c in out:
        c["s"] = c["words"][0]["s"]
    for i, c in enumerate(out):
        nxt = out[i + 1]["s"] if i + 1 < len(out) else c["words"][-1]["e"] + 0.6
        c["e"] = min(nxt, c["words"][-1]["e"] + 0.6)
    return out


def layout(words, max_w, size):
    """Greedy line-wrap. Returns [[(word, x_offset_from_line_left, width)], ...] plus line widths."""
    space = style.font(size).getlength(" ") * 0.85
    lines, cur, cw = [], [], 0
    for w in words:
        tw = text_width(display(w), size)
        if cur and cw + space + tw > max_w:
            lines.append((cur, cw)); cur, cw = [], 0
        x = cw + (space if cur else 0)
        cur.append((w, x, tw)); cw = x + tw
    if cur:
        lines.append((cur, cw))
    return lines


def display(w):
    return w["text"].upper().rstrip(",;:")


def render(frame, chunks, t, S, W, H, y_frac=None, size=style.CAPTION_SIZE, hidden=()):
    """Draw the caption chunk active at time t. S = canvas scale (1.0 at 1080 wide)."""
    for a, b in hidden:
        if a <= t < b:
            return
    c = next((c for c in chunks if c["s"] <= t < c["e"]), None)
    if not c:
        return
    sz = max(8, int(size * S))
    line_h = sz * 1.12
    yc = (y_frac or c.get("y") or style.CAPTION_Y) * H
    n = len(c["lines"])
    y0 = yc - (n - 1) * line_h / 2
    for li, (line, lw) in enumerate(c["lines"]):
        left = W / 2 - lw * S / 2
        for w, x, tw in line:
            if t < w["s"]:
                continue
            spr = text_sprite(display(w), sz, style.COLORS[w.get("color", "w")])
            k = pop_scale(t - w["s"], peak=1.28 if w.get("color", "w") != "w" else 1.12)
            blend(frame, spr, left + (x + tw / 2) * S, y0 + li * line_h, scale=k)
