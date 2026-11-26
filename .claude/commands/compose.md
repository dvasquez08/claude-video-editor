---
description: Build the HyperFrames composition from edit-plan.json
argument-hint: <slug>
---

Build the HyperFrames composition for `$ARGUMENTS`.

If the plan's `mode` is `cut-only`, skip this command entirely (there's nothing to compose).

1. Invoke the `/hyperframes` skill first and follow its conventions for project structure,
   timing, animation, and assets. Don't guess HTML video conventions.
2. Run `python3 scripts/check_plan.py work/<slug>/edit-plan.json` — stop if it fails.
3. Create the HyperFrames project at `work/<slug>/composition/` (use `npx hyperframes init`
   if it helps; check `npx hyperframes --help` for current flags). Match the plan's
   width, height, fps, and duration exactly.
4. Layers, bottom to top:
   - `cut.mp4` as the full-frame base video **with its audio** (copy or reference it into the
     project as HyperFrames expects).
   - Each overlay from the plan, as its own reusable component per `type`, so restyling
     a type changes every instance.
5. Styling comes only from `brand/brand.json`:
   - Define colors as CSS custom properties from `colors`, and load `fonts` from Google Fonts.
   - Use `motion` eases and durations for every in/out animation.
   - Keep everything inside `layout.safeMarginPx`, and keep non-full overlays out of
     the face-safe zone for the plan's `mode`
     (`layout.faceSafeZones.full` or `.corner`).
   - For the look, aim for glassy dark panels (`surface` at ~80% opacity + backdrop blur),
     thin `primary` accent lines, a subtle glow, a quick slide + fade + slight blur-in, and
     mono font for anything code-like.
   - No logo. Branding is the `channel.name` wordmark in the heading font (bold, white).
   - **Polish bar:** every overlay should look like a modern product UI animation, not a
     basic text layer. Use masked reveals, blur-ins, layered easing, light sweeps on accent
     elements, and frosted glass where a backdrop is needed. Plain colored text alone is never
     enough for a CTA.
6. Build `kinetic_text` as a **subtle keyword highlight**, not a caption:
   - One element per word (1–3 words). Each word enters at its own `props.words[].start`;
     fall back to `motion.wordStaggerFallbackSec` only if a word has no timestamp.
   - Entrance: translateY 16px → 0, opacity 0 → 1, blur 4px → 0, `motion.inDurationSec`,
     `motion.easeIn`. Exit: quick fade over `motion.outDurationSec` at `end`.
   - Size: ~4–6% of frame height, weight 600–700. No giant stacked headlines.
   - Color: the emphasis word uses the overlay's `props.color` (resolved from `colors.primary`
     or `colors.semantic`), with a faint glow in that color (~25% opacity). Other words white.
     Numbers can count up while entering.
   - Optional: a thin 2px accent underline or small dot in the same color. No panels or
     big backgrounds behind kinetic text, just a soft dark text-shadow for legibility.
   - Position beside the face-safe zone on the chosen `side`, roughly at eye level; never
     inside the face-safe zone.
   - Every other overlay type also uses its `props.color` for accents (lines, glows, icons);
     the `end_card` subscribe button uses `red`.
6b. Build `title_card`, `section_divider`, and `slide` from **one shared full-screen slide
   component** (CLAUDE.md "Full-screen slides"): `background`, soft radial glow in the
   overlay's color, `channel.name` wordmark top-left, headline left-aligned and entering word by word
   with blur-in, accent underline drawing in, optional subtitle in the accent color. The base
   video's audio keeps playing underneath; fade in/out over ~0.3 s.
6c. Build `like_subscribe` and `end_card` exactly as specified in CLAUDE.md ("Like / subscribe
   CTA" and "End card"). Each CTA step is timed to its own spoken word. Draw icons as inline SVG.
7. `punch_in` scales the base video around the frame centre (or the face-safe-zone centre),
   using `motion.punchInScale`, easing in and out.
8. Open the HyperFrames preview and spot-check 4 overlays (two kinetic texts, a lower third,
   the end card) for overlap, timing, and legibility. Words must land exactly on the spoken word, and the
   kinetic text should feel understated. Fix anything off.
9. Report the composition path and how to preview it.
