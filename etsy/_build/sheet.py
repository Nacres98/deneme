import sys, subprocess, glob, os, tempfile
from PIL import Image
pdf, out = sys.argv[1], sys.argv[2]
first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
last = int(sys.argv[4]) if len(sys.argv) > 4 else 999
res = sys.argv[5] if len(sys.argv) > 5 else "28"
d = tempfile.mkdtemp()
subprocess.run(["pdftoppm", "-r", res, "-f", str(first), "-l", str(last), "-png", pdf, f"{d}/p"], check=True)
ims = [Image.open(f) for f in sorted(glob.glob(f"{d}/p*.png"))]
cols = 6
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + 6), rows * (h + 6)), (120, 120, 120))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
sheet.save(out)
print(len(ims), "pages", sheet.size)
