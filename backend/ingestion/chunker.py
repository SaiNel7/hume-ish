"""
Split cleaned text into overlapping chunks.

Strategy (faithful to the spec):
  1. Split on paragraph boundaries (\n\n).
  2. Any paragraph that exceeds CHUNK_SIZE tokens is further split at sentence
     boundaries — never mid-sentence.
  3. Greedily pack units (paragraphs or sentences) into a chunk up to CHUNK_SIZE.
  4. The next chunk begins by rewinding ~CHUNK_OVERLAP tokens from the end of
     the current one, preserving context across boundaries.

Each chunk carries metadata: {source, chunk_index}.
"""

import re
from dataclasses import dataclass

import tiktoken

from backend.config import CHUNK_OVERLAP, CHUNK_SIZE

_enc = tiktoken.get_encoding("cl100k_base")

# Sentence boundary: terminal punctuation followed by whitespace + capital letter.
# Deliberately simple — 18th-century prose is well-punctuated.
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z"])')


@dataclass
class Chunk:
    text: str
    source: str       # e.g. "treatise_of_human_nature"
    chunk_index: int


def _token_count(text: str) -> int:
    return len(_enc.encode(text))


def _split_sentences(paragraph: str) -> list[str]:
    parts = _SENTENCE_SPLIT_RE.split(paragraph)
    return [p.strip() for p in parts if p.strip()]


def _to_units(text: str) -> list[str]:
    """
    Break text into the smallest indivisible units for packing:
      - Whole paragraph if it fits within CHUNK_SIZE.
      - Individual sentences otherwise.
    """
    units: list[str] = []
    for para in re.split(r"\n\n+", text):
        para = para.strip()
        if not para:
            continue
        if _token_count(para) <= CHUNK_SIZE:
            units.append(para)
        else:
            units.extend(_split_sentences(para))
    return units


def chunk_text(text: str, source: str) -> list[Chunk]:
    """Return overlapping chunks from cleaned text."""
    units = _to_units(text)
    chunks: list[Chunk] = []
    chunk_index = 0
    i = 0  # index into units[]

    while i < len(units):
        # Build one chunk by greedy accumulation
        token_count = 0
        end = i  # exclusive end

        while end < len(units):
            unit_tokens = _token_count(units[end])
            if token_count + unit_tokens > CHUNK_SIZE and end > i:
                break
            token_count += unit_tokens
            end += 1

        # Guard: single unit exceeds CHUNK_SIZE — include it anyway
        if end == i:
            end = i + 1

        chunk_body = "\n\n".join(units[i:end])
        chunks.append(Chunk(text=chunk_body, source=source, chunk_index=chunk_index))
        chunk_index += 1

        # Find overlap start: walk back from `end` until we've covered ~CHUNK_OVERLAP tokens
        overlap_tokens = 0
        overlap_start = end
        for k in range(end - 1, i, -1):
            overlap_tokens += _token_count(units[k])
            if overlap_tokens >= CHUNK_OVERLAP:
                overlap_start = k
                break
        else:
            # Entire chunk shorter than CHUNK_OVERLAP — no rewind possible
            overlap_start = end

        # If no rewind happened, force advance to avoid infinite loop
        i = overlap_start if overlap_start < end else end

    return chunks
