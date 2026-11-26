#!/usr/bin/env python3
"""Apply cuts.json to the raw video and remap the transcript to the cut timeline.

Usage:
    python scripts/apply_cuts.py <raw video> work/<slug>/cuts.json \
        work/<slug>/transcript.raw.json work/<slug>

Produces:
    work/<slug>/cut.mp4                 the tightened video
    work/<slug>/transcript.cut.json     words with timestamps on the cut timeline
    work/<slug>/timemap.json            raw→cut segment map (for debugging)

manual_removals in cuts.json are subtracted from the keep segments first.
"""
import json
import subprocess
import sys
from pathlib import Path

FADE = 0.012  # tiny audio fade at every edit to avoid clicks


def subtract(keep, removals):
    out = []
    for seg in keep:
        pieces = [(seg["start"], seg["end"])]
        for r in removals:
            nxt = []
            for s, e in pieces:
                if r["end"] <= s or r["start"] >= e:
                    nxt.append((s, e))
                    continue
                if r["start"] > s:
                    nxt.append((s, r["start"]))
                if r["end"] < e:
                    nxt.append((r["end"], e))
            pieces = nxt
        out += [(round(s, 3), round(e, 3)) for s, e in pieces if e - s > 0.05]
    return out


def has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    video, cuts_p, tr_p, out_dir = sys.argv[1:]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cuts = json.loads(Path(cuts_p).read_text())
    tr = json.loads(Path(tr_p).read_text())
    segs = subtract(cuts["keep"], cuts.get("manual_removals", []))
    if not segs:
        sys.exit("Nothing left to keep")
    audio = has_audio(video)

    lines, labels = [], []
    for i, (s, e) in enumerate(segs):
        d = e - s
        lines.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        labels.append(f"[v{i}]")
        if audio:
            lines.append(
                f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
                f"afade=t=in:st=0:d={FADE},afade=t=out:st={max(0, d - FADE):.3f}:d={FADE}[a{i}]")
            labels.append(f"[a{i}]")
    lines.append(f"{''.join(labels)}concat=n={len(segs)}:v=1:a={1 if audio else 0}"
                 + ("[outv][outa]" if audio else "[outv]"))
    script = out_dir / "cut_filter.txt"
    script.write_text(";\n".join(lines))

    out_mp4 = out_dir / "cut.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", video,
           "-filter_complex_script", str(script), "-map", "[outv]"]
    if audio:
        cmd += ["-map", "[outa]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_mp4)]
    subprocess.run(cmd, check=True)

    # Remap transcript to the cut timeline
    timemap, offset = [], 0.0
    for s, e in segs:
        timemap.append({"raw_start": s, "raw_end": e, "cut_start": round(offset, 3)})
        offset += e - s

    def remap(item):
        mid = (item["start"] + item["end"]) / 2
        for m in timemap:
            if m["raw_start"] <= mid <= m["raw_end"]:
                f = lambda t: round(m["cut_start"] + min(max(t, m["raw_start"]), m["raw_end"]) - m["raw_start"], 3)
                return {"text": item["text"], "start": f(item["start"]), "end": f(item["end"])}
        return None

    words = [w for w in (remap(x) for x in tr["words"]) if w]
    events = [w for w in (remap(x) for x in tr.get("events", [])) if w]
    cut_tr = {"source": str(out_mp4), "duration": round(offset, 3),
              "text": " ".join(w["text"] for w in words), "words": words, "events": events}
    (out_dir / "transcript.cut.json").write_text(json.dumps(cut_tr, indent=2))
    (out_dir / "timemap.json").write_text(json.dumps(timemap, indent=2))
    raw = tr["duration"]
    print(f"{raw:.1f}s → {offset:.1f}s (removed {raw - offset:.1f}s, {len(segs)} segments) → {out_mp4}")


if __name__ == "__main__":
    main()
