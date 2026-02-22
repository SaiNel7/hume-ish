"""
Clean and normalize raw Gutenberg text files.

Steps:
  1. Strip Gutenberg preamble/license (content outside *** START/END *** markers).
  2. Dehyphenate words split across line boundaries ("natu-\nral" → "natural").
  3. Collapse soft line breaks inside paragraphs (single \n → space).
  4. Normalize paragraph breaks to exactly two newlines.
  5. Collapse runs of spaces.
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

    # 2. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Dehyphenate: word-\nword → wordword  (18th-century printing artifact)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # 4. Collapse soft line breaks within a paragraph (single \n → space)
    #    A "hard" paragraph break is two or more consecutive \n.
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # 5. Normalize paragraph breaks to exactly two newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 6. Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    return text.strip()
