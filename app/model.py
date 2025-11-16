# /app/model.py
import joblib
import time
from pathlib import Path

# Load model once at startup
MODEL_PATH = Path(__file__).parent / "model.pkl"
model = joblib.load(MODEL_PATH)
MODEL_VERSION = "titanic-v1"  # Hardcoded for now; will come from MLflow later

def predict_titanic(pclass: int, sex: str, age: float, sibsp: int, parch: int, fare: float, embarked: str):
    start = time.perf_counter()
    # Map categorical features
    sex_encoded = 1 if sex.lower() == "male" else 0
    embarked_map = {"C": 0, "Q": 1, "S": 2}
    embarked_encoded = embarked_map.get(embarked.upper(), 2)
    
    features = [[pclass, sex_encoded, age, sibsp, parch, fare, embarked_encoded]]
    prediction = model.predict(features)[0]
    latency_ms = (time.perf_counter() - start) * 1000

    # Map class index to survival status
    survival_status = ["died", "survived"]
    return {
        "prediction": survival_status[prediction],
        "latency_ms": round(latency_ms, 2),
        "model_version": MODEL_VERSION
    }