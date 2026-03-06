"""
Query the Chroma collection and return the top-K most similar chunks.

Uses the same OpenAI embedding model as ingestion so the vector space matches.
"""

import chromadb
from openai import OpenAI

from backend.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL, OPENAI_API_KEY

_openai = OpenAI(api_key=OPENAI_API_KEY)
_COLLECTION_NAME = "hume_corpus"


def _collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_collection(_COLLECTION_NAME)


def retrieve(query: str, top_k: int) -> list[dict]:
    """
    Embed query and return top_k chunks from Chroma.
    Each result: {"text": str, "source": str, "chunk_index": int, "score": float}
    """
    # Embed the query with the same model used at ingestion time
    embedding_response = _openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
    )
    query_embedding = embedding_response.data[0].embedding

    results = _collection().query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Chroma cosine space returns distance = 1 - cosine_similarity
    return [
        {
            "text": doc,
            "source": meta["source"],
            "chunk_index": int(meta["chunk_index"]),
            "score": round(1.0 - dist, 4),
        }
        for doc, meta, dist in zip(docs, metas, distances)
    ]
