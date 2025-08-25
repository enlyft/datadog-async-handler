# Configuration

## Handler Parameters

The `DatadogHTTPHandler` accepts the following configuration parameters:

### Required Parameters

- **`api_key`** (str): Your Datadog API key

### Optional Parameters

- **`service`** (str): Service name for your logs (default: "python-app")
- **`environment`** (str): Environment name (default: "production")  
- **`version`** (str): Application version (default: "1.0.0")
- **`site`** (str): Datadog site (default: "datadoghq.com")
- **`tags`** (str): Comma-separated tags (default: "")
- **`batch_size`** (int): Number of logs to batch before sending (default: 10)
- **`flush_interval`** (float): Maximum time in seconds before flushing logs (default: 5.0)
- **`max_retries`** (int): Maximum number of retry attempts (default: 3)
- **`timeout`** (float): Request timeout in seconds (default: 30.0)

## Configuration Examples

### Basic Configuration

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

handler = DatadogHTTPHandler(
    api_key="your-datadog-api-key"
)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

### Advanced Configuration

```python
handler = DatadogHTTPHandler(
    api_key="your-datadog-api-key",
    service="my-web-service",
    environment="staging",
    version="2.1.0",
    site="datadoghq.eu",  # EU site
    tags="team:backend,component:auth",
    batch_size=25,
    flush_interval=10.0,
    max_retries=5,
    timeout=45.0
)
```

### Environment Variables

You can also configure the handler using environment variables:

```bash
export DATADOG_API_KEY="your-api-key"
export DATADOG_SERVICE="my-service"
export DATADOG_ENV="production"
export DATADOG_VERSION="1.0.0"
```

```python
import os
from datadog_http_handler import DatadogHTTPHandler

handler = DatadogHTTPHandler(
    api_key=os.environ["DATADOG_API_KEY"],
    service=os.environ.get("DATADOG_SERVICE", "python-app"),
    environment=os.environ.get("DATADOG_ENV", "production"),
    version=os.environ.get("DATADOG_VERSION", "1.0.0")
)
```

## Logging Configuration

### Log Levels

The handler respects standard Python logging levels:

```python
logger.debug("Debug message")     # DEBUG level
logger.info("Info message")       # INFO level  
logger.warning("Warning message") # WARNING level
logger.error("Error message")     # ERROR level
logger.critical("Critical message") # CRITICAL level
```

### Log Format

You can customize log formatting:

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Create handler
handler = DatadogHTTPHandler(api_key="your-key")

# Set custom format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# Add to logger
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

## Performance Tuning

### Batch Size

Larger batch sizes reduce API calls but increase memory usage:

```python
# For high-volume applications
handler = DatadogHTTPHandler(
    api_key="your-key",
    batch_size=50,  # Send 50 logs per batch
    flush_interval=2.0  # Flush every 2 seconds
)

# For low-volume applications
handler = DatadogHTTPHandler(
    api_key="your-key", 
    batch_size=5,   # Send 5 logs per batch
    flush_interval=10.0  # Flush every 10 seconds
)
```

### Timeout Settings

Adjust timeouts based on your network conditions:

```python
# For reliable networks
handler = DatadogHTTPHandler(
    api_key="your-key",
    timeout=10.0,  # 10 second timeout
    max_retries=2
)

# For unreliable networks
handler = DatadogHTTPHandler(
    api_key="your-key",
    timeout=60.0,  # 60 second timeout
    max_retries=5
)
```