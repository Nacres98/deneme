"""Original, procedurally synthesised SFX + music bed (no third-party samples -> no licensing issues),
and the final mix. All signals are float32 mono/stereo at SR."""
import subprocess
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e.astype(np.float32)


def _lp(x, k):
    """one-pole lowpass with per-sample coefficient array or scalar"""
    y = np.empty_like(x)
    acc = 0.0
    k = np.broadcast_to(np.asarray(k, np.float32), x.shape)
    for i in range(len(x)):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    return y


def _lp_fast(x, alpha):
    from scipy.signal import lfilter  # type: ignore
    return lfilter([alpha], [1, alpha - 1], x).astype(np.float32)


def lowpass(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    try:
        return _lp_fast(x, a)
    except ImportError:
        return _lp(x, a)


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


# ---------------------------------------------------------------- SFX
def whoosh(dur=0.45, up=True):
    n = int(dur * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n, dtype=np.float32)
    shape = np.sin(np.pi * t) ** 2 if up else np.exp(-4 * t)
    # crude sweeping band: mix of two lowpasses
    lo = lowpass(noise, 600); hi = lowpass(noise, 4000) - lowpass(noise, 1200)
    sweep = t if up else 1 - t
    x = (lo * (1 - sweep) + hi * sweep * 1.4) * shape
    return 0.6 * x / (np.abs(x).max() + 1e-9)


def impact(dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 48 + 90 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.0)
    click = lowpass(rng.standard_normal(n).astype(np.float32), 2500) * np.exp(-t * 40)
    x = sub * 0.9 + click * 0.5
    return (0.9 * x / np.abs(x).max()).astype(np.float32)


def pop(freq=900, dur=0.09):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    return (0.45 * x).astype(np.float32)


def tick(dur=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = highpass(rng.standard_normal(n).astype(np.float32), 3000) * np.exp(-t * 160)
    return (0.5 * x / np.abs(x).max()).astype(np.float32)


def riser(dur=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 200 + 900 * (t / dur) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    nz = highpass(rng.standard_normal(n).astype(np.float32), 2000)
    x = (tone * 0.25 + nz * 0.25) * (t / dur) ** 2
    return x.astype(np.float32)


def notify():
    a = pop(1320, 0.12); b = pop(1760, 0.16)
    out = np.zeros(int(0.3 * SR), np.float32)
    out[:len(a)] += a; out[int(0.09 * SR):int(0.09 * SR) + len(b)] += b
    return out


SFX = {"whoosh": whoosh, "whoosh_down": lambda: whoosh(0.5, up=False), "impact": impact,
       "pop": pop, "pop_hi": lambda: pop(1300), "tick": tick, "riser": riser, "notify": notify}


# ---------------------------------------------------------------- music bed
def music_bed(duration, bpm=140, seed=3):
    """Dark trap-style bed: 808 kick/bass, clap, hats, minor pad. Original synthesis."""
    r = np.random.default_rng(seed)
    n = int(duration * SR)
    out = np.zeros(n, np.float32)
    beat = 60 / bpm
    step = beat / 4
    roots = [55.0, 43.65, 49.0, 41.2]  # A1, F1, G1, E1  (Am - F - G - Em feel)
    chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [164.8, 196, 246.9]]

    def add(sig, at):
        i = int(at * SR)
        if i >= n:
            return
        j = min(n, i + len(sig))
        out[i:j] += sig[:j - i]

    kick_pat = [0, 6, 10]          # in 16ths per bar
    bars = int(duration / (beat * 4)) + 1
    for b in range(bars):
        t0 = b * beat * 4
        root = roots[(b // 2) % 4]
        for k in kick_pat:
            L = int(0.55 * SR); tt = np.arange(L) / SR
            f = root * 2 + root * 3 * np.exp(-tt * 30)
            add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2) * 0.55).astype(np.float32), t0 + k * step)
        for c in (4, 12):  # clap on 2 and 4
            L = int(0.18 * SR); tt = np.arange(L) / SR
            nz = highpass(r.standard_normal(L).astype(np.float32), 1200) * np.exp(-tt * 28)
            add(0.22 * nz, t0 + c * step)
        for h in range(16):  # hats with occasional rolls
            L = int(0.04 * SR); tt = np.arange(L) / SR
            nz = highpass(r.standard_normal(L).astype(np.float32), 7000) * np.exp(-tt * 120)
            vel = 0.07 if h % 2 else 0.1
            add(vel * nz, t0 + h * step)
            if h in (14,) and b % 2:
                add(0.06 * nz, t0 + (h + 0.5) * step)
        # pad: detuned saws through lowpass, 1 chord per 2 bars
        if b % 2 == 0:
            L = int(beat * 8 * SR); tt = np.arange(L) / SR
            sig = np.zeros(L, np.float32)
            for f in chords[(b // 2) % 4]:
                for det in (0.997, 1.003):
                    ph = (tt * f * det) % 1.0
                    sig += (2 * ph - 1).astype(np.float32)
            sig = lowpass(sig, 900) * np.minimum(1, tt / 0.6) * np.minimum(1, (tt[-1] - tt) / 0.4)
            add((0.035 * sig).astype(np.float32), t0)
    return out / (np.abs(out).max() + 1e-9) * 0.8


# ---------------------------------------------------------------- mix
def load_wav(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def db(x):
    return 10 ** (x / 20)


def mix(duration, voice, sfx_events, music=None, music_db=-21, sfx_db=-9, duck_db=-5):
    """voice: float array; sfx_events: [(time, name, gain_db)]; returns float32 mono."""
    n = int(duration * SR)
    out = np.zeros(n, np.float32)
    v = voice[:n]
    out[:len(v)] += v / (np.abs(v).max() + 1e-9) * 0.85
    if music is not None:
        m = np.resize(music, n) * db(music_db)
        # duck music under narration (smoothed voice envelope)
        envv = np.zeros(n, np.float32)
        envv[:len(v)] = np.abs(v)
        envv = lowpass(envv, 4)
        envv = envv / (envv.max() + 1e-9)
        m *= 1 - (1 - db(duck_db)) * np.clip(envv * 4, 0, 1)
        fade = int(0.8 * SR)
        m[-fade:] *= np.linspace(1, 0, fade)
        out += m
    cache = {}
    for t, name, g in sfx_events:
        if name not in cache:
            cache[name] = SFX[name]()
        s = cache[name] * db(sfx_db + g)
        i = int(t * SR)
        if 0 <= i < n:
            j = min(n, i + len(s))
            out[i:j] += s[:j - i]
    return out


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), str(path)], input=x.astype(np.float32).tobytes(), check=True)
