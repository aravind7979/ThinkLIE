"""
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

    print(f"\nRunning {len(tests)} eval queries...\n")
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
        print(f"   Latency: {result['latency_ms']}ms\n")

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
    print(f"\nFINAL SCORE: {passed}/{total} ({score:.1f}%)\n")

    RESULTS_FILE.write_text(json.dumps(results, indent=2))
    print(f"Results saved to evaluation/results.json")
    return score


if __name__ == "__main__":
    run_eval()