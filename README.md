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
    - [1. API Unit Tests (`tests/test_api.py`)](#1-api-unit-tests-teststest_apipy)
    - [2. Load Balancer Tests (`tests/test_lb.py`)](#2-load-balancer-tests-teststest_lbpy)
    - [3. Traffic Generation Tests (`tests/test_traffic.py`)](#3-traffic-generation-tests-teststest_trafficpy)
    - [Running All Tests](#running-all-tests)
    - [Test Environment Setup](#test-environment-setup)
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
✅ **Orchestration** - Docker Compose / Kubernetes with 3-replica deployment  
✅ **CI/CD** - GitHub Actions for automated testing and deployment  
✅ **Observability** - Prometheus + Grafana monitoring stack  
✅ **Model Tracking** - **MLflow for experiment tracking, model versioning, and registry** 🆕  
✅ **Traffic & Security** - Input validation, health checks, proper error handling  
✅ **State & Metadata** - PostgreSQL for prediction logging  
✅ **Cost & Scalability** - Resource limits, horizontal scaling ready  
✅ **Rollback** - Version-tagged Docker images with rollback capability  

**Model Details**: Logistic Regression trained on Titanic dataset (78-82% accuracy). Predicts passenger survival based on class, sex, age, family size, fare, and embarkation port. See [MODEL_CARD.md](MODEL_CARD.md) for full details.

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│   Client    │───▶│     NGINX    │───▶│   FastAPI     │
│             │    │Load Balancer │    │  (3 replicas) │
└─────────────┘    └──────────────┘    └───────┬───────┘
                                               │
                    ┌──────────────────────────┼──────────────────┐
                    ▼                          ▼                  ▼
              ┌──────────┐              ┌───────────┐      ┌──────────┐
              │PostgreSQL│              │ MLflow 🆕 │      │Prometheus│
              │(Pred Log)│              │(Model Reg)│      │(Metrics) │
              └──────────┘              └─────┬─────┘      └────┬─────┘
                                              │                 │
                                              └────────┬────────┘
                                                       ▼
                                                  ┌─────────┐
                                                  │ Grafana │
                                                  └─────────┘
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

**Implementation**: ✅ **MLflow Server with Full Model Registry** 🆕

**MLflow Features**:
- 🔬 **Experiment Tracking**: Track all training runs with hyperparameters and metrics
- 📊 **Model Registry**: Centralized model versioning with metadata
- 📁 **Artifact Storage**: Persistent storage for models and preprocessing objects
- 📈 **Metrics Logging**: Real-time prediction latency and performance tracking
- 🔄 **Model Comparison**: Side-by-side comparison of different model versions
- 🎯 **Model Lineage**: Complete history of model training and deployment

**Quick Start**:
```bash
# Start all services including MLflow
docker-compose up -d

# Access MLflow UI at http://localhost:5000
open http://localhost:5000

# Train a new model version
python train/train_with_mlflow.py --version 2.0
```

**Model Versioning Workflow**:
1. Train new model with MLflow tracking
2. Compare metrics in MLflow UI
3. Update `MODEL_VERSION` in docker-compose.yaml
4. Restart services to deploy new version
5. Rollback by reverting `MODEL_VERSION` if needed

**Serving Metrics** (logged per API replica):
- `prediction_latency_ms`: Real-time prediction latency
- `survival_probability`: Distribution of predicted probabilities
- Pod-level performance tracking

**Training Metrics** (logged per experiment):
- `train_accuracy`, `test_accuracy`
- `precision`, `recall`, `f1_score`
- Hyperparameters: `n_estimators`, `max_depth`, etc.

**Database Logging**: All predictions stored in PostgreSQL with:
- `request_id`, `model_version`, `latency_ms`
- Input features and prediction
- Timestamp for drift analysis

📖 **See [README_MLFLOW.md](README_MLFLOW.md) for detailed MLflow guide**

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

✅ **Complete rollback procedures documented** with exact commands for all scenarios.

**Version Management**:
- Docker images tagged with `latest` and `sha-<commit>`
- Git tags for release versions
- MLflow model versioning for model rollback
- Kubernetes revision history maintained

**Quick Rollback Commands**:

**Docker Compose** (< 30 seconds):
```bash
# Rollback model version only
# Edit docker-compose.yaml: MODEL_VERSION: "1.0"
docker-compose restart titanic-api
```

**Kubernetes** (< 1 minute):
```bash
# Rollback to previous version (most common)
kubectl rollout undo deployment/titanic-predictor -n mlops-dev

# Rollback to specific revision
kubectl rollout undo deployment/titanic-predictor --to-revision=2 -n mlops-dev

# Verify rollback
kubectl rollout status deployment/titanic-predictor -n mlops-dev
```

**Helm** (< 2 minutes):
```bash
# View release history
helm history titanic-predictor -n mlops-dev

# Rollback to previous release
helm rollback titanic-predictor -n mlops-dev

# Rollback to specific revision
helm rollback titanic-predictor 2 -n mlops-dev
```

**Canary Rollback** (< 10 seconds):
```bash
# Abort canary deployment
kubectl delete deployment/titanic-predictor-canary -n mlops-dev

# Or scale down canary
kubectl scale deployment/titanic-predictor-canary --replicas=0 -n mlops-dev
```

**Blue-Green Rollback** (< 5 seconds):
```bash
# Switch service back to blue (previous version)
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

**MLflow Model Rollback**:
```bash
# Update model version in deployment
kubectl set env deployment/titanic-predictor MODEL_VERSION=1.0 -n mlops-dev
```

**Automated Rollback**: 
- GitHub Actions can trigger rollback on failed health checks
- Health monitoring with automatic rollback capability
- Alerts sent via Slack/email on rollback events

📖 **See [ROLLBACK_PROCEDURES.md](ROLLBACK_PROCEDURES.md) for comprehensive rollback guide including:**
- Detailed step-by-step procedures for all deployment methods
- Canary deployment rollback strategies
- Blue-green deployment rollback procedures
- Emergency rollback procedures
- Rollback verification checklist
- Automated rollback workflows

## 🧪 Testing

The test suite includes three test files covering different aspects of the MLOps system:

### 1. API Unit Tests (`tests/test_api.py`)

Basic API functionality tests with sample predictions for different passenger profiles.

**Run tests**:
```bash
# Ensure the API is running first
docker compose up -d

# Run API tests
python tests/test_api.py
```

**Test Coverage**:
- ✅ Prediction endpoint (`/predict`)
- ✅ High survival probability scenario (First-class female passenger)
- ✅ Low survival probability scenario (Third-class male passenger)
- ✅ Response structure validation

**Expected Output**:
```
Testing Titanic prediction API...
Input: {'pclass': 1, 'sex': 'female', 'age': 29.0, ...}
Response: {'prediction': 'survived', 'survival_probability': 0.92, ...}

Input: {'pclass': 3, 'sex': 'male', 'age': 25.0, ...}
Response: {'prediction': 'died', 'survival_probability': 0.15, ...}
```

### 2. Load Balancer Tests (`tests/test_lb.py`)

Verifies that the NGINX load balancer correctly distributes requests across multiple API replicas.

**Run tests**:
```bash
# Start services with 3 replicas
docker compose up --build -d

# Verify replicas are running
docker compose ps

# Test load distribution
python tests/test_lb.py
```

**Test Coverage**:
- ✅ Request distribution across replicas
- ✅ Load balancing behavior validation
- ✅ Pod name differentiation

**Expected Output**:
```
Testing load balancer distribution across replicas...
Sending 6 requests to: http://localhost:8000/predict

Request 1 → Pod: titanic-api-1 | Prediction: survived
Request 2 → Pod: titanic-api-2 | Prediction: survived
Request 3 → Pod: titanic-api-3 | Prediction: survived
Request 4 → Pod: titanic-api-1 | Prediction: survived
Request 5 → Pod: titanic-api-2 | Prediction: survived
Request 6 → Pod: titanic-api-3 | Prediction: survived
```

**Note**: In Docker Compose, `pod_name` will reflect container names (`titanic-api-1`, `titanic-api-2`, etc.). In Kubernetes, you'll see K8s pod names.

### 3. Traffic Generation Tests (`tests/test_traffic.py`)

Comprehensive traffic generation script for testing metrics, monitoring, and error handling. Simulates realistic production traffic patterns including both successful requests and various error scenarios.

**Run tests**:
```bash
# Start services
docker compose up -d

# Generate 100 requests with 10% error rate (default)
python tests/test_traffic.py

# Custom configuration
python tests/test_traffic.py --requests 200 --delay 100 --error-rate 0.15

# Options:
#   --url           Base URL (default: http://localhost:8000)
#   --requests      Number of requests (default: 100)
#   --delay         Delay between requests in ms (default: 50)
#   --error-rate    Error percentage 0.0-1.0 (default: 0.1)
#   --quiet         Suppress verbose output
```

**Test Coverage**:
- ✅ Random passenger data generation
- ✅ Valid prediction requests
- ✅ Invalid input validation (missing fields, wrong types, invalid values)
- ✅ 4xx error scenarios (400, 404)
- ✅ 5xx error scenarios (500 internal server error)
- ✅ Latency tracking and statistics
- ✅ Error distribution analysis
- ✅ Load balancer distribution verification
- ✅ Grafana metrics generation

**Error Scenarios Tested**:
- Missing required fields (e.g., `pclass`, `age`, `fare`)
- Invalid data types (e.g., string instead of number)
- Invalid value ranges (e.g., negative age, invalid embarkation port)
- Non-existent endpoints (404 errors)
- Simulated server errors (500 errors)

**Expected Output**:
```
======================================================================
Generating 100 requests to http://localhost:8000
Error rate: 10.0%
======================================================================

[  1/100] ✓ Pod: titanic-api | Prediction: survived  | Probability: 0.8542 | Latency: 12.45ms
[  2/100] ✓ Pod: titanic-api | Prediction: died      | Probability: 0.1234 | Latency: 11.23ms
[  3/100] ⚠ Error [400]: Bad Request: invalid value for pclass
...

======================================================================
Traffic Generation Summary
======================================================================
Total Requests:     100
Successful:         90 (90.0%)
Failed:             10 (10.0%)
  - Expected:       10
  - Unexpected:     0

Error Breakdown:
  - 4xx Errors:     8
  - 5xx Errors:     2

Latency Statistics:
  Mean:             12.34ms
  Median:           11.50ms
  Min:              8.20ms
  Max:              45.67ms

======================================================================
✓ Traffic generation complete!
  Check Grafana dashboard at: http://localhost:3000
  Dashboard: Titanic Survival Prediction Dashboard
======================================================================
```

**Use Cases**:
- **Metrics Testing**: Generate traffic to populate Grafana dashboards
- **Load Testing**: Simulate high-volume production traffic
- **Error Handling**: Verify proper error responses and logging
- **Monitoring Validation**: Ensure Prometheus correctly captures metrics
- **Performance Baseline**: Establish latency benchmarks

### Running All Tests

```bash
# Start all services
docker compose up --build -d

# Wait for services to be ready
sleep 10

# Run all test suites
python tests/test_api.py
python tests/test_lb.py
python tests/test_traffic.py --requests 50

# Check Prometheus metrics
curl http://localhost:8000/metrics

# View logs
docker compose logs -f
```

### Test Environment Setup

**Prerequisites**:
```bash
# Install testing dependencies
pip install requests pytest

# Verify services are running
docker compose ps

# Check API health
curl http://localhost:8000/healthz
```

**Cleanup**:
```bash
# Stop services
docker compose down

# Remove volumes (optional)
docker compose down -v
```

---

**Built with**: Python, FastAPI, MLflow, scikit-learn, Docker, Kubernetes, Prometheus, Grafana, PostgreSQL, NGINX

**Repository**: https://github.com/nickyui99/mlops_takehome_nicholas

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