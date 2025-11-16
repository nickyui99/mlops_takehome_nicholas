# MLOps Take-Home: Titanic Survival Predictor

[![CI/CD Pipeline](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/ci.yml/badge.svg)](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/ci.yml)
[![Deploy to Dev](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/deploy-dev.yml/badge.svg)](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/deploy-dev.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/nickyui99/mlops_takehome_nicholas/pkgs/container/titanic-predictor)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](https://github.com/nickyui99/mlops_takehome_nicholas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
  - [🎯 Advanced Deployment Strategies](#-advanced-deployment-strategies)
    - [Canary Deployment](#canary-deployment)
      - [Quick Start: Canary Deployment](#quick-start-canary-deployment)
      - [Canary Rollback (If Issues Detected)](#canary-rollback-if-issues-detected)
    - [Blue-Green Deployment](#blue-green-deployment)
      - [Quick Start: Blue-Green Deployment](#quick-start-blue-green-deployment)
      - [Blue-Green Rollback (If Issues Detected)](#blue-green-rollback-if-issues-detected)
    - [Strategy Comparison](#strategy-comparison)
    - [Deployment Workflow Recommendations](#deployment-workflow-recommendations)
      - [Production Deployment Pipeline](#production-deployment-pipeline)
      - [Automated Rollback Triggers](#automated-rollback-triggers)
    - [Complete Demo Scripts](#complete-demo-scripts)
      - [Full Canary Deployment Demo](#full-canary-deployment-demo)
      - [Full Blue-Green Deployment Demo](#full-blue-green-deployment-demo)
  - [🧪 Testing](#-testing)
    - [1. CI Unit Tests (GitHub Actions)](#1-ci-unit-tests-github-actions)
    - [2. Integration Tests (Docker/K8s)](#2-integration-tests-dockerk8s)
    - [3. Load Balancer Tests (`tests/test_lb.py`)](#3-load-balancer-tests-teststest_lbpy)
    - [4. Traffic Generation Tests (`tests/test_traffic.py`)](#4-traffic-generation-tests-teststest_trafficpy)
    - [Running All Tests](#running-all-tests)
    - [Test Environment Setup](#test-environment-setup)
  - [📝 Notes for Reviewers](#-notes-for-reviewers)
  - [🐛 Troubleshooting](#-troubleshooting)
    - [Common Issues](#common-issues)
  - [📄 License](#-license)

## 🎯 Overview

This project implements a complete MLOps pipeline for a Titanic survival prediction model, addressing all required capabilities:

✅ **Load Balancer** - NGINX reverse proxy distributing traffic across replicas  
✅ **Orchestration** - Docker Compose / Kubernetes with 3-replica deployment  
✅ **CI/CD** - GitHub Actions for automated testing and deployment  
✅ **Observability** - Prometheus + Grafana monitoring stack  
✅ **Model Tracking** - **MLflow for experiment tracking, model versioning, and registry**  
✅ **Traffic & Security** - Input validation, health checks, proper error handling  
✅ **State & Metadata** - PostgreSQL for prediction logging  
✅ **Cost & Scalability** - Resource limits, horizontal scaling ready  
✅ **Rollback** - Version-tagged Docker images with rollback capability  

**Model Details**: Logistic Regression trained on Titanic dataset (78-82% accuracy). Predicts passenger survival based on class, sex, age, family size, fare, and embarkation port. See [MODEL_CARD.md](MODEL_CARD.md) for full details.

## 🏗️ Architecture

```
                                    ┌──────────────────────────┐
                                    │   GitHub Actions CI/CD   │
                                    │  (Build, Test, Deploy)   │
                                    └────────────┬─────────────┘
                                                 │
┌─────────────┐    ┌──────────────┐    ┌───────┴───────────┐
│   Client    │───▶│     NGINX    │───▶│     FastAPI       │
│             │    │Load Balancer │    │   (3 replicas)    │
└─────────────┘    └──────────────┘    └───────┬───────────┘
                                               │
                    ┌──────────────────────────┼────────────────────────┐
                    ▼                          ▼                        ▼
              ┌──────────┐              ┌───────────┐            ┌──────────┐
              │PostgreSQL│              │  MLflow   │            │Prometheus│
              │(Pred Log)│              │  Server   │            │(Metrics) │
              └──────────┘              │(Model Reg)│            └────┬─────┘
                                        │(Artifacts)│                 │
                                        └─────┬─────┘                 │
                    ┌─────────────────────────┴─────────────┬─────────┘
                    ▼                                       ▼
              ┌──────────┐                            ┌─────────┐
              │ Airflow  │                            │ Grafana │
              │(Pipeline)│                            │(Dashbrd)│
              └──────────┘                            └─────────┘
```

**Key Components**:
- **NGINX**: Reverse proxy with load balancing across 3 API replicas
- **FastAPI**: Prediction service with health checks and metrics
- **PostgreSQL**: Persistent storage for prediction logs and metadata
- **MLflow**: Complete ML lifecycle management (tracking, registry, artifacts)
- **Airflow**: Workflow orchestration for training pipelines
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Monitoring dashboards and visualization
- **GitHub Actions**: Automated CI/CD pipelines

## 📁 Repository Structure

```
mlops_takehome_nicholas/
├── .github/
│   └── workflows/               # CI/CD pipelines
│       ├── ci.yml              # Lint, test, build, push
│       ├── deploy-dev.yml      # Deploy to dev cluster
│       └── promote-prod.yml    # Promote to production
│
├── airflow-data/               # Airflow metadata and logs
│   ├── dags/                   # Airflow DAG definitions
│   ├── logs/                   # Execution logs
│   ├── mlruns/                 # MLflow runs from Airflow
│   ├── plugins/                # Custom Airflow plugins
│   ├── artifacts/              # Model artifacts from pipeline runs
│   ├── train/                  # Training scripts for Airflow
│   └── airflow.cfg             # Airflow configuration
│
├── app/                        # FastAPI application
│   ├── main.py                 # API endpoints & middleware
│   ├── model_loader.py         # Model loading logic
│   ├── model.py                # Model wrapper
│   └── db.py                   # PostgreSQL connection
│
├── artifacts/                  # Saved model artifacts (MLflow)
│   └── titanic-classifier/     # Titanic model artifacts
│
├── dashboards/                 # Grafana dashboards (JSON)
│   └── Titanic_dashboard.json  # Main monitoring dashboard
│
├── deploy/
│   ├── k8s/                    # Kubernetes manifests
│   │   ├── namespace.yaml      # Namespace definition
│   │   ├── deployment.yaml     # Pod deployment (3 replicas)
│   │   ├── service.yaml        # ClusterIP service
│   │   ├── ingress.yaml        # Ingress configuration
│   │   ├── blue-green/         # Blue-green deployment configs
│   │   └── canary/             # Canary deployment configs
│   └── monitoring/             # Prometheus & Grafana configs
│       ├── prometheus-values.yaml
│       ├── prometheus-scrape-config.yaml
│       ├── grafana-values.yaml
│       └── servicemonitor.yaml
│
├── mlflow/                     # MLflow server data
│   ├── artifacts/              # Model artifacts storage
│   └── mlruns/                 # Experiment runs metadata
│
├── mlruns/                     # Local MLflow runs (training)
│   ├── 1/                      # Experiment 1
│   └── 2/                      # Experiment 2
│       └── models/             # Registered models
│
├── pipelines/                  # Airflow DAG definitions
│   └── titanic_training_dag.py # Titanic model training pipeline
│
├── sql/
│   └── schema.sql              # Database schema definitions
│
├── tests/                      # Test suite
│   ├── test_api_ci.py          # CI unit tests (FastAPI TestClient, no server)
│   ├── test_training_ci.py     # CI training tests (no MLflow server)
│   ├── test_api.py             # Integration tests (real server)
│   ├── test_lb.py              # Load balancer tests
│   └── test_traffic.py         # Traffic generation tests
│
├── train/
│   ├── train.py                # Standard training script
│   └── train_with_mlflow.py    # MLflow-integrated training
│
├── docker-compose.yaml         # Main orchestration (API, DB, MLflow)
├── docker-compose.dev.yaml     # Development configuration
├── docker-compose.airflow.yaml # Airflow orchestration
├── Dockerfile                  # Container image definition
├── nginx.conf                  # NGINX load balancer config
├── requirements.txt            # Python dependencies
│
├── .github/workflows/          # CI/CD pipelines
│   ├── ci.yml                  # Main CI/CD workflow (lint, test, build, push)
│   ├── deploy-dev.yml          # Deploy to dev environment
│   └── promote-prod.yml        # Production promotion (canary/blue-green)
│
├── MODEL_CARD.md               # Model documentation
├── README.md                   # Main documentation (this file)
└── VIDEO_DEMO_GUIDE.md         # Video demonstration guide
```

**Key Directory Purposes**:
- **app/**: Core prediction API service
- **train/**: Model training scripts with MLflow integration
- **tests/**: CI test suite (test_api_ci.py, test_training_ci.py)
- **deploy/**: Kubernetes manifests and monitoring configurations
- **mlflow/ & mlruns/**: ML experiment tracking and model registry
- **.github/workflows/**: Complete CI/CD pipeline automation
- **train/**: Model training scripts

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
docker compose up --scale titanic-api=5 -d

# Check logs
docker compose logs -f titanic-api

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

### C) CI/CD (GitHub Actions)

**Complete CI/CD Pipeline** with 3 automated workflows:

#### 1. **CI/CD Pipeline** (`.github/workflows/ci.yml`)
Automated testing and image building on every push/PR:

```yaml
Triggers: push to main/develop, pull requests
├─ Lint and Test Job
│  ├─ Lint with ruff
│  ├─ Run API tests (tests/test_api_ci.py)
│  └─ Run training tests (tests/test_training_ci.py)
└─ Build and Push Job (on main only)
   ├─ Build Docker image
   └─ Push to ghcr.io/nickyui99/mlops_takehome_nicholas:latest
```

**Status**: [![CI/CD Pipeline](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/ci.yml/badge.svg)](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/ci.yml)

#### 2. **Deploy to Dev** (`.github/workflows/deploy-dev.yml`)
Automated deployment after successful CI build:

```yaml
Triggers: After CI/CD Pipeline succeeds on main
├─ Validate K8s manifests
├─ Simulate dev deployment
└─ Run smoke tests (health + prediction)
```

**Status**: [![Deploy to Dev](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/deploy-dev.yml/badge.svg)](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/deploy-dev.yml)

#### 3. **Promote to Production** (`.github/workflows/promote-prod.yml`)
Manual production promotion with deployment strategy choice:

```yaml
Triggers: Manual workflow_dispatch
Strategy Options:
├─ Canary Deployment (gradual rollout: 25% → 100%)
│  ├─ Deploy canary version
│  ├─ Monitor metrics for 2 minutes
│  ├─ Promote to stable if healthy
│  └─ Rollback if issues detected
└─ Blue-Green Deployment (instant cutover)
   ├─ Deploy green environment
   ├─ Test green environment
   ├─ Switch traffic to green
   └─ Keep blue for rollback
```

**View Workflows**: [GitHub Actions](https://github.com/nickyui99/mlops_takehome_nicholas/actions)

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

**Quick Start**:
```bash
# Start MLflow UI
docker compose up mlflow -d

# Access at http://localhost:5000
# Train model: python train/train_with_mlflow.py
```

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
- GitHub Actions workflows include rollback on failed health checks
- Canary: Monitors metrics for 2 minutes, auto-rollback if unhealthy
- Blue-green: Keeps previous environment for instant rollback
- Health monitoring with automatic rollback capability
- See `.github/workflows/promote-prod.yml` for implementation

---

## 🎯 Advanced Deployment Strategies

### Canary Deployment

**Canary deployment** gradually shifts traffic from the stable version to a new version, minimizing risk by exposing only a small percentage of users initially.

#### Quick Start: Canary Deployment

```bash
# 1. Ensure stable deployment is running (3 replicas)
kubectl get pods -n mlops-dev -l app=titanic-predictor

# 2. Deploy canary version (1 replica = ~25% traffic with 3 stable pods)
kubectl apply -f deploy/k8s/canary/deployment-canary.yaml

# 3. Wait for canary to be ready
kubectl wait --for=condition=ready pod -l version=canary -n mlops-dev --timeout=60s

# 4. Monitor traffic distribution
kubectl get pods -n mlops-dev -l app=titanic-predictor -o wide

# 5. Generate test traffic
python tests/test_traffic.py --requests 100

# 6. Monitor metrics in Grafana (http://localhost:3000)
# - Check error rates by version
# - Compare latency (p50, p95, p99)
# - Monitor prediction distribution

# 7. If metrics are good, scale up canary (50% traffic)
kubectl scale deployment titanic-predictor-canary --replicas=3 -n mlops-dev

# 8. Continue monitoring, then promote to 100%
kubectl set image deployment/titanic-predictor \
  titanic-predictor=titanic-predictor:v2.0 -n mlops-dev

# 9. Remove canary deployment
kubectl delete deployment titanic-predictor-canary -n mlops-dev
```

#### Canary Rollback (If Issues Detected)

```bash
# Immediate rollback - scale canary to 0 (< 10 seconds)
kubectl scale deployment titanic-predictor-canary --replicas=0 -n mlops-dev

# Or delete canary entirely
kubectl delete deployment titanic-predictor-canary -n mlops-dev
```

**Traffic Distribution:**
- **10% Canary**: 1 canary pod + 9 stable pods = 10% traffic
- **25% Canary**: 1 canary pod + 3 stable pods = 25% traffic (default)
- **50% Canary**: 3 canary pods + 3 stable pods = 50% traffic
- **100% Canary**: Update stable deployment, remove canary

**Key Benefits:**
- ✅ Minimal blast radius (only 10-25% of traffic affected)
- ✅ Gradual rollout with monitoring at each stage
- ✅ Data-driven decisions based on real production metrics
- ✅ Easy rollback by scaling down/deleting canary

---

### Blue-Green Deployment

**Blue-Green deployment** maintains two identical environments. Blue is the current production, Green is the new version. Traffic switches instantly between them.

#### Quick Start: Blue-Green Deployment

```bash
# 1. Deploy Blue environment (current production v1.0)
kubectl apply -f deploy/k8s/blue-green/deployment-blue.yaml

# 2. Create service pointing to Blue
kubectl apply -f deploy/k8s/blue-green/service-blue.yaml

# 3. Verify Blue is serving traffic
kubectl get pods -n mlops-dev -l version=blue
kubectl port-forward svc/titanic-predictor 8000:8000 -n mlops-dev

# 4. Test Blue environment
$body = @{
    pclass=1; sex="female"; age=29.0
    sibsp=0; parch=0; fare=100.0; embarked="C"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict `
  -Method Post -Body $body -ContentType "application/json"
# Should show: "model_version": "1.0", "pod_name": "...-blue-..."

# 5. Deploy Green environment (new version v2.0) in parallel
kubectl apply -f deploy/k8s/blue-green/deployment-green.yaml

# 6. Wait for Green to be ready
kubectl wait --for=condition=ready pod -l version=green -n mlops-dev --timeout=120s

# 7. Verify both environments are running
kubectl get pods -n mlops-dev -l app=titanic-predictor -o wide
# Should show 3 Blue pods + 3 Green pods (6 total)

# 8. Test Green internally before switching traffic
kubectl run test-pod --image=curlimages/curl -it --rm -n mlops-dev -- sh
# Inside test pod:
curl http://titanic-predictor-green:8000/healthz

# 9. INSTANT CUTOVER: Switch service from Blue to Green (< 5 seconds)
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"green"}}}'

# 10. Verify traffic switch
Invoke-RestMethod -Uri http://localhost:8000/predict `
  -Method Post -Body $body -ContentType "application/json"
# Should now show: "model_version": "2.0", "pod_name": "...-green-..."

# 11. Monitor Green for stability (15-30 minutes)
python tests/test_traffic.py --requests 500

# 12. If stable, remove Blue environment
kubectl delete deployment titanic-predictor-blue -n mlops-dev
```

#### Blue-Green Rollback (If Issues Detected)

```bash
# INSTANT ROLLBACK: Switch service back to Blue (< 5 seconds)
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify rollback
Invoke-RestMethod -Uri http://localhost:8000/predict `
  -Method Post -Body $body -ContentType "application/json"
# Should show: "model_version": "1.0", "pod_name": "...-blue-..."
```

**Key Benefits:**
- ✅ Zero-downtime deployment (< 5 seconds cutover)
- ✅ Instant rollback (< 5 seconds)
- ✅ Full testing of Green before cutover
- ✅ No impact on user experience during switch

**Resource Requirements:**
- **During Deployment**: 2x pods (both Blue and Green running)
- **After Cleanup**: 1x pods (only active environment)

---

### Strategy Comparison

| Feature | **Canary** | **Blue-Green** |
|---------|-----------|---------------|
| **Traffic Shift** | Gradual (10%→25%→50%→100%) | Instant (0%→100%) |
| **Rollback Speed** | ~10 seconds | ~5 seconds |
| **Resource Usage** | 1.1-1.5x pods | 2x pods (during switch) |
| **Risk Level** | Very Low (minimal blast radius) | Low (all-or-nothing) |
| **Monitoring Time** | Extended (hours) | Quick (minutes) |
| **Best For** | High-risk changes, new features | Confident releases, hotfixes |
| **Complexity** | Medium | Low |

**When to Use:**
- **Canary**: Major model changes, new algorithms, uncertain deployments
- **Blue-Green**: Hotfixes, well-tested releases, infrastructure updates

---

### Deployment Workflow Recommendations

#### Production Deployment Pipeline

```
1. CI/CD Pipeline Triggers
   ├─ Run unit tests
   ├─ Build Docker image
   ├─ Push to registry
   └─ Trigger deployment

2. Choose Deployment Strategy
   ├─ High Risk → Canary (10%→50%→100%)
   └─ Low Risk  → Blue-Green (instant cutover)

3. Deploy & Monitor
   ├─ Check health endpoints
   ├─ Monitor error rates
   ├─ Compare latency metrics
   └─ Verify prediction quality

4. Decision Point
   ├─ Metrics Good → Proceed to 100%
   └─ Issues Found → Rollback immediately

5. Cleanup
   └─ Remove old deployments/canary pods
```

#### Automated Rollback Triggers

Set up automated rollback based on:
- ❌ Error rate > 5% for 5 minutes
- ❌ Latency p95 > 100ms for 10 minutes
- ❌ Health check failures > 3 consecutive
- ❌ Prediction anomalies detected

**Example Prometheus Alert:**
```yaml
groups:
- name: deployment_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected - trigger rollback"
```

---

### Complete Demo Scripts

#### Full Canary Deployment Demo
```bash
# deploy/k8s/canary/demo-canary.sh
#!/bin/bash
set -e

echo "🚀 Starting Canary Deployment Demo"

# 1. Baseline
echo "📊 Current stable deployment:"
kubectl get pods -n mlops-dev -l app=titanic-predictor

# 2. Deploy canary (25% traffic)
echo "🐤 Deploying canary (1 pod = 25% traffic)..."
kubectl apply -f deploy/k8s/canary/deployment-canary.yaml
kubectl wait --for=condition=ready pod -l version=canary -n mlops-dev --timeout=60s

# 3. Generate traffic
echo "🔄 Generating test traffic..."
python tests/test_traffic.py --requests 100 --quiet

# 4. Check distribution
echo "📈 Pod distribution:"
kubectl get pods -n mlops-dev -l app=titanic-predictor

echo "✅ Canary deployed! Monitor Grafana at http://localhost:3000"
echo "Next: Scale to 50% with: kubectl scale deployment titanic-predictor-canary --replicas=3 -n mlops-dev"
```

#### Full Blue-Green Deployment Demo
```bash
# deploy/k8s/blue-green/demo-blue-green.sh
#!/bin/bash
set -e

echo "🚀 Starting Blue-Green Deployment Demo"

# 1. Deploy Blue
echo "🔵 Deploying Blue environment (v1.0)..."
kubectl apply -f deploy/k8s/blue-green/deployment-blue.yaml
kubectl apply -f deploy/k8s/blue-green/service-blue.yaml
kubectl wait --for=condition=ready pod -l version=blue -n mlops-dev --timeout=60s

# 2. Deploy Green
echo "🟢 Deploying Green environment (v2.0)..."
kubectl apply -f deploy/k8s/blue-green/deployment-green.yaml
kubectl wait --for=condition=ready pod -l version=green -n mlops-dev --timeout=120s

# 3. Show both environments
echo "📊 Both environments running:"
kubectl get pods -n mlops-dev -l app=titanic-predictor -o wide

# 4. Switch to Green
echo "🔀 Switching traffic to Green..."
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"green"}}}'

echo "✅ Traffic switched to Green! Test at http://localhost:8000/predict"
echo "Rollback command: kubectl patch service titanic-predictor -n mlops-dev -p '{\"spec\":{\"selector\":{\"version\":\"blue\"}}}'"
```

---

📺 **For detailed video demo guide, see [VIDEO_DEMO_GUIDE.md](VIDEO_DEMO_GUIDE.md)**

## 🧪 Testing

The test suite includes both **CI unit tests** (no infrastructure) and **integration tests** (Docker/K8s):

### 1. CI Unit Tests (GitHub Actions)

**API Tests** (`tests/test_api_ci.py`): FastAPI TestClient-based tests without server dependencies.

```bash
# Run CI tests locally
python -m pytest tests/test_api_ci.py -v
```

**Test Coverage**:
- ✅ Health check endpoint
- ✅ Valid prediction (returns survived/died + probability)
- ✅ Missing field validation (422 error)
- ✅ Metrics endpoint (Prometheus format)

**Training Tests** (`tests/test_training_ci.py`): Model validation without MLflow server.

```bash
# Run training tests
python -m pytest tests/test_training_ci.py -v
```

**Test Coverage**:
- ✅ Training script import (no MLflow connection on import)
- ✅ Model artifact existence
- ✅ Model loading with joblib
- ✅ Prediction shape validation

**Run all CI tests**:
```bash
python -m pytest tests/test_api_ci.py tests/test_training_ci.py -v
# Expected: 8 passed (4 API + 4 training)
```

---

### 2. Integration Tests (Docker/K8s)

**API Integration Tests** (`tests/test_api.py`): End-to-end API tests with real server.

**Run tests**:
```bash
# Start services first
docker compose up -d

# Run integration tests
python tests/test_api.py
```

**Test Coverage**:
- ✅ Real HTTP prediction endpoint
- ✅ High survival probability (first-class female)
- ✅ Low survival probability (third-class male)
- ✅ Response structure validation

**Expected Output**:
```
Testing Titanic prediction API...
Input: {'pclass': 1, 'sex': 'female', 'age': 29.0, ...}
Response: {'prediction': 'survived', 'survival_probability': 0.92, ...}
```

### 3. Load Balancer Tests (`tests/test_lb.py`)

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

### 4. Traffic Generation Tests (`tests/test_traffic.py`)

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

**CI Unit Tests** (no infrastructure needed):
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all CI tests
python -m pytest tests/test_api_ci.py tests/test_training_ci.py -v
# Expected: 8 passed (4 API + 4 training)
```

**Integration Tests** (requires Docker):
```bash
# Start all services
docker compose up --build -d

# Wait for services to be ready
sleep 10

# Run integration tests
python tests/test_api.py              # API endpoint tests
python tests/test_lb.py               # Load balancer tests
python tests/test_traffic.py --requests 50  # Traffic generation

# Check Prometheus metrics
curl http://localhost:8000/metrics

# View logs
docker compose logs -f
```

### Test Environment Setup

**CI Environment** (GitHub Actions):
```yaml
# Automated on every push/PR
# See: .github/workflows/ci.yml
- Linting with ruff
- 8 unit tests (test_api_ci.py + test_training_ci.py)
- Docker image build and push to GHCR
```

**Local Environment**:
```bash
# Install dependencies
pip install requests pytest httpx

# Verify Docker services
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

## 📝 Notes for Reviewers

**Design Decisions:**
1. **SQLite for MLflow**: Simple local setup; would use remote tracking server in production
2. **No DVC**: Titanic dataset is from seaborn and deterministic; DVC not needed for this scale
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

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with**: Python, FastAPI, MLflow, scikit-learn, Docker, Kubernetes, Prometheus, Grafana, PostgreSQL, NGINX

**Repository**: https://github.com/nickyui99/mlops_takehome_nicholas