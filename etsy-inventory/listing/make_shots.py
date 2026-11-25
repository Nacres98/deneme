"""Render real, cropped screenshots of the SAMPLE workbook for the Etsy listing images.

Each sheet's print area is set to one region of interest (fit to one page), the workbook is exported to PDF by
LibreOffice, every page is rasterised and trimmed. Only partial regions are captured on purpose: enough to show
value, not enough to rebuild the product from the images (no formulas, no full sheets).

Usage: python3 listing/make_shots.py  ->  listing/shots/*.png
"""
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image, ImageChops

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "output" / "NexaGlobe_Inventory_Tracker_SAMPLE_DATA.xlsx"
OUT = ROOT / "listing" / "shots"
OUT.mkdir(parents=True, exist_ok=True)
SHEETS = ["Start Here", "Dashboard", "Sales", "Order Import", "Products", "Performance", "Pricing Calculator",
          "Materials", "Recipes", "Stock Log", "Suppliers", "Expenses", "Mileage", "Reports"]


def find_row(ws, text, col="B"):
    for r in range(1, 200):
        v = ws[f"{col}{r}"].value
        if isinstance(v, str) and text in v:
            return r
    raise KeyError(text)


def render(name, regions, edits=None, dpi=220):
    """regions: {sheet: range}. Sheets not listed print a tiny dummy area (page ignored)."""
    tmp = Path(tempfile.mkdtemp())
    wb = load_workbook(SRC)
    for (sh, ref), v in (edits or {}).items():
        wb[sh][ref] = v
    for sh in SHEETS:
        ws = wb[sh]
        if "_xlnm.Print_Area" in ws.defined_names:
            del ws.defined_names["_xlnm.Print_Area"]
        ws.print_area = regions.get(sh, "A1:A1")
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_title_rows = None
        ws.oddFooter.center.text = ""
        ws.page_margins.left = ws.page_margins.right = ws.page_margins.top = ws.page_margins.bottom = 0.2
    x = tmp / f"{name}.xlsx"
    wb.save(x)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(x)],
                   capture_output=True, timeout=600)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(tmp / f"{name}.pdf"), str(tmp / "p")], capture_output=True)
    pages = sorted(tmp.glob("p-*.png"))
    listed = [sh for sh in SHEETS if sh in regions]
    if len(pages) == len(SHEETS):
        order = SHEETS
    else:
        assert len(pages) == len(listed), (name, len(pages))
        order = listed
    for sh, page in zip(order, pages):
        if sh not in regions:
            continue
        im = Image.open(page).convert("RGB")
        bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        im.crop(bbox).save(OUT / f"{name}__{sh.replace(' ', '_')}.png")
        print("  ", name, sh, im.crop(bbox).size)


wb0 = load_workbook(SRC)
st = wb0["Start Here"]
r_legend = find_row(st, "COLOR LEGEND")
r_types = find_row(st, "WORKS FOR ANY KIND")
r_routine = find_row(st, "10-MINUTE ROUTINE")

# 1. one region per tab (USD, Oct)
render("main", {
    "Start Here": f"B{r_types}:I{r_routine - 2}",
    "Dashboard": "B2:P49",
    "Sales": "A5:Y24",
    "Order Import": "AL19:AY27",
    "Products": "A5:AA22",
    "Performance": "A5:N22",
    "Pricing Calculator": "B2:K26",
    "Materials": "A5:X25",
    "Recipes": "A5:K12",
    "Stock Log": "A5:N18",
    "Suppliers": "A5:L10",
    "Expenses": "A5:K18",
    "Mileage": "A5:J16",
    "Reports": "B2:O27",
})
# 2. second regions
render("extra", {
    "Start Here": f"B{r_legend}:I{r_legend + 9}",
    "Dashboard": "B67:P88",
    "Products": "A5:B22",
    "Reports": "B62:N83",
    "Order Import": "A2:H18",
})
# 3. KPI cards in other currencies
for code in ("USD", "GBP", "EUR", "TRY"):
    render(f"kpi_{code}", {"Dashboard": "B5:H14"}, edits={("Start Here", "C7"): code})
print("done ->", OUT)
