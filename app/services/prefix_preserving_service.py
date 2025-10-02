"""Service for long text prefix-preserving intelligent autocomplete"""

import logging
from typing import Any, Dict, List, Optional

import jieba

from app.models.schemas import Suggestion
from app.services.opensearch_service import OpenSearchService
from app.services.llm_service import LLMService
from app.services.personalization_service import PersonalizationService

logger = logging.getLogger(__name__)


class PrefixPreservingService:
    """Long text prefix-preserving autocomplete service"""

    def __init__(
        self,
        opensearch_service: OpenSearchService,
        llm_service: LLMService,
        personalization_service: Optional[PersonalizationService] = None,
        min_tokens_for_prefix_mode: int = 5,
        candidate_limit: int = 20,
        llm_result_limit: int = 10,
        min_incomplete_term_length: int = 1,
    ):
        """Initialize prefix-preserving service

        Args:
            opensearch_service: OpenSearch service instance
            llm_service: LLM service instance
            personalization_service: Optional personalization service
            min_tokens_for_prefix_mode: Minimum tokens to trigger prefix mode
            candidate_limit: Maximum candidates to retrieve from search
            llm_result_limit: Maximum results to return from LLM ranking
            min_incomplete_term_length: Minimum length for incomplete term
        """
        self.opensearch = opensearch_service
        self.llm_service = llm_service
        self.personalization = personalization_service
        self.min_tokens_for_prefix_mode = min_tokens_for_prefix_mode
        self.candidate_limit = candidate_limit
        self.llm_result_limit = llm_result_limit
        self.min_incomplete_term_length = min_incomplete_term_length

    def analyze_input(self, query: str) -> Dict[str, Any]:
        """Analyze input text to identify prefix and incomplete term

        Args:
            query: User input query

        Returns:
            Dict containing:
                - prefix: Text before the incomplete term
                - incomplete_term: The last incomplete word
                - tokens: List of all tokens
                - is_long_query: Whether this qualifies for prefix preservation
        """
        try:
            # Tokenize using jieba
            tokens = jieba.lcut(query.strip())
            
            # Filter out empty tokens
            tokens = [t for t in tokens if t.strip()]
            
            # Determine if this is a long query
            is_long_query = len(tokens) >= self.min_tokens_for_prefix_mode
            
            # Identify incomplete term (last 1-2 tokens)
            if len(tokens) == 0:
                return {
                    "prefix": "",
                    "incomplete_term": "",
                    "tokens": [],
                    "is_long_query": False,
                }
            
            # For long queries, treat last token as incomplete if it's short
            # or if it's clearly a prefix (like "销" in "帮我查询一下今年北京的销")
            if is_long_query:
                incomplete_term = tokens[-1]
                # Check if term is likely incomplete (short or common prefix pattern)
                if len(incomplete_term) >= self.min_incomplete_term_length:
                    # Get prefix (everything before the incomplete term)
                    prefix = query[:query.rfind(incomplete_term)].strip()
                    
                    return {
                        "prefix": prefix,
                        "incomplete_term": incomplete_term,
                        "tokens": tokens,
                        "is_long_query": True,
                    }
            
            # Not a long query or doesn't fit pattern
            return {
                "prefix": "",
                "incomplete_term": query,
                "tokens": tokens,
                "is_long_query": False,
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze input: {e}")
            return {
                "prefix": "",
                "incomplete_term": query,
                "tokens": [],
                "is_long_query": False,
            }

    def search_completion_candidates(
        self, incomplete_term: str, limit: int = 20
    ) -> List[str]:
        """Search OpenSearch for completion candidates

        Args:
            incomplete_term: The incomplete word to complete
            limit: Maximum number of candidates to retrieve

        Returns:
            List of candidate completion terms
        """
        try:
            # Use prefix search in OpenSearch
            # Search for texts that start with or contain the incomplete term
            results = self.opensearch.keyword_search(
                query=incomplete_term,
                size=limit,
                min_score=0.1,
            )
            
            # Extract unique completion terms
            candidates = []
            seen = set()
            
            for result in results:
                text = result.get("text", "")
                # Try to extract the word that matches the incomplete term
                # For simplicity, we'll return full texts that contain completions
                if text and text.lower() not in seen:
                    seen.add(text.lower())
                    candidates.append(text)
            
            logger.info(f"Found {len(candidates)} candidates for '{incomplete_term}'")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to search completion candidates: {e}")
            return []

    def rank_and_complete(
        self,
        prefix: str,
        incomplete_term: str,
        candidates: List[str],
        user_context: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Use LLM to rank candidates and generate complete suggestions

        Args:
            prefix: Text before the incomplete term
            incomplete_term: The incomplete word
            candidates: List of candidate completions
            user_context: Optional user personalization context

        Returns:
            List of ranked completion results with text and score
        """
        if not self.llm_service or not self.llm_service.is_available():
            logger.warning("LLM service not available for prefix-preserving completion")
            # Fallback: simple prefix concatenation
            return self._fallback_completion(prefix, incomplete_term, candidates)
        
        try:
            # Use LLM to rank and complete
            completions = self.llm_service.rank_prefix_completions(
                prefix=prefix,
                incomplete_term=incomplete_term,
                candidates=candidates,
                user_context=user_context,
                limit=self.llm_result_limit,
            )
            
            return completions
            
        except Exception as e:
            logger.error(f"Failed to rank completions with LLM: {e}")
            return self._fallback_completion(prefix, incomplete_term, candidates)

    def _fallback_completion(
        self, prefix: str, incomplete_term: str, candidates: List[str]
    ) -> List[Dict[str, Any]]:
        """Fallback completion without LLM

        Simply concatenates prefix with candidate terms
        """
        results = []
        for i, candidate in enumerate(candidates[:self.llm_result_limit]):
            # Try to extract just the completion word from candidate
            # For now, use the full candidate as completion
            if incomplete_term and candidate.startswith(incomplete_term):
                # Candidate already starts with incomplete term
                completed_text = prefix + (candidate if not prefix else " " + candidate)
            else:
                # Use candidate as-is
                completed_text = prefix + (candidate if not prefix else " " + candidate)
            
            results.append({
                "text": completed_text.strip(),
                "score": 0.8 - (i * 0.05),  # Decreasing score
                "method": "fallback",
            })
        
        return results

    def _build_user_context(
        self, user_id: str, analysis: Dict
    ) -> Dict[str, Any]:
        """Build user personalization context

        Args:
            user_id: User identifier
            analysis: Input analysis results

        Returns:
            User context dictionary
        """
        if not self.personalization:
            return {}
        
        try:
            # Get user history
            history = self.personalization.get_user_preferences(user_id, limit=20)
            
            # Build context
            context = {
                "user_history": history[:5],  # Most recent 5 queries
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to build user context: {e}")
            return {}

    def get_suggestions_with_prefix_preservation(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> Optional[List[Suggestion]]:
        """Main entry point: Get prefix-preserving autocomplete suggestions

        Args:
            query: User input query
            user_id: Optional user ID for personalization
            limit: Maximum number of suggestions

        Returns:
            List of Suggestion objects, or None if prefix mode not applicable
        """
        try:
            # 1. Analyze input
            analysis = self.analyze_input(query)
            
            # 2. Check if prefix preservation mode should be used
            if not analysis["is_long_query"]:
                logger.debug("Query too short for prefix preservation mode")
                return None
            
            incomplete_term = analysis["incomplete_term"]
            if len(incomplete_term) < self.min_incomplete_term_length:
                logger.debug("Incomplete term too short")
                return None
            
            # 3. Search for completion candidates
            candidates = self.search_completion_candidates(
                incomplete_term, limit=self.candidate_limit
            )
            
            if not candidates:
                logger.info("No candidates found for completion")
                return None
            
            # 4. Get user context if available
            user_context = None
            if user_id and self.personalization:
                user_context = self._build_user_context(user_id, analysis)
            
            # 5. Use LLM to rank and complete
            results = self.rank_and_complete(
                prefix=analysis["prefix"],
                incomplete_term=incomplete_term,
                candidates=candidates,
                user_context=user_context,
            )
            
            if not results:
                return None
            
            # 6. Convert to Suggestion objects
            suggestions = []
            for result in results[:limit]:
                suggestion = Suggestion(
                    text=result["text"],
                    score=round(result.get("score", 0.5), 4),
                    source="prefix_preserved",
                    metadata={
                        "prefix": analysis["prefix"],
                        "incomplete_term": incomplete_term,
                        "method": result.get("method", "llm_ranked"),
                        "completed_term": result.get("completed_term", ""),
                    },
                )
                suggestions.append(suggestion)
            
            logger.info(
                f"Generated {len(suggestions)} prefix-preserved suggestions for: {query}"
            )
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get prefix-preserved suggestions: {e}")
            return None
