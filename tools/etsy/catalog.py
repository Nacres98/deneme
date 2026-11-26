"""Single list of every Etsy product and product group -> etsy/CATALOG.md

    python3 -m tools.etsy.catalog
Update STATUS / add rows here whenever a product is made or listed.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# group id, name (TR), status: done | in progress | planned
GROUPS = [
    ("G1", "Spreadsheet şablonları (Excel + Google Sheets)", "done"),
    ("G2", "Yazdırılabilir PDF planlayıcılar (Letter + A4)", "done"),
    ("G3", "Dijital planlayıcı (GoodNotes/Notability, köprülü PDF)", "planned"),
    ("G4", "CV / özgeçmiş şablonları (Word + Google Docs)", "planned"),
    ("G5", "Duvar sanatı (yazdırılabilir poster, özgün tasarım)", "planned"),
    ("G6", "Çocuk etkinlik ve çalışma sayfaları", "planned"),
    ("G7", "Küçük işletme şablonları (fatura, envanter, sipariş takibi)", "planned"),
    ("G8", "Düğün ve etkinlik planlayıcıları", "planned"),
    ("G9", "Telefon duvar kâğıdı ve özgün ikon setleri (marka logosu yok)", "planned"),
    ("G10", "Sosyal medya / Canva şablonları (Canva hesabı gerekir)", "planned"),
]

# slug, group, product name, list price, sale price, format
PRODUCTS = [
    ("life-organizer", "G1", "Just In Case Life Organizer", 12.99, 5.19, "xlsx"),
    ("budget-planner-2027", "G1", "2027 Budget Planner", 9.99, 4.99, "xlsx"),
    ("habit-tracker-2027", "G1", "2027 Habit Tracker", 5.99, 2.99, "xlsx"),
    ("bundle-2027", "G1", "2027 Life Admin Bundle (3 spreadsheets)", 19.99, 7.99, "xlsx x3"),
    ("printable-planner-2027", "G2", "2027 Printable Planner (17 pages)", 7.99, 3.99, "PDF Letter + A4"),
    ("printable-budget-binder-2027", "G2", "2027 Budget Binder (10 pages)", 8.99, 4.49, "PDF Letter + A4"),
    ("printable-meal-planner", "G2", "Meal Planner (6 pages)", 5.99, 2.99, "PDF Letter + A4"),
    ("printable-cleaning-schedule", "G2", "Cleaning Schedule (6 pages)", 4.99, 2.99, "PDF Letter + A4"),
    ("printable-habit-mood-tracker", "G2", "Habit & Mood Tracker (5 pages)", 4.99, 2.99, "PDF Letter + A4"),
    ("bundle-printables", "G2", "Printable Home Planner Bundle (5 printables)", 24.99, 9.99, "PDF x5"),
]


def main():
    lines = ["# Etsy ürün kataloğu", "",
             "`python3 -m tools.etsy.catalog` ile `tools/etsy/catalog.py` dosyasından üretilir; elle düzenleme.", "",
             "## Ürün grupları", "", "| # | Grup | Durum | Ürün sayısı |", "|---|---|---|---|"]
    for gid, name, status in GROUPS:
        n = sum(1 for p in PRODUCTS if p[1] == gid)
        lines.append(f"| {gid} | {name} | {status} | {n} |")
    for gid, name, _ in GROUPS:
        rows = [p for p in PRODUCTS if p[1] == gid]
        if not rows:
            continue
        lines += ["", f"## {gid}: {name}", "", "| Ürün | Format | Liste | Kampanya | Klasör |", "|---|---|---|---|---|"]
        for slug, _, name_, lp, sp, fmt in rows:
            ok = (ROOT / "etsy" / "products" / slug / "listing.md").exists()
            lines.append(f"| {name_} | {fmt} | ${lp:.2f} | **${sp:.2f}** | `products/{slug}/`{'' if ok else ' (listing eksik)'} |")
    total = len(PRODUCTS)
    lines += ["", f"Toplam: **{total} ilan** hazır."]
    out = ROOT / "etsy" / "CATALOG.md"
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
