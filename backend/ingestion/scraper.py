"""
Download Hume's public domain texts from Project Gutenberg / Archive.org.
Saves raw .txt files to data/raw/.
"""

HUME_SOURCES = {
    "treatise_of_human_nature": "https://www.gutenberg.org/cache/epub/4705/pg4705.txt",
    "enquiry_human_understanding": "https://www.gutenberg.org/cache/epub/9662/pg9662.txt",
    "enquiry_principles_morals": "https://www.gutenberg.org/cache/epub/4320/pg4320.txt",
    "dialogues_natural_religion": "https://www.gutenberg.org/cache/epub/4583/pg4583.txt",
    "essays_moral_political": "https://www.gutenberg.org/cache/epub/36120/pg36120.txt",
    "my_own_life": "https://www.gutenberg.org/cache/epub/9011/pg9011.txt",
}


def download_all(output_dir: str = "data/raw") -> None:
    """Download all Hume texts to output_dir."""
    raise NotImplementedError
