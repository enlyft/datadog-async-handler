# Usage Examples

## Django

### Basic Setup

Add the handler to your Django logging configuration:

```python
# settings.py
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'datadog': {
            'class': 'datadog_http_handler.DatadogHTTPHandler',
            'api_key': os.environ['DATADOG_API_KEY'],
            'service': 'my-django-app',
            'environment': os.environ.get('DJANGO_ENV', 'production'),
            'tags': 'framework:django,component:web',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['datadog'],
            'level': 'INFO',
            'propagate': True,
        },
        'myapp': {
            'handlers': ['datadog'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Using in Views

```python
# views.py
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    logger.info("Processing request", extra={
        'user_id': request.user.id,
        'request_path': request.path,
        'method': request.method
    })
    
    try:
        # Your view logic here
        result = process_data()
        logger.info("Request processed successfully")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error("Error processing request", extra={
            'error': str(e),
            'user_id': request.user.id
        })
        return JsonResponse({'status': 'error'}, status=500)
```

## FastAPI

### Basic Setup

```python
# main.py
import logging
import os
from fastapi import FastAPI
from datadog_http_handler import DatadogHTTPHandler

app = FastAPI()

# Configure logging
logger = logging.getLogger(__name__)
handler = DatadogHTTPHandler(
    api_key=os.environ["DATADOG_API_KEY"],
    service="my-fastapi-app", 
    environment="production",
    tags="framework:fastapi,component:api"
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info("Request received", extra={
        'method': request.method,
        'url': str(request.url),
        'client_ip': request.client.host
    })
    
    response = await call_next(request)
    
    logger.info("Request completed", extra={
        'status_code': response.status_code,
        'method': request.method,
        'url': str(request.url)
    })
    
    return response

@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    logger.info("Item requested", extra={'item_id': item_id})
    return {"item_id": item_id}
```

### Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    try:
        item = fetch_item(item_id)
        logger.info("Item fetched successfully", extra={
            'item_id': item_id,
            'item_name': item.name
        })
        return item
    except ItemNotFound:
        logger.warning("Item not found", extra={'item_id': item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error("Unexpected error fetching item", extra={
            'item_id': item_id,
            'error': str(e)
        })
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Flask

### Basic Setup

```python
# app.py
import logging
import os
from flask import Flask, request, jsonify
from datadog_http_handler import DatadogHTTPHandler

app = Flask(__name__)

# Configure logging
logger = logging.getLogger(__name__)
handler = DatadogHTTPHandler(
    api_key=os.environ["DATADOG_API_KEY"],
    service="my-flask-app",
    environment="production", 
    tags="framework:flask,component:web"
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@app.before_request
def log_request_info():
    logger.info("Request started", extra={
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    })

@app.after_request
def log_response_info(response):
    logger.info("Request completed", extra={
        'status_code': response.status_code,
        'method': request.method,
        'url': request.url
    })
    return response

@app.route('/')
def hello():
    logger.info("Hello endpoint accessed")
    return jsonify({'message': 'Hello World'})

@app.route('/users/<int:user_id>')
def get_user(user_id):
    logger.info("User requested", extra={'user_id': user_id})
    # Your logic here
    return jsonify({'user_id': user_id})
```

### Error Handling

```python
@app.errorhandler(404)
def not_found(error):
    logger.warning("404 error", extra={
        'url': request.url,
        'method': request.method
    })
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error("500 error", extra={
        'url': request.url,
        'method': request.method,
        'error': str(error)
    })
    return jsonify({'error': 'Internal server error'}), 500
```

## Celery

### Task Logging

```python
# tasks.py
import logging
import os
from celery import Celery
from datadog_http_handler import DatadogHTTPHandler

app = Celery('myapp')

# Configure logging for Celery
logger = logging.getLogger(__name__)
handler = DatadogHTTPHandler(
    api_key=os.environ["DATADOG_API_KEY"],
    service="my-celery-worker",
    environment="production",
    tags="framework:celery,component:worker"
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@app.task
def process_data(data_id):
    logger.info("Task started", extra={
        'task_id': process_data.request.id,
        'data_id': data_id
    })
    
    try:
        # Process data
        result = heavy_computation(data_id)
        
        logger.info("Task completed successfully", extra={
            'task_id': process_data.request.id,
            'data_id': data_id,
            'result_size': len(result)
        })
        
        return result
        
    except Exception as e:
        logger.error("Task failed", extra={
            'task_id': process_data.request.id,
            'data_id': data_id,
            'error': str(e)
        })
        raise

@app.task
def send_email(email_id):
    logger.info("Email task started", extra={
        'task_id': send_email.request.id,
        'email_id': email_id
    })
    
    # Send email logic
    success = send_email_logic(email_id)
    
    if success:
        logger.info("Email sent successfully", extra={
            'email_id': email_id
        })
    else:
        logger.error("Email failed to send", extra={
            'email_id': email_id
        })
```

## Structured Logging

### Adding Context

```python
import logging
from datadog_http_handler import DatadogHTTPHandler

logger = logging.getLogger(__name__)
handler = DatadogHTTPHandler(api_key="your-key")
logger.addHandler(handler)

def process_user_order(user_id, order_id):
    # Create logger with context
    order_logger = logging.LoggerAdapter(logger, {
        'user_id': user_id,
        'order_id': order_id
    })
    
    order_logger.info("Processing order")
    
    try:
        # Process order
        order_logger.info("Order validated")
        charge_payment(user_id, order_id)
        order_logger.info("Payment processed")
        send_confirmation(user_id, order_id)
        order_logger.info("Order completed successfully")
        
    except PaymentError as e:
        order_logger.error("Payment failed", extra={'error': str(e)})
        raise
    except Exception as e:
        order_logger.error("Unexpected error", extra={'error': str(e)})
        raise
```

### Custom Fields

```python
def api_request(endpoint, user_id):
    logger.info("API request", extra={
        'endpoint': endpoint,
        'user_id': user_id,
        'request_timestamp': time.time(),
        'session_id': get_session_id(),
        'version': '2.1.0'
    })
```

## Performance Monitoring

### Request Duration

```python
import time
import logging
from datadog_http_handler import DatadogHTTPHandler

logger = logging.getLogger(__name__)
handler = DatadogHTTPHandler(api_key="your-key")
logger.addHandler(handler)

def timed_operation(operation_name):
    start_time = time.time()
    
    try:
        # Your operation here
        result = expensive_operation()
        
        duration = time.time() - start_time
        logger.info("Operation completed", extra={
            'operation': operation_name,
            'duration_ms': duration * 1000,
            'status': 'success'
        })
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error("Operation failed", extra={
            'operation': operation_name,
            'duration_ms': duration * 1000,
            'status': 'error',
            'error': str(e)
        })
        raise
```