# ClinicalVoice — Agentic AI for Vernacular Health Record Generation in Rural India

**Team:** ClinicalVoice Team, Plaksha University, Mohali
**Context:** India Agentic AI Open Hackathon 2026

This document is a working brief for Claude Code (or any implementing engineer) to build a working prototype of ClinicalVoice. It summarizes the problem, the target architecture, the tech stack, the data strategy, and a concrete implementation plan broken into buildable milestones.

---

## 1. Problem Statement

India has 900M+ people served by ASHA/ANM frontline health workers. These workers travel village to village delivering maternal, child, and preventive care, but they must document every consultation manually — often in a language that isn't their native tongue. The result:

- Documentation is slow, error-prone, and takes time away from patient care.
- Almost no rural consultations produce structured digital health records.
- There is no continuity of care across visits because nothing is captured in a reusable, structured format.

**Vision:** A health worker speaks in their own language → a pipeline of AI agents transcribes, extracts, verifies, and generates a complete structured digital health record automatically, ready for India's Ayushman Bharat Digital Mission (ABDM) ecosystem.

---

## 2. Product Concept

ClinicalVoice turns a spoken, vernacular clinical conversation into a verified, standards-compliant digital health record with zero manual data entry, while keeping a human in the loop for anything ambiguous or high-risk.

**Core pipeline:**

```
Voice Input → Transcription → NLP Extraction → Verification → FHIR Record → Memory Store
```

---

## 3. Agent Architecture (5 Agents)

Each stage of the pipeline is owned by a specialized agent, orchestrated as a multi-agent workflow (LangGraph):

1. **Speech Agent** — Transcribes vernacular audio using multilingual ASR (target: NVIDIA NeMo, fine-tuned `nvidia/parakeet-tdt-1.1b` for Indian dialects/code-switching).
2. **Medical NLP Agent** — Extracts symptoms, medications, diagnoses, and durations from the transcript (target: NVIDIA NIM microservices for clinical entity extraction; BioBERT/ClinicalBERT/PubMedBERT-style models as fallback).
3. **Verification Agent** — Detects ambiguity or missing information in the extraction and asks clarifying questions back to the worker in their own language (human-in-the-loop loop).
4. **Record Generation Agent** — Converts verified structured data into an FHIR-compliant resource (e.g. `Encounter`, with SNOMED-coded `reasonCode`), designed for ABDM gateway ingestion.
5. **Patient Memory Agent** — Persists a longitudinal patient profile across visits (continuity of care), with confidence-aware updates and deduplication.

### Example FHIR output (illustrative)
```json
{
  "resourceType": "Encounter",
  "status": "finished",
  "reasonCode": [
    {
      "coding": [{
        "system": "snomed.info/sct",
        "code": "386661006",
        "display": "Fever with chills"
      }],
      "text": "3-day history of fever"
    }
  ]
}
```

---

## 4. Tech Stack

| Layer | Choice |
|---|---|
| Agent orchestration | LangGraph (multi-step orchestration, memory, tool-calling, task routing) |
| Speech recognition | NVIDIA NeMo (multilingual ASR); Parakeet-TDT-1.1B fine-tuned for regional dialects |
| Inference engine | NVIDIA NIM (medical NLP microservices) |
| Guardrails | NeMo Guardrails (clinical safety, hallucination prevention) |
| Backend API | FastAPI (Python) |
| Short-term memory | Redis |
| Long-term memory | PostgreSQL |
| Retrieval | Vector DB + semantic search (RAG for clinical context) |
| Frontend | React, voice interfaces, real-time inference UI |
| Health record standard | FHIR, targeting ABDM (Ayushman Bharat Digital Mission) interoperability |
| Compute | CUDA for local model training/inference |
| Future integration | MCP (Model Context Protocol) for tool interop |

---

## 5. Data Strategy

All external training data is open-source/permissive; no PII is used. All local healthcare training assets are designed to comply with HIPAA and India's DPDP Act.

| Dataset | Type | Scale | License |
|---|---|---|---|
| Mozilla Common Voice v17.0 | Speech ASR (Hindi/Hinglish) | ~25.4 GB, 1,200+ hrs, 1.1M clips | CC0 1.0 |
| MedDialog (EN) | Medical dialogue Q&A | ~1.8 GB, 260K conversations, 44.5M tokens | MIT |
| MTSamples base corpus | Clinical transcription entities | ~420 MB, 5,000 docs, 15M tokens | Permissive academic |
| Hinglish Clinical Synthetic DB | ASR dialogue waveforms | ~350 MB, 1,200 simulated cases, 2.4M tokens | Proprietary (MIT) |

**Synthetic data generation pipeline** (to cover rural dialects without violating patient privacy):
1. LangGraph agents generate raw clinical scenario matrices (e.g. high-risk obstetrics cases) from maternal health parameters.
2. A colloquial-translation layer converts clean clinical prompts into heavily code-switched Hinglish, Bundeli, and rural Hindi/Marathi dialects.
3. NVIDIA Riva/NeMo TTS renders these as synthetic audio, adding local noise perturbations (crowd noise, clinical room ambience) to mimic real field conditions.

---

## 6. Evaluation Metrics

- **WER (Word Error Rate)** — speech recognition accuracy.
- **Precision / Recall / F1** — clinical NLP extraction quality.
- **Record completeness & accuracy** — how complete/correct the generated FHIR record is vs. ground truth.
- **End-to-end latency** — voice input to finished record.
- **User feedback** — from simulated ASHA-worker sessions.

---

## 7. Differentiation vs. Generic AI Tools

| Generic AI Tools | ClinicalVoice |
|---|---|
| Stop at basic transcription, limited vernacular support | Vernacular AI engineered natively for Indian healthcare workflows |
| No self-correction | Agentic clarification loops catch contradictions/missing info instantly |
| No continuity | Patient memory maintains history across visits |
| No standards output | Clinical entity extraction → HL7 FHIR record generation → human-in-the-loop validation |

**Target impact:** ~80% reduction in manual documentation time for frontline workers, faster structured-record generation, and accelerated digital health adoption in underserved rural regions.

---

## 8. Known Limitations & Mitigations

| Limitation | Mitigation |
|---|---|
| Multilingual medical ASR is hard: dialects, code-switching, noise, domain terms | NeMo domain adaptation + synthetic clinical speech data + healthcare corpus fine-tuning |
| Scarce public healthcare NLP datasets in Indian languages | Synthetic multilingual conversations generated via LLM, reviewed against clinical templates |
| High accuracy bar — extraction errors propagate into real medical records | Dedicated Verification Agent with clarification loops + human-in-the-loop validation before finalizing |
| Longitudinal memory consistency / deduplication across visits | Structured patient profiles + confidence-aware memory updates + MemGPT-inspired retrieval |

---

## 9. Long-Term Vision (Post-Hackathon)

- Intelligent clinical decision support (beyond documentation)
- Automated follow-up scheduling/reminders
- Population health insights aggregated across ASHA/ANM records
- Full ABDM integration
- Support for all major Indian languages
- Edge/offline deployment for regions without reliable connectivity

---

## 10. Implementation Plan for Claude Code

The hackathon goal is: **an end-to-end working prototype that takes vernacular speech and outputs a structured FHIR health record with longitudinal patient memory.** Given typical hackathon constraints (no real NVIDIA NeMo/NIM access, limited time), the plan below is structured to degrade gracefully — build the full agentic pipeline with swappable model backends, so cloud APIs can stand in for NeMo/NIM where needed, while keeping the architecture "NVIDIA-ready."

### Suggested repo structure
```
clinicalvoice/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint
│   │   ├── agents/
│   │   │   ├── speech_agent.py        # ASR wrapper (NeMo or fallback: Whisper/cloud STT)
│   │   │   ├── nlp_agent.py           # Clinical entity extraction (NIM or fallback: LLM + regex/NER)
│   │   │   ├── verification_agent.py  # Ambiguity detection + clarification question generation
│   │   │   ├── record_agent.py        # FHIR resource construction
│   │   │   └── memory_agent.py        # Longitudinal patient memory read/write
│   │   ├── graph.py                # LangGraph orchestration wiring the 5 agents together
│   │   ├── models/                 # Pydantic schemas: transcript, extraction, FHIR resource, patient profile
│   │   ├── db/
│   │   │   ├── postgres.py         # Long-term memory (patient records)
│   │   │   └── redis_client.py     # Short-term memory (session/conversation state)
│   │   ├── guardrails/             # NeMo Guardrails config / safety checks
│   │   └── api/
│   │       ├── routes_encounter.py # POST /encounter (voice in → FHIR out)
│   │       └── routes_patient.py   # GET /patient/{id}/history
│   ├── requirements.txt
│   └── tests/
├── data/
│   ├── synthetic_pipeline/         # Scripts to generate synthetic Hinglish clinical dialogues
│   └── datasets/                   # Downloaded/prepared open datasets (Common Voice, MedDialog, MTSamples)
├── frontend/
│   ├── src/
│   │   ├── components/VoiceRecorder.tsx
│   │   ├── components/RecordViewer.tsx   # FHIR JSON / human-readable record display
│   │   ├── components/ClarificationChat.tsx  # Verification Agent Q&A UI
│   │   └── App.tsx
│   └── package.json
└── README.md
```

### Milestones

**M1 — Scaffolding & Contracts**
- Stand up FastAPI backend with health check, and a React frontend shell with a voice recorder component.
- Define Pydantic/TypeScript schemas for: raw transcript, extracted clinical entities, verification questions, FHIR Encounter resource, patient memory profile.
- Set up PostgreSQL (long-term) and Redis (short-term) with minimal schemas: `patients`, `encounters`, `sessions`.

**M2 — Speech Agent**
- Implement an ASR wrapper interface (`transcribe(audio) -> text`) with a pluggable backend.
- For the hackathon, integrate a working fallback (e.g. a hosted multilingual STT API or open Whisper) behind the same interface NeMo would use, so it can be swapped later.
- Record WER against a small labeled sample for the eval metric.

**M3 — Medical NLP Agent**
- Implement entity extraction (`extract(transcript) -> {symptoms, medications, diagnoses, durations}`).
- Start with an LLM-based structured-extraction prompt (function calling / JSON schema output) as the NIM stand-in.
- Track precision/recall/F1 against a small hand-labeled set of synthetic transcripts.

**M4 — Verification Agent**
- Given the extracted entities + original transcript, detect missing/ambiguous fields (e.g. no duration for a symptom, conflicting medication info).
- Generate a clarification question in the same language as the input.
- Loop: clarification answer re-enters the NLP agent for re-extraction.

**M5 — Record Generation Agent**
- Map verified structured entities to FHIR resources (start with `Encounter` + `Condition`/`MedicationStatement` as needed), including SNOMED coding where feasible.
- Validate output against a FHIR schema validator.

**M6 — Patient Memory Agent**
- Persist patient profile + encounter history in PostgreSQL.
- On each new encounter, retrieve relevant history (RAG-style) to inform verification (e.g. known chronic conditions) and to avoid duplicate entries.

**M7 — LangGraph Orchestration**
- Wire all 5 agents into a single LangGraph graph: `speech → nlp → verify (loop) → record → memory`.
- Add guardrail checks (e.g. block record finalization if verification hasn't passed).

**M8 — Frontend Integration**
- Voice recorder → upload/stream audio → show live transcript → show extracted fields → show clarification chat if triggered → show final FHIR record.

**M9 — Synthetic Data Pipeline (parallel track)**
- Build the LangGraph-based synthetic dialogue generator: clinical scenario → colloquial Hinglish/dialect translation → (optional) TTS rendering.
- Use this to create a small eval set for ASR/NLP metrics above.

**M10 — Demo Polish & Metrics Dashboard**
- Simple dashboard showing WER, extraction F1, record completeness, and end-to-end latency on the eval set, plus a live end-to-end demo path.

### Suggested first Claude Code task
Start with **M1**: scaffold the FastAPI backend + React frontend, define the shared schemas, and stand up Postgres/Redis locally (e.g. via docker-compose), so every later agent has a stable contract to build against.

---

## 11. Open Questions / Where Mentor Input Was Sought

- Best practices for leveraging NVIDIA NeMo/NIM/Agentic AI tooling within a tight hackathon timeline.
- Adapting ASR to healthcare vocabulary plus Indian language accents/dialects.
- Scalable multi-agent orchestration patterns: memory management and verification-loop design.
- FHIR record generation and ABDM integration best practices.
