"""Initial database setup with Repository, Document, Job, and VectorDocument models

Revision ID: 2ec9b2e8a63e
Revises:
Create Date: 2025-06-29 12:12:50.244669

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "2ec9b2e8a63e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create repositories table
    op.create_table(
        "repositories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "branch", sa.String(length=100), nullable=False, server_default="main"
        ),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )

    # Create documents table
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file_path", sa.String(length=1000), nullable=True),
        sa.Column("file_type", sa.String(length=100), nullable=True),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create jobs table
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="pending"
        ),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create vector_documents table
    op.create_table(
        "vector_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("source_url", sa.String(length=2000), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=True),
        sa.Column("repository_id", sa.Integer(), nullable=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_repositories_name", "repositories", ["name"])
    op.create_index("ix_repositories_url", "repositories", ["url"])
    op.create_index("ix_repositories_status", "repositories", ["status"])
    op.create_index("ix_repositories_created_at", "repositories", ["created_at"])

    op.create_index("ix_documents_repository_id", "documents", ["repository_id"])
    op.create_index("ix_documents_title", "documents", ["title"])
    op.create_index("ix_documents_file_type", "documents", ["file_type"])
    op.create_index("ix_documents_created_at", "documents", ["created_at"])

    op.create_index("ix_jobs_repository_id", "jobs", ["repository_id"])
    op.create_index("ix_jobs_job_type", "jobs", ["job_type"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])
    op.create_index("ix_jobs_started_at", "jobs", ["started_at"])
    op.create_index("ix_jobs_completed_at", "jobs", ["completed_at"])

    op.create_index(
        "ix_vector_documents_repository_id", "vector_documents", ["repository_id"]
    )
    op.create_index(
        "ix_vector_documents_document_id", "vector_documents", ["document_id"]
    )
    op.create_index(
        "ix_vector_documents_document_type", "vector_documents", ["document_type"]
    )
    op.create_index(
        "ix_vector_documents_created_at", "vector_documents", ["created_at"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index("ix_vector_documents_created_at", "vector_documents")
    op.drop_index("ix_vector_documents_document_type", "vector_documents")
    op.drop_index("ix_vector_documents_document_id", "vector_documents")
    op.drop_index("ix_vector_documents_repository_id", "vector_documents")

    op.drop_index("ix_jobs_completed_at", "jobs")
    op.drop_index("ix_jobs_started_at", "jobs")
    op.drop_index("ix_jobs_created_at", "jobs")
    op.drop_index("ix_jobs_status", "jobs")
    op.drop_index("ix_jobs_job_type", "jobs")
    op.drop_index("ix_jobs_repository_id", "jobs")

    op.drop_index("ix_documents_created_at", "documents")
    op.drop_index("ix_documents_file_type", "documents")
    op.drop_index("ix_documents_title", "documents")
    op.drop_index("ix_documents_repository_id", "documents")

    op.drop_index("ix_repositories_created_at", "repositories")
    op.drop_index("ix_repositories_status", "repositories")
    op.drop_index("ix_repositories_url", "repositories")
    op.drop_index("ix_repositories_name", "repositories")

    # Drop tables (in reverse order due to foreign key constraints)
    op.drop_table("vector_documents")
    op.drop_table("jobs")
    op.drop_table("documents")
    op.drop_table("repositories")
