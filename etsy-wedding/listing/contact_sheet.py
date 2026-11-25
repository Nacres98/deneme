"""Contact sheet of listing/images/01..10.png for a quick visual check. Usage: python3 listing/contact_sheet.py OUT.png"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ims = [Image.open(HERE / "images" / f"{i:02d}.png") for i in range(1, 11)]
sheet = Image.new("RGB", (2 * 760, 5 * 580), "white")
for i, im in enumerate(ims):
    t = im.copy()
    t.thumbnail((750, 570))
    sheet.paste(t, ((i % 2) * 760, (i // 2) * 580))
sheet.save(sys.argv[1])
print(ims[0].size, "->", sys.argv[1])
