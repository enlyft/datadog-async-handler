# Troubleshooting

## Common Issues

### 1. Handler Not Sending Logs

**Symptoms**: Logs are not appearing in Datadog

**Possible Causes**:
- Invalid API key
- Network connectivity issues
- Incorrect Datadog site configuration
- Logs are below the configured log level

**Solutions**:

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG)

handler = DatadogHTTPHandler(
    api_key="your-api-key",
    service="debug-test"
)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # Make sure level is set

# Test with a simple log
logger.info("Test log message")
```

### 2. High Memory Usage

**Symptoms**: Application memory usage increases over time

**Possible Causes**:
- Large batch sizes with slow network
- Logs are queuing up faster than they can be sent
- Long flush intervals with high log volume

**Solutions**:

```python
# Reduce batch size and flush interval
handler = DatadogHTTPHandler(
    api_key="your-api-key",
    batch_size=5,        # Smaller batches
    flush_interval=2.0,  # More frequent flushes
    timeout=10.0         # Shorter timeouts
)
```

### 3. API Rate Limiting

**Symptoms**: HTTP 429 errors in logs

**Possible Causes**:
- Sending too many requests to Datadog API
- Small batch sizes causing many API calls

**Solutions**:

```python
# Increase batch size to reduce API calls
handler = DatadogHTTPHandler(
    api_key="your-api-key",
    batch_size=50,       # Larger batches
    flush_interval=10.0, # Less frequent flushes
    max_retries=5        # More retries for rate limits
)
```

### 4. Connection Timeouts

**Symptoms**: Logs mention timeout errors

**Possible Causes**:
- Slow network connection
- Datadog API responding slowly
- Timeout settings too aggressive

**Solutions**:

```python
# Increase timeout settings
handler = DatadogHTTPHandler(
    api_key="your-api-key",
    timeout=60.0,        # Longer timeout
    max_retries=3        # Retry on timeout
)
```

### 5. Logs Not Formatted Correctly

**Symptoms**: Logs appear in Datadog but without expected structure

**Possible Causes**:
- Missing log formatter
- Incorrect extra fields
- Handler not configured properly

**Solutions**:

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Set up proper formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

handler = DatadogHTTPHandler(api_key="your-api-key")
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Use structured logging
logger.info("User action", extra={
    'user_id': 123,
    'action': 'login',
    'success': True
})
```

## Debugging Tips

### 1. Enable Debug Logging

Add this to see internal handler behavior:

```python
import logging

# Enable debug logging for the handler
logging.getLogger('datadog_http_handler').setLevel(logging.DEBUG)

# Enable debug logging for your application
logging.basicConfig(level=logging.DEBUG)
```

### 2. Test Handler Connectivity

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Create a test logger
test_logger = logging.getLogger('test')
test_handler = DatadogHTTPHandler(
    api_key="your-api-key",
    service="connectivity-test",
    batch_size=1,        # Send immediately
    flush_interval=1.0   # Flush quickly
)

test_logger.addHandler(test_handler)
test_logger.setLevel(logging.INFO)

# Send a test message
test_logger.info("Connectivity test message")

# Wait a moment for it to send
import time
time.sleep(3)

# Check your Datadog logs for the test message
```

### 3. Validate Configuration

```python
def validate_handler_config():
    import os
    
    # Check required environment variables
    api_key = os.environ.get('DATADOG_API_KEY')
    if not api_key:
        print("❌ DATADOG_API_KEY not set")
        return False
    
    if len(api_key) < 32:
        print("❌ DATADOG_API_KEY appears to be invalid (too short)")
        return False
    
    print("✅ API key configured")
    
    # Test handler creation
    try:
        handler = DatadogHTTPHandler(api_key=api_key)
        print("✅ Handler created successfully")
        return True
    except Exception as e:
        print(f"❌ Handler creation failed: {e}")
        return False

# Run validation
if validate_handler_config():
    print("Configuration looks good!")
else:
    print("Please fix configuration issues")
```

## Performance Optimization

### 1. Async Context (Future Enhancement)

Currently, the handler uses a background thread. For async applications, consider:

```python
# Current approach - works in any Python app
handler = DatadogHTTPHandler(
    api_key="your-key",
    batch_size=25,
    flush_interval=5.0
)

# For high-performance async apps, you might want to:
# 1. Use larger batch sizes
# 2. Longer flush intervals  
# 3. Consider batching at application level
```

### 2. Memory Management

```python
# For memory-sensitive applications
handler = DatadogHTTPHandler(
    api_key="your-key",
    batch_size=10,       # Smaller batches = less memory
    flush_interval=2.0,  # More frequent flushes
    timeout=15.0         # Don't hold connections too long
)
```

### 3. Network Optimization

```python
# For unreliable networks
handler = DatadogHTTPHandler(
    api_key="your-key",
    max_retries=5,       # More retries
    timeout=30.0,        # Longer timeout
    batch_size=20        # Moderate batch size
)

# For fast, reliable networks  
handler = DatadogHTTPHandler(
    api_key="your-key",
    max_retries=2,       # Fewer retries needed
    timeout=10.0,        # Shorter timeout
    batch_size=50        # Larger batches
)
```

## Getting Help

### 1. Check GitHub Issues

Visit the [GitHub Issues](https://github.com/enlyft/datadog-http-handler/issues) page to:
- Search for existing solutions
- Report new bugs
- Request features

### 2. Enable Verbose Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable debug for the handler specifically
handler_logger = logging.getLogger('datadog_http_handler')
handler_logger.setLevel(logging.DEBUG)
```

### 3. Minimal Reproduction

When reporting issues, provide a minimal example:

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

# Minimal test case
logger = logging.getLogger(__name__)
handler = DatadogHTTPHandler(api_key="test-key")
logger.addHandler(handler)

# Your specific issue case
logger.info("This doesn't work as expected")
```

### 4. Environment Information

Include this information when reporting issues:

```python
import sys
import platform
import datadog_http_handler

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Handler version: {datadog_http_handler.__version__}")
```