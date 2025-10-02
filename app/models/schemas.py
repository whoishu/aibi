"""Data models and schemas"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AutocompleteRequest(BaseModel):
    """Request model for autocomplete endpoint"""

    query: str = Field(..., description="User input string (supports Chinese)")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of suggestions")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class Suggestion(BaseModel):
    """Single suggestion item"""

    text: str = Field(..., description="Suggestion text")
    score: float = Field(..., description="Relevance score")
    source: str = Field(..., description="Source of suggestion (keyword/vector/personalized)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AutocompleteResponse(BaseModel):
    """Response model for autocomplete endpoint"""

    query: str = Field(..., description="Original query")
    suggestions: List[Suggestion] = Field(default_factory=list, description="List of suggestions")
    total: int = Field(..., description="Total number of suggestions")


class FeedbackRequest(BaseModel):
    """Request model for user feedback"""

    query: str = Field(..., description="Original query")
    selected_suggestion: str = Field(..., description="Selected suggestion")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: Optional[str] = Field(None, description="Timestamp")


class DocumentRequest(BaseModel):
    """Request model for adding/updating documents"""

    text: str = Field(..., description="Document text")
    doc_id: Optional[str] = Field(None, description="Document ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    keywords: Optional[List[str]] = Field(None, description="Associated keywords")


class BulkDocumentRequest(BaseModel):
    """Request model for bulk document operations"""

    documents: List[DocumentRequest] = Field(..., description="List of documents")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    opensearch_connected: bool = Field(..., description="OpenSearch connection status")
    redis_connected: bool = Field(..., description="Redis connection status")
