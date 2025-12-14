"""
Unit tests for RAGService.
"""
import pytest
from unittest.mock import Mock, MagicMock
from backend.models.schemas import EmailRequest
from backend.tests.conftest import rag_service, sample_email_request


class TestRAGService:
    """Test cases for RAGService."""
    
    @pytest.mark.asyncio
    async def test_generate_reply_success(self, rag_service, sample_email_request):
        """Test successful reply generation."""
        response = await rag_service.generate_reply(sample_email_request)
        
        assert response is not None
        assert hasattr(response, 'draft_reply')
        assert hasattr(response, 'intent')
        assert hasattr(response, 'artifacts')
        assert hasattr(response, 'confidence_score')
        assert isinstance(response.draft_reply, str)
        assert len(response.draft_reply) > 0
    
    @pytest.mark.asyncio
    async def test_generate_reply_with_faq_hits(self, rag_service, sample_email_request):
        """Test reply generation with FAQ hits."""
        # Mock FAQ hits - RAG service expects dict format, not FAQHit objects
        rag_service.qdrant_service.search_faqs_only.return_value = [
            {
                "score": 0.9,
                "question": "How to schedule?",
                "answer": "Use Calendly",
                "faq_id": 1
            }
        ]
        
        response = await rag_service.generate_reply(sample_email_request)
        
        assert response is not None
        assert len(response.context_used.faq_hits) > 0
    
    @pytest.mark.asyncio
    async def test_generate_reply_with_graph_nodes(self, rag_service, sample_email_request):
        """Test reply generation with graph nodes."""
        # Mock graph nodes
        rag_service.graph_service.get_nodes_by_intent.return_value = [
            {"name": "schedule_node", "type": "intent", "data": {}}
        ]
        
        response = await rag_service.generate_reply(sample_email_request)
        
        assert response is not None
        assert response.intent in ["schedule", "general_inquiry"]
    
    @pytest.mark.asyncio
    async def test_generate_reply_error_handling(self, rag_service, sample_email_request):
        """Test error handling in reply generation."""
        # Mock service failure
        rag_service.ollama_service.classify_intent_and_artifacts.side_effect = Exception("Service error")
        
        with pytest.raises(Exception):
            await rag_service.generate_reply(sample_email_request)
    
    @pytest.mark.asyncio
    async def test_generate_reply_empty_email(self, rag_service):
        """Test reply generation with empty email."""
        empty_request = EmailRequest(
            subject="",
            sender="test@example.com",
            body=""
        )
        
        response = await rag_service.generate_reply(empty_request)
        
        assert response is not None
        assert isinstance(response.draft_reply, str)
    
    def test_rag_service_init(self, rag_service):
        """Test RAG service initialization."""
        assert rag_service.top_k == 6
        assert rag_service.auto_send_threshold == 0.85
        assert rag_service.known_intents is not None
        assert rag_service.known_artifacts is not None

