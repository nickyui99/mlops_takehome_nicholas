# Quick Start: Testing MLflow Integration

Write-Host "🚀 MLflow Integration - Quick Start Guide" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Step 1: Check Docker
Write-Host "`n📦 Step 1: Checking Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker is installed" -ForegroundColor Green
    docker --version
} else {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Step 2: Check directory structure
Write-Host "`n📁 Step 2: Checking directory structure..." -ForegroundColor Yellow
$dirs = @("mlflow/mlruns", "mlflow/artifacts", "artifacts", "train")
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "✅ $dir exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Creating $dir..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created $dir" -ForegroundColor Green
    }
}

# Step 3: Start services
Write-Host "`n🐳 Step 3: Starting Docker Compose services..." -ForegroundColor Yellow
Write-Host "This will start: MLflow, API (3 replicas), PostgreSQL, Nginx" -ForegroundColor Gray

$startServices = Read-Host "`nStart services now? (y/n)"
if ($startServices -eq 'y') {
    docker-compose up -d
    
    Write-Host "`n⏳ Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Check service status
    Write-Host "`n📊 Service Status:" -ForegroundColor Yellow
    docker-compose ps
    
    # Step 4: Verify MLflow
    Write-Host "`n🔍 Step 4: Verifying MLflow..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ MLflow is running!" -ForegroundColor Green
            Write-Host "🌐 MLflow UI: http://localhost:5000" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "⚠️  MLflow not responding yet. Wait a moment and check http://localhost:5000" -ForegroundColor Yellow
    }
    
    # Step 5: Verify API
    Write-Host "`n🔍 Step 5: Verifying API..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/healthz" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API is running!" -ForegroundColor Green
            Write-Host "🌐 API: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "📖 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "⚠️  API not responding yet. Wait a moment and check http://localhost:8000" -ForegroundColor Yellow
    }
    
    # Step 6: Test prediction
    Write-Host "`n🧪 Step 6: Testing prediction..." -ForegroundColor Yellow
    $testPrediction = Read-Host "Send a test prediction? (y/n)"
    if ($testPrediction -eq 'y') {
        $body = @{
            pclass = 3
            sex = "female"
            age = 25.0
            sibsp = 0
            parch = 0
            fare = 7.75
            embarked = "S"
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
            Write-Host "`n✅ Prediction Response:" -ForegroundColor Green
            Write-Host "   Prediction: $($response.prediction)" -ForegroundColor White
            Write-Host "   Probability: $($response.survival_probability)" -ForegroundColor White
            Write-Host "   Latency: $($response.latency_ms) ms" -ForegroundColor White
            Write-Host "   Model Version: $($response.model_version)" -ForegroundColor White
            Write-Host "   Pod: $($response.pod_name)" -ForegroundColor White
        } catch {
            Write-Host "❌ Prediction failed: $_" -ForegroundColor Red
        }
    }
}

# Step 7: Next steps
Write-Host "`n📚 Next Steps:" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""
Write-Host "1. 🌐 Open MLflow UI:" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "2. 🚂 Train a new model:" -ForegroundColor Cyan
Write-Host "   python train/train_with_mlflow.py --version 2.0" -ForegroundColor White
Write-Host ""
Write-Host "3. 📊 View experiments in MLflow:" -ForegroundColor Cyan
Write-Host "   - Click 'titanic-classifier-training' for training runs" -ForegroundColor White
Write-Host "   - Click 'titanic-classifier-serving' for serving metrics" -ForegroundColor White
Write-Host ""
Write-Host "4. 🧪 Run tests:" -ForegroundColor Cyan
Write-Host "   python tests/test_api.py" -ForegroundColor White
Write-Host "   python tests/test_traffic.py" -ForegroundColor White
Write-Host ""
Write-Host "5. 📖 Read documentation:" -ForegroundColor Cyan
Write-Host "   README_MLFLOW.md" -ForegroundColor White
Write-Host "   MLFLOW_IMPLEMENTATION.md" -ForegroundColor White
Write-Host ""
Write-Host "6. 🛑 Stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "🎉 Setup complete!" -ForegroundColor Green
