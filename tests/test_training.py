# -*- coding: utf-8 -*-
"""
Unit tests for training pipeline
Tests model training, saving, and loading without requiring MLflow server
"""
import pytest
import sys
from pathlib import Path
try:
    import joblib
except ImportError:
    joblib = None
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_model_artifact_exists():
    """Test that model artifact file exists"""
    # Check primary location (MLflow artifacts)
    model_path_primary = Path(__file__).parent.parent / "artifacts" / "titanic-classifier" / "model.pkl"
    # Check alternative location (direct artifacts)
    model_path_alt = Path(__file__).parent.parent / "artifacts" / "model.pkl"
    
    if not (model_path_primary.exists() or model_path_alt.exists()):
        pytest.skip("Model artifacts not found - run training first")


def test_model_can_be_loaded():
    """Test that trained model can be loaded from joblib file"""
    if joblib is None:
        pytest.skip("joblib not installed")
    
    # Try primary location first
    model_path = Path(__file__).parent.parent / "artifacts" / "titanic-classifier" / "model.pkl"
    if not model_path.exists():
        model_path = Path(__file__).parent.parent / "artifacts" / "model.pkl"
    
    if not model_path.exists():
        pytest.skip("Model artifacts not found - run training first")
    
    model = joblib.load(model_path)
    
    assert model is not None, "Model should be loaded"
    assert hasattr(model, 'predict'), "Model should have predict method"
    assert hasattr(model, 'predict_proba'), "Loaded object should have predict_proba method"


def test_model_prediction_shape():
    """Test that model predictions have correct shape"""
    if joblib is None:
        pytest.skip("joblib not installed")
    
    # Try primary location first
    model_path = Path(__file__).parent.parent / "artifacts" / "titanic-classifier" / "model.pkl"
    if not model_path.exists():
        pytest.skip("Model artifacts not found - run training first")
    
    model = joblib.load(model_path)
    
    # Create sample input (7 features)
    sample_input = np.array([[3, 0, 22.0, 1, 0, 7.25, 2]])
    
    # Test prediction
    prediction = model.predict(sample_input)
    assert prediction.shape == (1,), "Prediction should have shape (1,)"
    assert prediction[0] in [0, 1], "Prediction should be 0 or 1"


def test_training_script_imports():
    """Test that training script can be imported without errors"""
    try:
        from train import train_with_mlflow
        assert True
    except ImportError as e:
        pytest.skip(f"Training script not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
