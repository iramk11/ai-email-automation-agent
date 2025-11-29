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
        Classify multiple intents in an email using LLM.
        Returns list of intents (can be multiple) - matches graph_rag_updated2.ipynb approach.
        
        Args:
            email_text: Email body text
            known_intents: List of known intent labels
            
        Returns:
            List of detected intent strings (can be multiple)
        """
        intents_str = ", ".join(known_intents)
        
        prompt = f"""You are an email intent classifier.

Available intents (choose from these EXACT labels):
{intents_str}

Email to classify:
\"\"\"{email_text}\"\"\"

Instructions:
1. Identify ALL relevant intents from the list above
2. An email can have multiple intents (e.g., "share resume" = send_materials, "schedule meeting" = schedule)
3. Return ONLY a JSON array with exact labels from the list
4. Use underscores for multi-word intents (e.g., send_materials, not "send materials")

Examples:
- "Can you send me your resume?" → ["send_materials"]
- "Share your resume and let's schedule a call" → ["send_materials", "schedule"]
- "What time works for a meeting?" → ["schedule"]

Return ONLY valid JSON array, nothing else:
"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"].strip()
            
            # Debug: print what LLM returned
            logger.info(f"🔍 LLM raw response: {content[:200]}...")
            
            # Remove markdown code blocks if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            try:
                intents = json.loads(content)
                if isinstance(intents, list):
                    # Filter to only valid intents
                    valid_intents = [i for i in intents if i in known_intents]
                    if valid_intents:
                        logger.info(f"✅ Classified intents: {valid_intents}")
                        return valid_intents
            except json.JSONDecodeError:
                # Try to extract array from text
                match = re.search(r'\[.*?\]', content)
                if match:
                    try:
                        intents = json.loads(match.group())
                        if isinstance(intents, list):
                            valid_intents = [i for i in intents if i in known_intents]
                            if valid_intents:
                                logger.info(f"✅ Classified intents: {valid_intents}")
                                return valid_intents
                    except:
                        pass
            
            # Fallback: try to find intent names in the response
            for intent in known_intents:
                if intent.lower() in content.lower():
                    logger.info(f"✅ Classified intents (fallback): [{intent}]")
                    return [intent]
            
            logger.warning("⚠️ Could not parse intents, using default")
            return ["general_inquiry"]
            
        except Exception as e:
            logger.error(f"⚠️ Error classifying intent: {e}")
            return ["general_inquiry"]
    
    def generate_reply(
        self, 
        email_text: str, 
        intent: str,
        faq_hits: List[Dict[str, Any]],
        graph_hits: List[Dict[str, Any]],
        expanded_graph: Dict[str, List[str]],
        style_examples: List[Dict[str, Any]] = None,  # ✅ NEW: Style examples
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
            expanded_graph, style_examples, user_name, user_tone
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
        style_examples: List[Dict[str, Any]] = None,  # ✅ NEW: Style examples
        user_name: str = "Assistant",
        user_tone: str = "polite, proactive, and professional"
    ) -> str:
        """Build the prompt for draft generation with style examples (Gmail-style approach)."""
        
        # Build FAQ section
        faq_section = "\n".join([
            f"{i+1}. Q: {f.get('question', '')}\n   A: {f.get('answer', '')}"
            for i, f in enumerate(faq_hits)
        ]) or "None"
        
        # Build graph section
        graph_section = "\n".join([
            f"{i+1}. Node: {g.get('node_name', '')} (type={g.get('node_type', 'unknown')}), neighbors={g.get('neighbors', [])}"
            for i, g in enumerate(graph_hits)
        ]) or "None"
        
        # Build expansion section
        expansion_section = "\n".join([
            f"{i+1}. {node} → {neighbors}"
            for i, (node, neighbors) in enumerate(expanded_graph.items(), 1)
        ]) or "None"
        
        # ✅ NEW: Style section (Gmail-style approach)
        style_section = ""
        if style_examples:
            style_section = "\n".join([
                f"{i+1}. Style Example {i+1} ({user_name}'s writing tone):\n   \"{s.get('reply_chunk', '')[:250]}...\""
                for i, s in enumerate(style_examples[:3])  # Show top 3 style examples
            ])
        else:
            style_section = "None"
        
        prompt = f"""You are **{user_name}**, a graduate student known for being {user_tone}.

Your job is to draft a short, natural, and professional email reply.

Keep it warm but not overly formal — think of how a thoughtful student would respond to a professor, coordinator, or peer.

**IMPORTANT**: Match the writing style shown in the style examples below. These are examples of {user_name}'s actual writing tone. Use similar phrasing, level of formality, and structure.

---

✉️ **Incoming Email**
\"\"\"{email_text}\"\"\"

🎯 **Detected Intent**: {intent}

📘 **Relevant FAQs** (Content Context)
{faq_section}

🧩 **Graph Context** (Structured Relationships)
{graph_section}

🔗 **Related Concepts**
{expansion_section}

✍️ **Writing Style Examples** (Style Anchor - Match This Tone)
{style_section}

---

Write your reply:
- Match the tone and style from the examples above
- Use similar phrasing, level of formality, and structure
- Acknowledge the sender and context
- If an action is requested, confirm or ask a polite follow-up question
- Keep the reply under 120 words
- Do NOT invent facts — only use what's in context
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

