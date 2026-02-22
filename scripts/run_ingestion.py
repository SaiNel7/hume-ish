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
from backend.ingestion.scraper import HUME_SOURCES, download_all
from backend.ingestion.store import collection_count, upsert_chunks

DATA_DIR = "data/raw"


def run() -> None:
    # ------------------------------------------------------------------
    # Step 1: Download
    # ------------------------------------------------------------------
    print("\n=== Step 1: Downloading Hume texts ===")
    download_all(DATA_DIR)

    # ------------------------------------------------------------------
    # Step 2: Clean → chunk → embed → store  (per book)
    # ------------------------------------------------------------------
    print("\n=== Step 2: Processing books ===")
    total_chunks = 0

    for key in HUME_SOURCES:
        path = os.path.join(DATA_DIR, f"{key}.txt")
        if not os.path.exists(path):
            print(f"  [skip] {key}: file not found after download")
            continue

        print(f"\n  [{key}]")

        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()

        cleaned = clean(raw)
        print(f"    cleaned  : {len(cleaned):,} chars")

        chunks = chunk_text(cleaned, source=key)
        print(f"    chunks   : {len(chunks)}")

        if not chunks:
            print("    [warning] no chunks produced — skipping")
            continue

        print(f"    embedding {len(chunks)} chunks ...")
        embeddings = embed_chunks(chunks)

        print(f"    storing  ...")
        upsert_chunks(chunks, embeddings)
        total_chunks += len(chunks)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n=== Done ===")
    print(f"  Books processed : {len(HUME_SOURCES)}")
    print(f"  Chunks this run : {total_chunks}")
    print(f"  Chroma total    : {collection_count()}")


if __name__ == "__main__":
    run()
