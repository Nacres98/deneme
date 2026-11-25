"""Fictional sample couple "Maya & Jordan" for the SAMPLE_DATA workbook (screenshots + learning).

Report date is pinned to 6 weeks before the wedding so every tab shows a realistic, mid-planning state.
All names, vendors and amounts are invented.
"""
import random
from datetime import date, timedelta

P1, P2 = "Maya", "Jordan"
WEDDING = date(2027, 6, 5)
REPORT = date(2027, 4, 24)
VENUE = "Willow Creek Barn, Asheville NC"
BUDGET = 38000
GUESTS = 130
CONTRIBUTORS = [("Maya & Jordan", 15000), ("Maya's parents", 12500), ("Jordan's parents", 10000), ("Grandma Rose", 1000)]

# (category, item, vendor, estimated, actual or None, notes)
BUDGET_ITEMS = [
    ("Venue", "Venue rental (Sat, 12 hrs)", "Willow Creek Barn", 6500, 6800, "Includes tables + ceremony lawn"),
    ("Catering & Bar", "Dinner, 110 guests", "Harvest Table Catering", 7200, 7480, "Family style"),
    ("Catering & Bar", "Bar package (4 hrs)", "Harvest Table Catering", 2400, 2250, "Beer, wine, 2 signature drinks"),
    ("Photography", "Photographer, 8 hrs + 2nd shooter", "Lena Park Photography", 3200, 3400, ""),
    ("Videography", "Highlight film", "Golden Hour Films", 1800, 1650, ""),
    ("Attire & Alterations", "Wedding dress", "Bloom Bridal", 1800, 1950, ""),
    ("Attire & Alterations", "Dress alterations", "Bloom Bridal", 300, None, "3 fittings"),
    ("Attire & Alterations", "Suit + shoes", "Tailor & Co.", 650, 690, ""),
    ("Hair & Makeup", "Hair & makeup, bride + 3", "Glow Studio", 900, 950, "Trial in April"),
    ("Flowers & Decor", "Bouquets & boutonnieres", "Wildflower Studio", 900, 980, ""),
    ("Flowers & Decor", "Centerpieces (12 tables)", "Wildflower Studio", 1400, 1350, ""),
    ("Music & Entertainment", "DJ + ceremony sound", "Spin Society", 1600, 1500, ""),
    ("Cake & Desserts", "Wedding cake, 3 tier", "Sugar & Spoon", 650, 620, ""),
    ("Stationery & Postage", "Save the dates", "Paper Moon Press", 220, 210, ""),
    ("Stationery & Postage", "Invitations + postage", "Paper Moon Press", 600, 640, ""),
    ("Ceremony & Officiant", "Officiant", "Rev. Sam Ortiz", 400, 400, ""),
    ("Ceremony & Officiant", "Marriage license", "", 90, 90, "County clerk"),
    ("Rentals & Lighting", "Chairs, linens, string lights", "Twinkle Rentals", 1500, 1620, ""),
    ("Transportation", "Guest shuttle", "River City Shuttles", 700, None, "2 loops from hotel"),
    ("Rings", "Wedding bands", "Hart Jewelers", 1400, 1320, ""),
    ("Favors & Gifts", "Guest favors", "", 300, None, "Local honey jars"),
    ("Favors & Gifts", "Wedding party gifts", "", 400, None, ""),
    ("Planner / Coordinator", "Day-of coordinator", "Simply Wed Co.", 1400, 1400, ""),
    ("Tips & Gratuities", "Vendor tips (see Tips tab)", "", 900, None, ""),
    ("Contingency", "Emergency fund", "", 700, None, "Keep ~2% aside"),
]

# vendor -> (category, contact, phone, email, web, status, contract, rating, notes)
VENDORS = [
    ("Willow Creek Barn", "Venue", "Ellie Grant", "(828) 555-0142", "events@willowcreekbarn.example", "willowcreekbarn.example", "Booked", "Yes", 5, "Rain plan: covered pavilion"),
    ("Mountain View Lodge", "Venue", "Tom Reyes", "(828) 555-0177", "tom@mvlodge.example", "mvlodge.example", "Declined", "No", 4, "Over budget"),
    ("Harvest Table Catering", "Catering & Bar", "Priya Shah", "(828) 555-0110", "hello@harvesttable.example", "harvesttable.example", "Booked", "Yes", 5, "Tasting done"),
    ("Smoke & Oak BBQ", "Catering & Bar", "Dan Wills", "(828) 555-0165", "dan@smokeoak.example", "smokeoak.example", "Quote received", "No", 4, ""),
    ("Lena Park Photography", "Photography", "Lena Park", "(828) 555-0133", "lena@lenapark.example", "@lenaparkphoto", "Booked", "Yes", 5, ""),
    ("Bright Frame Studio", "Photography", "Chris Ng", "(828) 555-0198", "chris@brightframe.example", "@brightframe", "Quote received", "No", 4, ""),
    ("Golden Hour Films", "Videography", "Ava Cole", "(828) 555-0121", "ava@goldenhour.example", "goldenhour.example", "Booked", "Yes", 5, ""),
    ("Bloom Bridal", "Attire & Alterations", "Nina", "(828) 555-0150", "shop@bloombridal.example", "bloombridal.example", "Booked", "Yes", 5, ""),
    ("Tailor & Co.", "Attire & Alterations", "Marco", "(828) 555-0186", "marco@tailorco.example", "tailorco.example", "Booked", "Yes", 4, ""),
    ("Glow Studio", "Hair & Makeup", "Jess Lee", "(828) 555-0104", "book@glowstudio.example", "@glowstudio", "Booked", "Yes", 5, ""),
    ("Wildflower Studio", "Flowers & Decor", "Rosa Diaz", "(828) 555-0139", "rosa@wildflower.example", "wildflower.example", "Booked", "Yes", 5, ""),
    ("Spin Society", "Music & Entertainment", "DJ Kai", "(828) 555-0127", "kai@spinsociety.example", "spinsociety.example", "Booked", "Yes", 5, ""),
    ("The Blue Notes", "Music & Entertainment", "Sam Hill", "(828) 555-0193", "band@bluenotes.example", "bluenotes.example", "Quote received", "No", 4, "5-piece band"),
    ("Sugar & Spoon", "Cake & Desserts", "Hannah", "(828) 555-0158", "orders@sugarspoon.example", "sugarspoon.example", "Booked", "Yes", 5, ""),
    ("Paper Moon Press", "Stationery & Postage", "Iris", "(828) 555-0112", "iris@papermoon.example", "papermoon.example", "Booked", "Yes", 5, ""),
    ("Rev. Sam Ortiz", "Ceremony & Officiant", "Sam Ortiz", "(828) 555-0170", "sam.ortiz@example.com", "", "Booked", "Yes", 5, ""),
    ("Twinkle Rentals", "Rentals & Lighting", "Leo", "(828) 555-0146", "leo@twinkle.example", "twinkle.example", "Booked", "Yes", 4, ""),
    ("River City Shuttles", "Transportation", "Office", "(828) 555-0181", "book@rivercity.example", "rivercity.example", "Contacted", "No", None, "Waiting on quote"),
    ("Hart Jewelers", "Rings", "Ms. Hart", "(828) 555-0115", "info@hartjewelers.example", "hartjewelers.example", "Booked", "Yes", 5, ""),
    ("Simply Wed Co.", "Planner / Coordinator", "Kim Tran", "(828) 555-0163", "kim@simplywed.example", "simplywed.example", "Booked", "Yes", 5, ""),
]
VENDOR_QUOTES = {"Willow Creek Barn": 6800, "Mountain View Lodge": 9200, "Harvest Table Catering": 9730,
                 "Smoke & Oak BBQ": 8100, "Lena Park Photography": 3400, "Bright Frame Studio": 2900,
                 "Golden Hour Films": 1650, "Spin Society": 1500, "The Blue Notes": 4200, "Twinkle Rentals": 1620,
                 "Simply Wed Co.": 1400, "Wildflower Studio": 2330, "Sugar & Spoon": 620, "Paper Moon Press": 850,
                 "Glow Studio": 950, "Hart Jewelers": 1320, "Rev. Sam Ortiz": 400, "Bloom Bridal": 1950,
                 "Tailor & Co.": 690}


def payments():
    """Deposits (paid) + final balances. Returns (item, type, due, amount, payer, paid, date_paid, notes)."""
    rnd = random.Random(11)
    payers = [c[0] for c in CONTRIBUTORS]
    rows = []
    finals = [date(2027, 4, 10), date(2027, 4, 30), date(2027, 5, 7), date(2027, 5, 15), date(2027, 5, 22), date(2027, 6, 1)]
    for i, (cat, item, vendor, est, act, _) in enumerate(BUDGET_ITEMS):
        cost = act or est
        if not vendor and cat not in ("Ceremony & Officiant",):
            continue
        if cat == "Ceremony & Officiant" and not vendor:  # license, paid in full
            rows.append((item, "Paid in full", date(2027, 4, 2), cost, payers[0], "Yes", date(2027, 4, 2), ""))
            continue
        if act is None:  # not contracted yet -> one scheduled payment, unpaid
            rows.append((item, "Deposit", date(2027, 5, 1), round(cost * 0.5), payers[0], "No", None, "Estimate"))
            continue
        payer = (payers[1] if cat in ("Venue", "Flowers & Decor") or item == "Wedding dress" else
                 payers[2] if cat == "Catering & Bar" else payers[0])
        if cost <= 700:
            d = date(2027, rnd.randint(1, 3), rnd.randint(2, 26))
            rows.append((item, "Paid in full", d, cost, payer, "Yes", d, ""))
            continue
        dep = round(cost * (0.5 if cost < 2000 else 0.3) / 10) * 10
        d = date(2026, rnd.randint(6, 11), rnd.randint(2, 26))
        rows.append((item, "Deposit", d, dep, payer, "Yes", d, ""))
        rest = cost - dep
        if cost >= 6000:  # installment + final
            inst = round(rest / 2 / 10) * 10
            d2 = date(2027, 2, 15)
            rows.append((item, "Installment", d2, inst, payer, "Yes", d2, ""))
            rest -= inst
        due = finals[i % len(finals)]
        if item == "Bar package (4 hrs)":  # one overdue to show the alert
            rows.append((item, "Final balance", date(2027, 4, 18), rest, payer, "No", None, "Overdue: call Priya"))
            continue
        paid = due < REPORT
        rows.append((item, "Final balance", due, rest, payer, "Yes" if paid else "No", due if paid else None,
                     "" if paid else ("Ask about card fee" if i % 4 == 0 else "")))
    rows.sort(key=lambda r: (r[2] or date(2100, 1, 1)))
    # Grandma Rose covers the cake
    rows = [(it, ty, du, am, ("Grandma Rose" if it == "Wedding cake, 3 tier" else pa), pd, dp, no)
            for it, ty, du, am, pa, pd, dp, no in rows]
    return rows


FIRST = ["Olivia", "Liam", "Emma", "Noah", "Ava", "Elijah", "Sophia", "James", "Isabella", "Lucas", "Mia", "Mason", "Amelia",
         "Ethan", "Harper", "Logan", "Evelyn", "Aiden", "Abigail", "Jackson", "Ella", "Levi", "Scarlett", "Sebastian", "Grace",
         "Mateo", "Chloe", "Jack", "Lily", "Owen", "Aria", "Henry", "Zoe", "Wyatt", "Nora", "Daniel", "Hazel", "Caleb", "Riley",
         "Isaac", "Layla", "Julian", "Ellie", "Ezra", "Stella", "Leo", "Violet", "Miles", "Aurora", "Theo", "Lucy", "Nathan",
         "Penelope", "Asher", "Claire", "Hudson", "Naomi", "Adrian", "Ruby", "Eli"]
LAST = ["Bennett", "Carter", "Diaz", "Ellis", "Foster", "Garcia", "Hayes", "Iverson", "Jensen", "Kim", "Lopez", "Morgan",
        "Nguyen", "Owens", "Patel", "Quinn", "Rivera", "Sullivan", "Turner", "Underwood", "Vasquez", "Walsh", "Young", "Zimmerman",
        "Brooks", "Chen", "Dawson", "Flores", "Grant", "Hughes"]
STREETS = ["Oak St", "Maple Ave", "Pine Rd", "Cedar Ln", "Elm Dr", "Birch Way", "Willow Ct", "Lakeview Blvd", "Hillcrest Dr"]
CITIES = ["Asheville, NC 28801", "Charlotte, NC 28202", "Raleigh, NC 27601", "Greenville, SC 29601", "Atlanta, GA 30303",
          "Nashville, TN 37203", "Richmond, VA 23219", "Chicago, IL 60601"]
MEALS = ["Chicken", "Beef", "Fish", "Vegetarian"]


def guests():
    """Returns list of dicts. ~100 invitations, ~140 people."""
    rnd = random.Random(5)
    out, used = [], set()
    plan = [(f"{P1}'s side", "Family", 26), (f"{P2}'s side", "Family", 22), (f"{P1}'s side", "Friends", 20),
            (f"{P2}'s side", "Friends", 18), ("Both / mutual", "Friends", 8), (f"{P1}'s side", "Work", 4), (f"{P2}'s side", "Work", 4)]
    for side, group, n in plan:
        for _ in range(n):
            while True:
                nm = f"{rnd.choice(FIRST)} {rnd.choice(LAST)}"
                if nm not in used:
                    used.add(nm)
                    break
            plus = rnd.random() < (0.45 if group != "Work" else 0.2)
            pn = (f"{rnd.choice(FIRST)} {nm.split()[1]}" if group == "Family" else rnd.choice(FIRST) + " " + rnd.choice(LAST)) if plus else ""
            r = rnd.random()
            rsvp = "Attending" if r < 0.72 else ("Declined" if r < 0.84 else "Pending")
            out.append(dict(name=nm, side=side, group=group, plus="Yes" if plus else "No", plus_name=pn,
                            addr=f"{rnd.randint(12, 980)} {rnd.choice(STREETS)}, {rnd.choice(CITIES)}",
                            contact=f"{nm.split()[0].lower()}.{nm.split()[1].lower()}@example.com",
                            std="Yes", inv="Yes", rsvp=rsvp,
                            meal=rnd.choice(MEALS) if rsvp == "Attending" else "",
                            meal2=(rnd.choice(MEALS) if rsvp == "Attending" and plus else ""),
                            diet=rnd.choice(["", "", "", "", "", "Gluten-free", "Nut allergy", "Dairy-free"]) if rsvp == "Attending" else "",
                            gift="", ty="No"))
    # gifts already received (shower/registry)
    for g in rnd.sample(out, 22):
        g["gift"] = rnd.choice(["Registry: stand mixer", "Registry: towels", "Check $150", "Registry: dutch oven",
                                "Honeymoon fund $100", "Picture frame", "Registry: wine glasses", "Check $200"])
        g["ty"] = "Yes" if rnd.random() < 0.6 else "No"
    return out


TABLES = [("Head Table", 10)] + [(f"Table {i}", 10) for i in range(1, 13)] + [(f"Table {i}", 10) for i in range(13, 16)]


def assign_tables(gs):
    """Seat attending + pending guests, family near the front."""
    order = sorted([g for g in gs if g["rsvp"] != "Declined"], key=lambda g: (g["group"] != "Family", g["side"], g["group"]))
    seats = {t: c for t, c in TABLES}
    seats["Head Table"] = 0  # wedding party only (kept simple)
    names = [t for t, _ in TABLES if t != "Head Table"]
    head = 10  # wedding party at the head table
    for g in [g for g in gs if g["group"] == "Friends" and g["rsvp"] == "Attending"]:
        size = 2 if g["plus"] == "Yes" else 1
        if size <= head:
            g["table"], g["group"] = "Head Table", "Wedding party"
            head -= size
        if head == 0:
            break
    order = [g for g in order if not g.get("table")]
    ti = 0
    for g in order:
        size = 2 if g["plus"] == "Yes" else 1
        if g["rsvp"] == "Pending" and sum(map(ord, g["name"])) % 3 == 0:
            continue  # leave some pending guests unseated on purpose
        while ti < len(names) and seats[names[ti]] < size:
            ti += 1
        if ti >= len(names):
            break
        g["table"] = names[ti]
        seats[names[ti]] -= size
    return gs


# Checklist: (task, phase, timeframe) - kept in BOTH files as a starter list
CHECKLIST = [
    ("Set your total budget and who's contributing", "Budget", "12+ months"),
    ("Draft the guest list (rough count)", "Guests", "12+ months"),
    ("Pick a wedding date (and a backup)", "Planning", "12+ months"),
    ("Research and tour venues", "Venue", "12+ months"),
    ("Book the venue and sign the contract", "Venue", "12+ months"),
    ("Hire a planner or day-of coordinator", "Vendors", "10-12 months"),
    ("Choose your wedding party", "Planning", "10-12 months"),
    ("Book photographer", "Vendors", "10-12 months"),
    ("Book videographer", "Vendors", "10-12 months"),
    ("Book caterer and schedule tasting", "Vendors", "10-12 months"),
    ("Start a wedding website", "Guests", "10-12 months"),
    ("Book officiant", "Ceremony", "8-10 months"),
    ("Book DJ or band", "Vendors", "8-10 months"),
    ("Shop for the dress / suit", "Attire", "8-10 months"),
    ("Reserve hotel room blocks for guests", "Guests", "8-10 months"),
    ("Order save the dates", "Stationery", "8-10 months"),
    ("Book florist", "Vendors", "6-8 months"),
    ("Send save the dates", "Stationery", "6-8 months"),
    ("Register for gifts", "Guests", "6-8 months"),
    ("Book hair & makeup", "Vendors", "6-8 months"),
    ("Book rentals (chairs, linens, lighting)", "Vendors", "6-8 months"),
    ("Plan the honeymoon and check passports", "Honeymoon", "6-8 months"),
    ("Order the cake / desserts", "Vendors", "4-6 months"),
    ("Book guest transportation", "Vendors", "4-6 months"),
    ("Order invitations", "Stationery", "4-6 months"),
    ("Buy wedding bands", "Attire", "4-6 months"),
    ("Choose wedding party attire", "Attire", "4-6 months"),
    ("Plan rehearsal dinner", "Planning", "4-6 months"),
    ("Book the honeymoon", "Honeymoon", "4-6 months"),
    ("Schedule dress fittings", "Attire", "2-4 months"),
    ("Hair & makeup trial", "Attire", "2-4 months"),
    ("Finalize the menu with caterer", "Vendors", "2-4 months"),
    ("Mail invitations (6-8 weeks out)", "Stationery", "1-2 months"),
    ("Write ceremony script / vows", "Ceremony", "1-2 months"),
    ("Choose ceremony and first-dance songs", "Ceremony", "1-2 months"),
    ("Buy favors and wedding party gifts", "Planning", "1-2 months"),
    ("Get the marriage license", "Ceremony", "1-2 months"),
    ("Confirm all vendor final payments due dates", "Budget", "1-2 months"),
    ("Chase missing RSVPs", "Guests", "2-4 weeks"),
    ("Give final headcount to caterer", "Vendors", "2-4 weeks"),
    ("Make the seating chart", "Guests", "2-4 weeks"),
    ("Final dress fitting", "Attire", "2-4 weeks"),
    ("Send day-of timeline to vendors + wedding party", "Planning", "2-4 weeks"),
    ("Prepare tip envelopes", "Budget", "1-2 weeks"),
    ("Break in wedding shoes", "Attire", "1-2 weeks"),
    ("Confirm arrival times with every vendor", "Vendors", "1-2 weeks"),
    ("Pack for the honeymoon", "Honeymoon", "Week of"),
    ("Pack an emergency kit", "Planning", "Week of"),
    ("Rehearsal + rehearsal dinner", "Ceremony", "Day before"),
    ("Hand off tip envelopes to coordinator", "Budget", "Wedding day"),
    ("Enjoy your day!", "Planning", "Wedding day"),
    ("Return rentals / suits", "After", "After"),
    ("Send thank-you cards", "After", "After"),
    ("Change name / update documents (optional)", "After", "After"),
    ("Leave reviews for your vendors", "After", "After"),
]

TIP_ROLES = [  # role, method, pct, flat, people, guide
    ("Catering staff / servers", "% of bill", 0.18, None, None, "15-20% of food & drink (check contract)"),
    ("Bartenders", "% of bill", 0.15, None, None, "10-20% of bar bill"),
    ("Hair stylist", "% of bill", 0.20, None, None, "15-25% of service"),
    ("Makeup artist", "% of bill", 0.20, None, None, "15-25% of service"),
    ("Photographer", "Flat amount", None, 150, None, "$50-200 per shooter (optional if owner)"),
    ("Videographer", "Flat amount", None, 100, None, "$50-200 per shooter"),
    ("DJ", "Flat amount", None, 100, None, "$50-150"),
    ("Band musicians", "Per person", None, 40, 5, "$25-50 per musician"),
    ("Officiant", "Flat amount", None, 75, None, "$50-100 or a donation"),
    ("Delivery / setup crew", "Per person", None, 15, 4, "$10-20 per person"),
    ("Shuttle / limo driver", "% of bill", 0.15, None, None, "15-20% of bill"),
    ("Day-of coordinator", "Flat amount", None, 150, None, "$100-300 (optional)"),
]

TIMELINE = [  # start, end, what, where, who
    ("09:00", "11:30", "Hair & makeup", "Bridal suite", "Bride + 3 attendants, Glow Studio"),
    ("11:30", "12:00", "Photographer arrives, detail shots", "Bridal suite", "Photographer"),
    ("12:00", "13:00", "Lunch + getting dressed", "Suites", "Wedding party"),
    ("13:15", "14:00", "First look + couple portraits", "Garden", "Couple, photographer, videographer"),
    ("14:00", "14:45", "Wedding party + family photos", "Lawn", "Families, wedding party"),
    ("15:00", "15:30", "Guests arrive, shuttle loop 1", "Ceremony lawn", "Ushers, driver"),
    ("15:30", "16:00", "Ceremony", "Ceremony lawn", "Officiant, DJ (sound)"),
    ("16:00", "17:00", "Cocktail hour", "Patio", "Bar, caterer, DJ"),
    ("17:00", "17:15", "Grand entrance", "Barn", "DJ, wedding party"),
    ("17:15", "18:15", "Dinner served", "Barn", "Caterer"),
    ("18:15", "18:45", "Toasts", "Barn", "Best man, maid of honor"),
    ("18:45", "19:00", "First dance + parent dances", "Barn", "DJ"),
    ("19:00", "19:15", "Cake cutting", "Barn", "Caterer, photographer"),
    ("19:15", "21:45", "Open dancing", "Barn", "DJ"),
    ("21:45", "22:00", "Sparkler send-off", "Front drive", "Coordinator"),
    ("22:00", "22:30", "Last shuttle + vendor breakdown", "Venue", "Driver, rentals, coordinator"),
]
