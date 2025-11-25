"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class EmailRequest(BaseModel):
    """Request model for email reply generation."""
    subject: str = Field(..., description="Email subject line")
    sender: str = Field(..., description="Sender's email address")
    body: str = Field(..., description="Email body content")
    user_name: Optional[str] = Field(None, description="Name of the user replying")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Meeting Request",
                "sender": "professor@university.edu",
                "body": "Hi, can we schedule a meeting to discuss your project?"
            }
        }


class FAQHit(BaseModel):
    """FAQ retrieval result."""
    score: float
    question: str
    answer: str
    faq_id: int


class GraphNodeHit(BaseModel):
    """Graph node retrieval result."""
    score: float
    node_name: str
    node_type: str
    neighbors: List[str]


class ContextUsed(BaseModel):
    """Context information used for generation."""
    faq_hits: List[FAQHit]
    graph_nodes: List[GraphNodeHit]
    expanded_graph: Dict[str, List[str]]


class EmailResponse(BaseModel):
    """Response model for generated email reply."""
    draft_reply: str = Field(..., description="Generated draft reply")
    intent: str = Field(..., description="Detected intent of the email")
    confidence_score: float = Field(..., description="Confidence score (0-1) based on retrieval")
    auto_send: bool = Field(..., description="Whether the reply is confident enough for auto-send")
    context_used: ContextUsed = Field(..., description="Context information used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_reply": "Hi Professor, I'd be happy to schedule a meeting...",
                "intent": "schedule",
                "confidence_score": 0.87,
                "auto_send": True,
                "context_used": {
                    "faq_hits": [],
                    "graph_nodes": [],
                    "expanded_graph": {}
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    services: Dict[str, bool]
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None

