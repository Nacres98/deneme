#!/usr/bin/env python3
"""Analyze a reference Short: metadata, cuts, pacing, caption placement/colour, audio, transcript.

Usage:
    python3 tools/analyze_reference.py reference/ref.mp4 [--out reference/analysis]
                                       [--every 1.5] [--scene 10] [--no-transcribe]

Outputs (in --out):
    meta.json            ffprobe stream info
    cuts.json            detected hard cuts + shot lengths
    frames/              stills every N seconds and just after every cut
    contact_XX.jpg       4x4 contact sheets (16 frames each) with timestamps
    captions.json        per-frame estimate of caption band (y-range) and highlight colours
    audio.json           loudness per 0.5 s + detected transient (SFX/impact) times
    transcript.json      word-level transcript (faster-whisper), words/sec
    report.md            human-readable summary
"""
import argparse, json, math, os, re, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets/fonts/Montserrat.ttf"

# palette from the brief - used to classify highlight words
GREEN = np.array([0x43, 0xE3, 0x4E]); RED = np.array([0xF0, 0x44, 0x4B])


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    return json.loads(r.stdout)


def detect_cuts(path, threshold):
    """Hard-cut detection with ffmpeg scdet; returns list of (time, score)."""
    r = run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf",
             f"scale=270:-2,scdet=threshold={threshold}", "-an", "-f", "null", "-"])
    cuts = []
    for m in re.finditer(r"lavfi\.scd\.score:\s*([\d.]+),\s*lavfi\.scd\.time:\s*([\d.]+)", r.stderr):
        cuts.append((float(m.group(2)), float(m.group(1))))
    # merge cuts closer than 0.15 s (flashes / impact frames)
    merged = []
    for t, s in cuts:
        if merged and t - merged[-1][0] < 0.15:
            if s > merged[-1][1]:
                merged[-1] = (t, s)
        else:
            merged.append((t, s))
    return merged


def grab(path, t, out, width=540):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(path),
         "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", str(out)])
    return out.exists()


def caption_band(img):
    """Estimate where bold white/green/red outlined text sits.

    Text pixels = saturated caption colours (white / palette green / palette red) that sit next to
    very dark outline pixels. Returns row-density profile and colour counts."""
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    h, w, _ = a.shape
    lum = a.mean(axis=2)
    white = (a.min(axis=2) > 225)
    green = (np.abs(a - GREEN).sum(axis=2) < 90)
    red = (np.abs(a - RED).sum(axis=2) < 90)
    dark = lum < 40
    # dilate dark mask by 3 px to find "near an outline"
    from numpy.lib.stride_tricks import sliding_window_view
    pad = np.pad(dark, 3)
    near_dark = sliding_window_view(pad, (7, 7)).any(axis=(2, 3))
    text = (white | green | red) & near_dark
    rows = text.sum(axis=1) / w
    band = None
    if rows.max() > 0.02:
        idx = np.where(rows > rows.max() * 0.35)[0]
        band = (int(idx.min()) / h, int(idx.max()) / h)
    return {
        "band": band,
        "white_px": int((white & near_dark).sum()),
        "green_px": int((green & near_dark).sum()),
        "red_px": int((red & near_dark).sum()),
    }


def contact_sheets(frames, outdir, per=16, cols=4):
    font = ImageFont.truetype(str(FONT), 28) if FONT.exists() else ImageFont.load_default()
    try:
        font.set_variation_by_name("ExtraBold")
    except Exception:
        pass
    sheets = []
    for k in range(0, len(frames), per):
        chunk = frames[k:k + per]
        ims = [Image.open(f) for _, f, _ in chunk]
        tw, th = 270, int(270 * ims[0].height / ims[0].width)
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for i, ((t, _, tag), im) in enumerate(zip(chunk, ims)):
            x, y = (i % cols) * tw, (i // cols) * th
            sheet.paste(im.resize((tw, th)), (x, y))
            label = f"{t:05.2f}s{' CUT' if tag == 'cut' else ''}"
            d.text((x + 8, y + 6), label, font=font, fill=(255, 230, 0), stroke_width=3, stroke_fill=(0, 0, 0))
        p = outdir / f"contact_{k // per + 1:02d}.jpg"
        sheet.save(p, quality=88)
        sheets.append(p)
    return sheets


def audio_profile(path):
    """RMS loudness per 0.5 s window and transient onsets (likely whooshes / impacts)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-ac", "1",
                        "-ar", "16000", "-f", "s16le", "-"], capture_output=True)
    if not r.stdout:
        return None
    x = np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768
    win = 8000
    n = len(x) // win
    rms = [float(20 * np.log10(np.sqrt((x[i*win:(i+1)*win] ** 2).mean()) + 1e-9)) for i in range(n)]
    # onset: 20 ms energy jump
    hop = 320
    e = np.array([np.sqrt((x[i:i+hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)])
    de = np.diff(e, prepend=e[0])
    thr = de.mean() + 4 * de.std()
    onsets, last = [], -1
    for i, v in enumerate(de):
        t = i * hop / 16000
        if v > thr and t - last > 0.25:
            onsets.append(round(t, 2)); last = t
    return {"window_s": 0.5, "rms_db": rms, "onsets": onsets}


def transcribe(path, model_size):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    m = WhisperModel(model_size, device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(path), word_timestamps=True, vad_filter=True)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    return {"language": info.language, "words": words}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=str(ROOT / "reference/analysis"))
    ap.add_argument("--every", type=float, default=1.5)
    ap.add_argument("--scene", type=float, default=10.0, help="scdet threshold (lower = more cuts)")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--whisper", default="small")
    a = ap.parse_args()

    src = Path(a.video); out = Path(a.out); (out / "frames").mkdir(parents=True, exist_ok=True)
    meta = probe(src)
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    dur = float(meta["format"]["duration"])
    num, den = map(int, v["avg_frame_rate"].split("/"))
    fps = num / den if den else 0
    print(f"[meta] {v['width']}x{v['height']} {fps:.2f} fps {dur:.2f}s")

    cuts = detect_cuts(src, a.scene)
    times = [0.0] + [t for t, _ in cuts] + [dur]
    shots = [round(times[i+1] - times[i], 3) for i in range(len(times) - 1)]
    (out / "cuts.json").write_text(json.dumps({"cuts": cuts, "shot_lengths": shots}, indent=2))
    print(f"[cuts] {len(cuts)} cuts, median shot {np.median(shots):.2f}s")

    # frames: regular interval + just after each cut
    pts = [(round(t, 2), "tick") for t in np.arange(0.2, dur, a.every)]
    pts += [(round(min(t + 0.1, dur - 0.05), 2), "cut") for t, _ in cuts]
    pts.sort()
    frames, cap = [], []
    for t, tag in pts:
        f = out / "frames" / f"f_{t:07.2f}_{tag}.jpg"
        if grab(src, t, f):
            frames.append((t, f, tag))
            c = caption_band(Image.open(f)); c["t"] = t; cap.append(c)
    (out / "captions.json").write_text(json.dumps(cap, indent=2))

    # two 16-frame sheets that sample the whole video evenly (for the QC step), plus full sheets
    idx = sorted(set(int(round(i)) for i in np.linspace(0, len(frames) - 1, min(32, len(frames)))))
    even = [frames[i] for i in idx]
    sheets = contact_sheets(even, out)
    print(f"[sheets] {[str(s) for s in sheets]}")

    aud = audio_profile(src)
    if aud:
        (out / "audio.json").write_text(json.dumps(aud))
    tr = None if a.no_transcribe else transcribe(src, a.whisper)
    if tr:
        (out / "transcript.json").write_text(json.dumps(tr, indent=2))

    # ---- report ----
    bands = [c["band"] for c in cap if c["band"]]
    L = [f"# Reference analysis: {src.name}", "",
         f"- Resolution: {v['width']}x{v['height']}, {fps:.2f} fps, {dur:.2f} s, codec {v['codec_name']}",
         f"- Hard cuts: {len(cuts)} -> {len(cuts) / dur * 60:.0f} cuts/min",
         f"- Shot length: median {np.median(shots):.2f}s, mean {np.mean(shots):.2f}s, "
         f"min {min(shots):.2f}s, max {max(shots):.2f}s",
         f"- Shots under 1.5 s: {sum(s < 1.5 for s in shots) / len(shots):.0%}"]
    if bands:
        tops = [b[0] for b in bands]; bots = [b[1] for b in bands]
        L.append(f"- Caption band (fraction of height): top ~{np.median(tops):.2f}, bottom ~{np.median(bots):.2f} "
                 f"(text found in {len(bands)}/{len(cap)} frames)")
        g = sum(c["green_px"] > 400 for c in cap); r = sum(c["red_px"] > 400 for c in cap)
        L.append(f"- Frames with green highlight: {g}; with red highlight: {r}")
    if aud:
        L.append(f"- Audio transients (likely SFX hits): {len(aud['onsets'])}; "
                 f"first ones at {aud['onsets'][:12]}")
    if tr and tr["words"]:
        w = tr["words"]; speech = w[-1]["e"] - w[0]["s"]
        L.append(f"- Narration: {len(w)} words, {len(w) / speech * 60:.0f} wpm, first word at {w[0]['s']:.2f}s")
        L += ["", "## Transcript", "", " ".join(x["w"] for x in w)]
    L += ["", "## Shot list", "", "| # | start | length |", "|---|---|---|"]
    L += [f"| {i+1} | {times[i]:.2f} | {s:.2f} |" for i, s in enumerate(shots)]
    (out / "report.md").write_text("\n".join(L) + "\n")
    print(f"[done] {out / 'report.md'}")


if __name__ == "__main__":
    main()
