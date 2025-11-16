# Blue-Green Deployment Strategy

This directory contains Kubernetes manifests for blue-green deployments.

## Overview

Blue-green deployment maintains two identical environments. Traffic switches instantly between them.

```
Initial State:
- Blue (v1.0): ACTIVE - 100% traffic → 3 replicas
- Green (v2.0): IDLE - 0% traffic → 0 replicas

Deploy Green:
- Blue (v1.0): ACTIVE - 100% traffic → 3 replicas
- Green (v2.0): IDLE - 0% traffic → 3 replicas (ready)

Switch to Green:
- Blue (v1.0): IDLE - 0% traffic → 3 replicas (kept for rollback)
- Green (v2.0): ACTIVE - 100% traffic → 3 replicas

Cleanup:
- Blue (v1.0): IDLE - 0% traffic → 0 replicas (scaled down)
- Green (v2.0): ACTIVE - 100% traffic → 3 replicas
```

## Files

- `deployment-blue.yaml` - Blue deployment (current production)
- `deployment-green.yaml` - Green deployment (new version)
- `service-blue.yaml` - Service pointing to blue
- `service-green.yaml` - Service pointing to green
- `ingress.yaml` - Ingress for external access

## Deployment Steps

### 1. Initial State (Blue is Active)

```bash
# Deploy blue version
kubectl apply -f deployment-blue.yaml
kubectl apply -f service-blue.yaml
kubectl apply -f ingress.yaml

# Verify blue is serving traffic
kubectl get svc titanic-predictor -n mlops-dev -o jsonpath='{.spec.selector.version}'
# Output: blue
```

### 2. Deploy Green (New Version)

```bash
# Deploy green deployment
kubectl apply -f deployment-green.yaml

# Wait for green to be ready
kubectl rollout status deployment/titanic-predictor-green -n mlops-dev

# Test green internally (without switching traffic)
kubectl port-forward -n mlops-dev deployment/titanic-predictor-green 8001:8000
curl http://localhost:8001/healthz
```

### 3. Switch Traffic to Green

```bash
# Update service to point to green
kubectl apply -f service-green.yaml

# Verify switch (should return 'green')
kubectl get svc titanic-predictor -n mlops-dev -o jsonpath='{.spec.selector.version}'

# Test from external URL
curl https://titanic-predictor.example.com/healthz
```

### 4. Monitor Green in Production

```bash
# Watch green pods
kubectl get pods -n mlops-dev -l version=green -w

# Check logs for errors
kubectl logs -n mlops-dev -l version=green --tail=100 -f

# Monitor metrics in Grafana/Prometheus
```

### 5. Rollback to Blue (if needed)

```bash
# Switch service back to blue
kubectl apply -f service-blue.yaml

# Verify rollback (should return 'blue')
kubectl get svc titanic-predictor -n mlops-dev -o jsonpath='{.spec.selector.version}'

# Blue instantly takes over all traffic
```

### 6. Cleanup Old Version

```bash
# If green is stable, scale down blue
kubectl scale deployment/titanic-predictor-blue --replicas=0 -n mlops-dev

# Or delete blue completely
kubectl delete -f deployment-blue.yaml
```

## Quick Switch Commands

### Switch to Green

```bash
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"green"}}}'
```

### Switch to Blue (Rollback)

```bash
kubectl patch service titanic-predictor -n mlops-dev \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

## Advantages

- ✅ **Zero downtime** - Instant traffic switch
- ✅ **Easy rollback** - Switch back to blue immediately
- ✅ **Full testing** - Test green before switching
- ✅ **Low risk** - Previous version always available

## Disadvantages

- ⚠️ **Double resources** - Need capacity for both environments
- ⚠️ **Database migrations** - Need to be backward compatible
- ⚠️ **Instant switch** - All users get new version at once (no gradual rollout)

## Best Practices

1. **Always test green** before switching traffic
2. **Keep blue running** for at least 1 hour after switch
3. **Monitor metrics** closely after switch
4. **Have rollback ready** - Single command to switch back
5. **Database compatibility** - Ensure migrations work for both versions
6. **Health checks** - Verify green is healthy before switching
