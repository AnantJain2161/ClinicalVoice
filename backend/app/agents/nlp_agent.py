"""Medical NLP Agent: extract(transcript) -> ExtractedEntities.

Pluggable backend so NVIDIA NIM clinical-entity microservices can later be
dropped in behind the same `NLPBackend` interface (brief section 10, M3).
"""

import re
from abc import ABC, abstractmethod

from app.config import settings
from app.models.schemas import Diagnosis, ExtractedEntities, Medication, Symptom

_EXTRACTION_SYSTEM_PROMPT = """You are a clinical information extraction system for rural Indian \
health worker consultations, which are often in Hinglish or code-switched regional languages.

Extract symptoms, medications, and diagnoses mentioned in the transcript. Respond with ONLY a JSON \
object matching this shape, with no extra commentary:

{
  "symptoms": [{"name": str, "duration": str | null, "severity": str | null, "notes": str | null}],
  "medications": [{"name": str, "dosage": str | null, "frequency": str | null}],
  "diagnoses": [{"name": str, "snomed_code": str | null}]
}

If a field isn't mentioned, use null. If nothing of a category is mentioned, use an empty list."""


class NLPBackend(ABC):
    @abstractmethod
    def extract(self, transcript_text: str, language: str | None = None) -> ExtractedEntities:
        ...


class MockNLPBackend(NLPBackend):
    """Tiny rule-based extractor with no external dependencies, for local dev/tests.

    Not a substitute for the LLM backend's clinical coverage — just enough
    pattern matching to make the mock path exercise real control flow.
    """

    _DURATION_RE = re.compile(r"(\d+)\s*-?\s*(day|days|week|weeks|hour|hours)", re.IGNORECASE)
    _SYMPTOM_KEYWORDS = ["fever", "chills", "cough", "headache", "vomiting", "pain", "nausea"]
    _MED_KEYWORDS = ["paracetamol", "ibuprofen", "ors", "amoxicillin", "azithromycin"]

    def extract(self, transcript_text: str, language: str | None = None) -> ExtractedEntities:
        text_lower = transcript_text.lower()
        duration_match = self._DURATION_RE.search(text_lower)
        duration = duration_match.group(0) if duration_match else None

        symptoms = [
            Symptom(name=kw, duration=duration)
            for kw in self._SYMPTOM_KEYWORDS
            if kw in text_lower
        ]
        medications = [
            Medication(name=kw)
            for kw in self._MED_KEYWORDS
            if kw in text_lower
        ]
        return ExtractedEntities(symptoms=symptoms, medications=medications, diagnoses=[])


class LLMExtractionBackend(NLPBackend):
    """LLM structured-extraction fallback standing in for NIM until real access is available."""

    def __init__(self) -> None:
        from openai import OpenAI

        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the 'openai' NLP backend")
        self._client = OpenAI(api_key=settings.openai_api_key)

    def extract(self, transcript_text: str, language: str | None = None) -> ExtractedEntities:
        response = self._client.chat.completions.create(
            model=settings.nlp_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": transcript_text},
            ],
        )
        raw_json = response.choices[0].message.content
        return ExtractedEntities.model_validate_json(raw_json)


class MedicalNLPAgent:
    def __init__(self, backend: NLPBackend | None = None) -> None:
        self._backend = backend or _build_backend(settings.nlp_backend)

    def extract(self, transcript_text: str, language: str | None = None) -> ExtractedEntities:
        return self._backend.extract(transcript_text, language)


def _build_backend(name: str) -> NLPBackend:
    if name == "openai":
        return LLMExtractionBackend()
    if name == "mock":
        return MockNLPBackend()
    raise ValueError(f"Unknown NLP backend: {name!r}")
