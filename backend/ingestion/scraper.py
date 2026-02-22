"""
Download Hume's public domain texts from Project Gutenberg.
Saves raw .txt files to data/raw/.
Skips files that already exist so the script is safe to re-run.
"""

import os
import httpx

HUME_SOURCES = {
    "treatise_of_human_nature":    "https://www.gutenberg.org/cache/epub/4705/pg4705.txt",
    "enquiry_human_understanding": "https://www.gutenberg.org/cache/epub/9662/pg9662.txt",
    "enquiry_principles_morals":   "https://www.gutenberg.org/cache/epub/4320/pg4320.txt",
    "dialogues_natural_religion":  "https://www.gutenberg.org/cache/epub/4583/pg4583.txt",
    "essays_moral_political":      "https://www.gutenberg.org/cache/epub/36120/pg36120.txt",
    "my_own_life":                 "https://www.gutenberg.org/cache/epub/9011/pg9011.txt",
}


def download_all(output_dir: str = "data/raw") -> None:
    """Download all Hume texts into output_dir as {key}.txt files."""
    os.makedirs(output_dir, exist_ok=True)

    for key, url in HUME_SOURCES.items():
        dest = os.path.join(output_dir, f"{key}.txt")
        if os.path.exists(dest):
            print(f"  [skip] {key} already downloaded")
            continue

        print(f"  [download] {key} ...")
        try:
            with httpx.Client(follow_redirects=True, timeout=60) as client:
                response = client.get(url)
                response.raise_for_status()

            with open(dest, "w", encoding="utf-8", errors="replace") as f:
                f.write(response.text)

            print(f"  [ok] {key} → {dest}")
        except httpx.HTTPError as exc:
            print(f"  [error] {key}: {exc}")
            raise
