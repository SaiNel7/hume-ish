"""
Chat endpoint tests — all external API calls are mocked so no credits are spent.

Mocked:
  backend.api.routes.retrieve       — ChromaDB + OpenAI embeddings
  backend.api.routes.rerank         — cross-encoder reranker
  backend.api.routes.generate_response — Claude (Anthropic)
  backend.api.routes.transcribe     — OpenAI Whisper
  backend.api.routes.synthesize     — Cartesia TTS
"""

from unittest.mock import patch
from urllib.parse import unquote

import pytest
from fastapi.testclient import TestClient

from backend.main import app

# ── Fake data ──────────────────────────────────────────────────────────────────

FAKE_CHUNKS = [
    {"text": "Hume argued that causation is a habit of the mind.", "source": "treatise"},
    {"text": "Custom and habit determine our causal inferences.", "source": "enquiry"},
]
FAKE_REPLY = "Causation, according to Hume, is merely a habit of mind — not something we perceive directly."
FAKE_TRANSCRIPT = "What did Hume say about causation?"
FAKE_MP3 = b"ID3\x00" + b"\x00" * 64   # minimal plausible MP3 header

PATCH_RETRIEVE = "backend.api.routes.retrieve"
PATCH_RERANK   = "backend.api.routes.rerank"
PATCH_GENERATE = "backend.api.routes.generate_response"
PATCH_STT      = "backend.api.routes.transcribe"
PATCH_TTS      = "backend.api.routes.synthesize"


@pytest.fixture
def client():
    return TestClient(app)


# ── /health ────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── /chat/text ─────────────────────────────────────────────────────────────────

@patch(PATCH_GENERATE, return_value=FAKE_REPLY)
@patch(PATCH_RERANK,   return_value=FAKE_CHUNKS)
@patch(PATCH_RETRIEVE, return_value=FAKE_CHUNKS)
def test_chat_text_basic(mock_retrieve, mock_rerank, mock_generate, client):
    r = client.post("/chat/text", json={"message": FAKE_TRANSCRIPT})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"] == FAKE_REPLY
    assert "session_id" in body
    assert isinstance(body["sources"], list)


@patch(PATCH_GENERATE, return_value=FAKE_REPLY)
@patch(PATCH_RERANK,   return_value=FAKE_CHUNKS)
@patch(PATCH_RETRIEVE, return_value=FAKE_CHUNKS)
def test_chat_text_returns_session_id(mock_retrieve, mock_rerank, mock_generate, client):
    r = client.post("/chat/text", json={"message": "hello"})
    assert r.status_code == 200
    session_id = r.json()["session_id"]
    assert len(session_id) == 36          # UUID4


@patch(PATCH_GENERATE, return_value=FAKE_REPLY)
@patch(PATCH_RERANK,   return_value=FAKE_CHUNKS)
@patch(PATCH_RETRIEVE, return_value=FAKE_CHUNKS)
def test_chat_text_session_continuity(mock_retrieve, mock_rerank, mock_generate, client):
    """Second message with the same session_id reuses the existing session."""
    r1 = client.post("/chat/text", json={"message": "First question"})
    session_id = r1.json()["session_id"]

    r2 = client.post("/chat/text", json={"message": "Follow-up", "session_id": session_id})
    assert r2.status_code == 200
    assert r2.json()["session_id"] == session_id

    # generate_response should have been called twice and the second call
    # should have received a history containing both the first and second messages
    assert mock_generate.call_count == 2
    # call_args holds a reference to the mutable history list; by the time we
    # inspect it the second assistant reply has been appended, giving us 4 turns
    second_history = mock_generate.call_args[0][0]
    contents = [t["content"] for t in second_history]
    assert "First question" in contents   # first turn was carried over
    assert "Follow-up" in contents        # second turn was added


@patch(PATCH_GENERATE, return_value=FAKE_REPLY)
@patch(PATCH_RERANK,   return_value=FAKE_CHUNKS)
@patch(PATCH_RETRIEVE, return_value=FAKE_CHUNKS)
def test_chat_text_sources_deduped(mock_retrieve, mock_rerank, mock_generate, client):
    """Sources list should contain unique slugs only."""
    duplicate_chunks = FAKE_CHUNKS + [FAKE_CHUNKS[0]]   # treatise appears twice
    mock_retrieve.return_value = duplicate_chunks
    mock_rerank.return_value   = duplicate_chunks

    r = client.post("/chat/text", json={"message": "causation"})
    sources = r.json()["sources"]
    assert len(sources) == len(set(sources))


# ── /chat/voice ────────────────────────────────────────────────────────────────

@patch(PATCH_TTS,      return_value=FAKE_MP3)
@patch(PATCH_GENERATE, return_value=FAKE_REPLY)
@patch(PATCH_RERANK,   return_value=FAKE_CHUNKS)
@patch(PATCH_RETRIEVE, return_value=FAKE_CHUNKS)
@patch(PATCH_STT,      return_value=FAKE_TRANSCRIPT)
def test_chat_voice_success(mock_stt, mock_retrieve, mock_rerank, mock_generate, mock_tts, client):
    audio = b"\x00" * 512
    r = client.post(
        "/chat/voice",
        files={"audio": ("test.webm", audio, "audio/webm")},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/mpeg"
    assert r.content == FAKE_MP3
    assert unquote(r.headers["x-transcript"]) == FAKE_TRANSCRIPT
    assert unquote(r.headers["x-reply"]) == FAKE_REPLY
    assert "x-session-id" in r.headers


@patch(PATCH_TTS,      return_value=FAKE_MP3)
@patch(PATCH_GENERATE, return_value=FAKE_REPLY)
@patch(PATCH_RERANK,   return_value=FAKE_CHUNKS)
@patch(PATCH_RETRIEVE, return_value=FAKE_CHUNKS)
@patch(PATCH_STT,      return_value=FAKE_TRANSCRIPT)
def test_chat_voice_session_continuity(mock_stt, mock_retrieve, mock_rerank, mock_generate, mock_tts, client):
    audio = b"\x00" * 512

    r1 = client.post("/chat/voice", files={"audio": ("a.webm", audio, "audio/webm")})
    session_id = r1.headers["x-session-id"]

    r2 = client.post(
        "/chat/voice",
        files={"audio": ("b.webm", audio, "audio/webm")},
        data={"session_id": session_id},
    )
    assert r2.headers["x-session-id"] == session_id
    assert mock_generate.call_count == 2


def test_chat_voice_empty_audio(client):
    r = client.post(
        "/chat/voice",
        files={"audio": ("empty.webm", b"", "audio/webm")},
    )
    assert r.status_code == 400


def test_chat_voice_audio_too_large(client):
    big_audio = b"\x00" * (11 * 1024 * 1024)   # 11 MB > 10 MB limit
    r = client.post(
        "/chat/voice",
        files={"audio": ("big.webm", big_audio, "audio/webm")},
    )
    assert r.status_code == 413
