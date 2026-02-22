# "Ask Hume" — Voice Interaction Platform Architecture
### *David Hume's philosophy. Paddy Pimblett's mouth.*

---

## The Concept

A real-time voice conversational agent that lets you debate empiricism, causality, and the problem of induction with David Hume — who inexplicably sounds like a Liverpudlian MMA fighter. Users speak, Hume responds in character using RAG over his complete works, delivered in Paddy's voice via ElevenLabs.

---

## System Architecture

```
User Mic Input
      │
      ▼
[STT: ElevenLabs]
      │
      ▼
[Conversation Manager]  ◄──── Session memory (last N turns)
      │
      ▼
[RAG Pipeline]
  ├── Query embedding (text-embedding-3-small)
  ├── Vector search over Hume corpus
  └── Top-K chunk retrieval + reranking
      │
      ▼
[LLM: Claude claude-sonnet-4-6]
  └── System prompt: "You are David Hume. Respond as him.
      Use retrieved passages to ground answers.
      Never break character. Be conversational."
      │
      ▼
[TTS: ElevenLabs Voice Clone — Paddy]
      │
      ▼
Audio output streamed to user
```

---

## Component Breakdown

### 1. STT (Speech-to-Text)
**ElevenLabs STT** (`/speech-to-text` endpoint)
- Keeps everything in one SDK
- Good accuracy, supports streaming

---

### 2. RAG Corpus — Hume's Public Domain Works

**Source texts to ingest (all on Project Gutenberg / Archive.org):**
- *A Treatise of Human Nature* (1739)
- *An Enquiry Concerning Human Understanding* (1748)
- *An Enquiry Concerning the Principles of Morals* (1751)
- *Dialogues Concerning Natural Religion* (1779, posthumous)
- *Essays, Moral, Political, and Literary* (1741)
- *My Own Life* (autobiography, 1776)

**Pipeline:**
```
Raw text → Clean + normalize → Chunk (512 tokens, 64 overlap)
        → Embed (text-embedding-3-small) → Store in vector DB
```
Chunking: split on paragraph boundaries first, then enforce 512 token max.
Never cut mid-sentence. 64 token overlap between chunks to preserve context
across boundaries. Metadata: store source book + chapter with each chunk
so retrieved passages can cite where they came from.

**Vector DB:**
**Chroma** (local, persists to CHROMA_PERSIST_DIR)

**Reranking:** Add a cross-encoder reranker (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-score top-20 chunks → pass top-5 to LLM. Dramatically improves relevance.

---

### 3. LLM — The "Brain"

**Claude API**
```python
import anthropic

client = anthropic.Anthropic()

HUME_SYSTEM_PROMPT = """
You are David Hume, the 18th century Scottish philosopher and empiricist.
You speak from direct personal conviction — you ARE Hume, not an AI playing him.
You draw on your actual writings when relevant, grounding responses in empiricist
philosophy. You're intellectually combative but good-humored. Never break character.
Keep responses conversational (2-4 sentences ideally), not lecture-length.
You have a slight wit and enjoy puncturing metaphysical pretension.

RETRIEVED CONTEXT FROM YOUR WORKS:
{rag_context}
"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    system=HUME_SYSTEM_PROMPT.format(rag_context=retrieved_chunks),
    messages=conversation_history
)
```

**Edge Case handling**
- If asked about events or ideas after 1776, note with curiosity that you cannot speak to them from experience, but reason from first principles.

---

### 4. Voice Clone — Paddy Pimblett via ElevenLabs

**Creating the clone:**
1. Gather 20–30 min of clean Paddy audio (UFC press conferences, podcast appearances, YouTube interviews — all publicly available)
2. Upload to ElevenLabs Professional Voice Clone
3. Fine-tune with a few sample sentences written in Hume's style to check cadence

**ElevenLabs TTS call:**
```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="...")

audio = client.text_to_speech.convert(
    voice_id="YOUR_PADDY_CLONE_ID",
    text=hume_response,
    model_id="eleven_turbo_v2_5",  # lowest latency
    voice_settings={
        "stability": 0.4,          # slight variation = more natural
        "similarity_boost": 0.85,
        "style": 0.2,
        "use_speaker_boost": True
    }
)
```

**Latency target:** ElevenLabs Turbo v2.5 adds ~200-400ms. Combined with STT + LLM, aim for <2.5s total response time.

---

### 5. Conversation Manager

Simple stateful object per session:
```python
class HumeSession:
    def __init__(self):
        self.history = []          # Last 10 turns (OpenAI message format)
        self.session_id = uuid4()
    
    def add_turn(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 20:  # keep last 10 exchanges
            self.history = self.history[-20:]
```

For a web app: store session in Redis or just in-memory with FastAPI.

---

## Tech Stack Summary

| Layer | Choice 
|---|---|
| Backend | **FastAPI** (Python) |
| STT | **ElevenLabs** |
| Embeddings | **OpenAI text-embedding-3-small** |
| Vector DB | **Chroma** → **Qdrant** |
| Reranker | **cross-encoder MiniLM** |
| LLM | **Claude claude-sonnet-4-6** |
| TTS | **ElevenLabs Turbo v2.5** |
| Frontend | **React + Web Audio API** |
| Hosting | **Railway / Fly.io** |

---

## Build Order (Recommended)

**RAG foundation**
- Scrape + clean 6 Hume texts
- Chunk, embed, store in Chroma
- Build retrieval function, test with plain text queries
- Validate: "What did Hume say about causation?" returns the right Treatise passages

***LLM + persona**
- Wire RAG into Claude with Hume system prompt
- Tune the prompt until responses sound genuinely like Hume
- Add conversation memory
- Test edge cases: questions outside his knowledge (20th century events), hostile prompts, etc.

**Voice**
- Create Paddy voice clone on ElevenLabs
- Integrate STT → LLM → TTS pipeline
- Optimize for latency (streaming TTS where possible)

**Frontend + polish**
- Minimal React frontend with a voice orb that pulses on speaking
- Visual waveform orb while Hume is "speaking"

## Environment Setup

Create a `.env` file in the project root — never commit this to GitHub.
```
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
OPENAI_API_KEY=sk-...          # only for text-embedding-3-small
CHROMA_PERSIST_DIR=./chroma_db
PADDY_VOICE_ID=...             # from ElevenLabs after creating the clone
```

Load in FastAPI with:
```python
from dotenv import load_dotenv
import os

load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
```

Add `.env` and `chroma_db/` to `.gitignore` immediately.
---