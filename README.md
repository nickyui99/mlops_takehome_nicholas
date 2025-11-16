# MLOps Take-Home: Titanic Survival Predictor

[![CI/CD Pipeline](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/ci.yml/badge.svg)](https://github.com/nickyui99/mlops_takehome_nicholas/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg?logo=python)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready ML system demonstrating end-to-end MLOps practices with Kubernetes orchestration, load balancing, CI/CD, and observability.

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [✅ MLOps Capabilities](#-mlops-capabilities)
- [🚀 Quick Start](#-quick-start)
  - [Docker Compose](#docker-compose)
  - [Kubernetes](#kubernetes)
- [📁 Repository Structure](#-repository-structure)
- [🧪 Testing](#-testing)
- [🔄 Deployment Strategies](#-deployment-strategies)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🔙 Rollback Procedures](#-rollback-procedures)
- [🐛 Troubleshooting](#-troubleshooting)

## 🎯 Overview

This project implements a complete MLOps pipeline for a Titanic survival prediction model with production-grade infrastructure:

**Model Details**: Logistic Regression trained on Titanic dataset (78-82% accuracy). Predicts passenger survival based on class, sex, age, family size, fare, and embarkation port. See [MODEL_CARD.md](MODEL_CARD.md) for full details.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                      (mlops-dev namespace)                   │
│                                                              │
│  ┌──────────────┐         ┌─────────────────────────────┐  │
│  │   Client     │────────▶│   Titanic Predictor Service │  │
│  └──────────────┘         │      (ClusterIP)            │  │
│                            └──────────┬──────────────────┘  │
│                                       │                     │
│                            ┌──────────▼──────────┐         │
│                            │  Titanic Predictor  │         │
│                            │   (3 Replicas)      │         │
│                            └──────────┬──────────┘         │
│                                       │                     │
│              ┌────────────────────────┼────────────────┐   │
│              ▼                        ▼                ▼   │
│         ┌─────────┐            ┌──────────┐    ┌────────┐ │
│         │ MLflow  │            │PostgreSQL│    │ Metrics│ │
│         │ Server  │            │  (DB)    │    │(Prom.) │ │
│         └─────────┘            └──────────┘    └────────┘ │
└─────────────────────────────────────────────────────────────┘

           Docker Compose Alternative (Development)
┌─────────────────────────────────────────────────────────────┐
│  Client ──▶ NGINX (LB) ──▶ API (3 replicas) ──▶ MLflow     │
│                               │                              │
│                               ├──▶ PostgreSQL                │
│                               └──▶ Prometheus ──▶ Grafana   │
└─────────────────────────────────────────────────────────────┘
```

**Key Components**:
- **Kubernetes**: Production orchestration with 3-replica deployment
- **Docker Compose**: Development environment with NGINX load balancing
- **FastAPI**: Prediction service with health checks and metrics
- **PostgreSQL**: Persistent storage for prediction logs
- **MLflow**: ML lifecycle management (tracking, registry, artifacts)
- **Prometheus & Grafana**: Metrics collection and visualization
- **Airflow**: Workflow orchestration for training pipelines
- **GitHub Actions**: Automated CI/CD pipelines

## ✅ MLOps Capabilities

| Capability | Implementation | Status |
|------------|----------------|--------|
| **Load Balancing** | Kubernetes Service (3 replicas) + NGINX (Docker) | ✅ |
| **Orchestration** | Kubernetes + Docker Compose | ✅ |
| **CI/CD** | GitHub Actions (build, test, deploy) | ✅ |
| **Observability** | Prometheus + Grafana monitoring | ✅ |
| **Model Tracking** | MLflow (experiments, versioning, registry) | ✅ |
| **Traffic & Security** | Input validation, health checks, error handling | ✅ |
| **State & Metadata** | PostgreSQL for prediction logs | ✅ |
| **Scalability** | Horizontal scaling with resource limits | ✅ |
| **Rollback** | Kubernetes rollout undo + version tagging | ✅ |
| **Advanced Deployment** | Blue-Green & Canary strategies | ✅ |

## 🚀 Quick Start

### Docker Compose

**Start all services:**
```powershell
docker-compose up -d
```

**Access services:**
- API: http://localhost:8000
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Test the API:**
```powershell
curl http://localhost:8000/healthz
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{\"pclass\":1,\"sex\":\"female\",\"age\":29,\"sibsp\":0,\"parch\":0,\"fare\":100,\"embarked\":\"S\"}'
```

**Stop services:**
```powershell
docker-compose down
```

### Kubernetes

**Prerequisites:**
- Docker Desktop with Kubernetes enabled
- kubectl configured

**Deploy to Kubernetes:**
```powershell
cd deploy/k8s

# Create namespace and deploy all services
kubectl apply -f namespace.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f mlflow-deployment.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check deployment status
kubectl get all -n mlops-dev

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=titanic-predictor -n mlops-dev --timeout=120s
```

**Access services:**
```powershell
# Port forward to access locally
kubectl port-forward -n mlops-dev svc/titanic-predictor 8000:8000
kubectl port-forward -n mlops-dev svc/mlflow 5000:5000

# Test the service
curl http://localhost:8000/healthz
```

**Clean up:**
```powershell
kubectl delete namespace mlops-dev
```

**Quick redeploy script available:**
```powershell
cd deploy/k8s
.\redeploy.ps1
```

## 📁 Repository Structure

```
mlops_takehome_nicholas/
├── .github/workflows/          # CI/CD pipelines
│   ├── ci.yml                  # Main CI/CD workflow
│   ├── deploy-dev.yml          # Dev deployment
│   └── promote-prod.yml        # Prod promotion
│
├── airflow-data/               # Airflow metadata and logs
│   ├── dags/                   # DAG definitions
│   ├── logs/                   # Execution logs
│   └── mlruns/                 # MLflow runs from Airflow
│
├── app/                        # FastAPI application
│   ├── main.py                 # API endpoints & middleware
│   ├── model_loader.py         # Model loading (with MLflow fallback)
│   ├── model.py                # Model wrapper
│   └── db.py                   # PostgreSQL connection
│
├── artifacts/                  # Saved model artifacts
│   └── titanic-classifier/     # Model files (bundled in Docker)
│
├── dashboards/                 # Grafana dashboards
│   └── Titanic_dashboard.json  # Main monitoring dashboard
│
├── deploy/
│   ├── k8s/                    # Kubernetes manifests
│   │   ├── namespace.yaml      # Namespace definition
│   │   ├── deployment.yaml     # App deployment (3 replicas)
│   │   ├── service.yaml        # ClusterIP service
│   │   ├── postgres-deployment.yaml  # PostgreSQL
│   │   ├── mlflow-deployment.yaml    # MLflow server
│   │   ├── mlflow.Dockerfile   # Custom MLflow image
│   │   ├── redeploy.ps1        # Quick redeploy script
│   │   ├── blue-green/         # Blue-green deployment configs
│   │   └── canary/             # Canary deployment configs
│   └── monitoring/             # Prometheus & Grafana configs
│
├── mlflow/                     # MLflow server data
│   ├── artifacts/              # Model artifacts storage
│   └── mlruns/                 # Experiment runs metadata
│
├── mlruns/                     # Local MLflow runs (training)
│
├── pipelines/                  # Airflow DAG definitions
│   └── titanic_training_dag.py # Training pipeline
│
├── sql/
│   └── schema.sql              # Database schema
│
├── tests/                      # Test suite
│   ├── test_api_ci.py          # CI unit tests
│   ├── test_training_ci.py     # CI training tests
│   ├── test_api.py             # Integration tests
│   ├── test_lb.py              # Load balancer tests
│   └── test_traffic.py         # Traffic generation tests
│
├── train/
│   ├── train.py                # Standard training script
│   └── train_with_mlflow.py    # MLflow-integrated training
│
├── docker-compose.yaml         # Main orchestration
├── docker-compose.airflow.yaml # Airflow orchestration
├── Dockerfile                  # Container image
├── nginx.conf                  # NGINX load balancer config
├── requirements.txt            # Python dependencies
│
├── GrafanaDashboard.png        # Dashboard screenshot
├── MODEL_CARD.md               # Model documentation
├── ROLLBACK_PROCEDURES.md      # Detailed rollback guide
├── ROLLBACK_QUICK_REFERENCE.md # Quick rollback commands
└── README.md                   # This file
```

## 🧪 Testing

### Run All Tests

**CI Tests (no server required):**
```powershell
pytest tests/test_api_ci.py tests/test_training_ci.py -v
```

**Integration Tests (requires running services):**
```powershell
# Start services first
docker-compose up -d

# Run tests
pytest tests/test_api.py tests/test_lb.py -v

# Traffic generation test
python tests/test_traffic.py
```

### Test Coverage

| Test File | Purpose | Environment |
|-----------|---------|-------------|
| `test_api_ci.py` | API unit tests | CI/Local (no server) |
| `test_training_ci.py` | Training tests | CI/Local (no server) |
| `test_api.py` | API integration | Docker/K8s |
| `test_lb.py` | Load balancer | Docker |
| `test_traffic.py` | Traffic simulation | Docker/K8s |

## 🔄 Deployment Strategies

### Standard Deployment (Kubernetes)

```powershell
# Update deployment
kubectl apply -f deploy/k8s/deployment.yaml

# Monitor rollout
kubectl rollout status deployment/titanic-predictor -n mlops-dev

# Verify
kubectl get pods -n mlops-dev
```

### Canary Deployment

Deploy new version to 10% of traffic, gradually increase:

```powershell
cd deploy/k8s/canary

# Deploy canary (10% traffic)
kubectl apply -f deployment-stable.yaml
kubectl apply -f deployment-canary.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress-canary.yaml

# Monitor metrics, then increase traffic
kubectl patch ingress titanic-predictor-canary -n mlops-dev \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"50"}}}'

# Promote or rollback
kubectl delete deployment titanic-predictor-canary -n mlops-dev  # Rollback
kubectl apply -f deployment-stable.yaml  # Promote (update stable to canary version)
```

### Blue-Green Deployment

Zero-downtime deployment with instant switch:

```powershell
cd deploy/k8s/blue-green

# Deploy green (new version)
kubectl apply -f deployment-blue.yaml   # Current production
kubectl apply -f deployment-green.yaml  # New version

# Test green
kubectl run test-curl --rm -i --tty --image=curlimages/curl -- \
  curl http://titanic-predictor-green:8000/healthz

# Switch traffic
kubectl apply -f ingress.yaml  # Switch to green

# Rollback if needed
kubectl patch svc titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

## 📊 Monitoring & Observability

### Prometheus Metrics

Available at `/metrics` endpoint:
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `model_predictions_total` - Total predictions by model version, pod, result
- `model_prediction_duration_seconds` - Model inference latency

### Grafana Dashboard

Import dashboard from `dashboards/Titanic_dashboard.json`

**Key Panels:**
- Request rate and error rate
- Latency percentiles (p50, p95, p99)
- Prediction distribution (survived vs died)
- Pod-level metrics
- Model version tracking

**Screenshot:**

![Grafana Dashboard](GrafanaDashboard.png)

### Health Checks

```powershell
# Docker Compose
curl http://localhost:8000/healthz

# Kubernetes
kubectl exec -n mlops-dev deployment/titanic-predictor -- curl -s http://localhost:8000/healthz

# Port-forwarded
kubectl port-forward -n mlops-dev svc/titanic-predictor 8000:8000
curl http://localhost:8000/healthz
```

## 🔙 Rollback Procedures

### Quick Rollback (Kubernetes)

**Undo last deployment:**
```powershell
kubectl rollout undo deployment/titanic-predictor -n mlops-dev
```

**Rollback to specific revision:**
```powershell
# View history
kubectl rollout history deployment/titanic-predictor -n mlops-dev

# Rollback to revision 2
kubectl rollout undo deployment/titanic-predictor --to-revision=2 -n mlops-dev
```

### Blue-Green Instant Switch

```powershell
# Switch back to blue (previous version)
kubectl patch svc titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Docker Compose Rollback

```bash
# Change MODEL_VERSION in docker-compose.yaml
docker-compose restart titanic-api
```

**See [ROLLBACK_PROCEDURES.md](ROLLBACK_PROCEDURES.md) for detailed procedures and [ROLLBACK_QUICK_REFERENCE.md](ROLLBACK_QUICK_REFERENCE.md) for emergency commands.**

## 🐛 Troubleshooting

### Kubernetes Pods Not Starting

**Check pod status:**
```powershell
kubectl get pods -n mlops-dev
kubectl describe pod <pod-name> -n mlops-dev
kubectl logs -n mlops-dev <pod-name>
```

**Common issues:**
- **ImagePullBackOff**: Build Docker image locally: `docker build -t titanic-predictor:latest .`
- **CrashLoopBackOff**: Check logs, ensure MLflow and PostgreSQL are ready
- **Pending**: Check resource constraints: `kubectl describe pod <pod-name> -n mlops-dev`

### MLflow Connection Issues

**Verify MLflow is running:**
```powershell
kubectl get pods -n mlops-dev -l app=mlflow
kubectl logs -n mlops-dev -l app=mlflow

# Test connectivity
kubectl run test-curl --rm -i -n mlops-dev --image=curlimages/curl -- \
  curl -s http://mlflow:5000/health
```

**App uses fallback model** if MLflow is unavailable - check logs for warnings.

### Database Connection Issues

**Check PostgreSQL:**
```powershell
kubectl get pods -n mlops-dev -l app=postgres
kubectl logs -n mlops-dev -l app=postgres

# Test connection
kubectl exec -n mlops-dev deployment/postgres -- \
  psql -U postgres -d mlops -c "SELECT 1;"
```

### Service Not Accessible

**Check service and endpoints:**
```powershell
kubectl get svc -n mlops-dev
kubectl get endpoints -n mlops-dev

# Port forward to test locally
kubectl port-forward -n mlops-dev svc/titanic-predictor 8000:8000
```

### Clean Redeploy

**If all else fails:**
```powershell
cd deploy/k8s
.\redeploy.ps1
```

Or manually:
```powershell
kubectl delete namespace mlops-dev
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/postgres-deployment.yaml
kubectl apply -f deploy/k8s/mlflow-deployment.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

## 📄 License

MIT License - See LICENSE file for details

---

**Project Status**: ✅ Production Ready

For questions or issues, please open a GitHub issue.
