# /app/model.py
import joblib
import time
from pathlib import Path

# Load model once at startup
MODEL_PATH = Path(__file__).parent / "model.pkl"
model = joblib.load(MODEL_PATH)
MODEL_VERSION = "iris-v1"  # Hardcoded for now; will come from MLflow later

def predict_iris(sepal_length: float, sepal_width: float, petal_length: float, petal_width: float):
    start = time.perf_counter()
    prediction = model.predict([[sepal_length, sepal_width, petal_length, petal_width]])[0]
    latency_ms = (time.perf_counter() - start) * 1000

    # Map class index to name
    species = ["setosa", "versicolor", "virginica"]
    return {
        "prediction": species[prediction],
        "latency_ms": round(latency_ms, 2),
        "model_version": MODEL_VERSION
    }