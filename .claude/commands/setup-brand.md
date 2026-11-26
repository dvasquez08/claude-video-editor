---
description: One-time guided setup — your name, colors, fonts, and where your face sits in frame
argument-hint: [optional: a website URL, hex colors, or a sample clip path]
---

Walk the user through setting up `brand/brand.json`. Arguments (optional): `$ARGUMENTS`

Ask one short group of questions at a time, show what you'll write, then write it.
Keep every key in `brand.json` that you don't change.

1. **Name and handle.** Ask what name should appear on slides and the end card
   (`channel.name`) and, optionally, their channel handle like `@yourchannel` (`channel.handle`,
   or `null`). Ask for an end card headline (default "Subscribe for more").

2. **Colors.** Ask how they want to set colors:
   - **Hex codes:** take a main accent (→ `primary`) and optionally a second accent and a background.
   - **A website:** try to fetch it and read its CSS colors. If the site blocks fetching, ask them to
     paste a bit of the page's HTML/CSS (Tailwind class names like `bg-sky-950` work: map them to
     Tailwind's hex values).
   - **"Pick for me":** keep the defaults.
   Then derive anything they didn't give:
   - `background`: a very dark shade that works behind white text.
   - `surface`: one step lighter than `background`.
   - `secondary`: a neighbouring hue to `primary`.
   - `gradient`: `primary` → `secondary` at 135deg.
   - `text`: white.
   - `textMuted`: a light grey.
   Leave `colors.semantic` (red/green/amber/purple) alone unless they ask.
   Check contrast: white text on `background` and `primary` on `background` must both be readable
   (WCAG contrast ≥ 4.5:1 for white, ≥ 3:1 for primary). Adjust shades if not, and say so.

3. **Fonts.** Default is Inter for headings/body and JetBrains Mono for code. Offer to change them;
   only accept fonts available on Google Fonts.

4. **Face position.** Ask for a short sample recording of each shot type they use (full-face,
   and screen-recording-with-webcam if they do tutorials). For each one:
   - grab a frame from the middle with
     `ffmpeg -ss <mid> -i <clip> -frames:v 1 work/setup-<type>.png`,
   - look at it and estimate the face (or webcam bubble) box as % of frame, with a little padding,
   - write it to `layout.faceSafeZones.full` / `.corner`,
   - describe where you put it ("face centred, box x 30–70%, y 5–75%").
   If they have no sample yet, keep the defaults and tell them to re-run `/setup-brand` later.

5. **Write and confirm.** Write `brand/brand.json`, run `python3 -m json.tool brand/brand.json`
   to validate it, then show a short summary: name, handle, color swatches as hex, fonts, face
   zones. Offer to render a 3-second title-card preview with HyperFrames so they can see the look.
