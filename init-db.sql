-- Database initialization script for FastAPI application
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS app_schema;

-- Set default permissions
GRANT ALL PRIVILEGES ON DATABASE fastapi_app_db TO fastapi_user;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- You can add more initialization commands here
-- For example, creating additional users or setting up specific configurations

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully for FastAPI application';
END $$; 