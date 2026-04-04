import os
import json
import redis
import chromadb
from typing import Dict, Any, List
from .embedder import embedder

class MemoryManager:
    def __init__(self):
        # Redis (Session Memory)
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            print(f"[MemoryManager] Redis connection failed: {e}")
            self.redis_client = None

        # ChromaDB (Long-Term Memory)
        try:
            self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
            self.lt_memory = self.chroma_client.get_or_create_collection(name="long_term_memory")
        except Exception as e:
            print(f"[MemoryManager] ChromaDB connection failed: {e}")
            self.lt_memory = None

    # --- Session Memory (Redis) ---
    def get_session_memory(self, session_id: str) -> List[Dict[str, str]]:
        if not self.redis_client:
            return []
        data = self.redis_client.get(f"session:{session_id}")
        return json.loads(data) if data else []

    def set_session_memory(self, session_id: str, history: List[Dict[str, str]]):
        if self.redis_client:
            # Keep only last 10 messages
            recent_history = history[-10:]
            self.redis_client.setex(f"session:{session_id}", 3600, json.dumps(recent_history))

    # --- Long Term Memory (ChromaDB) ---
    def add_long_term_memory(self, user_id: str, text: str):
        """Stores important signals in long term memory."""
        if not self.lt_memory or not text:
            return
        
        embedding = embedder.embed_text(text)
        if not embedding:
            return
            
        doc_id = f"{user_id}_{hash(text)}"
        self.lt_memory.upsert(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"user_id": user_id, "type": "learned_preference"}],
            ids=[doc_id]
        )

    def retrieve_long_term_memory(self, user_id: str, query: str, top_k: int = 3) -> List[str]:
        if not self.lt_memory or not query:
            return []
            
        embedding = embedder.embed_text(query)
        if not embedding:
            return []
            
        results = self.lt_memory.query(
            query_embeddings=[embedding],
            where={"user_id": user_id},
            n_results=top_k
        )
        
        memories = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            memories = results["documents"][0]
        return memories

memory_manager = MemoryManager()
