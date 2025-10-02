"""
Example demonstrating query sequence tracking and related queries optimization.

This example shows how the system learns from user behavior patterns (A->B->C sequences)
and provides intelligent related query suggestions.
"""

import json
from app.services.personalization_service import PersonalizationService


def simulate_user_behavior():
    """Simulate a user's query journey and show how sequences are tracked"""

    print("=" * 80)
    print("Query Sequence Tracking Example")
    print("=" * 80)
    print()

    # Create a mock Redis client for demonstration
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.sorted_sets = {}

        def lpush(self, key, value):
            if key not in self.data:
                self.data[key] = []
            self.data[key].insert(0, value)

        def ltrim(self, key, start, stop):
            if key in self.data:
                self.data[key] = self.data[key][start:stop+1]

        def lrange(self, key, start, stop):
            if key not in self.data:
                return []
            return self.data[key][start:stop+1 if stop >= 0 else None]

        def setex(self, key, time, value):
            self.data[key] = value

        def get(self, key):
            return self.data.get(key)

        def zincrby(self, key, increment, member):
            if key not in self.sorted_sets:
                self.sorted_sets[key] = {}
            self.sorted_sets[key][member] = self.sorted_sets[key].get(member, 0) + increment

        def zrevrange(self, key, start, stop, withscores=False):
            if key not in self.sorted_sets:
                return []
            items = sorted(self.sorted_sets[key].items(), key=lambda x: x[1], reverse=True)
            items = items[start:stop+1 if stop >= 0 else None]
            if withscores:
                return items
            return [item[0] for item in items]

        def scan_iter(self, match, count):
            pattern = match.replace('*', '')
            return [key for key in self.sorted_sets.keys() if pattern in key]

        def zscore(self, key, member):
            if key not in self.sorted_sets:
                return None
            return self.sorted_sets[key].get(member)

        def ping(self):
            return True

    # Initialize service with mock Redis
    mock_redis = MockRedis()
    service = PersonalizationService()
    service.redis_client = mock_redis

    user_id = "demo_user"

    print("Scenario: User makes a series of queries")
    print("-" * 80)
    print()

    # Simulate a typical user journey
    queries = [
        ("销售分析", "销售数据分析报告"),
        ("市场趋势", "2024市场趋势报告"),
        ("竞争分析", "行业竞争分析"),
        ("客户满意度", "客户满意度调查结果"),
    ]

    print("User's query sequence:")
    for i, (query, selection) in enumerate(queries, 1):
        print(f"  {i}. Query: '{query}' → Selected: '{selection}'")
        service.track_selection(user_id, query, selection)
    print()

    # Show what sequences were recorded
    print("Recorded sequences (Query A → Query B):")
    print("-" * 80)
    sequence_keys = [k for k in mock_redis.sorted_sets.keys() if k.startswith('sequence:')]
    for key in sequence_keys:
        prev_query = key.replace('sequence:', '')
        next_queries = mock_redis.zrevrange(key, 0, -1, withscores=True)
        for next_query, score in next_queries:
            print(f"  '{prev_query}' → '{next_query}' (score: {score})")
    print()

    # Now demonstrate how related queries work
    print("Getting related queries for '市场趋势':")
    print("-" * 80)
    sequences = service.get_query_sequences("市场趋势", user_id=user_id, limit=5)

    print("\nNext queries (what typically comes AFTER '市场趋势'):")
    if sequences['next']:
        for query, score in sequences['next']:
            print(f"  • '{query}' (score: {score})")
    else:
        print("  (none)")

    print("\nPrevious queries (what typically comes BEFORE '市场趋势'):")
    if sequences['previous']:
        for query, score in sequences['previous']:
            print(f"  • '{query}' (score: {score})")
    else:
        print("  (none)")

    print()
    print("=" * 80)
    print("Key Points:")
    print("=" * 80)
    print("• Next queries get HIGHER scores (0.85-0.95) - likely the user's next question")
    print("• Previous queries get LOWER scores (0.65-0.75) - contextual but less likely")
    print("• This helps users discover the natural flow of queries")
    print("• System learns from real user behavior patterns")
    print()


def show_integration_example():
    """Show how this integrates with the autocomplete service"""

    print("=" * 80)
    print("Integration with Related Queries API")
    print("=" * 80)
    print()

    print("When a user calls GET /api/v1/related-queries:")
    print()
    print("Request:")
    print(json.dumps({
        "query": "市场趋势",
        "user_id": "user123",
        "limit": 5
    }, ensure_ascii=False, indent=2))
    print()

    print("The system will:")
    print("  1. Get sequence-based queries (next and previous)")
    print("  2. Get hybrid search results (keyword + vector similarity)")
    print("  3. Get user's historical preferences")
    print("  4. Combine and deduplicate all results")
    print("  5. Sort by score (next queries naturally rank highest)")
    print()

    print("Example Response:")
    print(json.dumps({
        "query": "市场趋势",
        "related_queries": [
            {
                "text": "竞争分析",
                "score": 0.92,
                "source": "sequence_next",
                "metadata": {
                    "from_sequence": True,
                    "sequence_type": "next",
                    "sequence_score": 5.0
                }
            },
            {
                "text": "行业报告",
                "score": 0.85,
                "source": "hybrid",
                "metadata": {
                    "keywords": ["industry", "report"],
                    "doc_id": "doc123"
                }
            },
            {
                "text": "销售分析",
                "score": 0.72,
                "source": "sequence_prev",
                "metadata": {
                    "from_sequence": True,
                    "sequence_type": "previous",
                    "sequence_score": 3.0
                }
            }
        ],
        "total": 3
    }, ensure_ascii=False, indent=2))
    print()


if __name__ == "__main__":
    simulate_user_behavior()
    print()
    show_integration_example()
