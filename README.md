# MLOps Take-Home: Titanic Survival Predictor

Production-ready ML system demonstrating end-to-end MLOps practices with load balancing, orchestration, CI/CD, and observability.

## 📋 Table of Contents
- [MLOps Take-Home: Titanic Survival Predictor](#mlops-take-home-titanic-survival-predictor)
  - [📋 Table of Contents](#-table-of-contents)
  - [🎯 Overview](#-overview)
  - [🏗️ Architecture](#️-architecture)
  - [📁 Repository Structure](#-repository-structure)
  - [🚀 Quick Start](#-quick-start)
    - [Prerequisites](#prerequisites)
  - [✅ Required Capabilities](#-required-capabilities)
    - [A) Load Balancer (must-have)](#a-load-balancer-must-have)
    - [B) Orchestration](#b-orchestration)
    - [C) CI/CD (GitHub Actions only)](#c-cicd-github-actions-only)
    - [D) Observability (Grafana + Prometheus)](#d-observability-grafana--prometheus)
    - [E) Model Tracking / Monitoring](#e-model-tracking--monitoring)
    - [F) Traffic \& Security](#f-traffic--security)
    - [G) State \& Metadata](#g-state--metadata)
    - [H) Cost \& Scalability](#h-cost--scalability)
    - [I) Rollback](#i-rollback)
  - [🧪 Testing](#-testing)
    - [Load Balancer Test](#load-balancer-test)
  - [✅ Reproducibility Checklist](#-reproducibility-checklist)
  - [🔐 Security \& Best Practices](#-security--best-practices)
  - [📝 Notes for Reviewers](#-notes-for-reviewers)
  - [🐛 Troubleshooting](#-troubleshooting)
    - [Common Issues](#common-issues)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)

## 🎯 Overview

This project implements a complete MLOps pipeline for a Titanic survival prediction model, addressing all required capabilities:

✅ **Load Balancer** - NGINX reverse proxy distributing traffic across replicas  
✅ **Orchestration** - Kubernetes with 3-replica deployment  
✅ **CI/CD** - GitHub Actions for automated testing and deployment  
✅ **Observability** - Prometheus + Grafana monitoring stack  
✅ **Model Tracking** - MLflow for experiment tracking and versioning  
✅ **Traffic & Security** - Input validation, health checks, proper error handling  
✅ **State & Metadata** - PostgreSQL for prediction logging  
✅ **Cost & Scalability** - Resource limits, horizontal scaling ready  
✅ **Rollback** - Version-tagged Docker images with rollback capability  

**Model Details**: Logistic Regression trained on Titanic dataset (78-82% accuracy). Predicts passenger survival based on class, sex, age, family size, fare, and embarkation port. See [MODEL_CARD.md](MODEL_CARD.md) for full details.

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│   Client    │───▶│     NGINX    │───▶│   FastAPI     │
│             │    │Load Balancer │    │   (3 pods)    │
└─────────────┘    └──────────────┘    └───────┬───────┘
                                               │
                    ┌──────────────────────────┼──────────────┐
                    ▼                          ▼              ▼
              ┌──────────┐              ┌───────────┐  ┌──────────┐
              │PostgreSQL│              │ MLflow    │  │Prometheus│
              │(Pred Log)│              │(Model Reg)│  │(Metrics) │
              └──────────┘              └───────────┘  └──────────┘
```

## 📁 Repository Structure

```
├── app/                      # FastAPI application
│   ├── main.py              # API endpoints & middleware
│   ├── model_loader.py      # Model loading logic
│   ├── model.py             # Model wrapper
│   └── db.py                # PostgreSQL connection
├── train/
│   └── train.py             # Training script with MLflow
├── tests/
│   ├── test_api.py          # API unit tests
│   └── test_lb.py           # Load balancer test
├── deploy/
│   ├── k8s/                 # Kubernetes manifests
│   │   ├── deployment.yaml  # Pod deployment (3 replicas)
│   │   ├── service.yaml     # ClusterIP service
│   │   ├── ingress.yaml     # Ingress configuration
│   │   └── namespace.yaml   # Namespace definition
│   └── monitoring/          # Prometheus & Grafana configs
│       ├── prometheus-values.yaml
│       └── grafana-values.yaml
├── pipelines/
│   └── titanic_training_dag.py # Airflow DAG
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml              # Lint, test, build, push
│   ├── deploy-dev.yml      # Deploy to dev cluster
│   └── promote-prod.yml    # Promote to production
├── artifacts/               # Saved model artifacts
├── dashboards/              # Grafana dashboards (JSON)
├── sql/                     # Database schemas
├── Dockerfile               # Container image
├── docker-compose.yaml      # Multi-service orchestration
├── requirements.txt         # Python dependencies
└── MODEL_CARD.md            # Model documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose

**Note**: This project uses **Docker Compose** for local development and orchestration. Kubernetes deployment files are provided for production use but are optional for local testing.

**1. Clone and setup:**
```bash
git clone https://github.com/nickyui99/mlops_takehome_nicholas.git
cd mlops_takehome_nicholas
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**2. Train the model:**
```bash
python train/train.py
```

**3. Start services with load balancer:**
```bash
docker compose up --build
```

**4. Test the API:**
```powershell
# Health check
curl http://localhost:8000/healthz

# Make prediction - First-class female passenger (high survival probability)
$body = @{
    pclass=1
    sex="female"
    age=29.0
    sibsp=0
    parch=0
    fare=100.0
    embarked="C"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Body $body -ContentType "application/json"

# Expected output:
# {
#   "prediction": "survived",
#   "survival_probability": 0.92,
#   "latency_ms": 15.23,
#   "model_version": "v20251114_174012",
#   "pod_name": "titanic-api"
# }
```

## ✅ Required Capabilities

### A) Load Balancer (must-have)

**Implementation**: NGINX reverse proxy with Docker Compose scaling

- **Configuration**: `nginx.conf` distributes traffic across API replicas
- **Scaling**: Docker Compose configured with 3 replicas (`deploy.replicas: 3`)
- **Load balancing**: NGINX automatically distributes requests across instances
- **Health checks**: `/healthz` endpoint monitoring
- **Testing**: `tests/test_lb.py` verifies distribution

**Verification**:
```bash
# Start services with 3 replicas
docker compose up --build -d

# Verify 3 instances running
docker compose ps

# Test load distribution
python tests/test_lb.py
# Expected: Requests distributed to different pod_names
```

### B) Orchestration

**Implementation**: Docker Compose with multi-service orchestration and scaling

**Features**:
- **3 replicas** of the API service for high availability
- **Multi-container** orchestration (PostgreSQL, API, NGINX)
- **Service discovery** and networking
- **Dependency management** (API depends on PostgreSQL)
- **Load balancing** via NGINX reverse proxy

**Running the orchestrated stack**:
```bash
# Start all services with 3 API replicas
docker compose up --build -d

# View running services
docker compose ps

# Scale up/down if needed
docker compose up --scale iris-api=5 -d

# Check logs
docker compose logs -f iris-api

# Stop all services
docker compose down
```

**Optional: Kubernetes Deployment** (for production environments)

If you have a Kubernetes cluster available (Docker Desktop K8s, kind, minikube, or cloud):

**Prerequisites**:
```bash
# Ensure you're using the correct cluster context
kubectl config get-contexts

# Switch to docker-desktop (if using Docker Desktop)
kubectl config use-context docker-desktop

# Or switch to your preferred cluster
kubectl config use-context <your-cluster-name>

# Verify cluster is ready
kubectl get nodes
```

**Deployment Steps**:
```bash
# 1. Build and verify image (for local clusters)
docker build -t titanic-predictor:latest .
docker images | grep titanic-predictor

# 2. Create namespace
kubectl apply -f deploy/k8s/namespace.yaml

# 3. Deploy PostgreSQL using Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Windows PowerShell:
helm install postgres bitnami/postgresql -n mlops-dev `
  --set auth.postgresPassword=postgres `
  --set auth.database=mlops

# Linux/Mac:
helm install postgres bitnami/postgresql -n mlops-dev \
  --set auth.postgresPassword=postgres,auth.database=mlops

# 4. Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n mlops-dev --timeout=300s

# 5. Deploy application
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml

# 6. Verify deployment
kubectl get pods -n mlops-dev
kubectl get svc -n mlops-dev

# 7. Access the application (port forward)
kubectl port-forward svc/titanic-predictor-svc 8000:8000 -n mlops-dev
```

**Test the Kubernetes deployment**:
```powershell
# In a new terminal - Health check
curl http://localhost:8000/healthz

# Make prediction - Third-class male passenger (low survival probability)
$body = @{
    pclass=3
    sex="male"
    age=25.0
    sibsp=0
    parch=0
    fare=7.25
    embarked="S"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Body $body -ContentType "application/json"

# Expected output:
# {
#   "prediction": "died",
#   "survival_probability": 0.15,
#   "latency_ms": 12.45,
#   "model_version": "v20251114_174012",
#   "pod_name": "titanic-predictor-xyz"
# }
```

**Kubernetes Features**:
- 3 replica pods for high availability
- Resource limits (128Mi-256Mi memory, 100m-200m CPU)
- Liveness & readiness probes
- ClusterIP service with load balancing

### C) CI/CD (GitHub Actions only)

**Workflows**:

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Triggers on push/PR to main
   - Lints with `ruff`
   - Runs unit tests with `pytest`
   - Builds Docker image
   - Pushes to GitHub Container Registry

2. **Deploy to Dev** (`.github/workflows/deploy-dev.yml`)
   - Triggers on push to main
   - Deploys to development cluster
   - Runs smoke tests

3. **Promote to Prod** (`.github/workflows/promote-prod.yml`)
   - Manual workflow dispatch
   - Deploys tested image to production
   - Post-deployment health checks

### D) Observability (Grafana + Prometheus)

**Metrics Collection**:
- Prometheus scrapes `/metrics` endpoint every 15s
- Custom metrics: `http_requests_total`, `http_request_duration_seconds`
- FastAPI exposes metrics via `/metrics` endpoint

**Local Testing**:
```bash
# Check metrics endpoint
curl http://localhost:8000/metrics
```

**Optional: Deploy monitoring stack** (requires Kubernetes cluster)

```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  -n mlops-dev -f deploy/monitoring/prometheus-values.yaml

# Install Grafana
helm install grafana grafana/grafana \
  -n mlops-dev -f deploy/monitoring/grafana-values.yaml

# Get Grafana password
kubectl get secret grafana -n mlops-dev -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward
kubectl port-forward svc/grafana 3000:80 -n mlops-dev
```

**Dashboard**: Import `dashboards/titanic-dashboard.json` to visualize:
- Request rate and latency
- Error rates
- Model version distribution

**Structured Logging**: JSON logs with `request_id`, `model_version`, `pod_name`, `latency_ms`

### E) Model Tracking / Monitoring

**Implementation**: MLflow for experiment tracking

**Features**:
- Tracks hyperparameters, metrics, and artifacts
- Model versioning with run IDs
- Local artifact storage in `artifacts/`
- SQLite backend for metadata

**Start MLflow UI**:
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

**Database Logging**: All predictions stored in PostgreSQL with:
- `request_id`, `model_version`, `latency_ms`
- Input features and prediction
- Timestamp for drift analysis

### F) Traffic & Security

**Implemented**:
- ✅ **Input Validation**: Pydantic models enforce schema
- ✅ **Health Checks**: `/healthz` endpoint for liveness/readiness
- ✅ **Error Handling**: Proper HTTP status codes (400, 500)
- ✅ **Request IDs**: UUID tracking for debugging
- ✅ **Non-root Container**: Security best practice

**TODO for Production**:
- Move DB credentials to Kubernetes secrets
- Add rate limiting
- Implement authentication/authorization

### G) State & Metadata

**Database Schema** (`sql/schema.sql`):
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(36) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    prediction VARCHAR(20) NOT NULL,
    latency_ms FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Query predictions**:
```bash
docker exec -it postgres psql -U postgres -d mlops -c "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;"
```

### H) Cost & Scalability

**Resource Management**:
- **CPU**: 100m request, 200m limit per pod
- **Memory**: 128Mi request, 256Mi limit per pod
- **Replicas**: 3 pods for availability

**Horizontal Scaling**:
```bash
# Scale up
kubectl scale deployment titanic-predictor --replicas=5 -n mlops-dev

# Auto-scaling (HPA) ready
kubectl autoscale deployment titanic-predictor --cpu-percent=80 --min=3 --max=10 -n mlops-dev
```

**Cost Considerations**:
- Lightweight model (< 1MB)
- Fast inference (< 50ms)
- Efficient resource utilization

### I) Rollback

**Version Management**:
- Docker images tagged with `latest` and `sha-<commit>`
- Git tags for release versions

**Rollback procedure (Docker Compose)**:
```bash
# Rollback to specific image version
docker compose down
docker tag ghcr.io/nickyui99/titanic-predictor:sha-abc123 titanic-predictor:latest
docker compose up -d

# Or pull and use specific version
docker pull ghcr.io/nickyui99/titanic-predictor:sha-abc123
docker tag ghcr.io/nickyui99/titanic-predictor:sha-abc123 titanic-predictor:latest
docker compose up -d
```

**Rollback procedure (Kubernetes)** - if using K8s deployment:
```bash
# List available versions
kubectl get rs -n mlops-dev

# Rollback to previous version
kubectl rollout undo deployment/titanic-predictor -n mlops-dev

# Rollback to specific revision
kubectl rollout undo deployment/titanic-predictor --to-revision=2 -n mlops-dev

# Check rollout status
kubectl rollout status deployment/titanic-predictor -n mlops-dev
```

**Automated Rollback**: GitHub Actions can trigger rollback on failed health checks.

## 🧪 Testing

**Run tests locally**:
```bash
# Unit tests
pytest tests/test_api.py -v

# Load balancer test (requires running service)
python tests/test_lb.py
```

**Test Coverage**:
- ✅ API endpoint validation (`/predict`, `/healthz`)
- ✅ Model loading and inference
- ✅ Input validation (Pydantic)
- ✅ Load balancing distribution
- ✅ Database logging
- ✅ Prometheus metrics

---

**Built with**: Python, FastAPI, MLflow, scikit-learn, Docker, Kubernetes, Prometheus, Grafana, PostgreSQL, NGINX

**Repository**: https://github.com/nickyui99/mlops_takehome_nicholas
- **Load Balancing**: Verify requests distribute across pods

### Load Balancer Test

`tests/test_lb.py` is designed to demonstrate distribution across multiple replicas. Run it after deploying to Kubernetes with 3 replicas (as defined in `deploy/k8s/deployment.yaml`) or after setting up a load-balanced multi-replica environment. In plain Docker Compose with a single `titanic-api` instance, all responses will show the same `pod_name`.

## ✅ Reproducibility Checklist

- [x] **Code versioned**: Git repository with commit history
- [x] **Environment captured**: `requirements.txt` + `Dockerfile`
- [x] **Data versioned**: Titanic dataset versioned via seaborn package (pinned in requirements)
- [x] **Random seeds fixed**: `random_state=42` in training script
- [x] **Metrics logged**: MLflow tracks accuracy and all parameters
- [x] **Artifacts stored**: Models saved to `artifacts/` and MLflow registry
- [x] **CI validates**: GitHub Actions runs tests on every commit
- [x] **Model card**: Documentation in `MODEL_CARD.md`

## 🔐 Security & Best Practices

- ✅ Non-root user in Docker container
- ✅ Input validation with Pydantic
- ✅ Resource limits in Kubernetes
- ✅ Secrets management via environment variables
- ✅ Structured logging (no sensitive data in logs)
- ⚠️ **TODO**: Move DB credentials to K8s secrets for production

## 📝 Notes for Reviewers

**Design Decisions:**
1. **SQLite for MLflow**: Simple local setup; would use remote tracking server in production
2. **No DVC**: Iris dataset is embedded in sklearn and deterministic; DVC not needed for this scale
3. **Logistic Regression**: Simple, interpretable baseline model
4. **3 Replicas**: Balances availability with resource usage

**Production Enhancements:**
- Implement model A/B testing framework
- Add data drift detection using prediction logs
- Set up centralized log aggregation (ELK/Splunk)
- Implement model retraining pipeline
- Add horizontal pod autoscaling (HPA)

**Recent Improvements:**
- ✅ Fixed Airflow 2.10.x RecursionError with subprocess isolation and logging suppression
- ✅ Enhanced Docker build process with proper `.dockerignore`
- ✅ Improved documentation for multi-platform support (Windows PowerShell + Linux/Mac)
- ✅ Added comprehensive troubleshooting documentation in `AIRFLOW_ISSUE_ANALYSIS.md`

## 🐛 Troubleshooting

### Common Issues

**Airflow DAG fails with zombie task detection:**
- See [AIRFLOW_ISSUE_ANALYSIS.md](AIRFLOW_ISSUE_ANALYSIS.md) for detailed analysis
- Solution: Use subprocess isolation for training tasks (already implemented)

**Docker build fails with "airflow-data" access errors:**
- Ensure `.dockerignore` includes `airflow-data/`, `tests/`, `dashboards/`, `deploy/`

**Port 8000 already in use:**
- Check if docker-compose is running: `docker-compose ps`
- Stop conflicting services: `docker-compose down`

**MLflow server won't accept connections:**
- For local development: `mlflow ui` (localhost only)
- For network access: `mlflow server --host 0.0.0.0 --app-name basic-auth`

**Kubernetes not available:**
- Enable Kubernetes in Docker Desktop settings (see Deployment section)
- Verify with: `kubectl version --client`

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run linting: `ruff check .`
5. Submit PR with clear description

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with**: Python, FastAPI, MLflow, scikit-learn, Docker, Kubernetes, Prometheus, Grafana, PostgreSQL, NGINX

**Repository**: https://github.com/nickyui99/mlops_takehome_nicholas