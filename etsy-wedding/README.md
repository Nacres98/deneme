# NexaGlobe Wedding Planner Spreadsheet (Etsy digital product)

Plan: `PRODUCT_SPEC.md` (market research, tab structure, pricing notes).

| File | Purpose |
|---|---|
| `build_workbook.py` | `sample` → `output/NexaGlobe_Wedding_Planner_SAMPLE_DATA.xlsx`, `blank` → `output/NexaGlobe_Wedding_Planner_BLANK.xlsx` (same code path, identical formulas) |
| `sample_data.py` | Fictional couple "Maya & Jordan" (wedding Jun 5 2027, report date pinned to Apr 24 2027) |
| `audit_workbook.py` | LibreOffice recalculation under 7 scenarios + cross-sheet reconciliation |

```bash
cd etsy-wedding
python3 build_workbook.py sample
python3 build_workbook.py blank
python3 audit_workbook.py
```

Tabs (14): Start Here · Dashboard · Budget Builder · Budget · Payment Schedule · Who's Paying · Venue Comparison · Vendors ·
Guest List · Seating Chart · Wedding Party · Checklist · Tips & Envelopes · Day-Of Timeline (+ hidden Lists).

Compatibility rule: Excel 2016+ and Google Sheets. Only SUMIFS / COUNTIFS / SUMPRODUCT / INDEX / MATCH / SMALL /
IFERROR / EDATE / TEXT. No XLOOKUP, FILTER, LET, IFS, MAXIFS, TEXTJOIN, dynamic arrays or Excel Tables.

## Listing images, video & guide

```bash
python3 listing/make_shots.py      # cropped screenshots of the SAMPLE workbook (LibreOffice)
python3 listing/make_slides.py     # 10 slide layouts (HTML)
NODE_PATH=$(npm root -g) node listing/render_slides.js   # -> listing/images/01..10.png (3000x2250)
python3 listing/make_video.py      # -> listing/upload/listing_video.mp4
NODE_PATH=$(npm root -g) node guide/make_pdf.js          # -> output/NexaGlobe_Wedding_Planner_User_Guide.pdf
```
Upload-ready JPGs + video: `listing/upload/`. Titles, tags, description, price: `listing/etsy_listing_kit.md`.

## Etsy download package (3 files)
1. `output/NexaGlobe_Wedding_Planner_BLANK.xlsx`
2. `output/NexaGlobe_Wedding_Planner_SAMPLE_DATA.xlsx`
3. `output/NexaGlobe_Wedding_Planner_User_Guide.pdf`
