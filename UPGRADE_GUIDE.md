# Upgrade Guide: LLM Integration

## Overview

This guide helps you upgrade your ChatBI Autocomplete Service to use the new LLM-enhanced features for improved recommendations.

## What's New

Version 1.1.0 adds optional LLM (Large Language Model) integration:

- **Query Expansion**: Automatically finds related search terms
- **Smart Related Queries**: Context-aware follow-up suggestions
- **Better Intent Understanding**: Natural language processing
- **Improved Recommendations**: Higher quality suggestions

## Is This Right For You?

### ✅ Consider Using LLM If:
- You want the highest quality recommendations
- Users make complex or conversational queries
- You need better semantic understanding
- Budget allows for API costs (~$0.001-0.01 per query)
- Latency increase of 200-1000ms is acceptable

### ❌ Skip LLM If:
- You need ultra-low latency (< 100ms)
- Existing recommendations are sufficient
- Budget is very tight
- You can't access external APIs

## Upgrade Steps

### Step 1: Update Code

```bash
# Pull latest changes
git pull origin main

# Or if using the feature branch
git checkout copilot/fix-21c40bda-9da1-44c5-9438-76c346c4a86f
```

### Step 2: Install Dependencies (Optional)

Only needed if you want to enable LLM:

```bash
# For OpenAI (recommended)
pip install openai>=1.0.0

# Or for Anthropic
pip install anthropic>=0.18.0
```

### Step 3: Configure

#### Option A: Use Without LLM (Default)

No changes needed! The system works exactly as before.

#### Option B: Enable LLM

1. **Get an API Key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY="sk-..."
   # Or
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Update config.yaml**:
   ```yaml
   llm:
     enabled: true  # Changed from false
     provider: "openai"  # or "anthropic"
     model: "gpt-3.5-turbo"  # or "claude-3-haiku-20240307"
     temperature: 0.7
     max_tokens: 150
   ```

### Step 4: Verify

Run the verification script:

```bash
python scripts/verify_llm_integration.py
```

You should see:
```
✓ ALL CHECKS PASSED
```

### Step 5: Restart Service

```bash
# If running directly
python app/main.py

# If using uvicorn
uvicorn app.main:app --reload

# If using Docker
docker-compose restart
```

Check the logs for:
```
LLM service initialized with openai/gpt-3.5-turbo
```

## Verification

### Test Without LLM (Baseline)

```bash
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{"query": "销售", "limit": 5}'
```

### Test With LLM (Enhanced)

After enabling LLM, the same request will:
1. Expand the query with related terms
2. Search all variants
3. Return more comprehensive results

Check the response for:
- More diverse suggestions
- Better semantic matches
- Source indicators (some may be "llm")

### Test Related Queries

```bash
curl -X POST "http://localhost:8000/api/v1/related-queries" \
  -H "Content-Type: application/json" \
  -d '{"query": "市场趋势", "limit": 10}'
```

With LLM enabled, you'll see:
- Intelligent follow-up questions
- Context-aware suggestions
- Higher quality related queries

## Performance Tuning

### Reduce Latency

If LLM adds too much latency:

1. **Use Faster Model**:
   ```yaml
   llm:
     model: "gpt-3.5-turbo"  # Faster than GPT-4
   ```

2. **Reduce Max Tokens**:
   ```yaml
   llm:
     max_tokens: 100  # Less than default 150
   ```

3. **Implement Caching** (Future):
   Cache common queries in Redis

### Reduce Costs

1. **Use Cheaper Model**:
   - GPT-3.5-turbo: ~$0.001/query
   - GPT-4: ~$0.01/query
   - Claude Haiku: ~$0.0005/query

2. **Set Budget Alerts**:
   Configure in your provider's console

3. **Monitor Usage**:
   Track API calls in application logs

## Monitoring

### Check LLM Status

```bash
curl "http://localhost:8000/api/v1/health"
```

Look for LLM status in health endpoint.

### View Logs

```bash
# Check if LLM is enabled
grep "LLM service initialized" logs/app.log

# Check LLM usage
grep "LLM expanded query" logs/app.log
grep "LLM generated.*related queries" logs/app.log
```

### Track Metrics

Monitor these metrics:
- API call count to LLM provider
- Average latency with/without LLM
- Cache hit rate (if implemented)
- User satisfaction scores

## Troubleshooting

### LLM Not Available

**Problem**: Logs show "LLM service not available"

**Solutions**:
1. Check API key is set: `echo $OPENAI_API_KEY`
2. Verify key is valid: Test directly with provider
3. Check network connectivity
4. Ensure package is installed: `pip list | grep openai`

### High Latency

**Problem**: Requests taking > 2 seconds

**Solutions**:
1. Switch to faster model (gpt-3.5-turbo)
2. Reduce max_tokens
3. Check network latency to API
4. Consider disabling LLM for real-time use cases

### Unexpected Results

**Problem**: LLM suggestions not relevant

**Solutions**:
1. Adjust temperature (lower = more focused)
2. Try different model
3. Check prompts in LLMService code
4. Provide better context (user history)

### API Errors

**Problem**: Rate limits or API errors

**Solutions**:
1. Check API quota/limits
2. Implement exponential backoff
3. Upgrade API tier
4. Consider local models

## Rollback

If you need to rollback:

### Disable LLM

```yaml
# config.yaml
llm:
  enabled: false  # Disable
```

Restart service. System works exactly as before.

### Uninstall (Optional)

```bash
pip uninstall openai anthropic
```

## Migration Checklist

- [ ] Backup current configuration
- [ ] Pull latest code
- [ ] Install dependencies (optional)
- [ ] Configure LLM (optional)
- [ ] Run verification script
- [ ] Test with sample queries
- [ ] Monitor performance
- [ ] Check API usage
- [ ] Update documentation
- [ ] Train team on new features

## Best Practices

### 1. Start Small
- Enable LLM for 10% of traffic
- Monitor metrics
- Gradually increase if successful

### 2. Monitor Closely
- Track latency impact
- Watch API costs
- Measure recommendation quality

### 3. Have Fallbacks
- System works without LLM
- Graceful degradation on errors
- Cache common queries

### 4. Optimize Prompts
- Test different temperatures
- Adjust max_tokens
- Refine system prompts

### 5. Consider Privacy
- Don't send sensitive data
- Use local models if needed
- Review provider policies

## Support

### Documentation
- [LLM_INTEGRATION.md](LLM_INTEGRATION.md) - Detailed guide
- [CHANGELOG_LLM.md](CHANGELOG_LLM.md) - Full changelog
- [README.md](README.md) - Main documentation

### Examples
- `examples/llm_integration_example.py` - Usage examples
- `scripts/verify_llm_integration.py` - Verification

### Getting Help
1. Check logs for error messages
2. Run verification script
3. Review documentation
4. Open GitHub issue

## FAQ

**Q: Do I need to upgrade?**  
A: No, it's optional. Existing features work unchanged.

**Q: Will it break my current setup?**  
A: No, LLM is disabled by default and fully backward compatible.

**Q: How much does it cost?**  
A: ~$0.001-0.01 per query depending on model. You control usage.

**Q: Can I use it without internet?**  
A: Not yet, but local model support is planned.

**Q: Is my data sent to OpenAI/Anthropic?**  
A: Only queries if enabled. No user data by default.

**Q: Can I disable it later?**  
A: Yes, set `enabled: false` in config.yaml.

**Q: Does it require training?**  
A: No, works out of the box with pre-trained models.

**Q: Can I customize the prompts?**  
A: Yes, edit `app/services/llm_service.py` methods.

## Next Steps

After upgrading:

1. **Measure Impact**:
   - Compare recommendation quality
   - Track user engagement
   - Monitor API costs

2. **Optimize**:
   - Fine-tune temperature
   - Adjust prompts
   - Implement caching

3. **Expand**:
   - Try different models
   - Add more context
   - Customize for your domain

4. **Share Feedback**:
   - Report issues
   - Suggest improvements
   - Share your results

## Conclusion

The LLM integration provides powerful enhancements while maintaining system stability and backward compatibility. You can enable it when ready, and disable it anytime without issues.

**Start simple, measure impact, optimize, and scale!**
