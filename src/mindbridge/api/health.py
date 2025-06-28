"""Health check API endpoints."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    checks: Dict[str, str]


def check_database_health() -> bool:
    """Check database connectivity and health.
    
    Returns:
        True if database is healthy, False otherwise.
    """
    try:
        from mindbridge.database.connection import get_async_engine
        from sqlalchemy import text
        import asyncio
        
        async def _check_db():
            engine = get_async_engine()
            async with engine.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        
        # Run async check in sync context
        try:
            return asyncio.run(_check_db())
        except Exception as inner_e:
            logger.error("Database async check failed", error=str(inner_e))
            return False
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


def check_redis_health() -> bool:
    """Check Redis connectivity and health.
    
    Returns:
        True if Redis is healthy, False otherwise.
    """
    try:
        from mindbridge.cache.redis_cache import get_redis_cache
        import asyncio
        
        async def _check_redis():
            cache = get_redis_cache()
            await cache.connect()
            result = await cache.ping()
            await cache.disconnect()
            return result
        
        # Run async check in sync context
        try:
            return asyncio.run(_check_redis())
        except Exception as inner_e:
            logger.error("Redis async check failed", error=str(inner_e))
            return False
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
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
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        version="0.1.0"
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
    
    # Check individual services
    db_healthy = check_database_health()
    redis_healthy = check_redis_health()
    
    checks = {
        "database": "healthy" if db_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy"
    }
    
    # Determine overall status
    all_healthy = db_healthy and redis_healthy
    overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.UNHEALTHY
    
    response = ReadinessResponse(
        status=overall_status,
        checks=checks
    )
    
    if not all_healthy:
        logger.warning("Readiness check failed", checks=checks)
        raise HTTPException(status_code=503, detail=response.model_dump())
    
    logger.info("Readiness check passed", checks=checks)
    return response