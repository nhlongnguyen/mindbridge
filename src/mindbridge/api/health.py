"""Health check API endpoints."""

import asyncio
from datetime import UTC, datetime
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from mindbridge.__about__ import __version__
from mindbridge.database.connection import get_async_engine
from mindbridge.observability.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


class HealthStatus(str, Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class HealthResponse(BaseModel):
    """Health check response model."""

    status: HealthStatus
    timestamp: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    status: HealthStatus
    checks: dict[str, str]


async def check_database_health() -> bool:
    """Check database connectivity and health.

    Returns:
        True if database is healthy, False otherwise.
    """
    try:
        engine = get_async_engine()
        async with engine.get_session() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        logger.exception("Database health check failed")
        return False


async def check_redis_health() -> bool:
    """Check Redis connectivity and health.

    Returns:
        True if Redis is healthy, False otherwise.
    """
    try:
        from mindbridge.cache.redis_cache import get_redis_cache

        cache = get_redis_cache()
        await cache.connect()
        result = await cache.ping()
        await cache.disconnect()
        return result
    except Exception:
        logger.exception("Redis health check failed")
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        Health status response with timestamp and version.
    """
    logger.info("Health check requested")

    return HealthResponse(
        status=HealthStatus.HEALTHY,
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        version=__version__,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """Readiness check endpoint that verifies dependencies.

    Returns:
        Readiness status with individual service health checks.

    Raises:
        HTTPException: 503 if any service is unhealthy.
    """
    logger.info("Readiness check requested")

    # Check individual services concurrently
    db_healthy, redis_healthy = await asyncio.gather(
        check_database_health(), check_redis_health()
    )

    checks = {
        "database": "healthy" if db_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy",
    }

    # Determine overall status
    all_healthy = db_healthy and redis_healthy
    overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.UNHEALTHY

    response = ReadinessResponse(status=overall_status, checks=checks)

    if not all_healthy:
        logger.warning("Readiness check failed", checks=checks)
        raise HTTPException(status_code=503, detail=response.model_dump())

    logger.info("Readiness check passed", checks=checks)
    return response
