import os
import json
import chromadb
from typing import Dict, Any, List
from .embedder import embedder

class Retriever:
    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = knowledge_dir
        # Initialize Chroma for Knowledge Search
        try:
            self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
            self.knowledge_collection = self.chroma_client.get_or_create_collection(name="knowledge_base")
        except Exception as e:
            print(f"[Retriever] ChromaDB connection failed: {e}")
            self.knowledge_collection = None

    async def retrieve_context(self, domain: str, query: str = "") -> List[Dict[str, Any]]:
        """
        Multi-source retriever:
        1. Exact Domain Match (Legacy JSON) - Keyword based
        2. Semantic Search (ChromaDB)
        """
        results = []
        
        # 1. Semantic Search (if Chroma is available and has data)
        if self.knowledge_collection and query:
            query_embedding = embedder.embed_text(query)
            if query_embedding:
                try:
                    # Optional: filter by domain if semantic search supports it or just global search
                    semantic_results = self.knowledge_collection.query(
                        query_embeddings=[query_embedding],
                        n_results=3
                    )
                    
                    if semantic_results and "documents" in semantic_results and semantic_results["documents"]:
                        for idx, doc in enumerate(semantic_results["documents"][0]):
                            meta = semantic_results["metadatas"][0][idx] if semantic_results.get("metadatas") else {}
                            results.append({
                                "source": "semantic_search",
                                "content": doc,
                                "metadata": meta
                            })
                except Exception as e:
                    print(f"[Retriever] Semantic search error: {e}")

        # 2. Legacy JSON retrieval
        json_results = self._retrieve_from_json(domain)
        for jr in json_results:
            results.append({
                "source": "legacy_json",
                "content": str(jr),
                "metadata": {"domain": domain}
            })
            
        return results

    def _retrieve_from_json(self, domain: str) -> List[Dict[str, Any]]:
        if domain == "general":
            return []
            
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
