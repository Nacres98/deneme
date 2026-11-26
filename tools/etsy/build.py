"""Build every Etsy digital product: the spreadsheet plus the buyer's 'How to use' PDF.

    python3 -m tools.etsy.build            # all products -> etsy/products/<slug>/
    python3 -m tools.etsy.build --check    # also recalculate in LibreOffice and scan for formula errors
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from . import budget_planner, habit_tracker, life_organizer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "etsy" / "products"
FONT_FILE = ROOT / "assets" / "fonts" / "Montserrat.ttf"

PRODUCTS = {
    "life-organizer": dict(
        module=life_organizer, file="Just_In_Case_Life_Organizer.xlsx",
        name="Just In Case Life Organizer", color="3E5C50",
        tabs=["Start Here: how to use, privacy tips", "Dashboard: progress + estimated net worth",
              "13 organizer tabs: contacts, accounts, insurance, assets, debts, bills, digital accounts, "
              "medical, final wishes, document locator, pets & dependents"]),
    "budget-planner-2027": dict(
        module=budget_planner, file="2027_Budget_Planner.xlsx",
        name="2027 Budget Planner", color="2F4B7C",
        tabs=["Setup: your categories and monthly budgets", "Transactions: log income and expenses (1,500 rows)",
              "Monthly: automatic summary by category, over-budget in red", "Dashboard: yearly totals, savings "
              "rate, chart, budget use", "Savings Goals and Debt Payoff trackers"]),
    "habit-tracker-2027": dict(
        module=habit_tracker, file="2027_Habit_Tracker.xlsx",
        name="2027 Habit Tracker", color="6B4E71",
        tabs=["Setup: up to 12 habits and monthly goals", "12 month tabs: tick ✓ each day, progress bars",
              "Year Overview: heatmap of every habit by month"]),
}


def instructions_pdf(slug: str, p: dict, path: Path):
    pdfmetrics.registerFont(TTFont("Mont", str(FONT_FILE)))
    c = canvas.Canvas(str(path), pagesize=LETTER)
    w, h = LETTER
    brand = HexColor("#" + p["color"])
    c.setFillColor(brand)
    c.rect(0, h - 1.6 * inch, w, 1.6 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Mont", 26)
    c.drawString(0.8 * inch, h - 0.95 * inch, p["name"])
    c.setFont("Mont", 12)
    c.drawString(0.8 * inch, h - 1.3 * inch, "Thank you for your purchase! Here is how to get started.")

    y = h - 2.2 * inch

    def heading(text):
        nonlocal y
        c.setFillColor(brand)
        c.setFont("Mont", 14)
        c.drawString(0.8 * inch, y, text)
        y -= 0.3 * inch

    def line(text, indent=0.8):
        nonlocal y
        c.setFillColor(HexColor("#2B2B2B"))
        c.setFont("Mont", 10.5)
        # crude wrap at ~95 chars
        words, cur = text.split(), ""
        for wd in words:
            if len(cur) + len(wd) + 1 > 92:
                c.drawString(indent * inch, y, cur)
                y -= 0.22 * inch
                cur = wd
            else:
                cur = f"{cur} {wd}".strip()
        c.drawString(indent * inch, y, cur)
        y -= 0.26 * inch

    heading("Open in Google Sheets (free)")
    for s in ["1. Go to drive.google.com and sign in.",
              f"2. Click New > File upload and choose {p['file']}.",
              "3. Double-click the file, then File > Save as Google Sheets.",
              "4. Work in the new Google Sheets copy. Everything updates automatically."]:
        line(s, 1.0)
    y -= 0.1 * inch
    heading("Open in Microsoft Excel")
    for s in ["1. Download the .xlsx file to your computer.",
              "2. Open it in Excel (desktop, web or mobile). If you see 'Protected View', click Enable Editing."]:
        line(s, 1.0)
    y -= 0.1 * inch
    heading("What's inside")
    for t in p["tabs"]:
        line("• " + t, 1.0)
    y -= 0.1 * inch
    heading("Tips")
    for s in ["Shaded rows are for typing. Cells with formulas fill in by themselves; avoid typing over them.",
              "Look for dropdown arrows in a cell: pick from the list instead of typing.",
              "Make a copy before big changes (File > Make a copy) so you always have a clean version."]:
        line("• " + s, 1.0)
    if slug == "life-organizer":
        y -= 0.1 * inch
        heading("Privacy")
        line("• Record where things are and last 4 digits only. Never store full account numbers, "
             "Social Security numbers or passwords in a spreadsheet.", 1.0)
        line("• This is a record-keeping tool, not legal or financial advice.", 1.0)
    c.setFillColor(HexColor("#8A8A8A"))
    c.setFont("Mont", 9)
    c.drawString(0.8 * inch, 0.6 * inch, "Personal use only. Please do not resell or share the file. "
                                         "Questions? Message the shop on Etsy.")
    c.showPage()
    c.save()


def check(xlsx: Path) -> list[str]:
    """Recalculate with LibreOffice and return cells holding error values."""
    from openpyxl import load_workbook
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(tmp), str(xlsx)],
                   check=True, capture_output=True, timeout=180)
    wb = load_workbook(tmp / xlsx.name, data_only=True)
    bad = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("#") and cell.value.endswith(("!", "?", "A")):
                    bad.append(f"{ws.title}!{cell.coordinate}={cell.value}")
    shutil.rmtree(tmp)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("only", nargs="*")
    a = ap.parse_args()
    for slug, p in PRODUCTS.items():
        if a.only and slug not in a.only:
            continue
        d = OUT / slug
        d.mkdir(parents=True, exist_ok=True)
        x = p["module"].build(d / p["file"])
        instructions_pdf(slug, p, d / "How_To_Use.pdf")
        print(f"built {x.relative_to(ROOT)}")
        if a.check:
            bad = check(x)
            print(f"  formula errors: {len(bad)}" + ("" if not bad else "  " + ", ".join(bad[:15])))


if __name__ == "__main__":
    main()
