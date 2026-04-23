"""
Embedder — uses Gemini's embedding model to convert text → vectors.
Also handles caching embeddings to avoid redundant API calls.
"""

import json
import hashlib
from pathlib import Path
from typing import List
import numpy as np
import google.generativeai as genai


EMBED_CACHE_DIR = Path("cache/embedding_cache")
EMBED_CACHE_DIR.mkdir(parents=True, exist_ok=True)

import os
from dotenv import load_dotenv

load_dotenv()
with open("configs/model_config.json") as f:
    MODEL_CFG = json.load(f)
EMBED_MODEL = MODEL_CFG.get("embedding_model", "models/embedding-001")
API_KEY = os.getenv("GEMINI_API_KEY", MODEL_CFG.get("gemini_api_key"))
genai.configure(api_key=API_KEY)
EMBED_MODEL = MODEL_CFG.get("embedding_model", "models/embedding-001")


def _cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _load_cached(key: str) -> List[float] | None:
    p = EMBED_CACHE_DIR / f"{key}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _save_cached(key: str, vector: List[float]):
    p = EMBED_CACHE_DIR / f"{key}.json"
    p.write_text(json.dumps(vector))


def embed_query(text: str) -> List[float]:
    """Embed a single query string."""
    key = _cache_key(text)
    cached = _load_cached(key)
    if cached:
        return cached

    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_query"
    )
    vector = result["embedding"]
    _save_cached(key, vector)
    return vector


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """Embed a list of document chunks."""
    vectors = []
    for chunk in chunks:
        key = _cache_key(chunk)
        cached = _load_cached(key)
        if cached:
            vectors.append(cached)
            continue
        try:
            result = genai.embed_content(
                model=EMBED_MODEL,
                content=chunk,
                task_type="retrieval_document"
            )
            v = result["embedding"]
            _save_cached(key, v)
        except Exception as e:
            # Fallback zero vector if it fails to embed
            print(f"Failed to embed chunk. {e}")
            v = [0.0] * 768 # Approximate default for some generic embedders. Better to just pass or raise
            raise e
        vectors.append(v)
    return vectors


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a, b = np.array(v1), np.array(v2)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom != 0 else 0.0