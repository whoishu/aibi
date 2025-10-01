# Test Suite

This directory contains the test suite for the ChatBI Autocomplete Service.

## Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── test_config.py      # Configuration tests
│   └── test_schemas.py     # Schema validation tests
├── integration/        # Integration tests with external services
└── conftest.py        # Shared fixtures and test configuration
```

## Running Tests

### All Tests
```bash
make test
# or
pytest tests/ -v
```

### Unit Tests Only
```bash
make test-unit
# or
pytest tests/unit/ -v -m unit
```

### Integration Tests Only
```bash
make test-integration
# or
pytest tests/integration/ -v -m integration
```

### With Coverage
```bash
make coverage
# or
pytest tests/ -v --cov=app --cov-report=html
```

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.unit`: Fast tests that don't require external dependencies
- `@pytest.mark.integration`: Tests that require OpenSearch, Redis, or other services
- `@pytest.mark.slow`: Tests that take significant time to run

## Writing Tests

### Unit Tests

Unit tests should:
- Test individual functions/classes in isolation
- Mock external dependencies
- Run quickly (< 1 second per test)
- Not require external services

Example:
```python
import pytest
from app.models.schemas import AutocompleteRequest

@pytest.mark.unit
def test_autocomplete_request_validation():
    """Test request validation"""
    request = AutocompleteRequest(query="test", limit=5)
    assert request.query == "test"
    assert request.limit == 5
```

### Integration Tests

Integration tests should:
- Test interactions between components
- Use real or containerized services
- Test end-to-end workflows
- Be marked appropriately

Example:
```python
import pytest
from app.services.opensearch_service import OpenSearchService

@pytest.mark.integration
async def test_opensearch_connection(mock_opensearch_client):
    """Test OpenSearch connection"""
    service = OpenSearchService(mock_opensearch_client)
    result = await service.ping()
    assert result is True
```

## Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_opensearch_client`: Mock OpenSearch client
- `mock_redis_client`: Mock Redis client
- `mock_vector_service`: Mock vector service
- `sample_autocomplete_request`: Sample request data
- `sample_suggestions`: Sample suggestion data

## Coverage Goals

- Overall coverage: > 80%
- Critical paths: > 90%
- New code: > 85%

View coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## Best Practices

1. **Keep tests focused**: One test should verify one behavior
2. **Use descriptive names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use fixtures**: Reuse common setup code
5. **Mock external calls**: Don't hit real APIs in unit tests
6. **Clean up**: Tests should be independent and not leave state
7. **Document complex tests**: Add docstrings explaining the test

## Continuous Integration

Tests run automatically in GitHub Actions on:
- Every push to main/develop
- Every pull request
- Multiple Python versions (3.9, 3.10, 3.11, 3.12)

See `.github/workflows/ci.yml` for CI configuration.
