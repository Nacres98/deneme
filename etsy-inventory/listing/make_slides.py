"""Build the 10 Etsy listing images (3000x2250) from the real workbook screenshots in listing/shots.

Copy-safety: only partial crops are shown, every screenshot carries a faint "SAMPLE DATA · PREVIEW" watermark,
no formula bar / formulas are ever visible.

Usage: python3 listing/make_shots.py && python3 listing/make_slides.py && node listing/render_slides.js
"""
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SH = HERE / "shots"
DER = SH / "derived"
DER.mkdir(exist_ok=True)


def crop(src, box_frac, name):
    im = Image.open(SH / src)
    w, h = im.size
    x0, y0, x1, y1 = box_frac
    im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).save(DER / name)
    return f"shots/derived/{name}"


def hconcat(parts, name):
    ims = []
    for src, (x0, x1) in parts:
        im = Image.open(SH / src)
        w, h = im.size
        ims.append(im.crop((int(x0 * w), 0, int(x1 * w), h)))
    out = Image.new("RGB", (sum(i.width for i in ims), max(i.height for i in ims)), "white")
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width
    out.save(DER / name)
    return f"shots/derived/{name}"


dash = Image.open(SH / "main__Dashboard.png")
laptop = crop("main__Dashboard.png", (0, 0, 1, min(1, dash.width / 1.6 / dash.height)), "laptop_dash.png")
fees = crop("main__Sales.png", (0.512, 0, 1, 0.86), "sales_fees.png")
status = hconcat([("main__Products.png", (0, 0.147)), ("main__Products.png", (0.528, 0.93))], "products_status.png")
recipes = "shots/main__Recipes.png"
pricing = "shots/main__Pricing_Calculator.png"
reports = crop("main__Reports.png", (0, 0, 1, 1), "reports.png")
goals = crop("extra__Dashboard.png", (0, 0.27, 1, 1), "dash_tax_goals.png")
types = "shots/main__Start_Here.png"
legend = "shots/extra__Start_Here.png"
kpis = {c: f"shots/kpi_{c}__Dashboard.png" for c in ("USD", "GBP", "EUR", "TRY")}
TABS = ["Dashboard", "Sales", "Order Import", "Products", "Performance", "Pricing Calculator", "Materials", "Recipes",
        "Stock Log", "Suppliers", "Expenses", "Mileage", "Reports", "Start Here"]
tab_img = {t: f"shots/main__{t.replace(' ', '_')}.png" for t in TABS}


def shot(src, cls="", style=""):
    return f'<div class="shot {cls}" style="{style}"><img src="{src}"><div class="wm"></div></div>'


def badge(t, cls=""):
    return f'<span class="badge {cls}">{t}</span>'


def callout(t, style):
    return f'<div class="callout" style="{style}">{t}</div>'


slides = []
# 1 hero
slides.append(f"""
<div class="slide s1">
  <div class="kicker">EXCEL + GOOGLE SHEETS · INSTANT DOWNLOAD</div>
  <h1>Inventory &amp; Profit Tracker<br><span>for Any Small Business</span></h1>
  <div class="badges">{badge("14 TABS")}{badge("ANY BUSINESS", "clay")}{badge("TRUE PROFIT", "deep")}</div>
  <div class="laptop"><div class="screen">{shot(laptop, "flat")}</div><div class="base"></div></div>
  <div class="strip">Sample + Blank files &nbsp;·&nbsp; One-time purchase, no subscription &nbsp;·&nbsp; Works for makers, retail, food, B2B &amp; online shops</div>
</div>""")
# 2 KPIs
slides.append(f"""
<div class="slide">
  <h2>See your real profit instantly</h2>
  <p class="sub">12 live KPI cards · month-over-month change · goal progress</p>
  {shot(kpis["USD"], "", "width:1120px;left:190px;top:300px")}
  {callout("Profit after ALL fees,<br>shipping &amp; product cost", "left:60px;top:880px")}
  {callout("▲▼ vs last month,<br>automatically", "right:60px;top:880px")}
</div>""")
# 3 fees
slides.append(f"""
<div class="slide">
  <h2>Every fee, calculated for you</h2>
  <p class="sub">Listing · transaction · card processing · ads fees · shipping labels · product cost</p>
  {shot(fees, "", "width:1380px;left:60px;top:290px")}
  <div class="row3" style="top:830px">
    <div class="mini"><b>Any channel</b><br>In-store, invoices, website, Shopify, Etsy, Amazon: each with its own fee rates</div>
    <div class="mini"><b>Multi-item orders</b><br>Fixed fees charged once per order, automatically</div>
    <div class="mini"><b>Refunds &amp; unpaid invoices</b><br>Handled with one status dropdown</div>
  </div>
</div>""")
# 4 recipes
slides.append(f"""
<div class="slide">
  <h2>Recipes deduct your supplies</h2>
  <p class="sub">Make or sell 1 product → every material it uses updates automatically</p>
  <div class="flow">
    <div class="node deep">Make 1 × Candle 8 oz</div><div class="arrow">→</div>
    <div class="node">−200 g wax</div><div class="node">−20 ml fragrance</div><div class="node">−1 jar</div>
    <div class="node">−1 wick</div><div class="node">−1 label</div>
  </div>
  {shot(recipes, "", "width:1380px;left:60px;top:470px")}
  {callout("Unit cost builds itself:<br>materials + waste % + labor", "left:60px;top:760px")}
  {callout("Works for bakeries, soap,<br>jewelry, furniture, kits…", "right:60px;top:760px")}
</div>""")
# 5 stock
slides.append(f"""
<div class="slide">
  <h2>Never run out again</h2>
  <p class="sub">Days of stock left · stockout date · suggested batch / reorder quantity</p>
  {shot(status, "", "width:1380px;left:60px;top:290px")}
  <div class="row3" style="top:930px">
    <div class="mini"><span class="pill ok">IN STOCK</span></div>
    <div class="mini"><span class="pill warn">REORDER SOON</span> <span class="pill crit">CRITICAL</span></div>
    <div class="mini"><span class="pill out">OUT OF STOCK</span> &nbsp;for products AND raw materials</div>
  </div>
</div>""")
# 6 pricing
slides.append(f"""
<div class="slide">
  <h2>Know exactly what to charge</h2>
  <p class="sub">Pricing Calculator: break-even, suggested retail (.99), wholesale and free-shipping scenarios</p>
  {shot(pricing, "", "width:1380px;left:60px;top:290px")}
</div>""")
# 7 tax
slides.append(f"""
<div class="slide">
  <h2>Tax time, done</h2>
  <p class="sub">Monthly P&amp;L · expense categories mapped to Schedule C / HMRC · COGS worksheet · tax set-aside calendar</p>
  {shot(reports, "", "width:900px;left:60px;top:300px")}
  {shot(goals, "", "width:820px;left:620px;top:560px")}
</div>""")
# 8 currency
slides.append(f"""
<div class="slide">
  <h2>Your currency, one click</h2>
  <p class="sub">12 currencies: $ € £ ₺ ₹ CA$ AU$ NZ$ CHF MX$ S$ R</p>
  {shot(kpis["USD"], "fan", "width:620px;left:100px;top:290px;transform:rotate(-1.5deg)")}
  {shot(kpis["GBP"], "fan", "width:620px;left:780px;top:290px;transform:rotate(1.5deg)")}
  {shot(kpis["EUR"], "fan", "width:620px;left:100px;top:660px;transform:rotate(1deg)")}
  {shot(kpis["TRY"], "fan", "width:620px;left:780px;top:660px;transform:rotate(-1deg)")}
  <div class="cur" style="left:70px;top:265px">USD $</div><div class="cur" style="left:750px;top:265px">GBP £</div>
  <div class="cur" style="left:70px;top:635px">EUR €</div><div class="cur" style="left:750px;top:635px">TRY ₺</div>
</div>""")
# 9 any business
slides.append(f"""
<div class="slide">
  <h2>Made for any kind of business</h2>
  <p class="sub">Clear setup guide inside · color-coded cells · locked formulas you can't break</p>
  {shot(types, "", "width:1380px;left:60px;top:290px")}
  <div class="row3" style="top:880px">
    <div class="mini"><span class="chip" style="background:#FFF6E0">Cream = type here</span></div>
    <div class="mini"><span class="chip" style="background:#EEF3EF;color:#3F5A48">Green = pick from list ▼</span></div>
    <div class="mini"><span class="chip">White = automatic (locked)</span></div>
  </div>
</div>""")
# 10 everything inside
tiles = "".join(f'<div class="tile"><div class="timg" style="background-image:url(\'{tab_img[t]}\')"></div><div class="tname">{t}</div></div>'
                for t in TABS)
tiles += ('<div class="tile file"><div class="fi">XLSX</div><div class="tname">SAMPLE DATA file</div></div>'
          '<div class="tile file"><div class="fi deep">XLSX</div><div class="tname">BLANK file + PDF guide</div></div>')
slides.append(f"""
<div class="slide">
  <h2>Everything inside</h2>
  <p class="sub">14 connected tabs · Sample + Blank files · User Guide · Excel 2016+ &amp; Google Sheets</p>
  <div class="grid">{tiles}</div>
  <div class="strip">Instant download · Digital file, no physical item shipped</div>
</div>""")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;600;700;800&display=swap');
:root { --bg:#FAF7F2; --sand:#E9DFCF; --sage:#7C9A82; --deep:#3F5A48; --clay:#C98B6B; --ink:#2B2B2B; --muted:#8A8A80; }
* { box-sizing:border-box; margin:0; }
body { background:#ddd; font-family:Inter, sans-serif; }
.slide { width:1500px; height:1125px; background:var(--bg); position:relative; overflow:hidden; margin-bottom:20px; }
.slide::before { content:""; position:absolute; right:-160px; top:-160px; width:520px; height:520px; border-radius:50%; background:#EFE7D8; }
h1 { position:absolute; left:80px; top:115px; font-family:'DM Serif Display', serif; font-weight:400; font-size:70px; line-height:1.02; color:var(--deep); }
h1 span { color:var(--clay); }
h2 { position:absolute; left:80px; top:70px; font-family:'DM Serif Display', serif; font-weight:400; font-size:72px; color:var(--deep); }
.sub { position:absolute; left:82px; top:170px; font-size:27px; color:var(--clay); font-weight:600; max-width:1340px; }
.kicker { position:absolute; left:84px; top:70px; font-size:20px; letter-spacing:.18em; font-weight:700; color:var(--sage); }
.badges { position:absolute; left:80px; top:380px; display:flex; flex-direction:column; gap:16px; }
.badge { display:inline-block; background:var(--sage); color:#fff; font-weight:800; font-size:26px; letter-spacing:.06em; padding:14px 26px; border-radius:40px; width:max-content; }
.badge.clay { background:var(--clay); } .badge.deep { background:var(--deep); }
.shot { position:absolute; background:#fff; border-radius:14px; box-shadow:0 18px 50px rgba(63,90,72,.18), 0 2px 6px rgba(0,0,0,.06); overflow:hidden; border:1px solid #E6DCCB; }
.shot img { width:100%; display:block; }
.shot.flat { position:relative; border-radius:0; box-shadow:none; border:none; }
.wm { position:absolute; inset:0; pointer-events:none;
      background-image:repeating-linear-gradient(-28deg, transparent 0 210px, rgba(63,90,72,.0) 210px 211px);
}
.wm::after { content:"SAMPLE DATA · PREVIEW   SAMPLE DATA · PREVIEW   SAMPLE DATA · PREVIEW   SAMPLE DATA · PREVIEW   SAMPLE DATA · PREVIEW   SAMPLE DATA · PREVIEW";
      position:absolute; left:-20%; top:38%; width:140%; transform:rotate(-12deg); font-weight:800; font-size:44px; letter-spacing:.12em;
      color:rgba(63,90,72,.10); white-space:nowrap; text-align:center; }
.laptop { position:absolute; left:500px; top:345px; width:900px; }
.screen { background:#1f2421; border-radius:22px 22px 0 0; padding:22px 22px 26px; }
.screen .shot.flat { border-radius:4px; }
.base { height:34px; background:linear-gradient(#d9d5cf,#b9b4ac); border-radius:0 0 28px 28px; margin:0 -60px; box-shadow:0 20px 40px rgba(0,0,0,.15); }
.strip { position:absolute; left:0; right:0; bottom:0; height:92px; background:var(--deep); color:#fff; font-size:25px; font-weight:600; display:flex; align-items:center; justify-content:center; letter-spacing:.02em; }
.callout { position:absolute; background:var(--clay); color:#fff; font-weight:700; font-size:28px; line-height:1.25; padding:20px 28px; border-radius:16px; box-shadow:0 10px 30px rgba(201,139,107,.35); }
.row3 { position:absolute; left:60px; right:60px; top:880px; display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
.mini { background:#fff; border:1px solid #E6DCCB; border-top:6px solid var(--sage); border-radius:12px; padding:20px 22px; font-size:22px; color:var(--ink); line-height:1.35; }
.mini b { color:var(--deep); font-size:24px; }
.pill { display:inline-block; font-weight:800; font-size:21px; padding:8px 16px; border-radius:8px; margin:2px 0; }
.pill.ok { background:#DCEBDF; color:#3F7A4F; } .pill.warn { background:#FBEFD3; color:#9A6B00; }
.pill.crit { background:#F6DAD3; color:#A8402B; } .pill.out { background:#3A3A3A; color:#fff; }
.chip { display:inline-block; font-weight:700; font-size:24px; padding:10px 18px; border:2px solid #E8D9B0; border-radius:8px; color:#5B5B55; background:#fff; }
.flow { position:absolute; left:60px; right:60px; top:290px; display:flex; align-items:center; gap:14px; flex-wrap:nowrap; }
.node { background:#fff; border:2px solid var(--sage); color:var(--deep); font-weight:800; font-size:25px; padding:16px 20px; border-radius:14px; white-space:nowrap; }
.node.deep { background:var(--deep); color:#fff; border-color:var(--deep); }
.arrow { font-size:48px; color:var(--clay); font-weight:800; }
.grid { position:absolute; left:60px; right:60px; top:260px; display:grid; grid-template-columns:repeat(4,1fr); gap:18px; }
.tile { background:#fff; border:1px solid #E6DCCB; border-radius:12px; overflow:hidden; height:172px; position:relative; box-shadow:0 6px 18px rgba(63,90,72,.10); }
.timg { height:122px; background-size:cover; background-position:left top; filter:saturate(.95); }
.tname { position:absolute; bottom:0; left:0; right:0; height:50px; background:var(--deep); color:#fff; font-weight:700; font-size:21px; display:flex; align-items:center; padding-left:16px; }
.tile.file { display:flex; align-items:flex-start; justify-content:center; background:#F3EEE5; }
.fi { margin-top:22px; width:84px; height:92px; background:var(--sage); color:#fff; font-weight:800; font-size:20px; display:flex; align-items:center; justify-content:center; border-radius:8px; }
.fi.deep { background:var(--deep); }
.fan { box-shadow:0 24px 60px rgba(63,90,72,.25); }
.cur { position:absolute; z-index:5; background:var(--deep); color:#fff; font-weight:800; font-size:24px; padding:8px 16px; border-radius:10px; }
"""

html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(slides)}</body></html>"
(HERE / "slides.html").write_text(html, encoding="utf-8")
print("wrote", HERE / "slides.html", len(slides), "slides")
