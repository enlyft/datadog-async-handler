"""
Datadog HTTP logging handler implementation.

This module provides the DatadogHTTPHandler class, a modern Python logging handler
that sends logs to Datadog via HTTP API with asynchronous batching and retry logic.
"""

import logging
import os
import threading
import time
from queue import Empty, Queue
from typing import Optional

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem


class DatadogHTTPHandler(logging.Handler):
    """
    High-performance logging handler that sends logs to Datadog via HTTP API.

    This handler batches logs and sends them asynchronously to avoid blocking
    the main application thread. It includes retry logic with exponential backoff,
    comprehensive error handling, and support for all Datadog sites.

    Args:
        api_key: Datadog API key (or set DD_API_KEY env var)
        site: Datadog site (default: datadoghq.com)
        service: Service name for logs
        source: Log source (default: python)
        hostname: Hostname for logs
        tags: Tags to add to logs (comma-separated string)
        batch_size: Number of logs to batch before sending
        flush_interval_seconds: How often to flush logs (seconds)
        timeout_seconds: Request timeout
        max_retries: Maximum retry attempts
        level: Logging level

    Example:
        Basic usage:

        >>> import logging
        >>> handler = DatadogHTTPHandler(
        ...     api_key="your-api-key",
        ...     service="my-app",
        ...     tags="env:production,team:backend"
        ... )
        >>> logger = logging.getLogger(__name__)
        >>> logger.addHandler(handler)
        >>> logger.info("Application started")

        With environment variables:

        >>> # Set DD_API_KEY, DD_SERVICE, DD_ENV, etc.
        >>> handler = DatadogHTTPHandler()  # Uses env vars
        >>> logger = logging.getLogger(__name__)
        >>> logger.addHandler(handler)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        site: str = "datadoghq.com",
        service: Optional[str] = None,
        source: str = "python",
        hostname: Optional[str] = None,
        tags: Optional[str] = None,
        batch_size: int = 10,
        flush_interval_seconds: float = 5.0,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        level: int = logging.NOTSET,
    ) -> None:
        """Initialize the Datadog HTTP handler."""
        super().__init__(level)

        # API Configuration
        self.api_key = api_key or os.getenv("DD_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Datadog API key is required. Set DD_API_KEY env var or pass api_key parameter."
            )

        self.site = site or os.getenv("DD_SITE", "datadoghq.com")
        self.service = service or os.getenv("DD_SERVICE", "unknown")
        self.source = source
        self.hostname = hostname or os.getenv("DD_HOSTNAME")
        self.tags = tags or os.getenv("DD_TAGS", "")

        # Batch settings
        self.batch_size = max(1, batch_size)  # Ensure at least 1
        self.flush_interval = max(0.1, flush_interval_seconds)  # Minimum 100ms
        self.timeout = max(1.0, timeout_seconds)  # Minimum 1 second
        self.max_retries = max(0, max_retries)  # No negative retries

        # Initialize API client
        self._setup_api_client()

        # Background processing
        self._log_queue: Queue[HTTPLogItem] = Queue()
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._start_worker()

    def _setup_api_client(self) -> None:
        """Setup the Datadog API client."""
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = self.api_key
        configuration.server_variables["site"] = self.site

        self.api_client = ApiClient(configuration)
        self.logs_api = LogsApi(self.api_client)

    def _start_worker(self) -> None:
        """Start the background worker thread."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = threading.Thread(target=self._worker, daemon=True)
            self._worker_thread.start()

    def _worker(self) -> None:
        """Background worker that processes log batches."""
        batch: list[HTTPLogItem] = []
        last_flush = time.time()

        while not self._stop_event.is_set():
            try:
                # Get log from queue with timeout
                log_item = self._log_queue.get(timeout=0.1)
                batch.append(log_item)

                # Check if we should flush
                should_flush = len(batch) >= self.batch_size or (
                    batch and time.time() - last_flush >= self.flush_interval
                )

                if should_flush:
                    self._send_batch(batch)
                    batch.clear()
                    last_flush = time.time()

            except Empty:
                # No logs in queue, check if we should flush existing batch
                if batch and time.time() - last_flush >= self.flush_interval:
                    self._send_batch(batch)
                    batch.clear()
                    last_flush = time.time()
                continue

        # Flush remaining logs on shutdown
        if batch:
            self._send_batch(batch)

    def _send_batch(self, batch: list[HTTPLogItem]) -> None:
        """Send a batch of logs to Datadog."""
        if not batch:
            return

        for attempt in range(self.max_retries + 1):
            try:
                http_log = HTTPLog(batch)
                self.logs_api.submit_log(body=http_log)
                return  # Success

            except Exception as e:
                if attempt == self.max_retries:
                    # Last attempt failed, give up
                    self._handle_error(
                        f"Failed to send logs after {self.max_retries + 1} attempts: {e}"
                    )
                else:
                    # Wait before retry (exponential backoff)
                    time.sleep(2**attempt)

    def _handle_error(self, message: str) -> None:
        """Handle errors that occur during log submission."""
        # Log to stderr to avoid infinite recursion
        print(f"DatadogHTTPHandler error: {message}", file=__import__("sys").stderr)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        try:
            # Ensure handler is properly initialized
            if not hasattr(self, "_log_queue") or not hasattr(self, "api_key"):
                # Handler not properly initialized, skip logging to avoid errors
                return

            log_item = self._format_log_item(record)
            self._log_queue.put(log_item, block=False)
        except Exception:
            self.handleError(record)

    def _format_log_item(self, record: logging.LogRecord) -> HTTPLogItem:
        """Convert a LogRecord to a Datadog HTTPLogItem."""
        # Format the message
        message = self.format(record)

        # Build the log item
        log_item = HTTPLogItem(
            message=message,
            ddsource=self.source,
            service=self.service,
            hostname=self.hostname,
        )

        # Add tags
        tags_list = []
        if self.tags:
            tags_list.extend(self.tags.split(","))

        # Add log level as tag
        tags_list.append(f"level:{record.levelname.lower()}")

        # Add logger name as tag
        tags_list.append(f"logger:{record.name}")

        # Add environment if available
        env = os.getenv("DD_ENV")
        if env:
            tags_list.append(f"env:{env}")

        # Add version if available
        version = os.getenv("DD_VERSION")
        if version:
            tags_list.append(f"version:{version}")

        # Add any extra fields from the log record
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key.startswith("dd_") and isinstance(value, (str, int, float, bool)):
                    # Custom Datadog fields
                    tags_list.append(f"{key[3:]}:{value}")

        if tags_list:
            log_item.ddtags = ",".join(tags_list)

        return log_item

    def flush(self) -> None:
        """Flush any pending logs."""
        # Signal worker to process remaining logs
        if (
            hasattr(self, "_worker_thread")
            and self._worker_thread
            and self._worker_thread.is_alive()
        ):
            # Wait a bit for the worker to process
            time.sleep(0.1)

    def close(self) -> None:
        """Close the handler and cleanup resources."""
        # Stop the worker
        if hasattr(self, "_stop_event"):
            self._stop_event.set()

        # Wait for worker to finish
        if (
            hasattr(self, "_worker_thread")
            and self._worker_thread
            and self._worker_thread.is_alive()
        ):
            self._worker_thread.join(timeout=5.0)

        # Close API client
        if hasattr(self, "api_client"):
            self.api_client.close()

        super().close()

    def health_check(self) -> bool:
        """
        Perform a health check to verify the handler is working.

        Returns:
            True if the handler is healthy, False otherwise.
        """
        try:
            # Check if worker thread is alive
            if not self._worker_thread or not self._worker_thread.is_alive():
                return False

            # Check if we can create a test log item
            test_record = logging.LogRecord(
                name="health_check",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Health check",
                args=(),
                exc_info=None,
            )
            self._format_log_item(test_record)
            return True

        except Exception:
            return False

    def get_queue_size(self) -> int:
        """Get the current size of the log queue."""
        return self._log_queue.qsize() if hasattr(self, "_log_queue") else 0

    def __repr__(self) -> str:
        """Return a string representation of the handler."""
        return (
            f"DatadogHTTPHandler(service={self.service!r}, "
            f"source={self.source!r}, site={self.site!r})"
        )
