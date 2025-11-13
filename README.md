# MLOps Take-Home: Iris Classifier

Production-ready ML system demonstrating end-to-end MLOps practices: reproducible training, experiment tracking, containerized serving, Kubernetes deployment, and observability.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Training Pipeline](#training-pipeline)
- [Model Serving](#model-serving)
- [Deployment](#deployment)
- [Monitoring & Observability](#monitoring--observability)
- [CI/CD](#cicd)
- [Testing](#testing)

## 🎯 Overview

This project implements a complete MLOps pipeline for an Iris flower classification model, including:

✅ **Reproducible Training** with MLflow experiment tracking  
✅ **FastAPI REST API** with Prometheus metrics & structured logging  
✅ **Kubernetes Deployment** with 3-replica high availability  
✅ **PostgreSQL Database** for prediction logging  
✅ **Prometheus + Grafana** monitoring stack  
✅ **CI/CD Pipelines** with GitHub Actions  
✅ **Airflow DAG** for workflow orchestration  
✅ **Docker & Docker Compose** for local development  

**Model Details**: Logistic Regression trained on Iris dataset (96%+ accuracy). See [MODEL_CARD.md](MODEL_CARD.md) for full details.

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│   Client    │───▶│  Kubernetes  │───▶│   FastAPI     │
│             │    │   Service    │    │   (3 pods)    │
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
│   └── iris_training_dag.py # Airflow DAG
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml              # Lint, test, build, push
│   ├── deploy-dev.yml      # Deploy to dev cluster
│   └── promote-prod.yml    # Promote to production
├── artifacts/               # Saved model artifacts
├── dashboards/              # Grafana dashboards (JSON)
├── sql/                     # Database schemas
├── Dockerfile               # Container image
├── docker-compose.yaml      # Multi-service orchestration
├── docker-compose.airflow.yaml  # Airflow setup (Docker)
├── requirements.txt         # Python dependencies
├── AIRFLOW_SETUP.md         # Airflow documentation
└── MODEL_CARD.md            # Model documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- (Optional) Kubernetes cluster (kind/minikube for local)
- **Windows Users**: Docker Desktop with WSL2 backend for Airflow support

### ⚙️ Configuration (.env)
Create a `.env` file in the project root to override defaults as needed. The app has safe defaults and will work with Docker Compose out of the box.

```env
# Database (matches docker compose postgres service)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=mlops
DB_USER=postgres
DB_PASSWORD=postgres

# Model loading
# By default the server loads the local artifact bundle saved by the trainer
MODEL_URI=artifacts/iris-classifier
MODEL_NAME=iris-classifier
MODEL_VERSION=1

# MLflow tracking (optional for local dev)
# For simple local runs, you can leave this out. The trainer saves to artifacts/.
# If you run an MLflow server, set your client(s) to point at it instead.
# Example server: mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root file:./mlruns
# MLFLOW_TRACKING_URI=http://localhost:5000
```

### Local Development

> Compose topology: NGINX acts as a reverse proxy on port 8000 (host) → forwards to `iris-api:8000` (app). Hitting http://localhost:8000 will go through NGINX.

**1. Clone and install dependencies:**
```bash
git clone https://github.com/nickyui99/mlops_takehome_nicholas.git
cd mlops_takehome_nicholas
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**2. Train the model:**
```bash
python train/train.py
```
Output:
```
✅ Training successful!
   Run ID: abc123...
   Accuracy: 0.9667
   Local model saved to: artifacts/iris-classifier/
```

**3. Start API with Docker Compose:**
```bash
docker compose up --build
```

**4. Test the API:**

**PowerShell:**
```powershell
# Health check
curl http://localhost:8000/healthz

# Make prediction
$body = @{
    sepal_length=5.1
    sepal_width=3.5
    petal_length=1.4
    petal_width=0.2
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Body $body -ContentType "application/json"
```

**Bash/Linux:**
```bash
# Health check
curl http://localhost:8000/healthz

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

Response:
```json
{
  "prediction": "setosa",
  "latency_ms": 12.34,
  "model_version": "v2025xxxx_xxxxxx",
  "pod_name": "local-dev"
}
```

## 🔬 Training Pipeline

### Overview
Training script uses MLflow for experiment tracking and model versioning.

**Training script:** `train/train.py`

**Key features:**
- Loads Iris dataset from scikit-learn (deterministic, versioned by sklearn package)
- Trains Logistic Regression with fixed random seed (42)
- Logs hyperparameters: `test_size`, `random_state`, `max_iter`
- Logs metrics: `accuracy`
- Saves model artifacts to `artifacts/iris-classifier/`
- Tracks experiments in SQLite backend (`mlflow.db`)

### Manual Training
```bash
python train/train.py
```

### Automated Training (Airflow)

**⚠️ Windows Users**: Airflow doesn't support native Windows installation. Use Docker instead (see below).

**Using Docker (Recommended for Windows):**
```bash
# Start Airflow containers
cd mlops_takehome_nicholas
docker compose -f docker-compose.airflow.yaml up -d

# Wait ~30 seconds for initialization, then access Web UI
# Open: http://localhost:8080
# Login: admin / admin

# Trigger DAG via CLI
docker exec airflow-webserver airflow dags trigger iris_training_pipeline

# Check DAG status
docker exec airflow-webserver airflow dags list-runs -d iris_training_pipeline

# View logs for debugging
docker logs airflow-scheduler --tail 50

# Stop Airflow
docker compose -f docker-compose.airflow.yaml down
```

**Known Issue & Fix**: Airflow 2.10.x has a RecursionError in log processing with verbose MLflow output. This has been fixed by:
- Suppressing MLflow logging to CRITICAL level
- Isolating training tasks in subprocesses to prevent log overflow
- See [AIRFLOW_ISSUE_ANALYSIS.md](AIRFLOW_ISSUE_ANALYSIS.md) for technical details

**Using Native Airflow (Linux/Mac/WSL only):**
```bash
# Initialize Airflow
export AIRFLOW_HOME=~/airflow
airflow db init

# Start services
airflow webserver --port 8080 &
airflow scheduler &

# Trigger DAG
airflow dags trigger iris_training_pipeline
```

**DAG Steps:**
1. **Fetch Data**: Load Iris dataset
2. **Train Model**: Execute training with MLflow logging
3. **Evaluate**: Validate accuracy > 90%
4. **Register**: Promote model if validation passes

**📖 Detailed Setup**: See [AIRFLOW_SETUP.md](AIRFLOW_SETUP.md) for complete instructions, troubleshooting, and CLI reference.

### Model Versioning & Tracking
- **Artifacts (default path)**: Portable model saved to `artifacts/iris-classifier/` and loaded by the API. This works without running an MLflow server.
- **MLflow Tracking**: Local runs log to a SQLite DB (`mlflow.db`).
- **Registry (optional)**: To use the MLflow Model Registry, run an MLflow tracking server and point both training and serving to it.

**Start MLflow UI:**
```bash
# For local development (localhost only)
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# For network access
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000 --app-name basic-auth
```

Then access MLflow at http://localhost:5000

Then set your client(s) accordingly (PowerShell):

  ```powershell
  $env:MLFLOW_TRACKING_URI="http://localhost:5000"
  ```

- **Run ID**: Unique identifier for reproducibility
- **Data Version**: Tracked via sklearn package version in `requirements.txt`

## 🌐 Model Serving

### API Endpoints

#### `POST /predict`
Predict iris species from flower measurements.

**Request:**
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

**Response:**
```json
{
  "prediction": "setosa",
  "latency_ms": 12.34,
  "model_version": "v2025xxxx_xxxxxx",
  "pod_name": "local-dev"
}
```

#### `GET /healthz`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "model_version": "v2025xxxx_xxxxxx"
}
```

#### `GET /metrics`
Prometheus metrics for monitoring.

**Metrics exposed:**
- `http_requests_total` - Total request count by endpoint & status
- `http_request_duration_seconds` - Request latency histogram

### Features
- **Input Validation**: Pydantic models enforce schema
- **Structured Logging**: JSON logs with request IDs
- **Database Logging**: All predictions saved to PostgreSQL
- **Prometheus Metrics**: Custom counters & histograms
- **Error Handling**: Graceful degradation with proper status codes

## 🚢 Deployment

### Docker Deployment

**Build image:**
```bash
docker build -t iris-predictor:latest .
```

**Note**: Ensure `.dockerignore` excludes development files like `airflow-data/`, `tests/`, `dashboards/` to prevent build errors.

**Run with Docker Compose (recommended - includes PostgreSQL):**
```bash
docker-compose up -d
```

**Run standalone container (requires external PostgreSQL):**
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/mlops \
  iris-predictor:latest
```

**Note**: Port 8000 is used by the docker-compose nginx load balancer. To avoid conflicts, stop docker-compose before running standalone containers.

### Kubernetes Deployment

**Prerequisites:**
- Kubernetes cluster (Docker Desktop/kind/minikube/GKE/EKS/AKS)
- kubectl configured

**Enable Kubernetes in Docker Desktop:**
1. Open Docker Desktop Settings
2. Navigate to Kubernetes tab
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for Kubernetes to start (green indicator)

**Deploy full stack:**
```bash
# Create namespace
kubectl apply -f deploy/k8s/namespace.yaml

# Deploy PostgreSQL (using Helm)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql -n mlops-dev \
  --set auth.postgresPassword=postgres,auth.database=mlops

# Deploy application
kubectl apply -f deploy/k8s/

# Verify deployment
kubectl get pods -n mlops-dev
kubectl get svc -n mlops-dev
```

**Configuration:**
- **Replicas**: 3 pods for high availability
- **Resources**: 128Mi-256Mi memory, 100m-200m CPU
- **Health checks**: Liveness & readiness probes on `/healthz`
- **Load balancing**: Round-robin across pods

**Access the service:**
```bash
# Port forward
kubectl port-forward svc/iris-predictor-svc 8000:8000 -n mlops-dev

# Test
curl http://localhost:8000/healthz
```

> Ingress: To expose via Ingress, ensure an Ingress Controller (e.g., NGINX Ingress) is installed.

```bash
# Install NGINX Ingress Controller (example)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace

# Apply ingress
kubectl apply -f deploy/k8s/ingress.yaml
```

### Monitoring Stack

**Deploy Prometheus & Grafana:**
```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  -n mlops-dev -f deploy/monitoring/prometheus-values.yaml

# Install Grafana
helm install grafana grafana/grafana \
  -n mlops-dev -f deploy/monitoring/grafana-values.yaml

# Get Grafana password
kubectl get secret grafana -n mlops-dev -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward Grafana
kubectl port-forward svc/grafana 3000:80 -n mlops-dev
```

**Import dashboard:**
- Open http://localhost:3000
- Login with `admin` / (password from above)
- Import `dashboards/iris-dashboard.json`

## 📊 Monitoring & Observability

### Metrics Collection
- **Prometheus** scrapes `/metrics` endpoint every 15s
- **Custom metrics** tracked:
  - `http_requests_total` - Request counter by endpoint & status
  - `http_request_duration_seconds` - Latency histogram

### Alerting
Configured alerts in `deploy/monitoring/prometheus-values.yaml`:
- **HighErrorRate**: Triggers when error rate > 5% for 1 minute

### Logging
- **Structured JSON logs** to stdout
- Each request logged with:
  - `request_id` (UUID)
  - `model_version`
  - `pod_name` (for debugging in K8s)
  - `latency_ms`
  - `input` & `prediction`

**View logs:**
```bash
# Docker Compose
docker compose logs -f iris-api

# Kubernetes
kubectl logs -f deployment/iris-predictor -n mlops-dev
```

### Database Tracking
All predictions stored in PostgreSQL:
```sql
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;
```

Schema includes: `request_id`, `model_version`, `latency_ms`, `input_data`, `prediction`, `timestamp`

## 🔄 CI/CD

### GitHub Actions Workflows

#### **1. CI Pipeline** (`.github/workflows/ci.yml`)
Triggers on: `push`, `pull_request` to `main`

**Steps:**
1. Lint code with `ruff`
2. Run unit tests with `pytest`
3. Build Docker image
4. Push image to GitHub Container Registry (GHCR)

CI to GHCR notes:
- Ensure the workflow has `permissions: packages: write`.
- Login to GHCR before pushing, e.g.:

```yaml
- name: Login to GHCR
  run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
```

#### **2. Deploy to Dev** (`.github/workflows/deploy-dev.yml`)
Triggers on: `push` to `main`

**Steps:**
1. Set up Kind cluster
2. Deploy PostgreSQL via Helm
3. Apply Kubernetes manifests
4. Run smoke tests

#### **3. Promote to Prod** (`.github/workflows/promote-prod.yml`)
Triggers: Manual (`workflow_dispatch`)

**Steps:**
1. Deploy to production cluster
2. Run post-deployment health checks

### Secrets Management
Required GitHub secrets:
- `GITHUB_TOKEN` (automatic)

For production:
- Use Kubernetes secrets for DB credentials
- Mount secrets as environment variables
- Never commit credentials to repo

## 🧪 Testing

### Run Tests Locally
```bash
# Unit tests
pytest tests/test_api.py -v

# Load balancer test (requires running service)
python tests/test_lb.py
```

### Test Coverage
- **API Tests**: Validate `/predict` and `/healthz` endpoints
- **Model Loading**: Verify model loads correctly
- **Input Validation**: Test Pydantic schema enforcement
- **Load Balancing**: Verify requests distribute across pods

### Load Balancer Test

`tests/test_lb.py` is designed to demonstrate distribution across multiple replicas. Run it after deploying to Kubernetes with 3 replicas (as defined in `deploy/k8s/deployment.yaml`) or after setting up a load-balanced multi-replica environment. In plain Docker Compose with a single `iris-api` instance, all responses will show the same `pod_name`.

## ✅ Reproducibility Checklist

- [x] **Code versioned**: Git repository with commit history
- [x] **Environment captured**: `requirements.txt` + `Dockerfile`
- [x] **Data versioned**: Iris dataset versioned via sklearn package (pinned in requirements)
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

**Built with**: Python, FastAPI, MLflow, scikit-learn, Docker, Kubernetes, Prometheus, Grafana, PostgreSQL, Airflow