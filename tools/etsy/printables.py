"""Group 2: printable PDF planners. Each product renders US Letter + A4.

    python3 -m tools.etsy.printables [slug ...]
"""
from __future__ import annotations

import calendar
import json
import sys
from functools import partial
from pathlib import Path

from .pdf_kit import ROOT, Theme, cover, render

OUT = ROOT / "etsy" / "products"
YEAR = 2027


def shop_brand() -> str:
    cfg = ROOT / "config" / "etsy.json"
    name = json.loads(cfg.read_text()).get("shop_name", "") if cfg.exists() else ""
    return f"{name} · personal use only" if name else "Personal use only · please do not resell"


# ---------------------------------------------------------------- budget binder
def bb_year(k):
    x, y, w, h = k.header("Year at a glance", f"{YEAR} budget overview", ("Year",))
    months = [calendar.month_abbr[m].upper() for m in range(1, 13)]
    k.table(x, y + h, w, y, ["Month", "Income", "Expenses", "Savings", "Debt paid", "Notes"],
            [.12, .16, .16, .16, .16, .24], row_h=(h - 20) / 13, first_col=months + ["TOTAL"])


def bb_monthly(k):
    x, y, w, h = k.header("Monthly budget", "", ("Month", "Year"))
    top = y + h
    half = (w - 14) / 2
    t = k.section(x, top, half, "Income")
    k.table(x, t - 4, half, t - 4 - 20 - 18 * 5, ["Source", "Expected", "Actual"], [.5, .25, .25])
    t2 = k.section(x + half + 14, top, half, "Summary")
    k.table(x + half + 14, t2 - 4, half, t2 - 4 - 20 - 18 * 5, ["", "Budget", "Actual"], [.5, .25, .25],
            first_col=["Total income", "Total expenses", "Savings", "Debt payments", "Left over"])
    t3 = k.section(x, t - 4 - 20 - 18 * 5 - 14, w, "Expenses")
    cats = ["Rent / Mortgage", "Utilities", "Phone & Internet", "Groceries", "Dining out", "Transport / Gas",
            "Car payment", "Insurance", "Health", "Personal care", "Kids", "Pets", "Subscriptions",
            "Entertainment", "Clothing", "Gifts", "Savings", "Debt payments"]
    k.table(x, t3 - 4, w, y, ["Category", "Budget", "Actual", "Difference", "Notes"],
            [.3, .15, .15, .15, .25], first_col=cats)


def bb_bills(k):
    x, y, w, h = k.header("Bill tracker", "Tick each month when paid", ("Year",))
    k.table(x, y + h, w, y, ["Bill", "Due", "Amount"] + [calendar.month_abbr[m][0] for m in range(1, 13)],
            [.2, .07, .09] + [.64 / 12] * 12, row_h=22)


def bb_expenses(k):
    x, y, w, h = k.header("Expense log", "", ("Month",))
    k.table(x, y + h, w, y, ["Date", "Description", "Category", "Paid with", "Amount"],
            [.12, .36, .2, .16, .16])


def _hundred(k, x, y_top, w, h, label):
    k.box(x, y_top - h, w, h, label, lined=False)
    k.text(x + 10, y_top - 34, "GOAL  $ ____________      FOR  ______________________", 8.5)
    cols, rows = 10, 10
    gw, gh = w - 30, h - 60
    r = min(gw / cols, gh / rows) * 0.36
    for i in range(rows):
        for j in range(cols):
            cx = x + 15 + gw / cols * (j + .5)
            cy = y_top - 50 - gh / rows * (i + .5)
            k.circle(cx, cy, r, stroke=k.t.accent, lw=0.7)
            k.text(cx, cy - 2.2, str(i * cols + j + 1), 5.5, "Helvetica", "#9A9A9A", "center")


def bb_savings(k):
    x, y, w, h = k.header("Savings tracker", "Colour one circle for every 1% saved")
    _hundred(k, x, y + h, w, h * .62, "Savings goal")
    k.table(x, y + h * .36, w, y, ["Date", "Deposit", "Balance", "Notes"], [.2, .2, .2, .4])


def bb_debt(k):
    x, y, w, h = k.header("Debt payoff", "Colour one circle for every 1% paid off")
    _hundred(k, x, y + h, w, h * .5, "Debt")
    k.table(x, y + h * .48, w, y, ["Debt", "Balance", "Rate %", "Min. payment", "Due", "Paid off"],
            [.28, .15, .12, .17, .12, .16], row_h=20)


def bb_sinking(k):
    x, y, w, h = k.header("Sinking funds", "Save a little each month for big expenses")
    cw, ch = (w - 14) / 2, (h - 28) / 3
    for i in range(6):
        cx = x + (i % 2) * (cw + 14)
        cy = y + h - (i // 2 + 1) * ch - (i // 2) * 14
        k.rect(cx, cy, cw, ch, stroke=k.t.line, r=6)
        k.text(cx + 8, cy + ch - 15, "FUND  ____________________", 8, "Helvetica-Bold", k.t.accent)
        k.text(cx + 8, cy + ch - 29, "GOAL $ ________   BY ________", 8)
        k.table(cx + 6, cy + ch - 36, cw - 12, cy + 6, ["Date", "Amount", "Total"], row_h=15, header_h=15,
                font_size=7)


def bb_subs(k):
    x, y, w, h = k.header("Subscriptions", "Everything that renews automatically")
    k.table(x, y + h, w, y, ["Service", "Amount", "Billing", "Renews", "Paid from", "Keep?"],
            [.28, .13, .14, .15, .18, .12], row_h=22)


def bb_goals(k):
    x, y, w, h = k.header("Financial goals", f"What do you want your money to do in {YEAR}?")
    third = (h - 28) / 3
    for i, lab in enumerate(["Short term (this month)", "Medium term (this year)", "Long term (5+ years)"]):
        k.box(x, y + h - (i + 1) * third - i * 14, w, third, lab)


def bb_cover(k):
    cover(k, "Budget Binder", "Printable money planner · US Letter & A4", str(YEAR))


BUDGET_PAGES = [bb_cover, bb_year, bb_monthly, bb_bills, bb_expenses, bb_savings, bb_debt, bb_sinking, bb_subs,
                bb_goals]


# ---------------------------------------------------------------- 2027 calendar planner
def cp_cover(k):
    cover(k, "Planner", "Monthly calendar & weekly pages · Sunday start", str(YEAR))


def cp_year(k):
    x, y, w, h = k.header(f"{YEAR} at a glance")
    cols, rows = 3, 4
    cw, rh = w / cols, h / rows
    for m in range(12):
        k.mini_month(x + (m % cols) * cw + 8, y + h - (m // cols) * rh, cw - 16, YEAR, m + 1)


def cp_goals(k):
    x, y, w, h = k.header(f"{YEAR} goals", "Big picture first, then break it down")
    half = (w - 14) / 2
    labels = ["Health", "Money", "Career / School", "Relationships", "Home", "Fun & Growth"]
    bh = (h - 28) / 3
    for i, lab in enumerate(labels):
        k.box(x + (i % 2) * (half + 14), y + h - (i // 2 + 1) * bh - (i // 2) * 14, half, bh, lab)


def cp_month(k, m):
    x, y, w, h = k.header(calendar.month_name[m], str(YEAR))
    side = w * .24
    k.month_grid(x, y + h * .0, w - side - 12, h, YEAR, m)
    sx = x + w - side
    t = k.section(sx, y + h, side, "Goals")
    k.checklist(sx, t - 2, side, t - h * .38)
    t2 = k.section(sx, t - h * .38 - 10, side, "Notes")
    k.lines(sx, t2 - 2, side, y)


def cp_week(k):
    x, y, w, h = k.header("Weekly plan", "", ("Week of",))
    cw = (w - 14) / 2
    bh = (h - 3 * 10) / 4
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, d in enumerate(days):
        cx = x + (i % 2) * (cw + 14)
        cy = y + h - (i // 2 + 1) * bh - (i // 2) * 10
        k.box(cx, cy, cw, bh, d, gap=16)
    cx, cy = x + cw + 14, y
    k.rect(cx, cy, cw, bh, stroke=k.t.line, r=6)
    k.text(cx + 8, cy + bh - 13, "TOP PRIORITIES", 7.5, "Helvetica-Bold", k.t.accent)
    k.checklist(cx + 8, cy + bh - 16, cw - 16, cy + 6, gap=16)


def cp_day(k):
    x, y, w, h = k.header("Daily plan", "", ("Date",))
    left = w * .55
    t = k.section(x, y + h, left, "Schedule")
    hours = [f"{(hh - 1) % 12 + 1} {'AM' if hh < 12 else 'PM'}" for hh in range(6, 22)]
    gap = (t - 4 - y) / len(hours)
    for i, hr in enumerate(hours):
        yy = t - 4 - (i + 1) * gap
        k.text(x, yy + 4, hr, 7.5, "Helvetica-Bold", "#8A8A8A")
        k.hline(x + 34, x + left, yy)
    rx, rw = x + left + 14, w - left - 14
    t2 = k.section(rx, y + h, rw, "To do")
    k.checklist(rx, t2 - 2, rw, y + h * .45)
    t3 = k.section(rx, y + h * .45 - 10, rw, "Notes")
    k.lines(rx, t3 - 2, rw, y)


PLANNER_PAGES = [cp_cover, cp_year, cp_goals] + [partial(cp_month, m=m) for m in range(1, 13)] + [cp_week, cp_day]


# ---------------------------------------------------------------- meal planner
def mp_cover(k):
    cover(k, "Meal Planner", "Weekly menus · grocery list · recipes · pantry")


def mp_week(k):
    x, y, w, h = k.header("Weekly meal plan", "", ("Week of",))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    k.table(x, y + h, w, y + h * .25, ["Day", "Breakfast", "Lunch", "Dinner", "Snacks"],
            [.1, .225, .225, .225, .225], row_h=(h * .75 - 20) / 7, first_col=days)
    k.box(x, y, w, h * .25 - 12, "Prep ahead / notes")


GROCERY = ["Produce", "Meat & Fish", "Dairy & Eggs", "Bakery", "Pantry", "Frozen", "Drinks", "Household"]


def mp_grocery(k):
    x, y, w, h = k.header("Grocery list", "", ("Store", "Date"))
    cw = (w - 28) / 3
    bh = (h - 2 * 12) / 3
    for i, sec in enumerate(GROCERY + ["Other"]):
        cx = x + (i % 3) * (cw + 14)
        cy = y + h - (i // 3 + 1) * bh - (i // 3) * 12
        k.rect(cx, cy, cw, bh, stroke=k.t.line, r=6)
        k.text(cx + 8, cy + bh - 13, sec.upper(), 7.5, "Helvetica-Bold", k.t.accent)
        k.checklist(cx + 8, cy + bh - 16, cw - 16, cy + 6, gap=16)


def mp_recipe(k):
    x, y, w, h = k.header("Recipe", "", ("Serves", "Time"))
    k.text(x, y + h - 10, "RECIPE NAME", 7.5, "Helvetica-Bold", "#8A8A8A")
    k.hline(x + 70, x + w, y + h - 12, k.t.accent)
    left = w * .38
    t = k.section(x, y + h - 26, left, "Ingredients")
    k.checklist(x, t - 2, left, y + 70)
    t2 = k.section(x + left + 14, y + h - 26, w - left - 14, "Directions")
    yy = t2 - 18
    n = 1
    while yy > y + 70:
        k.text(x + left + 14, yy + 3, f"{n}.", 8, "Helvetica-Bold", k.t.accent)
        k.hline(x + left + 28, x + w, yy)
        yy -= 18
        n += 1
    k.box(x, y, w, 60, "Notes")


def mp_pantry(k):
    x, y, w, h = k.header("Pantry inventory", "What you have, so you buy only what you need")
    k.table(x, y + h, w, y, ["Item", "Qty", "Best by", "Restock?", "Item", "Qty", "Best by", "Restock?"],
            [.22, .07, .11, .1, .22, .07, .11, .1], row_h=20)


def mp_ideas(k):
    x, y, w, h = k.header("Meal ideas", "Family favourites to rotate")
    cw = (w - 14) / 2
    bh = (h - 14) / 2
    for i, lab in enumerate(["Breakfast", "Lunch", "Dinner", "Snacks & treats"]):
        k.box(x + (i % 2) * (cw + 14), y + h - (i // 2 + 1) * bh - (i // 2) * 14, cw, bh, lab)


MEAL_PAGES = [mp_cover, mp_week, mp_grocery, mp_recipe, mp_pantry, mp_ideas]


# ---------------------------------------------------------------- cleaning schedule
DAILY = ["Make beds", "Wash dishes / run dishwasher", "Wipe kitchen counters", "Quick bathroom wipe",
         "10-minute tidy", "Sort mail", "Laundry load", "Sweep high-traffic floors"]
WEEKLY = {"Monday": ["Clean bathrooms", "Replace towels"], "Tuesday": ["Dust surfaces", "Wipe electronics"],
          "Wednesday": ["Vacuum all rooms", "Shake out rugs"], "Thursday": ["Mop floors", "Clean mirrors"],
          "Friday": ["Fridge clean-out", "Take out recycling"], "Saturday": ["Change bed sheets", "Laundry catch-up"],
          "Sunday": ["Plan the week", "Reset entryway"]}
MONTHLY = ["Clean oven", "Descale kettle / coffee maker", "Wash shower curtain", "Dust ceiling fans", "Clean baseboards",
           "Wipe light switches & handles", "Clean microwave", "Vacuum sofa & under cushions", "Wash bins",
           "Clean inside windows", "Declutter one drawer", "Clean dishwasher filter"]
DEEP = {"Kitchen": ["Pull out & clean behind appliances", "Clean cabinet fronts", "Degrease range hood",
                    "Organize pantry"],
        "Bathroom": ["Scrub grout", "Wash bath mats", "Clean exhaust fan", "Toss old products"],
        "Bedrooms": ["Flip / rotate mattress", "Wash pillows & duvet", "Declutter closet", "Clean under bed"],
        "Living areas": ["Wash curtains", "Clean windows outside", "Shampoo rugs", "Dust books & shelves"],
        "Outdoor / Garage": ["Sweep porch", "Clean patio furniture", "Organize garage", "Clean gutters"],
        "Seasonal": ["Test smoke alarms", "Replace HVAC filter", "Swap seasonal clothes", "Check first-aid kit"]}


def cs_cover(k):
    cover(k, "Cleaning Schedule", "Daily · weekly · monthly · deep clean checklists")


def cs_daily(k):
    x, y, w, h = k.header("Daily cleaning", "Tick each day", ("Week of",))
    k.table(x, y + h, w, y + h * .35, ["Task", "M", "T", "W", "T", "F", "S", "S"],
            [.44] + [.08] * 7, row_h=(h * .65 - 20) / 12, first_col=DAILY)
    k.box(x, y, w, h * .35 - 12, "Notes & extra tasks")


def cs_weekly(k):
    x, y, w, h = k.header("Weekly rhythm", "One focus per day keeps the whole house done", ("Week of",))
    cw = (w - 14) / 2
    bh = (h - 3 * 10) / 4
    for i, (d, tasks) in enumerate(WEEKLY.items()):
        cx = x + (i % 2) * (cw + 14)
        cy = y + h - (i // 2 + 1) * bh - (i // 2) * 10
        k.rect(cx, cy, cw, bh, stroke=k.t.line, r=6)
        k.text(cx + 8, cy + bh - 13, d.upper(), 7.5, "Helvetica-Bold", k.t.accent)
        k.checklist(cx + 8, cy + bh - 16, cw - 16, cy + 6, tasks, gap=16, size=8.5)
    cx, cy = x + cw + 14, y
    k.box(cx, cy, cw, bh, "Errands & extras", gap=16)


def cs_monthly(k):
    x, y, w, h = k.header("Monthly tasks", "Tick the month when done", ("Year",))
    k.table(x, y + h, w, y, ["Task"] + [calendar.month_abbr[m][0] for m in range(1, 13)],
            [.34] + [.66 / 12] * 12, row_h=22, first_col=MONTHLY)


def cs_deep(k):
    x, y, w, h = k.header("Deep clean by room", "Spring, fall, or before guests")
    cw = (w - 14) / 2
    bh = (h - 2 * 12) / 3
    for i, (room, tasks) in enumerate(DEEP.items()):
        cx = x + (i % 2) * (cw + 14)
        cy = y + h - (i // 2 + 1) * bh - (i // 2) * 12
        k.rect(cx, cy, cw, bh, stroke=k.t.line, r=6)
        k.text(cx + 8, cy + bh - 13, room.upper(), 7.5, "Helvetica-Bold", k.t.accent)
        k.checklist(cx + 8, cy + bh - 16, cw - 16, cy + 6, tasks, gap=17, size=8.5)


def cs_supplies(k):
    x, y, w, h = k.header("Supplies & restock", "")
    k.table(x, y + h, w, y, ["Product", "Used for", "Where to buy", "Price", "Restock?"],
            [.28, .26, .2, .12, .14], row_h=22)


CLEAN_PAGES = [cs_cover, cs_daily, cs_weekly, cs_monthly, cs_deep, cs_supplies]


# ---------------------------------------------------------------- habit & mood tracker (undated)
def hm_cover(k):
    cover(k, "Habit & Mood Tracker", "Undated printable · use any month, any year")


def hm_habits(k):
    x, y, w, h = k.header("Habit tracker", "", ("Month",))
    name_w = .22
    k.table(x, y + h, w, y + 70, ["Habit"] + [str(d) for d in range(1, 32)], [name_w] + [(1 - name_w) / 31] * 31,
            row_h=22, font_size=7)
    k.box(x, y, w, 58, "Reward when I hit my goals", gap=16)


MOODS = [("Great", "#F2C14E"), ("Good", "#9BC59D"), ("Okay", "#A7C7E7"), ("Low", "#C3B1E1"), ("Stressed", "#F4A6A6")]


def hm_year_pixels(k):
    x, y, w, h = k.header("Year in pixels", "Colour each day with your mood", ("Year",))
    leg_h = 30
    gx, gy, gw, gh = x + 22, y + leg_h + 10, w - 22, h - leg_h - 26
    cw, rh = gw / 12, gh / 31
    for m in range(12):
        k.text(gx + cw * m + cw / 2, y + h - 12, calendar.month_abbr[m + 1][0], 8, "Helvetica-Bold",
               k.t.accent, "center")
    for d in range(31):
        k.text(x + 14, gy + gh - (d + 1) * rh + rh / 2 - 3, str(d + 1), 6.5, "Helvetica", "#8A8A8A", "right")
        for m in range(12):
            k.rect(gx + m * cw + 1, gy + gh - (d + 1) * rh + 1, cw - 2, rh - 2, stroke=k.t.line, r=2, lw=0.6)
    lx = x
    for name, col in MOODS:
        k.rect(lx, y + 8, 14, 14, fill=col, r=3)
        k.text(lx + 19, y + 11, name, 8.5)
        lx += 90


def hm_mood_month(k):
    x, y, w, h = k.header("Mood & energy", "", ("Month",))
    k.table(x, y + h, w, y, ["Day", "Mood", "Energy 1-5", "Sleep hrs", "Water", "Grateful for"],
            [.07, .14, .12, .11, .16, .4], row_h=(h - 20) / 31, first_col=[str(d) for d in range(1, 32)],
            font_size=7)


def hm_reflect(k):
    x, y, w, h = k.header("Monthly reflection", "", ("Month",))
    labels = ["Wins this month", "What was hard", "What I learned", "Focus for next month"]
    bh = (h - 3 * 12) / 4
    for i, lab in enumerate(labels):
        k.box(x, y + h - (i + 1) * bh - i * 12, w, bh, lab)


HABIT_PAGES = [hm_cover, hm_habits, hm_year_pixels, hm_mood_month, hm_reflect]


# ---------------------------------------------------------------- registry
PRINTABLES = {
    "printable-budget-binder-2027": dict(title="Budget Binder", file="Budget_Binder_2027", pages=BUDGET_PAGES,
                                         theme=Theme(accent="#7E9C8A", soft="#EEF3EF")),
    "printable-planner-2027": dict(title="2027 Planner", file="Printable_Planner_2027", pages=PLANNER_PAGES,
                                   theme=Theme(accent="#C08B6E", soft="#F7EFEA")),
    "printable-meal-planner": dict(title="Meal Planner", file="Meal_Planner", pages=MEAL_PAGES,
                                   theme=Theme(accent="#D4935B", soft="#FBF1E7")),
    "printable-cleaning-schedule": dict(title="Cleaning Schedule", file="Cleaning_Schedule", pages=CLEAN_PAGES,
                                        theme=Theme(accent="#6C9BB8", soft="#EAF2F7")),
    "printable-habit-mood-tracker": dict(title="Habit & Mood Tracker", file="Habit_Mood_Tracker", pages=HABIT_PAGES,
                                         theme=Theme(accent="#9C84B5", soft="#F2EEF7")),
}


def build(only=()):
    brand = shop_brand()
    out = []
    for slug, p in PRINTABLES.items():
        if only and slug not in only:
            continue
        d = OUT / slug
        d.mkdir(parents=True, exist_ok=True)
        for size in ("Letter", "A4"):
            f = render(d / f"{p['file']}_{size}.pdf", size, p["pages"], p["theme"], brand, p["title"])
            out.append(f)
            print("built", f.relative_to(ROOT), f"({len(p['pages'])} pages)")
    return out


if __name__ == "__main__":
    build(sys.argv[1:])
