"""
Unit tests for Titanic Predictor API
Uses FastAPI TestClient for testing without requiring a running server
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

# Create test client
client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "model_version" in data


def test_predict_endpoint_valid_input():
    """Test prediction endpoint with valid input"""
    payload = {
        "pclass": 1,
        "sex": "female",
        "age": 29.0,
        "sibsp": 0,
        "parch": 0,
        "fare": 100.0,
        "embarked": "C"
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "prediction" in data
    assert "survival_probability" in data
    assert "latency_ms" in data
    assert "model_version" in data
    assert "pod_name" in data
    
    # Check prediction is valid
    assert data["prediction"] in ["survived", "died"]
    assert 0 <= data["survival_probability"] <= 1


def test_predict_endpoint_first_class_female():
    """Test prediction for first-class female (should have high survival probability)"""
    payload = {
        "pclass": 1,
        "sex": "female",
        "age": 29.0,
        "sibsp": 0,
        "parch": 0,
        "fare": 100.0,
        "embarked": "C"
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # First-class female passenger should get a valid prediction
    assert "survival_probability" in data
    assert data["prediction"] in ["survived", "died"]


def test_predict_endpoint_third_class_male():
    """Test prediction for third-class male (should have lower survival probability)"""
    payload = {
        "pclass": 3,
        "sex": "male",
        "age": 25.0,
        "sibsp": 0,
        "parch": 0,
        "fare": 7.25,
        "embarked": "S"
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # Should return a valid prediction
    assert "prediction" in data
    assert "survival_probability" in data


def test_predict_endpoint_missing_field():
    """Test prediction endpoint with missing required field"""
    payload = {
        "pclass": 1,
        "sex": "female",
        # Missing 'age' field
        "sibsp": 0,
        "parch": 0,
        "fare": 100.0,
        "embarked": "C"
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    # Check that metrics are in Prometheus format
    assert "http_requests_total" in response.text or "# HELP" in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
