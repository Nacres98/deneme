"""2027 Habit Tracker: 12 monthly grids + yearly heatmap dashboard (Excel + Google Sheets)."""
from __future__ import annotations

from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Font

from .xlsx_kit import (FONT, Palette, base_sheet, col, fill, header_row, input_block, kpi,
                       list_validation, note, set_print, thin, title)

PAL = Palette(primary="6B4E71", accent="E8A0BF", soft="F7F0F5")
YEAR = 2027
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
HABITS = 12
DEFAULTS = ["Drink 8 glasses of water", "Move 30 minutes", "Read 10 pages", "No phone first hour",
            "Sleep by 11 pm", "Journal", "Meditate 5 min", "Eat a vegetable"]
DONE = "✓"
GRID_FIRST_ROW = 6


def _setup(wb):
    ws = wb.active
    ws.title = "Setup"
    base_sheet(ws, PAL, {"A": 3, "B": 6, "C": 36, "D": 18}, tab=PAL.accent)
    title(ws, PAL, f"{YEAR} Habit Tracker", "List up to 12 habits once here. They appear on every month "
          "automatically. On the month tabs pick ✓ from the dropdown (or type it) for each day you did it.", span=4)
    ws.cell(row=4, column=3, value="Year").font = Font(name=FONT, color=PAL.muted)
    y = ws.cell(row=4, column=4, value=YEAR)
    y.font, y.fill, y.border = Font(name=FONT, size=12, bold=True), fill(PAL.soft), thin(PAL.line)
    header_row(ws, PAL, 6, ["#", "Habit", "Goal (days / month)"], start_col=2)
    input_block(ws, PAL, 7, HABITS, 2, 3)
    for i in range(HABITS):
        ws.cell(row=7 + i, column=2, value=i + 1).alignment = Alignment(horizontal="center")
        if i < len(DEFAULTS):
            ws.cell(row=7 + i, column=3, value=DEFAULTS[i])
            ws.cell(row=7 + i, column=4, value=20)
    note(ws, PAL, 7 + HABITS + 1, "Change the Year cell and every calendar re-dates itself.", span=3, col=2)
    set_print(ws, landscape=False)


def _month(wb, m):
    name = MONTHS[m]
    ws = wb.create_sheet(name[:3])
    widths = {"A": 30}
    for d in range(31):
        widths[col(2 + d)] = 3.6
    widths[col(33)] = 8
    widths[col(34)] = 9
    widths[col(35)] = 10
    base_sheet(ws, PAL, widths)
    ws.merge_cells("A1:AI1")
    ws["A1"] = f'=UPPER("{name} ")&Setup!D4'
    ws["A1"].font = Font(name=FONT, size=20, bold=True, color=PAL.primary)
    ws.row_dimensions[1].height = 36
    ws["A2"] = "Pick ✓ for each day you did the habit."
    ws["A2"].font = Font(name=FONT, size=9, italic=True, color=PAL.muted)
    hr_day, hr_num = 4, 5
    ws.cell(row=hr_num, column=1, value="Habit")
    for d in range(31):
        c = 2 + d
        ws.cell(row=hr_day, column=c,
                value=f'=IF(MONTH(DATE(Setup!$D$4,{m + 1},{d + 1}))<>{m + 1},"",'
                      f'LEFT(TEXT(DATE(Setup!$D$4,{m + 1},{d + 1}),"ddd"),2))')
        ws.cell(row=hr_num, column=c,
                value=f'=IF(MONTH(DATE(Setup!$D$4,{m + 1},{d + 1}))<>{m + 1},"",{d + 1})')
    for ci, h in ((33, "Done"), (34, "Goal"), (35, "Progress")):
        ws.cell(row=hr_num, column=ci, value=h)
    for ci in range(1, 36):
        for r in (hr_day, hr_num):
            cell = ws.cell(row=r, column=ci)
            cell.font = Font(name=FONT, size=8 if r == hr_day else 9, bold=(r == hr_num),
                             color=PAL.muted if r == hr_day else "FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if r == hr_num:
                cell.fill = fill(PAL.primary)
    days_in = f"DAY(EOMONTH(DATE(Setup!$D$4,{m + 1},1),0))"
    first, last = GRID_FIRST_ROW, GRID_FIRST_ROW + HABITS - 1
    input_block(ws, PAL, first, HABITS, 2, 31, band=False)
    for i in range(HABITS):
        r = first + i
        a = ws.cell(row=r, column=1, value=f'=IF(Setup!C{7 + i}="","",Setup!C{7 + i})')
        a.font = Font(name=FONT, size=10, bold=True, color=PAL.ink)
        a.border = thin(PAL.line)
        for d in range(31):
            ws.cell(row=r, column=2 + d).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=r, column=33, value=f'=IF(A{r}="","",COUNTIF(B{r}:AF{r},"{DONE}"))')
        ws.cell(row=r, column=34, value=f'=IF(A{r}="","",MIN(Setup!D{7 + i},{days_in}))')
        ws.cell(row=r, column=35, value=f'=IF(OR(A{r}="",AH{r}="",AH{r}=0),"",MIN(1,AG{r}/AH{r}))').number_format = "0%"
        for ci in (33, 34, 35):
            cell = ws.cell(row=r, column=ci)
            cell.border = thin(PAL.line)
            cell.font = Font(name=FONT, size=10, bold=True, color=PAL.primary)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[r].height = 22
    grid = f"B{first}:AF{last}"
    list_validation(ws, grid, f'"{DONE}"')
    # done cells -> accent fill; days that don't exist in the month -> grey
    ws.conditional_formatting.add(grid, FormulaRule(formula=[f'B{first}="{DONE}"'],
                                                    fill=fill(PAL.accent), font=Font(color="FFFFFF", bold=True)))
    ws.conditional_formatting.add(grid, FormulaRule(formula=[f'B${hr_num}=""'], fill=fill("EDEDED")))
    ws.conditional_formatting.add(f"AI{first}:AI{last}", DataBarRule(start_type="num", start_value=0,
                                                                     end_type="num", end_value=1, color=PAL.accent))
    # daily completion row
    dr = last + 1
    ws.cell(row=dr, column=1, value="Daily score").font = Font(name=FONT, size=9, bold=True, color=PAL.muted)
    for d in range(31):
        L = col(2 + d)
        c = ws.cell(row=dr, column=2 + d,
                    value=f'=IF({L}${hr_num}="","",COUNTIF({L}{first}:{L}{last},"{DONE}"))')
        c.font = Font(name=FONT, size=8, color=PAL.muted)
        c.alignment = Alignment(horizontal="center")
    ws.conditional_formatting.add(f"B{dr}:AF{dr}", ColorScaleRule(start_type="num", start_value=0,
                                                                  start_color="FFFFFF", end_type="max",
                                                                  end_color=PAL.accent))
    ws.freeze_panes = "B6"
    set_print(ws)


def _dashboard(wb):
    ws = wb.create_sheet("Year Overview", 1)
    widths = {"A": 3, "B": 30}
    for m in range(12):
        widths[col(3 + m)] = 7.5
    widths[col(15)] = 10
    base_sheet(ws, PAL, widths, tab=PAL.accent)
    title(ws, PAL, "Year Overview", "Monthly progress for every habit. Darker = closer to your goal.", span=15)
    first, last = GRID_FIRST_ROW, GRID_FIRST_ROW + HABITS - 1
    kpi(ws, PAL, 4, 2, "Total check-ins",
        "=" + "+".join(f"SUM({MONTHS[m][:3]}!AG{first}:AG{last})" for m in range(12)), "#,##0", 1)
    kpi(ws, PAL, 4, 3, "Best month avg", "=IFERROR(MAX(C9:N9),0)", "0%", 4)
    kpi(ws, PAL, 4, 7, "Year average", '=IFERROR(AVERAGE(C10:N21),0)', "0%", 4)
    header_row(ws, PAL, 8, ["Habit", *[m[:3] for m in MONTHS], "Year"], start_col=2)
    ws.cell(row=9, column=2, value="All habits (avg)")
    for m in range(12):
        L = col(3 + m)
        ws.cell(row=9, column=3 + m, value=f'=IFERROR(AVERAGE({L}10:{L}21),"")').number_format = "0%"
    ws.cell(row=9, column=15, value='=IFERROR(AVERAGE(C9:N9),"")').number_format = "0%"
    for i in range(HABITS):
        r = 10 + i
        ws.cell(row=r, column=2, value=f'=IF(Setup!C{7 + i}="","",Setup!C{7 + i})')
        for m in range(12):
            ws.cell(row=r, column=3 + m, value=f'=IF($B{r}="","",{MONTHS[m][:3]}!AI{first + i})').number_format = "0%"
        ws.cell(row=r, column=15, value=f'=IF(B{r}="","",IFERROR(AVERAGE(C{r}:N{r}),""))').number_format = "0%"
    for r in range(9, 22):
        for ci in range(2, 16):
            cell = ws.cell(row=r, column=ci)
            cell.border = thin(PAL.line)
            cell.font = Font(name=FONT, size=10, bold=(ci == 2 or r == 9), color=PAL.ink)
            cell.alignment = Alignment(horizontal="left" if ci == 2 else "center", vertical="center")
        ws.row_dimensions[r].height = 22
    ws.conditional_formatting.add("C9:O21", ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                           end_type="num", end_value=1, end_color=PAL.accent))
    set_print(ws)


def build(path):
    wb = Workbook()
    _setup(wb)
    for m in range(12):
        _month(wb, m)
    _dashboard(wb)
    wb.active = 0
    wb.save(path)
    return path
