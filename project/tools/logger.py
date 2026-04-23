"""
Logger — writes structured logs to logs/ directory.
Tracks: queries, RAG hits, latency, session info.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _append(filepath: str, entry: dict):
    p = Path(filepath)
    line = json.dumps(entry, ensure_ascii=False)
    with open(p, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_query(
    query: str,
    mode: str,  # "rag" | "direct" | "cache_hit"
    latency_ms: int,
    session_id: str = "default",
    sources: List[str] = None,
):
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "session": session_id,
        "query": query,
        "mode": mode,
        "latency_ms": latency_ms,
        "sources": sources or [],
    }
    _append("logs/queries.log", entry)

    if mode == "rag":
        _append("logs/rag_hits.log", {
            "ts": entry["ts"],
            "query": query,
            "sources": sources or [],
            "latency_ms": latency_ms,
        })


def log_feedback(query: str, response: str, rating: int, correction: str = ""):
    """Call this when user gives thumbs-down or correction."""
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "query": query,
        "response": response,
        "rating": rating,  # 1=good, 0=bad
        "correction": correction,
    }
    _append("feedback/user_feedback.json", entry)

    if rating == 0:
        _append("feedback/failed_queries.json", entry)