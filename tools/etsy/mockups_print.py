"""Listing images for printable PDF products (2700x2025).

    python3 -m tools.etsy.mockups_print [slug ...]
01_cover.png: title + 3 fanned pages; 02_inside.png: every page as a thumbnail grid.
"""
from __future__ import annotations

import base64
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .pdf_kit import ROOT
from .printables import OUT, PRINTABLES

FONT_URL = (ROOT / "assets" / "fonts" / "Montserrat-SemiBold.ttf").as_uri()

COPY = {
    "printable-budget-binder-2027": ("2027 Budget Binder", "Printable money planner · US Letter + A4",
                                     ["10 pages", "Bill tracker", "Savings & debt trackers", "Sinking funds"]),
    "printable-planner-2027": ("2027 Printable Planner", "Monthly calendar + weekly & daily pages · Letter + A4",
                               ["12 monthly calendars", "Year at a glance", "Goals page", "Sunday start"]),
    "printable-meal-planner": ("Meal Planner Printable", "Weekly menu · grocery list · recipe cards · Letter + A4",
                               ["Weekly meal plan", "Grocery list by aisle", "Recipe page", "Pantry inventory"]),
    "printable-cleaning-schedule": ("Cleaning Schedule", "Printable cleaning checklist · Letter + A4",
                                    ["Daily & weekly", "Monthly tasks", "Deep clean by room", "Pre-filled tasks"]),
    "printable-habit-mood-tracker": ("Habit & Mood Tracker", "Undated printable · Letter + A4",
                                     ["31-day habit grid", "Year in pixels", "Mood & sleep log", "Reflection page"]),
}
FEATURE_PAGES = {  # 0-based page indexes shown next to the cover
    "printable-budget-binder-2027": [2, 5],
    "printable-planner-2027": [3, 15],
    "printable-meal-planner": [1, 2],
    "printable-cleaning-schedule": [2, 4],
    "printable-habit-mood-tracker": [1, 2],
}


def b64(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def page_pngs(pdf: Path, tmp: Path, dpi: int) -> list[Path]:
    stem = tmp / f"{pdf.stem}_{dpi}"
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(stem)], check=True, capture_output=True)
    return sorted(tmp.glob(f"{stem.name}-*.png"))


STYLE = """@font-face{{font-family:M;src:url('{font}')}}
*{{box-sizing:border-box;margin:0}}
body{{width:2700px;height:2025px;font-family:M,sans-serif;background:{bg};color:#fff;overflow:hidden;
 padding:110px 130px;display:flex;flex-direction:column}}
h1{{font-size:140px;letter-spacing:-2px;line-height:1}} p.sub{{font-size:52px;opacity:.9;margin-top:22px}}
ul{{list-style:none;display:flex;gap:24px;margin-top:40px;padding:0;flex-wrap:wrap}}
li{{background:rgba(255,255,255,.2);border-radius:60px;padding:16px 38px;font-size:42px}}
.pg{{background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.3);border-radius:6px}}
"""


def cover_html(title, sub, bullets, bg, pages):
    a, b, c = (b64(p) for p in pages)
    li = "".join(f"<li>{x}</li>" for x in bullets)
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{STYLE.format(font=FONT_URL, bg=bg)}
.stage{{position:relative;flex:1;margin-top:60px}}
.stage img{{position:absolute;height:1150px;top:20px}}
</style></head><body><h1>{title}</h1><p class=sub>{sub}</p><ul>{li}</ul>
<div class=stage>
<img class=pg src="{b}" style="left:180px;transform:rotate(-6deg);top:70px">
<img class=pg src="{c}" style="right:180px;transform:rotate(6deg);top:70px">
<img class=pg src="{a}" style="left:50%;transform:translateX(-50%);z-index:2">
</div></body></html>"""


def inside_html(title, bg, pages):
    n = len(pages)
    cols = 6 if n > 10 else (5 if n > 6 else n)
    imgs = "".join(f'<img class=pg src="{b64(p)}">' for p in pages)
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{STYLE.format(font=FONT_URL, bg=bg)}
h1{{font-size:96px}} .grid{{flex:1;display:grid;grid-template-columns:repeat({cols},1fr);gap:34px;margin-top:60px;
 align-content:center}} .grid img{{width:100%}}
</style></head><body><h1>What's inside · {n} pages</h1><p class=sub>{title}</p>
<div class=grid>{imgs}</div></body></html>"""


def main(only=()):
    tmp = Path(tempfile.mkdtemp())
    jobs = []
    for slug, p in PRINTABLES.items():
        if only and slug not in only:
            continue
        pdf = OUT / slug / f"{p['file']}_Letter.pdf"
        title, sub, bullets = COPY[slug]
        bg = p["theme"].accent
        big = page_pngs(pdf, tmp, 110)
        small = page_pngs(pdf, tmp, 45)
        img_dir = OUT / slug / "images"
        img_dir.mkdir(exist_ok=True)
        i1, i2 = FEATURE_PAGES[slug]
        h1 = tmp / f"{slug}_1.html"
        h1.write_text(cover_html(title, sub, bullets, bg, [big[0], big[i1], big[i2]]))
        h2 = tmp / f"{slug}_2.html"
        h2.write_text(inside_html(title, bg, small[:18]))
        jobs += [str(h1), str(img_dir / "01_cover.png"), str(h2), str(img_dir / "02_inside.png")]
    subprocess.run(["node", str(Path(__file__).with_name("screenshot.js")), *jobs], check=True, timeout=600)
    for out in jobs[1::2]:
        print("wrote", Path(out).relative_to(ROOT))
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main(sys.argv[1:])
