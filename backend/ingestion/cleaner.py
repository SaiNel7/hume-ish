"""
Clean and normalize raw Gutenberg text files.
Strips headers/footers, normalizes whitespace, removes hyphenation artifacts.
"""


def clean(raw_text: str) -> str:
    """Return cleaned text ready for chunking."""
    raise NotImplementedError
