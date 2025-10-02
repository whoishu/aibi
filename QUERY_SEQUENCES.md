# Query Sequence Tracking - Technical Documentation

## Overview

The query sequence tracking feature enhances the related queries API by analyzing user behavior patterns. When users follow a query sequence like A→B→C, the system learns and suggests:
- **Next queries**: What typically comes AFTER the current query (higher priority)
- **Previous queries**: What typically comes BEFORE the current query (lower priority)

## How It Works

### 1. Tracking Query Sequences

When a user makes a selection after a query, the system:

```python
# User queries "销售分析", then "市场趋势"
# System stores: "销售分析" → "市场趋势"

# Redis data structures:
sequence:销售分析 → {市场趋势: 1}  # Global sequence
user:user123:sequence:销售分析 → {市场趋势: 1}  # User-specific sequence
```

### 2. Retrieving Related Queries

When requesting related queries for "市场趋势":

```python
GET /api/v1/related-queries
{
  "query": "市场趋势",
  "user_id": "user123",
  "limit": 10
}
```

The system:
1. Finds "next" queries (what comes after "市场趋势") → e.g., "竞争分析"
2. Finds "previous" queries (what comes before "市场趋势") → e.g., "销售分析"
3. Combines with hybrid search and user history
4. Scores and prioritizes results

### 3. Scoring Strategy

```
Next queries:     0.85-0.95 (HIGH priority - likely next question)
Hybrid search:    0.4-0.8   (MEDIUM priority - semantic similarity)
Previous queries: 0.65-0.75 (LOWER priority - contextual)
User history:     0.7       (MEDIUM priority - user preferences)
```

## Example Scenario

### User Journey
```
User: Alice
1. Queries "销售分析" → selects result
2. Queries "市场趋势" → selects result
3. Queries "竞争分析" → selects result
```

### What Gets Stored
```
Sequences:
- "销售分析" → "市场趋势" (score: 1)
- "市场趋势" → "竞争分析" (score: 1)
```

### When Bob Queries "市场趋势"
```json
{
  "query": "市场趋势",
  "related_queries": [
    {
      "text": "竞争分析",
      "score": 0.92,
      "source": "sequence_next",
      "metadata": {
        "from_sequence": true,
        "sequence_type": "next",
        "sequence_score": 5.0
      }
    },
    {
      "text": "行业报告",
      "score": 0.85,
      "source": "hybrid",
      "metadata": {
        "keywords": ["industry", "report"]
      }
    },
    {
      "text": "销售分析",
      "score": 0.72,
      "source": "sequence_prev",
      "metadata": {
        "from_sequence": true,
        "sequence_type": "previous",
        "sequence_score": 3.0
      }
    }
  ]
}
```

## Redis Data Structures

### 1. Query Sequences (Global)
```
Key: sequence:{query}
Type: Sorted Set
Members: Next queries with their frequency scores

Example:
sequence:市场趋势 → {竞争分析: 10, 行业分析: 5, 业绩报告: 3}
```

### 2. Query Sequences (User-Specific)
```
Key: user:{user_id}:sequence:{query}
Type: Sorted Set
Members: Next queries with their frequency scores

Example:
user:alice:sequence:市场趋势 → {竞争分析: 3, 业绩报告: 2}
```

### 3. User History
```
Key: user:{user_id}:history
Type: List
Members: JSON objects with {query, selected, timestamp}

Example:
user:alice:history → [
  {"query": "竞争分析", "selected": "...", "timestamp": "2024-01-03T10:00:00"},
  {"query": "市场趋势", "selected": "...", "timestamp": "2024-01-03T09:30:00"},
  {"query": "销售分析", "selected": "...", "timestamp": "2024-01-03T09:00:00"}
]
```

## API Changes

### No Breaking Changes
The implementation is fully backward compatible. Existing API calls work exactly as before.

### Enhanced Responses
Related queries now include new sources:
- `sequence_next`: Query typically follows the input query
- `sequence_prev`: Query typically precedes the input query

## Implementation Details

### PersonalizationService

#### New Methods:
```python
def get_query_sequences(query: str, user_id: Optional[str] = None, limit: int = 10) -> Dict:
    """Get queries that typically come after (next) or before (previous) the given query
    
    Returns:
        {
            "next": [(query1, score1), (query2, score2), ...],
            "previous": [(query3, score3), ...]
        }
    """
```

#### Enhanced Methods:
```python
def track_selection(user_id: str, query: str, selected_text: str, timestamp: Optional[str] = None):
    """Now also tracks query sequences in addition to existing tracking"""
```

### AutocompleteService

#### Enhanced Methods:
```python
def get_related_queries(query: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Now incorporates query sequences with proper prioritization:
    1. Next queries (highest score)
    2. Hybrid search results
    3. User history
    4. Previous queries (lower score)
    """
```

## Benefits

### For Users
- ✅ Discovers natural query flow
- ✅ Suggests likely next questions
- ✅ Provides contextual alternatives
- ✅ Learns from actual usage patterns

### For the System
- ✅ Uses real user behavior data
- ✅ No manual curation needed
- ✅ Improves over time
- ✅ Personalized to each user

## Performance Considerations

### Redis Operations
- Sequence tracking: 2 ZINCRBY operations per query (O(log N))
- Sequence retrieval: 2 ZREVRANGE operations (O(log N + M))
- Previous query lookup: SCAN operations (can be expensive with many keys)

### Optimization Tips
1. Limit the number of sequences stored per query (top 100)
2. Set TTL on sequence keys (30-90 days)
3. Use Redis pipelining for bulk operations
4. Consider caching frequently accessed sequences

## Testing

### Unit Tests
```bash
pytest tests/unit/test_query_sequences.py -v
```

Tests cover:
- Query sequence tracking
- Next/previous query retrieval
- Score prioritization
- Deduplication
- Error handling

### Integration Tests
```bash
pytest tests/integration/test_query_endpoints.py -v
```

All existing tests pass, ensuring backward compatibility.

## Future Enhancements

### Potential Improvements:
1. **LLM-based query generation**: Use LLM to generate related queries based on sequences
2. **Temporal patterns**: Consider time-of-day or day-of-week patterns
3. **Query embeddings**: Cluster similar sequences for better generalization
4. **A/B testing**: Compare sequence-based vs traditional related queries
5. **Decay factors**: Weight recent sequences more heavily than old ones

## Monitoring

### Key Metrics to Track:
- Sequence coverage: % of queries with stored sequences
- Click-through rate: Users clicking sequence-based suggestions
- Query diversity: Number of unique sequences per query
- Storage growth: Redis memory usage for sequences

### Dashboard Queries:
```redis
# Count total sequences
KEYS sequence:* | COUNT

# Get top sequences for a query
ZREVRANGE sequence:市场趋势 0 10 WITHSCORES

# Check user-specific sequences
ZREVRANGE user:alice:sequence:市场趋势 0 10 WITHSCORES
```

## Troubleshooting

### Issue: No sequences returned
**Cause**: Not enough user data collected yet
**Solution**: System needs users to make sequential queries to build patterns

### Issue: Only previous queries, no next queries
**Cause**: Query is typically the last in a sequence
**Solution**: This is expected behavior for terminal queries

### Issue: Sequences not updating
**Cause**: Redis connection issues or storage limits
**Solution**: Check Redis connectivity and memory limits

## Summary

The query sequence tracking feature makes the related queries API smarter by learning from actual user behavior. It prioritizes likely next questions while still providing contextual alternatives, creating a more intuitive and helpful user experience.
