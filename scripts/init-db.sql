-- Initialize database with pgvector extension and optimized configuration
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_stat_statements for query monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Performance optimizations for pgvector operations
-- Increase maintenance_work_mem for faster index builds
SET maintenance_work_mem = '1GB';

-- Set optimal parallel workers for index operations
SET max_parallel_maintenance_workers = 7;

-- Configure shared buffers for better performance (if not set globally)
-- Note: This would typically be set in postgresql.conf
-- SHOW shared_buffers; -- Check current value

-- Create basic schema structure (will be managed by Alembic migrations)
-- This is just for initial setup and extension verification

-- Test vector operations to ensure pgvector is working
DO $$
BEGIN
    -- Test basic vector operations
    PERFORM '[1,2,3]'::vector <-> '[4,5,6]'::vector;
    RAISE NOTICE 'pgvector extension is working correctly';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'pgvector extension test failed: %', SQLERRM;
END$$;

-- Vector indexes for similarity search performance
-- Note: These will be created after vector_documents table is created by migrations

-- IVFFlat index for L2 distance (euclidean) - good for general use
-- Lists parameter should be approximately sqrt(total_rows)
-- For 100k+ vectors, use 100-1000 lists
CREATE INDEX IF NOT EXISTS vec_docs_embedding_ivfflat_l2_idx
ON vector_documents USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- HNSW index for cosine similarity - better for high-dimensional data
-- m = 16 is good default, ef_construction = 64 balances build time vs quality
CREATE INDEX IF NOT EXISTS vec_docs_embedding_hnsw_cosine_idx
ON vector_documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat index for inner product similarity
CREATE INDEX IF NOT EXISTS vec_docs_embedding_ivfflat_ip_idx
ON vector_documents USING ivfflat (embedding vector_ip_ops)
WITH (lists = 100);

-- Update table statistics for query planner optimization
ANALYZE vector_documents;
