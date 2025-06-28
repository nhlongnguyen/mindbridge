-- Initialize database with pgvector extension and basic schema
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic schema structure (will be managed by Alembic migrations)
-- This is just for initial setup