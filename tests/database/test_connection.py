"""Tests for database connection management."""

import os
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from mindbridge.database.connection import (
    DatabaseEngine,
    close_database_engine,
    get_async_engine,
)


class TestDatabaseEngine:
    """Test cases for DatabaseEngine class."""

    def test_database_engine_initialization_success(self) -> None:
        """Expected use case: Initialize DatabaseEngine with valid configuration."""
        # Arrange
        database_url = "postgresql+asyncpg://user:pass@localhost/test"
        pool_size = 5
        max_overflow = 10

        # Act
        engine = DatabaseEngine(
            database_url=database_url,
            pool_size=pool_size,
            max_overflow=max_overflow
        )

        # Assert
        assert engine._database_url == database_url
        assert engine._pool_size == pool_size
        assert engine._max_overflow == max_overflow
        assert engine._pool_timeout == 30  # default
        assert engine._pool_recycle == 3600  # default
        assert engine._pool_pre_ping is True  # default
        assert engine._echo is False  # default

    def test_database_engine_custom_configuration(self) -> None:
        """Expected use case: Initialize DatabaseEngine with custom settings."""
        # Arrange
        config = {
            "database_url": "postgresql+asyncpg://user:pass@localhost/test",
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 60,
            "pool_recycle": 7200,
            "pool_pre_ping": False,
            "echo": True
        }

        # Act
        engine = DatabaseEngine(**config)

        # Assert
        assert engine._database_url == config["database_url"]
        assert engine._pool_size == config["pool_size"]
        assert engine._max_overflow == config["max_overflow"]
        assert engine._pool_timeout == config["pool_timeout"]
        assert engine._pool_recycle == config["pool_recycle"]
        assert engine._pool_pre_ping == config["pool_pre_ping"]
        assert engine._echo == config["echo"]

    @patch('mindbridge.database.connection.create_async_engine')
    def test_engine_property_lazy_initialization(self, mock_create_engine: Mock) -> None:
        """Expected use case: Engine property should create engine lazily."""
        # Arrange
        mock_engine = Mock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        db_engine = DatabaseEngine("postgresql+asyncpg://user:pass@localhost/test")

        # Act
        engine1 = db_engine.engine
        engine2 = db_engine.engine

        # Assert
        assert engine1 is mock_engine
        assert engine2 is mock_engine
        assert mock_create_engine.call_count == 1  # Only called once

    @patch('mindbridge.database.connection.async_sessionmaker')
    @patch('mindbridge.database.connection.create_async_engine')
    def test_session_factory_property(self, mock_create_engine: Mock, mock_sessionmaker: Mock) -> None:
        """Expected use case: Session factory property should create factory lazily."""
        # Arrange
        mock_engine = Mock(spec=AsyncEngine)
        mock_factory = Mock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = mock_factory

        db_engine = DatabaseEngine("postgresql+asyncpg://user:pass@localhost/test")

        # Act
        factory1 = db_engine.session_factory
        factory2 = db_engine.session_factory

        # Assert
        assert factory1 is mock_factory
        assert factory2 is mock_factory
        assert mock_sessionmaker.call_count == 1  # Only called once

    @pytest.mark.asyncio
    @patch('mindbridge.database.connection.async_sessionmaker')
    @patch('mindbridge.database.connection.create_async_engine')
    async def test_get_session_success(self, mock_create_engine: Mock, mock_sessionmaker: Mock) -> None:
        """Expected use case: Get session should yield working session."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Create a proper async context manager mock
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_factory = Mock()
        mock_factory.return_value = mock_session_context

        mock_sessionmaker.return_value = mock_factory
        mock_create_engine.return_value = Mock(spec=AsyncEngine)

        db_engine = DatabaseEngine("postgresql+asyncpg://user:pass@localhost/test")

        # Act
        async with db_engine.get_session() as session:
            # Assert
            assert session is mock_session

    @pytest.mark.asyncio
    @patch('mindbridge.database.connection.async_sessionmaker')
    @patch('mindbridge.database.connection.create_async_engine')
    async def test_get_session_rollback_on_exception(self, mock_create_engine: Mock, mock_sessionmaker: Mock) -> None:
        """Failure case: Session should rollback on exception."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Create a proper async context manager mock
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_factory = Mock()
        mock_factory.return_value = mock_session_context

        mock_sessionmaker.return_value = mock_factory
        mock_create_engine.return_value = Mock(spec=AsyncEngine)

        db_engine = DatabaseEngine("postgresql+asyncpg://user:pass@localhost/test")

        # Act & Assert
        with pytest.raises(RuntimeError):
            async with db_engine.get_session():
                raise RuntimeError("Test exception")

        # Assert rollback was called
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    @patch('mindbridge.database.connection.create_async_engine')
    async def test_close_engine(self, mock_create_engine: Mock) -> None:
        """Expected use case: Close should dispose engine and reset state."""
        # Arrange
        mock_engine = AsyncMock(spec=AsyncEngine)
        mock_create_engine.return_value = mock_engine

        db_engine = DatabaseEngine("postgresql+asyncpg://user:pass@localhost/test")
        _ = db_engine.engine  # Initialize engine

        # Act
        await db_engine.close()

        # Assert
        mock_engine.dispose.assert_called_once()
        assert db_engine._engine is None
        assert db_engine._session_factory is None

    @pytest.mark.asyncio
    async def test_close_engine_when_not_initialized(self) -> None:
        """Edge case: Close should work even when engine not initialized."""
        # Arrange
        db_engine = DatabaseEngine("postgresql+asyncpg://user:pass@localhost/test")

        # Act & Assert (should not raise)
        await db_engine.close()


class TestGlobalEngineManagement:
    """Test cases for global engine management functions."""

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://user:pass@localhost/test"})
    @patch('mindbridge.database.connection.DatabaseEngine')
    def test_get_async_engine_success(self, mock_db_engine_class: Mock) -> None:
        """Expected use case: Get async engine with environment configuration."""
        # Arrange
        mock_engine_instance = Mock()
        mock_db_engine_class.return_value = mock_engine_instance

        # Act
        engine = get_async_engine()

        # Assert
        assert engine is mock_engine_instance
        mock_db_engine_class.assert_called_once()

    @patch('mindbridge.database.connection._database_engine', None)
    def test_get_async_engine_missing_url_fails(self) -> None:
        """Failure case: Get async engine without DATABASE_URL should fail."""
        # Arrange
        with patch.dict(os.environ, {}, clear=True), pytest.raises(RuntimeError, match="DATABASE_URL environment variable is required"):
            get_async_engine()

    @patch.dict(os.environ, {
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost/test",
        "DB_POOL_SIZE": "15",
        "DB_MAX_OVERFLOW": "25",
        "DB_ECHO": "true"
    })
    @patch('mindbridge.database.connection._database_engine', None)
    @patch('mindbridge.database.connection.DatabaseEngine')
    def test_get_async_engine_with_env_config(self, mock_db_engine_class: Mock) -> None:
        """Expected use case: Get async engine with environment variables."""
        # Arrange
        mock_engine_instance = Mock()
        mock_db_engine_class.return_value = mock_engine_instance

        # Act
        get_async_engine()

        # Assert
        mock_db_engine_class.assert_called_once_with(
            database_url="postgresql+asyncpg://user:pass@localhost/test",
            pool_size=15,
            max_overflow=25,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=True
        )

    @patch('mindbridge.database.connection._database_engine')
    @pytest.mark.asyncio
    async def test_close_database_engine_success(self, mock_engine: Mock) -> None:
        """Expected use case: Close global database engine."""
        # Arrange
        mock_engine.close = AsyncMock()

        # Act
        await close_database_engine()

        # Assert
        mock_engine.close.assert_called_once()

    @patch('mindbridge.database.connection._database_engine', None)
    @pytest.mark.asyncio
    async def test_close_database_engine_when_none(self) -> None:
        """Edge case: Close database engine when not initialized."""
        # Act & Assert (should not raise)
        await close_database_engine()

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://user:pass@localhost/test"})
    def test_get_async_engine_singleton_behavior(self) -> None:
        """Expected use case: get_async_engine should return same instance."""
        # Act
        engine1 = get_async_engine()
        engine2 = get_async_engine()

        # Assert
        assert engine1 is engine2  # Same instance

