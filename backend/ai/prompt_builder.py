from typing import Dict, Any

class PromptBuilder:
    def __init__(self):
        pass

    def build_prompt(self, analyzed_query: Dict[str, Any], domain: str, context: str, has_file: bool = False) -> str:
        """
        Constructs the final prompt string that enforces layered explanation depth.
        """
        intent = analyzed_query.get("intent", "general")
        depth = analyzed_query.get("depth", "intermediate")
        rewritten = analyzed_query.get("rewritten_query", "general query")

        file_instruction = ""
        if has_file:
            file_instruction = "\nIMPORTANT: A user file was provided. You MUST prioritize interpreting and reasoning over the file content BEFORE using general knowledge.\n"

        prompt_template = f"""You are an advanced, expert AI assistant with layered reasoning capabilities.
You are helping a user with a query classified as: 
- Intent: {intent}
- Depth: {depth}
- Topic Domain: {domain}

{context}
{file_instruction}
Based on the context and your expertise, answer the user's query thoughtfully.
Your explanation MUST follow this layered structure:

Step 1: Simple Intuition (Briefly explain the 'what' and 'why' for a layman)
Step 2: Core Concept (Define the specific technical idea or problem)
Step 3: Internal Mechanism (Explain HOW it works internally, the logic or code)
Step 4: Real-World Analogy or System Interaction (How does this fit into broader systems or real-life examples? Tradeoffs and constraints?)

Focus on system-level thinking, why tradeoffs exist, and how constraints shape the solution.
DO NOT give shallow, direct answers without explanation unless explicitly asked to do so.

User Query: {rewritten}
"""
        return prompt_template

prompt_builder = PromptBuilder()
