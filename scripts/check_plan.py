#!/usr/bin/env python3
"""Validate edit-plan.json against brand.json rules before composing.

Usage:
    python scripts/check_plan.py work/<slug>/edit-plan.json

Exits non-zero with a list of problems if anything breaks the rules.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"kinetic_text", "title_card", "section_divider", "lower_third", "code_card",
         "callout_list", "stat_card", "punch_in", "end_card", "slide", "like_subscribe"}
REGIONS = {"full", "top-left", "top-right", "bottom-left", "bottom-right", "center", "bottom-center"}
EXEMPT_FROM_SPACING = {"punch_in"}  # zooms can sit under other overlays
LIGHT_TYPES = {"code_card", "lower_third", "kinetic_text", "callout_list", "like_subscribe"}


def todos(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not k.startswith("_"):
                yield from todos(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, str) and obj.startswith("TODO"):
        yield path


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    plan = json.loads(Path(sys.argv[1]).read_text())
    brand = json.loads((ROOT / "brand" / "brand.json").read_text())
    motion = brand["motion"]
    problems = [f"brand.json still has TODO: {p}" for p in todos(brand)]
    if brand.get("channel", {}).get("name", "Your Name") == "Your Name":
        problems.append("brand.json channel.name is still 'Your Name' — run /setup-brand first")

    dur = plan["duration"]
    mode = plan.get("mode", "full")
    if mode not in ("full", "light"):
        problems.append(f"mode '{mode}' can't have an edit plan (cut-only skips planning)")
    ovs = sorted(plan["overlays"], key=lambda o: o["start"])
    ids = set()
    for o in ovs:
        tag = o.get("id", "?")
        if tag in ids:
            problems.append(f"{tag}: duplicate id")
        ids.add(tag)
        if o["type"] not in TYPES:
            problems.append(f"{tag}: unknown type '{o['type']}'")
        if o.get("region", "full") not in REGIONS:
            problems.append(f"{tag}: unknown region '{o.get('region')}'")
        if not (0 <= o["start"] < o["end"] <= dur + 0.01):
            problems.append(f"{tag}: bad timing {o['start']}–{o['end']} (video is {dur}s)")
        if not o.get("reason"):
            problems.append(f"{tag}: missing reason")
        c = o.get("props", {}).get("color", "primary")
        if c != "primary" and c not in brand["colors"].get("semantic", {}):
            problems.append(f"{tag}: color '{c}' is not 'primary' or a key in colors.semantic")
        if o["type"] == "kinetic_text":
            texts = " ".join(w.get("text", "").lower() for w in o.get("props", {}).get("words", []))
            if "subscribe" in texts or texts.strip(" .,!") == "like":
                problems.append(f"{tag}: use like_subscribe for like/subscribe, not kinetic_text")
        if o["type"] == "like_subscribe":
            steps = o.get("props", {}).get("steps", [])
            if not steps or any(st.get("action") not in ("like", "subscribe", "bell") for st in steps):
                problems.append(f"{tag}: like_subscribe needs steps with action like/subscribe/bell")
            elif any(not (o["start"] - 0.01 <= st.get("start", -1) <= o["end"]) for st in steps):
                problems.append(f"{tag}: like_subscribe step times must be inside {o['start']}-{o['end']}")
        if o["type"] == "kinetic_text":
            p = o.get("props", {})
            ws = p.get("words", [])
            if not 1 <= len(ws) <= 3:
                problems.append(f"{tag}: kinetic_text is keywords only: 1-3 words (has {len(ws)})")
            if o["end"] - o["start"] > 3.0:
                problems.append(f"{tag}: kinetic_text on screen {o['end'] - o['start']:.1f}s (max 3s)")
            starts = [w.get("start", -1) for w in ws]
            if starts != sorted(starts) or any(not (o["start"] - 0.01 <= t <= o["end"]) for t in starts):
                problems.append(f"{tag}: word starts must be ascending and inside {o['start']}-{o['end']}")
            if p.get("emphasis") and p["emphasis"] not in [w.get("text") for w in ws]:
                problems.append(f"{tag}: emphasis '{p['emphasis']}' is not one of its words")
            if p.get("side") not in ("left", "right"):
                problems.append(f"{tag}: side must be 'left' or 'right'")

    spaced = [o for o in ovs if o["type"] not in EXEMPT_FROM_SPACING]
    gap = motion["minSecondsBetweenOverlays"]
    for a, b in zip(spaced, spaced[1:]):
        if b["start"] - a["start"] < gap and b["type"] != "end_card":
            problems.append(f"{b['id']}: starts {b['start'] - a['start']:.1f}s after {a['id']} (min {gap}s)")
    for i, a in enumerate(spaced):
        for b in spaced[i + 1:]:
            if b["start"] >= a["end"]:
                break
            if a.get("region") == b.get("region") or "full" in (a.get("region"), b.get("region")):
                problems.append(f"{a['id']} and {b['id']} overlap in region '{a.get('region')}'")

    per_min = len(spaced) / max(dur / 60, 1)
    if per_min > motion["maxOverlaysPerMinute"]:
        problems.append(f"{per_min:.1f} overlays/min exceeds max {motion['maxOverlaysPerMinute']}")

    slides = [o for o in ovs if o["type"] in ("slide", "section_divider")]
    if len(slides) > motion["maxSlidesPerVideo"]:
        problems.append(f"{len(slides)} full-screen slides exceeds max {motion['maxSlidesPerVideo']}")
    if sum(o["type"] == "slide" for o in ovs) > 2:
        problems.append("more than 2 'slide' statement cards; keep them for the biggest ideas")
    for a, b2 in zip(slides, slides[1:]):
        if b2["start"] - a["start"] < motion["minSecondsBetweenSlides"]:
            problems.append(f"{b2['id']}: slide only {b2['start'] - a['start']:.0f}s after {a['id']} (min {motion['minSecondsBetweenSlides']}s)")
    for o in slides:
        if o["end"] - o["start"] > 3.0:
            problems.append(f"{o['id']}: full-screen slide {o['end'] - o['start']:.1f}s (max 3s)")

    if mode == "light":
        bad = sorted({o["type"] for o in ovs} - LIGHT_TYPES)
        if bad and not plan.get("notes"):
            problems.append(f"light mode only allows {sorted(LIGHT_TYPES)} unless the user asked (got {bad})")
        lpm = len(ovs) / max(dur / 60, 1)
        if not plan.get("notes") and lpm > motion["lightMaxPerMinute"]:
            problems.append(f"light mode: {lpm:.1f} overlays/min exceeds {motion['lightMaxPerMinute']} (no notes given)")

    kin = [o for o in ovs if o["type"] == "kinetic_text"]
    kin_per_min = len(kin) / max(dur / 60, 1)
    if kin_per_min > motion["maxKineticPerMinute"]:
        problems.append(f"{kin_per_min:.1f} kinetic_text/min exceeds max {motion['maxKineticPerMinute']} (no captions!)")
    covered = sum(o["end"] - o["start"] for o in spaced if o["type"] not in ("title_card", "end_card"))
    pct = 100 * covered / dur
    if pct > motion["maxTextCoveragePct"]:
        problems.append(f"text on screen {pct:.0f}% of runtime exceeds max {motion['maxTextCoveragePct']}%")
    accents = [o.get("props", {}).get("color", "primary") for o in spaced]
    if len(accents) >= 5 and accents.count("primary") < len(accents) / 2:
        problems.append("less than half of overlays use the primary color; keep it as the main brand accent")

    if problems:
        print("PLAN CHECK FAILED:\n- " + "\n- ".join(problems))
        sys.exit(1)
    print(f"OK — {len(ovs)} overlays over {dur:.1f}s ({per_min:.1f}/min)")


if __name__ == "__main__":
    main()
