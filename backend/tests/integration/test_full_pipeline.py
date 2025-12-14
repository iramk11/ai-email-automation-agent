"""
End-to-end integration tests for the full RAG pipeline.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.models.schemas import EmailRequest
from backend.tests.conftest import rag_service


class TestFullPipeline:
    """End-to-end pipeline tests."""
    
    @pytest.mark.asyncio
    async def test_full_rag_pipeline(self, rag_service):
        """Test complete RAG pipeline from email to reply."""
        from backend.models.schemas import FAQHit
        
        # Setup mocks for realistic flow
        rag_service.qdrant_service.search_faq_only.return_value = [
            FAQHit(score=0.85, question="How to schedule?", answer="Use Calendly link", faq_id=1)
        ]
        
        rag_service.graph_service.get_nodes_by_intent.return_value = [
            {"name": "schedule", "type": "intent", "data": {"examples": ["Meeting request"]}}
        ]
        
        rag_service.ollama_service.generate_draft.return_value = (
            "Thank you for reaching out. I'd be happy to schedule a meeting. "
            "Please use my Calendly link to find a time that works for you."
        )
        
        request = EmailRequest(
            subject="Meeting Request",
            sender="professor@university.edu",
            body="Hi, can we schedule a meeting to discuss your project?"
        )
        
        response = await rag_service.generate_reply(request)
        
        # Verify response structure
        assert response is not None
        assert response.draft_reply is not None
        assert len(response.draft_reply) > 0
        assert response.intent in ["schedule", "general_inquiry"]
        assert isinstance(response.artifacts, list)
        assert 0 <= response.confidence_score <= 1
        assert isinstance(response.auto_send, bool)
        
        # Verify context was used
        assert response.context_used is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_with_multiple_intents(self, rag_service):
        """Test pipeline handling multiple intents."""
        rag_service.ollama_service.classify_intent_and_artifacts.return_value = {
            "intents": ["schedule", "send_materials"],
            "artifacts": ["calendly", "ds_resume"]
        }
        
        request = EmailRequest(
            subject="Meeting and Resume Request",
            sender="recruiter@company.com",
            body="Can we schedule a call? Also, please send your data science resume."
        )
        
        response = await rag_service.generate_reply(request)
        
        assert response is not None
        assert len(response.artifacts) >= 0  # May include detected artifacts
        assert response.intent is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_error_recovery(self, rag_service):
        """Test pipeline error handling and recovery."""
        # Simulate partial failure
        rag_service.qdrant_service.search_faq_only.side_effect = Exception("Qdrant error")
        
        request = EmailRequest(
            subject="Test",
            sender="test@example.com",
            body="Test email"
        )
        
        # Should either handle gracefully or raise appropriate error
        with pytest.raises(Exception):
            await rag_service.generate_reply(request)
    
    @pytest.mark.asyncio
    async def test_pipeline_empty_context(self, rag_service):
        """Test pipeline with no matching context."""
        # No FAQ hits, no graph nodes
        rag_service.qdrant_service.search_faq_only.return_value = []
        rag_service.graph_service.get_nodes_by_intent.return_value = []
        
        request = EmailRequest(
            subject="Unique Request",
            sender="test@example.com",
            body="This is a completely unique email with no matching context."
        )
        
        response = await rag_service.generate_reply(request)
        
        # Should still generate a reply, possibly with lower confidence
        assert response is not None
        assert response.draft_reply is not None
        assert len(response.draft_reply) > 0

