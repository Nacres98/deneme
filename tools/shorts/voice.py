"""Narration: script markup parsing, TTS (Kokoro, local) or user recording, faster-whisper alignment.

Markup inside a line's text:
    *words*            -> green emphasis
    !words!            -> red emphasis
    [shown|spoken]     -> caption shows `shown`, TTS says `spoken` (e.g. [212 GB|two hundred twelve gigabytes])
    //                 -> force a caption break here
"""
import difflib, json, re, subprocess, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TTS_PY = ROOT / ".venv-tts" / "bin" / "python"
SR_W = 16000


def parse(text):
    """-> list of units {shown, spoken:[words], color, brk}"""
    units, color, brk = [], "w", False
    for m in re.finditer(r"\[([^|\]]+)\|([^\]]+)\]|//|[*!]|[^\s*!\[]+", text):
        tok = m.group(0)
        if tok == "//":
            brk = True; continue
        if tok in ("*", "!"):
            c = "g" if tok == "*" else "r"
            color = "w" if color == c else c
            continue
        if not m.group(1) and units and re.fullmatch(r"[.,?;:]+", tok):
            units[-1]["text"] += tok   # punctuation after an emphasis marker
            continue
        if m.group(1):
            shown, spoken = m.group(1), m.group(2).split()
        else:
            shown, spoken = tok, [tok]
        # trailing emphasis marker glued to punctuation, e.g. "*tonight*." handled by regex split
        units.append({"text": shown, "spoken": spoken, "color": color, "brk": brk})
        brk = False
    return units


def spoken_text(units):
    return " ".join(w for u in units for w in u["spoken"])


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


# ---------------------------------------------------------------- TTS
KOKORO_SNIPPET = r"""
import sys, json, numpy as np, soundfile as sf, warnings
warnings.filterwarnings('ignore')
from kokoro import KPipeline
job = json.load(open(sys.argv[1]))
p = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
for item in job['lines']:
    parts = [a for _, _, a in p(item['text'], voice=job['voice'], speed=job['speed'])]
    aud = np.concatenate(parts) if parts else np.zeros(2400, np.float32)
    sf.write(item['out'], aud, 24000)
    print(item['out'], round(len(aud) / 24000, 2), flush=True)
"""


def tts_kokoro(lines, voice, speed, outdir):
    """lines: [(id, text)] -> {id: wav_path}"""
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    job = {"voice": voice, "speed": speed, "lines": [{"text": t, "out": str(outdir / f"{i}.wav")} for i, t in lines]}
    jp = outdir / "job.json"; jp.write_text(json.dumps(job))
    sp = outdir / "_kokoro.py"; sp.write_text(KOKORO_SNIPPET)
    env = {"HF_HUB_DISABLE_XET": "1", "PATH": "/usr/bin:/bin:/usr/local/bin"}
    import os
    env = {**os.environ, **env}
    subprocess.run([str(TTS_PY), "-I", str(sp), str(jp)], check=True, env=env)
    return {i: outdir / f"{i}.wav" for i, _ in lines}


# ---------------------------------------------------------------- alignment
_model = None


def whisper_words(wav_path, prompt=None):
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel("small.en", device="cpu", compute_type="int8")
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(wav_path), "-ac", "1", "-ar", str(SR_W), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    segs, _ = _model.transcribe(np.frombuffer(raw, np.float32), word_timestamps=True, initial_prompt=prompt,
                                condition_on_previous_text=False)
    return [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]


def align_units(units, wwords, offset=0.0, line_dur=None):
    """Give each unit start/end times by matching its spoken words to whisper words."""
    sp = [(ui, norm(w)) for ui, u in enumerate(units) for w in u["spoken"]]
    a = [x for _, x in sp]
    b = [norm(w["w"]) for w in wwords]
    times = [None] * len(sp)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            ww = wwords[blk.b + k]
            times[blk.a + k] = (ww["s"], ww["e"])
    # fill gaps: whisper may merge/split numbers ("212" vs "two hundred twelve") -> interpolate
    known = [i for i, t in enumerate(times) if t]
    end_all = line_dur or (wwords[-1]["e"] if wwords else 1.0)
    for i in range(len(times)):
        if times[i]:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        t0 = times[prev][1] if prev is not None else 0.0
        t1 = times[nxt][0] if nxt is not None else end_all
        n_missing = (nxt if nxt is not None else len(times)) - (prev if prev is not None else -1) - 1
        pos = i - (prev if prev is not None else -1)
        step = (t1 - t0) / max(1, n_missing)
        times[i] = (t0 + step * (pos - 1), t0 + step * pos)
    out = []
    for ui, u in enumerate(units):
        ts = [times[k] for k, (uj, _) in enumerate(sp) if uj == ui]
        out.append({"text": u["text"], "color": u["color"], "brk": u["brk"],
                    "s": round(ts[0][0] + offset, 3), "e": round(ts[-1][1] + offset, 3)})
    return out
