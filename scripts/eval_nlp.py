#!/usr/bin/env python3
"""M3 eval: precision/recall/F1 of the Medical NLP Agent against the labeled
synthetic transcript set produced by data/synthetic_pipeline/generate_dialogues.py.

Scores symptoms + medications only (by name, case-insensitive) — diagnoses
are a clinical judgement made downstream of raw extraction, not something
the patient's own words reliably state, so they're excluded from this metric.

Usage:
    ASR_BACKEND=mock NLP_BACKEND=mock python scripts/eval_nlp.py
    NLP_BACKEND=openai OPENAI_API_KEY=sk-... python scripts/eval_nlp.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.agents.nlp_agent import MedicalNLPAgent  # noqa: E402

LABELED_SET = REPO_ROOT / "data" / "eval" / "nlp" / "labeled_transcripts.json"


def _names(items: list[dict], key: str = "name") -> set[str]:
    return {item[key].strip().lower() for item in items}


def score_record(agent: MedicalNLPAgent, record: dict) -> tuple[int, int, int]:
    """Returns (true_positives, false_positives, false_negatives) for one record."""
    predicted = agent.extract(record["transcript"], record.get("language"))
    predicted_names = _names([s.model_dump() for s in predicted.symptoms]) | _names(
        [m.model_dump() for m in predicted.medications]
    )
    gold_names = _names(record["entities"]["symptoms"]) | _names(record["entities"]["medications"])

    tp = len(predicted_names & gold_names)
    fp = len(predicted_names - gold_names)
    fn = len(gold_names - predicted_names)
    return tp, fp, fn


def main() -> None:
    if not LABELED_SET.exists():
        raise SystemExit(
            f"No labeled eval set at {LABELED_SET}. Run "
            "data/synthetic_pipeline/generate_dialogues.py first."
        )

    records = json.loads(LABELED_SET.read_text(encoding="utf-8"))
    agent = MedicalNLPAgent()

    total_tp = total_fp = total_fn = 0
    for record in records:
        tp, fp, fn = score_record(agent, record)
        total_tp += tp
        total_fp += fp
        total_fn += fn

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    print(f"Records evaluated: {len(records)}")
    print(f"TP={total_tp} FP={total_fp} FN={total_fn}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1:        {f1:.3f}")


if __name__ == "__main__":
    main()
