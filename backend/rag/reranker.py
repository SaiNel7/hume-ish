"""
Cross-encoder reranker using cross-encoder/ms-marco-MiniLM-L-6-v2.
Re-scores retrieved candidates and returns the top-K most relevant.
"""


def rerank(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    """
    Re-score candidates with the cross-encoder and return top_k results,
    sorted by descending relevance score.
    """
    raise NotImplementedError
