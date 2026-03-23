from typing import List, Dict, Any

class ContextInjector:
    def __init__(self):
        pass

    def inject_context(self, retrieved_data: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> str:
        """
        Assembles the retrieved knowledge and the chat history into a coherent context string.
        """
        context_parts = []
        
        # Inject Knowledge
        if retrieved_data:
            context_parts.append("--- RETRIEVED KNOWLEDGE ---")
            for doc in retrieved_data:
                title = doc.get("title", "Untitled")
                content = doc.get("content", "")
                examples = doc.get("code_examples", [])
                steps = doc.get("step_by_step_explanation", [])
                
                context_parts.append(f"Title: {title}\nContent:\n{content}")
                if examples:
                    ex_str = "\n".join(examples)
                    context_parts.append(f"Examples:\n{ex_str}")
                if steps:
                    step_str = "\n".join(steps)
                    context_parts.append(f"Step-by-step:\n{step_str}")
                context_parts.append("---------------------------")
        else:
            context_parts.append("--- NO SPECIFIC DOMAIN KNOWLEDGE RETRIEVED ---")

        # Inject Chat History (Memory)
        if history:
            context_parts.append("--- CHAT HISTORY ---")
            # Usually keep last N turns
            for msg in history[-5:]: 
                role = msg.get("role", "user")
                text = msg.get("content", "")
                context_parts.append(f"{role.capitalize()}: {text}")
            context_parts.append("--------------------")
            
        return "\n\n".join(context_parts)

context_injector = ContextInjector()
