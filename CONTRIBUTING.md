# Contributing to ChatBI Autocomplete Service

Thank you for your interest in contributing! This document provides guidelines and information about our development workflow.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for running dependencies)
- Git

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/whoishu/aibi.git
cd aibi
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
make install-dev
# Or manually:
pip install -r requirements-dev.txt
pre-commit install
```

4. Start dependencies:
```bash
make docker-up
# Or manually:
docker-compose up -d
```

## Code Quality Standards

We maintain high code quality standards using automated tools.

### Code Formatting

- **Black**: Code formatter with 100 character line length
- **isort**: Import statement organizer

Format your code:
```bash
make format
```

### Linting

- **Flake8**: Style guide enforcement
- **MyPy**: Static type checking

Run linters:
```bash
make lint
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON syntax checking
- Black formatting
- isort import sorting
- Flake8 linting
- MyPy type checking

Run manually:
```bash
make pre-commit
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests with external services
└── conftest.py     # Shared fixtures and configuration
```

### Running Tests

Run all tests:
```bash
make test
```

Run unit tests only:
```bash
make test-unit
```

Run integration tests only:
```bash
make test-integration
```

Generate coverage report:
```bash
make coverage
```

### Writing Tests

- Use pytest for all tests
- Add appropriate markers: `@pytest.mark.unit` or `@pytest.mark.integration`
- Mock external dependencies in unit tests
- Use fixtures from `conftest.py`
- Aim for >80% code coverage

Example:
```python
import pytest
from app.models.schemas import AutocompleteRequest

@pytest.mark.unit
def test_autocomplete_request():
    """Test autocomplete request validation"""
    request = AutocompleteRequest(query="test", limit=5)
    assert request.query == "test"
    assert request.limit == 5
```

## Development Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code standards

3. **Run tests** to ensure nothing breaks:
   ```bash
   make test
   ```

4. **Format and lint** your code:
   ```bash
   make format
   make lint
   ```

5. **Commit your changes** (pre-commit hooks will run automatically):
   ```bash
   git add .
   git commit -m "Add descriptive commit message"
   ```

6. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## CI/CD Pipeline

Our GitHub Actions workflow runs automatically on pull requests:

- **Lint**: Checks code formatting and style
- **Test**: Runs all tests across Python 3.9, 3.10, 3.11, and 3.12
- **Security**: Scans for vulnerabilities
- **Build**: Verifies installation

All checks must pass before merging.

## Security

### Dependency Security

We use Safety to check for known vulnerabilities:
```bash
make security
```

### Code Security

We use Bandit for security scanning:
```bash
bandit -r app/
```

## Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Update ARCHITECTURE.md for architectural changes
- Add docstrings to all new functions and classes
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)

## Commit Message Guidelines

Follow conventional commits format:

- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `style: Code style changes`
- `refactor: Code refactoring`
- `test: Add or update tests`
- `chore: Maintenance tasks`

## Code Review

All changes must be reviewed before merging:

1. Ensure all CI checks pass
2. Address reviewer feedback
3. Keep changes focused and minimal
4. Update documentation as needed

## Need Help?

- Check existing issues on GitHub
- Review our documentation in the repo
- Ask questions in pull request comments

## License

By contributing, you agree that your contributions will be licensed under the project's license.
