"""Unit tests for LLM service"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.llm_service import LLMService


class TestLLMService:
    """Test LLM service functionality"""

    def test_init_without_api_key(self):
        """Test initialization without API key"""
        llm = LLMService(provider="openai", api_key=None)
        assert llm.provider == "openai"
        assert not llm.is_available()

    def test_init_with_unknown_provider(self):
        """Test initialization with unknown provider"""
        llm = LLMService(provider="unknown", api_key="test")
        assert not llm.is_available()

    def test_is_available_without_client(self):
        """Test availability check when client is not initialized"""
        llm = LLMService(provider="openai", api_key=None)
        assert not llm.is_available()

    @patch('app.services.llm_service.OpenAI')
    def test_openai_initialization(self, mock_openai):
        """Test OpenAI client initialization"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        assert llm.is_available()

    def test_expand_query_not_available(self):
        """Test query expansion when LLM is not available"""
        llm = LLMService(provider="openai", api_key=None)
        result = llm.expand_query("test query")
        assert result == []

    @patch('app.services.llm_service.OpenAI')
    def test_expand_query_openai(self, mock_openai):
        """Test query expansion with OpenAI"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Query 1\nQuery 2\nQuery 3"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        result = llm.expand_query("销售")
        
        assert len(result) == 3
        assert "Query 1" in result
        assert "Query 2" in result
        assert "Query 3" in result

    @patch('app.services.llm_service.OpenAI')
    def test_generate_related_queries_openai(self, mock_openai):
        """Test related query generation with OpenAI"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Related 1\nRelated 2\nRelated 3"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        result = llm.generate_related_queries("市场趋势", limit=3)
        
        assert len(result) == 3
        assert result[0]["text"] == "Related 1"
        assert result[0]["source"] == "llm"
        assert result[0]["metadata"]["llm_generated"] is True
        assert result[0]["score"] > result[1]["score"]

    def test_generate_related_queries_not_available(self):
        """Test related query generation when LLM is not available"""
        llm = LLMService(provider="openai", api_key=None)
        result = llm.generate_related_queries("test query")
        assert result == []

    @patch('app.services.llm_service.OpenAI')
    def test_rewrite_query_openai(self, mock_openai):
        """Test query rewriting with OpenAI"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "销售额分析报告"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        result = llm.rewrite_query("销售", intent="clarify")
        
        assert result == "销售额分析报告"

    def test_rewrite_query_not_available(self):
        """Test query rewriting when LLM is not available"""
        llm = LLMService(provider="openai", api_key=None)
        result = llm.rewrite_query("test query")
        assert result is None

    def test_parse_llm_response_line_separated(self):
        """Test parsing line-separated LLM response"""
        llm = LLMService(provider="local")
        response = "Query 1\nQuery 2\nQuery 3"
        result = llm._parse_llm_response(response)
        
        assert len(result) == 3
        assert "Query 1" in result

    def test_parse_llm_response_comma_separated(self):
        """Test parsing comma-separated LLM response"""
        llm = LLMService(provider="local")
        response = "Query 1, Query 2, Query 3"
        result = llm._parse_llm_response(response)
        
        assert len(result) == 3
        assert "Query 1" in result

    def test_parse_llm_response_with_numbering(self):
        """Test parsing LLM response with numbering"""
        llm = LLMService(provider="local")
        response = "1. Query 1\n2. Query 2\n3. Query 3"
        result = llm._parse_llm_response(response)
        
        assert len(result) == 3
        assert "Query 1" in result
        assert "1." not in result[0]

    def test_parse_llm_response_with_bullets(self):
        """Test parsing LLM response with bullets"""
        llm = LLMService(provider="local")
        response = "- Query 1\n- Query 2\n- Query 3"
        result = llm._parse_llm_response(response)
        
        assert len(result) == 3
        assert "Query 1" in result
        assert "-" not in result[0]

    def test_parse_llm_response_with_quotes(self):
        """Test parsing LLM response with quotes"""
        llm = LLMService(provider="local")
        response = '"Query 1"\n"Query 2"\n"Query 3"'
        result = llm._parse_llm_response(response)
        
        assert len(result) == 3
        assert "Query 1" in result
        assert '"' not in result[0]

    @patch('app.services.llm_service.OpenAI')
    def test_expand_query_with_context(self, mock_openai):
        """Test query expansion with context"""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Contextual query 1\nContextual query 2"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        context = {
            "domain": "business_intelligence",
            "user_history": ["销售分析", "客户满意度"]
        }
        result = llm.expand_query("市场趋势", context=context)
        
        assert len(result) >= 2

    @patch('app.services.llm_service.OpenAI')
    def test_generate_related_queries_with_existing_results(self, mock_openai):
        """Test related query generation avoiding duplicates"""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "New query 1\nNew query 2"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        existing = ["Existing query 1", "Existing query 2"]
        result = llm.generate_related_queries(
            "test query",
            existing_results=existing,
            limit=2
        )
        
        assert len(result) == 2

    @patch('app.services.llm_service.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test handling of API errors"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        llm = LLMService(provider="openai", api_key="test-key")
        result = llm.expand_query("test query")
        
        assert result == []

    def test_build_query_expansion_prompt(self):
        """Test query expansion prompt building"""
        llm = LLMService(provider="local")
        prompt = llm._build_query_expansion_prompt("销售分析")
        
        assert "销售分析" in prompt
        assert "related" in prompt.lower()

    def test_build_related_queries_prompt(self):
        """Test related queries prompt building"""
        llm = LLMService(provider="local")
        prompt = llm._build_related_queries_prompt("市场趋势", limit=5)
        
        assert "市场趋势" in prompt
        assert "5" in prompt

    def test_build_query_rewrite_prompt(self):
        """Test query rewrite prompt building"""
        llm = LLMService(provider="local")
        prompt = llm._build_query_rewrite_prompt("销售", "clarify")
        
        assert "销售" in prompt
        assert "specific" in prompt.lower() or "clear" in prompt.lower()
