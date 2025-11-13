# /app/model_loader.py
import os
import json
from pathlib import Path
import mlflow

# Default to latest registered model version
MODEL_NAME = os.getenv("MODEL_NAME", "iris-classifier")
MODEL_STAGE_OR_VERSION = os.getenv("MODEL_VERSION", "1")  # or "Production"
MODEL_URI = os.getenv("MODEL_URI", "artifacts/iris-classifier")

def load_model():
    """Load model and return (model, metadata) tuple."""
    print(f"Loading model from MLflow: {MODEL_URI}")
    model = mlflow.pyfunc.load_model(MODEL_URI)
    
    # Load metadata if it exists
    metadata = {"model_version": "unknown"}
    metadata_path = Path(MODEL_URI) / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        print(f"Loaded metadata: {metadata.get('model_version', 'unknown')}")
    else:
        print(f"Warning: metadata.json not found at {metadata_path}")
    
    return model, metadata