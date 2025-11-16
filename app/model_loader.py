# /app/model_loader.py
import os
import json
from pathlib import Path
import joblib
import mlflow
from mlflow.tracking import MlflowClient

# Default to latest registered model version
MODEL_NAME = os.getenv("MODEL_NAME", "titanic-classifier")
MODEL_STAGE_OR_VERSION = os.getenv("MODEL_VERSION", "1")  # or "Production"
MODEL_URI = os.getenv("MODEL_URI", "artifacts/titanic-classifier")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")

def load_model():
    """Load model and return (model, metadata) tuple."""
    print(f"Loading model from directory: {MODEL_URI}")
    
    # Try to load from local path first
    model_path = Path(MODEL_URI) / "model.pkl"
    
    # If local file doesn't exist, try to download from MLflow
    if not model_path.exists():
        print(f"⚠️  Local model not found at {model_path}")
        print(f"📥 Attempting to download from MLflow: {MLFLOW_TRACKING_URI}")
        
        try:
            # Set MLflow tracking URI
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            client = MlflowClient()
            
            # Try to get the model from MLflow Model Registry
            try:
                model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE_OR_VERSION}"
                print(f"Trying to load from MLflow registry: {model_uri}")
                model = mlflow.sklearn.load_model(model_uri)
                print(f"✅ Successfully loaded model from MLflow registry")
                
                # Get model version details
                try:
                    model_version = client.get_model_version(MODEL_NAME, MODEL_STAGE_OR_VERSION)
                    metadata = {
                        "model_version": MODEL_STAGE_OR_VERSION,
                        "model_name": MODEL_NAME,
                        "run_id": model_version.run_id,
                        "source": "mlflow_registry"
                    }
                except:
                    metadata = {
                        "model_version": MODEL_STAGE_OR_VERSION,
                        "model_name": MODEL_NAME,
                        "source": "mlflow_registry"
                    }
                
                return model, metadata
                
            except Exception as e:
                print(f"⚠️  MLflow registry failed: {e}")
                print("Creating a simple fallback model...")
                
                # Create a simple fallback model for testing
                from sklearn.ensemble import RandomForestClassifier
                model = RandomForestClassifier(n_estimators=10, random_state=42)
                
                # Create dummy training data to fit the model
                import numpy as np
                X_dummy = np.random.rand(100, 7)  # 7 features
                y_dummy = np.random.randint(0, 2, 100)
                model.fit(X_dummy, y_dummy)
                
                print("✅ Created fallback model (for testing only)")
                metadata = {
                    "model_version": "fallback",
                    "model_name": "fallback-classifier",
                    "source": "fallback",
                    "warning": "This is a fallback model - not trained on real data"
                }
                
                return model, metadata
                
        except Exception as e:
            print(f"❌ Failed to load model from MLflow: {e}")
            raise FileNotFoundError(f"Model file not found locally and MLflow download failed: {e}")
    
    # Load from local path
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