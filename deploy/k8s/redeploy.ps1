# Script to clean up and redeploy Kubernetes resources

Write-Host "Step 1: Deleting all resources in mlops-dev namespace..." -ForegroundColor Cyan
kubectl delete all --all -n mlops-dev --force --grace-period=0 2>$null
kubectl delete pvc --all -n mlops-dev --force --grace-period=0 2>$null

Write-Host "Step 2: Waiting for resources to be deleted..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "Step 3: Deleting namespace..." -ForegroundColor Cyan
kubectl delete namespace mlops-dev --force --grace-period=0 2>$null

Write-Host "Step 4: Force removing finalizers if stuck..." -ForegroundColor Cyan
kubectl patch namespace mlops-dev -p '{\"metadata\":{\"finalizers\":[]}}' --type=merge 2>$null

Write-Host "Step 5: Waiting for namespace deletion..." -ForegroundColor Cyan
$timeout = 60
$elapsed = 0
while ($elapsed -lt $timeout) {
    $ns = kubectl get namespace mlops-dev 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Namespace deleted successfully!" -ForegroundColor Green
        break
    }
    Write-Host "Still waiting... ($elapsed seconds)" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    $elapsed += 5
}

if ($elapsed -ge $timeout) {
    Write-Host "Warning: Namespace still exists after timeout. Proceeding anyway..." -ForegroundColor Yellow
}

Write-Host "`nStep 6: Creating namespace..." -ForegroundColor Cyan
kubectl apply -f namespace.yaml

Write-Host "Step 7: Deploying Postgres..." -ForegroundColor Cyan
kubectl apply -f postgres-deployment.yaml

Write-Host "Step 8: Waiting for Postgres to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "Step 9: Deploying MLflow..." -ForegroundColor Cyan
kubectl apply -f mlflow-deployment.yaml

Write-Host "Step 10: Waiting for MLflow to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

Write-Host "Step 11: Deploying Titanic Predictor..." -ForegroundColor Cyan
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

Write-Host "`nStep 12: Checking deployment status..." -ForegroundColor Cyan
kubectl get all -n mlops-dev

Write-Host "`nDeployment complete! Wait a few minutes for all pods to be ready." -ForegroundColor Green
Write-Host "Monitor with: kubectl get pods -n mlops-dev -w" -ForegroundColor Cyan
