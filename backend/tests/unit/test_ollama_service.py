"""
Unit tests for OllamaService.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.ollama_service import OllamaService


class TestOllamaService:
    """Test cases for OllamaService."""
    
    @pytest.fixture
    def service(self):
        """Create OllamaService instance."""
        return OllamaService(model_name="llama3")
    
    def test_init(self, service):
        """Test service initialization."""
        assert service.model_name == "llama3"
        assert service.base_url is None
    
    @patch('backend.services.ollama_service.ollama')
    def test_classify_intent_and_artifacts(self, mock_ollama, service):
        """Test intent and artifact classification."""
        # Mock response
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"intents": ["schedule"], "artifacts": ["calendly"]}'
            }
        }
        
        result = service.classify_intent_and_artifacts(
            email_text="Can we schedule a meeting?",
            known_intents=["schedule", "follow_up"],
            known_artifacts=["calendly", "zoom_link"],
            artifact_dict={"calendly": "Scheduling link"}
        )
        
        assert "intents" in result
        assert "artifacts" in result
        assert isinstance(result["intents"], list)
        assert isinstance(result["artifacts"], list)
    
    @patch('backend.services.ollama_service.ollama')
    def test_classify_intent_and_artifacts_invalid_json(self, mock_ollama, service):
        """Test handling of invalid JSON response."""
        # Mock response with invalid JSON
        mock_ollama.chat.return_value = {
            "message": {
                "content": "This is not JSON"
            }
        }
        
        # Should handle gracefully
        result = service.classify_intent_and_artifacts(
            email_text="Test email",
            known_intents=["schedule"],
            known_artifacts=["calendly"],
            artifact_dict={"calendly": "Scheduling link"}
        )
        
        # Should return empty lists or handle error
        assert isinstance(result, dict)
    
    @patch('backend.services.ollama_service.ollama')
    def test_generate_reply(self, mock_ollama, service):
        """Test reply generation."""
        mock_ollama.chat.return_value = {
            "message": {
                "content": "Thank you for your email. I'd be happy to schedule a meeting."
            }
        }
        
        draft = service.generate_reply(
            email_text="Can we schedule a meeting?",
            intent="schedule",
            artifacts=["calendly"],
            faq_hits=[],
            graph_replies=[],
            user_name="Test User",
            user_tone="polite"
        )
        
        assert isinstance(draft, str)
        assert len(draft) > 0
    
    @patch('backend.services.ollama_service.ollama')
    def test_health_check(self, mock_ollama, service):
        """Test health check."""
        mock_ollama.chat.return_value = {
            "message": {"content": "test"}
        }
        
        result = service.health_check()
        assert result is True
    
    @patch('backend.services.ollama_service.ollama')
    def test_health_check_failure(self, mock_ollama, service):
        """Test health check failure."""
        mock_ollama.chat.side_effect = Exception("Connection error")
        
        result = service.health_check()
        assert result is False

