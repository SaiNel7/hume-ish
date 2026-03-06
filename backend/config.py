import os
from dotenv import load_dotenv

load_dotenv()

# Required for ingestion (phase 1)
OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# Required for LLM (phase 2) — validated at call time, not import time
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

# Required for voice (phase 3) — validated at call time, not import time
ELEVENLABS_API_KEY: str | None = os.getenv("ELEVENLABS_API_KEY")
PADDY_VOICE_ID: str | None = os.getenv("PADDY_VOICE_ID")

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "claude-sonnet-4-6"
TTS_MODEL = "eleven_turbo_v2_5"

CHUNK_SIZE = 512       # tokens
CHUNK_OVERLAP = 64     # tokens
TOP_K_RETRIEVE = 20    # chunks to retrieve before reranking
TOP_K_RERANK = 5       # chunks passed to LLM after reranking
MAX_HISTORY_TURNS = 20  # messages kept in session (10 exchanges)

# Server
# Comma-separated list of allowed frontend origins (no trailing slash)
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173"
).split(",")
MAX_AUDIO_BYTES: int = 10 * 1024 * 1024  # 10 MB — plenty for a short voice clip
