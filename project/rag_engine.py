"""
RAG Engine - Core orchestrator for the AI system.
Routes queries → decides RAG or direct → calls Gemini → returns response.
"""

import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Optional

import google.generativeai as genai

from tools.chunker import chunk_text
from tools.embedder import embed_query, embed_chunks, cosine_similarity
from tools.retriever import retrieve_top_k
from tools.router import route_query
from tools.logger import log_query
from tools.cacher import get_cache, set_cache
from tools.tool_registry import run_tool

# ── Setup ──────────────────────────────────────────────────────────────────────

with open("configs/model_config.json") as f:
    MODEL_CFG = json.load(f)

with open("configs/rag_config.json") as f:
    RAG_CFG = json.load(f)

genai.configure(api_key=MODEL_CFG["gemini_api_key"])
model = genai.GenerativeModel(
    MODEL_CFG["model_name"],
    system_instruction=(Path("prompts/system_prompt.txt").read_text(encoding="utf-8") if Path("prompts/system_prompt.txt").exists() else None)
)

logging.basicConfig(filename="logs/errors.log", level=logging.ERROR)
Path("logs").mkdir(exist_ok=True)
Path("feedback").mkdir(exist_ok=True)


# ── Prompt Loader ──────────────────────────────────────────────────────────────

def load_prompt(name: str) -> str:
    path = Path(f"prompts/{name}.txt")
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ── Main Query Function ────────────────────────────────────────────────────────

def ask(query: str, session_id: str = "default") -> dict:
    start = time.time()

    # 1. Check cache first
    cached = get_cache(query)
    if cached:
        log_query(query, "cache_hit", 0, session_id)
        return {"answer": cached, "source": "cache", "latency_ms": 0}

    # 2. Route the query
    route = route_query(query)
    use_rag = route["use_rag"]
    use_tool = route["use_tool"]

    context_block = ""
    sources = []
    
    # 2.5 Optional Tool Intervention
    tool_result = ""
    if use_tool:
        tool_result = run_tool(use_tool, query)

    # 3. RAG path — retrieve + inject context
    if use_rag:
        try:
            q_vec = embed_query(query)
            chunks, scores, metas = retrieve_top_k(q_vec, RAG_CFG["top_k"], RAG_CFG["similarity_threshold"])
            if chunks:
                context_block = "\n\n---\n\n".join(
                    f"[Source: {m.get('source','?')} | Topic: {m.get('topic','?')}]\n{c}"
                    for c, m in zip(chunks, metas)
                )
                sources = [m.get("source", "?") for m in metas]
        except Exception as e:
            logging.error(f"RAG retrieval error: {e}")

    # 4. Build final prompt
    if use_rag and context_block:
        template = load_prompt("rag_prompt")
        final_prompt = template.replace("{{CONTEXT}}", context_block).replace("{{QUERY}}", query)
    else:
        template = load_prompt("no_rag_prompt")
        final_prompt = template.replace("{{QUERY}}", query)
        
    if tool_result:
        final_prompt += f"\n\nNote: A tool was queried to help answer this. The tool returned: {tool_result}\nUse this tool output to accurately answer the question."

    # 5. Call Gemini
    try:
        response = model.generate_content(
            final_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=MODEL_CFG["max_tokens"],
                temperature=MODEL_CFG["temperature"],
            )
        )
        answer = response.text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        answer = "I encountered an error generating a response. Please try again."

    latency = round((time.time() - start) * 1000)

    # 6. Cache + log
    set_cache(query, answer)
    log_query(query, "rag" if use_rag else "direct", latency, session_id, sources)

    return {
        "answer": answer,
        "source": "rag" if (use_rag and context_block) else "direct",
        "sources_used": sources,
        "latency_ms": latency,
        "route": route,
    }


# ── CLI Interface ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("AI System Ready. Type 'exit' to quit.\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        result = ask(q)
        print(f"\nAI [{result['source']}]: {result['answer']}")
        if result.get("sources_used"):
            print(f"   Sources: {', '.join(result['sources_used'])}")
        print(f"   {result['latency_ms']}ms\n")