"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.embedding_service import EmbeddingService
from backend.services.qdrant_service import QdrantService
from backend.services.graph_service import GraphService
from backend.services.ollama_service import OllamaService
from backend.services.rag_service import RAGService
from backend.config import KNOWN_INTENTS, KNOWN_ARTIFACTS, ARTIFACT_DICTIONARY


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service."""
    service = MagicMock(spec=EmbeddingService)
    # EmbeddingService.encode() returns List[float], not numpy array
    service.encode.return_value = np.random.rand(384).astype(np.float32).tolist()
    service.encode_batch.return_value = [np.random.rand(384).astype(np.float32).tolist() for _ in range(3)]
    return service


@pytest.fixture
def mock_qdrant_service():
    """Mock Qdrant service."""
    service = MagicMock()  # Don't use spec to allow any attribute access
    service.search.return_value = []
    service.search_faqs_only.return_value = []  # Actual method name
    service.search_writing_style.return_value = []
    service.health_check.return_value = True
    return service


@pytest.fixture
def mock_graph_service():
    """Mock graph service."""
    service = MagicMock()  # Don't use spec to allow any attribute access
    service.get_nodes_by_intent.return_value = []
    service.expand_graph_context.return_value = {}
    service.health_check.return_value = True
    return service


@pytest.fixture
def mock_ollama_service():
    """Mock Ollama service."""
    service = MagicMock(spec=OllamaService)
    service.classify_intent_and_artifacts.return_value = {
        "intents": ["schedule"],
        "artifacts": ["calendly"]
    }
    service.generate_reply.return_value = "Thank you for your email. I'd be happy to schedule a meeting."
    service.health_check.return_value = True
    return service


@pytest.fixture
def rag_service(mock_embedding_service, mock_qdrant_service, mock_graph_service, mock_ollama_service):
    """RAG service with mocked dependencies."""
    return RAGService(
        embedding_service=mock_embedding_service,
        qdrant_service=mock_qdrant_service,
        graph_service=mock_graph_service,
        ollama_service=mock_ollama_service,
        known_intents=KNOWN_INTENTS,
        known_artifacts=KNOWN_ARTIFACTS,
        artifact_dict=ARTIFACT_DICTIONARY,
        top_k=6,
        auto_send_threshold=0.85
    )


@pytest.fixture
def sample_email_request():
    """Sample email request for testing."""
    from backend.models.schemas import EmailRequest
    return EmailRequest(
        subject="Meeting Request",
        sender="test@example.com",
        body="Hi, can we schedule a meeting to discuss your project?"
    )

