"""Phase 3 quality audit for the generated workbook.

1. Recalculates the workbook in LibreOffice under several scenarios and counts formula errors.
2. Reconciles cross-sheet totals (Sales vs Reports vs Dashboard, Expenses vs Reports, stock balances).
3. Scans for clipped text / '###' risk and overlapping charts.

Usage: python3 audit_workbook.py output/Makers_Inventory_Profit_System.xlsx
"""
import json
import warnings
warnings.filterwarnings("ignore")
import math
import shutil
import subprocess
import sys
import tempfile
from glob import glob
from pathlib import Path

from openpyxl import load_workbook

RECALC = glob("/root/.claude/skills/synced/*/xlsx/scripts/recalc.py")[0]
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "output/Makers_Inventory_Profit_System_SAMPLE_DATA.xlsx")
TMP = Path(tempfile.mkdtemp(prefix="audit_"))


def recalc(path):
    out = subprocess.run([sys.executable, RECALC, str(path), "300"], capture_output=True, text=True).stdout
    return json.loads(out)


def scenario(label, edits=None, clear=None):
    p = TMP / f"{label.replace(' ', '_')}.xlsx"
    shutil.copy(SRC, p)
    if edits or clear:
        wb = load_workbook(p)
        for (sh, ref), v in (edits or {}).items():
            wb[sh][ref] = v
        for sh, rng in clear or []:
            for row in wb[sh][rng]:
                for c in row:
                    c.value = None
        wb.save(p)
    res = recalc(p)
    return label, res, p


results = []
base = scenario("Baseline (sample data, USD, Oct)")
results.append(base)
results.append(scenario("Currency = GBP", {("Start Here", "C7"): "GBP"}))
results.append(scenario("Currency = EUR + Full Year", {("Start Here", "C7"): "EUR", ("Dashboard", "N3"): "Full Year"}))
results.append(scenario("Deduct on Sold (make-to-order)", {("Start Here", "C13"): "Sold"}))
results.append(scenario("Report Date blank (=TODAY)", {("Start Here", "C11"): None}))
results.append(scenario("Labor rate 0, empty Dec period", {("Start Here", "C17"): 0, ("Dashboard", "N3"): "Dec"}))
results.append(scenario("All sample data cleared (buyer reset)", clear=[
    ("Sales", "A6:M1505"), ("Stock Log", "A6:L1005"), ("Expenses", "A6:H1005"), ("Recipes", "A6:D505"),
    ("Products", "A6:H105"), ("Materials", "A6:J155"), ("Mileage", "A6:H1005"), ("Suppliers", "A6:H105"),
    ("Etsy Import", "A22:AJ521"), ("Etsy Import", "BA22:BB121"), ("Pricing Calculator", "C6:C14"),
    ("Pricing Calculator", "B18:B29"), ("Pricing Calculator", "D18:E29")]))

print("=" * 78)
print("A. FORMULA ERROR SCAN (LibreOffice full recalculation)")
print("=" * 78)
for label, res, _ in results:
    print(f"  {label:<42} formulas={res.get('total_formulas')!s:>6}  errors={res.get('total_errors')}  "
          f"{'' if res.get('status') == 'success' else res}")

# ------------------------------------------------------------------ reconciliation on baseline
wb = load_workbook(base[2], data_only=True)
S, R, D, P, M, E, L = (wb[n] for n in ("Sales", "Reports", "Dashboard", "Products", "Materials", "Expenses", "Stock Log"))


def col_sum(ws, col, r0, r1, cond=None):
    t = 0
    for r in range(r0, r1 + 1):
        v = ws[f"{col}{r}"].value
        if isinstance(v, (int, float)) and (cond is None or cond(r)):
            t += v
    return t


checks = []


def check(name, a, b, tol=0.01):
    checks.append((name, a, b, abs((a or 0) - (b or 0)) <= tol))


fy_rows = lambda ws: (lambda r: (d := ws[f"A{r}"].value) is not None and d.year == 2026)
check("Sales Net Revenue (FY) = Reports P&L Net Revenue", col_sum(S, "P", 6, 1505, fy_rows(S)), R["O10"].value)
check("Sales Net Profit − Opex = Reports NET PROFIT",
      col_sum(S, "X", 6, 1505, fy_rows(S)) - col_sum(E, "E", 6, 1005, fy_rows(E)), R["O23"].value)
check("Sales Total Fees = Reports fee rows", col_sum(S, "V", 6, 1505, fy_rows(S)), sum(R[f"O{r}"].value for r in range(12, 17)))
check("Expenses total = Reports category total", col_sum(E, "E", 6, 1005, fy_rows(E)), R["O58"].value)
check("Expenses deductible = Reports deductible", col_sum(E, "I", 6, 1005, fy_rows(E)), R["R58"].value)
check("Dashboard Oct revenue = Reports Oct column", D["T9"].value, R["L10"].value)
check("Dashboard Sep (prior) revenue = Reports Sep column", D["U9"].value, R["K10"].value)
check("Dashboard Oct net profit = Reports Oct NET PROFIT", D["T10"].value, R["L23"].value)
check("Channel chart total = Dashboard revenue", sum(D[f"T{r}"].value for r in range(35, 41)), D["T9"].value)
check("Revenue split (COGS+fees+labels+opex+profit) = revenue",
      sum(D[f"{c}57"].value for c in "TUVWX"), D["T9"].value, 0.05)
sold = col_sum(S, "E", 6, 1505, lambda r: S[f"L{r}"].value not in (None, "Cancelled"))
check("Units sold (Sales) = Σ Products Sold", sold, col_sum(P, "J", 6, 105))
prod_bal = sum((P[f"E{r}"].value or 0) + P[f"I{r}"].value - P[f"J{r}"].value + P[f"K{r}"].value - P[f"L{r}"].value
               for r in range(6, 21))
check("Products: opening + produced − sold ± adj − on hand = 0", prod_bal, 0)
mat_bal = sum((M[f"F{r}"].value or 0) + M[f"K{r}"].value - M[f"M{r}"].value + M[f"N{r}"].value - M[f"O{r}"].value
              for r in range(6, 26))
check("Materials: opening + received − used ± adj − on hand = 0", mat_bal, 0)
neg = [P[f"A{r}"].value for r in range(6, 21) if P[f"L{r}"].value < 0] + \
      [M[f"A{r}"].value for r in range(6, 26) if M[f"O{r}"].value < -0.001]
check("No negative stock in sample data (count)", len(neg), 0)
check("Part III: line 40 − 41 = 42", R["D81"].value - R["D82"].value, R["D83"].value)
check("Uncategorised expense check line = 0", R["C60"].value, 0)
PF, MI, PC, IM, SU = (wb[n] for n in ("Performance", "Mileage", "Pricing Calculator", "Etsy Import", "Suppliers"))
check("Performance Σ net profit = Sales FY net profit", col_sum(PF, "E", 6, 105), col_sum(S, "X", 6, 1505, fy_rows(S)))
check("Performance Σ units = Reports units sold", col_sum(PF, "C", 6, 105), R["O26"].value)
check("Performance profit shares sum to 100%", col_sum(PF, "G", 6, 105), 1.0, 0.0001)
check("Mileage deduction: Mileage tab = Reports", col_sum(MI, "J", 6, 1005, fy_rows(MI)), R["D69"].value)
check("Mileage deduction = distance × rate", col_sum(MI, "I", 6, 1005) * wb["Start Here"]["C21"].value, col_sum(MI, "J", 6, 1005))
check("Dashboard customers = distinct customers in Sales",
      D["T75"].value, len({S[f"M{r}"].value for r in range(6, 1506) if S[f"A{r}"].value and S[f"M{r}"].value}))
check("Pricing: unrounded suggested price hits target margin exactly",
      ((PC["I13"].value + PC["C10"].value) * (1 - PC["I9"].value) - PC["I10"].value - PC["I8"].value - PC["C9"].value)
      / (PC["I13"].value + PC["C10"].value), PC["I11"].value, 0.0001)
check("Pricing: .99-rounded price margin ≥ target (shortfall)", max(0, PC["I11"].value - PC["K20"].value), 0)
check("Pricing: break-even price → profit 0",
      (PC["I12"].value + PC["C10"].value) * (1 - PC["I9"].value) - PC["I10"].value - PC["I8"].value - PC["C9"].value, 0, 0.001)
check("Etsy Import: 4 READY / 1 duplicate in sample", sum(1 for r in range(22, 522) if IM[f"AY{r}"].value == "READY") * 10
      + sum(1 for r in range(22, 522) if IM[f"AY{r}"].value == "ALREADY IN SALES"), 41)
check("Etsy Import: shipping counted once per order", sum((IM[f"AS{r}"].value or 0) for r in range(22, 28) if IM[f"AM{r}"].value == "3290114501"), 6.95)
check("Suppliers Σ purchases = Part III purchases (line 36)", col_sum(SU, "J", 6, 105), R["D77"].value)

print()
print("=" * 78)
print("B. CROSS-SHEET RECONCILIATION (baseline)")
print("=" * 78)
for name, a, b, ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}  {name:<58} {a:>12,.2f} | {b:>12,.2f}")

# ------------------------------------------------------------------ layout scan
print()
print("=" * 78)
print("C. LAYOUT SCAN (clipping / ### risk / chart overlap)")
print("=" * 78)
wbf = load_workbook(SRC)  # formats & merges


def shown(v, fmt):
    if v is None or v == "":
        return ""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if "%" in fmt:
            return f"{v * 100:,.1f}%"
        if fmt == "mmm":
            return "Jan"
        if "yy" in fmt:
            return "Nov 20, 2026"
        if "∞" in fmt:
            return "∞" if v >= 9999 else f"{v:,.0f}"
        if "0000" in fmt:
            return f"$ {v:,.4f}"
        dec = 2 if ".00" in fmt else (1 if ".##" in fmt and v != int(v) else 0)
        return (f"AU$ {v:,.{dec}f}" if ".00" in fmt else f"{v:,.{dec}f}") if "#,##0" in fmt else f"{v}"
    if hasattr(v, "year"):
        return "Jan" if fmt == "mmm" else ("Nov 20, 2026" if "yy" in fmt else "Nov 20")
    return str(v)


issues = []
for ws in wbf.worksheets:
    vws = wb[ws.title]
    skip_cols = set(range(1, 37)) if ws.title == "Etsy Import" else set()  # raw CSV paste zone
    merged = {}
    for mr in ws.merged_cells.ranges:
        width = sum((ws.column_dimensions[chr(64 + c)].width if c <= 26 else 10) or 8.43
                    for c in range(mr.min_col, mr.max_col + 1))
        for r in range(mr.min_row, mr.max_row + 1):
            for c in range(mr.min_col, mr.max_col + 1):
                merged[(r, c)] = (width if (r, c) == (mr.min_row, mr.min_col) else None)
    for row in vws.iter_rows(min_row=1, max_row=min(vws.max_row, 120)):
        for c in row:
            if c.column in skip_cols and c.row >= 21:
                continue
            fc = ws.cell(c.row, c.column)
            txt = shown(c.value, fc.number_format)
            if not txt or (fc.alignment and (fc.alignment.wrap_text or fc.alignment.shrink_to_fit)):
                continue
            if (c.row, c.column) in merged:
                avail = merged[(c.row, c.column)]
                if avail is None:
                    continue
            else:
                avail = ws.column_dimensions[c.column_letter].width or 8.43
            if ws.column_dimensions[c.column_letter].hidden:
                continue
            size = (fc.font.sz or 10) if fc.font else 10
            need = len(txt) * size / 10 * (1.1 if (fc.font and fc.font.b) else 1.0)
            numeric = isinstance(c.value, (int, float)) or hasattr(c.value, "year")
            # text spilling into an EMPTY neighbour is fine; numbers never spill (they show ###)
            nxt = vws.cell(c.row, c.column + 1).value
            if need > avail + 0.5 and (numeric or (nxt not in (None, "") and c.row != 5)):
                issues.append(f"{ws.title}!{c.coordinate}: '{txt[:40]}' needs ~{need:.0f} chars, has {avail:.0f}")
for i in issues[:40]:
    print("  WARN", i)
print(f"  {len(issues)} potential clipping issue(s) found")

# chart overlap on Dashboard
from openpyxl.utils import column_index_from_string as ci
dws = wbf["Dashboard"]


def col_px(col_idx):
    w = dws.column_dimensions[chr(64 + col_idx)].width or 8.43
    return int(w * 7 + 5)


boxes = []
for ch in dws._charts:
    a = ch.anchor._from
    x0 = sum(col_px(c) for c in range(1, a.col + 1))
    y0 = sum((dws.row_dimensions[r].height or 15) * 4 / 3 for r in range(1, a.row + 1))
    ext = ch.anchor.ext  # one-cell anchor: size in EMU
    boxes.append((x0, y0, x0 + ext.width / 9525, y0 + ext.height / 9525, f"{chr(65 + a.col)}{a.row + 1}"))
overlaps = []
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        a, b = boxes[i], boxes[j]
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            overlaps.append((a[4], b[4]))
for b in boxes:
    print(f"  chart @ {b[4]:<4} x {b[0]:.0f}-{b[2]:.0f}px  y {b[1]:.0f}-{b[3]:.0f}px")
print(f"  chart overlaps: {overlaps or 'none'}")
right_edge_J = sum(col_px(c) for c in range(1, ci('Q')))
print(f"  right chart edge {max(b[2] for b in boxes):.0f}px vs card-grid edge {right_edge_J}px")
