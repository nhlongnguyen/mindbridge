"""Celery application creation and management."""

import asyncio
import logging
from typing import Any

from celery import Celery

from mindbridge.jobs.celery_config import CeleryConfig, get_celery_config
from mindbridge.jobs.exceptions import BrokerConfigurationError, BrokerConnectionError

logger = logging.getLogger(__name__)


def create_celery_app(
    config: CeleryConfig,
    app_name: str = "mindbridge",
    autodiscover_tasks: bool = True,
) -> Celery:
    """Create Celery application with configuration.

    Args:
        config: Celery configuration
        app_name: Application name
        autodiscover_tasks: Whether to auto-discover tasks

    Returns:
        Configured Celery application

    Raises:
        TypeError: If config is not CeleryConfig instance
    """
    if not isinstance(config, CeleryConfig):
        raise TypeError("config must be CeleryConfig instance")

    # Create Celery app
    app = Celery(app_name)

    # Configure from settings dictionary
    settings = config.get_celery_settings()
    settings_obj = type("CelerySettings", (), settings)()
    app.config_from_object(settings_obj)

    # Auto-discover tasks if enabled
    if autodiscover_tasks:
        app.autodiscover_tasks(
            [
                "mindbridge.jobs.tasks",
            ]
        )

    return app


# Global Celery app instance
_celery_app: Celery | None = None


def get_celery_app() -> Celery:
    """Get the global Celery application instance.

    Returns:
        Celery application instance

    Raises:
        BrokerConfigurationError: If configuration fails
    """
    global _celery_app

    if _celery_app is None:
        try:
            config = get_celery_config()
            _celery_app = create_celery_app(config)
        except Exception as e:
            raise BrokerConfigurationError(f"Failed to configure Celery: {e}", e) from e

    return _celery_app


async def check_broker_connection(config: CeleryConfig) -> bool:
    """Check if broker connection is working.

    Args:
        config: Celery configuration

    Returns:
        True if connection is working, False otherwise
    """
    try:
        app = create_celery_app(config)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        def _ping_broker() -> bool:
            try:
                inspect = app.control.inspect()
                result = inspect.ping()
                return result is not None and len(result) > 0
            except Exception as e:
                logger.warning("Broker ping failed: %s", str(e))
                return False

        result = await loop.run_in_executor(None, _ping_broker)
        return result

    except Exception as e:
        logger.error("Broker connection check failed: %s", str(e))
        return False


def get_broker_health(config: CeleryConfig) -> dict[str, Any]:
    """Get broker health information.

    Args:
        config: Celery configuration

    Returns:
        Dictionary containing health information
    """
    try:
        app = create_celery_app(config)
        inspect = app.control.inspect()

        # Get worker stats
        stats = inspect.stats()

        if not stats:
            return {
                "status": "unhealthy",
                "error": "No workers available",
                "workers": {},
            }

        return {
            "status": "healthy",
            "workers": stats,
            "worker_count": len(stats),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "workers": {},
        }


def get_broker_stats(config: CeleryConfig) -> dict[str, Any]:
    """Get detailed broker statistics.

    Args:
        config: Celery configuration

    Returns:
        Dictionary containing broker statistics
    """
    try:
        app = create_celery_app(config)
        inspect = app.control.inspect()

        # Get various statistics
        stats = inspect.stats()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()

        return {
            "stats": stats or {},
            "active_tasks": active_tasks or {},
            "scheduled_tasks": scheduled_tasks or {},
            "reserved_tasks": reserved_tasks or {},
            "workers_online": len(stats) if stats else 0,
        }

    except Exception as e:
        return {
            "error": str(e),
            "stats": {},
            "active_tasks": {},
            "scheduled_tasks": {},
            "reserved_tasks": {},
            "workers_online": 0,
        }


def get_queue_lengths(_config: CeleryConfig) -> dict[str, int]:
    """Get queue lengths for monitoring.

    Args:
        config: Celery configuration

    Returns:
        Dictionary mapping queue names to their lengths
    """
    try:
        # This would require additional Redis connection to check queue lengths
        # For now, return empty dict as this would need direct Redis access
        logger.debug(
            "Queue length monitoring not yet implemented - requires Redis connection"
        )
        return {}

    except Exception as e:
        logger.error("Failed to get queue lengths: %s", str(e))
        return {}


async def purge_queue(config: CeleryConfig, queue_name: str) -> int:
    """Purge messages from a specific queue.

    Args:
        config: Celery configuration
        queue_name: Name of queue to purge

    Returns:
        Number of messages purged

    Raises:
        BrokerConnectionError: If operation fails
    """
    try:
        app = create_celery_app(config)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        def _purge_queue() -> int:
            try:
                # Purge specific queue, not all queues
                result = (
                    app.control.purge(destination=[queue_name])
                    if queue_name
                    else app.control.purge()
                )
                return result or 0
            except Exception as e:
                raise BrokerConnectionError(f"Failed to purge queue: {e}", e) from e

        result = await loop.run_in_executor(None, _purge_queue)
        return result or 0

    except Exception as e:
        raise BrokerConnectionError(
            f"Failed to purge queue {queue_name}: {e}", e
        ) from e


async def shutdown_workers(config: CeleryConfig, _signal: str = "TERM") -> bool:
    """Shutdown Celery workers.

    Args:
        config: Celery configuration
        signal: Signal to send to workers (TERM, KILL, etc.)

    Returns:
        True if shutdown command was sent successfully

    Raises:
        BrokerConnectionError: If operation fails
    """
    try:
        app = create_celery_app(config)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        def _shutdown_workers() -> bool:
            try:
                app.control.broadcast("shutdown")
                return True
            except Exception as e:
                raise BrokerConnectionError(
                    f"Failed to shutdown workers: {e}", e
                ) from e

        result = await loop.run_in_executor(None, _shutdown_workers)
        return result

    except Exception as e:
        raise BrokerConnectionError(f"Failed to shutdown workers: {e}", e) from e


def reset_celery_app() -> None:
    """Reset the global Celery app instance."""
    global _celery_app
    _celery_app = None
