#!/usr/bin/env python3
"""Synthetic clinical dialogue generator (brief section 5 / milestone M9).

Pipeline: clinical scenario matrix -> colloquial Hinglish/dialect rendering
-> (optional) LLM paraphrase for extra variety -> labeled JSON records.

TTS rendering (brief step 3, NeMo Riva/TTS + noise perturbation) is left as
a future step — this script produces text-only labeled transcripts, which is
enough to drive the ASR/NLP eval scripts for now.

Usage:
    python generate_dialogues.py --count 16 --backend template
    python generate_dialogues.py --count 16 --backend llm   # requires OPENAI_API_KEY
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from colloquial_templates import render_transcript
from scenario_bank import SCENARIOS

DEFAULT_OUT = Path(__file__).parent.parent / "eval" / "nlp" / "labeled_transcripts.json"


def _llm_paraphrase(transcript: str, api_key: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Paraphrase this rural Indian health-worker consultation note as a natural, "
                    "code-switched Hinglish sentence a patient might actually say out loud. "
                    "Keep every symptom, duration, and medication mentioned. Output only the sentence."
                ),
            },
            {"role": "user", "content": transcript},
        ],
    )
    return response.choices[0].message.content.strip()


def generate(count: int, backend: str, seed: int, api_key: str | None) -> list[dict]:
    rng = random.Random(seed)
    records = []
    for i in range(count):
        scenario = SCENARIOS[i % len(SCENARIOS)]
        transcript, language = render_transcript(scenario, rng)

        if backend == "llm":
            if not api_key:
                raise SystemExit("--backend llm requires OPENAI_API_KEY to be set")
            transcript = _llm_paraphrase(transcript, api_key)

        records.append(
            {
                "record_id": f"{scenario['id']}-{i:03d}",
                "scenario_id": scenario["id"],
                "transcript": transcript,
                "language": language,
                "entities": {
                    "symptoms": scenario["symptoms"],
                    "medications": scenario["medications"],
                    "diagnoses": scenario["diagnoses"],
                },
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--backend", choices=["template", "llm"], default="template")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    import os

    records = generate(args.count, args.backend, args.seed, os.environ.get("OPENAI_API_KEY"))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} labeled synthetic transcripts to {args.out}")


if __name__ == "__main__":
    main()
