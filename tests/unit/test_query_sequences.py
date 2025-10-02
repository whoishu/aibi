"""Unit tests for query sequence tracking and related queries optimization"""
import pytest
from unittest.mock import Mock, MagicMock
from app.services.personalization_service import PersonalizationService
from app.services.autocomplete_service import AutocompleteService


@pytest.mark.unit
def test_track_query_sequences():
    """Test that query sequences are tracked correctly"""
    # Create mock Redis client
    mock_redis = MagicMock()

    # Create service with mock Redis
    service = PersonalizationService()
    service.redis_client = mock_redis

    # Simulate user making sequential queries
    # First query: "销售分析"
    mock_redis.lrange.return_value = []  # No previous query
    service.track_selection("user123", "销售分析", "销售数据分析报告")

    # Second query: "市场趋势" (should create sequence: 销售分析 -> 市场趋势)
    mock_redis.lrange.return_value = ['{"query": "销售分析", "selected": "销售数据分析报告", "timestamp": "2024-01-01"}']
    service.track_selection("user123", "市场趋势", "2024市场趋势报告")

    # Verify sequence was tracked
    # Should have called zincrby for global sequence
    calls = [call for call in mock_redis.zincrby.call_args_list if 'sequence:' in str(call)]
    assert len(calls) > 0, "Expected sequence tracking calls"


@pytest.mark.unit
def test_get_query_sequences():
    """Test retrieving query sequences (next and previous queries)"""
    mock_redis = MagicMock()

    service = PersonalizationService()
    service.redis_client = mock_redis

    # Mock next queries (queries that come after current query)
    mock_redis.zrevrange.side_effect = [
        [("市场趋势", 5.0), ("业绩报告", 3.0)],  # User-specific next queries
        [("竞争分析", 4.0)],  # Global next queries
    ]

    # Mock scan_iter for finding previous queries
    mock_redis.scan_iter.side_effect = [
        ["user:user123:sequence:销售分析"],  # User-specific sequences
        ["sequence:销售分析", "sequence:数据统计"],  # Global sequences
    ]
    mock_redis.zscore.side_effect = [6.0, 5.0, 3.0]  # Scores for previous queries

    result = service.get_query_sequences("市场趋势", user_id="user123", limit=5)

    # Verify result structure
    assert "next" in result
    assert "previous" in result

    # Verify next queries are present
    assert len(result["next"]) > 0
    next_queries = [q for q, _ in result["next"]]
    assert "市场趋势" in next_queries or "业绩报告" in next_queries or "竞争分析" in next_queries

    # Verify previous queries are present
    assert len(result["previous"]) > 0


@pytest.mark.unit
def test_get_query_sequences_without_redis():
    """Test that get_query_sequences handles missing Redis gracefully"""
    service = PersonalizationService()
    service.redis_client = None

    result = service.get_query_sequences("test query")

    assert result == {"next": [], "previous": []}


@pytest.mark.unit
def test_related_queries_with_sequences():
    """Test that related queries include sequence-based suggestions"""
    # Mock dependencies
    mock_opensearch = Mock()
    mock_vector_service = Mock()
    mock_personalization = Mock()

    # Setup mocks
    mock_vector_service.encode_single.return_value = [0.1, 0.2, 0.3]
    mock_opensearch.hybrid_search.return_value = [
        {
            "text": "销售数据统计",
            "score": 0.75,
            "keywords": ["sales"],
            "doc_id": "doc1"
        }
    ]

    # Mock sequence queries - "next" queries should have higher scores
    mock_personalization.get_query_sequences.return_value = {
        "next": [("市场分析", 10.0), ("业绩报告", 8.0)],
        "previous": [("数据收集", 5.0)]
    }
    mock_personalization.get_user_preferences.return_value = []

    # Create service
    service = AutocompleteService(
        opensearch_service=mock_opensearch,
        vector_service=mock_vector_service,
        personalization_service=mock_personalization,
        enable_personalization=True
    )

    # Get related queries
    results = service.get_related_queries("销售分析", user_id="user123", limit=10)

    # Verify results
    assert len(results) > 0

    # Check that we have sequence-based results
    sources = [r["source"] for r in results]
    assert "sequence_next" in sources or "sequence_prev" in sources, "Expected sequence-based results"

    # Verify that "next" queries have higher scores than "previous" queries
    next_queries = [r for r in results if r["source"] == "sequence_next"]
    prev_queries = [r for r in results if r["source"] == "sequence_prev"]

    if next_queries and prev_queries:
        avg_next_score = sum(q["score"] for q in next_queries) / len(next_queries)
        avg_prev_score = sum(q["score"] for q in prev_queries) / len(prev_queries)
        assert avg_next_score > avg_prev_score, "Next queries should have higher scores than previous queries"


@pytest.mark.unit
def test_related_queries_prioritizes_next_over_previous():
    """Test that next queries appear before previous queries in results"""
    mock_opensearch = Mock()
    mock_vector_service = Mock()
    mock_personalization = Mock()

    mock_vector_service.encode_single.return_value = [0.1, 0.2, 0.3]
    mock_opensearch.hybrid_search.return_value = []

    # Mock sequences where we have both next and previous queries
    mock_personalization.get_query_sequences.return_value = {
        "next": [("下一步操作", 5.0)],  # Should appear first
        "previous": [("上一步操作", 5.0)]  # Should appear after next
    }
    mock_personalization.get_user_preferences.return_value = []

    service = AutocompleteService(
        opensearch_service=mock_opensearch,
        vector_service=mock_vector_service,
        personalization_service=mock_personalization,
        enable_personalization=True
    )

    results = service.get_related_queries("当前步骤", user_id="user123", limit=10)

    # Find positions of next and previous queries
    next_pos = None
    prev_pos = None
    for i, r in enumerate(results):
        if r["source"] == "sequence_next":
            next_pos = i
        elif r["source"] == "sequence_prev":
            prev_pos = i

    # If both are present, next should come before previous
    if next_pos is not None and prev_pos is not None:
        assert next_pos < prev_pos, "Next queries should appear before previous queries"


@pytest.mark.unit
def test_related_queries_deduplication():
    """Test that related queries are properly deduplicated"""
    mock_opensearch = Mock()
    mock_vector_service = Mock()
    mock_personalization = Mock()

    mock_vector_service.encode_single.return_value = [0.1, 0.2, 0.3]

    # Return same query in hybrid search
    mock_opensearch.hybrid_search.return_value = [
        {
            "text": "市场分析",
            "score": 0.8,
            "keywords": [],
            "doc_id": "doc1"
        }
    ]

    # Also return it in sequences
    mock_personalization.get_query_sequences.return_value = {
        "next": [("市场分析", 10.0)],  # Duplicate
        "previous": []
    }
    mock_personalization.get_user_preferences.return_value = ["市场分析"]  # Another duplicate

    service = AutocompleteService(
        opensearch_service=mock_opensearch,
        vector_service=mock_vector_service,
        personalization_service=mock_personalization,
        enable_personalization=True
    )

    results = service.get_related_queries("销售分析", user_id="user123", limit=10)

    # Should only have one instance of "市场分析"
    texts = [r["text"] for r in results]
    assert texts.count("市场分析") == 1, "Duplicate queries should be removed"
