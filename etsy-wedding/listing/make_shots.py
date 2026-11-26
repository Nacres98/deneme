"""Real, cropped screenshots of the SAMPLE workbook for the Etsy listing images (LibreOffice render).

Each sheet's print area is set to one region (fit to one page), exported to PDF, rasterised and trimmed.
Only partial regions are captured: enough to show value, not enough to rebuild the product.
Usage: python3 listing/make_shots.py  ->  listing/shots/<pass>__<Sheet>.png
"""
import subprocess
import tempfile
import warnings
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image, ImageChops

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "output" / "NexaGlobe_Wedding_Planner_SAMPLE_DATA.xlsx"
OUT = ROOT / "listing" / "shots"
OUT.mkdir(parents=True, exist_ok=True)


def render(tag, regions, dpi=220, hide_rows=None):
    tmp = Path(tempfile.mkdtemp())
    wb = load_workbook(SRC)
    for ws in wb.worksheets:
        if ws.title not in regions:
            ws.sheet_state = "hidden"
            continue
        ws.sheet_state = "visible"
        for r in (hide_rows or {}).get(ws.title, ()):
            ws.row_dimensions[r].hidden = True
        ws.print_area = regions[ws.title]
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = ws.page_setup.fitToHeight = 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        for m in ("left", "right", "top", "bottom"):
            setattr(ws.page_margins, m, 0.15)
    wb.active = [ws.title for ws in wb.worksheets].index(next(iter(regions)))
    x = tmp / f"{tag}.xlsx"
    wb.save(x)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(x)], capture_output=True, timeout=600)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(tmp / f"{tag}.pdf"), str(tmp / "p")], capture_output=True)
    pages = sorted(tmp.glob("p-*.png"))
    order = [ws.title for ws in wb.worksheets if ws.title in regions]
    assert len(pages) == len(order), (tag, len(pages), order)
    for sh, page in zip(order, pages):
        im = Image.open(page).convert("RGB")
        bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        im = im.crop(bbox)
        fn = OUT / f"{tag}__{sh.replace(' ', '_').replace('&', 'and').replace(chr(39), '')}.png"
        im.save(fn)
        print("  ", fn.name, im.size)


render("a", {
    "Start Here": "B2:G27",
    "Dashboard": "B2:P18",
    "Budget Builder": "B2:I27",
    "Budget": "B2:L22",
    "Payment Schedule": "B4:M24",
    "Who's Paying": "B2:G38",
    "Vendors": "B2:N13",
    "Guest List": "B2:N22",
    "Seating Chart": "B2:M15",
    "Checklist": "B2:I30",
    "Tips & Envelopes": "B2:N17",
    "Day-Of Timeline": "B2:H21",
    "Venue Comparison": "B2:E38",
    "Wedding Party": "B2:P14",
})
render("b", {"Dashboard": "B21:P40", "Guest List": "M4:S22"})
render("c", {"Dashboard": "B43:P72"})
render("d", {"Payment Schedule": "B2:M42"}, hide_rows={"Payment Schedule": range(6, 25)})
