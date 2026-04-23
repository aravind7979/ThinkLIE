from typing import List, Dict, Any, Optional
import uuid

from .intent import intent_detector
from .domain import domain_selector
from .retriever import retriever
from .ranker import ranker
from .context import context_injector
from .prompt_builder import prompt_builder
from .post_processor import post_processor
from .memory import memory_manager
from .file_processor import file_processor

class Orchestrator:
    def __init__(self):
        pass

    async def generate_response(
        self, 
        query: str, 
        history: List[Dict[str, Any]], 
        client: Any,
        user_id: str = "anonymous",
        session_id: str = None,
        file_bytes: Optional[bytes] = None,
        file_type: Optional[str] = None
    ) -> str:
        """
        The main pipeline:
        User/File -> File Processor -> Analyzer -> Memory/Retrieval -> Ranker -> Context Builder -> LLM -> Post-Processor -> Output
        """
        if not session_id:
            session_id = f"sess_{uuid.uuid4()}"

        # 1. File Processor Module
        file_context = None
        if file_bytes:
            print(f"[Orchestrator] Processing attached file of type {file_type}...")
            file_context = await file_processor.process(file_bytes, file_type, query, client)

        # 2. Query Analyzer (Intent, Depth, Rewrite)
        # If there's an image, the query is combined. We just pass the text query.
        analyzed_query = await intent_detector.analyze(query, client)
        print(f"[Orchestrator] Analyzed Query: {analyzed_query}")

        # 3. Domain Selection (Legacy fallback + routing metadata)
        domain = await domain_selector.select_domain(analyzed_query.get("rewritten_query", query))
        print(f"[Orchestrator] Domain: {domain}")

        # 4. Memory & Retrieval
        # a. Session Memory 
        session_memory = memory_manager.get_session_memory(session_id)
        if not session_memory:
            session_memory = history[-5:] # fallback to API passed history
            
        # b. Long Term Memory
        lt_memory = memory_manager.retrieve_long_term_memory(user_id, query)
        
        # c. Knowledge Retrieval
        retrieved_docs = await retriever.retrieve_context(domain, analyzed_query.get("rewritten_query", query))

        # 5. Ranker
        ranked_docs = ranker.rank_and_filter(query, retrieved_docs, top_k=5)

        # 6. Context Builder
        # user_profile can be fetched from DB if provided, here we mock an empty profile
        context_str = context_injector.inject_context(
            ranked_data=ranked_docs,
            session_history=session_memory,
            long_term_memory=lt_memory,
            user_profile={"skills": "General Developer", "goals": "Learn system design"},
            file_context=file_context
        )

        # 7. Prompt Engineering
        final_prompt = prompt_builder.build_prompt(analyzed_query, domain, context_str, has_file=bool(file_context))
        
        # 8. LLM Generation
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=final_prompt
        )
        raw_text = response.text

        # 9. Post-Processing
        final_text = post_processor.process(raw_text)

        # 10. Update Memory (Background save)
        # Add to session
        session_memory.append({"role": "user", "content": query})
        session_memory.append({"role": "assistant", "content": final_text})
        memory_manager.set_session_memory(session_id, session_memory)
        
        # Store high signal to long-term memory if depth was advanced 
        if analyzed_query.get("depth") == "advanced":
            memory_manager.add_long_term_memory(user_id, f"User explored advanced topic: {query}")

        return final_text

    async def generate_response_stream(
        self, 
        query: str, 
        history: List[Dict[str, Any]], 
        client: Any,
        user_id: str = "anonymous",
        session_id: str = None,
        file_bytes: Optional[bytes] = None,
        file_type: Optional[str] = None
    ):
        """
        Streaming pipeline yielding chunks.
        """
        if not session_id:
            session_id = f"sess_{uuid.uuid4()}"

        # 1. File Processor Module
        file_context = None
        if file_bytes:
            file_context = await file_processor.process(file_bytes, file_type, query, client)

        # 2. Query Analyzer
        analyzed_query = await intent_detector.analyze(query, client)
        
        # 3. Domain Selection
        domain = await domain_selector.select_domain(analyzed_query.get("rewritten_query", query))

        # 4. Memory & Retrieval
        session_memory = memory_manager.get_session_memory(session_id)
        if not session_memory:
            session_memory = history[-5:]
            
        lt_memory = memory_manager.retrieve_long_term_memory(user_id, query)
        retrieved_docs = await retriever.retrieve_context(domain, analyzed_query.get("rewritten_query", query))
        ranked_docs = ranker.rank_and_filter(query, retrieved_docs, top_k=5)

        # 5. Context Builder
        context_str = context_injector.inject_context(
            ranked_data=ranked_docs,
            session_history=session_memory,
            long_term_memory=lt_memory,
            user_profile={"skills": "General Developer", "goals": "Learn system design"},
            file_context=file_context
        )

        # 6. Prompt Engineering
        final_prompt = prompt_builder.build_prompt(analyzed_query, domain, context_str, has_file=bool(file_context))
        
        # 7. LLM Streaming
        response_stream = client.models.generate_content_stream(
            model="gemini-2.5-flash-lite", 
            contents=final_prompt
        )
        
        full_response = ""
        for chunk in response_stream:
            text_chunk = chunk.text
            if text_chunk:
                full_response += text_chunk
                yield text_chunk

        # 8. Update Memory Post-Stream
        session_memory.append({"role": "user", "content": query})
        session_memory.append({"role": "assistant", "content": full_response})
        memory_manager.set_session_memory(session_id, session_memory)
        
        if analyzed_query.get("depth") == "advanced":
            memory_manager.add_long_term_memory(user_id, f"User explored advanced topic: {query}")

orchestrator = Orchestrator()
