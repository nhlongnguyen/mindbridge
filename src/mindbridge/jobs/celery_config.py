"""Celery configuration for Redis broker."""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from mindbridge.jobs.exceptions import BrokerConfigurationError


@dataclass
class CeleryBrokerConfig:
    """Configuration for Celery broker."""
    
    broker_url: str
    result_backend: Optional[str] = None
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = field(default_factory=lambda: ["json"])
    timezone: str = "UTC"
    enable_utc: bool = True
    visibility_timeout: int = 3600
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if not self.broker_url:
            raise ValueError("Broker URL cannot be empty")
        
        # Set result backend to broker URL if not specified
        if self.result_backend is None:
            self.result_backend = self.broker_url
        
        # Validate serializers
        valid_serializers = ["json", "pickle", "yaml", "msgpack"]
        if self.task_serializer not in valid_serializers:
            raise ValueError(f"Invalid task serializer: {self.task_serializer}")
        
        if self.result_serializer not in valid_serializers:
            raise ValueError(f"Invalid result serializer: {self.result_serializer}")
        
        # Validate accept content
        if not self.accept_content:
            raise ValueError("Accept content cannot be empty")
        
        valid_content_types = ["json", "pickle", "yaml", "msgpack"]
        for content_type in self.accept_content:
            if content_type not in valid_content_types:
                raise ValueError(f"Invalid content type: {content_type}")
        
        # Validate visibility timeout
        if self.visibility_timeout <= 0:
            raise ValueError("Visibility timeout must be > 0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "broker_url": self.broker_url,
            "result_backend": self.result_backend,
            "task_serializer": self.task_serializer,
            "result_serializer": self.result_serializer,
            "accept_content": self.accept_content,
            "timezone": self.timezone,
            "enable_utc": self.enable_utc,
            "broker_transport_options": {
                "visibility_timeout": self.visibility_timeout,
                "fanout_prefix": True,
                "fanout_patterns": True,
            },
            "result_backend_transport_options": {
                "visibility_timeout": self.visibility_timeout,
            },
        }


@dataclass
class CeleryConfig:
    """Configuration for Celery application."""
    
    broker_config: CeleryBrokerConfig
    task_routes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    beat_schedule: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    worker_prefetch_multiplier: int = 4
    task_soft_time_limit: int = 300
    task_time_limit: int = 600
    task_always_eager: bool = False
    task_eager_propagates: bool = True
    task_ignore_result: bool = False
    task_store_eager_result: bool = True
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if not isinstance(self.broker_config, CeleryBrokerConfig):
            raise TypeError("broker_config must be CeleryBrokerConfig instance")
        
        if not isinstance(self.task_routes, dict):
            raise TypeError("task_routes must be dictionary")
        
        if not isinstance(self.beat_schedule, dict):
            raise TypeError("beat_schedule must be dictionary")
        
        if self.worker_prefetch_multiplier <= 0:
            raise ValueError("Worker prefetch multiplier must be > 0")
        
        if self.task_soft_time_limit <= 0:
            raise ValueError("Task soft time limit must be > 0")
        
        if self.task_time_limit <= 0:
            raise ValueError("Task time limit must be > 0")
        
        if self.task_time_limit <= self.task_soft_time_limit:
            raise ValueError("Task time limit must be greater than soft time limit")
    
    def get_celery_settings(self) -> Dict[str, Any]:
        """Get Celery settings dictionary.
        
        Returns:
            Dictionary of Celery settings
        """
        settings = self.broker_config.to_dict()
        
        # Add additional settings
        settings.update({
            "task_routes": self.task_routes,
            "beat_schedule": self.beat_schedule,
            "worker_prefetch_multiplier": self.worker_prefetch_multiplier,
            "task_soft_time_limit": self.task_soft_time_limit,
            "task_time_limit": self.task_time_limit,
            "task_always_eager": self.task_always_eager,
            "task_eager_propagates": self.task_eager_propagates,
            "task_ignore_result": self.task_ignore_result,
            "task_store_eager_result": self.task_store_eager_result,
            "worker_send_task_events": True,
            "task_send_sent_event": True,
            "worker_hijack_root_logger": False,
            "worker_log_color": False,
            "task_reject_on_worker_lost": True,
            "task_acks_late": True,
            "worker_disable_rate_limits": False,
            "task_compression": "gzip",
            "result_compression": "gzip",
            "result_expires": 3600,  # 1 hour
            "broker_connection_retry_on_startup": True,
            "broker_connection_retry": True,
            "broker_connection_max_retries": 100,
        })
        
        return settings


def get_celery_config_from_env() -> CeleryConfig:
    """Get Celery configuration from environment variables.
    
    Returns:
        CeleryConfig instance
    
    Raises:
        BrokerConfigurationError: If required environment variables are missing
    """
    try:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise BrokerConfigurationError("REDIS_URL environment variable is required")
        
        # Parse broker and result backend URLs
        broker_url = os.getenv("CELERY_BROKER_URL", redis_url)
        result_backend = os.getenv("CELERY_RESULT_BACKEND", redis_url)
        
        # Parse visibility timeout
        visibility_timeout_str = os.getenv("CELERY_VISIBILITY_TIMEOUT", "3600")
        try:
            visibility_timeout = int(visibility_timeout_str)
        except ValueError:
            raise BrokerConfigurationError(f"Invalid CELERY_VISIBILITY_TIMEOUT: {visibility_timeout_str}")
        
        # Create broker configuration
        broker_config = CeleryBrokerConfig(
            broker_url=broker_url,
            result_backend=result_backend,
            task_serializer=os.getenv("CELERY_TASK_SERIALIZER", "json"),
            result_serializer=os.getenv("CELERY_RESULT_SERIALIZER", "json"),
            accept_content=os.getenv("CELERY_ACCEPT_CONTENT", "json").split(","),
            timezone=os.getenv("CELERY_TIMEZONE", "UTC"),
            enable_utc=os.getenv("CELERY_ENABLE_UTC", "true").lower() == "true",
            visibility_timeout=visibility_timeout,
        )
        
        # Parse worker settings
        worker_prefetch_multiplier = int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", "4"))
        task_soft_time_limit = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "300"))
        task_time_limit = int(os.getenv("CELERY_TASK_TIME_LIMIT", "600"))
        task_always_eager = os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
        
        # Default task routes
        task_routes = {
            "mindbridge.jobs.tasks.process_document": {"queue": "document_processing"},
            "mindbridge.jobs.tasks.index_repository": {"queue": "indexing"},
            "mindbridge.jobs.tasks.cleanup_expired_cache": {"queue": "maintenance"},
            "mindbridge.jobs.tasks.generate_embeddings": {"queue": "embeddings"},
            "mindbridge.jobs.tasks.update_search_index": {"queue": "search"},
        }
        
        # Default beat schedule
        beat_schedule = {
            "cleanup-expired-cache": {
                "task": "mindbridge.jobs.tasks.cleanup_expired_cache",
                "schedule": 3600.0,  # Every hour
            },
            "update-search-indexes": {
                "task": "mindbridge.jobs.tasks.update_search_indexes",
                "schedule": 1800.0,  # Every 30 minutes
            },
        }
        
        return CeleryConfig(
            broker_config=broker_config,
            task_routes=task_routes,
            beat_schedule=beat_schedule,
            worker_prefetch_multiplier=worker_prefetch_multiplier,
            task_soft_time_limit=task_soft_time_limit,
            task_time_limit=task_time_limit,
            task_always_eager=task_always_eager,
        )
        
    except Exception as e:
        if isinstance(e, BrokerConfigurationError):
            raise
        raise BrokerConfigurationError(f"Failed to load Celery configuration: {e}", e)


def get_celery_config() -> CeleryConfig:
    """Get Celery configuration.
    
    Returns:
        CeleryConfig instance
    """
    return get_celery_config_from_env()