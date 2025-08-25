# Datadog Async Handler Documentation

Welcome to the documentation for datadog-async-handler, a high-performance Python logging handler for Datadog.

## Quick Links

- [Installation Guide](installation.md)
- [API Reference](api.md)
- [Usage Examples](examples.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)

## Overview

The `datadog-async-handler` package provides a modern, high-performance logging handler that sends logs directly to Datadog's HTTP intake API. It features:

- **🚀 High Performance**: Asynchronous batching and background processing
- **🔄 Reliable Delivery**: Automatic retry with exponential backoff
- **📊 Batching**: Configurable batch size and flush intervals
- **🏷️ Rich Metadata**: Automatic service, environment, and custom tag support
- **🔧 Easy Integration**: Drop-in replacement for standard logging handlers
- **🌐 Multi-Site Support**: Works with all Datadog sites (US, EU, etc.)
- **📝 Type Safe**: Full type hints and mypy compatibility

## Quick Start

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Create handler
handler = DatadogHTTPHandler(
    api_key="your-datadog-api-key",
    service="my-application",
    tags="env:production,team:backend"
)

# Set up logging
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Start logging!
logger.info("Application started successfully")
```

## Installation

```bash
pip install datadog-async-handler
```

## Framework Integration

The handler works seamlessly with popular Python frameworks:

- [Django](examples.md#django)
- [FastAPI](examples.md#fastapi)
- [Flask](examples.md#flask)
- [Celery](examples.md#celery)

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/enlyft/datadog-http-handler/blob/main/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/enlyft/datadog-http-handler/blob/main/LICENSE) file for details.