"""Shared styling helpers for Etsy spreadsheet products (Excel + Google Sheets compatible).

Rules that keep files working after a Google Sheets import:
- only classic functions (SUMIFS, COUNTIFS, COUNTA, IFERROR, DATE, EOMONTH, TEXT), no dynamic arrays;
- list-type data validation and simple conditional formatting only;
- one font family (Arial) so Excel and Sheets render the same.
"""
from __future__ import annotations

from dataclasses import dataclass

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FONT = "Arial"


@dataclass(frozen=True)
class Palette:
    primary: str    # header bars, titles
    accent: str     # highlights, progress
    soft: str       # input-cell tint / banding
    ink: str = "2B2B2B"
    muted: str = "8A8A8A"
    paper: str = "FFFFFF"
    line: str = "E3E3E3"


def fill(hex_: str) -> PatternFill:
    return PatternFill("solid", start_color=hex_, end_color=hex_)


def thin(color: str) -> Border:
    s = Side(style="thin", color=color)
    return Border(left=s, right=s, top=s, bottom=s)


def base_sheet(ws, pal: Palette, widths: dict[str, float] | None = None, tab: str | None = None):
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = tab or pal.primary
    for col, w in (widths or {}).items():
        ws.column_dimensions[col].width = w


def title(ws, pal: Palette, text: str, subtitle: str = "", span: int = 8, row: int = 1):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=20, bold=True, color=pal.primary)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 36
    if subtitle:
        ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=span)
        s = ws.cell(row=row + 1, column=1, value=subtitle)
        s.font = Font(name=FONT, size=10, italic=True, color=pal.muted)
        s.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row + 1].height = 30


def header_row(ws, pal: Palette, row: int, headers: list[str], start_col: int = 1):
    for i, h in enumerate(headers):
        c = ws.cell(row=row, column=start_col + i, value=h)
        c.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        c.fill = fill(pal.primary)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = thin(pal.primary)
    ws.row_dimensions[row].height = 30


def input_block(ws, pal: Palette, first_row: int, n_rows: int, first_col: int, n_cols: int,
                band: bool = True, number_formats: dict[int, str] | None = None):
    """Formatted empty rows the buyer types into."""
    for r in range(first_row, first_row + n_rows):
        for ci in range(first_col, first_col + n_cols):
            c = ws.cell(row=r, column=ci)
            c.font = Font(name=FONT, size=10, color=pal.ink)
            c.border = thin(pal.line)
            c.alignment = Alignment(vertical="center", wrap_text=True)
            if band and (r - first_row) % 2 == 1:
                c.fill = fill(pal.soft)
            if number_formats and ci in number_formats:
                c.number_format = number_formats[ci]
        ws.row_dimensions[r].height = 20


def label_value(ws, pal: Palette, row: int, label: str, value=None, col: int = 1,
                fmt: str | None = None, bold_value: bool = True, value_col_offset: int = 1):
    lc = ws.cell(row=row, column=col, value=label)
    lc.font = Font(name=FONT, size=10, color=pal.muted)
    vc = ws.cell(row=row, column=col + value_col_offset, value=value)
    vc.font = Font(name=FONT, size=12, bold=bold_value, color=pal.ink)
    if fmt:
        vc.number_format = fmt
    return vc


def kpi(ws, pal: Palette, row: int, col: int, label: str, formula: str, fmt: str = "#,##0.00",
        width_cols: int = 2):
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + width_cols - 1)
    ws.merge_cells(start_row=row + 1, start_column=col, end_row=row + 1, end_column=col + width_cols - 1)
    l = ws.cell(row=row, column=col, value=label.upper())
    l.font = Font(name=FONT, size=8, bold=True, color=pal.muted)
    l.fill = fill(pal.soft)
    l.alignment = Alignment(horizontal="center", vertical="bottom")
    v = ws.cell(row=row + 1, column=col, value=formula)
    v.font = Font(name=FONT, size=18, bold=True, color=pal.primary)
    v.fill = fill(pal.soft)
    v.number_format = fmt
    v.alignment = Alignment(horizontal="center", vertical="center")
    for ci in range(col, col + width_cols):
        ws.cell(row=row, column=ci).fill = fill(pal.soft)
        ws.cell(row=row + 1, column=ci).fill = fill(pal.soft)
    ws.row_dimensions[row].height = 20
    ws.row_dimensions[row + 1].height = 34


def list_validation(ws, sqref: str, formula: str, prompt: str | None = None):
    dv = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
    if prompt:
        dv.promptTitle, dv.prompt, dv.showInputMessage = "Pick one", prompt, True
    dv.error, dv.errorTitle, dv.showErrorMessage = "Please pick a value from the list.", "Not in list", True
    ws.add_data_validation(dv)
    dv.add(sqref)
    return dv


def note(ws, pal: Palette, row: int, text: str, span: int = 8, col: int = 1, height: float = 30):
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + span - 1)
    c = ws.cell(row=row, column=col, value=text)
    c.font = Font(name=FONT, size=9, italic=True, color=pal.muted)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = height


def col(i: int) -> str:
    return get_column_letter(i)


def set_print(ws, landscape: bool = True):
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
