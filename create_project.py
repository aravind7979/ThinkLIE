import os
import json

base_dir = "C:\\ThinkLIE\\project"

dirs = [
    "configs",
    "knowledge/docs",
    "knowledge/chunks",
    "knowledge/domain",
    "embeddings",
    "metadata",
    "routing",
    "prompts",
    "cache/embedding_cache",
    "logs",
    "feedback",
    "tools",
    "evaluation"
]

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

files = {}

files["requirements.txt"] = """google-generativeai>=0.5.0
numpy>=1.24.0
pathlib2>=2.3.7
"""

files["configs/model_config.json"] = """{
  "gemini_api_key": "AIzaSyDRi4q78FR1ekk3SkV4eDRiry_Y3D6JDn4",
  "model_name": "gemini-1.5-pro",
  "max_tokens": 8192,
  "temperature": 0.2,
  "embedding_model": "models/embedding-001"
}"""

files["configs/rag_config.json"] = """{
  "top_k": 7,
  "similarity_threshold": 0.65,
  "chunk_size": 1000,
  "chunk_overlap": 150,
  "max_context_chars": 32000
}"""

files["routing/rag_rules.json"] = """{
  "use_rag_if_patterns": [
    "what is .*(in our|in the|according to|based on)",
    "explain .*(concept|term|definition|topic)",
    "how does .*(work|function|operate)",
    "tell me about",
    "summarize",
    "describe",
    "what are the .*(steps|rules|guidelines|requirements)",
    "find|search|look up",
    "latest|recent|current",
    "internal|our|company|project",
    "document|report|paper|article"
  ],
  "skip_rag_if_patterns": [
    "^(what is )?\\\\d+[\\\\\\\\+\\\\\\\\-\\\\\\\\*\\\\\\\\/]\\\\d+",
    "calculate|compute|solve|math",
    "translate .* to",
    "write a (poem|story|joke|haiku)",
    "what (time|day|date) is it",
    "hello|hi|hey|thanks|thank you"
  ]
}"""

files["routing/intent_rules.json"] = """{
  "intents": {
    "definition": [
      "what is", "define", "meaning of", "definition"
    ],
    "explanation": [
      "how does", "explain", "walk me through", "describe how"
    ],
    "comparison": [
      "difference between", "compare", "vs", "versus", "better"
    ],
    "summary": [
      "summarize", "tldr", "brief overview", "key points"
    ],
    "troubleshoot": [
      "error", "not working", "issue", "problem", "fix", "debug"
    ],
    "list": [
      "list", "give me", "what are", "enumerate", "examples of"
    ],
    "opinion": [
      "should i", "recommend", "best way", "advice", "suggest"
    ],
    "factual": [
      "who", "when", "where", "which year", "founded"
    ]
  }
}"""

files["routing/tool_rules.json"] = """{
  "tools": {
    "calculator": [
      "calculate", "compute", "\\\\d+\\\\s*[\\\\+\\\\-\\\\*\\\\/]\\\\s*\\\\d+", "percent of", "square root"
    ],
    "datetime": [
      "current time", "today's date", "what day is", "what time"
    ],
    "web_search": [
      "latest news", "current price", "today.*stock", "breaking"
    ]
  }
}"""

files["prompts/rag_prompt.txt"] = """You are an advanced AI assistant, equipped with detailed domain knowledge via provided context. Think deeply and respond with extreme precision, depth, and clarity, akin to a senior expert systematically breaking down a topic.

CONTEXT FROM KNOWLEDGE BASE:
{{CONTEXT}}

USER QUESTION:
{{QUERY}}

INSTRUCTIONS:
1. Ground your response using the provided context as your primary source of truth.
2. If the context covers the question completely, be exact, structural, and complete. Use formatting like bullet points, bolding, and step-by-step guides where applicable.
3. If the context is only partially relevant, state what is known from the context, and supplement it intelligently with your own broad training data while distinguishing between the two sources.
4. If the context is irrelevant, politely mention it and answer fully from your own knowledge.
5. Provide actionable insights, edge cases, or deep-dive technical explanations wherever possible to ensure the highest quality response.
6. Absolutely no fabrication or unverified claims. Do not hallucinate.

Answer thoroughly and professionally:"""

files["prompts/no_rag_prompt.txt"] = """You are a highly capable AI expert. Answer questions with maximum precision, depth, and clarity — analogous to a top-tier engineer, scientist, or analyst.

USER QUESTION:
{{QUERY}}

INSTRUCTIONS:
1. Provide a direct, confident answer upfront, structurally breaking down the response.
2. Explain the "why" and "how"—add comprehensive reasoning, historical context, or technical details depending on the domain.
3. Use code blocks, math formatting, bullet points, or markdown tables when they aid comprehension.
4. If a query is ambiguous, consider the most plausible interpretations and explicitly clarify your assumptions.
5. If you do not know the answer or lack confidence on an edge case, state it clearly rather than guessing.

Answer:"""

files["prompts/system_prompt.txt"] = """You are a state-of-the-art AI assistant, leveraging RAG-based domain retrieval to provide hyper-accurate, sophisticated answers.

Core Maxims:
- Depth & Rigor: Do not stop at surface-level. Deliver exhaustive insights.
- Absolute Honesty: Distinguish clearly between given facts and general knowledge.
- Structured Formatting: Output highly readable markdown.
- Efficient: Avoid unnecessary conversational filler. Just deliver the value.
"""

files["metadata/tags.json"] = """{
  "topics": [
    "AI",
    "machine-learning",
    "databases",
    "python",
    "general",
    "product",
    "internal"
  ],
  "importance_levels": {
    "critical": 3,
    "important": 2,
    "normal": 1,
    "archive": 0
  }
}"""

files["metadata/source_map.json"] = """{
  "_comment": "Maps source filenames to their origin and importance",
  "example_doc.txt": {
    "origin": "internal",
    "url": null,
    "importance": "normal",
    "added_by": "admin"
  }
}"""

files["metadata/doc_info.json"] = """[]"""

files["evaluation/test_queries.json"] = """[
  {
    "id": "eval_001",
    "query": "What is RAG in AI systems?",
    "expected_keywords": ["retrieval", "augmented", "generation", "vector", "context"],
    "should_use_rag": true,
    "category": "definition"
  },
  {
    "id": "eval_002",
    "query": "What is 25 * 4?",
    "expected_answer": "100",
    "should_use_rag": false,
    "category": "math"
  },
  {
    "id": "eval_003",
    "query": "Explain how embeddings work",
    "expected_keywords": ["vector", "similarity", "semantic", "representation"],
    "should_use_rag": true,
    "category": "explanation"
  },
  {
    "id": "eval_004",
    "query": "What are the steps to ingest a document?",
    "expected_keywords": ["chunk", "embed", "index", "store"],
    "should_use_rag": true,
    "category": "list"
  },
  {
    "id": "eval_005",
    "query": "Hello, how are you?",
    "expected_keywords": ["hello", "help"],
    "should_use_rag": false,
    "category": "greeting"
  }
]"""

files["tools/__init__.py"] = """# tools package"""

files["tools/router.py"] = '''"""
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
    }'''

files["tools/embedder.py"] = '''"""
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

with open("configs/model_config.json") as f:
    MODEL_CFG = json.load(f)
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
    return float(np.dot(a, b) / denom) if denom != 0 else 0.0'''

files["tools/chunker.py"] = '''"""
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
    text = re.sub(r"\\n{3,}", "\\n\\n", text.strip())
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
    
    return chunk_text(text, source=p.name, topic=topic, chunk_size=chunk_sz, overlap=olap)'''

files["tools/retriever.py"] = '''"""
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

    return chunks, scores, metas'''

files["tools/indexer.py"] = '''"""
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
    genai.configure(api_key=MODEL_CFG["gemini_api_key"])
    build_index()'''

files["tools/logger.py"] = '''"""
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
        f.write(line + "\\n")


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
        _append("feedback/failed_queries.json", entry)'''

files["tools/cacher.py"] = '''"""
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
    print("Cache cleared.")'''

files["tools/tool_registry.py"] = '''"""
Tool Registry — defines and executes external tool calls.
Add new tools here as your system grows.
"""

import datetime
import math


REGISTRY = {}


def tool(name: str):
    """Decorator to register a tool function."""
    def decorator(fn):
        REGISTRY[name] = fn
        return fn
    return decorator


@tool("calculator")
def calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


@tool("datetime")
def get_datetime(query: str = "") -> str:
    """Return current date and time."""
    now = datetime.datetime.now()
    return f"Current date/time: {now.strftime('%A, %B %d %Y at %H:%M:%S')}"


def run_tool(name: str, input_text: str) -> str:
    if name not in REGISTRY:
        return f"Tool '{name}' not found."
    return REGISTRY[name](input_text)


def list_tools() -> list:
    return list(REGISTRY.keys())'''

files["tools/feedback_analyzer.py"] = '''"""
Feedback Analyzer — reads feedback/user_feedback.json and
failed_queries.json to produce actionable improvement insights.

Usage:
    python tools/feedback_analyzer.py
"""

import json
from pathlib import Path
from collections import Counter


FEEDBACK_FILE = Path("feedback/user_feedback.json")
FAILED_FILE = Path("feedback/failed_queries.json")


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    return [json.loads(l) for l in lines if l.strip()]


def analyze():
    feedback = _load_jsonl(FEEDBACK_FILE)
    failed = _load_jsonl(FAILED_FILE)

    if not feedback:
        print("No feedback collected yet.")
        return

    total = len(feedback)
    good = sum(1 for f in feedback if f.get("rating") == 1)
    bad = total - good

    print(f"\\nFeedback Summary")
    print(f"   Total responses rated : {total}")
    print(f"   Good                  : {good} ({good/total:.0%})")
    print(f"   Bad                   : {bad} ({bad/total:.0%})")

    if failed:
        print(f"\\nFailed Queries ({len(failed)} total):")
        for i, f in enumerate(failed[-10:], 1):
            print(f"   {i}. {f['query'][:80]}")
            if f.get("correction"):
                print(f"      Correction: {f['correction'][:80]}")

    if failed:
        words = []
        for f in failed:
            words.extend(f["query"].lower().split())
        common = Counter(words).most_common(10)
        keywords = [w for w, _ in common if len(w) > 4]
        print(f"\\nCommon words in failed queries: {keywords[:6]}")
        print("   Consider adding documents on these topics to your knowledge base.\\n")


if __name__ == "__main__":
    analyze()'''

files["ingest.py"] = '''"""
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

    print("\\nNow run: python tools/indexer.py  to rebuild the vector index.")'''

files["evaluation/evaluator.py"] = '''"""
Evaluator — runs test_queries.json against the live system
and scores accuracy, RAG routing correctness, and keyword coverage.

Usage:
    python evaluation/evaluator.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from rag_engine import ask


TEST_FILE = Path("evaluation/test_queries.json")
RESULTS_FILE = Path("evaluation/results.json")


def run_eval():
    tests = json.loads(TEST_FILE.read_text())
    results = []
    passed = 0

    print(f"\\nRunning {len(tests)} eval queries...\\n")
    print("-" * 60)

    for t in tests:
        query = t["query"]
        result = ask(query)

        answer = result["answer"].lower()
        used_rag = result["source"] == "rag"
        expected_rag = t.get("should_use_rag", False)

        keywords = t.get("expected_keywords", [])
        keyword_hits = [kw for kw in keywords if kw.lower() in answer]
        keyword_score = len(keyword_hits) / len(keywords) if keywords else 1.0

        exact_match = True
        if "expected_answer" in t:
            exact_match = t["expected_answer"].lower() in answer

        routing_correct = (used_rag == expected_rag)
        passed_test = keyword_score >= 0.6 and exact_match and routing_correct
        if passed_test:
            passed += 1

        status = "PASS" if passed_test else "FAIL"
        print(f"{status} [{t['id']}] {query[:50]}")
        print(f"   RAG: expected={expected_rag} got={used_rag} {'OK' if routing_correct else 'WRONG'}")
        print(f"   Keywords: {keyword_hits}/{keywords} ({keyword_score:.0%})")
        print(f"   Latency: {result['latency_ms']}ms\\n")

        results.append({
            "id": t["id"],
            "query": query,
            "passed": passed_test,
            "keyword_score": keyword_score,
            "routing_correct": routing_correct,
            "latency_ms": result["latency_ms"],
            "answer_preview": result["answer"][:200],
        })

    total = len(tests)
    score = passed / total * 100
    print("-" * 60)
    print(f"\\nFINAL SCORE: {passed}/{total} ({score:.1f}%)\\n")

    RESULTS_FILE.write_text(json.dumps(results, indent=2))
    print(f"Results saved to evaluation/results.json")
    return score


if __name__ == "__main__":
    run_eval()'''

files["rag_engine.py"] = '''"""
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
                context_block = "\\n\\n---\\n\\n".join(
                    f"[Source: {m.get('source','?')} | Topic: {m.get('topic','?')}]\\n{c}"
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
        final_prompt += f"\\n\\nNote: A tool was queried to help answer this. The tool returned: {tool_result}\\nUse this tool output to accurately answer the question."

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
    print("AI System Ready. Type 'exit' to quit.\\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        result = ask(q)
        print(f"\\nAI [{result['source']}]: {result['answer']}")
        if result.get("sources_used"):
            print(f"   Sources: {', '.join(result['sources_used'])}")
        print(f"   {result['latency_ms']}ms\\n")'''

for file_path, content in files.items():
    with open(os.path.join(base_dir, file_path), 'w', encoding='utf-8') as f:
        f.write(content)

print("Project generated successfully.")
