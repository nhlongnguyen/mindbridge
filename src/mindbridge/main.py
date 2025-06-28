"""Main FastAPI application."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

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
    logger = get_logger(__name__)

    # Startup
    logger.info("Starting Mindbridge application")

    # Configure observability
    configure_logging(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_format=os.getenv("LOG_FORMAT", "console"),
    )
    configure_tracing(service_name="mindbridge")

    logger.info("Observability configured")

    yield

    # Shutdown
    logger.info("Shutting down Mindbridge application")


# Create FastAPI application
app = FastAPI(
    title="Mindbridge",
    description="Agentic RAG Documentation System",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
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
        "name": "Mindbridge",
        "version": "0.1.0",
        "description": "Agentic RAG Documentation System",
        "status": "running",
    }
