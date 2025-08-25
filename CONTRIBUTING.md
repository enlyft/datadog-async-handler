# Contributing to datadog-http-handler

Thank you for your interest in contributing to datadog-http-handler! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [UV](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/enlyft/datadog-http-handler.git
cd datadog-http-handler
```

2. Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync --extra dev
```

4. Install pre-commit hooks:
```bash
uv run pre-commit install
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/datadog_http_handler --cov-report=term-missing

# Run specific test
uv run pytest tests/test_handler.py::TestDatadogHTTPHandler::test_init_with_api_key
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/datadog_http_handler tests

# Run all quality checks
uv run pre-commit run --all-files
```

### Building

```bash
# Build package
uv build

# Install locally for testing
uv pip install -e .
```

## Code Style

This project uses:
- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

### Code Guidelines

1. **Type Hints**: All public functions and methods must have type hints
2. **Docstrings**: All public classes and functions must have docstrings
3. **Tests**: All new features must include tests
4. **Coverage**: Maintain >95% test coverage

### Example Function

```python
def process_log_item(record: logging.LogRecord, tags: Optional[list[str]] = None) -> HTTPLogItem:
    """Process a log record into a Datadog HTTP log item.
    
    Args:
        record: The log record to process
        tags: Optional additional tags to include
        
    Returns:
        Formatted HTTP log item ready for submission
        
    Raises:
        ValueError: If record cannot be processed
    """
    # Implementation here
    pass
```

## Testing

### Test Structure

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Performance Tests**: Benchmark critical paths

### Writing Tests

```python
import pytest
from datadog_http_handler import DatadogHTTPHandler

def test_handler_initialization():
    """Test that handler initializes correctly."""
    handler = DatadogHTTPHandler(
        api_key="test-key",
        service="test-service"
    )
    assert handler.service == "test-service"
    handler.close()
```

### Test Fixtures

Use the provided fixtures in `tests/conftest.py`:

```python
def test_log_formatting(handler_config, sample_log_record):
    """Test log record formatting."""
    handler = DatadogHTTPHandler(**handler_config)
    log_item = handler._format_log_item(sample_log_record)
    assert log_item.service == "test-service"
```

## Documentation

### Docstring Style

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int = 0) -> bool:
    """Brief description of the function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2 with default value
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        ConnectionError: When network request fails
    """
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** quality checks: `uv run pre-commit run --all-files`
6. **Commit** your changes: `git commit -m "Add amazing feature"`
7. **Push** to your fork: `git push origin feature/amazing-feature`
8. **Create** a Pull Request

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage maintained (>95%)
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## Release Process

1. Update version in `src/datadog_http_handler/__init__.py`
2. Update CHANGELOG.md
3. Create a tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will automatically build and publish

## Getting Help

- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check the README.md and code docstrings

## License

By contributing, you agree that your contributions will be licensed under the MIT License.