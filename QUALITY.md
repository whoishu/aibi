# Quality Management

This document describes the quality management practices and tools used in the ChatBI Autocomplete Service project.

## Overview

We maintain high code quality through:
- Automated code formatting
- Static code analysis
- Comprehensive testing
- Continuous integration
- Security scanning
- Dependency management

## Code Quality Tools

### Black - Code Formatter

Black automatically formats Python code to a consistent style.

**Configuration**: `pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

**Usage**:
```bash
make format          # Format all code
black app/ tests/    # Format specific directories
black --check app/   # Check without modifying
```

### isort - Import Organizer

isort organizes imports according to PEP 8 guidelines.

**Configuration**: `pyproject.toml`
```toml
[tool.isort]
profile = "black"
line_length = 100
```

**Usage**:
```bash
make format           # Format imports
isort app/ tests/     # Format specific directories
isort --check app/    # Check without modifying
```

### Flake8 - Style Checker

Flake8 checks code style and detects potential errors.

**Configuration**: `.flake8`
```ini
[flake8]
max-line-length = 100
max-complexity = 10
```

**Usage**:
```bash
make lint            # Run all linters
flake8 app/          # Check specific directory
```

### MyPy - Type Checker

MyPy performs static type checking to catch type-related errors.

**Configuration**: `pyproject.toml`
```toml
[tool.mypy]
python_version = "3.8"
check_untyped_defs = true
```

**Usage**:
```bash
make lint            # Run all linters including mypy
mypy app/            # Check specific directory
```

## Testing

### pytest - Testing Framework

We use pytest for all testing with coverage tracking.

**Configuration**: `pytest.ini` and `pyproject.toml`

**Test Categories**:
- **Unit Tests**: Fast, isolated tests (`@pytest.mark.unit`)
- **Integration Tests**: Tests with external services (`@pytest.mark.integration`)
- **Slow Tests**: Long-running tests (`@pytest.mark.slow`)

**Usage**:
```bash
make test                    # Run all tests
make test-unit              # Run unit tests only
make test-integration       # Run integration tests only
make coverage               # Run with coverage report
pytest tests/unit/test_config.py  # Run specific test file
```

### Coverage Requirements

- **Overall**: > 80% code coverage
- **Critical paths**: > 90% coverage
- **New code**: > 85% coverage

View coverage:
```bash
make coverage
# Open htmlcov/index.html in browser
```

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure code quality.

**Configuration**: `.pre-commit-config.yaml`

**Hooks included**:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- isort import sorting
- Flake8 linting
- MyPy type checking

**Setup**:
```bash
make install-dev     # Installs hooks
pre-commit run --all-files  # Run manually
```

## Continuous Integration

Our CI/CD pipeline runs on GitHub Actions for every push and pull request.

**Configuration**: `.github/workflows/ci.yml`

**Pipeline stages**:

1. **Lint**: Code quality checks
   - Black formatting
   - isort import sorting
   - Flake8 linting
   - MyPy type checking

2. **Test**: Comprehensive testing
   - Tests on Python 3.9, 3.10, 3.11, 3.12
   - Unit and integration tests
   - Coverage reporting
   - Upload to Codecov

3. **Security**: Security scanning
   - Safety dependency check
   - Bandit security scan

4. **Build**: Installation verification
   - Verify installation
   - Check imports

**All checks must pass before merging.**

## Security

### Dependency Scanning

We use Safety to scan for known vulnerabilities in dependencies.

**Usage**:
```bash
make security                     # Run security checks
safety check --file requirements.txt  # Direct usage
python scripts/check_dependencies.py  # Full dependency report
```

### Code Security Scanning

We use Bandit to scan for common security issues in Python code.

**Usage**:
```bash
make security        # Run security checks
bandit -r app/       # Direct usage
```

### Security Best Practices

1. Never commit secrets or credentials
2. Use environment variables for sensitive config
3. Keep dependencies updated
4. Review security scan reports
5. Follow OWASP guidelines

## Dependency Management

### Production Dependencies

**File**: `requirements.txt`

Contains only packages needed to run the application.

### Development Dependencies

**File**: `requirements-dev.txt`

Contains all development, testing, and quality tools.

### Checking Dependencies

```bash
python scripts/check_dependencies.py  # Check for updates and issues
pip list --outdated                   # List outdated packages
pip check                            # Check for conflicts
```

### Updating Dependencies

1. Check for updates:
   ```bash
   pip list --outdated
   ```

2. Update specific package:
   ```bash
   pip install --upgrade package-name
   pip freeze > requirements.txt
   ```

3. Test thoroughly after updates:
   ```bash
   make test
   make lint
   ```

4. Run security scan:
   ```bash
   make security
   ```

## Development Workflow

### Daily Development

1. **Start work**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes** with editor/IDE

3. **Format code** (happens automatically with pre-commit):
   ```bash
   make format
   ```

4. **Run tests**:
   ```bash
   make test
   ```

5. **Commit** (pre-commit hooks run automatically):
   ```bash
   git add .
   git commit -m "Add feature"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/my-feature
   ```

### Before Committing

Always run:
```bash
make format    # Format code
make lint      # Check code quality
make test      # Run tests
```

Or use the pre-commit hooks:
```bash
pre-commit run --all-files
```

## Quality Metrics

We track several quality metrics:

### Code Coverage
- Target: > 80%
- View: `htmlcov/index.html` after `make coverage`

### Code Complexity
- Max cyclomatic complexity: 10 (enforced by Flake8)
- Refactor complex functions

### Type Coverage
- Goal: Increase type annotations over time
- Check with MyPy

### Test Performance
- Unit tests: < 1s each
- Integration tests: < 5s each
- Full suite: < 2 minutes

## IDE Integration

### VS Code

Install extensions:
- Python
- Pylance
- Python Test Explorer

Settings (`.vscode/settings.json`):
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true
}
```

### PyCharm

1. Enable Black:
   - Preferences → Tools → Black
   - Check "On save"

2. Enable pytest:
   - Preferences → Tools → Python Integrated Tools
   - Testing → Default test runner → pytest

3. Enable inspections:
   - Preferences → Editor → Inspections
   - Enable Python inspections

## Troubleshooting

### Pre-commit hooks failing

```bash
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

### Tests failing locally but passing in CI

- Check Python version matches CI
- Ensure all dependencies installed
- Check environment variables

### Import errors in tests

- Ensure project root is in PYTHONPATH
- Check test file structure
- Verify __init__.py files exist

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)
- [Safety Documentation](https://pyup.io/safety/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

## Getting Help

- Review existing documentation
- Check GitHub Issues
- Ask in pull request comments
- Refer to CONTRIBUTING.md
