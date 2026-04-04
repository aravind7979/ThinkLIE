import re
from typing import List, Dict, Any
from datetime import datetime

class Ranker:
    def __init__(self):
        pass

    def rank_and_filter(self, query: str, retrieved_docs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Scores retrieved docs based on:
        - Relevance (keyword match density or pre-computed similarity from semantic search)
        - Information Density (length / noisiness)
        """
        scored_docs = []
        query_words = set(re.findall(r'\w+', query.lower()))

        for doc in retrieved_docs:
            content = str(doc.get("content", ""))
            content_lower = content.lower()

            # 1. Relevance Score (If from semantic search, assume 1.0 base, else text match)
            base_relevance = 1.0 if doc.get("source") == "semantic_search" else 0.5
            
            # Text overlap
            overlap = sum(1 for w in query_words if w in content_lower)
            relevance_score = base_relevance + (overlap * 0.1)

            # 2. Information Density (penalize extreme short/long or noisy chunks)
            content_length = len(content)
            density_score = 1.0
            if content_length < 50:
                density_score = 0.2
            elif content_length > 2000:
                density_score = 0.8
            
            # Final Score
            final_score = relevance_score * density_score
            
            doc["score"] = final_score
            scored_docs.append(doc)

        # Sort by score descending and take top_k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

ranker = Ranker()
