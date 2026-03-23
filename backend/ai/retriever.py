import os
import json
from typing import Dict, Any, List

class Retriever:
    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = knowledge_dir

    async def retrieve_context(self, domain: str, query: str = "") -> List[Dict[str, Any]]:
        """
        Retrieves context from the local JSON file for the given domain.
        Since the dataset per domain is small, we will return the entire content of that domain file
        or filter it simply if we want. For now, we load all documents in the domain json.
        """
        if domain == "general":
            return [] # No specific context for general queries
            
        filepath = os.path.join(self.knowledge_dir, f"{domain}.json")
        if not os.path.exists(filepath):
            return []
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading knowledge file {filepath}: {e}")
            return []

retriever = Retriever()
