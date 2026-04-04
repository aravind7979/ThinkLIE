import os
import sys
import json
import chromadb
from dotenv import load_dotenv

# Ensure we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from backend.ai.embedder import embedder

def ingest_all():
    print("Initializing ChromaDB connection...")
    chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
    collection = chroma_client.get_or_create_collection(name="knowledge_base")
    
    knowledge_dir = "./data/knowledge"
    if not os.path.exists(knowledge_dir):
        print(f"Directory {knowledge_dir} not found. Nothing to ingest.")
        return

    print("Scanning for JSON knowledge files...")
    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(knowledge_dir, filename)
            domain = filename.replace(".json", "")
            print(f"Processing domain: {domain}")
            
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for idx, doc in enumerate(data):
                        # Construct a searchable string representation
                        title = doc.get("title", f"Document {idx}")
                        content = doc.get("content", "")
                        text_to_embed = f"Title: {title}\nDomain: {domain}\nContent:\n{content}"
                        
                        # Generate embedding
                        emb = embedder.embed_text(text_to_embed)
                        if emb:
                            doc_id = f"{domain}_{idx}"
                            
                            # Upsert to ChromaDB
                            collection.upsert(
                                documents=[str(doc)],
                                embeddings=[emb],
                                metadatas=[{"domain": domain, "title": title}],
                                ids=[doc_id]
                            )
                            print(f"  Ingested: {title}")
                        else:
                            print(f"  Failed to embed: {title}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    print("Ingestion complete. The system is ready for semantic retrieval.")

if __name__ == "__main__":
    ingest_all()
