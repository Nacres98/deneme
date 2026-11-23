"""Small contact sheet of listing/images/*.png for quick visual review."""
import sys
from glob import glob

from PIL import Image

files = sorted(glob("listing/images/*.png"))
for f in files:
    print(f, Image.open(f).size)
w, h = 750, 562
sheet = Image.new("RGB", (w * 2, h * ((len(files) + 1) // 2)), "white")
for i, f in enumerate(files):
    sheet.paste(Image.open(f).resize((w, h)), ((i % 2) * w, (i // 2) * h))
sheet.save(sys.argv[1])
