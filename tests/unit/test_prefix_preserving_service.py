"""Unit tests for prefix-preserving service"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.prefix_preserving_service import PrefixPreservingService
from app.models.schemas import Suggestion


class TestPrefixPreservingService:
    """Test prefix-preserving service functionality"""

    @pytest.fixture
    def mock_opensearch(self):
        """Mock OpenSearch service"""
        mock = Mock()
        mock.keyword_search.return_value = [
            {"text": "销售额", "score": 0.9},
            {"text": "销量", "score": 0.85},
            {"text": "销售情况", "score": 0.8},
        ]
        return mock

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM service"""
        mock = Mock()
        mock.is_available.return_value = True
        mock.rank_prefix_completions.return_value = [
            {
                "text": "帮我查询一下今年北京的销售额",
                "score": 0.95,
                "method": "llm_ranked",
                "completed_term": "销售额",
            },
            {
                "text": "帮我查询一下今年北京的销量",
                "score": 0.90,
                "method": "llm_ranked",
                "completed_term": "销量",
            },
        ]
        return mock

    @pytest.fixture
    def service(self, mock_opensearch, mock_llm):
        """Create service instance"""
        return PrefixPreservingService(
            opensearch_service=mock_opensearch,
            llm_service=mock_llm,
            personalization_service=None,
        )

    def test_analyze_input_short_query(self, service):
        """Test analysis of short query"""
        result = service.analyze_input("销售")
        
        assert result["is_long_query"] is False
        assert result["tokens"] == ["销售"]

    def test_analyze_input_long_query(self, service):
        """Test analysis of long query"""
        result = service.analyze_input("帮我查询一下今年北京的销")
        
        assert result["is_long_query"] is True
        assert result["prefix"] == "帮我查询一下今年北京的"
        assert result["incomplete_term"] == "销"
        assert len(result["tokens"]) >= 5

    def test_analyze_input_empty_query(self, service):
        """Test analysis of empty query"""
        result = service.analyze_input("")
        
        assert result["is_long_query"] is False
        assert result["prefix"] == ""
        assert result["incomplete_term"] == ""

    def test_search_completion_candidates(self, service, mock_opensearch):
        """Test searching for completion candidates"""
        candidates = service.search_completion_candidates("销", limit=20)
        
        assert len(candidates) > 0
        assert "销售额" in candidates
        mock_opensearch.keyword_search.assert_called_once()

    def test_rank_and_complete_with_llm(self, service, mock_llm):
        """Test ranking and completion with LLM"""
        results = service.rank_and_complete(
            prefix="帮我查询一下今年北京的",
            incomplete_term="销",
            candidates=["销售额", "销量", "销售情况"],
        )
        
        assert len(results) > 0
        assert results[0]["text"] == "帮我查询一下今年北京的销售额"
        assert results[0]["score"] > 0
        mock_llm.rank_prefix_completions.assert_called_once()

    def test_rank_and_complete_fallback(self, mock_opensearch):
        """Test fallback completion without LLM"""
        mock_llm = Mock()
        mock_llm.is_available.return_value = False
        
        service = PrefixPreservingService(
            opensearch_service=mock_opensearch,
            llm_service=mock_llm,
            personalization_service=None,
        )
        
        results = service.rank_and_complete(
            prefix="帮我查询一下今年北京的",
            incomplete_term="销",
            candidates=["销售额", "销量"],
        )
        
        assert len(results) > 0
        assert "method" in results[0]
        assert results[0]["method"] == "fallback"

    def test_get_suggestions_short_query(self, service):
        """Test getting suggestions for short query"""
        result = service.get_suggestions_with_prefix_preservation(
            query="销售",
            limit=10,
        )
        
        # Should return None for short queries
        assert result is None

    def test_get_suggestions_long_query(self, service, mock_opensearch, mock_llm):
        """Test getting suggestions for long query"""
        result = service.get_suggestions_with_prefix_preservation(
            query="帮我查询一下今年北京的销",
            limit=10,
        )
        
        assert result is not None
        assert len(result) > 0
        assert all(isinstance(s, Suggestion) for s in result)
        assert result[0].source == "prefix_preserved"
        assert "prefix" in result[0].metadata
        assert "incomplete_term" in result[0].metadata

    def test_get_suggestions_no_candidates(self, service, mock_opensearch):
        """Test when no candidates are found"""
        mock_opensearch.keyword_search.return_value = []
        
        result = service.get_suggestions_with_prefix_preservation(
            query="帮我查询一下今年北京的销",
            limit=10,
        )
        
        assert result is None

    def test_build_user_context(self, mock_opensearch, mock_llm):
        """Test building user context"""
        mock_personalization = Mock()
        mock_personalization.get_user_preferences.return_value = [
            "销售分析",
            "客户满意度",
            "市场趋势",
        ]
        
        service = PrefixPreservingService(
            opensearch_service=mock_opensearch,
            llm_service=mock_llm,
            personalization_service=mock_personalization,
        )
        
        analysis = {"prefix": "帮我查询", "incomplete_term": "销", "tokens": []}
        context = service._build_user_context("user123", analysis)
        
        assert "user_history" in context
        assert len(context["user_history"]) > 0

    def test_fallback_completion(self, service):
        """Test fallback completion method"""
        results = service._fallback_completion(
            prefix="帮我查询一下今年北京的",
            incomplete_term="销",
            candidates=["销售额", "销量", "销售情况"],
        )
        
        assert len(results) > 0
        assert all("text" in r for r in results)
        assert all("score" in r for r in results)
        assert all("method" in r for r in results)
        assert results[0]["method"] == "fallback"

    def test_analyze_input_with_spaces(self, service):
        """Test analysis with extra spaces"""
        result = service.analyze_input("  帮我查询一下今年北京的销  ")
        
        assert result["is_long_query"] is True
        assert result["incomplete_term"] == "销"

    def test_metadata_in_suggestions(self, service, mock_opensearch, mock_llm):
        """Test that suggestions contain proper metadata"""
        result = service.get_suggestions_with_prefix_preservation(
            query="帮我查询一下今年北京的销",
            limit=10,
        )
        
        assert result is not None
        assert len(result) > 0
        suggestion = result[0]
        assert suggestion.metadata["prefix"] == "帮我查询一下今年北京的"
        assert suggestion.metadata["incomplete_term"] == "销"
        assert "method" in suggestion.metadata
