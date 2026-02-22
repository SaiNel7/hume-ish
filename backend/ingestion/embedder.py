"""
Embed chunks using OpenAI text-embedding-3-small.
Batches requests to respect rate limits.
"""

from backend.ingestion.chunker import Chunk


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """Return one embedding vector per chunk (same order)."""
    raise NotImplementedError
