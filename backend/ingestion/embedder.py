"""
Embed chunks using OpenAI text-embedding-3-small.
Requests are batched (100 texts per call) to stay well within API limits.
"""

from openai import OpenAI

from backend.config import EMBEDDING_MODEL, OPENAI_API_KEY
from backend.ingestion.chunker import Chunk

_client = OpenAI(api_key=OPENAI_API_KEY)

_BATCH_SIZE = 100


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """Return one embedding vector per chunk, preserving input order."""
    if not chunks:
        return []

    texts = [chunk.text for chunk in chunks]
    embeddings: list[list[float]] = []

    for batch_start in range(0, len(texts), _BATCH_SIZE):
        batch = texts[batch_start : batch_start + _BATCH_SIZE]
        response = _client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        # Sort by index to guarantee order matches input
        batch_embeddings = [
            item.embedding
            for item in sorted(response.data, key=lambda x: x.index)
        ]
        embeddings.extend(batch_embeddings)

    return embeddings
