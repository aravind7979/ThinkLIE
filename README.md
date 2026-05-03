# ThinkLIE - Production AI Conversational Platform

A full-stack AI system with a custom multi-stage Retrieval-Augmented Generation (RAG) pipeline, designed for context-grounded reasoning, real-time interaction, and scalable deployment.

---

## 🔗 Demo

* **Live App**: https://thinklie.vercel.app
* **GitHub**: https://github.com/aravind7979/thinklie

---

## ❓ Problem Statement

Most AI chat applications rely on direct LLM calls, leading to:

* Hallucinated responses due to lack of grounding
* No persistent memory across sessions
* Poor handling of multimodal and complex queries

ThinkLIE addresses this by implementing a structured AI orchestration system with retrieval, memory, and real-time interaction layers.

---

## 🏗️ System Architecture

User Input
→ Intent Detection
→ Query Rewriting
→ Domain Routing
→ Dual Retrieval (ChromaDB + JSON)
→ Re-Ranking (BM25-style)
→ Context Injection (Session + Long-term Memory + Files)
→ LLM (Gemini)
→ Post-Processing
→ Streaming Output (SSE / Voice)

---

## ⚙️ Key Features

* Multi-stage RAG pipeline for context-grounded responses
* Dual-source retrieval with semantic search and re-ranking
* Full-duplex live voice interaction via WebSocket (PCM streaming)
* Multimodal processing (images, PDFs, text, audio) with dynamic routing
* Two-tier memory architecture (Redis session + ChromaDB long-term)
* Custom token-indexed full-text search (no Elasticsearch)
* Real-time streaming responses via Server-Sent Events (SSE)

---

## 🧠 Engineering Highlights

### AI Orchestration

* Designed a multi-stage RAG pipeline instead of direct LLM calls
* Implemented query rewriting and domain routing for better retrieval accuracy

### Memory Architecture

* Redis-based session memory with TTL for short-term context
* ChromaDB-based long-term semantic memory for cross-session retrieval

### Real-Time Systems

* Built WebSocket proxy for low-latency voice interaction
* Implemented SSE streaming for incremental response delivery

### Search System

* Developed custom inverted-index search using SQL aggregation
* Eliminated need for external search engines

### Error Handling

* API fallback strategies for LLM failures
* Handling empty or noisy retrieval results
* Timeout and streaming interruption handling

---

## 🛠️ Tech Stack

* Backend: Python, FastAPI
* AI/LLM: Gemini API
* Databases: PostgreSQL, Redis, ChromaDB
* Infrastructure: Docker, AWS EC2
* Frontend: JavaScript (Vercel deployment)
* Protocols: WebSocket, Server-Sent Events (SSE)

---

## 🚀 Setup Instructions

git clone https://github.com/aravind7979/thinklie
cd thinklie

# Backend setup

pip install -r requirements.txt
uvicorn app.main:app --reload

# Docker (optional)

docker-compose up --build

---

## ⚖️ Trade-offs & Design Decisions

* External LLM (Gemini) vs Local Models
  → Chose Gemini for better reasoning performance and lower system complexity

* Custom Search vs Elasticsearch
  → Built lightweight inverted index for control and reduced dependencies

* RAG Pipeline Complexity vs Latency
  → Balanced multi-stage processing with near real-time responses

---

## 🔮 Future Work

* Local LLM integration (hybrid inference)
* Improved retrieval ranking strategies
* Persistent long-term user memory
* Distributed system scaling

---

## 📌 Why This Project Matters

ThinkLIE is not just an AI chatbot. It is a modular AI system that integrates retrieval, memory, real-time interaction, and scalable backend infrastructure - reflecting how modern production AI systems are designed.
