"""
Query the Chroma collection and return the top-K most similar chunks.
"""


def retrieve(query: str, top_k: int) -> list[dict]:
    """
    Embed the query and return top_k chunks from Chroma.
    Each result: {"text": str, "source": str, "chunk_index": int, "score": float}
    """
    raise NotImplementedError
