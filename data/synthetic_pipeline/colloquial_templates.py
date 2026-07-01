"""Colloquial-translation layer (brief section 5, step 2): renders clean
clinical scenario fields into heavily code-switched Hinglish phrasing, the
way an ASHA/ANM worker might actually describe a case out loud.

Template-based and fully offline — no LLM call required. `generate_dialogues.py`
also supports an `llm` mode that asks an LLM to paraphrase these same fields
for more variety, keeping the same ground-truth labels.
"""

import random

SYMPTOM_PHRASES: dict[str, list[str]] = {
    "fever": ["bukhar", "tez bukhar", "bukhar sa lag raha hai"],
    "chills": ["thand lagna", "kanpkapi ho rahi hai"],
    "cough": ["khansi", "khich khich khansi"],
    "headache": ["sar dard", "sar mein bahut dard"],
    "vomiting": ["ulti", "ulti aa rahi hai"],
    "diarrhea": ["dast", "loose motion ho rahe hain"],
    "swelling in legs": ["pairon mein sujan", "pair mein sujan hai"],
    "vaginal bleeding": ["neeche se bleeding ho rahi hai"],
    "rash": ["shareer par chhote chhote daane", "skin par rash nikla hai"],
    "joint pain": ["ghutno mein dard", "jodo mein dard rehta hai"],
}

MEDICATION_PHRASES: dict[str, list[str]] = {
    "paracetamol": ["paracetamol li thi", "PCM ki tablet khayi"],
    "ORS": ["ORS ghol pilaya", "ORS diya"],
    "ibuprofen": ["ibuprofen li thi"],
    "azithromycin": ["azithromycin ki dawai chalu ki"],
}

_DURATION_UNIT_HI = {
    "day": "din", "days": "din",
    "week": "hafte", "weeks": "hafte",
    "hour": "ghante", "hours": "ghante",
}


def _duration_to_hinglish(duration: str | None) -> str | None:
    if not duration:
        return None
    parts = duration.split()
    if len(parts) == 2 and parts[1].rstrip("s") in {"day", "week", "hour"}:
        number, unit = parts
        return f"{number} {_DURATION_UNIT_HI.get(unit, unit)} se"
    return duration  # already free text, e.g. "few hours"


def render_transcript(scenario: dict, rng: random.Random | None = None) -> tuple[str, str]:
    """Returns (transcript_text, language_tag) for a scenario dict from scenario_bank.SCENARIOS."""
    rng = rng or random.Random()
    clauses: list[str] = []

    for symptom in scenario["symptoms"]:
        phrase = rng.choice(SYMPTOM_PHRASES.get(symptom["name"], [symptom["name"]]))
        duration_hi = _duration_to_hinglish(symptom.get("duration"))
        clause = f"{phrase} {duration_hi} hai" if duration_hi else f"{phrase} hai"
        clauses.append(clause)

    for medication in scenario["medications"]:
        phrase = rng.choice(MEDICATION_PHRASES.get(medication["name"], [f"{medication['name']} li thi"]))
        clauses.append(phrase)

    transcript = ", ".join(clauses) + "."
    return transcript, "hi-en"
