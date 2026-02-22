import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
ELEVENLABS_API_KEY: str = os.environ["ELEVENLABS_API_KEY"]
OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
PADDY_VOICE_ID: str = os.environ["PADDY_VOICE_ID"]

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "claude-sonnet-4-6"
TTS_MODEL = "eleven_turbo_v2_5"

CHUNK_SIZE = 512       # tokens
CHUNK_OVERLAP = 64     # tokens
TOP_K_RETRIEVE = 20    # chunks to retrieve before reranking
TOP_K_RERANK = 5       # chunks passed to LLM after reranking
MAX_HISTORY_TURNS = 20 # messages kept in session (10 exchanges)
