#!/bin/bash

# Internal Developer Platform - Startup Script
echo "🚀 Starting Internal Developer Platform..."

# Detect operating system
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    MACHINE=macOS;;
    Linux*)     MACHINE=Linux;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "🖥️  Detected OS: ${MACHINE}"

# macOS-specific optimizations and checks
if [[ "$MACHINE" == "macOS" ]]; then
    echo "🍎 Applying macOS optimizations..."
    
    # Check Docker Desktop settings
    echo "📋 macOS Docker Desktop Recommendations:"
    echo "   • Memory: 4GB+ (8GB recommended)"
    echo "   • CPUs: 4+ cores recommended"
    echo "   • Disk: 60GB+ available space"
    echo "   • File sharing: Enable for project directory"
    echo ""
    
    # Check if Docker Desktop is using the right virtualization
    if docker info 2>/dev/null | grep -q "Operating System.*Docker Desktop"; then
        echo "✅ Docker Desktop detected"
    else
        echo "⚠️  Docker Desktop recommended for macOS"
    fi
    
    # Check available memory
    MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    echo "💾 Available system memory: ${MEMORY_GB}GB"
    if [[ $MEMORY_GB -lt 8 ]]; then
        echo "⚠️  Warning: Less than 8GB RAM detected. Consider closing other applications."
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    if [[ "$MACHINE" == "macOS" ]]; then
        echo "   On macOS: Start Docker Desktop from Applications"
    fi
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose and try again."
    if [[ "$MACHINE" == "macOS" ]]; then
        echo "   On macOS: brew install docker-compose"
    fi
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please review and update the configuration if needed."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p docker/postgres docker/nginx

# macOS-specific Docker optimizations
if [[ "$MACHINE" == "macOS" ]]; then
    echo "🔧 Applying macOS Docker optimizations..."
    
    # Set Docker buildkit for better performance
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    
    # Clean up any existing containers to free memory
    echo "🧹 Cleaning up existing containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
fi

# Build images first
echo "🔨 Building Docker images..."
docker-compose build --parallel

# Start the services in stages
echo "🐳 Starting core services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for core services to be ready
echo "⏳ Waiting for core services to be ready..."
sleep 10

# Check if PostgreSQL is ready
echo "🗄️  Waiting for PostgreSQL to be ready..."
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "   PostgreSQL is starting up..."
    sleep 3
done
echo "✅ PostgreSQL is ready!"

# Check if Redis is ready
echo "🔴 Waiting for Redis to be ready..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo "   Redis is starting up..."
    sleep 2
done
echo "✅ Redis is ready!"

# Start the main application services
echo "🌐 Starting Django application services..."
docker-compose up -d web celery celery-beat flower

# Wait for Django to be ready
echo "⏳ Waiting for Django to be ready..."
DJANGO_ATTEMPTS=0
DJANGO_MAX_ATTEMPTS=30
while [ $DJANGO_ATTEMPTS -lt $DJANGO_MAX_ATTEMPTS ]; do
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        echo "✅ Django is ready!"
        break
    fi
    echo "   Django is starting up... (attempt $((DJANGO_ATTEMPTS + 1))/$DJANGO_MAX_ATTEMPTS)"
    sleep 3
    DJANGO_ATTEMPTS=$((DJANGO_ATTEMPTS + 1))
done

if [ $DJANGO_ATTEMPTS -eq $DJANGO_MAX_ATTEMPTS ]; then
    echo "❌ Django failed to start. Check logs with: docker-compose logs web"
    exit 1
fi

# Create default users
echo "👥 Creating default users..."
if docker-compose exec -T web python manage.py create_default_users > /dev/null 2>&1; then
    echo "✅ Default users created successfully!"
else
    echo "⚠️  Warning: Could not create default users. You may need to create them manually."
fi

echo ""
echo "🎉 Internal Developer Platform is running!"
echo ""
echo "📍 Access Points:"
echo "   Dashboard: http://localhost:8000"
echo "   Admin: http://localhost:8000/admin"
echo "   API Docs: http://localhost:8000/api/schema/swagger-ui/"
echo "   Celery Monitor: http://localhost:5555"
echo ""
echo "👤 Default Users:"
echo "   • testuser/testuser123 (regular user)"
echo "   • superuser/superuser123 (superuser)"
echo "   • admin/admin (superuser - legacy)"
echo ""
echo "🔧 Management:"
echo "   Create custom user: docker-compose exec web python manage.py createsuperuser"
echo "   Reset user passwords: docker-compose exec web python manage.py create_default_users --force"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"

if [[ "$MACHINE" == "macOS" ]]; then
    echo "🍎 macOS-specific tips:"
    echo "   • All operations run in containers - no macOS dependencies"
    echo "   • Use './scripts/docker-commands.sh help' for all available commands"
    echo "   • If performance is slow, increase Docker Desktop memory"
    echo "   • Use 'docker system prune' periodically to free up space"
    echo ""
fi

echo "📖 For more information, see README.md"
echo "🛠️  For containerized commands, use: ./scripts/docker-commands.sh help" 
