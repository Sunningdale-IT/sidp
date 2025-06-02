# Internal Developer Platform (IDP) Helm Chart

This Helm chart deploys the Internal Developer Platform to a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for persistent volumes)

## Installing the Chart

### Add Dependencies

First, add the required Helm repositories:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install Dependencies

```bash
cd helm/idp-chart
helm dependency update
```

### Install the Chart

To install the chart with the release name `idp`:

```bash
# Install with default values
helm install idp ./helm/idp-chart

# Install with custom values
helm install idp ./helm/idp-chart -f values-production.yaml

# Install in a specific namespace
helm install idp ./helm/idp-chart --namespace idp --create-namespace
```

## Uninstalling the Chart

To uninstall/delete the `idp` deployment:

```bash
helm uninstall idp
```

## Configuration

The following table lists the configurable parameters and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.imageRegistry` | Global Docker image registry | `""` |
| `global.imagePullSecrets` | Global Docker registry secret names | `[]` |
| `global.storageClass` | Global StorageClass for Persistent Volume(s) | `""` |

### Application Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.registry` | IDP image registry | `docker.io` |
| `image.repository` | IDP image repository | `your-org/idp` |
| `image.tag` | IDP image tag | `1.0.0` |
| `image.pullPolicy` | IDP image pull policy | `IfNotPresent` |

### Replica Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount.web` | Number of web replicas | `2` |
| `replicaCount.celery` | Number of Celery worker replicas | `2` |
| `replicaCount.celeryBeat` | Number of Celery Beat replicas | `1` |
| `replicaCount.flower` | Number of Flower replicas | `1` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.web.port` | Web service port | `8000` |
| `service.flower.port` | Flower service port | `5555` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress controller resource | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts[0].host` | Hostname for the IDP service | `idp.yourcompany.com` |
| `ingress.tls` | TLS configuration | `[]` |

### Database Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Deploy PostgreSQL container | `true` |
| `postgresql.auth.database` | PostgreSQL database name | `idp` |
| `postgresql.auth.username` | PostgreSQL username | `postgres` |
| `postgresql.auth.password` | PostgreSQL password | `secure-postgres-password` |

### Redis Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Deploy Redis container | `true` |
| `redis.auth.enabled` | Enable Redis authentication | `false` |

### Security Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.secretKey` | Django secret key | `change-me-in-production` |
| `secrets.dbPassword` | Database password | `secure-postgres-password` |

### Resource Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.web.requests.cpu` | Web CPU request | `500m` |
| `resources.web.requests.memory` | Web memory request | `512Mi` |
| `resources.web.limits.cpu` | Web CPU limit | `1000m` |
| `resources.web.limits.memory` | Web memory limit | `1Gi` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable horizontal pod autoscaler | `true` |
| `autoscaling.web.minReplicas` | Minimum number of web replicas | `2` |
| `autoscaling.web.maxReplicas` | Maximum number of web replicas | `10` |
| `autoscaling.web.targetCPUUtilizationPercentage` | Target CPU utilization | `70` |

## Production Deployment

### 1. Create Production Values File

Create a `values-production.yaml` file:

```yaml
# Production configuration
env:
  DEBUG: "False"
  ALLOWED_HOSTS: "idp.yourcompany.com"
  CORS_ALLOWED_ORIGINS: "https://idp.yourcompany.com"

# Use your container registry
image:
  registry: your-registry.com
  repository: idp/app
  tag: "v1.0.0"

# Configure ingress for your domain
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: idp.yourcompany.com
      paths:
        - path: /
          pathType: Prefix
          service: web
  tls:
    - secretName: idp-tls
      hosts:
        - idp.yourcompany.com

# Production secrets (use external secret management)
secrets:
  secretKey: "your-secure-django-secret-key"
  dbPassword: "your-secure-database-password"

# Production database configuration
postgresql:
  auth:
    password: "your-secure-database-password"
  primary:
    persistence:
      size: 100Gi
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi
      limits:
        cpu: 2000m
        memory: 4Gi

# Production Redis configuration
redis:
  master:
    persistence:
      size: 20Gi
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1000m
        memory: 2Gi

# Production resource limits
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

# Enable autoscaling
autoscaling:
  enabled: true
  web:
    minReplicas: 3
    maxReplicas: 20
  celery:
    minReplicas: 3
    maxReplicas: 50
```

### 2. Deploy to Production

```bash
helm install idp ./helm/idp-chart \
  --namespace idp \
  --create-namespace \
  -f values-production.yaml
```

## Monitoring and Observability

### Enable Prometheus Monitoring

```yaml
podMonitor:
  enabled: true
  namespace: monitoring
  interval: 30s
```

### Health Checks

The chart includes comprehensive health checks:

- **Web**: HTTP health check on `/health/`
- **Celery**: Command-based health check using `celery inspect ping`

## Backup and Recovery

### Database Backup

```bash
# Create a backup job
kubectl create job --from=cronjob/backup-job backup-manual-$(date +%Y%m%d-%H%M%S)
```

### Restore from Backup

```bash
# Scale down the application
kubectl scale deployment idp-web --replicas=0
kubectl scale deployment idp-celery --replicas=0

# Restore database
kubectl exec -it idp-postgresql-0 -- pg_restore -U postgres -d idp /backup/backup.sql

# Scale up the application
kubectl scale deployment idp-web --replicas=2
kubectl scale deployment idp-celery --replicas=2
```

## Troubleshooting

### Common Issues

1. **Pod Startup Issues**
   ```bash
   kubectl logs -f deployment/idp-web
   kubectl describe pod <pod-name>
   ```

2. **Database Connection Issues**
   ```bash
   kubectl exec -it deployment/idp-web -- python manage.py dbshell
   ```

3. **Celery Worker Issues**
   ```bash
   kubectl logs -f deployment/idp-celery
   kubectl exec -it deployment/idp-celery -- celery -A idp inspect ping
   ```

### Debugging Commands

```bash
# Check all resources
kubectl get all -l app.kubernetes.io/name=idp

# Check configuration
kubectl get configmap idp-config -o yaml
kubectl get secret idp-secret -o yaml

# Check ingress
kubectl get ingress
kubectl describe ingress idp-ingress

# Check persistent volumes
kubectl get pv,pvc
```

## Security Considerations

1. **Secrets Management**: Use external secret management systems like:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager

2. **Network Policies**: Enable network policies to restrict pod-to-pod communication

3. **Pod Security**: The chart includes security contexts and runs as non-root user

4. **RBAC**: Minimal RBAC permissions are configured

## Upgrading

### Upgrade the Chart

```bash
# Update dependencies
helm dependency update

# Upgrade the release
helm upgrade idp ./helm/idp-chart -f values-production.yaml

# Check upgrade status
helm status idp
```

### Rolling Back

```bash
# List releases
helm history idp

# Rollback to previous version
helm rollback idp 1
```

## Contributing

1. Make changes to the chart
2. Update the version in `Chart.yaml`
3. Test the changes
4. Submit a pull request

## License

This chart is licensed under the MIT License. 
