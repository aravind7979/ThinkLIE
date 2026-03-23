from typing import Dict, Any

class IntentDetector:
    def __init__(self):
        # We don't have a complex intent model yet, so we will use few-shot prompting
        # or a simple rule-based approach for this demo.
        # But we'll try to use the GEMINI API for intent classification as requested by best practices.
        # However, to minimize LLM roundtrips and latency, we can use a local lightweight mechanism
        # or a single fast LLM call. Let's implement a simple keyword-based intent detector first,
        # with a fallback to the LLM if needed, to keep it fast.
        
        # Valid intents primarily from dataset: 
        # learning, informational, transactional.
        
        self.intent_keywords = {
            "learning": ["how does", "explain", "why is", "what is the difference", "tutorial", "step by step"],
            "transactional": ["write an email", "how do I write", "help me write", "rewrite", "generate"],
            "informational": ["what is", "list", "who", "when", "where", "difference between"]
        }

    async def detect_intent(self, query: str) -> str:
        """
        Detects the user's intent from the query.
        Returns one of: 'learning', 'informational', 'transactional', or 'general'
        """
        query_lower = query.lower()
        
        # Simple heuristic
        if any(kw in query_lower for kw in self.intent_keywords["transactional"]):
            return "transactional"
        elif any(kw in query_lower for kw in self.intent_keywords["learning"]):
            return "learning"
        elif any(kw in query_lower for kw in self.intent_keywords["informational"]):
            return "informational"
            
        return "general"  # Default fallback
        
# Singleton instance
intent_detector = IntentDetector()
