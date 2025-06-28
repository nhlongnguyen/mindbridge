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
