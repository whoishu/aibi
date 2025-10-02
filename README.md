# ChatBI Autocomplete Service

[![CI/CD Pipeline](https://github.com/whoishu/aibi/actions/workflows/ci.yml/badge.svg)](https://github.com/whoishu/aibi/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An intelligent autocomplete service for ChatBI system with hybrid search (keyword + vector), personalization, and continuous learning capabilities.

## Features

- **Hybrid Search**: Combines keyword-based and vector-based search for optimal results
- **Multilingual Support**: Full support for Chinese and English mixed input
- **Personalization**: Learns from user behavior and provides personalized suggestions
- **Real-time Updates**: Supports dynamic data updates for millions of documents
- **FastAPI Framework**: High-performance REST API
- **OpenSearch Backend**: Scalable search engine with KNN vector search
- **Redis-based Tracking**: User behavior tracking and preference learning
- **Web UI Demo**: React + TypeScript frontend for interactive testing

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       v
┌──────────────────────────────────────┐
│         FastAPI Service              │
├──────────────────────────────────────┤
│  • Autocomplete Endpoint             │
│  • Feedback Tracking                 │
│  • Document Management               │
└──────┬───────────────────────────────┘
       │
       v
┌──────────────────────────────────────┐
│    Autocomplete Service              │
├──────────────────────────────────────┤
│  • Query Processing                  │
│  • Result Ranking                    │
│  • Personalization                   │
└──┬───────────┬────────────┬──────────┘
   │           │            │
   v           v            v
┌────────┐  ┌──────┐  ┌─────────────┐
│OpenSearch│  │Vector│  │Personalize  │
│(Hybrid) │  │Model │  │(Redis)      │
└────────┘  └──────┘  └─────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- OpenSearch 2.0+
- Redis 6.0+ (optional, for personalization)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/whoishu/aibi.git
cd aibi
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the service by editing `config.yaml`:
```yaml
opensearch:
  host: "localhost"
  port: 9200
  index_name: "chatbi_autocomplete"

redis:
  host: "localhost"
  port: 6379

autocomplete:
  max_suggestions: 10
  keyword_weight: 0.7
  vector_weight: 0.3
  personalization_weight: 0.2
```

## Quick Start

### 1. Start Dependencies

Start OpenSearch:
```bash
docker run -d -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "plugins.security.disabled=true" \
  opensearchproject/opensearch:2.11.0
```

Start Redis (optional):
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Initialize Sample Data

```bash
python scripts/init_data.py
```

### 3. Start the Service

```bash
python app/main.py
```

Or use uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API

The service will be available at `http://localhost:8000`

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Try the Frontend Demo (Optional)

A React + TypeScript frontend demo is available:

**Option 1: Use the built version (recommended)**
```bash
# Build the frontend
cd frontend
npm install
npm run build
cd ..

# Start the backend
python app/main.py
```

The frontend will be available at `http://localhost:8000/demo`

**Option 2: Run frontend development server**
```bash
# Terminal 1: Start backend
python app/main.py

# Terminal 2: Start frontend dev server
cd frontend
npm run dev
```

Frontend dev server will be available at `http://localhost:3000`

See [frontend/README.md](frontend/README.md) for more details.

## API Usage

### Get Autocomplete Suggestions

```bash
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售",
    "user_id": "user123",
    "limit": 10
  }'
```

Response:
```json
{
  "query": "销售",
  "suggestions": [
    {
      "text": "销售额",
      "score": 2.5432,
      "source": "hybrid",
      "metadata": {
        "keywords": ["sales", "revenue", "销售"],
        "doc_id": "abc123"
      }
    },
    {
      "text": "销售额趋势分析",
      "score": 2.1234,
      "source": "keyword",
      "metadata": {
        "keywords": ["sales", "trend", "analysis"]
      }
    }
  ],
  "total": 2
}
```

### Submit User Feedback

```bash
curl -X POST "http://localhost:8000/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售",
    "selected_suggestion": "销售额趋势分析",
    "user_id": "user123"
  }'
```

### Add Documents

Single document:
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "客户满意度调查",
    "keywords": ["customer", "satisfaction", "survey"],
    "metadata": {"category": "customer"}
  }'
```

Bulk documents:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "text": "市场占有率分析",
        "keywords": ["market", "share"]
      },
      {
        "text": "品牌知名度调研",
        "keywords": ["brand", "awareness"]
      }
    ]
  }'
```

### Health Check

```bash
curl "http://localhost:8000/api/v1/health"
```

## Configuration

### Search Weights

Adjust the balance between keyword and vector search:

- `keyword_weight`: Weight for keyword-based search (0-1)
- `vector_weight`: Weight for vector-based search (0-1)
- `personalization_weight`: Boost factor for personalized results (0-1)

Higher keyword weight prioritizes exact matches and prefix matching.
Higher vector weight prioritizes semantic similarity.

### Personalization

Enable/disable personalization in `config.yaml`:

```yaml
autocomplete:
  enable_personalization: true
  personalization_weight: 0.2
```

Personalization learns from:
- User's historical selections
- Query-specific preferences
- Global popularity trends

## Development

### Project Structure

```
aibi/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── autocomplete_service.py
│   │   ├── opensearch_service.py
│   │   ├── vector_service.py
│   │   └── personalization_service.py
│   └── utils/
│       ├── __init__.py
│       └── config.py           # Configuration management
├── frontend/                   # React + TypeScript UI
│   ├── src/
│   │   ├── components/
│   │   │   └── Autocomplete.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py            # Test fixtures
├── scripts/
│   └── init_data.py            # Sample data initialization
├── config.yaml                 # Configuration file
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── Makefile                    # Development commands
└── README.md
```

### Development Setup

For development, install development dependencies:
```bash
pip install -r requirements-dev.txt
make install-dev  # Also installs pre-commit hooks
```

### Code Quality Tools

We use several tools to maintain code quality:

- **Black**: Code formatter
- **isort**: Import organizer
- **Flake8**: Style checker
- **MyPy**: Type checker
- **pytest**: Testing framework
- **pre-commit**: Git hooks

Run quality checks:
```bash
make lint        # Run all linters
make format      # Format code
make test        # Run tests
make coverage    # Generate coverage report
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

### Adding New Features

1. **Custom Vector Models**: Change the model in `config.yaml`:
```yaml
vector_model:
  model_name: "your-model-name"
  dimension: 768
```

2. **Custom Analyzers**: Modify the index settings in `opensearch_service.py`

3. **Additional Ranking Factors**: Extend the scoring logic in `autocomplete_service.py`

## Performance Considerations

- **Index Size**: Tested with up to 10 million documents
- **Query Latency**: Typically < 100ms for hybrid search
- **Vector Model**: Uses lightweight multilingual model (384 dimensions)
- **Caching**: Redis caches user preferences for fast lookups
- **Bulk Operations**: Use bulk API for inserting large datasets

## Best Practices

1. **Initialize with Quality Data**: Provide comprehensive keyword mappings
2. **Monitor User Feedback**: Track selection rates to improve rankings
3. **Regular Index Optimization**: Periodically rebuild index for better performance
4. **Balance Weights**: Fine-tune keyword/vector weights based on your use case
5. **Enable Personalization**: Significantly improves user experience over time

## Troubleshooting

### OpenSearch Connection Failed

- Verify OpenSearch is running: `curl http://localhost:9200`
- Check configuration in `config.yaml`
- Ensure network connectivity

### Vector Model Loading Slow

- First-time model download can take several minutes
- Model is cached locally after first load
- Consider using a smaller model for faster startup

### Redis Connection Issues

- Service works without Redis (personalization disabled)
- Check Redis is running: `redis-cli ping`
- Verify Redis configuration in `config.yaml`

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Development setup
- Code quality standards
- Testing requirements
- Pull request process
- CI/CD pipeline

## License

MIT License
