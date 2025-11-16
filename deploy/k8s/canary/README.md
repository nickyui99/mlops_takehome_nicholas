# Canary Deployment Strategy

This directory contains Kubernetes manifests for canary deployments.

## Overview

Canary deployment gradually rolls out changes to a small percentage of users before full rollout.

```
Initial State:
- Stable (v1.0): 100% traffic → 3 replicas

Canary State:
- Stable (v1.0): 90% traffic → 9 replicas
- Canary (v2.0): 10% traffic → 1 replica

Full Rollout:
- New Stable (v2.0): 100% traffic → 3 replicas
```

## Files

- `deployment-stable.yaml` - Stable/production deployment
- `deployment-canary.yaml` - Canary deployment with new version
- `service.yaml` - Service routing to both stable and canary
- `ingress-canary.yaml` - NGINX Ingress with canary annotations

## Deployment Steps

### 1. Deploy Stable Version

```bash
kubectl apply -f deployment-stable.yaml
kubectl apply -f service.yaml
```

### 2. Deploy Canary (10% traffic)

```bash
kubectl apply -f deployment-canary.yaml
kubectl apply -f ingress-canary.yaml
```

### 3. Monitor Canary

```bash
# Watch pod status
kubectl get pods -n mlops-dev -l version=canary -w

# Check metrics in Prometheus/Grafana
# Compare error rates between stable and canary

# View logs
kubectl logs -n mlops-dev -l version=canary --tail=100 -f
```

### 4. Promote or Rollback

**Promote canary to stable:**
```bash
# Update stable deployment to use canary image
kubectl set image deployment/titanic-predictor-stable \
  titanic-predictor=ghcr.io/nickyui99/titanic-predictor:v2.0 \
  -n mlops-dev

# Delete canary deployment
kubectl delete -f deployment-canary.yaml
kubectl delete -f ingress-canary.yaml
```

**Rollback canary:**
```bash
# Delete canary deployment
kubectl delete -f deployment-canary.yaml
kubectl delete -f ingress-canary.yaml

# Stable continues serving 100% traffic
```

## Gradual Rollout

To increase canary traffic gradually:

```bash
# 10% traffic
kubectl patch ingress titanic-predictor-canary -n mlops-dev \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"10"}}}'

# Wait and monitor...

# 25% traffic
kubectl patch ingress titanic-predictor-canary -n mlops-dev \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"25"}}}'

# Wait and monitor...

# 50% traffic
kubectl patch ingress titanic-predictor-canary -n mlops-dev \
  -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"50"}}}'

# If all good, promote to 100%
```
