# Gaming Shorts Producer: project notes for Claude

- Before writing any script, storyboard or `edit.json`: read `knowledge/style_playbook.md`; take facts only from `knowledge/facts.md`
  (add new ones there with an official link first); pick topics from `knowledge/idea_bank.md`; log uploads in `analytics/scoreboard.csv`.
- When the user sends videos to learn from: follow the study workflow in `knowledge/README.md`
  (analyze_reference.py + the `/watch` skill), write a note per video, and update the playbook.
- Pipeline: `python3 -m tools.shorts.build projects/<slug> [--draft]`; footage index: `tools/index_footage.py`.
- Voice: channel defaults live in `config/channel.json`. Omit `voice` in edit.json and drafts use Kokoro (free), finals use
  the ElevenLabs "Channel Narrator (design_3)" voice. The key is injected by the proxy. Starter plan: max output mp3_44100_128.
- Facts: every claim gets a source; label confirmed / reported / rumour. Never present speculation as confirmed,
  never pass GTA V footage off as GTA VI, never generate fake gameplay. Other creators' videos are style references only.
- The user writes in Turkish; reply in Turkish. Video narration and on-screen text are English (US audience).
