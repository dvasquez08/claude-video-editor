#!/usr/bin/env python3
"""Find dead air and filler words from a word-level transcript.

Usage:
    python scripts/find_cuts.py work/<slug>/transcript.raw.json work/<slug>/cuts.json

Writes cuts.json:
{
  "keep":   [ {"start": 0.00, "end": 4.21}, ... ],      # segments of the RAW clip to keep
  "auto_removals": [ {"start":..,"end":..,"reason":"silence 1.8s"}, ... ],
  "manual_removals": [],                                  # Claude adds retakes/false starts here
  "summary": {...}
}
Settings come from brand/brand.json → "cut".
"""
import json
import re
import sys
from pathlib import Path

BRAND = Path(__file__).resolve().parent.parent / "brand" / "brand.json"


def norm(t: str) -> str:
    return re.sub(r"[^a-z']", "", t.lower())


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    tr = json.loads(Path(sys.argv[1]).read_text())
    cfg = json.loads(BRAND.read_text())["cut"]
    max_gap = cfg["maxSilenceSeconds"]
    pad = cfg["keepPadSeconds"]
    fillers = {norm(f) for f in cfg["fillerWords"]}
    duration = tr["duration"]
    words = tr["words"]
    if not words:
        sys.exit("Transcript has no words")

    keep, cur_start, prev = [], None, None
    pending_filler = None  # filler(s) seen since prev kept word
    filler_count = 0

    for w in words:
        if norm(w["text"]) in fillers:
            pending_filler = (pending_filler[0], w["end"]) if pending_filler else (w["start"], w["end"])
            filler_count += 1
            continue
        if prev is None:
            cur_start = max(0.0, w["start"] - pad)
        else:
            gap = w["start"] - prev["end"]
            if pending_filler:
                close = min(prev["end"] + pad, pending_filler[0])
                open_ = max(w["start"] - pad, pending_filler[1])
                if open_ > close:
                    keep.append({"start": cur_start, "end": close})
                    cur_start = open_
            elif gap > max_gap:
                keep.append({"start": cur_start, "end": prev["end"] + pad})
                cur_start = w["start"] - pad
        prev, pending_filler = w, None

    keep.append({"start": cur_start, "end": min(duration, prev["end"] + pad)})
    keep = [{"start": round(s["start"], 3), "end": round(s["end"], 3)} for s in keep if s["end"] - s["start"] > 0.05]

    removals, cursor = [], 0.0
    for seg in keep:
        if seg["start"] - cursor > 0.01:
            removals.append({"start": round(cursor, 3), "end": seg["start"],
                             "reason": f"gap/filler {seg['start'] - cursor:.2f}s"})
        cursor = seg["end"]
    if duration - cursor > 0.01:
        removals.append({"start": round(cursor, 3), "end": duration, "reason": "trailing silence"})

    kept = sum(s["end"] - s["start"] for s in keep)
    out = {
        "source": tr.get("source"),
        "raw_duration": duration,
        "keep": keep,
        "auto_removals": removals,
        "manual_removals": [],
        "summary": {
            "kept_seconds": round(kept, 2),
            "removed_seconds": round(duration - kept, 2),
            "segments": len(keep),
            "filler_words_removed": filler_count,
        },
    }
    Path(sys.argv[2]).write_text(json.dumps(out, indent=2))
    print(f"keep {kept:.1f}s / {duration:.1f}s in {len(keep)} segments, "
          f"{filler_count} fillers → {sys.argv[2]}")


if __name__ == "__main__":
    main()
