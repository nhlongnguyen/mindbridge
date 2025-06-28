"""Tests for health check API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from mindbridge.api.health import (
    HealthResponse,
    HealthStatus,
    ReadinessResponse,
    router,
)


class TestHealthModels:
    """Test cases for health check data models."""

    def test_health_status_enum_values(self) -> None:
        """Expected use case: HealthStatus enum should have correct values."""
        assert HealthStatus.HEALTHY == HealthStatus.HEALTHY
        assert HealthStatus.UNHEALTHY == HealthStatus.UNHEALTHY
        assert HealthStatus.DEGRADED == HealthStatus.DEGRADED

    def test_health_response_model_creation(self) -> None:
        """Expected use case: HealthResponse model should create correctly."""
        response = HealthResponse(
            status=HealthStatus.HEALTHY,
            timestamp="2024-01-01T00:00:00Z",
            version="1.0.0",
        )

        assert response.status == HealthStatus.HEALTHY
        assert response.timestamp == "2024-01-01T00:00:00Z"
        assert response.version == "1.0.0"

    def test_readiness_response_model_creation(self) -> None:
        """Expected use case: ReadinessResponse model should create correctly."""
        checks = {"database": "healthy", "redis": "healthy"}
        response = ReadinessResponse(status=HealthStatus.HEALTHY, checks=checks)

        assert response.status == HealthStatus.HEALTHY
        assert response.checks == checks


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for health router."""
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_health_endpoint_returns_healthy_status(self, client: TestClient) -> None:
        """Expected use case: Health endpoint should return healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_health_endpoint_includes_timestamp(self, client: TestClient) -> None:
        """Expected use case: Health response should include current timestamp."""
        response = client.get("/health")
        data = response.json()

        assert "timestamp" in data
        # Should be ISO format timestamp
        timestamp = data["timestamp"]
        assert "T" in timestamp
        assert timestamp.endswith("Z")

    def test_health_endpoint_includes_version(self, client: TestClient) -> None:
        """Expected use case: Health response should include version."""
        response = client.get("/health")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    @patch("mindbridge.api.health.check_database_health")
    @patch("mindbridge.api.health.check_redis_health")
    def test_readiness_endpoint_all_services_healthy(
        self, mock_redis_check: MagicMock, mock_db_check: MagicMock, client: TestClient
    ) -> None:
        """Expected use case: Readiness endpoint when all services are healthy."""
        mock_db_check.return_value = True
        mock_redis_check.return_value = True

        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["checks"]["database"] == "healthy"
        assert data["checks"]["redis"] == "healthy"

    @patch("mindbridge.api.health.check_database_health")
    @patch("mindbridge.api.health.check_redis_health")
    def test_readiness_endpoint_database_unhealthy(
        self, mock_redis_check: MagicMock, mock_db_check: MagicMock, client: TestClient
    ) -> None:
        """Expected use case: Readiness endpoint when database is unhealthy."""
        mock_db_check.return_value = False
        mock_redis_check.return_value = True

        response = client.get("/ready")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["database"] == "unhealthy"
        assert data["checks"]["redis"] == "healthy"


class TestHealthCheckFunctions:
    """Test cases for health check utility functions."""

    @pytest.mark.asyncio
    @patch("mindbridge.database.connection.get_async_engine")
    async def test_check_database_health_success(
        self, mock_get_engine: MagicMock
    ) -> None:
        """Expected use case: Database health check should return True when healthy."""
        from mindbridge.api.health import check_database_health

        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_session.execute.return_value = None

        result = await check_database_health()
        assert result is True

    @pytest.mark.asyncio
    @patch("mindbridge.database.connection.get_async_engine")
    async def test_check_database_health_failure(
        self, mock_get_engine: MagicMock
    ) -> None:
        """Failure case: Database health check should return False when unhealthy."""
        from mindbridge.api.health import check_database_health

        mock_get_engine.side_effect = Exception("Database connection failed")

        result = await check_database_health()
        assert result is False

    @pytest.mark.asyncio
    @patch("mindbridge.cache.redis_cache.get_redis_cache")
    async def test_check_redis_health_success(self, mock_get_cache: MagicMock) -> None:
        """Expected use case: Redis health check should return True when healthy."""
        from mindbridge.api.health import check_redis_health

        mock_cache = MagicMock()
        mock_get_cache.return_value = mock_cache
        mock_cache.connect.return_value = None
        mock_cache.ping.return_value = True
        mock_cache.disconnect.return_value = None

        result = await check_redis_health()
        assert result is True

    @pytest.mark.asyncio
    @patch("mindbridge.cache.redis_cache.get_redis_cache")
    async def test_check_redis_health_failure(self, mock_get_cache: MagicMock) -> None:
        """Failure case: Redis health check should return False when unhealthy."""
        from mindbridge.api.health import check_redis_health

        mock_get_cache.side_effect = Exception("Redis connection failed")

        result = await check_redis_health()
        assert result is False


class TestHealthCheckEdgeCases:
    """Test edge cases for health check functionality."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for health router."""
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_health_endpoint_with_query_parameters(self, client: TestClient) -> None:
        """Edge case: Health endpoint should ignore query parameters."""
        response = client.get("/health?param=value")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_endpoint_with_different_methods(self, client: TestClient) -> None:
        """Edge case: Health endpoint should only accept GET requests."""
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed

    @patch("mindbridge.api.health.check_database_health")
    @patch("mindbridge.api.health.check_redis_health")
    def test_readiness_endpoint_partial_failure(
        self, mock_redis_check: MagicMock, mock_db_check: MagicMock, client: TestClient
    ) -> None:
        """Edge case: Readiness endpoint with mixed health states."""
        mock_db_check.return_value = True
        mock_redis_check.return_value = False

        response = client.get("/ready")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"]["database"] == "healthy"
        assert data["checks"]["redis"] == "unhealthy"
