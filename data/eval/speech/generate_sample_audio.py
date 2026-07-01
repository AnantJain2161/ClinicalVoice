#!/usr/bin/env python3
"""One-time helper: synthesizes a tiny labeled audio sample via offline TTS
(pyttsx3 / Windows SAPI5) so M2's WER sanity check has something to run
against without needing real field recordings yet.

English-only (SAPI5 default voices) — swap in real vernacular recordings, or
NeMo Riva TTS output, for a meaningful ASR score. See manifest.csv.

Usage: python generate_sample_audio.py
"""

import csv
from pathlib import Path

import pyttsx3

OUT_DIR = Path(__file__).parent / "audio"
MANIFEST = Path(__file__).parent / "manifest.csv"

SAMPLES = [
    ("sample_001", "Patient reports fever for three days with chills."),
    ("sample_002", "Cough and headache for five days, mild severity."),
    ("sample_003", "Vomiting and diarrhea since yesterday, severe."),
    ("sample_004", "Swelling in legs for one week and severe headache."),
    ("sample_005", "Joint pain for three weeks, took ibuprofen."),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()

    rows = []
    for name, text in SAMPLES:
        wav_path = OUT_DIR / f"{name}.wav"
        engine.save_to_file(text, str(wav_path))
        rows.append({"audio_path": f"audio/{name}.wav", "reference_text": text, "language": "en"})
    engine.runAndWait()

    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["audio_path", "reference_text", "language"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} audio clips to {OUT_DIR} and manifest to {MANIFEST}")


if __name__ == "__main__":
    main()
