"""
Ingest — add new documents to your knowledge base.

Usage:
    python ingest.py --file path/to/doc.txt --topic "AI"
    python ingest.py --folder knowledge/docs/ --topic "general"

After ingesting, always run:
    python tools/indexer.py
"""

import argparse
import shutil
from pathlib import Path

from tools.chunker import load_and_chunk_file


DOCS_DIR = Path("knowledge/docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def ingest_file(filepath: str, topic: str):
    src = Path(filepath)
    if not src.exists():
        print(f"File not found: {filepath}")
        return

    dest = DOCS_DIR / src.name
    shutil.copy2(src, dest)
    print(f"Copied {src.name} to knowledge/docs/")

    chunks = load_and_chunk_file(str(dest), topic=topic)
    print(f"Created {len(chunks)} chunks for '{src.name}'")


def ingest_folder(folder: str, topic: str):
    p = Path(folder)
    files = list(p.glob("*.txt")) + list(p.glob("*.md"))
    if not files:
        print("No .txt or .md files found in folder.")
        return
    for f in files:
        ingest_file(str(f), topic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into knowledge base")
    parser.add_argument("--file", help="Single file path")
    parser.add_argument("--folder", help="Folder of files")
    parser.add_argument("--topic", default="general", help="Topic label")
    args = parser.parse_args()

    if args.file:
        ingest_file(args.file, args.topic)
    elif args.folder:
        ingest_folder(args.folder, args.topic)
    else:
        print("Usage: python ingest.py --file <path> --topic <topic>")

    print("\nNow run: python tools/indexer.py  to rebuild the vector index.")