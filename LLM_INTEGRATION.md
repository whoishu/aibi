# LLM Integration Guide

## Overview

The ChatBI Autocomplete Service now supports optional LLM (Large Language Model) integration to enhance recommendation quality. When enabled, the LLM service provides:

1. **Query Expansion**: Automatically expands user queries with semantically related terms
2. **Related Query Generation**: Generates intelligent follow-up queries based on context
3. **Query Understanding**: Better understands user intent for improved search results

## Benefits

### Improved Recommendation Quality
- **Smarter Query Understanding**: LLMs understand user intent beyond keyword matching
- **Contextual Suggestions**: Generates queries based on conversation flow and user history
- **Semantic Expansion**: Discovers related queries that traditional methods might miss
- **Domain Awareness**: Can be fine-tuned for business intelligence terminology

### Enhanced User Experience
- **Natural Language Support**: Better handling of conversational queries
- **Follow-up Questions**: Suggests logical next steps in data exploration
- **Personalized Context**: Considers user history for more relevant suggestions

## Supported Providers

### 1. OpenAI
- **Models**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Setup**: Requires OpenAI API key
- **Cost**: Pay-per-use pricing

### 2. Anthropic
- **Models**: Claude-3-opus, Claude-3-sonnet, Claude-3-haiku
- **Setup**: Requires Anthropic API key
- **Cost**: Pay-per-use pricing

### 3. Local Models (Future)
- Self-hosted open-source models
- No API costs
- Requires local GPU/CPU resources

## Configuration

### 1. Enable LLM in config.yaml

```yaml
llm:
  enabled: true  # Enable LLM features
  provider: "openai"  # Options: "openai", "anthropic", "local"
  model: "gpt-3.5-turbo"  # Model to use
  temperature: 0.7  # Creativity level (0-1)
  max_tokens: 150  # Maximum response length
```

### 2. Set API Key

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option B: Configuration File**
```yaml
llm:
  enabled: true
  provider: "openai"
  api_key: "sk-..."  # Not recommended for production
```

### 3. Install Required Dependencies

For OpenAI:
```bash
pip install openai>=1.0.0
```

For Anthropic:
```bash
pip install anthropic>=0.18.0
```

## How It Works

### Query Expansion in Autocomplete

When a user types a query, the system:

1. **Original Search**: Performs standard hybrid search with the original query
2. **LLM Expansion**: Uses LLM to generate 2-3 related search terms
3. **Expanded Search**: Searches with expanded terms as well
4. **Merge Results**: Combines and deduplicates results
5. **Rank**: Applies scoring with original query results boosted

Example:
```
User Query: "销售"
LLM Expands: ["营业额", "收入分析"]
Combined Results: Results from all three queries, ranked by relevance
```

### Related Query Generation

When requesting related queries:

1. **Context Building**: Gathers user history and domain information
2. **LLM Generation**: Asks LLM to suggest logical follow-up queries
3. **Priority Scoring**: LLM suggestions get highest priority scores (0.9-0.95)
4. **Integration**: Combined with sequence-based and hybrid search results

Example:
```
User Query: "市场趋势"
Context: User previously searched "销售分析"
LLM Suggests:
  - "竞争对手分析"
  - "市场份额变化"
  - "未来预测模型"
```

## API Impact

### Autocomplete Endpoint

The `/api/v1/autocomplete` endpoint behavior:
- **Without LLM**: Standard hybrid search (keyword + vector)
- **With LLM**: Enhanced with query expansion for broader coverage

Response includes source information:
```json
{
  "suggestions": [
    {
      "text": "销售额趋势",
      "score": 0.92,
      "source": "hybrid"
    }
  ]
}
```

### Related Queries Endpoint

The `/api/v1/related-queries` endpoint behavior:
- **Without LLM**: Sequence-based + hybrid search + history
- **With LLM**: Additional intelligent suggestions with highest priority

Response indicates LLM-generated queries:
```json
{
  "related_queries": [
    {
      "text": "竞争对手分析",
      "score": 0.95,
      "source": "llm",
      "metadata": {
        "llm_generated": true,
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo"
      }
    }
  ]
}
```

## Performance Considerations

### Latency
- **LLM API Calls**: Add 200-1000ms latency per request
- **Mitigation**: 
  - Only used for non-trivial queries (length > 3)
  - Can be disabled for real-time requirements
  - Results are still returned if LLM is slow

### Cost
- **OpenAI GPT-3.5-turbo**: ~$0.001 per query expansion
- **OpenAI GPT-4**: ~$0.01 per query expansion
- **Recommendation**: Start with GPT-3.5-turbo, upgrade if needed

### Caching
- Consider caching LLM responses for common queries
- Implement in PersonalizationService using Redis
- Can reduce costs by 70-90% for popular queries

## Best Practices

### 1. Start with GPT-3.5-turbo
- Good balance of cost and quality
- Upgrade to GPT-4 only if needed

### 2. Monitor API Usage
- Track number of LLM calls
- Set budget alerts in provider console
- Consider rate limiting

### 3. Implement Fallbacks
- System gracefully disables LLM if unavailable
- All features work without LLM
- Log warnings for troubleshooting

### 4. Optimize Prompts
- Keep prompts concise
- Include relevant context only
- Test different temperature settings

### 5. Consider Privacy
- Don't send sensitive user data to external LLMs
- Use local models for sensitive environments
- Review provider's data retention policies

## Testing

### Unit Tests

Test LLM service independently:
```python
from app.services.llm_service import LLMService

# Test with mock responses
llm = LLMService(provider="openai", model="gpt-3.5-turbo")
expanded = llm.expand_query("销售")
assert len(expanded) > 0
```

### Integration Tests

Test full flow:
```python
# Test autocomplete with LLM
response = client.post("/api/v1/autocomplete", json={
    "query": "销售",
    "user_id": "test_user",
    "limit": 10
})
assert response.status_code == 200
```

## Troubleshooting

### LLM Service Not Available
**Symptom**: Log shows "LLM service not available"

**Solutions**:
1. Check API key is set correctly
2. Verify provider package is installed
3. Test API key directly with provider SDK
4. Check network connectivity

### High Latency
**Symptom**: Requests taking > 2 seconds

**Solutions**:
1. Use faster model (e.g., GPT-3.5-turbo instead of GPT-4)
2. Reduce max_tokens limit
3. Implement caching for common queries
4. Consider disabling for real-time use cases

### Unexpected Results
**Symptom**: LLM suggestions not relevant

**Solutions**:
1. Adjust temperature (lower = more focused)
2. Improve prompts with better context
3. Try different model
4. Add domain-specific instructions

### API Rate Limits
**Symptom**: "Rate limit exceeded" errors

**Solutions**:
1. Implement request throttling
2. Cache results aggressively
3. Upgrade API tier with provider
4. Use local models

## Examples

### Basic Setup

```python
# In your application
from app.services.llm_service import LLMService

llm = LLMService(
    provider="openai",
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Expand a query
expanded = llm.expand_query("销售分析")
# Returns: ["营业额分析", "收入趋势", "销售业绩", ...]

# Generate related queries
related = llm.generate_related_queries(
    query="市场趋势",
    limit=5,
    context={"domain": "business_intelligence"}
)
```

### With Context

```python
# Include user history for better suggestions
context = {
    "user_history": ["销售分析", "客户满意度"],
    "domain": "business_intelligence"
}

related = llm.generate_related_queries(
    query="市场趋势",
    limit=5,
    context=context
)
# Returns contextually relevant queries based on user's journey
```

## Future Enhancements

### Planned Features
1. **Query Intent Classification**: Classify queries into types (analytical, exploratory, etc.)
2. **Contextual Memory**: Maintain conversation context across queries
3. **Multi-turn Dialogue**: Support follow-up questions
4. **Custom Prompts**: Allow domain-specific prompt templates
5. **Local Model Support**: Integration with open-source models
6. **Response Caching**: Redis-based caching for common queries
7. **A/B Testing**: Framework to compare LLM vs non-LLM results

### Research Areas
- Fine-tuning models on business intelligence queries
- RAG (Retrieval-Augmented Generation) integration
- Multi-modal search (text + charts + tables)
- Streaming responses for real-time feedback

## References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
- [LangChain for LLM Applications](https://langchain.com)
- [Prompt Engineering Guide](https://www.promptingguide.ai)

## Support

For questions or issues:
1. Check logs for error messages
2. Verify configuration settings
3. Test API keys independently
4. Open an issue on GitHub with logs and configuration (redact API keys)
