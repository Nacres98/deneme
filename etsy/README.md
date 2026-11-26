# Etsy digital products

Original spreadsheet templates (Excel + Google Sheets) sold as instant downloads.
Research behind the product and price choices: `research/2026-11_competitor_study.md`.

## Build
```
python3 -m tools.etsy.build --check   # xlsx + How_To_Use.pdf per product, LibreOffice formula check
python3 -m tools.etsy.mockups         # 2700x2025 listing images from demo-filled copies
python3 -m tools.etsy.printables      # printable PDFs (Letter + A4)
python3 -m tools.etsy.mockups_print   # listing images for printables
python3 -m tools.etsy.catalog         # regenerate CATALOG.md (full product list)
```
Full product list and group roadmap: `CATALOG.md` (source: `tools/etsy/catalog.py`).
Sources: `tools/etsy/`: spreadsheets (`life_organizer.py`, `budget_planner.py`, `habit_tracker.py`, `xlsx_kit.py`),
printables (`printables.py`, `pdf_kit.py`). Shop name for PDF footers: `config/etsy.json` → `shop_name`.

## Products
See `CATALOG.md`.

Each folder holds the buyer files, `images/` and `listing.md` (title, 13 tags, description).

## Rules
- Original work only: other shops are market references, never copied. No brand logos (icon packs) or resold PLR.
- Sales are time-limited campaigns, not a permanent fake "original price".
- Log daily stats in `scoreboard.csv`.
