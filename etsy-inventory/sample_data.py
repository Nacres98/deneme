"""Cohesive sample data for the fictional brand "Ember & Sage Candle Co.".

Everything is simulated chronologically so stock never goes negative:
sales are generated first, production is planned to cover demand, and
material purchases are planned to cover production.
"""
import math
import random
from datetime import date, timedelta

random.seed(42)

FY = 2026
ASOF = date(2026, 11, 20)

# ---------------------------------------------------------------- products
# sku, name, collection, price, opening, labor_min, lead_days, weight, season_months
PRODUCTS = [
    ("CAN-001", "Sage & Sea Salt Candle - 8 oz", "Signature Candles", 32, 24, 12, 5, 10, None),
    ("CAN-002", "Fig & Cedar Candle - 8 oz", "Signature Candles", 32, 18, 12, 5, 8, None),
    ("CAN-003", "Lavender Fields Candle - 8 oz", "Signature Candles", 30, 20, 12, 5, 7, None),
    ("CAN-004", "Amber Noir Candle - 12 oz", "Signature Candles", 44, 12, 15, 5, 6, None),
    ("CAN-005", "Pumpkin Chai Candle - 12 oz", "Seasonal", 42, 0, 15, 5, 11, (9, 10, 11)),
    ("CAN-006", "Winter Pine Candle - 12 oz", "Seasonal", 42, 0, 15, 5, 10, (10, 11)),
    ("CAN-007", "Travel Tin Trio Gift Set", "Gift Sets", 38, 10, 20, 4, 5, None),
    ("MEL-001", "Wax Melt Bar - Sage & Sea Salt", "Wax Melts", 12, 30, 4, 3, 6, None),
    ("MEL-002", "Wax Melt Bar - Amber Noir", "Wax Melts", 12, 25, 4, 3, 4, None),
    ("DIF-001", "Reed Diffuser - Fig & Cedar", "Diffusers", 39, 10, 10, 4, 4, None),
    ("DIF-002", "Reed Diffuser - Lavender Fields", "Diffusers", 39, 8, 10, 4, 3, None),
    ("ROM-001", "Room Spray - Lavender Fields", "Room & Linen", 22, 15, 6, 3, 3, None),
    ("ROM-002", "Linen Mist - Sage & Sea Salt", "Room & Linen", 20, 12, 6, 3, 2, None),
    ("GFT-001", "Self-Care Gift Box", "Gift Sets", 68, 6, 25, 6, 3, None),
    ("SMP-001", "Scent Sampler - 6 Mini Tins", "Gift Sets", 38, 12, 15, 4, 4, None),
]
PRICE = {p[0]: p[3] for p in PRODUCTS}

# ---------------------------------------------------------------- materials
# id, name, category, unit, supplier, opening, cost, lead, moq
MATERIALS = [
    ("MAT-001", "Coconut Soy Wax", "Wax", "g", "Lumen Wax Supply", 9000, 0.011, 10, 4500),
    ("MAT-002", "Fragrance Oil - Sage & Sea Salt", "Fragrance Oil", "ml", "Aroma Lab Co.", 900, 0.085, 7, 480),
    ("MAT-003", "Fragrance Oil - Fig & Cedar", "Fragrance Oil", "ml", "Aroma Lab Co.", 700, 0.085, 7, 480),
    ("MAT-004", "Fragrance Oil - Lavender Fields", "Fragrance Oil", "ml", "Aroma Lab Co.", 700, 0.080, 7, 480),
    ("MAT-005", "Fragrance Oil - Amber Noir", "Fragrance Oil", "ml", "Aroma Lab Co.", 600, 0.095, 7, 480),
    ("MAT-006", "Fragrance Oil - Pumpkin Chai", "Fragrance Oil", "ml", "Aroma Lab Co.", 0, 0.090, 7, 480),
    ("MAT-007", "Fragrance Oil - Winter Pine", "Fragrance Oil", "ml", "Aroma Lab Co.", 0, 0.090, 7, 480),
    ("MAT-008", "Cotton Wick (pre-tabbed)", "Wick", "pcs", "Lumen Wax Supply", 300, 0.12, 7, 100),
    ("MAT-009", "Amber Jar - 8 oz", "Vessel", "pcs", "Vessel & Vial", 60, 1.35, 14, 48),
    ("MAT-010", "Amber Jar - 12 oz", "Vessel", "pcs", "Vessel & Vial", 30, 1.75, 14, 36),
    ("MAT-011", "Travel Tin - 2 oz", "Vessel", "pcs", "Vessel & Vial", 80, 0.85, 10, 48),
    ("MAT-012", "Wax Melt Clamshell", "Packaging", "pcs", "PackRight Supplies", 120, 0.32, 10, 100),
    ("MAT-013", "Diffuser Bottle - 100 ml", "Vessel", "pcs", "Vessel & Vial", 30, 2.10, 14, 24),
    ("MAT-014", "Rattan Reeds", "Diffuser Parts", "pcs", "Vessel & Vial", 400, 0.08, 10, 200),
    ("MAT-015", "Fragrance Base / Solubilizer", "Diffuser Parts", "ml", "Aroma Lab Co.", 3000, 0.03, 10, 1000),
    ("MAT-016", "Spray Bottle - 100 ml", "Vessel", "pcs", "Vessel & Vial", 36, 1.10, 10, 24),
    ("MAT-017", "Product Labels", "Labels", "pcs", "PrintNest Labels", 400, 0.18, 7, 250),
    ("MAT-018", "Kraft Gift Box", "Packaging", "pcs", "PackRight Supplies", 30, 2.40, 10, 25),
    ("MAT-019", "Shipping Mailer Box", "Packaging", "pcs", "PackRight Supplies", 120, 0.95, 7, 50),
    ("MAT-020", "Tissue Paper", "Packaging", "sheets", "PackRight Supplies", 300, 0.06, 7, 200),
]
MAT = {m[0]: m for m in MATERIALS}
WASTE = {"MAT-001": 0.02, "MAT-002": 0.02, "MAT-003": 0.02, "MAT-004": 0.02,
         "MAT-005": 0.02, "MAT-006": 0.02, "MAT-007": 0.02}


def _candle8(fo):
    return [("MAT-001", 200), (fo, 20), ("MAT-008", 1), ("MAT-009", 1),
            ("MAT-017", 1), ("MAT-019", 1), ("MAT-020", 1)]


def _candle12(fo):
    return [("MAT-001", 300), (fo, 30), ("MAT-008", 2), ("MAT-010", 1),
            ("MAT-017", 1), ("MAT-019", 1), ("MAT-020", 1)]


def _melt(fo):
    return [("MAT-001", 70), (fo, 8), ("MAT-012", 1), ("MAT-017", 1), ("MAT-019", 1)]


def _diffuser(fo):
    return [("MAT-013", 1), ("MAT-015", 85), (fo, 15), ("MAT-014", 8),
            ("MAT-017", 1), ("MAT-019", 1), ("MAT-020", 1)]


def _spray(fo):
    return [("MAT-016", 1), ("MAT-015", 90), (fo, 10), ("MAT-017", 1), ("MAT-019", 1)]


RECIPES = {
    "CAN-001": _candle8("MAT-002"),
    "CAN-002": _candle8("MAT-003"),
    "CAN-003": _candle8("MAT-004"),
    "CAN-004": _candle12("MAT-005"),
    "CAN-005": _candle12("MAT-006"),
    "CAN-006": _candle12("MAT-007"),
    "CAN-007": [("MAT-001", 180), ("MAT-002", 6), ("MAT-003", 6), ("MAT-004", 6),
                ("MAT-008", 3), ("MAT-011", 3), ("MAT-017", 3), ("MAT-018", 1),
                ("MAT-020", 2), ("MAT-019", 1)],
    "MEL-001": _melt("MAT-002"),
    "MEL-002": _melt("MAT-005"),
    "DIF-001": _diffuser("MAT-003"),
    "DIF-002": _diffuser("MAT-004"),
    "ROM-001": _spray("MAT-004"),
    "ROM-002": _spray("MAT-002"),
    "GFT-001": [("MAT-001", 260), ("MAT-004", 26), ("MAT-008", 2), ("MAT-009", 1),
                ("MAT-011", 1), ("MAT-016", 1), ("MAT-015", 90), ("MAT-002", 10),
                ("MAT-017", 3), ("MAT-018", 1), ("MAT-020", 2), ("MAT-019", 1)],
    "SMP-001": [("MAT-001", 240)] + [(f"MAT-00{i}", 4) for i in range(2, 8)] +
               [("MAT-008", 6), ("MAT-011", 6), ("MAT-017", 6), ("MAT-018", 1),
                ("MAT-020", 1), ("MAT-019", 1)],
}

CHANNELS = ["Etsy", "Shopify", "Amazon Handmade", "Wholesale", "Markets & Fairs", "Website / Direct"]

# ---------------------------------------------------------------- sales
ORDERS_PER_MONTH = {1: 40, 2: 54, 3: 42, 4: 41, 5: 55, 6: 37, 7: 34, 8: 42, 9: 58, 10: 79, 11: 64}
PREFIX = {"Etsy": "ETSY", "Shopify": "SHOP", "Amazon Handmade": "AMZ", "Wholesale": "WHL",
          "Markets & Fairs": "MKT", "Website / Direct": "WEB"}


def _month_days(m):
    start = date(FY, m, 1)
    end = date(FY, m + 1, 1) - timedelta(days=1) if m < 12 else date(FY, 12, 31)
    if m == ASOF.month:
        end = ASOF - timedelta(days=1)
    return start, end


def _pick_sku(m, wholesale=False):
    pool, weights = [], []
    for sku, _n, coll, _p, _o, _l, _ld, w, season in PRODUCTS:
        if season and m not in season:
            continue
        if wholesale and coll not in ("Signature Candles", "Wax Melts", "Seasonal"):
            continue
        if coll == "Gift Sets" and m in (2, 5, 11):
            w *= 2.2
        pool.append(sku)
        weights.append(w)
    return random.choices(pool, weights)[0]


def build_sales():
    rows = []
    seq = {c: 1000 for c in CHANNELS}
    for m, n in ORDERS_PER_MONTH.items():
        start, end = _month_days(m)
        span = (end - start).days
        orders = []
        for _ in range(n):
            ch = random.choices(CHANNELS, [64, 14, 5, 0, 10, 7])[0]
            orders.append((start + timedelta(days=random.randint(0, span)), ch))
        # 1-2 wholesale orders per month
        for _ in range(1 if m % 2 else 2):
            orders.append((start + timedelta(days=random.randint(0, span)), "Wholesale"))
        orders.sort()
        for d, ch in orders:
            seq[ch] += 1
            oid = f"{PREFIX[ch]}-{seq[ch]}"
            nlines = 1 if (ch == "Wholesale" or random.random() > 0.22) else 2
            status = random.choices(["Completed", "Refunded", "Cancelled"], [95, 3.5, 1.5])[0]
            ad = "Yes" if ch == "Etsy" and random.random() < 0.09 else "No"
            used = set()
            for li in range(nlines):
                sku = _pick_sku(m, ch == "Wholesale")
                while sku in used:
                    sku = _pick_sku(m, ch == "Wholesale")
                used.add(sku)
                if ch == "Wholesale":
                    qty = random.choice([6, 6, 12])
                    price = round(PRICE[sku] * 0.5, 2)
                else:
                    qty = 2 if random.random() < 0.15 else 1
                    price = PRICE[sku]
                disc = 0.0
                if ch in ("Etsy", "Shopify") and random.random() < 0.16:
                    disc = round(qty * price * 0.15, 2)
                first = li == 0
                if ch == "Markets & Fairs":
                    ship_chg, label = 0.0, 0.0
                elif ch == "Wholesale":
                    label = round(random.uniform(14, 22), 2) if first else 0.0
                    ship_chg = label
                else:
                    big = sku.startswith(("CAN-004", "CAN-005", "CAN-006", "GFT", "DIF"))
                    label = round(random.uniform(6.8, 9.4) if big else random.uniform(4.6, 7.2), 2) if first else 0.0
                    if ch == "Etsy" and random.random() < 0.30:
                        ship_chg = 0.0  # free shipping promo
                    elif ch == "Amazon Handmade":
                        ship_chg = 4.99 if first else 0.0
                    else:
                        ship_chg = 6.95 if first else 0.0
                taxable = qty * price - disc + ship_chg
                tax = 0.0 if ch == "Wholesale" else round(taxable * random.choice([0.06, 0.0725, 0.0825, 0.07]), 2)
                rows.append(dict(date=d, oid=oid, ch=ch, sku=sku, qty=qty, price=price, disc=disc,
                                 ship=ship_chg, tax=tax, ad=ad, label=label, status=status))
    return rows


# ---------------------------------------------------------------- production
# Optional per-SKU production buffer override
BUFFER = {}


def build_production(sales):
    demand = {}
    for s in sales:
        if s["status"] != "Cancelled":
            demand.setdefault(s["sku"], []).append((s["date"], s["qty"]))
    events = []
    for sku, _n, _c, _p, opening, *_ in PRODUCTS:
        stock = opening
        sdem = sorted(demand.get(sku, []))
        prod_dates = []
        for m in range(1, 12):
            prod_dates.append(date(FY, m, 1))
            prod_dates.append(date(FY, m, 15))
        prod_dates = [d for d in prod_dates if d < ASOF]
        for i, d in enumerate(prod_dates):
            nxt = prod_dates[i + 1] if i + 1 < len(prod_dates) else ASOF + timedelta(days=10)
            # stock movement since last event
            need = sum(q for dd, q in sdem if d <= dd < nxt + timedelta(days=6))
            buf = BUFFER.get(sku, math.ceil(need * 0.6) + 4)
            qty = need + buf - stock
            batch = 6 if PRICE[sku] > 12 else 12
            qty = max(0, math.ceil(qty / batch) * batch)
            if qty:
                events.append(dict(date=d, sku=sku, qty=qty))
            stock += qty - sum(q for dd, q in sdem if d <= dd < nxt)
            if stock < 0:  # never allow negative finished stock
                extra = math.ceil(-stock / batch) * batch
                events.append(dict(date=d, sku=sku, qty=extra))
                stock += extra
    events = [e for e in events if e["qty"] > 0]
    for sku, target in END_TARGET.items():
        _trim(events, demand.get(sku, []), sku, target)
    events = [e for e in events if e["qty"] > 0]
    events.sort(key=lambda e: (e["date"], e["sku"]))
    return events


# Desired on-hand at the report date for a few SKUs (demo of each status badge)
END_TARGET = {"CAN-001": 6, "CAN-005": 2, "MEL-002": 0, "DIF-001": 2}


def _min_running(events, dem, sku):
    opening = next(p[4] for p in PRODUCTS if p[0] == sku)
    moves = [(e["date"], 0, e["qty"]) for e in events if e["sku"] == sku] + [(d, 1, -q) for d, q in dem]
    stock, low = opening, opening
    for _d, _o, q in sorted(moves):
        stock += q
        low = min(low, stock)
    return low, stock


def _trim(events, dem, sku, target):
    _low, final = _min_running(events, dem, sku)
    excess = final - target
    for e in sorted([e for e in events if e["sku"] == sku], key=lambda e: e["date"], reverse=True):
        if excess <= 0:
            break
        cut = min(e["qty"], excess)
        e["qty"] -= cut
        if _min_running(events, dem, sku)[0] < 0:
            e["qty"] += cut
            break
        excess -= cut


# ---------------------------------------------------------------- purchases
LOW_MATS = {"MAT-010", "MAT-006", "MAT-009", "MAT-019"}   # left low on purpose for the demo
ON_ORDER = {"MAT-010": 72}


def _usage(events):
    use = {}
    for e in events:
        for mid, q in RECIPES[e["sku"]]:
            use.setdefault(mid, []).append((e["date"], q * (1 + WASTE.get(mid, 0)) * e["qty"]))
    return use


def build_purchases(events):
    use = _usage(events)
    purchases = []
    for mid, name, _c, _u, supplier, opening, cost, lead, moq in MATERIALS:
        stock = opening
        evs = sorted(use.get(mid, []))
        dates = sorted({d for d, _ in evs})
        for d in dates:
            need_now = sum(q for dd, q in evs if dd == d)
            horizon = sum(q for dd, q in evs if d <= dd < d + timedelta(days=50))
            low = False
            target = need_now * 1.05 if low else horizon * 1.5
            if stock < target:
                buy = math.ceil((target - stock) / moq) * moq
                uc = round(cost * random.uniform(0.95, 1.06), 4)
                freight = round(random.choice([0, 0, 6.5, 8.95, 12.0]), 2)
                purchases.append(dict(date=max(d - timedelta(days=3), date(FY, 1, 1)), mid=mid, qty=buy, cost=uc,
                                      freight=freight, supplier=supplier, status="Received",
                                      ref=f"PO-{len(purchases) + 2101}"))
                stock += buy
            stock -= need_now
    for mid, target in MAT_END_TARGET.items():
        _trim_purchases(purchases, use.get(mid, []), mid, target)
    purchases = [p for p in purchases if p["qty"] > 0]
    for mid, q in ON_ORDER.items():
        m = MAT[mid]
        purchases.append(dict(date=date(FY, 11, 17), mid=mid, qty=q, cost=m[6], freight=9.5,
                              supplier=m[4], status="Ordered", ref=f"PO-{len(purchases) + 2101}",
                              expected=date(FY, 12, 1)))
    purchases.sort(key=lambda p: p["date"])
    return purchases


# Desired on-hand at the report date for a few materials (demo of each badge)
MAT_END_TARGET = {"MAT-009": 8, "MAT-010": 20, "MAT-006": 185, "MAT-019": 62}


def _mat_running(purchases, uses, mid):
    stock = low = MAT[mid][5]
    moves = [(p["date"], 0, p["qty"]) for p in purchases if p["mid"] == mid] + [(d, 1, -q) for d, q in uses]
    for _d, _o, q in sorted(moves):
        stock += q
        low = min(low, stock)
    return low, stock


def _trim_purchases(purchases, uses, mid, target):
    excess = _mat_running(purchases, uses, mid)[1] - target
    for p in sorted([p for p in purchases if p["mid"] == mid], key=lambda p: p["date"], reverse=True):
        if excess <= 0:
            break
        cut = min(p["qty"], excess)
        p["qty"] -= cut
        while cut > 0 and _mat_running(purchases, uses, mid)[0] < 0:
            p["qty"] += 1
            cut -= 1
        excess -= cut
    for p in purchases:
        if p["mid"] == mid:
            p["qty"] = round(p["qty"], 1)


def build_stock_log(sales):
    events = build_production(sales)
    purchases = build_purchases(events)
    log = []
    for p in purchases:
        log.append(dict(date=p["date"], type="Material Purchase", sku="", mid=p["mid"], qty=p["qty"],
                        cost=p["cost"], freight=p["freight"], supplier=p["supplier"], status=p["status"],
                        expected=p.get("expected"), ref=p["ref"], notes=""))
    for i, e in enumerate(events):
        log.append(dict(date=e["date"], type="Production", sku=e["sku"], mid="", qty=e["qty"], cost=None,
                        freight=None, supplier="", status="", expected=None,
                        ref=f"B-{e['date'].strftime('%m%d')}-{i % 90 + 10}", notes=""))
    # a few realistic adjustments
    refunded = [s for s in sales if s["status"] == "Refunded"]
    if refunded:
        s = refunded[0]
        log.append(dict(date=s["date"] + timedelta(days=9), type="Return to Stock", sku=s["sku"], mid="",
                        qty=1, cost=None, freight=None, supplier="", status="", expected=None,
                        ref=s["oid"], notes="Returned unopened - resellable"))
    log.append(dict(date=date(FY, 3, 12), type="Damaged / Waste", sku="", mid="MAT-009", qty=2, cost=None,
                    freight=None, supplier="", status="", expected=None, ref="", notes="Jars cracked in delivery"))
    log.append(dict(date=date(FY, 7, 22), type="Damaged / Waste", sku="CAN-002", mid="", qty=1, cost=None,
                    freight=None, supplier="", status="", expected=None, ref="", notes="Frosting - kept as studio sample"))
    log.append(dict(date=date(FY, 6, 30), type="Adjustment", sku="", mid="MAT-017", qty=-12, cost=None,
                    freight=None, supplier="", status="", expected=None, ref="Count", notes="Mid-year stock count"))
    log.sort(key=lambda r: (r["date"], r["type"]))
    return log


# ---------------------------------------------------------------- expenses
def build_expenses():
    ex = []

    def add(d, vendor, desc, cat, amt, pay="Business Credit Card", rec="Yes", ded=None):
        ex.append(dict(date=d, vendor=vendor, desc=desc, cat=cat, amt=round(amt, 2), pay=pay, rec=rec, ded=ded))

    for m in range(1, 12):
        add(date(FY, m, 1), "Shared Maker Studio", "Studio membership", "Rent / Studio Space", 275, "Bank Transfer")
        add(date(FY, m, 3), "Shopify", "Basic plan subscription", "Website & Subscriptions", 39)
        add(date(FY, m, 4), "Canva", "Canva Pro", "Software & Apps", 15)
        add(date(FY, m, 8), "City Power & Light", "Studio electricity", "Utilities", random.uniform(48, 78), "Bank Transfer")
        add(date(FY, m, 12), "Mobile Carrier", "Phone & internet (60% business)", "Phone & Internet", 85, ded=0.6)
        add(date(FY, m, 15), "Etsy", "Etsy Ads (onsite)", "Advertising & Marketing",
            random.uniform(45, 70) if m < 9 else random.uniform(90, 140))
        add(date(FY, m, 20), "Hiscox", "General liability insurance", "Insurance", 32)
        if m % 2 == 0:
            add(date(FY, m, 18), "PackRight Supplies", "Packing tape, void fill", "Shop Supplies (non-inventory)",
                random.uniform(22, 48))
        if m in (4, 5, 9, 10, 11):
            add(date(FY, m, 6), "Town Makers Market", "Booth fee", "Market & Booth Fees", random.choice([60, 75, 95]))
        if m in (3, 9):
            add(date(FY, m, 22), "Props & Co.", "Photography props & backdrops", "Photography & Props",
                random.uniform(35, 80))
        if m in (2, 6, 10):
            add(date(FY, m, 26), "USPS", "Supplier sample postage", "Postage (non-order)", random.uniform(12, 30))
    add(date(FY, 1, 10), "County Clerk", "Business license renewal", "Taxes & Licenses", 75)
    add(date(FY, 2, 14), "Melt Pro Tools", "Pouring pitcher & heat gun", "Equipment (< $2,500)", 189)
    add(date(FY, 3, 30), "Bright Books CPA", "2025 tax return prep", "Legal & Professional", 425, "Bank Transfer")
    add(date(FY, 5, 9), "Maker Academy", "Candle business course", "Education & Training", 149)
    add(date(FY, 6, 3), "Bank", "Monthly account fees (YTD)", "Bank & Card Fees", 18, "Bank Transfer")
    add(date(FY, 8, 18), "Instagram", "Boosted Reels - fall launch", "Advertising & Marketing", 120)
    add(date(FY, 9, 5), "Office Depot", "Label printer ink & paper", "Office Supplies", 64)
    add(date(FY, 10, 2), "Gas Station", "Supplier pickup mileage", "Car & Vehicle", 46, "Business Debit Card")
    add(date(FY, 10, 21), "Freelance Designer", "Holiday packaging design", "Contract Labor", 300, "PayPal")
    add(date(FY, 11, 6), "Craft Fair Cafe", "Wholesale buyer lunch", "Meals (50%)", 58, ded=0.5)
    ex.sort(key=lambda r: r["date"])
    return ex
