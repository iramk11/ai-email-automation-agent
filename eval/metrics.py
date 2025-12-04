"""
Evaluation metrics for email reply generation.
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Lazy import flags - will be set when methods are called
ROUGE_AVAILABLE = None
MAUVE_AVAILABLE = None
SENTENCE_TRANSFORMERS_AVAILABLE = None


class MetricsCalculator:
    """Calculator for all evaluation metrics."""
    
    def __init__(self):
        """Initialize metrics calculator."""
        self.rouge_scorer = None
        self.sentence_model = None
        # Lazy initialization - models will be loaded when first needed
    
    def calculate_rouge_scores(
        self, 
        generated: str, 
        reference: str
    ) -> Dict[str, float]:
        """
        Calculate ROUGE-1, ROUGE-2, and ROUGE-L scores.
        
        Args:
            generated: Generated reply text
            reference: Ground truth reply text
            
        Returns:
            Dictionary with rouge1, rouge2, rougeL scores (f-measure)
        """
        global ROUGE_AVAILABLE
        if ROUGE_AVAILABLE is None:
            try:
                from rouge_score import rouge_scorer
                self.rouge_scorer = rouge_scorer.RougeScorer(
                    ['rouge1', 'rouge2', 'rougeL'],
                    use_stemmer=True
                )
                ROUGE_AVAILABLE = True
                logger.info("✅ ROUGE scorer initialized")
            except ImportError:
                ROUGE_AVAILABLE = False
                logger.warning("rouge-score not available. Install with: pip install rouge-score")
        
        if not ROUGE_AVAILABLE:
            logger.warning("ROUGE not available, returning zeros")
            return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
        
        try:
            scores = self.rouge_scorer.score(reference, generated)
            return {
                "rouge1": scores['rouge1'].fmeasure,
                "rouge2": scores['rouge2'].fmeasure,
                "rougeL": scores['rougeL'].fmeasure,
                "rouge1_precision": scores['rouge1'].precision,
                "rouge1_recall": scores['rouge1'].recall,
                "rouge2_precision": scores['rouge2'].precision,
                "rouge2_recall": scores['rouge2'].recall,
                "rougeL_precision": scores['rougeL'].precision,
                "rougeL_recall": scores['rougeL'].recall,
            }
        except Exception as e:
            logger.error(f"Error calculating ROUGE scores: {e}")
            return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    
    def calculate_mauve_score(
        self,
        generated_texts: List[str],
        reference_texts: List[str]
    ) -> Dict[str, float]:
        """
        Calculate MAUVE score for distributional similarity.
        
        Args:
            generated_texts: List of generated reply texts
            reference_texts: List of ground truth reply texts
            
        Returns:
            Dictionary with mauve_score and other statistics
        """
        if not MAUVE_AVAILABLE:
            logger.warning("MAUVE not available, returning None")
            return {"mauve_score": None, "error": "MAUVE library not installed"}
        
        try:
            # MAUVE requires tokenized text
            out = mauve.compute_mauve(
                p_text=generated_texts,
                q_text=reference_texts,
                device_id=0,
                verbose=False
            )
            
            return {
                "mauve_score": float(out.mauve),
                "divergence_curve": out.divergence_curve.tolist() if hasattr(out, 'divergence_curve') else None
            }
        except Exception as e:
            logger.error(f"Error calculating MAUVE: {e}")
            return {"mauve_score": None, "error": str(e)}
    
    def calculate_expert_score(
        self,
        generated: str,
        reference: str,
        user_style_examples: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Calculate ExPerT (Effective & Explainable Personalized Text) score.
        
        ExPerT measures:
        1. Semantic similarity to reference
        2. Style similarity to user's past emails
        3. Personalization quality
        
        Args:
            generated: Generated reply text
            reference: Ground truth reply text
            user_style_examples: List of example replies from user (for style matching)
            
        Returns:
            Dictionary with expert scores
        """
        global SENTENCE_TRANSFORMERS_AVAILABLE
        if SENTENCE_TRANSFORMERS_AVAILABLE is None:
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                    SENTENCE_TRANSFORMERS_AVAILABLE = True
                    logger.info("✅ Sentence transformer model loaded for ExPerT")
                except Exception as e:
                    SENTENCE_TRANSFORMERS_AVAILABLE = False
                    logger.warning(f"⚠️ Could not load sentence transformer: {e}")
            except ImportError:
                SENTENCE_TRANSFORMERS_AVAILABLE = False
                logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE or self.sentence_model is None:
            logger.warning("Sentence transformers not available for ExPerT")
            return {"expert_semantic": 0.0, "expert_style": 0.0, "expert_overall": 0.0}
        
        try:
            # 1. Semantic similarity (generated vs reference)
            embeddings = self.sentence_model.encode([generated, reference])
            semantic_sim = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            # 2. Style similarity (if user examples provided)
            style_sim = 0.0
            if user_style_examples and len(user_style_examples) > 0:
                # Encode generated and all style examples
                style_embeddings = self.sentence_model.encode([generated] + user_style_examples)
                generated_emb = style_embeddings[0]
                
                # Calculate average similarity to style examples
                style_similarities = [
                    np.dot(generated_emb, style_emb) / (
                        np.linalg.norm(generated_emb) * np.linalg.norm(style_emb)
                    )
                    for style_emb in style_embeddings[1:]
                ]
                style_sim = np.mean(style_similarities) if style_similarities else 0.0
            
            # 3. Overall ExPerT score (weighted combination)
            # Weight: 60% semantic, 40% style (if available)
            if user_style_examples:
                expert_overall = 0.6 * semantic_sim + 0.4 * style_sim
            else:
                expert_overall = semantic_sim  # Only semantic if no style examples
            
            return {
                "expert_semantic": float(semantic_sim),
                "expert_style": float(style_sim),
                "expert_overall": float(expert_overall)
            }
        except Exception as e:
            logger.error(f"Error calculating ExPerT: {e}")
            return {"expert_semantic": 0.0, "expert_style": 0.0, "expert_overall": 0.0}
    
    def calculate_llm_judge_score(
        self,
        generated: str,
        reference: str,
        user_style_examples: List[str],
        llm_service  # Can be Gemini or Ollama service
    ) -> Dict[str, Any]:
        """
        Use LLM-as-a-judge to evaluate style match.
        
        Args:
            generated: Generated reply text
            reference: Ground truth reply text
            user_style_examples: List of example replies from user
            ollama_service: OllamaService instance for LLM calls
            
        Returns:
            Dictionary with LLM judge scores and reasoning
        """
        # Build style examples context
        style_examples_text = "\n".join([
            f"Example {i+1}: {ex[:200]}..."
            for i, ex in enumerate(user_style_examples[:5])
        ]) if user_style_examples else "No examples available"
        
        prompt = f"""You are an expert evaluator of email writing style and tone.

Your task is to evaluate how well a generated email reply matches the user's typical writing style.

**IMPORTANT: Be lenient and generous in your scoring. Give credit for partial matches and similar approaches. Only use low scores (1-2) for clearly inappropriate or very different styles.**

**User's Style Examples:**
{style_examples_text}

**Generated Reply:**
{generated}

**Reference Reply (for context):**
{reference}

**Evaluation Rubric:**
Rate the generated reply on a scale of 1-5 for each dimension (be generous - use 3-5 for reasonable matches):

1. **Tone Match** (1-5): How well does the tone match? (formality level, warmth, politeness) - Be lenient: 3+ if tone is generally appropriate
2. **Phrasing Style** (1-5): How similar is the phrasing to the user's typical style? - Be lenient: 3+ if phrasing is reasonable
3. **Structure** (1-5): Does it follow the user's typical email structure? - Be lenient: 3+ if structure is acceptable
4. **Content Appropriateness** (1-5): Is the content appropriate for the context? - Be lenient: 3+ if content is relevant
5. **Overall Style Match** (1-5): Overall assessment of style similarity - Be lenient: 3+ if generally appropriate

Return ONLY a JSON object with this exact format:
{{
    "tone_match": <1-5>,
    "phrasing_style": <1-5>,
    "structure": <1-5>,
    "content_appropriateness": <1-5>,
    "overall_style_match": <1-5>
}}

Return ONLY valid JSON, nothing else:"""
        
        try:
            # Try to use the service's _call_gemini method if it's Gemini, otherwise use Ollama
            if hasattr(llm_service, '_call_gemini'):
                # It's a Gemini service
                content = llm_service._call_gemini(prompt)
            else:
                # It's an Ollama service
                import ollama
                response = ollama.chat(
                    model=llm_service.model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response["message"]["content"].strip()
            
            # Parse JSON from response
            import json
            import re
            
            # Remove markdown code blocks
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            # Try to extract JSON
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                result = json.loads(match.group())
                return {
                    "tone_match": result.get("tone_match", 0),
                    "phrasing_style": result.get("phrasing_style", 0),
                    "structure": result.get("structure", 0),
                    "content_appropriateness": result.get("content_appropriateness", 0),
                    "overall_style_match": result.get("overall_style_match", 0),
                    "average_score": np.mean([
                        result.get("tone_match", 0),
                        result.get("phrasing_style", 0),
                        result.get("structure", 0),
                        result.get("content_appropriateness", 0),
                        result.get("overall_style_match", 0)
                    ])
                }
            else:
                logger.warning("Could not parse LLM judge response")
                return {"error": "Could not parse LLM response"}
        except Exception as e:
            logger.error(f"Error in LLM judge evaluation: {e}")
            return {"error": str(e)}

