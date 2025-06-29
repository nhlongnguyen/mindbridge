"""Database models with pgvector support."""

import enum
import re
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)


class RepositoryStatus(enum.Enum):
    """Repository status enumeration."""

    PENDING = "pending"
    CLONING = "cloning"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(enum.Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(enum.Enum):
    """Job type enumeration."""

    CLONE = "clone"
    ANALYSIS = "analysis"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    CLEANUP = "cleanup"


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""

    pass


class VectorDocument(Base):
    """Vector document model for storing embeddings and metadata."""

    __tablename__ = "vector_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Vector embedding with 1536 dimensions (OpenAI ada-002 default)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

    # Metadata fields
    document_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    repository_id: Mapped[int | None] = mapped_column(
        ForeignKey("repositories.id"), nullable=True
    )
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository")
    document: Mapped["Document"] = relationship("Document")

    @validates("embedding")  # type: ignore[misc]
    def _validate_embedding(self, key: str, value: Any) -> list[float]:
        """Validate embedding field.

        Args:
            key: Field name
            value: Embedding vector value

        Returns:
            Validated embedding vector

        Raises:
            ValueError: If embedding is invalid
        """
        if not isinstance(value, list):
            raise ValueError("Embedding must be a list of floats")
        if len(value) != 1536:
            raise ValueError(
                f"Embedding must be exactly 1536 dimensions, got {len(value)}"
            )
        if not all(isinstance(x, int | float) for x in value):
            raise ValueError("All embedding values must be numbers")
        return value

    def __repr__(self) -> str:
        """String representation of VectorDocument."""
        return f"<VectorDocument(id={self.id}, title='{self.title}')>"


# Create indexes for VectorDocument
Index("ix_vector_documents_repository_id", VectorDocument.repository_id)
Index("ix_vector_documents_document_id", VectorDocument.document_id)
Index("ix_vector_documents_document_type", VectorDocument.document_type)
Index("ix_vector_documents_created_at", VectorDocument.created_at)


class Repository(Base):
    """Repository model for storing GitHub repository information."""

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    branch: Mapped[str] = mapped_column(String(100), nullable=False, default="main")
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(RepositoryStatus), nullable=False, default=RepositoryStatus.PENDING
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @validates("url")  # type: ignore[misc]
    def _validate_url(self, key: str, value: str) -> str:
        """Validate GitHub URL format.

        Args:
            key: Field name
            value: URL value

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is invalid
        """
        if not value:
            raise ValueError("URL cannot be empty")

        # Basic URL format check
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(url_pattern, value):
            raise ValueError("Invalid GitHub URL format")

        # GitHub-specific validation
        if "github.com" not in value.lower():
            raise ValueError("URL must be a GitHub repository")

        return value

    @validates("status")  # type: ignore[misc]
    def _validate_status(
        self, key: str, value: RepositoryStatus | str
    ) -> RepositoryStatus:
        """Validate repository status.

        Args:
            key: Field name
            value: Status value

        Returns:
            Validated status

        Raises:
            ValueError: If status is invalid
        """
        if isinstance(value, str):
            try:
                return RepositoryStatus(value)
            except ValueError as e:
                valid_values = [status.value for status in RepositoryStatus]
                raise ValueError(
                    f"Status must be one of: {', '.join(valid_values)}"
                ) from e
        return value

    def __repr__(self) -> str:
        """String representation of Repository."""
        return f"<Repository(id={self.id}, name='{self.name}')>"


# Create indexes for Repository
Index("ix_repositories_name", Repository.name)
Index("ix_repositories_url", Repository.url)
Index("ix_repositories_status", Repository.status)
Index("ix_repositories_created_at", Repository.created_at)


class Document(Base):
    """Document model for storing parsed files from repositories."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Foreign key
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id"), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="documents"
    )
    vector_documents: Mapped[list["VectorDocument"]] = relationship(
        "VectorDocument",
        primaryjoin="Document.id == foreign(VectorDocument.document_id)",
        viewonly=True,
    )

    @validates("content")  # type: ignore[misc]
    def _validate_content(self, key: str, value: str | None) -> str:
        """Validate document content.

        Args:
            key: Field name
            value: Content value

        Returns:
            Validated content

        Raises:
            ValueError: If content is invalid
        """
        if not value or (isinstance(value, str) and value.strip() == ""):
            raise ValueError("Content cannot be empty")
        return value

    def __repr__(self) -> str:
        """String representation of Document."""
        return f"<Document(id={self.id}, title='{self.title}')>"


# Create indexes for Document
Index("ix_documents_repository_id", Document.repository_id)
Index("ix_documents_title", Document.title)
Index("ix_documents_file_type", Document.file_type)
Index("ix_documents_created_at", Document.created_at)


class Job(Base):
    """Job model for tracking async processing tasks."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), nullable=False, default=JobStatus.PENDING
    )
    params: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign key
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id"), nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="jobs")

    @validates("status")  # type: ignore[misc]
    def _validate_status(self, key: str, value: JobStatus | str) -> JobStatus:
        """Validate job status.

        Args:
            key: Field name
            value: Status value

        Returns:
            Validated status

        Raises:
            ValueError: If status is invalid
        """
        if isinstance(value, str):
            try:
                return JobStatus(value)
            except ValueError as e:
                valid_values = [status.value for status in JobStatus]
                raise ValueError(
                    f"Status must be one of: {', '.join(valid_values)}"
                ) from e
        return value

    @validates("job_type")  # type: ignore[misc]
    def _validate_job_type(self, key: str, value: JobType | str) -> JobType:
        """Validate job type.

        Args:
            key: Field name
            value: Job type value

        Returns:
            Validated job type

        Raises:
            ValueError: If job type is invalid
        """
        if isinstance(value, str):
            try:
                return JobType(value)
            except ValueError as e:
                valid_values = [job_type.value for job_type in JobType]
                raise ValueError(
                    f"Job type must be one of: {', '.join(valid_values)}"
                ) from e
        return value

    def __repr__(self) -> str:
        """String representation of Job."""
        job_type_value = self.job_type.value if self.job_type else None
        status_value = self.status.value if self.status else None
        return f"<Job(id={self.id}, type='{job_type_value}', status='{status_value}')>"


# Create indexes for Job
Index("ix_jobs_repository_id", Job.repository_id)
Index("ix_jobs_job_type", Job.job_type)
Index("ix_jobs_status", Job.status)
Index("ix_jobs_created_at", Job.created_at)
Index("ix_jobs_started_at", Job.started_at)
Index("ix_jobs_completed_at", Job.completed_at)
