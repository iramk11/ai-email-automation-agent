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
from backend.models.schemas import EmailRequest, EmailResponse, ContextUsed, FAQHit, GraphNodeHit, StyleExample

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
        self.top_k = top_k
        self.auto_send_threshold = auto_send_threshold
        self.default_user_name = default_user_name
        self.default_user_tone = default_user_tone
        
        logger.info("RAG service initialized successfully")
    
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
            
            # Step 1: Classify intents (can be multiple)
            intents = self.ollama_service.classify_intent(email_text, self.known_intents)
            primary_intent = intents[0] if intents else "general_inquiry"
            logger.info(f"Detected intents: {intents} (primary: {primary_intent})")
            
            # Step 2: Embed query for vector search
            query_vector = self.embedding_service.encode(email_text)
            logger.info("Generated query embedding")
            
            # Step 3: Search Qdrant for FAQs ONLY (separate search to ensure FAQs are always retrieved)
            faq_hits_raw = self.qdrant_service.search_faqs_only(query_vector, limit=self.top_k)
            logger.info(f"Retrieved {len(faq_hits_raw)} FAQ hits from Qdrant")
            
            # Step 4: Intent-based graph retrieval (using NetworkX, NO Qdrant for graph nodes)
            intent_graph_nodes = self.graph_service.get_nodes_by_intents(intents, limit=5)
            
            # Convert to graph hit format
            graph_hits_raw = []
            for node in intent_graph_nodes:
                graph_hits_raw.append({
                    "score": 0.75,  # Intent-based matches get fixed score
                    "node_name": node["name"],
                    "node_type": node["type"],
                    "neighbors": node["neighbors"],
                    "relationships": node.get("relationships", {"outgoing": [], "incoming": []})
                })
            
            logger.info(f"Intent-based graph retrieval: {len(graph_hits_raw)} graph nodes")
            
            # Step 5: Style-based retrieval (Gmail-style approach)
            style_examples = self.qdrant_service.search_style(query_vector, limit=3)
            logger.info(f"Retrieved {len(style_examples)} style examples")
            
            # Convert to proper models
            faq_hits = [FAQHit(**faq) for faq in faq_hits_raw]
            graph_hits = [GraphNodeHit(**node) for node in graph_hits_raw]
            
            logger.info(f"Total retrieval: {len(faq_hits)} FAQ hits, {len(graph_hits)} graph hits, {len(style_examples)} style examples")
            
            # Log detailed FAQ context
            logger.info("="*70)
            logger.info("📚 FAQ CONTEXT BEING USED:")
            for i, faq in enumerate(faq_hits[:3], 1):  # Show top 3
                logger.info(f"  {i}. [Score: {faq.score:.3f}]")
                logger.info(f"     Q: {faq.question[:80]}...")
                logger.info(f"     A: {faq.answer[:100]}...")
            if len(faq_hits) > 3:
                logger.info(f"  ... and {len(faq_hits) - 3} more FAQs")
            
            # Log detailed graph context
            logger.info("🕸️  GRAPH CONTEXT BEING USED:")
            for i, node in enumerate(graph_hits, 1):
                logger.info(f"  {i}. [Score: {node.score:.3f}] {node.node_name} (type: {node.node_type})")
                logger.info(f"     Neighbors: {', '.join(node.neighbors[:5])}")
            
            # Step 5: Expand graph context
            expanded_graph = self.graph_service.expand_graph_hits(graph_hits_raw)
            logger.info(f"Expanded {len(expanded_graph)} graph nodes")
            
            if expanded_graph:
                logger.info("🔗 EXPANDED GRAPH RELATIONSHIPS:")
                for node, neighbors in list(expanded_graph.items())[:3]:
                    logger.info(f"  {node} → {', '.join(neighbors[:5])}")
            
            logger.info("="*70)
            
            # Step 6: Generate draft reply (use all intents for context + style examples)
            draft_reply = self.ollama_service.generate_reply(
                email_text=email_text,
                intent=", ".join(intents),  # Pass all intents as comma-separated string
                faq_hits=faq_hits_raw,
                graph_hits=graph_hits_raw,
                expanded_graph=expanded_graph,
                style_examples=style_examples,  # ✅ NEW: Pass style examples
                user_name=user_name,
                user_tone=self.default_user_tone
            )
            
            # Step 7: Calculate confidence score (using top FAQ hit score)
            confidence_score = faq_hits[0].score if faq_hits else 0.0
            if not faq_hits and graph_hits:
                confidence_score = graph_hits[0].score
            
            auto_send = confidence_score >= self.auto_send_threshold
            
            logger.info(f"Generated reply with confidence: {confidence_score:.3f}, auto_send: {auto_send}")
            logger.info("="*70)
            logger.info("✉️  GENERATED DRAFT REPLY:")
            logger.info(draft_reply)
            logger.info("="*70)
            
            # Convert style examples to proper models
            style_examples_models = [StyleExample(**s) for s in style_examples]
            
            # Build response
            response = EmailResponse(
                draft_reply=draft_reply,
                intent=primary_intent,  # Return primary intent
                confidence_score=confidence_score,
                auto_send=auto_send,
                context_used=ContextUsed(
                    faq_hits=faq_hits,
                    graph_nodes=graph_hits,
                    expanded_graph=expanded_graph,
                    style_examples=style_examples_models  # ✅ NEW: Include style examples
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

