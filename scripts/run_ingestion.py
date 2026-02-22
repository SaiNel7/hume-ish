"""
CLI entrypoint for the full ingestion pipeline:
  download → clean → chunk → embed → store

Usage:
    uv run python scripts/run_ingestion.py
"""

from backend.ingestion.scraper import download_all
from backend.ingestion.cleaner import clean
from backend.ingestion.chunker import chunk_text
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.store import upsert_chunks

DATA_DIR = "data/raw"


def run():
    print("Step 1: Downloading Hume texts...")
    download_all(DATA_DIR)

    print("Step 2: Cleaning, chunking, embedding, and storing...")
    # TODO: iterate over downloaded files
    raise NotImplementedError


if __name__ == "__main__":
    run()
