// Mirrors backend/app/models/schemas.py — keep in sync manually until M7
// generates this from the FastAPI OpenAPI schema.

export interface Transcript {
  text: string;
  language: string;
  confidence: number | null;
  audio_duration_sec: number | null;
}

export interface Symptom {
  name: string;
  duration: string | null;
  severity: string | null;
  notes: string | null;
}

export interface Medication {
  name: string;
  dosage: string | null;
  frequency: string | null;
}

export interface Diagnosis {
  name: string;
  snomed_code: string | null;
}

export interface ExtractedEntities {
  symptoms: Symptom[];
  medications: Medication[];
  diagnoses: Diagnosis[];
}

export type VerificationReason = "missing" | "ambiguous" | "conflicting";

export interface VerificationQuestion {
  field: string;
  reason: VerificationReason;
  question: string;
  language: string;
}

export interface VerificationResult {
  passed: boolean;
  questions: VerificationQuestion[];
}

export interface FHIRCoding {
  system: string;
  code: string;
  display: string;
}

export interface FHIRReasonCode {
  coding: FHIRCoding[];
  text: string;
}

export interface FHIREncounter {
  resourceType: "Encounter";
  id: string;
  status: "planned" | "in-progress" | "finished";
  subject_patient_id: string | null;
  reasonCode: FHIRReasonCode[];
  created_at: string;
}

export interface PatientProfile {
  patient_id: string;
  name: string | null;
  age: number | null;
  gender: string | null;
  village: string | null;
  chronic_conditions: string[];
  known_medications: Medication[];
  encounter_ids: string[];
  updated_at: string;
}
