# Claude Video Editor

**A Claude Code agent that edits your talking-head and tutorial videos.** Drop in a raw recording
and it cuts the dead air, "ums", and retakes, then adds subtle, modern motion graphics in your
brand colors with [HyperFrames](https://github.com/heygen-com/hyperframes), and renders a
finished MP4.

You stay in control: the agent shows you its animation plan and waits for your OK before
anything renders.

<!-- Add a before/after GIF or your YouTube tutorial link here -->

## What it does

- **Cuts the boring parts.** Removes silences, filler words (um, uh…), and false starts. When you
  flub a line, just pause and say it again; it keeps your last take.
- **Adds animations that match what you say**, timed to the exact word:
  - subtle keyword highlights (not captions)
  - full-screen title and section slides
  - lower thirds for tools and names
  - code cards for commands
  - zoom-ins for emphasis
- **Animates your call to action.** When you say "like and subscribe", a glassy button animates
  being clicked. Every video ends with a subscribe end card.
- **Colors with meaning:** your brand color by default, red for subscribe, green for money and
  results, amber for warnings.
- **Handles multi-shot videos.** Edit face-cam clips fully, give screen tutorials a light touch,
  then stitch everything together with soft crossfades.

## How it works

```
your clip ─▶ transcribe ─▶ cut dead air ─▶ plan animations ─▶ you approve ─▶ HyperFrames ─▶ MP4
             (ElevenLabs)   (FFmpeg)        (Claude)                         (render)
```

The transcript is internal. It's how Claude knows *when* you say each word, so it can cut fillers
and land each animation on the right word. It never appears in the video.

## Requirements

| Tool | Why | Check |
|---|---|---|
| [Claude Code](https://claude.com/claude-code) | Runs the agent | `claude --version` |
| Node.js 22+ | HyperFrames | `node -v` |
| FFmpeg (includes ffprobe) | Cutting, audio, stitching | `ffmpeg -version` |
| Python 3.10+ | Helper scripts | `python3 --version` |
| Google Chrome | HyperFrames renders through headless Chrome | — |
| [ElevenLabs](https://elevenlabs.io) API key | Speech-to-text with word timestamps | — |

**Windows:** `winget install Gyan.FFmpeg OpenJS.NodeJS Python.Python.3.12`
**macOS:** `brew install ffmpeg node python`

## Setup (one time)

```bash
git clone https://github.com/<your-username>/claude-video-editor.git
cd claude-video-editor
pip install -r requirements.txt
npx skills add heygen-com/hyperframes
cp .env.example .env        # then paste your ElevenLabs key into .env
claude
```

Then, inside Claude Code:

```
/setup-brand
```

It asks for your name, channel handle, and colors (hex codes, or your website), then measures
where your face sits from a sample clip so text never covers it.

### ElevenLabs API key

Create a key at **elevenlabs.io → Developers → API Keys** with the least access possible:

- **Restrict Key:** on
- **Speech to Text:** Access
- **Everything else:** No Access
- **Credit limit:** set a small cap so a leaked key can't drain your account

## Usage

Record each shot type as its own file, numbered in order, and put them in `input/`:

```
input/01-intro.mp4       ← face fills the frame
input/02-tutorial.mp4    ← screen recording, webcam in the corner
input/03-outro.mp4       ← face fills the frame
```

Edit each clip, then stitch:

```
/edit-video input/01-intro.mp4
/edit-video input/02-tutorial.mp4 light lower third when I open VS Code, code card for the npm command
/edit-video input/03-outro.mp4
/stitch my-video
```

Your finished video lands in `output/stitched/my-video.mp4`.

### Modes

| Mode | For | What you get |
|---|---|---|
| `full` (default) | Face-to-camera shots | Cuts + keywords, slides, lower thirds, zooms, CTA |
| `light` | Screen tutorials with a corner webcam | Cuts + only what you ask for in your notes |
| `cut-only` | Anything | Just dead air, fillers, and retakes removed |

Anything after the mode is a note to the editor ("title: How I automate my inbox",
"no zooms", "code card when I say npm install"). Notes always win.

### All commands

| Command | What it does |
|---|---|
| `/setup-brand` | One-time guided setup: name, colors, fonts, face position |
| `/edit-video <file> [mode] [notes]` | Full edit of one clip, with an approval step |
| `/stitch [name]` | Join all finished clips in filename order |
| `/revise <slug> <change>` | Tweak a finished edit ("drop the keyword at 1:12", "slower slides") |
| `/transcribe`, `/cut`, `/plan-edit`, `/compose`, `/render` | Run a single step again |

## Customizing

Everything visual lives in **`brand/brand.json`**:

- **`colors`:** background, accents, and `semantic` colors (red/green/amber/purple)
- **`fonts`:** any Google Font
- **`layout.faceSafeZones`:** where your face is in `full` shots, and your webcam bubble in `corner` shots
- **`motion`:** animation speed, how often overlays may appear, max % of the video with text on screen
- **`cut`:** how long a pause must be before it's cut, and which filler words to remove

The editing style itself (which animations exist and when to use them) is in **`CLAUDE.md`**.
Change it there to change how the agent edits.

## Recording tips

- **Face shots:** sit slightly off-centre and leave open space on one side. That's where text goes.
- **Flubbed a line?** Pause, then say the whole sentence again. Don't stop recording.
- **Say tool names and numbers clearly.** They become the highlighted keywords.
- **Short clips first:** test on 30–60 seconds before editing a 15-minute video.

## Project layout

```
.claude/commands/   slash commands (the agent's workflow)
CLAUDE.md           editing rules and style: the agent's brain
brand/brand.json    your colors, fonts, face position, animation limits
scripts/            transcribe, cut, validate plan, stitch
input/              your raw recordings (never modified)
work/               intermediate files per clip
output/             finished clips + output/stitched/
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `401` from ElevenLabs | Wrong key in `.env` |
| Permission error from ElevenLabs | Enable **Speech to Text** on the key |
| Model error from ElevenLabs | Set `ELEVENLABS_STT_MODEL` in `.env` to the current Scribe model |
| `channel.name is still 'Your Name'` | Run `/setup-brand` |
| Text covers your face | Re-run `/setup-brand` with a sample clip, or edit `layout.faceSafeZones` |
| Too many / too few animations | Adjust `motion.maxKineticPerMinute` and `minSecondsBetweenOverlays` in `brand.json` |

## Credits

- [HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen: HTML → video rendering
- [ElevenLabs Scribe](https://elevenlabs.io/speech-to-text): speech-to-text
- [FFmpeg](https://ffmpeg.org)

## License

MIT. See [LICENSE](LICENSE).
