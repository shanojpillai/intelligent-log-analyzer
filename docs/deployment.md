# Deployment Guide

## Overview

This guide covers deployment options for the Intelligent Log Analyzer system, from local development to production environments. The system is designed to be cloud-native and can be deployed on various platforms.

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for AI model downloads

### Software Dependencies
- Docker 20.10+
- Docker Compose 2.0+
- Git
- (Optional) Kubernetes 1.20+
- (Optional) Helm 3.0+

## Local Development Deployment

### Quick Start
```bash
# Clone repository
git clone https://github.com/shanojpillai/intelligent-log-analyzer.git
cd intelligent-log-analyzer

# Set up environment
cp .env.example .env
# Edit .env with your configurations

# Start all services
docker-compose up -d

# Check service health
docker-compose ps
```

### Environment Configuration
Edit `.env` file with appropriate values:

```bash
# AI Services
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama2

# Database
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# Storage
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# Security
SECRET_KEY=your_super_secret_key
JWT_SECRET=your_jwt_secret
```

### Service Access
- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
- **Weaviate**: http://localhost:8080

## Production Deployment

### Docker Compose Production

#### 1. Production Configuration
Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - BACKEND_URL=https://api.yourdomain.com
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - REDIS_URL=redis://:password@redis:6379
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped

  # ... other services
```

#### 2. SSL Configuration
```bash
# Generate SSL certificates (Let's Encrypt)
certbot certonly --standalone -d yourdomain.com

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/
```

#### 3. Deploy
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Kubernetes Deployment

#### 1. Namespace Setup
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: log-analyzer
```

#### 2. ConfigMap and Secrets
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: log-analyzer-config
  namespace: log-analyzer
data:
  OLLAMA_HOST: "http://ollama:11434"
  WEAVIATE_URL: "http://weaviate:8080"
  REDIS_URL: "redis://redis:6379"

---
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: log-analyzer-secrets
  namespace: log-analyzer
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your_secure_password"
  REDIS_PASSWORD: "your_redis_password"
  SECRET_KEY: "your_super_secret_key"
```

#### 3. Database Deployment
```yaml
# postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: log-analyzer
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: log_analyzer
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: log-analyzer-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

#### 4. Application Deployment
```yaml
# backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: log-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/log-analyzer-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: log-analyzer-config
        - secretRef:
            name: log-analyzer-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### 5. Deploy to Kubernetes
```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgres.yaml
kubectl apply -f backend.yaml

# Check deployment status
kubectl get pods -n log-analyzer
kubectl get services -n log-analyzer
```

### Helm Deployment

#### 1. Install Helm Chart
```bash
# Add repository
helm repo add log-analyzer ./helm-chart

# Install
helm install log-analyzer log-analyzer/log-analyzer \
  --namespace log-analyzer \
  --create-namespace \
  --values values.prod.yaml
```

#### 2. Helm Values Configuration
```yaml
# values.prod.yaml
global:
  domain: yourdomain.com
  
backend:
  replicaCount: 3
  image:
    repository: your-registry/log-analyzer-backend
    tag: "latest"
  
frontend:
  replicaCount: 2
  image:
    repository: your-registry/log-analyzer-frontend
    tag: "latest"

postgres:
  persistence:
    size: 20Gi
    storageClass: fast-ssd

redis:
  persistence:
    size: 5Gi

ingress:
  enabled: true
  tls:
    enabled: true
    secretName: log-analyzer-tls
```

## Cloud Platform Deployments

### AWS ECS Deployment

#### 1. Task Definition
```json
{
  "family": "log-analyzer-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/log-analyzer-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/log-analyzer",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 2. Service Configuration
```bash
# Create ECS service
aws ecs create-service \
  --cluster log-analyzer-cluster \
  --service-name log-analyzer-backend \
  --task-definition log-analyzer-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Run Deployment

#### 1. Build and Push Images
```bash
# Build and tag
docker build -t gcr.io/your-project/log-analyzer-backend ./backend
docker build -t gcr.io/your-project/log-analyzer-frontend ./frontend

# Push to Container Registry
docker push gcr.io/your-project/log-analyzer-backend
docker push gcr.io/your-project/log-analyzer-frontend
```

#### 2. Deploy Services
```bash
# Deploy backend
gcloud run deploy log-analyzer-backend \
  --image gcr.io/your-project/log-analyzer-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://...

# Deploy frontend
gcloud run deploy log-analyzer-frontend \
  --image gcr.io/your-project/log-analyzer-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars BACKEND_URL=https://backend-url
```

### Azure Container Instances

```bash
# Create resource group
az group create --name log-analyzer-rg --location eastus

# Deploy backend
az container create \
  --resource-group log-analyzer-rg \
  --name log-analyzer-backend \
  --image your-registry/log-analyzer-backend:latest \
  --dns-name-label log-analyzer-backend \
  --ports 8000 \
  --environment-variables DATABASE_URL=postgresql://...

# Deploy frontend
az container create \
  --resource-group log-analyzer-rg \
  --name log-analyzer-frontend \
  --image your-registry/log-analyzer-frontend:latest \
  --dns-name-label log-analyzer-frontend \
  --ports 8501 \
  --environment-variables BACKEND_URL=https://backend-url
```

## Monitoring and Observability

### Prometheus Monitoring
```yaml
# prometheus.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'log-analyzer-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'log-analyzer-services'
    static_configs:
      - targets: ['ai-analyzer:8000', 'embedding-engine:8000']
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "Log Analyzer Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration
```yaml
# logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
  file:
    class: logging.FileHandler
    filename: /var/log/app.log
    formatter: default
loggers:
  root:
    level: INFO
    handlers: [console, file]
```

## Security Hardening

### Network Security
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: log-analyzer-network-policy
spec:
  podSelector:
    matchLabels:
      app: log-analyzer
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000
```

### RBAC Configuration
```yaml
# rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: log-analyzer-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: log-analyzer-binding
subjects:
- kind: ServiceAccount
  name: log-analyzer-sa
roleRef:
  kind: Role
  name: log-analyzer-role
  apiGroup: rbac.authorization.k8s.io
```

## Backup and Disaster Recovery

### Database Backup
```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump -h postgres -U postgres log_analyzer > "$BACKUP_DIR/postgres_$TIMESTAMP.sql"

# Upload to S3
aws s3 cp "$BACKUP_DIR/postgres_$TIMESTAMP.sql" s3://your-backup-bucket/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "postgres_*.sql" -mtime +7 -delete
```

### Disaster Recovery Plan
1. **Data Recovery**: Restore from latest database backup
2. **Service Recovery**: Redeploy from container images
3. **Configuration Recovery**: Restore from version control
4. **Monitoring**: Verify all services are healthy

## Performance Optimization

### Resource Allocation
```yaml
# Resource limits for production
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Scaling Configuration
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Common Issues

#### Service Discovery Problems
```bash
# Check DNS resolution
kubectl exec -it pod-name -- nslookup service-name

# Check service endpoints
kubectl get endpoints -n log-analyzer
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl exec -it backend-pod -- psql -h postgres -U postgres -d log_analyzer

# Check database logs
kubectl logs postgres-pod -n log-analyzer
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n log-analyzer

# Monitor application metrics
curl http://backend-service:8000/metrics
```

### Health Checks
```yaml
# Kubernetes health checks
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Maintenance

### Update Procedures
1. **Rolling Updates**: Use Kubernetes rolling updates for zero-downtime deployments
2. **Database Migrations**: Run migrations before deploying new application versions
3. **Configuration Updates**: Update ConfigMaps and restart affected pods
4. **Security Updates**: Regularly update base images and dependencies

### Monitoring Checklist
- [ ] All services are running and healthy
- [ ] Database connections are stable
- [ ] API response times are within acceptable limits
- [ ] Error rates are below threshold
- [ ] Storage usage is within limits
- [ ] Backup processes are running successfully
