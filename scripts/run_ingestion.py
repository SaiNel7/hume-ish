"""
CLI entrypoint for the full ingestion pipeline:
  download → clean → chunk → embed → store

Usage (from project root):
    uv run python scripts/run_ingestion.py
"""

import os
import sys

# Ensure project root is on the path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.ingestion.chunker import chunk_text
from backend.ingestion.cleaner import clean
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.scraper import HUME_SOURCES, LOCAL_SOURCES, download_all
from backend.ingestion.store import collection_count, upsert_chunks

DATA_DIR = "data/raw"


def _process_book(key: str, path: str) -> int:
    """Clean → chunk → embed → store one book. Returns chunk count."""
    if not os.path.exists(path):
        print(f"  [skip] {key}: file not found at {path}")
        return 0

    print(f"\n  [{key}]")

    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()

    cleaned = clean(raw)
    print(f"    cleaned  : {len(cleaned):,} chars")

    chunks = chunk_text(cleaned, source=key)
    print(f"    chunks   : {len(chunks)}")

    if not chunks:
        print("    [warning] no chunks produced — skipping")
        return 0

    print(f"    embedding {len(chunks)} chunks ...")
    embeddings = embed_chunks(chunks)

    print(f"    storing  ...")
    upsert_chunks(chunks, embeddings)
    return len(chunks)


def run() -> None:
    # ------------------------------------------------------------------
    # Step 1: Download Gutenberg texts
    # ------------------------------------------------------------------
    print("\n=== Step 1: Downloading Hume texts ===")
    download_all(DATA_DIR)

    # ------------------------------------------------------------------
    # Step 2: Process all books (downloaded + local)
    # ------------------------------------------------------------------
    print("\n=== Step 2: Processing books ===")
    total_chunks = 0

    # Gutenberg books (paths inferred from download dir)
    for key in HUME_SOURCES:
        total_chunks += _process_book(key, os.path.join(DATA_DIR, f"{key}.txt"))

    # Local-only books (paths explicit in LOCAL_SOURCES)
    for key, path in LOCAL_SOURCES.items():
        total_chunks += _process_book(key, path)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    all_books = len(HUME_SOURCES) + len(LOCAL_SOURCES)
    print(f"\n=== Done ===")
    print(f"  Books processed : {all_books}")
    print(f"  Chunks this run : {total_chunks}")
    print(f"  Chroma total    : {collection_count()}")


if __name__ == "__main__":
    run()
