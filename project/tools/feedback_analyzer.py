"""
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

    print(f"\nFeedback Summary")
    print(f"   Total responses rated : {total}")
    print(f"   Good                  : {good} ({good/total:.0%})")
    print(f"   Bad                   : {bad} ({bad/total:.0%})")

    if failed:
        print(f"\nFailed Queries ({len(failed)} total):")
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
        print(f"\nCommon words in failed queries: {keywords[:6]}")
        print("   Consider adding documents on these topics to your knowledge base.\n")


if __name__ == "__main__":
    analyze()