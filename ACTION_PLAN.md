# ClinicalVoice — Action Plan

Derived from [ClinicalVoice_Project_Brief.md](ClinicalVoice_Project_Brief.md). This turns the 10 milestones into a sequenced, checkable build plan across a 3-week project.

**Goal:** working end-to-end demo — vernacular speech in, verified FHIR `Encounter` out, with longitudinal patient memory — by end of Week 3.

**Timeline:** Week 1: Jul 1 – Jul 7 · Week 2: Jul 8 – Jul 14 · Week 3: Jul 15 – Jul 21

---

## 0. Before writing code (Day 1)

- [x] Confirm repo init: `git init`, create `clinicalvoice/` structure from brief §10.
- [x] Decide model-backend stand-ins now (no NeMo/NIM access assumed):
  - ASR fallback: hosted multilingual STT API (e.g. Whisper API) behind a `transcribe(audio) -> text` interface.
  - NLP fallback: LLM function-calling / JSON-schema extraction behind an `extract(transcript) -> entities` interface.
  - Keep both interfaces named/shaped so NeMo/NIM can be swapped in later without touching callers.
- [x] Provision local infra: `docker-compose.yml` for Postgres + Redis.
- [x] Get API keys needed (STT provider, LLM provider) into `.env` (never commit) — `.env.example` scaffolded, defaults to no-key-needed mock backends.
- [ ] Assign owners per milestone if working as a team (parallel tracks noted below).

---

## Phase 1 — Foundation (Week 1, Jul 1–7)

**Phase goal:** stable contracts + the two independent, model-facing agents (speech, NLP) each working standalone with a measured baseline metric. Synthetic data generation starts in parallel since nothing downstream blocks on it.

### M1 — Scaffolding & Contracts ✅
**Depends on:** nothing. **Blocks:** everything else.
- [x] FastAPI backend with `/health` endpoint.
- [x] React frontend shell with a voice recorder component (record + playback only, no wiring yet).
- [x] Pydantic schemas: `Transcript`, `ExtractedEntities`, `VerificationQuestion`, `FHIREncounter`, `PatientProfile`.
- [x] Mirror as TypeScript types for frontend.
- [x] Postgres schema: `patients`, `encounters`, `sessions` tables (minimal columns, migrate later).
- [x] Redis client wired for session/conversation state.
- **Done when:** backend boots, frontend boots, `docker-compose up` gives working Postgres+Redis, schemas import cleanly on both sides. — **Verified:** 11/11 backend tests pass, `npm run build` typechecks and builds clean.

### M2 — Speech Agent ✅
**Depends on:** M1 schemas. **Parallelizable with:** M3, M9.
- [x] `speech_agent.py`: `transcribe(audio_bytes) -> Transcript` interface.
- [x] Wire fallback STT provider behind that interface (OpenAI Whisper; mock backend for no-key dev/CI).
- [x] Small labeled audio sample (5 clips, offline TTS) for WER sanity check.
- [x] Record WER number for the metrics dashboard (M10).
- **Done when:** an audio file in → text out, WER measured once. — **Baseline (mock backend): WER = 1.184.** Expected: mock always returns one fixed transcript; re-run with `ASR_BACKEND=openai` for a real number.

### M3 — Medical NLP Agent ✅
**Depends on:** M1 schemas. **Parallelizable with:** M2, M9.
- [x] `nlp_agent.py`: `extract(transcript) -> ExtractedEntities` (symptoms, medications, diagnoses, durations).
- [x] LLM-based structured-extraction prompt with strict JSON schema output as NIM stand-in.
- [x] Hand-label ~10–20 synthetic transcripts; compute precision/recall/F1 (16 auto-labeled via M9's generator).
- **Done when:** transcript in → structured entities out, F1 measured once. — **Baseline (mock backend): P=1.00, R=0.22, F1=0.36.** Mock only recognizes a small keyword list; re-run with `NLP_BACKEND=openai` for a real number.

### M9 — Synthetic Data Pipeline ✅ *(started alongside M2/M3, feeds M2/M3/M10 all project long)*
**Depends on:** nothing blocking.
- [x] LangGraph generator: clinical scenario matrix → colloquial Hinglish/dialect translation (template-based `generate_dialogues.py`; `--backend llm` variant available).
- [ ] Optional: NeMo Riva/TTS rendering with noise perturbation (deferred; text-only eval set used instead — acceptable fallback per plan).
- [x] Produce a small labeled eval set for WER/F1 metrics (16 records in `data/eval/nlp/labeled_transcripts.json`, 5 audio clips in `data/eval/speech/`).
- **Done when:** a repeatable script produces N labeled synthetic transcripts on demand. — **Verified:** `generate_dialogues.py --count 16` runs and writes labeled JSON.

**Phase 1 exit criteria — MET:** M1, M2, M3 done; M9 producing labeled batches for both eval scripts. Two agents work standalone with a baseline metric each; nothing wired together yet (that's Phase 2, M7).

---

## Phase 2 — Core Agentic Loop (Week 2, Jul 8–14)

**Phase goal:** the parts that make this "agentic" rather than a single API call — clarification loop, standards-compliant output, and cross-visit memory — each working standalone, then orchestrated into one graph.

### M4 — Verification Agent
**Depends on:** M3.
- [ ] `verification_agent.py`: detect missing/ambiguous fields (e.g. symptom with no duration, conflicting meds).
- [ ] Generate clarification question in the input's own language.
- [ ] Loop wiring: clarification answer → back into NLP agent → re-extraction.
- **Done when:** a deliberately incomplete transcript produces a sensible clarifying question, and a follow-up answer improves the extraction.

### M5 — Record Generation Agent
**Depends on:** M4 (verified entities).
- [ ] `record_agent.py`: map verified entities → FHIR `Encounter` (+ `Condition`/`MedicationStatement` as needed).
- [ ] Add SNOMED coding where feasible (static lookup table is fine at this stage).
- [ ] Validate output against a FHIR schema validator.
- **Done when:** verified entities in → schema-valid FHIR JSON out, matching the example in brief §3.

### M6 — Patient Memory Agent
**Depends on:** M1 (Postgres schema), M5 (encounters to persist).
- [ ] `memory_agent.py`: persist patient profile + encounter history to Postgres.
- [ ] On new encounter, retrieve relevant history (chronic conditions, prior meds) to feed into Verification Agent (M4) context.
- [ ] Basic dedup: don't re-write identical condition/medication entries across visits.
- **Done when:** two sequential encounters for the same patient show the second one referencing the first's history.

### M7 — LangGraph Orchestration
**Depends on:** M2–M6 all working standalone.
- [ ] `graph.py`: wire `speech → nlp → verify (loop) → record → memory` as a single LangGraph graph.
- [ ] Guardrail: block record finalization if verification hasn't passed.
- [ ] Expose via `POST /encounter` (voice in → FHIR out) and `GET /patient/{id}/history`.
- **Done when:** one API call takes raw audio and returns a finished FHIR record, looping through clarification if needed.

**Phase 2 exit criteria:** M4–M7 done. A single API call goes voice → FHIR record end-to-end, including at least one working clarification loop and one instance of memory-informed verification.

---

## Phase 3 — Integration, Evaluation & Demo (Week 3, Jul 15–21)

**Phase goal:** make the working pipeline visible and presentable, backed by real metrics, with a rehearsed and de-risked demo.

### M8 — Frontend Integration
**Depends on:** M7.
- [ ] Wire voice recorder → upload/stream to `/encounter`.
- [ ] Show live transcript → extracted fields → clarification chat (if triggered) → final FHIR record.
- **Done when:** a person can speak into the browser and see the full pipeline resolve to a FHIR record on screen.

### M10 — Demo Polish & Metrics Dashboard
**Depends on:** everything above.
- [ ] Dashboard (even a simple page/table) showing WER, extraction F1, record completeness, end-to-end latency.
- [ ] Expand M9's eval set if time allows; re-run metrics against the larger set.
- [ ] Rehearse one clean end-to-end live-demo path (pick the best-behaving sample case).
- [ ] Prepare fallback: a recorded video/gif of the pipeline in case of live-demo/network failure.
- **Done when:** metrics are visible somewhere, and the demo path has been run start-to-finish at least twice without manual intervention.

**Phase 3 exit criteria:** full pipeline usable from the browser, metrics dashboard populated, demo rehearsed with a fallback recording in hand.

---

## If a phase slips

Protect this chain over everything else — it's what makes the demo "agentic" rather than a single API call:

```
M1 → M2 → M3 → M5 → M7 → M8
```

M4 (verification loop) and M6 (patient memory) are the two most differentiating features per brief §7 — cut M9's TTS rendering and M10's dashboard/eval-set expansion before cutting these. If Phase 2 overruns, prefer pushing M10's polish into Week 3's buffer rather than cutting M4 or M6.

---

## Immediate next step

Start **M1**: scaffold FastAPI backend + React frontend, define shared schemas, stand up Postgres/Redis via `docker-compose`, per brief §10's "Suggested first Claude Code task."
