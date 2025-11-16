# -*- coding: utf-8 -*-
"""
Test training pipeline to meet CI/CD requirements
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_train_with_mlflow():
    """Test that training script runs successfully"""
    from train.train_with_mlflow import train_model
    
    # Run quick training with minimal parameters for fast CI testing
    run_id = train_model(
        n_estimators=10,  # Small for fast testing
        max_depth=3,
        min_samples_split=5,
        version="test-ci"
    )
    
    assert run_id is not None, "Training should return a run ID"
    assert len(run_id) > 0, "Run ID should not be empty"
    print(f"[SUCCESS] Training test passed with run_id: {run_id}")


def test_model_artifacts_exist():
    """Test that model artifacts are created after training"""
    from pathlib import Path
    
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "titanic-classifier"
    
    # Check key files exist
    expected_files = ["model.pkl", "scaler.pkl", "imputer.pkl", "metadata.json"]
    
    for file_name in expected_files:
        file_path = artifacts_dir / file_name
        assert file_path.exists(), f"Artifact {file_name} should exist at {file_path}"
    
    print("[SUCCESS] All model artifacts exist")


def test_model_loading():
    """Test that trained model can be loaded"""
    import joblib
    from pathlib import Path
    
    model_path = Path(__file__).parent.parent / "artifacts" / "titanic-classifier" / "model.pkl"
    
    if not model_path.exists():
        pytest.skip("Model not trained yet, skipping load test")
    
    # Test model can be loaded
    model = joblib.load(model_path)
    
    assert hasattr(model, 'predict'), "Loaded object should have predict method"
    assert hasattr(model, 'predict_proba'), "Loaded object should have predict_proba method"
    
    print("[SUCCESS] Model loaded successfully")


def test_mlflow_configuration():
    """Test MLflow tracking is configured correctly"""
    import mlflow
    import os
    
    # Set tracking URI (use local sqlite for testing)
    tracking_uri = "sqlite:///mlflow_test.db"
    mlflow.set_tracking_uri(tracking_uri)
    
    # Test we can create an experiment
    experiment_name = "test-experiment-ci"
    experiment_id = mlflow.create_experiment(experiment_name)
    
    assert experiment_id is not None, "Should be able to create MLflow experiment"
    
    # Test we can start a run
    with mlflow.start_run(experiment_id=experiment_id) as run:
        mlflow.log_param("test_param", "test_value")
        mlflow.log_metric("test_metric", 0.95)
        assert run.info.run_id is not None
    
    print("[SUCCESS] MLflow configuration working")


def test_training_script_imports():
    """Test that training script imports work correctly"""
    try:
        from train import train_with_mlflow
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.impute import SimpleImputer
        import mlflow
        import joblib
        print("[SUCCESS] All training imports successful")
    except ImportError as e:
        pytest.fail(f"Import error in training modules: {e}")


def test_synthetic_data_generation():
    """Test that synthetic data can be generated for training"""
    from train.train_with_mlflow import load_and_preprocess_data
    
    X_train, X_test, y_train, y_test = load_and_preprocess_data()
    
    assert len(X_train) > 0, "Training set should not be empty"
    assert len(X_test) > 0, "Test set should not be empty"
    assert X_train.shape[1] == 7, "Should have 7 features"
    
    print(f"[SUCCESS] Data generated: {len(X_train)} train, {len(X_test)} test samples")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
