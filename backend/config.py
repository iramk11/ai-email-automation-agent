"""
Configuration settings for the Graph RAG Email Assistant backend.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
QDRANT_DATA_PATH = BASE_DIR / "qdrant_data"
GRAPH_DATA_PATH = BASE_DIR / "graph_data.gpickle"

# Qdrant settings
QDRANT_COLLECTION_NAME = "knowledge_space"
QDRANT_VECTOR_SIZE = 384
QDRANT_DISTANCE_METRIC = "Cosine"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Ollama settings
OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# RAG settings
TOP_K_RESULTS = 6
AUTO_SEND_THRESHOLD = 0.85
MAX_REPLY_LENGTH = 120  # words

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:*",
    "https://mail.google.com"
]

# Intent classification
KNOWN_INTENTS = [
    'reschedule', 'follow_up', 'accept_or_decline', 
    'send_materials', 'request_feedback', 'confirm', 
    'schedule', 'request_info', 'share_feedback',
    'general_inquiry'
]

# User configuration (can be made dynamic per-user in future)
DEFAULT_USER_NAME = "Assistant"
DEFAULT_USER_TONE = "polite, proactive, and professional"

