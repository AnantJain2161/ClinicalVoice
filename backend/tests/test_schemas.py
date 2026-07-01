from app.models.schemas import (
    ExtractedEntities,
    FHIREncounter,
    FHIRReasonCode,
    PatientProfile,
    Symptom,
    Transcript,
    VerificationQuestion,
)


def test_transcript_roundtrip() -> None:
    t = Transcript(text="bukhar hai teen din se", language="hi-en", confidence=0.9)
    assert Transcript.model_validate_json(t.model_dump_json()) == t


def test_extracted_entities_defaults_are_empty() -> None:
    entities = ExtractedEntities()
    assert entities.symptoms == []
    assert entities.medications == []
    assert entities.diagnoses == []


def test_extracted_entities_with_symptom() -> None:
    entities = ExtractedEntities(symptoms=[Symptom(name="fever", duration="3 days")])
    assert entities.symptoms[0].name == "fever"


def test_verification_question_reason_is_constrained() -> None:
    q = VerificationQuestion(field="symptoms[0].duration", reason="missing", question="?", language="hi")
    assert q.reason == "missing"


def test_fhir_encounter_default_resource_type() -> None:
    encounter = FHIREncounter(reasonCode=[FHIRReasonCode(text="3-day history of fever")])
    assert encounter.resourceType == "Encounter"
    assert encounter.status == "finished"
    assert encounter.id


def test_patient_profile_generates_id() -> None:
    p1 = PatientProfile()
    p2 = PatientProfile()
    assert p1.patient_id != p2.patient_id
