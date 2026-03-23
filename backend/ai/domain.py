import os
import json
from typing import List

class DomainSelector:
    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = knowledge_dir
        self.domains = self._load_available_domains()
        
    def _load_available_domains(self) -> List[str]:
        if not os.path.exists(self.knowledge_dir):
            return []
            
        domains = []
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith(".json"):
                domains.append(filename.replace(".json", ""))
        return domains

    async def select_domain(self, query: str) -> str:
        """
        Selects the most relevant domain for the query.
        Since we don't have a vector DB yet, we can do a simple keyword match 
        against domain names, or use the LLM if we want it to be smart.
        For now, let's implement a keyword-based approach based on the JSON files available.
        """
        query_lower = query.lower()
        
        # Fallback keyword maps for domains to improve accuracy beyond exact domain name match
        domain_keywords = {
            "algorithms": ["binary search", "algorithm", "sort", "big o", "time complexity"],
            "system_design": ["load balancer", "system design", "scaling", "architecture", "microservices"],
            "backend_engineering": ["rest api", "backend", "database", "http", "api design"],
            "natural_language_processing": ["transformer", "attention", "nlp", "language model", "qkv"],
            "neural_networks": ["gradient descent", "neural network", "deep learning", "loss function", "optimizer"],
            "probability_and_statistics": ["bayes", "probability", "statistics", "theorem", "distribution"],
            "physics": ["relativity", "einstein", "physics", "time dilation", "speed of light"],
            "cognitive_psychology": ["cognitive bias", "psychology", "heuristic", "bias", "brain"],
            "personal_finance": ["compound interest", "finance", "investing", "rule of 72"],
            "neuroscience_health": ["sleep", "neuroscience", "brain", "rem", "health"],
            "business_communication": ["email", "professional", "communication", "manager"],
            "career_development": ["resume", "career", "interview", "job"],
            "productivity": ["pomodoro", "productivity", "time management", "focus", "deep work"],
            "creative_writing": ["story", "writing", "fiction", "character", "three act"],
            "logic_and_critical_thinking": ["fallacy", "logic", "critical thinking", "argument", "straw man"],
            "data_structures": ["hash table", "data structure", "array", "linked list", "dictionary"],
            "climate_science": ["climate", "global warming", "greenhouse", "co2", "emission"]
        }
        
        best_domain = None
        max_matches = 0
        
        for domain, keywords in domain_keywords.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            if matches > max_matches:
                max_matches = matches
                best_domain = domain
                
        # If heuristics fail but domain name is in query
        if not best_domain:
            for domain in self.domains:
                if domain.replace("_", " ") in query_lower:
                    best_domain = domain
                    break
                    
        return best_domain or "general" # General means no specific domain found

domain_selector = DomainSelector()
