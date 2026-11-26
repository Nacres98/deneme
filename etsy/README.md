# Etsy digital products

Original spreadsheet templates (Excel + Google Sheets) sold as instant downloads.
Research behind the product and price choices: `research/2026-11_competitor_study.md`.

## Build
```
python3 -m tools.etsy.build --check   # xlsx + How_To_Use.pdf per product, LibreOffice formula check
python3 -m tools.etsy.mockups         # 2700x2025 listing images from demo-filled copies
```
Sources: `tools/etsy/` (`life_organizer.py`, `budget_planner.py`, `habit_tracker.py`, shared `xlsx_kit.py`).

## Products
| slug | price (list → launch sale) |
|---|---|
| `life-organizer` | $12.99 → $5.19 |
| `budget-planner-2027` | $9.99 → $4.99 |
| `habit-tracker-2027` | $5.99 → $2.99 |
| `bundle-2027` | $19.99 → $7.99 |

Each folder holds the buyer files, `images/` and `listing.md` (title, 13 tags, description).

## Rules
- Original work only: other shops are market references, never copied. No brand logos (icon packs) or resold PLR.
- Sales are time-limited campaigns, not a permanent fake "original price".
- Log daily stats in `scoreboard.csv`.
