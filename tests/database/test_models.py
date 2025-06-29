"""Tests for database models."""

import pytest
from mindbridge.database.models import Base, Document, Job, Repository, VectorDocument


class TestVectorDocument:
    """Test cases for VectorDocument model."""

    def test_vector_document_creation_success(self) -> None:
        """Expected use case: Create VectorDocument with valid data."""
        # Arrange
        content = "This is a test document for vector analysis."
        title = "Test Document"
        source_url = "https://example.com/doc1"
        embedding = [0.1, 0.2, 0.3] * 512  # Creates 1536 dimensions (3 * 512 = 1536)

        # Act
        doc = VectorDocument(
            content=content, title=title, source_url=source_url, embedding=embedding
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
        doc = VectorDocument(content=content, embedding=embedding)

        # Assert
        assert doc.content == content
        assert doc.embedding == embedding
        assert doc.title is None
        assert doc.source_url is None
        assert doc.document_type is None
        assert doc.repository_id is None
        assert doc.file_path is None

    def test_vector_document_invalid_embedding_fails(self) -> None:
        """Failure case: VectorDocument with invalid embedding should fail validation."""
        # Arrange
        content = "Test content"

        # Act & Assert - Wrong dimension count
        with pytest.raises(
            ValueError, match="Embedding must be exactly 1536 dimensions"
        ):
            VectorDocument(content=content, embedding=[0.1] * 768)  # Wrong dimensions

        # Act & Assert - Non-list embedding
        with pytest.raises(ValueError, match="Embedding must be a list of floats"):
            VectorDocument(content=content, embedding="not a list")  # Wrong type

        # Act & Assert - Invalid values in embedding
        with pytest.raises(ValueError, match="All embedding values must be numbers"):
            VectorDocument(
                content=content,
                embedding=[0.1] * 1535 + ["not a number"],  # Invalid value
            )

    def test_vector_document_repr(self) -> None:
        """Expected use case: String representation of VectorDocument."""
        # Arrange
        doc = VectorDocument(
            content="Test content", title="Test Title", embedding=[0.1] * 1536
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
            "file_path": "src/main.py",
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
        doc = VectorDocument(content=long_content, embedding=embedding)

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
        doc = VectorDocument(content=content, title=title, embedding=embedding)

        # Assert
        assert doc.content == content
        assert doc.title == title
        assert doc.embedding == embedding


class TestBase:
    """Test cases for Base model class."""

    def test_base_is_declarative_base(self) -> None:
        """Expected use case: Base should be a proper SQLAlchemy declarative base."""
        # Act & Assert
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")
        # Base class itself doesn't have __tablename__, only concrete models do

    def test_base_has_async_attrs(self) -> None:
        """Expected use case: Base should support async attributes."""
        # Act & Assert
        # AsyncAttrs mixin should be present
        assert hasattr(Base, "__await__") or "AsyncAttrs" in str(Base.__mro__)

    def test_vector_document_inherits_from_base(self) -> None:
        """Expected use case: VectorDocument should inherit from Base."""
        # Act & Assert
        assert issubclass(VectorDocument, Base)
        assert hasattr(VectorDocument, "metadata")
        assert VectorDocument.__tablename__ == "vector_documents"


class TestRepository:
    """Test cases for Repository model."""

    def test_repository_creation_success(self) -> None:
        """Expected use case: Create Repository with valid data."""
        # Arrange
        name = "test-repo"
        url = "https://github.com/user/test-repo"
        description = "A test repository"

        # Act
        repo = Repository(name=name, url=url, description=description)

        # Assert
        assert repo.name == name
        assert repo.url == url
        assert repo.description == description
        assert repo.id is None  # Not yet persisted
        assert (
            repo.status is None or repo.status == "pending"
        )  # Default applied at DB level
        assert repo.created_at is None  # Will be set by database
        assert repo.updated_at is None  # Will be set by database

    def test_repository_minimal_creation(self) -> None:
        """Edge case: Create Repository with only required fields."""
        # Arrange
        name = "minimal-repo"
        url = "https://github.com/user/minimal-repo"

        # Act
        repo = Repository(name=name, url=url)

        # Assert
        assert repo.name == name
        assert repo.url == url
        assert repo.description is None
        assert (
            repo.status is None or repo.status == "pending"
        )  # Default applied at DB level
        assert (
            repo.branch is None or repo.branch == "main"
        )  # Default applied at DB level

    def test_repository_invalid_url_fails(self) -> None:
        """Failure case: Repository with invalid URL should fail validation."""
        # Arrange
        name = "test-repo"

        # Act & Assert - Invalid URL format
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            Repository(name=name, url="not-a-valid-url")

        # Act & Assert - Non-GitHub URL
        with pytest.raises(ValueError, match="URL must be a GitHub repository"):
            Repository(name=name, url="https://gitlab.com/user/repo")

    def test_repository_invalid_status_fails(self) -> None:
        """Failure case: Repository with invalid status should fail validation."""
        # Arrange
        name = "test-repo"
        url = "https://github.com/user/test-repo"

        # Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            Repository(name=name, url=url, status="invalid_status")

    def test_repository_relationships(self) -> None:
        """Expected use case: Repository should support relationships."""
        # Arrange
        repo = Repository(name="test-repo", url="https://github.com/user/test-repo")

        # Act & Assert
        assert hasattr(repo, "documents")
        assert hasattr(repo, "jobs")

    def test_repository_repr(self) -> None:
        """Expected use case: String representation of Repository."""
        # Arrange
        repo = Repository(name="test-repo", url="https://github.com/user/test-repo")
        repo.id = 1

        # Act
        repr_str = repr(repo)

        # Assert
        assert "Repository" in repr_str
        assert "id=1" in repr_str
        assert "name='test-repo'" in repr_str


class TestDocument:
    """Test cases for Document model."""

    def test_document_creation_success(self) -> None:
        """Expected use case: Create Document with valid data."""
        # Arrange
        title = "test.py"
        content = "print('Hello, World!')"
        file_path = "src/test.py"
        file_type = "python"
        repository_id = 1

        # Act
        doc = Document(
            title=title,
            content=content,
            file_path=file_path,
            file_type=file_type,
            repository_id=repository_id,
        )

        # Assert
        assert doc.title == title
        assert doc.content == content
        assert doc.file_path == file_path
        assert doc.file_type == file_type
        assert doc.repository_id == repository_id
        assert doc.id is None  # Not yet persisted
        assert doc.created_at is None  # Will be set by database
        assert doc.updated_at is None  # Will be set by database

    def test_document_minimal_creation(self) -> None:
        """Edge case: Create Document with only required fields."""
        # Arrange
        title = "minimal.txt"
        content = "Minimal content"
        repository_id = 1

        # Act
        doc = Document(title=title, content=content, repository_id=repository_id)

        # Assert
        assert doc.title == title
        assert doc.content == content
        assert doc.repository_id == repository_id
        assert doc.file_path is None
        assert doc.file_type is None

    def test_document_empty_content_fails(self) -> None:
        """Failure case: Document with empty content should fail validation."""
        # Arrange
        title = "empty.txt"
        repository_id = 1

        # Act & Assert
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Document(title=title, content="", repository_id=repository_id)

        with pytest.raises(ValueError, match="Content cannot be empty"):
            Document(title=title, content=None, repository_id=repository_id)

    def test_document_relationships(self) -> None:
        """Expected use case: Document should support relationships."""
        # Arrange
        doc = Document(title="test.py", content="test", repository_id=1)

        # Act & Assert
        assert hasattr(doc, "repository")
        assert hasattr(doc, "vector_documents")

    def test_document_repr(self) -> None:
        """Expected use case: String representation of Document."""
        # Arrange
        doc = Document(title="test.py", content="test content", repository_id=1)
        doc.id = 2

        # Act
        repr_str = repr(doc)

        # Assert
        assert "Document" in repr_str
        assert "id=2" in repr_str
        assert "title='test.py'" in repr_str


class TestJob:
    """Test cases for Job model."""

    def test_job_creation_success(self) -> None:
        """Expected use case: Create Job with valid data."""
        # Arrange
        repository_id = 1
        job_type = "analysis"
        params = {"include_tests": True, "max_depth": 5}

        # Act
        job = Job(repository_id=repository_id, job_type=job_type, params=params)

        # Assert
        assert job.repository_id == repository_id
        assert job.job_type == job_type
        assert job.params == params
        assert job.id is None  # Not yet persisted
        assert (
            job.status is None or job.status == "pending"
        )  # Default applied at DB level
        assert job.created_at is None  # Will be set by database
        assert job.updated_at is None  # Will be set by database
        assert job.started_at is None
        assert job.completed_at is None

    def test_job_minimal_creation(self) -> None:
        """Edge case: Create Job with only required fields."""
        # Arrange
        repository_id = 1
        job_type = "embedding"

        # Act
        job = Job(repository_id=repository_id, job_type=job_type)

        # Assert
        assert job.repository_id == repository_id
        assert job.job_type == job_type
        assert job.params is None
        assert (
            job.status is None or job.status == "pending"
        )  # Default applied at DB level

    def test_job_invalid_status_fails(self) -> None:
        """Failure case: Job with invalid status should fail validation."""
        # Arrange
        repository_id = 1
        job_type = "analysis"

        # Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            Job(repository_id=repository_id, job_type=job_type, status="invalid_status")

    def test_job_invalid_job_type_fails(self) -> None:
        """Failure case: Job with invalid job_type should fail validation."""
        # Arrange
        repository_id = 1

        # Act & Assert
        with pytest.raises(ValueError, match="Job type must be one of"):
            Job(repository_id=repository_id, job_type="invalid_type")

    def test_job_relationships(self) -> None:
        """Expected use case: Job should support relationships."""
        # Arrange
        job = Job(repository_id=1, job_type="analysis")

        # Act & Assert
        assert hasattr(job, "repository")

    def test_job_repr(self) -> None:
        """Expected use case: String representation of Job."""
        # Arrange
        job = Job(repository_id=1, job_type="analysis")
        job.id = 3

        # Act
        repr_str = repr(job)

        # Assert
        assert "Job" in repr_str
        assert "id=3" in repr_str
        assert "type='analysis'" in repr_str
        # Status could be None or 'pending' since defaults are applied at DB level
        assert "status=" in repr_str
