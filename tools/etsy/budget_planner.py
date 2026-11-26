"""2027 Budget Planner: transactions log -> monthly summary -> yearly dashboard (Excel + Google Sheets)."""
from __future__ import annotations

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, Font

from .xlsx_kit import (FONT, Palette, base_sheet, col, fill, header_row, input_block, kpi,
                       list_validation, note, set_print, thin, title)

PAL = Palette(primary="2F4B7C", accent="F4A259", soft="EEF2F8")
YEAR = 2027
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
INCOME = ["Salary", "Side hustle", "Freelance", "Gifts", "Refunds", "Other income"]
EXPENSE = ["Rent / Mortgage", "Utilities", "Groceries", "Dining out", "Transport", "Car payment", "Insurance",
           "Phone & Internet", "Subscriptions", "Health", "Personal care", "Clothing", "Kids", "Pets",
           "Entertainment", "Travel", "Gifts & Donations", "Debt payments", "Savings transfer", "Other"]
SLOTS_IN, SLOTS_EX = 10, 26          # category slots (buyer can rename/add)
TX_ROWS = 1500
TX_FIRST = 5
MONEY = '"$"#,##0.00'


def _setup(wb):
    ws = wb.active
    ws.title = "Setup"
    base_sheet(ws, PAL, {"A": 3, "B": 26, "C": 16, "D": 4, "E": 26, "F": 16}, tab=PAL.accent)
    title(ws, PAL, f"{YEAR} Budget Planner", "Step 1: rename or add categories and set a monthly budget for each. "
          "Step 2: log every transaction on the Transactions tab. Everything else updates itself.", span=6)
    ws.cell(row=4, column=2, value="Year").font = Font(name=FONT, size=10, color=PAL.muted)
    y = ws.cell(row=4, column=3, value=YEAR)
    y.font = Font(name=FONT, size=12, bold=True)
    y.fill, y.border = fill(PAL.soft), thin(PAL.line)
    header_row(ws, PAL, 6, ["Income category", "Monthly target"], start_col=2)
    header_row(ws, PAL, 6, ["Expense category", "Monthly budget"], start_col=5)
    input_block(ws, PAL, 7, SLOTS_IN, 2, 2, number_formats={3: MONEY})
    input_block(ws, PAL, 7, SLOTS_EX, 5, 2, number_formats={6: MONEY})
    for i, c in enumerate(INCOME):
        ws.cell(row=7 + i, column=2, value=c)
    for i, c in enumerate(EXPENSE):
        ws.cell(row=7 + i, column=5, value=c)
    r = 7 + SLOTS_IN + 1
    ws.cell(row=r, column=2, value="Total target").font = Font(name=FONT, bold=True, color=PAL.primary)
    t = ws.cell(row=r, column=3, value=f"=SUM(C7:C{6 + SLOTS_IN})")
    t.font, t.number_format = Font(name=FONT, bold=True, color=PAL.primary), MONEY
    r2 = 7 + SLOTS_EX + 1
    ws.cell(row=r2, column=5, value="Total budget").font = Font(name=FONT, bold=True, color=PAL.primary)
    t = ws.cell(row=r2, column=6, value=f"=SUM(F7:F{6 + SLOTS_EX})")
    t.font, t.number_format = Font(name=FONT, bold=True, color=PAL.primary), MONEY
    # hidden helper: combined category list for the Transactions dropdown
    ws.column_dimensions["H"].hidden = True
    ws["H6"] = "All categories"
    for i in range(SLOTS_IN):
        ws.cell(row=7 + i, column=8, value=f'=IF(B{7 + i}="","",B{7 + i})')
    for i in range(SLOTS_EX):
        ws.cell(row=7 + SLOTS_IN + i, column=8, value=f'=IF(E{7 + i}="","",E{7 + i})')
    set_print(ws, landscape=False)


def _transactions(wb):
    ws = wb.create_sheet("Transactions")
    base_sheet(ws, PAL, {"A": 13, "B": 34, "C": 12, "D": 22, "E": 14, "F": 18, "G": 8})
    title(ws, PAL, "Transactions", "One row per transaction. Pick Income or Expense, then a category. "
          "Amounts are always positive.", span=6)
    header_row(ws, PAL, TX_FIRST - 1, ["Date", "Description", "Type", "Category", "Amount", "Paid with", "Month"])
    input_block(ws, PAL, TX_FIRST, TX_ROWS, 1, 6, number_formats={1: "mm/dd/yyyy", 5: MONEY})
    last = TX_FIRST + TX_ROWS - 1
    list_validation(ws, f"C{TX_FIRST}:C{last}", '"Income,Expense"')
    list_validation(ws, f"D{TX_FIRST}:D{last}", f"=Setup!$H$7:$H${6 + SLOTS_IN + SLOTS_EX}")
    list_validation(ws, f"F{TX_FIRST}:F{last}", '"Cash,Debit card,Credit card,Bank transfer,Other"')
    for r in range(TX_FIRST, last + 1):
        c = ws.cell(row=r, column=7, value=f'=IF(A{r}="","",MONTH(A{r}))')
        c.font = Font(name=FONT, size=9, color=PAL.muted)
        c.alignment = Alignment(horizontal="center")
    # sample rows so the dashboard is not empty on first open (buyer deletes them)
    samples = [(f"01/01/{YEAR}", "Paycheck (sample, delete me)", "Income", "Salary", 3200),
               (f"01/02/{YEAR}", "Rent (sample, delete me)", "Expense", "Rent / Mortgage", 1250),
               (f"01/05/{YEAR}", "Groceries (sample, delete me)", "Expense", "Groceries", 142.37)]
    from datetime import datetime
    for i, (d, desc, typ, cat, amt) in enumerate(samples):
        r = TX_FIRST + i
        ws.cell(row=r, column=1, value=datetime.strptime(d, "%m/%d/%Y"))
        ws.cell(row=r, column=2, value=desc)
        ws.cell(row=r, column=3, value=typ)
        ws.cell(row=r, column=4, value=cat)
        ws.cell(row=r, column=5, value=amt)
    ws.freeze_panes = f"A{TX_FIRST}"
    ws.auto_filter.ref = f"A{TX_FIRST - 1}:G{last}"
    return last


def _monthly(wb, last):
    ws = wb.create_sheet("Monthly")
    widths = {"A": 24, "B": 13}
    for m in range(12):
        widths[col(3 + m)] = 11
    widths[col(15)] = 13
    widths[col(16)] = 13
    base_sheet(ws, PAL, widths)
    title(ws, PAL, "Monthly Summary", "Actuals by category and month, pulled from Transactions. "
          "Red = over the monthly budget.", span=16)
    tx = "Transactions!"
    rngs = dict(type=f"{tx}$C${TX_FIRST}:$C${last}", cat=f"{tx}$D${TX_FIRST}:$D${last}",
                amt=f"{tx}$E${TX_FIRST}:$E${last}", mon=f"{tx}$G${TX_FIRST}:$G${last}")

    def block(start, label, setup_col, budget_col, n, typ):
        header_row(ws, PAL, start, [label, "Monthly plan", *MONTHS, "Year total", "Avg / month"])
        for i in range(n):
            r = start + 1 + i
            src = 7 + i
            ws.cell(row=r, column=1, value=f'=IF(Setup!{setup_col}{src}="","",Setup!{setup_col}{src})')
            ws.cell(row=r, column=2, value=f'=IF(A{r}="","",Setup!{budget_col}{src})').number_format = MONEY
            for m in range(12):
                c = ws.cell(row=r, column=3 + m,
                            value=f'=IF($A{r}="","",SUMIFS({rngs["amt"]},{rngs["type"]},"{typ}",'
                                  f'{rngs["cat"]},$A{r},{rngs["mon"]},{m + 1}))')
                c.number_format = MONEY
            ws.cell(row=r, column=15, value=f'=IF(A{r}="","",SUM(C{r}:N{r}))').number_format = MONEY
            ws.cell(row=r, column=16, value=f'=IF(A{r}="","",O{r}/12)').number_format = MONEY
            for ci in range(1, 17):
                cell = ws.cell(row=r, column=ci)
                cell.border = thin(PAL.line)
                cell.font = Font(name=FONT, size=10, bold=(ci == 1), color=PAL.ink)
                if i % 2:
                    cell.fill = fill(PAL.soft)
        tr = start + n + 1
        ws.cell(row=tr, column=1, value=f"Total {typ.lower()}")
        for ci in range(2, 17):
            L = col(ci)
            ws.cell(row=tr, column=ci, value=f"=SUM({L}{start + 1}:{L}{start + n})").number_format = MONEY
        for ci in range(1, 17):
            cell = ws.cell(row=tr, column=ci)
            cell.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
            cell.fill = fill(PAL.accent if typ == "Expense" else PAL.primary)
        return start + 1, start + n, tr

    in_first, in_last, in_total = block(4, "Income", "B", "C", SLOTS_IN, "Income")
    ex_first, ex_last, ex_total = block(in_total + 2, "Expenses", "E", "F", SLOTS_EX, "Expense")
    # over-budget highlight on expense months
    ws.conditional_formatting.add(
        f"C{ex_first}:N{ex_last}",
        CellIsRule(operator="greaterThan", formula=[f"$B{ex_first}"], font=Font(color="C0392B", bold=True)))
    net = ex_total + 2
    ws.cell(row=net, column=1, value="Net (income - expenses)")
    ws.cell(row=net + 1, column=1, value="Savings rate")
    for ci in range(3, 16):
        L = col(ci)
        ws.cell(row=net, column=ci, value=f"={L}{in_total}-{L}{ex_total}").number_format = MONEY
        ws.cell(row=net + 1, column=ci, value=f'=IF({L}{in_total}=0,"",{L}{net}/{L}{in_total})').number_format = "0%"
    for r in (net, net + 1):
        for ci in range(1, 17):
            ws.cell(row=r, column=ci).font = Font(name=FONT, size=10, bold=True, color=PAL.primary)
            ws.cell(row=r, column=ci).border = thin(PAL.line)
    ws.freeze_panes = "C4"
    set_print(ws)
    return dict(in_total=in_total, ex_total=ex_total, net=net, ex_first=ex_first, ex_last=ex_last)


def _dashboard(wb, m):
    ws = wb.create_sheet("Dashboard", 1)
    base_sheet(ws, PAL, {c: 12 for c in "ABCDEFGHIJKLMN"}, tab=PAL.accent)
    ws.column_dimensions["A"].width = 3
    title(ws, PAL, f"{YEAR} Dashboard", "Updates automatically from your Transactions.", span=13)
    kpi(ws, PAL, 4, 2, "Income (year)", f"=Monthly!O{m['in_total']}", MONEY, 3)
    kpi(ws, PAL, 4, 5, "Expenses (year)", f"=Monthly!O{m['ex_total']}", MONEY, 3)
    kpi(ws, PAL, 4, 8, "Saved (year)", f"=Monthly!O{m['net']}", MONEY, 3)
    kpi(ws, PAL, 4, 11, "Savings rate", f"=Monthly!O{m['net'] + 1}", "0%", 3)

    # month table feeding the chart
    header_row(ws, PAL, 8, ["Month", "Income", "Expenses", "Net"], start_col=2)
    for i, mon in enumerate(MONTHS):
        r = 9 + i
        L = col(3 + i)
        ws.cell(row=r, column=2, value=mon)
        ws.cell(row=r, column=3, value=f"=Monthly!{L}{m['in_total']}").number_format = MONEY
        ws.cell(row=r, column=4, value=f"=Monthly!{L}{m['ex_total']}").number_format = MONEY
        ws.cell(row=r, column=5, value=f"=C{r}-D{r}").number_format = MONEY
        for ci in range(2, 6):
            cell = ws.cell(row=r, column=ci)
            cell.border = thin(PAL.line)
            cell.font = Font(name=FONT, size=10, color=PAL.ink)
    ch = BarChart()
    ch.type, ch.grouping, ch.title = "col", "clustered", "Income vs expenses"
    ch.y_axis.numFmt = "$#,##0"
    ch.add_data(Reference(ws, min_col=3, max_col=4, min_row=8, max_row=20), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=2, min_row=9, max_row=20))
    ch.height, ch.width = 7.5, 17
    ws.add_chart(ch, "G8")

    # top spending categories (year) with budget use
    r0 = 23
    header_row(ws, PAL, r0, ["Expense category", "", "Spent (year)", "Budget (year)", "% of budget"], start_col=2)
    ws.merge_cells(start_row=r0, start_column=2, end_row=r0, end_column=3)
    n = m["ex_last"] - m["ex_first"] + 1
    for i in range(n):
        r = r0 + 1 + i
        src = m["ex_first"] + i
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        ws.cell(row=r, column=2, value=f"=Monthly!A{src}")
        ws.cell(row=r, column=4, value=f'=IF(Monthly!A{src}="","",Monthly!O{src})').number_format = MONEY
        ws.cell(row=r, column=5, value=f'=IF(Monthly!A{src}="","",Monthly!B{src}*12)').number_format = MONEY
        ws.cell(row=r, column=6, value=f'=IF(OR(E{r}="",E{r}=0),"",D{r}/E{r})').number_format = "0%"
        for ci in range(2, 7):
            cell = ws.cell(row=r, column=ci)
            cell.border = thin(PAL.line)
            cell.font = Font(name=FONT, size=10, color=PAL.ink)
            if i % 2:
                cell.fill = fill(PAL.soft)
    end = r0 + n
    ws.conditional_formatting.add(f"F{r0 + 1}:F{end}", DataBarRule(start_type="num", start_value=0,
                                                                   end_type="num", end_value=1.2, color=PAL.accent))
    note(ws, PAL, end + 2, "Tip: delete the three sample rows on the Transactions tab before you start.", span=12,
         col=2)
    set_print(ws)


def _goals(wb):
    ws = wb.create_sheet("Savings Goals")
    base_sheet(ws, PAL, {"A": 26, "B": 14, "C": 14, "D": 14, "E": 14, "F": 16, "G": 30})
    title(ws, PAL, "Savings Goals", "Emergency fund, vacation, new car... add what you save each time.", span=7)
    header_row(ws, PAL, 4, ["Goal", "Target", "Saved so far", "Remaining", "Progress", "Target date", "Notes"])
    input_block(ws, PAL, 5, 12, 1, 7, number_formats={2: MONEY, 3: MONEY, 6: "mm/dd/yyyy"})
    for r in range(5, 17):
        ws.cell(row=r, column=4, value=f'=IF(B{r}="","",MAX(0,B{r}-C{r}))').number_format = MONEY
        ws.cell(row=r, column=5, value=f'=IF(OR(B{r}="",B{r}=0),"",MIN(1,C{r}/B{r}))').number_format = "0%"
    ws.conditional_formatting.add("E5:E16", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                        end_value=1, color=PAL.accent))
    for i, g in enumerate(["Emergency fund", "Vacation", "New car"]):
        ws.cell(row=5 + i, column=1, value=g)


def _debts(wb):
    ws = wb.create_sheet("Debt Payoff")
    base_sheet(ws, PAL, {"A": 24, "B": 14, "C": 10, "D": 14, "E": 14, "F": 14, "G": 14, "H": 12})
    title(ws, PAL, "Debt Payoff Tracker", "List each debt. Months-to-payoff uses your balance, APR and payment.",
          span=8)
    header_row(ws, PAL, 4, ["Debt", "Starting balance", "APR %", "Monthly payment", "Paid so far",
                            "Current balance", "Months left (est.)", "Progress"])
    input_block(ws, PAL, 5, 12, 1, 8, number_formats={2: MONEY, 3: "0.00", 4: MONEY, 5: MONEY, 6: MONEY})
    for r in range(5, 17):
        ws.cell(row=r, column=6, value=f'=IF(B{r}="","",MAX(0,B{r}-E{r}))').number_format = MONEY
        # NPER-style estimate, safe when payment does not cover interest
        ws.cell(row=r, column=7, value=(
            f'=IF(OR(F{r}="",D{r}="",D{r}=0),"",IF(F{r}=0,0,IF(C{r}=0,ROUNDUP(F{r}/D{r},0),'
            f'IF(D{r}<=F{r}*C{r}/1200,"Payment too low",ROUNDUP(NPER(C{r}/1200,-D{r},F{r}),0)))))'))
        ws.cell(row=r, column=8, value=f'=IF(OR(B{r}="",B{r}=0),"",E{r}/B{r})').number_format = "0%"
    ws.conditional_formatting.add("H5:H16", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                        end_value=1, color=PAL.accent))
    note(ws, PAL, 18, "Estimates only; your lender's statement is the source of truth. Not financial advice.", span=8)


def build(path):
    wb = Workbook()
    _setup(wb)
    last = _transactions(wb)
    m = _monthly(wb, last)
    _dashboard(wb, m)
    _goals(wb)
    _debts(wb)
    wb.active = 0
    wb.save(path)
    return path
