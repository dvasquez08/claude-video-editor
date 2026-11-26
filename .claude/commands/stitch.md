---
description: Join all finished clips into one video, in filename order
argument-hint: [output name, e.g. claude-edits-my-videos]
---

Stitch the finished clips into one video. Name: `$ARGUMENTS` (default: `final-video`).

1. List `output/*-final.mp4` in filename order and compare against `input/`. If any input clip
   has no finished version, tell the user which ones and ask whether to stitch anyway.
2. Show the user the order (filename · duration · mode from its `edit-plan.json`, or `cut-only`)
   and confirm before running if anything looks off (e.g. numbering gaps).
3. Run: `python3 scripts/stitch.py output/stitched/<name>.mp4 <clip1> <clip2> ...`
   It normalizes every clip to the first clip's resolution and fps (letterboxing if the
   aspect ratio differs), and crossfades by `stitch.transitionSec` from `brand.json`.
4. Check with `ffprobe` that it has video and audio and the expected length (sum of clips
   minus one transition per join).
5. Report the output path, total duration, and file size.
