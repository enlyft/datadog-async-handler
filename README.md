# Datadog Async Handler

[![PyPI version](https://badge.fury.io/py/datadog-async-handler.svg)](https://badge.fury.io/py/datadog-async-handler)
[![Python versions](https://img.shields.io/pypi/pyversions/datadog-async-handler.svg)](https://pypi.org/project/datadog-async-handler/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A modern, high-performance Python logging handler that sends logs directly to Datadog via HTTP API with asynchronous batching, retry logic, and comprehensive error handling.

## ✨ Features

- **🚀 High Performance**: Asynchronous batching and background processing
- **🔄 Reliable Delivery**: Automatic retry with exponential backoff
- **📊 Batching**: Configurable batch size and flush intervals
- **🏷️ Rich Metadata**: Automatic service, environment, and custom tag support
- **🔧 Easy Integration**: Drop-in replacement for standard logging handlers
- **🌐 Multi-Site Support**: Works with all Datadog sites (US, EU, etc.)
- **📝 Type Safe**: Full type hints and mypy compatibility
- **⚡ Modern**: Built with Python 3.9+ and latest best practices

## 🚀 Quick Start

### Installation

```bash
pip install datadog-async-handler
```

### Basic Usage

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Configure the handler
handler = DatadogHTTPHandler(
    api_key="your-datadog-api-key",  # or set DD_API_KEY env var
    service="my-application",
    source="python",
    tags="env:production,team:backend"
)

# Set up logging
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Start logging!
logger.info("Application started successfully", extra={
    "user_id": "12345",
    "action": "startup"
})
```

### Environment Variables

The handler automatically picks up standard Datadog environment variables:

```bash
export DD_API_KEY="your-api-key"
export DD_SERVICE="my-application"
export DD_ENV="production"
export DD_VERSION="1.2.3"
export DD_TAGS="team:backend,component:api"
export DD_SITE="datadoghq.com"  # or datadoghq.eu, ddog-gov.com, etc.
```

## 📖 Documentation

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `None` | Datadog API key (required) |
| `site` | `str` | `"datadoghq.com"` | Datadog site |
| `service` | `str` | `None` | Service name |
| `source` | `str` | `"python"` | Log source |
| `hostname` | `str` | `None` | Hostname |
| `tags` | `str` | `None` | Comma-separated tags |
| `batch_size` | `int` | `10` | Number of logs per batch |
| `flush_interval_seconds` | `float` | `5.0` | Batch flush interval |
| `timeout_seconds` | `float` | `10.0` | Request timeout |
| `max_retries` | `int` | `3` | Maximum retry attempts |

### Framework Integration Examples

#### Django

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'datadog': {
            'class': 'datadog_http_handler.DatadogHTTPHandler',
            'api_key': 'your-api-key',
            'service': 'django-app',
            'source': 'django',
        },
    },
    'root': {
        'handlers': ['datadog'],
        'level': 'INFO',
    },
}
```

#### FastAPI

```python
import logging
from fastapi import FastAPI
from datadog_http_handler import DatadogHTTPHandler

app = FastAPI()

# Configure logging
handler = DatadogHTTPHandler(service="fastapi-app", source="fastapi")
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

@app.get("/")
async def root():
    logging.info("API endpoint called", extra={"endpoint": "/"})
    return {"message": "Hello World"}
```

#### Flask

```python
import logging
from flask import Flask
from datadog_http_handler import DatadogHTTPHandler

app = Flask(__name__)

# Configure logging
handler = DatadogHTTPHandler(service="flask-app", source="flask")
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route("/")
def hello():
    app.logger.info("Flask endpoint called", extra={"endpoint": "/"})
    return "Hello World!"
```

## 🔧 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/enlyft/datadog-http-handler.git
cd datadog-http-handler

# Install UV (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
hatch run test

# Run with coverage
hatch run test-cov

# Run specific tests
hatch run test tests/test_handler.py::test_basic_logging
```

### Code Quality

```bash
# Format code
hatch run format

# Lint code
hatch run lint

# Type checking
hatch run type-check

# Run all checks
hatch run all
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📋 Requirements

- Python 3.9+
- `datadog-api-client>=2.0.0`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](https://enlyft.github.io/datadog-http-handler)
- [PyPI Package](https://pypi.org/project/datadog-async-handler/)
- [GitHub Repository](https://github.com/enlyft/datadog-http-handler)
- [Issue Tracker](https://github.com/enlyft/datadog-http-handler/issues)
- [Datadog Logs API Documentation](https://docs.datadoghq.com/api/latest/logs/)

## 🆚 Comparison with Other Solutions

| Feature | datadog-async-handler | datadog-http-handler | python-datadog | datadog-logger |
|---------|----------------------|---------------------|----------------|----------------|
| Async Batching | ✅ | ❌ | ❌ | ❌ |
| Retry Logic | ✅ | ❌ | ❌ | ❌ |
| Type Hints | ✅ | ❌ | ❌ | ❌ |
| Modern Python | ✅ (3.9+) | ❌ (3.6+) | ❌ (2.7+) | ❌ (3.6+) |
| Official API Client | ✅ | ❌ | ❌ | ❌ |
| Background Processing | ✅ | ❌ | ❌ | ❌ |
| Memory Efficient | ✅ | ❌ | ❌ | ❌ |
| Active Maintenance | ✅ | ❌ (2019) | ✅ | ❌ |
| Comprehensive Tests | ✅ | ❌ | ✅ | ❌ |

---

Made with ❤️ for the Python and Datadog communities.