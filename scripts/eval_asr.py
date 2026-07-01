#!/usr/bin/env python3
"""M2 eval: Word Error Rate of the Speech Agent against data/eval/speech/manifest.csv.

The bundled manifest points at English TTS clips (see
data/eval/speech/generate_sample_audio.py) since that's what's generatable
offline right now — swap in real vernacular field recordings (and switch
ASR_BACKEND=openai) for a meaningful score once available.

Usage:
    ASR_BACKEND=mock python scripts/eval_asr.py
    ASR_BACKEND=openai OPENAI_API_KEY=sk-... python scripts/eval_asr.py
"""

import csv
import sys
from pathlib import Path

import jiwer

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.agents.speech_agent import SpeechAgent  # noqa: E402

MANIFEST = REPO_ROOT / "data" / "eval" / "speech" / "manifest.csv"
AUDIO_ROOT = MANIFEST.parent


def main() -> None:
    if not MANIFEST.exists():
        raise SystemExit(
            f"No manifest at {MANIFEST}. Run data/eval/speech/generate_sample_audio.py first, "
            "or add your own audio_path,reference_text,language rows."
        )

    with MANIFEST.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    agent = SpeechAgent()
    evaluated, skipped = 0, 0
    references, hypotheses = [], []

    for row in rows:
        audio_path = AUDIO_ROOT / row["audio_path"]
        if not audio_path.exists():
            skipped += 1
            continue
        transcript = agent.transcribe(audio_path.read_bytes(), language_hint=row.get("language"))
        references.append(row["reference_text"])
        hypotheses.append(transcript.text)
        evaluated += 1

    if skipped:
        print(f"Skipped {skipped} row(s) with missing audio files.")
    if not evaluated:
        raise SystemExit("No audio files found to evaluate.")

    wer = jiwer.wer(references, hypotheses)
    print(f"Samples evaluated: {evaluated}")
    print(f"WER: {wer:.3f}")
    for ref, hyp in zip(references, hypotheses):
        print(f"  ref: {ref!r}\n  hyp: {hyp!r}\n")


if __name__ == "__main__":
    main()
