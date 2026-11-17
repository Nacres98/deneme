# Gaming Shorts Producer

A reusable pipeline for 1080×1920 / 60 fps gaming listicle Shorts (FFmpeg, Python, HTML Canvas, Playwright, faster-whisper).

## Status
- [x] `tools/analyze_reference.py`: reference-video analysis (cuts, pacing, contact sheets, caption band/colour, SFX transients, word transcript)
- [ ] Reference analysis: waiting for the reference MP4
- [ ] Topic, script, sources, storyboard: waiting for approval
- [ ] Footage indexer, voice + alignment, caption/graphics engine, timeline renderer

## Layout
```
assets/fonts/        Montserrat (SIL OFL 1.1)
reference/           put the reference MP4 here; analysis/ is generated
tools/               reusable pipeline scripts
projects/<slug>/     scripts, sources, footage, audio, graphics, previews, renders
```

## Analyze a reference
```
pip install faster-whisper opencv-python-headless numpy pillow
python3 tools/analyze_reference.py reference/ref.mp4
```
Transcription needs network access to huggingface.co for the Whisper model (use `--no-transcribe` without it).
