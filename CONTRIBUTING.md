# Contributing to aibi

Thank you for your interest in contributing to aibi! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker and Docker Compose (for running dependencies)

### Setting Up Your Development Environment

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/aibi.git
cd aibi
```

2. **Install uv (recommended package manager):**

```bash
pip install uv
```

3. **Sync dependencies:**

```bash
# Install all dependencies including development tools
uv sync --all-extras
```

This will create a `.venv` directory with all dependencies including:
- Core application dependencies (FastAPI, OpenSearch, etc.)
- Development tools (black, ruff, pytest)

4. **Start dependencies:**

```bash
docker-compose up -d
```

## Code Quality Standards

This project maintains high code quality standards using automated tools.

### Code Formatting

We use **[black](https://black.readthedocs.io/)** for consistent code formatting:

```bash
# Format all code
make format

# Or manually
uv run black app/ scripts/ examples/
```

Black configuration:
- Line length: 100 characters
- Target Python versions: 3.8+

### Linting

We use **[ruff](https://docs.astral.sh/ruff/)** for fast linting:

```bash
# Check code with ruff
make lint

# Or manually
uv run ruff check app/ scripts/ examples/

# Auto-fix issues where possible
uv run ruff check --fix app/ scripts/ examples/
```

Ruff checks for:
- Code style issues (pycodestyle)
- Common bugs (pyflakes, bugbear)
- Import sorting (isort)
- Outdated syntax (pyupgrade)

### Running All Checks

```bash
# Run both formatting and linting
make check
```

## Development Workflow

1. **Create a new branch:**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

3. **Format and lint your code:**

```bash
make check
```

4. **Test your changes:**

```bash
# Run the service
uv run python app/main.py

# Test API endpoints
uv run python scripts/test_api.py

# Verify installation
uv run python scripts/verify_installation.py
```

5. **Commit your changes:**

```bash
git add .
git commit -m "Description of your changes"
```

Use clear, descriptive commit messages. For example:
- `feat: add new autocomplete algorithm`
- `fix: resolve Redis connection timeout`
- `docs: update installation instructions`
- `refactor: simplify vector service logic`

6. **Push your changes:**

```bash
git push origin feature/your-feature-name
```

7. **Create a Pull Request**

## Project Structure

```
aibi/
├── app/                    # Main application code
│   ├── api/               # API routes and endpoints
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── utils/             # Utilities and config
├── scripts/               # Utility scripts
├── examples/              # Usage examples
├── config.yaml           # Configuration
├── pyproject.toml        # Dependencies and tool config
├── Makefile              # Development commands
└── README.md
```

## Adding Dependencies

When adding new dependencies:

1. **Add to pyproject.toml:**

```toml
[project]
dependencies = [
    "new-package>=1.0.0",
]
```

2. **Sync dependencies:**

```bash
uv sync
```

3. **Commit both pyproject.toml and uv.lock:**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add new-package dependency"
```

## Testing

While comprehensive tests are still being developed, please:

1. Run the verification script:
```bash
uv run python scripts/verify_installation.py
```

2. Test API endpoints manually:
```bash
uv run python scripts/test_api.py
```

3. Ensure your changes don't break existing functionality

## Code Review Process

1. All submissions require review
2. Reviewers will check:
   - Code follows style guidelines (black + ruff)
   - Changes are well-documented
   - No breaking changes to existing APIs
   - Tests pass (when available)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing documentation in the `/docs` directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
