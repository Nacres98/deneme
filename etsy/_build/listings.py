"""Write LISTING.md (copy-paste Etsy listing data) for each product, with Etsy limit checks."""
import os
from products import P, ROOT

COMMON_END = """
━━━━━━━━━━━━━━━━━━
⭐ HOW IT WORKS
1. Purchase this listing.
2. Download the files from your Etsy Purchases page (or the email link).
3. Print at home or at a local print shop at 100% / Actual size.
4. Cut, play and enjoy!

⭐ PLEASE NOTE
• This is a DIGITAL DOWNLOAD. No physical item will be shipped.
• Colors may vary slightly depending on your screen and printer.
• For personal use only. Please do not share, resell or redistribute the files.
• Because of the nature of digital files, refunds can't be offered, but if anything is wrong with your download, message us and we'll make it right.

Designed by NexaGlobe Studio. Created with the help of digital design tools, including AI.

🎄 More holiday printables in our shop: Christmas games, bingo, kids activities and gift tags.
"""

L = {
"party": dict(
 price="8.99", sale="5.39",
 title="Christmas Party Games Bundle, 21 Printable Games for Family, Adults & Office, Christmas Bingo, Trivia, Most Likely To, Instant Download",
 tags=["christmas games", "christmas party game", "printable games", "family game night", "holiday party games",
       "office party games", "christmas bingo", "christmas trivia", "most likely to", "games for adults",
       "christmas printable", "xmas games bundle", "christmas eve games"],
 category="Paper & Party Supplies › Party Supplies › Party Games",
 desc="""🎄 MERRY MAYHEM PARTY PACK: 21 Printable Christmas Party Games 🎄

Turn any Christmas gathering into the party everyone talks about! This printable bundle has 21 easy, family-friendly games for family nights, friends, classrooms and office parties. Just print, cut and play.

━━━━━━━━━━━━━━━━━━
⭐ WHAT'S INCLUDED (21 games + bonuses)
• Christmas Bingo (20 unique cards + calling cards)
• Who's Most Likely To (40 cards)
• This or That
• Would You Rather (30 cards)
• Christmas Trivia (30 questions + answer key)
• Emoji Christmas Quiz (+ answer key)
• Christmas Song Scramble (+ answer key)
• Christmas Word Scramble (+ answer key)
• Christmas Word Search (+ answer key)
• Find the Guest (icebreaker)
• What's On Your Phone?
• Christmas Scavenger Hunt
• Never Have I Ever (30 cards)
• Truth or Dare: family-friendly (48 cards)
• Christmas Charades (36 cards)
• Christmas Pictionary (36 cards)
• Name 5 in 10 Seconds (30 cards)
• Roll-the-Dice Gift Exchange
• Left Right Gift Exchange Story
• Christmas Story Fill-In
• How Many Words?
• BONUS: Party Scoreboard + Winner Certificates
• BONUS: separate How-to-Play host guide

⭐ FILES YOU GET
• Party Pack PDF in US Letter (8.5x11 in), 59 pages
• Party Pack PDF in A4, 59 pages
• How-to-Play Guide PDF in US Letter + A4

⭐ PERFECT FOR
Family Christmas parties • Christmas Eve • Friendsmas • Office & work parties • Classrooms • Holiday game nights • Virtual parties (share your screen!)
""",
 files="4 dosya: Party-Pack US-Letter + A4, How-to-Play-Guide US-Letter + A4"),
"bingo": dict(
 price="4.99", sale="2.99",
 title="Christmas Bingo Cards Printable, 60 Unique Cards, Picture Bingo for Kids & Word Bingo for Adults, Holiday Party Game, Classroom Game",
 tags=["christmas bingo", "bingo printable", "picture bingo", "kids christmas game", "holiday bingo",
       "christmas party game", "classroom party", "bingo cards", "family bingo game", "xmas bingo",
       "christmas printable", "school party game", "christmas activity"],
 category="Paper & Party Supplies › Party Supplies › Party Games",
 desc="""🎄 JINGLE GRID: Christmas Bingo, 60 Unique Printable Cards 🎄

The easiest Christmas party game for all ages! You get TWO complete bingo games: a Word Edition for teens and adults, and a colorful Picture Edition that kids who can't read yet can play too.

━━━━━━━━━━━━━━━━━━
⭐ WHAT'S INCLUDED
• 30 unique WORD bingo cards
• 30 unique PICTURE bingo cards
• Calling cards for both editions
• "Bingo Champion" winner certificates
• How-to-Play guide with 5 game variations (line, four corners, X, frame, blackout)

⭐ FILES YOU GET
• Bingo PDF in US Letter + A4 (38 pages each)
• How-to-Play Guide in US Letter + A4

⭐ PERFECT FOR
Classroom Christmas parties • Family gatherings • Church & community events • Senior centers • Office parties

💡 Tip: slip cards into sheet protectors and use dry-erase markers to play again and again.
""",
 files="4 dosya: Bingo US-Letter + A4, How-to-Play-Guide US-Letter + A4"),
"leftright": dict(
 price="3.49", sale="2.09",
 title="Left Right Christmas Gift Exchange Game, 3 Printable Stories for Family, Office & Kids, Pass the Gift Game, White Elephant Alternative",
 tags=["left right game", "gift exchange game", "left right story", "pass the gift game", "christmas games",
       "white elephant game", "office party games", "christmas party game", "secret santa game", "family party game",
       "christmas printable", "gift swap game", "xmas party games"],
 category="Paper & Party Supplies › Party Supplies › Party Games",
 desc="""🎄 THE LEFT-RIGHT SLEIGH RIDE: Christmas Gift Exchange Stories 🎄

The funniest five minutes of any Christmas party! Everyone sits in a circle with a wrapped gift. Read the story out loud and pass the gifts LEFT or RIGHT every time you hear the word. When the story ends, the gift in your hands is yours!

━━━━━━━━━━━━━━━━━━
⭐ WHAT'S INCLUDED
• Story 1: Family Christmas Eve (all ages)
• Story 2: The Office Party (perfect for coworkers)
• Story 3: Ellie the Elf (short story for kids)
• BONUS: Roll-the-Dice Gift Exchange game
• LEFT and RIGHT are highlighted in color so the reader never misses one
• All stories are original

⭐ FILES YOU GET
• Stories PDF in US Letter + A4
• How-to-Play Guide in US Letter + A4

⭐ PERFECT FOR
Family Christmas • Office parties • Secret Santa & white elephant swaps • Classrooms • Friendsmas
""",
 files="4 dosya: Stories US-Letter + A4, How-to-Play-Guide US-Letter + A4"),
"office": dict(
 price="6.49", sale="3.89",
 title="Office Christmas Party Games, 13 Printable Work Party Games, Team Building Icebreakers, Virtual Holiday Party, Coworker Games Bundle",
 tags=["office party games", "work party games", "team building games", "christmas icebreaker", "virtual party games",
       "coworker games", "holiday party games", "staff party games", "zoom party games", "christmas games",
       "office christmas", "corporate party game", "christmas printable"],
 category="Paper & Party Supplies › Party Supplies › Party Games",
 desc="""🎄 MISTLETOE & MEETINGS: 13 Office Christmas Party Games 🎄

Make this year's work holiday party actually fun! 13 workplace-friendly games that get coworkers talking, laughing and working as a team. Print them for the office or share them on screen for a virtual party.

━━━━━━━━━━━━━━━━━━
⭐ WHAT'S INCLUDED
• Who's Most Likely To: Office Edition (30 cards)
• Find the Coworker (icebreaker bingo)
• This or That: Office Edition
• Christmas Trivia (+ answer key)
• Emoji Christmas Quiz (+ answer key)
• Christmas Song Scramble (+ answer key)
• Two Truths & a Lie
• Desk Scavenger Hunt
• Name 5 in 10 Seconds
• Christmas Charades
• Christmas Bingo (20 cards)
• Roll-the-Dice Gift Exchange
• Left Right Office Story
• BONUS: Scoreboard + 4 Office Award certificates
• BONUS: Host guide with a ready 1-hour party plan

⭐ FILES YOU GET
• Games PDF in US Letter + A4 (37 pages)
• How-to-Play Host Guide in US Letter + A4

⭐ PERFECT FOR
Office holiday parties • Team building • Virtual / Zoom parties • Staff lunches • HR & party planners
""",
 files="4 dosya: Office-Games US-Letter + A4, How-to-Play-Guide US-Letter + A4"),
"kids": dict(
 price="5.49", sale="3.29",
 title="Christmas Activity Pages for Kids, Printable Coloring Pages, Mazes, Word Search, Letter to Santa, Kids Christmas Activity Book Ages 4-9",
 tags=["kids christmas", "christmas coloring", "kids activity pages", "christmas worksheets", "coloring pages kids",
       "letter to santa", "christmas mazes", "kids printables", "christmas activities", "classroom activity",
       "busy book christmas", "holiday kids fun", "christmas break fun"],
 category="Paper & Party Supplies › Paper › Coloring Pages (ya da Etsy'nin önerdiği 'Kids activity' kategorisi)",
 desc="""🎄 LITTLE ELF WORKSHOP: 21 Christmas Activities for Kids 🎄

Keep little elves happy and busy all through Christmas break! 21 printable activity pages for kids ages 4-9. Perfect for home, classrooms, restaurants, road trips and the long wait until Christmas morning.

━━━━━━━━━━━━━━━━━━
⭐ WHAT'S INCLUDED
• 8 Christmas coloring pages (big, simple designs)
• 3 mazes (easy, medium, tricky)
• 2 connect-the-dots (star & tree)
• Christmas word search
• I Spy & Count
• Picture Sudoku (2 puzzles, no reading needed)
• Trace the Words (writing practice)
• Trees vs. Stars tic-tac-toe
• Letter to Santa
• 2 drawing pages
• Answer keys for grown-ups

⭐ FILES YOU GET
• Activity PDF in US Letter (8.5x11 in) + A4, 26 pages each

⭐ PERFECT FOR
Christmas break • Classroom parties • Kids' table at Christmas dinner • Restaurants & travel • Homeschool
""",
 files="2 dosya: Activities US-Letter + A4"),
"tags": dict(
 price="3.49", sale="2.09",
 title="Printable Christmas Gift Tags, Editable To From Tags PDF, 68 Holiday Gift Labels, Kraft, Plaid & From Santa Tags, Instant Download",
 tags=["christmas gift tags", "printable gift tags", "editable gift tags", "holiday gift tags", "from santa tags",
       "christmas tags", "gift labels", "christmas labels", "kraft gift tags", "plaid gift tags",
       "christmas printable", "to from tags", "xmas gift tags"],
 category="Paper & Party Supplies › Paper › Stationery › Gift Tags & Labels (Etsy'nin önerisine göre)",
 desc="""🎄 RIBBON & PINE: 68 Printable Christmas Gift Tags 🎄

Give every present a beautiful finishing touch! 68 gift tags in 8 designs. Type the names right into the PDF before printing, or print and write them by hand.

━━━━━━━━━━━━━━━━━━
⭐ WHAT'S INCLUDED
• Pine & Berry (8 tags)
• Candy Stripe (8 tags)
• Midnight Snow (8 tags)
• Kraft Tree (8 tags)
• Holiday Plaid (8 tags)
• Ornament Glow (8 tags)
• Round tags (12 tags)
• "From Santa" & "Do Not Open Until Dec 25" tags (8 tags)

⭐ FILES YOU GET
• EDITABLE PDF (type To/From names) in US Letter + A4
• PRINT & WRITE PDF in US Letter + A4

✏️ Editing works best in the free Adobe Acrobat Reader (desktop or mobile). Fonts for typed names are fixed. Fields are for names only.

⭐ PERFECT FOR
Christmas gifts • Stocking stuffers • Teacher & neighbor gifts • Holiday baking • Santa gifts for kids
""",
 files="4 dosya: Editable US-Letter + A4, Print-and-Write US-Letter + A4"),
}

for k, v in L.items():
    assert len(v["title"]) <= 140, (k, len(v["title"]))
    assert len(v["tags"]) == 13, (k, len(v["tags"]))
    for t in v["tags"]:
        assert len(t) <= 20, (k, t, len(t))
    assert len(set(v["tags"])) == 13

for k, v in L.items():
    d = os.path.join(ROOT, P[k]["dir"])
    up = sorted(os.listdir(os.path.join(d, "upload_files")))
    imgs = sorted(os.listdir(os.path.join(d, "listing_images")))
    md = f"""# {P[k]['name']}: Etsy yükleme bilgileri

> Aşağıdaki **İngilizce** metinleri olduğu gibi kopyalayıp Etsy'ye yapıştır. Açıklamalar Türkçe.

## 1. Fotoğraflar (sırayla yükle)
`listing_images/` klasöründeki dosyaları **numara sırasıyla** yükle. 01 ana (kapak) görsel olur.
{chr(10).join(f'- {i}' for i in imgs)}

**Video:** `listing_video.mp4` (10 saniye, sessiz). Fotoğrafların altındaki video alanına yükle.

## 2. Başlık (Title) ({len(v['title'])}/140 karakter)
```
{v['title']}
```

## 3. Dijital dosyalar (Digital files) — {v['files']}
`upload_files/` klasöründeki dosyaların hepsini yükle (Etsy sınırı: en fazla 5 dosya, her biri 20 MB'tan küçük. Bunlar uyuyor):
{chr(10).join(f'- {f}' for f in up)}

## 4. Fiyat
- **Normal fiyat (Price):** ${v['price']}
- **Açılış indirimi:** mağaza genelinde %40 → müşteri **${v['sale']}** öder (detay ana README'de)
- **Quantity:** 999

## 5. Kategori ve özellikler
- **Category:** {v['category']}
- **Type:** Digital (Digital files)
- **Who made it?** I did · **What is it?** A finished product · **When was it made?** en güncel aralık (2026'yı kapsayan seçenek)
- **Holiday:** Christmas · **Occasion:** (varsa) Christmas / Holiday party
- **Renewal:** Automatic · **Personalization:** kapalı
- **Shop section:** Christmas Printables

## 6. Etiketler (Tags), 13 adet, her biri en fazla 20 karakter
Etsy'de etiket kutusuna **virgülle ayrılmış tek satır** olarak yapıştırabilirsin:
```
{', '.join(v['tags'])}
```

## 7. Açıklama (Description)
```
{v['desc'].strip()}
{COMMON_END.rstrip()}
```
"""
    open(os.path.join(d, "LISTING.md"), "w").write(md)
    print("wrote", k)
