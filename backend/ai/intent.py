import json
import re
from typing import Dict, Any

class QueryAnalyzer:
    def __init__(self):
        self.intent_keywords = {
            "conceptual": ["how does", "explain", "why is", "what is the difference", "concept"],
            "coding": ["write code", "how to build", "python", "javascript", "react", "fastapi"],
            "system_design": ["architecture", "scale", "system design", "load balancer"],
            "debugging": ["error", "bug", "traceback", "fix", "doesn't work", "issue"],
            "factual": ["what is", "list", "who", "when", "where"]
        }

    async def analyze(self, query: str, client: Any = None) -> Dict[str, Any]:
        """
        Classifies intent, rewrites query for retrieval, detects required depth.
        Fallback to rules if no client is provided/available.
        """
        if client:
            return self._analyze_llm(query, client)
        else:
            return self._analyze_rules(query)

    def _analyze_rules(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        # Intent
        detected_intent = "conceptual"
        for intent, kws in self.intent_keywords.items():
            if any(kw in query_lower for kw in kws):
                detected_intent = intent
                break
                
        # Depth
        depth = "intermediate"
        if any(w in query_lower for w in ["expert", "advanced", "deep dive"]):
            depth = "advanced"
        elif any(w in query_lower for w in ["basic", "simple", "beginner", "for dummies"]):
            depth = "basic"
            
        return {
            "intent": detected_intent,
            "depth": depth,
            "rewritten_query": query # Without LLM, returning original
        }

    def _analyze_llm(self, query: str, client: Any) -> Dict[str, Any]:
        try:
            prompt = f"""
            Analyze the following user query. Return ONLY a valid JSON object.
            Query: "{query}"
            
            JSON format:
            {{
                "intent": "evaluate as one of: conceptual, factual, coding, system_design, debugging",
                "depth": "evaluate as one of: basic, intermediate, advanced",
                "rewritten_query": "A search-engine optimized version of the query for semantic retrieval"
            }}
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(raw_text)
        except Exception as e:
            print(f"[QueryAnalyzer] LLM parsing error: {e}")
            return self._analyze_rules(query)

intent_detector = QueryAnalyzer()
