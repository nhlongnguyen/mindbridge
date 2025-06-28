"""Metrics collection API endpoints."""

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from mindbridge.observability.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=Response)
async def get_metrics() -> Response:
    """Prometheus metrics endpoint.

    Returns:
        Prometheus formatted metrics data.
    """
    logger.debug("Metrics endpoint requested")

    # Generate Prometheus metrics
    metrics_data = generate_latest()

    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
