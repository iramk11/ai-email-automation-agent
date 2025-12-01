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
    
    def classify_intent_and_artifacts(
        self,
        email_text: str,
        known_intents: List[str],
        known_artifacts: List[str],
        artifact_dict: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """
        Classify both intents AND artifacts from an email using LLM.
        NEW METHODOLOGY: Returns both intents and artifacts.
        
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
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response["message"]["content"].strip()
            
            logger.info(f"🔍 LLM raw response: {content[:300]}...")
            
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
        artifacts: List[str],  # NEW: Artifacts list
        faq_hits: List[Dict[str, Any]],
        graph_replies: List[str],  # NEW: Replies from graph RAG intersection search
        user_name: str = "Assistant",
        user_tone: str = "polite, proactive, and professional"
    ) -> str:
        """
        Generate email reply using LLM with context.
        NEW METHODOLOGY: Uses graph replies instead of style examples.
        
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
        
        # Debug: Check if graph_replies_section is in the prompt and has content
        if "Similar Email Replies" in prompt:
            replies_section_start = prompt.find("📧 **Similar Email Replies**")
            if replies_section_start != -1:
                # Extract the section
                next_section = prompt.find("---", replies_section_start)
                if next_section != -1:
                    replies_section = prompt[replies_section_start:next_section]
                    if "None" in replies_section or len(replies_section.strip().replace("📧 **Similar Email Replies**", "").replace("(Graph RAG Context - examples of how similar emails were replied to)", "").strip()) < 10:
                        logger.warning("⚠️ graph_replies_section in prompt appears to be empty or 'None'")
                    else:
                        logger.info(f"✅ graph_replies_section in prompt has content: {len(replies_section)} chars")
                        logger.debug(f"   Preview: {replies_section[:200]}...")
        
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
        artifacts: List[str],
        faq_hits: List[Dict[str, Any]],
        graph_replies: List[str],
        user_name: str = "Assistant",
        user_tone: str = "polite, proactive, and professional"
    ) -> str:
        """Build the prompt for draft generation WITHOUT style (using graph replies instead)."""
        
        # Build FAQ section
        faq_section = "\n".join([
            f"{i+1}. Q: {f.get('question', '')}\n   A: {f.get('answer', '')}"
            for i, f in enumerate(faq_hits)
        ]) or "None"
        
        # Graph replies section (NEW: replies from intersection search)
        graph_replies_section = ""
        logger.info(f"🔍 Building graph_replies_section: received {len(graph_replies) if graph_replies else 0} replies")
        
        if graph_replies and len(graph_replies) > 0:
            # Filter out empty replies
            valid_replies = [r for r in graph_replies if r and r.strip()]
            logger.info(f"   Valid replies after filtering: {len(valid_replies)}")
            
            if valid_replies:
                # Log sample of what we're adding
                for i, reply in enumerate(valid_replies[:3], 1):
                    logger.info(f"   Reply {i} preview: {reply[:100]}...")
                
                graph_replies_section = "\n".join([
                    f"{i+1}. Similar Reply Example {i+1}:\n   \"{reply[:300]}...\""
                    for i, reply in enumerate(valid_replies[:5])  # Top 5 replies
                ])
                logger.info(f"✅ Built graph_replies_section with {len(valid_replies)} examples (length: {len(graph_replies_section)} chars)")
            else:
                graph_replies_section = "None"
                logger.warning("⚠️ graph_replies list contains only empty strings")
        else:
            graph_replies_section = "None"
            logger.warning(f"⚠️ No graph replies provided (graph_replies={graph_replies})")
        
        # Final check: log if section is empty or just "None"
        if graph_replies_section == "None" or not graph_replies_section.strip():
            logger.warning("⚠️ graph_replies_section is empty or 'None' - prompt will not have graph context!")
        else:
            logger.info(f"✅ graph_replies_section has content: {len(graph_replies_section)} characters")
        
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

