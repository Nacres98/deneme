"""Build the NexaGlobe Wedding Planner Spreadsheet (.xlsx).

    python3 build_workbook.py sample  -> output/NexaGlobe_Wedding_Planner_SAMPLE_DATA.xlsx
    python3 build_workbook.py blank   -> output/NexaGlobe_Wedding_Planner_BLANK.xlsx

One code path for both files, so formulas are identical.
Compatibility: Excel 2016+ and Google Sheets. Only SUMIFS, COUNTIFS, SUMPRODUCT, INDEX/MATCH, SMALL, IFERROR,
IF/AND/OR, MIN/MAX, DATE, EDATE, TODAY, TEXT. No XLOOKUP/FILTER/LET/IFS/MAXIFS/TEXTJOIN/dynamic arrays/tables.
"""
import sys
from datetime import date, time

from openpyxl import Workbook
from openpyxl.chart import BarChart, DoughnutChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

import sample_data as sd

VARIANT = (sys.argv[1] if len(sys.argv) > 1 else "sample").lower()
assert VARIANT in ("sample", "blank"), "usage: build_workbook.py [sample|blank]"
BLANK = VARIANT == "blank"
OUT = f"output/NexaGlobe_Wedding_Planner_{'BLANK' if BLANK else 'SAMPLE_DATA'}.xlsx"

# ------------------------------------------------------------------ design tokens ("Ivory, Sage & Dusty Rose")
BG, CARD, BLUSH, ROSE, SAGE, DEEP = "FBF8F4", "FFFFFF", "F4E6E2", "C48E86", "8FA48F", "4B3F46"
GOLD, INK, MUTED, LINE, INPUT, INPUT_BD, CALC = "C7A465", "2F2A2C", "8D8487", "EFE6DF", "FFF9EE", "E9D7B4", "5E585A"
SAGE_LT, ROSE_LT, GOLD_LT = "E7EEE6", "F8E9E6", "F7EEDB"
HEAD, BODY = "Georgia", "Calibri"
BADGES = {  # status text -> (fill, font)
    "PAID": ("E2ECE1", "3F6B45"), "PAID IN FULL": ("E2ECE1", "3F6B45"), "DONE": ("E2ECE1", "3F6B45"),
    "PARTLY PAID": ("F7EEDB", "8A6A1F"), "SCHEDULED": ("E6ECF3", "3D5A80"), "UPCOMING": ("E6ECF3", "3D5A80"),
    "LATER": ("F1EFEF", "8D8487"), "DUE SOON": ("FBEBC8", "8A5A00"), "OVERDUE": ("F5D7D1", "A23B2A"),
    "NOT SCHEDULED": ("F1EFEF", "8D8487"), "NO DATE": ("F1EFEF", "8D8487"),
    "OPEN": ("E6ECF3", "3D5A80"), "FULL": ("E2ECE1", "3F6B45"), "OVER CAPACITY": ("F5D7D1", "A23B2A"), "EMPTY": ("F1EFEF", "8D8487"),
    "BOOKED": ("E2ECE1", "3F6B45"), "CHEAPEST": ("E2ECE1", "3F6B45"),
}
CURRENCIES = [("USD", "$"), ("EUR", "€"), ("GBP", "£"), ("CAD", "CA$"), ("AUD", "AU$"), ("NZD", "NZ$"), ("CHF", "CHF "),
              ("MXN", "MX$"), ("INR", "₹"), ("ZAR", "R "), ("SGD", "S$"), ("TRY", "₺")]
CATEGORIES = [("Venue", .18), ("Catering & Bar", .21), ("Photography", .09), ("Videography", .04),
              ("Attire & Alterations", .06), ("Hair & Makeup", .02), ("Flowers & Decor", .08),
              ("Music & Entertainment", .06), ("Cake & Desserts", .02), ("Stationery & Postage", .02),
              ("Ceremony & Officiant", .02), ("Rentals & Lighting", .04), ("Transportation", .02), ("Rings", .04),
              ("Favors & Gifts", .02), ("Planner / Coordinator", .04), ("Tips & Gratuities", .02), ("Contingency", .02)]
NCAT = len(CATEGORIES)
TIMEFRAMES = [("12+ months", 365), ("10-12 months", 300), ("8-10 months", 240), ("6-8 months", 180), ("4-6 months", 120),
              ("2-4 months", 75), ("1-2 months", 45), ("2-4 weeks", 21), ("1-2 weeks", 10), ("Week of", 4),
              ("Day before", 1), ("Wedding day", 0), ("After", -21)]

# data capacities (first row, last row)
B0, B1 = 6, 205    # Budget
Y0, Y1 = 6, 305    # Payment Schedule
V0, V1 = 6, 105    # Vendors
G0, G1 = 6, 405    # Guest List
T0, T1 = 7, 46     # Seating tables
C0, C1 = 6, 155    # Checklist
P0, P1 = 6, 35     # Tips
D0, D1 = 6, 65     # Timeline
SEATS = 12


def fill(c):
    return PatternFill("solid", start_color=c, end_color=c)


def side(c, style="thin"):
    return Side(style=style, color=c)


def font(size=10, bold=False, color=INK, name=BODY, italic=False, underline=None):
    return Font(name=name, size=size, bold=bold, color=color, italic=italic, underline=underline)


BOX_IN = Border(left=side(INPUT_BD), right=side(INPUT_BD), top=side(INPUT_BD), bottom=side(INPUT_BD))
UNDER = Border(bottom=side(LINE))
UNLOCK = Protection(locked=False)
FMT = {"money": '#,##0;-#,##0;"–"', "money2": '#,##0.00;-#,##0.00;"–"', "int": '#,##0;-#,##0;"–"',
       "pct": '0%;-0%;"–"', "pct1": '0.0%;-0.0%;"–"', "date": "mmm d, yyyy", "sdate": "ddd mmm d", "month": "mmm yyyy",
       "time": "h:mm AM/PM", "text": "@", "gen": "General", "days": '#,##0;"-"#,##0;"0"'}

wb = Workbook()
wb.remove(wb.active)
SHEETS = ["Start Here", "Dashboard", "Budget Builder", "Budget", "Payment Schedule", "Who's Paying", "Venue Comparison",
          "Vendors", "Guest List", "Seating Chart", "Wedding Party", "Checklist", "Tips & Envelopes", "Day-Of Timeline", "Lists"]
TABS = [DEEP, ROSE, GOLD, GOLD, GOLD, GOLD, SAGE, SAGE, ROSE, ROSE, ROSE, SAGE, GOLD, SAGE, MUTED]
W = {}
for n, c in zip(SHEETS, TABS):
    ws = wb.create_sheet(n)
    ws.sheet_properties.tabColor = c
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 100
    W[n] = ws
START, DASH, BB, BUD, PAY, WHO, VNU, VEN, GUEST, SEAT, PARTY, CHK, TIP, DAY, LST = (W[n] for n in SHEETS)


def q(n):
    return "'" + n.replace("'", "''") + "'" if any(ch in n for ch in " '&-") else n


def rng(sheet, col, r0, r1):
    return f"{q(sheet)}!${col}${r0}:${col}${r1}"


def name(nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


def page_bg(ws, ncols, nrows):
    """Paint an ivory canvas so the sheet looks designed rather than gridded."""
    for r in range(1, nrows + 1):
        for c in range(1, ncols + 1):
            ws.cell(r, c).fill = fill(BG)


def title(ws, text, sub, width_to="H"):
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 34
    ws.row_dimensions[3].height = 20
    ws.column_dimensions["A"].width = 2.5
    ws["B2"] = text
    ws["B2"].font = font(22, name=HEAD, color=DEEP)
    ws["B2"].alignment = Alignment(vertical="center")
    ws["B3"] = sub
    ws["B3"].font = font(10, italic=True, color=MUTED)


def legend(ws, cell):
    ws[cell] = "■ cream = type here    ■ white = automatic"
    ws[cell].font = font(9, color=MUTED)


def set_input(c, fmt=None, wrap=False, align="left"):
    c.fill = fill(INPUT)
    c.border = BOX_IN
    c.protection = UNLOCK
    c.font = font(10, color=INK)
    c.alignment = Alignment(vertical="center", horizontal=align, wrap_text=wrap)
    if fmt:
        c.number_format = FMT[fmt]


def set_calc(c, fmt=None, bold=False, align="left"):
    c.fill = fill(CARD)
    c.border = UNDER
    c.font = font(10, bold=bold, color=CALC)
    c.alignment = Alignment(vertical="center", horizontal=align)
    if fmt:
        c.number_format = FMT[fmt]


def dv_list(ws, source, ref, allow_other=False):
    dv = DataValidation(type="list", formula1=source, allow_blank=True, showDropDown=False)
    if allow_other:
        dv.showErrorMessage = False
    else:
        dv.error, dv.errorTitle, dv.showErrorMessage = "Please pick a value from the list.", "Pick from list", True
    ws.add_data_validation(dv)
    dv.add(ref)


def dv_num(ws, ref, kind="decimal"):
    dv = DataValidation(type=kind, operator="greaterThanOrEqual", formula1="0", allow_blank=True)
    dv.error, dv.errorTitle, dv.showErrorMessage = "Enter a number (0 or more).", "Number", True
    ws.add_data_validation(dv)
    dv.add(ref)


def dv_date(ws, ref):
    dv = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True)
    dv.error, dv.errorTitle, dv.showErrorMessage = "Enter a date, e.g. 6/5/2027.", "Date", True
    ws.add_data_validation(dv)
    dv.add(ref)


def badges(ws, ref, col_letter, first_row):
    for text, (bg, fg) in BADGES.items():
        ws.conditional_formatting.add(ref, FormulaRule(formula=[f'${col_letter}{first_row}="{text}"'],
                                                        fill=fill(bg), font=Font(color=fg, bold=True)))


def table(ws, cols, r0, r1, rows=(), header_row=5, autofilter=True):
    """cols: list of dict(h, w, kind=input|calc|helper, fmt, f, dv=(source, allow_other), num, date, align, wrap).
    rows: list of lists (values for INPUT columns only, in order)."""
    ws.row_dimensions[header_row].height = 32
    for i, c in enumerate(cols):
        col = CL(i + 2)
        ws.column_dimensions[col].width = c.get("w", 14)
        h = ws.cell(header_row, i + 2, c["h"])
        h.font = font(9.5, bold=True, color="FFFFFF" if c.get("kind") != "helper" else MUTED)
        h.fill = fill(DEEP if c.get("kind", "input") == "input" else (SAGE if c.get("kind") == "calc" else BG))
        h.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        if c.get("kind") == "helper":
            ws.column_dimensions[col].hidden = True
    inputs = [i for i, c in enumerate(cols) if c.get("kind", "input") == "input"]
    for r in range(r0, r1 + 1):
        ws.row_dimensions[r].height = 18
        vals = rows[r - r0] if r - r0 < len(rows) else None
        for i, c in enumerate(cols):
            cell = ws.cell(r, i + 2)
            kind = c.get("kind", "input")
            if kind == "input":
                set_input(cell, c.get("fmt"), c.get("wrap", False), c.get("align", "left"))
                if vals is not None:
                    v = vals[inputs.index(i)]
                    if v is not None and v != "":
                        cell.value = v
            else:
                set_calc(cell, c.get("fmt"), c.get("bold", False), c.get("align", "left"))
                cell.value = c["f"].format(r=r)
                if kind == "helper":
                    cell.font = font(8, color=MUTED)
    for i, c in enumerate(cols):
        col = CL(i + 2)
        ref = f"{col}{r0}:{col}{r1}"
        if c.get("dv"):
            dv_list(ws, c["dv"][0], ref, c["dv"][1])
        if c.get("num"):
            dv_num(ws, ref, c["num"])
        if c.get("date"):
            dv_date(ws, ref)
    ws.freeze_panes = ws.cell(header_row + 1, 3)
    if autofilter:
        ws.auto_filter.ref = f"B{header_row}:{CL(len(cols) + 1)}{r1}"


def cur_h(label):
    return f'="{label} ("&CUR_SYM&")"'


def money_txt(expr):
    """KPI text like $12,340 (works in Excel + Sheets)."""
    return f'CUR_SYM&TEXT({expr},"#,##0")'


# ================================================================== Lists (hidden helper sheet)
LST.sheet_state = "hidden"
LST["A1"], LST["B1"] = "Currency", "Symbol"
for i, (c, s) in enumerate(CURRENCIES, start=2):
    LST.cell(i, 1, c)
    LST.cell(i, 2, s)
LST["D1"], LST["E1"] = "Timeframe", "Days before"
for i, (t, d) in enumerate(TIMEFRAMES, start=2):
    LST.cell(i, 4, t)
    LST.cell(i, 5, d)
simple = {
    "G": ("Yes / No", ["Yes", "No"]),
    "H": ("RSVP", ["Pending", "Attending", "Declined"]),
    "I": ("Meal", ["Chicken", "Beef", "Fish", "Vegetarian", "Vegan", "Kids meal", "No meal"]),
    "K": ("Group", ["Family", "Friends", "Work", "Wedding party", "Plus-one", "Other"]),
    "M": ("Payment type", ["Deposit", "Installment", "Final balance", "Paid in full", "Tip", "Other"]),
    "N": ("Vendor status", ["Researching", "Contacted", "Quote received", "Booked", "Declined"]),
    "O": ("Tip method", ["% of bill", "Flat amount", "Per person"]),
    "P": ("Rating", [5, 4, 3, 2, 1]),
    "Q": ("Phase", ["Planning", "Budget", "Venue", "Vendors", "Guests", "Ceremony", "Attire", "Stationery", "Honeymoon", "After"]),
    "U": ("Role", ["Maid of honor", "Matron of honor", "Best man", "Bridesmaid", "Groomsman", "Best woman", "Flower girl",
                   "Ring bearer", "Usher", "Reader", "Parent", "Other"]),
}
for col, (h, vals) in simple.items():
    LST[f"{col}1"] = h
    for i, v in enumerate(vals, start=2):
        LST[f"{col}{i}"] = v
LST["J1"] = "Side"
LST["J2"] = "=IF('Start Here'!$C$6=\"\",\"Partner 1\",'Start Here'!$C$6)&\"'s side\""
LST["J3"] = "=IF('Start Here'!$C$7=\"\",\"Partner 2\",'Start Here'!$C$7)&\"'s side\""
LST["J4"] = "Both / mutual"
LST["L1"] = "Owner"
LST["L2"] = "=IF('Start Here'!$C$6=\"\",\"Partner 1\",'Start Here'!$C$6)"
LST["L3"] = "=IF('Start Here'!$C$7=\"\",\"Partner 2\",'Start Here'!$C$7)"
for i, v in enumerate(["Both", "Planner", "Family", "Wedding party"], start=4):
    LST[f"L{i}"] = v
LST["R1"] = "Contributors"
for i in range(5):
    LST[f"R{i + 2}"] = f"=IF('Start Here'!$C${16 + i}=\"\",\"\",'Start Here'!$C${16 + i})"
LST["T1"], LST["T2"] = "Currency symbol", f'=IFERROR(INDEX($B$2:$B${len(CURRENCIES) + 1},MATCH(\'Start Here\'!$C$12,$A$2:$A${len(CURRENCIES) + 1},0)),"$")'
LST["T3"], LST["T4"] = "Report date", "=IF('Start Here'!$C$13=\"\",TODAY(),'Start Here'!$C$13)"
LST["T4"].number_format = FMT["date"]
for c in "ABDEGHIJKLMNOPQRTU":
    LST.column_dimensions[c].width = 18
    LST[f"{c}1"].font = font(10, bold=True)

name("CUR_SYM", "Lists!$T$2")
name("TODAY_D", "Lists!$T$4")
name("WED_DATE", "'Start Here'!$C$8")
name("BUDGET", "'Start Here'!$C$10")
name("GUESTS_TARGET", "'Start Here'!$C$11")

L_YN = f"Lists!$G$2:$G$3"
L_RSVP = "Lists!$H$2:$H$4"
L_MEAL = "Lists!$I$2:$I$8"
L_SIDE = "Lists!$J$2:$J$4"
L_GROUP = "Lists!$K$2:$K$7"
L_OWNER = "Lists!$L$2:$L$7"
L_PTYPE = "Lists!$M$2:$M$7"
L_VSTAT = "Lists!$N$2:$N$6"
L_TIPM = "Lists!$O$2:$O$4"
L_RATE = "Lists!$P$2:$P$6"
L_PHASE = "Lists!$Q$2:$Q$11"
L_CONTRIB = "Lists!$R$2:$R$6"
L_ROLE = "Lists!$U$2:$U$13"
L_TF = f"Lists!$D$2:$D${len(TIMEFRAMES) + 1}"
L_TFD = f"Lists!$E$2:$E${len(TIMEFRAMES) + 1}"
L_CUR = f"Lists!$A$2:$A${len(CURRENCIES) + 1}"
CAT_R0 = 7
L_CAT = f"'Budget Builder'!$B${CAT_R0}:$B${CAT_R0 + NCAT - 1}"
L_ITEM = rng("Budget", "C", B0, B1)
L_VENDOR = rng("Vendors", "C", V0, V1)
L_TABLE = rng("Seating Chart", "B", T0, T1)

# ================================================================== Start Here
ws = START
page_bg(ws, 14, 60)
title(ws, "Wedding Planner", "Start here: fill in the cream cells below. Everything else in the planner updates automatically.")
for col, w in zip("ABCDEFGHIJKL", [2.5, 30, 30, 18, 4, 26, 60, 4, 4, 4, 4, 4]):
    ws.column_dimensions[col].width = w


def section(ws, cell, text, color=ROSE):
    ws[cell] = text.upper()
    ws[cell].font = font(10, bold=True, color=color)


section(ws, "B5", "Your wedding")
settings = [
    (6, "Partner 1 first name", sd.P1, None), (7, "Partner 2 first name", sd.P2, None),
    (8, "Wedding date", sd.WEDDING, "date"), (9, "Venue / city", sd.VENUE, None),
    (10, "Total budget", sd.BUDGET, "money"), (11, "Target guest count", sd.GUESTS, "int"),
    (12, "Currency", "USD", None), (13, "Report date (leave blank = today)", sd.REPORT, "date"),
]
for r, label, val, fmt in settings:
    ws.row_dimensions[r].height = 22
    ws[f"B{r}"] = label
    ws[f"B{r}"].font = font(10, color=INK)
    ws[f"B{r}"].alignment = Alignment(vertical="center")
    c = ws[f"C{r}"]
    set_input(c, fmt)
    if not BLANK:
        c.value = val
    elif r == 12:
        c.value = "USD"
dv_list(ws, L_CUR, "C12")
dv_date(ws, "C8")
dv_date(ws, "C13")
dv_num(ws, "C10")
dv_num(ws, "C11", "whole")
ws["D8"] = '=IF(C8="","",TEXT(C8,"dddd"))'
ws["D8"].font = font(9, italic=True, color=MUTED)
ws["D13"] = '=IF(C13="","using today\'s date","sample/preview date")'
ws["D13"].font = font(9, italic=True, color=MUTED)

section(ws, "B15", "Who's contributing (optional)")
ws["D15"] = cur_h("Pledged")
ws["D15"].font = font(9, bold=True, color=MUTED)
for i in range(5):
    r = 16 + i
    ws.row_dimensions[r].height = 22
    ws[f"B{r}"] = f"Contributor {i + 1}"
    ws[f"B{r}"].font = font(10)
    set_input(ws[f"C{r}"])
    set_input(ws[f"D{r}"], "money")
    if not BLANK and i < len(sd.CONTRIBUTORS):
        ws[f"C{r}"], ws[f"D{r}"] = sd.CONTRIBUTORS[i]
    elif BLANK and i == 0:
        ws[f"C{r}"] = "The couple"
dv_num(ws, "D16:D20")
ws["B22"] = "Contributors appear in the \"Paid by\" dropdown on Payment Schedule and are totalled on Who's Paying."
ws["B22"].font = font(9, italic=True, color=MUTED)

# tab guide
section(ws, "F5", "How this planner works", SAGE)
guide = [
    ("Dashboard", "Countdown, money at a glance, next payments and tasks, RSVPs, charts."),
    ("Budget Builder", "Splits your total budget across 18 categories (edit the %). Compares with what you planned."),
    ("Budget", "Every cost item: estimate, contract price, paid and still owed (paid comes from Payment Schedule)."),
    ("Payment Schedule", "Every deposit and balance with its due date. Mark Paid = Yes when you pay."),
    ("Who's Paying", "Pledged vs paid for each contributor (couple, parents...)."),
    ("Venue Comparison", "Up to 5 venues side by side: true total cost for your guest count, capacity, rating."),
    ("Vendors", "Contacts, quotes and status. Ranks quotes inside each category."),
    ("Guest List", "Sides, plus-ones, addresses, RSVPs, meals, tables, gifts and thank-you cards."),
    ("Seating Chart", "Table capacities and guest names per table, filled from the Guest List."),
    ("Wedding Party", "Roles, contacts, outfits and sizes, fittings, duties and thank-you gifts."),
    ("Checklist", "55+ tasks dated backwards from your wedding date. Mark Done = Yes."),
    ("Tips & Envelopes", "Tip calculator per vendor and envelope checklist for the day."),
    ("Day-Of Timeline", "Hour-by-hour plan to share with vendors and the wedding party."),
]
for i, (tab, desc) in enumerate(guide):
    r = 6 + i
    c = ws[f"F{r}"]
    c.value = f'=HYPERLINK("#\'{tab}\'!A1","{tab}  →")'
    c.font = font(10, bold=True, color=DEEP, underline="single")
    ws[f"G{r}"] = desc
    ws[f"G{r}"].font = font(9.5, color=CALC)
    ws[f"G{r}"].alignment = Alignment(wrap_text=True, vertical="center")
section(ws, "F20", "Good to know", SAGE)
tips = [
    "Cream cells are for typing. White cells calculate; leave them as they are.",
    "Give every Budget item a unique name: Payment Schedule links payments to it by name.",
    "Works in Excel 2016 or newer, Excel for Mac, and Google Sheets (File > Import or upload).",
    "Dropdowns: click a cell and use the small arrow. You can still type your own vendor names.",
    "Budget split percentages are only a starting point. Change them to fit your priorities.",
    "Tip ranges on Tips & Envelopes are common US suggestions, not rules. Check your contracts first.",
]
for i, t in enumerate(tips):
    ws[f"F{21 + i}"] = "•"
    ws[f"F{21 + i}"].alignment = Alignment(horizontal="right")
    ws[f"G{21 + i}"] = t
    ws[f"G{21 + i}"].font = font(9.5, color=CALC)
    ws[f"G{21 + i}"].alignment = Alignment(wrap_text=True, vertical="center")
for r in range(6, 27):
    ws.row_dimensions[r].height = 22 if r in (14, 15, 20) else 30
ws["F28"] = "■ cream = type here"
ws["F28"].fill = fill(INPUT)
ws["F28"].font = font(9, color=INK)
ws["G28"] = "■ white = automatic (formulas)"
ws["G28"].font = font(9, color=MUTED)
ws["B26"] = "NexaGlobe · Wedding Planner · personal use"
ws["B26"].font = font(8, italic=True, color=MUTED)

# ================================================================== Budget Builder
ws = BB
page_bg(ws, 12, 40)
title(ws, "Budget Builder", "Your total budget split into categories. Edit the % to match your priorities; compare with what you've planned in Budget.")
ws["B4"] = '="Total budget: "&' + money_txt("BUDGET") + '&"     ·     Target guests: "&TEXT(GUESTS_TARGET,"#,##0")&"     ·     Per guest: "&IF(N(GUESTS_TARGET)=0,"–",' + money_txt("BUDGET/GUESTS_TARGET") + ")"
ws["B4"].font = font(11, bold=True, color=DEEP)
hdr = ["Category", "Split %", cur_h("Suggested"), cur_h("Per guest"), cur_h("Planned in Budget"),
       cur_h("Left vs suggested"), cur_h("Paid so far"), "Planned % of total"]
widths = [26, 10, 15, 13, 18, 18, 15, 14]
for i, (h, w) in enumerate(zip(hdr, widths)):
    c = ws.cell(6, i + 2, h)
    c.font = font(9.5, bold=True, color="FFFFFF")
    c.fill = fill(DEEP if i < 2 else SAGE)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.column_dimensions[CL(i + 2)].width = w
ws.row_dimensions[6].height = 32
BUD_CAT, BUD_COST, BUD_PAID = rng("Budget", "B", B0, B1), rng("Budget", "G", B0, B1), rng("Budget", "I", B0, B1)
for i, (cat, pct) in enumerate(CATEGORIES):
    r = CAT_R0 + i
    ws.row_dimensions[r].height = 19
    ws[f"B{r}"] = cat
    set_input(ws[f"B{r}"])
    ws[f"C{r}"] = pct
    set_input(ws[f"C{r}"], "pct", align="center")
    for col, f, fmt in [("D", f"=N(BUDGET)*C{r}", "money"),
                        ("E", f"=IF(N(GUESTS_TARGET)=0,0,D{r}/GUESTS_TARGET)", "money"),
                        ("F", f"=SUMIFS({BUD_COST},{BUD_CAT},B{r})", "money"),
                        ("G", f"=D{r}-F{r}", "money"),
                        ("H", f"=SUMIFS({BUD_PAID},{BUD_CAT},B{r})", "money"),
                        ("I", f"=IF(N(BUDGET)=0,0,F{r}/BUDGET)", "pct1")]:
        ws[f"{col}{r}"] = f
        set_calc(ws[f"{col}{r}"], fmt, align="right")
TR = CAT_R0 + NCAT
ws[f"B{TR}"] = "Total"
for col, f, fmt in [("C", f"=SUM(C{CAT_R0}:C{TR - 1})", "pct"), ("D", f"=SUM(D{CAT_R0}:D{TR - 1})", "money"),
                    ("E", f"=SUM(E{CAT_R0}:E{TR - 1})", "money"), ("F", f"=SUM(F{CAT_R0}:F{TR - 1})", "money"),
                    ("G", f"=SUM(G{CAT_R0}:G{TR - 1})", "money"), ("H", f"=SUM(H{CAT_R0}:H{TR - 1})", "money"),
                    ("I", f"=SUM(I{CAT_R0}:I{TR - 1})", "pct1")]:
    ws[f"{col}{TR}"] = f
for col in "BCDEFGHI":
    c = ws[f"{col}{TR}"]
    c.font = font(10.5, bold=True, color=DEEP)
    c.fill = fill(BLUSH)
    c.border = Border(top=side(ROSE, "medium"))
    c.alignment = Alignment(horizontal="right" if col != "B" else "left", vertical="center")
    if col in "DEFGH":
        c.number_format = FMT["money"]
    elif col == "C":
        c.number_format = FMT["pct"]
    elif col == "I":
        c.number_format = FMT["pct1"]
ws[f"B{TR + 1}"] = f'=IF(ROUND(C{TR},4)=1,"✓ Split adds up to 100%","⚠ Split adds up to "&TEXT(C{TR},"0%")&". Adjust it to 100%.")'
ws[f"B{TR + 1}"].font = font(9.5, bold=True, color=SAGE)
uncat = f"=SUM({BUD_COST})-F{TR}"
ws[f"F{TR + 1}"] = uncat
ws[f"F{TR + 1}"].number_format = FMT["money"]
ws[f"F{TR + 1}"].font = font(9, color=MUTED)
ws[f"E{TR + 1}"] = "Not categorised:"
ws[f"E{TR + 1}"].font = font(9, color=MUTED)
ws[f"E{TR + 1}"].alignment = Alignment(horizontal="right")
ws[f"B{TR + 3}"] = ("The split percentages are a neutral starting point, not industry data. Rename categories here and the "
                    "Budget dropdown follows. Red = planned more than suggested.")
ws[f"B{TR + 3}"].font = font(9, italic=True, color=MUTED)
ws.conditional_formatting.add(f"G{CAT_R0}:G{TR}", FormulaRule(formula=[f"G{CAT_R0}<0"], font=Font(color="A23B2A", bold=True)))
ws.conditional_formatting.add(f"B{TR + 1}", FormulaRule(formula=[f"ROUND($C${TR},4)<>1"], font=Font(color="A23B2A", bold=True)))
dv_num(ws, f"C{CAT_R0}:C{TR - 1}")
ws.freeze_panes = "C7"

# ================================================================== Budget
ws = BUD
page_bg(ws, 15, 8)
title(ws, "Budget", "One row per cost. Paid and Still owed fill in from Payment Schedule (match the Item name).")
legend(ws, "B4")
PY_ITEM, PY_AMT, PY_PAID = rng("Payment Schedule", "B", Y0, Y1), rng("Payment Schedule", "G", Y0, Y1), rng("Payment Schedule", "I", Y0, Y1)
bud_cols = [
    dict(h="Category", w=22, dv=(L_CAT, False)),
    dict(h="Item (unique name)", w=30),
    dict(h="Vendor", w=24, dv=(L_VENDOR, True)),
    dict(h=cur_h("Estimate"), w=12, fmt="money", num="decimal", align="right"),
    dict(h=cur_h("Contract price"), w=13, fmt="money", num="decimal", align="right"),
    dict(h=cur_h("Cost used"), w=12, kind="calc", fmt="money", align="right",
         f='=IF(AND(E{r}="",F{r}=""),"",IF(F{r}<>"",F{r},E{r}))'),
    dict(h=cur_h("Scheduled"), w=12, kind="calc", fmt="money", align="right",
         f=f'=IF(C{{r}}="","",SUMIFS({PY_AMT},{PY_ITEM},C{{r}}))'),
    dict(h=cur_h("Paid"), w=12, kind="calc", fmt="money", align="right",
         f=f'=IF(C{{r}}="","",SUMIFS({PY_AMT},{PY_ITEM},C{{r}},{PY_PAID},"Yes"))'),
    dict(h=cur_h("Still owed"), w=12, kind="calc", fmt="money", align="right",
         f='=IF(OR(C{r}="",G{r}=""),"",G{r}-I{r})'),
    dict(h="Status", w=15, kind="calc", align="center",
         f='=IF(C{r}="","",IF(AND(N(G{r})>0,I{r}>=G{r}),"PAID IN FULL",IF(I{r}>0,"PARTLY PAID",IF(H{r}>0,"SCHEDULED","NOT SCHEDULED"))))'),
    dict(h="Notes", w=30),
]
rows = [] if BLANK else [[c, it, v or None, e, a, n] for c, it, v, e, a, n in sd.BUDGET_ITEMS]
table(ws, bud_cols, B0, B1, rows)
badges(ws, f"K{B0}:K{B1}", "K", B0)
ws.conditional_formatting.add(f"C{B0}:C{B1}", FormulaRule(formula=[f'AND(C{B0}<>"",COUNTIF($C${B0}:$C${B1},C{B0})>1)'],
                                                         fill=fill("F5D7D1"), font=Font(color="A23B2A", bold=True)))
ws["F4"] = f'="Total cost: "&{money_txt(f"SUM(G{B0}:G{B1})")}&"   ·   Paid: "&{money_txt(f"SUM(I{B0}:I{B1})")}&"   ·   Still owed: "&{money_txt(f"SUM(J{B0}:J{B1})")}&"   ·   Not scheduled yet: "&{money_txt(f"SUM(G{B0}:G{B1})-SUM(H{B0}:H{B1})")}'
ws["F4"].font = font(10.5, bold=True, color=DEEP)

# ================================================================== Payment Schedule
ws = PAY
page_bg(ws, 16, 8)
title(ws, "Payment Schedule", "Every deposit, installment and final balance. Pick the Budget item, add due date + amount, mark Paid = Yes when paid.")
legend(ws, "B4")
BUD_ITEM, BUD_CATC, BUD_VEN = rng("Budget", "C", B0, B1), rng("Budget", "B", B0, B1), rng("Budget", "D", B0, B1)
pay_cols = [
    dict(h="Budget item", w=30, dv=(L_ITEM, False)),
    dict(h="Category", w=20, kind="calc",
         f=f'=IF(B{{r}}="","",IFERROR(INDEX({BUD_CATC},MATCH(B{{r}},{BUD_ITEM},0))&"","(not in Budget)"))'),
    dict(h="Vendor", w=22, kind="calc", f=f'=IF(B{{r}}="","",IFERROR(INDEX({BUD_VEN},MATCH(B{{r}},{BUD_ITEM},0))&"",""))'),
    dict(h="Payment type", w=14, dv=(L_PTYPE, True)),
    dict(h="Due date", w=13, fmt="date", date=True, align="center"),
    dict(h=cur_h("Amount"), w=12, fmt="money", num="decimal", align="right"),
    dict(h="Paid by", w=18, dv=(L_CONTRIB, True)),
    dict(h="Paid?", w=8, dv=(L_YN, False), align="center"),
    dict(h="Date paid", w=13, fmt="date", date=True, align="center"),
    dict(h="Status", w=13, kind="calc", align="center",
         f='=IF(G{r}="","",IF(I{r}="Yes","PAID",IF(F{r}="","NO DATE",IF(F{r}<TODAY_D,"OVERDUE",IF(F{r}-TODAY_D<=30,"DUE SOON","UPCOMING")))))'),
    dict(h="Days left", w=9, kind="calc", fmt="days", align="center",
         f='=IF(OR(F{r}="",G{r}="",I{r}="Yes"),"",F{r}-TODAY_D)'),
    dict(h="Notes", w=26),
    dict(h="sort key", w=4, kind="helper", f='=IF(AND(G{r}<>"",I{r}<>"Yes",F{r}<>""),F{r}+ROW()/100000,"")'),
]
rows = [] if BLANK else [[it, ty, du, am, pa, pd, dp, no or None] for it, ty, du, am, pa, pd, dp, no in sd.payments()]
table(ws, pay_cols, Y0, Y1, rows)
badges(ws, f"K{Y0}:K{Y1}", "K", Y0)
ws.conditional_formatting.add(f"C{Y0}:C{Y1}", FormulaRule(formula=[f'C{Y0}="(not in Budget)"'], font=Font(color="A23B2A", bold=True)))
ws["F4"] = (f'="Paid: "&{money_txt(f"SUMIFS(G{Y0}:G{Y1},I{Y0}:I{Y1},\"Yes\")")}&"   ·   Scheduled, not paid yet: "&'
            f'{money_txt(f"SUM(G{Y0}:G{Y1})-SUMIFS(G{Y0}:G{Y1},I{Y0}:I{Y1},\"Yes\")")}&"   ·   Overdue: "&COUNTIF(K{Y0}:K{Y1},"OVERDUE")')
ws["F4"].font = font(10.5, bold=True, color=DEEP)

# ================================================================== Who's Paying
ws = WHO
page_bg(ws, 12, 40)
title(ws, "Who's Paying", "Pledged vs paid for each contributor. Names and pledges come from Start Here; payments from Payment Schedule.")
hdr = ["Contributor", cur_h("Pledged"), cur_h("Paid"), cur_h("Scheduled, not paid"), cur_h("Pledge left"), "Pledge used"]
for i, (h, w) in enumerate(zip(hdr, [26, 15, 15, 18, 15, 13])):
    c = ws.cell(6, i + 2, h)
    c.font = font(9.5, bold=True, color="FFFFFF")
    c.fill = fill(SAGE)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.column_dimensions[CL(i + 2)].width = w
ws.row_dimensions[6].height = 32
PY_BY = rng("Payment Schedule", "H", Y0, Y1)
for i in range(5):
    r, s = 7 + i, 16 + i
    ws[f"B{r}"] = f"=IF('Start Here'!$C${s}=\"\",\"\",'Start Here'!$C${s})"
    ws[f"C{r}"] = f"=IF(B{r}=\"\",\"\",N('Start Here'!$D${s}))"
    ws[f"D{r}"] = f'=IF(B{r}="","",SUMIFS({PY_AMT},{PY_BY},B{r},{PY_PAID},"Yes"))'
    ws[f"E{r}"] = f'=IF(B{r}="","",SUMIFS({PY_AMT},{PY_BY},B{r})-D{r})'
    ws[f"F{r}"] = f'=IF(B{r}="","",C{r}-D{r}-E{r})'
    ws[f"G{r}"] = f'=IF(OR(B{r}="",N(C{r})=0),"",(D{r}+E{r})/C{r})'
    for col in "BCDEFG":
        set_calc(ws[f"{col}{r}"], "pct" if col == "G" else ("money" if col != "B" else None), align="left" if col == "B" else "right")
    ws.row_dimensions[r].height = 20
r = 12
ws[f"B{r}"] = "Paid by: not assigned"
ws[f"C{r}"] = 0
ws[f"D{r}"] = f'=SUMIFS({PY_AMT},{PY_PAID},"Yes")-SUM(D7:D11)'
ws[f"E{r}"] = f'=SUM({PY_AMT})-SUMIFS({PY_AMT},{PY_PAID},"Yes")-SUM(E7:E11)'
ws[f"F{r}"] = ""
for col in "BCDEFG":
    set_calc(ws[f"{col}{r}"], "money" if col in "CDE" else None, align="left" if col == "B" else "right")
    ws[f"{col}{r}"].font = font(10, italic=True, color=MUTED)
r = 13
ws[f"B{r}"] = "Total"
for col in "CDEF":
    ws[f"{col}{r}"] = f"=SUM({col}7:{col}12)"
ws[f"G{r}"] = f'=IF(N(C13)=0,"",(D13+E13)/C13)'
for col in "BCDEFG":
    c = ws[f"{col}{r}"]
    c.font = font(10.5, bold=True, color=DEEP)
    c.fill = fill(BLUSH)
    c.border = Border(top=side(ROSE, "medium"))
    c.number_format = FMT["pct" if col == "G" else "money"]
    c.alignment = Alignment(horizontal="left" if col == "B" else "right")
ws["B15"] = "Funding check"
ws["B15"].font = font(10, bold=True, color=ROSE)
checks = [("Total pledged", "=C13"), ("Total wedding cost (Budget)", f"=SUM({BUD_COST})"),
          ("Gap to cover (cost – pledged)", "=C17-C16")]
for i, (lbl, f) in enumerate(checks):
    rr = 16 + i
    ws[f"B{rr}"] = lbl
    ws[f"C{rr}"] = f
    set_calc(ws[f"C{rr}"], "money", bold=i == 2, align="right")
    ws[f"B{rr}"].font = font(10, bold=i == 2)
ws["D18"] = '=IF(C18>0,"Not covered yet",IF(C18<0,"Pledges cover the cost ✓",""))'
ws["D18"].font = font(9.5, italic=True, color=MUTED)
ws.conditional_formatting.add("C18", FormulaRule(formula=["C18>0"], font=Font(color="A23B2A", bold=True)))
ch = BarChart()
ch.type, ch.grouping, ch.overlap = "bar", "stacked", 100
ch.title = "Pledges: paid vs scheduled vs left"
ch.style = 10
for col, colr in (("D", SAGE), ("E", GOLD), ("F", "E3D6D3")):
    ser_ref = Reference(ws, min_col=ord(col) - 64, min_row=6, max_row=11)
    ch.add_data(ser_ref, titles_from_data=True)
    ch.series[-1].graphicalProperties.solidFill = colr
    ch.series[-1].graphicalProperties.line.solidFill = colr
ch.set_categories(Reference(ws, min_col=2, min_row=7, max_row=11))
ch.height, ch.width = 7.5, 17
ch.legend.position = "b"
ch.legend.overlay = False
ch.x_axis.delete = False
ch.y_axis.delete = False
ch.y_axis.numFmt = '#,##0'
ch.y_axis.majorGridlines = None
ch.roundedCorners = False
ws.add_chart(ch, "B21")

# ================================================================== Vendors
ws = VEN
page_bg(ws, 16, 8)
title(ws, "Vendors", "Contacts, quotes and status. \"Quote rank\" compares quotes within the same category (1 = cheapest).")
legend(ws, "B4")
ven_cols = [
    dict(h="Category", w=20, dv=(L_CAT, False)),
    dict(h="Company", w=24),
    dict(h="Contact", w=14),
    dict(h="Phone", w=15),
    dict(h="Email", w=28),
    dict(h="Website / IG", w=22),
    dict(h=cur_h("Quote"), w=11, fmt="money", num="decimal", align="right"),
    dict(h="Status", w=14, dv=(L_VSTAT, False)),
    dict(h="Contract signed", w=10, dv=(L_YN, False), align="center"),
    dict(h="Rating", w=8, dv=(L_RATE, False), align="center"),
    dict(h="Quote rank", w=11, kind="calc", align="center",
         f='=IF(OR(B{r}="",H{r}=""),"",IF(COUNTIFS($B$6:$B$105,B{r},$H$6:$H$105,">0")<2,"–",COUNTIFS($B$6:$B$105,B{r},$H$6:$H$105,"<"&H{r},$H$6:$H$105,">0")+1&" of "&COUNTIFS($B$6:$B$105,B{r},$H$6:$H$105,">0")))'),
    dict(h=cur_h("In Budget"), w=12, kind="calc", fmt="money", align="right",
         f=f'=IF(C{{r}}="","",SUMIFS({BUD_COST},{BUD_VEN},C{{r}}))'),
    dict(h="Notes", w=28),
]
rows = [] if BLANK else [[cat, co, ct, ph, em, web, sd.VENDOR_QUOTES.get(co), st, con, rt, no or None]
                         for co, cat, ct, ph, em, web, st, con, rt, no in sd.VENDORS]
table(ws, ven_cols, V0, V1, rows)
ws.conditional_formatting.add(f"L{V0}:L{V1}", FormulaRule(formula=[f'LEFT(L{V0},2)="1 "'], fill=fill(SAGE_LT), font=Font(color="3F6B45", bold=True)))
ws.conditional_formatting.add(f"I{V0}:I{V1}", FormulaRule(formula=[f'I{V0}="Booked"'], fill=fill(SAGE_LT), font=Font(color="3F6B45", bold=True)))
ws.conditional_formatting.add(f"I{V0}:I{V1}", FormulaRule(formula=[f'I{V0}="Declined"'], font=Font(color=MUTED, italic=True)))

# ================================================================== Guest List
ws = GUEST
page_bg(ws, 25, 8)
title(ws, "Guest List", "One row per invitation. Party size counts the plus-one; seat guests by picking a table. Address columns are mail-merge ready.")
legend(ws, "B4")
guest_cols = [
    dict(h="Guest name", w=22),
    dict(h="Side", w=16, dv=(L_SIDE, False)),
    dict(h="Group", w=12, dv=(L_GROUP, True)),
    dict(h="Plus-one?", w=9, dv=(L_YN, False), align="center"),
    dict(h="Plus-one name", w=18),
    dict(h="Party size", w=8, kind="calc", align="center", f='=IF(B{r}="","",1+IF(E{r}="Yes",1,0))'),
    dict(h="Street address", w=26),
    dict(h="City", w=14),
    dict(h="State", w=7, align="center"),
    dict(h="ZIP", w=8, fmt="text", align="center"),
    dict(h="Email / phone", w=26),
    dict(h="Save the date sent", w=10, dv=(L_YN, False), align="center"),
    dict(h="Invite sent", w=9, dv=(L_YN, False), align="center"),
    dict(h="RSVP", w=11, dv=(L_RSVP, False), align="center"),
    dict(h="Attending", w=9, kind="calc", align="center", f='=IF(B{r}="","",IF(O{r}="Attending",G{r},0))'),
    dict(h="Meal", w=12, dv=(L_MEAL, True)),
    dict(h="Plus-one meal", w=12, dv=(L_MEAL, True)),
    dict(h="Dietary / allergies", w=16),
    dict(h="Table", w=12, dv=(L_TABLE, False)),
    dict(h="Gift received", w=22),
    dict(h="Thank-you sent", w=10, dv=(L_YN, False), align="center"),
    dict(h="seat key", w=4, kind="helper",
         f='=IF(OR(B{r}="",T{r}="",O{r}="Declined"),"",T{r}&"|"&COUNTIFS($T$6:T{r},T{r},$O$6:O{r},"<>Declined",$B$6:B{r},"<>"))'),
]
gs = [] if BLANK else sd.assign_tables(sd.guests())
def split_addr(a):
    street, city, st_zip = [x.strip() for x in a.split(",")]
    st, zp = st_zip.split()
    return [street, city, st, zp]


rows = [[g["name"], g["side"], g["group"], g["plus"], g["plus_name"] or None, *split_addr(g["addr"]), g["contact"], g["std"], g["inv"],
         g["rsvp"], g["meal"] or None, g["meal2"] or None, g["diet"] or None, g.get("table"), g["gift"] or None, g["ty"]] for g in gs]
table(ws, guest_cols, G0, G1, rows)
for txt, bg, fg in (("Attending", SAGE_LT, "3F6B45"), ("Declined", "F1EFEF", MUTED), ("Pending", GOLD_LT, "8A6A1F")):
    ws.conditional_formatting.add(f"O{G0}:O{G1}", FormulaRule(formula=[f'O{G0}="{txt}"'], fill=fill(bg), font=Font(color=fg, bold=True)))
ws.conditional_formatting.add(f"V{G0}:V{G1}", FormulaRule(formula=[f'AND(U{G0}<>"",V{G0}<>"Yes")'], fill=fill("F5D7D1")))
GN = f"$G${G0}:$G${G1}"
ws["H4"] = (f'="Invited: "&SUM({GN})&"   ·   Attending: "&SUM($P${G0}:$P${G1})&"   ·   Declined: "&SUMIFS({GN},$O${G0}:$O${G1},"Declined")'
            f'&"   ·   Awaiting reply: "&(SUM({GN})-SUM($P${G0}:$P${G1})-SUMIFS({GN},$O${G0}:$O${G1},"Declined"))')
ws["H4"].font = font(10.5, bold=True, color=DEEP)

# ================================================================== Seating Chart
ws = SEAT
page_bg(ws, 8 + SEATS, 50)
title(ws, "Seating Chart", "Name your tables and set capacity. Names fill in from Guest List (pick a Table there). \"+1\" = guest brings a plus-one.")
legend(ws, "B4")
G_TAB, G_SIZE, G_RSVP, G_ATT, G_KEY, G_NAME = (rng("Guest List", c, G0, G1) for c in "TGOPWB")
ws["H4"] = (f'="Seated: "&SUM(D{T0}:D{T1})&"   ·   Capacity: "&SUM(C{T0}:C{T1})&"   ·   Attending guests without a table: "&'
            f'(SUM({G_ATT})-SUM(E{T0}:E{T1}))')
ws["H4"].font = font(10.5, bold=True, color=DEEP)
seat_hdr = [("Table", 14, DEEP), ("Seats", 7, DEEP), ("Assigned", 9, SAGE), ("Confirmed", 9, SAGE), ("Free", 7, SAGE), ("Status", 14, SAGE)]
seat_hdr += [(f"Guest {k}", 17, ROSE) for k in range(1, SEATS + 1)]
ws.row_dimensions[6].height = 30
for i, (h, w, colr) in enumerate(seat_hdr):
    c = ws.cell(6, i + 2, h)
    c.font = font(9.5, bold=True, color="FFFFFF")
    c.fill = fill(colr)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.column_dimensions[CL(i + 2)].width = w
tables = [] if BLANK else sd.TABLES
for r in range(T0, T1 + 1):
    ws.row_dimensions[r].height = 19
    i = r - T0
    set_input(ws[f"B{r}"])
    set_input(ws[f"C{r}"], "int", align="center")
    if BLANK and i < 12:
        ws[f"B{r}"], ws[f"C{r}"] = ("Head Table" if i == 0 else f"Table {i}"), 8
    elif i < len(tables):
        ws[f"B{r}"], ws[f"C{r}"] = tables[i]
    ws[f"D{r}"] = f'=IF(B{r}="","",SUMIFS({G_SIZE},{G_TAB},B{r},{G_RSVP},"<>Declined"))'
    ws[f"E{r}"] = f'=IF(B{r}="","",SUMIFS({G_ATT},{G_TAB},B{r}))'
    ws[f"F{r}"] = f'=IF(B{r}="","",N(C{r})-D{r})'
    ws[f"G{r}"] = f'=IF(B{r}="","",IF(D{r}>N(C{r}),"OVER CAPACITY",IF(D{r}=0,"EMPTY",IF(D{r}=N(C{r}),"FULL","OPEN"))))'
    for col in "DEFG":
        set_calc(ws[f"{col}{r}"], "int" if col != "G" else None, align="center")
    for k in range(1, SEATS + 1):
        col = CL(7 + k)
        m = f'MATCH($B{r}&"|{k}",{G_KEY},0)'
        ws[f"{col}{r}"] = f'=IF($B{r}="","",IFERROR(INDEX({G_NAME},{m})&IF(INDEX({G_SIZE},{m})>1," +1",""),""))'
        set_calc(ws[f"{col}{r}"])
        ws[f"{col}{r}"].font = font(9, color=INK)
dv_num(ws, f"C{T0}:C{T1}", "whole")
badges(ws, f"G{T0}:G{T1}", "G", T0)
ws.freeze_panes = "C7"
ws[f"B{T1 + 2}"] = (f"Up to {SEATS} invitations are listed per table (a \"+1\" takes two seats). Rename a table here and "
                    "re-pick it on the Guest List.")
ws[f"B{T1 + 2}"].font = font(9, italic=True, color=MUTED)

# ================================================================== Checklist
ws = CHK
page_bg(ws, 12, 8)
title(ws, "Checklist", "Due dates are counted back from your wedding date. Mark Done = Yes. Add your own tasks at the bottom.")
legend(ws, "B4")
chk_cols = [
    dict(h="Task", w=46),
    dict(h="Phase", w=13, dv=(L_PHASE, True)),
    dict(h="When", w=14, dv=(L_TF, False)),
    dict(h="Due date", w=14, kind="calc", fmt="date", align="center",
         f=f'=IF(OR(B{{r}}="",D{{r}}="",N(WED_DATE)=0),"",WED_DATE-IFERROR(INDEX({L_TFD},MATCH(D{{r}},{L_TF},0)),0))'),
    dict(h="Owner", w=13, dv=(L_OWNER, True)),
    dict(h="Done?", w=8, dv=(L_YN, False), align="center"),
    dict(h="Status", w=12, kind="calc", align="center",
         f='=IF(B{r}="","",IF(G{r}="Yes","DONE",IF(E{r}="","NO DATE",IF(E{r}<TODAY_D,"OVERDUE",IF(E{r}-TODAY_D<=30,"DUE SOON","LATER")))))'),
    dict(h="Notes", w=30),
    dict(h="sort key", w=4, kind="helper", f='=IF(AND(B{r}<>"",G{r}<>"Yes",E{r}<>""),E{r}+ROW()/100000,"")'),
]
days = dict(TIMEFRAMES)
rows = []
owners = [sd.P1, sd.P2, "Both", "Planner"]
for i, (task, ph, tf) in enumerate(sd.CHECKLIST):
    if BLANK:
        rows.append([task, ph, tf, None, None, None])
    else:
        due = sd.WEDDING.toordinal() - days[tf]
        done = "Yes" if due < sd.REPORT.toordinal() and task not in ("Get the marriage license", "Buy favors and wedding party gifts") else None
        rows.append([task, ph, tf, owners[i % 4] if i % 3 else "Both", done, None])
table(ws, chk_cols, C0, C1, rows)
badges(ws, f"H{C0}:H{C1}", "H", C0)
ws.conditional_formatting.add(f"B{C0}:B{C1}", FormulaRule(formula=[f'$G{C0}="Yes"'], font=Font(color=MUTED, strike=True)))
ws["F4"] = f'="Done: "&COUNTIF(H{C0}:H{C1},"DONE")&" of "&COUNTA(B{C0}:B{C1})&"   ·   Overdue: "&COUNTIF(H{C0}:H{C1},"OVERDUE")&"   ·   Due in 30 days: "&COUNTIF(H{C0}:H{C1},"DUE SOON")'
ws["F4"].font = font(10.5, bold=True, color=DEEP)

# ================================================================== Tips & Envelopes
ws = TIP
page_bg(ws, 16, 8)
title(ws, "Tips & Envelopes", "Work out every tip, then tick off the envelopes. Ranges are common US suggestions; check if gratuity is already in your contract.")
legend(ws, "B4")
tip_cols = [
    dict(h="Who", w=24),
    dict(h="Vendor / name", w=22, dv=(L_VENDOR, True)),
    dict(h=cur_h("Bill amount"), w=12, fmt="money", num="decimal", align="right"),
    dict(h="Method", w=12, dv=(L_TIPM, False)),
    dict(h="Tip %", w=8, fmt="pct", num="decimal", align="center"),
    dict(h=cur_h("Flat / per person"), w=12, fmt="money", num="decimal", align="right"),
    dict(h="# people", w=8, fmt="int", num="whole", align="center"),
    dict(h="Gratuity in contract?", w=11, dv=(L_YN, False), align="center"),
    dict(h=cur_h("Tip"), w=11, kind="calc", fmt="money", align="right", bold=True,
         f='=IF(B{r}="","",IF(I{r}="Yes",0,IF(E{r}="% of bill",N(D{r})*N(F{r}),IF(E{r}="Per person",N(G{r})*N(H{r}),N(G{r})))))'),
    dict(h="Common range (guide)", w=30, kind="input"),
    dict(h="Who hands it over", w=15, dv=(L_OWNER, True)),
    dict(h="Envelope ready", w=10, dv=(L_YN, False), align="center"),
    dict(h="Given", w=8, dv=(L_YN, False), align="center"),
]
bills = {"Catering staff / servers": 7480, "Bartenders": 2250, "Hair stylist": 500, "Makeup artist": 450, "Shuttle / limo driver": 700}
vend = {"Catering staff / servers": "Harvest Table Catering", "Bartenders": "Harvest Table Catering", "Hair stylist": "Glow Studio",
        "Makeup artist": "Glow Studio", "Photographer": "Lena Park Photography", "Videographer": "Golden Hour Films",
        "DJ": "Spin Society", "Officiant": "Rev. Sam Ortiz", "Delivery / setup crew": "Twinkle Rentals",
        "Shuttle / limo driver": "River City Shuttles", "Day-of coordinator": "Simply Wed Co."}
rows = []
for role, meth, pct, flat, ppl, guide_txt in sd.TIP_ROLES:
    if BLANK:
        rows.append([role, None, None, meth, pct, flat, ppl, None, guide_txt, None, None, None])
    else:
        if role == "Band musicians":
            continue
        incl = "Yes" if role == "Catering staff / servers" else "No"
        rows.append([role, vend.get(role), bills.get(role), meth, pct, flat, ppl, incl, guide_txt,
                     "Planner" if role not in ("Hair stylist", "Makeup artist") else sd.P1,
                     "Yes" if role in ("Officiant", "DJ") else "No", None])
table(ws, tip_cols, P0, P1, rows)
TT = P1 + 1
ws[f"I{TT}"] = "Total tips"
ws[f"J{TT}"] = f"=SUM(J{P0}:J{P1})"
for col in "IJ":
    ws[f"{col}{TT}"].font = font(11, bold=True, color=DEEP)
    ws[f"{col}{TT}"].fill = fill(BLUSH)
ws[f"J{TT}"].number_format = FMT["money"]
ws["F4"] = (f'="Total tips: "&{money_txt(f"SUM(J{P0}:J{P1})")}&"   ·   Budgeted for tips: "&{money_txt(f"SUMIFS({BUD_COST},{BUD_CAT},\"Tips & Gratuities\")")}'
            f'&"   ·   Envelopes ready: "&COUNTIFS(M{P0}:M{P1},"Yes",B{P0}:B{P1},"<>")&" of "&COUNTA(B{P0}:B{P1})')
ws["F4"].font = font(10.5, bold=True, color=DEEP)
ws.conditional_formatting.add(f"M{P0}:N{P1}", FormulaRule(formula=[f'M{P0}="Yes"'], fill=fill(SAGE_LT), font=Font(color="3F6B45", bold=True)))
for r in range(P0, P1 + 1):
    ws[f"K{r}"].font = font(9, italic=True, color=MUTED)

# ================================================================== Day-Of Timeline
ws = DAY
page_bg(ws, 10, 8)
title(ws, "Day-Of Timeline", "Hour by hour. Starter plan included: change the times and names, then share it with vendors and the wedding party.")
legend(ws, "B4")
ws["F4"] = '=IF(N(WED_DATE)=0,"",TEXT(WED_DATE,"dddd, mmmm d, yyyy"))'
ws["F4"].font = font(11, bold=True, color=DEEP)
day_cols = [
    dict(h="Start", w=10, fmt="time", align="center"),
    dict(h="End", w=10, fmt="time", align="center"),
    dict(h="Length", w=8, kind="calc", align="center", f='=IF(OR(B{r}="",C{r}=""),"",TEXT(C{r}-B{r},"h:mm"))'),
    dict(h="What's happening", w=34),
    dict(h="Where", w=18),
    dict(h="Who's involved", w=34),
    dict(h="Notes", w=30),
]


def t(s):
    h, m = map(int, s.split(":"))
    return time(h, m)


rows = [[t(a), t(b), what, where, who, None] for a, b, what, where, who in sd.TIMELINE]
table(ws, day_cols, D0, D1, rows, autofilter=False)

# ================================================================== Venue Comparison
ws = VNU
page_bg(ws, 9, 45)
title(ws, "Venue Comparison", "Compare up to 5 venues side by side. The estimate uses your target guest count from Start Here.")
legend(ws, "B4")
ws.column_dimensions["B"].width = 34
NV = 5
VC = [CL(3 + i) for i in range(NV)]  # C..G
for c in VC:
    ws.column_dimensions[c].width = 22
ws.row_dimensions[6].height = 26
ws["B6"] = "Venue details"
ws["B6"].font = font(10, bold=True, color="FFFFFF")
ws["B6"].fill = fill(DEEP)
for i, c in enumerate(VC):
    ws[f"{c}6"] = f"Option {i + 1}"
    ws[f"{c}6"].font = font(10, bold=True, color="FFFFFF")
    ws[f"{c}6"].fill = fill(DEEP)
    ws[f"{c}6"].alignment = Alignment(horizontal="center", vertical="center")
VROWS = [  # (row, label, fmt, kind) kind: text|yn|num|pct|rate
    (7, "Venue name", None, "text"), (8, "Location / city", None, "text"), (9, "Contact & phone", None, "text"),
    (10, "Available dates", None, "text"), (11, "Max guests", "int", "num"), (12, cur_h("Venue / site fee"), "money", "num"),
    (13, "Catering in-house?", None, "yn"), (14, cur_h("Food & bar per guest"), "money", "num"),
    (15, cur_h("Rentals & other fees"), "money", "num"), (16, cur_h("Food & bar minimum spend"), "money", "num"),
    (17, "Service charge % (food & bar)", "pct", "pct"), (18, "Sales tax %", "pct1", "pct"),
    (19, "Ceremony on site?", None, "yn"), (20, "Rain / indoor backup?", None, "yn"), (21, "End time / curfew", None, "text"),
    (22, "Guest rooms nearby?", None, "yn"), (23, "Visited?", None, "yn"), (24, "Your rating (1-5)", None, "rate"),
    (25, "Pros / cons", None, "text"), (26, "Our choice?", None, "yn"),
]
for r, label, fmt, kind in VROWS:
    ws.row_dimensions[r].height = 40 if r == 25 else 20
    ws[f"B{r}"] = label
    ws[f"B{r}"].font = font(10, color=INK)
    ws[f"B{r}"].alignment = Alignment(vertical="center")
    ws[f"B{r}"].border = UNDER
    for c in VC:
        set_input(ws[f"{c}{r}"], fmt, wrap=(r == 25), align="left" if kind == "text" else "center")
    ref = f"C{r}:{VC[-1]}{r}"
    if kind == "yn":
        dv_list(ws, L_YN, ref)
    elif kind == "rate":
        dv_list(ws, L_RATE, ref)
    elif kind in ("num", "pct"):
        dv_num(ws, ref)
ws["B28"] = '="Estimated cost for "&TEXT(N(GUESTS_TARGET),"#,##0")&" guests"'
ws["B28"].font = font(10, bold=True, color="FFFFFF")
for c in ["B"] + VC:
    ws[f"{c}28"].fill = fill(SAGE)
ws.row_dimensions[28].height = 26
G = "N(GUESTS_TARGET)"
CROWS = [
    (29, cur_h("Food & bar"), "money", "=IF({c}7=\"\",\"\",N({c}14)*" + G + ")"),
    (30, cur_h("Minimum-spend top-up"), "money", "=IF({c}7=\"\",\"\",MAX(0,N({c}16)-{c}29))"),
    (31, cur_h("Service charge"), "money", "=IF({c}7=\"\",\"\",({c}29+{c}30)*N({c}17))"),
    (32, cur_h("Tax"), "money", "=IF({c}7=\"\",\"\",(N({c}12)+{c}29+{c}30+N({c}15)+{c}31)*N({c}18))"),
    (33, cur_h("Estimated total"), "money", "=IF({c}7=\"\",\"\",N({c}12)+{c}29+{c}30+N({c}15)+{c}31+{c}32)"),
    (34, cur_h("Per guest"), "money", "=IF(OR({c}7=\"\"," + G + "=0),\"\",{c}33/" + G + ")"),
    (35, "Fits your guest count?", None, "=IF({c}7=\"\",\"\",IF(N({c}11)=0,\"–\",IF({c}11>=" + G + ",\"FITS\",\"TOO SMALL\")))"),
    (36, cur_h("vs. Venue + Catering budget"), "money",
     "=IF({c}7=\"\",\"\",'Budget Builder'!$D$" + str(CAT_R0) + "+'Budget Builder'!$D$" + str(CAT_R0 + 1) + "-{c}33)"),
    (37, "Price rank", None, "=IF({c}7=\"\",\"\",COUNTIF($C$33:$G$33,\"<\"&{c}33)+1&\" of \"&COUNT($C$33:$G$33))"),
    (38, "Status", None, "=IF({c}7=\"\",\"\",IF({c}26=\"Yes\",\"CHOSEN\",IF(AND(COUNT($C$33:$G$33)>1,{c}33=MIN($C$33:$G$33)),\"BEST PRICE\",\"\")))"),
]
for r, label, fmt, f in CROWS:
    ws.row_dimensions[r].height = 20
    ws[f"B{r}"] = label
    ws[f"B{r}"].font = font(10, bold=r == 33, color=INK)
    ws[f"B{r}"].border = UNDER
    for c in VC:
        ws[f"{c}{r}"] = f.format(c=c)
        set_calc(ws[f"{c}{r}"], fmt, bold=r in (33, 38), align="center" if fmt is None else "right")
    if r == 33:
        for c in ["B"] + VC:
            ws[f"{c}{r}"].fill = fill(BLUSH)
            ws[f"{c}{r}"].font = font(10.5, bold=True, color=DEEP)
ws.conditional_formatting.add("C35:G35", FormulaRule(formula=['C35="TOO SMALL"'], fill=fill("F5D7D1"), font=Font(color="A23B2A", bold=True)))
ws.conditional_formatting.add("C35:G35", FormulaRule(formula=['C35="FITS"'], fill=fill(SAGE_LT), font=Font(color="3F6B45", bold=True)))
ws.conditional_formatting.add("C36:G36", FormulaRule(formula=['AND(C36<>"",C36<0)'], font=Font(color="A23B2A", bold=True)))
ws.conditional_formatting.add("C38:G38", FormulaRule(formula=['C38="CHOSEN"'], fill=fill(DEEP), font=Font(color="FFFFFF", bold=True)))
ws.conditional_formatting.add("C38:G38", FormulaRule(formula=['C38="BEST PRICE"'], fill=fill(SAGE_LT), font=Font(color="3F6B45", bold=True)))
ws["B40"] = ("If catering is not in-house, enter your caterer's per-guest price so options compare fairly. "
             "\"vs. budget\" uses the first two Budget Builder categories (Venue + Catering & Bar).")
ws["B40"].font = font(9, italic=True, color=MUTED)
ws.freeze_panes = "C7"
if not BLANK:
    for i, v in enumerate(sd.VENUES):
        c = VC[i]
        for r, val in zip(range(7, 27), v):
            if val is not None:
                ws[f"{c}{r}"] = val

# ================================================================== Wedding Party
ws = PARTY
page_bg(ws, 18, 8)
title(ws, "Wedding Party", "Everyone standing with you: roles, contacts, outfits and sizes, fittings, duties and thank-you gifts.")
legend(ws, "B4")
party_cols = [
    dict(h="Name", w=20),
    dict(h="Role", w=15, dv=(L_ROLE, True)),
    dict(h="Side", w=15, dv=(L_SIDE, False)),
    dict(h="Phone", w=15),
    dict(h="Email", w=26),
    dict(h="Outfit", w=22),
    dict(h="Size", w=8, align="center"),
    dict(h="Outfit ordered?", w=9, dv=(L_YN, False), align="center"),
    dict(h="Fitting date", w=13, fmt="date", date=True, align="center"),
    dict(h="Hair & makeup?", w=9, dv=(L_YN, False), align="center"),
    dict(h="At rehearsal?", w=9, dv=(L_YN, False), align="center"),
    dict(h="Duties on the day", w=30),
    dict(h="Thank-you gift", w=20),
    dict(h="Gift bought?", w=9, dv=(L_YN, False), align="center"),
    dict(h="Status", w=11, kind="calc", align="center",
         f='=IF(B{r}="","",IF(AND(I{r}="Yes",O{r}="Yes"),"READY","TO DO"))'),
]
PA0, PA1 = 6, 45
rows = [] if BLANK else [list(p) for p in sd.WEDDING_PARTY]
table(ws, party_cols, PA0, PA1, rows)
ws.conditional_formatting.add(f"P{PA0}:P{PA1}", FormulaRule(formula=[f'P{PA0}="READY"'], fill=fill(SAGE_LT), font=Font(color="3F6B45", bold=True)))
ws.conditional_formatting.add(f"P{PA0}:P{PA1}", FormulaRule(formula=[f'P{PA0}="TO DO"'], fill=fill(GOLD_LT), font=Font(color="8A6A1F", bold=True)))
ws["F4"] = (f'="People: "&COUNTA(B{PA0}:B{PA1})&"   ·   Outfits ordered: "&COUNTIFS(I{PA0}:I{PA1},"Yes",B{PA0}:B{PA1},"<>")'
            f'&"   ·   Gifts bought: "&COUNTIFS(O{PA0}:O{PA1},"Yes",B{PA0}:B{PA1},"<>")&"   ·   Hair & makeup: "&COUNTIFS(K{PA0}:K{PA1},"Yes",B{PA0}:B{PA1},"<>")')
ws["F4"].font = font(10.5, bold=True, color=DEEP)


# ================================================================== Dashboard
ws = DASH
page_bg(ws, 17, 70)
ws.column_dimensions["A"].width = 2.5
for col in "BCDEFGHIJKLMNOP":
    ws.column_dimensions[col].width = 11.5
ws.column_dimensions["H"].width = 3
ws.row_dimensions[1].height = 10
ws.row_dimensions[2].height = 40
ws["B2"] = '=IF(AND(\'Start Here\'!C6="",\'Start Here\'!C7=""),"Our Wedding",\'Start Here\'!C6&" & "&\'Start Here\'!C7)'
ws["B2"].font = font(26, name=HEAD, color=DEEP)
ws["B3"] = '=IF(N(WED_DATE)=0,"Add your wedding date on Start Here",TEXT(WED_DATE,"dddd, mmmm d, yyyy")&IF(\'Start Here\'!C9="","","  ·  "&\'Start Here\'!C9))'
ws["B3"].font = font(11, italic=True, color=ROSE)
ws["L3"] = '="Updated "&TEXT(TODAY_D,"mmm d, yyyy")'
ws["L3"].font = font(9, color=MUTED)
ws["L3"].alignment = Alignment(horizontal="right")
ws.merge_cells("L3:P3")

PAID_ALL = f'SUMIFS({PY_AMT},{PY_PAID},"Yes")'
COST_ALL = f"SUM({BUD_COST})"
G_INV = f"SUM({G_SIZE})"
G_ATTS = f"SUM({G_ATT})"
G_DEC = f'SUMIFS({G_SIZE},{G_RSVP},"Declined")'
CHK_STAT = rng("Checklist", "H", C0, C1)
CHK_TASK = rng("Checklist", "B", C0, C1)
PY_STAT = rng("Payment Schedule", "K", Y0, Y1)
tiles = [
    ("DAYS TO GO", '=IF(N(WED_DATE)=0,"–",MAX(0,WED_DATE-TODAY_D))', '=IF(N(WED_DATE)=0,"set a date",IF(WED_DATE<TODAY_D,"married! 🎉","until the big day"))', ROSE),
    ("BUDGET", "=" + money_txt("N(BUDGET)"), f'=IF(N(BUDGET)=0,"set it on Start Here",IF({COST_ALL}>BUDGET,"over by "&{money_txt(f"{COST_ALL}-BUDGET")},{money_txt(f"BUDGET-{COST_ALL}")}&" not yet planned"))', GOLD),
    ("COMMITTED", "=" + money_txt(COST_ALL), f'=IF(N(BUDGET)=0,"",TEXT({COST_ALL}/BUDGET,"0%")&" of budget")', GOLD),
    ("PAID SO FAR", "=" + money_txt(PAID_ALL), f'=IF({COST_ALL}=0,"",TEXT({PAID_ALL}/{COST_ALL},"0%")&" of committed")', SAGE),
    ("STILL TO PAY", "=" + money_txt(f"{COST_ALL}-{PAID_ALL}"), f'=COUNTIF({PY_STAT},"OVERDUE")&" overdue · "&COUNTIF({PY_STAT},"DUE SOON")&" due in 30 days"', SAGE),
    ("GUESTS ATTENDING", f'={G_ATTS}&" / "&{G_INV}', f'=({G_INV}-{G_ATTS}-{G_DEC})&" awaiting reply"', ROSE),
    ("TASKS DONE", f'=COUNTIF({CHK_STAT},"DONE")&" / "&COUNTA({CHK_TASK})', f'=COUNTIF({CHK_STAT},"OVERDUE")&" overdue"', SAGE),
]
# 7 tiles across B..P with H as a spacer: B-C, D-E, F-G, I-J, K-L, M-N, O-P
spans = [("B", "C"), ("D", "E"), ("F", "G"), ("I", "J"), ("K", "L"), ("M", "N"), ("O", "P")]
ws.row_dimensions[5].height = 20
ws.row_dimensions[6].height = 36
ws.row_dimensions[7].height = 30
for (a, b), (lbl, val, sub, colr) in zip(spans, tiles):
    for rr in (5, 6, 7):
        ws.merge_cells(f"{a}{rr}:{b}{rr}")
        for col in (a, b):
            ws[f"{col}{rr}"].fill = fill(CARD)
    ws[f"{a}5"].border = Border(top=side(colr, "thick"))
    ws[f"{b}5"].border = Border(top=side(colr, "thick"))
    ws[f"{a}5"] = lbl
    ws[f"{a}5"].font = font(8.5, bold=True, color=MUTED)
    ws[f"{a}6"] = val
    ws[f"{a}6"].font = font(19, name=HEAD, color=DEEP)
    ws[f"{a}7"] = sub
    ws[f"{a}7"].font = font(8.5, color=colr)
    for rr in (5, 6, 7):
        ws[f"{a}{rr}"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=rr == 7)


def dash_section(cell, text):
    ws[cell] = text
    ws[cell].font = font(13, name=HEAD, color=DEEP)


# --- upcoming payments (B..G) and next tasks (I..P)
dash_section("B9", "Upcoming & overdue payments")
dash_section("I9", "Next tasks")
PY_KEY, PY_DUE, PY_VEN, PY_STATC = (rng("Payment Schedule", c, Y0, Y1) for c in "NFDK")
CK_KEY, CK_DUE, CK_OWN = (rng("Checklist", c, C0, C1) for c in "JEF")
for col, h in zip("BCDEFG", ["Due", "Item", "", "Vendor", cur_h("Amount"), "Status"]):
    ws[f"{col}10"] = h
for col, h in zip("IJKLMNOP", ["Due", "Task", "", "", "", "", "Owner", "Status"]):
    ws[f"{col}10"] = h
for col in "BCDEFGIJKLMNOP":
    c = ws[f"{col}10"]
    c.font = font(9, bold=True, color="FFFFFF")
    c.fill = fill(SAGE)
    c.alignment = Alignment(horizontal="center", vertical="center")
ws.merge_cells("C10:D10")
ws.merge_cells("J10:N10")
NUP = 7
for k in range(1, NUP + 1):
    r = 10 + k
    ws.row_dimensions[r].height = 19
    key = f"SMALL({PY_KEY},{k})"
    m = f"MATCH({key},{PY_KEY},0)"
    ws[f"B{r}"] = f'=IFERROR(INDEX({PY_DUE},{m}),"")'
    ws[f"C{r}"] = f'=IFERROR(INDEX({PY_ITEM},{m}),"")'
    ws[f"E{r}"] = f'=IFERROR(INDEX({PY_VEN},{m}),"")'
    ws[f"F{r}"] = f'=IFERROR(INDEX({PY_AMT},{m}),"")'
    ws[f"G{r}"] = f'=IFERROR(INDEX({PY_STATC},{m}),"")'
    ws.merge_cells(f"C{r}:D{r}")
    keyc = f"SMALL({CK_KEY},{k})"
    mc = f"MATCH({keyc},{CK_KEY},0)"
    ws[f"I{r}"] = f'=IFERROR(INDEX({CK_DUE},{mc}),"")'
    ws[f"J{r}"] = f'=IFERROR(INDEX({CHK_TASK},{mc}),"")'
    ws[f"O{r}"] = f'=IFERROR(INDEX({CK_OWN},{mc})&"","")'
    ws[f"P{r}"] = f'=IFERROR(INDEX({CHK_STAT},{mc}),"")'
    ws.merge_cells(f"J{r}:N{r}")
    for col in "BCDEFGIJKLMNOP":
        c = ws[f"{col}{r}"]
        c.fill = fill(CARD)
        c.border = UNDER
        c.font = font(9.5, color=INK)
        c.alignment = Alignment(vertical="center", horizontal="center" if col in "BGIPO" else ("right" if col == "F" else "left"))
    ws[f"B{r}"].number_format = FMT["sdate"]
    ws[f"I{r}"].number_format = FMT["sdate"]
    ws[f"F{r}"].number_format = FMT["money"]
badges(ws, f"G11:G{10 + NUP}", "G", 11)
badges(ws, f"P11:P{10 + NUP}", "P", 11)
ws[f"B{11 + NUP}"] = '=IF(B11="","No unpaid payments with a due date. Add them on Payment Schedule.","")'
ws[f"I{11 + NUP}"] = '=IF(I11="",IF(N(WED_DATE)=0,"Add your wedding date on Start Here to date the checklist.","No open tasks with a due date. 🎉"),"")'
for cc in (f"B{11 + NUP}", f"I{11 + NUP}"):
    ws[cc].font = font(9, italic=True, color=MUTED)

# --- budget by category table (B..G) + doughnut chart (I..P)
R0 = 21
dash_section(f"B{R0}", "Budget by category")
for col, h in zip("BCDEFG", ["Category", "", cur_h("Suggested"), cur_h("Planned"), cur_h("Paid"), "Left"]):
    ws[f"{col}{R0 + 1}"] = h
for col in "BCDEFG":
    c = ws[f"{col}{R0 + 1}"]
    c.font = font(9, bold=True, color="FFFFFF")
    c.fill = fill(SAGE)
    c.alignment = Alignment(horizontal="center", vertical="center")
ws.merge_cells(f"B{R0 + 1}:C{R0 + 1}")
for i in range(NCAT):
    r, s = R0 + 2 + i, CAT_R0 + i
    ws[f"B{r}"] = f"='Budget Builder'!B{s}"
    ws[f"D{r}"] = f"='Budget Builder'!D{s}"
    ws[f"E{r}"] = f"='Budget Builder'!F{s}"
    ws[f"F{r}"] = f"='Budget Builder'!H{s}"
    ws[f"G{r}"] = f"=D{r}-E{r}"
    ws.merge_cells(f"B{r}:C{r}")
    for col in "BCDEFG":
        c = ws[f"{col}{r}"]
        c.fill = fill(CARD)
        c.border = UNDER
        c.font = font(9.5, color=INK)
        if col in "DEFG":
            c.number_format = FMT["money"]
            c.alignment = Alignment(horizontal="right")
    ws.row_dimensions[r].height = 17
ws.conditional_formatting.add(f"G{R0 + 2}:G{R0 + 1 + NCAT}", FormulaRule(formula=[f"G{R0 + 2}<0"], font=Font(color="A23B2A", bold=True)))
dn = DoughnutChart()
dn.title = "Planned spend by category"
dn.add_data(Reference(ws, min_col=5, min_row=R0 + 1, max_row=R0 + 1 + NCAT), titles_from_data=True)
dn.set_categories(Reference(ws, min_col=2, min_row=R0 + 2, max_row=R0 + 1 + NCAT))
palette = [ROSE, SAGE, GOLD, DEEP, "E0B8B1", "B9C8B8", "E3CF9E", "8C7A84", "D9A39B", "A3B5A2", "D4B97A", "6F5F68",
           "EBD0CB", "CBD7CA", "EEDDB6", "A8999F", "C9A9A4", "9AAE9A"]
s = dn.series[0]
for i, colr in enumerate(palette[:NCAT]):
    pt = DataPoint(idx=i)
    pt.graphicalProperties.solidFill = colr
    pt.graphicalProperties.line.solidFill = "FFFFFF"
    s.dPt.append(pt)
dn.holeSize = 55
dn.legend.position = "r"
dn.legend.overlay = False
dn.height, dn.width = 9.5, 16.5
dn.roundedCorners = False
ws.add_chart(dn, f"I{R0}")

# --- cash flow by month (B..E) + bar chart, RSVP & meals (I..P)
R1 = R0 + NCAT + 4
dash_section(f"B{R1}", "Payments by month")
for col, h in zip("BCDE", ["Month", "", cur_h("Paid"), cur_h("Still due")]):
    ws[f"{col}{R1 + 1}"] = h
for col in "BCDE":
    c = ws[f"{col}{R1 + 1}"]
    c.font = font(9, bold=True, color="FFFFFF")
    c.fill = fill(SAGE)
    c.alignment = Alignment(horizontal="center", vertical="center")
ws.merge_cells(f"B{R1 + 1}:C{R1 + 1}")
PY_DPAID = rng("Payment Schedule", "J", Y0, Y1)
NM = 12
for k in range(NM):
    r = R1 + 2 + k
    ws[f"B{r}"] = f"=EDATE(DATE(YEAR(TODAY_D),MONTH(TODAY_D),1),{k - 5})"
    ws[f"B{r}"].number_format = FMT["month"]
    ws.merge_cells(f"B{r}:C{r}")
    ws[f"D{r}"] = f'=SUMIFS({PY_AMT},{PY_PAID},"Yes",{PY_DPAID},">="&B{r},{PY_DPAID},"<"&EDATE(B{r},1))'
    ws[f"E{r}"] = f'=SUMIFS({PY_AMT},{PY_PAID},"<>Yes",{PY_DUE},">="&B{r},{PY_DUE},"<"&EDATE(B{r},1))'
    for col in "BCDE":
        c = ws[f"{col}{r}"]
        c.fill = fill(CARD)
        c.border = UNDER
        c.font = font(9.5, color=INK)
        if col in "DE":
            c.number_format = FMT["money"]
    ws.row_dimensions[r].height = 17
ws[f"B{R1 + 2 + NM}"] = "Earlier unpaid (overdue)"
ws[f"E{R1 + 2 + NM}"] = f'=SUMIFS({PY_AMT},{PY_PAID},"<>Yes",{PY_DUE},"<"&B{R1 + 2})'
ws[f"E{R1 + 2 + NM}"].number_format = FMT["money"]
for cc in (f"B{R1 + 2 + NM}", f"E{R1 + 2 + NM}"):
    ws[cc].font = font(9, italic=True, color="A23B2A")
bc = BarChart()
bc.type, bc.grouping, bc.overlap = "col", "stacked", 100
bc.title = "Payments by month"
for col, colr in ((4, SAGE), (5, ROSE)):
    bc.add_data(Reference(ws, min_col=col, min_row=R1 + 1, max_row=R1 + 1 + NM), titles_from_data=True)
    bc.series[-1].graphicalProperties.solidFill = colr
    bc.series[-1].graphicalProperties.line.solidFill = colr
bc.set_categories(Reference(ws, min_col=2, min_row=R1 + 2, max_row=R1 + 1 + NM))
bc.x_axis.number_format = "mmm yy"
bc.y_axis.numFmt = "#,##0"
bc.y_axis.majorGridlines = None
bc.legend.position = "b"
bc.legend.overlay = False
bc.x_axis.delete = False
bc.y_axis.delete = False
bc.height, bc.width = 7.2, 12.5
bc.roundedCorners = False
bc.gapWidth = 60
ws.add_chart(bc, f"B{R1 + NM + 4}")

dash_section(f"I{R1}", "RSVPs & meals")
rs = [("Invited (people)", f"={G_INV}"), ("Attending", f"={G_ATTS}"), ("Declined", f"={G_DEC}"),
      ("Awaiting reply", f"={G_INV}-{G_ATTS}-{G_DEC}"), ("Response rate", f'=IF({G_INV}=0,"",({G_ATTS}+{G_DEC})/{G_INV})'),
      ("Target guest count", "=N(GUESTS_TARGET)")]
G_MEAL, G_MEAL2, G_PLUS = rng("Guest List", "Q", G0, G1), rng("Guest List", "R", G0, G1), rng("Guest List", "E", G0, G1)
for i, (lbl, f) in enumerate(rs):
    r = R1 + 1 + i
    ws[f"I{r}"] = lbl
    ws.merge_cells(f"I{r}:K{r}")
    ws[f"L{r}"] = f
    ws[f"L{r}"].number_format = FMT["pct"] if lbl == "Response rate" else FMT["int"]
    for col in "IJKL":
        ws[f"{col}{r}"].fill = fill(CARD)
        ws[f"{col}{r}"].border = UNDER
    ws[f"I{r}"].font = font(9.5, color=INK)
    ws[f"L{r}"].font = font(10, bold=True, color=DEEP)
    ws[f"L{r}"].alignment = Alignment(horizontal="right")
ws[f"N{R1 + 1}"] = "Meal"
ws[f"P{R1 + 1}"] = "Count"
for col in "NOP":
    ws[f"{col}{R1 + 1}"].font = font(9, bold=True, color="FFFFFF")
    ws[f"{col}{R1 + 1}"].fill = fill(SAGE)
ws.merge_cells(f"N{R1 + 1}:O{R1 + 1}")
for i, meal in enumerate(simple["I"][1]):
    r = R1 + 2 + i
    ws[f"N{r}"] = meal
    ws.merge_cells(f"N{r}:O{r}")
    ws[f"P{r}"] = (f'=COUNTIFS({G_RSVP},"Attending",{G_MEAL},N{r})'
                   f'+COUNTIFS({G_RSVP},"Attending",{G_PLUS},"Yes",{G_MEAL2},N{r})')
    ws[f"P{r}"].number_format = FMT["int"]
    for col in "NOP":
        ws[f"{col}{r}"].fill = fill(CARD)
        ws[f"{col}{r}"].border = UNDER
        ws[f"{col}{r}"].font = font(9.5, color=INK)
    ws[f"P{r}"].alignment = Alignment(horizontal="right")
rr = R1 + 2 + len(simple["I"][1])
ws[f"N{rr}"] = "Meal not chosen yet"
ws[f"P{rr}"] = f"={G_ATTS}-SUM(P{R1 + 2}:P{rr - 1})"
for col in "NP":
    ws[f"{col}{rr}"].font = font(9, italic=True, color=MUTED)
ws[f"I{R1 + 9}"] = "Thank-you cards still to send"
ws.merge_cells(f"I{R1 + 9}:K{R1 + 9}")
G_GIFT, G_TY = rng("Guest List", "U", G0, G1), rng("Guest List", "V", G0, G1)
ws[f"L{R1 + 9}"] = f'=COUNTIFS({G_GIFT},"<>",{G_TY},"<>Yes")'
ws[f"I{R1 + 10}"] = "Seated / attending"
ws.merge_cells(f"I{R1 + 10}:K{R1 + 10}")
ws[f"L{R1 + 10}"] = f"=SUM({rng('Seating Chart', 'E', T0, T1)})&\" / \"&{G_ATTS}"
for r in (R1 + 9, R1 + 10):
    for col in "IJKL":
        ws[f"{col}{r}"].fill = fill(CARD)
        ws[f"{col}{r}"].border = UNDER
    ws[f"I{r}"].font = font(9.5, color=INK)
    ws[f"L{r}"].font = font(10, bold=True, color=DEEP)
    ws[f"L{r}"].alignment = Alignment(horizontal="right")
ws.freeze_panes = "A4"
ws.protection.sheet = True
ws.protection.formatColumns = False
ws.protection.formatRows = False

# ------------------------------------------------------------------ print setup + finish
for n in SHEETS[:-1]:
    w = W[n]
    w.page_setup.orientation = "landscape"
    w.page_setup.fitToWidth = 1
    w.page_setup.fitToHeight = 0
    w.sheet_properties.pageSetUpPr.fitToPage = True
    w.print_options.horizontalCentered = True
    w.page_margins.left = w.page_margins.right = 0.4
ACTIVE = 0 if BLANK else 1
wb.active = ACTIVE
for i, n in enumerate(SHEETS):
    W[n].sheet_view.tabSelected = (i == ACTIVE)
wb.properties.title = "Wedding Planner"
wb.properties.creator = "NexaGlobe"
import os
os.makedirs("output", exist_ok=True)
wb.save(OUT)
print("saved", OUT)
