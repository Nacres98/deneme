#!/usr/bin/env python3
"""Clean a voice recording and create an ElevenLabs Instant Voice Clone from it.

    python3 -m tools.shorts.clone_voice voice/raw/my_recording.m4a --name "Nacres Narrator" [--prep-only]

Steps: high-pass + gentle denoise + loudness normalise -> trim long silences -> 44.1 kHz mono WAV
-> POST /v1/voices/add (ElevenLabs key is injected by the network proxy, never stored in the repo).
Prints the new voice_id; put it into a project's edit.json: {"engine": "elevenlabs", "voice_id": "..."}.
Only clone a voice you own or have explicit permission to clone.
"""
import argparse, json, subprocess
from pathlib import Path


def prep(src, out):
    af = ("highpass=f=80,afftdn=nf=-25,"
          "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.6:stop_threshold=-45dB,"
          "loudnorm=I=-18:TP=-2:LRA=9")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-af", af, "-ac", "1", "-ar", "44100", str(out)], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                             capture_output=True, text=True).stdout)
    return d


def clone(wav, name, description):
    r = subprocess.run(["curl", "-sS", "--fail-with-body", "-X", "POST", "https://api.elevenlabs.io/v1/voices/add",
                        "-F", f"name={name}", "-F", f"description={description}",
                        "-F", "remove_background_noise=true", "-F", f"files=@{wav};type=audio/wav"],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"clone failed: {r.stdout[:400]} {r.stderr[:200]}")
    return json.loads(r.stdout)["voice_id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--name", default="Channel Narrator")
    ap.add_argument("--description", default="Channel owner's own voice, energetic US gaming narration")
    ap.add_argument("--prep-only", action="store_true")
    a = ap.parse_args()
    src = Path(a.recording)
    out = src.with_name(src.stem + "_clean.wav")
    d = prep(src, out)
    print(f"[prep] {out} ({d:.1f}s of speech)")
    if d < 45:
        print("  ! under 45 s of speech - clone quality will suffer; 2-3 minutes recommended")
    if a.prep_only:
        return
    vid = clone(out, a.name, a.description)
    print(f"[clone] voice_id = {vid}")
    Path("voice/voices.json").write_text(json.dumps({a.name: vid}, indent=1))


if __name__ == "__main__":
    main()
