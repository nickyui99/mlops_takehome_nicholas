# Migration from Iris to Titanic Dataset

## Overview
Successfully migrated the MLOps project from Iris flower classification to Titanic survival prediction.

## Changes Made

### 1. Training Script (`train/train.py`)
- ✅ Updated data source from `sklearn.datasets.load_iris()` to `seaborn.load_dataset('titanic')`
- ✅ Added feature engineering and preprocessing:
  - Categorical encoding (sex, embarked)
  - Median imputation for missing values
  - Standard scaling with `StandardScaler`
- ✅ Updated model name: `iris-classifier` → `titanic-classifier`
- ✅ Added additional metrics: precision, recall, F1 score
- ✅ Saved preprocessing artifacts (imputer, scaler, features list)

### 2. API Endpoints (`app/main.py`)
- ✅ Updated input model: `IrisInput` → `TitanicInput`
  - New features: pclass, sex, age, sibsp, parch, fare, embarked
- ✅ Updated output model: `IrisOutput` → `TitanicOutput`
  - Predictions: "setosa"/"versicolor"/"virginica" → "survived"/"died"
  - Added: survival_probability field
- ✅ Integrated preprocessing in prediction endpoint (imputation + scaling)

### 3. Model Loader (`app/model_loader.py`)
- ✅ Updated default model name: `iris-classifier` → `titanic-classifier`
- ✅ Updated default artifact path: `artifacts/iris-classifier` → `artifacts/titanic-classifier`
- ✅ Added model_path to metadata for preprocessing artifact access

### 4. Airflow Pipeline (`pipelines/`)
- ✅ Renamed: `iris_training_dag.py` → `titanic_training_dag.py`
- ✅ Updated DAG ID: `iris_training_pipeline` → `titanic_training_pipeline`
- ✅ Updated data fetching to verify seaborn Titanic dataset
- ✅ Adjusted accuracy threshold: 0.9 → 0.75 (realistic for Titanic)
- ✅ Updated model registration name

### 5. Deployment Files
- ✅ Updated Kubernetes deployment: `iris-predictor` → `titanic-predictor`
- ✅ Updated service: `iris-predictor-svc` → `titanic-predictor-svc`
- ✅ Updated ingress: `iris-ingress` → `titanic-ingress`
- ✅ Updated Docker Compose: `iris-api` → `titanic-api`
- ✅ Updated NGINX config upstream

### 6. Documentation
- ✅ Updated README.md title and overview
- ✅ Updated MODEL_CARD.md with Titanic dataset details
- ✅ Updated test files with Titanic sample data
- ✅ Updated deployment commands in README

### 7. Dependencies
- ✅ Added to requirements.txt:
  - seaborn (for Titanic dataset)
  - pandas (for data manipulation)
  - numpy (for numerical operations)

## Dataset Comparison

### Iris Dataset (Before)
- **Samples**: 150
- **Features**: 4 (sepal length, sepal width, petal length, petal width)
- **Classes**: 3 (setosa, versicolor, virginica)
- **Accuracy**: ~96-100%
- **Preprocessing**: None required

### Titanic Dataset (After)
- **Samples**: 891
- **Features**: 7 (pclass, sex, age, sibsp, parch, fare, embarked)
- **Classes**: 2 (survived, died)
- **Accuracy**: ~78-82%
- **Preprocessing**: Required (encoding, imputation, scaling)

## Model Performance

Latest training results:
```
Model Version: v20251114_174012
Accuracy:  80.45%
Precision: 72.97%
Recall:    78.26%
F1 Score:  75.52%
```

## Next Steps

1. **Test the API**: Run test_api.py with the new Titanic input format
2. **Retrain Docker Image**: Build new Docker image with updated code
3. **Update Kubernetes**: Apply updated deployment manifests
4. **Verify Grafana Dashboards**: Ensure metrics are still being collected
5. **Update CI/CD**: Verify GitHub Actions still work with new naming

## Testing Commands

```bash
# Test training
python train/train.py

# Test API (requires running containers)
python tests/test_api.py

# Build Docker image
docker build -t titanic-predictor:latest .

# Run with Docker Compose
docker compose up -d

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "pclass": 1,
    "sex": "female",
    "age": 29.0,
    "sibsp": 0,
    "parch": 0,
    "fare": 100.0,
    "embarked": "C"
  }'
```

## Files Modified

- `train/train.py`
- `app/main.py`
- `app/model_loader.py`
- `pipelines/titanic_training_dag.py` (renamed from iris_training_dag.py)
- `deploy/k8s/deployment.yaml`
- `deploy/k8s/service.yaml`
- `deploy/k8s/ingress.yaml`
- `docker-compose.yaml`
- `nginx.conf`
- `requirements.txt`
- `README.md`
- `MODEL_CARD.md`
- `tests/test_api.py`
