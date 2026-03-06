"""
FastAPI routes for the Ask Hume pipeline.

POST /chat/text   — JSON in, JSON out   (text-only, great for testing)
POST /chat/voice  — audio in, audio out (full voice pipeline)
"""

import io
from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.config import MAX_AUDIO_BYTES, TOP_K_RERANK, TOP_K_RETRIEVE
from backend.conversation.session import HumeSession
from backend.llm.claude_client import generate_response
from backend.rag.reranker import rerank
from backend.rag.retriever import retrieve
from backend.voice.stt import transcribe
from backend.voice.tts import synthesize

router = APIRouter()

# In-memory session store — fine for a single-server deployment
_sessions: dict[str, HumeSession] = {}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_or_create_session(session_id: str | None) -> HumeSession:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    session = HumeSession()
    _sessions[session.session_id] = session
    return session


def _rag_and_reply(session: HumeSession, message: str) -> tuple[str, list[str]]:
    """Run retrieve → rerank → Claude. Returns (reply_text, source_slugs)."""
    candidates = retrieve(message, top_k=TOP_K_RETRIEVE)
    top_chunks = rerank(message, candidates, top_k=TOP_K_RERANK)

    rag_context = "\n\n".join(
        f"[{i}] (source: {c['source']})\n{c['text']}"
        for i, c in enumerate(top_chunks, 1)
    )
    sources = list(dict.fromkeys(c["source"] for c in top_chunks))

    session.add_turn("user", message)
    reply = generate_response(session.history, rag_context)
    session.add_turn("assistant", reply)

    return reply, sources


# ---------------------------------------------------------------------------
# /chat/text  — JSON request / JSON response
# ---------------------------------------------------------------------------

class ChatTextRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatTextResponse(BaseModel):
    session_id: str
    reply: str
    sources: list[str]


@router.post("/chat/text", response_model=ChatTextResponse)
async def chat_text(req: ChatTextRequest) -> ChatTextResponse:
    session = _get_or_create_session(req.session_id)
    reply, sources = _rag_and_reply(session, req.message)
    return ChatTextResponse(session_id=session.session_id, reply=reply, sources=sources)


# ---------------------------------------------------------------------------
# /chat/voice — multipart audio in, MP3 audio out
# ---------------------------------------------------------------------------

@router.post("/chat/voice")
async def chat_voice(
    audio: UploadFile,
    session_id: str | None = Form(default=None),
) -> StreamingResponse:
    """
    Full voice pipeline: audio → STT → RAG + Claude → TTS → MP3

    Response headers (all must be listed in expose_headers in main.py):
      X-Session-Id  — pass back on subsequent requests for multi-turn conversation
      X-Transcript  — URL-encoded transcript of what was heard
      X-Reply       — URL-encoded text of Hume's reply (for caption display)
    """
    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio too large — maximum {MAX_AUDIO_BYTES // (1024 * 1024)} MB",
        )

    # STT
    transcript = transcribe(audio_bytes, filename=audio.filename or "audio.webm")

    # RAG + LLM
    session = _get_or_create_session(session_id)
    reply, _ = _rag_and_reply(session, transcript)

    # TTS
    mp3_bytes = synthesize(reply)

    return StreamingResponse(
        io.BytesIO(mp3_bytes),
        media_type="audio/mpeg",
        headers={
            "X-Session-Id": session.session_id,
            # URL-encode so newlines / special chars survive HTTP headers
            "X-Transcript": quote(transcript),
            "X-Reply": quote(reply),
        },
    )
