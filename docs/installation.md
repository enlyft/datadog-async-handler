# Installation

## Requirements

- Python 3.9 or higher
- A Datadog account with API access

## Install from PyPI

The easiest way to install the Datadog Async Handler is via pip:

```bash
pip install datadog-async-handler
```

## Install from Source

If you want to install from source:

```bash
git clone https://github.com/enlyft/datadog-http-handler.git
cd datadog-http-handler
pip install -e .
```

## Development Installation

For development, clone the repository and install with development dependencies:

```bash
git clone https://github.com/enlyft/datadog-http-handler.git
cd datadog-http-handler
pip install -e ".[dev]"
```

## Verify Installation

You can verify the installation by importing the handler:

```python
from datadog_http_handler import DatadogHTTPHandler
print("Installation successful!")
```