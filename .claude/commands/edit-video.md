---
description: Edit one clip — transcribe, cut dead air, plan animations, compose in HyperFrames, render
argument-hint: <path to raw video> [full|light|cut-only] [notes, e.g. "lower third when I open VS Code"]
---

Edit one clip, following CLAUDE.md. Arguments: `$ARGUMENTS`

Parse them as: first the video path, then an optional mode (`full`, `light`, `cut-only`;
default `full`), then anything else as the user's notes for this clip.

1. Check setup first: `brand/brand.json` has no `TODO` values and `channel.name` isn't
   `"Your Name"` (if it is, suggest `/setup-brand` and stop), `.env` has `ELEVENLABS_API_KEY`,
   and `ffmpeg`, `ffprobe`, `node`, and `python3` are on PATH. If anything is missing, stop and
   tell the user exactly what to fix.
2. Work out `<slug>` from the filename and create `work/<slug>/`. Note whether this is the
   first and/or last numbered clip in `input/` (decides title card / end card in `full` mode).
3. Run the steps from `/transcribe` and `/cut`.
4. **If mode is `cut-only`:** re-encode with
   `ffmpeg -i work/<slug>/cut.mp4 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart output/<slug>-final.mp4`,
   report raw → final duration and seconds removed, and stop. No pause, no planning.
5. Otherwise run `/plan-edit` with the mode and notes.
6. **Pause.** Show the user the cut summary and the edit plan as a short table
   (time · type · text · color · reason), and ask: "Good to compose, or any changes?"
   Wait for their answer. (In `light` mode with very specific notes and ≤ 3 overlays, you may
   skip the pause and say so.)
7. After approval, run `/compose` and `/render`.
8. Report: final file path, raw → final duration, number of overlays, anything worth a look.
   If there are other clips in `input/` without a matching `output/*-final.mp4`, list them.
