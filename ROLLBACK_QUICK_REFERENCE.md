# Quick Rollback Reference Card

## 🚨 Emergency Rollback (Choose One)

### Kubernetes - Standard Rollback
```bash
kubectl rollout undo deployment/titanic-predictor -n mlops-dev
```
**Time**: < 1 minute | **Risk**: Low | **Scope**: Full deployment

### Kubernetes - Specific Revision
```bash
kubectl rollout undo deployment/titanic-predictor --to-revision=2 -n mlops-dev
```
**Time**: < 1 minute | **Risk**: Low | **Scope**: Full deployment

### Helm - Rollback Release
```bash
helm rollback titanic-predictor -n mlops-dev
```
**Time**: < 2 minutes | **Risk**: Low | **Scope**: Full release

### Docker Compose - Model Version
```bash
# Edit docker-compose.yaml: MODEL_VERSION: "1.0"
docker-compose restart titanic-api
```
**Time**: < 30 seconds | **Risk**: Very Low | **Scope**: Model only

### Blue-Green - Switch Back
```bash
kubectl patch svc titanic-predictor -n mlops-dev -p '{"spec":{"selector":{"version":"blue"}}}'
```
**Time**: < 5 seconds | **Risk**: Very Low | **Scope**: Instant switch

### Canary - Abort
```bash
kubectl delete deployment/titanic-predictor-canary -n mlops-dev
```
**Time**: < 10 seconds | **Risk**: Very Low | **Scope**: Remove canary only

---

## 📋 Verification Commands

### Check Health
```bash
curl http://localhost:8000/healthz
kubectl exec deployment/titanic-predictor -n mlops-dev -- curl -s http://localhost:8000/healthz
```

### Check Version
```bash
kubectl get pods -n mlops-dev -l app=titanic-predictor -o jsonpath='{.items[0].spec.containers[0].image}'
```

### Check Model Version
```bash
curl -s http://localhost:8000/healthz | jq -r .model_version
```

### Check Rollout Status
```bash
kubectl rollout status deployment/titanic-predictor -n mlops-dev
```

### View Logs
```bash
kubectl logs -n mlops-dev -l app=titanic-predictor --tail=50
```

---

## 📞 Decision Tree

```
Issue Detected?
│
├─ Model performs poorly but app is stable?
│  └─> Use: Model Version Rollback (change MODEL_VERSION env var)
│
├─ Canary showing errors?
│  └─> Use: Canary Abort (delete canary deployment)
│
├─ Need instant rollback?
│  └─> Use: Blue-Green Switch (patch service selector)
│
├─ Full deployment has issues?
│  └─> Use: Kubernetes Rollback (kubectl rollout undo)
│
├─ Helm-managed deployment?
│  └─> Use: Helm Rollback (helm rollback)
│
└─ Docker Compose deployment?
   └─> Use: Docker Compose Restart (change config, restart)
```

---

## 🔢 Rollback by Time Constraint

| Time Available | Method | Command |
|----------------|--------|---------|
| **< 5 sec** | Blue-Green Switch | `kubectl patch svc titanic-predictor -n mlops-dev -p '{"spec":{"selector":{"version":"blue"}}}'` |
| **< 10 sec** | Canary Delete | `kubectl delete deployment/titanic-predictor-canary -n mlops-dev` |
| **< 30 sec** | Model Version | Edit docker-compose.yaml, `docker-compose restart titanic-api` |
| **< 1 min** | K8s Rollback | `kubectl rollout undo deployment/titanic-predictor -n mlops-dev` |
| **< 2 min** | Helm Rollback | `helm rollback titanic-predictor -n mlops-dev` |

---

## 📊 Risk Assessment

| Method | Downtime | Data Loss Risk | Complexity | Reversibility |
|--------|----------|----------------|------------|---------------|
| **Blue-Green** | None | None | Low | Instant |
| **Canary Abort** | None | None | Low | N/A |
| **K8s Rollback** | Minimal (~5s) | None | Low | Easy |
| **Helm Rollback** | Minimal (~10s) | None | Medium | Easy |
| **Model Version** | None | None | Low | Instant |
| **Docker Compose** | Brief (~5-10s) | None | Low | Easy |

---

## 🎯 Post-Rollback Checklist

- [ ] Health check returns 200 OK
- [ ] Correct version/revision running
- [ ] No errors in logs (check last 100 lines)
- [ ] All pods/replicas healthy
- [ ] Metrics showing normal patterns
- [ ] Database connections working
- [ ] External monitoring shows recovery
- [ ] Team notified of rollback
- [ ] Incident ticket created
- [ ] Root cause investigation scheduled

---

## 📖 Documentation References

- Full procedures: [ROLLBACK_PROCEDURES.md](ROLLBACK_PROCEDURES.md)
- Canary strategy: [deploy/k8s/canary/README.md](deploy/k8s/canary/README.md)
- Blue-Green strategy: [deploy/k8s/blue-green/README.md](deploy/k8s/blue-green/README.md)
- Main README: [README.md](README.md)

---

## 💡 Pro Tips

1. **Always verify health** after rollback
2. **Check logs immediately** for unexpected errors
3. **Monitor metrics** for 10-15 minutes post-rollback
4. **Document the incident** - what happened and why
5. **Schedule post-mortem** to prevent recurrence
6. **Keep rollback commands** in runbook or wiki
7. **Practice rollbacks** in staging regularly
8. **Set up alerts** for automatic rollback triggers

---

## 🆘 Emergency Contacts

```bash
# Get current on-call engineer
kubectl get configmap on-call-contacts -n mlops-dev -o yaml

# Send alert (example using Slack webhook)
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"🚨 Rollback executed for titanic-predictor"}'
```

---

**Keep this document accessible during incidents!**

**Last Updated**: November 15, 2025
