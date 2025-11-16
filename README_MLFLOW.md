# MLflow Integration Guide

## Overview

This project now includes MLflow for model tracking, versioning, and experiment management.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nginx     │────▶│  Titanic API │────▶│  MLflow     │
│ (Port 8000) │     │  (3 replicas)│     │ (Port 5000) │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  PostgreSQL  │     │  Artifacts  │
                    │  (Port 5432) │     │   Storage   │
                    └──────────────┘     └─────────────┘
```

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

This will start:
- **MLflow Server** on http://localhost:5000
- **Titanic API** (3 replicas) behind Nginx on http://localhost:8000
- **PostgreSQL** for predictions storage
- **Prometheus** for metrics collection

### 2. Access MLflow UI

Open your browser to: **http://localhost:5000**

You'll see:
- All experiments
- Training runs
- Model versions
- Metrics comparison
- Artifact storage

### 3. Train a New Model Version

```bash
# Train with default parameters (version 1.0)
python train/train_with_mlflow.py

# Train with custom parameters (version 2.0)
python train/train_with_mlflow.py \
  --n-estimators 200 \
  --max-depth 15 \
  --version 2.0

# Train version 3.0 with different settings
python train/train_with_mlflow.py \
  --n-estimators 150 \
  --max-depth 12 \
  --min-samples-split 10 \
  --version 3.0
```

## MLflow Features

### Model Tracking

Each API instance tracks:
- **Pod name** and **model version**
- **Prediction latencies** over time
- **Survival probabilities** distribution
- **Request counts** per model

### Experiment Management

In MLflow UI, you can:
- Compare model versions side-by-side
- View training metrics (accuracy, precision, recall, F1)
- Inspect model parameters
- Download model artifacts

### Model Registry

Models are registered with:
- **Version number** (e.g., 1.0, 2.0, 3.0)
- **Training metrics** (accuracy, F1 score)
- **Hyperparameters** (n_estimators, max_depth)
- **Artifacts** (model.pkl, imputer.pkl, scaler.pkl)

## Environment Variables

The following environment variables configure MLflow:

```yaml
MLFLOW_TRACKING_URI: http://mlflow:5000  # MLflow server URL
MODEL_NAME: titanic-classifier            # Model name in registry
MODEL_VERSION: "1"                        # Model version to serve
```

## Model Versioning Workflow

### 1. Train New Version

```bash
python train/train_with_mlflow.py --version 2.0
```

This creates:
- New MLflow run in "titanic-classifier-training" experiment
- Saved artifacts in `artifacts/titanic-classifier/`
- Registered model in MLflow Model Registry

### 2. Compare Models

1. Go to MLflow UI: http://localhost:5000
2. Navigate to "titanic-classifier-training" experiment
3. Select multiple runs
4. Click "Compare" button
5. View side-by-side metrics comparison

### 3. Deploy New Version

Update `docker-compose.yaml`:

```yaml
titanic-api:
  environment:
    MODEL_VERSION: "2"  # Change from "1" to "2"
```

Restart services:

```bash
docker-compose down
docker-compose up -d
```

### 4. Rollback to Previous Version

If needed, revert `MODEL_VERSION` to previous value and restart.

## MLflow API Examples

### Query MLflow Programmatically

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

# Get experiment
experiment = mlflow.get_experiment_by_name("titanic-classifier-training")

# List all runs
runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
print(runs[["run_id", "params.model_version", "metrics.test_accuracy"]])

# Load specific model
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
```

### Register Model to Production

```python
from mlflow.tracking import MlflowClient

client = MlflowClient("http://localhost:5000")

# Transition model to production
client.transition_model_version_stage(
    name="titanic-classifier",
    version=2,
    stage="Production"
)
```

## Monitoring in MLflow

### Serving Metrics

Each API replica logs:
- **prediction_latency_ms**: Time taken for each prediction
- **survival_probability**: Predicted survival chance

View these in MLflow UI:
1. Go to "titanic-classifier-serving" experiment
2. Select a run (one per API replica)
3. View "Metrics" tab for time-series data

### Training Metrics

Training runs log:
- **train_accuracy**: Training set accuracy
- **test_accuracy**: Test set accuracy
- **precision**: Precision score
- **recall**: Recall score
- **f1_score**: F1 score

## Directory Structure

```
mlflow/
├── mlruns/          # Experiment tracking data
│   └── mlflow.db    # SQLite backend store
└── artifacts/       # Model artifacts storage

artifacts/
└── titanic-classifier/
    ├── model.pkl      # Trained model
    ├── imputer.pkl    # Data imputer
    ├── scaler.pkl     # Feature scaler
    └── metadata.json  # Model metadata
```

## Troubleshooting

### MLflow UI not accessible

```bash
# Check if MLflow container is running
docker ps | grep mlflow

# View MLflow logs
docker logs mlflow

# Restart MLflow
docker-compose restart mlflow
```

### Models not appearing in MLflow

```bash
# Verify tracking URI
docker-compose exec titanic-api env | grep MLFLOW

# Check if experiment exists
docker-compose exec mlflow mlflow experiments list
```

### Training script fails

```bash
# Install dependencies locally
pip install -r requirements.txt

# Run with verbose output
python train/train_with_mlflow.py --version test
```

## Best Practices

1. **Version naming**: Use semantic versioning (1.0, 1.1, 2.0)
2. **Experiment tracking**: Always log hyperparameters and metrics
3. **Model comparison**: Compare at least 3 runs before deploying
4. **Artifact storage**: Keep preprocessing objects (imputer, scaler) with model
5. **Metadata**: Document model changes in metadata.json

## Next Steps

- [ ] Integrate with CI/CD for automatic model deployment
- [ ] Add model performance monitoring alerts
- [ ] Implement A/B testing between model versions
- [ ] Set up model drift detection
- [ ] Configure production/staging model stages

## Resources

- MLflow Documentation: https://mlflow.org/docs/latest/
- MLflow Model Registry: https://mlflow.org/docs/latest/model-registry.html
- MLflow Tracking: https://mlflow.org/docs/latest/tracking.html
