"""
Main FastAPI application for Graph RAG Email Assistant.
"""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import (
    API_HOST, API_PORT, CORS_ORIGINS, BASE_DIR,
    QDRANT_DATA_PATH, QDRANT_COLLECTION_NAME,
    GRAPH_DATA_PATH, EMBEDDING_MODEL, OLLAMA_MODEL,
    KNOWN_INTENTS, TOP_K_RESULTS, AUTO_SEND_THRESHOLD,
    DEFAULT_USER_NAME, DEFAULT_USER_TONE
)
from backend.api.routes import router, set_rag_service
from backend.services.embedding_service import EmbeddingService
from backend.services.qdrant_service import QdrantService
from backend.services.graph_service import GraphService
from backend.services.ollama_service import OllamaService
from backend.services.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global services
services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting Graph RAG Email Assistant API...")
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        
        embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
        services['embedding'] = embedding_service
        
        # Try graphrag_local/qdrant_data first (where notebook stores data), then fallback to root
        # Note: If notebook is running, you'll need to close it first or use a separate data path
        qdrant_path = BASE_DIR / "graphrag_local" / "qdrant_data"
        if not qdrant_path.exists():
            qdrant_path = QDRANT_DATA_PATH
        
        logger.info(f"Using Qdrant data path: {qdrant_path}")
        logger.info("⚠️  Note: Make sure the Jupyter notebook is closed, or Qdrant will be locked")
        qdrant_service = QdrantService(
            data_path=str(qdrant_path),
            collection_name=QDRANT_COLLECTION_NAME
        )
        services['qdrant'] = qdrant_service
        
        graph_service = GraphService(graph_path=str(GRAPH_DATA_PATH) if GRAPH_DATA_PATH.exists() else None)
        
        # If graph wasn't loaded from file, build it from labels
        if not graph_service.health_check():
            logger.info("Graph not found, building from labels file...")
            # Try multiple possible label file locations
            label_files = [
                BASE_DIR / "data" / "generated_email_pairs.json",  # New format from notebook
                BASE_DIR / "student_email_pairs.labels.jsonl",  # Old format
            ]
            
            labels = []
            labels_file = None
            for label_file in label_files:
                if label_file.exists():
                    labels_file = label_file
                    break
            
            if labels_file:
                import json
                logger.info(f"Loading labels from {labels_file}")
                
                if labels_file.suffix == '.json':
                    # JSON format (generated_email_pairs.json)
                    with open(labels_file, 'r', encoding='utf-8') as f:
                        labels = json.load(f)
                else:
                    # JSONL format
                    with open(labels_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                labels.append(json.loads(line))
                
                graph_service.build_from_labels(labels)
                logger.info(f"Built graph with {len(graph_service.graph.nodes())} nodes, {len(graph_service.graph.edges())} edges")
                
                # Optionally save for next time
                graph_service.save_graph(str(GRAPH_DATA_PATH))
            else:
                logger.warning(f"Labels file not found. Tried: {[str(f) for f in label_files]}")
        
        services['graph'] = graph_service
        
        ollama_service = OllamaService(model_name=OLLAMA_MODEL)
        services['ollama'] = ollama_service
        
        # Initialize RAG service
        rag_service = RAGService(
            embedding_service=embedding_service,
            qdrant_service=qdrant_service,
            graph_service=graph_service,
            ollama_service=ollama_service,
            known_intents=KNOWN_INTENTS,
            top_k=TOP_K_RESULTS,
            auto_send_threshold=AUTO_SEND_THRESHOLD,
            default_user_name=DEFAULT_USER_NAME,
            default_user_tone=DEFAULT_USER_TONE
        )
        services['rag'] = rag_service
        
        # Set RAG service in routes
        set_rag_service(rag_service)
        
        logger.info("All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Graph RAG Email Assistant API...")
    services.clear()


# Create FastAPI app
app = FastAPI(
    title="Graph RAG Email Assistant API",
    description="AI-powered email reply generation using Graph RAG with Qdrant, NetworkX, and Ollama",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Graph RAG Email Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )

