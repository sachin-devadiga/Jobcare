-- JobCare Voice PostgreSQL initialization script
-- Runs on first container startup

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create indexes for common search patterns
CREATE INDEX IF NOT EXISTS idx_pg_trgm_job_title ON jobs_job USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_pg_trgm_company_name ON companies_company USING gin (name gin_trgm_ops);
