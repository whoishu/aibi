"""Main autocomplete service orchestrating all components"""

import logging
from typing import List, Dict, Any, Optional
from app.services.opensearch_service import OpenSearchService
from app.services.vector_service import VectorService
from app.services.personalization_service import PersonalizationService
from app.models.schemas import Suggestion

logger = logging.getLogger(__name__)


class AutocompleteService:
    """Main service for autocomplete functionality"""
    
    def __init__(
        self,
        opensearch_service: OpenSearchService,
        vector_service: VectorService,
        personalization_service: Optional[PersonalizationService] = None,
        keyword_weight: float = 0.7,
        vector_weight: float = 0.3,
        personalization_weight: float = 0.2,
        enable_personalization: bool = True
    ):
        """Initialize autocomplete service
        
        Args:
            opensearch_service: OpenSearch service instance
            vector_service: Vector service instance
            personalization_service: Personalization service instance
            keyword_weight: Weight for keyword search
            vector_weight: Weight for vector search
            personalization_weight: Weight for personalization boost
            enable_personalization: Whether to enable personalization
        """
        self.opensearch = opensearch_service
        self.vector_service = vector_service
        self.personalization = personalization_service
        self.keyword_weight = keyword_weight
        self.vector_weight = vector_weight
        self.personalization_weight = personalization_weight
        self.enable_personalization = enable_personalization and personalization_service is not None
    
    def get_suggestions(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.1
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
            
            # Generate query vector
            query_vector = self.vector_service.encode_single(query)
            
            # Perform hybrid search
            results = self.opensearch.hybrid_search(
                query=query,
                query_vector=query_vector,
                size=limit * 2,  # Get more results for better filtering
                keyword_weight=self.keyword_weight,
                vector_weight=self.vector_weight,
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
            
            # Convert to Suggestion objects
            suggestions = []
            for result in results[:limit]:
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
                        **result.get("metadata", {})
                    }
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
        timestamp: Optional[str] = None
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
                    timestamp=timestamp
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
        metadata: Optional[Dict[str, Any]] = None
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
                doc_id=doc_id,
                text=text,
                vector=vector,
                keywords=keywords,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Added document: {text[:50]}...")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def add_documents_bulk(
        self,
        documents: List[Dict[str, Any]]
    ) -> tuple:
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
                
                processed_docs.append({
                    "doc_id": doc_id,
                    "text": doc["text"],
                    "vector": vectors[i].tolist(),
                    "keywords": doc.get("keywords", []),
                    "metadata": doc.get("metadata", {})
                })
            
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
        """Get related queries based on keywords, co-occurrence, and user history
        
        Args:
            query: User input query
            user_id: Optional user ID for personalization
            limit: Maximum number of related queries
            min_score: Minimum score threshold
            
        Returns:
            List of related queries with metadata
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
                            "score": 0.8,  # Fixed score for historical queries
                            "source": "history",
                            "keywords": [],
                            "metadata": {"from_user_history": True}
                        })
            
            # Combine results with history
            all_results = results + related_from_history
            
            # Deduplicate by text (case-insensitive)
            seen_texts = set()
            unique_results = []
            for result in all_results:
                text_lower = result["text"].lower()
                if text_lower not in seen_texts and text_lower != query.lower():
                    seen_texts.add(text_lower)
                    unique_results.append(result)
            
            # Sort by score
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
