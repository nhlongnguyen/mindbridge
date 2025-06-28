"""Tests for database models."""


import pytest

from mindbridge.database.models import Base, VectorDocument


class TestVectorDocument:
    """Test cases for VectorDocument model."""

    def test_vector_document_creation_success(self) -> None:
        """Expected use case: Create VectorDocument with valid data."""
        # Arrange
        content = "This is a test document for vector analysis."
        title = "Test Document"
        source_url = "https://example.com/doc1"
        embedding = [0.1, 0.2, 0.3] * 512  # 1536 dimensions

        # Act
        doc = VectorDocument(
            content=content,
            title=title,
            source_url=source_url,
            embedding=embedding
        )

        # Assert
        assert doc.content == content
        assert doc.title == title
        assert doc.source_url == source_url
        assert doc.embedding == embedding
        assert doc.id is None  # Not yet persisted
        assert doc.created_at is None  # Will be set by database
        assert doc.updated_at is None  # Will be set by database

    def test_vector_document_minimal_creation(self) -> None:
        """Edge case: Create VectorDocument with only required fields."""
        # Arrange
        content = "Minimal test document."
        embedding = [0.0] * 1536  # Exact dimension requirement

        # Act
        doc = VectorDocument(
            content=content,
            embedding=embedding
        )

        # Assert
        assert doc.content == content
        assert doc.embedding == embedding
        assert doc.title is None
        assert doc.source_url is None
        assert doc.document_type is None
        assert doc.repository_id is None
        assert doc.file_path is None

    def test_vector_document_empty_content_fails(self) -> None:
        """Failure case: VectorDocument with empty content should fail validation."""
        # Arrange
        embedding = [0.1] * 1536

        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            VectorDocument(
                content="",  # Empty content should fail
                embedding=embedding
            )

    def test_vector_document_repr(self) -> None:
        """Expected use case: String representation of VectorDocument."""
        # Arrange
        doc = VectorDocument(
            content="Test content",
            title="Test Title",
            embedding=[0.1] * 1536
        )
        doc.id = 123  # Simulate database-assigned ID

        # Act
        repr_str = repr(doc)

        # Assert
        assert "VectorDocument" in repr_str
        assert "id=123" in repr_str
        assert "title='Test Title'" in repr_str

    def test_vector_document_with_metadata(self) -> None:
        """Expected use case: VectorDocument with all metadata fields."""
        # Arrange
        doc_data = {
            "content": "Document with metadata",
            "title": "Metadata Test",
            "source_url": "https://github.com/user/repo/blob/main/file.py",
            "embedding": [0.5] * 1536,
            "document_type": "code",
            "repository_id": 42,
            "file_path": "src/main.py"
        }

        # Act
        doc = VectorDocument(**doc_data)

        # Assert
        assert doc.content == doc_data["content"]
        assert doc.title == doc_data["title"]
        assert doc.source_url == doc_data["source_url"]
        assert doc.embedding == doc_data["embedding"]
        assert doc.document_type == doc_data["document_type"]
        assert doc.repository_id == doc_data["repository_id"]
        assert doc.file_path == doc_data["file_path"]

    def test_vector_document_long_content(self) -> None:
        """Edge case: VectorDocument with very long content."""
        # Arrange
        long_content = "A" * 10000  # Very long content
        embedding = [0.1] * 1536

        # Act
        doc = VectorDocument(
            content=long_content,
            embedding=embedding
        )

        # Assert
        assert len(doc.content) == 10000
        assert doc.embedding == embedding

    def test_vector_document_special_characters(self) -> None:
        """Edge case: VectorDocument with special characters and unicode."""
        # Arrange
        content = "Document with unicode: 你好世界 and special chars: !@#$%^&*()"
        title = "Special chars: <script>alert('xss')</script>"
        embedding = [0.1] * 1536

        # Act
        doc = VectorDocument(
            content=content,
            title=title,
            embedding=embedding
        )

        # Assert
        assert doc.content == content
        assert doc.title == title
        assert doc.embedding == embedding


class TestBase:
    """Test cases for Base model class."""

    def test_base_is_declarative_base(self) -> None:
        """Expected use case: Base should be a proper SQLAlchemy declarative base."""
        # Act & Assert
        assert hasattr(Base, '__tablename__')
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')

    def test_base_has_async_attrs(self) -> None:
        """Expected use case: Base should support async attributes."""
        # Act & Assert
        # AsyncAttrs mixin should be present
        assert hasattr(Base, '__await__') or 'AsyncAttrs' in str(Base.__mro__)

    def test_vector_document_inherits_from_base(self) -> None:
        """Expected use case: VectorDocument should inherit from Base."""
        # Act & Assert
        assert issubclass(VectorDocument, Base)
        assert hasattr(VectorDocument, 'metadata')
        assert VectorDocument.__tablename__ == "vector_documents"

