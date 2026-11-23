"""Silent ~13 s listing video (1600x1200, H.264) from the rendered listing images.

Each scene slowly zooms in (Ken Burns) and cross-fades into the next. Etsy plays listing videos without sound.
Usage: python3 listing/make_video.py  ->  listing/video/listing_video.mp4
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE / "images"
OUT = HERE / "video"
OUT.mkdir(exist_ok=True)
SCENES = ["01", "02", "03", "04", "05", "06", "08", "10"]
DUR, FADE, FPS = 2.0, 0.4, 30
W, H = 1600, 1200

inputs, filters = [], []
for i, n in enumerate(SCENES):
    inputs += ["-i", str(IMG / f"{n}.png")]
    frames = int(DUR * FPS)
    filters.append(
        f"[{i}:v]scale={W * 2}:{H * 2},zoompan=z='min(zoom+0.0007,1.05)':d={frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[v{i}]")
prev, offset = "v0", DUR - FADE
for i in range(1, len(SCENES)):
    lab = f"x{i}"
    filters.append(f"[{prev}][v{i}]xfade=transition=fade:duration={FADE}:offset={offset:.2f}[{lab}]")
    prev, offset = lab, offset + DUR - FADE
cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", f"[{prev}]",
       "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
       str(OUT / "listing_video.mp4")]
subprocess.run(cmd, check=True, capture_output=True)
print("wrote", OUT / "listing_video.mp4")
