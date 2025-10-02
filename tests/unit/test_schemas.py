"""Unit tests for Pydantic schemas"""

import pytest
from pydantic import ValidationError
from app.models.schemas import (
    AutocompleteRequest,
    AutocompleteResponse,
    Suggestion,
    FeedbackRequest,
    DocumentRequest,
)


@pytest.mark.unit
def test_autocomplete_request_valid():
    """Test valid autocomplete request"""
    request = AutocompleteRequest(query="销售", user_id="user123", limit=5)
    assert request.query == "销售"
    assert request.user_id == "user123"
    assert request.limit == 5


@pytest.mark.unit
def test_autocomplete_request_defaults():
    """Test autocomplete request with defaults"""
    request = AutocompleteRequest(query="test")
    assert request.query == "test"
    assert request.user_id is None
    assert request.limit == 10


@pytest.mark.unit
def test_autocomplete_request_empty_query_fails():
    """Test that empty query raises validation error"""
    with pytest.raises(ValidationError):
        AutocompleteRequest(query="")


@pytest.mark.unit
def test_suggestion_model():
    """Test Suggestion model"""
    suggestion = Suggestion(text="销售额", score=2.5, source="hybrid")
    assert suggestion.text == "销售额"
    assert suggestion.score == 2.5
    assert suggestion.source == "hybrid"


@pytest.mark.unit
def test_autocomplete_response():
    """Test AutocompleteResponse model"""
    suggestions = [
        Suggestion(text="销售额", score=2.5, source="hybrid"),
        Suggestion(text="销售额趋势", score=2.0, source="keyword"),
    ]
    response = AutocompleteResponse(query="销售", suggestions=suggestions, total=2)
    assert response.query == "销售"
    assert len(response.suggestions) == 2
    assert response.total == 2


@pytest.mark.unit
def test_feedback_request_valid():
    """Test valid feedback request"""
    feedback = FeedbackRequest(query="销售", selected="销售额", user_id="user123")
    assert feedback.query == "销售"
    assert feedback.selected == "销售额"
    assert feedback.user_id == "user123"


@pytest.mark.unit
def test_document_request_valid():
    """Test valid document request"""
    doc = DocumentRequest(text="销售额趋势分析", metadata={"category": "sales"})
    assert doc.text == "销售额趋势分析"
    assert doc.metadata["category"] == "sales"


@pytest.mark.unit
def test_document_request_without_metadata():
    """Test document request without metadata"""
    doc = DocumentRequest(text="test query")
    assert doc.text == "test query"
    assert doc.metadata == {}
