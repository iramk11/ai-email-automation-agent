"""
Main evaluation orchestrator for AI Email Automation Agent.
"""
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import json

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import (
    BASE_DIR, QDRANT_DATA_PATH, GRAPH_DATA_PATH,
    EMBEDDING_MODEL, OLLAMA_MODEL, KNOWN_INTENTS,
    KNOWN_ARTIFACTS, ARTIFACT_DICTIONARY, TOP_K_RESULTS,
    AUTO_SEND_THRESHOLD, DEFAULT_USER_NAME, DEFAULT_USER_TONE
)
from backend.services.embedding_service import EmbeddingService
from backend.services.qdrant_service import QdrantService
from backend.services.graph_service import GraphService
from backend.services.ollama_service import OllamaService
from backend.services.gemini_service import GeminiService
from backend.services.rag_service import RAGService
from backend.models.schemas import EmailRequest

from eval.utils import load_golden_dataset, save_results, calculate_artifact_hit_rate, calculate_intent_hit_rate
from eval.metrics import MetricsCalculator

logger = logging.getLogger(__name__)


class EmailEvaluator:
    """Main evaluator for email generation system."""
    
    def __init__(self, dataset_path: str):
        """
        Initialize evaluator with services.
        
        Args:
            dataset_path: Path to golden benchmark dataset
        """
        self.dataset_path = dataset_path
        self.rag_service = None
        self.graph_service = None
        self.metrics_calc = MetricsCalculator()
        self.results = []
        
        logger.info("Initializing evaluation services...")
        self._initialize_services()
        logger.info("✅ Services initialized")
    
    def _initialize_services(self):
        """Initialize all backend services."""
        try:
            # Initialize embedding service
            embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
            
            # Initialize Qdrant service
            qdrant_path = BASE_DIR / "graphrag_local" / "qdrant_data"
            if not qdrant_path.exists():
                qdrant_path = QDRANT_DATA_PATH
            
            logger.info(f"Using Qdrant data path: {qdrant_path}")
            qdrant_service = QdrantService(
                data_path=str(qdrant_path),
                collection_name="knowledge_space"
            )
            
            # Initialize graph service
            graph_service = GraphService(
                graph_path=str(GRAPH_DATA_PATH) if GRAPH_DATA_PATH.exists() else None
            )
            
            # Rebuild graph if needed (same logic as main.py)
            if not graph_service.node_to_email_ids or len(graph_service.node_to_email_ids) == 0:
                logger.info("Rebuilding graph from labels...")
                label_files = [
                    BASE_DIR / "data" / "generated_email_pairs.json",
                    BASE_DIR / "student_email_pairs.labels.jsonl",
                ]
                
                labels = []
                labels_file = None
                for label_file in label_files:
                    if label_file.exists():
                        labels_file = label_file
                        break
                
                if labels_file:
                    if labels_file.suffix == '.json':
                        with open(labels_file, 'r', encoding='utf-8') as f:
                            labels = json.load(f)
                    else:
                        with open(labels_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip():
                                    labels.append(json.loads(line))
                    
                    graph_service.graph = graph_service.graph.__class__()
                    graph_service.email_id_to_reply = {}
                    graph_service.node_to_email_ids = {}
                    graph_service.build_from_labels(labels)
                    graph_service.save_graph(str(GRAPH_DATA_PATH))
                    logger.info("✅ Graph rebuilt and saved")
            
            self.graph_service = graph_service
            
            # Initialize Gemini service (preferred) or Ollama as fallback
            try:
                # Try Gemini first - use gemini-2.0-flash
                llm_service = GeminiService(model_name="gemini-2.0-flash")
                logger.info("✅ Using Gemini service")
            except Exception as e:
                logger.warning(f"⚠️ Gemini not available ({e}), falling back to Ollama")
                llm_service = OllamaService(model_name=OLLAMA_MODEL)
            
            # Initialize RAG service
            self.rag_service = RAGService(
                embedding_service=embedding_service,
                qdrant_service=qdrant_service,
                graph_service=graph_service,
                ollama_service=llm_service,  # Works with both Gemini and Ollama (same interface)
                known_intents=KNOWN_INTENTS,
                known_artifacts=KNOWN_ARTIFACTS,
                artifact_dict=ARTIFACT_DICTIONARY,
                top_k=TOP_K_RESULTS,
                auto_send_threshold=AUTO_SEND_THRESHOLD,
                default_user_name=DEFAULT_USER_NAME,
                default_user_tone=DEFAULT_USER_TONE
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}", exc_info=True)
            raise
    
    def _get_user_style_examples(self, limit: int = 10) -> List[str]:
        """
        Get example replies from user's past emails for style matching.
        
        Args:
            limit: Maximum number of examples to return
            
        Returns:
            List of example reply texts
        """
        if not self.graph_service:
            return []
        
        # Get all replies from the graph
        all_replies = list(self.graph_service.email_id_to_reply.values())
        
        # Filter out empty replies
        valid_replies = [r for r in all_replies if r and r.strip()]
        
        # Return up to limit examples
        return valid_replies[:limit]
    
    async def evaluate_single_email(
        self,
        entry: Dict[str, Any],
        user_style_examples: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate a single email from the golden dataset.
        
        Args:
            entry: Email entry from golden dataset
            user_style_examples: List of user's past replies for style matching
            
        Returns:
            Dictionary with evaluation results
        """
        email_id = entry.get("id", "unknown")
        labels = entry.get("labels", {})
        prospect_email = entry.get("prospect_email", "")
        ground_truth_reply = entry.get("reply", "")
        ground_truth_artifacts = labels.get("artifacts", [])
        ground_truth_intents = labels.get("intents", [])
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Evaluating: {email_id}")
        logger.info(f"{'='*70}")
        
        try:
            # Create email request
            email_request = EmailRequest(
                subject=entry.get("subject", ""),
                sender=entry.get("sender_email", "unknown@example.com"),
                body=prospect_email,
                user_name=DEFAULT_USER_NAME
            )
            
            # Generate reply using RAG service
            logger.info("Generating reply...")
            response = await self.rag_service.generate_reply(email_request)
            
            generated_reply = response.draft_reply
            predicted_artifacts = response.artifacts
            
            # Get all intents by re-classifying (response.intent is only primary intent)
            # This ensures we capture all intents for evaluation
            # Use the LLM service (could be Gemini or Ollama)
            llm_service = self.rag_service.ollama_service  # Same interface for both
            classification_result = llm_service.classify_intent_and_artifacts(
                email_text=prospect_email,
                known_intents=KNOWN_INTENTS,
                known_artifacts=KNOWN_ARTIFACTS,
                artifact_dict=ARTIFACT_DICTIONARY
            )
            predicted_intents = classification_result.get("intents", [response.intent] if response.intent else [])
            
            logger.info(f"✅ Generated reply: {generated_reply[:100]}...")
            logger.info(f"✅ Predicted artifacts: {predicted_artifacts}")
            logger.info(f"✅ Ground truth artifacts: {ground_truth_artifacts}")
            
            # Calculate metrics
            results = {
                "email_id": email_id,
                "prospect_email": prospect_email,
                "ground_truth_reply": ground_truth_reply,
                "generated_reply": generated_reply,
                "ground_truth_artifacts": ground_truth_artifacts,
                "predicted_artifacts": predicted_artifacts,
                "ground_truth_intents": ground_truth_intents,
                "predicted_intents": predicted_intents,
            }
            
            # 1. Artifact Hit Rate (with interchangeable support)
            logger.info("Calculating artifact hit rate...")
            artifact_metrics = calculate_artifact_hit_rate(
                predicted_artifacts,
                ground_truth_artifacts
            )
            results["artifact_metrics"] = artifact_metrics
            logger.info(f"   Artifact F1: {artifact_metrics['f1']:.3f}")
            
            # 1b. Intent Hit Rate (with interchangeable support)
            logger.info("Calculating intent hit rate...")
            intent_metrics = calculate_intent_hit_rate(
                predicted_intents,
                ground_truth_intents
            )
            results["intent_metrics"] = intent_metrics
            logger.info(f"   Intent F1: {intent_metrics['f1']:.3f}")
            
            # 2. ROUGE Scores
            logger.info("Calculating ROUGE scores...")
            rouge_scores = self.metrics_calc.calculate_rouge_scores(
                generated_reply,
                ground_truth_reply
            )
            results["rouge_scores"] = rouge_scores
            logger.info(f"   ROUGE-L: {rouge_scores['rougeL']:.3f}")
            
            # 3. ExPerT Score
            logger.info("Calculating ExPerT score...")
            expert_scores = self.metrics_calc.calculate_expert_score(
                generated_reply,
                ground_truth_reply,
                user_style_examples
            )
            results["expert_scores"] = expert_scores
            logger.info(f"   ExPerT Overall: {expert_scores['expert_overall']:.3f}")
            
            # 4. LLM-as-a-judge
            logger.info("Calculating LLM judge score...")
            llm_judge_scores = self.metrics_calc.calculate_llm_judge_score(
                generated_reply,
                ground_truth_reply,
                user_style_examples,
                self.rag_service.ollama_service  # Works with both Gemini and Ollama
            )
            results["llm_judge_scores"] = llm_judge_scores
            if "average_score" in llm_judge_scores:
                logger.info(f"   LLM Judge Average: {llm_judge_scores['average_score']:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error evaluating email {email_id}: {e}", exc_info=True)
            return {
                "email_id": email_id,
                "error": str(e),
                "prospect_email": prospect_email,
                "ground_truth_reply": ground_truth_reply
            }
    
    async def evaluate_dataset(
        self,
        limit: int = None,
        start_idx: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluate the entire golden dataset.
        
        Args:
            limit: Maximum number of emails to evaluate (None = all)
            start_idx: Starting index in dataset
            
        Returns:
            Dictionary with aggregated results
        """
        # Load dataset
        dataset = load_golden_dataset(self.dataset_path)
        
        # Limit dataset if specified
        if limit:
            dataset = dataset[start_idx:start_idx + limit]
        else:
            dataset = dataset[start_idx:]
        
        logger.info(f"Evaluating {len(dataset)} emails (starting from index {start_idx})")
        
        # Get user style examples
        user_style_examples = self._get_user_style_examples(limit=20)
        logger.info(f"Loaded {len(user_style_examples)} user style examples")
        
        # Evaluate each email
        individual_results = []
        for i, entry in enumerate(dataset, 1):
            logger.info(f"\n[{i}/{len(dataset)}] Processing email...")
            result = await self.evaluate_single_email(entry, user_style_examples)
            individual_results.append(result)
        
        # Calculate aggregate metrics
        logger.info("\n" + "="*70)
        logger.info("Calculating aggregate metrics...")
        logger.info("="*70)
        
        # Filter out errors
        valid_results = [r for r in individual_results if "error" not in r]
        
        if len(valid_results) == 0:
            logger.error("No valid results to aggregate!")
            return {
                "total_emails": len(dataset),
                "valid_results": 0,
                "errors": len(individual_results) - len(valid_results),
                "individual_results": individual_results
            }
        
        # Aggregate artifact metrics
        artifact_f1_scores = [r["artifact_metrics"]["f1"] for r in valid_results if "artifact_metrics" in r]
        artifact_precision = [r["artifact_metrics"]["precision"] for r in valid_results if "artifact_metrics" in r]
        artifact_recall = [r["artifact_metrics"]["recall"] for r in valid_results if "artifact_metrics" in r]
        artifact_exact_match = [r["artifact_metrics"]["exact_match"] for r in valid_results if "artifact_metrics" in r]
        
        # Aggregate intent metrics
        intent_f1_scores = [r["intent_metrics"]["f1"] for r in valid_results if "intent_metrics" in r]
        intent_precision = [r["intent_metrics"]["precision"] for r in valid_results if "intent_metrics" in r]
        intent_recall = [r["intent_metrics"]["recall"] for r in valid_results if "intent_metrics" in r]
        intent_exact_match = [r["intent_metrics"]["exact_match"] for r in valid_results if "intent_metrics" in r]
        
        # Aggregate ROUGE scores
        rouge1_scores = [r["rouge_scores"]["rouge1"] for r in valid_results if "rouge_scores" in r]
        rouge2_scores = [r["rouge_scores"]["rouge2"] for r in valid_results if "rouge_scores" in r]
        rougeL_scores = [r["rouge_scores"]["rougeL"] for r in valid_results if "rouge_scores" in r]
        
        # Aggregate ExPerT scores
        expert_overall = [r["expert_scores"]["expert_overall"] for r in valid_results if "expert_scores" in r]
        expert_semantic = [r["expert_scores"]["expert_semantic"] for r in valid_results if "expert_scores" in r]
        expert_style = [r["expert_scores"]["expert_style"] for r in valid_results if "expert_scores" in r]
        
        # Aggregate LLM judge scores
        llm_judge_avg = [
            r["llm_judge_scores"]["average_score"]
            for r in valid_results
            if "llm_judge_scores" in r and "average_score" in r["llm_judge_scores"]
        ]
        
        # Skip MAUVE calculation (as requested)
        logger.info("Skipping MAUVE calculation (as requested)")
        mauve_results = {"mauve_score": None, "note": "MAUVE calculation skipped"}
        
        # Build aggregate results
        aggregate_results = {
            "total_emails": len(dataset),
            "valid_results": len(valid_results),
            "errors": len(individual_results) - len(valid_results),
            "aggregate_metrics": {
                "artifact_hit_rate": {
                    "mean_f1": float(sum(artifact_f1_scores) / len(artifact_f1_scores)) if artifact_f1_scores else 0.0,
                    "mean_precision": float(sum(artifact_precision) / len(artifact_precision)) if artifact_precision else 0.0,
                    "mean_recall": float(sum(artifact_recall) / len(artifact_recall)) if artifact_recall else 0.0,
                    "exact_match_rate": float(sum(artifact_exact_match) / len(artifact_exact_match)) if artifact_exact_match else 0.0,
                },
                "intent_hit_rate": {
                    "mean_f1": float(sum(intent_f1_scores) / len(intent_f1_scores)) if intent_f1_scores else 0.0,
                    "mean_precision": float(sum(intent_precision) / len(intent_precision)) if intent_precision else 0.0,
                    "mean_recall": float(sum(intent_recall) / len(intent_recall)) if intent_recall else 0.0,
                    "exact_match_rate": float(sum(intent_exact_match) / len(intent_exact_match)) if intent_exact_match else 0.0,
                },
                "rouge_scores": {
                    "mean_rouge1": float(sum(rouge1_scores) / len(rouge1_scores)) if rouge1_scores else 0.0,
                    "mean_rouge2": float(sum(rouge2_scores) / len(rouge2_scores)) if rouge2_scores else 0.0,
                    "mean_rougeL": float(sum(rougeL_scores) / len(rougeL_scores)) if rougeL_scores else 0.0,
                },
                "expert_scores": {
                    "mean_overall": float(sum(expert_overall) / len(expert_overall)) if expert_overall else 0.0,
                    "mean_semantic": float(sum(expert_semantic) / len(expert_semantic)) if expert_semantic else 0.0,
                    "mean_style": float(sum(expert_style) / len(expert_style)) if expert_style else 0.0,
                },
                "llm_judge": {
                    "mean_average_score": float(sum(llm_judge_avg) / len(llm_judge_avg)) if llm_judge_avg else 0.0,
                },
                "mauve": mauve_results
            },
            "individual_results": individual_results
        }
        
        return aggregate_results

