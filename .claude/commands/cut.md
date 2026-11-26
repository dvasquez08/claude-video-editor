---
description: Remove dead air, filler words, and retakes from the raw clip
argument-hint: <slug or path to raw video>
---

Tighten the video for `$ARGUMENTS` (resolve to `<slug>` and the raw file in `input/`).
Requires `work/<slug>/transcript.raw.json` — run `/transcribe` first if it's missing.

1. Run: `python3 scripts/find_cuts.py work/<slug>/transcript.raw.json work/<slug>/cuts.json`
2. Read the transcript and look for **false starts and retakes** — places where the creator restarts
   or repeats the same sentence. For each, add to `manual_removals` in `cuts.json`:
   `{"start": <raw seconds>, "end": <raw seconds>, "reason": "retake: '<first few words>'"}`
   Keep the last complete take. Use word timestamps from the raw transcript. Be conservative —
   if unsure, leave it in and mention it in your report.
3. Run: `python3 scripts/apply_cuts.py <raw video> work/<slug>/cuts.json work/<slug>/transcript.raw.json work/<slug>`
4. Report: raw → cut duration, seconds removed, number of retakes removed (with timestamps on
   the cut timeline so the user can check them in `work/<slug>/cut.mp4`).
