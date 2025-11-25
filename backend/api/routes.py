"""
API routes for the Graph RAG Email Assistant.
"""
from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import (
    EmailRequest, EmailResponse, HealthResponse, ErrorResponse
)
from backend.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# RAG service will be injected as dependency
rag_service: RAGService = None


def set_rag_service(service: RAGService):
    """Set the RAG service instance."""
    global rag_service
    rag_service = service


@router.post(
    "/generate-reply",
    response_model=EmailResponse,
    summary="Generate email reply",
    description="Generate an AI-powered email reply using Graph RAG"
)
async def generate_reply(request: EmailRequest):
    """
    Generate a draft email reply.
    
    Args:
        request: Email request with subject, sender, and body
        
    Returns:
        EmailResponse with generated draft and context
    """
    try:
        logger.info(f"Received reply generation request from {request.sender}")
        
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service not initialized"
            )
        
        response = await rag_service.generate_reply(request)
        
        logger.info("Successfully generated reply")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate reply: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reply: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of all services"
)
async def health_check():
    """
    Perform health check on all services.
    
    Returns:
        HealthResponse with service status
    """
    try:
        if not rag_service:
            return HealthResponse(
                status="unhealthy",
                services={"rag": False}
            )
        
        services = rag_service.health_check()
        all_healthy = all(services.values())
        
        return HealthResponse(
            status="healthy" if all_healthy else "degraded",
            services=services
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            services={"error": False}
        )


@router.get(
    "/",
    summary="Root endpoint",
    description="API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Graph RAG Email Assistant API",
        "version": "1.0.0",
        "description": "AI-powered email reply generation using Graph RAG",
        "endpoints": {
            "generate_reply": "/api/generate-reply",
            "health": "/api/health"
        }
    }

