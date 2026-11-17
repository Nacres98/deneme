#!/usr/bin/env python3
"""Build a Short from a project's edit.json.

    python3 -m tools.shorts.build projects/<slug> [--draft] [--start 0 --end 10] [--stills 16]

Pipeline: voice (TTS or recording) -> whisper word alignment -> resolve word-anchored timeline
-> render frames (crop/zoom footage + captions + graphics) -> mix audio (voice, SFX, music) -> encode.
Everything resolved is written to <project>/build/timeline.json so the edit is inspectable/editable.
"""
import argparse, json, math, subprocess, sys, time
from pathlib import Path

import cv2
import numpy as np

from . import audio, captions, gfx, style, voice
from .draw import ease_in_out, clamp

ROOT = Path(__file__).resolve().parents[2]


# ======================================================================== timeline
def load_manifest(path):
    return json.loads(Path(path).read_text())["clips"]


def find_word(words, key, after=0):
    """Index of first word at/after `after` whose normalised text starts with key's first token."""
    toks = [voice.norm(k) for k in key.split()]
    for i in range(after, len(words)):
        def ok(w, k):
            n = voice.norm(w["text"])
            return n == k or (len(k) >= 4 and n.startswith(k))
        if all(i + j < len(words) and ok(words[i + j], toks[j]) for j in range(len(toks))):
            return i
    raise KeyError(f"anchor word '{key}' not found after index {after}: "
                   f"{' '.join(w['text'] for w in words[after:after + 30])}")


def resolve_time(spec, words, line, after_idx=0, edge="s"):
    """spec: word text | '+1.2' (sec from line start) | '-0.5' (sec before line end) | 'end'."""
    if spec is None:
        return line["t0"], after_idx
    if isinstance(spec, (int, float)):
        return line["t0"] + spec, after_idx
    if spec == "end":
        return line["t1"], after_idx
    if spec[0] in "+-" and spec[1:].replace(".", "").isdigit():
        v = float(spec)
        return (line["t0"] + v if v >= 0 else line["t1"] + v), after_idx
    i = find_word(words, spec, after_idx)
    return words[i][edge], i


def build_timeline(proj, spec, force_voice=False):
    bdir = proj / "build"; bdir.mkdir(exist_ok=True)
    vcfg = spec["voice"]
    lines = spec["lines"]
    units = {ln["id"]: voice.parse(ln["text"]) for ln in lines}

    # ---------------- voice
    vdir = proj / "audio" / "voice"
    cache = vdir / "spoken.json"
    want = {ln["id"]: voice.spoken_text(units[ln["id"]]) for ln in lines}
    have = json.loads(cache.read_text()) if cache.exists() else {}
    if vcfg.get("engine", "kokoro") == "kokoro":
        todo = [(i, t) for i, t in want.items()
                if force_voice or have.get(i) != t + f"|{vcfg['voice']}|{vcfg['speed']}" or not (vdir / f"{i}.wav").exists()]
        if todo:
            print(f"[voice] kokoro {vcfg['voice']} x{vcfg['speed']}: {len(todo)} line(s)")
            voice.tts_kokoro(todo, vcfg["voice"], vcfg["speed"], vdir)
            for i, t in todo:
                have[i] = t + f"|{vcfg['voice']}|{vcfg['speed']}"
            cache.write_text(json.dumps(have, indent=1))
    elif vcfg["engine"] == "elevenlabs":
        sig = lambda t: t + f"|el|{vcfg['voice_id']}|{vcfg.get('model', 'eleven_multilingual_v2')}|{vcfg.get('speed', 1.0)}"
        todo = [(i, t) for i, t in want.items() if force_voice or have.get(i) != sig(t) or not (vdir / f"{i}.wav").exists()]
        if todo:
            print(f"[voice] elevenlabs {vcfg['voice_id']}: {len(todo)} line(s), {sum(len(t) for _, t in todo)} chars")
            voice.tts_elevenlabs(todo, vcfg["voice_id"], vdir, vcfg.get("model", "eleven_multilingual_v2"),
                                 vcfg.get("settings"), vcfg.get("speed", 1.0))
            for i, t in todo:
                have[i] = sig(t)
                cache.write_text(json.dumps(have, indent=1))
    # engine "recorded": put your own <line id>.wav files in audio/voice/ (one per script line)

    # ---------------- assemble narration + align
    gap = vcfg.get("gap", 0.16)
    t = spec.get("lead_in", 0.05)
    words, line_times, vparts = [], {}, []
    for ln in lines:
        wav = audio.load_wav(vdir / f"{ln['id']}.wav")
        if vcfg.get("max_pause") or vcfg.get("tempo"):
            # tighten delivery without re-generating (no TTS credits): cap pauses, optional tempo
            af = []
            if vcfg.get("max_pause"):
                mp = vcfg["max_pause"]
                af.append(f"silenceremove=stop_periods=-1:stop_duration={mp}:stop_threshold=-38dB:stop_silence={mp}")
            if vcfg.get("tempo"):
                af.append(f"atempo={vcfg['tempo']}")
            wav = np.frombuffer(subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(audio.SR), "-ac", "1", "-i", "-", "-af", ",".join(af),
                 "-f", "f32le", "-ar", str(audio.SR), "-ac", "1", "-"], input=wav.astype(np.float32).tobytes(),
                capture_output=True, check=True).stdout, np.float32).copy()
        # trim TTS leading/trailing silence
        nz = np.where(np.abs(wav) > 0.01)[0]
        if len(nz):
            wav = wav[max(0, nz[0] - int(0.03 * audio.SR)): nz[-1] + int(0.08 * audio.SR)]
        dur = len(wav) / audio.SR
        tmp = bdir / f"_trim_{ln['id']}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(audio.SR), "-ac", "1", "-i", "-", str(tmp)],
                       input=wav.astype(np.float32).tobytes(), check=True)
        ww = voice.whisper_words(tmp, prompt=voice.spoken_text(units[ln["id"]]))
        aligned = voice.align_units(units[ln["id"]], ww, offset=t, line_dur=dur)
        for w in aligned:
            w["line"] = ln["id"]
        line_times[ln["id"]] = {"t0": t, "t1": t + dur, "w0": len(words)}
        words += aligned
        vparts.append((t, wav))
        t += dur + ln.get("pause_after", gap)
    total = t + spec.get("tail", 0.9)
    narration = np.zeros(int(total * audio.SR) + 1, np.float32)
    for t0, wav in vparts:
        i = int(t0 * audio.SR); narration[i:i + len(wav)] += wav

    # ---------------- shots / overlays
    shots, overlays, sfx, hidden = [], [], [], []
    clips = load_manifest(ROOT / spec.get("manifest", "footage_index/manifest.json"))
    for li, ln in enumerate(lines):
        lt = line_times[ln["id"]]
        lw = [w for w in words if w["line"] == ln["id"]]
        lt_next = line_times[lines[li + 1]["id"]]["t0"] if li + 1 < len(lines) else total
        line = {"t0": lt["t0"], "t1": lt["t1"]}
        # cuts land slightly before the anchor word (reads as "on the word")
        idx = 0
        starts = []
        for k, sh in enumerate(ln.get("shots", [])):
            if k == 0 and "at" not in sh:
                ts = lt["t0"] - (0.0 if li == 0 else ln.get("cut_lead", 0.06))
            else:
                ts, idx = resolve_time(sh.get("at"), lw, line, idx)
                ts -= 0.04
            starts.append(ts)
        for k, sh in enumerate(ln.get("shots", [])):
            te = starts[k + 1] if k + 1 < len(starts) else lt_next - (0.06 if li + 1 < len(lines) else -0.0)
            if li == 0 and k == 0:
                starts[k] = 0.0
            shots.append({**sh, "t0": round(max(0, starts[k]), 3), "t1": round(te, 3), "line": ln["id"]})

        if "heading" in ln:
            h = ln["heading"]
            t_until, _ = resolve_time(h.get("until"), lw, line, 0, edge="e")
            hd = max(h.get("min", 1.6), t_until - lt["t0"] + 0.35)
            overlays.append({"type": "heading", "t0": lt["t0"] - 0.05, "dur": hd,
                             "params": {"n": h["n"], "text": h["text"], "icon_name": h.get("icon")}})
            overlays.append({"type": "flash", "t0": lt["t0"] - 0.05, "dur": 0.12, "params": {}})
            hidden.append((lt["t0"] - 0.05, lt["t0"] - 0.05 + hd))
            sfx.append((lt["t0"] - 0.05, "impact", 0))
            if spec.get("counter", True):
                overlays.append({"type": "counter", "t0": lt["t0"], "dur": lt_next - lt["t0"] - 0.05,
                                 "params": {"n": h["n"], "total": spec.get("facts", 5)}})
        idx = 0
        for g in ln.get("gfx", []):
            g0, idx2 = resolve_time(g.get("at"), lw, line, g.get("_after", 0))
            if "until" in g:
                g1, _ = resolve_time(g["until"], lw, line, idx2, edge="e")
            else:
                g1 = g0 + g.get("dur", 2.0)
            g0 += g.get("delay", 0)
            overlays.append({"type": g["type"], "t0": round(g0 - 0.05, 3), "dur": round(g1 - g0 + 0.05 + g.get("hold", 0.15), 3),
                             "params": g.get("params", {})})
            if g.get("hide_captions"):
                hidden.append((g0 - 0.05, g1 + g.get("hold", 0.15)))
            if g.get("sfx"):
                sfx.append((g0 - 0.03, g["sfx"], g.get("sfx_db", 0)))
        for s in ln.get("sfx", []):
            ts, _ = resolve_time(s.get("at"), lw, line, 0)
            sfx.append((ts + s.get("offset", 0), s["name"], s.get("db", 0)))
    # subtle whoosh on hard cuts that start a new line without a heading impact
    for sh in shots:
        if sh.get("sfx"):
            sfx.append((sh["t0"] - 0.05, sh["sfx"], sh.get("sfx_db", -3)))

    # caption chunks (per line so chunks never span lines)
    chunks = []
    for ln in lines:
        lw = [w for w in words if w["line"] == ln["id"]]
        cs = captions.chunk_words(lw, max_words=spec.get("caption_words", 5))
        for c in cs:
            c["y"] = ln.get("caption_y")
            c["words"] = [{k: w[k] for k in ("text", "color", "s", "e")} for w in c["words"]]
        chunks += cs

    for sh in shots:
        c = clips[sh["clip"]]
        src = next(s for s in c["shots"] if s["id"] == sh["shot"])
        need = sh["t1"] - sh["t0"]
        span = src["end"] - src["start"] - 0.1
        if "speed" not in sh and need > span:
            sh["speed"] = round(max(0.5, span / need), 3)   # gentle slow-mo instead of a frozen frame
        speed = sh.get("speed", 1.0)
        if "src_in" in sh:
            sin = sh["src_in"]
        else:
            sin = src["start"] + 0.05 + max(0.0, (span - need * speed) * sh.get("pos", 0.5))
        sh["src"] = c["path"]; sh["src_in"] = round(sin, 3)
        sh["active"] = c.get("active_area", [0, 0, c["width"], c["height"]])
        sh["game"] = c.get("game")
        if need * speed > span + 0.05:
            sh["warn"] = f"source shot {src['len']:.2f}s shorter than needed {need * speed:.2f}s -> last frame held"

    tl = {"duration": round(total, 3), "words": words, "chunks": chunks, "shots": shots, "overlays": overlays,
          "sfx": sorted(sfx), "hidden": hidden, "lines": line_times}
    (bdir / "timeline.json").write_text(json.dumps(tl, indent=1))
    (bdir / "narration.f32").write_bytes(narration.tobytes())
    return tl, narration


# ======================================================================== footage
_face = None


def auto_cx(path, t, active):
    """Choose horizontal crop centre: faces first, then edge energy."""
    global _face
    x, y, w, h = active
    cap = cv2.VideoCapture(str(path)); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, fr = cap.read(); cap.release()
    if not ok:
        return 0.5
    fr = fr[y:y + h, x:x + w]
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    if _face is None:
        _face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = _face.detectMultiScale(g, 1.1, 5, minSize=(h // 12, h // 12))
    if len(faces):
        fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        return (fx + fw / 2) / w
    e = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0)) + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1))
    col = e.mean(axis=0)
    win = int(h * 9 / 16)
    cs = np.convolve(col, np.ones(win), "valid")
    best = int(np.argmax(cs * (1 - 0.35 * np.abs(np.linspace(-1, 1, len(cs))))))  # bias toward centre
    return (best + win / 2) / w


class ShotReader:
    def __init__(self, sh, W, H, fps):
        self.W, self.H = W, H
        x, y, aw, ah = sh["active"]
        fit = sh.get("fit", "fill")
        cx = sh.get("cx", "auto")
        if cx == "auto":
            cx = auto_cx(sh["src"], sh["src_in"] + 0.3, sh["active"])
            sh["cx_resolved"] = round(float(cx), 3)
        n = int(round((sh["t1"] - sh["t0"]) * fps)) + 2
        speed = sh.get("speed", 1.0)
        post = []
        if speed != 1.0:
            post.append(f"setpts=PTS/{speed}")
        if sh.get("fx") == "blur":
            post += ["gblur=sigma=14", "eq=brightness=-0.18:saturation=0.85"]
        elif sh.get("fx") == "dim":
            post += ["eq=brightness=-0.12"]
        post += [f"fps={fps}", f"tpad=stop_mode=clone:stop={n}"]
        if fit == "fill":
            ch = ah
            cw = int(round(ch * W / H)) // 2 * 2
            cx_px = int(clamp(cx * aw - cw / 2, 0, aw - cw)) + x
            filt = ",".join([f"crop={cw}:{ch}:{cx_px}:{y}", f"scale={W}:{H}:flags=lanczos", "unsharp=5:5:0.5"] + post)
        else:  # 16:9 letterboxed over a blurred copy of itself
            filt = (f"[0:v]crop={aw}:{ah}:{x}:{y},split[a][b];"
                    f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=30,eq=brightness=-0.3[bg];"
                    f"[b]scale={W}:-2:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2," + ",".join(post))
        cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{sh['src_in']:.3f}", "-i", sh["src"], "-an",
               "-filter_complex", filt, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.size = W * H * 3
        self.last = None

    def read(self):
        b = self.p.stdout.read(self.size)
        if len(b) == self.size:
            self.last = np.frombuffer(b, np.uint8).reshape(self.H, self.W, 3).copy()
        elif self.last is None:
            self.last = np.zeros((self.H, self.W, 3), np.uint8)
        return self.last.copy()

    def close(self):
        self.p.stdout.close(); self.p.wait()


def apply_zoom(fr, z, ox=0.0, oy=0.0):
    if abs(z - 1) < 1e-3:
        return fr
    H, W = fr.shape[:2]
    cw, ch = W / z, H / z
    x0 = clamp((W - cw) / 2 + ox * W, 0, W - cw); y0 = clamp((H - ch) / 2 + oy * H, 0, H - ch)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR)


# ======================================================================== render
def render(proj, spec, tl, narration, draft=False, t_start=0.0, t_end=None, out=None, stills=0):
    W, H = (540, 960) if draft else (spec.get("width", 1080), spec.get("height", 1920))
    fps = 30 if draft else spec.get("fps", 60)
    S = W / 1080
    t_end = min(t_end or tl["duration"], tl["duration"])
    nfr = int(round((t_end - t_start) * fps))
    out = Path(out or proj / ("previews" if draft else "renders") / ("draft.mp4" if draft else "final_video.mp4"))
    out.parent.mkdir(parents=True, exist_ok=True)

    # ---- audio
    music = audio.music_bed(tl["duration"] + 1, bpm=spec.get("music", {}).get("bpm", 140)) if spec.get("music", {"on": True}).get("on", True) else None
    mixed = audio.mix(tl["duration"], narration, tl["sfx"], music, music_db=spec.get("music", {}).get("db", -21))
    wav = proj / "build" / "mix.wav"
    audio.write_wav(wav, mixed)

    vtmp = out.with_suffix(".video.mp4")
    enc = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
           *(["-preset", "veryfast", "-crf", "23"] if draft else ["-preset", "slow", "-crf", str(spec.get("crf", 17))]),
           "-movflags", "+faststart", str(vtmp)]
    ep = subprocess.Popen(enc, stdin=subprocess.PIPE)
    shots = [s for s in tl["shots"] if s["t1"] > t_start and s["t0"] < t_end]
    reader, cur = None, None
    still_times = set(int(x) for x in np.linspace(0, nfr - 1, stills)) if stills else set()
    stills_out = []
    t0w = time.time()
    for f in range(nfr):
        t = t_start + f / fps
        sh = next((s for s in shots if s["t0"] <= t < s["t1"]), shots[-1])
        if sh is not cur:
            if reader:
                reader.close()
            sub = dict(sh)
            if t > sh["t0"]:  # starting mid-shot (partial render)
                sub["src_in"] = sh["src_in"] + (t - sh["t0"]) * sh.get("speed", 1.0)
                sub["t0"] = t
            reader, cur = ShotReader(sub, W, H, fps), sh
            sh["cx_resolved"] = sub.get("cx_resolved", sh.get("cx"))
        fr = reader.read()
        # camera: push-in across the shot + punch-in at cut
        ls = t - sh["t0"]; L = sh["t1"] - sh["t0"]
        z0, z1 = sh.get("zoom", [1.0, 1.06])
        z = z0 + (z1 - z0) * ease_in_out(ls / max(L, 0.01))
        if sh.get("punch"):
            z *= 1 + 0.10 * math.exp(-ls / 0.09)
        fr = apply_zoom(fr, z, *sh.get("offset", (0, 0)))
        for ov in tl["overlays"]:
            lt = t - ov["t0"]
            if 0 <= lt <= ov["dur"]:
                gfx.REGISTRY[ov["type"]](fr, lt, ov["dur"], S, W, H, **ov["params"])
        captions.render(fr, tl["chunks"], t, S, W, H, hidden=tl["hidden"])
        if sh.get("label_game"):
            gfx.label(fr, ls, L, S, W, H, text=sh["label_game"], x=0.5, y=0.93, size=34, color="w")
        ep.stdin.write(fr.tobytes())
        if f in still_times:
            p = proj / "previews" / "stills" / f"s_{t:06.2f}.jpg"; p.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(p), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR)); stills_out.append(p)
        if f % (fps * 5) == 0:
            print(f"  frame {f}/{nfr}  t={t:.1f}s  {f / max(1e-3, time.time() - t0w):.1f} fps", flush=True)
    reader.close(); ep.stdin.close(); ep.wait()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(vtmp), "-ss", f"{t_start:.3f}", "-t", f"{t_end - t_start:.3f}", "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ac", "2",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    vtmp.unlink()
    (proj / "build" / "timeline.json").write_text(json.dumps(tl, indent=1))
    print(f"[render] {out}  ({W}x{H} {fps}fps, {t_end - t_start:.1f}s) in {time.time() - t0w:.0f}s")
    return out, stills_out


def contact_sheet(paths, out, cols=4):
    from PIL import Image, ImageDraw
    ims = [Image.open(p) for p in paths]
    tw = 270; th = int(tw * ims[0].height / ims[0].width)
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * th), (10, 10, 10))
    d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(zip(paths, ims)):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), Path(p).stem[2:] + "s", font=style.font(22, False), fill=(255, 230, 0), stroke_width=3, stroke_fill=(0, 0, 0))
    sheet.save(out, quality=88)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--out")
    ap.add_argument("--stills", type=int, default=0)
    ap.add_argument("--revoice", action="store_true")
    ap.add_argument("--timeline-only", action="store_true")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    spec = json.loads((proj / "edit.json").read_text())
    if "voice" not in spec:  # channel defaults: free Kokoro for drafts, ElevenLabs narrator for finals
        ch = json.loads((ROOT / "config" / "channel.json").read_text())
        spec["voice"] = ch["voice_draft"] if a.draft else ch["voice_final"]
    tl, narration = build_timeline(proj, spec, a.revoice)
    print(f"[timeline] {tl['duration']:.2f}s, {len(tl['shots'])} shots, {len(tl['chunks'])} caption chunks, "
          f"{len(tl['overlays'])} overlays, {len(tl['sfx'])} sfx")
    for s in tl["shots"]:
        if s.get("warn"):
            print(f"  ! {s['line']} {s['clip']}#{s['shot']}: {s['warn']}")
    if a.timeline_only:
        return
    out, st = render(proj, spec, tl, narration, a.draft, a.start, a.end, a.out, a.stills)
    if st:
        for k in range(0, len(st), 16):
            contact_sheet(st[k:k + 16], proj / "previews" / f"contact_{k // 16 + 1:02d}.jpg")


if __name__ == "__main__":
    main()
