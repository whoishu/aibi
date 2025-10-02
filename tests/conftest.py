"""Pytest configuration and shared fixtures"""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client"""
    client = Mock()
    client.indices = Mock()
    client.indices.exists = AsyncMock(return_value=True)
    client.indices.create = AsyncMock()
    client.index = AsyncMock()
    client.search = AsyncMock(
        return_value={
            "hits": {"hits": [{"_source": {"text": "销售额", "frequency": 100}, "_score": 2.5}]}
        }
    )
    return client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    client = Mock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock()
    client.zadd = AsyncMock()
    client.zrevrange = AsyncMock(return_value=[])
    client.incr = AsyncMock()
    return client


@pytest.fixture
def mock_vector_service():
    """Mock Vector Service"""
    service = Mock()
    service.encode = Mock(return_value=[[0.1] * 384])
    return service


@pytest.fixture
def sample_autocomplete_request():
    """Sample autocomplete request data"""
    return {"query": "销售", "user_id": "test_user_123", "limit": 5}


@pytest.fixture
def sample_suggestions():
    """Sample suggestions"""
    return [
        {"text": "销售额", "score": 2.5, "source": "hybrid"},
        {"text": "销售额趋势分析", "score": 2.0, "source": "keyword"},
        {"text": "销售额同比增长率", "score": 1.8, "source": "vector"},
    ]
