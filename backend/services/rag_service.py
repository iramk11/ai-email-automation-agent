"""
RAG (Retrieval-Augmented Generation) orchestration service.
Coordinates all components: embedding, vector search, graph, and LLM.
"""
from typing import Dict, Any
import logging
from backend.services.embedding_service import EmbeddingService
from backend.services.qdrant_service import QdrantService
from backend.services.graph_service import GraphService
from backend.services.ollama_service import OllamaService
from backend.models.schemas import EmailRequest, EmailResponse, ContextUsed, FAQHit

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG orchestration service."""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
        graph_service: GraphService,
        ollama_service: OllamaService,
        known_intents: list,
        known_artifacts: list,
        artifact_dict: dict,
        top_k: int = 6,
        auto_send_threshold: float = 0.85,
        default_user_name: str = "Assistant",
        default_user_tone: str = "polite, proactive, and professional"
    ):
        """
        Initialize RAG service with all dependencies.
        
        Args:
            embedding_service: Service for text embeddings
            qdrant_service: Service for vector search
            graph_service: Service for graph operations
            ollama_service: Service for LLM operations
            known_intents: List of known intent labels
            top_k: Number of results to retrieve
            auto_send_threshold: Confidence threshold for auto-send
            default_user_name: Default user name for replies
            default_user_tone: Default tone for replies
        """
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service
        self.graph_service = graph_service
        self.ollama_service = ollama_service
        self.known_intents = known_intents
        self.known_artifacts = known_artifacts
        self.artifact_dict = artifact_dict
        self.top_k = top_k
        self.auto_send_threshold = auto_send_threshold
        self.default_user_name = default_user_name
        self.default_user_tone = default_user_tone
        
        logger.info("RAG service initialized successfully (enhanced methodology)")
    
    async def generate_reply(self, request: EmailRequest) -> EmailResponse:
        """
        Generate an email reply using the full RAG pipeline.
        
        Args:
            request: Email request containing subject, sender, body
            
        Returns:
            EmailResponse with generated draft and context
        """
        try:
            email_text = request.body
            user_name = request.user_name or self.default_user_name
            
            logger.info(f"Processing email from {request.sender}")
            logger.info("="*70)
            logger.info("🚀 ENHANCED EMAIL ANSWERING PIPELINE")
            logger.info("="*70)
            
            # Step 1: Enhanced intent + artifact classification (NEW)
            logger.info("📋 Step 1: Intent + Artifact Classification")
            classification_result = self.ollama_service.classify_intent_and_artifacts(
                email_text=email_text,
                known_intents=self.known_intents,
                known_artifacts=self.known_artifacts,
                artifact_dict=self.artifact_dict
            )
            
            intents = classification_result["intents"]
            artifacts = classification_result["artifacts"]
            primary_intent = intents[0] if intents else "general_inquiry"
            
            logger.info(f"   ✅ Intents: {intents}")
            logger.info(f"   ✅ Artifacts: {artifacts}")
            logger.info(f"   ✅ Primary Intent: {primary_intent}")
            
            # Step 2: Embed query for vector search
            query_vector = self.embedding_service.encode(email_text)
            logger.info("📋 Step 2: FAQ Search")
            
            # Step 3: Search Qdrant for FAQs ONLY (keep as-is)
            faq_hits_raw = self.qdrant_service.search_faqs_only(query_vector, limit=self.top_k)
            logger.info(f"   ✅ FAQ hits: {len(faq_hits_raw)}")
            
            # Step 4: Graph RAG search (NEW: intersection of intents and artifacts)
            logger.info("📋 Step 3: Graph RAG Search (Intent + Artifact Intersection)")
            
            matching_email_ids = []
            graph_replies = []
            
            if intents and artifacts:
                matching_email_ids = self.graph_service.find_emails_by_intent_artifact_intersection(
                    intents=intents,
                    artifacts=artifacts
                )
                
                # Extract replies from matching emails
                graph_replies = self.graph_service.get_replies_by_email_ids(matching_email_ids)
                
                logger.info(f"   ✅ Matching emails: {len(matching_email_ids)}")
                logger.info(f"   ✅ Replies extracted: {len(graph_replies)}")
                if graph_replies:
                    logger.info("   📧 Sample replies:")
                    for i, reply in enumerate(graph_replies[:3], 1):
                        logger.info(f"      {i}. {reply[:100]}...")
            else:
                logger.warning("   ⚠️ Need at least 1 intent AND 1 artifact for graph search")
            
            # Convert to proper models
            faq_hits = [FAQHit(**faq) for faq in faq_hits_raw]
            
            logger.info("="*70)
            logger.info("🔍 RETRIEVED CONTEXT")
            logger.info("="*70)
            
            # Log detailed FAQ context
            logger.info("📚 FAQ Chunks:")
            if faq_hits:
                for i, faq in enumerate(faq_hits[:3], 1):
                    logger.info(f"  {i}. [Score {faq.score:.3f}] Q: {faq.question}")
                    logger.info(f"     A: {faq.answer[:80]}...")
            else:
                logger.info("  None")
            
            logger.info(f"\n📧 Graph Replies: {len(graph_replies)}")
            if graph_replies:
                for i, reply in enumerate(graph_replies[:3], 1):
                    logger.info(f"  {i}. {reply[:100]}...")
            else:
                logger.info("  None")
            
            logger.info("="*70)
            
            # Step 5: Generate draft reply (NEW: uses graph replies instead of style)
            logger.info("📋 Step 4: Generating Reply")
            draft_reply = self.ollama_service.generate_reply(
                email_text=email_text,
                intent=", ".join(intents),
                artifacts=artifacts,
                faq_hits=faq_hits_raw,
                graph_replies=graph_replies,
                user_name=user_name,
                user_tone=self.default_user_tone
            )
            
            # Step 6: Calculate confidence score (using top FAQ hit score)
            confidence_score = faq_hits[0].score if faq_hits else 0.0
            auto_send = confidence_score >= self.auto_send_threshold
            
            logger.info(f"Generated reply with confidence: {confidence_score:.3f}, auto_send: {auto_send}")
            logger.info("="*70)
            logger.info("✉️  GENERATED DRAFT REPLY:")
            logger.info(draft_reply)
            logger.info("="*70)
            
            # Build response
            response = EmailResponse(
                draft_reply=draft_reply,
                intent=primary_intent,
                artifacts=artifacts,
                confidence_score=confidence_score,
                auto_send=auto_send,
                context_used=ContextUsed(
                    faq_hits=faq_hits,
                    graph_replies=graph_replies,
                    graph_emails_found=len(matching_email_ids)
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}", exc_info=True)
            raise
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all services.
        
        Returns:
            Dictionary with service health status
        """
        return {
            "qdrant": self.qdrant_service.health_check(),
            "graph": self.graph_service.health_check(),
            "ollama": self.ollama_service.health_check()
        }

