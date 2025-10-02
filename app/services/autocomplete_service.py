"""Main autocomplete service orchestrating all components"""

import logging
from typing import Any, Dict, List, Optional

from app.models.schemas import Suggestion
from app.services.opensearch_service import OpenSearchService
from app.services.personalization_service import PersonalizationService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.services.prefix_preserving_service import PrefixPreservingService

logger = logging.getLogger(__name__)


class AutocompleteService:
    """Main service for autocomplete functionality"""

    def __init__(
        self,
        opensearch_service: OpenSearchService,
        vector_service: VectorService,
        personalization_service: Optional[PersonalizationService] = None,
        llm_service: Optional[LLMService] = None,
        keyword_weight: float = 0.7,
        vector_weight: float = 0.3,
        personalization_weight: float = 0.2,
        enable_personalization: bool = True,
        enable_llm: bool = False,
        enable_prefix_preservation: bool = True,
    ):
        """Initialize autocomplete service

        Args:
            opensearch_service: OpenSearch service instance
            vector_service: Vector service instance
            personalization_service: Personalization service instance
            llm_service: LLM service instance for enhanced recommendations
            keyword_weight: Weight for keyword search
            vector_weight: Weight for vector search
            personalization_weight: Weight for personalization boost
            enable_personalization: Whether to enable personalization
            enable_llm: Whether to enable LLM-powered enhancements
            enable_prefix_preservation: Whether to enable prefix-preserving mode
        """
        self.opensearch = opensearch_service
        self.vector_service = vector_service
        self.personalization = personalization_service
        self.llm_service = llm_service
        self.keyword_weight = keyword_weight
        self.vector_weight = vector_weight
        self.personalization_weight = personalization_weight
        self.enable_personalization = enable_personalization and personalization_service is not None
        self.enable_llm = enable_llm and llm_service is not None and llm_service.is_available()
        self.enable_prefix_preservation = enable_prefix_preservation
        
        # Initialize prefix-preserving service if LLM is available
        self.prefix_preserving_service = None
        if self.enable_prefix_preservation and self.enable_llm and llm_service is not None:
            self.prefix_preserving_service = PrefixPreservingService(
                opensearch_service=opensearch_service,
                llm_service=llm_service,
                personalization_service=personalization_service,
            )

    def get_suggestions(
        self, query: str, user_id: Optional[str] = None, limit: int = 10, min_score: float = 0.1
    ) -> List[Suggestion]:
        """Get autocomplete suggestions for a query

        Args:
            query: User input query
            user_id: Optional user ID for personalization
            limit: Maximum number of suggestions
            min_score: Minimum score threshold

        Returns:
            List of suggestions
        """
        try:
            # Handle empty query
            if not query or len(query.strip()) == 0:
                return []

            query = query.strip()
            
            # Try prefix-preserving mode for long queries
            if self.prefix_preserving_service:
                prefix_results = self.prefix_preserving_service.get_suggestions_with_prefix_preservation(
                    query=query,
                    user_id=user_id,
                    limit=limit,
                )
                if prefix_results:
                    logger.info(f"Using prefix-preserving mode for query: {query}")
                    return prefix_results

            # Use LLM to expand/enhance query if enabled
            search_queries = [query]
            if self.enable_llm and len(query) > 3:  # Only for non-trivial queries
                context = {}
                if self.enable_personalization and user_id:
                    # Get user history for context
                    user_prefs = self.personalization.get_user_preferences(user_id, limit=5)
                    if user_prefs:
                        context["user_history"] = user_prefs
                
                expanded_queries = self.llm_service.expand_query(query, context=context)
                if expanded_queries:
                    # Add top 2 expanded queries for broader search coverage
                    search_queries.extend(expanded_queries[:2])
                    logger.info(f"LLM expanded query to: {search_queries}")

            # Collect results from all query variations
            all_results = []
            for search_query in search_queries:
                # Generate query vector
                query_vector = self.vector_service.encode_single(search_query)

                # Perform hybrid search
                results = self.opensearch.hybrid_search(
                    query=search_query,
                    query_vector=query_vector,
                    size=limit * 2,  # Get more results for better filtering
                    keyword_weight=self.keyword_weight,
                    vector_weight=self.vector_weight,
                    min_score=min_score,
                )
                
                # Boost original query results slightly
                if search_query == query:
                    for result in results:
                        result["score"] = result["score"] * 1.1
                
                all_results.extend(results)

            # Deduplicate by text
            seen_texts = set()
            unique_results = []
            for result in all_results:
                text_lower = result["text"].lower()
                if text_lower not in seen_texts:
                    seen_texts.add(text_lower)
                    unique_results.append(result)

            # Sort by score
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)

            # Apply personalization if enabled
            if self.enable_personalization and user_id:
                unique_results = self.personalization.boost_personalized_results(
                    user_id=user_id,
                    query=query,
                    results=unique_results,
                    boost_factor=self.personalization_weight,
                )

            # Convert to Suggestion objects
            suggestions = []
            for result in unique_results[:limit]:
                # Determine source
                source = "hybrid"
                if "source" in result:
                    source = result["source"]
                elif result.get("keyword_score", 0) > 0 and result.get("vector_score", 0) == 0:
                    source = "keyword"
                elif result.get("vector_score", 0) > 0 and result.get("keyword_score", 0) == 0:
                    source = "vector"

                suggestion = Suggestion(
                    text=result["text"],
                    score=round(result["score"], 4),
                    source=source,
                    metadata={
                        "keywords": result.get("keywords", []),
                        "doc_id": result.get("doc_id"),
                        **result.get("metadata", {}),
                    },
                )
                suggestions.append(suggestion)

            logger.info(f"Generated {len(suggestions)} suggestions for query: {query}")
            return suggestions

        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []

    def record_feedback(
        self,
        query: str,
        selected_suggestion: str,
        user_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> bool:
        """Record user feedback (selection)

        Args:
            query: Original query
            selected_suggestion: Selected suggestion text
            user_id: User ID
            timestamp: Timestamp of selection

        Returns:
            True if successful, False otherwise
        """
        try:
            success = True

            # Track in personalization service
            if self.enable_personalization and user_id and self.personalization:
                success = self.personalization.track_selection(
                    user_id=user_id,
                    query=query,
                    selected_text=selected_suggestion,
                    timestamp=timestamp,
                )

            # Update frequency in OpenSearch (for general popularity)
            # Note: This would require finding the doc_id first
            # For now, we track it through personalization service

            logger.info(f"Recorded feedback: {query} -> {selected_suggestion}")
            return success

        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    def add_document(
        self,
        text: str,
        doc_id: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add a document to the autocomplete index

        Args:
            text: Document text
            doc_id: Optional document ID
            keywords: Optional list of keywords
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate document ID if not provided
            if doc_id is None:
                import hashlib

                doc_id = hashlib.md5(text.encode()).hexdigest()

            # Generate vector embedding
            vector = self.vector_service.encode_single(text)

            # Index in OpenSearch
            success = self.opensearch.index_document(
                doc_id=doc_id, text=text, vector=vector, keywords=keywords, metadata=metadata
            )

            if success:
                logger.info(f"Added document: {text[:50]}...")

            return success

        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False

    def add_documents_bulk(self, documents: List[Dict[str, Any]]) -> tuple:
        """Add multiple documents in bulk

        Args:
            documents: List of document dicts with 'text' and optional 'keywords', 'metadata'

        Returns:
            Tuple of (success_count, error_count)
        """
        try:
            # Process documents and generate embeddings
            processed_docs = []
            texts = [doc["text"] for doc in documents]

            # Batch encode all texts
            vectors = self.vector_service.encode(texts)

            for i, doc in enumerate(documents):
                import hashlib

                doc_id = doc.get("doc_id")
                if doc_id is None:
                    doc_id = hashlib.md5(doc["text"].encode()).hexdigest()

                processed_docs.append(
                    {
                        "doc_id": doc_id,
                        "text": doc["text"],
                        "vector": vectors[i].tolist(),
                        "keywords": doc.get("keywords", []),
                        "metadata": doc.get("metadata", {}),
                    }
                )

            # Bulk index
            success, errors = self.opensearch.bulk_index_documents(processed_docs)
            logger.info(f"Bulk added {success} documents with {errors} errors")
            return success, errors

        except Exception as e:
            logger.error(f"Failed to bulk add documents: {e}")
            return 0, len(documents)

    def get_similar_queries(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Get similar queries based on semantic similarity

        Args:
            query: User input query
            user_id: Optional user ID for personalization
            limit: Maximum number of similar queries
            min_score: Minimum score threshold

        Returns:
            List of similar queries with metadata
        """
        try:
            # Handle empty query
            if not query or len(query.strip()) == 0:
                return []

            query = query.strip()

            # Generate query vector
            query_vector = self.vector_service.encode_single(query)

            # Use vector search for semantic similarity
            results = self.opensearch.vector_search(
                query_vector=query_vector,
                size=limit * 2,
                min_score=min_score
            )

            # Apply personalization if enabled
            if self.enable_personalization and user_id:
                results = self.personalization.boost_personalized_results(
                    user_id=user_id,
                    query=query,
                    results=results,
                    boost_factor=self.personalization_weight
                )

            # Convert to QueryItem format
            similar_queries = []
            for result in results[:limit]:
                # Skip if it's the same as input query
                if result["text"].lower() == query.lower():
                    continue

                # Determine source
                source = "vector"
                if "source" in result:
                    source = result["source"]

                query_item = {
                    "text": result["text"],
                    "score": round(result["score"], 4),
                    "source": source,
                    "metadata": {
                        "keywords": result.get("keywords", []),
                        "doc_id": result.get("doc_id"),
                        **result.get("metadata", {})
                    }
                }
                similar_queries.append(query_item)

            logger.info(f"Generated {len(similar_queries)} similar queries for: {query}")
            return similar_queries

        except Exception as e:
            logger.error(f"Failed to get similar queries: {e}")
            return []

    def get_related_queries(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Get related queries based on query sequences, keywords, co-occurrence, and user history

        This method analyzes user query patterns (A->B->C sequences) to provide contextual suggestions.
        When a user queries something similar to B, it suggests:
        - C (queries that typically follow B) with higher priority
        - A (queries that typically precede B) with lower priority

        Args:
            query: User input query
            user_id: Optional user ID for personalization
            limit: Maximum number of related queries
            min_score: Minimum score threshold

        Returns:
            List of related queries with metadata, ordered by relevance
        """
        try:
            # Handle empty query
            if not query or len(query.strip()) == 0:
                return []

            query = query.strip()

            # Generate query vector for hybrid search
            query_vector = self.vector_service.encode_single(query)

            # Use hybrid search with higher keyword weight for related queries
            # Related queries should include both semantically similar and keyword-related
            results = self.opensearch.hybrid_search(
                query=query,
                query_vector=query_vector,
                size=limit * 2,
                keyword_weight=0.6,  # Higher keyword weight for related queries
                vector_weight=0.4,
                min_score=min_score
            )

            # Get query sequences if personalization is enabled
            sequence_queries = []
            if self.enable_personalization and self.personalization:
                sequences = self.personalization.get_query_sequences(query, user_id=user_id, limit=10)

                # Add "next" queries (queries that typically follow the current query)
                # These get higher scores as they represent the likely next question
                for query_text, seq_score in sequences.get("next", []):
                    if query_text.lower() != query.lower():
                        # Higher score for next queries (0.85-0.95 range)
                        normalized_score = min(0.95, 0.85 + (seq_score / 20))
                        sequence_queries.append({
                            "text": query_text,
                            "score": normalized_score,
                            "source": "sequence_next",
                            "keywords": [],
                            "metadata": {
                                "from_sequence": True,
                                "sequence_type": "next",
                                "sequence_score": seq_score
                            }
                        })

                # Add "previous" queries (queries that typically precede the current query)
                # These get lower scores as they are less likely to be the user's next question
                for query_text, seq_score in sequences.get("previous", []):
                    if query_text.lower() != query.lower():
                        # Lower score for previous queries (0.65-0.75 range)
                        normalized_score = min(0.75, 0.65 + (seq_score / 20))
                        sequence_queries.append({
                            "text": query_text,
                            "score": normalized_score,
                            "source": "sequence_prev",
                            "keywords": [],
                            "metadata": {
                                "from_sequence": True,
                                "sequence_type": "previous",
                                "sequence_score": seq_score
                            }
                        })

            # Get user preferences if personalization is enabled
            related_from_history = []
            if self.enable_personalization and user_id and self.personalization:
                # Get user's query history for related queries
                user_prefs = self.personalization.get_user_preferences(user_id, limit=20)
                for pref in user_prefs:
                    # Add queries from user history that aren't already in results
                    if pref.lower() != query.lower():
                        related_from_history.append({
                            "text": pref,
                            "score": 0.7,  # Fixed score for historical queries
                            "source": "history",
                            "keywords": [],
                            "metadata": {"from_user_history": True}
                        })

            # Get LLM-generated related queries if enabled
            llm_queries = []
            if self.enable_llm:
                # Build context for LLM
                context = {}
                if self.enable_personalization and user_id:
                    user_prefs = self.personalization.get_user_preferences(user_id, limit=5)
                    if user_prefs:
                        context["user_history"] = user_prefs
                
                # Get existing query texts to avoid duplication
                existing_texts = [r["text"] for r in sequence_queries + results + related_from_history]
                
                llm_queries = self.llm_service.generate_related_queries(
                    query=query,
                    existing_results=existing_texts,
                    limit=5,
                    context=context
                )
                if llm_queries:
                    logger.info(f"LLM generated {len(llm_queries)} related queries")

            # Combine all results: LLM first (highest quality), then sequence queries, hybrid search, then history
            all_results = llm_queries + sequence_queries + results + related_from_history

            # Deduplicate by text (case-insensitive), keeping the first occurrence (highest priority)
            seen_texts = set()
            unique_results = []
            for result in all_results:
                text_lower = result["text"].lower()
                if text_lower not in seen_texts and text_lower != query.lower():
                    seen_texts.add(text_lower)
                    unique_results.append(result)

            # Sort by score (LLM and next queries will naturally rank higher)
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)

            # Convert to QueryItem format
            related_queries = []
            for result in unique_results[:limit]:
                # Determine source
                source = result.get("source", "hybrid")

                query_item = {
                    "text": result["text"],
                    "score": round(result.get("score", 0), 4),
                    "source": source,
                    "metadata": {
                        "keywords": result.get("keywords", []),
                        "doc_id": result.get("doc_id"),
                        **result.get("metadata", {})
                    }
                }
                related_queries.append(query_item)

            logger.info(f"Generated {len(related_queries)} related queries for: {query}")
            return related_queries

        except Exception as e:
            logger.error(f"Failed to get related queries: {e}")
            return []
