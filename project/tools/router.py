"""
Router — reads routing/rag_rules.json and intent_rules.json
to decide what path a query should take.
"""

import json
import re
from pathlib import Path


def _load(file: str) -> dict:
    p = Path(f"routing/{file}")
    return json.loads(p.read_text()) if p.exists() else {}


def route_query(query: str) -> dict:
    rag_rules = _load("rag_rules.json")
    intent_rules = _load("intent_rules.json")
    tool_rules = _load("tool_rules.json")

    q = query.lower()

    # ── RAG decision ──────────────────────────────────────────────────────────
    use_rag = False

    skip_patterns = rag_rules.get("skip_rag_if_patterns", [])
    for pattern in skip_patterns:
        if re.search(pattern, q):
            use_rag = False
            break
    else:
        use_patterns = rag_rules.get("use_rag_if_patterns", [])
        for pattern in use_patterns:
            if re.search(pattern, q):
                use_rag = True
                break

    # ── Intent detection ──────────────────────────────────────────────────────
    intent = "general"
    for intent_name, patterns in intent_rules.get("intents", {}).items():
        for pattern in patterns:
            if re.search(pattern, q):
                intent = intent_name
                break

    # ── Tool detection ────────────────────────────────────────────────────────
    use_tool = None
    for tool_name, patterns in tool_rules.get("tools", {}).items():
        for pattern in patterns:
            if re.search(pattern, q):
                use_tool = tool_name
                break

    return {
        "use_rag": use_rag,
        "intent": intent,
        "use_tool": use_tool,
    }