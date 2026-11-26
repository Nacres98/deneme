"""Build all six NexaGlobe Christmas products (US Letter + A4)."""
import io
import os
import sys

from reportlab.pdfgen import canvas

from lib import *  # noqa
import games as G

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

P = {
    "party": dict(dir="01_Merry-Mayhem-Party-Pack", name="Merry Mayhem Party Pack", file="Merry-Mayhem_Christmas-Party-Pack"),
    "bingo": dict(dir="02_Jingle-Grid-Bingo", name="Jingle Grid Bingo", file="Jingle-Grid_Christmas-Bingo"),
    "leftright": dict(dir="03_Left-Right-Sleigh-Ride", name="The Left-Right Sleigh Ride", file="Left-Right-Sleigh-Ride_Gift-Exchange-Stories"),
    "office": dict(dir="04_Mistletoe-and-Meetings", name="Mistletoe & Meetings", file="Mistletoe-and-Meetings_Office-Party-Games"),
    "kids": dict(dir="05_Little-Elf-Workshop", name="Little Elf Workshop", file="Little-Elf-Workshop_Kids-Christmas-Activities"),
    "tags": dict(dir="06_Ribbon-and-Pine-Gift-Tags", name="Ribbon & Pine Gift Tags", file="Ribbon-and-Pine_Christmas-Gift-Tags"),
}

CROSS = {
    "party": ["Jingle Grid Bingo · 60 cards", "Mistletoe & Meetings · office games", "Little Elf Workshop · kids activities"],
    "bingo": ["Merry Mayhem Party Pack · 21 games", "The Left-Right Sleigh Ride · gift swap stories", "Ribbon & Pine Gift Tags"],
    "leftright": ["Merry Mayhem Party Pack · 21 games", "Jingle Grid Bingo · 60 cards", "Ribbon & Pine Gift Tags"],
    "office": ["Merry Mayhem Party Pack · 21 games", "Jingle Grid Bingo · 60 cards", "The Left-Right Sleigh Ride"],
    "kids": ["Jingle Grid Bingo · picture edition inside", "Merry Mayhem Party Pack · 21 games", "Ribbon & Pine Gift Tags"],
    "tags": ["Merry Mayhem Party Pack · 21 games", "Little Elf Workshop · kids activities", "Jingle Grid Bingo · 60 cards"],
}


def out_dir(key):
    d = os.path.join(ROOT, P[key]["dir"], "upload_files")
    os.makedirs(d, exist_ok=True)
    return d


def two_pass(path, W, H, key, body):
    """body(ctx, toc) draws everything; toc collects (name, page). First pass only measures."""
    toc = []
    c = canvas.Canvas(io.BytesIO(), pagesize=(W, H))
    body(G.Ctx(c, W, H, P[key]["name"]), toc, None)
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle(P[key]["name"])
    c.setAuthor(BRAND)
    c.setSubject("Printable Christmas digital download")
    body(G.Ctx(c, W, H, P[key]["name"]), [], toc)
    c.save()
    import json
    if W == letter[0]:
        json.dump(toc, open(os.path.join(CACHE, f"toc_{key}.json"), "w"))


# --------------------------------------------------------------------------- 1. party pack
PARTY_GAMES = [
    ("Christmas Bingo", lambda x: G.g_bingo(x, 20, seed=11)),
    ("Who's Most Likely To", G.g_most_likely),
    ("This or That", G.g_this_or_that),
    ("Would You Rather", G.g_wyr),
    ("Christmas Trivia + answers", G.g_trivia),
    ("Emoji Christmas Quiz + answers", G.g_emoji),
    ("Christmas Song Scramble + answers", G.g_song_scramble),
    ("Christmas Word Scramble + answers", G.g_word_scramble),
    ("Christmas Word Search + answers", G.g_word_search),
    ("Find the Guest", G.g_find_guest),
    ("What's On Your Phone?", G.g_phone_hunt),
    ("Christmas Scavenger Hunt", G.g_scavenger),
    ("Never Have I Ever", G.g_nhie),
    ("Truth or Dare", G.g_truth_dare),
    ("Christmas Charades", G.g_charades),
    ("Christmas Pictionary", G.g_pictionary),
    ("Name 5 in 10 Seconds", G.g_name5),
    ("Roll-the-Dice Gift Exchange", G.g_dice_gift),
    ("Left Right Gift Exchange Story", G.g_left_right),
    ("Christmas Story Fill-In", G.g_madlib),
    ("How Many Words?", G.g_how_many),
    ("Bonus: Party Scoreboard", G.g_scoreboard),
    ("Bonus: Winner Certificates", G.g_certificates),
]
PARTY_KEYS = ["bingo", "most_likely", "this_or_that", "wyr", "trivia", "emoji", "song_scramble", "word_scramble",
              "word_search", "find_guest", "phone_hunt", "scavenger", "nhie", "truth_dare", "charades", "pictionary",
              "name5", "dice_gift", "left_right", "madlib", "how_many"]


def build_party(W, H, path):
    def body(ctx, toc, toc_final):
        c = ctx.c
        cover_page(c, W, H, ["Merry Mayhem", "Party Pack"],
                   "21 printable Christmas party games for family nights, friends and office parties. Print, cut and play.",
                   ("21", "party games"), "the holiday games collection",
                   ["Bingo", "Trivia", "Most Likely To", "Charades", "Gift Exchange", "+ answer keys"])
        ctx.end(footer_on=False)
        G.contents_page(ctx, "Merry Mayhem Party Pack", toc_final or [(n, 0) for n, _ in PARTY_GAMES],
                        "Every game includes its own 'how to play' box. Answer keys follow each quiz. A separate How-to-Play guide is included in your download.")
        for name, fn in PARTY_GAMES:
            toc.append((name, ctx.page))
            fn(ctx)
        terms_page(c, W, H, "Merry Mayhem Party Pack", CROSS["party"])
        ctx.end(footer_on=False)
    two_pass(path, W, H, "party", body)


def guide_party(W, H, path):
    G.host_guide(path, W, H, P["party"]["name"], PARTY_KEYS, "merry mayhem party pack",
                 "Here is everything you need to host a fun, stress-free Christmas game night. Pick 4-6 games for a 2-hour party. Mix quiet games (quizzes) with loud ones (charades) to keep the energy up.",
                 ["Print the quiz sheets on regular paper and the cards on cardstock.",
                  "Prep the night before: cut the cards and put each game in its own envelope.",
                  "Small prizes make everything more fun: candy canes, chocolates, socks or a $5 gift card.",
                  "Use the scoreboard to crown an overall champion with the certificate at the end!",
                  "Playing on a video call? Share your screen with the quiz pages and let everyone answer in the chat."])


BUILDERS = {"party": (build_party, guide_party)}

# --------------------------------------------------------------------------- 2. bingo
def build_bingo(W, H, path):
    def body(ctx, toc, toc_final):
        c = ctx.c
        cover_page(c, W, H, ["Jingle Grid", "Christmas Bingo"],
                   "60 unique bingo cards in two editions: a word edition for teens and adults and a picture edition for kids. Calling cards included.",
                   ("60", "bingo cards"), "the holiday games collection",
                   ["30 word cards", "30 picture cards", "calling cards", "game variations"])
        ctx.end(footer_on=False)
        G.contents_page(ctx, "Jingle Grid Bingo", toc_final or [("x", 0)] * 3,
                        "Print one card per player. Cards are unique, so there are no ties on the same card!")
        toc.append(("Word Edition: 30 cards + calling cards", ctx.page))
        G.g_bingo(ctx, 30, pictures=False, seed=31)
        toc.append(("Picture Edition: 30 cards + calling cards", ctx.page))
        G.g_bingo(ctx, 30, pictures=True, seed=31)
        toc.append(("Bonus: Bingo Champion certificates", ctx.page))
        G.g_certificates(ctx, ["Bingo Champion", "Bingo Legend"])
        terms_page(c, W, H, "Jingle Grid Bingo", CROSS["bingo"])
        ctx.end(footer_on=False)
    two_pass(path, W, H, "bingo", body)


def guide_bingo(W, H, path):
    G.host_guide(path, W, H, P["bingo"]["name"], ["bingo"], "jingle grid bingo",
                 "Bingo is the easiest party game there is: everyone can play, from 4 to 94. Here is how to run it like a pro.",
                 ["Use candy, mini marshmallows or chocolate chips as markers. Players get to eat them at the end!",
                  "Slip cards into sheet protectors and use dry-erase markers to reuse them all season.",
                  "Picture Edition is perfect for kids who can't read yet. Word Edition suits teens and adults.",
                  "Game ideas: Line, Four Corners, Letter X, Picture Frame (outer edge) and Blackout (whole card).",
                  "Keep the drawn calling cards in a separate pile so you can check a winner's card."])


# --------------------------------------------------------------------------- 3. left-right
def build_leftright(W, H, path):
    def body(ctx, toc, toc_final):
        c = ctx.c
        cover_page(c, W, H, ["The Left-Right", "Sleigh Ride"],
                   "Three original pass-the-gift stories for families, offices and kids, plus a bonus roll-the-dice gift swap.",
                   ("3+1", "gift games"), "the holiday games collection",
                   ["family story", "office story", "kids story", "dice game bonus"])
        ctx.end(footer_on=False)
        G.contents_page(ctx, "The Left-Right Sleigh Ride", toc_final or [("x", 0)] * 4,
                        "Everyone sits in a circle with a wrapped gift. Read the story out loud and pass the gifts LEFT or RIGHT every time you hear the word.")
        toc.append(("Story 1: Family Christmas Eve", ctx.page))
        G.g_left_right(ctx, "family")
        toc.append(("Story 2: The Office Party", ctx.page))
        G.g_left_right(ctx, "office")
        toc.append(("Story 3: Ellie the Elf (short, for kids)", ctx.page))
        G.g_left_right(ctx, "kids")
        toc.append(("Bonus: Roll-the-Dice Gift Exchange", ctx.page))
        G.g_dice_gift(ctx)
        terms_page(c, W, H, "The Left-Right Sleigh Ride", CROSS["leftright"])
        ctx.end(footer_on=False)
    two_pass(path, W, H, "leftright", body)


def guide_leftright(W, H, path):
    G.host_guide(path, W, H, P["leftright"]["name"], ["left_right", "dice_gift"], "the left-right sleigh ride",
                 "These games turn a simple gift swap into the loudest five minutes of the party.",
                 ["Set a gift budget in advance (e.g. $10 or $20) so everything feels fair.",
                  "Read slowly and pause after each LEFT and RIGHT. Speed up at the end for extra chaos!",
                  "Pick the story that suits your crowd: family, office or kids.",
                  "Remote party? Everyone keeps their own gift and 'passes' a name card instead. Swap the real gifts afterwards."])


# --------------------------------------------------------------------------- 4. office
OFFICE_GAMES = [
    ("Who's Most Likely To (office)", lambda x: G.g_most_likely(x, office=True)),
    ("Find the Coworker", G.g_find_coworker),
    ("This or That (office)", lambda x: G.g_this_or_that(x, office=True)),
    ("Christmas Trivia + answers", lambda x: G.g_trivia(x, office=True)),
    ("Emoji Christmas Quiz + answers", G.g_emoji),
    ("Christmas Song Scramble + answers", G.g_song_scramble),
    ("Two Truths & a Lie", G.g_two_truths),
    ("Desk Scavenger Hunt", G.g_desk_hunt),
    ("Name 5 in 10 Seconds", G.g_name5),
    ("Christmas Charades", G.g_charades),
    ("Christmas Bingo (20 cards)", lambda x: G.g_bingo(x, 20, seed=77, title_kicker="office edition")),
    ("Roll-the-Dice Gift Exchange", lambda x: G.g_dice_gift(x, office=True)),
    ("Left Right Office Story", lambda x: G.g_left_right(x, "office")),
    ("Bonus: Scoreboard", G.g_scoreboard),
    ("Bonus: Office Awards", lambda x: G.g_certificates(x, ["Office Party MVP", "Best Holiday Spirit", "Secret Santa Superstar", "Trivia Champion"])),
]
OFFICE_KEYS = ["most_likely", "find_coworker", "this_or_that", "trivia", "emoji", "song_scramble", "two_truths",
               "desk_hunt", "name5", "charades", "bingo", "dice_gift", "left_right"]


def build_office(W, H, path):
    def body(ctx, toc, toc_final):
        c = ctx.c
        cover_page(c, W, H, ["Mistletoe", "& Meetings"],
                   "13 office Christmas party games: icebreakers, quizzes and a gift swap. Work-friendly, inclusive and ready to print or share on a video call.",
                   ("13", "office games"), "the holiday games collection",
                   ["icebreakers", "trivia", "bingo", "gift exchange", "awards"], accent=PINE2)
        ctx.end(footer_on=False)
        G.contents_page(ctx, "Mistletoe & Meetings", toc_final or [(n, 0) for n, _ in OFFICE_GAMES],
                        "Every game is workplace-friendly. Each page has its own 'how to play' box, and a separate host guide is included.")
        for name, fn in OFFICE_GAMES:
            toc.append((name, ctx.page))
            fn(ctx)
        terms_page(c, W, H, "Mistletoe & Meetings", CROSS["office"])
        ctx.end(footer_on=False)
    two_pass(path, W, H, "office", body)


def guide_office(W, H, path):
    G.host_guide(path, W, H, P["office"]["name"], OFFICE_KEYS, "mistletoe & meetings",
                 "A one-hour office party plan: start with an icebreaker (Find the Coworker), play two quizzes in teams, then finish with the gift exchange and awards.",
                 ["Virtual team? Share the quiz pages on screen and have people answer in the chat.",
                  "Make teams that mix departments. It's the easiest way to get people talking.",
                  "Keep prizes small and fun: gift cards, snacks, an extra-long lunch break.",
                  "Hand out the award certificates at the end. People love taking them back to their desks!"])


# --------------------------------------------------------------------------- 5. kids
def build_kids(W, H, path):
    import kids as KD

    def body(ctx, toc, toc_final):
        c = ctx.c
        cover_page(c, W, H, ["Little Elf", "Workshop"],
                   "21 Christmas activities for kids ages 4-9: coloring, mazes, dot-to-dot, puzzles, a letter to Santa and more.",
                   ("21", "activities"), "kids christmas activities",
                   ["coloring", "mazes", "dot to dot", "word search", "picture sudoku", "letter to Santa"])
        ctx.end(footer_on=False)
        KD.parent_page(ctx, toc_final or [("x", 0)] * 11)
        toc.append(("8 Coloring Pages", ctx.page))
        KD.coloring_pages(ctx)
        toc.append(("3 Mazes", ctx.page))
        KD.maze_pages(ctx)
        toc.append(("2 Connect the Dots", ctx.page))
        KD.dot_pages(ctx)
        toc.append(("Word Search", ctx.page))
        grid, placed = KD.kids_word_search(ctx)
        toc.append(("I Spy & Count", ctx.page))
        counts = KD.count_page(ctx)
        toc.append(("Picture Sudoku", ctx.page))
        puzzles, base = KD.sudoku_pages(ctx)
        toc.append(("Trace the Words", ctx.page))
        KD.tracing_page(ctx)
        toc.append(("Trees vs. Stars Tic-Tac-Toe", ctx.page))
        KD.tictactoe_page(ctx)
        toc.append(("Letter to Santa", ctx.page))
        KD.letter_to_santa(ctx)
        toc.append(("2 Drawing Pages", ctx.page))
        KD.drawing_pages(ctx)
        toc.append(("Answer Keys", ctx.page))
        KD.answers_page(ctx, grid, placed, counts, puzzles, base)
        terms_page(c, W, H, "Little Elf Workshop", CROSS["kids"])
        ctx.end(footer_on=False)
    two_pass(path, W, H, "kids", body)


BUILDERS.update({"bingo": (build_bingo, guide_bingo), "leftright": (build_leftright, guide_leftright),
                 "office": (build_office, guide_office), "kids": (build_kids, None)})


def run(keys):
    if "tags" in keys:
        import tags as T
        d = out_dir("tags")
        for sz, (W, H) in SIZES.items():
            for ed, lab in ((True, "Editable"), (False, "Print-and-Write")):
                f = os.path.join(d, f"{P['tags']['file']}_{lab}_{sz}.pdf")
                print("built", f, "fields:", T.build_tags(W, H, f, ed))
        keys = [k for k in keys if k != "tags"]
    for key in keys:
        build, guide = BUILDERS[key]
        d = out_dir(key)
        for sz, (W, H) in SIZES.items():
            f = os.path.join(d, f"{P[key]['file']}_{sz}.pdf")
            build(W, H, f)
            if guide:
                guide(W, H, os.path.join(d, f"{P[key]['file'].split('_')[0]}_How-to-Play-Guide_{sz}.pdf"))
            print("built", f)


if __name__ == "__main__":
    run(sys.argv[1:] or list(BUILDERS) + ["tags"])
