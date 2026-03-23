from typing import List, Dict, Any
from .intent import intent_detector
from .domain import domain_selector
from .retriever import retriever
from .context import context_injector
from .prompt_builder import prompt_builder
class Orchestrator:
    def __init__(self):
        pass

    async def generate_response(
        self, 
        query: str, 
        history: List[Dict[str, Any]], 
        client: Any
    ) -> str:
        """
        The main pipeline: Query -> Intent -> Domain -> Retrieve -> Context -> Prompt -> LLM
        history: e.g. [{"role": "user", "content": "hello"}, {"role": "model", "content": "hi"}]
        client: genai.Client instance passed from app.py
        """
        # 1. Intent Detection
        intent = await intent_detector.detect_intent(query)
        print(f"[Orchestrator] Intent: {intent}")

        # 2. Domain Selection
        domain = await domain_selector.select_domain(query)
        print(f"[Orchestrator] Domain: {domain}")

        # 3. Retrieval
        retrieved_docs = await retriever.retrieve_context(domain, query)
        print(f"[Orchestrator] Retrieved {len(retrieved_docs)} docs.")

        # 4. Context Injection
        context_str = context_injector.inject_context(retrieved_docs, history)

        # 5. Prompt Engineering
        final_prompt = prompt_builder.build_prompt(query, intent, domain, context_str)
        
        # 6. LLM Generation
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=final_prompt
        )
        
        return response.text

orchestrator = Orchestrator()
