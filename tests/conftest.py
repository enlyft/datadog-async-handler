"""Test configuration for datadog-http-handler."""

import os
from unittest.mock import Mock

import pytest

# Set environment variables for testing
os.environ["DD_API_KEY"] = "test-api-key"
os.environ["DD_SERVICE"] = "test-service"
os.environ["DD_ENV"] = "test"


@pytest.fixture
def mock_datadog_api():
    """Mock the Datadog API client."""
    with pytest.mock.patch("datadog_http_handler.handler.ApiClient") as mock_client:
        mock_logs_api = Mock()
        mock_client.return_value.logs_api = mock_logs_api
        yield mock_logs_api


@pytest.fixture
def sample_log_record():
    """Create a sample log record for testing."""
    import logging

    return logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="/path/to/file.py",
        lineno=123,
        msg="Test log message with %s",
        args=("parameter",),
        exc_info=None,
    )


@pytest.fixture
def handler_config():
    """Default handler configuration for tests."""
    return {
        "api_key": "test-api-key",
        "service": "test-service",
        "source": "test",
        "batch_size": 5,
        "flush_interval_seconds": 1.0,
        "max_retries": 2,
    }
