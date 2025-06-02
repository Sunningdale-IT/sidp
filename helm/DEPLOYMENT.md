# IDP Kubernetes Deployment Guide

This guide provides step-by-step instructions for deploying the Internal Developer Platform (IDP) to a Kubernetes cluster using Helm.

## Prerequisites

### Required Tools
- **Kubernetes cluster** (1.19+)
- **Helm** (3.2.0+)
- **kubectl** configured to access your cluster
- **Docker** (for building custom images)

### Cluster Requirements
- **CPU**: Minimum 4 cores (8+ recommended for production)
- **Memory**: Minimum 8GB RAM (16GB+ recommended for production)
- **Storage**: Persistent volume support
- **Ingress Controller**: NGINX Ingress Controller (recommended)
- **Cert Manager**: For TLS certificates (optional but recommended)

## Quick Start

### 1. Clone and Prepare

```bash
# Clone the repository
git clone <repository-url>
cd sidp/helm

# Make deployment script executable
chmod +x deploy.sh
```

### 2. Deploy with Default Settings

```bash
# Deploy to default namespace 'idp'
./deploy.sh

# Or use Helm directly
helm install idp ./idp-chart --namespace idp --create-namespace
```

### 3. Access the Application

```bash
# Port forward to access locally
kubectl port-forward service/idp-web 8000:8000 -n idp

# Visit http://localhost:8000
# Login with admin/admin
```

## Production Deployment

### 1. Prepare Your Environment

#### Build and Push Docker Image

```bash
# Build the application image
docker build -t your-registry.com/idp/app:v1.0.0 .

# Push to your registry
docker push your-registry.com/idp/app:v1.0.0
```

#### Create Production Values File

```bash
cp idp-chart/values-production.yaml my-production-values.yaml
```

Edit `my-production-values.yaml`:

```yaml
# Update image settings
image:
  registry: your-registry.com
  repository: idp/app
  tag: "v1.0.0"

# Update domain settings
env:
  ALLOWED_HOSTS: "idp.yourcompany.com"
  CORS_ALLOWED_ORIGINS: "https://idp.yourcompany.com"

ingress:
  hosts:
    - host: idp.yourcompany.com
      paths:
        - path: /
          pathType: Prefix
          service: web

# Update secrets (use external secret management in production)
secrets:
  secretKey: "your-secure-django-secret-key"
  dbPassword: "your-secure-database-password"
```

### 2. Deploy to Production

```bash
# Deploy with production values
./deploy.sh -f my-production-values.yaml -n production

# Or use Helm directly
helm install idp ./idp-chart \
  --namespace production \
  --create-namespace \
  -f my-production-values.yaml
```

### 3. Verify Deployment

```bash
# Check all resources
kubectl get all -n production

# Check pod status
kubectl get pods -n production -w

# Check logs
kubectl logs -f deployment/idp-web -n production
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `idp.yourcompany.com` |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | `https://idp.yourcompany.com` |
| `PROMETHEUS_METRICS_ENABLED` | Enable metrics | `True` |

### Resource Configuration

```yaml
resources:
  web:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 2Gi
  celery:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 2Gi
```

### Autoscaling Configuration

```yaml
autoscaling:
  enabled: true
  web:
    minReplicas: 3
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70
  celery:
    minReplicas: 3
    maxReplicas: 50
    targetCPUUtilizationPercentage: 70
```

### Database Configuration

#### Using Built-in PostgreSQL

```yaml
postgresql:
  enabled: true
  auth:
    database: "idp"
    username: "postgres"
    password: "secure-password"
  primary:
    persistence:
      size: 100Gi
```

#### Using External PostgreSQL

```yaml
postgresql:
  enabled: false

externalPostgresql:
  host: "postgres.example.com"
  port: 5432
  username: "idp_user"
  password: "secure-password"
  database: "idp"
```

### Redis Configuration

#### Using Built-in Redis

```yaml
redis:
  enabled: true
  master:
    persistence:
      size: 20Gi
```

#### Using External Redis

```yaml
redis:
  enabled: false

externalRedis:
  host: "redis.example.com"
  port: 6379
```

## Security Configuration

### Secrets Management

For production, use external secret management:

```yaml
# Example with AWS Secrets Manager
secrets:
  secretKey: "arn:aws:secretsmanager:region:account:secret:idp-secret-key"
  dbPassword: "arn:aws:secretsmanager:region:account:secret:idp-db-password"
```

### Network Policies

```yaml
networkPolicy:
  enabled: true
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: ingress-nginx
      ports:
      - protocol: TCP
        port: 8000
```

### Pod Security

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000

podSecurityContext:
  seccompProfile:
    type: RuntimeDefault
```

## Monitoring and Observability

### Enable Prometheus Monitoring

```yaml
podMonitor:
  enabled: true
  namespace: monitoring
  interval: 30s
  path: /metrics
```

### Health Checks

The chart includes comprehensive health checks:

```yaml
healthChecks:
  enabled: true
  web:
    livenessProbe:
      httpGet:
        path: /health/
        port: 8000
      initialDelaySeconds: 60
      periodSeconds: 30
    readinessProbe:
      httpGet:
        path: /health/
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
```

## Backup and Recovery

### Database Backup

```bash
# Create a backup
kubectl exec -it idp-postgresql-0 -n production -- \
  pg_dump -U postgres idp > backup-$(date +%Y%m%d).sql

# Store in persistent volume or external storage
```

### Application Data Backup

```bash
# Backup static files
kubectl cp production/idp-web-xxx:/app/staticfiles ./staticfiles-backup

# Backup configuration
kubectl get configmap idp-config -n production -o yaml > config-backup.yaml
```

## Troubleshooting

### Common Issues

#### 1. Pod Startup Issues

```bash
# Check pod status
kubectl get pods -n production

# Check pod events
kubectl describe pod idp-web-xxx -n production

# Check logs
kubectl logs idp-web-xxx -n production
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
kubectl exec -it deployment/idp-web -n production -- \
  python manage.py dbshell

# Check database pod
kubectl logs idp-postgresql-0 -n production
```

#### 3. Celery Worker Issues

```bash
# Check Celery worker status
kubectl exec -it deployment/idp-celery -n production -- \
  celery -A idp inspect ping

# Check Celery logs
kubectl logs deployment/idp-celery -n production
```

#### 4. Ingress Issues

```bash
# Check ingress status
kubectl get ingress -n production
kubectl describe ingress idp-ingress -n production

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Debug Commands

```bash
# Get all resources
kubectl get all -n production -l app.kubernetes.io/name=idp

# Check resource usage
kubectl top pods -n production
kubectl top nodes

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Shell into pod
kubectl exec -it deployment/idp-web -n production -- /bin/bash
```

## Upgrading

### Upgrade Process

```bash
# Update chart dependencies
cd idp-chart
helm dependency update
cd ..

# Upgrade with new values
./deploy.sh -u -f my-production-values.yaml -n production

# Or use Helm directly
helm upgrade idp ./idp-chart \
  --namespace production \
  -f my-production-values.yaml
```

### Rolling Back

```bash
# Check release history
helm history idp -n production

# Rollback to previous version
helm rollback idp 1 -n production
```

## Scaling

### Manual Scaling

```bash
# Scale web pods
kubectl scale deployment idp-web --replicas=5 -n production

# Scale Celery workers
kubectl scale deployment idp-celery --replicas=10 -n production
```

### Automatic Scaling

Horizontal Pod Autoscaler (HPA) is enabled by default:

```yaml
autoscaling:
  enabled: true
  web:
    minReplicas: 3
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70
```

## Maintenance

### Regular Tasks

```bash
# Check cluster health
kubectl get nodes
kubectl get pods --all-namespaces

# Update dependencies
helm repo update
helm dependency update

# Check for security updates
kubectl get pods -n production -o jsonpath='{.items[*].spec.containers[*].image}'
```

### Cleanup

```bash
# Remove old releases
helm list -n production
helm uninstall old-release -n production

# Clean up unused resources
kubectl delete pods --field-selector=status.phase=Succeeded -n production
```

## Support

### Getting Help

1. **Check logs**: Always start with application and pod logs
2. **Check events**: Kubernetes events provide valuable debugging information
3. **Check resources**: Ensure adequate CPU, memory, and storage
4. **Check network**: Verify ingress, services, and network policies

### Useful Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Cert Manager](https://cert-manager.io/docs/)

## Best Practices

1. **Use external secret management** in production
2. **Enable monitoring and alerting**
3. **Implement proper backup strategies**
4. **Use resource limits and requests**
5. **Enable network policies for security**
6. **Regular security updates**
7. **Test deployments in staging first**
8. **Use GitOps for deployment automation** 
