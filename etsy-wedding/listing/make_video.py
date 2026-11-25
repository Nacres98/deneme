"""Silent ~15 s listing video (1600x1200, H.264) from the rendered listing images (slow zoom + cross-fades).
Usage: python3 listing/make_video.py  ->  listing/upload/listing_video.mp4
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE / "images"
OUT = HERE / "upload"
OUT.mkdir(exist_ok=True)
SCENES = ["01", "02", "03", "04", "05", "06", "07", "09"]
DUR, FADE, FPS = 2.2, 0.4, 30
W, H = 1600, 1200
inputs, filters = [], []
for i, n in enumerate(SCENES):
    inputs += ["-i", str(IMG / f"{n}.png")]
    frames = int(DUR * FPS)
    filters.append(f"[{i}:v]scale={W * 2}:{H * 2},zoompan=z='min(zoom+0.0006,1.05)':d={frames}:"
                   f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[v{i}]")
prev, offset = "v0", DUR - FADE
for i in range(1, len(SCENES)):
    filters.append(f"[{prev}][v{i}]xfade=transition=fade:duration={FADE}:offset={offset:.2f}[x{i}]")
    prev, offset = f"x{i}", offset + DUR - FADE
subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-c:v", "libx264",
                "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
                str(OUT / "listing_video.mp4")], check=True, capture_output=True)
print("wrote", OUT / "listing_video.mp4")
