# 🎬 Video Demo Guide: Canary & Blue-Green Deployments

## 📋 Prerequisites Checklist

Before starting the video recording, ensure:

```powershell
# 1. Kubernetes cluster is running
kubectl get nodes

# 2. Namespace exists
kubectl apply -f deploy/k8s/namespace.yaml

# 3. PostgreSQL is running
kubectl get pods -n mlops-dev | Select-String postgres

# 4. Stable deployment is running (3 replicas)
kubectl get pods -n mlops-dev -l app=titanic-predictor

# 5. Local Docker images are built
docker images | Select-String titanic-predictor
# Should show: titanic-predictor:v1.0 and titanic-predictor:v2.0
```

---

## 🎥 VIDEO SECTION 1: Blue-Green Deployment (3-4 minutes)

### **[0:00] Introduction**

**Narration:**
> "Now let's demonstrate Blue-Green deployment - a strategy that maintains two identical production environments. Blue represents the current version, Green is the new release. We can switch traffic instantly with zero downtime."

### **[0:20] Step 1: Deploy Blue Environment (Current Production)**

```powershell
# Show the blue deployment file
cat deploy/k8s/blue-green/deployment-blue.yaml

# Deploy Blue (v1.0)
kubectl apply -f deploy/k8s/blue-green/deployment-blue.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l version=blue -n mlops-dev --timeout=60s

# Show running blue pods
kubectl get pods -n mlops-dev -l version=blue
```

**Expected Output:**
```
NAME                                      READY   STATUS    RESTARTS   AGE
titanic-predictor-blue-xxxxx-aaaaa        1/1     Running   0          30s
titanic-predictor-blue-xxxxx-bbbbb        1/1     Running   0          30s
titanic-predictor-blue-xxxxx-ccccc        1/1     Running   0          30s
```

**Narration:**
> "Blue environment is live with 3 replicas running version 1.0. This is our current production."

### **[1:00] Step 2: Point Service to Blue**

```powershell
# Create service pointing to Blue
kubectl apply -f deploy/k8s/blue-green/service-blue.yaml

# Verify service is pointing to blue
kubectl get svc titanic-predictor -n mlops-dev -o yaml | Select-String -Pattern "version:"
```

**Narration:**
> "The titanic-predictor service routes all traffic to Blue pods using label selectors."

### **[1:20] Step 3: Test Blue Environment**

```powershell
# Port forward to test
kubectl port-forward svc/titanic-predictor 8000:8000 -n mlops-dev

# In a new terminal - Make prediction
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
```

**Expected Output:**
```json
{
  "prediction": "survived",
  "survival_probability": 0.92,
  "latency_ms": 12.45,
  "model_version": "1.0",
  "pod_name": "titanic-predictor-blue-xxxxx"
}
```

**Narration:**
> "Requests are being served by Blue environment - notice model_version is 1.0 and pod name includes 'blue'."

### **[2:00] Step 4: Deploy Green Environment (New Version)**

```powershell
# Deploy Green (v2.0) in parallel
kubectl apply -f deploy/k8s/blue-green/deployment-green.yaml

# Wait for green pods
kubectl wait --for=condition=ready pod -l version=green -n mlops-dev --timeout=120s

# Show both environments running
kubectl get pods -n mlops-dev -l app=titanic-predictor -o wide
```

**Expected Output:**
```
NAME                                      READY   STATUS    RESTARTS   AGE
titanic-predictor-blue-xxxxx-aaaaa        1/1     Running   0          2m
titanic-predictor-blue-xxxxx-bbbbb        1/1     Running   0          2m
titanic-predictor-blue-xxxxx-ccccc        1/1     Running   0          2m
titanic-predictor-green-xxxxx-ddddd       1/1     Running   0          30s
titanic-predictor-green-xxxxx-eeeee       1/1     Running   0          30s
titanic-predictor-green-xxxxx-fffff       1/1     Running   0          30s
```

**Narration:**
> "Both Blue and Green environments are now running in parallel - 6 total pods. Green is ready but not receiving traffic yet."

### **[2:40] Step 5: Instant Traffic Switch**

```powershell
# Show current service selector
kubectl get svc titanic-predictor -n mlops-dev -o yaml | Select-String -Pattern "version:" -Context 1,1

# Switch traffic to Green (instant cutover!)
kubectl patch service titanic-predictor -n mlops-dev -p '{"spec":{"selector":{"version":"green"}}}'

# Verify the switch
kubectl get svc titanic-predictor -n mlops-dev -o yaml | Select-String -Pattern "version:" -Context 1,1
```

**Narration:**
> "With a single command, we've switched 100% of traffic from Blue to Green. This happens in under 5 seconds with zero downtime."

### **[3:00] Step 6: Verify Green is Serving**

```powershell
# Make another prediction
Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Body $body -ContentType "application/json"
```

**Expected Output:**
```json
{
  "prediction": "survived",
  "survival_probability": 0.92,
  "latency_ms": 12.45,
  "model_version": "2.0",
  "pod_name": "titanic-predictor-green-xxxxx"
}
```

**Narration:**
> "Now all requests are served by Green - notice model_version is 2.0 and pod name includes 'green'. The cutover was instant and seamless."

### **[3:20] Step 7: Rollback Demo (If Needed)**

```powershell
# If Green has issues, instant rollback to Blue
kubectl patch service titanic-predictor -n mlops-dev -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify rollback
Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -Body $body -ContentType "application/json"
```

**Narration:**
> "If we detect issues with Green, we can roll back to Blue instantly - under 5 seconds. No downtime, no risk."

### **[3:40] Cleanup**

```powershell
# After Green is stable, remove Blue to save resources
kubectl delete deployment titanic-predictor-blue -n mlops-dev

# Verify only Green is running
kubectl get pods -n mlops-dev -l app=titanic-predictor
```

**Narration:**
> "Once Green is proven stable, we decommission the Blue environment. In the next deployment, Green becomes Blue and we deploy a new Green."

---

## 🎥 VIDEO SECTION 2: Canary Deployment (2-3 minutes)

### **[0:00] Introduction**

**Narration:**
> "Canary deployment takes a more gradual approach. We start by routing a small percentage of traffic to the new version, monitor metrics, then progressively increase traffic if everything looks good."

### **[0:15] Step 1: Start with Stable Deployment**

```powershell
# Ensure stable deployment has 3 replicas
kubectl get pods -n mlops-dev -l app=titanic-predictor,version!=canary
```

**Expected Output:**
```
NAME                                 READY   STATUS    RESTARTS   AGE
titanic-predictor-xxxxx-aaaaa        1/1     Running   0          5m
titanic-predictor-xxxxx-bbbbb        1/1     Running   0          5m
titanic-predictor-xxxxx-ccccc        1/1     Running   0          5m
```

**Narration:**
> "We start with 3 pods running the stable version 1.0."

### **[0:30] Step 2: Deploy Canary (10% Traffic)**

**Note for Video:** Since we have model loading issues with the actual canary, we'll demonstrate the concept using kubectl commands and explain the traffic distribution.

```powershell
# Show canary deployment config
cat deploy/k8s/canary/deployment-canary.yaml | Select-String -Pattern "replicas:" -Context 1,1

# Deploy canary with 1 replica (1 out of 10 total pods = 10%)
kubectl apply -f deploy/k8s/canary/deployment-canary.yaml
```

**Narration (IMPORTANT - Explain even if pods don't start):**
> "We deploy 1 canary pod alongside our 3 stable pods. The Kubernetes service will distribute traffic across all 4 pods, giving the canary approximately 25% of traffic. For true 10% traffic, we would need 1 canary out of 10 total pods."

```powershell
# Show the mix of pods
kubectl get pods -n mlops-dev -l app=titanic-predictor -o wide
```

**Expected Explanation (even if canary is pending):**
```
NAME                                    READY   STATUS    VERSION
titanic-predictor-xxxxx-aaaaa          1/1     Running   stable
titanic-predictor-xxxxx-bbbbb          1/1     Running   stable
titanic-predictor-xxxxx-ccccc          1/1     Running   stable
titanic-predictor-canary-xxxxx-ddddd   0/1     Pending   canary
```

**Narration:**
> "In a production environment with working canary pods, we would generate traffic and monitor metrics in Grafana. We'd watch for error rates, latency spikes, or prediction anomalies."

### **[1:00] Step 3: Monitor Metrics (Conceptual)**

**Show Grafana Dashboard (if available) or explain:**

```powershell
# Generate test traffic (if system is working)
python tests/test_traffic.py --requests 100
```

**Narration:**
> "We would run traffic through the system and observe metrics in Grafana:
> - Request success rate by version
> - Latency percentiles (p50, p95, p99)
> - Model prediction distribution
> - Error rates
> 
> If metrics look good after a threshold period (e.g., 10 minutes), we proceed to increase canary traffic."

### **[1:30] Step 4: Scale Canary (50% Traffic)**

```powershell
# Scale canary to 3 replicas (3 canary + 3 stable = 50% traffic)
kubectl scale deployment titanic-predictor-canary --replicas=3 -n mlops-dev

# Show the 50/50 split
kubectl get pods -n mlops-dev -l app=titanic-predictor
```

**Narration:**
> "After confirming canary is healthy, we scale to 3 replicas for 50% traffic. We continue monitoring for another period."

### **[2:00] Step 5: Full Rollout (100% Traffic)**

```powershell
# Promote canary to stable by updating the main deployment
kubectl set image deployment/titanic-predictor titanic-api=titanic-predictor:v2.0 -n mlops-dev

# Remove canary deployment
kubectl delete deployment titanic-predictor-canary -n mlops-dev

# Verify all pods are v2.0
kubectl get pods -n mlops-dev -l app=titanic-predictor
```

**Narration:**
> "Once we're confident, we update the stable deployment to v2.0 and remove the canary. The canary has been promoted to production."

### **[2:20] Rollback Scenario**

```powershell
# If canary shows issues at ANY stage:
# 1. Immediate mitigation - scale canary to 0
kubectl scale deployment titanic-predictor-canary --replicas=0 -n mlops-dev

# 2. Delete canary
kubectl delete deployment titanic-predictor-canary -n mlops-dev
```

**Narration:**
> "If we detect issues at any stage, we can immediately scale the canary to zero or delete it entirely. The stable pods continue serving traffic - risk is minimized."

---

## 🎬 VIDEO SECTION 3: Comparison & Best Practices (1 minute)

### **[0:00] Strategy Comparison**

**Show side-by-side comparison graphic or table:**

| Feature | Blue-Green | Canary |
|---------|-----------|--------|
| **Traffic Shift** | Instant (100%) | Gradual (10%→50%→100%) |
| **Rollback Speed** | <5 seconds | <10 seconds |
| **Resource Usage** | 2x pods during switch | 1.1-1.5x pods during rollout |
| **Risk** | All-or-nothing | Minimal blast radius |
| **Best For** | Confident releases, simple changes | Risky changes, new features |

**Narration:**
> "Blue-Green gives you instant cutover and instant rollback - perfect when you're confident in your release.
>
> Canary minimizes risk by gradually exposing users to the new version - ideal for major changes or uncertain deployments.
>
> Both strategies enable zero-downtime deployments and fast rollbacks, which are critical for production ML systems."

### **[0:30] Production Recommendations**

**Narration:**
> "In production, combine these with:
> - Automated health checks and smoke tests
> - Real-time monitoring with alerting (Prometheus + Grafana)
> - Automated rollback triggers based on error thresholds
> - Feature flags for even more granular control
> - A/B testing frameworks to measure business impact"

---

## 📋 Post-Recording Cleanup

```powershell
# Remove all deployments
kubectl delete deployment titanic-predictor-blue -n mlops-dev
kubectl delete deployment titanic-predictor-green -n mlops-dev
kubectl delete deployment titanic-predictor-canary -n mlops-dev

# Keep the original stable deployment
kubectl get pods -n mlops-dev -l app=titanic-predictor
```

---

## 🎯 Key Messages for Video

1. **Blue-Green = Speed**: Instant traffic cutover, instant rollback, zero downtime
2. **Canary = Safety**: Gradual rollout, limited blast radius, data-driven decisions
3. **Both = Essential**: Modern MLOps requires deployment strategies that minimize risk
4. **Observability is Critical**: You must monitor metrics to make informed decisions

---

## 💡 Video Tips

1. **Screen Layout**: Split screen showing terminal + Grafana dashboard
2. **Font Size**: Terminal at 16-18pt for readability
3. **Timing**: Pause after each command to show output
4. **Narration**: Explain WHY, not just WHAT
5. **Editing**: Speed up kubectl wait commands (2x-4x)
6. **Visual Aids**: Add animations showing traffic flow
7. **Timestamps**: Include in video description for easy navigation

---

## 🚨 Troubleshooting

If pods don't start:
- Check image names: `docker images`
- Check pod logs: `kubectl logs -n mlops-dev <pod-name>`
- Describe pod: `kubectl describe pod -n mlops-dev <pod-name>`

If health checks fail:
- Verify model artifacts exist in image
- Check environment variables (DB_HOST, MLFLOW_TRACKING_URI)
- Test locally first: `docker run -p 8000:8000 titanic-predictor:v1.0`

---

## ✅ Success Criteria

By the end of the video, viewers should understand:
- ✅ How Blue-Green deployment works
- ✅ How Canary deployment works
- ✅ When to use each strategy
- ✅ How to implement both in Kubernetes
- ✅ How to rollback quickly if issues arise

Good luck with your video! 🎥🚀
