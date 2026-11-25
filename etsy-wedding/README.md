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

Tabs: Start Here · Dashboard · Budget Builder · Budget · Payment Schedule · Who's Paying · Vendors · Guest List ·
Seating Chart · Checklist · Tips & Envelopes · Day-Of Timeline (+ hidden Lists).

Compatibility rule: Excel 2016+ and Google Sheets. Only SUMIFS / COUNTIFS / SUMPRODUCT / INDEX / MATCH / SMALL /
IFERROR / EDATE / TEXT. No XLOOKUP, FILTER, LET, IFS, MAXIFS, TEXTJOIN, dynamic arrays or Excel Tables.
