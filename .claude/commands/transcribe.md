---
description: Transcribe a raw clip with ElevenLabs (word-level timestamps)
argument-hint: <path to raw video>
---

Transcribe `$ARGUMENTS`.

1. Determine `<slug>` (filename without extension, lowercase, spaces → dashes); create `work/<slug>/`.
2. Run: `python3 scripts/transcribe.py "$ARGUMENTS" work/<slug>/transcript.raw.json`
3. If it fails with a 401, the API key in `.env` is wrong. If it's a 4xx about the model,
   set `ELEVENLABS_STT_MODEL` in `.env` to the current Scribe model name.
4. Report word count and duration. Don't paste the transcript.
