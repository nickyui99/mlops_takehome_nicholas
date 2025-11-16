"""
CI/CD Unit Tests for API
Minimal tests that run in GitHub Actions without requiring running servers
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
    """Test health check endpoint returns 200"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_predict_endpoint():
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
    assert data["prediction"] in ["survived", "died"]


def test_predict_validation():
    """Test prediction endpoint validates input"""
    # Missing required field
    invalid_payload = {
        "pclass": 1,
        "sex": "female",
        # missing age
    }
    
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422  # Validation error


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
