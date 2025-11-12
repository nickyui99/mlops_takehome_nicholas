# 🧪 End-to-End Testing Guide

This guide walks you through testing the entire MLOps pipeline from a fresh setup to full deployment.

## 📋 Testing Checklist

- [ ] Fresh environment setup
- [ ] Model training
- [ ] Local API testing
- [ ] Docker build & run
- [ ] Docker Compose multi-service
- [ ] Unit tests
- [ ] Kubernetes deployment
- [ ] Monitoring stack
- [ ] CI/CD validation

---

## 🎯 Testing Flow Overview

```
Fresh Setup → Train Model → Local API → Docker → K8s → Monitoring → CI/CD
     ↓            ↓            ↓          ↓       ↓         ↓         ↓
   (5 min)    (2 min)      (3 min)   (5 min) (10 min)  (5 min)   (3 min)
```

**Total Time**: ~35-40 minutes for complete validation

---

## Phase 1: Fresh Environment Setup (5 min)

### Prerequisites Check
```powershell
# Verify installations
python --version          # Should be 3.10+
docker --version          # Should be 20.10+
docker-compose --version  # Should be 2.0+
kubectl version --client  # Optional for K8s testing
git --version            # For version control
```

### Clean Environment Setup

**Step 1: Clean previous artifacts (if any)**
```powershell
# Remove old virtual environment
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }

# Remove old MLflow database (optional - for truly fresh start)
if (Test-Path mlflow.db) { Remove-Item mlflow.db }

# Remove old artifacts (optional)
if (Test-Path artifacts) { Remove-Item -Recurse -Force artifacts }
```

**Step 2: Create fresh virtual environment**
```powershell
# Create new virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\activate

# Verify activation (should show .venv in path)
python -c "import sys; print(sys.prefix)"
```

**Step 3: Install dependencies**
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify key packages
pip list | Select-String "fastapi|mlflow|scikit-learn"
```

**Expected Output:**
```
fastapi        0.xxx
mlflow         3.6.x
scikit-learn   1.x.x
```

✅ **Checkpoint**: Virtual environment ready with all dependencies

---

## Phase 2: Model Training (2 min)

### Train Model with MLflow

**Step 1: Run training script**
```powershell
python train/train.py
```

**Expected Output:**
```
✅ Training successful!
   Run ID: abc123def456...
   Accuracy: 0.9667
   Local model saved to: c:\...\artifacts\iris-classifier
```

**Step 2: Verify artifacts**
```powershell
# Check MLflow database created
Test-Path mlflow.db  # Should return True

# Check artifacts directory
Test-Path artifacts/iris-classifier  # Should return True

# List artifact contents
Get-ChildItem artifacts/iris-classifier
```

**Expected Files:**
```
conda.yaml
MLmodel
model.pkl
python_env.yaml
requirements.txt
```

**Step 3: Verify MLflow tracking**
```powershell
# Start MLflow UI (optional)
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Open browser to http://localhost:5000
# Should see experiment "iris-experiment" with 1 run
# Stop with Ctrl+C when done
```

✅ **Checkpoint**: Model trained and artifacts saved

---

## Phase 3: Local API Testing (3 min)

### Start FastAPI Server

**Step 1: Start the API**
```powershell
# Start server
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
✅ Model loaded. Version: iris-v1
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Step 2: Test health endpoint (in new terminal)**
```powershell
# Activate venv in new terminal
.\.venv\Scripts\activate

# Test health check
curl http://localhost:8000/healthz
```

**Expected Response:**
```json
{"status":"ok","model_version":"iris-v1"}
```

**Step 3: Test prediction endpoint**
```powershell
# Test with setosa sample
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

**Expected Response:**
```json
{
  "prediction": "setosa",
  "latency_ms": 12.34,
  "model_version": "iris-v1"
}
```

**Step 4: Test all three species**
```powershell
# Setosa
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'

# Versicolor
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"sepal_length":6.0,"sepal_width":2.7,"petal_length":5.1,"petal_width":1.6}'

# Virginica
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"sepal_length":7.2,"sepal_width":3.0,"petal_length":5.8,"petal_width":1.6}'
```

**Step 5: Check Prometheus metrics**
```powershell
curl http://localhost:8000/metrics
```

**Expected Output (excerpt):**
```
# HELP http_requests_total Total HTTP Requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/predict",method="POST",status="200"} 3.0
...
```

**Step 6: Stop the server**
```
Press Ctrl+C in the uvicorn terminal
```

✅ **Checkpoint**: API works locally

---

## Phase 4: Docker Testing (5 min)

### Build and Test Docker Image

**Step 1: Build Docker image**
```powershell
docker build -t iris-predictor:test .
```

**Expected Output (last line):**
```
Successfully tagged iris-predictor:test
```

**Step 2: Verify image created**
```powershell
docker images | Select-String iris-predictor
```

**Expected Output:**
```
iris-predictor   test   abc123def   X minutes ago   XXX MB
```

**Step 3: Run container**
```powershell
docker run -d -p 8000:8000 --name iris-test iris-predictor:test
```

**Step 4: Check container logs**
```powershell
docker logs iris-test
```

**Expected Output:**
```
INFO:     Started server process [1]
✅ Model loaded. Version: iris-v1
INFO:     Application startup complete.
```

**Step 5: Test containerized API**
```powershell
# Wait 5 seconds for startup
Start-Sleep -Seconds 5

# Test health
curl http://localhost:8000/healthz

# Test prediction
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

**Step 6: Cleanup**
```powershell
docker stop iris-test
docker rm iris-test
```

✅ **Checkpoint**: Docker container works

---

## Phase 5: Docker Compose Testing (5 min)

### Multi-Service Stack

**Step 1: Start full stack**
```powershell
docker-compose up -d
```

**Expected Output:**
```
Creating network "mlops_takehome_nicholas_default"
Creating mlops_takehome_nicholas_postgres_1 ... done
Creating mlops_takehome_nicholas_iris-api_1 ... done
```

**Step 2: Check services status**
```powershell
docker-compose ps
```

**Expected Output:**
```
NAME                                      STATE    PORTS
mlops_takehome_nicholas_postgres_1        Up       0.0.0.0:5432->5432/tcp
mlops_takehome_nicholas_iris-api_1        Up       0.0.0.0:8000->8000/tcp
```

**Step 3: Check API logs**
```powershell
docker-compose logs iris-api
```

**Step 4: Test API with database**
```powershell
# Wait for services to be ready
Start-Sleep -Seconds 10

# Make prediction (will be logged to PostgreSQL)
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

**Step 5: Verify database logging**
```powershell
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d mlops

# Run query (in psql)
# SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 5;

# Exit psql
# \q
```

**Expected**: You should see your prediction logged in the database

**Step 6: Cleanup**
```powershell
docker-compose down
```

✅ **Checkpoint**: Full stack works with database integration

---

## Phase 6: Unit Tests (3 min)

### Run Test Suite

**Step 1: Ensure API is running**
```powershell
# Start API if not running
uvicorn app.main:app --port 8000 &
```

**Step 2: Run pytest**
```powershell
pytest tests/test_api.py -v
```

**Expected Output:**
```
tests/test_api.py::test_root PASSED
tests/test_api.py::test_predict PASSED
tests/test_api.py::test_invalid_input PASSED
...
==================== X passed in X.XXs ====================
```

**Step 3: Test load balancing (optional)**
```powershell
# Only if running in K8s with multiple replicas
python tests/test_lb.py
```

✅ **Checkpoint**: Tests pass

---

## Phase 7: Kubernetes Deployment (10 min)

### Deploy to Local K8s Cluster

**Prerequisites:**
```powershell
# Start kind/minikube cluster
kind create cluster --name mlops-test
# OR
minikube start
```

**Step 1: Create namespace**
```powershell
kubectl apply -f deploy/k8s/namespace.yaml
```

**Expected Output:**
```
namespace/mlops-dev created
```

**Step 2: Deploy PostgreSQL via Helm**
```powershell
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install PostgreSQL
helm install postgres bitnami/postgresql `
  -n mlops-dev `
  --set auth.postgresPassword=postgres `
  --set auth.database=mlops
```

**Step 3: Load Docker image to cluster (kind)**
```powershell
# Build image first if not done
docker build -t iris-predictor:latest .

# Load to kind
kind load docker-image iris-predictor:latest --name mlops-test
```

**Step 4: Deploy application**
```powershell
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

**Step 5: Verify deployment**
```powershell
# Check pods
kubectl get pods -n mlops-dev

# Wait for pods to be ready (should see 3 pods)
kubectl wait --for=condition=ready pod -l app=iris-predictor -n mlops-dev --timeout=120s
```

**Expected Output:**
```
NAME                              READY   STATUS    RESTARTS   AGE
iris-predictor-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
iris-predictor-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
iris-predictor-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

**Step 6: Test service**
```powershell
# Port forward
kubectl port-forward svc/iris-predictor-svc 8000:80 -n mlops-dev

# In new terminal, test
curl http://localhost:8000/healthz
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

**Step 7: Test load balancing**
```powershell
# Run multiple requests
python tests/test_lb.py
```

**Expected Output:**
```
Request 1 → Pod: iris-predictor-xxxxxxxxxx-xxxxx
Request 2 → Pod: iris-predictor-xxxxxxxxxx-yyyyy
Request 3 → Pod: iris-predictor-xxxxxxxxxx-zzzzz
...
```

Should see traffic distributed across 3 different pods.

✅ **Checkpoint**: K8s deployment successful with load balancing

---

## Phase 8: Monitoring Stack (5 min)

### Deploy Prometheus & Grafana

**Step 1: Add Helm repos**
```powershell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

**Step 2: Install Prometheus**
```powershell
helm install prometheus prometheus-community/prometheus `
  -n mlops-dev `
  -f deploy/monitoring/prometheus-values.yaml
```

**Step 3: Install Grafana**
```powershell
helm install grafana grafana/grafana `
  -n mlops-dev `
  -f deploy/monitoring/grafana-values.yaml
```

**Step 4: Get Grafana password**
```powershell
kubectl get secret grafana -n mlops-dev -o jsonpath="{.data.admin-password}" | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
```

**Step 5: Access Grafana**
```powershell
kubectl port-forward svc/grafana 3000:80 -n mlops-dev
```

Open: http://localhost:3000
- Username: `admin`
- Password: (from step 4)

**Step 6: Import dashboard**
1. Click "+" → "Import"
2. Upload `dashboards/iris-dashboard.json`
3. Select Prometheus data source
4. Click "Import"

**Step 7: Generate metrics**
```powershell
# Make some predictions to generate data
for ($i=1; $i -le 20; $i++) {
    curl -X POST http://localhost:8000/predict `
      -H "Content-Type: application/json" `
      -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
    Start-Sleep -Milliseconds 500
}
```

**Step 8: Verify metrics in Grafana**
- Should see request rate increasing
- Should see latency metrics
- Should see predictions per model version

✅ **Checkpoint**: Monitoring stack operational

---

## Phase 9: CI/CD Validation (3 min)

### Verify GitHub Actions

**Step 1: Check workflow files**
```powershell
Get-ChildItem .github/workflows
```

**Expected Files:**
```
ci.yml
deploy-dev.yml
promote-prod.yml
```

**Step 2: Lint check locally**
```powershell
pip install ruff
ruff check .
```

**Expected Output:**
```
All checks passed!
```

**Step 3: Commit and push**
```powershell
git add .
git commit -m "test: complete end-to-end validation"
git push origin main
```

**Step 4: Monitor GitHub Actions**
1. Go to: https://github.com/nickyui99/mlops_takehome_nicholas/actions
2. Watch CI pipeline run
3. Verify all steps pass:
   - ✅ Lint
   - ✅ Tests
   - ✅ Docker build
   - ✅ Push to GHCR

✅ **Checkpoint**: CI/CD pipeline validated

---

## 🎉 Complete Testing Checklist

After completing all phases, verify:

```
✅ Phase 1: Fresh environment setup
✅ Phase 2: Model training with MLflow
✅ Phase 3: Local API working
✅ Phase 4: Docker container working
✅ Phase 5: Docker Compose stack working
✅ Phase 6: Unit tests passing
✅ Phase 7: Kubernetes deployment working
✅ Phase 8: Monitoring stack operational
✅ Phase 9: CI/CD pipeline validated
```

---

## 🧹 Cleanup After Testing

### Stop All Services

**Stop Docker Compose:**
```powershell
docker-compose down -v
```

**Stop Kubernetes:**
```powershell
# Delete namespace (removes everything)
kubectl delete namespace mlops-dev

# Delete cluster (optional)
kind delete cluster --name mlops-test
# OR
minikube delete
```

**Clean Docker:**
```powershell
# Remove images
docker rmi iris-predictor:test
docker rmi iris-predictor:latest

# Prune unused resources
docker system prune -f
```

**Deactivate virtual environment:**
```powershell
deactivate
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Port Already in Use
```
Error: Port 8000 already in use
```

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F
```

### Issue 2: MLflow Database Locked
```
Error: database is locked
```

**Solution:**
```powershell
# Stop all processes using MLflow
# Delete and recreate database
Remove-Item mlflow.db
python train/train.py
```

### Issue 3: Docker Build Fails
```
Error: failed to solve with frontend dockerfile.v0
```

**Solution:**
```powershell
# Check Docker daemon is running
docker ps

# Try building with no cache
docker build --no-cache -t iris-predictor:test .
```

### Issue 4: Kubernetes Pods Not Starting
```
Error: ImagePullBackOff or CrashLoopBackOff
```

**Solution:**
```powershell
# Check pod logs
kubectl logs <pod-name> -n mlops-dev

# Describe pod for events
kubectl describe pod <pod-name> -n mlops-dev

# For kind, ensure image is loaded
kind load docker-image iris-predictor:latest --name mlops-test
```

### Issue 5: Python Package Conflicts
```
Error: pip dependency resolver conflict
```

**Solution:**
```powershell
# Create fresh venv
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📊 Testing Report Template

After completing all tests, document your results:

```markdown
## Testing Report

**Date**: YYYY-MM-DD
**Tester**: Your Name
**Environment**: Windows 11, Python 3.10, Docker 24.x

### Results Summary
- ✅ Phase 1: Setup (5 min)
- ✅ Phase 2: Training (2 min)
- ✅ Phase 3: Local API (3 min)
- ✅ Phase 4: Docker (5 min)
- ✅ Phase 5: Docker Compose (5 min)
- ✅ Phase 6: Tests (3 min)
- ✅ Phase 7: Kubernetes (10 min)
- ✅ Phase 8: Monitoring (5 min)
- ✅ Phase 9: CI/CD (3 min)

**Total Time**: 41 minutes
**Overall Status**: ✅ PASS

### Notes
- All tests completed successfully
- No critical issues found
- Minor issue: [describe any issues]

### Recommendations
- Ready for demonstration
- Ready for production deployment with proper secrets management
```

---

## 🚀 Quick Re-test Flow (After Initial Setup)

For subsequent testing runs:

```powershell
# 1. Train model (if needed)
python train/train.py

# 2. Test locally
uvicorn app.main:app --port 8000
# Test in browser or with curl

# 3. Test Docker
docker-compose up -d
# Make requests
docker-compose down

# 4. Test K8s (if cluster exists)
kubectl delete namespace mlops-dev
kubectl apply -f deploy/k8s/namespace.yaml
# ... deploy steps ...

# 5. Run tests
pytest tests/ -v
```

**Total time for re-test**: ~15 minutes

---

**End of Testing Guide**
