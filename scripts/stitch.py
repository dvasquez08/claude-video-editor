#!/usr/bin/env python3
"""Join finished clips into one video with soft crossfades.

Usage:
    python scripts/stitch.py output/stitched/my-video.mp4 output/01-intro-final.mp4 output/02-tutorial-final.mp4 ...

All clips are normalized to the FIRST clip's resolution and fps (scaled to fit, padded with
the brand background colour if the aspect ratio differs). Clips without audio get silence.
Transition length comes from brand/brand.json -> stitch.transitionSec (0 = hard cut).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
         "-of", "json", path], capture_output=True, text=True, check=True)
    d = json.loads(out.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = v["r_frame_rate"].split("/")
    return {"duration": float(d["format"]["duration"]), "w": v["width"], "h": v["height"],
            "fps": round(float(num) / float(den), 3),
            "audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out, clips = sys.argv[1], sys.argv[2:]
    brand = json.loads((ROOT / "brand" / "brand.json").read_text())
    t = float(brand.get("stitch", {}).get("transitionSec", 0.3))
    pad_color = brand["colors"]["background"].lstrip("#")
    info = [probe(c) for c in clips]
    W, H, FPS = info[0]["w"], info[0]["h"], info[0]["fps"]
    if len(clips) > 1:
        t = min(t, *(i["duration"] / 2 for i in info))

    inputs, f = [], []
    for k, (c, i) in enumerate(zip(clips, info)):
        inputs += ["-i", c]
        f.append(f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x{pad_color},setsar=1,fps={FPS},"
                 f"format=yuv420p,settb=AVTB[v{k}]")
        if i["audio"]:
            f.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{k}]")
        else:
            f.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={i['duration']}[a{k}]")

    if len(clips) == 1:
        vlast, alast = "[v0]", "[a0]"
    elif t <= 0:
        f.append("".join(f"[v{k}][a{k}]" for k in range(len(clips)))
                 + f"concat=n={len(clips)}:v=1:a=1[vout][aout]")
        vlast, alast = "[vout]", "[aout]"
    else:
        vprev, aprev, offset = "[v0]", "[a0]", 0.0
        for k in range(1, len(clips)):
            offset += info[k - 1]["duration"] - t
            vo, ao = f"[vx{k}]", f"[ax{k}]"
            f.append(f"{vprev}[v{k}]xfade=transition=fade:duration={t}:offset={offset:.3f}{vo}")
            f.append(f"{aprev}[a{k}]acrossfade=d={t}{ao}")
            vprev, aprev = vo, ao
        vlast, alast = vprev, aprev

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(f),
           "-map", vlast, "-map", alast, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    total = probe(out)["duration"]
    print(f"{len(clips)} clips → {out} ({total:.1f}s, {W}x{H}@{FPS}, {t:.2f}s transitions)")


if __name__ == "__main__":
    main()
