"""Etsy listing images: fill a demo copy of each product, render one sheet with LibreOffice,
then frame it in a 2700x2025 (4:3) cover (Playwright via screenshot.js).

    python3 -m tools.etsy.mockups            # -> etsy/products/<slug>/images/*.png
Demo data is only for the pictures; the files buyers get stay empty.
"""
from __future__ import annotations

import base64
import random
import shutil
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image, ImageChops

from .build import OUT, PRODUCTS, ROOT

FONT_URL = (ROOT / "assets" / "fonts" / "Montserrat.ttf").as_uri()


# ---------- demo data ----------
def demo_budget(wb):
    ws = wb["Transactions"]
    rnd = random.Random(7)
    rows, d = [], date(2027, 1, 1)
    fixed = [("Salary", "Income", 3400, 1), ("Salary", "Income", 3400, 15), ("Rent / Mortgage", "Expense", 1350, 2),
             ("Utilities", "Expense", 160, 8), ("Phone & Internet", "Expense", 95, 10),
             ("Subscriptions", "Expense", 38, 12), ("Car payment", "Expense", 310, 20), ("Insurance", "Expense", 140, 22),
             ("Savings transfer", "Expense", 600, 16), ("Side hustle", "Income", 450, 25)]
    for m in range(1, 13):
        for cat, typ, amt, day in fixed:
            rows.append((date(2027, m, day), cat, typ, cat, round(amt * rnd.uniform(.95, 1.05), 2)))
        for _ in range(14):
            cat = rnd.choice(["Groceries", "Dining out", "Transport", "Entertainment", "Clothing", "Health", "Pets"])
            rows.append((date(2027, m, rnd.randint(1, 28)), cat, "Expense", cat, round(rnd.uniform(12, 140), 2)))
    for i, (dt, desc, typ, cat, amt) in enumerate(rows):
        r = 5 + i
        for c, v in enumerate((dt, desc, typ, cat, amt), start=1):
            ws.cell(row=r, column=c, value=v)
    s = wb["Setup"]
    budgets = [1350, 170, 520, 220, 200, 310, 140, 95, 40, 120, 60, 90, 0, 80, 150, 0, 50, 0, 600, 40]
    for i, b in enumerate(budgets):
        s.cell(row=7 + i, column=6, value=b)
    s["C7"], s["C8"] = 6800, 400
    g = wb["Savings Goals"]
    for r, (t, saved) in enumerate([(10000, 6400), (3000, 1150), (8000, 2300)], start=5):
        g.cell(row=r, column=2, value=t)
        g.cell(row=r, column=3, value=saved)


def demo_habits(wb):
    rnd = random.Random(3)
    for m, sheet in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
        ws = wb[sheet]
        days = (date(2027 + (m == 11), (m + 1) % 12 + 1, 1) - timedelta(days=1)).day
        for h in range(8):
            p = min(.95, .45 + .04 * m + .03 * (h % 3))
            for d in range(days):
                if rnd.random() < p:
                    ws.cell(row=6 + h, column=2 + d, value="✓")


def demo_life(wb):
    data = {
        "Key Contacts": [("Sarah Miller", "Sister / Executor", "(555) 201-3344", "sarah@example.com", "", "Yes"),
                         ("John Carter", "Estate attorney", "(555) 410-2200", "jc@example.com", "", "Yes"),
                         ("Dr. Lee", "Family doctor", "(555) 330-1188", "", "", "No")],
        "Bank Accounts": [("First Community Bank", "Checking", "4821", "Joint", "Spouse", 8400, "Yes"),
                          ("First Community Bank", "Savings", "1177", "Joint", "Spouse", 22500, "Yes"),
                          ("Online Bank", "Savings", "9032", "Me", "Sarah Miller", 12000, "Yes")],
        "Retirement & Investments": [("Fidelity", "401(k)", "5521", "Spouse", 148000),
                                     ("Vanguard", "Roth IRA", "3390", "Spouse", 41000)],
        "Property & Assets": [("Family home", "Real estate", "Deed in fire safe", 385000),
                              ("2021 Honda CR-V", "Vehicle", "Title in file cabinet", 21000)],
        "Debts & Loans": [("Home Lending Co.", "Mortgage", "7781", 214000, 1680, 1, "Yes"),
                          ("Auto Finance", "Auto loan", "2290", 9800, 365, 15, "Yes")],
        "Insurance": [("Life Insurer A", "Life", "6612", "Me", "Spouse", 500000)],
        "Digital Accounts": [("Gmail", "me@example.com", "Password manager", "My phone", "Download data first")],
    }
    for sheet, rows in data.items():
        ws = wb[sheet]
        for i, row in enumerate(rows):
            for c, v in enumerate(row, start=1):
                ws.cell(row=5 + i, column=c, value=v)
    p = wb["Personal Info"]
    for r, (det, loc) in enumerate([("Jane A. Miller", ""), ("03/14/1961", ""), ("", "Fire safe, top shelf"),
                                    ("", "Fire safe"), ("", "Desk drawer")], start=5):
        p.cell(row=r, column=2, value=det or "On file")
        p.cell(row=r, column=3, value=loc)


SHOTS = {
    "budget-planner-2027": (demo_budget, [("Dashboard", "01_dashboard"), ("Monthly", "02_monthly"),
                                          ("Transactions", "03_transactions")]),
    "habit-tracker-2027": (demo_habits, [("Year Overview", "01_overview"), ("Mar", "02_month")]),
    "life-organizer": (demo_life, [("Dashboard", "01_dashboard"), ("Bank Accounts", "02_accounts"),
                                   ("Start Here", "03_start")]),
}

COPY = {
    "budget-planner-2027": ("2027 Budget Planner", "Google Sheets + Excel",
                            ["Automatic dashboard & chart", "Monthly summary by category", "Savings goals + debt payoff",
                             "Instant download"]),
    "habit-tracker-2027": ("2027 Habit Tracker", "Google Sheets + Excel",
                           ["12 monthly trackers", "Auto progress bars", "Year-at-a-glance heatmap",
                            "Instant download"]),
    "life-organizer": ("Just In Case Life Organizer", "End of Life Planner · Google Sheets + Excel",
                       ["13 organized sections", "Auto net-worth dashboard", "Final wishes & document locator",
                        "Instant download"]),
}


def render_sheet(xlsx: Path, sheet: str, tmp: Path) -> Path:
    wb = load_workbook(xlsx)
    for ws in list(wb.worksheets):
        if ws.title != sheet:
            ws.sheet_state = "hidden"
    wb.active = wb.sheetnames.index(sheet)
    one = tmp / f"{xlsx.stem}__{sheet.replace(' ', '_')}.xlsx"
    wb.save(one)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(one)],
                   check=True, capture_output=True, timeout=180)
    pdf = one.with_suffix(".pdf")
    subprocess.run(["pdftoppm", "-r", "220", "-png", "-f", "1", "-l", "1", str(pdf), str(pdf.with_suffix(""))],
                   check=True, capture_output=True)
    png = next(tmp.glob(pdf.stem + "-*.png"))
    im = Image.open(png).convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if bbox:
        pad = 40
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad),
                      min(im.height, bbox[3] + pad)))
    out = tmp / f"{pdf.stem}_crop.png"
    im.save(out)
    return out


def cover_html(slug, shot: Path, color: str, main: bool) -> str:
    t, sub, bullets = COPY[slug]
    b64 = base64.b64encode(shot.read_bytes()).decode()
    li = "".join(f"<li>{b}</li>" for b in bullets) if main else ""
    head = (f"<div class='hd'><h1>{t}</h1><p>{sub}</p><ul>{li}</ul></div>" if main
            else f"<div class='hd small'><h1>{t}</h1><p>{sub}</p></div>")
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
@font-face{{font-family:M;src:url('{FONT_URL}')}}
*{{box-sizing:border-box;margin:0}}
body{{width:2700px;height:2025px;font-family:M,sans-serif;background:#{color};display:flex;
 flex-direction:column;padding:110px 130px;gap:70px;overflow:hidden;color:#fff}}
.hd h1{{font-size:{'150' if main else '96'}px;font-weight:800;letter-spacing:-2px}}
.hd p{{font-size:{'58' if main else '44'}px;opacity:.85;margin-top:14px;font-weight:500}}
ul{{list-style:none;display:flex;gap:26px;margin-top:44px;padding:0;flex-wrap:wrap}}
li{{background:rgba(255,255,255,.16);border-radius:60px;padding:18px 40px;font-size:44px;font-weight:600}}
.shot{{flex:1;min-height:0;background:#fff;border-radius:36px;box-shadow:0 40px 90px rgba(0,0,0,.35);
 display:flex;align-items:flex-start;justify-content:center;overflow:hidden;padding:40px}}
.shot img{{max-width:100%;max-height:100%;object-fit:contain;object-position:top}}
</style></head><body>{head}<div class=shot><img src="data:image/png;base64,{b64}"></div></body></html>"""


def main():
    tmp = Path(tempfile.mkdtemp())
    jobs = []
    for slug, (fill_demo, shots) in SHOTS.items():
        p = PRODUCTS[slug]
        demo = tmp / f"demo_{p['file']}"
        wb = load_workbook(OUT / slug / p["file"])
        fill_demo(wb)
        wb.save(demo)
        img_dir = OUT / slug / "images"
        img_dir.mkdir(exist_ok=True)
        for i, (sheet, name) in enumerate(shots):
            shot = render_sheet(demo, sheet, tmp)
            html = tmp / f"{slug}_{name}.html"
            html.write_text(cover_html(slug, shot, p["color"], main=(i == 0)))
            jobs += [str(html), str(img_dir / f"{name}.png")]
    subprocess.run(["node", str(Path(__file__).with_name("screenshot.js")), *jobs], check=True, timeout=300)
    for out in jobs[1::2]:
        print("wrote", Path(out).relative_to(ROOT))
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
