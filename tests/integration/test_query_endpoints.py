"""Integration tests for query endpoints (similar and related queries)"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_autocomplete_service():
    """Mock AutocompleteService for testing"""
    service = Mock()
    
    # Mock get_similar_queries
    service.get_similar_queries.return_value = [
        {
            "text": "销售数据分析",
            "score": 0.92,
            "source": "vector",
            "metadata": {"keywords": ["sales", "data"], "doc_id": "doc1"}
        },
        {
            "text": "销售趋势报告",
            "score": 0.88,
            "source": "vector",
            "metadata": {"keywords": ["sales", "trend"], "doc_id": "doc2"}
        }
    ]
    
    # Mock get_related_queries
    service.get_related_queries.return_value = [
        {
            "text": "市场分析",
            "score": 0.85,
            "source": "hybrid",
            "metadata": {"keywords": ["market"], "doc_id": "doc3"}
        },
        {
            "text": "业绩统计",
            "score": 0.80,
            "source": "history",
            "metadata": {"from_user_history": True}
        }
    ]
    
    return service


@pytest.fixture
def test_client(mock_autocomplete_service):
    """Create test client with mocked service"""
    from app.api.routes import router, set_autocomplete_service
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    
    set_autocomplete_service(mock_autocomplete_service)
    
    return TestClient(app)


@pytest.mark.integration
def test_similar_queries_endpoint(test_client):
    """Test similar queries endpoint returns correct response"""
    response = test_client.post(
        "/api/v1/similar-queries",
        json={"query": "销售分析", "user_id": "user123", "limit": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query"] == "销售分析"
    assert "similar_queries" in data
    assert len(data["similar_queries"]) == 2
    assert data["total"] == 2
    
    # Check first result
    first_query = data["similar_queries"][0]
    assert first_query["text"] == "销售数据分析"
    assert first_query["score"] == 0.92
    assert first_query["source"] == "vector"


@pytest.mark.integration
def test_similar_queries_without_user_id(test_client):
    """Test similar queries endpoint works without user_id"""
    response = test_client.post(
        "/api/v1/similar-queries",
        json={"query": "销售分析"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query"] == "销售分析"
    assert len(data["similar_queries"]) == 2


@pytest.mark.integration
def test_related_queries_endpoint(test_client):
    """Test related queries endpoint returns correct response"""
    response = test_client.post(
        "/api/v1/related-queries",
        json={"query": "销售报告", "user_id": "user456", "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["query"] == "销售报告"
    assert "related_queries" in data
    assert len(data["related_queries"]) == 2
    assert data["total"] == 2
    
    # Check first result
    first_query = data["related_queries"][0]
    assert first_query["text"] == "市场分析"
    assert first_query["score"] == 0.85
    assert first_query["source"] == "hybrid"


@pytest.mark.integration
def test_related_queries_with_history(test_client):
    """Test related queries includes history-based results"""
    response = test_client.post(
        "/api/v1/related-queries",
        json={"query": "销售报告", "user_id": "user456"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that history source is included
    sources = [q["source"] for q in data["related_queries"]]
    assert "history" in sources


@pytest.mark.integration
def test_similar_queries_empty_query(test_client, mock_autocomplete_service):
    """Test similar queries with empty query returns empty results"""
    mock_autocomplete_service.get_similar_queries.return_value = []
    
    response = test_client.post(
        "/api/v1/similar-queries",
        json={"query": ""}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["similar_queries"]) == 0
    assert data["total"] == 0


@pytest.mark.integration
def test_related_queries_empty_query(test_client, mock_autocomplete_service):
    """Test related queries with empty query returns empty results"""
    mock_autocomplete_service.get_related_queries.return_value = []
    
    response = test_client.post(
        "/api/v1/related-queries",
        json={"query": ""}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["related_queries"]) == 0
    assert data["total"] == 0


@pytest.mark.integration
def test_similar_queries_limit_parameter(test_client, mock_autocomplete_service):
    """Test similar queries respects limit parameter"""
    response = test_client.post(
        "/api/v1/similar-queries",
        json={"query": "test", "limit": 1}
    )
    
    assert response.status_code == 200
    # Verify limit was passed to service
    mock_autocomplete_service.get_similar_queries.assert_called_once()
    call_kwargs = mock_autocomplete_service.get_similar_queries.call_args.kwargs
    assert call_kwargs["limit"] == 1


@pytest.mark.integration
def test_related_queries_limit_parameter(test_client, mock_autocomplete_service):
    """Test related queries respects limit parameter"""
    response = test_client.post(
        "/api/v1/related-queries",
        json={"query": "test", "limit": 3}
    )
    
    assert response.status_code == 200
    # Verify limit was passed to service
    mock_autocomplete_service.get_related_queries.assert_called_once()
    call_kwargs = mock_autocomplete_service.get_related_queries.call_args.kwargs
    assert call_kwargs["limit"] == 3


@pytest.mark.integration
def test_similar_queries_error_handling(test_client, mock_autocomplete_service):
    """Test similar queries endpoint handles service errors"""
    mock_autocomplete_service.get_similar_queries.side_effect = Exception("Service error")
    
    response = test_client.post(
        "/api/v1/similar-queries",
        json={"query": "test"}
    )
    
    assert response.status_code == 500
    assert "detail" in response.json()


@pytest.mark.integration
def test_related_queries_error_handling(test_client, mock_autocomplete_service):
    """Test related queries endpoint handles service errors"""
    mock_autocomplete_service.get_related_queries.side_effect = Exception("Service error")
    
    response = test_client.post(
        "/api/v1/related-queries",
        json={"query": "test"}
    )
    
    assert response.status_code == 500
    assert "detail" in response.json()
