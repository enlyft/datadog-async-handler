"""Basic usage example for datadog-async-handler."""

import logging
import os

from datadog_http_handler import DatadogHTTPHandler

# Configure environment variables (or set them in your environment)
os.environ["DD_API_KEY"] = "your-datadog-api-key-here"
os.environ["DD_SERVICE"] = "example-app"
os.environ["DD_ENV"] = "development"
os.environ["DD_VERSION"] = "1.0.0"


def main():
    """Demonstrate basic usage of the Datadog HTTP handler."""
    # Create the handler
    handler = DatadogHTTPHandler(
        service="example-app",
        source="python",
        tags="component:example,team:engineering",
        batch_size=5,
        flush_interval_seconds=2.0,
    )

    # Set up logging
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Add a console handler for local debugging
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Log some messages
    logger.info("Application starting up")
    logger.info("User logged in", extra={"user_id": "12345", "action": "login"})
    logger.warning("Rate limit approaching", extra={"current_rate": 85, "limit": 100})
    logger.error(
        "Database connection failed", extra={"db_host": "localhost", "retry_count": 3}
    )

    # Log with custom Datadog fields
    logger.info(
        "Order processed successfully",
        extra={
            "dd_order_id": "order-12345",
            "dd_customer_tier": "premium",
            "dd_amount": 99.99,
        },
    )

    print("Logs sent to Datadog! Check your Datadog Logs dashboard.")

    # Important: Close the handler to ensure all logs are sent
    handler.close()


if __name__ == "__main__":
    main()
