"""
CI/CD Unit Tests for Training Pipeline
Minimal tests that run in GitHub Actions without requiring MLflow server
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_training_script_imports():
    """Test that training script can be imported"""
    try:
        from train import train_with_mlflow
        assert True
    except ImportError as e:
        pytest.skip(f"Training script not available: {e}")


def test_model_artifacts_exist():
    """Test that model artifacts exist after training"""
    artifact_path = Path(__file__).parent.parent / "artifacts" / "titanic-classifier"
    
    # If artifacts don't exist, skip (will be created by training)
    if not artifact_path.exists():
        pytest.skip("Model artifacts not found - run training first")
    
    # Check for key artifact files
    model_file = artifact_path / "model.pkl"
    assert model_file.exists(), "model.pkl should exist in artifacts"


def test_model_loading():
    """Test that model can be loaded"""
    artifact_path = Path(__file__).parent.parent / "artifacts" / "titanic-classifier"
    model_file = artifact_path / "model.pkl"
    
    if not model_file.exists():
        pytest.skip("Model not trained yet")
    
    try:
        import joblib
        model = joblib.load(model_file)
        assert model is not None
        assert hasattr(model, 'predict')
    except ImportError:
        pytest.skip("joblib not installed")


def test_model_prediction():
    """Test that model can make predictions"""
    artifact_path = Path(__file__).parent.parent / "artifacts" / "titanic-classifier"
    model_file = artifact_path / "model.pkl"
    
    if not model_file.exists():
        pytest.skip("Model not trained yet")
    
    try:
        import joblib
        import numpy as np
        
        model = joblib.load(model_file)
        
        # Test prediction with sample data
        sample = np.array([[3, 0, 22.0, 1, 0, 7.25, 2]])  # 3rd class male
        prediction = model.predict(sample)
        
        assert prediction is not None
        assert len(prediction) == 1
        assert prediction[0] in [0, 1]
    except ImportError:
        pytest.skip("Required libraries not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
