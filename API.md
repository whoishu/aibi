# API Documentation

Complete API reference for the ChatBI Autocomplete Service.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the service does not require authentication. For production deployment, consider adding API key or OAuth2 authentication.

## Endpoints

### Overview

The service provides several types of query assistance:

- **Autocomplete**: Suggests completions as users type
- **Similar Queries**: Returns queries that are semantically similar (using vector similarity)
- **Related Queries**: Returns queries that are contextually related (using hybrid search and user history)

The key differences:
- **Similar queries** focus on semantic similarity (e.g., "销售分析" → "销售数据分析", "销售趋势分析")
- **Related queries** include broader context, user history, and trending queries (e.g., "销售报告" → "市场分析", "业绩统计")

### 1. Get Autocomplete Suggestions

Get autocomplete suggestions for a user query.

**Endpoint**: `POST /autocomplete`

**Request Body**:
```json
{
  "query": "销售",
  "user_id": "user123",
  "limit": 10,
  "context": {}
}
```

**Parameters**:
- `query` (string, required): User input text (supports Chinese and English)
- `user_id` (string, optional): User ID for personalized suggestions
- `limit` (integer, optional): Maximum number of suggestions (1-50, default: 10)
- `context` (object, optional): Additional context information

**Response** (200 OK):
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
        "keywords": ["sales", "trend", "analysis"],
        "doc_id": "def456"
      }
    }
  ],
  "total": 2
}
```

**Response Fields**:
- `query`: Original query
- `suggestions`: Array of suggestions
  - `text`: Suggestion text
  - `score`: Relevance score (higher is better)
  - `source`: Source type (`keyword`, `vector`, `hybrid`, `personalized`)
  - `metadata`: Additional information
- `total`: Total number of suggestions returned

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售",
    "user_id": "user123",
    "limit": 5
  }'
```

---

### 2. Submit User Feedback

Record user's selection to improve future suggestions.

**Endpoint**: `POST /feedback`

**Request Body**:
```json
{
  "query": "销售",
  "selected_suggestion": "销售额趋势分析",
  "user_id": "user123",
  "timestamp": "2024-10-01T12:00:00Z"
}
```

**Parameters**:
- `query` (string, required): Original query
- `selected_suggestion` (string, required): The suggestion user selected
- `user_id` (string, optional): User ID
- `timestamp` (string, optional): ISO 8601 timestamp

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Feedback recorded"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售",
    "selected_suggestion": "销售额趋势分析",
    "user_id": "user123"
  }'
```

---

### 3. Add Single Document

Add a document to the autocomplete index.

**Endpoint**: `POST /documents`

**Request Body**:
```json
{
  "text": "客户满意度调查",
  "doc_id": "custom-id-123",
  "keywords": ["customer", "satisfaction", "survey", "客户", "满意度"],
  "metadata": {
    "category": "customer",
    "priority": "high"
  }
}
```

**Parameters**:
- `text` (string, required): Document text to be searchable
- `doc_id` (string, optional): Custom document ID (auto-generated if not provided)
- `keywords` (array, optional): Associated keywords for better matching
- `metadata` (object, optional): Additional metadata

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Document added"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "客户满意度调查",
    "keywords": ["customer", "satisfaction"],
    "metadata": {"category": "survey"}
  }'
```

---

### 4. Add Multiple Documents (Bulk)

Add multiple documents in a single request.

**Endpoint**: `POST /documents/bulk`

**Request Body**:
```json
{
  "documents": [
    {
      "text": "市场占有率分析",
      "keywords": ["market", "share", "analysis"]
    },
    {
      "text": "品牌知名度调研",
      "keywords": ["brand", "awareness", "research"]
    },
    {
      "text": "竞争对手分析",
      "keywords": ["competitor", "analysis"],
      "metadata": {"type": "analysis"}
    }
  ]
}
```

**Parameters**:
- `documents` (array, required): Array of document objects
  - Each document has same structure as single document endpoint

**Response** (200 OK):
```json
{
  "success": 3,
  "errors": 0,
  "message": "Added 3 documents with 0 errors"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"text": "销售数据分析", "keywords": ["sales", "data"]},
      {"text": "用户行为分析", "keywords": ["user", "behavior"]}
    ]
  }'
```

---

### 5. Health Check

Check service health and dependency status.

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "opensearch_connected": true,
  "redis_connected": true
}
```

**Response Fields**:
- `status`: Overall service status (`healthy`, `degraded`)
- `opensearch_connected`: OpenSearch connection status
- `redis_connected`: Redis connection status

**Example**:
```bash
curl "http://localhost:8000/api/v1/health"
```

---

### 6. Get Similar Queries

Get semantically similar queries for a user input query.

**Endpoint**: `POST /similar-queries`

**Request Body**:
```json
{
  "query": "销售分析",
  "user_id": "user123",
  "limit": 10
}
```

**Parameters**:
- `query` (string, required): User input query
- `user_id` (string, optional): User ID for personalization
- `limit` (integer, optional): Maximum number of similar queries (1-50, default: 10)

**Response** (200 OK):
```json
{
  "query": "销售分析",
  "similar_queries": [
    {
      "text": "销售数据分析",
      "score": 0.9234,
      "source": "vector",
      "metadata": {
        "keywords": ["sales", "data", "analysis"],
        "doc_id": "xyz789"
      }
    },
    {
      "text": "销售趋势报告",
      "score": 0.8756,
      "source": "vector",
      "metadata": {
        "keywords": ["sales", "trend", "report"],
        "doc_id": "abc456"
      }
    }
  ],
  "total": 2
}
```

**Response Fields**:
- `query`: Original query
- `similar_queries`: Array of similar queries
  - `text`: Query text
  - `score`: Similarity score (0-1, higher is more similar)
  - `source`: Source type (`vector`, `personalized`)
  - `metadata`: Additional information
- `total`: Total number of similar queries returned

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/similar-queries" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售分析",
    "user_id": "user123",
    "limit": 5
  }'
```

---

### 7. Get Related Queries

Get contextually related queries for a user input query.

**Endpoint**: `POST /related-queries`

**Request Body**:
```json
{
  "query": "销售报告",
  "user_id": "user123",
  "limit": 10
}
```

**Parameters**:
- `query` (string, required): User input query
- `user_id` (string, optional): User ID for personalization
- `limit` (integer, optional): Maximum number of related queries (1-50, default: 10)

**Response** (200 OK):
```json
{
  "query": "销售报告",
  "related_queries": [
    {
      "text": "市场分析报告",
      "score": 0.8543,
      "source": "hybrid",
      "metadata": {
        "keywords": ["market", "analysis", "report"],
        "doc_id": "def123"
      }
    },
    {
      "text": "业绩统计",
      "score": 0.8000,
      "source": "history",
      "metadata": {
        "from_user_history": true
      }
    },
    {
      "text": "季度总结",
      "score": 0.7654,
      "source": "hybrid",
      "metadata": {
        "keywords": ["quarter", "summary"],
        "doc_id": "ghi789"
      }
    }
  ],
  "total": 3
}
```

**Response Fields**:
- `query`: Original query
- `related_queries`: Array of related queries
  - `text`: Query text
  - `score`: Relevance score (0-1, higher is more relevant)
  - `source`: Source type (`hybrid`, `history`, `trending`)
  - `metadata`: Additional information
- `total`: Total number of related queries returned

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/related-queries" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售报告",
    "user_id": "user123",
    "limit": 5
  }'
```

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Service not initialized"
}
```

---

## Interactive Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

---

## Rate Limiting

Currently, there is no rate limiting. For production:

- Implement rate limiting per user_id
- Consider API gateway with rate limiting
- Monitor and alert on unusual patterns

---

## Best Practices

### 1. Query Optimization

**Do**:
- Send queries as user types (debounced)
- Limit results to 5-10 for UI display
- Include user_id for personalization

**Don't**:
- Send empty queries
- Request excessive results
- Skip user_id if available

### 2. Feedback Recording

**Do**:
- Record every user selection
- Include accurate timestamps
- Use consistent user_ids

**Don't**:
- Record programmatic selections
- Skip feedback for anonymous users

### 3. Document Management

**Do**:
- Use bulk endpoint for large datasets
- Include comprehensive keywords
- Provide meaningful metadata

**Don't**:
- Create duplicate documents
- Skip keywords for important terms
- Use extremely long text (>1000 chars)

### 4. Similar and Related Queries

**When to use Similar Queries**:
- User wants alternative phrasings of the same concept
- Showing "search instead for..." suggestions
- Query refinement based on semantic meaning

**When to use Related Queries**:
- Showing "people also searched for..." suggestions
- Broader exploration of related topics
- Combining semantic similarity with user behavior

**Best Practices**:
- Limit results to 5-8 for UI display
- Use personalization (user_id) when available
- Cache results for popular queries
- Show similar queries first, related queries second

### 5. Error Handling

```python
try:
    response = client.get_suggestions(query)
except requests.exceptions.Timeout:
    # Handle timeout
    pass
except requests.exceptions.ConnectionError:
    # Handle connection error
    pass
except requests.exceptions.HTTPError as e:
    # Handle HTTP errors
    if e.response.status_code == 503:
        # Service unavailable
        pass
```

---

## Code Examples

### Python

```python
import requests

class AutocompleteClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_suggestions(self, query, user_id=None, limit=10):
        response = requests.post(
            f"{self.base_url}/api/v1/autocomplete",
            json={"query": query, "user_id": user_id, "limit": limit}
        )
        return response.json()
    
    def get_similar_queries(self, query, user_id=None, limit=10):
        response = requests.post(
            f"{self.base_url}/api/v1/similar-queries",
            json={"query": query, "user_id": user_id, "limit": limit}
        )
        return response.json()
    
    def get_related_queries(self, query, user_id=None, limit=10):
        response = requests.post(
            f"{self.base_url}/api/v1/related-queries",
            json={"query": query, "user_id": user_id, "limit": limit}
        )
        return response.json()

# Usage
client = AutocompleteClient()
results = client.get_suggestions("销售", user_id="user123")
print(results)

# Get similar queries
similar = client.get_similar_queries("销售分析", user_id="user123")
print(similar["similar_queries"])

# Get related queries
related = client.get_related_queries("销售报告", user_id="user123")
print(related["related_queries"])
```

### JavaScript

```javascript
async function getAutocomplete(query, userId = null, limit = 10) {
  const response = await fetch('http://localhost:8000/api/v1/autocomplete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, user_id: userId, limit }),
  });
  return await response.json();
}

async function getSimilarQueries(query, userId = null, limit = 10) {
  const response = await fetch('http://localhost:8000/api/v1/similar-queries', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, user_id: userId, limit }),
  });
  return await response.json();
}

async function getRelatedQueries(query, userId = null, limit = 10) {
  const response = await fetch('http://localhost:8000/api/v1/related-queries', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, user_id: userId, limit }),
  });
  return await response.json();
}

// Usage
getAutocomplete('销售', 'user123').then(data => {
  console.log(data.suggestions);
});

getSimilarQueries('销售分析', 'user123').then(data => {
  console.log('Similar queries:', data.similar_queries);
});

getRelatedQueries('销售报告', 'user123').then(data => {
  console.log('Related queries:', data.related_queries);
});
```

### cURL

```bash
# Get suggestions
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","user_id":"user123","limit":5}'

# Get similar queries
curl -X POST "http://localhost:8000/api/v1/similar-queries" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售分析","user_id":"user123","limit":5}'

# Get related queries
curl -X POST "http://localhost:8000/api/v1/related-queries" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售报告","user_id":"user123","limit":5}'

# Submit feedback
curl -X POST "http://localhost:8000/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","selected_suggestion":"销售额","user_id":"user123"}'

# Add document
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{"text":"测试查询","keywords":["test","query"]}'
```

---

## WebSocket Support (Future)

Planned for future release:
- Real-time suggestion updates
- Streaming results
- Live personalization updates

---

## Versioning

Current API version: **v1**

Future versions will be accessible via:
- `/api/v2/...` for next major version
- Backward compatibility maintained for v1
