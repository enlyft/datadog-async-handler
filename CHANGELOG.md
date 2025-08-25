# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of datadog-http-handler
- Asynchronous HTTP logging handler for Datadog
- Batching support with configurable batch size and flush intervals
- Automatic retry logic with exponential backoff
- Comprehensive error handling and graceful degradation
- Type hints and mypy compatibility
- Support for all Datadog sites (US, EU, Government, etc.)
- Environment variable configuration support
- Framework integration examples (Django, FastAPI, Flask)
- Background worker thread for non-blocking log processing
- Automatic tag enrichment (environment, service, version)
- Memory-efficient queue management
- Graceful shutdown handling

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

## [0.1.0] - 2025-08-25

### Added
- Initial development version
- Core DatadogHTTPHandler implementation
- Basic test suite
- Documentation and examples
- Modern Python packaging with Hatch
- Comprehensive development tooling (Ruff, mypy, pytest)