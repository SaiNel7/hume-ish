"""
Clean and normalize raw Gutenberg text files.

Steps:
  1. Strip Gutenberg preamble/license (content outside *** START/END *** markers).
  2. Strip table of contents (CONTENTS block near the top, up to first prose paragraph).
  3. Dehyphenate words split across line boundaries ("natu-\nral" → "natural").
  4. Collapse soft line breaks inside paragraphs (single \n → space).
  5. Normalize paragraph breaks to exactly two newlines.
  6. Collapse runs of spaces.
"""

import re

# Gutenberg content delimiters — handle slight wording variations
_START_RE = re.compile(
    r"\*{3}\s*START\s+OF\s+(?:THE|THIS)\s+PROJECT\s+GUTENBERG[^\n]*\n",
    re.IGNORECASE,
)
_END_RE = re.compile(
    r"\*{3}\s*END\s+OF\s+(?:THE|THIS)\s+PROJECT\s+GUTENBERG[^\n]*",
    re.IGNORECASE,
)

# "CONTENTS" as a standalone paragraph, within the first 20 000 chars
_TOC_RE = re.compile(r"\n\n\s*CONTENTS\s*\n\n", re.IGNORECASE)


def _strip_toc(text: str) -> str:
    """
    Remove the table of contents if present near the top of the text.

    Finds a CONTENTS heading within the first 20 000 chars, then scans
    forward to the first paragraph that looks like actual prose:
      - longer than 200 characters
      - contains lowercase letters (not an all-caps heading/listing)
      - contains at least one sentence-ending punctuation mark

    Everything before that paragraph (title page + TOC) is discarded.
    Books without a CONTENTS block are returned unchanged.
    """
    match = _TOC_RE.search(text[:20_000])
    if not match:
        return text

    after_toc = text[match.end():]
    paragraphs = [p.strip() for p in re.split(r"\n\n+", after_toc) if p.strip()]

    for i, para in enumerate(paragraphs):
        if (
            len(para) > 200
            and re.search(r"[a-z]{3,}", para)       # has lowercase → not all-caps listing
            and re.search(r"[.!?]", para)            # has sentence-ending punctuation
        ):
            return "\n\n".join(paragraphs[i:])

    return text  # fallback: return unchanged if heuristic finds nothing


def clean(raw_text: str) -> str:
    """Return cleaned text ready for chunking."""
    text = raw_text

    # 1. Strip Gutenberg header
    start_match = _START_RE.search(text)
    if start_match:
        text = text[start_match.end():]

    # 1b. Strip Gutenberg footer
    end_match = _END_RE.search(text)
    if end_match:
        text = text[: end_match.start()]

    # 2. Strip table of contents
    text = _strip_toc(text)

    # 3. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 4. Dehyphenate: word-\nword → wordword  (18th-century printing artifact)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # 5. Collapse soft line breaks within a paragraph (single \n → space)
    #    A "hard" paragraph break is two or more consecutive \n.
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # 6. Normalize paragraph breaks to exactly two newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 7. Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    return text.strip()
