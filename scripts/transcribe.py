#!/usr/bin/env python3
"""Transcribe a video with ElevenLabs Speech-to-Text, word-level timestamps.

Usage:
    python scripts/transcribe.py input/my-recording.mp4 work/my-recording/transcript.raw.json

Extracts mono 16 kHz audio with FFmpeg first (smaller upload, same timing),
then writes:
{
  "text": "...",
  "language": "en",
  "duration": 123.45,
  "words": [ {"text": "Hello", "start": 0.12, "end": 0.48}, ... ],
  "events": [ {"text": "(laughter)", "start": ..., "end": ...} ]
}
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

API_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def probe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def extract_audio(video: str, dest: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", video,
         "-vn", "-ac", "1", "-ar", "16000", "-c:a", "aac", "-b:a", "96k", dest],
        check=True,
    )


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    video, out_path = sys.argv[1], sys.argv[2]

    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("ELEVENLABS_API_KEY missing — add it to .env")
    model = os.getenv("ELEVENLABS_STT_MODEL", "scribe_v2")

    with tempfile.TemporaryDirectory() as tmp:
        audio = os.path.join(tmp, "audio.m4a")
        extract_audio(video, audio)
        with open(audio, "rb") as f:
            resp = requests.post(
                API_URL,
                headers={"xi-api-key": api_key},
                data={
                    "model_id": model,
                    "timestamps_granularity": "word",
                    "tag_audio_events": "true",
                    "diarize": "false",
                },
                files={"file": ("audio.m4a", f, "audio/mp4")},
                timeout=600,
            )
    if resp.status_code != 200:
        sys.exit(f"ElevenLabs STT failed ({resp.status_code}): {resp.text[:500]}")
    data = resp.json()

    words, events = [], []
    for w in data.get("words", []):
        kind = w.get("type", "word")
        item = {"text": w["text"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
        if kind == "word" and item["text"]:
            words.append(item)
        elif kind == "audio_event":
            events.append(item)

    result = {
        "source": video,
        "text": data.get("text", ""),
        "language": data.get("language_code"),
        "duration": round(probe_duration(video), 3),
        "words": words,
        "events": events,
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    print(f"{len(words)} words, {result['duration']:.1f}s → {out_path}")


if __name__ == "__main__":
    main()
