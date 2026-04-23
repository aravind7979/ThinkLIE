"""
Indexer — reads all chunks from knowledge/chunks/,
embeds them via Gemini, and saves to embeddings/vectors.json.

Run this script whenever you add new documents:
    python tools/indexer.py
"""

import json
from pathlib import Path
import google.generativeai as genai

from tools.embedder import embed_chunks

CHUNKS_DIR = Path("knowledge/chunks")
VECTORS_FILE = Path("embeddings/vectors.json")
VECTORS_FILE.parent.mkdir(parents=True, exist_ok=True)
MAPPING_FILE = Path("embeddings/mapping.json")


def build_index():
    chunk_files = list(CHUNKS_DIR.glob("*.json"))
    if not chunk_files:
        print("No chunks found. Add documents first using ingest.py")
        return

    print(f"Indexing {len(chunk_files)} chunks...")

    chunks_data = []
    for cf in chunk_files:
        data = json.loads(cf.read_text())
        chunks_data.append(data)

    texts = [c["text"] for c in chunks_data]
    vectors = embed_chunks(texts)

    vector_store = []
    mapping = {}

    for chunk, vector in zip(chunks_data, vectors):
        entry = {
            "chunk_id": chunk["id"],
            "vector": vector,
        }
        vector_store.append(entry)
        mapping[chunk["id"]] = {
            "source": chunk["source"],
            "topic": chunk["topic"],
            "word_count": chunk.get("word_count", 0),
        }

    VECTORS_FILE.write_text(json.dumps(vector_store, indent=2))
    MAPPING_FILE.write_text(json.dumps(mapping, indent=2))

    print(f"Indexed {len(vector_store)} vectors saved to embeddings/vectors.json")


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    with open("configs/model_config.json") as f:
        MODEL_CFG = json.load(f)
    import os
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", MODEL_CFG.get("gemini_api_key", "")))
    build_index()