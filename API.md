# API Documentation

Complete API reference for the ChatBI Autocomplete Service.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the service does not require authentication. For production deployment, consider adding API key or OAuth2 authentication.

## Endpoints

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

### 4. Error Handling

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

# Usage
client = AutocompleteClient()
results = client.get_suggestions("销售", user_id="user123")
print(results)
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

// Usage
getAutocomplete('销售', 'user123').then(data => {
  console.log(data.suggestions);
});
```

### cURL

```bash
# Get suggestions
curl -X POST "http://localhost:8000/api/v1/autocomplete" \
  -H "Content-Type: application/json" \
  -d '{"query":"销售","user_id":"user123","limit":5}'

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
