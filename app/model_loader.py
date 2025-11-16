# /app/model_loader.py
import os
import json
from pathlib import Path
import joblib

# Default to latest registered model version
MODEL_NAME = os.getenv("MODEL_NAME", "titanic-classifier")
MODEL_STAGE_OR_VERSION = os.getenv("MODEL_VERSION", "1")  # or "Production"
MODEL_URI = os.getenv("MODEL_URI", "artifacts/titanic-classifier")

def load_model():
    """Load model and return (model, metadata) tuple."""
    print(f"Loading model from directory: {MODEL_URI}")
    
    # Load model directly with joblib (bypass MLflow's broken cloudpickle loader)
    model_path = Path(MODEL_URI) / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    print(f"Loading model from: {model_path}")
    model = joblib.load(model_path)
    
    # Load metadata if it exists
    metadata = {"model_version": "unknown", "model_path": MODEL_URI}
    metadata_path = Path(MODEL_URI) / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        metadata["model_path"] = MODEL_URI
        print(f"Loaded metadata: {metadata.get('model_version', 'unknown')}")
    else:
        print(f"Warning: metadata.json not found at {metadata_path}")
    
    return model, metadata