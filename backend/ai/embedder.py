import os
from google import genai
from typing import List

class Embedder:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model = "text-embedding-004"

    def embed_text(self, text: str) -> List[float]:
        if not self.client or not text:
            return []
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"[Embedder] Error: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not self.client or not texts:
            return []
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts
            )
            return [e.values for e in response.embeddings]
        except Exception as e:
            print(f"[Embedder] Batch Error: {e}")
            return []

embedder = Embedder()
