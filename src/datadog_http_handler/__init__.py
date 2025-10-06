"""
Datadog HTTP Handler - Modern Python logging handler for Datadog.

This package provides a high-performance, asynchronous logging handler that sends
logs directly to Datadog's HTTP intake API with batching, retry logic, and
comprehensive error handling.

Example:
    Basic usage:

    >>> import logging
    >>> from datadog_http_handler import DatadogHTTPHandler
    >>>
    >>> handler = DatadogHTTPHandler(
    ...     api_key="your-api-key",
    ...     service="my-app",
    ...     tags="env:production"
    ... )
    >>> logger = logging.getLogger(__name__)
    >>> logger.addHandler(handler)
    >>> logger.info("Hello Datadog!")
"""

from .handler import DatadogHTTPHandler

__version__ = "0.1.0"
__all__ = ["DatadogHTTPHandler", "DatadogJsonFormatter"]
