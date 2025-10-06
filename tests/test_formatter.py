"""Unit tests for DatadogJsonFormatter."""

import json
import logging
import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from datadog_http_handler.formatter import DatadogJsonFormatter


class TestDatadogJsonFormatter:
    """Test suite for DatadogJsonFormatter."""

    def test_init_with_service_name(self):
        """Test formatter initialization with service name."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        assert formatter.service_name == "test-service"
        assert formatter.version == "unknown"  # default when no env var
        assert formatter.environment == "development"  # default when no DD_ENV

    def test_init_with_version(self):
        """Test formatter initialization with version."""
        formatter = DatadogJsonFormatter(service_name="test-service", version="1.0.0")

        assert formatter.service_name == "test-service"
        assert formatter.version == "1.0.0"

    @patch.dict(os.environ, {"SERVICE_VERSION": "2.0.0", "DD_ENV": "production"})
    def test_init_with_environment_variables(self):
        """Test formatter initialization with environment variables."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        assert formatter.service_name == "test-service"
        assert formatter.version == "2.0.0"
        assert formatter.environment == "production"

    def test_basic_log_formatting(self):
        """Test basic log record formatting."""
        formatter = DatadogJsonFormatter(service_name="test-service", version="1.0.0")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345

        result = formatter.format(record)
        log_data = json.loads(result)

        # Check required fields
        assert "timestamp" in log_data
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert log_data["service"] == "test-service"
        assert log_data["version"] == "1.0.0"
        assert log_data["env"] == "development"
        assert log_data["process_id"] == 12345

        # Check source info
        assert "source" in log_data
        assert log_data["source"]["file"] == "/path/to/file.py"
        assert log_data["source"]["line"] == 123
        assert log_data["source"]["function"] == "<unknown>"

    def test_log_with_parameters(self):
        """Test log formatting with message parameters."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="/path/to/file.py",
            lineno=456,
            msg="Test message with %s and %d",
            args=("parameter", 42),
            exc_info=None,
        )
        record.process = 12345

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["message"] == "Test message with parameter and 42"
        assert log_data["level"] == "WARNING"

    def test_log_with_nested_dd_fields(self):
        """Test log formatting with nested Datadog fields."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        record.dd = {
            "trace_id": "123456789",
            "span_id": "987654321",
            "service": "traced-service",
            "version": "2.0.0",
            "env": "staging"
        }

        result = formatter.format(record)
        log_data = json.loads(result)

        # Check Datadog correlation IDs are at top level
        assert log_data["dd.trace_id"] == "123456789"
        assert log_data["dd.span_id"] == "987654321"
        assert log_data["dd.service"] == "traced-service"
        assert log_data["dd.version"] == "2.0.0"
        assert log_data["dd.env"] == "staging"

    def test_log_with_flat_dd_attributes(self):
        """Test log formatting with flat Datadog attributes."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        # Simulate ddtrace injecting flat attributes
        setattr(record, "dd.trace_id", "flat-trace-123")
        setattr(record, "dd.span_id", "flat-span-456")

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["dd.trace_id"] == "flat-trace-123"
        assert log_data["dd.span_id"] == "flat-span-456"

    def test_nested_dd_takes_precedence_over_flat(self):
        """Test that nested dd fields take precedence over flat attributes."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345

        # Add both nested and flat
        record.dd = {"trace_id": "nested-trace-123"}
        setattr(record, "dd.trace_id", "flat-trace-456")

        result = formatter.format(record)
        log_data = json.loads(result)

        # Nested should win
        assert log_data["dd.trace_id"] == "nested-trace-123"

    def test_log_with_extra_fields(self):
        """Test log formatting with extra fields."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        record.user_id = "user123"
        record.request_id = "req456"
        record.custom_field = {"nested": "value"}

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "extra" in log_data
        assert log_data["extra"]["user_id"] == "user123"
        assert log_data["extra"]["request_id"] == "req456"
        assert log_data["extra"]["custom_field"] == {"nested": "value"}

    def test_log_with_exception(self):
        """Test log formatting with exception info."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="/path/to/file.py",
                lineno=123,
                msg="Error occurred",
                args=(),
                exc_info=True,
            )
            record.process = 12345
            record.exc_info = (ValueError, ValueError("Test exception"), None)

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "exception" in log_data
        assert log_data["exception"]["class"] == "ValueError"
        assert log_data["exception"]["message"] == "Test exception"
        assert "traceback" in log_data["exception"]

    def test_log_with_stack_info(self):
        """Test log formatting with stack info."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        record.stack_info = "Stack trace info here"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["stack_trace"] == "Stack trace info here"

    def test_no_source_info_when_no_pathname(self):
        """Test that source info is not added when pathname is not available."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname=None,
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "source" not in log_data

    def test_timestamp_format(self):
        """Test that timestamp is in ISO format with UTC timezone."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        # Create record with specific timestamp
        test_time = 1609459200.0  # 2021-01-01 00:00:00 UTC
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        record.created = test_time

        result = formatter.format(record)
        log_data = json.loads(result)

        # Check timestamp format
        expected_timestamp = datetime.fromtimestamp(test_time, tz=timezone.utc).isoformat()
        assert log_data["timestamp"] == expected_timestamp
        assert log_data["timestamp"].endswith("+00:00")

    def test_json_serialization_with_non_serializable_objects(self):
        """Test that non-JSON serializable objects are handled gracefully."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345
        record.datetime_obj = datetime.now()
        record.set_obj = {1, 2, 3}

        result = formatter.format(record)
        log_data = json.loads(result)

        # Should not raise exception and objects should be converted to strings
        assert "extra" in log_data
        assert "datetime_obj" in log_data["extra"]
        assert "set_obj" in log_data["extra"]

    def test_exclude_standard_log_fields_from_extra(self):
        """Test that standard logging fields are excluded from extra."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345

        result = formatter.format(record)
        log_data = json.loads(result)

        # Standard fields should not appear in extra
        if "extra" in log_data:
            standard_fields = {
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "getMessage",
                "exc_info", "exc_text", "stack_info", "message"
            }
            for field in standard_fields:
                assert field not in log_data["extra"]

    def test_empty_extra_fields_not_included(self):
        """Test that empty extra fields are not included in output."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345

        result = formatter.format(record)
        log_data = json.loads(result)

        # No extra fields should mean no extra key
        assert "extra" not in log_data

    @patch.dict(os.environ, {"DD_ENV": "test-env"})
    def test_environment_from_dd_env(self):
        """Test that environment is read from DD_ENV."""
        formatter = DatadogJsonFormatter(service_name="test-service")

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.process = 12345

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["env"] == "test-env"
