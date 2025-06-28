"""Tests for database health checking functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from mindbridge.database.connection import DatabaseEngine
from mindbridge.database.health import DatabaseHealthChecker


class TestDatabaseHealthChecker:
    """Test cases for DatabaseHealthChecker class."""

    def test_health_checker_initialization(self) -> None:
        """Expected use case: Initialize health checker with database engine."""
        # Arrange
        mock_engine = Mock(spec=DatabaseEngine)

        # Act
        health_checker = DatabaseHealthChecker(mock_engine)

        # Assert
        assert health_checker._database_engine is mock_engine

    @pytest.mark.asyncio
    async def test_check_basic_connectivity_success(self) -> None:
        """Expected use case: Basic connectivity check should succeed."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_engine = AsyncMock(spec=DatabaseEngine)
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_engine.get_session.return_value.__aexit__.return_value = None

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_basic_connectivity()

        # Assert
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert result["checks"]["connectivity"]["status"] == "healthy"
        assert "Database connection successful" in result["checks"]["connectivity"]["message"]
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_basic_connectivity_sqlalchemy_error(self) -> None:
        """Failure case: Basic connectivity check with SQLAlchemy error."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = SQLAlchemyError("Connection failed")

        mock_engine = AsyncMock(spec=DatabaseEngine)
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_engine.get_session.return_value.__aexit__.return_value = None

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_basic_connectivity()

        # Assert
        assert result["status"] == "unhealthy"
        assert result["checks"]["connectivity"]["status"] == "unhealthy"
        assert "Database connection failed" in result["checks"]["connectivity"]["message"]
        assert "Connection failed" in result["checks"]["connectivity"]["message"]

    @pytest.mark.asyncio
    async def test_check_basic_connectivity_unexpected_error(self) -> None:
        """Failure case: Basic connectivity check with unexpected error."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = RuntimeError("Unexpected error")

        mock_engine = AsyncMock(spec=DatabaseEngine)
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_engine.get_session.return_value.__aexit__.return_value = None

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_basic_connectivity()

        # Assert
        assert result["status"] == "unhealthy"
        assert result["checks"]["connectivity"]["status"] == "unhealthy"
        assert "Unexpected error" in result["checks"]["connectivity"]["message"]

    @pytest.mark.asyncio
    async def test_check_pgvector_extension_success(self) -> None:
        """Expected use case: pgvector extension check should succeed."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock extension query result
        extension_result = Mock()
        extension_row = Mock()
        extension_row.extversion = "0.8.0"
        extension_result.fetchone.return_value = extension_row

        # Mock vector operation result
        vector_result = Mock()
        vector_result.scalar.return_value = 5.196152  # Example distance

        mock_session.execute.side_effect = [extension_result, vector_result]

        mock_engine = AsyncMock(spec=DatabaseEngine)
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_engine.get_session.return_value.__aexit__.return_value = None

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_pgvector_extension()

        # Assert
        assert result["status"] == "healthy"
        assert result["checks"]["pgvector_extension"]["status"] == "healthy"
        assert "version 0.8.0" in result["checks"]["pgvector_extension"]["message"]
        assert result["checks"]["vector_operations"]["status"] == "healthy"
        assert "5.196152" in result["checks"]["vector_operations"]["message"]

    @pytest.mark.asyncio
    async def test_check_pgvector_extension_not_installed(self) -> None:
        """Failure case: pgvector extension not installed."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock extension query result (no extension found)
        extension_result = Mock()
        extension_result.fetchone.return_value = None
        mock_session.execute.return_value = extension_result

        mock_engine = AsyncMock(spec=DatabaseEngine)
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_engine.get_session.return_value.__aexit__.return_value = None

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_pgvector_extension()

        # Assert
        assert result["status"] == "unhealthy"
        assert result["checks"]["pgvector_extension"]["status"] == "unhealthy"
        assert "not installed" in result["checks"]["pgvector_extension"]["message"]

    @pytest.mark.asyncio
    async def test_check_pgvector_extension_query_error(self) -> None:
        """Failure case: pgvector extension check with query error."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = SQLAlchemyError("Permission denied")

        mock_engine = AsyncMock(spec=DatabaseEngine)
        mock_engine.get_session.return_value.__aenter__.return_value = mock_session
        mock_engine.get_session.return_value.__aexit__.return_value = None

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_pgvector_extension()

        # Assert
        assert result["status"] == "unhealthy"
        assert result["checks"]["pgvector_extension"]["status"] == "unhealthy"
        assert "pgvector check failed" in result["checks"]["pgvector_extension"]["message"]

    @pytest.mark.asyncio
    async def test_check_pool_status_success(self) -> None:
        """Expected use case: Connection pool status check should succeed."""
        # Arrange
        mock_pool = Mock()
        mock_pool.size.return_value = 10
        mock_pool.checkedin.return_value = 8
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 3

        mock_engine_obj = Mock()
        mock_engine_obj.pool = mock_pool

        mock_engine = Mock(spec=DatabaseEngine)
        mock_engine.engine = mock_engine_obj

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_pool_status()

        # Assert
        assert result["status"] == "healthy"
        assert result["checks"]["connection_pool"]["status"] == "healthy"
        assert result["checks"]["connection_pool"]["pool_size"] == 10
        assert result["checks"]["connection_pool"]["checked_in"] == 8
        assert result["checks"]["connection_pool"]["checked_out"] == 2
        assert result["checks"]["connection_pool"]["overflow"] == 3
        assert result["checks"]["connection_pool"]["total_connections"] == 13  # 10 + 3

    @pytest.mark.asyncio
    async def test_check_pool_status_error(self) -> None:
        """Failure case: Pool status check with error."""
        # Arrange
        mock_engine = Mock(spec=DatabaseEngine)
        mock_engine.engine.pool.size.side_effect = RuntimeError("Pool error")

        health_checker = DatabaseHealthChecker(mock_engine)

        # Act
        result = await health_checker.check_pool_status()

        # Assert
        assert result["status"] == "unhealthy"
        assert result["checks"]["connection_pool"]["status"] == "unhealthy"
        assert "Pool status check failed" in result["checks"]["connection_pool"]["message"]

    @pytest.mark.asyncio
    async def test_comprehensive_health_check_all_healthy(self) -> None:
        """Expected use case: Comprehensive health check with all systems healthy."""
        # Arrange
        mock_engine = AsyncMock(spec=DatabaseEngine)
        health_checker = DatabaseHealthChecker(mock_engine)

        # Mock all individual checks to return healthy
        with patch.object(health_checker, 'check_basic_connectivity') as mock_connectivity, \
             patch.object(health_checker, 'check_pgvector_extension') as mock_pgvector, \
             patch.object(health_checker, 'check_pool_status') as mock_pool:

            mock_connectivity.return_value = {
                "status": "healthy",
                "checks": {"connectivity": {"status": "healthy", "message": "OK"}}
            }
            mock_pgvector.return_value = {
                "status": "healthy",
                "checks": {"pgvector_extension": {"status": "healthy", "message": "OK"}}
            }
            mock_pool.return_value = {
                "status": "healthy",
                "checks": {"connection_pool": {"status": "healthy", "pool_size": 10}}
            }

            # Act
            result = await health_checker.comprehensive_health_check()

        # Assert
        assert result["status"] == "healthy"
        assert "connectivity" in result["checks"]
        assert "pgvector_extension" in result["checks"]
        assert "connection_pool" in result["checks"]
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_comprehensive_health_check_one_unhealthy(self) -> None:
        """Failure case: Comprehensive health check with one system unhealthy."""
        # Arrange
        mock_engine = AsyncMock(spec=DatabaseEngine)
        health_checker = DatabaseHealthChecker(mock_engine)

        # Mock checks with one unhealthy
        with patch.object(health_checker, 'check_basic_connectivity') as mock_connectivity, \
             patch.object(health_checker, 'check_pgvector_extension') as mock_pgvector, \
             patch.object(health_checker, 'check_pool_status') as mock_pool:

            mock_connectivity.return_value = {
                "status": "healthy",
                "checks": {"connectivity": {"status": "healthy", "message": "OK"}}
            }
            mock_pgvector.return_value = {
                "status": "unhealthy",  # This one is unhealthy
                "checks": {"pgvector_extension": {"status": "unhealthy", "message": "Extension missing"}}
            }
            mock_pool.return_value = {
                "status": "healthy",
                "checks": {"connection_pool": {"status": "healthy", "pool_size": 10}}
            }

            # Act
            result = await health_checker.comprehensive_health_check()

        # Assert
        assert result["status"] == "unhealthy"  # Overall should be unhealthy
        assert "connectivity" in result["checks"]
        assert "pgvector_extension" in result["checks"]
        assert "connection_pool" in result["checks"]

    @pytest.mark.asyncio
    async def test_comprehensive_health_check_multiple_unhealthy(self) -> None:
        """Edge case: Comprehensive health check with multiple systems unhealthy."""
        # Arrange
        mock_engine = AsyncMock(spec=DatabaseEngine)
        health_checker = DatabaseHealthChecker(mock_engine)

        # Mock checks with multiple unhealthy
        with patch.object(health_checker, 'check_basic_connectivity') as mock_connectivity, \
             patch.object(health_checker, 'check_pgvector_extension') as mock_pgvector, \
             patch.object(health_checker, 'check_pool_status') as mock_pool:

            mock_connectivity.return_value = {
                "status": "unhealthy",
                "checks": {"connectivity": {"status": "unhealthy", "message": "Connection failed"}}
            }
            mock_pgvector.return_value = {
                "status": "unhealthy",
                "checks": {"pgvector_extension": {"status": "unhealthy", "message": "Extension missing"}}
            }
            mock_pool.return_value = {
                "status": "unhealthy",
                "checks": {"connection_pool": {"status": "unhealthy", "message": "Pool error"}}
            }

            # Act
            result = await health_checker.comprehensive_health_check()

        # Assert
        assert result["status"] == "unhealthy"
        assert result["checks"]["connectivity"]["status"] == "unhealthy"
        assert result["checks"]["pgvector_extension"]["status"] == "unhealthy"
        assert result["checks"]["connection_pool"]["status"] == "unhealthy"

