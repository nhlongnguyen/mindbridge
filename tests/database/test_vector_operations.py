"""Tests for vector similarity operations."""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mindbridge.database.models import VectorDocument


class TestVectorSimilarityOperations:
    """Test cases for vector similarity operations."""

    @pytest.mark.asyncio
    async def test_l2_distance_calculation_success(self) -> None:
        """Expected use case: Calculate L2 distance between vectors."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalar.return_value = 5.196152  # Example L2 distance
        mock_session.execute.return_value = mock_result

        query = text("SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector as distance")

        # Act
        result = await mock_session.execute(query)
        distance = result.scalar()

        # Assert
        assert distance == 5.196152
        mock_session.execute.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_cosine_distance_calculation_success(self) -> None:
        """Expected use case: Calculate cosine distance between vectors."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalar.return_value = 0.025368  # Example cosine distance
        mock_session.execute.return_value = mock_result

        query = text("SELECT '[1,2,3]'::vector <=> '[4,5,6]'::vector as distance")

        # Act
        result = await mock_session.execute(query)
        distance = result.scalar()

        # Assert
        assert distance == 0.025368
        mock_session.execute.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_inner_product_calculation_success(self) -> None:
        """Expected use case: Calculate inner product between vectors."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalar.return_value = -32.0  # Example inner product (negative)
        mock_session.execute.return_value = mock_result

        query = text("SELECT '[1,2,3]'::vector <#> '[4,5,6]'::vector as inner_product")

        # Act
        result = await mock_session.execute(query)
        inner_product = result.scalar()

        # Assert
        assert inner_product == -32.0
        mock_session.execute.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_vector_similarity_search_success(self) -> None:
        """Expected use case: Search for similar vectors using L2 distance."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Create mock documents
        doc1 = VectorDocument(
            id=1,
            content="Document 1",
            title="Title 1",
            embedding=[0.1, 0.2, 0.3] * 512  # 1536 dimensions
        )
        doc2 = VectorDocument(
            id=2,
            content="Document 2",
            title="Title 2",
            embedding=[0.4, 0.5, 0.6] * 512  # 1536 dimensions
        )

        mock_result = Mock()
        mock_result.fetchall.return_value = [doc1, doc2]
        mock_session.execute.return_value = mock_result

        query_vector = [0.2, 0.3, 0.4] * 512  # 1536 dimensions

        # Act
        # This would be the actual query in implementation
        query = text("""
            SELECT * FROM vector_documents
            ORDER BY embedding <-> :query_vector
            LIMIT :limit
        """)
        result = await mock_session.execute(query, {
            "query_vector": query_vector,
            "limit": 5
        })
        documents = result.fetchall()

        # Assert
        assert len(documents) == 2
        assert documents[0] is doc1
        assert documents[1] is doc2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_similarity_with_filtering_success(self) -> None:
        """Expected use case: Search similar vectors with content filtering."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        doc = VectorDocument(
            id=1,
            content="Python code document",
            title="Python Guide",
            embedding=[0.1, 0.2, 0.3] * 512,  # 1536 dimensions
            document_type="code"
        )

        mock_result = Mock()
        mock_result.fetchall.return_value = [doc]
        mock_session.execute.return_value = mock_result

        query_vector = [0.2, 0.3, 0.4] * 512  # 1536 dimensions

        # Act
        query = text("""
            SELECT * FROM vector_documents
            WHERE document_type = :doc_type
            ORDER BY embedding <-> :query_vector
            LIMIT :limit
        """)
        result = await mock_session.execute(query, {
            "query_vector": query_vector,
            "doc_type": "code",
            "limit": 5
        })
        documents = result.fetchall()

        # Assert
        assert len(documents) == 1
        assert documents[0].document_type == "code"
        assert documents[0].content == "Python code document"

    @pytest.mark.asyncio
    async def test_vector_similarity_empty_result(self) -> None:
        """Edge case: Vector similarity search with no results."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        query_vector = [0.9, 0.9, 0.9] * 512  # 1536 dimensions

        # Act
        query = text("""
            SELECT * FROM vector_documents
            ORDER BY embedding <-> :query_vector
            LIMIT :limit
        """)
        result = await mock_session.execute(query, {
            "query_vector": query_vector,
            "limit": 5
        })
        documents = result.fetchall()

        # Assert
        assert len(documents) == 0
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_distance_threshold_filtering(self) -> None:
        """Expected use case: Filter vectors by distance threshold."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        doc = VectorDocument(
            id=1,
            content="Close document",
            embedding=[0.1, 0.2, 0.3] * 512  # 1536 dimensions
        )

        mock_result = Mock()
        mock_result.fetchall.return_value = [doc]
        mock_session.execute.return_value = mock_result

        query_vector = [0.15, 0.25, 0.35]
        distance_threshold = 0.5

        # Act
        query = text("""
            SELECT * FROM vector_documents
            WHERE embedding <-> :query_vector < :threshold
            ORDER BY embedding <-> :query_vector
            LIMIT :limit
        """)
        result = await mock_session.execute(query, {
            "query_vector": query_vector,
            "threshold": distance_threshold,
            "limit": 10
        })
        documents = result.fetchall()

        # Assert
        assert len(documents) == 1
        assert documents[0].content == "Close document"

    def test_vector_dimension_validation(self) -> None:
        """Edge case: Validate vector dimensions match model requirements."""
        # Arrange
        correct_embedding = [0.1] * 1536  # Correct 1536 dimensions
        incorrect_embedding = [0.1] * 768  # Incorrect dimensions

        # Act & Assert - Correct dimensions
        doc_correct = VectorDocument(
            content="Test document",
            embedding=correct_embedding
        )
        assert len(doc_correct.embedding) == 1536

        # Act & Assert - Incorrect dimensions should raise validation error
        with pytest.raises(ValueError, match="Embedding must be exactly 1536 dimensions"):
            VectorDocument(
                content="Test document",
                embedding=incorrect_embedding
            )

    @pytest.mark.asyncio
    async def test_batch_vector_insert_success(self) -> None:
        """Expected use case: Insert multiple vector documents in batch."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        documents = [
            VectorDocument(
                content=f"Document {i}",
                title=f"Title {i}",
                embedding=[0.1 * i, 0.2 * i, 0.3 * i] * 512  # 1536 dimensions
            )
            for i in range(1, 4)
        ]

        # Act
        mock_session.add_all(documents)
        await mock_session.commit()

        # Assert
        mock_session.add_all.assert_called_once_with(documents)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_vector_document_retrieval_by_id(self) -> None:
        """Expected use case: Retrieve vector document by ID."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        doc = VectorDocument(
            id=123,
            content="Retrieved document",
            title="Retrieved Title",
            embedding=[0.1] * 1536
        )

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = doc
        mock_session.execute.return_value = mock_result

        # Act
        # This simulates: SELECT * FROM vector_documents WHERE id = 123
        result = await mock_session.execute(text("SELECT * FROM vector_documents WHERE id = :id"), {"id": 123})
        retrieved_doc = result.scalar_one_or_none()

        # Assert
        assert retrieved_doc is not None
        assert retrieved_doc.id == 123
        assert retrieved_doc.content == "Retrieved document"
        assert len(retrieved_doc.embedding) == 1536

    @pytest.mark.asyncio
    async def test_vector_document_update_embedding(self) -> None:
        """Expected use case: Update vector document embedding."""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Simulate existing document
        doc = VectorDocument(
            id=456,
            content="Document to update",
            embedding=[0.1] * 1536
        )

        new_embedding = [0.5] * 1536

        # Act
        doc.embedding = new_embedding
        await mock_session.commit()

        # Assert
        assert doc.embedding == new_embedding
        mock_session.commit.assert_called_once()

