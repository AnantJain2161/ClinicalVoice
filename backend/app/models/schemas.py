from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---- Speech Agent output ----------------------------------------------------

class Transcript(BaseModel):
    text: str
    language: str = Field(description="BCP-47-ish tag, e.g. 'hi-IN', 'hi-en' for Hinglish")
    confidence: float | None = None
    audio_duration_sec: float | None = None


# ---- Medical NLP Agent output ------------------------------------------------

class Symptom(BaseModel):
    name: str
    duration: str | None = None
    severity: str | None = None
    notes: str | None = None


class Medication(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None


class Diagnosis(BaseModel):
    name: str
    snomed_code: str | None = None


class ExtractedEntities(BaseModel):
    symptoms: list[Symptom] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    diagnoses: list[Diagnosis] = Field(default_factory=list)


# ---- Verification Agent output -----------------------------------------------

class VerificationQuestion(BaseModel):
    field: str = Field(description="Dotted path into ExtractedEntities, e.g. 'symptoms[0].duration'")
    reason: Literal["missing", "ambiguous", "conflicting"]
    question: str = Field(description="Clarifying question phrased in the transcript's own language")
    language: str


class VerificationResult(BaseModel):
    passed: bool
    questions: list[VerificationQuestion] = Field(default_factory=list)


# ---- Record Generation Agent output ------------------------------------------

class FHIRCoding(BaseModel):
    system: str = "http://snomed.info/sct"
    code: str
    display: str


class FHIRReasonCode(BaseModel):
    coding: list[FHIRCoding] = Field(default_factory=list)
    text: str


class FHIREncounter(BaseModel):
    resourceType: Literal["Encounter"] = "Encounter"
    id: str = Field(default_factory=_uuid)
    status: Literal["planned", "in-progress", "finished"] = "finished"
    subject_patient_id: str | None = None
    reasonCode: list[FHIRReasonCode] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


# ---- Patient Memory Agent state ----------------------------------------------

class PatientProfile(BaseModel):
    patient_id: str = Field(default_factory=_uuid)
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    village: str | None = None
    chronic_conditions: list[str] = Field(default_factory=list)
    known_medications: list[Medication] = Field(default_factory=list)
    encounter_ids: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=_now)
