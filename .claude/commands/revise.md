---
description: Change something in an existing edit and re-render
argument-hint: <slug> <what to change, e.g. "remove the keyword pop at 1:12, make lower thirds bigger">
---

Revise the edit for `$ARGUMENTS`.

1. Decide what kind of change it is:
   - **Plan change** (add/remove/retime an overlay, change text): edit `work/<slug>/edit-plan.json`,
     re-run `scripts/check_plan.py`, then update only the affected overlays in the composition.
   - **Style change** ("bigger", "different color", "slower"): edit the overlay type's component,
     not individual instances. If it should apply to every future video, also update
     `brand/brand.json` and say so.
   - **Cut change** ("put back the bit at 2:10", "cut the tangent at 4:00"): edit `manual_removals`
     in `cuts.json`, re-run `apply_cuts.py`, then shift every overlay timestamp after the change by
     the duration difference. Check the plan again.
2. Render a short preview around the changed area first, then the full video if the user approves.
3. Report what changed in one or two lines.
