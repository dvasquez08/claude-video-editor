---
description: Render the final MP4 (preview segment first for long videos)
argument-hint: <slug> [preview|full]
---

Render `$ARGUMENTS`.

1. If the cut video is longer than 3 minutes and the user didn't say `full`, render a
   **15-second preview** first: choose a stretch with a lower third and a code card or
   keyword pop, render just that range to `output/<slug>-preview.mp4`, then stop and ask
   whether to render the full video.
2. Full render: use the HyperFrames render command (check `npx hyperframes --help`) at the
   plan's resolution and fps, writing to `output/<slug>-final.mp4`. Use the fastest quality
   preset the CLI offers unless the user asks for best quality.
3. Verify with `ffprobe`: duration matches `edit-plan.json` within 0.1s, an audio stream
   exists, and resolution is correct.
4. Grab 3 frames with
   `ffmpeg -ss <t> -i output/<slug>-final.mp4 -frames:v 1 work/<slug>/check-<t>.png`
   at overlay midpoints, look at them, and confirm the overlays rendered.
5. Report the output path, final duration, file size, and render time.
6. Remind the user of any clips in `input/` still without an `output/*-final.mp4`, and that
   `/stitch` joins them when all are done.
