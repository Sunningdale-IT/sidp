# Internal Developer Platform (IDP)

A comprehensive Django-based Internal Developer Platform designed for modern development teams. This platform provides self-service capabilities, automated operations, and streamlined workflows for enterprise software development.

## 🚀 Features

### Core Platform Features
- **Dynamic Panels**: Configurable UI panels with various input types (radio, boolean, dropdown, text, textarea)
- **Operation Templates**: Automated CLI operations (kubectl, Azure CLI, git, docker, terraform, helm)
- **Secret Management**: Secure secrets storage and management
- **Async Task Processing**: Celery-based background job processing with monitoring
- **REST API**: Comprehensive API with session-based authentication
- **Real-time Monitoring**: Health checks, metrics, and observability

### Developer Self-Service Features
- **Service Catalog**: Track and manage internal services and APIs
- **Automated Workflows**: Pre-configured templates for common development tasks
- **Multi-Cloud Support**: AWS, Azure, GCP integration capabilities
- **Infrastructure as Code**: Terraform and Helm integration
- **Monitoring & Observability**: Prometheus metrics, structured logging
- **Security & Compliance**: Rate limiting, CSP headers, audit trails

### Modern UI/UX
- **Vintage Modern Design**: Clean aesthetic with Space Grotesk typography
- **Responsive Design**: Mobile-friendly interface optimized for all devices
- **Interactive Dashboard**: Real-time statistics and activity monitoring
- **Accessibility**: WCAG compliant design principles

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Django API    │    │   Background    │
│   (Templates)   │◄──►│   (REST/Auth)   │◄──►│   Jobs (Celery) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │   PostgreSQL    │    │     Redis       │
│ (Authentication)│    │   (Database)    │    │  (Cache/Queue)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15 with automated initialization
- **Cache/Queue**: Redis 7 for caching and task queuing
- **Authentication**: Django session-based authentication
- **Task Queue**: Celery with Redis broker and Flower monitoring
- **Containerization**: Docker & Docker Compose with optimizations
- **Monitoring**: Prometheus metrics, health checks, structured logging
- **Security**: CORS, CSP headers, rate limiting, secure secrets management

## 🍎 macOS Setup (Optimized)

### Prerequisites for macOS
- **Docker Desktop for Mac** (4.0+) - [Download here](https://www.docker.com/products/docker-desktop)
- **Homebrew** - [Install here](https://brew.sh/)
- **Git** - `brew install git`

### Docker Desktop Configuration for macOS
1. **Memory**: Allocate at least 4GB (8GB recommended)
2. **CPUs**: Allocate 4+ cores for optimal performance
3. **Disk**: Ensure 60GB+ available space
4. **File Sharing**: Enable for your project directory
5. **Features**: Enable "Use Docker Compose V2"

### macOS-Optimized Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd sidp

# Make scripts executable
chmod +x scripts/*.sh

# Run the macOS-optimized startup script
./scripts/start.sh
```

The startup script automatically:
- Detects macOS and applies performance optimizations
- Checks Docker Desktop configuration and provides recommendations
- Initializes databases automatically
- Starts services sequentially for stability
- Provides helpful access information

## 🚀 Quick Start with Docker Commands

### All-in-One Commands
```bash
# Start the entire platform
./scripts/docker-commands.sh start

# Create a superuser account
./scripts/docker-commands.sh createsuperuser

# Run tests
./scripts/docker-commands.sh test

# View logs
./scripts/docker-commands.sh logs

# Stop everything
./scripts/docker-commands.sh stop
```

### Available Commands
```bash
./scripts/docker-commands.sh help
```

## 🎯 Getting Started Guide

### 1. Initial Setup
```bash
# Clone and start the platform
git clone <repository-url>
cd sidp
./scripts/docker-commands.sh start
```

### 2. Create Your First User
```bash
# Create a superuser account
./scripts/docker-commands.sh createsuperuser
# Follow the prompts to create your admin account
```

**Default Users Available:**
The system automatically creates these default users for testing and development:
- **testuser** / **testuser123** (regular user)
- **superuser** / **superuser123** (superuser with admin access)
- **admin** / **admin** (legacy superuser)

You can reset these passwords anytime with:
```bash
./scripts/docker-commands.sh reset_users
```

### 3. Access the Platform
| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:8000 | Main IDP interface |
| **Admin Panel** | http://localhost:8000/admin | Django administration |
| **API Docs** | http://localhost:8000/api/schema/swagger-ui/ | Interactive API documentation |
| **Task Monitor** | http://localhost:5555 | Celery task monitoring |
| **Health Check** | http://localhost:8000/health/ | System health status |

### 4. Create Your First Panel
1. Go to http://localhost:8000/admin
2. Navigate to **Panels > Panels**
3. Click **Add Panel**
4. Fill in the details:
   - **Title**: "Deploy Application"
   - **Description**: "Deploy applications to different environments"
   - **Order**: 1
   - **Is Active**: ✓

### 5. Add Panel Fields
1. In the panel admin, scroll to **Panel Fields**
2. Add fields like:
   - **Environment** (dropdown): production, staging, development
   - **Application Name** (text): Name of the application
   - **Version** (text): Version to deploy
   - **Notify Team** (boolean): Send notifications

### 6. Create Operation Templates
1. Navigate to **Operations > Operation Templates**
2. Create templates for common tasks:
   - **Kubernetes Deployment**
   - **Database Migration**
   - **Environment Setup**

## 📊 Platform Usage

### Dashboard Overview
The dashboard provides:
- **Statistics**: Active panels, services, environments, deployments
- **Quick Actions**: Create panels, operations, view docs, monitor tasks
- **Panel Grid**: Visual representation of available self-service panels
- **Recent Activity**: Real-time activity feed

### Panel System
Panels are the core of the self-service experience:
- **Dynamic Fields**: Support for various input types
- **Validation**: Built-in validation and custom regex patterns
- **Data Sources**: Integration with external APIs for dynamic options
- **Submissions**: Track user submissions and their status

### Operation Templates
Automate common development tasks:
- **Command Templates**: Use `{{variable}}` placeholders
- **Security Validation**: Commands are validated before execution
- **Approval Workflows**: Optional approval process for sensitive operations
- **Logging**: Comprehensive logging of all operations
- **Retry Logic**: Automatic retry for failed operations

### API Integration
```bash
# Get all panels (requires authentication)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/panels/panels/

# Submit panel data
curl -X POST -H "Content-Type: application/json" \
  -d '{"environment": "staging", "app_name": "my-app"}' \
  http://localhost:8000/api/panels/submissions/

# Check operation status
curl http://localhost:8000/api/operations/executions/
```

## 🔧 Development and Customization

### Adding Custom Data Sources
1. Create a new `DynamicDataSource` in the admin
2. Configure the source type (Docker Registry, Kubernetes API, Git, Custom API)
3. Set authentication if required
4. Use in panel fields for dynamic options

### Creating Custom Operations
1. Define operation templates with command patterns
2. Use parameter substitution: `kubectl apply -f {{manifest_file}}`
3. Add pre/post execution scripts if needed
4. Configure timeout and retry settings

### Extending the API
The platform uses Django REST Framework:
- Add new viewsets in `views.py`
- Register URLs in `urls.py`
- Use serializers for data validation
- Implement custom permissions as needed

## 🔐 Security Features

### Authentication & Authorization
- **Django Admin**: Built-in user management
- **Session-based Auth**: Secure session handling
- **API Authentication**: Session and basic authentication
- **Permission System**: Django's built-in permissions

### Security Headers
- **CSP**: Content Security Policy
- **HSTS**: HTTP Strict Transport Security
- **XSS Protection**: Cross-site scripting prevention
- **Rate Limiting**: API endpoint protection

### Command Security
- **Command Validation**: Dangerous commands are blocked
- **Sandboxed Execution**: Operations run in controlled environments
- **Audit Logging**: All operations are logged
- **Secret Management**: Secure handling of sensitive data

## 🧪 Testing

### Run Tests
```bash
# All tests
./scripts/docker-commands.sh test

# Specific app tests
./scripts/docker-commands.sh test_app core
./scripts/docker-commands.sh test_app panels
./scripts/docker-commands.sh test_app operations

# With coverage
./scripts/docker-commands.sh coverage
```

### Manual Testing
1. **Dashboard Access**: Verify dashboard loads and displays correctly
2. **Panel Creation**: Create panels with different field types
3. **Operation Execution**: Test operation templates with various parameters
4. **API Endpoints**: Test API endpoints with different authentication methods
5. **Error Handling**: Verify error messages and logging

## 📦 Deployment

### Production Considerations
```bash
# Use production settings
export DJANGO_SETTINGS_MODULE=idp.production_settings

# Collect static files
./scripts/docker-commands.sh collectstatic

# Run migrations
./scripts/docker-commands.sh migrate

# Create production superuser
./scripts/docker-commands.sh createsuperuser
```

### Environment Variables
Key configuration options in `.env`:
```bash
# Database
DB_NAME=idp
DB_USER=postgres
DB_PASSWORD=secure_password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Security
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Key API Endpoints
```
# Panels
GET    /api/panels/panels/              # List all panels
POST   /api/panels/panels/              # Create panel
GET    /api/panels/panels/{id}/         # Get panel details
POST   /api/panels/submissions/         # Submit panel data
GET    /api/panels/submissions/         # List submissions

# Operations
GET    /api/operations/templates/       # List operation templates
POST   /api/operations/templates/       # Create operation template
GET    /api/operations/executions/      # List executions
POST   /api/operations/executions/      # Execute operation
GET    /api/operations/logs/            # View operation logs

# Data Sources
GET    /api/panels/data-sources/        # List dynamic data sources
POST   /api/panels/data-sources/        # Create data source
```

## 🛠️ Maintenance

### Regular Maintenance Tasks
```bash
# Clean up Python cache files
./scripts/docker-commands.sh cleanup_python

# Clean up Docker resources
./scripts/docker-commands.sh cleanup

# Backup database
./scripts/docker-commands.sh backup_db

# View system status
./scripts/docker-commands.sh status
```

### Monitoring
- **Health Checks**: Automated health monitoring
- **Celery Tasks**: Monitor background job processing
- **Database Performance**: Track query performance
- **Resource Usage**: Monitor container resource consumption

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database status
   ./scripts/docker-commands.sh logs postgres
   
   # Reinitialize database
   ./scripts/docker-commands.sh init_db
   ```

2. **Celery Task Issues**
   ```bash
   # Check Celery worker status
   ./scripts/docker-commands.sh logs celery
   
   # Restart Celery workers
   docker-compose restart celery celery-beat
   ```

3. **Permission Issues**
   ```bash
   # Check user permissions
   ./scripts/docker-commands.sh django_shell
   # In shell: User.objects.all()
   ```

### macOS-Specific Issues

1. **Slow Performance**
   - Increase Docker Desktop memory allocation
   - Use the provided performance optimizations
   - Close unnecessary applications

2. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :8000
   lsof -i :5432
   lsof -i :6379
   ```

## 🔮 Roadmap

### Planned Features
- [ ] **Enhanced UI**: React/Vue.js frontend
- [ ] **Service Mesh**: Istio/Linkerd integration
- [ ] **GitOps**: ArgoCD/Flux workflows
- [ ] **Policy Engine**: Open Policy Agent integration
- [ ] **Cost Management**: Cloud cost tracking
- [ ] **AI Integration**: Intelligent recommendations
- [ ] **Multi-tenancy**: Organization support
- [ ] **Plugin System**: Extensible architecture

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for developer productivity and platform engineering**
