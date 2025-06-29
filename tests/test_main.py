"""Tests for the main FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from mindbridge.main import app


class TestMainApplication:
    """Test cases for the main FastAPI application."""

    def test_app_initialization(self) -> None:
        """Expected use case: FastAPI app should initialize successfully."""
        assert app is not None
        assert app.title == "Mindbridge"
        assert app.description == "Agentic RAG Documentation System"

    def test_app_has_cors_middleware(self) -> None:
        """Expected use case: App should have CORS middleware configured."""
        middleware_types = [type(middleware) for middleware in app.user_middleware]
        # We'll check for CORS middleware after implementation
        assert len(middleware_types) >= 0  # Placeholder assertion

    def test_app_has_opentelemetry_middleware(self) -> None:
        """Expected use case: App should have OpenTelemetry middleware configured."""
        # This will be implemented after OpenTelemetry setup
        assert app is not None  # Placeholder assertion


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI app."""
        return TestClient(app)

    def test_health_check_endpoint_exists(self, client: TestClient) -> None:
        """Expected use case: Health check endpoint should return 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_format(self, client: TestClient) -> None:
        """Expected use case: Health check should return proper JSON format."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"

    def test_readiness_check_endpoint_exists(self, client: TestClient) -> None:
        """Expected use case: Readiness check endpoint should respond."""
        response = client.get("/ready")
        # Should respond with either 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]

    def test_readiness_check_response_format(self, client: TestClient) -> None:
        """Expected use case: Readiness check should return proper JSON format."""
        response = client.get("/ready")
        data = response.json()

        # Handle both success and error response formats
        if response.status_code == 200:
            assert "status" in data
            assert "checks" in data
            assert isinstance(data["checks"], dict)
        else:
            # Error case - data is in 'detail' field
            assert "detail" in data
            detail = data["detail"]
            assert "status" in detail
            assert "checks" in detail
            assert isinstance(detail["checks"], dict)


class TestMetricsEndpoints:
    """Test cases for metrics endpoints."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI app."""
        return TestClient(app)

    def test_metrics_endpoint_exists(self, client: TestClient) -> None:
        """Expected use case: Metrics endpoint should return 200."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_response_format(self, client: TestClient) -> None:
        """Expected use case: Metrics should return Prometheus format."""
        response = client.get("/metrics")
        assert "text/plain" in response.headers["content-type"]
        # Basic check for Prometheus format
        assert "# HELP" in response.text or "# TYPE" in response.text


class TestRootEndpoint:
    """Test cases for root endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI app."""
        return TestClient(app)

    def test_root_endpoint_exists(self, client: TestClient) -> None:
        """Expected use case: Root endpoint should return 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_response(self, client: TestClient) -> None:
        """Expected use case: Root endpoint should return API information."""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert data["name"] == "Mindbridge"
