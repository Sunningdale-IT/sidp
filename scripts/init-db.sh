#!/bin/bash

# Database initialization script
# Checks and creates databases if they don't exist

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[DB-INIT]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Database configuration
DB_HOST=${DB_HOST:-postgres}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_NAME=${DB_NAME:-idp}
DB_TEST_NAME=${DB_NAME}_test

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c '\q' 2>/dev/null; then
            log "PostgreSQL is ready!"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - PostgreSQL is starting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "PostgreSQL failed to start after $max_attempts attempts"
    return 1
}

# Check if database exists
database_exists() {
    local db_name=$1
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db_name'" | grep -q 1
}

# Create database if it doesn't exist
create_database() {
    local db_name=$1
    log "Creating database: $db_name"
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $db_name
}

# Create user if it doesn't exist
create_user() {
    local username=$1
    local password=$2
    log "Creating database user: $username"
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE USER $username WITH PASSWORD '$password';" 2>/dev/null || true
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $username;" 2>/dev/null || true
}

# Enable extensions
enable_extensions() {
    local db_name=$1
    log "Enabling extensions for database: $db_name"
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $db_name -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null || true
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $db_name -c "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";" 2>/dev/null || true
}

# Create Django default users
create_django_users() {
    log "Creating Django default users..."
    
    # Check if Django is available and database is migrated
    if python manage.py check --database=default >/dev/null 2>&1; then
        # Run the management command to create default users
        python manage.py create_default_users
        log "Django default users created successfully!"
    else
        warn "Django not ready yet - users will be created after migrations"
    fi
}

# Main initialization function
init_database() {
    log "Starting database initialization..."
    
    # Wait for PostgreSQL
    if ! wait_for_postgres; then
        error "Failed to connect to PostgreSQL"
        exit 1
    fi
    
    # Check and create main database
    if database_exists $DB_NAME; then
        info "Database $DB_NAME already exists"
    else
        create_database $DB_NAME
        log "Database $DB_NAME created successfully"
    fi
    
    # Check and create test database
    if database_exists $DB_TEST_NAME; then
        info "Test database $DB_TEST_NAME already exists"
    else
        create_database $DB_TEST_NAME
        log "Test database $DB_TEST_NAME created successfully"
    fi
    
    # Create additional database user for testing
    create_user "idp_test" "test_password"
    
    # Enable extensions
    enable_extensions $DB_NAME
    enable_extensions $DB_TEST_NAME
    
    log "Database initialization completed successfully!"
}

# Main function that can be called with parameters
main() {
    local create_users=${1:-true}
    
    # Always run database initialization
    init_database
    
    # Create Django users if requested and Django is available
    if [ "$create_users" = "true" ]; then
        create_django_users
    fi
}

# Run initialization
# If called with "no-users" parameter, skip user creation
main "${1:-true}" 
