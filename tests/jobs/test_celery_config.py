"""Tests for Celery broker configuration."""

from unittest.mock import MagicMock, patch

import pytest
from mindbridge.jobs.celery_app import create_celery_app, get_celery_app
from mindbridge.jobs.celery_config import CeleryBrokerConfig, CeleryConfig
from mindbridge.jobs.exceptions import BrokerConfigurationError


class TestCeleryBrokerConfig:
    """Test cases for Celery broker configuration."""

    def test_celery_broker_config_creation_success(self) -> None:
        """Expected use case: Create Celery broker config with valid parameters."""
        config = CeleryBrokerConfig(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            timezone="UTC",
            enable_utc=True,
            visibility_timeout=3600,
        )

        assert config.broker_url == "redis://localhost:6379/0"
        assert config.result_backend == "redis://localhost:6379/1"
        assert config.task_serializer == "json"
        assert config.result_serializer == "json"
        assert config.accept_content == ["json"]
        assert config.timezone == "UTC"
        assert config.enable_utc is True
        assert config.visibility_timeout == 3600

    def test_celery_broker_config_default_values(self) -> None:
        """Expected use case: Create Celery broker config with default values."""
        config = CeleryBrokerConfig(broker_url="redis://localhost:6379/0")

        assert config.broker_url == "redis://localhost:6379/0"
        assert config.result_backend == "redis://localhost:6379/0"
        assert config.task_serializer == "json"
        assert config.result_serializer == "json"
        assert config.accept_content == ["json"]
        assert config.timezone == "UTC"
        assert config.enable_utc is True
        assert config.visibility_timeout == 3600

    def test_celery_broker_config_invalid_broker_url(self) -> None:
        """Failure case: Invalid broker URL."""
        with pytest.raises(ValueError, match="Broker URL cannot be empty"):
            CeleryBrokerConfig(broker_url="")

        with pytest.raises(ValueError, match="Broker URL cannot be empty"):
            CeleryBrokerConfig(broker_url=None)  # type: ignore[arg-type]

    def test_celery_broker_config_invalid_serializer(self) -> None:
        """Failure case: Invalid serializer."""
        with pytest.raises(ValueError, match="Invalid task serializer"):
            CeleryBrokerConfig(
                broker_url="redis://localhost:6379/0", task_serializer="invalid"
            )

        with pytest.raises(ValueError, match="Invalid result serializer"):
            CeleryBrokerConfig(
                broker_url="redis://localhost:6379/0", result_serializer="invalid"
            )

    def test_celery_broker_config_invalid_content_types(self) -> None:
        """Failure case: Invalid accept content types."""
        with pytest.raises(ValueError, match="Accept content cannot be empty"):
            CeleryBrokerConfig(broker_url="redis://localhost:6379/0", accept_content=[])

        with pytest.raises(ValueError, match="Invalid content type"):
            CeleryBrokerConfig(
                broker_url="redis://localhost:6379/0", accept_content=["invalid"]
            )

    def test_celery_broker_config_invalid_visibility_timeout(self) -> None:
        """Failure case: Invalid visibility timeout."""
        with pytest.raises(ValueError, match="Visibility timeout must be > 0"):
            CeleryBrokerConfig(
                broker_url="redis://localhost:6379/0", visibility_timeout=0
            )

        with pytest.raises(ValueError, match="Visibility timeout must be > 0"):
            CeleryBrokerConfig(
                broker_url="redis://localhost:6379/0", visibility_timeout=-1
            )

    def test_celery_broker_config_redis_url_parsing(self) -> None:
        """Expected use case: Parse Redis URLs correctly."""
        config = CeleryBrokerConfig(broker_url="redis://user:pass@localhost:6380/2")

        assert config.broker_url == "redis://user:pass@localhost:6380/2"
        assert "localhost" in config.broker_url
        assert "6380" in config.broker_url
        assert "/2" in config.broker_url

    def test_celery_broker_config_to_dict(self) -> None:
        """Expected use case: Convert config to dictionary."""
        config = CeleryBrokerConfig(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            timezone="UTC",
            enable_utc=True,
            visibility_timeout=3600,
        )

        config_dict = config.to_dict()

        assert config_dict["broker_url"] == "redis://localhost:6379/0"
        assert config_dict["result_backend"] == "redis://localhost:6379/1"
        assert config_dict["task_serializer"] == "json"
        assert config_dict["result_serializer"] == "json"
        assert config_dict["accept_content"] == ["json"]
        assert config_dict["timezone"] == "UTC"
        assert config_dict["enable_utc"] is True
        assert config_dict["broker_transport_options"]["visibility_timeout"] == 3600


class TestCeleryConfig:
    """Test cases for Celery configuration."""

    @pytest.fixture
    def broker_config(self) -> CeleryBrokerConfig:
        """Create broker config for testing."""
        return CeleryBrokerConfig(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
        )

    @pytest.fixture
    def celery_config(self, broker_config: CeleryBrokerConfig) -> CeleryConfig:
        """Create Celery config for testing."""
        return CeleryConfig(
            broker_config=broker_config,
            task_routes={
                "mindbridge.jobs.tasks.process_document": {
                    "queue": "document_processing"
                },
                "mindbridge.jobs.tasks.index_repository": {"queue": "indexing"},
            },
            beat_schedule={
                "cleanup-expired-cache": {
                    "task": "mindbridge.jobs.tasks.cleanup_expired_cache",
                    "schedule": 3600.0,  # Every hour
                },
            },
            worker_prefetch_multiplier=4,
            task_soft_time_limit=300,
            task_time_limit=600,
        )

    def test_celery_config_creation_success(
        self, broker_config: CeleryBrokerConfig
    ) -> None:
        """Expected use case: Create Celery config successfully."""
        config = CeleryConfig(
            broker_config=broker_config,
            task_routes={
                "mindbridge.jobs.tasks.process_document": {
                    "queue": "document_processing"
                },
            },
            beat_schedule={
                "cleanup-expired-cache": {
                    "task": "mindbridge.jobs.tasks.cleanup_expired_cache",
                    "schedule": 3600.0,
                },
            },
        )

        assert config.broker_config == broker_config
        assert "mindbridge.jobs.tasks.process_document" in config.task_routes
        assert "cleanup-expired-cache" in config.beat_schedule
        assert config.worker_prefetch_multiplier == 4
        assert config.task_soft_time_limit == 300
        assert config.task_time_limit == 600

    def test_celery_config_default_values(
        self, broker_config: CeleryBrokerConfig
    ) -> None:
        """Expected use case: Create Celery config with default values."""
        config = CeleryConfig(broker_config=broker_config)

        assert config.broker_config == broker_config
        assert config.task_routes == {}
        assert config.beat_schedule == {}
        assert config.worker_prefetch_multiplier == 4
        assert config.task_soft_time_limit == 300
        assert config.task_time_limit == 600

    def test_celery_config_invalid_broker_config(self) -> None:
        """Failure case: Invalid broker config."""
        with pytest.raises(TypeError):
            CeleryConfig(broker_config=None)  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            CeleryConfig(broker_config="invalid")  # type: ignore[arg-type]

    def test_celery_config_invalid_task_routes(
        self, broker_config: CeleryBrokerConfig
    ) -> None:
        """Failure case: Invalid task routes."""
        with pytest.raises(TypeError):
            CeleryConfig(broker_config=broker_config, task_routes="invalid")  # type: ignore[arg-type]

    def test_celery_config_invalid_beat_schedule(
        self, broker_config: CeleryBrokerConfig
    ) -> None:
        """Failure case: Invalid beat schedule."""
        with pytest.raises(TypeError):
            CeleryConfig(broker_config=broker_config, beat_schedule="invalid")  # type: ignore[arg-type]

    def test_celery_config_invalid_worker_settings(
        self, broker_config: CeleryBrokerConfig
    ) -> None:
        """Failure case: Invalid worker settings."""
        with pytest.raises(ValueError, match="Worker prefetch multiplier must be > 0"):
            CeleryConfig(broker_config=broker_config, worker_prefetch_multiplier=0)

        with pytest.raises(ValueError, match="Task soft time limit must be > 0"):
            CeleryConfig(broker_config=broker_config, task_soft_time_limit=0)

        with pytest.raises(ValueError, match="Task time limit must be > 0"):
            CeleryConfig(broker_config=broker_config, task_time_limit=0)

    def test_celery_config_time_limit_validation(
        self, broker_config: CeleryBrokerConfig
    ) -> None:
        """Failure case: Time limit validation."""
        with pytest.raises(
            ValueError, match="Task time limit must be greater than soft time limit"
        ):
            CeleryConfig(
                broker_config=broker_config,
                task_soft_time_limit=600,
                task_time_limit=300,
            )

    def test_celery_config_get_celery_settings(
        self, celery_config: CeleryConfig
    ) -> None:
        """Expected use case: Get Celery settings dictionary."""
        settings = celery_config.get_celery_settings()

        assert settings["broker_url"] == "redis://localhost:6379/0"
        assert settings["result_backend"] == "redis://localhost:6379/1"
        assert settings["task_serializer"] == "json"
        assert settings["result_serializer"] == "json"
        assert settings["accept_content"] == ["json"]
        assert settings["timezone"] == "UTC"
        assert settings["enable_utc"] is True
        assert settings["broker_transport_options"]["visibility_timeout"] == 3600
        assert "mindbridge.jobs.tasks.process_document" in settings["task_routes"]
        assert "cleanup-expired-cache" in settings["beat_schedule"]
        assert settings["worker_prefetch_multiplier"] == 4
        assert settings["task_soft_time_limit"] == 300
        assert settings["task_time_limit"] == 600


class TestCeleryApp:
    """Test cases for Celery application creation and management."""

    @pytest.fixture
    def celery_config(self) -> CeleryConfig:
        """Create Celery config for testing."""
        broker_config = CeleryBrokerConfig(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
        )
        return CeleryConfig(broker_config=broker_config)

    def test_create_celery_app_success(self, celery_config: CeleryConfig) -> None:
        """Expected use case: Create Celery app successfully."""
        with patch("mindbridge.jobs.celery_app.Celery") as mock_celery_class:
            mock_app = MagicMock()
            mock_celery_class.return_value = mock_app

            app = create_celery_app(celery_config)

            assert app == mock_app
            mock_celery_class.assert_called_once_with("mindbridge")
            mock_app.config_from_object.assert_called_once()

    def test_create_celery_app_with_custom_name(
        self, celery_config: CeleryConfig
    ) -> None:
        """Expected use case: Create Celery app with custom name."""
        with patch("mindbridge.jobs.celery_app.Celery") as mock_celery_class:
            mock_app = MagicMock()
            mock_celery_class.return_value = mock_app

            app = create_celery_app(celery_config, app_name="custom_app")

            assert app == mock_app
            mock_celery_class.assert_called_once_with("custom_app")

    def test_create_celery_app_invalid_config(self) -> None:
        """Failure case: Create Celery app with invalid config."""
        with pytest.raises(TypeError):
            create_celery_app(None)  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            create_celery_app("invalid")  # type: ignore[arg-type]

    def test_get_celery_app_success(self, celery_config: CeleryConfig) -> None:
        """Expected use case: Get Celery app singleton."""
        with patch("mindbridge.jobs.celery_app.create_celery_app") as mock_create:
            mock_app = MagicMock()
            mock_create.return_value = mock_app

            with patch(
                "mindbridge.jobs.celery_app.get_celery_config"
            ) as mock_get_config:
                mock_get_config.return_value = celery_config

                app1 = get_celery_app()
                app2 = get_celery_app()

                assert app1 == app2  # Should be the same instance
                mock_create.assert_called_once()  # Should only create once

    def test_get_celery_app_configuration_error(self) -> None:
        """Failure case: Get Celery app with configuration error."""
        with patch("mindbridge.jobs.celery_app.get_celery_config") as mock_get_config:
            mock_get_config.side_effect = Exception("Configuration error")

            # Reset the global celery app first
            from mindbridge.jobs.celery_app import reset_celery_app

            reset_celery_app()

            with pytest.raises(
                BrokerConfigurationError, match="Failed to configure Celery"
            ):
                get_celery_app()

    @pytest.mark.asyncio
    async def test_celery_broker_connection_check_success(
        self, celery_config: CeleryConfig
    ) -> None:
        """Expected use case: Check broker connection successfully."""
        with patch("mindbridge.jobs.celery_app.create_celery_app") as mock_create:
            mock_app = MagicMock()
            mock_app.control.inspect.return_value.ping.return_value = {
                "worker1": "pong"
            }
            mock_create.return_value = mock_app

            from mindbridge.jobs.celery_app import check_broker_connection

            result = await check_broker_connection(celery_config)

            assert result is True

    @pytest.mark.asyncio
    async def test_celery_broker_connection_check_failure(
        self, celery_config: CeleryConfig
    ) -> None:
        """Failure case: Broker connection check fails."""
        with patch("mindbridge.jobs.celery_app.create_celery_app") as mock_create:
            mock_app = MagicMock()
            mock_app.control.inspect.return_value.ping.side_effect = Exception(
                "Connection error"
            )
            mock_create.return_value = mock_app

            from mindbridge.jobs.celery_app import check_broker_connection

            result = await check_broker_connection(celery_config)

            assert result is False

    @pytest.mark.asyncio
    async def test_celery_broker_connection_check_no_workers(
        self, celery_config: CeleryConfig
    ) -> None:
        """Expected use case: No workers available."""
        with patch("mindbridge.jobs.celery_app.create_celery_app") as mock_create:
            mock_app = MagicMock()
            mock_app.control.inspect.return_value.ping.return_value = None
            mock_create.return_value = mock_app

            from mindbridge.jobs.celery_app import check_broker_connection

            result = await check_broker_connection(celery_config)

            assert result is False

    def test_celery_app_task_registration(self, celery_config: CeleryConfig) -> None:
        """Expected use case: Register tasks with Celery app."""
        with patch("mindbridge.jobs.celery_app.Celery") as mock_celery_class:
            mock_app = MagicMock()
            mock_celery_class.return_value = mock_app

            app = create_celery_app(celery_config)

            # Test that we can get the task decorator
            task_decorator = app.task

            # Verify the app was created
            mock_celery_class.assert_called_once_with("mindbridge")
            assert task_decorator == mock_app.task

    def test_celery_app_autodiscover_tasks(self, celery_config: CeleryConfig) -> None:
        """Expected use case: Auto-discover tasks."""
        with patch("mindbridge.jobs.celery_app.Celery") as mock_celery_class:
            mock_app = MagicMock()
            mock_celery_class.return_value = mock_app

            create_celery_app(celery_config, autodiscover_tasks=True)

            mock_app.autodiscover_tasks.assert_called_once_with(
                [
                    "mindbridge.jobs.tasks",
                ]
            )

    def test_celery_config_environment_variables(self) -> None:
        """Expected use case: Load config from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "REDIS_URL": "redis://localhost:6379/0",
                "CELERY_BROKER_URL": "redis://localhost:6379/0",
                "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
                "CELERY_VISIBILITY_TIMEOUT": "7200",
            },
        ):
            from mindbridge.jobs.celery_config import get_celery_config_from_env

            config = get_celery_config_from_env()

            assert config.broker_config.broker_url == "redis://localhost:6379/0"
            assert config.broker_config.result_backend == "redis://localhost:6379/1"
            assert config.broker_config.visibility_timeout == 7200

    def test_celery_config_environment_variables_missing(self) -> None:
        """Failure case: Missing required environment variables."""
        with patch.dict("os.environ", {}, clear=True):
            from mindbridge.jobs.celery_config import get_celery_config_from_env

            with pytest.raises(
                BrokerConfigurationError,
                match="REDIS_URL environment variable is required",
            ):
                get_celery_config_from_env()

    def test_celery_config_environment_variables_invalid(self) -> None:
        """Failure case: Invalid environment variable values."""
        with patch.dict(
            "os.environ",
            {
                "REDIS_URL": "redis://localhost:6379/0",
                "CELERY_VISIBILITY_TIMEOUT": "invalid",
            },
        ):
            from mindbridge.jobs.celery_config import get_celery_config_from_env

            with pytest.raises(
                BrokerConfigurationError, match="Invalid CELERY_VISIBILITY_TIMEOUT"
            ):
                get_celery_config_from_env()

    def test_celery_broker_health_check_success(
        self, celery_config: CeleryConfig
    ) -> None:
        """Expected use case: Broker health check passes."""
        with patch("mindbridge.jobs.celery_app.create_celery_app") as mock_create:
            mock_app = MagicMock()
            mock_app.control.inspect.return_value.stats.return_value = {
                "worker1": {"broker": {"connect_timeout": 4.0}}
            }
            mock_create.return_value = mock_app

            from mindbridge.jobs.celery_app import get_broker_health

            health = get_broker_health(celery_config)

            assert health["status"] == "healthy"
            assert "worker1" in health["workers"]

    def test_celery_broker_health_check_failure(
        self, celery_config: CeleryConfig
    ) -> None:
        """Failure case: Broker health check fails."""
        with patch("mindbridge.jobs.celery_app.create_celery_app") as mock_create:
            mock_app = MagicMock()
            mock_app.control.inspect.return_value.stats.side_effect = Exception(
                "Connection error"
            )
            mock_create.return_value = mock_app

            from mindbridge.jobs.celery_app import get_broker_health

            health = get_broker_health(celery_config)

            assert health["status"] == "unhealthy"
            assert "error" in health

    def test_celery_task_routing_configuration(self) -> None:
        """Expected use case: Task routing configured correctly."""
        broker_config = CeleryBrokerConfig(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
        )
        celery_config = CeleryConfig(
            broker_config=broker_config,
            task_routes={
                "mindbridge.jobs.tasks.process_document": {
                    "queue": "document_processing"
                },
                "mindbridge.jobs.tasks.index_repository": {"queue": "indexing"},
            },
        )

        settings = celery_config.get_celery_settings()

        assert "task_routes" in settings
        task_routes = settings["task_routes"]

        assert "mindbridge.jobs.tasks.process_document" in task_routes
        assert (
            task_routes["mindbridge.jobs.tasks.process_document"]["queue"]
            == "document_processing"
        )

    def test_celery_beat_schedule_configuration(self) -> None:
        """Expected use case: Beat schedule configured correctly."""
        broker_config = CeleryBrokerConfig(
            broker_url="redis://localhost:6379/0",
            result_backend="redis://localhost:6379/1",
        )
        celery_config = CeleryConfig(
            broker_config=broker_config,
            beat_schedule={
                "cleanup-expired-cache": {
                    "task": "mindbridge.jobs.tasks.cleanup_expired_cache",
                    "schedule": 3600.0,  # Every hour
                },
            },
        )

        settings = celery_config.get_celery_settings()

        assert "beat_schedule" in settings
        beat_schedule = settings["beat_schedule"]

        assert "cleanup-expired-cache" in beat_schedule
        assert (
            beat_schedule["cleanup-expired-cache"]["task"]
            == "mindbridge.jobs.tasks.cleanup_expired_cache"
        )
        assert beat_schedule["cleanup-expired-cache"]["schedule"] == 3600.0

    def test_celery_worker_configuration(self, celery_config: CeleryConfig) -> None:
        """Expected use case: Worker configuration is correct."""
        settings = celery_config.get_celery_settings()

        assert settings["worker_prefetch_multiplier"] == 4
        assert settings["task_soft_time_limit"] == 300
        assert settings["task_time_limit"] == 600

    def test_celery_transport_options_configuration(
        self, celery_config: CeleryConfig
    ) -> None:
        """Expected use case: Transport options configured correctly."""
        settings = celery_config.get_celery_settings()

        assert "broker_transport_options" in settings
        transport_options = settings["broker_transport_options"]

        assert transport_options["visibility_timeout"] == 3600
