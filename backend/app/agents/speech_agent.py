"""Speech Agent: transcribe(audio) -> Transcript.

Pluggable backend so NVIDIA NeMo / Parakeet-TDT can later be dropped in behind
the same `ASRBackend` interface without touching callers (brief section 10, M2).
"""

import io
from abc import ABC, abstractmethod

from app.config import settings
from app.models.schemas import Transcript


class ASRBackend(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language_hint: str | None = None) -> Transcript:
        ...


class MockASRBackend(ASRBackend):
    """Deterministic stand-in with no external dependencies, for local dev/tests."""

    def transcribe(self, audio_bytes: bytes, language_hint: str | None = None) -> Transcript:
        return Transcript(
            text="Patient reports fever for 3 days with chills, took paracetamol yesterday.",
            language=language_hint or "hi-en",
            confidence=0.42,
            audio_duration_sec=None,
        )


class OpenAIWhisperBackend(ASRBackend):
    """Fallback ASR standing in for NeMo/Parakeet until real access is available."""

    def __init__(self) -> None:
        from openai import OpenAI

        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the 'openai' ASR backend")
        self._client = OpenAI(api_key=settings.openai_api_key)

    def transcribe(self, audio_bytes: bytes, language_hint: str | None = None) -> Transcript:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        response = self._client.audio.transcriptions.create(
            model=settings.asr_model,
            file=audio_file,
            language=language_hint.split("-")[0] if language_hint else None,
        )
        return Transcript(text=response.text, language=language_hint or "hi-en")


class SpeechAgent:
    def __init__(self, backend: ASRBackend | None = None) -> None:
        self._backend = backend or _build_backend(settings.asr_backend)

    def transcribe(self, audio_bytes: bytes, language_hint: str | None = None) -> Transcript:
        return self._backend.transcribe(audio_bytes, language_hint)


def _build_backend(name: str) -> ASRBackend:
    if name == "openai":
        return OpenAIWhisperBackend()
    if name == "mock":
        return MockASRBackend()
    raise ValueError(f"Unknown ASR backend: {name!r}")
