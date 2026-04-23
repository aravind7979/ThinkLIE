"""
Retriever — loads all chunk embeddings from embeddings/vectors.json
and retrieves top-K most similar chunks for a query vector.
"""

import json
from pathlib import Path
from typing import List, Tuple
import numpy as np

from tools.embedder import cosine_similarity

VECTORS_FILE = Path("embeddings/vectors.json")
CHUNKS_DIR = Path("knowledge/chunks")


def _load_vectors() -> List[dict]:
    """Load all stored {chunk_id, vector} pairs."""
    if not VECTORS_FILE.exists():
        return []
    return json.loads(VECTORS_FILE.read_text())


def _load_chunk(chunk_id: str) -> dict | None:
    p = CHUNKS_DIR / f"{chunk_id}.json"
    return json.loads(p.read_text()) if p.exists() else None


def retrieve_top_k(
    query_vector: List[float],
    top_k: int = 5,
    threshold: float = 0.65,
) -> Tuple[List[str], List[float], List[dict]]:
    """
    Returns:
        chunks  — list of chunk text strings
        scores  — similarity scores
        metas   — metadata dicts for each chunk
    """
    all_vectors = _load_vectors()
    if not all_vectors:
        return [], [], []

    scored = []
    for entry in all_vectors:
        score = cosine_similarity(query_vector, entry["vector"])
        if score >= threshold:
            scored.append((score, entry["chunk_id"]))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    chunks, scores, metas = [], [], []
    for score, chunk_id in top:
        chunk = _load_chunk(chunk_id)
        if chunk:
            chunks.append(chunk["text"])
            scores.append(score)
            metas.append({
                "source": chunk.get("source", "?"),
                "topic": chunk.get("topic", "?"),
                "score": round(score, 3),
            })

    return chunks, scores, metas