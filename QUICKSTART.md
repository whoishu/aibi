# Quick Start Guide

Get the ChatBI Autocomplete Service up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- 4GB RAM

## Steps

### 1. Clone & Setup

```bash
git clone https://github.com/whoishu/aibi.git
cd aibi
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Dependencies

```bash
docker-compose up -d
```

Wait 30 seconds for services to start, then verify:

```bash
curl http://localhost:9200  # OpenSearch should respond
```

### 3. Initialize Data

```bash
python scripts/init_data.py
```

This loads 50+ sample Chinese/English queries. Takes 1-2 minutes on first run (downloads ML model).

### 4. Start Service

```bash
python app/main.py
```

Service starts at http://localhost:8000

### 5. Test It!

Open another terminal and run:

```bash
python scripts/test_api.py
```

Or try manually:

```bash
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","limit":5}'
```

Expected response:
```json
{
  "query": "销售",
  "suggestions": [
    {"text": "销售额", "score": 2.54, "source": "hybrid"},
    {"text": "销售额趋势分析", "score": 2.12, "source": "keyword"},
    ...
  ],
  "total": 5
}
```

## What You Just Built

✅ **Hybrid Search**: Keyword + Vector semantic search  
✅ **Chinese/English Support**: Full multilingual capability  
✅ **Personalization**: User behavior tracking with Redis  
✅ **Real-time Updates**: Add documents via API  
✅ **FastAPI Service**: Modern async Python web framework  

## Next Steps

### Explore the API

Visit http://localhost:8000/docs for interactive API documentation.

### Try Personalization

```bash
# Get suggestions for a user
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","user_id":"user123"}'

# Record their selection
curl -X POST "http://localhost:8000/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","selected_suggestion":"销售额趋势分析","user_id":"user123"}'

# Query again - personalization kicks in!
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","user_id":"user123"}'
```

### Add Your Own Data

```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你的自定义查询",
    "keywords": ["custom", "query", "自定义"],
    "metadata": {"category": "custom"}
  }'
```

### Use the Python Client

```python
from examples.client_example import AutocompleteClient

client = AutocompleteClient()
results = client.get_suggestions("销售", user_id="user123")

for suggestion in results['suggestions']:
    print(f"{suggestion['text']} - {suggestion['score']}")
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Balance between exact matching (keyword) and semantic matching (vector)
autocomplete:
  keyword_weight: 0.7  # Higher = more exact matching
  vector_weight: 0.3   # Higher = more semantic matching
  personalization_weight: 0.2  # Personalization boost
```

Try different weights:
- **More exact**: `keyword_weight: 0.8, vector_weight: 0.2`
- **More semantic**: `keyword_weight: 0.5, vector_weight: 0.5`

## Troubleshooting

**Service won't start?**
```bash
# Check if ports are available
lsof -i :8000 -i :9200 -i :6379

# Check Docker containers
docker-compose ps
```

**No suggestions returned?**
```bash
# Verify data is indexed
curl http://localhost:9200/chatbi_autocomplete/_count

# Re-run initialization if count is 0
python scripts/init_data.py
```

**Slow first request?**
- Normal! Model loads on first request (~30 seconds)
- Subsequent requests are fast (~50-100ms)

## Architecture

```
User Query
    ↓
FastAPI Service
    ↓
AutocompleteService
    ├── Vector Search (semantic)
    ├── Keyword Search (exact)
    └── Personalization (user history)
    ↓
Combined & Ranked Results
    ↓
Response to User
```

## What's Included

```
aibi/
├── app/                    # Main application code
│   ├── api/               # FastAPI endpoints
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Configuration
├── examples/              # Usage examples
├── scripts/               # Utility scripts
├── config.yaml           # Configuration
├── docker-compose.yml    # Dependencies
└── requirements.txt      # Python packages
```

## Learn More

- **Full Documentation**: [README.md](README.md)
- **Setup Guide**: [SETUP.md](SETUP.md)
- **API Reference**: [API.md](API.md)
- **Changes**: [CHANGELOG.md](CHANGELOG.md)

## Need Help?

1. Check the [SETUP.md](SETUP.md) troubleshooting section
2. Verify installation: `python scripts/verify_installation.py`
3. Review logs for errors
4. Open an issue on GitHub

## Production Deployment

Ready for production? See [SETUP.md](SETUP.md) for:
- Security configuration
- Scaling guidelines
- Monitoring setup
- Backup procedures

---

**Congratulations!** You now have a working intelligent autocomplete system! 🎉
