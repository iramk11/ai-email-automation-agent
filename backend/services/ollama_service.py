"""
Ollama LLM service for intent classification and draft generation.
"""
import ollama
from typing import List, Dict, Any
import logging
import json
import re

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with local Ollama LLM."""
    
    def __init__(self, model_name: str = "llama3", base_url: str = None):
        """
        Initialize Ollama service.
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for Ollama API (optional)
        """
        self.model_name = model_name
        self.base_url = base_url
        logger.info(f"Initialized Ollama service with model: {model_name}")
    
    def classify_intent(self, email_text: str, known_intents: List[str]) -> List[str]:
        """
        Classify the intents of an email using LLM (can be multiple).
        
        Args:
            email_text: Email body text
            known_intents: List of known intent labels
            
        Returns:
            List of detected intent strings (primary intent first)
        """
        intents_str = ", ".join(known_intents)
        
        # Create a more structured prompt that's easier for LLM to follow
        prompt = f"""Classify the email intent(s) from this list ONLY:
{intents_str}

Email to classify:
\"\"\"{email_text}\"\"\"

Instructions:
1. An email can have multiple intents (e.g., "send_materials" + "request_info")
2. Choose ONLY from the list above
3. Return your answer in this exact format: intent1, intent2, intent3
4. Use underscores for multi-word intents (e.g., send_materials not send materials)

Your classification:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response['message']['content'].strip()
            logger.info(f"Raw LLM response for intent: {content}")
            
            # Parse comma-separated intents (simpler format)
            known_lower = [i.lower().replace(" ", "_") for i in known_intents]
            normalized = []
            
            # Clean up the response - remove common wrapper text
            content = content.lower()
            content = re.sub(r'(your classification:|the intents? (?:are|is):?|i would classify (?:this|the email) as:?)', '', content)
            content = content.strip()
            
            # Try multiple parsing strategies
            
            # Strategy 1: Comma-separated values
            parts = re.split(r'[,\n]', content)
            for part in parts:
                part_clean = part.strip().strip('[]"\'').replace(' ', '_')
                if part_clean in known_lower:
                    if part_clean not in normalized:
                        normalized.append(part_clean)
            
            # Strategy 2: Find any known intent in the text
            if not normalized:
                for known_intent in known_lower:
                    if known_intent in content:
                        if known_intent not in normalized:
                            normalized.append(known_intent)
            
            # Strategy 3: Try JSON parsing (in case LLM used JSON anyway)
            if not normalized and ('[' in content or '{' in content):
                try:
                    json_match = re.search(r'\[([^\]]+)\]', content)
                    if json_match:
                        json_str = '[' + json_match.group(1) + ']'
                        intents = json.loads(json_str)
                        for intent in intents:
                            intent_clean = str(intent).lower().replace(" ", "_").strip('"\'')
                            if intent_clean in known_lower and intent_clean not in normalized:
                                normalized.append(intent_clean)
                except:
                    pass
            
            if normalized:
                logger.info(f"Classified intents: {normalized}")
                return normalized
            
            logger.warning(f"Could not parse intent from: '{content}', defaulting to general_inquiry")
            return ["general_inquiry"]
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return ["general_inquiry"]
    
    def generate_reply(
        self, 
        email_text: str, 
        intent: str,
        faq_hits: List[Dict[str, Any]],
        graph_hits: List[Dict[str, Any]],
        expanded_graph: Dict[str, List[str]],
        user_name: str = "Assistant",
        user_tone: str = "polite, proactive, and professional"
    ) -> str:
        """
        Generate email reply using LLM with context.
        
        Args:
            email_text: Original email body
            intent: Detected intent
            faq_hits: FAQ retrieval results
            graph_hits: Graph node retrieval results
            expanded_graph: Expanded graph neighbors
            user_name: Name of the user replying
            user_tone: Desired tone for the reply
            
        Returns:
            Generated draft reply text
        """
        prompt = self._build_prompt(
            email_text, intent, faq_hits, graph_hits, 
            expanded_graph, user_name, user_tone
        )
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            draft = response['message']['content'].strip()
            logger.info("Successfully generated draft reply")
            return draft
            
        except Exception as e:
            logger.error(f"Draft generation failed: {e}")
            return "I apologize, but I'm unable to generate a reply at the moment. Please try again."
    
    def _build_prompt(
        self,
        email_text: str,
        intent: str,
        faq_hits: List[Dict[str, Any]],
        graph_hits: List[Dict[str, Any]],
        expanded_graph: Dict[str, List[str]],
        user_name: str,
        user_tone: str
    ) -> str:
        """Build the prompt for draft generation."""
        
        # Build FAQ section
        faq_section = ""
        if faq_hits:
            for i, faq in enumerate(faq_hits, 1):
                faq_section += f"{i}. Q: {faq.get('question', '')}\n"
                faq_section += f"   A: {faq.get('answer', '')}\n\n"
        else:
            faq_section = "None"
        
        # Build graph section
        graph_section = ""
        if graph_hits:
            for i, node in enumerate(graph_hits, 1):
                graph_section += f"{i}. Node: {node.get('node_name', '')} "
                graph_section += f"(type={node.get('node_type', 'unknown')}), "
                graph_section += f"neighbors={node.get('neighbors', [])}\n"
        else:
            graph_section = "None"
        
        # Build expansion section
        expansion_section = ""
        if expanded_graph:
            for i, (node, neighbors) in enumerate(expanded_graph.items(), 1):
                expansion_section += f"{i}. {node} → {neighbors}\n"
        else:
            expansion_section = "None"
        
        prompt = f"""You are **{user_name}**, known for being {user_tone}.

Your job is to draft a short, natural, and professional email reply.

---

✉️ **Incoming Email**
\"\"\"{email_text}\"\"\"

🎯 **Detected Intent**: {intent}

📘 **Relevant FAQs**
{faq_section}

🧩 **Graph Context**
{graph_section}

🔗 **Related Concepts**
{expansion_section}

---

Write your reply in {user_name}'s tone:
- Acknowledge the sender and context.
- If an action is requested, confirm or ask a polite follow-up question.
- Keep the reply under 120 words.
- Do NOT invent facts — only use what's in context.
- Be natural and conversational.
"""
        
        return prompt
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            # Try a simple chat to verify the model is accessible
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}]
            )
            return response is not None
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

