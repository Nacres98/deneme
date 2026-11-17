#!/usr/bin/env python3
"""Scan a footage folder: per clip metadata + shot list + labelled shot sheets.

Usage: python3 tools/index_footage.py footage/gta6_official [--out footage_index]

Writes <out>/manifest.json (merged with any existing hand annotations) and
<out>/<clip>_shots_XX.jpg sheets (one thumbnail per shot, labelled with shot id + time range).
Annotate subjects by editing manifest.json -> clips[*].shots[*].tags / note, or with
tools/annotate.py. Existing annotations are preserved when re-indexing.
"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_reference import probe, detect_cuts, grab, FONT  # noqa: E402
from PIL import Image, ImageDraw, ImageFont


def sheets(clip, shots, frames, out, cols=4, per=24):
    font = ImageFont.truetype(str(FONT), 22)
    font.set_variation_by_name("ExtraBold")
    tw = 320
    paths = []
    for k in range(0, len(shots), per):
        chunk = list(zip(shots[k:k + per], frames[k:k + per]))
        th = int(tw * 9 / 16)
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * th), (16, 16, 16))
        d = ImageDraw.Draw(sheet)
        for i, (s, f) in enumerate(chunk):
            x, y = (i % cols) * tw, (i // cols) * th
            if f and f.exists():
                sheet.paste(Image.open(f).resize((tw, th)), (x, y))
            d.text((x + 6, y + 4), f"#{s['id']} {s['start']:.1f}-{s['end']:.1f}", font=font,
                   fill=(255, 230, 0), stroke_width=3, stroke_fill=(0, 0, 0))
        p = out / f"{clip}_shots_{k // per + 1:02d}.jpg"
        sheet.save(p, quality=85)
        paths.append(str(p))
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default="footage_index")
    ap.add_argument("--scene", type=float, default=9.0)
    a = ap.parse_args()
    out = Path(a.out); (out / "thumbs").mkdir(parents=True, exist_ok=True)
    mpath = out / "manifest.json"
    old = json.loads(mpath.read_text()) if mpath.exists() else {"clips": {}}
    clips = {}
    for f in sorted(Path(a.folder).glob("*")):
        if f.suffix.lower() not in (".mp4", ".mov", ".mkv", ".webm"):
            continue
        meta = probe(f)
        v = next(s for s in meta["streams"] if s["codec_type"] == "video")
        n, d = map(int, v["avg_frame_rate"].split("/"))
        dur = float(meta["format"]["duration"])
        cuts = [t for t, _ in detect_cuts(f, a.scene)]
        bounds = [0.0] + cuts + [dur]
        prev = {s["id"]: s for s in old["clips"].get(f.stem, {}).get("shots", [])}
        shots, frames = [], []
        for i in range(len(bounds) - 1):
            s0, s1 = bounds[i], bounds[i + 1]
            if s1 - s0 < 0.2:
                continue
            sid = len(shots) + 1
            th = out / "thumbs" / f"{f.stem}_{sid:03d}.jpg"
            grab(f, (s0 + s1) / 2, th, width=480)
            keep = prev.get(sid, {}) if abs(prev.get(sid, {}).get("start", -9) - s0) < 0.1 else {}
            shots.append({"id": sid, "start": round(s0, 3), "end": round(s1, 3),
                          "len": round(s1 - s0, 3), "tags": keep.get("tags", []), "note": keep.get("note", "")})
            frames.append(th)
        clips[f.stem] = {
            "path": str(f), "game": old["clips"].get(f.stem, {}).get("game", "UNKNOWN"),
            "source": old["clips"].get(f.stem, {}).get("source", ""),
            "duration": round(dur, 3), "width": v["width"], "height": v["height"],
            "fps": round(n / d, 3) if d else None, "shots": shots,
            "sheets": sheets(f.stem, shots, frames, out),
        }
        print(f"{f.name}: {v['width']}x{v['height']} {n/d:.0f}fps {dur:.1f}s, {len(shots)} shots")
    mpath.write_text(json.dumps({"clips": clips}, indent=2))


if __name__ == "__main__":
    main()
