---
description: Decide where animations go — writes edit-plan.json from the cut transcript
argument-hint: <slug> [full|light] [notes, e.g. "video title: Claude edits my videos"]
---

Create the edit plan for `$ARGUMENTS`.

Inputs: `work/<slug>/transcript.cut.json`, `brand/brand.json`, and the overlay vocabulary +
schema in CLAUDE.md. Get resolution and fps with
`ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of json work/<slug>/cut.mp4`.

0. Mode is `full` unless given. Write `"mode"` and the user's `"notes"` (verbatim) into the plan.
   **`light` mode:** skip step 2 below. Place only what the user's notes ask for, timed from the
   transcript. With no notes, add at most `motion.lightMaxPerMinute` small overlays per minute
   (`code_card`, `lower_third`, `kinetic_text`, `callout_list` only), positioned away from the
   corner webcam (`layout.faceSafeZones.corner`) and away from what's being demonstrated.
   Then go to step 3.
   **`full` mode:** the user's notes are extra requests on top of your own plan; honour them all.
1. Read the whole cut transcript first and outline the video's structure: intro, sections, outro.
2. Place overlays. **Less is more: this is NOT a captioned video.** Most of the runtime should
   have no text at all (see "The signature look" in CLAUDE.md).
   - `kinetic_text`: only for the key moments (core promise, a big number, an important tool
     name, a payoff). About one every 20–40 s. **1–3 words only**, the creator's exact words, with
     each word's `start` copied from the cut transcript into `props.words`.
   - `title_card` at 0s **only if this is the first clip** (or the only one). If the user didn't
     give a title, propose one from the content.
   - `section_divider` at real topic changes, plus at most 1–2 `slide` statement cards for the
     single biggest ideas. Both use the full-screen slide look (CLAUDE.md), and they're rare:
     they take over the whole frame.
   - `lower_third` on the first mention of a tool/product/person that matters. Only the first.
   - `code_card` when the creator says a command, file name, or env var — show it in the mono font.
   - `callout_list` when the creator enumerates things; items appear as each is said.
   - `stat_card` only for a big number that needs a label.
   - `punch_in` on 3–6 emphasis moments. These add energy without adding text.
   - `like_subscribe` whenever the creator asks viewers to like/subscribe (never `kinetic_text` for
     that). Copy the spoken timestamps of "like"/"subscribe"/"bell" into `props.steps`.
   - `end_card` over the last 4–6 seconds **only if this is the last clip** (or the only one).
   - For every overlay, set `props.color` by meaning (CLAUDE.md "Color" table): `red` for
     like/subscribe, `green` for money, `amber` for warnings, `purple` for AI-magic moments,
     otherwise `primary`. `primary` should stay the most common accent.
3. Time every overlay from word timestamps (start ≈ trigger word start − 0.15s).
   Keep titles ≤ 6 words and kinetic text ≤ 3 words.
4. Write `work/<slug>/edit-plan.json`, then run `python3 scripts/check_plan.py work/<slug>/edit-plan.json`.
   Fix every problem it reports (usually by dropping the weaker overlay, never by shrinking timing to sneak more in) and re-run until OK.
5. Show the user a compact table: `mm:ss | type | text | color | reason`, plus the % of runtime with text on screen.
