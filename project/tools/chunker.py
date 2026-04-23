"""
Chunker — splits raw documents into clean chunks.
Supports overlap to avoid context loss at chunk boundaries.
Saves chunks to knowledge/chunks/ and metadata to metadata/doc_info.json
"""

import json
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict


CHUNKS_DIR = Path("knowledge/chunks")
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

META_FILE = Path("metadata/doc_info.json")
META_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_meta() -> List[dict]:
    return json.loads(META_FILE.read_text()) if META_FILE.exists() else []


def _save_meta(meta: List[dict]):
    META_FILE.write_text(json.dumps(meta, indent=2))


def chunk_text(
    text: str,
    source: str,
    topic: str = "general",
    chunk_size: int = 500,
    overlap: int = 80,
) -> List[Dict]:
    """
    Split text into overlapping chunks.
    Returns list of chunk dicts with id, text, source, topic.
    Also persists chunks to disk.
    """
    # Clean text
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    words = text.split()

    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i: i + chunk_size]
        chunk_text_str = " ".join(chunk_words)
        chunk_id = str(uuid.uuid4())[:8]

        chunk = {
            "id": chunk_id,
            "text": chunk_text_str,
            "source": source,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
            "word_count": len(chunk_words),
        }
        chunks.append(chunk)

        # Save chunk to file
        chunk_file = CHUNKS_DIR / f"{chunk_id}.json"
        chunk_file.write_text(json.dumps(chunk, indent=2))

        i += chunk_size - overlap  # overlap step

    # Update metadata
    meta = _load_meta()
    meta.append({
        "source": source,
        "topic": topic,
        "chunk_count": len(chunks),
        "chunk_ids": [c["id"] for c in chunks],
        "indexed_at": datetime.utcnow().isoformat(),
    })
    _save_meta(meta)

    return chunks


def load_and_chunk_file(filepath: str, topic: str = "general") -> List[Dict]:
    """Convenience: read a .txt or .md file and chunk it."""
    p = Path(filepath)
    text = p.read_text(encoding="utf-8")
    
    with open("configs/rag_config.json") as f:
        rag_cfg = json.load(f)
    chunk_sz = rag_cfg.get("chunk_size", 1000)
    olap = rag_cfg.get("chunk_overlap", 150)
    
    return chunk_text(text, source=p.name, topic=topic, chunk_size=chunk_sz, overlap=olap)