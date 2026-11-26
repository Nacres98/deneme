"""Etsy listing images (3000x2250, 4:3) + short preview video for each product."""
import glob
import json
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FONTS = os.path.join(HERE, "fonts")
CACHE = os.path.join(HERE, "cache")
sys.path.insert(0, HERE)
from products import P  # noqa

W, H = 3000, 2250
PINE = (30, 58, 43)
PINE2 = (47, 90, 67)
PINE_LIGHT = (46, 84, 66)
BERRY = (163, 48, 43)
GOLD = (184, 145, 58)
CREAM = (251, 247, 239)
CREAM2 = (241, 233, 216)
INK = (42, 42, 42)
MUTED = (138, 132, 122)


def F(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), size)


def pages(key, pdf_suffix="US-Letter"):
    d = os.path.join(CACHE, "pages", key)
    if not glob.glob(os.path.join(d, "p-*.png")):
        os.makedirs(d, exist_ok=True)
        pdf = sorted(glob.glob(os.path.join(ROOT, P[key]["dir"], "upload_files", f"{P[key]['file']}_*{pdf_suffix}.pdf")))[0]
        subprocess.run(["pdftoppm", "-r", "110", "-png", pdf, os.path.join(d, "p")], check=True)
    files = sorted(glob.glob(os.path.join(d, "p-*.png")))
    return {int(os.path.basename(f)[2:-4]): f for f in files}


def toc(key):
    p = os.path.join(CACHE, f"toc_{key}.json")
    return dict(json.load(open(p))) if os.path.exists(p) else {}


def snow_bg(color=PINE, flake=PINE_LIGHT, seed=1, n=70):
    im = Image.new("RGB", (W, H), color)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(14, 40)
        for i in range(6):
            a = math.radians(90 + 60 * i)
            ex, ey = x + r * math.cos(a), y + r * math.sin(a)
            d.line([(x, y), (ex, ey)], fill=flake, width=3)
            for f in (0.5,):
                bx, by = x + r * f * math.cos(a), y + r * f * math.sin(a)
                for s in (35, -35):
                    b = a + math.radians(s)
                    d.line([(bx, by), (bx + r * 0.3 * math.cos(b), by + r * 0.3 * math.sin(b))], fill=flake, width=3)
    return im


def paper(path, width, border=True):
    im = Image.open(path).convert("RGB")
    k = width / im.width
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    if border:
        ImageDraw.Draw(im).rectangle([0, 0, im.width - 1, im.height - 1], outline=(225, 220, 210), width=2)
    return im


def place(base, im, cx, cy, angle=0, shadow=40):
    im = im.convert("RGBA")
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (im.width + shadow * 4, im.height + shadow * 4), (0, 0, 0, 0))
    alpha = im.split()[3].point(lambda a: 85 if a > 0 else 0)
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255))
    blk.putalpha(alpha)
    sh.paste(blk, (shadow * 2, shadow * 2), blk)
    sh = sh.filter(ImageFilter.GaussianBlur(shadow * 0.6))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    base.paste(sh, (x - shadow * 2 + 18, y - shadow * 2 + 30), sh)
    base.paste(im, (x, y), im)


def text_c(d, xy, txt, font, fill, anchor="mm"):
    d.text(xy, txt, font=font, fill=fill, anchor=anchor)


def spaced(d, xy, txt, font, fill, spacing=10, anchor="m"):
    txt = txt.upper()
    widths = [d.textlength(ch, font=font) for ch in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    x = xy[0] - total / 2 if anchor == "m" else xy[0]
    for ch, w in zip(txt, widths):
        d.text((x, xy[1]), ch, font=font, fill=fill, anchor="lm")
        x += w + spacing


def pill(d, cx, cy, txt, font, bg, fg, padx=46, h=96):
    w = d.textlength(txt, font=font) + padx * 2
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2, fill=bg)
    d.text((cx, cy + 2), txt, font=font, fill=fg, anchor="mm")
    return w


def holly(d, cx, cy, s):
    for sgn in (-1, 1):
        pts = []
        for i in range(13):
            t = i / 12
            half = math.sin(math.pi * t) * s * 0.21 * (0.72 if i % 2 else 1)
            pts.append((cx + sgn * s * t, cy - half))
        for i in range(12, -1, -1):
            t = i / 12
            half = math.sin(math.pi * t) * s * 0.21 * (0.72 if i % 2 else 1)
            pts.append((cx + sgn * s * t, cy + half))
        d.polygon(pts, fill=PINE2)
    for dx, dy in ((-0.11, -0.05), (0.11, -0.05), (0, 0.09)):
        r = s * 0.12
        d.ellipse([cx + dx * s - r, cy + dy * s - r, cx + dx * s + r, cy + dy * s + r], fill=BERRY)


def wrap(d, txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


# --------------------------------------------------------------------------- image types
def hero(cfg, pg):
    im = snow_bg(seed=cfg["seed"])
    d = ImageDraw.Draw(im)
    # left panel
    lx = 120
    d.rounded_rectangle([lx, 150, 1380, H - 150], radius=46, fill=CREAM)
    d.rounded_rectangle([lx + 22, 172, 1358, H - 172], radius=34, outline=GOLD, width=4)
    holly(d, (lx + 1380) / 2, 330, 80)
    spaced(d, ((lx + 1380) / 2, 450), cfg["kicker"], F("Montserrat-SemiBold", 40), GOLD, 12)
    big = cfg["big"]
    bf = F("Playfair-Black", 300 if len(big) <= 3 else 220)
    text_c(d, ((lx + 1380) / 2, 640), big, bf, BERRY)
    y = 900
    for line in cfg["headline"]:
        hf = F("Playfair-Black", 116)
        while d.textlength(line, font=hf) > 1100:
            hf = F("Playfair-Black", hf.size - 4)
        text_c(d, ((lx + 1380) / 2, y), line, hf, PINE)
        y += 132
    y += 30
    for line in wrap(d, cfg["sub"], F("Playfair-Italic", 66), 1060):
        text_c(d, ((lx + 1380) / 2, y), line, F("Playfair-Italic", 66), BERRY)
        y += 82
    yb = max(y + 90, H - 520)
    for i, b in enumerate(cfg["badges"]):
        pill(d, (lx + 1380) / 2, yb + i * 112, b, F("Montserrat-Bold", 40), PINE if i == 0 else CREAM2, CREAM if i == 0 else PINE, h=88)
    # fanned pages
    pp = cfg["hero_pages"]
    spots = [(1890, 1190, 7, 880), (2580, 1190, -7, 880), (2235, 1125, 0, 1020)]
    for (cx, cy, ang, w), p in zip(spots, pp):
        place(im, paper(pg[p], w), cx, cy, ang)
    return im


def inside(cfg, pg):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    holly(d, W / 2, 130, 60)
    text_c(d, (W / 2, 250), "What's inside", F("Playfair-Black", 120), PINE)
    spaced(d, (W / 2, 345), cfg["inside_kicker"], F("Montserrat-SemiBold", 38), BERRY, 10)
    items = cfg["inside"]
    cols = 6 if len(items) > 10 else 5
    rows = math.ceil(len(items) / cols)
    tw = 380
    gapx = (W - 160 - cols * tw) / (cols - 1)
    th = int(tw * 1.294)
    top = 440
    rowh = (H - top - 60) / rows
    scale = min(1, (rowh - 90) / th)
    tw2, th2 = int(tw * scale), int(th * scale)
    for i, (p, label) in enumerate(items):
        r, c = divmod(i, cols)
        n_in_row = min(cols, len(items) - r * cols)
        rowx = (W - (n_in_row * tw + (n_in_row - 1) * gapx)) / 2
        cx = rowx + c * (tw + gapx) + tw / 2
        cy = top + r * rowh + th2 / 2 + 10
        place(im, paper(pg[p], tw2), cx, cy, 0, 16)
        d.text((cx, cy + th2 / 2 + 46), label, font=F("Montserrat-SemiBold", 34), fill=INK, anchor="mm")
    return im


def closeup(cfg, pg, pa, pb, caption, sub):
    im = snow_bg(CREAM2, (232, 222, 200), seed=len(caption), n=50)
    d = ImageDraw.Draw(im)
    text_c(d, (W / 2, 170), caption, F("Playfair-Black", 104), PINE)
    text_c(d, (W / 2, 290), sub, F("Montserrat-Medium", 50), BERRY)
    pw = 1080
    place(im, paper(pg[pa], pw), W / 2 - 600, 1300, 2.5)
    place(im, paper(pg[pb], pw), W / 2 + 600, 1300, -2.5)
    return im


def how_it_works(cfg):
    im = Image.new("RGB", (W, H), PINE)
    d = ImageDraw.Draw(im)
    text_c(d, (W / 2, 260), "How it works", F("Playfair-Black", 130), CREAM)
    spaced(d, (W / 2, 380), "instant digital download", F("Montserrat-SemiBold", 40), GOLD, 12)
    steps = [("1", "Purchase", "Add to cart and check out."),
             ("2", "Download", "Files appear instantly on your Etsy Purchases page and in your email."),
             ("3", "Print", "Print at home or at a local print shop on Letter or A4 paper."),
             ("4", cfg["step4"][0], cfg["step4"][1])]
    cw = (W - 240) / 4
    for i, (n, t, s) in enumerate(steps):
        cx = 120 + cw * i + cw / 2
        d.rounded_rectangle([cx - cw / 2 + 30, 560, cx + cw / 2 - 30, 1720], radius=40, fill=CREAM)
        d.ellipse([cx - 110, 640, cx + 110, 860], fill=BERRY)
        text_c(d, (cx, 750), n, F("Playfair-Black", 130), CREAM)
        text_c(d, (cx, 980), t, F("Playfair-Black", 86), PINE)
        y = 1100
        for line in wrap(d, s, F("Montserrat-Regular", 46), cw - 150):
            text_c(d, (cx, y), line, F("Montserrat-Regular", 46), INK)
            y += 66
    text_c(d, (W / 2, 1900), "No physical item will be shipped.", F("Montserrat-Medium", 52), CREAM2)
    text_c(d, (W / 2, 1990), "Print as many copies as you need for your own events.", F("Montserrat-Regular", 46), (180, 200, 186))
    return im


def details(cfg, pg):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    place(im, paper(pg[1], 1150), 760, H / 2 + 20, -3)
    x = 1500
    holly(d, x + 60, 300, 50)
    d.text((x, 430), "The details", font=F("Playfair-Black", 120), fill=PINE, anchor="lm")
    y = 600
    for b in cfg["details"]:
        d.ellipse([x, y - 14, x + 28, y + 14], fill=BERRY)
        lines = wrap(d, b, F("Montserrat-Medium", 54), W - x - 200)
        for j, line in enumerate(lines):
            d.text((x + 60, y + j * 72), line, font=F("Montserrat-Medium", 54), fill=INK, anchor="lm")
        y += 72 * len(lines) + 52
    return im


def cross_sell(key):
    im = snow_bg(seed=99)
    d = ImageDraw.Draw(im)
    text_c(d, (W / 2, 230), "Complete your holiday", F("Playfair-Black", 130), CREAM)
    spaced(d, (W / 2, 350), "more from the collection", F("Montserrat-SemiBold", 40), GOLD, 12)
    others = [k for k in P if k != key][:5]
    n = len(others)
    pw = 470
    gap = (W - 200 - n * pw) / (n - 1)
    for i, k in enumerate(others):
        cover = pages(k)[1]
        cx = 100 + pw / 2 + i * (pw + gap)
        place(im, paper(cover, pw), cx, 1200, 0, 24)
        text_c(d, (cx, 1700), P[k]["name"].replace("The ", ""), F("Playfair-Bold", 50), CREAM)
    text_c(d, (W / 2, 1980), "Visit our shop for the full holiday collection", F("Montserrat-Medium", 56), CREAM2)
    return im


# --------------------------------------------------------------------------- per-product config
def configs():
    t = {k: toc(k) for k in P}
    tp, to, tk, tb, tl = t["party"], t["office"], t["kids"], t["bingo"], t["leftright"]
    return {
        "party": dict(seed=1, kicker="christmas party games", big="21", headline=["Christmas", "Party Games"],
                      sub="Printable bundle for family, friends & office",
                      badges=["INSTANT DOWNLOAD", "US LETTER + A4", "ANSWER KEYS INCLUDED"],
                      hero_pages=[tp["Who's Most Likely To"], tp["Christmas Bingo"] + 1, 1],
                      inside_kicker="21 games + scoreboard + certificates",
                      inside=[(tp["Christmas Bingo"] + 1, "Bingo (20 cards)"), (tp["Who's Most Likely To"], "Most Likely To"),
                              (tp["This or That"], "This or That"), (tp["Would You Rather"], "Would You Rather"),
                              (tp["Christmas Trivia + answers"], "Trivia"), (tp["Emoji Christmas Quiz + answers"], "Emoji Quiz"),
                              (tp["Christmas Song Scramble + answers"], "Song Scramble"), (tp["Christmas Word Scramble + answers"], "Word Scramble"),
                              (tp["Christmas Word Search + answers"], "Word Search"), (tp["Find the Guest"], "Find the Guest"),
                              (tp["What's On Your Phone?"], "Phone Hunt"), (tp["Christmas Scavenger Hunt"], "Scavenger Hunt"),
                              (tp["Never Have I Ever"], "Never Have I Ever"), (tp["Truth or Dare"] + 1, "Truth or Dare"),
                              (tp["Christmas Charades"], "Charades"), (tp["Christmas Pictionary"], "Pictionary"),
                              (tp["Name 5 in 10 Seconds"], "Name 5 in 10"), (tp["Roll-the-Dice Gift Exchange"], "Dice Gift Swap")],
                      closeups=[(tp["Christmas Bingo"] + 1, tp["Who's Most Likely To"], "Something for everyone", "Bingo cards and Who's Most Likely To"),
                                (tp["Christmas Trivia + answers"], tp["Emoji Christmas Quiz + answers"], "Quizzes with answer keys", "Trivia, Emoji Quiz, Scrambles and Word Search"),
                                (tp["Christmas Charades"], tp["Roll-the-Dice Gift Exchange"], "Get everyone moving", "Charades, Pictionary and two gift exchange games")],
                      step4=("Play!", "Gather everyone and let the merry mayhem begin."),
                      details=["21 games + scoreboard + winner certificates", "59 pages, US Letter & A4 versions",
                               "Separate How-to-Play host guide", "Answer keys for every quiz",
                               "Family-friendly: ages 10 to 100", "Instant download, print at home"]),
        "bingo": dict(seed=2, kicker="printable bingo game", big="60", headline=["Christmas", "Bingo Cards"],
                      sub="Word + picture editions for kids & adults",
                      badges=["INSTANT DOWNLOAD", "US LETTER + A4", "CALLING CARDS INCLUDED"],
                      hero_pages=[tb["Word Edition: 30 cards + calling cards"] + 1, tb["Picture Edition: 30 cards + calling cards"] + 1, 1],
                      inside_kicker="two complete editions",
                      inside=[(tb["Word Edition: 30 cards + calling cards"], "Word Edition"), (tb["Word Edition: 30 cards + calling cards"] + 1, "Word cards"),
                              (tb["Picture Edition: 30 cards + calling cards"] - 1, "Word calling cards"),
                              (tb["Picture Edition: 30 cards + calling cards"], "Picture Edition"), (tb["Picture Edition: 30 cards + calling cards"] + 1, "Picture cards"),
                              (tb["Bonus: Bingo Champion certificates"] - 1, "Picture calling cards"), (tb["Bonus: Bingo Champion certificates"], "Winner certificates"),
                              (2, "Contents")],
                      closeups=[(tb["Word Edition: 30 cards + calling cards"] + 2, tb["Picture Edition: 30 cards + calling cards"] + 2, "Two editions, 60 cards", "Every card is unique"),
                                (tb["Picture Edition: 30 cards + calling cards"] - 1, tb["Bonus: Bingo Champion certificates"] - 1, "Calling cards included", "Cut, shuffle and draw")],
                      step4=("Shout BINGO!", "Use candy as markers for extra fun."),
                      details=["30 word bingo cards + 30 picture bingo cards", "Every card is unique", "Calling cards for both editions",
                               "Picture edition is great for non-readers", "Bonus winner certificates", "US Letter & A4, instant download"]),
        "leftright": dict(seed=3, kicker="gift exchange game", big="3+1", headline=["Left Right", "Gift Exchange"],
                          sub="Original stories for family, office & kids",
                          badges=["INSTANT DOWNLOAD", "US LETTER + A4", "BONUS DICE GAME"],
                          hero_pages=[tl["Story 2: The Office Party"], tl["Story 1: Family Christmas Eve"], 1],
                          inside_kicker="3 stories + bonus game",
                          inside=[(tl["Story 1: Family Christmas Eve"], "Family story"), (tl["Story 2: The Office Party"], "Office story"),
                                  (tl["Story 3: Ellie the Elf (short, for kids)"], "Kids story"), (tl["Bonus: Roll-the-Dice Gift Exchange"], "Dice gift swap"),
                                  (2, "Contents")],
                          closeups=[(tl["Story 1: Family Christmas Eve"], tl["Story 3: Ellie the Elf (short, for kids)"], "Pass it left, pass it right", "LEFT and RIGHT are highlighted for easy reading"),
                                    (tl["Story 2: The Office Party"], tl["Bonus: Roll-the-Dice Gift Exchange"], "Perfect for any party", "Office story + bonus dice game")],
                          step4=("Pass the gifts!", "Read the story out loud and pass on every LEFT and RIGHT."),
                          details=["3 original Left Right stories", "Family, office and kids versions", "LEFT / RIGHT highlighted in color",
                                   "Bonus: Roll-the-Dice Gift Exchange", "Takes only 5-10 minutes", "US Letter & A4, instant download"]),
        "office": dict(seed=4, kicker="office party games", big="13", headline=["Office Christmas", "Party Games"],
                       sub="Icebreakers, quizzes & a gift swap for teams",
                       badges=["INSTANT DOWNLOAD", "WORK-FRIENDLY", "PRINT OR SHARE ON ZOOM"],
                       hero_pages=[to["Find the Coworker"], to["Who's Most Likely To (office)"], 1],
                       inside_kicker="13 games + awards",
                       inside=[(to[k], lab) for k, lab in [("Who's Most Likely To (office)", "Most Likely To"), ("Find the Coworker", "Find the Coworker"),
                               ("This or That (office)", "This or That"), ("Christmas Trivia + answers", "Trivia"), ("Emoji Christmas Quiz + answers", "Emoji Quiz"),
                               ("Christmas Song Scramble + answers", "Song Scramble"), ("Two Truths & a Lie", "Two Truths & a Lie"), ("Desk Scavenger Hunt", "Desk Hunt"),
                               ("Name 5 in 10 Seconds", "Name 5 in 10"), ("Christmas Charades", "Charades"), ("Christmas Bingo (20 cards)", "Bingo"),
                               ("Roll-the-Dice Gift Exchange", "Dice Gift Swap")]],
                       closeups=[(to["Find the Coworker"], to["Who's Most Likely To (office)"], "Break the ice", "Find the Coworker + Most Likely To (office edition)"),
                                 (to["Christmas Trivia + answers"], to["Desk Scavenger Hunt"], "Team challenges", "Trivia with answers and the Desk Scavenger Hunt"),
                                 (to["Bonus: Office Awards"], to["Roll-the-Dice Gift Exchange"], "End on a high note", "Office awards and the gift exchange")],
                       step4=("Play as a team", "In the office or on a video call."),
                       details=["13 workplace-friendly games", "Icebreakers, quizzes, gift exchange", "Scoreboard + 4 office award certificates",
                                "Separate host guide with a 1-hour party plan", "Works in person or on video calls", "US Letter & A4, instant download"]),
        "kids": dict(seed=5, kicker="kids christmas activities", big="21", headline=["Christmas", "Activity Pages"],
                     sub="Coloring, mazes & puzzles for ages 4-9",
                     badges=["INSTANT DOWNLOAD", "US LETTER + A4", "ANSWER KEYS INCLUDED"],
                     hero_pages=[tk["8 Coloring Pages"] + 1, tk["3 Mazes"] + 1, 1],
                     inside_kicker="21 activities + answer keys",
                     inside=[(tk["8 Coloring Pages"], "Coloring"), (tk["8 Coloring Pages"] + 3, "Coloring"), (tk["8 Coloring Pages"] + 5, "Coloring"),
                             (tk["3 Mazes"], "Easy maze"), (tk["3 Mazes"] + 2, "Tricky maze"), (tk["2 Connect the Dots"], "Dot to dot"),
                             (tk["Word Search"], "Word search"), (tk["I Spy & Count"], "I Spy & count"), (tk["Picture Sudoku"], "Picture sudoku"),
                             (tk["Trace the Words"], "Tracing"), (tk["Letter to Santa"], "Letter to Santa"), (tk["2 Drawing Pages"], "Drawing")],
                     closeups=[(tk["8 Coloring Pages"] + 1, tk["8 Coloring Pages"] + 4, "8 coloring pages", "Big, simple designs for little hands"),
                               (tk["3 Mazes"], tk["I Spy & Count"], "Puzzles & games", "Mazes, I Spy, word search and picture sudoku"),
                               (tk["Letter to Santa"], tk["Picture Sudoku"], "Make it personal", "Letter to Santa and drawing pages")],
                     step4=("Get creative!", "Crayons, markers and a cozy afternoon."),
                     details=["21 activities for ages 4-9", "8 coloring pages, 3 mazes, 2 dot-to-dots", "Word search, I Spy, picture sudoku, tracing",
                              "Letter to Santa + drawing pages", "Answer keys for grown-ups", "US Letter & A4, instant download"]),
        "tags": dict(seed=6, kicker="printable gift tags", big="68", headline=["Christmas", "Gift Tags"],
                     sub="Editable To/From fields + print & write version",
                     badges=["INSTANT DOWNLOAD", "EDITABLE PDF", "US LETTER + A4"],
                     hero_pages=[5, 4, 1],
                     inside_kicker="8 designs · 68 tags",
                     inside=[(3, "Pine & Berry"), (4, "Candy Stripe"), (5, "Midnight Snow"), (6, "Kraft Tree"),
                             (7, "Holiday Plaid"), (8, "Ornament Glow"), (9, "Round tags"), (10, "From Santa")],
                     closeups=[(4, 7, "Classic & cozy", "Candy Stripe and Holiday Plaid"), (9, 10, "Round & Santa tags", "Including 'Do Not Open Until Dec 25'")],
                     step4=("Tie it on!", "Type the names first, or write them by hand."),
                     details=["68 tags in 8 designs", "Editable PDF: type To/From names before printing", "Print-and-write version included",
                              "Round tags + From Santa tags", "Works with free Adobe Acrobat Reader", "US Letter & A4, instant download"]),
    }


def build(key):
    cfg = configs()[key]
    pg = pages(key)
    out = os.path.join(ROOT, P[key]["dir"], "listing_images")
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "*")):
        os.remove(f)
    imgs = [("01_main", hero(cfg, pg)), ("02_whats-inside", inside(cfg, pg))]
    for i, (a, b, cap, sub) in enumerate(cfg["closeups"]):
        imgs.append((f"{3 + i:02d}_preview", closeup(cfg, pg, a, b, cap, sub)))
    n = len(imgs) + 1
    imgs.append((f"{n:02d}_how-it-works", how_it_works(cfg)))
    imgs.append((f"{n + 1:02d}_details", details(cfg, pg)))
    imgs.append((f"{n + 2:02d}_more-from-shop", cross_sell(key)))
    paths = []
    for name, im in imgs:
        p = os.path.join(out, f"{name}.jpg")
        im.convert("RGB").save(p, "JPEG", quality=88, optimize=True, progressive=True)
        paths.append(p)
    # 10s preview video (Etsy: 5-15 s, no sound), 1920x1440
    vid = os.path.join(ROOT, P[key]["dir"], "listing_video.mp4")
    seq = paths[:-1]
    per = 10 / len(seq)
    lst = os.path.join(CACHE, f"vid_{key}.txt")
    with open(lst, "w") as f:
        for p in seq:
            f.write(f"file '{p}'\nduration {per:.3f}\n")
        f.write(f"file '{seq[-1]}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", "scale=1920:1440,fps=30,format=yuv420p", "-an", "-c:v", "libx264", "-crf", "22", "-preset", "medium",
                    "-movflags", "+faststart", vid], check=True)
    print(key, len(paths), "images + video")


if __name__ == "__main__":
    for k in sys.argv[1:] or list(P):
        build(k)
