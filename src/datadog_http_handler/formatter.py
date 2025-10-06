import json
import logging
import os
from typing import Optional
from datetime import datetime, timezone


class DatadogJsonFormatter(logging.Formatter):
    """
    JSON formatter optimized for Datadog log ingestion.

    This formatter creates structured JSON logs with fields that Datadog
    can automatically parse and index for better searchability and analysis.
    """

    def __init__(self, service_name: str, version: Optional[str] = None):
        """
        Initialize the formatter.

        Args:
            service_name: Name of the service (e.g., 'auth-service', 'embedding-service')
            version: Version of the service (optional)
        """
        super().__init__()
        self.service_name = service_name
        self.version = version or os.getenv("SERVICE_VERSION", "unknown")
        self.environment = os.getenv("DD_ENV", "development")

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log string
        """
        # Base log structure for Datadog
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "version": self.version,
            "env": self.environment,
            "process_id": record.process,
        }

        # --- Datadog correlation IDs (must be at top level) ---
        # First check nested dd fields
        if hasattr(record, "dd"):
            dd_fields = record.dd
            if "trace_id" in dd_fields:
                log_entry["dd.trace_id"] = dd_fields["trace_id"]
            if "span_id" in dd_fields:
                log_entry["dd.span_id"] = dd_fields["span_id"]
            if "service" in dd_fields:
                log_entry["dd.service"] = dd_fields["service"]
            if "version" in dd_fields:
                log_entry["dd.version"] = dd_fields["version"]
            if "env" in dd_fields:
                log_entry["dd.env"] = dd_fields["env"]

        # Then check for flat Datadog attributes that ddtrace may inject
        dd_flat_keys = ["dd.trace_id", "dd.span_id", "dd.service", "dd.version", "dd.env"]
        for dd_key in dd_flat_keys:
            # Only use flat key if we don't already have this field from record.dd
            if dd_key not in log_entry and hasattr(record, dd_key):
                log_entry[dd_key] = getattr(record, dd_key)

        # --- Add source info ---
        if record.pathname:
            log_entry["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # --- Collect remaining extras, except dd (already flattened) ---
        extra_fields = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "message",
                "dd",  # skip dd because we handled it
                "dd.trace_id",  # skip flat dd keys because we handled them
                "dd.span_id",
                "dd.service",
                "dd.version",
                "dd.env",
            }
        }
        if extra_fields:
            log_entry["extra"] = extra_fields

        # --- Exception handling ---
        if record.exc_info:
            log_entry["exception"] = {
                "class": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        if record.stack_info:
            log_entry["stack_trace"] = record.stack_info

        return json.dumps(log_entry, default=str, ensure_ascii=False)

