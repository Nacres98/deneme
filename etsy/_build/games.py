"""Page builders for every party game. Each function draws one or more full pages."""
import random

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.lib.colors import white

from lib import *  # noqa
import content as K


class Ctx:
    def __init__(self, c, W, H, product):
        self.c, self.W, self.H, self.product = c, W, H, product
        self.page = 1

    def end(self, footer_on=True):
        if footer_on:
            footer(self.c, self.W, self.H, self.product, self.page)
        self.c.showPage()
        self.page += 1


# --------------------------------------------------------------------------- rules (used in pages + host guide)
RULES = {
    "bingo": dict(title="Christmas Bingo", players="2-30", time="15-30 min", need="Bingo cards, calling cards, pens or markers (candy works great!)",
                  rules=["Give each player one bingo card.", "The host cuts out the calling cards, shuffles them and draws one at a time, reading it out loud.",
                         "Players mark the word or picture if it is on their card. The center square is free.",
                         "The first player to complete a full row, column or diagonal shouts 'BINGO!' and wins.",
                         "Variations: four corners, an X shape, or a full card (blackout) for a longer game."]),
    "most_likely": dict(title="Who's Most Likely To", players="4+", time="10-20 min", need="Prompt cards",
                        rules=["Cut the cards and put them in a pile, face down.", "One player reads a card out loud: 'Who's most likely to...'",
                               "On the count of three, everyone points at the player they think fits best.",
                               "The player with the most fingers pointing at them takes the card. The player with the most cards at the end is crowned the group's 'Most Likely'!"]),
    "this_or_that": dict(title="This or That", players="2+", time="10 min", need="Game sheets, pens",
                         rules=["Each player gets a sheet and circles one answer in every row.", "Read the rows out loud one by one and see who picked what.",
                                "Play as a team: guess what a partner will pick and score a point for each match."]),
    "wyr": dict(title="Would You Rather", players="2+", time="10-20 min", need="Question cards",
                rules=["Take turns drawing a card and reading it to the group.", "Everyone answers and explains why. No skipping!",
                       "Party version: players who pick the less popular answer get a point."]),
    "trivia": dict(title="Christmas Trivia", players="2+ (or teams)", time="15-25 min", need="Question sheet, pens, answer key",
                   rules=["Give each player or team a question sheet.", "Set a timer (10-15 minutes is good) and let everyone answer.",
                          "Swap sheets and mark them using the answer key.", "One point per correct answer. Most points wins!"]),
    "emoji": dict(title="Emoji Christmas Quiz", players="2+", time="10-15 min", need="Quiz sheet, pens, answer key",
                  rules=["Each row of emoji is a Christmas movie, song or ballet. The category is shown in small letters.",
                         "Write your guess on the line. You have 10 minutes.", "Check with the answer key. Most correct answers wins."]),
    "song_scramble": dict(title="Christmas Song Scramble", players="2+", time="10 min", need="Game sheet, pens, answer key",
                          rules=["Each line is a well-known Christmas song title with the letters mixed up in each word.",
                                 "Unscramble as many titles as you can before the timer runs out.", "Most correct titles wins. Bonus point for humming it!"]),
    "word_scramble": dict(title="Christmas Word Scramble", players="2+", time="10 min", need="Game sheet, pens, answer key",
                          rules=["Unscramble each Christmas word.", "First to finish them all, or the player with the most correct words when time is up, wins."]),
    "word_search": dict(title="Christmas Word Search", players="1+", time="10-15 min", need="Puzzle sheet, pen or highlighter",
                        rules=["Find all the hidden words in the grid. Words can go across, down or diagonally.",
                               "Cross off each word in the list as you find it.", "Race mode: first to find every word wins!"]),
    "find_guest": dict(title="Find the Guest", players="8+", time="15-20 min", need="Game sheets, pens",
                       rules=["Give everyone a sheet. Mingle and find a guest who matches each square.",
                              "Ask them to write their name in the square. Each person may sign only one square on your sheet.",
                              "First to fill a full row (or the whole card) wins. Great icebreaker!"]),
    "phone_hunt": dict(title="What's On Your Phone?", players="3+", time="10 min", need="Game sheets, pens, phones",
                       rules=["Players get points for each item they can find on their own phone.", "The host reads each item out loud. Show it to the group to claim the points.",
                              "Add up the points. Highest score wins!"]),
    "scavenger": dict(title="Christmas Scavenger Hunt", players="2+ (or teams)", time="15-30 min", need="Checklists, pens",
                      rules=["Give each player or team a checklist.", "Find each item around the house (or take a photo of it).",
                             "Tick the box when you find it. First to find everything, or most items when time is up, wins."]),
    "nhie": dict(title="Never Have I Ever", players="3+", time="10-20 min", need="Prompt cards",
                 rules=["Everyone holds up 10 fingers.", "Take turns reading a card: 'Never have I ever...'",
                        "If you HAVE done it, put one finger down.", "The last player with fingers still up wins!"]),
    "truth_dare": dict(title="Truth or Dare", players="3+", time="15-30 min", need="Truth cards and dare cards",
                       rules=["Make two piles: Truth and Dare.", "On your turn, pick a pile and draw a card.",
                              "Answer the truth or do the dare! If you pass, you must do the next card from the other pile.",
                              "All dares are family-friendly and safe to do at a party."]),
    "charades": dict(title="Christmas Charades", players="4+ (2 teams)", time="15-30 min", need="Charades cards, a timer",
                     rules=["Split into two teams.", "One player draws a card and acts it out without talking.",
                            "Their team has 60 seconds to guess. Each correct guess is 1 point.", "Teams take turns. The team with the most points wins."]),
    "pictionary": dict(title="Christmas Pictionary", players="4+ (2 teams)", time="15-30 min", need="Word cards, paper or a whiteboard, a timer",
                       rules=["Split into two teams.", "One player draws a card and sketches the word. No letters or numbers!",
                              "Their team has 60 seconds to guess.", "1 point per correct guess. The team with the most points wins."]),
    "name5": dict(title="Name 5 in 10", players="3+", time="10-15 min", need="Category cards, a timer",
                  rules=["Draw a card and read the category to the player on your left.",
                         "They have 10 seconds to name 5 things in that category.", "If they do it, they keep the card. Most cards wins!"]),
    "dice_gift": dict(title="Roll-the-Dice Gift Exchange", players="5+", time="15-20 min", need="One wrapped gift per player, 1 die, the rules sheet",
                      rules=["Everyone brings one wrapped gift. Sit in a circle with gifts in the middle.",
                             "Round 1: take turns rolling the die and follow the Round 1 action for that number.",
                             "Round 2: set a timer (5-10 minutes). Keep rolling and follow the Round 2 actions.",
                             "When the timer goes off, the gift you are holding is yours!"]),
    "left_right": dict(title="Left Right Gift Exchange", players="4+", time="5-10 min", need="One wrapped gift per player, the story",
                       rules=["Everyone sits in a circle holding a wrapped gift.", "One person reads the story out loud.",
                              "Every time you hear LEFT, pass your gift to the left. Every time you hear RIGHT, pass it to the right.",
                              "When the story ends, the gift in your hands is yours to keep!"]),
    "madlib": dict(title="Christmas Story Fill-In", players="2+", time="10 min", need="Word list, story sheet, pen",
                   rules=["Without showing the story, ask the group for each word on the word list (an adjective, a color...).",
                          "Write the words in the numbered blanks.", "Read the finished story out loud. Expect a lot of laughter!"]),
    "how_many": dict(title="How Many Words?", players="2+", time="10 min", need="Game sheet, pen, a timer",
                     rules=["Make as many words as you can using only the letters in MERRY CHRISTMAS.",
                            "Each letter can be used as many times as it appears.", "3+ letter words only. Most words in 5 minutes wins!"]),
    "two_truths": dict(title="Two Truths & a Lie", players="4+", time="10-20 min", need="Game slips, pens",
                       rules=["Each player writes two true facts and one made-up fact about their holidays.",
                              "Take turns reading them out loud.", "Everyone votes on which one is the lie. You get 1 point for each person you fool!"]),
    "find_coworker": dict(title="Find the Coworker", players="8+", time="15-20 min", need="Game sheets, pens",
                          rules=["Give everyone a sheet. Mingle and find a coworker who matches each square.",
                                 "They sign their name in the square. Each person may sign only one square on your sheet.",
                                 "First to complete a row wins. The perfect icebreaker for teams!"]),
    "desk_hunt": dict(title="Desk Scavenger Hunt", players="4+ (or teams)", time="10-15 min", need="Checklists, pens",
                      rules=["Give each player or team a checklist.", "Find each item at your desk or around the office.",
                             "First to tick every box, or most items when time is up, wins."]),
}


# --------------------------------------------------------------------------- generic helpers
def card_pages(ctx, title, kicker, items, label, key, cols=3, rows=4, label_color=BERRY, icon="holly", text_style=None,
               first_how=True):
    c, W, H = ctx.c, ctx.W, ctx.H
    per = cols * rows
    for start in range(0, len(items), per):
        chunk = items[start:start + per]
        first = start == 0
        y = page_header(c, W, H, title, kicker, title_size=26 if first else 22)
        if first and first_how:
            y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES[key]["rules"])) - 12
        gx, gw = 40, W - 80
        gy = 40
        gh = y - gy
        cw, ch = gw / cols, gh / rows
        cut_grid(c, gx, gy, gw, gh, cols, rows)
        for i, txt in enumerate(chunk):
            col, row = i % cols, i // cols
            x0 = gx + col * cw
            y0 = gy + gh - (row + 1) * ch
            lab = label(txt) if callable(label) else label
            lc = label_color(txt) if callable(label_color) else label_color
            spaced(c, lab, x0 + cw / 2, y0 + ch - 20, size=6.8, color=lc, spacing=1.4)
            body = txt[0] if isinstance(txt, tuple) else txt
            st = text_style or STY["card"]
            size = st.fontSize
            while True:
                s2 = ParagraphStyle("x", parent=st, fontSize=size, leading=size * 1.3)
                p = Paragraph(body, s2)
                _, ph = p.wrap(cw - 26, ch)
                if ph < ch - 52 or size < 7:
                    break
                size -= 0.5
            p.drawOn(c, x0 + 13, y0 + (ch - ph) / 2 - 2)
            if icon == "holly":
                holly(c, x0 + cw / 2, y0 + 15, 8)
            elif icon == "flake":
                snowflake(c, x0 + cw / 2, y0 + 15, 6, SAGE, 0.8)
        ctx.end()


def answer_lines(c, x, y, w, color=LINE):
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    c.line(x, y, x + w, y)


def numbered_rows(ctx, title, kicker, rows, key, row_h=None, two_col=False, draw_row=None, how_text=True):
    """Generic worksheet: header, how-to, numbered rows. rows: list; draw_row(c, i, item, x, y, w, h)."""
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, title, kicker)
    if how_text:
        y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES[key]["rules"])) - 16
    cols = 2 if two_col else 1
    per_col = (len(rows) + cols - 1) // cols
    colw = (W - 96 - (20 if two_col else 0)) / cols
    rh = row_h or min(34, (y - 50) / per_col)
    for i, item in enumerate(rows):
        col, r = i // per_col, i % per_col
        x = 48 + col * (colw + 20)
        yy = y - r * rh
        draw_row(c, i, item, x, yy, colw, rh)
    ctx.end()


def answer_key_page(ctx, title, pairs, two_col=True, size=9.5):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, title, "answer key", title_size=24)
    cols = 2 if two_col and len(pairs) > 12 else 1
    per = (len(pairs) + cols - 1) // cols
    colw = (W - 100) / cols
    rh = min(26, (y - 60) / per)
    for i, (q, a) in enumerate(pairs):
        col, r = i // per, i % per
        x = 50 + col * colw
        yy = y - r * rh
        c.setFont("Montserrat-Bold", size)
        c.setFillColor(BERRY)
        c.drawString(x, yy, f"{i + 1}.")
        c.setFillColor(INK)
        c.setFont("Montserrat-Medium", size)
        txt = a if not q else f"{a}"
        c.drawString(x + 22, yy, txt)
        if q:
            c.setFont("Montserrat-Regular", size - 2)
            c.setFillColor(MUTED)
            c.drawString(x + 22, yy - 10, q[:70])
    ctx.end()


# --------------------------------------------------------------------------- individual games
def g_most_likely(ctx, office=False):
    items = K.MOST_LIKELY_OFFICE if office else K.MOST_LIKELY
    card_pages(ctx, "Who's Most Likely To", "office edition" if office else "christmas edition",
               [f"...{t}?" for t in items], "who's most likely to", "most_likely")


def g_wyr(ctx):
    card_pages(ctx, "Would You Rather", "christmas edition", K.WOULD_YOU_RATHER, "would you rather", "wyr", icon="flake")


def g_nhie(ctx):
    card_pages(ctx, "Never Have I Ever", "christmas edition", [f"Never have I ever {t}." for t in K.NEVER_HAVE_I_EVER],
               "never have i ever", "nhie")


def g_truth_dare(ctx):
    items = [("<b>Truth:</b> " + t) for t in K.TRUTHS] + [("<b>Dare:</b> " + d) for d in K.DARES]
    card_pages(ctx, "Truth or Dare", "family-friendly", items,
               lambda t: "truth" if "Truth" in t else "dare", "truth_dare",
               label_color=lambda t: PINE2 if "Truth" in t else BERRY)


def g_charades(ctx):
    card_pages(ctx, "Christmas Charades", "act it out", K.CHARADES, "act it out", "charades", cols=4, rows=6,
               text_style=STY["cardbig"].clone("cb2", fontSize=13.5, leading=16.5), icon=None)


def g_pictionary(ctx):
    card_pages(ctx, "Christmas Pictionary", "draw it", K.PICTIONARY, "draw it", "pictionary", cols=4, rows=6,
               text_style=STY["cardbig"].clone("cb3", fontSize=14, leading=17), icon=None)


def g_name5(ctx):
    card_pages(ctx, "Name 5 in 10 Seconds", "fast thinking", K.NAME_5, "name 5...", "name5", cols=3, rows=5,
               text_style=STY["cardbig"].clone("cb4", fontSize=14, leading=17.5), icon="flake")


def g_this_or_that(ctx, office=False):
    pairs = K.THIS_OR_THAT_OFFICE if office else K.THIS_OR_THAT
    per = len(pairs) if len(pairs) <= 24 else 20
    for pi in range(0, len(pairs), per):
        chunk = pairs[pi:pi + per]

        def row(c, i, item, x, y, w, h):
            a, b = item
            n = pi + i + 1
            c.setFont("Montserrat-Bold", 9)
            c.setFillColor(GOLD)
            c.drawString(x, y - h * 0.55, f"{n:02d}")
            cx = x + w / 2
            c.setFillColor(CREAM)
            c.setStrokeColor(CREAM2)
            c.roundRect(x + 26, y - h + 4, w - 26, h - 6, 6, fill=1, stroke=1)
            sz = fit_font(a, "Montserrat-Medium", 10.5, w / 2 - 70)
            c.setFont("Montserrat-Medium", sz)
            c.setFillColor(INK)
            c.drawCentredString(cx - w * 0.22 + 13, y - h * 0.58, a)
            sz = fit_font(b, "Montserrat-Medium", 10.5, w / 2 - 70)
            c.setFont("Montserrat-Medium", sz)
            c.drawCentredString(cx + w * 0.22 + 13, y - h * 0.58, b)
            c.setFont("Playfair-Italic", 11)
            c.setFillColor(BERRY)
            c.drawCentredString(cx + 13, y - h * 0.58, "or")

        numbered_rows(ctx, "This or That", ("office edition" if office else "christmas edition") + (f" · part {pi // per + 1}" if len(pairs) > per else ""),
                      chunk, "this_or_that", draw_row=row, how_text=pi == 0)


def g_trivia(ctx, office=False):
    qs = K.TRIVIA_OFFICE if office else K.TRIVIA
    per = len(qs) if len(qs) <= 20 else 15
    for pi in range(0, len(qs), per):
        chunk = qs[pi:pi + per]

        def row(c, i, item, x, y, w, h):
            q, _ = item
            n = pi + i + 1
            c.setFont("Playfair-Bold", 12)
            c.setFillColor(BERRY)
            c.drawString(x, y - 13, f"{n}.")
            para(c, q, x + 26, y - 2, w - 26, STY["body"].clone("tq", fontSize=10, leading=13))
            answer_lines(c, x + 26, y - h + 8, w - 26)

        numbered_rows(ctx, "Christmas Trivia", f"part {pi // per + 1} of {(len(qs) + per - 1) // per}" if len(qs) > per else "test your knowledge", chunk, "trivia",
                      draw_row=row, how_text=pi == 0, row_h=None)
    answer_key_page(ctx, "Christmas Trivia", [(None, a) for _, a in qs])


def g_emoji(ctx):
    items = K.EMOJI_QUIZ

    def row(c, i, item, x, y, w, h):
        seq, ans, cat = item
        c.setFont("Montserrat-Bold", 9)
        c.setFillColor(GOLD)
        c.drawString(x, y - h / 2 - 3, f"{i + 1:02d}")
        es = min(h - 12, 26)
        emoji_row(c, seq, x + 30 + (len(seq) * (es + 4)) / 2, y - h / 2 + 2, es, 4)
        spaced(c, cat, x + w - 4, y - 12, size=6, color=MUTED, spacing=1.2, anchor="right")
        answer_lines(c, x + 150, y - h + 8, w - 150)

    numbered_rows(ctx, "Emoji Christmas Quiz", "movies · songs · ballet", items, "emoji", draw_row=row, two_col=True)
    answer_key_page(ctx, "Emoji Christmas Quiz", [(None, a) for _, a, _ in items])


def g_song_scramble(ctx):
    items = K.SONG_TITLES

    def row(c, i, item, x, y, w, h):
        c.setFont("Montserrat-Bold", 9)
        c.setFillColor(GOLD)
        c.drawString(x, y - 14, f"{i + 1:02d}")
        c.setFont("Montserrat-SemiBold", 12)
        c.setFillColor(PINE)
        c.drawString(x + 28, y - 14, scramble(item, i + 11))
        answer_lines(c, x + 28 + (w - 28) * 0.52, y - 16, (w - 28) * 0.48)

    numbered_rows(ctx, "Christmas Song Scramble", "unscramble the titles", items, "song_scramble", draw_row=row)
    answer_key_page(ctx, "Christmas Song Scramble", [(None, a) for a in items])


def g_word_scramble(ctx):
    items = K.SCRAMBLE_WORDS

    def row(c, i, item, x, y, w, h):
        c.setFont("Montserrat-Bold", 9)
        c.setFillColor(GOLD)
        c.drawString(x, y - 16, f"{i + 1:02d}")
        c.setFont("Montserrat-SemiBold", 13)
        c.setFillColor(PINE)
        c.drawString(x + 28, y - 16, scramble(item, i + 3))
        answer_lines(c, x + 28, y - h + 6, w - 40)

    numbered_rows(ctx, "Christmas Word Scramble", "unscramble the words", items, "word_scramble", draw_row=row, two_col=True)
    answer_key_page(ctx, "Christmas Word Scramble", [(None, a) for a in items])


def make_word_search(words, n, seed, diag=True):
    rnd = random.Random(seed)
    while True:
        grid = [[None] * n for _ in range(n)]
        placed = {}
        dirs = [(0, 1), (1, 0), (1, 1), (-1, 1)] if diag else [(0, 1), (1, 0)]
        ok = True
        for w in sorted(words, key=len, reverse=True):
            for _ in range(400):
                dr, dc = rnd.choice(dirs)
                r = rnd.randrange(n)
                cc = rnd.randrange(n)
                cells = [(r + dr * k, cc + dc * k) for k in range(len(w))]
                if all(0 <= a < n and 0 <= b < n and grid[a][b] in (None, w[k]) for k, (a, b) in enumerate(cells)):
                    for k, (a, b) in enumerate(cells):
                        grid[a][b] = w[k]
                    placed[w] = cells
                    break
            else:
                ok = False
                break
        if ok:
            break
        seed += 1
        rnd = random.Random(seed)
    letters = "ABCDEFGHIKLMNOPRSTUWY"
    for a in range(n):
        for b in range(n):
            if grid[a][b] is None:
                grid[a][b] = rnd.choice(letters)
    return grid, placed


def draw_word_search(c, grid, placed, x, y, size, highlight=False, font="Montserrat-SemiBold"):
    n = len(grid)
    cell = size / n
    rounded_card(c, x - 8, y - 8, size + 16, size + 16, CREAM, CREAM2, 10)
    if highlight:
        c.saveState()
        c.setStrokeColor(GOLD)
        c.setStrokeAlpha(0.45)
        c.setLineWidth(cell * 0.72)
        c.setLineCap(1)
        for w, cells in placed.items():
            (r0, c0), (r1, c1) = cells[0], cells[-1]
            c.line(x + c0 * cell + cell / 2, y + size - r0 * cell - cell / 2, x + c1 * cell + cell / 2, y + size - r1 * cell - cell / 2)
        c.restoreState()
    c.setFillColor(INK)
    c.setFont(font, cell * 0.52)
    for r in range(n):
        for cc in range(n):
            c.drawCentredString(x + cc * cell + cell / 2, y + size - r * cell - cell * 0.68, grid[r][cc])


def g_word_search(ctx, words=None, n=15, title="Christmas Word Search", seed=21, diag=True):
    words = words or K.WORD_SEARCH
    c, W, H = ctx.c, ctx.W, ctx.H
    grid, placed = make_word_search(words, n, seed, diag)
    y = page_header(c, W, H, title, "find all the words")
    y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES["word_search"]["rules"])) - 22
    size = min(W - 150, y - 180)
    gx = (W - size) / 2
    draw_word_search(c, grid, placed, gx, y - size, size)
    # word list
    cols = 4 if len(words) > 10 else 5
    yy = y - size - 40
    colw = (W - 120) / cols
    per = (len(words) + cols - 1) // cols
    for i, w in enumerate(sorted(words)):
        col, r = i // per, i % per
        c.setStrokeColor(SAGE)
        c.rect(60 + col * colw, yy - r * 18 - 1, 8, 8, fill=0, stroke=1)
        c.setFont("Montserrat-Medium", 10)
        c.setFillColor(INK)
        c.drawString(74 + col * colw, yy - r * 18, w)
    ctx.end()
    # key
    y = page_header(c, W, H, title, "answer key", title_size=24)
    size2 = min(W - 160, y - 80)
    draw_word_search(c, grid, placed, (W - size2) / 2, y - size2 - 10, size2, highlight=True)
    ctx.end()


def bingo_grid(c, x, y, size, cells, title="BINGO", pictures=False, card_no=None):
    hdr = size * 0.16
    rounded_card(c, x, y, size, size + hdr + 26, white, PINE, 10, 1.4)
    c.setFillColor(PINE)
    c.roundRect(x, y + size + 10, size, hdr + 16, 10, fill=1, stroke=0)
    c.rect(x, y + size + 10, size, 10, fill=1, stroke=0)
    letters = list(title)
    cw = size / 5
    for i, L in enumerate(letters):
        c.setFont("Playfair-Black", hdr * 0.72)
        c.setFillColor(CREAM)
        c.drawCentredString(x + cw * i + cw / 2, y + size + 10 + hdr * 0.35, L)
    gx, gy = x + 6, y + 6
    gs = size - 12
    cs = gs / 5
    for r in range(5):
        for k in range(5):
            cx0, cy0 = gx + k * cs, gy + gs - (r + 1) * cs
            c.setStrokeColor(LINE)
            c.setLineWidth(0.8)
            c.setFillColor(white)
            c.rect(cx0, cy0, cs, cs, fill=1, stroke=1)
            item = cells[r * 5 + k]
            if item is None:
                c.setFillColor(CREAM)
                c.rect(cx0 + 2, cy0 + 2, cs - 4, cs - 4, fill=1, stroke=0)
                draw_star(c, cx0 + cs / 2, cy0 + cs * 0.58, cs * 0.2)
                c.setFont("Montserrat-Bold", cs * 0.13)
                c.setFillColor(BERRY)
                c.drawCentredString(cx0 + cs / 2, cy0 + cs * 0.17, "FREE")
            elif pictures:
                ch, name = item
                draw_emoji(c, ch, cx0 + cs / 2, cy0 + cs * 0.58, cs * 0.52)
                c.setFont("Montserrat-Medium", fit_font(name, "Montserrat-Medium", cs * 0.12, cs - 6))
                c.setFillColor(MUTED)
                c.drawCentredString(cx0 + cs / 2, cy0 + cs * 0.1, name)
            else:
                fs = min(10.5, cs * 0.17)
                for wd in item.split():
                    fs = min(fs, fit_font(wd, "Montserrat-Medium", fs, cs - 10, 5))
                p = Paragraph(item, STY["card"].clone("bg", fontSize=fs, leading=fs * 1.2))
                _, ph = p.wrap(cs - 6, cs)
                p.drawOn(c, cx0 + 3, cy0 + (cs - ph) / 2)
    if card_no:
        c.setFont("Montserrat-Regular", 6.5)
        c.setFillColor(MUTED)
        c.drawRightString(x + size - 4, y - 10, f"card {card_no}")


def g_bingo(ctx, n_cards=30, pictures=False, title_kicker=None, how_page=True, seed=5):
    c, W, H = ctx.c, ctx.W, ctx.H
    pool = K.BINGO_PICTURES if pictures else K.BINGO_WORDS
    rnd = random.Random(seed + (100 if pictures else 0))
    cards = []
    seen = set()
    while len(cards) < n_cards:
        pick = rnd.sample(pool, 24)
        key = tuple(sorted(str(p) for p in pick))
        if key in seen:
            continue
        seen.add(key)
        cells = pick[:12] + [None] + pick[12:]
        cards.append(cells)
    name = "Picture Bingo" if pictures else "Christmas Bingo"
    if how_page:
        y = page_header(c, W, H, name, title_kicker or ("for kids & families" if pictures else "word edition"))
        y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES["bingo"]["rules"])) - 30
        size = min(W - 200, y - 100)
        bingo_grid(c, (W - size) / 2, y - size - size * 0.16 - 26, size, cards[0], pictures=pictures, card_no=1)
        ctx.end()
        rest = cards[1:]
        start_no = 2
    else:
        rest = cards
        start_no = 1
    # two cards per page
    size = min(W * 0.52, (H - 120) / 2 - 60)
    for i in range(0, len(rest), 2):
        for j, cells in enumerate(rest[i:i + 2]):
            yb = H / 2 + 18 if j == 0 else 52
            bingo_grid(c, (W - size) / 2, yb, size, cells, pictures=pictures, card_no=start_no + i + j)
        c.saveState()
        c.setDash(3, 3)
        c.setStrokeColor(LINE)
        c.line(30, H / 2, W - 30, H / 2)
        c.restoreState()
        ctx.end()
    # calling cards
    cols, rows = 5, 8
    for start in range(0, len(pool), cols * rows):
        y = page_header(c, W, H, name, "calling cards · cut & draw", title_size=22)
        gx, gy, gw = 40, 40, W - 80
        gh = y - gy
        cut_grid(c, gx, gy, gw, gh, cols, rows)
        cw, chh = gw / cols, gh / rows
        for i, it in enumerate(pool[start:start + cols * rows]):
            col, r = i % cols, i // cols
            x0, y0 = gx + col * cw, gy + gh - (r + 1) * chh
            if pictures:
                draw_emoji(c, it[0], x0 + cw / 2, y0 + chh * 0.6, chh * 0.45)
                c.setFont("Montserrat-Medium", 8)
                c.setFillColor(INK)
                c.drawCentredString(x0 + cw / 2, y0 + chh * 0.14, it[1])
            else:
                c.setFont("Playfair-Bold", fit_font(it, "Playfair-Bold", 13, cw - 14))
                c.setFillColor(PINE)
                c.drawCentredString(x0 + cw / 2, y0 + chh / 2 - 3, it)
                snowflake(c, x0 + cw / 2, y0 + 11, 4, SAGE, 0.6)
        ctx.end()


def human_bingo(ctx, title, items, key, kicker):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, title, kicker)
    y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES[key]["rules"])) - 14
    size = min(W - 80, y - 46)
    x0 = (W - size) / 2
    cs = size / 5
    cells = items[:12] + [None] + items[12:24]
    for r in range(5):
        for k in range(5):
            cx0, cy0 = x0 + k * cs, y - (r + 1) * cs
            c.setStrokeColor(PINE)
            c.setLineWidth(0.9)
            c.setFillColor(white)
            c.rect(cx0, cy0, cs, cs, fill=1, stroke=1)
            it = cells[r * 5 + k]
            if it is None:
                c.setFillColor(PINE)
                c.rect(cx0, cy0, cs, cs, fill=1, stroke=0)
                draw_star(c, cx0 + cs / 2, cy0 + cs * 0.58, cs * 0.18)
                c.setFillColor(CREAM)
                c.setFont("Montserrat-Bold", 7.5)
                c.drawCentredString(cx0 + cs / 2, cy0 + cs * 0.2, "FREE SPACE")
                continue
            c.setFont("Montserrat-Bold", 6)
            c.setFillColor(BERRY)
            c.drawCentredString(cx0 + cs / 2, cy0 + cs - 12, "FIND SOMEONE WHO")
            p = Paragraph(it, STY["card"].clone("hb", fontSize=8.2, leading=10.2))
            _, ph = p.wrap(cs - 10, cs)
            p.drawOn(c, cx0 + 5, cy0 + cs * 0.55 - ph / 2)
            c.setStrokeColor(LINE)
            c.line(cx0 + 8, cy0 + 14, cx0 + cs - 8, cy0 + 14)
            c.setFont("Montserrat-Regular", 5.5)
            c.setFillColor(MUTED)
            c.drawCentredString(cx0 + cs / 2, cy0 + 6, "name")
    ctx.end()


def g_find_guest(ctx):
    human_bingo(ctx, "Find the Guest", K.FIND_THE_GUEST, "find_guest", "party icebreaker")


def g_find_coworker(ctx):
    human_bingo(ctx, "Find the Coworker", K.FIND_THE_COWORKER, "find_coworker", "office icebreaker")


def checklist(ctx, title, kicker, items, key, points=False):
    def row(c, i, item, x, y, w, h):
        txt, pts = item if points else (item, None)
        c.setStrokeColor(PINE2)
        c.setLineWidth(1)
        c.roundRect(x + 2, y - h + 8, 13, 13, 3, fill=0, stroke=1)
        size = fit_font(txt, "Montserrat-Medium", 10.5, w - (110 if points else 40))
        c.setFont("Montserrat-Medium", size)
        c.setFillColor(INK)
        c.drawString(x + 26, y - h + 11, txt)
        if points:
            c.setFillColor(BERRY)
            c.roundRect(x + w - 54, y - h + 6, 54, 17, 8, fill=1, stroke=0)
            c.setFillColor(CREAM)
            c.setFont("Montserrat-Bold", 8.5)
            c.drawCentredString(x + w - 27, y - h + 11.5, f"{pts} pts")
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(x, y - h + 2, x + w, y - h + 2)

    numbered_rows(ctx, title, kicker, items, key, draw_row=row, two_col=not points)
    if points:
        pass


def g_phone_hunt(ctx):
    checklist(ctx, "What's On Your Phone?", "christmas edition", K.PHONE_HUNT, "phone_hunt", points=True)


def g_scavenger(ctx):
    checklist(ctx, "Christmas Scavenger Hunt", "around the house", K.SCAVENGER_HOME, "scavenger")


def g_desk_hunt(ctx):
    checklist(ctx, "Desk Scavenger Hunt", "office edition", K.SCAVENGER_DESK, "desk_hunt")


def die_face(c, x, y, s, n):
    c.setFillColor(white)
    c.setStrokeColor(PINE)
    c.setLineWidth(1.4)
    c.roundRect(x, y, s, s, s * 0.18, fill=1, stroke=1)
    pos = {1: [(0.5, 0.5)], 2: [(0.27, 0.73), (0.73, 0.27)], 3: [(0.27, 0.73), (0.5, 0.5), (0.73, 0.27)],
           4: [(0.27, 0.27), (0.27, 0.73), (0.73, 0.27), (0.73, 0.73)],
           5: [(0.27, 0.27), (0.27, 0.73), (0.5, 0.5), (0.73, 0.27), (0.73, 0.73)],
           6: [(0.27, 0.25), (0.27, 0.5), (0.27, 0.75), (0.73, 0.25), (0.73, 0.5), (0.73, 0.75)]}[n]
    c.setFillColor(BERRY)
    for px, py in pos:
        c.circle(x + px * s, y + py * s, s * 0.085, fill=1, stroke=0)


def g_dice_gift(ctx, office=False):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "Roll-the-Dice Gift Exchange", "office edition" if office else "a gift swap with a twist")
    y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES["dice_gift"]["rules"])) - 18
    rh = min(42, (y - 60 - 2 * 36) / 12)
    for label, rows in (("Round 1 · take turns", K.DICE_GIFT_ROUND1), ("Round 2 · timer on!", K.DICE_GIFT_ROUND2)):
        spaced(c, label, W / 2, y, size=9, color=BERRY)
        y -= 14
        for n, txt in rows:
            die_face(c, 70, y - rh + 4, rh - 8, n)
            c.setFont("Montserrat-Medium", fit_font(txt, "Montserrat-Medium", 12, W - 220))
            c.setFillColor(INK)
            c.drawString(70 + rh + 8, y - rh / 2 - 2, txt)
            c.setStrokeColor(LINE)
            c.setLineWidth(0.5)
            c.line(70, y - rh, W - 70, y - rh)
            y -= rh
        y -= 22
    ctx.end()


def story_pages(ctx, title, kicker, text, key="left_right", how_text=True):
    c, W, H = ctx.c, ctx.W, ctx.H
    paras = [p.strip() for p in text.split("\n\n")]
    st = STY["story"].clone("st2", fontSize=11.5, leading=17.5)
    first = True
    i = 0
    while i < len(paras):
        y = page_header(c, W, H, title, kicker, title_size=26 if first else 22)
        if first and how_text:
            y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES[key]["rules"])) - 16
        first = False
        while i < len(paras):
            p = Paragraph(paras[i].replace("<b>LEFT</b>", "<font color='#A3302B'><b>LEFT</b></font>").replace("<b>RIGHT</b>", "<font color='#2F5A43'><b>RIGHT</b></font>"), st)
            _, ph = p.wrap(W - 140, H)
            if y - ph < 60:
                break
            p.drawOn(c, 70, y - ph)
            y -= ph + 12
            i += 1
        if i == len(paras):
            holly(c, W / 2, max(y - 20, 60), 16)
        ctx.end()


def g_left_right(ctx, which="family"):
    text = {"family": K.LEFT_RIGHT_FAMILY, "office": K.LEFT_RIGHT_OFFICE, "kids": K.LEFT_RIGHT_KIDS}[which]
    kick = {"family": "family story", "office": "office story", "kids": "short story for kids"}[which]
    story_pages(ctx, "Left Right Gift Exchange", kick, text)


def g_madlib(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "Christmas Story Fill-In", "step 1 · collect the words")
    y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES["madlib"]["rules"])) - 20
    n = len(K.MADLIB_BLANKS)
    per = (n + 1) // 2
    rh = min(36, (y - 60) / per)
    for i, b in enumerate(K.MADLIB_BLANKS):
        col, r = i // per, i % per
        x = 60 + col * (W - 120) / 2
        yy = y - r * rh
        c.setFont("Montserrat-Bold", 10)
        c.setFillColor(BERRY)
        c.drawString(x, yy - 14, f"{i + 1}.")
        answer_lines(c, x + 24, yy - 16, (W - 120) / 2 - 50)
        c.setFont("Montserrat-Regular", 7)
        c.setFillColor(MUTED)
        c.drawString(x + 24, yy - 25, b.lower())
    ctx.end()
    y = page_header(c, W, H, "Christmas Story Fill-In", "step 2 · read it out loud")
    text = K.MADLIB
    k = [0]
    import re

    def sub(m):
        k[0] += 1
        return f"<font color='#A3302B'>________</font><font size=8 color='#8A847A'>({k[0]})</font>"
    text = re.sub(r"\[[^\]]+\]", sub, text)
    for ptxt in text.split("\n\n"):
        y -= para(c, ptxt, 70, y, W - 140, STY["story"].clone("ml", leading=26)) + 14
    holly(c, W / 2, y - 16, 16)
    ctx.end()


def g_how_many(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "How Many Words?", "word challenge")
    y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES["how_many"]["rules"])) - 30
    word = "MERRY CHRISTMAS"
    tile = min(30, (W - 120) / 16)
    x = W / 2 - len(word) * (tile + 3) / 2
    for ch in word:
        if ch != " ":
            c.setFillColor(PINE)
            c.roundRect(x, y - tile, tile, tile, 4, fill=1, stroke=0)
            c.setFillColor(CREAM)
            c.setFont("Playfair-Black", tile * 0.6)
            c.drawCentredString(x + tile / 2, y - tile * 0.72, ch)
        x += tile + 3
    y -= tile + 26
    cols, rows = 3, 14
    rh = (y - 60) / rows
    colw = (W - 120) / cols
    for i in range(cols * rows):
        col, r = i // rows, i % rows
        xx = 60 + col * colw
        yy = y - r * rh
        c.setFont("Montserrat-Regular", 8)
        c.setFillColor(GOLD)
        c.drawRightString(xx + 14, yy - rh + 6, str(i + 1))
        answer_lines(c, xx + 20, yy - rh + 5, colw - 34)
    ctx.end()


def g_two_truths(ctx):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "Two Truths & a Lie", "holiday edition")
    y = how_to_box(c, 48, y + 4, W - 96, " ".join(RULES["two_truths"]["rules"])) - 12
    gx, gy, gw, gh = 40, 40, W - 80, y - 40
    cut_grid(c, gx, gy, gw, gh, 2, 2)
    for i in range(4):
        col, r = i % 2, i // 2
        x0, y0 = gx + col * gw / 2, gy + gh - (r + 1) * gh / 2
        cw, ch = gw / 2, gh / 2
        c.setFont("Montserrat-Regular", 8)
        c.setFillColor(MUTED)
        c.drawString(x0 + 18, y0 + ch - 26, "Name:")
        answer_lines(c, x0 + 50, y0 + ch - 27, cw - 70)
        for k in range(3):
            yy = y0 + ch - 70 - k * (ch - 90) / 3
            c.setFillColor(GOLD)
            c.circle(x0 + 26, yy + 3, 8, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont("Montserrat-Bold", 8)
            c.drawCentredString(x0 + 26, yy, str(k + 1))
            answer_lines(c, x0 + 42, yy - 2, cw - 62)
            answer_lines(c, x0 + 42, yy - 22, cw - 62)
    ctx.end()


def g_scoreboard(ctx, games=None):
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, "Party Scoreboard", "keep track of the winners")
    cols = 7
    rows = 14
    tw = W - 90
    first = tw * 0.28
    cw = (tw - first) / (cols - 1)
    rh = (y - 70) / (rows + 1)
    x0 = 45
    c.setFillColor(PINE)
    c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont("Montserrat-Bold", 8)
    c.drawString(x0 + 10, y - rh * 0.62, "PLAYER / TEAM")
    for k in range(cols - 2):
        c.drawCentredString(x0 + first + cw * k + cw / 2, y - rh * 0.62, f"GAME {k + 1}")
    c.drawCentredString(x0 + first + cw * (cols - 2) + cw / 2, y - rh * 0.62, "TOTAL")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    for r in range(1, rows + 1):
        yy = y - (r + 1) * rh
        if r % 2 == 0:
            c.setFillColor(CREAM)
            c.rect(x0, yy, tw, rh, fill=1, stroke=0)
        c.line(x0, yy, x0 + tw, yy)
    for k in range(cols):
        xx = x0 + first + cw * k if k < cols else x0 + tw
        c.line(xx, y - rh, xx, y - (rows + 1) * rh)
    c.rect(x0, y - (rows + 1) * rh, tw, rows * rh + rh, fill=0, stroke=1)
    ctx.end()


def g_certificates(ctx, awards=None):
    c, W, H = ctx.c, ctx.W, ctx.H
    awards = awards or ["Party Game Champion", "Trivia Master", "Best Ugly Sweater", "Bingo Legend"]
    for i in range(0, len(awards), 2):
        for j, aw in enumerate(awards[i:i + 2]):
            y0 = H / 2 + 12 if j == 0 else 24
            h = H / 2 - 36
            c.setFillColor(CREAM)
            c.setStrokeColor(GOLD)
            c.setLineWidth(1.2)
            c.roundRect(36, y0, W - 72, h, 12, fill=1, stroke=1)
            c.roundRect(44, y0 + 8, W - 88, h - 16, 9, fill=0, stroke=1)
            holly(c, W / 2, y0 + h - 36, 18)
            spaced(c, "certificate of awesome", W / 2, y0 + h - 70, size=8, color=GOLD, spacing=2.5)
            c.setFont("Playfair-Black", fit_font(aw, "Playfair-Black", 30, W - 160))
            c.setFillColor(PINE)
            c.drawCentredString(W / 2, y0 + h - 108, aw)
            c.setFont("Montserrat-Regular", 9)
            c.setFillColor(MUTED)
            c.drawCentredString(W / 2, y0 + h - 132, "proudly presented to")
            answer_lines(c, W / 2 - 150, y0 + h * 0.3, 300, PINE2)
            c.setFont("GreatVibes", 22)
            c.setFillColor(BERRY)
            c.drawCentredString(W / 2, y0 + 30, "Merry Christmas")
        c.saveState()
        c.setDash(3, 3)
        c.setStrokeColor(LINE)
        c.line(30, H / 2, W - 30, H / 2)
        c.restoreState()
        ctx.end(footer_on=False)


def contents_page(ctx, title, entries, intro=None):
    """entries: list of (name, page)."""
    c, W, H = ctx.c, ctx.W, ctx.H
    y = page_header(c, W, H, title, "what's inside")
    if intro:
        y -= para(c, intro, 80, y, W - 160, "bodyc") + 14
    cols = 2 if len(entries) > 14 else 1
    per = (len(entries) + cols - 1) // cols
    colw = (W - 120) / cols
    rh = min(24, (y - 60) / per)
    for i, (name, pg) in enumerate(entries):
        col, r = i // per, i % per
        x = 60 + col * colw
        yy = y - r * rh
        c.setFont("Montserrat-Bold", 9)
        c.setFillColor(GOLD)
        c.drawString(x, yy - 12, f"{i + 1:02d}")
        c.setFont("Montserrat-Medium", 10.5)
        c.setFillColor(INK)
        c.drawString(x + 24, yy - 12, name)
        c.setFont("Montserrat-Regular", 9)
        c.setFillColor(MUTED)
        c.drawRightString(x + colw - 18, yy - 12, f"p. {pg}")
        c.setStrokeColor(LINE)
        c.setDash(1, 2)
        nw = pdfmetrics.stringWidth(name, "Montserrat-Medium", 10.5)
        c.line(x + 30 + nw, yy - 11, x + colw - 42, yy - 11)
        c.setDash()
    ctx.end()


def host_guide(path, W, H, product, keys, cover_title, intro, extra_tips=None):
    """Separate 'How to play' booklet."""
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(f"{product} - How to Play Guide")
    c.setAuthor(BRAND)
    ctx = Ctx(c, W, H, product)
    y = page_header(c, W, H, "How to Play", cover_title)
    y -= para(c, intro, 70, y, W - 140, "bodyc") + 18
    st_r = STY["small"].clone("rr", fontSize=9, leading=12.5)
    for k in keys:
        r = RULES[k]
        body = "".join(f"<bullet>&bull;</bullet>{t}<br/>" for t in r["rules"])
        p = Paragraph("<br/>".join(f"&bull;&nbsp; {t}" for t in r["rules"]), st_r)
        _, ph = p.wrap(W - 190, H)
        need = 46 + ph
        if y - need < 50:
            ctx.end()
            y = H - 60
        c.setFillColor(CREAM)
        c.setStrokeColor(CREAM2)
        c.roundRect(55, y - need, W - 110, need - 6, 8, fill=1, stroke=1)
        c.setFont("Playfair-Bold", 13.5)
        c.setFillColor(PINE)
        c.drawString(70, y - 24, r["title"])
        c.setFont("Montserrat-Regular", 7.5)
        c.setFillColor(BERRY)
        meta = f"PLAYERS {r['players']}   ·   TIME {r['time']}"
        c.drawRightString(W - 70, y - 22, meta)
        c.setFont("Montserrat-Regular", 7.5)
        c.setFillColor(MUTED)
        c.drawString(70, y - 36, "You'll need: " + r["need"])
        p.drawOn(c, 70, y - 42 - ph)
        y -= need + 4
    if extra_tips:
        if y < 200:
            ctx.end()
            y = H - 60
        y -= 10
        spaced(c, "host tips", W / 2, y, size=8.5)
        y -= 12
        for t in extra_tips:
            y -= para(c, "&bull;&nbsp; " + t, 80, y, W - 160, "small") + 4
    ctx.end()
    c.save()
