"""
Persist embedded chunks into Chroma.
Collection name: "hume_corpus"
"""

from backend.ingestion.chunker import Chunk


def upsert_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    """Insert or update chunks + embeddings in the Chroma collection."""
    raise NotImplementedError
