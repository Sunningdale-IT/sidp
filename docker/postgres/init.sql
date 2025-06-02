-- Create additional user for testing
CREATE USER idp_test WITH PASSWORD 'test_password';
GRANT ALL PRIVILEGES ON DATABASE idp TO idp_test;

-- Enable necessary extensions
\c idp;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c keycloak;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 
