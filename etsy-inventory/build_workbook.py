"""Build the Maker's Inventory & Profit System workbook (.xlsx).

Compatibility rules: Excel 2016-365 + Google Sheets. Only SUMIFS, COUNTIF(S),
SUMPRODUCT, INDEX/MATCH, IFERROR, IF/AND/OR, MIN/MAX, ROUND(UP), DATE, EOMONTH,
EDATE, TODAY, FIXED. No XLOOKUP/FILTER/LET/IFS/MAXIFS/AGGREGATE/tables.

Run:  python3 build_workbook.py  ->  output/Makers_Inventory_Profit_System.xlsx
"""
from datetime import date

from openpyxl import Workbook
from openpyxl.chart import BarChart, DoughnutChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.series import DataPoint
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.styles.numbers import NumberFormat
from openpyxl.formatting.rule import Rule
from openpyxl.utils import get_column_letter as CL
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

import sample_data as sd

OUT = "output/Makers_Inventory_Profit_System.xlsx"

# ------------------------------------------------------------------ design tokens (Theme A)
BG, CARD, SAND, SAGE, DEEP, CLAY = "FAF7F2", "FFFFFF", "E9DFCF", "7C9A82", "3F5A48", "C98B6B"
INK, MUTED, INPUT, INPUT_BD, DD, CALC_TXT = "2B2B2B", "8A8A80", "FFF6E0", "E8D9B0", "EEF3EF", "5B5B55"
LINE, GOLD, MIST = "EFE8DC", "D9B77E", "A9B8AE"
HEAD_FONT, BODY_FONT = "Georgia", "Calibri"
BADGES = {
    "IN STOCK": ("DCEBDF", "3F7A4F"),
    "REORDER SOON": ("FBEFD3", "9A6B00"),
    "ON ORDER": ("E3EAF2", "3D5A80"),
    "CRITICAL": ("F6DAD3", "A8402B"),
    "OUT OF STOCK": ("3A3A3A", "FFFFFF"),
}
CURRENCIES = [("USD", "$", "US Dollar"), ("EUR", "€", "Euro"), ("GBP", "£", "British Pound"),
              ("CAD", "CA$", "Canadian Dollar"), ("AUD", "AU$", "Australian Dollar")]

# data-row capacities
S0, S1 = 6, 1505      # Sales
P0, P1 = 6, 105       # Products
M0, M1 = 6, 155       # Materials
R0, R1 = 6, 505       # Recipes
L0, L1 = 6, 1005      # Stock Log
E0, E1 = 6, 1005      # Expenses


def fill(c):
    return PatternFill("solid", start_color=c, end_color=c)


def side(c, style="thin"):
    return Side(style=style, color=c)


THIN_LINE = Border(bottom=side(LINE))
INPUT_BORDER = Border(left=side(INPUT_BD), right=side(INPUT_BD), top=side(INPUT_BD), bottom=side(INPUT_BD))
UNLOCK = Protection(locked=False)

FMT = {
    "money": "#,##0.00;-#,##0.00;\"–\"",
    "money0": "#,##0;-#,##0;\"–\"",
    "int": "#,##0;-#,##0;\"–\"",
    "qty": "#,##0.##;-#,##0.##;\"–\"",
    "pct": "0.0%;-0.0%;\"–\"",
    "date": "mmm d, yyyy",
    "days": "[>=9999]\"∞\";#,##0",
    "dec": "#,##0.00",
    "cost4": "#,##0.0000",
    "text": "@",
    "gen": "General",
}


def font(size=10, bold=False, color=INK, name=BODY_FONT, italic=False, underline=None):
    return Font(name=name, size=size, bold=bold, color=color, italic=italic, underline=underline)


wb = Workbook()
wb.remove(wb.active)
SHEETS = ["Start Here", "Dashboard", "Sales", "Products", "Materials", "Recipes", "Stock Log", "Expenses", "Reports"]
TAB_COLORS = [DEEP, CLAY, SAGE, SAGE, SAGE, SAGE, SAGE, GOLD, DEEP]
ws_ = {}
for n, c in zip(SHEETS, TAB_COLORS):
    w = wb.create_sheet(n)
    w.sheet_properties.tabColor = c
    w.sheet_view.showGridLines = False
    w.sheet_view.zoomScale = 90
    ws_[n] = w
START, DASH, SALES, PROD, MATS, RECI, LOG, EXP, REP = (ws_[n] for n in SHEETS)


def q(sheet):
    return f"'{sheet}'" if " " in sheet else sheet


def name(nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


MONEY_RANGES = {}  # (sheet, decimals) -> list of ranges that get the currency CF


def money_range(ws, rng, dec=2):
    MONEY_RANGES.setdefault((ws.title, dec), []).append(rng)


def cur_header(label):
    """Header text that shows the active currency symbol, e.g. Unit Price ($)."""
    return f'="{label} ("&CUR_SYM&")"'


# ------------------------------------------------------------------ generic data-sheet builder
def data_sheet(ws, title, desc, cols, first, last, freeze_col="B", hidden=()):
    """cols: list of dict(h, w, kind in input|dd|calc|helper, fmt, f (formula template with {r}), money)."""
    ws.row_dimensions[1].height = 8
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 30
    ws.row_dimensions[4].height = 18
    ws.row_dimensions[5].height = 34
    ws["A2"] = title
    ws["A2"].font = font(18, True, DEEP, HEAD_FONT)
    ws["A2"].alignment = Alignment(vertical="center")
    ws["A3"] = desc
    ws["A3"].font = font(10, False, MUTED, italic=True)
    ws["A3"].alignment = Alignment(vertical="top", wrap_text=False)
    # legend chips row 4
    chips = [("Type here", INPUT, INK), ("Pick ▼", DD, DEEP), ("Auto (locked)", CARD, CALC_TXT)]
    col = 1
    for text, bg, fg in chips:
        c = ws.cell(4, col, text)
        c.fill = fill(bg)
        c.font = font(8, True, fg)
        c.alignment = Alignment(horizontal="center", vertical="center", shrink_to_fit=True)
        c.border = INPUT_BORDER
        col += 1
    # nav links (right side of row 2)
    nav_col = len(cols) - 1
    for i, (lbl, tgt) in enumerate([("⌂ Start", "Start Here"), ("▦ Dashboard", "Dashboard")]):
        c = ws.cell(2, nav_col + i, lbl)
        c.hyperlink = f"#{q(tgt)}!A1"
        c.font = font(9, True, SAGE, underline="single")
        c.alignment = Alignment(horizontal="center", vertical="center")

    for j, cd in enumerate(cols, start=1):
        L = CL(j)
        ws.column_dimensions[L].width = cd["w"]
        h = ws.cell(5, j, cur_header(cd["h"]) if cd.get("money") else cd["h"])
        kind = cd["kind"]
        if kind in ("input", "dd"):
            h.fill, h.font = fill(DEEP), font(10, True, "FFFFFF")
        elif kind == "helper":
            h.fill, h.font = fill(LINE), font(8, False, MUTED, italic=True)
        else:
            h.fill, h.font = fill(SAND), font(10, True, DEEP)
        h.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        h.border = Border(bottom=side(DEEP, "medium"))
        nf = FMT[cd.get("fmt", "gen")]
        al = Alignment(horizontal=cd.get("align", "right" if cd.get("fmt") not in ("text", "gen", None) else "left"),
                       vertical="center")
        for r in range(first, last + 1):
            c = ws.cell(r, j)
            if kind in ("calc", "helper"):
                c.value = cd["f"].format(r=r)
                c.font = font(10, kind == "calc" and cd.get("bold", False), CALC_TXT if kind == "calc" else MUTED)
                c.border = THIN_LINE
            else:
                c.fill = fill(INPUT if kind == "input" else DD)
                c.font = font(10, False, INK)
                c.protection = UNLOCK
                c.border = Border(bottom=side("F3EBDB"))
            c.number_format = nf
            c.alignment = al
        if cd.get("money"):
            money_range(ws, f"{L}{first}:{L}{last}")
        if kind == "helper" or L in hidden:
            ws.column_dimensions[L].hidden = True
    ws.freeze_panes = f"{freeze_col}{first}"
    lastcol = CL(len(cols))
    ws.auto_filter.ref = f"A5:{lastcol}{last}"
    ws.print_title_rows = "5:5"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.3
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.oddFooter.center.text = "&A  ·  Page &P of &N"
    ws.oddFooter.center.size = 8


def add_dv(ws, formula, rng, prompt=None, title=None, allow_blank=True):
    dv = DataValidation(type="list", formula1=formula, allow_blank=allow_blank, showDropDown=False)
    dv.error = "Please pick a value from the list (edit the list on Start Here to add options)."
    dv.errorTitle = "Not in list"
    dv.showErrorMessage = True
    if prompt:
        dv.prompt, dv.promptTitle, dv.showInputMessage = prompt, title or "Tip", True
    ws.add_data_validation(dv)
    dv.add(rng)


def add_num_dv(ws, rng, prompt, title, kind="decimal", minimum=0):
    dv = DataValidation(type=kind, operator="greaterThanOrEqual", formula1=str(minimum), allow_blank=True)
    dv.error, dv.errorTitle, dv.showErrorMessage = "Please enter a number (0 or more).", "Numbers only", True
    dv.prompt, dv.promptTitle, dv.showInputMessage = prompt, title, True
    ws.add_data_validation(dv)
    for part in rng.split():
        dv.add(part)


def add_date_dv(ws, rng, prompt="Enter a date, e.g. 3/15/2026"):
    dv = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True)
    dv.error, dv.errorTitle, dv.showErrorMessage = "Please enter a valid date.", "Date needed", True
    dv.prompt, dv.promptTitle, dv.showInputMessage = prompt, "Date", True
    ws.add_data_validation(dv)
    dv.add(rng)


def badge_cf(ws, rng):
    for txt, (bg, fg) in BADGES.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{txt}"'],
                                                      fill=fill(bg), font=Font(bold=True, color=fg)))


def neg_red(ws, rng):
    ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], font=Font(color="A8402B")))


# ================================================================== START HERE
st = START
widths = {"A": 2, "B": 39, "C": 26, "D": 14, "E": 14, "F": 14, "G": 14, "H": 14, "I": 14, "J": 3,
          "K": 18, "L": 21, "M": 21, "N": 18, "O": 20, "P": 20}
for k, v in widths.items():
    st.column_dimensions[k].width = v
for r in range(1, 90):
    for c in range(1, 17):
        st.cell(r, c).fill = fill(BG)
st.row_dimensions[1].height = 10
st.merge_cells("B2:I2")
st["B2"] = "Maker's Inventory & Profit System"
st["B2"].font = font(24, True, DEEP, HEAD_FONT)
st.row_dimensions[2].height = 38
st.merge_cells("B3:I3")
st["B3"] = "Inventory  ·  Recipes (BOM)  ·  Demand Forecasting  ·  True Etsy Profit  ·  Tax-Ready Books"
st["B3"].font = font(11, False, CLAY, italic=True)
st.row_dimensions[3].height = 20


def section(ws, r, text, c1="B", c2="I"):
    ws.merge_cells(f"{c1}{r}:{c2}{r}")
    c = ws[f"{c1}{r}"]
    c.value = text
    c.font = font(13, True, DEEP, HEAD_FONT)
    c.alignment = Alignment(vertical="center")
    for col in range(ws[f"{c1}{r}"].column, ws[f"{c2}{r}"].column + 1):
        ws.cell(r, col).border = Border(bottom=side(SAGE, "medium"))
    ws.row_dimensions[r].height = 26


section(st, 5, "①  CONTROL PANEL  —  set these once")
controls = [
    ("Business Name", "Ember & Sage Candle Co.", "text", None, "Shown on the Dashboard header."),
    ("Currency", "USD", "text", "CUR_CODES", "Pick USD, EUR, GBP, CAD or AUD. Every money column & KPI updates."),
    ("Currency Symbol (auto)", "=IFERROR(INDEX(CUR_SYMS,MATCH(C7,CUR_CODES,0)),\"$\")", "text", "calc", "Calculated from your currency choice."),
    ("Fiscal / Tax Year", 2026, "gen", None, "Reports & the tax summary use this year."),
    ("Tax Region", "US (IRS Schedule C)", "text", '"US (IRS Schedule C),UK (HMRC SA103)"', "Both mappings are always shown on Reports; this sets the headline."),
    ("Report Date  (leave blank = today)", date(2026, 11, 20), "date", None, "Forecasts count from this date. Clear it to use today's date automatically."),
    ("Report Date in use (auto)", "=IF(C11=\"\",TODAY(),C11)", "date", "calc", "Used by all forecasts."),
    ("Deduct Materials When", "Produced", "text", '"Produced,Sold"', "Produced = you make stock ahead (log batches). Sold = you make to order."),
    ("Sales Lookback (days)", 90, "int", None, "Average daily sales are measured over this many days."),
    ("Default Safety Stock (days)", 14, "int", None, "Extra cover kept on hand. Override per item on Products/Materials."),
    ("Reorder Coverage (days)", 30, "int", None, "How many days of demand each reorder / batch should cover."),
    ("Your Labor Rate (per hour)", 18, "dec", None, "Added to unit cost for true pricing. Set 0 to leave labor out."),
    ("Target Profit Margin", 0.35, "pct", None, "Used for the 'Price for Target Margin' suggestion on Products."),
]
for i, (lbl, val, fmt, dv, hint) in enumerate(controls):
    r = 6 + i
    st.row_dimensions[r].height = 20
    a = st.cell(r, 2, lbl)
    a.font = font(10, True, INK)
    a.alignment = Alignment(vertical="center")
    c = st.cell(r, 3, val)
    c.number_format = FMT[fmt] if fmt != "gen" else "0"
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = INPUT_BORDER
    if dv == "calc":
        c.fill, c.font = fill(CARD), font(10, True, CALC_TXT)
    else:
        c.fill = fill(DD if dv else INPUT)
        c.font = font(10, True, INK)
        c.protection = UNLOCK
        if dv:
            add_dv(st, dv, f"C{r}")
    st.merge_cells(f"D{r}:I{r}")
    h = st.cell(r, 4, hint)
    h.font = font(9, False, MUTED, italic=True)
    h.alignment = Alignment(vertical="center", indent=1)
add_num_dv(st, "C14:C17", "Whole days or an hourly rate. Numbers only.", "Number")
add_num_dv(st, "C18", "Enter a percentage, e.g. 35%", "Target margin", minimum=0)
add_date_dv(st, "C11", "Leave blank to always use today's date.")
for nm, cell in [("BIZ_NAME", "C6"), ("CUR_CODE", "C7"), ("CUR_SYM", "C8"), ("FY", "C9"), ("TAX_REGION", "C10"),
                 ("ASOF", "C12"), ("MODE", "C13"), ("LOOKBACK", "C14"), ("SAFETY_DAYS", "C15"),
                 ("COVER_DAYS", "C16"), ("LABOR_RATE", "C17"), ("TARGET_MARGIN", "C18")]:
    name(nm, f"'Start Here'!${cell[0]}${cell[1:]}")

# --- channel fee table
section(st, 20, "②  CHANNEL FEES  —  verify against each platform's fee page once a year")
fee_hdr = ["Sales Channel", "Listing Fee\n(per item sold)", "Transaction %", "Payment\nProcessing %",
           "Processing Fixed\n(per order)", "Offsite Ads %", "Ads Cap\n(per order)", "Other %\n(e.g. regulatory)"]
for j, t in enumerate(fee_hdr):
    c = st.cell(21, 2 + j, t)
    c.fill, c.font = fill(DEEP), font(9, True, "FFFFFF")
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
st.row_dimensions[21].height = 32
fees = [
    ("Etsy", 0.20, 0.065, 0.03, 0.25, 0.15, 100, 0),
    ("Shopify", 0, 0, 0.029, 0.30, 0, 0, 0),
    ("Amazon Handmade", 0, 0.15, 0, 0, 0, 0, 0),
    ("Wholesale", 0, 0, 0, 0, 0, 0, 0),
    ("Markets & Fairs", 0, 0, 0.026, 0.15, 0, 0, 0),
    ("Website / Direct", 0, 0, 0.029, 0.30, 0, 0, 0),
    ("", None, None, None, None, None, None, None),
    ("", None, None, None, None, None, None, None),
]
fee_fmt = ["text", "money", "pct", "pct", "money", "pct", "money", "pct"]
for i, row in enumerate(fees):
    r = 22 + i
    st.row_dimensions[r].height = 19
    for j, v in enumerate(row):
        c = st.cell(r, 2 + j, v)
        c.fill = fill(INPUT)
        c.font = font(10, j == 0, INK)
        c.border = INPUT_BORDER
        c.number_format = FMT[fee_fmt[j]] if j else "@"
        c.alignment = Alignment(horizontal="left" if j == 0 else "center", vertical="center")
        c.protection = UNLOCK
money_range(st, "C22:C29")
money_range(st, "F22:F29")
money_range(st, "H22:H29")
for nm, col in [("FEE_CH", "B"), ("FEE_LIST", "C"), ("FEE_TX", "D"), ("FEE_PROC", "E"), ("FEE_FIX", "F"),
                ("FEE_ADS", "G"), ("FEE_CAP", "H"), ("FEE_OTH", "I")]:
    name(nm, f"'Start Here'!${col}$22:${col}$29")
st.merge_cells("B30:I31")
st["B30"] = ("Row 1 (Etsy) is treated as your MAIN channel for per-unit pricing on the Products tab. Defaults are typical "
             "US rates at the time of writing and are examples only. Check etsy.com/legal/fees, your Shopify plan and Amazon "
             "Handmade referral fees, then type your own rates. Rename or add channels in the 2 blank rows; the Sales dropdown updates automatically.")
st["B30"].font = font(9, False, MUTED, italic=True)
st["B30"].alignment = Alignment(wrap_text=True, vertical="top")
st.row_dimensions[30].height = 22
st.row_dimensions[31].height = 22

# --- how to use
section(st, 33, "③  HOW TO USE  —  5 steps")
steps = [
    ("1", "Control Panel & Fees", "Set your business name, currency, tax year and channel fee rates above."),
    ("2", "Products & Materials", "List every finished product (SKU) on Products and every supply on Materials, with opening stock."),
    ("3", "Recipes (BOM)", "For each product, list the materials one unit uses (e.g. 200 g wax, 1 jar, 1 wick). Unit costs build themselves."),
    ("4", "Log as you go", "Sales: one row per item sold.  Stock Log: production batches, supply purchases, returns, damage.  Expenses: business costs."),
    ("5", "Read the results", "Dashboard = KPIs, charts & what to reorder.  Reports = monthly P&L, Schedule C / HMRC summary & COGS."),
]
for i, (n_, t, d) in enumerate(steps):
    r = 34 + i
    st.row_dimensions[r].height = 30
    c = st.cell(r, 2, f"  {n_}   {t}")
    c.font = font(11, True, "FFFFFF")
    c.fill = fill(SAGE if i % 2 == 0 else DEEP)
    c.alignment = Alignment(vertical="center")
    st.merge_cells(f"C{r}:I{r}")
    c = st.cell(r, 3, d)
    c.font = font(10, False, INK)
    c.fill = fill(CARD)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)

# --- legend
section(st, 40, "④  COLOR LEGEND  —  you can't break it")
legend = [
    (INPUT, INK, "Type here", "Cream cells are yours: type, paste or delete freely."),
    (DD, DEEP, "Pick from list ▼", "Green-tint cells have a dropdown. Edit the lists on the right to add options."),
    (CARD, CALC_TXT, "Auto-calculated", "White cells hold formulas and are locked, so they can't be overwritten by accident."),
    (BADGES["IN STOCK"][0], BADGES["IN STOCK"][1], "IN STOCK", "Above reorder point."),
    (BADGES["REORDER SOON"][0], BADGES["REORDER SOON"][1], "REORDER SOON", "At or below reorder point: order / produce now to avoid a stockout."),
    (BADGES["ON ORDER"][0], BADGES["ON ORDER"][1], "ON ORDER", "Low, but an open purchase order covers it (materials)."),
    (BADGES["CRITICAL"][0], BADGES["CRITICAL"][1], "CRITICAL", "Below safety stock: you will likely run out before new stock arrives."),
    (BADGES["OUT OF STOCK"][0], BADGES["OUT OF STOCK"][1], "OUT OF STOCK", "Zero or negative on hand. Pause the listing or make more."),
]
for i, (bg, fg, t, d) in enumerate(legend):
    r = 41 + i
    st.row_dimensions[r].height = 19
    c = st.cell(r, 2, t)
    c.fill, c.font, c.border = fill(bg), font(9, True, fg), INPUT_BORDER
    c.alignment = Alignment(horizontal="center", vertical="center")
    st.merge_cells(f"C{r}:I{r}")
    c = st.cell(r, 3, d)
    c.font = font(10, False, INK)
    c.alignment = Alignment(vertical="center", indent=1)
st.merge_cells("B49:I49")
st["B49"] = ("Sheets are protected WITHOUT a password so formulas stay safe. To customise a formula: Review > Unprotect Sheet "
             "(Google Sheets ignores protection). Re-protect afterwards: Review > Protect Sheet.")
st["B49"].font = font(9, False, MUTED, italic=True)
st["B49"].alignment = Alignment(wrap_text=True, vertical="top")
st.row_dimensions[49].height = 28

# --- reset guide
section(st, 51, "⑤  RESET SAMPLE DATA IN 60 SECONDS")
st.merge_cells("B52:I52")
st["B52"] = ("For each row: click the Name Box (left of the formula bar), paste the range, press Enter, then press Delete. "
             "Only cream / green input cells are cleared, so every formula keeps working.")
st["B52"].font = font(10, False, INK)
st["B52"].alignment = Alignment(wrap_text=True, vertical="center")
st.row_dimensions[52].height = 30
reset = [
    ("Sales", f"A{S0}:L{S1}"),
    ("Stock Log", f"A{L0}:L{L1}"),
    ("Expenses", f"A{E0}:H{E1}"),
    ("Recipes", f"A{R0}:D{R1}"),
    ("Products", f"A{P0}:H{P1}"),
    ("Materials", f"A{M0}:J{M1}"),
    ("Reports (COGS inputs)", "D76, D78:D80, E82"),
    ("Start Here", "C6, C11  (business name + report date)"),
]
for j, t in enumerate(["Tab", "Range to paste in the Name Box"]):
    c = st.cell(53, 2 + j, t)
    c.fill, c.font = fill(SAND), font(9, True, DEEP)
st.merge_cells("C53:I53")
for i, (tab, rng) in enumerate(reset):
    r = 54 + i
    st.row_dimensions[r].height = 18
    c = st.cell(r, 2, tab)
    c.font = font(10, True, INK)
    c.hyperlink = f"#{q(tab.split(' (')[0])}!A1"
    st.merge_cells(f"C{r}:I{r}")
    c = st.cell(r, 3, rng)
    c.font = Font(name="Consolas", size=10, color=DEEP)
    for col in range(2, 10):
        st.cell(r, col).border = THIN_LINE
st.merge_cells("B62:I63")
st["B62"] = ("Tip: clear Sales, Stock Log & Expenses first, then Recipes, Products and Materials. Tax-year setup: change "
             "'Fiscal / Tax Year' and enter your opening inventory on Reports. Need more rows? Unprotect the sheet, copy the "
             "last row's formulas down, and extend the dropdown ranges.")
st["B62"].font = font(9, False, MUTED, italic=True)
st["B62"].alignment = Alignment(wrap_text=True, vertical="top")
st.row_dimensions[62].height = 20
st.row_dimensions[63].height = 20

# --- compatibility / FAQ
section(st, 65, "⑥  COMPATIBILITY & GOOD TO KNOW")
faq = [
    ("Works in", "Microsoft Excel 2016, 2019, 2021, 365 (Windows & Mac) and Google Sheets (File > Import or open from Drive)."),
    ("Currency in Google Sheets", "Headers and KPI cards show your symbol. Number cells show plain amounts (Sheets can't switch formats by formula)."),
    ("Multi-item orders", "Enter one row per item with the SAME Order ID. Fixed processing fees are charged once per order automatically."),
    ("Refunds", "Set Status = Refunded: revenue & transaction fee drop to 0; processing fee, listing fee and label cost stay as a loss."),
    ("Tax disclaimer", "Category mapping is a bookkeeping aid, not tax advice. Confirm with your accountant / tax adviser."),
]
for i, (t, d) in enumerate(faq):
    r = 66 + i
    st.row_dimensions[r].height = 30
    c = st.cell(r, 2, t)
    c.font = font(10, True, DEEP)
    c.alignment = Alignment(vertical="center")
    st.merge_cells(f"C{r}:I{r}")
    c = st.cell(r, 3, d)
    c.font = font(10, False, INK)
    c.alignment = Alignment(vertical="center", wrap_text=True)
    for col in range(2, 10):
        st.cell(r, col).border = THIN_LINE

# --- dropdown lists (right side)
section(st, 5, "DROPDOWN LISTS  —  edit freely", "K", "P")
for j, t in enumerate(["Currency Code", "Symbol", "Currency Name"]):
    c = st.cell(6, 11 + j, t)
    c.fill, c.font = fill(SAND), font(9, True, DEEP)
for i, (code, sym, nm) in enumerate(CURRENCIES):
    for j, v in enumerate((code, sym, nm)):
        c = st.cell(7 + i, 11 + j, v)
        c.font = font(10)
        c.border = THIN_LINE
name("CUR_CODES", "'Start Here'!$K$7:$K$11")
name("CUR_SYMS", "'Start Here'!$L$7:$L$11")
lists = {
    "K": ("Dashboard Period", ["Full Year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], "PERIOD_LIST"),
    "L": ("Product Collections", ["Signature Candles", "Seasonal", "Wax Melts", "Diffusers", "Room & Linen", "Gift Sets"], "COLLECTIONS"),
    "M": ("Material Categories", ["Wax", "Fragrance Oil", "Wick", "Vessel", "Diffuser Parts", "Labels", "Packaging", "Dye / Colorant"], "MAT_CATS"),
    "N": ("Units", ["g", "kg", "oz", "lb", "ml", "L", "pcs", "sheets", "m"], "UNITS"),
    "O": ("Payment Methods", ["Business Credit Card", "Business Debit Card", "Bank Transfer", "PayPal", "Cash", "Personal Card"], "PAY_METHODS"),
}
for col, (title, items, nm) in lists.items():
    c = st[f"{col}14"]
    c.value = title
    c.fill, c.font = fill(SAND), font(9, True, DEEP)
    for i in range(20):
        cell = st[f"{col}{15 + i}"]
        cell.value = items[i] if i < len(items) else None
        cell.font = font(10)
        cell.border = THIN_LINE
        if col != "K":
            cell.fill = fill(INPUT)
            cell.protection = UNLOCK
    end = 15 + (len(items) - 1 if col == "K" else 19)
    name(nm, f"'Start Here'!${col}$15:${col}${end}")
name("MONTHS", "'Start Here'!$K$16:$K$27")
st.merge_cells("K36:P38")
st["K36"] = "Add your own options in the blank cream cells under each list. They appear in the dropdowns right away."
st["K36"].font = font(9, False, MUTED, italic=True)
st["K36"].alignment = Alignment(wrap_text=True, vertical="top")
st.freeze_panes = "A5"
st.print_area = "B2:I71"
st.page_setup.orientation = "portrait"
st.page_setup.fitToWidth = 1
st.page_setup.fitToHeight = 0
st.sheet_properties.pageSetUpPr.fitToPage = True

# ================================================================== SALES
SR = lambda col: f"Sales!${col}${S0}:${col}${S1}"
LK = "MATCH($C{r},FEE_CH,0)"
sales_cols = [
    dict(h="Order Date", w=13, kind="input", fmt="date"),
    dict(h="Order ID", w=12, kind="input", fmt="text", align="left"),
    dict(h="Channel", w=17, kind="dd", fmt="text", align="left"),
    dict(h="SKU", w=11, kind="dd", fmt="text", align="left"),
    dict(h="Qty", w=7, kind="input", fmt="int"),
    dict(h="Unit Price", w=11, kind="input", fmt="money", money=True),
    dict(h="Discount", w=11, kind="input", fmt="money", money=True),
    dict(h="Shipping Charged", w=11, kind="input", fmt="money", money=True),
    dict(h="Sales Tax Collected", w=11, kind="input", fmt="money", money=True),
    dict(h="Offsite Ad?", w=9, kind="dd", fmt="text", align="center"),
    dict(h="Shipping Label Cost", w=11, kind="input", fmt="money", money=True),
    dict(h="Status", w=12, kind="dd", fmt="text", align="center"),
    dict(h="Product", w=34, kind="calc", fmt="text", align="left",
         f='=IF($D{r}="","",IFERROR(INDEX(Products!$B$6:$B$105,MATCH($D{r},SKU_LIST,0)),"⚠ Unknown SKU"))'),
    dict(h="Item Sales", w=11, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF($L{r}="Completed",$E{r}*$F{r},0))'),
    dict(h="Net Revenue", w=12, kind="calc", fmt="money", money=True, bold=True,
         f='=IF($A{r}="","",IF($L{r}="Completed",$Z{r},0))'),
    dict(h="Listing Fee", w=10, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF($L{r}="Cancelled",0,$E{r}*IFERROR(INDEX(FEE_LIST,' + LK + '),0)))'),
    dict(h="Transaction Fee", w=11, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF($L{r}="Completed",$Z{r}*IFERROR(INDEX(FEE_TX,' + LK + '),0),0))'),
    dict(h="Processing Fee", w=11, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF($L{r}="Cancelled",0,($Z{r}+$I{r})*IFERROR(INDEX(FEE_PROC,' + LK + '),0)+$Y{r}*IFERROR(INDEX(FEE_FIX,' + LK + '),0)))'),
    dict(h="Offsite Ads Fee", w=11, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF(AND($L{r}="Completed",$J{r}="Yes"),MIN($Z{r}*IFERROR(INDEX(FEE_ADS,' + LK + '),0),'
           'IF(IFERROR(INDEX(FEE_CAP,' + LK + '),0)>0,IFERROR(INDEX(FEE_CAP,' + LK + '),0),$Z{r})),0))'),
    dict(h="Other Fees", w=10, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF($L{r}="Completed",$Z{r}*IFERROR(INDEX(FEE_OTH,' + LK + '),0),0))'),
    dict(h="Total Fees", w=11, kind="calc", fmt="money", money=True, bold=True, f='=IF($A{r}="","",SUM(P{r}:T{r}))'),
    dict(h="COGS", w=11, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",IF($L{r}="Completed",$E{r}*IFERROR(INDEX(Products!$O$6:$O$105,MATCH($D{r},SKU_LIST,0)),0),0))'),
    dict(h="Net Profit", w=12, kind="calc", fmt="money", money=True, bold=True,
         f='=IF($A{r}="","",O{r}-U{r}-V{r}-IF($L{r}="Cancelled",0,$K{r}))'),
    dict(h="Margin %", w=9, kind="calc", fmt="pct", f='=IF($A{r}="","",IF(O{r}=0,"",W{r}/O{r}))'),
    dict(h="First line of order", w=8, kind="helper", fmt="int",
         f='=IF($A{r}="","",IF(COUNTIF($B$6:$B{r},$B{r})=1,1,0))'),
    dict(h="Fee base", w=8, kind="helper", fmt="money", f='=IF($A{r}="","",$E{r}*$F{r}-$G{r}+$H{r})'),
]
data_sheet(SALES, "Sales & Orders",
           "One row per item sold. Use the same Order ID for multi-item orders. Fees, COGS and true net profit calculate automatically.",
           sales_cols, S0, S1, freeze_col="C")
add_date_dv(SALES, f"A{S0}:A{S1}")
add_dv(SALES, "FEE_CH", f"C{S0}:C{S1}", "Pick the sales channel (edit channels on Start Here).", "Channel")
add_dv(SALES, "SKU_LIST", f"D{S0}:D{S1}", "Pick a SKU from your Products tab.", "SKU")
add_dv(SALES, '"Yes,No"', f"J{S0}:J{S1}", "Yes if Etsy charged an Offsite Ads fee on this order.", "Offsite Ads")
add_dv(SALES, '"Completed,Refunded,Cancelled"', f"L{S0}:L{S1}", "Completed, Refunded or Cancelled.", "Status")
add_num_dv(SALES, f"E{S0}:I{S1} K{S0}:K{S1}", "Numbers only (0 or more).", "Amount")
badge_cf(SALES, f"L{S0}:L{S1}")
SALES.conditional_formatting.add(f"L{S0}:L{S1}", CellIsRule(operator="equal", formula=['"Refunded"'], font=Font(color="A8402B", bold=True)))
SALES.conditional_formatting.add(f"L{S0}:L{S1}", CellIsRule(operator="equal", formula=['"Cancelled"'], font=Font(color=MUTED, italic=True)))
neg_red(SALES, f"W{S0}:X{S1}")

# ================================================================== PRODUCTS
LOGR = lambda col: f"'Stock Log'!${col}${L0}:${col}${L1}"
prod_cols = [
    dict(h="SKU", w=11, kind="input", fmt="text", align="left"),
    dict(h="Product Name", w=34, kind="input", fmt="text", align="left"),
    dict(h="Collection", w=17, kind="dd", fmt="text", align="left"),
    dict(h="Retail Price", w=10, kind="input", fmt="money", money=True),
    dict(h="Opening Stock", w=9, kind="input", fmt="int"),
    dict(h="Labor Min / Unit", w=9, kind="input", fmt="int"),
    dict(h="Production Lead Time (days)", w=11, kind="input", fmt="int"),
    dict(h="Safety Days (blank = default)", w=11, kind="input", fmt="int"),
    dict(h="Produced", w=9, kind="calc", fmt="int",
         f=f'=IF($A{{r}}="","",SUMIFS({LOGR("E")},{LOGR("C")},$A{{r}},{LOGR("B")},"Production"))'),
    dict(h="Sold", w=8, kind="calc", fmt="int",
         f=f'=IF($A{{r}}="","",SUMIFS({SR("E")},{SR("D")},$A{{r}},{SR("L")},"<>Cancelled"))'),
    dict(h="Returns & Adjust.", w=9, kind="calc", fmt="int",
         f=f'=IF($A{{r}}="","",SUMIFS({LOGR("E")},{LOGR("C")},$A{{r}},{LOGR("B")},"Return to Stock")+SUMIFS({LOGR("E")},{LOGR("C")},$A{{r}},{LOGR("B")},"Adjustment")-SUMIFS({LOGR("E")},{LOGR("C")},$A{{r}},{LOGR("B")},"Damaged / Waste"))'),
    dict(h="On Hand", w=9, kind="calc", fmt="int", bold=True, f='=IF($A{r}="","",$E{r}+I{r}-J{r}+K{r})'),
    dict(h="Material Cost / Unit", w=11, kind="calc", fmt="money", money=True,
         f=f'=IF($A{{r}}="","",SUMIFS(Recipes!$H${R0}:$H${R1},Recipes!$A${R0}:$A${R1},$A{{r}}))'),
    dict(h="Labor Cost / Unit", w=10, kind="calc", fmt="money", money=True, f='=IF($A{r}="","",$F{r}/60*LABOR_RATE)'),
    dict(h="Unit Cost (COGS)", w=11, kind="calc", fmt="money", money=True, bold=True, f='=IF($A{r}="","",M{r}+N{r})'),
    dict(h="Stock Value", w=11, kind="calc", fmt="money", money=True, f='=IF($A{r}="","",MAX(0,L{r})*O{r})'),
    dict(h="Avg Daily Sales", w=9, kind="calc", fmt="dec",
         f=f'=IF($A{{r}}="","",SUMIFS({SR("E")},{SR("D")},$A{{r}},{SR("L")},"<>Cancelled",{SR("A")},">"&(ASOF-LOOKBACK),{SR("A")},"<="&ASOF)/LOOKBACK)'),
    dict(h="Days Left", w=8, kind="calc", fmt="days", f='=IF($A{r}="","",IF(L{r}<=0,0,IF(Q{r}=0,9999,ROUND(L{r}/Q{r},0))))'),
    dict(h="Est. Stockout Date", w=13, kind="calc", fmt="date", f='=IF($A{r}="","",IF(R{r}>=9999,"—",ASOF+R{r}))'),
    dict(h="Safety Stock", w=8, kind="calc", fmt="int", f='=IF($A{r}="","",ROUND(Q{r}*IF($H{r}="",SAFETY_DAYS,$H{r}),0))'),
    dict(h="Reorder Point", w=8, kind="calc", fmt="int", f='=IF($A{r}="","",ROUND(Q{r}*$G{r},0)+T{r})'),
    dict(h="Suggested Batch", w=9, kind="calc", fmt="int", bold=True,
         f='=IF($A{r}="","",IF(L{r}<=U{r},MAX(0,ROUNDUP(Q{r}*($G{r}+COVER_DAYS)+T{r}-L{r},0)),0))'),
    dict(h="Status", w=15, kind="calc", fmt="text", align="center",
         f='=IF($A{r}="","",IF(L{r}<=0,"OUT OF STOCK",IF(L{r}<=T{r},"CRITICAL",IF(L{r}<=U{r},"REORDER SOON","IN STOCK"))))'),
    dict(h="Profit / Unit on Main Channel", w=11, kind="calc", fmt="money", money=True,
         f='=IF($A{r}="","",$D{r}-$D{r}*(INDEX(FEE_TX,1)+INDEX(FEE_PROC,1)+INDEX(FEE_OTH,1))-INDEX(FEE_FIX,1)-INDEX(FEE_LIST,1)-O{r})'),
    dict(h="Margin on Main Channel", w=9, kind="calc", fmt="pct", f='=IF($A{r}="","",IFERROR(X{r}/$D{r},""))'),
    dict(h="Price for Target Margin", w=11, kind="calc", fmt="money", money=True, bold=True,
         f='=IF($A{r}="","",IFERROR((O{r}+INDEX(FEE_LIST,1)+INDEX(FEE_FIX,1))/(1-INDEX(FEE_TX,1)-INDEX(FEE_PROC,1)-INDEX(FEE_OTH,1)-TARGET_MARGIN),""))'),
    dict(h="urgency score", w=8, kind="helper", fmt="gen", f='=IF(OR($A{r}="",W{r}="IN STOCK"),"",R{r}+ROW()/100000)'),
    dict(h="urgency rank", w=8, kind="helper", fmt="gen", f=f'=IF(AA{{r}}="","",RANK(AA{{r}},$AA${P0}:$AA${P1},1))'),
    dict(h="period profit", w=8, kind="helper", fmt="dec",
         f=f'=IF($A{{r}}="","",SUMIFS({SR("W")},{SR("D")},$A{{r}},{SR("A")},">="&P_START,{SR("A")},"<="&P_END))'),
    dict(h="profit score", w=8, kind="helper", fmt="gen", f='=IF($A{r}="","",AC{r}+ROW()/1000000)'),
    dict(h="profit rank", w=8, kind="helper", fmt="gen", f=f'=IF(AD{{r}}="","",RANK(AD{{r}},$AD${P0}:$AD${P1},0))'),
    dict(h="material stock value", w=8, kind="helper", fmt="dec", f='=IF($A{r}="","",MAX(0,L{r})*M{r})'),
]
data_sheet(PROD, "Products  ·  Finished Goods & Demand Forecast",
           "Your finished SKUs. Stock = opening + produced − sold ± returns/adjustments. Unit cost comes from Recipes + labor. Forecast uses the last 90 days of sales.",
           prod_cols, P0, P1, freeze_col="C")
PROD["X5"] = '="Profit / Unit on "&INDEX(FEE_CH,1)&" ("&CUR_SYM&")"'
PROD["Y5"] = '="Margin on "&INDEX(FEE_CH,1)'
add_dv(PROD, "COLLECTIONS", f"C{P0}:C{P1}", "Pick a collection (edit list on Start Here).", "Collection")
add_num_dv(PROD, f"D{P0}:H{P1}", "Numbers only (0 or more).", "Number")
badge_cf(PROD, f"W{P0}:W{P1}")
neg_red(PROD, f"X{P0}:Y{P1}")
name("SKU_LIST", f"Products!$A${P0}:$A${P1}")

# ================================================================== MATERIALS
mat_cols = [
    dict(h="Material ID", w=11, kind="input", fmt="text", align="left"),
    dict(h="Material Name", w=34, kind="input", fmt="text", align="left"),
    dict(h="Category", w=14, kind="dd", fmt="text", align="left"),
    dict(h="Unit", w=7, kind="dd", fmt="text", align="center"),
    dict(h="Supplier", w=18, kind="input", fmt="text", align="left"),
    dict(h="Opening Qty", w=10, kind="input", fmt="qty"),
    dict(h="Default Unit Cost", w=10, kind="input", fmt="cost4", money=True),
    dict(h="Supplier Lead Time (days)", w=10, kind="input", fmt="int"),
    dict(h="Safety Days (blank = default)", w=10, kind="input", fmt="int"),
    dict(h="Min Order Qty (MOQ)", w=10, kind="input", fmt="qty"),
    dict(h="Received", w=10, kind="calc", fmt="qty",
         f=f'=IF($A{{r}}="","",SUMIFS({LOGR("E")},{LOGR("D")},$A{{r}},{LOGR("B")},"Material Purchase",{LOGR("I")},"<>Ordered"))'),
    dict(h="On Order", w=9, kind="calc", fmt="qty",
         f=f'=IF($A{{r}}="","",SUMIFS({LOGR("E")},{LOGR("D")},$A{{r}},{LOGR("B")},"Material Purchase",{LOGR("I")},"Ordered"))'),
    dict(h="Used (via Recipes)", w=10, kind="calc", fmt="qty",
         f=f'=IF($A{{r}}="","",SUMIFS(Recipes!$J${R0}:$J${R1},Recipes!$B${R0}:$B${R1},$A{{r}}))'),
    dict(h="Waste & Adjust.", w=9, kind="calc", fmt="qty",
         f=f'=IF($A{{r}}="","",SUMIFS({LOGR("E")},{LOGR("D")},$A{{r}},{LOGR("B")},"Adjustment")-SUMIFS({LOGR("E")},{LOGR("D")},$A{{r}},{LOGR("B")},"Damaged / Waste"))'),
    dict(h="On Hand", w=10, kind="calc", fmt="qty", bold=True, f='=IF($A{r}="","",$F{r}+K{r}-M{r}+N{r})'),
    dict(h="Avg Unit Cost", w=10, kind="calc", fmt="cost4", money=True,
         f=f'=IF($A{{r}}="","",IFERROR(($F{{r}}*$G{{r}}+SUMIFS({LOGR("N")},{LOGR("D")},$A{{r}},{LOGR("B")},"Material Purchase",{LOGR("I")},"<>Ordered"))/($F{{r}}+K{{r}}),$G{{r}}))'),
    dict(h="Stock Value", w=11, kind="calc", fmt="money", money=True, f='=IF($A{r}="","",MAX(0,O{r})*P{r})'),
    dict(h="Daily Usage (forecast)", w=10, kind="calc", fmt="dec",
         f=f'=IF($A{{r}}="","",SUMIFS(Recipes!$K${R0}:$K${R1},Recipes!$B${R0}:$B${R1},$A{{r}}))'),
    dict(h="Days Left", w=8, kind="calc", fmt="days", f='=IF($A{r}="","",IF(O{r}<=0,0,IF(R{r}=0,9999,ROUND(O{r}/R{r},0))))'),
    dict(h="Est. Stockout Date", w=13, kind="calc", fmt="date", f='=IF($A{r}="","",IF(S{r}>=9999,"—",ASOF+S{r}))'),
    dict(h="Safety Stock", w=9, kind="calc", fmt="qty", f='=IF($A{r}="","",ROUND(R{r}*IF($I{r}="",SAFETY_DAYS,$I{r}),0))'),
    dict(h="Reorder Point", w=9, kind="calc", fmt="qty", f='=IF($A{r}="","",ROUND(R{r}*$H{r},0)+U{r})'),
    dict(h="Reorder Qty (MOQ multiple)", w=11, kind="calc", fmt="qty", bold=True,
         f='=IF($A{r}="","",IF(O{r}+L{r}<=V{r},IF(N($J{r})>0,CEILING(MAX($J{r},R{r}*($H{r}+COVER_DAYS)+U{r}-O{r}-L{r}),$J{r}),ROUNDUP(R{r}*($H{r}+COVER_DAYS)+U{r}-O{r}-L{r},0)),0))'),
    dict(h="Status", w=15, kind="calc", fmt="text", align="center",
         f='=IF($A{r}="","",IF(O{r}<=0,"OUT OF STOCK",IF(O{r}<=U{r},"CRITICAL",IF(O{r}<=V{r},IF(O{r}+L{r}>V{r},"ON ORDER","REORDER SOON"),"IN STOCK"))))'),
    dict(h="urgency score", w=8, kind="helper", fmt="gen", f='=IF(OR($A{r}="",X{r}="IN STOCK"),"",S{r}+ROW()/100000)'),
    dict(h="urgency rank", w=8, kind="helper", fmt="gen", f=f'=IF(Y{{r}}="","",RANK(Y{{r}},$Y${M0}:$Y${M1},1))'),
]
data_sheet(MATS, "Materials  ·  Raw Materials, Supplies & Packaging",
           "Every supply you buy. Usage is deducted automatically through Recipes. Daily usage is forecast from your product sales, so reorders happen before you run out.",
           mat_cols, M0, M1, freeze_col="C")
add_dv(MATS, "MAT_CATS", f"C{M0}:C{M1}", "Pick a category (edit list on Start Here).", "Category")
add_dv(MATS, "UNITS", f"D{M0}:D{M1}", "Unit you buy AND use in recipes (e.g. g, ml, pcs).", "Unit")
add_num_dv(MATS, f"F{M0}:J{M1}", "Numbers only (0 or more).", "Number")
badge_cf(MATS, f"X{M0}:X{M1}")
name("MAT_LIST", f"Materials!$A${M0}:$A${M1}")

# ================================================================== RECIPES
pm = "MATCH($A{r},SKU_LIST,0)"
mm = "MATCH($B{r},MAT_LIST,0)"
rec_cols = [
    dict(h="SKU", w=11, kind="dd", fmt="text", align="left"),
    dict(h="Material ID", w=11, kind="dd", fmt="text", align="left"),
    dict(h="Qty per Unit", w=10, kind="input", fmt="qty"),
    dict(h="Waste %", w=8, kind="input", fmt="pct"),
    dict(h="Product", w=34, kind="calc", fmt="text", align="left",
         f='=IF($A{r}="","",IFERROR(INDEX(Products!$B$6:$B$105,' + pm + '),"⚠ Unknown SKU"))'),
    dict(h="Material", w=34, kind="calc", fmt="text", align="left",
         f='=IF($B{r}="","",IFERROR(INDEX(Materials!$B$6:$B$155,' + mm + '),"⚠ Unknown material"))'),
    dict(h="Unit", w=7, kind="calc", fmt="text", align="center",
         f='=IF($B{r}="","",IFERROR(INDEX(Materials!$D$6:$D$155,' + mm + ')&"",""))'),
    dict(h="Line Cost / Unit", w=11, kind="calc", fmt="money", money=True,
         f='=IF(OR($A{r}="",$B{r}=""),"",$C{r}*(1+$D{r})*IFERROR(INDEX(Materials!$P$6:$P$155,' + mm + '),0))'),
    dict(h="Units Made / Sold", w=10, kind="calc", fmt="int",
         f='=IF(OR($A{r}="",$B{r}=""),"",IF(MODE="Sold",IFERROR(INDEX(Products!$J$6:$J$105,' + pm + '),0),IFERROR(INDEX(Products!$I$6:$I$105,' + pm + '),0)))'),
    dict(h="Material Consumed", w=11, kind="calc", fmt="qty", bold=True,
         f='=IF(OR($A{r}="",$B{r}=""),"",$C{r}*(1+$D{r})*I{r})'),
    dict(h="Daily Usage (forecast)", w=11, kind="calc", fmt="dec",
         f='=IF(OR($A{r}="",$B{r}=""),"",$C{r}*(1+$D{r})*IFERROR(INDEX(Products!$Q$6:$Q$105,' + pm + '),0))'),
]
data_sheet(RECI, "Recipes  ·  Bill of Materials (BOM)",
           "One row per material per product. Qty is per ONE finished unit. Materials are deducted when units are produced (or sold; see Start Here > Deduct Materials When).",
           rec_cols, R0, R1, freeze_col="C")
add_dv(RECI, "SKU_LIST", f"A{R0}:A{R1}", "Pick the finished product.", "SKU")
add_dv(RECI, "MAT_LIST", f"B{R0}:B{R1}", "Pick a material used in one unit.", "Material")
add_num_dv(RECI, f"C{R0}:D{R1}", "Qty per ONE finished unit, in the material's unit. Waste % e.g. 2%.", "Recipe")

# ================================================================== STOCK LOG
log_cols = [
    dict(h="Date", w=13, kind="input", fmt="date"),
    dict(h="Type", w=17, kind="dd", fmt="text", align="left"),
    dict(h="SKU (products)", w=11, kind="dd", fmt="text", align="left"),
    dict(h="Material ID (supplies)", w=11, kind="dd", fmt="text", align="left"),
    dict(h="Qty", w=9, kind="input", fmt="qty"),
    dict(h="Unit Cost", w=10, kind="input", fmt="cost4", money=True),
    dict(h="Freight-In", w=10, kind="input", fmt="money", money=True),
    dict(h="Supplier", w=18, kind="input", fmt="text", align="left"),
    dict(h="PO Status", w=10, kind="dd", fmt="text", align="center"),
    dict(h="Expected Date", w=13, kind="input", fmt="date"),
    dict(h="Batch / PO Ref", w=12, kind="input", fmt="text", align="left"),
    dict(h="Notes", w=34, kind="input", fmt="text", align="left"),
    dict(h="Item Name", w=34, kind="calc", fmt="text", align="left",
         f='=IF(AND($C{r}="",$D{r}=""),"",IF($C{r}<>"",IFERROR(INDEX(Products!$B$6:$B$105,MATCH($C{r},SKU_LIST,0)),"⚠ Unknown SKU"),'
           'IFERROR(INDEX(Materials!$B$6:$B$155,MATCH($D{r},MAT_LIST,0)),"⚠ Unknown material")))'),
    dict(h="Total Cost", w=11, kind="calc", fmt="money", money=True, bold=True,
         f='=IF($A{r}="","",$E{r}*$F{r}+$G{r})'),
]
data_sheet(LOG, "Stock Log  ·  Production, Purchases & Adjustments",
           "Production = finished units made (SKU).  Material Purchase = supplies bought (Material ID; status Ordered until it arrives).  Return / Adjustment (+/−) / Damaged.",
           log_cols, L0, L1, freeze_col="C")
add_date_dv(LOG, f"A{L0}:A{L1}")
add_date_dv(LOG, f"J{L0}:J{L1}", "When the order should arrive.")
add_dv(LOG, '"Production,Material Purchase,Return to Stock,Adjustment,Damaged / Waste"', f"B{L0}:B{L1}",
       "Production & Return use the SKU column. Material Purchase uses Material ID. Adjustment / Damaged can use either.", "Movement type")
add_dv(LOG, "SKU_LIST", f"C{L0}:C{L1}", "Finished product (for Production / Returns).", "SKU")
add_dv(LOG, "MAT_LIST", f"D{L0}:D{L1}", "Supply (for Material Purchase).", "Material")
add_dv(LOG, '"Ordered,Received"', f"I{L0}:I{L1}", "Ordered = on the way (not in stock yet). Received = in stock.", "PO Status")

# ================================================================== EXPENSES
exp_cols = [
    dict(h="Date", w=13, kind="input", fmt="date"),
    dict(h="Vendor", w=20, kind="input", fmt="text", align="left"),
    dict(h="Description", w=32, kind="input", fmt="text", align="left"),
    dict(h="Category", w=31, kind="dd", fmt="text", align="left"),
    dict(h="Amount", w=11, kind="input", fmt="money", money=True),
    dict(h="Payment Method", w=22, kind="dd", fmt="text", align="left"),
    dict(h="Receipt Saved?", w=9, kind="dd", fmt="text", align="center"),
    dict(h="Business Use % (blank = 100%)", w=11, kind="input", fmt="pct"),
    dict(h="Deductible Amount", w=12, kind="calc", fmt="money", money=True, bold=True,
         f='=IF($A{r}="","",$E{r}*IF($H{r}="",1,$H{r}))'),
    dict(h="IRS Schedule C Line", w=42, kind="calc", fmt="text", align="left",
         f='=IF($D{r}="","",IFERROR(INDEX(Reports!$P$32:$P$57,MATCH($D{r},EXP_CATS,0)),""))'),
    dict(h="HMRC SA103 Category", w=38, kind="calc", fmt="text", align="left",
         f='=IF($D{r}="","",IFERROR(INDEX(Reports!$Q$32:$Q$57,MATCH($D{r},EXP_CATS,0)),""))'),
]
data_sheet(EXP, "Expenses  ·  Operating Costs (Tax-Deductible)",
           "Business running costs. Do NOT enter supply / material purchases here; log those on Stock Log so they flow into COGS and inventory.",
           exp_cols, E0, E1, freeze_col="C")
add_date_dv(EXP, f"A{E0}:A{E1}")
add_dv(EXP, "EXP_CATS", f"D{E0}:D{E1}", "Pick a category; it maps to Schedule C / HMRC automatically.", "Category")
add_dv(EXP, "PAY_METHODS", f"F{E0}:F{E1}", "How you paid.", "Payment")
add_dv(EXP, '"Yes,No"', f"G{E0}:G{E1}", "Keep receipts for every deduction.", "Receipt")
add_num_dv(EXP, f"E{E0}:E{E1}", "Amount paid (number).", "Amount")
EXP.conditional_formatting.add(f"G{E0}:G{E1}", CellIsRule(operator="equal", formula=['"No"'], fill=fill("F6DAD3"), font=Font(color="A8402B", bold=True)))

# ================================================================== REPORTS
rp = REP
rp.column_dimensions["A"].width = 2
rp.column_dimensions["B"].width = 42
for j in range(3, 15):
    rp.column_dimensions[CL(j)].width = 11
rp.column_dimensions["O"].width = 13
rp.column_dimensions["P"].width = 44
rp.column_dimensions["Q"].width = 50
rp.column_dimensions["R"].width = 13
for col in "STU":
    rp.column_dimensions[col].hidden = True
rp.row_dimensions[2].height = 30
rp["B2"] = '="Profit & Loss  ·  Tax Year "&FY'
rp["B2"].font = font(18, True, DEEP, HEAD_FONT)
rp["B3"] = "Monthly P&L from Sales & Expenses, expenses by tax category, and the Schedule C Part III cost-of-goods worksheet."
rp["B3"].font = font(10, False, MUTED, italic=True)
for i, (lbl, tgt) in enumerate([("⌂ Start Here", "Start Here"), ("▦ Dashboard", "Dashboard")]):
    c = rp.cell(2, 16 + i, lbl)
    c.hyperlink = f"#{q(tgt)}!A1"
    c.font = font(9, True, SAGE, underline="single")


def hdr_row(r, labels_from_col2=None):
    rp.row_dimensions[r].height = 22
    c = rp.cell(r, 2, labels_from_col2 or "")
    c.fill, c.font = fill(DEEP), font(10, True, "FFFFFF")
    for j in range(3, 16):
        c = rp.cell(r, j)
        c.fill, c.font = fill(DEEP), font(10, True, "FFFFFF")
        c.alignment = Alignment(horizontal="center", vertical="center")
        if j <= 14:
            c.value = f"=DATE(FY,{j - 2},1)"
            c.number_format = "mmm"
        else:
            c.value = "Total"


hdr_row(5, "PROFIT & LOSS")
DR = lambda col: f'Sales!${col}${S0}:${col}${S1}'
MCRIT = f'{DR("A")},">="&C$5,{DR("A")},"<="&EOMONTH(C$5,0)'
pl = [
    (6, "REVENUE", None, "sec"),
    (7, "Item Sales", f'=SUMIFS({DR("N")},{MCRIT})', "row"),
    (8, "Less: Discounts", f'=SUMIFS({DR("G")},{MCRIT},{DR("L")},"Completed")', "row"),
    (9, "Shipping Income", f'=SUMIFS({DR("H")},{MCRIT},{DR("L")},"Completed")', "row"),
    (10, "Net Revenue", "=C7-C8+C9", "total"),
    (11, "COST OF SALES & PLATFORM FEES", None, "sec"),
    (12, "Listing Fees", f'=SUMIFS({DR("P")},{MCRIT})', "row"),
    (13, "Transaction Fees", f'=SUMIFS({DR("Q")},{MCRIT})', "row"),
    (14, "Payment Processing Fees", f'=SUMIFS({DR("R")},{MCRIT})', "row"),
    (15, "Offsite Ads Fees", f'=SUMIFS({DR("S")},{MCRIT})', "row"),
    (16, "Other Platform Fees", f'=SUMIFS({DR("T")},{MCRIT})', "row"),
    (17, "Shipping Labels", f'=SUMIFS({DR("K")},{MCRIT},{DR("L")},"<>Cancelled")', "row"),
    (18, "Cost of Goods Sold (materials + labor)", f'=SUMIFS({DR("V")},{MCRIT})', "row"),
    (19, "Total Cost of Sales", "=SUM(C12:C18)", "sub"),
    (20, "Gross Profit", "=C10-C19", "total"),
    (21, "Gross Margin %", '=IF(C10=0,0,C20/C10)', "pct"),
    (22, "Operating Expenses", f'=SUMIFS(Expenses!$E${E0}:$E${E1},Expenses!$A${E0}:$A${E1},">="&C$5,Expenses!$A${E0}:$A${E1},"<="&EOMONTH(C$5,0))', "row"),
    (23, "NET PROFIT", "=C20-C22", "grand"),
    (24, "Net Margin %", '=IF(C10=0,0,C23/C10)', "pct"),
    (25, "Orders", f'=SUMIFS({DR("Y")},{MCRIT},{DR("L")},"Completed")', "count"),
    (26, "Units Sold", f'=SUMIFS({DR("E")},{MCRIT},{DR("L")},"Completed")', "count"),
    (27, "Memo: Sales Tax Collected (not revenue)", f'=SUMIFS({DR("I")},{MCRIT},{DR("L")},"<>Cancelled")', "memo"),
]
for r, lbl, f, kind in pl:
    rp.row_dimensions[r].height = 19
    c = rp.cell(r, 2, lbl)
    if kind == "sec":
        for j in range(2, 16):
            rp.cell(r, j).fill = fill(SAND)
        c.font = font(9, True, DEEP)
        continue
    bold = kind in ("total", "grand", "sub")
    c.font = font(11 if kind == "grand" else 10, bold, DEEP if bold else (MUTED if kind == "memo" else INK),
                  italic=kind == "memo")
    c.alignment = Alignment(indent=0 if bold else 1)
    for j in range(3, 16):
        col = CL(j)
        cell = rp.cell(r, j)
        if j <= 14:
            cell.value = f.replace("C$5", f"{col}$5").replace("C7", f"{col}7").replace("C8", f"{col}8") \
                .replace("C9", f"{col}9").replace("C10", f"{col}10").replace("C12:C18", f"{col}12:{col}18") \
                .replace("C19", f"{col}19").replace("C20", f"{col}20").replace("C22", f"{col}22").replace("C23", f"{col}23")
        else:
            if kind == "pct":
                cell.value = "=IF(O10=0,0,O20/O10)" if r == 21 else "=IF(O10=0,0,O23/O10)"
            else:
                cell.value = f"=SUM(C{r}:N{r})"
        cell.number_format = FMT["pct"] if kind == "pct" else (FMT["int"] if kind == "count" else FMT["money0"])
        cell.font = font(11 if kind == "grand" else 10, bold or j == 15, DEEP if bold else (MUTED if kind == "memo" else CALC_TXT),
                         italic=kind == "memo")
        if kind in ("total", "sub"):
            cell.border = Border(top=side(SAGE))
        if kind == "grand":
            cell.fill = fill("E4ECE6")
            cell.border = Border(top=side(DEEP, "medium"), bottom=side(DEEP, "medium"))
        elif kind not in ("total", "sub"):
            cell.border = THIN_LINE
    if kind == "grand":
        c.fill = fill("E4ECE6")
        c.border = Border(top=side(DEEP, "medium"), bottom=side(DEEP, "medium"))
    if kind not in ("pct", "count"):
        money_range(rp, f"C{r}:O{r}", 0)
neg_red(rp, "C20:O24")

# --- expense categories x months + tax mapping
section(rp, 30, "OPERATING EXPENSES BY CATEGORY  ·  TAX MAPPING", "B", "R")
hdr_row(31, "Category  (edit / add in cream cells)")
for j, t in [(16, "IRS Schedule C Line"), (17, "HMRC SA103 Category"), (18, "Deductible (FY)")]:
    c = rp.cell(31, j, t)
    c.fill, c.font = fill(DEEP), font(10, True, "FFFFFF")
    c.alignment = Alignment(horizontal="center", vertical="center")
CATS = [
    ("Advertising & Marketing", "Line 8 - Advertising", "Advertising costs"),
    ("Car & Vehicle", "Line 9 - Car and truck expenses", "Car, van and travel expenses"),
    ("Platform Fees (manual)", "Line 10 - Commissions and fees", "Other business expenses"),
    ("Contract Labor", "Line 11 - Contract labor", "Wages, salaries and other staff costs"),
    ("Equipment (< $2,500)", "Line 13 - Depreciation / Sec. 179", "Capital allowances (not an expense box)"),
    ("Insurance", "Line 15 - Insurance", "Rent, rates, power and insurance costs"),
    ("Bank & Loan Interest", "Line 16 - Interest", "Interest on bank and other loans"),
    ("Legal & Professional", "Line 17 - Legal and professional services", "Accountancy, legal and other professional fees"),
    ("Office Supplies", "Line 18 - Office expense", "Phone, fax, stationery and other office costs"),
    ("Software & Apps", "Line 18 - Office expense", "Phone, fax, stationery and other office costs"),
    ("Rent / Studio Space", "Line 20b - Rent (other business property)", "Rent, rates, power and insurance costs"),
    ("Repairs & Maintenance", "Line 21 - Repairs and maintenance", "Repairs and maintenance of property and equipment"),
    ("Shop Supplies (non-inventory)", "Line 22 - Supplies", "Other business expenses"),
    ("Taxes & Licenses", "Line 23 - Taxes and licenses", "Other business expenses"),
    ("Travel", "Line 24a - Travel", "Car, van and travel expenses"),
    ("Meals (50%)", "Line 24b - Deductible meals", "Not usually allowable (entertaining)"),
    ("Utilities", "Line 25 - Utilities", "Rent, rates, power and insurance costs"),
    ("Phone & Internet", "Line 25 - Utilities", "Phone, fax, stationery and other office costs"),
    ("Wages", "Line 26 - Wages", "Wages, salaries and other staff costs"),
    ("Website & Subscriptions", "Line 27a - Other expenses", "Phone, fax, stationery and other office costs"),
    ("Market & Booth Fees", "Line 27a - Other expenses", "Other business expenses"),
    ("Photography & Props", "Line 27a - Other expenses", "Advertising costs"),
    ("Postage (non-order)", "Line 18 - Office expense", "Phone, fax, stationery and other office costs"),
    ("Education & Training", "Line 27a - Other expenses", "Other business expenses"),
    ("Bank & Card Fees", "Line 27a - Other expenses", "Bank, credit card and other financial charges"),
    ("Home Office", "Line 30 - Business use of home (Form 8829)", "Use of home (HMRC simplified expenses)"),
]
EC = lambda col: f'Expenses!${col}${E0}:${col}${E1}'
for i in range(26):
    r = 32 + i
    rp.row_dimensions[r].height = 18
    cat = CATS[i] if i < len(CATS) else ("", "", "")
    for j, v in [(2, cat[0]), (16, cat[1]), (17, cat[2])]:
        c = rp.cell(r, j, v or None)
        c.fill, c.font, c.protection = fill(INPUT), font(10), UNLOCK
        c.border = Border(bottom=side("F3EBDB"))
    for j in range(3, 15):
        col = CL(j)
        c = rp.cell(r, j, f'=IF($B{r}="","",SUMIFS({EC("E")},{EC("D")},$B{r},{EC("A")},">="&{col}$31,{EC("A")},"<="&EOMONTH({col}$31,0)))')
        c.number_format, c.font, c.border = FMT["money0"], font(10, False, CALC_TXT), THIN_LINE
    c = rp.cell(r, 15, f'=IF($B{r}="","",SUM(C{r}:N{r}))')
    c.number_format, c.font, c.border = FMT["money0"], font(10, True, DEEP), THIN_LINE
    c = rp.cell(r, 18, f'=IF($B{r}="","",SUMIFS({EC("I")},{EC("D")},$B{r},{EC("A")},">="&DATE(FY,1,1),{EC("A")},"<="&DATE(FY,12,31)))')
    c.number_format, c.font, c.border = FMT["money0"], font(10, True, DEEP), THIN_LINE
    # hidden helpers for dashboard ranking (period)
    rp.cell(r, 19, f'=IF($B{r}="","",SUMIFS({EC("E")},{EC("D")},$B{r},{EC("A")},">="&P_START,{EC("A")},"<="&P_END))')
    rp.cell(r, 20, f'=IF(OR($B{r}="",S{r}=0),"",S{r}+ROW()/1000000)')
    rp.cell(r, 21, f'=IF(T{r}="","",RANK(T{r},$T$32:$T$57,0))')
    money_range(rp, f"C{r}:O{r}", 0)
    money_range(rp, f"R{r}", 0)
name("EXP_CATS", "Reports!$B$32:$B$57")
r = 58
rp.cell(r, 2, "Total Operating Expenses").font = font(10, True, DEEP)
for j in list(range(3, 16)) + [18]:
    col = CL(j)
    c = rp.cell(r, j, f"=SUM({col}32:{col}57)")
    c.number_format, c.font = FMT["money0"], font(10, True, DEEP)
    c.border = Border(top=side(DEEP, "medium"))
rp.cell(r, 2).border = Border(top=side(DEEP, "medium"))
money_range(rp, "C58:O58", 0)
money_range(rp, "R58", 0)
rp.merge_cells("B59:Q59")
rp["B59"] = ("Mapping is a bookkeeping aid only, not tax advice. Expense totals check: Reports total should equal the Expenses tab total "
             "for the year (uncategorised rows are excluded and show on the check line below).")
rp["B59"].font = font(9, False, MUTED, italic=True)
rp["B60"] = "Check: uncategorised expenses this year"
rp["B60"].font = font(9, False, MUTED)
rp["C60"] = (f'=SUMIFS({EC("E")},{EC("A")},">="&DATE(FY,1,1),{EC("A")},"<="&DATE(FY,12,31))-O58')
rp["C60"].number_format = FMT["money"]
rp["C60"].font = font(9, True, CALC_TXT)
rp.conditional_formatting.add("C60", CellIsRule(operator="notEqual", formula=["0"], fill=fill("F6DAD3"), font=Font(color="A8402B", bold=True)))

# --- annual tax summary
section(rp, 62, "ANNUAL TAX SUMMARY  (estimate)", "B", "E")
tax_rows = [
    (63, '="Gross receipts / sales  ("&IF(LEFT(TAX_REGION,2)="UK","SA103 turnover","Sch. C line 1")&")"', "=O10"),
    (64, '="Cost of goods sold  ("&IF(LEFT(TAX_REGION,2)="UK","cost of goods","Sch. C line 4, from Part III")&")"', "=D83"),
    (65, "Gross profit", "=D63-D64"),
    (66, "Platform & payment fees (from Sales)", "=SUM(O12:O16)"),
    (67, "Shipping labels (from Sales)", "=O17"),
    (68, "Operating expenses (deductible)", "=R58"),
    (69, "Estimated net profit (before self-employment / income tax)", "=D65-D66-D67-D68"),
]
for r, lbl, f in tax_rows:
    rp.row_dimensions[r].height = 19
    rp.merge_cells(f"B{r}:C{r}")
    c = rp.cell(r, 2, lbl)
    c.font = font(10, r in (65, 69), DEEP if r in (65, 69) else INK)
    c = rp.cell(r, 4, f)
    c.number_format, c.font = FMT["money"], font(10, r in (65, 69), DEEP if r in (65, 69) else CALC_TXT)
    rp.column_dimensions["D"].width = 15
    for j in range(2, 5):
        rp.cell(r, j).border = THIN_LINE
    money_range(rp, f"D{r}")
for j in range(2, 5):
    rp.cell(69, j).fill = fill("E4ECE6")
    rp.cell(69, j).border = Border(top=side(DEEP, "medium"), bottom=side(DEEP, "medium"))
neg_red(rp, "D63:D69")
rp.merge_cells("F63:N69")
rp["F63"] = ("How COGS is handled: the P&L above uses each SKU's standard unit cost (materials + your labor rate) so you see true "
             "per-sale profit. For tax, US sole proprietors report COGS on Schedule C Part III (below): opening inventory + supply "
             "purchases − closing inventory, valued at MATERIAL cost only (your own time is not deductible). Platform fees are "
             "usually reported on line 10; shipping labels on line 27a or as part of COGS, so ask your tax pro. UK sellers: use the "
             "HMRC column above and the turnover / cost of goods figures here.")
rp["F63"].font = font(9, False, MUTED, italic=True)
rp["F63"].alignment = Alignment(wrap_text=True, vertical="top")

section(rp, 72, "SCHEDULE C  ·  PART III  ·  COST OF GOODS SOLD WORKSHEET", "B", "E")
part3 = [
    (74, "Line", "Amount", None, "hdr"),
    (75, "Inventory valuation method", "Cost", None, "info"),
    (76, "35  Inventory at beginning of year", "=SUMPRODUCT(Materials!$F$6:$F$155,Materials!$G$6:$G$155)+SUMPRODUCT(Products!$E$6:$E$105,Products!$M$6:$M$105)", None, "input"),
    (77, "36  Purchases (supplies received this year)",
     f'=SUMIFS({LOGR("N")},{LOGR("B")},"Material Purchase",{LOGR("I")},"<>Ordered",{LOGR("A")},">="&DATE(FY,1,1),{LOGR("A")},"<="&DATE(FY,12,31))', None, "calc"),
    (78, "37  Cost of labor (wages paid; not your own time)", 0, None, "input"),
    (79, "38  Materials and supplies", 0, None, "input"),
    (80, "39  Other costs", 0, None, "input"),
    (81, "40  Add lines 35 through 39", "=SUM(D76:D80)", None, "sub"),
    (82, "41  Inventory at end of year", '=IF(E82="",SUM(Materials!$Q$6:$Q$155)+SUM(Products!$AF$6:$AF$105),E82)', None, "calc"),
    (83, "42  Cost of goods sold (40 minus 41)", "=D81-D82", None, "total"),
]
for r, lbl, f, _, kind in part3:
    rp.row_dimensions[r].height = 19
    rp.merge_cells(f"B{r}:C{r}")
    c = rp.cell(r, 2, lbl)
    d = rp.cell(r, 4, f)
    if kind == "hdr":
        for j in range(2, 6):
            rp.cell(r, j).fill = fill(SAND)
            rp.cell(r, j).font = font(9, True, DEEP)
        rp.cell(r, 5, "Override")
        continue
    c.font = font(10, kind == "total", DEEP if kind == "total" else INK)
    d.number_format = FMT["money"] if kind != "info" else "@"
    d.alignment = Alignment(horizontal="right")
    if kind == "input":
        d.fill, d.protection, d.font, d.border = fill(INPUT), UNLOCK, font(10, False, INK), INPUT_BORDER
    else:
        d.font = font(10, kind in ("total", "sub"), DEEP if kind in ("total", "sub") else CALC_TXT)
        for j in range(2, 5):
            rp.cell(r, j).border = THIN_LINE
    if kind != "info":
        money_range(rp, f"D{r}")
e82 = rp["E82"]
e82.fill, e82.protection, e82.border, e82.number_format = fill(INPUT), UNLOCK, INPUT_BORDER, FMT["money"]
money_range(rp, "E82")
for j in range(2, 5):
    rp.cell(83, j).fill = fill("E4ECE6")
    rp.cell(83, j).border = Border(top=side(DEEP, "medium"), bottom=side(DEEP, "medium"))
rp.merge_cells("F74:N83")
rp["F74"] = ("Line 35: prefilled with your opening stock at cost. Replace it with last year's line 41 figure. "
             "Line 41: closing stock at material cost as of the Report Date. Type your Dec 31 physical count value in "
             "the cream Override cell (E82) at year end. Lines 37–39: enter only if they apply. Line 42 flows to the tax summary above.")
rp["F74"].font = font(9, False, MUTED, italic=True)
rp["F74"].alignment = Alignment(wrap_text=True, vertical="top")
rp.freeze_panes = "C6"
rp.print_area = "B2:R83"
rp.page_setup.orientation = "landscape"
rp.page_setup.fitToWidth = 1
rp.page_setup.fitToHeight = 0
rp.sheet_properties.pageSetUpPr.fitToPage = True

# ================================================================== DASHBOARD
d = DASH
for r in range(1, 75):
    for c in range(1, 18):
        d.cell(r, c).fill = fill(BG)
d.column_dimensions["A"].width = 2
for col in "BCDFGHJKLNOP":
    d.column_dimensions[col].width = 11
for col in "EIM":
    d.column_dimensions[col].width = 2.5
d.column_dimensions["Q"].width = 3
d.column_dimensions["R"].width = 3
d.column_dimensions["S"].width = 26
for col in "TUVWX":
    d.column_dimensions[col].width = 19

d.row_dimensions[1].height = 10
d.merge_cells("B2:J2")
d["B2"] = "=BIZ_NAME"
d["B2"].font = font(22, True, DEEP, HEAD_FONT)
d.row_dimensions[2].height = 34
d.merge_cells("B3:J3")
d["B3"] = '="Inventory & Profit Dashboard  ·  "&IF(PERIOD="Full Year","Tax year "&FY,PERIOD&" "&FY)'
d["B3"].font = font(11, False, CLAY, italic=True)
d["L2"] = "REPORT DATE"
d["L2"].font = font(8, True, MUTED)
d["L2"].alignment = Alignment(horizontal="center", vertical="bottom")
d.merge_cells("K3:L3")
d["K3"] = "=ASOF"
d["K3"].number_format = FMT["date"]
d["K3"].font = font(11, True, DEEP)
d["K3"].alignment = Alignment(horizontal="center")
d.merge_cells("N2:P2")
d["N2"] = "PERIOD  ▼  (pick)"
d["N2"].font = font(8, True, MUTED)
d["N2"].alignment = Alignment(horizontal="center", vertical="bottom")
d.merge_cells("N3:P3")
d["N3"] = "Oct"
d["N3"].fill, d["N3"].font = fill(DD), font(12, True, DEEP)
d["N3"].alignment = Alignment(horizontal="center", vertical="center")
d["N3"].protection = UNLOCK
for col in "NOP":
    d[f"{col}3"].border = Border(top=side(SAGE), bottom=side(SAGE), left=side(SAGE) if col == "N" else None,
                                 right=side(SAGE) if col == "P" else None)
add_dv(d, "PERIOD_LIST", "N3", "Full Year or a single month of the tax year.", "Period")
name("PERIOD", "Dashboard!$N$3")
d.row_dimensions[3].height = 24
nav = [("B", "⌂ Start"), ("C", "Sales"), ("D", "Products"), ("F", "Materials"), ("G", "Recipes"),
       ("H", "Stock Log"), ("J", "Expenses"), ("K", "Reports")]
for col, lbl in nav:
    c = d[f"{col}4"]
    c.value = lbl
    c.hyperlink = f"#{q('Start Here' if lbl.startswith('⌂') else lbl)}!A1"
    c.font = font(9, True, SAGE, underline="single")
d.row_dimensions[4].height = 20
d.row_dimensions[5].height = 8

# helper block (chart data + period math), right of the print area
d["S2"] = "CHART DATA & HELPERS (auto, do not edit)"
d["S2"].font = font(9, True, MUTED)
helpers = [
    ("S3", "Period start", "T3", '=IF(PERIOD="Full Year",DATE(FY,1,1),DATE(FY,MATCH(PERIOD,MONTHS,0),1))', "P_START"),
    ("S4", "Period end", "T4", '=IF(PERIOD="Full Year",DATE(FY,12,31),EOMONTH(P_START,0))', "P_END"),
    ("S5", "Prior period start", "T5", '=IF(PERIOD="Full Year",DATE(FY-1,1,1),EDATE(P_START,-1))', "PREV_START"),
    ("S6", "Prior period end", "T6", '=IF(PERIOD="Full Year",DATE(FY-1,12,31),EOMONTH(PREV_START,0))', "PREV_END"),
]
for lc, lbl, vc, f, nm in helpers:
    d[lc] = lbl
    d[lc].font = font(9, False, MUTED)
    d[vc] = f
    d[vc].number_format = FMT["date"]
    d[vc].font = font(9, False, CALC_TXT)
    name(nm, f"Dashboard!${vc[0]}${vc[1:]}")

SA = DR("A")
per = lambda s, e: f'{SA},">="&{s},{SA},"<="&{e}'
EXA = f"Expenses!$A${E0}:$A${E1}"
kpi_rows = [
    ("Net Revenue", f'=SUMIFS({DR("O")},{per("P_START","P_END")})', f'=SUMIFS({DR("O")},{per("PREV_START","PREV_END")})'),
    ("True Net Profit", f'=SUMIFS({DR("W")},{per("P_START","P_END")})-SUMIFS(Expenses!$E${E0}:$E${E1},{EXA},">="&P_START,{EXA},"<="&P_END)',
     f'=SUMIFS({DR("W")},{per("PREV_START","PREV_END")})-SUMIFS(Expenses!$E${E0}:$E${E1},{EXA},">="&PREV_START,{EXA},"<="&PREV_END)'),
    ("Profit Margin", "=IF(T9=0,0,T10/T9)", "=IF(U9=0,0,U10/U9)"),
    ("Orders", f'=SUMIFS({DR("Y")},{per("P_START","P_END")},{DR("L")},"Completed")',
     f'=SUMIFS({DR("Y")},{per("PREV_START","PREV_END")},{DR("L")},"Completed")'),
    ("Avg Order Value", "=IF(T12=0,0,T9/T12)", "=IF(U12=0,0,U9/U12)"),
    ("Fees % of Revenue", f'=IF(T9=0,0,SUMIFS({DR("U")},{per("P_START","P_END")})/T9)',
     f'=IF(U9=0,0,SUMIFS({DR("U")},{per("PREV_START","PREV_END")})/U9)'),
    ("Inventory Value", "=SUM(Products!$P$6:$P$105)+SUM(Materials!$Q$6:$Q$155)", "=SUM(Products!$P$6:$P$105)"),
    ("Items to Reorder",
     '=COUNTIF(Products!$W$6:$W$105,"OUT OF STOCK")+COUNTIF(Products!$W$6:$W$105,"CRITICAL")+COUNTIF(Products!$W$6:$W$105,"REORDER SOON")'
     '+COUNTIF(Materials!$X$6:$X$155,"OUT OF STOCK")+COUNTIF(Materials!$X$6:$X$155,"CRITICAL")+COUNTIF(Materials!$X$6:$X$155,"REORDER SOON")',
     '=COUNTIF(Products!$W$6:$W$105,"OUT OF STOCK")+COUNTIF(Products!$W$6:$W$105,"CRITICAL")+COUNTIF(Materials!$X$6:$X$155,"OUT OF STOCK")+COUNTIF(Materials!$X$6:$X$155,"CRITICAL")'),
]
d["S8"], d["T8"], d["U8"] = "KPI", "This period", "Prior period"
for c in ("S8", "T8", "U8"):
    d[c].font = font(9, True, MUTED)
for i, (lbl, cur, prev) in enumerate(kpi_rows):
    r = 9 + i
    d[f"S{r}"] = lbl
    d[f"T{r}"] = cur
    d[f"U{r}"] = prev
    for c in (f"S{r}", f"T{r}", f"U{r}"):
        d[c].font = font(9, False, CALC_TXT)
    d[f"T{r}"].number_format = d[f"U{r}"].number_format = FMT["pct"] if lbl in ("Profit Margin", "Fees % of Revenue") else FMT["dec"]
d["S17"] = "Prior label"
d["T17"] = '=IF(PERIOD="Full Year","last year","last month")'


def money_txt(cell):
    return f'=IF({cell}<0,"-","")&CUR_SYM&FIXED(ABS({cell}),0)'


def delta_txt(cur, prev, pts=False):
    if pts:
        return (f'=IF({prev}=0,"No prior-period data",IF({cur}>={prev},"▲ ","▼ ")&FIXED(ABS({cur}-{prev})*100,1)&" pts vs "&$T$17)')
    return (f'=IF({prev}=0,"No prior-period data",IF({cur}>={prev},"▲ ","▼ ")&FIXED(ABS({cur}-{prev})/ABS({prev})*100,0)&"% vs "&$T$17)')


cards = [
    ("NET REVENUE", money_txt("T9"), delta_txt("T9", "U9"), "up"),
    ("TRUE NET PROFIT", money_txt("T10"), delta_txt("T10", "U10"), "up"),
    ("PROFIT MARGIN", '=FIXED(T11*100,1)&"%"', delta_txt("T11", "U11", pts=True), "up"),
    ("ORDERS", "=FIXED(T12,0)", delta_txt("T12", "U12"), "up"),
    ("AVG ORDER VALUE", '=CUR_SYM&FIXED(T13,2)', delta_txt("T13", "U13"), "up"),
    ("FEES % OF REVENUE", '=FIXED(T14*100,1)&"%"', delta_txt("T14", "U14", pts=True), "down"),
    ("INVENTORY VALUE (AT COST)", money_txt("T15"), '="Finished "&CUR_SYM&FIXED(U15,0)&"  ·  Supplies "&CUR_SYM&FIXED(T15-U15,0)', "flat"),
    ("ITEMS TO REORDER", "=FIXED(T16,0)", '=FIXED(U16,0)&" critical or out of stock"', "alert"),
]
CARD_COLS = ["B", "F", "J", "N"]
CARD_BD = side("E6DCCB")


def draw_card(top, col, label, value, delta, kind, accent):
    c0 = d[f"{col}{top}"].column
    cols = [CL(c0), CL(c0 + 1), CL(c0 + 2)]
    rng = lambda r: f"{cols[0]}{r}:{cols[2]}{r}"
    d.merge_cells(rng(top))
    d.merge_cells(f"{cols[0]}{top + 1}:{cols[2]}{top + 2}")
    d.merge_cells(rng(top + 3))
    for r in range(top, top + 4):
        for k, cc in enumerate(cols):
            cell = d[f"{cc}{r}"]
            cell.fill = fill(CARD)
            cell.border = Border(top=side(accent, "thick") if r == top else None,
                                 bottom=CARD_BD if r == top + 3 else None,
                                 left=CARD_BD if k == 0 else None, right=CARD_BD if k == 2 else None)
    lc = d[f"{cols[0]}{top}"]
    lc.value, lc.font = label, font(8, True, MUTED)
    lc.alignment = Alignment(horizontal="left", vertical="bottom", indent=1)
    vc = d[f"{cols[0]}{top + 1}"]
    vc.value, vc.font = value, font(22, True, DEEP, HEAD_FONT)
    vc.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    dc = d[f"{cols[0]}{top + 3}"]
    dc.value, dc.font = delta, font(9, True, MUTED)
    dc.alignment = Alignment(horizontal="left", vertical="top", indent=1)
    ref = f"{cols[0]}{top + 3}"
    good, bad = Font(color="3F7A4F", bold=True), Font(color="A8402B", bold=True)
    if kind in ("up", "down"):
        up_font, dn_font = (good, bad) if kind == "up" else (bad, good)
        d.conditional_formatting.add(ref, FormulaRule(formula=[f'LEFT({ref},1)="▲"'], font=up_font))
        d.conditional_formatting.add(ref, FormulaRule(formula=[f'LEFT({ref},1)="▼"'], font=dn_font))
    if kind == "alert":
        d.conditional_formatting.add(f"{cols[0]}{top + 1}", FormulaRule(formula=["$T$16>0"], font=Font(color="A8402B", bold=True)))


accents = [SAGE, DEEP, SAGE, CLAY, GOLD, CLAY, SAGE, "A8402B"]
for i, (lbl, val, dl, kind) in enumerate(cards):
    top = 6 if i < 4 else 11
    draw_card(top, CARD_COLS[i % 4], lbl, val, dl, kind, accents[i])
for top in (6, 11):
    d.row_dimensions[top].height = 22
    d.row_dimensions[top + 1].height = 20
    d.row_dimensions[top + 2].height = 20
    d.row_dimensions[top + 3].height = 20
d.row_dimensions[10].height = 10
d.row_dimensions[15].height = 12


def chart_title(cell_range, text):
    d.merge_cells(cell_range)
    c = d[cell_range.split(":")[0]]
    c.value = text
    c.font = font(12, True, DEEP, HEAD_FONT)
    c.alignment = Alignment(vertical="center")
    d.row_dimensions[c.row].height = 24


chart_title("B16:H16", '="Net Revenue vs True Net Profit  ·  "&FY')
chart_title("J16:P16", "Net Revenue by Channel  ·  selected period")
chart_title("B33:H33", "Top 10 Products by Net Profit  ·  selected period")
chart_title("J33:P33", "Where Every Dollar Goes  ·  selected period")
d["J33"] = '="Where Every "&CUR_SYM&" Goes  ·  selected period"'
chart_title("B50:H50", "Top Expense Categories  ·  selected period")
chart_title("J50:P50", "Action List  ·  produce or reorder next")
for r in list(range(17, 33)) + list(range(34, 50)) + list(range(51, 67)):
    d.row_dimensions[r].height = 15

# --- chart data blocks
d["S19"] = "Month"
d["T19"] = "Net Revenue"
d["U19"] = "Net Profit"
months_txt = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
for i in range(12):
    r = 20 + i
    col = CL(3 + i)
    d[f"S{r}"] = months_txt[i]
    d[f"T{r}"] = f"=Reports!{col}10"
    d[f"U{r}"] = f"=Reports!{col}23"
d["S34"] = "Channel"
d["T34"] = "Net Revenue"
for i in range(6):
    r = 35 + i
    d[f"S{r}"] = f'=IF(INDEX(FEE_CH,{i + 1})="","(unused)",INDEX(FEE_CH,{i + 1}))'
    d[f"T{r}"] = f'=IF(INDEX(FEE_CH,{i + 1})="",0,SUMIFS({DR("O")},{DR("C")},INDEX(FEE_CH,{i + 1}),{per("P_START","P_END")}))'
d["S43"] = "Product"
d["T43"] = "Net Profit"
for k in range(1, 11):
    r = 43 + k
    d[f"S{r}"] = f'=IFERROR(INDEX(Products!$B$6:$B$105,MATCH({k},Products!$AE$6:$AE$105,0)),"")'
    d[f"T{r}"] = f'=IFERROR(INDEX(Products!$AC$6:$AC$105,MATCH({k},Products!$AE$6:$AE$105,0)),0)'
d["S56"] = "Split"
split = [("COGS", f'=SUMIFS({DR("V")},{per("P_START","P_END")})'),
         ("Platform Fees", f'=SUMIFS({DR("U")},{per("P_START","P_END")})'),
         ("Shipping Labels", f'=SUMIFS({DR("K")},{per("P_START","P_END")},{DR("L")},"<>Cancelled")'),
         ("Operating Expenses", f'=SUMIFS(Expenses!$E${E0}:$E${E1},{EXA},">="&P_START,{EXA},"<="&P_END)'),
         ("Net Profit", "=MAX(0,T9-SUM(T57:W57))")]
for i, (lbl, f) in enumerate(split):
    col = CL(20 + i)
    d[f"{col}56"] = lbl
    d[f"{col}57"] = f
d["S57"] = "Revenue"
d["S60"] = "Category"
d["T60"] = "Amount"
for k in range(1, 9):
    r = 60 + k
    d[f"S{r}"] = f'=IFERROR(INDEX(EXP_CATS,MATCH({k},Reports!$U$32:$U$57,0)),"")'
    d[f"T{r}"] = f'=IFERROR(INDEX(Reports!$S$32:$S$57,MATCH({k},Reports!$U$32:$U$57,0)),0)'
for r in range(19, 70):
    for col in "STUVWX":
        cell = d[f"{col}{r}"]
        if cell.value is not None:
            cell.font = font(9, r in (19, 34, 43, 56, 60), MUTED if r in (19, 34, 43, 56, 60) else CALC_TXT)
            if col != "S" and isinstance(cell.value, str) and cell.value.startswith("=") and r not in (35, 36, 37, 38, 39, 40) or (col == "T" and 35 <= r <= 40):
                cell.number_format = FMT["dec"]
for col in "TUVWX":
    d[f"{col}56"].font = font(9, True, MUTED)
d["S57"].font = font(9, False, CALC_TXT)


def style_axes(ch, yfmt="#,##0"):
    ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="EAE3D6"))
    ch.y_axis.numFmt = yfmt
    ch.y_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.x_axis.spPr = GraphicalProperties(ln=LineProperties(solidFill="D8CFBF"))
    ch.x_axis.delete = False
    ch.y_axis.delete = False


def frame(ch):
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(solidFill="E6DCCB"))
    ch.roundedCorners = False


CM_W, CM_H = 13.3, 8.2
# 1. combo revenue vs profit
bar = BarChart()
bar.type = "col"
bar.gapWidth = 60
bar.add_data(Reference(d, min_col=20, min_row=19, max_row=31), titles_from_data=True)
bar.set_categories(Reference(d, min_col=19, min_row=20, max_row=31))
bar.series[0].graphicalProperties.solidFill = SAGE
bar.series[0].graphicalProperties.line.noFill = True
line = LineChart()
line.add_data(Reference(d, min_col=21, min_row=19, max_row=31), titles_from_data=True)
s = line.series[0]
s.graphicalProperties.line.solidFill = CLAY
s.graphicalProperties.line.width = 31750
s.marker.symbol = "circle"
s.marker.size = 6
s.marker.graphicalProperties = GraphicalProperties(solidFill=CLAY)
s.marker.graphicalProperties.line.solidFill = CLAY
s.smooth = False
style_axes(bar)
bar += line
bar.legend.position = "b"
bar.legend.overlay = False
bar.width, bar.height = CM_W, CM_H
frame(bar)
d.add_chart(bar, "B17")

# 2. channel doughnut
dn = DoughnutChart(holeSize=58)
dn.add_data(Reference(d, min_col=20, min_row=34, max_row=40), titles_from_data=True)
dn.set_categories(Reference(d, min_col=19, min_row=35, max_row=40))
pal = [DEEP, SAGE, CLAY, GOLD, MIST, "E3C9B5"]
dn.series[0].data_points = [DataPoint(idx=i, spPr=GraphicalProperties(solidFill=pal[i])) for i in range(6)]
for dp in dn.series[0].data_points:
    dp.graphicalProperties.line.solidFill = "FFFFFF"
dn.dataLabels = DataLabelList()
dn.dataLabels.showPercent = True
dn.dataLabels.showVal = False
dn.dataLabels.showCatName = False
dn.dataLabels.showSerName = False
dn.dataLabels.showLeaderLines = False
dn.dataLabels.showLegendKey = False
dn.legend.position = "r"
dn.legend.overlay = False
dn.width, dn.height = CM_W, CM_H
frame(dn)
d.add_chart(dn, "J17")

# 3. top products horizontal bar
tb = BarChart()
tb.type = "bar"
tb.gapWidth = 45
tb.add_data(Reference(d, min_col=20, min_row=43, max_row=53), titles_from_data=True)
tb.set_categories(Reference(d, min_col=19, min_row=44, max_row=53))
tb.series[0].graphicalProperties.solidFill = DEEP
tb.series[0].graphicalProperties.line.noFill = True
tb.x_axis.scaling.orientation = "maxMin"
style_axes(tb)
tb.legend = None
tb.width, tb.height = CM_W, CM_H
frame(tb)
d.add_chart(tb, "B34")

# 4. where every dollar goes (100% stacked)
ps = BarChart()
ps.type = "bar"
ps.grouping = "percentStacked"
ps.overlap = 100
ps.gapWidth = 40
ps.add_data(Reference(d, min_col=20, max_col=24, min_row=56, max_row=57), titles_from_data=True)
ps.set_categories(Reference(d, min_col=19, min_row=57, max_row=57))
for sr, colr in zip(ps.series, [CLAY, GOLD, MIST, SAND, DEEP]):
    sr.graphicalProperties.solidFill = colr
    sr.graphicalProperties.line.solidFill = "FFFFFF"
style_axes(ps, "0%")
ps.legend.position = "b"
ps.legend.overlay = False
ps.width, ps.height = CM_W, CM_H
frame(ps)
d.add_chart(ps, "J34")

# 5. expense categories
eb = BarChart()
eb.type = "bar"
eb.gapWidth = 45
eb.add_data(Reference(d, min_col=20, min_row=60, max_row=68), titles_from_data=True)
eb.set_categories(Reference(d, min_col=19, min_row=61, max_row=68))
eb.series[0].graphicalProperties.solidFill = CLAY
eb.series[0].graphicalProperties.line.noFill = True
eb.x_axis.scaling.orientation = "maxMin"
style_axes(eb)
eb.legend = None
eb.width, eb.height = CM_W, CM_H
frame(eb)
d.add_chart(eb, "B51")

# --- action list (J51:P66)
for r in range(51, 67):
    for col in "JKLMNOP":
        d[f"{col}{r}"].fill = fill(CARD)
    d[f"J{r}"].border = Border(left=CARD_BD)
    d[f"P{r}"].border = Border(right=CARD_BD)


def al_header(r, title):
    d.merge_cells(f"J{r}:L{r}")
    d[f"J{r}"] = title
    for col, t in [("N", "Days Left"), ("O", "Make / Buy"), ("P", "Status")]:
        d[f"{col}{r}"] = t
    for col in "JKLMNOP":
        c = d[f"{col}{r}"]
        c.fill, c.font = fill(SAND), font(9, True, DEEP)
        c.alignment = Alignment(horizontal="left" if col == "J" else "center", vertical="center", indent=1 if col == "J" else 0)


def al_rows(r0, sheet, name_col, days_col, qty_col, status_col, rank_col, last):
    for k in range(1, 6):
        r = r0 + k - 1
        m = f"MATCH({k},{sheet}!${rank_col}$6:${rank_col}${last},0)"
        d.merge_cells(f"J{r}:L{r}")
        d[f"J{r}"] = f'=IFERROR(INDEX({sheet}!${name_col}$6:${name_col}${last},{m}),"")'
        d[f"N{r}"] = f'=IFERROR(INDEX({sheet}!${days_col}$6:${days_col}${last},{m}),"")'
        d[f"O{r}"] = f'=IFERROR(INDEX({sheet}!${qty_col}$6:${qty_col}${last},{m}),"")'
        d[f"P{r}"] = f'=IFERROR(INDEX({sheet}!${status_col}$6:${status_col}${last},{m}),"")'
        d[f"J{r}"].font = font(9, False, INK)
        d[f"J{r}"].alignment = Alignment(indent=1, vertical="center", shrink_to_fit=True)
        for col, fmt in (("N", "days"), ("O", "qty")):
            d[f"{col}{r}"].number_format = FMT[fmt]
            d[f"{col}{r}"].font = font(10, False, CALC_TXT)
            d[f"{col}{r}"].alignment = Alignment(horizontal="center", vertical="center")
        d[f"P{r}"].font = font(8, True, INK)
        d[f"P{r}"].alignment = Alignment(horizontal="center", vertical="center", shrink_to_fit=True)
        for col in "JKLMNOP":
            d[f"{col}{r}"].border = Border(bottom=side(LINE), left=CARD_BD if col == "J" else None,
                                           right=CARD_BD if col == "P" else None)
    badge_cf(d, f"P{r0}:P{r0 + 4}")


al_header(52, "Finished Products")
al_rows(53, "Products", "B", "R", "V", "W", "AB", P1)
al_header(59, "Materials & Packaging")
al_rows(60, "Materials", "B", "S", "W", "X", "Z", M1)
d.merge_cells("J65:P66")
d["J65"] = "Ranked by fewest days of stock left. Full lists: Products & Materials tabs."
d["J65"].font = font(8, False, MUTED, italic=True)
d["J65"].alignment = Alignment(wrap_text=True, vertical="center", indent=1)
for col in "JKLMNOP":
    d[f"{col}66"].border = Border(bottom=CARD_BD, left=CARD_BD if col == "J" else None, right=CARD_BD if col == "P" else None)
for r in (51, 58):
    d.row_dimensions[r].height = 8 if r == 51 else 10
d.print_area = "B2:P67"
d.page_setup.orientation = "portrait"
d.page_setup.fitToWidth = 1
d.page_setup.fitToHeight = 1
d.sheet_properties.pageSetUpPr.fitToPage = True
d.print_options.horizontalCentered = True
d.page_margins.left = d.page_margins.right = 0.3

# ================================================================== currency CF on all money ranges
CUR_FMTS = {
    "USD": '"$"#,##0.00;-"$"#,##0.00;"–"',
    "EUR": '"€"#,##0.00;-"€"#,##0.00;"–"',
    "GBP": '"£"#,##0.00;-"£"#,##0.00;"–"',
    "CAD": '"CA$"#,##0.00;-"CA$"#,##0.00;"–"',
    "AUD": '"AU$"#,##0.00;-"AU$"#,##0.00;"–"',
}
for i, (code, fc) in enumerate(CUR_FMTS.items()):
    dxfs = {2: DifferentialStyle(numFmt=NumberFormat(numFmtId=300 + i, formatCode=fc)),
            0: DifferentialStyle(numFmt=NumberFormat(numFmtId=310 + i, formatCode=fc.replace(".00", "")))}
    for (sheet, dec), ranges in MONEY_RANGES.items():
        rule = Rule(type="expression", dxf=dxfs[dec], formula=[f'CUR_CODE="{code}"'])
        wb[sheet].conditional_formatting.add(" ".join(ranges), rule)

# ================================================================== SAMPLE DATA
sales = sd.build_sales()
log = sd.build_stock_log(sales)
exps = sd.build_expenses()
for i, p in enumerate(sd.PRODUCTS):
    r = P0 + i
    sku, nm_, coll, price, opening, labor, lead, *_ = p
    for col, v in zip("ABCDEFG", (sku, nm_, coll, price, opening, labor, lead)):
        PROD[f"{col}{r}"] = v
PROD[f"H{P0}"] = 10  # one example override of safety days
for i, m in enumerate(sd.MATERIALS):
    r = M0 + i
    mid, nm_, cat, unit, sup, opening, cost, lead, moq = m
    for col, v in zip("ABCDEFGHJ", (mid, nm_, cat, unit, sup, opening, cost, lead, moq)):
        MATS[f"{col}{r}"] = v
r = R0
for sku, lines in sd.RECIPES.items():
    for mid, qty in lines:
        RECI[f"A{r}"], RECI[f"B{r}"], RECI[f"C{r}"] = sku, mid, qty
        w = sd.WASTE.get(mid, 0)
        RECI[f"D{r}"] = w if w else None
        r += 1
RECIPE_ROWS = r - R0
for i, s in enumerate(sales):
    r = S0 + i
    vals = (s["date"], s["oid"], s["ch"], s["sku"], s["qty"], s["price"], s["disc"] or None, s["ship"] or None,
            s["tax"] or None, s["ad"], s["label"] or None, s["status"])
    for col, v in zip("ABCDEFGHIJKL", vals):
        SALES[f"{col}{r}"] = v
for i, e in enumerate(log):
    r = L0 + i
    vals = (e["date"], e["type"], e["sku"] or None, e["mid"] or None, e["qty"], e["cost"], e["freight"] or None,
            e["supplier"] or None, e["status"] or None, e["expected"], e["ref"] or None, e["notes"] or None)
    for col, v in zip("ABCDEFGHIJKL", vals):
        LOG[f"{col}{r}"] = v
for i, e in enumerate(exps):
    r = E0 + i
    vals = (e["date"], e["vendor"], e["desc"], e["cat"], e["amt"], e["pay"], e["rec"], e["ded"])
    for col, v in zip("ABCDEFGH", vals):
        EXP[f"{col}{r}"] = v
EXP[f"G{E0 + 5}"] = "No"  # one missing receipt to demo the flag

# ================================================================== dynamic print areas (print only rows in use)
for w, last_col, first, last in [(SALES, "X", S0, S1), (PROD, "Z", P0, P1), (MATS, "X", M0, M1), (RECI, "K", R0, R1),
                                 (LOG, "N", L0, L1), (EXP, "K", E0, E1)]:
    t = q(w.title)
    w.defined_names["_xlnm.Print_Area"] = DefinedName(
        "_xlnm.Print_Area", localSheetId=wb.index(w),
        attr_text=f"{t}!$A$1:INDEX({t}!${last_col}${first}:${last_col}${last},MAX(1,COUNTA({t}!$A${first}:$A${last})))")

# ================================================================== protection
for w in wb.worksheets:
    p = w.protection
    p.sheet = True
    p.formatColumns = False
    p.formatRows = False
    p.formatCells = False
    p.autoFilter = False
    p.sort = False
    p.selectLockedCells = False
    p.selectUnlockedCells = False

wb.active = 0
wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print(f"saved {OUT}: {len(sales)} sales lines, {len(log)} stock moves, {len(exps)} expenses, {RECIPE_ROWS} recipe lines")
