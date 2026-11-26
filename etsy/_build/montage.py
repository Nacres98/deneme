import sys, glob
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(d + "/*.jpg"))
tw = 640; th = 480
o = Image.new("RGB", (tw * 4 + 30, th * ((len(fs) + 3) // 4) + 10 * ((len(fs) + 3) // 4)), (90, 90, 90))
for i, f in enumerate(fs):
    im = Image.open(f).resize((tw, th))
    o.paste(im, ((i % 4) * (tw + 10), (i // 4) * (th + 10)))
o.save(out)
