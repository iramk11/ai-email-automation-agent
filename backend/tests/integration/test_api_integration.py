"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from backend.models.schemas import EmailResponse, ContextUsed, FAQHit
from backend.api.routes import set_rag_service


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def mock_rag_service(self):
        """Create a mock RAG service."""
        from backend.tests.conftest import rag_service
        return rag_service
    
    @pytest.fixture
    def client(self, mock_rag_service):
        """Create test client with mocked service."""
        from backend.main import app
        # Set the mock service
        set_rag_service(mock_rag_service)
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data or "message" in data
    
    def test_health_check(self, client, mock_rag_service):
        """Test health check endpoint."""
        # Mock health check to return healthy status
        mock_rag_service.health_check = MagicMock(return_value={
            "qdrant": True,
            "graph": True,
            "ollama": True
        })
        
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    def test_generate_reply_endpoint(self, client, mock_rag_service):
        """Test reply generation endpoint."""
        # Mock response
        mock_response = EmailResponse(
            draft_reply="Thank you for your email.",
            intent="schedule",
            artifacts=["calendly"],
            confidence_score=0.9,
            auto_send=True,
            context_used=ContextUsed(
                faq_hits=[],
                graph_replies=[],
                graph_emails_found=0
            )
        )
        
        mock_rag_service.generate_reply = AsyncMock(return_value=mock_response)
        
        request_data = {
            "subject": "Meeting Request",
            "sender": "test@example.com",
            "body": "Can we schedule a meeting?"
        }
        
        response = client.post("/api/generate-reply", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "draft_reply" in data
        assert "intent" in data
        assert "confidence_score" in data
    
    def test_generate_reply_validation_error(self, client):
        """Test reply generation with invalid input."""
        # Missing required fields
        request_data = {
            "subject": "Test"
            # Missing sender and body
        }
        
        response = client.post("/api/generate-reply", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_generate_reply_service_error(self, client, mock_rag_service):
        """Test reply generation with service error."""
        mock_rag_service.generate_reply = AsyncMock(side_effect=Exception("Service error"))
        
        request_data = {
            "subject": "Test",
            "sender": "test@example.com",
            "body": "Test body"
        }
        
        response = client.post("/api/generate-reply", json=request_data)
        assert response.status_code == 500

