# Deployment Guide

This guide covers deploying the Fire and Smoke Detection system to production environments.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Prerequisites

- Python 3.11+
- Virtual environment
- All dependencies installed

### Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/fire-smoke-detection-yolov8.git
   cd fire-smoke-detection-yolov8
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Application**
   ```bash
   # Edit configs/config.yaml with your settings
   ```

3. **Run Locally**

   **FastAPI Backend:**
   ```bash
   uvicorn app.api:app --host 0.0.0.0 --port 8000
   ```

   **Streamlit Dashboard:**
   ```bash
   streamlit run app/streamlit_app.py --server.port 8501
   ```

4. **Access Application**
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501
   - API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Build Docker Image

```bash
# Build image
docker build -t fire-smoke-detection:latest .

# Tag for registry
docker tag fire-smoke-detection:latest your-registry/fire-smoke-detection:latest
```

### Single Container Deployment

**FastAPI Only:**
```bash
docker run -d \
  --name fire-smoke-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  -e PYTHONUNBUFFERED=1 \
  fire-smoke-detection:latest
```

**Streamlit Only:**
```bash
docker run -d \
  --name fire-smoke-dashboard \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  -e PYTHONUNBUFFERED=1 \
  fire-smoke-detection:latest \
  streamlit run app/streamlit_app.py --server.port 8501
```

### Docker Compose Deployment

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Scale services
docker compose up -d --scale api=3

# Stop services
docker compose down
```

### Docker Configuration

**Environment Variables:**
```bash
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false
MODEL_PATH=/app/outputs/fire_smoke_detection/weights/best.pt
DATA_PATH=/app/data
```

**Volume Mapping:**
```yaml
volumes:
  - ./data:/app/data          # Dataset
  - ./outputs:/app/outputs    # Model outputs
  - ./configs:/app/configs    # Configuration
  - ./logs:/app/logs          # Application logs
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 Instance

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium or higher (for GPU: g4dn.xlarge)
   - Security Group: Allow ports 80, 443, 8000, 8501

2. **Connect and Setup**
   ```bash
   ssh -i key.pem ubuntu@instance-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3.11 python3.11-venv python3-pip docker.io git -y
   
   # Clone repository
   git clone https://github.com/yourusername/fire-smoke-detection-yolov8.git
   cd fire-smoke-detection-yolov8
   
   # Setup and run
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run with Systemd**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/fire-smoke-api.service
   
   [Unit]
   Description=Fire and Smoke Detection API
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/fire-smoke-detection-yolov8
   Environment="PATH=/home/ubuntu/fire-smoke-detection-yolov8/venv/bin"
   ExecStart=/home/ubuntu/fire-smoke-detection-yolov8/venv/bin/uvicorn app.api:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start service
   sudo systemctl enable fire-smoke-api
   sudo systemctl start fire-smoke-api
   sudo systemctl status fire-smoke-api
   ```

#### Option 2: ECS (Elastic Container Service)

1. **Push to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
   
   docker tag fire-smoke-detection:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/fire-smoke-detection:latest
   docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/fire-smoke-detection:latest
   ```

2. **Create ECS Cluster and Task Definition**
   - Create ECS cluster
   - Define task with image from ECR
   - Configure memory, CPU, ports
   - Set environment variables

### Google Cloud Deployment

#### Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/fire-smoke-detection

# Deploy to Cloud Run
gcloud run deploy fire-smoke-detection \
  --image gcr.io/PROJECT_ID/fire-smoke-detection:latest \
  --platform managed \
  --region us-central1 \
  --memory 2G \
  --timeout 60s \
  --set-env-vars MODEL_PATH=/tmp/model.pt
```

#### Compute Engine

Similar to AWS EC2, use gcloud compute instances to create VM and deploy.

### Azure Deployment

#### App Service

```bash
# Create resource group
az group create --name fire-smoke-rg --location eastus

# Create App Service Plan
az appservice plan create --name fire-smoke-plan --resource-group fire-smoke-rg --sku B2

# Create Web App
az webapp create --resource-group fire-smoke-rg --plan fire-smoke-plan --name fire-smoke-app

# Configure deployment from GitHub
az webapp deployment github-token --token <token>
```

---

## Production Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Model Configuration
MODEL_PATH=/app/models/best.pt
DEVICE=0  # GPU device, or "cpu"

# Data Paths
DATA_PATH=/data
OUTPUT_PATH=/outputs
LOG_PATH=/logs

# Security
ALLOWED_ORIGINS=https://yourdomain.com
SECRET_KEY=your-secret-key
CORS_ENABLED=true

# Performance
MAX_UPLOAD_SIZE=100  # MB
CACHE_PREDICTIONS=true
BATCH_SIZE=16
```

### Logging Configuration

```yaml
logging:
  level: INFO
  file: /var/log/fire-smoke/app.log
  max_bytes: 104857600  # 100MB
  backup_count: 10
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Security Checklist

- [ ] Update default passwords and secrets
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Enable authentication
- [ ] Set up log aggregation
- [ ] Configure backups
- [ ] Enable monitoring and alerting
- [ ] Use environment variables for secrets
- [ ] Restrict API access with API keys

### Load Balancing

```yaml
# Nginx configuration example
upstream api_backend {
    server api:8000;
}

upstream streamlit_backend {
    server dashboard:8501;
}

server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://api_backend;
    }

    location /dashboard/ {
        proxy_pass http://streamlit_backend;
    }
}
```

---

## Monitoring

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check model loading
curl http://localhost:8000/classes

# Check response time
time curl http://localhost:8000/health
```

### Metrics Collection

```python
# Example monitoring setup
from prometheus_client import Counter, Histogram
import time

prediction_count = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

@app.post("/predict/image")
async def predict(file: UploadFile):
    start = time.time()
    # ... prediction code ...
    prediction_latency.observe(time.time() - start)
    prediction_count.inc()
```

### Log Aggregation

```bash
# Tail logs
docker compose logs -f

# Save logs to file
docker compose logs > logs.txt

# Filter logs
docker compose logs api | grep ERROR
```

### Performance Monitoring

Monitor:
- **CPU Usage**: Should not exceed 80%
- **Memory Usage**: Keep under allocated limit
- **GPU Utilization**: Monitor VRAM usage
- **Response Time**: Target < 500ms for images
- **Throughput**: Track requests/second
- **Error Rate**: Keep below 0.1%

---

## Troubleshooting

### Common Issues

#### Issue: Model Not Loading
```bash
# Check model path
ls -la outputs/fire_smoke_detection/weights/

# Verify model file
file outputs/fire_smoke_detection/weights/best.pt

# Load model directly
python -c "from ultralytics import YOLO; m = YOLO('path/to/best.pt')"
```

#### Issue: Out of Memory
```bash
# Reduce batch size
# Reduce input image size
# Use GPU memory optimization
# Enable model quantization
```

#### Issue: Slow Inference
```bash
# Check GPU utilization
nvidia-smi

# Profile inference
python -m cProfile -s cumtime src/detect.py

# Enable TensorRT optimization
# Use ONNX export for faster inference
```

#### Issue: Docker Connection Failed
```bash
# Check Docker daemon
sudo systemctl start docker

# Check network
docker network ls

# Rebuild container
docker compose down
docker compose build --no-cache
docker compose up
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run with verbose output
python src/train.py --verbose

# Check configuration
python -c "from src.config import get_config; print(get_config())"
```

### Health Check

```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s $HEALTH_URL)

if echo $RESPONSE | grep -q "healthy"; then
    echo "✅ API is healthy"
    exit 0
else
    echo "❌ API health check failed"
    exit 1
fi
```

---

## Scaling Considerations

### Horizontal Scaling

```yaml
# Docker Compose scaling
services:
  api:
    deploy:
      replicas: 3
    
  # With load balancer
  load_balancer:
    image: nginx:latest
```

### Vertical Scaling

- Increase CPU/Memory allocation
- Use GPU for inference
- Optimize model (quantization, distillation)

### Caching Strategy

```python
# Implement result caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_cached(image_hash):
    # Cached predictions
    pass
```

---

## Backup and Recovery

```bash
# Backup model weights
tar -czf backup_models_$(date +%Y%m%d).tar.gz outputs/

# Backup database
docker exec fire-smoke-db pg_dump > backup_db.sql

# Restore from backup
tar -xzf backup_models_*.tar.gz
```

---

## Support

For deployment issues:
1. Check logs: `docker compose logs`
2. Verify configuration: Check configs/config.yaml
3. Test endpoints: Use API documentation
4. Review troubleshooting section above

---

**Happy Deploying!** 🚀
