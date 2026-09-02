"""Unit tests for DatadogHTTPHandler."""

import logging
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from datadog_http_handler import DatadogHTTPHandler


class TestDatadogHTTPHandler:
    """Test suite for DatadogHTTPHandler."""

    def test_init_with_api_key(self, handler_config):
        """Test handler initialization with API key."""
        handler = DatadogHTTPHandler(**handler_config)

        assert handler.api_key == "test-api-key"
        assert handler.service == "test-service"
        assert handler.source == "test"
        assert handler.batch_size == 5
        assert handler.flush_interval == 1.0
        assert handler.max_retries == 2

    def test_init_without_api_key(self):
        """Test handler initialization fails without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Datadog API key is required"):
                DatadogHTTPHandler()

    @patch("datadog_http_handler.handler.ApiClient")
    @patch("datadog_http_handler.handler.LogsApi")
    def test_setup_api_client(self, mock_logs_api, mock_api_client, handler_config):
        """Test API client setup."""
        handler = DatadogHTTPHandler(**handler_config)

        mock_api_client.assert_called_once()
        assert hasattr(handler, "api_client")
        assert hasattr(handler, "logs_api")

    @patch("datadog_http_handler.handler.ApiClient")
    def test_worker_thread_starts(self, mock_api_client, handler_config):
        """Test that worker thread starts automatically."""
        handler = DatadogHTTPHandler(**handler_config)

        assert handler._worker_thread is not None
        assert handler._worker_thread.is_alive()
        assert handler._worker_thread.daemon

    @patch("datadog_http_handler.handler.ApiClient")
    def test_emit_log_record(self, mock_api_client, handler_config, sample_log_record):
        """Test emitting a log record."""
        handler = DatadogHTTPHandler(**handler_config)

        # Emit a log record
        handler.emit(sample_log_record)

        # Check that log was added to queue
        assert handler.get_queue_size() > 0

    @patch("datadog_http_handler.handler.ApiClient")
    def test_format_log_item(self, mock_api_client, handler_config, sample_log_record):
        """Test log item formatting."""
        handler = DatadogHTTPHandler(**handler_config)

        log_item = handler._format_log_item(sample_log_record)

        assert log_item.message == "Test log message with parameter"
        assert log_item.ddsource == "test"
        assert log_item.service == "test-service"
        assert "level:info" in log_item.ddtags
        assert "logger:test.logger" in log_item.ddtags

    @patch("datadog_http_handler.handler.ApiClient")
    def test_format_log_item_with_env_vars(
        self, mock_api_client, handler_config, sample_log_record
    ):
        """Test log item formatting with environment variables."""
        with patch.dict("os.environ", {"DD_ENV": "production", "DD_VERSION": "1.0.0"}):
            handler = DatadogHTTPHandler(**handler_config)
            log_item = handler._format_log_item(sample_log_record)

            assert "env:production" in log_item.ddtags
            assert "version:1.0.0" in log_item.ddtags

    @patch("datadog_http_handler.handler.ApiClient")
    def test_batch_sending(self, mock_api_client, handler_config):
        """Test batch sending functionality."""
        mock_logs_api = MagicMock()
        mock_api_client.return_value = MagicMock()

        with patch.object(DatadogHTTPHandler, "_setup_api_client"):
            handler = DatadogHTTPHandler(**handler_config)
            handler.logs_api = mock_logs_api

            # Create mock log items
            mock_log_items = [MagicMock() for _ in range(3)]

            # Test batch sending
            handler._send_batch(mock_log_items)

            # Verify API was called
            mock_logs_api.submit_log.assert_called_once()

    @patch("datadog_http_handler.handler.ApiClient")
    def test_batch_sending_with_retry(self, mock_api_client, handler_config):
        """Test batch sending with retry logic."""
        mock_logs_api = MagicMock()
        mock_logs_api.submit_log.side_effect = [Exception("Network error"), None]

        with patch.object(DatadogHTTPHandler, "_setup_api_client"):
            handler = DatadogHTTPHandler(**handler_config)
            handler.logs_api = mock_logs_api

            # Create mock log items
            mock_log_items = [MagicMock() for _ in range(3)]

            # Test batch sending with retry
            with patch("time.sleep"):  # Speed up test
                handler._send_batch(mock_log_items)

            # Verify API was called twice (original + 1 retry)
            assert mock_logs_api.submit_log.call_count == 2

    @patch("datadog_http_handler.handler.ApiClient")
    def test_health_check(self, mock_api_client, handler_config):
        """Test health check functionality."""
        handler = DatadogHTTPHandler(**handler_config)

        # Should be healthy when properly initialized
        assert handler.health_check() is True

    @patch("datadog_http_handler.handler.ApiClient")
    def test_close_handler(self, mock_api_client, handler_config):
        """Test handler cleanup."""
        handler = DatadogHTTPHandler(**handler_config)

        # Close the handler
        handler.close()

        # Check that stop event is set
        assert handler._stop_event.is_set()

    @patch("datadog_http_handler.handler.ApiClient")
    def test_queue_size_tracking(
        self, mock_api_client, handler_config, sample_log_record
    ):
        """Test queue size tracking."""
        handler = DatadogHTTPHandler(**handler_config)

        initial_size = handler.get_queue_size()
        assert initial_size == 0

        # Add a log record
        handler.emit(sample_log_record)

        # Queue size should increase
        assert handler.get_queue_size() > initial_size

    @patch("datadog_http_handler.handler.ApiClient")
    def test_repr(self, mock_api_client, handler_config):
        """Test string representation."""
        handler = DatadogHTTPHandler(**handler_config)

        repr_str = repr(handler)
        assert "DatadogHTTPHandler" in repr_str
        assert "test-service" in repr_str
        assert "test" in repr_str

    @patch("datadog_http_handler.handler.ApiClient")
    def test_flush(self, mock_api_client, handler_config):
        """Test flush functionality."""
        handler = DatadogHTTPHandler(**handler_config)

        # Should not raise an exception
        handler.flush()

    @patch("datadog_http_handler.handler.ApiClient")
    def test_error_handling(self, mock_api_client, handler_config):
        """Test error handling during emission."""
        handler = DatadogHTTPHandler(**handler_config)

        # Create a problematic log record
        bad_record = Mock()
        bad_record.getMessage.side_effect = Exception("Format error")

        # Should not raise exception, but handle gracefully
        with patch.object(handler, "handleError") as mock_handle_error:
            handler.emit(bad_record)
            # Error handling should be triggered
            # (The exact behavior depends on the implementation)


class TestDatadogHTTPHandlerIntegration:
    """Integration tests for DatadogHTTPHandler."""

    @patch("datadog_http_handler.handler.ApiClient")
    @pytest.mark.slow
    def test_full_logging_workflow(self, mock_api_client, handler_config):
        """Test complete logging workflow."""
        mock_logs_api = MagicMock()

        with patch.object(DatadogHTTPHandler, "_setup_api_client"):
            handler = DatadogHTTPHandler(**handler_config)
            handler.logs_api = mock_logs_api

            # Set up logger
            logger = logging.getLogger("test_integration")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            # Log several messages
            for i in range(10):
                logger.info(f"Test message {i}", extra={"request_id": f"req-{i}"})

            # Allow time for batching
            time.sleep(2.0)

            # Verify logs were sent
            assert mock_logs_api.submit_log.call_count > 0

    @patch("datadog_http_handler.handler.ApiClient")
    def test_batch_size_triggering(self, mock_api_client, handler_config):
        """Test that batch size triggers sending."""
        mock_logs_api = MagicMock()
        handler_config["batch_size"] = 3  # Small batch for testing

        with patch.object(DatadogHTTPHandler, "_setup_api_client"):
            handler = DatadogHTTPHandler(**handler_config)
            handler.logs_api = mock_logs_api

            # Send exactly batch_size logs
            logger = logging.getLogger("test_batch")
            logger.addHandler(handler)

            for i in range(3):
                logger.info(f"Batch test {i}")

            # Allow processing time
            time.sleep(0.5)

            # Should have triggered at least one batch send
            assert mock_logs_api.submit_log.call_count >= 1


class TestForkSafety:
    """A process that forks while the worker thread is inside a TLS flush hands the
    child OpenSSL state mid-update; the child then deadlocks on its own first TLS
    handshake. fork() must be serialized against in-flight sends, and the child must
    get a fresh worker."""

    @pytest.fixture
    def handler(self, handler_config):
        with patch.object(DatadogHTTPHandler, "_setup_api_client"):
            handler = DatadogHTTPHandler(**handler_config)
        handler.logs_api = MagicMock()
        try:
            yield handler
        finally:
            handler.close()

    def test_registers_at_fork_hooks(self, handler_config):
        with (
            patch.object(DatadogHTTPHandler, "_setup_api_client"),
            patch("datadog_http_handler.handler.os.register_at_fork") as register,
        ):
            handler = DatadogHTTPHandler(**handler_config)
            try:
                register.assert_called_once()
                assert set(register.call_args.kwargs) == {
                    "before",
                    "after_in_parent",
                    "after_in_child",
                }
            finally:
                handler.close()

    def test_worker_thread_is_named(self, handler):
        assert handler._worker_thread.name == "datadog-http-handler"

    def test_before_fork_waits_for_inflight_send(self, handler):
        started, release = threading.Event(), threading.Event()

        def blocking_submit(body):
            started.set()
            release.wait(5)

        handler.logs_api.submit_log.side_effect = blocking_submit
        sender = threading.Thread(target=handler._send_batch, args=([MagicMock()],))
        sender.start()
        assert started.wait(2)

        hook = threading.Thread(target=handler._before_fork)
        hook.start()
        hook.join(0.3)
        assert hook.is_alive(), "fork() proceeded while a TLS flush was in flight"

        release.set()
        hook.join(2)
        sender.join(2)
        assert not hook.is_alive()
        assert handler._send_lock.locked(), "parent must hold the lock across fork()"
        handler._after_fork_in_parent()
        assert not handler._send_lock.locked()

    def test_before_fork_does_not_hold_lock_across_retry_backoff(self, handler):
        """Only the network attempt is locked, so fork() may proceed during back-off."""
        in_backoff = threading.Event()
        handler.logs_api.submit_log.side_effect = Exception("boom")

        def slow_backoff(_seconds: float) -> None:
            in_backoff.set()
            time.sleep(0.3)

        with patch("datadog_http_handler.handler.time.sleep", side_effect=slow_backoff):
            sender = threading.Thread(target=handler._send_batch, args=([MagicMock()],))
            sender.start()
            assert in_backoff.wait(2)
            assert not handler._send_lock.locked()
            sender.join(5)

    def test_before_fork_is_bounded_when_send_is_wedged(self, handler):
        never = threading.Event()
        handler.logs_api.submit_log.side_effect = lambda body: never.wait(30)
        sender = threading.Thread(
            target=handler._send_batch, args=([MagicMock()],), daemon=True
        )
        sender.start()
        time.sleep(0.05)

        with patch.object(DatadogHTTPHandler, "_FORK_WAIT_SECONDS", 0.2):
            t0 = time.monotonic()
            handler._before_fork()
            elapsed = time.monotonic() - t0

        assert elapsed < 2, (
            "a worker wedged in C must not freeze the parent's fork forever"
        )
        handler._after_fork_in_parent()  # never acquired: must not raise
        never.set()

    def test_after_fork_in_child_replaces_queue_lock_and_worker(self, handler):
        old_thread, old_queue, old_lock = (
            handler._worker_thread,
            handler._log_queue,
            handler._send_lock,
        )
        handler._send_lock.acquire()  # the lock the child inherits from the parent is held

        handler._after_fork_in_child()

        assert handler._send_lock is not old_lock
        assert not handler._send_lock.locked()
        assert handler._log_queue is not old_queue
        assert handler._log_queue.empty()
        assert handler._worker_thread is not old_thread
        assert handler._worker_thread.is_alive()
