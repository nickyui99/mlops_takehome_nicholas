# Rollback Procedures - Complete Guide

This document provides detailed rollback procedures for all deployment scenarios including Docker Compose, Kubernetes, Helm, and advanced deployment strategies (canary, blue-green).

## 📋 Table of Contents

- [Docker Compose Rollback](#docker-compose-rollback)
- [Kubernetes Rollback](#kubernetes-rollback)
- [Helm Rollback](#helm-rollback)
- [Canary Deployment Rollback](#canary-deployment-rollback)
- [Blue-Green Deployment Rollback](#blue-green-deployment-rollback)
- [MLflow Model Rollback](#mlflow-model-rollback)
- [Emergency Rollback Procedures](#emergency-rollback-procedures)

---

## Docker Compose Rollback

### Method 1: Rollback to Previous Image Tag

```bash
# View available image tags
docker images ghcr.io/nickyui99/titanic-predictor

# Stop current services
docker-compose down

# Pull specific version
docker pull ghcr.io/nickyui99/titanic-predictor:sha-abc123

# Update docker-compose.yaml or use override
docker-compose up -d
```

### Method 2: Rollback Model Version Only

```bash
# Edit docker-compose.yaml - change MODEL_VERSION
# From:
#   MODEL_VERSION: "2.0"
# To:
#   MODEL_VERSION: "1.0"

# Restart services
docker-compose restart titanic-api

# Verify rollback
curl http://localhost:8000/healthz
```

### Method 3: Use Git to Rollback Configuration

```bash
# Find previous commit with working version
git log --oneline

# Reset docker-compose.yaml to previous version
git checkout <commit-hash> -- docker-compose.yaml

# Restart services
docker-compose down
docker-compose up -d
```

---

## Kubernetes Rollback

### Method 1: Rollback to Previous Revision (Simple)

```bash
# View rollout history
kubectl rollout history deployment/titanic-predictor -n mlops-dev

# Rollback to previous revision (most common)
kubectl rollout undo deployment/titanic-predictor -n mlops-dev

# Monitor rollback status
kubectl rollout status deployment/titanic-predictor -n mlops-dev

# Verify pods are running with old version
kubectl get pods -n mlops-dev -l app=titanic-predictor
kubectl describe pod <pod-name> -n mlops-dev | grep Image:
```

### Method 2: Rollback to Specific Revision

```bash
# View detailed rollout history with revisions
kubectl rollout history deployment/titanic-predictor -n mlops-dev

# Output example:
# REVISION  CHANGE-CAUSE
# 1         Initial deployment
# 2         Updated to v2.0
# 3         Updated to v3.0

# Rollback to specific revision (e.g., revision 2)
kubectl rollout undo deployment/titanic-predictor \
  --to-revision=2 \
  -n mlops-dev

# Verify rollback
kubectl rollout status deployment/titanic-predictor -n mlops-dev
```

### Method 3: Direct Image Update (Fastest)

```bash
# Update deployment to use specific image version
kubectl set image deployment/titanic-predictor \
  titanic-predictor=ghcr.io/nickyui99/titanic-predictor:sha-abc123 \
  -n mlops-dev

# Or update with model version
kubectl set env deployment/titanic-predictor \
  MODEL_VERSION=1.0 \
  -n mlops-dev

# Monitor rollback
kubectl rollout status deployment/titanic-predictor -n mlops-dev
```

### Method 4: Edit Deployment Directly

```bash
# Edit deployment manifest
kubectl edit deployment/titanic-predictor -n mlops-dev

# Change the image tag in the editor:
# spec:
#   containers:
#   - image: ghcr.io/nickyui99/titanic-predictor:sha-abc123  # Change this
#     name: titanic-predictor

# Save and exit - rollback happens automatically

# Verify
kubectl get pods -n mlops-dev -w
```

### Method 5: Apply Previous Manifest

```bash
# Keep versioned deployment files
# deploy/k8s/deployment-v1.0.yaml
# deploy/k8s/deployment-v2.0.yaml

# Rollback by applying previous manifest
kubectl apply -f deploy/k8s/deployment-v1.0.yaml -n mlops-dev

# Verify
kubectl get deployment titanic-predictor -n mlops-dev -o wide
```

---

## Helm Rollback

### Prerequisites

```bash
# Install Helm (if not already installed)
# Windows (PowerShell)
choco install kubernetes-helm

# Linux/Mac
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Method 1: Rollback to Previous Release

```bash
# View Helm release history
helm history titanic-predictor -n mlops-dev

# Output example:
# REVISION  UPDATED                   STATUS      CHART               DESCRIPTION
# 1         Mon Oct 1 12:00:00 2024   superseded  titanic-v1.0.0      Install complete
# 2         Mon Oct 15 14:30:00 2024  superseded  titanic-v2.0.0      Upgrade complete
# 3         Mon Nov 1 16:45:00 2024   deployed    titanic-v3.0.0      Upgrade complete

# Rollback to previous release (revision 2)
helm rollback titanic-predictor -n mlops-dev

# Or specify revision number
helm rollback titanic-predictor 2 -n mlops-dev

# Monitor rollback
kubectl rollout status deployment/titanic-predictor -n mlops-dev
```

### Method 2: Rollback with Custom Values

```bash
# Rollback to specific revision with value overrides
helm rollback titanic-predictor 2 \
  --set image.tag=sha-abc123 \
  --set modelVersion=1.0 \
  -n mlops-dev

# Or use values file
helm rollback titanic-predictor 2 \
  -f deploy/helm/values-production-v1.yaml \
  -n mlops-dev
```

### Method 3: Helm Upgrade to Previous Chart Version

```bash
# Upgrade to specific chart version (acts as rollback)
helm upgrade titanic-predictor ./deploy/helm/titanic-chart \
  --version 1.0.0 \
  --set image.tag=sha-abc123 \
  --set modelVersion=1.0 \
  -n mlops-dev

# Wait for rollout to complete
helm status titanic-predictor -n mlops-dev
```

### Method 4: Helm Uninstall and Reinstall (Nuclear Option)

```bash
# CAUTION: This will cause downtime

# Export current values for reference
helm get values titanic-predictor -n mlops-dev > current-values.yaml

# Uninstall current release
helm uninstall titanic-predictor -n mlops-dev

# Reinstall with previous version
helm install titanic-predictor ./deploy/helm/titanic-chart \
  --version 1.0.0 \
  -f deploy/helm/values-production-v1.yaml \
  -n mlops-dev
```

---

## Canary Deployment Rollback

### Understanding Canary Deployment

Canary deployment gradually rolls out changes to a small subset of users before rolling out to everyone.

```
┌─────────────────────────────────────┐
│  Canary Deployment (10% traffic)    │
├─────────────────────────────────────┤
│  Stable (v1.0): 90% → 9 replicas    │
│  Canary (v2.0): 10% → 1 replica     │
└─────────────────────────────────────┘
```

### Kubernetes Canary Rollback

#### Step 1: Create Canary Deployment

```yaml
# deploy/k8s/deployment-canary.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: titanic-predictor-canary
  namespace: mlops-dev
spec:
  replicas: 1  # 10% of total (if stable has 9 replicas)
  selector:
    matchLabels:
      app: titanic-predictor
      version: canary
  template:
    metadata:
      labels:
        app: titanic-predictor
        version: canary
    spec:
      containers:
      - name: titanic-predictor
        image: ghcr.io/nickyui99/titanic-predictor:v2.0  # New version
        env:
        - name: MODEL_VERSION
          value: "2.0"
```

#### Step 2: Rollback Canary (Delete Canary Deployment)

```bash
# If canary has issues, simply delete it
kubectl delete deployment titanic-predictor-canary -n mlops-dev

# Stable deployment continues serving 100% traffic
kubectl get deployments -n mlops-dev

# Verify all traffic goes to stable
kubectl get pods -n mlops-dev -l app=titanic-predictor
```

#### Step 3: Rollback Promoted Canary

If canary was already promoted to stable:

```bash
# Scale down canary
kubectl scale deployment/titanic-predictor-canary --replicas=0 -n mlops-dev

# Rollback stable deployment
kubectl rollout undo deployment/titanic-predictor -n mlops-dev

# Delete canary
kubectl delete deployment titanic-predictor-canary -n mlops-dev
```

### Helm Canary Rollback (using Flagger or Argo Rollouts)

#### Using Flagger

```bash
# Check canary status
kubectl describe canary titanic-predictor -n mlops-dev

# Abort canary if issues detected
kubectl annotate canary/titanic-predictor \
  flagger.app/abort="true" \
  -n mlops-dev

# Flagger will automatically rollback to stable

# Or manually scale down canary
kubectl scale deployment/titanic-predictor-canary --replicas=0 -n mlops-dev
```

#### Using Argo Rollouts

```bash
# View rollout status
kubectl argo rollouts get rollout titanic-predictor -n mlops-dev

# Abort canary rollout
kubectl argo rollouts abort titanic-predictor -n mlops-dev

# Undo to previous version
kubectl argo rollouts undo titanic-predictor -n mlops-dev

# Or promote if you want to go back to promoting stable
kubectl argo rollouts promote titanic-predictor -n mlops-dev
```

### NGINX Ingress Canary Rollback

```bash
# Remove canary ingress
kubectl delete ingress titanic-predictor-canary -n mlops-dev

# Or update canary ingress to route 0% traffic
kubectl patch ingress titanic-predictor-canary -n mlops-dev \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"0"}}}'

# Scale down canary deployment
kubectl scale deployment/titanic-predictor-canary --replicas=0 -n mlops-dev
```

---

## Blue-Green Deployment Rollback

### Understanding Blue-Green Deployment

Blue-Green deployment runs two identical environments. Traffic switches from blue (old) to green (new) instantly.

```
┌─────────────────────────────────────┐
│     Blue-Green Deployment           │
├─────────────────────────────────────┤
│  Blue (v1.0):  ACTIVE (3 replicas)  │
│  Green (v2.0): IDLE (3 replicas)    │
│                                     │
│  After switch:                      │
│  Blue (v1.0):  IDLE (3 replicas)    │
│  Green (v2.0): ACTIVE (3 replicas)  │
└─────────────────────────────────────┘
```

### Kubernetes Blue-Green Rollback

#### Step 1: Current State (Green is Active)

```bash
# Service currently points to green
kubectl get svc titanic-predictor -n mlops-dev -o yaml | grep selector -A 2

# Output:
# selector:
#   app: titanic-predictor
#   version: green
```

#### Step 2: Rollback to Blue

```bash
# Switch service selector back to blue
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify traffic switched
kubectl get endpoints titanic-predictor -n mlops-dev

# Test the blue environment
kubectl port-forward -n mlops-dev svc/titanic-predictor 8000:80
curl http://localhost:8000/healthz
```

#### Step 3: Full Rollback with Manifest

```bash
# deploy/k8s/service-blue.yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: titanic-predictor
  namespace: mlops-dev
spec:
  selector:
    app: titanic-predictor
    version: blue  # Switch back to blue
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
EOF

# Verify rollback
kubectl describe svc titanic-predictor -n mlops-dev
```

### Helm Blue-Green Rollback

```bash
# Rollback using Helm values
helm upgrade titanic-predictor ./deploy/helm/titanic-chart \
  --set service.selector.version=blue \
  --set green.enabled=false \
  --set blue.enabled=true \
  -n mlops-dev

# Or use values file
cat > rollback-blue-values.yaml <<EOF
service:
  selector:
    version: blue

blue:
  enabled: true
  replicas: 3
  image:
    tag: sha-abc123
  modelVersion: "1.0"

green:
  enabled: false
EOF

helm upgrade titanic-predictor ./deploy/helm/titanic-chart \
  -f rollback-blue-values.yaml \
  -n mlops-dev
```

### Istio Blue-Green Rollback

```bash
# Update VirtualService to route 100% to blue
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: titanic-predictor
  namespace: mlops-dev
spec:
  hosts:
  - titanic-predictor
  http:
  - route:
    - destination:
        host: titanic-predictor
        subset: blue
      weight: 100
    - destination:
        host: titanic-predictor
        subset: green
      weight: 0
EOF

# Verify routing
kubectl get virtualservice titanic-predictor -n mlops-dev -o yaml
```

---

## MLflow Model Rollback

### Docker Compose MLflow Rollback

```bash
# Method 1: Update environment variable
# Edit docker-compose.yaml
nano docker-compose.yaml

# Change:
# environment:
#   MODEL_VERSION: "2.0"
# To:
#   MODEL_VERSION: "1.0"

# Restart services
docker-compose restart titanic-api

# Verify version
curl http://localhost:8000/healthz | jq .model_version
```

### Kubernetes MLflow Rollback

```bash
# Update model version via environment variable
kubectl set env deployment/titanic-predictor \
  MODEL_VERSION=1.0 \
  -n mlops-dev

# Or patch deployment
kubectl patch deployment titanic-predictor -n mlops-dev \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"titanic-predictor","env":[{"name":"MODEL_VERSION","value":"1.0"}]}]}}}}'

# Monitor rollout
kubectl rollout status deployment/titanic-predictor -n mlops-dev

# Verify model version
kubectl exec -it deployment/titanic-predictor -n mlops-dev -- \
  curl http://localhost:8000/healthz
```

### MLflow Registry Rollback

```python
# Python script to rollback model in MLflow
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")
client = MlflowClient()

# Transition previous version to Production
client.transition_model_version_stage(
    name="titanic-classifier",
    version=1,  # Previous version
    stage="Production"
)

# Archive current version
client.transition_model_version_stage(
    name="titanic-classifier",
    version=2,  # Current (problematic) version
    stage="Archived"
)

print("✅ Model rolled back to version 1")
```

---

## Emergency Rollback Procedures

### 1. Immediate Rollback (< 1 minute)

```bash
# Kubernetes - fastest rollback
kubectl rollout undo deployment/titanic-predictor -n mlops-dev

# Docker Compose - restart with previous version
docker-compose down && docker-compose up -d

# Verify
curl http://localhost:8000/healthz
```

### 2. Rollback with Health Check Verification

```bash
#!/bin/bash
# emergency-rollback.sh

NAMESPACE="mlops-dev"
DEPLOYMENT="titanic-predictor"
REVISION="2"  # Known good revision

echo "🚨 Starting emergency rollback..."

# Rollback
kubectl rollout undo deployment/$DEPLOYMENT --to-revision=$REVISION -n $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=2m

# Verify health
HEALTH_CHECK=$(kubectl exec deployment/$DEPLOYMENT -n $NAMESPACE -- curl -s http://localhost:8000/healthz)

if echo $HEALTH_CHECK | grep -q "ok"; then
  echo "✅ Rollback successful and health check passed"
  exit 0
else
  echo "❌ Rollback completed but health check failed"
  exit 1
fi
```

### 3. Multi-Environment Rollback

```bash
# Rollback across all environments
for ENV in dev staging production; do
  echo "Rolling back mlops-$ENV..."
  kubectl rollout undo deployment/titanic-predictor -n mlops-$ENV
  kubectl rollout status deployment/titanic-predictor -n mlops-$ENV
done
```

### 4. Automated Rollback (GitHub Actions)

```yaml
# .github/workflows/auto-rollback.yml
name: Auto Rollback on Health Check Failure

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
    - name: Check Health
      id: health
      run: |
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/healthz)
        if [ $RESPONSE -ne 200 ]; then
          echo "health_failed=true" >> $GITHUB_OUTPUT
        fi
    
    - name: Rollback if Unhealthy
      if: steps.health.outputs.health_failed == 'true'
      run: |
        kubectl rollout undo deployment/titanic-predictor -n mlops-production
        
        # Send alert
        curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
          -d '{"text":"🚨 Auto-rollback triggered due to health check failure"}'
```

---

## Rollback Verification Checklist

After any rollback, verify:

- [ ] Health check returns 200 OK
- [ ] Model version is correct
- [ ] Predictions are working
- [ ] Metrics are being collected
- [ ] No errors in logs
- [ ] Database connections are working
- [ ] All replicas are healthy

```bash
# Quick verification script
echo "🔍 Verifying rollback..."

# Health check
curl -f http://localhost:8000/healthz || echo "❌ Health check failed"

# Model version
VERSION=$(curl -s http://localhost:8000/healthz | jq -r .model_version)
echo "Model version: $VERSION"

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"pclass":3,"sex":"female","age":25,"sibsp":0,"parch":0,"fare":7.75,"embarked":"S"}' \
  | jq .

# Check pods (Kubernetes)
kubectl get pods -n mlops-dev -l app=titanic-predictor

# Check logs for errors
kubectl logs -n mlops-dev -l app=titanic-predictor --tail=50 | grep -i error

echo "✅ Verification complete"
```

---

## Best Practices

1. **Always tag Docker images** with commit SHA or semantic version
2. **Keep at least 3 previous versions** available for rollback
3. **Document the reason for rollback** in Git commits or tickets
4. **Test rollback procedures** regularly in non-production environments
5. **Monitor metrics during rollback** to ensure success
6. **Have a rollback plan** before every deployment
7. **Use automated health checks** to trigger rollbacks
8. **Keep rollback time < 5 minutes** for production systems

---

## Summary of Rollback Commands

| Scenario | Command | Time |
|----------|---------|------|
| **K8s Previous Version** | `kubectl rollout undo deployment/titanic-predictor -n mlops-dev` | <1 min |
| **K8s Specific Revision** | `kubectl rollout undo deployment/titanic-predictor --to-revision=2 -n mlops-dev` | <1 min |
| **Helm Previous Release** | `helm rollback titanic-predictor -n mlops-dev` | <2 min |
| **Helm Specific Revision** | `helm rollback titanic-predictor 2 -n mlops-dev` | <2 min |
| **Docker Compose** | `docker-compose down && docker-compose up -d` | <30 sec |
| **Canary Abort** | `kubectl delete deployment/titanic-predictor-canary -n mlops-dev` | <10 sec |
| **Blue-Green Switch** | `kubectl patch svc titanic-predictor -n mlops-dev -p '{"spec":{"selector":{"version":"blue"}}}'` | <5 sec |
| **MLflow Model Version** | `kubectl set env deployment/titanic-predictor MODEL_VERSION=1.0 -n mlops-dev` | <1 min |

---

## Conclusion

This document provides comprehensive rollback procedures for all deployment scenarios. Always test rollback procedures in non-production environments before relying on them in production.

For questions or issues, refer to:
- [README.md](README.md) - Main project documentation
- [README_MLFLOW.md](README_MLFLOW.md) - MLflow-specific rollback
- [MLFLOW_IMPLEMENTATION.md](MLFLOW_IMPLEMENTATION.md) - Implementation details
