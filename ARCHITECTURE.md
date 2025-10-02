# System Architecture

## Overview

The ChatBI Autocomplete Service is designed as a modular, scalable system with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Client Layer                        │
│  (Web UI, Mobile App, CLI, API Consumers)               │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (Future)                  │
│         (Rate Limiting, Authentication, CORS)            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Application                    │
├─────────────────────────────────────────────────────────┤
│  Routes Layer (app/api/routes.py)                       │
│  - /autocomplete     - /feedback                         │
│  - /documents        - /health                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            AutocompleteService (Orchestrator)            │
├─────────────────────────────────────────────────────────┤
│  • Query Processing & Expansion                          │
│  • Result Ranking & Scoring                              │
│  • Feedback Recording                                    │
│  • Document Management                                   │
└───┬──────────────┬──────────────┬──────────┬─────┬──────┘
    │              │              │          │     │
    ▼              ▼              ▼          ▼     ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌────────┐
│OpenSearch│  │  Vector  │  │Personal- │  │  LLM  │  │ Config │
│ Service  │  │ Service  │  │ization   │  │Service│  │Manager │
└────┬────┘  └────┬─────┘  └────┬─────┘  └───┬───┘  └────────┘
     │            │              │            │
     ▼            ▼              ▼            ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
│OpenSearch│  │Sentence  │  │  Redis   │  │OpenAI/     │
│ (Index)  │  │Transform │  │(Cache)   │  │Anthropic   │
└──────────┘  └──────────┘  └──────────┘  └────────────┘
```

## Component Details

### 1. API Layer (app/api/)

**Responsibility**: HTTP interface, request validation, response formatting

**Components**:
- `routes.py`: FastAPI endpoints
  - Request handling
  - Input validation (Pydantic)
  - Response serialization
  - Error handling

**Key Features**:
- RESTful design
- Automatic OpenAPI/Swagger documentation
- CORS support
- Async/await for concurrency

### 2. Service Layer (app/services/)

#### 2.1 AutocompleteService (Orchestrator)

**Responsibility**: Main business logic, coordinates all services

**Key Methods**:
```python
get_suggestions(query, user_id, limit, min_score)
  ├─> Generate query vector (VectorService)
  ├─> Perform hybrid search (OpenSearchService)
  ├─> Apply personalization (PersonalizationService)
  └─> Format and return results

record_feedback(query, selected, user_id)
  └─> Track selection (PersonalizationService)

add_document(text, keywords, metadata)
  ├─> Generate vector (VectorService)
  └─> Index document (OpenSearchService)
```

#### 2.2 OpenSearchService

**Responsibility**: Search engine operations

**Features**:
- **Keyword Search**:
  - Phrase prefix matching (for autocomplete)
  - Fuzzy matching (typo tolerance)
  - Term matching on keywords
  
- **Vector Search**:
  - KNN (k-nearest neighbors) search
  - Cosine similarity
  
- **Hybrid Search**:
  - Combines keyword + vector scores
  - Configurable weights
  - Result deduplication

**Index Schema**:
```json
{
  "text": {type: "text", with completion},
  "keywords": {type: "keyword"},
  "vector": {type: "knn_vector", dimension: 384},
  "metadata": {type: "object"},
  "frequency": {type: "integer"},
  "created_at": {type: "date"},
  "updated_at": {type: "date"}
}
```

#### 2.3 VectorService

**Responsibility**: Vector embedding generation

**Implementation**:
- Uses Sentence Transformers
- Model: `paraphrase-multilingual-MiniLM-L12-v2`
- Dimension: 384
- Supports batch encoding

**Features**:
- Lazy model loading
- Caching (in-memory)
- Multilingual support

#### 2.4 PersonalizationService

**Responsibility**: User behavior tracking and personalization

**Data Structures** (Redis):
```
user:{user_id}:history        → List[{query, selected, timestamp}]
user:{user_id}:query:{query}  → String (most recent selection)
user:{user_id}:freq           → Sorted Set (frequency scores)
global:query:{query}          → Sorted Set (global popularity)
```

**Features**:
- Historical selection tracking
- Query-specific preferences
- Frequency-based boosting
- TTL-based expiration

#### 2.5 LLMService (Optional)

**Responsibility**: LLM-powered query understanding and enhancement

**Supported Providers**:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Local models (future)

**Features**:
- **Query Expansion**: Generates semantically related search terms
- **Related Query Generation**: Suggests intelligent follow-up queries
- **Query Rewriting**: Optimizes queries for better search results
- **Context-Aware**: Considers user history and domain

**Integration Points**:
- Autocomplete: Expands queries for broader coverage
- Related Queries: Adds LLM-generated suggestions with high priority
- Graceful Fallback: System works without LLM if unavailable

### 3. Model Layer (app/models/)

**Responsibility**: Data validation and serialization

**Models**:
- `AutocompleteRequest`: Input validation
- `AutocompleteResponse`: Output format
- `Suggestion`: Single result
- `FeedbackRequest`: User feedback
- `DocumentRequest`: Document input

### 4. Configuration Layer (app/utils/)

**Responsibility**: Configuration management

**Features**:
- YAML-based config
- Environment variable support
- Type-safe configuration (Pydantic)
- Default values

## Data Flow

### Autocomplete Request Flow

```
1. User Input: "销售"
   ↓
2. API Layer: Validate request
   ↓
3. AutocompleteService: Process query
   │
   ├─> 3a. VectorService: Generate embedding
   │   └─> [0.123, -0.456, ...] (384 dimensions)
   │
   ├─> 3b. OpenSearchService: Hybrid search
   │   ├─> Keyword search: "销售" → ["销售额", "销售额趋势"]
   │   ├─> Vector search: semantic → ["营销", "推广"]
   │   └─> Combine with weights (0.7 keyword + 0.3 vector)
   │
   └─> 3c. PersonalizationService: Apply boost
       └─> Check user history → Boost "销售额趋势分析"
   ↓
4. Rank & Format: Sort by final score
   ↓
5. Return: Top N suggestions
```

### Feedback Recording Flow

```
1. User Selection: "销售额趋势分析"
   ↓
2. API Layer: Validate feedback
   ↓
3. AutocompleteService: Record feedback
   ↓
4. PersonalizationService: Update Redis
   ├─> user:{id}:history ← Add entry
   ├─> user:{id}:query:销售 ← Update preference
   ├─> user:{id}:freq ← Increment score
   └─> global:query:销售 ← Global tracking
   ↓
5. Return: Success
```

### Document Indexing Flow

```
1. New Document: "市场份额分析"
   ↓
2. API Layer: Validate document
   ↓
3. AutocompleteService: Process document
   │
   ├─> 3a. VectorService: Generate embedding
   │   └─> [0.789, -0.234, ...] (384 dimensions)
   │
   └─> 3b. OpenSearchService: Index
       ├─> Create document ID (if not provided)
       ├─> Prepare document with vector
       └─> Index in OpenSearch
   ↓
4. Return: Success
```

## Scalability Considerations

### Horizontal Scaling

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ API Pod 1│  │ API Pod 2│  │ API Pod 3│
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
         ┌──────────▼──────────┐
         │   Load Balancer     │
         └──────────┬──────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│OpenSearch│  │OpenSearch│  │OpenSearch│
│  Node 1  │  │  Node 2  │  │  Node 3  │
└──────────┘  └──────────┘  └──────────┘
```

**Stateless Design**:
- API instances share no state
- All state in OpenSearch/Redis
- Can scale horizontally

### Vertical Optimization

**Caching Layers**:
1. In-memory cache for hot queries
2. Redis for user preferences
3. OpenSearch for search results

**Performance Targets**:
- Query latency: < 100ms (p95)
- Throughput: 1000+ QPS per instance
- Index size: Up to 10M documents

## Security Architecture

### Current

```
Client → [CORS] → FastAPI → Services → Datastores
```

### Recommended for Production

```
Client → [TLS] → API Gateway → [Auth] → FastAPI
                    ↓
              [Rate Limit]
              [API Key Validation]
              [Request Logging]
```

**Security Measures**:
- HTTPS/TLS encryption
- API authentication (JWT/OAuth2)
- Rate limiting per user
- Input sanitization
- Audit logging

## Monitoring & Observability

### Metrics to Track

**Service Metrics**:
- Request rate (QPS)
- Response latency (p50, p95, p99)
- Error rate
- Cache hit rate

**Search Metrics**:
- Query types (keyword/vector/hybrid)
- Average result count
- Zero-result rate
- Search latency

**Personalization Metrics**:
- Feedback rate
- User engagement
- Preference accuracy

### Logging

**Log Levels**:
- ERROR: Service failures
- WARNING: Degraded performance
- INFO: Request/response logs
- DEBUG: Detailed tracing

**Structured Logging**:
```json
{
  "timestamp": "2024-10-01T12:00:00Z",
  "level": "INFO",
  "service": "autocomplete",
  "operation": "search",
  "user_id": "user123",
  "query": "销售",
  "results": 5,
  "latency_ms": 87
}
```

## Future Enhancements

### Planned Features

1. **Advanced Caching**:
   - Multi-level cache
   - Cache warming
   - Predictive caching

2. **Query Analysis**:
   - Intent detection
   - Query expansion
   - Typo correction

3. **ML Enhancements**:
   - Learning-to-rank
   - A/B testing framework
   - Custom models

4. **Real-time Updates**:
   - WebSocket support
   - Streaming results
   - Live personalization

### Architectural Evolution

```
Current: Monolithic Service
    ↓
Next: Microservices
    ├─> Search Service
    ├─> Personalization Service
    ├─> Analytics Service
    └─> Admin Service
```

## Technology Stack

### Core Technologies

- **Python 3.8+**: Main language
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Storage & Search

- **OpenSearch**: Search engine
- **Redis**: User preferences
- **Sentence Transformers**: Vector embeddings

### DevOps

- **Docker**: Containerization
- **Docker Compose**: Local development
- **Git**: Version control

## Development Workflow

```
┌──────────────┐
│ Local Dev    │ → Code → Commit → PR
└──────────────┘
       ↓
┌──────────────┐
│ CI/CD        │ → Test → Build → Deploy
└──────────────┘
       ↓
┌──────────────┐
│ Production   │ → Monitor → Alert → Improve
└──────────────┘
```

## Deployment Patterns

### Development
```
docker-compose up -d
python app/main.py
```

### Staging
```
docker build -t autocomplete:staging .
docker run -p 8000:8000 autocomplete:staging
```

### Production
```
Kubernetes Deployment
├─> Pods: 3+ replicas
├─> Service: Load balancer
├─> HPA: Auto-scaling
└─> Monitoring: Prometheus + Grafana
```
