"""Database models with pgvector support."""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    repository_id: Mapped[int | None] = mapped_column(nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        """String representation of VectorDocument."""
        return f"<VectorDocument(id={self.id}, title='{self.title}')>"

