"""Little Elf Workshop: kids Christmas activity pages."""
import math
import random

from reportlab.lib.colors import white, HexColor

from lib import *  # noqa
import games as G
import content as K


def frame(c, W, H, x=36, y=40, top=None):
    top = top or H - 120
    c.setStrokeColor(PINE)
    c.setLineWidth(1.4)
    c.roundRect(x, y, W - 2 * x, top - y, 16, fill=0, stroke=1)
    return x, y, W - 2 * x, top - y


def kid_header(c, W, H, title, kicker):
    y = H - 50
    holly(c, W / 2, y, 14)
    spaced(c, kicker, W / 2, y - 26, size=8.5, color=BERRY)
    c.setFont("Playfair-Black", fit_font(title, "Playfair-Black", 30, W - 100))
    c.setFillColor(PINE)
    c.drawCentredString(W / 2, y - 58, title)
    return y - 78


def outline_text(c, text, x, y, size, font="Playfair-Black", maxw=None):
    if maxw:
        size = min(size, fit_font(text, font, size, maxw))
    c.saveState()
    t = c.beginText()
    t.setTextRenderMode(1)
    t.setFont(font, size)
    t.setTextOrigin(x - pdfmetrics.stringWidth(text, font, size) / 2, y)
    c.setStrokeColor(INK)
    c.setLineWidth(1.6)
    t.textLine(text)
    c.drawText(t)
    c.restoreState()


# --------------------------------------------------------------------------- coloring
def coloring_pages(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    L = "line"

    def page(title, drawfn, word=None):
        top = kid_header(c, W, H, title, "color me")
        x, y, w, h = frame(c, W, H, 36, 40, top)
        drawfn(x, y, w, h)
        if word:
            outline_text(c, word, W / 2, y + 28, 58, maxw=w - 60)
        ctx.end()

    def p1(x, y, w, h):
        base = y + 110
        th = h - 150
        tree(c, W / 2, base, th * 0.68, th, L, seed=2)
        gift(c, W / 2 - th * 0.55, base - 8, th * 0.2, th * 0.2, L)
        gift(c, W / 2 + th * 0.36, base - 8, th * 0.22, th * 0.16, L)
        c.setStrokeColor(INK)
        c.line(x + 20, base - 8, x + w - 20, base - 8)
    page("Oh Christmas Tree", p1, "MERRY CHRISTMAS")

    def p2(x, y, w, h):
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        p = c.beginPath()
        p.moveTo(x, y + 140)
        p.curveTo(x + w * 0.3, y + 200, x + w * 0.6, y + 120, x + w, y + 180)
        c.drawPath(p, fill=0, stroke=1)
        snowman(c, W / 2, y + 120, h * 0.68, L)
        rnd = random.Random(4)
        for _ in range(9):
            snowflake(c, x + rnd.uniform(40, w - 40), y + rnd.uniform(h * 0.62, h - 30), rnd.uniform(12, 22), INK, 1.6)
        tree(c, x + 80, y + 150, 80, 120, L, decorate=False)
    page("Let It Snow", p2, "LET IT SNOW")

    def p3(x, y, w, h):
        s = min(h * 0.42, w * 0.38)
        gingerbread(c, W / 2, y + h * 0.42, s * 1.3, L)
        gingerbread(c, x + w * 0.2, y + 110, s, L)
        gingerbread(c, x + w * 0.8, y + 110, s, L)
        candy_cane(c, x + w - 90, y + h - 130, 90, L, 16)
        candy_cane(c, x + 40, y + h - 130, 90, L, 16)
    page("Gingerbread Friends", p3)

    def p4(x, y, w, h):
        pats = ["stripes", "zigzag", "dots", "star", "zigzag", "stripes"]
        r = min(w / 7.5, h / 7.5)
        for i in range(6):
            col, row = i % 3, i // 3
            ox = x + w * (0.2 + 0.3 * col)
            oy = y + h * (0.68 - 0.42 * row) - (r * 0.4 if col == 1 else 0)
            c.setStrokeColor(INK)
            c.setLineWidth(1.2)
            c.line(ox, oy + r * 1.46, ox, y + h)
            ornament(c, ox, oy, r, L, pattern=pats[i])
    page("Shiny Ornaments", p4, "JOY")

    def p5(x, y, w, h):
        # mantel
        my = y + h * 0.62
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        c.setFillColor(white)
        c.rect(x + 20, my, w - 40, 26, fill=1, stroke=1)
        c.rect(x + 50, y + 90, 40, my - y - 90, fill=1, stroke=1)
        c.rect(x + w - 90, y + 90, 40, my - y - 90, fill=1, stroke=1)
        s = min(170, h * 0.36)
        for k in range(3):
            sx = x + w * (0.22 + k * 0.24)
            stocking(c, sx, my - s - 6, s, L)
        for k in range(5):
            bell(c, x + 60 + k * (w - 120) / 4, my + 40, 36, L)
        holly(c, W / 2, my + 100, 40, L)
    page("Hung With Care", p5, "NOEL")

    def p6(x, y, w, h):
        gs = min(w, h) * 0.3
        gift(c, W / 2 - gs * 0.9, y + 90, gs, gs, L)
        gift(c, W / 2 + gs * 0.05, y + 90, gs * 0.9, gs * 0.7, L)
        gift(c, W / 2 - gs * 0.5, y + 90 + gs * 0.95, gs * 0.8, gs * 0.65, L)
        candy_cane(c, x + 50, y + 100, gs * 1.5, L, 18)
        candy_cane(c, x + w - 130, y + 100, gs * 1.5, L, 18)
        for k in range(5):
            draw_star(c, x + 60 + k * (w - 120) / 4, y + h - 50, 18, L)
    page("Presents!", p6, "GIFTS")

    def p7(x, y, w, h):
        r = min(w, h) * 0.26
        wreath(c, W / 2, y + h * 0.52, r, L)
        bell(c, x + 80, y + 110, 70, L)
        bell(c, x + w - 80, y + 110, 70, L)
        santa_hat(c, W / 2, y + h * 0.52 - r * 0.25, r * 0.75, L)
    page("Welcome Wreath", p7, "WELCOME")

    def p8(x, y, w, h):
        s = min(w, h) * 0.38
        mitten(c, x + w * 0.12, y + h * 0.35, s, L)
        mitten(c, x + w * 0.55, y + h * 0.4, s, L)
        santa_hat(c, W / 2, y + h * 0.08 + 60, s * 0.9, L)
        rnd = random.Random(9)
        for _ in range(7):
            snowflake(c, x + rnd.uniform(40, w - 40), y + h - rnd.uniform(30, 120), rnd.uniform(10, 18), INK, 1.4)
    page("Warm & Cozy", p8)


# --------------------------------------------------------------------------- mazes
def make_maze(n, m, seed):
    rnd = random.Random(seed)
    walls = {(r, k): {"N": True, "S": True, "E": True, "W": True} for r in range(n) for k in range(m)}
    seen = {(0, 0)}
    stack = [(0, 0)]
    D = {"N": (-1, 0, "S"), "S": (1, 0, "N"), "E": (0, 1, "W"), "W": (0, -1, "E")}
    while stack:
        r, k = stack[-1]
        opts = [(d, r + dr, k + dk, o) for d, (dr, dk, o) in D.items() if (r + dr, k + dk) in walls and (r + dr, k + dk) not in seen]
        if not opts:
            stack.pop()
            continue
        d, nr, nk, o = rnd.choice(opts)
        walls[(r, k)][d] = False
        walls[(nr, nk)][o] = False
        seen.add((nr, nk))
        stack.append((nr, nk))
    # solve
    from collections import deque
    prev = {(0, 0): None}
    q = deque([(0, 0)])
    while q:
        cur = q.popleft()
        for d, (dr, dk, _) in D.items():
            if not walls[cur][d]:
                nx = (cur[0] + dr, cur[1] + dk)
                if nx not in prev:
                    prev[nx] = cur
                    q.append(nx)
    path = []
    cur = (n - 1, m - 1)
    while cur:
        path.append(cur)
        cur = prev[cur]
    return walls, path[::-1]


def draw_maze(c, walls, n, m, x, y, cs, path=None, lw=2.2):
    if path:
        c.saveState()
        c.setStrokeColor(BERRY)
        c.setLineWidth(cs * 0.3)
        c.setLineCap(1)
        c.setLineJoin(1)
        p = c.beginPath()
        for i, (r, k) in enumerate(path):
            px, py = x + k * cs + cs / 2, y + (n - r) * cs - cs / 2
            (p.moveTo if i == 0 else p.lineTo)(px, py)
        c.drawPath(p, fill=0, stroke=1)
        c.restoreState()
    c.setStrokeColor(PINE)
    c.setLineWidth(lw)
    c.setLineCap(1)
    for (r, k), wl in walls.items():
        x0, y0 = x + k * cs, y + (n - r - 1) * cs
        if wl["N"] and not (r == 0 and k == 0):
            c.line(x0, y0 + cs, x0 + cs, y0 + cs)
        if wl["W"]:
            c.line(x0, y0, x0, y0 + cs)
        if r == n - 1 and wl["S"] and not (k == m - 1):
            c.line(x0, y0, x0 + cs, y0)
        if k == m - 1 and wl["E"]:
            c.line(x0 + cs, y0, x0 + cs, y0 + cs)


def maze_pages(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    specs = [("Help the Elf Find the Tree", "easy maze", 8, 1), ("Deliver the Present", "medium maze", 12, 2),
             ("Santa's Sleigh Route", "tricky maze", 16, 3)]
    stored = []
    for title, kick, n, seed in specs:
        top = kid_header(c, W, H, title, kick)
        m = n
        size = min(W - 130, top - 150)
        cs = size / n
        x0, y0 = (W - size) / 2, 80 + (top - 150 - size) / 2 + 30
        walls, path = make_maze(n, m, seed)
        stored.append((title, walls, n, m, path))
        draw_maze(c, walls, n, m, x0, y0, cs)
        # start/end icons
        draw_emoji(c, "🧝", x0 + cs / 2, y0 + size + 26, 34)
        spaced(c, "start", x0 + cs / 2, y0 + size + 48, size=7, color=BERRY)
        draw_emoji(c, ["🎄", "🎁", "🏠"][seed - 1], x0 + size - cs / 2, y0 - 26, 34)
        spaced(c, "finish", x0 + size - cs / 2, y0 - 52, size=7, color=BERRY)
        ctx.end()
    # solutions on one page
    kid_header(c, W, H, "Maze Solutions", "for grown-ups")
    sz = min((W - 120) / 2, (H - 200) / 2)
    pos = [((W / 2 - sz - 20), H - 140 - sz), (W / 2 + 20, H - 140 - sz), (W / 2 - sz / 2, H - 140 - 2 * sz - 50)]
    for (title, walls, n, m, path), (px, py) in zip(stored, pos):
        draw_maze(c, walls, n, m, px, py, sz / n, path, lw=1.2)
        c.setFont("Montserrat-Medium", 8)
        c.setFillColor(MUTED)
        c.drawCentredString(px + sz / 2, py - 14, title)
    ctx.end()


# --------------------------------------------------------------------------- dot to dot
def dot_pages(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H

    def star_pts(cx, cy, r):
        pts = []
        verts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.42
            a = math.radians(90 + i * 36)
            verts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        for i in range(10):
            a, b = verts[i], verts[(i + 1) % 10]
            for t in (0, 1 / 3, 2 / 3):
                pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        return pts

    def tree_pts(cx, by, w, h):
        poly = [(0, 1), (0.22, 0.72), (0.12, 0.72), (0.34, 0.44), (0.2, 0.44), (0.46, 0.14), (0.1, 0.14), (0.1, 0),
                (-0.1, 0), (-0.1, 0.14), (-0.46, 0.14), (-0.2, 0.44), (-0.34, 0.44), (-0.12, 0.72), (-0.22, 0.72)]
        pts = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            seg = max(1, int(math.hypot((b[0] - a[0]) * w, (b[1] - a[1]) * h) / 45))
            for t in range(seg):
                f = t / seg
                pts.append((cx + (a[0] + (b[0] - a[0]) * f) * w, by + (a[1] + (b[1] - a[1]) * f) * h))
        return pts

    for title, kind in (("Connect the Dots: Star", "star"), ("Connect the Dots: Tree", "tree")):
        top = kid_header(c, W, H, title, "1, 2, 3... connect!")
        x, y, w, h = frame(c, W, H, 36, 40, top)
        cx, cy = W / 2, y + h / 2
        pts = star_pts(cx, cy, min(w, h) * 0.42) if kind == "star" else tree_pts(cx, y + 40, min(w, h) * 1.05, h - 80)
        for i, (px, py) in enumerate(pts):
            c.setFillColor(INK)
            c.circle(px, py, 3.2, fill=1, stroke=0)
            ang = math.atan2(py - cy, px - cx)
            c.setFont("Montserrat-SemiBold", 10)
            c.setFillColor(BERRY if i == 0 else INK)
            c.drawCentredString(px + 13 * math.cos(ang), py + 13 * math.sin(ang) - 3.5, str(i + 1))
        c.setFont("Montserrat-Regular", 8)
        c.setFillColor(MUTED)
        c.drawCentredString(W / 2, y + 14, f"Start at 1 and finish back at 1. Then color your picture!")
        ctx.end()


# --------------------------------------------------------------------------- counting
ICONS = [("tree", "🎄"), ("star", "⭐"), ("bell", "🔔"), ("gift", "🎁"), ("cane", "🍭")]


def count_page(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    top = kid_header(c, W, H, "I Spy Christmas", "count & write")
    x, y, w, h = 50, 210, W - 100, top - 230
    rounded_card(c, x, y, w, h, CREAM, CREAM2, 14)
    rnd = random.Random(12)
    counts = {"🎄": 6, "⭐": 9, "🔔": 5, "🎁": 8, "🍭": 7}
    placed = []
    s = 30
    for e, n in counts.items():
        for _ in range(n):
            for _ in range(500):
                px, py = rnd.uniform(x + 30, x + w - 30), rnd.uniform(y + 30, y + h - 30)
                if all(math.hypot(px - a, py - b) > s * 1.25 for a, b in placed):
                    break
            placed.append((px, py))
            draw_emoji(c, e, px, py, s * rnd.uniform(0.85, 1.15))
    for i, e in enumerate(counts):
        bx = 60 + i * (W - 120) / 5
        draw_emoji(c, e, bx + 22, 160, 30)
        c.setStrokeColor(PINE)
        c.setLineWidth(1.2)
        c.roundRect(bx + 4, 80, 40, 40, 8, fill=0, stroke=1)
        c.setFont("Montserrat-Regular", 7)
        c.setFillColor(MUTED)
        c.drawCentredString(bx + 24, 68, "how many?")
    ctx.end()
    return counts


def sudoku_pages(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    base = [[0, 1, 2, 3], [2, 3, 0, 1], [1, 0, 3, 2], [3, 2, 1, 0]]
    syms = ["🎄", "⭐", "🎁", "🔔"]
    puzzles = [
        (syms, [(0, 1), (0, 2), (1, 0), (1, 3), (2, 1), (2, 3), (3, 0), (3, 2)]),
        (["⛄", "🧦", "🍪", "🦌"], [(0, 0), (0, 3), (1, 1), (1, 2), (2, 0), (2, 2), (3, 1), (3, 3), (3, 0)]),
    ]
    top = kid_header(c, W, H, "Christmas Picture Sudoku", "draw the missing pictures")
    para(c, "Every row, every column and every thick box needs all 4 pictures, just once. Draw the missing ones!",
         70, top + 6, W - 140, "bodyc")
    sz = min(W - 200, (top - 120) / 2 - 20)
    for pi, (sy, blanks) in enumerate(puzzles):
        x0 = (W - sz) / 2
        y0 = top - 50 - (pi + 1) * sz - pi * 40
        cs = sz / 4
        for r in range(4):
            for k in range(4):
                c.setStrokeColor(LINE)
                c.setLineWidth(0.8)
                c.rect(x0 + k * cs, y0 + (3 - r) * cs, cs, cs, fill=0, stroke=1)
                if (r, k) not in blanks:
                    draw_emoji(c, sy[base[r][k]], x0 + k * cs + cs / 2, y0 + (3 - r) * cs + cs / 2, cs * 0.55)
        c.setStrokeColor(PINE)
        c.setLineWidth(2.4)
        c.rect(x0, y0, sz, sz, fill=0, stroke=1)
        c.line(x0 + sz / 2, y0, x0 + sz / 2, y0 + sz)
        c.line(x0, y0 + sz / 2, x0 + sz, y0 + sz / 2)
    ctx.end()
    return puzzles, base


def letter_to_santa(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    top = kid_header(c, W, H, "Dear Santa", "my letter to the north pole")
    santa_hat(c, W - 90, top + 40, 48)
    y = top - 10
    c.setFont("Montserrat-Medium", 11)
    c.setFillColor(INK)
    c.drawString(70, y, "My name is")
    G.answer_lines(c, 140, y - 2, 170)
    c.drawString(330, y, "I am")
    G.answer_lines(c, 362, y - 2, 40)
    c.drawString(410, y, "years old.")
    y -= 32
    c.drawString(70, y, "This year I have been:")
    for i, t in enumerate(["very nice", "mostly nice", "trying my best!"]):
        bx = 220 + i * 105
        c.setStrokeColor(PINE)
        c.roundRect(bx, y - 2, 11, 11, 2, fill=0, stroke=1)
        c.drawString(bx + 16, y, t)
    y -= 34
    c.drawString(70, y, "Something kind I did this year:")
    y -= 10
    for k in range(3):
        y -= 26
        G.answer_lines(c, 70, y, W - 140)
    y -= 34
    c.drawString(70, y, "For Christmas I would love:")
    y -= 10
    for k in range(5):
        y -= 26
        c.setFillColor(BERRY)
        c.drawString(70, y + 3, f"{k + 1}.")
        c.setFillColor(INK)
        G.answer_lines(c, 88, y, W - 158)
    c.setFont("GreatVibes", 26)
    c.setFillColor(BERRY)
    c.drawString(70, 92, "Love,")
    G.answer_lines(c, 140, 92, 200)
    c.setFont("Montserrat-Regular", 8)
    c.setFillColor(MUTED)
    c.drawString(350, 96, "P.S. I will leave cookies for you!")
    ctx.end()


def drawing_pages(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    for title, prompt in (("Draw Your Dream Christmas Tree", "decorate it any way you like"),
                          ("My Best Christmas Memory", "draw it, then tell someone about it")):
        top = kid_header(c, W, H, title, prompt)
        x, y, w, h = frame(c, W, H, 50, 120, top)
        if "Tree" in title:
            c.setStrokeColor(LINE)
            c.setDash(4, 4)
            c.setLineWidth(1.4)
            cx, by = W / 2, y + 30
            p = c.beginPath()
            p.moveTo(cx - w * 0.32, by + 40)
            p.lineTo(cx, y + h - 40)
            p.lineTo(cx + w * 0.32, by + 40)
            p.close()
            c.drawPath(p, fill=0, stroke=1)
            c.rect(cx - 18, by, 36, 40, fill=0, stroke=1)
            c.setDash()
        for k in range(2):
            G.answer_lines(c, 60, 92 - k * 26, W - 120)
        ctx.end()


def tracing_page(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    top = kid_header(c, W, H, "Trace the Words", "writing practice")
    words = ["JOY", "SNOW", "ELF", "STAR", "SANTA", "MERRY"]
    rh = (top - 70) / len(words)
    for i, wd in enumerate(words):
        yb = top - (i + 1) * rh + 18
        size = rh * 0.55
        c.setStrokeColor(LINE)
        c.setLineWidth(0.8)
        c.line(60, yb, W - 60, yb)
        c.line(60, yb + size * 0.72, W - 60, yb + size * 0.72)
        c.setDash(2, 3)
        c.line(60, yb + size * 0.36, W - 60, yb + size * 0.36)
        c.setDash()
        x = 70
        reps = 0
        while True:
            wdw = pdfmetrics.stringWidth(wd, "Montserrat-Bold", size)
            if x + wdw > W - 60 or reps >= 3:
                break
            if reps == 0:
                c.setFillColor(PINE)
                c.setFont("Montserrat-Bold", size)
                c.drawString(x, yb, wd)
            else:
                c.saveState()
                t = c.beginText()
                t.setTextRenderMode(1)
                t.setFont("Montserrat-Bold", size)
                t.setTextOrigin(x, yb)
                c.setStrokeColor(HexColor("#B9B3A7"))
                c.setLineWidth(1)
                c.setDash(2, 2)
                t.textLine(wd)
                c.drawText(t)
                c.restoreState()
            x += wdw + 30
            reps += 1
    ctx.end()


def tictactoe_page(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    top = kid_header(c, W, H, "Trees vs. Stars", "christmas tic-tac-toe")
    para(c, "One player draws trees, the other draws stars. Get three in a row to win!", 70, top + 6, W - 140, "bodyc")
    sz = min((W - 160) / 2, (top - 110) / 2)
    for i in range(4):
        col, r = i % 2, i // 2
        x0 = W / 2 - sz - 30 + col * (sz + 60)
        y0 = top - 40 - (r + 1) * sz - r * 30
        c.setStrokeColor(PINE)
        c.setLineWidth(3)
        c.setLineCap(1)
        for k in (1, 2):
            c.line(x0 + k * sz / 3, y0 + 6, x0 + k * sz / 3, y0 + sz - 6)
            c.line(x0 + 6, y0 + k * sz / 3, x0 + sz - 6, y0 + k * sz / 3)
    ctx.end()


def answers_page(ctx, ws_grid, ws_placed, counts, puzzles, base):
    c, W, H = ctx.c, ctx.W, ctx.H
    kid_header(c, W, H, "Answer Keys", "for grown-ups")
    size = min(W / 2 - 70, 230)
    G.draw_word_search(c, ws_grid, ws_placed, 60, H - 160 - size, size, highlight=True)
    c.setFont("Montserrat-Medium", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(60 + size / 2, H - 182 - size, "Word Search")
    # counts
    bx = W / 2 + 30
    yy = H - 170
    c.setFont("Montserrat-Medium", 9)
    c.drawString(bx, yy + 10, "I Spy Christmas")
    for i, (e, n) in enumerate(counts.items()):
        draw_emoji(c, e, bx + 12, yy - 16 - i * 30, 22)
        c.setFont("Playfair-Bold", 16)
        c.setFillColor(PINE)
        c.drawString(bx + 34, yy - 22 - i * 30, str(n))
    # sudoku solutions
    sz = 140
    for pi, (sy, _) in enumerate(puzzles):
        x0 = 60 + pi * (sz + 50) + (W - 2 * sz - 50 - 120) / 2
        y0 = 80
        cs = sz / 4
        for r in range(4):
            for k in range(4):
                c.setStrokeColor(LINE)
                c.rect(x0 + k * cs, y0 + (3 - r) * cs, cs, cs, fill=0, stroke=1)
                draw_emoji(c, sy[base[r][k]], x0 + k * cs + cs / 2, y0 + (3 - r) * cs + cs / 2, cs * 0.55)
        c.setStrokeColor(PINE)
        c.setLineWidth(2)
        c.rect(x0, y0, sz, sz, fill=0, stroke=1)
        c.setFont("Montserrat-Medium", 8)
        c.setFillColor(MUTED)
        c.drawCentredString(x0 + sz / 2, y0 - 14, f"Picture Sudoku {pi + 1}")
    ctx.end()


def kids_word_search(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    grid, placed = G.make_word_search(K.WORD_SEARCH_KIDS, 10, 8, diag=False)
    top = kid_header(c, W, H, "Christmas Word Search", "find 10 words")
    para(c, "The words go across (left to right) or down. Circle each one you find!", 70, top + 6, W - 140, "bodyc")
    size = min(W - 170, top - 190)
    G.draw_word_search(c, grid, placed, (W - size) / 2, top - 40 - size, size, font="Montserrat-Bold")
    yy = top - 80 - size
    for i, w in enumerate(K.WORD_SEARCH_KIDS):
        col, r = i % 5, i // 5
        bx = 70 + col * (W - 140) / 5
        c.setStrokeColor(SAGE)
        c.rect(bx, yy - r * 24 - 1, 9, 9, fill=0, stroke=1)
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(INK)
        c.drawString(bx + 14, yy - r * 24, w)
    ctx.end()
    return grid, placed


def parent_page(ctx, toc):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "Hello, Little Elves!", "a note for grown-ups")
    y -= para(c, "Thank you for choosing <b>Little Elf Workshop</b>! These pages are made for ages 4-9, perfect for "
                 "Christmas break, classroom parties, restaurant tables, road trips and quiet time before the big day. "
                 "Print only the pages you need, as many times as you like for your family or class.", 80, y, W - 160, "bodyc") + 18
    tips = ["Print at 100% / Actual size on US Letter or A4 paper.", "Coloring pages look great on thicker paper with crayons, markers or colored pencils.",
            "Mazes and puzzles get harder as you go. Start with the easy maze for little ones.",
            "Answer keys are on the last pages, so you can tear them off first!"]
    for t in tips:
        y -= para(c, "&bull;&nbsp; " + t, 100, y, W - 200, "small") + 4
    y -= 18
    spaced(c, "what's inside", W / 2, y, size=8.5)
    y -= 16
    per = (len(toc) + 1) // 2
    for i, (n, p) in enumerate(toc):
        col, r = i // per, i % per
        x = 80 + col * (W - 160) / 2
        c.setFont("Montserrat-Medium", 9.5)
        c.setFillColor(INK)
        c.drawString(x, y - r * 18, n)
        c.setFillColor(MUTED)
        c.drawRightString(x + (W - 160) / 2 - 20, y - r * 18, f"p. {p}")
    ctx.end()
