# Maker's Inventory & Profit System (Etsy digital product)

Excel / Google Sheets template for handmade sellers: finished goods + raw materials (BOM),
demand forecasting & reorder alerts, true per-order platform-fee profit, multi-currency,
monthly P&L, Schedule C / HMRC expense mapping and a Part III COGS worksheet.

| File | Purpose |
|---|---|
| `build_workbook.py` | Builds `output/Makers_Inventory_Profit_System.xlsx` (9 tabs, theme "Editorial Sage & Warm Sand") |
| `sample_data.py` | Simulated sample brand "Ember & Sage Candle Co." (15 SKUs, 20 materials, ~660 sale lines) |
| `audit_workbook.py` | Phase-3 QA: LibreOffice recalc under 7 scenarios, cross-sheet reconciliation, clipping & chart-overlap scan |
| `output/audit_report.txt` | Latest audit result |
| `output/preview_*.png` | LibreOffice renders for a quick look (Excel rendering differs slightly) |

Rebuild:

```bash
cd etsy-inventory
python3 build_workbook.py
python3 audit_workbook.py output/Makers_Inventory_Profit_System.xlsx
```

Compatibility rule: only SUMIFS / COUNTIF(S) / SUMPRODUCT / INDEX / MATCH / IFERROR / RANK / CEILING /
EOMONTH / EDATE / FIXED and friends. No XLOOKUP, FILTER, LET, IFS, MAXIFS, AGGREGATE, dynamic arrays or Excel Tables.
