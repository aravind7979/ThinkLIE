from typing import List, Dict, Any

class ContextBuilder:
    def __init__(self):
        pass

    def inject_context(
        self,
        ranked_data: List[Dict[str, Any]],
        session_history: List[Dict[str, Any]],
        long_term_memory: List[str] = None,
        user_profile: Dict[str, Any] = None,
        file_context: Dict[str, Any] = None
    ) -> str:
        """
        Assembles memory, history, and ranked knowledge.
        Provides a minimal, structured context to the LLM.
        """
        context_parts = []
        
        # 1. User File Context
        if file_context:
            context_parts.append("--- USER FILE CONTEXT ---")
            context_parts.append(f"File Type: {file_context.get('type')}")
            # Cap file content to prevent blowing out the context window unnecessarily
            content = file_context.get('content', '')[:10000]
            context_parts.append(f"File Content Extracted:\n{content}")

        # 2. User Profile
        if user_profile:
            context_parts.append("--- USER PROFILE ---")
            skills = user_profile.get("skills", "")
            goals = user_profile.get("goals", "")
            if skills: context_parts.append(f"Skills: {skills}")
            if goals: context_parts.append(f"Goals: {goals}")
        
        # 3. Long Term Memory
        if long_term_memory:
            context_parts.append("--- LONG TERM MEMORY ---")
            for idx, mem in enumerate(long_term_memory):
                context_parts.append(f"[{idx+1}] {mem}")
        
        # 3. Ranked Knowledge Context
        if ranked_data:
            context_parts.append("--- RANKED KNOWLEDGE ---")
            for idx, doc in enumerate(ranked_data):
                # Clean/compress the chunk visually
                content = str(doc.get("content", "")).strip()[:1500]  # Cap per chunk token length
                source = doc.get("source", "unknown")
                score = doc.get("score", 0.0)
                context_parts.append(f"[Source: {source} | Score: {score:.2f}]\n{content}\n")
        else:
            context_parts.append("--- NO SPECIFIC DOMAIN KNOWLEDGE RETRIEVED ---")

        # 4. Session Context
        if session_history:
            context_parts.append("--- SESSION CONTEXT (Recent History) ---")
            for msg in session_history[-3:]: # compress: keep only last 3 turns
                role = msg.get("role", "user")
                text = msg.get("content", "")
                context_parts.append(f"{role.capitalize()}: {text}")
            
        return "\n\n".join(context_parts)

context_injector = ContextBuilder()
