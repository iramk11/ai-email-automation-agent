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
API_PORT = 8001
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

# Artifact dictionary - explains what each artifact means
# Only includes artifacts actually used in generated_email_pairs.json and golden_dataset_benchmark.json
ARTIFACT_DICTIONARY = {
    "calendly": "Calendly scheduling link - use when email asks to schedule, book, or arrange a meeting",
    "draft": "Draft document - use when email asks for draft, document review, or written materials",
    "ds_resume": "Data Science resume - use when email mentions ML, data science, analytics, or data-related roles",
    "github": "GitHub profile - use when email asks for code samples, GitHub, or technical projects",
    "linkedin_profile": "LinkedIn profile link - use when email asks for LinkedIn, professional profile, or networking",
    "phone_number": "Phone number - use when email asks for phone contact or urgent communication",
    "portfolio": "Portfolio website - use when email asks for work samples, projects, or portfolio",
    "report": "Report document - use when email asks for report, progress update, or formal document",
    "swe_resume": "Software Engineering resume - use when email mentions software engineering, development, or SWE roles",
    "zoom_link": "Zoom meeting link - use when email asks for video call, Zoom meeting, or virtual meeting"
}

# Known artifacts (extracted from data)
KNOWN_ARTIFACTS = list(ARTIFACT_DICTIONARY.keys())

# User configuration (can be made dynamic per-user in future)
DEFAULT_USER_NAME = "Zubair"
DEFAULT_USER_TONE = "polite, proactive, and clear in communication"

