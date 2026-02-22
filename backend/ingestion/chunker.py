"""
Split cleaned text into overlapping chunks.

Strategy:
  1. Split on paragraph boundaries first.
  2. Merge paragraphs up to CHUNK_SIZE tokens.
  3. Apply CHUNK_OVERLAP token overlap between consecutive chunks.
  4. Never cut mid-sentence.

Each chunk carries metadata: {source, chunk_index}.
"""

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str       # e.g. "treatise_of_human_nature"
    chunk_index: int


def chunk_text(text: str, source: str) -> list[Chunk]:
    """Return overlapping chunks from cleaned text."""
    raise NotImplementedError
