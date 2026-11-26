"""'Just In Case' Life Organizer: an estate / emergency-binder spreadsheet (Excel + Google Sheets)."""
from __future__ import annotations

from openpyxl import Workbook
from openpyxl.formatting.rule import DataBarRule
from openpyxl.styles import Alignment, Font

from .xlsx_kit import (FONT, Palette, base_sheet, col, fill, header_row, input_block, kpi,
                       list_validation, note, set_print, thin, title)

PAL = Palette(primary="3E5C50", accent="C9A66B", soft="F1F5F2")
ROWS = 40          # input rows per list sheet
FIRST = 5          # first input row on list sheets

# name, subtitle, [(header, width, number_format | None)], dropdown {header: "a,b,c"}, money column header
SECTIONS = [
    ("Personal Info", "The basics a family member needs first. Write WHERE documents are, not the numbers themselves.",
     [("Item", 28, None), ("Details", 40, None), ("Where it is kept", 30, None), ("Notes", 30, None)], {}, None),
    ("Key Contacts", "Who to call: family, executor, attorney, accountant, doctor, employer, neighbours.",
     [("Name", 24, None), ("Relationship / Role", 22, None), ("Phone", 16, None), ("Email", 26, None),
      ("Address", 30, None), ("Notify first?", 12, None), ("Notes", 26, None)],
     {"Notify first?": "Yes,No"}, None),
    ("Bank Accounts", "Checking, savings, CDs, brokerage. Last 4 digits only.",
     [("Institution", 24, None), ("Account type", 16, None), ("Last 4 digits", 12, None), ("Owner(s)", 18, None),
      ("Beneficiary / POD", 22, None), ("Approx. balance", 15, "#,##0.00"), ("Online access?", 12, None),
      ("Notes", 24, None)],
     {"Account type": "Checking,Savings,CD,Money market,Brokerage,Other",
      "Online access?": "Yes,No"}, "Approx. balance"),
    ("Retirement & Investments", "401(k), IRA, pensions, stocks, crypto (record where the wallet/seed backup is stored, never the seed).",
     [("Provider", 24, None), ("Type", 16, None), ("Last 4 digits", 12, None), ("Beneficiary", 22, None),
      ("Approx. value", 15, "#,##0.00"), ("Contact", 20, None), ("Notes", 28, None)],
     {"Type": "401(k),IRA,Roth IRA,Pension,Stocks,Bonds,Crypto,Annuity,Other"}, "Approx. value"),
    ("Insurance", "Life, health, home, auto, disability, long-term care.",
     [("Insurer", 22, None), ("Policy type", 16, None), ("Policy # (last 4)", 14, None), ("Insured person", 18, None),
      ("Beneficiary", 20, None), ("Coverage amount", 15, "#,##0.00"), ("Agent / phone", 22, None),
      ("Renewal date", 13, "mm/dd/yyyy"), ("Notes", 22, None)],
     {"Policy type": "Life,Health,Home,Renters,Auto,Disability,Long-term care,Umbrella,Pet,Other"}, None),
    ("Property & Assets", "Home, vehicles, valuables, collections, business interests.",
     [("Asset", 26, None), ("Category", 16, None), ("Location / Title held by", 26, None),
      ("Est. value", 15, "#,##0.00"), ("Documents kept at", 24, None), ("Who should receive it", 22, None),
      ("Notes", 22, None)],
     {"Category": "Real estate,Vehicle,Jewelry,Art,Collectible,Electronics,Business,Other"}, "Est. value"),
    ("Debts & Loans", "Mortgage, car loans, credit cards, student loans, personal loans.",
     [("Lender", 22, None), ("Type", 16, None), ("Last 4 digits", 12, None), ("Balance owed", 15, "#,##0.00"),
      ("Monthly payment", 15, "#,##0.00"), ("Due day", 10, None), ("Autopay?", 10, None), ("Notes", 24, None)],
     {"Type": "Mortgage,Auto loan,Credit card,Student loan,Personal loan,Medical,Other", "Autopay?": "Yes,No"},
     "Balance owed"),
    ("Bills & Subscriptions", "Everything that charges automatically, so it can be cancelled or transferred.",
     [("Service", 24, None), ("Category", 16, None), ("Amount", 12, "#,##0.00"), ("Frequency", 12, None),
      ("Paid from", 20, None), ("Account login hint", 22, None), ("Cancel or keep?", 14, None), ("Notes", 22, None)],
     {"Category": "Utility,Phone,Internet,Streaming,Software,Membership,Insurance,Charity,Other",
      "Frequency": "Monthly,Quarterly,Yearly,Weekly", "Cancel or keep?": "Cancel,Keep,Transfer"}, None),
    ("Digital Accounts", "Email, social media, cloud photos. Do NOT type passwords here: note your password manager and legacy contact instead.",
     [("Service", 22, None), ("Username / email", 26, None), ("Where the password is kept", 26, None),
      ("2-factor device", 16, None), ("Wish for account", 18, None), ("Notes", 26, None)],
     {"Wish for account": "Memorialize,Delete,Transfer,Download data first"}, None),
    ("Medical", "Doctors, conditions, medications, allergies, advance directive location.",
     [("Person", 18, None), ("Type", 16, None), ("Name / Detail", 28, None), ("Dose / Phone", 18, None),
      ("Notes", 34, None)],
     {"Type": "Doctor,Medication,Condition,Allergy,Pharmacy,Directive,Organ donor,Other"}, None),
    ("Final Wishes", "Funeral, burial or cremation, service, music, readings, obituary notes.",
     [("Topic", 26, None), ("My wish", 50, None), ("Pre-arranged with", 24, None), ("Notes", 26, None)], {}, None),
    ("Document Locator", "Where each original document is: safe, filing cabinet, attorney, safe-deposit box.",
     [("Document", 28, None), ("Location", 28, None), ("Who has a copy", 22, None), ("Last updated", 13, "mm/dd/yyyy"),
      ("Notes", 26, None)], {}, None),
    ("Pets & Dependents", "Care instructions for pets and anyone who depends on you.",
     [("Name", 18, None), ("Type / Relation", 16, None), ("Vet / Doctor", 22, None), ("Routine & needs", 36, None),
      ("Preferred caregiver", 22, None), ("Notes", 22, None)], {}, None),
]

PREFILL = {
    "Personal Info": ["Full legal name", "Date of birth", "Social Security card", "Birth certificate", "Passport",
                      "Driver's license", "Marriage / divorce papers", "Military records", "Employer & HR contact",
                      "Will", "Trust documents", "Power of attorney", "Safe-deposit box (bank & key)"],
    "Final Wishes": ["Burial or cremation", "Funeral home", "Type of service", "Location of service",
                     "Music", "Readings / speakers", "Flowers or donations to", "Obituary details",
                     "Clothing / jewelry", "Who should be invited", "Reception / gathering"],
    "Document Locator": ["Will", "Trust", "Power of attorney", "Healthcare directive", "Property deeds",
                         "Vehicle titles", "Tax returns (last 7 years)", "Insurance policies", "Birth certificate",
                         "Passport", "Marriage certificate", "Spare keys"],
}


def _start_here(wb, owner_cell="C6"):
    ws = wb.active
    ws.title = "Start Here"
    base_sheet(ws, PAL, {"A": 3, "B": 26, "C": 60, "D": 20}, tab=PAL.accent)
    ws.merge_cells("B2:D2")
    ws["B2"] = "Just In Case Life Organizer"
    ws["B2"].font = Font(name=FONT, size=24, bold=True, color=PAL.primary)
    ws.row_dimensions[2].height = 40
    ws.merge_cells("B3:D3")
    ws["B3"] = "Everything your family would need, in one place."
    ws["B3"].font = Font(name=FONT, size=11, italic=True, color=PAL.muted)
    rows = [
        ("Prepared by", None),
        ("Last updated", None),
        ("Executor / trusted person", None),
        ("Where this file is saved", None),
    ]
    for i, (k, v) in enumerate(rows):
        r = 5 + i
        ws.cell(row=r, column=2, value=k).font = Font(name=FONT, size=10, color=PAL.muted)
        c = ws.cell(row=r, column=3, value=v)
        c.fill = fill(PAL.soft)
        c.border = thin(PAL.line)
        c.font = Font(name=FONT, size=11, color=PAL.ink)
    ws["C6"].number_format = "mm/dd/yyyy"
    steps = [
        "HOW TO USE",
        "1. Fill in the tabs in any order. Shaded rows are for typing; dropdowns appear where useful.",
        "2. The Dashboard tab tracks your progress and estimates net worth automatically.",
        "3. Record WHERE things are and the last 4 digits only. Never type full account numbers, SSNs or passwords.",
        "4. Review it once a year (birthday or tax day works) and update the 'Last updated' date above.",
        "5. Tell your executor or a trusted person that this file exists and where to find it.",
        "",
        "PRIVACY",
        "Keep this file in a secure place: an encrypted drive, a password-protected cloud folder, or printed in a safe.",
        "",
        "DISCLAIMER",
        "This organizer is a personal record-keeping tool, not legal, tax or financial advice, and it does not replace "
        "a will or other legal documents. Talk to a licensed professional about estate planning in your state.",
    ]
    for i, s in enumerate(steps):
        r = 11 + i
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        c = ws.cell(row=r, column=2, value=s)
        bold = s.isupper() and s != ""
        c.font = Font(name=FONT, size=11 if bold else 10, bold=bold, color=PAL.primary if bold else PAL.ink)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 30 if len(s) > 95 else 18
    set_print(ws, landscape=False)


def _list_sheet(wb, name, subtitle, cols, dropdowns):
    ws = wb.create_sheet(name)
    widths = {col(i + 1): w for i, (_, w, _) in enumerate(cols)}
    base_sheet(ws, PAL, widths)
    title(ws, PAL, name, subtitle, span=len(cols))
    header_row(ws, PAL, FIRST - 1, [h for h, _, _ in cols])
    fmts = {i + 1: f for i, (_, _, f) in enumerate(cols) if f}
    input_block(ws, PAL, FIRST, ROWS, 1, len(cols), number_formats=fmts)
    for i, (h, _, _) in enumerate(cols):
        if h in dropdowns:
            letter = col(i + 1)
            list_validation(ws, f"{letter}{FIRST}:{letter}{FIRST + ROWS - 1}", f'"{dropdowns[h]}"')
    for i, item in enumerate(PREFILL.get(name, [])):
        ws.cell(row=FIRST + i, column=1, value=item).font = Font(name=FONT, size=10, bold=True, color=PAL.primary)
    ws.freeze_panes = ws.cell(row=FIRST, column=2)
    set_print(ws)
    return ws


def _dashboard(wb):
    ws = wb.create_sheet("Dashboard", 1)
    base_sheet(ws, PAL, {"A": 3, "B": 28, "C": 14, "D": 14, "E": 30, "F": 3, "G": 16, "H": 16}, tab=PAL.accent)
    ws.merge_cells("B1:H1")
    ws["B1"] = "Dashboard"
    ws["B1"].font = Font(name=FONT, size=20, bold=True, color=PAL.primary)
    ws.row_dimensions[1].height = 36

    def rng(sheet, header):
        cols = next(c for n, _, c, _, _ in SECTIONS if n == sheet)
        idx = [h for h, _, _ in cols].index(header) + 1
        return f"'{sheet}'!{col(idx)}{FIRST}:{col(idx)}{FIRST + ROWS - 1}"

    assets = (f"SUM({rng('Bank Accounts', 'Approx. balance')})+SUM({rng('Retirement & Investments', 'Approx. value')})"
              f"+SUM({rng('Property & Assets', 'Est. value')})")
    debts = f"SUM({rng('Debts & Loans', 'Balance owed')})"
    kpi(ws, PAL, 3, 2, "Est. assets", f"={assets}", "$#,##0", 1)
    kpi(ws, PAL, 3, 3, "Est. debts", f"={debts}", "$#,##0", 2)
    kpi(ws, PAL, 3, 5, "Est. net worth", f"=B4-C4", "$#,##0", 1)
    kpi(ws, PAL, 3, 7, "Sections started", f'=COUNTIF(D9:D{8 + len(SECTIONS)},">0")&" / {len(SECTIONS)}"', "@", 2)

    header_row(ws, PAL, 8, ["Section", "Rows filled", "Progress", "Status"], start_col=2)
    target = 5  # rows that count as "complete enough" for the progress bar
    for i, (name, *_rest) in enumerate(SECTIONS):
        r = 9 + i
        ws.cell(row=r, column=2, value=name).font = Font(name=FONT, size=10, bold=True, color=PAL.ink)
        # count rows where any user column (not the prefilled label) has content
        if name in PREFILL:
            formula = f"=COUNTA('{name}'!B{FIRST}:B{FIRST + ROWS - 1})"
        else:
            formula = f"=COUNTA('{name}'!A{FIRST}:A{FIRST + ROWS - 1})"
        ws.cell(row=r, column=3, value=formula)
        ws.cell(row=r, column=4, value=f"=MIN(1,C{r}/{target})").number_format = "0%"
        ws.cell(row=r, column=5, value=f'=IF(C{r}=0,"Not started",IF(C{r}<{target},"In progress","Looking good"))')
        for c in range(2, 6):
            cell = ws.cell(row=r, column=c)
            cell.border = thin(PAL.line)
            cell.font = Font(name=FONT, size=10, bold=(c == 2), color=PAL.ink)
            cell.alignment = Alignment(horizontal="left" if c in (2, 5) else "center", vertical="center")
            if i % 2:
                cell.fill = fill(PAL.soft)
        ws.cell(row=r, column=2).value = f'=HYPERLINK("#\'{name}\'!A1","{name}")'
        ws.row_dimensions[r].height = 20
    end = 8 + len(SECTIONS)
    ws.conditional_formatting.add(f"D9:D{end}", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                             end_value=1, color=PAL.accent))
    note(ws, PAL, end + 2, "Values are rough estimates from what you typed. Click a section name to jump to it.",
         span=7, col=2)
    set_print(ws, landscape=False)


def build(path):
    wb = Workbook()
    _start_here(wb)
    for name, sub, cols, dd, _money in SECTIONS:
        _list_sheet(wb, name, sub, cols, dd)
    _dashboard(wb)
    wb.active = 0
    wb.save(path)
    return path
