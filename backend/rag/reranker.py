"""
Cross-encoder reranker using cross-encoder/ms-marco-MiniLM-L-6-v2.

Re-scores top-K retrieved candidates and returns the top-N most relevant.
The model is loaded once on first use (lazy singleton) since it's ~85 MB.
"""

from sentence_transformers import CrossEncoder

_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model: CrossEncoder | None = None


def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(_MODEL_NAME)
    return _model


def rerank(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    """
    Re-score candidates with the cross-encoder and return top_k results,
    sorted by descending relevance score.
    """
    if not candidates:
        return []

    model = _get_model()
    pairs = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    scored = [
        {**c, "rerank_score": float(score)}
        for c, score in zip(candidates, scores)
    ]
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_k]
