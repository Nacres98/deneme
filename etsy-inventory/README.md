# Maker's Inventory & Profit System (Etsy digital product)

Excel / Google Sheets template for handmade sellers: finished goods + raw materials (BOM),
demand forecasting & reorder alerts, true per-order platform-fee profit, multi-currency,
monthly P&L, Schedule C / HMRC expense mapping and a Part III COGS worksheet.

| File | Purpose |
|---|---|
| `build_workbook.py` | `sample` → `output/Makers_Inventory_Profit_System_SAMPLE_DATA.xlsx`, `blank` → `output/Makers_Inventory_Profit_System_BLANK.xlsx` (same code path, identical formulas; 14 tabs, theme "Editorial Sage & Warm Sand") |
| `sample_data.py` | Simulated sample brand "Ember & Sage Candle Co." (15 SKUs, 20 materials, ~660 sale lines) |
| `audit_workbook.py` | QA: LibreOffice recalc under 7 scenarios, 28 cross-sheet reconciliation checks, clipping & chart-overlap scan |
| `output/audit_report.txt` | Latest audit result (the "buyer reset" scenario = the BLANK file) |
| `listing/etsy_listing_kit.md` | Titles, tags, description, 10-slide image plan |
| `guide/quick_start_guide.html` + `guide/make_pdf.js` | Source of `output/Quick_Start_Guide.pdf` (run `node guide/make_pdf.js`) |
| `output/preview_*.png` | LibreOffice renders for a quick look (Excel rendering differs slightly) |

Rebuild:

```bash
cd etsy-inventory
python3 build_workbook.py sample
python3 build_workbook.py blank
python3 audit_workbook.py output/Makers_Inventory_Profit_System_SAMPLE_DATA.xlsx
```

Compatibility rule: only SUMIFS / COUNTIF(S) / SUMPRODUCT / INDEX / MATCH / IFERROR / RANK / CEILING /
EOMONTH / EDATE / FIXED and friends. No XLOOKUP, FILTER, LET, IFS, MAXIFS, AGGREGATE, dynamic arrays or Excel Tables.

## Etsy download package (upload these 3 files)

1. `output/Makers_Inventory_Profit_System_SAMPLE_DATA.xlsx`
2. `output/Makers_Inventory_Profit_System_BLANK.xlsx`
3. `output/Quick_Start_Guide.pdf`

## Open items

- [ ] **Verify Etsy Import against a real Etsy "Order Items" CSV header** (the user will provide the file at the end):
      exact column names, and whether "Order Shipping" / "Order Sales Tax" repeat on every line of multi-item orders.
- [ ] Open both files once in real Excel and Google Sheets (QA so far used LibreOffice).
- [ ] Market & price research → listing images (copy-safe crops) → short listing video → upload guide.
