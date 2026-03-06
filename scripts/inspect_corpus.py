"""
Inspect cleaned text and stored chunks for a given book.

Usage:
    uv run python scripts/inspect_corpus.py <slug> [--chars N] [--chunks N]

Examples:
    uv run python scripts/inspect_corpus.py treatise_of_human_nature
    uv run python scripts/inspect_corpus.py my_own_life --chars 3000 --chunks 5
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb

from backend.config import CHROMA_PERSIST_DIR
from backend.ingestion.cleaner import clean
from backend.ingestion.scraper import HUME_SOURCES, LOCAL_SOURCES

ALL_SOURCES = {
    **{k: f"data/raw/{k}.txt" for k in HUME_SOURCES},
    **LOCAL_SOURCES,
}


def show_cleaned(slug: str, chars: int) -> None:
    path = ALL_SOURCES.get(slug)
    if not path or not os.path.exists(path):
        print(f"[error] No file found for slug '{slug}'")
        return

    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()

    cleaned = clean(raw)

    print(f"\n{'='*60}")
    print(f"CLEANED TEXT — {slug}  ({len(cleaned):,} chars total)")
    print(f"{'='*60}")
    print(f"\n--- first {chars} chars ---\n")
    print(cleaned[:chars])
    print(f"\n--- last {chars} chars ---\n")
    print(cleaned[-chars:])


def show_chunks(slug: str, n: int) -> None:
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        collection = client.get_collection("hume_corpus")
    except Exception:
        print("[error] Chroma collection 'hume_corpus' not found — run ingestion first")
        return

    results = collection.get(
        where={"source": slug},
        limit=n,
        include=["documents", "metadatas"],
    )

    docs = results.get("documents") or []
    metas = results.get("metadatas") or []

    print(f"\n{'='*60}")
    print(f"STORED CHUNKS — {slug}  (showing first {len(docs)} of collection)")
    print(f"{'='*60}")

    for i, (doc, meta) in enumerate(zip(docs, metas)):
        print(f"\n--- chunk {meta.get('chunk_index')} ---")
        print(doc[:500])
        if len(doc) > 500:
            print(f"  ... [{len(doc) - 500} more chars]")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", choices=list(ALL_SOURCES.keys()))
    parser.add_argument("--chars", type=int, default=2000, help="chars of cleaned text to show")
    parser.add_argument("--chunks", type=int, default=3, help="chunks to show from Chroma")
    args = parser.parse_args()

    show_cleaned(args.slug, args.chars)
    show_chunks(args.slug, args.chunks)


if __name__ == "__main__":
    main()
