# /app/model_loader.py
import os
import mlflow

# Default to latest registered model version
MODEL_NAME = os.getenv("MODEL_NAME", "iris-classifier")
MODEL_STAGE_OR_VERSION = os.getenv("MODEL_VERSION", "1")  # or "Production"
MODEL_URI = os.getenv("MODEL_URI", "artifacts/iris-classifier")

def load_model():
    print(f"Loading model from MLflow: {MODEL_URI}")
    return mlflow.pyfunc.load_model(MODEL_URI)