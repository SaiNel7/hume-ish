# Ask Hume

A voice-first RAG chatbot that lets you converse with David Hume's philosophy. Ask questions via microphone; get answers in Hume's voice, grounded in his actual writings.

## How it works

1. **Ingestion** — Downloads public-domain Hume texts from Project Gutenberg, cleans them, chunks them, embeds via OpenAI, and stores in ChromaDB.
2. **Query** — User speaks → Whisper transcribes → top chunks retrieved + reranked → Claude generates a response in Hume's voice → Cartesia synthesizes speech.
3. **Frontend** — React app with a voice recorder UI; plays back the audio response and displays the transcript.

## Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI, Python 3.11+ |
| LLM | Anthropic Claude |
| STT | OpenAI Whisper |
| TTS | Cartesia |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector DB | ChromaDB |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Frontend | React 18, TypeScript, Vite, Tailwind |

## Setup

### Prerequisites
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+

### 1. Clone & install

```bash
git clone <repo-url>
cd humeish
uv sync                        # install Python deps
cd frontend && npm install     # install JS deps
cd ..
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
CARTESIA_API_KEY=...
CARTESIA_VOICE_ID=...
```

### 3. Ingest Hume's writings

Only needed once. Downloads and indexes all texts (~a few minutes):

```bash
uv run python scripts/run_ingestion.py
```

### 4. Run

**Backend** (from repo root):
```bash
uv run python -m uvicorn backend.main:app --reload
```

**Frontend** (in a separate terminal):
```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Project structure

```
backend/
  api/          # FastAPI routes (/chat/text, /chat/voice)
  conversation/ # Session management
  ingestion/    # Download → clean → chunk → embed → store pipeline
  llm/          # Claude client + system prompt
  rag/          # Vector retrieval + cross-encoder reranking
  voice/        # Whisper STT, Cartesia TTS
frontend/
  src/
    api/        # API client
    components/ # UI components
    hooks/      # useVoiceRecorder
scripts/
  run_ingestion.py   # Run the full ingestion pipeline
  inspect_corpus.py  # Debug stored chunks
tests/               # pytest suite (fully mocked)
```

## Tests

```bash
uv run pytest
```
