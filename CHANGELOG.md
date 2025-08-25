# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-08-25

### Added
- First stable release of datadog-async-handler
- High-performance async HTTP logging handler for Datadog
- Asynchronous batching and background processing
- Automatic retry logic with exponential backoff
- Configurable batch size and flush intervals
- Rich metadata support (service, environment, tags)
- Multi-site Datadog support (US, EU, etc.)
- Full type hints and mypy compatibility
- Comprehensive documentation and examples
- GitHub Actions CI/CD with trusted PyPI publishing

### Features
- **Performance**: Non-blocking background processing
- **Reliability**: Comprehensive retry logic and error handling
- **Efficiency**: Memory-optimized batching reduces API calls
- **Integration**: Drop-in replacement for standard logging handlers
- **Framework Support**: Examples for Django, FastAPI, Flask, Celery
- **Testing**: Comprehensive test suite with >95% coverage

### Documentation
- Complete API reference with mkdocstrings
- Framework integration examples
- Configuration guide with all parameters
- Troubleshooting documentation
- Installation instructions

### Infrastructure
- Modern Python packaging with pyproject.toml
- Hatch build system with UV package manager
- Ruff for formatting and linting
- MyPy for type checking
- Pytest for testing
- MkDocs Material theme for documentation
- GitHub Actions for CI/CD
- Trusted publishing to PyPI

## [Unreleased]

### Planned
- Async/await support for truly asynchronous logging
- Metrics and tracing integration
- Advanced filtering and transformation options
- Performance optimizations
- Additional framework integrations