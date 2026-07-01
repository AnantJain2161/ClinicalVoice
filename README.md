# ClinicalVoice

Agentic AI pipeline that turns vernacular clinical speech into a verified, FHIR-compliant health record. See [ClinicalVoice_Project_Brief.md](ClinicalVoice_Project_Brief.md) for the full concept/architecture and [ACTION_PLAN.md](ACTION_PLAN.md) for the 3-week phased build plan.

**Status:** Phase 1 complete — scaffolding, Speech Agent, Medical NLP Agent, and the synthetic data pipeline are working standalone with baseline metrics. Verification/Record/Memory agents and LangGraph orchestration (Phase 2) come next.

---

## Prerequisites

- Python 3.11+ (tested on 3.14)
- Node.js 20+
- Docker Desktop (for Postgres + Redis)

## 1. Infra

```bash
docker-compose up -d
```

Starts Postgres on `5432` and Redis on `6379` with the credentials in [docker-compose.yml](docker-compose.yml).

## 2. Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # macOS/Linux: .venv/bin/pip
cp .env.example .env                              # defaults to mock backends, no API key needed
./.venv/Scripts/python -m uvicorn app.main:app --reload
```

Visit `http://localhost:8000/health` — should return `{"status": "ok"}`.

Run tests:

```bash
./.venv/Scripts/python -m pytest -q
```

### Swapping in real model backends

By default `ASR_BACKEND` and `NLP_BACKEND` are `mock` (deterministic, no external calls — good for local dev and CI). Set `OPENAI_API_KEY` in `.env` and switch both to `openai` to use real Whisper transcription and LLM-based clinical extraction, standing in for NVIDIA NeMo/NIM until those are wired in.

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens the voice recorder shell at `http://localhost:5173`. Record/playback works standalone; wiring to the backend pipeline happens in Phase 2 (M7/M8).

## 4. Synthetic data + eval scripts (M9, M2, M3)

Generate a labeled synthetic transcript set (clinical scenario → colloquial Hinglish rendering):

```bash
./backend/.venv/Scripts/python data/synthetic_pipeline/generate_dialogues.py --count 16
```

Writes to `data/eval/nlp/labeled_transcripts.json`. Pass `--backend llm` (requires `OPENAI_API_KEY`) for LLM-paraphrased variety instead of the template renderer.

Generate a tiny offline-TTS audio sample for the ASR eval (English only — swap in real vernacular recordings for a meaningful score):

```bash
./backend/.venv/Scripts/python data/eval/speech/generate_sample_audio.py
```

Run the eval scripts:

```bash
ASR_BACKEND=mock ./backend/.venv/Scripts/python scripts/eval_asr.py
NLP_BACKEND=mock ./backend/.venv/Scripts/python scripts/eval_nlp.py
```

Both work against the mock backends out of the box; set `ASR_BACKEND=openai` / `NLP_BACKEND=openai` with a key for real numbers.

## Repo layout

See brief section 10 for the target structure. Current state:

```
backend/app/
  main.py            # FastAPI app, /health
  config.py          # env-driven settings (backend selection, DSNs)
  models/schemas.py   # shared Pydantic contracts
  db/postgres.py      # SQLAlchemy models: patients, encounters, sessions
  db/redis_client.py  # session/conversation state helpers
  agents/speech_agent.py  # ASR: transcribe() interface, mock + OpenAI backends
  agents/nlp_agent.py     # extraction: extract() interface, mock + OpenAI backends
backend/tests/        # pytest suite for the above
data/synthetic_pipeline/  # scenario bank + colloquial renderer + generator CLI
data/eval/nlp/         # labeled synthetic transcripts (F1 eval set)
data/eval/speech/      # audio manifest + generator (WER eval set)
scripts/eval_nlp.py    # precision/recall/F1 against data/eval/nlp
scripts/eval_asr.py    # WER against data/eval/speech
frontend/src/
  components/VoiceRecorder.tsx  # record + playback
  types.ts                       # TS mirror of backend schemas
  App.tsx
```
