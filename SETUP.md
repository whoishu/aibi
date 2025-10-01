# Setup Guide

This guide will help you set up and run the ChatBI Autocomplete Service.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for OpenSearch and Redis)
- 4GB+ RAM available
- Internet connection (for downloading models and dependencies)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/whoishu/aibi.git
cd aibi
```

### 2. Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework
- Uvicorn - ASGI server
- OpenSearch client - Search engine client
- Sentence Transformers - Vector embedding model
- Redis client - User behavior tracking
- Other supporting libraries

**Note**: First-time installation will download the multilingual sentence transformer model (~400MB). This may take a few minutes.

### 4. Start Dependencies with Docker

```bash
# Start OpenSearch and Redis
docker-compose up -d

# Check if containers are running
docker-compose ps
```

Expected output:
```
NAME                  STATUS    PORTS
chatbi_opensearch     Up        0.0.0.0:9200->9200/tcp, 0.0.0.0:9600->9600/tcp
chatbi_redis          Up        0.0.0.0:6379->6379/tcp
```

**Troubleshooting**:
- If ports are already in use, modify `docker-compose.yml` to use different ports
- On Linux, you may need to increase `vm.max_map_count`: 
  ```bash
  sudo sysctl -w vm.max_map_count=262144
  ```

### 5. Verify Dependencies

```bash
# Test OpenSearch
curl http://localhost:9200

# Test Redis
docker exec chatbi_redis redis-cli ping
# Should return: PONG
```

### 6. Initialize Sample Data

```bash
python scripts/init_data.py
```

This script will:
- Create the OpenSearch index with proper mappings
- Generate vector embeddings for sample data
- Index 50+ sample Chinese/English queries

**Note**: Initial model loading may take 1-2 minutes.

### 7. Start the Service

```bash
# Development mode (with auto-reload)
python app/main.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 8. Verify Installation

```bash
# In a new terminal
python scripts/verify_installation.py

# Test the API
python scripts/test_api.py
```

## Configuration

### Basic Configuration

Edit `config.yaml` to customize settings:

```yaml
# OpenSearch settings
opensearch:
  host: "localhost"
  port: 9200
  index_name: "chatbi_autocomplete"

# Redis settings (optional)
redis:
  host: "localhost"
  port: 6379

# Search weights
autocomplete:
  keyword_weight: 0.7      # 0-1, higher = more exact matching
  vector_weight: 0.3       # 0-1, higher = more semantic matching
  personalization_weight: 0.2  # 0-1, personalization boost
```

### Advanced Configuration

**Vector Model**: Change the embedding model (requires model re-download):

```yaml
vector_model:
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  dimension: 384
```

Available models:
- `paraphrase-multilingual-MiniLM-L12-v2` (384d, 420MB) - Default, good balance
- `paraphrase-multilingual-mpnet-base-v2` (768d, 970MB) - Better quality, slower
- `distiluse-base-multilingual-cased-v2` (512d, 480MB) - Fast, good for English

**Search Tuning**:

For more exact matching (keyword priority):
```yaml
autocomplete:
  keyword_weight: 0.8
  vector_weight: 0.2
```

For more semantic matching (meaning priority):
```yaml
autocomplete:
  keyword_weight: 0.5
  vector_weight: 0.5
```

## Deployment

### Production Deployment

1. **Environment Variables**: Create `.env` file:
```bash
OPENSEARCH_HOST=opensearch.example.com
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your-password
REDIS_HOST=redis.example.com
```

2. **Update Configuration**: Use environment variables in config

3. **Use Production Server**:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

4. **Set Up Reverse Proxy**: Use nginx or similar

5. **Enable HTTPS**: Use Let's Encrypt or similar

### Docker Deployment

Build the service as a Docker image:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t chatbi-autocomplete .
docker run -p 8000:8000 --network host chatbi-autocomplete
```

## Scaling

### Horizontal Scaling

The service is stateless and can be scaled horizontally:

```bash
# Using Docker Compose
docker-compose up -d --scale api=3
```

### OpenSearch Cluster

For production, use an OpenSearch cluster:

```yaml
opensearch:
  host: "opensearch-cluster.example.com"
  port: 9200
  use_ssl: true
  verify_certs: true
```

### Redis Cluster

For high availability:

```yaml
redis:
  host: "redis-cluster.example.com"
  port: 6379
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Logs

Service logs include:
- Request/response logs
- Search performance metrics
- Error traces

### Metrics

Consider adding Prometheus metrics for:
- Request latency
- Search performance
- Cache hit rates
- Model inference time

## Backup and Recovery

### Backup OpenSearch Data

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/my_backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/mount/backups/my_backup"
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true"
```

### Backup Redis Data

```bash
docker exec chatbi_redis redis-cli BGSAVE
```

## Troubleshooting

### Common Issues

**Issue**: Service won't start
- Check if ports 8000, 9200, 6379 are available
- Verify dependencies are installed
- Check logs for detailed errors

**Issue**: Slow first request
- Model loading takes time on first request
- Subsequent requests will be fast

**Issue**: No suggestions returned
- Verify data is indexed: `curl http://localhost:9200/chatbi_autocomplete/_count`
- Check query format
- Try increasing limit or reducing min_score

**Issue**: OpenSearch connection failed
- Verify OpenSearch is running
- Check network connectivity
- Review credentials in config

**Issue**: Personalization not working
- Verify Redis is running
- Check if personalization is enabled in config
- Ensure user_id is provided in requests

## Next Steps

- Read the [API Documentation](http://localhost:8000/docs)
- Check out [examples/client_example.py](examples/client_example.py)
- See [README.md](README.md) for API usage
- Review [config.yaml](config.yaml) for customization options
