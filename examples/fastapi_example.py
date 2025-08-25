"""FastAPI integration example for datadog-async-handler."""

import logging
import os
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException
except ImportError:
    print("FastAPI not installed. Install with: pip install fastapi uvicorn")
    exit(1)

from datadog_http_handler import DatadogHTTPHandler

# Configure Datadog
os.environ.setdefault("DD_SERVICE", "fastapi-example")
os.environ.setdefault("DD_ENV", "development")

# Global logger
logger = logging.getLogger("fastapi_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    handler = DatadogHTTPHandler(
        service="fastapi-example",
        source="fastapi",
        tags="framework:fastapi,component:api",
    )

    # Configure logging
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Add console logging for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)

    logger.info("FastAPI application starting up")

    yield

    # Shutdown
    logger.info("FastAPI application shutting down")
    handler.close()


# Create FastAPI app
app = FastAPI(
    title="Datadog Logging Example",
    description="Example FastAPI app with Datadog HTTP logging",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
        },
    )

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
        },
    )

    return response


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "Hello World!", "service": "fastapi-example"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID."""
    logger.info("User lookup requested", extra={"user_id": user_id})

    if user_id <= 0:
        logger.warning("Invalid user ID provided", extra={"user_id": user_id})
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Simulate user lookup
    user_data = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
    }

    logger.info("User lookup successful", extra={"user_id": user_id})
    return user_data


@app.post("/orders")
async def create_order(order_data: dict):
    """Create a new order."""
    logger.info("Order creation requested", extra={"order_data": order_data})

    try:
        # Simulate order processing
        order_id = "order-12345"

        logger.info(
            "Order created successfully",
            extra={
                "dd_order_id": order_id,
                "dd_customer_id": order_data.get("customer_id"),
                "dd_amount": order_data.get("amount", 0),
            },
        )

        return {"order_id": order_id, "status": "created"}

    except Exception as e:
        logger.error(
            "Order creation failed",
            extra={"error": str(e), "order_data": order_data},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Order creation failed") from e


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "fastapi-example"}


if __name__ == "__main__":
    import time

    import uvicorn

    # Run the server
    logger.info("Starting FastAPI server")
    uvicorn.run(
        "fastapi_example:app", host="0.0.0.0", port=8000, log_level="info", reload=True
    )
