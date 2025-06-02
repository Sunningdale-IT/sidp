#!/bin/bash

# Internal Developer Platform - Docker Commands Script
# All operations run in containers - no macOS dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for colored output
log() {
    echo -e "${GREEN}[IDP]${NC} $1"
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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    log "Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url" > /dev/null 2>&1; then
            log "$service is ready!"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - $service is starting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "$service failed to start after $max_attempts attempts"
    return 1
}

# Build all images
build() {
    log "Building Docker images..."
    docker-compose build --parallel
}

# Start core services
start_core() {
    log "Starting core services (PostgreSQL, Redis)..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    log "Waiting for core services..."
    sleep 10
    
    # Check PostgreSQL
    until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
        echo "  PostgreSQL is starting..."
        sleep 2
    done
    log "PostgreSQL is ready!"
    
    # Check Redis
    until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
        echo "  Redis is starting..."
        sleep 2
    done
    log "Redis is ready!"
}

# Start application services
start_app() {
    log "Starting application services..."
    docker-compose up -d web celery celery-beat flower
    
    # Wait for Django
    wait_for_service "Django" "http://localhost:8000/health/"
}

# Full startup
start() {
    check_docker
    build
    start_core
    start_app
    
    log "🎉 Internal Developer Platform is running!"
    info "Access points:"
    info "  Dashboard: http://localhost:8000"
    info "  Admin: http://localhost:8000/admin"
    info "  API Docs: http://localhost:8000/api/schema/swagger-ui/"
    info "  Celery Monitor: http://localhost:5555"
    info ""
    info "Create superuser: ./scripts/docker-commands.sh createsuperuser"
}

# Stop all services
stop() {
    log "Stopping all services..."
    docker-compose down
}

# Restart services
restart() {
    log "Restarting services..."
    stop
    start
}

# Run database migrations in container
migrate() {
    log "Running database migrations..."
    docker-compose exec web ./scripts/init-db.sh
    docker-compose exec web python manage.py migrate
}

# Initialize database
init_db() {
    log "Initializing database..."
    docker-compose exec web ./scripts/init-db.sh
}

# Create superuser in container
createsuperuser() {
    log "Creating superuser..."
    docker-compose exec web python manage.py createsuperuser
}

# Create default users in container
create_users() {
    log "Creating default users..."
    docker-compose exec web python manage.py create_default_users
}

# Reset default user passwords
reset_users() {
    log "Resetting default user passwords..."
    docker-compose exec web python manage.py create_default_users --force
}

# Collect static files in container
collectstatic() {
    log "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput
}

# Run tests in container
test() {
    log "Running tests in container..."
    docker-compose --profile testing run --rm test
}

# Run specific test in container
test_app() {
    local app=$1
    if [ -z "$app" ]; then
        error "Please specify an app to test (e.g., panels, operations, core)"
        exit 1
    fi
    log "Running tests for $app..."
    docker-compose exec web python manage.py test $app --settings=idp.test_settings
}

# Run coverage tests in container
coverage() {
    log "Running coverage tests..."
    docker-compose exec web coverage run --source='.' manage.py test --settings=idp.test_settings
    docker-compose exec web coverage report
    docker-compose exec web coverage html
    log "Coverage report generated in htmlcov/"
}

# Run linting in container
lint() {
    log "Running code linting..."
    docker-compose exec web black --check .
    docker-compose exec web isort --check-only .
    docker-compose exec web flake8 .
}

# Format code in container
format() {
    log "Formatting code..."
    docker-compose exec web black .
    docker-compose exec web isort .
}

# Shell access to web container
shell() {
    log "Opening shell in web container..."
    docker-compose exec web bash
}

# Django shell in container
django_shell() {
    log "Opening Django shell..."
    docker-compose exec web python manage.py shell
}

# View logs
logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Clean up Docker resources
cleanup() {
    log "Cleaning up Docker resources..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    docker volume prune -f
}

# Clean up Python files
cleanup_python() {
    log "Cleaning up Python cache and profiling files..."
    find . -name "*.pyc" -type f -delete
    find . -name "*.pyo" -type f -delete
    find . -name "*.prof" -type f -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage" -type f -delete
    find . -name "*.log" -type f -delete
    log "Python cleanup completed"
}

# Show status of all services
status() {
    log "Service status:"
    docker-compose ps
}

# Backup database
backup_db() {
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    log "Creating database backup: $backup_file"
    docker-compose exec -T postgres pg_dump -U postgres idp > "$backup_file"
    log "Backup created: $backup_file"
}

# Restore database
restore_db() {
    local backup_file=$1
    if [ -z "$backup_file" ]; then
        error "Please specify backup file to restore"
        exit 1
    fi
    log "Restoring database from: $backup_file"
    docker-compose exec -T postgres psql -U postgres idp < "$backup_file"
    log "Database restored"
}

# Show help
help() {
    echo "Internal Developer Platform - Docker Commands"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  build              Build Docker images"
    echo "  start              Start all services"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  status             Show service status"
    echo ""
    echo "Database:"
    echo "  migrate            Run database migrations"
    echo "  init_db            Initialize database (create if not exists)"
    echo "  backup_db          Backup database"
    echo "  restore_db <file>  Restore database from backup"
    echo ""
    echo "User Management:"
    echo "  createsuperuser    Create Django superuser (interactive)"
    echo "  create_users       Create default users (testuser, superuser, admin)"
    echo "  reset_users        Reset default user passwords"
    echo ""
    echo "Development:"
    echo "  collectstatic      Collect static files"
    echo "  shell              Open bash shell in web container"
    echo "  django_shell       Open Django shell"
    echo "  logs [service]     View logs (all services or specific)"
    echo ""
    echo "Testing:"
    echo "  test               Run all tests"
    echo "  test_app <app>     Run tests for specific app"
    echo "  coverage           Run tests with coverage report"
    echo ""
    echo "Code Quality:"
    echo "  lint               Run code linting"
    echo "  format             Format code"
    echo ""
    echo "Maintenance:"
    echo "  cleanup            Clean up Docker resources"
    echo "  cleanup_python     Clean up Python files"
    echo "  help               Show this help message"
}

# Main command dispatcher
case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    migrate)
        migrate
        ;;
    createsuperuser)
        createsuperuser
        ;;
    collectstatic)
        collectstatic
        ;;
    test)
        test
        ;;
    test_app)
        test_app "$2"
        ;;
    coverage)
        coverage
        ;;
    lint)
        lint
        ;;
    format)
        format
        ;;
    shell)
        shell
        ;;
    django_shell)
        django_shell
        ;;
    logs)
        logs "$2"
        ;;
    cleanup)
        cleanup
        ;;
    cleanup_python)
        cleanup_python
        ;;
    backup_db)
        backup_db
        ;;
    restore_db)
        restore_db "$2"
        ;;
    init_db)
        init_db
        ;;
    create_users)
        create_users
        ;;
    reset_users)
        reset_users
        ;;
    help|--help|-h)
        help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac 
