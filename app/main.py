# /app/main.py
import os
import uuid
import json
import time
from fastapi import FastAPI, Request
import mlflow
from pydantic import BaseModel
from typing import Literal
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
from contextlib import asynccontextmanager

from app.model_loader import load_model
from app.db import init_db, get_db_connection

# --- Environment ---
POD_NAME = os.getenv("HOSTNAME", "unknown")

# --- Logging ---
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# --- Metrics ---
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP Request Latency", ["endpoint"])


# --- Model ---
model = None
model_version = "unknown"
model_metadata = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, model_version, model_metadata

    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    init_db()
    model, model_metadata = load_model()

    # Extract version from metadata
    model_version = model_metadata.get("model_version", "unknown")
    print(f"✅ Model loaded. Version: {model_version}")
    yield

app = FastAPI(lifespan=lifespan)

# --- Models ---
class TitanicInput(BaseModel):
    pclass: int  # Passenger class (1, 2, or 3)
    sex: str  # 'male' or 'female'
    age: float  # Age in years
    sibsp: int  # Number of siblings/spouses aboard
    parch: int  # Number of parents/children aboard
    fare: float  # Passenger fare
    embarked: str  # Port of embarkation ('C', 'Q', or 'S')

class TitanicOutput(BaseModel):
    prediction: Literal["survived", "died"]
    survival_probability: float
    latency_ms: float
    model_version: str
    pod_name: str

# --- Endpoints ---
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "model_version": model_version}

@app.post("/predict", response_model=TitanicOutput)
async def predict(request: Request, input: TitanicInput):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    
    # Preprocess input
    sex_encoded = 0 if input.sex.lower() == 'male' else 1
    embarked_map = {'C': 0, 'Q': 1, 'S': 2}
    embarked_encoded = embarked_map.get(input.embarked.upper(), 2)
    
    # Create feature vector in the same order as training
    input_vec = [[input.pclass, sex_encoded, input.age, input.sibsp, input.parch, input.fare, embarked_encoded]]
    
    # Apply preprocessing (imputation and scaling)
    import joblib
    from pathlib import Path
    model_path = Path(model_metadata.get('model_path', 'artifacts/titanic-classifier'))
    imputer = joblib.load(model_path / 'imputer.pkl')
    scaler = joblib.load(model_path / 'scaler.pkl')
    
    input_imputed = imputer.transform(input_vec)
    input_scaled = scaler.transform(input_imputed)
    
    # Predict - Load the underlying sklearn model for predict_proba
    sklearn_model = joblib.load(model_path / 'model.pkl')
    prediction_idx = sklearn_model.predict(input_scaled)[0]
    prediction_proba = sklearn_model.predict_proba(input_scaled)[0]
    survival_prob = float(prediction_proba[1])  # Probability of survival
    
    outcomes = ["died", "survived"]
    prediction = outcomes[int(prediction_idx)]
    latency_ms = (time.perf_counter() - start) * 1000

    print(f"Model version: {model_version}, Prediction: {prediction} ({survival_prob:.2%}), Latency: {latency_ms:.2f}ms")

    # Log
    logger.info("prediction_served",
        request_id=request_id,
        model_version=model_version,
        pod_name=POD_NAME,
        latency_ms=round(latency_ms, 2),
        input=input.dict(),
        prediction=prediction
    )

    # Save to DB
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO predictions (request_id, model_version, latency_ms, input_data, prediction)
                VALUES (%s, %s, %s, %s, %s)
            """, (request_id, model_version, latency_ms, json.dumps(input.dict()), prediction))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("db_insert_failed", error=str(e))

    # Record metrics
    REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/predict").observe(latency_ms / 1000.0)

    return {
        "prediction": prediction,
        "survival_probability": round(survival_prob, 4),
        "latency_ms": round(latency_ms, 2),
        "model_version": model_version,
        "pod_name": POD_NAME
    }

# --- Observability ---
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

from fastapi.responses import Response