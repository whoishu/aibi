"""API routes for autocomplete service"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import (
    AutocompleteRequest,
    AutocompleteResponse,
    BulkDocumentRequest,
    DocumentRequest,
    FeedbackRequest,
    HealthResponse,
)
from app.services.autocomplete_service import AutocompleteService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instance (will be set by main app)
_autocomplete_service: Optional[AutocompleteService] = None


def get_autocomplete_service() -> AutocompleteService:
    """Dependency to get autocomplete service"""
    if _autocomplete_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return _autocomplete_service


def set_autocomplete_service(service: AutocompleteService):
    """Set the global autocomplete service instance"""
    global _autocomplete_service
    _autocomplete_service = service


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    request: AutocompleteRequest, service: AutocompleteService = Depends(get_autocomplete_service)
):
    """
    Get autocomplete suggestions for user input

    - **query**: User input string (supports Chinese and English)
    - **user_id**: Optional user ID for personalized suggestions
    - **limit**: Maximum number of suggestions (1-50)
    - **context**: Optional additional context
    """
    try:
        suggestions = service.get_suggestions(
            query=request.query, user_id=request.user_id, limit=request.limit
        )

        return AutocompleteResponse(
            query=request.query, suggestions=suggestions, total=len(suggestions)
        )
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def feedback(
    request: FeedbackRequest, service: AutocompleteService = Depends(get_autocomplete_service)
):
    """
    Record user feedback (selection)

    - **query**: Original query
    - **selected_suggestion**: The suggestion user selected
    - **user_id**: Optional user ID
    - **timestamp**: Optional timestamp
    """
    try:
        success = service.record_feedback(
            query=request.query,
            selected_suggestion=request.selected_suggestion,
            user_id=request.user_id,
            timestamp=request.timestamp,
        )

        return {
            "success": success,
            "message": "Feedback recorded" if success else "Failed to record feedback",
        }
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents")
async def add_document(
    request: DocumentRequest, service: AutocompleteService = Depends(get_autocomplete_service)
):
    """
    Add a document to the autocomplete index

    - **text**: Document text
    - **doc_id**: Optional document ID
    - **keywords**: Optional list of keywords
    - **metadata**: Optional metadata
    """
    try:
        success = service.add_document(
            text=request.text,
            doc_id=request.doc_id,
            keywords=request.keywords,
            metadata=request.metadata,
        )

        return {
            "success": success,
            "message": "Document added" if success else "Failed to add document",
        }
    except Exception as e:
        logger.error(f"Add document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/bulk")
async def add_documents_bulk(
    request: BulkDocumentRequest, service: AutocompleteService = Depends(get_autocomplete_service)
):
    """
    Add multiple documents in bulk

    - **documents**: List of documents to add
    """
    try:
        documents = [doc.dict() for doc in request.documents]
        success, errors = service.add_documents_bulk(documents)

        return {
            "success": success,
            "errors": errors,
            "message": f"Added {success} documents with {errors} errors",
        }
    except Exception as e:
        logger.error(f"Bulk add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check(service: AutocompleteService = Depends(get_autocomplete_service)):
    """
    Health check endpoint
    """
    try:
        opensearch_connected = service.opensearch.check_connection()
        redis_connected = False

        if service.personalization:
            redis_connected = service.personalization.check_connection()

        status = "healthy" if opensearch_connected else "degraded"

        return HealthResponse(
            status=status,
            opensearch_connected=opensearch_connected,
            redis_connected=redis_connected,
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
