# Prefix-Preserving Autocomplete Feature

## Overview

The prefix-preserving autocomplete feature intelligently completes long queries while preserving the full user context. This is particularly useful for Chinese queries where users type partial words at the end of a longer phrase.

## Problem Statement

Traditional autocomplete systems replace the entire query when suggesting completions. For long queries like "帮我查询一下今年北京的销", users expect to see completions like:
- "帮我查询一下今年北京的**销售额**"
- "帮我查询一下今年北京的**销量**"
- "帮我查询一下今年北京的**销售情况**"

Instead of completely different queries.

## How It Works

### Architecture

```
User Query
    ↓
Tokenization (jieba)
    ↓
Prefix/Incomplete Term Detection
    ↓
    ├─── Short Query (< 5 tokens) → Regular Autocomplete
    └─── Long Query (≥ 5 tokens)
            ↓
        Search Candidates (OpenSearch)
            ↓
        LLM Ranking & Completion
            ↓
        Prefix-Preserved Suggestions
```

### Components

#### 1. PrefixPreservingService

The main service handling prefix-preserving autocomplete logic.

**Key Methods:**

- `analyze_input(query)`: Tokenizes the query and identifies prefix/incomplete term
- `search_completion_candidates(incomplete_term)`: Searches OpenSearch for candidates
- `rank_and_complete(prefix, incomplete_term, candidates)`: Uses LLM to rank and generate completions
- `get_suggestions_with_prefix_preservation(query, user_id, limit)`: Main entry point

#### 2. LLMService Enhancement

Added `rank_prefix_completions()` method for intelligent ranking of completion candidates.

#### 3. AutocompleteService Integration

The AutocompleteService automatically detects long queries and uses prefix-preserving mode when appropriate.

## Configuration

### Enable/Disable Feature

In `config.yaml`:

```yaml
autocomplete:
  enable_prefix_preservation: true  # Enable/disable the feature
  
llm:
  enabled: true  # LLM must be enabled for best results
```

### Advanced Configuration

The feature has sensible defaults, but you can customize behavior:

```python
from app.services.prefix_preserving_service import PrefixPreservingService

service = PrefixPreservingService(
    opensearch_service=opensearch,
    llm_service=llm,
    personalization_service=personalization,
    min_tokens_for_prefix_mode=5,    # Minimum tokens to trigger prefix mode
    candidate_limit=20,               # Max candidates from search
    llm_result_limit=10,              # Max results from LLM
    min_incomplete_term_length=1,    # Min length for incomplete term
)
```

## Usage Examples

### Example 1: Basic Usage

```python
from app.services.autocomplete_service import AutocompleteService

# Initialize service (done automatically in main.py)
autocomplete = AutocompleteService(
    opensearch_service=opensearch,
    vector_service=vector,
    llm_service=llm,
    enable_prefix_preservation=True,
)

# Get suggestions
suggestions = autocomplete.get_suggestions(
    query="帮我查询一下今年北京的销",
    user_id="user123",
    limit=5,
)

# Results will preserve the prefix:
# 1. "帮我查询一下今年北京的销售额" (score: 0.95)
# 2. "帮我查询一下今年北京的销量" (score: 0.92)
# 3. "帮我查询一下今年北京的销售情况" (score: 0.88)
```

### Example 2: API Usage

```bash
curl -X POST http://localhost:8000/api/v1/autocomplete \
  -H "Content-Type: application/json" \
  -d '{
    "query": "帮我查询一下今年北京的销",
    "user_id": "user123",
    "limit": 5
  }'
```

Response:

```json
{
  "query": "帮我查询一下今年北京的销",
  "suggestions": [
    {
      "text": "帮我查询一下今年北京的销售额",
      "score": 0.95,
      "source": "prefix_preserved",
      "metadata": {
        "prefix": "帮我查询一下今年北京的",
        "incomplete_term": "销",
        "method": "llm_ranked",
        "completed_term": "销售额"
      }
    },
    {
      "text": "帮我查询一下今年北京的销量",
      "score": 0.92,
      "source": "prefix_preserved",
      "metadata": {
        "prefix": "帮我查询一下今年北京的",
        "incomplete_term": "销",
        "method": "llm_ranked",
        "completed_term": "销量"
      }
    }
  ],
  "total": 2
}
```

### Example 3: Fallback Behavior

If LLM is not available, the system falls back to simple concatenation:

```python
# LLM service unavailable
suggestions = autocomplete.get_suggestions(
    query="帮我查询一下今年北京的销",
    limit=5,
)

# Still returns useful suggestions using fallback method
```

## Behavior Details

### When Prefix Mode is Triggered

Prefix-preserving mode activates when:
1. Query has **≥ 5 tokens** (configurable via `min_tokens_for_prefix_mode`)
2. Last token is **≥ 1 character** (configurable via `min_incomplete_term_length`)
3. Prefix-preserving is enabled in configuration
4. LLM service is available (optional, fallback exists)

### Short Query Behavior

For short queries (< 5 tokens), the system uses regular autocomplete:

```python
# Short query - uses regular autocomplete
suggestions = autocomplete.get_suggestions(
    query="销售",  # Only 1 token
    limit=5,
)
# Returns: various queries containing "销售"
```

### Tokenization

Uses **jieba** for Chinese text segmentation:

```python
"帮我查询一下今年北京的销" 
→ ['帮', '我', '查询', '一下', '今年', '北京', '的', '销']
```

## Performance Considerations

### Caching

LLM completions for popular prefixes can be cached to reduce latency:

```python
# Future enhancement - cache hot completions
cache_key = f"prefix:{prefix}:{incomplete_term}"
```

### Timeout

LLM calls have reasonable timeouts. If LLM times out, the system falls back to rule-based completion.

### Cost

LLM API calls incur cost. Consider:
- Only enabling for queries ≥ 5 tokens
- Caching popular completions
- Rate limiting per user

## Monitoring

### Metrics to Track

```python
# Suggested metrics
metrics = {
    "prefix_mode_trigger_rate": "% of queries using prefix mode",
    "llm_success_rate": "% of successful LLM completions",
    "fallback_rate": "% using fallback method",
    "avg_response_time": "Average completion time",
    "user_selection_rate": "% of suggestions selected by users",
}
```

### Logging

The service logs key events:

```python
logger.info(f"Using prefix-preserving mode for query: {query}")
logger.info(f"Found {len(candidates)} candidates for '{incomplete_term}'")
logger.info(f"LLM ranked {len(results)} prefix completions")
```

## Testing

### Unit Tests

```bash
# Run prefix-preserving service tests
pytest tests/unit/test_prefix_preserving_service.py -v

# Run all tests
pytest tests/unit/ -v
```

### Example Script

```bash
# Run demonstration script
cd /home/runner/work/aibi/aibi
PYTHONPATH=. python examples/prefix_preserving_example.py
```

## Troubleshooting

### Issue: Prefix mode not triggering

**Solution:**
1. Check query has ≥ 5 tokens
2. Verify `enable_prefix_preservation: true` in config
3. Ensure LLM service is available (check logs)

### Issue: LLM returning empty results

**Solution:**
1. Check LLM API key is configured
2. Verify LLM service is available: `llm_service.is_available()`
3. System will automatically fall back to rule-based completion

### Issue: Poor completion quality

**Solution:**
1. Add more diverse examples to OpenSearch index
2. Adjust LLM prompt in `_build_completion_ranking_prompt()`
3. Tune LLM temperature (lower for more deterministic results)

## Future Enhancements

### Planned Features

1. **Caching Layer**: Cache popular prefix completions
2. **Personalization**: Weight completions based on user history
3. **Multi-language Support**: Extend beyond Chinese
4. **A/B Testing**: Framework for testing different strategies
5. **Analytics Dashboard**: Visualize completion metrics

### Configuration Extensions

```yaml
# Future configuration options
prefix_preservation:
  min_tokens: 5
  max_tokens: 20
  cache_ttl: 3600
  enable_personalization: true
  personalization_weight: 0.2
```

## Dependencies

- **jieba** (0.42.1): Chinese text segmentation
- **pydantic**: Data validation
- **OpenSearch**: Candidate search
- **LLM Service**: Intelligent ranking (OpenAI/Anthropic/local)

## API Reference

### PrefixPreservingService

```python
class PrefixPreservingService:
    def __init__(
        self,
        opensearch_service: OpenSearchService,
        llm_service: LLMService,
        personalization_service: Optional[PersonalizationService] = None,
        min_tokens_for_prefix_mode: int = 5,
        candidate_limit: int = 20,
        llm_result_limit: int = 10,
        min_incomplete_term_length: int = 1,
    )
    
    def analyze_input(self, query: str) -> Dict[str, Any]
    def search_completion_candidates(self, incomplete_term: str, limit: int = 20) -> List[str]
    def rank_and_complete(self, prefix: str, incomplete_term: str, candidates: List[str], user_context: Optional[Dict] = None) -> List[Dict[str, Any]]
    def get_suggestions_with_prefix_preservation(self, query: str, user_id: Optional[str] = None, limit: int = 10) -> Optional[List[Suggestion]]
```

### LLMService Extension

```python
class LLMService:
    def rank_prefix_completions(
        self,
        prefix: str,
        incomplete_term: str,
        candidates: List[str],
        user_context: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]
```

## License

This feature is part of the aibi project and follows the same license.

## Contributing

Contributions are welcome! Please:
1. Add tests for new features
2. Update this documentation
3. Follow existing code style
4. Submit PR with clear description

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review example scripts in `examples/`
