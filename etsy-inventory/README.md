# NexaGlobe Inventory Tracker (Etsy digital product, usable by any small business)

Excel / Google Sheets template for any small product business (makers, retail, food, B2B, POD, services; any sales channel): finished goods + raw materials (BOM),
demand forecasting & reorder alerts, true per-order platform-fee profit, multi-currency,
monthly P&L, Schedule C / HMRC expense mapping and a Part III COGS worksheet.

| File | Purpose |
|---|---|
| `build_workbook.py` | `sample` → `output/NexaGlobe_Inventory_Tracker_SAMPLE_DATA.xlsx`, `blank` → `output/NexaGlobe_Inventory_Tracker_BLANK.xlsx` (same code path, identical formulas; 14 tabs, theme "Editorial Sage & Warm Sand") |
| `sample_data.py` | Simulated sample brand "Ember & Sage Candle Co." (15 SKUs, 20 materials, ~660 sale lines) |
| `audit_workbook.py` | QA: LibreOffice recalc under 7 scenarios, 28 cross-sheet reconciliation checks, clipping & chart-overlap scan |
| `output/audit_report.txt` | Latest audit result (the "buyer reset" scenario = the BLANK file) |
| `listing/etsy_listing_kit.md` | Titles, tags, description, 10-slide image plan |
| `guide/quick_start_guide.html` + `guide/make_pdf.js` | Source of `output/NexaGlobe_Inventory_Tracker_User_Guide.pdf` (run `node guide/make_pdf.js`) |
| `output/preview_*.png` | LibreOffice renders for a quick look (Excel rendering differs slightly) |

Rebuild:

```bash
cd etsy-inventory
python3 build_workbook.py sample
python3 build_workbook.py blank
python3 audit_workbook.py output/NexaGlobe_Inventory_Tracker_SAMPLE_DATA.xlsx
```

Compatibility rule: only SUMIFS / COUNTIF(S) / SUMPRODUCT / INDEX / MATCH / IFERROR / RANK / CEILING /
EOMONTH / EDATE / FIXED and friends. No XLOOKUP, FILTER, LET, IFS, MAXIFS, AGGREGATE, dynamic arrays or Excel Tables.

## Listing images & video

```bash
python3 listing/make_shots.py      # real cropped screenshots of the SAMPLE workbook (LibreOffice)
python3 listing/make_slides.py     # 10 slide layouts (HTML)
node listing/render_slides.js      # -> listing/images/01..10.png (3000x2250)
python3 listing/make_video.py      # -> listing/video/listing_video.mp4 (13 s, 1600x1200, silent)
```
Upload-ready copies (JPG + MP4) live in `listing/upload/`. Screenshots are partial crops with a faint
"SAMPLE DATA · PREVIEW" watermark; no formulas are ever visible.

## Etsy download package (upload these 3 files)

1. `output/NexaGlobe_Inventory_Tracker_SAMPLE_DATA.xlsx`
2. `output/NexaGlobe_Inventory_Tracker_BLANK.xlsx`
3. `output/NexaGlobe_Inventory_Tracker_User_Guide.pdf`

## Open items

- [ ] **Verify Order Import (Etsy & Shopify presets) against real CSV headers** (the user will provide the file at the end):
      exact column names, and whether "Order Shipping" / "Order Sales Tax" repeat on every line of multi-item orders.
- [ ] Open both files once in real Excel and Google Sheets (QA so far used LibreOffice).
- [x] Market & price research ($39 list, $27.30 launch)
- [x] Listing images (10) + listing video
- [ ] Step-by-step Etsy upload guide
