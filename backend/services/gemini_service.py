"""
Gemini LLM service for intent classification and draft generation.
"""
import os
from typing import List, Dict, Any
import logging
import json
import re
import time
from collections import deque

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API calls (15 requests per minute for Gemini)."""
    
    def __init__(self, max_requests: int = 15, time_window: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = deque()
        self.lock = False
    
    def wait_if_needed(self):
        """Wait if we're at the rate limit."""
        now = time.time()
        
        # Remove requests older than the time window
        while self.request_times and self.request_times[0] < now - self.time_window:
            self.request_times.popleft()
        
        # If we're at the limit, wait until the oldest request expires
        if len(self.request_times) >= self.max_requests:
            oldest_time = self.request_times[0]
            wait_time = (oldest_time + self.time_window) - now + 0.1  # Add 0.1s buffer
            if wait_time > 0:
                logger.info(f"⏳ Rate limit reached ({self.max_requests} req/min). Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                # Clean up again after waiting
                now = time.time()
                while self.request_times and self.request_times[0] < now - self.time_window:
                    self.request_times.popleft()
        
        # Record this request
        self.request_times.append(time.time())


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", api_key: str = None):
        """
        Initialize Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use (e.g., "gemini-pro", "gemini-1.5-pro")
            api_key: Gemini API key (if None, reads from GEMINI_API_KEY env var)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        
        self.model_name = model_name
        
        # Try to load from .env file first
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "env", ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            self.api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            except Exception as e:
                logger.warning(f"Could not read .env file: {e}")
        
        # Fallback to parameter or environment variable
        self.api_key = self.api_key if hasattr(self, 'api_key') and self.api_key else (api_key or os.getenv("GEMINI_API_KEY"))
        
        if not self.api_key or self.api_key == "your_key_here":
            raise ValueError("GEMINI_API_KEY not found. Set it in env/.env file or as environment variable.")
        
        # Configure client
        genai.configure(api_key=self.api_key)
        
        # Load model
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize rate limiter (15 requests per minute for Gemini free tier)
        self.rate_limiter = RateLimiter(max_requests=15, time_window=60.0)
        
        logger.info(f"Initialized Gemini service with model: {model_name} (rate limit: 15 req/min)")
    
    def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini API with a prompt (with rate limiting).
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Response text from Gemini
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def classify_intent_and_artifacts(
        self,
        email_text: str,
        known_intents: List[str],
        known_artifacts: List[str],
        artifact_dict: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """
        Classify both intents AND artifacts from an email using LLM.
        
        Args:
            email_text: Email body text
            known_intents: List of known intent labels
            known_artifacts: List of known artifact labels
            artifact_dict: Dictionary explaining what each artifact means
        
        Returns:
            Dictionary with "intents" and "artifacts" lists
        """
        intents_str = ", ".join(known_intents)
        artifacts_str = ", ".join(known_artifacts)
        
        # Build artifact descriptions for the prompt
        artifact_descriptions = "\n".join([
            f"- {artifact}: {desc}"
            for artifact, desc in sorted(artifact_dict.items())
            if artifact in known_artifacts
        ])
        
        prompt = f"""You are an email intent and artifact classifier.

Available intents (choose from these EXACT labels):
{intents_str}

Available artifacts (choose from these EXACT labels):
{artifacts_str}

Artifact meanings (use these to decide which artifacts are needed):
{artifact_descriptions}

Email to classify:
\"\"\"{email_text}\"\"\"

Instructions:
1. Identify ALL relevant intents from the intent list
2. Identify which artifacts will be useful for responding to this email
   - Be precise: if it asks for ML/analytics resume, return ONLY ds_resume
   - If it asks for software engineering resume, return ONLY swe_resume
   - Only return artifacts that are directly relevant
   - Keep the list concise and to the point
3. Return ONLY a JSON object with this exact format:
{{
    "intents": ["intent1", "intent2"],
    "artifacts": ["artifact1", "artifact2"]
}}

Examples:
- "Can you send me your ML resume?" → {{"intents": ["send_materials"], "artifacts": ["ds_resume"]}}
- "Share your resume and let's schedule a call" → {{"intents": ["send_materials", "schedule"], "artifacts": ["ds_resume", "calendly"]}}
- "What time works for a meeting?" → {{"intents": ["schedule"], "artifacts": ["calendly"]}}
- "Can I get your LinkedIn?" → {{"intents": ["request_info"], "artifacts": ["linkedin_profile"]}}

Return ONLY valid JSON, nothing else:
"""
        
        try:
            content = self._call_gemini(prompt)
            
            logger.info(f"🔍 Gemini raw response: {content[:300]}...")
            
            # Remove markdown code blocks if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            try:
                result = json.loads(content)
                if isinstance(result, dict):
                    intents = result.get("intents", [])
                    artifacts = result.get("artifacts", [])
                    
                    # Filter to only valid intents and artifacts
                    valid_intents = [i for i in intents if i in known_intents]
                    valid_artifacts = [a for a in artifacts if a in known_artifacts]
                    
                    logger.info(f"✅ Classified intents: {valid_intents}")
                    logger.info(f"✅ Classified artifacts: {valid_artifacts}")
                    
                    return {
                        "intents": valid_intents if valid_intents else ["general_inquiry"],
                        "artifacts": valid_artifacts
                    }
            except json.JSONDecodeError:
                # Try to extract JSON object from text
                match = re.search(r'\{.*?\}', content, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        if isinstance(result, dict):
                            intents = result.get("intents", [])
                            artifacts = result.get("artifacts", [])
                            valid_intents = [i for i in intents if i in known_intents]
                            valid_artifacts = [a for a in artifacts if a in known_artifacts]
                            logger.info(f"✅ Classified intents: {valid_intents}")
                            logger.info(f"✅ Classified artifacts: {valid_artifacts}")
                            return {
                                "intents": valid_intents if valid_intents else ["general_inquiry"],
                                "artifacts": valid_artifacts
                            }
                    except:
                        pass
            
            # Fallback: try to find intent/artifact names in the response
            found_intents = []
            found_artifacts = []
            
            for intent in known_intents:
                if intent.lower() in content.lower():
                    found_intents.append(intent)
            
            for artifact in known_artifacts:
                if artifact.lower() in content.lower():
                    found_artifacts.append(artifact)
            
            if found_intents or found_artifacts:
                logger.info(f"✅ Classified (fallback) intents: {found_intents}")
                logger.info(f"✅ Classified (fallback) artifacts: {found_artifacts}")
                return {
                    "intents": found_intents if found_intents else ["general_inquiry"],
                    "artifacts": found_artifacts
                }
            
            logger.warning("⚠️ Could not parse intents/artifacts, using defaults")
            return {
                "intents": ["general_inquiry"],
                "artifacts": []
            }
            
        except Exception as e:
            logger.error(f"⚠️ Error classifying intent/artifacts: {e}")
            return {
                "intents": ["general_inquiry"],
                "artifacts": []
            }
    
    def generate_reply(
        self, 
        email_text: str, 
        intent: str,
        artifacts: List[str],
        faq_hits: List[Dict[str, Any]],
        graph_replies: List[str],
        user_name: str = "Assistant",
        user_tone: str = "polite, proactive, and professional"
    ) -> str:
        """
        Generate email reply using LLM with context.
        
        Args:
            email_text: Original email body
            intent: Detected intent
            artifacts: Detected artifacts
            faq_hits: FAQ retrieval results
            graph_replies: Replies from graph RAG intersection search
            user_name: Name of the user replying
            user_tone: Desired tone for the reply
            
        Returns:
            Generated draft reply text
        """
        prompt = self._build_prompt(
            email_text, intent, artifacts, faq_hits, graph_replies, user_name, user_tone
        )
        
        try:
            draft = self._call_gemini(prompt)
            logger.info("Successfully generated draft reply")
            return draft
            
        except Exception as e:
            logger.error(f"Draft generation failed: {e}")
            return "I apologize, but I'm unable to generate a reply at the moment. Please try again."
    
    def _build_prompt(
        self,
        email_text: str,
        intent: str,
        artifacts: List[str],
        faq_hits: List[Dict[str, Any]],
        graph_replies: List[str],
        user_name: str = "Assistant",
        user_tone: str = "polite, proactive, and professional"
    ) -> str:
        """Build the prompt for draft generation."""
        
        # Build FAQ section
        faq_section = "\n".join([
            f"{i+1}. Q: {f.get('question', '')}\n   A: {f.get('answer', '')}"
            for i, f in enumerate(faq_hits)
        ]) or "None"
        
        # Graph replies section
        graph_replies_section = ""
        if graph_replies and len(graph_replies) > 0:
            valid_replies = [r for r in graph_replies if r and r.strip()]
            if valid_replies:
                graph_replies_section = "\n".join([
                    f"{i+1}. Similar Reply Example {i+1}:\n   \"{reply[:300]}...\""
                    for i, reply in enumerate(valid_replies[:5])
                ])
            else:
                graph_replies_section = "None"
        else:
            graph_replies_section = "None"
        
        intents_str = intent
        artifacts_str = ", ".join(artifacts) if artifacts else "None"
        
        prompt = f"""You are **{user_name}**, a graduate student known for being {user_tone}.

Your job is to draft a short, natural, and professional email reply.

Keep it warm but not overly formal — think of how a thoughtful student would respond to a professor, coordinator, or peer.

**IMPORTANT**: Make sure to only output the email reply text, nothing else - no introductory phrases like "Here is my reply:" or "Reply:" or any similar phrases.

---

✉️ **Incoming Email**
\"\"\"{email_text}\"\"\"

🎯 **Detected Intents**: {intents_str}
📎 **Relevant Artifacts**: {artifacts_str}

📘 **Relevant FAQs** (Content Context)
{faq_section}

📧 **Similar Email Replies** (Graph RAG Context - examples of how similar emails were replied to)
{graph_replies_section}

---

Write your reply:
- Use similar tone and structure as the example replies above
- Acknowledge the sender and context
- If an action is requested, confirm or ask a polite follow-up question
- Include relevant artifacts/links if needed (based on detected artifacts)
- Keep the reply under 120 words
- Do NOT invent facts — only use what's in context
- End with: "Best Regards,\\n{user_name}"
"""
        
        return prompt
    
    def health_check(self) -> bool:
        """
        Check if Gemini service is healthy.
        
        Returns:
            True if service is healthy
        """
        try:
            # Try a simple call to verify the API is accessible
            test_response = self.model.generate_content("test")
            return test_response is not None
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

