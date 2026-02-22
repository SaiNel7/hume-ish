"""
Persist embedded chunks into Chroma (local, persistent).

Collection : "hume_corpus"
Distance   : cosine  (appropriate for normalised embedding vectors)
Document ID: "{source}__{chunk_index}"  — deterministic so re-runs upsert cleanly
"""

import chromadb

from backend.config import CHROMA_PERSIST_DIR
from backend.ingestion.chunker import Chunk

_COLLECTION_NAME = "hume_corpus"


def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    """Insert or update chunks + embeddings in the Chroma collection."""
    if not chunks:
        return

    collection = _get_collection()

    ids = [f"{c.source}__{c.chunk_index}" for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [{"source": c.source, "chunk_index": c.chunk_index} for c in chunks]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def collection_count() -> int:
    """Return the total number of chunks currently stored."""
    return _get_collection().count()
