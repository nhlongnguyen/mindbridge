"""Global test configuration and fixtures for Mindbridge tests."""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from typing import Any, Dict, Union
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Set test environment variables
os.environ.setdefault(
    "DATABASE_URL", "postgresql://test:test@localhost:5432/mindbridge_test"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture  # type: ignore[misc]
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints."""
    # This will be implemented once FastAPI app is created
    async with AsyncClient(base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_database() -> MagicMock:
    """Mock database connection for unit tests."""
    return MagicMock()


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock Redis connection for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_embedding_service() -> AsyncMock:
    """Mock embedding service for testing."""
    mock = AsyncMock()
    mock.generate_embedding.return_value = [0.1] * 384  # Mock embedding vector
    return mock


@pytest.fixture
def sample_repository_data() -> Dict[str, str | int]:
    """Sample repository data for testing."""
    return {
        "name": "test-repo",
        "url": "https://github.com/test/test-repo",
        "branch": "main",
        "description": "A test repository",
        "language": "Python",
        "stars": 100,
        "forks": 20,
    }


@pytest.fixture
def sample_document_data() -> Dict[str, str | Dict[str, str]]:
    """Sample document data for testing."""
    return {
        "title": "Test Document",
        "content": "This is a test document with some content for testing purposes.",
        "file_path": "docs/test.md",
        "file_type": "markdown",
        "metadata": {
            "author": "Test Author",
            "created_at": "2024-01-01T00:00:00Z",
        },
    }


@pytest.fixture
def sample_search_query() -> Dict[str, str | Dict[str, str] | int]:
    """Sample search query for testing."""
    return {
        "query": "How to implement async functions in Python?",
        "filters": {
            "language": "Python",
            "file_type": "markdown",
        },
        "limit": 10,
    }
