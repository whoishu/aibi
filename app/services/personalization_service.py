"""Personalization service using Redis for user behavior tracking"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Service for tracking user behavior and providing personalized recommendations"""

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """Initialize personalization service

        Args:
            redis_host: Redis host
            redis_port: Redis port
            redis_db: Redis database number
        """
        self.redis_client = None
        self.redis_config = {
            "host": redis_host,
            "port": redis_port,
            "db": redis_db,
            "decode_responses": True,
        }
        self._connect()

    def _connect(self):
        """Connect to Redis"""
        try:
            import redis

            self.redis_client = redis.Redis(**self.redis_config)
            self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Personalization disabled.")
            self.redis_client = None

    def check_connection(self) -> bool:
        """Check if Redis is connected

        Returns:
            True if connected, False otherwise
        """
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False

    def _get_previous_query(self, user_id: str) -> Optional[str]:
        """Get the most recent query from user's history

        Args:
            user_id: User ID

        Returns:
            Previous query text or None
        """
        if self.redis_client is None:
            return None

        try:
            history_key = f"user:{user_id}:history"
            # Get the most recent item (index 0)
            recent_items = self.redis_client.lrange(history_key, 0, 0)
            if recent_items:
                history_item = json.loads(recent_items[0])
                return history_item.get("query")
            return None
        except Exception as e:
            logger.error(f"Failed to get previous query: {e}")
            return None

    def track_selection(
        self, user_id: str, query: str, selected_text: str, timestamp: Optional[str] = None
    ) -> bool:
        """Track user's selection for a query

        Args:
            user_id: User ID
            query: Original query
            selected_text: Text that user selected
            timestamp: Timestamp of selection

        Returns:
            True if successful, False otherwise
        """
        if self.redis_client is None:
            return False

        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()

            # Store in multiple structures for different query patterns

            # 1. User's selection history
            history_key = f"user:{user_id}:history"
            history_item = json.dumps(
                {"query": query, "selected": selected_text, "timestamp": timestamp}
            )
            self.redis_client.lpush(history_key, history_item)
            self.redis_client.ltrim(history_key, 0, 999)  # Keep last 1000 items

            # 2. User's query -> selection mapping (most recent)
            query_key = f"user:{user_id}:query:{query}"
            self.redis_client.setex(query_key, timedelta(days=30), selected_text)

            # 3. User's frequent selections
            freq_key = f"user:{user_id}:freq"
            self.redis_client.zincrby(freq_key, 1, selected_text)

            # 4. Global query -> selection frequency
            global_key = f"global:query:{query}"
            self.redis_client.zincrby(global_key, 1, selected_text)

            # 5. Track query sequences for better related query suggestions
            # Get the previous query from user's recent history
            prev_query = self._get_previous_query(user_id)
            if prev_query and prev_query != query:
                # Store: previous_query -> current_query sequence
                sequence_key = f"sequence:{prev_query}"
                self.redis_client.zincrby(sequence_key, 1, query)
                # Also store user-specific sequences
                user_sequence_key = f"user:{user_id}:sequence:{prev_query}"
                self.redis_client.zincrby(user_sequence_key, 1, query)

            logger.debug(f"Tracked selection for user {user_id}: {query} -> {selected_text}")
            return True

        except Exception as e:
            logger.error(f"Failed to track selection: {e}")
            return False

    def get_user_preferences(self, user_id: str, limit: int = 20) -> List[str]:
        """Get user's most frequent selections

        Args:
            user_id: User ID
            limit: Maximum number of preferences to return

        Returns:
            List of frequently selected texts
        """
        if self.redis_client is None:
            return []

        try:
            freq_key = f"user:{user_id}:freq"
            # Get top selections by score (descending)
            results = self.redis_client.zrevrange(freq_key, 0, limit - 1)
            return list(results) if results else []

        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return []

    def get_user_query_history(self, user_id: str, query: str) -> Optional[str]:
        """Get user's previous selection for a specific query

        Args:
            user_id: User ID
            query: Query string

        Returns:
            Previous selection or None
        """
        if self.redis_client is None:
            return None

        try:
            query_key = f"user:{user_id}:query:{query}"
            return self.redis_client.get(query_key)

        except Exception as e:
            logger.error(f"Failed to get query history: {e}")
            return None

    def get_global_preferences(self, query: str, limit: int = 10) -> List[tuple]:
        """Get global most selected items for a query

        Args:
            query: Query string
            limit: Maximum number of results

        Returns:
            List of (text, score) tuples
        """
        if self.redis_client is None:
            return []

        try:
            global_key = f"global:query:{query}"
            # Get top selections with scores
            results = self.redis_client.zrevrange(global_key, 0, limit - 1, withscores=True)
            return list(results) if results else []

        except Exception as e:
            logger.error(f"Failed to get global preferences: {e}")
            return []

    def get_query_sequences(
        self, query: str, user_id: Optional[str] = None, limit: int = 10
    ) -> Dict[str, List[tuple]]:
        """Get queries that typically come after (next) or before (previous) the given query

        Args:
            query: Query string
            user_id: Optional user ID for personalized sequences
            limit: Maximum number of sequences to return

        Returns:
            Dictionary with 'next' and 'previous' query lists, each containing (query, score) tuples
        """
        if self.redis_client is None:
            return {"next": [], "previous": []}

        try:
            result = {"next": [], "previous": []}

            # Get queries that come after this query (next queries)
            # First check user-specific sequences if user_id is provided
            if user_id:
                user_sequence_key = f"user:{user_id}:sequence:{query}"
                user_next = self.redis_client.zrevrange(user_sequence_key, 0, limit - 1, withscores=True)
                if user_next:
                    result["next"].extend(user_next)

            # Then check global sequences
            global_sequence_key = f"sequence:{query}"
            global_next = self.redis_client.zrevrange(global_sequence_key, 0, limit - 1, withscores=True)

            # Combine and deduplicate next queries
            seen_queries = {q for q, _ in result["next"]}
            for query_text, score in global_next:
                if query_text not in seen_queries:
                    result["next"].append((query_text, score))
                    seen_queries.add(query_text)

            # Limit the results
            result["next"] = result["next"][:limit]

            # Get queries that come before this query (previous queries)
            # We need to find all keys where this query is a value in the sequence
            # For performance, we'll scan user-specific and global sequence keys
            if user_id:
                # Check user-specific sequences
                pattern = f"user:{user_id}:sequence:*"
                for key in self.redis_client.scan_iter(match=pattern, count=100):
                    score = self.redis_client.zscore(key, query)
                    if score is not None:
                        # Extract the previous query from the key
                        prev_query = key.split(f"user:{user_id}:sequence:")[1]
                        if prev_query and prev_query != query:
                            result["previous"].append((prev_query, score))

            # Also check global sequences
            pattern = "sequence:*"
            for key in self.redis_client.scan_iter(match=pattern, count=100):
                score = self.redis_client.zscore(key, query)
                if score is not None:
                    # Extract the previous query from the key
                    prev_query = key.split("sequence:")[1]
                    if prev_query and prev_query != query:
                        # Check if not already in results
                        if prev_query not in {q for q, _ in result["previous"]}:
                            result["previous"].append((prev_query, score))

            # Sort previous queries by score and limit
            result["previous"].sort(key=lambda x: x[1], reverse=True)
            result["previous"] = result["previous"][:limit]

            logger.debug(f"Found {len(result['next'])} next and {len(result['previous'])} previous queries for: {query}")
            return result

        except Exception as e:
            logger.error(f"Failed to get query sequences: {e}")
            return {"next": [], "previous": []}

    def boost_personalized_results(
        self, user_id: str, query: str, results: List[Dict[str, Any]], boost_factor: float = 0.2
    ) -> List[Dict[str, Any]]:
        """Apply personalization boost to search results

        Args:
            user_id: User ID
            query: Query string
            results: List of search results
            boost_factor: How much to boost personalized items (0-1)

        Returns:
            Results with adjusted scores
        """
        if self.redis_client is None or not user_id:
            return results

        try:
            # Get user preferences
            user_prefs = set(self.get_user_preferences(user_id, limit=50))
            query_history = self.get_user_query_history(user_id, query)

            # Boost matching results
            boosted_results = []
            for result in results:
                text = result["text"]
                score = result["score"]

                # Strong boost if exact query match from history
                if query_history and text == query_history:
                    score = score * (1 + boost_factor * 2)
                    result["source"] = "personalized"
                # Moderate boost if in user preferences
                elif text in user_prefs:
                    score = score * (1 + boost_factor)
                    result["source"] = result.get("source", "hybrid") + "+personalized"

                result["score"] = score
                boosted_results.append(result)

            # Re-sort by adjusted scores
            boosted_results.sort(key=lambda x: x["score"], reverse=True)
            return boosted_results

        except Exception as e:
            logger.error(f"Failed to boost results: {e}")
            return results
