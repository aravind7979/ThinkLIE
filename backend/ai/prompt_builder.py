from typing import Dict, Any

class PromptBuilder:
    def __init__(self):
        pass

    def build_prompt(self, query: str, intent: str, domain: str, context: str) -> str:
        """
        Constructs the final prompt string that is sent to the LLM.
        """
        # A simple parameterized prompt template
        prompt_template = f"""You are an expert AI assistant knowledgeable in many domains.
Currently, you are helping a user with a query classified as: '{intent}' intent in the '{domain}' domain.

{context}

Based on the context and your expertise, answer the user's query thoughtfully.
User Query: {query}
"""
        return prompt_template

prompt_builder = PromptBuilder()

# For the orchestrator to call the LLM directly, or orchestrator can get the client from app.py
# If app.py passes the active LLM client/model down, we don't need a singleton here.
