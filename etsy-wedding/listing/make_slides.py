"""Writes listing/slides.html: 10 Etsy listing images (4:3), rendered by render_slides.js to 3000x2250.

Every screenshot is a real, cropped LibreOffice render of the SAMPLE workbook (listing/shots/).
Fictional sample couple; no formulas visible.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "shots/"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600;700&display=swap');
:root{--bg:#FBF8F4;--ink:#2F2A2C;--deep:#4B3F46;--rose:#C48E86;--rose-lt:#F4E6E2;--sage:#8FA48F;--sage-lt:#E7EEE6;
--gold:#C7A465;--gold-lt:#F7EEDB;--muted:#8D8487;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#ddd;font-family:Inter,sans-serif;color:var(--ink)}
.slide{width:1500px;height:1125px;background:var(--bg);position:relative;overflow:hidden;margin:20px auto}
.serif{font-family:'Cormorant Garamond',serif}
h1{font-family:'Cormorant Garamond',serif;font-weight:600;color:var(--deep);line-height:1.02}
h2{font-family:'Cormorant Garamond',serif;font-weight:600;color:var(--deep);font-size:78px;line-height:1.05}
.kicker{font-size:22px;letter-spacing:.22em;text-transform:uppercase;color:var(--rose);font-weight:600}
.sub{font-size:28px;color:#5E585A;line-height:1.4}
.shot{background:#fff;border-radius:18px;box-shadow:0 24px 60px rgba(75,63,70,.18),0 2px 6px rgba(75,63,70,.08);
overflow:hidden;position:absolute;border:1px solid #EFE6DF}
.shot img{display:block;width:100%}
.tag{position:absolute;font-size:13px;letter-spacing:.14em;color:#B6ADB0;font-weight:600}
.pill{display:inline-block;padding:12px 24px;border-radius:999px;font-weight:600;font-size:22px;margin:0 10px 12px 0}
.p-rose{background:var(--rose-lt);color:#9A5E55}.p-sage{background:var(--sage-lt);color:#3F6B45}.p-gold{background:var(--gold-lt);color:#8A6A1F}
.p-deep{background:var(--deep);color:#fff}
.brand{position:absolute;left:70px;bottom:44px;font-family:'Cormorant Garamond',serif;font-size:26px;color:var(--muted);letter-spacing:.06em}
.num{position:absolute;right:70px;bottom:44px;font-size:18px;color:#B6ADB0;letter-spacing:.2em}
.callout{position:absolute;background:var(--deep);color:#fff;border-radius:16px;padding:22px 28px;font-size:24px;line-height:1.35;
box-shadow:0 16px 40px rgba(75,63,70,.25)}
.callout b{color:#F3D9A4}
.dot{display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:10px;vertical-align:middle}
ul.ticks{list-style:none}
ul.ticks li{font-size:27px;line-height:1.35;margin:0 0 18px 0;padding-left:48px;position:relative}
ul.ticks li:before{content:"✓";position:absolute;left:0;top:-2px;width:34px;height:34px;border-radius:50%;background:var(--sage);
color:#fff;font-size:20px;display:flex;align-items:center;justify-content:center;font-weight:700}
"""


def shot(src, left, top, width, rot=0, extra=""):
    return (f'<div class="shot" style="left:{left}px;top:{top}px;width:{width}px;transform:rotate({rot}deg);{extra}">'
            f'<img src="{S}{src}"></div>')


def frame(i, inner, sample=True):
    tag = '<div class="tag" style="right:70px;top:40px">SAMPLE DATA · PREVIEW</div>' if sample else ""
    return (f'<section class="slide">{inner}{tag}<div class="brand">NexaGlobe · Wedding Planner</div>'
            f'<div class="num">{i:02d} / 10</div></section>')


slides = []

# 01 cover
slides.append(frame(1, f"""
<div style="position:absolute;left:80px;top:90px;width:640px">
  <div class="kicker">Excel &amp; Google Sheets</div>
  <h1 style="font-size:118px;margin:22px 0 26px">Wedding<br>Planner<br>Spreadsheet</h1>
  <div class="sub" style="font-size:31px">Budget, payments, guests, seating<br>&amp; checklist, all connected.</div>
  <div style="margin-top:42px">
    <span class="pill p-deep">12 tabs</span><span class="pill p-rose">Auto dashboard</span><br>
    <span class="pill p-sage">Tip calculator</span><span class="pill p-gold">Instant download</span>
  </div>
</div>
{shot("b__Dashboard.png", 730, 590, 740, 2.5)}
{shot("a__Dashboard.png", 700, 150, 880, -3)}
"""))

# 02 everything connected (difference #1)
box = lambda x, y, t, s, c: (f'<div style="position:absolute;left:{x}px;top:{y}px;width:330px;height:170px;background:#fff;border-radius:20px;'
                             f'border-top:8px solid {c};box-shadow:0 14px 34px rgba(75,63,70,.12);padding:26px 28px">'
                             f'<div class="serif" style="font-size:40px;font-weight:600;color:#4B3F46">{t}</div>'
                             f'<div style="font-size:21px;color:#5E585A;margin-top:8px;line-height:1.35">{s}</div></div>')
arrow = lambda x, y, w, rot=0: (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:4px;background:#C7A465;'
                                f'transform:rotate({rot}deg);transform-origin:left center"></div>'
                                f'<div style="position:absolute;left:{x}px;top:{y}px;transform:rotate({rot}deg) translateX({w - 6}px);'
                                f'transform-origin:left center;width:0;height:0;border-left:18px solid #C7A465;border-top:11px solid transparent;'
                                f'border-bottom:11px solid transparent;margin-top:-9px"></div>')
slides.append(frame(2, f"""
<div style="position:absolute;left:80px;top:80px;width:1340px">
  <div class="kicker">What makes it different</div>
  <h2 style="margin-top:14px">Type it once. Everything updates.</h2>
  <div class="sub" style="margin-top:14px">Mark one payment as <b>Paid</b> and the whole planner follows. No copying numbers between tabs.</div>
</div>
<div style="position:absolute;left:80px;top:470px;width:380px;height:250px;background:#4B3F46;border-radius:24px;padding:34px;color:#fff">
  <div style="font-size:20px;letter-spacing:.18em;color:#F3D9A4;font-weight:600">YOU TYPE</div>
  <div class="serif" style="font-size:46px;font-weight:600;margin-top:12px;line-height:1.1">Payment<br>Schedule</div>
  <div style="font-size:22px;margin-top:14px;color:#E9DCD8">Deposit · $1,020 · Paid = Yes</div>
</div>
{arrow(470, 595, 130, -32)}{arrow(470, 595, 130, 0)}{arrow(470, 595, 130, 32)}
{box(620, 360, "Budget", "Paid & still owed per item, status turns PAID IN FULL", "#C7A465")}
{box(620, 555, "Who's Paying", "Your parents' pledge: paid, scheduled and left", "#C48E86")}
{box(620, 750, "Dashboard", "Paid so far, still to pay, next due dates and the monthly chart", "#8FA48F")}
<div style="position:absolute;left:1010px;top:360px;width:410px">
  <ul class="ticks">
    <li>Guest List RSVPs fill the <b>Seating Chart</b> with names</li>
    <li>Your wedding date dates the whole <b>Checklist</b></li>
    <li>Budget Builder compares <b>suggested vs planned</b> per category</li>
    <li>Overdue and due-in-30-days <b>alerts</b></li>
  </ul>
</div>
""", sample=False))

# 03 dashboard
slides.append(frame(3, f"""
<div style="position:absolute;left:80px;top:70px;width:1340px">
  <div class="kicker">Dashboard</div>
  <h2 style="margin-top:10px">Your whole wedding on one page</h2>
</div>
{shot("a__Dashboard.png", 80, 270, 1340)}
<div class="callout" style="left:860px;top:800px;width:520px">Countdown, budget, <b>paid vs still to pay</b>, RSVPs and tasks, updated automatically.</div>
"""))

# 04 payments
slides.append(frame(4, f"""
<div style="position:absolute;left:80px;top:70px;width:1340px">
  <div class="kicker">Payment Schedule</div>
  <h2 style="margin-top:10px">Never miss a deposit or final balance</h2>
</div>
{shot("d__Payment_Schedule.png", 80, 250, 1340)}
<div style="position:absolute;left:80px;top:880px">
  <span class="pill" style="background:#F5D7D1;color:#A23B2A">OVERDUE</span>
  <span class="pill" style="background:#FBEBC8;color:#8A5A00">DUE SOON</span>
  <span class="pill" style="background:#E6ECF3;color:#3D5A80">UPCOMING</span>
  <span class="pill p-sage">PAID</span>
</div>
<div class="callout" style="left:900px;top:860px;width:480px">Every deposit &amp; balance with its <b>due date</b>, who paid it, and a <b>monthly cash-flow</b> chart.</div>
"""))

# 05 who's paying
slides.append(frame(5, f"""
<div style="position:absolute;left:80px;top:110px;width:600px">
  <div class="kicker">Who's Paying</div>
  <h2 style="margin-top:14px">Parents chipping in? Keep it clear.</h2>
  <div class="sub" style="margin-top:26px">Add up to 5 contributors with their pledge. Every payment you mark with <b>Paid by</b> shows here:</div>
  <ul class="ticks" style="margin-top:30px">
    <li>Pledged vs paid vs scheduled</li>
    <li>How much of each pledge is left</li>
    <li>Funding gap: cost minus pledges</li>
  </ul>
</div>
{shot("a__Whos_Paying.png", 760, 90, 640, 1.5)}
"""))

# 06 guests + seating
slides.append(frame(6, f"""
<div style="position:absolute;left:80px;top:70px;width:1340px">
  <div class="kicker">Guest List &amp; Seating Chart</div>
  <h2 style="margin-top:10px">RSVPs, meals &amp; a seating chart that fills itself</h2>
</div>
{shot("a__Guest_List.png", 80, 290, 900, -1.5)}
{shot("a__Seating_Chart.png", 520, 640, 900, 1.5)}
<div class="callout" style="left:1010px;top:300px;width:410px">Pick a table on the Guest List and the <b>names appear</b> on the Seating Chart, with capacity warnings.</div>
"""))

# 07 tips
slides.append(frame(7, f"""
<div style="position:absolute;left:80px;top:70px;width:1340px">
  <div class="kicker">Tips &amp; Envelopes</div>
  <h2 style="margin-top:10px">Know exactly what to tip, and who hands it over</h2>
</div>
{shot("a__Tips_and_Envelopes.png", 80, 290, 1340)}
<div style="position:absolute;left:80px;top:830px;width:820px">
  <ul class="ticks">
    <li>% of bill, flat amount or per person</li>
    <li>Skips vendors with gratuity already in the contract</li>
    <li>Envelope-ready checklist for the big day</li>
  </ul>
</div>
<div class="callout" style="left:930px;top:850px;width:450px">Common US tip ranges included as a guide. <b>Edit everything.</b></div>
"""))

# 08 checklist + budget builder
slides.append(frame(8, f"""
<div style="position:absolute;left:80px;top:70px;width:1340px">
  <div class="kicker">Checklist &amp; Budget Builder</div>
  <h2 style="margin-top:10px">55 tasks, dated from your wedding day</h2>
</div>
{shot("a__Checklist.png", 80, 270, 700, -1.5)}
{shot("a__Budget_Builder.png", 720, 300, 700, 1.5)}
<div class="callout" style="left:760px;top:880px;width:620px">Enter your date once: every task gets a <b>due date</b>. Split your budget across <b>18 categories</b>.</div>
"""))

# 09 what's included
tabs = [("Start Here", "names, date, budget, currency"), ("Dashboard", "countdown, KPIs, charts"),
        ("Budget Builder", "split by category"), ("Budget", "every cost & status"),
        ("Payment Schedule", "due dates & alerts"), ("Who's Paying", "contributors & pledges"),
        ("Vendors", "contacts, quote ranking"), ("Guest List", "RSVP, meals, gifts"),
        ("Seating Chart", "tables fill with names"), ("Checklist", "55 dated tasks"),
        ("Tips & Envelopes", "tip calculator"), ("Day-Of Timeline", "hour-by-hour plan")]
cells = "".join(f'<div style="background:#fff;border-radius:16px;padding:20px 24px;border-left:6px solid '
                f'{["#C48E86", "#8FA48F", "#C7A465"][i % 3]}"><div class="serif" style="font-size:32px;font-weight:600;color:#4B3F46">{t}</div>'
                f'<div style="font-size:19px;color:#8D8487;margin-top:4px">{d}</div></div>' for i, (t, d) in enumerate(tabs))
slides.append(frame(9, f"""
<div style="position:absolute;left:80px;top:70px;width:1340px">
  <div class="kicker">What's included</div>
  <h2 style="margin-top:10px">12 connected tabs + 3 files</h2>
</div>
<div style="position:absolute;left:80px;top:270px;width:900px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px">{cells}</div>
<div style="position:absolute;left:1020px;top:270px;width:400px;background:#4B3F46;border-radius:24px;padding:36px;color:#fff">
  <div style="font-size:20px;letter-spacing:.18em;color:#F3D9A4;font-weight:600">YOU DOWNLOAD</div>
  <div style="font-size:25px;line-height:1.5;margin-top:18px">
  <span class="dot" style="background:#C48E86"></span>Blank planner (.xlsx)<br>
  <span class="dot" style="background:#8FA48F"></span>Sample planner to explore<br>
  <span class="dot" style="background:#C7A465"></span>Quick-start guide (PDF)</div>
  <div style="font-size:20px;letter-spacing:.18em;color:#F3D9A4;font-weight:600;margin-top:34px">WORKS IN</div>
  <div style="font-size:25px;line-height:1.5;margin-top:12px">Microsoft Excel 2016+<br>Excel for Mac<br>Google Sheets (free)</div>
  <div style="font-size:20px;letter-spacing:.18em;color:#F3D9A4;font-weight:600;margin-top:34px">12 CURRENCIES</div>
  <div style="font-size:22px;line-height:1.5;margin-top:12px">$ · € · £ · CA$ · AU$ · and more</div>
</div>
""", sample=False))

# 10 how it works
step = lambda n, t, d, x: (f'<div style="position:absolute;left:{x}px;top:420px;width:400px;background:#fff;border-radius:24px;padding:40px 36px;'
                           f'box-shadow:0 14px 34px rgba(75,63,70,.10)"><div class="serif" style="font-size:90px;color:#C48E86;line-height:1">{n}</div>'
                           f'<div class="serif" style="font-size:42px;font-weight:600;color:#4B3F46;margin-top:10px">{t}</div>'
                           f'<div style="font-size:24px;color:#5E585A;margin-top:12px;line-height:1.4">{d}</div></div>')
slides.append(frame(10, f"""
<div style="position:absolute;left:80px;top:90px;width:1340px">
  <div class="kicker">How it works</div>
  <h2 style="margin-top:14px">Start planning in 5 minutes</h2>
  <div class="sub" style="margin-top:14px">Digital download. Nothing is shipped. Files are available right after purchase.</div>
</div>
{step("1", "Download", "Find the files under Purchases &amp; Reviews in your Etsy account.", 80)}
{step("2", "Open", "Open in Excel, or upload to Google Drive and open with Google Sheets.", 550)}
{step("3", "Fill in", "Add your names, date and budget on Start Here. The rest updates itself.", 1020)}
<div style="position:absolute;left:80px;top:850px;width:1340px;font-size:22px;color:#8D8487;line-height:1.5">
Personal use only. Sample names, vendors and amounts are fictional. Tip ranges and budget splits are editable suggestions, not rules.</div>
""", sample=False))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(slides)}</body></html>"
(HERE / "slides.html").write_text(html)
print("wrote slides.html with", len(slides), "slides")
