"""
Cacher — exact-match query cache stored in cache/query_cache.json.
Prevents duplicate Gemini API calls for identical queries.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

CACHE_FILE = Path("cache/query_cache.json")
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

MAX_ENTRIES = 500


def _load() -> dict:
    return json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}


def _save(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def _key(query: str) -> str:
    return hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]


def get_cache(query: str) -> str | None:
    cache = _load()
    entry = cache.get(_key(query))
    return entry["answer"] if entry else None


def set_cache(query: str, answer: str):
    cache = _load()

    if len(cache) >= MAX_ENTRIES:
        oldest = sorted(cache.items(), key=lambda x: x[1].get("ts", ""))[0][0]
        del cache[oldest]

    cache[_key(query)] = {
        "query": query,
        "answer": answer,
        "ts": datetime.utcnow().isoformat(),
    }
    _save(cache)


def clear_cache():
    _save({})
    print("Cache cleared.")