"""QA for the Wedding Planner workbook.

1. LibreOffice full recalculation under several scenarios -> formula error count must be 0.
2. Cross-sheet reconciliation on the sample file (Budget vs Payment Schedule vs Who's Paying vs Dashboard,
   Guest List vs Seating Chart vs Dashboard, Budget Builder split = 100%).

Usage: python3 audit_workbook.py [output/NexaGlobe_Wedding_Planner_SAMPLE_DATA.xlsx]
"""
import json
import shutil
import subprocess
import sys
import tempfile
import warnings
from datetime import date
from glob import glob
from pathlib import Path

from openpyxl import load_workbook

warnings.filterwarnings("ignore")
RECALC = glob("/root/.claude/skills/synced/*/xlsx/scripts/recalc.py")[0]
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "output/NexaGlobe_Wedding_Planner_SAMPLE_DATA.xlsx")
TMP = Path(tempfile.mkdtemp(prefix="wed_audit_"))


def scenario(label, edits=None):
    p = TMP / (label.replace(" ", "_").replace("/", "_") + ".xlsx")
    shutil.copy(SRC, p)
    if edits:
        wb = load_workbook(p)
        for (sh, ref), v in edits.items():
            wb[sh][ref] = v
        wb.save(p)
    out = subprocess.run([sys.executable, RECALC, str(p), "180"], capture_output=True, text=True).stdout
    return label, json.loads(out), p


S = "Start Here"
runs = [scenario("Baseline"),
        scenario("Currency EUR", {(S, "C12"): "EUR"}),
        scenario("No wedding date", {(S, "C8"): None}),
        scenario("Report date blank (today)", {(S, "C13"): None}),
        scenario("Budget 0, guests 0", {(S, "C10"): None, (S, "C11"): None}),
        scenario("Wedding in the past", {(S, "C8"): date(2025, 5, 1)}),
        scenario("No partner names", {(S, "C6"): None, (S, "C7"): None})]
print("=" * 70 + "\nA. FORMULA ERRORS (LibreOffice recalculation)\n" + "=" * 70)
ok = True
for label, res, _ in runs:
    print(f"  {label:<30} formulas={res.get('total_formulas')}  errors={res.get('total_errors')}")
    ok &= res.get("total_errors") == 0

wb = load_workbook(runs[0][2], data_only=True)
B, P, WP, D, G, SE, BB = (wb[n] for n in ("Budget", "Payment Schedule", "Who's Paying", "Dashboard", "Guest List", "Seating Chart", "Budget Builder"))


def nums(ws, col, r0, r1, cond=None):
    return sum(v for r in range(r0, r1 + 1) if isinstance(v := ws[f"{col}{r}"].value, (int, float)) and (cond is None or cond(r)))


cost = nums(B, "G", 6, 205)
paid_pay = nums(P, "G", 6, 305, lambda r: P[f"I{r}"].value == "Yes")
sched = nums(P, "G", 6, 305)
checks = [
    ("Budget paid = Payment Schedule paid", nums(B, "I", 6, 205), paid_pay),
    ("Budget scheduled = Payment Schedule total", nums(B, "H", 6, 205), sched),
    ("Who's Paying paid total = paid", WP["D13"].value, paid_pay),
    ("Who's Paying scheduled+paid = schedule total", WP["D13"].value + WP["E13"].value, sched),
    ("Budget Builder planned = Budget cost", BB["F25"].value, cost),
    ("Budget Builder split = 100%", round(BB["C25"].value, 6), 1),
    ("Dashboard committed tile", D["F6"].value, f"${cost:,.0f}"),
    ("Dashboard paid tile", D["I6"].value, f"${paid_pay:,.0f}"),
    ("Seating confirmed = attending (all seated in sample)", nums(SE, "E", 7, 46), nums(G, "P", 6, 405)),
    ("Seating assigned = party size of seated non-declined",
     nums(SE, "D", 7, 46), nums(G, "G", 6, 405, lambda r: G[f"T{r}"].value and G[f"O{r}"].value != "Declined")),
    ("Dashboard meals = attending", sum(D[f"P{r}"].value for r in range(45, 53)), nums(G, "P", 6, 405)),
]
print("\n" + "=" * 70 + "\nB. RECONCILIATION (sample data)\n" + "=" * 70)
for label, a, b in checks:
    good = (abs(a - b) < 0.01) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else a == b
    ok &= good
    print(f"  {'OK ' if good else 'FAIL'} {label:<52} {a!s:>10} | {b!s}")
names = [SE.cell(r, c).value for r in range(7, 47) for c in range(8, 20) if SE.cell(r, c).value]
print(f"  {'OK ' if len(names) == len(set(names)) else 'FAIL'} No guest appears twice on Seating Chart ({len(names)} invitations listed)")
ok &= len(names) == len(set(names))
print("\nRESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
