"""Main FastAPI application."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from mindbridge.__about__ import __description__, __title__, __version__
from mindbridge.api.health import router as health_router
from mindbridge.api.metrics import router as metrics_router
from mindbridge.observability.logging_config import configure_logging, get_logger
from mindbridge.observability.tracing import configure_tracing


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events.

    Args:
        _app: FastAPI application instance (unused).

    Yields:
        None during application runtime.
    """
    # Configure observability first
    configure_logging(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_format=os.getenv("LOG_FORMAT", "console"),
    )
    configure_tracing(service_name="mindbridge")

    # Get logger after configuration
    logger = get_logger(__name__)

    # Startup
    logger.info("Starting Mindbridge application")
    logger.info("Observability configured")

    yield

    # Shutdown
    logger.info("Shutting down Mindbridge application")


# Create FastAPI application
app = FastAPI(
    title=__title__,
    description=__description__,
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS")
if not origins:
    raise RuntimeError("ALLOWED_ORIGINS environment variable must be set for security")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Include routers
app.include_router(health_router)
app.include_router(metrics_router)


@app.get("/", tags=["root"])
async def root() -> dict[str, Any]:
    """Root endpoint providing API information.

    Returns:
        API information including name, version, and description.
    """
    logger = get_logger(__name__)
    logger.info("Root endpoint accessed")

    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "status": "running",
    }
